'use client'

import { PageContainer } from '@/components/layout/page-container'
import { Card } from '@/components/ui/card'
import { Zap, Brain, Database, GitBranch, ShieldCheck, Layers, Workflow, BarChart3, Activity } from 'lucide-react'

const HIGHLIGHTS = [
  { icon: Zap, label: 'Sub-25ms scoring', sub: 'Async FastAPI pipeline' },
  { icon: Brain, label: '3-model ensemble', sub: 'Statistical + Behavioural + ML' },
  { icon: GitBranch, label: 'Feedback loop', sub: 'Analyst labels drive retraining' },
  { icon: Database, label: 'Auditable schema', sub: 'Append-only, Alembic-managed' },
]

const DETECTORS = [
  {
    name: 'Statistical',
    weight: '25%',
    icon: BarChart3,
    desc: 'Hard signals: amount thresholds, z-scores, transaction velocity, and odd-hour activity.',
  },
  {
    name: 'Behavioural',
    weight: '35%',
    icon: Activity,
    desc: "Deviation from the entity's own history: spend spikes, first-time destinations, dormant-account reactivation.",
  },
  {
    name: 'ML (Isolation Forest)',
    weight: '40%',
    icon: Brain,
    desc: 'Unsupervised model that flags multi-dimensional anomalies no single rule would catch.',
  },
]

const STACK = [
  'Python', 'FastAPI', 'scikit-learn', 'Isolation Forest', 'PostgreSQL',
  'SQLAlchemy', 'Alembic', 'Next.js', 'TypeScript', 'Tailwind CSS', 'React Query',
]

export function AboutPage() {
  return (
    <PageContainer>
      <div className="space-y-6 max-w-5xl">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold text-foreground tracking-tight">About This Project</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Market Anomaly &amp; Fraud Detection System - a real-time, ML-powered risk engine with an analyst workflow.
          </p>
        </div>

        {/* Highlights strip */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {HIGHLIGHTS.map((h) => {
            const Icon = h.icon
            return (
              <Card key={h.label} className="p-4 bg-card border-border">
                <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10 text-primary mb-3">
                  <Icon className="h-5 w-5" />
                </div>
                <p className="text-sm font-semibold text-foreground leading-tight">{h.label}</p>
                <p className="text-xs text-muted-foreground mt-0.5">{h.sub}</p>
              </Card>
            )
          })}
        </div>

        {/* Overview */}
        <Card className="p-6 bg-card border-border">
          <div className="space-y-4 text-sm leading-relaxed text-muted-foreground">
            <p>
              Financial fraud costs institutions billions each year, yet legacy rule-based systems raise false
              positives on 70-80% of the transactions they flag. Fixed thresholds freeze legitimate customers,
              bury analysts in noise, and get reverse-engineered by fraudsters within days.
            </p>
            <p>
              This platform scores every transaction in real time by combining three independent detectors -
              statistical rules, per-entity behavioural baselines, and an unsupervised Isolation Forest model -
              into a weighted, confidence-aware 0-100 risk score. Alerts flow to analysts who investigate and
              label them, and those decisions feed back to continuously improve the model.
            </p>
            <p>
              It is built to production standards: a layered FastAPI backend over async PostgreSQL, reversible
              Alembic migrations, structured logging and observability, and a Next.js analyst dashboard -
              scoring each transaction in under 25 ms.
            </p>
          </div>
        </Card>

        {/* How it works */}
        <Card className="p-6 bg-card border-border">
          <div className="mb-3 flex items-center gap-2">
            <Workflow className="h-4 w-4 text-muted-foreground" />
            <h3 className="text-sm font-semibold text-foreground">How it works</h3>
          </div>
          <p className="mb-5 text-sm leading-relaxed text-muted-foreground">
            Each transaction first passes through feature engineering, which derives signals such as amount
            z-scores, velocity, time-of-day, geo and device risk, and per-entity baselines. Three independent
            detectors then score it in parallel, and their outputs are blended into a single confidence-weighted
            score from 0 to 100 - mapped to Low, Medium, High, or Critical. Anything above the alert threshold is
            raised to an analyst, whose decision is stored and fed back to retrain the model.
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {DETECTORS.map((d) => {
              const Icon = d.icon
              return (
                <div key={d.name} className="rounded-lg border border-border bg-muted/30 p-4">
                  <div className="mb-2 flex items-center justify-between">
                    <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10 text-primary">
                      <Icon className="h-4 w-4" />
                    </div>
                    <span className="rounded-full bg-muted px-2 py-0.5 text-[11px] font-semibold text-muted-foreground">
                      {d.weight}
                    </span>
                  </div>
                  <p className="text-sm font-semibold text-foreground">{d.name}</p>
                  <p className="mt-1 text-xs leading-relaxed text-muted-foreground">{d.desc}</p>
                </div>
              )
            })}
          </div>
          <p className="mt-4 text-xs text-muted-foreground">
            Weights reflect each detector&apos;s contribution to the composite score, with a confidence floor so a
            low-confidence detector can&apos;t wipe out its share.
          </p>
        </Card>

        {/* Tech stack */}
        <Card className="p-5 bg-card border-border">
          <div className="mb-3 flex items-center gap-2">
            <Layers className="h-4 w-4 text-muted-foreground" />
            <h3 className="text-sm font-semibold text-foreground">Built With</h3>
          </div>
          <div className="flex flex-wrap gap-2">
            {STACK.map((t) => (
              <span
                key={t}
                className="rounded-md border border-border bg-muted/40 px-2.5 py-1 text-xs font-medium text-foreground"
              >
                {t}
              </span>
            ))}
          </div>
        </Card>

        {/* Engineering notes */}
        <Card className="p-5 bg-card border-border">
          <div className="mb-2 flex items-center gap-2">
            <ShieldCheck className="h-4 w-4 text-emerald-500" />
            <h3 className="text-sm font-semibold text-foreground">Engineering notes</h3>
          </div>
          <ul className="space-y-1.5 text-sm text-muted-foreground">
            <li>Layered FastAPI backend: routes to services to repositories over async SQLAlchemy.</li>
            <li>Reversible Alembic migrations; schema ownership deferred to migrations in production.</li>
            <li>Confidence-weighted score aggregation with a floor to keep weak detectors honest.</li>
            <li>Structured logging and observability middleware on every request.</li>
          </ul>
        </Card>
      </div>
    </PageContainer>
  )
}
