"""
Agent 工具定义
定义 Agent 可以使用的各种工具
"""
from typing import List, Dict, Any, Optional
from services.tavily_service import tavily_service
from services.chroma_service import vector_db_service


class SearchTool:
    """联网搜索工具"""
    
    name = "web_search"
    description = "搜索实时新闻和最新信息。当用户询问最近的新闻、时事、或需要最新信息时使用此工具。"
    
    @staticmethod
    async def execute(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        执行联网搜索
        
        Args:
            query: 搜索关键词
            max_results: 最大返回结果数
            
        Returns:
            搜索结果列表
        """
        if not tavily_service.is_available():
            return []
        
        results = await tavily_service.search_news(
            query=query,
            max_results=max_results
        )
        
        # 添加来源标识
        for result in results:
            result["source"] = "tavily_search"
        
        return results


class KnowledgeRetrievalTool:
    """本地知识库检索工具"""
    
    name = "knowledge_retrieval"
    description = "从本地新闻数据库中检索相关新闻。当用户询问历史新闻、特定主题的新闻、或数据库中的信息时使用此工具。"
    
    @staticmethod
    async def execute(
        query: str, 
        category_id: Optional[int] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        执行知识库检索
        
        Args:
            query: 查询文本
            category_id: 可选的分类ID过滤
            top_k: 返回最相似的K条新闻
            
        Returns:
            检索结果列表
        """
        results = await vector_db_service.search_similar_news(
            query=query,
            category_id=category_id,
            top_k=top_k
        )
        
        # 添加来源标识
        for result in results:
            result["source"] = "local_knowledge"
            # 转换 news_id 为 id 以保持统一格式
            if "news_id" in result:
                result["id"] = result["news_id"]
        
        return results


class DateTimeTool:
    """日期时间工具"""
    
    name = "get_current_time"
    description = "获取当前日期和时间。当用户询问时间相关的问题时使用。"
    
    @staticmethod
    async def execute() -> str:
        """
        获取当前时间
        
        Returns:
            当前时间的字符串表示
        """
        from datetime import datetime
        now = datetime.now()
        return now.strftime("%Y年%m月%d日 %H:%M:%S")


# 工具注册表
TOOLS_REGISTRY = {
    "web_search": SearchTool,
    "knowledge_retrieval": KnowledgeRetrievalTool,
    "get_current_time": DateTimeTool,
}


def get_tool_names() -> List[str]:
    """获取所有工具名称"""
    return list(TOOLS_REGISTRY.keys())


def get_tool_description() -> str:
    """获取工具描述（用于 LLM 理解）"""
    descriptions = []
    for name, tool_class in TOOLS_REGISTRY.items():
        descriptions.append(f"- {name}: {tool_class.description}")
    return "\n".join(descriptions)
