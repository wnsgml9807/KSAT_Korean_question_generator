import streamlit as st
import time
import json
import logging
import os
import glob
import uuid
import re
import asyncio
import agent_server
# from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction # 사용되지 않으므로 주석 처리
from typing import Dict, List, Optional, Any, Union, AsyncGenerator

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = f"session_{uuid.uuid4()}"
# if "latest_passage_info" not in st.session_state: # 제거
#     st.session_state.latest_passage_info = {"title": "", "passage": ""} # 제거
# 폼 ID별 저장 성공/실패 상태를 관리하기 위한 딕셔너리 추가
if "form_save_status" not in st.session_state:
    st.session_state.form_save_status = {}
# 세션 전체에서 마지막으로 생성된 지문 텍스트 저장용 변수 추가
if "last_passage_text_in_session" not in st.session_state:
    st.session_state.last_passage_text_in_session = None


# --- 에이전트 초기화 및 캐싱 ---
@st.cache_resource
def get_agent():
    logger.info("--- 에이전트 초기화 시도 ---")
    agent = agent_server.initialize_agent()
    if agent:
        logger.info("--- 에이전트 초기화 성공 ---")
    else:
        logger.error("--- 에이전트 초기화 실패 ---")
    return agent

agent_executor = get_agent()

# 에이전트 초기화 실패 시 앱 중단
if not agent_executor:
    st.error("에이전트를 초기화할 수 없습니다. 앱을 재시작하거나 로그를 확인해주세요.")
    st.stop()
# ------------------------------

###################
# 도우미 함수들
###################

def typing_effect(text, speed=0.005):
    """문자열을 한 글자씩 yield하여 타이핑 효과 생성"""
    for char in text:
        yield char
        time.sleep(speed)


def save_message(role, content):
    """메시지를 세션에 저장하는 함수"""
    st.session_state.messages.append({
        "role": role,
        "content": content
    })

# --- 파일 저장 함수 (범용적으로 수정) ---
def save_data_to_json(file_path, data):
    """데이터를 JSON 파일에 저장"""
    try:
        save_dir = os.path.dirname(file_path)
        os.makedirs(save_dir, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"Data successfully saved to: {file_path}")
        return True
    except Exception as e:
        logger.error(f"Error saving file {file_path}: {e}", exc_info=True)
        return False

# --- 콜백 함수 (폼 ID 기반 저장 및 상태 업데이트) ---
def handle_save(form_id, title, content, question_text, success_placeholder):
    """폼 제출 시 실행될 콜백 함수 (폼 ID 기반 저장 및 상태 업데이트)"""
    logger.info(f"--- handle_save callback initiated for form_id: {form_id} ---")
    # 저장 경로를 DB/saved로 고정
    saved_dir = os.path.join("DB", "saved") # 경로 확인 및 고정
    permanent_save_path = os.path.join(saved_dir, f"{form_id}.json")
    data_to_save = {'title': title, 'passage': content, 'question': question_text}

    if save_data_to_json(permanent_save_path, data_to_save):
        st.session_state.form_save_status[form_id] = {"success": True, "message": "저장되었습니다!"}
        logger.info(f"--- Data for form {form_id} saved successfully to {permanent_save_path} ---")
    else:
        st.session_state.form_save_status[form_id] = {"success": False, "message": "저장 실패!"}
        logger.warning(f"--- Save failed for form {form_id} to {permanent_save_path} ---")

# --- passage_container_layout (최종 단순화) ---
def passage_container_layout(passage_text: str, is_new: bool):
    """지문 컨테이너 레이아웃 함수 (순수 텍스트 입력만 처리)"""
    import time as time_module
    container_id = f"passage_container_{time_module.time_ns()}_{uuid.uuid4()}"

    # 입력된 passage_text(순수 문자열)를 첫 줄바꿈으로 분리
    lines = passage_text.strip().split("\n", 1)
    title = lines[0] if lines else "제목 없음"
    content = lines[1].strip() if len(lines) > 1 else ""

    with st.container(key=container_id, border=True):
        if is_new: st.write_stream(typing_effect('### ' + title))
        else: st.markdown('### ' + title)
        if is_new: st.write_stream(typing_effect(content))
        else: st.markdown(content)
    return container_id

