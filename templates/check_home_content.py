#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
홈 페이지 내용 확인 스크립트
"""

import requests

def check_home_content():
    """홈 페이지 내용 확인"""
    try:
        print("🔍 홈 페이지 내용 확인...")
        
        response = requests.get("http://127.0.0.1:8001/", timeout=10)
        
        if response.status_code == 200:
            content = response.text
            print(f"📝 응답 길이: {len(content)} 문자")
            
            # 주요 내용 확인
            if "EORA AI System" in content:
                print("✅ EORA AI System 텍스트 발견")
            else:
                print("❌ EORA AI System 텍스트 없음")
                
            if "감정 중심 인공지능 플랫폼" in content:
                print("✅ 감정 중심 인공지능 플랫폼 텍스트 발견")
            else:
                print("❌ 감정 중심 인공지능 플랫폼 텍스트 없음")
                
            if "채팅 시작" in content:
                print("✅ 채팅 시작 버튼 발견")
            else:
                print("❌ 채팅 시작 버튼 없음")
                
            if "favicon.ico" in content:
                print("✅ favicon 링크 발견")
            else:
                print("❌ favicon 링크 없음")
                
            # HTML 구조 확인
            if "<!DOCTYPE html>" in content:
                print("✅ DOCTYPE 선언 발견")
            else:
                print("❌ DOCTYPE 선언 없음")
                
            if "<html" in content:
                print("✅ HTML 태그 발견")
            else:
                print("❌ HTML 태그 없음")
                
            if "<head>" in content:
                print("✅ HEAD 태그 발견")
            else:
                print("❌ HEAD 태그 없음")
                
            if "<body>" in content:
                print("✅ BODY 태그 발견")
            else:
                print("❌ BODY 태그 없음")
                
            # 내용 미리보기
            print("\n📄 내용 미리보기 (처음 500자):")
            print("-" * 50)
            print(content[:500])
            print("-" * 50)
            
            # 오류 메시지 확인
            if "템플릿 오류가 발생했습니다" in content:
                print("\n❌ 템플릿 오류가 발생했습니다!")
                # 오류 메시지 추출
                start = content.find("템플릿 오류가 발생했습니다:")
                if start != -1:
                    end = content.find("</p>", start)
                    if end != -1:
                        error_msg = content[start:end]
                        print(f"오류 내용: {error_msg}")
            else:
                print("\n✅ 템플릿 오류 없음")
                
        else:
            print(f"❌ 홈 페이지 로드 실패: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 확인 중 오류 발생: {e}")

if __name__ == "__main__":
    print("🔍 홈 페이지 내용 상세 확인")
    print("=" * 50)
    check_home_content()
    print("\n" + "=" * 50)
    print("🏁 확인 완료") 