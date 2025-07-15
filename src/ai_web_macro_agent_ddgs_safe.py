# src/ai_web_macro_agent.py

import os
import time
import requests
import subprocess
import pyautogui
import cv2
import numpy as np
from bs4 import BeautifulSoup
# ❌ 비활성화됨: DDGS 사용 불가
DDGS = None  # 대체 객체 설정

DOWNLOADS_DIR = "downloads"
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

class AIWebMacroAgent:
    def __init__(self):
        self.search_engine = "duckduckgo"

    def search_file_url(self, keyword: str) -> str:
        print('[비활성화] DDGS 검색 생략')
        return None
        return ddgs.text(query, max_results=5)
        for r in results:
            if any(ext in r['href'] for ext in ['.exe', '.zip', '.msi']):
                return r['href']
        return None

    def download_file(self, url: str, filename: str = None) -> str:
        filename = filename or url.split("/")[-1]
        file_path = os.path.join(DOWNLOADS_DIR, filename)
        try:
            with requests.get(url, stream=True, timeout=30) as r:
                with open(file_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
            return file_path
        except Exception as e:
            print(f"[❌] 다운로드 실패: {e}")
            return None

    def run_installer(self, filepath: str):
        print(f"[⚙️] 설치 파일 실행 중: {filepath}")
        try:
            subprocess.Popen(filepath)
            time.sleep(5)  # 설치 창 뜰 때까지 대기
        except Exception as e:
            print(f"[❌] 실행 실패: {e}")

    def wait_and_click_image(self, image_path: str, timeout: int = 20):
        print(f"[🖼] 이미지 서치: {image_path}")
        start = time.time()
        while time.time() - start < timeout:
            screenshot = pyautogui.screenshot()
            screen_np = np.array(screenshot)
            screen_gray = cv2.cvtColor(screen_np, cv2.COLOR_BGR2GRAY)

            template = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            res = cv2.matchTemplate(screen_gray, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(res)

            if max_val > 0.8:
                pyautogui.click(max_loc[0] + 10, max_loc[1] + 10)
                print(f"[✅] 클릭 완료: {image_path}")
                return True
            time.sleep(1)
        print(f"[❌] 시간 초과: 이미지 찾지 못함")
        return False

    def install_tool(self, tool_name: str):
        print(f"[🔍] 설치 대상 검색: {tool_name}")
        url = self.search_file_url(tool_name)
        if not url:
            print(f"[❌] 설치 파일 URL을 찾지 못했습니다.")
            return

        file_path = self.download_file(url)
        if not file_path:
            print(f"[❌] 파일 다운로드 실패")
            return

        self.run_installer(file_path)
        print(f"[🧠] 사용자 선택 확인을 위해 이미지 자동 클릭을 시도할 수 있습니다.")