import pytest
from fastapi.testclient import TestClient
from checkout.main import app
import json


class TestIntegration:
    """Integration tests for API workflow"""

    def test_validation_workflow(self, client):
        """Test validation across different endpoints"""
        # Invalid category creation - empty name
        invalid_category = {"name": ""}  # Empty name
        response = client.post("/api/v1/admin/categories", json=invalid_category)
        assert response.status_code == 400
        assert "name is required" in response.json()["detail"].lower()

        # Invalid category creation - whitespace only
        invalid_category = {"name": "   "}  # Whitespace only
        response = client.post("/api/v1/admin/categories", json=invalid_category)
        assert response.status_code == 400

        # Invalid category creation - too long name
        invalid_category = {"name": "x" * 101}  # Too long
        response = client.post("/api/v1/admin/categories", json=invalid_category)
        assert response.status_code == 400
        assert "cannot exceed 100 characters" in response.json()["detail"]

        # Invalid item creation - empty name
        invalid_item = {"name": "", "price": 10.99, "category_id": 1}
        response = client.post("/api/v1/admin/items", json=invalid_item)
        assert response.status_code == 400
        assert "name is required" in response.json()["detail"].lower()

        # Invalid item creation - negative price
        invalid_item = {
            "name": "Test Item",
            "price": -5.99,  # Negative price
            "category_id": 1,
        }
        response = client.post("/api/v1/admin/items", json=invalid_item)
        assert response.status_code == 400
        assert "greater than 0" in response.json()["detail"]

        # Invalid item creation - price too high
        invalid_item = {
            "name": "Expensive Item",
            "price": 1000.00,  # Too expensive
            "category_id": 1,
        }
        response = client.post("/api/v1/admin/items", json=invalid_item)
        assert response.status_code == 400
        assert "cannot exceed $999.99" in response.json()["detail"]

        # Invalid item creation - non-existent category
        invalid_item = {
            "name": "Test Item",
            "price": 15.99,
            "category_id": 99999,  # Non-existent category
        }
        response = client.post("/api/v1/admin/items", json=invalid_item)
        assert response.status_code == 400
        assert "does not exist" in response.json()["detail"]

    @pytest.fixture(scope="function")
    def test_duplicate_validation_workflow(self, client):
        """Test duplicate name validation"""
        # Create a category
        category_data = {"name": "Unique Category", "image": "unique.jpg"}
        response = client.post("/api/v1/admin/categories", json=category_data)
        assert response.status_code == 200
        category = response.json()

        # Try to create duplicate category (case insensitive)
        duplicate_category = {"name": "unique category", "image": "duplicate.jpg"}
        response = client.post("/api/v1/admin/categories", json=duplicate_category)
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

        # Create an item in the category
        item_data = {
            "name": "Unique Item",
            "price": 12.99,
            "category_id": category["id"],
        }
        response = client.post("/api/v1/admin/items", json=item_data)
        assert response.status_code == 200

        # Try to create duplicate item in same category
        duplicate_item = {
            "name": "unique item",  # Case insensitive
            "price": 15.99,
            "category_id": category["id"],
        }
        response = client.post("/api/v1/admin/items", json=duplicate_item)
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_field_length_validation_workflow(self, client):
        """Test field length validation"""
        # Create a valid category first
        category_data = {"name": "Test Category", "image": "test.jpg"}
        response = client.post("/api/v1/admin/categories", json=category_data)
        assert response.status_code == 200
        category = response.json()

        # Test long description for item
        long_description_item = {
            "name": "Item with Long Description",
            "price": 12.99,
            "description": "x" * 501,  # Too long
            "category_id": category["id"],
        }
        response = client.post("/api/v1/admin/items", json=long_description_item)
        assert response.status_code == 400
        assert "500 characters" in response.json()["detail"]

        # Test valid long description (exactly 500 chars)
        valid_long_item = {
            "name": "Item with Max Description",
            "price": 12.99,
            "description": "x" * 500,  # Exactly 500
            "category_id": category["id"],
        }
        response = client.post("/api/v1/admin/items", json=valid_long_item)
        assert response.status_code == 200

    def test_api_versioning(self, client):
        """Test that API versioning is working"""
        # All our endpoints use /api/v1/ prefix
        response = client.get("/api/v1/menu")
        assert response.status_code == 200

        # Test that root endpoint doesn't require versioning
        response = client.get("/")
        assert response.status_code == 200

    def test_validation_workflow(self, client):
        """Test validation across different endpoints"""
        # Invalid category creation - empty name
        invalid_category = {"name": ""}  # Empty name
        response = client.post("/api/v1/admin/categories", json=invalid_category)
        assert response.status_code == 400
        assert "name is required" in response.json()["detail"].lower()

        # Invalid category creation - whitespace only
        invalid_category = {"name": "   "}  # Whitespace only
        response = client.post("/api/v1/admin/categories", json=invalid_category)
        assert response.status_code == 400

        # Invalid category creation - too long name
        invalid_category = {"name": "x" * 101}  # Too long
        response = client.post("/api/v1/admin/categories", json=invalid_category)
        assert response.status_code == 400
        assert "cannot exceed 100 characters" in response.json()["detail"]

        # Invalid item creation - empty name
        invalid_item = {"name": "", "price": 10.99, "category_id": 1}
        response = client.post("/api/v1/admin/items", json=invalid_item)
        assert response.status_code == 400
        assert "name is required" in response.json()["detail"].lower()

        # Invalid item creation - negative price
        invalid_item = {
            "name": "Test Item",
            "price": -5.99,  # Negative price
            "category_id": 1,
        }
        response = client.post("/api/v1/admin/items", json=invalid_item)
        assert response.status_code == 400
        assert "greater than 0" in response.json()["detail"]

        # Invalid item creation - price too high
        invalid_item = {
            "name": "Expensive Item",
            "price": 1000.00,  # Too expensive
            "category_id": 1,
        }
        response = client.post("/api/v1/admin/items", json=invalid_item)
        assert response.status_code == 400
        assert "cannot exceed $999.99" in response.json()["detail"]

        # Invalid item creation - non-existent category
        invalid_item = {
            "name": "Test Item",
            "price": 15.99,
            "category_id": 99999,  # Non-existent category
        }
        response = client.post("/api/v1/admin/items", json=invalid_item)
        assert response.status_code == 400
        assert "does not exist" in response.json()["detail"]

    def test_duplicate_validation_workflow(self, client, db):
        """Test duplicate name validation"""
        # Create a category
        category_data = {"name": "Unique Category", "image": "unique.jpg"}
        response = client.post("/api/v1/admin/categories", json=category_data)
        assert response.status_code == 200
        category = response.json()

        # Try to create duplicate category (case insensitive)
        duplicate_category = {"name": "unique category", "image": "duplicate.jpg"}
        response = client.post("/api/v1/admin/categories", json=duplicate_category)
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

        # Create an item in the category
        item_data = {
            "name": "Unique Item",
            "price": 12.99,
            "category_id": category["id"],
        }
        response = client.post("/api/v1/admin/items", json=item_data)
        assert response.status_code == 200

        # Try to create duplicate item in same category
        duplicate_item = {
            "name": "unique item",  # Case insensitive
            "price": 15.99,
            "category_id": category["id"],
        }
        response = client.post("/api/v1/admin/items", json=duplicate_item)
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_field_length_validation_workflow(self, client, db):
        """Test field length validation"""
        # Create a valid category first
        category_data = {"name": "Test Category", "image": "test.jpg"}
        response = client.post("/api/v1/admin/categories", json=category_data)
        assert response.status_code == 200
        category = response.json()

        # Test long description for item
        long_name_item = {
            "name": "Item with Long name" + "x" * 500,  # Make name long but valid
            "price": 12.99,
            "category_id": category["id"],
        }
        response = client.post("/api/v1/admin/items", json=long_name_item)
        assert response.status_code == 400
        assert "200 characters" in response.json()["detail"]

        # Test valid long name
        valid_long_item = {
            "name": "Item with Max name" + "x" * 180,
            "price": 12.99,
            "category_id": category["id"],
        }
        response = client.post("/api/v1/admin/items", json=valid_long_item)
        assert response.status_code == 200

    @pytest.fixture(scope="function")
    def client_with_data(self, client, setup_test_data):
        """Client with test data already loaded"""
        return client

    def test_complete_order_workflow(self, client, db):
        """Test complete workflow from menu to order creation"""
        # Step 1: Create test data via admin endpoints
        category_data = {
            "name": "Integration Test Category",
            "image": "integration.jpg",
        }

        category_response = client.post("/api/v1/admin/categories", json=category_data)
        assert category_response.status_code == 200
        category = category_response.json()

        # Create test items
        item1_data = {
            "name": "Integration Item 1",
            "price": 10.99,
            "image_id": "item1.jpg",
            "category_id": category["id"],
        }

        item2_data = {
            "name": "Integration Item 2",
            "price": 15.99,
            "image_id": "item2.jpg",
            "category_id": category["id"],
        }

        item1_response = client.post("/api/v1/admin/items", json=item1_data)
        item2_response = client.post("/api/v1/admin/items", json=item2_data)

        assert item1_response.status_code == 200
        assert item2_response.status_code == 200

        item1 = item1_response.json()
        item2 = item2_response.json()

        # Step 2: Get menu data
        menu_response = client.get("/api/v1/menu")
        assert menu_response.status_code == 200

        menu = menu_response.json()
        assert len(menu["categories"]) >= 1
        assert len(menu["items"]) >= 2

        # Step 3: Get specific items
        item1_detail_response = client.get(f"/api/v1/items/{item1['id']}")
        assert item1_detail_response.status_code == 200
        assert item1_detail_response.json()["name"] == "Integration Item 1"

        # Step 4: Create order with items
        order_data = {
            "items": [
                {"item_id": item1["id"], "quantity": 2},
                {"item_id": item2["id"], "quantity": 1},
            ],
            "total": 37.97,  # (10.99 * 2) + (15.99 * 1)
            "payment": {
                "card_number": "4111111111111111",
                "card_holder_name": "Integration Test User",
                "expiry_month": 12,
                "expiry_year": 2026,
                "cvv": "123",
                "billing_address": {
                    "street": "123 Test St",
                    "city": "Test City",
                    "zip": "12345",
                },
            },
        }

        order_response = client.post("/api/v1/orders", json=order_data)
        assert order_response.status_code == 200

        order = order_response.json()
        assert order["total"] == 37.97
        assert "id" in order
        assert "payment_key" in order

        # Step 5: Retrieve the created order
        order_detail_response = client.get(f"/api/v1/orders/{order['id']}")
        assert order_detail_response.status_code == 200

        order_detail = order_detail_response.json()
        assert order_detail["id"] == order["id"]
        assert order_detail["total"] == 37.97

    def test_menu_browsing_workflow(self, client_with_data):
        """Test menu browsing workflow"""
        # Get all categories
        categories_response = client_with_data.get("/api/v1/categories")
        assert categories_response.status_code == 200
        categories = categories_response.json()

        # Get all items
        items_response = client_with_data.get("/api/v1/items")
        assert items_response.status_code == 200
        items = items_response.json()

        # Get items by category
        if categories:
            category_id = categories[0]["id"]
            category_items_response = client_with_data.get(
                f"/api/v1/items?category_id={category_id}"
            )
            assert category_items_response.status_code == 200
            category_items = category_items_response.json()

            # All returned items should belong to the requested category
            for item in category_items:
                assert item["category_id"] == category_id

    def test_error_handling_workflow(self, client, db):
        """Test error handling in various scenarios"""
        # Try to get non-existent item
        response = client.get("/api/v1/items/99999")
        assert response.status_code == 404

        # Try to get non-existent order
        response = client.get("/api/v1/orders/99999")
        assert response.status_code == 404

        # Try to create order with invalid item
        order_data = {
            "items": [{"item_id": 99999, "quantity": 1}],
            "total": 10.99,
            "payment": {
                "card_number": "4111111111111111",
                "card_holder_name": "Test User",
                "expiry_month": 12,
                "expiry_year": 2026,
                "cvv": "123",
            },
        }
        response = client.post("/api/v1/orders", json=order_data)
        assert response.status_code == 400

    def test_validation_workflow(self, client, db):
        """Test validation across different endpoints"""
        # Invalid category creation
        invalid_category = {"name": ""}  # Empty name
        response = client.post("/api/v1/admin/categories", json=invalid_category)
        assert response.status_code == 400

        # Invalid item creation
        invalid_item = {
            "name": "Test Item",
            "price": -5.99,  # Negative price
            "category_id": 1,
        }
        response = client.post("/api/v1/admin/items", json=invalid_item)
        assert response.status_code == 422

    def test_large_order_workflow(self, client_with_data, setup_test_data):
        """Test workflow with larger order"""
        test_data = setup_test_data
        items = test_data["items"]

        # Create order with many items and high quantities
        order_items = []
        total = 0

        for i, item in enumerate(items):
            quantity = 5 + i  # Different quantities
            order_items.append({"item_id": item.id, "quantity": quantity})
            total += item.price * quantity

        order_data = {
            "items": order_items,
            "total": round(total, 2),
            "payment": {
                "card_number": "4111111111111111",
                "card_holder_name": "Large Order User",
                "expiry_month": 6,
                "expiry_year": 2027,
                "cvv": "456",
            },
        }

        response = client_with_data.post("/api/v1/orders", json=order_data)
        assert response.status_code == 200

        order = response.json()
        assert order["total"] == total

    def test_concurrent_order_simulation(self, client_with_data, setup_test_data):
        """Simulate concurrent orders to test database handling"""
        test_data = setup_test_data
        items = test_data["items"]

        orders = []

        # Create multiple orders quickly
        for i in range(3):
            order_data = {
                "items": [{"item_id": items[0].id, "quantity": 1}],
                "total": items[0].price,
                "payment": {
                    "card_number": f"411111111111{i:04d}",
                    "card_holder_name": f"User {i}",
                    "expiry_month": 12,
                    "expiry_year": 2025,
                    "cvv": "123",
                },
            }

            response = client_with_data.post("/api/v1/orders", json=order_data)
            assert response.status_code == 200
            orders.append(response.json())

        # Verify all orders were created with unique IDs
        order_ids = [order["id"] for order in orders]
        assert len(set(order_ids)) == len(order_ids)  # All unique

    def test_api_versioning(self, client, db):
        """Test that API versioning is working"""
        # All our endpoints use /api/v1/ prefix
        response = client.get("/api/v1/menu")
        assert response.status_code == 200

        # Test that root endpoint doesn't require versioning
        response = client.get("/")
        assert response.status_code == 200

    def test_response_formats(self, client_with_data):
        """Test that all responses follow expected formats"""
        # Test menu response format
        response = client_with_data.get("/api/v1/menu")
        assert response.status_code == 200

        data = response.json()
        assert "categories" in data
        assert "items" in data
        assert isinstance(data["categories"], list)
        assert isinstance(data["items"], list)

        # Test categories response format
        response = client_with_data.get("/api/v1/categories")
        assert response.status_code == 200

        categories = response.json()
        assert isinstance(categories, list)

        if categories:
            category = categories[0]
            assert "id" in category
            assert "name" in category
            # image is optional

    def test_payment_data_security(self, client_with_data, setup_test_data):
        """Test that sensitive payment data is properly handled"""
        test_data = setup_test_data
        items = test_data["items"]

        order_data = {
            "items": [{"item_id": items[0].id, "quantity": 1}],
            "total": items[0].price,
            "payment": {
                "card_number": "4111111111111111",
                "card_holder_name": "Security Test User",
                "expiry_month": 12,
                "expiry_year": 2025,
                "cvv": "123",
            },
        }

        response = client_with_data.post("/api/v1/orders", json=order_data)
        assert response.status_code == 200

        order = response.json()

        # Response should not contain full card number
        response_str = json.dumps(order)
        assert "4111111111111111" not in response_str

        # Should contain payment key but not full card data
        assert "payment_key" in order
        assert len(order["payment_key"]) > 0
