/**
 * Tests for MacroBreakdown component.
 */

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MacroBreakdown } from '../MacroBreakdown';

describe('MacroBreakdown', () => {
  const mockData = {
    protein_g: 150,
    carbohydrates_g: 200,
    fat_g: 67,
    fiber_g: 25,
  };

  const mockGoals = {
    protein_g: 150,
    carbs_g: 225,
    fat_g: 67,
    fiber_g: 28,
  };

  it('renders all macro nutrients', () => {
    render(<MacroBreakdown data={mockData} goals={mockGoals} />);

    expect(screen.getByText('Protein')).toBeInTheDocument();
    expect(screen.getByText('Carbohydrates')).toBeInTheDocument();
    expect(screen.getByText('Fat')).toBeInTheDocument();
    expect(screen.getByText('Fiber')).toBeInTheDocument();
  });

  it('displays current and goal values', () => {
    render(<MacroBreakdown data={mockData} goals={mockGoals} />);

    expect(screen.getByText(/150\.0 \/ 150 g/)).toBeInTheDocument();
    expect(screen.getByText(/200\.0 \/ 225 g/)).toBeInTheDocument();
    expect(screen.getByText(/67\.0 \/ 67 g/)).toBeInTheDocument();
    expect(screen.getByText(/25\.0 \/ 28 g/)).toBeInTheDocument();
  });

  it('shows on target status when within 90-110%', () => {
    const { container } = render(<MacroBreakdown data={mockData} goals={mockGoals} />);

    // Protein is exactly 100%, check that progress bar is at 100%
    const text = container.textContent;
    expect(text).toContain('150.0 / 150 g');
    expect(text).toContain('100%');
  });

  it('shows remaining amount when below goal', () => {
    render(<MacroBreakdown data={mockData} goals={mockGoals} />);

    // Carbs: 200/225 = 88.9%, should show remaining
    expect(screen.getByText(/25\.0g remaining/)).toBeInTheDocument();
  });

  it('calculates percentages correctly', () => {
    const { container } = render(<MacroBreakdown data={mockData} goals={mockGoals} />);

    // Check that percentages are displayed in the component
    const text = container.textContent;
    expect(text).toContain('100%'); // Protein
    expect(text).toContain('89%'); // Carbs
  });

  it('displays total macros summary', () => {
    render(<MacroBreakdown data={mockData} goals={mockGoals} />);

    expect(screen.getByText('Total Macros')).toBeInTheDocument();
    expect(screen.getByText('Total Goal')).toBeInTheDocument();

    // Total current: 150 + 200 + 67 = 417g
    const totalMacros = screen.getByText('417g');
    expect(totalMacros).toBeInTheDocument();

    // Total goal: 150 + 225 + 67 = 442g
    const totalGoal = screen.getByText('442g');
    expect(totalGoal).toBeInTheDocument();
  });

  it('renders custom title when provided', () => {
    render(
      <MacroBreakdown
        data={mockData}
        goals={mockGoals}
        title="Custom Title"
      />
    );

    expect(screen.getByText('Custom Title')).toBeInTheDocument();
  });

  it('handles zero goal gracefully', () => {
    const zeroGoals = {
      protein_g: 0,
      carbs_g: 0,
      fat_g: 0,
      fiber_g: 0,
    };

    render(<MacroBreakdown data={mockData} goals={zeroGoals} />);

    // Should not crash and should show 0% or handle gracefully
    expect(screen.getByText('Protein')).toBeInTheDocument();
  });
});
