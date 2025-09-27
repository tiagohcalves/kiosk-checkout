# Restaurant Checkout System - Backend

A FastAPI-based REST API for a restaurant checkout system with SQLite database.

## Features

- **Menu Management**: Fetch categories and menu items
- **Order Processing**: Submit and retrieve orders
- **Payment Handling**: Store payment information securely
- **Database**: SQLite with SQLAlchemy ORM

## API Endpoints

### Menu Endpoints
- `GET /api/v1/categories` - Get all categories
- `GET /api/v1/menu` - Get complete menu (categories + items)
- `GET /api/v1/items` - Get all items (optional category filter)
- `GET /api/v1/items/{item_id}` - Get specific item

### Order Endpoints
- `POST /api/v1/orders` - Submit new order
- `GET /api/v1/orders/{order_id}` - Get order details

### Admin Endpoints
- `POST /api/v1/admin/categories` - Create category
- `POST /api/v1/admin/items` - Create menu item

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Seed the database:
```bash
python checkout/repository/seed.py
```

3. Run the server:
```bash
uvicorn checkout.main:app --reload
```

The API will be available at `http://localhost:8000`
API documentation at `http://localhost:8000/docs`

## Database Models

- **Category**: Menu categories (appetizers, mains, etc.)
- **Item**: Menu items with prices and descriptions
- **Order**: Customer orders with totals and payment info
- **OrderItem**: Individual items within an order

## Order Submission Format

```json
{
  "items": [
    {"item_id": 1, "quantity": 2},
    {"item_id": 3, "quantity": 1}
  ],
  "total": 23.97,
  "payment": {
    "card_number": "4532123456789012",
    "card_holder_name": "John Doe",
    "expiry_month": 12,
    "expiry_year": 2025,
    "cvv": "123",
    "billing_address": {
      "street": "123 Main St",
      "city": "Anytown",
      "state": "CA",
      "zip": "12345"
    }
  }
}
```
