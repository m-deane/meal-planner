/**
 * User preferences and allergens API functions.
 *
 * Note: Favorites functions are in api/favorites.ts (canonical source).
 */

import { apiClient } from './client';
import type {
  UserPreference,
  UserAllergen,
  UserAllergensResponse,
  PreferenceUpdateRequest,
  AllergenUpdateRequest,
} from '../types/user';

/**
 * Get user preferences.
 */
export const getPreferences = async (): Promise<UserPreference> => {
  const { data } = await apiClient.get<UserPreference>('/users/me/preferences');
  return data;
};

/**
 * Update user preferences.
 */
export const updatePreferences = async (
  preferences: PreferenceUpdateRequest
): Promise<UserPreference> => {
  const { data } = await apiClient.put<UserPreference>(
    '/users/me/preferences',
    preferences
  );
  return data;
};

/**
 * Get user allergens.
 * Backend returns: { allergens: UserAllergen[], count: number }
 */
export const getAllergens = async (): Promise<UserAllergen[]> => {
  const { data } = await apiClient.get<UserAllergensResponse>('/users/me/allergens');
  return data.allergens;
};

/**
 * Update user allergens (replaces all).
 * Backend returns: { allergens: UserAllergen[], count: number }
 */
export const updateAllergens = async (
  allergenData: AllergenUpdateRequest
): Promise<UserAllergen[]> => {
  const { data } = await apiClient.put<UserAllergensResponse>(
    '/users/me/allergens',
    allergenData
  );
  return data.allergens;
};
