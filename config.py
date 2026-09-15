import pandas as pd

COIN_N, COIN_H, COIN_SH = 20, 40, 60
# COST dict is now dynamic, read from tuning_cfg['prices']
DEFAULT_PRICES = [
    {"Item": "Revive", "Price": 380},
    {"Item": "Hammer", "Price": 160},
    {"Item": "Broom", "Price": 240},
    {"Item": "Scissors", "Price": 120},
    {"Item": "Booster Set", "Price": 380}
]

DEFAULT_KEY_STAGES = [
    {"Stage": 1, "KeysReq": 3, "Reward": "15m Heart"},
    {"Stage": 2, "KeysReq": 8, "Reward": "1x Scissors"},
    {"Stage": 3, "KeysReq": 15, "Reward": "15m x2 Key"},
    {"Stage": 4, "KeysReq": 25, "Reward": "1x Bronze Pack"},
    {"Stage": 5, "KeysReq": 33, "Reward": "1x Hammer"},
    {"Stage": 6, "KeysReq": 40, "Reward": "1x Broom"},
    {"Stage": 7, "KeysReq": 52, "Reward": "1x Bronze Pack"},
    {"Stage": 8, "KeysReq": 67, "Reward": "30m x2 Key"},
    {"Stage": 9, "KeysReq": 77, "Reward": "1x Scissors"},
    {"Stage": 10, "KeysReq": 89, "Reward": "1x Emerald Pack"},
    {"Stage": 11, "KeysReq": 99, "Reward": "30m Heart"},
    {"Stage": 12, "KeysReq": 111, "Reward": "80 Coins"},
    {"Stage": 13, "KeysReq": 126, "Reward": "1x Emerald Pack"},
    {"Stage": 14, "KeysReq": 138, "Reward": "1x Broom"},
    {"Stage": 15, "KeysReq": 154, "Reward": "30m x2 Key"},
    {"Stage": 16, "KeysReq": 164, "Reward": "120 Coins"},
    {"Stage": 17, "KeysReq": 176, "Reward": "1x Silver Pack"},
    {"Stage": 18, "KeysReq": 192, "Reward": "1x Scissors"},
    {"Stage": 19, "KeysReq": 204, "Reward": "1h Heart"},
    {"Stage": 20, "KeysReq": 214, "Reward": "200 Coins"},
    {"Stage": 21, "KeysReq": 229, "Reward": "1x Amethyst Pack"},
    {"Stage": 22, "KeysReq": 241, "Reward": "1x Hammer"},
    {"Stage": 23, "KeysReq": 259, "Reward": "1h x2 Key"},
    {"Stage": 24, "KeysReq": 279, "Reward": "1x Ruby Pack"},
    {"Stage": 25, "KeysReq": 304, "Reward": "1000 Coins"},
]


