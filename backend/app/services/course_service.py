from typing import List, Optional

from sqlalchemy import and_
from sqlalchemy.orm import Session, joinedload, with_loader_criteria

from app.models.course import Course
from app.models.flashcard import Flashcard
from app.models.user import User
from app.schemas.course import CourseCreate, FlashcardCreate

DEFAULT_ICON = "mdi-book-open-page-variant-outline"


def _visible_cards(include_pending: bool):
    if include_pending:
        return Flashcard.is_deleted == False
    return and_(Flashcard.is_deleted == False, Flashcard.is_approved == True)


def list_courses(db: Session, user_id: int, include_pending: bool = False) -> List[Course]:
    return (
        db.query(Course)
        .options(
            joinedload(Course.cards),
            with_loader_criteria(Flashcard, _visible_cards(include_pending)),
        )
        .filter(Course.user_id == user_id, Course.is_deleted == False)
        .order_by(Course.id)
        .all()
    )


def get_course_by_id(db: Session, course_id: int) -> Optional[Course]:
    return (
        db.query(Course)
        .filter(Course.id == course_id, Course.is_deleted == False)
        .first()
    )


def get_flashcard(db: Session, card_id: int) -> Optional[Flashcard]:
    return (
        db.query(Flashcard)
        .filter(Flashcard.id == card_id, Flashcard.is_deleted == False)
        .first()
    )


def create_course(db: Session, payload: CourseCreate) -> Course:
    course = Course(
        name=payload.name.strip(),
        icon=payload.icon or DEFAULT_ICON,
        user_id=payload.user_id,
    )
    db.add(course)
    db.commit()
    db.refresh(course)
    course.cards = []
    return course


def create_flashcard(db: Session, payload: FlashcardCreate, approved: bool) -> Flashcard:
    card = Flashcard(
        front=payload.front.strip(),
        back=payload.back.strip(),
        course_id=payload.course_id,
        user_id=payload.user_id,
        is_approved=approved,
    )
    db.add(card)
    db.commit()
    db.refresh(card)
    return card


def soft_delete_flashcard(db: Session, card: Flashcard) -> Flashcard:
    card.is_deleted = True
    db.commit()
    db.refresh(card)
    return card


def approve_flashcard(db: Session, card: Flashcard) -> Flashcard:
    card.is_approved = True
    db.commit()
    db.refresh(card)
    return card


def seed_demo(db: Session) -> None:
    """Load the original sample courses once, for the first user, if they have none."""
    user = db.query(User).order_by(User.id).first()
    if not user:
        return
    if db.query(Course).filter(Course.user_id == user.id).first():
        return

    samples = [
        {
            "name": "Statistical Thinking",
            "icon": "mdi-chart-bar",
            "cards": [
                ("What is the mean?", "The average of a set of numbers."),
                ("What is a median?", "The middle value when data is ordered."),
            ],
        },
        {
            "name": "Computational Thinking",
            "icon": "mdi-language-python",
            "cards": [
                ("What is decomposition?", "Breaking a problem into smaller parts."),
            ],
        },
        {
            "name": "AI Lodge",
            "icon": "mdi-robot-outline",
            "cards": [],
        },
    ]

    for sample in samples:
        course = Course(name=sample["name"], icon=sample["icon"], user_id=user.id)
        db.add(course)
        db.flush()
        for front, back in sample["cards"]:
            db.add(Flashcard(
                front=front,
                back=back,
                course_id=course.id,
                user_id=user.id,
            ))
    db.commit()
