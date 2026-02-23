import plotly.express as px
import plotly.graph_objects as go


class ChartFactory:
    @staticmethod
    def create_chart(chart_type, df, config):
        """Centralized chart creation logic"""
        if not df.empty and config.get('x_col') and config.get('y_cols'):
            if chart_type == 'scatter':
                return ChartFactory._create_scatter(df, config)
            elif chart_type == 'scatter-multi':
                return ChartFactory._create_scatter_multi(df, config)
            elif chart_type == 'line':
                return ChartFactory._create_line(df, config)
            elif chart_type == 'bar-group':
                return ChartFactory._create_bar_group(df, config)
            elif chart_type == 'bar-stacked':
                return ChartFactory._create_bar_stacked(df, config)
            elif chart_type == 'histogram-group':
                return ChartFactory._create_histogram_group(df, config)
            elif chart_type == 'histogram-stacked':
                return ChartFactory._create_histogram_stacked(df, config)
            elif chart_type == 'pie':
                return ChartFactory._create_pie(df, config)
            elif chart_type == 'bubble':
                return ChartFactory._create_bubble(df, config)
            elif chart_type == 'heatmap':
                return ChartFactory._create_heatmap(df, config)
            elif chart_type == 'log':
                return ChartFactory._create_log(df, config)
            elif chart_type == 'sunburst':
                return ChartFactory._create_sunburst(df, config)
            elif chart_type == 'icicle':
                return ChartFactory._create_icicle(df, config)

        return go.Figure().update_layout(title=config.get('title', 'No Data'))

    @staticmethod
    def _create_scatter(df, config):
        fig = px.scatter(df, x=config['x_col'], y=config['y_cols'][0], color=config.get('color_col'))
        return ChartFactory._apply_layout(fig, config)

    @staticmethod
    def _create_scatter_multi(df, config):
        fig = go.Figure()
        for y_col in config['y_cols']:
            fig.add_trace(go.Scatter(x=df[config['x_col']], y=df[y_col], mode='markers', name=y_col))
        fig.update_layout(hovermode='x')
        return ChartFactory._apply_layout(fig, config)

    @staticmethod
    def _create_line(df, config):
        fig = px.line(df, x=config['x_col'], y=config['y_cols'], color=config.get('color_col'))
        fig.update_layout(hovermode='x unified')
        return ChartFactory._apply_layout(fig, config)

    @staticmethod
    def _create_bar_group(df, config):
        fig = px.bar(df, x=config['x_col'], y=config['y_cols'], color=config.get('color_col'), barmode='group')
        return ChartFactory._apply_layout(fig, config)

    @staticmethod
    def _create_bar_stacked(df, config):
        fig = px.bar(df, x=config['x_col'], y=config['y_cols'], color=config.get('color_col'), barmode='stack')
        return ChartFactory._apply_layout(fig, config)

    @staticmethod
    def _create_histogram_group(df, config):
        fig = px.histogram(df, x=config['x_col'], color=config.get('color_col'), barmode='group')
        return ChartFactory._apply_layout(fig, config)

    @staticmethod
    def _create_histogram_stacked(df, config):
        fig = px.histogram(df, x=config['x_col'], color=config.get('color_col'), barmode='stack')
        return ChartFactory._apply_layout(fig, config)

    @staticmethod
    def _create_pie(df, config):
        fig = px.pie(df, names=config['x_col'], values=config['y_cols'][0])
        return ChartFactory._apply_layout(fig, config)

    @staticmethod
    def _create_bubble(df, config):
        size_data = df[config['z_col']] if config.get('z_col') else [20] * len(df)
        if hasattr(size_data, 'max') and size_data.max() != size_data.min():
            size_scaled = (size_data - size_data.min()) / (size_data.max() - size_data.min())
            size_scaled *= 100
        else:
            size_scaled = size_data

        fig = px.scatter(df, x=config['x_col'], y=config['y_cols'][0], size=size_scaled,
                        color=config.get('color_col'), size_max=60)
        return ChartFactory._apply_layout(fig, config)

    @staticmethod
    def _create_heatmap(df, config):
        fig = px.density_heatmap(df, x=config['x_col'], y=config['y_cols'][0], z=config.get('z_col'),
                               nbinsx=31, nbinsy=24, color_continuous_scale='Viridis')
        return ChartFactory._apply_layout(fig, config)

    @staticmethod
    def _create_log(df, config):
        fig = px.line(df, x=config['x_col'], y=config['y_cols'][0], log_y=True, color=config.get('color_col'))
        return ChartFactory._apply_layout(fig, config)

    @staticmethod
    def _create_sunburst(df, config):
        fig = px.sunburst(df, path=config['y_cols'], values=config['x_col'], color=config.get('color_col'))
        return ChartFactory._apply_layout(fig, config)

    @staticmethod
    def _create_icicle(df, config):
        fig = px.icicle(df, path=config['y_cols'], values=config['x_col'], color=config.get('color_col'))
        return ChartFactory._apply_layout(fig, config)

    @staticmethod
    def _apply_layout(fig, config):
        fig.update_layout(
            title=config.get('title', 'Chart'),
            xaxis_title=config.get('x_title', 'X-axis'),
            yaxis_title=config.get('y_title', 'Y-axis')
        )
        return fig
