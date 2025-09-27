from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

import checkout.repository.repository as repository
import checkout.models.schemas as schemas
from checkout.repository.database import get_db, create_tables

# Create database tables
create_tables()

app = FastAPI(
    title="Restaurant Checkout API",
    description="A simple restaurant checkout system API",
    version="1.0.0"
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["root"])
async def root():
    """Root endpoint"""
    return {"message": "Kiosk Checkout API", "version": "1.0.0"}


@app.get("/api/v1/categories", response_model=List[schemas.Category], tags=["menu"])
async def get_categories(db: Session = Depends(get_db)):
    """Get all menu categories"""
    categories = repository.get_categories(db)
    return categories


@app.get("/api/v1/menu", response_model=schemas.MenuResponse, tags=["menu"])
async def get_menu(db: Session = Depends(get_db)):
    """Get complete menu with categories and items"""
    categories = repository.get_categories(db)
    items = repository.get_items(db)
    
    return schemas.MenuResponse(categories=categories, items=items)


@app.get("/api/v1/items", response_model=List[schemas.Item], tags=["menu"])
async def get_items(category_id: int = None, db: Session = Depends(get_db)):
    """Get all items or items by category"""
    items = repository.get_items(db, category_id=category_id)
    return items


@app.get("/api/v1/items/{item_id}", response_model=schemas.Item, tags=["menu"])
async def get_item(item_id: int, db: Session = Depends(get_db)):
    """Get a specific item by ID"""
    item = repository.get_item_by_id(db, item_id=item_id)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    return item


@app.post("/api/v1/orders", response_model=schemas.Order, tags=["orders"])
async def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    """Submit a new order"""
    try:
        # Validate that all items exist and calculate total
        calculated_total = 0
        for order_item in order.items:
            item = repository.get_item_by_id(db, order_item.item_id)
            if not item:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Item with ID {order_item.item_id} not found"
                )
            calculated_total += item.price * order_item.quantity
        
        # Verify the total matches (with small tolerance for floating point)
        if abs(calculated_total - order.total) > 0.01:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Total mismatch. Expected: {calculated_total}, Received: {order.total}"
            )
        
        db_order = repository.create_order(db=db, order=order)
        return db_order
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing the order"
        )


@app.get("/api/v1/orders/{order_id}", response_model=schemas.Order, tags=["orders"])
async def get_order(order_id: int, db: Session = Depends(get_db)):
    """Get order details by ID"""
    order = repository.get_order_by_id(db, order_id=order_id)
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    return order


# Admin endpoints for seeding data
@app.post("/api/v1/admin/categories", response_model=schemas.Category, tags=["admin"])
async def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_db)):
    """Create a new category (admin only)"""
    try:
        return repository.create_category(db=db, category=category)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category creation failed"
        )


@app.post("/api/v1/admin/items", response_model=schemas.Item, tags=["admin"])
async def create_item(item: schemas.ItemCreate, db: Session = Depends(get_db)):
    """Create a new menu item (admin only)"""
    try:
        return repository.create_item(db=db, item=item)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Item creation failed"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
