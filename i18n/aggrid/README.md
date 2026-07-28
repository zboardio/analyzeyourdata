# AG Grid UI locale files

Per-language `localeText` dictionaries for the AG Grid table, loaded at startup
for the container's `APP_LANGUAGE` and passed via `dashGridOptions['localeText']`.

## Provenance

- All files except `sl.json` are extracted verbatim from the official
  [`@ag-grid-community/locale`](https://www.npmjs.com/package/@ag-grid-community/locale)
  npm package, version **33.3.2** (matching the bundled AG Grid 33.x), which is
  published under the **MIT license** (© AG Grid Ltd.).
- Language mapping: `cs`→CZ, `da`→DK, `sv`→SE, `uk`→UA; all others map 1:1.
- `sl.json` (Slovenian) is **not** available upstream — it is a project-maintained
  translation of the core grid strings (filters, menus, tool panels, grouping,
  export, pagination). Keys not present fall back to AG Grid's built-in English
  defaults per key. Native-speaker review and contributions are welcome.

## Updating

When `dash-ag-grid` is upgraded to a new AG Grid major version, re-extract the
dictionaries from the matching `@ag-grid-community/locale` version:

```bash
npm pack @ag-grid-community/locale@<version>
# then serialize each AG_GRID_LOCALE_* export to i18n/aggrid/<lang>.json
```
