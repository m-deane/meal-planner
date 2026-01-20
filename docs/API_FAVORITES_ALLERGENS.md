# Favorites and Allergen Filtering API Guide

## Quick Reference

### Favorites Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/v1/favorites` | GET | Required | List user's favorites |
| `/api/v1/favorites/{recipe_id}` | POST | Required | Add to favorites |
| `/api/v1/favorites/{recipe_id}` | DELETE | Required | Remove from favorites |
| `/api/v1/favorites/{recipe_id}/notes` | PUT | Required | Update notes |
| `/api/v1/favorites/{recipe_id}/status` | GET | Required | Check if favorited |
| `/api/v1/favorites/count` | GET | Required | Get favorites count |

### Safe Recipes Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/v1/recipes/safe` | GET | Required | Get allergen-safe recipes |
| `/api/v1/recipes/{id}/allergen-warnings` | GET | Required | Get allergen warnings |
| `/api/v1/recipes/{id}/allergen-substitutions` | GET | Required | Get substitutions |

### Enhanced Recipe Endpoints

| Endpoint | Additional Feature |
|----------|-------------------|
| `/api/v1/recipes` | Now includes `is_favorite` field when authenticated |
| `/api/v1/recipes` | Supports `exclude_user_allergens=true` parameter |
| `/api/v1/recipes/search` | Now includes `is_favorite` field when authenticated |

## Detailed Usage

### 1. Managing Favorites

#### Add Recipe to Favorites

```http
POST /api/v1/favorites/42
Authorization: Bearer {token}
Content-Type: application/json

{
  "notes": "Kids love this recipe! Make extra sauce next time."
}
```

Response:
```json
{
  "id": 1,
  "recipe": {
    "id": 42,
    "slug": "chicken-tikka-masala",
    "name": "Chicken Tikka Masala",
    "description": "Creamy Indian curry with tender chicken",
    "cooking_time_minutes": 45,
    "difficulty": "medium",
    "image_url": "https://example.com/images/chicken-tikka.jpg"
  },
  "notes": "Kids love this recipe! Make extra sauce next time.",
  "created_at": "2026-01-20T14:30:00Z"
}
```

#### List Favorites

```http
GET /api/v1/favorites?page=1&page_size=20&order_by=created_at
Authorization: Bearer {token}
```

Query Parameters:
- `page` (int, default=1): Page number
- `page_size` (int, default=20, max=100): Items per page
- `order_by` (string, default="created_at"): Sort field (created_at or recipe.name)

Response:
```json
{
  "items": [
    {
      "id": 1,
      "recipe": {...},
      "notes": "Family favorite!",
      "created_at": "2026-01-20T14:30:00Z"
    }
  ],
  "total": 15,
  "page": 1,
  "page_size": 20,
  "pages": 1
}
```

#### Update Favorite Notes

```http
PUT /api/v1/favorites/42/notes
Authorization: Bearer {token}
Content-Type: application/json

{
  "notes": "Updated: Use less salt, add more garlic"
}
```

To clear notes, send `null`:
```json
{
  "notes": null
}
```

#### Check Favorite Status

```http
GET /api/v1/favorites/42/status
Authorization: Bearer {token}
```

Response:
```json
{
  "is_favorite": true,
  "notes": "Family favorite!",
  "created_at": "2026-01-20T14:30:00Z"
}
```

#### Remove from Favorites

```http
DELETE /api/v1/favorites/42
Authorization: Bearer {token}
```

Response:
```json
{
  "message": "Recipe removed from favorites"
}
```

#### Get Favorites Count

```http
GET /api/v1/favorites/count
Authorization: Bearer {token}
```

Response:
```json
{
  "count": 15
}
```

### 2. Allergen-Safe Recipes

#### Get Safe Recipes

Get recipes that are safe based on your allergen profile:

```http
GET /api/v1/recipes/safe?page=1&page_size=20
Authorization: Bearer {token}
```

With additional filters:
```http
GET /api/v1/recipes/safe?max_cooking_time=30&difficulty=easy&min_protein=20
Authorization: Bearer {token}
```

Query Parameters:
- `page` (int): Page number
- `page_size` (int): Items per page
- `max_cooking_time` (int): Maximum cooking time in minutes
- `difficulty` (string): easy, medium, or hard
- `category_slugs` (list): Filter by categories
- `dietary_tag_slugs` (list): Filter by dietary tags
- `min_protein` (float): Minimum protein in grams
- `max_carbs` (float): Maximum carbs in grams

Response: Standard paginated recipe list (only safe recipes)

#### Get Allergen Warnings

Check if a recipe is safe for you before viewing/making it:

```http
GET /api/v1/recipes/42/allergen-warnings
Authorization: Bearer {token}
```

Response:
```json
{
  "recipe_id": 42,
  "recipe_name": "Thai Peanut Noodles",
  "warnings": [
    {
      "allergen_name": "Peanuts",
      "severity": "severe",
      "ingredient_name": "Peanut butter",
      "message": "SEVERE ALLERGY: This recipe contains peanut butter which contains Peanuts"
    }
  ],
  "is_safe": false
}
```

Severity Levels:
- `severe`: Complete avoidance required - recipe excluded from safe recipes
- `avoid`: Should avoid - recipe excluded from safe recipes
- `trace_ok`: Can tolerate trace amounts - recipe included in safe recipes

#### Get Ingredient Substitutions

Get suggestions for making a recipe safe:

```http
GET /api/v1/recipes/42/allergen-substitutions
Authorization: Bearer {token}
```

