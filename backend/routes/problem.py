from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from backend.auth.deps import get_current_user
from backend.db import get_session
from backend.models.auth_models import Attempt, Problem, User
from backend.schemas.problem import (
    AttemptResponse,
    ProblemCreateRequest,
    ProblemCreateResponse,
)

router = APIRouter(tags=["problem"])


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
            solution_image_key=attempt.solution_image_key,
            verdict=attempt.verdict,
            response_type=attempt.response_type,
            message_is=attempt.message_is,
            created_at=attempt.created_at,
        )
        for attempt in attempts
    ]
