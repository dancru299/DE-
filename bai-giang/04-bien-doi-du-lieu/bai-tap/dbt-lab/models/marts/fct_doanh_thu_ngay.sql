-- D3 · Model INCREMENTAL — bài quan trọng nhất của phần dbt
--
-- Nhiệm vụ: bảng doanh thu theo ngày, chạy tăng dần thay vì tính lại từ đầu.
--
-- Cần khai báo config với 4 thứ:
--   materialized  = 'incremental'
--   unique_key    = 'ngay'          -> dbt biết dòng nào là "cùng một dòng"
--   incremental_strategy = 'delete+insert'
--   (tuỳ chọn) partition/ order
--
-- Rồi bọc phần lọc trong {% if is_incremental() %} ... {% endif %}
--   - lần chạy ĐẦU (bảng chưa tồn tại): khối này bị bỏ qua -> tính toàn bộ lịch sử
--   - các lần sau: chỉ tính lại vài ngày gần đây
--
-- BẮT BUỘC dùng CỬA SỔ NHÌN LẠI 3 ngày, đừng chỉ lấy đúng ngày mới nhất.
-- Lý do: đơn về trễ (xem B14). Chỉ lấy 1 ngày là vĩnh viễn thiếu số.

select
    ngay_dat as ngay,
    count(*) as so_don,
    sum(tong_tien) as doanh_thu
from {{ source('nguon', 'don_hang') }}
where trang_thai = 'hoan_thanh'
group by 1
-- TODO: thêm config(...) ở đầu file và khối is_incremental()
