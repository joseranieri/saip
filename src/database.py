"""
Módulo de Banco de Dados Local (SQLite) do SAIP.

Garante a criação automática das tabelas 'users' e 'datasets', aplica
migrações incrementais para os metadados de edição (1º ao 8º simulado) e
ano letivo, e fornece consultas ordenadas para análise temporal.
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "saip.db"


def _ensure_schema(conn: sqlite3.Connection) -> None:
    """Garante que as tabelas e colunas existam na conexão ativa."""
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            must_change_password INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL
        )
        """
    )

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS datasets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            original_filename TEXT NOT NULL,
            simulado_num INTEGER DEFAULT 1,
            ano_letivo INTEGER DEFAULT 2026,
            row_count INTEGER NOT NULL,
            column_names TEXT NOT NULL,
            records_json TEXT NOT NULL,
            metrics_json TEXT NOT NULL,
            created_at TEXT NOT NULL,
            created_by TEXT NOT NULL
        )
        """
    )

    existing_cols = {
        row["name"]
        for row in conn.execute("PRAGMA table_info(datasets)").fetchall()
    }
    if "simulado_num" not in existing_cols:
        conn.execute(
            "ALTER TABLE datasets ADD COLUMN simulado_num INTEGER DEFAULT 1"
        )
    if "ano_letivo" not in existing_cols:
        conn.execute(
            "ALTER TABLE datasets ADD COLUMN ano_letivo INTEGER DEFAULT 2026"
        )

    conn.commit()


def get_connection() -> sqlite3.Connection:
    """Abre conexão com o banco SQLite local e garante o schema."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    _ensure_schema(conn)
    return conn


get_db_connection = get_connection


def init_db() -> None:
    """Inicializa o banco SQLite local."""
    with get_connection() as conn:
        _ensure_schema(conn)


def save_dataset(
    name: str,
    original_filename: str,
    row_count: int,
    column_names: list[str],
    records: list[dict],
    metrics: dict,
    username: str,
    simulado_num: int = 1,
    ano_letivo: int = 2026,
) -> int:
    """Salva um conjunto de dados processado com a edição do simulado e o ano letivo."""
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO datasets (
                name,
                original_filename,
                simulado_num,
                ano_letivo,
                row_count,
                column_names,
                records_json,
                metrics_json,
                created_at,
                created_by
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                name,
                original_filename,
                int(simulado_num),
                int(ano_letivo),
                int(row_count),
                json.dumps(column_names, ensure_ascii=False),
                json.dumps(records, ensure_ascii=False, default=str),
                json.dumps(metrics, ensure_ascii=False, default=str),
                created_at,
                username,
            ),
        )
        conn.commit()
        return int(cursor.lastrowid)


def list_datasets() -> list[dict]:
    """Lista os metadados de todas as importações salvas, ordenadas por ano e simulado."""
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT
                id,
                name,
                original_filename,
                COALESCE(simulado_num, 1) AS simulado_num,
                COALESCE(ano_letivo, 2026) AS ano_letivo,
                row_count,
                created_at,
                created_by
            FROM datasets
            ORDER BY ano_letivo DESC, simulado_num ASC, id DESC
            """
        ).fetchall()

    return [dict(row) for row in rows]


def get_dataset(dataset_id: int) -> dict | None:
    """Recupera um conjunto de dados completo pelo seu ID."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM datasets WHERE id = ?",
            (int(dataset_id),),
        ).fetchone()

    if not row:
        return None

    data = dict(row)
    data["simulado_num"] = data.get("simulado_num") or 1
    data["ano_letivo"] = data.get("ano_letivo") or 2026
    data["column_names"] = json.loads(data["column_names"])
    data["records"] = json.loads(data["records_json"])
    data["metrics"] = json.loads(data["metrics_json"])
    return data


def get_datasets_by_year(ano_letivo: int) -> list[dict]:
    """
    Retorna todos os simulados salvos de um determinado ano letivo,
    ordenados cronologicamente do 1º ao 8º simulado. Caso exista mais de
    uma importação para o mesmo simulado, utiliza a mais recente.
    """
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM datasets
            WHERE COALESCE(ano_letivo, 2026) = ?
            ORDER BY COALESCE(simulado_num, 1) ASC, id ASC
            """,
            (int(ano_letivo),),
        ).fetchall()

    by_simulado: dict[int, dict] = {}
    for row in rows:
        item = dict(row)
        sim_num = int(item.get("simulado_num") or 1)
        item["simulado_num"] = sim_num
        item["ano_letivo"] = int(item.get("ano_letivo") or 2026)
        item["column_names"] = json.loads(item["column_names"])
        item["records"] = json.loads(item["records_json"])
        item["metrics"] = json.loads(item["metrics_json"])
        by_simulado[sim_num] = item

    return [by_simulado[k] for k in sorted(by_simulado.keys())]