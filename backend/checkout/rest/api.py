from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List
import time
import uuid

import checkout.models.schemas as schemas
from checkout.repository.database import create_tables
from checkout.service.service import (
    MenuService,
    OrderService,
    AdminService,
    get_admin_service,
    get_menu_service,
    get_order_service,
)
from checkout.utils.logging_config import get_logger, set_request_id

# Initialize logger
logger = get_logger(__name__)

# Create database tables
logger.info("Creating database tables...")
create_tables()
logger.info("Database tables created successfully")

app = FastAPI(
    title="Restaurant Checkout API",
    description="A simple kiosk checkout system API",
    version="1.0.0",
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests and responses"""
    # Generate unique request ID
    request_id = str(uuid.uuid4())[:8]
    set_request_id(request_id)

    start_time = time.time()

    logger.info(
        f"[{request_id}] {request.method} {request.url.path} - "
        f"Query params: {dict(request.query_params)} - "
        f"Client: {request.client.host if request.client else 'unknown'}"
    )

    try:
        response = await call_next(request)
        process_time = time.time() - start_time

        logger.info(
            f"[{request_id}] Response: {response.status_code} - "
            f"Time: {process_time:.3f}s"
        )

        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            f"[{request_id}] Request failed: {str(e)} - " f"Time: {process_time:.3f}s"
        )
        raise


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions"""
    request_id = getattr(request.state, "request_id", "unknown")

    if isinstance(exc, HTTPException):
        logger.warning(
            f"[{request_id}] HTTP Exception: {exc.status_code} - {exc.detail}"
        )
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
    else:
        logger.error(
            f"[{request_id}] Unhandled exception: {type(exc).__name__}: {str(exc)}",
            exc_info=True,
        )
        return JSONResponse(
            status_code=500, content={"detail": "Internal server error"}
        )


# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("FastAPI application initialized with middleware and CORS")


@app.get("/", tags=["root"])
async def root():
    """Root endpoint"""
    logger.info("Root endpoint accessed")
    return {"message": "Kiosk Checkout API", "version": "1.0.0"}


@app.get("/api/v1/categories", response_model=List[schemas.Category], tags=["menu"])
async def get_categories(menu_service: MenuService = Depends(get_menu_service)):
    """Get all menu categories"""
    logger.info("Fetching all categories")
    try:
        categories = menu_service.get_categories()
        logger.info(f"Successfully retrieved {len(categories)} categories")
        return categories
    except Exception as e:
        logger.error(f"Failed to retrieve categories: {str(e)}")
        raise


@app.get("/api/v1/menu", response_model=schemas.MenuResponse, tags=["menu"])
async def get_menu(menu_service: MenuService = Depends(get_menu_service)):
    """Get complete menu with categories and items"""
    logger.info("Fetching complete menu")
    try:
        menu = menu_service.get_menu()
        logger.info(
            f"Successfully retrieved menu with {len(menu.categories)} categories and {len(menu.items)} items"
        )
        return menu
    except Exception as e:
        logger.error(f"Failed to retrieve menu: {str(e)}")
        raise


@app.get("/api/v1/items", response_model=List[schemas.Item], tags=["menu"])
async def get_items(
    category_id: int = None, menu_service: MenuService = Depends(get_menu_service)
):
    """Get all items or items by category"""
    if category_id:
        logger.info(f"Fetching items for category_id: {category_id}")
    else:
        logger.info("Fetching all items")

    try:
        items = menu_service.get_items(category_id=category_id)
        logger.info(f"Successfully retrieved {len(items)} items")
        return items
    except Exception as e:
        logger.error(f"Failed to retrieve items: {str(e)}")
        raise


@app.get("/api/v1/items/{item_id}", response_model=schemas.Item, tags=["menu"])
async def get_item(item_id: int, menu_service: MenuService = Depends(get_menu_service)):
    """Get a specific item by ID"""
    logger.info(f"Fetching item with ID: {item_id}")
    try:
        item = menu_service.get_item_by_id(item_id)
        logger.info(f"Successfully retrieved item: {item.name} (ID: {item_id})")
        return item
    except HTTPException as e:
        logger.warning(f"Item not found with ID: {item_id}")
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve item {item_id}: {str(e)}")
        raise


@app.post("/api/v1/orders", response_model=schemas.Order, tags=["orders"])
async def create_order(
    order: schemas.OrderCreate, order_service: OrderService = Depends(get_order_service)
):
    """Submit a new order"""
    logger.info(
        f"Creating new order with {len(order.items)} items, total: ${order.total:.2f}"
    )

    # Log order items (without sensitive payment info)
    item_summary = [f"Item {item.item_id} x{item.quantity}" for item in order.items]
    logger.info(f"Order items: {', '.join(item_summary)}")

    try:
        created_order = order_service.create_order(order)
        logger.info(f"Successfully created order ID: {created_order.id}")
        return created_order
    except HTTPException as e:
        logger.warning(f"Order creation failed with validation error: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Failed to create order: {str(e)}")
        raise


@app.get("/api/v1/orders/{order_id}", response_model=schemas.Order, tags=["orders"])
async def get_order(
    order_id: int, order_service: OrderService = Depends(get_order_service)
):
    """Get order details by ID"""
    logger.info(f"Fetching order with ID: {order_id}")
    try:
        order = order_service.get_order_by_id(order_id)
        logger.info(
            f"Successfully retrieved order ID: {order_id}, total: ${order.total:.2f}"
        )
        return order
    except HTTPException as e:
        logger.warning(f"Order not found with ID: {order_id}")
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve order {order_id}: {str(e)}")
        raise


# Admin endpoints for seeding data
@app.post("/api/v1/admin/categories", response_model=schemas.Category, tags=["admin"])
async def create_category(
    category: schemas.CategoryCreate,
    admin_service: AdminService = Depends(get_admin_service),
):
    """Create a new category (admin only)"""
    logger.info(f"Admin creating new category: {category.name}")
    try:
        created_category = admin_service.create_category(category)
        logger.info(
            f"Successfully created category ID: {created_category.id}, name: {created_category.name}"
        )
        return created_category
    except HTTPException as e:
        logger.warning(f"Category creation failed: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Failed to create category '{category.name}': {str(e)}")
        raise


@app.post("/api/v1/admin/items", response_model=schemas.Item, tags=["admin"])
async def create_item(
    item: schemas.ItemCreate, admin_service: AdminService = Depends(get_admin_service)
):
    """Create a new menu item (admin only)"""
    logger.info(
        f"Admin creating new item: {item.name}, price: ${item.price:.2f}, category_id: {item.category_id}"
    )
    try:
        created_item = admin_service.create_item(item)
        logger.info(
            f"Successfully created item ID: {created_item.id}, name: {created_item.name}"
        )
        return created_item
    except HTTPException as e:
        logger.warning(f"Item creation failed: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Failed to create item '{item.name}': {str(e)}")
        raise
