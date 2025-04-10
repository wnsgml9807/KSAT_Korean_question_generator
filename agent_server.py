from dotenv import load_dotenv
from langgraph.prebuilt import create_react_agent
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
import os
import logging
import time
import json
from langgraph.checkpoint.memory import MemorySaver
from typing import Optional, Dict, Any, AsyncGenerator
from prompt import system_prompt
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
import sys
import asyncio
from contextlib import asynccontextmanager
import re # 정규표현식 모듈 임포트
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

from tools import (
    prompt_for_suneung_writing, 
    structure_for_suneung_writing,
    prompt_for_technology_subject,
    prompt_for_humanities_subject,
    retrieve_data
)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def initialize_agent():
    """에이전트를 초기화하고 생성된 에이전트 객체를 반환합니다."""
    try:
        # 모델 초기화
        model = ChatAnthropic(
            model="claude-3-7-sonnet-latest",
            temperature=1,
            max_tokens=3000
        )
        
        # 도구 리스트 직접 생성
        tools = [
            prompt_for_suneung_writing, 
            structure_for_suneung_writing,
            prompt_for_technology_subject,
            prompt_for_humanities_subject,
            retrieve_data
        ]
        logger.info(f"로컬 도구 로드 완료: {len(tools)} 개")

        # 에이전트 생성
        agent_executor = create_react_agent(
            model, 
            tools, 
            prompt=system_prompt(),
            checkpointer=MemorySaver()
        )
        logger.info("에이전트 초기화 완료")
        return agent_executor
    except Exception as e:
        logger.error(f"에이전트 초기화 실패: {str(e)}", exc_info=True)
        return None

# 환경 변수 로드 (모듈 로드 시 실행)
load_dotenv(override=True)

# LangSmith 설정 - 추적 비활성화 (모듈 로드 시 실행)
os.environ["LANGSMITH_TRACING"] = "false"
# os.environ["LANGSMITH_PROJECT"] = "Kice_Agent"

# --- 응답 생성 함수 수정 ---
async def generate_agent_response(agent_executor: Any, prompt: str, session_id: str) -> AsyncGenerator[Dict[str, Any], None]:
    """에이전트 이벤트 스트림을 생성하여 필요한 정보만 yield합니다."""
    if not agent_executor:
        logger.error("에이전트가 초기화되지 않았습니다.")
        yield {"type": "error", "event": "agent_initialization_error", "text": "에이전트가 준비되지 않았습니다."}
        return

    try:
        logger.info(f"에이전트 호출 시작: {prompt[:30]}... (세션: {session_id})")
        inputs = {"messages": [HumanMessage(content=prompt)]}
        config = {"configurable": {"thread_id": session_id}}

        async for event in agent_executor.astream_events(inputs, config=config, version="v1"):
            # print(event) # 디버깅용 print는 주석 처리하거나 제거
            kind = event["event"]
            run_id = event.get("run_id") # 모든 이벤트에서 run_id 가져오기 시도
            name = event.get("name")
            print(kind, name)
            if kind == "on_chat_model_stream":
                data = event.get("data", {})
                chunk = data.get("chunk")
                if chunk and hasattr(chunk, 'content'):
                    content = chunk.content # 항상 리스트라고 가정
                    token_text = ""
                    if isinstance(content, list):
                        for block in content:
                            if isinstance(block, dict) and block.get("type") == "text":
                                token_text += block.get("text", "")
                    if token_text:
                        yield {"type": "ai_token", "text": token_text}

            elif kind == "on_tool_start":
                # generate_passage 또는 generate_question은 이제 일반 도구임
                # if name in ["generate_passage", "generate_question"]: # 조건 제거
                # 모든 도구 시작 시 로깅만 하고 yield는 하지 않음 (필요시 아래 주석 해제)
                logger.info(f"SERVER: Tool start: {name} (run_id: {run_id})")
                # yield {
                #     "type": "tool_start",
                #     "tool_name": name,
                #     "run_id": run_id
                # }

            elif kind == "on_tool_end":
                data = event.get("data", {})
                tool_output = data.get("output")
                output_content_str = "" # 최종 텍스트 초기화

                # --- 결과 텍스트 추출 로직 (모든 도구에 동일 적용) ---
                if isinstance(tool_output, ToolMessage):
                    output_content_str = str(tool_output.content) if tool_output.content is not None else ""
                elif tool_output is not None:
                    output_content_str = str(tool_output)
                # --- 추출 로직 끝 ---
                
                logger.info(f"Tool end: {name} (run_id: {run_id}), Yielding text: {output_content_str[:50]}...")
                yield {
                    "type": "tool_end",
                    "tool_name": name,
                    "text": output_content_str,
                    "run_id": run_id
                }

            elif kind in ["on_tool_error", "on_chain_error", "on_llm_error"]:
                error_message = str(event.get("data", ""))
                logger.error(f"Error ({kind}): {name} (run_id: {run_id}) - {error_message}")
                yield {
                    "type": "error",
                    "tool_name": name,
                    "text": error_message,
                    "run_id": run_id # 오류 발생 시에도 run_id 포함 (스피너 제거용)
                }
            # 다른 이벤트 (on_chain_start, on_chain_stream 등)는 무시

    except Exception as e:
        logger.error(f"스트림 처리 중 예외: {str(e)}", exc_info=True)
        yield {
            "type": "error",
            "text": f"스트림 오류: {str(e)}"
            # run_id를 특정할 수 없으므로 여기서는 포함하지 않음
        }
# --- 응답 생성 함수 끝 --- 