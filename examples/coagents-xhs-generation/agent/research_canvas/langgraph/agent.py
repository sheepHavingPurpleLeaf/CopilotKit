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
from research_canvas.langgraph.router_node import router_node
from research_canvas.langgraph.conversation_node import conversation_node
from research_canvas.langgraph.note_creation_node import note_creation_node
from research_canvas.langgraph.search import search_node
from research_canvas.langgraph.delete import delete_node, perform_delete_node

# Define a new graph with updated routing structure
workflow = StateGraph(AgentState)
workflow.add_node("download", download_node)
workflow.add_node("router_node", router_node)
workflow.add_node("conversation_node", conversation_node)
workflow.add_node("note_creation_node", note_creation_node)
workflow.add_node("search_node", search_node)
workflow.add_node("delete_node", delete_node)
workflow.add_node("perform_delete_node", perform_delete_node)

# Set up the new routing structure
workflow.set_entry_point("download")
workflow.add_edge("download", "router_node")

# Router uses conditional routing - no need to define explicit edges
# The Command.goto in router_node will handle routing

# End nodes
workflow.add_edge("conversation_node", END)  # Conversation ends directly
workflow.add_edge("note_creation_node", END)  # Note creation ends directly

# Handle special flows that need routing back
workflow.add_edge("delete_node", "perform_delete_node")
workflow.add_edge("perform_delete_node", "router_node")  # Back to router after delete
workflow.add_edge("search_node", "download")  # Search goes back to download

# Conditionally use a checkpointer based on the environment
# This allows compatibility with both LangGraph API and CopilotKit
compile_kwargs = {"interrupt_after": ["delete_node"]}

# Check if we should use a custom checkpointer
def should_use_custom_checkpointer():
    """
    Determine if we should use a custom checkpointer.
    Returns False for LangGraph managed environments where persistence is handled automatically.
    """
    langgraph_indicators = [
        # Direct LangGraph API flag
        os.environ.get("LANGGRAPH_API", "").lower() == "true",
        # LangGraph Studio detection
        os.environ.get("USER_AGENT", "").startswith("LangGraphStudio"),
        "langgraph-studio" in os.environ.get("HTTP_USER_AGENT", "").lower(),
        # LangGraph Cloud environment variables
        bool(os.environ.get("LANGSMITH_API_KEY")),
        bool(os.environ.get("POSTGRES_URI")),
        # Container/deployment detection
        os.path.exists("/.dockerenv"),
        bool(os.environ.get("KUBERNETES_SERVICE_HOST")),
    ]
    
    # If any LangGraph indicators are present, don't use custom checkpointer
    return not any(langgraph_indicators)

# Compile the graph with appropriate checkpointer configuration
if should_use_custom_checkpointer():
    # For local development with CopilotKit, use MemorySaver
    from langgraph.checkpoint.memory import MemorySaver
    memory = MemorySaver() 
    compile_kwargs["checkpointer"] = memory
    print("Using MemorySaver checkpointer for local development")
else:
    # For LangGraph managed environments, let the platform handle persistence
    print("Using platform-managed persistence (no custom checkpointer)")

graph = workflow.compile(**compile_kwargs)