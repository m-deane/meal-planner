/**
 * Axios HTTP client configuration with interceptors for error handling and authentication.
 */

import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig, AxiosResponse } from 'axios';
import type { APIError } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

/**
 * Create configured axios instance.
 */
const createAPIClient = (): AxiosInstance => {
  const client = axios.create({
    baseURL: API_BASE_URL,
    timeout: 30000,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  // Request interceptor for auth token
  client.interceptors.request.use(
    (config: InternalAxiosRequestConfig): InternalAxiosRequestConfig => {
      const token = localStorage.getItem('auth_token');

      if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`;
      }

      return config;
    },
    (error: AxiosError): Promise<AxiosError> => {
      return Promise.reject(error);
    }
  );

  // Response interceptor for error handling
  client.interceptors.response.use(
    (response: AxiosResponse): AxiosResponse => response,
    (error: AxiosError): Promise<APIError> => {
      const apiError: APIError = {
        message: 'An unexpected error occurred',
        status: error.response?.status,
      };

      if (error.response) {
        // Server responded with error status
        const data = error.response.data as Record<string, unknown>;

        if (typeof data === 'object' && data !== null) {
          // FastAPI validation error format
          if ('detail' in data) {
            if (Array.isArray(data.detail)) {
              apiError.message = 'Validation error';
              apiError.errors = data.detail.map((err: Record<string, unknown>) => ({
                field: Array.isArray(err.loc) ? err.loc.join('.') : undefined,
                message: String(err.msg || 'Invalid value'),
              }));
            } else if (typeof data.detail === 'string') {
              apiError.message = data.detail;
            }
          } else if ('message' in data && typeof data.message === 'string') {
            apiError.message = data.message;
          }
        }

        // Handle specific HTTP status codes
        switch (error.response.status) {
          case 401:
            apiError.message = 'Authentication required';
            localStorage.removeItem('auth_token');
            window.location.href = '/login';
            break;
          case 403:
            apiError.message = 'Access forbidden';
            break;
          case 404:
            apiError.message = 'Resource not found';
            break;
          case 422:
            if (!apiError.errors) {
              apiError.message = 'Invalid request data';
            }
            break;
          case 429:
            apiError.message = 'Too many requests. Please try again later.';
            break;
          case 500:
            apiError.message = 'Internal server error';
            break;
          case 503:
            apiError.message = 'Service temporarily unavailable';
            break;
        }
      } else if (error.request) {
        // Request made but no response received
        apiError.message = 'Network error. Please check your connection.';
      } else {
        // Error setting up the request
        apiError.message = error.message || 'Failed to make request';
      }

      return Promise.reject(apiError);
    }
  );

  return client;
};

export const apiClient = createAPIClient();

/**
 * Type guard for API errors.
 */
export const isAPIError = (error: unknown): error is APIError => {
  return (
    typeof error === 'object' &&
    error !== null &&
    'message' in error &&
    typeof (error as APIError).message === 'string'
  );
};

/**
 * Format API error for display.
 */
export const formatAPIError = (error: unknown): string => {
  if (isAPIError(error)) {
    if (error.errors && error.errors.length > 0) {
      return error.errors
        .map(err => (err.field ? `${err.field}: ${err.message}` : err.message))
        .join(', ');
    }
    return error.message;
  }

  if (error instanceof Error) {
    return error.message;
  }

  return 'An unexpected error occurred';
};
