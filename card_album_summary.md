# Card Album Economy - Technical Specification (Chi Tiết Implement)

Tài liệu này đóng vai trò là **Bản Đặc Tả Kỹ Thuật (Technical Spec)** đi sâu vào tận cùng các biến số, luồng thực thi (execution flow) và logic toán học của hệ thống Card Album. Dành riêng cho Kỹ sư và Game Designer để tái cấu trúc (re-implement) hệ thống vào một dự án khác.

---

## 1. Dữ Liệu Nền Tảng (Core Data Structures)
Hệ thống sử dụng các hằng số tĩnh để định hình bộ sưu tập:
- **Rarities**: `[1, 2, 3, 4, 5, 6]` (6 là thẻ Vàng).
- **Max Cards per Rarity**: `{1: 33, 2: 28, 3: 23, 4: 18, 5: 15, 6: 18}`. Tổng cộng 135 thẻ.
- **Card Sets**: 15 Sets. Mỗi Set chứa một tổ hợp thẻ khác nhau (Ví dụ: Set 1 có 8 thẻ 1-Sao, 1 thẻ 2-Sao). Mỗi thẻ được định danh duy nhất bằng tuple `(set_id, rarity, index)`.
- **Star Values (Duplicate)**: `{1: 1, 2: 2, 3: 3, 4: 5, 5: 10, 6: 15}`.

**State của Người Chơi (Session State):**
- `inventory`: Dict lưu số lượng thẻ đã mở khoá theo từng độ hiếm (VD: `{1: 33, 2: 10...}`).
- `owned_cards`: Set chứa các tuple định danh thẻ đã sở hữu `(set_id, rarity, index)`.
- `stars`: Số dư sao hiện tại.
- `pack_pity`: Dict lưu số Pack mở "tạch" (chưa ra thẻ mới) của từng loại Pack.

---

## 2. Thuật Toán Gacha Rớt Thẻ (Card Rolling Algorithm)

Luồng rút một lá bài cụ thể (`roll_card`) yêu cầu 2 bước: Bước 1 tính tỷ lệ ra thẻ mới, Bước 2 chọn đích danh lá bài.

### 2.1. Tính tỷ lệ Thẻ Mới (Calculate New Chance)
```python
base_new = (max_cards - cards_owned) / max_cards
final_power = global_power_x + pack_y_value
new_chance = base_new ^ final_power
final_chance = min(1.0, new_chance + pity_bonus)
```
**Lưu ý khi Implement:**
- Nếu `cards_owned >= max_cards`, hàm trả về 0.0 ngay lập tức (Bắt buộc rớt thẻ trùng).
- Công thức luỹ thừa `^` làm cho việc ra thẻ mới cực kỳ khó khi `base_new` nhỏ (tiến gần đến việc full thẻ). `y_value` âm từ các Pack cao cấp (VD: Gold pack có `y = -1.0`) giúp triệt tiêu `global_power_x` (thường là `2.5`), đẩy `final_chance` lên cao.

### 2.2. Chọn Bài (Pick Card Logic)
- **Nếu trúng Thẻ Mới (`pick_new_card`):** Lọc toàn bộ danh sách thẻ thoả mãn `rarity`, loại trừ các thẻ có trong `owned_cards` VÀ loại trừ các thẻ vừa rút được trong cùng một Pack (`drawn_in_batch`). Sau đó áp dụng logic nhét bài **SS2 Set Pity** (xem Phần 4) hoặc random ngẫu nhiên. Thẻ chọn xong sẽ lập tức được add vào `owned_cards` và `drawn_in_batch`.
- **Nếu trúng Thẻ Trùng (`pick_dup_card`):** Lọc toàn bộ thẻ **đã sở hữu** của `rarity` đó (loại trừ `drawn_in_batch` để không ra 2 lá trùng y hệt nhau trong 1 pack). Random 1 lá. Nếu player chưa sở hữu lá nào của rarity đó (trường hợp cực hiếm do lỗi state), fallback random toàn bộ danh sách thẻ của rarity đó.

