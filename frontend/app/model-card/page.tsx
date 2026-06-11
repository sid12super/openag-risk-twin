'use client';

import { useEffect, useState } from 'react';
import { api, ApiError } from '@/lib/api';
import { ModelCardResponse } from '@/lib/types';
import { Loading } from '@/components/Loading';
import { ErrorState } from '@/components/ErrorState';
import { MetricReadout } from '@/components/MetricReadout';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export default function ModelCardPage() {
  const [data, setData] = useState<ModelCardResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const modelCard = await api.modelCard();
      setData(modelCard);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(`Couldn't reach the API. Retry.`);
      } else {
        setError(`Failed to load model card. Retry.`);
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  if (loading) return <Loading />;
  if (error) return <ErrorState message={error} onRetry={fetchData} />;
  if (!data) return <ErrorState message="No data available. Retry." onRetry={fetchData} />;

  const chartData = Object.entries(data.evaluation.per_year_rmse).map(([year, rmse]) => ({
    year,
    rmse,
  }));

  return (
    <div className="space-y-8">
      <div>
        <p className="text-xs uppercase tracking-widest text-[--muted] mb-6">
          {data.model} · {data.target}
        </p>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-6 mb-8">
          <MetricReadout label="RMSE" value={data.evaluation.rmse} decimals={3} />
          <MetricReadout label="Skill vs RW" value={data.evaluation.skill_vs_rw} decimals={2} />
          <div className="col-span-1">
            <span className="font-mono text-base font-medium text-[--ink] tabular-nums">
              {data.evaluation.oos_period}
            </span>
            <span className="text-xs text-[--muted] uppercase tracking-wide block">Period</span>
          </div>
        </div>
      </div>

      <div className="space-y-4">
        <p className="text-xs uppercase tracking-widest text-[--muted]">Yearly RMSE</p>
        <div className="w-full h-48 bg-[--surface] rounded border border-[--line] p-4">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData}>
              <CartesianGrid
                strokeDasharray="3 3"
                vertical={false}
                stroke="var(--line)"
                opacity={0.5}
              />
              <XAxis
                dataKey="year"
                stroke="var(--muted)"
                tick={{ fontSize: 12, fontFamily: 'var(--font-mono)', fill: 'var(--muted)' }}
                axisLine={{ stroke: 'var(--line)' }}
                tickLine={false}
              />
              <YAxis
                stroke="var(--muted)"
                tick={{ fontSize: 12, fontFamily: 'var(--font-mono)', fill: 'var(--muted)' }}
                axisLine={{ stroke: 'var(--line)' }}
                tickLine={false}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'var(--surface)',
                  border: '1px solid var(--line)',
                  borderRadius: '4px',
                }}
                cursor={{ fill: 'rgba(92, 107, 60, 0.05)' }}
              />
              <Bar dataKey="rmse" fill="var(--accent)" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="space-y-4">
        <p className="text-xs uppercase tracking-widest text-[--muted]">Features</p>
        <div className="flex flex-wrap gap-2">
          {data.features.map((feature) => (
            <span
              key={feature}
              className="px-3 py-1 bg-[--line] text-[--ink] rounded text-sm font-mono"
            >
              {feature}
            </span>
          ))}
        </div>
      </div>

      <div className="space-y-4 py-8 border-t border-[--line]">
        <p className="text-xs uppercase tracking-widest text-[--muted]">Framing</p>
        <div className="pl-4 border-l-4 border-[--accent] max-w-2xl">
          <p className="text-base leading-relaxed text-[--ink]">{data.framing}</p>
        </div>
      </div>

      <div className="space-y-2 text-xs text-[--muted]">
        <p className="uppercase tracking-widest">Data sources</p>
        <ul className="list-disc list-inside space-y-1">
          {data.data_sources.map((source) => (
            <li key={source}>{source}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}
