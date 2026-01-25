/**
 * Login form component with validation and error handling.
 */

import { useState } from 'react';
import type { FormEvent } from 'react';
import { Link } from 'react-router-dom';
import { useLogin } from '../../hooks/useAuth';
import { formatAPIError } from '../../api/client';
import { Loader2 } from 'lucide-react';

export const LoginForm = (): JSX.Element => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});

  const loginMutation = useLogin();

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};

    if (!username.trim()) {
      errors['username'] = 'Username or email is required';
    }

    if (!password) {
      errors['password'] = 'Password is required';
    } else if (password.length < 6) {
      errors['password'] = 'Password must be at least 6 characters';
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = (e: FormEvent<HTMLFormElement>): void => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    loginMutation.mutate({ username, password });
  };

  return (
    <div className="w-full max-w-md">
      <div className="bg-white shadow-lg rounded-lg px-8 py-10">
        <h2 className="text-3xl font-bold text-gray-900 text-center mb-8">
          Sign In
        </h2>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Global error */}
          {loginMutation.isError && (
            <div className="rounded-md bg-red-50 p-4">
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg
                    className="h-5 w-5 text-red-400"
                    viewBox="0 0 20 20"
                    fill="currentColor"
                  >
                    <path
                      fillRule="evenodd"
                      d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                      clipRule="evenodd"
                    />
                  </svg>
                </div>
                <div className="ml-3">
                  <p className="text-sm font-medium text-red-800">
                    {formatAPIError(loginMutation.error)}
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Username/Email */}
          <div>
            <label
              htmlFor="username"
              className="block text-sm font-medium text-gray-700"
            >
              Username or Email
            </label>
            <div className="mt-1">
              <input
                id="username"
                name="username"
                type="text"
                autoComplete="username"
                required
                value={username}
                onChange={(e) => { setUsername(e.target.value); }}
                className={`
                  appearance-none block w-full px-3 py-2 border rounded-md shadow-sm
                  placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-offset-2
                  ${
                    validationErrors['username']
                      ? 'border-red-300 focus:ring-red-500 focus:border-red-500'
                      : 'border-gray-300 focus:ring-blue-500 focus:border-blue-500'
                  }
                `}
                placeholder="Enter your username or email"
              />
              {validationErrors['username'] && (
                <p className="mt-2 text-sm text-red-600">
                  {validationErrors['username']}
                </p>
              )}
            </div>
          </div>

          {/* Password */}
          <div>
            <label
              htmlFor="password"
              className="block text-sm font-medium text-gray-700"
            >
              Password
            </label>
            <div className="mt-1">
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="current-password"
                required
                value={password}
                onChange={(e) => { setPassword(e.target.value); }}
                className={`
                  appearance-none block w-full px-3 py-2 border rounded-md shadow-sm
                  placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-offset-2
                  ${
                    validationErrors['password']
                      ? 'border-red-300 focus:ring-red-500 focus:border-red-500'
                      : 'border-gray-300 focus:ring-blue-500 focus:border-blue-500'
                  }
                `}
                placeholder="Enter your password"
              />
              {validationErrors['password'] && (
                <p className="mt-2 text-sm text-red-600">
                  {validationErrors['password']}
                </p>
              )}
            </div>
          </div>

          {/* Remember me and Forgot password */}
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <input
                id="remember-me"
                name="remember-me"
                type="checkbox"
                checked={rememberMe}
                onChange={(e) => { setRememberMe(e.target.checked); }}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label
                htmlFor="remember-me"
                className="ml-2 block text-sm text-gray-900"
              >
                Remember me
              </label>
            </div>

            <div className="text-sm">
              <Link
                to="/forgot-password"
                className="font-medium text-blue-600 hover:text-blue-500"
              >
                Forgot password?
              </Link>
            </div>
          </div>

          {/* Submit button */}
          <div>
            <button
              type="submit"
              disabled={loginMutation.isPending}
              className="
                w-full flex justify-center py-2 px-4 border border-transparent
                rounded-md shadow-sm text-sm font-medium text-white bg-blue-600
                hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2
                focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed
                transition-colors duration-200
              "
            >
              {loginMutation.isPending ? (
                <>
                  <Loader2 className="animate-spin -ml-1 mr-3 h-5 w-5" />
                  Signing in...
                </>
              ) : (
                'Sign in'
              )}
            </button>
          </div>
        </form>

        {/* Register link */}
        <div className="mt-6">
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-300" />
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-white text-gray-500">
                Don't have an account?
              </span>
            </div>
          </div>

          <div className="mt-6">
            <Link
              to="/register"
              className="
                w-full flex justify-center py-2 px-4 border border-gray-300
                rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white
                hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2
                focus:ring-blue-500 transition-colors duration-200
              "
            >
              Create new account
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};
