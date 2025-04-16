from sqlmodel import SQLModel, Field, Relationship
from datetime import date
from typing import List, Optional
import enum

class ItemTypeEnum(str, enum.Enum):
    CONSUMABLE = "Consumable"
    NON_CONSUMABLE = "Non Consumable"
    
class StatusEnum(str,enum.Enum):
    Pending= "Pending"
    Approved= "Approved"
    Rejected= "Rejected"

class StockBase(SQLModel):
    gem_id: int = Field(primary_key=True)
    vendor_name: str
    date_of_order: date
    date_of_purchase: date

class Stock(StockBase, table=True):
    date_of_adding: date = Field(default_factory=date.today)
    items: List["Item"] = Relationship(back_populates="stock")

class ItemBase(SQLModel):
    item_name: str
    item_type: str
    item_quantity: int
    item_price: float

class Item(ItemBase, table=True):
    item_id: int = Field(default=None, primary_key=True)
    stock_id: Optional[int] = Field(default=None, foreign_key="stock.gem_id")
    stock: Optional[Stock] = Relationship(back_populates="items")
    
class ItemCreate(SQLModel):
    item_name: str
    item_type: ItemTypeEnum
    item_quantity: int = Field(gt=0)
    item_price: float = Field(gt=0)

class StockCreate(SQLModel):
    gem_id: int
    vendor_name: str
    date_of_order: date
    date_of_purchase: date
    items: List[ItemCreate]
    
class ItemResponse(SQLModel):
    item_id: int
    item_name: str
    item_type: ItemTypeEnum
    item_quantity: int
    item_price: float
    
class StockResponse(SQLModel):
    gem_id: int
    vendor_name: str
    date_of_order: date
    date_of_purchase: date
    date_of_adding: date
    items: List[ItemResponse]
    
class RequestItemResponse(SQLModel):
    item_name: str
    qty: int
    
class RequestResponse(SQLModel):
    request_id: int
    campus_name: str
    date_of_request: date
    status: StatusEnum
    items: List[RequestItemResponse]
    
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
    items: List[RequestItemResponse]
    issued: List[ReqIssueResponse]
    
class ReqIssueBase(SQLModel):
    item_name: str
    qty: int = Field(gt=0)
    Item_Type: ItemTypeEnum
    
class CountsResponse(SQLModel):
    Approved: int
    Rejected: int
    Pending: int