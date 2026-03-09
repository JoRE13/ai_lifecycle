from datetime import datetime, timezone
from uuid import UUID
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from backend.auth.deps import get_current_user
from backend.db import get_session
from backend.models.auth_models import AnalyticsEvent, Attempt, AttemptFeedback, Problem, User
from backend.schemas.problem import (
    AnalyticsEventResponse,
    AttemptFeedbackCreateRequest,
    AttemptFeedbackResponse,
    AttemptResponse,
    ProblemCreateRequest,
    ProblemCreateResponse,
)
from backend.storage.r2 import R2ConfigurationError, presigned_get_url

router = APIRouter(tags=["problem"])


def _record_event(
    *,
    session: Session,
    user_id: UUID,
    problem_id: UUID | None,
    attempt_id: UUID | None,
    event_type: str,
    mode: str | None = None,
    verdict: str | None = None,
    metadata_json: str | None = None,
) -> None:
    session.add(
        AnalyticsEvent(
            id=uuid4(),
            user_id=user_id,
            problem_id=problem_id,
            attempt_id=attempt_id,
            event_type=event_type,
            mode=mode,
            verdict=verdict,
            metadata_json=metadata_json,
            created_at=datetime.now(timezone.utc),
        )
    )


@router.post("/problem", response_model=ProblemCreateResponse)
def create_problem(
    payload: ProblemCreateRequest,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    now = datetime.now(timezone.utc)
    title = payload.title.strip()
    if not title:
        raise HTTPException(status_code=422, detail="title must not be empty")

    problem = Problem(
        user_id=user.id,
        title=title,
        created_at=now,
        updated_at=now,
    )
    session.add(problem)
    _record_event(
        session=session,
        user_id=user.id,
        problem_id=problem.id,
        attempt_id=None,
        event_type="problem_created",
    )
    session.commit()
    session.refresh(problem)
    return ProblemCreateResponse(
        id=problem.id,
        user_id=problem.user_id,
        title=problem.title or "",
        created_at=problem.created_at,
        updated_at=problem.updated_at,
    )


@router.get("/problems", response_model=list[ProblemCreateResponse])
def list_problems(
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    statement = (
        select(Problem)
        .where(Problem.user_id == user.id)
        .order_by(Problem.created_at.desc())
    )
    problems = session.exec(statement).all()
    return [
        ProblemCreateResponse(
            id=problem.id,
            user_id=problem.user_id,
            title=problem.title or "",
            created_at=problem.created_at,
            updated_at=problem.updated_at,
        )
        for problem in problems
    ]


@router.get("/problems/{problem_id}/attempts", response_model=list[AttemptResponse])
def list_problem_attempts(
    problem_id: UUID,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    problem = session.exec(
        select(Problem).where(Problem.id == problem_id, Problem.user_id == user.id)
    ).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    attempts = session.exec(
        select(Attempt)
        .where(Attempt.problem_id == problem_id, Attempt.user_id == user.id)
        .order_by(Attempt.created_at.desc())
    ).all()
    return [
        AttemptResponse(
            id=attempt.id,
            problem_id=attempt.problem_id,
            user_id=attempt.user_id,
            mode=attempt.mode,
            solution_image_url=_attempt_solution_url(attempt),
            verdict=attempt.verdict,
            response_type=attempt.response_type,
            message_is=attempt.message_is,
            error_type=attempt.error_type,
            model_name=attempt.model_name,
            prompt_version=attempt.prompt_version,
            latency_ms=attempt.latency_ms,
            tokens_in=attempt.tokens_in,
            tokens_out=attempt.tokens_out,
            tokens_thoughts=attempt.tokens_thoughts,
            tokens_total=attempt.tokens_total,
            created_at=attempt.created_at,
        )
        for attempt in attempts
    ]


def _attempt_solution_url(attempt: Attempt) -> str | None:
    if not attempt.solution_image_key:
        return None
    try:
        return presigned_get_url(key=attempt.solution_image_key)
    except R2ConfigurationError:
        return None


@router.post(
    "/attempts/{attempt_id}/feedback",
    response_model=AttemptFeedbackResponse,
)
def submit_attempt_feedback(
    attempt_id: UUID,
    payload: AttemptFeedbackCreateRequest,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    attempt = session.exec(
        select(Attempt).where(Attempt.id == attempt_id, Attempt.user_id == user.id)
    ).first()
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")

    feedback = AttemptFeedback(
        id=uuid4(),
        attempt_id=attempt.id,
        user_id=user.id,
        rating=payload.rating,
        comment=payload.comment,
        created_at=datetime.now(timezone.utc),
    )
    session.add(feedback)
    _record_event(
        session=session,
        user_id=user.id,
        problem_id=attempt.problem_id,
        attempt_id=attempt.id,
        event_type="feedback_submitted",
        mode=attempt.mode,
        verdict=attempt.verdict,
    )
    session.commit()

    return AttemptFeedbackResponse(
        id=feedback.id,
        attempt_id=feedback.attempt_id,
        user_id=feedback.user_id,
        rating=feedback.rating,
        comment=feedback.comment,
        created_at=feedback.created_at,
    )


@router.get("/analytics/events", response_model=list[AnalyticsEventResponse])
def list_analytics_events(
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    events = session.exec(
        select(AnalyticsEvent)
        .where(AnalyticsEvent.user_id == user.id)
        .order_by(AnalyticsEvent.created_at.desc())
        .limit(200)
    ).all()
    return [
        AnalyticsEventResponse(
            id=event.id,
            user_id=event.user_id,
            problem_id=event.problem_id,
            attempt_id=event.attempt_id,
            event_type=event.event_type,
            mode=event.mode,
            verdict=event.verdict,
            metadata_json=event.metadata_json,
            created_at=event.created_at,
        )
        for event in events
    ]
