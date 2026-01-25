import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { SearchBar } from '../SearchBar';

describe('SearchBar', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('renders with placeholder', () => {
    render(<SearchBar value="" onChange={vi.fn()} placeholder="Search recipes..." />);
    expect(screen.getByPlaceholderText('Search recipes...')).toBeInTheDocument();
  });

  it('displays current value', () => {
    render(<SearchBar value="test query" onChange={vi.fn()} />);
    expect(screen.getByRole('searchbox')).toHaveValue('test query');
  });

  it('calls onChange after debounce delay', () => {
    const handleChange = vi.fn();
    render(<SearchBar value="" onChange={handleChange} debounceMs={300} />);

    const input = screen.getByRole('searchbox');
    fireEvent.change(input, { target: { value: 'test' } });

    expect(handleChange).not.toHaveBeenCalled();

    vi.runAllTimers();

    expect(handleChange).toHaveBeenCalledWith('test');
  });

  it('calls onChangeImmediate without debounce', () => {
    const handleChangeImmediate = vi.fn();
    render(
      <SearchBar
        value=""
        onChange={vi.fn()}
        onChangeImmediate={handleChangeImmediate}
      />
    );

    const input = screen.getByRole('searchbox');
    fireEvent.change(input, { target: { value: 'test' } });

    expect(handleChangeImmediate).toHaveBeenCalledWith('test');
  });

  it('shows clear button when there is a value', () => {
    render(<SearchBar value="test" onChange={vi.fn()} />);
    expect(screen.getByLabelText('Clear search')).toBeInTheDocument();
  });

  it('does not show clear button when value is empty', () => {
    render(<SearchBar value="" onChange={vi.fn()} />);
    expect(screen.queryByLabelText('Clear search')).not.toBeInTheDocument();
  });

  it('clears value when clear button is clicked', () => {
    const handleChange = vi.fn();
    render(<SearchBar value="test" onChange={handleChange} />);

    fireEvent.click(screen.getByLabelText('Clear search'));

    expect(handleChange).toHaveBeenCalledWith('');
  });

  it('calls onClear when clear button is clicked', () => {
    const handleClear = vi.fn();
    render(<SearchBar value="test" onChange={vi.fn()} onClear={handleClear} />);

    fireEvent.click(screen.getByLabelText('Clear search'));

    expect(handleClear).toHaveBeenCalledTimes(1);
  });

  it('clears value on Escape key', () => {
    const handleChange = vi.fn();
    render(<SearchBar value="test" onChange={handleChange} />);

    const input = screen.getByRole('searchbox');
    fireEvent.keyDown(input, { key: 'Escape' });

    expect(handleChange).toHaveBeenCalledWith('');
  });

  it('shows loading spinner when loading prop is true', () => {
    render(<SearchBar value="" onChange={vi.fn()} loading />);
    expect(screen.getByLabelText('Searching...')).toBeInTheDocument();
  });

  it('hides clear button when loading', () => {
    render(<SearchBar value="test" onChange={vi.fn()} loading />);
    expect(screen.queryByLabelText('Clear search')).not.toBeInTheDocument();
  });

  it('applies different sizes correctly', () => {
    const { rerender } = render(<SearchBar value="" onChange={vi.fn()} size="sm" />);
    expect(screen.getByRole('searchbox')).toHaveClass('h-9', 'text-sm');

    rerender(<SearchBar value="" onChange={vi.fn()} size="md" />);
    expect(screen.getByRole('searchbox')).toHaveClass('h-10', 'text-base');

    rerender(<SearchBar value="" onChange={vi.fn()} size="lg" />);
    expect(screen.getByRole('searchbox')).toHaveClass('h-12', 'text-lg');
  });

  it('applies fullWidth class when fullWidth prop is true', () => {
    const { container } = render(<SearchBar value="" onChange={vi.fn()} fullWidth />);
    expect(container.firstChild).toHaveClass('w-full');
  });

  it('auto-focuses when autoFocus prop is true', () => {
    render(<SearchBar value="" onChange={vi.fn()} autoFocus />);
    expect(screen.getByRole('searchbox')).toHaveFocus();
  });

  it('applies custom aria-label', () => {
    render(<SearchBar value="" onChange={vi.fn()} aria-label="Search for recipes" />);
    expect(screen.getByLabelText('Search for recipes')).toBeInTheDocument();
  });

  it('cancels previous debounce timer on new input', () => {
    const handleChange = vi.fn();
    render(<SearchBar value="" onChange={handleChange} debounceMs={300} />);

    const input = screen.getByRole('searchbox');

    fireEvent.change(input, { target: { value: 'test1' } });
    vi.advanceTimersByTime(100);

    fireEvent.change(input, { target: { value: 'test2' } });
    vi.advanceTimersByTime(100);

    fireEvent.change(input, { target: { value: 'test3' } });
    vi.runAllTimers();

    expect(handleChange).toHaveBeenCalledTimes(1);
    expect(handleChange).toHaveBeenCalledWith('test3');
  });
});
