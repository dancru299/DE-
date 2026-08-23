{{ config(
    materialized = 'incremental',
    unique_key = 'ngay',
    incremental_strategy = 'delete+insert'
) }}

select
    ngay_dat        as ngay,
    count(*)        as so_don,
    sum(tong_tien)  as doanh_thu
from {{ ref('stg_don_hang') }}
where la_hoan_thanh

{% if is_incremental() %}
    -- Chỉ chạy từ lần thứ hai trở đi.
    -- {{ this }} = chính bảng này ở trạng thái hiện tại trong kho.
    -- Trừ 3 ngày = CỬA SỔ NHÌN LẠI, để bắt lại những đơn về trễ.
    -- Tính lại 3 ngày không sợ nhân đôi vì unique_key + delete+insert
    -- đã làm cho model này idempotent.
    and ngay_dat >= (select coalesce(max(ngay), date '1900-01-01') - 3 from {{ this }})
{% endif %}

group by 1
