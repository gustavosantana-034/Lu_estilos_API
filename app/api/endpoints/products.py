from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies.database import get_db
from app.core.security import get_current_active_user, get_current_admin_user
from app.models.product import Product, ProductImage
from app.models.user import User
from app.schemas.product import ProductCreate, ProductUpdate, Product as ProductSchema

router = APIRouter()

@router.get("/", response_model=List[ProductSchema])
async def read_products(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    available: Optional[bool] = None,
):
    """
    Retrieve products with pagination and filtering options
    """
    query = db.query(Product)
    
    # Apply filters if provided
    if category:
        query = query.filter(Product.section == category)
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    if available is not None:
        if available:
            query = query.filter(Product.stock > 0, Product.is_active == True)
        else:
            query = query.filter((Product.stock == 0) | (Product.is_active == False))
    
    # Get paginated results
    products = query.offset(skip).limit(limit).all()
    
    return products

@router.post("/", response_model=ProductSchema, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_in: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Create a new product
    """
    # Check if product with this barcode already exists
    if product_in.barcode and db.query(Product).filter(Product.barcode == product_in.barcode).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Barcode already registered",
        )
    
    # Create new product
    db_product = Product(
        description=product_in.description,
        price=product_in.price,
        barcode=product_in.barcode,
        section=product_in.section,
        stock=product_in.stock,
        expiration_date=product_in.expiration_date,
        is_active=product_in.is_active,
        created_by=current_user.id,
    )
    
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    
    # Add product images if provided
    if product_in.images:
        for image_data in product_in.images:
            db_image = ProductImage(
                product_id=db_product.id,
                image_url=image_data.image_url,
                is_primary=image_data.is_primary,
            )
            db.add(db_image)
        
        db.commit()
        db.refresh(db_product)
    
    return db_product

@router.get("/{product_id}", response_model=ProductSchema)
async def read_product(
    product_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get a specific product by ID
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    
    return product

@router.put("/{product_id}", response_model=ProductSchema)
async def update_product(
    product_id: str,
    product_in: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Update a product
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    
    # Check barcode uniqueness if updating barcode
    if product_in.barcode and product_in.barcode != product.barcode:
        if db.query(Product).filter(Product.barcode == product_in.barcode).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Barcode already registered",
            )
    
    # Update product fields
    update_data = product_in.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(product, field, value)
    
    db.add(product)
    db.commit()
    db.refresh(product)
    
    return product

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),  # Only admins can delete
):
    """
    Delete a product
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    
    db.delete(product)
    db.commit()
    
    return None