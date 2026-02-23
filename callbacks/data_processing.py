import dash
from dash import Input, Output, State, callback_context
import pandas as pd

from i18n import t
from utils.data_processing import handle_datetime_conversion
from utils.mongodb import log_usage


def register_callbacks(app):

    @app.callback(
        Output('datetime-input-container', 'style'),
        Input('datetime-toggle', 'value')
    )
    def toggle_datetime_inputs(enabled):
        return {'display': 'block'} if enabled else {'display': 'none'}

    @app.callback(
        Output('custom-datetime-container', 'style'),
        Input('datetime-format', 'value')
    )
    def toggle_custom_format_input(selected_format):
        return {'display': 'block'} if selected_format == 'custom' else {'display': 'none'}

    @app.callback(
        [Output('data-grid', 'columnDefs'),
         Output('data-grid', 'rowData'),
         Output('error-alert', 'children'),
         Output('error-alert', 'is_open')],
        [Input('confirm-button', 'n_clicks'),
         Input('stored-data', 'data')],
        [State('datetime-toggle', 'value'),
         State('datetime-column', 'value'),
         State('datetime-format', 'value'),
         State('custom-datetime-format', 'value')]
    )
    def update_dataframe(n_clicks, data, datetime_enabled, datetime_col, datetime_format, custom_format):
        if not data:
            return dash.no_update, dash.no_update, "", False

        ctx = callback_context
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None

        # Auto-load: when new data arrives and datetime is disabled → load directly
        if trigger_id == 'stored-data':
            if datetime_enabled:
                return dash.no_update, dash.no_update, "", False
            df = pd.DataFrame(data)
        # Manual load: confirm button clicked → process with or without datetime
        elif trigger_id == 'confirm-button':
            if not n_clicks:
                return dash.no_update, dash.no_update, "", False
            df = pd.DataFrame(data)
            try:
                if datetime_enabled:
                    if datetime_format == 'custom':
                        datetime_format = custom_format
                    df = handle_datetime_conversion(df, datetime_col, datetime_format)
                    log_usage('datetime_processing', format_used=datetime_format)
            except Exception as e:
                return [], [], f"❌ {t('messages.error')}: {str(e)}", True
        else:
            return dash.no_update, dash.no_update, "", False

        columnDefs = [
            {
                'headerName': col,
                'field': col,
                'pinned': 'left' if col == 'ts' else None,
                'minWidth': 230 if col == 'ts' else None
            }
            for col in df.columns
        ]

        return columnDefs, df.to_dict('records'), "", False

    @app.callback(
        [Output('datetime-column', 'options')] +
        [Output(f'chart-{i}-color-column', 'options') for i in range(1, 4)] +
        [Output(f'chart-{i}-x-axis-column', 'options') for i in range(1, 4)] +
        [Output(f'chart-{i}-y-axis-columns', 'options') for i in range(1, 4)] +
        [Output(f'chart-{i}-z-axis-columns', 'options') for i in range(1, 4)],
        Input('stored-data', 'data')
    )
    def update_dropdown_options(data):
        if data:
            df = pd.DataFrame(data)
            base_options = [{'label': col, 'value': col} for col in df.columns]
            enhanced_options = base_options + [
                {'label': 'count', 'value': 'count'},
                {'label': 'ts', 'value': 'ts'},
                {'label': 'tsDate', 'value': 'tsDate'},
                {'label': 'tsHour', 'value': 'tsHour'},
                {'label': 'tsDateHour', 'value': 'tsDateHour'},
                {'label': 'tsWeekday', 'value': 'tsWeekday'},
                {'label': 'tsCalendarWeek', 'value': 'tsCalendarWeek'},
                {'label': 'tsMonth', 'value': 'tsMonth'},
                {'label': 'tsQuarter', 'value': 'tsQuarter'},
                {'label': 'tsYear', 'value': 'tsYear'},
                {'label': 'tsYearCalendarWeek', 'value': 'tsYearCalendarWeek'},
                {'label': 'tsYearMonth', 'value': 'tsYearMonth'},
                {'label': 'tsYearQuarter', 'value': 'tsYearQuarter'}
            ]
            return [base_options] + [enhanced_options] * 12

        empty = []
        return [empty] * 13
