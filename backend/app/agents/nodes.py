"""
Each function here is one LangGraph node. Keeping them small and
single-purpose mirrors how the demo video's assistant works step by
step (extract -> assess -> check completeness -> flag duplicates ->
suggest CAPA -> summarize) rather than one giant prompt doing everything.
"""
from app.agents.state import ComplaintAgentState
from app.agents.groq_client import call_groq_json, call_groq_text
from app.config import settings

REQUIRED_FIELDS = [
    "complaint_source", "customer_name", "product_name", "batch_lot_number",
    "manufacturing_date", "expiry_date", "quantity_affected",
    "complaint_type", "complaint_date", "detailed_description",
]


# ---------------------------------------------------------------------------
# Node 1: Field extraction (fast model - gemma2-9b-it)
# ---------------------------------------------------------------------------
def extract_fields(state: ComplaintAgentState) -> ComplaintAgentState:
    system = """You are a Quality Assurance data-entry assistant for a pharmaceutical
manufacturer (API and Finished Dosage Form / FDF). Extract structured complaint
fields from the raw text of a customer complaint (email, PDF, or free text).

Return ONLY a JSON object with these exact keys (use null if not present/found):
complaint_source (e.g. "Email", "Phone", "Customer Portal"),
customer_name, product_name, product_strength_grade, batch_lot_number,
manufacturing_date (YYYY-MM-DD), expiry_date (YYYY-MM-DD),
quantity_affected (number only), quantity_unit (e.g. "kg", "units", "vials"),
complaint_type (e.g. "Contamination", "Packaging Defect", "Out of Specification",
"Discoloration", "Foreign Particle", "Short Shelf Life", "Efficacy Issue"),
complaint_date (YYYY-MM-DD), detailed_description (2-4 sentence factual summary
of what went wrong, in your own words)."""

    user = f"Raw complaint text:\n\n{state['raw_text']}"
    fields = call_groq_json(system, user, model=settings.GROQ_EXTRACTION_MODEL)
    return {"extracted_fields": fields}


# ---------------------------------------------------------------------------
# Node 2: Completeness checker (bonus feature)
# ---------------------------------------------------------------------------
def check_completeness(state: ComplaintAgentState) -> ComplaintAgentState:
    fields = state.get("extracted_fields", {}) or {}
    missing = [f for f in REQUIRED_FIELDS if not fields.get(f)]
    score = round(100 * (len(REQUIRED_FIELDS) - len(missing)) / len(REQUIRED_FIELDS), 1)
    return {"completeness_score": score, "missing_fields": missing}


# ---------------------------------------------------------------------------
# Node 3: AI risk classification (severity + priority)
# ---------------------------------------------------------------------------
def classify_risk(state: ComplaintAgentState) -> ComplaintAgentState:
    system = """You are a pharma QA risk assessor. Given extracted complaint fields,
classify Initial Severity as one of: Critical, Major, Minor, and Priority as one
of: High, Medium, Low. Base this on patient safety impact (e.g. contamination,
sterility, potency/efficacy issues, mislabeling of dose = Critical/High;
packaging/cosmetic defects with no safety impact = Minor/Low).

Return ONLY JSON: {"severity": "...", "priority": "...", "reasoning": "1-2 sentences"}"""

    user = f"Extracted fields:\n{state.get('extracted_fields')}"
    result = call_groq_json(system, user, model=settings.GROQ_REASONING_MODEL)
    return {
        "severity": result.get("severity"),
        "priority": result.get("priority"),
        "risk_reasoning": result.get("reasoning"),
    }


# ---------------------------------------------------------------------------
# Node 4: Duplicate complaint detection (bonus feature)
# ---------------------------------------------------------------------------
def detect_duplicates(state: ComplaintAgentState) -> ComplaintAgentState:
    existing = state.get("existing_complaints") or []
    if not existing:
        return {"duplicate_of": None, "duplicate_confidence": None}

    system = """You compare a new pharmaceutical complaint against a list of
existing complaints (same product, similar batch, similar description commonly
indicate a duplicate). Return ONLY JSON:
{"duplicate_of": "<id or null>", "confidence": <0-1 float>}"""

    user = (
        f"New complaint fields:\n{state.get('extracted_fields')}\n\n"
        f"Existing complaints (id + key fields):\n{existing}"
    )
    result = call_groq_json(system, user, model=settings.GROQ_REASONING_MODEL)
    return {
        "duplicate_of": result.get("duplicate_of"),
        "duplicate_confidence": result.get("confidence"),
    }


# ---------------------------------------------------------------------------
# Node 5: Root cause + CAPA recommendation (bonus feature)
# ---------------------------------------------------------------------------
def suggest_root_cause_and_capa(state: ComplaintAgentState) -> ComplaintAgentState:
    system = """You are a pharma QA/CAPA specialist. Given a complaint's details,
propose a likely ROOT CAUSE category (e.g. raw material variability, equipment
malfunction, process deviation, packaging line contamination, labeling error,
storage/transport condition) with brief justification, and a draft CAPA
(Corrective and Preventive Action) recommendation appropriate for a pharma QMS
(e.g. batch record review, supplier audit, requalification, retraining).

Return ONLY JSON: {"root_cause": "...", "capa_recommendation": "..."}
Keep each to 2-3 sentences. This is a preliminary AI suggestion for a QA
reviewer, not a final determination."""

    user = f"Complaint fields:\n{state.get('extracted_fields')}\nSeverity: {state.get('severity')}"
    result = call_groq_json(system, user, model=settings.GROQ_REASONING_MODEL)
    return {
        "root_cause_suggestion": result.get("root_cause"),
        "capa_recommendation": result.get("capa_recommendation"),
    }


# ---------------------------------------------------------------------------
# Node 6: Summary + chat-panel assistant message
# ---------------------------------------------------------------------------
def summarize_and_respond(state: ComplaintAgentState) -> ComplaintAgentState:
    fields = state.get("extracted_fields", {}) or {}
    missing = state.get("missing_fields", [])

    summary_system = "Summarize this pharmaceutical complaint in 2 sentences for a QA reviewer."
    summary = call_groq_text(summary_system, str(fields), model=settings.GROQ_EXTRACTION_MODEL)

    if missing:
        missing_list = ", ".join(m.replace("_", " ") for m in missing)
        assistant_message = (
            f"I've extracted what I could from the document and pre-filled the form "
            f"({state.get('completeness_score')}% complete). I couldn't find: {missing_list}. "
            f"Could you provide those, or I can proceed with a preliminary triage as-is?"
        )
    else:
        assistant_message = (
            f"I've extracted all key fields and pre-filled the form. "
            f"Suggested severity: {state.get('severity')}, priority: {state.get('priority')}. "
            f"Review and click Save Complaint when ready."
        )

    return {"summary": summary.strip(), "assistant_message": assistant_message}
