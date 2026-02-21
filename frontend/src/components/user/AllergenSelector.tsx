/**
 * Allergen selection and severity component.
 */

import { useState, FormEvent, useEffect } from 'react';
import { useAllergens as useUserAllergens, useUpdateAllergens } from '../../hooks/useUser';
import { useAllergens as useAllAllergens } from '../../hooks/useCategories';
import { formatAPIError } from '../../api/client';
import { Loader2, CheckCircle, AlertTriangle } from 'lucide-react';
import { AllergenSeverity } from '../../types/user';

interface AllergenSelection {
  allergen_id: number;
  allergen_name: string;
  severity: AllergenSeverity;
  notes: string | null;
}

export const AllergenSelector = (): JSX.Element => {
  const { data: userAllergens, isLoading: userAllergensLoading } = useUserAllergens();
  const { data: allAllergens, isLoading: allAllergensLoading } = useAllAllergens();
  const updateAllergensMutation = useUpdateAllergens();

  const [selections, setSelections] = useState<Map<number, AllergenSelection>>(
    new Map()
  );
  const [success, setSuccess] = useState(false);

  // Initialize selections with user allergens
  useEffect(() => {
    if (userAllergens) {
      const newSelections = new Map<number, AllergenSelection>();
      userAllergens.forEach((ua) => {
        newSelections.set(ua.allergen_id, {
          allergen_id: ua.allergen_id,
          allergen_name: ua.allergen.name,
          severity: ua.severity as AllergenSeverity,
          notes: null,
        });
      });
      setSelections(newSelections);
    }
  }, [userAllergens]);

  const toggleAllergen = (allergenId: number, allergenName: string): void => {
    setSelections((prev) => {
      const newSelections = new Map(prev);
      if (newSelections.has(allergenId)) {
        newSelections.delete(allergenId);
      } else {
        newSelections.set(allergenId, {
          allergen_id: allergenId,
          allergen_name: allergenName,
          severity: AllergenSeverity.MODERATE,
          notes: null,
        });
      }
      return newSelections;
    });
  };

  const updateSeverity = (allergenId: number, severity: AllergenSeverity): void => {
    setSelections((prev) => {
      const newSelections = new Map(prev);
      const existing = newSelections.get(allergenId);
      if (existing) {
        newSelections.set(allergenId, { ...existing, severity });
      }
      return newSelections;
    });
  };

  const updateNotes = (allergenId: number, notes: string): void => {
    setSelections((prev) => {
      const newSelections = new Map(prev);
      const existing = newSelections.get(allergenId);
      if (existing) {
        newSelections.set(allergenId, { ...existing, notes: notes || null });
      }
      return newSelections;
    });
  };

  const handleSubmit = (e: FormEvent<HTMLFormElement>): void => {
    e.preventDefault();
    setSuccess(false);

    const allergenData = Array.from(selections.values()).map((selection) => ({
      allergen_id: selection.allergen_id,
      severity: selection.severity,
      notes: selection.notes,
    }));

    updateAllergensMutation.mutate(
      { allergens: allergenData },
      {
        onSuccess: () => {
          setSuccess(true);
          setTimeout(() => setSuccess(false), 3000);
        },
      }
    );
  };

  const getSeverityColor = (severity: AllergenSeverity): string => {
    switch (severity) {
      case AllergenSeverity.MILD:
        return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case AllergenSeverity.MODERATE:
        return 'text-orange-600 bg-orange-50 border-orange-200';
      case AllergenSeverity.SEVERE:
        return 'text-red-600 bg-red-50 border-red-200';
      case AllergenSeverity.LIFE_THREATENING:
        return 'text-red-800 bg-red-100 border-red-300';
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  if (userAllergensLoading || allAllergensLoading) {
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
          <AlertTriangle className="h-5 w-5 text-gray-400 mr-2" />
          <h3 className="text-lg font-medium text-gray-900">Allergens & Restrictions</h3>
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
                  Allergen preferences updated successfully
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Error message */}
        {updateAllergensMutation.isError && (
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
                  {formatAPIError(updateAllergensMutation.error)}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Allergen list */}
        <div className="space-y-4">
          <p className="text-sm text-gray-600">
            Select allergens you need to avoid and specify their severity.
          </p>

          <div className="space-y-3">
            {allAllergens?.map((allergen) => {
              const isSelected = selections.has(allergen.id);
              const selection = selections.get(allergen.id);

              return (
                <div
                  key={allergen.id}
                  className={`
                    border rounded-lg p-4 transition-colors
                    ${
                      isSelected
                        ? 'border-blue-300 bg-blue-50'
                        : 'border-gray-200 bg-white'
                    }
                  `}
                >
                  <div className="flex items-start">
                    <div className="flex items-center h-5">
                      <input
                        id={`allergen-${allergen.id}`}
                        type="checkbox"
                        checked={isSelected}
                        onChange={() => toggleAllergen(allergen.id, allergen.name)}
                        className="
                          focus:ring-blue-500 h-4 w-4 text-blue-600
                          border-gray-300 rounded
                        "
                      />
                    </div>
                    <div className="ml-3 flex-1">
                      <label
                        htmlFor={`allergen-${allergen.id}`}
                        className="font-medium text-gray-900 cursor-pointer"
                      >
                        {allergen.name}
                      </label>
                      {allergen.description && (
                        <p className="text-sm text-gray-500 mt-1">
                          {allergen.description}
                        </p>
                      )}

                      {/* Severity selector (only shown if selected) */}
                      {isSelected && selection && (
                        <div className="mt-3 space-y-3">
                          <div>
                            <label
                              htmlFor={`severity-${allergen.id}`}
                              className="block text-sm font-medium text-gray-700 mb-2"
                            >
                              Severity
                            </label>
                            <select
                              id={`severity-${allergen.id}`}
                              value={selection.severity}
                              onChange={(e) =>
                                updateSeverity(
                                  allergen.id,
                                  e.target.value as AllergenSeverity
                                )
                              }
                              className={`
                                mt-1 block w-full pl-3 pr-10 py-2 text-base border
                                focus:outline-none focus:ring-blue-500 focus:border-blue-500
                                sm:text-sm rounded-md ${getSeverityColor(selection.severity)}
                              `}
                            >
                              <option value={AllergenSeverity.MILD}>
                                Mild - Minor discomfort
                              </option>
                              <option value={AllergenSeverity.MODERATE}>
                                Moderate - Noticeable reaction
                              </option>
                              <option value={AllergenSeverity.SEVERE}>
                                Severe - Serious reaction
                              </option>
                              <option value={AllergenSeverity.LIFE_THREATENING}>
                                Life-threatening - Anaphylaxis risk
                              </option>
                            </select>
                          </div>

                          {/* Notes */}
                          <div>
                            <label
                              htmlFor={`notes-${allergen.id}`}
                              className="block text-sm font-medium text-gray-700 mb-2"
                            >
                              Notes (optional)
                            </label>
                            <textarea
                              id={`notes-${allergen.id}`}
                              rows={2}
                              value={selection.notes ?? ''}
                              onChange={(e) => updateNotes(allergen.id, e.target.value)}
                              className="
                                shadow-sm focus:ring-blue-500 focus:border-blue-500
                                block w-full sm:text-sm border-gray-300 rounded-md
                              "
                              placeholder="Add any additional notes..."
                            />
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {allAllergens?.length === 0 && (
            <p className="text-center text-gray-500 py-8">
              No allergen data available
            </p>
          )}
        </div>

        {/* Submit button */}
        <div className="mt-8 pt-6 border-t border-gray-200">
          <button
            type="submit"
            disabled={updateAllergensMutation.isPending}
            className="
              inline-flex justify-center py-2 px-4 border border-transparent
              shadow-sm text-sm font-medium rounded-md text-white bg-blue-600
              hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2
              focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed
            "
          >
            {updateAllergensMutation.isPending ? (
              <>
                <Loader2 className="animate-spin -ml-1 mr-2 h-4 w-4" />
                Saving...
              </>
            ) : (
              'Save Allergen Preferences'
            )}
          </button>
        </div>
      </form>
    </div>
  );
};
