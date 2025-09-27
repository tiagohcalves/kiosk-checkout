import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session
from checkout.models import models, schemas
from checkout.repository import repository


class TestRepository:
    """Test cases for repository functions"""

    def test_get_categories(self, db, setup_test_data):
        """Test getting all categories"""
        test_data = setup_test_data
        categories = repository.get_categories(db)

        assert len(categories) == 1
        assert categories[0].name == "Test Category"
        assert categories[0].image == "test.jpg"

    def test_get_items_all(self, db, setup_test_data):
        """Test getting all items"""
        test_data = setup_test_data
        items = repository.get_items(db)

        assert len(items) == 2
        assert items[0].name == "Test Item 1"
        assert items[1].name == "Test Item 2"

    def test_get_items_by_category(self, db, setup_test_data):
        """Test getting items by category"""
        test_data = setup_test_data
        category_id = test_data["category"].id
        items = repository.get_items(db, category_id=category_id)

        assert len(items) == 2
        for item in items:
            assert item.category_id == category_id

    def test_get_item_by_id_exists(self, db, setup_test_data):
        """Test getting item by ID when it exists"""
        test_data = setup_test_data
        item_id = test_data["items"][0].id
        item = repository.get_item_by_id(db, item_id)

        assert item is not None
        assert item.id == item_id
        assert item.name == "Test Item 1"

    def test_get_item_by_id_not_exists(self, db):
        """Test getting item by ID when it doesn't exist"""
        item = repository.get_item_by_id(db, 999)
        assert item is None

    def test_create_category(self, db):
        """Test creating a new category"""
        category_data = schemas.CategoryCreate(name="New Category", image="new.jpg")
        category = repository.create_category(db, category_data)

        assert category.id is not None
        assert category.name == "New Category"
        assert category.image == "new.jpg"

    def test_create_item(self, db, setup_test_data):
        """Test creating a new item"""
        test_data = setup_test_data
        category_id = test_data["category"].id

        item_data = schemas.ItemCreate(
            name="New Item",
            price=20.99,
            image_id="new_item.jpg",
            category_id=category_id,
        )
        item = repository.create_item(db, item_data)

        assert item.id is not None
        assert item.name == "New Item"
        assert item.price == 20.99
        assert item.category_id == category_id

    def test_create_order_success(self, db, setup_test_data):
        """Test creating a successful order"""
        test_data = setup_test_data
        items = test_data["items"]

        order_data = schemas.OrderCreate(
            items=[
                schemas.OrderItemCreate(item_id=items[0].id, quantity=2),
                schemas.OrderItemCreate(item_id=items[1].id, quantity=1),
            ],
            total=37.97,  # (10.99 * 2) + (15.99 * 1)
            payment=schemas.PaymentData(
                card_number="1234567890123456",
                card_holder_name="John Doe",
                expiry_month=12,
                expiry_year=2025,
                cvv="123",
            ),
        )

        order = repository.create_order(db, order_data)

        assert order.id is not None
        assert order.total == 37.97
        assert order.payment_key is not None
        assert len(order.order_items) == 2

    def test_create_order_invalid_item(self, db):
        """Test creating order with invalid item ID"""
        order_data = schemas.OrderCreate(
            items=[schemas.OrderItemCreate(item_id=999, quantity=1)],
            total=10.99,
            payment=schemas.PaymentData(
                card_number="1234567890123456",
                card_holder_name="John Doe",
                expiry_month=12,
                expiry_year=2025,
                cvv="123",
            ),
        )

        with pytest.raises(ValueError, match="Item with ID 999 not found"):
            repository.create_order(db, order_data)

    def test_get_order_by_id_exists(self, db, setup_test_data):
        """Test getting order by ID when it exists"""
        test_data = setup_test_data
        items = test_data["items"]

        # First create an order
        order_data = schemas.OrderCreate(
            items=[schemas.OrderItemCreate(item_id=items[0].id, quantity=1)],
            total=10.99,
            payment=schemas.PaymentData(
                card_number="1234567890123456",
                card_holder_name="John Doe",
                expiry_month=12,
                expiry_year=2025,
                cvv="123",
            ),
        )
        created_order = repository.create_order(db, order_data)

        # Then retrieve it
        retrieved_order = repository.get_order_by_id(db, created_order.id)

        assert retrieved_order is not None
        assert retrieved_order.id == created_order.id
        assert retrieved_order.total == 10.99

    def test_get_order_by_id_not_exists(self, db):
        """Test getting order by ID when it doesn't exist"""
        order = repository.get_order_by_id(db, 999)
        assert order is None

    def test_payment_key_generation(self, db, setup_test_data):
        """Test that payment key is generated correctly"""
        test_data = setup_test_data
        items = test_data["items"]

        order_data = schemas.OrderCreate(
            items=[schemas.OrderItemCreate(item_id=items[0].id, quantity=1)],
            total=10.99,
            payment=schemas.PaymentData(
                card_number="1234567890123456",
                card_holder_name="John Doe",
                expiry_month=12,
                expiry_year=2025,
                cvv="123",
            ),
        )

        order = repository.create_order(db, order_data)

        # Payment key should be 16 character hash
        assert len(order.payment_key) == 16
        assert order.payment_key.isalnum()

    def test_payment_data_masking(self, db, setup_test_data):
        """Test that sensitive payment data is masked"""
        test_data = setup_test_data
        items = test_data["items"]

        order_data = schemas.OrderCreate(
            items=[schemas.OrderItemCreate(item_id=items[0].id, quantity=1)],
            total=10.99,
            payment=schemas.PaymentData(
                card_number="1234567890123456",
                card_holder_name="John Doe",
                expiry_month=12,
                expiry_year=2025,
                cvv="123",
            ),
        )

        order = repository.create_order(db, order_data)

        # Payment data should contain masked card number
        import json

        payment_data = json.loads(order.payment_data)
        assert payment_data["card_number"] == "**** **** **** 3456"
        assert payment_data["card_holder_name"] == "John Doe"
