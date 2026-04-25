from fastapi import APIRouter, HTTPException

from database import get_pool
from models import Application, HilActionPayload, HilActionResponse, HilQueueResponse
from routers.applications import (
    APPLICATION_SELECT,
    fetchrow_with_retry,
    fetch_with_retry,
    map_application_row,
)

router = APIRouter()


@router.get("/hil-review/queue", response_model=HilQueueResponse)
async def get_hil_queue():
    pool = await get_pool()
    rows = await fetch_with_retry(APPLICATION_SELECT + "\nORDER BY a.application_date DESC")
    apps: list[Application] = [await map_application_row(pool, dict(row)) for row in rows]

    awaiting = [app for app in apps if app.hil_required_flag and app.decision == "HIL Pending"]
    review = [app for app in apps if app.hil_required_flag and app.decision == "Conditional Approval"]
    approved = [app for app in apps if app.decision == "STP Approved"]
    rejected = [app for app in apps if app.decision == "Rejected"]
    return HilQueueResponse(
        awaiting=awaiting,
        review=review,
        approved=approved,
        rejected=rejected,
    )


@router.post("/hil-review/{application_id}/action", response_model=HilActionResponse)
async def post_hil_action(application_id: str, payload: HilActionPayload):
    pool = await get_pool()
    async with pool.acquire() as conn:
        exists = await conn.fetchval(
            "SELECT 1 FROM applications WHERE application_id = $1",
            application_id,
        )
        if not exists:
            raise HTTPException(status_code=404, detail="Application not found")

        if payload.action == "approve":
            db_decision = "APPROVED"
            hil_required = False
        elif payload.action == "modify_approve":
            db_decision = "APPROVED"
            hil_required = True
        else:
            db_decision = "REJECTED"
            hil_required = True

        await conn.execute(
            """
            UPDATE applications
            SET decision = $2, hil_required_flag = $3
            WHERE application_id = $1
            """,
            application_id,
            db_decision,
            hil_required,
        )

        await conn.execute(
            """
            UPDATE decision_engine_output
            SET decision = $2, hil_required_flag = $3
            WHERE application_id = $1
            """,
            application_id,
            db_decision,
            hil_required,
        )

    row = await fetchrow_with_retry(
        APPLICATION_SELECT + "\nWHERE a.application_id = $1\nLIMIT 1",
        application_id,
    )
    if not row:
        raise HTTPException(status_code=404, detail="Application not found after update")

    updated_application = await map_application_row(pool, dict(row))
    return HilActionResponse(success=True, updated_application=updated_application)
