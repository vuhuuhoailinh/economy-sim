import random
import pandas as pd
from config import DEFAULT_PRICES
from utils.parser import parse_rewards

def run_deterministic_simulation(cfg, tuning_cfg):
    days = cfg['sim_days']

    avg_base_coin_per_lvl = (20 * 6 + 40 * 2 + 60 * 1) / 9
    avg_win_rate = (cfg['win_rate_n'] * 6 + cfg['win_rate_h'] * 2 + cfg['win_rate_sh'] * 1) / 9
    
    
    prices_df = tuning_cfg.get('prices', pd.DataFrame(DEFAULT_PRICES))
    COST = dict(zip(prices_df['Item'], prices_df['Price']))
    avg_booster_cost = (COST.get('Revive', 190) * 0.5) + (COST.get('Hammer', 120) * 0.2) + (COST.get('Broom', 120) * 0.2) + (COST.get('Scissors', 120) * 0.1)
    
    tot_base, tot_rv, tot_liveops, tot_sink = 0, 0, 0, 0
    tot_liveops_keys, tot_liveops_streak, tot_liveops_mp = 0, 0, 0
    
    inv = {'Hammer': 0, 'Broom': 0, 'Scissors': 0}
    tot_bst_earned = {'Hammer': 0, 'Broom': 0, 'Scissors': 0}
    tot_bst_earned_keys = {'Hammer': 0, 'Broom': 0, 'Scissors': 0}
    tot_bst_earned_streak = {'Hammer': 0, 'Broom': 0, 'Scissors': 0}
    tot_bst_earned_mp = {'Hammer': 0, 'Broom': 0, 'Scissors': 0}
    master_pass_tokens = 0.0
    master_pass_bonus_bank = 0.0
    claimed_master_pass_reqs = set()
    tot_bst_used = {'Hammer': 0, 'Broom': 0, 'Scissors': 0}
    tot_revives_bought = 0
    
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
        won_levels = int(round(daily_levels * avg_win_rate))
        lost_levels = int(daily_levels - won_levels)
        
        day_log = {
            "Day": d, 
            "CoinsEarned": 0, "CoinsSpent": 0,
            "LevelsPlayed": daily_levels,
            "LevelsWon": won_levels,
            "LevelsLost": lost_levels,
            "BoostersEarned": {'Hammer': 0, 'Broom': 0, 'Scissors': 0},
            "BoostersSpent": {'Hammer': 0, 'Broom': 0, 'Scissors': 0},
            "CoinLog": [], "BoosterLog": [], "EventLog": [],
            "LiveOpsCoins": 0, "KeysEarned": 0,
            "DailyKeys": 0, "DailyStreak": 0, "DailyMPTokens": 0,
            "DayName": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][(d-1)%7],
            "KeyStage": 0, "StreakStage": 0,
            "MPStage": 0, "MPTokens": 0, "MPTier": cfg.get('mp_tier', 'Free') if cfg.get('enable_mp', True) else "Off"
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
        # Master Pass
        enable_mp = cfg.get('enable_mp', True)
        mp_tier = cfg.get('mp_tier', 'Free')
        avg_tokens_per_lvl = (cfg['win_rate_n'] * 6 * 1 + cfg['win_rate_h'] * 2 * 2 + cfg['win_rate_sh'] * 1 * 3) / 9
        daily_tokens = (daily_levels * avg_tokens_per_lvl) if enable_mp else 0.0
        mp_df = tuning_cfg.get('master_pass_stages', pd.DataFrame())
        max_mp_stage = mp_df['TokensReq'].max() if not mp_df.empty else 150

        free_c, free_h, free_b, free_s = 0, 0, 0, 0
        prem_c, prem_h, prem_b, prem_s = 0, 0, 0, 0
        mp_stages_reached = 0
        reached_stage_info = []

        if enable_mp:
            if (d - 1) % 30 == 0:
                master_pass_tokens = 0.0
                master_pass_bonus_bank = 0.0
                claimed_master_pass_reqs = set()
                day_log["EventLog"].append(f"Master Pass [{mp_tier}] Started (30-day Cycle)!")

            prev_mp_tokens = master_pass_tokens
            master_pass_tokens += daily_tokens
            day_log["DailyMPTokens"] = int(daily_tokens)

            if not mp_df.empty:
                for idx, row in mp_df.iterrows():
                    req = row['TokensReq']
                    stg = row['Stage']
                    rew_str = row['Reward']
                    prem_rew_str = row.get('PremiumReward', '')
                    if ((prev_mp_tokens < req and master_pass_tokens >= req) or (req == 0 and master_pass_tokens >= 0)) and req not in claimed_master_pass_reqs:
                        claimed_master_pass_reqs.add(req)
                        mp_stages_reached += 1
                        _fc, _fh, _fb, _fs = parse_rewards(rew_str)
                        free_c += _fc; free_h += _fh; free_b += _fb; free_s += _fs
                        
                        _pc, _ph, _pb, _ps = 0, 0, 0, 0
                        if mp_tier == 'Premium' and prem_rew_str:
                            _pc, _ph, _pb, _ps = parse_rewards(prem_rew_str)
                            prem_c += _pc; prem_h += _ph; prem_b += _pb; prem_s += _ps
                        
                        reached_stage_info.append({
                            'stage': stg,
                            'free_reward': rew_str,
                            'prem_reward': prem_rew_str if mp_tier == 'Premium' else None
                        })

            if master_pass_tokens > max_mp_stage:
                prev_overflow = max(0, prev_mp_tokens - max_mp_stage)
                curr_overflow = master_pass_tokens - max_mp_stage
                chunks_today = int(curr_overflow / 10) - int(prev_overflow / 10)
                if chunks_today > 0:
                    added_bank = chunks_today * 150
                    master_pass_bonus_bank = min(3000, master_pass_bonus_bank + added_bank)

            if d % 30 == 0 and master_pass_bonus_bank > 0:
                day_log["CoinLog"].append(f"Master Pass End: +{int(master_pass_bonus_bank)} Coins (Bonus Bank)")
                day_liveops += master_pass_bonus_bank
                tot_liveops_mp += master_pass_bonus_bank
        else:
            day_log["DailyMPTokens"] = 0

        c = free_c + prem_c
        h = free_h + prem_h
        b = free_b + prem_b
        s = free_s + prem_s

        current_mp_stage = max((int(row['Stage']) for idx, row in mp_df.iterrows() if row['TokensReq'] in claimed_master_pass_reqs), default=0) if enable_mp else 0
        day_log["MPStage"] = current_mp_stage
        day_log["MPTokens"] = int(master_pass_tokens)
        day_log["MPTier"] = mp_tier if enable_mp else "Off"

        if mp_stages_reached > 0:
            day_liveops += c
            tot_liveops_mp += c

            inv['Hammer'] += h; inv['Broom'] += b; inv['Scissors'] += s
            tot_bst_earned['Hammer'] += h; tot_bst_earned['Broom'] += b; tot_bst_earned['Scissors'] += s
            tot_bst_earned_mp['Hammer'] += h; tot_bst_earned_mp['Broom'] += b; tot_bst_earned_mp['Scissors'] += s

            if free_c > 0:
                day_log["CoinLog"].append(f"Master Pass [Free]: +{int(free_c)} Coins")
            if prem_c > 0:
                day_log["CoinLog"].append(f"Master Pass [Premium]: +{int(prem_c)} Coins")

            def _fmt_bst(hh, bb, ss):
                parts = []
                if hh > 0: parts.append(f"+{int(hh)} Hammer")
                if bb > 0: parts.append(f"+{int(bb)} Broom")
                if ss > 0: parts.append(f"+{int(ss)} Scissors")
                return ", ".join(parts)

            f_bst_str = _fmt_bst(free_h, free_b, free_s)
            p_bst_str = _fmt_bst(prem_h, prem_b, prem_s)
            if f_bst_str:
                day_log["BoosterLog"].append(f"Master Pass [Free]: {f_bst_str}")
            if p_bst_str:
                day_log["BoosterLog"].append(f"Master Pass [Premium]: {p_bst_str}")

            for stg_info in reached_stage_info:
                stg = stg_info['stage']
                r_free = stg_info['free_reward']
                r_prem = stg_info['prem_reward']
                if r_prem:
                    day_log["EventLog"].append(f"Master Pass Stage {stg} Unlocked: Free: [{r_free}] | Premium: [{r_prem}]")
                else:
                    day_log["EventLog"].append(f"Master Pass Stage {stg} Unlocked: Free: [{r_free}]")

            day_log["EventLog"].append(f"Master Pass [{mp_tier}]: +{int(daily_tokens)} Tokens (Total: {int(master_pass_tokens)}) | Hit {mp_stages_reached} Stage(s)")
            day_log["BoostersEarned"]['Hammer'] += h
            day_log["BoostersEarned"]['Broom'] += b
            day_log["BoostersEarned"]['Scissors'] += s
        else:
            if daily_tokens > 0:
                day_log["EventLog"].append(f"Master Pass [{mp_tier}]: +{int(daily_tokens)} Tokens (Total: {int(master_pass_tokens)})")

        
