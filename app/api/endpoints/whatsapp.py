from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import requests
from typing import Optional

from app.api.dependencies.database import get_db
from app.core.config import settings
from app.core.security import get_current_admin_user
from app.models.user import User
from app.models.order import Order
from app.models.client import Client

router = APIRouter()

async def send_whatsapp_message(phone_number: str, message: str) -> dict:
    """
    Send a WhatsApp message using the WhatsApp Business API
    """
    if not settings.WHATSAPP_API_KEY or not settings.WHATSAPP_PHONE_NUMBER_ID:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="WhatsApp API not configured",
        )
    
    url = f"{settings.WHATSAPP_API_URL}/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
    
    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_API_KEY}",
        "Content-Type": "application/json",
    }
    
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": phone_number,
        "type": "text",
        "text": {
            "body": message
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send WhatsApp message: {str(e)}",
        )

async def send_order_notification(order_id: str, db: Session, status_change: bool = False) -> dict:
    """
    Send a WhatsApp notification about an order
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )
    
    client = db.query(Client).filter(Client.id == order.client_id).first()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found",
        )
    
    # Extract phone number (remove formatting)
    phone_number = ''.join(filter(str.isdigit, client.phone))
    
    # Ensure phone number is in international format
    if not phone_number.startswith('55'):  # Brazil country code
        phone_number = f"55{phone_number}"
    
    # Create message based on whether it's a new order or status update
    if status_change:
        message = (
            f"Olá {client.name},\n\n"
            f"O status do seu pedido #{order.id[:8]} foi atualizado para: {order.status.upper()}.\n\n"
            f"Valor total: R$ {order.total_amount:.2f}\n\n"
            f"Obrigado por escolher a Lu Estilo!"
        )
    else:
        message = (
            f"Olá {client.name},\n\n"
            f"Recebemos seu pedido #{order.id[:8]} com sucesso!\n\n"
            f"Status atual: {order.status.upper()}\n"
            f"Valor total: R$ {order.total_amount:.2f}\n\n"
            f"Agradecemos pela preferência!\n"
            f"Lu Estilo"
        )
    
    return await send_whatsapp_message(phone_number, message)

@router.post("/send-message", status_code=status.HTTP_200_OK)
async def send_custom_message(
    client_id: str,
    message: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),  # Only admins can send custom messages
):
    """
    Send a custom WhatsApp message to a client
    """
    client = db.query(Client).filter(Client.id == client_id).first()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found",
        )
    
    # Extract phone number (remove formatting)
    phone_number = ''.join(filter(str.isdigit, client.phone))
    
    # Ensure phone number is in international format
    if not phone_number.startswith('55'):  # Brazil country code
        phone_number = f"55{phone_number}"
    
    return await send_whatsapp_message(phone_number, message)

@router.post("/send-promotional-message", status_code=status.HTTP_200_OK)
async def send_promotional_message(
    message: str,
    section: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),  # Only admins can send promotional messages
):
    """
    Send a promotional WhatsApp message to all clients or clients who bought from a specific section
    """
    # Get all clients
    query = db.query(Client).filter(Client.is_active == True)
    
    # If section is provided, filter clients who bought products from that section
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No clients found",
        )
    
    results = []
    
    for client in clients:
        # Extract phone number (remove formatting)
        phone_number = ''.join(filter(str.isdigit, client.phone))
        
        # Ensure phone number is in international format
        if not phone_number.startswith('55'):  # Brazil country code
            phone_number = f"55{phone_number}"
        
        # Personalize the message with client name
        personalized_message = f"Olá {client.name},\n\n{message}\n\nAtenciosamente,\nLu Estilo"
        
        try:
            result = await send_whatsapp_message(phone_number, personalized_message)
            results.append({"client_id": client.id, "status": "success", "result": result})
        except Exception as e:
            results.append({"client_id": client.id, "status": "error", "error": str(e)})
    
    return {"message": f"Sent promotional message to {len(clients)} clients", "results": results}