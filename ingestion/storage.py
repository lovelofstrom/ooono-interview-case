import json
import os
from datetime import datetime
from pathlib import Path

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "lake" / "raw" / "codriver"


def latest_received_at(endpoint: str) -> str | None:
    """Latest received_at already stored for an event endpoint (drives, warnings), or None before the first run.

    Only the newest file is read: each run fetches records received after the previous
    run's latest, so the newest file always holds the latest received_at.
    """
    files = sorted((RAW_DIR / endpoint).glob("*.jsonl"))
    if not files:
        return None
    lines = files[-1].read_text().splitlines()
    latest = max(
        datetime.fromisoformat(json.loads(line)["received_at"]) for line in lines
    )
    return latest.strftime("%Y-%m-%dT%H:%M:%SZ")


def write(endpoint: str, rows: list[dict], run_at: datetime) -> Path:
    """Store rows exactly as received in data/lake/raw/codriver/<endpoint>/<run time>.jsonl."""
    folder = RAW_DIR / endpoint
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / f"{run_at:%Y-%m-%dT%H%M%SZ}.jsonl"
    tmp = target.with_suffix(".jsonl.tmp")
    tmp.write_text("".join(json.dumps(row) + "\n" for row in rows))
    os.replace(tmp, target)
    return target
