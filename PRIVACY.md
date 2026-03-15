# Data Privacy Policy

## Your Data Stays in Your Browser

- All uploaded files are processed in-memory only (Pandas DataFrame)
- Data is stored in browser session memory (`dcc.Store`) — never on the server
- No uploaded data is written to disk, database, or external services
- Closing the browser tab clears all data

## What We Do Store

- **Feedback submissions** (voluntary): category, message, language, timestamp, git_commit
- **Anonymous usage analytics**: event type, data source type, file format, row/column counts, language, timestamp
- No file contents, column names, or actual data values are ever logged

## External Data Sources

- Google Sheets/Airtable data is fetched server-side, processed in-memory, then sent to your browser
- No external source data is cached or stored on the server
- Credentials (Airtable API keys) are held in browser session memory only

## Build Transparency

- Every deployment includes a git commit hash (visible in the footer)
- Source code is public — anyone can audit all data handling paths
- `/api/version` endpoint returns the running commit for verification

## Open Source

- Full source code available on [GitHub](https://github.com/your-repo)
- Reproducible Docker builds from public Dockerfile
