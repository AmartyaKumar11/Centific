"use client";

import { useMemo, useState } from "react";
import { AlertTriangle, CheckCircle2, Clock3, Mail, Send, ShieldCheck } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

type CaseStatus = "Processing" | "Awaiting Input" | "Awaiting Approval" | "Completed" | "Rejected";

type TimelineEvent = {
  id: string;
  timestamp: string;
  title: string;
  note: string;
  icon: "info" | "warning" | "action";
  compared: string;
  resolution: string;
  impact: string;
};

const initialTimeline: TimelineEvent[] = [
  {
    id: "email-1",
    timestamp: "22 Apr 2026, 10:34 AM",
    title: "Email received",
    note: "Applicant shared salary slips and Form 16.",
    icon: "info",
    compared: "Declared income INR 120,000 vs extracted salary INR 118,400.",
    resolution: "Marked as minor discrepancy and moved for reconciliation.",
    impact: "Confidence unchanged at 82% pending bank statement."
  },
  {
    id: "mismatch-1",
    timestamp: "22 Apr 2026, 10:42 AM",
    title: "Income mismatch detected",
    note: "Bank credit average was lower than payroll record.",
    icon: "warning",
    compared: "Salary slip INR 118,400 vs bank credit INR 115,800.",
    resolution: "Agent triggered clarification request flow.",
    impact: "Confidence dropped from 82% to 76%."
  },
  {
    id: "send-1",
    timestamp: "22 Apr 2026, 10:45 AM",
    title: "Email sent to applicant",
    note: "Requested latest bank statement for discrepancy closure.",
    icon: "action",
    compared: "Required 6-month banking evidence vs 3-month current evidence.",
    resolution: "Case moved to Awaiting Input.",
    impact: "No confidence change."
  },
  {
    id: "receive-2",
    timestamp: "22 Apr 2026, 10:56 AM",
    title: "Bank statement received",
    note: "Latest statement closed variance within policy threshold.",
    icon: "info",
    compared: "Updated April credit aligns with payroll run.",
    resolution: "Conflict auto-resolved by reconciliation rule.",
    impact: "Confidence increased from 76% to 87%."
  },
  {
    id: "approve-req",
    timestamp: "22 Apr 2026, 11:08 AM",
    title: "Case sent for approval",
    note: "Senior loan officer review requested by agent.",
    icon: "action",
    compared: "Risk threshold <=35 vs observed risk 28; DTI <=50% vs observed 36.8%.",
    resolution: "Conditional recommendation package delivered via email.",
    impact: "Case moved to Awaiting Approval."
  }
];

