# FULL CODEBASE: Card Album Simulator

Tài liệu này chứa toàn bộ source code của dự án Card Album Simulator, được gom thành một file duy nhất để phục vụ việc phân tích, đọc hiểu và implement lại bởi các mô hình AI hoặc kỹ sư phần mềm.

## 📁 Danh Mục File

- `main.py` (5 dòng)
- `test_simulator.py` (24 dòng)
- `card_album/__init__.py` (1 dòng)
- `card_album/config.py` (107 dòng)
- `card_album/config_manager.py` (113 dòng)
- `card_album/config_ui.py` (348 dòng)
- `card_album/gacha.py` (642 dòng)
- `card_album/liveops_simulator.py` (434 dòng)
- `card_album/monte_carlo.py` (228 dòng)
- `card_album/rewards_data.py` (105 dòng)
- `card_album/scratch_gacha.py` (219 dòng)
- `card_album/scratch_gacha_counters.py` (35 dòng)
- `card_album/state.py` (122 dòng)
- `card_album/ui/__init__.py` (1 dòng)
- `card_album/ui/analytics.py` (225 dòng)
- `card_album/ui/chest_drop.py` (500 dòng)
- `card_album/ui/gacha.py` (351 dòng)
- `card_album/ui/inventory.py` (150 dòng)
- `card_album/ui/main.py` (137 dòng)
- `card_album/ui/utils.py` (23 dòng)

**Tổng cộng:** 20 files, 3,770 dòng code.

---

## File: `main.py`

```python
﻿from card_album.ui import run_app


if __name__ == "__main__":
    run_app()
```

---

## File: `test_simulator.py`

```python
import math
from typing import Dict, Any, List

def is_card_rush_day(day: int) -> bool:
    if day <= 0: return False
    week = (day - 1) // 7 + 1
    weekday = (day - 1) % 7 + 1
    if week <= 2: return weekday == 6
    elif 3 <= week <= 5: return weekday in (3, 6)
    else: return weekday in (1, 3, 6)

def get_day_of_level(level: int, levels_per_day: int) -> int:
    if levels_per_day <= 0: return 1
    return math.ceil(level / levels_per_day)

def upgrade_pack(pack: str, is_cr: bool) -> str:
    if is_cr and pack in ("Bronze", "Emerald", "Silver"):
        return pack + "+"
    return pack

def test():
    for d in range(1, 40):
        print(f"Day {d} (Week {(d-1)//7+1}, Day {(d-1)%7+1}): CR? {is_card_rush_day(d)}")
test()
```

---

## File: `card_album/__init__.py`

```python
"""Card Album simulator package."""
```

---

## File: `card_album/config.py`

```python
from dataclasses import dataclass


RARITIES = [1, 2, 3, 4, 5, 6]

MAX_CARDS = {1: 33, 2: 28, 3: 23, 4: 18, 5: 15, 6: 18}
STAR_VALUES = {1: 1, 2: 2, 3: 3, 4: 5, 5: 10, 6: 15}
TOTAL_CARDS = sum(MAX_CARDS.values())

RARITY_LABELS = {
    1: "Thẻ 1-Sao",
    2: "Thẻ 2-Sao",
    3: "Thẻ 3-Sao",
    4: "Thẻ 4-Sao",
    5: "Thẻ 5-Sao",
    6: "Thẻ VÀNG",
}


@dataclass(frozen=True)
class PackConfig:
    name: str
    size: int
    guaranteed_tier: int
    weights: dict[int, int]
    y_value: float
    pity_threshold: int
    pity_increment: float


PACKS = {
    "Bronze": PackConfig("Bronze", 2, 1, {1: 35, 2: 26, 3: 20, 4: 11, 5: 7, 6: 1}, 1.0, 0, 0.0),
    "Bronze+": PackConfig("Bronze+", 3, 1, {1: 35, 2: 26, 3: 20, 4: 11, 5: 7, 6: 1}, 1.0, 0, 0.0),
    "Emerald": PackConfig("Emerald", 3, 2, {1: 32, 2: 24, 3: 20, 4: 12, 5: 10, 6: 2}, 0.5, 0, 0.0),
    "Emerald+": PackConfig("Emerald+", 5, 2, {1: 32, 2: 24, 3: 20, 4: 12, 5: 10, 6: 2}, 0.5, 0, 0.0),
    "Silver": PackConfig("Silver", 4, 3, {1: 28, 2: 22, 3: 19, 4: 15, 5: 11, 6: 5}, 0.0, 3, 0.20),
    "Silver+": PackConfig("Silver+", 6, 3, {1: 28, 2: 22, 3: 19, 4: 15, 5: 11, 6: 5}, 0.0, 3, 0.20),
    "Amethyst": PackConfig("Amethyst", 5, 4, {1: 23, 2: 21, 3: 19, 4: 17, 5: 12, 6: 7}, -0.5, 3, 0.20),
    "Ruby": PackConfig("Ruby", 6, 5, {1: 18, 2: 18, 3: 19, 4: 20, 5: 15, 6: 10}, -1.0, 2, 0.33),
    "Gold": PackConfig("Gold", 6, 6, {1: 18, 2: 18, 3: 19, 4: 20, 5: 15, 6: 10}, -1.0, 2, 0.33),
    "Rainbow": PackConfig("Rainbow", 6, 6, {1: 18, 2: 18, 3: 19, 4: 20, 5: 15, 6: 10}, -1.0, 0, 0.0),
}

# The actual distribution of 135 cards into 15 sets, based on their rarities.
# Key: Set ID (1-15), Value: Dict of {rarity: count}
CARD_SETS = {
    1: {"name": "Items", "cards": {1: 8, 2: 1}},
    2: {"name": "Transport", "cards": {1: 7, 2: 2}},
    3: {"name": "Souvenirs", "cards": {1: 7, 2: 1, 3: 1}},
    4: {"name": "Cuisine", "cards": {1: 5, 2: 3, 3: 1}},
    5: {"name": "Camping", "cards": {1: 3, 2: 4, 3: 1, 4: 1}},
    6: {"name": "Beach", "cards": {1: 2, 2: 4, 3: 1, 4: 1, 5: 1}},
    7: {"name": "Retreat", "cards": {1: 1, 2: 3, 3: 2, 4: 1, 5: 1, 6: 1}},
    8: {"name": "Theme Park", "cards": {2: 4, 3: 2, 4: 1, 5: 1, 6: 1}},
    9: {"name": "Nature", "cards": {2: 3, 3: 2, 4: 1, 5: 2, 6: 1}},
    10: {"name": "Ice Nature", "cards": {2: 2, 3: 2, 4: 2, 5: 1, 6: 2}},
    11: {"name": "Museum", "cards": {2: 1, 3: 3, 4: 1, 5: 2, 6: 2}},
    12: {"name": "Culture", "cards": {3: 3, 4: 2, 5: 2, 6: 2}},
    13: {"name": "Landmark", "cards": {3: 3, 4: 2, 5: 1, 6: 3}},
    14: {"name": "Festivals", "cards": {3: 2, 4: 2, 5: 2, 6: 3}},
    15: {"name": "Wonders", "cards": {4: 4, 5: 2, 6: 3}},
}

CHEST_CONFIG = {
    "Bronze": {"cost": 100, "packs": ["Silver"]},
    "Silver": {"cost": 250, "packs": ["Amethyst", "Silver"]},
    "Gold": {"cost": 500, "packs": ["Rainbow", "Amethyst", "Silver"]}
}

PACK_ORDER = ["Bronze", "Bronze+", "Emerald", "Emerald+", "Silver", "Silver+", "Amethyst", "Ruby", "Gold", "Rainbow"]
PACK_ICONS = {
    "Bronze": "🟫",
    "Bronze+": "🟫",
    "Emerald": "🟩",
    "Emerald+": "🟩",
    "Silver": "⬜",
    "Silver+": "⬜",
    "Amethyst": "🟪",
    "Ruby": "🟥",
    "Gold": "🟨",
    "Rainbow": "🌈",
}


# Configuration for the new Chest Drop (Win Streak) mini-game
@dataclass(frozen=True)
class ChestTierConfig:
    name: str
    y_value: float
    weights: dict[int, int]

CHEST_DROP_TIERS = {
    1: ChestTierConfig("1-Sao", 1.0, {1: 100, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}),
    2: ChestTierConfig("2-Sao", 0.5, {1: 0, 2: 100, 3: 0, 4: 0, 5: 0, 6: 0}),
    3: ChestTierConfig("3-Sao", 0.0, {1: 0, 2: 0, 3: 100, 4: 0, 5: 0, 6: 0}),
    4: ChestTierConfig("4-Sao", -0.5, {1: 0, 2: 0, 3: 0, 4: 100, 5: 0, 6: 0}),
    5: ChestTierConfig("5-Sao", -1.0, {1: 0, 2: 0, 3: 0, 4: 0, 5: 60, 6: 40})
}

CHEST_UPGRADE_MATRIX = {
    1: {1: 0.35, 2: 0.20, 3: 0.15, 4: 0.10, 5: 0.0},
    2: {1: 0.0, 2: 0.35, 3: 0.20, 4: 0.15, 5: 0.0},
    3: {1: 0.0, 2: 0.0, 3: 0.20, 4: 0.15, 5: 0.0},
    4: {1: 0.0, 2: 0.0, 3: 0.0, 4: 0.15, 5: 0.0},
    5: {1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0, 5: 0.0}
}

```

---

## File: `card_album/config_manager.py`

```python
import json
import copy
from .config import PACKS, PACK_ORDER
from .rewards_data import (
    MASTER_PASS_FREE,
    MASTER_PASS_PREMIUM,
    WIN_STREAK_REWARDS,
    KEY_COLLECTION_REWARDS,
)


def get_default_config() -> dict:
    """Returns the default configuration as a dictionary."""
    # Convert PACKS to dict
    packs_dict = {}
    for name in PACK_ORDER:
        if name in PACKS:
            p = PACKS[name]
            packs_dict[name] = {
                "size": p.size,
                "guaranteed_tier": p.guaranteed_tier,
                "y_value": p.y_value,
                "pity_threshold": p.pity_threshold,
                "pity_increment": p.pity_increment,
                "weights": {str(k): v for k, v in p.weights.items()},
            }

    from .config import CHEST_DROP_TIERS, CHEST_UPGRADE_MATRIX
    chest_tiers_dict = {}
    for tier, cfg in CHEST_DROP_TIERS.items():
        chest_tiers_dict[str(tier)] = {
            "name": cfg.name,
            "y_value": cfg.y_value,
            "weights": {str(k): v for k, v in cfg.weights.items()},
        }
        
    chest_upgrade_matrix = {}
    for stier, cfg in CHEST_UPGRADE_MATRIX.items():
        chest_upgrade_matrix[str(stier)] = {str(k): v for k, v in cfg.items()}

    return {
        "packs": packs_dict,
        "chest_tiers": chest_tiers_dict,
        "chest_upgrade_matrix": chest_upgrade_matrix,
        "rewards": {
            "master_pass_free": copy.deepcopy(MASTER_PASS_FREE),
            "master_pass_premium": copy.deepcopy(MASTER_PASS_PREMIUM),
            "win_streak_rewards": copy.deepcopy(WIN_STREAK_REWARDS),
            "key_collection_rewards": copy.deepcopy(KEY_COLLECTION_REWARDS),
        },
        "system": {
            "new_card_power": 2.5,
            "new_card_formula_type": "document",
            "chest_drop_x": 2.0
        }
    }


def load_config_to_state(session_state, config_dict=None) -> None:
    """Loads a configuration dictionary into session state."""
    if config_dict is None:
        config_dict = get_default_config()

    # Load packs
    session_state["config_packs"] = config_dict["packs"]

    # Load chest tiers
    session_state["config_chest_drop_tiers"] = config_dict.get("chest_tiers", get_default_config()["chest_tiers"])
    
    # Load chest upgrade matrix
    session_state["config_chest_upgrade_matrix"] = config_dict.get("chest_upgrade_matrix", get_default_config()["chest_upgrade_matrix"])

    # Load rewards (convert keys back to int if they were strings from JSON)
    rewards = config_dict["rewards"]
    session_state["config_rewards"] = {
        "master_pass_free": {int(k): v for k, v in rewards["master_pass_free"].items()},
        "master_pass_premium": {int(k): v for k, v in rewards["master_pass_premium"].items()},
        "win_streak_rewards": {int(k): v for k, v in rewards["win_streak_rewards"].items()},
        "key_collection_rewards": {int(k): v for k, v in rewards["key_collection_rewards"].items()},
    }
    
    if "system" in config_dict:
        session_state["new_card_power"] = config_dict["system"].get("new_card_power", 3.0)
        session_state["new_card_formula_type"] = config_dict["system"].get("new_card_formula_type", "simple")
        session_state["config_chest_drop_x"] = config_dict["system"].get("chest_drop_x", 2.0)


def export_config_to_json(session_state) -> str:
    """Exports current session state config to JSON string."""
    config_dict = {
        "packs": session_state["config_packs"],
        "chest_tiers": session_state.get("config_chest_drop_tiers", get_default_config()["chest_tiers"]),
        "chest_upgrade_matrix": session_state.get("config_chest_upgrade_matrix", get_default_config()["chest_upgrade_matrix"]),
        "rewards": session_state["config_rewards"],
        "system": {
            "new_card_power": session_state.get("new_card_power", 3.0),
            "new_card_formula_type": session_state.get("new_card_formula_type", "simple"),
            "chest_drop_x": session_state.get("config_chest_drop_x", 2.0)
        }
    }
    return json.dumps(config_dict, indent=4, ensure_ascii=False)


def import_config_from_json(session_state, json_str: str) -> bool:
    """Imports configuration from a JSON string into session state. Returns True if successful."""
    try:
        config_dict = json.loads(json_str)
        if "packs" not in config_dict or "rewards" not in config_dict:
            return False
        load_config_to_state(session_state, config_dict)
        return True
    except Exception:
        return False
```

---

## File: `card_album/config_ui.py`

```python
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
    st.header("⚙️ Economy Tuning")
    if st.session_state.pop("show_config_success", False):
        st.success("✅ Đã áp dụng các thay đổi cấu hình lên hệ thống!")

    st.markdown("Tab này cho phép tinh chỉnh toàn bộ hệ thống nền kinh tế, từ tỉ lệ rớt thẻ đến phần thưởng của các sự kiện.")
    
    col_apply, col1, col2, col3 = st.columns(4)
    
    with col_apply:
        applied = st.button("✅ Áp dụng Cấu hình", type="primary", use_container_width=True)
            
    with col1:
        if st.button("🔄 Khôi phục (Reset)", use_container_width=True):
            load_config_to_state(st.session_state, None)
            clear_draft_config()
            st.success("Đã khôi phục cài đặt gốc!")
            st.rerun()

    with col2:
        json_str = export_config_to_json(st.session_state)
        st.download_button(
            label="💾 Tải (Export JSON)",
            data=json_str,
            file_name="economy_config.json",
            mime="application/json",
            use_container_width=True
        )
    
    with col3:
        uploaded_file = st.file_uploader("📂 Tải lên (Import JSON)", type=["json"], label_visibility="collapsed")
        if uploaded_file is not None:
            content = uploaded_file.getvalue().decode("utf-8")
            if st.session_state.get("last_uploaded_json") != content:
                st.session_state["last_uploaded_json"] = content
                if import_config_from_json(st.session_state, content):
                    clear_draft_config()
                    st.toast("✅ Tải Config thành công!")
                    st.rerun()
                else:
                    st.error("File Config không hợp lệ!")

    st.divider()

    with st.expander("📖 Hướng dẫn cấu hình Hệ thống & Công thức Tỉ lệ", expanded=False):
        st.markdown("""
        **1. Công thức tính cơ hội rớt Thẻ Mới:**
        Game hiện tại áp dụng công thức sau để tính tỉ lệ ra thẻ mới:
        
        `New Card Ratio = (Remaining New/Total)^(x+y) + Pity`
        - `x`: Base for all pack, default = 3
        - `y`: Base each pack (Cấu hình riêng trong từng gói thẻ giúp gói thẻ xịn dễ rớt thẻ mới hơn)
        
        **2. Giải thích Bảng Tỉ lệ Gói Thẻ (Packs Config):**
        - Bạn hoàn toàn có thể **chỉnh sửa tỉ lệ rớt thẻ** của từng Gói Thẻ ngay trong bảng bên dưới.
        - Tỉ lệ rớt được hệ thống tính toán dựa trên **Trọng số (Weights)** thay vì % tuyệt đối. (Bạn có thể rê chuột vào tiêu đề cột để xem chú thích).
        - **Quy tắc tính:** Cơ hội rớt của một độ hiếm = (Trọng số của độ hiếm đó) / (Tổng trọng số của tất cả các độ hiếm).
        - **Ví dụ rõ ràng:**
          > Nếu Gói Bronze được cấu hình Trọng số là: 1-Sao: `35`, 2-Sao: `26`, 3-Sao: `20`, 4-Sao: `11`, 5-Sao: `7`, Gold: `1`.
          > Khi đó, Tổng trọng số = 35 + 26 + 20 + 11 + 7 + 1 = 100.
          > 👉 Tỉ lệ rớt thẻ 1-Sao sẽ là `35 / 100 = 35%`. Tỉ lệ thẻ Gold là `1 / 100 = 1%`.
          > Nếu bạn sửa số thẻ Gold từ `1` thành `100`, Tổng trọng số sẽ tăng lên thành 199. Lúc này tỉ lệ rớt thẻ Gold cực cao, chiếm `100 / 199 ≈ 50%`!
        
        **3. Bảng Phần thưởng (Rewards):**
        - Bảng phần thưởng bao gồm các mốc thưởng trong Master Pass, Win Streak, và Key Collection (Chỉ đọc).
        - Hệ thống sẽ tự động quét từ khóa `Pack` và gắn icon 📦 để bạn dễ nhận biết đâu là mốc nhận thẻ.
        
        **4. Cơ chế Bảo hiểm (Pity System):**
        - Mỗi gói thẻ sẽ có bộ đếm bảo hiểm (Pity) chạy hoàn toàn ĐỘC LẬP với nhau.
        - Mỗi khi bạn mở một gói thẻ và tạch (không ra thẻ mới), bộ đếm của loại gói đó sẽ tăng lên 1.
        - Khi tạch đến ngưỡng `Pity Threshold` (vd: 3 lần), hệ thống sẽ buff thêm `Pity Incr` (vd: +20%) vào Tỉ lệ ra thẻ mới ở lần mở gói tiếp theo. Càng tạch nhiều, buff càng to (Tối đa +100%).
        
        **5. Cơ chế Tối ưu Bộ Sưu Tập (SS2):**
        Khi bật tính năng **SS2 Optimize Collection**, game sẽ kích hoạt 2 cơ chế:
        - **First Pack Luck**: Lần ĐẦU TIÊN mở bất kỳ Gói thẻ nào, chắc chắn 100% rớt Thẻ Mới.
        - **Set Completion Pity**: Bàn tay vô hình nhét thẻ bạn thiếu vào set gần hoàn thành nhất. Xác suất = (Độ mót của Album) × (Độ rẻ của Thẻ).
          > **Độ mót (Pity Set)**: `S.Base + (S.Max - S.Base) * (1 - Số Set Xong / Tổng Set)`. Càng xong ít Set, xác suất nhét bài càng cao (Max bằng S.Max).
          > **Độ rẻ (Pity Rarity)**: `C.Base + (C.Max - C.Base) * (5 - Rarity) / 4`. Thẻ càng rẻ (ít Sao) thì xác suất nhét vào set càng cao (Max bằng C.Max đối với thẻ 1-sao).
        """)

    # ----------------- SYSTEM CONFIG -----------------
    st.subheader("⚙️ Công Thức Rớt Thẻ Mới (New Card Ratio)")
    
    st.markdown("### 1. Gacha Cơ Bản (Mở Gói)")
    power = st.session_state["draft_new_card_power"]
    if "ui_new_power" not in st.session_state:
        st.session_state["ui_new_power"] = float(power)
    st.markdown("Hệ số Khó chung (x) theo công thức: **New Card Ratio = (Remaining New/Total)^(x+y) + Pity**", help="Hệ số lũy thừa x. Giá trị càng cao, khi bạn sưu tập được càng nhiều thẻ thì cơ hội ra thẻ mới càng nhỏ.")
    c1, _ = st.columns([1, 4])
    with c1:
        st.number_input("power_input", step=0.1, label_visibility="collapsed", key="ui_new_power")
    st.session_state["draft_new_card_formula_type"] = "document"
    st.caption("Lưu ý: Hệ số y sẽ phụ thuộc vào từng loại Pack (Cấu hình ở bảng bên dưới).")
    
    st.write("")
    st.markdown("### 2. Đập Rương (Chest Drop)")
    
    chest_x = st.session_state["draft_chest_drop_x"]
    if "ui_chest_x" not in st.session_state:
        st.session_state["ui_chest_x"] = float(chest_x)
    st.markdown("Hệ số Khó chung của Đập Rương (x): **New Card Ratio = (Remaining New/Total)^(x+y)**", help="Hệ số x cho Đập Rương. Hệ số y sẽ phụ thuộc trực tiếp vào độ hiếm của thẻ (1-Sao y=1.0, 2-Sao y=0.5, 3-Sao y=0.0, 4-Sao y=-0.5, 5-Sao y=-1.0, 6-Sao y=-1.5).")
    c2, _ = st.columns([1, 4])
    with c2:
        st.number_input("chest_power_input", step=0.1, label_visibility="collapsed", key="ui_chest_x")
    
    st.markdown("**Bảng Cấu Hình Tỉ Lệ Đập Rương (Chest Drop Tiers):**")
    st.caption("Cấu hình tỉ lệ thăng cấp, hệ số y_value và trọng số rớt thẻ (weights) cho từng cấp rương.")
    
    chest_tiers_data = []
    draft_tiers = st.session_state["draft_config_chest_drop_tiers"]
    
    for tier in range(1, 6):
        tier_str = str(tier)
        t_cfg = draft_tiers[tier_str]
        row = {
            "Cấp Rương": t_cfg["name"],
            "y_value": t_cfg["y_value"],
        }
        for i in range(1, 7):
            col_name = f"Star_{i}" if i < 6 else "Gold"
            row[col_name] = t_cfg["weights"].get(str(i), 0)
        chest_tiers_data.append(row)
        
    df_chest_tiers = pd.DataFrame(chest_tiers_data)
    
    chest_col_config = {
        "Cấp Rương": st.column_config.TextColumn("Cấp Rương", disabled=True),
        "y_value": st.column_config.NumberColumn("y_value", help="Hệ số độ khó (y) khi đập rương này."),
    }
    for i in range(1, 7):
        col_name = f"Star_{i}" if i < 6 else "Gold"
        label_help = f"{i}-Sao" if i < 6 else "Thẻ VÀNG (6-Sao)"
        chest_col_config[col_name] = st.column_config.NumberColumn(col_name, help=f"Trọng số bốc trúng độ hiếm {label_help}. Số càng to tỉ lệ càng cao.")
        
    edited_chest_tiers = st.data_editor(
        df_chest_tiers,
        hide_index=True,
        use_container_width=True,
        key="chest_drop_tiers_editor",
        column_config=chest_col_config
    )
    
    st.markdown("**Bảng Tỉ Lệ Thăng Cấp Rương:**")
    st.caption("Cấu hình tỉ lệ thăng cấp phụ thuộc vào rương khởi đầu. Dòng là rương khởi đầu, Cột là rương hiện tại.")
    
    matrix_data = []
    draft_matrix = st.session_state["draft_config_chest_upgrade_matrix"]
    for stier in range(1, 6):
        row = {"Rương Khởi Đầu": f"{stier}-Sao"}
        for ctier in range(1, 5):
            row[f"Lên {ctier+1}-Sao"] = float(draft_matrix[str(stier)].get(str(ctier), 0.0))
        matrix_data.append(row)
        
    df_matrix = pd.DataFrame(matrix_data)
    matrix_col_config = {"Rương Khởi Đầu": st.column_config.TextColumn("Rương Khởi Đầu", disabled=True)}
    for ctier in range(1, 5):
        col_name = f"Lên {ctier+1}-Sao"
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
    st.markdown("### 3. Tối ưu Bộ Sưu Tập (SS2 Optimize Collection)")
    st.caption("Cấu hình tỉ lệ rớt bù (Pity) khi mở thẻ mới, giúp người chơi dễ dàng hoàn thành Set đang dở.")
    
    if "ui_ss2_s_base" not in st.session_state:
        st.session_state["ui_ss2_s_base"] = float(st.session_state.get("config_ss2_s_base", 0.1))
        st.session_state["ui_ss2_s_max"] = float(st.session_state.get("config_ss2_s_max", 0.5))
        st.session_state["ui_ss2_c_base"] = float(st.session_state.get("config_ss2_c_base", 0.3))
        st.session_state["ui_ss2_c_max"] = float(st.session_state.get("config_ss2_c_max", 1.0))
        
    cc1, cc2, cc3, cc4 = st.columns(4)
    with cc1:
        st.number_input("S.Base (Độ mót Min)", step=0.01, key="ui_ss2_s_base", help="Hệ số bù thấp nhất khi đã xong nhiều Set")
    with cc2:
        st.number_input("S.Max (Độ mót Max)", step=0.01, key="ui_ss2_s_max", help="Hệ số bù cao nhất khi chưa xong Set nào")
    with cc3:
        st.number_input("C.Base (Độ rẻ Min)", step=0.01, key="ui_ss2_c_base", help="Hệ số buff đối với Thẻ khó ra (Thẻ 5-Sao)")
    with cc4:
        st.number_input("C.Max (Độ rẻ Max)", step=0.01, key="ui_ss2_c_max", help="Hệ số buff đối với Thẻ siêu dễ (Thẻ 1-Sao)")

    st.divider()
    
    # ----------------- PACKS CONFIG -----------------
    st.subheader("🎲 Tỉ lệ rớt của các Gói Thẻ")
    st.caption("Cấu hình số thẻ trong mỗi gói, thẻ bảo hiểm, hệ số rớt (y_value) và trọng số (weights) của từng độ hiếm.")
    packs_data = []
    
    # Store mapping to retrieve pack name cleanly from iconified name
    pack_name_mapping = {}
    
    for pack_name, p in st.session_state["draft_config_packs"].items():
        icon = PACK_ICONS.get(pack_name, "")
        display_name = f"{icon} {pack_name}"
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
        "Pack": st.column_config.TextColumn("Tên Gói", disabled=True),
        "Size": st.column_config.NumberColumn("Size", help="Số lượng thẻ rút ra từ gói này."),
        "Guaranteed": st.column_config.NumberColumn("Guaranteed", help="Độ hiếm tối thiểu được bảo đảm (Ví dụ: 3 là có ít nhất 1 thẻ 3-Sao)."),
        "y_value": st.column_config.NumberColumn("y_value", help="Hệ số độ khó riêng (y) của gói (Chỉ dùng cho Công thức Tài liệu). Âm = rớt thẻ dễ hơn."),
        "Pity Threshold": st.column_config.NumberColumn("Pity Threshold", help="Số lần mở gói xịt liên tiếp để kích hoạt Pity."),
        "Pity Incr": st.column_config.NumberColumn("Pity Incr", help="% cơ hội cộng thêm khi đạt ngưỡng Pity (VD: 0.2 = +20%)."),
    }
    for i in range(1, 7):
        col_name = f"Star_{i}" if i < 6 else "Gold"
        label_help = f"{i}-Sao" if i < 6 else "Thẻ VÀNG (6-Sao)"
        col_config[col_name] = st.column_config.NumberColumn(col_name, help=f"Trọng số bốc trúng độ hiếm {label_help}. Số càng to tỉ lệ càng cao.")
        
    edited_packs = st.data_editor(df_packs, num_rows="fixed", hide_index=True, use_container_width=True, column_config=col_config, key="pack_config_editor")

    st.divider()

    # ----------------- REWARDS CONFIG -----------------
    def render_reward_viewer(title: str, config_key: str, key_col: str):
        st.subheader(title)
        data_dict = st.session_state["config_rewards"][config_key]
        df = pd.DataFrame(list(data_dict.items()), columns=[key_col, "Reward"])
        # Add visual helper column for packs
        df["Có Pack?"] = df["Reward"].apply(lambda x: "📦" if "Pack" in str(x) else "")
        
        st.dataframe(df, hide_index=True, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        render_reward_viewer("🎁 Master Pass (Free)", "master_pass_free", "Level")
        render_reward_viewer("🔥 Win Streak", "win_streak_rewards", "Wins")
    with c2:
        render_reward_viewer("👑 Master Pass (Premium)", "master_pass_premium", "Level")
        render_reward_viewer("🔑 Key Collection", "key_collection_rewards", "Stage")

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
                col_name = f"Lên {ctier+1}-Sao"
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
        
        st.toast("✅ Cấu hình đã được lưu thành công!")
        st.session_state["show_config_success"] = True
        st.rerun()

```

