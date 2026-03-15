# CLAUDE.md - Analyze Your Data

## Security

- NEVER read `.env`, `.env.*` files except `.env.example` — they contain secrets

## Overview

Interactive data analysis and visualization tool built with Dash. Users upload data (CSV, Excel, JSON, Parquet, SQLite, SharePoint, Google Sheets, Airtable), apply optional datetime processing, view/filter in AG Grid, and create up to 3 independent charts with export.

Deployed as one Docker container per language (15 languages), routed via Cloudflare Tunnel subdomains.

## Tech Stack

- **Python**: 3.12+
- **Dash**: 4.0.0 (Plotly web framework)
- **Dash Bootstrap Components**: 2.0.4
- **Dash AG Grid**: 33.3.3 (Enterprise, licensed)
- **Pandas**: 3.0.0
- **Plotly**: 6.0.0+
- **PyArrow**: 23.0.0 (Parquet file support)
- **PyTables**: 3.10.2 (HDF5 file support — Pandas format)
- **h5py**: 3.12.1+ (HDF5 file support — generic format)
- **PyMongo**: 4.16.0 (usage analytics logging)
- **Gunicorn**: 23.0.0+ (production WSGI server)

## Project Structure

```
analyzeyourdata-en/
├── app.py                          # Entry point, layout assembly, callback registration
├── config.py                       # Centralized config via env vars
├── CLAUDE.md                       # This file
├── README.md                       # Project README
├── PRIVACY.md                      # Data privacy policy
├── requirements.txt                # Pinned dependencies
├── Dockerfile                      # Production container
├── docker-compose.yml              # Local development (15 services)
├── docker-compose.swarm.yml        # Production Swarm deployment with replicas
├── .env                            # Real credentials (gitignored)
├── .env.example                    # Env var template
├── .github/
│   └── workflows/
│       └── deploy.yml              # CI/CD: build, push to GHCR, deploy to VDS
├── components/
│   ├── __init__.py
│   ├── layout.py                   # Navbar, footer, feedback modal, navbar callbacks
│   ├── data_source_section.py      # Step 1 UI: data source selection & upload
│   └── chart_config_section.py     # Chart config panels (type, axes, titles)
├── callbacks/
│   ├── __init__.py
│   ├── data_loading.py             # Upload/SharePoint/Google/Airtable/SQLite callbacks
│   ├── data_processing.py          # Datetime toggle, grid population, dropdown options
│   └── chart_callbacks.py          # Chart render/visibility/download + dashboard export
├── utils/
│   ├── __init__.py
│   ├── chart_factory.py            # ChartFactory class (chart type → plotly figure)
│   ├── data_processing.py          # File parsing, datetime conversion, SQLite helpers
│   ├── data_sources.py             # DataSourceHandler (SharePoint, Google, Airtable)
│   ├── general.py                  # load_markdown_file() with language fallback
│   ├── mongodb.py                  # MongoDB: log_usage(), save_feedback()
│   └── analytics.py                # RAM monitoring (monitor_memory)
├── i18n/
│   ├── __init__.py                 # Translation loader: load_translations(), t()
│   ├── en.json                     # English
│   ├── cs.json                     # Czech (Čeština)
│   ├── da.json                     # Danish (Dansk)
│   ├── de.json                     # German (Deutsch)
│   ├── es.json                     # Spanish (Español)
│   ├── fr.json                     # French (Français)
│   ├── hr.json                     # Croatian (Hrvatski)
│   ├── it.json                     # Italian (Italiano)
│   ├── nl.json                     # Dutch (Nederlands)
│   ├── pl.json                     # Polish (Polski)
│   ├── pt.json                     # Portuguese (Português)
│   ├── sk.json                     # Slovak (Slovenčina)
│   ├── sl.json                     # Slovenian (Slovenščina)
│   ├── sv.json                     # Swedish (Svenska)
│   └── uk.json                     # Ukrainian (Українська)
├── assets/
│   ├── css/style.css               # Custom styles
│   ├── markdown/                   # Language-aware markdown content
│   │   ├── master/                # Master templates + variables.json
│   │   ├── en/                     # English: info.md, how_to_use.md, 404.md
│   │   ├── cs/                     # Czech
│   │   ├── da/                     # Danish
│   │   ├── de/                     # German
│   │   ├── es/                     # Spanish
│   │   ├── fr/                     # French
│   │   ├── hr/                     # Croatian
│   │   ├── it/                     # Italian
│   │   ├── nl/                     # Dutch
│   │   ├── pl/                     # Polish
│   │   ├── pt/                     # Portuguese
│   │   ├── sk/                     # Slovak
│   │   ├── sl/                     # Slovenian
│   │   ├── sv/                     # Swedish
│   │   └── uk/                     # Ukrainian
│   ├── image/                      # Logo, favicon, images
│   └── video/                      # Tutorial videos
└── development/                    # Dev scripts (gitignored)
```

