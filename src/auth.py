"""
Módulo de Autenticação do SAIP.
Gerencia criação, verificação, alteração e reset para a senha padrão.
"""

import hashlib
import hmac
import os
import secrets
from datetime import datetime

from src.database import get_connection

DEFAULT_USERNAME = os.getenv("DEFAULT_ADMIN_USER", "admin")
DEFAULT_PASSWORD = os.getenv("DEFAULT_ADMIN_PASSWORD", "Saip@2026!")


def _hash_password(password: str, salt: str | None = None) -> str:
    """Gera hash seguro PBKDF2-HMAC-SHA256."""
    if salt is None:
        salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        200_000,
    )
    return f"{salt}${dk.hex()}"


def _verify_password(password: str, stored_hash: str) -> bool:
    """Verifica senha contra o hash armazenado (suporta PBKDF2 ou SHA256 simples)."""
    if "$" in stored_hash:
        salt, _ = stored_hash.split("$", 1)
        expected = _hash_password(password, salt)
        return hmac.compare_digest(expected, stored_hash)
    # Compatibilidade caso um hash SHA256 simples tenha sido usado anteriormente
    simple_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
    return hmac.compare_digest(simple_hash, stored_hash)


def ensure_default_user(username: str = DEFAULT_USERNAME) -> None:
    """Garante que o usuário padrão exista no banco."""
    with get_connection() as conn:
        user = conn.execute(
            "SELECT id FROM users WHERE username = ?",
            (username,),
        ).fetchone()

        if not user:
            created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            conn.execute(
                """
                INSERT INTO users (username, password_hash, must_change_password, created_at)
                VALUES (?, ?, 1, ?)
                """,
                (username, _hash_password(DEFAULT_PASSWORD), created_at),
            )
            conn.commit()


def reset_default_password(username: str = DEFAULT_USERNAME) -> str:
    """
    Reseta a senha do usuário especificado de volta para a senha padrão
    e exige a troca no próximo acesso (must_change_password = 1).
    """
    ensure_default_user(username)
    new_hash = _hash_password(DEFAULT_PASSWORD)

    with get_connection() as conn:
        conn.execute(
            """
            UPDATE users
            SET password_hash = ?, must_change_password = 1
            WHERE username = ?
            """,
            (new_hash, username),
        )
        conn.commit()

    return DEFAULT_PASSWORD


def authenticate(username: str, password: str) -> dict | None:
    """Autentica usuário e senha."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id, username, password_hash, must_change_password FROM users WHERE username = ?",
            (username.strip(),),
        ).fetchone()

    if not row:
        return None

    if _verify_password(password, row["password_hash"]):
        return dict(row)
    return None


def change_password(username: str, current_password: str, new_password: str) -> bool:
    """Altera a senha validando a senha atual."""
    user = authenticate(username, current_password)
    if not user:
        return False

    new_hash = _hash_password(new_password)
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE users
            SET password_hash = ?, must_change_password = 0
            WHERE username = ?
            """,
            (new_hash, username),
        )
        conn.commit()
    return True