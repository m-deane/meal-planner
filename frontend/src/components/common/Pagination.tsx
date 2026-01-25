import React from 'react';
import { ChevronLeftIcon, ChevronRightIcon } from '@heroicons/react/24/outline';

/**
 * Pagination component props interface
 */
export interface PaginationProps {
  /**
   * Current page number (1-indexed)
   */
  currentPage: number;

  /**
   * Total number of pages
   */
  totalPages: number;

  /**
   * Callback when page changes
   */
  onPageChange: (page: number) => void;

  /**
   * Number of items per page
   */
  itemsPerPage?: number;

  /**
   * Total number of items
   */
  totalItems?: number;

  /**
   * Available options for items per page
   */
  itemsPerPageOptions?: number[];

  /**
   * Callback when items per page changes
   */
  onItemsPerPageChange?: (itemsPerPage: number) => void;

  /**
   * Number of page buttons to show (excluding ellipsis)
   * @default 7
   */
  siblingCount?: number;

  /**
   * Whether to show items per page selector
   * @default false
   */
  showItemsPerPage?: boolean;

  /**
   * Whether to show total items count
   * @default true
   */
  showTotalItems?: boolean;

  /**
   * Additional CSS classes
   */
  className?: string;
}

/**
 * Generate array of page numbers with ellipsis
 */
const generatePageNumbers = (
  currentPage: number,
  totalPages: number,
  siblingCount = 1
): (number | 'ellipsis')[] => {
  const totalPageNumbers = siblingCount + 5; // siblings + first + last + current + 2 ellipsis

  if (totalPages <= totalPageNumbers) {
    return Array.from({ length: totalPages }, (_, i) => i + 1);
  }

  const leftSiblingIndex = Math.max(currentPage - siblingCount, 1);
  const rightSiblingIndex = Math.min(currentPage + siblingCount, totalPages);

  const shouldShowLeftEllipsis = leftSiblingIndex > 2;
  const shouldShowRightEllipsis = rightSiblingIndex < totalPages - 1;

  if (!shouldShowLeftEllipsis && shouldShowRightEllipsis) {
    const leftItemCount = 3 + 2 * siblingCount;
    const leftRange = Array.from({ length: leftItemCount }, (_, i) => i + 1);
    return [...leftRange, 'ellipsis', totalPages];
  }

  if (shouldShowLeftEllipsis && !shouldShowRightEllipsis) {
    const rightItemCount = 3 + 2 * siblingCount;
    const rightRange = Array.from(
      { length: rightItemCount },
      (_, i) => totalPages - rightItemCount + i + 1
    );
    return [1, 'ellipsis', ...rightRange];
  }

  if (shouldShowLeftEllipsis && shouldShowRightEllipsis) {
    const middleRange = Array.from(
      { length: rightSiblingIndex - leftSiblingIndex + 1 },
      (_, i) => leftSiblingIndex + i
    );
    return [1, 'ellipsis', ...middleRange, 'ellipsis', totalPages];
  }

  return [];
};

/**
 * Pagination component with page numbers, navigation, and items per page selector
 *
 * @example
 * ```tsx
 * <Pagination
 *   currentPage={currentPage}
 *   totalPages={totalPages}
 *   onPageChange={setCurrentPage}
 *   totalItems={totalItems}
 *   itemsPerPage={itemsPerPage}
 *   itemsPerPageOptions={[10, 25, 50, 100]}
 *   onItemsPerPageChange={setItemsPerPage}
 *   showItemsPerPage
 * />
 * ```
 */
