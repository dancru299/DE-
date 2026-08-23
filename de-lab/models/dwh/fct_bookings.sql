{{
    config(
        materialized = 'incremental'
    )
}}

-- ============================================================================
-- Bảng fact đơn đặt phòng.
--
-- 'incremental' = lần chạy đầu tạo bảng đầy đủ; những lần sau CHỈ xử lý
-- phần dữ liệu mới rồi ghi thêm vào. Ở công ty bạn đây là kiểu materialization
-- quan trọng nhất -- vì quét lại toàn bộ bảng mỗi ngày trên BigQuery là đốt tiền.
--
-- Khối is_incremental() ở cuối file chỉ được chèn vào SQL ở những lần chạy SAU.
-- Muốn xem SQL thật sự chạy, mở: target/compiled/de_lab/models/dwh/fct_bookings.sql
-- ============================================================================

select
    booking_id,
    customer_id,
    hotel_code,
    ngay_nhan_phong,
    ngay_tra_phong,
    trang_thai,
    tong_tien,
    date_diff('day', ngay_nhan_phong, ngay_tra_phong) as so_dem,
    tao_luc,
    cap_nhat_luc

from {{ ref('stg_bookings') }}

{% if is_incremental() %}

  -- Chỉ lấy dòng mới hơn dòng mới nhất đang có trong bảng
  where cap_nhat_luc > (select max(cap_nhat_luc) from {{ this }})

{% endif %}
