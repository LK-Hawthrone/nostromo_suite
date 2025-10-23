# core/hash_manager.py
import hashlib
import secrets

def generate_salt(length: int = 16) -> str:
    """
    Generates a secure random salt.
    Default size: 16 bytes → 32 hex characters.
    """
    return secrets.token_hex(length)

def hash_with_salt(value: str, salt: str) -> str:
    """
    Returns a SHA-256 hash of the given value combined with the salt.
    """
    combined = (value + salt).encode('utf-8')
    hashed = hashlib.sha256(combined).hexdigest()
    return hashed

def verify_hash(value: str, salt: str, stored_hash: str) -> bool:
    """
    Verifies whether a plain value, when hashed with the same salt,
    matches the stored hash.
    """
    return hash_with_salt(value, salt) == stored_hash

def secure_store(value: str) -> tuple:
    """
    Generates a salt + hash pair ready for database storage.
    Returns a tuple: (hashed_value, salt)
    """
    salt = generate_salt()
    hashed = hash_with_salt(value, salt)
    return hashed, salt
