import streamlit as st
# ChromaDB가 최신 sqlite3를 사용하도록 설정
try:
    if st.secrets:
        __import__('pysqlite3')
        import sys
        sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except Exception as e:
    pass

import os
import logging
import time
# 페이지 설정 (가장 먼저 호출)
st.set_page_config(
    page_title="KSAT 국어 AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


pg = st.navigation([
    st.Page("app_chat.py", title="💬 채팅"),
    st.Page("app_text.py", title="📝 지문"),
])


# 사이드바 UI 구성
with st.sidebar:
    st.title("수능 독서 출제용 Agent")
    st.write("Version 0.1.0")

    st.info(
        """
        **제작자:** 권준희
        wnsgml9807@naver.com
        """
    )

    # 세션 초기화 버튼
    if st.button("🔄️ 세션 초기화"):
        keys_to_clear = list(st.session_state.keys())
        for key in keys_to_clear:
            del st.session_state[key]
        st.success("세션이 초기화되었습니다. 페이지를 새로고침합니다.")
        time.sleep(1)
        st.rerun()

pg.run()