{% macro vnd(cot) %}
    round({{ cot }} / 1000, 0)
{% endmacro %}
