-- Cùng mẫu khử trùng lặp như stg_services.
-- Model này là đầu vào cho snapshot ở bài 6, nên bắt buộc mỗi khách chỉ 1 dòng.
select
    customer_id,
    full_name                        as ho_ten,
    lower(trim(email))               as email,
    city                             as thanh_pho,
    cast(updated_at as timestamp)    as cap_nhat_luc
from {{ source('lake', 'customers') }}
qualify row_number() over (
            partition by customer_id
            order by updated_at desc
        ) = 1
