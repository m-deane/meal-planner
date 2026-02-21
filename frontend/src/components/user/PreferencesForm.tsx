/**
 * User preferences form component for nutrition targets and dietary preferences.
 */

import { useState, FormEvent, useEffect } from 'react';
import { usePreferences, useUpdatePreferences } from '../../hooks/useUser';
import { useCategories } from '../../hooks/useCategories';
import { formatAPIError } from '../../api/client';
import { Loader2, CheckCircle, Target, Users } from 'lucide-react';
import { CategoryType } from '../../types';

export const PreferencesForm = (): JSX.Element => {
  const { data: preferences, isLoading: preferencesLoading } = usePreferences();
  const { data: categories } = useCategories();
  const updatePreferencesMutation = useUpdatePreferences();

  const [calorieTarget, setCalorieTarget] = useState<number | null>(null);
  const [proteinTarget, setProteinTarget] = useState<number | null>(null);
  const [carbTarget, setCarbTarget] = useState<number | null>(null);
  const [fatTarget, setFatTarget] = useState<number | null>(null);
  const [defaultServings, setDefaultServings] = useState(2);
  const [preferredCuisines, setPreferredCuisines] = useState<string[]>([]);
  const [success, setSuccess] = useState(false);

  // Initialize form with preferences data
  useEffect(() => {
    if (preferences) {
      setCalorieTarget(preferences.calorie_target);
      setProteinTarget(preferences.protein_target_g);
      setCarbTarget(preferences.carb_limit_g);
      setFatTarget(preferences.fat_limit_g);
      setDefaultServings(preferences.default_servings);
      setPreferredCuisines(preferences.preferred_cuisines);
    }
  }, [preferences]);

  const handleSubmit = (e: FormEvent<HTMLFormElement>): void => {
    e.preventDefault();
    setSuccess(false);

    updatePreferencesMutation.mutate(
      {
        calorie_target: calorieTarget,
        protein_target_g: proteinTarget,
        carb_limit_g: carbTarget,
        fat_limit_g: fatTarget,
        default_servings: defaultServings,
        preferred_cuisines: preferredCuisines,
      },
      {
        onSuccess: () => {
          setSuccess(true);
          setTimeout(() => setSuccess(false), 3000);
        },
      }
    );
  };

  const toggleCuisine = (cuisineSlug: string): void => {
    setPreferredCuisines((prev) =>
      prev.includes(cuisineSlug)
        ? prev.filter((c) => c !== cuisineSlug)
        : [...prev, cuisineSlug]
    );
  };

  const cuisineCategories =
    categories?.filter((cat) => cat.category_type === CategoryType.CUISINE) ?? [];

  if (preferencesLoading) {
    return (
      <div className="flex justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    );
  }

  return (
    <div className="bg-white shadow rounded-lg">
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center">
          <Target className="h-5 w-5 text-gray-400 mr-2" />
          <h3 className="text-lg font-medium text-gray-900">
            Nutrition & Preferences
          </h3>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="px-6 py-6">
        {/* Success message */}
        {success && (
          <div className="mb-6 rounded-md bg-green-50 p-4">
            <div className="flex">
              <CheckCircle className="h-5 w-5 text-green-400" />
              <div className="ml-3">
                <p className="text-sm font-medium text-green-800">
                  Preferences updated successfully
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Error message */}
        {updatePreferencesMutation.isError && (
          <div className="mb-6 rounded-md bg-red-50 p-4">
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
                  {formatAPIError(updatePreferencesMutation.error)}
                </p>
              </div>
            </div>
          </div>
        )}

        <div className="space-y-8">
          {/* Nutrition Targets */}
          <div>
            <h4 className="text-sm font-medium text-gray-900 mb-4">
              Daily Nutrition Targets
            </h4>
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
              {/* Calorie Target */}
              <div>
                <label
                  htmlFor="calorie-target"
                  className="block text-sm font-medium text-gray-700"
                >
                  Calories
                </label>
                <div className="mt-1 relative">
                  <input
                    id="calorie-target"
                    name="calorie-target"
                    type="number"
                    min="0"
                    step="50"
                    value={calorieTarget ?? ''}
                    onChange={(e) =>
                      setCalorieTarget(e.target.value ? Number(e.target.value) : null)
                    }
                    className="
                      appearance-none block w-full px-3 py-2 border border-gray-300
                      rounded-md shadow-sm placeholder-gray-400 focus:outline-none
                      focus:ring-blue-500 focus:border-blue-500
                    "
                    placeholder="2000"
                  />
                  <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                    <span className="text-gray-500 sm:text-sm">kcal</span>
                  </div>
                </div>
              </div>

              {/* Protein Target */}
              <div>
                <label
                  htmlFor="protein-target"
                  className="block text-sm font-medium text-gray-700"
                >
                  Protein
                </label>
                <div className="mt-1 relative">
                  <input
                    id="protein-target"
                    name="protein-target"
                    type="number"
                    min="0"
                    step="5"
                    value={proteinTarget ?? ''}
                    onChange={(e) =>
                      setProteinTarget(e.target.value ? Number(e.target.value) : null)
                    }
                    className="
                      appearance-none block w-full px-3 py-2 border border-gray-300
                      rounded-md shadow-sm placeholder-gray-400 focus:outline-none
                      focus:ring-blue-500 focus:border-blue-500
                    "
                    placeholder="150"
                  />
                  <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                    <span className="text-gray-500 sm:text-sm">g</span>
                  </div>
                </div>
              </div>

              {/* Carb Target */}
              <div>
                <label
                  htmlFor="carb-target"
                  className="block text-sm font-medium text-gray-700"
                >
                  Carbohydrates
                </label>
                <div className="mt-1 relative">
                  <input
                    id="carb-target"
                    name="carb-target"
                    type="number"
                    min="0"
                    step="5"
                    value={carbTarget ?? ''}
                    onChange={(e) =>
                      setCarbTarget(e.target.value ? Number(e.target.value) : null)
                    }
                    className="
                      appearance-none block w-full px-3 py-2 border border-gray-300
                      rounded-md shadow-sm placeholder-gray-400 focus:outline-none
                      focus:ring-blue-500 focus:border-blue-500
                    "
                    placeholder="225"
                  />
                  <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                    <span className="text-gray-500 sm:text-sm">g</span>
                  </div>
                </div>
              </div>

              {/* Fat Target */}
              <div>
                <label
                  htmlFor="fat-target"
                  className="block text-sm font-medium text-gray-700"
                >
                  Fat
                </label>
                <div className="mt-1 relative">
                  <input
                    id="fat-target"
                    name="fat-target"
                    type="number"
                    min="0"
                    step="5"
                    value={fatTarget ?? ''}
                    onChange={(e) =>
                      setFatTarget(e.target.value ? Number(e.target.value) : null)
                    }
                    className="
                      appearance-none block w-full px-3 py-2 border border-gray-300
                      rounded-md shadow-sm placeholder-gray-400 focus:outline-none
                      focus:ring-blue-500 focus:border-blue-500
                    "
                    placeholder="67"
                  />
                  <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                    <span className="text-gray-500 sm:text-sm">g</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Default Servings */}
          <div>
            <label
              htmlFor="default-servings"
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              <div className="flex items-center">
                <Users className="h-4 w-4 text-gray-400 mr-2" />
                Default Number of Servings
              </div>
            </label>
            <select
              id="default-servings"
              name="default-servings"
              value={defaultServings}
              onChange={(e) => setDefaultServings(Number(e.target.value))}
              className="
                mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300
                focus:outline-none focus:ring-blue-500 focus:border-blue-500
                sm:text-sm rounded-md
              "
            >
              {[1, 2, 3, 4, 5, 6, 7, 8].map((num) => (
                <option key={num} value={num}>
                  {num} {num === 1 ? 'serving' : 'servings'}
                </option>
              ))}
            </select>
          </div>

          {/* Preferred Cuisines */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Preferred Cuisines
            </label>
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
              {cuisineCategories.map((cuisine) => (
                <div key={cuisine.id} className="relative flex items-start">
                  <div className="flex items-center h-5">
                    <input
                      id={`cuisine-${cuisine.id}`}
                      type="checkbox"
                      checked={preferredCuisines.includes(cuisine.slug)}
                      onChange={() => toggleCuisine(cuisine.slug)}
                      className="
                        focus:ring-blue-500 h-4 w-4 text-blue-600 border-gray-300
                        rounded
                      "
                    />
                  </div>
                  <div className="ml-3 text-sm">
                    <label
                      htmlFor={`cuisine-${cuisine.id}`}
                      className="font-medium text-gray-700 cursor-pointer"
                    >
                      {cuisine.name}
                    </label>
                  </div>
                </div>
              ))}
            </div>
            {cuisineCategories.length === 0 && (
              <p className="text-sm text-gray-500 italic">
                No cuisines available
              </p>
            )}
          </div>
        </div>

        {/* Submit button */}
        <div className="mt-8 pt-6 border-t border-gray-200">
          <button
            type="submit"
            disabled={updatePreferencesMutation.isPending}
            className="
              inline-flex justify-center py-2 px-4 border border-transparent
              shadow-sm text-sm font-medium rounded-md text-white bg-blue-600
              hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2
              focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed
            "
          >
            {updatePreferencesMutation.isPending ? (
              <>
                <Loader2 className="animate-spin -ml-1 mr-2 h-4 w-4" />
                Saving...
              </>
            ) : (
              'Save Preferences'
            )}
          </button>
        </div>
      </form>
    </div>
  );
};
