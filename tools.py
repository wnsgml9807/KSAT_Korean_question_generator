# math_server.py
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from typing import Literal, Dict, List, Any, Union
import logging
import codecs
import json
import os
import re

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

async def subject_for_humanities() :
    """인문 주제 선정 메뉴얼"""
    prompt = """
1. 인문 지문은 특정 주제에 대한 다양한 인물들의 관점을 심도있게 비교하는 것이 좋아.
2. 심리학/철학/사회학/인문학 등 다양한 분야의 소재를 검토해 줘.
3. 너무 피상적이지 않은 주제를 선택하지 않는 게 좋아.
     나쁜 예시 : 심리학 종류 구분, 서양 철학과 동양 철학 특징 비교, 유명한 사회학자 소개
     좋은 예시 :
     (철학/윤리학) 칸트의 의무론적 윤리설과 밀의 공리주의적 윤리설이 특정 행위(예: 선의의 거짓말, 안락사)의 정당성을 판단하는 기준을 비교 분석. (특정 행위에 대한 두 관점 비교)
     (심리학) 특정 심리 현상(예: 확증 편향, 방관자 효과)의 원인과 결과에 대한 행동주의 심리학(스키너 등)과 인지 심리학의 설명을 비교. (특정 현상에 대한 두 학파 비교)
     (사회/정치철학) 사회 계약론에서 홉스와 로크가 제시하는 자연 상태의 개념과 국가 권력의 정당성 근거를 비교 분석. (특정 이론 내 핵심 개념 비교)
     (미학) 예술 작품의 가치 판단 기준으로 '형식'을 강조하는 형식주의 미학(클라이브 벨 등)과 '사회적 맥락'을 중시하는 마르크스주의 미학의 관점을 비교. (특정 대상에 대한 두 관점 비교)
     (역사/사상) 특정 역사적 사건(예: 프랑스 혁명)에 대한 보수주의적 해석(에드먼드 버크 등)과 진보주의적 해석의 차이점을 비교. (특정 사건에 대한 두 관점 비교)
    """
    return prompt

async def subject_for_technology() :
    """기술 주제 선정 및 작성 지침"""
    prompt = """
1.  기술 지문은 특정 알고리즘이나 기계장치의 **작동 과정**을 **단계적으로 설명**하는 것이 핵심입니다.
2.  각 설명 단계는 이전 단계의 결과나 상태를 바탕으로 **유기적으로 연결**되어야 합니다.
3.  단순히 각 단계를 나열하는 것을 넘어, 구성 요소들이 어떻게 **복잡하게 상호작용**하는지 그 **메커니즘**을 설명해야 합니다.
4.  컴퓨터 알고리즘의 경우, **분기문(if-else), 반복문(for, while), 재귀 호출, 조건 처리** 등 논리적 흐름을 명확히 보여주어 적절한 난이도를 확보할 수 있습니다.
5.  **수식이나 복잡한 수학적 기호는 절대 사용하지 마세요.** 원리 설명에 필요한 경우, 단어 또는 쉬운 비유로 풀어 설명해야 합니다.
6.  '엔트로피', '임피던스' 와 같이 배경지식 없이는 이해하기 어려운 **전문 용어는 피하거나, 반드시 쉬운 언어로 정의 또는 비유**를 통해 설명해야 합니다. 전반적으로 **쉬운 단어와 명확한 문장**으로 작성되어야 합니다.
7.  **좋은 예시:**
    *   검색 엔진의 웹 페이지 순위 결정 과정 (크롤링-인덱싱-랭킹 알고리즘 단계 및 상호작용 설명)
    *   GPS의 위치 측정 원리 (여러 위성 신호 수신, 거리 계산, 삼각 측량, 오차 보정 과정 설명)
    *   특정 데이터 압축 알고리즘(예: 런-렝스 부호화, 허프만 코딩)의 작동 방식 (데이터 분석, 변환 규칙 적용, 부호화/복호화 단계 설명)
    *   디지털 카메라 이미지 센서(CCD 또는 CMOS)의 빛 처리 및 디지털 신호 변환 과정 설명
    *   특정 유형의 3D 프린터(예: FDM 방식) 작동 원리 (모델링 데이터 슬라이싱, 노즐 이동 및 재료 압출, 레이어 적층 과정 설명)
8.  **나쁜 예시:**
    *   다양한 인공지능 기술의 종류와 발전 역사 (작동 과정 설명 부족)
    *   최신 스마트폰의 기능 나열 및 소개 (메커니즘 설명 부족)
    *   컴퓨터 하드웨어 부품(CPU, RAM, GPU 등)의 역할 설명 (상호작용 메커니즘 부족)
    *   네트워크 프로토콜(TCP/IP) 계층 구조 설명 (각 계층의 상세 작동 과정 없이 구조만 나열)
    """
    return prompt

async def retrieve_data(query: str, type: Literal["question", "answer"]) -> Dict[str, Any]:
    """수능 문제와 해설 기출 DB에서 검색, 검색은 지문에 들어있는 키워드를 검색할 수 있어.(예:인공지능)"""
    client = chromadb.PersistentClient(path="DB/kice")

    embedding = SentenceTransformerEmbeddingFunction()
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
    doc = "\n".join(doc[0].split('\n'))
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
