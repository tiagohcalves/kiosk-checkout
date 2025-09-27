# Service imports for backward compatibility
from checkout.service.payment_service import FakePaymentService
from checkout.service.menu_service import MenuService, get_menu_service
from checkout.service.order_service import OrderService, get_order_service
from checkout.service.admin_service import AdminService, get_admin_service

# Re-export all services and dependencies for backward compatibility
__all__ = [
    "FakePaymentService",
    "MenuService",
    "OrderService", 
    "AdminService",
    "get_menu_service",
    "get_order_service",
    "get_admin_service",
]
