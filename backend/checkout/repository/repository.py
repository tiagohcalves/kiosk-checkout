from sqlalchemy.orm import Session
import json
import hashlib
from typing import List

import checkout.models.schemas as schemas
import checkout.models.models as models
from checkout.utils.logging_config import get_logger

logger = get_logger(__name__)


def get_categories(db: Session) -> List[models.Category]:
    """Fetch all categories"""
    logger.debug("Repository: Fetching all categories from database")
    try:
        categories = db.query(models.Category).all()
        logger.debug(
            f"Repository: Retrieved {len(categories)} categories from database"
        )
        return categories
    except Exception as e:
        logger.error(f"Repository: Failed to fetch categories: {str(e)}")
        raise


def get_items(db: Session, category_id: int = None) -> List[models.Item]:
    """Fetch all items or items by category"""
    if category_id:
        logger.debug(
            f"Repository: Fetching items for category {category_id} from database"
        )
    else:
        logger.debug("Repository: Fetching all items from database")

    try:
        query = db.query(models.Item)
        if category_id:
            query = query.filter(models.Item.category_id == category_id)
        items = query.all()
        logger.debug(f"Repository: Retrieved {len(items)} items from database")
        return items
    except Exception as e:
        logger.error(f"Repository: Failed to fetch items: {str(e)}")
        raise


def get_item_by_id(db: Session, item_id: int) -> models.Item:
    """Get a specific item by ID"""
    logger.debug(f"Repository: Fetching item with ID {item_id} from database")
    try:
        item = db.query(models.Item).filter(models.Item.id == item_id).first()
        if item:
            logger.debug(f"Repository: Found item '{item.name}' (ID: {item_id})")
        else:
            logger.debug(f"Repository: No item found with ID {item_id}")
        return item
    except Exception as e:
        logger.error(f"Repository: Failed to fetch item {item_id}: {str(e)}")
        raise


def create_order(db: Session, order: schemas.OrderCreate) -> models.Order:
    """Create a new order with order items"""
    logger.info(
        f"Repository: Creating order with {len(order.items)} items, total: ${order.total:.2f}"
    )

    try:
        logger.debug("Repository: Starting database transaction for order creation")

        # Generate payment key (hash of sensitive payment data)
        logger.debug("Repository: Generating payment key")
        payment_key = hashlib.sha256(
            f"{order.payment.card_number[-4:]}{order.payment.card_holder_name}".encode()
        ).hexdigest()[:16]
        logger.debug(f"Repository: Generated payment key: {payment_key}")

        # Store payment data as JSON (in real app, encrypt this)
        payment_data = order.payment.model_dump()
        # Mask sensitive data for storage
        payment_data["card_number"] = (
            "**** **** **** " + payment_data["card_number"][-4:]
        )
        logger.debug("Repository: Processed payment data (sensitive info masked)")

        # Create order
        logger.debug("Repository: Creating order record")
        db_order = models.Order(
            total=order.total,
            payment_key=payment_key,
            payment_data=json.dumps(payment_data),
        )
        db.add(db_order)
        db.flush()  # Get the order ID
        logger.debug(f"Repository: Created order record with ID: {db_order.id}")

        # Create order items
        logger.debug(f"Repository: Creating {len(order.items)} order items")
        for i, item_data in enumerate(order.items, 1):
            logger.debug(
                f"Repository: Processing order item {i}/{len(order.items)}: item_id={item_data.item_id}, quantity={item_data.quantity}"
            )

            # Verify item exists
            item = get_item_by_id(db, item_data.item_id)
            if not item:
                logger.error(
                    f"Repository: Item not found during order creation: {item_data.item_id}"
                )
                raise ValueError(f"Item with ID {item_data.item_id} not found")

            db_order_item = models.OrderItem(
                order_id=db_order.id,
                item_id=item_data.item_id,
                quantity=item_data.quantity,
            )
            db.add(db_order_item)
            logger.debug(
                f"Repository: Added order item for '{item.name}' x{item_data.quantity}"
            )

        logger.debug("Repository: Committing transaction")
        db.commit()
        db.refresh(db_order)
        logger.info(f"Repository: Successfully created order ID: {db_order.id}")
        return db_order

    except Exception as e:
        logger.error(
            f"Repository: Order creation failed, rolling back transaction: {str(e)}"
        )
        db.rollback()
        raise e


def get_order_by_id(db: Session, order_id: int) -> models.Order:
    """Get order by ID with all related data"""
    logger.debug(f"Repository: Fetching order with ID {order_id} from database")
    try:
        order = db.query(models.Order).filter(models.Order.id == order_id).first()
        if order:
            logger.debug(
                f"Repository: Found order ID {order_id}, total: ${order.total:.2f}"
            )
        else:
            logger.debug(f"Repository: No order found with ID {order_id}")
        return order
    except Exception as e:
        logger.error(f"Repository: Failed to fetch order {order_id}: {str(e)}")
        raise


def create_category(db: Session, category: schemas.CategoryCreate) -> models.Category:
    """Create a new category"""
    logger.debug(f"Repository: Creating category '{category.name}' in database")
    try:
        db_category = models.Category(name=category.name, image=category.image)
        db.add(db_category)
        logger.debug("Repository: Committing category creation")
        db.commit()
        db.refresh(db_category)
        logger.debug(
            f"Repository: Successfully created category ID: {db_category.id}, name: '{db_category.name}'"
        )
        return db_category
    except Exception as e:
        logger.error(
            f"Repository: Failed to create category '{category.name}': {str(e)}"
        )
        db.rollback()
        raise


def create_item(db: Session, item: schemas.ItemCreate) -> models.Item:
    """Create a new menu item"""
    logger.debug(
        f"Repository: Creating item '{item.name}' in database, price: ${item.price:.2f}, category_id: {item.category_id}"
    )
    try:
        db_item = models.Item(
            name=item.name,
            price=item.price,
            image_id=item.image_id,
            category_id=item.category_id,
        )
        db.add(db_item)
        logger.debug("Repository: Committing item creation")
        db.commit()
        db.refresh(db_item)
        logger.debug(
            f"Repository: Successfully created item ID: {db_item.id}, name: '{db_item.name}'"
        )
        return db_item
    except Exception as e:
        logger.error(f"Repository: Failed to create item '{item.name}': {str(e)}")
        db.rollback()
        raise
