/**
 * Registration page component.
 */

import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { RegisterForm } from '../components/auth';
import { useIsAuthenticated } from '../hooks/useAuth';
import { ChefHat } from 'lucide-react';

export const RegisterPage = (): JSX.Element => {
  const navigate = useNavigate();
  const isAuthenticated = useIsAuthenticated();

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/', { replace: true });
    }
  }, [isAuthenticated, navigate]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        {/* Logo and branding */}
        <div className="text-center">
          <div className="flex justify-center">
            <div className="bg-blue-600 rounded-full p-3">
              <ChefHat className="h-12 w-12 text-white" />
            </div>
          </div>
          <h1 className="mt-6 text-4xl font-extrabold text-gray-900">
            Join Meal Planner
          </h1>
          <p className="mt-2 text-sm text-gray-600">
            Start planning delicious and healthy meals today
          </p>
        </div>

        {/* Registration form */}
        <RegisterForm />

        {/* Terms and privacy */}
        <div className="text-center">
          <p className="text-xs text-gray-500">
            By creating an account, you agree to our{' '}
            <a href="/terms" className="text-blue-600 hover:text-blue-500">
              Terms of Service
            </a>{' '}
            and{' '}
            <a href="/privacy" className="text-blue-600 hover:text-blue-500">
              Privacy Policy
            </a>
          </p>
        </div>
      </div>
    </div>
  );
};
