# Agent Dashboard — UI Component Map (AI Agent Spec)

**Viewport assumption:** `1440 × 900` CSS pixels (desktop).

**Coordinate convention:** Approximate **center** `(x, y)` of each interactive region in viewport space, origin top-left. Values are **estimates** from layout (fixed positioning, max-width containers, `className` dimensions). They shift with content, font metrics, and scroll.

**Selectors:** Most components do not set `data-testid`. Prefer `aria-label` where present, otherwise a **unique CSS path** or **role + text** selector. Suggested stable hooks for automation are noted.

---

## Methodology (dimensions)

| Source | How size was obtained |
|--------|------------------------|
| Tailwind arbitrary sizes | Literal (e.g. `h-[60px] w-[60px]` → **60 × 60**) |
| Tailwind spacing scale | `py-2` → 8px top+bottom (when 1 unit = 4px) |
| Components | Read from `frontend/**/*.tsx` as of this document |

---

## Global shell (all routes below `/`)

Present on every route: **`TaskBar`** (`footer.fixed.bottom-5`), three **`AppIcon`** links + clock.

| Component | Selector | Visible label | Approx center (×900) | Size (W×H px) |
|-----------|----------|---------------|----------------------|---------------|
| `AppIcon` → Overview | `a[aria-label="Overview"]` | Overview (tooltip on hover) | ~(676, 835) | **60 × 60** (icon `span`; link hit area extends slightly) |
| `AppIcon` → HIL Review | `a[aria-label="HIL Review"]` | HIL Review | ~(720, 835) | **60 × 60** |
| `AppIcon` → Applications | `a[aria-label="Applications"]` | Applications | ~(764, 835) | **60 × 60** |
| Clock | `footer nav ~ span.text-xs` (sibling after `nav`) | `HH:MM:SS` (locale) | ~(830, 835) | ~**72 × 16** (text only; not a control) |

**TaskBar dock container** (rounded bar): visually ~**280–320 × 72** px, centered horizontally at **x ≈ 720**, bottom inset **20px** (`bottom-5`).

---

## 1. `/` — Desktop Home (`DesktopLandingPage`)

**Route:** `/`  
**Main:** `DesktopLandingPage` in `frontend/app/page.tsx`

### Interactive / primary targets

| Component | Selector | Visible text | Approx center (×900) | Size (W×H px) |
|-----------|----------|--------------|----------------------|---------------|
| *(global)* TaskBar nav | see Global shell | — | — | — |

### Non-interactive informational UI (included for agent vision / OCR)

| Component | Selector / region | Visible text | Approx region | Size (notes) |
|-----------|-------------------|--------------|---------------|----------------|
| Left snapshot card | `aside.w-\\[290px\\]` (first in `lg:flex` row) | “Today’s Queue Snapshot” | left **x ~ 165**, top **y ~ 140** | **290 × ~200** (varies with 2×2 `MetricTile` grid) |
| `MetricTile` ×4 | `.grid.grid-cols-2` inner cells | Need Review, Reviewed, Accepted, Rejected + numbers | inside left card | each tile ~**125 × 52** (`rounded-lg border px-2.5 py-2`) |
| Right “Decision Mix” card | `aside.w-\\[270px\\]` | “Decision Mix”, Accepted/Rejected/Under Review rows | **x ~ 1275**, **y ~ 140** | **270 × ~220** |
| `MixRow` progress bars | `div.h-2.rounded-full` | `%` labels | inside right card | bar track **h = 8px**, width ≈ card minus padding |
| Center hero card | `section` → inner `max-w-3xl` (`768px` max) centered | “Loan Underwriting AI Agent”, “AI Loan Agent”, “Virtual Credit Underwriter” | center **(720, 380)** | card max **768 × ~220** (`p-8`), Mac dots row **~52 × 10** |

### Charts / canvas on home

None (metrics are numeric tiles and progress bars only).

---

## 2. `/overview` — Compact dashboard (`OverviewPage` → `CompactDashboard`)

**Route:** `/overview`  
**Viewport block:** `main.max-w-\\[1600px\\]` → `CompactDashboard`

### KPI row (`CompactKPICard` ×5)

Each card: `article.h-\\[68px\\]`, `border-l-4`, `px-3 py-2`.

