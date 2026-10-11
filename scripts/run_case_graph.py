import argparse
import json
from typing import NotRequired, TypedDict

from langgraph.graph import END, START, StateGraph

from build_case_report import build_report, get_evidence
from summarize_case import draft_report


class CaseState(TypedDict):
    case_id: str
    evidence: NotRequired[dict]
    report: NotRequired[dict]
    result: NotRequired[dict]


def retrieve_evidence(state: CaseState) -> dict:
    return {"evidence": get_evidence(state["case_id"])}


def evaluate_policy(state: CaseState) -> dict:
    return {"report": build_report(state["evidence"])}


def draft_summary(state: CaseState) -> dict:
    return {"result": draft_report(state["report"])}


workflow = StateGraph(CaseState)
workflow.add_node("retrieve_evidence", retrieve_evidence)
workflow.add_node("evaluate_policy", evaluate_policy)
workflow.add_node("draft_summary", draft_summary)

workflow.add_edge(START, "retrieve_evidence")
workflow.add_edge("retrieve_evidence", "evaluate_policy")
workflow.add_edge("evaluate_policy", "draft_summary")
workflow.add_edge("draft_summary", END)

graph = workflow.compile()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--case-id", required=True)
    args = parser.parse_args()

    final_state = graph.invoke({"case_id": args.case_id})
    print(json.dumps(final_state["result"], indent=2, default=str))


if __name__ == "__main__":
    main()