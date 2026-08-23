with moi_nhat as (
    select *
    from {{ source('nguon', 'khach_hang_raw') }}
    qualify row_number() over (partition by ma_kh order by nhan_luc desc) = 1
)

select
    ma_kh,
    array_to_string(
        list_transform(string_split(lower(trim(ten)), ' '),
                       lambda x: case when x = '' then x else upper(x[1]) || x[2:] end),
        ' ')                                        as ten,
    coalesce(tinh, 'khong_ro')                      as tinh,
    lower(hang_thanh_vien)                          as hang_thanh_vien,
    coalesce(
        try_strptime(ngay_dang_ky_text, '%Y-%m-%d'),
        try_strptime(ngay_dang_ky_text, '%d/%m/%Y')
    )::date                                         as ngay_dang_ky,
    nhan_luc
from moi_nhat