Response:
```json
[
  {
    "original_ingredient": "Peanut butter",
    "allergen": "Peanuts",
    "substitutes": [
      "Sunflower seed butter",
      "Almond butter",
      "Tahini",
      "Soy nut butter"
    ],
    "notes": "Use equal amounts unless otherwise specified. Taste and texture may vary."
  }
]
```

### 3. Enhanced Recipe Listing

#### Recipes with Favorite Status

When authenticated, all recipe listings include `is_favorite` field:

```http
GET /api/v1/recipes?page=1&page_size=20
Authorization: Bearer {token}
```

Response includes:
```json
{
  "items": [
    {
      "id": 42,
      "name": "Chicken Tikka Masala",
      "slug": "chicken-tikka-masala",
      "is_favorite": true,
      ...
    }
  ]
}
```

If not authenticated, `is_favorite` will be `null`.

#### Filter by User Allergens

Automatically exclude recipes based on your allergen profile:

```http
GET /api/v1/recipes?exclude_user_allergens=true&page=1
Authorization: Bearer {token}
```

This combines your allergen profile filtering with any other filters:
```http
GET /api/v1/recipes?exclude_user_allergens=true&max_cooking_time=30&category_slugs=italian
Authorization: Bearer {token}
```

## Allergen Severity Guide

### Severe
- Recipe is **completely excluded** from safe recipes
- Shown with "SEVERE ALLERGY" warning
- Use for life-threatening allergies
- Example: Peanut allergy for someone with anaphylaxis risk

### Avoid
- Recipe is **excluded** from safe recipes
- Shown with "WARNING" message
- Use for strong allergies that should be avoided
- Example: Lactose intolerance

### Trace OK
- Recipe is **included** in safe recipes
- Shown with "INFO" message about trace amounts
- Use for mild sensitivities where trace amounts are acceptable
- Example: Mild gluten sensitivity (not celiac)

## Substitution Database

The system includes substitutions for common allergens:

### Peanuts
- Peanut butter → Sunflower seed butter, almond butter, tahini
- Peanuts → Almonds, cashews, sunflower seeds
- Peanut oil → Vegetable oil, canola oil

### Dairy
- Milk → Oat milk, soy milk, almond milk, coconut milk
- Butter → Margarine, coconut oil, olive oil
- Cheese → Nutritional yeast, vegan cheese
- Cream → Coconut cream, cashew cream
- Yogurt → Coconut yogurt, soy yogurt

### Eggs
- Eggs → Flax eggs, chia eggs, applesauce, banana
- Egg whites → Aquafaba (chickpea liquid)

### Gluten
- Wheat flour → Rice flour, almond flour, GF flour blend
- Pasta → Rice pasta, quinoa pasta, zucchini noodles
- Bread → Gluten-free bread, corn tortillas
- Soy sauce → Tamari (gluten-free), coconut aminos

### Soy
- Soy sauce → Coconut aminos, tamari
- Tofu → Chickpeas, white beans, tempeh
- Soy milk → Oat milk, almond milk

### Fish
- Fish sauce → Soy sauce, tamari, coconut aminos
- Anchovies → Capers, olives, miso paste

### Shellfish
- Shrimp → Chicken, firm white fish, mushrooms
- Crab → Hearts of palm, jackfruit
- Oyster sauce → Hoisin sauce, mushroom sauce

### Sesame
- Sesame oil → Olive oil, avocado oil
- Sesame seeds → Sunflower seeds, pumpkin seeds
- Tahini → Sunflower seed butter

## Error Responses

### 401 Unauthorized
```json
{
  "detail": "Authentication required"
}
```
Solution: Include valid JWT token in Authorization header

### 404 Not Found
```json
{
  "detail": "Recipe with ID 999 not found"
}
```
Solution: Verify recipe ID exists

### 409 Conflict
```json
{
  "detail": "Recipe is already in favorites"
}
```
Solution: Recipe is already favorited, update notes instead

## Best Practices

1. **Check Status Before Adding**: Use `/status` endpoint to check if already favorited
2. **Handle Pagination**: Always implement pagination for favorites lists
3. **Verify Safety**: Check `/allergen-warnings` before displaying recipe details
4. **Use Substitutions**: Show substitution suggestions to users with allergens
5. **Cache Favorite Status**: Cache favorite status on client side for better UX
6. **Show Severity**: Display severity level clearly in UI (color coding recommended)
7. **Batch Loading**: Load favorite status for multiple recipes in one request
8. **Error Handling**: Implement proper error handling for all edge cases

## Integration Example (JavaScript)

```javascript
// Add to favorites
async function addFavorite(recipeId, notes) {
  const response = await fetch(`/api/v1/favorites/${recipeId}`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ notes })
  });

  if (!response.ok) {
    if (response.status === 409) {
      console.log('Already favorited');
      return;
    }
    throw new Error('Failed to add favorite');
  }

  return await response.json();
}

// Get safe recipes
async function getSafeRecipes(filters = {}) {
  const params = new URLSearchParams(filters);
  const response = await fetch(`/api/v1/recipes/safe?${params}`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });

  return await response.json();
}

// Check allergen warnings
async function checkAllergenWarnings(recipeId) {
  const response = await fetch(
    `/api/v1/recipes/${recipeId}/allergen-warnings`,
    {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    }
  );

  const data = await response.json();

  if (!data.is_safe) {
    console.warn('Recipe contains allergens:', data.warnings);
  }

  return data;
}
```

## Notes

- All endpoints require authentication via JWT token
- Favorites are user-specific and private
- Allergen profiles are automatically used for safe recipe filtering
- Substitutions are suggestions and may require recipe adjustments
- Always test recipes with substitutions for taste and texture
- Severity levels can be updated in user's allergen profile
