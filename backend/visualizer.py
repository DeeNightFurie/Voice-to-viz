"""Purpose: Creates interactive Plotly charts from cleaned data. Generates HTML files served to frontend. Supports all major chart types via voice commands.

Supported Voice Viz Commands:

"show bar chart [x_column] [y_column]"

"show line chart [x_column] [y_column]"

"show pie chart [x_column] [y_column]"

etc."""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import json
import os
from typing import Dict, Any
from pathlib import Path
from models import VizType 

class Visualizer:
    def __init__(self):
        self.viz_path = "visualizations/"
        os.makedirs(self.viz_path, exist_ok=True)
    
    def create_chart(self, data_file: str, viz_request: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Plotly chart based on voice command"""
        try:
            # Load processed data
            with open(data_file, 'r') as f:
                data_info = json.load(f)
            
            df = pd.DataFrame(data_info['data'])
            
            # Create chart based on viz_type
            fig = self._generate_figure(df, viz_request)
            
            # Save HTML chart
            chart_file = f"{self.viz_path}{Path(data_file).stem}_chart.html"
            fig.write_html(chart_file)
            
            return {
                'success': True,
                'chart_url': f"/visualizations/{Path(chart_file).name}",
                'chart_data': self._fig_to_json(fig)
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _generate_figure(self, df: pd.DataFrame, request: Dict[str, Any]) -> go.Figure:
        """Generate specific chart type"""
        viz_type = request.get('viz_type', 'bar')
        x_col = request['x_column']
        y_col = request.get('y_column')
        title = request.get('title', 'Data Visualization')
        
        if viz_type == 'bar':
            fig = px.bar(df, x=x_col, y=y_col, title=title)
        elif viz_type == 'line':
            fig = px.line(df, x=x_col, y=y_col, title=title)
        elif viz_type == 'pie':
            fig = px.pie(df, names=x_col, values=y_col, title=title)
        elif viz_type == 'scatter':
            fig = px.scatter(df, x=x_col, y=y_col, title=title)
        elif viz_type == 'histogram':
            fig = px.histogram(df, x=x_col, title=title)
        else:
            fig = px.bar(df, x=x_col, y=y_col, title=title)
        
        fig.update_layout(
            height=500,
            showlegend=True,
            font=dict(size=12)
        )
        
        return fig
    
    def _fig_to_json(self, fig: go.Figure) -> str:
        """Convert figure to JSON for frontend"""
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    def list_charts(self) -> list:
        """List available visualizations"""
        charts = []
        for file in Path(self.viz_path).glob("*.html"):
            charts.append(file.name)
        return charts

# Global visualizer instance
viz_engine = Visualizer()
