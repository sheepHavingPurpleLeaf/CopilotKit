"""
RAG retrieval node for Xiaohongshu content generation.
Retrieves relevant content examples from the knowledge base.
"""
import os
import logging
from typing import List, Dict, Any
from research_canvas.langgraph.state import AgentState
from research_canvas.rag.builder import build_retriever
from research_canvas.rag.retriever import Resource

logger = logging.getLogger(__name__)


def load_xhs_rag_config() -> Dict[str, Any]:
    """Load XHS RAG configuration from environment variables."""
    return {
        "dataset_id": os.getenv("XHS_DATASET_ID", ""),
        "dataset_ids": [
            id.strip() for id in os.getenv("XHS_DATASET_IDS", "").split(",") 
            if id.strip()
        ],
        "max_retrieval_results": int(os.getenv("XHS_MAX_RESULTS", "5")),
        "similarity_threshold": float(os.getenv("XHS_SIMILARITY_THRESHOLD", "0.7")),
    }


def build_query_from_state(state: AgentState) -> str:
    """Build search query from agent state."""
    query_parts = []
    
    # Add product information
    if hasattr(state, 'product_info') and state.product_info:
        product_info = state.product_info
        if product_info.get('name'):
            query_parts.append(f"产品: {product_info['name']}")
        if product_info.get('category'):
            query_parts.append(f"类别: {product_info['category']}")
        if product_info.get('target_audience'):
            query_parts.append(f"目标受众: {product_info['target_audience']}")
        if product_info.get('selling_points'):
            selling_points = product_info['selling_points']
            if isinstance(selling_points, list) and selling_points:
                query_parts.append(f"卖点: {', '.join(selling_points)}")
    
    # Add brief data information if available
    if hasattr(state, 'brief_data') and state.brief_data:
        brief_data = state.brief_data
        if brief_data.get('brandName'):
            query_parts.append(f"品牌: {brief_data['brandName']}")
        if brief_data.get('productName'):
            query_parts.append(f"产品: {brief_data['productName']}")
        if brief_data.get('targetAudience'):
            query_parts.append(f"目标受众: {brief_data['targetAudience']}")
        if brief_data.get('contentStyle'):
            query_parts.append(f"风格: {brief_data['contentStyle']}")
    
    # Add note style preference
    if hasattr(state, 'note_style') and state.note_style:
        style_map = {
            "grass_planting": "种草",
            "review": "测评",
            "tutorial": "教程",
            "lifestyle": "生活方式",
            "unboxing": "开箱"
        }
        style_text = style_map.get(state.note_style, state.note_style)
        query_parts.append(f"风格: {style_text}")
    
    return " ".join(query_parts) if query_parts else "小红书文案"


def build_resources_from_config(config: Dict[str, Any]) -> List[Resource]:
    """Build resource list from configuration."""
    resources = []
    
    # Use multiple dataset IDs if configured
    if config.get("dataset_ids"):
        for dataset_id in config["dataset_ids"]:
            resources.append(
                Resource(
                    uri=f"rag://dataset/{dataset_id}",
                    title=f"XHS Dataset {dataset_id[:8]}...",
                    description="小红书文案数据集",
                )
            )
    # Use single dataset ID as fallback
    elif config.get("dataset_id"):
        dataset_id = config["dataset_id"]
        resources.append(
            Resource(
                uri=f"rag://dataset/{dataset_id}",
                title=f"XHS Dataset {dataset_id[:8]}...",
                description="小红书文案数据集",
            )
        )
    
    return resources


