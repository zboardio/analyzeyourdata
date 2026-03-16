from dash import dcc, html
import dash_bootstrap_components as dbc

from config import Config
from i18n import t
from utils.general import get_variable


def create_data_source_section():
    """Create enhanced data source selection section with horizontal layout"""
    return html.Div([
        html.H4(t('data_source.step1_heading', max_size=Config.MAX_FILE_SIZE_MB),
                style={'marginTop': '30px', 'marginBottom': '20px'}),

        # Horizontal Data source selection radio buttons
        dbc.Row([
            dbc.Label(t('data_source.choose_source'), style={'fontWeight': 'bold', 'marginBottom': '15px'}),
            dbc.RadioItems(
                id='data-source-type',
                options=[
                    {'label': [html.I(className="fas fa-upload me-2"), t('data_source.upload')], 'value': 'upload'},
                    {'label': [html.I(className="fab fa-google me-2"), t('data_source.google_sheets')], 'value': 'google_sheets'},
                    {'label': [html.I(className="fas fa-table me-2"), t('data_source.airtable')], 'value': 'airtable'},
                ],
                value='upload',
                inline=True,  # Changed to horizontal layout
                className='mb-4',
                style={'display': 'flex', 'flexWrap': 'wrap', 'gap': '20px'}
            ),
        ]),

        # Upload section
        html.Div([
            dcc.Upload(
                id='upload-data',
                children=html.Div([t('data_source.drag_drop'), html.A(t('data_source.select_files'))]),
                style={
                    'width': '100%', 'height': '120px', 'lineHeight': '120px',
                    'borderWidth': '2px', 'borderStyle': 'dashed', 'borderRadius': '8px',
                    'textAlign': 'center', 'marginRight': '10px', 'marginLeft': '10px',
                    'fontWeight': '600'
                },
                className='upload-area',
                multiple=False
            ),
            # Test dataset link for Direct File Upload
            html.Div([
                html.I(className="fas fa-flask me-2"),
                html.Span(t('test_dataset.try_label_plural')),
                html.A(
                    [t('test_dataset.browse_btn'), " ", html.I(className="fas fa-arrow-right ms-1")],
                    href=get_variable('URL_TEST_DATASET_FOLDER'),
                    target='_blank',
                    className='btn btn-outline-primary ms-2',
                ),
            ], id='test-dataset-upload-section', className='test-dataset-section test-dataset-inline',
               style={'display': 'none'} if not get_variable('URL_TEST_DATASET_FOLDER') else {}),

            html.Div(id='delimiter-selection-container', style={'display':'none', 'marginTop':'1rem'}, children=[
                dbc.Alert(id='delimiter-preview-alert', is_open=False, color='warning', style={'marginTop':'20px'}),
                dbc.Label(t('delimiter.label'), style={'marginTop': '1.25rem', 'marginBottom': '0.75rem'}),
                dbc.Row([
                    dbc.Col(
                        dcc.Dropdown(
                            id='delimiter-dropdown',
                            options=[
                                {'label': t('delimiter.comma'), 'value': ','},
                                {'label': t('delimiter.semicolon'), 'value': ';'},
                                {'label': t('delimiter.tab'), 'value': '\t'},
                                {'label': t('delimiter.space'), 'value': ' '},
                                {'label': t('delimiter.pipe'), 'value': '|'},
                                {'label': t('delimiter.custom'), 'value': 'custom'}
                            ],
                            clearable=False,
                        ), width='auto',
                    ),
                    dbc.Col(
                        dcc.Input(
                            id='custom-delimiter-input',
                            placeholder=t('delimiter.custom_placeholder'),
                            style={'display':'none', 'width':'250px'}
                        ), width='auto',
                    ),
                    dbc.Col(
                        dbc.Button([html.I(className="fas fa-check me-2"), t('delimiter.confirm_btn')],
                                  id='delimiter-confirm-btn', color='primary'),
                        width='auto',
                    ),
                ], align='center', className='g-3'),
            ]),

            # SQLite table selection container
            html.Div([
                dbc.Alert(id='sqlite-info-alert', is_open=False, color='info', style={'marginTop':'20px'}),
                dbc.Label(t('sqlite.select_table_label'), style={'fontWeight': 'bold', 'marginTop': '15px'}),
                dcc.Dropdown(
                    id='sqlite-table-dropdown',
                    placeholder=t('sqlite.table_placeholder'),
                    style={'marginBottom':'10px'}
                ),
                dbc.Button([html.I(className="fas fa-table me-2"), t('sqlite.load_btn')],
                          id='sqlite-table-load-btn', color='primary', className='btn-load-full'),
            ], id='sqlite-table-selection-container', style={'display': 'none'}),
        ], id='upload-section'),

        # SharePoint URL section
        html.Div([
            dbc.Row([
                dbc.Col([
                    dbc.Label(t('sharepoint.url_label'), style={'fontWeight': 'bold'}),
                    dbc.InputGroup([
                        dbc.Input(id='sharepoint-url-input', placeholder=t('sharepoint.url_placeholder'), type='url'),
                        dbc.Button([html.I(className="fas fa-download me-2"), t('sharepoint.load_btn')],
                                  id='sharepoint-load-btn', color='primary')
                    ], className='mb-3'),
                    dbc.Alert(t('sharepoint.access_alert'),
                             color='info', className='mb-3'),
                    # Test dataset for SharePoint
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-flask me-2"),
                            html.Span(t('test_dataset.try_label')),
                        ], className='mb-2'),
                        dbc.InputGroup([
                            dbc.Input(
                                id='test-url-sharepoint',
                                value=get_variable('URL_TEST_DATASET_SHAREPOINT'),
                                readonly=True,
                            ),
                            dbc.Button(
                                [html.I(className="fas fa-copy me-1"), html.Span(t('test_dataset.copy_btn'), id='copy-sharepoint-label')],
                                id='copy-sharepoint-test-url',
                                color='outline-primary',
                            ),
                        ]),
                    ], id='test-dataset-sharepoint-section', className='test-dataset-section',
                       style={'display': 'none'} if not get_variable('URL_TEST_DATASET_SHAREPOINT') else {}),
                ], width=12)
            ]),
            # Sheet selection for SharePoint
            html.Div([
                dbc.Label(t('sharepoint.select_sheet'), style={'fontWeight': 'bold'}),
                dcc.Dropdown(id='sharepoint-sheet-dropdown', placeholder=t('sharepoint.sheet_placeholder'), className='mb-3'),
                dbc.Button([html.I(className="fas fa-table me-2"), t('sharepoint.load_sheet_btn')],
                          id='sharepoint-sheet-load-btn', color='primary', className='btn-load-full')
            ], id='sharepoint-sheet-selection', style={'display': 'none'})
        ], id='sharepoint-section', style={'display': 'none'}),

        # Google Sheets URL section
        html.Div([
            dbc.Row([
                dbc.Col([
                    dbc.Label(t('google_sheets.url_label'), style={'fontWeight': 'bold'}),
                    dbc.InputGroup([
                        dbc.Input(id='google-sheets-url-input', placeholder=t('google_sheets.url_placeholder'), type='url'),
                        dbc.Button([html.I(className="fas fa-download me-2"), t('google_sheets.load_btn')],
                                  id='google-sheets-load-btn', color='primary')
                    ], className='mb-3'),
                    dbc.Alert(t('google_sheets.access_alert'),
                             color='info', className='mb-3'),
                ], width=12)
            ]),
            # Test dataset for Google Sheets
            html.Div([
                html.Div([
                    html.I(className="fas fa-flask me-2"),
                    html.Span(t('test_dataset.try_label')),
                ], className='mb-2'),
                dbc.InputGroup([
                    dbc.Input(
                        id='test-url-google',
                        value=get_variable('URL_TEST_DATASET_GOOGLE'),
                        readonly=True,
                    ),
                    dbc.Button(
                        [html.I(className="fas fa-copy me-1"), html.Span(t('test_dataset.copy_btn'), id='copy-google-label')],
                        id='copy-google-test-url',
                        color='outline-primary',
                    ),
                ]),
            ], id='test-dataset-google-section', className='test-dataset-section',
               style={'display': 'none'} if not get_variable('URL_TEST_DATASET_GOOGLE') else {}),
        ], id='google-sheets-section', style={'display': 'none'}),

        # Airtable API section
        html.Div([
            dbc.Row([
                dbc.Col([
                    dbc.Label(t('airtable.config_label'), style={'fontWeight': 'bold', 'marginBottom': '15px'}),

                    # API Key input
                    dbc.Label(t('airtable.api_key_label'), style={'fontWeight': 'bold'}),
                    html.Form([
                        dbc.InputGroup([
                            dbc.Input(
                                id='airtable-api-key-input',
                                placeholder=t('airtable.api_key_placeholder'),
                                type='password',
                                autocomplete='off'
                            ),
                            dbc.InputGroupText(html.I(className="fas fa-key"))
                        ], className='mb-3'),
                    ], **{'data-dash-no-submit': 'true'}, style={'margin': '0'}),

                    # Base ID input
                    dbc.Label(t('airtable.base_id_label'), style={'fontWeight': 'bold'}),
                    dbc.InputGroup([
                        dbc.Input(
                            id='airtable-base-id-input',
                            placeholder=t('airtable.base_id_placeholder'),
                            type='text'
                        ),
                        dbc.InputGroupText(html.I(className="fas fa-database"))
                    ], className='mb-3'),

                    # Connect button
                    dbc.Button([
                        html.I(className="fas fa-plug me-2"),
                        t('airtable.connect_btn')
                    ], id='airtable-connect-btn', color='primary', className='btn-load-full'),

                    # Help alert
                    dbc.Alert([
                        html.H6(t('airtable.help_heading'), className="alert-heading"),
                        html.P([
                            t('airtable.help_step1_prefix'),
                            html.A(t('airtable.help_step1_link'), href="https://airtable.com/create/tokens", target="_blank"),
                            t('airtable.help_step1_suffix')
                        ]),
                        html.P([
                            t('airtable.help_step2_prefix'),
                            html.A(t('airtable.help_step2_link'), href="https://airtable.com/api", target="_blank")
                        ]),
                        html.P(t('airtable.help_step3'))
                    ], color='info', className='mb-3'),

                ], width=12)
            ]),

            # Table selection for Airtable
            html.Div([
                dbc.Label(t('airtable.select_table'), style={'fontWeight': 'bold'}),
                dcc.Dropdown(id='airtable-table-dropdown', placeholder=t('airtable.table_placeholder'), className='mb-3'),
                dbc.Button([html.I(className="fas fa-table me-2"), t('airtable.load_table_btn')],
                          id='airtable-table-load-btn', color='primary', className='btn-load-full')
            ], id='airtable-table-selection', style={'display': 'none'})
        ], id='airtable-section', style={'display': 'none'}),

        # Loading indicator
        html.Div([
            dbc.Spinner([html.Div(id='loading-content')], id='data-loading-spinner', size='lg', color='primary')
        ], id='loading-container', className='loading-container', style={'display': 'none', 'textAlign': 'center', 'margin': '20px 0'}),

        # Storage and alerts
        dcc.Store(id='stored-data', storage_type='memory'),
        dcc.Store(id='stored-sheet-names', storage_type='memory'),
        dcc.Store(id='stored-source-url', storage_type='memory'),
        dcc.Store(id='stored-sqlite-path', storage_type='memory'),
        dcc.Store(id='stored-sqlite-tables', storage_type='memory'),
        dcc.Store(id='stored-airtable-credentials', storage_type='memory'),
        dcc.Store(id='stored-airtable-tables', storage_type='memory'),
        dcc.Loading([
            dbc.Alert(id='upload-alert', is_open=False, style={'marginTop': '30px'})
        ], type='default', color='var(--primary-color)')
    ])
