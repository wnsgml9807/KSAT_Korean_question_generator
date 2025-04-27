import streamlit as st
import os

# 현재 파일의 디렉토리를 기준으로 about.txt 경로 설정
file_path = os.path.join(os.path.dirname(__file__), "about.txt")

# about.txt 파일 읽기
try:
    with open(file_path, "r", encoding="utf-8") as f:
        about_text = f.read()
except FileNotFoundError:
    about_text = "오류: `about.txt` 파일을 찾을 수 없습니다. `frontend/pages/` 디렉토리에 파일을 생성해주세요."
except Exception as e:
    about_text = f"오류: 파일을 읽는 중 문제가 발생했습니다 - {e}"

# 파일에서 읽어온 내용 표시
st.title("Multi-Agent 기반 지문 생성 시스템")
st.markdown("***2025-04-27 ver. 0.2.0***")
st.info("왼쪽 사이드바에서 채팅으로 이동할 수 있습니다.")
st.markdown(about_text) 