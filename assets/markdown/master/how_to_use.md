# How to Use Analyze Your Data

## Quick Overview

**Analyze Your Data** lets you upload data, explore it in an interactive grid, and create up to 3 independent charts — all in your browser. No data is stored on the server; everything stays in your session.

---

## Step 1: Load Your Data

Choose one of the supported data sources:

### Direct File Upload
- Click the upload area or drag & drop your file
- **Supported formats:** Excel (`.xlsx`, `.xls`), CSV (`.csv`, `.txt`, `.log`), JSON, Parquet, HDF5, SQLite (`.db`, `.sqlite`, `.sqlite3`)
- For CSV/TXT/LOG files, confirm or change the delimiter (comma, semicolon, tab, pipe, or space)
- Maximum file size: **{{VALUE_MAX_FILE_SIZE_MB}} MB**

### SQLite Database
- Upload a `.db`, `.sqlite`, or `.sqlite3` file
- Browse available tables with row and column counts
- Select the table you want to analyze and click **Load Selected Table**

### Microsoft SharePoint / OneDrive — Discontinued

**Microsoft has disabled unauthenticated access to the OneDrive sharing API.** The API endpoint that previously allowed loading files from public SharePoint/OneDrive links now returns authentication errors. This is a change made by Microsoft — not by this application.

Microsoft's replacement requires Azure AD OAuth 2.0 authentication, which adds significant friction (Microsoft account sign-in, organization admin approval) with limited guarantees of long-term stability.

> **Recommended alternative:** Download your file from SharePoint/OneDrive to your computer, then use **Direct File Upload** above. This is faster, more reliable, and keeps your data fully in your control.

### Google Sheets
- Copy the URL from the browser bar while viewing the desired sheet tab and paste it
- The sheet tab (GID) is automatically detected from the URL
- The document must be shared as "Anyone with the link can view"

**How to get the URL:** In Google Sheets, click Share → set to "Anyone with the link" → Viewer. Then navigate to the sheet tab you want to load and copy the URL from your browser's address bar (it contains the sheet ID automatically).

**Test URL** — try this to verify your setup:
```
{{URL_TEST_DATASET_GOOGLE}}
```

### Airtable

Airtable connection requires a **Personal Access Token** and a **Base ID**.

#### How to create a Personal Access Token

1. Go to [airtable.com/create/tokens]({{URL_DOCUMENTATION_AIRTABLE_TOKENS}}) (or navigate to your Account → Developer Hub → Personal Access Tokens)
2. Click **Create new token**
3. Give it a name (e.g. "Analyze Your Data")
4. Under **Scopes**, add at minimum:
   - `data.records:read` — to read table records
   - `schema.bases:read` — to list tables in a base
5. Under **Access**, select the specific base(s) you want to connect to
6. Click **Create token** and copy it immediately — you won't be able to see it again

> **Reference:** [Creating Personal Access Tokens — Airtable Support]({{URL_DOCUMENTATION_AIRTABLE_PAT}})

#### How to find your Base ID

1. Open your Airtable base in the browser
2. Look at the URL: `https://airtable.com/appXXXXXXXXXXXXXX/...`
3. The Base ID is the part starting with `app` (e.g. `appXXXXXXXXXXXXXX`)

#### Loading data

1. Enter your **Personal Access Token** in the token field
2. Enter your **Base ID**
3. Click **Connect to Airtable** — available tables will be listed
4. Select a table and click **Load Selected Table**

> **Tip:** Your token is held in browser session memory only — it is never stored on the server. Closing the browser tab clears it.


> **Tip:** For sensitive or private data, use Direct File Upload — your data never leaves the browser.

---

## Step 2: Datetime Processing (Optional)

Datetime processing is **disabled by default**. When disabled, your data loads directly into the grid — no extra steps needed.

If your data contains a datetime column and you want time-based analysis:

1. Toggle datetime processing to **Enabled**
2. Select the **Datetime Column** from the dropdown
3. Choose the matching **Datetime Format** (or enter a custom Python `strftime()` format)
4. Click **Load data to AgGrid Table**

Generated columns include: `tsYear`, `tsMonth`, `tsDay`, `tsHour`, `tsMinute`, `tsDayOfWeek`, `tsWeekNumber`, `tsDate`, and more.

---

