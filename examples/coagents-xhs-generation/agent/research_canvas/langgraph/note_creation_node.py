"""Note Creation Node for Xiaohongshu Note Generation"""

from typing import List, cast, Literal
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import SystemMessage, AIMessage, ToolMessage
from langchain.tools import tool
from langgraph.types import Command
from copilotkit.langgraph import copilotkit_customize_config
from research_canvas.langgraph.state import AgentState, ProductInfo, BloggerPersona
from research_canvas.langgraph.model import get_model
from research_canvas.langgraph.download import get_resource
from research_canvas.langgraph.rag_node import rag_retrieval_node


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

@tool
def RetrieveFromKnowledgeBase(query: str = ""): # pylint: disable=invalid-name,unused-argument
    """
    从文案库检索相关的小红书文案示例。基于当前的Brief数据和产品信息进行智能检索。
    当用户要求"检索文案库"、"查找文案示例"或需要参考类似文案时使用此工具。
    参数: query - 可选的自定义检索查询，如果不提供则会基于当前状态自动构建查询
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
    print(f"  - Brief数据: {'已上传' if state.get('brief_data') and state.get('brief_data').get('brandName') else '未上传'}")
    
    current_persona = state.get('blogger_persona', {})
    has_valid_persona = current_persona and isinstance(current_persona, dict) and current_persona.get('name')
    print(f"  - 博主人设: {'已生成' if has_valid_persona else '未生成'}")
    print(f"  - 参考素材: {len(state.get('reference_materials', []))}个")
    print(f"  - RAG检索结果: {len(state.get('retrieved_examples', []))}个")

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
    brief_data = state.get("brief_data", {})
    xiaohongshu_note = state.get("xiaohongshu_note", "")
    # 使用product_info中的target_audience，保持一致性
    target_audience = product_info.get("target_audience", "") if product_info else ""
    note_style = state.get("note_style", "grass_planting")
    blogger_persona = state.get("blogger_persona", {})
    # RAG检索结果
    retrieved_examples = state.get("retrieved_examples", [])
    retrieved_content = state.get("retrieved_content", "")

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
    print(f"🔧 可用工具: {[tool.name for tool in [Search, WriteXiaohongshuNote, WriteProductInfo, AnalyzeCompetitors, DeleteReferenceMaterials, GenerateBloggerPersona, RetrieveFromKnowledgeBase]]}")
    
    try:
        response = await model.bind_tools(
            [
                Search,
                WriteXiaohongshuNote,
                WriteProductInfo,
                AnalyzeCompetitors,
                DeleteReferenceMaterials,
                GenerateBloggerPersona,
                RetrieveFromKnowledgeBase,
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

            ## 当前产品信息（结构化数据）：
            {product_info}

            ## Brief数据（用户上传的详细信息）：
            {brief_data}

            ## 目标用户：
            {target_audience}

            ## 笔记风格：
            {note_style}

            ## 已生成的笔记内容：
            {xiaohongshu_note}

            ## 博主人设：
            {blogger_persona}

            ## 可用的参考素材：
            {reference_materials}

            ## RAG检索到的小红书文案示例：
            {retrieved_content}

            ## 智能建议系统：
            
            **RAG检索说明：**
            - 以上RAG检索结果来自真实的小红书文案库，包含成功的文案示例
            - 请参考这些示例的写作风格、结构布局和表达方式
            - 结合这些示例优化你生成的博主人设和小红书文案
            - 学习示例中的关键词使用、情感表达和用户互动方式
            
            **当前状态分析：**
            - 产品信息状态: {'已完善' if product_info and product_info.get('name') else '待完善'}
            - Brief数据状态: {'已上传' if brief_data and brief_data.get('brandName') else '未上传'}
            - 博主人设状态: {'已生成' if blogger_persona and blogger_persona.get('name') else '待生成'}
            - 建议下一步: {'可以生成博主人设或直接创作笔记' if (product_info and product_info.get('name')) or (brief_data and brief_data.get('brandName')) else '请先提供产品信息或上传Brief表'}
            
            ## 工具使用指南：
            
            **根据用户需求智能选择合适的工具：**
            
            1. **产品信息相关** → 使用 WriteProductInfo 工具
               - 用户提供产品详情、特点、价格等信息时
               - **重要：如果Brief数据已上传但产品信息未完善，优先从Brief数据中提取信息填写产品信息**
               
            2. **博主人设生成** → 使用 GenerateBloggerPersona 工具
               - 当有产品信息但还没有博主人设时，优先生成人设
               - 用户明确要求生成博主人设时
               
            3. **笔记创作相关** → 使用 WriteXiaohongshuNote 工具  
               - 用户明确要求创作笔记、文案时
               - 用户说"帮我写"、"创作内容"等时
               - 建议在有博主人设的基础上创作笔记
               
               
            5. **搜索需求** → 使用 Search 工具
               - 用户要求搜索参考资料时
               
            6. **竞品分析** → 使用 AnalyzeCompetitors 工具
               - 用户需要分析同类产品时
               
            7. **文案库检索** → 使用 RetrieveFromKnowledgeBase 工具
               - 用户要求"检索文案库"、"查找文案示例"、"帮我检索文案库"时
               - 需要参考类似产品的成功文案时
               - **优先级高**：当有Brief数据时，应主动建议使用此工具获取相关文案示例

            **重要原则：**
            - 仔细理解用户意图，选择最合适的工具
            - 如果用户只是询问或讨论，可以直接文本回复而不调用工具
            - 只有在明确需要执行特定功能时才调用对应工具
            - **智能数据使用**：
              - Brief数据包含完整的产品详细信息，优先参考Brief数据回答用户问题
              - 当用户询问产品信息时，应该从Brief数据中提取相关信息回答
              - 如果Brief数据存在但product_info不完整，建议使用WriteProductInfo工具从Brief数据中提取并填写产品信息
            - **智能工作流程**：
              1. 产品信息录入 (WriteProductInfo) - 可从Brief数据中提取
              2. 博主人设生成 (GenerateBloggerPersona) - 基于产品信息自动触发
              3. 笔记创作 (WriteXiaohongshuNote) - 融入博主人设风格
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
        
        # 处理所有工具调用
        updates = {}
        tool_messages = []
        ai_responses = []
        
        print(f"🚀 开始处理 {len(ai_message.tool_calls)} 个工具调用")
        
        for i, tool_call in enumerate(ai_message.tool_calls):
            tool_name = tool_call["name"]
            tool_args = tool_call.get("args", {})
            tool_id = tool_call["id"]
            
            print(f"🔧 [{i+1}/{len(ai_message.tool_calls)}] 执行工具: {tool_name}")
            
            if tool_name == "WriteXiaohongshuNote":
                xiaohongshu_note = tool_args.get("xiaohongshu_note", "")
                print(f"📝 生成笔记长度: {len(xiaohongshu_note)}字符")
                print(f"📝 笔记预览: {xiaohongshu_note[:100]}...")
                
                updates["xiaohongshu_note"] = xiaohongshu_note
                tool_messages.append(ToolMessage(
                    tool_call_id=tool_id,
                    content="小红书笔记已生成完成。"
                ))
                ai_responses.append(f"✅ 小红书笔记创作完成！({len(xiaohongshu_note)}字符)")
                
            elif tool_name == "WriteProductInfo":
                product_info = tool_args.get("product_info", {})
                print(f"📦 更新产品信息: {product_info}")
                
                updates["product_info"] = product_info
                tool_messages.append(ToolMessage(
                    tool_call_id=tool_id,
                    content="产品信息已更新。"
                ))
                ai_responses.append("📦 产品信息已成功更新")
                
            elif tool_name == "GenerateBloggerPersona":
                blogger_persona = tool_args.get("blogger_persona", {})
                print(f"👤 生成博主人设: {blogger_persona.get('name', '未命名')}")
                print(f"📝 人设风格: {blogger_persona.get('style', '未定义')}")
                
                updates["blogger_persona"] = blogger_persona
                tool_messages.append(ToolMessage(
                    tool_call_id=tool_id,
                    content="博主人设已生成完成。"
                ))
                ai_responses.append(f"👤 博主人设'{blogger_persona.get('name', '未命名')}'已生成")
                
            elif tool_name == "RetrieveFromKnowledgeBase":
                print(f"📚 开始文案库检索...")
                custom_query = tool_args.get("query", "")
                print(f"🔍 自定义查询: {custom_query if custom_query else '使用自动构建查询'}")
                
                # 调用RAG检索函数
                try:
                    rag_result = rag_retrieval_node(state)
                    retrieved_examples = rag_result.get("retrieved_examples", [])
                    retrieved_content = rag_result.get("retrieved_content", "")
                    
                    print(f"📚 检索完成，获得 {len(retrieved_examples)} 个文案示例")
                    
                    updates["retrieved_examples"] = retrieved_examples
                    updates["retrieved_content"] = retrieved_content
                    
                    tool_messages.append(ToolMessage(
                        tool_call_id=tool_id,
                        content=f"已从文案库检索到 {len(retrieved_examples)} 个相关文案示例，可用于参考创作。"
                    ))
                    ai_responses.append(f"📚 文案库检索完成，获得 {len(retrieved_examples)} 个相关示例")
                    
                except Exception as e:
                    print(f"❌ RAG检索失败: {str(e)}")
                    tool_messages.append(ToolMessage(
                        tool_call_id=tool_id,
                        content=f"文案库检索失败: {str(e)}"
                    ))
                    ai_responses.append(f"❌ 文案库检索失败: {str(e)}")
                
            elif tool_name == "Search":
                print(f"🔍 搜索请求将转发到搜索节点")
                # 搜索需要特殊处理，跳转到搜索节点
                return Command(
                    goto="search_node",
                    update={
                        "messages": [ai_message]
                    }
                )
                
            elif tool_name == "DeleteReferenceMaterials":
                print(f"🗑️ 删除请求将转发到删除节点")
                # 删除需要特殊处理，跳转到删除节点
                return Command(
                    goto="delete_node",
                    update={
                        "messages": [ai_message]
                    }
                )
            else:
                print(f"⚠️ 未知工具: {tool_name}")
                tool_messages.append(ToolMessage(
                    tool_call_id=tool_id,
                    content=f"未知工具: {tool_name}"
                ))
        
        # 生成综合回复消息
        if ai_responses:
            combined_response = "\n".join(ai_responses)
            final_ai_message = AIMessage(
                content=f"{combined_response}\n\n可以继续和我聊天或请求其他功能！"
            )
        else:
            final_ai_message = AIMessage(content="操作已完成！")
        
        print(f"✅ 所有工具调用处理完成，返回到router进行下一步决策")
        
        # 构建完整的消息序列
        all_messages = [ai_message] + tool_messages + [final_ai_message]
        
        return Command(
            goto="router_node",  # 回到router而不是直接结束
            update={
                **updates,
                "messages": all_messages
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