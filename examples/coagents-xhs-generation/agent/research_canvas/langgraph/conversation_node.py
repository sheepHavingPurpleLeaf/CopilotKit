"""Conversation Node for General Chat and Information"""

from typing import Literal, cast
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import SystemMessage, AIMessage
from langgraph.types import Command
from research_canvas.langgraph.state import AgentState
from research_canvas.langgraph.model import get_model


async def conversation_node(state: AgentState, config: RunnableConfig) -> \
    Command[Literal["__end__"]]:
    """
    Conversation node for handling general chat, greetings, and information queries.
    This node provides direct text responses without calling any tools.
    """
    
    try:
        print("💬 CONVERSATION NODE - 处理普通对话")
        
        if not state.get('messages'):
            print("⚠️ 没有消息，结束处理")
            return Command(goto="__end__")
        
        latest_message = state['messages'][-1]
        print(f"👤 用户输入: {latest_message.content}")
        
        model = get_model(state)
        
        # 获取当前状态信息用于介绍
        product_info = state.get("product_info") or {}
        xiaohongshu_note = state.get("xiaohongshu_note") or ""
        tags = state.get("tags") or []
        materials = state.get("reference_materials") or []
        tags_count = len(tags)
        materials_count = len(materials)

        response = await model.ainvoke([
            SystemMessage(
                content=f"""
                你是一个专业的小红书笔记撰写助手，主要帮助商家创作吸引人的小红书内容。

                ## 你的身份和能力
                我是小红书笔记撰写助手！✨ 我可以帮助你：

                🎯 **核心功能：**
                - 创作符合小红书平台特色的笔记内容
                - 生成热门话题标签，提高曝光度  
                - 分析竞品笔记，提供优化建议
                - 支持多种笔记风格：种草、测评、教程、生活方式、开箱等

                📝 **使用方法：**
                - 告诉我你的产品信息，我会帮你写笔记
                - 说"帮我写笔记"或"创作小红书内容"开始创作
                - 需要搜索参考资料时，直接告诉我搜索需求

                ## 当前工作状态
                - 产品信息: {"已录入" if product_info else "待录入"}
                - 笔记内容: {"已生成" if xiaohongshu_note else "未生成"}  
                - 话题标签: {tags_count}个
                - 参考素材: {materials_count}个

                ## 回复要求
                - 用友好、专业的语气回复
                - 适当使用emoji增加亲和力
                - 针对用户的具体问题给出清晰回答
                - 如果是问候，要热情回应并简单介绍自己
                - 如果是功能询问，要详细说明能力和使用方法
                - 不要调用任何工具，直接返回文本回复
                """
            ),
            *state["messages"],
        ], config)
        
        ai_message = cast(AIMessage, response)
        
        print("✅ 对话回复已生成")
        
        return Command(
            goto="__end__",
            update={
                "messages": [ai_message]
            }
        )
        
    except Exception as e:
        print(f"❌ CONVERSATION NODE 处理出错: {str(e)}")
        # 返回一个友好的错误回复
        error_message = AIMessage(content="抱歉，我现在遇到了一些技术问题。请稍后再试，或者重新开始对话。")
        return Command(
            goto="__end__",
            update={
                "messages": [error_message]
            }
        )