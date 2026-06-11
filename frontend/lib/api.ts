import * as types from './types';

const BASE = process.env.NEXT_PUBLIC_API_URL ?? 'https://openag-risk-twin.onrender.com';

class ApiError extends Error {
  constructor(
    message: string,
    public status?: number,
    public response?: Response,
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

async function fetchJson<T>(endpoint: string): Promise<T> {
  const url = `${BASE}${endpoint}`;
  const response = await fetch(url);

  if (!response.ok) {
    throw new ApiError(`Failed to fetch ${endpoint}`, response.status, response);
  }

  return response.json() as Promise<T>;
}

export const api = {
  health: () => fetchJson<types.HealthResponse>('/health'),
  forecast: () => fetchJson<types.ForecastResponse>('/forecast'),
  scenario: () => fetchJson<types.ScenarioResponse>('/scenario'),
  modelCard: () => fetchJson<types.ModelCardResponse>('/model-card'),
};

export { ApiError };
