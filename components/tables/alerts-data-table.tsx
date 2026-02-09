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
        cell: ({ row }) => <span className="font-mono text-sm">{row.original.alert_id}</span>,
      },
      {
        accessorKey: 'timestamp',
        header: 'Timestamp',
        cell: ({ row }) => <span className="text-sm">{formatDate(row.original.timestamp)}</span>,
      },
      {
        accessorKey: 'entity',
        header: 'Entity',
        cell: ({ row }) => <span className="text-sm">{row.original.entity}</span>,
      },
      {
        accessorKey: 'risk_score',
        header: 'Risk Score',
        cell: ({ row }) => <span className="font-semibold">{formatRiskScore(row.original.risk_score)}</span>,
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
      <div className="rounded-md border border-border">
        <Table>
          <TableHeader>
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <TableHead key={header.id} className="bg-secondary/50">
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
                className="cursor-pointer hover:bg-secondary/50 transition-colors"
                onClick={() => onRowClick?.(row.original)}
              >
                {row.getVisibleCells().map((cell) => (
                  <TableCell key={cell.id}>{flexRender(cell.column.columnDef.cell, cell.getContext())}</TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      <div className="flex items-center justify-between">
        <div className="text-sm text-muted-foreground">
          Page {table.getState().pagination.pageIndex + 1} of {table.getPageCount()}
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => table.previousPage()}
            disabled={!table.getCanPreviousPage()}
          >
            <ChevronLeft className="h-4 w-4" />
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => table.nextPage()}
            disabled={!table.getCanNextPage()}
          >
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  )
}
