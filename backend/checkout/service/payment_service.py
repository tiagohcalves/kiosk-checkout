from checkout.utils.logging_config import get_logger

logger = get_logger(__name__)


class FakePaymentService:
    """A mock payment processing service"""

    @staticmethod
    def process_payment(amount: float, payment_data: dict) -> bool:
        """Simulate payment processing"""
        logger.debug(f"Processing payment of ${amount:.2f} with data: {payment_data}")
        return True