"""Persona Generation Node for Creating Blogger Personas"""

from typing import Literal, cast
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import SystemMessage, AIMessage, ToolMessage
from langchain.tools import tool
from langgraph.types import Command
from copilotkit.langgraph import copilotkit_customize_config
from research_canvas.langgraph.state import AgentState, BloggerPersona
from research_canvas.langgraph.model import get_model


@tool
def GenerateBloggerPersona(blogger_persona: BloggerPersona):  # pylint: disable=invalid-name,unused-argument
    """
    生成博主人设。根据产品信息和目标用户，创建合适的博主人设。
    参数: blogger_persona - 包含博主人设详细信息的对象
    """


async def persona_generation_node(state: AgentState, config: RunnableConfig) -> \
    Command[Literal["__end__"]]:
    """
    Persona Generation Node for creating blogger personas based on product information.
    This node analyzes product info and generates appropriate blogger personas.
    """
    
    try:
        print("👤 PERSONA GENERATION NODE - 开始生成博主人设")
        
        config = copilotkit_customize_config(
            config,
            emit_intermediate_state=[{
                "state_key": "blogger_persona",
                "tool": "GenerateBloggerPersona",
                "tool_argument": "blogger_persona",
            }],
        )

        # 获取产品信息
        product_info = state.get("product_info", {})
        if not product_info:
            print("⚠️ 没有产品信息，无法生成博主人设")
            return Command(goto="__end__")

        print(f"📦 基于产品信息生成人设: {product_info.get('name', '未知产品')}")

        model = get_model(state)

        response = await model.bind_tools(
            [GenerateBloggerPersona],
            parallel_tool_calls=False
        ).ainvoke([
            SystemMessage(
                content=f"""
                你是一个专业的小红书博主人设策划师，需要根据产品信息创造一个合适的博主人设。

                ## 产品信息
                {product_info}

                ## 人设生成要求

                你需要调用 GenerateBloggerPersona 工具，生成一个完整的博主人设，包含以下要素：

                ### 1. 博主名称 (name)
                - 符合产品调性的亲切昵称
                - 体现专业领域特色
                - 朗朗上口，容易记忆

                ### 2. 内容风格 (style)  
                - 根据产品特性确定内容定位
                - 如：专业科普型、体验分享型、生活方式型等

                ### 3. 语言风格 (tone)
                - 符合目标用户偏好的表达方式
                - 如：亲切自然、专业权威、幽默风趣等

                ### 4. 目标受众 (target_audience)
                - 明确用户画像：年龄、性别、生活状态等
                - 与产品目标用户高度匹配

                ### 5. 专业领域 (expertise)
                - 博主的专长领域，2-4个相关领域
                - 确保与产品类别高度相关

                ### 6. 个性特点 (personality_traits)
                - 3-5个鲜明的个性标签
                - 体现博主的独特价值主张

                ### 7. 内容主题 (content_themes)
                - 博主常创作的内容类型
                - 与产品推广自然结合

                ## 生成原则
                1. **真实可信**：人设要贴近真实博主，避免过度包装
                2. **产品匹配**：人设与产品调性、目标用户高度契合
                3. **差异化**：在同类博主中有独特定位
                4. **可持续**：人设要能支撑长期内容创作
                5. **小红书化**：符合小红书平台用户偏好

                请立即调用 GenerateBloggerPersona 工具生成博主人设。
                """
            ),
            *state["messages"],
        ], config)

        ai_message = cast(AIMessage, response)
        
        if hasattr(ai_message, 'tool_calls') and ai_message.tool_calls:
            tool_call = ai_message.tool_calls[0]
            if tool_call["name"] == "GenerateBloggerPersona":
                blogger_persona = tool_call["args"].get("blogger_persona", {})
                
                print(f"✅ 博主人设生成完成: {blogger_persona.get('name', '未命名')}")
                print(f"📝 人设风格: {blogger_persona.get('style', '未定义')}")
                
                return Command(
                    goto="__end__",
                    update={
                        "blogger_persona": blogger_persona,
                        "messages": [ai_message, ToolMessage(
                            tool_call_id=tool_call["id"],
                            content="博主人设已生成完成。"
                        )]
                    }
                )
        
        print("⚠️ 未能生成博主人设")
        return Command(goto="__end__")
        
    except Exception as e:
        print(f"❌ PERSONA GENERATION NODE 处理出错: {str(e)}")
        return Command(goto="__end__")