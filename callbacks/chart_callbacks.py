import io
import zipfile

import dash
from dash import dcc, Input, Output, State
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio

from i18n import t
from utils.chart_factory import ChartFactory
from utils.mongodb import log_usage


def register_callbacks(app):

    def create_chart_callback(chart_number):
        @app.callback(
            Output(f'chart-{chart_number}', 'figure'),
            [Input('data-grid', 'virtualRowData'),
             Input(f'chart-{chart_number}-type', 'value'),
             Input(f'chart-{chart_number}-color-column', 'value'),
             Input(f'chart-{chart_number}-x-axis-column', 'value'),
             Input(f'chart-{chart_number}-y-axis-columns', 'value'),
             Input(f'chart-{chart_number}-z-axis-columns', 'value'),
             Input(f'chart-{chart_number}-chart-title', 'value'),
             Input(f'chart-{chart_number}-x-axis-title', 'value'),
             Input(f'chart-{chart_number}-y-axis-title', 'value')]
        )
        def update_chart(data, chart_type, color_col, x_col, y_cols, z_col, title, x_title, y_title):
            if not data or not x_col or not y_cols:
                return go.Figure().update_layout(title=t('chart.no_data', num=chart_number))

            df = pd.DataFrame(data)
            config = {
                'x_col': x_col,
                'y_cols': y_cols,
                'color_col': color_col,
                'z_col': z_col,
                'title': title or t('chart.chart_title_default', num=chart_number),
                'x_title': x_title or 'x-axis',
                'y_title': y_title or 'y-axis'
            }

            log_usage('chart_render', chart_number=chart_number, chart_type=chart_type)
            return ChartFactory.create_chart(chart_type, df, config)

        return update_chart

    def create_visibility_callback(chart_number):
        @app.callback(
            [Output(f'chart-{chart_number}-color-column-container', 'style'),
             Output(f'chart-{chart_number}-z-axes-column-container', 'style'),
             Output(f'chart-{chart_number}-x-axis-title-container', 'style'),
             Output(f'chart-{chart_number}-y-axis-title-container', 'style')],
            Input(f'chart-{chart_number}-type', 'value')
        )
        def update_input_visibility(chart_type):
            COLOR_CHARTS = [
                'scatter', 'line', 'bar-group', 'bar-stacked',
                'histogram-group', 'histogram-stacked', 'bubble', 'log', 'icicle', 'sunburst'
            ]
            Z_AXIS_CHARTS = ['heatmap', 'bubble']
            NO_AXIS_TITLES = ['pie', 'sunburst', 'icicle']

            show_color = chart_type in COLOR_CHARTS
            show_z = chart_type in Z_AXIS_CHARTS
            show_axis_titles = chart_type not in NO_AXIS_TITLES

            return (
                {'display': 'block'} if show_color else {'display': 'none'},
                {'display': 'block'} if show_z else {'display': 'none'},
                {'display': 'block'} if show_axis_titles else {'display': 'none'},
                {'display': 'block'} if show_axis_titles else {'display': 'none'}
            )

        return update_input_visibility

    def create_download_callback(chart_number):
        @app.callback(
            Output(f'chart-{chart_number}-file-download', 'data'),
            Input(f'chart-{chart_number}-download-button', 'n_clicks'),
            State(f'chart-{chart_number}', 'figure')
        )
        def download_chart(n_clicks, figure):
            if n_clicks and figure:
                log_usage('chart_export', chart_number=chart_number)
                fig_html = pio.to_html(figure, full_html=True)
                return dcc.send_bytes(fig_html.encode(), f"chart-{chart_number}-export.html")
            return None

        return download_chart

    # Register callbacks for all 3 charts
    for i in range(1, 4):
        create_chart_callback(i)
        create_visibility_callback(i)
        create_download_callback(i)

    # Combined Dashboard Export (zip of individual chart HTML files)
    # Two identical buttons (top + bottom), both trigger the same export
    @app.callback(
        [Output('dashboard-file-download', 'data'),
         Output('dashboard-file-download-bottom', 'data')],
        [Input('dashboard-download-button', 'n_clicks'),
         Input('dashboard-download-button-bottom', 'n_clicks')],
        [State('chart-1', 'figure'),
         State('chart-2', 'figure'),
         State('chart-3', 'figure')],
        prevent_initial_call=True,
    )
    def download_dashboard(n_clicks_top, n_clicks_bottom, fig1, fig2, fig3):
        if not any([fig1, fig2, fig3]):
            return None, None

        figures = [fig1, fig2, fig3]
        active_charts = sum(1 for f in figures if f and f.get('data'))
        log_usage('dashboard_export', active_charts=active_charts)

        buf = io.BytesIO()
        with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
            for i, fig in enumerate(figures, 1):
                if fig and fig.get('data'):
                    fig_obj = go.Figure(fig)
                    html = pio.to_html(fig_obj, full_html=True)
                    zf.writestr(f"chart-{i}.html", html)

        buf.seek(0)
        zip_data = dcc.send_bytes(buf.getvalue(), "charts-export.zip")

        # Send to whichever Download component the clicked button is paired with
        ctx = dash.callback_context
        trigger = ctx.triggered[0]["prop_id"].split(".")[0]
        if trigger == 'dashboard-download-button':
            return zip_data, None
        return None, zip_data
