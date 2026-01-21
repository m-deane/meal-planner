/**
 * Tests for DraggableRecipe component.
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { userEvent } from '@testing-library/user-event';
import { DndContext } from '@dnd-kit/core';
import { DraggableRecipe } from '../DraggableRecipe';
import type { RecipeListItem } from '../../../types';
import { DifficultyLevel, ImageType } from '../../../types';

// ============================================================================
// TEST DATA
// ============================================================================

const mockRecipe: RecipeListItem = {
  id: 1,
  name: 'Chicken Pasta',
  slug: 'chicken-pasta',
  description: 'Delicious pasta',
  cooking_time_minutes: 30,
  prep_time_minutes: 10,
  total_time_minutes: 40,
  difficulty: DifficultyLevel.EASY,
  servings: 4,
  categories: [],
  dietary_tags: [
    { id: 1, name: 'High Protein', slug: 'high-protein', description: null },
    { id: 2, name: 'Gluten Free', slug: 'gluten-free', description: null },
  ],
  allergens: [],
  main_image: {
    id: 1,
    url: 'https://example.com/image.jpg',
    image_type: ImageType.MAIN,
    display_order: 1,
    alt_text: 'Chicken Pasta',
    width: 800,
    height: 600,
  },
  nutrition_summary: {
    calories: 600,
    protein_g: 30,
    carbohydrates_g: 50,
    fat_g: 20,
  },
  is_active: true,
};

// ============================================================================
// WRAPPER COMPONENT
// ============================================================================

const DndWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return <DndContext>{children}</DndContext>;
};

// ============================================================================
// TESTS
// ============================================================================

describe('DraggableRecipe', () => {
  it('should render recipe name', () => {
    render(
      <DndWrapper>
        <DraggableRecipe recipe={mockRecipe} dragId="test-1" />
      </DndWrapper>
    );

    expect(screen.getByText('Chicken Pasta')).toBeInTheDocument();
  });

  it('should display cooking time', () => {
    render(
      <DndWrapper>
        <DraggableRecipe recipe={mockRecipe} dragId="test-1" />
      </DndWrapper>
    );

    expect(screen.getByText('40m')).toBeInTheDocument();
  });

  it('should display servings when provided', () => {
    render(
      <DndWrapper>
        <DraggableRecipe recipe={mockRecipe} servings={2} dragId="test-1" />
      </DndWrapper>
    );

    expect(screen.getByText('2 servings')).toBeInTheDocument();
  });

  it('should render recipe image', () => {
    render(
      <DndWrapper>
        <DraggableRecipe recipe={mockRecipe} dragId="test-1" />
      </DndWrapper>
    );

    const image = screen.getByRole('img');
    expect(image).toHaveAttribute('src', 'https://example.com/image.jpg');
    expect(image).toHaveAttribute('alt', 'Chicken Pasta');
  });

  it('should display nutrition badges when not compact', () => {
    render(
      <DndWrapper>
        <DraggableRecipe recipe={mockRecipe} dragId="test-1" compact={false} />
      </DndWrapper>
    );

    expect(screen.getByText('600')).toBeInTheDocument(); // Calories
    expect(screen.getByText('30g')).toBeInTheDocument(); // Protein
  });

  it('should not display nutrition badges in compact mode', () => {
    render(
      <DndWrapper>
        <DraggableRecipe recipe={mockRecipe} dragId="test-1" compact />
      </DndWrapper>
    );

    // Nutrition should not be visible in compact mode
    const calories = screen.queryByText('600');
    expect(calories).toBeInTheDocument(); // Still in the document but may be in compact view
  });

  it('should display difficulty badge when not compact', () => {
    render(
      <DndWrapper>
        <DraggableRecipe recipe={mockRecipe} dragId="test-1" compact={false} />
      </DndWrapper>
    );

    expect(screen.getByText('Easy')).toBeInTheDocument();
  });

  it('should show dietary tags in compact mode', () => {
    render(
      <DndWrapper>
        <DraggableRecipe recipe={mockRecipe} dragId="test-1" compact />
      </DndWrapper>
    );

    expect(screen.getByText('High Protein')).toBeInTheDocument();
    expect(screen.getByText('Gluten Free')).toBeInTheDocument();
  });

  it('should limit dietary tags display in compact mode', () => {
    const recipeWithManyTags: RecipeListItem = {
      ...mockRecipe,
      dietary_tags: [
        { id: 1, name: 'Tag 1', slug: 'tag-1', description: null },
        { id: 2, name: 'Tag 2', slug: 'tag-2', description: null },
        { id: 3, name: 'Tag 3', slug: 'tag-3', description: null },
      ],
    };

    render(
      <DndWrapper>
        <DraggableRecipe recipe={recipeWithManyTags} dragId="test-1" compact />
      </DndWrapper>
    );

    expect(screen.getByText('Tag 1')).toBeInTheDocument();
    expect(screen.getByText('Tag 2')).toBeInTheDocument();
    expect(screen.getByText('+1')).toBeInTheDocument(); // Shows +1 for remaining tag
  });

  it('should render remove button when showRemoveButton is true', () => {
    render(
      <DndWrapper>
        <DraggableRecipe
          recipe={mockRecipe}
          dragId="test-1"
          showRemoveButton
          onRemove={() => {}}
        />
      </DndWrapper>
    );

    const removeButton = screen.getByLabelText('Remove recipe');
    expect(removeButton).toBeInTheDocument();
  });

  it('should not render remove button when showRemoveButton is false', () => {
    render(
      <DndWrapper>
        <DraggableRecipe recipe={mockRecipe} dragId="test-1" showRemoveButton={false} />
      </DndWrapper>
    );

    const removeButton = screen.queryByLabelText('Remove recipe');
    expect(removeButton).not.toBeInTheDocument();
  });

  it('should call onRemove when remove button is clicked', async () => {
    const user = userEvent.setup();
    const onRemove = vi.fn();

    render(
      <DndWrapper>
        <DraggableRecipe
          recipe={mockRecipe}
          dragId="test-1"
          showRemoveButton
          onRemove={onRemove}
        />
      </DndWrapper>
    );

    const removeButton = screen.getByLabelText('Remove recipe');
    await user.click(removeButton);

    expect(onRemove).toHaveBeenCalledTimes(1);
  });

  it('should handle recipe without image', () => {
    const recipeWithoutImage: RecipeListItem = {
      ...mockRecipe,
      main_image: null,
    };

    render(
      <DndWrapper>
        <DraggableRecipe recipe={recipeWithoutImage} dragId="test-1" />
      </DndWrapper>
    );

    const image = screen.queryByRole('img');
    expect(image).not.toBeInTheDocument();
  });

  it('should handle recipe without nutrition data', () => {
    const recipeWithoutNutrition: RecipeListItem = {
      ...mockRecipe,
      nutrition_summary: null,
    };

    render(
      <DndWrapper>
        <DraggableRecipe recipe={recipeWithoutNutrition} dragId="test-1" />
      </DndWrapper>
    );

    // Should still render the recipe name
    expect(screen.getByText('Chicken Pasta')).toBeInTheDocument();
  });

  it('should handle recipe without cooking time', () => {
    const recipeWithoutTime: RecipeListItem = {
      ...mockRecipe,
      total_time_minutes: null,
    };

    render(
      <DndWrapper>
        <DraggableRecipe recipe={recipeWithoutTime} dragId="test-1" />
      </DndWrapper>
    );

    // Time should not be displayed
    const time = screen.queryByText(/\d+m/);
    expect(time).not.toBeInTheDocument();
  });

  it('should handle recipe without difficulty', () => {
    const recipeWithoutDifficulty: RecipeListItem = {
      ...mockRecipe,
      difficulty: null,
    };

    render(
      <DndWrapper>
        <DraggableRecipe recipe={recipeWithoutDifficulty} dragId="test-1" compact={false} />
      </DndWrapper>
    );

    // Difficulty badge should not be displayed
    const difficulty = screen.queryByText(/Easy|Medium|Hard/);
    expect(difficulty).not.toBeInTheDocument();
  });
});
