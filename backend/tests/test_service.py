"""
Unit tests for service layer classes
"""
import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from checkout.service.service import MenuService, OrderService, AdminService, FakePaymentService
from checkout.models import models, schemas


class TestFakePaymentService:
    """Test cases for FakePaymentService"""
    
    def test_process_payment_success(self):
        """Test successful payment processing"""
        amount = 25.99
        payment_data = {
            "card_number": "1234567890123456",
            "card_holder_name": "John Doe"
        }
        
        result = FakePaymentService.process_payment(amount, payment_data)
        assert result is True
    
    def test_process_payment_with_different_amounts(self):
        """Test payment processing with various amounts"""
        payment_data = {"card_number": "1234", "card_holder_name": "Test"}
        
        # Test different amounts
        for amount in [0.01, 10.50, 100.00, 999.99]:
            result = FakePaymentService.process_payment(amount, payment_data)
            assert result is True
    
    def test_process_payment_with_empty_data(self):
        """Test payment processing with empty data"""
        result = FakePaymentService.process_payment(10.00, {})
        assert result is True


class TestMenuService:
    """Test cases for MenuService"""
    
    @pytest.fixture
    def mock_db(self):
        """Create mock database session"""
        return Mock(spec=Session)
    
    @pytest.fixture
    def menu_service(self, mock_db):
        """Create MenuService instance with mock database"""
        return MenuService(mock_db)
    
    @pytest.fixture
    def sample_categories(self):
        """Sample category data for testing"""
        return [
            models.Category(id=1, name="Burgers", image="burgers.jpg"),
            models.Category(id=2, name="Drinks", image="drinks.jpg")
        ]
    
    @pytest.fixture
    def sample_items(self):
        """Sample item data for testing"""
        return [
            models.Item(id=1, name="Classic Burger", price=12.99, image_id="burger1.jpg", category_id=1),
            models.Item(id=2, name="Cheese Burger", price=14.99, image_id="burger2.jpg", category_id=1),
            models.Item(id=3, name="Coke", price=2.99, image_id="coke.jpg", category_id=2)
        ]
    
    @patch('checkout.service.service.repository.get_categories')
    def test_get_categories_success(self, mock_get_categories, menu_service, sample_categories):
        """Test successful category retrieval"""
        mock_get_categories.return_value = sample_categories
        
        result = menu_service.get_categories()
        
        assert len(result) == 2
        assert result[0].name == "Burgers"
        assert result[1].name == "Drinks"
        mock_get_categories.assert_called_once_with(menu_service.db)
    
    @patch('checkout.service.service.repository.get_categories')
    def test_get_categories_empty(self, mock_get_categories, menu_service):
        """Test category retrieval when no categories exist"""
        mock_get_categories.return_value = []
        
        result = menu_service.get_categories()
        
        assert len(result) == 0
        mock_get_categories.assert_called_once_with(menu_service.db)
    
    @patch('checkout.service.service.repository.get_categories')
    def test_get_categories_database_error(self, mock_get_categories, menu_service):
        """Test category retrieval when database error occurs"""
        mock_get_categories.side_effect = Exception("Database connection failed")
        
        with pytest.raises(Exception, match="Database connection failed"):
            menu_service.get_categories()
    
    @patch('checkout.service.service.repository.get_items')
    @patch('checkout.service.service.repository.get_categories')
    def test_get_menu_success(self, mock_get_categories, mock_get_items, menu_service, sample_categories, sample_items):
        """Test successful menu retrieval"""
        mock_get_categories.return_value = sample_categories
        mock_get_items.return_value = sample_items
        
        result = menu_service.get_menu()
        
        assert isinstance(result, schemas.MenuResponse)
        assert len(result.categories) == 2
        assert len(result.items) == 3
        mock_get_categories.assert_called_once_with(menu_service.db)
        mock_get_items.assert_called_once_with(menu_service.db)
    
    @patch('checkout.service.service.repository.get_items')
    def test_get_items_all(self, mock_get_items, menu_service, sample_items):
        """Test getting all items"""
        mock_get_items.return_value = sample_items
        
        result = menu_service.get_items()
        
        assert len(result) == 3
        mock_get_items.assert_called_once_with(menu_service.db, category_id=None)
    
    @patch('checkout.service.service.repository.get_items')
    def test_get_items_by_category(self, mock_get_items, menu_service):
        """Test getting items by category"""
        category_items = [
            models.Item(id=1, name="Classic Burger", price=12.99, image_id="burger1.jpg", category_id=1),
            models.Item(id=2, name="Cheese Burger", price=14.99, image_id="burger2.jpg", category_id=1)
        ]
        mock_get_items.return_value = category_items
        
        result = menu_service.get_items(category_id=1)
        
        assert len(result) == 2
        assert all(item.category_id == 1 for item in result)
        mock_get_items.assert_called_once_with(menu_service.db, category_id=1)
    
    @patch('checkout.service.service.repository.get_item_by_id')
    def test_get_item_by_id_success(self, mock_get_item, menu_service, sample_items):
        """Test successful item retrieval by ID"""
        mock_get_item.return_value = sample_items[0]
        
        result = menu_service.get_item_by_id(1)
        
        assert result.id == 1
        assert result.name == "Classic Burger"
        mock_get_item.assert_called_once_with(menu_service.db, item_id=1)
    
    @patch('checkout.service.service.repository.get_item_by_id')
    def test_get_item_by_id_not_found(self, mock_get_item, menu_service):
        """Test item retrieval when item doesn't exist"""
        mock_get_item.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            menu_service.get_item_by_id(999)
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert exc_info.value.detail == "Item not found"
    
    @patch('checkout.service.service.repository.get_item_by_id')
    def test_get_item_by_id_database_error(self, mock_get_item, menu_service):
        """Test item retrieval when database error occurs"""
        mock_get_item.side_effect = Exception("Database error")
        
        with pytest.raises(Exception, match="Database error"):
            menu_service.get_item_by_id(1)