| Component | Selector | Visible label (title) | Approx center (×900)* | Size (W×H px) |
|-----------|----------|------------------------|----------------------|---------------|
| KPI 1 | `article` nth-of-type in first grid row | Applications Today | ~(268, 118) | **~312 × 68** (1600px content − padding, ÷5 columns at `lg`) |
| KPI 2 | same row | STP Approved (%) | ~(524, 118) | **~312 × 68** |
| KPI 3 | same row | HIL Queue | ~(780, 118) | **~312 × 68** |
| KPI 4 | same row | Rejected | ~(1036, 118) | **~312 × 68** |
| KPI 5 | same row | Avg TAT | ~(1292, 118) | **~312 × 68** |

\*Centers assume `max-w-[1600px]` centered on 1440 → content uses full **1440** width; horizontal splits are approximate **(1440 − 24 px) / 5**.

### Chart cards (`article.h-\\[220px\\]` shell, `padding: 12px`)

| Component | Selector | Title text | Approx center | Outer size |
|-----------|----------|------------|---------------|------------|
| Decision Distribution | `section article` ~1 | Decision Distribution | ~(268, 268) | **~413 × 220** (`lg:col-span-4`) |
| Risk Distribution | next article | Risk Distribution | ~(720, 268) | **~413 × 220** |
| Employer Split | next article | Employer Split | ~(1172, 268) | **~413 × 220** |
| Daily Batch Volume | `lg:col-span-6` article | Daily Batch Volume | ~(358, 508) | **~628 × 220** |
| Top Rejection Reasons | `lg:col-span-6` article | Top Rejection Reasons | ~(1082, 508) | **~628 × 220** |

**Chart canvas:** inner wrapper `div.h-\\[180px\\]` → plotting area **width ≈ card − 24px**, **height = 180**.

**Interaction:** Chart.js `Doughnut` / `Bar` — legend and canvas respond to pointer (toggle dataset / tooltip). No `data-testid`; target via **canvas** inside each `article` or **legend** under chart.

### Pipeline strip

| Component | Selector | Visible text | Approx center | Size |
|-----------|----------|--------------|---------------|------|
| Pipeline container | `article` with `grid-cols-7`, `min-w-\\[820px\\]` | steps 01–07 | ~(720, 688) | **scroll width ≥820 × ~80** (`COMPACT_PIPELINE_HEIGHT_CLASS`) |
| Step cell ×7 | `div.rounded-md` per step | “Data Intake”, “Feature Eng”, … | spaced ~117px apart in row | each **~110 × ~48** (`px-2 py-1.5`) |

### Bottom metric quartet (`h-\\[150px\\]`)

| Title | Approx center | Size |
|-------|---------------|------|
| STP Rate | ~(198, 818) | **~330 × 150** |
| Decision Accuracy | ~(534, 818) | **~330 × 150** |
| False Reject Rate | ~(870, 818) | **~330 × 150** |
| LMS Push Success | ~(1206, 818) | **~330 × 150** |

---

## 3. `/applications` and `/apps` — Applications register (`ApplicationsPage`)

**Routes:** `/applications`, `/apps` (same component)

### Top bar (`MacWindowCard` “All Applications”)

| Component | Selector | Visible label | Approx center | Size (W×H px) |
|-----------|----------|-----------------|---------------|---------------|
| Search input | `input[placeholder='Search applicant or app id']` | *(placeholder)* “Search applicant or app id” | ~(1050, 132) | **~220 × 40** (`px-3 py-2 text-sm`) |
| Status filter | `select` (first) | “All Status” | ~(1188, 132) | **~130 × 40** |
| Risk filter | `select` (second) | “All Risk Tiers” | ~(1310, 132) | **~130 × 40** |
| Export button | `button` with “Export CSV” | Export CSV | ~(1395, 132) | **~100 × 40** |

### Charts row (`Charts`)

Three `MacWindowCard`s in `grid lg:grid-cols-3`:

| Title | Chart area | Inner plot | |
|-------|------------|------------|--|
| Decision Distribution | `div.h-56` | **224px** tall canvas region | |
| Risk Distribution | `div.h-56` | **224px** tall | |
| Confidence Distribution | `div.h-56` | Bar chart | |

