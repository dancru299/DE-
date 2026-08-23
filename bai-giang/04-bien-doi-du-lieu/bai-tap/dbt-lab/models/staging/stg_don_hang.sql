-- D2 · Staging cho đơn hàng
--
-- Nhiệm vụ: chuẩn hoá tên cột và ép kiểu, thêm cột la_hoan_thanh (boolean),
-- và thêm cột ma_kh = 'KH' || lpad(khach_id, 4, '0') để nối được với stg_khach_hang.
-- (bảng thô chỉ có ma_kh, bảng đơn chỉ có khach_id — chuẩn hoá khoá nối
--  là việc rất hay phải làm ở tầng staging)
-- Vẫn giữ nguyên tắc: một model = một bảng nguồn, không join.

select *
from {{ source('nguon', 'don_hang') }}
-- TODO
