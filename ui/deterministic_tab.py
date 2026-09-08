import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from simulation.deterministic_sim import run_deterministic_simulation

def reset_defaults():
    for k, v in st.session_state.default_config.items():
        st.session_state[f"ui_{k}"] = v

def set_defaults():
    st.session_state.default_config = {
        'sim_days': st.session_state.ui_sim_days,
        'daily_sessions': st.session_state.ui_daily_sessions,
        'min_l': st.session_state.ui_min_l,
        'max_l': st.session_state.ui_max_l,
        'win_rate_n': st.session_state.ui_win_rate_n,
        'win_rate_h': st.session_state.ui_win_rate_h,
        'win_rate_sh': st.session_state.ui_win_rate_sh,
        'rv_watch_rate': st.session_state.ui_rv_watch_rate,
        'rv_multiplier': st.session_state.ui_rv_multiplier,
        'booster_use_rate': st.session_state.ui_booster_use_rate,
        'revive_buy_rate': st.session_state.ui_revive_buy_rate,
        'enable_keys': st.session_state.ui_enable_keys,
        'enable_streak': st.session_state.ui_enable_streak,
        'enable_mp': st.session_state.ui_enable_mp,
        'mp_tier': st.session_state.ui_mp_tier
    }
    
def render_deterministic_tab():
    st.header("Simulation Settings")
    
    with st.expander("System Assumptions & Economy Overview", expanded=False):
        st.markdown("""
        ### 1. Level Progression & Win Rates
        - Level Progression: **6 Normal (N) - 2 Hard (H) - 1 Super Hard (SH)**.
        - **Tiền thưởng cơ bản khi thắng màn (Base Coins)**:
          - Normal: **20 Coins**
          - Hard: **40 Coins** (gấp 2 lần)
          - Super Hard: **60 Coins** (gấp 3 lần)
          - *Trung bình một màn thắng nhận được: ~28.89 Coins (trước khi xem quảng cáo).*
        - **Tỷ lệ thắng (Win Rate mặc định)**: Normal 100%, Hard 90%, Super Hard 80%.

        ### 2. Coins Economy: Faucets & Sinks
        - **Nguồn bơm tiền (Inflows / Faucets)**:
          - **Gameplay Base**: Nhận trực tiếp mỗi khi vượt qua màn chơi.
          - **Rewarded Video (Ads)**: Xem quảng cáo sau khi thắng để nhận hệ số nhân thưởng (Mặc định: 25% tỷ lệ xem với hệ số x3 tiền thưởng).
          - **Key Collection**: Tiền thưởng từ các mốc chìa khóa của sự kiện trong tuần.
          - **Win Streak**: Thưởng tiền trực tiếp khi đạt chuỗi thắng cao (Mốc 2: 40 coins, Mốc 18: 80 coins, Mốc 36: 300 coins). Các gói Card Pack là vật phẩm sưu tập thẻ, không tính vào Coins.
          - **Master Pass**: 
            - Các mốc thưởng Coins trực tiếp: Free gồm mốc 3, 6, 16, 22, 30 (tổng 480 Coins); Premium nhận thêm mốc 0, 5, 10, 15, 20, 25, 30 (tổng thêm 2,500 Coins). Các gói thẻ Card Packs (Emerald, Silver, Amethyst, Ruby, Rainbow...) không quy đổi ra Coins.
            - **Bonus Bank**: Sau khi vượt qua mốc 30 (max stage), mỗi 10 Tokens tích lũy thêm sẽ cộng 150 Coins vào ngân hàng thưởng (tối đa 3,000 Coins), được chi trả vào ngày cuối cùng của chu kỳ 30 ngày.
        - **Nguồn xả tiền (Outflows / Sinks)**:
          - **Revive (Hồi sinh)**: Khi thua màn, người chơi có xác suất `Revive Buy Rate` (Mặc định 10%) tiêu tốn **380 Coins** để mua tiếp 5 lượt đi (thay vì xem Ads hoặc bỏ cuộc).
          - *Lưu ý: Game không cho phép dùng Coins mua trực tiếp Booster trong màn chơi.*

        ### 3. Booster Economy: Faucets & Sinks
        - **Nhóm Booster hỗ trợ**: Hammer (Búa), Broom (Chổi), Scissors (Kéo).
        - **Nguồn nhận Booster (Inflows)**:
          - **Key Collection**: Thưởng qua rương mốc chìa khóa.
          - **Win Streak**: Thưởng từ mốc chuỗi thắng cao (Mốc 11 nhận Scissors, Mốc 30 nhận Hammer, Mốc 36 nhận Broom).
          - **Master Pass**: Mốc 0 mở khóa nhận ngay 1x Hammer, và các mốc giải thưởng đan xen xuyên suốt 30 stage.
        - **Tiêu thụ Booster (Sinks)**:
          - Cứ mỗi màn chơi bắt đầu, dựa trên `Booster Use Rate` người chơi sẽ **bốc ngẫu nhiên 1 trong 3 loại booster** có sẵn trong kho để sử dụng. Nếu kho đồ không còn loại nào, người chơi sẽ không tiêu thụ booster.

        ### 4. Calendar & Cadence
        - **Lịch vận hành tuần**: Ngày 1 của mô phỏng luôn mặc định là **Thứ Hai (Monday)**.
        - **Key Collection**: Diễn ra từ **Thứ Hai đến Thứ Năm** (Ngày 1 - 4). Mỗi màn thắng nhận **5 Keys**.
        - **Win Streak**: Diễn ra vào cuối tuần từ **Thứ Sáu đến Chủ Nhật** (Ngày 5 - 7). Chuỗi thắng tích lũy theo số ván thắng liên tiếp; nếu thua trận sẽ bị ngắt chuỗi về 0.
        - **Master Pass**: Chu kỳ kéo dài **30 ngày** (reset hàng tháng).
          - Tokens nhận được khi thắng màn: Normal = **1 Token**, Hard = **2 Tokens**, Super Hard = **3 Tokens**.
          - Hoàn thành các mốc để nhận thưởng. Sau khi vượt mốc 30 sẽ bắt đầu tích Coins vào Bonus Bank.
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
            st.subheader("LiveOps Controls")
            col_ctrl, _ = st.columns([2.5, 4.5])
            with col_ctrl:
                enable_keys = st.toggle("Key Collection", key="ui_enable_keys")
                enable_streak = st.toggle("Win Streak", key="ui_enable_streak")
                enable_mp = st.toggle("Master Pass", key="ui_enable_mp")
                mp_tier = st.selectbox("Master Pass Tier", ["Free", "Premium"], key="ui_mp_tier", disabled=not enable_mp)
        
        st.markdown("<br>", unsafe_allow_html=True)
        col_btns, _ = st.columns([1.5, 8.5])
        with col_btns:
            calc_button = st.form_submit_button("Calculate", type="primary")
            set_default_button = st.form_submit_button("Save", on_click=set_defaults)
            reset_button = st.form_submit_button("Reset", on_click=reset_defaults)
            
    if set_default_button:
        st.success("Saved as default!")

    if calc_button or st.session_state.config is not None:
        if calc_button or set_default_button:
            st.session_state.config = {
                'sim_days': sim_days, 'daily_sessions': daily_sessions, 'levels_per_session': levels_per_session, 'min_l': min_l, 'max_l': max_l,
                'win_rate_n': win_rate_n, 'win_rate_h': win_rate_h, 'win_rate_sh': win_rate_sh,
                'rv_watch_rate': rv_watch_rate, 'rv_multiplier': rv_multiplier, 
                'booster_use_rate': booster_use_rate, 'revive_buy_rate': revive_buy_rate,
                'enable_keys': enable_keys, 'enable_streak': enable_streak, 'enable_mp': enable_mp, 'mp_tier': mp_tier,
                'daily_levels': int(daily_sessions * levels_per_session)
            }
            
        cfg = st.session_state.config
        tuning_cfg = st.session_state.tuning
        
        # Run Simulation
        res = run_deterministic_simulation(cfg, tuning_cfg)
        
        st.divider()
        st.header(f"Simulation Results (After {res['days']} Days)")
        
        st.subheader("1. Currency Overview (Coins)")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric(f"Total Inflow", f"{int(res['tot_inflow']):,}", f"Avg: {int(res['tot_inflow']/res['days']):,}/day")
        c2.metric(f"Total Sinks", f"{int(res['tot_sink']):,}", f"Avg: {int(res['tot_sink']/res['days']):,}/day", delta_color="inverse")
        c3.metric(f"Net Accumulated", f"{int(res['net_accum']):,}", f"Avg: {int(res['net_accum']/res['days']):,}/day")
        c4.metric(f"Avg Win Rate", f"{res['avg_win_rate']*100:.1f}%")
        
        st.subheader("2. Gameplay & Booster Summary")
        b1, b2, b3, b4 = st.columns(4)
        avg_levels_day = res.get('avg_levels_per_day', res['total_levels_played'] / res['days'])
        avg_levels_str = f"{int(avg_levels_day):,}" if avg_levels_day.is_integer() else f"{avg_levels_day:.1f}"
        b1.metric("Total Levels Played", f"{res['total_levels_played']:,}", f"Avg: {avg_levels_str}/day")
        b2.metric("Total Boosters Used", f"{int(res['total_bst_used_overall']):,}")
        inv = res['final_inv']
        b3.metric("Boosters", f"{inv['Hammer']} H | {inv['Broom']} B | {inv['Scissors']} S")
        b4.metric("Avg Fails / Day", f"{res['failed_levels_per_day']:.1f}")
        
        st.divider()
        prices_df = tuning_cfg.get('prices')
        if prices_df is not None and not prices_df.empty:
            cost_dict = dict(zip(prices_df['Item'], prices_df['Price']))
        else:
            cost_dict = {'Revive': 380, 'Hammer': 160, 'Broom': 240, 'Scissors': 120}
            
        st.subheader("3. Resource Distribution")
        pc1, pc2 = st.columns(2)
        with pc1:
            fig_in = px.pie(names=["Gameplay Base", "Ads (RV)", "Key Collection", "Win Streak", "Master Pass"], 
                            values=[res['tot_base'], res['tot_rv'], res.get('tot_liveops_keys', 0), res.get('tot_liveops_streak', 0), res.get('tot_liveops_mp', 0)], 
                            title="Inflows Breakdown", hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig_in, use_container_width=True)
        with pc2:
            keys_bst = res['tot_bst_earned_keys']
            streak_bst = res['tot_bst_earned_streak']
            mp_bst = res.get('tot_bst_earned_mp', {'Hammer': 0, 'Broom': 0, 'Scissors': 0})
            
            total_keys = sum(keys_bst.values())
            total_streak = sum(streak_bst.values())
            total_mp = sum(mp_bst.values())
            
            fig_out = px.pie(
                names=["Key Collection", "Win Streak", "Master Pass"],
                values=[total_keys, total_streak, total_mp],
                title="Booster Inflow (By Source)", hole=0.4, color_discrete_sequence=px.colors.qualitative.Set3
            )
            st.plotly_chart(fig_out, use_container_width=True)

        st.divider()
        st.subheader(f"Daily Trends ({res['days']}-Day Logs)")
        
        df_log = pd.DataFrame(res['macro_log'])
        df_log['BoostersEarnedTotal'] = df_log['BoostersEarned'].apply(lambda x: sum(x.values()))
        df_log['BoostersSpentTotal'] = df_log['BoostersSpent'].apply(lambda x: sum(x.values()))
        
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

        fig_liveops = go.Figure()
        fig_liveops.add_trace(go.Bar(x=df_log['Day'], y=df_log['DailyKeys'], name='Keys Earned', marker_color='#1f77b4'))
        if 'DailyMPTokens' in df_log.columns:
            fig_liveops.add_trace(go.Bar(x=df_log['Day'], y=df_log['DailyMPTokens'], name='MP Tokens', marker_color='#9467bd'))
        fig_liveops.add_trace(go.Bar(x=df_log['Day'], y=df_log['DailyStreak'], name='Max Win Streak', marker_color='#ff7f0e'))
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
                    mp_info = f"Master Pass [{mp_tier_str}]: Stage {lg.get('MPStage', 0)} ({lg.get('MPTokens', 0)} Tokens)"
                else:
                    mp_info = "Master Pass: Off"
                keys_info = f"Keys: Stage {lg.get('KeyStage', 0)} ({lg.get('DailyKeys', 0)} Keys)"
                streak_info = f"Streak: Stage {lg.get('StreakStage', 0)} ({lg.get('DailyStreak', 0)} Wins)"

                st.markdown(
                    f"- **Gameplay & Wallet:** Levels: **{lg.get('LevelsPlayed', 0)}** (Won: {lg.get('LevelsWon', 0)}, Lost: {lg.get('LevelsLost', 0)}) | "
                    f"Daily Coins: **+{lg['CoinsEarned']:,}** / **-{lg['CoinsSpent']:,}** | "
                    f"Cumulative Balance: **{lg.get('CumulativeCoins', 0):,}** | "
                    f"Inventory: **{inv_str}**  \n"
                    f"- **LiveOps Status:** {keys_info} | {streak_info} | {mp_info}"
                )
                
                if lg['CoinLog']:
                    st.markdown("**Coins Flow**")
                    for item in lg['CoinLog']: st.markdown(f"- {item}")
                
                if lg['BoosterLog']:
                    st.markdown("**Boosters Flow**")
                    for item in lg['BoosterLog']: st.markdown(f"- {item}")
                
                if lg['EventLog']:
                    st.markdown("**Events & Tokens**")
                    for item in lg['EventLog']: st.markdown(f"- {item}")
                    
                st.markdown("---")