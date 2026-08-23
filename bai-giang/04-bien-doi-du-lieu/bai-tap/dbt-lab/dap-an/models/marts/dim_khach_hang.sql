with chi_tieu as (
    select
        ma_kh,
        count(*)        as so_don,
        sum(tong_tien)  as tong_chi_tieu,
        max(ngay_dat)   as ngay_mua_gan_nhat
    from {{ ref('stg_don_hang') }}
    where la_hoan_thanh
    group by 1
)

select
    k.ma_kh,
    k.ten,
    k.tinh,
    k.hang_thanh_vien,
    k.ngay_dang_ky,
    coalesce(c.so_don, 0)         as so_don,
    coalesce(c.tong_chi_tieu, 0)  as tong_chi_tieu,
    c.ngay_mua_gan_nhat
from {{ ref('stg_khach_hang') }} k
left join chi_tieu c using (ma_kh)
