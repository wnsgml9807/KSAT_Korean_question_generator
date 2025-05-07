---
marp: true
---

# KSAT Agent
_Multi-Agent 기반 수능 국어 독서 영역 출제 자동화 시스템_

```
제작자 : 권준희
소속 : 연세대학교 교육학과
ver 0.6.0 (05.07)
- 개념 지도 기반 passage_editor 전용 파인튜닝 모델 탑재
- 주제 선택 전문 에이전트 subject_collector 탑재
- Docker 이미지 생성 + Google Cloud Platform 서버 구축
```
<br>

<div align="center">
  <h3> 직접 사용해 보세요 ✨</h3>
  <a href="https://ksat-generator-kjh7207.streamlit.app/" target="_blank">
    <img src="https://img.shields.io/badge/KSAT_Agent_실행하기-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="KSAT Agent 실행하기" width="300"/>
  </a>
  <p><i>버튼을 클릭하면 데모 앱 링크로 이동합니다. 🚀</i></p>
</div>
<br>

---

### 1️⃣ 개요

수능 국어, 특히 독서 지문의 출제에는 상당한 시간과 비용이 필요합니다.

KSAT Agent는 고품질의 수능 국어 독서 지문 세트를 **약 10분 안에** 완성하여 제공할 수 있습니다.

사용자는 AI와 함께 원하는 주제를 섬세하게 결정한 후, 나머지 출제 과정은 AI 에이전트들이 분담하여 처리합니다.

---

### 2️⃣ 효과성

기존 출제 프로세스를 크게 단축하고, 상당한 비용을 절감할 수 있습니다.

##### 기존 출제 프로세스

| 기존 출제 과정 | 주요 문제점 |
|----------------|------------|
| **출제 기간** | 초안 작성 → 검토 → 수정이 반복되어 1~2개월의 시간을 필요로 합니다. |
| **높은 출제 비용** | 지문 세트당 백만 원 이상의 높은 원고료를 지불해야 합니다. |
| **서면 위주 의사소통** | 출제자와 검토자가 분리되어 있는 구조로 인해, 의견 교환에 제한이 있고 즉각적인 피드백이 어렵습니다. |


##### KSAT Agent 활용 시

| 항목 | 기존 | KSAT Agent 사용 시 |
|------|---------|--------------------|
| **소요 시간** | 1 ~ 2 개월 | **10 분** |
| **비용** | 100~200만 원 | **500 원** (평균 사용량 기준) |
| **의사소통** | 서면 피드백 반복 | 기출 분석과 최신 경향을 학습한 AI와 **실시간 대화** |

---

### 3️⃣ 에이전트 구조

#### 핵심 아이디어

1. **역할 분담** – '주제선정·탐색·설계·집필·출제·검증·총괄' 각 단계를 전문화된 AI가 전담합니다.
2. **순환 검토** – 검증 단계에서 오류를 발견하면 이전 단계로 피드백하여 전체 일정을 단축합니다.
3. **대화형 인터페이스** – 사용자는 채팅 한 줄로 주제를 입력하고, 진행 상황과 결과를 실시간으로 확인합니다.


#### 에이전트 역할 요약

| 단계 | 에이전트 | 사용 모델 | 주요 업무 |
|------|----------|----------|-----------|
| **사용자 입력** | 사용자 | - | 초기 주제 및 요구사항 전달 |
| **주제 구체화** | Subject Collector | GPT-4.1 | 사용자 의도 파악 및 상세 주제/서술 구조 확정 |
| **총괄 조정** | Supervisor | GPT-4.1 | 전체 절차 지휘 및 에이전트 간 작업 조율 |
| **연구 분석** | Researcher | Gemini-2.5 Flash | 기출 지문 검색/분석, 관련 자료 수집 및 요약 |
| **구조 설계** | Architecture | Claude-3.7 | 개념 지도 초안 작성, 문단 배치 및 논리 흐름 설계 |
| **지문 집필** | Passage Editor | GPT-4.1 (파인튜닝) | 설계안 기반 지문 집필, 개념 지도 구현 |
| **문항 출제** | Question Editor | Gemini-2.5 Flash | 5지선다 문항 작성 및 선지 변별력 확보 |
| **검증** | Validator | Gemini-2.5 Flash | 지문/문항의 일관성, 논리 오류, 난이도 등 종합 검토 및 피드백 |
| **최종 결과물** | 시스템 | - | 완성된 지문, 문항, 해설 세트 |

*Validator가 "통과" 판정을 내리면 작업이 종료됩니다. Validator의 피드백에 따라 Supervisor는 이전 단계의 에이전트에게 재작업을 지시할 수 있습니다.


#### 작업 흐름

