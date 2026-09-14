import streamlit as st
import pandas as pd
from config import DEFAULT_KEY_STAGES, DEFAULT_STREAK_STAGES
from card_album.config_ui import render_config_tab as render_card_album_config

def render_tuning_tab():
    subtabs = st.tabs([
        "LiveOps Economy Tables (View-Only)", 
        "Card Set Rewards (View-Only)", 
        "Card Album Tuning (Gacha & Chests)"
    ])
    
    with subtabs[0]:
        st.header("Economy Tuning (LiveOps & Events)")
        
        st.subheader("1. :orange[Key Collection]")
        st.markdown("Cơ chế: Người chơi thu thập Key khi vượt màn (1 Win = 5 Keys). Đạt mốc Key nào nhận thưởng mốc đó. Cuối chu kỳ sẽ reset số Key về 0. **Lưu ý: Chỉ diễn ra từ Thứ 2 đến hết Thứ 5.**")
        c1, c2 = st.columns([1, 4])
        with c1:
            st.info(":orange[**Schedule:**]\n:orange[Mon - Thu]")
        with c2:
            st.dataframe(st.session_state.tuning['key_stages'], use_container_width=True, hide_index=True)

        st.subheader("2. :red[Win Streak]")
        st.markdown("Cơ chế: Thắng liên tiếp (không được thua) để nhận thưởng. Thua sẽ bị reset chuỗi về 0. **Lưu ý: Chỉ diễn ra từ Thứ 6 đến hết Chủ Nhật.**")
        c3, c4 = st.columns([1, 4])
        with c3:
            st.info(":red[**Schedule:**]\n:red[Fri - Sun]")
        with c4:
            st.dataframe(st.session_state.tuning['streak_stages'], use_container_width=True, hide_index=True)

        st.markdown("---")
        st.subheader("3. :violet[Master Pass]")
        st.markdown("Cơ chế: Người chơi thu thập Token khi vượt màn (N: 1, H: 2, SH: 3). Master Pass kéo dài 30 ngày và tự động reset.")
        c5, c6 = st.columns([1, 4])
        with c5:
            st.info(":violet[**Schedule:**]\n:violet[30 Days Cycle]")
        with c6:
            st.dataframe(st.session_state.tuning.get('master_pass_stages', pd.DataFrame()), use_container_width=True, hide_index=True)
        
        st.markdown("---")
        st.subheader("4. Store Prices (Booster & Revive)")
        st.dataframe(st.session_state.tuning.get('prices', pd.DataFrame()), use_container_width=True, hide_index=True)

    with subtabs[1]:
        st.header("Card Set SS1 & Grand Prize Rewards")
        st.markdown(
            "Bảng cấu hình danh sách 15 Set Thẻ SS1 cùng cấu trúc độ hiếm của từng Set, "
            "phần thưởng khi hoàn thành từng Set (Album Thường & Grand Album), "
            "và giải thưởng lớn Grand Prize khi hoàn thành toàn bộ 135 Thẻ."
        )
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Sets", "15 Sets")
        m2.metric("Total Cards", "135 Cards")
        m3.metric("Grand Prize (Album)", "5,000 Coins + 5x Set")
        m4.metric("Grand Prize (Grand)", "10,000 Coins + 10x Set")
        
        st.markdown("---")
        df_set_rewards = st.session_state.tuning.get('card_set_rewards', pd.DataFrame())
        
        col_cfg = {
            "Set": st.column_config.TextColumn("Set", help="Set index (1-15 or Total)"),
            "Name": st.column_config.TextColumn("Set Name / Theme"),
            "Common": st.column_config.NumberColumn("1-Star Common", help="Number of 1-Star cards in Set"),
            "Uncommon": st.column_config.NumberColumn("2-Star Uncommon", help="Number of 2-Star cards in Set"),
            "Rare": st.column_config.NumberColumn("3-Star Rare", help="Number of 3-Star cards in Set"),
            "Epic": st.column_config.NumberColumn("4-Star Epic", help="Number of 4-Star cards in Set"),
            "Legendary": st.column_config.NumberColumn("5-Star Legendary", help="Number of 5-Star cards in Set"),
            "Secret": st.column_config.NumberColumn("6-Star Secret Gold", help="Number of Gold (6-Star) cards in Set"),
            "AlbumReward": st.column_config.TextColumn("Album Reward", help="Reward for completing Set first time (Round 0)"),
            "GrandAlbumReward": st.column_config.TextColumn("Grand Album Reward", help="Reward for completing Set in Grand Album (Round 1)")
        }
        
        st.dataframe(
            df_set_rewards,
            column_config=col_cfg,
            use_container_width=True,
            hide_index=True
        )
        
        st.info(
            "Quy tắc trả thưởng Album:\n"
            "- Khi một Set hoàn thành đủ 9 thẻ, phần thưởng tương ứng (Coins hoặc Boosters) sẽ tự động cộng vào tài khoản và inventory.\n"
            "- Khi hoàn tất cả 15 Sets (135/135 thẻ), người chơi nhận thêm Grand Prize (5,000 Coins + 5x Booster Set) và mở khóa Grand Album.\n"
            "- Ở vòng Grand Album, phần thưởng Coins của các Set được nhân đôi (ví dụ: Set 1 là 200 Coins, Set 13 là 1,000 Coins). "
            "Khi hoàn thành toàn bộ Grand Album, nhận Grand Prize cực đại (10,000 Coins + 10x Booster Set)."
        )

    with subtabs[2]:
        render_card_album_config()

