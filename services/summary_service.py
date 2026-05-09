"""
新闻摘要服务
使用阿里云通义千问生成新闻摘要
"""
import dashscope
from typing import Optional
from config.ai_conf import DASHSCOPE_API_KEY, DASHSCOPE_MODEL


class SummaryService:
    """新闻摘要服务类"""
    
    def __init__(self):
        """初始化摘要服务"""
        dashscope.api_key = DASHSCOPE_API_KEY
        self.model = DASHSCOPE_MODEL
    
    async def generate_summary(self, title: str, content: str, 
                              max_length: int = 200) -> Optional[str]:
        """
        生成新闻摘要
        
        Args:
            title: 新闻标题
            content: 新闻内容
            max_length: 摘要最大长度
            
        Returns:
            生成的摘要，失败返回 None
        """
        try:
            # 构建提示词
            prompt = f"""请为以下新闻生成一个简洁的摘要（不超过{max_length}字）：

标题：{title}

内容：{content[:1000]}

摘要："""

            # 调用通义千问 API
            response = dashscope.Generation.call(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的新闻摘要助手，擅长提取新闻的核心信息。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # 较低的温度，保证稳定性
                max_tokens=300
            )
            
            if response.status_code == 200:
                summary = response.output.text.strip()
                return summary
            else:
                print(f"生成摘要失败: {response.message}")
                return None
                
        except Exception as e:
            print(f"生成摘要异常: {str(e)}")
            return None
    
    async def generate_quick_summary(self, text: str, 
                                    max_length: int = 100) -> Optional[str]:
        """
        快速生成短文本摘要（用于实时场景）
        
        Args:
            text: 需要摘要的文本
            max_length: 摘要最大长度
            
        Returns:
            生成的摘要，失败返回 None
        """
        try:
            prompt = f"""请用一句话总结以下内容（不超过{max_length}字）：

{text[:800]}

总结："""

            response = dashscope.Generation.call(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=150
            )
            
            if response.status_code == 200:
                summary = response.output.text.strip()
                return summary
            else:
                return None
                
        except Exception as e:
            print(f"快速生成摘要异常: {str(e)}")
            return None


# 创建全局单例
summary_service = SummaryService()