```mermaid
flowchart TD
    %% Supervisor 중심 워크플로우 (단방향 흐름)
    
    S["Supervisor"]:::super
    
    H(["Human Input"]):::user
    R["Researching"]:::research
    W["Writing"]:::edit
    V["Validating"]:::valid
    F(["Finish"]):::result
    
    H --> S
    S --> R
    R --> W
    W --> V
    V --> F
    
    %% Supervisor 연결
    S <-.-> R
    S <-.-> W
    S <-.-> V
    S <-.-> F
    
    %% 스타일링
    classDef user fill:#cce5ff,stroke:#0066cc,stroke-width:1px
    classDef super fill:#ffe6cc,stroke:#ff9933,stroke-width:2px,color:#ff6600,font-weight:bold
    classDef research fill:#e6ffcc,stroke:#66cc33,stroke-width:1px
    classDef edit fill:#f9ddff,stroke:#cc66ff,stroke-width:1px
    classDef valid fill:#e6e6ff,stroke:#6666ff,stroke-width:1px
    classDef result fill:#f2f2f2,stroke:#666666,stroke-width:1px
```

---

### 4️⃣ 세부 기술 구현

#### 프로젝트 구조

```
KSAT Agent/
├── frontend/               # Streamlit 기반 웹 인터페이스 (Git 관리, Streamlit Cloud 배포)
│   ├── pages/
│   │   └── about.py        # 프로젝트 소개 페이지
│   ├── app_main.py         # 메인 앱 진입점
│   ├── requirements.txt    # Frontend 의존성 (Streamlit Cloud용)
│   └── .streamlit/         # Streamlit 설정 (필요시)
│
├── backend/                # 멀티 에이전트 시스템 코어 (Git 관리)
│   ├── DB/                 # 데이터베이스 (ChromaDB, SQLite)
│   ├── agent_server.py     # FastAPI 서버 진입점
│   ├── graph_factory.py    # LangGraph 워크플로우
│   ├── agents_prompt/      # 에이전트별 프롬프트
│   ├── tools.py            # 에이전트 공용 도구
│   ├── handoff_tools.py    # 에이전트 핸드오프 도구
│   ├── model_config.py     # LLM 모델 설정
│   ├── Dockerfile          # Backend Docker 이미지 빌드용
│   ├── docker-compose.yaml # Docker Compose 설정
│   ├── supervisord.conf    # Supervisor 설정
│   └── requirements.txt    # Backend 의존성
│  
└── Parser/                 # (참고: 기출 문제 분석 및 데이터 전처리 로직 - Git 관리 범위 외)

```

#### 주요 기술 스택

| 영역 | 기술 | 용도 |
|------|------|------|
| **프론트엔드** | Streamlit | 사용자 인터페이스 및 실시간 진행상황 표시 |
| **백엔드** | FastAPI | API 서버 및 스트리밍 응답 처리 |
| **멀티에이전트** | LangGraph | 에이전트 간 상태 관리 및 워크플로우 |
| | LangChain | 메모리, 체인, 도구 활용 |
| **데이터베이스** | ChromaDB | 의미 검색 및 벡터 저장소 |
| | SQLite | 세션 상태 관리 및 체크포인트 |
| **LLM** | OpenAI GPT-4.1 | Supervisor 에이전트 |
| | Anthropic Claude-3.7 | Passage Editor 에이전트 |
| | Gemini-2.5 Flash | Researcher, Question Editor, Validator, Subject Collector 에이전트 |
| **임베딩** | OpenAI text-embedding-3 | 한국어 텍스트 벡터화 |
| **배포** | Docker, GCP (Google Cloud Platform) | Backend 서버 컨테이너화 및 클라우드 VM 배포 |
| | Streamlit Cloud | Frontend 웹 애플리케이션 배포 |
| **CI/CD** | GitHub Actions | 코드 변경 시 자동 빌드 및 배포 |

#### LangGraph 선택 배경

수능 지문 생성은 여러 단계의 복잡한 작업이 순차적으로 이루어져야 합니다. 초기에는 단일 LLM을 사용한 접근법도 고려했으나, 다음과 같은 한계에 직면했습니다:
```
1. 토큰 제한에 빠르게 도달 - 수능 지문 생성에 필요한 모든 지시와 컨텍스트가 16K 토큰을 쉽게 초과
2. 역할 혼란 - 하나의 모델이 연구자, 작가, 검토자 역할을 번갈아 수행하며 일관성 상실
3. 전문성 결여 - 전체 태스크를 한 번에 처리하려다 보니 각 단계별 품질이 저하
```
LangGraph는 이러한 문제들을 해결할 수 있는 최적의 프레임워크였습니다:

