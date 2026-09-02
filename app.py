import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import random

st.set_page_config(page_title="Economy Sim Dashboard", layout="wide", page_icon="🎮")
st.title("🎮 Game Economy Simulation Dashboard")

# --- CONSTANTS ---
COIN_N, COIN_H, COIN_SH = 20, 40, 60
COST = {'Revive': 190, 'Hammer': 120, 'Broom': 120, 'Scissors': 120, 'Booster Set': 380}

LIVEOPS = {
    'Key Collection': {'cadence': 7, 'reward': 1400, 'bst_hammer': 1, 'bst_broom': 1, 'bst_scissors': 0},
    'Win Streak': {'cadence': 3, 'reward': 420, 'bst_hammer': 0, 'bst_broom': 0, 'bst_scissors': 0},
    'Card Album': {'cadence': 60, 'reward': 6250, 'bst_hammer': 2, 'bst_broom': 1, 'bst_scissors': 2},
}

tabs = st.tabs(["📊 Macro Economy", "🎲 Micro Simulation", "⚙️ Economy Tuning"])

if 'config' not in st.session_state:
    st.session_state.config = None

# ==============================================================================
# TAB 1: MACRO ECONOMY & SETTINGS
# ==============================================================================
with tabs[0]:
    st.header("Macro Simulation Settings")
    
    with st.form("macro_form"):
        col_p1, col_p2, col_p3 = st.columns(3)
        with col_p1:
            st.subheader("Player Behavior")
            sim_days = st.slider("Simulation Days", 1, 100, 30)
            daily_sessions = st.slider("Sessions/Day", 1, 5, 2)
            levels_per_session = st.slider("Levels/Session", 1, 10, 2)
            
        with col_p2:
            st.subheader("Win Rates")
            win_rate_n = st.slider("Normal Level", 0.0, 1.0, 0.80)
            win_rate_h = st.slider("Hard Level", 0.0, 1.0, 0.40)
            win_rate_sh = st.slider("Super Hard", 0.0, 1.0, 0.15)
            
        with col_p3:
            st.subheader("Monetization & Sinks")
            rv_watch_rate = st.slider("RV Watch Rate", 0.0, 1.0, 0.25)
            rv_multiplier = st.slider("RV Multiplier", 2.0, 5.0, 3.0)
            booster_buy_rate = st.slider("Booster Purchase Rate (on fail)", 0.0, 1.0, 0.10)
            
        calc_button = st.form_submit_button("Save Configuration & Calculate")

    if calc_button or st.session_state.config is not None:
        if calc_button:
            st.session_state.config = {
                'sim_days': sim_days, 'daily_sessions': daily_sessions, 'levels_per_session': levels_per_session,
                'win_rate_n': win_rate_n, 'win_rate_h': win_rate_h, 'win_rate_sh': win_rate_sh,
                'rv_watch_rate': rv_watch_rate, 'rv_multiplier': rv_multiplier, 'booster_buy_rate': booster_buy_rate,
                'daily_levels': daily_sessions * levels_per_session
            }
        cfg = st.session_state.config
        days = cfg['sim_days']
        daily_levels = cfg['daily_levels']
        
        avg_base_coin_per_lvl = (COIN_N * 6 + COIN_H * 2 + COIN_SH * 1) / 9
        avg_win_rate = (cfg['win_rate_n'] * 6 + cfg['win_rate_h'] * 2 + cfg['win_rate_sh'] * 1) / 9
        failed_levels_per_day = daily_levels * (1 - avg_win_rate)
        
        avg_booster_cost = (COST['Revive'] * 0.5) + (COST['Hammer'] * 0.2) + (COST['Broom'] * 0.2) + (COST['Scissors'] * 0.1)
        
        tot_base, tot_rv, tot_liveops, tot_sink = 0, 0, 0, 0
        
        inv = {'Hammer': 0, 'Broom': 0, 'Scissors': 0}
        tot_bst_earned = {'Hammer': 0, 'Broom': 0, 'Scissors': 0}
        tot_bst_used_free = {'Hammer': 0, 'Broom': 0, 'Scissors': 0}
        tot_bst_bought = {'Revive': 0, 'Hammer': 0, 'Broom': 0, 'Scissors': 0}
        
        macro_log = []
        
        # We accumulate fractions but cast to int when appending to the log to represent a discrete 1-player experience
        accum_needed = {'Revive': 0.0, 'Hammer': 0.0, 'Broom': 0.0, 'Scissors': 0.0}
        
        for d in range(1, days + 1):
            day_log = {"Day": d, "Sources": [], "Sinks": [], "CoinsEarned": 0, "CoinsSpent": 0}
            
            day_base = daily_levels * avg_base_coin_per_lvl * avg_win_rate
            day_rv = day_base * cfg['rv_watch_rate'] * (cfg['rv_multiplier'] - 1)
            
            day_log["Sources"].append(f"Gameplay Base (from {daily_levels} levels played): +{int(day_base)} Coins")
            day_log["Sources"].append(f"Rewarded Video (RV): +{int(day_rv)} Coins")
            day_log["CoinsEarned"] += int(day_base) + int(day_rv)
            
            tot_base += day_base
            tot_rv += day_rv
            
            day_liveops = 0
            for event, e_cfg in LIVEOPS.items():
                if d % e_cfg['cadence'] == 0:
                    day_liveops += e_cfg['reward']
                    inv['Hammer'] += e_cfg['bst_hammer']
                    inv['Broom'] += e_cfg['bst_broom']
                    inv['Scissors'] += e_cfg['bst_scissors']
                    tot_bst_earned['Hammer'] += e_cfg['bst_hammer']
                    tot_bst_earned['Broom'] += e_cfg['bst_broom']
                    tot_bst_earned['Scissors'] += e_cfg['bst_scissors']
                    
                    bst_str = []
                    if e_cfg['bst_hammer'] > 0: bst_str.append(f"{e_cfg['bst_hammer']} Hammer")
                    if e_cfg['bst_broom'] > 0: bst_str.append(f"{e_cfg['bst_broom']} Broom")
                    if e_cfg['bst_scissors'] > 0: bst_str.append(f"{e_cfg['bst_scissors']} Scissors")
                    bst_txt = ", ".join(bst_str)
                    
                    day_log["Sources"].append(f"LiveOps {event}: +{e_cfg['reward']} Coins" + (f", +{bst_txt}" if bst_txt else ""))
            
            day_log["CoinsEarned"] += int(day_liveops)
            tot_liveops += day_liveops
            
            # Add today's needed boosters to the accumulator
            accum_needed['Revive'] += failed_levels_per_day * cfg['booster_buy_rate'] * 0.5
            accum_needed['Hammer'] += failed_levels_per_day * cfg['booster_buy_rate'] * 0.2
            accum_needed['Broom'] += failed_levels_per_day * cfg['booster_buy_rate'] * 0.2
            accum_needed['Scissors'] += failed_levels_per_day * cfg['booster_buy_rate'] * 0.1
            
            # Consume integer amounts from the accumulator
            use_r = int(accum_needed['Revive'])
            use_h = int(accum_needed['Hammer'])
            use_b = int(accum_needed['Broom'])
            use_s = int(accum_needed['Scissors'])
            
            accum_needed['Revive'] -= use_r
            accum_needed['Hammer'] -= use_h
            accum_needed['Broom'] -= use_b
            accum_needed['Scissors'] -= use_s
            
            # Process Revives (always bought)
            tot_bst_bought['Revive'] += use_r
            sink_revive = use_r * COST['Revive']
            if use_r > 0: day_log["Sinks"].append(f"Purchase {use_r} Revive: -{sink_revive} Coins")
            
            day_sink = sink_revive
            
            def process_booster(name, needed):
                global inv
                used_free = min(inv[name], needed)
                inv[name] -= used_free
                bought = needed - used_free
                cost = bought * COST[name]
                tot_bst_used_free[name] += used_free
                tot_bst_bought[name] += bought
                return used_free, bought, cost
                
            free_h, bought_h, cost_h = process_booster('Hammer', use_h)
            free_b, bought_b, cost_b = process_booster('Broom', use_b)
            free_s, bought_s, cost_s = process_booster('Scissors', use_s)
            
            if free_h > 0: day_log["Sinks"].append(f"Use {free_h} Free Hammer (from Inventory)")
            if bought_h > 0: day_log["Sinks"].append(f"Purchase {bought_h} Hammer: -{cost_h} Coins")
            if free_b > 0: day_log["Sinks"].append(f"Use {free_b} Free Broom (from Inventory)")
            if bought_b > 0: day_log["Sinks"].append(f"Purchase {bought_b} Broom: -{cost_b} Coins")
            if free_s > 0: day_log["Sinks"].append(f"Use {free_s} Free Scissors (from Inventory)")
            if bought_s > 0: day_log["Sinks"].append(f"Purchase {bought_s} Scissors: -{cost_s} Coins")
            
            day_sink += cost_h + cost_b + cost_s
            day_log["CoinsSpent"] += day_sink
            day_log["Inv"] = inv.copy()
            
            tot_sink += day_sink
            macro_log.append(day_log)

        tot_inflow = tot_base + tot_rv + tot_liveops
        net_accum = tot_inflow - tot_sink
        
        st.divider()
        st.header(f"Macro Results (After {days} Days)")
        
        st.subheader("1. Currency Overview (Coins)")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric(f"Total Inflow", f"{int(tot_inflow):,}", f"Avg: {int(tot_inflow/days):,}/day")
        c2.metric(f"Total Sinks", f"{int(tot_sink):,}", f"Avg: {int(tot_sink/days):,}/day", delta_color="inverse")
        c3.metric(f"Net Accumulated", f"{int(net_accum):,}", f"Avg: {int(net_accum/days):,}/day")
        c4.metric(f"Avg Win Rate", f"{avg_win_rate*100:.1f}%")
        
        st.subheader("2. Gameplay & Booster Summary")
        b1, b2, b3, b4 = st.columns(4)
        total_levels_played = daily_levels * days
        total_bst_used_overall = sum(tot_bst_used_free.values()) + sum(tot_bst_bought.values())
        b1.metric("Total Levels Played", f"{total_levels_played:,}")
        b2.metric("Total Boosters Used", f"{int(total_bst_used_overall):,}", "Free + Purchased")
        b3.metric("Free Boosters (Inv)", f"{inv['Hammer']}H | {inv['Broom']}B | {inv['Scissors']}S")
        b4.metric("Avg Fails / Day", f"{failed_levels_per_day:.1f}")
        
        st.divider()
        st.subheader("3. Resource Distribution")
        pc1, pc2 = st.columns(2)
        with pc1:
            fig_in = px.pie(names=["Gameplay Base", "Ads (RV)", "LiveOps"], values=[tot_base, tot_rv, tot_liveops], title="Inflows Breakdown", hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig_in, use_container_width=True)
        with pc2:
            fig_out = px.pie(
                names=["Purchase Revive", "Purchase Hammer", "Purchase Broom", "Purchase Scissors"],
                values=[tot_bst_bought['Revive']*COST['Revive'], tot_bst_bought['Hammer']*COST['Hammer'], tot_bst_bought['Broom']*COST['Broom'], tot_bst_bought['Scissors']*COST['Scissors']],
                title="Coin Sinks Breakdown", hole=0.4, color_discrete_sequence=px.colors.qualitative.Set2
            )
            st.plotly_chart(fig_out, use_container_width=True)

        with st.expander("📝 Show Daily Sources & Sinks Log"):
            log_text = ""
            for lg in macro_log:
                log_text += f"**Day {lg['Day']}:** (+{lg['CoinsEarned']} Coins | -{lg['CoinsSpent']} Coins | Inv: {lg['Inv']['Hammer']}H, {lg['Inv']['Broom']}B, {lg['Inv']['Scissors']}S)\n"
                log_text += "- **Sources:**\n"
                for src in lg['Sources']:
                    log_text += f"  - {src}\n"
                if not lg['Sources']: log_text += "  - None\n"
                
                log_text += "- **Sinks:**\n"
                for snk in lg['Sinks']:
                    log_text += f"  - {snk}\n"
                if not lg['Sinks']: log_text += "  - None\n"
                log_text += "\n"
            st.markdown(log_text)

