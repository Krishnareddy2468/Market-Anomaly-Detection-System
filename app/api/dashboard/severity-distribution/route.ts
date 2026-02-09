import { NextResponse } from 'next/server'

export async function GET() {
  try {
    const distribution = {
      data: [
        { name: 'Critical', value: 15, color: 'hsl(0, 84%, 50%)' },
        { name: 'High', value: 35, color: 'hsl(0, 84%, 60%)' },
        { name: 'Medium', value: 45, color: 'hsl(54, 92%, 50%)' },
        { name: 'Low', value: 25, color: 'hsl(120, 73%, 55%)' },
      ],
    }

    return NextResponse.json(distribution)
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to fetch severity distribution' },
      { status: 500 }
    )
  }
}