> **State 관리의 효율성** : LangChain의 단순 체인과 달리, LangGraph는 복잡한 상태를 그래프 노드 간에 유지하고 전달할 수 있어 여러 에이전트가 협업하기에 이상적입니다.
>
> **유연한 워크플로우** : 조건부 경로와 순환 가능한 그래프 구조를 통해 "검증 실패 → 재작업" 같은 복잡한 워크플로우를 자연스럽게 구현할 수 있습니다.
>
> **체크포인팅** : 내장된 체크포인트 기능을 활용하여, 장시간 실행 과정에서 발생할 수 있는 오류나 중단으로부터 상대적으로 안전하게 작업을 이어갈 수 있습니다. (본 프로젝트에서는 AsyncSqliteSaver를 사용)

```python
# graph_factory.py 중 일부
builder = StateGraph(MultiAgentState)

builder.add_node("subject_collector", subject_collector_agent) # 주제 구체화
builder.add_node("researcher", researcher_agent)
builder.add_node("architecture", architecture_agent)
# ... (다른 에이전트 노드 추가) ...
builder.add_node("validator", validator_agent)

builder.add_conditional_edges( # 검증 결과에 따른 분기
    "validator",
    lambda state: "architecture" if state.get("validation_result") == "rewrite_architecture" else
                 "passage_editor" if state.get("validation_result") == "rewrite_passage" else
                 "question_editor" if state.get("validation_result") == "rewrite_question" else
                 "END", # 최종 통과
    {"architecture": "architecture", "passage_editor": "passage_editor", "question_editor": "question_editor", "END": END}
)
graph = builder.compile(checkpointer=saver) # AsyncSqliteSaver 인스턴스 주입
```

#### LLM 모델 선택

각 태스크의 특성에 맞게 최적화된 LLM 모델을 사용했습니다.

실제 테스트 결과, Claude는 문체와 깊이 있는 내용 생성에 강점을 보였고, Gemini는 분석과 문항 생성의 속도에서 우위를 보였습니다.

이러한 모델 조합을 통해 품질과 비용 효율성 모두를 확보할 수 있었습니다.

| 에이전트 | 사용 모델 | 선택 이유 |
|---------|---------|----------|
| **Supervisor** | ```GPT-4.1``` | • 지시사항을 정확히 이해하고 따르는 능력(instruction following)이 탁월함<br>• 사용자 친화적인 어조로 소통하며 작업 흐름을 조율<br>• 복잡한 작업 흐름을 관리하는 능력이 뛰어남 |
| **Passage Editor** | ```Claude-3.7``` (파인튜닝 적용) | • 한국어 문체가 자연스럽고 수능 지문 스타일의 고품질 텍스트 생성<br>• 복잡한 개념도 논리적 구조를 유지하며 1,700자 내외로 압축하는 능력 탁월<br>• 내적 일관성이 높은 지문 작성 가능 |
| **Subject Collector, Researcher, Question Editor & Validator** | ```Gemini-2.5 Flash``` | • 빠른 응답 속도로 사용자 의도 파악, 지문 분석 및 문항 생성<br>• 수학적/논리적 관계 파악에 강점, 선지 간 변별력 체크에 효과적<br>• 비용 효율적이라 반복적 검증 및 다양한 탐색 과정에 적합 |

```python
# 예시: Passage Editor 에이전트 생성 (파인튜닝 모델 사용)
passage_editor_agent = create_react_agent(
    model="ft:gpt-4.1-ksat-agent-passage-editor-v2", # 파인튜닝된 모델 ID
    tools=passage_editor_tools,
    prompt=passage_prompt
)
```

#### 에이전트 간 작업 통제권 전환 메커니즘

초기 버전에서는 에이전트 간 전환을 위해 LangGraph의 조건부 엣지를 이용했습니다. 그러나 이는 다음과 같은 문제를 야기했습니다:

```
1. 확장성 한계 - 새 에이전트 추가 시, 분기 로직과 코드를 일일이 수정해야 함
2. 복잡한 상태 관리 - 누가 다음에 실행될지 추적하는 로직이 복잡해짐
3. 유연성 부족 - 실행 중 워크플로우 변경이 어려움
```

이를 해결하기 위해 Supervisor 에이전트가 다음 작업자를 명시적으로 호출하고, 호출된 에이전트는 자신의 역할을 수행 후 Supervisor에게 다시 제어권을 넘기는 방식을 채택했습니다. `handoff_to_supervisor` 도구를 사용하여 이 과정을 구현했습니다.

```python
# handoff_tools.py 일부
@tool
async def handoff_to_supervisor(
    # ... (매개변수 생략)
):
    """작업 완료 후 Supervisor에게 통제권을 넘깁니다."""
    # ... (메시지 생성 및 상태 업데이트 로직)
    return Command(goto="supervisor", ...) # Supervisor 노드로 이동
```

