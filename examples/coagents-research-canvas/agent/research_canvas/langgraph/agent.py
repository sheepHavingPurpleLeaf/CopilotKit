"""
This is the main entry point for the AI.
It defines the workflow graph and the entry point for the agent.
"""
# pylint: disable=line-too-long, unused-import
import json
import os
from typing import cast

from langchain_core.messages import AIMessage, ToolMessage
from langgraph.graph import StateGraph, END
from research_canvas.langgraph.state import AgentState
from research_canvas.langgraph.download import download_node
from research_canvas.langgraph.chat import chat_node
from research_canvas.langgraph.search import search_node
from research_canvas.langgraph.delete import delete_node, perform_delete_node

# Define a new graph
workflow = StateGraph(AgentState)
workflow.add_node("download", download_node)
workflow.add_node("chat_node", chat_node)
workflow.add_node("search_node", search_node)
workflow.add_node("delete_node", delete_node)
workflow.add_node("perform_delete_node", perform_delete_node)


workflow.set_entry_point("download")
workflow.add_edge("download", "chat_node")
workflow.add_edge("delete_node", "perform_delete_node")
workflow.add_edge("perform_delete_node", "chat_node")
workflow.add_edge("search_node", "download")

# Conditionally use a checkpointer based on the environment
# This allows compatibility with both LangGraph API and CopilotKit
compile_kwargs = {"interrupt_after": ["delete_node"]}

# Check if we're running in LangGraph Studio/API mode
# Multiple ways to detect Studio environment
is_langgraph_studio = (
    os.environ.get("LANGGRAPH_API", "false").lower() == "true" or
    os.environ.get("LANGGRAPH_RUNTIME", "") == "inmem" or
    "langgraph_runtime_inmem" in str(os.environ.get("PYTHONPATH", "")) or
    any("langgraph" in str(v) for v in os.environ.values() if isinstance(v, str))
)

if is_langgraph_studio:
    # When running in LangGraph Studio/API, don't use a custom checkpointer
    print("🎨 Running in LangGraph Studio mode - using built-in persistence")
    graph = workflow.compile(**compile_kwargs)
else:
    # For CopilotKit and other contexts, use MemorySaver
    print("🔧 Running in CopilotKit mode - using MemorySaver")
    from langgraph.checkpoint.memory import MemorySaver
    memory = MemorySaver()
    compile_kwargs["checkpointer"] = memory
    graph = workflow.compile(**compile_kwargs)