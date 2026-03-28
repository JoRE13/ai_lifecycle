import json
from datetime import datetime, timedelta, timezone
import logging
from uuid import UUID
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from backend.auth.deps import get_current_user
from backend.db import get_session
from backend.error_taxonomy import normalize_error_type
from backend.llm import submit_langfuse_score
from backend.models.auth_models import (
    AnalyticsEvent,
    Attempt,
    ErrorBankEntry,
    AttemptFeedback,
    AttemptLabel,
    Folder,
    Problem,
    User,
)
from backend.schemas.problem import (
    AnalyticsEventResponse,
    AttemptFeedbackCreateRequest,
    AttemptFeedbackResponse,
    AttemptLabelCreateRequest,
    AttemptLabelResponse,
    AttemptResponse,
    ErrorBankEntryResponse,
    ErrorBankSummaryResponse,
    FolderCreateRequest,
    FolderResponse,
    FolderUpdateRequest,
    ProblemBatchMoveRequest,
    ProblemBatchMoveResponse,
    ProblemCreateRequest,
    ProblemCreateResponse,
    ProblemMoveRequest,
    UserStatsSummaryResponse,
)
from backend.storage.r2 import R2ConfigurationError, presigned_get_url

router = APIRouter(tags=["problem"])
logger = logging.getLogger(__name__)
DEFAULT_FOLDER_NAME = "Unsorted"
DEFAULT_FOLDER_COLOR = "#6B7280"
SUCCESS_VERDICTS = {"correct_so_far", "fully_correct", "fully_solved"}
SOLVED_VERDICTS = {"fully_solved"}


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


def _ensure_default_folder(*, session: Session, user_id: UUID) -> Folder:
    existing = session.exec(
        select(Folder).where(Folder.user_id == user_id, Folder.name == DEFAULT_FOLDER_NAME)
    ).first()
    if existing and existing.parent_folder_id is not None:
        existing.parent_folder_id = None
        existing.updated_at = datetime.now(timezone.utc)
        session.add(existing)
    if existing:
        return existing

    now = datetime.now(timezone.utc)
    folder = Folder(
        user_id=user_id,
        parent_folder_id=None,
        name=DEFAULT_FOLDER_NAME,
        color=DEFAULT_FOLDER_COLOR,
        created_at=now,
        updated_at=now,
        archived_at=None,
    )
    session.add(folder)
    try:
        session.flush()
        return folder
    except IntegrityError:
        session.rollback()
        existing_after_conflict = session.exec(
            select(Folder).where(Folder.user_id == user_id, Folder.name == DEFAULT_FOLDER_NAME)
        ).first()
        if existing_after_conflict:
            return existing_after_conflict
        raise


def _normalize_folder_name(name: str) -> str:
    normalized = name.strip()
    if not normalized:
        raise HTTPException(status_code=422, detail="folder name must not be empty")
    return normalized


def _normalize_folder_color(color: str | None) -> str | None:
    if color is None:
        return None
    normalized = color.strip()
    if not normalized:
        return None
    return normalized


def _resolve_folder(
    *,
    session: Session,
    user_id: UUID,
    folder_id: UUID,
    allow_archived: bool = False,
) -> Folder:
    folder = session.exec(
        select(Folder).where(Folder.id == folder_id, Folder.user_id == user_id)
    ).first()
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    if folder.archived_at is not None and not allow_archived:
        raise HTTPException(status_code=409, detail="Folder is archived")
    return folder


def _is_default_folder(folder: Folder) -> bool:
    return folder.name == DEFAULT_FOLDER_NAME


def _validate_parent_folder(
    *,
    session: Session,
    user_id: UUID,
    parent_folder_id: UUID,
) -> Folder:
    parent_folder = _resolve_folder(
        session=session,
        user_id=user_id,
        folder_id=parent_folder_id,
        allow_archived=False,
    )
    if parent_folder.parent_folder_id is not None:
        raise HTTPException(
            status_code=422,
            detail="Only one level of subfolders is supported",
        )
    return parent_folder


def _problem_response(problem: Problem, folder_name: str | None) -> ProblemCreateResponse:
    return ProblemCreateResponse(
        id=problem.id,
        user_id=problem.user_id,
        folder_id=problem.folder_id,
        folder_name=folder_name,
        title=problem.title or "",
        created_at=problem.created_at,
        updated_at=problem.updated_at,
    )


