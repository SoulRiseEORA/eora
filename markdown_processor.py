#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EORA AI 마크다운 처리기
API 응답을 마크다운으로 포맷팅하여 보기 좋게 출력
"""

import re
import html
from typing import Dict, Any


class MarkdownProcessor:
    """마크다운 처리 및 포맷팅 클래스"""
    
    def __init__(self):
        self.markdown_patterns = {
            # 굵은 글씨 패턴
            'bold': [
                (r'\*\*(.*?)\*\*', r'<strong>\1</strong>'),
                (r'__(.*?)__', r'<strong>\1</strong>'),
            ],
            # 이탤릭 패턴
            'italic': [
                (r'\*(.*?)\*', r'<em>\1</em>'),
                (r'_(.*?)_', r'<em>\1</em>'),
            ],
            # 코드 블록 패턴
            'code_block': [
                (r'```(.*?)\n(.*?)```', r'<pre><code class="language-\1">\2</code></pre>'),
                (r'```(.*?)```', r'<pre><code>\1</code></pre>'),
            ],
            # 인라인 코드 패턴
            'inline_code': [
                (r'`(.*?)`', r'<code>\1</code>'),
            ],
            # 헤더 패턴
            'headers': [
                (r'^### (.*?)$', r'<h3>\1</h3>'),
                (r'^## (.*?)$', r'<h2>\1</h2>'),
                (r'^# (.*?)$', r'<h1>\1</h1>'),
            ],
            # 리스트 패턴
            'lists': [
                (r'^- (.*?)$', r'<li>\1</li>'),
                (r'^\* (.*?)$', r'<li>\1</li>'),
                (r'^\+ (.*?)$', r'<li>\1</li>'),
                (r'^\d+\. (.*?)$', r'<li>\1</li>'),
            ],
            # 링크 패턴
            'links': [
                (r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank">\1</a>'),
            ],
            # 줄바꿈 패턴
            'line_breaks': [
                (r'\n\n+', r'</p><p>'),  # 빈 줄은 문단 구분
                (r'\n', r'<br>'),        # 일반 줄바꿈은 <br>
            ]
        }
    
    def process_markdown(self, text: str) -> str:
        """마크다운 텍스트를 HTML로 변환"""
        if not text:
            return ""
        
        # HTML 특수문자 이스케이프 (마크다운 처리 전)
        processed = html.escape(text)
        
        # 코드 블록 먼저 처리 (다른 마크다운과 충돌 방지)
        for pattern, replacement in self.markdown_patterns['code_block']:
            processed = re.sub(pattern, replacement, processed, flags=re.DOTALL | re.MULTILINE)
        
        # 인라인 코드 처리
        for pattern, replacement in self.markdown_patterns['inline_code']:
            processed = re.sub(pattern, replacement, processed)
        
        # 굵은 글씨 처리
        for pattern, replacement in self.markdown_patterns['bold']:
            processed = re.sub(pattern, replacement, processed)
        
        # 이탤릭 처리
        for pattern, replacement in self.markdown_patterns['italic']:
            processed = re.sub(pattern, replacement, processed)
        
        # 헤더 처리
        for pattern, replacement in self.markdown_patterns['headers']:
            processed = re.sub(pattern, replacement, processed, flags=re.MULTILINE)
        
        # 링크 처리
        for pattern, replacement in self.markdown_patterns['links']:
            processed = re.sub(pattern, replacement, processed)
        
        # 줄바꿈 및 문단 처리
        processed = f"<p>{processed}</p>"
        for pattern, replacement in self.markdown_patterns['line_breaks']:
            processed = re.sub(pattern, replacement, processed)
        
        # 리스트 처리 (줄바꿈 후에)
        processed = self._process_lists(processed)
        
        # 빈 문단 제거
        processed = re.sub(r'<p></p>', '', processed)
        processed = re.sub(r'<p>\s*</p>', '', processed)
        
        return processed.strip()
    
    def _process_lists(self, text: str) -> str:
        """리스트 항목들을 적절한 ul/ol 태그로 감싸기"""
        lines = text.split('<br>')
        result_lines = []
        in_list = False
        list_items = []
        
        for line in lines:
            line = line.strip()
            
            # 리스트 항목 감지
            if re.match(r'^<li>', line):
                if not in_list:
                    in_list = True
                    list_items = []
                list_items.append(line)
            else:
                if in_list:
                    # 리스트 종료 - ul 태그로 감싸기
                    result_lines.append('<ul>')
                    result_lines.extend(list_items)
                    result_lines.append('</ul>')
                    in_list = False
                    list_items = []
                
                if line:  # 빈 줄이 아닌 경우만 추가
                    result_lines.append(line)
        
        # 마지막에 리스트가 열려있다면 닫기
        if in_list:
            result_lines.append('<ul>')
            result_lines.extend(list_items)
            result_lines.append('</ul>')
        
        return '<br>'.join(result_lines)
    
    def format_response(self, content: str, response_type: str = "chat") -> Dict[str, Any]:
        """응답을 포맷팅하여 반환"""
        
        # 마크다운 처리
        formatted_content = self.process_markdown(content)
        
        # 응답 객체 생성
        response = {
            "content": content,           # 원본 텍스트
            "formatted_content": formatted_content,  # HTML 포맷팅된 텍스트
            "response_type": response_type,
            "has_markdown": self._has_markdown_elements(content),
            "metadata": {
                "word_count": len(content.split()),
                "line_count": len(content.split('\n')),
                "has_code": '`' in content or '```' in content,
                "has_lists": bool(re.search(r'^[-*+]\s', content, re.MULTILINE)),
                "has_headers": bool(re.search(r'^#{1,6}\s', content, re.MULTILINE))
            }
        }
        
        return response
    
    def _has_markdown_elements(self, text: str) -> bool:
        """텍스트에 마크다운 요소가 있는지 확인"""
        markdown_indicators = [
            r'\*\*.*?\*\*',    # 굵은 글씨
            r'__.*?__',        # 굵은 글씨
            r'\*.*?\*',        # 이탤릭
            r'_.*?_',          # 이탤릭
            r'`.*?`',          # 코드
            r'```.*?```',      # 코드 블록
            r'^#{1,6}\s',      # 헤더
            r'^[-*+]\s',       # 리스트
            r'^\d+\.\s',       # 번호 리스트
            r'\[.*?\]\(.*?\)', # 링크
        ]
        
        for pattern in markdown_indicators:
            if re.search(pattern, text, re.MULTILINE | re.DOTALL):
                return True
        
        return False
    
    def create_beautiful_response(self, content: str, title: str = None) -> str:
        """아름다운 응답 형식 생성"""
        formatted = self.process_markdown(content)
        
        # 응답 래퍼
        if title:
            formatted = f"""
            <div class="eora-response">
                <div class="response-title">
                    <h3>{html.escape(title)}</h3>
                </div>
                <div class="response-content">
                    {formatted}
                </div>
            </div>
            """
        else:
            formatted = f"""
            <div class="eora-response">
                <div class="response-content">
                    {formatted}
                </div>
            </div>
            """
        
        return formatted.strip()


# 전역 마크다운 프로세서 인스턴스
markdown_processor = MarkdownProcessor()


def format_api_response(content: str, response_type: str = "chat", title: str = None) -> Dict[str, Any]:
    """API 응답 포맷팅 함수"""
    return markdown_processor.format_response(content, response_type)


def process_markdown_text(text: str) -> str:
    """마크다운 텍스트 처리 함수"""
    return markdown_processor.process_markdown(text)


def create_beautiful_response(content: str, title: str = None) -> str:
    """아름다운 응답 생성 함수"""
    return markdown_processor.create_beautiful_response(content, title) 