이 접근법의 장점은 Supervisor의 프롬프트와 판단 로직을 통해 워크플로우를 유연하게 관리할 수 있다는 점입니다.

#### ChromaDB 선택 이유와 임베딩 전략

LLM이 기출 문제를 능동적으로 검색할 수 있는 시스템을 구축하기 위해 여러 벡터 데이터베이스 옵션을 검토했습니다:

> 검토한 벡터 DB 후보:
> - Pinecone: 관리형 서비스, 확장성 우수
> - Milvus: 고성능 분산 처리 가능
> - ChromaDB: 경량화, 로컬 실행 가능, Python 통합 우수


최종적으로 ChromaDB를 선택한 이유는 다음과 같습니다:

1. **로컬 클라이언트**: 서버리스 환경에서도 SQLite 백엔드로 완전히 작동하여 외부 의존성 최소화. VM 환경에서 별도의 DB 서버 없이 파일 기반으로 운영 가능.
2. **메타데이터 필터링**: 연도, 월, 영역 등의 복합 필터링을 `where` 절로 간단히 구현 가능.
3. **임베딩 유연성**: 다양한 임베딩 모델을 쉽게 교체할 수 있는 아키텍처 지원.

한국어 텍스트 임베딩을 위해 여러 모델을 벤치마크한 결과, OpenAI의 `text-embedding-3-large`가 한글 수능 지문의 의미적 유사성을 가장 정확히 포착하는 것으로 확인되어 채택했습니다.

```python
# tools.py의 ChromaDB 검색 함수 예시
results = collection.query(
    query_texts=[query],
    n_results=n_results,
    where={"year": year, "field": field} # 메타데이터 필터링
)
```

#### 토큰 비용 관리

AI 모델의 컨텍스트 제한과 비용 문제를 해결하기 위해, 일반적으로 사용되는 요약 모델 접근법 대신 독창적인 "절삭+주입" 전략을 개발했습니다:

```python
# message_reducer.py의 메시지 절삭 로직 (개념)
# 실제 구현은 state['messages']를 직접 수정하거나, 훅(hook)을 통해 처리
def truncate_messages_for_llm(messages: list, max_tokens: int) -> list:
    """긴 메시지 목록을 LLM 입력 크기에 맞게 절삭합니다."""
    # ... (토큰 수 계산 및 절삭 로직)
    # 예: 최근 메시지 위주 보존, 시스템 메시지 보존, 중간 메시지 요약 또는 생략
    # 현재 프로젝트에서는 앞/뒤 일부만 남기는 방식을 사용함
    # if num_tokens(content) > TRUNCATE_THRESHOLD:
    #     truncated = content[:500] + "\n...[중략]...\n" + content[-500:]
    return processed_messages
```

이 접근법을 통해 얻은 이점:

1. **요약 모델 비용 절감**: 추가 LLM 호출 없이 단순 절삭으로 토큰 절약.
2. **중요 정보 보존**: 일반적으로 메시지의 앞부분(지시사항)과 뒷부분(최근 대화)에 중요 정보가 집중되어 있으므로, 이 부분을 유지.
3. **처리 지연 최소화**: 요약 모델 호출 대비 시간 절약.

실제 테스트에서 품질 저하 없이 토큰 사용량을 효과적으로 관리할 수 있었습니다.

---

### 5️⃣ 개념 지도

>개념 지도에 대한 상세한 설명은 부록을 참고 부탁드립니다.

#### 개념 지도 소개

교육 콘텐츠 평가에서 "논리 구조가 복잡하다"나 "정보 밀도가 높다"와 같은 표현은 주관적이고 정성적인 평가에 불과했습니다. 이로 인해 난이도와 정보 밀도의 조절이 출제자의 경험과 직관에 의존해야 했고, AI를 활용한 자동화 시스템 구축이 어려웠습니다.

KSAT Agent는 자체 개발한 **개념 지도**를 통해 이러한 정성적 평가를 정량화했습니다:

| 기능 | 기존 방식 | 개념 지도의 효과 |
|------|-----------|--------------------------------|
| 논리 구조 파악 | 전문가의 주관적 평가 | **엣지 타입·깊이**를 계량화 |
| 정보 밀도 판단 | 단순 글자수·문단수 | **노드 수 / 1천 token** 지표 |
| 선지 생성 근거 | 수작업 검색 | 그래프 경로 탐색 |

##### ① 예시 지문

> "촉매는 화학 반응의 활성화 에너지를 낮춰 반응 속도를 높입니다. 그러나 촉매 자체는 반응 전후에 변하지 않습니다."

##### ② 자동 추출된 그래프

