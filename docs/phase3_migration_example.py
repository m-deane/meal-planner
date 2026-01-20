"""
Phase 3 Database Migration Example

This script demonstrates how to add the new user-related tables
to an existing meal-planner database.

WARNING: Always backup your database before running migrations!
"""

import sys
from pathlib import Path
from datetime import datetime
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.database.models import Base, SchemaVersion


def check_existing_tables(engine):
    """Check which tables already exist in the database."""
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()

    print("\n" + "="*60)
    print("EXISTING TABLES")
    print("="*60)
    for table in sorted(existing_tables):
        print(f"  ✓ {table}")
    print(f"\nTotal: {len(existing_tables)} tables")

    return existing_tables


def get_new_tables():
    """Get list of Phase 3 tables."""
    return [
        'users',
        'user_preferences',
        'favorite_recipes',
        'saved_meal_plans',
        'user_allergens',
        'ingredient_prices'
    ]


def verify_prerequisites(engine):
    """Verify that prerequisite tables exist."""
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()

    required_tables = ['recipes', 'ingredients', 'units', 'allergens']
    missing_tables = [t for t in required_tables if t not in existing_tables]

    if missing_tables:
        print("\n❌ ERROR: Missing prerequisite tables:")
        for table in missing_tables:
            print(f"  - {table}")
        return False

    print("\n✓ All prerequisite tables exist")
    return True


def create_phase3_tables(engine):
    """Create only the new Phase 3 tables."""
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    new_tables = get_new_tables()

    print("\n" + "="*60)
    print("CREATING PHASE 3 TABLES")
    print("="*60)

    # SQLAlchemy's create_all() only creates tables that don't exist
    Base.metadata.create_all(engine)

    # Verify new tables were created
    inspector = inspect(engine)
    current_tables = inspector.get_table_names()

    created_tables = [t for t in new_tables if t in current_tables and t not in existing_tables]

    if created_tables:
        print("\n✓ Successfully created tables:")
        for table in created_tables:
            print(f"  - {table}")
    else:
        print("\n⚠ No new tables created (they may already exist)")

    return created_tables


def add_schema_version(engine, version="3.0.0", description="Phase 3: User models"):
    """Record the migration in schema_version table."""
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Check if version already exists
        existing = session.query(SchemaVersion).filter_by(version=version).first()

        if existing:
            print(f"\n⚠ Schema version {version} already recorded")
            return

        # Add new schema version
        schema_version = SchemaVersion(
            version=version,
            description=description,
            applied_at=datetime.utcnow()
        )
        session.add(schema_version)
        session.commit()

        print(f"\n✓ Recorded schema version: {version}")

    except Exception as e:
        session.rollback()
        print(f"\n❌ Error recording schema version: {e}")
    finally:
        session.close()


def verify_table_structure(engine, table_name):
    """Verify table structure after creation."""
    inspector = inspect(engine)

    # Get columns
    columns = inspector.get_columns(table_name)

    # Get indexes
    indexes = inspector.get_indexes(table_name)

    # Get foreign keys
    foreign_keys = inspector.get_foreign_keys(table_name)

    print(f"\nTable: {table_name}")
    print(f"  Columns: {len(columns)}")
    print(f"  Indexes: {len(indexes)}")
    print(f"  Foreign Keys: {len(foreign_keys)}")

    return {
        'columns': columns,
        'indexes': indexes,
        'foreign_keys': foreign_keys
    }


