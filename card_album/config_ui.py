import pandas as pd
import streamlit as st
from .config_manager import export_config_to_json, import_config_from_json, load_config_to_state
from .config import PACK_ICONS

import copy

def init_draft_config():
    if "draft_config_packs" not in st.session_state:
        st.session_state["draft_config_packs"] = copy.deepcopy(st.session_state["config_packs"])
    if "draft_config_rewards" not in st.session_state:
        st.session_state["draft_config_rewards"] = copy.deepcopy(st.session_state["config_rewards"])
    if "draft_new_card_formula_type" not in st.session_state:
        st.session_state["draft_new_card_formula_type"] = st.session_state.get("new_card_formula_type", "simple")
    if "draft_new_card_power" not in st.session_state:
        st.session_state["draft_new_card_power"] = st.session_state.get("new_card_power", 3.0)
    if "draft_chest_drop_x" not in st.session_state:
        st.session_state["draft_chest_drop_x"] = st.session_state.get("config_chest_drop_x", 2.0)
    if "draft_config_chest_drop_tiers" not in st.session_state:
        st.session_state["draft_config_chest_drop_tiers"] = copy.deepcopy(st.session_state.get("config_chest_drop_tiers", {}))
    if "draft_config_chest_upgrade_matrix" not in st.session_state:
        st.session_state["draft_config_chest_upgrade_matrix"] = copy.deepcopy(st.session_state.get("config_chest_upgrade_matrix", {}))

def clear_draft_config():
    keys_to_clear = [
        "draft_config_packs", "draft_config_rewards", 
        "draft_new_card_formula_type", "draft_new_card_power",
        "draft_chest_drop_x", "draft_config_chest_drop_tiers", "draft_config_chest_upgrade_matrix",
        "draft_config_packs", "draft_config_rewards",
        "reward_editor_master_pass_free", "reward_editor_master_pass_premium", "reward_editor_win_streak_rewards",
        "reward_editor_key_collection_rewards", "chest_drop_tiers_editor", "chest_upgrade_matrix_editor"
    ]
    for key in keys_to_clear:
        st.session_state.pop(key, None)

