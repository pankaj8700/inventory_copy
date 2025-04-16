from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from database import get_session
from models.stock import Stock, Item, StockBase, StockCreate, StockResponse, RequestResponse, RequestIssueResponse, ReqIssueBase, StatusEnum, ReqIssueResponse
from typing import List
from models.inventory import Request, ReqIssue, RequestIssueResponse2
from datetime import date
import logging
from fastapi.responses import JSONResponse
from utils.mail import *

router = APIRouter(prefix="/central_stock", tags=["Central_Stock"])

# Configure the logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

@router.post("/create_stock", response_model=StockResponse, tags=["Central_Stock"])
def create_stock(stock: StockCreate, session: Session = Depends(get_session)):
    # Check if gem_id already exists
    existing_stock = session.exec(select(Stock).where(Stock.gem_id == stock.gem_id)).first()
    if existing_stock:
        raise HTTPException(
            status_code=400,
            detail=f"Stock with gem_id {stock.gem_id} already exists."
        )
    # Create a new stock entry
    stock_model = Stock(
        gem_id=stock.gem_id,
        vendor_name=stock.vendor_name,
        date_of_order=stock.date_of_order,
        date_of_purchase=stock.date_of_purchase
    )

    session.add(stock_model)
    session.commit()
    session.refresh(stock_model)

    item_models = [
        Item(
            item_name=item.item_name,
            item_type=item.item_type,
            item_quantity=item.item_quantity,
            item_price=item.item_price,
            stock_id=stock_model.gem_id  # Fixed foreign key
        )
        for item in stock.items
    ]
    
    session.add_all(item_models)
    session.commit()

    return stock_model

@router.get("/get_stock_with_items/{gem_id}", response_model=StockResponse, tags=["Central_Stock"])
def get_stock_with_items(gem_id: int, session: Session = Depends(get_session)):
    stock = session.exec(select(Stock).where(Stock.gem_id == gem_id)).first()
    if not stock:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Stock not found")
    return stock


# issue to the request
@router.post("/item_issue_to_request/{request_id}", response_model=RequestIssueResponse, tags=["Central_Stock"], response_model_exclude={"reason"})
async def issue_request(request_id: int, issue: List[ReqIssueBase], session: Session = Depends(get_session)):
    try:
        request = session.exec(select(Request).where(Request.request_id == request_id).where(Request.status == "Pending")).first()
        if not request:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found")

        request.status = StatusEnum.Approved
        request.date_of_approval = date.today()
        issue_model = [
            ReqIssue(
                item_name=item.item_name,
                qty=item.qty,
                Item_Type = item.Item_Type,
                request_id=request.request_id
            )
            for item in issue
        ]
        # Commit the request and items
        session.add_all(issue_model)
        session.commit()
        session.refresh(request)

        issued_items = [
            ReqIssueResponse(
                item_name=item.item_name,
                qty=item.qty,
                Item_Type=item.Item_Type
            )
            for item in issue_model
        ]
        # Convert the request to a dictionary
        request_data = {
            "request_id": request.request_id,
            "campus_name": request.campus_name,
            "date_of_request": request.date_of_request,
            "status": request.status,
            "date_of_approval": request.date_of_approval
        }
        # Create an HTML template
        html = f"""
        <html>
        <body>
            <h1>Request Issued</h1>
            <p>Request ID: {request_data['request_id']}</p>
            <p>Campus Name: {request_data['campus_name']}</p>
            <p>Date of Request: {request_data['date_of_request']}</p>
            <p>Status: {['Approved']}</p>
            <p>Date of Approval: {request_data['date_of_approval']}</p>
            <h2>Issued Items</h2>
            <ul>
                {"".join([f"<li>{item.item_name}: {item.qty}: {item.Item_Type}</li>" for item in issue_model])}
            </ul>
        </body>
        </html>
        """
        
        message = MessageSchema(
            subject="Your Request has been Approved",
            recipients=[request.your_mail_id],
            body=html,
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message)
        logger.info("Email sent successfully")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return JSONResponse(status_code=500, content={"message": "Failed to send email"})

    return request

@router.post("/reject_request/{request_id}/{reason}", response_model=RequestIssueResponse, tags=["Central_Stock"],response_model_exclude={"issued"})
async def reject_request(request_id: int, reason: str, session: Session = Depends(get_session)):
    try:
        # Fetch the request from the database
        request = session.exec(select(Request).where(Request.request_id == request_id).where(Request.status == StatusEnum.Pending)).first()
        if not request:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found")

        # Update the request status to Rejected and add the reason
        request.status = "Rejected"
        request.reason = reason# Corrected: Use dot notation to set the reason field
        session.commit()
        session.refresh(request)
        
        # Prepare the email content
        html = f"""
        <html>
        <body>
            <h1>Request Rejected</h1>
            <p>Request ID: {request.request_id}</p>
            <p>Campus Name: {request.campus_name}</p>
            <p>Date of Request: {request.date_of_request}</p>
            <p>Status: {"Rejected"}</p>
            <p>Reason: {reason}</p>
        </body>
        </html>
        """

        message = MessageSchema(
            subject="Your Request has been Rejected",
            recipients=[request.your_mail_id],
            body=html,
            subtype=MessageType.html
        )

        # Send the email
        fm = FastMail(conf)
        await fm.send_message(message)
        return request

    except Exception as e:
        # Rollback the transaction if an error occurs
        session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {str(e)}")
    
@router.get("/all_issued_items", response_model=List[RequestIssueResponse2], tags=["Central_Stock"])
async def get_issued_items(session: Session = Depends(get_session)):
    issued_items = session.exec(select(Request).where(Request.status == "Approved")).all()
    if issued_items is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No issued items found")
    return issued_items
    