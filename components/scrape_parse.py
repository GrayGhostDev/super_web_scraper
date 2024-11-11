import streamlit as st
from scraper.advanced_scraper import AdvancedScraper
from parse import parse_with_ollama
import json
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def render_scrape_parse_tab():
    col1, col2 = st.columns([2, 1])
    
    with col1:
        url = st.text_input("Enter the URL", "")
        parse_description = st.text_area("Describe what you want to parse", "")
        
        # Advanced settings in sidebar
        with st.sidebar:
            show_advanced = st.checkbox("Show Advanced Settings")
            if show_advanced:
                st.subheader("Scraping Options")
                method = st.selectbox("Scraping Method", ["selenium", "requests"])
                save_results = st.checkbox("Save Results to File", value=True)
                
                st.subheader("LLM Options")
                model_name = st.text_input("LLM Model", "llama2:3.2")
                temperature = st.slider("Temperature", 0.0, 1.0, 0.7)
                max_tokens = st.slider("Max Tokens", 100, 1000, 500)
            else:
                method = "selenium"
                save_results = True
                model_name = "llama2:3.2"
                temperature = 0.7
                max_tokens = 500
        
        if st.button("Scrape and Parse"):
            if not url:
                st.error("Please enter a URL to scrape")
                return
                
            if not parse_description:
                st.error("Please enter a description of what to parse")
                return
                
            with st.spinner("Scraping and parsing..."):
                try:
                    # Initialize scraper
                    scraper = AdvancedScraper()
                    
                    # Scrape website
                    scraped_data = scraper.scrape(
                        url,
                        method=method,
                        save_file=f"scraped_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json" if save_results else None
                    )
                    
                    if not scraped_data:
                        st.error("Failed to scrape the website. Please check the URL and try again.")
                        return
                    
                    # Prepare content for parsing
                    content_for_parsing = []
                    for item in scraped_data['content']:
                        content_for_parsing.append(item['text'])
                    
                    if not content_for_parsing:
                        st.warning("No content found to parse. The page might be empty or blocked.")
                        return
                    
                    # Parse content
                    parsed_results = parse_with_ollama(
                        content_for_parsing,
                        parse_description,
                        model_name=model_name,
                        temperature=temperature,
                        max_tokens=max_tokens
                    )
                    
                    if not parsed_results:
                        st.warning("No matching content found for your parsing description.")
                        return
                    
                    # Store results in session state
                    st.session_state["parsed_results"] = parsed_results
                    st.session_state["scraped_data"] = scraped_data
                    st.success("Scraping and parsing completed!")
                    
                except Exception as e:
                    logger.error(f"Error during scraping/parsing: {str(e)}")
                    st.error(f"An error occurred: {str(e)}")
    
    with col2:
        if "parsed_results" in st.session_state:
            st.subheader("Parsed Results")
            st.text_area("Results", st.session_state["parsed_results"], height=200)
            
            if "scraped_data" in st.session_state:
                st.subheader("Additional Information")
                
                with st.expander("Metadata"):
                    st.json(st.session_state["scraped_data"]["metadata"])
                
                with st.expander("Links Found"):
                    st.json(st.session_state["scraped_data"]["links"])
                
                with st.expander("Structured Data"):
                    st.json(st.session_state["scraped_data"]["structured_data"])
            
            if st.download_button(
                "Download All Data",
                json.dumps({
                    "parsed_results": st.session_state["parsed_results"],
                    "scraped_data": st.session_state.get("scraped_data", {})
                }, indent=2),
                "scraped_results.json",
                "application/json"
            ):
                st.success("Data downloaded!")