# Key Collection
        k_df = tuning_cfg['key_stages']
        max_keys_cap = k_df['KeysReq'].max() if not k_df.empty else 304
        
        if (d - 1) % 7 == 0:
            accum_keys = 0.0
            claimed_key_reqs = set()
            
            
        enable_keys = cfg.get('enable_keys', True)
        keys_event_str = ""
        if enable_keys and d % 7 in [1, 2, 3, 4]:
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
        
        if enable_keys:
            for req, rew_str in zip(k_df['KeysReq'], k_df['Reward']):
                if prev_keys < req and accum_keys >= req and req not in claimed_key_reqs:
                    claimed_key_reqs.add(req)
                    stages_reached += 1
                    _c, _h, _b, _s = parse_rewards(rew_str)
                    c+=_c; h+=_h; b+=_b; s+=_s
                
        if stages_reached > 0:
            day_liveops += c
            tot_liveops_keys += c
            inv['Hammer'] += h; inv['Broom'] += b; inv['Scissors'] += s
            tot_bst_earned['Hammer'] += h; tot_bst_earned['Broom'] += b; tot_bst_earned['Scissors'] += s
            tot_bst_earned_keys['Hammer'] += h; tot_bst_earned_keys['Broom'] += b; tot_bst_earned_keys['Scissors'] += s
            
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
        
        enable_streak = cfg.get('enable_streak', True)
        if enable_streak and d % 7 in [5, 6, 0]:
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
                        tot_liveops_streak += _c
                        if _c > 0: day_log["CoinLog"].append(f"Win Streak (Stage {req}): +{int(_c)} Coins")
                        inv['Hammer'] += _h; inv['Broom'] += _b; inv['Scissors'] += _s
                        if _h>0 or _b>0 or _s>0:
                            bst_parts = []
                            if _h > 0: bst_parts.append(f"+{int(_h)} Hammer")
                            if _b > 0: bst_parts.append(f"+{int(_b)} Broom")
                            if _s > 0: bst_parts.append(f"+{int(_s)} Scissors")
                            day_log["BoosterLog"].append(f"Win Streak (Stage {req}): {', '.join(bst_parts)}")
                        tot_bst_earned['Hammer'] += _h; tot_bst_earned['Broom'] += _b; tot_bst_earned['Scissors'] += _s
                        tot_bst_earned_streak['Hammer'] += _h; tot_bst_earned_streak['Broom'] += _b; tot_bst_earned_streak['Scissors'] += _s
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
        current_coins += int(day_liveops)
        day_log["LiveOpsCoins"] = int(day_liveops)
        tot_liveops += day_liveops
        
        def process_revive():
            nonlocal current_coins
            bought = 0
            cost = 0
            
            situations = failed_levels_per_day
            willing_to_buy = situations * cfg.get('revive_buy_rate', 0.1)
            accum_needed["Revive_buy"] = accum_needed.get("Revive_buy", 0) + willing_to_buy
            wanted_to_buy = int(accum_needed["Revive_buy"])
            if wanted_to_buy > 0:
                unit_cost = COST.get("Revive", 380)
                affordable = int(current_coins / unit_cost)
                bought = min(wanted_to_buy, affordable)
                cost = bought * unit_cost
                current_coins -= cost
                if bought > 0:
                    accum_needed["Revive_buy"] -= bought
                if wanted_to_buy > affordable:
                    accum_needed["Revive_buy"] = 0
            return bought, cost

        # Call Revive
        bought_r, cost_r = process_revive()
        free_r = 0 # Not used

        # Process Boosters Randomly 1 out of 3
        uses_total = daily_levels * cfg.get('booster_use_rate', 0.5)
        accum_needed['bst_free'] = accum_needed.get('bst_free', 0) + uses_total
        target_uses = int(accum_needed['bst_free'])
        
        used_h, used_b, used_s = 0, 0, 0
        while target_uses > 0 and (inv['Hammer'] > 0 or inv['Broom'] > 0 or inv['Scissors'] > 0):
            available = [k for k in ['Hammer', 'Broom', 'Scissors'] if inv[k] > 0]
            if not available:
                break
            chosen = random.choice(available)
            inv[chosen] -= 1
            if chosen == 'Hammer':
                used_h += 1
            elif chosen == 'Broom':
                used_b += 1
            elif chosen == 'Scissors':
                used_s += 1
            target_uses -= 1
                
        accum_needed['bst_free'] -= (used_h + used_b + used_s)
        
        free_h, bought_h, cost_h = used_h, 0, 0
        free_b, bought_b, cost_b = used_b, 0, 0
        free_s, bought_s, cost_s = used_s, 0, 0
        
        sink_revive = int(cost_r)
        if bought_r > 0: 
            day_log["CoinLog"].append(f"Purchase {bought_r} Revive: -{int(cost_r)} Coins")
            tot_revives_bought += bought_r
        day_sink = sink_revive
        
        if free_h > 0: 
            day_log["BoosterLog"].append(f"Use {free_h} Hammer (from Inv)")
            day_log["BoostersSpent"]['Hammer'] += free_h
            tot_bst_used['Hammer'] += free_h
            
        if free_b > 0: 
            day_log["BoosterLog"].append(f"Use {free_b} Broom (from Inv)")
            day_log["BoostersSpent"]['Broom'] += free_b
            tot_bst_used['Broom'] += free_b
            
        if free_s > 0: 
            day_log["BoosterLog"].append(f"Use {free_s} Scissors (from Inv)")
            day_log["BoostersSpent"]['Scissors'] += free_s
            tot_bst_used['Scissors'] += free_s
        
        day_sink += int(cost_h) + int(cost_b) + int(cost_s)
        day_log["CoinsSpent"] += day_sink
        day_log["Inv"] = inv.copy()
        day_log["CumulativeCoins"] = current_coins
        
        tot_sink += day_sink
        macro_log.append(day_log)

    tot_inflow = tot_base + tot_rv + tot_liveops
    net_accum = tot_inflow - tot_sink
    total_bst_used_overall = sum(tot_bst_used.values())
    tot_bst_bought = {'Hammer': 0, 'Broom': 0, 'Scissors': 0, 'Revive': tot_revives_bought}
    
    return {
        'days': days,
        'daily_levels': daily_levels,
        'tot_inflow': tot_inflow,
        'tot_sink': tot_sink,
        'net_accum': net_accum,
        'avg_win_rate': avg_win_rate,
        'total_levels_played': sum(lg['LevelsPlayed'] for lg in macro_log),
        'avg_levels_per_day': sum(lg['LevelsPlayed'] for lg in macro_log) / days,
        'total_bst_used_overall': total_bst_used_overall,
        'tot_revives_bought': tot_revives_bought,
        'failed_levels_per_day': (sum(lg['LevelsPlayed'] for lg in macro_log) * (1 - avg_win_rate)) / days,
        'final_inv': inv,
        'tot_base': tot_base,
        'tot_rv': tot_rv,
        'tot_liveops': tot_liveops,
        'tot_liveops_keys': tot_liveops_keys,
        'tot_liveops_streak': tot_liveops_streak,
        'tot_liveops_mp': tot_liveops_mp,
        'tot_bst_bought': tot_bst_bought,
        'tot_bst_earned': tot_bst_earned,
        'tot_bst_earned_keys': tot_bst_earned_keys,
        'tot_bst_earned_streak': tot_bst_earned_streak,
        'tot_bst_earned_mp': tot_bst_earned_mp,
        'macro_log': macro_log
    }
