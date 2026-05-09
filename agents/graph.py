"""
LangGraph Agent 主图
构建完整的 Agent 工作流
"""
from typing import Literal
from langgraph.graph import StateGraph, END
from agents.state import AgentState
from agents.nodes import (
    router_node,
    search_node,
    retrieve_node,
    context_builder_node,
    generate_answer_node
)


def route_question(state: AgentState) -> Literal["search", "retrieve", "generate"]:
    """
    路由函数：根据问题类型决定下一步
    
    Returns:
        "search": 执行联网搜索
        "retrieve": 执行知识库检索
        "generate": 直接生成答案（闲聊）
    """
    if state.question_type == "realtime":
        return "search"
    elif state.question_type == "knowledge":
        return "retrieve"
    else:  # chat
        return "generate"


def build_agent_graph():
    """
    构建 Agent 工作流图
    
    工作流程：
    1. Router Node - 判断问题类型
    2. 根据类型分支：
       - realtime -> Search Node
       - knowledge -> Retrieve Node
       - chat -> 直接到 Generate Node
    3. Search/Retrieve -> Context Builder Node
    4. Context Builder -> Generate Answer Node
    5. Generate Answer -> END
    """
    
    # 创建状态图
    workflow = StateGraph(AgentState)
    
    # 添加节点
    workflow.add_node("router", router_node)
    workflow.add_node("search", search_node)
    workflow.add_node("retrieve", retrieve_node)
    workflow.add_node("context_builder", context_builder_node)
    workflow.add_node("generate", generate_answer_node)
    
    # 设置入口点
    workflow.set_entry_point("router")
    
    # 添加条件边（路由决策）
    workflow.add_conditional_edges(
        "router",
        route_question,
        {
            "search": "search",
            "retrieve": "retrieve",
            "generate": "generate"
        }
    )
    
    # 搜索和检索后都进入上下文构建
    workflow.add_edge("search", "context_builder")
    workflow.add_edge("retrieve", "context_builder")
    
    # 上下文构建后生成答案
    workflow.add_edge("context_builder", "generate")
    
    # 生成答案后结束
    workflow.add_edge("generate", END)
    
    # 编译图
    graph = workflow.compile()
    
    return graph


# 创建全局单例
agent_graph = build_agent_graph()


async def run_agent(session_id: str, user_input: str, chat_history: list = None) -> dict:
    """
    运行 Agent 的便捷函数
    
    Args:
        session_id: 会话ID
        user_input: 用户输入
        chat_history: 对话历史
        
    Returns:
        AgentState 字典
    """
    # 初始化状态
    initial_state = AgentState(
        session_id=session_id,
        user_input=user_input,
        chat_history=chat_history or []
    )
    
    # 运行图
    result = await agent_graph.ainvoke(initial_state)
    
    return result


# 导出
__all__ = ["agent_graph", "run_agent"]
