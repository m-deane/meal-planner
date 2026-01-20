/**
 * Export and sharing options for shopping lists.
 */

import React, { useState } from 'react';
import {
  Download,
  Copy,
  Share2,
  Printer,
  Mail,
  CheckCircle,
  AlertCircle,
} from 'lucide-react';
import { useShoppingListStore } from '../../store/shoppingListStore';
import {
  formatForClipboard,
  printList,
  shareList,
  copyToClipboard,
  canShare,
} from '../../utils/shoppingList';

export interface ExportOptionsProps {
  className?: string;
}

type ExportStatus = 'idle' | 'success' | 'error';

export const ExportOptions: React.FC<ExportOptionsProps> = ({ className = '' }) => {
  const { state } = useShoppingListStore();
  const [copyStatus, setCopyStatus] = useState<ExportStatus>('idle');
  const [shareStatus, setShareStatus] = useState<ExportStatus>('idle');
  const [statusMessage, setStatusMessage] = useState<string>('');

  const hasItems = state.items.length > 0;

  const showStatus = (message: string): void => {
    setStatusMessage(message);
    setTimeout(() => {
      setStatusMessage('');
    }, 3000);
  };

  const handleCopyToClipboard = async (): Promise<void> => {
    try {
      const text = formatForClipboard(state.items);
      await copyToClipboard(text);
      setCopyStatus('success');
      showStatus('Copied to clipboard!');
      setTimeout(() => setCopyStatus('idle'), 2000);
    } catch (error) {
      setCopyStatus('error');
      showStatus('Failed to copy to clipboard');
      setTimeout(() => setCopyStatus('idle'), 2000);
    }
  };

  const handlePrint = (): void => {
    try {
      printList(state.items);
    } catch (error) {
      showStatus('Failed to open print dialog');
    }
  };

  const handleShare = async (): Promise<void> => {
    try {
      await shareList(state.items);
      setShareStatus('success');
      showStatus('Shared successfully!');
      setTimeout(() => setShareStatus('idle'), 2000);
    } catch (error) {
      setShareStatus('error');
      showStatus('Failed to share');
      setTimeout(() => setShareStatus('idle'), 2000);
    }
  };

  const handleDownloadJSON = (): void => {
    try {
      const data = JSON.stringify(state.items, null, 2);
      const blob = new Blob([data], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `shopping-list-${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      showStatus('Downloaded as JSON');
    } catch (error) {
      showStatus('Failed to download');
    }
  };

  const handleEmailList = (): void => {
    try {
      const text = formatForClipboard(state.items);
      const subject = encodeURIComponent('Shopping List');
      const body = encodeURIComponent(text);
      const mailtoLink = `mailto:?subject=${subject}&body=${body}`;
      window.location.href = mailtoLink;
    } catch (error) {
      showStatus('Failed to open email client');
    }
  };

  return (
    <div className={`bg-white rounded-lg shadow-sm border border-gray-200 p-4 ${className}`}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Export & Share</h3>
        {statusMessage && (
          <div
            className={`flex items-center gap-2 px-3 py-1 rounded-lg text-sm font-medium ${
              copyStatus === 'success' || shareStatus === 'success'
                ? 'bg-green-50 text-green-700'
                : 'bg-red-50 text-red-700'
            }`}
          >
            {copyStatus === 'success' || shareStatus === 'success' ? (
              <CheckCircle className="w-4 h-4" />
            ) : (
              <AlertCircle className="w-4 h-4" />
            )}
            {statusMessage}
          </div>
        )}
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
        {/* Copy to clipboard */}
        <button
          onClick={handleCopyToClipboard}
          disabled={!hasItems}
          className="flex flex-col items-center gap-2 p-4 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <Copy className="w-6 h-6 text-gray-700" />
          <span className="text-sm font-medium text-gray-700">Copy Text</span>
        </button>

        {/* Print */}
        <button
          onClick={handlePrint}
          disabled={!hasItems}
          className="flex flex-col items-center gap-2 p-4 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <Printer className="w-6 h-6 text-gray-700" />
          <span className="text-sm font-medium text-gray-700">Print</span>
        </button>

        {/* Share (if available) */}
        {canShare() && (
          <button
            onClick={handleShare}
            disabled={!hasItems}
            className="flex flex-col items-center gap-2 p-4 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Share2 className="w-6 h-6 text-gray-700" />
            <span className="text-sm font-medium text-gray-700">Share</span>
          </button>
        )}

        {/* Email */}
        <button
          onClick={handleEmailList}
          disabled={!hasItems}
          className="flex flex-col items-center gap-2 p-4 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <Mail className="w-6 h-6 text-gray-700" />
          <span className="text-sm font-medium text-gray-700">Email</span>
        </button>

        {/* Download JSON */}
        <button
          onClick={handleDownloadJSON}
          disabled={!hasItems}
          className="flex flex-col items-center gap-2 p-4 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <Download className="w-6 h-6 text-gray-700" />
          <span className="text-sm font-medium text-gray-700">JSON</span>
        </button>
      </div>

      {!hasItems && (
        <p className="mt-4 text-sm text-gray-500 text-center">
          Add items to enable export options
        </p>
      )}
    </div>
  );
};
