#!/usr/bin/env python3
"""세션 파일 마이그레이션 스크립트"""
import os
import json
import shutil
from datetime import datetime

def migrate_sessions():
    """기존 세션 파일들을 새로운 user_id 형식으로 마이그레이션"""
    sessions_dir = "sessions_backup"
    
    if not os.path.exists(sessions_dir):
        print("sessions_backup 디렉토리가 없습니다.")
        return
    
    # 백업 디렉토리 생성
    backup_dir = f"sessions_backup_old_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)
    
    migrated = 0
    errors = 0
    
    for filename in os.listdir(sessions_dir):
        if not filename.endswith('.json'):
            continue
            
        old_path = os.path.join(sessions_dir, filename)
        
        try:
            # 백업
            shutil.copy2(old_path, os.path.join(backup_dir, filename))
            
            # 파일명 분석
            if filename.startswith('admin_'):
                # admin_session_local_xxx.json -> admin@eora.ai_session_local_xxx.json
                new_filename = filename.replace('admin_', 'admin@eora.ai_', 1)
                new_path = os.path.join(sessions_dir, new_filename)
                
                # 파일 내용도 업데이트 (필요한 경우)
                with open(old_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # user_id 필드 업데이트 (있는 경우)
                updated = False
                for item in data:
                    if isinstance(item, dict):
                        if item.get('user_id') == 'admin':
                            item['user_id'] = 'admin@eora.ai'
                            updated = True
                        if item.get('user') == 'admin':
                            item['user'] = 'admin@eora.ai'
                            updated = True
                
                # 새 파일로 저장
                with open(new_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                # 기존 파일 삭제
                if old_path != new_path:
                    os.remove(old_path)
                
                print(f"✅ 마이그레이션 완료: {filename} -> {new_filename}")
                migrated += 1
                
        except Exception as e:
            print(f"❌ 마이그레이션 실패: {filename} - {str(e)}")
            errors += 1
    
    print(f"\n📊 마이그레이션 결과:")
    print(f"  - 성공: {migrated}개")
    print(f"  - 실패: {errors}개")
    print(f"  - 백업 위치: {backup_dir}")

if __name__ == "__main__":
    migrate_sessions() 