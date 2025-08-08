
import requests
import urllib.parse
import openai
import platform

class WebSearcher:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }

    def search_install_file(self, keyword: str) -> list:
        query = f"{keyword} filetype:exe OR filetype:zip OR filetype:msi"
        return self._ddg_links(query)

    def search_error_fix(self, error_message: str) -> list:
        query = f"python error fix {error_message}"
        return self._ddg_links(query)

    def _ddg_links(self, query: str) -> list:
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

def web_search_solution(item: str, is_error=False) -> str:
    """
    error 또는 설치항목 item을 검색 후 GPT로 결과 확인 → 정확한 링크 반환
    """
    searcher = WebSearcher()
    results = searcher.search_error_fix(item) if is_error else searcher.search_install_file(item)
    search_type = "오류" if is_error else "설치파일"

    context = f"{search_type} 관련 검색어: '{item}'\n검색결과 상위 5개 URL:\n"
    for i, r in enumerate(results):
        context += f"{i+1}. {r}\n"

    system_info = platform.system() + " " + platform.machine()

    gpt_prompt = (
        f"아래는 사용자의 {search_type} 관련 웹검색 결과입니다. "
        f"당신은 개발 도우미로서 이 검색결과 중 어떤 링크를 열고 설치하거나 참고하면 가장 좋을지 추천해줘. "
        f"설치 시 사용자 컴퓨터 환경({system_info})과 일치하는지 확인해줘.\n\n{context}"
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": gpt_prompt},
                {"role": "user", "content": f"가장 신뢰할 수 있고 설치가능성이 높은 링크를 추천해줘"}
            ],
            temperature=0.4
        )
        gpt_answer = response['choices'][0]['message']['content']
        return f"🔍 GPT 확인 결과:\n{gpt_answer}"
    except Exception as e:
        return f"[❌ GPT 응답 실패]\n{e}"
