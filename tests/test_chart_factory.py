import pandas as pd
import plotly.graph_objects as go
import pytest

from utils.chart_factory import ChartFactory

DF = pd.DataFrame({
    'x': [1, 2, 3, 4],
    'y1': [10.0, 20.0, 15.0, 30.0],
    'y2': [5.0, 8.0, 2.0, 9.0],
    'cat': ['a', 'a', 'b', 'b'],
    'size': [1.0, 2.0, 3.0, 4.0],
})

XY_TYPES = [
    'scatter', 'scatter-multi', 'line', 'bar-group', 'bar-stacked',
    'histogram-group', 'histogram-stacked', 'pie', 'bubble', 'heatmap', 'log',
]


@pytest.mark.parametrize('chart_type', XY_TYPES)
def test_xy_chart_types_return_figures(chart_type):
    config = {'x_col': 'x', 'y_cols': ['y1', 'y2'], 'color_col': 'cat',
              'z_col': 'size', 'title': 'T', 'x_title': 'X', 'y_title': 'Y'}
    fig = ChartFactory.create_chart(chart_type, DF, config)
    assert isinstance(fig, go.Figure)
    assert fig.layout.title.text == 'T'
    assert len(fig.data) > 0


@pytest.mark.parametrize('chart_type', ['sunburst', 'icicle'])
def test_hierarchical_chart_types(chart_type):
    # For these types x_col holds the values column and y_cols the path
    config = {'x_col': 'size', 'y_cols': ['cat'], 'title': 'H'}
    fig = ChartFactory.create_chart(chart_type, DF, config)
    assert isinstance(fig, go.Figure)
    assert len(fig.data) > 0


def test_empty_dataframe_returns_no_data_figure():
    fig = ChartFactory.create_chart('scatter', pd.DataFrame(), {'x_col': 'x', 'y_cols': ['y']})
    assert isinstance(fig, go.Figure)
    assert fig.layout.title.text == 'No Data'


def test_missing_config_returns_no_data_figure():
    fig = ChartFactory.create_chart('scatter', DF, {'title': 'custom'})
    assert fig.layout.title.text == 'custom'
    assert len(fig.data) == 0


def test_unknown_chart_type_returns_no_data_figure():
    fig = ChartFactory.create_chart('doesnotexist', DF, {'x_col': 'x', 'y_cols': ['y1']})
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 0


def test_bubble_constant_size_column():
    df = DF.assign(size=1.0)  # max == min triggers the constant-size branch
    config = {'x_col': 'x', 'y_cols': ['y1'], 'z_col': 'size'}
    fig = ChartFactory.create_chart('bubble', df, config)
    assert isinstance(fig, go.Figure)
