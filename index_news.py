"""
新闻数据索引脚本
将 MySQL 数据库中的新闻数据导入到 ChromaDB 向量数据库
"""
import asyncio
import sys
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# 添加项目根目录到路径
sys.path.insert(0, '.')

from config.db_conf import ASYNC_DATABASE_URL, AsyncSessionLocal
from models.news import News
from services.chroma_service import vector_db_service


async def index_all_news():
    """
    将所有新闻从 MySQL 导入到向量数据库
    
    流程：
    1. 连接 MySQL 数据库
    2. 读取所有新闻数据
    3. 逐条生成向量并存储到 ChromaDB
    4. 统计导入结果
    """
    
    print("=" * 60)
    print("开始导入新闻数据到向量数据库")
    print("=" * 60)
    
    # 初始化向量数据库
    print("\n1. 初始化向量数据库...")
    vector_db_service.initialize()
    print(f"   ✓ 向量数据库就绪，集合: {vector_db_service.collection_name}")
    
    # 创建数据库连接
    print("\n2. 连接 MySQL 数据库...")
    print("   ✓ 数据库连接成功")
    
    # 读取所有新闻
    print("\n3. 读取新闻数据...")
    async with AsyncSessionLocal() as session:
        stmt = select(News)
        result = await session.execute(stmt)
        news_list = result.scalars().all()
        
        total_count = len(news_list)
        print(f"   ✓ 共找到 {total_count} 条新闻")
        
        if total_count == 0:
            print("\n⚠️  数据库中没有新闻数据，无需导入")
            return
        
        # 批量导入
        print("\n4. 开始向量化并导入...")
        success_count = 0
        failed_count = 0
        skipped_count = 0
        
        for i, news in enumerate(news_list, 1):
            try:
                # 检查是否已存在
                existing = vector_db_service.collection.get(
                    ids=[f"news_{news.id}"]
                )
                
                if existing and existing['ids']:
                    print(f"   [{i}/{total_count}] 跳过已存在的新闻 ID: {news.id}")
                    skipped_count += 1
                    continue
                
                # 准备文本内容（标题 + 内容）
                text = f"{news.title} {news.content[:500] if news.content else ''}"
                
                if not text.strip():
                    print(f"   [{i}/{total_count}] ⚠️  跳过空内容新闻 ID: {news.id}")
                    skipped_count += 1
                    continue
                
                # 插入到向量数据库
                success = await vector_db_service.insert_news(
                    news_id=news.id,
                    category_id=news.category_id,
                    title=news.title,
                    content=news.content or "",
                    publish_time=news.publish_time.strftime("%Y-%m-%d %H:%M:%S"),
                    author=news.author or ""
                )
                
                if success:
                    success_count += 1
                    print(f"   [{i}/{total_count}] ✓ 成功导入: {news.title[:30]}...")
                else:
                    failed_count += 1
                    print(f"   [{i}/{total_count}] ✗ 导入失败: {news.title[:30]}...")
                    
            except Exception as e:
                failed_count += 1
                print(f"   [{i}/{total_count}] ✗ 错误: {str(e)}")
    
    # 输出统计信息
    print("\n" + "=" * 60)
    print("导入完成！统计信息：")
    print("=" * 60)
    print(f"总新闻数:   {total_count}")
    print(f"成功导入:   {success_count}")
    print(f"跳过(已存在): {skipped_count}")
    print(f"失败:       {failed_count}")
    print(f"向量库总数: {vector_db_service.collection.count()}")
    print("=" * 60)
    
    if failed_count > 0:
        print("\n⚠️  有部分新闻导入失败，请检查错误信息")
        return 1
    else:
        print("\n🎉 所有新闻导入成功！")
        return 0


async def clear_and_reindex():
    """
    清空向量数据库并重新索引所有新闻
    用于完全重建索引
    """
    print("=" * 60)
    print("警告：这将清空向量数据库并重新索引！")
    print("=" * 60)
    
    response = input("\n确认操作？(yes/no): ")
    if response.lower() != 'yes':
        print("操作已取消")
        return
    
    # 清空集合
    print("\n清空向量数据库...")
    vector_db_service.initialize()
    vector_db_service.collection.delete(where={})
    print("✓ 向量数据库已清空")
    
    # 重新索引
    await index_all_news()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='新闻数据索引工具')
    parser.add_argument(
        '--clear',
        action='store_true',
        help='清空向量数据库并重新索引'
    )
    
    args = parser.parse_args()
    
    if args.clear:
        exit_code = asyncio.run(clear_and_reindex())
    else:
        exit_code = asyncio.run(index_all_news())
    
    sys.exit(exit_code)
