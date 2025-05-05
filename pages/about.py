import streamlit as st
import os
import streamlit_mermaid as stmd

# 현재 파일의 디렉토리를 기준으로 about.txt 경로 설정
file_path = os.path.join(os.path.dirname(__file__), "about.txt")
file_path2 = os.path.join(os.path.dirname(__file__), "about2.txt")
file_path3 = os.path.join(os.path.dirname(__file__), "about3.txt")
file_path4 = os.path.join(os.path.dirname(__file__), "image.png")
# about.txt 파일 읽기
try:
    with open(file_path, "r", encoding="utf-8") as f:
        about_text = f.read()
    with open(file_path2, "r", encoding="utf-8") as f:
        about_text2 = f.read()
    with open(file_path3, "r", encoding="utf-8") as f:
        about_text3 = f.read()
except FileNotFoundError:
    about_text = "오류: `about.txt` 파일을 찾을 수 없습니다. `frontend/pages/` 디렉토리에 파일을 생성해주세요."
except Exception as e:
    about_text = f"오류: 파일을 읽는 중 문제가 발생했습니다 - {e}"


# 파일에서 읽어온 내용 표시
st.info("왼쪽 사이드바에서 채팅으로 이동할 수 있습니다.")
st.write(about_text, unsafe_allow_html=True) 
stmd.st_mermaid(f"""
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
""", zoom=False, show_controls=False)
st.write(about_text2, unsafe_allow_html=True) 
st.image(file_path4, output_format="auto", width=800)
st.markdown("<br>", unsafe_allow_html=True)
st.write(about_text3, unsafe_allow_html=True) 