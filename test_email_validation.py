#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
이메일 검증 패턴 테스트
"""

import re

def test_email_validation():
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    test_emails = [
        'test@example.com',
        'user.name@domain.co.kr', 
        'invalid-email',
        'test@',
        '@domain.com',
        'test@domain',
        'user+tag@example.org',
        'user_name@test-domain.com',
        'test.email+tag@domain.co.uk',
        'test@sub.domain.com',
        '',
        'a@b.co',
        'test@domain.c'  # 1글자 TLD (무효해야 함)
    ]
    
    print("=" * 50)
    print("📧 이메일 검증 패턴 테스트")
    print("=" * 50)
    
    for email in test_emails:
        result = bool(re.match(pattern, email))
        status = "✅ 유효" if result else "❌ 무효"
        print(f"{email:<30} -> {status}")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    test_email_validation()