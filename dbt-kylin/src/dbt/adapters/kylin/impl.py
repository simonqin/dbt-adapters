from typing import Any, Iterable, FrozenSet, List, Optional, Tuple

from dbt.adapters.base import BaseRelation
from dbt.adapters.base.impl import ConstraintSupport
from dbt.adapters.contracts.relation import RelationConfig, RelationType
from dbt.adapters.sql import SQLAdapter
from dbt_common.clients.agate_helper import table_from_rows
from dbt_common.contracts.constraints import ConstraintType
from dbt_common.exceptions import DbtRuntimeError

from dbt.adapters.kylin.column import KylinColumn
from dbt.adapters.kylin.connections import KylinConnectionManager
from dbt.adapters.kylin.relation import KylinRelation

try:
    from kylinpy.exceptions import NoSuchTableError
except ImportError:
    NoSuchTableError = None


def _extract_comment(metadata: Any) -> Optional[str]:
    if not isinstance(metadata, dict):
        return None
    lowered = {str(key).lower(): value for key, value in metadata.items()}
    for key in (
        "comment",
        "remarks",
        "description",
        "desc",
        "comment_text",
        "column_comment",
        "table_comment",
    ):
        value = metadata.get(key)
        if not value:
            value = lowered.get(key)
        if value:
            return str(value)
    return None


class KylinAdapter(SQLAdapter):
    Relation = KylinRelation
    ConnectionManager = KylinConnectionManager
    Column = KylinColumn
    CATALOG_COLUMN_NAMES = (
        "table_database",
        "table_schema",
        "table_name",
        "table_type",
        "table_comment",
        "table_owner",
        "column_name",
        "column_index",
        "column_type",
        "column_comment",
    )

    CONSTRAINT_SUPPORT = {
        ConstraintType.check: ConstraintSupport.NOT_ENFORCED,
        ConstraintType.not_null: ConstraintSupport.NOT_ENFORCED,
        ConstraintType.unique: ConstraintSupport.NOT_ENFORCED,
        ConstraintType.primary_key: ConstraintSupport.NOT_ENFORCED,
        ConstraintType.foreign_key: ConstraintSupport.NOT_ENFORCED,
    }

    @classmethod
    def is_cancelable(cls) -> bool:
        return False

    @classmethod
    def date_function(cls) -> str:
        return "current_timestamp()"

    @classmethod
    def convert_text_type(cls, agate_table, col_idx: int) -> str:
        return "string"

    @classmethod
    def convert_number_type(cls, agate_table, col_idx: int) -> str:
        import agate

        decimals = agate_table.aggregate(agate.MaxPrecision(col_idx))
        return "double" if decimals else "bigint"

    @classmethod
    def convert_integer_type(cls, agate_table, col_idx: int) -> str:
        return "bigint"

    @classmethod
    def convert_date_type(cls, agate_table, col_idx: int) -> str:
        return "date"

    @classmethod
    def convert_time_type(cls, agate_table, col_idx: int) -> str:
        return "time"

    @classmethod
    def convert_datetime_type(cls, agate_table, col_idx: int) -> str:
        return "timestamp"

    @classmethod
    def quote(cls, identifier: str) -> str:
        return '"{}"'.format(identifier)

    def _get_handle(self) -> Any:
        connection = self.connections.get_thread_connection()
        return connection.handle

    def _raise_not_supported(self, operation: str) -> None:
        raise DbtRuntimeError(
            "Kylin adapter is read-only; {} is not supported.".format(operation)
        )

    def create_schema(self, relation: BaseRelation) -> None:
        self._raise_not_supported("create schema")

    def drop_schema(self, relation: BaseRelation) -> None:
        self._raise_not_supported("drop schema")

    def drop_relation(self, relation: BaseRelation) -> None:
        self._raise_not_supported("drop relation")

    def truncate_relation(self, relation: BaseRelation) -> None:
        self._raise_not_supported("truncate relation")

    def rename_relation(self, from_relation: BaseRelation, to_relation: BaseRelation) -> None:
        self._raise_not_supported("rename relation")

    def alter_column_type(self, relation, column_name, new_column_type) -> None:
        self._raise_not_supported("alter column type")

    def expand_column_types(self, goal, current) -> None:
        self._raise_not_supported("expand column types")

    def list_schemas(self, database: str) -> List[str]:
        handle = self._get_handle()
        return handle.get_all_schemas()

    def check_schema_exists(self, database: str, schema: str) -> bool:
        return schema in self.list_schemas(database)

    def list_relations_without_caching(self, schema_relation: BaseRelation) -> List[BaseRelation]:
        handle = self._get_handle()
        schema = schema_relation.schema or self.config.credentials.schema
        database = schema_relation.database or self.config.credentials.database
        tables = handle.get_all_tables(schema)
        relations: List[BaseRelation] = []
        for name in tables:
            relations.append(
                self.Relation.create(
                    database=database,
                    schema=schema,
                    identifier=name,
                    type=RelationType.Table,
                )
            )
        return relations

    def get_relation(self, database: str, schema: str, identifier: str) -> Optional[BaseRelation]:
        if not self.Relation.get_default_include_policy().database:
            database = None  # type: ignore
        return super().get_relation(database, schema, identifier)

    def get_columns_in_relation(self, relation: BaseRelation) -> List[KylinColumn]:
        handle = self._get_handle()
        schema = relation.schema or self.config.credentials.schema
        identifier = relation.identifier
        if identifier is None:
            return []

        try:
            table = handle.get_table_source(identifier, schema)
        except Exception as exc:
            if NoSuchTableError is not None and isinstance(exc, NoSuchTableError):
                return []
            raise

        table_comment = _extract_comment(getattr(table, "table_desc", None))
        columns: List[KylinColumn] = []
        for idx, col in enumerate(table.columns):
            raw_type = col.datatype
            dtype, char_size, numeric_precision, numeric_scale = KylinColumn.normalize_type(raw_type)
            column_comment = _extract_comment(getattr(col, "description", None))
            columns.append(
                KylinColumn(
                    table_database=relation.database,
                    table_schema=schema,
                    table_name=identifier,
                    table_type=str(relation.type) if relation.type else None,
                    column_index=idx,
                    column=col.name,
                    dtype=dtype,
                    char_size=char_size,
                    numeric_precision=numeric_precision,
                    numeric_scale=numeric_scale,
                    table_comment=table_comment,
                    column_comment=column_comment,
                )
            )
        return columns

    def get_catalog(
        self,
        relation_configs: Iterable[RelationConfig],
        used_schemas: FrozenSet[Tuple[str, str]],
    ):
        rows: List[List[Any]] = []
        schema_pairs = sorted({pair for pair in used_schemas if pair[1]})
        default_database = self.config.credentials.database

        for database, schema in schema_pairs:
            database = database or default_database
            relations = self.list_relations(database, schema)
            for relation in relations:
                for column in self.get_columns_in_relation(relation):
                    rows.append(
                        [
                            relation.database,
                            relation.schema,
                            relation.identifier,
                            str(relation.type) if relation.type else None,
                            column.table_comment,
                            None,
                            column.name,
                            column.column_index,
                            column.data_type,
                            column.column_comment,
                        ]
                    )

        text_only_columns = [
            name for name in self.CATALOG_COLUMN_NAMES if name != "column_index"
        ]
        table = table_from_rows(
            rows=rows, column_names=self.CATALOG_COLUMN_NAMES, text_only_columns=text_only_columns
        )
        return table, []

    def debug_query(self) -> None:
        self.execute("select 1 as id")