export const Pagination: React.FC<PaginationProps> = ({
  currentPage,
  totalPages,
  onPageChange,
  itemsPerPage,
  totalItems,
  itemsPerPageOptions = [10, 25, 50, 100],
  onItemsPerPageChange,
  siblingCount = 1,
  showItemsPerPage = false,
  showTotalItems = true,
  className = '',
}) => {
  const pageNumbers = generatePageNumbers(currentPage, totalPages, siblingCount);

  const handlePrevious = () => {
    if (currentPage > 1) {
      onPageChange(currentPage - 1);
    }
  };

  const handleNext = () => {
    if (currentPage < totalPages) {
      onPageChange(currentPage + 1);
    }
  };

  const handlePageClick = (page: number) => {
    onPageChange(page);
  };

  const handleItemsPerPageChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newItemsPerPage = parseInt(e.target.value, 10);
    onItemsPerPageChange?.(newItemsPerPage);
  };

  if (totalPages <= 0) {
    return null;
  }

  return (
    <div className={`flex items-center justify-between gap-4 ${className}`}>
      {/* Items info and per-page selector */}
      <div className="flex items-center gap-4">
        {showTotalItems && totalItems !== undefined && (
          <div className="text-sm text-gray-700">
            Showing{' '}
            <span className="font-medium">
              {itemsPerPage ? (currentPage - 1) * itemsPerPage + 1 : 1}
            </span>{' '}
            to{' '}
            <span className="font-medium">
              {itemsPerPage
                ? Math.min(currentPage * itemsPerPage, totalItems)
                : totalItems}
            </span>{' '}
            of <span className="font-medium">{totalItems}</span> results
          </div>
        )}

        {showItemsPerPage && itemsPerPage && onItemsPerPageChange && (
          <div className="flex items-center gap-2">
            <label htmlFor="items-per-page" className="text-sm text-gray-700">
              Per page:
            </label>
            <select
              id="items-per-page"
              value={itemsPerPage}
              onChange={handleItemsPerPageChange}
              className="rounded-md border border-gray-300 px-3 py-1.5 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              aria-label="Items per page"
            >
              {itemsPerPageOptions.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      {/* Page navigation */}
      <nav
        className="inline-flex items-center gap-1 rounded-md shadow-sm"
        aria-label="Pagination"
      >
        {/* Previous button */}
        <button
          type="button"
          onClick={handlePrevious}
          disabled={currentPage === 1}
          className="inline-flex items-center rounded-l-md border border-gray-300 bg-white px-2 py-2 text-sm font-medium text-gray-500 hover:bg-gray-50 focus:z-10 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
          aria-label="Previous page"
        >
          <ChevronLeftIcon className="h-5 w-5" aria-hidden="true" />
        </button>

        {/* Page numbers */}
        {pageNumbers.map((pageNumber, index) => {
          if (pageNumber === 'ellipsis') {
            return (
              <span
                key={`ellipsis-${index}`}
                className="inline-flex items-center border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700"
              >
                ...
              </span>
            );
          }

          const isActive = pageNumber === currentPage;

          return (
            <button
              key={pageNumber}
              type="button"
              onClick={() => { handlePageClick(pageNumber); }}
              className={`
                inline-flex items-center border border-gray-300 px-4 py-2 text-sm font-medium
                focus:z-10 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500
                ${
                  isActive
                    ? 'z-10 bg-blue-600 text-white border-blue-600 hover:bg-blue-700'
                    : 'bg-white text-gray-700 hover:bg-gray-50'
                }
              `.trim().replace(/\s+/g, ' ')}
              aria-label={`Page ${pageNumber}`}
              aria-current={isActive ? 'page' : undefined}
            >
              {pageNumber}
            </button>
          );
        })}

        {/* Next button */}
        <button
          type="button"
          onClick={handleNext}
          disabled={currentPage === totalPages}
          className="inline-flex items-center rounded-r-md border border-gray-300 bg-white px-2 py-2 text-sm font-medium text-gray-500 hover:bg-gray-50 focus:z-10 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
          aria-label="Next page"
        >
          <ChevronRightIcon className="h-5 w-5" aria-hidden="true" />
        </button>
      </nav>
    </div>
  );
};

export default Pagination;
