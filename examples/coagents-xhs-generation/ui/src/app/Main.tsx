import { XiaohongshuCanvas } from "@/components/ResearchCanvas";
import { AgentState } from "@/lib/types";
import { useCoAgent } from "@copilotkit/react-core";
import { CopilotChat } from "@copilotkit/react-ui";
import { useCopilotChatSuggestions } from "@copilotkit/react-ui";

export default function Main() {
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
        selling_points: [],
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
      logs: [],
    },
  });

  useCopilotChatSuggestions({
    instructions: "帮我写一篇小红书笔记",
  });

  return (
    <>
      <h1 className="flex h-[60px] bg-[#0E103D] text-white items-center px-10 text-2xl font-medium">
        文案生成画板
      </h1>

      <div
        className="flex flex-1 border"
        style={{ height: "calc(100vh - 60px)" }}
      >
        <div className="flex-1 overflow-hidden">
          <XiaohongshuCanvas />
        </div>
        <div
          className="w-[500px] h-full flex-shrink-0"
          style={
            {
              "--copilot-kit-background-color": "#E0E9FD",
              "--copilot-kit-secondary-color": "#6766FC",
              "--copilot-kit-separator-color": "#b8b8b8",
              "--copilot-kit-primary-color": "#FFFFFF",
              "--copilot-kit-contrast-color": "#000000",
              "--copilot-kit-secondary-contrast-color": "#000",
            } as any
          }
        >
          <CopilotChat
            className="h-full"
            onSubmitMessage={async (message) => {
              // clear the logs before starting the new research
              setState({ ...state, logs: [] });
              await new Promise((resolve) => setTimeout(resolve, 30));
            }}
            labels={{
              initial: "你好！我是小红书笔记生成助手，可以帮你创作吸引人的小红书内容。请告诉我你的产品信息！",
            }}
          />
        </div>
      </div>
    </>
  );
}
