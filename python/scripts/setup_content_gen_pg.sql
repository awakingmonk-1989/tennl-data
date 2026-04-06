-- Idempotent PostgreSQL setup for content_gen database.
--
-- Usage (from repo root):
--
--   psql -d postgres -c "CREATE DATABASE content_gen" 2>/dev/null || true
--   psql -d content_gen -f python/scripts/setup_content_gen_pg.sql
--
-- On macOS with Homebrew postgresql@18, the default user is your OS username.
-- Override via: CONTENT_GEN_PG_DSN="postgresql://user@host:5432/content_gen"

CREATE TABLE IF NOT EXISTS content_gen_article (
    id              UUID    PRIMARY KEY,
    run_id          TEXT    NOT NULL,
    article_md      TEXT,
    article_json    JSONB,
    status          TEXT,
    reason          TEXT,
    error_message   TEXT
);
