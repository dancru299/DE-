-- D6 · Macro — hàm dùng lại của dbt, viết bằng Jinja
--
-- Nhiệm vụ: viết macro vnd(cot) trả về biểu thức làm tròn về nghìn đồng.
-- Dùng trong model:  {{ vnd('tong_tien') }} as tong_tien_nghin
--
-- Macro là cách chống lặp code. Khi logic đổi, sửa một chỗ,
-- mọi model dùng nó đổi theo.

{% macro vnd(cot) %}
    {{ cot }}
{% endmacro %}
-- TODO: sửa thành round({{ cot }} / 1000, 0)
