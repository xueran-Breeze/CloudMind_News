"""
阿里云通义 Embedding 服务
用于将文本转换为向量表示
"""
import dashscope
from typing import List, Union
from config.ai_conf import DASHSCOPE_API_KEY, DASHSCOPE_EMBEDDING_MODEL


class EmbeddingService:
    """阿里云通义 Embedding 服务类"""
    
    def __init__(self):
        """初始化 Embedding 服务"""
        dashscope.api_key = DASHSCOPE_API_KEY
        self.model = DASHSCOPE_EMBEDDING_MODEL
    
    async def get_embedding(self, text: str) -> List[float]:
        """
        获取单个文本的向量嵌入
        
        Args:
            text: 需要转换的文本
            
        Returns:
            向量列表，例如 [0.1, 0.2, 0.3, ...]
        """
        if not text or not text.strip():
            raise ValueError("文本不能为空")
        
        try:
            response = dashscope.TextEmbedding.call(
                model=self.model,
                input=text
            )
            
            if response.status_code == 200:
                # 修复：直接使用字典访问
                embedding = response.output['embeddings'][0]['embedding']
                return embedding
            else:
                raise Exception(f"Embedding API 调用失败: {response.message}")
        except Exception as e:
            raise Exception(f"获取向量嵌入失败: {str(e)}")
    
    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        批量获取文本的向量嵌入
        
        Args:
            texts: 文本列表
            
        Returns:
            向量列表的列表，例如 [[0.1, 0.2], [0.3, 0.4], ...]
        """
        if not texts:
            return []
        
        # 过滤空文本
        valid_texts = [text for text in texts if text and text.strip()]
        if not valid_texts:
            return []
        
        try:
            response = dashscope.TextEmbedding.call(
                model=self.model,
                input=valid_texts
            )
            
            if response.status_code == 200:
                # 修复：使用字典访问
                embeddings = [item['embedding'] for item in response.output['embeddings']]
                return embeddings
            else:
                raise Exception(f"批量 Embedding API 调用失败: {response.message}")
        except Exception as e:
            raise Exception(f"批量获取向量嵌入失败: {str(e)}")
    
    def get_embedding_dimension(self) -> int:
        """
        获取向量维度
        
        Returns:
            向量维度，text-embedding-v3 是 1536 维
        """
        # text-embedding-v3 的维度是 1536
        if "v3" in self.model.lower():
            return 1536
        elif "v2" in self.model.lower():
            return 768
        else:
            # 默认返回 1536
            return 1536


# 创建全局单例
embedding_service = EmbeddingService()
