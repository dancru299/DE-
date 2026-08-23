-- D1 · Model staging đầu tiên
--
-- Nhiệm vụ: biến khach_hang_raw thành bảng sạch.
--   1. khử trùng theo ma_kh, giữ bản nhan_luc mới nhất   (dùng lại B1/B2)
--   2. trim tên, tinh NULL -> 'khong_ro', hạng về chữ thường
--   3. parse ngay_dang_ky_text (hai định dạng) về DATE   (dùng lại B3)
--
-- Quy tắc vàng của tầng staging: CHỈ làm sạch, KHÔNG gộp bảng,
-- KHÔNG tính toán nghiệp vụ. Một model staging ứng với đúng một bảng nguồn.
--
-- Chú ý: luôn gọi nguồn bằng {{ source(...) }}, không viết thẳng tên bảng.
-- Nhờ vậy dbt mới vẽ được sơ đồ lineage và biết thứ tự chạy.

select *
from {{ source('nguon', 'khach_hang_raw') }}
-- TODO: viết lại cho đúng nhiệm vụ ở trên
