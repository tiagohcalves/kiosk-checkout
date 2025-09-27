from sqlalchemy.orm import Session
import json
import hashlib
from typing import List

import checkout.models.schemas as schemas
import checkout.models.models as models


def get_categories(db: Session) -> List[models.Category]:
    """Fetch all categories"""
    return db.query(models.Category).all()


def get_items(db: Session, category_id: int = None) -> List[models.Item]:
    """Fetch all items or items by category"""
    query = db.query(models.Item)
    if category_id:
        query = query.filter(models.Item.category_id == category_id)
    return query.all()


def get_item_by_id(db: Session, item_id: int) -> models.Item:
    """Get a specific item by ID"""
    return db.query(models.Item).filter(models.Item.id == item_id).first()


def create_order(db: Session, order: schemas.OrderCreate) -> models.Order:
    """Create a new order with order items"""
    try:
        # Generate payment key (hash of sensitive payment data)
        payment_key = hashlib.sha256(
            f"{order.payment.card_number[-4:]}{order.payment.card_holder_name}".encode()
        ).hexdigest()[:16]

        # Store payment data as JSON (in real app, encrypt this)
        payment_data = order.payment.model_dump()
        # Mask sensitive data for storage
        payment_data["card_number"] = (
            "**** **** **** " + payment_data["card_number"][-4:]
        )

        # Create order
        db_order = models.Order(
            total=order.total,
            payment_key=payment_key,
            payment_data=json.dumps(payment_data),
        )
        db.add(db_order)
        db.flush()  # Get the order ID

        # Create order items
        for item_data in order.items:
            # Verify item exists
            item = get_item_by_id(db, item_data.item_id)
            if not item:
                raise ValueError(f"Item with ID {item_data.item_id} not found")

            db_order_item = models.OrderItem(
                order_id=db_order.id,
                item_id=item_data.item_id,
                quantity=item_data.quantity,
            )
            db.add(db_order_item)

        db.commit()
        db.refresh(db_order)
        return db_order

    except Exception as e:
        db.rollback()
        raise e


def get_order_by_id(db: Session, order_id: int) -> models.Order:
    """Get order by ID with all related data"""
    return db.query(models.Order).filter(models.Order.id == order_id).first()


def create_category(db: Session, category: schemas.CategoryCreate) -> models.Category:
    """Create a new category"""
    db_category = models.Category(name=category.name, image=category.image)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


def create_item(db: Session, item: schemas.ItemCreate) -> models.Item:
    """Create a new menu item"""
    db_item = models.Item(
        name=item.name,
        price=item.price,
        image_id=item.image_id,
        category_id=item.category_id,
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item
