"""
Database connection management for SQLite and PostgreSQL.
Supports automatic switching based on environment.
"""

import os
from contextlib import contextmanager
from typing import Generator, Optional

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from .models import Base


# Module-level engine instance (lazy-initialized)
engine: Optional[Engine] = None


def get_database_url() -> str:
    """
    Get database URL from environment or default to SQLite.

    Environment variables:
        DATABASE_URL: Full database connection string
        DB_TYPE: 'sqlite' or 'postgresql' (default: sqlite)
        DB_PATH: Path for SQLite database (default: ./data/recipes.db)
        POSTGRES_USER: PostgreSQL username
        POSTGRES_PASSWORD: PostgreSQL password
        POSTGRES_HOST: PostgreSQL host (default: localhost)
        POSTGRES_PORT: PostgreSQL port (default: 5432)
        POSTGRES_DB: PostgreSQL database name
    """
    # Check for explicit DATABASE_URL
    if db_url := os.getenv('DATABASE_URL'):
        return db_url

    # Determine database type
    db_type = os.getenv('DB_TYPE', 'sqlite').lower()

    if db_type == 'sqlite':
        db_path = os.getenv('DB_PATH', './data/recipes.db')
        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
        return f'sqlite:///{db_path}'

    elif db_type == 'postgresql':
        user = os.getenv('POSTGRES_USER', 'postgres')
        password = os.getenv('POSTGRES_PASSWORD', '')
        host = os.getenv('POSTGRES_HOST', 'localhost')
        port = os.getenv('POSTGRES_PORT', '5432')
        database = os.getenv('POSTGRES_DB', 'recipes')

        return f'postgresql://{user}:{password}@{host}:{port}/{database}'

    else:
        raise ValueError(f"Unsupported database type: {db_type}")


def get_engine(database_url: Optional[str] = None, echo: bool = False) -> Engine:
    """
    Create and configure SQLAlchemy engine.

    Args:
        database_url: Database connection string (auto-detected if None)
        echo: Enable SQL query logging

    Returns:
        Configured SQLAlchemy engine
    """
    url = database_url or get_database_url()

    # SQLite-specific configuration
    if url.startswith('sqlite'):
        engine = create_engine(
            url,
            echo=echo,
            connect_args={'check_same_thread': False},
            poolclass=StaticPool
        )

        # Enable foreign keys for SQLite
        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_conn, connection_record):
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    # PostgreSQL configuration
    else:
        engine = create_engine(
            url,
            echo=echo,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,  # Verify connections before using
            pool_recycle=3600    # Recycle connections after 1 hour
        )

    return engine


# Global session factory
_SessionFactory: Optional[sessionmaker] = None


def get_session_factory(engine: Optional[Engine] = None) -> sessionmaker:
    """
    Get or create session factory.

    Args:
        engine: SQLAlchemy engine (creates new if None)

    Returns:
        Session factory
    """
    global _SessionFactory

    if _SessionFactory is None:
        if engine is None:
            engine = get_engine()
        _SessionFactory = sessionmaker(bind=engine, expire_on_commit=False)

    return _SessionFactory


def get_session(engine: Optional[Engine] = None) -> Session:
    """
    Get a new database session.

    Args:
        engine: SQLAlchemy engine (uses default if None)

    Returns:
        Database session
    """
    factory = get_session_factory(engine)
    return factory()


def get_db_session(engine: Optional[Engine] = None) -> Generator[Session, None, None]:
    """
    Generator that yields a database session for dependency injection.
    Used by CLI commands for session management.

    Usage:
        session = next(get_db_session())
        try:
            # Use session
        finally:
            session.close()

    Args:
        engine: SQLAlchemy engine (uses default if None)

    Yields:
        Database session
    """
    session = get_session(engine)
    try:
        yield session
    finally:
        session.close()


@contextmanager
def session_scope(engine: Optional[Engine] = None) -> Generator[Session, None, None]:
    """
    Context manager for database sessions with automatic commit/rollback.

    Usage:
        with session_scope() as session:
            recipe = session.query(Recipe).first()

    Args:
        engine: SQLAlchemy engine (uses default if None)

    Yields:
        Database session
    """
    session = get_session(engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def create_tables(engine: Optional[Engine] = None, drop_existing: bool = False) -> None:
    """
    Create all database tables.

    Args:
        engine: SQLAlchemy engine (uses default if None)
        drop_existing: Drop existing tables before creating
    """
    if engine is None:
        engine = get_engine()

    if drop_existing:
        Base.metadata.drop_all(engine)

    Base.metadata.create_all(engine)


def init_database(
    database_url: Optional[str] = None,
    drop_existing: bool = False,
    seed_data: bool = True
) -> Engine:
    """
    Initialize database with tables and optional seed data.

    Args:
        database_url: Database connection string
        drop_existing: Drop existing tables before creating
        seed_data: Insert initial seed data

    Returns:
        Configured engine
    """
    global engine
    engine = get_engine(database_url)
    create_tables(engine, drop_existing)

    if seed_data:
        from .seed import seed_initial_data
        seed_initial_data(engine)

    return engine


def check_connection(engine: Optional[Engine] = None) -> bool:
    """
    Verify database connection.

    Args:
        engine: SQLAlchemy engine (uses default if None)

    Returns:
        True if connection successful
    """
    if engine is None:
        engine = get_engine()

    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False
