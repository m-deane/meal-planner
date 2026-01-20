"""
Dependency injection utilities for FastAPI endpoints.
Provides database sessions, authentication, and common dependencies.
"""

from datetime import datetime, timedelta
from typing import Annotated, Generator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from src.database.connection import get_session
from src.api.config import api_config

# Security scheme for JWT
security = HTTPBearer(auto_error=False)


def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency for FastAPI endpoints.

    Yields:
        Database session that is automatically closed after request

    Example:
        @app.get("/recipes")
        def list_recipes(db: Session = Depends(get_db)):
            return db.query(Recipe).all()
    """
    session = get_session()
    try:
        yield session
    finally:
        session.close()


# Type alias for cleaner dependency injection
DatabaseSession = Annotated[Session, Depends(get_db)]


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.

    Args:
        data: Payload data to encode in the token
        expires_delta: Custom expiration time (default: from config)

    Returns:
        Encoded JWT token string

    Example:
        token = create_access_token({"sub": "user123", "role": "admin"})
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=api_config.jwt_expire_minutes)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        api_config.jwt_secret,
        algorithm=api_config.jwt_algorithm
    )

    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """
    Decode and verify a JWT access token.

    Args:
        token: JWT token string

    Returns:
        Decoded token payload

    Raises:
        JWTError: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            api_config.jwt_secret,
            algorithms=[api_config.jwt_algorithm]
        )
        return payload
    except JWTError as e:
        raise JWTError(f"Token validation failed: {str(e)}")


def get_current_user(
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(security)]
) -> dict:
    """
    Dependency to get current authenticated user from JWT token.

    Args:
        credentials: HTTP Bearer token from Authorization header

    Returns:
        User information from token payload

    Raises:
        HTTPException: 401 if token is missing or invalid

    Example:
        @app.get("/profile")
        def get_profile(user: dict = Depends(get_current_user)):
            return {"username": user["sub"]}
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    try:
        payload = decode_access_token(token)
        user_id: str = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return payload

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user_optional(
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(security)]
) -> Optional[dict]:
    """
    Dependency to optionally get current user (for endpoints that work with/without auth).

    Args:
        credentials: HTTP Bearer token from Authorization header

    Returns:
        User information from token payload or None if not authenticated

    Example:
        @app.get("/recipes")
        def list_recipes(user: Optional[dict] = Depends(get_current_user_optional)):
            # Show personalized results if user is authenticated
            if user:
                return get_personalized_recipes(user["sub"])
            return get_public_recipes()
    """
    if credentials is None:
        return None

    try:
        token = credentials.credentials
        payload = decode_access_token(token)
        user_id: str = payload.get("sub")

        if user_id is None:
            return None

        return payload

    except JWTError:
        return None


# Type aliases for cleaner dependency injection
CurrentUser = Annotated[dict, Depends(get_current_user)]
OptionalUser = Annotated[Optional[dict], Depends(get_current_user_optional)]


def verify_admin_role(user: CurrentUser) -> dict:
    """
    Dependency to verify user has admin role.

    Args:
        user: Current authenticated user

    Returns:
        User information

    Raises:
        HTTPException: 403 if user is not an admin

    Example:
        @app.delete("/recipes/{recipe_id}")
        def delete_recipe(
            recipe_id: int,
            admin: dict = Depends(verify_admin_role)
        ):
            # Only admins can access this endpoint
            pass
    """
    role = user.get("role")

    if role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    return user


# Type alias for admin dependency
AdminUser = Annotated[dict, Depends(verify_admin_role)]


def get_pagination_params(
    skip: int = 0,
    limit: int = api_config.pagination_default_limit
) -> tuple[int, int]:
    """
    Dependency for pagination parameters with validation.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        Validated (skip, limit) tuple

    Raises:
        HTTPException: 400 if parameters are invalid

    Example:
        @app.get("/recipes")
        def list_recipes(
            db: DatabaseSession,
            pagination: tuple[int, int] = Depends(get_pagination_params)
        ):
            skip, limit = pagination
            return db.query(Recipe).offset(skip).limit(limit).all()
    """
    if skip < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="skip parameter must be >= 0"
        )

    if limit < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="limit parameter must be >= 1"
        )

    if limit > api_config.pagination_max_limit:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"limit parameter must be <= {api_config.pagination_max_limit}"
        )

    return skip, limit


# Type alias for pagination dependency
PaginationParams = Annotated[tuple[int, int], Depends(get_pagination_params)]
