# Fraud Detection Platform - Architecture Guide

## Overview
This document outlines the professional, maintainable architecture for the Fraud Detection Platform frontend, following enterprise-grade best practices.

## Project Structure

```
lib/
├── hooks/                 # React Query custom hooks
│   ├── useAlerts.ts      # Alert data and mutations
│   ├── useDashboard.ts   # Dashboard metrics and trends
│   └── useAnalytics.ts   # Analytics and feedback data
├── services/             # API layer with business logic
│   ├── api-client.ts     # HTTP client with error handling
│   ├── alerts.service.ts # Alert operations
│   ├── dashboard.service.ts
│   └── analytics.service.ts
├── types/                # TypeScript interfaces
│   ├── alert.ts          # Alert domain types
│   ├── metrics.ts        # Metrics and analytics types
│   └── index.ts
└── utils/                # Utilities and helpers
    ├── formatters.ts     # Data formatting functions
    └── constants.ts      # App constants

components/
├── layout/               # Layout components
│   ├── Sidebar.tsx
│   ├── TopBar.tsx
│   └── PageContainer.tsx
├── cards/                # Reusable card components
│   └── MetricCard.tsx
├── tables/               # Data tables
│   └── AlertsDataTable.tsx (TanStack Table)
├── charts/               # Chart components
│   ├── AlertsTrendChart.tsx
│   └── SeverityDonut.tsx
├── badges/               # Badge components
│   └── SeverityBadge.tsx
├── buttons/              # Button variants
│   └── ActionButtons.tsx
├── pages/                # Page-level components
└── providers/            # Context providers
    └── QueryProvider.tsx

app/
├── page.tsx              # Main router
├── layout.tsx            # Root layout
└── globals.css           # Global styles
```

## State Management Strategy

### React Query (Server State)
- **Purpose**: Manage server data (alerts, metrics, analytics)
- **Cache Strategy**: 
  - Dashboard metrics: 60s stale time, 5m garbage collection
  - Alerts list: 30s stale time
  - Analytics: 5m stale time
- **Automatic Invalidation**: After mutations (decision submission, alert updates)

### Local UI State
- **Filters**: Page number, severity, status, search term
- **Modal/Dialog**: Show/hide states, selected alert
- **Form**: Input validation, submission state

### URL Parameters
- Alert ID in investigation page
- Pagination state in alerts table

## API Contract

All endpoints follow REST conventions with JSON responses.

### Base URL
```
{BASE_URL}/api/v1
```

### Endpoints

#### Dashboard
- `GET /dashboard/metrics` - KPI metrics
- `GET /dashboard/alerts-trend?range=24h` - Alert trend data

#### Alerts
- `GET /alerts?page=1&limit=10&severity=HIGH&status=ACTIVE&search=...` - List alerts
- `GET /alerts/{alert_id}` - Alert details
- `POST /investigations/{alert_id}/decision` - Submit investigation decision

#### Analytics
- `GET /analytics/performance` - Model performance metrics
- `GET /analytics/feedback?page=1&limit=20` - Feedback history
- `GET /analytics/health` - System health status

### Error Handling

```json
{
  "error_code": "ALERT_NOT_FOUND",
  "message": "The requested alert does not exist"
}
```

Frontend must:
- Show user-friendly messages
- Never crash on errors
- Log errors silently
- Retry transient failures (2x retry by default)

## Component Patterns

### Data-Driven Components

```tsx
// Using React Query hooks
const { data, isLoading, error } = useAlerts({ page, severity })

if (isLoading) return <Skeleton />
if (error) return <ErrorBoundary />

return <AlertsDataTable data={data} />
```

### Reusable Cards

```tsx
<MetricCard
  title="Active Alerts"
  value={142}
  format="number"
  trend={8.2}
  icon={<AlertIcon />}
/>
```

### Tables with TanStack

```tsx
<AlertsDataTable
  data={alerts}
  isLoading={loading}
  onRowClick={(alert) => navigate(`/alert/${alert.id}`)}
/>
```

## Formatting & Constants

### Formatters
- `formatCurrency(amount, currency)` - Numbers to currency
- `formatDate(dateString)` - ISO to readable date
- `formatPercent(value, decimals)` - Numbers to percentages
- `formatRiskScore(score)` - Clamp 0-100
- `getSeverityColor(severity)` - Color classes
- `getSeverityBadgeClass(severity)` - Badge styling

### Constants
- `ALERT_SEVERITY_OPTIONS` - Severity dropdown options
- `ALERT_STATUS_OPTIONS` - Status filter options
- `DEFAULT_PAGE_SIZE` - 10 items per page
- `SEVERITY_LEVELS` - Numeric severity mapping

## Loading & Empty States

### Mandatory States
- ✅ Skeleton loaders for tables
- ✅ "No data" empty states
- ✅ Disabled buttons during submit
- ✅ Toast notifications for success/error
- ✅ Error boundaries with retry

### Example
```tsx
if (isLoading) return <AlertsTableSkeleton />
if (error) return <ErrorMessage onRetry={refetch} />
if (data.length === 0) return <EmptyState />
return <AlertsTable data={data} />
```

## TypeScript Types

All domain logic is typed:

```tsx
// Alert types
type AlertSeverity = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'
type AlertStatus = 'ACTIVE' | 'INVESTIGATING' | 'RESOLVED' | 'FALSE_POSITIVE'

interface Alert {
  alert_id: string
  timestamp: string
  entity: string
  risk_score: number
  severity: AlertSeverity
  status: AlertStatus
}

// Response types
interface AlertsResponse {
  data: Alert[]
  pagination: {
    page: number
    total_pages: number
    total_records: number
  }
}
```

## Performance Optimizations

1. **React Query Caching**: Automatic deduplication and background refetch
2. **Component Code Splitting**: Page-level lazy loading
3. **Memoization**: useMemo for columns/filters
4. **Debounced Search**: Prevent excessive queries
5. **Virtualized Tables**: TanStack handles row virtualization

## Security Best Practices

1. **API Client**: CORS handling, error redaction
2. **Input Validation**: Zod schemas (future)
3. **XSS Prevention**: React DOM escaping by default
4. **CSRF**: HTTP-only cookies (backend responsibility)
5. **Error Messages**: Never expose sensitive data

## Future Enhancements

- [ ] Offline support with Service Workers
- [ ] Real-time updates with WebSockets
- [ ] Advanced search with Elasticsearch
- [ ] Export functionality (CSV, PDF)
- [ ] Dark mode toggle
- [ ] Role-based access control
- [ ] Audit logging
- [ ] Alert subscriptions/notifications

## Debugging

Enable debug logs:
```tsx
// In components
console.log("[v0] Data loaded:", data)

// In services
console.error(`[API Error] ${endpoint}:`, error)
```

Remove debug statements after resolution.

## References

- [React Query Docs](https://tanstack.com/query/latest)
- [TanStack Table](https://tanstack.com/table/latest)
- [TypeScript Handbook](https://www.typescriptlang.org/docs)
- [REST API Best Practices](https://restfulapi.net)
