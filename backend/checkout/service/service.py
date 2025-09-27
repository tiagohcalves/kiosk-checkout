from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from typing import List

from checkout.repository.database import get_db
import checkout.repository.repository as repository
import checkout.models.schemas as schemas
from checkout.utils.logging_config import get_logger

logger = get_logger(__name__)


class FakePaymentService:
    """A mock payment processing service"""

    @staticmethod
    def process_payment(amount: float, payment_data: dict) -> bool:
        """Simulate payment processing"""
        logger.debug(f"Processing payment of ${amount:.2f} with data: {payment_data}")
        return True


class MenuService:
    """Service class for menu-related operations"""

    def __init__(self, db: Session):
        """Initialize the service with a database session"""
        self.db = db

    def get_categories(self) -> List[schemas.Category]:
        """Get all menu categories"""
        logger.debug("MenuService: Fetching all categories")
        try:
            categories = repository.get_categories(self.db)
            logger.debug(f"MenuService: Retrieved {len(categories)} categories")
            return categories
        except Exception as e:
            logger.error(f"MenuService: Failed to get categories: {str(e)}")
            raise

    def get_menu(self) -> schemas.MenuResponse:
        """Get complete menu with categories and items"""
        logger.debug("MenuService: Fetching complete menu")
        try:
            categories = repository.get_categories(self.db)
            items = repository.get_items(self.db)
            logger.debug(
                f"MenuService: Retrieved {len(categories)} categories and {len(items)} items"
            )
            return schemas.MenuResponse(categories=categories, items=items)
        except Exception as e:
            logger.error(f"MenuService: Failed to get menu: {str(e)}")
            raise

    def get_items(self, category_id: int = None) -> List[schemas.Item]:
        """Get all items or items by category"""
        if category_id:
            logger.debug(f"MenuService: Fetching items for category {category_id}")
        else:
            logger.debug("MenuService: Fetching all items")

        try:
            items = repository.get_items(self.db, category_id=category_id)
            logger.debug(f"MenuService: Retrieved {len(items)} items")
            return items
        except Exception as e:
            logger.error(f"MenuService: Failed to get items: {str(e)}")
            raise

    def get_item_by_id(self, item_id: int) -> schemas.Item:
        """Get a specific item by ID"""
        logger.debug(f"MenuService: Fetching item with ID {item_id}")
        try:
            item = repository.get_item_by_id(self.db, item_id=item_id)
            if item is None:
                logger.warning(f"MenuService: Item not found with ID {item_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
                )
            logger.debug(f"MenuService: Retrieved item '{item.name}' (ID: {item_id})")
            return item
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"MenuService: Failed to get item {item_id}: {str(e)}")
            raise


class OrderService:
    """Service class for order-related operations"""

    def __init__(self, db: Session):
        """Initialize the service with a database session"""
        self.db = db
        logger.debug("OrderService initialized")

    def create_order(self, order: schemas.OrderCreate) -> schemas.Order:
        """Submit a new order with validation"""
        logger.info(
            f"OrderService: Creating order with {len(order.items)} items, total: ${order.total:.2f}"
        )

        try:
            # Validate that all items exist and calculate total
            calculated_total = 0
            logger.debug("OrderService: Starting order validation")

            for order_item in order.items:
                logger.debug(
                    f"OrderService: Validating item {order_item.item_id} x{order_item.quantity}"
                )
                item = repository.get_item_by_id(self.db, order_item.item_id)
                if not item:
                    logger.warning(
                        f"OrderService: Item not found during order validation: {order_item.item_id}"
                    )
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Item with ID {order_item.item_id} not found",
                    )

                item_total = item.price * order_item.quantity
                calculated_total += item_total
                logger.debug(
                    f"OrderService: Item '{item.name}' - ${item.price:.2f} x{order_item.quantity} = ${item_total:.2f}"
                )

            logger.debug(
                f"OrderService: Calculated total: ${calculated_total:.2f}, Provided total: ${order.total:.2f}"
            )

            # Verify the total matches (with small tolerance for floating point)
            if abs(calculated_total - order.total) > 0.01:
                logger.warning(
                    f"OrderService: Total mismatch - Expected: ${calculated_total:.2f}, Received: ${order.total:.2f}"
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Total mismatch. Expected: {calculated_total}, Received: {order.total}",
                )

            # Simulate payment processing
            if not FakePaymentService.process_payment(order.total, order.payment):
                logger.warning("OrderService: Payment processing failed")
                raise HTTPException(
                    status_code=status.HTTP_402_PAYMENT_REQUIRED,
                    detail="Payment processing failed",
                )

            logger.debug("OrderService: Order validation successful, creating order")
            db_order = repository.create_order(db=self.db, order=order)
            logger.info(f"OrderService: Successfully created order ID: {db_order.id}")
            return db_order

        except HTTPException:
            raise
        except ValueError as e:
            logger.error(f"OrderService: Validation error: {str(e)}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except Exception as e:
            logger.error(
                f"OrderService: Unexpected error creating order: {str(e)}",
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while processing the order",
            )

    def get_order_by_id(self, order_id: int) -> schemas.Order:
        """Get order details by ID"""
        logger.debug(f"OrderService: Fetching order with ID {order_id}")
        try:
            order = repository.get_order_by_id(self.db, order_id=order_id)
            if order is None:
                logger.warning(f"OrderService: Order not found with ID {order_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
                )
            logger.debug(
                f"OrderService: Retrieved order ID {order_id}, total: ${order.total:.2f}"
            )
            return order
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"OrderService: Failed to get order {order_id}: {str(e)}")
            raise


