
# duckduckgo_search.py - Mocked fallback version
# 실제 duckduckgo_search 패키지 대체용 로컬 버전

class DDGS:
    def __init__(self):
        pass

    def text(self, query, max_results=5):
        # 모의 데이터 반환
        return [
            {"title": f"Test Result {i+1}", "href": f"https://example.com/{i+1}", "body": f"Summary for result {i+1}"}
            for i in range(max_results)
        ]

    def images(self, query, max_results=3):
        return [
            {"title": f"Image {i+1}", "image": f"https://img.example.com/{i+1}.jpg"}
            for i in range(max_results)
        ]

    def videos(self, query, max_results=2):
        return [
            {"title": f"Video {i+1}", "url": f"https://video.example.com/{i+1}"}
            for i in range(max_results)
        ]
