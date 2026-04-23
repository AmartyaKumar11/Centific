# Agent Workspace Functional Specification

This document defines the **exact frontend-only functionality** for the `agent-workspace-react` project.
It is designed for a master agent to generate or orchestrate subagents by reading component behavior and UI actions.

---

## 1) Product Intent

- Product type: Agent-first loan case workspace
- Interaction model: Event-driven, loop-based, audit-friendly
- Channel assumptions: External communications occur via email
- Scope: Frontend-only simulation (no backend calls, no API integration)

---

## 2) Global Case State Model

Managed inside `app/page.tsx` via React state:

- `status: CaseStatus`
  - Enum values:
    - `Processing`
    - `Awaiting Input`
    - `Awaiting Approval`
    - `Completed`
    - `Rejected`
- `confidence: number`
  - Starts at `87`
  - Increases when issues are resolved
- `iterations: number`
  - Starts at `11`
  - Increments on status changes and issue resolution
- `conflicts: number`
  - Starts at `2`
  - Decrements on issue resolution
- `selectedEvent: TimelineEvent | null`
  - Controls timeline detail modal open/close
- `issues: string[]`
  - Open issue list
  - Removal of item simulates issue resolution

---

## 3) Component Inventory

### 3.1 `HomePage` (`app/page.tsx`)

Primary orchestrator component for:

- layout composition
- local state ownership
- interaction handlers
- modal lifecycle
- business walkthrough simulation controls

### 3.2 `Card` (`components/ui/card.tsx`)

Reusable container abstraction:

- props:
  - `title: string`
  - `subtitle?: string`
  - `right?: ReactNode`
  - `children: ReactNode`
- behavior:
  - purely presentational
  - standardizes header/body layout

### 3.3 `Badge` (`components/ui/badge.tsx`)

Reusable semantic status indicator:

- tones:
  - `default`
  - `success`
  - `warning`
  - `danger`
  - `soft`
- behavior:
  - purely presentational
  - used for case status, trust levels, and action states

### 3.4 `Button` (`components/ui/button.tsx`)

Reusable action trigger:

- variants:
  - `primary`
  - `secondary`
  - `ghost`
  - `danger`
- behavior:
  - accepts optional `onClick`
  - dispatches local UI actions in `HomePage`

### 3.5 Utility `cn` (`lib/utils.ts`)

- className composition helper
- used by UI primitives for variant styling

---

## 4) Timeline Model

`initialTimeline` is a static array with 5 events:

- mandatory event fields:
  - `id`
  - `timestamp`
  - `title`
  - `note`
  - `icon` (`info | warning | action`)
  - `compared`
  - `resolution`
  - `impact`

### Timeline click behavior

When any timeline item is clicked:

1. `selectedEvent` is set to clicked event object
2. Modal becomes visible
3. Modal renders:
   - Compared Values
   - Resolution
   - Impact

Modal close actions:

- click `Close` button
- click modal backdrop

---

## 5) Action Map: Every Interactive Control

## 5.1 Agent Controls Panel Buttons

### A) `Set Processing`
- Handler: `handleStatusChange("Processing")`
- Effects:
  - `status = Processing`
  - `iterations += 1`

### B) `Set Awaiting Input`
- Handler: `handleStatusChange("Awaiting Input")`
- Effects:
  - `status = Awaiting Input`
  - `iterations += 1`

### C) `Set Awaiting Approval`
- Handler: `handleStatusChange("Awaiting Approval")`
- Effects:
  - `status = Awaiting Approval`
  - `iterations += 1`

### D) `Mark Completed`
- Handler: `handleStatusChange("Completed")`
- Effects:
  - `status = Completed`
  - `iterations += 1`

### E) `Mark Rejected`
- Handler: `handleStatusChange("Rejected")`
- Effects:
  - `status = Rejected`
  - `iterations += 1`

## 5.2 Open Issues Panel Buttons

Each issue row has a `Resolve` button.

- Handler: `resolveIssue(index)`
- Effects:
  - removes issue by array index
  - `conflicts -= 1` (not below 0)
  - `confidence += 2` (capped at 99)
  - `iterations += 1`

When all issues are resolved:

- warning list hides
- success empty state appears: `All blockers resolved.`

## 5.3 Timeline Event Rows

- Interaction: click any row
- Handler: `setSelectedEvent(event)`
- Effects:
  - opens modal
  - loads event-specific `compared`, `resolution`, `impact`

## 5.4 Modal Close Controls

- `Close` button => `setSelectedEvent(null)`
- backdrop click => `setSelectedEvent(null)`

---

## 6) Panels and Intended BA Interpretation

### 6.1 Header + Case Status
- Displays current operational state of case
- Serves as global health indicator

### 6.2 Case Summary Header Metrics
- Case ID
- Status
- Confidence
- Iterations
- Conflicts

These values are expected to evolve during BA walkthrough using action buttons.

### 6.3 Case Timeline (Primary)
- Canonical source of "what agent did"
- Click-to-drill for audit details

### 6.4 Communication Log
- Demonstrates all external interactions are email-based
- Split into Sent and Received for clarity

### 6.5 Income / Risk / Credit
- Each card includes:
  - source
  - confidence
  - conflict resolution note

### 6.6 Open Issues
- Prominent unresolved blockers
- Interactive issue closure simulation

### 6.7 Agent Recommendation
- Recommendation type + rationale + conditions
- Structured for decision review

### 6.8 Data Trust Levels
- Source reliability tiers:
  - Bank statement = High
  - Salary slip = Medium
  - User input = Low

---

## 7) Shadcn Alignment Strategy

Project uses shadcn-style architecture:

- separated primitive UI components (`Button`, `Badge`, `Card`)
- utility-based class composition (`cn`)
- composable panel layout

If full shadcn CLI integration is later required, primitives can be swapped with generated shadcn components without changing business logic in `HomePage`.

---

## 8) BA Walkthrough Script (Recommended)

1. Review baseline case state in summary header.
2. Click each timeline event to inspect compared values, resolution, and impact.
3. Use Agent Controls to transition case state.
4. Resolve open issues one by one and observe confidence/conflict updates.
5. Validate final recommendation and trust-level rationale.

---

## 9) Files for Master Agent Consumption

- UI code:
  - `app/page.tsx`
  - `components/ui/card.tsx`
  - `components/ui/button.tsx`
  - `components/ui/badge.tsx`
  - `app/globals.css`
- Utility:
  - `lib/utils.ts`
- Functional mapping doc:
  - `AGENT_COMPONENT_FUNCTIONALITY.md`

