import json

import redis.asyncio as redis

REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0

# 创建异步 Redis 客户端连接实例
# 配置连接到本地 Redis 服务，启用自动解码响应为字符串
redis_client = redis.Redis(
    host=REDIS_HOST,  # Redis 服务器地址
    port=REDIS_PORT,  # Redis 端口号
    db=REDIS_DB,  # Redis 数据库索引
    decode_responses=True  # 自动解码响应为字符串
)

# 设置 和 读取 (字符串 和 列表或字典)

# 读取：字符串
async def get_cache(key):
    try:
        return await redis_client.get(key)
    except Exception as e:
        print(f"获取缓存失败: {e}")
        return None


# 读取：列表或字典
async def get_json_cache(key):
    try:
        data = await redis_client.get(key)
        if data:
            return json.loads(data)  # 序列化：将字符串数据转换成 Python 对象
        return None
    except Exception as e:
        print(f"获取 JSON 缓存失败: {e}")
        return None


# 设置缓存
async def set_cache(key: str, value: str, expire: int = 3600):
    try:
        if isinstance(value, dict) or isinstance(value, list):
            value = json.dumps(value, ensure_ascii=False)  # 反序列化：将 Python 对象转换成字符串, ensure_ascii=False 避免中文乱码
        await redis_client.setex(key, expire, value)
        return True
    except Exception as e:
        print(f"设置缓存失败: {e}")
        return False
