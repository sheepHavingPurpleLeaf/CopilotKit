"""
DeepSeek model configuration for Xiaohongshu note generation.
"""
import os
from langchain_core.language_models.chat_models import BaseChatModel
from research_canvas.langgraph.state import AgentState

def get_model(state: AgentState) -> BaseChatModel:
    """
    Get DeepSeek model for Xiaohongshu note generation.
    """
    print("Using DeepSeek model for Xiaohongshu note generation")
    
    from langchain_openai import ChatOpenAI
    
    return ChatOpenAI(
        temperature=0,
        model=os.getenv("DEEPSEEK_MODEL", "ep-20250206170923-bx29l"),
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3")
    )
