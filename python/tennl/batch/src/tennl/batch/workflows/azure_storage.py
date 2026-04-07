"""Azure Blob + Table persistence for content-gen workflow output.

Write order (per store strategy spec §7):
  1. Blob (source of truth)
  2. workflowentityindex table upsert
  3. categoryentityindex table upsert

If table writes fail the blob is still durable; reconciliation repairs indexes.
"""

from __future__ import annotations

import json
import logging
import re
import socket
import time
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any

from azure.data.tables import TableServiceClient, UpdateMode
from azure.storage.blob import BlobServiceClient

logger = logging.getLogger(__name__)

SEP = "__"
SHARD_COUNT = 16


# Azure Table key restrictions (PartitionKey/RowKey):
# - must not include '/', '\\', '#', '?', or control characters.
# We keep the blob path flexible, but table keys must be normalized.
_TABLE_KEY_DISALLOWED_RE = re.compile(r"[\/\\#\?\x00-\x1F\x7F]")


def _table_key_component(value: str) -> str:
    """Normalize category/sub_category into a safe Azure Table key component."""
    v = (value or "").strip().lower()
    # Remove known-disallowed characters first.
    v = _TABLE_KEY_DISALLOWED_RE.sub("", v)
    # Collapse whitespace to nothing (match prior behavior) and drop separators that
    # tend to appear in subtopics (e.g. "&", ":").
    v = re.sub(r"\s+", "", v)
    # Keep only URL-ish safe characters for keys.
    v = re.sub(r"[^a-z0-9_\-]", "", v)
    return v or "unknown"


# ---------------------------------------------------------------------------
# ID generators
# ---------------------------------------------------------------------------

def _hostname_prefix(length: int = 6) -> str:
    return socket.gethostname()[:length].lower().replace("-", "").replace(".", "")


def generate_entity_id(content_type: str) -> str:
    """{content_type}_{6chars_hostname}_{timestamp_millis}"""
    ts = int(time.time() * 1000)
    return f"{content_type}_{_hostname_prefix()}_{ts}"


def generate_workflow_execution_id(content_type: str) -> str:
    """{content_type}_workflow_{timestamp_millis}"""
    ts = int(time.time() * 1000)
    return f"{content_type}_workflow_{ts}"


def iso_utc(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return (
        dt.astimezone(timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )


def _shard_for(value: str, shard_count: int = SHARD_COUNT) -> str:
    digest = sha256(value.encode("utf-8")).hexdigest()
    return f"{int(digest[:8], 16) % shard_count:02d}"


# ---------------------------------------------------------------------------
# Blob path builder
# ---------------------------------------------------------------------------

def _blob_path(
    content_type: str,
    category: str,
    sub_category: str,
    workflow_execution_id: str,
    entity_id: str,
) -> str:
    return f"{content_type}/{category}/{sub_category}/{workflow_execution_id}/{entity_id}.json"


# ---------------------------------------------------------------------------
# Public write method
# ---------------------------------------------------------------------------

def write_to_azure_storage(
    *,
    connection_string: str,
    container_name: str,
    content_type: str,
    category: str,
    sub_category: str,
    workflow_execution_id: str,
    entity_id: str,
    article_md: str,
    article_json: dict[str, Any],
    status: str = "generated",
    source: str = "tennl_batch_workflow_v1",
) -> dict[str, str]:
    """Blob-first write, then table index upserts.

    Returns a dict with ``blob_url``, ``workflow_execution_id``, ``entity_id``.
    """
    now = datetime.now(timezone.utc)
    event_time = iso_utc(now)

    # --- 1. Blob (source of truth) ----------------------------------------
    blob_svc = BlobServiceClient.from_connection_string(connection_string)
    blob_container = blob_svc.get_container_client(container_name)
    try:
        blob_container.create_container()
    except Exception:
        pass  # already exists or being created concurrently
    blob_key = _blob_path(content_type, category, sub_category, workflow_execution_id, entity_id)

    payload = json.dumps(
        {
            "workflowExecutionId": workflow_execution_id,
            "entityId": entity_id,
            "category": category,
            "subCategory": sub_category,
            "eventTime": event_time,
            "contentType": content_type,
            "indexStatus": "pending_index",
            "article_md": article_md,
            "article_json": article_json,
        },
        ensure_ascii=False,
        indent=2,
    )
    blob_client = blob_container.get_blob_client(blob_key)
    blob_client.upload_blob(payload, overwrite=True, content_settings=_json_content_settings())
    blob_url = blob_client.url
    logger.info("Blob written: %s", blob_key)

    # --- 2. Table indexes --------------------------------------------------
    table_svc = TableServiceClient.from_connection_string(connection_string)
    shard_id = _shard_for(workflow_execution_id)
    safe_category = _table_key_component(category)
    safe_sub_category = _table_key_component(sub_category)

    wf_entity = {
        "PartitionKey": workflow_execution_id,
        "RowKey": f"{event_time}{SEP}{entity_id}",
        "workflowExecutionId": workflow_execution_id,
        "entityId": entity_id,
        "category": category,
        "subCategory": sub_category,
        "eventTime": event_time,
        "blobUrl": blob_url,
        "status": status,
        "source": source,
    }
    cat_entity = {
        "PartitionKey": f"{safe_category}{SEP}{safe_sub_category}{SEP}{shard_id}",
        "RowKey": f"{event_time}{SEP}{workflow_execution_id}{SEP}{entity_id}",
        "workflowExecutionId": workflow_execution_id,
        "entityId": entity_id,
        "category": category,
        "subCategory": sub_category,
        "eventTime": event_time,
        "blobUrl": blob_url,
        "status": status,
        "source": source,
    }

    try:
        wf_table = table_svc.get_table_client("workflowentityindex")
        wf_table.upsert_entity(entity=wf_entity, mode=UpdateMode.REPLACE)
        logger.info("workflowentityindex upserted: PK=%s", wf_entity["PartitionKey"])
    except Exception:
        logger.exception("workflowentityindex upsert failed — blob is durable, reconciliation will repair")

    try:
        cat_table = table_svc.get_table_client("categoryentityindex")
        cat_table.upsert_entity(entity=cat_entity, mode=UpdateMode.REPLACE)
        logger.info("categoryentityindex upserted: PK=%s", cat_entity["PartitionKey"])
    except Exception:
        logger.exception("categoryentityindex upsert failed — blob is durable, reconciliation will repair")

    # --- 3. Update blob indexStatus ----------------------------------------
    try:
        updated = json.loads(payload)
        updated["indexStatus"] = "indexed"
        blob_client.upload_blob(
            json.dumps(updated, ensure_ascii=False, indent=2),
            overwrite=True,
            content_settings=_json_content_settings(),
        )
    except Exception:
        logger.exception("Failed to update blob indexStatus — reconciler will handle")

    return {
        "blob_url": blob_url,
        "workflow_execution_id": workflow_execution_id,
        "entity_id": entity_id,
    }


def _json_content_settings():
    from azure.storage.blob import ContentSettings
    return ContentSettings(content_type="application/json")
