"""Grievance workflow endpoint — 9-stage multi-turn workflow."""

from fastapi import APIRouter
from pydantic import BaseModel

from app.grievance.workflow import GrievanceWorkflow

router = APIRouter(prefix="/grievances", tags=["grievances"])

_workflow = GrievanceWorkflow()


class GrievanceRequest(BaseModel):
    message: str
    conversation_id: str
    user_id: str


@router.post("")
def handle_grievance(req: GrievanceRequest) -> dict:
    result = _workflow.process_message(
        user_message=req.message,
        conversation_id=req.conversation_id,
        user_id=req.user_id,
    )
    return {
        "status": "ok",
        "response": result.response,
        "stage": result.stage.value if hasattr(result.stage, "value") else str(result.stage),
        "draft": result.draft,
        "is_complete": result.is_complete,
        "submission_route": result.submission_route,
        "evidence": result.evidence,
    }


@router.get("/{reference}")
def get_grievance_status(reference: str) -> dict:
    from app.grievance.status_lookup import GrievanceStatusLookup
    lookup = GrievanceStatusLookup()
    result = lookup.get_status_lookup(reference)
    return {"status": "ok", "result": result}
