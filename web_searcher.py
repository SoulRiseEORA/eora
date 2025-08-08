
import requests
import urllib.parse

class WebSearcher:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }

    def search_install_file(self, keyword: str) -> list:
        """
        설치파일을 DuckDuckGo 기반으로 검색합니다.
        :param keyword: 예) pyinstaller installer download
        :return: 링크 리스트
        """
        query = f"{keyword} filetype:exe OR filetype:zip OR filetype:msi"
        return self._ddg_links(query)

    def search_error_fix(self, error_message: str) -> list:
        """
        오류 메시지로 해결 링크 검색
        """
        query = f"python error fix {error_message}"
        return self._ddg_links(query)

    def _ddg_links(self, query: str) -> list:
        """
        DuckDuckGo 웹 검색 링크 추출
        """
        try:
            base = "https://html.duckduckgo.com/html/"
            response = requests.post(base, data={"q": query}, headers=self.headers, timeout=10)
            results = []
            for line in response.text.split("\n"):
                if 'class="result__url"' in line:
                    start = line.find('href="') + 6
                    end = line.find('"', start)
                    url = line[start:end]
                    if url.startswith("http"):
                        results.append(urllib.parse.unquote(url))
            return results[:5]
        except Exception as e:
            return [f"[❌ 검색 실패]: {e}"]

def web_search_solution(error_text: str) -> str:
    searcher = WebSearcher()
    results = searcher.search_error_fix(error_text)
    return results[0] if results else '[❌ 해결 링크 없음]'
