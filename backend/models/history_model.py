from sqlalchemy import Column, Integer, String

from utils.db_utils import Base

class History(Base):
    __tablename__ = 'history'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=False)
    chat_name = Column(String, nullable=False)
