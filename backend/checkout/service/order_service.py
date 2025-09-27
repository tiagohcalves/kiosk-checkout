from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status

from checkout.repository.database import get_db
import checkout.repository.repository as repository
import checkout.models.schemas as schemas
from checkout.service.payment_service import FakePaymentService
from checkout.utils.logging_config import get_logger

logger = get_logger(__name__)


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


# Service dependency
def get_order_service(db: Session = Depends(get_db)) -> OrderService:
    """Dependency to get OrderService instance"""
    return OrderService(db)