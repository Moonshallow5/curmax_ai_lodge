from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.course import CourseCreate, CourseOut, FlashcardCreate, FlashcardOut
from app.services import course_service, friend_service

router = APIRouter(tags=["courses"])


def _require_user(db: Session, user_id: int) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.get("/courses", response_model=List[CourseOut])
def get_courses(user_id: int, viewer_id: Optional[int] = None, db: Session = Depends(get_db)):
    _require_user(db, user_id)
    include_pending = viewer_id is not None and viewer_id == user_id
    return course_service.list_courses(db, user_id, include_pending)


@router.post("/courses", response_model=CourseOut, status_code=status.HTTP_201_CREATED)
def add_course(payload: CourseCreate, db: Session = Depends(get_db)):
    _require_user(db, payload.user_id)
    return course_service.create_course(db, payload)


def _owned_card(db: Session, card_id: int, user_id: int):
    _require_user(db, user_id)
    card = course_service.get_flashcard(db, card_id)
    if not card:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Flashcard not found")
    course = course_service.get_course_by_id(db, card.course_id)
    if not course or course.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the owner can change this flashcard")
    return card


@router.post("/flashcards", response_model=FlashcardOut, status_code=status.HTTP_201_CREATED)
def add_flashcard(payload: FlashcardCreate, db: Session = Depends(get_db)):
    _require_user(db, payload.user_id)
    course = course_service.get_course_by_id(db, payload.course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    is_owner = course.user_id == payload.user_id
    if not is_owner and not friend_service.are_friends(db, course.user_id, payload.user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can add flashcards after you are friends",
        )
    return course_service.create_flashcard(db, payload, approved=is_owner)


@router.post("/flashcards/{card_id}/delete", response_model=FlashcardOut)
def delete_flashcard(card_id: int, user_id: int, db: Session = Depends(get_db)):
    card = _owned_card(db, card_id, user_id)
    return course_service.soft_delete_flashcard(db, card)


@router.post("/flashcards/{card_id}/approve", response_model=FlashcardOut)
def approve_flashcard(card_id: int, user_id: int, db: Session = Depends(get_db)):
    card = _owned_card(db, card_id, user_id)
    return course_service.approve_flashcard(db, card)
