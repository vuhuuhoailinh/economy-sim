import random
import pandas as pd
from config import DEFAULT_PRICES, SET_REWARDS_MAP, GRAND_PRIZE_REWARDS
from utils.parser import parse_rewards, parse_packs
from card_album.config import PACK_ORDER, TOTAL_CARDS, CARD_SETS, CHEST_CONFIG
from card_album.config_manager import get_default_config
from card_album.state import fresh_inventory, fresh_pack_counts, total_cards_collected, reset_season
from card_album.gacha import open_pack, process_chest_drop_hit, format_card_name

def is_card_rush_day(day: int) -> bool:
    if day <= 0: return False
    week = (day - 1) // 7 + 1
    weekday = (day - 1) % 7 + 1
    if week <= 6: 
        return weekday == 6
    else: 
        return weekday in (3, 6)

def upgrade_pack(pack: str, is_cr: bool) -> str:
    if is_cr and pack in ("Bronze", "Emerald", "Silver"):
        return pack + "+"
    return pack

def create_album_state(tuning_cfg=None):
    def_cfg = get_default_config()
    custom_packs = tuning_cfg.get('config_packs') if tuning_cfg else None
    custom_chest_tiers = tuning_cfg.get('config_chest_drop_tiers') if tuning_cfg else None
    custom_chest_matrix = tuning_cfg.get('config_chest_upgrade_matrix') if tuning_cfg else None
    chest_x = tuning_cfg.get('config_chest_drop_x', 2.0) if tuning_cfg else 2.0
    new_card_power = tuning_cfg.get('new_card_power', 2.5) if tuning_cfg else 2.5
    s_base = tuning_cfg.get('config_ss2_s_base', 0.1) if tuning_cfg else 0.1
    s_max = tuning_cfg.get('config_ss2_s_max', 0.5) if tuning_cfg else 0.5
    c_base = tuning_cfg.get('config_ss2_c_base', 0.3) if tuning_cfg else 0.3
    c_max = tuning_cfg.get('config_ss2_c_max', 1.0) if tuning_cfg else 1.0

    return {
        "inventory": fresh_inventory(),
        "stars": 0,
        "total_packs": 0,
        "pack_counts": fresh_pack_counts(),
        "pack_pity": fresh_pack_counts(),
        "log": [],
        "grand_album_enabled": True,
        "grand_album_completions": 0,
        "grand_album_finished": False,
        "new_card_formula_type": "document",
        "config_packs": custom_packs if custom_packs else def_cfg["packs"],
        "new_card_power": new_card_power,
        "pity_multiplier": 1.0,
        "owned_cards": set(),
        "total_cards_drawn": 0,
        "new_cards_drawn": 0,
        "dup_cards_drawn": 0,
        "pack_stars_gained": 0,
        "new_cards_by_rarity": {r: 0 for r in range(1, 7)},
        "dup_cards_by_rarity": {r: 0 for r in range(1, 7)},
        "cd_total_cards_drawn": 0,
        "cd_new_cards_drawn": 0,
        "cd_dup_cards_drawn": 0,
        "cd_stars_gained": 0,
        "cd_new_cards_by_rarity": {r: 0 for r in range(1, 7)},
        "cd_dup_cards_by_rarity": {r: 0 for r in range(1, 7)},
        "chest_drop_counts": {r: 0 for r in range(1, 6)},
        "config_chest_drop_tiers": custom_chest_tiers if custom_chest_tiers else def_cfg["chest_tiers"],
        "config_chest_upgrade_matrix": custom_chest_matrix if custom_chest_matrix else def_cfg["chest_upgrade_matrix"],
        "config_chest_drop_x": chest_x,
        "opened_pack_types_ss2": set(),
        "ss2_optimize_collection": True,
        "config_ss2_s_base": s_base,
        "config_ss2_s_max": s_max,
        "config_ss2_c_base": c_base,
        "config_ss2_c_max": c_max,
        "cd_log": [],
        "cd_upgrade_summary": {t: {dest: 0 for dest in range(1, 6)} for t in range(1, 4)},
        "cd_total_chests_opened": 0
    }


