from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from dotenv import load_dotenv
from pydantic import BaseModel
import os
from twilio.rest import Client as TwilioClient

from app.api.dependencies.database import get_db
from app.core.security import get_current_admin_user
from app.models.user import User
from app.models.order import Order
from app.models.client import Client
from app.models.product import Product
from app.models.order import OrderItem

# Load environment variables
load_dotenv()

router = APIRouter()

# Twilio config
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")

def send_whatsapp_message(phone_number: str, message: str) -> dict:
    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_NUMBER]):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Twilio is not properly configured."
        )
    try:
        client = TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        message_response = client.messages.create(
            body=message,
            from_=TWILIO_WHATSAPP_NUMBER,
            to=f"whatsapp:+{phone_number}"
        )
        return {
            "sid": message_response.sid,
            "status": message_response.status,
            "to": message_response.to,
            "message": message,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send WhatsApp message via Twilio: {str(e)}"
        )

async def send_order_notification(order_id: str, db: Session, status_change: bool = False) -> dict:
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    client = db.query(Client).filter(Client.id == order.client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    phone_number = ''.join(filter(str.isdigit, client.phone))
    if not phone_number.startswith('55'):
        phone_number = f"55{phone_number}"

    if status_change:
        message = (
            f"Hello {client.name},\n\n"
            f"The status of your order #{order.id[:8]} has been updated to: {order.status.upper()}.\n"
            f"Total amount: R$ {order.total_amount:.2f}\n\n"
            f"Thank you for choosing Lu Estilo!"
        )
    else:
        message = (
            f"Hello {client.name},\n\n"
            f"We have received your order #{order.id[:8]}!\n"
            f"Current status: {order.status.upper()}\n"
            f"Total amount: R$ {order.total_amount:.2f}\n\n"
            f"Thanks for your preference!\nLu Estilo"
        )

    return send_whatsapp_message(phone_number, message)


class WhatsAppMessagePayload(BaseModel):
    client_id: str
    message: str
@router.post("/send-message", status_code=200)
async def send_custom_message(
    payload: WhatsAppMessagePayload,  # recebe JSON no corpo
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    client_id = payload.client_id
    message = payload.message

    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    phone_number = ''.join(filter(str.isdigit, client.phone))
    if not phone_number.startswith('55'):
        phone_number = f"55{phone_number}"

    return send_whatsapp_message(phone_number, message)

@router.post("/send-promotional-message", status_code=200)
async def send_promotional_message(
    message: str,
    section: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    query = db.query(Client).filter(Client.is_active == True)

    if section:
        query = (
            query
            .join(Order, Client.id == Order.client_id)
            .join(OrderItem, Order.id == OrderItem.order_id)
            .join(Product, OrderItem.product_id == Product.id)
            .filter(Product.section == section)
            .distinct()
        )

    clients = query.all()

    if not clients:
        raise HTTPException(status_code=404, detail="No clients found.")

    results = []

    for client in clients:
        phone_number = ''.join(filter(str.isdigit, client.phone))
        if not phone_number.startswith('55'):
            phone_number = f"55{phone_number}"

        personalized_message = f"Hello {client.name},\n\n{message}\n\nBest regards,\nLu Estilo"

        try:
            result = send_whatsapp_message(phone_number, personalized_message)
            results.append({"client_id": client.id, "status": "success", "result": result})
        except Exception as e:
            results.append({"client_id": client.id, "status": "error", "error": str(e)})

    return {"message": f"Sent promotional message to {len(clients)} clients.", "results": results}
