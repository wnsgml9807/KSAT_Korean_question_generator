import streamlit as st
import os
import streamlit_mermaid as stmd
import base64


st.markdown("""
<style>
    /* 전체 폰트 및 기본 스타일 */
    body {
        font-family: 'Pretendard', sans-serif;
    }
    /* 제목 스타일 */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Pretendard', sans-serif;
        font-weight: 700;
    }
    h1 {
        font-size: 2.8em;
        color: #1E293B;
    }
    h2 {
        font-size: 2em;
        margin-top: 1.5em;
        padding-bottom: 0.3em;
        border-bottom: 2px solid #E5E7EB;
        color: #334155;
    }
    h3 {
        font-size: 1.5em;
        margin-top: 1.2em;
        color: #475569;
    }
    /* 본문 텍스트 - 기본 브라우저 스타일 사용 */
    /* 뱃지 스타일 */
    .badge-container {
        display: flex;
        gap: 8px;
        margin-top: 1em;
        margin-bottom: 1.5em;
        flex-wrap: wrap;
    }
    .badge {
        display: inline-block;
        padding: 0.4em 0.8em;
        font-size: 0.9em;
        font-weight: 600;
        line-height: 1;
        text-align: center;
        white-space: nowrap;
        vertical-align: baseline;
        border-radius: 0.375rem;
    }
    .badge-python { background-color: #FFF7ED; color: #C2410C; }
    .badge-langgraph { background-color: #FCE7F3; color: #831843; }
    .badge-fastapi { background-color: #E0F2F7; color: #00796B; }
    .badge-chromadb { background-color: #E8EAF6; color: #3F51B5; }
    .badge-streamlit { background-color: #FFF0F0; color: #FF4B4B; }
    .badge-docker { background-color: #E3F2FD; color: #1E88E5; }

    /* 나눔명조 폰트 (지문용) */
    @import url('https://fonts.googleapis.com/css2?family=Nanum+Myeongjo:wght@400;700;800&display=swap');
    .passage-font {
        border: 1px solid #D1D5DB;
        border-radius: 5px;
        padding: 15px !important;
        margin-top: 15px;
        margin-bottom: 20px;
        font-family: 'Nanum Myeongjo', serif !important;
        font-size: 15px !important;
        line-height: 1.8;
        background-color: #F9FAFB;
    }
    .passage-font p {
        text-indent: 1em; /* 각 문단의 첫 줄 들여쓰기 */
        margin-bottom: 0em;
        font-size: 1em;
    }
</style>
""", unsafe_allow_html=True)


col1, col2, col3 = st.columns([1,8,1])

