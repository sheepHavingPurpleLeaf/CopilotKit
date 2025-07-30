"use client";

import { useState, useEffect, useRef } from "react";
import { Textarea } from "@/components/ui/textarea";
import {
  useCoAgent,
  useCoAgentStateRender,
  useCopilotAction,
} from "@copilotkit/react-core";
import { Progress } from "./Progress";
import { ProductInfoTabs } from "./ProductInfoTabs";
import { AgentState, ReferenceMaterial, ProductInfo, BloggerPersona, BriefData, RetrievedExample } from "@/lib/types";

export function XiaohongshuCanvas() {
  const { state, setState } = useCoAgent<AgentState>({
    name: "xiaohongshu_agent",
    initialState: {
      model: "deepseek",
      product_info: {
        name: "",
        category: "",
        price: "",
        features: [],
        target_audience: "",
        selling_points: []
      },
      xiaohongshu_note: "",
      reference_materials: [],
      brief_data: null,
      note_style: "grass_planting",
      blogger_persona: {
        name: "",
        style: "",
        tone: "",
        target_audience: "",
        expertise: [],
        personality_traits: [],
        content_themes: []
      },
      logs: [],
      retrieved_examples: [],
      retrieved_content: ""
    },
  });


  useCoAgentStateRender({
    name: "xiaohongshu_agent",
    render: ({ state, nodeName, status }) => {
      if (!state.logs || state.logs.length === 0) {
        return null;
      }
      return <Progress logs={state.logs} />;
    },
  });

  // 用于跟踪之前的brief_data状态
  const prevBriefDataRef = useRef<BriefData | null>(null);


  // 移除了 DeleteReferenceMaterials action，因为现在使用 Brief 表代替参考素材

  // 产品信息更新处理
  const handleProductInfoUpdate = (productInfo: ProductInfo) => {
    setState(prevState => ({ 
      model: prevState?.model || "deepseek",
      xiaohongshu_note: prevState?.xiaohongshu_note || "",
      reference_materials: prevState?.reference_materials || [],
      brief_data: prevState?.brief_data || null,
      note_style: prevState?.note_style || "grass_planting",
      blogger_persona: prevState?.blogger_persona || {
        name: "",
        style: "",
        tone: "",
        target_audience: "",
        expertise: [],
        personality_traits: [],
        content_themes: []
      },
      logs: prevState?.logs || [],
      retrieved_examples: prevState?.retrieved_examples || [],
      retrieved_content: prevState?.retrieved_content || "",
      product_info: productInfo,
    }));
  };

  // Brief 数据更新处理
  const handleBriefDataUpdate = async (briefData: BriefData | null) => {
    // 保存到localStorage作为备份，防止Hot Refresh丢失数据
    if (briefData) {
      localStorage.setItem('xhs-brief-data', JSON.stringify(briefData));
    } else {
      localStorage.removeItem('xhs-brief-data');
    }
    
    // 更新状态
    setState(prevState => ({
      model: prevState?.model || "deepseek",
      product_info: prevState?.product_info || {
        name: "",
        category: "",
        price: "",
        features: [],
        target_audience: "",
        selling_points: []
      },
      xiaohongshu_note: prevState?.xiaohongshu_note || "",
      reference_materials: prevState?.reference_materials || [],
      note_style: prevState?.note_style || "grass_planting",
      blogger_persona: prevState?.blogger_persona || {
        name: "",
        style: "",
        tone: "",
        target_audience: "",
        expertise: [],
        personality_traits: [],
        content_themes: []
      },
      logs: prevState?.logs || [],
      retrieved_examples: prevState?.retrieved_examples || [],
      retrieved_content: prevState?.retrieved_content || "",
      brief_data: briefData,
    }));
    
    // 检查是否是新的Brief数据上传
    const isNewBriefData = briefData && !prevBriefDataRef.current;
    prevBriefDataRef.current = briefData;
    
  };

  // 在组件初始化时恢复localStorage中的Brief数据
  useEffect(() => {
    const savedBriefData = localStorage.getItem('xhs-brief-data');
    if (savedBriefData && !state.brief_data) {
      try {
        const briefData = JSON.parse(savedBriefData);
        setState(prevState => ({ 
          model: prevState?.model || "deepseek",
          product_info: prevState?.product_info || {
            name: "",
            category: "",
            price: "",
            features: [],
            target_audience: "",
            selling_points: []
          },
          xiaohongshu_note: prevState?.xiaohongshu_note || "",
          reference_materials: prevState?.reference_materials || [],
          note_style: prevState?.note_style || "grass_planting",
          blogger_persona: prevState?.blogger_persona || {
            name: "",
            style: "",
            tone: "",
            target_audience: "",
            expertise: [],
            personality_traits: [],
            content_themes: []
          },
          logs: prevState?.logs || [],
          retrieved_examples: prevState?.retrieved_examples || [],
          retrieved_content: prevState?.retrieved_content || "",
          brief_data: briefData,
        }));
      } catch (error) {
        localStorage.removeItem('xhs-brief-data');
      }
    }
  }, [state.brief_data, setState]);

  
  
  return (
    <div className="w-full h-full overflow-y-auto p-10 bg-[#F5F8FF]">
      <div className="space-y-8 pb-10">
        <ProductInfoTabs
          productInfo={state.product_info || {
            name: "",
            category: "",
            price: "",
            features: [],
            target_audience: "",
            selling_points: []
          }}
          briefData={state.brief_data}
          onProductInfoUpdate={handleProductInfoUpdate}
          onBriefDataUpdate={handleBriefDataUpdate}
        />

        {/* 文案库检索 - 移到博主人设之前 */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-lg font-medium text-primary">
              文案库检索
            </h2>
          </div>
          <div className="space-y-4 bg-background p-6 rounded-xl">
            {state.retrieved_examples && state.retrieved_examples.length > 0 ? (
              <div className="space-y-3">
                <div className="text-sm text-slate-600 mb-3">
                  已检索到 {state.retrieved_examples.length} 个相关文案示例
                </div>
                {state.retrieved_examples.slice(0, 3).map((example, index) => (
                  <div
                    key={example.id}
                    className="border border-slate-200 rounded-lg p-3 bg-slate-50"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-slate-700">
                        {example.title}
                      </span>
                      <span className="text-xs text-slate-500 bg-green-100 px-2 py-1 rounded">
                        相似度: {(example.similarity * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="text-xs text-slate-600 line-clamp-3">
                      {example.content.substring(0, 120)}...
                    </div>
                  </div>
                ))}
                {state.retrieved_examples.length > 3 && (
                  <div className="text-xs text-slate-500 text-center">
                    还有 {state.retrieved_examples.length - 3} 个示例可供参考
                  </div>
                )}
              </div>
            ) : (
              <div className="text-sm text-slate-400">
                上传Brief数据后，系统将自动从文案库检索相关示例
              </div>
            )}
          </div>
        </div>

        <div>
          <h2 className="text-lg font-medium mb-3 text-primary">
            博主人设
          </h2>
          <div className="space-y-4 bg-background p-6 rounded-xl">
            {state.blogger_persona && state.blogger_persona.name ? (
              <div className="space-y-3">
                <div className="flex items-center space-x-2">
                  <span className="text-sm font-medium text-slate-600">博主名称:</span>
                  <span className="text-sm text-slate-800 font-medium">{state.blogger_persona.name}</span>
                </div>
                <div className="flex items-start space-x-2">
                  <span className="text-sm font-medium text-slate-600 mt-0.5">内容风格:</span>
                  <span className="text-sm text-slate-800 flex-1">{state.blogger_persona.style}</span>
                </div>
                <div className="flex items-start space-x-2">
                  <span className="text-sm font-medium text-slate-600 mt-0.5">语言风格:</span>
                  <span className="text-sm text-slate-800 flex-1">{state.blogger_persona.tone}</span>
                </div>
                <div className="flex items-start space-x-2">
                  <span className="text-sm font-medium text-slate-600 mt-0.5">目标受众:</span>
                  <span className="text-sm text-slate-800 flex-1">{state.blogger_persona.target_audience}</span>
                </div>
                {state.blogger_persona.expertise && state.blogger_persona.expertise.length > 0 && (
                  <div className="flex items-start space-x-2">
                    <span className="text-sm font-medium text-slate-600 mt-0.5">专业领域:</span>
                    <div className="flex flex-wrap gap-1 flex-1">
                      {state.blogger_persona.expertise.map((skill, index) => (
                        <span
                          key={index}
                          className="inline-flex items-center px-2 py-1 rounded-md text-xs bg-green-100 text-green-800"
                        >
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                {state.blogger_persona.personality_traits && state.blogger_persona.personality_traits.length > 0 && (
                  <div className="flex items-start space-x-2">
                    <span className="text-sm font-medium text-slate-600 mt-0.5">个性特点:</span>
                    <div className="flex flex-wrap gap-1 flex-1">
                      {state.blogger_persona.personality_traits.map((trait, index) => (
                        <span
                          key={index}
                          className="inline-flex items-center px-2 py-1 rounded-md text-xs bg-purple-100 text-purple-800"
                        >
                          {trait}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                {state.blogger_persona.content_themes && state.blogger_persona.content_themes.length > 0 && (
                  <div className="flex items-start space-x-2">
                    <span className="text-sm font-medium text-slate-600 mt-0.5">内容主题:</span>
                    <div className="flex flex-wrap gap-1 flex-1">
                      {state.blogger_persona.content_themes.map((theme, index) => (
                        <span
                          key={index}
                          className="inline-flex items-center px-2 py-1 rounded-md text-xs bg-orange-100 text-orange-800"
                        >
                          {theme}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-sm text-slate-400">
                提供产品信息后，AI将生成合适的博主人设
              </div>
            )}
          </div>
        </div>


        <div className="flex flex-col h-full">
          <h2 className="text-lg font-medium mb-3 text-primary">
            小红书笔记
          </h2>
          <Textarea
            data-test-id="xiaohongshu-note"
            placeholder="在这里撰写小红书笔记内容..."
            value={state.xiaohongshu_note || ""}
            onChange={(e) => setState({ 
              ...state, 
              xiaohongshu_note: e.target.value,
            })}
            rows={10}
            aria-label="Xiaohongshu note"
            className="bg-background px-6 py-8 border-0 shadow-none rounded-xl text-md font-extralight focus-visible:ring-0 placeholder:text-slate-400"
            style={{ minHeight: "200px" }}
          />
        </div>
      </div>
    </div>
  );
}
