import importlib.util
import sys
import types
import unittest
from dataclasses import dataclass
from pathlib import Path


def _load_connections_module() -> types.ModuleType:
    module_name = "dbt.adapters.kylin.connections"
    module_path = (
        Path(__file__).resolve().parents[3]
        / "dbt-kylin"
        / "src"
        / "dbt"
        / "adapters"
        / "kylin"
        / "connections.py"
    )

    stubs: dict[str, types.ModuleType] = {}

    def add_stub(name: str) -> types.ModuleType:
        stub = types.ModuleType(name)
        stubs[name] = stub
        return stub

    add_stub("dbt")
    add_stub("dbt.adapters")
    add_stub("dbt.adapters.kylin")
    add_stub("dbt.adapters.contracts")
    add_stub("dbt.adapters.events")
    add_stub("dbt_common")

    connection_stub = add_stub("dbt.adapters.contracts.connection")

    @dataclass
    class Credentials:
        database: str
        schema: str

    class AdapterResponse:
        pass

    class Connection:
        pass

    connection_stub.AdapterResponse = AdapterResponse
    connection_stub.Connection = Connection
    connection_stub.Credentials = Credentials

    logging_stub = add_stub("dbt.adapters.events.logging")

    class AdapterLogger:
        def __init__(self, name: str) -> None:
            self.name = name

        def debug(self, *args, **kwargs) -> None:
            return None

    logging_stub.AdapterLogger = AdapterLogger

    sql_stub = add_stub("dbt.adapters.sql")

    class SQLConnectionManager:
        pass

    sql_stub.SQLConnectionManager = SQLConnectionManager

    exceptions_stub = add_stub("dbt_common.exceptions")

    class DbtDatabaseError(Exception):
        pass

    class DbtRuntimeError(Exception):
        pass

    exceptions_stub.DbtDatabaseError = DbtDatabaseError
    exceptions_stub.DbtRuntimeError = DbtRuntimeError

    original_modules = {}
    for name, stub in stubs.items():
        original_modules[name] = sys.modules.get(name)
        sys.modules[name] = stub

    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise AssertionError("Unable to load Kylin connections module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)
    finally:
        for name, original in original_modules.items():
            if original is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = original
    return module


class KylinCredentialsImportTest(unittest.TestCase):
    def test_kylin_credentials_imports(self) -> None:
        module = _load_connections_module()
        self.assertTrue(hasattr(module, "KylinCredentials"))
