import pytest
from src.utils.password_utils import PasswordUtils
from src.utils.security_utils import SecurityUtils
from src.utils.phone_utils import PhoneUtils
from .test_base import AsyncTestCase

class TestUtils(AsyncTestCase):
    def test_password_utils(self):
        # Test password validation
        assert PasswordUtils.validate_password("StrongPass123!")
        assert not PasswordUtils.validate_password("weak")
        
        # Test password hashing
        password = "MyPassword123"
        hashed = PasswordUtils.hash_password(password)
        assert PasswordUtils.verify_password(hashed, password)

    def test_security_utils(self):
        # Test token generation and validation
        token = SecurityUtils.generate_access_token(user_id=123)
        payload = SecurityUtils.validate_token(token)
        assert payload is not None
        assert payload['user_id'] == 123

    def test_phone_utils(self):
        # Test phone number validation
        assert PhoneUtils.validate_phone("+79123456789")
        assert not PhoneUtils.validate_phone("invalid")
        
        # Test phone number formatting
        assert PhoneUtils.format_phone("+79123456789") == "+7 (912) 345-67-89"

if __name__ == '__main__':
    unittest.main()
