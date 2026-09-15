import pandas as pd
import numpy as np
import random
from config import COIN_N, COIN_H, COIN_SH, DEFAULT_PRICES, get_streak_floor
from utils.parser import parse_rewards

def run_monte_carlo_simulation(cfg, t_cfg, num_players):
    enable_keys = cfg.get('enable_keys', True)
    enable_streak = cfg.get('enable_streak', True)
    enable_mp = cfg.get('enable_mp', True)
    mp_tier = cfg.get('mp_tier', 'Free')
    days = cfg['sim_days']
    prices_df = t_cfg.get('prices', pd.DataFrame(DEFAULT_PRICES))
    COST = dict(zip(prices_df['Item'], prices_df['Price']))
    daily_lvls_seq = []
    for _ in range(days):
        if cfg.get('min_l', 2) == cfg.get('max_l', 2):
            daily_lvls_seq.append(cfg['daily_sessions'] * cfg.get('min_l', 2))
        else:
            daily_lvls_seq.append(sum(random.randint(cfg['min_l'], cfg['max_l']) for _ in range(cfg['daily_sessions'])))
            
    max_levels = sum(daily_lvls_seq)
    
    level_to_day = np.zeros(max_levels, dtype=int)
    is_start_of_day = np.zeros(max_levels, dtype=bool)
    
    idx = 0
    for day_idx, d_lvls in enumerate(daily_lvls_seq):
        d = day_idx + 1
        if d_lvls > 0:
            is_start_of_day[idx] = True
            level_to_day[idx : idx + d_lvls] = d
            idx += d_lvls
            
    PROGRESSION_CYCLE = ['N', 'N', 'H', 'N', 'N', 'H', 'N', 'N', 'SH']
    level_types = [PROGRESSION_CYCLE[i % 9] for i in range(max_levels)]
    
    balance_matrix = np.zeros((num_players, max_levels + 1))
    balance_matrix[:, 0] = 400
    
    p0_flat_log = []
    
    # We will simulate all players. 
    # For performance, this can be vectorized, but we'll stick to a simple loop for now
    for p in range(num_players):
        p_inv = {'Hammer': 0, 'Broom': 0, 'Scissors': 0}
        p_balance = 400
        keys_collected = 0
        streak_wins = 0
        
        for i in range(max_levels):
            d = level_to_day[i]
            l_type = level_types[i]
            if l_type == 'N': w_p = cfg['win_rate_n']; rwd = COIN_N
            elif l_type == 'H': w_p = cfg['win_rate_h']; rwd = COIN_H
            else: w_p = cfg['win_rate_sh']; rwd = COIN_SH
                
            win = random.random() < w_p
            watch_rv = random.random() < cfg['rv_watch_rate']
            
            actual_rwd = (rwd * cfg['rv_multiplier']) if (win and watch_rv) else (rwd if win else 0)
            
            liveops_rwd = 0
            added_bst = []
            
            # Reset trackers based on cadence at start of day
            if is_start_of_day[i]:
                if (d - 1) % 7 == 0: 
                    keys_collected = 0
                if d % 7 == 5:
                    streak_wins = 0
                    max_streak_in_cadence = 0
                if enable_mp and (d - 1) % 30 == 0:
                    if d > 1 and mp_bank > 0:
                        liveops_rwd += mp_bank
                        added_bst.append(f"MP Bank (+{mp_bank} Coins)")
                    mp_tokens = 0
                    mp_bank = 0
                    # Grant Stage 0 immediately
                    mp_df = t_cfg.get('master_pass_stages', pd.DataFrame())
                    if not mp_df.empty:
                        stage0 = mp_df[mp_df['TokensReq'] == 0]
                        if not stage0.empty:
                            for _, r_row in stage0.iterrows():
                                c, h, b, s = parse_rewards(r_row['Reward'])
                                if mp_tier == 'Premium' and 'PremiumReward' in r_row:
                                    _pc, _ph, _pb, _ps = parse_rewards(r_row['PremiumReward'])
                                    c += _pc; h += _ph; b += _pb; s += _ps
                                liveops_rwd += c
                                p_inv['Hammer'] += h; p_inv['Broom'] += b; p_inv['Scissors'] += s
                                if h>0: added_bst.append(f"{h}H")
                                if b>0: added_bst.append(f"{b}B")
                                if s>0: added_bst.append(f"{s}S")
                                if c>0 or h>0 or b>0 or s>0:
                                    added_bst.append(f"MP [{mp_tier}] Stage 0")
                
            if win:
                d_current = d
                if enable_keys and (d_current % 7 in [1, 2, 3, 4]):
                    k_df = t_cfg['key_stages']
                    max_keys_cap = k_df['KeysReq'].max() if not k_df.empty else 304
                    
                    prev_keys = keys_collected
                    keys_collected = min(max_keys_cap, keys_collected + 5)
                    
                    k_match = k_df[(k_df['KeysReq'] > prev_keys) & (k_df['KeysReq'] <= keys_collected)]
                    if not k_match.empty:
                        for rew_str in k_match['Reward'].tolist():
                            c, h, b, s = parse_rewards(rew_str)
                            liveops_rwd += c
                            p_inv['Hammer'] += h; p_inv['Broom'] += b; p_inv['Scissors'] += s
                            if h>0: added_bst.append(f"{h}H")
                            if b>0: added_bst.append(f"{b}B")
                            if s>0: added_bst.append(f"{s}S")
                            if c>0 or h>0 or b>0 or s>0:
                                added_bst.append("Key Milestone!")
                
                # Master Pass
                if enable_mp:
                    mp_df = t_cfg.get('master_pass_stages', pd.DataFrame())
                    mp_max_stage_tokens = mp_df['TokensReq'].max() if not mp_df.empty else 150
                    prev_tokens = mp_tokens
                    tokens_earned = 1 if l_type == 'N' else (2 if l_type == 'H' else 3)
                    if mp_tier != 'Premium':
                        mp_tokens = min(float(mp_max_stage_tokens), mp_tokens + tokens_earned)
                    else:
                        mp_tokens += tokens_earned
                    
                    if not mp_df.empty:
                        mp_match = mp_df[(mp_df['TokensReq'] > prev_tokens) & (mp_df['TokensReq'] <= mp_tokens)]
                        if not mp_match.empty:
                            for _, r_row in mp_match.iterrows():
                                c, h, b, s = parse_rewards(r_row['Reward'])
                                if mp_tier == 'Premium' and 'PremiumReward' in r_row:
                                    _pc, _ph, _pb, _ps = parse_rewards(r_row['PremiumReward'])
                                    c += _pc; h += _ph; b += _pb; s += _ps
                                liveops_rwd += c
                                p_inv['Hammer'] += h; p_inv['Broom'] += b; p_inv['Scissors'] += s
                                if h>0: added_bst.append(f"{h}H")
                                if b>0: added_bst.append(f"{b}B")
                                if s>0: added_bst.append(f"{s}S")
                                if c>0 or h>0 or b>0 or s>0:
                                    added_bst.append("MP Milestone!")
                    if mp_tier == 'Premium' and mp_tokens > mp_max_stage_tokens:
                        prev_overflow = max(0, prev_tokens - mp_max_stage_tokens)
                        curr_overflow = mp_tokens - mp_max_stage_tokens
                        if int(curr_overflow / 10) > int(prev_overflow / 10):
                            added_bank = (int(curr_overflow / 10) - int(prev_overflow / 10)) * 150
                            mp_bank = min(3000, mp_bank + added_bank)
                            added_bst.append("MP Bank Updated")
                
                d_current = d
                if enable_streak and (d_current % 7 in [5, 6, 0]):
                    s_df = t_cfg['streak_stages']
                    max_streak_cap = s_df['WinsReq'].max() if not s_df.empty else 36
                    streak_wins = min(max_streak_cap, streak_wins + 1)
                    if streak_wins > max_streak_in_cadence:
                        s_df = t_cfg['streak_stages']
                        s_match = s_df[s_df['WinsReq'] == streak_wins]
                        if not s_match.empty:
                            c, h, b, s = parse_rewards(s_match['Reward'].values[0])
                            liveops_rwd += c
                            p_inv['Hammer'] += h; p_inv['Broom'] += b; p_inv['Scissors'] += s
                            if h>0: added_bst.append(f"{h}H")
                            if b>0: added_bst.append(f"{b}B")
                            if s>0: added_bst.append(f"{s}S")
                            if c>0 or h>0 or b>0 or s>0: added_bst.append("Streak Milestone!")
                        max_streak_in_cadence = streak_wins
                else:
                    streak_wins = 0
            else:
                d_current = d
                if enable_streak and (d_current % 7 in [5, 6, 0]):
                    s_df = t_cfg.get('streak_stages', pd.DataFrame())
                    streak_wins = int(get_streak_floor(streak_wins, s_df))
                else:
                    streak_wins = 0
            
            p_balance += liveops_rwd
            
            cost = 0
            action_str = ""
            src_str = f"Level ({rwd} Coins)" if win else ""
            if win and watch_rv: src_str += f" + RV ({(actual_rwd - rwd):.0f} Coins)"
            if liveops_rwd > 0: 
                src_str += f" + Event ({liveops_rwd} Coins)"
                if added_bst: src_str += f" & {', '.join(added_bst)}"
                
            if random.random() < cfg.get('booster_use_rate', 0.5):
                owned = [b for b in ['Hammer', 'Broom', 'Scissors'] if p_inv[b] > 0]
                if owned:
                    b_used = random.choice(owned)
                    p_inv[b_used] -= 1
                    action_str = f"Use {b_used} -> "
            
            if not win:
                buy_rate = cfg.get('revive_buy_rate', 0.10)
                if random.random() < buy_rate:
                    cost = COST.get('Revive', 380)
                    if p_balance >= cost:
                        action_str += f"Lose -> Buy Revive (-{cost} Coins)"
                    else:
                        cost = 0
                        action_str += "Lose -> Give Up (Not Enough Coins)"
                else:
                    action_str += "Lose -> Give Up (Save Coins / Watch Ads)"
            else:
                action_str += "Win"  
                    
            p_balance = max(0, p_balance + actual_rwd - cost)
            balance_matrix[p, i+1] = p_balance
            
            # Log only for Player 0
            if p == 0:
                p0_flat_log.append({
                    "Day": d, "Level": i+1, "Difficulty": l_type, "Action (Sink)": action_str,
                    "Source (Inflow)": src_str if src_str else "-",
                    "Inv (H/B/S)": f"{p_inv['Hammer']}/{p_inv['Broom']}/{p_inv['Scissors']}",
                    "Net Coins": int(p_balance)
                })
                
    return balance_matrix, p0_flat_log, max_levels
