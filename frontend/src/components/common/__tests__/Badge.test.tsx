import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { Badge, BadgeGroup } from '../Badge';

describe('Badge', () => {
  it('renders badge with text', () => {
    render(<Badge>Test Badge</Badge>);
    expect(screen.getByText('Test Badge')).toBeInTheDocument();
  });

  it('applies default color variant', () => {
    const { container } = render(<Badge>Default</Badge>);
    const badge = container.firstChild as HTMLElement;
    expect(badge).toHaveClass('bg-gray-100', 'text-gray-800');
  });

  it('applies different color variants correctly', () => {
    const { rerender, container } = render(<Badge color="success">Success</Badge>);
    let badge = container.firstChild as HTMLElement;
    expect(badge).toHaveClass('bg-green-100', 'text-green-800');

    rerender(<Badge color="warning">Warning</Badge>);
    badge = container.firstChild as HTMLElement;
    expect(badge).toHaveClass('bg-yellow-100', 'text-yellow-800');

    rerender(<Badge color="error">Error</Badge>);
    badge = container.firstChild as HTMLElement;
    expect(badge).toHaveClass('bg-red-100', 'text-red-800');

    rerender(<Badge color="info">Info</Badge>);
    badge = container.firstChild as HTMLElement;
    expect(badge).toHaveClass('bg-cyan-100', 'text-cyan-800');

    rerender(<Badge color="primary">Primary</Badge>);
    badge = container.firstChild as HTMLElement;
    expect(badge).toHaveClass('bg-blue-100', 'text-blue-800');
  });

  it('applies outline variant correctly', () => {
    const { container } = render(<Badge color="primary" outline>Outline</Badge>);
    const badge = container.firstChild as HTMLElement;
    expect(badge).toHaveClass('bg-transparent', 'text-blue-700', 'border-blue-400');
  });

  it('applies different sizes correctly', () => {
    const { rerender, container } = render(<Badge size="sm">Small</Badge>);
    let badge = container.firstChild as HTMLElement;
    expect(badge).toHaveClass('px-2', 'py-0.5', 'text-xs');

    rerender(<Badge size="md">Medium</Badge>);
    badge = container.firstChild as HTMLElement;
    expect(badge).toHaveClass('px-2.5', 'py-1', 'text-sm');
  });

  it('applies pill shape when pill prop is true', () => {
    const { container } = render(<Badge pill>Pill Badge</Badge>);
    const badge = container.firstChild as HTMLElement;
    expect(badge).toHaveClass('rounded-full');
  });

  it('applies rounded shape by default', () => {
    const { container } = render(<Badge>Default Badge</Badge>);
    const badge = container.firstChild as HTMLElement;
    expect(badge).toHaveClass('rounded-md');
  });

  it('renders icon when provided', () => {
    const Icon = () => <span data-testid="badge-icon">Icon</span>;
    render(<Badge icon={<Icon />}>With Icon</Badge>);
    expect(screen.getByTestId('badge-icon')).toBeInTheDocument();
  });

  it('shows remove button when removable is true', () => {
    render(<Badge removable>Removable</Badge>);
    expect(screen.getByLabelText('Remove')).toBeInTheDocument();
  });

  it('calls onRemove when remove button is clicked', () => {
    const handleRemove = vi.fn();
    render(<Badge removable onRemove={handleRemove}>Removable</Badge>);

    fireEvent.click(screen.getByLabelText('Remove'));
    expect(handleRemove).toHaveBeenCalledTimes(1);
  });

  it('stops event propagation when remove button is clicked', () => {
    const handleRemove = vi.fn();
    const handleClick = vi.fn();

    render(
      <div onClick={handleClick}>
        <Badge removable onRemove={handleRemove}>
          Removable
        </Badge>
      </div>
    );

    fireEvent.click(screen.getByLabelText('Remove'));

    expect(handleRemove).toHaveBeenCalledTimes(1);
    expect(handleClick).not.toHaveBeenCalled();
  });

  it('applies custom className', () => {
    const { container } = render(<Badge className="custom-class">Badge</Badge>);
    expect(container.firstChild).toHaveClass('custom-class');
  });
});

describe('BadgeGroup', () => {
  it('renders multiple badges', () => {
    render(
      <BadgeGroup>
        <Badge>Badge 1</Badge>
        <Badge>Badge 2</Badge>
        <Badge>Badge 3</Badge>
      </BadgeGroup>
    );

    expect(screen.getByText('Badge 1')).toBeInTheDocument();
    expect(screen.getByText('Badge 2')).toBeInTheDocument();
    expect(screen.getByText('Badge 3')).toBeInTheDocument();
  });

  it('applies correct gap classes', () => {
    const { rerender, container } = render(
      <BadgeGroup gap="sm">
        <Badge>Badge 1</Badge>
      </BadgeGroup>
    );
    let group = container.firstChild as HTMLElement;
    expect(group).toHaveClass('gap-1');

    rerender(
      <BadgeGroup gap="md">
        <Badge>Badge 1</Badge>
      </BadgeGroup>
    );
    group = container.firstChild as HTMLElement;
    expect(group).toHaveClass('gap-2');

    rerender(
      <BadgeGroup gap="lg">
        <Badge>Badge 1</Badge>
      </BadgeGroup>
    );
    group = container.firstChild as HTMLElement;
    expect(group).toHaveClass('gap-3');
  });

  it('applies wrap class by default', () => {
    const { container } = render(
      <BadgeGroup>
        <Badge>Badge 1</Badge>
      </BadgeGroup>
    );
    expect(container.firstChild).toHaveClass('flex-wrap');
  });

  it('applies nowrap class when wrap is false', () => {
    const { container } = render(
      <BadgeGroup wrap={false}>
        <Badge>Badge 1</Badge>
      </BadgeGroup>
    );
    expect(container.firstChild).toHaveClass('flex-nowrap');
  });

  it('applies custom className', () => {
    const { container } = render(
      <BadgeGroup className="custom-class">
        <Badge>Badge 1</Badge>
      </BadgeGroup>
    );
    expect(container.firstChild).toHaveClass('custom-class');
  });
});
