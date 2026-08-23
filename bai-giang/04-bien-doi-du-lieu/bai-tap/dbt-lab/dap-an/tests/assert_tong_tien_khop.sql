-- Trả về rỗng = đạt. Trả về dòng nào = dòng đó vi phạm.
with that as (
    select don_id, sum(so_luong * don_gia) as tong_tien_that
    from {{ source('nguon', 'chi_tiet_don') }}
    group by 1
)
select
    d.don_id,
    d.tong_tien                          as tong_tien_ghi,
    coalesce(t.tong_tien_that, 0)        as tong_tien_that
from {{ ref('stg_don_hang') }} d
left join that t using (don_id)
where d.tong_tien <> coalesce(t.tong_tien_that, 0)
