'use client';

import { useEffect, useState } from 'react';
import { api, ApiError } from '@/lib/api';
import { ScenarioResponse, REGIME_DISPLAY_NAMES } from '@/lib/types';
import { Loading } from '@/components/Loading';
import { ErrorState } from '@/components/ErrorState';

export default function ScenarioPage() {
  const [data, setData] = useState<ScenarioResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [generating, setGenerating] = useState(false);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const scenario = await api.scenario();
      setData(scenario);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(`Couldn't reach the API. Retry.`);
      } else {
        setError(`Failed to load scenario. Retry.`);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = async () => {
    setGenerating(true);
    await fetchData();
    setGenerating(false);
  };

  useEffect(() => {
    fetchData();
  }, []);

  if (loading && !data) return <Loading />;
  if (error && !data) return <ErrorState message={error} onRetry={fetchData} />;
  if (!data) return <ErrorState message="No data available. Retry." onRetry={fetchData} />;

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <p className="text-xs uppercase tracking-widest text-[--muted]">
          SCENARIO · {REGIME_DISPLAY_NAMES[data.regime]}
        </p>
        <span className="text-xs uppercase tracking-widest bg-[--line] text-[--muted] px-3 py-1 rounded">
          {data.source}
        </span>
      </div>

      <div className="prose prose-sm max-w-2xl">
        <p className="text-base leading-relaxed text-[--ink]">{data.narrative}</p>
      </div>

      <button
        onClick={handleGenerate}
        disabled={generating}
        className="px-4 py-2 bg-[--accent] text-white rounded text-sm font-medium hover:opacity-90 disabled:opacity-60 transition-opacity"
      >
        {generating ? 'Generating…' : 'Generate scenario'}
      </button>
    </div>
  );
}
