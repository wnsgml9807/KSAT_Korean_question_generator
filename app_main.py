import streamlit as st
from st_screen_stats import ScreenData
import logging
import os
import uuid
import requests
import json
import re
import time
import streamlit_mermaid as stmd  # 머메이드 라이브러리 추가
from streamlit import Page # Import Page
import hashlib # 비밀번호 해싱을 위해 추가
from typing import Dict, Any

# Configuration class for app settings
class Config:
    """Application configuration settings"""
    def __init__(self):
        self.page_title = "KSAT Agent"
        self.page_icon = "📚"
        self.layout = "wide"
        self.sidebar_state = "expanded"
        self.version = "0.6.0"
        self.author = "권준희"
        self.where = "연세대학교 교육학과"
        self.contact = "wnsgml9807@naver.com"
        self.about_page_path = "pages/about.py" # Add path for about page
        
        # Backend URL configuration
        try:
            self.backend_url = st.secrets.get("FASTAPI_SERVER_URL") or os.environ.get("FASTAPI_SERVER_URL")
            if not self.backend_url:
                self.backend_url = "http://127.0.0.1:8000"
        except Exception:
            self.backend_url = "http://127.0.0.1:8000"

# Logging setup
def setup_logging():
    """Configure logging for the application"""
    # 로깅 포맷에 사용자 이름 추가 준비 (실제 추가는 로깅 시점에)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s' # 포맷은 그대로 두거나 필요시 수정
    )
    return logging.getLogger(__name__)

# Session Management
class SessionManager:
    """Manages application session state"""
    
    @staticmethod
    def initialize_session(logger):
        """Initialize session state variables if they don't exist"""
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        if "session_id" not in st.session_state:
            st.session_state.session_id = f"session_{uuid.uuid4()}"
        
        # 뷰포트 높이 초기화 (세션에 없을 경우)
        if "viewport_height" not in st.session_state:
            st.session_state.viewport_height = 800 # 기본 높이 설정
        
        # 스트리밍 상태 플래그 초기화
        if "is_streaming" not in st.session_state:
            st.session_state.is_streaming = False
        
        if "input" not in st.session_state:
            st.session_state.input = None
            
        if "current_agent" not in st.session_state:
            st.session_state["current_agent"] = "supervisor"  

        # 추가된 세션 상태 값 초기화
        if "last_stream_ending_agent" not in st.session_state:
            st.session_state.last_stream_ending_agent = None # 또는 "supervisor"로 초기화 가능
        if "is_first_stream_for_session" not in st.session_state:
            st.session_state.is_first_stream_for_session = True

    @staticmethod
    def reset_session(logger):
        """Reset the session state, preserving only viewport_height"""
        current_session_id = st.session_state.get("session_id")
        current_viewport_height = st.session_state.get("viewport_height")
        logger.info(f"세션 리셋 요청 (ID: {current_session_id}).")

        # 세션 변수 정리 (viewport_height만 제외)
        keys_to_clear = list(st.session_state.keys())
        for key in keys_to_clear:
            if key not in ["viewport_height"]:
                del st.session_state[key]
        
        # 새 세션 ID 생성
        st.session_state.session_id = f"session_{uuid.uuid4()}"
        logger.info(f"새 세션 ID 생성됨: {st.session_state.session_id}")
        
        # 필수 세션 변수 다시 초기화
        st.session_state.messages = []
        st.session_state.is_streaming = False
        st.session_state.last_stream_ending_agent = None
        st.session_state.is_first_stream_for_session = True
        
        # 페이지 새로고침 수행
        st.toast("대화가 초기화되었습니다.", icon="🔄")
        st.rerun()

    @staticmethod
    def add_message(role, content):
        """Add a message to the session state"""
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        st.session_state.messages.append({"role": role, "content": content})
        
        
        