---

## File: `card_album/gacha.py`

```python
import random

from .config import (
    MAX_CARDS,
    PACK_ORDER,
    RARITY_LABELS,
    STAR_VALUES,
    TOTAL_CARDS,
    CARD_SETS,
    CHEST_CONFIG,
)
from .state import total_cards_collected

def rarity_label(rarity: int) -> str:
    return RARITY_LABELS[rarity]



def get_pity_bonus(session_state, pack_type: str) -> tuple[float, str]:
    if session_state.get("total_packs", 0) <= 5:
        return 1.0, "+100% (5 Gói Đầu Tiên)"

    pack_config = session_state["config_packs"][pack_type]
    threshold = pack_config.get("pity_threshold", 0)
    increment = pack_config.get("pity_increment", 0.0)
    misses = session_state["pack_pity"].get(pack_type, 0)
    
    if threshold > 0 and misses >= threshold:
        bonus = min(1.0, (misses - threshold + 1) * increment * session_state.get("pity_multiplier", 1.0))
        if bonus > 0:
            return bonus, f"+{int(bonus * 100)}% (Tạch {misses} gói)"

    return 0.0, "0% (Bình thường)"


def check_grand_album(session_state) -> None:
    if session_state.get("grand_album_enabled", False):
        if total_cards_collected(session_state) == TOTAL_CARDS:
            completions = session_state.get("grand_album_completions", 0)
            if completions < 1:
                session_state["inventory"] = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
                session_state["owned_cards"] = set()
                session_state["grand_album_completions"] = completions + 1
                add_log(session_state, "🏆 CHÚC MỪNG! Đã hoàn thành Album. Chuyển sang vòng Grand Album!")
            elif completions == 1 and not session_state.get("grand_album_finished", False):
                session_state["grand_album_finished"] = True
                add_log(session_state, "🏆 CHÚC MỪNG! Đã hoàn thành toàn bộ Grand Album! Các thẻ tiếp theo sẽ biến thành Sao.")


def calculate_new_chance(session_state, rarity: int, pack_type: str) -> float:
    cards_owned = session_state["inventory"][rarity]
    max_cards = MAX_CARDS[rarity]
    if cards_owned >= max_cards:
        return 0.0

    base_new = (max_cards - cards_owned) / max_cards
    
    formula_type = session_state.get("new_card_formula_type", "document")
    power = session_state.get("new_card_power", 2.5)
    
    if formula_type == "document":
        pack_config = session_state["config_packs"].get(pack_type, {})
        y_val = pack_config.get("y_value", 0.0) if isinstance(pack_config, dict) else getattr(pack_config, "y_value", 0.0)
        final_power = power + y_val
    else:
        final_power = power
        
    return min(1.0, base_new ** final_power)


def get_ss2_pity_info(session_state) -> dict:
    from .config import CARD_SETS
    set_counts = {}
    for c in session_state.get("owned_cards", set()):
        s_id = c[0]
        set_counts[s_id] = set_counts.get(s_id, 0) + 1
            
    completed_sets = 0
    best_set_id = None
    max_cards_in_incomplete = -1
    
    for s_id, s_info in CARD_SETS.items():
        total_in_set = sum(s_info["cards"].values())
        owned = set_counts.get(s_id, 0)
        if owned >= total_in_set:
            completed_sets += 1
        else:
            if owned > max_cards_in_incomplete:
                max_cards_in_incomplete = owned
                best_set_id = s_id
                
    s_base = session_state.get("config_ss2_s_base", 0.1)
    s_max = session_state.get("config_ss2_s_max", 0.5)
    pity_set = s_base + (s_max - s_base) * (1.0 - completed_sets / len(CARD_SETS))
    
    c_base = session_state.get("config_ss2_c_base", 0.3)
    c_max = session_state.get("config_ss2_c_max", 1.0)
    
    missing_details = []
    if best_set_id:
        s_info = CARD_SETS[best_set_id]
        for r, count in s_info["cards"].items():
            owned_r = sum(1 for c in session_state.get("owned_cards", set()) if c[0] == best_set_id and c[1] == r)
            if owned_r < count:
                eff_r = min(5, r)
                pity_r = c_base + (c_max - c_base) * (5.0 - eff_r) / 4.0
                final_chance = pity_set * pity_r
                missing_details.append({
                    "rarity": r,
                    "missing_count": count - owned_r,
                    "pity_rarity": pity_r,
                    "final_chance": final_chance
                })
    
    return {
        "completed_sets": completed_sets,
        "total_sets": len(CARD_SETS),
        "pity_set": pity_set,
        "best_set_id": best_set_id,
        "best_set_owned": max_cards_in_incomplete,
        "best_set_total": sum(CARD_SETS[best_set_id]["cards"].values()) if best_set_id else 0,
        "best_set_name": CARD_SETS[best_set_id]["name"] if best_set_id else "",
        "missing_details": missing_details
    }

def pick_new_card(session_state, rarity: int, drawn_in_batch: set = None, apply_set_pity: bool = True):
    possible_cards = []
    from .config import CARD_SETS
    for set_id, set_info in CARD_SETS.items():
        if rarity in set_info["cards"]:
            count = set_info["cards"][rarity]
            for idx in range(count):
                possible_cards.append((set_id, rarity, idx))
                
    if drawn_in_batch is None:
        drawn_in_batch = set()
        
    missing_cards = [c for c in possible_cards if c not in session_state["owned_cards"] and c not in drawn_in_batch]
    import random
    
    if apply_set_pity and session_state.get("ss2_optimize_collection", True):
        # Calculate completion per set
        set_counts = {}
        for c in session_state["owned_cards"]:
            s_id = c[0]
            set_counts[s_id] = set_counts.get(s_id, 0) + 1
                
        completed_sets = 0
        best_set_id = None
        max_cards_in_incomplete = -1
        
        for s_id, s_info in CARD_SETS.items():
            total_in_set = sum(s_info["cards"].values())
            owned = set_counts.get(s_id, 0)
            if owned >= total_in_set:
                completed_sets += 1
            else:
                if owned > max_cards_in_incomplete:
                    max_cards_in_incomplete = owned
                    best_set_id = s_id
                    
        if best_set_id is not None:
            s_info = CARD_SETS[best_set_id]
            if rarity in s_info["cards"]:
                total_rarity = s_info["cards"][rarity]
                owned_rarity_count = sum(1 for c in session_state["owned_cards"] if c[0] == best_set_id and c[1] == rarity)
                
                if owned_rarity_count < total_rarity:
                    s_base = session_state.get("config_ss2_s_base", 0.1)
                    s_max = session_state.get("config_ss2_s_max", 0.5)
                    c_base = session_state.get("config_ss2_c_base", 0.3)
                    c_max = session_state.get("config_ss2_c_max", 1.0)
                    
                    pity_set = s_base + (s_max - s_base) * (1.0 - completed_sets / len(CARD_SETS))
                    effective_rarity = min(5, rarity)
                    pity_rarity_card = c_base + (c_max - c_base) * (5.0 - effective_rarity) / 4.0
                    
                    if random.random() < (pity_set * pity_rarity_card):
                        # SUCCESS: Force missing card from this set
                        missing_in_best = [c for c in missing_cards if c[0] == best_set_id]
                        if missing_in_best:
                            chosen_card = random.choice(missing_in_best)
                            session_state["owned_cards"].add(chosen_card)
                            drawn_in_batch.add(chosen_card)
                            return chosen_card

    if missing_cards:
        chosen_card = random.choice(missing_cards)
        session_state["owned_cards"].add(chosen_card)
        drawn_in_batch.add(chosen_card)
        return chosen_card
    return None

def pick_dup_card(session_state, rarity: int, drawn_in_batch: set = None):
    if drawn_in_batch is None:
        drawn_in_batch = set()
        
    owned = [c for c in session_state["owned_cards"] if c[1] == rarity and c not in drawn_in_batch]
    import random
    if owned:
        chosen = random.choice(owned)
        drawn_in_batch.add(chosen)
        return chosen
    possible_cards = []
    from .config import CARD_SETS
    for set_id, set_info in CARD_SETS.items():
        if rarity in set_info["cards"]:
            count = set_info["cards"][rarity]
            for idx in range(count):
                if (set_id, rarity, idx) not in drawn_in_batch:
                    possible_cards.append((set_id, rarity, idx))
    if possible_cards:
        chosen = random.choice(possible_cards)
        drawn_in_batch.add(chosen)
        return chosen
    return None

def roll_card(session_state, rarity: int, pity_bonus: float, pack_type: str, drawn_in_batch: set = None) -> tuple[str, int, tuple]:
    session_state["total_cards_drawn"] += 1
    cards_owned = session_state["inventory"][rarity]
    max_cards = MAX_CARDS[rarity]
    
    if cards_owned >= max_cards:
        final_chance = 0.0
    else:
        new_chance = calculate_new_chance(session_state, rarity, pack_type)
        final_chance = min(1.0, new_chance + pity_bonus)

    if random.random() < final_chance:
        session_state["inventory"][rarity] += 1
        c = pick_new_card(session_state, rarity, drawn_in_batch)
        session_state["new_cards_drawn"] += 1
        session_state["new_cards_by_rarity"][rarity] += 1
        check_grand_album(session_state)
        if "recent_draws" in session_state: session_state["recent_draws"].append(("NEW", rarity, c))
        return "NEW", rarity, c

    session_state["stars"] += STAR_VALUES[rarity]
    session_state["pack_stars_gained"] = session_state.get("pack_stars_gained", 0) + STAR_VALUES[rarity]
    session_state["dup_cards_drawn"] += 1
    session_state["dup_cards_by_rarity"][rarity] += 1
    c = pick_dup_card(session_state, rarity)
    if "recent_draws" in session_state: session_state["recent_draws"].append(("DUP", rarity, c))
    return "DUP", rarity, c


def open_pack(session_state, pack_type: str) -> None:
    session_state["total_packs"] += 1
    session_state["pack_counts"][pack_type] += 1

    pity_bonus, pity_message = get_pity_bonus(session_state, pack_type)
    
    first_pack_luck = False
    if session_state.get("ss2_optimize_collection", True):
        if "opened_pack_types_ss2" not in session_state:
            session_state["opened_pack_types_ss2"] = set()
        if pack_type not in session_state["opened_pack_types_ss2"]:
            session_state["opened_pack_types_ss2"].add(pack_type)
            first_pack_luck = True
            pity_bonus = 1.0
            pity_message = "100% (First Pack's Luck SS2)"
            
    pack_config = session_state["config_packs"][pack_type]
    effective_size = pack_config["size"]
    
    got_new = False
    raw_results = []
    current_pity_bonus = pity_bonus
    
    drawn_in_batch = set()

    for _ in range(effective_size - 1):
        rarity_str = random.choices(
            list(pack_config["weights"].keys()),
            weights=list(pack_config["weights"].values()),
        )[0]
        rarity_rolled = int(rarity_str)
        status, final_rarity, specific_card = roll_card(session_state, rarity_rolled, current_pity_bonus, pack_type, drawn_in_batch)
        if status == "NEW":
            got_new = True
            if session_state.get("total_packs", 0) > 5 and not first_pack_luck:
                current_pity_bonus = 0.0 # Reset immediately when a new card is chosen
        raw_results.append((status, final_rarity, specific_card))

    is_rainbow = (pack_type == "Rainbow")
    if is_rainbow:
        wild_status, wild_rarity, wild_specific_card = open_rainbow_pack_guaranteed(session_state, drawn_in_batch)
        if wild_status == "NEW":
            got_new = True
            if not first_pack_luck:
                current_pity_bonus = 0.0
        raw_results.append((wild_status, wild_rarity, wild_specific_card))
    else:
        guaranteed_tier = pack_config["guaranteed_tier"]
        guaranteed_rarity = guaranteed_tier
        status, final_rarity, specific_card = roll_card(session_state, guaranteed_rarity, current_pity_bonus, pack_type, drawn_in_batch)
        if status == "NEW":
            got_new = True
            if not first_pack_luck:
                current_pity_bonus = 0.0
        raw_results.append((status, final_rarity, specific_card))

    # Sort by rarity ascending
    raw_results.sort(key=lambda x: x[1])

    pack_results = []
    tagged_guarantee = False
    
    for status, rarity, specific_card in raw_results:
        guaranteed = False
        if is_rainbow:
            # For Rainbow, just tag the first NEW one as the "guaranteed" if any
            if status == "NEW" and not tagged_guarantee:
                guaranteed = True
                tagged_guarantee = True
        else:
            # Tag the first card that matches the guaranteed tier exactly
            if rarity == pack_config["guaranteed_tier"] and not tagged_guarantee:
                guaranteed = True
                tagged_guarantee = True
                
        pack_results.append((status, rarity, specific_card, guaranteed))

    update_pity(session_state, pack_type, got_new)
    add_log(session_state, format_pack_log(session_state, pack_type, pack_results, pity_message, got_new))


def open_rainbow_pack_guaranteed(session_state, drawn_in_batch: set = None) -> tuple[str, int, tuple]:
    session_state["total_cards_drawn"] += 1
    if session_state["inventory"][6] < MAX_CARDS[6]:
        session_state["inventory"][6] += 1
        c = pick_new_card(session_state, 6, drawn_in_batch)
        session_state["new_cards_drawn"] += 1
        session_state["new_cards_by_rarity"][6] += 1
        check_grand_album(session_state)
        if "recent_draws" in session_state: session_state["recent_draws"].append(("NEW", 6, c))
        return "NEW", 6, c

    missing_rarities = [r for r in [1, 2, 3, 4, 5] if session_state["inventory"][r] < MAX_CARDS[r]]
    if missing_rarities:
        rarity = random.choice(missing_rarities)
        session_state["inventory"][rarity] += 1
        c = pick_new_card(session_state, rarity, drawn_in_batch)
        session_state["new_cards_drawn"] += 1
        session_state["new_cards_by_rarity"][rarity] += 1
        check_grand_album(session_state)
        if "recent_draws" in session_state: session_state["recent_draws"].append(("NEW", rarity, c))
        return "NEW", rarity, c

    session_state["stars"] += STAR_VALUES[6]
    session_state["pack_stars_gained"] = session_state.get("pack_stars_gained", 0) + STAR_VALUES[6]
    session_state["dup_cards_drawn"] += 1
    session_state["dup_cards_by_rarity"][6] += 1
    c = pick_dup_card(session_state, 6, drawn_in_batch)
    if "recent_draws" in session_state: session_state["recent_draws"].append(("DUP", 6, c))
    return "DUP", 6, c


def update_pity(session_state, pack_type: str, got_new: bool) -> None:
    if got_new:
        session_state["pack_pity"][pack_type] = 0
    else:
        session_state["pack_pity"].setdefault(pack_type, 0)
        session_state["pack_pity"][pack_type] += 1


def format_card_name(card):
    from .config import CARD_SETS
    if not card: return "?"
    set_id, rarity, idx = card
    return f"{CARD_SETS[set_id]['name']} #{idx+1}"

def format_pack_log(session_state, pack_type: str, pack_results: list[tuple[str, int, tuple, bool]], pity_message: str, got_new: bool) -> str:
    result_parts = []
    for status, rarity, specific_card, guaranteed in pack_results:
        label = f"{rarity}-Sao" if rarity < 6 else "Thẻ VÀNG"
        cname = format_card_name(specific_card)
        suffix = " [Bảo Hiểm]" if guaranteed else ""
        result_parts.append(f"{label} [{cname}] ({status}){suffix}")

    card_rush_note = ", Card Rush" if "+" in pack_type else ""

    prefix = "✅" if got_new else "❌"
    pack_count = session_state["pack_counts"][pack_type]
    return (
        f"{prefix} 📦 {pack_type} Pack #{pack_count}"
        f" (Buff: {pity_message}{card_rush_note}) | "
        f"Mở ra: {', '.join(result_parts)}"
    )


def open_chest(session_state, chest_type: str) -> dict:
    if chest_type not in CHEST_CONFIG:
        return {"success": False, "message": f"⚠️ Không tìm thấy rương {chest_type}!"}
    cost = CHEST_CONFIG[chest_type]["cost"]
    if session_state["stars"] < cost:
        return {"success": False, "message": f"⚠️ Không đủ Sao! Cần {cost}⭐ để mở Rương {chest_type}."}
    
    start_total = session_state.get("total_cards_drawn", 0)
    start_stars = session_state.get("stars", 0)
    
    session_state["stars"] -= cost
    add_log(session_state, f"🌟 Đổi {cost}⭐ để mở {chest_type} Chest!")
    packs_to_open = CHEST_CONFIG[chest_type]["packs"]
    
    # Check if card rush is enabled and apply +
    is_cr = session_state.get("card_rush_enabled", False)
    
    has_recent = "recent_draws" in session_state
    if not has_recent:
        session_state["recent_draws"] = []
        
    opened_packs = []
    for base_pack in packs_to_open:
        pack_type = f"{base_pack}+" if is_cr and f"{base_pack}+" in session_state["config_packs"] else base_pack
        open_pack(session_state, pack_type)
        opened_packs.append(pack_type)
        
    total_drawn = session_state.get("total_cards_drawn", 0) - start_total
    stars_diff = session_state.get("stars", 0) - start_stars
    
    # We only slice the recent_draws added during THIS chest if has_recent was True, but actually returning everything is fine if it's ignored by open_bulk_packs
    new_cards_list = [c for s, r, c in session_state.get("recent_draws", []) if s == "NEW"]
    dup_cards_list = [c for s, r, c in session_state.get("recent_draws", []) if s == "DUP"]
    
    if not has_recent:
        del session_state["recent_draws"]
    
    return {
        "success": True,
        "chest_type": chest_type,
        "message": f"Mở thành công {chest_type} Chest!",
        "summary": ", ".join(opened_packs),
        "total_cards": total_drawn,
        "stars_diff": stars_diff,
        "new_cards_list": new_cards_list,
        "dup_cards_list": dup_cards_list
    }


def run_auto_chests(session_state) -> dict:
    chests_opened = 0
    breakdown = {"Gold": 0, "Silver": 0, "Bronze": 0}
    max_auto_chests = 1000
    while session_state["stars"] >= 100 and chests_opened < max_auto_chests:
        if session_state["stars"] >= 500:
            open_chest(session_state, "Gold")
            chests_opened += 1
            breakdown["Gold"] += 1
        elif session_state["stars"] >= 250:
            open_chest(session_state, "Silver")
            chests_opened += 1
            breakdown["Silver"] += 1
        elif session_state["stars"] >= 100:
            open_chest(session_state, "Bronze")
            chests_opened += 1
            breakdown["Bronze"] += 1
    return breakdown

def open_bulk_packs(session_state, bulk_settings: dict[str, int], auto_chest: bool = False) -> dict:
    total_to_open = sum(bulk_settings.values())
    if total_to_open == 0:
        return {"success": False, "message": "⚠️ Vui lòng chọn ít nhất 1 pack để mở!"}

    if total_to_open > 1:
        add_log(session_state, f"========== BẮT ĐẦU MỞ NHIỀU ({total_to_open} PACKS) ==========")
    session_state["recent_draws"] = []
    start_new = session_state.get("new_cards_drawn", 0)
    start_dup = session_state.get("dup_cards_drawn", 0)
    start_total = session_state.get("total_cards_drawn", 0)
    start_stars = session_state.get("stars", 0)
    chests_opened = 0
    chests_breakdown = {"Gold": 0, "Silver": 0, "Bronze": 0}
    
    for pack_type, count in bulk_settings.items():
        for _ in range(count):
            open_pack(session_state, pack_type)

    if auto_chest:
        max_auto_chests = 500
        while session_state["stars"] >= 100 and chests_opened < max_auto_chests:
            if session_state["stars"] >= 500:
                open_chest(session_state, "Gold")
                chests_opened += 1
                chests_breakdown["Gold"] += 1
            elif session_state["stars"] >= 250:
                open_chest(session_state, "Silver")
                chests_opened += 1
                chests_breakdown["Silver"] += 1
            elif session_state["stars"] >= 100:
                open_chest(session_state, "Bronze")
                chests_opened += 1
                chests_breakdown["Bronze"] += 1
                
        if session_state["stars"] >= 100 and chests_opened >= max_auto_chests:
            add_log(session_state, "⚠️ Dừng tự động mở rương do đạt giới hạn an toàn (500 rương) để tránh treo máy!")

    summary = ", ".join(f"{count} {pack_type}" for pack_type, count in bulk_settings.items() if count > 0)
    chest_parts = []
    if chests_breakdown["Gold"] > 0: chest_parts.append(f"{chests_breakdown['Gold']} Rương Vàng")
    if chests_breakdown["Silver"] > 0: chest_parts.append(f"{chests_breakdown['Silver']} Rương Bạc")
    if chests_breakdown["Bronze"] > 0: chest_parts.append(f"{chests_breakdown['Bronze']} Rương Đồng")
    
    if chest_parts:
        chest_str = " + ".join(chest_parts)
        if summary: summary += f" + {chest_str}"
        else: summary = chest_str
    
    if total_to_open > 1 or chests_opened > 0:
        add_log(session_state, f"🌟 HOÀN THÀNH MỞ: {summary}")
    
    new_drawn = session_state.get("new_cards_drawn", 0) - start_new
    dup_drawn = session_state.get("dup_cards_drawn", 0) - start_dup
    total_drawn = session_state.get("total_cards_drawn", 0) - start_total
    stars_diff = session_state.get("stars", 0) - start_stars
    
    new_cards_list = [c for s, r, c in session_state.get("recent_draws", []) if s == "NEW"]
    dup_cards_list = [c for s, r, c in session_state.get("recent_draws", []) if s == "DUP"]
    if "recent_draws" in session_state: del session_state["recent_draws"]

    return {
        "success": True, 
        "message": f"Đã mở thành công {total_to_open} pack!",
        "summary": summary,
        "new_cards": new_drawn,
        "dup_cards": dup_drawn,
        "total_cards": total_drawn,
        "stars_diff": stars_diff,
        "chests_opened": chests_opened,
        "new_cards_list": new_cards_list,
        "dup_cards_list": dup_cards_list
    }


def add_log(session_state, entry: str) -> None:
    session_state["log"].insert(0, entry)
    if len(session_state["log"]) > 300:
        session_state["log"] = session_state["log"][:300]


def build_rate_rows(session_state, pack_type: str) -> list[dict]:
    if pack_type == "Rainbow":
        return []

    pack_config = session_state["config_packs"][pack_type]
    total_weight = sum(pack_config["weights"].values())
    pity_bonus, _ = get_pity_bonus(session_state, pack_type)
    rows = []

    for rarity_str, weight in pack_config["weights"].items():
        rarity = int(rarity_str)
        drop_rate = weight / total_weight
        new_chance = calculate_new_chance(session_state, rarity, pack_type)
        duplicate_chance = 1.0 - new_chance
        new_value = f"{new_chance * 100:.1f}%"
        if pity_bonus > 0 and session_state["inventory"][rarity] < MAX_CARDS[rarity]:
            new_value += f" (+{pity_bonus * 100:.0f}%)"

        rows.append(
            {
                "Độ hiếm": f"{rarity}-Sao" if rarity < 6 else "VÀNG",
                "Khả năng Rớt": f"{drop_rate * 100:.1f}%",
                "Thẻ MỚI": new_value,
                "Thẻ TRÙNG": f"{duplicate_chance * 100:.1f}% (+{STAR_VALUES[rarity]}⭐)",
            }
        )

    return rows


# --- CHEST DROP (WIN STREAK MINI-GAME) LOGIC ---
def calculate_chest_drop_new_chance(session_state, rarity: int, y_val: float) -> float:
    cards_owned = session_state['inventory'][rarity]
    max_cards = MAX_CARDS[rarity]
    if cards_owned >= max_cards:
        return 0.0
    base_new = (max_cards - cards_owned) / max_cards
    x_val = float(session_state.get('config_chest_drop_x', 2.0))
    final_power = x_val + y_val
    return min(1.0, base_new ** final_power)

def roll_chest_drop_card(session_state, rarity: int, y_val: float, drawn_in_batch: set = None) -> tuple[str, tuple]:
    session_state['cd_total_cards_drawn'] += 1
    new_chance = calculate_chest_drop_new_chance(session_state, rarity, y_val)
            
    if random.random() < new_chance:
        session_state['inventory'][rarity] += 1
        c = pick_new_card(session_state, rarity, drawn_in_batch)
        session_state['cd_new_cards_drawn'] += 1
        session_state['cd_new_cards_by_rarity'][rarity] += 1
        check_grand_album(session_state)
        if 'recent_draws' in session_state: session_state['recent_draws'].append(('NEW', rarity, c))
        return 'NEW', c
    session_state['stars'] += STAR_VALUES[rarity]
    session_state['cd_stars_gained'] += STAR_VALUES[rarity]
    session_state['cd_dup_cards_drawn'] += 1
    session_state['cd_dup_cards_by_rarity'][rarity] += 1
    c = pick_dup_card(session_state, rarity, drawn_in_batch)
    if 'recent_draws' in session_state: session_state['recent_draws'].append(('DUP', rarity, c))
    return 'DUP', c

def process_chest_drop_hit(session_state, start_tier: int, current_tier: int, drawn_in_batch: set = None) -> dict:
    session_state["chest_drop_counts"][current_tier] += 1
    tiers_config = session_state.get('config_chest_drop_tiers')
    matrix_config = session_state.get('config_chest_upgrade_matrix')
    if not tiers_config or not matrix_config:
        from .config_manager import get_default_config
        def_cfg = get_default_config()
        tiers_config = def_cfg["chest_tiers"]
        matrix_config = def_cfg["chest_upgrade_matrix"]
        
    t_cfg = tiers_config[str(current_tier)]
    weights = t_cfg["weights"]
    
    total_weight = sum(int(v) for v in weights.values())
    r = random.uniform(0, total_weight)
    current_weight = 0
    drop_rarity = current_tier
    for rarity_str, weight in weights.items():
        current_weight += int(weight)
        if r <= current_weight:
            drop_rarity = int(rarity_str)
            break
            
    # We will implement the drawn_in_batch logic in Phase 2
    status, card_tuple = roll_chest_drop_card(session_state, drop_rarity, float(t_cfg["y_value"]), drawn_in_batch)
    
    upgraded = False
    next_tier = current_tier
    if current_tier < 5:
        upgrade_chance = float(matrix_config[str(start_tier)][str(current_tier)])
        if random.random() < upgrade_chance:
            upgraded = True
            next_tier = current_tier + 1
            
    return {
        'status': status,
        'rarity': drop_rarity,
        'card': card_tuple,
        'upgraded': upgraded,
        'next_tier': next_tier
    }
```

