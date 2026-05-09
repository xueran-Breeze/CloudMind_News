"""
Agent 状态定义
定义 LangGraph 工作流中传递的状态结构
"""
from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field


class AgentState(BaseModel):
    """
    Agent 工作流的状态
    
    Attributes:
        session_id: 会话ID，用于追踪对话历史
        user_input: 用户当前输入的问题
        chat_history: 对话历史记录
        question_type: 问题类型分类结果
        search_results: 联网搜索结果
        retrieval_results: 本地知识库检索结果
        context: 整合后的上下文信息
        answer: AI生成的最终答案
        sources: 信息来源列表
        error: 错误信息（如果有）
    """
    
    # 会话信息
    session_id: str = Field(..., description="会话ID")
    user_input: str = Field(..., description="用户当前输入")
    chat_history: List[Dict[str, str]] = Field(default_factory=list, description="对话历史")
    
    # 路由决策
    question_type: Optional[Literal["realtime", "knowledge", "chat"]] = Field(
        None, 
        description="问题类型：realtime(实时新闻), knowledge(本地知识), chat(闲聊)"
    )
    
    # 检索结果
    search_results: List[Dict[str, Any]] = Field(default_factory=list, description="联网搜索结果")
    retrieval_results: List[Dict[str, Any]] = Field(default_factory=list, description="本地检索结果")
    
    # 上下文和答案
    context: str = Field("", description="整合后的上下文")
    answer: str = Field("", description="AI生成的答案")
    sources: List[Dict[str, str]] = Field(default_factory=list, description="信息来源")
    
    # 错误处理
    error: Optional[str] = Field(None, description="错误信息")
    
    class Config:
        arbitrary_types_allowed = True


class QuestionRouterOutput(BaseModel):
    """
    问题路由器的输出
    
    Attributes:
        question_type: 问题类型
        reasoning: 判断理由
    """
    question_type: Literal["realtime", "knowledge", "chat"] = Field(
        ..., 
        description="问题类型"
    )
    reasoning: str = Field(..., description="判断理由")


class SearchResult(BaseModel):
    """
    搜索结果结构
    
    Attributes:
        title: 标题
        content: 内容
        url: 来源URL
        source: 来源类型
        score: 相关性分数
    """
    title: str = Field(..., description="标题")
    content: str = Field(..., description="内容")
    url: str = Field("", description="来源URL")
    source: str = Field(..., description="来源类型：tavily_search 或 local_knowledge")
    score: float = Field(0.0, description="相关性分数")


# 导出供其他模块使用
__all__ = ["AgentState", "QuestionRouterOutput", "SearchResult"]
