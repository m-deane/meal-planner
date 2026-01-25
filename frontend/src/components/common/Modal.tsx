import React, { Fragment } from 'react';
import { Dialog, Transition } from '@headlessui/react';
import { XMarkIcon } from '@heroicons/react/24/outline';

/**
 * Modal size types
 */
export type ModalSize = 'sm' | 'md' | 'lg' | 'full';

/**
 * Modal component props interface
 */
export interface ModalProps {
  /**
   * Whether the modal is open
   */
  isOpen: boolean;

  /**
   * Callback when the modal should close
   */
  onClose: () => void;

  /**
   * Modal title
   */
  title?: React.ReactNode;

  /**
   * Modal description (shown below title)
   */
  description?: React.ReactNode;

  /**
   * Main content of the modal
   */
  children: React.ReactNode;

  /**
   * Action buttons/footer content
   */
  actions?: React.ReactNode;

  /**
   * Size of the modal
   * @default 'md'
   */
  size?: ModalSize;

  /**
   * Whether to show the close button
   * @default true
   */
  showCloseButton?: boolean;

  /**
   * Whether clicking the backdrop closes the modal
   * @default true
   */
  closeOnBackdropClick?: boolean;

  /**
   * Additional CSS classes for the modal panel
   */
  className?: string;

  /**
   * Whether to prevent scrolling when modal is open
   * @default true
   */
  preventScroll?: boolean;
}

const sizeClasses: Record<ModalSize, string> = {
  sm: 'max-w-md',
  md: 'max-w-lg',
  lg: 'max-w-2xl',
  full: 'max-w-full mx-4',
};

/**
 * Modal component using Headless UI Dialog
 *
 * @example
 * ```tsx
 * const [isOpen, setIsOpen] = useState(false);
 *
 * <Modal
 *   isOpen={isOpen}
 *   onClose={() => setIsOpen(false)}
 *   title="Confirm Action"
 *   description="Are you sure you want to proceed?"
 *   size="md"
 *   actions={
 *     <>
 *       <Button variant="outline" onClick={() => setIsOpen(false)}>
 *         Cancel
 *       </Button>
 *       <Button variant="primary" onClick={handleConfirm}>
 *         Confirm
 *       </Button>
 *     </>
 *   }
 * >
 *   Modal content goes here
 * </Modal>
 * ```
 */
export const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  title,
  description,
  children,
  actions,
  size = 'md',
  showCloseButton = true,
  closeOnBackdropClick = true,
  className = '',
}) => {
  const handleClose = () => {
    if (closeOnBackdropClick) {
      onClose();
    }
  };

  return (
    <Transition appear show={isOpen} as={Fragment}>
      <Dialog
        as="div"
        className="relative z-50"
        onClose={handleClose}
        static={!closeOnBackdropClick}
      >
        {/* Backdrop */}
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-200"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-black bg-opacity-50 transition-opacity" />
        </Transition.Child>

        {/* Modal positioning */}
        <div className="fixed inset-0 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4 text-center">
            <Transition.Child
              as={Fragment}
              enter="ease-out duration-300"
              enterFrom="opacity-0 scale-95"
              enterTo="opacity-100 scale-100"
              leave="ease-in duration-200"
              leaveFrom="opacity-100 scale-100"
              leaveTo="opacity-0 scale-95"
            >
              <Dialog.Panel
                className={`
                  w-full ${sizeClasses[size]} transform overflow-hidden rounded-lg
                  bg-white text-left align-middle shadow-xl transition-all
                  ${className}
                `.trim().replace(/\s+/g, ' ')}
              >
                {/* Close button */}
                {showCloseButton && (
                  <button
                    type="button"
                    className="absolute right-4 top-4 rounded-lg p-1 text-gray-400 hover:bg-gray-100 hover:text-gray-600 focus:outline-none focus:ring-2 focus:ring-gray-300"
                    onClick={onClose}
                    aria-label="Close modal"
                  >
                    <XMarkIcon className="h-5 w-5" aria-hidden="true" />
                  </button>
                )}

                {/* Header */}
                {(title ?? description) && (
                  <div className="border-b border-gray-200 px-6 py-4 pr-12">
                    {title && (
                      <Dialog.Title
                        as="h3"
                        className="text-lg font-semibold leading-6 text-gray-900"
                      >
                        {title}
                      </Dialog.Title>
                    )}
                    {description && (
                      <Dialog.Description className="mt-2 text-sm text-gray-600">
                        {description}
                      </Dialog.Description>
                    )}
                  </div>
                )}

                {/* Content */}
                <div className="px-6 py-4">
                  {children}
                </div>

                {/* Actions/Footer */}
                {actions && (
                  <div className="border-t border-gray-200 bg-gray-50 px-6 py-4">
                    <div className="flex items-center justify-end gap-3">
                      {actions}
                    </div>
                  </div>
                )}
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition>
  );
};

export default Modal;
