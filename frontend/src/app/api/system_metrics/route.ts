import { NextResponse } from 'next/server';
import {promises as fs} from 'fs';
import path from 'path';


// Define the exact shape of incoming data expected from Python
export interface SystemMetrics {
    report_date: string;
    total_active_users: number;
    total_revenue_usd: number;
    anomaly_detected: boolean;
}


export async function GET() {
  try {

    // Resolve absolute path mapping within the container framework
    const cachePath = path.join(process.cwd(),'public', 'auto_latest_report.json');
    

    // for local development
    //const cachePath = path.join(process.cwd(), '../backend/cache/auto_latest_report.json');
    
    let report = {  "report_date": "2020-01-01",
                    "total_active_users": 0,
                    "total_revenue_usd": 0,
                    "anomaly_detected": false
                  };

    // Graceful fallback safeguard if the shared folder is not yet initialized
   
    const rawData = await fs.readFile(cachePath, 'utf-8');
    report = JSON.parse(rawData);
    
    const mockTelemetry = {
      status: report.anomaly_detected ? "unhealthy" : "healthy",
      database: "connected",
      db_latency_ms: 1.84,
      system_metrics: {
        cpu_usage_percent: 12.4,
        memory_usage_percent: 45.2,
        memory_used_gb: 3.61
      }
    };

    return NextResponse.json(report);
  } catch (error) {
    return NextResponse.json(
      { error: 'Automated telemetry error', details: String(error) }, 
      { status: 500 }
    );
  }
}
