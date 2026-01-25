import React from 'react';

/**
 * Card component props interface
 */
export interface CardProps {
  /**
   * Header content of the card
   */
  header?: React.ReactNode;

  /**
   * Body content of the card
   */
  children: React.ReactNode;

  /**
   * Footer content of the card
   */
  footer?: React.ReactNode;

  /**
   * Optional image to display at the top of the card
   */
  image?: {
    src: string;
    alt: string;
    aspectRatio?: 'square' | 'video' | 'wide';
  };

  /**
   * Whether to show hover effects
   * @default false
   */
  hoverable?: boolean;

  /**
   * Click handler for the entire card
   */
  onClick?: () => void;

  /**
   * Additional CSS classes
   */
  className?: string;

  /**
   * Whether the card is in a selected state
   * @default false
   */
  selected?: boolean;

  /**
   * Padding size for card body
   * @default 'md'
   */
  padding?: 'none' | 'sm' | 'md' | 'lg';
}

const paddingClasses = {
  none: 'p-0',
  sm: 'p-3',
  md: 'p-4',
  lg: 'p-6',
};

const aspectRatioClasses = {
  square: 'aspect-square',
  video: 'aspect-video',
  wide: 'aspect-[21/9]',
};

/**
 * Card component for displaying content in a contained, elevated box
 *
 * @example
 * ```tsx
 * <Card
 *   header={<h3>Card Title</h3>}
 *   footer={<Button>Action</Button>}
 *   hoverable
 * >
 *   Card content goes here
 * </Card>
 *
 * <Card
 *   image={{ src: '/image.jpg', alt: 'Description', aspectRatio: 'video' }}
 *   onClick={() => console.log('Card clicked')}
 *   hoverable
 * >
 *   Content with image
 * </Card>
 * ```
 */
export const Card: React.FC<CardProps> = ({
  header,
  children,
  footer,
  image,
  hoverable = false,
  onClick,
  className = '',
  selected = false,
  padding = 'md',
}) => {
  const isClickable = Boolean(onClick);

  const baseClasses = 'bg-white rounded-lg shadow-md overflow-hidden transition-all duration-200';

  const interactionClasses = [
    hoverable && 'hover:shadow-lg hover:-translate-y-0.5',
    isClickable && 'cursor-pointer',
    selected && 'ring-2 ring-blue-500 ring-offset-2',
  ]
    .filter(Boolean)
    .join(' ');

  const combinedClasses = `${baseClasses} ${interactionClasses} ${className}`.trim();

  const handleClick = () => {
    if (onClick) {
      onClick();
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLDivElement>) => {
    if (isClickable && (e.key === 'Enter' || e.key === ' ')) {
      e.preventDefault();
      onClick?.();
    }
  };

  return (
    <div
      className={combinedClasses}
      onClick={handleClick}
      onKeyDown={handleKeyDown}
      role={isClickable ? 'button' : undefined}
      tabIndex={isClickable ? 0 : undefined}
      aria-pressed={isClickable && selected ? selected : undefined}
    >
      {image && (
        <div className={`w-full overflow-hidden ${aspectRatioClasses[image.aspectRatio ?? 'video']}`}>
          <img
            src={image.src}
            alt={image.alt}
            className="w-full h-full object-cover"
            loading="lazy"
          />
        </div>
      )}

      {header && (
        <div className={`border-b border-gray-200 ${paddingClasses[padding]}`}>
          {header}
        </div>
      )}

      <div className={paddingClasses[padding]}>
        {children}
      </div>

      {footer && (
        <div className={`border-t border-gray-200 bg-gray-50 ${paddingClasses[padding]}`}>
          {footer}
        </div>
      )}
    </div>
  );
};

export default Card;
