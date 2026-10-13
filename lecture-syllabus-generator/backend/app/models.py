from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean,
    DateTime, ForeignKey, JSON,
)
from sqlalchemy.orm import relationship
from app.db import Base


class Task(Base):
    __tablename__ = "task"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), default="未命名任务")
    status = Column(String(32), default="pending")  # pending/running/success/failed/partial
    page_count = Column(Integer, default=0)
    error_msg = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    pages = relationship("Page", back_populates="task", cascade="all, delete-orphan")
    knowledge_points = relationship("KnowledgePoint", back_populates="task", cascade="all, delete-orphan")
    outlines = relationship("Outline", back_populates="task", cascade="all, delete-orphan")
    export_logs = relationship("ExportLog", back_populates="task", cascade="all, delete-orphan")


class Page(Base):
    __tablename__ = "page"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("task.id"), nullable=False, index=True)
    page_no = Column(Integer, nullable=False)  # 逻辑页码
    filename = Column(String(512), nullable=False)
    file_path = Column(String(512), nullable=False)
    confidence = Column(Float, default=0.0)
    low_confidence_flag = Column(Boolean, default=False)
    failed_flag = Column(Boolean, default=False)
    recognized_text = Column(Text, nullable=True)
    error_msg = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    task = relationship("Task", back_populates="pages")


class KnowledgePoint(Base):
    __tablename__ = "knowledge_point"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("task.id"), nullable=False, index=True)
    page_id = Column(Integer, ForeignKey("page.id"), nullable=False)
    content = Column(Text, nullable=False)
    kp_type = Column(String(64), default="concept")  # concept/conclusion/method/example
    source_type = Column(String(32), default="课堂原话")  # 课堂原话 / AI推断
    source_pages = Column(String(128), nullable=False)  # 如 "P1" 或 "P1,P2"
    dedup_key = Column(String(256), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    task = relationship("Task", back_populates="knowledge_points")


class Outline(Base):
    __tablename__ = "outline"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("task.id"), nullable=False, index=True)
    markdown = Column(Text, nullable=False)
    version = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    task = relationship("Task", back_populates="outlines")
    nodes = relationship("OutlineNode", back_populates="outline", cascade="all, delete-orphan")


class OutlineNode(Base):
    __tablename__ = "outline_node"

    id = Column(Integer, primary_key=True, index=True)
    outline_id = Column(Integer, ForeignKey("outline.id"), nullable=False, index=True)
    level = Column(Integer, nullable=False)  # 1=模块, 2=知识点
    title = Column(String(512), nullable=False)
    content = Column(Text, nullable=True)
    source_type = Column(String(32), nullable=True)
    source_pages = Column(String(128), nullable=True)
    parent_id = Column(Integer, ForeignKey("outline_node.id"), nullable=True)
    sort_order = Column(Integer, default=0)

    outline = relationship("Outline", back_populates="nodes")
    children = relationship("OutlineNode", cascade="all, delete-orphan")


class ExportLog(Base):
    __tablename__ = "export_log"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("task.id"), nullable=False, index=True)
    file_size = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    task = relationship("Task", back_populates="export_logs")