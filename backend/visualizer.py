"""Purpose: Creates interactive Plotly charts from cleaned data. Generates HTML files served to frontend."""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import json
import os
import uuid
from typing import Dict, Any
from pathlib import Path

class Visualizer:
    def __init__(self):
        self.viz_path = "visualizations/"
        os.makedirs(self.viz_path, exist_ok=True)
    
    def create_chart(self, chart_type: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        try:
            from data_processor import processor
            if processor.data is None or processor.data.empty:
                return {'success': False, 'error': 'No data loaded'}
            
            processor.save_processed()
            
            # ✅ FORCE SAFE DataFrame
            data_info = json.load(open(processor.processed_file))
            df = pd.DataFrame(data_info['data'])
            
            if df.empty:
                return {'success': False, 'error': 'Empty dataframe'}
            
            fig = self._generate_figure(df, chart_type, params)
            
            # ✅ Guaranteed unique filename
            chart_uuid = uuid.uuid4().hex[:8]
            chart_filename = f"{processor.filename}_{chart_type}_{chart_uuid}.html"
            chart_file = os.path.join(self.viz_path, chart_filename)
            
            fig.write_html(chart_file, include_plotlyjs='cdn')
            print(f"✅ CHART CREATED: http://localhost:8000/visualizations/{chart_filename}")
            
            return {
                'success': True,
                'chart_url': f"/visualizations/{chart_filename}",
                'chart_type': chart_type
            }
        except Exception as e:
            print(f"❌ FULL ERROR: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': f'{type(e).__name__}: {str(e)}'}
    
    def _generate_figure(self, df: pd.DataFrame, chart_type: str, params: Dict[str, Any]) -> go.Figure:
        """✅ BULLETPROOF - NO DataFrame truth checks"""
        cols = df.columns.tolist()
        x_idx = 0 if len(cols) > 0 else None
        y_idx = 1 if len(cols) > 1 else None
        x_col = cols[x_idx] if x_idx is not None else cols[0]
        y_col = cols[y_idx] if y_idx is not None else None
        
        title = params.get('title', f"{chart_type.title()} Chart ({len(df)} rows)")
        print(f"📊 {chart_type}: x={x_col}, y={y_col}, shape={df.shape}")
        
        try:
            if chart_type == 'bar':
                if y_col is not None and y_col in cols:
                    fig = px.bar(df, x=x_col, y=y_col, title=title)
                else:
                    fig = px.bar(df, x=x_col, title=title)
            elif chart_type == 'line':
                if y_col is not None and y_col in cols:
                    fig = px.line(df, x=x_col, y=y_col, title=title)
                else:
                    fig = px.line(df, x=x_col, title=title)
            elif chart_type == 'pie':
                if y_col is not None and y_col in cols:
                    fig = px.pie(df, names=x_col, values=y_col, title=title)
                else:
                    fig = px.pie(df, names=x_col, title=title)
            elif chart_type == 'scatter':
                if y_col is not None and y_col in cols:
                    fig = px.scatter(df, x=x_col, y=y_col, title=title)
                else:
                    fig = px.scatter(df, x=x_col, title=title)
            elif chart_type == 'histogram':
                fig = px.histogram(df, x=x_col, title=title)
            else:
                fig = px.bar(df, x=x_col, title="Default Chart")
            
            fig.update_layout(
                height=350, width=400,
                showlegend=True,
                font_size=11,
                margin=dict(l=30, r=30, t=30, b=30)
            )
            return fig
        except Exception as e:
            print(f"❌ Plotly error: {e}")
            # Fallback bar chart
            fig = px.bar(df.head(10), x=cols[0] if cols else "x", y=cols[1] if len(cols)>1 else "y", title="Fallback Chart")
            return fig

viz_engine = Visualizer()
