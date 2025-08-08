from prometheus_client import start_http_server, Histogram, Counter

# GPT 응답 지연 시간 히스토그램
RESPONSE_LATENCY = Histogram(
    'aura_response_latency',
    'GPT 응답 시간',
    ['model']
)
# 메모리 회상 쿼리 카운터
MEMORY_QUERY = Counter(
    'memory_query_count',
    '회상 쿼리 횟수'
)

def start_metrics_server(port=8000):
    start_http_server(port)