---

## File: `card_album/liveops_simulator.py`

```python
import math
import re
from typing import Dict, Any, List
from .config import PACK_ORDER

def is_card_rush_day(day: int) -> bool:
    if day <= 0: return False
    week = (day - 1) // 7 + 1
    weekday = (day - 1) % 7 + 1
    if week <= 6: 
        return weekday == 6
    else: 
        return weekday in (3, 6)

def get_day_of_level(level: int, levels_per_weekday: int, levels_per_weekend: int) -> int:
    if levels_per_weekday <= 0 and levels_per_weekend <= 0: return 1
    total = 0
    day = 1
    while True:
        weekday = (day - 1) % 7 + 1
        total += levels_per_weekend if weekday in (5, 6, 7) else levels_per_weekday
        if level <= total:
            return day
        day += 1

def get_day_string(day: int) -> str:
    week = (day - 1) // 7 + 1
    weekday = (day - 1) % 7 + 1
    days_map = {1: "Thứ 2", 2: "Thứ 3", 3: "Thứ 4", 4: "Thứ 5", 5: "Thứ 6", 6: "Thứ 7", 7: "Chủ Nhật"}
    return f"Tuần {week} - {days_map[weekday]}"

def upgrade_pack(pack: str, is_cr: bool) -> str:
    if is_cr and pack in ("Bronze", "Emerald", "Silver"):
        return pack + "+"
    return pack

def add_packs_from_string(reward_str: str, packs_dict: dict, is_cr: bool, day: int = 0, source: str = "", cr_detailed_logs: list = None):
    if not isinstance(reward_str, str):
        reward_str = str(reward_str)
    for base in ["Bronze", "Emerald", "Silver", "Amethyst", "Ruby", "Gold", "Rainbow"]:
        matches = re.findall(rf"(?:(\d+)[xX]\s*)?[*]*\s*{base}", reward_str, re.IGNORECASE)
        total_to_add = 0
        for match in matches:
            total_to_add += int(match) if match else 1
            
        if total_to_add > 0:
            upgraded = upgrade_pack(base, is_cr)
            packs_dict[upgraded] += total_to_add
            if is_cr and upgraded != base and cr_detailed_logs is not None:
                cr_detailed_logs.append(f"Đã nâng cấp {total_to_add} gói {base} → {upgraded} (Từ {source} vào {get_day_string(day)})")

def calculate_levels(daily_levels: List[int]) -> Dict[str, int]:
    total_levels = sum(daily_levels)
    full_cycles = total_levels // 9
    remainder = total_levels % 9
    
    normal = full_cycles * 6
    hard = full_cycles * 2
    super_hard = full_cycles * 1
    
    pattern = ['N', 'N', 'H', 'N', 'N', 'H', 'N', 'N', 'SH']
    for i in range(remainder):
        if pattern[i] == 'N': normal += 1
        elif pattern[i] == 'H': hard += 1
        elif pattern[i] == 'SH': super_hard += 1
            
    return {
        "total": total_levels,
        "normal": normal,
        "hard": hard,
        "super_hard": super_hard
    }

def simulate_core_gameplay(daily_levels: List[int], cr_enabled: bool, cr_detailed_logs: list, core_enabled: bool = True) -> Dict[str, Any]:
    packs = {"Bronze": 0, "Bronze+": 0, "Emerald": 0, "Emerald+": 0}
    logs = []
    
    bronze_count = 0
    emerald_count = 0
    bronze_plus = 0
    emerald_plus = 0
    
    level = 0
    for idx, lpd in enumerate(daily_levels):
        day = idx + 1
        is_cr = cr_enabled and is_card_rush_day(day)
        
        for _ in range(lpd):
            level += 1
            if level % 3 == 0 and level % 9 != 0:
                if is_cr and core_enabled: 
                    bronze_plus += 1
                    cr_detailed_logs.append(f"Đã nâng cấp 1 gói Bronze → Bronze+ (Từ Cày Cuốc [Màn Hard] vào {get_day_string(day)})")
                elif core_enabled:
                    bronze_count += 1
            elif level % 9 == 0:
                if is_cr and core_enabled: 
                    emerald_plus += 1
                    cr_detailed_logs.append(f"Đã nâng cấp 1 gói Emerald → Emerald+ (Từ Cày Cuốc [Màn Super Hard] vào {get_day_string(day)})")
                elif core_enabled:
                    emerald_count += 1
            
    packs["Bronze"] = bronze_count
    packs["Bronze+"] = bronze_plus
    packs["Emerald"] = emerald_count
    packs["Emerald+"] = emerald_plus
    
    tot_bronze = bronze_count + bronze_plus
    tot_emerald = emerald_count + emerald_plus
    logs.append(f"**Tổng kết:** Chiến thắng {tot_bronze} màn Hard, {tot_emerald} màn Super Hard")
    logs.append(f"- Màn Hard: {bronze_count} Bronze, {bronze_plus} Bronze+")
    logs.append(f"- Màn Super Hard: {emerald_count} Emerald, {emerald_plus} Emerald+")
    
    return {"packs": packs, "logs": logs}

def simulate_win_streak(daily_levels: List[int], cr_enabled: bool, cr_detailed_logs: list, config_rewards: dict) -> Dict[str, Any]:
    packs = {"Bronze": 0, "Bronze+": 0, "Emerald": 0, "Emerald+": 0, "Silver": 0, "Silver+": 0, "Amethyst": 0, "Ruby": 0, "Gold": 0, "Rainbow": 0}
    logs = []
    
    total_level = 0
    event_count = 0
    event_wins = 0
    claimed_milestones = set()
    has_avatar = False
    
    for idx, lpd in enumerate(daily_levels):
        day = idx + 1
        weekday = (day - 1) % 7 + 1
        is_cr = cr_enabled and is_card_rush_day(day)
        
        # Reset event every Friday
        if weekday == 5:
            event_count += 1
            event_wins = 0
            claimed_milestones = set()
            
        for _ in range(lpd):
            total_level += 1
            # Event is active Friday, Saturday, Sunday
            if weekday in (5, 6, 7):
                event_wins += 1
                
                # Check milestones immediately upon winning a level
                for req_wins, reward_str in config_rewards["win_streak_rewards"].items():
                    if event_wins == req_wins and req_wins not in claimed_milestones:
                        claimed_milestones.add(req_wins)
                        
                        reward_str_to_process = reward_str
                        if "Avatar" in reward_str:
                            if not has_avatar:
                                has_avatar = True
                                reward_str_to_process = reward_str.split("(Hoặc")[0].strip()
                            else:
                                reward_str_to_process = "500 Coins + 1x Boosters Set + **1x Ruby Pack**"
                        
                        if "Pack" in reward_str_to_process:
                            cr_tag = " (Card Rush)" if is_cr else ""
                            logs.append(f"Tuần {(day - 1) // 7 + 1} - Mốc {req_wins} Win{cr_tag}: {reward_str_to_process}")
                            
                        add_packs_from_string(reward_str_to_process, packs, is_cr, day, f"Win Streak Tuần {(day - 1) // 7 + 1} Mốc {req_wins}", cr_detailed_logs)
                        
    return {"packs": packs, "logs": logs}

def simulate_key_collection(daily_levels: List[int], cr_enabled: bool, cr_detailed_logs: list, config_rewards: dict) -> Dict[str, Any]:
    packs = {"Bronze": 0, "Bronze+": 0, "Emerald": 0, "Emerald+": 0, "Silver": 0, "Silver+": 0, "Amethyst": 0, "Ruby": 0, "Gold": 0, "Rainbow": 0}
    logs = [f"**Lưu ý:** Sự kiện Key Collection diễn ra và reset hàng tuần vào mỗi Thứ 2."]
    
    stage_reqs = {1:3, 2:8, 3:15, 4:25, 5:33, 6:40, 7:52, 8:67, 9:77, 10:89, 11:99, 12:111, 13:126, 14:138, 15:154, 16:164, 17:176, 18:192, 19:204, 20:214, 21:229, 22:241, 23:259, 24:279, 25:304}
    total_keys_ever = 0
    event_keys = 0
    claimed_milestones = set()
    
    for idx, lpd in enumerate(daily_levels):
        day = idx + 1
        weekday = (day - 1) % 7 + 1
        is_cr = cr_enabled and is_card_rush_day(day)
        
        # Reset event every Monday
        if weekday == 1:
            event_keys = 0
            claimed_milestones = set()
            
        for _ in range(lpd):
            event_keys += 5
            total_keys_ever += 5
            
            for stage, req_keys in stage_reqs.items():
                if event_keys >= req_keys and stage not in claimed_milestones:
                    claimed_milestones.add(stage)
                    reward_str = config_rewards["key_collection_rewards"].get(stage, "")
                    
                    if "Pack" in reward_str:
                        cr_tag = " (Card Rush)" if is_cr else ""
                        logs.append(f"Tuần {(day - 1) // 7 + 1} - Stage {stage} ({req_keys} keys){cr_tag}: {reward_str}")
                    add_packs_from_string(reward_str, packs, is_cr, day, f"Key Collection Tuần {(day - 1) // 7 + 1} Stage {stage}", cr_detailed_logs)

    logs.insert(1, f"**Tổng số Keys kiếm được (cả mùa):** {total_keys_ever} Keys (Mỗi level qua bàn nhận mặc định 5 keys)")
    return {"packs": packs, "logs": logs}

def get_tokens_for_level(level: int) -> int:
    if level % 9 == 0: return 3
    if level % 3 == 0: return 2
    return 1

def simulate_master_pass(daily_levels: List[int], is_premium: bool, cr_enabled: bool, cr_detailed_logs: list, config_rewards: dict) -> Dict[str, Any]:
    stage_tokens = [0, 1, 3, 6, 10, 18, 23, 29, 38, 45, 55, 63, 75, 86, 95, 110, 126, 136, 150, 168, 188, 203, 214, 233, 250, 270, 288, 309, 333, 355, 380]
    
    packs = {"Bronze": 0, "Bronze+": 0, "Emerald": 0, "Emerald+": 0, "Silver": 0, "Silver+": 0, "Amethyst": 0, "Ruby": 0, "Gold": 0, "Rainbow": 0}
    logs = [f"**Lưu ý:** Sự kiện Master Pass diễn ra và reset hàng tháng (mỗi 30 ngày)."]
    
    total_tokens_ever = 0
    event_tokens = 0
    claimed_milestones = set()
    global_level = 0
    
    for idx, lpd in enumerate(daily_levels):
        day = idx + 1
        weekday = (day - 1) % 7 + 1
        is_cr = cr_enabled and is_card_rush_day(day)
        
        # Reset event every 30 days (Monthly Battle Pass)
        if day % 30 == 1:
            event_tokens = 0
            claimed_milestones = set()
            
        for _ in range(lpd):
            global_level += 1
            tokens_earned = get_tokens_for_level(global_level)
            event_tokens += tokens_earned
            total_tokens_ever += tokens_earned
            
            for stage, req_tokens in enumerate(stage_tokens):
                if event_tokens >= req_tokens and stage not in claimed_milestones:
                    claimed_milestones.add(stage)
                    
                    free_r = config_rewards["master_pass_free"].get(stage, "")
                    prem_r = config_rewards["master_pass_premium"].get(stage, "")
                    
                    has_pack_free = "Pack" in free_r
                    has_pack_prem = is_premium and "Pack" in prem_r
                    
                    if has_pack_free or has_pack_prem:
                        cr_tag = " (Card Rush)" if is_cr else ""
                        log_line = f"Tháng {(day - 1) // 30 + 1} - Stage {stage} ({req_tokens} tokens){cr_tag}: "
                        if has_pack_free: log_line += f"[Free] {free_r} "
                        if has_pack_prem: log_line += f"| [Premium] {prem_r}"
                        logs.append(log_line)
                    
                    add_packs_from_string(free_r, packs, is_cr, day, f"Master Pass Tháng {(day - 1) // 30 + 1} Stage {stage} [Free]", cr_detailed_logs)
                    if is_premium:
                        add_packs_from_string(prem_r, packs, is_cr, day, f"Master Pass Tháng {(day - 1) // 30 + 1} Stage {stage} [Premium]", cr_detailed_logs)

    logs.insert(1, f"**Tổng số Token kiếm được (cả mùa):** {total_tokens_ever} Tokens (Thắng màn Normal = 1 Token, Hard = 2 Tokens, Super Hard = 3 Tokens)")
    return {"packs": packs, "logs": logs}

def simulate_liveops(days: int, levels_per_weekday: tuple, levels_per_weekend: tuple, toggles: Dict[str, bool], iap: Dict[str, Any], config_rewards: Dict[str, Any]) -> Dict[str, Any]:
    import random
    daily_levels = []
    for day in range(1, days + 1):
        weekday = (day - 1) % 7 + 1
        if weekday in (5, 6, 7):
            daily_levels.append(random.randint(levels_per_weekend[0], levels_per_weekend[1]))
        else:
            daily_levels.append(random.randint(levels_per_weekday[0], levels_per_weekday[1]))
            
    levels_info = calculate_levels(daily_levels)
    total_levels = levels_info["total"]
    cr_enabled = toggles.get("card_rush", False)
    core_enabled = toggles.get("core_gameplay", True)
    
    result_packs = {p: 0 for p in PACK_ORDER}
    all_logs = {}
    cr_detailed_logs = []
    
    core = simulate_core_gameplay(daily_levels, cr_enabled, cr_detailed_logs, core_enabled)
    for p, v in core["packs"].items(): result_packs[p] += v
    all_logs["core"] = core["logs"]
    
    if toggles.get("win_streak"):
        ws = simulate_win_streak(daily_levels, cr_enabled, cr_detailed_logs, config_rewards)
        for p, v in ws["packs"].items(): result_packs[p] += v
        all_logs["win_streak"] = ws["logs"]
        
    if toggles.get("key_collection"):
        kc = simulate_key_collection(daily_levels, cr_enabled, cr_detailed_logs, config_rewards)
        for p, v in kc["packs"].items(): result_packs[p] += v
        all_logs["key_collection"] = kc["logs"]
        
    if toggles.get("master_pass"):
        mp = simulate_master_pass(daily_levels, toggles.get("master_pass_premium", False), cr_enabled, cr_detailed_logs, config_rewards)
        for p, v in mp["packs"].items(): result_packs[p] += v
        all_logs["master_pass"] = mp["logs"]
        
    chest_drop_res = {"chests": {1: 0, 2: 0, 3: 0}, "logs": []}
    if toggles.get("chest_drop", True):
        from .liveops_simulator import simulate_chest_drop
        chest_drop_res = simulate_chest_drop(daily_levels)
        all_logs["chest_drop"] = chest_drop_res["logs"]
    iap_summary = {p: 0 for p in PACK_ORDER}
    total_spent = 0.0
    total_iap_bought = 0
    
    if toggles.get("master_pass") and toggles.get("master_pass_premium"):
        total_spent += 9.99
        
    # Always give Part 1 Free
    iap_summary["Bronze"] += 1
    
    for item, val in iap.items():
        if isinstance(val, bool):
            if val:
                total_iap_bought += 1
                if item == "chain_part_2":
                    iap_summary["Emerald"] += 1
                    iap_summary["Bronze"] += 1
                    total_spent += 2.49
                elif item == "chain_part_3":
                    iap_summary["Silver"] += 1
                    iap_summary["Emerald"] += 1
                    total_spent += 4.99
                elif item == "chain_part_4":
                    iap_summary["Amethyst"] += 1
                    iap_summary["Emerald"] += 1
                    iap_summary["Silver"] += 1
                    total_spent += 10.99
                elif item == "chain_part_5":
                    iap_summary["Ruby"] += 1
                    iap_summary["Amethyst"] += 1
                    iap_summary["Silver"] += 1
                    total_spent += 18.99
                elif item == "chain_part_6":
                    iap_summary["Gold"] += 1
                    iap_summary["Silver"] += 1
                    iap_summary["Amethyst"] += 1
                    total_spent += 27.99
                elif item == "chain_part_7":
                    iap_summary["Rainbow"] += 1
                    iap_summary["Ruby"] += 1
                    iap_summary["Emerald"] += 1
                    iap_summary["Silver"] += 1
                    iap_summary["Amethyst"] += 1
                    total_spent += 49.99
        elif isinstance(val, (int, float)) and val > 0:
            qty = int(val)
            total_iap_bought += qty
            if item == "ooc_4": 
                iap_summary["Emerald"] += 1 * qty
                total_spent += 6.99 * qty
            elif item == "ooc_5": 
                iap_summary["Silver"] += 1 * qty
                total_spent += 14.99 * qty
            elif item == "ooc_6": 
                iap_summary["Amethyst"] += 1 * qty
                total_spent += 29.99 * qty
            elif item == "shop_9.99": 
                iap_summary["Silver"] += 1 * qty
                total_spent += 9.99 * qty
            elif item == "shop_19.99": 
                iap_summary["Amethyst"] += 1 * qty
                total_spent += 19.99 * qty
            elif item == "shop_29.99": 
                iap_summary["Ruby"] += 1 * qty
                total_spent += 29.99 * qty
            elif item == "shop_49.99": 
                iap_summary["Rainbow"] += 1 * qty
                total_spent += 49.99 * qty
            elif item == "shop_99.99": 
                iap_summary["Rainbow"] += 3 * qty
                total_spent += 99.99 * qty

    for p, v in iap_summary.items(): result_packs[p] += v
    
    all_logs["iap"] = ["**Tự động nhận Part 1 Chain Offer (Miễn phí)**"]
    if total_iap_bought > 0:
        all_logs["iap"].append(f"Đã mua/nhận tổng cộng {total_iap_bought} gói IAP/Chain Offer")
    
    assumptions = [
        "Tỉ lệ thắng (Win-rate) là 100%.",
        "Tiến trình Level: N-N-H, N-N-H, N-N-SH (sau 2 Normal - 1 Hard, sau 2 Hard - 1 Super Hard)).",
        "Mặc định người chơi đã mở khóa tất cả LiveOps. Key Collection reset mỗi đầu tuần (Thứ 2). Master Pass reset mỗi tháng (30 ngày).",
        "Người chơi bắt đầu chu kỳ 60 ngày kể từ Thứ Hai đầu tuần và chơi đều đặn mỗi ngày (không cách ngày).",
        "Toàn bộ các gói Pack mua từ IAP/Cửa hàng đều mặc định là gói Thường (Không áp dụng thưởng sự kiện Card Rush)."
    ]
    if cr_enabled:
        if not cr_detailed_logs: 
            cr_detailed_logs.append("Không nhận được gói Plus (+) nào trong thời gian diễn ra Card Rush.")
        cr_detailed_logs.insert(0, "**Lịch mở sự kiện:** Tuần 1-6 (Thứ 7), Tuần 7 trở đi (Thứ 4, Thứ 7).")
        all_logs["card_rush"] = cr_detailed_logs

    # Calculate Bonus Cards
    bonus_cards = (result_packs["Bronze+"] * 1) + (result_packs["Emerald+"] * 2) + (result_packs["Silver+"] * 2)

    source_breakdown = {
        "Core Gameplay": sum(core["packs"].values()),
        "Win Streak": sum(ws["packs"].values()) if toggles.get("win_streak") else 0,
        "Key Collection": sum(kc["packs"].values()) if toggles.get("key_collection") else 0,
        "Master Pass": sum(mp["packs"].values()) if toggles.get("master_pass") else 0,
        "IAP / Mua sắm": sum(iap_summary.values())
    }

    return {
        "assumptions": assumptions,
        "levels_info": levels_info,
        "logs": all_logs,
        "iap_packs": iap_summary,
        "total_packs": result_packs,
        "chest_drop_chests": chest_drop_res["chests"] if 'chest_drop_res' in locals() else {1:0, 2:0, 3:0},
        "total_spent": total_spent,
        "bonus_cards": bonus_cards,
        "source_breakdown": source_breakdown
    }


def simulate_chest_drop(daily_levels: List[int]) -> dict:
    chests = {1: 0, 2: 0, 3: 0}
    logs = ["**Lưu ý:** Chest Drop tính năng chạy và reset vào 0h mỗi ngày."]
    for idx, lpd in enumerate(daily_levels):
        day = idx + 1
        daily_chests = []
        if lpd >= 3: 
            chests[1] += 1
            daily_chests.append("1-Sao")
        if lpd >= 7: 
            chests[2] += 1
            daily_chests.append("2-Sao")
        if lpd >= 12: 
            chests[3] += 1
            daily_chests.append("3-Sao")
            
        if daily_chests:
            logs.append(f"Ngày {day} ({get_day_string(day)}) - Cày {lpd} màn: Nhận Rương {', '.join(daily_chests)}")
            
    logs.insert(1, f"**Sau {len(daily_levels)} ngày, tích lũy được:** {chests[1]} Rương 1-Sao, {chests[2]} Rương 2-Sao, {chests[3]} Rương 3-Sao.")
    return {"chests": chests, "logs": logs}
```

