'use client';

import {
  ComposedChart,
  Line,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { HistoryPoint, Interval80 } from '@/lib/types';

interface IntervalChartProps {
  history: HistoryPoint[];
  interval80: Interval80;
  point: number;
  asOf: string;
  horizonDays: number;
}

export function IntervalChart({
  history,
  interval80,
  point,
  asOf,
  horizonDays,
}: IntervalChartProps) {
  // Parse asOf and calculate forecast date
  const asOfDate = new Date(asOf);
  const forecastDate = new Date(asOfDate);
  forecastDate.setDate(forecastDate.getDate() + horizonDays);
  const forecastDateStr = forecastDate.toISOString().split('T')[0];

  // Prepare chart data: history + forecast point
  const chartData = [
    ...history.map((h) => ({
      date: h.date,
      close: h.close,
      low: null as number | null,
      high: null as number | null,
      forecast: null as number | null,
    })),
    {
      date: forecastDateStr,
      close: null as number | null,
      low: interval80.low,
      high: interval80.high,
      forecast: point,
    },
  ];

  const CustomTooltip = ({ active, payload }: any) => {
    if (!active || !payload) return null;
    const data = payload[0].payload;
    return (
      <div className="bg-[--surface] border border-[--line] rounded px-3 py-2 shadow-sm">
        <p className="text-xs text-[--muted] font-mono">{data.date}</p>
        {data.close !== null && (
          <p className="text-sm font-mono text-[--ink] tabular-nums">{data.close.toFixed(2)}</p>
        )}
        {data.forecast !== null && (
          <p className="text-sm font-mono text-[--accent] tabular-nums">
            forecast: {data.forecast.toFixed(2)}
          </p>
        )}
      </div>
    );
  };

  return (
    <div className="w-full h-80 bg-[--surface] rounded border border-[--line] p-4">
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart data={chartData}>
          <defs>
            <linearGradient id="bandFill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="rgb(201, 138, 43)" stopOpacity={0.16} />
              <stop offset="100%" stopColor="rgb(201, 138, 43)" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid
            strokeDasharray="3 3"
            vertical={false}
            stroke="var(--line)"
            opacity={0.5}
          />
          <XAxis
            dataKey="date"
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
          <Tooltip content={<CustomTooltip />} />
          <Area
            type="monotone"
            dataKey="low"
            fill="url(#bandFill)"
            stroke="none"
            isAnimationActive={false}
          />
          <Area
            type="monotone"
            dataKey="high"
            fill="none"
            stroke="none"
            isAnimationActive={false}
          />
          <Line
            type="monotone"
            dataKey="close"
            stroke="var(--ink)"
            dot={false}
            strokeWidth={2}
            isAnimationActive={false}
            name="history"
          />
          <Line
            type="stepAfter"
            dataKey="forecast"
            stroke="var(--accent)"
            dot={{ fill: 'var(--accent)', r: 4 }}
            strokeWidth={2}
            isAnimationActive={false}
            name="forecast"
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}
