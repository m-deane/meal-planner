/**
 * User authentication and profile types matching backend schemas.
 */

// ============================================================================
// ENUMS
// ============================================================================

export enum AllergenSeverity {
  MILD = 'mild',
  MODERATE = 'moderate',
  SEVERE = 'severe',
  LIFE_THREATENING = 'life_threatening',
}

export enum UserRole {
  USER = 'user',
  ADMIN = 'admin',
}

// ============================================================================
// USER TYPES
// ============================================================================

export interface User {
  id: number;
  email: string;
  username: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

/**
 * User preferences as returned by the backend.
 * Matches backend UserPreferenceResponse schema.
 * Note: carb and fat fields use *_limit_g (not *_target_g).
 */
export interface UserPreference {
  id: number;
  user_id: number;
  calorie_target: number | null;
  protein_target_g: number | null;
  carb_limit_g: number | null;
  fat_limit_g: number | null;
  default_servings: number;
  preferred_cuisines: string[];
  created_at: string;
  updated_at: string;
}

/**
 * Allergen detail object nested inside a UserAllergen.
 * Matches backend AllergenResponse schema.
 */
export interface AllergenDetail {
  id: number;
  name: string;
  description: string | null;
}

/**
 * A single user allergen record as returned by the backend.
 * Matches backend UserAllergenResponse schema:
 * { user_id, allergen_id, severity, allergen: AllergenResponse, created_at }
 */
export interface UserAllergen {
  user_id: number;
  allergen_id: number;
  severity: string;
  allergen: AllergenDetail;
  created_at: string;
}

/**
 * Wrapped response for user allergens list.
 * Matches backend UserAllergenListResponse schema:
 * { allergens: UserAllergenResponse[], count: number }
 */
export interface UserAllergensResponse {
  allergens: UserAllergen[];
  count: number;
}

export interface UserFavorite {
  id: number;
  user_id: number;
  recipe_id: number;
  notes: string | null;
  created_at: string;
}

// ============================================================================
// REQUEST/RESPONSE TYPES
// ============================================================================

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  username: string;
  password: string;
  confirm_password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface PasswordChangeRequest {
  current_password: string;
  new_password: string;
  confirm_password: string;
}

export interface UserUpdateRequest {
  email?: string;
  username?: string;
}

/**
 * Request to update user preferences.
 * Field names match backend UserPreferenceUpdate schema.
 */
export interface PreferenceUpdateRequest {
  calorie_target?: number | null;
  protein_target_g?: number | null;
  carb_limit_g?: number | null;
  fat_limit_g?: number | null;
  default_servings?: number;
  preferred_cuisines?: string[];
}

export interface AllergenUpdateRequest {
  allergens: Array<{
    allergen_id: number;
    severity: AllergenSeverity;
    notes?: string | null;
  }>;
}

export interface FavoriteAddRequest {
  recipe_id: number;
  notes?: string | null;
}
