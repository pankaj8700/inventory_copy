from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from database import get_session
from models.inventory import Request, RequestItem, ReqIssue, StatusEnum, RequestItemResponse, RequestResponse, RequestCreate, RequestIssueResponse
from models.indent import Indent, IndentCreate, IndentResponse
import logging
from fastapi.responses import JSONResponse
from fastapi_mail import FastMail, MessageSchema, MessageType

from utils.mail import conf


router = APIRouter(prefix="/inventory", tags=["Clg_Stock"])

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Request with Items
@router.post("/create_request", response_model=RequestResponse, tags=["Clg_Stock"], description="Warning: If your mail_id is wrong then also your request has been submitted, please don't request again")
async def create_request(request: RequestCreate, session: Session = Depends(get_session)):
    try:
        request_model = Request(your_mail_id=request.your_mail_id,campus_name=request.campus_name)
        session.add(request_model)
        session.commit()
        session.refresh(request_model)

        item_models = [
            RequestItem(
                item_name=item.item_name,
                qty=item.qty,
                request_id=request_model.request_id  # Fixed foreign key
            )
            for item in request.items
        ]
        session.add_all(item_models)
        session.commit()
        session.refresh(request_model)
        
        # Convert request_model to a dictionary
        request_data = request_model.dict()
        # Create an HTML template    
        html = f"""
        <html>
        <body>
            <h1>Request Created</h1>
            <p><strong>Your Request ID:</strong> {request_data['request_id']}</p>
            <p><strong>Campus Name:</strong> {request_data['campus_name']}</p>
            <p><strong>Status:</strong> {"Pending"}</p>
            <h2>Items</h2>
            <ul>
                {"".join([f"<li>{item.item_name}: {item.qty}</li>" for item in item_models])}
            </ul>
        </body>
        </html>
        """
        
        message = MessageSchema(
            subject="Your request has been created",
            recipients=[request.your_mail_id],
            body=html,
            subtype=MessageType.html)

        fm = FastMail(conf)
        await fm.send_message(message)
        logger.info("Email sent successfully")
        
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return JSONResponse(status_code=500, content={"message": "Failed to create request and send email"})

    return request_model


# Fetch Request with Items status

@router.get("/get_request_with_items_status/{request_id}/{campus_name}", response_model=RequestIssueResponse, tags=["Clg_Stock"])
def get_request_with_items(request_id: int, campus_name: str, session: Session = Depends(get_session)):
    request = session.exec(select(Request).where(
        Request.request_id == request_id, Request.campus_name == campus_name)).first()
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Request not found")
    return request

@router.get("/get_history/{campus_name}", tags=["Clg_Stock"])
def get_history(campus_name: str, session: Session = Depends(get_session)):
    try:        
        requests = session.exec(select(Request).where(Request.campus_name == campus_name)).all()
        return requests
    except Exception as e:
        logger.error(f"Failed to get history: {e}")
        return JSONResponse(status_code=500, content={"message": "Failed to get history"})
    


