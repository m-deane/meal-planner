"""
FastAPI routers for meal planner API.
"""

from .recipes import router as recipes_router
from .categories import (
    router as categories_router,
    dietary_tags_router,
    allergens_router,
)
from .meal_plans import router as meal_plans_router
from .shopping_lists import router as shopping_lists_router
from .auth import auth_router
from .users import users_router
from .cost import router as cost_router
from .multi_week import router as multi_week_router
from .safe_recipes import router as safe_recipes_router
from .favorites import router as favorites_router

__all__ = [
    "recipes_router",
    "categories_router",
    "dietary_tags_router",
    "allergens_router",
    "meal_plans_router",
    "shopping_lists_router",
    "auth_router",
    "users_router",
    "cost_router",
    "multi_week_router",
    "safe_recipes_router",
    "favorites_router",
]
