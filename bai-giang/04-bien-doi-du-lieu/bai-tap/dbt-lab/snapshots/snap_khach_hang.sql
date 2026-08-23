-- D5 · Snapshot — SCD Type 2 phiên bản dbt
--
-- Ở bài B13 bạn tự dựng bảng lịch sử bằng LEAD. dbt làm sẵn việc đó:
-- mỗi lần chạy `dbt snapshot`, nó so bản hiện tại với bản đã lưu,
-- thấy khác thì đóng dòng cũ (dbt_valid_to) và mở dòng mới.
--
-- TODO: điền config còn thiếu
--   target_schema = 'main'
--   unique_key    = 'ma_kh'
--   strategy      = 'check'
--   check_cols    = ['tinh', 'hang_thanh_vien']
--
-- strategy 'check'     : so nội dung cột -> dùng khi nguồn KHÔNG có cột updated_at
-- strategy 'timestamp' : tin vào cột thời gian -> nhanh hơn, nên ưu tiên khi có

{% snapshot snap_khach_hang %}
{{ config(target_schema='main', unique_key='ma_kh', strategy='check', check_cols=['tinh']) }}

select ma_kh, tinh, hang_thanh_vien
from {{ source('nguon', 'khach_hang') }}

{% endsnapshot %}
