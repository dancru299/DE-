-- Tầng staging: ép kiểu, đổi tên cột cho thống nhất. 1 dòng nguồn = 1 dòng ra.
select
    booking_id,
    customer_id,
    hotel_code,
    cast(checkin_date  as date)      as ngay_nhan_phong,
    cast(checkout_date as date)      as ngay_tra_phong,
    upper(trim(status))              as trang_thai,
    cast(total_amount as bigint)     as tong_tien,
    cast(created_at as timestamp)    as tao_luc,
    cast(updated_at as timestamp)    as cap_nhat_luc
from {{ source('lake', 'bookings') }}
