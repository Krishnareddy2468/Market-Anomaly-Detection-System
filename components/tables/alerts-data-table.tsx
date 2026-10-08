'use client'

import { useMemo } from 'react'
import { useReactTable, getCoreRowModel, getPaginationRowModel, getFilteredRowModel, ColumnDef, flexRender } from '@tanstack/react-table'
import { Alert } from '@/lib/types'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Button } from '@/components/ui/button'
import { formatDate, formatRiskScore } from '@/lib/utils/formatters'
import { SeverityBadge, StatusBadge } from '@/components/badges/severity-badge'
import { ChevronLeft, ChevronRight } from 'lucide-react'

interface AlertsDataTableProps {
  data: Alert[]
  onRowClick?: (alert: Alert) => void
  isLoading?: boolean
}

export function AlertsDataTable({ data, onRowClick, isLoading }: AlertsDataTableProps) {
  const columns = useMemo<ColumnDef<Alert>[]>(
    () => [
      {
        accessorKey: 'alert_id',
        header: 'Alert ID',
        cell: ({ row }) => <span className="font-mono text-xs text-primary">{row.original.alert_id}</span>,
      },
      {
        accessorKey: 'timestamp',
        header: 'Timestamp',
        cell: ({ row }) => <span className="text-xs text-muted-foreground">{formatDate(row.original.timestamp)}</span>,
      },
      {
        accessorKey: 'entity',
        header: 'Entity',
        cell: ({ row }) => <span className="text-xs font-medium">{row.original.entity}</span>,
      },
      {
        accessorKey: 'risk_score',
        header: 'Risk Score',
        cell: ({ row }) => {
          const score = row.original.risk_score
          const color = score >= 90 ? 'text-red-500' : score >= 70 ? 'text-orange-500' : score >= 50 ? 'text-yellow-600' : 'text-emerald-500'
          return (
            <div className="flex items-center gap-2">
              <span className={`font-bold text-sm ${color}`}>{formatRiskScore(score)}</span>
              <div className="h-1.5 w-16 rounded-full bg-muted overflow-hidden">
                <div
                  className={`h-full rounded-full ${score >= 90 ? 'bg-red-500' : score >= 70 ? 'bg-orange-500' : score >= 50 ? 'bg-yellow-500' : 'bg-emerald-500'}`}
                  style={{ width: `${score}%` }}
                />
              </div>
            </div>
          )
        },
      },
      {
        accessorKey: 'severity',
        header: 'Severity',
        cell: ({ row }) => <SeverityBadge severity={row.original.severity} />,
      },
      {
        accessorKey: 'status',
        header: 'Status',
        cell: ({ row }) => <StatusBadge status={row.original.status} />,
      },
    ],
    [],
  )

  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    state: {
      pagination: {
        pageIndex: 0,
        pageSize: 10,
      },
    },
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <p className="text-sm text-muted-foreground">Loading alerts...</p>
      </div>
    )
  }

  if (data.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12">
        <p className="text-sm text-muted-foreground">No alerts found</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="rounded-lg border border-border overflow-hidden">
        <Table>
          <TableHeader>
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id} className="border-border hover:bg-transparent">
                {headerGroup.headers.map((header) => (
                  <TableHead key={header.id} className="bg-muted/50 text-[10px] font-semibold uppercase tracking-wider text-muted-foreground h-10">
                    {header.isPlaceholder ? null : flexRender(header.column.columnDef.header, header.getContext())}
                  </TableHead>
                ))}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {table.getRowModel().rows.map((row) => (
              <TableRow
                key={row.id}
                className="cursor-pointer hover:bg-muted/30 transition-colors border-border"
                onClick={() => onRowClick?.(row.original)}
              >
                {row.getVisibleCells().map((cell) => (
                  <TableCell key={cell.id} className="py-3">{flexRender(cell.column.columnDef.cell, cell.getContext())}</TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      <div className="flex items-center justify-between">
        <div className="text-xs text-muted-foreground">
          Page {table.getState().pagination.pageIndex + 1} of {table.getPageCount()}
        </div>
        <div className="flex gap-1.5">
          <Button
            variant="outline"
            size="sm"
            onClick={() => table.previousPage()}
            disabled={!table.getCanPreviousPage()}
            className="h-8 w-8 p-0"
          >
            <ChevronLeft className="h-3.5 w-3.5" />
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => table.nextPage()}
            disabled={!table.getCanNextPage()}
            className="h-8 w-8 p-0"
          >
            <ChevronRight className="h-3.5 w-3.5" />
          </Button>
        </div>
      </div>
    </div>
  )
}
