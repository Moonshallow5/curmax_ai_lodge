from datetime import datetime

from pydantic import BaseModel

from app.schemas.user import UserOut


class FriendRequestCreate(BaseModel):
    requester_id: int
    addressee_id: int


class FriendRequestOut(BaseModel):
    id: int
    requester_id: int
    addressee_id: int
    status: str
    created_at: datetime
    updated_at: datetime
    is_deleted: bool
    requester: UserOut
    addressee: UserOut

    class Config:
        from_attributes = True
