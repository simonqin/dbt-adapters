from dbt.adapters.kylin.connections import KylinConnectionManager  # noqa
from dbt.adapters.kylin.connections import KylinCredentials
from dbt.adapters.kylin.relation import KylinRelation  # noqa
from dbt.adapters.kylin.column import KylinColumn  # noqa
from dbt.adapters.kylin.impl import KylinAdapter

from dbt.adapters.base import AdapterPlugin
from dbt.include import kylin

Plugin = AdapterPlugin(
    adapter=KylinAdapter,  # type:ignore
    credentials=KylinCredentials,
    include_path=kylin.PACKAGE_PATH,
)
