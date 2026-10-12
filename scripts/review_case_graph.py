import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import NotRequired

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from run_case_graph import (
    CaseState,
    draft_summary,
    evaluate_policy,
    retrieve_evidence,
)


class ReviewState(CaseState):
    review: NotRequired[dict]
    review_status: NotRequired[str]


def human_review(state: ReviewState) -> dict:
    response = interrupt({
        "case_id": state["case_id"],
        "instruction": "A human must review the evidence and draft.",
        "choices": ["APPROVE_ESCALATION", "RETURN_FOR_REVISION"],
    })

    decision = response["decision"]
    reviewer = response["reviewer"].strip()
    note = response["note"].strip()

    if decision not in {"APPROVE_ESCALATION", "RETURN_FOR_REVISION"}:
        raise ValueError("Invalid reviewer decision")
    if not reviewer or not note:
        raise ValueError("Reviewer and note are required")

    if decision == "APPROVE_ESCALATION":
        eligible = any(
            item["decision"] == "INVESTIGATOR_REVIEW"
            and item["human_approval_required_for_escalation"]
            for item in state["result"]["policy_decisions"]
        )
        if not eligible:
            raise ValueError("Policy does not permit this escalation")

    return {
        "review": {
            "decision": decision,
            "reviewer": reviewer,
            "note": note,
            "reviewed_at_utc": datetime.now(timezone.utc).isoformat(),
        },
        "review_status": (
            "HUMAN_APPROVED_FOR_ESCALATION"
            if decision == "APPROVE_ESCALATION"
            else "RETURNED_FOR_REVISION"
        ),
    }


def build_graph(checkpointer):
    workflow = StateGraph(ReviewState)
    workflow.add_node("retrieve_evidence", retrieve_evidence)
    workflow.add_node("evaluate_policy", evaluate_policy)
    workflow.add_node("draft_summary", draft_summary)
    workflow.add_node("human_review", human_review)

    workflow.add_edge(START, "retrieve_evidence")
    workflow.add_edge("retrieve_evidence", "evaluate_policy")
    workflow.add_edge("evaluate_policy", "draft_summary")
    workflow.add_edge("draft_summary", "human_review")
    workflow.add_edge("human_review", END)

    return workflow.compile(checkpointer=checkpointer)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--case-id", required=True)
    parser.add_argument(
        "--decision",
        choices=["APPROVE_ESCALATION", "RETURN_FOR_REVISION"],
    )
    parser.add_argument("--reviewer")
    parser.add_argument("--note")
    args = parser.parse_args()

    if args.decision and (
        not args.reviewer or not args.reviewer.strip()
        or not args.note or not args.note.strip()
    ):
        parser.error("--decision requires --reviewer and --note")

    root = Path(__file__).resolve().parents[1]
    db_path = root / "data" / "generated" / "review_checkpoints.sqlite"
    db_path.parent.mkdir(parents=True, exist_ok=True)

    config = {
        "configurable": {
            "thread_id": f"case-review:{args.case_id}"
        }
    }

    with SqliteSaver.from_conn_string(str(db_path)) as checkpointer:
        graph = build_graph(checkpointer)
        saved = graph.get_state(config)

        if args.decision:
            if "human_review" not in saved.next:
                raise SystemExit("This case is not awaiting human review")

            state = graph.invoke(
                Command(resume={
                    "decision": args.decision,
                    "reviewer": args.reviewer,
                    "note": args.note,
                }),
                config=config,
            )
            print(json.dumps({
                **state["result"],
                "review": state["review"],
                "status": state["review_status"],
            }, indent=2, default=str))
            return

        if saved.values:
            if "human_review" in saved.next:
                print(json.dumps({
                    **saved.values["result"],
                    "status": "AWAITING_HUMAN_REVIEW",
                }, indent=2, default=str))
                return
            raise SystemExit("This case already has a completed review")

        state = graph.invoke({"case_id": args.case_id}, config=config)
        if "__interrupt__" not in state:
            raise RuntimeError("Expected the graph to pause for human review")

        print(json.dumps({
            **state["result"],
            "status": "AWAITING_HUMAN_REVIEW",
        }, indent=2, default=str))


if __name__ == "__main__":
    main()