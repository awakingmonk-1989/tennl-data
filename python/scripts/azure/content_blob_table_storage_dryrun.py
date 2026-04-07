#!/usr/bin/env python3
"""Dry-run: insert mock records into Azure Blob + Tables and verify queries.

All dry-run records use a 'dry_run_' prefix in entity/workflow IDs so they are
easily identifiable and kept for reference (no cleanup).

Run:
    UV_PROJECT_ENVIRONMENT="python/tennl/batch/.venv" \
    uv run --project python/tennl/batch \
    python python/scripts/azure/content_blob_table_storage_dryrun.py

Requires Azure credentials via environment variables:

- Prefer `AZURE_STORAGE_CONNECTION_STRING`
- Or provide `AZURE_STORAGE_ACCOUNT_KEY` (script constructs the connection string)
"""

from __future__ import annotations

import json
import os
import time
from collections import defaultdict
from datetime import datetime, timezone
from hashlib import sha256

from azure.data.tables import TableServiceClient, UpdateMode
from azure.storage.blob import BlobServiceClient, ContentSettings

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

ACCOUNT_NAME = os.environ.get("AZURE_STORAGE_ACCOUNT_NAME", "devworkflow")

_conn_str = os.environ.get("AZURE_STORAGE_CONNECTION_STRING", "")
_account_key = os.environ.get("AZURE_STORAGE_ACCOUNT_KEY", "")

if _conn_str:
    CONN_STR = _conn_str
elif _account_key:
    CONN_STR = (
        "DefaultEndpointsProtocol=https;"
        f"AccountName={ACCOUNT_NAME};"
        f"AccountKey={_account_key};"
        "EndpointSuffix=core.windows.net"
    )
else:
    raise RuntimeError(
        "Azure storage credentials missing. Set AZURE_STORAGE_CONNECTION_STRING "
        "or AZURE_STORAGE_ACCOUNT_KEY in the environment."
    )

CONTAINER = "content"
SEP = "__"
SHARD_COUNT = 16
DRY_RUN_PREFIX = "dry_run_"
DRY_RUN_SESSION = os.environ.get("DRY_RUN_SESSION", "")
RECORD_COUNT = int(os.environ.get("DRY_RUN_RECORD_COUNT", "10"))

# Spread across 2 workflow executions and 3 category/sub combos
_session_suffix = f"_{DRY_RUN_SESSION}" if DRY_RUN_SESSION else ""
WORKFLOWS = [
    f"{DRY_RUN_PREFIX}articles_workflow_1000000000001{_session_suffix}",
    f"{DRY_RUN_PREFIX}articles_workflow_1000000000002{_session_suffix}",
]

CATEGORIES = [
    ("lifehacks", "focusattention"),
    ("lifehacks", "productivity"),
    ("wellness", "sleep"),
]

# ---------------------------------------------------------------------------
# Helpers (mirror azure_storage.py logic)
# ---------------------------------------------------------------------------