| 노드 ID | 라벨 | 설명 |
|---------|------|------|
| N1 | Catalyst | 촉매 |
| N2 | ActivationEnergy | 활성화 에너지 |
| N3 | ReactionRate | 반응 속도 |

| 엣지 | 타입·레이블 | 의미 |
|------|-------------|------|
| N1→N2 | Causality · `influences` | 촉매가 에너지를 낮춤 |
| N2→N3 | Causality · `causes` | 낮아진 에너지가 속도 증가 초래 |
| N1→N1 | QuantComparison · `is_equal_to` | 촉매 전후 동일(자기 보존) |

이러한 정량적 지표를 통해 Question Editor는 "원인→결과→불변" 경로를 선지 패턴으로 활용할 수 있습니다.

이처럼 개념 지도는 논리 구조, 정보 밀도, 추론 경로를 객관적 수치로 변환하여, 개념 지도의 적용을 통해 에이전트에게 지문의 난이도와 정보 밀도를 정량적으로 주문할 수 있게 됩니다.

![개념 지도 예시](frontend/pages/image.png) 

---

### 6️⃣ 지문 작성용 LLM 파인튜닝

**Problem** 
> "본질적으로 '쉽고 직관적으로' 설명하도록 학습된 LLM 모델의 특성 상,
> 프롬프트만으로 정보의 밀도와 독해 난이도를 극적으로 향상시키기에는 한계가 있다고 느꼈다."

따라서 다음의 데이터 파이프라인을 구축하여 소규모 파인튜닝을 진행한 결과, 지문 퀄리티를 극적으로 향상시킬 수 있었다. (이 과정은 `Parser/` 및 별도 스크립트를 통해 진행)

| 구분 | 내용 |
|------|------|
| 학습 데이터 1 | LLM을 활용해 **기출 지문**에서 추출한 개념 지도 |
| 학습 데이터 2 | 기출 지문 원문 |

#### ① SFT 데이터셋 생성 파이프라인

| 단계               | 스크립트 (`Parser/` 및 관련 스크립트)        | 핵심 로직·함수                                                   | 산출물                                     |
| ---------------- | --------------------------------- | ---------------------------------------------------------- | --------------------------------------- |
| **1. 기출 txt 파싱** | `concept_map_converter.py` (가칭)   | `passage_parser()` 〈줄바꿈·특수 기호 정리〉                          | `passage` (*str*)                       |
| **2. 개념 지도 변환**  | `convert_concept_map_async()` (가칭) | Gemini-2.5-flash -> JSON (15 ± 5 노드)                       | `concept_map.json`                      |
| **3. JSONL 빌드**  | `training_data_generator_async()` (가칭) | 3-turn 메시지 샘플<br>`system→user(concept)→assistant(passage)` | `…training_dataset.jsonl`               |
| **4. 검증·Split**  | `data_validation_cli.py` (가칭)     | 토큰·포맷 검사 → 90 / 10 split                                   | `train.jsonl` (76) <br>`val.jsonl` (10) |

> *데이터 통계* : 전체 ≈ 12 만 tokens, 1 샘플 평균 1 500 tokens

---

#### ② Fine-Tune 설정 (OpenAI)


| 파라미터       | 값                                           | 비고             |
| ---------- | ------------------------------------------- | -------------- |
| Base model | `gpt-4.1-2025-04-14`                        | 2025-Q2 공개     |
| Epochs     | 3 (*auto*)                                  | 데이터 소량, 과적합 방지 |
| Batch / LR | auto / default                              |                |
| Run ID     | `ft:gpt-4.1-…:ksat-agent-passage-editor-v2` |                |

**결과 지표**

| Metric          | 값         |
| --------------- | --------- |
| Train loss      | **0.274** |
| Valid loss      | **0.255** |
| Full valid loss | 0.302     |

(loss gap ≈ 0.02 → 안정 수렴)

---

#### ③ Inference 파라미터 (안정 preset)

```python
gen_cfg = {
    "model": "ft:gpt-4.1-ksat-agent-passage-editor-v2",
    "temperature": 0.30,
    "top_p": 0.85,
    "repetition_penalty": 1.2,
    "max_tokens": 1200,
}
```

* `temperature 0.5` : 논리 일관성↑
* `top_p 0.85`      : 기본값에 비해 보수적으로 책정하여 문체 일관성↑
* `repetition_penalty 1.2` : 꼬리 반복 현상상 90 %↓

---

#### ④ 정량적 개선 결과