Approx row center **y ~ 380** (below top card).

### Table (`ApplicationsTable` → `MacWindowCard` “Application Register”)

| Component | Selector | Visible label | Interaction | Approx row center y* |
|-----------|----------|-----------------|-------------|---------------------|
| Header badge | `headerRight` span | “{n} applications” | none | — |
| Table header | `thead th` | Applicant, Loan Amount, … | — | **y ~ 520** (first header row) |
| Body row | `tbody tr` | Applicant name + id | **click** opens `ApplicationReviewModal` | **~548 + i×48** (row height varies) |
| Open page link | `Link` in Route column | “Open page” | navigates to `/applications/:id` | end of row, **~56 × 28** link box |

\*Row height not fixed; **~48px** is a reasonable estimate for `px-4 py-3` cells.

---

## 4. `/applications/:id` — Application detail (`ApplicationDetailPage`)

**Route:** `/applications/:id`

| Component | Selector | Visible text | Approx center | Size (W×H px) |
|-----------|----------|--------------|---------------|---------------|
| Back link | `Link` in `ApplicationHeader` | “Back to Dashboard” | ~(1320, 156) | **~150 × 36** (`px-3 py-2 text-sm`) |
| Header card | `MacWindowCard` title = applicant name | applicant id, reasoning summary | ~(720, 220) | **max-w-5xl (~1024) × ~140+** body |
| Summary rows | `SummaryRow` ×8 | Employer, Income, CIBIL, DTI, Risk, Decision, Approved Amount, Confidence | two columns **md:grid-cols-2** | each row ~**full half-width × ~40** |
| Timeline | `Timeline` → `TimelineStep` × N | step_name, tool_name, reasoning | ~(720, 560) | card full width **~1024 × variable** |

### `TimelineStep` nodes

| Part | Selector | Notes | Size |
|------|----------|-------|------|
| Status dot | `span.absolute.h-3.w-3.rounded-full` | color by status | **12 × 12** |
| Body | `article.relative.pl-8` | stacked `space-y-6` | width **~960** inside card |

---

## 5. `/hil-review` — HIL lanes (`HilReviewPage` → `HilReviewClient`)

**Route:** `/hil-review`

### Outer card

| Component | Selector | Visible text | Approx center | Size |
|-----------|----------|--------------|---------------|------|
| Gate card | first `MacWindowCard` | “HIL Review - Credit Officer Gate” | ~(720, 200) | **max-w-[1500] × variable** |
| Loading | `p` when loading | “Loading queue…” | — | — |
| Error | `p.text-rose-600` | API error string | — | — |

### Lanes ×4 (`MacWindowCard` per lane)

| Lane title | Header badge | Kanban card (`role="button"`) |
|------------|--------------|-------------------------------|
| Awaiting Review | count badge | Applicant card: id, name, loan line, risk chip, bar |
| Under Review | count | same pattern |
| CO Approved | count | same |
| CO Rejected | count | same |

**Lane column** (at `lg:grid-cols-4`): approximate width **(1500 − gaps) / 4 ~ 360px**, `min-h-[460px]`.

**Kanban card** (one application):

| Sub-element | Selector | Visible | Approx size |
|-------------|----------|---------|-------------|
| Card container | `div.cursor-pointer.rounded-lg...p-3` | — | **~340 × ~140** (varies) |
| Risk chip | `span.chip` | scoreBand text | **~120 × 24** |
| Progress bar | `div.h-1.5` | — | **full width × 6px** |

---

## 6. HIL / review modal — `ApplicationDetailModal`

**Where used:** Opened from **`HilReviewClient`** when a lane card is clicked (same component can be reused elsewhere if imported).

**Overlay:** `div.fixed.inset-0.z-50` — clicking **backdrop** (mousedown on overlay, not dialog) closes.

### Header

| Component | Selector | Visible text | Approx center (×900)* | Size |
|-----------|----------|--------------|-------------------------|------|
| Title block | `header` left `div` | “Application Review & Status”, `{application.id}` | ~(480, 120) | text block |
| Close | `header button` (rose) | “Close” | ~(1180, 120) | **~56 × 28** |

\*Modal `max-w-[1200px]` centered → panel **x ≈ 360–1080**.

