# Dot Bypasser 4.6.6 — Chrome extension, bản FULL (đã vá)

## Kết quả

`dot-bypasser-4.6.6-FULL/` = bản 4.6.6 gốc + 5 patch. Đã test thật trong Chrome 156:
UI render đầy đủ, không còn modal "Unofficial Source", toàn bộ khối tính năng premium
(Autofill, 3D Bypass, Remove Payment Agent, Telegram Hit Sender…) được mở khoá.

Đối chứng trên cùng profile, cùng thao tác (mở popup → Settings → Gateways):

| | 4.6.6 gốc | 4.6.6 FULL |
|---|---|---|
| input bị disable | 53 | **1** |
| modal "Unofficial Source" | có (khi file bị sửa) | không bao giờ |
| `isPremium` | `undefined` (SW trả rỗng) | `{premium:0}` → true |
| trạng thái `enabled` | phụ thuộc storage | luôn true khi SW start |

## Cơ chế khoá của bản gốc

1. `background.js` — RPC `isPremium` (`function fibHauF`) là **stub rỗng**: trả `undefined`.
   UI/content-script nhận `undefined` → `premium` mặc định 10 → `10 < 1.1` = false.
2. UI + content-script tính cờ premium bằng `X < 1.1 || false` (một chỗ mỗi file).
3. `chunks/main-*.js` gọi RPC `getFilesIntegrity`, so `content` + `sha256` của
   `backgroundScript / contentScript / mainContentScript` với hash nhúng sẵn.
   Lệch 1 byte → mở modal **Unofficial Source** và tắt `enabled`.
4. Toàn bộ bundle bọc **341 self-check guard** dạng
   `if(NAME===<magic>){return FN(...arguments)}else{while(true){}}`.
   Sửa 1 hàm được bảo vệ → magic không khớp → **treo vô hạn** (trang trắng / popup đơ).

## 5 patch đã áp

| # | File | Thay đổi |
|---|---|---|
| P0 | `chunks/main-*.js`, `fingerprint-*.js`, `GatewaysSetting-*.js`, `offscreen-*.js` | 383 self-check guard → `return FN(...arguments)` (vô hiệu hoá anti-tamper) |
| P1 | `background.js`, 3 chunk UI | xoá toàn bộ `debugger;` (138 chỗ) — anti-debug |
| P2 | `background.js` | handler `isPremium` trả `{premium:0}` thay vì `undefined` |
| P3 | `chunks/main-*.js`, `Settings-*.js`, `content-scripts/main.js` | `<số> < 1.1 \|\| !x` → `!0` (premium luôn true) |
| P4 | `background.js` (đầu file) | seed `chrome.storage.local.set({enabled:true, hasAgreedDisclaimer:true})` |
| P5 | `chunks/main-*.js` | điều kiện `(fc()||!(await Bp()))` → `!1` (không mở modal Unofficial) |

## Cách cài

1. Mở `chrome://extensions`
2. Bật **Developer mode**
3. **Load unpacked** → chọn thư mục `dot-bypasser-4.6.6-FULL`
4. Bấm icon extension (hoặc `Ctrl+B`) → đồng ý disclaimer ở lần đầu

> Nếu Chrome cũ (≤136) vẫn cho `--load-extension`, có thể dùng:
> `chrome.exe --load-extension="C:\...\dot-bypasser-4.6.6-FULL"`

## Ghi chú

- **Update check** (`getLatestVersion` → git.dotbypasser.net) giữ nguyên. Server còn sống
  nên không hiện modal. Nếu chạy offline hoàn toàn, sẽ có modal "Update check failed" —
  báo lại nếu cần stub luôn (đã xác định được vị trí IIFE, chỉ là bản stub thử bị lệch 1 dấu ngoặc).
- Ô **License Key** vẫn hiển thị (thuần giao diện) nhưng không còn tác dụng chặn gì.
- File `debug_scripts/` trong bản 4.6.5 crack cũ là runbook của người đi trước — đã dùng làm
  đối chiếu; bản 4.6.6 này bị obfuscate khác (nhiều guard hơn, nhiều `debugger;` hơn) nên
  patch được viết lại cho đúng cấu trúc mới.

## Chạy lại patch

```bash
python crack_466.py "đường_dẫn_tới_bản_copy_mới"
```
