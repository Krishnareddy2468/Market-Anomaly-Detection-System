'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'

const feedbackData = [
  {
    id: 'FBK-001',
    alertId: 'ALT-042',
    decision: 'Fraud',
    analystNotes: 'Unusual location, confirmed with customer',
    timestamp: '2024-02-09 15:32',
    analyst: 'John Smith',
  },
  {
    id: 'FBK-002',
    alertId: 'ALT-038',
    decision: 'False Positive',
    analystNotes: 'Customer travel, known pattern',
    timestamp: '2024-02-09 14:18',
    analyst: 'Sarah Johnson',
  },
  {
    id: 'FBK-003',
    alertId: 'ALT-035',
    decision: 'Fraud',
    analystNotes: 'Multiple red flags, device fingerprint mismatch',
    timestamp: '2024-02-09 13:45',
    analyst: 'Michael Chen',
  },
  {
    id: 'FBK-004',
    alertId: 'ALT-029',
    decision: 'False Positive',
    analystNotes: 'Legitimate high-value transaction for business account',
    timestamp: '2024-02-09 12:22',
    analyst: 'Emma Davis',
  },
  {
    id: 'FBK-005',
    alertId: 'ALT-024',
    decision: 'Fraud',
    analystNotes: 'Matched against known fraud patterns, blocking account',
    timestamp: '2024-02-09 11:08',
    analyst: 'John Smith',
  },
  {
    id: 'FBK-006',
    alertId: 'ALT-019',
    decision: 'False Positive',
    analystNotes: 'API integration test, whitelisted',
    timestamp: '2024-02-09 10:15',
    analyst: 'Robert Wilson',
  },
  {
    id: 'FBK-007',
    alertId: 'ALT-012',
    decision: 'Fraud',
    analystNotes: 'Account takeover attempt, password reset initiated',
    timestamp: '2024-02-09 09:42',
    analyst: 'Sarah Johnson',
  },
  {
    id: 'FBK-008',
    alertId: 'ALT-008',
    decision: 'False Positive',
    analystNotes: 'Bulk purchase by authorized distributor',
    timestamp: '2024-02-09 08:30',
    analyst: 'Michael Chen',
  },
]

export function FeedbackPage() {
  const fraudCount = feedbackData.filter((f) => f.decision === 'Fraud').length
  const fpCount = feedbackData.filter((f) => f.decision === 'False Positive').length

  return (
    <div className="p-6 space-y-6 ml-20 md:ml-64">
      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="bg-card border-border">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm text-muted-foreground font-medium">Total Resolutions</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold text-primary">{feedbackData.length}</p>
          </CardContent>
        </Card>
        <Card className="bg-card border-border">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm text-muted-foreground font-medium">Confirmed Fraud</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold text-accent">{fraudCount}</p>
          </CardContent>
        </Card>
        <Card className="bg-card border-border">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm text-muted-foreground font-medium">False Positives</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold text-green-600">{fpCount}</p>
          </CardContent>
        </Card>
      </div>

      {/* Feedback Table */}
      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle className="text-primary">Resolved Alerts</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow className="border-border">
                  <TableHead className="text-primary font-semibold">Feedback ID</TableHead>
                  <TableHead className="text-primary font-semibold">Alert ID</TableHead>
                  <TableHead className="text-primary font-semibold">Decision</TableHead>
                  <TableHead className="text-primary font-semibold">Analyst Notes</TableHead>
                  <TableHead className="text-primary font-semibold">Analyst</TableHead>
                  <TableHead className="text-primary font-semibold">Timestamp</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {feedbackData.map((feedback) => (
                  <TableRow key={feedback.id} className="border-border hover:bg-secondary/30">
                    <TableCell className="font-mono text-sm text-foreground">{feedback.id}</TableCell>
                    <TableCell className="font-mono text-sm text-foreground">{feedback.alertId}</TableCell>
                    <TableCell>
                      <span
                        className={`px-2 py-1 rounded-full text-xs font-semibold ${
                          feedback.decision === 'Fraud'
                            ? 'bg-accent/20 text-accent'
                            : 'bg-green-100 text-green-700'
                        }`}
                      >
                        {feedback.decision}
                      </span>
                    </TableCell>
                    <TableCell className="text-sm text-foreground max-w-xs truncate">{feedback.analystNotes}</TableCell>
                    <TableCell className="text-sm text-foreground">{feedback.analyst}</TableCell>
                    <TableCell className="text-sm text-muted-foreground">{feedback.timestamp}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
