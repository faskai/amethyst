"""Resource persistence DAO."""

import json
import os

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


def create_resource(resource_key: str, json_obj: dict):
    """Insert or update resource by key."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO resource (id, json_obj) 
                VALUES (%s, %s)
                ON CONFLICT (id) 
                DO UPDATE SET json_obj = EXCLUDED.json_obj
                """,
                (resource_key, json.dumps(json_obj)),
            )
            conn.commit()
    finally:
        conn.close()


def get_resource(resource_key: str) -> dict:
    """Get resource by key."""
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT json_obj FROM resource WHERE id = %s", (resource_key,))
            row = cur.fetchone()
            return row["json_obj"] if row else None
    finally:
        conn.close()


def list_resources() -> list:
    """List all resources."""
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT id, json_obj FROM resource ORDER BY id")
            rows = cur.fetchall()
            return (
                [{"id": row["id"], **row["json_obj"]} for row in rows] if rows else []
            )
    finally:
        conn.close()


def search_resources(query: str) -> list:
    """Search resources by name using ILIKE."""
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT id, json_obj 
                FROM resource 
                WHERE json_obj->>'name' ILIKE %s 
                ORDER BY json_obj->>'name'
                """,
                (f"%{query}%",),
            )
            rows = cur.fetchall()
            return (
                [{"id": row["id"], **row["json_obj"]} for row in rows] if rows else []
            )
    finally:
        conn.close()


def delete_resource(resource_key: str):
    """Delete resource by key."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM resource WHERE id = %s", (resource_key,))
            conn.commit()
    finally:
        conn.close()
