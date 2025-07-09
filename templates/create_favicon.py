#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EORA AI System Favicon 생성기 (굵은 E, 정중앙)
"""

from PIL import Image, ImageDraw, ImageFont
import os

def get_bold_font(size):
    # 굵은 폰트 우선 시도
    font_candidates = [
        "DejaVuSans-Bold.ttf",  # 리눅스/윈도우 공통
        "arialbd.ttf",         # Arial Bold (Windows)
        "Arial Black.ttf",     # Arial Black (Windows)
        "arial.ttf",           # 일반 Arial
    ]
    for font_name in font_candidates:
        try:
            return ImageFont.truetype(font_name, size)
        except:
            continue
    return ImageFont.load_default()

def create_favicon():
    size = 32
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 보라색 그라데이션 배경
    for y in range(size):
        r = int(128 + (y / size) * 64)
        g = int(64 + (y / size) * 32)
        b = int(192 + (y / size) * 48)
        draw.line([(0, y), (size, y)], fill=(r, g, b, 255))

    # 원형 마스크
    mask = Image.new('L', (size, size), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse([0, 0, size-1, size-1], fill=255)
    img.putalpha(mask)

    # 최대한 크게, 굵은 E
    text = "E"
    # 폰트 크기 자동 조정 (80%까지)
    for font_size in range(size, 0, -1):
        font = get_bold_font(font_size)
        bbox = draw.textbbox((0, 0), text, font=font)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        if w <= size * 0.8 and h <= size * 0.8:
            break
    # 중앙 좌표 계산
    x = (size - w) // 2 - bbox[0]
    y = (size - h) // 2 - bbox[1]
    # 그림자 효과
    draw.text((x+1, y+1), text, fill=(0, 0, 0, 120), font=font)
    # 메인 텍스트 (흰색)
    draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)

    # 저장
    img.save("favicon.ico", format='ICO', sizes=[(32, 32), (16, 16)])
    print("✅ favicon.ico 파일이 성공적으로 생성되었습니다!")
    print(f"📁 저장 위치: {os.path.abspath('favicon.ico')}")
    print(f"🎨 굵은 E, 정중앙, 보라색 그라데이션 배경")

if __name__ == "__main__":
    print("🎨 EORA AI System Favicon 생성기 (굵은 E, 정중앙)")
    print("=" * 50)
    try:
        create_favicon()
        print("💡 favicon.ico를 웹사이트 루트에 배치하세요.")
    except ImportError:
        print("❌ PIL(Pillow) 라이브러리가 설치되지 않았습니다.")
        print("📦 설치 명령: pip install Pillow")
    except Exception as e:
        print(f"❌ favicon 생성 중 오류 발생: {e}") 