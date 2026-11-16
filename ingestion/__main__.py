"""Fetch new Co-Driver data from the API and store it in the raw zone of the lake.

Usage: python -m ingestion
"""

import logging
import os
from datetime import UTC, datetime
from pathlib import Path

from dotenv import load_dotenv

from ingestion import storage
from ingestion.api import ApiClient

EVENTS = {"drives": "/v1/drives", "warnings": "/v1/warnings"}
SNAPSHOTS = {"users": "/v1/users"}


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
    client = ApiClient(
        os.environ["API_BASE_URL"],
        os.environ["API_CLIENT_ID"],
        os.environ["API_CLIENT_SECRET"],
    )
    run_at = datetime.now(UTC)

    for name, path in EVENTS.items():
        since = storage.latest_received_at(name)
        params = {"received_since": since} if since else {}
        ingest(client, name, path, params, run_at)

    for name, path in SNAPSHOTS.items():
        ingest(client, name, path, {}, run_at)


def ingest(
    client: ApiClient, name: str, path: str, params: dict, run_at: datetime
) -> None:
    """Fetch one endpoint and store the result, logging what happened."""
    rows = client.fetch_all(path, params)
    if not rows:
        logging.info("%s: no new rows", name)
        return
    file = storage.write(name, rows, run_at)
    logging.info("%s: %d rows -> %s", name, len(rows), file)


if __name__ == "__main__":
    main()
