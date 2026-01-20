/**
 * Tests for NutritionCard component.
 */

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { NutritionCard } from '../NutritionCard';

describe('NutritionCard', () => {
  it('renders basic nutrition data', () => {
    render(
      <NutritionCard
        label="Calories"
        value={2000}
        unit="cal"
        decimals={0}
      />
    );

    expect(screen.getByText('Calories')).toBeInTheDocument();
    expect(screen.getByText('2000')).toBeInTheDocument();
    expect(screen.getByText('cal')).toBeInTheDocument();
  });

  it('displays goal information when provided', () => {
    render(
      <NutritionCard
        label="Protein"
        value={150}
        unit="g"
        goal={160}
        decimals={0}
      />
    );

    expect(screen.getByText(/Goal: 160 g/i)).toBeInTheDocument();
  });

  it('shows on target trend when within 5% of goal', () => {
    render(
      <NutritionCard
        label="Calories"
        value={2000}
        unit="cal"
        goal={2000}
        showTrend={true}
      />
    );

    expect(screen.getByText('On target')).toBeInTheDocument();
  });

  it('shows above trend when over goal', () => {
    render(
      <NutritionCard
        label="Calories"
        value={2500}
        unit="cal"
        goal={2000}
        showTrend={true}
        decimals={0}
      />
    );

    expect(screen.getByText(/25% above/i)).toBeInTheDocument();
  });

  it('shows below trend when under goal', () => {
    render(
      <NutritionCard
        label="Protein"
        value={100}
        unit="g"
        goal={150}
        showTrend={true}
        decimals={0}
      />
    );

    expect(screen.getByText(/33% below/i)).toBeInTheDocument();
  });

  it('formats decimals correctly', () => {
    render(
      <NutritionCard
        label="Protein"
        value={150.567}
        unit="g"
        decimals={1}
      />
    );

    expect(screen.getByText('150.6')).toBeInTheDocument();
  });

  it('displays subtitle when provided', () => {
    render(
      <NutritionCard
        label="Calories"
        value={2000}
        unit="cal"
        subtitle="Average per day"
      />
    );

    expect(screen.getByText('Average per day')).toBeInTheDocument();
  });

  it('hides trend when showTrend is false', () => {
    render(
      <NutritionCard
        label="Calories"
        value={2500}
        unit="cal"
        goal={2000}
        showTrend={false}
      />
    );

    expect(screen.queryByText(/above/i)).not.toBeInTheDocument();
  });
});
