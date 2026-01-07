{# Read-only adapter: block all write materializations. #}

{% macro kylin__readonly_error(operation) -%}
  {{ exceptions.raise_compiler_error("Kylin adapter is read-only; " ~ operation ~ " is not supported.") }}
{%- endmacro %}

{% materialization table, adapter='kylin' %}
  {{ kylin__readonly_error('table materialization') }}
{% endmaterialization %}

{% materialization view, adapter='kylin' %}
  {{ kylin__readonly_error('view materialization') }}
{% endmaterialization %}

{% materialization incremental, adapter='kylin' %}
  {{ kylin__readonly_error('incremental materialization') }}
{% endmaterialization %}

{% materialization snapshot, adapter='kylin' %}
  {{ kylin__readonly_error('snapshot materialization') }}
{% endmaterialization %}

{% materialization seed, adapter='kylin' %}
  {{ kylin__readonly_error('seed materialization') }}
{% endmaterialization %}

{% materialization clone, adapter='kylin' %}
  {{ kylin__readonly_error('clone materialization') }}
{% endmaterialization %}

{% materialization materialized_view, adapter='kylin' %}
  {{ kylin__readonly_error('materialized view materialization') }}
{% endmaterialization %}
