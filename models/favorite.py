from datetime import datetime

from sqlalchemy import DateTime, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now(),
        comment="创建时间"
    )

class Favorite(Base):
    __tablename__ = "favorite"
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="收藏ID"
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="用户ID"
    )
    news_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="新闻ID"
    )

