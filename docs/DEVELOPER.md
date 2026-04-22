# Developer Guide

Technical documentation for developers who want to understand, modify, or deploy Analyze Your Data.

---

## Tech Stack

- **Python**: 3.12+
- **Dash**: 4.0.0 (Plotly web framework)
- **Dash Bootstrap Components**: 2.0.4
- **Dash AG Grid**: 33.3.3 (Enterprise features require license)
- **Pandas**: 3.0.0
- **Plotly**: 6.0.0+
- **PyMongo**: 4.16.0 (optional, for usage analytics)
- **Gunicorn**: 23.0.0+ (production WSGI server)

---

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
python app.py                        # http://127.0.0.1:8050

# Production server (without Docker)
gunicorn app:server -b 0.0.0.0:8050 --workers 2 --timeout 120
```

---

## Docker Deployment

### Single Language Instance

```bash
docker build -t analyzeyourdata .
docker run -p 8050:8050 --env-file .env analyzeyourdata
```

### Multi-Language Deployment

The application supports 15 languages, each running as a separate container with its own `APP_LANGUAGE` env var:

```bash
# Build all containers
docker compose build

# Start all language instances
docker compose up

# Start specific languages only
docker compose up app-en app-de app-fr
```

### Build with Git Commit Tracking

For build transparency (commit hash shown in footer):

```bash
docker compose build --build-arg GIT_COMMIT=$(git rev-parse --short HEAD)
docker compose up
```

Or in a single step:

```bash
GIT_COMMIT=$(git rev-parse --short HEAD) docker compose up --build
```

---

## Production Deployment

Production runs on Docker Swarm — one service per language (15 total), each backed by the same image differentiated by `APP_LANGUAGE`. Three Compose files exist, each for a different context:

| File | Image source | Typical use |
|---|---|---|
| `docker-compose.yml` | Local `build:` | Local development (`docker compose up`) |
| `docker-compose.local.yml` | Local `analyzeyourdata:latest` | Manual Swarm deploy (builds on the host) |
| `docker-compose.cicd.yml` | `ghcr.io/zboardio/analyzeyourdata:${IMAGE_TAG:-latest}` | CI/CD Swarm deploy (registry image) |

Both Swarm files define rolling-update policies (`parallelism: 1`, `order: start-first`, `failure_action: rollback`) and resource limits per service.

### CI/CD Pipeline

Automated deploys live in `.github/workflows/deploy.yml`. On every push to `main`:

1. Build the Docker image, tagging it both `:latest` and `:<short-sha>`.
2. Push both tags to GitHub Container Registry (`ghcr.io/zboardio/analyzeyourdata`).
3. SSH into the production host and run `docker stack deploy -c docker-compose.cicd.yml ayd --with-registry-auth` with `IMAGE_TAG=<short-sha>` exported.
4. Because each deploy references a new SHA tag, Swarm sees a service spec change and performs a rolling update automatically — no `docker service update --force` needed.
5. Verify all 15 services report the new commit via `/api/version`, with retries until the rolling update converges.

Deploys are serialized with a `concurrency` block so two rapid pushes can't race.

### Rollback

Any image that has been built and pushed is retained on `ghcr.io` and can be redeployed at any time:

1. **GitHub Actions → Build and Deploy → Run workflow**
2. **`image_tag`** input: the short SHA you want to run (e.g. `a1b2c3d`).
3. The workflow skips the build step and redeploys that tag.

Docker Swarm also provides a one-step native rollback (`docker service rollback <service>`), which reverts to the previous task spec. The `image_tag` path above is preferred for arbitrary-depth rollback.

### Verifying a Deployment

Every running container exposes its commit at `/api/version`:

```bash
curl https://<host>/api/version
# → {"git_commit": "a1b2c3d", "language": "en"}
```

The same commit is rendered in the footer as "Build: `<commit>`" with a link to the exact commit on GitHub.

---

## Environment Variables

See `.env.example` for the full list. Key groups:

| Variable | Description |
|----------|-------------|
| `APP_LANGUAGE` | Language code (en, cs, de, etc.) — determines i18n and markdown content |
| `APP_URL_*` | 15 language URLs for navbar cross-links (empty = hidden from dropdown) |
| `AG_GRID_LICENSE_KEY` | AG Grid Enterprise license (optional, enables advanced features) |
| `MONGO_URI` | MongoDB connection string (optional, for analytics logging) |
| `GIT_COMMIT` | Git short hash, injected at Docker build time |
| `LOGO_PATH` | Navbar logo path (empty = hidden) |
| `DOCUMENTATION_URL` | Documentation link (empty = buttons hidden) |
| `DONATE_URL` | Donation link (empty = card hidden) |
| `SECRET_KEY` | Session secret (change in production) |

### Navbar Language Visibility

The navbar language dropdown only shows languages with a non-empty `APP_URL_*`:

```bash
# .env
APP_URL_EN=https://en.example.com    # shown
APP_URL_DE=https://de.example.com    # shown
APP_URL_FR=                          # hidden (empty)
```

---

## Project Structure

```
├── app.py                      # Entry point, layout assembly
├── config.py                   # Centralized config via env vars
├── components/
│   ├── layout.py               # Navbar, footer, modals
│   ├── data_source_section.py  # Step 1: data source UI
│   └── chart_config_section.py # Chart configuration panels
├── callbacks/
│   ├── data_loading.py         # Upload, SharePoint, Google, Airtable, SQLite
│   ├── data_processing.py      # Datetime toggle, grid, dropdowns
│   └── chart_callbacks.py      # Chart render, download, dashboard export
├── utils/
│   ├── chart_factory.py        # Chart type → Plotly figure
│   ├── data_processing.py      # File parsing, datetime conversion
│   ├── data_sources.py         # External data source handlers
│   ├── general.py              # Markdown loader with fallback
│   └── mongodb.py              # Analytics logging (optional)
├── i18n/
│   ├── __init__.py             # Translation loader: t()
│   └── {lang}.json             # Translation files (15 languages)
└── assets/
    ├── css/style.css           # Custom styles
    └── markdown/{lang}/        # Language-specific content