| 지표                 | 프롬프트 Only | Fine-Tune 후 | 개선폭    |
| ------------------ | --------- | ----------- | ------ |
| 단락별 "정의→인과→비교" 완성률 | 38 %      | **71 %**    | +33 %p |
| 매력적 오답(값·조건 교란) 비율 | 42 %      | **88 %**    | +46 %p |
| 중복·불필요 문장 비중       | 12 %      | **3 %**     | -9 %p  |
| 수능 전문가 총점(5점 만점)   | 3.0       | **4.5**     | +1.5   |

---

#### ⑤ 주요 이슈 & 해결책

| 이슈                                 | 해결 방법                                  |
| ---------------------------------- | -------------------------------------- |
| 동일 문장, 문단 반복                       | `repetition_penalty=1.2` + Top-k 노드 필터 |
| 이상한 문자열이 출력되는 현상                      | `temperature=0.6` 하향 조정 |

---

### 7️⃣ 서버 아키텍처

#### 7.1 다중 사용자 세션 관리

다중 사용자 환경에서 각 사용자의 작업 상태를 안전하게 관리하기 위해 세 가지 핵심 요소를 도입했습니다:

| 요소 | 사용 기술 | 주요 기능 |
|------|-----------|----------|
| **대화 상태** | `MultiAgentState` (`TypedDict`) | 에이전트 간 메시지·요약·검색 결과를 단일 객체로 공유 |
| **세션 DB** | `AsyncSqliteSaver` | Stream lit 다중 사용자 환경에서 세션별 체크포인트 유지 |
| **만료 정리** | `cleanup_old_sessions()` | 24 시간 후 SQLite 파일 자동 삭제로 디스크 사용 최소화 |

이를 통해 여러 사용자가 동시에 시스템을 사용해도 각 작업이 완전히 분리되어 관리되며, 

만약 작업 중 오류가 발생하더라도 서버 DB에 저장된 세션을 불러와 마지막 체크포인트부터 작업을 재개할 수 있습니다:

```python
# 각 사용자별 독립된 세션 데이터베이스 생성
memory = await aiosqlite.connect(f"sessions/{user_id}_{timestamp}.db")
saver  = AsyncSqliteSaver(memory)
await saver.setup()          # 필요한 테이블 자동 생성

# 중요 작업 단계마다 상태 스냅샷 저장
await saver.flush(state)     # 체크포인트 생성
```


#### 7.2 실시간 스트리밍 구현

작업 시간이 5-10분 정도 소요되는 시스템에서는 사용자에게 진행 상황을 실시간으로 보여주는 것이 중요합니다. 

이를 위해 FastAPI의 스트리밍 기능과 LangGraph의 `astream` 기능을 결합했습니다:

```python
@app.post("/chat/stream")
async def chat_stream_endpoint(request: ChatRequest):
    """실시간으로 에이전트 작업 과정을 스트리밍합니다"""
    async def event_generator():
        # 각 에이전트의 작업 과정을 실시간으로 스트림으로 전송
        async for item in stream_agent_response(request):
            # 줄바꿈을 추가해 클라이언트가 각 이벤트를 구분할 수 있게 함
            yield item + "\n"
    
    # 브라우저에 지속적인 연결 유지를 위한 헤더 설정
    return StreamingResponse(
        event_generator(),
        media_type="application/json",
        headers={
            "Cache-Control": "no-cache",  # 캐싱 방지
            "Connection": "keep-alive",   # 연결 유지
        }
    )
```

이 구현을 통해 사용자는 실시간 진행 상황을 토큰 단위로 확인할 수 있습니다.

서버-클라이언트 간 데이터 전송을 위해 SSE(Server-Sent Events) 대신 단순 JSON 라인 형식을 채택하여 토큰 단위 전송-파싱 과정을 단순화했습니다.

#### 7.3 운영 환경

KSAT Agent 백엔드 시스템은 안정적이고 확장 가능한 운영을 위해 다음과 같은 환경으로 구성되어 있습니다.

| 구성 요소 | 설명 | 주요 기능 |
|----------|------|-----------|
| **실행 환경** | Docker 컨테이너 + GCP 가상머신 | • 개발/운영 환경 일관성 유지<br>• 종속성 격리<br>• 간편한 배포 및 확장 |
| **프로세스 관리** | Supervisor | • 서버 프로세스 자동 관리<br>• 예기치 않은 종료 시 재시작<br>• 로그 수집 및 모니터링 |
| **CI/CD 체계** | GitHub Actions | • main 브랜치 변경 감지<br>• 자동 빌드 및 배포<br>• 서버 코드 동기화 |

**인프라 구성 파일**

```
backend/
├── Dockerfile            # 백엔드 컨테이너 정의
├── docker-compose.yaml   # 컨테이너 구성 및 네트워크 설정
├── supervisord.conf      # 프로세스 관리 설정
├── requirements.txt      # Python 종속성
└── .env                  # 환경 변수 (Git 제외)

frontend/
└── requirements.txt      # Streamlit 앱 종속성
```

