'use client';

import { useEffect, useState } from 'react';

export function Loading() {
  const [showWaking, setShowWaking] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => {
      setShowWaking(true);
    }, 3000);

    return () => clearTimeout(timer);
  }, []);

  return (
    <div className="flex flex-col items-center justify-center gap-4 py-16">
      <div className="flex gap-2">
        <div className="w-2 h-2 bg-[--band] rounded-full animate-pulse"></div>
        <div className="w-2 h-2 bg-[--band] rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
        <div className="w-2 h-2 bg-[--band] rounded-full animate-pulse" style={{ animationDelay: '0.4s' }}></div>
      </div>
      {showWaking && (
        <p className="text-sm text-[--muted] text-center max-w-sm">
          Waking the backend — free tier sleeps after 15 min idle, first request takes ~30–60s.
        </p>
      )}
    </div>
  );
}
