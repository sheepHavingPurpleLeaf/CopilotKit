import { Annotation } from "@langchain/langgraph";
import { CopilotKitStateAnnotation } from "@copilotkit/sdk-js/langgraph";

// Define a ReferenceMaterial annotation for Xiaohongshu note creation
const ReferenceMaterialAnnotation = Annotation.Root({
  url: Annotation<string>,
  title: Annotation<string>,
  description: Annotation<string>,
  type: Annotation<"competitor_note" | "user_review" | "product_info" | "trend_analysis" | "image">,
  content: Annotation<string>,
});

// Define ProductInfo annotation
const ProductInfoAnnotation = Annotation.Root({
  name: Annotation<string>,
  category: Annotation<string>,
  price: Annotation<string>,
  features: Annotation<string[]>,
  target_audience: Annotation<string>,
  selling_points: Annotation<string[]>,
});

// Define Tag annotation for hashtags/topics
const TagAnnotation = Annotation.Root({
  name: Annotation<string>,
  heat_level: Annotation<"high" | "medium" | "low">,
  category: Annotation<string>,
});

// Define a Log annotation with properties for message and done status
const LogAnnotation = Annotation.Root({
  message: Annotation<string>,
  done: Annotation<boolean>,
});

// Define the AgentState annotation for Xiaohongshu note generation
export const AgentStateAnnotation = Annotation.Root({
  model: Annotation<string>,
  product_info: Annotation<typeof ProductInfoAnnotation.State>,
  xiaohongshu_note: Annotation<string>,
  reference_materials: Annotation<(typeof ReferenceMaterialAnnotation.State)[]>,
  tags: Annotation<(typeof TagAnnotation.State)[]>,
  target_audience: Annotation<string>,
  note_style: Annotation<"grass_planting" | "review" | "tutorial" | "lifestyle" | "unboxing">,
  logs: Annotation<(typeof LogAnnotation.State)[]>,
  ...CopilotKitStateAnnotation.spec,
});

export type AgentState = typeof AgentStateAnnotation.State;
export type ReferenceMaterial = typeof ReferenceMaterialAnnotation.State;
export type ProductInfo = typeof ProductInfoAnnotation.State;
export type Tag = typeof TagAnnotation.State;

// 为向后兼容保留的类型别名
export type Resource = ReferenceMaterial;