# UI Components
class UI:
    """UI component management"""
    
    @staticmethod
    def setup_page_config(config):
        """Configure the Streamlit page settings"""
        st.set_page_config(
            page_title=config.page_title,
            page_icon=config.page_icon,
            layout=config.layout,
            initial_sidebar_state=config.sidebar_state,
            menu_items=None
        )
    
    @staticmethod
    def add_custom_css():
        """Add custom CSS styles to the page"""
        st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Nanum+Myeongjo:wght@400;700;800&display=swap');
        .passage-font {
            border: 0.5px solid black;
            border-radius: 0px;
            padding: 10px;
            margin-bottom: 20px;
            font-family: 'Nanum Myeongjo', serif !important;
            line-height: 1.7;
            letter-spacing: -0.01em;
            font-weight: 500;
        }
        .passage-font p {
            text-indent: 1em; /* 각 문단의 첫 줄 들여쓰기 */
            margin-bottom: 0em;
        }
        .question-font {
            font-family: 'Nanum Myeongjo', serif !important;
            line-height: 1.7em;
            letter-spacing: -0.01em;
            font-weight: 500;
            margin-bottom: 1.5em;
        }
        """, unsafe_allow_html=True)
    

    @staticmethod
    def create_sidebar(config, logger):
        """Create sidebar, detect screen height, and update session state."""
        with st.sidebar:
            st.title("KSAT Agent")
            st.write(f"version {config.version}")
            
            st.info(
                f"""
                **제작자:** {config.author}
                {config.contact}
                """
            )
            
            
            if not st.session_state.get("is_streaming", False):
                try:
                    with st.container(border=False, height=1):
                        screen_data = ScreenData()
                        stats = screen_data.st_screen_data() # 컴포넌트 로딩 및 값 가져오기

                    if stats and "innerHeight" in stats:
                        height = stats.get("innerHeight")
                        if height is not None and isinstance(height, (int, float)) and height > 0:
                            # 세션 상태에 최신 높이 저장/업데이트 (현재 높이와 다를 경우에만 업데이트 고려 가능)
                            if st.session_state.get("viewport_height") != height:
                                st.session_state.viewport_height = height
                        else:
                            pass
                except Exception as e:
                    pass
                    # 오류 발생 시에도 세션 상태에 viewport_height가 없으면 기본값 설정
                    if "viewport_height" not in st.session_state:
                        st.session_state.viewport_height = 800 # 기본값 설정

            # Session reset button
            if st.button("🔄️ 대화 새로고침", use_container_width=True, type="primary"):
                # 리셋 시 viewport_height는 SessionManager.reset_session에서 유지됨
                SessionManager.reset_session(logger)
                st.success("대화 기록이 초기화됩니다.")
                time.sleep(1)
                st.rerun()
    
    @staticmethod
    def create_layout(viewport_height):
        """Create the main layout with columns"""
        # Create main columns
        chat_column, artifact_column = st.columns([3, 5], vertical_alignment="top", gap="medium")
        
        # Chat container
        with chat_column:
            # 채팅 컨테이너 높이 설정 (전체 뷰포트 높이에서 약간의 여유분 제외)
            chat_container = st.container(border=True, height=max(viewport_height - 60, 300)) 
            response_status = st.status("에이전트 응답 완료", state="complete")
            
        # Artifact containers
        with artifact_column:
            # welcome_placeholder 생성 제거
            # welcome_placeholder = st.empty()
            
            passage_column, question_column = st.columns(2, vertical_alignment="top")
            
            # passage_placeholder를 담는 컨테이너에 높이 고정
            with passage_column:
                with st.container(border=False, height=viewport_height): 
                    passage_placeholder = st.empty()
            
            # question_placeholder를 담는 컨테이너에 높이 고정
            with question_column:
                with st.container(border=False, height=viewport_height): 
                    question_placeholder = st.empty()
        
        # welcome_placeholder 반환 제거
        return chat_container, passage_placeholder, question_placeholder, response_status
    
    @staticmethod
    def calculate_viewport_height(screen_height):
        """Calculate viewport height based on screen height"""
        if screen_height is not None:
            return max(int(screen_height) - 250, 300)
        else:
            return 300 # Keep default

# Message Handling
class MessageRenderer:
    """Handles message rendering and processing"""
    
    def __init__(self, chat_container, passage_placeholder, question_placeholder, logger):
        self.chat_container = chat_container
        self.passage_placeholder = passage_placeholder
        self.question_placeholder = question_placeholder
        self.logger = logger
    
    def _get_friendly_tool_name(self, tool_name):
        """Translate internal tool names to user-friendly names."""
        if tool_name == "retrieve_data":
            return "기출 DB 검색"
        elif tool_name == "retrieve_subject_collection":
            return "기출 주제 조회"
        elif tool_name == "concept_map_manual":
            return "개념 지도 작성 지침 열람"
        elif tool_name == "google_search_node":
            return "Google 검색"            
        # 다른 도구 이름 변환 규칙 추가 가능
        return tool_name
    
    def render_message(self, message):
        """Render a message based on its role and content"""
        role = message.get("role", "unknown")
        content = message.get("content", "")
        
        # Handle user messages
        if role == "user":
            with self.chat_container:
                with st.chat_message("user"):
                    st.markdown(content, unsafe_allow_html=True)
            return
        
        # Handle assistant messages
        if role == "assistant":
            with self.chat_container:
                with st.container(border=False):
                    # Create placeholders for streaming content
                    placeholders = [st.empty() for _ in range(100)]
                    current_idx = 0
                
                # Process content
                self._process_assistant_content(content, placeholders, current_idx)
    
    def _process_assistant_content(self, content, placeholders, current_idx):
        """Process and render assistant message content"""
        # Parse content if it's a string
        
        if isinstance(content, str):
            try:
                msg_data = json.loads(content)
            except (json.JSONDecodeError, TypeError):
                # Not JSON, render as plain text
                st.markdown(content, unsafe_allow_html=True)
                return
        else:
            # Already a dictionary
            msg_data = content
        
        # Process structured messages
        if isinstance(msg_data, dict) and "messages" in msg_data:
            for item in msg_data["messages"]:
                item_type = item.get("type", "")
                item_agent = item.get("agent", "")
                item_content = item.get("content", "")
                item_info = item.get("info", "")
                
                # Handle text messages
                if item_type == "text":
                    # 수정: 아티팩트 텍스트와 일반 텍스트 분리 처리
                    if item_agent in ["passage_editor", "question_editor"]:
                        # 1. 완료 상태 표시 (placeholder 사용)
                        status_label = "지문 작성 완료" if item_agent == "passage_editor" else "문제 작성 완료"
                        with placeholders[current_idx].status(f"{status_label}", state="complete", expanded=False):
                            pass # 내용 없음
                        current_idx += 1 # 상태 표시 후 인덱스 증가
                        
                        # 2. 실제 텍스트는 아티팩트 패널에만 렌더링
                        self._render_text_item(item, item_agent)
                    else:
                        # 일반 텍스트 메시지는 placeholder 사용
                        if current_idx < len(placeholders):
                            with placeholders[current_idx].container(border=False):
                                st.markdown(item_content, unsafe_allow_html=True)
                        else:
                            st.markdown(item_content, unsafe_allow_html=True)
                        current_idx += 1
                    
                # Handle tool execution results
                elif item_type == "tool":
                    # _render_tool_item 내부에서 placeholder 인덱스를 사용하므로,
                    # 호출 전에 인덱스 유효성 검사도 고려할 수 있음
                    if current_idx < len(placeholders):
                        self._render_tool_item(item, placeholders, current_idx)
                        current_idx += 1 # 도구 아이템 처리 후 인덱스 증가
                    else:
                        st.warning(f"도구 표시 오류: {self._get_friendly_tool_name(item.get('name', ''))}")
                    
                # Handle agent changes
                elif item_type == "agent_change":
                    if item_agent == "system":
                        if item_info == "end":
                            with placeholders[current_idx].container(border=False):
                                st.success("에이전트의 응답이 종료되었습니다.")
                        elif item_info == "error":
                            with placeholders[current_idx].container(border=False):
                                st.error(item_content)
                    else:
                        # Display agent change
                        with placeholders[current_idx].container(border=False):
                            st.info(f"{item_agent} 에이전트에게 통제권을 전달합니다.")
                            
                    current_idx += 1
        else:
            # Render plain content
            st.markdown(str(content))
    
    def _render_text_item(self, item, agent):
        """Render text message content to the appropriate artifact panel."""
        if agent == "passage_editor":
            with self.passage_placeholder:
                st.markdown(item["content"], unsafe_allow_html=True)
        elif agent == "question_editor":
            with self.question_placeholder:
                st.markdown(item["content"], unsafe_allow_html=True)
    
    def _render_tool_item(self, item, placeholders, idx):
        """Render tool execution results according to final desired state."""
        tool_name = item.get("name", "도구 실행 결과")
        tool_content = item.get("content", "") # Get content for mermaid
        
        # Get friendly name for display
        friendly_tool_name = self._get_friendly_tool_name(tool_name)
        
        # Check if index is within bounds
        if idx >= len(placeholders):
            st.warning(f"도구 표시 오류: {friendly_tool_name}")
            return
            
        # Mermaid 도구: 확장된 완료 상태로 표시
        if tool_name == "mermaid_tool": # 내부 로직은 원래 이름 사용 유지
            with placeholders[idx].status(f"📊 개념 지도", state="complete", expanded=True):
                # --- Mermaid 렌더링 로직 복원 ---
                try:
                    mermaid_key = f"mermaid_render_{uuid.uuid4()}"
                    stmd.st_mermaid(tool_content, key=mermaid_key)
                except Exception as e:
                    st.error(f"Mermaid 렌더링 중 오류 발생: {e}")
                    st.code(tool_content)
                    self.logger.error(f"Mermaid 렌더링 오류: {e}", exc_info=True)
                # --- --------------------- ---
        elif tool_name == "google_search_node":
            with placeholders[idx].status(f"🔍 Google 검색", state="complete", expanded=False):
                st.markdown(tool_content, unsafe_allow_html=True)
        else:
            # 그 외 모든 도구: 축소된 완료 상태로 표시 (내용 숨김)
            current_placeholder = placeholders[idx]
            # Placeholder를 사용하여 완료 상태, 축소된 형태로 표시
            current_placeholder.status(f"{friendly_tool_name} 완료", state="complete", expanded=False)

# Backend Communication
class BackendClient:
    """Handles communication with the backend API"""
    
    def __init__(self, backend_url, chat_container, passage_placeholder, question_placeholder, response_status):
        self.backend_url = backend_url
        self.chat_container = chat_container
        self.passage_placeholder = passage_placeholder
        self.question_placeholder = question_placeholder
        self.response_status = response_status
        self.logger = logging.getLogger(__name__)

    def _get_friendly_tool_name(self, tool_name):
        """Translate internal tool names to user-friendly names."""
        if tool_name == "retrieve_data":
            return "기출 DB 검색"
        elif tool_name == "retrieve_subject_collection":
            return "기출 주제 조회"
        elif tool_name == "concept_map_manual":
            return "개념 지도 작성 지침 열람"
        elif tool_name == "google_search_node":
            return "Google 검색"            
        # 다른 도구 이름 변환 규칙 추가 가능
        return tool_name

    def send_message(self, prompt, session_id):
        """Send a message to the backend and process streaming response"""
        with self.chat_container:
            # Create more placeholders for streaming content (increased from 50 to 100)
            placeholders = [st.empty() for _ in range(100)]
            
            # Initialize message data storage
            message_data = {"messages": []}
            
            # 사용자 이름 가져오기 (로그 추적용)
            user_id = "anonymous" # 로그인 코드 제거로 인한 변경

            # 핵심 로그: 사용자 입력
            self.logger.info(f"User [{user_id}]: 프롬프트 전송됨\n{prompt}")

            try:
                # Setup the API request
                endpoint = f"{self.backend_url}/chat/stream"
                response = requests.post(
                    endpoint,
                    json={"prompt": prompt, "session_id": session_id, "user_id": user_id}, # user_id 추가
                    stream=True,
                    timeout=1200
                )
                response.raise_for_status()
                # self.logger.info("백엔드 스트림 연결 성공") # 로그 제거
                
                # 스트리밍 시작 시 플래그 설정
                st.session_state.is_streaming = True
                # Process streaming response
                return self._process_stream(response, placeholders, message_data)
                
            except requests.exceptions.RequestException as e:
                return self._handle_request_error(e, placeholders, 0) # 에러 처리 및 로깅 유지
            except Exception as e:
                return self._handle_generic_error(e, placeholders, 0) # 에러 처리 및 로깅 유지

    
    def _process_stream(self, response, placeholders, message_data):
        """Process streaming response from backend"""
        current_idx = 0
        current_text = ""
        previous_chunk_agent = None
        artifact_type = "chat"
        has_ended = False
        pending_tool_status_update = None

        # --- 세션 상태 값 가져오기 ---
        is_this_the_first_stream_of_session = st.session_state.is_first_stream_for_session
        last_stream_agent = st.session_state.last_stream_ending_agent
        # --- ------------------- ---

        try:
            # 초기 상태 설정
            with self.chat_container:
                self.response_status.update(label="에이전트 응답 중...", state="running")

            # --- 첫 스트림 플래그 업데이트 ---
            if is_this_the_first_stream_of_session:
                st.session_state.is_first_stream_for_session = False # 이제 첫 스트림 아님
            # --- ----------------------- ---

            for line in response.iter_lines(decode_unicode=True):
                if not line: continue

                # --- 이전 도구 상태 업데이트 (매 루프 시작 시) ---
                if pending_tool_status_update is not None:
                    prev_tool_name = pending_tool_status_update["tool_name"]
                    status_obj = pending_tool_status_update["status_obj"]
                    friendly_prev_tool_name = self._get_friendly_tool_name(prev_tool_name)
                    try:
                        status_obj.update(label=f"{friendly_prev_tool_name} 완료", state="complete", expanded=False)
                    except Exception as e:
                        self.logger.error(f"Error updating tool status ({friendly_prev_tool_name}): {e}", exc_info=True)
                    pending_tool_status_update = None # 업데이트 완료

                # --- 현재 라인 처리 ---
                try:
                    payload = json.loads(line)
                    msg_type = payload.get("type", "message")
                    text = payload.get("text", "")
                    current_chunk_agent = payload.get("response_agent", "unknown")

                    # --- 스트림 종료 처리 ---
                    if msg_type == "end" and current_chunk_agent == "system":
                        if current_text: # 남은 텍스트 처리
                            last_agent = previous_chunk_agent if previous_chunk_agent is not None else "unknown"
                            last_artifact_type = self._determine_artifact_type(last_agent)
                            self._update_artifact(current_text, last_artifact_type, placeholders, current_idx, is_final=True)
                            message_data["messages"].append({"type": "text", "content": current_text, "agent": last_agent})
                            self.logger.info(f'User [{st.session_state.get("username", "anonymous")}]: 에이전트 응답:{last_agent}\\n{current_text}')
                            current_idx += 1
                            current_text = ""
                        self.response_status.update(label="에이전트의 응답이 종료되었습니다.", state="complete")
                        message_data["messages"].append({"type": "agent_change", "agent": "system", "info": "end"})
                        has_ended = True
                        break

                    # --- 에러 메시지 처리 ---
                    elif msg_type == "error":
                        if current_text: # 남은 텍스트 처리
                            last_agent = previous_chunk_agent if previous_chunk_agent is not None else "unknown"
                            last_artifact_type = self._determine_artifact_type(last_agent)
                            self._update_artifact(current_text, last_artifact_type, placeholders, current_idx, is_final=True)
                            self.logger.info(f'User [{st.session_state.get("username", "anonymous")}]: 에이전트 응답:{last_agent}\\n{current_text}')
                            message_data["messages"].append({"type": "text", "content": current_text, "agent": last_agent})
                            current_idx += 1
                            current_text = ""
                        self.response_status.update(label="에러 발생 : " + text, state="error")
                        message_data["messages"].append({"type": "agent_change", "agent": "system", "info": "error", "content": text})
                        with placeholders[current_idx].container(border=False):
                            st.error(text)
                        current_idx += 1
                        previous_chunk_agent = current_chunk_agent # 에러 시점 에이전트 기록
                        continue

                    # --- 핸드오프 메시지 표시 로직 (수정됨: 플래그 제거) ---
                    # 조건 1: 스트림 시작 시 (첫 청크) 핸드오프 감지
                    if (previous_chunk_agent is None and
                        not is_this_the_first_stream_of_session and
                        last_stream_agent is not None and
                        current_chunk_agent != last_stream_agent and
                        current_chunk_agent != "system"):
                        # not handoff_message_shown_this_stream 조건 제거

                        self.logger.info(f'User [{st.session_state.get("username", "anonymous")}]: 스트림 시작 시 핸드오프 감지: {last_stream_agent} -> {current_chunk_agent}')
                        with placeholders[current_idx].container(border=False):
                            st.info(f"{current_chunk_agent} 에이전트에게 통제권을 전달합니다.")
                        message_data["messages"].append({"type": "agent_change", "agent": current_chunk_agent, "info": "handoff_start"})
                        current_idx += 1
                        # handoff_message_shown_this_stream = True # 플래그 업데이트 제거

                    # 조건 2: 스트림 도중 핸드오프 감지
                    elif (previous_chunk_agent is not None and
                          current_chunk_agent != previous_chunk_agent and
                          current_chunk_agent != "system"):
                          # not handoff_message_shown_this_stream 조건 제거

                        # 변경 직전 텍스트 처리 (previous_chunk_agent 기준)
                        if current_text:
                            prev_artifact_type = self._determine_artifact_type(previous_chunk_agent)
                            self._update_artifact(current_text, prev_artifact_type, placeholders, current_idx, is_final=True)
                            self.logger.info(f'User [{st.session_state.get("username", "anonymous")}]: 에이전트 응답:{previous_chunk_agent}\\n{current_text}')
                            message_data["messages"].append({"type": "text", "content": current_text, "agent": previous_chunk_agent})
                            current_idx += 1
                            current_text = ""

                        self.logger.info(f'User [{st.session_state.get("username", "anonymous")}]: 스트림 중 핸드오프 감지: {previous_chunk_agent} -> {current_chunk_agent}')
                        with placeholders[current_idx].container(border=False):
                             st.info(f"{current_chunk_agent} 에이전트에게 통제권을 전달합니다.")
                        message_data["messages"].append({"type": "agent_change", "agent": current_chunk_agent, "info": "handoff_midstream"})
                        current_idx += 1
                        # handoff_message_shown_this_stream = True # 플래그 업데이트 제거
                    # --- ------------------------------------------------- ---

                    # --- 이후 로직 (메시지/툴 처리) ---
                    artifact_type = self._determine_artifact_type(current_chunk_agent)

                    if msg_type == "message":
                        current_text += text
                        self._update_artifact(current_text, artifact_type, placeholders, current_idx)
                    elif msg_type == "tool":
                        # 도구 실행 전 텍스트 처리 (current_chunk_agent 기준)
                        if current_text:
                           self._update_artifact(current_text, artifact_type, placeholders, current_idx, is_final=True)
                           self.logger.info(f'User [{st.session_state.get("username", "anonymous")}]: 에이전트 응답:{current_chunk_agent}\\n{current_text}')
                           message_data["messages"].append({"type": "text", "content": current_text, "agent": current_chunk_agent})
                           current_idx += 1
                           current_text = ""

                        tool_name = payload.get("tool_name", "도구")
                        tool_content = text
                        friendly_tool_name = self._get_friendly_tool_name(tool_name)
                        message_data["messages"].append({
                            "type": "tool",
                            "name": tool_name,
                            "content": tool_content,
                            "agent": current_chunk_agent
                        })

                        if tool_name == "mermaid_tool":
                            with placeholders[current_idx].status(f"📊 개념 지도", state="complete", expanded=True):
                                try:
                                    mermaid_key = f"mermaid_render_{uuid.uuid4()}"
                                    stmd.st_mermaid(tool_content, key=mermaid_key)
                                except Exception as e:
                                    st.error(f"Mermaid 렌더링 중 오류 발생: {e}")
                                    st.code(tool_content)
                                    self.logger.error(f"Mermaid 렌더링 오류: {e}", exc_info=True)
                            current_idx += 1
                        elif tool_name == "google_search_node":
                            with placeholders[current_idx].status(f"🔍 Google 검색", state="complete", expanded=False):
                                st.markdown(tool_content, unsafe_allow_html=True)
                            current_idx += 1
                        else:
                            current_placeholder = placeholders[current_idx]
                            status_obj = current_placeholder.status(f"{friendly_tool_name} 중...", state="running", expanded=False)
                            pending_tool_status_update = { "tool_name": tool_name, "status_obj": status_obj }
                            current_idx += 1

                    # --- 루프 마지막: 이전 청크 에이전트 업데이트 ---
                    previous_chunk_agent = current_chunk_agent

                except json.JSONDecodeError as e:
                    self._handle_json_error(e, line, placeholders, current_idx)
                    current_idx += 1 # 에러 메시지 표시 후 인덱스 증가
                except Exception as e:
                    self._handle_stream_error(e, placeholders, current_idx)
                    current_idx += 1 # 에러 메시지 표시 후 인덱스 증가

            # --- 스트림 루프 종료 후 처리 ---
            if not has_ended and current_text:
                 last_processed_agent = previous_chunk_agent if previous_chunk_agent is not None else "unknown"
                 last_artifact_type = self._determine_artifact_type(last_processed_agent)
                 self._update_artifact(current_text, last_artifact_type, placeholders, current_idx, is_final=True)
                 self.logger.info(f'User [{st.session_state.get("username", "anonymous")}]: 최종 에이전트 응답:{last_processed_agent}\\n{current_text}')
                 message_data["messages"].append({"type": "text","content": current_text,"agent": last_processed_agent})

        finally:
            # --- 마지막 에이전트 상태 저장 ---
            if previous_chunk_agent is not None:
                 st.session_state.last_stream_ending_agent = previous_chunk_agent
            # --- ----------------------- ---
            st.session_state.is_streaming = False # 스트리밍 종료 시 플래그 해제

        return message_data
    
        def _parse_stream_line(self, line):
            """Parse a line from the SSE stream"""
        return json.loads(line[6:])  # Remove 'data: ' prefix
    
    def _determine_artifact_type(self, agent):
        """Determine artifact type based on agent"""
        if agent == "passage_editor":
            return "passage"
        elif agent == "question_editor":
            return "question"
        else:
            return "chat"
    
    def _update_artifact(self, text, artifact_type, placeholders, idx, is_final=False):
        """Update the appropriate artifact based on type"""
        # Check if index is within bounds
        if idx >= len(placeholders):
            return
            
        if artifact_type == "passage":
            status_text = "지문 작성 완료" if is_final else "지문 작성 중..."
            state = "complete" if is_final else "running"  # Always use valid state
            
            # Always show status for passage updates
            try:
                placeholders[idx].status(status_text, expanded=False, state=state)
            except Exception as e:
                pass
            
            # Update the passage content - 불필요한 div 태그 제거
            with self.passage_placeholder:
                st.markdown(text, unsafe_allow_html=True)
                
        elif artifact_type == "question":
            status_text = "문제 작성 완료" if is_final else "문제 작성 중..."
            state = "complete" if is_final else "running"  # Always use valid state
            
            # Always show status for question updates
            try:
                placeholders[idx].status(status_text, expanded=False, state=state)
            except Exception as e:
                pass
                
            # Update the question content - 불필요한 div 태그 제거
            with self.question_placeholder:
                st.markdown(text, unsafe_allow_html=True)
                
        else:
            # For regular chat messages, just use a container
            with placeholders[idx].container(border=False):
                st.markdown(text, unsafe_allow_html=True)
    
    def _handle_json_error(self, error, line, placeholders, idx):
        """Handle JSON parsing errors"""
        error_msg = f"JSON 파싱 오류: {str(error)}"
        self.logger.error(f"User [{st.session_state.get('username', 'anonymous')}]: JSON 파싱 실패, 데이터 무시: {line} (오류: {str(error)})", exc_info=True)
        
        # Check if index is within bounds
        if idx < len(placeholders):
            with placeholders[idx].container(border=False):
                st.error(error_msg)
        else:
            # If index is out of bounds, create a new error message
            st.error(error_msg)
    
    def _handle_stream_error(self, error, placeholders, idx):
        """Handle general errors during stream processing"""
        error_msg = f"메시지 처리 오류: {str(error)}"
        self.logger.error(f"User [{st.session_state.get('username', 'anonymous')}]: 메시지 처리 중 오류 발생: {str(error)}", exc_info=True)
        
        # Check if index is within bounds
        if idx < len(placeholders):
            with placeholders[idx].container(border=False):
                st.error(error_msg)
        else:
            # If index is out of bounds, create a new error message
            st.error(error_msg)
    
    def _handle_request_error(self, error, placeholders, idx):
        """Handle request errors"""
        error_msg = f"백엔드 연결 오류: {error}"
        self.logger.error(f"User [{st.session_state.get('username', 'anonymous')}]: {error_msg}", exc_info=True)
        
        # Check if index is within bounds
        if idx < len(placeholders):
            with placeholders[idx].container():
                st.error(error_msg)
        else:
            # If index is out of bounds, create a new error message
            st.error(error_msg)
            
        return error_msg
    
    def _handle_generic_error(self, error, placeholders, idx):
        """Handle generic errors"""
        error_msg = f"응답 처리 중 오류 발생: {error}"
        self.logger.error(f"User [{st.session_state.get('username', 'anonymous')}]: {error_msg}", exc_info=True)
        
        # Check if index is within bounds
        if idx < len(placeholders):
            with placeholders[idx].container():
                st.error(error_msg)
        else:
            # If index is out of bounds, create a new error message
            st.error(error_msg)
            
        return error_msg


# Main Application Page Logic
def show_main_app(config, logger):
    """Displays the main chat interface and handles interaction"""
       
    # 콜백 함수 정의 (show_main_app 내부) - 스트리밍 상태만 설정
    def on_submit():
        """채팅 입력 제출 시 호출되는 콜백 함수"""
        st.session_state.is_streaming = True
    
    # Initialize session (ensures messages/session_id/viewport_height exist)
    SessionManager.initialize_session(logger)

    # --- rerun 시 세션 상태에서 가장 최근 높이 값 사용 ---
    latest_detected_height = st.session_state.get("viewport_height", 800)
    viewport_height = UI.calculate_viewport_height(latest_detected_height)

    # --- 레이아웃 생성 ---
    chat_container, passage_placeholder, question_placeholder, response_status = UI.create_layout(viewport_height)
    
    
    # --- Helper 생성 ---
    message_renderer = MessageRenderer(chat_container, passage_placeholder, question_placeholder, logger)
    backend_client = BackendClient(config.backend_url, chat_container, passage_placeholder, question_placeholder, response_status)

    # 첫 메시지일 경우, 환영 메시지 표시
    if len(st.session_state.messages) == 0:
        with passage_placeholder.container():
            st.title("Welcome!")
            st.subheader(":thinking_face: 하단 입력창에 원하는 '분야'를 입력해 보세요!")
            st.markdown("🎯*예시 1: 인문 지문을 작성해 줘.*")
            st.markdown("🎯*예시 2: 과학 지문을 작성해 줘.*")
            st.markdown("🎯*예시 3: 복합 분야 지문을 작성해 줘.*")
            st.markdown(" ")
            st.markdown("ver : 0.6.3")
            st.code("""
            - 주제 선정 시 Google 검색 기능 추가
            - 개념 분해(DCS) 보고서 도입
            """)
    
    
    # --- 기존 메시지 표시 ---
    for message in st.session_state.messages:
        message_renderer.render_message(message)

    # --- 채팅 입력창 ---
    prompt = st.chat_input(
        "ex) 인문 지문을 작성하고 싶어",
        disabled=st.session_state.is_streaming,
        on_submit=on_submit
    )
    
    # --- 프롬프트 처리 ---
    if prompt:
        st.session_state.is_streaming = True
        
        # 1. 사용자 메시지를 먼저 상태에 추가
        SessionManager.add_message("user", prompt)

        # 3. 사용자 메시지 렌더링
        message_renderer.render_message({"role": "user", "content": prompt})

        # 4. 백엔드 호출 및 응답 처리
        try:
            response = backend_client.send_message(prompt, st.session_state.session_id)
            SessionManager.add_message("assistant", response)
            st.session_state.is_streaming = False
        except Exception as e:
             logger.error(f"백엔드 호출 중 오류 발생: {e}", exc_info=True)
             st.error(f"오류가 발생하여 응답을 처리할 수 없습니다: {e}")

        st.rerun() # st.rerun()은 JS 코드 추가 이후에 호출

# Application Entry Point
def main():
    """Main application entry point setting up pages and navigation"""
    # Setup
    config = Config()
    logger = setup_logging()

    # --- Common Elements Setup ---
    # Configure page settings globally (applies to all pages)
    UI.setup_page_config(config)
    # Add custom CSS globally
    UI.add_custom_css()
    # Create the common sidebar elements (title, info, reset button, height detection)
    # This function now primarily sets up the sidebar content and detects height.
    UI.create_sidebar(config, logger)
    # --- End Common Elements Setup ---


    # --- Page Definition ---
    # Define pages using st.Page
    # Use a lambda to pass config and logger to the main app function
    pages = [
        Page(lambda: show_main_app(config, logger), title="Agent", icon="🤖", default=True),
        Page(config.about_page_path, title="About", icon="📄")
    ]
    # --- End Page Definition ---

    # --- Navigation and Page Execution ---
    # Create the navigation menu (renders in the sidebar automatically)
    # and get the selected page object
    pg = st.navigation(pages)

    # Run the selected page's content
    pg.run()
    # --- End Navigation and Page Execution ---


if __name__ == "__main__":
    main()