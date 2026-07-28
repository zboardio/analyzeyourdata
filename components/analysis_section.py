from dash import dcc, html
import dash_bootstrap_components as dbc
import dash_ag_grid as dag

from config import Config
from i18n import t, load_aggrid_locale
from components.chart_config_section import create_chart_config_section


def create_datetime_section():
    """Step 2: optional datetime processing controls."""
    return html.Div([
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
    ])


def create_grid_section():
    """Step 3: AG Grid table with export buttons.

    Community by default; Enterprise features (pivot, grouping, sidebar,
    Excel export) only when enabled via config. Grid UI strings are localized
    via localeText for non-English languages.
    """
    grid_default_col_def = {
        'editable': False,
        'resizable': True,
        'filter': True,
        'sortable': True,
    }
    grid_options = {}
    locale_text = load_aggrid_locale()
    if locale_text:
        grid_options['localeText'] = locale_text
    if Config.AG_GRID_ENTERPRISE_ENABLED:
        grid_default_col_def.update({
            'enablePivot': True,
            'enableRowGroup': True,
            'enableValue': True,
        })
        grid_options.update({
            'groupTotalRow': 'top',
            'rowGroupPanelShow': 'always',
            'groupDefaultExpanded': -1,
            "sideBar": {"toolPanels": ["columns", "filters"]}, # After dash-ag-grid v34.x stable release whitch to "filters-new"
        })

    return html.Div([
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
                            defaultColDef=grid_default_col_def,
                            dashGridOptions=grid_options,
                            enableEnterpriseModules=Config.AG_GRID_ENTERPRISE_ENABLED,
                            licenseKey=Config.AG_GRID_LICENSE_KEY,
                            className=Config.AG_GRID_THEME,
                            style={'height': f'{Config.AG_GRID_HEIGHT}px', 'marginBottom': '10px'}
                        )
                    ])
                ]),
                # AgGrid Export Buttons (Excel export requires AG Grid Enterprise)
                dbc.Row([
                    dbc.Col(
                        ([dbc.Button(
                            [html.I(className="fas fa-file-excel me-2"), t('grid.export_excel')],
                            id='grid-export-excel-btn', color='primary', className='mx-2', style={'width': '48%'}
                        )] if Config.AG_GRID_ENTERPRISE_ENABLED else []) +
                        [dbc.Button(
                            [html.I(className="fas fa-file-csv me-2"), t('grid.export_csv')],
                            id='grid-export-csv-btn', color='primary', className='mx-2', style={'width': '48%'}
                        )],
                        style={'display': 'flex', 'justifyContent': 'center'}),
                ], className="mt-3"),
                html.Div(id='grid-export-excel-dummy', style={'display': 'none'}) if Config.AG_GRID_ENTERPRISE_ENABLED else html.Div(),
                html.Div(id='grid-export-csv-dummy', style={'display': 'none'}),
            ], className='chart-container'),
        ], type='default', color='var(--primary-color)'),
    ])


def _create_dashboard_export_row(button_id, download_id):
    """Combined dashboard export row — rendered above and below the charts."""
    return html.Div([
        dbc.Row([
            dbc.Col(html.H5(t('dashboard.heading'), className="mb-0"), className="d-flex align-items-center"),
            dbc.Col(
                dbc.Button([html.I(className="fas fa-download me-2"), t('dashboard.download_btn')],
                          id=button_id, color='primary'),
                width="auto"
            ),
        ], className="g-3", justify="between"),
        dcc.Download(id=download_id),
    ], className='chart-container')


def create_charts_section():
    """Step 4: three independent chart panels with dashboard export."""
    chart_blocks = []
    for i in range(1, 4):
        chart_blocks.append(html.Div([
            create_chart_config_section(i),
            dcc.Loading(
                dcc.Graph(id=f'chart-{i}', style={'width': '100%', 'height': f'{Config.CHART_HEIGHT}px'}),
                type='default', color='var(--primary-color)'
            )
        ], className='chart-container'))
        chart_blocks.append(html.Hr())

    return html.Div([
        html.H4(t('chart.step4_heading'), style={'marginTop': '30px', 'marginBottom': '20px'}),
        _create_dashboard_export_row('dashboard-download-button', 'dashboard-file-download'),
        *chart_blocks,
        _create_dashboard_export_row('dashboard-download-button-bottom', 'dashboard-file-download-bottom'),
    ])
