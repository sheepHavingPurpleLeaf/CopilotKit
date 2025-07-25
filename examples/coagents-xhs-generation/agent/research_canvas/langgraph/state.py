"""
This is the state definition for the Xiaohongshu note generation AI.
It defines the state of the agent and the state of the conversation.
"""

from typing import List, TypedDict, Literal
from langgraph.graph import MessagesState

class ReferenceMaterial(TypedDict):
    """
    Represents a reference material for creating Xiaohongshu notes.
    """
    url: str
    title: str
    description: str
    type: Literal["competitor_note", "user_review", "product_info", "trend_analysis", "image"]
    content: str

class ProductInfo(TypedDict):
    """
    Represents product information for creating Xiaohongshu notes.
    """
    name: str
    category: str
    price: str
    features: List[str]
    target_audience: str
    selling_points: List[str]

class Tag(TypedDict):
    """
    Represents a hashtag/topic tag for Xiaohongshu notes.
    """
    name: str
    heat_level: Literal["high", "medium", "low"]
    category: str

class BloggerPersona(TypedDict):
    """
    Represents a blogger persona for creating Xiaohongshu notes.
    """
    name: str  # 博主人设名称，如"美妆达人小雅"
    style: str  # 内容风格，如"亲和力强、专业可信"
    tone: str  # 语言风格，如"亲切自然、略带俏皮"
    target_audience: str  # 目标受众，如"25-35岁都市女性"
    expertise: List[str]  # 专业领域，如["护肤", "彩妆", "时尚搭配"]
    personality_traits: List[str]  # 个性特点，如["真实体验派", "性价比追求者"]
    content_themes: List[str]  # 内容主题，如["产品测评", "使用心得", "避雷指南"]

class Log(TypedDict):
    """
    Represents a log of an action performed by the agent.
    """
    message: str
    done: bool

class AgentState(MessagesState):
    """
    This is the state of the Xiaohongshu note generation agent.
    It is a subclass of the MessagesState class from langgraph.
    
    All fields are optional with proper defaults to avoid initialization issues.
    """
    model: str = ""
    product_info: ProductInfo = {}  # Default to empty dict
    xiaohongshu_note: str = ""
    reference_materials: List[ReferenceMaterial] = []  # Default to empty list
    tags: List[Tag] = []  # Default to empty list
    target_audience: str = ""
    note_style: Literal["grass_planting", "review", "tutorial", "lifestyle", "unboxing"] = "grass_planting"
    blogger_persona: BloggerPersona = {}  # Default to empty dict
    logs: List[Log] = []  # Default to empty list

# 为向后兼容保留的类型别名
Resource = ReferenceMaterial
