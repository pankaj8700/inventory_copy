from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from database import get_session
from models.inventory import RequestIssueResponse, Request
from models.stock import CountsResponse
from typing import List

router = APIRouter(prefix="/vc", tags=["VC"])

@router.get("/all_requets", response_model=List[RequestIssueResponse])
async def get_all_requests(session: Session = Depends(get_session)):
    requests = session.exec(select(Request).order_by(Request.request_id)).all()
    if requests is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No requests found")
    return requests

@router.get("/all_approved", response_model=List[RequestIssueResponse])
async def get_all_approved(session: Session = Depends(get_session)):
    request = session.exec(select(Request).where(Request.status == "Approved")).all()
    if request is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No requests found")
    return request

@router.get("/all_rejected", response_model=List[RequestIssueResponse])
async def get_all_rejected(session: Session = Depends(get_session)):
    request = session.exec(select(Request).where(Request.status == "Rejected")).all()
    if request is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No requests found")
    return request

@router.get("/all_pending", response_model=List[RequestIssueResponse])
async def get_all_pending(session: Session = Depends(get_session)):
    request = session.exec(select(Request).where(Request.status == "Pending")).all()
    if request is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No requests found")
    return request

@router.get("/counts", response_model=CountsResponse, tags=["VC"])
async def get_counts(session: Session = Depends(get_session)):
    approved_items = session.exec(
        select(Request).where(Request.status == "Approved")
    ).all()
    approved_count = len(approved_items)

    rejected_items = session.exec(
        select(Request).where(Request.status == "Rejected")
    ).all()
    rejected_count = len(rejected_items)

    pending_items = session.exec(
        select(Request).where(Request.status == "Pending")
    ).all()
    pending_count = len(pending_items)

    return {"Approved": approved_count, "Rejected": rejected_count, "Pending": pending_count}