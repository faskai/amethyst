"""App persistence DAO."""

import json
import os
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
#   json_obj JSONB
# );


def create_app(json_obj: dict) -> str:
    """Insert new app."""
    app_id = str(uuid4())
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO app (id, json_obj) VALUES (%s, %s)",
                (app_id, json.dumps(json_obj)),
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


def update_app(app_id: str, json_obj: dict):
    """Update app."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE app SET json_obj = %s WHERE id = %s",
                (json.dumps(json_obj), app_id),
            )
            conn.commit()
    finally:
        conn.close()


def list_apps() -> list:
    """List all apps."""
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT id, json_obj FROM app ORDER BY id DESC")
            rows = cur.fetchall()
            return (
                [{"id": row["id"], **row["json_obj"]} for row in rows] if rows else []
            )
    finally:
        conn.close()
