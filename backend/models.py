# backend/models.py

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float
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
    llm_calls = relationship("LlmCall", back_populates="finding")
    actions = relationship("Action", back_populates="finding")  
    
class LlmCall(Base):
    __tablename__ = "llm_calls"
    
    id = Column(Integer, primary_key=True)
    finding_id = Column(Integer, ForeignKey("findings.id"))
    tool_name = Column(String, nullable=False)                   # "assess_risk" / "generate_test" / "propose_fix" 
    input_tokens = Column(Integer, nullable=False)
    output_tokens = Column(Integer, nullable=False)
    estimated_cost_usd = Column(Float, nullable=False)
    called_at = Column(DateTime, default=datetime.utcnow)
    
    finding = relationship("Finding", back_populates="llm_calls")   
    
class Action(Base):
    __tablename__ = "actions"
    
    id = Column(Integer, primary_key=True)
    finding_id = Column(Integer, ForeignKey("findings.id"))
    raw_action_type = Column(String, nullable=False)             # 모델이 원래 고른 값
    final_action_type = Column(String, nullable=False)           # override 반영한 최종 값
    risk_reason = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    escalation_source = Column(String, nullable=True)            # "model_choice" / "confidence_override" / None
    attempt_number = Column(Integer, default=1)                  # 재시도 횟수 추적 (EPIC 3에서 씀)
    created_at = Column(DateTime, default=datetime.utcnow) 
    
    finding = relationship("Finding", back_populates="actions")      
