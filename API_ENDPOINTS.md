# API Endpoints Reference

This document outlines all available API endpoints and their mock implementations.

## Base URL
`http://localhost:3000` (development)

## Dashboard Endpoints

### GET /api/dashboard/metrics
Returns key performance indicators and dashboard metrics.

**Response:**
```json
{
  "success": true,
  "data": {
    "total_transactions": 2400000,
    "active_alerts": 142,
    "high_risk_alerts": 28,
    "false_positive_rate": 2.3,
    "trends": {
      "alerts_change_pct": 8.2,
      "false_positive_change_pct": -0.5,
      "transaction_volume_change_pct": 12.5
    },
    "timestamp": "2024-02-09T..."
  }
}
```

### GET /api/dashboard/alerts-trend
Returns time-series alert trend data.

**Query Parameters:**
- `range` (optional): `24h` | `7d` | `30d` (default: `24h`)

**Response:**
```json
{
  "success": true,
  "data": [
    { "time": "12 AM", "alerts": 24 },
    { "time": "1 AM", "alerts": 32 }
  ]
}
```

### GET /api/dashboard/severity-distribution
Returns alert severity distribution data.

**Response:**
```json
{
  "success": true,
  "data": [
    { "name": "High", "value": 35, "color": "hsl(0, 84%, 60%)" },
    { "name": "Medium", "value": 45, "color": "hsl(54, 92%, 50%)" },
    { "name": "Low", "value": 20, "color": "hsl(120, 73%, 75%)" }
  ]
}
```

## Alerts Endpoints

### GET /api/alerts
Fetch paginated alert list with optional filters.

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 10)
- `severity` (optional): `HIGH` | `MEDIUM` | `LOW` | `ALL`
- `status` (optional): `ACTIVE` | `INVESTIGATING` | `REVIEWING` | `RESOLVED` | `ALL`
- `search` (optional): Search by alert ID or entity

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "alert_id": "ALT-001",
      "created_at": "2024-02-09T14:32:18Z",
      "entity_id": "USER-42521",
      "entity_type": "user",
      "risk_score": 94,
      "severity": "HIGH",
      "status": "ACTIVE",
      "description": "Unusual transaction pattern detected"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total_records": 142,
    "total_pages": 15
  }
}
```

## Analytics Endpoints

### GET /api/analytics/metrics
Returns model performance metrics.

**Response:**
```json
{
  "success": true,
  "data": {
    "precision": 0.96,
    "recall": 0.92,
    "f1_score": 0.94,
    "accuracy": 0.95,
    "auc_roc": 0.98,
    "timestamp": "2024-02-09T..."
  }
}
```

### GET /api/analytics/trends
Returns alert and resolution trends over time.

**Response:**
```json
{
  "success": true,
  "data": [
    { "date": "Jan 1", "alerts": 120, "resolved": 100, "false_positives": 20 }
  ]
}
```

## Feedback Endpoints

### GET /api/feedback
Fetch analyst feedback history with pagination.

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 10)

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "FB-001",
      "alert_id": "ALT-001",
      "decision": "CONFIRMED_FRAUD",
      "confidence": 0.95,
      "notes": "User verified suspicious activity.",
      "analyst": "John Analyst",
      "created_at": "2024-02-09T13:32:18Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total_records": 3,
    "total_pages": 1
  }
}
```

## Error Responses

All endpoints return errors in the following format:

```json
{
  "success": false,
  "error": "Error message describing what went wrong"
}
```

## Service Layer

The service layer abstracts API calls:

- `DashboardService` - Dashboard metrics and trends
- `AlertsService` - Alert CRUD and filtering
- `AnalyticsService` - Performance metrics and feedback
- `ApiClient` - HTTP client with retry logic

## React Query Hooks

All data fetching is managed through custom hooks:

- `useDashboardData()` - Dashboard metrics and trends
- `useAlerts(filters)` - Alert list
- `usePerformanceMetrics()` - Analytics metrics
- `useAnalyticsTrends()` - Analytics trends
- `useFeedbackHistory()` - Feedback data

Hooks automatically handle caching, retries, and error states.
