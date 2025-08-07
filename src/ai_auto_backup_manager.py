# ai_auto_backup_manager.py
import os
import shutil
import json
from datetime import datetime

BACKUP_DIR = "./backups"
ROLLBACK_LOG = "./logs/rollback_history.json"

os.makedirs(BACKUP_DIR, exist_ok=True)
os.makedirs(os.path.dirname(ROLLBACK_LOG), exist_ok=True)

class BackupManager:
    def __init__(self):
        self.backup_log = self._load_log()
        self.error_count = 0

    def _load_log(self):
        if os.path.exists(ROLLBACK_LOG):
            with open(ROLLBACK_LOG, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def _save_log(self):
        with open(ROLLBACK_LOG, "w", encoding="utf-8") as f:
            json.dump(self.backup_log, f, indent=4, ensure_ascii=False)

    def auto_backup_check(self, filepath: str, status: str, summary: str = ""):
        if not os.path.exists(filepath):
            print(f"[백업 실패] 파일 없음: {filepath}")
            return

        filename = os.path.basename(filepath)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        version_tag = f"{filename}_{timestamp}"
        backup_path = os.path.join(BACKUP_DIR, version_tag)

        if status == "success":
            shutil.copy2(filepath, backup_path)
            self.backup_log.append({
                "file": filename,
                "version": timestamp,
                "summary": summary,
                "path": backup_path
            })
            self._save_log()
            print(f"[백업 완료] {version_tag}")
            self.error_count = 0

        elif status == "error":
            self.error_count += 1
            if self.error_count >= 10:
                self.rollback_to_last_success()
            elif self.error_count >= 5:
                print("[주의] 최근 성공 파일을 참고하세요.")

    def rollback_to_last_success(self):
        if not self.backup_log:
            print("[롤백 실패] 백업 없음")
            return

        last = self.backup_log[-1]
        shutil.copy2(last['path'], last['file'])
        print(f"[롤백 완료] {last['file']} ← {last['version']}")

    def get_backup_list(self):
        return self.backup_log[-5:]

backup_manager = BackupManager()

def auto_backup_check(filepath: str, status: str, summary: str = ""):
    backup_manager.auto_backup_check(filepath, status, summary)

def get_backup_list():
    return backup_manager.get_backup_list()

def rollback_to_last_success():
    return backup_manager.rollback_to_last_success()
