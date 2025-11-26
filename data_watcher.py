import os
import time
import pandas as pd
from datetime import datetime
import streamlit as st

class DataWatcher:
    def __init__(self, excel_path):
        self.excel_path = excel_path
        self.last_modified = None
        self.last_data = None
    
    def get_file_modified_time(self):
        """Get the last modified time of the Excel file"""
        try:
            return os.path.getmtime(self.excel_path)
        except Exception as e:
            st.error(f"Error getting file modification time: {str(e)}")
            return None
    
    def load_data(self):
        """Load data from Excel file"""
        try:
            return pd.read_csv(self.excel_path)
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
            return None
    
    def check_for_updates(self):
        """Check if the Excel file has been updated"""
        current_modified = self.get_file_modified_time()
        
        if current_modified is None:
            return False
        
        if self.last_modified is None:
            self.last_modified = current_modified
            self.last_data = self.load_data()
            return False
        
        if current_modified > self.last_modified:
            self.last_modified = current_modified
            self.last_data = self.load_data()
            return True
        
        return False
    
    def get_latest_data(self):
        """Get the latest data from the Excel file"""
        if self.last_data is None:
            self.last_data = self.load_data()
        return self.last_data

def setup_data_watcher(excel_path):
    """Set up the data watcher in the session state"""
    if 'data_watcher' not in st.session_state:
        st.session_state.data_watcher = DataWatcher(excel_path)
    
    return st.session_state.data_watcher

def check_data_updates():
    """Check for data updates and refresh if needed"""
    if 'data_watcher' in st.session_state:
        watcher = st.session_state.data_watcher
        if watcher.check_for_updates():
            st.success("New data detected! Refreshing dashboard...")
            st.rerun() 