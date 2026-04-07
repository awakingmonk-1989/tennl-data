#!/usr/bin/env python3
"""Verify a novelty batch run:

- Local batch directory artifacts (.md + .json for each run_id)
- PostgreSQL rows exist for those run_ids
- Azure storage has fresh blob + table index entries created after the batch start time

This intentionally does NOT require per-run Azure IDs; it verifies counts via
time-window queries and naming conventions.

Env:
  - CONTENT_GEN_PG_DSN (optional; defaults match pg_storage.py)
  - AZURE_STORAGE_CONNECTION_STRING (required for Azure verification)

Usage:
  UV_PROJECT_ENVIRONMENT="python/tennl/batch/.venv" uv run --project python/tennl/batch \
    python python/scripts/verify_novelty_batch_run_artifacts.py \
    --batch-dir specs/data/batch_YYYYMMDD_HHMMSS \
    --started-at-iso 2026-04-02T05:30:00Z
"""

from __future__ import annotations

import argparse
import os
import re
from datetime import datetime, timezone
from datetime import timedelta
from pathlib import Path


def _parse_iso(s: str) -> datetime:
    # Accept "Z" suffix.
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    dt = datetime.fromisoformat(s)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _run_ids_from_batch_dir(batch_dir: Path) -> list[str]:
    ids: set[str] = set()
    for p in batch_dir.glob("*.json"):
        ids.add(p.stem)
    return sorted(ids)


def verify_local(batch_dir: Path) -> list[str]:
    if not batch_dir.exists():
        raise SystemExit(f"ERROR: batch dir not found: {batch_dir}")
    run_ids = _run_ids_from_batch_dir(batch_dir)
    if not run_ids:
        raise SystemExit(f"ERROR: no .json artifacts found in {batch_dir}")

    missing = []
    for rid in run_ids:
        if not (batch_dir / f"{rid}.md").exists():
            missing.append(f"{rid}.md")
        if not (batch_dir / f"{rid}.json").exists():
            missing.append(f"{rid}.json")
    if missing:
        raise SystemExit(f"ERROR: missing artifacts: {missing[:10]}{' ...' if len(missing) > 10 else ''}")

    print(f"[OK] Local artifacts: {len(run_ids)} run_ids, {2*len(run_ids)} files present")
    return run_ids


def verify_pg(run_ids: list[str]) -> None:
    import psycopg

    dsn = os.environ.get("CONTENT_GEN_PG_DSN", "postgresql://devansh@localhost:5432/content_gen")
    placeholders = ",".join(["%s"] * len(run_ids))
    q = f"SELECT run_id, status, reason FROM content_gen_article WHERE run_id IN ({placeholders})"

    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute(q, run_ids)
            rows = cur.fetchall()

    found = {r[0] for r in rows}
    missing = [rid for rid in run_ids if rid not in found]
    if missing:
        raise SystemExit(f"ERROR: PG missing {len(missing)} rows (example: {missing[:3]})")
    print(f"[OK] PostgreSQL: {len(rows)}/{len(run_ids)} rows present for batch run_ids")


def verify_azure(started_at: datetime, expected_min: int) -> None:
    conn_str = os.environ.get("AZURE_STORAGE_CONNECTION_STRING", "").strip()
    if not conn_str:
        raise SystemExit("ERROR: AZURE_STORAGE_CONNECTION_STRING not set (cannot verify Azure)")

    # Azure Table filters expect literal strings; we query by our own eventTime field (ISO-UTC).
    # Allow for clock skew between local machine and Azure timestamps.
    skew_s = int(os.environ.get("AZURE_CLOCK_SKEW_SECONDS", "900"))
    effective_start = started_at - timedelta(seconds=skew_s)

    started_at_iso = (
        started_at.astimezone(timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )
    effective_start_iso = (
        effective_start.astimezone(timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )

    from azure.data.tables import TableServiceClient
    from azure.storage.blob import BlobServiceClient

    table_svc = TableServiceClient.from_connection_string(conn_str)
    wf_table = table_svc.get_table_client("workflowentityindex")
    cat_table = table_svc.get_table_client("categoryentityindex")

    # We can’t query workflowentityindex efficiently without PartitionKey, so we only
    # assert presence via source+eventTime scan. For N=10 this is fine.
    wf_rows = list(
        wf_table.query_entities(
            f"eventTime ge '{effective_start_iso}' and source eq 'tennl_batch_workflow_v1'"
        )
    )
    cat_rows = list(
        cat_table.query_entities(
            f"eventTime ge '{effective_start_iso}' and source eq 'tennl_batch_workflow_v1'"
        )
    )

    if len(wf_rows) < expected_min:
        raise SystemExit(f"ERROR: workflowentityindex rows since start: got {len(wf_rows)} < {expected_min}")
    if len(cat_rows) < expected_min:
        raise SystemExit(f"ERROR: categoryentityindex rows since start: got {len(cat_rows)} < {expected_min}")

    print(f"[OK] Azure Tables: workflowentityindex rows since start={len(wf_rows)}; categoryentityindex={len(cat_rows)}")

    blob_svc = BlobServiceClient.from_connection_string(conn_str)
    container = blob_svc.get_container_client("content")
    blobs = list(container.list_blobs(name_starts_with="articles/"))
    # Narrow down by last_modified time (server-side filter isn't available).
    fresh = [b for b in blobs if b.last_modified and b.last_modified >= effective_start]
    # Most of our payloads use this workflow id prefix.
    # NOTE: Use `\d` (digit) — not `\\d` (literal backslash + d).
    fresh_articles = [b for b in fresh if re.search(r"/articles_workflow_\d+/", b.name)]

    if len(fresh_articles) < expected_min:
        raise SystemExit(f"ERROR: fresh article blobs since start: got {len(fresh_articles)} < {expected_min}")
    print(
        f"[OK] Azure Blobs: fresh article blobs since start={len(fresh_articles)} "
        f"(clock_skew_s={skew_s})"
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch-dir", required=True, help="Path to specs/data/batch_* directory")
    ap.add_argument("--started-at-iso", required=True, help="Batch start time ISO (e.g. 2026-04-02T05:30:00Z)")
    args = ap.parse_args()

    batch_dir = Path(args.batch_dir)
    started_at = _parse_iso(args.started_at_iso)

    run_ids = verify_local(batch_dir)
    verify_pg(run_ids)
    verify_azure(started_at, expected_min=len(run_ids))

    print("[OK] Batch verification complete")


if __name__ == "__main__":
    main()

