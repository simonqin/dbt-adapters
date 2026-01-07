{#-- Kylin v3 supports 'bool_or' and 'any', but Kylin v2 needs to use 'max' for this
  -- https://spark.apache.org/docs/latest/api/sql/index.html#any
  -- https://spark.apache.org/docs/latest/api/sql/index.html#bool_or
  -- https://spark.apache.org/docs/latest/api/sql/index.html#max
#}

{% macro kylin__bool_or(expression) -%}

    max({{ expression }})

{%- endmacro %}
