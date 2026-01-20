/**
 * Zustand store for authentication state with localStorage persistence.
 */

import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import type { User } from '../types/user';

// ============================================================================
// TYPES
// ============================================================================

interface AuthState {
  token: string | null;
  user: User | null;
  isAuthenticated: boolean;
}

interface AuthActions {
  setToken: (token: string | null) => void;
  setUser: (user: User | null) => void;
  setAuth: (token: string, user: User) => void;
  logout: () => void;
  clearAuth: () => void;
}

type AuthStore = AuthState & AuthActions;

// ============================================================================
// INITIAL STATE
// ============================================================================

const initialState: AuthState = {
  token: null,
  user: null,
  isAuthenticated: false,
};

// ============================================================================
// STORE
// ============================================================================

export const useAuthStore = create<AuthStore>()(
  persist(
    (set) => ({
      ...initialState,

      setToken: (token) => {
        if (token) {
          localStorage.setItem('auth_token', token);
        } else {
          localStorage.removeItem('auth_token');
        }
        set((state) => ({
          token,
          isAuthenticated: !!token && !!state.user,
        }));
      },

      setUser: (user) => {
        set((state) => ({
          user,
          isAuthenticated: !!user && !!state.token,
        }));
      },

      setAuth: (token, user) => {
        localStorage.setItem('auth_token', token);
        set({
          token,
          user,
          isAuthenticated: true,
        });
      },

      logout: () => {
        localStorage.removeItem('auth_token');
        set(initialState);
      },

      clearAuth: () => {
        localStorage.removeItem('auth_token');
        set(initialState);
      },
    }),
    {
      name: 'auth-storage',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        token: state.token,
        user: state.user,
      }),
    }
  )
);

// ============================================================================
// SELECTORS
// ============================================================================

export const selectIsAuthenticated = (state: AuthStore): boolean => state.isAuthenticated;
export const selectUser = (state: AuthStore): User | null => state.user;
export const selectToken = (state: AuthStore): string | null => state.token;
export const selectUserId = (state: AuthStore): number | null => state.user?.id ?? null;
