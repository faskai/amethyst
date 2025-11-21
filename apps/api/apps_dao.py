"""App persistence DAO."""

import os
from datetime import datetime
from uuid import uuid4

import psycopg2
from psycopg2.extras import RealDictCursor


def get_db_connection():
    return psycopg2.connect(
        user="postgres",
        password=os.getenv("PGPASSWORD"),
        host=os.getenv("PGHOST", "localhost"),
        database=os.getenv("PGDATABASE", "amethyst"),
        port=5432,
    )


# CREATE TABLE app (
#   id VARCHAR(50) PRIMARY KEY,
#   json_obj JSONB,
#   updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );


def create_app(json_str: str, updated_at: datetime) -> str:
    """Insert new app."""
    app_id = str(uuid4())
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO app (id, json_obj, updated_at) VALUES (%s, %s, %s)",
                (app_id, json_str, updated_at),
            )
            conn.commit()
        return app_id
    finally:
        conn.close()


def get_app(app_id: str) -> dict:
    """Get app by ID."""
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT json_obj FROM app WHERE id = %s", (app_id,))
            row = cur.fetchone()
            return row["json_obj"] if row else None
    finally:
        conn.close()


def update_app(app_id: str, json_str: str, updated_at: datetime):
    """Update app."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE app SET json_obj = %s, updated_at = %s WHERE id = %s",
                (json_str, updated_at, app_id),
            )
            conn.commit()
    finally:
        conn.close()


def list_apps() -> list:
    """List all apps sorted by updated_at DESC."""
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT id, json_obj FROM app ORDER BY updated_at DESC")
            rows = cur.fetchall()
            return (
                [{"id": row["id"], **row["json_obj"]} for row in rows] if rows else []
            )
    finally:
        conn.close()
