"""Delete Xiaohongshu Reference Materials"""

import json
from typing import cast
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import ToolMessage, AIMessage
from research_canvas.langgraph.state import AgentState

async def delete_node(state: AgentState, config: RunnableConfig): # pylint: disable=unused-argument
    """
    Delete Xiaohongshu Reference Materials Node
    """
    print("=" * 80)
    print("🗑️ DELETE NODE - 处理删除参考素材请求")
    print(f"📈 当前参考素材数量: {len(state.get('reference_materials', []))}")
    print("➡️ 下一步: 返回chat_node")
    print("=" * 80)
    print()
    return state

async def perform_delete_node(state: AgentState, config: RunnableConfig): # pylint: disable=unused-argument
    """
    Perform Delete Xiaohongshu Reference Materials Node
    """
    print("=" * 80)
    print("🗑️ PERFORM DELETE NODE - 执行删除操作")
    
    ai_message = cast(AIMessage, state["messages"][-2])
    tool_message = cast(ToolMessage, state["messages"][-1])
    
    original_count = len(state.get("reference_materials", []))
    
    if tool_message.content == "YES":
        print("✅ 确认删除操作")
        
        if ai_message.tool_calls:
            urls = ai_message.tool_calls[0]["args"]["urls"]
        else:
            parsed_tool_call = json.loads(ai_message.additional_kwargs["function_call"]["arguments"])
            urls = parsed_tool_call["urls"]

        print(f"🎯 要删除的URL数量: {len(urls)}")
        for i, url in enumerate(urls):
            print(f"  [{i+1}] {url}")

        state["reference_materials"] = [
            material for material in state["reference_materials"] if material["url"] not in urls
        ]
        
        deleted_count = original_count - len(state["reference_materials"])
        print(f"🗑️ 实际删除: {deleted_count} 个素材")
        print(f"📈 剩余素材数量: {len(state['reference_materials'])}")
    else:
        print("❌ 取消删除操作")
    
    print("➡️ 下一步: 继续对话")
    print("=" * 80)
    print()

    return state
