# OpenDataPhilly Database Backups

This repository contains automated scripts and workflows for downloading and backing up data from [OpenDataPhilly](https://opendataphilly.org/), Philadelphia's open data portal.

## Overview

OpenDataPhilly provides access to hundreds of datasets from the City of Philadelphia, covering topics like property data, business licenses, real estate transactions, and more. This repository provides a flexible CLI tool for downloading any dataset from OpenDataPhilly and creating database backups.

## What This Repository Does

### Data Collection
The repository downloads and processes any dataset from OpenDataPhilly, here are some examples:

- **OPA Properties Public**: Property assessment data split by zip code
- **Business Licenses**: Rental business licenses filtered by license type and issue date
- **RTT Summary**: Real estate transfer tax data for deeds and related documents

## CLI Commands

The `download_opa_data.py` script provides several commands for downloading data from OpenDataPhilly:

### `by-col` Command
Downloads data split by a specific column value (e.g., zip codes, categories).

```bash
poetry run python download_opa_data.py by-col \
  --table opa_properties_public \
  --csv-split-col zip_code \
  --where-str "market_value > 100000" \
  --skip-save-to-csv \
  --save-to-sqlite
```

**Options:**
- `--table`: Required. The OpenDataPhilly table name
- `--csv-split-col`: Required. Column to split data by (e.g., zip_code, category)
- `--where-str`: Optional. SQL WHERE clause to filter data
- `--save-to-csv/--skip-save-to-csv`: Whether to save CSV files (default: save)
- `--save-to-sqlite/--skip-save-to-sqlite`: Whether to save to SQLite DB (default: save)
- `--db-filepath`: SQLite database file path (default: open_data_philly.db)
- `--debug-mode/--do-not-debug`: Enable debug output (default: disabled)

### `by-datetime` Command
Downloads data split by date/time columns (currently supports year granularity).

```bash
poetry run python download_opa_data.py by-datetime \
  --table business_licenses \
  --split-by initialissuedate year \
  --where-str "licensetype = 'Rental'" \
  --skip-save-to-csv \
  --save-to-sqlite
```

**Options:**
- `--table`: Required. The OpenDataPhilly table name
- `--split-by`: Required. Column and granularity (e.g., "initialissuedate year")
- `--where-str`: Optional. SQL WHERE clause to filter data
- `--save-to-csv/--skip-save-to-csv`: Whether to save CSV files (default: save)
- `--save-to-sqlite/--skip-save-to-sqlite`: Whether to save to SQLite DB (default: save)
- `--db-filepath`: SQLite database file path (default: open_data_philly.db)
- `--debug-mode/--do-not-debug`: Enable debug output (default: disabled)

### `json-file-per-row` Command
Creates individual JSON files for each row in a table (limited to 10 rows for testing).

```bash
poetry run python download_opa_data.py json-file-per-row \
  --table opa_properties_public \
  --column objectid
```

### `download-car-ped-stops-relation-to-hin` Command
Specialized command for downloading car/pedestrian stops data with High Injury Network (HIN) analysis.

```bash
poetry run python download_opa_data.py download-car-ped-stops-relation-to-hin \
  --dist-from-hin-threshold 0.0001
```

## Data Sources

All data is sourced from [OpenDataPhilly](https://opendataphilly.org/), which provides:
- Open access to Philadelphia government data
- Regular updates from various city departments
- APIs and bulk downloads for programmatic access
- Documentation and metadata for each dataset

## Usage

### Prerequisites
- Python 3.10.4
- Poetry for dependency management

### Local Development
```bash
# Install dependencies
poetry install

# Example: Download property data by zip code
poetry run python download_opa_data.py by-col \
  --table opa_properties_public \
  --csv-split-col zip_code \
  --skip-save-to-csv

# Example: Download business licenses by year
poetry run python download_opa_data.py by-datetime \
  --table business_licenses \
  --split-by initialissuedate year \
  --where-str "licensetype = 'Rental'" \
  --skip-save-to-csv

# Example: Download RTT summary data by year with filtering
poetry run python download_opa_data.py by-datetime \
  --table rtt_summary \
  --split-by recording_date year \
  --where-str "document_type IN ('DEED', 'DEED_SHERIFF', 'DEED OF CONDEMNATION', 'DEED LAND BANK')" \
  --skip-save-to-csv
```

### Output Options
- **CSV Files**: Split by the specified column or time period
- **SQLite Database**: Single database file with all downloaded data
- **JSON Files**: Individual files per row (for testing)

## Contributing

This repository is designed for automated data collection and backup. If you need to modify the data collection process or add new datasets, please:

1. Fork the repository
2. Test your changes locally
3. Submit a pull request with a clear description of the changes

## License

This project is open source. Please ensure compliance with OpenDataPhilly's terms of service when using the collected data.

## Acknowledgments

- [OpenDataPhilly](https://opendataphilly.org/) for providing access to Philadelphia's open data
- The City of Philadelphia for making this data publicly available
- The open data community for supporting transparency and accessibility

## Links

- [OpenDataPhilly Portal](https://opendataphilly.org/)
- [Philadelphia Open Data Policy](https://www.phila.gov/departments/office-of-open-data-and-digital-transformation/)
