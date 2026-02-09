import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Button } from '@/components/ui/button'
import { Eye } from 'lucide-react'

interface Alert {
  id: string
  timestamp: string
  entity: string
  risk: number
  severity: 'high' | 'medium' | 'low'
  status: string
}

interface AlertsTableProps {
  alerts: Alert[]
}

const severityColors = {
  high: 'bg-accent/20 text-accent',
  medium: 'bg-yellow-100 text-yellow-700',
  low: 'bg-green-100 text-green-700',
}

export function AlertsTable({ alerts }: AlertsTableProps) {
  return (
    <div className="overflow-x-auto">
      <Table>
        <TableHeader>
          <TableRow className="border-border">
            <TableHead className="text-primary font-semibold">Alert ID</TableHead>
            <TableHead className="text-primary font-semibold">Timestamp</TableHead>
            <TableHead className="text-primary font-semibold">Entity</TableHead>
            <TableHead className="text-primary font-semibold">Risk Score</TableHead>
            <TableHead className="text-primary font-semibold">Severity</TableHead>
            <TableHead className="text-primary font-semibold">Status</TableHead>
            <TableHead className="text-primary font-semibold">Action</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {alerts.map((alert) => (
            <TableRow key={alert.id} className="border-border hover:bg-secondary/30">
              <TableCell className="font-mono text-sm text-foreground">{alert.id}</TableCell>
              <TableCell className="text-sm text-muted-foreground">{alert.timestamp}</TableCell>
              <TableCell className="text-sm text-foreground">{alert.entity}</TableCell>
              <TableCell>
                <div className="flex items-center gap-2">
                  <div className="flex-1 bg-secondary rounded-full h-2 max-w-[100px]">
                    <div
                      className="h-full bg-accent rounded-full"
                      style={{ width: `${alert.risk}%` }}
                    />
                  </div>
                  <span className="text-sm font-semibold text-foreground w-8">{alert.risk}</span>
                </div>
              </TableCell>
              <TableCell>
                <span
                  className={`px-2.5 py-1.5 rounded-full text-xs font-semibold ${
                    severityColors[alert.severity]
                  }`}
                >
                  {alert.severity.charAt(0).toUpperCase() + alert.severity.slice(1)}
                </span>
              </TableCell>
              <TableCell className="text-sm text-foreground">{alert.status}</TableCell>
              <TableCell>
                <Button variant="ghost" size="sm" className="text-accent hover:bg-accent/10">
                  <Eye size={16} className="mr-1" />
                  View
                </Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  )
}
