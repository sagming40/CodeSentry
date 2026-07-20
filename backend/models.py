# backend/models.py

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base

class Scan(Base):
    __tablename__ = "scans"
    
    id = Column(Integer, primary_key=True)
    repo_path = Column(String, nullable=False)
    status = Column(String, default="running")
    started_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)
    total_files_scanned = Column(Integer, default=0)
    
    findings = relationship("Finding", back_populates="scan")

class Finding(Base):
    __tablename__ = "findings"
    
    id = Column(Integer, primary_key=True)
    scan_id = Column(Integer, ForeignKey("scans.id"))
    file_path = Column(String, nullable=False)
    function_name = Column(String, nullable=False)
    complexity_score = Column(Integer, nullable=False)
    has_test = Column(Boolean, default=False)
    status = Column(String, default="found")
    
    scan = relationship("Scan", back_populates="findings")    
