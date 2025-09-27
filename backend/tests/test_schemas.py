import pytest
from datetime import datetime, timezone
from pydantic import ValidationError
from checkout.models import schemas


class TestSchemas:
    """Test cases for Pydantic schemas"""

    def test_category_create_valid(self):
        """Test creating valid CategoryCreate schema"""
        category_data = {"name": "Test Category", "image": "test.jpg"}
        category = schemas.CategoryCreate(**category_data)

        assert category.name == "Test Category"
        assert category.image == "test.jpg"

    def test_category_create_without_image(self):
        """Test creating CategoryCreate without optional image"""
        category_data = {"name": "Test Category"}
        category = schemas.CategoryCreate(**category_data)

        assert category.name == "Test Category"
        assert category.image is None

    def test_item_create_valid(self):
        """Test creating valid ItemCreate schema"""
        item_data = {
            "name": "Test Item",
            "price": 12.99,
            "image_id": "item.jpg",
            "category_id": 1,
        }
        item = schemas.ItemCreate(**item_data)

        assert item.name == "Test Item"
        assert item.price == 12.99
        assert item.category_id == 1

    def test_item_create_negative_price(self):
        """Test ItemCreate with negative price should fail"""
        item_data = {"name": "Test Item", "price": -5.99, "category_id": 1}

        with pytest.raises(ValidationError) as exc_info:
            schemas.ItemCreate(**item_data)

        assert "Input should be greater than 0" in str(exc_info.value)

    def test_item_create_zero_price(self):
        """Test ItemCreate with zero price should fail"""
        item_data = {"name": "Test Item", "price": 0.0, "category_id": 1}

        with pytest.raises(ValidationError) as exc_info:
            schemas.ItemCreate(**item_data)

        assert "Input should be greater than 0" in str(exc_info.value)

    def test_order_item_create_valid(self):
        """Test creating valid OrderItemCreate schema"""
        order_item_data = {"item_id": 1, "quantity": 3}
        order_item = schemas.OrderItemCreate(**order_item_data)

        assert order_item.item_id == 1
        assert order_item.quantity == 3

    def test_order_item_create_zero_quantity(self):
        """Test OrderItemCreate with zero quantity should fail"""
        order_item_data = {"item_id": 1, "quantity": 0}

        with pytest.raises(ValidationError) as exc_info:
            schemas.OrderItemCreate(**order_item_data)

        assert "Input should be greater than 0" in str(exc_info.value)

    def test_order_item_create_negative_quantity(self):
        """Test OrderItemCreate with negative quantity should fail"""
        order_item_data = {"item_id": 1, "quantity": -1}

        with pytest.raises(ValidationError) as exc_info:
            schemas.OrderItemCreate(**order_item_data)

        assert "Input should be greater than 0" in str(exc_info.value)

    def test_payment_data_valid(self):
        """Test creating valid PaymentData schema"""
        payment_data = {
            "card_number": "1234567890123456",
            "card_holder_name": "John Doe",
            "expiry_month": 12,
            "expiry_year": 2025,
            "cvv": "123",
            "billing_address": {
                "street": "123 Main St",
                "city": "Anytown",
                "zip": "12345",
            },
        }
        payment = schemas.PaymentData(**payment_data)

        assert payment.card_number == "1234567890123456"
        assert payment.card_holder_name == "John Doe"
        assert payment.expiry_month == 12
        assert payment.expiry_year == 2025
        assert payment.cvv == "123"

    def test_payment_data_invalid_month_high(self):
        """Test PaymentData with invalid high month"""
        payment_data = {
            "card_number": "1234567890123456",
            "card_holder_name": "John Doe",
            "expiry_month": 13,  # Invalid
            "expiry_year": 2025,
            "cvv": "123",
        }

        with pytest.raises(ValidationError):
            schemas.PaymentData(**payment_data)

    def test_payment_data_invalid_month_low(self):
        """Test PaymentData with invalid low month"""
        payment_data = {
            "card_number": "1234567890123456",
            "card_holder_name": "John Doe",
            "expiry_month": 0,  # Invalid
            "expiry_year": 2025,
            "cvv": "123",
        }

        with pytest.raises(ValidationError):
            schemas.PaymentData(**payment_data)

    def test_payment_data_without_billing_address(self):
        """Test PaymentData without optional billing address"""
        payment_data = {
            "card_number": "1234567890123456",
            "card_holder_name": "John Doe",
            "expiry_month": 12,
            "expiry_year": 2025,
            "cvv": "123",
        }
        payment = schemas.PaymentData(**payment_data)

        assert payment.billing_address is None

    def test_order_create_valid(self):
        """Test creating valid OrderCreate schema"""
        order_data = {
            "items": [{"item_id": 1, "quantity": 2}, {"item_id": 2, "quantity": 1}],
            "total": 25.98,
            "payment": {
                "card_number": "1234567890123456",
                "card_holder_name": "John Doe",
                "expiry_month": 12,
                "expiry_year": 2025,
                "cvv": "123",
            },
        }
        order = schemas.OrderCreate(**order_data)

        assert len(order.items) == 2
        assert order.total == 25.98
        assert order.payment.card_holder_name == "John Doe"

    def test_order_create_zero_total(self):
        """Test OrderCreate with zero total should fail"""
        order_data = {
            "items": [{"item_id": 1, "quantity": 1}],
            "total": 0.0,
            "payment": {
                "card_number": "1234567890123456",
                "card_holder_name": "John Doe",
                "expiry_month": 12,
                "expiry_year": 2025,
                "cvv": "123",
            },
        }

        with pytest.raises(ValidationError) as exc_info:
            schemas.OrderCreate(**order_data)

        assert "Input should be greater than 0" in str(exc_info.value)

    def test_order_create_negative_total(self):
        """Test OrderCreate with negative total should fail"""
        order_data = {
            "items": [{"item_id": 1, "quantity": 1}],
            "total": -10.99,
            "payment": {
                "card_number": "1234567890123456",
                "card_holder_name": "John Doe",
                "expiry_month": 12,
                "expiry_year": 2025,
                "cvv": "123",
            },
        }

        with pytest.raises(ValidationError) as exc_info:
            schemas.OrderCreate(**order_data)

        assert "Input should be greater than 0" in str(exc_info.value)

    def test_order_create_empty_items(self):
        """Test OrderCreate with empty items list"""
        order_data = {
            "items": [],
            "total": 10.99,
            "payment": {
                "card_number": "1234567890123456",
                "card_holder_name": "John Doe",
                "expiry_month": 12,
                "expiry_year": 2025,
                "cvv": "123",
            },
        }

        # This should be valid according to the schema (business logic validation happens elsewhere)
        order = schemas.OrderCreate(**order_data)
        assert len(order.items) == 0

    def test_menu_response_valid(self):
        """Test creating valid MenuResponse schema"""
        menu_data = {
            "categories": [{"id": 1, "name": "Category 1", "image": "cat1.jpg"}],
            "items": [
                {
                    "id": 1,
                    "name": "Item 1",
                    "price": 10.99,
                    "category_id": 1,
                    "image_id": "item1.jpg",
                }
            ],
        }
        menu = schemas.MenuResponse(**menu_data)

        assert len(menu.categories) == 1
        assert len(menu.items) == 1
        assert menu.categories[0].name == "Category 1"
        assert menu.items[0].name == "Item 1"

    def test_schema_serialization(self):
        """Test schema serialization to dict"""
        category = schemas.CategoryCreate(name="Test", image="test.jpg")
        category_dict = category.dict()

        assert category_dict == {"name": "Test", "image": "test.jpg"}

    def test_schema_json_serialization(self):
        """Test schema JSON serialization"""
        item_data = {"name": "Test Item", "price": 12.99, "category_id": 1}
        item = schemas.ItemCreate(**item_data)
        json_str = item.json()

        assert "Test Item" in json_str
        assert "12.99" in json_str