class AdminService:
    """Service class for admin operations"""

    def __init__(self, db: Session):
        """Initialize the service with a database session"""
        self.db = db
        logger.debug("AdminService initialized")

    def create_category(self, category: schemas.CategoryCreate) -> schemas.Category:
        """Create a new category with validation"""
        logger.info(f"AdminService: Creating category '{category.name}'")

        try:
            # Basic validation
            logger.debug("AdminService: Starting category validation")
            if not category.name or not category.name.strip():
                logger.warning("AdminService: Category name is empty")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Category name is required and cannot be empty",
                )

            # Check name length
            if len(category.name.strip()) > 100:
                logger.warning(
                    f"AdminService: Category name too long: {len(category.name.strip())} characters"
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Category name cannot exceed 100 characters",
                )

            # Check for duplicate category names
            logger.debug("AdminService: Checking for duplicate category names")
            existing_categories = repository.get_categories(self.db)
            if any(
                cat.name.lower() == category.name.strip().lower()
                for cat in existing_categories
            ):
                logger.warning(
                    f"AdminService: Duplicate category name: '{category.name}'"
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="A category with this name already exists",
                )

            # Validate image field if provided
            if category.image and len(category.image) > 255:
                logger.warning(
                    f"AdminService: Image filename too long: {len(category.image)} characters"
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Image filename cannot exceed 255 characters",
                )

            logger.debug(
                "AdminService: Category validation successful, creating category"
            )
            created_category = repository.create_category(db=self.db, category=category)
            logger.info(
                f"AdminService: Successfully created category ID: {created_category.id}, name: '{created_category.name}'"
            )
            return created_category

        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                f"AdminService: Unexpected error creating category: {str(e)}",
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while creating the category",
            )

    def create_item(self, item: schemas.ItemCreate) -> schemas.Item:
        """Create a new menu item with validation"""
        logger.info(
            f"AdminService: Creating item '{item.name}', price: ${item.price:.2f}, category_id: {item.category_id}"
        )

        try:
            # Basic validation
            logger.debug("AdminService: Starting item validation")
            if not item.name or not item.name.strip():
                logger.warning("AdminService: Item name is empty")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Item name is required and cannot be empty",
                )

            # Check name length
            if len(item.name.strip()) > 200:
                logger.warning(
                    f"AdminService: Item name too long: {len(item.name.strip())} characters"
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Item name cannot exceed 200 characters",
                )

            # Validate price
            if item.price <= 0:
                logger.warning(f"AdminService: Invalid price: ${item.price:.2f}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Price must be greater than 0",
                )

            # Validate category exists
            logger.debug(
                f"AdminService: Validating category exists: {item.category_id}"
            )
            categories = repository.get_categories(self.db)
            if not any(cat.id == item.category_id for cat in categories):
                logger.warning(f"AdminService: Category not found: {item.category_id}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Category with ID {item.category_id} does not exist",
                )

            # Check for duplicate item names within the same category
            logger.debug(
                f"AdminService: Checking for duplicate item names in category {item.category_id}"
            )
            existing_items = repository.get_items(self.db, category_id=item.category_id)
            if any(
                existing_item.name.lower() == item.name.strip().lower()
                for existing_item in existing_items
            ):
                logger.warning(
                    f"AdminService: Duplicate item name in category {item.category_id}: '{item.name}'"
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="An item with this name already exists in this category",
                )

            if item.image_id and len(item.image_id) > 255:
                logger.warning(
                    f"AdminService: Image ID too long: {len(item.image_id)} characters"
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Image ID cannot exceed 255 characters",
                )

            logger.debug("AdminService: Item validation successful, creating item")
            created_item = repository.create_item(db=self.db, item=item)
            logger.info(
                f"AdminService: Successfully created item ID: {created_item.id}, name: '{created_item.name}'"
            )
            return created_item

        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                f"AdminService: Unexpected error creating item: {str(e)}", exc_info=True
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while creating the item",
            )


# Service dependencies
def get_menu_service(db: Session = Depends(get_db)) -> MenuService:
    """Dependency to get MenuService instance"""
    return MenuService(db)


def get_order_service(db: Session = Depends(get_db)) -> OrderService:
    """Dependency to get OrderService instance"""
    return OrderService(db)


def get_admin_service(db: Session = Depends(get_db)) -> AdminService:
    """Dependency to get AdminService instance"""
    return AdminService(db)
