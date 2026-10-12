from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.friend import FriendRequestCreate, FriendRequestOut
from app.services import friend_service

router = APIRouter(prefix="/friend-requests", tags=["friends"])


def _require_user(db: Session, user_id: int) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.get("", response_model=List[FriendRequestOut])
def list_requests(user_id: int, db: Session = Depends(get_db)):
    _require_user(db, user_id)
    return friend_service.list_for_user(db, user_id)


@router.post("", response_model=FriendRequestOut, status_code=status.HTTP_201_CREATED)
def create_request(payload: FriendRequestCreate, db: Session = Depends(get_db)):
    _require_user(db, payload.requester_id)
    _require_user(db, payload.addressee_id)
    try:
        return friend_service.send_request(db, payload)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))


@router.post("/{request_id}/accept", response_model=FriendRequestOut)
def accept_request(request_id: int, db: Session = Depends(get_db)):
    row = friend_service.get_request(db, request_id)
    if not row or row.status != "pending":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Friend request not found")
    return friend_service.set_status(db, row, "accepted")


@router.post("/{request_id}/decline", response_model=FriendRequestOut)
def decline_request(request_id: int, db: Session = Depends(get_db)):
    row = friend_service.get_request(db, request_id)
    if not row or row.status != "pending":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Friend request not found")
    return friend_service.set_status(db, row, "declined")