# --- passage_and_question_container_layout (is_new 추가 및 콜백 수정) ---
def passage_and_question_container_layout(title, content, question_text, is_new, form_id=None):
    """지문 폼 및 문제 레이아웃 함수 (is_new 플래그, form_id 기반 저장 콜백)"""
    # form_id가 제공되지 않으면 새로 생성
    if form_id is None:
        form_id = f"form_{uuid.uuid4()}"

    # 폼 생성
    with st.form(key=form_id, border=True):
        if is_new: st.write_stream(typing_effect('### ' + title))
        else: st.markdown('### ' + title) # markdown 사용

        # 지문은 항상 expander 안에 표시 (is_new 여부와 관계없이)
        with st.expander('지문 보기', expanded=False):
             st.markdown(content) # 항상 markdown 사용

        # 질문 표시
        if is_new:
            st.write_stream(typing_effect(question_text))
        else:
            st.markdown(question_text) # 항상 markdown 사용

        # --- 성공/실패 메시지 표시를 위한 placeholder ---
        status_placeholder = st.empty()
        # 저장 상태 확인 및 메시지 표시 (콜백 실행 후 리렌더링 시 표시됨)
        form_status = st.session_state.form_save_status.get(form_id)
        if form_status:
            if form_status["success"]:
                status_placeholder.success(form_status["message"])
            else:
                status_placeholder.error(form_status["message"])
            # 메시지 표시 후 상태 제거 (새로고침 시 다시 표시되지 않도록)
            # del st.session_state.form_save_status[form_id] # -> 콜백에서 상태 설정 후 즉시 표시 어려움. 일단 유지.

        # 저장 버튼 (콜백 함수에 form_id 전달)
        st.form_submit_button(
            "저장",
            on_click=handle_save,
            args=(form_id, title, content, question_text, status_placeholder) # permanent_save_path 대신 form_id 전달
        )
    return form_id


