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
    generate_passage,
    generate_question,
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
            generate_passage,
            generate_question,
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

# --- 응답 생성 함수 단순화 --- 
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
            print(event)
            kind = event["event"]
            name = event.get("name")
            
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
            
            # on_chain_stream, on_tool_start 이벤트는 처리/yield하지 않음

            elif kind == "on_tool_end":
                data = event.get("data", {})
                tool_output = data.get("output") # ToolMessage 객체 또는 다른 타입일 수 있음
                name = event.get("name")
                output_content_str = "" # 최종적으로 yield할 순수 텍스트

                # generate_passage 결과 처리: content='...' 또는 순수 텍스트 처리
                if name == "generate_passage":
                    actual_content = ""
                    # tool_output이 ToolMessage 객체인지 확인
                    if isinstance(tool_output, ToolMessage):
                        actual_content = tool_output.content
                    else: # ToolMessage가 아니면 tool_output 자체를 내용으로 간주
                        actual_content = tool_output

                    # 실제 내용(actual_content)이 문자열인지 확인
                    if isinstance(actual_content, str):
                        stripped_content = actual_content.strip()
                        # content='...' 형태인지 확인 (문자열 메소드 사용)
                        if stripped_content.startswith("content='") and stripped_content.endswith("'"): # Use ' not "
                             # 앞뒤 'content='와 ' 제거
                             start_index = len("content='")
                             end_index = -1 # 마지막 ' 제외
                             output_content_str = stripped_content[start_index:end_index].strip() # 추출 후 앞뒤 공백 제거
                             logger.info("generate_passage: Extracted content from 'content=...' string.")
                        else:
                             # content='...' 형태가 아니면 순수 텍스트로 간주
                             output_content_str = actual_content
                             logger.info("generate_passage: Using raw string output.")
                    elif actual_content is not None:
                        # 문자열이 아닌 다른 타입이면 문자열로 변환 (예외 처리)
                        output_content_str = str(actual_content)
                        logger.warning(f"generate_passage: Output was not a string ({type(actual_content)}), converted to string.")
                    # else: actual_content is None 이면 output_content_str은 "" 유지

                # 다른 도구 결과 처리 (단순 문자열 변환)
                else:
                    if isinstance(tool_output, ToolMessage):
                        output_content_str = str(tool_output.content) if tool_output.content is not None else ""
                    elif tool_output is not None:
                        output_content_str = str(tool_output)
                    # else: tool_output is None 이면 output_content_str은 "" 유지

                logger.info(f"Tool end: {name}, Yielding text: {output_content_str[:100]}...")
                yield {
                    "type": "tool_end",
                    "tool_name": name,
                    "text": output_content_str # 항상 순수 텍스트 또는 빈 문자열
                }

            elif kind in ["on_tool_error", "on_chain_error", "on_llm_error"]:
                # 오류는 간단히 문자열로 변환하여 전달
                error_message = str(event.get("data", ""))
                logger.error(f"Error ({kind}): {name} - {error_message}")
                yield {
                    "type": "error",
                    "tool_name": name,
                    "text": error_message
                }

    except Exception as e:
        # 스트림 루프 자체의 예외
        logger.error(f"스트림 처리 중 예외: {str(e)}", exc_info=True)
        yield {
            "type": "error",
            "text": f"스트림 오류: {str(e)}"
        }
# --- 응답 생성 함수 끝 --- 