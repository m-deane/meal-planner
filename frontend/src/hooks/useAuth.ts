/**
 * React Query hooks for authentication operations.
 */

import {
  useMutation,
  useQuery,
  useQueryClient,
  UseMutationResult,
  UseQueryResult,
} from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import {
  login as loginAPI,
  register as registerAPI,
  logout as logoutAPI,
  getMe,
  updateMe,
  changePassword,
  verifyToken,
} from '../api/auth';
import type {
  LoginRequest,
  RegisterRequest,
  TokenResponse,
  User,
  UserUpdateRequest,
  PasswordChangeRequest,
} from '../types/user';
import type { APIError } from '../types';

/**
 * Query keys for authentication.
 */
export const authKeys = {
  all: ['auth'] as const,
  me: () => [...authKeys.all, 'me'] as const,
  verify: () => [...authKeys.all, 'verify'] as const,
};

/**
 * Hook for login mutation.
 */
export const useLogin = (): UseMutationResult<
  TokenResponse,
  APIError,
  LoginRequest
> => {
  const queryClient = useQueryClient();
  const { setAuth } = useAuthStore();
  const navigate = useNavigate();

  return useMutation({
    mutationFn: loginAPI,
    onSuccess: (data) => {
      setAuth(data.access_token, data.user);
      queryClient.setQueryData(authKeys.me(), data.user);
      navigate('/');
    },
  });
};

/**
 * Hook for register mutation.
 */
export const useRegister = (): UseMutationResult<User, APIError, RegisterRequest> => {
  const navigate = useNavigate();

  return useMutation({
    mutationFn: registerAPI,
    onSuccess: () => {
      navigate('/login', {
        state: { message: 'Registration successful. Please log in.' },
      });
    },
  });
};

/**
 * Hook for logout mutation.
 */
export const useLogout = (): UseMutationResult<void, APIError, void> => {
  const queryClient = useQueryClient();
  const { logout: logoutStore } = useAuthStore();
  const navigate = useNavigate();

  return useMutation({
    mutationFn: logoutAPI,
    onSuccess: () => {
      logoutStore();
      queryClient.clear();
      navigate('/login');
    },
    onError: () => {
      // Clear auth even if API call fails
      logoutStore();
      queryClient.clear();
      navigate('/login');
    },
  });
};

/**
 * Hook to get current authenticated user.
 */
export const useCurrentUser = (): UseQueryResult<User | undefined> => {
  const { isAuthenticated, user, setUser, clearAuth } = useAuthStore();

  const query = useQuery({
    queryKey: authKeys.me(),
    queryFn: getMe,
    enabled: isAuthenticated,
    initialData: user ?? undefined,
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
    retry: false,
  });

  // Handle successful fetch
  if (query.data && query.isSuccess) {
    setUser(query.data);
  }

  // Handle error
  if (query.isError) {
    clearAuth();
  }

  return query;
};

/**
 * Hook to check if user is authenticated.
 */
export const useIsAuthenticated = (): boolean => {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  return isAuthenticated;
};

/**
 * Hook for updating user profile.
 */
export const useUpdateProfile = (): UseMutationResult<
  User,
  APIError,
  UserUpdateRequest
> => {
  const queryClient = useQueryClient();
  const { setUser } = useAuthStore();

  return useMutation({
    mutationFn: updateMe,
    onSuccess: (data) => {
      setUser(data);
      queryClient.setQueryData(authKeys.me(), data);
    },
  });
};

/**
 * Hook for changing password.
 */
export const useChangePassword = (): UseMutationResult<
  void,
  APIError,
  PasswordChangeRequest
> => {
  return useMutation({
    mutationFn: changePassword,
  });
};

/**
 * Hook to verify token validity.
 */
export const useVerifyToken = (): UseQueryResult<boolean> => {
  const { isAuthenticated, clearAuth } = useAuthStore();

  const query = useQuery({
    queryKey: authKeys.verify(),
    queryFn: verifyToken,
    enabled: isAuthenticated,
    staleTime: 2 * 60 * 1000, // 2 minutes
    retry: false,
  });

  // Handle successful verification
  if (query.data !== undefined && query.isSuccess && !query.data) {
    clearAuth();
  }

  return query;
};