> **참고** : API 키 등 민감 정보는 `.env` 파일로 서버에서 직접 관리되며, Git 저장소에 포함되지 않습니다.

---
### 8️⃣ 맺음말

KSAT Agent는 기존 출제 프로세스를 상당 부분 효율화할 수 있을 것으로 기대합니다. 투입 비용을 낮춤으로써, 양질의 문항이 저렴한 가격에 공급될 수 있기를 바랍니다. 

KSAT Agent가 교사와 학생들에게 실질적인 이로움을 가져다 주고, 나아가 교육 콘텐츠 제작의 패러다임을 바꾸는 계기가 되면 좋겠습니다. 

감사합니다.


<br>
<br>

### :bulb: 부록 : 개념 지도 스키마 v5.0 Docs 

_상위권‧고난도 수능 독서 출제를 위한 설계_

---

#### 1. 개요 & 필요성  
고난도 독서 문항은 **단일 사실 확인**이 아닌 *다단계 추론·비판적 비교·관점 충돌*을 요구한다.  
스키마 v5.0은 이러한 문항을 **그래프 한 ∼ 두 홉** 안에서 근거를 찾고, 세 ∼ 네 홉까지 확장해 종합적 판단이 가능하도록 다음을 목표로 한다.

| 목표 | 설명 |
|------|------|
| **추론 깊이** | 인과·조건·반례·메타평가까지 4-레벨 이상 연쇄 관계 추적 가능 |
| **관점 대립** | 동일 노드에 대해 *주장·근거·반박·양보*를 구조적으로 표현 |
| **질적 비교** | "A ↔ B" 단순 비교를 넘어 *우위/열위·준거축*을 명시 |
| **검증 가능성** | 선지 판별 시 *supporting_sentence* 1-2개면 충분하도록 설계 |
| **다분야 호환** | 법·정치, 과학·기술, 철학·예술 지문 모두 공통 스키마 사용 |

---

#### 2. 주요 변경점 (v4.1 → v5.0)

| 구분 | v4.1 | v5.0 (신규·변경) |
|------|------|-----------------|
| **Edge Type 수** | 15종 | **20종** (5 종 추가) |
| **Label 수** | 27개 | **38개** |
| **다중 논증 구조** | supports / contradicts | **argument_unit**, **rebuttal_of**, **conditioned_by** 등 세분화 |
| **메타 관계** | 부재 | **stance_on**, **uses_framework** → 관점·방법론 표현 |
| **수량 비교** | is_equal_to 등 3개 | **delta_is_positive/negative** 추가 → 기울기·증감 표현 |
| **예외·한계** | 없음 | **has_exception**, **has_scope_limit** |
| **불확실성** | 없음 | **has_probability**, **is_hypothetical** |
| **노드 속성** | id/label 등 | **tier**(core/support), **discourse_role**(claim/data/warrant) 추가 |
| **JSON 스키마** | 단일 버전 | **$schema** 필드로 버전 명시, backward-compatible |

---

#### 3. 엣지 스키마 v5.0 (총 20 Type / 38 Label)

> **굵게**: v5.0 신규

| Type | Label (필수) | 설명·용례 |
|------|--------------|-----------|
| **Hierarchy** | **is_parent_of**, **is_child_of** | 학파·법조문·분류 체계 |
| Classification | belongs_to | "정신분석 이론 A belongs_to 심리학" |
| Definition | defines | "도덕 문장 defines 진리 부정" |
| Composition | has_part | "플라스틱 has_part 결정 영역" |
| Property | has_attribute | "경영 공시 has_attribute 투명성" |
| Comparison | is_similar_to, differs_from | 철학 A vs B 비교 |
| **QuantComparison** | is_greater_than, is_less_than, is_equal_to, **delta_is_positive/negative** | 지지율 증가·감소 등 |
| Causality | causes, influences | "과산화물 개시제 causes 이중 결합 파괴" |
| **CounterCausality** | **mitigates**, **exacerbates** | "사외이사 mitigates 폐쇄적 경영" |
| Conditionality | requires, depends_on | "재판매가격유지 requires 정당한 이유" |
| **Exception** | **has_exception**, **has_scope_limit** | 여론조사 공표 금지 예외(저작물) |
| Temporal | occurs_at, before, after | 오존홀 occurs_at 9-11월 |
| Spatial | is_located_at | 오존홀 is_located_at 남극 성층권 |
| Purpose | has_purpose, functions_as, uses_means | 스톡옵션 has_purpose 인센티브 |
| Example | is_example_of | 폴리에틸렌 is_example_of 열가소성 |
| Reference | refers_to, is_source_of | 문헌 간 인용 |
| Evaluation | views_as, has_stance | "바쟁 has_stance 몽타주 부정" |
| Argumentation | supports, contradicts, **rebuttal_of**, **argument_unit** | 복합 논증 트리 |
| **Methodology** | **uses_framework**, **is_derived_from** | "천두슈 uses_framework 과학 정신" |
| **Modality** | **is_hypothetical**, **has_probability** | "오존 회복 has_probability 0.8 by 2050" |

