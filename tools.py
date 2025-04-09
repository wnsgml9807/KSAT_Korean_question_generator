# math_server.py
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from typing import Literal, Dict, List, Any, Union
import logging
import codecs
import json
import os
import re

# ChromaDB가 최신 sqlite3를 사용하도록 설정
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logging.getLogger('sse_starlette').setLevel(logging.INFO)

# --- 임시 파일 경로 정의 ---
TEMP_PASSAGE_DIR = os.path.join("DB", "temp")
TEMP_PASSAGE_FILE = os.path.join(TEMP_PASSAGE_DIR, "latest_passage.json")

# --- 임시 디렉토리 생성 ---
os.makedirs(TEMP_PASSAGE_DIR, exist_ok=True)


async def prompt_for_suneung_writing() :
    """수능 지문 작성 시 공통 참고사항"""
    prompt = """
1. 수식이 들어가면 안 돼.
2. 새로운 개념을 제시할 때는 반드시 사전에 정의하기.
3. 각 문단이 유기적으로 연결되도록 작성하고, 글의 전체 구조가 하나의 흐름을 이루도록 작성하기.
4. 쉬운 언어로 설명하되, 논리적으로 풀어 써야 해.
5. 개념을 얕고 넓게 설명하기보다는, 깊고 좁게 설명하기.
6. 첫 문단은 이후 이어질 글의 방향성을 암시하는 것이 좋아.
7. 영어를 비롯한 외래어는 최소화하기    
8. 최대 2000자를 넘지 않도록 작성하기
    """
    return prompt

async def structure_for_suneung_writing() :
    """수능 지문에서 자주 사용되는 글의 구조"""
    prompt = """
1. 기술적/철학적/사회적/법적/경제적 문제를 제시하고 그것을 해결해 나가는 구조
2. 철학적 논란 및 질문을 제시하고 여러 인물들의 관점을 비교하는 구조.
3. 특정 현상이나 기계의 작동 과정을 단계적으로 설명하는 구조
4. 두 가지 이론이나 기술, 주장, 법률 등의 공통점과 차이점을 비교 분석하는 구조.
5. 위에서 언급한 구조를 조합하여 사용하는 구조.
    """
    return prompt

async def prompt_for_technology_subject() :
    """수능 기술 지문 작성 시 참고사항"""
    prompt = """
1. 수식이 들어가면 안 돼.
2. 새로운 개념을 제시할 때는 반드시 정의하기.
3. 쉬운 언어로 설명하되, 논리적으로 풀어 써야 해.
4. 개념을 얕고 넓게 설명하기보다는, 깊고 좁게 설명하기.
5. 단순히 개념을 나열하기보다는 특정 문제를 해결하는 과정이나 작동 과정을 단계적으로 설명하기.
6. 영어를 비롯한 외래어는 최소화하기
    """
    return prompt

async def prompt_for_humanities_subject() :
    """수능 인문 지문 작성 시 참고사항"""
    prompt = """
1. 서양/동양의 인문/철학 주제 중 하나를 선택
2. 새로운 개념을 제시할 때는 반드시 정의하기.
3. 쉬운 언어로 설명하되, 논리적으로 풀어 써야 해.
4. 특정 주제에 대한 여러 인물 간의 주장을 비교하는 것이 좋아.
5. 인물들이 너무 많아선 안되고, 쵣대 3명의 인물의 각 관점을 심도 있게 비교하는 것이 좋아.
6. 영어를 비롯한 외래어는 최소화하기
    """
    return prompt

async def generate_passage(passage: str) -> str :
    """지문 작성 시 반드시 이 함수를 통해 지문 출력해.
    첫 줄에는 지문 제목을 붙여줘.
    문단 바꾸기를 할 때에는 줄 바꿈을 해 줘."""
    
    # 단순 포맷팅 후 반환 (임시 파일 저장 로직 제거)
    lines = passage.strip().split('\n')
    title = lines[0] if lines else "제목 없음"
    content_body = '\n'.join(lines[1:]) if len(lines) > 1 else ""
    formatted_passage_output = f"{title}\n{content_body}" 
    
    return formatted_passage_output

async def generate_question(questions: str) -> str :
    """문제를 작성 시 반드시 이 함수를 통해 출력해. 표준 마크다운 형식을 사용해줘. 지문은 포함하지 말고 문제만 출력해.
    1.  질문(1. 윗글에 대한~)은 **볼드체**로 표시해줘.
    2.  각 선지(①~⑤)는 마크다운 인용(>) 형식으로 표시해줘.
    3.  <보기>가 포함된 경우:내용을 헤더 없는 1열 마크다운 테이블 안에 !볼드 없이! 넣어줘. 보기 내용 안에서 줄바꿈이 필요하면 HTML `<br>`태그를 사용해줘.
        예시:
        | <보기> 	|
        |---	|
        | 내용 |
        
    4.  질문과 첫 번째 선지/보기 테이블 사이, 그리고 각 문제 사이에는 **빈 줄 하나(\n\n)**를 넣어줘.
    5.  선지 등 테이블 외부의 텍스트 줄 끝에는 (빈 줄 제외) **스페이스 두 개**를 추가하여 줄바꿈(\n)을 명확히 해줘."""

    raw_questions = f'{questions}'.strip()

    # --- 후처리: 줄 끝 스페이스 추가 (테이블 외부용) ---
    processed_lines = []
    # 테이블 내부에도 스페이스가 추가될 수 있으나, <br> 사용 시 큰 문제 없을 것으로 예상
    for line in raw_questions.split('\n'):
        if line.strip(): 
            processed_lines.append(line + "  ") 
        else:
            processed_lines.append(line) 
            
    formatted_questions = '\n'.join(processed_lines)
    # ----------------------------------------------------

    # <보기> 테이블 변환 후처리 로직 없음 (AI 생성 의존)

    return formatted_questions
    
async def retrieve_data(query: str, type: Literal["question", "answer"]) -> Dict[str, Any]:
    """수능 문제와 해설 기출 DB에서 검색"""
    client = chromadb.PersistentClient(path="Agent/DB/kice")

    embedding = SentenceTransformerEmbeddingFunction(model_name="paraphrase-multilingual-mpnet-base-v2")
    collection = client.get_collection(
        name = 'kice_database',
        embedding_function=embedding)
    results = collection.query(
        query_texts=query,
        n_results=1,
        where={"type": type}
    )
    
    # 로깅 추가 (디버깅용)
    logger.debug(f"검색 결과 처리 완료: {len(results.get('documents', [[]])[0]) if 'documents' in results else 0}개 문서")

    doc_index = results.get('ids', [[]])[0]
    doc = results.get('documents', [[]])[0]
    if type == "question":  
        result = f"""
[검색어]
{query}
[검색 결과]
index: {doc_index}
content: {doc}"""
    else:
        result = f"""
[검색어]
{query}
[검색 결과]
index: {doc_index}
content: {doc}"""
    return result
