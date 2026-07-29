from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.utils.document_parser import extract_text
from app.agents.graph import intake_graph
from app.agents.groq_client import call_groq_text
from app.config import settings

router = APIRouter(prefix="/api/ai", tags=["ai"])


def _run_intake_graph(db: Session, raw_text: str, source_document_name: str | None) -> schemas.IngestResponse:
    # Give the graph a lightweight view of existing complaints for duplicate detection
    existing = [
        {
            "id": c.id,
            "product_name": c.product_name,
            "batch_lot_number": c.batch_lot_number,
            "complaint_type": c.complaint_type,
        }
        for c in db.query(models.Complaint).limit(50).all()
    ]

    result = intake_graph.invoke({"raw_text": raw_text, "existing_complaints": existing})
    extracted = result.get("extracted_fields", {}) or {}

    # Persist a new complaint row pre-filled with everything the graph produced
    complaint = models.Complaint(
        source_document_name=source_document_name,
        raw_extracted_text=raw_text,
        ai_completeness_score=result.get("completeness_score"),
        ai_missing_fields=",".join(result.get("missing_fields", [])),
        ai_summary=result.get("summary"),
        ai_root_cause_suggestion=result.get("root_cause_suggestion"),
        ai_capa_recommendation=result.get("capa_recommendation"),
        ai_duplicate_of=result.get("duplicate_of"),
        ai_duplicate_confidence=result.get("duplicate_confidence"),
        initial_severity=result.get("severity"),
        priority=result.get("priority"),
        **{k: v for k, v in extracted.items() if k not in ("initial_severity", "priority")},
    )
    db.add(complaint)
    db.commit()
    db.refresh(complaint)

    return schemas.IngestResponse(
        complaint_id=complaint.id,
        extracted=schemas.ComplaintFieldsExtracted(**extracted),
        analysis=schemas.AIAnalysis(
            completeness_score=result.get("completeness_score"),
            missing_fields=result.get("missing_fields", []),
            summary=result.get("summary"),
            root_cause_suggestion=result.get("root_cause_suggestion"),
            capa_recommendation=result.get("capa_recommendation"),
            duplicate_of=result.get("duplicate_of"),
            duplicate_confidence=result.get("duplicate_confidence"),
        ),
        assistant_message=result.get("assistant_message", ""),
    )


@router.post("/ingest/document", response_model=schemas.IngestResponse)
async def ingest_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Drag & drop path - PDF / DOCX / TXT / EML."""
    file_bytes = await file.read()
    raw_text = extract_text(file.filename, file_bytes)
    return _run_intake_graph(db, raw_text, source_document_name=file.filename)


@router.post("/ingest/text", response_model=schemas.IngestResponse)
async def ingest_text(text: str = Form(...), db: Session = Depends(get_db)):
    """'Paste Complaint Text / Email' path."""
    return _run_intake_graph(db, text, source_document_name=None)


@router.post("/chat", response_model=schemas.ChatResponse)
async def chat(req: schemas.ChatRequest, db: Session = Depends(get_db)):
    """
    Free-form follow-up chat in the AI Assistant panel, e.g. "what's missing?"
    or "set severity to Major". Grounded on the complaint's current data.
    """
    complaint = db.query(models.Complaint).get(req.complaint_id)
    context = {c: getattr(complaint, c, None) for c in schemas.ComplaintFieldsExtracted.model_fields}

    system = (
        "You are the AI Complaint Intake Assistant for a pharmaceutical QA team. "
        "Answer the reviewer's question about this complaint concisely and helpfully, "
        "grounded only in the provided complaint data. If asked to change a field, "
        "explain what you'd change but note the reviewer must confirm it in the form."
    )
    user = f"Complaint data:\n{context}\n\nReviewer question: {req.message}"
    reply = call_groq_text(system, user, model=settings.GROQ_REASONING_MODEL)
    return schemas.ChatResponse(reply=reply)
