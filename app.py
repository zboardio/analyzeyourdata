import dash
from dash import dcc, html, clientside_callback, Input, Output
import dash_bootstrap_components as dbc
import dash_ag_grid as dag
import tracemalloc
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
from components.chart_config_section import create_chart_config_section
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

# Custom favicon (Dash 4.0+ requires custom index_string for non-.ico favicons)
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        <link rel="icon" type="image/svg+xml" href="/assets/favicon.svg">
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


@server.route('/api/version')
def api_version():
    """Public endpoint for build transparency — returns git commit and language."""
    from flask import jsonify
    return jsonify(git_commit=Config.GIT_COMMIT, language=Config.APP_LANGUAGE)

# Validate configuration on startup
config_errors = Config.validate_config()
if config_errors:
    print("Configuration Errors:")
    for error in config_errors:
        print(f"  - {error}")

# Get navbar and footer
navbar = create_navbar()
footer = create_footer()

# Variables
info_md = load_markdown_file("info.md")

# RAM monitoring
tracemalloc.start()

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

        # html.H1(t('app.title'), style={'textAlign': 'center'}),

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
        html.H4(t('datetime.step2_heading'), style={'marginTop': '30px', 'marginBottom': '10px'}),

        dbc.Row([
            dbc.Col([
                html.Div([
                    dbc.Label([
                        t('datetime.enable_label'),
                        html.I(className="fas fa-circle-info", id='datetime-toggle-tooltip',
                              style={'color': '#0098A3', 'marginLeft': '6px', 'cursor': 'pointer', 'fontSize': '1.1rem'})
                    ], id='datetime-toggle-label', style={'fontWeight': 'bold'}),
                    dbc.Tooltip(
                        t('datetime.toggle_tooltip'),
                        target='datetime-toggle-label', placement='top', style={'whiteSpace': 'pre-line'}
                    )
                ])
            ], width="auto", style={'display': 'flex', 'alignItems': 'center'}),

            dbc.Col([dbc.Label(t('datetime.disabled'))], width="auto", style={'display': 'flex', 'alignItems': 'center'}),

            dbc.Col([
                dbc.Switch(id='datetime-toggle', value=False, style={'marginLeft': '10px', 'marginRight': '10px'})
            ], width="auto", style={'display': 'flex', 'alignItems': 'center'}),

            dbc.Col([dbc.Label(t('datetime.enabled'))], width="auto", style={'display': 'flex', 'alignItems': 'center'}),
        ], style={'marginTop': '20px'}),

        html.Div([
            dbc.Row([
                dbc.Col([
                    dbc.Label(t('datetime.column_label')),
                    dcc.Dropdown(id='datetime-column', multi=False, placeholder=t('datetime.column_placeholder'))
                ]),
                dbc.Col([
                    dbc.Label(t('datetime.format_label')),
                    dcc.Dropdown(id='datetime-format', options=Config.DATETIME_FORMATS, multi=False,
                               placeholder=t('datetime.format_placeholder'), value='%Y-%m-%dT%H:%M:%S.%f')
                ]),
                dbc.Col([
                    dbc.Label([
                        t('datetime.custom_label'),
                        html.I(className="fas fa-circle-info", id='custom-format-tooltip-icon',
                              style={'color': '#0098A3', 'cursor': 'pointer', 'marginLeft': '6px'}),
                        html.A("🔗", href="https://www.programiz.com/python-programming/datetime/strftime",
                              target="_blank", style={'marginLeft': '8px', 'textDecoration': 'none'})
                    ], html_for='custom-datetime-format'),
                    dcc.Input(id='custom-datetime-format', placeholder=t('datetime.custom_placeholder'),
                             style={'padding': '3px', 'paddingLeft': '10px', 'width': '100%'}),
                    dbc.Tooltip(
                        t('datetime.custom_tooltip'),
                        target='custom-format-tooltip-icon', placement='top', style={'whiteSpace': 'pre-line'}
                    )
                ], id='custom-datetime-container', style={'display': 'none'})
            ], style={'marginTop': '10px'})
        ], id='datetime-input-container'),

        dbc.Row([
            dbc.Col([
                dbc.Button([html.I(className="fas fa-table me-2"), t('datetime.load_btn')],
                          id='confirm-button', color='primary', style={'width': '98%'})
            ], style={'display': 'flex', 'justifyContent': 'center'})
        ], style={'marginTop': '20px', 'marginBottom': '30px'}),

        dbc.Alert(id='error-alert', color='danger', is_open=False, style={"marginTop": "10px"}),
        html.Hr(),

        # AgGrid Section
        html.H4(t('grid.step3_heading'), style={'marginTop': '30px', 'marginBottom': '15px'}),

        dcc.Loading([
            html.Div([
                # AgGrid Table
                dbc.Row([
                    dbc.Col([
                        dag.AgGrid(
                            id='data-grid',
                            columnDefs=[],
                            rowData=[],
                            columnSize='sizeToFit',
                            defaultColDef={
                                'editable': False,
                                'enablePivot': True,
                                'enableRowGroup': True,
                                'enableValue': True,
                                'resizable': True,
                                'filter': True,
                                'sortable': True,
                            },
                            dashGridOptions={
                                'groupTotalRow': 'top',
                                'rowGroupPanelShow': 'always',
                                'groupDefaultExpanded': -1,
                                "sideBar": {"toolPanels": ["columns", "filters"]}, # After dash-ag-grid v34.x stable release whitch to "filters-new"
                            },
                            enableEnterpriseModules=True,
                            licenseKey=Config.AG_GRID_LICENSE_KEY,
                            className=Config.AG_GRID_THEME,
                            style={'height': f'{Config.AG_GRID_HEIGHT}px', 'marginBottom': '10px'}
                        )
                    ])
                ]),
                # AgGrid Export Buttons
                dbc.Row([
                    dbc.Col([
                        dbc.Button(
                            [html.I(className="fas fa-file-excel me-2"), t('grid.export_excel')],
                            id='grid-export-excel-btn', color='primary', className='mx-2', style={'width': '48%'}
                        ),
                        dbc.Button(
                            [html.I(className="fas fa-file-csv me-2"), t('grid.export_csv')],
                            id='grid-export-csv-btn', color='primary', className='mx-2', style={'width': '48%'}
                        ),
                    ], style={'display': 'flex', 'justifyContent': 'center'}),
                ], className="mt-3"),
                html.Div(id='grid-export-excel-dummy', style={'display': 'none'}),
                html.Div(id='grid-export-csv-dummy', style={'display': 'none'}),
            ], className='chart-container'),
        ], type='default', color='var(--primary-color)'),
        html.Hr(),

        # Multi-Chart Section
        html.H4(t('chart.step4_heading'), style={'marginTop': '30px', 'marginBottom': '20px'}),

        # Combined Dashboard Export (top)
        html.Div([
            dbc.Row([
                dbc.Col(html.H5(t('dashboard.heading'), className="mb-0"), className="d-flex align-items-center"),
                dbc.Col(
                    dbc.Button([html.I(className="fas fa-download me-2"), t('dashboard.download_btn')],
                              id='dashboard-download-button', color='primary'),
                    width="auto"
                ),
            ], className="g-3", justify="between"),
            dcc.Download(id="dashboard-file-download"),
        ], className='chart-container'),

        # Chart 1
        html.Div([
            create_chart_config_section(1),
            dcc.Loading(
                dcc.Graph(id='chart-1', style={'width': '100%', 'height': f'{Config.CHART_HEIGHT}px'}),
                type='default', color='var(--primary-color)'
            )
        ], className='chart-container'),
        html.Hr(),

        # Chart 2
        html.Div([
            create_chart_config_section(2),
            dcc.Loading(
                dcc.Graph(id='chart-2', style={'width': '100%', 'height': f'{Config.CHART_HEIGHT}px'}),
                type='default', color='var(--primary-color)'
            )
        ], className='chart-container'),
        html.Hr(),

        # Chart 3
        html.Div([
            create_chart_config_section(3),
            dcc.Loading(
                dcc.Graph(id='chart-3', style={'width': '100%', 'height': f'{Config.CHART_HEIGHT}px'}),
                type='default', color='var(--primary-color)'
            )
        ], className='chart-container'),
        html.Hr(),

        # Combined Dashboard Export (bottom, duplicate)
        html.Div([
            dbc.Row([
                dbc.Col(html.H5(t('dashboard.heading'), className="mb-0"), className="d-flex align-items-center"),
                dbc.Col(
                    dbc.Button([html.I(className="fas fa-download me-2"), t('dashboard.download_btn')],
                              id='dashboard-download-button-bottom', color='primary'),
                    width="auto"
                ),
            ], className="g-3", justify="between"),
            dcc.Download(id="dashboard-file-download-bottom"),
        ], className='chart-container'),
    ]),

    footer
])

# Register all callbacks
register_navbar_callbacks(app)
register_data_loading(app)
register_data_processing(app)
register_chart_callbacks(app)

# Grid export clientside callbacks (Excel via AG Grid Enterprise API, CSV via built-in)
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
