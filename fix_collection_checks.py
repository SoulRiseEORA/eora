#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MongoDB Collection 검사 방식 수정 스크립트
collection을 if collection: 에서 if collection is not None: 으로 변경
"""

import os
import re

def fix_collection_checks():
    """MongoDB collection 검사 방식을 수정합니다."""
    
    target_files = [
        "src/aura_memory_system.py",
        "src/app.py",
        "src/database.py"
    ]
    
    # 수정할 패턴들
    patterns = [
        (r'if\s+self\.memory_collection\s*:', 'if self.memory_collection is not None:'),
        (r'if\s+memories_collection\s*:', 'if memories_collection is not None:'),
        (r'if\s+sessions_collection\s*:', 'if sessions_collection is not None:'),
        (r'if\s+chat_logs_collection\s*:', 'if chat_logs_collection is not None:'),
        (r'if\s+users_collection\s*:', 'if users_collection is not None:'),
        (r'if\s+points_collection\s*:', 'if points_collection is not None:'),
        (r'if\s+system_logs_collection\s*:', 'if system_logs_collection is not None:'),
    ]
    
    for file_path in target_files:
        if not os.path.exists(file_path):
            print(f"⚠️ 파일을 찾을 수 없습니다: {file_path}")
            continue
            
        print(f"🔧 수정 중: {file_path}")
        
        try:
            # 파일 읽기
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # 패턴별 수정
            for pattern, replacement in patterns:
                matches = re.findall(pattern, content)
                if matches:
                    content = re.sub(pattern, replacement, content)
                    print(f"   ✅ {len(matches)}개 패턴 수정: {pattern}")
            
            # 변경사항이 있으면 파일 저장
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"   💾 파일 저장 완료: {file_path}")
            else:
                print(f"   ℹ️ 수정할 내용이 없습니다: {file_path}")
                
        except Exception as e:
            print(f"   ❌ 오류 발생: {e}")

if __name__ == "__main__":
    print("🔧 MongoDB Collection 검사 방식 수정 시작")
    fix_collection_checks()
    print("✅ 수정 완료!") 