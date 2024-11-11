```python
import streamlit as st
from typing import Dict, Any, List
from .DataChart import DataChart
from ..progress.ProgressTracker import ProgressTracker
from ..notification.NotificationManager import NotificationManager

class DashboardLayout:
    def __init__(self):
        self.progress_tracker = ProgressTracker()
        self.notification_manager = NotificationManager()
        self.data_chart = DataChart()

    def render_dashboard(self, data: Dict[str, Any]):
        """Render main dashboard layout."""
        # Header
        st.title("Gray Ghost Data Profile Generator")
        
        # Notifications
        self.notification_manager.render_notifications()
        
        # Progress Overview
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Profiles Processed", data.get('processed_count', 0))
        with col2:
            st.metric("Success Rate", f"{data.get('success_rate', 0)}%")
        with col3:
            st.metric("Active Tasks", len(data.get('active_tasks', [])))

        # Main Content
        tab1, tab2 = st.tabs(["Data Visualization", "Task Progress"])
        
        with tab1:
            self._render_visualization_tab(data)
        
        with tab2:
            self._render_progress_tab()

    def _render_visualization_tab(self, data: Dict[str, Any]):
        """Render data visualization tab."""
        col1, col2 = st.columns(2)
        
        with col1:
            if 'profile_data' in data:
                st.plotly_chart(
                    self.data_chart.create_profile_completion_chart(data['profile_data']),
                    use_container_width=True
                )
        
        with col2:
            if 'enrichment_data' in data:
                st.plotly_chart(
                    self.data_chart.create_enrichment_sources_chart(data['enrichment_data']),
                    use_container_width=True
                )
        
        if 'validation_data' in data:
            st.plotly_chart(
                self.data_chart.create_validation_metrics_chart(data['validation_data']),
                use_container_width=True
            )

    def _render_progress_tab(self):
        """Render task progress tab."""
        st.subheader("Task Progress")
        self.progress_tracker.render_progress()
        
        overall_progress = self.progress_tracker.get_overall_progress()
        st.metric("Overall Progress", f"{overall_progress:.1f}%")
```