def rag_retrieval_node(state: AgentState) -> Dict[str, Any]:
    """
    RAG retrieval node that fetches relevant Xiaohongshu content examples.
    
    Args:
        state: Current agent state containing product info and preferences
        
    Returns:
        Dict containing retrieved examples and content for use in generation
    """
    logger.info("🔍 Starting RAG retrieval for Xiaohongshu content examples...")
    
    # 检查是否有Brief数据或产品信息，如果都没有则跳过RAG
    brief_data = state.get('brief_data')
    product_info = state.get('product_info', {})
    
    has_brief_data = brief_data and (brief_data.get('brandName') or brief_data.get('productName'))
    has_product_info = product_info and product_info.get('name')
    
    logger.info(f"📊 State check:")
    logger.info(f"  brief_data exists: {brief_data is not None}")
    logger.info(f"  brief_data content: {brief_data}")
    logger.info(f"  product_info exists: {bool(product_info)}")
    logger.info(f"  product_info content: {product_info}")
    logger.info(f"  has_brief_data: {has_brief_data}")
    logger.info(f"  has_product_info: {has_product_info}")
    
    if not has_brief_data and not has_product_info:
        logger.info("⚠️ No brief data or product info available, skipping RAG retrieval")
        return {
            "retrieved_examples": [],
            "retrieved_content": "暂无Brief数据或产品信息，RAG检索将在数据上传后自动进行"
        }
    
    # Load configuration
    config = load_xhs_rag_config()
    logger.info(f"⚙️ RAG Config loaded: {config}")
    
    # Build search query from current state
    query = build_query_from_state(state)
    logger.info(f"🔍 RAG query built: '{query}'")
    
    # Get retriever instance
    retriever = build_retriever()
    if not retriever:
        logger.warning("❌ No RAG retriever available, skipping retrieval")
        return {
            "retrieved_examples": [],
            "retrieved_content": "无可用的RAG检索服务"
        }
    
    try:
        # Build resource list from configuration
        resources = build_resources_from_config(config)
        logger.info(f"📁 Resources built: {len(resources)} resources")
        for i, resource in enumerate(resources):
            logger.info(f"  [{i+1}] {resource.uri} - {resource.title}")
        
        if not resources:
            logger.warning("❌ No datasets configured for retrieval")
            return {
                "retrieved_examples": [],
                "retrieved_content": "未配置小红书文案数据集"
            }
        
        # Retrieve relevant documents
        logger.info(f"🚀 Calling RAGFlow API with query: '{query}' and {len(resources)} resources")
        documents = retriever.query_relevant_documents(query, resources)
        logger.info(f"📄 Raw documents returned: {len(documents)}")
        
        # Log document details
        for i, doc in enumerate(documents):
            logger.info(f"  Document {i+1}: ID={doc.id}, Title='{doc.title}', Chunks={len(doc.chunks)}")
            for j, chunk in enumerate(doc.chunks):
                logger.info(f"    Chunk {j+1}: similarity={chunk.similarity:.3f}, content_length={len(chunk.content)}")
        
        # Process retrieval results
        retrieved_examples = []
        retrieved_content_parts = []
        max_results = config.get("max_retrieval_results", 5)
        similarity_threshold = config.get("similarity_threshold", 0.7)
        
        logger.info(f"🔧 Processing with max_results={max_results}, similarity_threshold={similarity_threshold}")
        
        for i, doc in enumerate(documents[:max_results]):
            if not doc.chunks:
                logger.info(f"  Document {i+1}: No chunks, skipping")
                continue
                
            # Get the most relevant chunk from each document
            best_chunk = max(doc.chunks, key=lambda x: x.similarity)
            logger.info(f"  Document {i+1}: Best chunk similarity={best_chunk.similarity:.3f}")
            
            # Apply similarity threshold filtering
            if best_chunk.similarity < similarity_threshold:
                logger.info(f"  Document {i+1}: Filtered out (similarity {best_chunk.similarity:.3f} < {similarity_threshold})")
                continue
            
            # Create example entry
            example = {
                "id": doc.id,
                "title": doc.title or "未知标题",
                "content": best_chunk.content,
                "similarity": best_chunk.similarity,
                "url": doc.url,
            }
            retrieved_examples.append(example)
            
            # Build merged content for prompt
            retrieved_content_parts.append(
                f"【参考文案】\n标题: {doc.title or '未知'}\n内容: {best_chunk.content}\n"
            )
        
        # Combine all retrieved content
        retrieved_content = (
            "\n" + "="*50 + "\n".join(retrieved_content_parts)
            if retrieved_content_parts
            else "未找到相关的小红书文案示例"
        )
        
        logger.info(f"✅ RAG retrieval completed:")
        logger.info(f"  📊 Total raw documents: {len(documents)}")
        logger.info(f"  ✨ Final examples after filtering: {len(retrieved_examples)}")
        logger.info(f"  📝 Query used: '{query}'")
        logger.info(f"  🎯 Similarity threshold: {similarity_threshold}")
        
        if retrieved_examples:
            logger.info(f"  📋 Retrieved examples:")
            for i, example in enumerate(retrieved_examples):
                logger.info(f"    [{i+1}] Title: {example['title']}, Similarity: {example['similarity']:.3f}")
        else:
            logger.warning(f"  ⚠️ No examples passed similarity filter (threshold={similarity_threshold})")
        
        return {
            "retrieved_examples": retrieved_examples,
            "retrieved_content": retrieved_content,
        }
        
    except Exception as e:
        logger.error(f"Error during RAG retrieval: {str(e)}")
        return {
            "retrieved_examples": [],
            "retrieved_content": f"RAG检索过程中出现错误: {str(e)}",
        }