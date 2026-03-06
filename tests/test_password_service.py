"""
Level 2: Password Service Tests — Introduces async testing.

WHAT'S NEW HERE:
    - These tests are 'async def' instead of regular 'def'
    - pytest-asyncio runs them in an event loop automatically
    - No mocking needed! We test real bcrypt hashing/verification.

WHY TEST THIS?
    Password hashing is security-critical. These tests ensure:
    1. Hashing produces something different from the plain password
    2. Verification works correctly (right password → True, wrong → False)
"""

from app.modules.auth.services.password import PasswordService


class TestPasswordService:
    """Tests for the PasswordService (bcrypt hashing & verification)."""

    async def test_hash_produces_different_string(self):
        """
        Hashing a password should return a string that is NOT the original.
        If it returned the same string, the password wouldn't be encrypted!
        """
        service = PasswordService()
        plain = "MyPassword123"

        hashed = await service.get_password_hash(plain)

        assert hashed != plain  # It should be different
        assert isinstance(hashed, str)  # It should be a string
        assert len(hashed) > 0  # It should not be empty

    async def test_verify_correct_password(self):
        """Verifying the correct password against its hash should return True."""
        service = PasswordService()
        plain = "CorrectPassword1"

        hashed = await service.get_password_hash(plain)
        result = await service.verify_password(plain, hashed)

        assert result is True

    async def test_verify_wrong_password(self):
        """Verifying a wrong password against the hash should return False."""
        service = PasswordService()

        hashed = await service.get_password_hash("RealPassword1")
        result = await service.verify_password("WrongPassword1", hashed)

        assert result is False

    async def test_same_password_different_hashes(self):
        """
        Hashing the same password twice should produce DIFFERENT results.
        This is because bcrypt adds a random 'salt' each time — a security feature.
        """
        service = PasswordService()
        plain = "SamePassword1"

        hash1 = await service.get_password_hash(plain)
        hash2 = await service.get_password_hash(plain)

        assert hash1 != hash2  # Different hashes (different salts)

        # But both should still verify correctly
        assert await service.verify_password(plain, hash1) is True
        assert await service.verify_password(plain, hash2) is True
