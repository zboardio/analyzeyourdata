# Third-Party Licenses

This project uses the following third-party libraries:

## AG Grid Enterprise

This application uses AG Grid Enterprise features (row grouping, pivoting, etc.).
AG Grid Enterprise is licensed separately under a commercial license.

**Important:** The `AG_GRID_LICENSE_KEY` environment variable is required to use
Enterprise features. The maintainer of this repository holds a valid AG Grid
Enterprise license for the hosted deployment. If you fork or deploy this
application, you must obtain your own license from AG Grid.

- AG Grid Licensing: https://www.ag-grid.com/license-pricing/
- AG Grid EULA: https://www.ag-grid.com/eula/

Without a valid license key, AG Grid will display a watermark and license warning.
Community features will still work.

## Other Dependencies

All other dependencies (Dash, Plotly, Pandas, etc.) are MIT or BSD licensed
and fully compatible with this project's MIT license. See `requirements.txt`
for the complete list.