export default function HomePage() {
  const [status, setStatus] = useState<CaseStatus>("Processing");
  const [confidence, setConfidence] = useState(87);
  const [iterations, setIterations] = useState(11);
  const [conflicts, setConflicts] = useState(2);
  const [selectedEvent, setSelectedEvent] = useState<TimelineEvent | null>(null);

  const [issues, setIssues] = useState([
    "Missing property valuation document",
    "Pending final senior loan officer approval",
    "Employer validation awaiting external registry response"
  ]);

  const resolvedIssueCount = 3 - issues.length;

  const statusTone = useMemo(() => {
    if (status === "Rejected") return "danger";
    if (status === "Completed") return "success";
    if (status === "Awaiting Input" || status === "Awaiting Approval") return "warning";
    return "default";
  }, [status]);

  function handleStatusChange(next: CaseStatus) {
    setStatus(next);
    setIterations((v) => v + 1);
  }

  function resolveIssue(index: number) {
    setIssues((prev) => prev.filter((_, i) => i !== index));
    setConflicts((v) => (v > 0 ? v - 1 : 0));
    setConfidence((v) => Math.min(99, v + 2));
    setIterations((v) => v + 1);
  }

  return (
    <main className="workspace">
      <header className="topbar-lite">
        <div>
          <h1>AI Loan Officer Agent Workspace</h1>
          <p>Agent-first visualization for audit-friendly case execution.</p>
        </div>
        <div className="top-actions">
          <Badge tone={statusTone as "default" | "success" | "warning" | "danger"}>Case Status: {status}</Badge>
          <Badge tone="soft">Case ID: LPA-2026-00847</Badge>
        </div>
      </header>

      <section className="case-summary">
        <div className="metric"><span>Case ID</span><strong>LPA-2026-00847</strong></div>
        <div className="metric"><span>Status</span><strong>{status}</strong></div>
        <div className="metric"><span>Confidence</span><strong>{confidence}%</strong></div>
        <div className="metric"><span>Iterations</span><strong>{iterations}</strong></div>
        <div className="metric"><span>Conflicts</span><strong>{conflicts}</strong></div>
      </section>

      <section className="main-grid">
        <div className="main-column">
          <Card
            title="Case Timeline"
            subtitle="Primary event stream that the agent used to reach current recommendation"
          >
            <ul className="timeline-list">
              {initialTimeline.map((event) => (
                <li key={event.id} className="timeline-item">
                  <button type="button" onClick={() => setSelectedEvent(event)} className="timeline-button">
                    <span className={`timeline-icon ${event.icon}`}>
                      {event.icon === "warning" ? <AlertTriangle size={14} /> : event.icon === "action" ? <Send size={14} /> : <Clock3 size={14} />}
                    </span>
                    <span className="timeline-content">
                      <span className="timeline-time">{event.timestamp}</span>
                      <span className="timeline-title">{event.title}</span>
                      <span className="timeline-note">{event.note}</span>
                    </span>
                  </button>
                </li>
              ))}
            </ul>
          </Card>

          <Card title="Communication Log" subtitle="All email interactions with applicant and senior loan officer">
            <div className="comm-grid">
              <div>
                <h4>Emails Sent</h4>
                <div className="comm-item"><Mail size={14} /> Subject: Need latest bank statement<br />Summary: Requested April credits to close income mismatch.</div>
                <div className="comm-item"><Mail size={14} /> Subject: Case sent for approval<br />Summary: Shared recommendation + unresolved blockers.</div>
              </div>
              <div>
                <h4>Emails Received</h4>
                <div className="comm-item"><Mail size={14} /> Subject: Salary slips and Form 16<br />Summary: Applicant submitted core income documents.</div>
                <div className="comm-item"><Mail size={14} /> Subject: Updated statement attached<br />Summary: Applicant provided requested banking evidence.</div>
              </div>
            </div>
          </Card>
        </div>

        <aside className="side-column">
          <Card title="Agent Controls" subtitle="Frontend-only controls for BA walkthrough and subagent simulation">
            <div className="button-grid">
              <Button onClick={() => handleStatusChange("Processing")}>Set Processing</Button>
              <Button onClick={() => handleStatusChange("Awaiting Input")}>Set Awaiting Input</Button>
              <Button onClick={() => handleStatusChange("Awaiting Approval")}>Set Awaiting Approval</Button>
              <Button variant="primary" onClick={() => handleStatusChange("Completed")}>Mark Completed</Button>
              <Button variant="danger" onClick={() => handleStatusChange("Rejected")}>Mark Rejected</Button>
            </div>
          </Card>

          <Card title="Income / Risk / Credit" subtitle="Updated cards with source, confidence, and conflict resolution">
            <div className="kpi-stack">
              <div className="kpi"><h4>Income: INR 118,400</h4><p>Source: Salary Slip + Bank Statement</p><p>Confidence: 88%</p><p>Resolution: mismatch closed after latest statement.</p></div>
              <div className="kpi"><h4>Risk: 28 / 100</h4><p>Source: Policy Risk Model</p><p>Confidence: 84%</p><p>Resolution: active-loan impact lowered after clean repayment history.</p></div>
              <div className="kpi"><h4>Credit: 762</h4><p>Source: CIBIL API</p><p>Confidence: 99%</p><p>Resolution: no conflict; direct bureau pull.</p></div>
            </div>
          </Card>

          <Card
            title="Open Issues"
            subtitle={`Unresolved blockers: ${issues.length} | Resolved this session: ${resolvedIssueCount}`}
            right={<Badge tone={issues.length > 0 ? "warning" : "success"}>{issues.length > 0 ? "Action Needed" : "All Clear"}</Badge>}
          >
            {issues.length === 0 ? (
              <div className="empty-state"><CheckCircle2 size={16} /> All blockers resolved.</div>
            ) : (
              <ul className="issue-list">
                {issues.map((issue, index) => (
                  <li key={issue} className="issue-item">
                    <span><AlertTriangle size={14} /> {issue}</span>
                    <Button onClick={() => resolveIssue(index)} variant="ghost">Resolve</Button>
                  </li>
                ))}
              </ul>
            )}
          </Card>

          <Card title="Agent Recommendation" subtitle="Recommendation type, explanation, and conditions">
            <div className="recommendation">
              <Badge tone="default">Conditional Approval</Badge>
              <p>
                Recommend prequalification approval due to strong credit score, acceptable DTI, and verified income.
              </p>
              <p>
                Conditions: property valuation must satisfy LTV policy, employer validation must return a match, and no new liabilities should be reported.
              </p>
            </div>
          </Card>

          <Card title="Data Trust Levels" subtitle="Source reliability used by the agent">
            <div className="trust-list">
              <div><span>Bank statement</span><Badge tone="success">High</Badge></div>
              <div><span>Salary slip</span><Badge tone="warning">Medium</Badge></div>
              <div><span>User input</span><Badge tone="danger">Low</Badge></div>
            </div>
          </Card>
        </aside>
      </section>

      {selectedEvent ? (
        <div className="modal-layer" role="dialog" aria-modal="true" onClick={() => setSelectedEvent(null)}>
          <div className="modal-body" onClick={(event) => event.stopPropagation()}>
            <div className="modal-head">
              <h3>{selectedEvent.title}</h3>
              <Button variant="ghost" onClick={() => setSelectedEvent(null)}>Close</Button>
            </div>
            <div className="modal-content">
              <div><h4>Compared values</h4><p>{selectedEvent.compared}</p></div>
              <div><h4>Resolution</h4><p>{selectedEvent.resolution}</p></div>
              <div><h4>Impact</h4><p>{selectedEvent.impact}</p></div>
            </div>
          </div>
        </div>
      ) : null}
    </main>
  );
}
