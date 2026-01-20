import React, { useState, useEffect, useRef } from 'react';
import { MagnifyingGlassIcon, XMarkIcon } from '@heroicons/react/24/outline';
import { Spinner } from './Spinner';

/**
 * SearchBar component props interface
 */
export interface SearchBarProps {
  /**
   * Current search value
   */
  value: string;

  /**
   * Callback when search value changes (debounced)
   */
  onChange: (value: string) => void;

  /**
   * Callback when search value changes (immediate, not debounced)
   */
  onChangeImmediate?: (value: string) => void;

  /**
   * Placeholder text
   * @default 'Search...'
   */
  placeholder?: string;

  /**
   * Whether the search is loading
   * @default false
   */
  loading?: boolean;

  /**
   * Debounce delay in milliseconds
   * @default 300
   */
  debounceMs?: number;

  /**
   * Whether to show the clear button
   * @default true
   */
  showClearButton?: boolean;

  /**
   * Callback when clear button is clicked
   */
  onClear?: () => void;

  /**
   * Additional CSS classes
   */
  className?: string;

  /**
   * Whether the input should be full width
   * @default false
   */
  fullWidth?: boolean;

  /**
   * Size of the search bar
   * @default 'md'
   */
  size?: 'sm' | 'md' | 'lg';

  /**
   * Auto-focus on mount
   * @default false
   */
  autoFocus?: boolean;

  /**
   * Accessible label for screen readers
   */
  'aria-label'?: string;
}

const sizeClasses = {
  sm: 'h-9 text-sm',
  md: 'h-10 text-base',
  lg: 'h-12 text-lg',
};

const iconSizeClasses = {
  sm: 'h-4 w-4',
  md: 'h-5 w-5',
  lg: 'h-6 w-6',
};

/**
 * SearchBar component with debouncing and loading state
 *
 * @example
 * ```tsx
 * const [searchQuery, setSearchQuery] = useState('');
 *
 * <SearchBar
 *   value={searchQuery}
 *   onChange={setSearchQuery}
 *   loading={isSearching}
 *   placeholder="Search recipes..."
 *   debounceMs={300}
 * />
 * ```
 */
export const SearchBar: React.FC<SearchBarProps> = ({
  value,
  onChange,
  onChangeImmediate,
  placeholder = 'Search...',
  loading = false,
  debounceMs = 300,
  showClearButton = true,
  onClear,
  className = '',
  fullWidth = false,
  size = 'md',
  autoFocus = false,
  'aria-label': ariaLabel = 'Search',
}) => {
  const [inputValue, setInputValue] = useState(value);
  const debounceTimerRef = useRef<number | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Sync internal state with external value
  useEffect(() => {
    setInputValue(value);
  }, [value]);

  // Cleanup debounce timer on unmount
  useEffect(() => {
    return () => {
      if (debounceTimerRef.current) {
        window.clearTimeout(debounceTimerRef.current);
      }
    };
  }, []);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    setInputValue(newValue);

    // Call immediate callback if provided
    onChangeImmediate?.(newValue);

    // Clear existing timer
    if (debounceTimerRef.current) {
      window.clearTimeout(debounceTimerRef.current);
    }

    // Set new debounced callback
    debounceTimerRef.current = window.setTimeout(() => {
      onChange(newValue);
    }, debounceMs);
  };

  const handleClear = () => {
    setInputValue('');
    onChange('');
    onClear?.();
    inputRef.current?.focus();
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Escape') {
      handleClear();
    }
  };

  const widthClass = fullWidth ? 'w-full' : 'w-64';

  return (
    <div className={`relative ${widthClass} ${className}`}>
      {/* Search icon */}
      <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
        <MagnifyingGlassIcon
          className={`${iconSizeClasses[size]} text-gray-400`}
          aria-hidden="true"
        />
      </div>

      {/* Input */}
      <input
        ref={inputRef}
        type="text"
        value={inputValue}
        onChange={handleInputChange}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        autoFocus={autoFocus}
        className={`
          ${sizeClasses[size]}
          w-full
          rounded-lg
          border
          border-gray-300
          pl-10
          pr-10
          placeholder-gray-400
          transition-colors
          focus:border-blue-500
          focus:outline-none
          focus:ring-2
          focus:ring-blue-500
          focus:ring-opacity-50
        `.trim().replace(/\s+/g, ' ')}
        aria-label={ariaLabel}
        role="searchbox"
      />

      {/* Loading spinner or clear button */}
      <div className="absolute inset-y-0 right-0 flex items-center pr-3">
        {loading ? (
          <Spinner size="sm" color="gray" label="Searching..." />
        ) : (
          showClearButton &&
          inputValue && (
            <button
              type="button"
              onClick={handleClear}
              className="rounded-full p-1 text-gray-400 hover:bg-gray-100 hover:text-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
              aria-label="Clear search"
            >
              <XMarkIcon className={iconSizeClasses[size]} aria-hidden="true" />
            </button>
          )
        )}
      </div>
    </div>
  );
};

export default SearchBar;
