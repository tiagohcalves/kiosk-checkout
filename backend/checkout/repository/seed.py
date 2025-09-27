"""
Seed script to populate the database with sample menu data
"""

import json
import sys
import argparse
from pathlib import Path

from checkout.repository.database import SessionLocal, create_tables
from checkout.repository.repository import create_category, create_item
from checkout.models.schemas import CategoryCreate, ItemCreate


def load_menu_data(json_file_path: str) -> dict:
    """Load menu data from JSON file"""
    try:
        json_path = Path(json_file_path)
        if not json_path.exists():
            raise FileNotFoundError(f"JSON file not found: {json_file_path}")

        with open(json_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        # Validate required keys
        if "categories" not in data or "items" not in data:
            raise ValueError("JSON file must contain 'categories' and 'items' keys")

        return data

    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {e}")
    except Exception as e:
        raise Exception(f"Error loading JSON file: {e}")


def seed_database(menu_data: dict):
    """Seed the database with menu data"""
    db = SessionLocal()

    try:
        # Create categories first
        category_mapping = {}
        for cat_data in menu_data["categories"]:
            # Remove 'id' from category data if present, as it will be auto-generated
            cat_create_data = {k: v for k, v in cat_data.items() if k != "id"}
            category = create_category(db, CategoryCreate(**cat_create_data))
            category_mapping[cat_data.get("name", "")] = category.id
            print(f"Created category: {category.name}")

        # Create items
        for item_data in menu_data["items"]:
            # Remove 'id' from item data if present, as it will be auto-generated
            item_create_data = {k: v for k, v in item_data.items() if k != "id"}
            item = create_item(db, ItemCreate(**item_create_data))
            print(f"Created item: {item.name} - ${item.price}")

        print(
            f"Successfully seeded database with {len(menu_data['categories'])} categories and {len(menu_data['items'])} items"
        )

    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def main():
    """Main function to handle command line arguments and seed the database"""
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

    try:
        # Load menu data from JSON file
        print(f"Loading menu data from: {args.json_file}")
        menu_data = load_menu_data(args.json_file)

        # Create tables if they don't exist
        print("Creating database tables...")
        create_tables()

        # Seed the database
        print("Seeding database...")
        seed_database(menu_data)

        print("Database seeding completed successfully!")

    except Exception as e:
        print(f"Failed to seed database: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
