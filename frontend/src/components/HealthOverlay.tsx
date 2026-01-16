import { useEffect, useState } from "react";

interface CacheStats {
  entries: number;
  hits: number;
  misses: number;
  hit_rate: number;
}

interface HealthPayload {
  status: string;
  cache?: CacheStats;
}

const POLL_INTERVAL = 8000;

export function HealthOverlay() {
  const [cache, setCache] = useState<CacheStats | null>(null);

  useEffect(() => {
    let active = true;
    const fetchHealth = async () => {
      try {
        const response = await fetch(`${import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000"}/health`);
        if (!response.ok) return;
        const payload = (await response.json()) as HealthPayload;
        if (active && payload.cache) {
          setCache(payload.cache);
        }
      } catch {
        if (active) {
          setCache(null);
        }
      }
    };
    fetchHealth();
    const timer = window.setInterval(fetchHealth, POLL_INTERVAL);
    return () => {
      active = false;
      window.clearInterval(timer);
    };
  }, []);

  if (!cache) {
    return null;
  }

  return (
    <div className="health-overlay" role="status">
      <span>Cache: {cache.entries} entries</span>
      <span>Hit Rate: {(cache.hit_rate * 100).toFixed(1)}%</span>
      <span>Hits: {cache.hits}</span>
      <span>Misses: {cache.misses}</span>
    </div>
  );
}
