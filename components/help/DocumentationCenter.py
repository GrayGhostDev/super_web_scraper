```python
import streamlit as st
from typing import Dict, Any, List
import markdown2
import yaml

class DocumentationCenter:
    def __init__(self):
        self.sections = self._load_documentation()
        self.current_section = None

    def render_documentation(self):
        """Render the documentation center."""
        st.title("Documentation")

        # Documentation navigation
        col1, col2 = st.columns([1, 3])

        with col1:
            self._render_navigation()

        with col2:
            self._render_content()

    def _render_navigation(self):
        """Render documentation navigation."""
        st.subheader("Contents")

        # Section selection
        for section in self.sections:
            if st.button(
                section['title'],
                key=f"doc_section_{section['id']}"
            ):
                self.current_section = section

        # Quick search
        st.text_input("Search documentation", key="doc_search")

    def _render_content(self):
        """Render documentation content."""
        if not self.current_section:
            self._render_welcome()
            return

        section = self.current_section
        st.header(section['title'])

        # Render content with markdown support
        st.markdown(section['content'])

        # Render subsections
        if 'subsections' in section:
            for subsection in section['subsections']:
                with st.expander(subsection['title']):
                    st.markdown(subsection['content'])

        # Related topics
        if 'related' in section:
            st.subheader("Related Topics")
            for topic in section['related']:
                st.markdown(f"- [{topic['title']}](#{topic['id']})")

    def _render_welcome(self):
        """Render welcome page."""
        st.header("Welcome to Gray Ghost Documentation")
        st.markdown("""
        Welcome to the Gray Ghost documentation center. Here you'll find:
        
        - Getting Started Guide
        - Feature Documentation
        - API Reference
        - Best Practices
        - Troubleshooting Guide
        
        Select a topic from the navigation menu to get started.
        """)

    def _load_documentation(self) -> List[Dict[str, Any]]:
        """Load documentation content."""
        return [
            {
                'id': 'getting-started',
                'title': 'Getting Started',
                'content': """
                ## Getting Started with Gray Ghost

                Gray Ghost is a powerful data profile generator that helps you collect,
                enrich, and analyze professional profile data.

                ### Quick Start

                1. **Search for Profiles**
                   - Enter search criteria
                   - Select data sources
                   - Run search

                2. **Enrich Profiles**
                   - Select profiles to enrich
                   - Choose enrichment sources
                   - Start enrichment process

                3. **Export Data**
                   - Select export format
                   - Choose fields to export
                   - Download results
                """,
                'subsections': [
                    {
                        'title': 'Installation',
                        'content': '...'
                    },
                    {
                        'title': 'Configuration',
                        'content': '...'
                    }
                ]
            },
            {
                'id': 'features',
                'title': 'Features',
                'content': """
                ## Gray Ghost Features

                ### Data Collection
                - Multi-source data collection
                - Parallel processing
                - Real-time updates

                ### Data Enrichment
                - Multiple enrichment sources
                - Automatic validation
                - Quality scoring

                ### Export Options
                - Multiple formats (CSV, JSON, Excel)
                - Custom field selection
                - Batch export
                """
            },
            {
                'id': 'api-reference',
                'title': 'API Reference',
                'content': '...'
            },
            {
                'id': 'troubleshooting',
                'title': 'Troubleshooting',
                'content': '...'
            }
        ]

    def search_documentation(self, query: str) -> List[Dict[str, Any]]:
        """Search documentation content."""
        results = []
        for section in self.sections:
            if self._search_section(section, query.lower()):
                results.append(section)
        return results

    def _search_section(self, section: Dict[str, Any], query: str) -> bool:
        """Search within a section."""
        if query in section['title'].lower() or query in section['content'].lower():
            return True
        
        if 'subsections' in section:
            for subsection in section['subsections']:
                if query in subsection['title'].lower() or \
                   query in subsection['content'].lower():
                    return True
        
        return False
```