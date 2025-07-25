"""Demo"""

import os
from dotenv import load_dotenv
load_dotenv()

# pylint: disable=wrong-import-position
from fastapi import FastAPI
import uvicorn
from copilotkit.integrations.fastapi import add_fastapi_endpoint
from research_canvas.fixed_agent import FixedLangGraphAgent
from research_canvas.langgraph.agent import graph
from ag_ui_langgraph import add_langgraph_fastapi_endpoint

# from contextlib import asynccontextmanager
# from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
# @asynccontextmanager
# async def lifespan(fastapi_app: FastAPI):
#     """Lifespan for the FastAPI app."""
#     async with AsyncSqliteSaver.from_conn_string(
#         ":memory:"
#     ) as checkpointer:
#         # Create an async graph
#         graph = workflow.compile(checkpointer=checkpointer)

#         # Create SDK with the graph
#         sdk = CopilotKitRemoteEndpoint(
#             agents=[
#                 LangGraphAgent(
#                     name="research_agent",
#                     description="Research agent.",
#                     graph=graph,
#                 ),
#                 LangGraphAgent(
#                     name="research_agent_google_genai",
#                     description="Research agent.",
#                     graph=graph
#                 ),
#             ],
#         )

#         # Add the CopilotKit FastAPI endpoint
#         add_fastapi_endpoint(fastapi_app, sdk, "/copilotkit")
#         yield

# app = FastAPI(lifespan=lifespan)


app = FastAPI()

# Create the Xiaohongshu note generation agent using the fixed version
xiaohongshu_agent = FixedLangGraphAgent(
    name="xiaohongshu_agent",
    description="专业的小红书笔记生成助手，帮助商家创作吸引人的小红书内容。",
    graph=graph
)

# Add endpoints following the original project pattern
add_langgraph_fastapi_endpoint(
    app=app,
    agent=xiaohongshu_agent,
    path="/copilotkit/agents/xiaohongshu_agent"
)


@app.get("/health")
def health():
    """Health check."""
    return {"status": "ok"}


def main():
    """Run the uvicorn server."""
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(
        "research_canvas.demo:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        reload_dirs=(
            ["."] +
            (["../../../sdk-python/copilotkit"]
             if os.path.exists("../../../sdk-python/copilotkit")
             else []
             )
        )
    )
