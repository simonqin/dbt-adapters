{% macro kylin__concat(fields) -%}
    concat({{ fields|join(', ') }})
{%- endmacro %}
