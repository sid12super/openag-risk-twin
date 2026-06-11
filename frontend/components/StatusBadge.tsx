'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';

export function StatusBadge() {
  const [status, setStatus] = useState<'live' | 'waking' | 'offline'>('waking');

  useEffect(() => {
    let cancelled = false;
    let attempts = 0;
    const maxAttempts = 15; // ~60s, covers a Render free-tier cold start
    const delayMs = 4000;

    const ping = async () => {
      try {
        await api.health();
        if (!cancelled) setStatus('live');
      } catch {
        if (cancelled) return;
        attempts += 1;
        if (attempts >= maxAttempts) {
          setStatus('offline');
        } else {
          setStatus('waking');
          setTimeout(ping, delayMs);
        }
      }
    };

    ping();
    return () => { cancelled = true; };
  }, []);

  const statusColors = {
    live: 'bg-[--live] text-white',
    waking: 'bg-[--waking] text-white',
    offline: 'bg-[--down] text-white',
  };
  const statusLabels = { live: '● live', waking: '● waking…', offline: '● offline' };

  return (
    <span className={`px-3 py-1 rounded text-sm font-medium ${statusColors[status]}`}>
      {statusLabels[status]}
    </span>
  );
}