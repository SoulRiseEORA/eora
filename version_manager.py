"""
version_manager.py
- 코드 버전 관리 및 롤백 시스템
"""

import os
from shutil import copy2

def backup_file(path):
    backup = str(path) + ".bak"
    copy2(path, backup)
    return backup

def restore_file(path):
    backup = str(path) + ".bak"
    if os.path.exists(backup):
        copy2(backup, path)
        return True
    return False
