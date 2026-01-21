/**
 * Registration form component with validation and error handling.
 */

import { useState, FormEvent } from 'react';
import { Link } from 'react-router-dom';
import { useRegister } from '../../hooks/useAuth';
import { formatAPIError } from '../../api/client';
import { Loader2 } from 'lucide-react';

export const RegisterForm = (): JSX.Element => {
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});

  const registerMutation = useRegister();

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};

    // Email validation
    if (!email.trim()) {
      errors['email'] = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      errors['email'] = 'Please enter a valid email address';
    }

    // Username validation
    if (!username.trim()) {
      errors['username'] = 'Username is required';
    } else if (username.length < 3) {
      errors['username'] = 'Username must be at least 3 characters';
    } else if (!/^[a-zA-Z0-9_-]+$/.test(username)) {
      errors['username'] = 'Username can only contain letters, numbers, hyphens, and underscores';
    }

    // Password validation
    if (!password) {
      errors['password'] = 'Password is required';
    } else if (password.length < 8) {
      errors['password'] = 'Password must be at least 8 characters';
    } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(password)) {
      errors['password'] = 'Password must contain uppercase, lowercase, and number';
    }

    // Confirm password validation
    if (!confirmPassword) {
      errors['confirmPassword'] = 'Please confirm your password';
    } else if (password !== confirmPassword) {
      errors['confirmPassword'] = 'Passwords do not match';
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = (e: FormEvent<HTMLFormElement>): void => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    registerMutation.mutate({
      email,
      username,
      password,
      confirm_password: confirmPassword,
    });
  };

  return (
    <div className="w-full max-w-md">
      <div className="bg-white shadow-lg rounded-lg px-8 py-10">
        <h2 className="text-3xl font-bold text-gray-900 text-center mb-8">
          Create Account
        </h2>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Global error */}
          {registerMutation.isError && (
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
                    {formatAPIError(registerMutation.error)}
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Email */}
          <div>
            <label
              htmlFor="email"
              className="block text-sm font-medium text-gray-700"
            >
              Email
            </label>
            <div className="mt-1">
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className={`
                  appearance-none block w-full px-3 py-2 border rounded-md shadow-sm
                  placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-offset-2
                  ${
                    validationErrors['email']
                      ? 'border-red-300 focus:ring-red-500 focus:border-red-500'
                      : 'border-gray-300 focus:ring-blue-500 focus:border-blue-500'
                  }
                `}
                placeholder="you@example.com"
              />
              {validationErrors['email'] && (
                <p className="mt-2 text-sm text-red-600">
                  {validationErrors['email']}
                </p>
              )}
            </div>
          </div>

          {/* Username */}
          <div>
            <label
              htmlFor="username"
              className="block text-sm font-medium text-gray-700"
            >
              Username
            </label>
            <div className="mt-1">
              <input
                id="username"
                name="username"
                type="text"
                autoComplete="username"
                required
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className={`
                  appearance-none block w-full px-3 py-2 border rounded-md shadow-sm
                  placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-offset-2
                  ${
                    validationErrors['username']
                      ? 'border-red-300 focus:ring-red-500 focus:border-red-500'
                      : 'border-gray-300 focus:ring-blue-500 focus:border-blue-500'
                  }
                `}
                placeholder="johndoe"
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
                autoComplete="new-password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className={`
                  appearance-none block w-full px-3 py-2 border rounded-md shadow-sm
                  placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-offset-2
                  ${
                    validationErrors['password']
                      ? 'border-red-300 focus:ring-red-500 focus:border-red-500'
                      : 'border-gray-300 focus:ring-blue-500 focus:border-blue-500'
                  }
                `}
                placeholder="••••••••"
              />
              {validationErrors['password'] && (
                <p className="mt-2 text-sm text-red-600">
                  {validationErrors['password']}
                </p>
              )}
              <p className="mt-2 text-sm text-gray-500">
                Must be at least 8 characters with uppercase, lowercase, and number
              </p>
            </div>
          </div>

          {/* Confirm Password */}
          <div>
            <label
              htmlFor="confirm-password"
              className="block text-sm font-medium text-gray-700"
            >
              Confirm Password
            </label>
            <div className="mt-1">
              <input
                id="confirm-password"
                name="confirm-password"
                type="password"
                autoComplete="new-password"
                required
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className={`
                  appearance-none block w-full px-3 py-2 border rounded-md shadow-sm
                  placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-offset-2
                  ${
                    validationErrors['confirmPassword']
                      ? 'border-red-300 focus:ring-red-500 focus:border-red-500'
                      : 'border-gray-300 focus:ring-blue-500 focus:border-blue-500'
                  }
                `}
                placeholder="••••••••"
              />
              {validationErrors['confirmPassword'] && (
                <p className="mt-2 text-sm text-red-600">
                  {validationErrors['confirmPassword']}
                </p>
              )}
            </div>
          </div>

          {/* Submit button */}
          <div>
            <button
              type="submit"
              disabled={registerMutation.isPending}
              className="
                w-full flex justify-center py-2 px-4 border border-transparent
                rounded-md shadow-sm text-sm font-medium text-white bg-blue-600
                hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2
                focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed
                transition-colors duration-200
              "
            >
              {registerMutation.isPending ? (
                <>
                  <Loader2 className="animate-spin -ml-1 mr-3 h-5 w-5" />
                  Creating account...
                </>
              ) : (
                'Create account'
              )}
            </button>
          </div>
        </form>

        {/* Login link */}
        <div className="mt-6">
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-300" />
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-white text-gray-500">
                Already have an account?
              </span>
            </div>
          </div>

          <div className="mt-6">
            <Link
              to="/login"
              className="
                w-full flex justify-center py-2 px-4 border border-gray-300
                rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white
                hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2
                focus:ring-blue-500 transition-colors duration-200
              "
            >
              Sign in instead
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};
