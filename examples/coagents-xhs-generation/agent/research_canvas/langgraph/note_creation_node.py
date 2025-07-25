"""Note Creation Node for Xiaohongshu Note Generation"""

from typing import List, cast, Literal
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import SystemMessage, AIMessage, ToolMessage
from langchain.tools import tool
from langgraph.types import Command
from copilotkit.langgraph import copilotkit_customize_config
from research_canvas.langgraph.state import AgentState, ProductInfo, Tag, BloggerPersona
from research_canvas.langgraph.model import get_model
from research_canvas.langgraph.download import get_resource


@tool
def Search(queries: List[str]): # pylint: disable=invalid-name,unused-argument
    """
    搜索小红书相关内容，包括竞品笔记、用户评价、热门话题等。
    当需要更多参考素材时使用此工具。
    参数: queries - 搜索关键词列表
    """

@tool
def WriteXiaohongshuNote(xiaohongshu_note: str): # pylint: disable=invalid-name,unused-argument
    """
    撰写小红书笔记内容。当用户明确要求创作小红书文案时使用此工具。
    参数: xiaohongshu_note - 完整的小红书笔记内容
    """

@tool
def WriteProductInfo(product_info: ProductInfo): # pylint: disable=invalid-name,unused-argument
    """
    填写或更新产品信息。当用户提供产品详情时使用此工具。
    参数: product_info - 包含产品名称、类别、价格等信息的对象
    """

@tool
def GenerateTags(tags: List[Tag]): # pylint: disable=invalid-name,unused-argument
    """
    生成小红书话题标签。当需要为笔记添加标签时使用此工具。
    参数: tags - 标签列表，包含标签名称、热度等级等
    """

@tool
def AnalyzeCompetitors(analysis: str): # pylint: disable=invalid-name,unused-argument
    """
    分析竞品笔记内容。当需要分析同类产品的小红书内容时使用。
    参数: analysis - 竞品分析结果
    """

@tool
def DeleteReferenceMaterials(urls: List[str]): # pylint: disable=invalid-name,unused-argument
    """
    删除不需要的参考素材。当用户要求删除某些素材时使用。
    参数: urls - 要删除的素材URL列表
    """

@tool
def GenerateBloggerPersona(blogger_persona: BloggerPersona): # pylint: disable=invalid-name,unused-argument
    """
    生成博主人设。根据产品信息和目标用户，创建合适的博主人设。
    参数: blogger_persona - 包含博主人设详细信息的对象
    """


