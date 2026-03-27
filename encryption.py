"""Encryption utility for QR code data using AES-256-GCM"""

import base64
import json
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.backends import default_backend
import os


def derive_key(password: str, salt: bytes) -> bytes:
    """Derive AES-256 key from password using PBKDF2"""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,  # 256 bits for AES-256
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    return kdf.derive(password.encode())


def encrypt_data(plaintext: str, password: str) -> str:
    """
    Encrypt plaintext with password using AES-256-GCM.
    Returns base64-encoded string containing salt + nonce + ciphertext + tag.
    """
    # Generate random salt and nonce
    salt = os.urandom(16)  # 128 bits
    nonce = os.urandom(12)  # 96 bits (standard for GCM)

    # Derive key from password
    key = derive_key(password, salt)

    # Encrypt
    cipher = AESGCM(key)
    ciphertext = cipher.encrypt(nonce, plaintext.encode(), None)

    # Combine: salt (16) + nonce (12) + ciphertext+tag (variable)
    payload = salt + nonce + ciphertext

    # Encode to base64 for QR code compatibility
    encoded = base64.urlsafe_b64encode(payload).decode('ascii')

    return encoded


def decrypt_data(encoded: str, password: str) -> str:
    """
    Decrypt base64-encoded encrypted data with password.
    Raises exception if decryption fails (wrong password or corrupted data).
    """
    # Decode from base64
    try:
        payload = base64.urlsafe_b64decode(encoded.encode('ascii'))
    except Exception as e:
        raise ValueError(f"Invalid base64 encoding: {e}")

    # Extract components
    if len(payload) < 28:  # 16 (salt) + 12 (nonce) + 0 (minimum ciphertext)
        raise ValueError("Payload too short")

    salt = payload[:16]
    nonce = payload[16:28]
    ciphertext = payload[28:]

    # Derive key from password
    key = derive_key(password, salt)

    # Decrypt
    cipher = AESGCM(key)
    try:
        plaintext = cipher.decrypt(nonce, ciphertext, None)
    except Exception as e:
        raise ValueError(f"Decryption failed - wrong password or corrupted data: {e}")

    return plaintext.decode()
