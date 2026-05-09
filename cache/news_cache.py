# 新闻相关的缓存方法：新闻分类、新闻列表、新闻详情的读入和写入
from typing import List, Dict, Any

from config.cache_conf import get_json_cache, set_cache

#key - value
CATEGORIES_KEY = "news:categories"
NEWS_LIST_KEY_PREFIX = "news:list:"  # 新闻列表缓存key前缀，后面拼接 category_id
NEWS_DETAIL_KEY_PREFIX = "news:detail:"  # 新闻详情缓存key前缀，后面拼接 news_id

#获取新闻分类缓存
async def get_cached_categories():
    return await get_json_cache(CATEGORIES_KEY)

#写入新闻分类缓存：缓存的数据，过期时间
#分类、配置：7200 列表：600 详情：1800 验证码：120 --数据越稳定，缓存越持久
async def set_cache_categories(
        data: List[Dict[str, Any]],
        expire: int = 7200
):
    return await set_cache(CATEGORIES_KEY, data, expire)


# 获取新闻列表缓存
async def get_cached_news_list(category_id: int, page: int, page_size: int):
    key = f"{NEWS_LIST_KEY_PREFIX}{category_id}:{page}:{page_size}"
    return await get_json_cache(key)


# 写入新闻列表缓存
async def set_cache_news_list(
        category_id: int,
        page: int,
        page_size: int,
        data: List[Dict[str, Any]],
        expire: int = 600  # 新闻列表缓存10分钟
):
    key = f"{NEWS_LIST_KEY_PREFIX}{category_id}:{page}:{page_size}"
    return await set_cache(key, data, expire)


# 获取新闻详情缓存
async def get_cached_news_detail(news_id: int):
    key = f"{NEWS_DETAIL_KEY_PREFIX}{news_id}"
    return await get_json_cache(key)


# 写入新闻详情缓存
async def set_cache_news_detail(
        news_id: int,
        data: Dict[str, Any],
        expire: int = 1800  # 新闻详情缓存30分钟
):
    key = f"{NEWS_DETAIL_KEY_PREFIX}{news_id}"
    return await set_cache(key, data, expire)