## Step 3: Explore Your Data in AG Grid

**AG Grid** provides powerful interactive data exploration with built-in side panels:

- **Sort** — click any column header
- **Filter** — click the filter icon on any column header to set conditions, or use the **Filters panel** on the right side to manage all column filters in one place
- **Group** — drag column headers into the "Row Group" panel above the table
- **Pivot** — enable pivot mode from the **Columns panel** on the right side for cross-tabulations
- **Resize** — drag column borders to adjust widths
- **Aggregate** — when grouping, AG Grid shows subtotals and grand totals
- **Columns panel** — toggle column visibility, reorder columns, and configure pivot/value settings from the side panel
- **Filters panel** — view and manage all active filters across columns from one convenient panel

> **Key:** The charts below read from the **currently filtered/grouped data** visible in AG Grid. Every filter, sort, or group action updates all charts instantly — **this is the core power of the tool.** Use AG Grid as your interactive data slicer and see the results reflected in real-time across all your visualizations.

### AG Grid Export

Use the **Export to Excel** and **Export to CSV** buttons below AG Grid to download the currently visible data:

- The export always reflects the **current view** of AG Grid — filters, grouping, and sorting are all respected
- **Excel export** includes table formatting with active filters, so you can continue filtering directly in Excel
- **CSV export** provides a clean flat file of the filtered data
- This means you can apply different filter criteria in AG Grid and export multiple times to create **separate files for different subsets** of your data — a powerful workflow for data analysis and reporting

> **Tip:** You can also right-click anywhere in the AG Grid table for additional export options via the context menu.

---

## Step 4: Create Charts

You can create up to **3 independent charts**, each with its own configuration:

1. **Show/Hide** — use the toggle to show or hide each chart section
2. **Chart Type** — choose from: Scatter, Scatter (multi y), Line, Bar (grouped), Bar (stacked), Histogram (grouped), Histogram (stacked), Pie, Bubble, Heatmap, Log, Sunburst, Icicle
3. **X-Axis Column** — select the column for the horizontal axis
4. **Y-Axis Column(s)** — select one or more columns for the vertical axis
5. **Color Column** (optional) — color data points by a categorical column
6. **Z-Axis Column** (optional) — for Bubble and Heatmap chart types
7. **Titles** — set custom chart title, X-axis title, and Y-axis title

Charts read from the currently filtered/grouped AG Grid data. **Every filter, sort, or group action in AG Grid updates all charts instantly.**

---

## Step 5: Export

### Individual Charts
- Click **Download Chart as HTML** below each chart to save it as a standalone interactive HTML file

### All Charts (ZIP)
- Click **Download All Charts** at the top or bottom of the chart section
- Each active chart is exported as a separate standalone HTML file, bundled into a single ZIP download
- Only charts with data are included in the ZIP

### AG Grid Data
- Use the **Export to Excel** or **Export to CSV** buttons below AG Grid (see Step 3 above)
- Exports exactly the data currently visible in AG Grid (respects filters, grouping, sorting)

> **Tip:** Exported HTML chart files are fully interactive — you can zoom, hover for tooltips, and pan — no software needed, just a web browser.

---

## Tips & Troubleshooting

| Issue | Solution |
|---|---|
| File upload fails | Check that the file is under {{VALUE_MAX_FILE_SIZE_MB}} MB and in a supported format |
| SharePoint link doesn't work | Microsoft has disabled unauthenticated API access. Download the file and use Direct File Upload instead. |
| Google Sheet won't load | Make sure sharing is set to "Anyone with the link can view" |
| Airtable won't connect | Verify your Personal Access Token has `data.records:read` and `schema.bases:read` scopes, and the Base ID starts with `app` |
| Datetime parsing errors | Verify the selected format matches your data. Try a custom format if needed |
| Charts are empty | Make sure data is loaded in AG Grid and X/Y columns are selected |
| AG Grid shows no data after filter | Clear or adjust your column filters in the Filters panel |

---

## Data Privacy

- All uploaded data is processed **in-memory only** (never written to disk or a database)
- Data is stored in your **browser session** — closing the tab clears everything
- No uploaded data is sent to external services
- Only voluntary feedback submissions and anonymous usage analytics are stored
- See [PRIVACY.md]({{URL_DOCUMENTATION_AYD_PRIVACY}}) for full details
