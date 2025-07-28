"""Router Node for Intent Recognition and Message Routing"""

from typing import Literal, cast
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage
from langgraph.types import Command
from research_canvas.langgraph.state import AgentState
from research_canvas.langgraph.model import get_model


async def router_node(state: AgentState, config: RunnableConfig) -> \
    Command[Literal["conversation_node", "note_creation_node", "search_node", "__end__"]]:
    """
    Router node for intent recognition and message routing.
    Analyzes user input and routes to appropriate processing node.
    """
    
    try:
        print("🔀 ROUTER NODE - 开始意图识别")
        
        if not state.get('messages'):
            return Command(goto="__end__")
        
        latest_message = state['messages'][-1]
        
        # 如果最后一条消息是AI消息，说明刚完成了一个工具调用，应该结束流程
        if isinstance(latest_message, AIMessage):
            print(f"📝 检测到AI消息，工具调用流程完成，结束对话")
            return Command(goto="__end__")
        
        # 只处理人类消息
        if not isinstance(latest_message, HumanMessage):
            print(f"⚠️ 非人类消息类型: {type(latest_message).__name__}，结束流程")
            return Command(goto="__end__")
        
        user_input = latest_message.content
        model = get_model(state)
        
        response = await model.ainvoke([
            SystemMessage(
                content="""
                你是一个意图识别助手，需要分析用户输入并识别用户意图。

                请根据用户输入，识别以下意图类型之一：

                1. **conversation** - 普通对话
                   - 问候语："你好"、"嗨"、"hi"
                   - 自我介绍询问："你是谁"、"介绍一下自己"
                   - 功能咨询："你能做什么"、"怎么使用"
                   - 闲聊内容

                2. **note_creation** - 笔记创作和产品信息
                   - 明确的创作请求："帮我写笔记"、"创作小红书内容"
                   - 笔记相关需求："我要发小红书"、"写个种草文案"
                   - 产品信息录入："我的产品是..."、"产品名称是..."
                   - 博主人设生成："生成博主人设"、"创建人设"、"帮我创建人设"
                   - 任何包含产品名称的具体产品信息
                   - 内容创作指令和产品相关功能

                4. **search** - 搜索需求
                   - 搜索请求："搜索一下..."、"查找..."
                   - 参考需求："找些参考资料"、"看看竞品"

                **重要规则：**
                - 如果用户输入是问候、自我介绍询问或功能咨询，返回 "conversation"
                - 如果用户明确提供产品信息、要求创作内容或生成博主人设，返回 "note_creation"
                - 如果用户要求搜索，返回 "search"
                - 如果不确定，默认返回 "conversation"

                请只返回意图类型，不要添加其他解释。
                """
            ),
            HumanMessage(content=user_input)
        ], config)
        
        ai_response = cast(AIMessage, response)
        intent = ai_response.content.strip().lower()
        
        print(f"🤖 AI返回的意图: '{intent}'")
        
        # 根据意图决定路由目标
        if intent == "conversation":
            next_node = "conversation_node"
        elif intent == "note_creation":
            next_node = "note_creation_node"
        elif intent == "search":
            next_node = "search_node"
        else:
            # 默认处理为普通对话
            next_node = "conversation_node"
            print(f"⚠️ 未识别的意图 '{intent}'，默认路由到conversation_node")
        
        print(f"🎯 路由决策: {next_node}")
        
        return Command(
            goto=next_node,
            update={}  # 不更新状态，保持原有消息
        )
        
    except Exception as e:
        print(f"❌ ROUTER NODE 处理出错: {str(e)}")
        # 出错时默认路由到对话节点
        return Command(
            goto="conversation_node",
            update={}
        )