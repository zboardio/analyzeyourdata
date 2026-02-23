<p align="center">
  <img src="assets/image/logo.png" alt="Analyze Your Data" height="80">
</p>

<h1 align="center">Analyze Your Data</h1>

<p align="center">
  <strong>Interactive data analysis and visualization — all in your browser</strong>
</p>

<p align="center">
  <a href="https://github.com/zboardio/analyzeyourdata/blob/main/LICENSE"><img src="https://img.shields.io/github/license/zboardio/analyzeyourdata?color=dark-green" alt="License"></a>
  <a href="https://github.com/zboardio/analyzeyourdata"><img src="https://img.shields.io/github/commit-activity/m/zboardio/analyzeyourdata?color=dark-green" alt="Commit Activity"></a>
  <a href="https://github.com/zboardio/analyzeyourdata"><img src="https://img.shields.io/github/last-commit/zboardio/analyzeyourdata?color=dark-green" alt="Last Commit"></a>
  <img src="https://img.shields.io/badge/python-3.12+-blue" alt="Python">
  <img src="https://img.shields.io/badge/dash-4.0.0-blue" alt="Dash">
  <img src="https://img.shields.io/badge/languages-15-orange" alt="Languages">
</p>

---

A free, open-source tool for interactive data analysis and visualization. Upload your data, explore it in a powerful grid, build charts, and export dashboards — no account needed, no data stored on the server.

Whether you're a data analyst exploring a dataset, a manager reviewing monthly reports, or a student working on a project — this tool gives you a full analysis workflow without installing anything or writing a single line of code.

## 🚀 How It Works

| Step | What you do |
|------|------------|
| **1. Load** | Drag & drop a file, paste a SharePoint/Google Sheets link, or connect to Airtable |
| **2. Explore** | Sort, filter, group, and pivot your data in an enterprise-grade AG Grid table |
| **3. Visualize** | Pick from 13 chart types, configure up to 3 independent charts |
| **4. Connect** | Filter data in the grid — **all charts update in real-time** |
| **5. Export** | Download charts as interactive HTML, or export grid data to CSV/Excel |

> 💡 **The core power:** Grid and charts are always in sync. Every filter, sort, or group action updates all charts instantly. Right-click the grid to export the exact data you see.

## 📁 Supported Data Sources

<table>
  <tr>
    <td><strong>📤 Direct Upload</strong></td>
    <td>Excel <code>.xlsx</code> <code>.xls</code> · CSV <code>.csv</code> <code>.txt</code> <code>.log</code> · JSON · Parquet · HDF5 · SQLite <code>.db</code> <code>.sqlite</code></td>
  </tr>
  <tr>
    <td><strong>☁️ SharePoint / OneDrive</strong></td>
    <td>Paste an anonymous sharing link</td>
  </tr>
  <tr>
    <td><strong>📊 Google Sheets</strong></td>
    <td>Paste a public sharing link, optionally specify a sheet GID</td>
  </tr>
  <tr>
    <td><strong>🔗 Airtable</strong></td>
    <td>Connect with a Personal Access Token and Base ID</td>
  </tr>
</table>

## 📈 13 Chart Types

Scatter · Scatter (multi-Y) · Line · Bar (grouped) · Bar (stacked) · Histogram (grouped) · Histogram (stacked) · Pie · Bubble · Heatmap · Logarithmic · Sunburst · Icicle

Each chart is independently configurable with custom axes, colors, titles, and Z-axis parameters. Download individual charts or a combined dashboard as standalone interactive HTML files.

## 🕐 Datetime Intelligence

If your data contains a datetime column, the tool automatically generates useful time-based columns — year, month, day, weekday, calendar week, hour, and more. Group and chart by time periods without any manual preparation.

## 🌍 Available in 15 Languages

🇬🇧 English · 🇨🇿 Čeština · 🇩🇰 Dansk · 🇩🇪 Deutsch · 🇪🇸 Español · 🇫🇷 Français · 🇭🇷 Hrvatski · 🇮🇹 Italiano · 🇳🇱 Nederlands · 🇵🇱 Polski · 🇵🇹 Português · 🇸🇰 Slovenčina · 🇸🇮 Slovenščina · 🇸🇪 Svenska · 🇺🇦 Українська

Each language runs as an independent Docker container with fully translated UI, tooltips, and documentation.

## 🔒 Data Privacy

Your uploaded data stays in your browser session memory and is **never stored on the server**. No file contents, column names, or data values are logged. Closing the browser tab clears everything.

We only store voluntary feedback submissions and anonymous usage analytics (event types, file formats, row counts — never actual data). See [PRIVACY.md](PRIVACY.md) for the full policy.

## 🔍 Build Transparency

Every deployment includes a git commit hash visible in the footer, linking directly to the source code on GitHub. The `/api/version` endpoint returns the exact commit running in production — anyone can verify that the deployed app matches this public repository.

## 🛠️ Tech Stack

| Component | Version | Purpose |
|-----------|---------|---------|
| [Plotly Dash](https://dash.plotly.com) | 4.0.0 | Web framework |
| [AG Grid Enterprise](https://www.ag-grid.com) | 33.3.3 | Interactive data grid |
| [Pandas](https://pandas.pydata.org) | 3.0.0 | Data processing |
| [Plotly](https://plotly.com/python/) | 6.0.0+ | Chart rendering |
| [MongoDB](https://www.mongodb.com) | — | Usage analytics |
| [Gunicorn](https://gunicorn.org) | 23.0.0+ | Production WSGI server |

**Architecture:** One Docker container per language, routed via Cloudflare Tunnel subdomains. All containers share the same codebase — differentiated only by the `APP_LANGUAGE` environment variable.

## 🐳 Self-Hosting

```bash
git clone https://github.com/zboardio/analyzeyourdata.git
cd analyzeyourdata
cp .env.example .env    # configure your settings
docker compose up       # starts all language instances
```

You'll need an [AG Grid Enterprise license](https://www.ag-grid.com/license-pricing/) and optionally a MongoDB connection for analytics. See `.env.example` for the full configuration reference.

## 🤝 Contributing

Contributions are welcome! The project uses Python 3.12+, Dash 4.0.0, and follows a modular callback architecture.

```bash
pip install -r requirements.txt
python app.py  # starts on http://127.0.0.1:8050
```

See `CLAUDE.md` for the full developer reference — project structure, callback patterns, environment variables, and i18n system.

## ⚠️ Known Limitations

- **Microsoft SharePoint** — Corporate/enterprise tenants may block anonymous sharing links due to organization security policies. Personal OneDrive links work reliably.
- **Airtable** — Requires a Personal Access Token with `data.records:read` and `schema.bases:read` scopes.

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

<p align="center">
  Developed by <strong><a href="https://zboardio-webpage.pages.dev/en/#hero">zboardio</a></strong>
</p>