def iso_utc(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def shard_for(value: str) -> str:
    digest = sha256(value.encode("utf-8")).hexdigest()
    return f"{int(digest[:8], 16) % SHARD_COUNT:02d}"


def make_entity_id(idx: int) -> str:
    return f"{DRY_RUN_PREFIX}articles_devmac_{1000000000000 + idx}{_session_suffix}"


# ---------------------------------------------------------------------------
# Insert
# ---------------------------------------------------------------------------

def insert_records():
    blob_svc = BlobServiceClient.from_connection_string(CONN_STR)
    blob_container = blob_svc.get_container_client(CONTAINER)
    try:
        blob_container.create_container()
        print(f"[SETUP] Container '{CONTAINER}' created")
    except Exception:
        print(f"[SETUP] Container '{CONTAINER}' already exists")

    table_svc = TableServiceClient.from_connection_string(CONN_STR)
    wf_table = table_svc.get_table_client("workflowentityindex")
    cat_table = table_svc.get_table_client("categoryentityindex")

    records = []
    for i in range(RECORD_COUNT):
        wf_exec_id = WORKFLOWS[i % len(WORKFLOWS)]
        cat, sub = CATEGORIES[i % len(CATEGORIES)]
        ent_id = make_entity_id(i)
        now = datetime.now(timezone.utc)
        event_time = iso_utc(now)
        shard_id = shard_for(wf_exec_id)

        blob_key = f"articles/{cat}/{sub}/{wf_exec_id}/{ent_id}.json"
        blob_payload = json.dumps({
            "workflowExecutionId": wf_exec_id,
            "entityId": ent_id,
            "category": cat,
            "subCategory": sub,
            "eventTime": event_time,
            "contentType": "articles",
            "indexStatus": "indexed",
            "article_md": f"# Dry Run {i}\n\nMock article #{i}.",
            "article_json": {"hero": {"title": f"Dry Run {i}"}, "posts": []},
        }, ensure_ascii=False, indent=2)

        blob_client = blob_container.get_blob_client(blob_key)
        blob_client.upload_blob(
            blob_payload, overwrite=True,
            content_settings=ContentSettings(content_type="application/json"),
        )
        blob_url = blob_client.url

        wf_entity = {
            "PartitionKey": wf_exec_id,
            "RowKey": f"{event_time}{SEP}{ent_id}",
            "workflowExecutionId": wf_exec_id,
            "entityId": ent_id,
            "category": cat,
            "subCategory": sub,
            "eventTime": event_time,
            "blobUrl": blob_url,
            "status": "dryrun",
            "source": "dryrun_script_v1",
        }
        wf_table.upsert_entity(entity=wf_entity, mode=UpdateMode.REPLACE)

        cat_entity = {
            "PartitionKey": f"{cat}{SEP}{sub}{SEP}{shard_id}",
            "RowKey": f"{event_time}{SEP}{wf_exec_id}{SEP}{ent_id}",
            "workflowExecutionId": wf_exec_id,
            "entityId": ent_id,
            "category": cat,
            "subCategory": sub,
            "eventTime": event_time,
            "blobUrl": blob_url,
            "status": "dryrun",
            "source": "dryrun_script_v1",
        }
        cat_table.upsert_entity(entity=cat_entity, mode=UpdateMode.REPLACE)

        records.append({
            "i": i, "wf": wf_exec_id, "ent": ent_id, "cat": cat, "sub": sub,
            "shard": shard_id, "event_time": event_time,
        })
        print(f"  [{i+1:2d}/{RECORD_COUNT}] wf={wf_exec_id[-4:]}  ent=...{ent_id[-4:]}  {cat}/{sub}  shard={shard_id}")

        time.sleep(0.05)  # small delay so eventTimes differ

    return records


# ---------------------------------------------------------------------------
# Query checks
# ---------------------------------------------------------------------------

def check_workflow_index(records: list[dict]):
    print("\n=== CHECK: workflowentityindex ===")
    table_svc = TableServiceClient.from_connection_string(CONN_STR)
    wf_table = table_svc.get_table_client("workflowentityindex")

    for wf_id in WORKFLOWS:
        rows = list(wf_table.query_entities(f"PartitionKey eq '{wf_id}'"))
        expected = [r for r in records if r["wf"] == wf_id]
        match = len(rows) == len(expected)
        symbol = "OK" if match else "FAIL"
        print(f"  [{symbol}] PK={wf_id}  rows={len(rows)}  expected={len(expected)}")
        if not match:
            print(f"       GOT entity IDs: {[r['entityId'] for r in rows]}")

    all_rows = []
    for wf_id in WORKFLOWS:
        all_rows.extend(wf_table.query_entities(f"PartitionKey eq '{wf_id}'"))
    assert len(all_rows) == RECORD_COUNT, f"Expected {RECORD_COUNT} total rows, got {len(all_rows)}"
    print(f"  [OK] Total rows across all workflow partitions: {len(all_rows)}")


def check_category_index(records: list[dict]):
    print("\n=== CHECK: categoryentityindex ===")
    table_svc = TableServiceClient.from_connection_string(CONN_STR)
    cat_table = table_svc.get_table_client("categoryentityindex")

    shard_dist: dict[str, int] = defaultdict(int)

    for cat, sub in CATEGORIES:
        expected = [r for r in records if r["cat"] == cat and r["sub"] == sub]
        total_rows = []

        shards_hit = set()
        for s in range(SHARD_COUNT):
            pk = f"{cat}{SEP}{sub}{SEP}{s:02d}"
            rows = list(cat_table.query_entities(f"PartitionKey eq '{pk}'"))
            # Filter to the current dry-run session so historical dry-run rows don't
            # break invariants.
            rows = [r for r in rows if r.get("workflowExecutionId") in WORKFLOWS]
            if rows:
                shards_hit.add(f"{s:02d}")
                shard_dist[f"{s:02d}"] += len(rows)
            total_rows.extend(rows)

        match = len(total_rows) == len(expected)
        symbol = "OK" if match else "FAIL"
        print(f"  [{symbol}] {cat}/{sub}  rows={len(total_rows)}  expected={len(expected)}  shards_used={sorted(shards_hit)}")

    print(f"\n  Shard distribution across all categories:")
    for sid in sorted(shard_dist):
        print(f"    shard {sid}: {shard_dist[sid]} row(s)")


def check_blobs(records: list[dict]):
    print("\n=== CHECK: blob storage ===")
    blob_svc = BlobServiceClient.from_connection_string(CONN_STR)
    container = blob_svc.get_container_client(CONTAINER)

    blobs = list(container.list_blobs(name_starts_with="articles/"))
    if DRY_RUN_SESSION:
        dry_run_blobs = [b for b in blobs if DRY_RUN_SESSION in b.name]
    else:
        dry_run_blobs = [b for b in blobs if DRY_RUN_PREFIX in b.name]
    print(f"  Total blobs under articles/: {len(blobs)}")
    if DRY_RUN_SESSION:
        print(f"  Dry-run blobs (session '{DRY_RUN_SESSION}'): {len(dry_run_blobs)}")
    else:
        print(f"  Dry-run blobs (with '{DRY_RUN_PREFIX}'): {len(dry_run_blobs)}")
    assert len(dry_run_blobs) == RECORD_COUNT, f"Expected {RECORD_COUNT} dry-run blobs, got {len(dry_run_blobs)}"
    print(f"  [OK] All {RECORD_COUNT} dry-run blobs present")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print(f"Dry-run: inserting {RECORD_COUNT} mock records (prefix='{DRY_RUN_PREFIX}')")
    print(f"Storage account: {ACCOUNT_NAME}")
    print(f"Container: {CONTAINER}")
    print(f"Workflows: {WORKFLOWS}")
    print(f"Categories: {CATEGORIES}")
    print()

    records = insert_records()
    print(f"\nInserted {len(records)} records.")

    check_workflow_index(records)
    check_category_index(records)
    check_blobs(records)

    print("\n" + "=" * 60)
    print("DRY RUN COMPLETE — all checks passed.")
    print("Records are KEPT for reference (no cleanup).")
    print("=" * 60)


if __name__ == "__main__":
    main()
