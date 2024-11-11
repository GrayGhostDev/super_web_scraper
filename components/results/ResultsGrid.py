```python
import streamlit as st
import pandas as pd
from typing import Dict, Any, List
from ..visualization.DataChart import DataChart

class ResultsGrid:
    def __init__(self):
        self.data_chart = DataChart()

    def render_results(self, results: List[Dict[str, Any]]):
        """Render search results in a grid layout."""
        if not results:
            st.info("No results found. Try adjusting your search criteria.")
            return

        # Convert results to DataFrame for easier handling
        df = pd.DataFrame(results)

        # Display summary metrics
        self._render_summary_metrics(df)

        # Display results grid
        self._render_grid(df)

        # Display visualization
        self._render_visualization(df)

    def _render_summary_metrics(self, df: pd.DataFrame):
        """Render summary metrics for the results."""
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Results", len(df))
        
        with col2:
            verified_count = len(df[df['email_verified'] == True])
            st.metric("Verified Profiles", verified_count)
        
        with col3:
            avg_completeness = df['profile_completeness'].mean()
            st.metric("Avg. Completeness", f"{avg_completeness:.1f}%")
        
        with col4:
            companies_count = df['company'].nunique()
            st.metric("Unique Companies", companies_count)

    def _render_grid(self, df: pd.DataFrame):
        """Render the main results grid."""
        # Add selection checkboxes
        df['selected'] = False
        selected_indices = []

        for idx, row in df.iterrows():
            with st.container():
                col1, col2, col3 = st.columns([1, 3, 1])
                
                with col1:
                    if st.checkbox("", key=f"select_{idx}"):
                        selected_indices.append(idx)
                
                with col2:
                    self._render_profile_card(row)
                
                with col3:
                    self._render_action_buttons(row)

        # Store selected indices in session state
        st.session_state.selected_profiles = selected_indices

    def _render_profile_card(self, profile: pd.Series):
        """Render a single profile card."""
        st.markdown(f"""
            <div style="padding: 10px; border: 1px solid #ddd; border-radius: 5px;">
                <h3>{profile['name']}</h3>
                <p>{profile['title']} at {profile['company']}</p>
                <p>📍 {profile['location']}</p>
                <p>✉️ {profile['email'] if profile['email_verified'] else 'Email not verified'}</p>
            </div>
        """, unsafe_allow_html=True)

    def _render_action_buttons(self, profile: pd.Series):
        """Render action buttons for a profile."""
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("View Details", key=f"view_{profile.name}"):
                st.session_state.selected_profile = profile.name
        
        with col2:
            if st.button("Enrich", key=f"enrich_{profile.name}"):
                st.session_state.enrich_profile = profile.name

    def _render_visualization(self, df: pd.DataFrame):
        """Render result visualizations."""
        with st.expander("Results Analysis"):
            tab1, tab2 = st.tabs(["Distribution", "Metrics"])
            
            with tab1:
                # Company distribution
                fig = self.data_chart.create_company_distribution_chart(df)
                st.plotly_chart(fig, use_container_width=True)
            
            with tab2:
                # Profile completeness
                fig = self.data_chart.create_completeness_distribution_chart(df)
                st.plotly_chart(fig, use_container_width=True)
```