### Body — left: audit trail (`EventTimeline`)

| Component | Selector | Visible | Region |
|-----------|----------|---------|--------|
| Scroll section | `section.max-h-[400px].overflow-y-auto` | — | **~480px wide × 400px max** (`md:col-span-2`) |
| Event card | `article` per event | timestamp, `{code}`, title, description, `<code>` output | **~440 × ~120** each (`p-3`) |

### Body — right: borrower / metrics (`BorrowerProfile`)

| Block | Content | Approx width |
|-------|---------|--------------|
| Identity / tags | name, id, tag chips | full **~700px** column (`md:col-span-3`) |
| Risk score | large number + bar | **h-2** bar |
| Key Metrics | `MetricsGrid` | **2 col** grid of `MetricItem` |
| `MetricItem` | `div.rounded-md...p-3` | label + value + optional badge | **~330 × ~88** per cell (varies) |
| Decision Summary | `DecisionSummary` section | recommendation, confidence, reasons | **~full column × ~200+** |

### Footer actions

| Component | Selector | Visible text | Approx center (footer row) | Size |
|-----------|----------|--------------|----------------------------|------|
| Cancel | `footer button` (white) | “Cancel” | ~(1010, 820) | **~72 × 32** |
| Modify & Approve | `footer button.bg-amber-500` | “[~] Modify & Approve” | ~(1095, 820) | **~140 × 32** |
| Reject | `footer button.bg-rose-600` | “[x] Reject” | ~(1195, 820) | **~88 × 32** |
| Approve | `footer button.bg-emerald-600` | “[+] Approve” | ~(1285, 820) | **~88 × 32** |

**Modal panel:** `max-w-[1200px]`, `rounded-xl`; content grid `max-h-[74vh]` → on 900px viewport, body **~666px** max height.

---

## Related: `/applications` row modal (`ApplicationReviewModal`)

When a **table row** is clicked on `/applications`, `ApplicationReviewModal` opens (different from `ApplicationDetailModal`). It uses **`MacWindowCard`** and detailed read-only sections; it does not expose the same Approve/Reject/Modify footer as `ApplicationDetailModal`. Reference: `frontend/components/Application/ApplicationReviewModal.tsx`.

---

## Suggested `data-testid` hooks (not present today)

For stable automation, consider adding:

| Location | Suggested id |
|----------|----------------|
| TaskBar | `taskbar`, `taskbar-link-overview`, `taskbar-link-hil`, `taskbar-link-apps` |
| Overview KPI | `kpi-applications-today`, … |
| Applications search | `applications-search` |
| Applications table row | `application-row-{id}` |
| HIL lane card | `hil-card-{applicationId}` |
| Modal | `hil-modal`, `hil-modal-approve`, `hil-modal-reject`, `hil-modal-modify` |

---

## File reference (primary components)

| Screen | Files |
|--------|--------|
| `/` | `frontend/app/page.tsx`, `frontend/app/components/DesktopLandingPage.tsx`, `frontend/app/components/TaskBar.tsx`, `frontend/app/components/AppIcon.tsx` |
| `/overview` | `frontend/app/overview/page.tsx`, `frontend/components/Dashboard/CompactDashboard.tsx`, `frontend/components/Dashboard/CompactKPICard.tsx`, `frontend/components/Dashboard/compact/constants.ts` |
| `/applications` | `frontend/app/applications/page.tsx`, `frontend/components/Dashboard/Charts.tsx`, `frontend/components/Dashboard/ApplicationsTable.tsx`, `frontend/components/ui/MacWindowCard.tsx` |
| `/applications/:id` | `frontend/app/applications/[id]/page.tsx`, `ApplicationHeader.tsx`, `ApplicationSummary.tsx`, `Timeline.tsx`, `TimelineStep.tsx` |
| `/hil-review` | `frontend/app/hil-review/page.tsx`, `frontend/components/Hil/HilReviewClient.tsx` |
| HIL modal | `frontend/components/Application/ApplicationDetailModal.tsx`, `BorrowerProfile.tsx`, `EventTimeline.tsx`, `MetricsGrid.tsx`, `MetricItem.tsx`, `DecisionSummary.tsx` |
