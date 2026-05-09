from datetime import datetime

from sqlalchemy import Integer, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass

class History(Base):
    __tablename__ = "history"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, autoincrement=False, nullable=False)
    news_id: Mapped[int] = mapped_column(Integer, autoincrement=False, nullable=False)
    view_time:Mapped[datetime]=mapped_column(DateTime, default=datetime.now)