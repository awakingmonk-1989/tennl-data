"""Local PostgreSQL persistence for batch-mode article storage.

Inserts one row per workflow run (success or failure) into
``content_gen.content_gen_article``. Failure is logged but never stops
the batch — same resilience pattern as Azure persist.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any, Optional, Protocol

logger = logging.getLogger(__name__)

PG_DSN = os.environ.get(
    "CONTENT_GEN_PG_DSN",
    "postgresql://devansh@localhost:5432/content_gen",
)


class PsycopgPool(Protocol):
    """Minimal protocol for psycopg_pool.ConnectionPool."""

    def connection(self):  # pragma: no cover
        """Return a context manager yielding a psycopg connection."""


def insert_article(
    *,
    run_id: str,
    article_md: Optional[str] = None,
    article_json: Optional[dict[str, Any]] = None,
    status: str = "success",
    reason: Optional[str] = None,
    error_message: Optional[str] = None,
    pool: Optional[PsycopgPool] = None,
) -> None:
    """INSERT a single row for a workflow run. Fails gracefully with a log."""
    try:
        import psycopg

        json_value = (
            json.dumps(article_json, ensure_ascii=False) if article_json else None
        )
        def _do_insert(conn: Any) -> None:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO content_gen_article
                        (id, run_id, article_md, article_json, status, reason, error_message)
                    VALUES (%s::uuid, %s, %s, %s::jsonb, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING
                    """,
                    (run_id, run_id, article_md, json_value, status, reason, error_message),
                )
            conn.commit()

        if pool is not None:
            with pool.connection() as conn:
                _do_insert(conn)
        else:
            # Sequential / single mode: no pool needed.
            with psycopg.connect(PG_DSN) as conn:
                _do_insert(conn)
        logger.info("PostgreSQL insert: run_id=%s status=%s", run_id, status)
    except Exception:
        logger.exception("PostgreSQL insert failed for run_id=%s — batch continues", run_id)
