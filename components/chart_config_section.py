from dash import dcc, html
import dash_bootstrap_components as dbc

from config import Config
from i18n import t


def create_chart_config_section(chart_num):
    """Create configuration section for a specific chart"""
    return html.Div([
        html.H5(t('chart.config_heading', num=chart_num), style={'marginBottom': '15px'}),
        dbc.Row([
            dbc.Label(t('chart.select_type'), style={'fontWeight': 'bold'}),
            dbc.RadioItems(
                id=f'chart-{chart_num}-type',
                options=[
                    {'label': 'Scatter', 'value': 'scatter'},
                    {'label': 'Scatter (multi y)', 'value': 'scatter-multi'},
                    {'label': 'Line', 'value': 'line'},
                    {'label': 'Bar (grouped)', 'value': 'bar-group'},
                    {'label': 'Bar (stacked)', 'value': 'bar-stacked'},
                    {'label': 'Histogram (grouped)', 'value': 'histogram-group'},
                    {'label': 'Histogram (stacked)', 'value': 'histogram-stacked'},
                    {'label': 'Pie Chart', 'value': 'pie'},
                    {'label': 'Bubble Chart', 'value': 'bubble'},
                    {'label': 'Heatmap', 'value': 'heatmap'},
                    {'label': 'Log Chart', 'value': 'log'},
                    {'label': 'Sunburst Chart', 'value': 'sunburst'},
                    {'label': 'Icicle Chart', 'value': 'icicle'},
                ],
                value=Config.DEFAULT_CHART_TYPE,
                inline=True,
            ),
        ], style={"marginBottom": "20px"}),

        dbc.Row([
            dbc.Label(t('chart.define_axes'), style={'fontWeight': 'bold'}),
            dbc.Col([
                dbc.Label([
                    t('chart.x_axis'),
                    html.I(className="fas fa-circle-info", id=f'chart-{chart_num}-x-axis-label',
                          style={'color': '#0098A3', 'marginLeft': '6px', 'cursor': 'pointer', 'fontSize': '1.1rem'}),
                ], html_for=f'chart-{chart_num}-x-axis-column'),
                dcc.Dropdown(id=f'chart-{chart_num}-x-axis-column', multi=False,
                           placeholder=t('chart.x_axis_placeholder'), value='ts'),
                dbc.Tooltip(
                    t('chart.x_axis_tooltip'),
                    target=f'chart-{chart_num}-x-axis-label', placement='top', style={'whiteSpace': 'pre-line'}
                )
            ]),
            dbc.Col([
                dbc.Label([
                    t('chart.y_axis'),
                    html.I(className="fas fa-circle-info", id=f'chart-{chart_num}-y-axis-label',
                          style={'color': '#0098A3', 'marginLeft': '6px', 'cursor': 'pointer', 'fontSize': '1.1rem'}),
                ], html_for=f'chart-{chart_num}-y-axis-column'),
                dcc.Dropdown(id=f'chart-{chart_num}-y-axis-columns', multi=True, placeholder=t('chart.y_axis_placeholder')),
                dbc.Tooltip(
                    t('chart.y_axis_tooltip'),
                    target=f'chart-{chart_num}-y-axis-label', placement='top', style={'whiteSpace': 'pre-line'}
                )
            ]),
            dbc.Col([
                dbc.Label([
                    t('chart.color'),
                    html.I(className="fas fa-circle-info", id=f'chart-{chart_num}-color-label',
                          style={'color': '#0098A3', 'marginLeft': '6px', 'cursor': 'pointer', 'fontSize': '1.1rem'}),
                ], html_for=f'chart-{chart_num}-color-column'),
                dcc.Dropdown(id=f'chart-{chart_num}-color-column', multi=False, placeholder=t('chart.color_placeholder')),
                dbc.Tooltip(
                    t('chart.color_tooltip'),
                    target=f'chart-{chart_num}-color-label', placement='top', style={'whiteSpace': 'pre-line'}
                )
            ], id=f'chart-{chart_num}-color-column-container'),
            dbc.Col([
                dbc.Label(t('chart.z_axis'), html_for=f'chart-{chart_num}-z-axis-columns', id=f'chart-{chart_num}-z-axis-label'),
                dcc.Dropdown(id=f'chart-{chart_num}-z-axis-columns', multi=False, placeholder=t('chart.z_axis_placeholder')),
                dbc.Tooltip(
                    t('chart.z_axis_tooltip'),
                    target=f'chart-{chart_num}-z-axis-label', placement='top', style={'whiteSpace': 'pre-line'}
                )
            ], id=f'chart-{chart_num}-z-axes-column-container')
        ], style={'marginBottom': '10px'}),

        dbc.Row([
            dbc.Label(t('chart.set_titles'), style={'fontWeight': 'bold'}),
            dbc.Col([
                dbc.Label(t('chart.chart_title_label')),
                dcc.Input(id=f'chart-{chart_num}-chart-title', type='text', placeholder=t('chart.chart_title_placeholder'),
                         value=t('chart.chart_title_default', num=chart_num), debounce=True, style={'padding': '7px', 'width': '100%'})
            ]),
            dbc.Col([
                dbc.Label(t('chart.x_axis_title_label')),
                dcc.Input(id=f'chart-{chart_num}-x-axis-title', type='text', placeholder=t('chart.x_axis_title_placeholder'),
                         value='x-axis', debounce=True, style={'padding': '7px', 'width': '100%'})
            ], id=f'chart-{chart_num}-x-axis-title-container'),
            dbc.Col([
                dbc.Label(t('chart.y_axis_title_label')),
                dcc.Input(id=f'chart-{chart_num}-y-axis-title', type='text', placeholder=t('chart.y_axis_title_placeholder'),
                         value='y-axis', debounce=True, style={'padding': '7px', 'width': '100%'})
            ], id=f'chart-{chart_num}-y-axis-title-container'),
        ], style={'marginBottom': '10px'}),

        dbc.Row([
            dbc.Col([
                dbc.Button([html.I(className="fas fa-download me-2"), t('chart.download_btn', num=chart_num)],
                          id=f'chart-{chart_num}-download-button', color='primary', style={"float": "right"}),
                dcc.Download(id=f"chart-{chart_num}-file-download"),
            ], style={"marginTop": "20px"},)
        ]),
    ], style={'marginBottom': '30px'})
