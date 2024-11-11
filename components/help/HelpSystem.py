```python
import streamlit as st
from typing import Dict, Any, List

class HelpSystem:
    def __init__(self):
        self.help_content = {
            'profile_search': {
                'title': 'Searching for Profiles',
                'content': """
                ### How to Search for Profiles
                1. Enter search criteria in the search fields
                2. Select any additional filters
                3. Click the 'Search' button
                
                **Tips:**
                - Use quotation marks for exact matches
                - Combine multiple filters for better results
                """
            },
            'data_enrichment': {
                'title': 'Data Enrichment',
                'content': """
                ### Understanding Data Enrichment
                Data enrichment adds additional information from various sources:
                - LinkedIn profiles
                - Company information
                - Contact details
                - Professional history
                
                **Note:** Enrichment quality depends on available source data
                """
            },
            'export_data': {
                'title': 'Exporting Data',
                'content': """
                ### How to Export Data
                1. Select the profiles to export
                2. Choose the export format
                3. Click 'Export Selected'
                
                **Available Formats:**
                - CSV
                - JSON
                - Excel
                """
            }
        }

    def render_help_sidebar(self):
        """Render help content in the sidebar."""
        with st.sidebar:
            st.markdown("### Help & Documentation")
            for topic in self.help_content.keys():
                if st.button(self.help_content[topic]['title']):
                    st.session_state.selected_help_topic = topic

    def render_help_content(self):
        """Render selected help content."""
        if hasattr(st.session_state, 'selected_help_topic'):
            topic = self.help_content[st.session_state.selected_help_topic]
            st.markdown(topic['content'])

    def show_contextual_help(self, context: str):
        """Show contextual help for specific features."""
        if context in self.help_content:
            with st.expander("ℹ️ Help"):
                st.markdown(self.help_content[context]['content'])
```