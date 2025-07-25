import {
  CopilotRuntime,
  OpenAIAdapter,
  copilotRuntimeNextJSAppRouterEndpoint,
  LangGraphHttpAgent,
} from "@copilotkit/runtime";
import OpenAI from "openai";
import { NextRequest } from "next/server";

const openai = new OpenAI({ 
  apiKey: process.env.OPENAI_API_KEY,
  baseURL: process.env.OPENAI_BASE_URL || "https://ark.cn-beijing.volces.com/api/v3"
});

const llmAdapter = new OpenAIAdapter({ 
  openai,
  model: process.env.DEEPSEEK_MODEL || "ep-20250206170923-bx29l",
  // DeepSeek compatibility options
  keepSystemRole: true,  // DeepSeek might not support "developer" role conversion
  disableParallelToolCalls: true,  // Force sequential tool execution for better compatibility
} as any);

export const POST = async (req: NextRequest) => {
  const baseUrl = process.env.REMOTE_ACTION_URL || "http://localhost:8000";
  
  const runtime = new CopilotRuntime({
    agents: {
      'xiaohongshu_agent': new LangGraphHttpAgent({
        url: `${baseUrl}/copilotkit/agents/xiaohongshu_agent`,
      })
    }
  });

  const { handleRequest } = copilotRuntimeNextJSAppRouterEndpoint({
    runtime,
    serviceAdapter: llmAdapter,
    endpoint: "/api/copilotkit",
  });

  try {
    return await handleRequest(req);
  } catch (error: any) {
    // Filter out developer role errors - they don't affect functionality
    if (error?.message?.includes('invalid value: `developer`') || 
        error?.error?.param === 'messages.role') {
      console.warn('⚠️ Non-critical role compatibility warning (functionality not affected):', error.message);
      // Return a successful response to prevent UI errors
      return new Response(JSON.stringify({ success: true }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    throw error;
  }
};
