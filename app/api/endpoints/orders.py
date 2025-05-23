from typing import List, Optional
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies.database import get_db
from app.core.security import get_current_active_user, get_current_admin_user
from app.models.order import Order, OrderItem, OrderStatus
from app.models.product import Product
from app.models.user import User
from app.schemas.order import OrderCreate, OrderUpdate, Order as OrderSchema
from app.api.endpoints.whatsapp import send_order_notification

router = APIRouter()

@router.get("/", response_model=List[OrderSchema])
async def read_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 100,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    section: Optional[str] = None,
    order_id: Optional[str] = None,
    status: Optional[OrderStatus] = None,
    client_id: Optional[str] = None,
):
    """
    Retrieve orders with pagination and filtering options
    """
    query = db.query(Order)
    
    # Apply filters if provided
    if start_date:
        query = query.filter(Order.created_at >= datetime.combine(start_date, datetime.min.time()))
    if end_date:
        query = query.filter(Order.created_at <= datetime.combine(end_date, datetime.max.time()))
    if order_id:
        query = query.filter(Order.id == order_id)
    if status:
        query = query.filter(Order.status == status)
    if client_id:
        query = query.filter(Order.client_id == client_id)
    
    # Filter by product section
    if section:
        # This requires a join with OrderItem and Product
        query = (
            query
            .join(OrderItem, Order.id == OrderItem.order_id)
            .join(Product, OrderItem.product_id == Product.id)
            .filter(Product.section == section)
            .distinct()
        )
    
    # Get paginated results
    orders = query.offset(skip).limit(limit).all()
    
    return orders

@router.post("/", response_model=OrderSchema, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_in: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Create a new order
    """
    # Check if there are items in the order
    if not order_in.items or len(order_in.items) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order must contain at least one item",
        )
    
    # Validate that all products exist and have enough stock
    for item in order_in.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {item.product_id} not found",
            )
        
        if product.stock < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Not enough stock for product {product.description}",
            )
    
    # Calculate total amount if not provided
    total_amount = sum(item.quantity * item.unit_price for item in order_in.items)
    
    # Create new order
    db_order = Order(
        client_id=order_in.client_id,
        status=order_in.status,
        total_amount=total_amount,
        notes=order_in.notes,
        created_by=current_user.id,
    )
    
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    # Add order items and update product stock
    for item in order_in.items:
        db_item = OrderItem(
            order_id=db_order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            unit_price=item.unit_price,
            total_price=item.quantity * item.unit_price,
        )
        
        db.add(db_item)
        
        # Update product stock
        product = db.query(Product).filter(Product.id == item.product_id).first()
        product.stock -= item.quantity
        db.add(product)
    
    db.commit()
    db.refresh(db_order)
    
    # Send WhatsApp notification
    try:
        await send_order_notification(db_order.id, db)
    except Exception as e:
        # Log the error but don't fail the order creation
        print(f"Error sending WhatsApp notification: {e}")
    
    return db_order

@router.get("/{order_id}", response_model=OrderSchema)
async def read_order(
    order_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get a specific order by ID
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )
    
    return order

@router.put("/{order_id}", response_model=OrderSchema)
async def update_order(
    order_id: str,
    order_in: OrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Update an order (status and notes only)
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )
    
    # Update order fields
    update_data = order_in.dict(exclude_unset=True)
    old_status = order.status
    
    for field, value in update_data.items():
        setattr(order, field, value)
    
    db.add(order)
    db.commit()
    db.refresh(order)
    
    # Send WhatsApp notification if status changed
    if old_status != order.status:
        try:
            await send_order_notification(order.id, db, status_change=True)
        except Exception as e:
            # Log the error but don't fail the order update
            print(f"Error sending WhatsApp notification: {e}")
    
    return order

@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(
    order_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),  # Only admins can delete
):
    """
    Delete an order
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )
    
    # Restore product stock for each order item
    order_items = db.query(OrderItem).filter(OrderItem.order_id == order_id).all()
    
    for item in order_items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        
        if product:
            product.stock += item.quantity
            db.add(product)
    
    db.delete(order)
    db.commit()
    
    return None