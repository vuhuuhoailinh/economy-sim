import re
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from simulation.deterministic_sim import run_deterministic_simulation
from card_album.state import sync_album_state

def highlight_liveops(text: str) -> str:
    patterns = [
        (r'\b(LiveOps Keys|Keys? Collection)\b', ':orange[**Key Collection**]'),
        (r'\b(LiveOps Streak|Win Streak)\b', ':red[**Win Streak**]'),
        (r'\bMaster Pass\b', ':violet[**Master Pass**]'),
        (r'\bCard Rush\b', ':blue[**Card Rush**]'),
        (r'\bChest Drop\b', ':green[**Chest Drop**]'),
        (r'\b(Auto Star Chest|Star Chest)\b', ':violet[**Star Chest**]'),
        (r'\bGrand Album\b', ':rainbow[**Grand Album**]'),
        (r'\bGrand Prize\b', ':rainbow[**Grand Prize**]'),
        (r'\bCard Album\b', ':blue[**Card Album**]')
    ]
    for pattern, repl in patterns:
        text = re.sub(pattern, repl, text)
    return text


from config import DEFAULT_CONFIG

def reset_defaults():
    st.session_state.default_config = DEFAULT_CONFIG.copy()
    for k, v in DEFAULT_CONFIG.items():
        st.session_state[f"ui_{k}"] = v
    st.session_state.config = None
    st.session_state.pop("last_sim_res", None)
    st.session_state.pop("last_sim_album", None)

    
