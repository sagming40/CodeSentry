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
    
    # ↓↓↓ 신규 추가 — "이 함수가 파일의 몇 번째 줄 ~ 몇 번째 줄인지" 주소값
    # 비유: function_name만 있는 건 "홍길동"이라는 이름만 아는 것이고,
    # line_number/end_line_number까지 있어야 "몇 동 몇 호 사는 홍길동"인지 정확히 특정됨
    # (동명이인 있어도 헷갈릴 일이 없어짐)
    line_number = Column(Integer, nullable=True)       # 함수 시작 줄
    end_line_number = Column(Integer, nullable=True)   # 함수 끝나는 줄
    
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
    
    # ↓↓↓ Task 3-1 신규 추가분 ↓↓↓
    content = Column(String, nullable=True)                      # test_code 또는 fix_diff — 서랍(actions) 안에 넣을 "실제 결과물"
    detail = Column(String, nullable=True)                       # covered_cases 또는 fix_explanation — 결과물에 붙는 "설명 라벨"
    # nullable=True인 이유: assess_risk 단계(attempt_number=1의 판단 row)에는 아직 생성물이 없으니까
    
    # ↓↓↓ Task 3-2 신규 추가분 ↓↓↓
    # 비유: content가 "만든 요리"라면 execution_status는 "손님이 먹어보고 합격/불합격 도장 찍은 것"
    # pending: 아직 샌드박스에서 실행 안 해봄 / passed: 통과 / failed: 실패
    # (propose_fix는 샌드박스 실행 자체를 안 거치니까 이 값이 계속 None으로 남음 — 그게 정상)
    execution_status = Column(String, nullable=True)
       
    created_at = Column(DateTime, default=datetime.utcnow) 
    
    finding = relationship("Finding", back_populates="actions")      
