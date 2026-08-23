-- D2b · Model mart đầu tiên, nối hai model staging lại
--
-- Nhiệm vụ: bảng khách hàng phục vụ báo cáo, gồm thông tin khách
-- kèm các chỉ số: so_don, tong_chi_tieu, ngay_mua_gan_nhat.
--
-- Chú ý: ở tầng mart phải gọi model khác bằng {{ ref('ten_model') }},
-- KHÔNG dùng {{ source(...) }} nữa. Nhầm chỗ này là lỗi phổ biến nhất
-- của người mới học dbt — nó phá vỡ lineage và dbt sẽ chạy sai thứ tự.

select *
from {{ ref('stg_khach_hang') }}
-- TODO: nối với stg_don_hang để thêm 3 chỉ số ở trên
