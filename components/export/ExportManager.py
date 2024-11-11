```python
import streamlit as st
import pandas as pd
import json
from typing import Dict, Any, List
from datetime import datetime
import io

class ExportManager:
    def render_export_panel(self, data: List[Dict[str, Any]]):
        """Render the export panel."""
        st.subheader("Export Data")

        # Export format selection
        format_option = st.selectbox(
            "Export Format",
            options=["CSV", "JSON", "Excel"]
        )

        # Export options
        with st.expander("Export Options"):
            self._render_export_options()

        # Export button
        if st.button("Export Selected Data"):
            self._export_data(data, format_option)

    def _render_export_options(self):
        """Render export configuration options."""
        st.checkbox("Include metadata", value=True)
        st.checkbox("Include enrichment data", value=True)
        st.checkbox("Include verification status", value=True)
        
        st.multiselect(
            "Select fields to export",
            options=[
                "Name", "Email", "Phone", "Company",
                "Title", "Location", "Industry",
                "Skills", "Experience", "Education"
            ],
            default=["Name", "Email", "Company", "Title"]
        )

    def _export_data(self, data: List[Dict[str, Any]], format_option: str):
        """Export data in the selected format."""
        try:
            # Convert data to DataFrame
            df = pd.DataFrame(data)
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"profile_data_{timestamp}"

            # Export based on selected format
            if format_option == "CSV":
                self._export_csv(df, filename)
            elif format_option == "JSON":
                self._export_json(data, filename)
            else:  # Excel
                self._export_excel(df, filename)

            st.success("Data exported successfully!")
            
        except Exception as e:
            st.error(f"Export failed: {str(e)}")

    def _export_csv(self, df: pd.DataFrame, filename: str):
        """Export data as CSV."""
        csv = df.to_csv(index=False)
        self._create_download_button(
            csv,
            f"{filename}.csv",
            "text/csv"
        )

    def _export_json(self, data: List[Dict[str, Any]], filename: str):
        """Export data as JSON."""
        json_str = json.dumps(data, indent=2)
        self._create_download_button(
            json_str,
            f"{filename}.json",
            "application/json"
        )

    def _export_excel(self, df: pd.DataFrame, filename: str):
        """Export data as Excel."""
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Profiles', index=False)
        
        excel_data = output.getvalue()
        self._create_download_button(
            excel_data,
            f"{filename}.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    def _create_download_button(self, data: Any, filename: str, mime: str):
        """Create a download button for the exported data."""
        st.download_button(
            label="Download Export",
            data=data,
            file_name=filename,
            mime=mime
        )
```