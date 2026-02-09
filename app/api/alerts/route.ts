import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const page = parseInt(searchParams.get('page') || '1')
    const limit = parseInt(searchParams.get('limit') || '10')
    const severity = searchParams.get('severity') || 'ALL'
    const status = searchParams.get('status') || 'ALL'
    const search = searchParams.get('search') || ''

    // Mock alert data with correct field names matching Alert type
    const allAlerts = [
      {
        alert_id: 'ALT-001',
        timestamp: new Date(Date.now() - 2 * 60000).toISOString(),
        entity: 'User #42521',
        risk_score: 94,
        severity: 'HIGH',
        status: 'ACTIVE',
      },
      {
        alert_id: 'ALT-002',
        timestamp: new Date(Date.now() - 8 * 60000).toISOString(),
        entity: 'Account #8839',
        risk_score: 78,
        severity: 'MEDIUM',
        status: 'ACTIVE',
      },
      {
        alert_id: 'ALT-003',
        timestamp: new Date(Date.now() - 15 * 60000).toISOString(),
        entity: 'Transaction #4521',
        risk_score: 62,
        severity: 'MEDIUM',
        status: 'INVESTIGATING',
      },
      {
        alert_id: 'ALT-004',
        timestamp: new Date(Date.now() - 22 * 60000).toISOString(),
        entity: 'User #18754',
        risk_score: 45,
        severity: 'LOW',
        status: 'ACTIVE',
      },
      {
        alert_id: 'ALT-005',
        timestamp: new Date(Date.now() - 34 * 60000).toISOString(),
        entity: 'Account #5521',
        risk_score: 38,
        severity: 'LOW',
        status: 'RESOLVED',
      },
      {
        alert_id: 'ALT-006',
        timestamp: new Date(Date.now() - 45 * 60000).toISOString(),
        entity: 'Transaction #8234',
        risk_score: 88,
        severity: 'HIGH',
        status: 'ACTIVE',
      },
      {
        alert_id: 'ALT-007',
        timestamp: new Date(Date.now() - 60 * 60000).toISOString(),
        entity: 'User #55423',
        risk_score: 71,
        severity: 'MEDIUM',
        status: 'INVESTIGATING',
      },
      {
        alert_id: 'ALT-008',
        timestamp: new Date(Date.now() - 75 * 60000).toISOString(),
        entity: 'Account #9021',
        risk_score: 52,
        severity: 'MEDIUM',
        status: 'ACTIVE',
      },
      {
        alert_id: 'ALT-009',
        timestamp: new Date(Date.now() - 90 * 60000).toISOString(),
        entity: 'User #33421',
        risk_score: 96,
        severity: 'CRITICAL',
        status: 'ACTIVE',
      },
      {
        alert_id: 'ALT-010',
        timestamp: new Date(Date.now() - 120 * 60000).toISOString(),
        entity: 'Transaction #12345',
        risk_score: 85,
        severity: 'HIGH',
        status: 'FALSE_POSITIVE',
      },
    ]

    // Filter by severity
    let filtered = allAlerts
    if (severity !== 'ALL') {
      filtered = filtered.filter((a) => a.severity === severity.toUpperCase())
    }

    // Filter by status
    if (status !== 'ALL') {
      filtered = filtered.filter((a) => a.status === status.toUpperCase())
    }

    // Filter by search
    if (search) {
      filtered = filtered.filter(
        (a) =>
          a.alert_id.toLowerCase().includes(search.toLowerCase()) ||
          a.entity.toLowerCase().includes(search.toLowerCase())
      )
    }

    // Paginate
    const total = filtered.length
    const start = (page - 1) * limit
    const data = filtered.slice(start, start + limit)

    return NextResponse.json({
      data,
      pagination: {
        page,
        total_pages: Math.ceil(total / limit),
        total_records: total,
      },
    })
  } catch (error) {
    console.error('[API] Error fetching alerts:', error)
    return NextResponse.json(
      { error: 'Failed to fetch alerts' },
      { status: 500 }
    )
  }
}
