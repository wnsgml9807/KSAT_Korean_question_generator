import streamlit as st
from st_screen_stats import ScreenData
import logging
import os
import uuid
import requests
import json
import re
import time
from streamlit import Page # Import Page

# Configuration class for app settings
class Config:
    """Application configuration settings"""
    def __init__(self):
        self.page_title = "KSAT 국어 출제용 AI"
        self.page_icon = "📚"
        self.layout = "wide"
        self.sidebar_state = "expanded"
        self.version = "0.2.0"
        self.author = "권준희"
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
    
    @staticmethod
    def reset_session(logger):
        """Reset the session state"""
        # Generate new session ID
        st.session_state.session_id = f"session_{uuid.uuid4()}"
        logger.info(f"세션 ID 재생성: {st.session_state.session_id}")
        
        # Clear all other session state variables
        keys_to_clear = list(st.session_state.keys())
        for key in keys_to_clear:
            if key != "session_id":  # Keep the newly generated session_id
                del st.session_state[key]
        
        # Re-initialize necessary session variables
        st.session_state.messages = []
        logger.info("세션 상태 초기화 완료")
    
    @staticmethod
    def add_message(role, content, logger):
        """Add a message to the session state"""
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        st.session_state.messages.append({"role": role, "content": content})
        
        logger.info(f"""세션에 저장된 응답 메세지:\n{content}""")
        
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
        """Create and populate the sidebar with common elements"""
        with st.sidebar:
            st.title("수능 독서 출제용 Agent")
            st.write(f"Version {config.version}")
            
            st.info(
                f"""
                **제작자:** {config.author}
                {config.contact}
                """
            )
            
            # Get screen data for responsive design - Restore this block
            try:
                screen_data = ScreenData()
                stats = screen_data.st_screen_data()

                # None이 아닐 때만 세션 상태 업데이트
                if stats is not None and "innerHeight" in stats:
                    height = stats.get("innerHeight")
                    # 유효한 높이 값이면 세션 상태 업데이트
                    if height is not None and isinstance(height, (int, float)) and height > 0:
                        st.session_state.viewport_height = height
                        #logger.info(f"뷰포트 높이 업데이트: {height}px") # Log update
                    else: # Log invalid height received
                        logger.warning(f"수신된 뷰포트 높이 값이 유효하지 않음: {height}")
                else: # Log if stats is None or innerHeight is missing
                     logger.warning(f"화면 통계에서 innerHeight를 찾을 수 없음: {stats}")


            except Exception as e:
                logger.error(f"화면 데이터 얻기 실패: {str(e)}")
                # 오류 발생 시에도 기존 세션 값이나 기본값 유지 시도
                height = st.session_state.get("viewport_height", 800)
                logger.info(f"화면 데이터 얻기 실패, 세션/기본 높이 사용: {height}px")

            # 항상 최신 세션 상태 값 사용 로그 (디버깅 도움)
            current_height_in_state = st.session_state.get("viewport_height", 800)
            #logger.info(f"현재 세션 뷰포트 높이: {current_height_in_state}px")
            # create_sidebar no longer returns height, it just ensures session_state is updated.


            # Session reset button
            if st.button("🔄️ 세션 초기화"): # Button text simplified
                # Store viewport height temporarily
                viewport_height = st.session_state.get("viewport_height")

                SessionManager.reset_session(logger)

                # Restore viewport height if it existed
                if viewport_height is not None:
                    st.session_state.viewport_height = viewport_height

                st.success("세션이 초기화되었습니다. 페이지를 새로고침합니다.")
                time.sleep(1)
                st.rerun()
            # Removed return height, sidebar content is common. Height is managed in session state.
    
    @staticmethod
    def create_layout(viewport_height):
        """Create the main layout with columns"""
        # Create main columns
        chat_column, artifact_column = st.columns([3, 5], vertical_alignment="top", gap="medium")
        
        # Chat container
        with chat_column:
            chat_container = st.container(border=False, height=viewport_height)
        
        # Artifact containers
        with artifact_column:
            passage_column, question_column = st.columns(2, vertical_alignment="top")
            
            with passage_column:
                with st.container(border=False, height=viewport_height):
                    passage_placeholder = st.empty()
            
            with question_column:
                with st.container(border=False, height=viewport_height):
                    question_placeholder = st.empty()
        
        return chat_container, passage_placeholder, question_placeholder
    
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
                    placeholders = [st.empty() for _ in range(50)]
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
                with placeholders[idx].container(border=True):
                    st.markdown(item["content"], unsafe_allow_html=True)
            else:
                st.markdown(item["content"], unsafe_allow_html=True)
    
    def _render_tool_item(self, item, placeholders, idx):
        """Render tool execution results"""
        tool_name = item.get("name", "도구 실행 결과")
        if tool_name in ["handoff_for_agent", "handoff_for_supervisor"]:
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
    
    def __init__(self, backend_url, chat_container, passage_placeholder, question_placeholder, logger):
        self.backend_url = backend_url
        self.chat_container = chat_container
        self.passage_placeholder = passage_placeholder
        self.question_placeholder = question_placeholder
        self.logger = logger
    
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
        
        # for line in response.iter_lines(decode_unicode=True):
        #     if not line or not line.startswith("data: "):
        #         continue
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
                        current_idx += 1
                        current_text = ""  # 텍스트 초기화 (중요)
                    
                    # 종료 메시지 표시
                    with placeholders[current_idx].container(border=False):
                        st.success("에이전트의 응답이 종료되었습니다.")
                    
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
                        message_data["messages"].append({
                            "type": "text",
                            "content": current_text,
                            "agent": current_agent
                        })
                        current_idx += 1
                        current_text = ""
                    
                    # 에러 메시지 표시
                    with placeholders[current_idx].container(border=False):
                        st.error(text)
                    
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
                        message_data["messages"].append({
                            "type": "text",
                            "content": current_text,
                            "agent": current_agent
                        })
                        current_idx += 1
                        current_text = ""
                    
                    # 도구 실행 결과 표시
                    tool_name = payload.get("tool_name")
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
            self._update_artifact(current_text, artifact_type, placeholders, current_idx, is_final=True)
            message_data["messages"].append({
                "type": "text",
                "content": current_text,
                "agent": current_agent
            })
        
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
            with placeholders[idx].container(border=True):
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
    # Calculate viewport height using session state value set in sidebar
    viewport_height = UI.calculate_viewport_height(st.session_state.get("viewport_height", 800))

    # Create layout for the main app page
    chat_container, passage_placeholder, question_placeholder = UI.create_layout(viewport_height)

    # Initialize session (ensures messages/session_id exist)
    SessionManager.initialize_session(logger)

    # Create helpers
    message_renderer = MessageRenderer(chat_container, passage_placeholder, question_placeholder)
    backend_client = BackendClient(config.backend_url, chat_container, passage_placeholder, question_placeholder, logger)

    # Display existing messages
    for message in st.session_state.messages:
        message_renderer.render_message(message)

    # Handle user input
    if prompt := st.chat_input("ex) 인문 지문을 작성하고 싶어"):
        # Add user message to session state
        SessionManager.add_message("user", prompt)
        # Display user message
        message_renderer.render_message({"role": "user", "content": prompt})

        # Get response from backend
        response = backend_client.send_message(prompt, st.session_state.session_id)
        
        # Save assistant response to session state
        SessionManager.add_message("assistant", response)

        logger.info(f"""세션에 응답 저장됨""")


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
        Page(lambda: show_main_app(config, logger), title="Agent", icon="🤖"),
        Page(config.about_page_path, title="About", icon="📄", default=True)
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