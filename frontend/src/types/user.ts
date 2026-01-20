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

export interface UserPreference {
  id: number;
  user_id: number;
  calorie_target: number | null;
  protein_target_g: number | null;
  carb_target_g: number | null;
  fat_target_g: number | null;
  default_servings: number;
  preferred_cuisines: string[];
  created_at: string;
  updated_at: string;
}

export interface UserAllergen {
  id: number;
  user_id: number;
  allergen_id: number;
  allergen_name: string;
  severity: AllergenSeverity;
  notes: string | null;
  created_at: string;
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

export interface PreferenceUpdateRequest {
  calorie_target?: number | null;
  protein_target_g?: number | null;
  carb_target_g?: number | null;
  fat_target_g?: number | null;
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
