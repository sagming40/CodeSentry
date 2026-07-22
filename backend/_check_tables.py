# backend/_check_tables.py
# 임시 검증용 — 커밋 제외 대상

from sqlalchemy import inspect
from backend.database import engine, Base
from backend import models  # noqa: F401 — 모델 클래스들을 이 시점에 등록시키기 위한 import

Base.metadata.create_all(bind=engine)

inspector = inspect(engine)
print("현재 codesentry.db에 있는 테이블들:")
for table_name in inspector.get_table_names():
    print(" -", table_name)
