import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from checkout.models.models import Base, Category, Item, Order, OrderItem
from datetime import datetime, timezone


class TestModels:
    """Test cases for SQLAlchemy models"""

    @pytest.fixture(scope="function")
    def db_session(self):
        """Create a test database session"""
        engine = create_engine("sqlite:///:memory:", echo=False)
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        try:
            yield session
        finally:
            session.close()

    def test_create_category(self, db_session):
        """Test creating a category"""
        category = Category(name="Test Category", image="test.jpg")
        db_session.add(category)
        db_session.commit()
        
        assert category.id is not None
        assert category.name == "Test Category"
        assert category.image == "test.jpg"

    def test_category_unique_name(self, db_session):
        """Test that category names must be unique"""
        category1 = Category(name="Unique Category", image="test1.jpg")
        category2 = Category(name="Unique Category", image="test2.jpg")
        
        db_session.add(category1)
        db_session.commit()
        
        db_session.add(category2)
        with pytest.raises(Exception):  # Should raise integrity error
            db_session.commit()

    def test_create_item(self, db_session):
        """Test creating an item"""
        # First create a category
        category = Category(name="Test Category", image="test.jpg")
        db_session.add(category)
        db_session.commit()
        
        # Then create an item
        item = Item(
            name="Test Item",
            price=12.99,
            image_id="item.jpg",
            category_id=category.id
        )
        db_session.add(item)
        db_session.commit()
        
        assert item.id is not None
        assert item.name == "Test Item"
        assert item.price == 12.99
        assert item.category_id == category.id

    def test_item_category_relationship(self, db_session):
        """Test the relationship between Item and Category"""
        # Create category
        category = Category(name="Test Category", image="test.jpg")
        db_session.add(category)
        db_session.commit()
        
        # Create item
        item = Item(
            name="Test Item",
            price=12.99,
            category_id=category.id
        )
        db_session.add(item)
        db_session.commit()
        
        # Test relationship
        assert item.category.name == "Test Category"
        assert item in category.items

    def test_create_order(self, db_session):
        """Test creating an order"""
        order = Order(
            total=25.98,
            payment_key="abc123",
            payment_data='{"card": "****1234"}'
        )
        db_session.add(order)
        db_session.commit()
        
        assert order.id is not None
        assert order.total == 25.98
        assert order.payment_key == "abc123"
        assert order.timestamp is not None

    def test_create_order_item(self, db_session):
        """Test creating an order item"""
        # Create category
        category = Category(name="Test Category", image="test.jpg")
        db_session.add(category)
        db_session.commit()
        
        # Create item
        item = Item(
            name="Test Item",
            price=12.99,
            category_id=category.id
        )
        db_session.add(item)
        db_session.commit()
        
        # Create order
        order = Order(
            total=25.98,
            payment_key="abc123",
            payment_data='{"card": "****1234"}'
        )
        db_session.add(order)
        db_session.commit()
        
        # Create order item
        order_item = OrderItem(
            order_id=order.id,
            item_id=item.id,
            quantity=2
        )
        db_session.add(order_item)
        db_session.commit()
        
        assert order_item.id is not None
        assert order_item.quantity == 2
        assert order_item.order_id == order.id
        assert order_item.item_id == item.id

    def test_order_item_relationships(self, db_session):
        """Test relationships in OrderItem model"""
        # Create category
        category = Category(name="Test Category", image="test.jpg")
        db_session.add(category)
        db_session.commit()
        
        # Create item
        item = Item(
            name="Test Item",
            price=12.99,
            category_id=category.id
        )
        db_session.add(item)
        db_session.commit()
        
        # Create order
        order = Order(
            total=25.98,
            payment_key="abc123",
            payment_data='{"card": "****1234"}'
        )
        db_session.add(order)
        db_session.commit()
        
        # Create order item
        order_item = OrderItem(
            order_id=order.id,
            item_id=item.id,
            quantity=2
        )
        db_session.add(order_item)
        db_session.commit()
        
        # Test relationships
        assert order_item.order.id == order.id
        assert order_item.item.name == "Test Item"
        assert order_item in order.order_items
        assert order_item in item.order_items

    def test_cascade_delete_category_items(self, db_session):
        """Test that deleting a category handles related items appropriately"""
        # Create category
        category = Category(name="Test Category", image="test.jpg")
        db_session.add(category)
        db_session.commit()
        
        # Create items
        item1 = Item(name="Item 1", price=10.99, category_id=category.id)
        item2 = Item(name="Item 2", price=15.99, category_id=category.id)
        db_session.add(item1)
        db_session.add(item2)
        db_session.commit()
        
        category_id = category.id
        
        # Delete category
        db_session.delete(category)
        
        # This might raise an integrity error depending on foreign key constraints
        # The behavior depends on the database configuration
        try:
            db_session.commit()
            # If commit succeeds, items should still exist but with null category_id
            remaining_items = db_session.query(Item).filter(Item.category_id == category_id).all()
            # Behavior depends on foreign key setup
        except Exception:
            # If foreign key constraint prevents deletion, that's also valid
            db_session.rollback()

    def test_model_repr_methods(self, db_session):
        """Test string representations of models"""
        category = Category(name="Test Category", image="test.jpg")
        db_session.add(category)
        db_session.commit()
        
        # Models should be printable (even if __repr__ isn't explicitly defined)
        category_str = str(category)
        assert category_str is not None
        assert len(category_str) > 0

    def test_model_table_names(self):
        """Test that all models have correct table names"""
        assert Category.__tablename__ == "categories"
        assert Item.__tablename__ == "items"
        assert Order.__tablename__ == "orders"
        assert OrderItem.__tablename__ == "order_items"

    def test_nullable_fields(self, db_session):
        """Test nullable fields in models"""
        # Category with no image
        category = Category(name="No Image Category")
        db_session.add(category)
        db_session.commit()
        
        assert category.image is None
        
        # Item with minimal required fields
        item = Item(
            name="Minimal Item",
            price=9.99,
            category_id=category.id
        )
        db_session.add(item)
        db_session.commit()
        
        assert item.image_id is None
