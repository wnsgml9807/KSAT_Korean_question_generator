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

# Configuration class for app settings
class Config:
    """Application configuration settings"""
    def __init__(self):
        self.page_title = "KSAT 국어 출제용 AI"
        self.page_icon = "📚"
        self.layout = "wide"
        self.sidebar_state = "expanded"
        self.version = "0.4.0"
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
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
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
            logger.info("세션 상태에 'messages' 초기화")
        
        if "session_id" not in st.session_state:
            st.session_state.session_id = f"session_{uuid.uuid4()}"
            logger.info(f"새 세션 ID 생성: {st.session_state.session_id}")

        # 뷰포트 높이 초기화 (세션에 없을 경우)
        if "viewport_height" not in st.session_state:
            st.session_state.viewport_height = 800 # 기본 높이 설정
            logger.info(f"세션 상태에 'viewport_height' 초기화: {st.session_state.viewport_height}px")

        # 스트리밍 상태 플래그 초기화
        if "is_streaming" not in st.session_state:
            st.session_state.is_streaming = False
            logger.info("세션 상태에 'is_streaming' 초기화: False")
        
        if "input" not in st.session_state:
            st.session_state.input = None
            logger.info("세션 상태에 'input' 초기화: None")

    @staticmethod
    def reset_session(logger):
        """Reset the session state, preserving session_id and viewport_height"""
        # Generate new session ID (already done, but just confirming logic)
        # st.session_state.session_id = f"session_{uuid.uuid4()}"
        # logger.info(f"세션 ID 재생성: {st.session_state.session_id}") # This might be needed if we want a *new* session ID on reset

        # Get current session_id and viewport_height to preserve them
        current_session_id = st.session_state.get("session_id")
        current_viewport_height = st.session_state.get("viewport_height")
        logger.info(f"세션 리셋 전: session_id={current_session_id}, viewport_height={current_viewport_height}")

        # Clear all other session state variables
        keys_to_clear = list(st.session_state.keys())
        for key in keys_to_clear:
            # session_id 와 viewport_height 를 제외하고 모두 삭제
            if key not in ["session_id", "viewport_height"]:
                del st.session_state[key]
        
        # Re-initialize necessary session variables (like messages)
        st.session_state.messages = []
        # 스트리밍 상태도 리셋
        st.session_state.is_streaming = False
        logger.info("메시지 등 다른 세션 변수 초기화 완료 (session_id, viewport_height 유지됨)")
        # If session_id needs to be regenerated on reset, uncomment the lines above
        # And ensure the new session_id is kept here

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
        </style>
        """, unsafe_allow_html=True)
    

    @staticmethod
    def create_sidebar(config, logger):
        """Create sidebar, detect screen height, and update session state."""
        with st.sidebar:
            st.title("수능 독서 출제용 Agent")
            st.write(f"version {config.version}")
            
            st.info(
                f"""
                **제작자:** {config.author}
                {config.where}
                {config.contact}
                """
            )
            
            # --- 사이드바에서 높이 감지 및 세션 상태 업데이트 ---
            # 스트리밍 중이 아닐 때만 화면 크기 감지 실행
            if not st.session_state.get("is_streaming", False):
                try:
                    screen_data = ScreenData()
                    stats = screen_data.st_screen_data() # 컴포넌트 로딩 및 값 가져오기

                    if stats and "innerHeight" in stats:
                        height = stats.get("innerHeight")
                        if height is not None and isinstance(height, (int, float)) and height > 0:
                            # 세션 상태에 최신 높이 저장/업데이트 (현재 높이와 다를 경우에만 업데이트 고려 가능)
                            if st.session_state.get("viewport_height") != height:
                                st.session_state.viewport_height = height
                                # logger.info(f"사이드바에서 뷰포트 높이 업데이트: {height}px") # 변경 시에만 로깅
                        else:
                            logger.warning(f"사이드바: 수신된 높이 값 유효하지 않음: {height}")
                    else:
                         logger.warning(f"사이드바: innerHeight 찾을 수 없음: {stats}")
                except Exception as e:
                    logger.error(f"사이드바: 화면 데이터 얻기 실패: {str(e)}")
                    # 오류 발생 시에도 세션 상태에 viewport_height가 없으면 기본값 설정
                    if "viewport_height" not in st.session_state:
                         st.session_state.viewport_height = 800 # 기본값 설정
                    # logger.info(f"사이드바: 화면 데이터 얻기 실패, 현재 세션/기본 높이: {st.session_state.viewport_height}px")

            # 현재 세션의 높이 값 확인 (디버깅용, 로깅 불필요 시 주석 처리)
            # current_height_in_state = st.session_state.get("viewport_height", 800)
            # logger.info(f"현재 세션 뷰포트 높이 (사이드바 로딩 시점): {current_height_in_state}px")
            # --- --------------------------------------- ---


            # Session reset button
            if st.button("🔄️ 세션 초기화"):
                # 리셋 시 viewport_height는 SessionManager.reset_session에서 유지됨
                SessionManager.reset_session(logger)
                st.success("세션이 초기화되었습니다. (화면 높이 정보 유지됨)")
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
    
    def __init__(self, chat_container, passage_placeholder, question_placeholder):
        self.chat_container = chat_container
        self.passage_placeholder = passage_placeholder
        self.question_placeholder = question_placeholder
    
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
        
        logger = logging.getLogger(__name__)
        
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
                    self._render_text_item(item, item_agent, placeholders, current_idx)
                    current_idx += 1
                    
                # Handle tool execution results
                elif item_type == "tool":
                    self._render_tool_item(item, placeholders, current_idx)
                    current_idx += 1
                    
                # Handle agent changes
                elif item_type == "agent_change":
                    if item_agent == "system":
                        if item_info == "end":
                            with placeholders[current_idx].container(border=False):
                                st.success("에이전트의 응답이 종료되었습니다.")
                                logger.info("에이전트의 응답이 종료되었습니다.")
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
    
    def _render_text_item(self, item, agent, placeholders, idx):
        """Render text message from an agent"""
        if agent == "passage_editor":
            with self.passage_placeholder:
                st.markdown(item["content"], unsafe_allow_html=True)
        elif agent == "question_editor":
            with self.question_placeholder:
                st.markdown(item["content"], unsafe_allow_html=True)
        else:
            # Check if index is within bounds
            if idx < len(placeholders):
                with placeholders[idx].container(border=False):
                    st.markdown(item["content"], unsafe_allow_html=True)
            else:
                st.markdown(item["content"], unsafe_allow_html=True)
    
    def _render_tool_item(self, item, placeholders, idx):
        """Render tool execution results"""
        tool_name = item.get("name", "도구 실행 결과")
        
        # mermaid_tool 특별 처리
        if tool_name == "mermaid_tool":
            with placeholders[idx].expander(f"📊 개념 지도", expanded=True):
                # streamlit-mermaid 라이브러리 사용 (상단에 import 되어 있음)
                mermaid_key = f"mermaid_render_{uuid.uuid4()}"  # 고유한 키 생성
                stmd.st_mermaid(item["content"], key=mermaid_key)
                
        elif tool_name in ["handoff_for_agent", "handoff_for_supervisor"]:
            # Display handoffs in borderless container
            with placeholders[idx].container(border=False):
                st.markdown(item["content"])
        else:
            # Display other tools in expander
            with placeholders[idx].expander(f"🛠️ {tool_name} 도구를 사용합니다.", expanded=False):
                st.code(item["content"])

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
    def send_message(self, prompt, session_id):
        """Send a message to the backend and process streaming response"""
        with self.chat_container:
            # Create more placeholders for streaming content (increased from 50 to 100)
            placeholders = [st.empty() for _ in range(100)]
            
            # Initialize message data storage
            message_data = {"messages": []}
            
            self.logger.info(f"""백엔드 요청 전송됨\n세션 ID: {session_id}\n프롬프트:\n{prompt}""")
            
            try:
                # Setup the API request
                endpoint = f"{self.backend_url}/chat/stream"
                response = requests.post(
                    endpoint,
                    json={"prompt": prompt, "session_id": session_id},
                    stream=True,
                    timeout=1200
                )
                response.raise_for_status()
                self.logger.info("백엔드 스트림 연결 성공")
                
                # 스트리밍 시작 시 플래그 설정
                st.session_state.is_streaming = True
                # Process streaming response
                return self._process_stream(response, placeholders, message_data)
                
            except requests.exceptions.RequestException as e:
                return self._handle_request_error(e, placeholders, 0)
            except Exception as e:
                return self._handle_generic_error(e, placeholders, 0)

    
    def _process_stream(self, response, placeholders, message_data):
        """Process streaming response from backend"""
        current_idx = 0
        current_text = ""
        current_agent = "supervisor"
        artifact_type = "chat"
        has_ended = False  # 정상 종료 여부 추적
        
        logger = logging.getLogger(__name__)        
        
        try:
            # 초기 상태 설정
            with self.chat_container:
                self.response_status.update(label="에이전트 응답 중...", state="running")
            
            # for line in response.iter_lines(decode_unicode=True):
            for line in response.iter_lines(decode_unicode=True):
                if not line:
                    continue
                
                try:
                    # Parse event data
                    #payload = self._parse_stream_line(line)
                    payload = json.loads(line)
                    msg_type = payload.get("type", "message")
                    text = payload.get("text", "")
                    agent = payload.get("response_agent", "unknown")
                    
                    # 스트림 종료 메시지 특별 처리 (서버는 항상 마지막에 type=end, agent=system 보냄)
                    if msg_type == "end" and agent == "system":
                        # 현재 텍스트가 있으면 반드시 최종 업데이트 수행
                        if current_text:
                            self._update_artifact(current_text, artifact_type, placeholders, current_idx, is_final=True)
                            message_data["messages"].append({
                                "type": "text",
                                "content": current_text,
                                "agent": current_agent
                            })
                            logger.info(f'에이전트 응답:{current_agent}\n{current_text}')
                            current_idx += 1
                            current_text = ""  # 텍스트 초기화 (중요)
                            
                        # 종료 메시지 표시
                            with placeholders[current_idx].container(border=False):
                                st.success("에이전트의 응답이 종료되었습니다.")
                            
                        # 종료 메시지 표시
                        # with placeholders[current_idx].container(border=False):
                        #     st.success("에이전트의 응답이 종료되었습니다.")
                        self.response_status.update(label="에이전트의 응답이 종료되었습니다.", state="complete")
                        
                        message_data["messages"].append({
                            "type": "agent_change",
                            "agent": "system",
                            "info": "end"
                        })
                        
                        has_ended = True  # 정상 종료 표시
                        break
                    
                    # 에러 메시지 처리
                    elif msg_type == "error":
                        # 현재 텍스트가 있으면 저장
                        if current_text:
                            self._update_artifact(current_text, artifact_type, placeholders, current_idx, is_final=True)
                            logger.info(f'에이전트 응답:{current_agent}\n{current_text}')
                            # 에러 메시지 표시
                            with placeholders[current_idx].container(border=False):
                                st.error(text)
                            # 이전 텍스트 저장
                            message_data["messages"].append({
                                "type": "text",
                                "content": current_text,
                                "agent": current_agent
                            })
                            current_idx += 1
                            current_text = ""
                        
                        # 에러 메시지 표시
                        self.response_status.update(label="에러 발생 : " + text, state="error")
                        
                        message_data["messages"].append({
                            "type": "agent_change",
                            "agent": "system",
                            "info": "error",
                            "content": text
                        })
                        current_idx += 1
                        continue
                    
                    # 일반 에이전트 변경 처리
                    if agent != current_agent:
                        # 현재 텍스트가 있으면 저장
                        if current_text:
                            logger.info(f'에이전트 응답:{current_agent}\n{current_text}')
                            self._update_artifact(current_text, artifact_type, placeholders, current_idx, is_final=True)
                            message_data["messages"].append({
                                "type": "text",
                                "content": current_text,
                                "agent": current_agent
                            })
                            current_idx += 1
                            current_text = ""
                        
                        # system 에이전트가 아닌 경우만 에이전트 변경 메시지 표시
                        if agent != "system":
                            logger.info(f'에이전트 변경:{current_agent} to {agent}')
                            with placeholders[current_idx].container(border=False):
                                st.info(f"{agent} 에이전트에게 통제권을 전달합니다.")
                            
                            message_data["messages"].append({
                                "type": "agent_change",
                                "agent": agent,
                                "info": "handoff"
                            })
                            current_idx += 1
                        
                        current_agent = agent
                    
                    # 아티팩트 타입 결정
                    artifact_type = self._determine_artifact_type(agent)
                    
                    # 메시지 유형별 처리
                    if msg_type == "message":
                        # 텍스트 누적
                        current_text += text
                        # 아티팩트 업데이트 (진행 중)
                        self._update_artifact(current_text, artifact_type, placeholders, current_idx)
                        
                    elif msg_type == "tool":
                        # 현재 텍스트가 있으면 저장
                        if current_text:
                            self._update_artifact(current_text, artifact_type, placeholders, current_idx, is_final=True)
                            logger.info(f'에이전트 응답:{current_agent}\n{current_text}')
                            message_data["messages"].append({
                                "type": "text",
                                "content": current_text,
                                "agent": current_agent
                            })
                            current_idx += 1
                            current_text = ""
                        
                        # 도구 실행 결과 표시
                        tool_name = payload.get("tool_name")
                        
                        # mermaid_tool 특별 처리
                        if tool_name == "mermaid_tool":
                            with placeholders[current_idx].expander(f"📊 개념 지도", expanded=True):
                                # streamlit-mermaid 라이브러리 사용 (상단에 import 되어 있음)
                                mermaid_key = f"mermaid_render_{uuid.uuid4()}"  # 고유한 키 생성
                                stmd.st_mermaid(text, key=mermaid_key)
                        else:
                            with placeholders[current_idx].expander(f"🛠️ {tool_name} 도구를 사용합니다.", expanded=False):
                                st.code(text)
                        
                        # 도구 실행 결과 저장
                        message_data["messages"].append({
                            "type": "tool",
                            "name": tool_name,
                            "content": text,
                            "agent": current_agent
                        })
                        current_idx += 1
                    
                except json.JSONDecodeError as e:
                    self._handle_json_error(e, line, placeholders, current_idx)
                    current_idx += 1
                except Exception as e:
                    self._handle_stream_error(e, placeholders, current_idx)
                    current_idx += 1
            
            # 비정상 종료 시에만 현재 텍스트 저장 (정상 종료는 이미 처리됨)
            if not has_ended and current_text:
                logger.info(f'에이전트 응답:{current_agent}\n{current_text}')
                self._update_artifact(current_text, artifact_type, placeholders, current_idx, is_final=True)
                message_data["messages"].append({
                    "type": "text",
                    "content": current_text,
                    "agent": current_agent
                })
        
        finally:
            # 스트리밍 종료 시 플래그 해제 (정상/오류 종료 모두)
            st.session_state.is_streaming = False
            logger.info("스트리밍 종료/중단, is_streaming = False")
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
            self.logger.warning(f"Placeholder index {idx} out of range (max: {len(placeholders)-1})")
            return
            
        if artifact_type == "passage":
            status_text = "지문 작성 완료" if is_final else "지문 작성 중..."
            state = "complete" if is_final else "running"  # Always use valid state
            
            # Always show status for passage updates
            try:
                placeholders[idx].status(status_text, expanded=False, state=state)
            except Exception as e:
                self.logger.warning(f"상태 업데이트 실패: {str(e)}")
            
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
                self.logger.warning(f"상태 업데이트 실패: {str(e)}")
                
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
        self.logger.warning(f"JSON 파싱 실패, 데이터 무시: {line[6:]} (오류: {str(error)})")
        
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
        self.logger.error(f"메시지 처리 중 오류 발생: {str(error)}", exc_info=True)
        
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
        self.logger.error(error_msg, exc_info=True)
        
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
        self.logger.error(error_msg, exc_info=True)
        
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
    message_renderer = MessageRenderer(chat_container, passage_placeholder, question_placeholder)
    backend_client = BackendClient(config.backend_url, chat_container, passage_placeholder, question_placeholder, response_status)

    # 첫 메시지일 경우, 환영 메시지 표시
    if len(st.session_state.messages) == 0:
        with passage_placeholder.container():
            st.title("Welcome!")
            st.subheader(":thinking_face: 하단 입력창에 원하는 주제를 입력하세요.")
            st.markdown("🎯*예시 1: 사회적인 문제를 깊이 다루는 지문을 출제해 줘.*")
            st.markdown("🎯*예시 2: 최신 기술을 설명하는 고난도 지문을 써 봐.*")
            st.markdown("🎯*예시 3: 여러 학자들의 관점을 비교하는 문제를 만들어 줘.*")
            st.markdown(" ")
            st.markdown("ver : 0.4.0")
    
    
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
        
        # 5. UI 업데이트를 위한 rerun
        logger.info("프롬프트 처리 완료. UI 업데이트 위해 rerun 호출.")
        st.rerun()

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