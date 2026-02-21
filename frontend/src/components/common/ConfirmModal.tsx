import React from 'react';
import { Modal } from './Modal';

/**
 * ConfirmModal variant types
 */
export type ConfirmModalVariant = 'danger' | 'warning' | 'default';

/**
 * ConfirmModal component props
 */
export interface ConfirmModalProps {
  /** Whether the modal is open */
  isOpen: boolean;
  /** Callback when the modal should close */
  onClose: () => void;
  /** Callback when the confirm button is clicked */
  onConfirm: () => void;
  /** Modal title */
  title: string;
  /** Confirmation message body */
  message: string;
  /** Label for the confirm button */
  confirmLabel?: string;
  /** Label for the cancel button */
  cancelLabel?: string;
  /** Visual variant controlling the confirm button colour */
  variant?: ConfirmModalVariant;
}

const confirmButtonClasses: Record<ConfirmModalVariant, string> = {
  danger: 'bg-red-500 hover:bg-red-600 text-white',
  warning: 'bg-amber-500 hover:bg-amber-600 text-white',
  default: 'bg-indigo-500 hover:bg-indigo-600 text-white',
};

/**
 * ConfirmModal - a reusable confirmation dialog built on top of Modal.
 *
 * Replaces native `window.confirm()` calls with an accessible, styled modal.
 *
 * @example
 * ```tsx
 * <ConfirmModal
 *   isOpen={showConfirm}
 *   onClose={() => setShowConfirm(false)}
 *   onConfirm={handleDelete}
 *   title="Delete item"
 *   message="Are you sure? This cannot be undone."
 *   confirmLabel="Delete"
 *   variant="danger"
 * />
 * ```
 */
export const ConfirmModal: React.FC<ConfirmModalProps> = ({
  isOpen,
  onClose,
  onConfirm,
  title,
  message,
  confirmLabel = 'Confirm',
  cancelLabel = 'Cancel',
  variant = 'default',
}) => {
  const handleConfirm = () => {
    onConfirm();
    onClose();
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={title} size="sm">
      <p className="text-gray-600 mb-6">{message}</p>
      <div className="flex justify-end gap-3">
        <button
          type="button"
          onClick={onClose}
          className="px-4 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50"
        >
          {cancelLabel}
        </button>
        <button
          type="button"
          onClick={handleConfirm}
          className={`px-4 py-2 text-sm rounded-lg ${confirmButtonClasses[variant]}`}
        >
          {confirmLabel}
        </button>
      </div>
    </Modal>
  );
};

export default ConfirmModal;
