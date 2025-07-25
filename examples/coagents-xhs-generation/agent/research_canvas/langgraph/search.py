"""
The search node is responsible for searching for Xiaohongshu-related content.
搜索节点负责搜索小红书相关内容：竞品笔记、用户评价、热门话题等。
"""

import os
import json
import asyncio
import aiohttp
from typing import cast, List, Dict, Any
from pydantic import BaseModel, Field
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AIMessage, ToolMessage, SystemMessage
from langchain.tools import tool
from tavily import TavilyClient
from copilotkit.langgraph import copilotkit_emit_state, copilotkit_customize_config
from research_canvas.langgraph.state import AgentState, ReferenceMaterial
from research_canvas.langgraph.model import get_model

class ReferenceMaterialInput(BaseModel):
    """小红书参考素材输入模型"""
    url: str = Field(description="资源链接")
    title: str = Field(description="资源标题")
    description: str = Field(description="资源描述")
    type: str = Field(description="素材类型：competitor_note/user_review/product_info/trend_analysis/image")

@tool
def ExtractReferenceMaterials(reference_materials: List[ReferenceMaterialInput]): # pylint: disable=invalid-name,unused-argument
    """从搜索结果中提取3-5个最相关的小红书参考素材"""

# Initialize Tavily API key
tavily_api_key = os.getenv("TAVILY_API_KEY")
tavily_client = None

def get_tavily_client():
    """Get or initialize Tavily client"""
    global tavily_client
    if tavily_client is None:
        if not tavily_api_key:
            raise ValueError("TAVILY_API_KEY environment variable is not set")
        tavily_client = TavilyClient(api_key=tavily_api_key)
    return tavily_client

# 针对小红书内容的异步搜索函数
async def async_xiaohongshu_search(query: str) -> Dict[str, Any]:
    """小红书相关内容搜索的异步包装器"""
    loop = asyncio.get_event_loop()
    try:
        # 为小红书内容优化搜索查询
        xiaohongshu_query = f"{query} 小红书 OR 红书笔记 OR 种草 OR 测评"
        
        # 在线程池中运行同步的 tavily_client.search
        client = get_tavily_client()
        return await loop.run_in_executor(
            None, 
            lambda: client.search(
                query=xiaohongshu_query,
                search_depth="advanced",
                include_answer=True,
                max_results=10,
                include_domains=["xiaohongshu.com", "xhs.com"]  # 优先搜索小红书域名
            )
        )
    except Exception as e:
        raise Exception(f"小红书内容搜索失败: {str(e)}")

async def search_node(state: AgentState, config: RunnableConfig):
    """
    小红书内容搜索节点 - 负责搜索竞品笔记、用户评价、热门话题等。
    """
    
    # 详细日志：搜索节点开始
    print("=" * 80)
    print("🔍 SEARCH NODE - 开始搜索小红书内容")
    
    ai_message = cast(AIMessage, state["messages"][-1])

    state["reference_materials"] = state.get("reference_materials", [])
    state["logs"] = state.get("logs", [])
    queries = ai_message.tool_calls[0]["args"]["queries"]
    
    print(f"📊 搜索查询:")
    for i, query in enumerate(queries):
        print(f"  [{i+1}] {query}")
    print(f"📈 现有参考素材数量: {len(state.get('reference_materials', []))}")
    print(f"🔧 Tavily API状态: {'已配置' if tavily_api_key else '未配置'}")

    # 为每个查询添加日志
    for query in queries:
        state["logs"].append({
            "message": f"正在搜索小红书内容: {query}",
            "done": False
        })

    await copilotkit_emit_state(config, state)

    search_results = []

    print(f"🚀 开始并行搜索 {len(queries)} 个查询...")
    
    # 使用 asyncio.gather 并行执行多个小红书搜索
    tasks = [async_xiaohongshu_search(query) for query in queries]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            # 处理异常
            print(f"❌ 搜索失败 [{i+1}]: {str(result)}")
            search_results.append({"error": str(result)})
        else:
            print(f"✅ 搜索成功 [{i+1}]: 找到 {len(result.get('results', []))} 个结果")
            search_results.append(result)
        
        state["logs"][i]["done"] = True
        await copilotkit_emit_state(config, state)

    # 配置中间状态发射
    config = copilotkit_customize_config(
        config,
        emit_intermediate_state=[{
            "state_key": "reference_materials",
            "tool": "ExtractReferenceMaterials",
            "tool_argument": "reference_materials",
        }],
    )

    print(f"🤖 准备让AI分析搜索结果并提取参考素材...")
    
    model = get_model(state)
    ainvoke_kwargs = {}
    if model.__class__.__name__ in ["ChatOpenAI"]:
        ainvoke_kwargs["parallel_tool_calls"] = False

    # 让AI提取最相关的小红书参考素材
    response = await model.bind_tools(
        [ExtractReferenceMaterials],
        tool_choice="ExtractReferenceMaterials",
        **ainvoke_kwargs
    ).ainvoke([
        SystemMessage(
            content="""
            你需要从以下搜索结果中提取3-5个最相关的小红书参考素材。
            
            重点关注：
            1. 竞品的小红书笔记 (competitor_note)
            2. 用户评价和反馈 (user_review)  
            3. 产品相关信息 (product_info)
            4. 热门话题趋势分析 (trend_analysis)
            5. 相关图片素材 (image)
            
            为每个素材标注正确的类型，并提供简洁有用的描述。
            """
        ),
        *state["messages"],
        ToolMessage(
            tool_call_id=ai_message.tool_calls[0]["id"],
            content=f"小红书内容搜索完成: {search_results}"
        )
    ], config)

    state["logs"] = []
    await copilotkit_emit_state(config, state)

    ai_message_response = cast(AIMessage, response)
    reference_materials = ai_message_response.tool_calls[0]["args"]["reference_materials"]

    print(f"📥 AI提取结果:")
    print(f"  - 提取素材数量: {len(reference_materials)}")
    
    # 为每个素材添加默认类型（如果缺失）
    for i, material in enumerate(reference_materials):
        if "type" not in material:
            material["type"] = "competitor_note"  # 默认类型
        print(f"  [{i+1}] {material.get('title', 'Unknown')} ({material.get('type', 'Unknown')})")

    state["reference_materials"].extend(reference_materials)

    print(f"📈 总参考素材数量: {len(state['reference_materials'])}")
    print(f"➡️ 下一步: 返回chat_node")
    print("=" * 80)
    print()

    state["messages"].append(ToolMessage(
        tool_call_id=ai_message.tool_calls[0]["id"],
        content=f"已添加以下小红书参考素材: {reference_materials}"
    ))

    return state