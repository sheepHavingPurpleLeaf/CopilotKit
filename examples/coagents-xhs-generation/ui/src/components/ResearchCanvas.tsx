"use client";

import { useState } from "react";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  useCoAgent,
  useCoAgentStateRender,
  useCopilotAction,
} from "@copilotkit/react-core";
import { Progress } from "./Progress";
import { EditResourceDialog } from "./EditResourceDialog";
import { AddResourceDialog } from "./AddResourceDialog";
import { Resources } from "./Resources";
import { AgentState, ReferenceMaterial, ProductInfo, Tag, BloggerPersona } from "@/lib/types";

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
      tags: [],
      target_audience: "",
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
      logs: []
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

  useCopilotAction({
    name: "DeleteReferenceMaterials",
    description:
      "Prompt the user for reference materials delete confirmation, and then perform deletion",
    available: "remote",
    parameters: [
      {
        name: "urls",
        type: "string[]",
      },
    ],
    renderAndWait: ({ args, status, handler }) => {
      return (
        <div
          className=""
          data-test-id="delete-material-generative-ui-container"
        >
          <div className="font-bold text-base mb-2">
            删除这些参考素材？
          </div>
          <Resources
            resources={referenceMaterials.filter((material) =>
              (args.urls || []).includes(material.url)
            )}
            customWidth={200}
          />
          {status === "executing" && (
            <div className="mt-4 flex justify-start space-x-2">
              <button
                onClick={() => handler("NO")}
                className="px-4 py-2 text-[#6766FC] border border-[#6766FC] rounded text-sm font-bold"
              >
                取消
              </button>
              <button
                data-test-id="button-delete"
                onClick={() => handler("YES")}
                className="px-4 py-2 bg-[#6766FC] text-white rounded text-sm font-bold"
              >
                删除
              </button>
            </div>
          )}
        </div>
      );
    },
  });

  const referenceMaterials: ReferenceMaterial[] = state.reference_materials || [];
  const setReferenceMaterials = (reference_materials: ReferenceMaterial[]) => {
    setState({ ...state, reference_materials });
  };

  // const [referenceMaterials, setReferenceMaterials] = useState<ReferenceMaterial[]>(dummyMaterials);
  const [newMaterial, setNewMaterial] = useState<ReferenceMaterial>({
    url: "",
    title: "",
    description: "",
    type: "competitor_note",
    content: "",
  });
  const [isAddMaterialOpen, setIsAddMaterialOpen] = useState(false);

  const addMaterial = () => {
    if (newMaterial.url) {
      setReferenceMaterials([...referenceMaterials, { ...newMaterial }]);
      setNewMaterial({ url: "", title: "", description: "", type: "competitor_note", content: "" });
      setIsAddMaterialOpen(false);
    }
  };

  const removeMaterial = (url: string) => {
    setReferenceMaterials(
      referenceMaterials.filter((material: ReferenceMaterial) => material.url !== url)
    );
  };

  const [editMaterial, setEditMaterial] = useState<ReferenceMaterial | null>(null);
  const [originalUrl, setOriginalUrl] = useState<string | null>(null);
  const [isEditMaterialOpen, setIsEditMaterialOpen] = useState(false);

  const handleCardClick = (material: ReferenceMaterial) => {
    setEditMaterial({ ...material }); // Ensure a new object is created
    setOriginalUrl(material.url); // Store the original URL
    setIsEditMaterialOpen(true);
  };

  const updateMaterial = () => {
    if (editMaterial && originalUrl) {
      setReferenceMaterials(
        referenceMaterials.map((material) =>
          material.url === originalUrl ? { ...editMaterial } : material
        )
      );
      setEditMaterial(null);
      setOriginalUrl(null);
      setIsEditMaterialOpen(false);
    }
  };

  return (
    <div className="w-full h-full overflow-y-auto p-10 bg-[#F5F8FF]">
      <div className="space-y-8 pb-10">
        <div>
          <h2 className="text-lg font-medium mb-3 text-primary">
            产品信息
          </h2>
          <div className="space-y-4 bg-background p-6 rounded-xl">
            <Input
              placeholder="产品名称"
              value={state.product_info?.name || ""}
              onChange={(e) =>
                setState({ 
                  ...state, 
                  product_info: { 
                    ...state.product_info, 
                    name: e.target.value 
                  } 
                })
              }
              aria-label="Product name"
              className="border-0 shadow-none text-md font-extralight focus-visible:ring-0 placeholder:text-slate-400"
            />
            <Input
              placeholder="产品类别"
              value={state.product_info?.category || ""}
              onChange={(e) =>
                setState({ 
                  ...state, 
                  product_info: { 
                    ...state.product_info, 
                    category: e.target.value 
                  } 
                })
              }
              aria-label="Product category"
              className="border-0 shadow-none text-md font-extralight focus-visible:ring-0 placeholder:text-slate-400"
            />
            <Input
              placeholder="目标用户"
              value={state.target_audience || ""}
              onChange={(e) =>
                setState({ ...state, target_audience: e.target.value })
              }
              aria-label="Target audience"
              className="border-0 shadow-none text-md font-extralight focus-visible:ring-0 placeholder:text-slate-400"
            />
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

        <div>
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-medium text-primary">参考素材</h2>
            <EditResourceDialog
              isOpen={isEditMaterialOpen}
              onOpenChange={setIsEditMaterialOpen}
              editResource={editMaterial}
              setEditResource={setEditMaterial}
              updateResource={updateMaterial}
            />
            <AddResourceDialog
              isOpen={isAddMaterialOpen}
              onOpenChange={setIsAddMaterialOpen}
              newResource={newMaterial}
              setNewResource={setNewMaterial}
              addResource={addMaterial}
            />
          </div>
          {referenceMaterials.length === 0 && (
            <div className="text-sm text-slate-400">
              点击上方按钮添加参考素材。
            </div>
          )}

          {referenceMaterials.length !== 0 && (
            <Resources
              resources={referenceMaterials}
              handleCardClick={handleCardClick}
              removeResource={removeMaterial}
            />
          )}
        </div>

        <div className="flex flex-col h-full">
          <h2 className="text-lg font-medium mb-3 text-primary">
            小红书笔记
          </h2>
          <Textarea
            data-test-id="xiaohongshu-note"
            placeholder="在这里撰写小红书笔记内容..."
            value={state.xiaohongshu_note || ""}
            onChange={(e) => setState({ ...state, xiaohongshu_note: e.target.value })}
            rows={10}
            aria-label="Xiaohongshu note"
            className="bg-background px-6 py-8 border-0 shadow-none rounded-xl text-md font-extralight focus-visible:ring-0 placeholder:text-slate-400"
            style={{ minHeight: "200px" }}
          />
          
          <div className="mt-4">
            <h3 className="text-md font-medium mb-2 text-primary">
              话题标签
            </h3>
            <div className="flex flex-wrap gap-2 bg-background p-4 rounded-xl min-h-[60px]">
              {(state.tags || []).map((tag, index) => (
                <span
                  key={index}
                  className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-blue-100 text-blue-800"
                >
                  #{tag.name}
                  <span className="ml-1 text-xs text-blue-600">({tag.heat_level})</span>
                </span>
              ))}
              {(!state.tags || state.tags.length === 0) && (
                <div className="text-sm text-slate-400">
                  AI将根据产品信息自动生成相关话题标签
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
