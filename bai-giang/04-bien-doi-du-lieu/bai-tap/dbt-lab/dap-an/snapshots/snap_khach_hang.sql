{% snapshot snap_khach_hang %}
{{ config(
    target_schema = 'main',
    unique_key    = 'ma_kh',
    strategy      = 'check',
    check_cols    = ['tinh', 'hang_thanh_vien']
) }}

select ma_kh, tinh, hang_thanh_vien
from {{ source('nguon', 'khach_hang') }}

{% endsnapshot %}
