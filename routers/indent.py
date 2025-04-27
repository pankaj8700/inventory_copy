# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlmodel import Session, select
# from database import get_session
# from models.indent import Indent, IndentBase, IndentCreate, IndentResponse
# import qrcode
# from fastapi.responses import StreamingResponse
# from io import BytesIO

# router = APIRouter()

# ## indent issue route

# import logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# @router.post("/create_indent_for_Non_Consumable", tags=["Indent"])
# def create_indent(indent: IndentCreate, session: Session = Depends(get_session)):
#     try:
#         indent_model = Indent(
#             item_name=indent.item_name,
#             Quantity=indent.Quantity,
#             Department=indent.Department,
#             Item_Type="Non Consumable"
#         )
#         session.add(indent_model)
#         session.commit()
#         session.refresh(indent_model)

#         # Generate QR code
#         qr = qrcode.QRCode(
#             version=1,
#             error_correction=qrcode.constants.ERROR_CORRECT_L,
#             box_size=5,
#             border=4, 
#         )
#         qr.add_data(f"Indent ID: {indent_model.indent_id},Date of Indent: {indent_model.date_of_indent},Item Name: {indent_model.item_name}, Quantity: {indent_model.Quantity}, Department: {indent_model.Department}, Item Type: {indent_model.Item_Type}")
#         qr.make(fit=True)
#         img = qr.make_image(fill_color="black", back_color="white")

    #     # Save the QR code image to a BytesIO object
    #     img_io = BytesIO()
    #     img.save(img_io, 'PNG')
    #     img_io.seek(0)

    #     return StreamingResponse(img_io, media_type="image/png")
    # except Exception as e:
    #     logger.error(f"Error occurred: {e}")
    #     raise
    
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from database import get_session
from models.indent import Indent, IndentBase, IndentCreate, IndentResponse
import barcode
from barcode.writer import ImageWriter
from fastapi.responses import StreamingResponse
from io import BytesIO

router = APIRouter()

## indent issue route

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.post("/create_indent_for_Non_Consumable", tags=["Indent"])
def create_indent(indent: IndentCreate, session: Session = Depends(get_session)):
    try:
        indent_model = Indent(
            item_name=indent.item_name,
            Quantity=indent.Quantity,
            Department=indent.Department,
            Item_Type="Non Consumable"
        )
        session.add(indent_model)
        session.commit()
        session.refresh(indent_model)

        # Generate Barcode
        barcode_data = f"Indent ID: {indent_model.indent_id}, Date of Indent: {indent_model.date_of_indent}, Item Name: {indent_model.item_name}, Quantity: {indent_model.Quantity}, Department: {indent_model.Department}, Item Type: {indent_model.Item_Type}"
        barcode_class = barcode.get_barcode_class('code128')  # Use Code128 barcode format
        barcode_instance = barcode_class(barcode_data, writer=ImageWriter())

        # Save the barcode image to a BytesIO object
        img_io = BytesIO()
        barcode_instance.write(img_io)
        img_io.seek(0)

        return StreamingResponse(img_io, media_type="image/png")
    except Exception as e:
        logger.error(f"Error occurred: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to generate barcode")

# indent issue for consumable items
@router.post("/create_indent_for_Consumable",response_model=IndentResponse, tags=["Indent"])
async def create_indent(indent: IndentCreate, session: Session = Depends(get_session)):
    indent_model = Indent(
        item_name=indent.item_name,
        Quantity=indent.Quantity,
        Department=indent.Department,
        Item_Type= "Consumable"
    )
    session.add(indent_model)
    session.commit()
    session.refresh(indent_model)
    return indent_model

## get indent detail by indent id

@router.get("/get_indent/{indent_id}", response_model=IndentResponse, tags=["Indent"])
def get_indent(indent_id: int, session: Session = Depends(get_session)):
    indent = session.exec(select(Indent).where(Indent.indent_id == indent_id)).first()
    if not indent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Indent not found")
    return indent