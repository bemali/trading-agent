from pathlib import Path
import json
from filelock import FileLock
import os
from datetime import datetime

# Base directory for user data
BASE = Path(__file__).resolve().parents[2] / "data" / "users"

def user_dir(username: str) -> Path:
    """
    Create and return a user directory path.
    
    Args:
        username: The username to create a directory for
        
    Returns:
        Path object to the user directory
    """
    p = BASE / username
    p.mkdir(parents=True, exist_ok=True)
    return p

def atomic_write(path: Path, data):
    """
    Atomically write data to a file using a temporary file and replace operation.
    
    Args:
        path: Path to write to
        data: JSON-serializable data to write
    """
    tmp = path.with_suffix('.tmp')
    with tmp.open('w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.flush()
        os.fsync(f.fileno())  # Ensure data is written to disk
    tmp.replace(path)  # Atomic replacement

def read_json(path: Path):
    """
    Read and parse a JSON file.
    
    Args:
        path: Path to the JSON file
        
    Returns:
        Parsed JSON data or None if file doesn't exist
    """
    if not path.exists():
        return None
    with path.open('r', encoding='utf-8') as f:
        return json.load(f)

def write_json_with_lock(path: Path, data):
    """
    Write JSON data to a file with file locking to prevent concurrent writes.
    
    Args:
        path: Path to write to
        data: JSON-serializable data to write
    """
    lock = FileLock(str(path) + ".lock")
    with lock:
        atomic_write(path, data)
