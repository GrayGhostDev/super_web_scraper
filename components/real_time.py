import streamlit as st
import time
from datetime import datetime
import threading
from queue import Queue
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataRetriever:
    def __init__(self):
        self.data_queue = Queue()
        self.is_running = False
        self._thread = None

    def start(self, niche, params):
        if self.is_running:
            return
        
        self.is_running = True
        self._thread = threading.Thread(
            target=self._retrieve_data,
            args=(niche, params),
            daemon=True
        )
        self._thread.start()

    def stop(self):
        self.is_running = False
        if self._thread:
            self._thread.join(timeout=1.0)
            self._thread = None

    def _retrieve_data(self, niche, params):
        while self.is_running:
            try:
                data = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "niche": niche,
                    "params": params,
                    "status": "active"
                }
                self.data_queue.put(data)
                time.sleep(2)
            except Exception as e:
                logger.error(f"Error in data retrieval: {str(e)}")
                time.sleep(5)  # Wait longer on error

def render_real_time_tab():
    if "data_retriever" not in st.session_state:
        st.session_state["data_retriever"] = DataRetriever()
    
    st.subheader("Real-Time Data Retrieval")
    
    niche = st.text_input("Enter Niche / Department")
    params = []
    for i in range(3):
        param = st.text_input(f"Search Parameter {i+1}")
        params.append(param)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Start Data Retrieval"):
            if not niche:
                st.error("Please enter a niche/department")
                return
                
            if not any(params):
                st.error("Please enter at least one search parameter")
                return
                
            st.session_state["data_retriever"].start(niche, params)
            st.success("Data retrieval started!")
            
    with col2:
        if st.button("Stop Data Retrieval"):
            st.session_state["data_retriever"].stop()
            st.info("Data retrieval stopped.")
    
    # Display real-time data
    if st.session_state["data_retriever"].is_running:
        st.subheader("Live Data Feed")
        data_container = st.empty()
        
        try:
            while not st.session_state["data_retriever"].data_queue.empty():
                data = st.session_state["data_retriever"].data_queue.get_nowait()
                data_container.json(data)
        except Exception as e:
            logger.error(f"Error displaying data: {str(e)}")
            st.error("Error displaying data feed")