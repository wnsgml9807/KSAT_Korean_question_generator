import streamlit as st
import os
import streamlit_mermaid as stmd

# 현재 파일의 디렉토리를 기준으로 about.txt 경로 설정
file_path = os.path.join(os.path.dirname(__file__), "about.txt")
file_path2 = os.path.join(os.path.dirname(__file__), "about2.txt")
# about.txt 파일 읽기
try:
    with open(file_path, "r", encoding="utf-8") as f:
        about_text = f.read()
    with open(file_path2, "r", encoding="utf-8") as f:
        about_text2 = f.read()
except FileNotFoundError:
    about_text = "오류: `about.txt` 파일을 찾을 수 없습니다. `frontend/pages/` 디렉토리에 파일을 생성해주세요."
except Exception as e:
    about_text = f"오류: 파일을 읽는 중 문제가 발생했습니다 - {e}"


# 파일에서 읽어온 내용 표시
st.info("왼쪽 사이드바에서 채팅으로 이동할 수 있습니다.")
st.markdown(about_text, unsafe_allow_html=True) 
stmd.st_mermaid(f"""
graph LR
    %% ---------------- 노드 ----------------
    S((Supervisor))
    R([1.Researcher])
    A([2.Architecture])
    P([3.Passage<br/>Editor])
    Q([4.Question<br/>Editor])
    V([5.Validator])
    Z((End))

    %% --------- 통제권 전달(점선) ----------
    S -.-> R
    S -.-> A
    S -.-> P
    S -.-> Q
    S -.-> V

    %% ---------- 작업 흐름(굵은 화살표) ----------
    R ==> A ==> P ==> Q ==> V ==> Z


    %% ---------- 검증 피드백(선택) ----------
    V -->|수정 요청| S

""")
st.markdown(about_text2, unsafe_allow_html=True) 