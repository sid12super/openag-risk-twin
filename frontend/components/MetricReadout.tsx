'use client';

interface MetricReadoutProps {
  label: string;
  value: number;
  decimals?: number;
}

export function MetricReadout({ label, value, decimals = 2 }: MetricReadoutProps) {
  const formatted = value.toFixed(decimals);

  return (
    <div className="flex flex-col gap-1">
      <span className="font-mono text-base font-medium text-[--ink] tabular-nums">{formatted}</span>
      <span className="text-xs text-[--muted] uppercase tracking-wide">{label}</span>
    </div>
  );
}
