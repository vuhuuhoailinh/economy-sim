import streamlit as st
import pandas as pd
from config import get_default_tuning, DEFAULT_CONFIG
from ui.deterministic_tab import render_deterministic_tab
from ui.card_album_tab import render_card_album_tab
from ui.tuning_tab import render_tuning_tab
from card_album.state import ensure_album_state

# ==============================================================================
# MAIN APP CONFIGURATION
# ==============================================================================
st.set_page_config(page_title="Game Economy & Card Album Simulator", layout="wide")
st.title("Game Economy & Card Album Simulator")

# Initialize global card album state
ensure_album_state(st.session_state)

# Initialize global economy state
if 'config' not in st.session_state:
    st.session_state.config = None
if (
    'tuning' not in st.session_state 
    or 'PremiumReward' not in st.session_state.tuning.get('master_pass_stages', pd.DataFrame()).columns 
    or 'card_set_rewards' not in st.session_state.tuning
    or 'Pack' not in ' '.join(st.session_state.tuning.get('key_stages', pd.DataFrame())['Reward'].tolist())
):
    st.session_state.tuning = get_default_tuning()

if 'default_config' not in st.session_state:
    st.session_state.default_config = DEFAULT_CONFIG.copy()

if 'v3_defaults_60d' not in st.session_state:
    st.session_state['v3_defaults_60d'] = True
    st.session_state.default_config = DEFAULT_CONFIG.copy()
    for k, v in DEFAULT_CONFIG.items():
        st.session_state[f"ui_{k}"] = v

for k, v in st.session_state.default_config.items():
    if f"ui_{k}" not in st.session_state:
        st.session_state[f"ui_{k}"] = v

if st.session_state.get('ui_booster_use_rate') == 0.50:
    st.session_state['ui_booster_use_rate'] = 0.0

# Create Main Tabs
tabs = st.tabs(["Simulation", "Card Album", "Economy Tuning"])

with tabs[0]:
    render_deterministic_tab()

with tabs[1]:
    render_card_album_tab()

with tabs[2]:
    render_tuning_tab()
