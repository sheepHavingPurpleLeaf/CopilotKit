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

// 话题标签类型
export type Tag = {
  name: string;
  heat_level: "high" | "medium" | "low";
  category: string;
};

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

// Agent状态类型
export type AgentState = {
  model: string;
  product_info: ProductInfo;
  xiaohongshu_note: string;
  reference_materials: ReferenceMaterial[];
  tags: Tag[];
  target_audience: string;
  note_style: NoteStyle;
  blogger_persona: BloggerPersona;
  logs: any[];
};

// 为向后兼容保留的类型别名
export type Resource = ReferenceMaterial;