# OpenDataPhilly Database Backups

This repository creates a monthly SQLite backup of selected
[OpenDataPhilly](https://opendataphilly.org/) datasets and publishes it as a
dated GitHub release.

The generic downloading code lives in
[whoownsphilly/open-data-philly-downloader](https://github.com/whoownsphilly/open-data-philly-downloader).
This repository contains only the backup configuration and release workflow.

## Included datasets

- `opa_properties_public`, split by ZIP code
- rental records from `business_licenses`, split by year
- `violations` since 2020, split by year
- deed records from `rtt_summary`, split by year

The workflow pins the downloader to an exact Git commit for reproducible runs.
It writes into `open_data_philly.next.db`, creates useful indexes, verifies the
database with SQLite's integrity checker, and only then publishes it as
`open_data_philly.db`.

## Run locally

Install the pinned downloader dependency:

```bash
uv sync
```

Then run any of the commands used in `.github/workflows/main.yml`, for example:

```bash
uv run odp-download table \
  --table shootings \
  --db-filepath open_data_philly.db
```

The shared downloader supports whole-table downloads, column and date splits,
pagination, retries, optional CSV output, SQLite indexes, and Carto SQL filters.
Run `uv run odp-download --help` for the complete command list.
