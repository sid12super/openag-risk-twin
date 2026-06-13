'use client';

import { useEffect, useState } from 'react';
import { api, ApiError } from '@/lib/api';
import { ForecastResponse, REGIME_DISPLAY_NAMES } from '@/lib/types';
import { Loading } from '@/components/Loading';
import { ErrorState } from '@/components/ErrorState';
import { MetricReadout } from '@/components/MetricReadout';
import { IntervalChart } from '@/components/IntervalChart';

export default function ForecastPage() {
  const [data, setData] = useState<ForecastResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const forecast = await api.forecast();
      setData(forecast);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(`Couldn't reach the API. Retry.`);
      } else {
        setError(`Failed to load forecast. Retry.`);
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

  return (
    <div className="space-y-8">
      <div>
        <p className="text-xs uppercase tracking-widest text-[--muted] mb-4">
          CORN ZC=F · {data.horizon_days}-DAY HORIZON
        </p>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-6">
          <MetricReadout label="Last price" value={data.last_price} decimals={2} />
          <MetricReadout label="Point" value={data.point} decimals={2} />
          <MetricReadout label="Band low" value={data.interval_80.low} decimals={2} />
          <MetricReadout label="Band high" value={data.interval_80.high} decimals={2} />
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <span className="text-xs uppercase tracking-widest text-[--muted]">Regime</span>
            <span className="font-mono text-sm font-medium text-[--ink] tabular-nums">
              {REGIME_DISPLAY_NAMES[data.regime.label]}
            </span>
          </div>
          <div className="w-24 h-4 bg-[--line] rounded overflow-hidden">
            <div
              className="h-full bg-[--band]"
              style={{ width: `${Math.min(data.regime.vol_pct * 100, 100)}%` }}
            ></div>
          </div>
          <span className="font-mono text-xs text-[--muted] tabular-nums">
            {data.regime.vol_pct.toFixed(1)}%
          </span>
        </div>
      </div>

      <IntervalChart
        history={data.history}
        interval80={data.interval_80}
        point={data.point}
        asOf={data.as_of}
        horizonDays={data.horizon_days}
      />
    </div>
  );
}
