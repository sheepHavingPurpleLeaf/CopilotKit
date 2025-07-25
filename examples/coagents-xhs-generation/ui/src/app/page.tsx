"use client";

import { CopilotKit } from "@copilotkit/react-core";
import Main from "./Main";

export default function Home() {
  return (
    <CopilotKit 
      runtimeUrl="/api/copilotkit" 
      showDevConsole={false} 
      agent="xiaohongshu_agent"
    >
      <Main />
    </CopilotKit>
  );
}