@router.post("/folders", response_model=FolderResponse)
def create_folder(
    payload: FolderCreateRequest,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    name = _normalize_folder_name(payload.name)
    color = _normalize_folder_color(payload.color)
    parent_folder_id = payload.parent_folder_id
    existing = session.exec(
        select(Folder).where(
            Folder.user_id == user.id,
            func.lower(Folder.name) == name.lower(),
        )
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Folder name already exists")

    if parent_folder_id is not None:
        _validate_parent_folder(
            session=session,
            user_id=user.id,
            parent_folder_id=parent_folder_id,
        )

    now = datetime.now(timezone.utc)
    folder = Folder(
        user_id=user.id,
        parent_folder_id=parent_folder_id,
        name=name,
        color=color,
        created_at=now,
        updated_at=now,
        archived_at=None,
    )
    session.add(folder)
    session.flush()
    _record_event(
        session=session,
        user_id=user.id,
        problem_id=None,
        attempt_id=None,
        event_type="folder_created",
        metadata_json=json.dumps(
            {
                "folder_id": str(folder.id),
                "folder_name": folder.name,
                "parent_folder_id": str(parent_folder_id) if parent_folder_id else None,
            }
        ),
    )
    session.commit()
    session.refresh(folder)
    return FolderResponse(
        id=folder.id,
        user_id=folder.user_id,
        parent_folder_id=folder.parent_folder_id,
        name=folder.name,
        color=folder.color,
        created_at=folder.created_at,
        updated_at=folder.updated_at,
        archived_at=folder.archived_at,
        problem_count=0,
    )


@router.get("/folders", response_model=list[FolderResponse])
def list_folders(
    include_archived: bool = False,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    default_folder = _ensure_default_folder(session=session, user_id=user.id)
    session.commit()
    session.refresh(default_folder)

    statement = select(Folder).where(Folder.user_id == user.id)
    if not include_archived:
        statement = statement.where(Folder.archived_at.is_(None))
    folders = session.exec(statement.order_by(Folder.created_at.asc())).all()

    rows = session.exec(
        select(Problem.folder_id, func.count(Problem.id))
        .where(Problem.user_id == user.id)
        .group_by(Problem.folder_id)
    ).all()
    folder_counts = {folder_id: count for folder_id, count in rows if folder_id is not None}
    unassigned_count = next((count for folder_id, count in rows if folder_id is None), 0)
    if unassigned_count:
        folder_counts[default_folder.id] = folder_counts.get(default_folder.id, 0) + unassigned_count

    return [
        FolderResponse(
            id=folder.id,
            user_id=folder.user_id,
            parent_folder_id=folder.parent_folder_id,
            name=folder.name,
            color=folder.color,
            created_at=folder.created_at,
            updated_at=folder.updated_at,
            archived_at=folder.archived_at,
            problem_count=folder_counts.get(folder.id, 0),
        )
        for folder in folders
    ]


@router.patch("/folders/{folder_id}", response_model=FolderResponse)
def update_folder(
    folder_id: UUID,
    payload: FolderUpdateRequest,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    folder = _resolve_folder(session=session, user_id=user.id, folder_id=folder_id, allow_archived=True)
    now = datetime.now(timezone.utc)
    updated_fields = getattr(payload, "model_fields_set", getattr(payload, "__fields_set__", set()))

    if not updated_fields.intersection({"name", "color", "parent_folder_id"}):
        raise HTTPException(status_code=422, detail="No folder fields provided for update")

    if payload.name is not None:
        new_name = _normalize_folder_name(payload.name)
        if _is_default_folder(folder) and new_name != DEFAULT_FOLDER_NAME:
            raise HTTPException(status_code=400, detail="Cannot rename default folder")
        duplicate = session.exec(
            select(Folder).where(
                Folder.user_id == user.id,
                Folder.id != folder.id,
                func.lower(Folder.name) == new_name.lower(),
            )
        ).first()
        if duplicate:
            raise HTTPException(status_code=409, detail="Folder name already exists")
        folder.name = new_name

    if payload.color is not None:
        folder.color = _normalize_folder_color(payload.color)

    if "parent_folder_id" in updated_fields:
        new_parent_folder_id = payload.parent_folder_id
        if _is_default_folder(folder) and new_parent_folder_id is not None:
            raise HTTPException(status_code=400, detail="Cannot move default folder")
        if new_parent_folder_id == folder.id:
            raise HTTPException(status_code=422, detail="Folder cannot be its own parent")

        if new_parent_folder_id is not None:
            parent_folder = _validate_parent_folder(
                session=session,
                user_id=user.id,
                parent_folder_id=new_parent_folder_id,
            )
            has_children = session.exec(
                select(Folder.id).where(
                    Folder.user_id == user.id,
                    Folder.parent_folder_id == folder.id,
                    Folder.archived_at.is_(None),
                )
            ).first()
            if has_children:
                raise HTTPException(
                    status_code=422,
                    detail="Folder with subfolders cannot be moved under another folder",
                )
            folder.parent_folder_id = parent_folder.id
        else:
            folder.parent_folder_id = None

    folder.updated_at = now
    _record_event(
        session=session,
        user_id=user.id,
        problem_id=None,
        attempt_id=None,
        event_type="folder_updated",
        metadata_json=json.dumps(
            {
                "folder_id": str(folder.id),
                "folder_name": folder.name,
                "parent_folder_id": (
                    str(folder.parent_folder_id) if folder.parent_folder_id is not None else None
                ),
            }
        ),
    )
    session.add(folder)
    session.commit()
    session.refresh(folder)

    problem_count = session.exec(
        select(func.count(Problem.id)).where(Problem.user_id == user.id, Problem.folder_id == folder.id)
    ).one()

    return FolderResponse(
        id=folder.id,
        user_id=folder.user_id,
        parent_folder_id=folder.parent_folder_id,
        name=folder.name,
        color=folder.color,
        created_at=folder.created_at,
        updated_at=folder.updated_at,
        archived_at=folder.archived_at,
        problem_count=problem_count,
    )


@router.delete("/folders/{folder_id}", response_model=FolderResponse)
def archive_folder(
    folder_id: UUID,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    folder = _resolve_folder(session=session, user_id=user.id, folder_id=folder_id, allow_archived=True)
    if _is_default_folder(folder):
        raise HTTPException(status_code=400, detail="Cannot archive default folder")

    default_folder = _ensure_default_folder(session=session, user_id=user.id)
    if default_folder.archived_at is not None:
        default_folder.archived_at = None
        default_folder.updated_at = datetime.now(timezone.utc)

    now = datetime.now(timezone.utc)
    moved_count = 0
    detached_child_folder_count = 0
    child_folders = session.exec(
        select(Folder).where(Folder.user_id == user.id, Folder.parent_folder_id == folder.id)
    ).all()
    for child_folder in child_folders:
        child_folder.parent_folder_id = None
        child_folder.updated_at = now
        session.add(child_folder)
        detached_child_folder_count += 1

    problems_to_move = session.exec(
        select(Problem).where(Problem.user_id == user.id, Problem.folder_id == folder.id)
    ).all()
    for problem in problems_to_move:
        problem.folder_id = default_folder.id
        problem.updated_at = now
        session.add(problem)
        moved_count += 1

    folder.archived_at = now
    folder.updated_at = now
    session.add(folder)
    _record_event(
        session=session,
        user_id=user.id,
        problem_id=None,
        attempt_id=None,
        event_type="folder_archived",
        metadata_json=json.dumps(
            {
                "folder_id": str(folder.id),
                "moved_problem_count": moved_count,
                "detached_child_folder_count": detached_child_folder_count,
            }
        ),
    )
    session.commit()
    session.refresh(folder)

    return FolderResponse(
        id=folder.id,
        user_id=folder.user_id,
        parent_folder_id=folder.parent_folder_id,
        name=folder.name,
        color=folder.color,
        created_at=folder.created_at,
        updated_at=folder.updated_at,
        archived_at=folder.archived_at,
        problem_count=0,
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

    folder_id = payload.folder_id
    if folder_id is None:
        target_folder = _ensure_default_folder(session=session, user_id=user.id)
    else:
        target_folder = _resolve_folder(
            session=session, user_id=user.id, folder_id=folder_id, allow_archived=False
        )

    problem = Problem(
        user_id=user.id,
        folder_id=target_folder.id,
        title=title,
        created_at=now,
        updated_at=now,
    )
    session.add(problem)
    # Ensure the parent row exists before inserting analytics rows with FK refs.
    session.flush()
    _record_event(
        session=session,
        user_id=user.id,
        problem_id=problem.id,
        attempt_id=None,
        event_type="problem_created",
        metadata_json=json.dumps({"folder_id": str(target_folder.id)}),
    )
    session.commit()
    session.refresh(problem)
    return _problem_response(problem, target_folder.name)


@router.get("/problems", response_model=list[ProblemCreateResponse])
def list_problems(
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    statement = (
        select(Problem, Folder.name)
        .join(Folder, Folder.id == Problem.folder_id, isouter=True)
        .where(Problem.user_id == user.id)
        .order_by(Problem.created_at.desc())
    )
    rows = session.exec(statement).all()
    return [
        _problem_response(problem, folder_name)
        for problem, folder_name in rows
    ]


@router.patch("/problems/{problem_id}/move", response_model=ProblemCreateResponse)
def move_problem_to_folder(
    problem_id: UUID,
    payload: ProblemMoveRequest,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    problem = session.exec(
        select(Problem).where(Problem.id == problem_id, Problem.user_id == user.id)
    ).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    target_folder = _resolve_folder(
        session=session,
        user_id=user.id,
        folder_id=payload.folder_id,
        allow_archived=False,
    )
    problem.folder_id = target_folder.id
    problem.updated_at = datetime.now(timezone.utc)
    session.add(problem)
    _record_event(
        session=session,
        user_id=user.id,
        problem_id=problem.id,
        attempt_id=None,
        event_type="problem_moved",
        metadata_json=json.dumps({"folder_id": str(target_folder.id)}),
    )
    session.commit()
    session.refresh(problem)
    return _problem_response(problem, target_folder.name)


@router.patch("/problems/move-batch", response_model=ProblemBatchMoveResponse)
def move_problems_batch(
    payload: ProblemBatchMoveRequest,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    target_folder = _resolve_folder(
        session=session,
        user_id=user.id,
        folder_id=payload.folder_id,
        allow_archived=False,
    )
    requested_ids = list(dict.fromkeys(payload.problem_ids))
    problems = session.exec(
        select(Problem).where(
            Problem.user_id == user.id,
            Problem.id.in_(requested_ids),
        )
    ).all()
    if len(problems) != len(requested_ids):
        raise HTTPException(status_code=404, detail="One or more problems not found")

    now = datetime.now(timezone.utc)
    for problem in problems:
        problem.folder_id = target_folder.id
        problem.updated_at = now
        session.add(problem)
        _record_event(
            session=session,
            user_id=user.id,
            problem_id=problem.id,
            attempt_id=None,
            event_type="problem_moved",
            metadata_json=json.dumps({"folder_id": str(target_folder.id), "batch": True}),
        )

    session.commit()
    return ProblemBatchMoveResponse(moved_count=len(problems))


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
            page_count=attempt.page_count or 1,
            problem_image_url=_attempt_asset_url(attempt.problem_image_key),
            solution_image_url=_attempt_asset_url(attempt.solution_image_key),
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


@router.post("/attempts/{attempt_id}/labels", response_model=AttemptLabelResponse)
def create_attempt_label(
    attempt_id: UUID,
    payload: AttemptLabelCreateRequest,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    attempt = session.exec(
        select(Attempt).where(Attempt.id == attempt_id, Attempt.user_id == user.id)
    ).first()
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")

    now = datetime.now(timezone.utc)
    label = AttemptLabel(
        id=uuid4(),
        attempt_id=attempt.id,
        user_id=user.id,
        anon_user_id=user.anon_user_id,
        label_source=payload.label_source.strip(),
        label_name=payload.label_name.strip(),
        label_value=payload.label_value.strip(),
        confidence=payload.confidence,
        notes=payload.notes,
        created_at=now,
    )
    session.add(label)
    _record_event(
        session=session,
        user_id=user.id,
        problem_id=attempt.problem_id,
        attempt_id=attempt.id,
        event_type="attempt_labeled",
        mode=attempt.mode,
        verdict=attempt.verdict,
        metadata_json=json.dumps(
            {
                "label_source": label.label_source,
                "label_name": label.label_name,
            }
        ),
    )
    session.commit()
    session.refresh(label)

    return AttemptLabelResponse(
        id=label.id,
        attempt_id=label.attempt_id,
        user_id=label.user_id,
        anon_user_id=label.anon_user_id,
        label_source=label.label_source,
        label_name=label.label_name,
        label_value=label.label_value,
        confidence=label.confidence,
        notes=label.notes,
        created_at=label.created_at,
    )


@router.get("/attempts/{attempt_id}/labels", response_model=list[AttemptLabelResponse])
def list_attempt_labels(
    attempt_id: UUID,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    attempt = session.exec(
        select(Attempt).where(Attempt.id == attempt_id, Attempt.user_id == user.id)
    ).first()
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")

    labels = session.exec(
        select(AttemptLabel)
        .where(AttemptLabel.attempt_id == attempt.id, AttemptLabel.user_id == user.id)
        .order_by(AttemptLabel.created_at.desc())
    ).all()
    return [
        AttemptLabelResponse(
            id=label.id,
            attempt_id=label.attempt_id,
            user_id=label.user_id,
            anon_user_id=label.anon_user_id,
            label_source=label.label_source,
            label_name=label.label_name,
            label_value=label.label_value,
            confidence=label.confidence,
            notes=label.notes,
            created_at=label.created_at,
        )
        for label in labels
    ]


def _attempt_asset_url(asset_key: str | None) -> str | None:
    if not asset_key:
        return None
    try:
        return presigned_get_url(key=asset_key)
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

    trace_id = payload.trace_id or attempt.trace_id
    observation_id = payload.observation_id or attempt.observation_id
    request_id = payload.request_id or attempt.request_id

    feedback = AttemptFeedback(
        id=uuid4(),
        attempt_id=attempt.id,
        user_id=user.id,
        rating=payload.rating,
        comment=payload.comment,
        trace_id=trace_id,
        observation_id=observation_id,
        request_id=request_id,
        client_request_id=payload.client_request_id,
        session_id=payload.session_id,
        feature=payload.feature,
        flow=payload.flow,
        route_name=payload.route_name,
        mode=payload.mode or attempt.mode,
        model_name=payload.model_name or attempt.model_name,
        prompt_version=payload.prompt_version or attempt.prompt_version,
        latency_ms=payload.latency_ms if payload.latency_ms is not None else attempt.latency_ms,
        tokens_in=payload.tokens_in if payload.tokens_in is not None else attempt.tokens_in,
        tokens_out=payload.tokens_out if payload.tokens_out is not None else attempt.tokens_out,
        tokens_total=payload.tokens_total if payload.tokens_total is not None else attempt.tokens_total,
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

    rating_value = (payload.rating or "").strip().lower()
    thumbs_up_values = {"thumb_up", "thumbs_up", "up", "like", "positive"}
    thumbs_down_values = {"thumb_down", "thumbs_down", "down", "dislike", "negative"}

    score_metadata = {
        "attempt_id": str(attempt.id),
        "problem_id": str(attempt.problem_id),
        "user_id": str(user.id),
        "request_id": request_id,
    }
    score_attempted = False
    score_successes: list[bool] = []
    score_errors: list[str] = []

    def _capture_score_result(result: tuple[bool, str | None]) -> None:
        success, error = result
        score_successes.append(success)
        if not success and error:
            score_errors.append(error)

    try:
        if rating_value in thumbs_up_values:
            score_attempted = True
            _capture_score_result(
                submit_langfuse_score(
                    name="thumbs_up",
                    value=1.0,
                    observation_id=observation_id,
                    trace_id=trace_id,
                    comment=payload.comment,
                    metadata=score_metadata,
                )
            )
        elif rating_value in thumbs_down_values:
            score_attempted = True
            _capture_score_result(
                submit_langfuse_score(
                    name="thumbs_down",
                    value=1.0,
                    observation_id=observation_id,
                    trace_id=trace_id,
                    comment=payload.comment,
                    metadata=score_metadata,
                )
            )

        if payload.comment and payload.comment.strip():
            score_attempted = True
            _capture_score_result(
                submit_langfuse_score(
                    name="corrected",
                    value=1.0,
                    observation_id=observation_id,
                    trace_id=trace_id,
                    comment=payload.comment,
                    metadata=score_metadata,
                )
            )
    except Exception:
        logger.exception("Failed to submit Langfuse feedback scores")

    score_submitted = None
    score_error = None
    if score_attempted:
        score_submitted = all(score_successes) if score_successes else False
        if not score_submitted and score_errors:
            score_error = " | ".join(dict.fromkeys(score_errors))

    return AttemptFeedbackResponse(
        id=feedback.id,
        attempt_id=feedback.attempt_id,
        user_id=feedback.user_id,
        rating=feedback.rating,
        comment=feedback.comment,
        created_at=feedback.created_at,
        score_submitted=score_submitted,
        score_error=score_error,
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


@router.get("/analytics/summary", response_model=UserStatsSummaryResponse)
def get_user_stats_summary(
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    now = datetime.now(timezone.utc)
    today = now.date()
    seven_days_ago = now - timedelta(days=7)

    total_attempts = session.exec(
        select(func.count(Attempt.id)).where(Attempt.user_id == user.id)
    ).one()
    success_attempts = session.exec(
        select(func.count(Attempt.id)).where(
            Attempt.user_id == user.id,
            Attempt.verdict.in_(SUCCESS_VERDICTS),
        )
    ).one()
    attempts_last_7_days = session.exec(
        select(func.count(Attempt.id)).where(
            Attempt.user_id == user.id,
            Attempt.created_at >= seven_days_ago,
        )
    ).one()
    solved_problems_count = session.exec(
        select(func.count(func.distinct(Attempt.problem_id))).where(
            Attempt.user_id == user.id,
            Attempt.verdict.in_(SOLVED_VERDICTS),
        )
    ).one()

    days_with_activity_rows = session.exec(
        select(func.date(Attempt.created_at))
        .where(Attempt.user_id == user.id)
        .distinct()
        .order_by(func.date(Attempt.created_at).desc())
    ).all()
    normalized_days_with_activity = {
        d.date() if isinstance(d, datetime) else d for d in days_with_activity_rows
    }

    active_streak_days = 0
    cursor_day = today
    while cursor_day in normalized_days_with_activity:
        active_streak_days += 1
        cursor_day -= timedelta(days=1)

    success_rate = (float(success_attempts) / float(total_attempts)) if total_attempts else 0.0
    return UserStatsSummaryResponse(
        solved_problems_count=int(solved_problems_count or 0),
        success_rate=success_rate,
        active_streak_days=active_streak_days,
        attempts_last_7_days=int(attempts_last_7_days or 0),
        total_attempts=int(total_attempts or 0),
    )


@router.get("/analytics/error-bank", response_model=ErrorBankSummaryResponse)
def get_error_bank_summary(
    limit: int = 50,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    safe_limit = max(1, min(limit, 200))
    raw_entries = session.exec(
        select(ErrorBankEntry)
        .where(ErrorBankEntry.anon_user_id == user.anon_user_id)
    ).all()

    aggregated: dict[tuple[str, str], dict[str, int | str | datetime]] = {}
    for entry in raw_entries:
        concept_tag = entry.concept_tag or ""
        normalized_error_type = normalize_error_type(entry.error_type, concept_tag=concept_tag) or entry.error_type
        key = (normalized_error_type, concept_tag)
        existing = aggregated.get(key)
        if existing is None:
            aggregated[key] = {
                "error_type": normalized_error_type,
                "concept_tag": concept_tag,
                "count": int(entry.count),
                "fixed_count": int(entry.fixed_count),
                "unclear_count": int(entry.unclear_count),
                "last_seen_at": entry.last_seen_at,
            }
            continue
        existing["count"] = int(existing["count"]) + int(entry.count)
        existing["fixed_count"] = int(existing["fixed_count"]) + int(entry.fixed_count)
        existing["unclear_count"] = int(existing["unclear_count"]) + int(entry.unclear_count)
        if entry.last_seen_at > existing["last_seen_at"]:
            existing["last_seen_at"] = entry.last_seen_at

    merged_entries = sorted(
        aggregated.values(),
        key=lambda item: (int(item["count"]), item["last_seen_at"]),
        reverse=True,
    )

    total_occurrences = sum(int(item["count"]) for item in merged_entries)
    total_distinct_errors = len(merged_entries)

    response_entries = []
    for entry in merged_entries[:safe_limit]:
        count = int(entry["count"])
        fixed_count = int(entry["fixed_count"])
        unclear_count = int(entry["unclear_count"])
        unresolved_count = max(0, count - fixed_count)
        resolution_ratio = (fixed_count / count) if count else 0.0
        unclear_ratio = (unclear_count / count) if count else 0.0
        response_entries.append(
            ErrorBankEntryResponse(
                error_type=str(entry["error_type"]),
                concept_tag=str(entry["concept_tag"]) or None,
                count=count,
                fixed_count=fixed_count,
                unclear_count=unclear_count,
                unresolved_count=unresolved_count,
                resolution_ratio=resolution_ratio,
                unclear_ratio=unclear_ratio,
                last_seen_at=entry["last_seen_at"],
            )
        )

    return ErrorBankSummaryResponse(
        total_occurrences=total_occurrences,
        total_distinct_errors=total_distinct_errors,
        entries=response_entries,
    )
