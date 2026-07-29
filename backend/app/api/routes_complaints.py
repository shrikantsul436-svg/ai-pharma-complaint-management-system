from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/api/complaints", tags=["complaints"])


@router.get("", response_model=list[schemas.ComplaintOut])
def list_complaints(db: Session = Depends(get_db)):
    return db.query(models.Complaint).order_by(models.Complaint.created_at.desc()).all()


@router.get("/{complaint_id}", response_model=schemas.ComplaintOut)
def get_complaint(complaint_id: str, db: Session = Depends(get_db)):
    complaint = db.query(models.Complaint).get(complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return complaint


@router.put("/{complaint_id}")
def update_complaint(complaint_id: str, fields: schemas.ComplaintFieldsExtracted, db: Session = Depends(get_db)):
    """Used when the QA reviewer edits a field manually before saving, or hits Save Complaint."""
    complaint = db.query(models.Complaint).get(complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    for field, value in fields.model_dump(exclude_unset=True).items():
        setattr(complaint, field, value)

    complaint.status = models.ComplaintStatus.under_review
    db.commit()
    db.refresh(complaint)
    return {"ok": True, "id": complaint.id}


@router.delete("/{complaint_id}")
def delete_complaint(complaint_id: str, db: Session = Depends(get_db)):
    complaint = db.query(models.Complaint).get(complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    db.delete(complaint)
    db.commit()
    return {"ok": True}
