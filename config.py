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
    {"Stage": 4, "KeysReq": 25, "Reward": "30m Heart"},
    {"Stage": 5, "KeysReq": 33, "Reward": "1x Hammer"},
    {"Stage": 6, "KeysReq": 40, "Reward": "1x Scissors"},
    {"Stage": 7, "KeysReq": 52, "Reward": "Chest: 1x Hammer + 1x Broom"},
    {"Stage": 8, "KeysReq": 67, "Reward": "30m x2 Key"},
    {"Stage": 9, "KeysReq": 77, "Reward": "100 Coins"},
    {"Stage": 10, "KeysReq": 89, "Reward": "1x Scissors"},
    {"Stage": 11, "KeysReq": 99, "Reward": "1x Broom"},
    {"Stage": 12, "KeysReq": 111, "Reward": "1x Hammer"},
    {"Stage": 13, "KeysReq": 126, "Reward": "Chest: 30m Heart + 1x Hammer + 1x Scissors"},
    {"Stage": 14, "KeysReq": 138, "Reward": "1x Broom"},
    {"Stage": 15, "KeysReq": 154, "Reward": "30m x2 Key"},
    {"Stage": 16, "KeysReq": 164, "Reward": "1x Hammer"},
    {"Stage": 17, "KeysReq": 176, "Reward": "1x Broom"},
    {"Stage": 18, "KeysReq": 192, "Reward": "400 Coins"},
    {"Stage": 19, "KeysReq": 204, "Reward": "1x Scissors"},
    {"Stage": 20, "KeysReq": 214, "Reward": "1h Heart"},
    {"Stage": 21, "KeysReq": 229, "Reward": "1x Broom"},
    {"Stage": 22, "KeysReq": 241, "Reward": "1x Scissors"},
    {"Stage": 23, "KeysReq": 259, "Reward": "1h x2 Key"},
    {"Stage": 24, "KeysReq": 279, "Reward": "Chest: 1h Heart, 1x Boosters Set"},
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
    {"WinsReq": 2, "Reward": "40 coins"},
    {"WinsReq": 5, "Reward": "15m Heart + 1x Bronze pack"},
    {"WinsReq": 8, "Reward": "1x Emerald pack"},
    {"WinsReq": 11, "Reward": "1x Scissors"},
    {"WinsReq": 14, "Reward": "1x Silver pack"},
    {"WinsReq": 18, "Reward": "15m Heart + 80 Coins"},
    {"WinsReq": 24, "Reward": "1x Amethyst Pack"},
    {"WinsReq": 30, "Reward": "2x Hammer + 30m heart"},
    {"WinsReq": 36, "Reward": "300 coins + Ruby Pack + 1 Broom"}
]

def get_default_tuning():
    return {
        'key_stages': pd.DataFrame(DEFAULT_KEY_STAGES),
        'streak_stages': pd.DataFrame(DEFAULT_STREAK_STAGES),
        'prices': pd.DataFrame(DEFAULT_PRICES),
        'key_cadence': 7,
        'streak_cadence': 3,
        'master_pass_cadence': 30,
        'master_pass_stages': pd.DataFrame(DEFAULT_MASTER_PASS_STAGES)
    }
