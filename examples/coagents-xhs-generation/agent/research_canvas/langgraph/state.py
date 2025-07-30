"""
This is the state definition for the Xiaohongshu note generation AI.
It defines the state of the agent and the state of the conversation.
"""

from typing import List, TypedDict, Literal, Optional
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

class BriefData(TypedDict):
    """
    Represents brief data uploaded by user for creating Xiaohongshu notes.
    """
    # 基本信息
    brandName: str          # 品牌名称
    productName: str        # 产品名称
    productPrice: str       # 售价
    productFunction: str    # 功效
    usageMethod: str        # 使用方法
    storeLink: str          # 店铺/链接
    
    # 产品介绍
    targetAudience: str     # 目标受众（年龄、性别、职业、地域、兴趣爱好）
    usageScenario: str      # 使用场景（室内/户外场景）
    coreSellingPoint1: str  # 核心卖点1
    coreSellingPoint2: str  # 核心卖点2
    coreSellingPoint3: str  # 核心卖点3
    auxiliarySellingPoints: str # 辅助卖点
    
    # 产品痛点切入
    painPointType: str      # 类型
    budgetRange: str        # 单条预算范围
    
    # 合作需求
    isSupplyScript: str     # 是否供稿
    isCarLink: str          # 是否挂车
    isFreeShipping: str     # 是否免费寄样
    isReporting: str        # 是否报备
    expectedPublishTime: str # 预期发布时间
    
    # 博主要求
    collaboratorCount: str  # 人数
    fansCount: str          # 粉丝数目
    contentCategory: str    # 内容类目
    bloggerGender: str      # 博主性别
    bloggerAge: str         # 博主年龄
    promotionChannels: str  # 推广渠道
    
    # 内容形式 - 图文
    imageTextTitle: str     # 标题要求
    imageTextPoints: str    # 必须要点/可提要点
    imageCount: str         # 图片数量要求
    productImageRatio: str  # 产品图片比例
    textWordCount: str      # 文案字数
    
    # 内容形式 - 视频
    videoLength: str        # 视频时长
    videoPoints: str        # 必提要点/可提要点
    videoDetailDisplay: str # 产品细节展示
    
    # 内容风格和要求
    contentStyle: str       # 内容风格
    hasSubtitles: str       # 是否带有字幕
    bgmRequirements: str    # BGM要求
    realPersonAppearance: str # 是否真人出镜
    
    # 选题和关键词
    topicStyles: str        # 选题风格
    mustIncludeKeywords: str # 必带关键词
    mustIncludeTopics: str  # 必带话题
    mustIncludeTags: str    # 必带标签
    
    # 参考和审核
    excellentCaseReference: str # 优秀案例参考
    deadlineConfirmation: str   # 离期确认
    scriptProvided: str         # 脚本/素材是否提供
    scriptAuditRequired: str    # 脚本/素材是否审核
    
    # 发布要求
    contentRetentionPeriod: str # 内容保留
    materialAuthorizationRights: str # 素材授权
    brandPinToTop: str          # 品牌置顶
    
    # 评论区引导与维护
    commentGuidance: str        # 评论区引导与维护
    
    # 激励政策
    trafficMaintenance: str     # 流量维护
    contentBoost: str           # 内容加热
    
    # 其他
    otherRequirements: str      # 其他事项
    uploadTime: str             # 上传时间

class Log(TypedDict):
    """
    Represents a log of an action performed by the agent.
    """
    message: str
    done: bool

class RetrievedExample(TypedDict):
    """
    Represents a retrieved example from RAG knowledge base.
    """
    id: str
    title: str
    content: str
    similarity: float
    url: Optional[str]

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
    brief_data: Optional[BriefData] = None  # Brief 表数据
    note_style: Literal["grass_planting", "review", "tutorial", "lifestyle", "unboxing"] = "grass_planting"
    blogger_persona: BloggerPersona = {}  # Default to empty dict
    logs: List[Log] = []  # Default to empty list
    # RAG retrieval results
    retrieved_examples: List[RetrievedExample] = []  # Retrieved content examples
    retrieved_content: str = ""  # Merged retrieved content for prompts

# 为向后兼容保留的类型别名
Resource = ReferenceMaterial