DEFAULT_MASTER_PASS_STAGES = [
    {"Stage": 0, "TokensReq": 0, "Reward": "1x Hammer", "PremiumReward": "8-Heart Limit + Golden Frame + 500 coins"},
    {"Stage": 1, "TokensReq": 1, "Reward": "15m Heart", "PremiumReward": "30m Heart"},
    {"Stage": 2, "TokensReq": 3, "Reward": "1x Bronze Pack", "PremiumReward": "1x Emerald Pack"},
    {"Stage": 3, "TokensReq": 6, "Reward": "40 Coins", "PremiumReward": "1x Scissors"},
    {"Stage": 4, "TokensReq": 10, "Reward": "1x Scissors", "PremiumReward": "1x Hammer"},
    {"Stage": 5, "TokensReq": 18, "Reward": "Chest: 1x Scissors + 1x Bronze Pack", "PremiumReward": "Chest: 100 Coins + 1x Broom + 1x Emerald Pack"},
    {"Stage": 6, "TokensReq": 23, "Reward": "60 Coins", "PremiumReward": "1x Scissors"},
    {"Stage": 7, "TokensReq": 29, "Reward": "15m Heart", "PremiumReward": "30m Heart"},
    {"Stage": 8, "TokensReq": 38, "Reward": "1x Hammer", "PremiumReward": "1x Hammer"},
    {"Stage": 9, "TokensReq": 45, "Reward": "1x Broom", "PremiumReward": "1x Broom"},
    {"Stage": 10, "TokensReq": 55, "Reward": "Chest: 1x Scissors + 1x Hammer + 1x Emerald Pack", "PremiumReward": "Chest: 150 Coins + 1x Hammer + 1x Broom + 1x Silver Pack"},
    {"Stage": 11, "TokensReq": 63, "Reward": "1x Hammer", "PremiumReward": "2x Scissors"},
    {"Stage": 12, "TokensReq": 75, "Reward": "1x Silver Pack", "PremiumReward": "1x Amethyst Pack"},
    {"Stage": 13, "TokensReq": 86, "Reward": "30m Heart", "PremiumReward": "60m Heart"},
    {"Stage": 14, "TokensReq": 95, "Reward": "1x Scissors", "PremiumReward": "1x Broom"},
    {"Stage": 15, "TokensReq": 107, "Reward": "Chest: 1x Scissors + 1x Broom + 1x Silver Pack", "PremiumReward": "Chest: 200 Coins + 1x Boosters Set + 1x Silver Pack"},
    {"Stage": 16, "TokensReq": 121, "Reward": "80 Coins", "PremiumReward": "2x Hammer"},
    {"Stage": 17, "TokensReq": 130, "Reward": "1x Emerald Pack", "PremiumReward": "1x Silver Pack"},
    {"Stage": 18, "TokensReq": 142, "Reward": "1x Scissors", "PremiumReward": "2x Scissors"},
    {"Stage": 19, "TokensReq": 157, "Reward": "30m Heart", "PremiumReward": "60m Heart"},
    {"Stage": 20, "TokensReq": 173, "Reward": "Chest: 1x Hammer + 1x Broom + 1x Amethyst Pack", "PremiumReward": "Chest: 300 Coins + 60m Heart + 1x Boosters Set + 1x Amethyst Pack"},
    {"Stage": 21, "TokensReq": 186, "Reward": "1x Hammer", "PremiumReward": "2x Hammer"},
    {"Stage": 22, "TokensReq": 196, "Reward": "100 Coins", "PremiumReward": "2x Broom"},
    {"Stage": 23, "TokensReq": 211, "Reward": "30m Heart", "PremiumReward": "60m Heart"},
    {"Stage": 24, "TokensReq": 225, "Reward": "1x Emerald Pack", "PremiumReward": "1x Silver Pack"},
    {"Stage": 25, "TokensReq": 241, "Reward": "Chest: 1x Boosters Set + 1x Silver Pack", "PremiumReward": "Chest: 500 Coins + 60m Heart + 2x Boosters Set + 1x Ruby Pack"},
    {"Stage": 26, "TokensReq": 256, "Reward": "1x Hammer", "PremiumReward": "3x Hammer"},
    {"Stage": 27, "TokensReq": 273, "Reward": "1x Scissors", "PremiumReward": "3x Scissors"},
    {"Stage": 28, "TokensReq": 292, "Reward": "1x Silver Pack", "PremiumReward": "1x Amethyst Pack"},
    {"Stage": 29, "TokensReq": 309, "Reward": "1x Broom", "PremiumReward": "3x Broom"},
    {"Stage": 30, "TokensReq": 329, "Reward": "Chest: 200 Coins + 1x Boosters Set + 1x Ruby Pack", "PremiumReward": "Chest: 750 Coins + 60m Heart + 3x Boosters Set + 1x Rainbow Pack"},
]
DEFAULT_STREAK_STAGES = [
    {"WinsReq": 2, "Reward": "40 Coins", "Checkpoint": "Normal", "ResetFloor": 0},
    {"WinsReq": 5, "Reward": "15m Infinite Heart + 1x Bronze Pack", "Checkpoint": "CHECKPOINT 1", "ResetFloor": 5},
    {"WinsReq": 8, "Reward": "1x Emerald Pack", "Checkpoint": "Normal", "ResetFloor": 5},
    {"WinsReq": 11, "Reward": "1x Scissors", "Checkpoint": "CHECKPOINT 2", "ResetFloor": 11},
    {"WinsReq": 14, "Reward": "1x Silver Pack", "Checkpoint": "Normal", "ResetFloor": 11},
    {"WinsReq": 18, "Reward": "15m Infinite Heart + 80 Coins", "Checkpoint": "CHECKPOINT 3", "ResetFloor": 18},
    {"WinsReq": 24, "Reward": "1x Amethyst Pack", "Checkpoint": "Normal", "ResetFloor": 18},
    {"WinsReq": 30, "Reward": "2x Hammer + 30m Infinite Heart", "Checkpoint": "CHECKPOINT 4", "ResetFloor": 30},
    {"WinsReq": 36, "Reward": "300 Coins + 1x Ruby Pack + 1x Broom + Avatar", "Checkpoint": "GRAND FINALE", "ResetFloor": 30}
]