class TestOrderService:
    """Test cases for OrderService"""
    
    @pytest.fixture
    def mock_db(self):
        """Create mock database session"""
        return Mock(spec=Session)
    
    @pytest.fixture
    def order_service(self, mock_db):
        """Create OrderService instance with mock database"""
        return OrderService(mock_db)
    
    @pytest.fixture
    def sample_order_create(self):
        """Sample order create data"""
        return schemas.OrderCreate(
            items=[
                schemas.OrderItemCreate(item_id=1, quantity=2),
                schemas.OrderItemCreate(item_id=2, quantity=1)
            ],
            total=26.97,
            payment=schemas.PaymentData(
                card_number="1234567890123456",
                card_holder_name="John Doe",
                expiry_month=12,
                expiry_year=2025,
                cvv="123"
            )
        )
    
    @pytest.fixture
    def sample_items(self):
        """Sample items for order testing"""
        return {
            1: models.Item(id=1, name="Burger", price=10.99, image_id="burger.jpg", category_id=1),
            2: models.Item(id=2, name="Fries", price=4.99, image_id="fries.jpg", category_id=1)
        }
    
    @patch('checkout.service.service.FakePaymentService.process_payment')
    @patch('checkout.service.service.repository.create_order')
    @patch('checkout.service.service.repository.get_item_by_id')
    def test_create_order_success(self, mock_get_item, mock_create_order, mock_payment, 
                                 order_service, sample_order_create, sample_items):
        """Test successful order creation"""
        # Setup mocks
        def get_item_side_effect(db, item_id):
            return sample_items.get(item_id)
        
        mock_get_item.side_effect = get_item_side_effect
        mock_payment.return_value = True
        
        created_order = models.Order(id=1, total=25.98, payment_key="test_key")
        mock_create_order.return_value = created_order
        
        result = order_service.create_order(sample_order_create)
        
        assert result.id == 1
        assert result.total == 25.98
        mock_create_order.assert_called_once()
        mock_payment.assert_called_once()
    
    @patch('checkout.service.service.repository.get_item_by_id')
    def test_create_order_item_not_found(self, mock_get_item, order_service, sample_order_create):
        """Test order creation when item doesn't exist"""
        mock_get_item.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            order_service.create_order(sample_order_create)
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Item with ID 1 not found" in exc_info.value.detail
    
    @patch('checkout.service.service.repository.get_item_by_id')
    def test_create_order_total_mismatch(self, mock_get_item, order_service, sample_items):
        """Test order creation with incorrect total"""
        def get_item_side_effect(db, item_id):
            return sample_items.get(item_id)
        
        mock_get_item.side_effect = get_item_side_effect
        
        # Create order with wrong total
        order_data = schemas.OrderCreate(
            items=[schemas.OrderItemCreate(item_id=1, quantity=1)],
            total=50.00,  # Should be 10.99
            payment=schemas.PaymentData(
                card_number="1234567890123456",
                card_holder_name="John Doe",
                expiry_month=12,
                expiry_year=2025,
                cvv="123"
            )
        )
        
        with pytest.raises(HTTPException) as exc_info:
            order_service.create_order(order_data)
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Total mismatch" in exc_info.value.detail
    
    @patch('checkout.service.service.FakePaymentService.process_payment')
    @patch('checkout.service.service.repository.get_item_by_id')
    def test_create_order_payment_failed(self, mock_get_item, mock_payment, 
                                        order_service, sample_order_create, sample_items):
        """Test order creation when payment fails"""
        def get_item_side_effect(db, item_id):
            return sample_items.get(item_id)
        
        mock_get_item.side_effect = get_item_side_effect
        mock_payment.return_value = False
        
        with pytest.raises(HTTPException) as exc_info:
            order_service.create_order(sample_order_create)
        
        assert exc_info.value.status_code == status.HTTP_402_PAYMENT_REQUIRED
        assert exc_info.value.detail == "Payment processing failed"
    
    @patch('checkout.service.service.repository.get_order_by_id')
    def test_get_order_by_id_success(self, mock_get_order, order_service):
        """Test successful order retrieval by ID"""
        sample_order = models.Order(id=1, total=25.98, payment_key="test_key")
        mock_get_order.return_value = sample_order
        
        result = order_service.get_order_by_id(1)
        
        assert result.id == 1
        assert result.total == 25.98
        mock_get_order.assert_called_once_with(order_service.db, order_id=1)
    
    @patch('checkout.service.service.repository.get_order_by_id')
    def test_get_order_by_id_not_found(self, mock_get_order, order_service):
        """Test order retrieval when order doesn't exist"""
        mock_get_order.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            order_service.get_order_by_id(999)
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert exc_info.value.detail == "Order not found"
    
    def test_create_order_total_calculation_edge_cases(self, order_service):
        """Test total calculation with edge cases"""
        sample_items = {
            1: models.Item(id=1, name="Item1", price=0.01, image_id="item1.jpg", category_id=1),
            2: models.Item(id=2, name="Item2", price=999.99, image_id="item2.jpg", category_id=1)
        }
        
        with patch('checkout.service.service.repository.get_item_by_id') as mock_get_item:
            def get_item_side_effect(db, item_id):
                return sample_items.get(item_id)
            
            mock_get_item.side_effect = get_item_side_effect
            
            # Test with very small amounts
            order_data = schemas.OrderCreate(
                items=[schemas.OrderItemCreate(item_id=1, quantity=100)],
                total=1.00,  # 0.01 * 100
                payment=schemas.PaymentData(
                    card_number="1234567890123456",
                    card_holder_name="John Doe",
                    expiry_month=12,
                    expiry_year=2025,
                    cvv="123"
                )
            )
            
            with patch('checkout.service.service.FakePaymentService.process_payment', return_value=True), \
                 patch('checkout.service.service.repository.create_order') as mock_create:
                mock_create.return_value = models.Order(id=1, total=1.00, payment_key="key")
                
                result = order_service.create_order(order_data)
                assert result.total == 1.00


