'use client';

import {
  ComposedChart, Line, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts';
import { HistoryPoint, Interval80 } from '@/lib/types';

interface IntervalChartProps {
  history: HistoryPoint[];
  interval80: Interval80;
  point: number;
  asOf: string;
  horizonDays: number;
}

export function IntervalChart({ history, interval80, point, asOf, horizonDays }: IntervalChartProps) {
  const asOfDate = new Date(asOf);
  const forecastDate = new Date(asOfDate);
  forecastDate.setDate(forecastDate.getDate() + horizonDays);
  const forecastDateStr = forecastDate.toISOString().split('T')[0];

  const lastIdx = history.length - 1;
  const lastClose = history[lastIdx]?.close ?? point;

  // Cone: band pinched at the last actual, widening to [low, high] at the horizon.
  const chartData = [
    ...history.map((h, i) => ({
      date: h.date,
      close: h.close,
      band: i === lastIdx ? [lastClose, lastClose] : (null as null | number[]),
      forecast: i === lastIdx ? lastClose : (null as null | number),
    })),
    {
      date: forecastDateStr,
      close: null as null | number,
      band: [interval80.low, interval80.high] as number[],
      forecast: point as null | number,
    },
  ];

  const CustomTooltip = ({ active, payload }: any) => {
    if (!active || !payload || !payload.length) return null;
    const d = payload[0].payload;
    return (
      <div className="bg-[--surface] border border-[--line] rounded px-3 py-2 shadow-sm">
        <p className="text-xs text-[--muted] font-mono">{d.date}</p>
        {d.close != null && (
          <p className="text-sm font-mono text-[--ink] tabular-nums">{d.close.toFixed(2)}</p>
        )}
        {d.forecast != null && d.close == null && (
          <p className="text-sm font-mono text-[--accent] tabular-nums">
            forecast {d.forecast.toFixed(2)} · band {interval80.low.toFixed(2)}–{interval80.high.toFixed(2)}
          </p>
        )}
      </div>
    );
  };

  return (
    <div className="w-full h-80 bg-[--surface] rounded border border-[--line] p-4">
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--line)" opacity={0.5} />
          <XAxis dataKey="date" stroke="var(--muted)" minTickGap={40}
            tick={{ fontSize: 12, fontFamily: 'var(--font-mono)', fill: 'var(--muted)' }}
            axisLine={{ stroke: 'var(--line)' }} tickLine={false} />
          <YAxis stroke="var(--muted)" domain={['dataMin - 30', 'dataMax + 30']} width={48}
            tick={{ fontSize: 12, fontFamily: 'var(--font-mono)', fill: 'var(--muted)' }}
            axisLine={{ stroke: 'var(--line)' }} tickLine={false} />
          <Tooltip content={<CustomTooltip />} />
          <Area type="monotone" dataKey="band" fill="rgba(201, 138, 43, 0.18)" stroke="none"
            connectNulls isAnimationActive={false} />
          <Line type="monotone" dataKey="close" stroke="var(--ink)" dot={false}
            strokeWidth={2} connectNulls isAnimationActive={false} />
          <Line type="linear" dataKey="forecast" stroke="var(--accent)" strokeDasharray="4 3"
            dot={{ fill: 'var(--accent)', r: 4 }} strokeWidth={2} connectNulls isAnimationActive={false} />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}