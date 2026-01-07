# dbt-kylin

Apache Kylin adapter for dbt. This adapter is **read-only** and uses the Kylin HTTP API via `kylinpy`.

## Supported features

- Query execution (read-only)
- `dbt compile`
- `dbt test` (query-based tests)

Not supported:

- DDL or write operations (table/view/incremental/snapshot/seed)
- Schema changes

## Installation

```bash
pip install dbt-kylin
```

See `dbt-kylin/INSTALL.md` for more install options and `dbt-kylin/PACKAGING.md` for build steps.

## Profiles

```yaml
kylin:
  target: dev
  outputs:
    dev:
      type: kylin
      host: <kylin-host>
      port: 7070
      user: <username>
      password: <password>
      project: <kylin-project>
      schema: <default-schema> # default: DEFAULT
      # optional
      timeout: 30
      is_debug: false
      is_pushdown: false
      unverified: true
```

Notes:

- `project` maps to Kylin project (dbt `database`).
- `schema` defaults to `DEFAULT` and can be overridden per model/source.
- Kylin API version is fixed to `v4`.
- `is_ssl` and `prefix` are fixed to `false` and `/kylin/api`.
