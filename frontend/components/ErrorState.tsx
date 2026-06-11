'use client';

interface ErrorStateProps {
  message: string;
  onRetry: () => void;
}

export function ErrorState({ message, onRetry }: ErrorStateProps) {
  return (
    <div className="flex flex-col items-center justify-center gap-4 py-16 bg-red-50 rounded border border-[--line] p-6">
      <p className="text-sm text-[--ink]">{message}</p>
      <button
        onClick={onRetry}
        className="px-4 py-2 bg-[--accent] text-white rounded text-sm font-medium hover:opacity-90 transition-opacity"
      >
        Retry
      </button>
    </div>
  );
}
