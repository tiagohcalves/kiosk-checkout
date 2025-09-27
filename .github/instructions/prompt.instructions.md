---
applyTo: '**'
---
# GitHub Copilot Instructions - Restaurant Checkout System

## Project Overview
You are helping build a kiosk checkout system with a React frontend and Python backend. This is a take-home assignment project with the following structure:

### Architecture
- **Frontend**: React app with menu browsing, cart management, and checkout
- **Backend**: Python REST API with menu and order endpoints
- **Database**: Relational DB with items, categories, and orders

### Tech Stack Preferences
- **Frontend**: React with hooks, modern JavaScript (ES6+), CSS modules or styled-components
- **Backend**: Python with FastAPI, async/await patterns, Pydantic models
- **Database**: SQLite with SQLAlchemy ORM

## Code Style Guidelines

### General
- Use modern JavaScript features (destructuring, arrow functions, async/await)
- Prefer functional components over class components
- Use meaningful variable names and add JSDoc comments for complex functions
- Implement proper error handling with try-catch blocks
- Follow RESTful conventions for API endpoints

### Frontend Patterns
- Create reusable components (MenuItem, CartItem, LoadingSpinner, ErrorBoundary)
- Use custom hooks for data fetching and cart operations
- Implement loading and error states for all API calls
- Use controlled components for forms
- Add PropTypes or TypeScript for type safety

### Backend Patterns
- Use Pydantic models for request/response validation
- Implement proper HTTP status codes using FastAPI's HTTPException
- Use dependency injection for database sessions
- Add request validation using Pydantic BaseModel classes
- Implement database transactions for order operations
- Use async/await for all database operations

## Key Features to Implement

### Frontend Components
```javascript
// Suggest components like:
- MenuPage: Display categorized menu items
- CartPage: Show cart items with add/remove functionality  
- CheckoutPage: Payment form and order submission
- MenuItem: Individual menu item card
- CartItem: Cart item with quantity controls
- PaymentForm: Form with validation
```

### Backend Endpoints
```python
# Suggest API structure with FastAPI:
@app.get("/api/v1/menu") - Fetch all menu items with categories
@app.get("/api/v1/categories") - Fetch all categories  
@app.post("/api/v1/orders") - Submit new order
@app.get("/api/v1/orders/{order_id}") - Get order details
```

### Database Models
```python
# Reference these SQLAlchemy models:
class Item(Base):
    id, category_id, name, price, image_id

class Category(Base):
    id, name, image

class Order(Base):
    id, timestamp, total, payment_key

class OrderItem(Base):
    id, order_id, item_id, quantity
```