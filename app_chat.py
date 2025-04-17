import streamlit as st
import json
import logging
import os
import uuid
import requests
from typing import Dict, List, Optional, Union, Any

# --- 기본 설정 ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

FASTAPI_SERVER_URL = os.environ.get("FASTAPI_SERVER_URL", "http://127.0.0.1:8000")

# --- 세션 상태 초기화 ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = f"session_{uuid.uuid4()}"

# --- 렌더링 함수 ---

def render_tool_result(container, tool_name: str, msg_text: str):
    """도구 결과를 Expander 내에 렌더링합니다."""
    tool_label = f"✔️ **{tool_name}**"
    
    # st 모듈인 경우 직접 렌더링
    if container == st:
        with st.expander(tool_label, expanded=True):
            try:
                if isinstance(msg_text, str) and msg_text.strip().startswith(("{", "[")):
                    result_data = json.loads(msg_text)
                    st.json(result_data)
                else:
                    st.code(str(msg_text) if msg_text is not None else "결과 없음", language="text")
            except (json.JSONDecodeError, TypeError):
                st.code(str(msg_text) if msg_text is not None else "결과 없음", language="text")
    # 플레이스홀더인 경우 컨테이너로 사용
    else:
        with container:
            with st.expander(tool_label, expanded=True):
                try:
                    if isinstance(msg_text, str) and msg_text.strip().startswith(("{", "[")):
                            result_data = json.loads(msg_text)
                            st.json(result_data)
                    else:
                        st.code(str(msg_text) if msg_text is not None else "결과 없음", language="text")
                except (json.JSONDecodeError, TypeError):
                        st.code(str(msg_text) if msg_text is not None else "결과 없음", language="text")

def render_error_message(container, tool_name: Optional[str], msg_text: str):
    """오류 메시지를 렌더링합니다."""
    error_source = f" (`{tool_name}`)" if tool_name else ""
    
    # st 모듈인 경우 직접 렌더링
    if container == st:
        st.error(f"**오류 발생{error_source}:** {msg_text or '상세 정보 없음'}")
    # 플레이스홀더인 경우 컨테이너로 사용
    else:
        with container:
                st.error(f"**오류 발생{error_source}:** {msg_text or '상세 정보 없음'}")

def display_message_content(message_content: Union[str, List[Dict]]):
    """메시지 내용을 화면에 표시 (텍스트 또는 이벤트 스트림 처리)"""
    if isinstance(message_content, str):
        st.markdown(message_content)
        return

    if not isinstance(message_content, list):
        logger.warning(f"알 수 없는 메시지 형식: {type(message_content)}")
        st.markdown(str(message_content))
        return

    # --- 이벤트 리스트 처리 로직 (주로 히스토리 렌더링용) ---
    current_ai_text_buffer = ""
    for event in message_content:
        if not isinstance(event, dict): continue

        event_type = event.get("type")
        tool_name = event.get("tool_name")
        text = event.get("text", "")

        if event_type == "ai_token":
            current_ai_text_buffer += text
        elif event_type == "tool_start":
            if current_ai_text_buffer:
                st.markdown(current_ai_text_buffer)
                current_ai_text_buffer = ""
        elif event_type == "tool_end":
            if current_ai_text_buffer:
                st.markdown(current_ai_text_buffer)
                current_ai_text_buffer = ""
            if tool_name:
                render_tool_result(st, tool_name, text)
        elif event_type == "error":
            if current_ai_text_buffer:
                st.markdown(current_ai_text_buffer)
                current_ai_text_buffer = ""
            render_error_message(st, tool_name, text)

    # 루프 종료 후 남은 텍스트 출력
    if current_ai_text_buffer:
        st.markdown(current_ai_text_buffer)


# --- 메인 UI 로직 ---

# 1. 스크립트 실행 시 모든 이전 메시지 표시
logger.info(f"Rendering history: {len(st.session_state.messages)} messages.")
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        try:
            display_message_content(message["content"])
        except Exception as e:
            logger.error(f"Error rendering history message ({message['role']}): {e}", exc_info=True)
            st.error(f"{message['role']} 메시지 렌더링 중 오류 발생")

