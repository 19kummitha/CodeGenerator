# database.py
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

DATABASE_URL = "sqlite:///./history.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

class OutputHistory(Base):
    __tablename__ = "output_history"

    id = Column(Integer, primary_key=True, index=True)
    mode = Column(String(50))  # "SQL" or "Code"
    language = Column(String(50), nullable=True)
    question = Column(Text)
    schema = Column(Text, nullable=True)
    response = Column(Text)
    explanation = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)
