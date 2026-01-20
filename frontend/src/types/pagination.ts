/**
 * Pagination and sorting types matching backend schemas.
 */

// ============================================================================
// ENUMS
// ============================================================================

export enum SortOrder {
  ASC = 'asc',
  DESC = 'desc',
}

// ============================================================================
// PAGINATION TYPES
// ============================================================================

export interface PaginationParams {
  page: number;
  page_size: number;
}

export interface SortParams {
  sort_by?: string;
  sort_order: SortOrder;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  has_next: boolean;
  has_previous: boolean;
}
