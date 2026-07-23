'use client';

import { useEffect, useState } from 'react';

// Define the exact TypeScript interface matching the backend /health schema
interface SystemMetrics {
  cpu_usage_percent: number;
  memory_usage_percent: number;
  memory_used_gb: number;
}

interface HealthStatus {
  status: string;
  database: string;
  db_latency_ms: number;
  system_metrics: SystemMetrics;
}

export default function Home() {
  const [data, setData] = useState<HealthStatus | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Fetches live health analytics from the Next.js automated API route
    fetch('http://localhost:3000/api/metrics')
      .then((res) => {
        if (!res.ok) throw new Error('Systems are currently unreachable.');
        return res.json();
      })
      .then((payload: HealthStatus) => {
        setData(payload);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  return (
    <main className="min-h-screen bg-gray-50 p-8 font-sans">
      <div className="max-w-5xl mx-auto space-y-8">
        
        {/* Header - Required by your automated UI tests */}
        <header className="border-b border-gray-200 pb-5">
          <h1 className="text-3xl font-bold tracking-tight text-gray-900">
            Production Dashboard
          </h1>
          <p className="text-sm text-gray-500 mt-1">
            Automated Stack Infrastructure Analytics
          </p>
        </header>

        {/* Loading and Error States */}
        {loading && (
          <div className="p-6 bg-white rounded-lg shadow-sm border border-gray-200 animate-pulse text-gray-600">
            Fetching real-time infrastructure data stream...
          </div>
        )}

        {error && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-md text-sm text-red-800">
            <span className="font-semibold">System Outage Warning:</span> {error}
          </div>
        )}

        {/* Live Metrics Grid */}
        {data && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              
              {/* Database Connection Card */}
              <div className="p-6 bg-white rounded-xl shadow-sm border border-gray-200">
                <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-wider">
                  Database Link
                </h2>
                <div className="mt-3 flex items-baseline gap-2">
                  <span className={`text-2xl font-bold ${data.database === 'connected' ? 'text-emerald-600' : 'text-rose-600'}`}>
                    {data.database.toUpperCase()}
                  </span>
                </div>
                <p className="text-xs text-gray-500 mt-2">
                  Network Latency: <span className="font-medium text-gray-700">{data.db_latency_ms} ms</span>
                </p>
              </div>

              {/* CPU Cluster Card */}
              <div className="p-6 bg-white rounded-xl shadow-sm border border-gray-200">
                <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-wider">
                  Compute Cluster Load
                </h2>
                <div className="mt-3">
                  <span className="text-4xl font-bold text-gray-900 tracking-tight">
                    {data.system_metrics.cpu_usage_percent}%
                  </span>
                </div>
                <div className="w-full bg-gray-100 h-2 rounded-full mt-3 overflow-hidden">
                  <div 
                    className="bg-indigo-600 h-2 rounded-full transition-all duration-500" 
                    style={{ width: `${data.system_metrics.cpu_usage_percent}%` }}
                  />
                </div>
              </div>

              {/* Memory Card */}
              <div className="p-6 bg-white rounded-xl shadow-sm border border-gray-200">
                <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-wider">
                  Memory Utilization
                </h2>
                <div className="mt-3">
                  <span className="text-4xl font-bold text-gray-900 tracking-tight">
                    {data.system_metrics.memory_usage_percent}%
                  </span>
                </div>
                <p className="text-xs text-gray-500 mt-2">
                  Capacity Consumed: <span className="font-medium text-gray-700">{data.system_metrics.memory_used_gb} GB</span>
                </p>
              </div>

            </div>

            {/* Global Infrastructure Status Banner */}
            <div className={`p-4 rounded-lg border text-sm flex items-center justify-between ${
              data.status === 'healthy' 
                ? 'bg-emerald-50 border-emerald-200 text-emerald-800' 
                : 'bg-amber-50 border-amber-200 text-amber-800'
            }`}>
              <div>
                System Node Operational Status: <span className="font-bold uppercase">{data.status}</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className={`h-2.5 w-2.5 rounded-full ${data.status === 'healthy' ? 'bg-emerald-500' : 'bg-amber-500'}`} />
                <span className="text-xs font-medium">Live Feed Enabled</span>
              </div>
            </div>
          </div>
        )}

      </div>
    </main>
  );
}