DEFAULT_STREAK_CHECKPOINTS = [5, 11, 18, 30]

def get_streak_floor(current_streak: float, s_df=None) -> float:
    """
    Returns the checkpoint floor for a given win streak.
    If s_df is provided with 'ResetFloor' column, uses the max ResetFloor for reached milestones.
    Otherwise falls back to DEFAULT_STREAK_CHECKPOINTS = [5, 11, 18, 30].
    """
    if s_df is not None and not s_df.empty:
        if 'ResetFloor' in s_df.columns:
            reached = s_df[s_df['WinsReq'] <= current_streak]
            if not reached.empty:
                return float(reached['ResetFloor'].max())
            return 0.0
        elif 'Checkpoint' in s_df.columns:
            cps = s_df[s_df['Checkpoint'].astype(str).str.contains('CHECKPOINT', case=False, na=False)]['WinsReq'].tolist()
            floor = 0.0
            for cp in sorted(cps):
                if current_streak >= cp:
                    floor = float(cp)
                else:
                    break
            return floor
    floor = 0.0
    for cp in DEFAULT_STREAK_CHECKPOINTS:
        if current_streak >= cp:
            floor = float(cp)
        else:
            break
    return floor

DEFAULT_CARD_SET_REWARDS = [
    {"Set": 1, "Name": "Items", "Common": 8, "Uncommon": 1, "Rare": 0, "Epic": 0, "Legendary": 0, "Secret": 0, "AlbumReward": "100 Coins", "GrandAlbumReward": "200 Coins"},
    {"Set": 2, "Name": "Transport", "Common": 7, "Uncommon": 2, "Rare": 0, "Epic": 0, "Legendary": 0, "Secret": 0, "AlbumReward": "2x Scissors", "GrandAlbumReward": "2x Scissors"},
    {"Set": 3, "Name": "Souvenirs", "Common": 7, "Uncommon": 1, "Rare": 1, "Epic": 0, "Legendary": 0, "Secret": 0, "AlbumReward": "2x Hammer", "GrandAlbumReward": "2x Hammer"},
    {"Set": 4, "Name": "Cuisine", "Common": 5, "Uncommon": 3, "Rare": 1, "Epic": 0, "Legendary": 0, "Secret": 0, "AlbumReward": "150 Coins", "GrandAlbumReward": "300 Coins"},
    {"Set": 5, "Name": "Camping", "Common": 3, "Uncommon": 4, "Rare": 1, "Epic": 1, "Legendary": 0, "Secret": 0, "AlbumReward": "2x Scissors", "GrandAlbumReward": "2x Scissors"},
    {"Set": 6, "Name": "Beach", "Common": 2, "Uncommon": 4, "Rare": 1, "Epic": 1, "Legendary": 1, "Secret": 0, "AlbumReward": "2x Broom", "GrandAlbumReward": "2x Broom"},
    {"Set": 7, "Name": "Retreat", "Common": 1, "Uncommon": 3, "Rare": 2, "Epic": 1, "Legendary": 1, "Secret": 1, "AlbumReward": "200 Coins", "GrandAlbumReward": "400 Coins"},
    {"Set": 8, "Name": "Theme Park", "Common": 0, "Uncommon": 4, "Rare": 2, "Epic": 1, "Legendary": 1, "Secret": 1, "AlbumReward": "2x Hammer", "GrandAlbumReward": "2x Hammer"},
    {"Set": 9, "Name": "Nature", "Common": 0, "Uncommon": 3, "Rare": 2, "Epic": 1, "Legendary": 2, "Secret": 1, "AlbumReward": "2x Broom", "GrandAlbumReward": "2x Broom"},
    {"Set": 10, "Name": "Ice Nature", "Common": 0, "Uncommon": 2, "Rare": 2, "Epic": 2, "Legendary": 1, "Secret": 2, "AlbumReward": "300 Coins", "GrandAlbumReward": "600 Coins"},
    {"Set": 11, "Name": "Museum", "Common": 0, "Uncommon": 1, "Rare": 3, "Epic": 1, "Legendary": 2, "Secret": 2, "AlbumReward": "3x Scissors", "GrandAlbumReward": "3x Scissors"},
    {"Set": 12, "Name": "Culture", "Common": 0, "Uncommon": 0, "Rare": 3, "Epic": 2, "Legendary": 2, "Secret": 2, "AlbumReward": "3x Hammer", "GrandAlbumReward": "3x Hammer"},
    {"Set": 13, "Name": "Landmark", "Common": 0, "Uncommon": 0, "Rare": 3, "Epic": 2, "Legendary": 1, "Secret": 3, "AlbumReward": "500 Coins", "GrandAlbumReward": "1000 Coins"},
    {"Set": 14, "Name": "Festivals", "Common": 0, "Uncommon": 0, "Rare": 2, "Epic": 2, "Legendary": 2, "Secret": 3, "AlbumReward": "3x Hammer", "GrandAlbumReward": "3x Hammer"},
    {"Set": 15, "Name": "Wonders", "Common": 0, "Uncommon": 0, "Rare": 0, "Epic": 4, "Legendary": 2, "Secret": 3, "AlbumReward": "3x Broom", "GrandAlbumReward": "3x Broom"},
    {"Set": "Total", "Name": "Travel (Grand Prize)", "Common": 33, "Uncommon": 28, "Rare": 23, "Epic": 18, "Legendary": 15, "Secret": 18, "AlbumReward": "Grand Prize: Exclusive Badge + 5000 Coins + 5x Booster Set", "GrandAlbumReward": "Grand Prize: Diamond Exclusive Badge + 10000 Coins + 10x Booster Set"}
]

