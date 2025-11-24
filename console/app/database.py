from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func # <-- PENTING: Import func untuk waktu
from datetime import datetime # Tetap diimpor jika masih digunakan di tempat lain
import json
from app.config import settings

DATABASE_URL = settings.DATABASE_URL

# Hapus connect_args={"check_same_thread": False} karena ini untuk SQLite
engine = create_engine(DATABASE_URL) 
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# === Database Models ===
class UserDB(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True)
    name = Column(String)
    email = Column(String)
    payment_authorized = Column(Boolean, default=False)
    # Gunakan func.now() untuk timestamp yang benar
    created_at = Column(DateTime, default=func.now())

class PlanDB(Base):
    __tablename__ = "plans"
    id = Column(String, primary_key=True)
    user_id = Column(String)
    status = Column(String, default="draft")
    destination = Column(String)
    start_date = Column(String)
    end_date = Column(String)
    budget_idr = Column(Integer)
    itinerary_json = Column(Text)  # JSON string
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class BookingDB(Base):
    __tablename__ = "bookings"
    id = Column(String, primary_key=True)
    plan_id = Column(String)
    user_id = Column(String)
    booking_type = Column(String)
    provider_ref = Column(String)
    status = Column(String, default="pending")
    amount_idr = Column(Integer)
    details_json = Column(Text)
    created_at = Column(DateTime, default=func.now())

class AuditLogDB(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=func.now())
    user_id = Column(String)
    action = Column(String)
    details = Column(Text)
    ip_address = Column(String, nullable=True)

# Create tables
def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()