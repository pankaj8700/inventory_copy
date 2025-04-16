from sqlmodel import SQLModel, Field, Relationship
from datetime import date
from typing import List, Optional
from pydantic import EmailStr
import enum
from models.stock import RequestItemResponse, ItemTypeEnum

class StatusEnum(str, enum.Enum):
    Pending = "Pending"
    Approved = "Approved"
    Rejected = "Rejected"

class RequestBase(SQLModel):
    your_mail_id: str
    campus_name: str
    reason: Optional[str]

class Request(RequestBase, table=True):
    request_id: int = Field(default=None, primary_key=True)
    date_of_request: date = Field(default_factory=date.today)
    status: StatusEnum = Field(default=StatusEnum.Pending)
    date_of_approval: Optional[date] = Field(default=None)
    items: List["RequestItem"] = Relationship(back_populates="request")
    issued: List["ReqIssue"] = Relationship(back_populates="request")

class RequestItemBase(SQLModel):
    item_name: str
    qty: int = Field(gt=0, description="Quantity must be greater than 0")
    description: Optional[str] = Field(default=None, description="Description of the item", max_length=100)

class RequestItem(RequestItemBase, table=True):
    item_id: int = Field(default=None, primary_key=True)
    request_id: int = Field(default=None, foreign_key="request.request_id")
    description: Optional[str] = Field(default=None)
    request: Optional["Request"] = Relationship(back_populates="items")

class ReqIssueBase(SQLModel):
    item_name: str
    qty: int
    Item_Type: str

class ReqIssue(ReqIssueBase, table=True):
    issue_id: int = Field(default=None, primary_key=True)
    request_id: int = Field(default=None, foreign_key="request.request_id")
    request: Optional[Request] = Relationship(back_populates="issued")
    
class RequestResponse(SQLModel):
    request_id: int
    campus_name: str
    date_of_request: date
    status: StatusEnum
    items: List[RequestItemBase]
    
class ReqIssueResponse(SQLModel):
    item_name: str
    qty: int
    Item_Type: ItemTypeEnum
    
class RequestIssueResponse(SQLModel):
    request_id: int
    campus_name: str
    date_of_request: date
    status: StatusEnum
    reason: Optional[str]
    items: List[RequestItemBase]
    issued: List[ReqIssueResponse]
    
class RequestIssueResponse2(SQLModel):
    request_id: int
    campus_name: str
    date_of_request: date
    date_of_approval: date
    issued: List[ReqIssueResponse]
    
    
class RequestItemResponse(SQLModel):
    item_name: str
    qty: int = Field(gt=0)
    
class RequestCreate(SQLModel):
    your_mail_id: EmailStr
    campus_name: str
    items: List[RequestItemBase]