import streamlit as st
from components.scrape_parse import render_scrape_parse_tab
from components.real_time import render_real_time_tab
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(page_title="Gray Ghost Data Profile Generator", layout="wide")
st.title("Gray Ghost Data Profile Generator")

# Initialize session state variables
if "parsed_results" not in st.session_state:
    st.session_state["parsed_results"] = ""
if "data_retrieval_started" not in st.session_state:
    st.session_state["data_retrieval_started"] = False
if "real_time_data" not in st.session_state:
    st.session_state["real_time_data"] = {}

# Sidebar
tab = st.sidebar.radio("Select Option", ["Scrape and Parse", "Real-Time Data Retrieval"])

if tab == "Scrape and Parse":
    render_scrape_parse_tab()
else:
    render_real_time_tab()