---

## File: `card_album/monte_carlo.py`

```python
import streamlit as st
import pandas as pd
import altair as alt
import copy

from .config import PACK_ORDER, MAX_CARDS, TOTAL_CARDS
from .gacha import open_bulk_packs
from .state import fresh_inventory, fresh_pack_counts

def render_monte_carlo_tab():
    st.header("📊 Monte Carlo Simulator")
    st.markdown("Chạy mô phỏng mở **Giỏ Hàng (Cart)** hàng ngàn lần để tính xác suất hoàn thành Album và sự phân bổ của Thẻ/Sao dư thừa.")
    
    # Check if cart is empty
    cart_packs = st.session_state.get("cart_packs", {})
    cart_chests = {
        1: st.session_state.get("bulk_chest_1", 0),
        2: st.session_state.get("bulk_chest_2", 0),
        3: st.session_state.get("bulk_chest_3", 0)
    }
    
    total_cart_packs = sum(cart_packs.values())
    total_cart_chests = sum(cart_chests.values())
    
    if total_cart_packs == 0 and total_cart_chests == 0:
        st.warning("Giỏ hàng của bạn đang trống! Hãy sang tab **LiveOps Economy**, **Mở Gói (Gacha)**, hoặc **Chest Drop** để thêm thẻ/rương vào giỏ.")
        return
        
    cart_pack_str = ', '.join([f'{v} {k}' for k, v in cart_packs.items() if v > 0])
    cart_chest_str = ', '.join([f'{v} Rương {k}-Sao' for k, v in cart_chests.items() if v > 0])
    
    if cart_pack_str and cart_chest_str:
        st.info(f"**Giỏ Hàng Pack:** {cart_pack_str}\n | 🛒 **Giỏ Hàng Chest:** {cart_chest_str}", icon="🛒")
    elif cart_pack_str:
        st.info(f"**Giỏ Hàng Pack:** {cart_pack_str}", icon="🛒")
    else:
        st.info(f"**Giỏ Hàng Chest:** {cart_chest_str}", icon="🛒")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        iterations = st.number_input("Số lần chạy mô phỏng (Iterations)", min_value=10, max_value=5000, value=100, step=10)
        simulate_from_scratch = st.checkbox("🔄 Bắt đầu từ Kho Thẻ Trống", value=True, help="Nếu bật, mỗi lần chạy sẽ bắt đầu với 0 thẻ và 0 sao (Mô phỏng từ đầu game). Nếu tắt, sẽ bốc tiếp trên số thẻ bạn đang có hiện tại.")
        auto_chest = st.checkbox("🔄 Tự động dùng sao dư để đổi Star Chest", value=True, help="Hệ thống sẽ tự động mua rương xịn nhất có thể (Vàng -> Bạc -> Đồng) cho đến khi không đủ sao (dưới 100 sao).")
        start_btn = st.button("🚀 BẮT ĐẦU MÔ PHỎNG", type="primary", use_container_width=True)
        
    if start_btn:
        with st.spinner(f"Đang giả lập {iterations} lần bóc..."):
            results = run_monte_carlo(st.session_state, cart_packs, cart_chests, iterations, simulate_from_scratch, auto_chest)
            st.session_state["mc_results"] = results
            
    if "mc_results" in st.session_state:
        res = st.session_state["mc_results"]
        render_monte_carlo_results(res, iterations, total_cart_packs, total_cart_chests, auto_chest)


def run_monte_carlo(base_state, cart_packs, cart_chests, iterations, simulate_from_scratch=True, auto_chest=False):
    cards_collected = []
    stars_collected = []
    grand_album_count = []
    total_dups = []
    total_stars_earned = []
    
    for _ in range(iterations):
        # Create an isolated dummy state
        sim_state = {
            "inventory": fresh_inventory() if simulate_from_scratch else copy.deepcopy(base_state["inventory"]),
            "stars": 0 if simulate_from_scratch else base_state["stars"],
            "total_packs": 0 if simulate_from_scratch else base_state["total_packs"],
            "pack_counts": fresh_pack_counts() if simulate_from_scratch else copy.deepcopy(base_state["pack_counts"]),
            "pack_pity": fresh_pack_counts() if simulate_from_scratch else copy.deepcopy(base_state["pack_pity"]),
            "log": [], # We don't care about logs in MC
            "card_rush_enabled": base_state["card_rush_enabled"],
            "grand_album_enabled": base_state["grand_album_enabled"],
            "grand_album_completions": 0 if simulate_from_scratch else base_state.get("grand_album_completions", 0),
            "grand_album_finished": False if simulate_from_scratch else base_state.get("grand_album_finished", False),
            "new_card_formula_type": base_state["new_card_formula_type"],
            "config_packs": base_state["config_packs"],
            "new_card_power": base_state.get("new_card_power", 1.0),
            "pity_multiplier": base_state.get("pity_multiplier", 1.0),
            "owned_cards": set() if simulate_from_scratch else copy.deepcopy(base_state.get("owned_cards", set())),
            "total_cards_drawn": 0 if simulate_from_scratch else base_state.get("total_cards_drawn", 0),
            "new_cards_drawn": 0 if simulate_from_scratch else base_state.get("new_cards_drawn", 0),
            "dup_cards_drawn": 0 if simulate_from_scratch else base_state.get("dup_cards_drawn", 0),
            "new_cards_by_rarity": {r: 0 for r in range(1, 7)} if simulate_from_scratch else copy.deepcopy(base_state.get("new_cards_by_rarity", {r: 0 for r in range(1, 7)})),
            "dup_cards_by_rarity": {r: 0 for r in range(1, 7)} if simulate_from_scratch else copy.deepcopy(base_state.get("dup_cards_by_rarity", {r: 0 for r in range(1, 7)})),
            "pack_stars_gained": 0 if simulate_from_scratch else base_state.get("pack_stars_gained", 0),
            "cd_total_cards_drawn": 0 if simulate_from_scratch else base_state.get("cd_total_cards_drawn", 0),
            "cd_new_cards_drawn": 0 if simulate_from_scratch else base_state.get("cd_new_cards_drawn", 0),
            "cd_dup_cards_drawn": 0 if simulate_from_scratch else base_state.get("cd_dup_cards_drawn", 0),
            "cd_stars_gained": 0 if simulate_from_scratch else base_state.get("cd_stars_gained", 0),
            "chest_drop_counts": {r: 0 for r in range(1, 6)} if simulate_from_scratch else copy.deepcopy(base_state.get("chest_drop_counts", {r: 0 for r in range(1, 6)})),
            "config_chest_drop_tiers": base_state.get("config_chest_drop_tiers", {}),
            "config_chest_upgrade_matrix": base_state.get("config_chest_upgrade_matrix", {}),
            "config_chest_drop_x": base_state.get("config_chest_drop_x", 2.0),
            "cd_new_cards_by_rarity": {r: 0 for r in range(1, 7)} if simulate_from_scratch else copy.deepcopy(base_state.get("cd_new_cards_by_rarity", {r: 0 for r in range(1, 7)})),
            "cd_dup_cards_by_rarity": {r: 0 for r in range(1, 7)} if simulate_from_scratch else copy.deepcopy(base_state.get("cd_dup_cards_by_rarity", {r: 0 for r in range(1, 7)})),
            "opened_pack_types_ss2": set() if simulate_from_scratch else copy.deepcopy(base_state.get("opened_pack_types_ss2", set())),
            "ss2_optimize_collection": base_state.get("ss2_optimize_collection", True),
            "config_ss2_s_base": base_state.get("config_ss2_s_base", 0.1),
            "config_ss2_s_max": base_state.get("config_ss2_s_max", 0.5),
            "config_ss2_c_base": base_state.get("config_ss2_c_base", 0.3),
            "config_ss2_c_max": base_state.get("config_ss2_c_max", 1.0),
        }
        
        # Run the bulk open packs (without auto_chest yet)
        open_bulk_packs(sim_state, cart_packs, auto_chest=False)
        
        # Run the bulk open chests
        from .gacha import process_chest_drop_hit
        for start_tier, count in cart_chests.items():
            for _ in range(count):
                current_t = start_tier
                drawn_in_batch = set()
                for _ in range(5):
                    res = process_chest_drop_hit(sim_state, start_tier, current_t, drawn_in_batch)
                    current_t = res["next_tier"]
                    
        # NOW run auto chest with combined stars
        if auto_chest:
            from .gacha import run_auto_chests
            run_auto_chests(sim_state)
            
        # Record results
        total_cards = sim_state["grand_album_completions"] * TOTAL_CARDS + sum(sim_state["inventory"].values())
        cards_collected.append(total_cards)
        stars_collected.append(sim_state["stars"])
        grand_album_count.append(sim_state["grand_album_completions"])
        total_dups.append(sim_state.get("dup_cards_drawn", 0) + sim_state.get("cd_dup_cards_drawn", 0))
        total_stars_earned.append(sim_state.get("pack_stars_gained", 0) + sim_state.get("cd_stars_gained", 0))
        
    return {
        "cards": cards_collected,
        "stars": stars_collected,
        "grand_albums": grand_album_count,
        "total_dups": total_dups,
        "total_stars_earned": total_stars_earned
    }


def render_monte_carlo_results(res, iterations, total_cart_packs, total_cart_chests, auto_chest):
    st.divider()
    st.subheader(f"📈 Kết quả sau {iterations} lần chạy")
    
    df = pd.DataFrame(res)
    
    # Calculate completions
    start_completions = 0 if st.session_state.get("simulate_from_scratch", True) else st.session_state.get("grand_album_completions", 0)
    start_inventory = 0 if st.session_state.get("simulate_from_scratch", True) else sum(st.session_state["inventory"].values())
    start_total_cards = start_completions * TOTAL_CARDS + start_inventory
    start_stars = 0 if st.session_state.get("simulate_from_scratch", True) else st.session_state.get("stars", 0)
    start_dups = 0 if st.session_state.get("simulate_from_scratch", True) else st.session_state.get("dup_cards_drawn", 0) + st.session_state.get("cd_dup_cards_drawn", 0)
    
    # Metrics (Deltas)
    avg_cards_gained = df["cards"].mean() - start_total_cards
    max_cards_gained = df["cards"].max() - start_total_cards
    min_cards_gained = df["cards"].min() - start_total_cards
    
    completions = df[df["grand_albums"] > start_completions]
    completion_rate = len(completions) / iterations * 100
    
    avg_dups_gained = df.get("total_dups", pd.Series([0])).mean() - start_dups
    
    total_drawn = avg_cards_gained + avg_dups_gained
    dup_rate = (avg_dups_gained / total_drawn * 100) if total_drawn > 0 else 0
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Hoàn thành Album", f"{completion_rate:.1f}%")
    c2.metric("Thẻ Mới Thu Thập", f"{avg_cards_gained:.1f}")
    c3.metric("Thẻ Trùng (Dups)", f"{avg_dups_gained:.1f}")
    c4.metric("♻️ Tỉ lệ Thẻ Trùng", f"{avg_dups_gained:.1f}/{total_drawn:.1f} ({dup_rate:.2f}%)")
    
    st.write("")
    c5, c6, c7, c8 = st.columns(4)
    
    c5.metric("Max Thẻ Mới", f"{max_cards_gained}")
    c6.metric("Min Thẻ Mới", f"{min_cards_gained}")
    
    if auto_chest:
        avg_stars = df["stars"].mean()
        c7.metric("Trung bình Sao Dư Thừa", f"{avg_stars:.0f} ⭐")
    else:
        avg_stars_gained = df["stars"].mean() - start_stars
        c7.metric("Trung bình Sao Nhận Được", f"{avg_stars_gained:.0f} ⭐")
        
    c8.empty()
    
    # Charts
    st.info("💡 **Lưu ý:** Để biểu đồ hiển thị chuẩn xác và không bị gãy đoạn do cơ chế Reset của Grand Album, **Số Thẻ Cuối Cùng** sẽ được cộng dồn liên tục nếu bạn vượt quá 135 thẻ. (VD: Nếu bạn full album bị reset về 0, rồi bóc thêm được 10 thẻ nữa, hệ thống sẽ ghi nhận bạn có 145 thẻ).")
    
    def bin_data(series, num_bins=20):
        min_val = int(series.min())
        max_val = int(series.max())
        if max_val == min_val:
            return pd.Series([str(min_val)] * len(series), index=series.index)
            
        step = max(1, (max_val - min_val) // num_bins + 1)
        bins = list(range(min_val, max_val + step + 1, step))
        labels = []
        for i in range(len(bins)-1):
            start = bins[i]
            end = bins[i+1] - 1
            if start == end:
                labels.append(str(start))
            else:
                labels.append(f"{start} - {end}")
        return pd.cut(series, bins=bins, right=False, labels=labels, include_lowest=True)

    df["cards_group"] = bin_data(df["cards"], 20)
    df["stars_group"] = bin_data(df["stars"], 20)
    
    cards_summary = df.groupby("cards_group", observed=True).size().reset_index(name="count")
    stars_summary = df.groupby("stars_group", observed=True).size().reset_index(name="count")

    st.subheader("Phân bổ Số lượng Thẻ thu thập được")
    chart_cards = alt.Chart(cards_summary).mark_bar(opacity=0.8, color="#4CAF50").encode(
        alt.X("cards_group:O", title="Số Thẻ Cuối Cùng", axis=alt.Axis(labelAngle=-45), sort=cards_summary["cards_group"].tolist()),
        alt.Y('count:Q', title="Số Lần Lặp (Tần suất)"),
        tooltip=[alt.Tooltip('cards_group:O', title='Số Thẻ'), alt.Tooltip('count:Q', title='Số Lần Lặp')]
    )
    st.altair_chart(chart_cards, use_container_width=True)
    
    st.subheader("Phân bổ Số Sao dư thừa")
    chart_stars = alt.Chart(stars_summary).mark_bar(opacity=0.8, color="#FFC107").encode(
        alt.X("stars_group:O", title="Tổng số Sao", axis=alt.Axis(labelAngle=-45), sort=stars_summary["stars_group"].tolist()),
        alt.Y('count:Q', title="Số Lần Lặp (Tần suất)"),
        tooltip=[alt.Tooltip('stars_group:O', title='Tổng số Sao'), alt.Tooltip('count:Q', title='Số Lần Lặp')]
    )
    st.altair_chart(chart_stars, use_container_width=True)
```

