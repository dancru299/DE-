-- ============================================================================
-- Tầng mart: bảng phục vụ một nhu cầu nghiệp vụ CỤ THỂ.
--
-- Ở đây: danh sách đơn đã xác nhận CÓ dịch vụ đưa đón -- đúng dạng bảng mà
-- một hệ thống downstream (CRM, marketing automation...) sẽ đọc để gửi đi.
--
-- Đặc điểm của mart: đã lọc, đã join, đã sẵn sàng dùng. Người đọc bảng này
-- không cần biết gì về tầng dưới.
-- ============================================================================

with don as (
    select * from {{ ref('fct_bookings') }}
    where trang_thai = 'CONFIRMED'
),

dua_don as (
    select * from {{ ref('stg_services') }}
    where loai_dich_vu = 'SHUTTLE'
),

khach_hang as (
    select * from {{ ref('stg_customers') }}
)

select
    d.booking_id,
    d.customer_id,
    k.ho_ten,
    d.hotel_code,
    d.ngay_nhan_phong,
    d.so_dem,
    d.tong_tien,
    dd.gio_don,
    dd.so_tien           as tien_dua_don,
    d.cap_nhat_luc

from don d
inner join dua_don dd
        on d.booking_id = dd.booking_id
left join khach_hang k
       on d.customer_id = k.customer_id
