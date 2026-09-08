import streamlit as st
import pandas as pd
from config import DEFAULT_KEY_STAGES, DEFAULT_STREAK_STAGES

def render_tuning_tab():
    st.header("Economy Tuning (LiveOps & Events)")
    
    st.subheader("1. Key Collection")
    st.markdown("Cơ chế: Người chơi thu thập Key khi vượt màn (1 Win = 5 Keys). Đạt mốc Key nào nhận thưởng mốc đó. Cuối chu kỳ sẽ reset số Key về 0. **Lưu ý: Chỉ diễn ra từ Thứ 2 đến hết Thứ 5.**")
    c1, c2 = st.columns([1, 4])
    with c1:
        st.info("Schedule:\nMon - Thu")
    with c2:
        st.dataframe(st.session_state.tuning['key_stages'], use_container_width=True, hide_index=True)

    st.subheader("2. Win Streak")
    st.markdown("Cơ chế: Thắng liên tiếp (không được thua) để nhận thưởng. Thua sẽ bị reset chuỗi về 0. **Lưu ý: Chỉ diễn ra từ Thứ 6 đến hết Chủ Nhật.**")
    c3, c4 = st.columns([1, 4])
    with c3:
        st.info("Schedule:\nFri - Sun")
    with c4:
        st.dataframe(st.session_state.tuning['streak_stages'], use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("3. Master Pass")
    st.markdown("Cơ chế: Người chơi thu thập Token khi vượt màn (N: 1, H: 2, SH: 3). Master Pass kéo dài 30 ngày và tự động reset.")
    c5, c6 = st.columns([1, 4])
    with c5:
        st.info("Schedule:\n30 Days Cycle")
    with c6:
        st.dataframe(st.session_state.tuning.get('master_pass_stages', pd.DataFrame()), use_container_width=True, hide_index=True)
    
    st.markdown("---")
    st.subheader("4. Store Prices (Giá Booster & Revive)")
    st.dataframe(st.session_state.tuning.get('prices', pd.DataFrame()), use_container_width=True, hide_index=True)
