from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from typing import List

from checkout.repository.database import get_db
import checkout.repository.repository as repository
import checkout.models.schemas as schemas
from checkout.utils.logging_config import get_logger

logger = get_logger(__name__)


class MenuService:
    """Service class for menu-related operations"""

    def __init__(self, db: Session):
        """Initialize the service with a database session"""
        self.db = db

    def get_categories(self) -> List[schemas.Category]:
        """Get all menu categories"""
        logger.debug("MenuService: Fetching all categories")
        try:
            categories = repository.get_categories(self.db)
            logger.debug(f"MenuService: Retrieved {len(categories)} categories")
            return categories
        except Exception as e:
            logger.error(f"MenuService: Failed to get categories: {str(e)}")
            raise

    def get_menu(self) -> schemas.MenuResponse:
        """Get complete menu with categories and items"""
        logger.debug("MenuService: Fetching complete menu")
        try:
            categories = repository.get_categories(self.db)
            items = repository.get_items(self.db)
            logger.debug(
                f"MenuService: Retrieved {len(categories)} categories and {len(items)} items"
            )
            return schemas.MenuResponse(categories=categories, items=items)
        except Exception as e:
            logger.error(f"MenuService: Failed to get menu: {str(e)}")
            raise

    def get_items(self, category_id: int = None) -> List[schemas.Item]:
        """Get all items or items by category"""
        if category_id:
            logger.debug(f"MenuService: Fetching items for category {category_id}")
        else:
            logger.debug("MenuService: Fetching all items")

        try:
            items = repository.get_items(self.db, category_id=category_id)
            logger.debug(f"MenuService: Retrieved {len(items)} items")
            return items
        except Exception as e:
            logger.error(f"MenuService: Failed to get items: {str(e)}")
            raise

    def get_item_by_id(self, item_id: int) -> schemas.Item:
        """Get a specific item by ID"""
        logger.debug(f"MenuService: Fetching item with ID {item_id}")
        try:
            item = repository.get_item_by_id(self.db, item_id=item_id)
            if item is None:
                logger.warning(f"MenuService: Item not found with ID {item_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
                )
            logger.debug(f"MenuService: Retrieved item '{item.name}' (ID: {item_id})")
            return item
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"MenuService: Failed to get item {item_id}: {str(e)}")
            raise


# Service dependency
def get_menu_service(db: Session = Depends(get_db)) -> MenuService:
    """Dependency to get MenuService instance"""
    return MenuService(db)