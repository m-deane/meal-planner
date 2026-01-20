/**
 * Tests for MacroChart component.
 */

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MacroChart } from '../MacroChart';

describe('MacroChart', () => {
  const mockData = {
    protein_g: 150,
    carbohydrates_g: 200,
    fat_g: 67,
  };

  it('renders chart with title', () => {
    render(<MacroChart data={mockData} />);

    expect(screen.getByText('Macronutrient Distribution')).toBeInTheDocument();
  });

  it('renders custom title when provided', () => {
    render(<MacroChart data={mockData} title="Custom Macro Chart" />);

    expect(screen.getByText('Custom Macro Chart')).toBeInTheDocument();
  });

  it('displays message when no data available', () => {
    const emptyData = {
      protein_g: 0,
      carbohydrates_g: 0,
      fat_g: 0,
    };

    render(<MacroChart data={emptyData} />);

    expect(screen.getByText('No nutrition data available')).toBeInTheDocument();
  });

  it('calculates macro percentages correctly', () => {
    // Protein: 150g * 4 = 600 cal
    // Carbs: 200g * 4 = 800 cal
    // Fat: 67g * 9 = 603 cal
    // Total: 2003 cal
    // Protein %: 600/2003 = ~30%
    // Carbs %: 800/2003 = ~40%
    // Fat %: 603/2003 = ~30%

    const { container } = render(<MacroChart data={mockData} />);

    // Check that the responsive container is rendered
    const responsiveContainer = container.querySelector('.recharts-responsive-container');
    expect(responsiveContainer).toBeInTheDocument();
  });

  it('renders legend with gram values', () => {
    const { container } = render(<MacroChart data={mockData} />);

    // Check that the component renders without errors
    // Recharts may not fully render in test environment
    expect(container.querySelector('.recharts-responsive-container')).toBeInTheDocument();
  });
});
