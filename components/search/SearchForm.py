```python
import streamlit as st
from typing import Dict, Any, List, Optional
from ..help.HelpSystem import HelpSystem

class SearchForm:
    def __init__(self):
        self.help_system = HelpSystem()

    def render_search_form(self) -> Optional[Dict[str, Any]]:
        """Render the search form and return search parameters."""
        st.subheader("Profile Search")
        self.help_system.show_contextual_help('profile_search')

        with st.form("search_form"):
            # Basic Search Fields
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Name")
                company = st.text_input("Company")
                location = st.text_input("Location")
            
            with col2:
                title = st.text_input("Job Title")
                industry = st.text_input("Industry")
                email_domain = st.text_input("Email Domain")

            # Advanced Filters
            with st.expander("Advanced Filters"):
                experience_min = st.number_input("Minimum Years of Experience", min_value=0)
                skills = st.multiselect(
                    "Required Skills",
                    options=self._get_skill_options()
                )
                data_sources = st.multiselect(
                    "Data Sources",
                    options=["LinkedIn", "Hunter.io", "RocketReach", "People Data Labs"]
                )

            submitted = st.form_submit_button("Search")
            
            if submitted:
                return {
                    'name': name,
                    'company': company,
                    'location': location,
                    'title': title,
                    'industry': industry,
                    'email_domain': email_domain,
                    'experience_min': experience_min,
                    'skills': skills,
                    'data_sources': data_sources
                }
        
        return None

    def _get_skill_options(self) -> List[str]:
        """Get list of available skills."""
        return [
            "Python", "JavaScript", "Java", "C++", "SQL",
            "Data Analysis", "Machine Learning", "Project Management",
            "Sales", "Marketing", "Business Development",
            "Leadership", "Communication", "Problem Solving"
        ]
```