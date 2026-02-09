import { NextResponse } from 'next/server'

export async function GET() {
  try {
    const trend = {
      data: {
        timestamps: [
          '00:00', '02:00', '04:00', '06:00', '08:00', '10:00',
          '12:00', '14:00', '16:00', '18:00', '20:00', '22:00'
        ],
        values: [24, 32, 28, 35, 42, 55, 68, 72, 85, 78, 65, 48],
      },
    }

    return NextResponse.json(trend)
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to fetch trend' },
      { status: 500 }
    )
  }
}
