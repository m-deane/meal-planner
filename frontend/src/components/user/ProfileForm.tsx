/**
 * User profile editing form component.
 */

import { useState, FormEvent, useEffect } from 'react';
import { useCurrentUser, useUpdateProfile, useChangePassword } from '../../hooks/useAuth';
import { formatAPIError } from '../../api/client';
import { Loader2, CheckCircle, User as UserIcon, Lock } from 'lucide-react';

export const ProfileForm = (): JSX.Element => {
  const { data: user, isLoading: userLoading } = useCurrentUser();
  const updateProfileMutation = useUpdateProfile();
  const changePasswordMutation = useChangePassword();

  // Profile form state
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [profileValidationErrors, setProfileValidationErrors] = useState<
    Record<string, string>
  >({});
  const [profileSuccess, setProfileSuccess] = useState(false);

  // Password form state
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmNewPassword, setConfirmNewPassword] = useState('');
  const [passwordValidationErrors, setPasswordValidationErrors] = useState<
    Record<string, string>
  >({});
  const [passwordSuccess, setPasswordSuccess] = useState(false);

  // Initialize form with user data
  useEffect(() => {
    if (user) {
      setEmail(user.email);
      setUsername(user.username);
    }
  }, [user]);

  const validateProfileForm = (): boolean => {
    const errors: Record<string, string> = {};

    if (!email.trim()) {
      errors['email'] = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      errors['email'] = 'Please enter a valid email address';
    }

    if (!username.trim()) {
      errors['username'] = 'Username is required';
    } else if (username.length < 3) {
      errors['username'] = 'Username must be at least 3 characters';
    }

    setProfileValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const validatePasswordForm = (): boolean => {
    const errors: Record<string, string> = {};

    if (!currentPassword) {
      errors['currentPassword'] = 'Current password is required';
    }

    if (!newPassword) {
      errors['newPassword'] = 'New password is required';
    } else if (newPassword.length < 8) {
      errors['newPassword'] = 'Password must be at least 8 characters';
    } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(newPassword)) {
      errors['newPassword'] = 'Password must contain uppercase, lowercase, and number';
    }

    if (!confirmNewPassword) {
      errors['confirmNewPassword'] = 'Please confirm your new password';
    } else if (newPassword !== confirmNewPassword) {
      errors['confirmNewPassword'] = 'Passwords do not match';
    }

    setPasswordValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleProfileSubmit = (e: FormEvent<HTMLFormElement>): void => {
    e.preventDefault();
    setProfileSuccess(false);

    if (!validateProfileForm()) {
      return;
    }

    updateProfileMutation.mutate(
      { email, username },
      {
        onSuccess: () => {
          setProfileSuccess(true);
          setTimeout(() => setProfileSuccess(false), 3000);
        },
      }
    );
  };

  const handlePasswordSubmit = (e: FormEvent<HTMLFormElement>): void => {
    e.preventDefault();
    setPasswordSuccess(false);

    if (!validatePasswordForm()) {
      return;
    }

    changePasswordMutation.mutate(
      {
        current_password: currentPassword,
        new_password: newPassword,
        confirm_password: confirmNewPassword,
      },
      {
        onSuccess: () => {
          setPasswordSuccess(true);
          setCurrentPassword('');
          setNewPassword('');
          setConfirmNewPassword('');
          setTimeout(() => setPasswordSuccess(false), 3000);
        },
      }
    );
  };

  if (userLoading) {
    return (
      <div className="flex justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Profile Information Section */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex items-center">
            <UserIcon className="h-5 w-5 text-gray-400 mr-2" />
            <h3 className="text-lg font-medium text-gray-900">
              Profile Information
            </h3>
          </div>
        </div>

        <form onSubmit={handleProfileSubmit} className="px-6 py-6">
          {/* Success message */}
          {profileSuccess && (
            <div className="mb-4 rounded-md bg-green-50 p-4">
              <div className="flex">
                <CheckCircle className="h-5 w-5 text-green-400" />
                <div className="ml-3">
                  <p className="text-sm font-medium text-green-800">
                    Profile updated successfully
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Error message */}
          {updateProfileMutation.isError && (
            <div className="mb-4 rounded-md bg-red-50 p-4">
              <div className="flex">
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
                <div className="ml-3">
                  <p className="text-sm font-medium text-red-800">
                    {formatAPIError(updateProfileMutation.error)}
                  </p>
                </div>
              </div>
            </div>
          )}

          <div className="space-y-6">
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
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className={`
                    appearance-none block w-full px-3 py-2 border rounded-md shadow-sm
                    placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-offset-2
                    ${
                      profileValidationErrors['email']
                        ? 'border-red-300 focus:ring-red-500 focus:border-red-500'
                        : 'border-gray-300 focus:ring-blue-500 focus:border-blue-500'
                    }
                  `}
                />
                {profileValidationErrors['email'] && (
                  <p className="mt-2 text-sm text-red-600">
                    {profileValidationErrors['email']}
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
                  required
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className={`
                    appearance-none block w-full px-3 py-2 border rounded-md shadow-sm
                    placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-offset-2
                    ${
                      profileValidationErrors['username']
                        ? 'border-red-300 focus:ring-red-500 focus:border-red-500'
                        : 'border-gray-300 focus:ring-blue-500 focus:border-blue-500'
                    }
                  `}
                />
                {profileValidationErrors['username'] && (
                  <p className="mt-2 text-sm text-red-600">
                    {profileValidationErrors['username']}
                  </p>
                )}
              </div>
            </div>
          </div>

          <div className="mt-6">
            <button
              type="submit"
              disabled={updateProfileMutation.isPending}
              className="
                inline-flex justify-center py-2 px-4 border border-transparent
                shadow-sm text-sm font-medium rounded-md text-white bg-blue-600
                hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2
                focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed
              "
            >
              {updateProfileMutation.isPending ? (
                <>
                  <Loader2 className="animate-spin -ml-1 mr-2 h-4 w-4" />
                  Saving...
                </>
              ) : (
                'Save Changes'
              )}
            </button>
          </div>
        </form>
      </div>

      {/* Change Password Section */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex items-center">
            <Lock className="h-5 w-5 text-gray-400 mr-2" />
            <h3 className="text-lg font-medium text-gray-900">Change Password</h3>
          </div>
        </div>

        <form onSubmit={handlePasswordSubmit} className="px-6 py-6">
          {/* Success message */}
          {passwordSuccess && (
            <div className="mb-4 rounded-md bg-green-50 p-4">
              <div className="flex">
                <CheckCircle className="h-5 w-5 text-green-400" />
                <div className="ml-3">
                  <p className="text-sm font-medium text-green-800">
                    Password changed successfully
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Error message */}
          {changePasswordMutation.isError && (
            <div className="mb-4 rounded-md bg-red-50 p-4">
              <div className="flex">
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
                <div className="ml-3">
                  <p className="text-sm font-medium text-red-800">
                    {formatAPIError(changePasswordMutation.error)}
                  </p>
                </div>
              </div>
            </div>
          )}

          <div className="space-y-6">
            {/* Current Password */}
            <div>
              <label
                htmlFor="current-password"
                className="block text-sm font-medium text-gray-700"
              >
                Current Password
              </label>
              <div className="mt-1">
                <input
                  id="current-password"
                  name="current-password"
                  type="password"
                  autoComplete="current-password"
                  required
                  value={currentPassword}
                  onChange={(e) => setCurrentPassword(e.target.value)}
                  className={`
                    appearance-none block w-full px-3 py-2 border rounded-md shadow-sm
                    placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-offset-2
                    ${
                      passwordValidationErrors['currentPassword']
                        ? 'border-red-300 focus:ring-red-500 focus:border-red-500'
                        : 'border-gray-300 focus:ring-blue-500 focus:border-blue-500'
                    }
                  `}
                />
                {passwordValidationErrors['currentPassword'] && (
                  <p className="mt-2 text-sm text-red-600">
                    {passwordValidationErrors['currentPassword']}
                  </p>
                )}
              </div>
            </div>

            {/* New Password */}
            <div>
              <label
                htmlFor="new-password"
                className="block text-sm font-medium text-gray-700"
              >
                New Password
              </label>
              <div className="mt-1">
                <input
                  id="new-password"
                  name="new-password"
                  type="password"
                  autoComplete="new-password"
                  required
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  className={`
                    appearance-none block w-full px-3 py-2 border rounded-md shadow-sm
                    placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-offset-2
                    ${
                      passwordValidationErrors['newPassword']
                        ? 'border-red-300 focus:ring-red-500 focus:border-red-500'
                        : 'border-gray-300 focus:ring-blue-500 focus:border-blue-500'
                    }
                  `}
                />
                {passwordValidationErrors['newPassword'] && (
                  <p className="mt-2 text-sm text-red-600">
                    {passwordValidationErrors['newPassword']}
                  </p>
                )}
              </div>
            </div>

            {/* Confirm New Password */}
            <div>
              <label
                htmlFor="confirm-new-password"
                className="block text-sm font-medium text-gray-700"
              >
                Confirm New Password
              </label>
              <div className="mt-1">
                <input
                  id="confirm-new-password"
                  name="confirm-new-password"
                  type="password"
                  autoComplete="new-password"
                  required
                  value={confirmNewPassword}
                  onChange={(e) => setConfirmNewPassword(e.target.value)}
                  className={`
                    appearance-none block w-full px-3 py-2 border rounded-md shadow-sm
                    placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-offset-2
                    ${
                      passwordValidationErrors['confirmNewPassword']
                        ? 'border-red-300 focus:ring-red-500 focus:border-red-500'
                        : 'border-gray-300 focus:ring-blue-500 focus:border-blue-500'
                    }
                  `}
                />
                {passwordValidationErrors['confirmNewPassword'] && (
                  <p className="mt-2 text-sm text-red-600">
                    {passwordValidationErrors['confirmNewPassword']}
                  </p>
                )}
              </div>
            </div>
          </div>

          <div className="mt-6">
            <button
              type="submit"
              disabled={changePasswordMutation.isPending}
              className="
                inline-flex justify-center py-2 px-4 border border-transparent
                shadow-sm text-sm font-medium rounded-md text-white bg-blue-600
                hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2
                focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed
              "
            >
              {changePasswordMutation.isPending ? (
                <>
                  <Loader2 className="animate-spin -ml-1 mr-2 h-4 w-4" />
                  Changing...
                </>
              ) : (
                'Change Password'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
