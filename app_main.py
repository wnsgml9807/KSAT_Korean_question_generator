# ChromaDB가 최신 sqlite3를 사용하도록 설정
# __import__('pysqlite3')
# import sys
# sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import streamlit as st
import requests
import time
import os
import glob
import uuid
import logging # 로깅 추가
# from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction # 사용 안 함
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
# 로깅 설정 (기본 설정)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# 페이지 설정
st.set_page_config(page_title="수능 국어 지문 생성기", page_icon="📄", layout="wide")


# --- 저장된 파일 전체 삭제 함수 ---
def clear_saved_files():
    """DB/saved 폴더 내의 모든 .json 파일을 삭제합니다."""
    saved_dir = os.path.join("DB", "saved")
    deleted_count = 0
    error_count = 0
    if os.path.exists(saved_dir):
        try:
            # .json 파일만 대상으로 변경 (다른 파일 보호)
            files_to_delete = glob.glob(os.path.join(saved_dir, "*.json"))
            if not files_to_delete:
                st.info("삭제할 저장된 파일이 없습니다.")
                return

            # 사용자 확인 단계 추가
            confirm = st.sidebar.warning(f"정말로 저장된 파일 {len(files_to_delete)}개를 모두 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다.", icon="⚠️")
            if confirm:
                 if st.sidebar.button("예, 모두 삭제합니다.", key="confirm_delete_all"):
                    with st.spinner("파일 삭제 중..."):
                        for f in files_to_delete:
                            try:
                                os.remove(f)
                                deleted_count += 1
                            except Exception as e_remove:
                                logger.error(f"Error removing file {f}: {e_remove}") # 로거 사용 (만약 로거가 설정되어 있다면) 또는 print
                                # print(f"Error removing file {f}: {e_remove}") # 로거 없을 시 print 사용
                                error_count += 1

                        if error_count == 0:
                            st.success(f"저장된 파일 {deleted_count}개를 모두 삭제했습니다.")
                        else:
                            st.error(f"파일 {error_count}개 삭제 중 오류가 발생했습니다. {deleted_count}개만 삭제되었습니다.")
                    st.rerun() # 삭제 후 상태 갱신

        except Exception as e:
            st.error(f"전체 파일 삭제 중 오류 발생: {e}")
            logger.error(f"Error clearing saved files: {e}", exc_info=True) # 로거 사용 권장
            # print(f"Error clearing saved files: {e}") # 로거 없을 시
    else:
        st.info("저장 폴더(DB/saved)가 존재하지 않습니다.")


pg = st.navigation([
    st.Page("app/app_chat.py", title="💬 채팅"),
    st.Page("app/app_text.py", title="📝 지문"),
])


# 사이드바 UI 구성
with st.sidebar:
    st.title("수능 국어 지문 생성기")
    st.write("Version 0.1.0")

    # 제작자 정보 표시
    st.info('''
    제작자 - 권준희
    wnsgml9807@naver.com
    ''')

    # 세션 초기화 버튼
    if st.button("🔄️ 세션 초기화"):
        # 세션 상태의 모든 키 삭제
        keys_to_clear = list(st.session_state.keys())
        for key in keys_to_clear:
            del st.session_state[key]
        st.success("세션이 초기화되었습니다. 페이지를 새로고침합니다.")
        time.sleep(1) # 메시지 표시 시간
        st.rerun() # 세션 초기화 후 새로고침

    # 전체 삭제 버튼
    if st.button("🗑️ 전체 삭제"):
         clear_saved_files() # 함수 호출

    # 서버 재시작 버튼 (필요시 유지) - 현재 제거된 상태
    # if st.button("🚀 서버 재시작"):
    #     ...

pg.run()