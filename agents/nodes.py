"""
LangGraph 节点函数
定义 Agent 工作流中的各个节点
"""
import json
from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from dashscope import Generation
from config.ai_conf import DASHSCOPE_API_KEY, DASHSCOPE_MODEL

from agents.state import AgentState, QuestionRouterOutput
from agents.tools import SearchTool, KnowledgeRetrievalTool, DateTimeTool


# 初始化 LLM
def get_llm():
    """获取 LLM 实例"""
    return {
        "api_key": DASHSCOPE_API_KEY,
        "model": DASHSCOPE_MODEL
    }


async def router_node(state: AgentState) -> Dict[str, Any]:
    """
    路由节点：判断问题类型
    
    根据用户问题判断应该使用哪种工具：
    - realtime: 需要实时信息，使用联网搜索
    - knowledge: 查询本地知识库
    - chat: 普通闲聊，直接回答
    """
    try:
        # 构建提示词
        prompt = f"""你是一个智能问题分类器。请分析用户的问题，判断它属于哪种类型：

问题类型定义：
1. realtime（实时新闻）：询问最新的新闻、时事、最近发生的事件、当前情况等
2. knowledge（本地知识）：询问历史新闻、特定主题的新闻、数据库中的信息、过去的事件等
3. chat（闲聊）：问候、感谢、日常对话、与新闻无关的聊天等

用户问题：{state.user_input}

对话历史：
{json.dumps(state.chat_history[-3:], ensure_ascii=False) if state.chat_history else "无"}

请以 JSON 格式输出，包含两个字段：
- question_type: "realtime"、"knowledge" 或 "chat"
- reasoning: 简短说明判断理由

只输出 JSON，不要其他内容。"""

        # 调用通义千问 API
        response = Generation.call(
            model=DASHSCOPE_MODEL,
            messages=[
                {"role": "system", "content": "你是一个专业的问题分类助手。"},
                {"role": "user", "content": prompt}
            ],
            result_format='message'
        )
        
        if response.status_code == 200:
            content = response.output.choices[0].message.content
            
            # 尝试解析 JSON
            try:
                # 清理可能的 markdown 标记
                content = content.strip()
                if content.startswith("```json"):
                    content = content[7:]
                if content.endswith("```"):
                    content = content[:-3]
                
                result = json.loads(content)
                question_type = result.get("question_type", "chat")
                
                # 验证类型
                if question_type not in ["realtime", "knowledge", "chat"]:
                    question_type = "chat"
                
                return {
                    "question_type": question_type
                }
            except json.JSONDecodeError:
                # 如果解析失败，默认为 chat
                return {"question_type": "chat"}
        else:
            print(f"路由节点 API 调用失败: {response.message}")
            return {"question_type": "chat"}
            
    except Exception as e:
        print(f"路由节点错误: {str(e)}")
        return {"question_type": "chat"}


async def search_node(state: AgentState) -> Dict[str, Any]:
    """
    搜索节点：执行联网搜索
    
    当问题类型为 realtime 时调用此节点
    """
    try:
        print(f"执行联网搜索: {state.user_input}")
        
        # 执行搜索
        results = await SearchTool.execute(
            query=state.user_input,
            max_results=5
        )
        
        return {
            "search_results": results
        }
        
    except Exception as e:
        print(f"搜索节点错误: {str(e)}")
        return {
            "search_results": [],
            "error": f"搜索失败: {str(e)}"
        }


async def retrieve_node(state: AgentState) -> Dict[str, Any]:
    """
    检索节点：从本地知识库检索
    
    当问题类型为 knowledge 时调用此节点
    """
    try:
        print(f"执行知识库检索: {state.user_input}")
        
        # 执行检索
        results = await KnowledgeRetrievalTool.execute(
            query=state.user_input,
            top_k=5
        )
        
        return {
            "retrieval_results": results
        }
        
    except Exception as e:
        print(f"检索节点错误: {str(e)}")
        return {
            "retrieval_results": [],
            "error": f"检索失败: {str(e)}"
        }