```

---

## Architecture Patterns

### Callback Registration

Callbacks are organized by module, each exposing `register_callbacks(app)`:

```python
# app.py
register_navbar_callbacks(app)   # from components.layout
register_data_loading(app)       # 8 callbacks
register_data_processing(app)    # 4 callbacks
register_chart_callbacks(app)    # 10 callbacks
```

### Data Flow

1. **Data Source** → Upload / SharePoint / Google Sheets / Airtable / SQLite
2. **Store** → `dcc.Store(id='stored-data')` holds data as list of dicts
3. **Datetime Processing** → Optional column enrichment (disabled by default)
4. **AG Grid** → Interactive table with filtering, grouping, pivoting
5. **Charts** → 3 independent charts read from `virtualRowData` (filtered data)
6. **Export** → Individual chart HTML, ZIP bundle, or grid data as CSV/Excel

### i18n System

```python
from i18n import t

label = t('upload_button')          # Simple lookup
msg = t('rows_loaded', count=500)   # With interpolation
```

- JSON translation files in `i18n/` — loaded once at import
- `APP_LANGUAGE` env var determines which file loads
- One container per language in production

### Markdown Content

Language-aware markdown with fallback chain:

```
load_markdown_file("info.md")
  → {lang}/info.md
  → en/info.md (fallback)
  → {lang}/404.md
  → en/404.md
  → hardcoded 404
```

**Variable resolution**: Markdown files use `{{VARIABLE}}` placeholders resolved at load time from `assets/markdown/master/variables.json`.

```markdown
<!-- In markdown file -->
Upload files up to {{VALUE_MAX_FILE_SIZE_MB}} MB.

<!-- Rendered -->
Upload files up to 20 MB.
```

---

## Adding a New Language

1. Create `i18n/{lang}.json` — translate all keys from `en.json`
2. Create `assets/markdown/{lang}/` with:
   - `info.md` — homepage content
   - `how_to_use.md` — help modal content
   - `404.md` — fallback content
3. Add `APP_URL_{LANG}` to `config.py` with localhost default
4. Add language tuple to `all_languages` in `components/layout.py`
5. Add `navbar.lang_{language}` key to **all** existing JSON files
6. Add service to `docker-compose.yml`
7. Update `.env.example`

---

## Usage Logging (Optional)

If `MONGO_URI` is configured, the app logs anonymous usage events:

```python
from utils.mongodb import log_usage
log_usage('data_load', source_type='upload', file_ext='csv', rows=1000, cols=15)
```

- Fire-and-forget (silent on failure)
- Logs: event type, timestamp, language, git_commit
- **Never logs file contents, column names, or data values**

---

## API Endpoint

```
GET /api/version
```

Returns build information for transparency:

```json
{
  "git_commit": "a1b2c3d",
  "language": "en"
}
```

---

## Production Checklist

- [ ] Set strong, unique `SECRET_KEY`
- [ ] Configure `AG_GRID_LICENSE_KEY` (if using Enterprise features)
- [ ] Set `APP_URL_*` for deployed languages
- [ ] Configure reverse proxy / load balancer
- [ ] Set up SSL/TLS termination
- [ ] Configure `MONGO_URI` (optional, for analytics)
- [ ] Inject `GIT_COMMIT` at build time
