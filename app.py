import streamlit as st
import pandas as pd
from config import get_default_tuning
from ui.deterministic_tab import render_deterministic_tab
from ui.tuning_tab import render_tuning_tab

# ==============================================================================
# MAIN APP CONFIGURATION
# ==============================================================================
st.set_page_config(page_title="Economy Simulator", layout="wide")
st.title("Economy Simulator")

# Initialize global state
if 'config' not in st.session_state:
    st.session_state.config = None
if 'tuning' not in st.session_state or 'PremiumReward' not in st.session_state.tuning.get('master_pass_stages', pd.DataFrame()).columns:
    st.session_state.tuning = get_default_tuning()
if 'default_config' not in st.session_state or 'enable_keys' not in st.session_state.default_config:
    st.session_state.default_config = {
        'sim_days': 30, 'daily_sessions': 2, 'levels_per_session': 2.0, 
        'min_l': 1, 'max_l': 4,
        'win_rate_n': 1.0, 'win_rate_h': 0.90, 'win_rate_sh': 0.80,
        'rv_watch_rate': 0.25, 'rv_multiplier': 3.0, 
        'booster_use_rate': 0.0, 'revive_buy_rate': 0.10,
        'enable_keys': True, 'enable_streak': True, 'enable_mp': True, 'mp_tier': 'Free'
    }

if st.session_state.get('default_config', {}).get('sim_days') == 60:
    st.session_state.default_config['sim_days'] = 30
if st.session_state.get('ui_sim_days') == 60:
    st.session_state['ui_sim_days'] = 30

for k, v in st.session_state.default_config.items():
    if f"ui_{k}" not in st.session_state:
        st.session_state[f"ui_{k}"] = v

if st.session_state.get('ui_booster_use_rate') == 0.50:
    st.session_state['ui_booster_use_rate'] = 0.0

# Create Tabs
tabs = st.tabs(["Simulation", "Economy Tuning"])

with tabs[0]:
    render_deterministic_tab()

with tabs[1]:
    render_tuning_tab()