# 2. 사용자 입력 처리
if prompt := st.chat_input("질문을 입력하세요..."):
    # 2.1 사용자 메시지 저장
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2.2 사용자 메시지 즉시 표시
    with st.chat_message("user"):
        display_message_content(prompt)

    # 3. AI 응답 처리 시작
    with st.chat_message("assistant"):
        full_event_stream = []
        # 스트리밍할 텍스트와 도구 결과를 순서대로 표시하기 위한 placeholder 배열
        placeholders = []
        current_placeholder_index = 0
        MAX_PLACEHOLDERS = 30  # 최대 20개 placeholder 미리 준비
        
        # 미리 충분한 placeholder를 생성
        for _ in range(MAX_PLACEHOLDERS):
            placeholders.append(st.empty())
        
        current_text_buffer = ""
        
        # 도구 상태를 추적하기 위한 딕셔너리
        active_tools: Dict[str, Any] = {}

        try:
            logger.info(f"Sending request to FastAPI: {FASTAPI_SERVER_URL}/chat/stream")
            response = requests.post(
                f"{FASTAPI_SERVER_URL}/chat/stream",
                json={"prompt": prompt, "session_id": st.session_state.session_id},
                stream=True,
                headers={"Accept": "text/event-stream"},
                timeout=300
            )
            response.raise_for_status()
            logger.info("Request successful, processing stream...")

            for line in response.iter_lines(decode_unicode=True):
                if line.startswith("data:"):
                    message_str = line[len("data: "):].strip()
                    if not message_str: continue
                    
                    try:
                        event = json.loads(message_str)
                        if not isinstance(event, dict):
                            continue

                        # 이벤트 기록
                        full_event_stream.append(event)

                        msg_type = event.get("type")
                        tool_name = event.get("tool_name", "")
                        run_id = event.get("run_id", "")
                        text = event.get("text", "")

                        if msg_type == "ai_token":
                            current_text_buffer += text
                            # 현재 텍스트 플레이스홀더에 누적 텍스트 표시
                            placeholders[current_placeholder_index].markdown(current_text_buffer + "▌")  # 타이핑 효과
                        
                        elif msg_type == "tool_start":
                            # 현재 텍스트 블록 마무리하고 다음 플레이스홀더로 이동
                            if current_text_buffer:
                                placeholders[current_placeholder_index].markdown(current_text_buffer)
                                current_text_buffer = ""
                                current_placeholder_index += 1
                            
                            # 도구 실행 상태 표시 및 추적 - st.status()를 직접 호출
                            if current_placeholder_index < MAX_PLACEHOLDERS:
                                # 직접 status 객체 생성
                                status = placeholders[current_placeholder_index].status(f"🔄 **{tool_name}** 실행 중...")
                                active_tools[run_id] = {
                                    "status": status,
                                    "placeholder_index": current_placeholder_index,
                                    "tool_name": tool_name
                                }
                                current_placeholder_index += 1
                        
                        elif msg_type == "tool_end":
                            # 도구 실행 상태 완료 처리
                            if run_id in active_tools:
                                tool_info = active_tools[run_id]
                                if tool_info["status"]:
                                    tool_info["status"].update(label=f"✅ **{tool_info['tool_name']}** 완료", state="complete")
                                # 해당 도구 플레이스홀더 다음에 결과 표시
                                if current_placeholder_index < MAX_PLACEHOLDERS:
                                    render_tool_result(placeholders[current_placeholder_index], tool_name, text)
                                    current_placeholder_index += 1
                                # 완료된 도구 추적에서 제거
                                del active_tools[run_id]
                            else:
                                # run_id가 없는 경우 일반적인 방식으로 처리
                                if current_placeholder_index < MAX_PLACEHOLDERS:
                                    render_tool_result(placeholders[current_placeholder_index], tool_name, text)
                                    current_placeholder_index += 1
                                
                        elif msg_type == "error":
                            # 도구 실행 상태 오류 처리
                            if run_id in active_tools:
                                tool_info = active_tools[run_id]
                                if tool_info["status"]:
                                    tool_info["status"].update(label=f"❌ **{tool_info['tool_name']}** 오류 발생", state="error")
                                # 해당 도구 플레이스홀더 다음에 오류 메시지 표시
                                if current_placeholder_index < MAX_PLACEHOLDERS:
                                    render_error_message(placeholders[current_placeholder_index], tool_name, text)
                                    current_placeholder_index += 1
                                # 오류 발생 도구 추적에서 제거
                                del active_tools[run_id]
                            else:
                                # run_id가 없는 경우 일반적인 방식으로 처리
                                if current_placeholder_index < MAX_PLACEHOLDERS:
                                    render_error_message(placeholders[current_placeholder_index], tool_name, text)
                                    current_placeholder_index += 1
                        
                        # 플레이스홀더 한계에 도달하면 더 이상 진행하지 않음
                        if current_placeholder_index >= MAX_PLACEHOLDERS - 1:
                            logger.warning(f"최대 플레이스홀더 수({MAX_PLACEHOLDERS})에 도달. 이후 내용 표시 불가.")
                            break

                    except json.JSONDecodeError as e:
                        logger.error(f"JSON Decode Error: {e}")
                        if current_placeholder_index < MAX_PLACEHOLDERS:
                            render_error_message(placeholders[current_placeholder_index], None, f"JSON 파싱 오류: {e}")
                            current_placeholder_index += 1
                    except Exception as e:
                        logger.error(f"Error processing message: {e}", exc_info=True)
                        if current_placeholder_index < MAX_PLACEHOLDERS:
                            render_error_message(placeholders[current_placeholder_index], None, f"처리 중 오류: {e}")
                            current_placeholder_index += 1

            # 스트림 종료 후 마지막 텍스트 표시
            if current_text_buffer and current_placeholder_index < MAX_PLACEHOLDERS:
                placeholders[current_placeholder_index].markdown(current_text_buffer)

            # 미완료된 도구 상태 처리
            for tool_id, tool_info in active_tools.items():
                if tool_info["status"]:
                    tool_info["status"].update(label=f"⚠️ **{tool_info['tool_name']}** 응답 없음", state="error")

            # 3.1 AI 응답 전체 저장
            if full_event_stream:
                st.session_state.messages.append({"role": "assistant", "content": full_event_stream})
                logger.info("Assistant response saved to session state.")
            else:
                logger.warning("Assistant response stream was empty, not saved.")

        except requests.exceptions.RequestException as e:
            error_text = f"서버 연결 실패: {FASTAPI_SERVER_URL}. 서버가 실행 중인지 확인하세요. ({e})"
            logger.error(f"FastAPI connection error: {e}", exc_info=True)
            placeholders[0].error(error_text)
            # 실패 시 에러 메시지 저장
            st.session_state.messages.append({"role": "assistant", "content": [{"type": "error", "text": error_text}]})
        except Exception as e:
            error_text = f"요청 처리 중 알 수 없는 오류 발생: {e}"
            logger.error(f"Unknown error during request processing: {e}", exc_info=True)
            placeholders[0].error(error_text)
            # 실패 시 에러 메시지 저장
            st.session_state.messages.append({"role": "assistant", "content": [{"type": "error", "text": error_text}]}) 