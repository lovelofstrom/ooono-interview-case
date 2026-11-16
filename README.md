# OOONO AE Interview

## Setup

Install uv, e.g. `brew install uv` on macOS (see uv's docs for other systems).
Run `make setup`. It installs the dependencies and creates `.env` from
`.env.example`.
Add your API credentials to `API_CLIENT_ID` and `API_CLIENT_SECRET` in `.env`.

## Execution

Run `make all` to ingest and transform the data.

- The first run fetches all data and takes about 14 minutes. Later runs only
  fetch new data.
- The result is `data/warehouse.duckdb`, with the models in the schemas
  `dev_staging` and `dev_marts`.

### Assumptions

- **Data volume:** the data is small enough to rebuild all dbt models on every
  run. Ingestion is incremental, the models are not.
- **Time zones:** timestamps without a `Z` are the phone's local time, and
  weeks are based on it. The data covers two time zones an hour apart, so this
  only matters for drives around midnight between Sunday and Monday.
- **Duplicates:** the first received copy of a drive or warning is the right
  one. Duplicates in the data only differed in `received_at`.
- **Cut-outs:** a drive counts as cut out when the same user starts a new drive
  0–29 seconds after it ended.
- **Unauthenticated drives:** all drives without a logged-in user share the
  user ID `unauthenticated`, so they can't be linked to a driver. They're kept
  in `fct_drives` but left out of `agg_drives_weekly`.
- **Plans:** a user's current plan and price are applied to all their past
  drives.

### What was left out

- A dashboard. `fct_drives` and `agg_drives_weekly` are the tables one would sit
  on, and `fct_drives` also supports daily or hourly views without new models.
- A week-over-week report. Comparing the last two full weeks is left to the
  query on top of `agg_drives_weekly`. Which would need to include complete
  weeks since the model include the current week.
- Warnings in the marts. They're ingested and staged, but showed no link to
  cut-outs.
- Deployment, scheduling and CI/CD. Someone has to run the pipeline.
- Python tests and monitoring. Only the dbt models are tested.

### Where it would run at OOONO

The code is written to be run locally, so it would not work out of the box at
OOONO. `.env` would be replaced by AWS Secrets Manager. The JSON files would
be saved in S3 instead of on a local disk. The actual ingestion could be
done using Lambda.

I haven't used Snowflake, but in AWS the raw tables would be created using a
crawler.

The dbt models would be added to your dbt project would materialized on the
daily schedule after ingestion is complete.
