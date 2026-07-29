from typing import Optional, List
from pydantic import BaseModel


class ComplaintFieldsExtracted(BaseModel):
    """
    What the LangGraph extraction node produces. Every field is Optional
    because the LLM may not find every value in a given document - the
    frontend renders unresolved fields as "Awaiting AI extraction...".
    """
    complaint_source: Optional[str] = None
    customer_name: Optional[str] = None

    product_name: Optional[str] = None
    product_strength_grade: Optional[str] = None
    batch_lot_number: Optional[str] = None
    manufacturing_date: Optional[str] = None
    expiry_date: Optional[str] = None
    quantity_affected: Optional[float] = None
    quantity_unit: Optional[str] = None

    complaint_type: Optional[str] = None
    complaint_date: Optional[str] = None
    detailed_description: Optional[str] = None

    initial_severity: Optional[str] = None
    priority: Optional[str] = None


class AIAnalysis(BaseModel):
    completeness_score: Optional[float] = None
    missing_fields: List[str] = []
    summary: Optional[str] = None
    root_cause_suggestion: Optional[str] = None
    capa_recommendation: Optional[str] = None
    duplicate_of: Optional[str] = None
    duplicate_confidence: Optional[float] = None


class IngestResponse(BaseModel):
    complaint_id: str
    extracted: ComplaintFieldsExtracted
    analysis: AIAnalysis
    assistant_message: str


class ChatRequest(BaseModel):
    complaint_id: str
    message: str


class ChatResponse(BaseModel):
    reply: str
    updated_fields: Optional[ComplaintFieldsExtracted] = None


class ComplaintOut(ComplaintFieldsExtracted):
    id: str
    status: str
    source_document_name: Optional[str] = None
    ai_completeness_score: Optional[float] = None
    ai_summary: Optional[str] = None

    class Config:
        from_attributes = True
