from .config import MAX_CARDS, PACK_ORDER


def fresh_inventory() -> dict[int, int]:
    return {rarity: 0 for rarity in MAX_CARDS}


def fresh_pack_counts() -> dict[str, int]:
    return {pack: 0 for pack in PACK_ORDER}


def ensure_album_state(session_state) -> None:
    if "config_packs" not in session_state:
        from .config_manager import load_config_to_state
        load_config_to_state(session_state)

    if "inventory" not in session_state:
        session_state["inventory"] = fresh_inventory()
    else:
        for rarity in MAX_CARDS:
            session_state["inventory"].setdefault(rarity, 0)

    if "stars" not in session_state:
        session_state["stars"] = 0
    if "total_packs" not in session_state:
        session_state["total_packs"] = 0

    if "pack_counts" not in session_state:
        session_state["pack_counts"] = fresh_pack_counts()
    else:
        for pack in PACK_ORDER:
            session_state["pack_counts"].setdefault(pack, 0)

    if "pack_pity" not in session_state:
        session_state["pack_pity"] = fresh_pack_counts()
    else:
        for pack in PACK_ORDER:
            session_state["pack_pity"].setdefault(pack, 0)

    if "log" not in session_state:
        session_state["log"] = []
    if "card_rush_enabled" not in session_state:
        session_state["card_rush_enabled"] = False
    if "grand_album_enabled" not in session_state:
        session_state["grand_album_enabled"] = True
    if "new_card_formula_type" not in session_state:
        session_state["new_card_formula_type"] = "simple"
    if "cart_packs" not in session_state:
        session_state["cart_packs"] = fresh_pack_counts()
    else:
        for pack in PACK_ORDER:
            session_state["cart_packs"].setdefault(pack, 0)
    if "owned_cards" not in session_state:
        session_state["owned_cards"] = set()
    if "total_cards_drawn" not in session_state:
        session_state["total_cards_drawn"] = 0
    if "new_cards_drawn" not in session_state:
        session_state["new_cards_drawn"] = 0
    if "dup_cards_drawn" not in session_state:
        session_state["dup_cards_drawn"] = 0
    if "pack_stars_gained" not in session_state:
        session_state["pack_stars_gained"] = 0
    if "new_cards_by_rarity" not in session_state:
        session_state["new_cards_by_rarity"] = {r: 0 for r in range(1, 7)}
    if "dup_cards_by_rarity" not in session_state:
        session_state["dup_cards_by_rarity"] = {r: 0 for r in range(1, 7)}
    
    # Chest Drop Specific Counters
    if "cd_total_cards_drawn" not in session_state:
        session_state["cd_total_cards_drawn"] = 0
    if "cd_new_cards_drawn" not in session_state:
        session_state["cd_new_cards_drawn"] = 0
    if "cd_dup_cards_drawn" not in session_state:
        session_state["cd_dup_cards_drawn"] = 0
    if "cd_stars_gained" not in session_state:
        session_state["cd_stars_gained"] = 0
    if "cd_new_cards_by_rarity" not in session_state:
        session_state["cd_new_cards_by_rarity"] = {r: 0 for r in range(1, 7)}
    if "cd_dup_cards_by_rarity" not in session_state:
        session_state["cd_dup_cards_by_rarity"] = {r: 0 for r in range(1, 7)}
    if "chest_drop_counts" not in session_state:
        session_state["chest_drop_counts"] = {r: 0 for r in range(1, 6)}
    if "cd_active_session" not in session_state:
        session_state["cd_active_session"] = None
    if "cd_history" not in session_state:
        session_state["cd_history"] = []
    if "opened_pack_types_ss2" not in session_state:
        session_state["opened_pack_types_ss2"] = set()
    if "cd_log" not in session_state:
        session_state["cd_log"] = []
    if "cd_upgrade_summary" not in session_state:
        session_state["cd_upgrade_summary"] = {t: {dest: 0 for dest in range(1, 6)} for t in range(1, 4)}
    if "cd_total_chests_opened" not in session_state:
        session_state["cd_total_chests_opened"] = 0


def reset_progress(session_state) -> None:
    keys_to_clear = [
        "inventory", "stars", "total_packs", "pack_counts", 
        "pack_pity", "log", "grand_album_completions", "grand_album_finished",
        "owned_cards", "total_cards_drawn", "new_cards_drawn", "dup_cards_drawn", "pack_stars_gained",
        "new_cards_by_rarity", "dup_cards_by_rarity",
        "cd_total_cards_drawn", "cd_new_cards_drawn", "cd_dup_cards_drawn", "cd_stars_gained",
        "cd_new_cards_by_rarity", "cd_dup_cards_by_rarity", "chest_drop_counts", "opened_pack_types_ss2",
        "cd_log", "cd_upgrade_summary", "cd_history", "cd_total_chests_opened"
    ]
    for k in keys_to_clear:
        session_state.pop(k, None)
    ensure_album_state(session_state)


