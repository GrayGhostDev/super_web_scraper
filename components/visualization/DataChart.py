```python
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any, List
import pandas as pd

class DataChart:
    @staticmethod
    def create_profile_completion_chart(profile_data: Dict[str, Any]) -> go.Figure:
        """Create profile completion donut chart."""
        required_fields = ['name', 'email', 'company', 'title', 'location']
        completed = sum(1 for field in required_fields if profile_data.get(field))
        completion_rate = (completed / len(required_fields)) * 100

        fig = go.Figure(data=[go.Pie(
            values=[completion_rate, 100 - completion_rate],
            hole=.7,
            labels=['Completed', 'Incomplete'],
            marker_colors=['#00CC96', '#EF553B']
        )])

        fig.update_layout(
            title_text="Profile Completion",
            showlegend=False,
            annotations=[dict(text=f"{completion_rate:.0f}%", x=0.5, y=0.5, font_size=20, showarrow=False)]
        )
        return fig

    @staticmethod
    def create_enrichment_sources_chart(enrichment_data: Dict[str, Any]) -> go.Figure:
        """Create enrichment sources bar chart."""
        sources = enrichment_data.get('sources', [])
        source_counts = pd.Series(sources).value_counts()

        fig = px.bar(
            x=source_counts.index,
            y=source_counts.values,
            title="Data Enrichment Sources",
            labels={'x': 'Source', 'y': 'Count'}
        )
        return fig

    @staticmethod
    def create_validation_metrics_chart(validation_data: Dict[str, Any]) -> go.Figure:
        """Create validation metrics radar chart."""
        metrics = validation_data.get('metrics', {})
        
        fig = go.Figure(data=go.Scatterpolar(
            r=[metrics.get(m, 0) for m in ['accuracy', 'completeness', 'consistency', 'timeliness']],
            theta=['Accuracy', 'Completeness', 'Consistency', 'Timeliness'],
            fill='toself'
        ))

        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=False,
            title="Data Quality Metrics"
        )
        return fig
```