---

## File: `card_album/rewards_data.py`

```python
MASTER_PASS_FREE = \
{0: '1x Hammer',
 1: '15m Heart',
 2: '**1x Bronze Pack**',
 3: '40 Coins',
 4: '1x Scissors',
 5: 'Chest: 1x Scissors + **1x Bronze Pack**',
 6: '60 Coins',
 7: '15m Heart',
 8: '1x Hammer',
 9: '1x Broom',
 10: 'Chest: 1x Scissors + 1x Hammer + **1x Emerald Pack**',
 11: '1x Hammer',
 12: '**1x Silver Pack**',
 13: '30m Heart',
 14: '1x Scissors',
 15: 'Chest: 1x Scissors + 1x Broom + **1x Silver Pack**',
 16: '80 Coins',
 17: '**1x Emerald Pack**',
 18: '1x Scissors',
 19: '30m Heart',
 20: 'Chest: 1x Hammer + 1x Broom + **1x Amethyst Pack**',
 21: '1x Hammer',
 22: '100 Coins',
 23: '30m Heart',
 24: '**1x Emerald Pack**',
 25: 'Chest: 1x Boosters Set + **1x Silver Pack**',
 26: '1x Hammer',
 27: '1x Scissors',
 28: '**1x Silver Pack**',
 29: '1x Broom',
 30: 'Chest: 200 Coins + 1x Boosters Set + **1x Ruby Pack**'}

MASTER_PASS_PREMIUM = \
{0: '8-Heart Limit + 600 Coins',
 1: '30m Heart',
 2: '**1x Emerald Pack**',
 3: '1x Scissors',
 4: '1x Hammer',
 5: 'Chest: 100 Coins + 1x Broom + **1x Emerald Pack**',
 6: '1x Scissors',
 7: '30m Heart',
 8: '1x Hammer',
 9: '1x Broom',
 10: 'Chest: 150 Coins + 1x Hammer + 1x Broom + **1x Silver Pack**',
 11: '2x Scissors',
 12: '**1x Amethyst Pack**',
 13: '60m Heart',
 14: '1x Broom',
 15: 'Chest: 200 Coins + 1x Boosters Set + **1x Silver Pack**',
 16: '2x Hammer',
 17: '**1x Silver Pack**',
 18: '2x Scissors',
 19: '60m Heart',
 20: 'Chest: 300 Coins + 60m Heart + 1x Boosters Set + **1x Amethyst Pack**',
 21: '2x Hammer',
 22: '2x Broom',
 23: '60m Heart',
 24: '**1x Silver Pack**',
 25: 'Chest: 500 Coins + 60m Heart + 2x Boosters Set + **1x Ruby Pack**',
 26: '3x Hammer',
 27: '3x Scissors',
 28: '**1x Amethyst Pack**',
 29: '3x Broom',
 30: 'Chest: 750 Coins + 60m Heart + 3x Boosters Set + **1x Rainbow Pack**'}

WIN_STREAK_REWARDS = \
{2: '40 Coins',
 5: '1x Scissors + **1x Bronze Pack**',
 8: '15m Heart + 1x Hammer',
 11: '80 Coins + **1x Emerald Pack**',
 15: '1x Broom',
 20: '30m Heart + **1x Silver Pack**',
 25: '160 Coins',
 30: '2x Scissors + **1x Amethyst Pack**',
 35: '1h Heart + 1x Hammer + 1x Broom',
 45: '500 Coins + 1x Boosters Set + Avatar (Hoặc **1x Ruby Pack** nếu đã sở hữu Avatar)'}

KEY_COLLECTION_REWARDS = \
{1: '15m Heart',
 2: '1x Scissors',
 3: '15m x2 Key',
 4: '**1x Bronze Pack**',
 5: '1x Hammer',
 6: '1x Broom',
 7: '**1x Bronze Pack**',
 8: '30m x2 Key',
 9: '1x Scissors',
 10: '**1x Emerald Pack**',
 11: '30m Heart',
 12: '80 Coins',
 13: '**1x Emerald Pack**',
 14: '1x Broom',
 15: '30m x2 Key',
 16: '120 Coins',
 17: '**1x Silver Pack**',
 18: '1x Scissors',
 19: '1h Heart',
 20: '200 Coins',
 21: '**1x Amethyst Pack**',
 22: '1x Hammer',
 23: '1h x2 Key',
 24: '**1x Ruby Pack**',
 25: '1000 Coins'}

```

---

## File: `card_album/scratch_gacha.py`

```python
import re

with open('d:/Python/demo/card_album/gacha.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_pick = '''def pick_new_card(session_state, rarity: int):
    possible_cards = []
    from .config import CARD_SETS
    for set_id, set_info in CARD_SETS.items():
        if rarity in set_info["cards"]:
            count = set_info["cards"][rarity]
            for idx in range(count):
                possible_cards.append((set_id, rarity, idx))
                
    missing_cards = [c for c in possible_cards if c not in session_state["owned_cards"]]
    import random
    if missing_cards:
        chosen_card = random.choice(missing_cards)
        session_state["owned_cards"].add(chosen_card)
        return chosen_card
    return None

def pick_dup_card(session_state, rarity: int):
    owned = [c for c in session_state["owned_cards"] if c[1] == rarity]
    import random
    if owned:
        return random.choice(owned)
    possible_cards = []
    from .config import CARD_SETS
    for set_id, set_info in CARD_SETS.items():
        if rarity in set_info["cards"]:
            count = set_info["cards"][rarity]
            for idx in range(count):
                possible_cards.append((set_id, rarity, idx))
    return random.choice(possible_cards) if possible_cards else None
'''

content = re.sub(r'def pick_new_card.*?session_state\["owned_cards"\].add\(chosen_card\)', new_pick.strip(), content, flags=re.DOTALL)

roll_card_orig = '''def roll_card(session_state, rarity: int, pity_bonus: float, pack_type: str) -> tuple[str, int]:
    session_state["total_cards_drawn"] += 1
    cards_owned = session_state["inventory"][rarity]
    max_cards = MAX_CARDS[rarity]
    
    if cards_owned >= max_cards:
        final_chance = 0.0
    else:
        new_chance = calculate_new_chance(session_state, rarity, pack_type)
        final_chance = min(1.0, new_chance + pity_bonus)

    if random.random() < final_chance:
        session_state["inventory"][rarity] += 1
        pick_new_card(session_state, rarity)
        session_state["new_cards_drawn"] += 1
        check_grand_album(session_state)
        return "NEW", rarity

    session_state["stars"] += STAR_VALUES[rarity]
    session_state["dup_cards_drawn"] += 1
    return "DUP", rarity'''

roll_card_new = '''def roll_card(session_state, rarity: int, pity_bonus: float, pack_type: str) -> tuple[str, int, tuple]:
    session_state["total_cards_drawn"] += 1
    cards_owned = session_state["inventory"][rarity]
    max_cards = MAX_CARDS[rarity]
    
    if cards_owned >= max_cards:
        final_chance = 0.0
    else:
        new_chance = calculate_new_chance(session_state, rarity, pack_type)
        final_chance = min(1.0, new_chance + pity_bonus)

    if random.random() < final_chance:
        session_state["inventory"][rarity] += 1
        c = pick_new_card(session_state, rarity)
        session_state["new_cards_drawn"] += 1
        check_grand_album(session_state)
        if "recent_draws" in session_state: session_state["recent_draws"].append(("NEW", rarity, c))
        return "NEW", rarity, c

    session_state["stars"] += STAR_VALUES[rarity]
    session_state["dup_cards_drawn"] += 1
    c = pick_dup_card(session_state, rarity)
    if "recent_draws" in session_state: session_state["recent_draws"].append(("DUP", rarity, c))
    return "DUP", rarity, c'''

content = content.replace(roll_card_orig, roll_card_new)

rainbow_orig = '''def open_rainbow_pack_guaranteed(session_state) -> tuple[str, int]:
    session_state["total_cards_drawn"] += 1
    if session_state["inventory"][6] < MAX_CARDS[6]:
        session_state["inventory"][6] += 1
        pick_new_card(session_state, 6)
        session_state["new_cards_drawn"] += 1
        check_grand_album(session_state)
        return "NEW", 6

    missing_rarities = [r for r in [1, 2, 3, 4, 5] if session_state["inventory"][r] < MAX_CARDS[r]]
    if missing_rarities:
        rarity = random.choice(missing_rarities)
        session_state["inventory"][rarity] += 1
        pick_new_card(session_state, rarity)
        session_state["new_cards_drawn"] += 1
        check_grand_album(session_state)
        return "NEW", rarity

    session_state["stars"] += STAR_VALUES[6]
    session_state["dup_cards_drawn"] += 1
    return "DUP", 6'''

rainbow_new = '''def open_rainbow_pack_guaranteed(session_state) -> tuple[str, int, tuple]:
    session_state["total_cards_drawn"] += 1
    if session_state["inventory"][6] < MAX_CARDS[6]:
        session_state["inventory"][6] += 1
        c = pick_new_card(session_state, 6)
        session_state["new_cards_drawn"] += 1
        check_grand_album(session_state)
        if "recent_draws" in session_state: session_state["recent_draws"].append(("NEW", 6, c))
        return "NEW", 6, c

    missing_rarities = [r for r in [1, 2, 3, 4, 5] if session_state["inventory"][r] < MAX_CARDS[r]]
    if missing_rarities:
        rarity = random.choice(missing_rarities)
        session_state["inventory"][rarity] += 1
        c = pick_new_card(session_state, rarity)
        session_state["new_cards_drawn"] += 1
        check_grand_album(session_state)
        if "recent_draws" in session_state: session_state["recent_draws"].append(("NEW", rarity, c))
        return "NEW", rarity, c

    session_state["stars"] += STAR_VALUES[6]
    session_state["dup_cards_drawn"] += 1
    c = pick_dup_card(session_state, 6)
    if "recent_draws" in session_state: session_state["recent_draws"].append(("DUP", 6, c))
    return "DUP", 6, c'''

content = content.replace(rainbow_orig, rainbow_new)

content = content.replace('status, final_rarity = roll_card(', 'status, final_rarity, specific_card = roll_card(')
content = content.replace('raw_results.append((status, final_rarity))', 'raw_results.append((status, final_rarity, specific_card))')
content = content.replace('wild_status, wild_rarity = open_rainbow_pack_guaranteed(', 'wild_status, wild_rarity, wild_specific_card = open_rainbow_pack_guaranteed(')
content = content.replace('raw_results.append((wild_status, wild_rarity))', 'raw_results.append((wild_status, wild_rarity, wild_specific_card))')
content = content.replace('for status, rarity in raw_results:', 'for status, rarity, specific_card in raw_results:')
content = content.replace('pack_results.append((status, rarity, guaranteed))', 'pack_results.append((status, rarity, specific_card, guaranteed))')

log_orig = '''def format_pack_log(session_state, pack_type: str, pack_results: list[tuple[str, int, bool]], pity_message: str, got_new: bool) -> str:
    result_parts = []
    for status, rarity, guaranteed in pack_results:
        label = f"{rarity}-Sao" if rarity < 6 else "Thẻ VÀNG"
        suffix = " [Bảo Hiểm]" if guaranteed else ""
        result_parts.append(f"{label} ({status}){suffix}")'''

log_new = '''def format_card_name(card):
    from .config import CARD_SETS
    if not card: return "?"
    set_id, rarity, idx = card
    return f"{CARD_SETS[set_id]['name']} #{idx+1}"

def format_pack_log(session_state, pack_type: str, pack_results: list[tuple[str, int, tuple, bool]], pity_message: str, got_new: bool) -> str:
    result_parts = []
    for status, rarity, specific_card, guaranteed in pack_results:
        label = f"{rarity}-Sao" if rarity < 6 else "Thẻ VÀNG"
        cname = format_card_name(specific_card)
        suffix = " [Bảo Hiểm]" if guaranteed else ""
        result_parts.append(f"{label} [{cname}] ({status}){suffix}")'''

content = content.replace(log_orig, log_new)

bulk_orig = '''    add_log(session_state, f"========== BẮT ĐẦU MỞ NHIỀU ({total_to_open} PACKS) ==========")
    
    start_new = session_state.get("new_cards_drawn", 0)'''

bulk_new = '''    add_log(session_state, f"========== BẮT ĐẦU MỞ NHIỀU ({total_to_open} PACKS) ==========")
    session_state["recent_draws"] = []
    start_new = session_state.get("new_cards_drawn", 0)'''
content = content.replace(bulk_orig, bulk_new)

bulk_orig2 = '''    new_drawn = session_state.get("new_cards_drawn", 0) - start_new
    dup_drawn = session_state.get("dup_cards_drawn", 0) - start_dup
    total_drawn = session_state.get("total_cards_drawn", 0) - start_total
    stars_diff = session_state.get("stars", 0) - start_stars
    
    return {
        "success": True, 
        "message": f"Đã mở thành công {total_to_open} pack!",
        "summary": summary,
        "new_cards": new_drawn,
        "dup_cards": dup_drawn,
        "total_cards": total_drawn,
        "stars_diff": stars_diff,
        "chests_opened": chests_opened
    }'''

bulk_new2 = '''    new_drawn = session_state.get("new_cards_drawn", 0) - start_new
    dup_drawn = session_state.get("dup_cards_drawn", 0) - start_dup
    total_drawn = session_state.get("total_cards_drawn", 0) - start_total
    stars_diff = session_state.get("stars", 0) - start_stars
    
    new_cards_list = [c for s, r, c in session_state.get("recent_draws", []) if s == "NEW"]
    dup_cards_list = [c for s, r, c in session_state.get("recent_draws", []) if s == "DUP"]
    if "recent_draws" in session_state: del session_state["recent_draws"]

    return {
        "success": True, 
        "message": f"Đã mở thành công {total_to_open} pack!",
        "summary": summary,
        "new_cards": new_drawn,
        "dup_cards": dup_drawn,
        "total_cards": total_drawn,
        "stars_diff": stars_diff,
        "chests_opened": chests_opened,
        "new_cards_list": new_cards_list,
        "dup_cards_list": dup_cards_list
    }'''
content = content.replace(bulk_orig2, bulk_new2)

with open('d:/Python/demo/card_album/gacha.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated successfully")
```

---

## File: `card_album/scratch_gacha_counters.py`

```python
import re

with open('d:/Python/demo/card_album/gacha.py', 'r', encoding='utf-8') as f:
    content = f.read()

# roll_card
content = content.replace(
    'session_state["new_cards_drawn"] += 1\n        check_grand_album',
    'session_state["new_cards_drawn"] += 1\n        session_state["new_cards_by_rarity"][rarity] += 1\n        check_grand_album'
)

content = content.replace(
    'session_state["dup_cards_drawn"] += 1\n    c = pick_dup_card',
    'session_state["dup_cards_drawn"] += 1\n    session_state["dup_cards_by_rarity"][rarity] += 1\n    c = pick_dup_card'
)

# open_rainbow_pack_guaranteed
content = content.replace(
    'session_state["new_cards_drawn"] += 1\n        check_grand_album(session_state)\n        if "recent_draws" in session_state: session_state["recent_draws"].append(("NEW", 6, c))',
    'session_state["new_cards_drawn"] += 1\n        session_state["new_cards_by_rarity"][6] += 1\n        check_grand_album(session_state)\n        if "recent_draws" in session_state: session_state["recent_draws"].append(("NEW", 6, c))'
)

content = content.replace(
    'session_state["new_cards_drawn"] += 1\n        check_grand_album(session_state)\n        if "recent_draws" in session_state: session_state["recent_draws"].append(("NEW", rarity, c))',
    'session_state["new_cards_drawn"] += 1\n        session_state["new_cards_by_rarity"][rarity] += 1\n        check_grand_album(session_state)\n        if "recent_draws" in session_state: session_state["recent_draws"].append(("NEW", rarity, c))'
)

content = content.replace(
    'session_state["dup_cards_drawn"] += 1\n    c = pick_dup_card(session_state, 6)',
    'session_state["dup_cards_drawn"] += 1\n    session_state["dup_cards_by_rarity"][6] += 1\n    c = pick_dup_card(session_state, 6)'
)

with open('d:/Python/demo/card_album/gacha.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated successfully")
```

---

## File: `card_album/state.py`

```python
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


def reset_progress(session_state) -> None:
    keys_to_clear = [
        "inventory", "stars", "total_packs", "pack_counts", 
        "pack_pity", "log", "grand_album_completions", "grand_album_finished",
        "owned_cards", "total_cards_drawn", "new_cards_drawn", "dup_cards_drawn", "pack_stars_gained",
        "new_cards_by_rarity", "dup_cards_by_rarity",
        "cd_total_cards_drawn", "cd_new_cards_drawn", "cd_dup_cards_drawn", "cd_stars_gained",
        "cd_new_cards_by_rarity", "cd_dup_cards_by_rarity", "chest_drop_counts", "opened_pack_types_ss2"
    ]
    for k in keys_to_clear:
        session_state.pop(k, None)
    ensure_album_state(session_state)


def total_cards_collected(session_state) -> int:
    return sum(session_state["inventory"].values())

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
```

---

## File: `card_album/ui/__init__.py`

```python
from .main import run_app
```

---

## File: `card_album/ui/analytics.py`

