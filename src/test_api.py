#!/usr/bin/env python3
"""
API 상태 테스트 스크립트
"""

import requests
import json

BASE = "http://127.0.0.1:8001"

print("[1] 회원가입 테스트...")
reg = requests.post(f"{BASE}/api/auth/register", json={
    "name": "테스트회원",
    "email": "testuser1@eora.ai",
    "password": "testpw1234"
})
print("회원가입 응답:", reg.status_code, reg.text)

print("[2] 일반 회원 로그인...")
login = requests.post(f"{BASE}/api/auth/login", json={
    "email": "testuser1@eora.ai",
    "password": "testpw1234"
})
print("로그인 응답:", login.status_code, login.text)
user_token = login.cookies.get("token")

print("[3] 일반 회원으로 관리자 페이지 접근...")
admin_page = requests.get(f"{BASE}/admin", cookies={"token": user_token})
print("관리자 페이지 접근 응답:", admin_page.status_code)

print("[4] 채팅(포인트 차감) 테스트...")
chat = requests.post(f"{BASE}/api/chat", json={
    "message": "안녕!",
    "session_id": "testsession1"
}, cookies={"token": user_token})
print("채팅 응답:", chat.status_code, chat.text)

print("[5] 관리자 로그인...")
admin_login = requests.post(f"{BASE}/api/auth/login", json={
    "email": "admin@eora.ai",
    "password": "admin1234"
})
print("관리자 로그인 응답:", admin_login.status_code, admin_login.text)
admin_token = admin_login.cookies.get("token")

print("[6] 관리자 페이지 접근...")
admin_page2 = requests.get(f"{BASE}/admin", cookies={"token": admin_token})
print("관리자 페이지 접근 응답:", admin_page2.status_code)

print("[7] 회원별 포인트/채팅 DB 분리 여부는 MongoDB에서 직접 확인 필요!") 