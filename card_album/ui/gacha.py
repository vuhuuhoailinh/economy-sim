import pandas as pd
import streamlit as st
import altair as alt

from ..config import (
    MAX_CARDS,
    PACK_ICONS,
    PACK_ORDER,
    PACKS,
    RARITIES,
    TOTAL_CARDS,
)
from ..gacha import build_rate_rows, get_pity_bonus, open_bulk_packs, open_pack, open_chest, rarity_label
from ..state import ensure_album_state, reset_progress, total_cards_collected
from ..liveops_simulator import simulate_liveops

from .utils import format_card_name_ui

def render_pity_panel(selected_pack: str) -> None:
    st.subheader("Pity Stats")
    _, pity_message = get_pity_bonus(st.session_state, selected_pack)
    st.markdown(f"**Selected Pack ({selected_pack}):** `{pity_message}`")
    pity_data = {p: misses for p, misses in st.session_state["pack_pity"].items() if misses > 0}
    if pity_data:
        st.caption("Pity Accumulation (Consecutive misses per pack):")
        cols = st.columns(4)
        for i, (pack, misses) in enumerate(pity_data.items()):
            cols[i % 4].metric(pack, f"{misses} misses")
    else:
        st.caption("No active pity accumulated.")

    pity_rules = []
    for pack_name, pack_config in st.session_state["config_packs"].items():
        if pack_config["pity_threshold"] > 0 and pack_config["pity_increment"] > 0:
            if "+" not in pack_name:
                incr_percent = int(pack_config["pity_increment"] * 100)
                pity_rules.append(f"{pack_name} ({pack_config['pity_threshold']} misses: +{incr_percent}%)")
                
    if pity_rules:
        st.caption(f"*Pity mechanics (Consecutive misses): {', '.join(pity_rules)}*")

def render_ss2_pity_panel() -> None:
    if st.session_state.get("ss2_optimize_collection", True):
        from ..gacha import get_ss2_pity_info
        info = get_ss2_pity_info(st.session_state)
        
        st.subheader("SS2 Collection Optimization")
        
        c1, c2, c3 = st.columns([1, 1.2, 1.5])
        with c1:
            st.metric("Completed Sets", f"{info['completed_sets']}/{info['total_sets']}")
            st.caption(f"Album Need Factor (Pity Set): **{info['pity_set']*100:.1f}%**")
        with c2:
            st.metric("Closest Set", info['best_set_name'] if info['best_set_id'] else "None")
            st.caption(f"Progress: **{info['best_set_owned']}/{info['best_set_total']} cards**" if info['best_set_id'] else "")
            
        with c3:
            if info['missing_details']:
                st.markdown(f"**Dynamic Rate Breakdown ({info['best_set_name']}):**")
                for detail in info['missing_details']:
                    rarity = detail['rarity']
                    r_label = f"{rarity}⭐" if rarity < 6 else "Gold (6⭐)"
                    st.caption(
                        f"- Missing **{detail['missing_count']} {r_label} cards** -> "
                        f"Targeted Chance: **{detail['final_chance']*100:.1f}%** "
                        f"*(Pity Rarity: {detail['pity_rarity']*100:.1f}%)*"
                    )


