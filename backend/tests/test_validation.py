import pytest
from fastapi.testclient import TestClient


class TestValidation:
    """Test cases for API validation functionality"""

    def test_category_name_validation(self, client):
        """Test category name validation rules"""
        # Test empty name
        response = client.post("/api/v1/admin/categories", json={"name": ""})
        assert response.status_code == 400
        assert "name is required" in response.json()["detail"].lower()

        # Test whitespace-only name
        response = client.post("/api/v1/admin/categories", json={"name": "   "})
        assert response.status_code == 400
        assert "name is required" in response.json()["detail"].lower()

        # Test name too long (101 characters)
        long_name = "x" * 101
        response = client.post("/api/v1/admin/categories", json={"name": long_name})
        assert response.status_code == 400
        assert "cannot exceed 100 characters" in response.json()["detail"]

        # Test valid name at maximum length (100 characters)
        max_name = "x" * 100
        response = client.post("/api/v1/admin/categories", json={"name": max_name})
        assert response.status_code == 200

    def test_category_image_validation(self, client):
        """Test category image field validation"""
        # Test image filename too long (256 characters)
        long_image = "x" * 256
        response = client.post("/api/v1/admin/categories", json={
            "name": "Valid Category",
            "image": long_image
        })
        assert response.status_code == 400
        assert "cannot exceed 255 characters" in response.json()["detail"]

        # Test valid image at maximum length (255 characters)
        max_image = "x" * 255
        response = client.post("/api/v1/admin/categories", json={
            "name": "Valid Category 2",
            "image": max_image
        })
        assert response.status_code == 200

    def test_category_duplicate_validation(self, client):
        """Test category duplicate name validation"""
        # Create first category
        category_data = {"name": "Test Category", "image": "test1.jpg"}
        response = client.post("/api/v1/admin/categories", json=category_data)
        assert response.status_code == 200

        # Try to create duplicate with exact same name
        duplicate_data = {"name": "Test Category", "image": "test2.jpg"}
        response = client.post("/api/v1/admin/categories", json=duplicate_data)
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

        # Try to create duplicate with different case
        case_duplicate = {"name": "test category", "image": "test3.jpg"}
        response = client.post("/api/v1/admin/categories", json=case_duplicate)
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

        # Test with mixed case
        mixed_case = {"name": "TeSt CaTeGoRy", "image": "test4.jpg"}
        response = client.post("/api/v1/admin/categories", json=mixed_case)
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_item_name_validation(self, client, db):
        """Test item name validation rules"""
        # First create a category
        category_response = client.post("/api/v1/admin/categories", json={
            "name": "Test Category 2", 
            "image": "test.jpg"
        })
        assert category_response.status_code == 200
        category_id = category_response.json()["id"]

        # Test empty name
        response = client.post("/api/v1/admin/items", json={
            "name": "",
            "price": 10.99,
            "category_id": category_id
        })
        assert response.status_code == 400
        assert "name is required" in response.json()["detail"].lower()

        # Test whitespace-only name
        response = client.post("/api/v1/admin/items", json={
            "name": "   ",
            "price": 10.99,
            "category_id": category_id
        })
        assert response.status_code == 400
        assert "name is required" in response.json()["detail"].lower()

        # Test name too long (201 characters)
        long_name = "x" * 201
        response = client.post("/api/v1/admin/items", json={
            "name": long_name,
            "price": 10.99,
            "category_id": category_id
        })
        assert response.status_code == 400
        assert "cannot exceed 200 characters" in response.json()["detail"]

        # Test valid name at maximum length (200 characters)
        max_name = "x" * 200
        response = client.post("/api/v1/admin/items", json={
            "name": max_name,
            "price": 10.99,
            "category_id": category_id
        })
        assert response.status_code == 200

    def test_item_price_validation(self, client, db):
        """Test item price validation rules"""
        # First create a category
        category_response = client.post("/api/v1/admin/categories", json={
            "name": "Test Category 3",
            "image": "test.jpg"
        })
        assert category_response.status_code == 200
        category_id = category_response.json()["id"]

        # Test zero price
        response = client.post("/api/v1/admin/items", json={
            "name": "Zero Price Item",
            "price": 0.0,
            "category_id": category_id
        })
        assert response.status_code == 422
        assert "greater than 0" in response.json()["detail"][0]["msg"]

        # Test negative price
        response = client.post("/api/v1/admin/items", json={
            "name": "Negative Price Item",
            "price": -5.99,
            "category_id": category_id
        })
        assert response.status_code == 422
        assert "greater than 0" in response.json()["detail"][0]["msg"]

        # Test valid high price
        response = client.post("/api/v1/admin/items", json={
            "name": "Max Price Item",
            "price": 999.99,
            "category_id": category_id
        })
        assert response.status_code == 200

        # Test valid low price
        response = client.post("/api/v1/admin/items", json={
            "name": "Cheap Item",
            "price": 0.01,
            "category_id": category_id
        })
        assert response.status_code == 200

    def test_item_category_validation(self, client, db):
        """Test item category validation"""
        # Test with non-existent category
        response = client.post("/api/v1/admin/items", json={
            "name": "Test Item",
            "price": 10.99,
            "category_id": 99999
        })
        assert response.status_code == 400
        assert "does not exist" in response.json()["detail"]

    def test_item_duplicate_validation(self, client, db):
        """Test item duplicate name validation within categories"""
        # Create a category
        category_response = client.post("/api/v1/admin/categories", json={
            "name": "Test Category 4",
            "image": "test.jpg"
        })
        assert category_response.status_code == 200
        category_id = category_response.json()["id"]

        # Create second category
        category2_response = client.post("/api/v1/admin/categories", json={
            "name": "Another Category",
            "image": "test2.jpg"
        })
        assert category2_response.status_code == 200
        category2_id = category2_response.json()["id"]

        # Create first item
        item_response = client.post("/api/v1/admin/items", json={
            "name": "Test Item",
            "price": 10.99,
            "category_id": category_id
        })
        assert item_response.status_code == 200

        # Try to create duplicate in same category
        duplicate_response = client.post("/api/v1/admin/items", json={
            "name": "test item",  # Case insensitive
            "price": 15.99,
            "category_id": category_id
        })
        assert duplicate_response.status_code == 400
        assert "already exists" in duplicate_response.json()["detail"]

        # Should be able to create same name in different category
        different_category_response = client.post("/api/v1/admin/items", json={
            "name": "Test Item",  # Same name, different category
            "price": 12.99,
            "category_id": category2_id
        })
        assert different_category_response.status_code == 200
