# Packaging

This project uses `hatchling` for builds.

## Build sdist and wheel

```bash
cd dbt-kylin
python -m pip install --upgrade hatch
python -m hatch build
```

Artifacts will be created under `dbt-kylin/dist/`.

## Quick local install

```bash
python -m pip install dist/dbt_kylin-<version>-py3-none-any.whl
```