## Key Patterns

### Callback Registration

Callbacks are organized into modules, each exposing a `register_callbacks(app)` function called from `app.py`:

```python
# app.py
from callbacks.data_loading import register_callbacks as register_data_loading
from callbacks.data_processing import register_callbacks as register_data_processing
from callbacks.chart_callbacks import register_callbacks as register_chart_callbacks

register_navbar_callbacks(app)   # from components.layout
register_data_loading(app)       # 8 callbacks: upload, SharePoint, Google, Airtable, SQLite
register_data_processing(app)    # 4 callbacks: datetime toggle, grid, dropdowns
register_chart_callbacks(app)    # 10 callbacks: 3×render, 3×visibility, 3×download, dashboard
```

### ChartFactory

Static factory class in `utils/chart_factory.py` that maps chart type strings to plotly figure constructors. Called as:

```python
from utils.chart_factory import ChartFactory
fig = ChartFactory.create_chart(chart_type, df, config)
```

Config dict keys: `x_col`, `y_cols`, `color_col`, `z_col`, `title`, `x_title`, `y_title`.

### i18n System

Fully implemented internationalization with 15 languages (en, cs, da, de, es, fr, hr, it, nl, pl, pt, sk, sl, sv, uk):

- **JSON translation files** in `i18n/` — loaded once at import time via `load_translations()`
- **Singleton pattern** — `_translations` dict populated at module import, accessed via `t(key, **kwargs)`
- **`APP_LANGUAGE` env var** determines which JSON file loads at startup
- **One Docker container per language**, routed via subdomain
- **Navbar language switcher** links to sibling subdomains (configurable URLs)

```python
from i18n import t
label = t('upload_button')          # Simple lookup
msg = t('rows_loaded', count=500)   # With interpolation
```

### Markdown Content

Language-aware markdown files in `assets/markdown/{lang}/`:

- **`load_markdown_file(filename, subdirectory=None)`** in `utils/general.py`
- **Fallback chain**: `{lang}/{file}` → `en/{file}` → `{lang}/404.md` → `en/404.md` → hardcoded 404
- Content files per language: `info.md` (homepage), `how_to_use.md` (guide modal), `404.md` (fallback)
- **Variable resolution**: `{{VARIABLE}}` placeholders in markdown files are replaced at load time with values from `assets/markdown/master/variables.json`

### Markdown Masters & Variables

Master templates in `assets/markdown/master/` are the source of truth for markdown content:

- **`variables.json`** — shared values (URLs, counts) used across all languages
- **`info.md`**, **`how_to_use.md`** — English master templates with `{{VARIABLE}}` placeholders
- **Workflow**: edit masters first, then propagate text changes to `en/` and other language files
- All language files (including `en/`) use the same `{{VARIABLE}}` placeholders — values resolve at runtime from `variables.json`

```python
# In markdown files:
# {{URL_PLOTLY_DASH}} → https://dash.plotly.com
# {{VALUE_CHART_TYPE_SUPPORTED}} → 13

# Variable resolution happens automatically in load_markdown_file()
```

### Usage Logging

Fire-and-forget MongoDB logging via `log_usage()` in `utils/mongodb.py`:

```python
from utils.mongodb import log_usage
log_usage('data_load', source_type='upload', file_ext='csv', rows=1000, cols=15)
```

- Silent on failure (no exceptions propagated to user)
- Logs: event type, timestamp, language, git_commit, plus event-specific fields
- **Never logs file contents, column names, or actual data values**
- Separate collection for feedback (`save_feedback()`)

### Module Dependency Graph (no circular imports)

```
app.py
 ├── config.py
 ├── i18n/__init__.py            → config
 ├── utils/general.py            → config
 ├── utils/analytics.py          → stdlib only
 ├── utils/chart_factory.py      → plotly only
 ├── utils/data_processing.py    → stdlib + pandas only
 ├── utils/mongodb.py            → config, pymongo
 ├── components/layout.py        → config, i18n, utils/mongodb, utils/general
 ├── components/data_source_section.py → config, i18n
 ├── components/chart_config_section.py → config, i18n
 ├── callbacks/data_loading.py   → config, i18n, utils/data_sources, utils/data_processing, utils/mongodb
 ├── callbacks/data_processing.py → i18n, utils/data_processing
 └── callbacks/chart_callbacks.py → i18n, utils/chart_factory, utils/mongodb
```

### Data Flow

1. **Data Source** -> Upload / SharePoint / Google Sheets / Airtable / SQLite
2. **Store** -> `dcc.Store(id='stored-data')` holds data as list of dicts
3. **Datetime Processing** -> Optional enrichment (ts, tsDate, tsHour, etc.) — disabled by default
4. **AG Grid** -> Interactive table with filtering, grouping, pivoting
5. **Charts** -> 3 independent charts read from `virtualRowData` (filtered grid data)
6. **Export** -> Individual chart HTML, all charts as ZIP, or grid data as CSV/Excel

## Environment Variables

### Application
| Variable | Default | Description |
|----------|---------|-------------|
| `APP_TITLE` | `Analyze Your Data` | Browser tab title |
| `APP_BRAND_NAME` | `Analyze Your Data` | Navbar brand text |
| `APP_DESCRIPTION` | *(long string)* | Meta description |
| `APP_LANGUAGE` | `en` | Language code (en/cs/da/de/es/fr/hr/it/nl/pl/pt/sk/sl/sv/uk) |
| `GIT_COMMIT` | `dev` | Git short hash, injected at Docker build via `--build-arg` |

### Server
| Variable | Default | Description |
|----------|---------|-------------|
| `APP_HOST` | `127.0.0.1` | Bind host |
| `APP_PORT` | `8050` | Bind port |
| `APP_DEBUG` | `True` | Debug mode |

### Language Instance URLs (for navbar cross-links)
| Variable | Default | Description |
|----------|---------|-------------|
| `APP_URL_EN` | `http://localhost:8050` | English |
| `APP_URL_CS` | `http://localhost:8051` | Czech |
| `APP_URL_DA` | `http://localhost:8054` | Danish |
| `APP_URL_DE` | `http://localhost:8052` | German |
| `APP_URL_ES` | `http://localhost:8055` | Spanish |
| `APP_URL_FR` | `http://localhost:8056` | French |
| `APP_URL_HR` | `http://localhost:8057` | Croatian |
| `APP_URL_IT` | `http://localhost:8058` | Italian |
| `APP_URL_NL` | `http://localhost:8059` | Dutch |
| `APP_URL_PL` | `http://localhost:8053` | Polish |
| `APP_URL_PT` | `http://localhost:8060` | Portuguese |
| `APP_URL_SK` | `http://localhost:8061` | Slovak |
| `APP_URL_SL` | `http://localhost:8062` | Slovenian |
| `APP_URL_SV` | `http://localhost:8063` | Swedish |
| `APP_URL_UK` | `http://localhost:8064` | Ukrainian |