@st.dialog("Cards Drawn", width="large")
def show_draw_result_dialog(res: dict):
    st.markdown("""
        <style>
            /* Hack to make the dialog wider on desktop screens */
            div[data-testid="stDialog"] div[role="dialog"] {
                width: 85vw !important;
                max-width: 1200px !important;
            }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown(f"**Successfully Opened: {res.get('summary', '')}**")
    if "bulk_summary" in res:
        bs = res["bulk_summary"]
        st.info(f"Bulk Chest Upgrade Summary: Max tier reached: 2⭐ ({bs.get(2,0)} times), 3⭐ ({bs.get(3,0)} times), 4⭐ ({bs.get(4,0)} times), 5⭐ ({bs.get(5,0)} times)")
    else:
        st.info(f"Total Cards Drawn: +{res.get('total_cards', 0)} | ⭐ Stars Gained: +{res.get('stars_diff', 0)}")
    
    rarity_colors = {
        1: "#B0C4DE", 2: "#32CD32", 3: "#1E90FF",
        4: "#9370DB", 5: "#FFA500", 6: "#FFD700"
    }
    
    def render_card_html(card, is_new):
        from ..config import CARD_SETS
        from ..gacha import STAR_VALUES
        if not card: return ""
        set_id, r, idx = card
        cname = f"{CARD_SETS[set_id]['name']} #{idx+1}"
        color = rarity_colors.get(r, "gray")
        icon = "⭐" * r if r < 6 else "Gold (6⭐)"
        
        box_shadow = f"box-shadow: 0 0 15px {color};" if is_new else ""
        opacity = "1.0" if is_new else "0.6"
        
        if color.startswith("#") and len(color) == 7:
            r_val, g_val, b_val = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
            bg = f"rgba({r_val}, {g_val}, {b_val}, 0.15)"
        else:
            bg = "rgba(128, 128, 128, 0.15)"
            
        badge = f"<div style='position:absolute; top:-10px; right:-10px; background:#ef4444; color:white; font-size:0.7em; padding:2px 6px; border-radius:10px; font-weight:bold; box-shadow: 0 0 5px #ef4444;'>NEW</div>" if is_new else f"<div style='position:absolute; top:-10px; right:-10px; background:gray; color:white; font-size:0.7em; padding:2px 6px; border-radius:10px; font-weight:bold;'>+{STAR_VALUES[r]}⭐</div>"
        
        return f"<div style='position:relative; width: 100px; height: 130px; border: 2px solid {color}; border-radius: 8px; padding: 5px; text-align: center; background: {bg}; {box_shadow} opacity: {opacity}; display: flex; flex-direction: column; justify-content: space-between;'>{badge}<div style='font-size: 0.8em; margin-top: 10px;'>{icon}</div><div style='font-size: 0.75em; font-weight: bold; line-height: 1.2; word-wrap: break-word; margin-bottom: 5px;'>{cname}</div></div>"
        
    new_cards = res.get("new_cards_list", [])
    dup_cards = res.get("dup_cards_list", [])
    
    if new_cards:
        st.markdown("<h3>New Cards</h3>", unsafe_allow_html=True)
        html_parts = [render_card_html(c, True) for c in new_cards]
        st.markdown("<div style='display: flex; flex-wrap: wrap; justify-content: center; gap: 15px; margin-bottom: 20px;'>" + "".join(html_parts) + "</div>", unsafe_allow_html=True)
        
    if dup_cards:
        st.markdown("<h3>Duplicate Cards (Converted to ⭐)</h3>", unsafe_allow_html=True)
        html_parts = [render_card_html(c, False) for c in dup_cards]
        st.markdown("<div style='display: flex; flex-wrap: wrap; justify-content: center; gap: 15px;'>" + "".join(html_parts) + "</div>", unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Collect", use_container_width=True, type="primary"):
        st.rerun()


def render_pack_opener_tab() -> None:
    with st.container(border=True):
        st.subheader("Pack Opening Overview")
        col_stats1, col_stats2, col_stats3, col_stats4, col_stats5 = st.columns(5)
        
        rarity_colors = {
            1: "gray", 2: "#32CD32", 3: "#1E90FF",
            4: "#9370DB", 5: "#FFA500", 6: "#FF1493"
        }
        
        def st_color_tier(r):
            colors = {1: "gray", 2: "green", 3: "blue", 4: "violet", 5: "orange", 6: "red"}
            c = colors.get(int(r), "gray")
            label = f"{r}⭐" if int(r) < 6 else "Gold (6⭐)"
            return f":{c}[{label}]"

        
        new_total = st.session_state.get('new_cards_drawn', 0)
        new_dict = st.session_state.get('new_cards_by_rarity', {})
        new_parts = []
        for r in range(1, 7):
            if new_dict.get(r, 0) > 0:
                icon = "⭐" if r < 6 else "⭐ (Gold)"
                new_parts.append(f"<span style='color:{rarity_colors[r]}'>{r}{icon}: {new_dict[r]}</span>")
        new_detail = f"<div style='font-size:0.85em; margin-top:-10px; color:#aaa'>({', '.join(new_parts)})</div>" if new_parts else ""

        dup_total = st.session_state.get('dup_cards_drawn', 0)
        dup_dict = st.session_state.get('dup_cards_by_rarity', {})
        dup_parts = []
        for r in range(1, 7):
            if dup_dict.get(r, 0) > 0:
                icon = "⭐" if r < 6 else "⭐ (Gold)"
                dup_parts.append(f"<span style='color:{rarity_colors[r]}'>{r}{icon}: {dup_dict[r]}</span>")
        dup_detail = f"<div style='font-size:0.85em; margin-top:-10px; color:#aaa'>({', '.join(dup_parts)})</div>" if dup_parts else ""
        
        with col_stats1:
            total_drawn = st.session_state['total_cards_drawn']
            st.metric("Total Cards Drawn", f"{total_drawn}")
        with col_stats2:
            st.metric("New Cards Drawn", f"{new_total}")
            if new_detail: st.markdown(new_detail, unsafe_allow_html=True)
        with col_stats3:
            pack_stars = st.session_state.get('pack_stars_gained', 0)
            st.metric("Duplicates (⭐ Gained)", f"{dup_total} (+{pack_stars}⭐)")
            if dup_detail: st.markdown(dup_detail, unsafe_allow_html=True)
        with col_stats4:
            st.metric("Total Packs Opened", f"{st.session_state['total_packs']}")
        with col_stats5:
            rate = (dup_total / total_drawn * 100) if total_drawn > 0 else 0
            st.metric("Duplicate Rate", f"{dup_total}/{total_drawn} ({rate:.2f}%)")
        
        st.markdown("<hr style='margin: 10px 0px; opacity: 0.3'>", unsafe_allow_html=True)
        st.caption("Packs opened breakdown:")
        pack_cols = st.columns(5)
        for i, pack in enumerate(PACK_ORDER):
            with pack_cols[i % 5]:
                icon = PACK_ICONS.get(pack, "")
                st.markdown(f"**{icon} {pack} Pack**: {st.session_state['pack_counts'][pack]}")
                
        st.markdown("<hr style='margin: 10px 0px; opacity: 0.3'>", unsafe_allow_html=True)
        render_ss2_pity_panel()
            
    st.markdown("<hr style='margin: 15px 0px; opacity: 0.3'>", unsafe_allow_html=True)
    
    col_left, col_right = st.columns([1, 1.2])
    with col_left:
        st.subheader("Card Pack Cart (Sandbox)")
        st.caption("Select the quantity of packs to open manually for testing. *(All simulation packs have already been opened and credited in the overview above)*.")
        shop_cols = st.columns(2)
        for i, pack in enumerate(PACK_ORDER):
            with shop_cols[i % 2]:
                if f"cart_input_{pack}" not in st.session_state:
                    st.session_state[f"cart_input_{pack}"] = st.session_state["cart_packs"].get(pack, 0)
                icon = PACK_ICONS.get(pack, "")
                st.number_input(f"{icon} {pack} Pack", min_value=0, max_value=10000, step=1, key=f"cart_input_{pack}")
                st.session_state["cart_packs"][pack] = st.session_state[f"cart_input_{pack}"]

        st.markdown("<br>", unsafe_allow_html=True)
        auto_chest = st.checkbox("Auto exchange surplus stars for Star Chests", key="auto_chest_chk", help="Automatically purchases the highest tier Star Chest available (Gold 500⭐ -> Silver 250⭐ -> Bronze 100⭐) until stars are below 100.")
        def execute_cart():
            res = open_bulk_packs(st.session_state, st.session_state["cart_packs"], st.session_state.get("auto_chest_chk", False))
            if not res["success"]:
                st.session_state["cart_error"] = res["message"]
            else:
                st.session_state["cart_success"] = res
        def reset_cart():
            for p in PACK_ORDER:
                st.session_state[f"cart_input_{p}"] = 0
                st.session_state["cart_packs"][p] = 0

        col_exec, col_reset = st.columns([3, 1])
        col_exec.button("Open Selected Packs", type="primary", use_container_width=True, on_click=execute_cart)
        col_reset.button("Clear Cart", use_container_width=True, on_click=reset_cart)
        if "cart_error" in st.session_state:
            st.error(st.session_state.pop("cart_error"))
        if "cart_success" in st.session_state:
            show_draw_result_dialog(st.session_state.pop("cart_success"))

        st.markdown("<hr style='margin: 15px 0px; opacity: 0.3'>", unsafe_allow_html=True)
        st.subheader(f"Star Chest Exchange ({st.session_state['stars']} ⭐)")
        st.caption("Spend surplus stars from duplicate cards to open Star Chests.")
        
        def execute_chest(chest_type):
            res = open_chest(st.session_state, chest_type)
            if res["success"]:
                st.session_state["chest_success"] = res
            else:
                st.session_state["chest_error"] = res["message"]

        chest_col1, chest_col2, chest_col3 = st.columns(3)
        chest_col1.button("Bronze Chest (100 ⭐)", use_container_width=True, on_click=execute_chest, args=("Bronze",))
        chest_col2.button("Silver Chest (250 ⭐)", use_container_width=True, on_click=execute_chest, args=("Silver",))
        chest_col3.button("Gold Chest (500 ⭐)", use_container_width=True, on_click=execute_chest, args=("Gold",))
        
        if "chest_error" in st.session_state:
            st.error(st.session_state.pop("chest_error"))
        if "chest_success" in st.session_state:
            show_draw_result_dialog(st.session_state.pop("chest_success"))

    with col_right:
        selected_pack = st.selectbox(
            "Select Pack:", 
            PACK_ORDER,
            format_func=lambda x: f"{PACK_ICONS.get(x, '')} {x} Pack".strip()
        )
        
        def execute_multi_pack(pack, count):
            res = open_bulk_packs(st.session_state, {pack: count}, False)
            if res["success"]:
                st.session_state["single_success"] = res
                st.session_state["single_success_count"] = count
                st.session_state["single_success_pack"] = pack
            else:
                st.session_state["single_error"] = res["message"]
                
        col_btn1, col_btn10 = st.columns(2)
        col_btn1.button(f"Open 1 Pack", type="primary", use_container_width=True, on_click=execute_multi_pack, args=(selected_pack, 1))
        col_btn10.button(f"Open 10 Packs", type="primary", use_container_width=True, on_click=execute_multi_pack, args=(selected_pack, 10))
        
        if "single_error" in st.session_state:
            st.error(st.session_state.pop("single_error"))
        if "single_success" in st.session_state:
            res = st.session_state.pop("single_success")
            count = st.session_state.pop("single_success_count")
            pack = st.session_state.pop("single_success_pack")
            res["summary"] = f"{count}x {pack} Pack"
            show_draw_result_dialog(res)
            
        st.markdown("<hr style='margin: 10px 0px; opacity: 0.3'>", unsafe_allow_html=True)
        render_rate_panel(selected_pack)

    st.divider()
    render_log_panel()


def render_log_panel() -> None:
    st.subheader("Pack Opening Logs")
    if st.session_state["log"]:
        latest = st.session_state["log"][0]
        if is_positive_log(latest):
            st.success(f"**[LATEST]** {latest}")
        else:
            st.warning(f"**[LATEST]** {latest}")

    with st.expander("Full Log History", expanded=True):
        log_container = st.container(height=400)
        for entry in st.session_state["log"][1:]:
            if is_positive_log(entry):
                log_container.success(entry)
            elif "====" in entry:
                log_container.markdown(f"**{entry}**")
            else:
                log_container.warning(entry)

        if not st.session_state["log"]:
            log_container.info("No packs opened yet. Use the cart or single pack buttons above.")


def render_rate_panel(selected_pack: str) -> None:
    icon = PACK_ICONS.get(selected_pack, "")
    header_pack = f"{icon} {selected_pack} Pack".strip()
    st.subheader(f"Dynamic Odds: {header_pack}")

    if selected_pack == "Rainbow":
        st.info(
            "**Rainbow Pack Mechanics:**\n"
            "- Pack contains 6 cards total (first 5 cards drawn with boosted high-rarity rates).\n"
            "- The 6th card is 100% guaranteed to be a NEW card.\n"
            "- Prioritizes completing Gold Cards (6⭐) first.\n"
            "- If all 18 Gold cards are collected, completes random missing cards."
        )
        return

    effective_size = PACKS[selected_pack].size
    rows = build_rate_rows(st.session_state, selected_pack)
    df_rows = pd.DataFrame(rows)
    # Rename Vietnamese columns to English if present
    df_rows = df_rows.rename(columns={
        "Độ Hiếm": "Rarity",
        "Trọng Số": "Weight",
        "Tỉ Lệ Rơi": "Drop Rate",
        "Thẻ MỚI": "New Card Chance",
        "Thẻ TRÙNG": "Duplicate Chance"
    })
    st.dataframe(
        df_rows, 
        use_container_width=True, 
        hide_index=True,
        column_config={
            "New Card Chance": st.column_config.Column(
                "New Card Chance",
                help="Probability of drawing a card you DO NOT own yet. Includes active Pity buff. Drops to 0% once all cards in this rarity are collected."
            ),
            "Duplicate Chance": st.column_config.Column(
                "Duplicate Chance",
                help="Formula: 100% - New Card Chance. Duplicates automatically convert into Stars based on rarity."
            )
        }
    )
        
    guaranteed_tier = PACKS[selected_pack].guaranteed_tier
    guaranteed_label = f"{guaranteed_tier}⭐" if guaranteed_tier < 6 else "Gold (6⭐)"
    caption = f"This pack contains **{effective_size} cards**. Guaranteed at least 1 **{guaranteed_label}**."
    st.caption(caption)
    
    st.divider()
    render_pity_panel(selected_pack)


def is_positive_log(entry: str) -> bool:
    return "NEW" in entry or "Rainbow" in entry or "Gold" in entry


