from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class FlashcardCreate(BaseModel):
    front: str = Field(..., min_length=1)
    back: str = Field(..., min_length=1)
    course_id: int
    user_id: int


class FlashcardOut(BaseModel):
    id: int
    front: str
    back: str
    course_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    is_deleted: bool
    is_approved: bool

    class Config:
        from_attributes = True


class CourseCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    user_id: int
    icon: Optional[str] = "mdi-book-open-page-variant-outline"


class CourseOut(BaseModel):
    id: int
    name: str
    icon: str
    user_id: int
    created_at: datetime
    updated_at: datetime
    is_deleted: bool
    cards: List[FlashcardOut] = []

    class Config:
        from_attributes = True