async def note_creation_node(state: AgentState, config: RunnableConfig) -> \
    Command[Literal["search_node", "note_creation_node", "delete_node", "__end__"]]:
    """
    Note Creation Node for Xiaohongshu Note Generation
    专注处理笔记创作、产品信息录入和相关功能
    """
    
    print("=" * 80)
    print("📝 NOTE CREATION NODE - 开始处理笔记创作")
    print(f"📝 当前消息数: {len(state.get('messages', []))}")
    if state.get('messages'):
        latest_message = state['messages'][-1]
        print(f"👤 最新消息: {latest_message.content[:100]}...")
        print(f"🔍 消息类型: {type(latest_message).__name__}")
    
    print(f"📊 当前状态:")
    print(f"  - 笔记内容: {'已生成' if state.get('xiaohongshu_note') else '未生成'}")
    print(f"  - 产品信息: {'已填写' if state.get('product_info') and state.get('product_info').get('name') else '未填写'}")
    
    current_persona = state.get('blogger_persona', {})
    has_valid_persona = current_persona and isinstance(current_persona, dict) and current_persona.get('name')
    print(f"  - 博主人设: {'已生成' if has_valid_persona else '未生成'}")
    print(f"  - 标签: {len(state.get('tags', []))}个")
    print(f"  - 参考素材: {len(state.get('reference_materials', []))}个")

    # 只为核心功能启用emit配置，避免过度复杂导致错误
    config = copilotkit_customize_config(
        config,
        emit_intermediate_state=[{
            "state_key": "product_info",
            "tool": "WriteProductInfo",
            "tool_argument": "product_info",
        }, {
            "state_key": "xiaohongshu_note",
            "tool": "WriteXiaohongshuNote",
            "tool_argument": "xiaohongshu_note",
        }, {
            "state_key": "blogger_persona",
            "tool": "GenerateBloggerPersona",
            "tool_argument": "blogger_persona",
        }],
    )

    # 确保必要的状态字段存在
    state["reference_materials"] = state.get("reference_materials", [])
    product_info = state.get("product_info", {})
    xiaohongshu_note = state.get("xiaohongshu_note", "")
    tags = state.get("tags", [])
    target_audience = state.get("target_audience", "")
    note_style = state.get("note_style", "grass_planting")
    blogger_persona = state.get("blogger_persona", {})

    # 处理参考素材
    reference_materials = []
    for material in state["reference_materials"]:
        content = get_resource(material["url"])
        if content == "ERROR":
            continue
        reference_materials.append({
            **material,
            "content": content
        })

    model = get_model(state)
    
    print(f"🤖 准备调用DeepSeek模型...")
    print(f"🔧 可用工具: {[tool.name for tool in [Search, WriteXiaohongshuNote, WriteProductInfo, GenerateTags, AnalyzeCompetitors, DeleteReferenceMaterials, GenerateBloggerPersona]]}")
    
    try:
        response = await model.bind_tools(
            [
                Search,
                WriteXiaohongshuNote,
                WriteProductInfo,
                GenerateTags,
                AnalyzeCompetitors,
                DeleteReferenceMaterials,
                GenerateBloggerPersona,
            ],
            parallel_tool_calls=False
        ).ainvoke([
            SystemMessage(
                content=f"""
            你是一个专业的小红书笔记撰写助手，专门帮助商家创作吸引人的小红书内容。

            ## 你的核心任务：
            1. 根据产品信息创作符合小红书平台特色的笔记内容
            2. 生成热门话题标签，提高笔记曝光度
            3. 分析竞品笔记，提供优化建议
            4. 适应不同笔记风格：种草、测评、教程、生活方式、开箱等

            ## 小红书笔记特色要求：
            - 标题吸引眼球，包含热门关键词
            - 内容真实有趣，避免过度营销
            - 适当使用表情符号增加亲和力
            - 结构清晰，易于阅读
            - 包含实用信息和个人体验

            ## 当前产品信息：
            {product_info}

            ## 目标用户：
            {target_audience}

            ## 笔记风格：
            {note_style}

            ## 已生成的笔记内容：
            {xiaohongshu_note}

            ## 话题标签：
            {tags}

            ## 博主人设：
            {blogger_persona}

            ## 可用的参考素材：
            {reference_materials}

            ## 智能建议系统：
            
            **当前状态分析：**
            - 产品信息状态: {'已完善' if product_info and product_info.get('name') else '待完善'}
            - 博主人设状态: {'已生成' if blogger_persona and blogger_persona.get('name') else '待生成'}
            - 建议下一步: {'可以生成博主人设或直接创作笔记' if product_info and product_info.get('name') and not (blogger_persona and blogger_persona.get('name')) else '可以创作笔记内容' if blogger_persona and blogger_persona.get('name') else '请先提供产品信息'}
            
            ## 工具使用指南：
            
            **根据用户需求智能选择合适的工具：**
            
            1. **产品信息相关** → 使用 WriteProductInfo 工具
               - 用户提供产品详情、特点、价格等信息时
               
            2. **博主人设生成** → 使用 GenerateBloggerPersona 工具
               - 当有产品信息但还没有博主人设时，优先生成人设
               - 用户明确要求生成博主人设时
               
            3. **笔记创作相关** → 使用 WriteXiaohongshuNote 工具  
               - 用户明确要求创作笔记、文案时
               - 用户说"帮我写"、"创作内容"等时
               - 建议在有博主人设的基础上创作笔记
               
            4. **标签生成** → 使用 GenerateTags 工具
               - 用户需要话题标签时
               
            5. **搜索需求** → 使用 Search 工具
               - 用户要求搜索参考资料时
               
            6. **竞品分析** → 使用 AnalyzeCompetitors 工具
               - 用户需要分析同类产品时

            **重要原则：**
            - 仔细理解用户意图，选择最合适的工具
            - 如果用户只是询问或讨论，可以直接文本回复而不调用工具
            - 只有在明确需要执行特定功能时才调用对应工具
            - **智能工作流程**：
              1. 产品信息录入 (WriteProductInfo)
              2. 博主人设生成 (GenerateBloggerPersona) - 基于产品信息自动触发
              3. 笔记创作 (WriteXiaohongshuNote) - 融入博主人设风格
              4. 标签生成 (GenerateTags) - 配合笔记内容
            - 当有产品信息但缺少博主人设时，**强烈建议先生成人设**
            - 博主人设能让笔记更具个性化和可信度
            - 优先提供有用的建议和指导
            """
        ),
        *state["messages"],
    ], config)
    
    except Exception as e:
        print(f"❌ 模型调用失败: {str(e)}")
        # 返回错误响应
        error_message = AIMessage(content=f"抱歉，处理您的请求时遇到了问题：{str(e)}。请稍后重试。")
        return Command(
            goto="__end__",
            update={
                "messages": [error_message]
            }
        )

    ai_message = cast(AIMessage, response)
    
    # 详细日志：DeepSeek响应分析
    print(f"📥 DeepSeek响应分析:")
    print(f"  - 响应类型: {type(ai_message).__name__}")
    print(f"  - 有工具调用: {bool(hasattr(ai_message, 'tool_calls') and ai_message.tool_calls)}")
    
    if hasattr(ai_message, 'tool_calls') and ai_message.tool_calls:
        print(f"🔧 工具调用详情:")
        for i, tool_call in enumerate(ai_message.tool_calls):
            print(f"  [{i+1}] 工具: {tool_call['name']}")
            print(f"      参数: {tool_call.get('args', {})}")
            
        # 处理工具调用
        tool_name = ai_message.tool_calls[0]["name"]
        print(f"🚀 执行工具: {tool_name}")
        
        if tool_name == "WriteXiaohongshuNote":
            xiaohongshu_note = ai_message.tool_calls[0]["args"].get("xiaohongshu_note", "")
            print(f"📝 生成笔记长度: {len(xiaohongshu_note)}字符")
            print(f"📝 笔记预览: {xiaohongshu_note[:100]}...")
            
            # 修复：不再将ToolMessage重新加入处理队列
            print(f"✅ 笔记生成完成，直接结束")
            return Command(
                goto="__end__",
                update={
                    "xiaohongshu_note": xiaohongshu_note,
                    "messages": [ai_message, ToolMessage(
                        tool_call_id=ai_message.tool_calls[0]["id"],
                        content="小红书笔记已生成完成。"
                    )]
                }
            )
            
        elif tool_name == "WriteProductInfo":
            product_info = ai_message.tool_calls[0]["args"].get("product_info", {})
            print(f"📦 更新产品信息: {product_info}")
            
            # 检查是否已有博主人设
            current_persona = state.get("blogger_persona", {})
            has_persona = current_persona and isinstance(current_persona, dict) and current_persona.get("name")
            
            if not has_persona:
                print(f"💡 产品信息已更新，建议生成博主人设")
                # 返回带有建议的消息，包含明确的系统回复
                suggestion_message = ToolMessage(
                    tool_call_id=ai_message.tool_calls[0]["id"],
                    content="产品信息已更新！"
                )
                # 添加一个AI助手的建议消息
                ai_suggestion = AIMessage(
                    content="✅ 产品信息已成功录入！接下来我建议生成一个专属的博主人设，这样可以让后续的笔记创作更加个性化和有针对性。\n\n您可以说：\n- \"生成博主人设\"\n- \"帮我创建人设\" \n- 或者直接说\"帮我写笔记\"，我会先生成人设再创作笔记。"
                )
                return Command(
                    goto="__end__",
                    update={
                        "product_info": product_info,
                        "messages": [ai_message, suggestion_message, ai_suggestion]
                    }
                )
            else:
                suggestion_message = ToolMessage(
                    tool_call_id=ai_message.tool_calls[0]["id"],
                    content="产品信息已更新。"
                )
            
            print(f"✅ 产品信息更新完成")
            return Command(
                goto="__end__",
                update={
                    "product_info": product_info,
                    "messages": [ai_message, suggestion_message]
                }
            )
            
        elif tool_name == "GenerateTags":
            tags = ai_message.tool_calls[0]["args"].get("tags", [])
            print(f"🏷️ 生成标签数量: {len(tags)}个")
            for i, tag in enumerate(tags[:3]):  # 显示前3个标签
                print(f"  [{i+1}] {tag.get('name', 'Unknown')} (热度: {tag.get('heat_level', 'Unknown')})")
            print(f"✅ 标签生成完成，直接结束")
            
            # 标签状态将通过return的update自动同步到前端
            
            return Command(
                goto="__end__",
                update={
                    "tags": tags,
                    "messages": [ai_message, ToolMessage(
                        tool_call_id=ai_message.tool_calls[0]["id"],
                        content="话题标签已生成。"
                    )]
                }
            )
            
        elif tool_name == "Search":
            print(f"🔍 执行搜索工具")
            print(f"➡️ 下一步: 跳转到search_node")
            return Command(
                goto="search_node",
                update={
                    "messages": [ai_message]
                }
            )
            
        elif tool_name == "DeleteReferenceMaterials":
            print(f"🗑️ 执行删除素材工具")
            print(f"➡️ 下一步: 跳转到delete_node")
            return Command(
                goto="delete_node",
                update={
                    "messages": [ai_message]
                }
            )
            
        elif tool_name == "GenerateBloggerPersona":
            blogger_persona = ai_message.tool_calls[0]["args"].get("blogger_persona", {})
            print(f"👤 生成博主人设: {blogger_persona.get('name', '未命名')}")
            print(f"📝 人设风格: {blogger_persona.get('style', '未定义')}")
            print(f"✅ 博主人设生成完成，直接结束")
            
            # 博主人设状态将通过return的update自动同步到前端
            
            return Command(
                goto="__end__",
                update={
                    "blogger_persona": blogger_persona,
                    "messages": [ai_message, ToolMessage(
                        tool_call_id=ai_message.tool_calls[0]["id"],
                        content="博主人设已生成完成。"
                    )]
                }
            )
    else:
        # 没有工具调用，直接返回文本回复
        print(f"📝 文本响应: {ai_message.content[:200]}...")
        print(f"✅ 直接文本回复，无工具调用")

    print(f"🏁 处理完成")
    print("=" * 80)
    print()

    return Command(
        goto="__end__",
        update={
            "messages": [response]
        }
    )