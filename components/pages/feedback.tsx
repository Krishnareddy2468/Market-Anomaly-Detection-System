'use client'

import { useFeedbackHistory } from '@/lib/hooks/useAnalytics'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { PageContainer } from '@/components/layout/page-container'
import { formatDate } from '@/lib/utils/formatters'

export function FeedbackPage() {
  const { data, isLoading } = useFeedbackHistory(1, 20)
  const feedbackData = data?.data || []
  const summary = data?.summary
  const safeDate = (value?: string) => {
    if (!value || !value.trim()) return '-'
    try {
      return formatDate(value)
    } catch {
      return '-'
    }
  }

  return (
    <PageContainer>
      <div className="space-y-6">
      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="bg-card border-border">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm text-muted-foreground font-medium">Total Resolutions</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold text-primary">{summary?.total_resolutions ?? 0}</p>
          </CardContent>
        </Card>
        <Card className="bg-card border-border">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm text-muted-foreground font-medium">Confirmed Fraud</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold text-accent">{summary?.confirmed_frauds ?? 0}</p>
          </CardContent>
        </Card>
        <Card className="bg-card border-border">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm text-muted-foreground font-medium">False Positives</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold text-green-600">{summary?.false_positives ?? 0}</p>
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
                {isLoading && (
                  <TableRow className="border-border">
                    <TableCell colSpan={6} className="text-center text-muted-foreground">
                      Loading feedback...
                    </TableCell>
                  </TableRow>
                )}
                {feedbackData.map((feedback, index) => (
                  <TableRow
                    key={feedback.feedback_id || `${feedback.alert_id || 'unknown'}-${feedback.resolved_at || 'na'}-${index}`}
                    className="border-border hover:bg-secondary/30"
                  >
                    <TableCell className="font-mono text-sm text-foreground">{feedback.feedback_id || '-'}</TableCell>
                    <TableCell className="font-mono text-sm text-foreground">{feedback.alert_id}</TableCell>
                    <TableCell>
                      <span
                        className={`px-2 py-1 rounded-full text-xs font-semibold ${
                          feedback.decision === 'FRAUD'
                            ? 'bg-accent/20 text-accent'
                            : 'bg-green-100 text-green-700'
                        }`}
                      >
                        {(feedback.decision || 'UNKNOWN').replace('_', ' ')}
                      </span>
                    </TableCell>
                    <TableCell className="text-sm text-foreground max-w-xs truncate">{feedback.notes || '-'}</TableCell>
                    <TableCell className="text-sm text-foreground">{feedback.analyst}</TableCell>
                    <TableCell className="text-sm text-muted-foreground">{safeDate(feedback.resolved_at)}</TableCell>
                  </TableRow>
                ))}
                {!isLoading && feedbackData.length === 0 && (
                  <TableRow className="border-border">
                    <TableCell colSpan={6} className="text-center text-muted-foreground">
                      No feedback records found.
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
      </div>
    </PageContainer>
  )
}
