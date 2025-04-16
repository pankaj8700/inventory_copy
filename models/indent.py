from sqlmodel import SQLModel, Field
from datetime import date
from models.stock import ItemTypeEnum
class IndentBase(SQLModel):
    item_name: str
    Quantity: int
    Department: str
    Item_Type: str

class Indent(IndentBase, table=True):
    indent_id: int = Field(default=None, primary_key=True, index= True)
    date_of_indent: date = Field(default_factory=date.today)
    
    
class IndentCreate(SQLModel):
    item_name: str
    Quantity: int = Field(gt=0)
    Department: str

class IndentResponse(SQLModel):
    indent_id: int
    date_of_indent: date
    item_name: str
    Quantity: int
    Department: str
    Item_Type: ItemTypeEnum
    
class IndentUpdate(SQLModel):
    Quantity: int
    
class IndentResponse(SQLModel):
    indent_id: int
    date_of_indent: date
    item_name: str
    Quantity: int
    Department: str
    Item_Type: ItemTypeEnum