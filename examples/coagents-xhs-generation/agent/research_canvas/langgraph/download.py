"""
This module contains the implementation for downloading Xiaohongshu reference materials.
Supports text content, images, and multimedia content.
"""

import aiohttp
import html2text
from copilotkit.langgraph import copilotkit_emit_state
from langchain_core.runnables import RunnableConfig
from research_canvas.langgraph.state import AgentState

_RESOURCE_CACHE = {}

def get_resource(url: str):
    """
    Get a Xiaohongshu reference material from the cache.
    """
    return _RESOURCE_CACHE.get(url, "")


_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3" # pylint: disable=line-too-long

async def _download_resource(url: str):
    """
    Download a Xiaohongshu reference material from the internet asynchronously.
    Supports text content, images, and multimedia.
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url,
                headers={"User-Agent": _USER_AGENT},
                timeout=aiohttp.ClientTimeout(total=15)  # Increased timeout for multimedia
            ) as response:
                response.raise_for_status()
                content_type = response.headers.get('content-type', '').lower()
                
                # Handle different content types
                if 'image' in content_type:
                    # For images, store metadata and URL
                    content = f"[图片素材] {url}\n内容类型: {content_type}"
                elif 'video' in content_type or 'audio' in content_type:
                    # For multimedia, store metadata and URL
                    content = f"[多媒体素材] {url}\n内容类型: {content_type}"
                else:
                    # For text/HTML content, convert to markdown
                    html_content = await response.text()
                    content = html2text.html2text(html_content)
                
                _RESOURCE_CACHE[url] = content
                return content
    except Exception as e: # pylint: disable=broad-except
        _RESOURCE_CACHE[url] = "ERROR"
        return f"Error downloading reference material: {e}"

async def download_node(state: AgentState, config: RunnableConfig):
    """
    Download Xiaohongshu reference materials from the internet.
    Supports text content, images, and multimedia.
    """
    state["reference_materials"] = state.get("reference_materials", [])
    state["logs"] = state.get("logs", [])
    materials_to_download = []

    logs_offset = len(state["logs"])

    # Find reference materials that are not downloaded
    for material in state["reference_materials"]:
        if not get_resource(material["url"]):
            materials_to_download.append(material)
            material_type = material.get("type", "unknown")
            state["logs"].append({
                "message": f"正在下载{material_type}素材: {material['title']}",
                "done": False
            })

    # Emit the state to let the UI update
    await copilotkit_emit_state(config, state)

    # Download the reference materials
    for i, material in enumerate(materials_to_download):
        await _download_resource(material["url"])
        state["logs"][logs_offset + i]["done"] = True

        # update UI
        await copilotkit_emit_state(config, state)

    return state
