from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from database import get_session
from models.inventory import RequestIssueResponse, Request
from typing import List

router = APIRouter(prefix="/vc", tags=["VC"])

@router.get("/all_requets", response_model=List[RequestIssueResponse])
async def get_all_requests(session: Session = Depends(get_session)):
    requests = session.exec(select(Request)).all()
    if requests is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No requests found")
    return requests