# ==============================================================================
# TAB 2: MICRO ECONOMY (MONTE CARLO)
# ==============================================================================
with tabs[1]:
    if st.session_state.config is None:
        st.warning("⚠️ Please save configuration in Macro Economy tab first!")
    else:
        cfg = st.session_state.config
        st.header("Micro Journey (Monte Carlo Simulation)")
        
        num_players = st.number_input("Number of Simulated Players", 1, 5000, 1000)
            
        if st.button("🚀 Run Micro Simulation", type="primary"):
            with st.spinner("Simulating journeys..."):
                days = cfg['sim_days']
                daily_lvls = cfg['daily_levels']
                max_levels = days * daily_lvls
                PROGRESSION_CYCLE = ['N', 'N', 'H', 'N', 'N', 'H', 'N', 'N', 'SH']
                level_types = [PROGRESSION_CYCLE[i % 9] for i in range(max_levels)]
                
                balance_matrix = np.zeros((num_players, max_levels + 1))
                balance_matrix[:, 0] = 400
                
                p0_flat_log = []
                p0_inv = {'Hammer': 0, 'Broom': 0, 'Scissors': 0}
                p0_balance = 400
                
                for i in range(max_levels):
                    d = (i // daily_lvls) + 1
                    l_type = level_types[i]
                    if l_type == 'N': w_p = cfg['win_rate_n']; rwd = COIN_N
                    elif l_type == 'H': w_p = cfg['win_rate_h']; rwd = COIN_H
                    else: w_p = cfg['win_rate_sh']; rwd = COIN_SH
                        
                    win = random.random() < w_p
                    watch_rv = random.random() < cfg['rv_watch_rate']
                    use_b = (not win) and (random.random() < cfg['booster_buy_rate'])
                    
                    actual_rwd = (rwd * cfg['rv_multiplier']) if (win and watch_rv) else (rwd if win else 0)
                    
                    liveops_rwd = 0
                    added_bst = []
                    if i % daily_lvls == 0:
                        for event, e_cfg in LIVEOPS.items():
                            if d % e_cfg['cadence'] == 0:
                                liveops_rwd += e_cfg['reward']
                                if e_cfg['bst_hammer'] > 0: 
                                    p0_inv['Hammer'] += e_cfg['bst_hammer']
                                    added_bst.append(f"{e_cfg['bst_hammer']} Hammer")
                                if e_cfg['bst_broom'] > 0: 
                                    p0_inv['Broom'] += e_cfg['bst_broom']
                                    added_bst.append(f"{e_cfg['bst_broom']} Broom")
                                if e_cfg['bst_scissors'] > 0: 
                                    p0_inv['Scissors'] += e_cfg['bst_scissors']
                                    added_bst.append(f"{e_cfg['bst_scissors']} Scissors")
                    
                    p0_balance += liveops_rwd
                    
                    cost = 0
                    action_str = "Win"
                    src_str = f"Level ({rwd} Coins)" if win else ""
                    if win and watch_rv: src_str += f" + RV ({(actual_rwd - rwd):.0f} Coins)"
                    if liveops_rwd > 0: 
                        src_str += f" + Event ({liveops_rwd} Coins)"
                        if added_bst: src_str += f" & {', '.join(added_bst)}"
                        
                    if not win:
                        if use_b:
                            r = random.random()
                            if r < 0.5: bst_type = 'Revive'
                            elif r < 0.7: bst_type = 'Hammer'
                            elif r < 0.9: bst_type = 'Broom'
                            else: bst_type = 'Scissors'
                                
                            if bst_type != 'Revive' and p0_inv[bst_type] > 0:
                                p0_inv[bst_type] -= 1
                                action_str = f"Lose -> Use Free {bst_type}"
                            else:
                                cost = COST[bst_type]
                                action_str = f"Lose -> Buy {bst_type} (-{cost} Coins)"
                        else:
                            action_str = "Lose -> Give Up (Lose Heart)"
                            
                    p0_balance = max(0, p0_balance + actual_rwd - cost)
                    
                    # Update matrix for plotting
                    balance_matrix[:, i+1] = p0_balance # Simplified for visual plot matching P0
                    
                    p0_flat_log.append({
                        "Day": d, "Level": i+1, "Difficulty": l_type, "Action (Sink)": action_str,
                        "Source (Inflow)": src_str if src_str else "-",
                        "Inv (H/B/S)": f"{p0_inv['Hammer']}/{p0_inv['Broom']}/{p0_inv['Scissors']}",
                        "Net Coins": int(p0_balance)
                    })
                    
                st.subheader("🕵️‍♂️ Level-by-Level Log (Player #1)")
                st.dataframe(pd.DataFrame(p0_flat_log), use_container_width=True)

# ==============================================================================
# TAB 3: ECONOMY TUNING (ALL RESOURCES LIST)
# ==============================================================================
with tabs[2]:
    st.header("⚙️ Economy Tuning (LiveOps & Events)")
    
    st.subheader("1. Key Collection (7-Day Cadence)")
    st.markdown("Cơ chế: Người chơi thu thập Key khi vượt màn. Thu thập đủ sẽ mở khóa từng mốc phần thưởng.")
    st.dataframe(pd.DataFrame([
        {"Milestone": "Stages 1-4", "Rewards": "Infinite Hearts (15m-30m), 1-2 Boosters (Hammer/Broom)"},
        {"Milestone": "Stage 5", "Rewards": "100 Coins"},
        {"Milestone": "Stages 6-9", "Rewards": "Infinite Hearts (30m), 1-2 Boosters (Scissors)"},
        {"Milestone": "Stage 10", "Rewards": "200 Coins"},
        {"Milestone": "Stages 11-14", "Rewards": "Infinite Hearts (30m), 2 Boosters (Random)"},
        {"Milestone": "Stage 15", "Rewards": "300 Coins"},
        {"Milestone": "Stages 16-19", "Rewards": "Infinite Hearts (60m), 2-3 Boosters"},
        {"Milestone": "Stage 20", "Rewards": "400 Coins + 1 Hammer"},
        {"Milestone": "Stages 21-24", "Rewards": "Infinite Hearts (60m-2h), 2-3 Boosters"},
        {"Milestone": "Stage 25 (Complete)", "Rewards": "400 Coins + 1 Broom"},
        {"Milestone": "TOTAL COINS (Stage 5+10+15+20+25)", "Rewards": "1400 Coins"},
    ]), use_container_width=True)
    
    st.subheader("2. Win Streak (3-Day Cadence)")
    st.markdown("Cơ chế: Giữ chuỗi thắng liên tiếp để nhận thưởng trực tiếp vào ván chơi và mở khóa hòm phần thưởng.")
    st.dataframe(pd.DataFrame([
        {"Milestone": "Stage 1 (1 Win)", "Rewards": "1 Pre-level Booster (Bắt đầu màn với 1 Rocket/Bomb)"},
        {"Milestone": "Stage 2 (2 Wins)", "Rewards": "2 Pre-level Boosters"},
        {"Milestone": "Stage 3 (3 Wins)", "Rewards": "3 Pre-level Boosters + 50 Coins (Mở hòm nhỏ)"},
        {"Milestone": "Stage 6 (6 Wins)", "Rewards": "Max Pre-level Boosters + 120 Coins (Mở hòm vừa)"},
        {"Milestone": "Stage 9 (9 Wins)", "Rewards": "Max Pre-level Boosters + 250 Coins (Mở hòm lớn)"},
        {"Milestone": "TOTAL COINS", "Rewards": "420 Coins"},
    ]), use_container_width=True)
    
    st.subheader("3. Card Album (60-Day Cadence)")
    st.markdown("Cơ chế: Mở gói thẻ thu thập thẻ bài. Hoàn thành theo Set (Bộ) hoặc hoàn thành toàn bộ Album (Đại đa số nhận thẻ trùng).")
    st.dataframe(pd.DataFrame([
        {"Milestone": "Complete 1 Common Set (1-3 stars)", "Rewards": "150 - 400 Coins, 0-1 Random Booster"},
        {"Milestone": "Complete 1 Rare Set (4-5 stars)", "Rewards": "600 - 1000 Coins, 2 Boosters (Hammer, Scissors)"},
        {"Milestone": "ALBUM COMPLETION (100%)", "Rewards": "6250 Coins + 2 Hammer + 1 Broom + 2 Scissors"},
        {"Milestone": "Duplicates Convert", "Rewards": "Đổi thẻ trùng lặp ra Star chest (Nhận thêm một ít Coins & Thẻ mới)"},
    ]), use_container_width=True)
