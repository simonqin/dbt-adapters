from dataclasses import dataclass
import re
from typing import Any, Optional, Tuple, TypeVar

from dbt.adapters.base.column import Column
from dbt_common.dataclass_schema import dbtClassMixin

Self = TypeVar("Self", bound="KylinColumn")

_TYPE_MAP = {
    "CHAR": "string",
    "VARCHAR": "string",
    "STRING": "string",
    "DECIMAL": "decimal",
    "DOUBLE": "double",
    "FLOAT": "float",
    "BIGINT": "bigint",
    "LONG": "bigint",
    "LONG8": "bigint",
    "INTEGER": "int",
    "INT": "int",
    "INT4": "bigint",
    "TINYINT": "smallint",
    "SMALLINT": "smallint",
    "BOOLEAN": "boolean",
    "DATE": "date",
    "DATETIME": "timestamp",
    "TIMESTAMP": "timestamp",
}


@dataclass
class KylinColumn(dbtClassMixin, Column):
    table_database: Optional[str] = None
    table_schema: Optional[str] = None
    table_name: Optional[str] = None
    table_type: Optional[str] = None
    column_index: Optional[int] = None
    table_comment: Optional[str] = None
    column_comment: Optional[str] = None

    @classmethod
    def translate_type(cls, dtype: str) -> str:
        normalized, _, _, _ = cls.normalize_type(dtype)
        return normalized

    def can_expand_to(self, other_column: Column) -> bool:
        return self.is_string() and other_column.is_string()

    def literal(self, value: Any) -> str:
        return "cast({} as {})".format(value, self.dtype)

    def is_string(self) -> bool:
        return self.dtype.lower() in {"string", "varchar", "char", "text"}

    @property
    def quoted(self) -> str:
        return '"{}"'.format(self.column)

    @property
    def data_type(self) -> str:
        return self.dtype

    @classmethod
    def string_type(cls, size: int) -> str:
        return "string"

    def __repr__(self) -> str:
        return "<KylinColumn {} ({})>".format(self.name, self.data_type)

    @classmethod
    def normalize_type(
        cls, raw_type: Optional[str]
    ) -> Tuple[str, Optional[int], Optional[int], Optional[int]]:
        if not raw_type:
            return "string", None, None, None

        raw = raw_type.strip()
        depth = 0
        cut = None
        for idx, char in enumerate(raw):
            if char == "(":
                depth += 1
            elif char == ")":
                depth = max(0, depth - 1)
            elif char.isspace() and depth == 0:
                cut = idx
                break
        if cut is not None:
            raw = raw[:cut]

        match = re.match(r"^([^(]+)(?:\\(([^)]+)\\))?$", raw)
        if not match:
            return raw.lower(), None, None, None

        base = match.group(1).strip()
        params = match.group(2)
        base_upper = base.upper()
        normalized = _TYPE_MAP.get(base_upper, base.lower())

        char_size = None
        numeric_precision = None
        numeric_scale = None
        if params:
            parts = [p.strip() for p in params.split(",") if p.strip()]
            if normalized == "decimal":
                if len(parts) >= 1 and parts[0].isdigit():
                    numeric_precision = int(parts[0])
                if len(parts) >= 2 and parts[1].isdigit():
                    numeric_scale = int(parts[1])
            elif normalized == "string":
                if parts[0].isdigit():
                    char_size = int(parts[0])

        return normalized, char_size, numeric_precision, numeric_scale