with col2:
    st.markdown("""
    # KSAT Agent
    ### Multi-Agent 기반 교육용 출제 시스템
    
    **기획 및 제작**: 권준희 (연세대 교육학과 재학)<br>
    **ver. 0.7.4** (06.10)
    """, unsafe_allow_html=True)

    # 기술 스택 뱃지
    st.markdown("""
    <div class="badge-container">
        <span class="badge badge-python">Python</span>
        <span class="badge badge-langgraph">LangGraph</span>
        <span class="badge badge-fastapi">FastAPI</span>
        <span class="badge badge-fastapi">Uvicorn</span>
        <span class="badge badge-chromadb">ChromaDB</span>
        <span class="badge badge-streamlit">Streamlit</span>
        <span class="badge badge-docker">Docker</span>
    </div>
    """, unsafe_allow_html=True)

    # 데모 실행하기 버튼
    st.html('''
    <div align="center" style="margin: 20px 0;">
      <h3 style="margin-bottom: 20px;"> 직접 사용해 보세요 ✨</h3>
    </div>
    ''')
    
    # Streamlit 페이지 이동을 위한 버튼 (중앙 정렬)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🚀 KSAT Agent 실행하기", type="primary", use_container_width=True):
            # Query params를 사용해서 페이지 변경 신호 전달
            st.query_params.page = "chat"
            st.rerun()
    
    st.html('''
    <div align="center" style="margin-top: 10px;">
      <p><i>버튼을 클릭하면 데모 앱으로 이동합니다. 🚀</i></p>
    </div>
    ''')

    # --- 1. 개요 ---
    st.markdown('<h2 style="text-decoration: none; border-bottom: none;">1. 개요</h2>', unsafe_allow_html=True)

    with open("./docs/preview.png", "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")
    st.html(f'''
        <div style="text-align: center; margin-top: 20px; margin-bottom: 20px;">
            <img src="data:image/png;base64,{data}" alt="KSAT Agent 최종 화면" style="width: 100%; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        </div>
    ''')

    st.markdown("""
    <p>KSAT(Korean SAT) Agent는 수능 시험 대비용 국어 모의고사를 출제하는 교육용 AI 에이전트 시스템입니다. 시중의 값비싼 모의고사 컨텐츠 대신, 학생들이 저렴한 가격에 양질의 학습 컨텐츠를 누리길 바라는 마음에서 프로젝트를 시작하게 되었습니다. 현재는 교사와 출제 전문가들이 국어 문항을 손쉽게 출제할 수 있는 보조 시스템으로 타겟 중입니다.</p>
    <p>완성도 높은 문항은 논리적으로 정교하면서도 학생들에게 인지적 부담을 줄 수 있어야 합니다. 범용 AI는 이러한 '수능 감각'을 갖추지 못해 양질의 문항을 생성하는 데 한계가 있었기 때문에, 오랜 기간 문항 출제자로 활동한 경험과 노하우를 바탕으로 전문화된 AI 출제 시스템을 개발했습니다.</p>
    """, unsafe_allow_html=True)

    # --- 2. 프로젝트 성과 ---
    st.markdown('<h2 style="text-decoration: none; border-bottom: none;">2. 프로젝트 성과</h2>', unsafe_allow_html=True)
    
    st.markdown("#### 1) 비용 및 시간 절감")
    st.markdown("""
    <p>수능형 모의고사를 출판하는 작업은 많은 비용과 시간을 수반합니다. 각 분야(법/경제/기술 등) 전문가들에게 지문 원고를 의뢰하고 수 차례의 검토 작업을 진행하는 데에는 많은 인력과 한 달 이상의 시간, 그리고 하나의 문항 세트당 수백만 원 이상의 비용이 발생합니다. KSAT Agent는 AI를 바탕으로 이런 비용을 획기적으로 감소시킵니다.</p>
    """, unsafe_allow_html=True)

    col_left, col_right = st.columns(2)
    with col_left:
        st.markdown("""
        <div style="background:#ffffff;border:1px solid #e5e7eb;border-radius:12px;padding:24px;box-shadow:0 1px 3px rgba(0,0,0,0.05);height:200px;display:flex;flex-direction:column;margin-bottom:30px;">
            <h4 style="margin-top:0;margin-bottom:12px;color:#374151;font-weight:600;border-left:4px solid #ef4444;padding-left:12px;">기존 프로세스</h4>
            <ul style="padding-left:20px;color:#6b7280;line-height:1.6;flex-grow:1;">
                <li>수백만 원의 인건비</li>
                <li>1~2개월 소요</li>
                <li>외부 출제자와 내부 연구진 간 의사소통의 비효율성</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    with col_right:
        st.markdown("""
        <div style="background:#ffffff;border:1px solid #e5e7eb;border-radius:12px;padding:24px;box-shadow:0 1px 3px rgba(0,0,0,0.05);height:200px;display:flex;flex-direction:column;margin-bottom:30px;">
            <h4 style="margin-top:0;margin-bottom:12px;color:#064e3b;font-weight:700;border-left:4px solid #10b981;padding-left:12px;">KSAT Agent</h4>
            <ul style="padding-left:20px;color:#065f46;line-height:1.6;font-weight:500;flex-grow:1;">
                <li>500원 이하의 문항 제작비용</li>
                <li>5분 안에 초안 생성</li>
                <li>실시간 채팅을 통한 상호작용</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 2) 높은 수준의 퀄리티")
    st.markdown("""
    <p>동시에, KSAT Agent는 ChatGPT 등 범용 AI가 달성하기 힘든 높은 수준의 퀄리티를 유지합니다. Multi-Agent 시스템과 Fine-tuning된 전용 AI 모델을 구축하는 등 다양한 최신 기술을 통합적으로 활용하여 출제 성능을 극대화했습니다. 그 결과, 입시 전문 플랫폼 '오르비'의 유명 강사에게 실제 수능에 출제된 기출 문제 대비 75% 수준의 퀄리티에 도달했다는 평가를 받을 수 있었습니다. 이러한 성과를 바탕으로, 현재 KSAT Agent는 '강남대성학원' 소속의 부설 연구기관과 인수계약을 진행하고 있습니다.</p>
    """, unsafe_allow_html=True)

    with open("./docs/logo_kangnam_202111.png", "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")

    st.html(f'''
        <div style="margin-top: 15px; text-align: center;">
            <img src="data:image/png;base64,{data}" alt="강남대성 로고" style="height: 100px;">
        </div>
    ''')

    st.divider()

    # --- 3. 사용자 경험 ---
    st.markdown('<h2 style="text-decoration: none; border-bottom: none;">3. 사용자 경험 (UX)</h2>', unsafe_allow_html=True)
    st.markdown("""
    <p>사용자가 손쉽게 조작할 수 있도록 Streamlit 기반의 직관적인 챗봇 UI를 제작했습니다. 레이아웃은 총 세 개로 이루어져 있습니다. 왼쪽은 에이전트와 소통을 위한 영역, 가운데와 오른쪽은 각각 지문과 문항이 출력되는 영역으로, 실제 수능 시험지 스타일을 그대로 본떠 css를 구성했습니다.</p>
    
    <h4>작동 단계</h4>
    <ol>
        <li><strong>분야 입력</strong>: 사용자가 원하는 분야(인문/사회/예술/기술/과학)를 입력</li>
        <li><strong>주제 추천</strong>: 기출 DB에서 유사한 소재의 지문을 검색하여 새로운 주제를 추천</li>
        <li><strong>주제 선택</strong>: 사용자가 추천된 주제 중 하나를 선택</li>
        <li><strong>자료 리서치 및 개요 작성</strong>: 에이전트가 선택된 주제에 대한 자료 조사와 구조화된 개요 작성</li>
        <li><strong>지문 및 문항 생성</strong>: 완성된 개요를 바탕으로 수능형 지문과 문항, 해설을 자동 생성</li>
    </ol>
    
    <p>아래는 KSAT Agent 시연 영상입니다.</p>
    """, unsafe_allow_html=True)

    # 시연 영상 (실제 영상 파일 또는 링크로 교체 필요)
    st.video("https://youtu.be/faHAOZtIAKI") # Placeholder video

    st.divider()

    # --- 4. 시스템 아키텍처 및 사용 기술 스택 ---
    st.markdown('<h2 style="text-decoration: none; border-bottom: none;">4. 시스템 아키텍처 및 기술 스택</h2>', unsafe_allow_html=True)
    st.markdown("#### 1) 사용 기술 스택")
    st.markdown("""
    - **Frontend**: `Streamlit` + `custom css`
    - **Backend**: `LangGraph` + `Fastapi` + `ChromaDB`
    - **AI Fine-tuning**: `OpenAI`
    - **Package**: `Docker`
    """)
    st.markdown("#### 2) 시스템 아키텍처")
    
    # 컬럼을 사용해서 가운데 정렬 시도
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        stmd.st_mermaid("""
        graph TB
            subgraph FRONTEND["🖥️ Frontend"]
                UI["Streamlit UI"]
            end

            subgraph BACKEND["🐳 Docker Container"]
                FASTAPI["FastAPI Server"]
                LANGGRAPH["LangGraph Engine"]
                
                subgraph AGENTS["AI Agents"]
                    SUPERVISOR["🤖 Supervisor"]
                    PASSAGE["✍️ Passage Editor"]
                    QUESTION["❓ Question Editor"]
                end
            end

            subgraph DATA["💾 Data Layer"]
                CHROMA["ChromaDB<br/>(Vector Store)"]
                SQLITE["SQLite<br/>(Checkpoints)"]
            end

            subgraph EXTERNAL["🌐 External APIs"]
                OPENAI["OpenAI API"]
                GEMINI["Gemini API"]
            end

            %% 연결 관계
            UI --> FASTAPI
            FASTAPI --> LANGGRAPH
            LANGGRAPH --> SUPERVISOR
            
            SUPERVISOR --> PASSAGE
            SUPERVISOR --> QUESTION
            
            PASSAGE --> CHROMA
            QUESTION --> CHROMA
            LANGGRAPH --> SQLITE
            
            SUPERVISOR --> OPENAI
            PASSAGE --> OPENAI
            QUESTION --> GEMINI
            
            %% 스타일링
            classDef frontend fill:#E3F2FD,stroke:#1565C0,stroke-width:2px
            classDef backend fill:#E8F5E9,stroke:#2E7D32,stroke-width:2px
            classDef agent fill:#F3E5F5,stroke:#6A1B9A,stroke-width:2px
            classDef data fill:#FFF3E0,stroke:#F57C00,stroke-width:2px
            classDef external fill:#FAFAFA,stroke:#616161,stroke-width:2px
            
            class UI frontend
            class FASTAPI,LANGGRAPH backend
            class SUPERVISOR,PASSAGE,QUESTION agent
            class CHROMA,SQLITE data
            class OPENAI,GEMINI external
        """, pan=False, zoom=False, show_controls=False)
    
    st.markdown("#### 3) 스트리밍 워크플로우")
    
    # 컬럼을 사용해서 가운데 정렬
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        stmd.st_mermaid("""
        sequenceDiagram
            participant User as 👤 사용자
            participant FastAPI as ⚙️ FastAPI 서버
            participant LangGraph as 🧠 LangGraph 엔진
            
            User->>FastAPI: 요청 입력(/stream 엔드포인트)
            FastAPI->>LangGraph: 세션 생성/조회 후 astream 호출
            
            loop 실시간 이벤트 스트림
                LangGraph-->>FastAPI: AI/ToolMessage 전송
                FastAPI-->>User: 파싱 후 SSE 이벤트 전송
            end
        """, pan=False, zoom=False, show_controls=False)

    st.divider()

    # --- 5. AI 모델 활용 ---
    st.markdown('<h2 style="text-decoration: none; border-bottom: none;">5. AI 모델 활용</h2>', unsafe_allow_html=True)
    st.markdown("""
    범용 AI가 작성한 글은 개념을 '쉽고 친절하게' 설명하는 데 초점이 맞추어져 있습니다. 하지만 수능 지문은 다릅니다. 다양한 개념 간의 복잡한 논리적 관계를 '명확하면서도 압축적'으로 표현해야 합니다. 아래의 예시와 같이, 기존 모델로는 이러한 문체를 구현하기에 한계가 있었습니다. 이에 후술할 두 개의 AI 모델을 Openai에서 제공하는 도구를 활용하여 직접 fine-tuning하여 탑재했습니다.
    """, unsafe_allow_html=True)

    col_d, col_e = st.columns(2)
    with col_d:
        st.markdown("""
        <div style="background:#ffffff;border:1px solid #e5e7eb;border-radius:12px;padding:24px;box-shadow:0 1px 3px rgba(0,0,0,0.05);height:250px;display:flex;flex-direction:column;margin-bottom:30px;">
            <h4 style="margin-top:0;margin-bottom:12px;color:#923c0e;font-weight:600;border-left:4px solid #ef4444;padding-left:12px;">범용 AI 모델의 문체</h4>
            <ul style="padding-left:20px;color:#6b7280;line-height:1.6;margin-bottom:15px;">
                <li>직관적이고 친절한 설명적 어투</li>
                <li>낮은 정보 밀도와 분절된 개념 관계</li>
                <li>주제를 둘러싼 다양한 화제를 나열식으로 설명하는 발산적 글쓰기</li>
                <li>선형적 구조 (A-B-C-D)</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    with col_e:
        st.markdown("""
        <div style="background:#ffffff;border:1px solid #e5e7eb;border-radius:12px;padding:24px;box-shadow:0 1px 3px rgba(0,0,0,0.05);height:250px;display:flex;flex-direction:column;margin-bottom:30px;">
            <h4 style="margin-top:0;margin-bottom:12px;color:#065f46;font-weight:700;border-left:4px solid #10b981;padding-left:12px;">실제 수능의 문체</h4>
            <ul style="padding-left:20px;color:#065f46;line-height:1.6;font-weight:500;margin-bottom:15px;">
                <li>학술적이고 압축적인 어투</li>
                <li>높은 정보 밀도와 유기적인 개념 관계</li>
                <li>소수의 핵심 개념을 정의하고 이들 간의 논리적 관계를 파고드는 수렴형 글쓰기</li>
                <li>나선형 구조 (A-B-A`-B`)</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    #### 1) 개념 구성 및 개요 작성 모델 – Reinforced Learning
    <p>좋은 지문을 작성하기 위해서는 먼저 지문에 어떤 개념을 포함할지(What) 선정해야 합니다. 그리고 그것을 유기적으로 엮어 글을 써 내려가야 합니다.</p>
    """, unsafe_allow_html=True)

    # 좋은 지문의 조건을 인용구로 처리
    st.markdown("""
    > **수능 지문의 특징**
    > 
    > - 지문에 제시된 모든 개념은 향후 논의에서 다시 언급되어 이후 내용을 전개하는 데 활용됨.
    > - 서로 다른 개념을 제시할 때는 단순히 병렬적으로 나열하는 것이 아니라, 학생들이 명확한 기준을 중심으로 비교-대조할 수 있도록 유도함.
    > - 개념을 정의하고 설명하는 것에 그치지 않고, 특정 문제를 해결하거나 의문을 해소하는 등 완결된 서사 구조 속에서 활용됨.
    """)

    st.markdown("""
    <p>범용 AI모델은 특히 개념의 유기적인 연결 부분에서 취약점을 보여, 최신 AI 학습 기법인 강화학습(RL)을 사용하여 이 부분을 집중적으로 보강했습니다. 강화학습이란 AI의 출력물에 따라 특정 기준에 맞춰 '보상'을 부여하는 방법론으로, GPT, Gemini, Claud 등 최신 모델들에서 활발히 사용되는 방법론입니다. KSAT Agent의 경우, Openai의 o4-mini 모델을 기반으로 데이터셋과 보상 함수를 자체적으로 설계해 강화학습을 진행했습니다. 
    """, unsafe_allow_html=True)

    # 컬럼을 사용해서 가운데 정렬
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        stmd.st_mermaid("""
        graph TD
            Agent["🤖 Agent<br/>(o4-mini)"]
            Environment["🌐 Environment<br/>(학습 환경)"]
            Grader["⚖️ Grader<br/>(동적 생성)"]
            
            Agent -->|"개요 작성 (Action)"| Environment
            Environment -->|"평가 요청"| Grader
            Grader -->|"보상 점수 (Reward)"| Agent
            
            style Agent fill:#E3F2FD,stroke:#1565C0,stroke-width:3px
            style Environment fill:#FFF3E0,stroke:#F57C00,stroke-width:3px
            style Grader fill:#E8F5E9,stroke:#2E7D32,stroke-width:3px
        """, pan=False, zoom=False, show_controls=False)

    st.markdown("""
    <p>이때, 모델이 단순히 보상을 높이기 위해 편법(동일한 어구를 반복적으로 사용하여 '유기성' 점수를 높이는 등 올바르지 않은 학습 결과)을 사용하지 못하도록, 보상 점수를 책정하는 Grader를 샘플 데이터마다 '동적'으로 생성하여, 기출 지문에서 나타나는 개념 구성 방식과 서사 구조를 올바르게 체득할 수 있도록 섬세하게 설계했습니다.</p>
    <p>학습 후 출력물을 분석한 결과, 동일한 분량의 개요에서 개념 밀도는 50% 향상되었으며, 인과/대조/조건/포함관계 등 개념 간의 논리적 연결 구조는 70% 향상되었습니다.</p>
    """, unsafe_allow_html=True)

    col_h, col_i = st.columns(2)
    with col_h:
        st.markdown("<h5>원본 모델(o4-mini)의 개요</h5>", unsafe_allow_html=True)
        st.markdown("""
        <div style="background:#ffffff;border:1px solid #e5e7eb;border-radius:12px;padding:24px;box-shadow:0 1px 3px rgba(0,0,0,0.05);height:520px;display:flex;flex-direction:column;margin-bottom:30px;">
            <ul style="color:#6b7280;line-height:1.6;margin-bottom:15px;">
                <li>개념의 수는 많으나, 다소 산발적이고 이후 논의와의 관련성이 부족함</li>
                <li>개념 간의 유기적인 관계가 다소 미흡</li>
            </ul>
            <div class=\"passage-font\" style="font-size:13px !important;line-height:1.6;background:rgba(255,255,255,0.7);padding:12px;border-radius:8px;flex-grow:1;overflow-y:auto;">
            <b>1. 도입부 - 효소와 저해제의 기본 개념</b><br>
            - 생명체 내에서 <mark style=\"background:#FFE4E1;\">효소</mark>의 역할 설명 (생화학 반응의 촉매)<br>
            - <mark style=\"background:#FFE4E1;\">효소</mark>의 활성 부위와 <mark style=\"background:#E1F5FE;\">기질</mark>의 결합 원리 소개<br>
            - <mark style=\"background:#FFE4E1;\">효소</mark> 반응을 조절하는 <mark style=\"background:#F3E5F5;\">저해제</mark>의 존재와 필요성 제시<br>
            - <mark style=\"background:#F3E5F5;\">저해제</mark>를 <mark style=\"background:#E8F5E9;\">경쟁적 저해제</mark>와 <mark style=\"background:#FFF3E0;\">비경쟁적 저해제</mark>로 분류<br>
            <b>2. 의학적 응용과 약물 개발</b><br>
            - <mark style=\"background:#E8F5E9;\">경쟁적 저해제</mark>의 <mark style=\"background:#FAFAFA;\">약물 활용 사례</mark> (예: <mark style=\"background:#E3F2FD;\">스타틴 계열 콜레스테롤 저하제</mark>)<br>
            - <mark style=\"background:#FFF3E0;\">비경쟁적 저해제</mark>의 <mark style=\"background:#FAFAFA;\">약물 활용 사례</mark> (예: <mark style=\"background:#FFEBEE;\">항암제</mark>)<br>
            - <mark style=\"background:#E0F2F1;\">선택적 저해제 개발</mark>의 중요성<br>
            - <mark style=\"background:#F1F8E9;\">부작용 최소화</mark>를 위한 <mark style=\"background:#FCE4EC;\">특이성 향상 전략</mark><br>
            <b>3. 세포 내 조절 메커니즘과 진화적 의의</b><br>
            - <mark style=\"background:#EDE7F6;\">대사 경로</mark>에서의 <mark style=\"background:#E8EAF6;\">피드백 저해 현상</mark><br>
            - <mark style=\"background:#F9FBE7;\">알로스테릭 조절</mark>을 통한 <mark style=\"background:#E0F7FA;\">효율적 에너지 관리</mark><br>
            - <mark style=\"background:#E8F5E9;\">경쟁적</mark>/<mark style=\"background:#FFF3E0;\">비경쟁적 저해</mark>의 <mark style=\"background:#FFF8E1;\">상호보완적 역할</mark><br>
            - <mark style=\"background:#F3E5F5;\">생명체의 항상성 유지</mark>에 대한 기여 (후략)<br>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col_i:
        st.markdown("<h5>KSAT Agent 전용 모델의 개요</h5>", unsafe_allow_html=True)
        st.markdown("""
        <div style="background:#ffffff;border:1px solid #e5e7eb;border-radius:12px;padding:24px;box-shadow:0 1px 3px rgba(0,0,0,0.05);height:520px;display:flex;flex-direction:column;margin-bottom:30px;">
            <ul style="color:#065f46;line-height:1.6;font-weight:500;margin-bottom:15px;">
                <li>개념의 수는 적지만, 하나의 개념이 이후 논의에서 계속 등장하면서 반복적으로 활용됨</li>
                <li>개념 간의 유기적인 관계가 풍부함</li>
            </ul>
            <div class=\"passage-font\" style="font-size:13px !important;line-height:1.6;background:rgba(255,255,255,0.7);padding:12px;border-radius:8px;flex-grow:1;overflow-y:auto;">
            <b>1. 효소 반응의 기본</b><br>
            - <mark style=\"background:#FEF3C7;\">효소</mark>는 화학 반응을 빨리 일어나게 도와주는 단백질이고, <mark style=\"background:#E1F5FE;\">기질</mark>은 효소가 반응을 일으키는 대상 물질이다.<br>
            - <mark style=\"background:#FEF3C7;\">효소</mark>와 <mark style=\"background:#E1F5FE;\">기질</mark>이 만나 ES(효소-기질) 복합체를 만든 뒤 반응이 일어나면 생성물(P)이 생긴다.<br>
            - 반응 속도는 <mark style=\"background:#E1F5FE;\">기질</mark> 농도가 높아질수록 빨라지지만, 일정 이상이 되면 최대 속도(Vmax)에 도달해 더 빨라지지 않는다.<br>
            - <mark style=\"background:#E1F5FE;\">기질</mark> 농도가 Vmax의 절반 속도를 낼 때의 농도를 Km이라고 부른다. 이는 '<mark style=\"background:#FEF3C7;\">효소</mark>가 <mark style=\"background:#E1F5FE;\">기질</mark>을 얼마나 잘 붙잡느냐'를 수치로 나타낸 것이다.<br>
            <b>2. 경쟁적 저해제</b><br>
            - 경쟁적 저해제는 <mark style=\"background:#E1F5FE;\">기질</mark>과 모양이 비슷해서 <mark style=\"background:#FEF3C7;\">효소</mark>의 활성 부위(기질이 붙는 자리)를 대신 차지하는 물질이다.<br>
            - 저해제와 <mark style=\"background:#E1F5FE;\">기질</mark>이 같은 자리를 두고 "경쟁"하기 때문에, 저해제 농도가 높아지면 <mark style=\"background:#E1F5FE;\">기질</mark>이 붙기 어려워진다.<br>
            - 이 경우 Km은 커진다. 하지만 Vmax는 변하지 않는다. (후략)
        </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    #### 2) 지문 작성 모델 – Supervised Fine Tuning
    <p>완성도 높은 수능 지문을 작성하기 위해서는 내용물뿐만 아니라 그것을 어떻게 서술하는지(How)도 중요합니다. KSAT Agent는 작성된 개요를 수능형 지문으로 변환하는 모델을 별도로 튜닝해 탑재했습니다. 기출에서 추출한 개요-기출 지문 쌍으로 이루어진 100여개의 데이터의 다양성을 높여 과적합을 방지하고자, 데이터 증강(Augmentation) 기법을 사용해 지도 학습(SFT)를 성공적으로 완료할 수 있었습니다. 개요를 작성하는 AI가 지문을 작성하는 AI에게 개요를 건네주면, 해당 개요를 수능 문체와 형식에 맞게 다듬고 온전한 지문으로 변환합니다.</p>
    """, unsafe_allow_html=True)

    with open("./docs/fine-tune.png", "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")
    st.html(f'''
        <div style="text-align: center; margin-top: 20px;">
            <img src="data:image/png;base64,{data}" alt="Fine-tuning 성능 향상 결과" style="width: 100%; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <figcaption style="font-size: 0.9em; color: grey; margin-top: 10px;">Fine-tuning Loss Curve</figcaption>
        </div>
    ''')
    st.markdown("""
    | Loss Type | 초기 (0 step) | 106 step | 213 step | 총 감소값 |
    |:-----------|:---------------|:----------|:----------|:-----------|
    | **Training Loss** | 1.6 | 0.9 | 0.5 | **-1.1** |
    | **Validation Loss** | 1.6 | 1.0 | 0.65 | **-0.95** |

    **Loss 감소율**: Training Loss 68.8% 감소, Validation Loss 59.4% 감소
    <br><br>
    """, unsafe_allow_html=True)



    st.markdown("""
    #### 3) 문제 출제 모델 – 최신 Gemini 2.5 pro 모델 활용
    <p>앞선 두 모델이 출력한 지문을 바탕으로, 완성도 높은 고난도 문항을 출제하는 데에는 Gemini 2.5 pro + RAG 조합을 구성해 사용했습니다. 3년간의 출제 노하우를 담아 섬세하게 설계된 1000줄 가량의 프롬프트와 잘 정제된 기출 데이터를 사용했습니다.</p>
    """, unsafe_allow_html=True)

    # Gemini 로고 추가
    with open("./docs/Google_Gemini_logo.svg.webp", "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")
    st.html(f'''
        <div style="text-align: center; margin: 20px 0;">
            <img src="data:image/webp;base64,{data}" alt="Google Gemini 로고" style="height: 80px;">
        </div>
    ''')

    st.divider()

    # --- 6. LangGraph 설계/구현 ---
    st.markdown('<h2 style="text-decoration: none; border-bottom: none;">6. LangGraph 설계/구현</h2>', unsafe_allow_html=True)
    st.markdown("""
    <p>앞서 설명한 다양한 AI 모델들을 효과적으로 통합하고 일관된 워크플로우를 구축하기 위해, Multi-Agent 프레임워크인 LangGraph를 사용했습니다. LangGraph는 다양한 제조사의 모델을 하나의 워크플로우에 통합하는 데에 최적화된 최신 프레임워크입니다.</p>
    """, unsafe_allow_html=True)

    st.markdown("""
    #### 1) State 구현
    <p>LangGraph의 에이전트들은 상태(State)를 통해 서로의 출력물을 공유하고 참조할 수 있습니다. KSAT Agent는 에이전트별 컨택스트 관리를 위해 맞춤형 State와 업데이트 로직을 구현했습니다.</p>
    
    - **MultiAgentState 클래스 정의:**
    ```python
    from langgraph.prebuilt.chat_agent_executor import AgentState
    from typing import Annotated, List, Literal
    from langchain_core.messages import BaseMessage
    from message_reducer import merge_messages
    
    class MultiAgentState(AgentState):
        messages: Annotated[List[BaseMessage], merge_messages]
        current_agent: str | None = None
        llm_input_messages: List[BaseMessage] = []
        react_count: int = 0  # 같은 에이전트면 두 번 연속 기출문제 주입 방지
        summary: str = ""
        passage: str = ""
        question: str = ""
        request: str = ""
        mode: Literal["new", "edit"] = "new"
    
    class QuestionEditorState(MultiAgentState):
        messages: Annotated[List[BaseMessage], add_messages]
        passage: str
        request: str
        question: str
    ```
    
    - **State 필드별 에이전트 참조 관계:**

    | field | Supervisor | Passage Editor | Question Editor | 설명 |
    |------------|:-------------:|:------------------:|:------------------:|------|
    | **messages** | 👀 참조 | - | - | 전체 대화 내역 (merge_messages 리듀서 적용) |
    | **summary** | ✍️ **생성** | 👀 참조 | - | Supervisor가 작성한 개요 |
    | **passage** | 👀 참조 | ✍️ **생성** | 👀 **참조** | Passage Editor가 작성한 지문 |
    | **question** | 👀 참조 | - | ✍️ **생성** | Question Editor가 작성한 문항 |
    | **request** | 👀 참조 | 👀 참조 | 👀 참조 | 에이전트에게 전달될 사용자 요청 |
    | **mode** | ✍️ **생성** | 👀 참조 | - | 작업 모드 ("new" 또는 "edit") |""", unsafe_allow_html=True)

    st.markdown("""
    #### 2) Graph 구조
    """, unsafe_allow_html=True)

    # 컬럼을 사용해서 가운데 정렬
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        stmd.st_mermaid("""
            graph TD
                START[시작] --> SUPERVISOR["🤖 Supervisor"];

                SUPERVISOR --> PASSAGE["✍️ Passage"];
                SUPERVISOR --> QUESTION["❓ Question"];
                
                PASSAGE --> TOOLNODE["🛠️ ToolNode"];
                QUESTION --> TOOLNODE;
                
                TOOLNODE --> SUPERVISOR;

                SUPERVISOR --> END[종료];

                classDef supervisor fill:#F3E5F5,stroke:#6A1B9A,stroke-width:2px;
                classDef passage fill:#E3F2FD,stroke:#1565C0,stroke-width:2px;
                classDef question fill:#E8F5E9,stroke:#2E7D32,stroke-width:2px;
                classDef toolnode fill:#FFF3E0,stroke:#F57C00,stroke-width:2px;
                
                class SUPERVISOR supervisor;
                class PASSAGE passage;
                class QUESTION question;
                class TOOLNODE toolnode;
        """, pan=False, zoom=False, show_controls=False)

    st.markdown("""
    #### 3) Handoff 메커니즘
    
    KSAT Agent는 정형적인 그래프 구조에 얽매이지 않고, 에이전트가 자율적으로 워크플로우를 통제할 수 있도록 설계되었습니다. 이를 위해 LangGraph의 `Command`와 `Send` 메커니즘을 활용한 동적 에이전트 호출 시스템을 구현했습니다.
    
    **핵심 코드:**
    ```python
    return Command(
        graph=Command.PARENT,
        goto=Send("passage_editor", {
            "summary": summary, 
            "request": request, 
            "passage": pre_passage, 
            "mode": mode
        }),
        update={
            "messages": state["messages"] + [tool_message],
            "current_agent": "passage_editor",
        }
    )
    ```
    
    **동작 원리:**
    - `Command.PARENT`: 현재 그래프에서 부모 그래프로 제어권을 전달
    - `Send("passage_editor", {...})`: passage_editor 노드로 직접 이동하며, 필요한 상태 데이터를 함께 전달
    - `update`: 전역 상태를 업데이트하여 다른 에이전트들이 참조할 수 있도록 함
    
    이를 통해 Supervisor 에이전트는 사용자의 요청을 분석한 후, 적절한 전문 에이전트를 동적으로 호출할 수 있습니다.
    
    #### 4) Message Reducer 구현
    **다중 LLM 제공업체 통합을 위한 커스텀 메시지 리듀서:**
    
    LangGraph에서 기본적으로 제공하는 message reducer는 강력하지만, 제조사들마다 tool-invocation이나 reasoning 토큰에 규격 차이가 있어 하나의 워크플로우에 통합하려면 reducer를 따로 구현해야 했습니다. KSAT Agent가 탑재한 파인 튜닝 모델(OpenAI)과 Gemini, Claude 모델들의 메시지 규격을 통일하기 위한 자체 알고리즘을 구현했습니다.
    
    ```python
    def merge_messages(
        left: Messages | BaseMessage | dict,
        right: Messages | BaseMessage | dict,
        *,
        format: Optional[Literal["langchain-openai"]] = None,
        strip_function_call: bool = True,
    ) -> Messages:
        
        def _prepare(msgs: Messages):
            for m in msgs:
                # ID 할당
                if m.id is None:
                    m.id = str(uuid.uuid4())
                
                # OpenAI 함수 호출 처리
                if strip_function_call and getattr(m, "additional_kwargs", None):
                    # OpenAI function_call 필드 제거 (필요시)
                    m.additional_kwargs.pop("function_call", None)
                    # reasoning 필드 제거 (OpenAI o4 모델 에러 방지)
                    m.additional_kwargs.pop("reasoning", None)
                
                # Gemini 도구 호출 처리
                tool_calls = getattr(m, "tool_calls", None)
                if tool_calls:
                    # ID 없는 도구 호출에 ID 부여
                    for tool_call in tool_calls:
                        if isinstance(tool_call, dict) and "id" not in tool_call:
                            tool_call["id"] = str(uuid.uuid4())
                
                # Claude 도구 호출 처리 (tool_use 필드)
                if getattr(m, "additional_kwargs", {}).get("tool_use"):
                    tool_use = m.additional_kwargs.get("tool_use", {})
                    if isinstance(tool_use, dict) and tool_use.get("id") is None:
                        tool_use["id"] = str(uuid.uuid4())
        
        # ... 메시지 병합 로직 ...
        return merged
    ```
    
    #### 5) ChromaDB RAG 구현
    
    KSAT Agent는 3개의 전문화된 ChromaDB 컬렉션을 구축하여 다양한 관점에서 기출 데이터를 활용할 수 있도록 설계되었습니다. 각 컬렉션은 서로 다른 임베딩 모델과 검색 전략을 사용합니다.
    
    **3개 컬렉션 구조:**
    
    | 컬렉션명 | 임베딩 모델 | 데이터 형태 | 활용 목적 |
    |----------|-------------|-------------|-----------|
    | **kice_materials_v2** | text-embedding-3-large | 원본 지문 + 메타데이터 | 유사 지문 검색 |
    | **kice_subject_summaries** | text-embedding-3-small | 주제별 요약 | 주제 탐색 |
    | **kice_summary_with_outline** | text-embedding-3-large | AI 생성 개요 | 구조화된 개요 참조 |
    
    **핵심 검색 도구 구현:**
    ```python
    @tool
    async def retrieve_data(
        query: str,
        tool_call_id: Annotated[str, InjectedToolCallId],
        state: Annotated[dict, InjectedState],
        field: List[Literal['인문','사회','예술','기술','과학']] | None = None,
    ):
        \"\"\"기출 DB에서 텍스트 쿼리와 메타데이터 필터를 사용하여 관련 지문을 검색합니다.
        여러 분야가 지정되면 각 분야에서 검색된 결과를 종합하여 유사도 상위 3개를 반환합니다.\"\"\"
        
        n_results = 3
        db_path = os.path.join(os.path.dirname(__file__), "DB/kice")
        collection_name = "kice_materials_v2"
        
        client = chromadb.PersistentClient(path=db_path)
        collection = client.get_collection(
            name=collection_name,
            embedding_function=OpenAIEmbeddingFunction(
                model_name="text-embedding-3-large",
                api_key=os.environ.get("OPENAI_API_KEY")
            )
        )
        
        # 분야별 검색 수행
        all_results_intermediate = []
        seen_ids = set()
        
        if not fields_list:
            # 전체 분야 검색
            raw_chroma_results = await asyncio.to_thread(
                collection.query,
                query_texts=[query],
                n_results=n_results,
                include=['documents', 'metadatas', 'distances']
            )
        else:
            # 각 분야별 검색 후 통합
            for field_item in fields_list:
                where_filter = {"field": field_item}
                field_specific_results = await asyncio.to_thread(
                    collection.query,
                    query_texts=[query],
                    n_results=n_results,
                    where=where_filter,
                    include=['documents', 'metadatas', 'distances']
                )
                # 결과 통합 로직...
        
        # 유사도 기준 정렬 및 최종 결과 반환
        return Command(update={"messages": state["messages"] + [tool_message]})
    ```
    
    **메타데이터 필터링 전략:**
    - **분야별 필터링**: 5개 주요 분야(인문, 사회, 예술, 기술, 과학)로 구분하여 정확한 검색 결과 제공
    - **중복 제거**: `seen_ids` 집합을 활용하여 여러 분야 검색 시 중복 문서 방지
    - **유사도 기준 통합**: 각 분야별 검색 결과를 distance 값으로 정렬하여 최종 상위 결과 선별
    
    **비동기 처리 최적화:**
    ```python
    # ChromaDB 쿼리를 별도 스레드에서 실행하여 메인 이벤트 루프 블로킹 방지
    raw_chroma_results = await asyncio.to_thread(
        collection.query,
        query_texts=[query],
        n_results=n_results,
        where=where_filter,
        include=['documents', 'metadatas', 'distances']
    )
    ```
    
    **검색 결과 포맷팅:**
    - JSON 형태의 구조화된 메타데이터 파싱
    - 유사도 점수 계산 (1 - distance)
    - 순위별 결과 정렬 및 반환
    
    이를 통해 에이전트들은 사용자 쿼리에 가장 적합한 기출 지문을 실시간으로 검색하고, 이를 바탕으로 고품질의 지문과 문항을 생성할 수 있습니다.
    
    #### 6) 기타 Tool
    - **google_search_node**: Google 검색 도구를 통한 실시간 정보 수집
    - **mermaid_tool**: 머메이드 다이어그램 생성 도구
    - **use_question_artifact**: 생성한 문항을 사용자에게 출력하는 도구
    
    모든 도구는 `Command` 객체를 반환하여 LangGraph의 상태 업데이트 메커니즘과 통합됩니다.
    """)

    st.divider()

    # --- 7. Docker 컨테이너화 및 배포 환경 ---
    st.markdown('<h2 style="text-decoration: none; border-bottom: none;">7. Docker 컨테이너화 및 배포 환경</h2>', unsafe_allow_html=True)
    st.markdown("""
    #### 1) Docker 컨테이너화
    <p>KSAT Agent는 기본적으로 Linux Ubuntu 22.04 + Pyhon 3.11 slim 조합으로 Docker 컨테이너화되어, 어디서든 쉽게 구축할 수 있도록 배포 환경을 설계했습니다.</p>
    
    #### 2) GCP 서버 구축
    <p>학원 시연 및 포트폴리오용 데모는 GCP Cloud의 Virtual Compute Machine 서버에서 가동되며, Streamlit 링크를 통해 인터넷 사용이 가능한 어디서든 접속하여 사용할 수 있도록 배포 환경이 구축되어 있습니다. 현재는 시험 배포판으로, 100명 이하의 사용자가 접속하여 사용했을 때 무리가 없도록 uvicorn + 4x worker 조합으로 구성되었습니다. 향후 상용화 단계로 진입했을 때 분산 서버 아키텍처와 Gunicorn 조합을 사용할 예정입니다.</p>

    #### 3) CI/CD 구축
    <p>Github Action Workflow를 구축하여, 로컬 머신에서 git push만으로 서버에서 가동 중인 docker 컨테이너를 compose down 후 코드를 pull, 새로운 빌드로 다시 compose-up하는 단계를 모두 자동화하여, 빠른 개발과 배포가 가능하도록 구축해 두었습니다.</p>
    """, unsafe_allow_html=True)

    # 컬럼을 사용해서 가운데 정렬
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        stmd.st_mermaid("""
        graph LR
            A["👨‍💻 개발자<br/>main 브랜치 푸시"] --> B["🔄 Github Actions<br/>빌드 & 체크아웃"]
            B --> C["🔐 GCP 서버<br/>코드 동기화"]
            C --> D["🐳 Docker 재빌드<br/>배포 완료"]
        """, pan=False, zoom=False, show_controls=False)