def render_config_tab():
    init_draft_config()
    st.header("Card Album Tuning")
    if st.session_state.pop("show_config_success", False):
        st.success("Configuration changes applied successfully!")

    st.markdown("Fine-tune the entire card economy system, from card drop rates and pity mechanisms to chest drops and collection optimizations.")
    
    col_apply, col1, col2, col3 = st.columns(4)
    
    with col_apply:
        applied = st.button("Apply Configuration", type="primary", use_container_width=True)
            
    with col1:
        if st.button("Reset Defaults", use_container_width=True):
            load_config_to_state(st.session_state, None)
            clear_draft_config()
            st.success("Default configuration restored successfully!")
            st.rerun()

    with col2:
        json_str = export_config_to_json(st.session_state)
        st.download_button(
            label="Export JSON",
            data=json_str,
            file_name="economy_config.json",
            mime="application/json",
            use_container_width=True
        )
    
    with col3:
        uploaded_file = st.file_uploader("Import JSON", type=["json"], label_visibility="collapsed")
        if uploaded_file is not None:
            content = uploaded_file.getvalue().decode("utf-8")
            if st.session_state.get("last_uploaded_json") != content:
                st.session_state["last_uploaded_json"] = content
                if import_config_from_json(st.session_state, content):
                    clear_draft_config()
                    st.toast("Config imported successfully!")
                    st.rerun()
                else:
                    st.error("Invalid config file!")

    st.divider()

    with st.expander("System Configuration Guide & Drop Rate Formulas", expanded=False):
        st.markdown("""
        **1. New Card Drop Probability Formula:**
        The game calculates new card drop chance using:
        
        `New Card Ratio = (Remaining New / Total) ^ (x + y) + Pity`
        - `x`: Global difficulty base for all packs (default = 3.0).
        - `y`: Pack-specific coefficient (configured per pack, making premium packs drop new cards more easily).
        
        **2. Pack Drop Rates Table (Weights Explanation):**
        - You can directly edit the drop rate of each Card Pack in the table below.
        - Drop rates are calculated based on **relative weights** instead of fixed percentages.
        - **Calculation Rule:** Drop chance of a rarity = `(Weight of that rarity) / (Total weights of all rarities)`.
        - **Example:**
          > If Bronze Pack has weights: 1-Star: `35`, 2-Star: `26`, 3-Star: `20`, 4-Star: `11`, 5-Star: `7`, Gold: `1`.
          > Total Weight = 35 + 26 + 20 + 11 + 7 + 1 = 100.
          > 1-Star drop chance = `35 / 100 = 35%`. Gold drop chance = `1 / 100 = 1%`.
          > If you change Gold weight from `1` to `100`, Total Weight becomes 199. Gold drop chance becomes `100 / 199 ≈ 50%`!
        
        **3. LiveOps Rewards:**
        - Reward milestones for Master Pass, Win Streak, and Key Collection can be viewed in detail under the "LiveOps Economy Tables" tab.
        
        **4. Pity System:**
        - Each pack type maintains an INDEPENDENT pity counter.
        - Each time a pack is opened without any new card, that pack's pity counter increments by 1.
        - Once consecutive misses reach `Pity Threshold` (e.g. 3 times), `Pity Incr` (e.g. +20%) is added to the New Card Ratio on the next open. More misses increase the buff progressively (up to +100%).
        
        **5. Collection Optimization (SS2):**
        When **SS2 Optimize Collection** is enabled, two mechanics are activated:
        - **First Pack Luck**: The very FIRST time any pack type is opened, it is guaranteed 100% to drop a New Card.
        - **Set Completion Pity**: Algorithmic weighting prioritizes missing cards for near-complete sets:
          > Probability = `(Set Urgency) × (Card Affordability)`.
          > **Set Urgency**: `S.Base + (S.Max - S.Base) * (1 - Completed Sets / Total Sets)`. Fewer completed sets = higher push probability (capped at S.Max).
          > **Card Affordability**: `C.Base + (C.Max - C.Base) * (5 - Rarity) / 4`. Lower rarity cards have higher completion probability (capped at C.Max for 1-Star).
        """)

    # ----------------- SYSTEM CONFIG -----------------
    st.subheader("1. New Card Drop Formula (New Card Ratio)")
    
    st.markdown("### 1. Base Gacha (Card Packs)")
    power = st.session_state["draft_new_card_power"]
    if "ui_new_power" not in st.session_state:
        st.session_state["ui_new_power"] = float(power)
    st.markdown("General Difficulty Exponent (x) in formula: **New Card Ratio = (Remaining New/Total)^(x+y) + Pity**", help="Power exponent x. Higher values make it progressively harder to obtain new cards as collection completes.")
    c1, _ = st.columns([1, 4])
    with c1:
        st.number_input("power_input", step=0.1, label_visibility="collapsed", key="ui_new_power")
    st.session_state["draft_new_card_formula_type"] = "document"
    st.caption("Note: Coefficient y depends on each pack type (configured in the table below).")
    
    st.write("")
    st.markdown("### 2. Chest Drop Mini-Game")
    
    chest_x = st.session_state["draft_chest_drop_x"]
    if "ui_chest_x" not in st.session_state:
        st.session_state["ui_chest_x"] = float(chest_x)
    st.markdown("General Difficulty Exponent for Chest Drops (x): **New Card Ratio = (Remaining New/Total)^(x+y)**", help="Exponent x for Chest Drops. Coefficient y depends directly on card rarity (1-Star y=1.0, 2-Star y=0.5, 3-Star y=0.0, 4-Star y=-0.5, 5-Star y=-1.0, 6-Star y=-1.5).")
    c2, _ = st.columns([1, 4])
    with c2:
        st.number_input("chest_power_input", step=0.1, label_visibility="collapsed", key="ui_chest_x")
    
    st.markdown("**Chest Drop Tiers Configuration:**")
    st.caption("Configure tier upgrade rates, y_value, and drop weights for each chest tier.")
    
    chest_tiers_data = []
    draft_tiers = st.session_state["draft_config_chest_drop_tiers"]
    
    for tier in range(1, 6):
        tier_str = str(tier)
        t_cfg = draft_tiers[tier_str]
        row = {
            "Chest Tier": t_cfg["name"],
            "y_value": t_cfg["y_value"],
        }
        for i in range(1, 7):
            col_name = f"Star_{i}" if i < 6 else "Gold"
            row[col_name] = t_cfg["weights"].get(str(i), 0)
        chest_tiers_data.append(row)
        
    df_chest_tiers = pd.DataFrame(chest_tiers_data)
    
    chest_col_config = {
        "Chest Tier": st.column_config.TextColumn("Chest Tier", disabled=True),
        "y_value": st.column_config.NumberColumn("y_value", help="Difficulty coefficient (y) when opening this chest."),
    }
    for i in range(1, 7):
        col_name = f"Star_{i}" if i < 6 else "Gold"
        label_help = f"{i}-Star" if i < 6 else "GOLD (6-Star)"
        chest_col_config[col_name] = st.column_config.NumberColumn(col_name, help=f"Drop weight for {label_help} rarity. Higher value = higher drop rate.")
        
    edited_chest_tiers = st.data_editor(
        df_chest_tiers,
        hide_index=True,
        use_container_width=True,
        key="chest_drop_tiers_editor",
        column_config=chest_col_config
    )
    
    st.markdown("**Chest Upgrade Probability Matrix:**")
    st.caption("Configure upgrade probability based on starting chest. Rows represent starting chest, columns represent upgrade target.")
    
    matrix_data = []
    draft_matrix = st.session_state["draft_config_chest_upgrade_matrix"]
    for stier in range(1, 6):
        row = {"Starting Chest": f"{stier}-Star"}
        for ctier in range(1, 5):
            row[f"To {ctier+1}-Star"] = float(draft_matrix[str(stier)].get(str(ctier), 0.0))
        matrix_data.append(row)
        
    df_matrix = pd.DataFrame(matrix_data)
    matrix_col_config = {"Starting Chest": st.column_config.TextColumn("Starting Chest", disabled=True)}
    for ctier in range(1, 5):
        col_name = f"To {ctier+1}-Star"
        matrix_col_config[col_name] = st.column_config.NumberColumn(col_name, min_value=0.0, max_value=1.0, step=0.01)

    edited_matrix = st.data_editor(
        df_matrix,
        hide_index=True,
        use_container_width=True,
        key="chest_upgrade_matrix_editor",
        column_config=matrix_col_config
    )

    st.divider()
    
    st.write("")
    st.markdown("### 3. Collection Optimization (SS2 Optimize Collection)")
    st.caption("Configure pity weighting when drawing new cards, helping players complete unfinished sets.")
    
    if "ui_ss2_s_base" not in st.session_state:
        st.session_state["ui_ss2_s_base"] = float(st.session_state.get("config_ss2_s_base", 0.1))
        st.session_state["ui_ss2_s_max"] = float(st.session_state.get("config_ss2_s_max", 0.5))
        st.session_state["ui_ss2_c_base"] = float(st.session_state.get("config_ss2_c_base", 0.3))
        st.session_state["ui_ss2_c_max"] = float(st.session_state.get("config_ss2_c_max", 1.0))
        
    cc1, cc2, cc3, cc4 = st.columns(4)
    with cc1:
        st.number_input("S.Base (Urgency Min)", step=0.01, key="ui_ss2_s_base", help="Minimum boost factor when many sets are completed")
    with cc2:
        st.number_input("S.Max (Urgency Max)", step=0.01, key="ui_ss2_s_max", help="Maximum boost factor when few sets are completed")
    with cc3:
        st.number_input("C.Base (Affordability Min)", step=0.01, key="ui_ss2_c_base", help="Buff factor for difficult cards (5-Star)")
    with cc4:
        st.number_input("C.Max (Affordability Max)", step=0.01, key="ui_ss2_c_max", help="Buff factor for common cards (1-Star)")

    st.divider()
    
    # ----------------- PACKS CONFIG -----------------
    st.subheader("2. Pack Drop Rates Configuration")
    st.caption("Configure card count per pack, guaranteed rarity tier, pack-specific y_value, and rarity weights.")
    packs_data = []
    
    # Store mapping to retrieve pack name cleanly from iconified name
    pack_name_mapping = {}
    
    for pack_name, p in st.session_state["draft_config_packs"].items():
        icon = PACK_ICONS.get(pack_name, "")
        display_name = f"{icon} {pack_name}".strip()
        pack_name_mapping[display_name] = pack_name
        
        row = {
            "Pack": display_name,
            "Size": p["size"],
            "Guaranteed": p["guaranteed_tier"],
            "y_value": p["y_value"],
            "Pity Threshold": p.get("pity_threshold", 0),
            "Pity Incr": p.get("pity_increment", 0.0),
        }
        for i in range(1, 7):
            col_name = f"Star_{i}" if i < 6 else "Gold"
            row[col_name] = p["weights"].get(str(i), 0)
        packs_data.append(row)
        
    df_packs = pd.DataFrame(packs_data)
    
    # Configure columns with tooltips
    col_config = {
        "Pack": st.column_config.TextColumn("Pack Name", disabled=True),
        "Size": st.column_config.NumberColumn("Size", help="Number of cards drawn from this pack."),
        "Guaranteed": st.column_config.NumberColumn("Guaranteed", help="Minimum guaranteed rarity tier (e.g., 3 guarantees at least one 3-Star card)."),
        "y_value": st.column_config.NumberColumn("y_value", help="Pack difficulty coefficient (y). Negative values make new cards easier to obtain."),
        "Pity Threshold": st.column_config.NumberColumn("Pity Threshold", help="Consecutive empty opens required to trigger pity bonus."),
        "Pity Incr": st.column_config.NumberColumn("Pity Incr", help="Drop chance bonus added upon reaching pity threshold (e.g. 0.2 = +20%)."),
    }
    for i in range(1, 7):
        col_name = f"Star_{i}" if i < 6 else "Gold"
        label_help = f"{i}-Star" if i < 6 else "GOLD (6-Star)"
        col_config[col_name] = st.column_config.NumberColumn(col_name, help=f"Drop weight for {label_help} rarity. Higher value = higher drop rate.")
        
    edited_packs = st.data_editor(df_packs, num_rows="fixed", hide_index=True, use_container_width=True, column_config=col_config, key="pack_config_editor")


    if applied:
        # Apply System Config
        new_power = st.session_state["ui_new_power"]
        st.session_state["draft_new_card_power"] = new_power
        st.session_state["new_card_formula_type"] = "document"
        st.session_state["new_card_power"] = new_power
        
        new_chest_x = st.session_state["ui_chest_x"]
        st.session_state["draft_chest_drop_x"] = new_chest_x
        st.session_state["config_chest_drop_x"] = new_chest_x
        
        st.session_state["config_ss2_s_base"] = st.session_state["ui_ss2_s_base"]
        st.session_state["config_ss2_s_max"] = st.session_state["ui_ss2_s_max"]
        st.session_state["config_ss2_c_base"] = st.session_state["ui_ss2_c_base"]
        st.session_state["config_ss2_c_max"] = st.session_state["ui_ss2_c_max"]
        
        # Apply Chest Tiers Config
        for idx, row in edited_chest_tiers.iterrows():
            tier_str = str(idx + 1)
            t = st.session_state["draft_config_chest_drop_tiers"][tier_str]
            t["y_value"] = float(row["y_value"])
            for i in range(1, 7):
                col_name = f"Star_{i}" if i < 6 else "Gold"
                t["weights"][str(i)] = int(row[col_name])
        st.session_state["config_chest_drop_tiers"] = copy.deepcopy(st.session_state["draft_config_chest_drop_tiers"])
        
        # Apply Chest Upgrade Matrix
        for idx, row in edited_matrix.iterrows():
            stier_str = str(idx + 1)
            for ctier in range(1, 5):
                col_name = f"To {ctier+1}-Star"
                st.session_state["draft_config_chest_upgrade_matrix"][stier_str][str(ctier)] = float(row[col_name])
            # Set ctier=5 to 0.0 implicitly since there is no UI for it
            st.session_state["draft_config_chest_upgrade_matrix"][stier_str]["5"] = 0.0
        st.session_state["config_chest_upgrade_matrix"] = copy.deepcopy(st.session_state["draft_config_chest_upgrade_matrix"])
        
        # Apply Packs Config
        for idx, row in edited_packs.iterrows():
            display_name = row["Pack"]
            pack_name = pack_name_mapping.get(display_name, display_name)
            p = st.session_state["draft_config_packs"][pack_name]
            p["size"] = int(row["Size"])
            p["guaranteed_tier"] = int(row["Guaranteed"])
            p["y_value"] = float(row["y_value"])
            p["pity_threshold"] = int(row["Pity Threshold"])
            p["pity_increment"] = float(row["Pity Incr"])
            for i in range(1, 7):
                col_name = f"Star_{i}" if i < 6 else "Gold"
                p["weights"][str(i)] = int(row[col_name])
        st.session_state["config_packs"] = copy.deepcopy(st.session_state["draft_config_packs"])
        
        # Removed Rewards Config application because they are now read-only
        
        st.toast("Configuration saved successfully!")
        st.session_state["show_config_success"] = True
        st.rerun()