---

#### 4. 노드 메타데이터 확장

| 필드 | 형식 | 설명 |
|------|------|------|
| id | string | 고유 ID |
| label | string | 정규화된 단수 명사 |
| type | string | concept / process / actor / value 등 |
| **tier** | core / support | 핵심 채점용 vs 배경 정보 |
| **discourse_role** | claim / data / warrant / rebuttal / backing | 톤퀸 모델 기반 |
| description | string | (선택) 요약 |
| text_span | [int,int] | 원문 위치 |

---

#### 5. JSON Top-Level 구조

```json
{
  "$schema": "https://kice-graph.org/schema/v5.0",
  "graph_id": "2025_06_section_8_11",
  "document_source": {
    "title": "플라스틱 중합 과정",
    "source_file": "2025_06_section_8_11.txt",
    "sections": ["8","9","10","11"]
  },
  "nodes": [ /* … */ ],
  "edges": [ /* … */ ]
}
```

* `$schema` 필드는 파서가 v5.0을 인식하도록 필수.  
* **Backward compatibility** : v4.1 그래프를 v5.0 파서는 idempotent 변환 지원.

---

#### 6. 구축 Workflow (고난도 버전)  

1. **Micro-chunk 파싱** : 문단→문장→의미 단위로 토큰화  
2. **Core claim 선정** : tier=core 후보만 우선 그래프화  
3. **Multi-hop 연결** : 최소 2-hop으로 답이 구성되도록 엣지 설계  
4. **반례·제한** 배치 : has_exception / rebuttal_of 추가 → 판단형·보기형 선지 소재  
5. **정량-정성 믹스** : QuantComparison + Evaluation 혼합 → '△보다 크다 + 가치 판단' 선지 제작  
6. **검증 문장 링크** : 모든 edge.metadata.supporting_sentence → 원문 exact string  

---

#### 7. 고난도 출제용 패턴 가이드

| 문항 유형 | 그래프 패턴 | 예시(첨부 기출) |
|-----------|-------------|-----------------|
| 복합 추론형 | causes + has_exception + rebuttal_of | 오존홀 생성(원인) ↔ 온실가스 has_exception (성층권 온도 상승 시) |
| 시점 변동형 | before / after + delta_is_positive | 북극 2011·2020 오존 감소 before 2023 |
| 관점 대립형 | has_stance (+supports/contradicts) | 바쟁 vs 정신분석 영화 이론 |
| 조건 위배형 | requires + contradicts | 도덕 문장 진리값 requires 검증 가능 ↔ 에이어 contradicts |

---

#### 8. 품질 Checklist (5 항)

1. **근거 포함률 100 %** : 모든 core edge는 supporting_sentence 필수  
2. **다중 경로** : 정답 선지는 2 이상 경로, 오답 선지는 1 경로 or break edge  
3. **분기 균형** : 한 노드 degree 최대 7, 과도한 스타 구조 금지  
4. **용어 일관성** : 동일 개념 label 동일, 상위/하위 관계 명시  
5. **오류 로그 0** : JSON schema validation & unit-test 통과

---

#### 9. 예시 스니펫 (v5.0)

```json
{
  "nodes":[
    {"id":"n1","label":"Montage","type":"technique","tier":"core"},
    {"id":"n2","label":"Continuity of Reality","type":"property","tier":"core"},
    {"id":"n3","label":"Bazin","type":"actor","tier":"core","discourse_role":"claim"},
    {"id":"n4","label":"Disruption","type":"effect","tier":"support"}
  ],
  "edges":[
    {"source_id":"n1","target_id":"n2","type":"Comparison","label":"differs_from",
     "metadata":{"supporting_sentence":"바쟁은 몽타주가 현실의 연속성을 깨뜨린다고 보았다."}},
    {"source_id":"n1","target_id":"n4","type":"Causality","label":"causes",
     "metadata":{"supporting_sentence":"몽타주는 공간을 불연속적으로 연결해 관객에게 생소한 느낌을 준다."}},
    {"source_id":"n3","target_id":"n1","type":"Evaluation","label":"views_as",
     "metadata":{"supporting_sentence":"바쟁은 몽타주가 관객 해석을 제한한다고 비판했다."}}
  ]
}