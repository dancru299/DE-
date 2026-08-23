select
    don_id,
    khach_id,
    'KH' || lpad(khach_id::varchar, 4, '0')  as ma_kh,   -- chuẩn hoá khoá nối
    ngay_dat,
    trang_thai,
    tong_tien::bigint                        as tong_tien,
    cap_nhat_luc,
    trang_thai = 'hoan_thanh'                as la_hoan_thanh
from {{ source('nguon', 'don_hang') }}