```python
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

def render_analytics_tab() -> None:
    st.header("📈 LiveOps Economy Simulator")
    st.markdown("Giả lập số lượng gói thẻ nhận được từ các sự kiện LiveOps dựa trên số ngày chơi và nỗ lực cày cuốc.")
    
    col1, col2 = st.columns([1, 1.5])
    
    with col1:
        st.subheader("🗓️ Thông số Cày cuốc")
        days = st.number_input("Số Ngày (Mùa giải)", min_value=1, max_value=365, value=60)
        
        st.markdown("**Số Level chơi mỗi ngày**")
        input_mode = st.radio("Chế độ nhập liệu:", ["Cố định (Fixed)", "Khoảng ngẫu nhiên (Range)"], horizontal=True, label_visibility="collapsed")
        
        if input_mode == "Khoảng ngẫu nhiên (Range)":
            levels_per_weekday = st.slider("Trong tuần (T2-T5)", min_value=0, max_value=100, value=(5, 7))
            levels_per_weekend = st.slider("Cuối tuần (T6-CN)", min_value=0, max_value=100, value=(12, 15))
        else:
            col_lvl1, col_lvl2 = st.columns(2)
            with col_lvl1:
                levels_per_weekday_val = st.number_input("Trong tuần (T2-T5)", min_value=0, max_value=100, value=5)
            with col_lvl2:
                levels_per_weekend_val = st.number_input("Cuối tuần (T6-CN)", min_value=0, max_value=100, value=15)
            levels_per_weekday = (levels_per_weekday_val, levels_per_weekday_val)
            levels_per_weekend = (levels_per_weekend_val, levels_per_weekend_val)
        
        st.subheader("🎯 Bật/Tắt LiveOps")
        toggles = {}
        toggles["core_gameplay"] = st.toggle(
            "⚔️ Core Gameplay (Thưởng Level Khó)",
            value=True,
            help="Thưởng 1 Bronze khi thắng Hard, 1 Emerald khi thắng Super Hard."
        )
        toggles["win_streak"] = st.toggle("Win Streak", value=True,
            help="Nhận phần thưởng khi đạt các chuỗi thắng liên tiếp (Sự kiện diễn ra từ T6-CN hàng tuần, reset mỗi đầu sự kiện).")
        toggles["key_collection"] = st.toggle(
            "🔑 Key Collection", 
            value=True,
            help="Tích lũy chìa khóa qua các màn chơi để mở khóa phần thưởng."
        )
        toggles["master_pass"] = st.toggle(
            "🎟️ Master Pass", 
            value=True,
            help="Hệ thống Battle Pass của game, gồm nhánh Free và Premium."
        )
        
        if toggles["master_pass"]:
            toggles["master_pass_premium"] = st.checkbox("Mở khóa nhánh Premium (Yarn Pass) - $9.99", value=False)
        else:
            toggles["master_pass_premium"] = False
            
        toggles["card_rush"] = st.toggle(
            "⚡ Card Rush", 
            value=True,
            help="Nhân thêm số lượng thẻ cho các gói nhận được vào ngày sự kiện."
        )
        toggles["chest_drop"] = st.toggle(
            "🎮 Chest Drop",
            value=True,
            help="Nhận Rương 1-Sao (3 win), 2-Sao (7 win), 3-Sao (12 win) hàng ngày."
        )
            
        st.subheader("🛒 Cửa Hàng & IAP")
        iap_selections = {}
        
        with st.expander("🛍️ Main Shop Bundles", expanded=False):
            iap_selections["shop_9.99"] = st.number_input("$9.99 (Decorated Pouch): +1 Silver Pack", min_value=0, value=0)
            iap_selections["shop_19.99"] = st.number_input("$19.99 (Artisan Satchel): +1 Amethyst Pack", min_value=0, value=0)
            iap_selections["shop_29.99"] = st.number_input("$29.99 (Exquisite Basket): +1 Ruby Pack", min_value=0, value=0)
            iap_selections["shop_49.99"] = st.number_input("$49.99 (Overflowing Chest): +1 Rainbow Pack", min_value=0, value=0)
            iap_selections["shop_99.99"] = st.number_input("$99.99 (Royal Vault): +3 Rainbow Pack", min_value=0, value=0)
            
        with st.expander("💸 Out Of Coins", expanded=False):
            iap_selections["ooc_4"] = st.number_input("Super OOC 4 ($6.99): 2000 Coins + 2x Scissors + 1x Emerald Pack", min_value=0, value=0)
            iap_selections["ooc_5"] = st.number_input("OOC 5 ($14.99): 5000 Coins + 3x Scissors + 2x Hammer + 1x Silver Pack", min_value=0, value=0)
            iap_selections["ooc_6"] = st.number_input("OOC 6 ($29.99): 11000 Coins + 4x Scissors + 3x Hammer + 2x Broom + 1x Amethyst Pack", min_value=0, value=0)
        
        with st.expander("🔗 Chain Offer", expanded=False):
            st.info("💡 Part 1 (Miễn phí) luôn được tự động nhận: **1x Bronze Pack** + 1x Scissors + 15m Heart.")
            iap_selections["chain_part_2"] = st.checkbox("Mua Part 2 ($2.49) -> Nhận toàn bộ Part 2: **1x Emerald, 1x Bronze**, 900 Coins, 1x Scissors, 1x Hammer, 30m Heart", value=False)
            iap_selections["chain_part_3"] = st.checkbox("Mua Part 3 ($4.99) -> Nhận toàn bộ Part 3: **1x Silver, 1x Emerald**, 1800 Coins, 1x Scissors, 1x Hammer, 1x Broom, 60m Heart", value=False)
            iap_selections["chain_part_4"] = st.checkbox("Mua Part 4 ($10.99) -> Nhận toàn bộ Part 4: **1x Amethyst, 1x Emerald, 1x Silver**, 4000 Coins, 3x Scissors, 3x Hammer, 1x Broom, 1h Heart", value=False)
            iap_selections["chain_part_5"] = st.checkbox("Mua Part 5 ($18.99) -> Nhận toàn bộ Part 5: **1x Ruby, 1x Amethyst, 1x Silver**, 8300 Coins, 2x Scissors, 2x Hammer, 2x Broom, 4h Heart", value=False)
            iap_selections["chain_part_6"] = st.checkbox("Mua Part 6 ($27.99) -> Nhận toàn bộ Part 6: **1x Gold, 1x Silver, 1x Amethyst**, 13200 Coins, 4x Scissors, 4x Hammer, 3x Broom, 6h Heart", value=False)
            iap_selections["chain_part_7"] = st.checkbox("Mua Part 7 ($49.99) -> Nhận toàn bộ Part 7: **1x Rainbow, 1x Ruby, 1x Emerald, 1x Silver, 1x Amethyst**, 25500 Coins, 4x Scissors, 4x Hammer, 4x Broom, 12h Heart", value=False)
            
    with col2:
        if st.button("🧮 TÍNH TOÁN PHẦN THƯỞNG", type="primary", use_container_width=True):
            res = simulate_liveops(days, levels_per_weekday, levels_per_weekend, toggles, iap_selections, st.session_state["config_rewards"])
            st.session_state["liveops_result"] = res
            
        if "liveops_result" in st.session_state:
            res = st.session_state["liveops_result"]
            st.success("✅ **Đã tính toán xong**")
            
            with st.expander("⚙️ Các giả định (Assumptions) của hệ thống", expanded=True):
                for asm in res.get("assumptions", []):
                    st.markdown(f"- {asm}")
            
            lvl = res["levels_info"]
            st.markdown(f"**Tổng quan Level:** Chơi {lvl['total']} màn (Thắng: {lvl['normal']} Normal, {lvl['hard']} Hard, {lvl['super_hard']} Super Hard)")
            
            st.subheader("📦 Tổng số Gói (Packs) Nhận Được")
            total = res["total_packs"]
            c1, c2, c3, c4 = st.columns(4)
            c1.metric(f"{PACK_ICONS['Bronze']} Bronze", total["Bronze"])
            c2.metric(f"{PACK_ICONS['Emerald']} Emerald", total["Emerald"])
            c3.metric(f"{PACK_ICONS['Silver']} Silver", total["Silver"])
            c4.metric(f"{PACK_ICONS['Amethyst']} Amethyst", total["Amethyst"])
            
            if total.get("Bronze+") or total.get("Emerald+") or total.get("Silver+"):
                cp1, cp2, cp3, _ = st.columns(4)
                cp1.metric(f"{PACK_ICONS['Bronze+']} Bronze+", total.get("Bronze+", 0))
                cp2.metric(f"{PACK_ICONS['Emerald+']} Emerald+", total.get("Emerald+", 0))
                cp3.metric(f"{PACK_ICONS['Silver+']} Silver+", total.get("Silver+", 0))
            
            c5, c6, c7, c8 = st.columns(4)
            c5.metric(f"{PACK_ICONS['Ruby']} Ruby", total["Ruby"])
            c6.metric(f"{PACK_ICONS['Gold']} Gold", total["Gold"])
            c7.metric(f"{PACK_ICONS['Rainbow']} Rainbow", total["Rainbow"])
            c8.metric("💸 Tổng chi (IAP)", f"${res.get('total_spent', 0.0):.2f}")
            
            st.write("")
            if res.get("chest_drop_chests"):
                chests = res["chest_drop_chests"]
                if sum(chests.values()) > 0:
                    st.subheader("📦 Tổng số Rương Chest Drop Nhận Được")
                    cc1, cc2, cc3 = st.columns(3)
                    cc1.metric("Rương 1-Sao", chests.get(1, 0))
                    cc2.metric("Rương 2-Sao", chests.get(2, 0))
                    cc3.metric("Rương 3-Sao", chests.get(3, 0))
                    st.write("")
            def add_packs_to_cart(total_packs, chests_earned):
                for pack in PACK_ORDER:
                    st.session_state[f"cart_input_{pack}"] = 0
                    st.session_state["cart_packs"][pack] = 0
                for pack, count in total_packs.items():
                    if pack in PACK_ORDER and count > 0:
                        st.session_state[f"cart_input_{pack}"] = count
                        st.session_state["cart_packs"][pack] = count
                        
                for tier in range(1, 6):
                    key = f"bulk_chest_{tier}"
                    st.session_state[key] = 0
                if chests_earned:
                    for tier, count in chests_earned.items():
                        key = f"bulk_chest_{tier}"
                        st.session_state[key] = count

                st.session_state["show_cart_success"] = True
                        
            st.button("📥 LƯU TOÀN BỘ PACKS & RƯƠNG VÀO GIỎ HÀNG", type="primary", on_click=add_packs_to_cart, args=(total, res.get("chest_drop_chests", {})))
            
            if st.session_state.get("show_cart_success"):
                st.success("✅ Đã thêm Packs vào Giỏ Hàng! Bạn có thể sang tab **Mở Gói (Gacha)** hoặc **Monte Carlo Simulator** để tiến hành mở.")
                st.session_state["show_cart_success"] = False
            
            st.divider()
            st.subheader("🔎 Chi tiết Nguồn nhận & Phần thưởng khác")
            
            import pandas as pd
            import altair as alt
            source_df = pd.DataFrame(list(res["source_breakdown"].items()), columns=["Source", "Total"])
            source_df = source_df[source_df["Total"] > 0]
            if not source_df.empty:
                chart = alt.Chart(source_df).mark_arc().encode(
                    theta=alt.Theta(field="Total", type="quantitative"),
                    color=alt.Color(field="Source", type="nominal", legend=alt.Legend(title="Nguồn", orient="right")),
                    tooltip=["Source", "Total"]
                ).properties(height=300)
                st.altair_chart(chart, use_container_width=True)
            else:
                st.info("Chưa có dữ liệu nguồn nhận")
                
            st.write("")
            
            with st.expander("⚔️ Thắng Level Hard/Super Hard (Core Gameplay)"):
                for l in res["logs"]["core"]: st.markdown(f"- {l}")
                
            if toggles["win_streak"]:
                with st.expander("🔥 Win Streak"):
                    for l in res["logs"]["win_streak"]: st.markdown(f"- {l}")
                    
            if toggles.get("chest_drop", True):
                with st.expander("🎮 Chest Drop Hàng Ngày"):
                    if "chest_drop" in res["logs"]:
                        for l in res["logs"]["chest_drop"]: st.markdown(f"- {l}")
                    
            if toggles["key_collection"]:
                with st.expander("🔑 Key Collection"):
                    for l in res["logs"]["key_collection"]: st.markdown(f"- {l}")
                    
            if toggles["master_pass"]:
                with st.expander("🎟️ Master Pass (Yarn Pass)"):
                    for l in res["logs"]["master_pass"]: st.markdown(f"- {l}")
            
            with st.expander("🛒 IAP / Mua sắm"):
                iap_str = ", ".join([f"**{p}:** {v}" for p, v in res["iap_packs"].items() if v > 0])
                if not iap_str: iap_str = "Chưa mua/nhận gói nào"
                st.write(f"**Tổng kết Pack từ IAP:** {iap_str}")
                for l in res["logs"]["iap"]: st.markdown(f"- {l}")
                
            if toggles["card_rush"]:
                with st.expander("⚡ Card Rush Bonus"):
                    if res["logs"].get("card_rush"):
                        for l in res["logs"]["card_rush"]: st.markdown(f"- {l}")
                    else:
                        st.markdown("- Chưa có thông tin Card Rush.")


```

---

## File: `card_album/ui/chest_drop.py`

```python
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

@st.dialog("BẠN VỪA NHẬN ĐƯỢC!", width="large")
def show_chest_drop_bulk_result_dialog(res: dict):
    st.markdown("""
        <style>
            div[data-testid="stDialog"] div[role="dialog"] {
                width: 85vw !important;
                max-width: 1200px !important;
            }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown(f"**🌟 MỞ THÀNH CÔNG: {res.get('total_chests', 0)} RƯƠNG**")
    
    us = res.get("upgrade_summary", {})
    summary_html = ""
    for start_tier, tier_stats in us.items():
        total_started = sum(tier_stats.values())
        if total_started > 0:
            summary_html += f"<div style='margin-bottom: 5px;'><b>📦 Rương {start_tier}-Sao (Tổng: {total_started}):</b> "
            parts = []
            for t in sorted(tier_stats.keys()):
                count = tier_stats[t]
                if count > 0:
                    if t == start_tier:
                        parts.append(f"{count} rương giữ nguyên")
                    else:
                        parts.append(f"<b><span style='color: #32CD32;'>{count} rương lên {t}-Sao</span></b>")
            summary_html += ", ".join(parts) + "</div>"
            
    if summary_html:
        st.info("🏆 **Thống Kê Thăng Cấp (Upgrade Summary):**")
        st.markdown(summary_html, unsafe_allow_html=True)
        
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
        icon = "⭐" * r if r < 6 else "🌟"
        
        box_shadow = f"box-shadow: 0 0 15px {color};" if is_new else ""
        opacity = "1.0" if is_new else "0.6"
        
        if color.startswith("#") and len(color) == 7:
            r_val, g_val, b_val = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
            bg = f"rgba({r_val}, {g_val}, {b_val}, 0.15)"
        else:
            bg = "rgba(128, 128, 128, 0.15)"
            
        badge = f"<div style='position:absolute; top:-10px; right:-10px; background:red; color:white; font-size:0.7em; padding:2px 6px; border-radius:10px; font-weight:bold; box-shadow: 0 0 5px red;'>NEW</div>" if is_new else f"<div style='position:absolute; top:-10px; right:-10px; background:gray; color:white; font-size:0.7em; padding:2px 6px; border-radius:10px; font-weight:bold;'>+{STAR_VALUES[r]}⭐</div>"
        
        return f"<div style='position:relative; width: 100px; height: 130px; border: 2px solid {color}; border-radius: 8px; padding: 5px; text-align: center; background: {bg}; {box_shadow} opacity: {opacity}; display: flex; flex-direction: column; justify-content: space-between;'>{badge}<div style='font-size: 0.8em; margin-top: 10px;'>{icon}</div><div style='font-size: 0.75em; font-weight: bold; line-height: 1.2; word-wrap: break-word; margin-bottom: 5px;'>{cname}</div></div>"
        
    new_cards = res.get("new_cards_list", [])
    dup_cards = res.get("dup_cards_list", [])
    
    if new_cards:
        st.markdown("<h3>✨ THẺ MỚI NHẬN</h3>", unsafe_allow_html=True)
        html_parts = [render_card_html(c, True) for c in new_cards]
        st.markdown("<div style='display: flex; flex-wrap: wrap; justify-content: center; gap: 15px; margin-bottom: 20px;'>" + "".join(html_parts) + "</div>", unsafe_allow_html=True)
        
    if dup_cards:
        st.markdown("<h3>♻️ THẺ TRÙNG (Đổi thành Sao)</h3>", unsafe_allow_html=True)
        html_parts = [render_card_html(c, False) for c in dup_cards]
        st.markdown("<div style='display: flex; flex-wrap: wrap; justify-content: center; gap: 15px;'>" + "".join(html_parts) + "</div>", unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("THU THẬP", use_container_width=True, type="primary"):
        st.rerun()


def render_chest_drop_tab() -> None:
    import streamlit as st
    import pandas as pd
    import time
    
    with st.container(border=True):
        st.subheader("📊 Tổng Quan Chest Drop")
        col_stats1, col_stats2, col_stats3, col_stats4, col_stats5 = st.columns(5)
        
        rarity_colors = {
            1: "gray", 2: "#32CD32", 3: "#1E90FF",
            4: "#9370DB", 5: "#FFA500", 6: "#FF1493"
        }
        
        def st_color_tier(r):
            colors = {1: "gray", 2: "green", 3: "blue", 4: "violet", 5: "orange", 6: "red"}
            c = colors.get(int(r), "gray")
            label = f"{r}-Sao" if int(r) < 6 else "VÀNG"
            return f":{c}[{label}]"

        
        new_total = st.session_state.get('cd_new_cards_drawn', 0)
        new_dict = st.session_state.get('cd_new_cards_by_rarity', {})
        new_parts = []
        for r in range(1, 7):
            if new_dict.get(r, 0) > 0:
                icon = "⭐" if r < 6 else "🌟"
                new_parts.append(f"<span style='color:{rarity_colors[r]}'>{r}{icon}: {new_dict[r]}</span>")
        new_detail = f"<div style='font-size:0.85em; margin-top:-10px; color:#aaa'>({', '.join(new_parts)})</div>" if new_parts else ""

        dup_total = st.session_state.get('cd_dup_cards_drawn', 0)
        dup_dict = st.session_state.get('cd_dup_cards_by_rarity', {})
        dup_parts = []
        for r in range(1, 7):
            if dup_dict.get(r, 0) > 0:
                icon = "⭐" if r < 6 else "🌟"
                dup_parts.append(f"<span style='color:{rarity_colors[r]}'>{r}{icon}: {dup_dict[r]}</span>")
        dup_detail = f"<div style='font-size:0.85em; margin-top:-10px; color:#aaa'>({', '.join(dup_parts)})</div>" if dup_parts else ""
        
        with col_stats1:
            total_cd_cards = st.session_state.get('cd_total_cards_drawn', 0)
            st.metric("🃏 Tổng Thẻ Rút Ra", f"{total_cd_cards}")
        with col_stats2:
            st.metric("🎴 Thẻ Mới Nhận", f"{new_total}")
            if new_detail: st.markdown(new_detail, unsafe_allow_html=True)
        with col_stats3:
            cd_stars = st.session_state.get('cd_stars_gained', 0)
            st.metric("♻️ Thẻ Trùng (Sao Nhận)", f"{dup_total} (+{cd_stars}⭐)")
            if dup_detail: st.markdown(dup_detail, unsafe_allow_html=True)
        with col_stats4:
            total_chests = sum(st.session_state.get('chest_drop_counts', {1:0,2:0,3:0,4:0,5:0}).values())
            st.metric("📦 Tổng Rương Đã Mở", f"{total_chests}")
        with col_stats5:
            rate = (dup_total / total_cd_cards * 100) if total_cd_cards > 0 else 0
            st.metric("♻️ Tỉ lệ Thẻ Trùng", f"{dup_total}/{total_cd_cards} ({rate:.2f}%)")
        
        st.markdown("<hr style='margin: 10px 0px; opacity: 0.3'>", unsafe_allow_html=True)
        st.caption("Chi tiết số lượng Chest đã mở từ giỏ:")
        pack_cols = st.columns(5)
        cd_counts = st.session_state.get("chest_drop_counts", {1:0,2:0,3:0,4:0,5:0})
        for i in range(1, 6):
            with pack_cols[i - 1]:
                st.markdown(f"**Rương {st_color_tier(i)}**: {cd_counts.get(i, 0)}")
                
        st.markdown("<hr style='margin: 10px 0px; opacity: 0.3'>", unsafe_allow_html=True)
        from .gacha import render_ss2_pity_panel
        render_ss2_pity_panel()
    
    upgrade_cfg = st.session_state.get('config_chest_drop_tiers', {})
    
    def get_reward_str(tier_str):
        if tier_str not in upgrade_cfg: return "Unknown"
        w = upgrade_cfg[tier_str]["weights"]
        total = sum(w.values())
        if total == 0: return "Không có phần thưởng"
        parts = []
        for r_str, weight in w.items():
            if weight > 0:
                parts.append(f"{weight/total*100:.0f}% Thẻ {r_str}-Sao" if r_str != "6" else f"{weight/total*100:.0f}% VÀNG")
        return ", ".join(parts)
        
    def get_upgrade_str(tier_str, start_tier_str="1"):
        matrix = st.session_state.get('config_chest_upgrade_matrix', {})
        if start_tier_str not in matrix or tier_str not in matrix[start_tier_str]: return "0%"
        val = matrix[start_tier_str][tier_str]
        if int(tier_str) < int(start_tier_str): return "Không khả dụng"
        if val == 0: return "Không thăng cấp"
        return f"{val*100:.0f}%"

    from ..gacha import calculate_chest_drop_new_chance, add_log
    def get_new_chance_str(tier_str):
        if tier_str not in upgrade_cfg: return "0%"
        t_cfg = upgrade_cfg[tier_str]
        w = t_cfg["weights"]
        y_val = float(t_cfg["y_value"])
        total = sum(w.values())
        if total == 0: return "0%"
        parts = []
        for r_str, weight in w.items():
            if weight > 0:
                rarity = int(r_str)
                new_chance = calculate_chest_drop_new_chance(st.session_state, rarity, y_val)
                label = f"{r_str}-Sao" if r_str != "6" else "VÀNG"
                if len([v for v in w.values() if v > 0]) > 1:
                    parts.append(f"{new_chance*100:.1f}% ({label})")
                else:
                    parts.append(f"{new_chance*100:.1f}%")
        return ", ".join(parts)

    current_sandbox_tier = st.session_state.get("sandbox_chest_tier", 1)
    
    df_upgrade = pd.DataFrame([
        {"Rương": "1-Sao", "Phần thưởng (Mỗi hit)": get_reward_str("1"), "Thẻ MỚI": get_new_chance_str("1"), "Tỉ lệ thăng cấp": get_upgrade_str("1", str(current_sandbox_tier))},
        {"Rương": "2-Sao", "Phần thưởng (Mỗi hit)": get_reward_str("2"), "Thẻ MỚI": get_new_chance_str("2"), "Tỉ lệ thăng cấp": get_upgrade_str("2", str(current_sandbox_tier))},
        {"Rương": "3-Sao", "Phần thưởng (Mỗi hit)": get_reward_str("3"), "Thẻ MỚI": get_new_chance_str("3"), "Tỉ lệ thăng cấp": get_upgrade_str("3", str(current_sandbox_tier))},
        {"Rương": "4-Sao", "Phần thưởng (Mỗi hit)": get_reward_str("4"), "Thẻ MỚI": get_new_chance_str("4"), "Tỉ lệ thăng cấp": get_upgrade_str("4", str(current_sandbox_tier))},
        {"Rương": "5-Sao", "Phần thưởng (Mỗi hit)": get_reward_str("5"), "Thẻ MỚI": get_new_chance_str("5"), "Tỉ lệ thăng cấp": "Không thăng cấp"},
    ])

    cart = st.session_state.get("cart_chests", {1:0, 2:0, 3:0})
    # --- SANDBOX SIMULATOR ---
    st.subheader("🎮 Sandbox Chest Drop")
    st.markdown("Giả lập đập rương hoàn toàn miễn phí, không tốn rương trong giỏ hàng. Bạn có thể tự do test nhân phẩm!")
    
    col_ctrl, col_reward = st.columns([1, 2])
    
    active_session = st.session_state.get("cd_active_session")
    
    with col_ctrl:
        with st.container(border=True):
            tier = st.selectbox(
                "Chọn rương:",
                [1, 2, 3],
                format_func=lambda x: f"Rương {x}-Sao",
                key="sandbox_chest_tier"
            )
            
            # Auto init or reset if tier changed
            if active_session is None or active_session.get("start_tier") != tier:
                active_session = {
                    "start_tier": tier,
                    "current_tier": tier,
                    "hits_done": 0,
                    "rewards": [],
                    "max_tier": tier,
                    "upgraded_last_hit": False,
                    "drawn_in_batch": set()
                }
                st.session_state["cd_active_session"] = active_session
                
            hits_done = active_session["hits_done"]
            current_tier = active_session["current_tier"]
            upgraded = active_session.get("upgraded_last_hit", False)
            
            st.markdown(f"**Đang mở: Rương {st_color_tier(active_session['start_tier'])}**")
            
            st.progress(hits_done / 5.0)
            st.caption(f"Tiến độ: **Hit {hits_done}/5**")
            
            if hits_done > 0:
                st.write("")
            
            if hits_done < 5:
                if st.button(f"🔨 Đập! (Hit {hits_done+1})", key="sandbox_hit", type="primary", use_container_width=True):
                    from ..gacha import process_chest_drop_hit
                    res = process_chest_drop_hit(st.session_state, active_session["start_tier"], current_tier, active_session["drawn_in_batch"])
                    
                    active_session["rewards"].append({
                        "status": res["status"],
                        "card": res["card"],
                        "upgraded": res["upgraded"],
                        "next_tier": res["next_tier"]
                    })
                    active_session["upgraded_last_hit"] = res["upgraded"]
                    active_session["current_tier"] = res["next_tier"]
                    if res["next_tier"] > active_session["max_tier"]:
                        active_session["max_tier"] = res["next_tier"]
                    active_session["hits_done"] += 1
                    
                    if active_session["hits_done"] == 5:
                        def add_cd_log(session_state, msg):
                            if "cd_log" not in session_state: session_state["cd_log"] = []
                            session_state["cd_log"].insert(0, msg)
                            if len(session_state["cd_log"]) > 300: session_state["cd_log"] = session_state["cd_log"][:300]
                        
                        hit_logs = []
                        from ..gacha import format_card_name
                        for item in active_session["rewards"]:
                            if not item.get("card"): continue
                            card_r = item["card"][1]
                            cname = format_card_name(item["card"])
                            status_str = f"({item['status']})"
                            card_str = f"{card_r}-Sao [{cname}] {status_str}"
                            if item["upgraded"]:
                                hit_logs.append(f"{card_str} ✨Lên {item['next_tier']}-Sao")
                            else:
                                hit_logs.append(card_str)
                            
                        has_new = any(item["status"] == "NEW" for item in active_session["rewards"])
                        prefix = "✅" if has_new else "❌"
                        log_msg = f"{prefix} 📦 Mở Rương {active_session['start_tier']}-Sao | Mở ra: " + ", ".join(hit_logs)
                        add_cd_log(st.session_state, log_msg)
                    
                    st.rerun()
            else:
                if st.button("THU THẬP", key="sandbox_reset", type="primary", use_container_width=True):
                    st.session_state["cd_active_session"] = {
                        "start_tier": tier,
                        "current_tier": tier,
                        "hits_done": 0,
                        "rewards": [],
                        "max_tier": tier,
                        "upgraded_last_hit": False,
                        "drawn_in_batch": set()
                    }
                    st.rerun()
                        
    with col_reward:
        with st.container(border=True):
            st.markdown("**Phần Thưởng Nhận Được:**")
            if active_session is None or len(active_session["rewards"]) == 0:
                st.caption("Chưa đập hit nào... Hãy bắt đầu đập để xem kết quả!")
            else:
                rarity_colors = {
                    1: "#B0C4DE", 2: "#32CD32", 3: "#1E90FF",
                    4: "#9370DB", 5: "#FFA500", 6: "#FFD700"
                }
                from ..gacha import STAR_VALUES
                from ..config import CARD_SETS
                
                html_parts = []
                for item in active_session["rewards"]:
                    is_new = (item["status"] == "NEW")
                    card = item["card"]
                    if not card: continue
                    set_id, r, idx = card
                    cname = f"{CARD_SETS[set_id]['name']} #{idx+1}"
                    color = rarity_colors.get(r, "gray")
                    icon = "⭐" * r if r < 6 else "🌟"
                    
                    box_shadow = f"box-shadow: 0 0 15px {color};" if is_new else ""
                    opacity = "1.0" if is_new else "0.6"
                    
                    if color.startswith("#") and len(color) == 7:
                        r_val, g_val, b_val = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
                        bg = f"rgba({r_val}, {g_val}, {b_val}, 0.15)"
                    else:
                        bg = "rgba(128, 128, 128, 0.15)"
                        
                    badge = f"<div style='position:absolute; top:-10px; right:-10px; background:red; color:white; font-size:0.7em; padding:2px 6px; border-radius:10px; font-weight:bold; box-shadow: 0 0 5px red;'>NEW</div>" if is_new else f"<div style='position:absolute; top:-10px; right:-10px; background:gray; color:white; font-size:0.7em; padding:2px 6px; border-radius:10px; font-weight:bold;'>+{STAR_VALUES[r]}⭐</div>"
                    html_parts.append(f"<div style='position:relative; width: 100px; height: 130px; border: 2px solid {color}; border-radius: 8px; padding: 5px; text-align: center; background: {bg}; {box_shadow} opacity: {opacity}; display: flex; flex-direction: column; justify-content: space-between; margin-right: 10px; margin-bottom: 15px;'>{badge}<div style='font-size: 0.8em; margin-top: 10px;'>{icon}</div><div style='font-size: 0.75em; font-weight: bold; line-height: 1.2; word-wrap: break-word; margin-bottom: 5px;'>{cname}</div></div>")
                    
                    if item.get("upgraded"):
                        n_tier = item.get("next_tier")
                        html_parts.append(f"<div style='position:relative; width: 100px; height: 130px; border: 2px dashed #32CD32; border-radius: 8px; padding: 5px; text-align: center; background: rgba(50,205,50,0.1); display: flex; flex-direction: column; justify-content: center; margin-right: 10px; margin-bottom: 15px;'><div style='font-size: 1.5em; margin-bottom:5px;'>✨</div><div style='font-size: 0.85em; font-weight: bold; color: #32CD32;'>LÊN<br>{n_tier}-SAO!</div></div>")
                    
                st.markdown("<div style='display: flex; flex-wrap: wrap;'>" + "".join(html_parts) + "</div>", unsafe_allow_html=True)


    st.divider()
    col_left, col_right = st.columns([1, 2])
    
    with col_left:
        st.subheader('🛒 Giỏ Hàng')
        st.caption("Nhập số lượng rương bạn muốn mở.")
        
        qty_1 = st.number_input("Rương 1-Sao", min_value=0, max_value=9999, step=1, key="bulk_chest_1")
        qty_2 = st.number_input("Rương 2-Sao", min_value=0, max_value=9999, step=1, key="bulk_chest_2")
        qty_3 = st.number_input("Rương 3-Sao", min_value=0, max_value=9999, step=1, key="bulk_chest_3")
            
        total_bulk = qty_1 + qty_2 + qty_3
        
        st.write("")
        def reset_cart_cd():
            st.session_state["bulk_chest_1"] = 0
            st.session_state["bulk_chest_2"] = 0
            st.session_state["bulk_chest_3"] = 0
            
        col_exec, col_reset = st.columns([3, 1])
        
        if col_exec.button('💥 MỞ TOÀN BỘ GIỎ HÀNG', type='primary', use_container_width=True):
            if total_bulk == 0:
                st.error("Giỏ hàng đang trống!")
            else:
                from ..gacha import process_chest_drop_hit
                all_new = []
                all_dup = []
                
                def add_cd_log(session_state, msg):
                    if "cd_log" not in session_state: session_state["cd_log"] = []
                    session_state["cd_log"].insert(0, msg)
                    if len(session_state["cd_log"]) > 300: session_state["cd_log"] = session_state["cd_log"][:300]
                    
                add_cd_log(st.session_state, f"========== BẮT ĐẦU MỞ HÀNG LOẠT ({total_bulk} RƯƠNG) ==========")
                
                upgrade_summary = {
                    1: {1:0, 2:0, 3:0, 4:0, 5:0},
                    2: {2:0, 3:0, 4:0, 5:0},
                    3: {3:0, 4:0, 5:0}
                }
            
                cart_to_open = {1: qty_1, 2: qty_2, 3: qty_3}
                
                from ..gacha import format_card_name
                for start_tier, count in cart_to_open.items():
                    for i in range(count):
                        current_t = start_tier
                        hit_logs = []
                        chest_has_new = False
                        drawn_in_batch = set()
                        for _ in range(5):
                            res = process_chest_drop_hit(st.session_state, start_tier, current_t, drawn_in_batch)
                            if res["status"] == "NEW": 
                                all_new.append(res["card"])
                                chest_has_new = True
                            else: 
                                all_dup.append(res["card"])
                            
                            card_r = res["card"][1] if res["card"] else 0
                            cname = format_card_name(res["card"]) if res["card"] else ""
                            status_str = f"({res['status']})"
                            card_str = f"{st_color_tier(card_r)} [{cname}] {status_str}"
                            if res["upgraded"]:
                                hit_logs.append(f"{card_str} ✨Lên {st_color_tier(res['next_tier'])}")
                            else:
                                hit_logs.append(card_str)
                                
                            current_t = res["next_tier"]
                        upgrade_summary[start_tier][current_t] += 1
                        
                        prefix = "✅" if chest_has_new else "❌"
                        log_msg = f"{prefix} 📦 Mở Rương {st_color_tier(start_tier)} #{i+1} | Mở ra: " + ", ".join(hit_logs)
                        add_cd_log(st.session_state, log_msg)
                
                summary_html = ""
                for start_tier, tier_stats in upgrade_summary.items():
                    total_started = sum(tier_stats.values())
                    if total_started > 0:
                        parts = []
                        for t in sorted(tier_stats.keys()):
                            count = tier_stats[t]
                            if count > 0:
                                if t == start_tier:
                                    parts.append(f"{count} rương giữ nguyên")
                                else:
                                    parts.append(f"{count} rương thăng cấp {st_color_tier(t)}")
                        summary_html += f"[{st_color_tier(start_tier)}: " + ", ".join(parts) + "] "
                
                add_cd_log(st.session_state, f"🌟 HOÀN THÀNH MỞ HÀNG LOẠT: Thêm {len(all_new)} thẻ mới, {len(all_dup)} thẻ trùng. {summary_html}")
                        
                st.session_state.cd_show_bulk_result = True
                st.session_state.cd_new_cards = all_new
                st.session_state.cd_dup_cards = all_dup
                st.session_state.cd_upgrade_summary = upgrade_summary
                st.session_state.cd_total_bulk_opened = total_bulk
                st.rerun()
            
        col_reset.button("🗑️ Xoá giỏ", use_container_width=True, on_click=reset_cart_cd)
                
        if st.session_state.get('cd_show_bulk_result', False):
            st.session_state.cd_show_bulk_result = False
            res_dict = {
                "new_cards_list": st.session_state.get("cd_new_cards", []),
                "dup_cards_list": st.session_state.get("cd_dup_cards", []),
                "upgrade_summary": st.session_state.get("cd_upgrade_summary", {}),
                "total_chests": st.session_state.get("cd_total_bulk_opened", 0)
            }
            show_chest_drop_bulk_result_dialog(res_dict)
            
    with col_right:
        st_colors = {1: "gray", 2: "green", 3: "blue", 4: "violet", 5: "orange", 6: "red"}
        color_name = st_colors.get(int(current_sandbox_tier), "gray")
        st.subheader(f"🔎 Bảng Tỉ Lệ Động: :{color_name}[Rương {current_sandbox_tier}-Sao]")
        st.markdown("**Tỉ lệ thăng cấp và phần thưởng rương sau mỗi hit:**")
        st.dataframe(df_upgrade, hide_index=True)

    st.divider()
    render_cd_log_panel()


def render_cd_log_panel() -> None:
    st.subheader("📝 Kết Quả Mở Chest")
    cd_log = st.session_state.get("cd_log", [])
    if not cd_log:
        st.caption("Chưa có dữ liệu lịch sử mở chest.")
        return
        
    latest = cd_log[0]
    if "MỚI" in latest or "✨" in latest or "🌟" in latest:
        st.success(f"**[MỚI NHẤT]** {latest}")
    else:
        st.warning(f"**[MỚI NHẤT]** {latest}")

    with st.expander("📜 Xem toàn bộ lịch sử", expanded=True):
        log_container = st.container(height=400)
        for entry in cd_log[1:]:
            if "MỚI" in entry or "✨" in entry or "🌟" in entry:
                log_container.success(entry)
            elif "====" in entry:
                log_container.markdown(f"**{entry}**")
            else:
                log_container.warning(entry)


```

