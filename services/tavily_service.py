"""
Tavily 搜索服务
用于联网搜索实时新闻
"""
from typing import List, Dict, Any, Optional
from tavily import TavilyClient
from config.ai_conf import TAVILY_API_KEY


class TavilyService:
    """Tavily 搜索服务类"""
    
    def __init__(self):
        """初始化 Tavily 服务"""
        if not TAVILY_API_KEY or TAVILY_API_KEY == "your-tavily-api-key-here":
            print("警告: Tavily API Key 未配置，搜索功能将不可用")
            self.client = None
        else:
            self.client = TavilyClient(api_key=TAVILY_API_KEY)
    
    async def search_news(self, query: str, max_results: int = 5, 
                         search_depth: str = "basic") -> List[Dict[str, Any]]:
        """
        搜索新闻
        
        Args:
            query: 搜索关键词
            max_results: 最大返回结果数
            search_depth: 搜索深度，"basic" 或 "advanced"
            
        Returns:
            搜索结果列表
        """
        if not self.client:
            print("Tavily 客户端未初始化")
            return []
        
        try:
            # 调用 Tavily API
            response = self.client.search(
                query=query,
                max_results=max_results,
                search_depth=search_depth,
                include_answer=False,
                include_raw_content=False,
                include_images=False
            )
            
            # 解析结果
            results = []
            for result in response.get("results", []):
                results.append({
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "content": result.get("content", ""),
                    "score": result.get("score", 0),
                    "source": "tavily_search"
                })
            
            return results
            
        except Exception as e:
            print(f"Tavily 搜索失败: {str(e)}")
            return []
    
    async def search_with_summary(self, query: str, max_results: int = 3) -> Dict[str, Any]:
        """
        搜索并生成摘要
        
        Args:
            query: 搜索关键词
            max_results: 最大返回结果数
            
        Returns:
            包含摘要和结果的字典
        """
        if not self.client:
            return {"summary": "", "results": []}
        
        try:
            # 调用 Tavily API（带摘要）
            response = self.client.search(
                query=query,
                max_results=max_results,
                search_depth="advanced",
                include_answer=True
            )
            
            return {
                "summary": response.get("answer", ""),
                "results": [
                    {
                        "title": r.get("title", ""),
                        "url": r.get("url", ""),
                        "content": r.get("content", ""),
                        "score": r.get("score", 0),
                        "source": "tavily_search"
                    }
                    for r in response.get("results", [])
                ]
            }
            
        except Exception as e:
            print(f"Tavily 搜索摘要失败: {str(e)}")
            return {"summary": "", "results": []}
    
    def is_available(self) -> bool:
        """
        检查 Tavily 服务是否可用
        
        Returns:
            是否可用
        """
        return self.client is not None


# 创建全局单例
tavily_service = TavilyService()
