/**
 * Authentication API functions.
 */

import { apiClient } from './client';
import type {
  LoginRequest,
  RegisterRequest,
  TokenResponse,
  User,
  UserUpdateRequest,
  PasswordChangeRequest,
} from '../types/user';

/**
 * Login with username and password.
 */
export const login = async (credentials: LoginRequest): Promise<TokenResponse> => {
  const formData = new URLSearchParams();
  formData.append('username', credentials.username);
  formData.append('password', credentials.password);

  const { data } = await apiClient.post<TokenResponse>('/auth/login', formData, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  });

  // Store token in localStorage
  if (data.access_token) {
    localStorage.setItem('auth_token', data.access_token);
  }

  return data;
};

/**
 * Register a new user.
 */
export const register = async (userData: RegisterRequest): Promise<User> => {
  const { data } = await apiClient.post<User>('/auth/register', userData);
  return data;
};

/**
 * Logout and clear authentication token.
 */
export const logout = async (): Promise<void> => {
  try {
    await apiClient.post('/auth/logout');
  } finally {
    // Always clear token even if API call fails
    localStorage.removeItem('auth_token');
  }
};

/**
 * Get current authenticated user.
 */
export const getMe = async (): Promise<User> => {
  const { data } = await apiClient.get<User>('/auth/me');
  return data;
};

/**
 * Update current user profile.
 */
export const updateMe = async (userData: UserUpdateRequest): Promise<User> => {
  const { data } = await apiClient.patch<User>('/auth/me', userData);
  return data;
};

/**
 * Change user password.
 */
export const changePassword = async (
  passwordData: PasswordChangeRequest
): Promise<void> => {
  await apiClient.post('/auth/change-password', passwordData);
};

/**
 * Refresh authentication token.
 */
export const refreshToken = async (): Promise<TokenResponse> => {
  const { data } = await apiClient.post<TokenResponse>('/auth/refresh');

  // Update stored token
  if (data.access_token) {
    localStorage.setItem('auth_token', data.access_token);
  }

  return data;
};

/**
 * Verify current token is valid.
 */
export const verifyToken = async (): Promise<boolean> => {
  try {
    await apiClient.get('/auth/verify');
    return true;
  } catch {
    return false;
  }
};

/**
 * Request password reset email.
 */
export const requestPasswordReset = async (email: string): Promise<void> => {
  await apiClient.post('/auth/password-reset/request', { email });
};

/**
 * Reset password with token.
 */
export const resetPassword = async (
  token: string,
  newPassword: string
): Promise<void> => {
  await apiClient.post('/auth/password-reset/confirm', {
    token,
    new_password: newPassword,
  });
};
