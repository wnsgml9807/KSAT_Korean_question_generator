import streamlit as st
import logging
import os
import uuid
import requests
import json
import re
import time

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="KSAT 국어 출제용 AI",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

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
        # 세션 ID를 새로 생성
        st.session_state.session_id = f"session_{uuid.uuid4()}"
        logger.info(f"세션 ID 재생성: {st.session_state.session_id}")
        
        # Streamlit 세션 상태 초기화
        keys_to_clear = list(st.session_state.keys())
        for key in keys_to_clear:
            if key != "session_id":  # session_id는 방금 새로 설정했으므로 삭제하지 않음
                del st.session_state[key]
                
        st.success("세션이 초기화되었습니다. 페이지를 새로고침합니다.")
        time.sleep(1)
        st.rerun()


# --- 백엔드 URL 설정 ---
try:
    # Streamlit Cloud 환경변수 또는 로컬 환경변수
    FASTAPI_SERVER_URL = st.secrets.get("FASTAPI_SERVER_URL") or os.environ.get("FASTAPI_SERVER_URL")
    if not FASTAPI_SERVER_URL:
        FASTAPI_SERVER_URL = "http://127.0.0.1:8000"
except Exception:
    FASTAPI_SERVER_URL = "http://127.0.0.1:8000"

logger.info(f"백엔드 서버: {FASTAPI_SERVER_URL}")

# --- 세션 상태 초기화 ---
if "messages" not in st.session_state:
    st.session_state.messages = []
    logger.info("세션 상태에 'messages' 초기화")

if "session_id" not in st.session_state:
    st.session_state.session_id = f"session_{uuid.uuid4()}"
    logger.info(f"새 세션 ID 생성: {st.session_state.session_id}")

# --- 저장된 메시지 표시 함수 ---
def render_message(message):
    """저장된 메시지를 타입에 따라 적절하게 렌더링하는 함수"""
    role = message.get("role", "unknown")
    content = message.get("content", "")
    
    # 사용자 메시지 표시
    if role == "user":
        with st.chat_message("user"):
            st.markdown(content)
        return
    
    # 어시스턴트 메시지 표시
    if role == "assistant":
        with st.chat_message("assistant"):
            # 플레이스홀더 30개 미리 생성
            placeholders = [st.empty() for _ in range(30)]
            current_idx = 0
            
            # 메시지가 JSON 형식인지 확인
            try:
                msg_data = json.loads(content) if isinstance(content, str) else content
                if isinstance(msg_data, dict) and "messages" in msg_data:
                    current_agent = "supervisor"
                    
                    # 메시지 항목 순회
                    for item in msg_data["messages"]:
                        if item["type"] == "text":
                            # 일반 텍스트 메시지
                            with placeholders[current_idx].container():
                                st.markdown(item["content"])
                            current_idx += 1
                            
                        elif item["type"] == "tool":
                            # 도구 실행 결과
                            tool_name = item.get("name", "도구 실행 결과")
                            if tool_name in ["handoff_for_agent", "handoff_for_supervisor"]:
                                # 핸드오프는 일반 마크다운으로 표시
                                with placeholders[current_idx].container():
                                    st.markdown(item["content"])
                            else:
                                # 다른 도구들은 익스팬더로 표시
                                with placeholders[current_idx].expander(f"🛠️ {tool_name}"):
                                    st.code(item["content"])
                            current_idx += 1
                            
                        elif item["type"] == "agent_change":
                            # 에이전트 전환 시 새로운 섹션 시작
                            current_agent = item.get("agent", "unknown")
                            placeholders[current_idx].markdown(f"----- \n### {current_agent}:")
                            current_idx += 1
                            
                else:
                    # 기존 형식 지원
                    st.markdown(content)
            except (json.JSONDecodeError, TypeError):
                # 기존 메시지 형식 표시 (하위 호환성)
                st.markdown(content)

# --- 저장된 메시지 표시 ---
for message in st.session_state.messages:
    render_message(message)

