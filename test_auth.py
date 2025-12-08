#!/usr/bin/env python3
"""Simple test script to verify authentication functionality."""
import os
import sys
import tempfile
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from auth import UserStore

def test_authentication():
    """Test basic authentication functionality."""
    print("Testing authentication system...")
    
    # Create temporary file path
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        test_file = f.name
    # Delete the file so UserStore can create it fresh
    os.unlink(test_file)
    
    try:
        # Test 1: Initialize user store
        print("\n✓ Test 1: Initialize UserStore")
        store = UserStore(test_file)
        assert Path(test_file).exists(), "Users file should be created"
        
        # Test 2: Verify default credentials
        print("✓ Test 2: Verify default credentials (admin/admin123)")
        assert store.verify_user("admin", "admin123"), "Default credentials should work"
        
        # Test 3: Reject wrong password
        print("✓ Test 3: Reject wrong password")
        assert not store.verify_user("admin", "wrongpassword"), "Wrong password should be rejected"
        
        # Test 4: Reject non-existent user
        print("✓ Test 4: Reject non-existent user")
        assert not store.verify_user("nonexistent", "password"), "Non-existent user should be rejected"
        
        # Test 5: Get user
        print("✓ Test 5: Get user")
        user = store.get_user("admin")
        assert user is not None, "Should get user object"
        assert user.username == "admin", "Username should match"
        assert user.id == "admin", "User ID should match username"
        
        # Test 6: Change password
        print("✓ Test 6: Change password")
        assert store.change_password("admin", "newpassword123"), "Password change should succeed"
        assert store.verify_user("admin", "newpassword123"), "New password should work"
        assert not store.verify_user("admin", "admin123"), "Old password should not work"
        
        # Test 7: Custom credentials via environment
        print("✓ Test 7: Custom credentials via environment variables")
        os.environ["RECEIPT_SCANNER_USERNAME"] = "testuser"
        os.environ["RECEIPT_SCANNER_PASSWORD"] = "testpass456"
        
        # Create new store with custom credentials
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            test_file2 = f.name
        os.unlink(test_file2)  # Delete so UserStore can create it fresh
        
        store2 = UserStore(test_file2)
        assert store2.verify_user("testuser", "testpass456"), "Custom credentials should work"
        
        # Cleanup
        os.unlink(test_file2)
        del os.environ["RECEIPT_SCANNER_USERNAME"]
        del os.environ["RECEIPT_SCANNER_PASSWORD"]
        
        print("\n✅ All tests passed!")
        return True
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return False
    
    finally:
        # Cleanup
        if os.path.exists(test_file):
            os.unlink(test_file)

if __name__ == "__main__":
    success = test_authentication()
    sys.exit(0 if success else 1)
