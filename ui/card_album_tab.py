import streamlit as st
from card_album.state import ensure_album_state, sync_album_state
from card_album.ui.inventory import render_inventory_tab
from card_album.ui.gacha import render_pack_opener_tab
from card_album.ui.chest_drop import render_chest_drop_tab

def render_card_album_tab():
    ensure_album_state(st.session_state)
    
    # Check if there is an album result from simulation to sync
    if "last_sim_album" in st.session_state:
        sim_data = st.session_state["last_sim_album"]
        col_sync, _ = st.columns([3.5, 6.5])
        with col_sync:
            st.markdown("""
            <style>
            div.element-container:has(#sync-btn-album) + div.element-container button,
            div[data-testid="stColumn"]:has(#sync-btn-album) button,
            div:has(> #sync-btn-album) + div button {
                background-color: #dc2626 !important;
                background: linear-gradient(135deg, #ef4444, #dc2626) !important;
                color: #ffffff !important;
                border: 1px solid #b91c1c !important;
                font-weight: bold !important;
                box-shadow: 0 2px 5px rgba(220, 38, 38, 0.3) !important;
            }
            div.element-container:has(#sync-btn-album) + div.element-container button:hover,
            div[data-testid="stColumn"]:has(#sync-btn-album) button:hover,
            div:has(> #sync-btn-album) + div button:hover {
                background: linear-gradient(135deg, #dc2626, #b91c1c) !important;
                border-color: #991b1b !important;
                color: #ffffff !important;
                box-shadow: 0 4px 10px rgba(220, 38, 38, 0.5) !important;
            }
            </style>
            <span id="sync-btn-album"></span>
            """, unsafe_allow_html=True)
            if st.button("Đồng bộ thẻ từ Kết quả Mô phỏng", type="primary", use_container_width=True, help="Nạp toàn bộ thẻ, sao, tiến độ 15 set, lịch sử pack mở và chest drop từ lượt mô phỏng gần nhất."):
                tot_p = st.session_state.get("last_sim_res", {}).get("tot_packs_earned")
                sync_album_state(st.session_state, sim_data, tot_p)
                st.success("Đã đồng bộ thành công tiến độ bộ sưu tập, Gacha Sandbox & Chest Drop từ mô phỏng!")
                st.rerun()

    subtabs = st.tabs([
        "Card Inventory", 
        "Gacha Sandbox", 
        "Chest Drop Minigame"
    ])
    
    with subtabs[0]:
        render_inventory_tab()
        
    with subtabs[1]:
        render_pack_opener_tab()
        
    with subtabs[2]:
        render_chest_drop_tab()

