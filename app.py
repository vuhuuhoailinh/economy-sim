import streamlit as st
from config import get_default_tuning
from ui.macro_tab import render_macro_tab
from ui.micro_tab import render_micro_tab
from ui.tuning_tab import render_tuning_tab

# ==============================================================================
# MAIN APP CONFIGURATION
# ==============================================================================
st.set_page_config(page_title="Economy Simulator", layout="wide")
st.title("Economy Simulator")

# Initialize global state
if 'config' not in st.session_state:
    st.session_state.config = None
if 'tuning' not in st.session_state:
    st.session_state.tuning = get_default_tuning()

# Create Tabs
tabs = st.tabs(["Simulation", "Monte Carlo", "Economy Tuning"])

with tabs[0]:
    render_macro_tab()

with tabs[1]:
    render_micro_tab()
    
with tabs[2]:
    render_tuning_tab()