# --- 사용자 입력 처리 ---
if prompt := st.chat_input("질문을 입력하세요..."):
    # 사용자 메시지를 세션 상태에 추가
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # 사용자 메시지 표시
    render_message({"role": "user", "content": prompt})

    # 어시스턴트 응답 처리 시작
    with st.chat_message("assistant"):
        # 플레이스홀더 30개 미리 생성
        placeholders = [st.empty() for _ in range(30)]
        
        # 현재 사용할 플레이스홀더 인덱스
        current_idx = 0
        
        # 메시지 저장용 객체
        message_data = {
            "messages": []
        }
        
        # 현재 텍스트 누적
        current_text = ""
        
        logger.info(f"백엔드 요청 전송 - 세션 ID: {st.session_state.session_id}, 프롬프트: {prompt[:50]}...")
        
        try:
            response = requests.post(
                f"{FASTAPI_SERVER_URL}/chat/stream",
                json={"prompt": prompt, "session_id": st.session_state.session_id},
                stream=True,
                timeout=600
            )
            response.raise_for_status()
            logger.info("백엔드 스트림 연결 성공")
            
            current_agent = "supervisor"
            for line in response.iter_lines(decode_unicode=True):
                if not line or not line.startswith("data: "):
                    continue
                try:
                    # 'data: ' 접두사 제거 및 JSON 파싱
                    payload = json.loads(line[6:])
                    msg_type = payload.get("type", "message")
                    text = payload.get("text", "")
                    agent = payload.get("response_agent", "unknown")
                    
                    if agent != current_agent:
                        # 현재 텍스트 저장 (있을 경우)
                        if current_text:
                            with placeholders[current_idx].container():
                                st.markdown(current_text)
                            message_data["messages"].append({
                                "type": "text",
                                "content": current_text
                            })
                            current_idx += 1
                            current_text = ""
                        
                        # 에이전트 전환 표시
                        with placeholders[current_idx].container():
                            st.markdown(f"----- \n### {agent}:")
                        message_data["messages"].append({
                            "type": "agent_change",
                            "agent": agent
                        })
                        current_agent = agent
                        current_idx += 1
                    
                    # 메시지 타입별 처리
                    if msg_type == "message":
                        # 일반 텍스트는 현재 플레이스홀더에 스트리밍
                        current_text += text
                        with placeholders[current_idx].container():
                            st.markdown(current_text)
                        
                    elif msg_type == "tool":
                        # 현재 텍스트 저장 (있을 경우)
                        if current_text:
                            with placeholders[current_idx].container():
                                st.markdown(current_text)
                            message_data["messages"].append({
                                "type": "text",
                                "content": current_text
                            })
                            current_idx += 1
                            current_text = ""
                        
                        # 도구 실행 결과를 새 플레이스홀더에 익스팬더로 표시
                        tool_name = payload.get("tool_name")
                        if tool_name == "handoff_for_agent" or tool_name == "handoff_for_supervisor":
                            with placeholders[current_idx].container():
                                st.markdown(text)
                        else:
                            with placeholders[current_idx].expander(f"🛠️ {tool_name}", expanded=True):
                                st.code(text)
                        
                        # 도구 실행 결과 저장
                        message_data["messages"].append({
                            "type": "tool",
                            "name": tool_name,
                            "content": text
                        })
                        current_idx += 1
                    
                    elif msg_type == "end":
                        # 최종 텍스트 저장
                        if current_text:
                            with placeholders[current_idx].container():
                                st.markdown(current_text)
                            message_data["messages"].append({
                                "type": "text",
                                "content": current_text
                            })
                        continue
                                        
                except json.JSONDecodeError as e:
                    logger.warning(f"JSON 파싱 실패, 데이터 무시: {line[6:]} (오류: {str(e)})")
                    with placeholders[current_idx].container():
                        st.error(f"JSON 파싱 오류: {str(e)}")
                    current_idx += 1
                    continue
                except Exception as e:
                    logger.error(f"메시지 처리 중 오류 발생: {str(e)}", exc_info=True)
                    with placeholders[current_idx].container():
                        st.error(f"메시지 처리 오류: {str(e)}")
                    current_idx += 1
                    continue
            
            # 완성된 어시스턴트 응답을 JSON 형태로 세션 상태에 저장
            st.session_state.messages.append({"role": "assistant", "content": message_data})
            logger.info("어시스턴트 응답 저장 완료")
            
        except requests.exceptions.RequestException as e:
            error_msg = f"백엔드 연결 오류: {e}"
            logger.error(error_msg, exc_info=True)
            with placeholders[current_idx].container():
                st.error(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
        except Exception as e:
            error_msg = f"응답 처리 중 오류 발생: {e}"
            logger.error(error_msg, exc_info=True)
            with placeholders[current_idx].container():
                st.error(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
