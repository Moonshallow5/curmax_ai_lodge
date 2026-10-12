from typing import List, Optional

from sqlalchemy.orm import Session, joinedload

from app.models.course import Course
from app.models.flashcard import Flashcard
from app.models.friend_request import FriendRequest
from app.models.user import User
from app.schemas.friend import FriendRequestCreate
from app.services.user_service import get_user_by_email, hash_password


def _load_options():
    return (
        joinedload(FriendRequest.requester),
        joinedload(FriendRequest.addressee),
    )


def list_for_user(db: Session, user_id: int) -> List[FriendRequest]:
    return (
        db.query(FriendRequest)
        .options(*_load_options())
        .filter(
            FriendRequest.is_deleted == False,
            (FriendRequest.requester_id == user_id) | (FriendRequest.addressee_id == user_id),
        )
        .order_by(FriendRequest.created_at.desc())
        .all()
    )


def get_request(db: Session, request_id: int) -> Optional[FriendRequest]:
    return (
        db.query(FriendRequest)
        .options(*_load_options())
        .filter(FriendRequest.id == request_id, FriendRequest.is_deleted == False)
        .first()
    )


def _pair(db: Session, first_id: int, second_id: int) -> Optional[FriendRequest]:
    return (
        db.query(FriendRequest)
        .options(*_load_options())
        .filter(
            (
                (FriendRequest.requester_id == first_id) & (FriendRequest.addressee_id == second_id)
            ) | (
                (FriendRequest.requester_id == second_id) & (FriendRequest.addressee_id == first_id)
            )
        )
        .first()
    )


def are_friends(db: Session, first_id: int, second_id: int) -> bool:
    row = _pair(db, first_id, second_id)
    return bool(row and not row.is_deleted and row.status == "accepted")


def send_request(db: Session, payload: FriendRequestCreate) -> FriendRequest:
    if payload.requester_id == payload.addressee_id:
        raise ValueError("You cannot send a friend request to yourself")

    existing = _pair(db, payload.requester_id, payload.addressee_id)
    if existing and not existing.is_deleted and existing.status in ("pending", "accepted"):
        if existing.status == "accepted":
            raise ValueError("You are already friends")
        raise ValueError("A friend request is already pending")

    if existing:
        existing.requester_id = payload.requester_id
        existing.addressee_id = payload.addressee_id
        existing.status = "pending"
        existing.is_deleted = False
        db.commit()
        db.refresh(existing)
        return get_request(db, existing.id)

    row = FriendRequest(
        requester_id=payload.requester_id,
        addressee_id=payload.addressee_id,
        status="pending",
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return get_request(db, row.id)


def set_status(db: Session, row: FriendRequest, status: str) -> FriendRequest:
    row.status = status
    db.commit()
    db.refresh(row)
    return get_request(db, row.id)


def seed_demo_friend(db: Session) -> None:
    """Second account plus one pending request so the home-page bell has something to show."""
    alex = get_user_by_email(db, "alex@test.com")
    if not alex:
        alex = User(
            name="Alex",
            email="alex@test.com",
            password_hash=hash_password("12345678"),
        )
        db.add(alex)
        db.flush()
        course = Course(name="Alex's Notes", icon="mdi-notebook-outline", user_id=alex.id)
        db.add(course)
        db.flush()
        db.add(Flashcard(
            front="Who owns these cards?",
            back="Alex. Open this profile from People on the home page.",
            course_id=course.id,
            user_id=alex.id,
        ))

    owner = get_user_by_email(db, "sandeep@test.com")
    if not owner:
        owner = db.query(User).filter(User.id != alex.id).order_by(User.id).first()
    if not owner or owner.id == alex.id:
        db.commit()
        return

    if not _pair(db, alex.id, owner.id):
        db.add(FriendRequest(
            requester_id=alex.id,
            addressee_id=owner.id,
            status="pending",
        ))
    db.commit()
