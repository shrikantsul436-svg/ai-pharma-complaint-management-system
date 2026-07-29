"""
Shared state object that flows through every node of the LangGraph.
Each node reads what it needs and writes its own slice back in -
this is the standard LangGraph "state accumulates as it flows" pattern.
"""
from typing import TypedDict, Optional, List


class ComplaintAgentState(TypedDict, total=False):
    # input
    raw_text: str
    existing_complaints: List[dict]        # used for duplicate detection

    # step 1: field extraction (gemma2-9b-it)
    extracted_fields: dict

    # step 2: completeness check
    completeness_score: float
    missing_fields: List[str]

    # step 3: risk classification (severity/priority confirmation + reasoning)
    severity: str
    priority: str
    risk_reasoning: str

    # step 4: duplicate detection
    duplicate_of: Optional[str]
    duplicate_confidence: Optional[float]

    # step 5: root cause + CAPA (llama-3.3-70b-versatile)
    root_cause_suggestion: str
    capa_recommendation: str

    # step 6: summary + assistant message shown in the chat panel
    summary: str
    assistant_message: str
