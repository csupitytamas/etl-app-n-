from sqlalchemy import Column, Integer, String, JSON, DateTime
from datetime import datetime
from src.db.connection import Base

class APISchema(Base):
    __tablename__ = "api_schemas"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String, unique=True, nullable=False)
    field_mappings = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)