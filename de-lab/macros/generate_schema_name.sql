{#
  Mặc định dbt đặt tên schema là <schema_trong_profiles>_<schema_trong_config>,
  ví dụ "dwh_mart" -- xấu và khó hiểu.

  Macro này ghi đè hành vi đó: config ghi gì thì lấy đúng thế.
  Gần như mọi dbt repo thật đều có macro này. Bạn sẽ gặp lại nó ở repo công ty.
#}
{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- if custom_schema_name is none -%}
        {{ target.schema }}
    {%- else -%}
        {{ custom_schema_name | trim }}
    {%- endif -%}
{%- endmacro %}
