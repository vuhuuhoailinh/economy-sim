import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from simulation.macro_sim import run_macro_simulation

def render_macro_tab():
    st.header("Simulation Settings")
    
    with st.expander("📌 System Assumptions (Giả định hệ thống)", expanded=False):
        st.markdown("""
        - **Level Progression**: Cấu trúc độ khó xoay vòng n-n-h-n-n-h-n-n-sh.
        - **LiveOps Status**: Mặc định giả sử người chơi đã mở khóa (unlock) tất cả các LiveOps.
        - **Calendar**: Ngày 1 của mô phỏng luôn luôn là **Thứ Hai (Monday)**.
        - **Win Streak**: Sự kiện chuỗi thắng chỉ diễn ra vào cuối tuần, từ **Thứ Sáu đến hết Chủ Nhật**.
        """)
        
    with st.form("macro_form"):
        col_p1, col_p2, col_p3 = st.columns(3)
        with col_p1:
            st.subheader("Player Behavior")
            sim_days = st.slider("Simulation Days", 1, 180, 60)
            daily_sessions = st.slider("Sessions/Day", 1, 5, 2)
            c_min, c_max = st.columns(2)
            min_l = c_min.number_input("Levels/Session (Min)", 1, 50, 1)
            max_l = c_max.number_input("Levels/Session (Max)", min_l, 50, max(4, min_l))
            
            levels_per_session = (min_l + max_l) / 2.0
            
        with col_p2:
            st.subheader("Win Rates")
            win_rate_n = st.slider("Normal Level", 0.0, 1.0, 1.0)
            win_rate_h = st.slider("Hard Level", 0.0, 1.0, 0.80)
            win_rate_sh = st.slider("Super Hard", 0.0, 1.0, 0.60)
            
        with col_p3:
            st.subheader("Monetization & Sinks")
            rv_watch_rate = st.slider("RV Watch Rate", 0.0, 1.0, 0.25)
            rv_multiplier = st.slider("RV Multiplier", 2.0, 5.0, 3.0)
            
            booster_use_rate = st.slider("Booster Use Rate", 0.0, 1.0, 0.50, help="Tỉ lệ người chơi sử dụng booster đang có sẵn trong túi.")
            revive_buy_rate = st.slider("Revive Buy Rate", 0.0, 1.0, 0.02, help="Tỉ lệ dùng Coins mua mạng (chỉ mua khi đủ tiền).")
            booster_buy_rate = st.slider("Booster Purchase Rate", 0.0, 1.0, 0.10, help="Tỉ lệ mua Booster khi túi trống (chỉ mua khi đủ tiền).")
            
        calc_button = st.form_submit_button("Save Configuration & Calculate")

    if calc_button or st.session_state.config is not None:
        if calc_button:
            st.session_state.config = {
                'sim_days': sim_days, 'daily_sessions': daily_sessions, 'levels_per_session': levels_per_session, 'min_l': min_l, 'max_l': max_l,
                'win_rate_n': win_rate_n, 'win_rate_h': win_rate_h, 'win_rate_sh': win_rate_sh,
                'rv_watch_rate': rv_watch_rate, 'rv_multiplier': rv_multiplier, 
                'booster_use_rate': booster_use_rate, 'revive_buy_rate': revive_buy_rate,
            'booster_buy_rate': booster_buy_rate,
                'daily_levels': int(daily_sessions * levels_per_session)
            }
            
        cfg = st.session_state.config
        tuning_cfg = st.session_state.tuning
        
        # Run Simulation
        res = run_macro_simulation(cfg, tuning_cfg)
        
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
        b1.metric("Total Levels Played", f"{res['total_levels_played']:,}")
        b2.metric("Total Boosters Used", f"{int(res['total_bst_used_overall']):,}", "Free + Purchased")
        inv = res['final_inv']
        b3.metric("Free Boosters (Inv)", f"{inv['Hammer']}H | {inv['Broom']}B | {inv['Scissors']}S")
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
            fig_in = px.pie(names=["Gameplay Base", "Ads (RV)", "LiveOps"], 
                            values=[res['tot_base'], res['tot_rv'], res['tot_liveops']], 
                            title="Inflows Breakdown", hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig_in, use_container_width=True)
        with pc2:
            tot_bst_earned = res['tot_bst_earned']
            fig_out = px.pie(
                names=["Hammer", "Broom", "Scissors"],
                values=[tot_bst_earned['Hammer'], tot_bst_earned['Broom'], tot_bst_earned['Scissors']],
                title="Booster Inflow Breakdown", hole=0.4, color_discrete_sequence=px.colors.qualitative.Set3
            )
            st.plotly_chart(fig_out, use_container_width=True)

        st.divider()
        st.subheader("Daily Trends (30-Day Logs)")
        
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
        
        fig_liveops = go.Figure()
        fig_liveops.add_trace(go.Bar(x=df_log['Day'], y=df_log['DailyKeys'], name='Keys Earned', marker_color='#1f77b4'))
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
        
        fig_boosters = go.Figure()
        fig_boosters.add_trace(go.Bar(x=df_log['Day'], y=df_log['BoostersEarnedTotal'], name='Earned (+)', marker_color='#2ca02c'))
        fig_boosters.add_trace(go.Bar(x=df_log['Day'], y=-df_log['BoostersSpentTotal'], name='Spent (-)', marker_color='#d62728'))
        fig_boosters.update_layout(barmode='relative', title='Daily Boosters Flow', xaxis_title='Day', yaxis_title='Total Boosters (H+B+S)', margin=dict(l=0, r=0, t=40, b=0), height=400)
        st.plotly_chart(fig_boosters, use_container_width=True)

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
                
                st.caption(
                    f"**Levels Played:** {lg.get('LevelsPlayed', 0)} | "
                    f"**Daily Coins:** +{lg['CoinsEarned']} / -{lg['CoinsSpent']} | "
                    f"**Cumulative Coins:** {lg.get('CumulativeCoins', 0):,} | "
                    f"**Keys (Stage {lg['KeyStage']}):** {lg['DailyKeys']} | "
                    f"**Streak (Stage {lg['StreakStage']}):** {lg['DailyStreak']} | "
                    f"**Inventory:** {inv_str}"
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