---

## File: `card_album/ui/gacha.py`

```python
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
    st.subheader("🍀 Chỉ số Pity")
    _, pity_message = get_pity_bonus(st.session_state, selected_pack)
    st.markdown(f"**Gói đang chọn ({selected_pack}):** `{pity_message}`")
    # Lọc ra các gói đang bị tạch (misses > 0) và có cấu hình pity
    pity_data = {p: misses for p, misses in st.session_state["pack_pity"].items() if misses > 0}
    if pity_data:
        st.caption("Các gói đang tích lũy Pity (Số lần mở xịt liên tiếp):")
        cols = st.columns(4)
        for i, (pack, misses) in enumerate(pity_data.items()):
            cols[i % 4].metric(pack, f"{misses} tạch")
    else:
        st.caption("Hiện chưa có gói nào đang tích Pity!")

    pity_rules = []
    for pack_name, pack_config in st.session_state["config_packs"].items():
        if pack_config["pity_threshold"] > 0 and pack_config["pity_increment"] > 0:
            if "+" not in pack_name:
                incr_percent = int(pack_config["pity_increment"] * 100)
                pity_rules.append(f"{pack_name} ({pack_config['pity_threshold']} lần +{incr_percent}%)")
                
    if pity_rules:
        st.caption(f"*Cơ chế (Tạch liên tiếp): {', '.join(pity_rules)}*")

def render_ss2_pity_panel() -> None:
    if st.session_state.get("ss2_optimize_collection", True):
        from ..gacha import get_ss2_pity_info
        info = get_ss2_pity_info(st.session_state)
        
        st.subheader("🤖 Tối ưu Bộ Sưu Tập (SS2)")
        
        c1, c2, c3 = st.columns([1, 1.2, 1.5])
        with c1:
            st.metric("📦 Set Đã Xong", f"{info['completed_sets']}/{info['total_sets']}")
            st.caption(f"Độ mót (Pity Set): **{info['pity_set']*100:.1f}%**")
        with c2:
            st.metric("🎯 Set Gần Xong Nhất", info['best_set_name'] if info['best_set_id'] else "Chưa có")
            st.caption(f"Tiến độ: **{info['best_set_owned']}/{info['best_set_total']} thẻ**" if info['best_set_id'] else "")
            
        with c3:
            if info['missing_details']:
                st.markdown(f"**🔍 Chi tiết Tỉ Lệ Động ({info['best_set_name']}):**")
                for detail in info['missing_details']:
                    rarity = detail['rarity']
                    icon = "⭐" if rarity < 6 else "🌟"
                    r_label = f"{rarity}{icon}" if rarity < 6 else "VÀNG"
                    st.caption(
                        f"- Thiếu **{detail['missing_count']} thẻ {r_label}** ➔ "
                        f"Tỉ lệ ép bài: **{detail['final_chance']*100:.1f}%** "
                        f"*(Pity Rarity: {detail['pity_rarity']*100:.1f}%)*"
                    )


@st.dialog("BẠN VỪA NHẬN ĐƯỢC!", width="large")
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
    
    st.markdown(f"**🌟 MỞ THÀNH CÔNG: {res.get('summary', '')}**")
    if "bulk_summary" in res:
        bs = res["bulk_summary"]
        st.info(f"🏆 Tổng kết Mở Bulk Rương: Rương đã thăng cấp tối đa lên: 2-Sao ({bs.get(2,0)} lần), 3-Sao ({bs.get(3,0)} lần), 4-Sao ({bs.get(4,0)} lần), 5-Sao ({bs.get(5,0)} lần)")
    else:
        st.info(f"📦 Tổng thẻ rút được: +{res.get('total_cards', 0)} | ⭐ Sao Nhận Về: +{res.get('stars_diff', 0)}")
    
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
        icon = "⭐" * r if r < 6 else "🌟"
        
        box_shadow = f"box-shadow: 0 0 15px {color};" if is_new else ""
        opacity = "1.0" if is_new else "0.6"
        
        if color.startswith("#") and len(color) == 7:
            r_val, g_val, b_val = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
            bg = f"rgba({r_val}, {g_val}, {b_val}, 0.15)"
        else:
            bg = "rgba(128, 128, 128, 0.15)"
            
        badge = f"<div style='position:absolute; top:-10px; right:-10px; background:red; color:white; font-size:0.7em; padding:2px 6px; border-radius:10px; font-weight:bold; box-shadow: 0 0 5px red;'>NEW</div>" if is_new else f"<div style='position:absolute; top:-10px; right:-10px; background:gray; color:white; font-size:0.7em; padding:2px 6px; border-radius:10px; font-weight:bold;'>+{STAR_VALUES[r]}⭐</div>"
        
        return f"<div style='position:relative; width: 100px; height: 130px; border: 2px solid {color}; border-radius: 8px; padding: 5px; text-align: center; background: {bg}; {box_shadow} opacity: {opacity}; display: flex; flex-direction: column; justify-content: space-between;'>{badge}<div style='font-size: 0.8em; margin-top: 10px;'>{icon}</div><div style='font-size: 0.75em; font-weight: bold; line-height: 1.2; word-wrap: break-word; margin-bottom: 5px;'>{cname}</div></div>"
        
    new_cards = res.get("new_cards_list", [])
    dup_cards = res.get("dup_cards_list", [])
    
    if new_cards:
        st.markdown("<h3>✨ THẺ MỚI NHẬN</h3>", unsafe_allow_html=True)
        html_parts = [render_card_html(c, True) for c in new_cards]
        st.markdown("<div style='display: flex; flex-wrap: wrap; justify-content: center; gap: 15px; margin-bottom: 20px;'>" + "".join(html_parts) + "</div>", unsafe_allow_html=True)
        
    if dup_cards:
        st.markdown("<h3>♻️ THẺ TRÙNG (Đổi thành Sao)</h3>", unsafe_allow_html=True)
        html_parts = [render_card_html(c, False) for c in dup_cards]
        st.markdown("<div style='display: flex; flex-wrap: wrap; justify-content: center; gap: 15px;'>" + "".join(html_parts) + "</div>", unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("THU THẬP", use_container_width=True, type="primary"):
        st.rerun()


def render_pack_opener_tab() -> None:
    with st.container(border=True):
        st.subheader("📊 Tổng Quan Mở Pack")
        col_stats1, col_stats2, col_stats3, col_stats4, col_stats5 = st.columns(5)
        
        rarity_colors = {
            1: "gray", 2: "#32CD32", 3: "#1E90FF",
            4: "#9370DB", 5: "#FFA500", 6: "#FF1493"
        }
        
        def st_color_tier(r):
            colors = {1: "gray", 2: "green", 3: "blue", 4: "violet", 5: "orange", 6: "red"}
            c = colors.get(int(r), "gray")
            label = f"{r}-Sao" if int(r) < 6 else "VÀNG"
            return f":{c}[{label}]"

        
        new_total = st.session_state.get('new_cards_drawn', 0)
        new_dict = st.session_state.get('new_cards_by_rarity', {})
        new_parts = []
        for r in range(1, 7):
            if new_dict.get(r, 0) > 0:
                icon = "⭐" if r < 6 else "🌟"
                new_parts.append(f"<span style='color:{rarity_colors[r]}'>{r}{icon}: {new_dict[r]}</span>")
        new_detail = f"<div style='font-size:0.85em; margin-top:-10px; color:#aaa'>({', '.join(new_parts)})</div>" if new_parts else ""

        dup_total = st.session_state.get('dup_cards_drawn', 0)
        dup_dict = st.session_state.get('dup_cards_by_rarity', {})
        dup_parts = []
        for r in range(1, 7):
            if dup_dict.get(r, 0) > 0:
                icon = "⭐" if r < 6 else "🌟"
                dup_parts.append(f"<span style='color:{rarity_colors[r]}'>{r}{icon}: {dup_dict[r]}</span>")
        dup_detail = f"<div style='font-size:0.85em; margin-top:-10px; color:#aaa'>({', '.join(dup_parts)})</div>" if dup_parts else ""
        
        with col_stats1:
            total_drawn = st.session_state['total_cards_drawn']
            st.metric("🃏 Tổng Thẻ Rút Ra", f"{total_drawn}")
        with col_stats2:
            st.metric("🎴 Thẻ Mới Nhận", f"{new_total}")
            if new_detail: st.markdown(new_detail, unsafe_allow_html=True)
        with col_stats3:
            pack_stars = st.session_state.get('pack_stars_gained', 0)
            st.metric("♻️ Thẻ Trùng (Sao Nhận)", f"{dup_total} (+{pack_stars}⭐)")
            if dup_detail: st.markdown(dup_detail, unsafe_allow_html=True)
        with col_stats4:
            st.metric("📦 Tổng Pack Đã Mở", f"{st.session_state['total_packs']}")
        with col_stats5:
            rate = (dup_total / total_drawn * 100) if total_drawn > 0 else 0
            st.metric("♻️ Tỉ lệ Thẻ Trùng", f"{dup_total}/{total_drawn} ({rate:.2f}%)")
        
        st.markdown("<hr style='margin: 10px 0px; opacity: 0.3'>", unsafe_allow_html=True)
        st.caption("Chi tiết số lượng từng gói đã mở:")
        pack_cols = st.columns(5)
        for i, pack in enumerate(PACK_ORDER):
            with pack_cols[i % 5]:
                st.markdown(f"**{PACK_ICONS[pack]} {pack}**: {st.session_state['pack_counts'][pack]}")
                
        st.markdown("<hr style='margin: 10px 0px; opacity: 0.3'>", unsafe_allow_html=True)
        render_ss2_pity_panel()
            
    st.markdown("<hr style='margin: 15px 0px; opacity: 0.3'>", unsafe_allow_html=True)
    
    col_left, col_right = st.columns([1, 1.2])
    with col_left:
        st.subheader("🛒 Giỏ Hàng")
        st.caption("Nhập số lượng gói bạn muốn mở.")
        shop_cols = st.columns(2)
        for i, pack in enumerate(PACK_ORDER):
            with shop_cols[i % 2]:
                if f"cart_input_{pack}" not in st.session_state:
                    st.session_state[f"cart_input_{pack}"] = st.session_state["cart_packs"].get(pack, 0)
                st.number_input(f"{PACK_ICONS[pack]} {pack}", min_value=0, max_value=10000, step=1, key=f"cart_input_{pack}")
                st.session_state["cart_packs"][pack] = st.session_state[f"cart_input_{pack}"]

        st.markdown("<br>", unsafe_allow_html=True)
        auto_chest = st.checkbox("🔄 Tự động dùng sao dư để đổi Star Chest", key="auto_chest_chk", help="Hệ thống sẽ tự động mua rương xịn nhất có thể (Vàng -> Bạc -> Đồng) cho đến khi không đủ sao (dưới 100 sao).")
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
        col_exec.button("🚀 MỞ CÁC GÓI ĐÃ CHỌN", type="primary", use_container_width=True, on_click=execute_cart)
        col_reset.button("🗑️ Xóa Giỏ Hàng", use_container_width=True, on_click=reset_cart)
        if "cart_error" in st.session_state:
            st.error(st.session_state.pop("cart_error"))
        if "cart_success" in st.session_state:
            show_draw_result_dialog(st.session_state.pop("cart_success"))

        st.markdown("<hr style='margin: 15px 0px; opacity: 0.3'>", unsafe_allow_html=True)
        st.subheader(f"🌟 Đổi Rương Sao (Hiện có {st.session_state['stars']} ⭐)")
        st.caption("Dùng Sao để đổi lấy rương thưởng đặc biệt.")
        
        def execute_chest(chest_type):
            res = open_chest(st.session_state, chest_type)
            if res["success"]:
                st.session_state["chest_success"] = res
            else:
                st.session_state["chest_error"] = res["message"]

        chest_col1, chest_col2, chest_col3 = st.columns(3)
        chest_col1.button("🥉 Bronze Chest (100⭐)", use_container_width=True, on_click=execute_chest, args=("Bronze",))
        chest_col2.button("🥈 Silver Chest (250⭐)", use_container_width=True, on_click=execute_chest, args=("Silver",))
        chest_col3.button("🥇 Gold Chest (500⭐)", use_container_width=True, on_click=execute_chest, args=("Gold",))
        
        if "chest_error" in st.session_state:
            st.error(st.session_state.pop("chest_error"))
        if "chest_success" in st.session_state:
            show_draw_result_dialog(st.session_state.pop("chest_success"))

    with col_right:
        selected_pack = st.selectbox("🔍 Chọn Pack:", PACK_ORDER)
        
        def execute_multi_pack(pack, count):
            res = open_bulk_packs(st.session_state, {pack: count}, False)
            if res["success"]:
                st.session_state["single_success"] = res
                st.session_state["single_success_count"] = count
                st.session_state["single_success_pack"] = pack
            else:
                st.session_state["single_error"] = res["message"]
                
        col_btn1, col_btn10 = st.columns(2)
        col_btn1.button(f"🎟️ Mở 1 gói", type="primary", use_container_width=True, on_click=execute_multi_pack, args=(selected_pack, 1))
        col_btn10.button(f"🎟️ Mở 10 gói", type="primary", use_container_width=True, on_click=execute_multi_pack, args=(selected_pack, 10))
        
        if "single_error" in st.session_state:
            st.error(st.session_state.pop("single_error"))
        if "single_success" in st.session_state:
            res = st.session_state.pop("single_success")
            count = st.session_state.pop("single_success_count")
            pack = st.session_state.pop("single_success_pack")
            res["summary"] = f"{count} gói {pack}"
            show_draw_result_dialog(res)
            
        st.markdown("<hr style='margin: 10px 0px; opacity: 0.3'>", unsafe_allow_html=True)
        render_rate_panel(selected_pack)

    st.divider()
    render_log_panel()


def render_log_panel() -> None:
    st.subheader("📝 Kết Quả Mở Pack")
    if st.session_state["log"]:
        latest = st.session_state["log"][0]
        if is_positive_log(latest):
            st.success(f"**[MỚI NHẤT]** {latest}")
        else:
            st.warning(f"**[MỚI NHẤT]** {latest}")

    with st.expander("📜 Xem toàn bộ lịch sử", expanded=True):
        log_container = st.container(height=400)
        for entry in st.session_state["log"][1:]:
            if is_positive_log(entry):
                log_container.success(entry)
            elif "====" in entry:
                log_container.markdown(f"**{entry}**")
            else:
                log_container.warning(entry)

        if not st.session_state["log"]:
            log_container.info("Chưa mở gói nào. Hãy sử dụng chức năng ở cột trái!")


def render_rate_panel(selected_pack: str) -> None:
    st.subheader(f"🔍 Tỉ Lệ Động: Gói {selected_pack}")

    if selected_pack == "Rainbow":
        st.info(
            "**Cơ chế Rainbow:**\n"
            "- Gói có tổng cộng 6 thẻ (5 thẻ đầu random theo tỉ lệ cao).\n"
            "- Thẻ thứ 6 (bảo hiểm) 100% ra thẻ MỚI.\n"
            "- Ưu tiên lấp đầy Thẻ Vàng trước.\n"
            "- Nếu đã có đủ 18 Thẻ Vàng, lấp ngẫu nhiên các thẻ còn thiếu."
        )
        return

    effective_size = PACKS[selected_pack].size
    rows = build_rate_rows(st.session_state, selected_pack)
    st.dataframe(
        pd.DataFrame(rows), 
        use_container_width=True, 
        hide_index=True,
        column_config={
            "Thẻ MỚI": st.column_config.Column(
                "Thẻ MỚI",
                help="Tỉ lệ bốc được thẻ mà bạn CHƯA CÓ trong Album. Được cộng dồn với Buff Pity. Sẽ về 0% nếu đã sưu tập đủ độ hiếm đó."
            ),
            "Thẻ TRÙNG": st.column_config.Column(
                "Thẻ TRÙNG",
                help="Công thức: 100% - Tỉ lệ Thẻ MỚI.\nThẻ trùng sẽ tự động được phân rã thành số Sao tương ứng với độ hiếm."
            )
        }
    )
        
    guaranteed_tier = PACKS[selected_pack].guaranteed_tier
    guaranteed_label = f"{guaranteed_tier}-Sao" if guaranteed_tier < 6 else "Thẻ VÀNG"
    caption = f"Gói này gồm **{effective_size} thẻ**. Chắc chắn có ít nhất 1 **{guaranteed_label}**."
    st.caption(caption)
    
    st.divider()
    render_pity_panel(selected_pack)


def is_positive_log(entry: str) -> bool:
    return "✅" in entry or "🌈" in entry or "🌟" in entry


```

