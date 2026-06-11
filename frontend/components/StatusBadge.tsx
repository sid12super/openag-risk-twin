'use client';

import { useEffect, useState } from 'react';
import { api, ApiError } from '@/lib/api';

export function StatusBadge() {
  const [status, setStatus] = useState<'live' | 'waking' | 'offline'>('waking');

  useEffect(() => {
    let isMounted = true;
    let startTime: number;
    let timeoutId: NodeJS.Timeout;

    const checkHealth = async () => {
      startTime = Date.now();
      try {
        await api.health();
        if (isMounted) setStatus('live');
      } catch (error) {
        if (isMounted) {
          if (error instanceof ApiError) {
            setStatus('offline');
          }
        }
      }
    };

    const showWaking = () => {
      timeoutId = setTimeout(() => {
        if (isMounted && status === 'waking') {
          setStatus('waking');
        }
      }, 3000);
    };

    checkHealth();
    showWaking();

    return () => {
      isMounted = false;
      clearTimeout(timeoutId);
    };
  }, []);

  const statusColors = {
    live: 'bg-[--live] text-white',
    waking: 'bg-[--waking] text-white',
    offline: 'bg-[--down] text-white',
  };

  const statusLabels = {
    live: '● live',
    waking: '● waking…',
    offline: '● offline',
  };

  return (
    <span className={`px-3 py-1 rounded text-sm font-medium ${statusColors[status]}`}>
      {statusLabels[status]}
    </span>
  );
}
