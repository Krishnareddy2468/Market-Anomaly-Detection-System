import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const page = parseInt(searchParams.get('page') || '1')
    const limit = parseInt(searchParams.get('limit') || '10')

    const feedback = {
      success: true,
      data: [
        {
          id: 'FB-001',
          alert_id: 'ALT-001',
          decision: 'CONFIRMED_FRAUD',
          confidence: 0.95,
          notes: 'Unusual transaction pattern confirmed. User verified suspicious activity.',
          analyst: 'John Analyst',
          created_at: new Date(Date.now() - 60 * 60000).toISOString(),
        },
        {
          id: 'FB-002',
          alert_id: 'ALT-005',
          decision: 'FALSE_POSITIVE',
          confidence: 0.82,
          notes: 'Session expired naturally. No fraud detected.',
          analyst: 'Sarah Review',
          created_at: new Date(Date.now() - 120 * 60000).toISOString(),
        },
        {
          id: 'FB-003',
          alert_id: 'ALT-003',
          decision: 'CONFIRMED_FRAUD',
          confidence: 0.88,
          notes: 'Large transfer verified as unauthorized.',
          analyst: 'Mike Analyst',
          created_at: new Date(Date.now() - 180 * 60000).toISOString(),
        },
      ],
      pagination: {
        page,
        limit,
        total_records: 3,
        total_pages: 1,
      },
    }

    return NextResponse.json(feedback)
  } catch (error) {
    return NextResponse.json(
      { success: false, error: 'Failed to fetch feedback' },
      { status: 500 }
    )
  }
}
