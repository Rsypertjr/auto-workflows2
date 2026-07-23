// frontend/src/app/dashboard/page.tsx 
'use client';

import {useEffect, useState } from 'react';
import type { SystemMetrics } from '../api/system_metrics/route.ts';

export default function AutomatedDashboard() {
    const [metrics, setMetrics] = useState<SystemMetrics | null>(null);
    const [loading, setLoading] = useState<boolean>(true);

    useEffect(() => {
        fetch('http://localhost:3000/api/system_metrics')
            //.then((res) => res.json())
            .then((res) => {
                if (!res.ok) throw new Error('Systems are currently unreachable.');
                return res.json();
            })
            .then((data: SystemMetrics) => {
                setMetrics(data);
                setLoading(false);
            })
            .catch(() => setLoading(false));
    }, []);


    if (loading) return <p className="p-8">Loadig automated report feed...</p>;
    if (!metrics) return <p className="p-8 text-red-500">Failed to render automated stream.</p>


    return (
        <main className="p-8 max-w-4xl mx-auto space-y-6">
            <header className="border-b pb-4">
                <h1 className="text-2xl font-bold text-gray-900">System Activity Report</h1>
                <p className="text-sm text-gray-500">Last auto-generated: {metrics.report_date}</p>
            </header>

            <section className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Card 1 */}
                <div className="p-6 bg-white shadow rounded-lg border">
                    <h2 className="text-sm font-medium text-gray-500 uppercase">Active Platform Accounts</h2>
                    <p className="mt-2 text-3xl font-semibold text-indigo-600">{metrics.total_active_users}</p>
                </div>

                {/* Card 2 */}
                <div className="p-6 bg-white shadow rounded-lg border">
                    <h2 className="text-sm font-medium text-gray-500 uppercase">Validatede Monthly Revenue</h2>
                    <p className="mt-2 text-3xl font-semibold text-emerald-600">
                        ${metrics.total_revenue_usd}
                    </p>
                </div>

                {metrics.anomaly_detected && (
                    <div className="p-4 bg-amber-50 text-amber-800 rounded border border-amber-20 text-sm">
                        <strong>System Alert:</strong> Unexpected variance flagged.  Our automated triage pipeline has opened a review ticket.
                    </div>
                )}
            </section>


        </main>
    )


}