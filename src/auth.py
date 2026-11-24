
import os
import hmac
import hashlib
import secrets

from src.database import get_connection

ITERATIONS = 310_000


def hash_password(password, salt=None):

    salt = salt or secrets.token_bytes(16)

    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        ITERATIONS
    )

    return salt.hex(), digest.hex()


def verify_password(password, salt_hex, hash_hex):

    _, candidate = hash_password(
        password,
        bytes.fromhex(salt_hex)
    )

    return hmac.compare_digest(candidate, hash_hex)


def ensure_default_user():

    username = os.getenv("SAIP_ADMIN_USER", "admin")
    password = os.getenv(
        "SAIP_ADMIN_PASSWORD",
        "SAIP@Mudar123"
    )

    with get_connection() as conn:

        user = conn.execute(
            "SELECT id FROM users WHERE username = ?",
            (username,)
        ).fetchone()

        if not user:

            salt, digest = hash_password(password)

            conn.execute("""
                INSERT INTO users (
                    username,
                    password_salt,
                    password_hash,
                    must_change_password
                )
                VALUES (?, ?, ?, 1)
            """, (username, salt, digest))


def authenticate(username, password):

    with get_connection() as conn:

        user = conn.execute("""
            SELECT *
            FROM users
            WHERE username = ?
            AND active = 1
        """, (username,)).fetchone()

    if user and verify_password(
        password,
        user["password_salt"],
        user["password_hash"]
    ):
        return dict(user)

    return None


def change_password(username, current_password, new_password):

    with get_connection() as conn:

        user = conn.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        ).fetchone()

        if not user:
            return False

        if not verify_password(
            current_password,
            user["password_salt"],
            user["password_hash"]
        ):
            return False

        salt, digest = hash_password(new_password)

        conn.execute("""
            UPDATE users
            SET
                password_salt = ?,
                password_hash = ?,
                must_change_password = 0
            WHERE username = ?
        """, (salt, digest, username))

    return True
