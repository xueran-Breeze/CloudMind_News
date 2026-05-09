import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 阿里云百炼平台配置
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "sk-d2a1695f50f243c8ae58e7f2b0fd08b4")
DASHSCOPE_API_URL = os.getenv("DASHSCOPE_API_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions")
DASHSCOPE_MODEL = os.getenv("DASHSCOPE_MODEL", "qwen3.6-flash")
DASHSCOPE_EMBEDDING_MODEL = os.getenv("DASHSCOPE_EMBEDDING_MODEL", "text-embedding-v3")

# Tavily 搜索 API 配置
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")

# Chroma 配置
CHROMA_DATA_PATH = os.getenv("CHROMA_DATA_PATH", "./chroma_data")
CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "news_embeddings")

# Redis 配置
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))

# AI Agent 配置
CONVERSATION_TTL = int(os.getenv("CONVERSATION_TTL", "86400"))  # 24小时
MAX_HISTORY_ROUNDS = int(os.getenv("MAX_HISTORY_ROUNDS", "10"))  # 最多10轮对话
NEWS_CACHE_TTL = int(os.getenv("NEWS_CACHE_TTL", "600"))  # 新闻列表缓存10分钟
DETAIL_CACHE_TTL = int(os.getenv("DETAIL_CACHE_TTL", "1800"))  # 新闻详情缓存30分钟