SET_REWARDS_MAP = {
    row["Set"]: {
        "Name": row["Name"],
        "AlbumReward": row["AlbumReward"],
        "GrandAlbumReward": row["GrandAlbumReward"]
    }
    for row in DEFAULT_CARD_SET_REWARDS if isinstance(row["Set"], int)
}

GRAND_PRIZE_REWARDS = {
    "AlbumReward": "Grand Prize: Exclusive Badge + 5000 Coins + 5x Booster Set",
    "GrandAlbumReward": "Grand Prize: Diamond Exclusive Badge + 10000 Coins + 10x Booster Set"
}

def get_default_tuning():
    return {
        'key_stages': pd.DataFrame(DEFAULT_KEY_STAGES),
        'streak_stages': pd.DataFrame(DEFAULT_STREAK_STAGES),
        'prices': pd.DataFrame(DEFAULT_PRICES),
        'key_cadence': 7,
        'streak_cadence': 3,
        'master_pass_cadence': 30,
        'master_pass_stages': pd.DataFrame(DEFAULT_MASTER_PASS_STAGES),
        'card_set_rewards': pd.DataFrame(DEFAULT_CARD_SET_REWARDS)
    }

DEFAULT_CONFIG = {
    'sim_days': 60,
    'daily_sessions': 2,
    'levels_per_session': 2.0,
    'min_l': 1,
    'max_l': 4,
    'win_rate_n': 1.0,
    'win_rate_h': 0.90,
    'win_rate_sh': 0.80,
    'rv_watch_rate': 0.25,
    'rv_multiplier': 3.0,
    'booster_use_rate': 0.0,
    'revive_buy_rate': 0.10,
    'enable_keys': True,
    'enable_streak': True,
    'enable_mp': True,
    'mp_tier': 'Free',
    'enable_core_packs': False,
    'enable_card_rush': True,
    'enable_chest_drop': True,
    'enable_auto_star_chest': True
}


