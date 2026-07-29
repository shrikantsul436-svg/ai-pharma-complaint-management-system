"""
Wires the nodes in agents/nodes.py into a single LangGraph pipeline:

  extract_fields -> check_completeness -> classify_risk
                  -> detect_duplicates -> suggest_root_cause_and_capa
                  -> summarize_and_respond

This is the graph that runs every time a document/text is dropped on the
"AI Complaint Intake Assistant" panel. It's intentionally a linear chain
(not branching) because each step's output feeds the next - but it's
built as a real StateGraph so branching (e.g. skip CAPA suggestion for
Minor severity) is a one-line change if needed later.
"""
from langgraph.graph import StateGraph, END

from app.agents.state import ComplaintAgentState
from app.agents import nodes


def build_intake_graph():
    graph = StateGraph(ComplaintAgentState)

    graph.add_node("extract_fields", nodes.extract_fields)
    graph.add_node("check_completeness", nodes.check_completeness)
    graph.add_node("classify_risk", nodes.classify_risk)
    graph.add_node("detect_duplicates", nodes.detect_duplicates)
    graph.add_node("suggest_root_cause_and_capa", nodes.suggest_root_cause_and_capa)
    graph.add_node("summarize_and_respond", nodes.summarize_and_respond)

    graph.set_entry_point("extract_fields")
    graph.add_edge("extract_fields", "check_completeness")
    graph.add_edge("check_completeness", "classify_risk")
    graph.add_edge("classify_risk", "detect_duplicates")
    graph.add_edge("detect_duplicates", "suggest_root_cause_and_capa")
    graph.add_edge("suggest_root_cause_and_capa", "summarize_and_respond")
    graph.add_edge("summarize_and_respond", END)

    return graph.compile()


# Compiled once at import time and reused across requests (LangGraph graphs
# are stateless/thread-safe to invoke repeatedly).
intake_graph = build_intake_graph()
