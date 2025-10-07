import sys
from pathlib import Path
import json
import os

# Add the project root directory to sys.path to resolve imports
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# Import directly from the utils directory
from app.utils.storage import user_dir, write_json_with_lock, read_json

def test_json_operations():
    """Test the JSON read/write operations with locking"""
    
    # Test data
    test_user = "testuser"
    test_data = {
        "name": "Test User",
        "email": "test@example.com",
        "created_at": "2025-10-07T10:20:00"
    }
    
    # Get user directory
    user_path = user_dir(test_user)
    
    # Path for test file
    test_file = user_path / "profile.json"
    
    # Write data with lock
    write_json_with_lock(test_file, test_data)
    print(f"✓ Successfully wrote data to {test_file}")
    
    # Read data back
    read_data = read_json(test_file)
    
    # Verify data matches
    if read_data == test_data:
        print(f"✓ Successfully read back identical data")
        print(f"Test passed! JSON read/write operations work correctly.")
        return True
    else:
        print(f"❌ Data mismatch!")
        print(f"Original: {test_data}")
        print(f"Read: {read_data}")
        return False

if __name__ == "__main__":
    test_json_operations()
