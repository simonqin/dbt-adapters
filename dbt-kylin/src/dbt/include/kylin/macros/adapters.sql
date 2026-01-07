{% macro kylin__create_schema(relation) %}
  {{ kylin__readonly_error('create schema') }}
{% endmacro %}

{% macro kylin__drop_schema(relation) %}
  {{ kylin__readonly_error('drop schema') }}
{% endmacro %}

{% macro kylin__create_table_as(temporary, relation, compiled_code, language='sql') %}
  {{ kylin__readonly_error('create table as') }}
{% endmacro %}

{% macro kylin__get_create_table_as_sql(temporary, relation, sql) %}
  {{ kylin__readonly_error('create table as') }}
{% endmacro %}

{% macro kylin__create_view_as(relation, sql) %}
  {{ kylin__readonly_error('create view as') }}
{% endmacro %}

{% macro kylin__get_create_view_as_sql(relation, sql) %}
  {{ kylin__readonly_error('create view as') }}
{% endmacro %}

{% macro kylin__drop_relation(relation) %}
  {{ kylin__readonly_error('drop relation') }}
{% endmacro %}

{% macro kylin__truncate_relation(relation) %}
  {{ kylin__readonly_error('truncate relation') }}
{% endmacro %}

{% macro kylin__rename_relation(from_relation, to_relation) %}
  {{ kylin__readonly_error('rename relation') }}
{% endmacro %}

{% macro kylin__drop_table(relation) %}
  {{ kylin__readonly_error('drop table') }}
{% endmacro %}

{% macro kylin__drop_view(relation) %}
  {{ kylin__readonly_error('drop view') }}
{% endmacro %}

{% macro kylin__get_drop_sql(relation) %}
  {{ kylin__readonly_error('drop relation') }}
{% endmacro %}

{% macro kylin__get_rename_table_sql(relation, new_name) %}
  {{ kylin__readonly_error('rename table') }}
{% endmacro %}

{% macro kylin__get_rename_view_sql(relation, new_name) %}
  {{ kylin__readonly_error('rename view') }}
{% endmacro %}

{% macro kylin__get_replace_table_sql(existing_relation, target_relation, sql) %}
  {{ kylin__readonly_error('replace table') }}
{% endmacro %}

{% macro kylin__get_replace_view_sql(existing_relation, target_relation, sql) %}
  {{ kylin__readonly_error('replace view') }}
{% endmacro %}

{% macro kylin__create_or_replace_clone(this_relation, defer_relation) %}
  {{ kylin__readonly_error('clone') }}
{% endmacro %}

{% macro kylin__can_clone_table() %}
  {{ return(false) }}
{% endmacro %}

{% macro kylin__get_create_materialized_view_as_sql(relation, sql) %}
  {{ kylin__readonly_error('create materialized view') }}
{% endmacro %}

{% macro kylin__refresh_materialized_view(relation) %}
  {{ kylin__readonly_error('refresh materialized view') }}
{% endmacro %}

{% macro kylin__get_replace_materialized_view_sql(relation, sql) %}
  {{ kylin__readonly_error('replace materialized view') }}
{% endmacro %}

{% macro kylin__get_rename_materialized_view_sql(relation, new_name) %}
  {{ kylin__readonly_error('rename materialized view') }}
{% endmacro %}

{% macro kylin__drop_materialized_view(relation) %}
  {{ kylin__readonly_error('drop materialized view') }}
{% endmacro %}

{% macro kylin__create_csv_table(model, agate_table) %}
  {{ kylin__readonly_error('seed (create csv table)') }}
{% endmacro %}

{% macro kylin__reset_csv_table(model, full_refresh, old_relation, agate_table) %}
  {{ kylin__readonly_error('seed (reset csv table)') }}
{% endmacro %}

{% macro kylin__load_csv_rows(model, agate_table) %}
  {{ kylin__readonly_error('seed (load csv rows)') }}
{% endmacro %}

{% macro kylin__alter_column_type(relation, column_name, new_column_type) %}
  {{ kylin__readonly_error('alter column type') }}
{% endmacro %}

{% macro kylin__alter_relation_add_remove_columns(relation, add_columns, remove_columns) %}
  {{ kylin__readonly_error('alter relation columns') }}
{% endmacro %}

{% macro kylin__alter_relation_comment(relation, relation_comment) %}
  {{ kylin__readonly_error('alter relation comment') }}
{% endmacro %}

{% macro kylin__alter_column_comment(relation, column_dict) %}
  {{ kylin__readonly_error('alter column comment') }}
{% endmacro %}

{% macro kylin__apply_grants(relation, grant_config, should_revoke) %}
  {{ kylin__readonly_error('apply grants') }}
{% endmacro %}

{% macro kylin__get_create_index_sql(relation, index_dict) %}
  {{ kylin__readonly_error('create index') }}
{% endmacro %}

{% macro kylin__create_indexes(relation) %}
  {{ kylin__readonly_error('create index') }}
{% endmacro %}

{% macro kylin__get_drop_index_sql(relation, index_name) %}
  {{ kylin__readonly_error('drop index') }}
{% endmacro %}

{% macro kylin__get_show_indexes_sql(relation) %}
  {{ kylin__readonly_error('show indexes') }}
{% endmacro %}