def run_deterministic_simulation(cfg, tuning_cfg):
    days = cfg['sim_days']

    avg_base_coin_per_lvl = (20 * 6 + 40 * 2 + 60 * 1) / 9
    avg_win_rate = (cfg['win_rate_n'] * 6 + cfg['win_rate_h'] * 2 + cfg['win_rate_sh'] * 1) / 9
    
    prices_df = tuning_cfg.get('prices', pd.DataFrame(DEFAULT_PRICES))
    COST = dict(zip(prices_df['Item'], prices_df['Price']))
    
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
    
    # Card Album State & Tracking
    sim_album_state = create_album_state(tuning_cfg)
    tot_packs_earned = {p: 0 for p in PACK_ORDER}
    tot_packs_earned_core = {p: 0 for p in PACK_ORDER}
    tot_packs_earned_mp = {p: 0 for p in PACK_ORDER}
    tot_packs_earned_streak = {p: 0 for p in PACK_ORDER}
    tot_packs_earned_keys = {p: 0 for p in PACK_ORDER}
    tot_packs_earned_star_chest = {p: 0 for p in PACK_ORDER}
    tot_star_chests = {'Gold': 0, 'Silver': 0, 'Bronze': 0}
    tot_chests_earned = {1: 0, 2: 0, 3: 0}
    global_won_level = 0
    tot_album_coins = 0
    tot_bst_earned_album = {'Hammer': 0, 'Broom': 0, 'Scissors': 0}
    claimed_sets_round = {0: set(), 1: set()}
    claimed_grand_prize = {0: False, 1: False}

    enable_core_packs = cfg.get('enable_core_packs', False)
    enable_card_rush = cfg.get('enable_card_rush', True)
    enable_chest_drop = cfg.get('enable_chest_drop', True)
    enable_auto_star_chest = cfg.get('enable_auto_star_chest', True)
    auto_open_packs = cfg.get('auto_open_packs', True)

    macro_log = []
    accum_needed = {'Revive': 0.0, 'Hammer': 0.0, 'Broom': 0.0, 'Scissors': 0.0}
    current_coins = 400
    streak_wins = 0.0
    accum_fails = 0.0
    accum_lost_levels = 0.0
    accum_keys = 0.0
    claimed_streak_reqs = set()
    claimed_key_reqs = set()
    
    for d in range(1, days + 1):
        is_cr = enable_card_rush and is_card_rush_day(d)
        day_packs = {}
        day_chests = {}

        if cfg.get('min_l', 2) == cfg.get('max_l', 2):
            daily_levels = cfg['daily_sessions'] * cfg.get('min_l', 2)
        else:
            daily_levels = sum(random.randint(cfg['min_l'], cfg['max_l']) for _ in range(cfg['daily_sessions']))
            
        accum_lost_levels += daily_levels * (1.0 - avg_win_rate)
        actual_lost = int(round(accum_lost_levels, 5))
        if actual_lost > 0:
            accum_lost_levels -= actual_lost
            actual_lost = min(daily_levels, actual_lost)
        lost_levels = actual_lost
        won_levels = daily_levels - lost_levels
        failed_levels_per_day = daily_levels * (1 - avg_win_rate)
        
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
            "MPStage": 0, "MPTokens": 0, "MPTier": cfg.get('mp_tier', 'Free') if cfg.get('enable_mp', True) else "Off",
            "IsCardRush": is_cr,
            "PacksEarned": {}, "ChestsEarned": {},
            "AlbumCardsNew": 0, "AlbumCardsDup": 0, "AlbumStarsGained": 0,
            "AlbumTotalOwned": 0, "AlbumCompletionPct": 0.0, "AlbumStarsTotal": 0,
            "AlbumSetsCompleted": 0,
            "AlbumSeason": ((d - 1) // 60) + 1
        }
        
        # Check for Card Album Season Rollover (Season duration = 60 days)
        if d > 1 and (d - 1) % 60 == 0:
            season_num = (d - 1) // 60 + 1
            prev_season = season_num - 1
            reset_season(sim_album_state)
            claimed_sets_round = {0: set(), 1: set()}
            claimed_grand_prize = {0: False, 1: False}
            day_log["EventLog"].append(
                f":rainbow[**Card Album Season {season_num} Started (Day {d})**]: Mùa Card Album {prev_season} (60 ngày) đã kết thúc! Bắt đầu Mùa {season_num}, toàn bộ thẻ về 0 để mở lại chu kỳ sưu tập mới."
            )
        
        day_base = daily_levels * avg_base_coin_per_lvl * avg_win_rate
        day_rv = day_base * cfg['rv_watch_rate'] * (cfg['rv_multiplier'] - 1)
        
        day_base_earned = int(round(day_base))
        day_rv_earned = int(round(day_rv))
        
        day_log["CoinLog"].append(f"Gameplay Base (from {daily_levels} levels played): +{day_base_earned} Coins")
        day_log["CoinLog"].append(f"Rewarded Video (RV): +{day_rv_earned} Coins")
        day_log["CoinsEarned"] += day_base_earned + day_rv_earned
        current_coins += day_base_earned + day_rv_earned
        
        tot_base += day_base_earned
        tot_rv += day_rv_earned

        # Core Gameplay Packs & Daily Chests
        if enable_core_packs:
            for _ in range(won_levels):
                global_won_level += 1
                if global_won_level % 3 == 0 and global_won_level % 9 != 0:
                    p = upgrade_pack("Bronze", is_cr)
                    day_packs[p] = day_packs.get(p, 0) + 1
                    tot_packs_earned_core[p] = tot_packs_earned_core.get(p, 0) + 1
                elif global_won_level % 9 == 0:
                    p = upgrade_pack("Emerald", is_cr)
                    day_packs[p] = day_packs.get(p, 0) + 1
                    tot_packs_earned_core[p] = tot_packs_earned_core.get(p, 0) + 1

        if enable_chest_drop:
            if won_levels >= 3:
                day_chests[1] = day_chests.get(1, 0) + 1
                tot_chests_earned[1] += 1
            if won_levels >= 7:
                day_chests[2] = day_chests.get(2, 0) + 1
                tot_chests_earned[2] += 1
            if won_levels >= 12:
                day_chests[3] = day_chests.get(3, 0) + 1
                tot_chests_earned[3] += 1

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
            if mp_tier != 'Premium':
                master_pass_tokens = min(float(max_mp_stage), master_pass_tokens + daily_tokens)
            else:
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
                        
                        # Parse packs from Free track
                        _fp = parse_packs(rew_str)
                        for p, cnt in _fp.items():
                            p_act = upgrade_pack(p, is_cr)
                            day_packs[p_act] = day_packs.get(p_act, 0) + cnt
                            tot_packs_earned_mp[p_act] = tot_packs_earned_mp.get(p_act, 0) + cnt

                        _pc, _ph, _pb, _ps = 0, 0, 0, 0
                        if mp_tier == 'Premium' and prem_rew_str:
                            _pc, _ph, _pb, _ps = parse_rewards(prem_rew_str)
                            prem_c += _pc; prem_h += _ph; prem_b += _pb; prem_s += _ps
                            
                            # Parse packs from Premium track
                            _pp = parse_packs(prem_rew_str)
                            for p, cnt in _pp.items():
                                p_act = upgrade_pack(p, is_cr)
                                day_packs[p_act] = day_packs.get(p_act, 0) + cnt
                                tot_packs_earned_mp[p_act] = tot_packs_earned_mp.get(p_act, 0) + cnt
                        
                        reached_stage_info.append({
                            'stage': stg,
                            'free_reward': rew_str,
                            'prem_reward': prem_rew_str if mp_tier == 'Premium' else None
                        })

            if mp_tier == 'Premium' and master_pass_tokens > max_mp_stage:
                prev_overflow = max(0, prev_mp_tokens - max_mp_stage)
                curr_overflow = master_pass_tokens - max_mp_stage
                chunks_today = int(curr_overflow / 10) - int(prev_overflow / 10)
                if chunks_today > 0:
                    added_bank = chunks_today * 150
                    master_pass_bonus_bank = min(3000, master_pass_bonus_bank + added_bank)

            if mp_tier == 'Premium' and d % 30 == 0 and master_pass_bonus_bank > 0:
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
        
        c, h, b, s = 0, 0, 0, 0
        stages_reached = 0
        
        if enable_keys:
            for req, rew_str in zip(k_df['KeysReq'], k_df['Reward']):
                if prev_keys < req and accum_keys >= req and req not in claimed_key_reqs:
                    claimed_key_reqs.add(req)
                    stages_reached += 1
                    _c, _h, _b, _s = parse_rewards(rew_str)
                    c += _c; h += _h; b += _b; s += _s
                    
                    _kp = parse_packs(rew_str)
                    for p, cnt in _kp.items():
                        p_act = upgrade_pack(p, is_cr)
                        day_packs[p_act] = day_packs.get(p_act, 0) + cnt
                        tot_packs_earned_keys[p_act] = tot_packs_earned_keys.get(p_act, 0) + cnt
                
        if stages_reached > 0:
            day_liveops += c
            tot_liveops_keys += c
            inv['Hammer'] += h; inv['Broom'] += b; inv['Scissors'] += s
            tot_bst_earned['Hammer'] += h; tot_bst_earned['Broom'] += b; tot_bst_earned['Scissors'] += s
            tot_bst_earned_keys['Hammer'] += h; tot_bst_earned_keys['Broom'] += b; tot_bst_earned_keys['Scissors'] += s
            
            if c > 0: day_log["CoinLog"].append(f"Key Collection ({stages_reached} stages): +{int(c)} Coins")
            if h > 0 or b > 0 or s > 0:
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
                        if _h > 0 or _b > 0 or _s > 0:
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

                        _sp = parse_packs(rew_str)
                        for p, cnt in _sp.items():
                            p_act = upgrade_pack(p, is_cr)
                            day_packs[p_act] = day_packs.get(p_act, 0) + cnt
                            tot_packs_earned_streak[p_act] = tot_packs_earned_streak.get(p_act, 0) + cnt
                
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

        # Card Album Daily Packs & Chests Opening
        def claim_sets_for_round(rnd: int):
            nonlocal current_coins, tot_album_coins
            set_counts = {}
            for c in sim_album_state.get("owned_cards", set()):
                set_counts[c[0]] = set_counts.get(c[0], 0) + 1

            newly_completed = []
            for s_id, s_info in CARD_SETS.items():
                if set_counts.get(s_id, 0) >= sum(s_info["cards"].values()):
                    if s_id not in claimed_sets_round[rnd]:
                        claimed_sets_round[rnd].add(s_id)
                        newly_completed.append(s_id)
                        
                        set_data = SET_REWARDS_MAP.get(s_id, {})
                        rew_str = set_data.get("AlbumReward" if rnd == 0 else "GrandAlbumReward", "")
                        if rew_str:
                            _c, _h, _b, _s = parse_rewards(rew_str)
                            if _c > 0:
                                day_log["CoinsEarned"] += _c
                                current_coins += _c
                                tot_album_coins += _c
                                day_log["CoinLog"].append(f"Card Album Set {s_id} ({set_data.get('Name')}) Completed: +{_c} Coins")
                            if _h > 0 or _b > 0 or _s > 0:
                                inv['Hammer'] += _h; inv['Broom'] += _b; inv['Scissors'] += _s
                                tot_bst_earned['Hammer'] += _h; tot_bst_earned['Broom'] += _b; tot_bst_earned['Scissors'] += _s
                                tot_bst_earned_album['Hammer'] += _h; tot_bst_earned_album['Broom'] += _b; tot_bst_earned_album['Scissors'] += _s
                                day_log["BoostersEarned"]['Hammer'] += _h
                                day_log["BoostersEarned"]['Broom'] += _b
                                day_log["BoostersEarned"]['Scissors'] += _s
                                
                                bst_parts = []
                                if _h > 0: bst_parts.append(f"+{_h} Hammer")
                                if _b > 0: bst_parts.append(f"+{_b} Broom")
                                if _s > 0: bst_parts.append(f"+{_s} Scissors")
                                day_log["BoosterLog"].append(f"Card Album Set {s_id} ({set_data.get('Name')}) Completed: {', '.join(bst_parts)}")

            if newly_completed:
                total_in_rnd = len(claimed_sets_round[rnd])
                for s_id in newly_completed:
                    set_data = SET_REWARDS_MAP.get(s_id, {})
                    rew_str = set_data.get("AlbumReward" if rnd == 0 else "GrandAlbumReward", "")
                    prefix = "Grand Album" if rnd == 1 else "Card Album"
                    day_log["EventLog"].append(f"{prefix} Set {s_id} ({set_data.get('Name')}) Completed! Reward: [{rew_str}] (Total: {total_in_rnd}/15 Sets)")

            # Check Grand Prize for round 0 (full 135 cards)
            if rnd == 0 and (len(claimed_sets_round[0]) == 15 or total_cards_collected(sim_album_state) >= TOTAL_CARDS) and not claimed_grand_prize[0]:
                claimed_grand_prize[0] = True
                gp_rew = GRAND_PRIZE_REWARDS["AlbumReward"]
                _c, _h, _b, _s = parse_rewards(gp_rew)
                day_log["CoinsEarned"] += _c
                current_coins += _c
                tot_album_coins += _c
                inv['Hammer'] += _h; inv['Broom'] += _b; inv['Scissors'] += _s
                tot_bst_earned['Hammer'] += _h; tot_bst_earned['Broom'] += _b; tot_bst_earned['Scissors'] += _s
                tot_bst_earned_album['Hammer'] += _h; tot_bst_earned_album['Broom'] += _b; tot_bst_earned_album['Scissors'] += _s
                day_log["BoostersEarned"]['Hammer'] += _h
                day_log["BoostersEarned"]['Broom'] += _b
                day_log["BoostersEarned"]['Scissors'] += _s
                day_log["CoinLog"].append(f"Album Grand Prize (Full 135 Cards): +{_c} Coins")
                day_log["BoosterLog"].append(f"Album Grand Prize: +{_h} Hammer, +{_b} Broom, +{_s} Scissors")
                day_log["EventLog"].append(f"🏆 COMPLETED FULL ALBUM! Grand Prize: [{gp_rew}] ➔ Mở khóa Grand Album!")

            # Check Grand Prize for round 1 (Grand Album finished)
            if rnd == 1 and (len(claimed_sets_round[1]) == 15 or sim_album_state.get("grand_album_finished", False)) and not claimed_grand_prize[1]:
                claimed_grand_prize[1] = True
                gp_rew = GRAND_PRIZE_REWARDS["GrandAlbumReward"]
                _c, _h, _b, _s = parse_rewards(gp_rew)
                day_log["CoinsEarned"] += _c
                current_coins += _c
                tot_album_coins += _c
                inv['Hammer'] += _h; inv['Broom'] += _b; inv['Scissors'] += _s
                tot_bst_earned['Hammer'] += _h; tot_bst_earned['Broom'] += _b; tot_bst_earned['Scissors'] += _s
                tot_bst_earned_album['Hammer'] += _h; tot_bst_earned_album['Broom'] += _b; tot_bst_earned_album['Scissors'] += _s
                day_log["BoostersEarned"]['Hammer'] += _h
                day_log["BoostersEarned"]['Broom'] += _b
                day_log["BoostersEarned"]['Scissors'] += _s
                day_log["CoinLog"].append(f"Grand Album Grand Prize: +{_c} Coins")
                day_log["BoosterLog"].append(f"Grand Album Grand Prize: +{_h} Hammer, +{_b} Broom, +{_s} Scissors")
                day_log["EventLog"].append(f"🏆 COMPLETED GRAND ALBUM! Grand Prize: [{gp_rew}]")

        sim_album_state["on_album_complete"] = lambda state, completions: claim_sets_for_round(completions)

        start_new_total = sim_album_state["new_cards_drawn"] + sim_album_state["cd_new_cards_drawn"]
        start_dup_total = sim_album_state["dup_cards_drawn"] + sim_album_state["cd_dup_cards_drawn"]
        start_stars_gained = sim_album_state.get("pack_stars_gained", 0) + sim_album_state.get("cd_stars_gained", 0)

        for p, count in day_packs.items():
            tot_packs_earned[p] = tot_packs_earned.get(p, 0) + count
            if auto_open_packs:
                for _ in range(count):
                    open_pack(sim_album_state, p)

        if auto_open_packs:
            for stier, count in day_chests.items():
                for c_num in range(count):
                    sim_album_state["cd_total_chests_opened"] = sim_album_state.get("cd_total_chests_opened", 0) + 1
                    cur_tier = stier
                    drawn_in_chest = set()
                    hit_logs = []
                    chest_has_new = False
                    for _ in range(5):
                        hit = process_chest_drop_hit(sim_album_state, stier, cur_tier, drawn_in_chest)
                        if hit["status"] == "NEW":
                            chest_has_new = True
                        card_tuple = hit.get("card")
                        cname = format_card_name(card_tuple) if card_tuple else "?"
                        card_r = card_tuple[1] if card_tuple else hit.get("rarity", cur_tier)
                        status_str = f"({hit['status']})"
                        card_str = f"{card_r}⭐ [{cname}] {status_str}"
                        if hit.get("upgraded", False):
                            hit_logs.append(f"{card_str} ➔ Upgraded to {hit['next_tier']}⭐")
                        else:
                            hit_logs.append(card_str)
                        cur_tier = hit['next_tier']
                    
                    if "cd_upgrade_summary" not in sim_album_state:
                        sim_album_state["cd_upgrade_summary"] = {t: {dest: 0 for dest in range(1, 6)} for t in range(1, 4)}
                    if stier in sim_album_state["cd_upgrade_summary"]:
                        sim_album_state["cd_upgrade_summary"][stier][cur_tier] = sim_album_state["cd_upgrade_summary"][stier].get(cur_tier, 0) + 1
                    
                    if "cd_log" not in sim_album_state:
                        sim_album_state["cd_log"] = []
                    prefix = "[NEW]" if chest_has_new else "[DUP]"
                    log_msg = f"Day {d} {prefix} Chest {stier}⭐ #{c_num+1} (Final: {cur_tier}⭐) | Hits: " + ", ".join(hit_logs)
                    sim_album_state["cd_log"].insert(0, log_msg)
                    if len(sim_album_state["cd_log"]) > 300:
                        sim_album_state["cd_log"] = sim_album_state["cd_log"][:300]

            # Auto Star Chest Exchange if enabled (Target Gold 500⭐ down to Bronze 100⭐)
            if enable_auto_star_chest:
                star_chests_today = {'Gold': 0, 'Silver': 0, 'Bronze': 0}
                is_season_end_or_last_day = (d % 60 == 0) or (d == days)
                auto_loops = 0
                while auto_loops < 50:
                    auto_loops += 1
                    if sim_album_state["stars"] >= 500:
                        c_type = "Gold"
                    elif is_season_end_or_last_day and sim_album_state["stars"] >= 250:
                        c_type = "Silver"
                    elif is_season_end_or_last_day and sim_album_state["stars"] >= 100:
                        c_type = "Bronze"
                    else:
                        break
                    
                    cost = CHEST_CONFIG[c_type]["cost"]
                    sim_album_state["stars"] -= cost
                    star_chests_today[c_type] += 1
                    tot_star_chests[c_type] += 1
                    
                    for base_p in CHEST_CONFIG[c_type]["packs"]:
                        act_p = upgrade_pack(base_p, is_cr)
                        tot_packs_earned[act_p] = tot_packs_earned.get(act_p, 0) + 1
                        tot_packs_earned_star_chest[act_p] = tot_packs_earned_star_chest.get(act_p, 0) + 1
                        day_packs[act_p] = day_packs.get(act_p, 0) + 1
                        open_pack(sim_album_state, act_p)

                day_log["StarChestsEarned"] = star_chests_today.copy()
                if sum(star_chests_today.values()) > 0:
                    parts = []
                    spent_stars = 0
                    if star_chests_today['Gold'] > 0:
                        parts.append(f"{star_chests_today['Gold']} Gold")
                        spent_stars += star_chests_today['Gold'] * CHEST_CONFIG['Gold']['cost']
                    if star_chests_today['Silver'] > 0:
                        parts.append(f"{star_chests_today['Silver']} Silver")
                        spent_stars += star_chests_today['Silver'] * CHEST_CONFIG['Silver']['cost']
                    if star_chests_today['Bronze'] > 0:
                        parts.append(f"{star_chests_today['Bronze']} Bronze")
                        spent_stars += star_chests_today['Bronze'] * CHEST_CONFIG['Bronze']['cost']
                    day_log["EventLog"].append(
                        f":violet[**Auto Star Chest**]: Opened {', '.join(parts)} Chest(s) (-{spent_stars}⭐)"
                    )

        cards_new_today = (sim_album_state["new_cards_drawn"] + sim_album_state["cd_new_cards_drawn"]) - start_new_total
        cards_dup_today = (sim_album_state["dup_cards_drawn"] + sim_album_state["cd_dup_cards_drawn"]) - start_dup_total
        stars_gained_today = (sim_album_state.get("pack_stars_gained", 0) + sim_album_state.get("cd_stars_gained", 0)) - start_stars_gained
        current_owned_cards = total_cards_collected(sim_album_state)

        # Track completed sets and grant rewards
        current_round = min(1, sim_album_state.get("grand_album_completions", 0))
        claim_sets_for_round(current_round)

        cards_new_today = (sim_album_state["new_cards_drawn"] + sim_album_state["cd_new_cards_drawn"]) - start_new_total
        cards_dup_today = (sim_album_state["dup_cards_drawn"] + sim_album_state["cd_dup_cards_drawn"]) - start_dup_total
        stars_gained_today = (sim_album_state.get("pack_stars_gained", 0) + sim_album_state.get("cd_stars_gained", 0)) - start_stars_gained
        current_owned_cards = total_cards_collected(sim_album_state)
        ga_completions = sim_album_state.get("grand_album_completions", 0)
        cumulative_cards = ga_completions * TOTAL_CARDS + current_owned_cards

        total_sets_completed = len(claimed_sets_round[current_round])
        day_log["AlbumSetsCompleted"] = total_sets_completed
        day_log["AlbumTotalSetsCompleted"] = len(claimed_sets_round[0]) + len(claimed_sets_round[1])
        day_log["PacksEarned"] = {k: v for k, v in day_packs.items() if v > 0}
        day_log["ChestsEarned"] = {k: v for k, v in day_chests.items() if v > 0}
        day_log["AlbumCardsNew"] = cards_new_today
        day_log["AlbumCardsDup"] = cards_dup_today
        day_log["AlbumStarsGained"] = stars_gained_today
        day_log["AlbumTotalOwned"] = current_owned_cards
        day_log["AlbumCumulativeCards"] = cumulative_cards
        day_log["AlbumRound"] = 2 if ga_completions >= 1 else 1
        day_log["AlbumStage"] = "Grand Album" if ga_completions >= 1 else "Standard Album"
        day_log["AlbumCompletionPct"] = (current_owned_cards / TOTAL_CARDS) * 100
        day_log["AlbumStarsTotal"] = sim_album_state["stars"]

        if is_cr:
            day_log["EventLog"].append("Card Rush Active: Bronze, Emerald, Silver upgraded to Plus (+)")

        pack_summary_parts = []
        for p, cnt in day_packs.items():
            if cnt > 0: pack_summary_parts.append(f"+{cnt} {p}")
        for t, cnt in day_chests.items():
            if cnt > 0: pack_summary_parts.append(f"+{cnt} Chest {t}*")
            
        if pack_summary_parts:
            round_tag = f"[{day_log['AlbumStage']}] " if ga_completions >= 1 else ""
            day_log["EventLog"].append(
                f"{round_tag}Card Album: {', '.join(pack_summary_parts)} | Progress: +{cards_new_today} New, {cards_dup_today} Dup (+{stars_gained_today} Stars) -> Total: {current_owned_cards}/135 ({current_owned_cards/135*100:.1f}%) | Sets: {total_sets_completed}/15"
            )

        def process_revive():
            nonlocal current_coins
            bought = 0
            cost = 0
            
            if lost_levels > 0:
                willing_to_buy = lost_levels * cfg.get('revive_buy_rate', 0.1)
                accum_needed["Revive_buy"] = accum_needed.get("Revive_buy", 0) + willing_to_buy
                wanted_to_buy = min(lost_levels, int(round(accum_needed["Revive_buy"], 5)))
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
        if target_uses > 0:
            accum_needed['bst_free'] = 0.0
        
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

    tot_inflow = tot_base + tot_rv + tot_liveops + tot_album_coins
    net_accum = tot_inflow - tot_sink
    total_bst_used_overall = sum(tot_bst_used.values())
    tot_bst_bought = {'Hammer': 0, 'Broom': 0, 'Scissors': 0, 'Revive': tot_revives_bought}
    
    # Calculate completed sets
    final_owned = total_cards_collected(sim_album_state)
    ga_completions = sim_album_state.get('grand_album_completions', 0)
    current_round = min(1, ga_completions)
    completed_sets_count = len(claimed_sets_round[current_round])

    return {
        'days': days,
        'daily_levels': daily_levels,
        'tot_inflow': tot_inflow,
        'tot_sink': tot_sink,
        'net_accum': net_accum,
        'avg_win_rate': avg_win_rate,
        'total_levels_played': sum(lg['LevelsPlayed'] for lg in macro_log),
        'total_levels_won': sum(lg.get('LevelsWon', 0) for lg in macro_log),
        'total_levels_lost': sum(lg.get('LevelsLost', 0) for lg in macro_log),
        'avg_levels_per_day': sum(lg['LevelsPlayed'] for lg in macro_log) / days,
        'avg_won_per_day': sum(lg.get('LevelsWon', 0) for lg in macro_log) / days,
        'avg_lost_per_day': sum(lg.get('LevelsLost', 0) for lg in macro_log) / days,
        'total_bst_used_overall': total_bst_used_overall,
        'tot_revives_bought': tot_revives_bought,
        'failed_levels_per_day': sum(lg.get('LevelsLost', 0) for lg in macro_log) / days,
        'final_inv': inv,
        'tot_base': tot_base,
        'tot_rv': tot_rv,
        'tot_liveops': tot_liveops,
        'tot_liveops_keys': tot_liveops_keys,
        'tot_liveops_streak': tot_liveops_streak,
        'tot_liveops_mp': tot_liveops_mp,
        'tot_album_coins': tot_album_coins,
        'tot_bst_earned_album': tot_bst_earned_album,
        'tot_bst_bought': tot_bst_bought,
        'tot_bst_earned': tot_bst_earned,
        'tot_bst_earned_keys': tot_bst_earned_keys,
        'tot_bst_earned_streak': tot_bst_earned_streak,
        'tot_bst_earned_mp': tot_bst_earned_mp,
        'macro_log': macro_log,
        'sim_album_state': sim_album_state,
        'tot_packs_earned': tot_packs_earned,
        'tot_packs_earned_core': tot_packs_earned_core,
        'tot_packs_earned_mp': tot_packs_earned_mp,
        'tot_packs_earned_streak': tot_packs_earned_streak,
        'tot_packs_earned_keys': tot_packs_earned_keys,
        'tot_packs_earned_star_chest': tot_packs_earned_star_chest,
        'tot_star_chests': tot_star_chests,
        'enable_auto_star_chest': enable_auto_star_chest,
        'tot_chests_earned': tot_chests_earned,
        'album_summary': {
            'total_cards_owned': final_owned,
            'total_cards': TOTAL_CARDS,
            'completion_pct': (final_owned / TOTAL_CARDS) * 100,
            'cumulative_cards': ga_completions * TOTAL_CARDS + final_owned,
            'total_stars': sim_album_state['stars'],
            'new_cards_drawn': sim_album_state['new_cards_drawn'] + sim_album_state['cd_new_cards_drawn'],
            'dup_cards_drawn': sim_album_state['dup_cards_drawn'] + sim_album_state['cd_dup_cards_drawn'],
            'completed_sets': completed_sets_count,
            'main_album_sets': len(claimed_sets_round[0]),
            'grand_album_sets': len(claimed_sets_round[1]),
            'total_sets_completed': len(claimed_sets_round[0]) + len(claimed_sets_round[1]),
            'grand_album_completions': ga_completions,
            'grand_album_finished': sim_album_state.get('grand_album_finished', False),
            'is_grand_album': ga_completions >= 1,
            'current_season': ((days - 1) // 60) + 1,
            'season_day': ((days - 1) % 60) + 1
        }
    }
