from __future__ import annotations

import hashlib
import hmac
import secrets


ALGORITHM = "pbkdf2_sha256"
ITERATIONS = 600_000
SALT_BYTES = 16


def get_password_hash(password: str) -> str:
    if not password:
        raise ValueError("La contrasena de administrador es obligatoria.")

    salt = secrets.token_hex(SALT_BYTES)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        ITERATIONS,
    ).hex()
    return f"{ALGORITHM}${ITERATIONS}${salt}${password_hash}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        algorithm, iterations_text, salt, expected_hash = password_hash.split("$", 3)
        iterations = int(iterations_text)
    except ValueError:
        return False

    if algorithm != ALGORITHM:
        return False

    candidate_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        iterations,
    ).hex()
    return hmac.compare_digest(candidate_hash, expected_hash)
