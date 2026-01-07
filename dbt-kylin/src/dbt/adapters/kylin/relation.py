from dataclasses import dataclass, field
from typing import TypeVar

from dbt.adapters.base.relation import BaseRelation, Policy

Self = TypeVar("Self", bound="BaseRelation")


@dataclass
class KylinQuotePolicy(Policy):
    database: bool = False
    schema: bool = False
    identifier: bool = False


@dataclass
class KylinIncludePolicy(Policy):
    database: bool = False
    schema: bool = True
    identifier: bool = True


@dataclass(frozen=True, eq=False, repr=False)
class KylinRelation(BaseRelation):
    quote_policy: Policy = field(default_factory=lambda: KylinQuotePolicy())
    include_policy: Policy = field(default_factory=lambda: KylinIncludePolicy())
    quote_character: str = '"'
