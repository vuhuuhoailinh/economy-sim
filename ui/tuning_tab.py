import streamlit as st
import pandas as pd
from config import DEFAULT_KEY_STAGES, DEFAULT_STREAK_STAGES

def render_tuning_tab():
    st.header("Economy Tuning (LiveOps & Events)")
    
    with st.form("tuning_form"):
        st.subheader("1. Key Collection")
        st.markdown("Cơ chế: Người chơi thu thập Key khi vượt màn (1 Win = 5 Keys). Đạt mốc Key nào nhận thưởng mốc đó. Cuối chu kỳ sẽ reset số Key về 0. **Lưu ý: Chỉ diễn ra từ Thứ 2 đến hết Thứ 5.**")
        c1, c2 = st.columns([1, 4])
        with c1:
            st.info("Schedule:\nMon - Thu")
            new_key_cadence = 7
        with c2:
            new_key_stages = st.data_editor(st.session_state.tuning['key_stages'], num_rows="fixed", use_container_width=True, hide_index=True)

        st.subheader("2. Win Streak")
        st.markdown("Cơ chế: Thắng liên tiếp (không được thua) để nhận thưởng. Thua sẽ bị reset chuỗi về 0. **Lưu ý: Chỉ diễn ra từ Thứ 6 đến hết Chủ Nhật.**")
        c3, c4 = st.columns([1, 4])
        with c3:
            st.info("Schedule:\nFri - Sun")
            new_streak_cadence = 7 # Dummy fallback
        with c4:
            new_streak_stages = st.data_editor(st.session_state.tuning['streak_stages'], num_rows="fixed", use_container_width=True, hide_index=True)

        st.markdown("---")
        st.subheader("3. Store Prices (Giá Booster & Revive)")
        new_prices = st.data_editor(st.session_state.tuning.get('prices', pd.DataFrame()), num_rows="fixed", use_container_width=True, hide_index=True)

        st.markdown("---")
        col_btn1, col_btn2, _ = st.columns([1, 1, 4])
        with col_btn1:
            submitted = st.form_submit_button("Save Config", type="primary")
        with col_btn2:
            reset = st.form_submit_button("Reset to Default")
            
        if submitted:
            st.session_state.tuning['key_stages'] = new_key_stages
            st.session_state.tuning['streak_stages'] = new_streak_stages
            st.session_state.tuning['key_cadence'] = new_key_cadence
            st.session_state.tuning['prices'] = new_prices
            st.rerun()
            
        if reset:
            st.session_state.tuning = {
                 'key_stages': pd.DataFrame(DEFAULT_KEY_STAGES),
                 'streak_stages': pd.DataFrame(DEFAULT_STREAK_STAGES),
                 'key_cadence': 7,
                 'streak_cadence': 7
            }
            st.rerun()
