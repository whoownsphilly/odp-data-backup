# OpenDataPhilly Database Backups

This project creates a monthly SQLite backup of selected
[OpenDataPhilly](https://opendataphilly.org/) tables. It also includes a generic
CLI that can download any table exposed by Philadelphia's Carto SQL API.

## Why the downloader lives here

SQLite types are derived at runtime from Carto's field metadata. Rows are not
validated against hand-written Python models, so a harmless upstream change
such as an integer appearing in a text-affinity column cannot stop a backup.

The downloader also:

- retrieves large datasets in configurable pages;
- retries rate limits and transient server failures;
- supports arbitrary tables and optional SQL filters;
- supports whole-table, column-split, and date-split downloads;
- optionally writes CSV alongside SQLite;
- JSON-encodes nested values that SQLite cannot bind directly;
- can create indexes after loading finishes;
- validates identifiers used as table and column names.

## Install

Python 3.10.4 or newer and [uv](https://docs.astral.sh/uv/) are required.

```bash
uv sync --frozen
```

## Download any table

```bash
uv run --frozen odp-download table \
  --table shootings \
  --db-filepath open_data_philly.db \
  --index date_
```

Add a Carto SQL filter with `--where`:

```bash
uv run --frozen odp-download table \
  --table violations \
  --where "violationdate >= '2025-01-01'"
```

Use `--csv-path violations.csv` to produce CSV output as well. SQLite output is
always enabled because it is this project's primary artifact.

## Split large downloads

Splitting limits the amount of upstream data handled by any one query. Every
split is still paginated, so a split larger than Carto's response limit is not
truncated.

By a column's distinct values:

```bash
uv run --frozen odp-download by-col \
  --table opa_properties_public \
  --csv-split-col zip_code \
  --index zip_code
```

By year, month, or day:

```bash
uv run --frozen odp-download by-datetime \
  --table rtt_summary \
  --split-by recording_date year \
  --where "document_type IN ('DEED', 'DEED_SHERIFF')" \
  --index recording_date
```

Pass `--csv-dir csvs` to either split command to write one CSV per split. Use
`--page-size` to tune the default 25,000-row page size and `--endpoint` to use a
different compatible Carto SQL endpoint.

Run `uv run odp-download COMMAND --help` for all options.

## Automated backup

The GitHub Actions workflow downloads the configured tables into a temporary
database, creates indexes, runs SQLite's integrity check, and only then renames
the file and publishes a dated GitHub release. Dependencies are resolved from
the committed `uv.lock` file.

## Tests

```bash
uv run --extra test pytest
```
