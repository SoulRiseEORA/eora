import requests
import json

def test_prompt_api():
    base_url = "http://127.0.0.1:8001"
    
    print("=== 프롬프트 API 테스트 ===")
    
    # 1. 프롬프트 목록 조회
    print("\n1. 프롬프트 목록 조회")
    try:
        response = requests.get(f"{base_url}/api/prompts")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            prompts = response.json()
            print(f"총 프롬프트 수: {len(prompts)}")
            
            # AI별로 그룹화하여 출력
            ai_groups = {}
            for prompt in prompts:
                ai_name = prompt.get('ai_name', 'unknown')
                category = prompt.get('category', 'unknown')
                if ai_name not in ai_groups:
                    ai_groups[ai_name] = {}
                if category not in ai_groups[ai_name]:
                    ai_groups[ai_name][category] = []
                ai_groups[ai_name][category].append(prompt)
            
            for ai_name, categories in ai_groups.items():
                print(f"\n{ai_name.upper()}:")
                for category, category_prompts in categories.items():
                    print(f"  {category}: {len(category_prompts)}개")
                    for i, prompt in enumerate(category_prompts[:2]):  # 처음 2개만 출력
                        content_preview = prompt.get('content', '')[:100]
                        print(f"    {i+1}. {content_preview}...")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # 2. ai1 system 프롬프트 확인
    print("\n2. AI1 System 프롬프트 확인")
    try:
        response = requests.get(f"{base_url}/api/prompts")
        if response.status_code == 200:
            prompts = response.json()
            ai1_system = [p for p in prompts if p.get('ai_name') == 'ai1' and p.get('category') == 'system']
            if ai1_system:
                print(f"AI1 System 프롬프트 수: {len(ai1_system)}")
                for i, prompt in enumerate(ai1_system):
                    content = prompt.get('content', '')
                    print(f"  {i+1}. 길이: {len(content)} 문자")
                    print(f"     내용 미리보기: {content[:200]}...")
            else:
                print("AI1 System 프롬프트를 찾을 수 없습니다.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_prompt_api() 