import re

def parse_rewards(r_str):
    c, h, b, s = 0, 0, 0, 0
    if not isinstance(r_str, str): return c, h, b, s
    
    r_str = r_str.lower()
    
    coin_match = re.search(r'(\d+)\s*coins?', r_str)
    if coin_match: c += int(coin_match.group(1))
        
    h_match = re.search(r'(\d+)x?\s*hammer', r_str)
    if h_match: h += int(h_match.group(1))
    elif 'hammer' in r_str: h += 1
        
    b_match = re.search(r'(\d+)x?\s*broom', r_str)
    if b_match: b += int(b_match.group(1))
    elif 'broom' in r_str: b += 1
        
    s_match = re.search(r'(\d+)x?\s*scissors?', r_str)
    if s_match: s += int(s_match.group(1))
    elif 'scissors' in r_str: s += 1
        
    set_match = re.search(r'(\d+)x?\s*boosters?\s*set', r_str)
    if set_match:
        count = int(set_match.group(1))
        h += count; b += count; s += count
    elif 'boosters set' in r_str:
        h += 1; b += 1; s += 1
        
    # Card packs are collectible album cards, not direct in-game coins
    return c, h, b, s