class TestAdminService:
    """Test cases for AdminService"""
    
    @pytest.fixture
    def mock_db(self):
        """Create mock database session"""
        return Mock(spec=Session)
    
    @pytest.fixture
    def admin_service(self, mock_db):
        """Create AdminService instance with mock database"""
        return AdminService(mock_db)
    
    @pytest.fixture
    def sample_categories(self):
        """Sample existing categories"""
        return [
            models.Category(id=1, name="Existing Category", image="existing.jpg")
        ]
    
    @patch('checkout.service.service.repository.create_category')
    @patch('checkout.service.service.repository.get_categories')
    def test_create_category_success(self, mock_get_categories, mock_create_category, admin_service):
        """Test successful category creation"""
        mock_get_categories.return_value = []
        created_category = models.Category(id=1, name="New Category", image="new.jpg")
        mock_create_category.return_value = created_category
        
        category_data = schemas.CategoryCreate(name="New Category", image="new.jpg")
        result = admin_service.create_category(category_data)
        
        assert result.name == "New Category"
        assert result.image == "new.jpg"
        mock_create_category.assert_called_once()
    
    @patch('checkout.service.service.repository.get_categories')
    def test_create_category_empty_name(self, mock_get_categories, admin_service):
        """Test category creation with empty name"""
        mock_get_categories.return_value = []
        
        category_data = schemas.CategoryCreate(name="", image="test.jpg")
        
        with pytest.raises(HTTPException) as exc_info:
            admin_service.create_category(category_data)
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Category name is required" in exc_info.value.detail
    
    @patch('checkout.service.service.repository.get_categories')
    def test_create_category_name_too_long(self, mock_get_categories, admin_service):
        """Test category creation with name too long"""
        mock_get_categories.return_value = []
        
        long_name = "a" * 101  # 101 characters
        category_data = schemas.CategoryCreate(name=long_name, image="test.jpg")
        
        with pytest.raises(HTTPException) as exc_info:
            admin_service.create_category(category_data)
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "cannot exceed 100 characters" in exc_info.value.detail
    
    @patch('checkout.service.service.repository.get_categories')
    def test_create_category_duplicate_name(self, mock_get_categories, admin_service, sample_categories):
        """Test category creation with duplicate name"""
        mock_get_categories.return_value = sample_categories
        
        category_data = schemas.CategoryCreate(name="Existing Category", image="test.jpg")
        
        with pytest.raises(HTTPException) as exc_info:
            admin_service.create_category(category_data)
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in exc_info.value.detail
    
    @patch('checkout.service.service.repository.get_categories')
    def test_create_category_duplicate_name_case_insensitive(self, mock_get_categories, admin_service, sample_categories):
        """Test category creation with duplicate name (case insensitive)"""
        mock_get_categories.return_value = sample_categories
        
        category_data = schemas.CategoryCreate(name="EXISTING CATEGORY", image="test.jpg")
        
        with pytest.raises(HTTPException) as exc_info:
            admin_service.create_category(category_data)
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in exc_info.value.detail
    
    @patch('checkout.service.service.repository.get_categories')
    def test_create_category_image_too_long(self, mock_get_categories, admin_service):
        """Test category creation with image filename too long"""
        mock_get_categories.return_value = []
        
        long_image = "a" * 256  # 256 characters
        category_data = schemas.CategoryCreate(name="Valid Name", image=long_image)
        
        with pytest.raises(HTTPException) as exc_info:
            admin_service.create_category(category_data)
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "cannot exceed 255 characters" in exc_info.value.detail
    
    @patch('checkout.service.service.repository.create_item')
    @patch('checkout.service.service.repository.get_items')
    @patch('checkout.service.service.repository.get_categories')
    def test_create_item_success(self, mock_get_categories, mock_get_items, mock_create_item, admin_service):
        """Test successful item creation"""
        mock_get_categories.return_value = [models.Category(id=1, name="Test Category")]
        mock_get_items.return_value = []
        created_item = models.Item(id=1, name="New Item", price=12.99, category_id=1)
        mock_create_item.return_value = created_item
        
        item_data = schemas.ItemCreate(
            name="New Item",
            price=12.99,
            image_id="item.jpg",
            category_id=1
        )
        result = admin_service.create_item(item_data)
        
        assert result.name == "New Item"
        assert result.price == 12.99
        mock_create_item.assert_called_once()
    
    @patch('checkout.service.service.repository.get_categories')
    def test_create_item_empty_name(self, mock_get_categories, admin_service):
        """Test item creation with empty name"""
        mock_get_categories.return_value = [models.Category(id=1, name="Test Category")]
        
        item_data = schemas.ItemCreate(name="", price=12.99, category_id=1)
        
        with pytest.raises(HTTPException) as exc_info:
            admin_service.create_item(item_data)
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Item name is required" in exc_info.value.detail
    
    @patch('checkout.service.service.repository.get_categories')
    def test_create_item_category_not_found(self, mock_get_categories, admin_service):
        """Test item creation with non-existent category"""
        mock_get_categories.return_value = [models.Category(id=1, name="Test Category")]
        
        item_data = schemas.ItemCreate(name="Valid Item", price=12.99, category_id=999)
        
        with pytest.raises(HTTPException) as exc_info:
            admin_service.create_item(item_data)
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Category with ID 999 does not exist" in exc_info.value.detail
    
    @patch('checkout.service.service.repository.get_items')
    @patch('checkout.service.service.repository.get_categories')
    def test_create_item_duplicate_name_in_category(self, mock_get_categories, mock_get_items, admin_service):
        """Test item creation with duplicate name in same category"""
        mock_get_categories.return_value = [models.Category(id=1, name="Test Category")]
        existing_item = models.Item(id=1, name="Existing Item", price=10.99, category_id=1)
        mock_get_items.return_value = [existing_item]
        
        item_data = schemas.ItemCreate(name="Existing Item", price=12.99, category_id=1)
        
        with pytest.raises(HTTPException) as exc_info:
            admin_service.create_item(item_data)
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists in this category" in exc_info.value.detail
    
    @patch('checkout.service.service.repository.get_items')
    @patch('checkout.service.service.repository.get_categories')
    def test_create_item_name_too_long(self, mock_get_categories, mock_get_items, admin_service):
        """Test item creation with name too long"""
        mock_get_categories.return_value = [models.Category(id=1, name="Test Category")]
        mock_get_items.return_value = []
        
        long_name = "a" * 201  # 201 characters
        item_data = schemas.ItemCreate(name=long_name, price=12.99, category_id=1)
        
        with pytest.raises(HTTPException) as exc_info:
            admin_service.create_item(item_data)
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "cannot exceed 200 characters" in exc_info.value.detail
    
    @patch('checkout.service.service.repository.get_items')
    @patch('checkout.service.service.repository.get_categories')
    def test_create_item_image_id_too_long(self, mock_get_categories, mock_get_items, admin_service):
        """Test item creation with image ID too long"""
        mock_get_categories.return_value = [models.Category(id=1, name="Test Category")]
        mock_get_items.return_value = []
        
        long_image_id = "a" * 256  # 256 characters
        item_data = schemas.ItemCreate(name="Valid Item", price=12.99, image_id=long_image_id, category_id=1)
        
        with pytest.raises(HTTPException) as exc_info:
            admin_service.create_item(item_data)
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Image ID cannot exceed 255 characters" in exc_info.value.detail
    
    @patch('checkout.service.service.repository.create_item')
    @patch('checkout.service.service.repository.get_items')
    @patch('checkout.service.service.repository.get_categories')
    def test_create_item_database_error(self, mock_get_categories, mock_get_items, mock_create_item, admin_service):
        """Test item creation when database error occurs"""
        mock_get_categories.return_value = [models.Category(id=1, name="Test Category")]
        mock_get_items.return_value = []
        mock_create_item.side_effect = Exception("Database error")
        
        item_data = schemas.ItemCreate(name="Valid Item", price=12.99, category_id=1)
        
        with pytest.raises(HTTPException) as exc_info:
            admin_service.create_item(item_data)
        
        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "An error occurred while creating the item" in exc_info.value.detail


class TestServiceDependencies:
    """Test cases for service dependency functions"""
    
    @patch('checkout.service.service.get_db')
    def test_get_menu_service(self, mock_get_db):
        """Test MenuService dependency injection"""
        from checkout.service.service import get_menu_service
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        service = get_menu_service(mock_db)
        assert isinstance(service, MenuService)
        assert service.db == mock_db
    
    @patch('checkout.service.service.get_db')
    def test_get_order_service(self, mock_get_db):
        """Test OrderService dependency injection"""
        from checkout.service.service import get_order_service
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        service = get_order_service(mock_db)
        assert isinstance(service, OrderService)
        assert service.db == mock_db
    
    @patch('checkout.service.service.get_db')
    def test_get_admin_service(self, mock_get_db):
        """Test AdminService dependency injection"""
        from checkout.service.service import get_admin_service
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        service = get_admin_service(mock_db)
        assert isinstance(service, AdminService)
        assert service.db == mock_db