# --- 통합 렌더링 함수 ---
def render_message(message_content: Union[Dict, List, str], ai_placeholder_dict: Dict[str, Optional[st.delta_generator.DeltaGenerator]] = None, ai_text_dict: Dict[str, str] = None, is_new: bool = True):
    """스트리밍 또는 히스토리 메시지를 받아 UI를 렌더링합니다. is_new=True이면 스트리밍 효과 적용."""

    if ai_placeholder_dict is None: ai_placeholder_dict = {'current': None}
    if ai_text_dict is None: ai_text_dict = {'current': ""}

    if isinstance(message_content, list):
        for item in message_content:
            render_message(item, is_new=False) # 리스트 내 항목은 항상 is_new=False
        return

    elif isinstance(message_content, dict):
        msg_type = message_content.get("type")
        msg_text = message_content.get("text", "")
        tool_name = message_content.get("tool_name")

        placeholder = ai_placeholder_dict.get('current')
        full_text = ai_text_dict.get('current', "")

        if msg_type == "ai_token" and is_new:
            if placeholder is None:
                placeholder = st.empty()
                ai_placeholder_dict['current'] = placeholder
            full_text += msg_text
            ai_text_dict['current'] = full_text
            placeholder.markdown(full_text + " ▌")

        elif msg_type == "ai":
             st.markdown(msg_text)

        elif msg_type == "tool_end" or msg_type == "error":
            if is_new and placeholder is not None:
                placeholder.markdown(full_text)
                ai_placeholder_dict['current'] = None
                ai_text_dict['current'] = ""

            if msg_type == "tool_end":
                if tool_name == "generate_passage":
                    # UI 렌더링 (msg_text는 순수 지문 텍스트)
                    passage_container_layout(msg_text, is_new=is_new)

                elif tool_name == "generate_question":
                    # is_new True/False 관계없이 message_content에서 정보 추출
                    # run_agent_stream에서 이 키들이 message_content에 추가되었음
                    title = message_content.get("title", "제목 없음")
                    passage = message_content.get("passage", "지문 없음")
                    question_text = msg_text # 'text' 키에 질문 내용이 있음
                    form_id = message_content.get("form_id")

                    if not form_id:
                         form_id = f"form_missing_{uuid.uuid4()}" # form_id 없으면 임시 ID
                         logger.warning(f"generate_question message missing form_id. Assigning temporary ID: {form_id}")

                    # 필요한 정보가 있는지 확인 후 레이아웃 호출
                    if title != "제목 없음" and passage != "지문 없음" and question_text:
                         passage_and_question_container_layout(
                             title, passage, question_text, is_new=is_new, form_id=form_id
                         )
                    else:
                         # 정보 부족 시 경고 표시
                         logger.error(f"generate_question message (form_id: {form_id}) missing critical info in message_content: title='{title}' passage_len={len(passage)} question='{question_text}'")
                         st.warning(f"질문 ({tool_name}): 메시지 데이터 오류로 완전한 정보를 표시할 수 없습니다.")
                         with st.container(border=True):
                             st.markdown(f"**{tool_name} 결과 (정보 불완전):**")
                             if question_text:
                                 st.markdown(question_text)
                             else:
                                 st.markdown("*질문 내용을 찾을 수 없습니다.*")

                else: # 기타 도구
                    with st.expander(f"✔️ **{tool_name} 결과:**", expanded=is_new):
                        try:
                             if isinstance(msg_text, str):
                                result_data = json.loads(msg_text)
                                st.json(result_data)
                             else:
                                st.json(msg_text)
                        except (json.JSONDecodeError, TypeError):
                             st.code(str(msg_text) if msg_text is not None else "결과 없음", language="text")

            elif msg_type == "error":
                error_source = f" (`{tool_name}`)" if tool_name else ""
                st.error(f"**오류 발생{error_source}:** {msg_text or '상세 정보 없음'}")

        else: # tool_start 등 무시
            pass

    elif isinstance(message_content, str): # 사용자 메시지 등
         st.markdown(message_content)

    else: # 알 수 없는 타입
        st.write(str(message_content))

###################
# 메인 UI 코드 (스트리밍 로직 수정)
###################

# --- 콜백 함수에서 설정한 전역 상태 메시지 제거 ---
# if st.session_state.get("save_success", False): ... (제거)
# if st.session_state.get("save_error", False): ... (제거)
# 폼 내부에서 상태를 표시하므로 전역 메시지는 필요 없음

if st.session_state.get("page_switch_error", False):
    st.error("페이지 전환에 실패했습니다. 수동으로 이동해주세요.")
    st.session_state.page_switch_error = False

# --- 기존 메시지 표시 (통합 render_message 사용) ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        # is_new=False 로 호출하여 스트리밍 효과 없이 렌더링
        render_message(message["content"], is_new=False)


