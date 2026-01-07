from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, Tuple

from dbt.adapters.contracts.connection import AdapterResponse, Connection, Credentials
from dbt.adapters.events.logging import AdapterLogger
from dbt.adapters.sql import SQLConnectionManager
from dbt_common.exceptions import DbtDatabaseError, DbtRuntimeError

logger = AdapterLogger("Kylin")

try:
    from kylinpy.kylindb import Connection as KylinDBConnection
    from kylinpy.client import HTTPError
except ImportError:
    KylinDBConnection = None
    HTTPError = None


def _coerce_bool(value: Any, *, default: bool) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"1", "true", "t", "yes", "y"}:
            return True
        if normalized in {"0", "false", "f", "no", "n", ""}:
            return False
    return bool(value)


@dataclass
class KylinCredentials(Credentials):
    host: str
    user: str
    password: str
    database: str
    schema: str = "DEFAULT"
    port: int = 7070
    timeout: int = 30
    is_pushdown: bool = False
    is_debug: bool = False
    unverified: bool = True
    connect_retries: int = 0

    # fixed settings
    is_ssl: bool = False
    prefix: str = "/kylin/api"
    version: str = "v4"

    _ALIASES = {"project": "database"}

    @property
    def type(self) -> str:
        return "kylin"

    @property
    def unique_field(self) -> str:
        return self.host

    def __post_init__(self) -> None:
        if KylinDBConnection is None:
            raise DbtRuntimeError(
                "kylinpy is required. Install with `pip install dbt-kylin`."
            )
        if not self.host:
            raise DbtRuntimeError("Must specify `host` in profile")
        if not self.database:
            raise DbtRuntimeError("Must specify `project` in profile")
        if not self.schema:
            raise DbtRuntimeError("Must specify `schema` in profile")
        if not self.user:
            raise DbtRuntimeError("Must specify `user` in profile")
        if not self.password:
            raise DbtRuntimeError("Must specify `password` in profile")

        self.is_ssl = False
        self.prefix = "/kylin/api"
        self.version = "v4"

        self.is_pushdown = _coerce_bool(self.is_pushdown, default=False)
        self.is_debug = _coerce_bool(self.is_debug, default=False)
        self.unverified = _coerce_bool(self.unverified, default=True)

    def _connection_keys(self) -> Tuple[str, ...]:
        return (
            "host",
            "port",
            "user",
            "database",
            "schema",
            "timeout",
            "is_pushdown",
            "is_debug",
            "unverified",
        )


class KylinConnectionManager(SQLConnectionManager):
    TYPE = "kylin"

    @contextmanager
    def exception_handler(self, sql):
        try:
            yield
        except Exception as e:
            if HTTPError is not None and isinstance(e, HTTPError):
                logger.debug("Kylin error: {}".format(str(e)))
                self.rollback_if_open()
                raise DbtDatabaseError(str(e).strip()) from e
            logger.debug("Error running SQL: {}".format(sql))
            self.rollback_if_open()
            raise DbtRuntimeError(e) from e

    @classmethod
    def open(cls, connection: Connection) -> Connection:
        if connection.state == "open":
            logger.debug("Connection is already open, skipping open.")
            return connection

        if KylinDBConnection is None:
            raise DbtRuntimeError(
                "kylinpy is required. Install with `pip install dbt-kylin`."
            )

        credentials = cls.get_credentials(connection.credentials)

        def connect() -> Any:
            return KylinDBConnection.connect(
                host=credentials.host,
                port=credentials.port,
                username=credentials.user,
                password=credentials.password,
                project=credentials.database,
                is_ssl=credentials.is_ssl,
                prefix=credentials.prefix,
                timeout=credentials.timeout,
                version=credentials.version,
                is_pushdown=credentials.is_pushdown,
                is_debug=credentials.is_debug,
                unverified=credentials.unverified,
            )

        return cls.retry_connection(
            connection=connection,
            connect=connect,
            logger=logger,
            retry_limit=credentials.connect_retries,
            retry_timeout=1,
            retryable_exceptions=(HTTPError,) if HTTPError is not None else tuple(),
        )

    def cancel(self, connection: Connection) -> None:
        logger.debug("Cancel is not supported for Kylin connections.")

    @classmethod
    def get_credentials(cls, credentials: Credentials) -> Credentials:
        return credentials

    @classmethod
    def get_response(cls, cursor: Any) -> AdapterResponse:
        code = "SUCCESS"
        if cursor is None:
            return AdapterResponse(_message=code, code=code, rows_affected=0)
        rows = cursor.rowcount
        return AdapterResponse(_message="{} {}".format(code, rows), code=code, rows_affected=rows)
