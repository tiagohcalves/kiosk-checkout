from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status

from checkout.repository.database import get_db
import checkout.repository.repository as repository
import checkout.models.schemas as schemas
from checkout.utils.logging_config import get_logger

logger = get_logger(__name__)


class AdminService:
    """Service class for admin operations"""

    def __init__(self, db: Session):
        """Initialize the service with a database session"""
        self.db = db
        logger.debug("AdminService initialized")

    def create_category(self, category: schemas.CategoryCreate) -> schemas.Category:
        """Create a new category with validation"""
        logger.info(f"AdminService: Creating category '{category.name}'")

        try:
            # Basic validation
            logger.debug("AdminService: Starting category validation")
            if not category.name or not category.name.strip():
                logger.warning("AdminService: Category name is empty")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Category name is required and cannot be empty",
                )

            # Check name length
            if len(category.name.strip()) > 100:
                logger.warning(
                    f"AdminService: Category name too long: {len(category.name.strip())} characters"
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Category name cannot exceed 100 characters",
                )

            # Check for duplicate category names
            logger.debug("AdminService: Checking for duplicate category names")
            existing_categories = repository.get_categories(self.db)
            if any(
                cat.name.lower() == category.name.strip().lower()
                for cat in existing_categories
            ):
                logger.warning(
                    f"AdminService: Duplicate category name: '{category.name}'"
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="A category with this name already exists",
                )

            # Validate image field if provided
            if category.image and len(category.image) > 255:
                logger.warning(
                    f"AdminService: Image filename too long: {len(category.image)} characters"
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Image filename cannot exceed 255 characters",
                )

            logger.debug(
                "AdminService: Category validation successful, creating category"
            )
            created_category = repository.create_category(db=self.db, category=category)
            logger.info(
                f"AdminService: Successfully created category ID: {created_category.id}, name: '{created_category.name}'"
            )
            return created_category

        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                f"AdminService: Unexpected error creating category: {str(e)}",
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while creating the category",
            )

    def create_item(self, item: schemas.ItemCreate) -> schemas.Item:
        """Create a new menu item with validation"""
        logger.info(
            f"AdminService: Creating item '{item.name}', price: ${item.price:.2f}, category_id: {item.category_id}"
        )

        try:
            # Basic validation
            logger.debug("AdminService: Starting item validation")
            if not item.name or not item.name.strip():
                logger.warning("AdminService: Item name is empty")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Item name is required and cannot be empty",
                )

            # Check name length
            if len(item.name.strip()) > 200:
                logger.warning(
                    f"AdminService: Item name too long: {len(item.name.strip())} characters"
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Item name cannot exceed 200 characters",
                )

            # Validate price
            if item.price <= 0:
                logger.warning(f"AdminService: Invalid price: ${item.price:.2f}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Price must be greater than 0",
                )

            # Validate category exists
            logger.debug(
                f"AdminService: Validating category exists: {item.category_id}"
            )
            categories = repository.get_categories(self.db)
            if not any(cat.id == item.category_id for cat in categories):
                logger.warning(f"AdminService: Category not found: {item.category_id}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Category with ID {item.category_id} does not exist",
                )

            # Check for duplicate item names within the same category
            logger.debug(
                f"AdminService: Checking for duplicate item names in category {item.category_id}"
            )
            existing_items = repository.get_items(self.db, category_id=item.category_id)
            if any(
                existing_item.name.lower() == item.name.strip().lower()
                for existing_item in existing_items
            ):
                logger.warning(
                    f"AdminService: Duplicate item name in category {item.category_id}: '{item.name}'"
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="An item with this name already exists in this category",
                )

            if item.image_id and len(item.image_id) > 255:
                logger.warning(
                    f"AdminService: Image ID too long: {len(item.image_id)} characters"
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Image ID cannot exceed 255 characters",
                )

            logger.debug("AdminService: Item validation successful, creating item")
            created_item = repository.create_item(db=self.db, item=item)
            logger.info(
                f"AdminService: Successfully created item ID: {created_item.id}, name: '{created_item.name}'"
            )
            return created_item

        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                f"AdminService: Unexpected error creating item: {str(e)}", exc_info=True
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while creating the item",
            )


# Service dependency
def get_admin_service(db: Session = Depends(get_db)) -> AdminService:
    """Dependency to get AdminService instance"""
    return AdminService(db)