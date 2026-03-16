import os
import dash
from dash import dcc, html, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import pandas as pd
import base64
import csv
import tempfile

from config import Config
from i18n import t
from utils.data_sources import DataSourceHandler
from utils.data_processing import load_sqlite_tables, load_sqlite_table_data, parse_uploaded_file
from utils.mongodb import log_usage


def register_callbacks(app):

    # Clientside callback: copy SharePoint test URL to clipboard
    app.clientside_callback(
        """
        function(n_clicks) {
            if (!n_clicks) return window.dash_clientside.no_update;
            var input = document.getElementById('test-url-sharepoint');
            if (input) {
                navigator.clipboard.writeText(input.value);
                var label = document.getElementById('copy-sharepoint-label');
                if (label) {
                    var original = label.textContent;
                    label.textContent = '""" + t('test_dataset.copied_btn') + """';
                    setTimeout(function() { label.textContent = original; }, 1500);
                }
            }
            return window.dash_clientside.no_update;
        }
        """,
        Output('copy-sharepoint-test-url', 'title'),
        Input('copy-sharepoint-test-url', 'n_clicks'),
        prevent_initial_call=True
    )

    # Clientside callback: copy Google Sheets test URL to clipboard
    app.clientside_callback(
        """
        function(n_clicks) {
            if (!n_clicks) return window.dash_clientside.no_update;
            var input = document.getElementById('test-url-google');
            if (input) {
                navigator.clipboard.writeText(input.value);
                var label = document.getElementById('copy-google-label');
                if (label) {
                    var original = label.textContent;
                    label.textContent = '""" + t('test_dataset.copied_btn') + """';
                    setTimeout(function() { label.textContent = original; }, 1500);
                }
            }
            return window.dash_clientside.no_update;
        }
        """,
        Output('copy-google-test-url', 'title'),
        Input('copy-google-test-url', 'n_clicks'),
        prevent_initial_call=True
    )

    @app.callback(
        [Output('upload-section', 'style'),
         Output('sharepoint-section', 'style'),
         Output('google-sheets-section', 'style'),
         Output('airtable-section', 'style')],
        Input('data-source-type', 'value')
    )
    def toggle_data_source_sections(source_type):
        upload_style = {'display': 'block'} if source_type == 'upload' else {'display': 'none'}
        sharepoint_style = {'display': 'block'} if source_type == 'sharepoint' else {'display': 'none'}
        google_style = {'display': 'block'} if source_type == 'google_sheets' else {'display': 'none'}
        airtable_style = {'display': 'block'} if source_type == 'airtable' else {'display': 'none'}
        return upload_style, sharepoint_style, google_style, airtable_style

    @app.callback(
        [Output('stored-airtable-credentials', 'data'),
         Output('stored-airtable-tables', 'data'),
         Output('airtable-table-selection', 'style'),
         Output('airtable-table-dropdown', 'options'),
         Output('upload-alert', 'children', allow_duplicate=True),
         Output('upload-alert', 'color', allow_duplicate=True),
         Output('upload-alert', 'is_open', allow_duplicate=True)],
        Input('airtable-connect-btn', 'n_clicks'),
        [State('airtable-api-key-input', 'value'),
         State('airtable-base-id-input', 'value')],
        prevent_initial_call=True
    )
    def handle_airtable_connection(n_clicks, api_key, base_id):
        if not n_clicks or not api_key or not base_id:
            return dash.no_update, dash.no_update, {'display': 'none'}, [], "", 'info', False

        try:
            # Validate credentials
            if not DataSourceHandler.validate_airtable_credentials(api_key, base_id):
                alert = html.Div([
                    html.P(f"❌ {t('airtable.invalid_credentials')}"),
                    html.P(t('airtable.invalid_credentials_detail'))
                ])
                return dash.no_update, dash.no_update, {'display': 'none'}, [], alert, 'danger', True

            # Get tables
            tables = DataSourceHandler.get_airtable_tables(api_key, base_id)

            if not tables:
                alert = html.Div([
                    html.P(f"⚠️ {t('airtable.no_tables')}"),
                    html.P(t('airtable.no_tables_detail'))
                ])
                return dash.no_update, dash.no_update, {'display': 'none'}, [], alert, 'warning', True

            # Create table dropdown options
            table_options = []
            for table in tables:
                field_count = len(table.get('fields', []))
                label = f"{table['name']} ({t('messages.fields_count', count=field_count)})"
                table_options.append({'label': label, 'value': table['name']})

            # Store credentials
            credentials = {'api_key': api_key, 'base_id': base_id}

            alert = html.Div([
                html.P(f"✅ {t('airtable.connected')}"),
                html.P(t('airtable.tables_found', count=len(tables)))
            ])

            return credentials, tables, {'display': 'block'}, table_options, alert, 'success', True

        except Exception as e:
            alert = html.Div([html.P(f"❌ {t('airtable.error_connecting')}"), html.P(str(e))])
            return dash.no_update, dash.no_update, {'display': 'none'}, [], alert, 'danger', True

    @app.callback(
        Output('custom-delimiter-input', 'style'),
        Input('delimiter-dropdown', 'value')
    )
    def toggle_custom_delimiter_input(delimiter_value):
        if delimiter_value == 'custom':
            return {'display': 'block', 'width': '150px', 'marginBottom': '10px'}
        return {'display': 'none'}

    @app.callback(
        [Output('stored-data', 'data'),
         Output('stored-sheet-names', 'data'),
         Output('stored-source-url', 'data'),
         Output('sharepoint-sheet-selection', 'style'),
         Output('sharepoint-sheet-dropdown', 'options'),
         Output('upload-alert', 'children'),
         Output('upload-alert', 'color'),
         Output('upload-alert', 'is_open'),
         Output('loading-container', 'style')],
        [Input('sharepoint-load-btn', 'n_clicks'),
         Input('sharepoint-sheet-load-btn', 'n_clicks')],
        [State('sharepoint-url-input', 'value'),
         State('sharepoint-sheet-dropdown', 'value'),
         State('stored-source-url', 'data')]
    )
    def handle_sharepoint_data(load_clicks, sheet_clicks, url, selected_sheet, stored_url):
        ctx = callback_context
        if not ctx.triggered:
            return dash.no_update, dash.no_update, dash.no_update, {'display': 'none'}, [], "", 'info', False, {'display': 'none'}

        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

        try:
            if trigger_id == 'sharepoint-load-btn' and load_clicks and url:
                if not DataSourceHandler.validate_url(url, 'sharepoint'):
                    alert = html.Div([
                        html.P(f"❌ {t('sharepoint.invalid_url')}"),
                        html.P(t('sharepoint.invalid_url_detail'))
                    ])
                    return dash.no_update, dash.no_update, dash.no_update, {'display': 'none'}, [], alert, 'warning', True, {'display': 'none'}

                df, sheet_names = DataSourceHandler.load_from_sharepoint(url)

                if len(sheet_names) > 1:
                    sheet_options = [{'label': sheet, 'value': sheet} for sheet in sheet_names]
                    alert = html.Div([
                        html.P(f"✅ {t('sharepoint.loaded')}"),
                        html.P(t('sharepoint.sheets_found', count=len(sheet_names)))
                    ])
                    return dash.no_update, sheet_names, url, {'display': 'block'}, sheet_options, alert, 'info', True, {'display': 'none'}
                else:
                    log_usage('data_load', source_type='sharepoint', rows=df.shape[0], columns=df.shape[1])
                    alert = html.Div([
                        html.P(f"✅ {t('sharepoint.data_loaded')}"),
                        html.P(t('messages.dimensions', rows=df.shape[0], cols=df.shape[1])),
                        html.P(t('messages.columns', columns=' | '.join(df.columns)))
                    ])
                    return df.to_dict('records'), sheet_names, url, {'display': 'none'}, [], alert, 'success', True, {'display': 'none'}

            elif trigger_id == 'sharepoint-sheet-load-btn' and sheet_clicks and selected_sheet and stored_url:
                df = DataSourceHandler.load_sharepoint_sheet(stored_url, selected_sheet)
                log_usage('data_load', source_type='sharepoint', rows=df.shape[0], columns=df.shape[1])
                alert = html.Div([
                    html.P(f"✅ {t('sharepoint.sheet_loaded', sheet=selected_sheet)}"),
                    html.P(t('messages.dimensions', rows=df.shape[0], cols=df.shape[1])),
                    html.P(t('messages.columns', columns=' | '.join(df.columns)))
                ])
                return df.to_dict('records'), dash.no_update, dash.no_update, {'display': 'none'}, [], alert, 'success', True, {'display': 'none'}

        except Exception as e:
            alert = html.Div([html.P(f"❌ {t('sharepoint.error_loading')}"), html.P(str(e))])
            return dash.no_update, dash.no_update, dash.no_update, {'display': 'none'}, [], alert, 'danger', True, {'display': 'none'}

        return dash.no_update, dash.no_update, dash.no_update, {'display': 'none'}, [], "", 'info', False, {'display': 'none'}

    @app.callback(
        [Output('stored-data', 'data', allow_duplicate=True),
         Output('upload-alert', 'children', allow_duplicate=True),
         Output('upload-alert', 'color', allow_duplicate=True),
         Output('upload-alert', 'is_open', allow_duplicate=True),
         Output('loading-container', 'style', allow_duplicate=True)],
        Input('google-sheets-load-btn', 'n_clicks'),
        State('google-sheets-url-input', 'value'),
        prevent_initial_call=True
    )
    def handle_google_sheets_data(n_clicks, url):
        if not n_clicks or not url:
            return dash.no_update, "", 'info', False, {'display': 'none'}

        try:
            if not DataSourceHandler.validate_url(url, 'google_sheets'):
                alert = html.Div([
                    html.P(f"❌ {t('google_sheets.invalid_url')}"),
                    html.P(t('google_sheets.invalid_url_detail'))
                ])
                return dash.no_update, alert, 'warning', True, {'display': 'none'}

            df = DataSourceHandler.load_from_google_sheets(url)
            log_usage('data_load', source_type='google_sheets', rows=df.shape[0], columns=df.shape[1])
            alert = html.Div([
                html.P(f"✅ {t('google_sheets.data_loaded')}"),
                html.P(t('messages.dimensions', rows=df.shape[0], cols=df.shape[1])),
                html.P(t('messages.columns', columns=' | '.join(df.columns)))
            ])
            return df.to_dict('records'), alert, 'success', True, {'display': 'none'}

        except Exception as e:
            alert = html.Div([html.P(f"❌ {t('google_sheets.error_loading')}"), html.P(str(e))])
            return dash.no_update, alert, 'danger', True, {'display': 'none'}

    @app.callback(
        [Output('stored-data', 'data', allow_duplicate=True),
         Output('upload-alert', 'children', allow_duplicate=True),
         Output('upload-alert', 'color', allow_duplicate=True),
         Output('upload-alert', 'is_open', allow_duplicate=True)],
        Input('sqlite-table-load-btn', 'n_clicks'),
        [State('sqlite-table-dropdown', 'value'),
         State('stored-sqlite-path', 'data')],
        prevent_initial_call=True
    )
    def handle_sqlite_table_load(n_clicks, selected_table, sqlite_path):
        if not n_clicks or not selected_table or not sqlite_path:
            return dash.no_update, "", 'info', False

        try:
            df = load_sqlite_table_data(sqlite_path, selected_table)
            file_size_mb = round(os.path.getsize(sqlite_path) / (1024 * 1024), 2) if os.path.exists(sqlite_path) else None
            log_usage('data_load', source_type='upload', file_ext='sqlite', file_size_mb=file_size_mb, rows=df.shape[0], columns=df.shape[1])
            alert = html.Div([
                html.P(f"✅ {t('sqlite.table_loaded', table=selected_table)}"),
                html.P(t('messages.dimensions', rows=df.shape[0], cols=df.shape[1])),
                html.P(t('messages.columns', columns=' | '.join(df.columns)))
            ])
            return df.to_dict('records'), alert, 'success', True

        except Exception as e:
            alert = html.Div([html.P(f"❌ {t('sqlite.error_loading_table')}"), html.P(str(e))])
            return dash.no_update, alert, 'danger', True

    @app.callback(
        [Output('delimiter-selection-container', 'style'),
         Output('delimiter-dropdown', 'value'),
         Output('custom-delimiter-input', 'value'),
         Output('delimiter-preview-alert', 'children'),
         Output('delimiter-preview-alert', 'is_open'),
         Output('sqlite-table-selection-container', 'style'),
         Output('sqlite-info-alert', 'children'),
         Output('sqlite-info-alert', 'is_open'),
         Output('sqlite-table-dropdown', 'options'),
         Output('stored-sqlite-path', 'data'),
         Output('stored-sqlite-tables', 'data'),
         Output('stored-data', 'data', allow_duplicate=True),
         Output('upload-alert', 'children', allow_duplicate=True),
         Output('upload-alert', 'color', allow_duplicate=True),
         Output('upload-alert', 'is_open', allow_duplicate=True)],
        [Input('upload-data', 'contents'),
         Input('delimiter-confirm-btn', 'n_clicks')],
        [State('upload-data', 'filename'),
         State('delimiter-dropdown', 'value'),
         State('custom-delimiter-input', 'value')],
        prevent_initial_call=True
    )
    def handle_upload_or_confirm(contents, n_clicks, filename, delimiter_dropdown, custom_delimiter):
        ctx = callback_context
        if not ctx.triggered:
            return (dash.no_update,) * 15

        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if not contents:
            return ({'display': 'none'}, ',', '', '', False, {'display': 'none'}, '', False, [],
                    dash.no_update, dash.no_update, dash.no_update, "", 'info', False)

        file_ext = filename.split('.')[-1].lower()
        decoded = base64.b64decode(contents.split(',')[1])

        MAX_FILE_SIZE_BYTES = Config.MAX_FILE_SIZE_MB * 1024 * 1024

        if len(decoded) > MAX_FILE_SIZE_BYTES:
            size_mb = len(decoded) / (1024 * 1024)
            alert = html.Div([
                html.P(f"⚠️ {t('messages.file_too_large', size=f'{size_mb:.2f}', max_size=Config.MAX_FILE_SIZE_MB)}")
            ])
            return ({'display': 'none'}, ',', '', '', False, {'display': 'none'}, '', False, [],
                    dash.no_update, dash.no_update, dash.no_update, alert, 'warning', True)

        if trigger_id == 'upload-data':
            if file_ext in ['db', 'sqlite', 'sqlite3']:
                # Handle SQLite files
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp:
                        tmp.write(decoded)
                        tmp.flush()

                        tables, table_info = load_sqlite_tables(tmp.name)

                        if not tables:
                            alert = html.Div([
                                html.P(f"⚠️ {t('sqlite.no_tables')}"),
                                html.P(t('sqlite.no_tables_detail'))
                            ])
                            return ({'display': 'none'}, ',', '', '', False, {'display': 'none'}, '', False, [],
                                    dash.no_update, dash.no_update, dash.no_update, alert, 'warning', True)

                        # Create table dropdown options with row counts
                        table_options = []
                        for table in tables:
                            info = table_info[table]
                            label = f"{table} ({info['rows']:,} rows, {len(info['columns'])} columns)"
                            table_options.append({'label': label, 'value': table})

                        # Create info alert
                        info_alert = html.Div([
                            html.P(f"📊 {t('sqlite.db_loaded', filename=filename)}"),
                            html.Hr(),
                            html.P(t('sqlite.tables_found', count=len(tables))),
                            html.Ul([html.Li(f"{table}: {table_info[table]['rows']:,} rows") for table in tables])
                        ])

                        return ({'display': 'none'}, ',', '', '', False, {'display': 'block'},
                                info_alert, True, table_options, tmp.name, table_info,
                                dash.no_update, "", 'info', False)

                except Exception as e:
                    alert = html.Div([
                        html.P(f"❌ {t('sqlite.error_loading')}"),
                        html.P(str(e))
                    ])
                    return ({'display': 'none'}, ',', '', '', False, {'display': 'none'}, '', False, [],
                            dash.no_update, dash.no_update, dash.no_update, alert, 'danger', True)

            elif file_ext in ['csv', 'txt', 'log']:
                sample = decoded.decode('utf-8')[:1024]
                try:
                    detected = csv.Sniffer().sniff(sample)
                    detected_delim = detected.delimiter
                except:
                    detected_delim = ','

                dropdown_val = detected_delim if detected_delim in [',', ';', '\t', ' ', '|'] else 'custom'
                custom_val = '' if dropdown_val != 'custom' else detected_delim

                msg_define_delimiter = html.Div([
                    html.P(t('messages.file_to_upload', filename=filename)),
                    html.Hr(),
                    html.P(t('messages.suggested_delimiter', delimiter=detected_delim.replace(chr(9), 'Tab (\\t)'))),
                    html.Hr(),
                    html.P(t('messages.confirm_delimiter'))
                ])

                return ({'display': 'block'}, dropdown_val, custom_val, msg_define_delimiter, True,
                        {'display': 'none'}, '', False, [], dash.no_update, dash.no_update,
                        dash.no_update, "", 'info', False)

            else:
                try:
                    df = parse_uploaded_file(contents, filename)
                    file_size_mb = round(len(decoded) / (1024 * 1024), 2)
                    log_usage('data_load', source_type='upload', file_ext=file_ext, file_size_mb=file_size_mb, rows=df.shape[0], columns=df.shape[1])
                    alert = html.Div([
                        html.P(f"✅ {t('messages.file_uploaded', filename=filename)}"),
                        html.Hr(),
                        html.P([
                            t('messages.unnamed_removed'), html.Br(),
                            f"- {t('messages.dimensions', rows=df.shape[0], cols=df.shape[1])}", html.Br(),
                            f"- {t('messages.columns', columns=' | '.join(df.columns))}"
                        ])
                    ])
                    return ({'display': 'none'}, ',', '', '', False, {'display': 'none'}, '', False, [],
                            dash.no_update, dash.no_update, df.to_dict('records'), alert, 'success', True)
                except Exception as e:
                    return ({'display': 'none'}, ',', '', '', False, {'display': 'none'}, '', False, [],
                            dash.no_update, dash.no_update, dash.no_update,
                            html.Div([html.P(str(e))]), 'warning', True)

        elif trigger_id == 'delimiter-confirm-btn':
            delimiter = custom_delimiter if delimiter_dropdown == 'custom' else delimiter_dropdown
            try:
                df = parse_uploaded_file(contents, filename, delimiter)
                file_size_mb = round(len(decoded) / (1024 * 1024), 2)
                log_usage('data_load', source_type='upload', file_ext=file_ext, file_size_mb=file_size_mb, rows=df.shape[0], columns=df.shape[1])
                alert = html.Div([
                    html.P(f"✅ {t('messages.file_uploaded', filename=filename)}"),
                    html.Hr(),
                    html.P([
                        t('messages.delimiter_used', delimiter=delimiter.replace(chr(9), 'Tab (\\t)')), html.Br(),
                        t('messages.unnamed_removed'), html.Br(),
                        f"- {t('messages.dimensions', rows=df.shape[0], cols=df.shape[1])}", html.Br(),
                        f"- {t('messages.columns', columns=' | '.join(df.columns))}"
                    ])
                ])
                return ({'display': 'block'}, delimiter_dropdown, custom_delimiter, '', False,
                        {'display': 'none'}, '', False, [], dash.no_update, dash.no_update,
                        df.to_dict('records'), alert, 'success', True)
            except Exception as e:
                return ({'display': 'block'}, delimiter_dropdown, custom_delimiter, '', False,
                        {'display': 'none'}, '', False, [], dash.no_update, dash.no_update,
                        dash.no_update, html.Div([html.P(str(e))]), 'warning', True)

        return (dash.no_update,) * 15

    @app.callback(
        [Output('stored-data', 'data', allow_duplicate=True),
         Output('upload-alert', 'children', allow_duplicate=True),
         Output('upload-alert', 'color', allow_duplicate=True),
         Output('upload-alert', 'is_open', allow_duplicate=True)],
        Input('airtable-table-load-btn', 'n_clicks'),
        [State('airtable-table-dropdown', 'value'),
         State('stored-airtable-credentials', 'data')],
        prevent_initial_call=True
    )
    def handle_airtable_table_load(n_clicks, selected_table, credentials):
        if not n_clicks or not selected_table or not credentials:
            return dash.no_update, "", 'info', False

        try:
            df = DataSourceHandler.load_from_airtable(
                credentials['api_key'],
                credentials['base_id'],
                selected_table
            )

            log_usage('data_load', source_type='airtable', rows=df.shape[0], columns=df.shape[1])
            alert = html.Div([
                html.P(f"✅ {t('airtable.table_loaded', table=selected_table)}"),
                html.P(t('messages.dimensions', rows=df.shape[0], cols=df.shape[1])),
                html.P(t('messages.columns', columns=' | '.join(df.columns)))
            ])
            return df.to_dict('records'), alert, 'success', True

        except Exception as e:
            alert = html.Div([
                html.P(f"❌ {t('airtable.error_loading_table')}"),
                html.P(str(e))
            ])
            return dash.no_update, alert, 'danger', True
