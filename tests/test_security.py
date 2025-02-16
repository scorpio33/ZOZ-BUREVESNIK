import pytest
from src.core.security import SecurityManager

class TestSecurity:
    @pytest.fixture
    def security_manager(self):
        return SecurityManager()
    
    def test_password_strength(self, security_manager):
        # Test password hashing
        password = "test_password123"
        hashed = security_manager.hash_password(password)
        assert len(hashed) == 64  # SHA-256 produces 64 character hex string
        assert security_manager.verify_password(hashed, password)
        assert not security_manager.verify_password(hashed, "wrong_password")
    
    def test_verification_code_security(self, security_manager):
        code = security_manager.generate_verification_code()
        assert len(code) == 6
        assert code.isdigit()
        
    def test_brute_force_protection(self, security_manager):
        user_id = 12345
        
        # Should allow initial attempts
        assert security_manager.check_brute_force(user_id)
        
        # Record failed attempts
        for _ in range(3):
            security_manager.record_failed_attempt(user_id)
            
        # Should be locked out after max attempts
        assert not security_manager.check_brute_force(user_id)
        
        # Reset should allow access again
        security_manager.reset_attempts(user_id)
        assert security_manager.check_brute_force(user_id)
    
    def test_session_security(self, security_manager):
        # Test multiple users don't interfere
        user1_id = 11111
        user2_id = 22222
        
        # Lock out user1
        for _ in range(3):
            security_manager.record_failed_attempt(user1_id)
            
        # User2 should still have access
        assert security_manager.check_brute_force(user2_id)
        # User1 should be locked
        assert not security_manager.check_brute_force(user1_id)
    
if __name__ == '__main__':
    unittest.main()