---

## File: `card_album/ui/inventory.py`

```python
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

def render_grand_album_section() -> None:
    col_toggles = st.columns(2)
    with col_toggles[0]:
        st.toggle(
            "🏆 Grand Album",
            key="grand_album_enabled",
            help="Khi bật, cho phép Album tự động reset khi cày đủ 135 thẻ (áp dụng cho cả Mở Pack và Mô Phỏng).",
        )
    with col_toggles[1]:
        st.toggle(
            "🚀 SS2 Optimize Collection",
            key="ss2_optimize_collection",
            value=True,
            help="Tối ưu Card Collection Season 2: First Pack Luck & Set Completion Pity.",
        )
    if st.session_state.get("grand_album_enabled", True):
        st.caption("Grand Album: Khi đạt mốc 135 thẻ, kho thẻ tự reset về 0 (giữ nguyên Sao). Các thẻ tiếp theo rút được sẽ tính cho vòng Album mới.")


def render_inventory_tab() -> None:
    col_ga, col_reset = st.columns([4, 1])
    with col_ga:
        render_grand_album_section()
    with col_reset:
        if st.button("🗑️ Reset Dữ Liệu", use_container_width=True, type="primary"):
            reset_progress(st.session_state)
            st.rerun()
    st.divider()
    
    total_cards = total_cards_collected(st.session_state)
    completions = st.session_state.get("grand_album_completions", 0)
    is_finished = st.session_state.get("grand_album_finished", False)
    
    st.subheader("Tiến độ Album")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🎴 Thẻ thu thập được", f"{total_cards} / {TOTAL_CARDS}")
        if completions > 0 or is_finished:
            st.markdown("<div style='margin-top:-15px; color:#FFD700; font-weight:bold;'>🏆 Grand Album</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='margin-top:-15px; color:#888; font-weight:bold;'>Thường</div>", unsafe_allow_html=True)
            
    col2.metric("⭐ Tổng Sao Hiện Có", f"{st.session_state['stars']}")
    total_new = st.session_state.get('new_cards_drawn', 0) + st.session_state.get('cd_new_cards_drawn', 0)
    total_dup = st.session_state.get('dup_cards_drawn', 0) + st.session_state.get('cd_dup_cards_drawn', 0)
    col3.metric("📈 Thẻ Mới / Thẻ Trùng", f"{total_new} / {total_dup}")
    
    total_drawn = total_new + total_dup
    dup_rate = (total_dup / total_drawn * 100) if total_drawn > 0 else 0
    col4.metric("♻️ Tỉ lệ Thẻ Trùng", f"{total_dup}/{total_drawn} ({dup_rate:.2f}%)")
    
    st.divider()
    st.subheader("Tiến độ theo Độ Hiếm")
    from ..config import MAX_CARDS
    
    rarity_colors = {
        1: "gray", 2: "#32CD32", 3: "#1E90FF",
        4: "#9370DB", 5: "#FFA500", 6: "#FF1493"
    }

    rarity_cols = st.columns(6)
    for r in range(1, 7):
        with rarity_cols[r-1]:
            if r < 6:
                icon_str = "⭐" * r
            else:
                icon_str = "<span style='font-size: 1.2em;'>🌟</span>"
            r_owned = st.session_state["inventory"][r]
            r_max = MAX_CARDS[r]
            color = rarity_colors[r]
            pct = int((r_owned / r_max) * 100) if r_max > 0 else 0
            
            html = f"""
            <div style='margin-bottom: 10px;'>
                <div style='font-weight: bold; color: {color}; margin-bottom: 8px;'>{icon_str}</div>
                <div style='width: 100%; background-color: rgba(128,128,128,0.2); border-radius: 5px; height: 10px; margin-bottom: 8px;'>
                    <div style='width: {pct}%; background-color: {color}; height: 100%; border-radius: 5px;'></div>
                </div>
                <div style='font-size: 0.85em; color: gray;'>{r_owned} / {r_max} thẻ</div>
            </div>
            """
            st.markdown(html, unsafe_allow_html=True)
    
    st.divider()
    st.subheader("Chi tiết 15 Set Thẻ")
    from ..config import CARD_SETS
    cols = st.columns(3)
    
    set_colors_rgb = [
        "255, 99, 132", "54, 162, 235", "255, 206, 86", 
        "75, 192, 192", "153, 102, 255", "255, 159, 64", 
        "233, 30, 99", "0, 150, 136", "139, 195, 74", 
        "205, 220, 57", "121, 85, 72", "96, 125, 139", 
        "244, 67, 54", "33, 150, 243", "156, 39, 176"
    ]
    
    for idx, (set_id, set_info) in enumerate(CARD_SETS.items()):
        with cols[idx % 3]:
            total_in_set = sum(set_info["cards"].values())
            owned_in_set = [c for c in st.session_state["owned_cards"] if c[0] == set_id]
            owned_count = len(owned_in_set)
            
            rgb = set_colors_rgb[idx % len(set_colors_rgb)]
            pct = int((owned_count / total_in_set) * 100) if total_in_set > 0 else 0
            
            breakdown_html = ""
            for r in sorted(set_info["cards"].keys()):
                r_total = set_info["cards"][r]
                r_owned = len([c for c in owned_in_set if c[1] == r])
                icon = "⭐" * r if r < 6 else "🌟"
                if r_owned == r_total:
                    breakdown_html += f"<div style='font-size:0.85em; margin-top:2px;'>✅ {icon} {r_owned}/{r_total}</div>"
                else:
                    breakdown_html += f"<div style='font-size:0.85em; margin-top:2px; opacity:0.7;'>⬛ {icon} {r_owned}/{r_total}</div>"
            
            is_completed = (total_in_set > 0 and owned_count == total_in_set)
            border_style = f"2px solid rgb({rgb})" if is_completed else f"1px solid rgba({rgb}, 0.5)"
            shadow_style = f"box-shadow: 0 0 12px rgba({rgb}, 0.6);" if is_completed else ""
            title_prefix = "🏆 " if is_completed else ""
            
            set_html = f"""
            <div style='background-color: rgba({rgb}, 0.15); padding: 15px; border-radius: 10px; border: {border_style}; {shadow_style} margin-bottom: 15px;'>
                <div style='font-weight: bold; margin-bottom: 8px;'>{title_prefix}Set {set_id}: {set_info['name']}</div>
                <div style='width: 100%; background-color: rgba(128,128,128,0.2); border-radius: 5px; height: 8px; margin-bottom: 8px;'>
                    <div style='width: {pct}%; background-color: rgb({rgb}); height: 100%; border-radius: 5px;'></div>
                </div>
                <div style='font-size: 0.9em; margin-bottom: 10px;'>Đã có: <b>{owned_count} / {total_in_set}</b> thẻ</div>
                {breakdown_html}
            </div>
            """
            st.markdown(set_html, unsafe_allow_html=True)


```

---

## File: `card_album/ui/main.py`

```python
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

from .inventory import render_inventory_tab
from .gacha import render_pack_opener_tab
from .chest_drop import render_chest_drop_tab
from .analytics import render_analytics_tab

def run_app() -> None:
    st.set_page_config(page_title="Card Album Simulator", layout="wide")
    ensure_album_state(st.session_state)
    
    col_title, col_btn = st.columns([0.95, 0.05], vertical_alignment="bottom")
    with col_title:
        st.title("🎲 Card Album Simulator")
    with col_btn:
        st.markdown(
            """
            <span id="info-button-target"></span>
            <style>
            div.element-container:has(#info-button-target) + div.element-container button {
                border-radius: 50% !important;
                padding: 0 !important;
                min-width: 28px !important;
                width: 28px !important;
                min-height: 28px !important;
                height: 28px !important;
                font-weight: normal !important;
                font-size: 16px !important;
                font-style: italic !important;
                font-family: 'Times New Roman', serif !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                background-color: var(--background-color, white) !important;
                color: var(--text-color, black) !important;
                border: 1px solid var(--text-color, black) !important;
            }
            div.element-container:has(#info-button-target) + div.element-container button * {
                color: var(--text-color, black) !important;
            }
            </style>
            """, 
            unsafe_allow_html=True
        )
        if st.button("i", type="primary", help="Infomation"):
            show_logic_dialog()
    
    tab_inventory, tab_manual, tab_chestdrop, tab_auto, tab_mc, tab_config = st.tabs(["📚 Bộ Sưu Tập", "📦 Mở Pack", "🎮 Chest Drop", "📈 LiveOps Economy", "📊 Monte Carlo Simulator", "⚙️ Economy Tuning"])
    
    with tab_inventory:
        render_inventory_tab()
        
    with tab_manual:
        render_pack_opener_tab()
        
    with tab_chestdrop:
        render_chest_drop_tab()
        
    with tab_mc:
        from ..monte_carlo import render_monte_carlo_tab
        render_monte_carlo_tab()
        
    with tab_auto:
        render_analytics_tab()
        
    with tab_config:
        from ..config_ui import render_config_tab
        render_config_tab()


@st.dialog("📖 TỔNG QUAN LOGIC HỆ THỐNG", width="large")
def show_logic_dialog():
    st.markdown("""
        <style>
            /* Hack to make the dialog wider on desktop screens */
            div[data-testid="stDialog"] div[role="dialog"] {
                width: 85vw !important;
                max-width: 1200px !important;
            }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
### 1. Cơ Chế Gacha Cơ Bản & Pity (Bảo hiểm)
- **Tỉ lệ Rớt Độ Hiếm (Drop Rates):** 
  - (VD: 28% ra 1-Sao, 1% ra Vàng) là **CỐ ĐỊNH** và luôn không đổi trong suốt quá trình mở gói.
- **Công thức Tỉ lệ Thẻ MỚI (New Chance):** 
  - Là tỉ lệ để lá thẻ vừa rớt ra rơi vào lá bạn CHƯA CÓ. Tỉ lệ này tự động trượt giảm dần theo công thức chung: 
  - `New Card Ratio = (Remaining New / Total) ^ (x + y) + Pity`
  - `x`: Hệ số Khó chung (Càng cao càng khó ra thẻ mới, tuỳ chỉnh trong Tuning).
  - `y`: Hệ số Khó riêng (Ở Gacha mở pack, y lấy theo loại Gói. Ở Chest Drop, y lấy theo Độ Hiếm của thẻ).
- **Thẻ Bảo Hiểm (Guaranteed):** Mỗi gói đều cam kết rớt 1 thẻ ở ĐÚNG độ hiếm cụ thể (Ví dụ gói Emerald chắc chắn có 1 thẻ 2-Sao).
- **Cơ Chế Pity (Đếm Tạch):** 
  - Hoạt động **độc lập** cho TỪNG LOẠI GÓI THẺ. (Pity của Silver KHÔNG chia sẻ cho Amethyst).
  - Mỗi khi mở một gói mà không ra bất kỳ thẻ **NEW** nào, số lần "Tạch" của gói đó tăng lên 1.
  - Khi tạch đến ngưỡng quy định, gói đó sẽ được **buff thêm % Tỉ lệ ra Thẻ Mới** ở lần mở sau. (Vd: Gói Silver tạch 3 lần sẽ buff +20%).
- **Ngắt Pity Giữa Chừng (Mid-Pack Reset):** Tỉ lệ buff Pity được cộng thẳng vào từng lá bài khi nó lật lên. Ngay khoảnh khắc lá bài đầu tiên nổ ra chữ **NEW**, lượng % buff này sẽ **lập tức bốc hơi (về 0%)**. Các lá bài lật sau đó trong cùng gói sẽ trở về tỉ lệ gốc, nhằm chống lạm phát thẻ mới.

### 2. Rainbow Pack & 5 Gói Tân Thủ
- **Tân Thủ:** 5 gói thẻ đầu tiên bạn nhận được trong Mùa (từ bất kỳ nguồn nào) sẽ được hệ thống buff **100% rớt toàn Thẻ Mới**.
- **Rainbow Pack:** Gói thẻ đặc quyền có 6 thẻ, trong đó chắc chắn rớt 1 Thẻ Mới (Wild Card). Thuật toán sẽ luôn ưu tiên rớt **Thẻ Vàng (6-Sao)** trước. 
  - *Clarification:* Trong game gốc, nếu Vàng đã full, Wild Card sẽ ưu tiên các "Bộ (Sets) chỉ còn thiếu 1 lá". Do Simulator này chỉ track tiến độ theo Độ Hiếm, hệ thống sẽ giả lập bằng cách rớt ngẫu nhiên 1 Thẻ Mới từ các độ hiếm còn thiếu.

### 3. Grand Album & Thẻ Trùng (Duplicated)
- **Hoàn thành Album:** Sau khi sưu tập đủ 135 thẻ, bạn sẽ hoàn thành vòng Album và được thăng cấp sang "Grand Album".
- **Luật Reset:** Khi thăng cấp, kho thẻ sẽ **bị Reset toàn bộ về 0**, nhưng lượng **Sao (Stars)** bạn tích lũy được sẽ **giữ nguyên vẹn** (Dùng để mua các rương sao sau này).
- **Thẻ Trùng:** Mọi thẻ trùng lặp quay ra sẽ tự động phân rã thành **Sao**. Thẻ càng hiếm, số Sao thu được càng cao (Từ 1 Sao cho thẻ 1-Sao lên tới 15 Sao cho Thẻ Vàng).

### 4. Hệ Sinh Thái LiveOps (Sự kiện & Nền kinh tế)
Trong tab `📈 LiveOps Simulator`, hệ thống sử dụng thuật toán giả lập để ước tính số Pack và Rương (Chest) bạn nhận được dựa trên giả định bạn chơi hoàn hảo (perfect play) theo số ngày và **khoảng số level ngẫu nhiên** mỗi ngày đã cấu hình:
- **Core Gameplay (Thắng màn Khó):** Cứ thắng màn Hard sẽ thưởng gói Bronze, thắng Super Hard thưởng gói Emerald. Tiến trình Level diễn ra theo chu kỳ cố định: N-N-H, N-N-H, N-N-SH (sau 2 Normal tới 1 Hard, sau 2 Hard tới 1 Super Hard).
- **Win Streak:** Giữ chuỗi thắng liên tiếp để càn quét các phần thưởng dọc đường. Sự kiện tự động kích hoạt vào mỗi cuối tuần (Thứ 6 đến Chủ Nhật). Chuỗi thắng bị reset về 0 mỗi đầu sự kiện. Từ lần đạt mốc cao nhất (Mốc 45) thứ 2 trở đi, phần thưởng Avatar sẽ được quy đổi thành Ruby Pack. *(Có thể xem chi tiết các phần thưởng ở tab Economy Tuning)*
- **Master Pass (Battle Pass):** Hệ thống Battle Pass của game. Thu thập token từ các màn chơi (Thắng Normal: 1 Token, Hard: 2 Tokens, Super Hard: 3 Tokens) để thăng cấp (tối đa 30) và nhận thưởng. Nhánh Premium (trả phí) sẽ mở khóa nhiều phần thưởng hấp dẫn hơn. Sự kiện được reset tiến trình và lặp lại mỗi tháng (30 ngày). *(Có thể xem chi tiết các phần thưởng ở tab Economy Tuning)*
- **Key Collection:** Cày chìa khóa theo tiến độ để mở khóa các phần thưởng theo mốc. Mỗi level qua màn nhận mặc định 5 keys bất kể độ khó. Sự kiện được reset tiến trình và lặp lại vào mỗi đầu tuần (Thứ 2). *(Có thể xem chi tiết các phần thưởng ở tab Economy Tuning)*
- **Chain Offer & IAP:** Các sự kiện bán gói ưu đãi theo chuỗi. Simulator cho phép bạn giả lập "tiêu tiền" vào các mốc Chain (VD: Mua OOC, Mua Shop) để tính toán tổng lợi nhuận Pack thu về so với số USD đã bỏ ra. Mặc định mua các gói này nhận Pack thường (Không áp dụng thưởng sự kiện Card Rush).
- **⚡ Card Rush:** Sự kiện đặc biệt mở theo lịch tuần (Tuần 1-6: Thứ 7 | Tuần 7 trở đi: Thứ 4, 7). Khi kích hoạt, các gói thẻ thường (Bronze, Emerald, Silver) sẽ chuyển thành **Plus (+), thêm 50% số lượng thẻ** vào từng gói (VD: Bronze từ 2 lên 3 thẻ, Emerald từ 3 lên 5 thẻ, Silver từ 4 lên 6 thẻ...). Mua gói từ Shop/IAP sẽ KHÔNG được cộng dồn Card Rush.

### 5. Minigame Đập Rương (Chest Drop)
- **Thu thập:** Nhận được từ việc cày cuốc (đạt mốc 3, 7, 12 level trong cùng 1 ngày sẽ nhận lần lượt rương 1-Sao, 2-Sao, 3-Sao).
- **Thăng Cấp Rương (Upgrade):** Khi mở rương, có xác suất rương sẽ tự động nâng cấp lên sao cao hơn (tối đa 5-Sao). Tỉ lệ thăng cấp phụ thuộc vào rương khởi đầu (Rương 3-Sao khởi đầu sẽ dễ nổ ra 5-Sao hơn rương 1-Sao).
- **Tránh trùng lặp (No-Dup):** Khi mở 1 Gói Thẻ hoặc 1 Rương bất kỳ, hệ thống đảm bảo các lá thẻ rớt ra trong **chính Gói/Rương đó** sẽ hoàn toàn khác nhau và không bị trùng lặp (nếu số lượng thẻ rớt ra vượt quá số lượng thẻ của game thì mới bắt buộc phải trùng).
    """)

```

---

## File: `card_album/ui/utils.py`

```python
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

def format_card_name_ui(card):
    if not card: return "Unknown"
    from ..config import CARD_SETS
    set_id, rarity, idx = card
    return f"{CARD_SETS[set_id]['name']} #{idx+1}"


```

---

