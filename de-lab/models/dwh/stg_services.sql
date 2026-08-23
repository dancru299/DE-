-- ============================================================================
-- MẪU KHỬ TRÙNG LẶP -- đọc kỹ, bài 3 bạn sẽ phải tự áp dụng mẫu này.
--
-- Lake là append-only: sửa 1 dịch vụ -> có 2 dòng cùng service_id.
-- QUALIFY giữ lại đúng dòng mới nhất của mỗi key.
-- (QUALIFY có ở cả DuckDB và BigQuery -- lọc trên kết quả window function,
--  gọn hơn nhiều so với bọc subquery rồi where rn = 1)
-- ============================================================================
select
    service_id,
    booking_id,
    upper(trim(service_type))        as loai_dich_vu,
    cast(amount as bigint)           as so_tien,
    cast(pickup_time as timestamp)   as gio_don,
    cast(updated_at as timestamp)    as cap_nhat_luc
from {{ source('lake', 'services') }}
qualify row_number() over (
            partition by service_id
            order by updated_at desc
        ) = 1
