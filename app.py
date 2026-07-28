import dash
from dash import dcc, html, clientside_callback, Input, Output
import dash_bootstrap_components as dbc
import threading

from config import Config
from i18n import t
from utils.general import load_markdown_file
from utils.analytics import monitor_memory
from components.layout import (
    create_navbar, create_footer, create_feedback_modal,
    create_how_to_use_modal, create_email_toast, create_powered_by_section,
    register_navbar_callbacks
)
from components.data_source_section import create_data_source_section
from components.analysis_section import (
    create_datetime_section, create_grid_section, create_charts_section
)
from callbacks.data_loading import register_callbacks as register_data_loading
from callbacks.data_processing import register_callbacks as register_data_processing
from callbacks.chart_callbacks import register_callbacks as register_chart_callbacks

# Create the Dash app
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css",
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap",
    ]
)

# Custom favicon (Dash 4.0+ requires custom index_string for non-.ico favicons).
# SVG for modern browsers; ICO fallback for Safari and anything that ignores SVG icons.
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        <link rel="icon" type="image/svg+xml" href="/assets/favicon.svg">
        <link rel="alternate icon" type="image/x-icon" href="/assets/favicon.ico">
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

app.title = t('app.title')
server = app.server
server.secret_key = Config.SECRET_KEY
# Hard cap on request bodies (uploads are base64, grid/chart callbacks POST the
# dataset back as JSON — see MAX_CONTENT_LENGTH_MB in config.py)
server.config['MAX_CONTENT_LENGTH'] = Config.MAX_CONTENT_LENGTH_MB * 1024 * 1024


@server.route('/api/version')
def api_version():
    """Public endpoint for build transparency — returns git commit and language."""
    from flask import jsonify
    return jsonify(git_commit=Config.GIT_COMMIT, language=Config.APP_LANGUAGE)


@server.route('/favicon.ico')
def favicon_ico():
    """Root fallback for browsers that request /favicon.ico directly."""
    from flask import redirect
    return redirect('/assets/favicon.ico')

# Validate configuration on startup — warnings are logged, errors abort
config_errors, config_warnings = Config.validate_config()
for warning in config_warnings:
    print(f"Configuration warning: {warning}")
if config_errors:
    for error in config_errors:
        print(f"Configuration error: {error}")
    raise SystemExit("Invalid configuration — aborting startup.")

# Get navbar and footer
navbar = create_navbar()
footer = create_footer()

# Variables
info_md = load_markdown_file("info.md")

# Layout of the Dash app
app.layout = html.Div([
    navbar,
    create_feedback_modal(),
    create_how_to_use_modal(),
    create_email_toast(),

    html.Div(className='custom-container', children=[

        # Donation card
        dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.H5([
                            html.I(className="fas fa-mug-hot me-2"),
                            t('donate.heading')
                        ], className="mb-1"),
                        html.P(t('donate.description'), className="mb-0 text-muted"),
                    ], className="d-flex flex-column justify-content-center"),
                    dbc.Col([
                        dbc.Button([
                            html.I(className="fas fa-heart me-2"),
                            t('donate.btn')
                        ], href=Config.DONATE_URL, target="_blank", color="primary", size="lg")
                    ], width="auto", className="d-flex align-items-center"),
                ], align="center"),
            ])
        ], className="my-4", style={
            'border': '2px solid var(--primary-color)',
            'borderRadius': '12px',
            'background': 'linear-gradient(135deg, rgba(0,152,163,0.05), rgba(0,212,170,0.05))'
        }) if Config.DONATE_URL else html.Div(),

        html.Div(
            html.Img(
                src='/assets/image/zboardio-data-analysis.gif',
                className='hero-image',
                alt='Welcome to the zboardio.com',
            ),
            className='hero-section',
        ),

        dcc.Markdown(info_md, className="markdown-content", link_target="_blank"),

        create_powered_by_section(),

        html.Div([
            html.Hr(),
            html.H5(t('video.intro_heading'), style={'textAlign': 'center'}),
            html.Div(
                html.Iframe(
                    src=Config.YOUTUBE_INTRO_URL,
                    style={'width': '100%', 'height': '450px', 'border': 'none', 'borderRadius': '8px'},
                    allow='accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share; fullscreen',
                ),
                style={'maxWidth': '800px', 'margin': '0 auto', 'padding': '10px 0'},
            ),
        ]) if Config.YOUTUBE_INTRO_URL else html.Div(),

        # Data Source Section
        html.Hr(),
        create_data_source_section(),
        html.Hr(),

        # Datetime Processing Section
        create_datetime_section(),
        html.Hr(),

        # AgGrid Section
        create_grid_section(),
        html.Hr(),

        # Multi-Chart Section (3 charts + dashboard export)
        create_charts_section(),
    ]),

    footer
])

# Register all callbacks
register_navbar_callbacks(app)
register_data_loading(app)
register_data_processing(app)
register_chart_callbacks(app)

# Grid export clientside callbacks (Excel via AG Grid Enterprise API, CSV via built-in)
if Config.AG_GRID_ENTERPRISE_ENABLED:
    clientside_callback(
        """async function(n_clicks) {
            if (n_clicks) {
                const api = await dash_ag_grid.getApiAsync("data-grid");
                api.exportDataAsExcel({exportAsExcelTable: true});
            }
            return dash_clientside.no_update;
        }""",
        Output('grid-export-excel-dummy', 'children'),
        Input('grid-export-excel-btn', 'n_clicks'),
        prevent_initial_call=True,
    )

clientside_callback(
    """async function(n_clicks) {
        if (n_clicks) {
            const api = await dash_ag_grid.getApiAsync("data-grid");
            api.exportDataAsCsv();
        }
        return dash_clientside.no_update;
    }""",
    Output('grid-export-csv-dummy', 'children'),
    Input('grid-export-csv-btn', 'n_clicks'),
    prevent_initial_call=True,
)

# Memory monitoring
if Config.MEMORY_MONITORING_ENABLED:
    threading.Thread(target=monitor_memory, args=(Config.MEMORY_MONITORING_INTERVAL,), daemon=True).start()

if __name__ == '__main__':
    app.run(host=Config.APP_HOST, port=Config.APP_PORT, debug=Config.APP_DEBUG)