async def context_builder_node(state: AgentState) -> Dict[str, Any]:
    """
    上下文构建节点：整合搜索结果和检索结果
    
    将搜索/检索结果整理成 LLM 可以理解的上下文格式
    """
    try:
        context_parts = []
        sources = []
        
        # 处理联网搜索结果
        if state.search_results:
            context_parts.append("【联网搜索结果】")
            for i, result in enumerate(state.search_results, 1):
                context_parts.append(f"{i}. {result.get('title', '无标题')}")
                context_parts.append(f"   内容: {result.get('content', '')[:300]}")
                if result.get('url'):
                    context_parts.append(f"   来源: {result['url']}")
                context_parts.append("")
                
                sources.append({
                    "type": "web",
                    "title": result.get("title", ""),
                    "url": result.get("url", "")
                })
        
        # 处理本地检索结果
        if state.retrieval_results:
            context_parts.append("【本地知识库检索结果】")
            for i, result in enumerate(state.retrieval_results, 1):
                context_parts.append(f"{i}. {result.get('title', '无标题')}")
                context_parts.append(f"   内容: {result.get('content', '')[:300]}")
                context_parts.append(f"   发布时间: {result.get('publish_time', '未知')}")
                context_parts.append(f"   来源: 本地数据库 (ID: {result.get('id', 'N/A')})")
                context_parts.append("")
                
                sources.append({
                    "type": "local",
                    "title": result.get("title", ""),
                    "id": str(result.get("id", ""))  # 转换为字符串
                })
        
        # 整合上下文
        context = "\n".join(context_parts) if context_parts else "无额外信息"
        
        return {
            "context": context,
            "sources": sources
        }
        
    except Exception as e:
        print(f"上下文构建节点错误: {str(e)}")
        return {
            "context": "",
            "sources": [],
            "error": f"上下文构建失败: {str(e)}"
        }


async def generate_answer_node(state: AgentState) -> Dict[str, Any]:
    """
    答案生成节点：基于上下文生成最终答案
    
    使用 LLM 结合上下文和对话历史生成回答
    """
    try:
        # 构建系统提示词
        system_prompt = """你是一个专业的新闻AI助手。你的任务是基于提供的信息回答用户的问题。

回答规则：
1. 如果有提供【联网搜索结果】或【本地知识库检索结果】，请基于这些信息回答问题
2. 如果没有相关信息，可以用自己的知识回答，但要说明
3. **必须在回答末尾标注信息来源**：
   - 来自网络搜索：标注"来源：[标题](URL)"
   - 来自本地知识库：标注"来源：本地数据库 - [标题]"
   - 如果是常识性回答：标注"来源：AI助手常识"
4. 保持回答简洁、准确、客观
5. 如果信息不足，诚实地告诉用户
6. 使用中文回答"""

        # 构建用户消息
        user_message = f"""对话历史：
{json.dumps(state.chat_history[-5:], ensure_ascii=False, indent=2) if state.chat_history else "无"}

当前问题：{state.user_input}

参考信息：
{state.context}

请基于以上信息回答问题，记得标注来源。"""

        # 调用通义千问 API
        response = Generation.call(
            model=DASHSCOPE_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            result_format='message'
        )
        
        if response.status_code == 200:
            answer = response.output.choices[0].message.content
            return {"answer": answer}
        else:
            print(f"答案生成 API 调用失败: {response.message}")
            return {
                "answer": "抱歉，我暂时无法生成回答，请稍后再试。",
                "error": f"API 调用失败: {response.message}"
            }
            
    except Exception as e:
        print(f"答案生成节点错误: {str(e)}")
        return {
            "answer": "抱歉，发生了错误，请稍后再试。",
            "error": str(e)
        }


# 导出所有节点函数
__all__ = [
    "router_node",
    "search_node", 
    "retrieve_node",
    "context_builder_node",
    "generate_answer_node"
]