def reset_season(session_state) -> None:
    session_state["inventory"] = fresh_inventory()
    session_state["owned_cards"] = set()
    session_state["stars"] = 0
    session_state["grand_album_completions"] = 0
    session_state["grand_album_finished"] = False
    session_state["pack_pity"] = fresh_pack_counts()
    session_state["opened_pack_types_ss2"] = set()
    session_state["new_cards_drawn"] = 0
    session_state["dup_cards_drawn"] = 0
    session_state["cd_new_cards_drawn"] = 0
    session_state["cd_dup_cards_drawn"] = 0
    session_state["new_cards_by_rarity"] = {r: 0 for r in range(1, 7)}
    session_state["dup_cards_by_rarity"] = {r: 0 for r in range(1, 7)}
    session_state["cd_new_cards_by_rarity"] = {r: 0 for r in range(1, 7)}
    session_state["cd_dup_cards_by_rarity"] = {r: 0 for r in range(1, 7)}
    session_state["pack_stars_gained"] = 0
    session_state["cd_stars_gained"] = 0
    session_state["cd_log"] = []
    session_state["cd_upgrade_summary"] = {t: {dest: 0 for dest in range(1, 6)} for t in range(1, 4)}
    session_state["cd_total_chests_opened"] = 0
    ensure_album_state(session_state)


def total_cards_collected(session_state) -> int:
    return sum(session_state["inventory"].values())


def sync_album_state(target_state, source_state, tot_packs_earned: dict = None) -> None:
    """
    Synchronizes full simulation state to interactive Card Album session state:
    - Card inventory, collection sets, stars, Grand Album flags
    - Gacha Sandbox: pack counts opened, pity misses, total cards drawn, pack logs
    - Chest Drop Minigame: chests opened (1-5⭐), 5-hit logs, upgrade summary matrix
    """
    ensure_album_state(target_state)

    # 1. Base Inventory & Collection
    target_state["inventory"] = source_state["inventory"].copy()
    target_state["owned_cards"] = source_state["owned_cards"].copy()
    target_state["stars"] = source_state["stars"]
    target_state["grand_album_completions"] = source_state.get("grand_album_completions", 0)
    target_state["grand_album_finished"] = source_state.get("grand_album_finished", False)
    target_state["opened_pack_types_ss2"] = set(source_state.get("opened_pack_types_ss2", set()))

    # 2. Gacha Sandbox Tracking, Pity & Logs
    target_state["total_packs"] = source_state.get("total_packs", 0)
    target_state["pack_counts"] = dict(source_state.get("pack_counts", fresh_pack_counts()))
    target_state["pack_pity"] = dict(source_state.get("pack_pity", fresh_pack_counts()))
    target_state["total_cards_drawn"] = source_state.get("total_cards_drawn", 0)
    target_state["new_cards_drawn"] = source_state.get("new_cards_drawn", 0)
    target_state["dup_cards_drawn"] = source_state.get("dup_cards_drawn", 0)
    target_state["pack_stars_gained"] = source_state.get("pack_stars_gained", 0)
    target_state["new_cards_by_rarity"] = dict(source_state.get("new_cards_by_rarity", {r: 0 for r in range(1, 7)}))
    target_state["dup_cards_by_rarity"] = dict(source_state.get("dup_cards_by_rarity", {r: 0 for r in range(1, 7)}))
    target_state["log"] = list(source_state.get("log", []))

    # 3. Chest Drop Minigame Tracking, Upgrades & Logs
    target_state["cd_total_chests_opened"] = source_state.get("cd_total_chests_opened", source_state.get("cd_total_cards_drawn", 0) // 5)
    target_state["chest_drop_counts"] = dict(source_state.get("chest_drop_counts", {r: 0 for r in range(1, 6)}))
    target_state["cd_total_cards_drawn"] = source_state.get("cd_total_cards_drawn", 0)
    target_state["cd_new_cards_drawn"] = source_state.get("cd_new_cards_drawn", 0)
    target_state["cd_dup_cards_drawn"] = source_state.get("cd_dup_cards_drawn", 0)
    target_state["cd_stars_gained"] = source_state.get("cd_stars_gained", 0)
    target_state["cd_new_cards_by_rarity"] = dict(source_state.get("cd_new_cards_by_rarity", {r: 0 for r in range(1, 7)}))
    target_state["cd_dup_cards_by_rarity"] = dict(source_state.get("cd_dup_cards_by_rarity", {r: 0 for r in range(1, 7)}))
    target_state["cd_log"] = list(source_state.get("cd_log", []))
    if "cd_upgrade_summary" in source_state:
        target_state["cd_upgrade_summary"] = {
            t: dict(dests) for t, dests in source_state["cd_upgrade_summary"].items()
        }

    # 4. Reset manual sandbox cart inputs to 0 so the user doesn't accidentally re-open packs
    if "cart_packs" in target_state:
        for p in PACK_ORDER:
            target_state["cart_packs"][p] = 0
            target_state[f"cart_input_{p}"] = 0


def log_chest_drop(session_state, action_type: str, chests_opened: int, start_tier: int, new_cards: int, dup_cards: int, upgrade_summary: dict = None) -> None:
    import datetime
    if "cd_history" not in session_state:
        session_state["cd_history"] = []
    
    entry = {
        "time": datetime.datetime.now().strftime("%H:%M:%S"),
        "type": action_type,
        "start_tier": start_tier,
        "chests": chests_opened,
        "new": new_cards,
        "dup": dup_cards,
        "upgrades": upgrade_summary or {}
    }
    session_state["cd_history"].insert(0, entry)
