import { NextResponse } from 'next/server'

export async function GET() {
  try {
    const metrics = {
      data: {
        total_transactions: 2456789,
        active_alerts: 142,
        high_risk_alerts: 28,
        false_positive_rate: 2.3,
        trends: {
          alerts_change_pct: 8.2,
          false_positive_change_pct: -0.5,
        },
      },
    }

    return NextResponse.json(metrics)
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to fetch metrics' },
      { status: 500 }
    )
  }
}
