/**
 * FavoriteNoteModal - Modal for adding/editing notes on a favorite recipe.
 */

import React, { useState, useEffect } from 'react';
import { Modal } from '../common/Modal';
import { Button } from '../common/Button';
import { useUpdateFavorite } from '../../hooks/useFavorites';
import type { FavoriteRecipe } from '../../types';

interface FavoriteNoteModalProps {
  isOpen: boolean;
  onClose: () => void;
  favorite: FavoriteRecipe;
}

export const FavoriteNoteModal: React.FC<FavoriteNoteModalProps> = ({
  isOpen,
  onClose,
  favorite,
}) => {
  const [notes, setNotes] = useState(favorite.notes ?? '');
  const [hasChanges, setHasChanges] = useState(false);

  const updateMutation = useUpdateFavorite();

  useEffect(() => {
    setNotes(favorite.notes || '');
    setHasChanges(false);
  }, [favorite.notes, isOpen]);

  const handleNotesChange = (e: React.ChangeEvent<HTMLTextAreaElement>): void => {
    setNotes(e.target.value);
    setHasChanges(e.target.value !== (favorite.notes || ''));
  };

  const handleSave = async (): Promise<void> => {
    if (!hasChanges) {
      onClose();
      return;
    }

    try {
      const trimmedNotes = notes.trim();
      await updateMutation.mutateAsync({
        recipeId: favorite.recipe.id,
        data: trimmedNotes ? { notes: trimmedNotes } : {},
      });
      onClose();
    } catch (error) {
      console.error('Failed to update notes:', error);
    }
  };

  const handleCancel = (): void => {
    setNotes(favorite.notes || '');
    setHasChanges(false);
    onClose();
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleCancel}
      title="Edit Recipe Notes"
      size="lg"
    >
      <div className="space-y-4">
        <div>
          <p className="text-sm text-gray-600 mb-2">
            Recipe: <span className="font-semibold text-gray-900">{favorite.recipe.name}</span>
          </p>
        </div>

        <div>
          <label htmlFor="favorite-notes" className="block text-sm font-medium text-gray-700 mb-2">
            Your Notes
          </label>
          <textarea
            id="favorite-notes"
            value={notes}
            onChange={handleNotesChange}
            rows={6}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none"
            placeholder="Add notes about this recipe... (e.g., modifications, serving suggestions, when you last made it)"
            disabled={updateMutation.isPending}
          />
          <p className="mt-1 text-xs text-gray-500">
            {notes.length} characters
          </p>
        </div>

        {updateMutation.isError && (
          <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-600">
              Failed to save notes. Please try again.
            </p>
          </div>
        )}

        <div className="flex justify-end gap-3 pt-4 border-t border-gray-200">
          <Button
            variant="outline"
            onClick={handleCancel}
            disabled={updateMutation.isPending}
          >
            Cancel
          </Button>
          <Button
            variant="primary"
            onClick={handleSave}
            disabled={!hasChanges || updateMutation.isPending}
            loading={updateMutation.isPending}
          >
            Save Notes
          </Button>
        </div>
      </div>
    </Modal>
  );
};
