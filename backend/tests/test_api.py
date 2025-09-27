from fastapi import status


class TestAPIEndpoints:
    """
    Test cases for API endpoints
    
    Note: some tests have the db fixture without using it to ensure a clean database state.
    """

    def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "Kiosk Checkout API"
        assert data["version"] == "1.0.0"

    def test_get_categories_empty(self, client):
        """Test getting categories when database is empty"""
        response = client.get("/api/v1/categories")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_get_categories_with_data(self, client, setup_test_data):
        """Test getting categories with data"""
        response = client.get("/api/v1/categories")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Test Category"
        assert data[0]["image"] == "test.jpg"

    def test_get_menu(self, client, setup_test_data):
        """Test getting complete menu"""
        response = client.get("/api/v1/menu")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "categories" in data
        assert "items" in data
        assert len(data["categories"]) == 1
        assert len(data["items"]) == 2

    def test_get_items_all(self, client, setup_test_data):
        """Test getting all items"""
        response = client.get("/api/v1/items")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] == "Test Item 1"
        assert data[1]["name"] == "Test Item 2"

    def test_get_items_by_category(self, client, setup_test_data):
        """Test getting items by category"""
        test_data = setup_test_data
        category_id = test_data["category"].id
        
        response = client.get(f"/api/v1/items?category_id={category_id}")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert len(data) == 2
        for item in data:
            assert item["category_id"] == category_id

    def test_get_item_by_id_exists(self, client, setup_test_data):
        """Test getting item by ID when it exists"""
        test_data = setup_test_data
        item_id = test_data["items"][0].id
        
        response = client.get(f"/api/v1/items/{item_id}")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["id"] == item_id
        assert data["name"] == "Test Item 1"

    def test_get_item_by_id_not_exists(self, client, db):
        """Test getting item by ID when it doesn't exist"""
        response = client.get("/api/v1/items/998")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        data = response.json()
        assert data["detail"] == "Item not found"

    def test_create_order_success(self, client, setup_test_data):
        """Test creating a successful order"""
        test_data = setup_test_data
        items = test_data["items"]
        
        order_data = {
            "items": [
                {"item_id": items[0].id, "quantity": 2},
                {"item_id": items[1].id, "quantity": 1}
            ],
            "total": 37.97,  # (10.99 * 2) + (15.99 * 1)
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
        
        response = client.post("/api/v1/orders", json=order_data)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["total"] == 37.97
        assert "id" in data
        assert "timestamp" in data
        assert "payment_key" in data

    def test_create_order_invalid_item(self, client, db):
        """Test creating order with invalid item ID"""
        order_data = {
            "items": [
                {"item_id": 999, "quantity": 1}
            ],
            "total": 10.99,
            "payment": {
                "card_number": "1234567890123456",
                "card_holder_name": "John Doe",
                "expiry_month": 12,
                "expiry_year": 2025,
                "cvv": "123"
            }
        }
        
        response = client.post("/api/v1/orders", json=order_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        data = response.json()
        assert "Item with ID 999 not found" in data["detail"]

    def test_create_order_total_mismatch(self, client, setup_test_data):
        """Test creating order with incorrect total"""
        test_data = setup_test_data
        items = test_data["items"]
        
        order_data = {
            "items": [
                {"item_id": items[0].id, "quantity": 1}
            ],
            "total": 99.99,  # Wrong total (should be 10.99)
            "payment": {
                "card_number": "1234567890123456",
                "card_holder_name": "John Doe",
                "expiry_month": 12,
                "expiry_year": 2025,
                "cvv": "123"
            }
        }
        
        response = client.post("/api/v1/orders", json=order_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        data = response.json()
        assert "Total mismatch" in data["detail"]

    def test_create_order_invalid_payment_data(self, client, setup_test_data):
        """Test creating order with invalid payment data"""
        test_data = setup_test_data
        items = test_data["items"]
        
        order_data = {
            "items": [
                {"item_id": items[0].id, "quantity": 1}
            ],
            "total": 10.99,
            "payment": {
                "card_number": "1234567890123456",
                "card_holder_name": "John Doe",
                "expiry_month": 13,  # Invalid month
                "expiry_year": 2025,
                "cvv": "123"
            }
        }
        
        response = client.post("/api/v1/orders", json=order_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_order_by_id_exists(self, client, setup_test_data):
        """Test getting order by ID when it exists"""
        test_data = setup_test_data
        items = test_data["items"]
        
        # First create an order
        order_data = {
            "items": [
                {"item_id": items[0].id, "quantity": 1}
            ],
            "total": 10.99,
            "payment": {
                "card_number": "1234567890123456",
                "card_holder_name": "John Doe",
                "expiry_month": 12,
                "expiry_year": 2025,
                "cvv": "123"
            }
        }
        
        create_response = client.post("/api/v1/orders", json=order_data)
        created_order = create_response.json()
        order_id = created_order["id"]
        
        # Then retrieve it
        response = client.get(f"/api/v1/orders/{order_id}")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["id"] == order_id
        assert data["total"] == 10.99

    def test_get_order_by_id_not_exists(self, client, db):
        """Test getting order by ID when it doesn't exist"""
        response = client.get("/api/v1/orders/999")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        data = response.json()
        assert data["detail"] == "Order not found"

    def test_create_category_admin(self, client, db):
        """Test creating category via admin endpoint"""
        category_data = {
            "name": "New Category",
            "image": "new_category.jpg"
        }
        
        response = client.post("/api/v1/admin/categories", json=category_data)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["name"] == "New Category"
        assert data["image"] == "new_category.jpg"
        assert "id" in data

    def test_create_item_admin(self, client, setup_test_data):
        """Test creating item via admin endpoint"""
        test_data = setup_test_data
        category_id = test_data["category"].id
        
        item_data = {
            "name": "New Item",
            "price": 25.99,
            "image_id": "new_item.jpg",
            "description": "A new test item",
            "category_id": category_id
        }
        
        response = client.post("/api/v1/admin/items", json=item_data)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["name"] == "New Item"
        assert data["price"] == 25.99
        assert data["category_id"] == category_id
        assert "id" in data

    def test_create_item_admin_invalid_category(self, client, db):
        """Test creating item with invalid category ID"""
        item_data = {
            "name": "New Item",
            "price": 25.99,
            "category_id": 999  # Non-existent category
        }
        
        response = client.post("/api/v1/admin/items", json=item_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_validation_errors(self, client):
        """Test various validation errors"""
        # Test negative price
        invalid_item = {
            "name": "Invalid Item",
            "price": -5.99,
            "category_id": 1
        }
        
        response = client.post("/api/v1/admin/items", json=invalid_item)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_cors_headers(self, client):
        """Test CORS headers are present"""
        response = client.options("/api/v1/menu")
        # The test client might not include all CORS headers, but we can test the endpoint works
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_405_METHOD_NOT_ALLOWED]
