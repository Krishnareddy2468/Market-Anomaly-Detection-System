import { NextResponse } from 'next/server'

export async function GET() {
  try {
    const trends = {
      success: true,
      data: [
        { date: 'Jan 1', alerts: 120, resolved: 100, false_positives: 20 },
        { date: 'Jan 2', alerts: 135, resolved: 115, false_positives: 20 },
        { date: 'Jan 3', alerts: 128, resolved: 110, false_positives: 18 },
        { date: 'Jan 4', alerts: 145, resolved: 130, false_positives: 15 },
        { date: 'Jan 5', alerts: 142, resolved: 128, false_positives: 14 },
        { date: 'Jan 6', alerts: 155, resolved: 142, false_positives: 13 },
        { date: 'Jan 7', alerts: 168, resolved: 155, false_positives: 13 },
      ],
    }

    return NextResponse.json(trends)
  } catch (error) {
    return NextResponse.json(
      { success: false, error: 'Failed to fetch trends' },
      { status: 500 }
    )
  }
}