def render_deterministic_tab():
    st.header("Simulation Settings")
    
    with st.expander("System Assumptions & Economy Overview", expanded=False):
        st.markdown("""
        ### 1. Level Progression & Win Rates
        - **Level Progression**: Diễn ra theo chu kỳ cố định 9 màn: **6 Normal (N) - 2 Hard (H) - 1 Super Hard (SH)** (tỷ lệ 6 : 2 : 1).
        - **Tiền thưởng cơ bản khi thắng màn (Base Coins)**:
          - Normal: **20 Coins**
          - Hard: **40 Coins** (gấp 2 lần Normal)
          - Super Hard: **60 Coins** (gấp 3 lần Normal)
          - *Trung bình một màn thắng nhận được: ~28.89 Coins (trước khi xem quảng cáo).*
        - **Tỷ lệ thắng (Win Rate mặc định)**: Normal **100%**, Hard **90%**, Super Hard **80%** (Trung bình chu kỳ: **95.56%**).
        - **Tần suất chơi (Daily Sessions mặc định)**: **2 sessions/ngày**, mỗi session chơi ngẫu nhiên từ **1 đến 4 màn** (trung bình ~5 màn/ngày).

        ### 2. Coins Economy: Faucets & Sinks
        - **Số dư khởi đầu (Initial Coins)**: Bắt đầu mô phỏng với **400 Coins**.
        - **Nguồn bơm tiền (Inflows / Faucets)**:
          - **Gameplay Base**: Nhận trực tiếp mỗi khi vượt qua màn chơi theo chu kỳ màn chơi.
          - **Rewarded Video (Ads)**: Xem quảng cáo sau khi thắng (Mặc định: **25%** tỷ lệ xem với hệ số **x3** tiền thưởng, tương ứng cộng thêm +200% tiền thưởng gốc của màn đó).
          - **:orange[Key Collection]**: Diễn ra từ **Thứ 2 đến hết Thứ 5** (1 Win = 5 Keys, trần 304 Keys/tuần). Thưởng tiền tại Mốc 12 (80 Coins), Mốc 16 (120 Coins), Mốc 20 (200 Coins), Mốc 25 (1,000 Coins) -> **Tổng 1,400 Coins/chu kỳ tuần**.
          - **:red[Win Streak]**: Diễn ra từ **Thứ 6 đến hết Chủ Nhật** (thua reset chuỗi về 0, trần 36 trận thắng). Thưởng tiền tại Mốc 2 (40 Coins), Mốc 18 (80 Coins), Mốc 36 (300 Coins) -> **Tổng 420 Coins/chu kỳ tuần**.
          - **:violet[Master Pass] (Chu kỳ 30 ngày)**: Thu thập token từ màn chơi (N: 1, H: 2, SH: 3 Tokens, max 329 Tokens).
            - **Nhánh Free (Mặc định bật)**: Mốc 3 (40c), Mốc 6 (60c), Mốc 16 (80c), Mốc 22 (100c), Mốc 30 (200c trong Rương) -> **Tổng 480 Coins/chu kỳ 30 ngày**.
            - **Nhánh Premium (Nếu bật)**: Nhận thêm tại Mốc 0 (500c), Mốc 5 (100c), Mốc 10 (150c), Mốc 15 (200c), Mốc 20 (300c), Mốc 25 (500c), Mốc 30 (750c) -> **Cộng thêm 2,500 Coins**.
            - **Bonus Bank**: Sau khi vượt mốc 30 (329 Tokens), mỗi 10 Tokens tích lũy thêm sẽ cộng **150 Coins** vào ngân hàng thưởng (tối đa **3,000 Coins**), được chi trả vào ngày cuối cùng của chu kỳ 30 ngày.
          - **Card Set Completion & :rainbow[Grand Prize]**:
            - Thưởng Coins khi hoàn thành từng Set: Set 1 (100 Coins), Set 4 (150 Coins), Set 7 (200 Coins), Set 10 (300 Coins), Set 13 (500 Coins). Ở vòng Grand Album phần thưởng Coins của các Set này được nhân đôi (x2).
            - **Grand Prize**: Hoàn tất 15 Sets (135/135 Thẻ) nhận **+5,000 Coins** (Album Thường) hoặc **+10,000 Coins** (Grand Album).
        - **Nguồn xả tiền (Outflows / Sinks)**:
          - **Revive (Hồi sinh)**: Khi thua màn, người chơi có xác suất `Revive Buy Rate` (Mặc định 10%) tiêu tốn **380 Coins** để mua tiếp 5 lượt đi (chỉ mua khi số dư tài khoản >= 380 Coins).
          - *Lưu ý: Game không cho phép dùng Coins mua trực tiếp Booster trong màn chơi.*

        ### 3. Booster Economy: Faucets & Sinks
        - **Nhóm Booster hỗ trợ**: Hammer (Búa), Broom (Chổi), Scissors (Kéo).
        - **Nguồn nhận Booster (Inflows)**:
          - **:orange[Key Collection]**: Thưởng qua các mốc chìa khóa: Mốc 2 (1 Scissors), Mốc 5 (1 Hammer), Mốc 6 (1 Broom), Mốc 9 (1 Scissors), Mốc 14 (1 Broom), Mốc 18 (1 Scissors), Mốc 22 (1 Hammer) -> **Tổng 2 Hammer, 2 Broom, 3 Scissors/chu kỳ tuần**.
          - **:red[Win Streak]**: Thưởng từ mốc chuỗi thắng: Mốc 11 (1 Scissors), Mốc 30 (**2x Hammer**), Mốc 36 (1 Broom) -> **Tổng 2 Hammer, 1 Broom, 1 Scissors/chu kỳ tuần**.
          - **:violet[Master Pass]**: Mốc 0 mở khóa nhận ngay 1x Hammer; nhiều mốc thưởng đơn lẻ và Rương Booster Set (1 Hammer + 1 Broom + 1 Scissors) ở cả 2 nhánh Free và Premium.
          - **Card Set Completion & :rainbow[Grand Prize]**:
            - Hoàn thành Set nhận Booster: Set 2, 5 (2x Scissors); Set 3, 8 (2x Hammer); Set 6, 9 (2x Broom); Set 11 (3x Scissors); Set 12, 14 (3x Hammer); Set 15 (3x Broom).
            - **Grand Prize**: Nhận ngay **5x Booster Set** (5 Hammer, 5 Broom, 5 Scissors) ở Album Thường và **10x Booster Set** (10 Hammer, 10 Broom, 10 Scissors) ở Grand Album.
        - **Tiêu thụ Booster (Sinks)**:
          - `Booster Use Rate`: **Mặc định 0% (0.0)** để giả lập tích lũy kho đồ thuần túy.
          - Khi bật (> 0): Cứ mỗi màn chơi bắt đầu, người chơi sẽ **bốc ngẫu nhiên 1 trong 3 loại booster đang có trong kho** để sử dụng. Nếu kho đồ không còn loại nào, người chơi sẽ không tiêu thụ booster và **tuyệt đối không mua bù bằng Coins**.

        ### 4. Card Album & LiveOps Events
        - **Card Packs Inflows**:
          - **Core Gameplay**: Thắng màn Hard nhận 1x Bronze Pack, thắng Super Hard nhận 1x Emerald Pack (**Mặc định TẮT** để tránh lạm phát thẻ từ cày cuốc thường; có thể bật trong config).
          - **:orange[Key Collection]**: Cung cấp Bronze, Emerald, Silver, Amethyst, Ruby Packs theo các mốc chìa khóa.
          - **:red[Win Streak]**: Cung cấp Bronze, Emerald, Silver, Amethyst, Ruby Packs theo các mốc chuỗi thắng.
          - **:violet[Master Pass]**: Cung cấp Bronze, Emerald, Silver, Amethyst, Ruby, Rainbow Packs.
          - **:violet[Star Chest] (Tự động Đổi Rương Sao)**: **Mặc định BẬT**. Ưu tiên tự động đổi từ **Gold Star Chest (500⭐: 1x Rainbow, 1x Amethyst, 1x Silver)**; vào ngày cuối của Mùa (Day 60), hệ thống sẽ vét đổi tiếp Silver Star Chest (250⭐) và Bronze Star Chest (100⭐) nếu không đủ 500⭐.
          - **:blue[Card Rush Event]**: Kích hoạt vào Thứ 7 (Tuần 1-6) và Thứ 4 + Thứ 7 (Tuần 7+), tự động nâng cấp Bronze -> Bronze+ (3 thẻ, +50%), Emerald -> Emerald+ (5 thẻ, +67%), Silver -> Silver+ (6 thẻ, +50%).
          - **:green[Chest Drop Minigame]**: Thắng 3, 7, 12 level trong ngày nhận rương 1-Sao, 2-Sao, 3-Sao. Mỗi rương được đập đúng 5 lần (đảm bảo 5 thẻ trong cùng 1 rương không trùng lặp), có xác suất thăng cấp lên tối đa 5-Sao.
        - **Card Album Mechanics**:
          - **Chu kỳ Mùa (Season)**: Kéo dài đúng **60 Ngày**. Khi kết thúc 60 ngày sẽ bắt đầu Mùa mới (Season 2, Day 61), **reset toàn bộ thẻ về 0** để mở lại chu kỳ sưu tập mới.
          - Tổng cộng 135 thẻ phân bổ trong 15 Sets thẻ (mỗi set 9 thẻ, từ 1-Sao đến 6-Sao Secret Gold).
          - Tỷ lệ ra thẻ Mới: `New Card Ratio = (Remaining New / Total) ^ (power + y_value) + Pity`.
          - Thẻ trùng lặp được quy đổi tự động thành Sao: 1⭐=1, 2⭐=2, 3⭐=3, 4⭐=5, 5⭐=10, 6⭐=15 Sao.
          - Cơ chế **Set Completion Pity (SS2)**: Tự động hỗ trợ nhét thẻ còn thiếu vào Set gần hoàn thành nhất.
          - Cơ chế **First Pack Luck (SS2)**: Lần đầu tiên mở bất kỳ loại gói thẻ nào trong mùa chắc chắn 100% rớt Thẻ Mới.
          - Cơ chế **:rainbow[Grand Album]**: Hoàn thành đủ 15 Sets (135/135 thẻ) nhận Grand Prize Vòng 1, kho thẻ tự động reset về 0 để mở khóa Grand Album (nhân đôi Coins thưởng của các Set), **giữ nguyên toàn bộ số Sao đã tích lũy**.
        """)
        
    with st.form("macro_form"):
        col_p1, col_p2, col_p3 = st.columns(3)
        with col_p1:
            st.subheader("Player Behavior")
            sim_days = st.slider("Simulation Days", 1, 180, key="ui_sim_days")
            daily_sessions = st.slider("Sessions/Day", 1, 5, key="ui_daily_sessions")
            c_min, c_max = st.columns(2)
            min_l = c_min.number_input("Levels/Session (Min)", 1, 50, key="ui_min_l")
            max_l = c_max.number_input("Levels/Session (Max)", 1, 50, key="ui_max_l")
            
            levels_per_session = (min_l + max_l) / 2.0
            
        with col_p2:
            st.subheader("Win Rates")
            win_rate_n = st.slider("Normal Level", 0.0, 1.0, key="ui_win_rate_n")
            win_rate_h = st.slider("Hard Level", 0.0, 1.0, key="ui_win_rate_h")
            win_rate_sh = st.slider("Super Hard", 0.0, 1.0, key="ui_win_rate_sh")
            
        with col_p3:
            st.subheader("Monetization & Sinks")
            rv_watch_rate = st.slider("RV Watch Rate", 0.0, 1.0, key="ui_rv_watch_rate", help="Tỷ lệ người chơi xem video quảng cáo (Rewarded Video) để nhân số tiền thưởng sau khi vượt qua màn chơi.")
            rv_multiplier = st.slider("RV Multiplier", 2.0, 5.0, key="ui_rv_multiplier", help="Hệ số nhân số tiền thưởng nhận được khi người chơi xem video quảng cáo (ví dụ: x3, x4, x5).")
            
            booster_use_rate = st.slider("Booster Use Rate", 0.0, 1.0, key="ui_booster_use_rate", help="Tỷ lệ người chơi sử dụng Booster đang có sẵn trong một màn chơi (bất kể thắng/thua).")
            revive_buy_rate = st.slider("Revive Buy Rate", 0.0, 1.0, key="ui_revive_buy_rate", help="Tỷ lệ người chơi dùng Coins mua Revive khi thua (thay vì xem Ads hoặc bỏ cuộc).")
            
        st.markdown("<br>", unsafe_allow_html=True)
        with st.container(border=True):
            st.subheader("LiveOps & Card Album Controls")
            col_ctrl1, col_ctrl2 = st.columns(2)
            with col_ctrl1:
                enable_keys = st.toggle(
                    ":orange[**Key Collection**]", 
                    key="ui_enable_keys",
                    help="Sự kiện Key Collection (Thứ 2 - Thứ 5): Người chơi thu thập Key mỗi khi vượt màn (1 Win = 5 Keys). Tích lũy Key để mở 25 mốc thưởng Coins, Boosters, Hearts và Gói thẻ (Keys tự động reset về 0 sau mỗi tuần)."
                )
                enable_streak = st.toggle(
                    ":red[**Win Streak**]", 
                    key="ui_enable_streak",
                    help="Sự kiện Win Streak (Thứ 6 - Chủ Nhật): Thắng liên tiếp (không được thua) để nhận 9 mốc thưởng Coins, Boosters, Hearts và Gói thẻ cao cấp (Amethyst, Ruby). Thua màn sẽ bị reset chuỗi thắng về 0."
                )
                enable_mp = st.toggle(
                    ":violet[**Master Pass**]", 
                    key="ui_enable_mp",
                    help="Sự kiện Master Pass (Chu kỳ 30 ngày): Thu thập Master Pass Tokens khi vượt màn (Normal: 1 Token, Hard: 2 Tokens, Super Hard: 3 Tokens). Gồm 30 mốc thưởng Free & Premium với Coins, Boosters Set và nhiều Gói thẻ hiếm."
                )
                mp_tier = st.selectbox(
                    ":violet[**Master Pass Tier**]", 
                    ["Free", "Premium"], 
                    key="ui_mp_tier", 
                    disabled=not enable_mp,
                    help="Chọn luồng phần thưởng Master Pass: 'Free' (chỉ nhận mốc Free thông thường) hoặc 'Premium' (nhận song song cả mốc Free và Premium với giá trị thưởng vượt trội)."
                )
            with col_ctrl2:
                enable_core_packs = st.toggle("Thưởng Pack từ Màn Hard/Super Hard", value=st.session_state.get("ui_enable_core_packs", False), key="ui_enable_core_packs", help="Thắng màn Hard nhận Bronze Pack, màn Super Hard nhận Emerald Pack.")
                enable_card_rush = st.toggle(":blue[**Card Rush**] (+50% Thẻ)", value=st.session_state.get("ui_enable_card_rush", True), key="ui_enable_card_rush", help="Vào ngày Card Rush (Thứ 7 hoặc Thứ 4+7), các gói Bronze, Emerald, Silver tự động nâng cấp thành bản Plus (+).")
                enable_chest_drop = st.toggle(":green[**Chest Drop**] (3/7/12 Wins)", value=st.session_state.get("ui_enable_chest_drop", True), key="ui_enable_chest_drop", help="Thắng 3, 7, 12 ván/ngày nhận Rương 1-Sao, 2-Sao, 3-Sao và tự động mở 5-hit.")
                enable_auto_star_chest = st.toggle("Tự động đổi :violet[**Star Chest**] (Đổi Rương Sao)", value=st.session_state.get("ui_enable_auto_star_chest", True), key="ui_enable_auto_star_chest", help="Chiến thuật đổi rương tối ưu: Tích lũy sao ưu tiên đổi Rương Vàng (500⭐ - nhận Rainbow Pack có thẻ mới). Vào ngày cuối mùa hoặc cuối mô phỏng, hệ thống tự động đổi nốt số sao dư theo thứ tự từ cao xuống thấp (Vàng 500⭐ -> Bạc 250⭐ -> Đồng 100⭐).")
        
        st.markdown("<br>", unsafe_allow_html=True)
        col_calc, col_reset, _ = st.columns([1.5, 1.5, 7.0])
        with col_calc:
            calc_button = st.form_submit_button("Calculate", type="primary", use_container_width=True)
        with col_reset:
            reset_button = st.form_submit_button("Reset", on_click=reset_defaults, use_container_width=True)

    if calc_button or st.session_state.config is not None:
        if calc_button:
            st.session_state.config = {
                'sim_days': sim_days, 'daily_sessions': daily_sessions, 'levels_per_session': levels_per_session, 'min_l': min_l, 'max_l': max_l,
                'win_rate_n': win_rate_n, 'win_rate_h': win_rate_h, 'win_rate_sh': win_rate_sh,
                'rv_watch_rate': rv_watch_rate, 'rv_multiplier': rv_multiplier, 
                'booster_use_rate': booster_use_rate, 'revive_buy_rate': revive_buy_rate,
                'enable_keys': enable_keys, 'enable_streak': enable_streak, 'enable_mp': enable_mp, 'mp_tier': mp_tier,
                'enable_core_packs': enable_core_packs, 'enable_card_rush': enable_card_rush, 'enable_chest_drop': enable_chest_drop,
                'enable_auto_star_chest': enable_auto_star_chest,
                'auto_open_packs': True,
                'daily_levels': int(daily_sessions * levels_per_session)
            }
            
        cfg = st.session_state.config
        tuning_cfg = dict(st.session_state.tuning)
        if 'config_packs' in st.session_state:
            tuning_cfg['config_packs'] = st.session_state['config_packs']
        if 'config_chest_drop_tiers' in st.session_state:
            tuning_cfg['config_chest_drop_tiers'] = st.session_state['config_chest_drop_tiers']
        if 'config_chest_upgrade_matrix' in st.session_state:
            tuning_cfg['config_chest_upgrade_matrix'] = st.session_state['config_chest_upgrade_matrix']
        if 'config_chest_drop_x' in st.session_state:
            tuning_cfg['config_chest_drop_x'] = st.session_state['config_chest_drop_x']
        if 'new_card_power' in st.session_state:
            tuning_cfg['new_card_power'] = st.session_state['new_card_power']
        if 'config_ss2_s_base' in st.session_state:
            tuning_cfg['config_ss2_s_base'] = st.session_state['config_ss2_s_base']
        if 'config_ss2_s_max' in st.session_state:
            tuning_cfg['config_ss2_s_max'] = st.session_state['config_ss2_s_max']
        if 'config_ss2_c_base' in st.session_state:
            tuning_cfg['config_ss2_c_base'] = st.session_state['config_ss2_c_base']
        if 'config_ss2_c_max' in st.session_state:
            tuning_cfg['config_ss2_c_max'] = st.session_state['config_ss2_c_max']
        
        # Run Simulation
        res = run_deterministic_simulation(cfg, tuning_cfg)
        st.session_state["last_sim_album"] = res["sim_album_state"]
        st.session_state["last_sim_res"] = res
        
        st.divider()
        st.header(f"Simulation Results (After {res['days']} Days)")
        
        st.subheader("1. Currency Overview (Coins)")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Inflow", f"{int(res['tot_inflow']):,}", f"Avg: {int(res['tot_inflow']/res['days']):,}/day")
        c2.metric("Total Sinks", f"{int(res['tot_sink']):,}", f"Avg: {int(res['tot_sink']/res['days']):,}/day", delta_color="inverse")
        c3.metric("Net Accumulated", f"{int(res['net_accum']):,}", f"Avg: {int(res['net_accum']/res['days']):,}/day")
        c4.metric("Avg Win Rate", f"{res['avg_win_rate']*100:.1f}%")
        
        st.subheader("2. Gameplay & Booster Summary")
        b1, b2, b3, b4 = st.columns(4)
        avg_levels_day = res.get('avg_levels_per_day', res['total_levels_played'] / res['days'])
        avg_levels_str = f"{int(avg_levels_day):,}" if avg_levels_day.is_integer() else f"{avg_levels_day:.1f}"
        b1.metric("Total Levels Played", f"{res['total_levels_played']:,}", f"Avg: {avg_levels_str}/day")
        b2.metric("Total Boosters Used", f"{int(res['total_bst_used_overall']):,}")
        inv = res['final_inv']
        b3.metric("Boosters", f"{inv['Hammer']} H | {inv['Broom']} B | {inv['Scissors']} S")
        b4.metric("Avg Fails / Day", f"{res['failed_levels_per_day']:.1f}")
        
        st.subheader("3. Card Album Progression")
        alb = res['album_summary']
        a1, a2, a3, a4, a5 = st.columns(5)
        cur_season = alb.get('current_season', 1)
        season_label = f"Season {cur_season}" if cur_season > 1 else "Season 1"
        a1.metric(f"Cards ({season_label})", f"{alb['total_cards_owned']} / {alb['total_cards']}", f"{alb['completion_pct']:.1f}% Album")
        a2.metric("Duplicate Stars", f"{alb['total_stars']:,} Stars")
        a3.metric("Completed Sets", f"{alb['completed_sets']} / 15 Sets")
        tot_packs_count = sum(res['tot_packs_earned'].values())
        tot_chests_count = sum(res.get('tot_chests_earned', {}).values())
        a4.metric("Packs Earned", f"{tot_packs_count:,} Packs")
        a5.metric("Chests (Đã đập)", f"{tot_chests_count:,} Rương", "Tự động 5-hit/rương")

        album_coins_str = f"+{res.get('tot_album_coins', 0):,} Coins" if res.get('tot_album_coins', 0) > 0 else "0 Coins"
        alb_bst = res.get('tot_bst_earned_album', {})
        bst_parts = []
        if alb_bst.get('Hammer', 0) > 0: bst_parts.append(f"{alb_bst['Hammer']} Hammer")
        if alb_bst.get('Broom', 0) > 0: bst_parts.append(f"{alb_bst['Broom']} Broom")
        if alb_bst.get('Scissors', 0) > 0: bst_parts.append(f"{alb_bst['Scissors']} Scissors")
        album_bst_str = ", ".join(bst_parts) if bst_parts else "0 Boosters"
        star_chests_info = ""
        tsc = res.get('tot_star_chests', {})
        if sum(tsc.values()) > 0:
            star_chests_info = f" | **Star Chests Đã Đổi:** {tsc.get('Gold',0)} Gold, {tsc.get('Silver',0)} Silver, {tsc.get('Bronze',0)} Bronze"
        st.caption(f"**Phần thưởng nhận từ Hoàn thành Set & Album:** {album_coins_str} | {album_bst_str}{star_chests_info}")

        col_sync_btn, _ = st.columns([3.5, 6.5])
        with col_sync_btn:
            st.markdown("""
            <style>
            div.element-container:has(#sync-btn-sim) + div.element-container button,
            div[data-testid="stColumn"]:has(#sync-btn-sim) button,
            div:has(> #sync-btn-sim) + div button {
                background-color: #dc2626 !important;
                background: linear-gradient(135deg, #ef4444, #dc2626) !important;
                color: #ffffff !important;
                border: 1px solid #b91c1c !important;
                font-weight: bold !important;
                box-shadow: 0 2px 5px rgba(220, 38, 38, 0.3) !important;
            }
            div.element-container:has(#sync-btn-sim) + div.element-container button:hover,
            div[data-testid="stColumn"]:has(#sync-btn-sim) button:hover,
            div:has(> #sync-btn-sim) + div button:hover {
                background: linear-gradient(135deg, #dc2626, #b91c1c) !important;
                border-color: #991b1b !important;
                color: #ffffff !important;
                box-shadow: 0 4px 10px rgba(220, 38, 38, 0.5) !important;
            }
            </style>
            <span id="sync-btn-sim"></span>
            """, unsafe_allow_html=True)
            if st.button("Đồng bộ thẻ sang Tab Card Album", type="primary", use_container_width=True, help="Nạp toàn bộ thẻ, sao, tiến độ 15 set, lịch sử pack mở và chest drop từ kết quả mô phỏng sang Tab Card Album."):
                sim_data = res["sim_album_state"]
                sync_album_state(st.session_state, sim_data, res.get("tot_packs_earned"))
                st.success("Đã đồng bộ thành công sang Bộ Sưu Tập Card Album, Gacha Sandbox & Chest Drop!")

        st.divider()
        st.subheader("4. Resource & Pack Distribution")
        pc1, pc2, pc3, pc4 = st.columns(4)

        liveops_color_map = {
            "Key Collection": "#d97706",
            "Win Streak": "#dc2626",
            "Master Pass": "#7c3aed",
            "Card Rush": "#0284c7",
            "Chest Drop": "#059669",
            "Star Chest": "#8b5cf6",
            "Card Album": "#4f46e5",
            "Gameplay Base": "#3b82f6",
            "Core Gameplay": "#3b82f6",
            "Ads (RV)": "#10b981"
        }

        with pc1:
            in_names = ["Gameplay Base", "Ads (RV)", "Key Collection", "Win Streak", "Master Pass"]
            in_values = [res['tot_base'], res['tot_rv'], res.get('tot_liveops_keys', 0), res.get('tot_liveops_streak', 0), res.get('tot_liveops_mp', 0)]
            if res.get('tot_album_coins', 0) > 0:
                in_names.append("Card Album")
                in_values.append(res['tot_album_coins'])
            fig_in = px.pie(
                names=in_names, 
                values=in_values, 
                title="Coins Inflows Breakdown", 
                hole=0.4, 
                color=in_names,
                color_discrete_map=liveops_color_map
            )
            st.plotly_chart(fig_in, use_container_width=True)
        with pc2:
            keys_bst = res['tot_bst_earned_keys']
            streak_bst = res['tot_bst_earned_streak']
            mp_bst = res.get('tot_bst_earned_mp', {'Hammer': 0, 'Broom': 0, 'Scissors': 0})
            album_bst_total = sum(res.get('tot_bst_earned_album', {}).values())
            
            total_keys = sum(keys_bst.values())
            total_streak = sum(streak_bst.values())
            total_mp = sum(mp_bst.values())
            
            bst_names = ["Key Collection", "Win Streak", "Master Pass"]
            bst_values = [total_keys, total_streak, total_mp]
            if album_bst_total > 0:
                bst_names.append("Card Album")
                bst_values.append(album_bst_total)
            
            fig_out = px.pie(
                names=bst_names,
                values=bst_values,
                title="Booster Inflows (By Source)", 
                hole=0.4, 
                color=bst_names,
                color_discrete_map=liveops_color_map
            )
            st.plotly_chart(fig_out, use_container_width=True)
        with pc3:
            pack_dist = {k: v for k, v in res['tot_packs_earned'].items() if v > 0}
            if pack_dist:
                fig_packs = px.pie(
                    names=list(pack_dist.keys()),
                    values=list(pack_dist.values()),
                    title="Packs Earned (By Type)", hole=0.4, color_discrete_sequence=px.colors.qualitative.Bold
                )
                st.plotly_chart(fig_packs, use_container_width=True)
            else:
                st.info("No packs earned.")
        with pc4:
            lo_pack_sources = [
                ("Core Gameplay", sum(res.get('tot_packs_earned_core', {}).values())),
                ("Master Pass", sum(res.get('tot_packs_earned_mp', {}).values())),
                ("Win Streak", sum(res.get('tot_packs_earned_streak', {}).values())),
                ("Key Collection", sum(res.get('tot_packs_earned_keys', {}).values())),
                ("Star Chest", sum(res.get('tot_packs_earned_star_chest', {}).values()))
            ]
            lo_p_names = [s for s, c in lo_pack_sources if c > 0]
            lo_p_values = [c for s, c in lo_pack_sources if c > 0]
            if lo_p_values:
                fig_lo_packs = px.pie(
                    names=lo_p_names,
                    values=lo_p_values,
                    title="Packs Earned (By LiveOps Source)",
                    hole=0.4,
                    color=lo_p_names,
                    color_discrete_map=liveops_color_map
                )
                st.plotly_chart(fig_lo_packs, use_container_width=True)
            else:
                st.info("No packs earned.")

        st.divider()
        st.subheader(f"Daily Trends ({res['days']}-Day Logs)")
        
        df_log = pd.DataFrame(res['macro_log'])
        df_log['BoostersEarnedTotal'] = df_log['BoostersEarned'].apply(lambda x: sum(x.values()))
        df_log['BoostersSpentTotal'] = df_log['BoostersSpent'].apply(lambda x: sum(x.values()))
        
        # 1. Coins Chart
        coins_chart_type = st.radio("Coins Chart Type", ["Daily Flow", "Cumulative Balance"], horizontal=True)
        fig_coins = go.Figure()
        if coins_chart_type == "Daily Flow":
            fig_coins.add_trace(go.Bar(x=df_log['Day'], y=df_log['CoinsEarned'], name='Earned (+)', marker_color='#2ca02c'))
            fig_coins.add_trace(go.Bar(x=df_log['Day'], y=-df_log['CoinsSpent'], name='Spent (-)', marker_color='#d62728'))
            fig_coins.update_layout(barmode='relative', title='Daily Coins Flow', xaxis_title='Day', yaxis_title='Coins', margin=dict(l=0, r=0, t=40, b=0), height=400)
        else:
            fig_coins.add_trace(go.Scatter(x=df_log['Day'], y=df_log.get('CumulativeCoins', []), mode='lines+markers', name='Cumulative Coins', marker_color='#1f77b4', fill='tozeroy'))
            fig_coins.update_layout(title='Cumulative Coins Balance', xaxis_title='Day', yaxis_title='Total Coins', margin=dict(l=0, r=0, t=40, b=0), height=400)
        st.plotly_chart(fig_coins, use_container_width=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 2. Boosters Chart
        df_log['InvTotal'] = df_log['Inv'].apply(lambda x: sum(x.values()))
        boosters_chart_type = st.radio("Boosters Chart Type", ["Daily Flow", "Cumulative Balance"], horizontal=True)
        fig_boosters = go.Figure()
        if boosters_chart_type == "Daily Flow":
            fig_boosters.add_trace(go.Bar(x=df_log['Day'], y=df_log['BoostersEarnedTotal'], name='Earned (+)', marker_color='#2ca02c'))
            fig_boosters.add_trace(go.Bar(x=df_log['Day'], y=-df_log['BoostersSpentTotal'], name='Spent (-)', marker_color='#d62728'))
            fig_boosters.update_layout(barmode='relative', title='Daily Boosters Flow', xaxis_title='Day', yaxis_title='Total Boosters (H+B+S)', margin=dict(l=0, r=0, t=40, b=0), height=400)
        else:
            fig_boosters.add_trace(go.Scatter(x=df_log['Day'], y=df_log['InvTotal'], mode='lines+markers', name='Cumulative Boosters', marker_color='#1f77b4', fill='tozeroy'))
            fig_boosters.update_layout(title='Cumulative Boosters Inventory', xaxis_title='Day', yaxis_title='Total Boosters', margin=dict(l=0, r=0, t=40, b=0), height=400)
        st.plotly_chart(fig_boosters, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # 3. Card Album Growth Chart
        fig_album = go.Figure()
        fig_album.add_trace(go.Scatter(x=df_log['Day'], y=df_log['AlbumTotalOwned'], mode='lines+markers', name='Cards Collected', line=dict(color='#9467bd', width=3), fill='tozeroy'))
        fig_album.add_trace(go.Scatter(x=df_log['Day'], y=[135]*len(df_log), mode='lines', name='Album Max (135)', line=dict(color='#d62728', dash='dash')))
        fig_album.update_layout(title='Card Album Growth (Cards Owned vs Max)', xaxis_title='Day', yaxis_title='Unique Cards Owned', margin=dict(l=0, r=0, t=40, b=0), height=400)
        st.plotly_chart(fig_album, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # 4. Daily Chest Drop Chart
        df_log['Chest1'] = df_log['ChestsEarned'].apply(lambda x: x.get(1, 0) if isinstance(x, dict) else 0)
        df_log['Chest2'] = df_log['ChestsEarned'].apply(lambda x: x.get(2, 0) if isinstance(x, dict) else 0)
        df_log['Chest3'] = df_log['ChestsEarned'].apply(lambda x: x.get(3, 0) if isinstance(x, dict) else 0)
        df_log['TotalChests'] = df_log['Chest1'] + df_log['Chest2'] + df_log['Chest3']

        chests_chart_view = st.radio("Chest Drop Chart View", ["Breakdown by Tier", "Total Daily Chests"], horizontal=True)
        fig_chestdrop = go.Figure()
        if chests_chart_view == "Breakdown by Tier":
            fig_chestdrop.add_trace(go.Bar(x=df_log['Day'], y=df_log['Chest1'], name='1-Sao (3 Wins)', marker_color='#cd7f32'))
            fig_chestdrop.add_trace(go.Bar(x=df_log['Day'], y=df_log['Chest2'], name='2-Sao (7 Wins)', marker_color='#4682b4'))
            fig_chestdrop.add_trace(go.Bar(x=df_log['Day'], y=df_log['Chest3'], name='3-Sao (12 Wins)', marker_color='#ffd700'))
            fig_chestdrop.update_layout(barmode='stack', title='Daily Chest Drop Earned (By Tier)', xaxis_title='Day', yaxis_title='Chests Earned', margin=dict(l=0, r=0, t=40, b=0), height=400)
        else:
            fig_chestdrop.add_trace(go.Bar(x=df_log['Day'], y=df_log['TotalChests'], name='Total Chests', marker_color='#ff7f0e'))
            fig_chestdrop.update_layout(title='Total Daily Chest Drop Earned', xaxis_title='Day', yaxis_title='Chests Earned', margin=dict(l=0, r=0, t=40, b=0), height=400)
        st.plotly_chart(fig_chestdrop, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # 5. LiveOps Tokens Chart
        fig_liveops = go.Figure()
        fig_liveops.add_trace(go.Bar(x=df_log['Day'], y=df_log['DailyKeys'], name='Keys Earned', marker_color='#d97706'))
        if 'DailyMPTokens' in df_log.columns:
            fig_liveops.add_trace(go.Bar(x=df_log['Day'], y=df_log['DailyMPTokens'], name='MP Tokens', marker_color='#7c3aed'))
        fig_liveops.add_trace(go.Bar(x=df_log['Day'], y=df_log['DailyStreak'], name='Max Win Streak', marker_color='#dc2626'))
        fig_liveops.update_layout(
            barmode='group',
            title='Daily LiveOps (Tokens & Streak)', 
            xaxis_title='Day', 
            yaxis=dict(title='Count', rangemode='tozero'), 
            margin=dict(l=0, r=0, t=40, b=0), 
            height=400
        )
        st.plotly_chart(fig_liveops, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # 6. Levels Won vs Lost Chart
        levels_chart_type = st.radio("Levels Chart Type", ["Daily Levels", "Cumulative Levels"], horizontal=True)
        fig_levels = go.Figure()
        if levels_chart_type == "Daily Levels":
            fig_levels.add_trace(go.Bar(x=df_log['Day'], y=df_log.get('LevelsWon', []), name='Won Levels', marker_color='#2ca02c'))
            fig_levels.add_trace(go.Bar(x=df_log['Day'], y=df_log.get('LevelsLost', []), name='Lost Levels', marker_color='#d62728'))
            fig_levels.update_layout(
                barmode='group',
                title='Daily Levels Played (Won vs Lost)',
                xaxis_title='Day',
                yaxis_title='Levels',
                margin=dict(l=0, r=0, t=40, b=0),
                height=400
            )
        else:
            df_log['CumulativeWon'] = df_log.get('LevelsWon', pd.Series()).cumsum()
            df_log['CumulativeLost'] = df_log.get('LevelsLost', pd.Series()).cumsum()
            df_log['CumulativeTotal'] = df_log.get('LevelsPlayed', pd.Series()).cumsum()
            fig_levels.add_trace(go.Scatter(x=df_log['Day'], y=df_log['CumulativeTotal'], mode='lines+markers', name='Total Levels Played', marker_color='#1f77b4', line=dict(width=3)))
            fig_levels.add_trace(go.Scatter(x=df_log['Day'], y=df_log['CumulativeWon'], mode='lines+markers', name='Cumulative Won', marker_color='#2ca02c', line=dict(dash='dash')))
            fig_levels.add_trace(go.Scatter(x=df_log['Day'], y=df_log['CumulativeLost'], mode='lines+markers', name='Cumulative Lost', marker_color='#d62728', line=dict(dash='dot')))
            fig_levels.update_layout(
                title='Cumulative Levels Played',
                xaxis_title='Day',
                yaxis_title='Total Levels',
                margin=dict(l=0, r=0, t=40, b=0),
                height=400
            )
        st.plotly_chart(fig_levels, use_container_width=True)

        st.divider()
        st.subheader("Daily Detailed Logs")
        
        with st.expander("Click to view full logs for all days"):
            for lg in res['macro_log']:
                st.markdown(f"### Day {lg['Day']} ({lg['DayName']})")
                inv = lg['Inv']
                inv_parts = []
                if inv['Hammer'] > 0: inv_parts.append(f"{inv['Hammer']} Hammer")
                if inv['Broom'] > 0: inv_parts.append(f"{inv['Broom']} Broom")
                if inv['Scissors'] > 0: inv_parts.append(f"{inv['Scissors']} Scissors")
                inv_str = ", ".join(inv_parts) if inv_parts else "Empty"
                
                mp_tier_str = lg.get('MPTier', 'Free')
                if mp_tier_str != 'Off':
                    mp_info = f":violet[**Master Pass [{mp_tier_str}]:**] Stage {lg.get('MPStage', 0)} ({lg.get('MPTokens', 0)} Tokens)"
                else:
                    mp_info = ":violet[**Master Pass:**] Off"
                keys_info = f":orange[**Key Collection:**] Stage {lg.get('KeyStage', 0)} ({lg.get('DailyKeys', 0)} Keys)"
                streak_info = f":red[**Win Streak:**] Stage {lg.get('StreakStage', 0)} ({lg.get('DailyStreak', 0)} Wins)"
                album_info = f":blue[**Card Album:**] **{lg.get('AlbumTotalOwned', 0)}/135** ({lg.get('AlbumCompletionPct', 0.0):.1f}%) | Stars: **{lg.get('AlbumStarsTotal', 0)}** | Sets Completed: **{lg.get('AlbumSetsCompleted', 0)}/15**"

                st.markdown(
                    f"- **Gameplay & Wallet:** Levels: **{lg.get('LevelsPlayed', 0)}** (Won: {lg.get('LevelsWon', 0)}, Lost: {lg.get('LevelsLost', 0)}) | "
                    f"Daily Coins: **+{lg['CoinsEarned']:,}** / **-{lg['CoinsSpent']:,}** | "
                    f"Cumulative Balance: **{lg.get('CumulativeCoins', 0):,}** | "
                    f"Inventory: **{inv_str}**  \n"
                    f"- **LiveOps Status:** {keys_info} | {streak_info} | {mp_info}  \n"
                    f"- **Card Album:** {album_info}"
                )
                
                if lg['CoinLog']:
                    st.markdown("**Coins Flow**")
                    for item in lg['CoinLog']: st.markdown(f"- {highlight_liveops(item)}")
                
                if lg['BoosterLog']:
                    st.markdown("**Boosters Flow**")
                    for item in lg['BoosterLog']: st.markdown(f"- {highlight_liveops(item)}")
                
                if lg['EventLog']:
                    st.markdown("**Events & Album Logs**")
                    for item in lg['EventLog']: st.markdown(f"- {highlight_liveops(item)}")
                    
                st.markdown("---")
