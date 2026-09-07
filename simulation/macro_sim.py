import random
import pandas as pd
from config import DEFAULT_PRICES
from utils.parser import parse_rewards

def run_macro_simulation(cfg, tuning_cfg):
    days = cfg['sim_days']

    avg_base_coin_per_lvl = (20 * 6 + 40 * 2 + 60 * 1) / 9
    avg_win_rate = (cfg['win_rate_n'] * 6 + cfg['win_rate_h'] * 2 + cfg['win_rate_sh'] * 1) / 9
    
    
    prices_df = tuning_cfg.get('prices', pd.DataFrame(DEFAULT_PRICES))
    COST = dict(zip(prices_df['Item'], prices_df['Price']))
    avg_booster_cost = (COST.get('Revive', 190) * 0.5) + (COST.get('Hammer', 120) * 0.2) + (COST.get('Broom', 120) * 0.2) + (COST.get('Scissors', 120) * 0.1)
    
    tot_base, tot_rv, tot_liveops, tot_sink = 0, 0, 0, 0
    
    inv = {'Hammer': 0, 'Broom': 0, 'Scissors': 0}
    tot_bst_earned = {'Hammer': 0, 'Broom': 0, 'Scissors': 0}
    tot_bst_used_free = {'Revive': 0, 'Hammer': 0, 'Broom': 0, 'Scissors': 0}
    tot_bst_bought = {'Revive': 0, 'Hammer': 0, 'Broom': 0, 'Scissors': 0}
    
    macro_log = []
    accum_needed = {'Revive': 0.0, 'Hammer': 0.0, 'Broom': 0.0, 'Scissors': 0.0}
    current_coins = 400
    streak_wins = 0.0
    accum_fails = 0.0
    accum_keys = 0.0
    claimed_streak_reqs = set()
    claimed_key_reqs = set()
    
    for d in range(1, days + 1):
        if cfg.get('min_l', 2) == cfg.get('max_l', 2):
            daily_levels = cfg['daily_sessions'] * cfg.get('min_l', 2)
        else:
            daily_levels = sum(random.randint(cfg['min_l'], cfg['max_l']) for _ in range(cfg['daily_sessions']))
            
        failed_levels_per_day = daily_levels * (1 - avg_win_rate)
        
        day_log = {
            "Day": d, 
            "CoinsEarned": 0, "CoinsSpent": 0,
            "BoostersEarned": {'Hammer': 0, 'Broom': 0, 'Scissors': 0},
            "BoostersSpent": {'Hammer': 0, 'Broom': 0, 'Scissors': 0},
            "CoinLog": [], "BoosterLog": [], "EventLog": [],
            "LiveOpsCoins": 0, "KeysEarned": 0,
            "DailyKeys": 0, "DailyStreak": 0,
            "DayName": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][(d-1)%7],
            "KeyStage": 0, "StreakStage": 0
        }
        
        day_base = daily_levels * avg_base_coin_per_lvl * avg_win_rate
        day_rv = day_base * cfg['rv_watch_rate'] * (cfg['rv_multiplier'] - 1)
        
        day_log["CoinLog"].append(f"Gameplay Base (from {daily_levels} levels played): +{int(day_base)} Coins")
        day_log["CoinLog"].append(f"Rewarded Video (RV): +{int(day_rv)} Coins")
        day_log["CoinsEarned"] += int(day_base) + int(day_rv)
        current_coins += int(day_base) + int(day_rv)
        
        tot_base += day_base
        tot_rv += day_rv
        
        day_liveops = 0
        # Key Collection
        k_df = tuning_cfg['key_stages']
        max_keys_cap = k_df['KeysReq'].max() if not k_df.empty else 304
        
        if (d - 1) % 7 == 0:
            accum_keys = 0.0
            claimed_key_reqs = set()
            
            
        if d % 7 in [1, 2, 3, 4]:
            daily_keys_potential = daily_levels * avg_win_rate * 5
            prev_keys = accum_keys
            accum_keys = min(max_keys_cap, accum_keys + daily_keys_potential)
            actual_daily_keys = accum_keys - prev_keys
            
            if actual_daily_keys == 0 and accum_keys >= max_keys_cap:
                keys_event_str = f"Keys Collection: Capped at {int(max_keys_cap)} Keys"
            elif actual_daily_keys > 0:
                keys_event_str = f"Keys Collection: +{int(actual_daily_keys)} Keys"
            else:
                keys_event_str = "" 
        else:
            actual_daily_keys = 0.0
            
        day_log["DailyKeys"] = int(actual_daily_keys)
        day_log["LevelsPlayed"] = daily_levels
        day_log["KeyStage"] = len(claimed_key_reqs)
        
        k_df = tuning_cfg['key_stages']
        c, h, b, s = 0, 0, 0, 0
        stages_reached = 0
        
        for req, rew_str in zip(k_df['KeysReq'], k_df['Reward']):
            if prev_keys < req and accum_keys >= req and req not in claimed_key_reqs:
                claimed_key_reqs.add(req)
                stages_reached += 1
                _c, _h, _b, _s = parse_rewards(rew_str)
                c+=_c; h+=_h; b+=_b; s+=_s
                
        if stages_reached > 0:
            day_liveops += c
            inv['Hammer'] += h; inv['Broom'] += b; inv['Scissors'] += s
            tot_bst_earned['Hammer'] += h; tot_bst_earned['Broom'] += b; tot_bst_earned['Scissors'] += s
            
            if c > 0: day_log["CoinLog"].append(f"Key Collection ({stages_reached} stages): +{int(c)} Coins")
            if h>0 or b>0 or s>0:
                bst_parts = []
                if h > 0: bst_parts.append(f"+{int(h)} Hammer")
                if b > 0: bst_parts.append(f"+{int(b)} Broom")
                if s > 0: bst_parts.append(f"+{int(s)} Scissors")
                day_log["BoosterLog"].append(f"Key Collection: {', '.join(bst_parts)}")
                
        if d % 7 in [1, 2, 3, 4] and keys_event_str:
            if stages_reached > 0:
                day_log["EventLog"].append(f"{keys_event_str} | Hit {stages_reached} Key Milestone(s)!")
            else:
                day_log["EventLog"].append(keys_event_str)
            day_log["BoostersEarned"]['Hammer'] += h
            day_log["BoostersEarned"]['Broom'] += b
            day_log["BoostersEarned"]['Scissors'] += s

        # Win Streak (Fri-Sun only)
        if d % 7 == 5:
            streak_wins = 0.0
            accum_fails = 0.0
            claimed_streak_reqs = set()
            
            
        s_df = tuning_cfg['streak_stages']
        max_streak_cap = s_df['WinsReq'].max() if not s_df.empty else 36
        max_streak_today = streak_wins
        day_liveops_streak = 0
        
        if d % 7 in [5, 6, 0]:
            for _ in range(daily_levels):
                prev_streak = streak_wins
                accum_fails += (1 - avg_win_rate)
                streak_wins = min(max_streak_cap, streak_wins + avg_win_rate)
                
                if streak_wins > max_streak_today:
                    max_streak_today = streak_wins
                    
                for req in s_df['WinsReq']:
                    if prev_streak < req and streak_wins >= req and req not in claimed_streak_reqs:
                        claimed_streak_reqs.add(req)
                        rew_str = s_df[s_df['WinsReq'] == req]['Reward'].values[0]
                        _c, _h, _b, _s = parse_rewards(rew_str)
                        day_liveops_streak += _c
                        if _c > 0: day_log["CoinLog"].append(f"Win Streak (Stage {req}): +{int(_c)} Coins")
                        inv['Hammer'] += _h; inv['Broom'] += _b; inv['Scissors'] += _s
                        if _h>0 or _b>0 or _s>0:
                            bst_parts = []
                            if _h > 0: bst_parts.append(f"+{int(_h)} Hammer")
                            if _b > 0: bst_parts.append(f"+{int(_b)} Broom")
                            if _s > 0: bst_parts.append(f"+{int(_s)} Scissors")
                            day_log["BoosterLog"].append(f"Win Streak (Stage {req}): {', '.join(bst_parts)}")
                        tot_bst_earned['Hammer'] += _h; tot_bst_earned['Broom'] += _b; tot_bst_earned['Scissors'] += _s
                        day_log["BoostersEarned"]['Hammer'] += _h
                        day_log["BoostersEarned"]['Broom'] += _b
                        day_log["BoostersEarned"]['Scissors'] += _s
                
                if accum_fails >= 1.0:
                    accum_fails -= 1.0
                    streak_wins = 0.0
            day_log["EventLog"].append(f"Win Streak: Max Streak {int(max_streak_today)}/{int(max_streak_cap)} Wins")
            day_log["StreakStage"] = len(claimed_streak_reqs)
        else:
            streak_wins = 0.0
            accum_fails = 0.0
            max_streak_today = 0.0
        day_log["DailyStreak"] = int(max_streak_today)
        if day_liveops_streak > 0:
            day_log["CoinLog"].append(f"LiveOps Streak: +{int(day_liveops_streak)} Coins")
            day_liveops += day_liveops_streak
        
        day_log["CoinsEarned"] += int(day_liveops)
        day_log["CoinsEarned"] += int(day_liveops_streak)
        current_coins += int(day_liveops_streak)
        current_coins += int(day_liveops)
        day_log["LiveOpsCoins"] = int(day_liveops)
        tot_liveops += day_liveops + day_liveops_streak
        
        def process_booster(name, weight):
            nonlocal current_coins
            situations = failed_levels_per_day * weight
            willing_to_use_free = situations * cfg.get('booster_use_rate', 0.5)
            
            accum_needed[f"{name}_free"] = accum_needed.get(f"{name}_free", 0) + willing_to_use_free
            use_free = int(accum_needed[f"{name}_free"])
            use_free = min(inv.get(name, 0), use_free)
            
            if use_free > 0:
                accum_needed[f"{name}_free"] -= use_free
                if name in inv: inv[name] -= use_free
            
            remaining_situations = situations - willing_to_use_free
            willing_to_buy = remaining_situations * (cfg.get('revive_buy_rate', 0.02) if name == 'Revive' else cfg.get('booster_buy_rate', 0.1))
            
            accum_needed[f"{name}_buy"] = accum_needed.get(f"{name}_buy", 0) + willing_to_buy
            wanted_to_buy = int(accum_needed[f"{name}_buy"])
            
            bought = 0
            cost = 0
            if wanted_to_buy > 0:
                unit_cost = COST.get(name, 120)
                affordable = int(current_coins / unit_cost)
                bought = min(wanted_to_buy, affordable)
                
                cost = bought * unit_cost
                current_coins -= cost
                
                if bought > 0:
                    accum_needed[f"{name}_buy"] -= bought
                    
                if wanted_to_buy > affordable:
                    accum_needed[f"{name}_buy"] = 0
                
            tot_bst_used_free[name] += use_free
            tot_bst_bought[name] += bought
            return use_free, bought, cost

        free_r, bought_r, cost_r = process_booster('Revive', 0.5)
        free_h, bought_h, cost_h = process_booster('Hammer', 0.2)
        free_b, bought_b, cost_b = process_booster('Broom', 0.2)
        free_s, bought_s, cost_s = process_booster('Scissors', 0.1)
        
        sink_revive = int(cost_r)
        if bought_r > 0: day_log["CoinLog"].append(f"Purchase {bought_r} Revive: -{int(cost_r)} Coins")
        day_sink = sink_revive
        
        if free_h > 0: 
            day_log["BoosterLog"].append(f"Use {free_h} Free Hammer (from Inv)")
            day_log["BoostersSpent"]['Hammer'] += free_h
        if bought_h > 0: 
            day_log["CoinLog"].append(f"Purchase {bought_h} Hammer: -{int(cost_h)} Coins")
            day_log["BoosterLog"].append(f"Use {bought_h} Bought Hammer")
            day_log["BoostersSpent"]['Hammer'] += bought_h
            
        if free_b > 0: 
            day_log["BoosterLog"].append(f"Use {free_b} Free Broom (from Inv)")
            day_log["BoostersSpent"]['Broom'] += free_b
        if bought_b > 0: 
            day_log["CoinLog"].append(f"Purchase {bought_b} Broom: -{int(cost_b)} Coins")
            day_log["BoosterLog"].append(f"Use {bought_b} Bought Broom")
            day_log["BoostersSpent"]['Broom'] += bought_b
            
        if free_s > 0: 
            day_log["BoosterLog"].append(f"Use {free_s} Free Scissors (from Inv)")
            day_log["BoostersSpent"]['Scissors'] += free_s
        if bought_s > 0: 
            day_log["CoinLog"].append(f"Purchase {bought_s} Scissors: -{int(cost_s)} Coins")
            day_log["BoosterLog"].append(f"Use {bought_s} Bought Scissors")
            day_log["BoostersSpent"]['Scissors'] += bought_s
        
        day_sink += int(cost_h) + int(cost_b) + int(cost_s)
        day_log["CoinsSpent"] += day_sink
        day_log["Inv"] = inv.copy()
        day_log["CumulativeCoins"] = current_coins
        
        tot_sink += day_sink
        macro_log.append(day_log)

    tot_inflow = tot_base + tot_rv + tot_liveops
    net_accum = tot_inflow - tot_sink
    total_bst_used_overall = sum(tot_bst_used_free.values()) + sum(tot_bst_bought.values())
    
    return {
        'days': days,
        'daily_levels': daily_levels,
        'tot_inflow': tot_inflow,
        'tot_sink': tot_sink,
        'net_accum': net_accum,
        'avg_win_rate': avg_win_rate,
        'total_levels_played': sum(lg['LevelsPlayed'] for lg in macro_log),
        'total_bst_used_overall': total_bst_used_overall,
        'failed_levels_per_day': (sum(lg['LevelsPlayed'] for lg in macro_log) * (1 - avg_win_rate)) / days,
        'final_inv': inv,
        'tot_base': tot_base,
        'tot_rv': tot_rv,
        'tot_liveops': tot_liveops,
        'tot_bst_bought': tot_bst_bought,
        'macro_log': macro_log
    }