---

## 3. Luồng Mở Gói (Pack Opening Flow)

Mỗi `PackConfig` chứa các thông số: `size`, `weights` (dict trọng số rớt các rarity), `guaranteed_tier`, `pity_threshold`, `pity_increment`.

**Execution Flow của hàm `open_pack(pack_type)`:**
1. **Lấy Pity Bonus (Khởi đầu gói):**
   - Nếu `total_packs <= 5` (Tân thủ): Trả về `pity_bonus = 1.0` (100%).
   - Hoặc nếu gói này chưa từng mở (First Pack Luck SS2): Trả về `pity_bonus = 1.0` (100%).
   - Nếu không, kiểm tra `pack_pity[pack_type] >= threshold`. Nếu đúng, `pity_bonus = (misses - threshold + 1) * increment`.
2. **Khởi tạo mảng:** `drawn_in_batch = set()`, `current_pity_bonus = pity_bonus`.
3. **Vòng lặp ngẫu nhiên (n-1 lá bài):**
   - Lặp `size - 1` lần.
   - Quay random `rarity` dựa trên `weights`.
   - Gọi `roll_card(rarity, current_pity_bonus)`.
   - **ĐẶC BIỆT CHÚ Ý:** Nếu bốc trúng thẻ "NEW", hệ thống kiểm tra nếu đây **không phải** là Gói Tân Thủ (`total_packs > 5`) VÀ **không phải** First Pack Luck, thì lập tức `current_pity_bonus = 0.0` để huỷ buff bảo hiểm cho các lá bài còn lại trong gói. (Ngược lại, Tân Thủ và First Pack Luck sẽ giữ nguyên buff 1.0 cho *toàn bộ* lá bài trong gói).
4. **Lá bài Bảo Hiểm (Lá cuối cùng):**
   - Nếu Pack là "Rainbow": Chạy hàm `open_rainbow_pack_guaranteed`. Cố gắng nhét thẻ VÀNG (6-Sao) mới. Nếu full VÀNG, nhét thẻ mới ngẫu nhiên từ 1->5 Sao. Nếu full toàn bộ game, nhét VÀNG trùng.
   - Nếu Pack thường: Cố định `rarity = guaranteed_tier` và gọi `roll_card` như bình thường.
5. **Cập nhật Pity (End of Pack):**
   - Nếu gói vừa mở có **ít nhất 1 lá NEW**, set `pack_pity[pack_type] = 0`.
   - Nếu gói toàn DUP, `pack_pity[pack_type] += 1`.

---

## 4. Bàn Tay Vô Hình - Set Completion Pity (SS2)

Cơ chế này can thiệp trực tiếp vào hàm `pick_new_card`. Khi hệ thống đã quyết định thả một lá "Thẻ Mới" có `rarity` nhất định, nó tính toán xem có nên can thiệp "nhét" lá bài đó vào Set Thẻ mà user đang khao khát nhất hay không.

**Luồng thực thi Set Pity:**
1. Tính mảng `set_counts`: Số lượng thẻ đang sở hữu của mỗi Set (Lưu ý: Quét realtime trên `owned_cards`, tức là đã bao gồm cả thẻ vừa rút ở lá trước trong cùng batch).
2. Xác định `completed_sets` (số set đã full thẻ).
3. Tìm `best_set_id`: Set chưa hoàn thành có số thẻ sở hữu cao nhất.
4. Kiểm tra xem `best_set_id` có còn thiếu thẻ của `rarity` đang xét hay không (`owned_rarity_count < total_rarity`).
5. Nếu thoả mãn, tính 2 hệ số nhét bài:
   - `pity_set = s_base + (s_max - s_base) * (1.0 - completed_sets / 15)`
   - `eff_r = min(5, rarity)` (Gom thẻ Vàng và 5-sao chung độ khó).
   - `pity_rarity_card = c_base + (c_max - c_base) * (5.0 - eff_r) / 4.0`
