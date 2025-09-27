import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from checkout.main import app
from checkout.models.models import Base
from checkout.repository.database import get_db

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
def client():
    """Create test client"""
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db():
    """Create fresh database session for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def sample_category_data():
    """Sample category data for testing"""
    return {
        "name": "Burgers",
        "image": "burgers.jpg"
    }

@pytest.fixture
def sample_item_data():
    """Sample item data for testing"""
    return {
        "name": "Classic Burger",
        "price": 12.99,
        "image_id": "burger1.jpg",
        "category_id": 1
    }

@pytest.fixture
def sample_order_data():
    """Sample order data for testing"""
    return {
        "items": [
            {"item_id": 1, "quantity": 2},
            {"item_id": 2, "quantity": 1}
        ],
        "total": 25.98,
        "payment": {
            "card_number": "1234567890123456",
            "card_holder_name": "John Doe",
            "expiry_month": 12,
            "expiry_year": 2025,
            "cvv": "123",
            "billing_address": {
                "street": "123 Main St",
                "city": "Anytown",
                "zip": "12345"
            }
        }
    }

@pytest.fixture
def setup_test_data(db):
    """Setup test data in database"""
    from checkout.models.models import Category, Item
    
    # Create test category
    category = Category(name="Test Category", image="test.jpg")
    db.add(category)
    db.commit()
    db.refresh(category)
    
    # Create test items
    item1 = Item(
        name="Test Item 1",
        price=10.99,
        image_id="item1.jpg",
        category_id=category.id
    )
    item2 = Item(
        name="Test Item 2",
        price=15.99,
        image_id="item2.jpg", 
        category_id=category.id
    )
    
    db.add(item1)
    db.add(item2)
    db.commit()
    db.refresh(item1)
    db.refresh(item2)
    
    return {
        "category": category,
        "items": [item1, item2]
    }
