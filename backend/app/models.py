import enum
import uuid
from datetime import datetime

from sqlalchemy import Column, String, Text, DateTime, Enum, Float
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from app.database import Base


def gen_uuid():
    return str(uuid.uuid4())


class ComplaintStatus(str, enum.Enum):
    pending_triage = "Pending Triage"
    under_review = "Under Review"
    capa_initiated = "CAPA Initiated"
    closed = "Closed"


class Severity(str, enum.Enum):
    critical = "Critical"
    major = "Major"
    minor = "Minor"


class Priority(str, enum.Enum):
    high = "High"
    medium = "Medium"
    low = "Low"


class Complaint(Base):
    """
    Mirrors the four sections of the 'Log Customer Complaint' form:
    1. Origin & Customer Details
    2. Product & Batch Identification
    3. Complaint Details
    4. Initial Assessment & Priority

    Fields are nullable because the AI Copilot fills them in incrementally
    as it extracts information from the uploaded document / pasted text -
    the same "Awaiting AI extraction..." -> populated flow shown in the UI.
    """
    __tablename__ = "complaints"

    id = Column(String(36), primary_key=True, default=gen_uuid)

    # 1. Origin & Customer Details
    complaint_source = Column(String(120), nullable=True)   # e.g. Email, Phone, Portal
    customer_name = Column(String(200), nullable=True)

    # 2. Product & Batch Identification
    product_name = Column(String(200), nullable=True)
    product_strength_grade = Column(String(120), nullable=True)
    batch_lot_number = Column(String(120), nullable=True)
    manufacturing_date = Column(String(30), nullable=True)  # stored as ISO string for simplicity
    expiry_date = Column(String(30), nullable=True)
    quantity_affected = Column(Float, nullable=True)
    quantity_unit = Column(String(20), default="kg")

    # 3. Complaint Details
    complaint_type = Column(String(120), nullable=True)     # e.g. Contamination, Packaging, OOS
    complaint_date = Column(String(30), nullable=True)
    detailed_description = Column(Text, nullable=True)

    # 4. Initial Assessment & Priority (AI Copilot Risk Assessment)
    initial_severity = Column(Enum(Severity), nullable=True)
    priority = Column(Enum(Priority), nullable=True)

    # Bookkeeping
    status = Column(Enum(ComplaintStatus), default=ComplaintStatus.pending_triage)
    source_document_name = Column(String(255), nullable=True)
    raw_extracted_text = Column(Text, nullable=True)

    # Bonus AI features - stored so the frontend can render them without recomputation
    ai_completeness_score = Column(Float, nullable=True)     # 0-100
    ai_missing_fields = Column(Text, nullable=True)           # comma-separated
    ai_summary = Column(Text, nullable=True)
    ai_root_cause_suggestion = Column(Text, nullable=True)
    ai_capa_recommendation = Column(Text, nullable=True)
    ai_duplicate_of = Column(String(36), nullable=True)       # id of a likely duplicate complaint
    ai_duplicate_confidence = Column(Float, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