6. Quay `random.random() < (pity_set * pity_rarity_card)`.
   - Nếu Pass: Lọc riêng các thẻ thiếu trong `best_set_id` và random pick 1 lá.
   - Nếu Fail hoặc không thoả mãn điều kiện: Random pick trong TOÀN BỘ các thẻ thiếu của `rarity` đó trên toàn album.

---

## 5. Chest Drop Minigame (Đập Rương Win Streak)

Đây là một minigame độc lập (Sandbox / LiveOps), người chơi gõ búa 5 lần (5 Hits) vào một cái Rương.

**Luồng thực thi cho 1 Hit (`process_chest_drop_hit`):**
1. **Xác định Rarity của Hit:** Sử dụng `CHEST_DROP_TIERS[current_tier].weights` để random ra `drop_rarity`. Lưu ý: Rương 1-Sao chỉ rớt độ hiếm 1-Sao, Rương 5-Sao rớt thẻ 5-Sao (60%) và thẻ Vàng (40%).
2. **Tính tỷ lệ New Card:** `y_value` được lấy từ Rương (`current_tier`), KHÔNG PHẢI từ `drop_rarity`. 
   `new_chance = (Remaining New / Max Cards) ^ (2.0 + y_value)`.
3. Gọi `roll_chest_drop_card` (Bản chất giống `roll_card` nhưng không có `pity_bonus` và không có cơ chế `First Pack Luck`). Vẫn áp dụng `Set Completion Pity` (SS2) khi `pick_new_card`.
4. **Upgrade Tier:** Tra cứu ma trận `CHEST_UPGRADE_MATRIX[start_tier][current_tier]`.
   - Nếu `start_tier` = 1, `current_tier` = 1, `chance` = 0.35 (35%).
   - Quay random, nếu trúng: `next_tier = current_tier + 1`. (Chỉ thăng đúng 1 cấp).
5. Trả về kết quả Hit (Thẻ rớt ra, trạng thái NEW/DUP, có thăng cấp hay không, và `next_tier` để dùng cho Hit tiếp theo).

---

## 6. Grand Album (Prestige System)

Hàm `check_grand_album` được kích hoạt mỗi khi nhặt thẻ mới.
- Kiểm tra số lượng thẻ thu thập `== 135`.
- Nếu `grand_album_completions < 1`:
  - Reset `inventory` về `{1: 0, 2: 0...}`.
  - Reset `owned_cards` = `set()`.
  - Tăng `completions += 1`.
  - Gửi log chúc mừng bước sang Grand Album.
- Nếu `completions == 1` và full thẻ lần 2:
  - Bật cờ `grand_album_finished = True`.
  - KHÔNG reset nữa. Các thẻ sau này bốc được tự động nhảy vào fallback Duplicate và quy đổi thành Sao. 

---

## 7. Luồng "Card Rush" LiveOp
Cơ chế cực kỳ đơn giản để thúc đẩy tiêu dùng:
- Khi Event "Card Rush" kích hoạt, cờ `is_cr = True`.
- Hệ thống `open_pack` tự động Append dấu `+` vào `pack_type`. (Ví dụ: `Bronze` gọi thành `Bronze+`).
- Nếu `Bronze+` tồn tại trong `PACKS` config, hệ thống sẽ mở theo config của bản `+` (Về bản chất, bản `+` chỉ có thông số `size` lớn hơn 1, giữ nguyên `weights` và `guaranteed_tier`).
- Nếu bản `+` không tồn tại (Ví dụ gói Rainbow), hệ thống fallback về gói gốc.

**--- END OF SPECIFICATION ---**
Tài liệu này bao quát các luồng xử lý và sai số toán học (edge cases) được code xử lý (như chống trùng thẻ trong cùng 1 pack qua biến `drawn_in_batch`). Các kỹ sư Backend/Game Logic có thể bám vào đây để lập trình kiến trúc hoàn chỉnh.
