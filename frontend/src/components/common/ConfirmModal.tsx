import React from 'react';
import { Modal } from './Modal';
import { Button } from './Button';
import type { ButtonVariant } from './Button';

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

const confirmButtonVariant: Record<ConfirmModalVariant, ButtonVariant> = {
  danger: 'danger',
  warning: 'primary',
  default: 'primary',
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
  const handleConfirm = (): void => {
    onConfirm();
    onClose();
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={title} size="sm">
      <p className="text-gray-600 mb-6">{message}</p>
      <div className="flex justify-end gap-3">
        <Button
          variant="ghost"
          size="sm"
          onClick={onClose}
          className="border border-gray-300"
        >
          {cancelLabel}
        </Button>
        <Button
          variant={confirmButtonVariant[variant]}
          size="sm"
          onClick={handleConfirm}
        >
          {confirmLabel}
        </Button>
      </div>
    </Modal>
  );
};

export default ConfirmModal;
