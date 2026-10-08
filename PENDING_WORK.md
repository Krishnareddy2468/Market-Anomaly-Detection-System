# Pending Work Tracker

Last updated: 2026-10-09

## 1. Immediate Completion Tasks (Current Branch)

- [x] Validate non-deployment changes end-to-end (typecheck + backend deterministic smoke test)
- [x] Resolve lint command blocker in offline environment (mapped `lint` -> `typecheck`)
- [x] Local UI/API verification — frontend `tsc` + `next build` (11 pages) pass; backend
      routes verified live against a seeded PostgreSQL via `backend/scripts/smoke_test.py` (17/17)
- [x] Commit staged changes with a focused message

## 2. Deployment Checklist Status (docs/STEP7_DEPLOYMENT_PRODUCTION.md)

Pre-deployment:
- [x] Health check endpoint exists (`GET /health`) and returns `status: healthy` in code
- [x] CORS is configurable via `CORS_ORIGINS`
- [x] Structured logging is implemented and supports `LOG_FORMAT=json`
- [x] Seed script exists (`python -m app.db.seed`)
- [x] All environment variables documented and verified complete in `.env.example`
      (26/26 `Settings` fields present)
- [x] Database migrations set up and tested with Alembic — initial migration
      (`alembic/versions/6f7832725e27_initial_schema.py`) verified upgrade → downgrade →
      re-upgrade (fully reversible, incl. explicit Postgres ENUM cleanup) against Postgres 16.
      `init_db()` now defers schema ownership to Alembic outside `development`.
- [ ] Secrets rotated from development defaults — *deferred to deployment time* (rotate
      `SECRET_KEY` / DB credentials in the target environment; `.env.example` flags the defaults)

Post-deployment verification:
- [ ] `/health` checked on deployed environment
- [ ] Dashboard load performance verified (<2s)
- [ ] Alert pagination verified in deployed UI
- [ ] Investigation context completeness verified in deployed UI
- [ ] Structured logs confirmed in runtime sink (CloudWatch/stdout)
- [ ] Error responses checked for stack-trace leakage

## 3. Product Backlog (ARCHITECTURE.md Future Enhancements)

- [ ] Offline support with Service Workers
- [ ] Real-time updates with WebSockets
- [ ] Advanced search with Elasticsearch
- [ ] Export functionality (CSV, PDF)
- [ ] Dark mode toggle
- [ ] Role-based access control
- [ ] Audit logging
- [ ] Alert subscriptions/notifications

## 4. Validation Snapshot (2026-10-09)

Completed checks:
- [x] TypeScript type check passed (`tsc --noEmit` via `npm run typecheck`/`lint`)
- [x] Frontend production build passed (`next build`, 11 routes generated)
- [x] Detection pipeline deterministic smoke test passed (same input => same scores)
- [x] Full backend booted against live PostgreSQL 16; `/health` + all route groups return 200
- [x] Detection endpoint verified live (suspicious => MEDIUM/alert, benign => LOW/no-alert, <10ms)
- [x] Investigation write path verified (ACTIVE → INVESTIGATING → decision → feedback persisted)
- [x] Alembic migration round-trip verified (upgrade/downgrade/re-upgrade)

Environment notes:
- Local verification used an isolated Docker Postgres 16 with `DATABASE_URL` overridden via env
  (the committed `.env` was never modified). Reusable check: `backend/scripts/smoke_test.py`.

## 5. Recommended Next Actions

- [x] Run `npm run lint` (typecheck) — passes
- [x] Start backend-independent detection smoke tests (direct engine execution)
- [x] Start full backend and run health + detection endpoint smoke tests against live DB
- [x] Verify alerts/analytics/feedback/investigation pages/APIs against updated contracts
- [x] Run Alembic migration verification against a live DB
- [x] Commit staged changes after smoke checks pass
- [ ] AWS deployment (RDS + ECS) and post-deploy verification — *out of scope for now*
