```python
import streamlit as st
from typing import Dict, Any
from ..progress.ProgressTracker import ProgressTracker
from ..notification.NotificationManager import NotificationManager

class EnrichmentPanel:
    def __init__(self):
        self.progress_tracker = ProgressTracker()
        self.notification_manager = NotificationManager()

    def render_enrichment_panel(self, profile_data: Dict[str, Any]):
        """Render the enrichment panel for a profile."""
        st.subheader("Data Enrichment")

        # Display current enrichment status
        self._render_enrichment_status(profile_data)

        # Data source selection
        selected_sources = self._render_source_selection()

        # Enrichment options
        with st.expander("Enrichment Options"):
            self._render_enrichment_options()

        # Enrichment button
        if st.button("Start Enrichment"):
            self._start_enrichment(profile_data, selected_sources)

    def _render_enrichment_status(self, profile_data: Dict[str, Any]):
        """Render current enrichment status."""
        enrichment_data = profile_data.get('enrichment', {})
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                "Enrichment Score",
                f"{enrichment_data.get('score', 0)}%"
            )
        
        with col2:
            st.metric(
                "Last Updated",
                enrichment_data.get('last_updated', 'Never')
            )

        # Show enriched fields
        if enriched_fields := enrichment_data.get('fields', []):
            st.write("Enriched Fields:")
            for field in enriched_fields:
                st.write(f"✓ {field}")

    def _render_source_selection(self) -> list:
        """Render data source selection."""
        return st.multiselect(
            "Select Data Sources",
            options=[
                "LinkedIn",
                "Hunter.io",
                "RocketReach",
                "People Data Labs",
                "LexisNexis"
            ],
            default=["LinkedIn", "Hunter.io"]
        )

    def _render_enrichment_options(self):
        """Render enrichment options."""
        st.checkbox("Verify email addresses", value=True)
        st.checkbox("Update existing data", value=False)
        st.checkbox("Include social profiles", value=True)
        st.checkbox("Fetch company data", value=True)
        
        st.select_slider(
            "Confidence threshold",
            options=["Low", "Medium", "High"],
            value="Medium"
        )

    def _start_enrichment(self, profile_data: Dict[str, Any], sources: list):
        """Start the enrichment process."""
        # Add enrichment task to progress tracker
        self.progress_tracker.add_task(
            "enrichment",
            "Enriching profile data",
            len(sources)
        )

        # Show progress
        with st.spinner("Enriching profile data..."):
            for i, source in enumerate(sources, 1):
                # Simulate enrichment process
                st.text(f"Fetching data from {source}...")
                self.progress_tracker.update_task("enrichment", i)

        # Show completion notification
        self.notification_manager.add_notification(
            "Profile enrichment completed successfully!",
            type="success"
        )
```