### UI & Branding
| Variable | Default | Description |
|----------|---------|-------------|
| `LOGO_PATH` | *(empty)* | Navbar logo path (e.g., `/assets/image/logo.png`). If empty, logo is hidden. |
| `GITHUB_URL` | `https://github.com/your-repo` | GitHub repository URL |
| `WEBSITE_URL` | *(url)* | Company website URL |
| `CONTACT_EMAIL` | `contact@...` | Contact email address |
| `DOCUMENTATION_URL` | *(empty)* | Documentation URL. If empty, docs buttons are hidden in footer and modal. |
| `DONATE_URL` | *(empty)* | Donation page URL. If empty, donation card is hidden. |
| `YOUTUBE_INTRO_URL` | *(empty)* | YouTube embed URL. If empty, video section is hidden. |

**Favicon**: Dash auto-discovers `/assets/favicon.ico` — no env var needed.

### Data & Storage
| Variable | Default | Description |
|----------|---------|-------------|
| `MAX_FILE_SIZE_MB` | `20` | Max upload size |
| `MONGO_URI` | *(empty)* | MongoDB connection string |
| `MONGODB_DATABASE` | `analyzeYourData` | MongoDB database name |
| `MONGODB_COLLECTION_LOGS` | `usageLogs` | Collection for usage analytics |
| `MONGODB_COLLECTION_FEEDBACK` | `feedback` | Collection for user feedback |

### External Services
| Variable | Default | Description |
|----------|---------|-------------|
| `AG_GRID_LICENSE_KEY` | *(none)* | AG Grid Enterprise license |
| `SECRET_KEY` | `dev-secret-key-...` | Session secret |

## Commands

```bash
# Development
pip install -r requirements.txt
python app.py                        # Starts on http://127.0.0.1:8050

# Local Docker (without Swarm)
docker build -t analyzeyourdata .
docker compose up                    # All 15 language instances
docker compose up app-en             # English only (:8050)

# Production (Docker Swarm)
docker swarm init                                    # One-time setup
docker stack deploy -c docker-compose.swarm.yml ayd # Deploy stack
docker service ls                                    # List services
docker service ps ayd_app-en                         # View replicas
docker service logs ayd_app-en --follow              # Stream logs
docker service scale ayd_app-en=5                    # Scale up
docker service update --image ghcr.io/zboardio/analyzeyourdata:latest ayd_app-en  # Update
docker service rollback ayd_app-en                   # Rollback

# Gunicorn (without Docker)
gunicorn app:server -b 0.0.0.0:8050 --workers 2 --timeout 120
```

## Deployment Architecture

Production runs on Docker Swarm with Cloudflare Tunnel routing:

```
                         Internet
                            │
                    Cloudflare CDN
                            │
                    Cloudflare Tunnel
                            │
          ┌─────────────────┴─────────────────┐
          │         VDS (Docker Swarm)        │
          │                                    │
          │  ┌────────────────────────────┐   │
          │  │   Portainer :9443 (UI)     │   │
          │  └────────────────────────────┘   │
          │                                    │
          │  ┌────────────────────────────┐   │
          │  │   cloudflared (tunnel)     │   │
          │  └────────────┬───────────────┘   │
          │               │                    │
          │    ┌──────────┴──────────┐        │
          │    │   Docker Swarm      │        │
          │  ┌─┴──┬──────┬──────┬───┴─┐      │
          │  │en×3│es×3  │cs×1  │...×1│      │
          │  │8050│8055  │8051  │     │      │
          │  └────┴──────┴──────┴─────┘      │
          └────────────────────────────────────┘

Domain routing (Cloudflare Tunnel ingress):
  analyzeyourdata.zboardio.com → :8050 → app-en (3 replicas)
  analizatusdatos.zboardio.com → :8055 → app-es (3 replicas)
  analyzujsvojedata.zboardio.com → :8051 → app-cs (1 replica)
  ... (15 languages total, see deploy/cloudflared/config.example.yml)

Ports: 8050-8064 (see docker-compose.swarm.yml for exact mapping)
```

Each service is identical code, differentiated only by `APP_LANGUAGE` env var.
Docker Swarm automatically load-balances requests across replicas.

## Known Upstream Issues

### dcc.Markdown — React 18 warnings (Dash 4.0.0)

Two console warnings originate from `dcc.Markdown` internals and cannot be fixed in application code:

1. **`defaultProps` deprecation** — `dcc.Markdown` uses `defaultProps` on function components, deprecated in React 18 and removed in React 19.
2. **State update before mount** — async-loaded `dcc.Markdown` triggers a state update before the component mounts.

Both are cosmetic (no functional impact). Tracked upstream:
- [plotly/dash#3199](https://github.com/plotly/dash/issues/3199) — dcc.Markdown React 18 compatibility
- [plotly/dash#3231](https://github.com/plotly/dash/issues/3231) — React 19 support

**Action:** Remove this section once resolved upstream. See `Dash_feedback.md` for full details.

### Inline styles must use camelCase

Dash 4.0 / React 18 no longer silently converts kebab-case CSS properties in inline `style` dicts. All inline styles must use camelCase (`marginTop`, not `margin-top`). This has been fixed across the codebase — keep it in mind when adding new components.

### Dash 4.0.0 Theming — CSS Custom Properties

Dash 4.0.0 uses CSS custom properties for interactive element colors (dropdowns, checkboxes, focus rings, etc.). The default purple (`#7f4bc4`) is controlled by:

```css
--Dash-Fill-Interactive-Strong: #7f4bc4;
```

**To apply a custom brand color across all Dash components**, override this single variable in `:root`:

```css
:root {
    --Dash-Fill-Interactive-Strong: #0098A3;  /* your brand color */
}
```

This replaces the need for individual overrides on `.dash-options-list-option`, `.dash-dropdown`, `.dash-options-list-option-checkbox`, `.dash-dropdown-action-button`, etc. — one variable controls them all.

Similarly, Bootstrap component-level colors (e.g., `.btn-outline-primary`) use hardcoded Sass-compiled values, **not** `var(--bs-primary)`. To override, set component-level variables directly:

```css
.btn-outline-primary {
    --bs-btn-color: var(--primary-color);
    --bs-btn-border-color: var(--primary-color);
    /* ... etc */
}
```

**Key insight:** Dash 4.0.0 loads custom CSS after Bootstrap, so `!important` is generally not needed to override Bootstrap defaults. It may still be needed for Dash component inline styles set by React.

## Build Transparency & Data Privacy Traceability

**Goal:** Public proof that the deployed application does not log or store any uploaded user data files. Anyone can verify this by inspecting the source code at the exact commit running in production.

### Implemented

1. **Git commit hash in every deployment** — `GIT_COMMIT` env var injected via Docker `--build-arg`. Stored in MongoDB feedback documents and exposed publicly.

2. **`/api/version` endpoint** (`app.py`) — returns `{"git_commit": "...", "language": "..."}`. Users and auditors can see exactly which commit is running, then look it up on GitHub.

3. **Footer build transparency** (`components/layout.py`) — shows "Build: `<commit>`" linking directly to the commit on GitHub, plus a "Verify source code" link to the repo.

4. **Feedback document structure** (`utils/mongodb.py`) — stores `git_commit` (not a static version string), linking each feedback entry to the exact deployed code.

5. **`PRIVACY.md`** — documents what data is and isn't stored, external source handling, and build transparency.

### Strategy (future)

1. **Public GitHub repository** — full source code, anyone can audit all data handling paths (`callbacks/data_loading.py`, `utils/data_processing.py`, `utils/data_sources.py`).

2. **CI/CD pipeline transparency** — GitHub Actions builds Docker images from the public repo. Build logs are public, showing:
   - Which commit triggered the build
   - That no additional code was injected
   - The exact `docker build --build-arg GIT_COMMIT=...` command

3. **Reproducible builds** — anyone can clone the repo, build the Docker image from the same commit, and compare behavior. The Dockerfile is deterministic (pinned dependencies in `requirements.txt`).

### Remaining checklist

- [x] Add `GIT_COMMIT` to `docker-compose.yml` build args
- [x] Set up CI/CD pipeline (`.github/workflows/deploy.yml`)
- [ ] Configure GitHub Actions secrets (VDS_HOST, VDS_USER, VDS_SSH_KEY)
- [ ] Deploy to production VDS
