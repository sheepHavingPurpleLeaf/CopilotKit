// 参考素材类型 (原Resource)
export type ReferenceMaterial = {
  url: string;
  title: string;
  description: string;
  type: "competitor_note" | "user_review" | "product_info" | "trend_analysis" | "image";
  content?: string;
};

// 产品信息类型
export type ProductInfo = {
  name: string;
  category: string;
  price?: string;
  features: string[];
  target_audience: string;
  selling_points: string[];
};

// 小红书笔记风格类型
export type NoteStyle = "grass_planting" | "review" | "tutorial" | "lifestyle" | "unboxing";


// 博主人设类型
export type BloggerPersona = {
  name: string;  // 博主人设名称，如"美妆达人小雅"
  style: string;  // 内容风格，如"亲和力强、专业可信"
  tone: string;  // 语言风格，如"亲切自然、略带俏皮"
  target_audience: string;  // 目标受众，如"25-35岁都市女性"
  expertise: string[];  // 专业领域，如["护肤", "彩妆", "时尚搭配"]
  personality_traits: string[];  // 个性特点，如["真实体验派", "性价比追求者"]
  content_themes: string[];  // 内容主题，如["产品测评", "使用心得", "避雷指南"]
};

// RAG检索示例类型
export type RetrievedExample = {
  id: string;
  title: string;
  content: string;
  similarity: number;
  url?: string;
};

// Agent状态类型
export type AgentState = {
  model: string;
  product_info: ProductInfo;
  xiaohongshu_note: string;
  reference_materials: ReferenceMaterial[];
  brief_data: BriefData | null;
  note_style: NoteStyle;
  blogger_persona: BloggerPersona;
  logs: any[];
  // RAG检索结果
  retrieved_examples?: RetrievedExample[];
  retrieved_content?: string;
};

// Brief 表数据类型
export type BriefData = {
  // 基本信息
  brandName: string;          // 品牌名称
  productName: string;        // 产品名称
  productPrice: string;       // 售价
  productFunction: string;    // 功效
  usageMethod: string;        // 使用方法
  storeLink: string;          // 店铺/链接
  
  // 产品介绍
  targetAudience: string;     // 目标受众（年龄、性别、职业、地域、兴趣爱好）
  usageScenario: string;      // 使用场景（室内/户外场景）
  coreSellingPoint1: string;  // 核心卖点1
  coreSellingPoint2: string;  // 核心卖点2
  coreSellingPoint3: string;  // 核心卖点3
  auxiliarySellingPoints: string; // 辅助卖点
  
  // 产品痛点切入
  painPointType: string;      // 类型
  budgetRange: string;        // 单条预算范围
  
  // 合作需求
  isSupplyScript: string;     // 是否供稿
  isCarLink: string;          // 是否挂车
  isFreeShipping: string;     // 是否免费寄样
  isReporting: string;        // 是否报备
  expectedPublishTime: string; // 预期发布时间
  
  // 博主要求
  collaboratorCount: string;  // 人数
  fansCount: string;          // 粉丝数目
  contentCategory: string;    // 内容类目
  bloggerGender: string;      // 博主性别
  bloggerAge: string;         // 博主年龄
  promotionChannels: string;  // 推广渠道
  
  // 内容形式 - 图文
  imageTextTitle: string;     // 标题要求
  imageTextPoints: string;    // 必须要点/可提要点
  imageCount: string;         // 图片数量要求
  productImageRatio: string;  // 产品图片比例
  textWordCount: string;      // 文案字数
  
  // 内容形式 - 视频
  videoLength: string;        // 视频时长
  videoPoints: string;        // 必提要点/可提要点
  videoDetailDisplay: string; // 产品细节展示
  
  // 内容风格和要求
  contentStyle: string;       // 内容风格
  hasSubtitles: string;       // 是否带有字幕
  bgmRequirements: string;    // BGM要求
  realPersonAppearance: string; // 是否真人出镜
  
  // 选题和关键词
  topicStyles: string;        // 选题风格
  mustIncludeKeywords: string; // 必带关键词
  mustIncludeTopics: string;  // 必带话题
  mustIncludeTags: string;    // 必带标签
  
  // 参考和审核
  excellentCaseReference: string; // 优秀案例参考
  deadlineConfirmation: string;   // 离期确认
  scriptProvided: string;         // 脚本/素材是否提供
  scriptAuditRequired: string;    // 脚本/素材是否审核
  
  // 发布要求
  contentRetentionPeriod: string; // 内容保留
  materialAuthorizationRights: string; // 素材授权
  brandPinToTop: string;          // 品牌置顶
  
  // 评论区引导与维护
  commentGuidance: string;        // 评论区引导与维护
  
  // 激励政策
  trafficMaintenance: string;     // 流量维护
  contentBoost: string;           // 内容加热
  
  // 其他
  otherRequirements: string;      // 其他事项
  uploadTime: string;             // 上传时间
};

// 为向后兼容保留的类型别名
export type Resource = ReferenceMaterial;