# 사용자 입력 처리
prompt = st.chat_input("질문을 입력하세요...")
if prompt:
    save_message("user", prompt)
    with st.chat_message("user"):
        # 사용자 메시지도 통합 렌더러 사용 (is_new=False)
        render_message(prompt, is_new=False)

    with st.chat_message("assistant"):
        try:
            # 스트리밍 및 렌더링 상태 관리 변수
            ai_placeholder_dict = {'current': None}
            ai_text_dict = {'current': ""}
            full_event_stream = [] # 최종 저장용

            # 비동기 스트림 처리 및 렌더링
            async def run_agent_stream():
                last_passage_text_in_stream = None # 현재 스트림 내 마지막 지문 텍스트 저장용

                async for msg in agent_server.generate_agent_response(agent_executor, prompt, st.session_state.session_id):
                    msg_type = msg.get("type")
                    tool_name = msg.get("tool_name")

                    # generate_passage 결과 텍스트 저장 (스트림 변수 및 세션 변수 모두)
                    if msg_type == "tool_end" and tool_name == "generate_passage":
                        passage_text = msg.get("text", "")
                        last_passage_text_in_stream = passage_text # 스트림 변수 업데이트
                        st.session_state.last_passage_text_in_session = passage_text # 세션 변수 업데이트
                        logger.info("Stored passage text from current stream and updated session state.")

                    # generate_question 처리 시 연관 지문 찾기 (우선순위 적용)
                    elif msg_type == "tool_end" and tool_name == "generate_question":
                        passage_to_associate = None
                        source = "none" # 지문 출처 추적용

                        # 1순위: 현재 스트림에서 생성된 지문 사용
                        if last_passage_text_in_stream:
                            passage_to_associate = last_passage_text_in_stream
                            source = "stream"
                        # 2순위: 세션에서 가장 마지막으로 생성된 지문 사용
                        elif st.session_state.last_passage_text_in_session:
                            passage_to_associate = st.session_state.last_passage_text_in_session
                            source = "session"

                        # 연관 지문 텍스트 파싱
                        title = "연관 지문 없음"
                        passage = "연관된 지문 정보를 찾을 수 없습니다."
                        if passage_to_associate:
                            try:
                                lines = passage_to_associate.strip().split("\n", 1)
                                title = lines[0] if lines else "제목 없음"
                                passage = lines[1].strip() if len(lines) > 1 else ""
                                logger.info(f"Associated passage '{title[:20]}...' (from {source}) with question.")
                            except Exception as e:
                                logger.error(f"Error parsing associated passage text (from {source}): {e}")
                                title = "지문 파싱 오류"
                                passage = f"연관된 지문 텍스트(출처: {source}) 파싱 중 오류 발생:\n{passage_to_associate}"
                        else:
                            logger.warning("generate_question: Could not find any preceding passage in stream or session.")

                        # 메시지에 title, passage, form_id 추가
                        msg["title"] = title
                        msg["passage"] = passage
                        msg["form_id"] = f"form_{uuid.uuid4()}"
                        logger.info(f"Added title/passage/form_id to generate_question message (form_id: {msg['form_id']}, source: {source}).")

                    # 메시지 렌더링 (is_new=True)
                    render_message(msg, ai_placeholder_dict, ai_text_dict, is_new=True)

                    # 최종 저장용 스트림에 추가
                    full_event_stream.append(msg)

                    await asyncio.sleep(0.005)
                # --- 여기까지 async for 루프 ---

                # 마지막 AI 텍스트 완료 처리 (루프 밖)
                if ai_placeholder_dict['current'] is not None:
                     ai_placeholder_dict['current'].markdown(ai_text_dict['current'])

                # 최종 메시지 저장 로직 (루프 밖)
                final_messages_to_save = []
                temp_ai_text = ""
                for event in full_event_stream:
                    event_type = event.get("type")
                    if event_type == "ai_token":
                        temp_ai_text += event.get("text", "")
                    elif event_type != "tool_start":
                        if temp_ai_text:
                            final_messages_to_save.append({"type": "ai", "text": temp_ai_text})
                            temp_ai_text = ""
                        final_messages_to_save.append(event)
                if temp_ai_text:
                    final_messages_to_save.append({"type": "ai", "text": temp_ai_text})

                if final_messages_to_save:
                    save_message("assistant", final_messages_to_save)

            # run_agent_stream 호출 (try 블록 내부)
            asyncio.run(run_agent_stream())

        except Exception as e:
            logger.error(f"AI 응답 생성/처리 중 외부 오류 발생: {e}", exc_info=True)
            st.error(f"요청 처리 중 심각한 오류 발생: {str(e)}")

# --- (추가) 대화 초기화 시 임시 파일 삭제 로직 (app_main.py로 이동됨) --- 
# def clear_my_temp_passage_files(): ... 