def run_migration(database_url, verify_only=False):
    """
    Run the Phase 3 migration.

    Args:
        database_url: SQLAlchemy database URL
        verify_only: If True, only check status without making changes
    """
    print("\n" + "="*60)
    print("PHASE 3 MIGRATION: USER MODELS")
    print("="*60)
    print(f"\nDatabase: {database_url}")
    print(f"Mode: {'VERIFY ONLY' if verify_only else 'MIGRATE'}")

    # Create engine
    engine = create_engine(database_url, echo=False)

    # Step 1: Check existing tables
    existing_tables = check_existing_tables(engine)

    # Step 2: Verify prerequisites
    if not verify_prerequisites(engine):
        print("\n❌ Migration aborted: Prerequisites not met")
        return False

    # Step 3: Check which new tables already exist
    new_tables = get_new_tables()
    already_exists = [t for t in new_tables if t in existing_tables]
    to_create = [t for t in new_tables if t not in existing_tables]

    if already_exists:
        print("\n⚠ Tables already exist:")
        for table in already_exists:
            print(f"  - {table}")

    if to_create:
        print("\n📋 Tables to create:")
        for table in to_create:
            print(f"  - {table}")
    else:
        print("\n✓ All Phase 3 tables already exist")
        return True

    # Step 4: Create tables (if not verify-only mode)
    if not verify_only:
        if to_create:
            response = input("\nProceed with migration? (yes/no): ")
            if response.lower() != 'yes':
                print("\n❌ Migration cancelled by user")
                return False

            created = create_phase3_tables(engine)

            # Step 5: Verify table structure
            print("\n" + "="*60)
            print("VERIFYING TABLE STRUCTURE")
            print("="*60)
            for table in created:
                verify_table_structure(engine, table)

            # Step 6: Record schema version
            add_schema_version(engine, "3.0.0", "Phase 3: User models and personalization")

            print("\n" + "="*60)
            print("✓ MIGRATION COMPLETED SUCCESSFULLY")
            print("="*60)

            return True
    else:
        print("\n" + "="*60)
        print("VERIFICATION COMPLETE (No changes made)")
        print("="*60)
        return True


def rollback_migration(database_url):
    """
    Rollback Phase 3 migration by dropping tables.

    WARNING: This will delete all user data!
    """
    print("\n" + "="*60)
    print("⚠ WARNING: ROLLBACK PHASE 3 MIGRATION")
    print("="*60)
    print("\nThis will DELETE the following tables and ALL their data:")

    new_tables = get_new_tables()
    for table in new_tables:
        print(f"  - {table}")

    response = input("\nType 'DELETE ALL USER DATA' to confirm: ")
    if response != 'DELETE ALL USER DATA':
        print("\n❌ Rollback cancelled")
        return False

    engine = create_engine(database_url, echo=False)

    # Drop tables in reverse order to handle foreign key constraints
    for table_name in reversed(new_tables):
        try:
            with engine.connect() as conn:
                conn.execute(text(f"DROP TABLE IF EXISTS {table_name}"))
                conn.commit()
                print(f"✓ Dropped table: {table_name}")
        except Exception as e:
            print(f"❌ Error dropping {table_name}: {e}")

    print("\n✓ Rollback completed")
    return True


# Example usage
if __name__ == "__main__":
    import sys

    # Default to SQLite for testing
    DATABASE_URL = "sqlite:///data/recipes.db"

    # Parse command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "verify":
            # Just verify, don't make changes
            run_migration(DATABASE_URL, verify_only=True)

        elif command == "migrate":
            # Run the migration
            run_migration(DATABASE_URL, verify_only=False)

        elif command == "rollback":
            # Rollback the migration
            rollback_migration(DATABASE_URL)

        elif command == "help":
            print("""
Phase 3 Migration Script

Usage:
    python docs/phase3_migration_example.py [command]

Commands:
    verify      Check migration status without making changes
    migrate     Run the migration (interactive confirmation)
    rollback    Rollback migration (WARNING: deletes all user data)
    help        Show this help message

Examples:
    # Check status
    python docs/phase3_migration_example.py verify

    # Run migration
    python docs/phase3_migration_example.py migrate

    # For PostgreSQL
    DATABASE_URL="postgresql://user:pass@localhost/dbname" \\
        python docs/phase3_migration_example.py migrate
            """)
        else:
            print(f"Unknown command: {command}")
            print("Run with 'help' for usage information")
    else:
        # No arguments, run verification
        print("No command specified. Running verification...")
        print("Use 'help' for usage information\n")
        run_migration(DATABASE_URL, verify_only=True)
