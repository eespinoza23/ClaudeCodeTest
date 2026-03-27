import pytest
from encryption import encrypt_data, decrypt_data, derive_key

class TestEncryption:
    def test_encrypt_decrypt_roundtrip(self):
        """Encrypted data should decrypt to original"""
        plaintext = "John Smith | Vegetarian"
        password = "master_password_123"

        encrypted = encrypt_data(plaintext, password)
        decrypted = decrypt_data(encrypted, password)

        assert decrypted == plaintext

    def test_decrypt_wrong_password_fails(self):
        """Wrong password should raise exception"""
        plaintext = "John Smith | Vegetarian"
        password = "correct_password"

        encrypted = encrypt_data(plaintext, password)

        with pytest.raises(Exception):
            decrypt_data(encrypted, "wrong_password")

    def test_encrypt_returns_base64(self):
        """Encrypted data should be base64 encoded"""
        plaintext = "Test Data"
        password = "password"

        encrypted = encrypt_data(plaintext, password)

        # Should be valid base64 (no special chars except - _ =)
        assert all(c.isalnum() or c in '-_=' for c in encrypted)

    def test_encrypt_is_deterministic_with_seed(self):
        """Same plaintext + password should produce different ciphertexts (due to random nonce)"""
        plaintext = "John Smith | Vegetarian"
        password = "password"

        encrypted1 = encrypt_data(plaintext, password)
        encrypted2 = encrypt_data(plaintext, password)

        # They should be different (different nonces)
        assert encrypted1 != encrypted2

        # But both should decrypt to the same thing
        assert decrypt_data(encrypted1, password) == plaintext
        assert decrypt_data(encrypted2, password) == plaintext
