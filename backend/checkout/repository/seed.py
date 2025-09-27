"""
Seed script to populate the database with sample menu data
"""

import json
import sys
import argparse
from pathlib import Path

# Setup logging
from checkout.utils.logging_config import setup_logging, get_logger

setup_logging(log_level="INFO")
logger = get_logger(__name__)

from checkout.repository.database import SessionLocal, create_tables
from checkout.repository.repository import create_category, create_item
from checkout.models.schemas import CategoryCreate, ItemCreate


def load_menu_data(json_file_path: str) -> dict:
    """Load menu data from JSON file"""
    logger.info(f"Loading menu data from: {json_file_path}")

    try:
        json_path = Path(json_file_path)
        if not json_path.exists():
            logger.error(f"JSON file not found: {json_file_path}")
            raise FileNotFoundError(f"JSON file not found: {json_file_path}")

        logger.debug(f"Reading JSON file: {json_path}")
        with open(json_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        # Validate required keys
        if "categories" not in data or "items" not in data:
            logger.error("JSON file missing required 'categories' or 'items' keys")
            raise ValueError("JSON file must contain 'categories' and 'items' keys")

        logger.info(
            f"Successfully loaded {len(data.get('categories', []))} categories and {len(data.get('items', []))} items from JSON"
        )
        return data

    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON format: {e}")
        raise ValueError(f"Invalid JSON format: {e}")
    except Exception as e:
        logger.error(f"Error loading JSON file: {e}")
        raise Exception(f"Error loading JSON file: {e}")


def seed_database(menu_data: dict):
    """Seed the database with menu data"""
    logger.info("Starting database seeding process")
    db = SessionLocal()

    try:
        # Create categories first
        logger.info(f"Creating {len(menu_data['categories'])} categories")
        category_mapping = {}
        for i, cat_data in enumerate(menu_data["categories"], 1):
            logger.debug(
                f"Creating category {i}/{len(menu_data['categories'])}: {cat_data.get('name', 'Unknown')}"
            )
            # Remove 'id' from category data if present, as it will be auto-generated
            cat_create_data = {k: v for k, v in cat_data.items() if k != "id"}
            category = create_category(db, CategoryCreate(**cat_create_data))
            category_mapping[cat_data.get("name", "")] = category.id
            logger.info(f"Created category: {category.name} (ID: {category.id})")

        # Create items
        logger.info(f"Creating {len(menu_data['items'])} items")
        for i, item_data in enumerate(menu_data["items"], 1):
            logger.debug(
                f"Creating item {i}/{len(menu_data['items'])}: {item_data.get('name', 'Unknown')}"
            )
            # Remove 'id' from item data if present, as it will be auto-generated
            item_create_data = {k: v for k, v in item_data.items() if k != "id"}
            item = create_item(db, ItemCreate(**item_create_data))
            logger.info(
                f"Created item: {item.name} - ${item.price:.2f} (ID: {item.id})"
            )

        logger.info(
            f"Successfully seeded database with {len(menu_data['categories'])} categories and {len(menu_data['items'])} items"
        )

    except Exception as e:
        logger.error(f"Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        logger.debug("Closing database session")
        db.close()


def main():
    """Main function to handle command line arguments and seed the database"""
    logger.info("Starting database seed script")

    parser = argparse.ArgumentParser(
        description="Seed the database with menu data from JSON file"
    )
    parser.add_argument(
        "json_file",
        nargs="?",
        default="../seed_data.json",
        help="Path to JSON file containing menu data (default: ../seed_data.json)",
    )

    args = parser.parse_args()
    logger.info(f"Using JSON file: {args.json_file}")

    try:
        # Load menu data from JSON file
        menu_data = load_menu_data(args.json_file)

        # Create tables if they don't exist
        logger.info("Creating database tables if they don't exist...")
        create_tables()

        # Seed the database
        seed_database(menu_data)

        logger.info("Database seeding completed successfully!")

    except Exception as e:
        logger.error(f"Failed to seed database: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
