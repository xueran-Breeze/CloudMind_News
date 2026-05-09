"""
ChromaDB 向量数据库服务
用于存储和检索新闻向量
"""
import os
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from config.ai_conf import CHROMA_DATA_PATH, CHROMA_COLLECTION_NAME
from services.embedding_service import embedding_service


class VectorDBService:
    """ChromaDB 向量数据库服务类"""
    
    def __init__(self):
        """初始化 ChromaDB 服务"""
        self.collection_name = CHROMA_COLLECTION_NAME
        self.data_path = CHROMA_DATA_PATH
        self.dimension = embedding_service.get_embedding_dimension()
        self._initialized = False
        self.client = None
        self.collection = None
    
    def _ensure_data_dir(self):
        """确保数据目录存在"""
        if not os.path.exists(self.data_path):
            os.makedirs(self.data_path)
    
    def initialize(self):
        """
        初始化 ChromaDB 连接和集合
        需要在应用启动时调用一次
        """
        if self._initialized:
            return
        
        try:
            # 确保数据目录存在
            self._ensure_data_dir()
            
            # 创建持久化客户端
            self.client = chromadb.PersistentClient(
                path=self.data_path,
                settings=Settings(anonymized_telemetry=False)
            )
            
            # 创建或获取集合
            self._create_collection()
            
            self._initialized = True
            print(f"ChromaDB 服务初始化成功，集合: {self.collection_name}")
            
        except Exception as e:
            raise Exception(f"ChromaDB 初始化失败: {str(e)}")
    
    def _create_collection(self):
        """创建新闻向量集合"""
        try:
            # 尝试获取现有集合
            self.collection = self.client.get_collection(name=self.collection_name)
            print(f"使用已存在的集合: {self.collection_name}")
        except:
            # 创建新集合
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "新闻向量索引集合"}
            )
            print(f"创建新集合: {self.collection_name}")
    
    async def insert_news(self, news_id: int, category_id: int, title: str, 
                         content: str, publish_time: str, author: str = "") -> bool:
        """
        插入单条新闻向量
        
        Args:
            news_id: 新闻ID
            category_id: 分类ID
            title: 新闻标题
            content: 新闻内容
            publish_time: 发布时间
            author: 作者
            
        Returns:
            是否插入成功
        """
        try:
            # 确保已初始化
            if not self._initialized:
                self.initialize()
            
            # 生成向量嵌入（使用标题+内容）
            text = f"{title} {content[:500]}"  # 只取前500字符避免过长
            embedding = await embedding_service.get_embedding(text)
            
            # 准备元数据
            metadata = {
                "news_id": news_id,
                "category_id": category_id,
                "title": title,
                "content": content[:9000],  # 限制长度
                "publish_time": publish_time,
                "author": author
            }
            
            # 插入数据（使用 news_id 作为 ID）
            self.collection.add(
                ids=[f"news_{news_id}"],
                embeddings=[embedding],
                metadatas=[metadata]
            )
            
            return True
            
        except Exception as e:
            print(f"插入新闻向量失败: {str(e)}")
            return False
    
    async def insert_batch_news(self, news_list: List[Dict[str, Any]]) -> int:
        """
        批量插入新闻向量
        
        Args:
            news_list: 新闻列表，每个元素包含 news_id, category_id, title, content, publish_time, author
            
        Returns:
            成功插入的数量
        """
        if not news_list:
            return 0
        
        success_count = 0
        for news in news_list:
            try:
                result = await self.insert_news(
                    news_id=news["news_id"],
                    category_id=news["category_id"],
                    title=news["title"],
                    content=news["content"],
                    publish_time=news["publish_time"],
                    author=news.get("author", "")
                )
                if result:
                    success_count += 1
            except Exception as e:
                print(f"批量插入新闻 {news.get('news_id')} 失败: {str(e)}")
                continue
        
        return success_count
    
    async def search_similar_news(self, query: str, category_id: Optional[int] = None, 
                                 top_k: int = 5) -> List[Dict[str, Any]]:
        """
        搜索相似新闻
        
        Args:
            query: 查询文本
            category_id: 可选的分类ID过滤
            top_k: 返回最相似的K条新闻
            
        Returns:
            相似新闻列表
        """
        try:
            # 确保已初始化
            if not self._initialized:
                self.initialize()
            
            # 生成查询向量
            query_embedding = await embedding_service.get_embedding(query)
            
            # 构建过滤器
            where_filter = None
            if category_id is not None:
                where_filter = {"category_id": category_id}
            
            # 执行搜索
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=where_filter,
                include=["metadatas", "distances"]
            )
            
            # 解析结果
            similar_news = []
            if results['ids'] and results['ids'][0]:
                for i, news_id in enumerate(results['ids'][0]):
                    metadata = results['metadatas'][0][i]
                    distance = results['distances'][0][i] if results['distances'] else 0
                    
                    similar_news.append({
                        "news_id": metadata.get("news_id"),
                        "category_id": metadata.get("category_id"),
                        "title": metadata.get("title"),
                        "content": metadata.get("content"),
                        "publish_time": metadata.get("publish_time"),
                        "author": metadata.get("author"),
                        "similarity_score": float(1 - distance)  # 转换为相似度分数
                    })
            
            return similar_news
            
        except Exception as e:
            print(f"搜索相似新闻失败: {str(e)}")
            return []
    
    def delete_news(self, news_id: int) -> bool:
        """
        删除指定新闻的向量
        
        Args:
            news_id: 新闻ID
            
        Returns:
            是否删除成功
        """
        try:
            self.collection.delete(ids=[f"news_{news_id}"])
            return True
        except Exception as e:
            print(f"删除新闻向量失败: {str(e)}")
            return False
    
    def clear_collection(self) -> bool:
        """
        清空整个集合
        
        Returns:
            是否清空成功
        """
        try:
            # 删除并重新创建集合
            self.client.delete_collection(name=self.collection_name)
            self._create_collection()
            return True
        except Exception as e:
            print(f"清空集合失败: {str(e)}")
            return False
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        获取集合统计信息
        
        Returns:
            统计信息字典
        """
        try:
            stats = {
                "collection_name": self.collection_name,
                "entity_count": self.collection.count(),
                "dimension": self.dimension
            }
            return stats
        except Exception as e:
            print(f"获取集合统计失败: {str(e)}")
            return {}


# 创建全局单例
vector_db_service = VectorDBService()
