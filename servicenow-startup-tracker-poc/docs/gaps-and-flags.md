# Gaps and flags — `x_bst_startuptrk`

This document discharges the obligation of **prompt section 11.0**: *flag any requirement with no clean ServiceNow equivalent rather than silently omitting or half-implementing it.* It is the **single collection point** for that obligation across the whole package. Every requirement that the ServiceNow scoped application `x_bst_startuptrk` does not implement, implements only through a named workaround, or excludes outright is listed here — with its source, the platform's position on it, and what was consequently done.

**Read this document before reporting any part of the package as complete.** Seven of the nineteen flags below are places where the delivery is **less**, or more conditional, than a first reading of the requirements would suggest, and three of those carry the `Partially implemented, flagged` disposition — a requirement met in part that must never be claimed as met in full. Counts of delivered artifacts elsewhere in the package are counts of **artifacts**, not assertions that every requirement behind them is satisfied; where the two differ, this document governs.

The inventory is exhaustive by construction. A requirement that is neither implemented nor listed in this document is an unexplained omission, and the bidirectional traceability matrix cannot close without it. **No list below is abbreviated:** every excluded requirement, every unresolved gap and every untouched artifact is named individually, and no entry closes with an open-ended terminator standing in for items it does not name.

**On the word "exhaustive".** It is a claim about a construction, not about omniscience: every requirement was walked, and each one is either implemented, or listed here. Five entries were added **after** the artifacts were first delivered, when they were checked against the real provider contracts and the binding field list — which is precisely the case the claim has to survive. A reader who finds a sixth should treat its absence as a defect in this document rather than as evidence that the shortfall was intended.

**Authority.** The frozen prompt and the Agent Action Plan are authoritative for all application content. This document is authoritative for one thing only: **which requirements are unimplemented, worked around or excluded, and on what factual basis.** Where a requirement is implemented, the document that owns it is authoritative for how — [`./data-model.md`](./data-model.md) for the schema, [`./access-control.md`](./access-control.md) for authorization, [`./api-reference.md`](./api-reference.md) for the API surface, and the six guides indexed by [`./manual-build-instructions.md`](./manual-build-instructions.md) for everything built by hand. Every identifier used below — table name, column name, role name, property key, page name, widget name, gap identifier — matches those documents character for character. No variant spelling is valid.

This document carries **no rationale**. It states what each requirement is, where it comes from, what the platform offers or does not offer, and what was done. Every decision behind those outcomes, every alternative considered and every risk each carries is recorded in [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md), which is the single source of truth for "why". Each entry below ends with a pointer to that log, and the pointer does the work.

**Reviewer.** Three of the call-out categories that [`../../docs/review/CRITICAL_DECISIONS.md`](../../docs/review/CRITICAL_DECISIONS.md) is required to raise intersect this inventory: the authorization decision, recorded here as [F10](#f10--the-administrator-access-control-override), and the ambiguity resolutions, recorded here as [F6](#f6--inclusion-criteria-field-ambiguity--resolved) and under [Ambiguity resolutions besides F6](#ambiguity-resolutions-besides-f6). That document's five entries are not reproduced here.

## Referenced documents

**Every document named below is delivered and readable.** Each link resolves to a file in this repository, so a reader can follow any of them and read the content the statement around it describes; no link is a forward reference to something still to be written.

| Document | What it supplies to this inventory |
| --- | --- |
| [`./data-model.md`](./data-model.md) | The ten tables field by field, the closed field list, the seven premium-gated columns, and the two columns the startup inclusion criteria test. |
| [`./access-control.md`](./access-control.md) | The three roles, the premium field matrix, the `admin_overrides` posture and the impersonation procedure. |
| [`./api-reference.md`](./api-reference.md) | The physical base path, the six resources and the thirty-one operations. |
| [`./manual-build-instructions.md`](./manual-build-instructions.md) | The split between Update Set metadata and hand-built artifacts, and the execution order of the six guides. |
| [`./manual-build/02-flow-crunchbase-ingestion.md`](./manual-build/02-flow-crunchbase-ingestion.md) | The cadence guard, and the definition of a scheduled run. |
| [`./manual-build/03-flow-linkedin-ingestion.md`](./manual-build/03-flow-linkedin-ingestion.md) | The same guard on the second flow. |
| [`./manual-build/04-service-portal-pages-and-widgets.md`](./manual-build/04-service-portal-pages-and-widgets.md) | The five pages, the eight widgets, the query-parameter routing, the 1024-pixel floor and the build mechanics of gaps G1 through G5 and G7. |
| [`./manual-build/06-staging-table-csv-import.md`](./manual-build/06-staging-table-csv-import.md) | The six CSV files, and the absence of a seventh for news articles. |
| [`./deployment-runbook.md`](./deployment-runbook.md) | The import route, the post-commit gates, and the definition of a scheduled run. |
| [`./validation-gates.md`](./validation-gates.md) | The eleven required post-commit gates, the acceptance-required `GATE-COL-01`, the three non-normative diagnostics, and the external instance prerequisite for XML entity resolution. |
| [`./validation-checklist.md`](./validation-checklist.md) | The evidence record for the five success criteria, including criterion 2 for the access-control checks and criterion 4 for the scheduled runs. |
| [`../sample-data/README.md`](../sample-data/README.md) | The fallback-only posture of the sample dataset. |
| [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md) | The single source of truth for every "why" behind every entry in this document. |
| [`../../docs/decisions/TRACEABILITY_MATRIX.md`](../../docs/decisions/TRACEABILITY_MATRIX.md) | The bidirectional matrix this inventory closes the unimplemented half of. |
| [`../../docs/review/CRITICAL_DECISIONS.md`](../../docs/review/CRITICAL_DECISIONS.md) | The five risk-ordered review entries, three of whose call-out categories intersect this inventory. |

## Numbering convention

**Four identifier schemes appear on this page, and the first two are easily confused.** Read the padding.

| Scheme | Form | Meaning | Examples |
| --- | --- | --- | --- |
| **This document's flag identifiers** | `F` followed by **one or two** digits, never zero-padded | A flag in this inventory. There are exactly nineteen, `F1` through `F19`. | `F1`, `F6`, `F13`, `F19` |
| **Source requirement identifiers** | `F` followed by **three** zero-padded digits, optionally then a hyphen and a sub-number | A feature or a requirement in the source requirements document, `documentation/Software Requirements Specifications (SRS).md`. There are ten features, `F001` through `F010`, each carrying five requirements. | `F009`, `F009-5`, `F010-1`, `F001-1`, `F003-3`, `F006-4`, `F007-5` |
| **Design-system gap identifiers** | `G` followed by one digit | A gap in the user-interface design system. There are exactly seven, `G1` through `G7`. | `G1`, `G6`, `G7` |
| **Open integration limitation identifiers** | `OPEN-` followed by one digit | A capability built in full that cannot be exercised against its live source until a third party supplies missing information. There is exactly one, and it is **not** a flag and **not** counted into the twelve. | `OPEN-1` |

Every source requirement identifier in this document is written in its three-digit padded form. `F1` is this document's first flag; `F001` is the source document's first feature; `F001-1` is that feature's first requirement. The three are distinct and are never interchangeable.

Source requirement identifiers are cited as `SRS:L<line>` against `documentation/Software Requirements Specifications (SRS).md`. Repository source files are cited as `<path>:L<line>` or `<path>:L<first>-L<last>`.

## Dispositions

Every **flag** in this document carries exactly one of three dispositions. The single open integration limitation, `OPEN-1`, uses its own disposition vocabulary and is stated under [Open integration limitations](#open-integration-limitations).

| Disposition | Meaning |
| --- | --- |
| **Flagged, not implemented** | No platform equivalent exists. The requirement is not built, and it is not partially built. |
| **Resolved by documented workaround** | A platform equivalent exists only indirectly. The requirement is met by a named mechanism that is specified in a document of this package. |
| **Partially implemented, flagged** | The requirement is met in part and cannot be met in full, and the shortfall is **specific, bounded and observable** — the entry names exactly which part is unmet and where the shortfall is counted or logged at run time. This disposition exists because prompt section 11.0 forbids **silently** half-implementing a requirement, not half-implementing one; an entry here is the opposite of silence. Anything carrying it is reported as partial wherever its status is claimed, and never as implemented. |
| **Consciously excluded** | The requirement has no counterpart in the authoritative prompt. It is not built, and its absence is recorded so that it reads as a decision rather than an oversight. |
| **Blocked on an external prerequisite** | The requirement **is** built, and it cannot be exercised or validated until a named artifact that this work cannot create comes into existence. The build is complete; the evidence is not obtainable. A blocker is not a workaround and must never be recorded as one — the distinction is what stops a blocked capability being reported as a working one. |

## Flag summary

Nineteen flags. Every one has a detail section below. Twelve were identified as the artifacts were designed; **F13** through **F17** were identified as the delivered artifacts were reviewed against the real provider contracts and the binding field list; and **F18** and **F19** were identified as the delivered artifacts were reviewed against the frozen artifact inventories. Each of the last seven is a place where the delivery is **less**, or more conditional, than a first reading of the requirements would suggest. They are listed here for the same reason as the first twelve: an unrecorded shortfall is the failure mode prompt section 11.0 exists to prevent.

| ID | Requirement | Disposition | Detail |
| --- | --- | --- | --- |
| **F1** | Premium subscription billing and payment processing | **Flagged, not implemented** | [F1](#f1--premium-subscription-billing-and-payment-processing) |
| **F2** | Automatic entitlement transition from base user to premium user upon payment | **Flagged, not implemented** | [F2](#f2--automatic-entitlement-transition-on-payment) |
| **F3** | Runtime-configurable flow schedule interval, 6 to 48 hours | **Resolved by documented workaround** | [F3](#f3--runtime-configurable-flow-schedule-interval) |
| **F4** | Path-style portal routes, the legacy `/company/:id` URL form | **Resolved by documented workaround** | [F4](#f4--path-style-portal-routes) |
| **F5** | A namespace-free API base path | **Flagged, not implemented** | [F5](#f5--a-namespace-free-api-base-path) |
| **F6** | Inclusion-criteria field ambiguity over `institutional_funding_last_5yrs` | **Resolved by documented workaround** | [F6](#f6--inclusion-criteria-field-ambiguity--resolved) |
| **F7** | Design-system component gaps, G1 through G5 | **Resolved by documented workaround** | [F7](#f7--design-system-component-gaps) |
| **F8** | An administrative console as a portal route | **Resolved by documented workaround** | [F8](#f8--an-administrative-console-as-a-portal-route) |
| **F9** | Three source requirements with no prompt counterpart: `F001-1`, `F003-3`, `F007-5` | **Consciously excluded** | [F9](#f9--srs-requirements-with-no-prompt-counterpart) |
| **F10** | Verifiable field-level access-control enforcement, given that record access controls carry an administrator override | **Resolved by documented workaround** | [F10](#f10--the-administrator-access-control-override) |
| **F11** | Geographic distribution maps, `F009-5`, and growth-rate comparisons, `F009-3` | **Consciously excluded** | [F11](#f11--geographic-distribution-maps) |
| **F12** | The entire Notification System feature, `F010`, all five requirements | **Consciously excluded** | [F12](#f12--the-notification-system-feature) |
| **F13** | Cleaning rule 3's coercion of an unmatched choice value to "Other", in the six delivered choice lists that declare no such member | **Partially implemented, flagged** | [F13](#f13--cleaning-rule-3s-other-coercion-in-six-choice-lists) |
| **F14** | An authenticated Crunchbase call through a Basic-authentication alias, which that provider does not accept in any form | **Resolved by documented workaround** | [F14](#f14--the-crunchbase-authentication-model) |
| **F15** | Live acquisition of Founder, Executive and Job posting records from LinkedIn | **Partially implemented, flagged** | [F15](#f15--linkedin-publishes-no-read-api-for-people-or-third-party-job-postings) |
| **F16** | Three columns the live provider path cannot fill: `startup.institutional_funding_last_5yrs`, `investor.aum_usd` and `fundinground.source_url` | **Partially implemented, flagged** | [F16](#f16--three-columns-the-live-path-cannot-fill) |
| **F17** | A funding round with more than one lead investor, which the provider reports and the binding field list cannot represent | **Flagged, not implemented** | [F17](#f17--a-round-with-several-lead-investors) |
| **F18** | Both flows calling their provider through a generic Flow Designer REST step, which one of two instance conditions may not permit | **Resolved by documented workaround** | [F18](#f18--the-outbound-path-branch-between-the-rest-step-and-a-scoped-script-step) |
| **F19** | Retention, minimisation or data-subject erasure of the verbatim upstream payload and person data staged in `x_bst_startuptrk_ingest_staging` | **Flagged, not implemented** | [F19](#f19--no-retention-minimisation-or-data-subject-erasure-of-staged-data) |

By disposition: five are **flagged, not implemented** — F1, F2, F5, F17 and F19; eight are **resolved by documented workaround** — F3, F4, F6, F7, F8, F10, F14 and F18; three are **partially implemented, flagged** — F13, F15 and F16; three are **consciously excluded** — F9, F11 and F12. Five plus eight plus three plus three is nineteen.

**One further item is recorded on this page and is deliberately not among the numbered flags:** [`OPEN-1`](#open-1--live-linkedin-ingestion-pending-an-endpoint-contract-declaration), the open integration limitation covering live LinkedIn ingestion. It is not a flag because the requirement is not unsatisfiable by the platform — the capability is built in full and runs in `fallback` mode; what is missing is an endpoint contract only the credential owner can declare. It is listed under [Open integration limitations](#open-integration-limitations) and it carries the `OPEN-` prefix so it can never be counted into the flag inventory.

Three flags are marked for prominence because a later reader acting on a partial understanding of any of them would introduce a defect: **[F6](#f6--inclusion-criteria-field-ambiguity--resolved)**, which must not be "corrected" by adding the premium-gated column to the inclusion predicate; **[F10](#f10--the-administrator-access-control-override)**, which invalidates any access-control verification performed as the instance administrator; and **[F19](#f19--no-retention-minimisation-or-data-subject-erasure-of-staged-data)**, which means an operator who runs a live ingestion and does not clear the staging table has left verbatim upstream person data on the instance indefinitely.

## The nineteen flags

Each section below states five things in the same order: **the requirement**, **its source** with a citation, **the platform position**, **the disposition**, and **the decision-log pointer** that carries the "why".

### F1 — Premium subscription billing and payment processing

**The requirement.** Charge a subscriber for premium access: present a price, take a payment, hold a subscription, renew it, and cancel or lapse it.

**The source.** The source requirements document asks for this in three places, and the project proposal and the technical specification each name the mechanism.

| Citation | Text as it appears |
| --- | --- |
| `SRS:L446` | Requirement `F006-4`, "Implement subscription management system" |
| `SRS:L107` | "7. Payment Gateways: For processing premium subscription payments (handled by third-party services)." |
| `SRS:L255` | "9. Successful integration with chosen payment gateway for premium subscriptions." — a stated success criterion |
| `documentation/Software Project Proposal.md:L165-L166` | "3. Financial Transactions" / "Processing payments for premium subscriptions will be handled by a third-party service" |
| `documentation/Technical Specifications.md:L486` | Names Stripe as the payment gateway, "Easy integration for subscription management" |

Two of those five place the capability outside the system being built: `SRS:L107` frames payment gateways as third-party services, and the project proposal states the same. The technical specification names an external provider rather than an internal component.

**The platform position.** **There is no equivalent whatsoever.** The Now Platform grants entitlement through **roles**, and it has no commerce capability: no product catalogue with a price, no cart, no checkout, no payment-gateway integration, no card handling, no invoice, no subscription lifecycle and no dunning. Nothing in the platform's own feature set stands in for any part of the requirement, and nothing in this application substitutes for it.

**Disposition — flagged, not implemented, and not half-implemented.** No billing table exists in the `x_bst_startuptrk` scope. No price, currency, plan, invoice, transaction, card, customer-identifier or subscription-state column exists on any of the ten tables of [`./data-model.md`](./data-model.md). No REST resource in [`./api-reference.md`](./api-reference.md) accepts or returns a payment. No portal widget renders a price, a plan comparison or a checkout control, and [`./manual-build/04-service-portal-pages-and-widgets.md`](./manual-build/04-service-portal-pages-and-widgets.md) instructs the build to publish nothing about billing, payment, price or checkout. No flow, business rule or scheduled job touches an entitlement period. The requirement is absent in full rather than present in part.

This flag is also design-system gap **G6** in the [Design-system gap inventory](#design-system-gap-inventory), which is the only one of the seven gaps with no resolution.

The consequent entitlement path is recorded in [F2](#f2--automatic-entitlement-transition-on-payment).

**Decision log.** [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md).

### F2 — Automatic entitlement transition on payment

**The requirement.** On successful payment, a caller holding the base role becomes entitled to the premium dataset without administrative action; on lapse or cancellation, the entitlement is withdrawn the same way.

**The source.** Requirement `F006-4` at `SRS:L446`, read together with the three role tiers at `SRS:L77`, "Role-based access control (free users, premium subscribers, administrators)". The transition between the first two tiers is the subject of this flag.

**The platform position.** The entitlement itself exists and works: `x_bst_startuptrk.premium_user` is a real role, and holding it grants read access to all seven premium-gated columns exactly as the matrix in [`./access-control.md`](./access-control.md) specifies. What has no platform equivalent is the **trigger** for granting it. This flag depends entirely on [F1](#f1--premium-subscription-billing-and-payment-processing): there is no payment event on the instance for a rule to react to, so there is nothing for an automatic transition to be automatic about.

**Disposition — flagged, not implemented.** The delivered Update Set contains three `sys_user_role` definitions and **zero** `sys_user_has_role` assignments, and no business rule, flow or Script Include in the application grants, revokes or schedules the expiry of a role. `sys_user` and `sys_user_has_role` sit outside the `x_bst_startuptrk` scope, and prompt section 6.0 forbids modifying anything outside it.

**The operational path.** Entitlement is granted **manually**: an administrator adds `x_bst_startuptrk.premium_user` to the person's `sys_user` record on the instance, and removes it to withdraw entitlement. That act takes effect immediately on both surfaces, because both consult the caller's effective roles on every read. The role, its capability and the seven columns it unlocks are specified in [`./access-control.md`](./access-control.md).

**Decision log.** [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md).

### F3 — Runtime-configurable flow schedule interval

**The requirement.** The two ingestion flows run on a cadence that is **configurable between 6 and 48 hours, with a default of 24** — configurable at run time, without editing the flow.

**The source.** Prompt section 4.0. The bound values and the default are stated there and are transcribed unchanged into the property inventory of [`./api-reference.md`](./api-reference.md).

**The platform position.** A Flow Designer **scheduled trigger takes a fixed interval and cannot read a system property at run time.** The interval is part of the trigger's own configuration, so a cadence expressed as a property is not natively expressible: changing it would mean editing and re-publishing the flow, which is not run-time configuration.

**Disposition — resolved by documented workaround.** The trigger repeats **hourly**, and the flow's **first action after the trigger** is a cadence guard. The guard compares the elapsed time since the last successful run — held in the durable property `x_bst_startuptrk.ingestion.last_run_provenance`, which carries one `source=provenance|state|stamp|run` marker per source system and is read through `AppProperties.getLastSuccessAt(source)`, rather than derived from a log record that a severity threshold or a retention window could remove — against `x_bst_startuptrk.ingestion.cadence_hours`, whose value `AppProperties` clamps to the range 6 to 48 and which ships at 24. **One property carries both sources' markers**, which holds the property inventory at the eleven Agent Action Plan section 0.4.7 declares while keeping the two cadences independent. When the configured interval has not elapsed, the execution exits before doing any work. The cadence therefore changes at run time by editing one property, which is what the requirement asks for. The guard is built per [`./manual-build/02-flow-crunchbase-ingestion.md`](./manual-build/02-flow-crunchbase-ingestion.md) and [`./manual-build/03-flow-linkedin-ingestion.md`](./manual-build/03-flow-linkedin-ingestion.md), and the property is one of the eleven in [`./api-reference.md`](./api-reference.md).

**The operational consequence.** Because the trigger fires hourly and the guard admits one execution per cadence window, most executions do no work. The number of no-op executions between two consecutive scheduled runs is one fewer than the configured cadence in hours: **23 at the shipped cadence of 24 hours**, 5 at the minimum of 6, and 47 at the maximum of 48.

**Consequently, a "scheduled run" means an execution that passed the cadence guard.** An execution that started, found the cadence had not elapsed and exited without ingesting is a no-op: it is not a scheduled run, it does not count towards the three consecutive runs the fourth success criterion requires, and it must not appear in that criterion's evidence. The same definition is stated in [`./deployment-runbook.md`](./deployment-runbook.md), in both flow guides, and in criterion 4 of [`./validation-checklist.md`](./validation-checklist.md).

**Decision log.** [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md).

### F4 — Path-style portal routes

**The requirement.** Five portal routes, addressed as URL **paths** with the record identifier as a path segment, in the form the legacy single-page application used.

**The source.** The five legacy routes are declared at `src/frontend/App.tsx:L29-L37`:

| Legacy path | Component |
| --- | --- |
| `/` | Home |
| `/search` | Search |
| `/company/:id` | Company |
| `/investor/:id` | Investor |
| `/user/:id` | User |

Prompt section 5.0 mandates **five routes**. It does not mandate their **URL syntax**.

**The platform position.** Service Portal addresses a page by **query parameter**, not by path: a page is reached as `?id=<page>` on the portal's URL suffix, and a record-scoped page adds `&sys_id=<record>`. The portal suffix of this application is `bst`, so every link is rooted at `/bst`. Reproducing `/company/:id` as a path would require URL rewriting in front of the platform, which is infrastructure outside the scoped application.

**Disposition — resolved by documented workaround, and recorded as a deviation.** All five routes are delivered as five `sp_page` records — `bst_home`, `bst_company`, `bst_investor`, `bst_dashboard` and `bst_account` — addressed by query parameter. The route count and the navigable surface satisfy the requirement; the URL form deviates from the legacy path style. The mapping is not one-for-one in either direction: the legacy tree had two routes over search-related surfaces and no dashboard route, while the target has one Home / Search page and one Dashboard / Trends page, and the legacy `/user/:id` becomes `bst_account`. The addressing scheme, the page names and the link construction are specified in [`./manual-build/04-service-portal-pages-and-widgets.md`](./manual-build/04-service-portal-pages-and-widgets.md).

**Decision log.** [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md).

### F5 — A namespace-free API base path

**The requirement.** Serve the REST API under the base path `/api/v1/`.

**The source.** Prompt section 3.0 states the logical base path `/api/v1/` and, in the same clause, names the API namespace `x_bst_startuptrk`. The logical form has a provenance in the legacy tree: `src/shared/constants.ts:L2` declares `export const API_BASE_URL = '/api/v1';`.

**The platform position.** **A scoped Scripted REST API always carries its namespace segment in its base path.** The namespace is not optional and cannot be removed, so `/api/v1/` cannot be served by a scoped application. The logical path resolves **physically** to `/api/x_bst_startuptrk/v1/`. The prompt's own phrasing anticipates this by naming the namespace alongside the version.

**Disposition — flagged, not implemented.** The logical path is **not served and does not resolve.** No route, alias, rewrite or compatibility shim maps it to the physical path, and none is built. Every consumer calls:

```text
https://<instance>.service-now.com/api/x_bst_startuptrk/v1/<resource>
```

Every path template in [`./api-reference.md`](./api-reference.md) is relative to that physical base, so `GET /startups` means `GET /api/x_bst_startuptrk/v1/startups`. **No consumer may be written against the logical form.**

**Decision log.** [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md).

### F6 — Inclusion-criteria field ambiguity — resolved

> **Marked for prominence.** This entry records a resolved ambiguity. The predicate below is the delivered predicate. **Do not "correct" it by adding `institutional_funding_last_5yrs` to it.**

**The requirement, and the ambiguity in it.** The column `x_bst_startuptrk_startup.institutional_funding_last_5yrs` appears in **two** lists in the prompt:

| List | Section | What membership of that list implies |
| --- | --- | --- |
| The fields associated with the startup inclusion criteria | Prompt section 1.1 | That the column participates in the eligibility predicate |
| The premium-gated fields | Prompt section 2.0 | That a caller holding only `x_bst_startuptrk.user` is denied read access to the column |

Read together, the two memberships are in tension: a predicate cannot test a column its caller may not read.

**The source.** Prompt section 1.1's **operative rule text** names two conditions and no third. Its antecedents are in the source requirements document as the two data constraints at `SRS:L218`, "Limited to startups headquartered in Boston area", and `SRS:L219`, "Focus on companies that have raised institutional money in the past 5 years".

**The platform position.** The inclusion criteria and the field gate are **two different mechanisms that the platform evaluates independently**. The criteria are a **query filter**: the application builds them into the query, and the platform does not apply them of its own accord. The gate is a **field-level read ACL**: the platform applies it on the access-controlled read path and returns nothing for a denied field. A column a caller may not read therefore cannot serve as a predicate term for that caller — the filter would have no readable value to test — and the platform offers no mechanism that makes a denied field testable in a caller's own query.

**The resolution — the filter tests exactly two columns.** A startup is eligible for Service Portal search results only if:

> `active` = true **AND** `headquarters_location` contains **"Boston"** OR **"Cambridge, MA"** (case-insensitive substring).

`x_bst_startuptrk_startup.institutional_funding_last_5yrs` is **not** part of that predicate. It remains a premium-gated **display** attribute: a value shown to callers entitled to read it, and omitted from the response for callers who are not. `StartupSearchService` is the single Script Include that builds the query, and the two location tokens are read from `x_bst_startuptrk.inclusion.location_tokens`. The predicate, its construction and its application to both the page and the count are specified in [`./data-model.md`](./data-model.md); the field gate is specified in [`./access-control.md`](./access-control.md).

**The concrete consequence.** The base role `x_bst_startuptrk.user` cannot read `institutional_funding_last_5yrs` — the field-level read ACL denies it, and the value is omitted rather than nulled. A predicate depending on that column would therefore be unbuildable for that role: the portal list on the Home / Search route could not evaluate the predicate for a caller holding only `x_bst_startuptrk.user`, which is every caller who is not an administrator and not entitled to the premium dataset.

**Disposition — resolved by documented workaround.** The predicate is delivered as stated, over `active` and `headquarters_location` only. Records failing the criteria remain in the table for administrative visibility and are excluded from all portal-facing and non-administrative list and search queries.

**Decision log.** [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md).

### F7 — Design-system component gaps

**The requirement.** Build the five-route portal experience from Service Portal widgets and Bootstrap components. UI Builder is forbidden by prompt section 5.0, so no `sys_ux_*` record of any kind is authored.

**The source.** Prompt section 5.0 for the mandate, and the legacy component vocabulary for the elements needing an equivalent: the Material-UI v4 set imported across `src/frontend/components/`, including the card, card-media, tabs, circular-progress and typography components.

**The platform position.** Service Portal's design system is **AngularJS with Bootstrap 3.3.6**, which is platform-native, is not installable and has no npm or PyPI identity. Five of the elements the portal needs have **no component in that library**: a chart, a multi-select chip input, a spinner, a card-media surface and a paywall treatment.

**Disposition — resolved by documented workaround, all five inside the design system.** The five are recorded as gaps **G1** through **G5** in the [Design-system gap inventory](#design-system-gap-inventory), each with the platform mechanism that resolves it and the widget that carries it. No gap is left as a placeholder and none is resolved by importing an outside library. The build mechanics are in [`./manual-build/04-service-portal-pages-and-widgets.md`](./manual-build/04-service-portal-pages-and-widgets.md).

Two further gaps are recorded in the same inventory and are **not** covered by this flag: **G6**, premium billing and checkout, which has no resolution and is [F1](#f1--premium-subscription-billing-and-payment-processing); and **G7**, the icon-system split, which is not a missing component.

**Decision log.** [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md).

### F8 — An administrative console as a portal route

**The requirement.** An administrative interface for managing the platform — managing user accounts and roles, correcting startup data, monitoring system health, viewing platform usage statistics, and managing API keys and rate limits.

**The source.** The source requirements document asks for it as feature `F008`, "Administrative interface for managing the platform and monitoring system health", and names a console in three further places.

| Citation | Text as it appears |
| --- | --- |
| `SRS:L463` | "8. Admin Dashboard" |
| `SRS:L858` | "8. Admin Panel" |
| `SRS:L871` | "[Admin Panel Mockup]" |

**The platform position.** Prompt section 5.0 enumerates **exactly five** portal routes — Home / Search, Company Profile, Investor Profile, Dashboard / Trends and Account Management — and **none of them is an administrative console.** A sixth route is therefore not authored. Separately, the platform already supplies an administrative surface for a scoped application: its own list and form views, reached through the application menu, with the access-control records deciding what each caller may do there.

**Disposition — resolved by documented workaround, and flagged as a conscious non-implementation of the source feature.** The administrative need is served by the platform's **native list and form views inside the scoped application**, reachable by a holder of `x_bst_startuptrk.admin`. The delivered Update Set ships, for that purpose:

| Artifact | Count in the delivered Update Set | Coverage |
| --- | --- | --- |
| Default form section, `sys_ui_section` | 10 | One per table — all seven entity tables and all three supporting tables |
| Default list view, `sys_ui_list` | 10 | One per table, same coverage |
| Application menu, `sys_app_application` | 1 | "Boston Startup Tracker" |
| Application module, `sys_app_module` | 9 | Startups, Investors, Founders, Executives, Funding rounds, Job postings, News articles, Ingestion staging, System properties |

Those views are usable the moment the Update Set commits, which is what serves feature `F008` without a sixth portal route. The **News articles** module is additionally the manual-entry surface for the one entity no flow ingests.

**What is not delivered.** No custom administrative portal route, page or widget exists. Of feature `F008`'s five requirements, `F008-1` account and role management is a platform concern outside the application scope, `F008-2` manual data correction is served by the native form views above, and `F008-3` health monitoring, `F008-4` platform usage analytics and `F008-5` API-key management have no counterpart in the authoritative prompt and are **consciously excluded**; the rate-limit half of `F008-5` is configured through the two `x_bst_startuptrk.rest.rate_limit_*` properties rather than through an interface. The tables, columns and modules are specified in [`./data-model.md`](./data-model.md); the properties are in [`./api-reference.md`](./api-reference.md).

**Decision log.** [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md).

### F9 — SRS requirements with no prompt counterpart

**The requirement.** Three requirements of the source requirements document, each stated there and each without a counterpart in the authoritative prompt.

| Source requirement | Citation | Text as it appears |
| --- | --- | --- |
| `F001-1` | `SRS:L373` | "Develop web crawlers to collect data from specified public sources" |
| `F003-3` | `SRS:L403` | "Create saved search functionality for registered users" |
| `F007-5` | `SRS:L461` | "Create scheduled report delivery system for premium users" |

**The platform position and what was done, requirement by requirement.**

**`F001-1`, web crawlers.** The prompt names **only** Crunchbase and LinkedIn as data sources, and requires no scraping of any kind. The legacy tree carries four crawler modules, and all four are dropped:

| Legacy module | Class |
| --- | --- |
| `src/data_collection/scrapers/startup_scraper.py` | `StartupScraper` |
| `src/data_collection/scrapers/investor_scraper.py` | `InvestorScraper` |
| `src/data_collection/scrapers/job_scraper.py` | `JobScraper` |
| `src/data_collection/scrapers/news_scraper.py` | `NewsScraper` |

No flow, Script Include, business rule or scheduled job in `x_bst_startuptrk` fetches or parses an HTML page. The two ingestion flows call the two named APIs through **generic Flow Designer REST steps bound to a credential alias by name — the primary path — with a scoped script step resolving the same alias by name as the documented fallback**, the arm being selected per source by the two conditions of [F18](#f18--the-outbound-path-branch-between-the-rest-step-and-a-scoped-script-step) — for Crunchbase, whose key cannot travel in a header the connection populates, that selection is the scoped script arm, per [`./manual-build/02-flow-crunchbase-ingestion.md`](./manual-build/02-flow-crunchbase-ingestion.md) and [`./manual-build/03-flow-linkedin-ingestion.md`](./manual-build/03-flow-linkedin-ingestion.md). Neither arm is a spoke; the branch is [F18](#f18--the-outbound-path-branch-between-the-rest-step-and-a-scoped-script-step).

**`F003-3`, saved search.** The binding field list declares **no saved-search entity**: no saved-search table, no stored-query column and no per-user search-history record exists on any of the ten tables of [`./data-model.md`](./data-model.md), and prompt section 1.0's field definitions are closed, so none may be added. Search filters are supplied per request — as query parameters on the `/startups` list operation in [`./api-reference.md`](./api-reference.md), and as widget inputs on the Home / Search route — and are not persisted.

**`F007-5`, scheduled report delivery.** No report definition, subscription, delivery schedule or outbound email is authored in the application. The one scheduled job the Update Set ships is the rate-limit counter prune; it does not deliver a report.

**Disposition — consciously excluded, all three.** They are recorded here so that their absence reads as a decision rather than an oversight. Their positions in the feature roll-up are shown in [SRS feature coverage roll-up](#srs-feature-coverage-roll-up).

**Decision log.** [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md).

### F10 — The administrator access-control override

> **Marked for prominence.** This is not a platform gap. It is a gap in any naive verification procedure, and acting on the naive procedure produces evidence that is worthless.

**The requirement.** Prompt section 10.0 criterion 2: field-level access control on all seven premium-gated fields, **verified per role per field**.

**The source.** Prompt section 2.0 for the enforcement requirement and prompt section 10.0 criterion 2 for the verification requirement. The seven fields and the three roles are enumerated in [`./access-control.md`](./access-control.md).

**The platform position, and the failure mode it creates.** Record access controls carry `admin_overrides` **true** by default, and all **49** access controls in this application carry it. **The platform administrator role therefore overrides every one of them, and every operator of a Personal Developer Instance holds that role.**

The consequence is a false positive that looks exactly like a pass: a walkthrough performed while signed in as the instance administrator **displays all seven premium fields** and appears to prove enforcement **that has not been tested at all**. Nothing in the result distinguishes correct enforcement from no enforcement. Note also that the scoped role `x_bst_startuptrk.admin` and the platform administrator role are **different roles**; holding the scoped one does not carry the override.

**Disposition — resolved by documented workaround.** Verification is performed **under impersonation, never as the instance administrator**:

1. Create three purpose-built users, each holding **exactly one** of `x_bst_startuptrk.admin`, `x_bst_startuptrk.premium_user` and `x_bst_startuptrk.user`, and **none** of the elevated platform roles — not the platform `admin` role, not `security_admin`, not `maint`.
2. Impersonate each user in turn.
3. Assert all **21** outcomes, the full cross-product of the seven premium fields by the three roles.
4. Confirm a denied field's key is **absent from** the response object rather than present with a null or an empty string.
5. Confirm both access-control layers are load-bearing by reading a non-premium column in the same call under the base role.

The three users are created by Automated Test Framework setup steps at run time rather than shipped in the Update Set, because `sys_user` sits outside the application scope. The full procedure is in [`./access-control.md`](./access-control.md), the suite that executes it is built per [`./manual-build/05-atf-test-suites.md`](./manual-build/05-atf-test-suites.md), and the evidence is recorded against criterion 2 of [`./validation-checklist.md`](./validation-checklist.md).

**Any access-control result obtained without impersonation must not be recorded as evidence.** This is the point the **Security** reviewer entry in [`../../docs/review/CRITICAL_DECISIONS.md`](../../docs/review/CRITICAL_DECISIONS.md) is required to check above all others.

**Decision log.** [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md).

### F11 — Geographic distribution maps

**The requirement.** Requirement `F009-5`, "Create geographic distribution maps of Boston startups" — a map surface plotting tracked startups by location.

**The source.** `SRS:L489`, inside feature `F009` "Data Visualization", whose identifier `ID: F009` is declared at `SRS:L479` and whose description reads "Interactive charts and graphs to visualize startup ecosystem trends."

**The platform position.** **No geographic field exists in the binding schema.** `x_bst_startuptrk_startup.headquarters_location` is a plain `string` of maximum length 100: a free-text place name carrying no latitude, no longitude, no coordinate pair and no geographic platform type. The delivered Update Set declares no latitude, longitude, coordinate or geolocation column on any of its ten tables. Prompt section 1.0's field definitions are **binding and complete**, so no geographic attribute may be added to satisfy this requirement, and no derivation exists from a free-text place name to a plottable coordinate inside the application.

**Disposition — consciously excluded.** No map widget, no geographic report and no coordinate column is authored. The column definitions are in [`./data-model.md`](./data-model.md).

**The rest of feature `F009`, so the feature is fully accounted for.**

| Requirement | Citation | Coverage |
| --- | --- | --- |
| `F009-1` "Develop interactive charts for funding trends" | `SRS:L485` | **Covered** — the Dashboard / Trends route, page `bst_dashboard`, widgets `bst-trends-kpi` and `bst-trends-charts`, under design-system gap **G1** |
| `F009-2` "Create industry distribution visualizations" | `SRS:L486` | **Covered** — the same route and the same two widgets, under gap **G1** |
| `F009-3` "Implement growth rate comparisons across startups" | `SRS:L487` | **Consciously excluded** — no growth column and no headcount history exists in the binding schema. `employee_count_range` is a single current band drawn from `1-10`, `11-50`, `51-200`, `201-500`, `500+`, with no prior value retained, so no rate of change is derivable from it. |
| `F009-4` "Develop investor portfolio visualizations" | `SRS:L488` | **Covered** — the Investor Profile route, page `bst_investor`, with `x_bst_startuptrk_investor.portfolio_count` surfaced in the overview panel alongside the rounds led and rounds participated lists |
| `F009-5` "Create geographic distribution maps of Boston startups" | `SRS:L489` | **Consciously excluded** — this flag |

Three of the five are covered; two are excluded. The widgets and their build mechanics are in [`./manual-build/04-service-portal-pages-and-widgets.md`](./manual-build/04-service-portal-pages-and-widgets.md), and the `portfolio_count` derivation is in [`./data-model.md`](./data-model.md).

**Decision log.** [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md).

### F12 — The Notification System feature

**The requirement.** Feature `F010` "Notification System" in its entirety — a system to alert users about updates to startups they are following or to their saved searches.

**The source.** `ID: F010` at `SRS:L493`, described there as "System to alert users about updates to startups they're following or saved searches." The feature carries five requirements, and **all five** are the subject of this flag.

| Requirement | Citation | Text as it appears |
| --- | --- | --- |
| `F010-1` | `SRS:L499` | "Implement in-app notification system" |
| `F010-2` | `SRS:L500` | "Develop email notification service" |
| `F010-3` | `SRS:L501` | "Create notification preferences management for users" |
| `F010-4` | `SRS:L502` | "Implement real-time updates for followed startups" |
| `F010-5` | `SRS:L503` | "Develop digest emails for weekly or monthly updates" |

**The platform position.** **No notification, follow, saved-search or email requirement appears anywhere in the authoritative prompt.** The binding schema is correspondingly empty of the entities all five requirements would need: the ten tables of [`./data-model.md`](./data-model.md) contain **no notification table, no follow relationship, no subscription-to-a-record entity, no saved-search entity and no notification-preference column**, and the delivered Update Set declares no notification record, no email notification and no event registration. Because prompt section 1.0's field definitions are binding and complete, none of those entities may be added, so none of the five requirements is implementable within the closed field list.

The two features are also linked at the requirement level: a follow or saved-search capability is the prerequisite for `F010-4` and for the saved-search half of the feature description, and that prerequisite is itself excluded as `F003-3` under [F9](#f9--srs-requirements-with-no-prompt-counterpart).

**Disposition — consciously excluded, all five.** Nothing in the application notifies, follows, subscribes, digests or emails. The exclusion is recorded here so the absence of an entire source feature reads as a decision rather than an oversight.

**Decision log.** [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md).

### F13 — Cleaning rule 3's "Other" coercion in six choice lists

**The requirement.** Cleaning rule 3, stated verbatim in the prompt: normalise `funding_stage` and `round_type` values to the enumerated choice list, with unmatched values **mapped to "Other" and logged**.

**The source.** Prompt section 4.0, cleaning rule 3, preserved verbatim in the Agent Action Plan at section 0.10.2. The conflicting statement is prompt section 1.0, which declares the field definitions and their choice values **"binding and complete — do not add, omit, or infer additional fields."**

**The platform position.** Nothing about the platform prevents the coercion. **The two requirements conflict with each other.** Of the ten choice lists the delivered application carries, six declare no `Other` member and cannot receive the coercion without adding one:

| # | Choice list | Declared values |
| --- | --- | --- |
| 1 | `startup.funding_stage` | Pre-Seed, Seed, Series A, Series B, Series C+, Growth, Public, Acquired |
| 2 | `startup.employee_count_range` | 1-10, 11-50, 51-200, 201-500, 500+ |
| 3 | `investor.type` | VC, Angel, PE, Corporate, Accelerator |
| 4 | `fundinground.round_type` | the eight `funding_stage` values |
| 5 | `jobposting.remote_type` | Onsite, Hybrid, Remote |
| 6 | `jobposting.seniority` | Entry, Mid, Senior, Lead, Executive |

The four that **do** declare an `Other` member — `startup.industry`, `founder.title`, `executive.title` and `jobposting.department` — receive the coercion exactly as the rule states. Both statements come from the same authority, so neither can be preferred on authority grounds, and every resolution breaches one of them.

**The disposition — partially implemented, flagged.** The rule is applied in full in the four lists that can receive it. In the six that cannot, the field is **left unwritten**, the record is **kept**, and the event is recorded three ways so the shortfall is a number rather than an inference:

| Surface | What it carries |
| --- | --- |
| The log line | The exact outcome text `left unwritten: the prompt 1.0 choice list declares no Other member (flagged deviation from cleaning rule 3)` |
| The event | A `deviation` member set true, alongside the record type, the field and the offending value |
| The run summary | A dedicated `rule3_deviations` counter, **separate from** the general `unmatched` count, so `unmatched` is always greater than or equal to it and the difference is the compliant half |

An Automated Test Framework assertion checks all three. Adding an `Other` member to any of the six is **forbidden**: the field-list fidelity gate counts columns and choice values against the binding list, so the addition would fail the gate it was meant to satisfy. Anyone who believes the lists were intended to be extensible should reopen that gate rather than edit the mapper — the permanent zero in `rule3_deviations` afterwards is what would confirm the reading.

**Where this is stated.** Section 5.4 of [`./manual-build/02-flow-crunchbase-ingestion.md`](./manual-build/02-flow-crunchbase-ingestion.md) and the corresponding section of [`./manual-build/03-flow-linkedin-ingestion.md`](./manual-build/03-flow-linkedin-ingestion.md); the fixture's own expected counts in [`../sample-data/README.md`](../sample-data/README.md); the assertion in [`./manual-build/05-atf-test-suites.md`](./manual-build/05-atf-test-suites.md); and the criterion 4c evidence in [`./validation-checklist.md`](./validation-checklist.md).

**Decision log.** [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md) — the conflict at `D-022`, the resolution at `D-232`, and the fourth ambiguity call-out in [`../../docs/review/CRITICAL_DECISIONS.md`](../../docs/review/CRITICAL_DECISIONS.md).

### F14 — The Crunchbase authentication model

**The requirement.** Authenticate the Crunchbase call through the named Connection & Credential Alias `x_bst_startuptrk.crunchbase_api`, described in the plan as a Basic Auth alias holding the API key in its password field.

**The source.** Prompt section 4.0 and Agent Action Plan section 0.4.8.

**The platform position.** The alias mechanism works exactly as specified; the **provider** does not. Crunchbase v4 authenticates an `X-cb-user-key` request header, or the same key as a `user_key` query parameter, and accepts **HTTP Basic in no form at all**. A Basic-authentication alias is therefore usable as an encrypted **store** for the key but not as the transport, and one consequence follows that an operator will meet: the platform's own generic connection test composes neither that header nor LinkedIn's two versioning headers, so it can report green on a chain no provider would accept and red on one that works.

**The disposition — resolved by documented workaround.** The alias remains Basic-authentication and remains the only home for the key. The flow reads the key through the alias at run time and sends it as an `X-cb-user-key` header, so no key appears in a URL, a flow input, a script step or the Update Set — the property the requirement was protecting is fully preserved. The generic connection test is retained as a **diagnostic** and is explicitly **not** a completion criterion; the provider-correct authenticated probe of guide 01 is.

**One further consequence: the base URL is a candidate, not a confirmed endpoint.** The provider labels the delivered root `https://api.crunchbase.com/api/v4` a legacy v4 root and publishes newer roots alongside it, so **live mode is not activated on Crunchbase until the authenticated probe returns `code=ok` at status `200` against whatever value `x_bst_startuptrk.crunchbase.base_url` currently holds**. A `404` or a `410` from the probe is a configuration fault on the root itself and not a credential fault, and correcting it is an instance configuration change — the property and the connection record's **Connection URL** are edited together, the probe is re-run, and the Update Set is not re-exported. The shipped value is retained as the default because Agent Action Plan section 0.4.7 pins it; changing it at authoring time would substitute one unverified root for another.

**Where this is stated.** The wire contract, the probe, the activation gate and the five-item base-URL update procedure are in [`./manual-build/01-connection-credential-aliases.md`](./manual-build/01-connection-credential-aliases.md); the alias-resolution step is section 3.5 of [`./manual-build/02-flow-crunchbase-ingestion.md`](./manual-build/02-flow-crunchbase-ingestion.md).

**Decision log.** [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md) — `D-229` for the wire contract and the two corrected base URLs, `D-230` for the alias resolution.

### F15 — LinkedIn publishes no read API for people or third-party job postings

**The requirement.** Ingest Founder, Executive and Job posting records from LinkedIn on the configured cadence.

**The source.** Prompt section 4.0, which names LinkedIn as a source and lists those three record types among the six ingested entities.

**The platform position.** This is a **provider** limitation and not a platform one, and it cannot be worked around by any instance, entitlement or credential. No public LinkedIn API enumerates a company's people, so founders and executives have no live read path. The Job Posting API is a **write** API for publishing an organisation's own postings, not a read API for third-party postings. What is available is organisation identity — `GET /rest/organizationsLookup` and the versioned organisation endpoints — which confirms the credential, the two mandatory versioning headers and the company identity, and returns none of the three record types.

**The disposition — partially implemented, flagged.** The flow exists, runs on the cadence, authenticates through its alias and writes all three record types; its **live call is an organisation-identity probe rather than an acquisition**, and the rows themselves come from the sanctioned fallback dataset in every credential posture. The consequence must be stated wherever a run is reported: **`LinkedIn Ingestion` can never be labelled `live validated`** — not on any instance, not with any credential. Prompt section 10.0 criterion 4 explicitly accepts the sample-dataset substitute, so this does not block acceptance; it constrains only what the evidence may claim.

**Where this is stated.** [`./manual-build/03-flow-linkedin-ingestion.md`](./manual-build/03-flow-linkedin-ingestion.md); the labelling rule in [`../sample-data/README.md`](../sample-data/README.md) and in criterion 4d of [`./validation-checklist.md`](./validation-checklist.md).

**Decision log.** [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md) — `D-233`.

### F16 — Three columns the live path cannot fill

**The requirement.** Populate every column of the binding field list from the named sources.

**The source.** Prompt section 1.0 for the columns, prompt section 4.0 for the sources.

**The platform position.** Three columns have no counterpart in what the providers publish.

| Column | Why the live path cannot fill it | What the flow does |
| --- | --- | --- |
| `startup.institutional_funding_last_5yrs` | Crunchbase exposes no such field. The five-year window is expressible only as a **query predicate**, not as a returned value. | Left unset by the live path. The fallback dataset carries it as a column, so a fallback-sourced startup has it. |
| `investor.aum_usd` | Crunchbase v4 publishes no assets-under-management field. | Left unset for a live-sourced investor, on both paths. |
| `fundinground.source_url` | The funding-round search response carries no public round URL; `permalink` is a slug rather than an `https` URL and the boundary validation would refuse it. | Left unset rather than filled with a value that is not a URL. |

**The disposition — partially implemented, flagged.** The columns exist, carry their specified types, and are readable and writable by hand and by the fallback path; what is unavailable is **live population**. No placeholder, sentinel or inferred value is written into any of the three: an unset column is honest where a fabricated one would be indistinguishable from data. Two of the three are premium-gated, so a base-role caller cannot tell an unset value from a denied one in any case.

**Where this is stated.** Section 3.4 of [`./manual-build/02-flow-crunchbase-ingestion.md`](./manual-build/02-flow-crunchbase-ingestion.md); the column contract in [`../sample-data/README.md`](../sample-data/README.md).

**Decision log.** [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md) — `D-231` for the live-path contract, `D-239` for the boundary validation that refuses a non-URL.

### F17 — A round with several lead investors

**The requirement.** Record a funding round's lead investor in the single `lead_investor` reference column the binding field list defines.

**The source.** Prompt section 1.5, which defines `lead_investor` as one Reference to Investor.

**The platform position.** The provider reports **several** lead investors on a co-led round; `lead_investor_identifiers` then arrives as a comma-joined list. The schema has one reference column and the field list is binding and complete, so a second lead cannot be stored anywhere — not as a second reference, not as a list, not as a note.

**The disposition — flagged, not implemented.** Where more than one lead is reported, no Investor record matches the joined string, the reference is **left unset**, and an unresolved-reference line is logged. **No wrong lead is stored**, which is the property worth having: a co-led round with an empty lead is recoverable, a co-led round attributed to one arbitrary lead is not. Every named investor, including every lead, is still captured as a participating-investor row in the join table, so no relationship is lost — only the lead/participant distinction for that round.

**Where this is stated.** Section 3.4 of [`./manual-build/02-flow-crunchbase-ingestion.md`](./manual-build/02-flow-crunchbase-ingestion.md).

**Decision log.** [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md) — `D-010` for the participation model and `D-014` for the two traversal paths the join rows still serve.

### F18 — The outbound path branch between the REST step and a scoped script step

**The requirement.** Prompt section 4.0 mandates Flow Designer flows and forbids IntegrationHub spokes, and requires both credential aliases to be referenced **by name** in Flow Designer REST steps. Agent Action Plan section 0.8.4 makes the generic Flow Designer REST step the **primary** path and a scoped script step resolving the alias by name its **entitlement fallback**, and requires the guides to document a pre-flight branch and then follow one arm of it.

**The source.** Prompt section 4.0 and Agent Action Plan section 0.8.4.

**The platform position.** Two conditions decide which arm an instance can build, and neither is knowable from the repository.

| # | Condition | Why it decides |
| --- | --- | --- |
| P1 | Whether the generic REST step is available on this instance | The step is an entitled capability. An instance without the entitlement cannot build the primary arm at all. |
| P2 | Whether the connection record can supply the provider's credential-bearing request header | Crunchbase authenticates an `X-cb-user-key` header and accepts HTTP Basic in no form, and the REST step's own **Request headers** field takes only literals and data pills. A secret may be neither, so the primary arm is usable for Crunchbase **only** where the connection itself carries the header. |

**The disposition — resolved by documented workaround.** The REST step arm is the primary path and is built wherever both conditions hold. Where either fails, the fallback arm is a scoped script step that resolves the same alias **by name** through the connection-info provider and executes the call through the scoped outbound REST message API. Three properties hold on both arms, and they are what make the fallback a fallback rather than a deviation:

| Property | Both arms |
| --- | --- |
| The alias is referenced by name | Yes. Arm A binds it in the step's **Connection alias** field; arm B resolves it by name at run time. |
| No spoke is involved | Yes. A generic REST step is not a spoke, and neither is a scoped script step. No spoke content set is installed, activated, referenced or opened. |
| No credential material enters the flow, its inputs, its scripts or the Update Set | Yes. Arm A never holds the key at all; arm B reads it inside the step and hands it straight to the request without assigning it to a variable that outlives the call. |

**Exactly one arm is built**, decided once at build time and recorded before the flow is activated. There is no runtime branch between them, and building both is forbidden. Every budget, error code, output variable and health check in the rest of each flow applies unchanged to whichever arm was built; only the transport differs.

**Where this is stated.** The two checks, the arm-selection table, the arm-parity table and the recording obligation are section 3.1 of [`./manual-build/02-flow-crunchbase-ingestion.md`](./manual-build/02-flow-crunchbase-ingestion.md) and the corresponding section of [`./manual-build/03-flow-linkedin-ingestion.md`](./manual-build/03-flow-linkedin-ingestion.md). The wire contract that makes P2 a real question for Crunchbase is [The provider wire contract](./manual-build/01-connection-credential-aliases.md#the-provider-wire-contract).

**Decision log.** [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md).

### F19 — No retention, minimisation or data-subject erasure of staged data

**The requirement.** Not a stated requirement. It is a consequence of one that *is* stated: prompt section 4.0 requires a staging table whose shape mimics the expected API response, and Agent Action Plan section 0.4.3 gives that table a `raw_payload` column holding the upstream response verbatim alongside the flattened person columns `name`, `title`, `bio`, `linkedin_url` and `contact_email`. Nothing in the prompt or the plan says how long that data lives.

**The source.** Prompt section 4.0 and Agent Action Plan sections 0.4.3 and 0.4.7.

**The platform position.** The platform would support it readily — a scheduled job and a Script Include would do it — but the **artifact inventories are closed**. Agent Action Plan section 0.4.5 declares exactly eight Script Includes, section 0.4.7 exactly eleven system properties, and section 0.4.2 exactly three business rules and one scheduled job, and that one job is the rate-limit counter prune. A retention capability would need a ninth Script Include, at least two further properties and a second scheduled job, so it cannot be delivered without departing from the frozen plan.

**The disposition — flagged, not implemented.** No delivered artifact minimises, prunes or erases a staging row, and there is no data-subject erasure method. Three delivered mechanisms bound the exposure instead, and they are access controls and one narrow window rather than a retention policy:

| Mechanism | Table | Effect |
| --- | --- | --- |
| `access` `package_private` and `ws_access` false | `x_bst_startuptrk_ingest_staging`, `x_bst_startuptrk_rate_limit_counter` | Neither table is addressable from another application scope and neither is served by the platform Table API. |
| Read, write, create and delete controls granting `x_bst_startuptrk.admin` alone | Both | No caller holding only `x_bst_startuptrk.user` or `x_bst_startuptrk.premium_user` can reach a row on either table by any route. |
| The hourly `Prune rate limit counters` job | Counter only | Every row whose window has closed is deleted, so the counter table's retention is the window length — sixty seconds at the shipped value. The `caller` references it holds survive minutes. |

**The staging table has no equivalent, and that is the residual gap:** a settled row keeps its `raw_payload` and its five person columns until an administrator deletes it, on a live run exactly as on a fallback run. **What a human must do:** clear settled staging rows as part of operating the flows. The two supported routes, and the two rules that bind either of them, are in [`./data-model.md`](./data-model.md) and [`./manual-build/06-staging-table-csv-import.md`](./manual-build/06-staging-table-csv-import.md).

**One surface is not affected, and it is worth saying so.** The **logs** hold nothing to erase. `IngestionLogger` records an identifier only when it is a platform record identifier or an opaque `<kind>:<token>` reference, and a value only when it is a short enumeration label; everything else becomes the literal `(redacted)` or `(blank)`, and nothing derived from a dropped value — no hash, no digest, no fingerprint — is recorded anywhere. So no name, address, biography, URL or upstream message reaches the flow execution log or the system log in the first place.

**Decision log.** [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md).

## Open integration limitations

**These are not flags, and they are counted separately from the twelve.** A flag records a *requirement* the platform cannot cleanly satisfy. An open integration limitation records a *capability that is built in full but cannot be exercised against its live source* until a third party supplies information this delivery cannot obtain. The distinction matters operationally: a flag closes only if the requirement changes, whereas an open limitation closes the moment the missing information arrives, with no code change and no rebuild.

There is exactly **one**, and it carries the `OPEN-` prefix so it can never be mistaken for an `F` flag or counted into the twelve.

### OPEN-1 — Live LinkedIn ingestion, pending an endpoint-contract declaration

**The capability.** Ingestion of Founder, Executive and JobPosting records from LinkedIn, on the configured cadence, through the `x_bst_startuptrk.linkedin_oauth` alias.

**What is delivered.** All of it, except the live call. The five LinkedIn custom actions are built and published, the scheduled flow is assembled, activated and validated, the alias and connection definition records are built, and the ingestion runs end to end in `fallback` mode against [`../sample-data/`](../sample-data/). Nothing about the build is provisional.

**What is unavailable, and why.** **Live LinkedIn ingestion is formally declared unavailable.** The endpoint contract for this source is undetermined: current company resources are versioned and product-gated and reject a request that omits the version header, no generally available resource enumerates an arbitrary company's employees, and job-posting resources require a separate approved partnership whose response shape depends on which partnership is granted. The legacy resource paths in `src/data_collection/api_integrators/linkedin_integrator.py` descend from a scaffold that cannot run and are **not** a verified contract, so they are not shipped as though they were.

**The gate.** The live path is gated on an **eight-row endpoint-contract declaration** the credential owner completes in [`./manual-build/03-flow-linkedin-ingestion.md`](./manual-build/03-flow-linkedin-ingestion.md): product or partner programme, API version header and value, base URL, granted scopes, resource path per record type, response envelope, pagination contract and rate limit. **The live-call script refuses to issue a request while any row is undeclared**, so an incomplete declaration cannot produce a silent partial call.

**Disposition — open, with the build complete.** Founder, Executive and JobPosting records arrive **only** from the fallback dataset until the declaration is completed, so live coverage of those three entity tables is an open item rather than a delivered capability. Every LinkedIn result is labelled `fallback validated` and never `live validated`. The declaration may never be completed, in which case the limitation persists.

**How it closes.** The credential owner completes the eight rows and provisions the credential; guide 03's resumption procedure is followed; `x_bst_startuptrk.ingestion.source_mode` moves to `live` only once the connection test passes. No artifact of this delivery is rewritten.

**Distinguish it from the credential gap.** The Crunchbase source has a **published, verified** contract and needs only its credential. LinkedIn needs the credential **and** the contract declaration. Both sources currently run in `fallback` mode, but for different reasons, and only LinkedIn's is recorded here.

**Decision log.** `D-103` in [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md), risk **High**, flagged as a deviation.

## SRS feature coverage roll-up

Ten rows, one per feature of `documentation/Software Requirements Specifications (SRS).md`. Every feature is either mapped to a target artifact or explicitly excluded, so all ten are accounted for in one place.

**This roll-up is at feature level.** The **Target coverage** column names the artifacts that serve the feature; it is **not** a claim that every one of that feature's five sub-requirements is realised in full. The **Not covered** column names every sub-requirement this inventory records as having **no** target artifact. The complete requirement-by-requirement mapping in both directions is the business of [`../../docs/decisions/TRACEABILITY_MATRIX.md`](../../docs/decisions/TRACEABILITY_MATRIX.md), and this table is the feature-level summary of its unimplemented half.

Every one of the ten features carries at least one sub-requirement with no target artifact, so no row of the **Not covered** column is empty.

| Feature | Title | Target coverage | Not covered |
| --- | --- | --- | --- |
| `F001` | Data Aggregation System, `SRS:L365` | The two Flow Designer ingestion flows, the four cleaning rules, the staging table `x_bst_startuptrk_ingest_staging`, and the cadence property `x_bst_startuptrk.ingestion.cadence_hours` | `F001-1` web crawlers — [F9](#f9--srs-requirements-with-no-prompt-counterpart). `F001-5` data versioning — the three residuals table below. |
| `F002` | User Interface, `SRS:L379` | The five Service Portal routes — `bst_home`, `bst_company`, `bst_investor`, `bst_dashboard`, `bst_account` — with responsive support narrowed to **1024 pixels and above** | `F002-5` WCAG 2.1 Level AA conformance — see [Responsive stance](#responsive-stance--the-1024-pixel-floor) |
| `F003` | Search and Filtering, `SRS:L393` | The Home / Search route, the startup inclusion filter built by `StartupSearchService`, and the `/startups` list-and-search operation with its `name`, `industry` and `location` filters | `F003-3` saved search — [F9](#f9--srs-requirements-with-no-prompt-counterpart). `F003-5` sorting options — the residuals table below. |
| `F004` | Company Profiles, `SRS:L407` | The Company Profile route, page `bst_company`, with its five tabs — Overview, Funding, People, Jobs, News | `F004-4` is served by **manual entry or CSV import only**; automated news ingestion is excluded — see [Capabilities named out of scope](#capabilities-named-out-of-scope) |
| `F005` | API Access, `SRS:L421` | One `sys_ws_definition` with **31 operations** across six resources plus the nested executives sub-resource, documented in [`./api-reference.md`](./api-reference.md) | `F005-5` client SDKs — no SDK is delivered in any language |
| `F006` | User Management, `SRS:L435` | The three roles `x_bst_startuptrk.admin`, `x_bst_startuptrk.premium_user` and `x_bst_startuptrk.user`, with the table-level and field-level access controls of [`./access-control.md`](./access-control.md) | `F006-4` subscription management — [F1](#f1--premium-subscription-billing-and-payment-processing). `F006-1` registration and `F006-5` account recovery are platform concerns outside the application scope. |
| `F007` | Analytics and Reporting, `SRS:L449` | The Dashboard / Trends route, page `bst_dashboard`, and JSON export through the REST resources | `F007-5` scheduled report delivery — [F9](#f9--srs-requirements-with-no-prompt-counterpart). The **CSV half of `F007-2`** — the residuals table below. |
| `F008` | Admin Dashboard, `SRS:L463` | The platform's native list and form views inside the scoped application — 10 form sections, 10 list views and a nine-module application menu — reachable by `x_bst_startuptrk.admin`; see [F8](#f8--an-administrative-console-as-a-portal-route) | `F008-3` health monitoring, `F008-4` platform usage analytics, and the API-key interface of `F008-5` — [F8](#f8--an-administrative-console-as-a-portal-route) |
| `F009` | Data Visualization, `SRS:L477` | The Dashboard / Trends route with `bst-trends-kpi` and `bst-trends-charts` under gap **G1**, and the Investor Profile route with `portfolio_count` surfaced | `F009-3` growth-rate comparisons and `F009-5` geographic maps — [F11](#f11--geographic-distribution-maps) |
| `F010` | Notification System, `SRS:L491` | **Nothing.** No target artifact exists for any part of this feature. | All five: `F010-1`, `F010-2`, `F010-3`, `F010-4`, `F010-5` — [F12](#f12--the-notification-system-feature) |

Ten features. Nine have at least one target artifact; `F010` has none.

### Where each named exclusion is recorded

Every sub-requirement named in the **Not covered** column resolves to an entry in this document, so no exclusion in the roll-up is left unrecorded.

| Sub-requirement | Recorded in |
| --- | --- |
| `F001-1`, `F003-3`, `F007-5` | [F9](#f9--srs-requirements-with-no-prompt-counterpart) |
| `F002-5` | [Responsive stance — the 1024-pixel floor](#responsive-stance--the-1024-pixel-floor) |
| `F004-4` | [Capabilities named out of scope](#capabilities-named-out-of-scope) — automated news ingestion |
| `F006-4` | [F1](#f1--premium-subscription-billing-and-payment-processing) |
| `F008-3`, `F008-4`, `F008-5` API-key interface | [F8](#f8--an-administrative-console-as-a-portal-route) |
| `F009-3`, `F009-5` | [F11](#f11--geographic-distribution-maps) |
| `F010-1` through `F010-5` | [F12](#f12--the-notification-system-feature) |
| `F001-5`, `F003-5`, `F005-5`, `F006-1`, `F006-5`, and the CSV half of `F007-2` | The residuals table immediately below |

Six sub-requirements are named in the roll-up and belong to no flag section. They are recorded here.

| Sub-requirement | Text as it appears | Position |
| --- | --- | --- |
| `F001-5` | "Implement data versioning for historical tracking" — `SRS:L377` | **Consciously excluded.** The prompt declares no version, revision or history column, and prompt section 1.0's field list is closed. Every one of the 111 dictionary records the Update Set carries is delivered with `audit` false, so no field-level audit history is written either. A record's current values and the platform's own `sys_updated_on` and `sys_updated_by` stamps are the only history the application keeps. |
| `F003-5` | "Develop sorting options for search results" — `SRS:L405` | **Consciously excluded.** No list operation accepts a sort parameter. Each of the seven list operations applies one documented order with a `sys_id` tie-breaker so that offset paging is stable, and that order is fixed rather than caller-configurable. The per-operation orders are in [`./api-reference.md`](./api-reference.md). |
| `F007-2`, CSV half | "Create data export functionality in various formats (CSV, JSON)" — `SRS:L458` | **Partly covered, CSV consciously excluded.** JSON export is served by the six REST resources. **CSV export is not:** the API is JSON only, with `consumes` and `produces` pinned to `application/json` and the `_customized` flags set on the definition and on all 31 operations, so no operation emits CSV. The one CSV surface in the package is the **inbound** sample dataset of [`./manual-build/06-staging-table-csv-import.md`](./manual-build/06-staging-table-csv-import.md), which is an import path and not an export. |
| `F005-5` | "Develop SDKs for common programming languages (JavaScript, Python)" — `SRS:L433` | **Consciously excluded.** The prompt requires a Scripted REST API and its documentation; it requires no client library. No SDK, package or generated client is delivered in any language, and no repository manifest is created for one. The API contract in [`./api-reference.md`](./api-reference.md) is the sole consumer-facing artifact. |
| `F006-1` | "Implement user registration and authentication system" — `SRS:L443` | **Consciously excluded from the application scope.** Identity, authentication and session handling are platform concerns on `sys_user`, which sits outside `x_bst_startuptrk`, and prompt section 6.0 forbids modifying anything outside the scope. The application declares no identity table and no credential column; see [`./access-control.md`](./access-control.md). |
| `F006-5` | "Develop password reset and account recovery mechanisms" — `SRS:L447` | **Consciously excluded from the application scope.** Same position as `F006-1`: a `sys_user` concern outside the scope, with no counterpart in the authoritative prompt. |

**Decision log.** [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md).

### The five flags that are not source-requirement exclusions

The roll-up above walks the **source requirements document**, so it reaches F1 through F12 and no further. **F13** through **F17** are not exclusions of a source requirement at all: each is a shortfall against the **authoritative prompt**, discovered where the prompt meets a real provider contract or its own binding field list. They are reached through the prompt-section side of the traceability matrix rather than through this roll-up.

| Flag | Prompt section it falls short of | Nature of the shortfall |
| --- | --- | --- |
| [F13](#f13--cleaning-rule-3s-other-coercion-in-six-choice-lists) | 4.0 cleaning rule 3, against 1.0's binding choice lists | Two requirements of the same authority conflict; the rule is applied in four of ten lists and the shortfall is counted at run time |
| [F14](#f14--the-crunchbase-authentication-model) | 4.0 credential aliases | The specified authentication model is not one the provider accepts; the alias is retained as the key's only home and the transport changes |
| [F15](#f15--linkedin-publishes-no-read-api-for-people-or-third-party-job-postings) | 4.0 ingested entities | The provider publishes no read API for three of the six record types; the sanctioned fallback dataset supplies them |
| [F16](#f16--three-columns-the-live-path-cannot-fill) | 1.0 field list, against 4.0's sources | Three columns exist and are writable but have no live source |
| [F17](#f17--a-round-with-several-lead-investors) | 1.5 `lead_investor` | The binding shape cannot represent what the provider reports; nothing wrong is stored in its place |

None of the five is a platform limitation. Four are provider or requirement-conflict limitations, and the fifth is a consequence of the field list being binding — so none is closable by building more inside `x_bst_startuptrk`.

## Design-system gap inventory

The user-interface design system is **platform-native**: Service Portal's AngularJS 1.x with **Bootstrap 3.3.6**, both already present on the instance. It is not an npm or PyPI package, there is nothing to install, and it cannot be pinned from this repository — its version is bound to the platform release. UI Builder is forbidden by prompt section 5.0, so no `sys_ux_*` record of any kind is authored.

Seven gaps exist between what the five portal routes need and what that library provides. Six are resolved inside the system. One has no resolution.

| ID | Gap | Resolution |
| --- | --- | --- |
| **G1** | **Charts** for the Dashboard / Trends route. Bootstrap 3 has no chart component. | Platform reporting surfaced through a report or chart widget, or Angular-rendered inline SVG in a custom widget. **Both mechanics are specified in buildable detail** in [`./manual-build/04-service-portal-pages-and-widgets.md`](./manual-build/04-service-portal-pages-and-widgets.md) and the `render_mode` option of `bst-trends-charts` selects between them: `svg` renders the Angular-bound inline SVG bar chart of [The inline SVG chart](./manual-build/04-service-portal-pages-and-widgets.md#the-inline-svg-chart), carrying its element list, its five geometry constants, every `ng-attr-*` binding and its accessible `title`, `desc` and companion table; `report` embeds a saved platform report per [The report embed](./manual-build/04-service-portal-pages-and-widgets.md#the-report-embed). **`svg` is the shipped mode** on both dashboard instances, and `report` falls back to `svg` when no readable report is configured, so a chart renders in every configuration. **Nothing is lost in the migration:** the legacy manifest declared `chart.js` at `package.json:L19` and `react-chartjs-2` at `package.json:L21` but **never imported either**, and the legacy dashboard at `src/frontend/components/Dashboard/Dashboard.tsx:L68-L106` is a six-panel grid-and-paper layout — QuickStats, RecentUpdates, TrendingStartups, FeaturedCompanies, LatestNews and JobOpenings — with **no chart import at all**. |
| **G2** | **Multi-select chip input** for `x_bst_startuptrk_investor.focus_areas`. No multiselect and no chip control exists in the library. | A platform **multi-choice** field rendered through the stock **Form** widget for write paths, and `.label` chips inside a `.panel-body` for read-only portal display. The read-only chips are built in `bst-investor-profile`. |
| **G3** | **Loading indicator.** Bootstrap 3 has no spinner. | Service Portal's own loading indicator, or a striped progress bar — `.progress` containing `.progress-bar.progress-bar-striped.active`. The striped form is built in `bst-startup-results`. |
| **G4** | **Card media**, the image surface of a result card. | A Bootstrap media object image — `.media-left` containing `img.media-object` — bound to `x_bst_startuptrk_startup.logo_url`. `.thumbnail` is the alternative container. Built in `bst-startup-results` and in the company-profile header. |
| **G5** | **Premium upsell and paywall treatment** for `x_bst_startuptrk.user`. No library component exists for the pattern. | An informational alert panel carrying a primary call to action — `.alert.alert-info` containing a `.btn.btn-primary` — rendered **in place of** each gated field or gated tab region wherever the read ACL denies, never as a blank, an empty cell or a zero. Packaged as the reusable `bst-premium-upsell` widget, embedded by `bst-company-profile`, `bst-investor-profile` and `bst-account-summary`. |
| **G6** | **Premium subscription billing and checkout.** The platform grants entitlement through roles and has no commerce capability. | **No resolution.** This is [F1](#f1--premium-subscription-billing-and-payment-processing): flagged, not implemented, not half-implemented. It is the only one of these seven gaps with no resolution. |
| **G7** | **Icon-system split.** The executive deck uses **Lucide 0.460.0** by rule mandate; the portal uses the **platform glyph font** — `.icon-search`, `.icon-user`, `.icon-chart` and the further `.icon-*` classes the release provides. | **Not unifiable, and not a defect.** The boundary runs both ways and is recorded so no agent crosses it: **no widget may reference Lucide** — no Lucide script tag, stylesheet, `data-lucide` attribute or Lucide SVG in any widget template, client controller, CSS field or theme field; and **no platform glyph may appear in the deck**, whose icons are Lucide SVG only. Both surfaces additionally carry a zero-emoji rule. |

Six gaps resolve inside the system; **G6** does not. The five component gaps G1 through G5 are collected as [F7](#f7--design-system-component-gaps); G6 is [F1](#f1--premium-subscription-billing-and-payment-processing); G7 is a boundary rather than a missing component and belongs to no flag. Every resolution above is built per [`./manual-build/04-service-portal-pages-and-widgets.md`](./manual-build/04-service-portal-pages-and-widgets.md), which carries the markup, the option schemas and the class lists.

**Decision log.** [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md).

### Responsive stance — the 1024-pixel floor

Responsive support is **deliberately narrowed**, and the narrowing is stated here as a fact rather than left to be discovered.

- **Viewports below 1024 pixels are out of scope.** Prompt section 7.2 excludes them.
- **1024 pixels is the declared supported viewport floor of the portal.**
- Widget layouts use **medium and large column classes only**: `.col-md-*` and `.col-lg-*`.
- **No extra-small or small refinement is authored:** no `.col-xs-*`, no `.col-sm-*`, no `.hidden-xs`, no `.visible-sm-*`, and no media query keyed to the extra-small or small breakpoint. On every `sp_rectangle`, `size_md` and `size_lg` are set and `size`, `size_xs` and `size_sm` are left empty.
- The portal walkthrough is verified at 1024 pixels wide and above. **A narrower viewport is not a defect.**

The floor narrows the source requirements document's own interface constraint at `SRS:L214`, "Must be accessible on devices with minimum screen width of 320px".

**Accessibility conformance is not claimed.** Source requirement `F002-5` at `SRS:L391`, "Ensure WCAG 2.1 Level AA accessibility compliance", has no counterpart in the authoritative prompt, and **no conformance level is asserted anywhere in this package**: no audit was performed, no conformance statement is published, and no accessibility acceptance criterion appears in the success criteria. Disposition: **consciously excluded**. The portal is nevertheless built from stock Service Portal widgets and unmodified Bootstrap 3.3.6 components rather than hand-rolled markup, which is a build rule stated in [`./manual-build/04-service-portal-pages-and-widgets.md`](./manual-build/04-service-portal-pages-and-widgets.md) and not a conformance claim.

The layout mechanics are in [`./manual-build/04-service-portal-pages-and-widgets.md`](./manual-build/04-service-portal-pages-and-widgets.md).

### Residual risks of the Table API read route on the seven entity tables

**This entry is not one of the twelve flags, and it is deliberately not numbered.** The `F` inventory discharges prompt section 11.0's obligation, which concerns requirements with no clean ServiceNow equivalent. What follows is an accepted residual risk of a delivered design decision, recorded so it is visible rather than implicit.

**What is delivered.** The seven entity tables carry `access` `public`, `read_access` `true` and `ws_access` `true`, so `GET /api/now/table/x_bst_startuptrk_<entity>` serves them. Every cross-scope write, schema and configuration capability is `false` on all ten tables, and the three supporting tables — the join table, the staging table and the rate-limit counter — remain `package_private` with `ws_access` `false` and are reachable over no external route. The posture is tabulated in [`./data-model.md`](./data-model.md) and [`./access-control.md`](./access-control.md), and it is what makes the eleven required post-commit gates of [`./validation-gates.md`](./validation-gates.md) the direct entity-table reads AAP section 0.11.2 specifies.

**What the route does enforce.** The platform Table API is access-controlled. It authenticates the caller, evaluates the table-level read control — which admits only `x_bst_startuptrk.admin`, `x_bst_startuptrk.user` and `x_bst_startuptrk.premium_user` — and evaluates every field-level read control before returning a value. All seven premium fields are therefore omitted from a Table API response to a caller holding only `x_bst_startuptrk.user`, exactly as they are omitted from the application's own API. No unauthenticated or unroled caller reads anything.

**Three residual differences from the application's own API, each with its compensating control.**

| # | Residual risk | Compensating control | Owner |
| --- | --- | --- | --- |
| 1 | The Table API route is outside the application's fixed-window rate limiter, so a caller holding a scoped role can issue reads that the `x_bst_startuptrk.rate_limit_requests` budget does not count. | A platform **inbound REST rate-limit rule** on the seven tables, which AAP section 0.8.3 already sanctions as defence in depth for the application's own endpoint. It is not shipped in the Update Set: an inbound rate-limit rule is instance configuration outside the application scope, and prompt section 6.0 forbids the scoped application from creating it. | Instance operator, at deployment time. Recommended, not required, and the deployment is not gated on it. |
| 2 | The Table API route is outside the two `REST_Endpoint` execution controls, whose particular contribution is that the platform's default REST control admits any authenticated internal user. | The **table-level read controls**, which admit only the three scoped roles. "Only the three application roles may read this data" holds on both routes; only the mechanism differs. | Delivered. Recorded by the non-normative diagnostic `GATE-SEC-01` in [`./validation-gates.md`](./validation-gates.md). |
| 3 | `access` `public` with `read_access` `true` permits a script in another application scope — including a Global-scope background script an operator pastes in — to read entity rows through unsecured record access, which evaluates no access control. | Bounded rather than eliminated. Such a script must already be running with instance-level privilege, which reaches every table on the instance regardless of this posture. What the posture does **not** grant is any cross-scope write, schema or configuration capability, and the staging table — the only table holding verbatim upstream payloads and unvalidated personal data — stays sealed. | Accepted. Recorded by the non-normative diagnostics `GATE-SEC-01` and `GATE-SEC-02`. |

**Why the risk is accepted rather than removed.** Removing it means setting `ws_access` `false`, which makes the eleven required gates unexecutable, and the required gate set is fixed by the frozen Agent Action Plan and by the deployment environment. Where a delivered design choice and the specification conflict, the specification governs and the artifact is corrected. The decision, its alternatives and this risk register are recorded in [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md).

### Flow execution context retention

**This entry is not one of the twelve flags, and it is deliberately not numbered.** It is a **platform-owner procedure** that this delivery is forbidden from implementing, recorded in full so the obligation is legible and actionable rather than assumed to be handled.

**The surface.** Flow Designer persists each execution's step inputs and outputs in the platform's own flow execution tables. Two step outputs of each ingestion flow carry upstream content into them by necessity:

| Value | Step | What it carries |
| --- | --- | --- |
| `response_body` | 3 | The verbatim upstream response, which on the live path can contain personal names, contact addresses, biographies and locators. |
| `rows` | 4 | The same values in normalised form, as the mapped row set the cleaning rules consume. |

Neither can be removed without breaking the pipeline: step 4 parses the first and step 5 cleans the second. Everything else those flows emit is a run identifier, an opaque record reference, a bounded code, a counter, a per-run arrival ordinal or the literal `(redacted)` — the five permitted classes, enforced by `IngestionLogger` and enumerated in **What the execution context retains** in [`./manual-build/02-flow-crunchbase-ingestion.md`](./manual-build/02-flow-crunchbase-ingestion.md#what-the-execution-context-retains) and [`./manual-build/03-flow-linkedin-ingestion.md`](./manual-build/03-flow-linkedin-ingestion.md#what-the-execution-context-retains).

**Why it falls to the platform owner.** The flow execution tables are platform tables outside the `x_bst_startuptrk` scope. Prompt section 6.0 forbids this application from modifying anything outside its scope, so their retention window, their cleanup schedule and their read access are the platform owner's to set. **Clearing the staging table does not clear them**, and neither does the one scheduled job this delivery ships, which prunes only rate-limit counter rows. Any statement that this application's retention posture covers its own logs is true and says nothing about this surface.

**What the platform owner is asked to do.** Four items. None is satisfied by anything in this package.

| # | Action | How to confirm it was done |
| --- | --- | --- |
| 1 | **Record the instance's current flow-execution-data retention window** — how long a completed flow execution context and its step data survive before the platform's own cleanup removes them. | The retention configuration and the cleanup schedule, captured as observed values with the date observed. |
| 2 | **Set that window to the shortest value the instance's own operational needs allow**, and record the value set and who set it. Ingestion troubleshooting needs days, not months. | The before and after values. |
| 3 | **Record who can read a flow execution context on this instance**, by role, and confirm that the set is no wider than the set that may read `x_bst_startuptrk_ingest_staging` — which is `x_bst_startuptrk.admin` alone, because that table is `package_private` with `ws_access` `false`. Where the flow-execution reader set is wider, record the difference as an accepted exposure with a named owner. | The role list, and either an equality statement or a recorded exposure. |
| 4 | **Confirm each ingestion flow's own logging level is at the least verbose setting that still records step outcomes.** Guides 02 and 03 require this to be set before activation; this item verifies it independently, because a verbose setting multiplies what item 1's window is retaining. | The logging level of each flow, read from the flow record. |

**The delivered side of the boundary, so the split is unambiguous.** This application minimises what it contributes to that surface, and those parts are delivered rather than deferred: every error output of step 3 is a bounded code from a closed four-value vocabulary and never the platform's own message text, which can quote the endpoint, the composed request and a fragment of the body; no step output other than the two above carries upstream content, and widening any output to add one is forbidden; neither of the two is ever copied into a log line, an annotation or a third output; and the orchestrator construction is the recommended one partly because it keeps every per-record intermediate value — each cleaned record, each resolved reference, each upsert result — inside a single step call, so none of them enters the execution context at all.

**Status: flagged and unmet.** No evidence for items 1 to 4 has been recorded, because the actions belong to the platform owner and are outside this delivery's scope. This entry is the record of the obligation, not of its discharge. The related operator-owned staging and counter procedure is in [`./data-model.md`](./data-model.md); the redaction and reference contract the logger applies is specified there and in [`./api-reference.md`](./api-reference.md).

### Repository manifests are unchanged

**Zero dependencies are added to any repository manifest.** No `package.json`, `requirements.txt`, `pyproject.toml`, lock file, `go.mod` or `Gemfile` is created, updated or removed by this work.

- The design system **ships with the platform** and has no package identity, so it cannot be expressed in a manifest.
- The retired Material-UI packages — `"@material-ui/core": "^4.12.3"` at `package.json:L15` and `"@material-ui/icons": "^4.11.2"` at `package.json:L16` — are **left in place, untouched**, together with the declared-and-never-imported `chart.js` and `react-chartjs-2`. The legacy manifest is read-only reference.
- The two-level Update Set XML validator at [`../scripts/validate_update_set_xml.py`](../scripts/validate_update_set_xml.py) is written against the Python standard library only, so it introduces no dependency either.

**Decision log.** [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md).

### Rule-mandated dependency pins and their known advisories

**This entry is not one of the twelve flags, and it is deliberately not numbered `F13`.** The `F` inventory discharges prompt section 11.0's obligation, which concerns **requirements with no clean ServiceNow equivalent**. What follows is a different kind of item: a conflict between a **project rule** and the **published security baseline** of a third-party library that rule pins by exact version. It is recorded here so the conflict is visible at the same place a reader looks for everything the delivery could not resolve cleanly, without disturbing the twelve-flag count that this document, [`./validation-checklist.md`](./validation-checklist.md) and the decision log all assert.

**The scope of the pins.** Exactly one delivered artifact loads third-party code: the executive presentation at [`../../blitzy-deck/boston-startup-tracker-servicenow-executive-summary.html`](../../blitzy-deck/boston-startup-tracker-servicenow-executive-summary.html). Its three libraries are pinned to **exact versions stated verbatim by the presentation rule** — reveal.js `5.1.0`, Mermaid `11.4.0`, Lucide `0.460.0` — across five versioned files, two stylesheets and three scripts. **No part of the ServiceNow application loads any of them**: the scoped application's user interface is Service Portal with the platform's own AngularJS and Bootstrap, and the deck is never served by the instance, never loaded by the portal and carries no application data. The pins are also **not expressible in a repository manifest**, because the rule requires the deck to run with no build step and no local file dependency, so the libraries are referenced by `script` and `link` tag from a content delivery network.

**The conflict.** As of the assessment of **2026-08-08**, the pinned Mermaid release `11.4.0` is affected by published advisories that are fixed in a later release of the same major line. Upgrading is the ordinary remedy. **It is not available to this delivery**, because the version is not an implementation choice: the presentation rule states `11.4.0` verbatim, and the authority model forbids deviating from a rule to satisfy a heuristic or a baseline. The pin is therefore **retained deliberately**, and the residual risk is **accepted and disclosed** rather than silently carried.

#### Advisory scope, as identified on the assessment date

Six advisory records were identified against the pinned Mermaid release and its distributed build. For each one the table records the range the advisory states, whether the pinned `11.4.0` falls inside that range, and whether the code path the advisory describes is reachable in this deck. **The reachability answer is a fact about the delivered file, and every one of them is independently checkable in it.**

| Advisory | Subject | Stated affected range | `11.4.0` inside it | Reachable here | Basis for the reachability answer |
| --- | --- | --- | --- | --- | --- |
| `CVE-2026-71438`, `GHSA-c4c3-pg64-4m4v` | Prototype pollution through the configuration setters `mermaid.initialize`, `mermaidAPI.setConfig` and `mermaidAPI.updateSiteConfig`, which deep-merge caller-supplied configuration. Rated **Low** by the maintainer, on the ground that those entry points are documented as receiving configuration the integrating application controls. | Before `10.9.8`, and from `11.0.0-alpha.1` up to but excluding `11.16.1`. Fixed in `10.9.8` and `11.16.1`. | **Yes** | **No** | The deck calls `mermaid.initialize` **exactly once**, with an object literal written into the file. It never calls `setConfig` or `updateSiteConfig`, and no diagram source carries a `%%{init: ...}%%` directive or YAML frontmatter. No caller-supplied, fetched or typed value reaches any configuration entry point. |
| `CVE-2026-71437`, `GHSA-3rrr-jr9j-h3q3` | Prototype pollution when an untrusted `architecture-beta` diagram is rendered. | From `11.5.0` up to but excluding `11.16.1`. Fixed in `11.16.1`. | **No.** The pin precedes the first affected release. | **No** | Two independent reasons: the pinned release is below the range, and the deck contains no `architecture-beta` diagram. |
| `CVE-2025-54881` | Cross-site scripting through unsanitised sequence-diagram labels. | Before `11.10.0`. Fixed in `11.10.0`. | **Yes** | **No** | All five diagram sources are `flowchart`. The deck contains no `sequenceDiagram`. |
| `CVE-2026-71439` | Denial of service when a radar diagram is rendered. | Re-query at acceptance. | Re-query at acceptance. | **No** | The deck contains no radar diagram. |
| `CVE-2026-50159` | Cascading-stylesheet injection reaching elements that are siblings of the rendered diagram. | Re-query at acceptance. | Re-query at acceptance. | **No** | Every diagram source is a literal in the file. Nothing fetched, parameterised or typed is ever rendered. |
| `GHSA-m4gq-x24j-jpmf` | Prototype pollution and cross-site scripting through the sanitiser version bundled into the distributed builds. The advisory names those builds explicitly, and `dist/mermaid.min.js` reached over a content delivery network is among them. | The `10.x` line is fixed at `10.9.3`. Re-query the `11.x` line at acceptance. | Re-query at acceptance. | **No** | The deck does load exactly that build, so the bundled sanitiser is present. What the sanitiser processes is diagram source, and every diagram source is a literal in the file. |

**The advisory database is live and the table above is a snapshot taken on the assessment date.** Re-query all three pinned libraries on the acceptance date and record what comes back. A record that appears after the assessment date is a **new input to this decision**, not a defect in this record; a record that changes a `Re-query at acceptance` cell to a stated range is the answer that cell asks for.

#### Exposure

Five properties of the delivered file bound the exposure, and each is checkable in it without running anything.

1. **Five diagrams, all `flowchart`, all literal.** Every diagram source is written into the file between `<pre class="mermaid ...">` and its closing tag. There is no `sequenceDiagram`, no radar diagram and no `architecture-beta` diagram.
2. **One configuration call, with a literal argument.** `mermaid.initialize` is called once. `setConfig`, `updateSiteConfig` and the in-diagram `%%{init: ...}%%` directive appear nowhere.
3. **No input surface at all.** The deck reads no query parameter, accepts no form field, fetches no data and stores nothing. Rendering is driven by `mermaid.run` over the nodes already in the document.
4. **No privileged context.** The deck is opened as a local file over `file://`. It has no server, no session, no cookie, no credential and no privileged origin, and it carries no application data.
5. **Nothing depends on it.** No part of the ServiceNow application, the Update Set or the instance loads the deck or any of its three libraries. The portal runs on the platform's own AngularJS and Bootstrap.

#### Compensating controls, all delivered

- **Byte-pinning.** All five versioned assets carry a **SHA-384 `integrity` attribute** and `crossorigin="anonymous"`, so the exact reviewed bytes are the only bytes the browser will execute. A substituted or tampered file fails to load rather than running. The verification command and the expected outcome are gate [G-8](./validation-checklist.md#g-8--deck-structure) of [`./validation-checklist.md`](./validation-checklist.md).
- **No untrusted input reaches the library.** Every one of the five diagram sources is authored literally in the deck file. The deck accepts no user input, no query parameter, no form field and no fetched data, so no caller-supplied text ever reaches a Mermaid parser or its configuration setter.
- **A minimal blast radius.** The deck is a **static local file**. It has no server, no session, no credential, no cookie and no privileged origin, and it reads and writes nothing outside the page. Nothing in the ServiceNow instance, the scoped application or the Update Set depends on it.

#### Residual risk

Two residues remain after the compensating controls, and both are bounded.

- **The library stays un-upgraded for as long as the rule pins it.** If a future advisory describes a path the deck *does* exercise — a flowchart parser defect, or a defect in the rendering of a literal source — the compensating controls do not remove it, and the only remedy is re-pinning, which is the rule owner's act. The scope of that residue is whoever opens the deck, on their own machine, in a page with no privileged context.
- **A content-network compromise fails closed, not silently.** The SHA-384 digests mean substituted bytes do not execute; the asset is blocked instead. The consequence is a deck that does not render, which gate `G-8` detects, rather than a deck that renders hostile code.

#### The two options

Exactly two dispositions are available, and choosing between them is the rule owner's act rather than the delivery's.

| Option | What it requires | Consequence |
| --- | --- | --- |
| **A — re-pin** | The presentation rule is amended to a Mermaid release at or above `11.16.1`. The deck's pin, its `script` source and its SHA-384 `integrity` digest are re-derived, and gate `G-8` is re-run over all five assets. | The advisory closes. It also changes an artifact a rule specifies verbatim, which no agent may do on its own authority. |
| **B — accept** | The pin is retained, this record is signed, and the review trigger below is set. | The advisory stays open and disclosed. Nothing in the deck or the application changes. |

**Recommended disposition: B.** The recommendation rests on the reachability column above rather than on convenience: of the six advisories identified, one does not apply to the pinned release at all and the other five describe code paths this deck does not exercise.

#### Disposition record

The delivery has completed every field it can establish. **The four fields marked `REQUIRED — not yet supplied` are a human act, and no gate tick, script or agent can supply them.** Until all four carry a value this record's status is `OPEN`, and the corresponding row of [`./validation-checklist.md`](./validation-checklist.md) fails.

| Field | Value |
| --- | --- |
| Item | Mermaid, loaded by the executive presentation as `dist/mermaid.min.js` over a content delivery network. |
| Pinned version | `11.4.0`. |
| Fixing release for the advisories that apply | `11.16.1` for the two prototype-pollution records; `11.10.0` for the sequence-diagram record. |
| Authority for the pin | The presentation rule, which states `11.4.0` verbatim. A rule outranks a security baseline in this project's authority model, so the version is **not** an implementation choice and re-pinning is not the delivery's to make. |
| Assessment date | **2026-08-08** (UTC). |
| Assessed by | The delivery, as part of the frontend review. The assessment is the two tables and the exposure list above. |
| Scope of the risk | One artifact: `blitzy-deck/boston-startup-tracker-servicenow-executive-summary.html`. **Not** the scoped application, **not** the Update Set, **not** the instance, **not** any portal page, and no application data. |
| Mitigations in place | SHA-384 byte-pinning with `crossorigin="anonymous"` on all five assets; diagram sources authored literally in the file; no input surface; static local file with no privileged context. Stated in full under [Compensating controls, all delivered](#compensating-controls-all-delivered) above and verified by gate `G-8`. |
| Residual risk after mitigation | As stated under [Residual risk](#residual-risk) above: an un-upgraded library for as long as the rule pins it, and a fail-closed content-network compromise. |
| Recommended disposition | **B — accept**, on the reachability finding rather than on convenience. |
| Review trigger | Re-run this assessment when **either** the presentation rule is next amended **or** a new advisory is published that names a `flowchart` parsing or rendering path, whichever comes first. |
| **Decision — `A` or `B`** | **REQUIRED — not yet supplied.** |
| **Risk owner — the role accountable for the decision** | **REQUIRED — not yet supplied.** The rule owner, because the pin is a rule. |
| **Accepted by — name of the person** | **REQUIRED — not yet supplied.** |
| **Date accepted (UTC)** | **REQUIRED — not yet supplied.** |
| Advisory set re-queried on the acceptance date | Record the query date and what it returned, including any record absent from the snapshot above. |
| Status | **`OPEN`.** Set to `CLOSED — accepted` or `CLOSED — re-pinned` only when all four required fields carry a value. |

**Where this record is enforced.** [`./validation-checklist.md`](./validation-checklist.md) carries the advisory gate inside `G-8`, the definition-of-done item that refuses to be satisfied by a tick, and the final sign-off row that names the four required fields. The acceptance, its alternatives and its residual risk are logged as a **High**-rated decision in [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md).

**Decision log.** [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md).

## Superseded and retired inventory

This section records what is **not** in the application and which repository artifacts are left untouched. Every statement is a fact about the delivered state. The legacy Flask and React tree under `src/`, the infrastructure configuration under `config/`, and the five files under `documentation/` are **read-only reference**: nothing in them is modified, repaired, pruned or resurrected by this work.

### Attributes requested by the original brief that are not columns

**The source.** `documentation/Input Prompt.md` is the original stakeholder brief. It is a **single line** of prose, and prompt section 1.1 explicitly supersedes it. It asks for a list of active venture-backed companies with Boston headquarters that have raised institutional money in the past five years, and it names the attributes to aggregate.

**The platform position.** Prompt section 1.0's field definitions are **binding and complete** — no column may be added, omitted or inferred — so an attribute the brief asks for and prompt section 1.0 does not declare **does not become a column**.

Eleven requested attributes have no column in the delivered schema.

| Attribute as the brief words it | Nearest delivered column, if any |
| --- | --- |
| Sub-sector if relevant | None. `x_bst_startuptrk_startup.industry` is a single closed choice list of six values with no second level. |
| Number of employees | None. `x_bst_startuptrk_startup.employee_count_range` is a band, not a count. |
| Number of employees locally | None. No local-versus-total split exists on any column. |
| Headcount growth last 12 months | None. No growth column and no headcount history exists; see [F11](#f11--geographic-distribution-maps) for the same absence behind `F009-3`. |
| Last Fundraise Amount | None as a startup attribute. `x_bst_startuptrk_fundinground.amount_usd` records a round's amount, and no most-recent-round projection is stored on the startup. |
| Hiring? Yes/No | None. `x_bst_startuptrk_jobposting.active` marks a posting, not a company-level hiring flag. |
| Bonus: Employee count by department | None. |
| Bonus: Competitors | None. No competitor entity, reference or list exists — which is also why the company profile carries no "Similar Companies" tab. |
| Bonus: Site Traffic | None. |
| Bonus: Revenue | None. |
| Bonus: Tech Stack | None. |

**Three of the brief's signals do survive**, as columns on `x_bst_startuptrk_startup`, and their provenance is traceable to the source requirements document as well as to the brief.

| Column | The brief's wording | Corroborating citation |
| --- | --- | --- |
| `active` | "all \"active\" venture backed companies" | `SRS:L219` |
| `headquarters_location` | "with Boston HQs" | `SRS:L218`, "Limited to startups headquartered in Boston area" |
| `institutional_funding_last_5yrs` | "have raised institutional money in the past 5 years" | `SRS:L219`, "Focus on companies that have raised institutional money in the past 5 years" |

The brief's remaining requested attributes are delivered under different names within the closed field list: company name and website as `name` and `website`; industry as `industry`; the public description as `description`; fundraise stage as `funding_stage`; amount fundraised as `total_funding_usd`; investors through `x_bst_startuptrk_investor` with `x_bst_startuptrk_fundinground.lead_investor` and the join table; founders and executives as their own two tables; roles available as `x_bst_startuptrk_jobposting`; and most recent news as `x_bst_startuptrk_newsarticle`. Every column is specified in [`./data-model.md`](./data-model.md).

**Disposition — consciously excluded**, for the eleven attributes in the first table. They are recorded here so a future reader does not mistake their absence for an oversight.

**Decision log.** [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md).

### Capabilities named out of scope

Prompt section 7.2 names these capabilities as out of scope. Each row gives the repository artifacts left untouched and the one-line consequence for the delivered application.

| Capability | Repository artifacts left untouched | Consequence |
| --- | --- | --- |
| **Redis caching** | `config/redis.conf`, `src/backend/utils/cache.py`, the `redis` service in `docker-compose.yml` | **No platform cache layer is built.** No caching Script Include, no cached response and no cache-invalidation rule exists in the application. |
| **Elasticsearch** | `config/elasticsearch.yml`, the `elasticsearch` service in `docker-compose.yml` | **Search runs on encoded GlideRecord queries.** The portal search and the `/startups` list-and-search operation use case-insensitive `CONTAINS` and exact-match conditions built by `StartupSearchService`; no search index, analyser or full-text engine is configured. |
| **Docker, Nginx and Supervisor configuration** | `docker-compose.yml`, `config/nginx.conf`, `config/supervisord.conf`, `.dockerignore` | **No Dockerfile is authored** and no container, reverse proxy or process supervisor is part of the deliverable. The application runs on the Now Platform, whose runtime is the instance. |
| **IntegrationHub spokes** | — | **Generic REST steps bound to credential aliases, with a scoped script step as the documented entitlement fallback.** No spoke content set is installed, activated, referenced or opened, and no spoke action appears in either flow. A generic REST step is not a spoke, and neither is a scoped script step resolving an alias by name. The branch between the two arms, and which one each instance builds, is [F18](#f18--the-outbound-path-branch-between-the-rest-step-and-a-scoped-script-step). |
| **UI Builder** | — | **No experience or component record exists.** Zero `sys_ux_*` records of any kind are authored, and the UI Builder designer is not opened. The five routes are Service Portal pages. |
| **Automated NewsArticle ingestion** | — | **News articles are created by manual entry or CSV import only, and there is no sample CSV.** No flow writes `x_bst_startuptrk_newsarticle`, the staging table's `record_type` choice list carries no news member, and there are exactly six sample CSV files rather than seven. Manual entry is through the **News articles** module of the application menu, or a write to the `/news` REST resource. This is the position behind the `F004-4` cell of the roll-up above. |
| **Responsive design below 1024 pixels** | — | **No small-viewport refinement is authored.** See [Responsive stance — the 1024-pixel floor](#responsive-stance--the-1024-pixel-floor). |

The six sample CSV files and the import procedure are in [`./manual-build/06-staging-table-csv-import.md`](./manual-build/06-staging-table-csv-import.md) and [`../sample-data/README.md`](../sample-data/README.md); the flow build rules that forbid spokes are in [`./manual-build/02-flow-crunchbase-ingestion.md`](./manual-build/02-flow-crunchbase-ingestion.md) and [`./manual-build/03-flow-linkedin-ingestion.md`](./manual-build/03-flow-linkedin-ingestion.md).

**Decision log.** [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md).

### Ambiguity resolutions besides F6

Two further ambiguities in the requirements were resolved. Both are stated here as resolutions and nothing more.

**`participating_investors` — a List field and a named join table.** Prompt section 1.5 describes the attribute as a **List** and, in the same clause, names a physical table `x_bst_startuptrk_m2m_round_investor`. **Resolution: the join table is authoritative and is the only write target for participation.** `x_bst_startuptrk_fundinground.participating_investors` exists as a `glide_list` of references to `x_bst_startuptrk_investor` — the platform's List type, which is what the requirement declares — and it is **stored, read-only and derived**: a one-way projection of the join table, refreshed by the round-investor-link business rule. **Nothing writes both**, so there is no dual write and nothing to drift. The funding-round form surfaces the **related list** over the join table as the place an administrator adds and removes participants, and the REST layer emits `participating_investors` as a **JSON array** assembled from the join table rather than from the projected column.

**"Exactly 7 custom tables" against ten physical tables.** Prompt section 1.0 states exactly seven custom tables; the application declares ten. **Resolution: the seven-table count governs the entity tables**, and prompt section 10.0 criterion 1 is evaluated against those seven only. The other three are documented separately as **supporting artifacts**: `x_bst_startuptrk_m2m_round_investor`, named verbatim by prompt section 1.5; `x_bst_startuptrk_ingest_staging`, required by prompt section 4.0's fallback dataset; and `x_bst_startuptrk_rate_limit_counter`, required to emit prompt section 8.0's rate-limit response body with a computed retry interval.

Both resolutions are specified in full in [`./data-model.md`](./data-model.md), and both are among the ambiguity resolutions that [`../../docs/review/CRITICAL_DECISIONS.md`](../../docs/review/CRITICAL_DECISIONS.md) is required to call out.

**Decision log.** [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md).

### Defensive exclusion — the named gRPC path

Prompt section 7.2 excludes anything under a `/CalculationsGrpcService` path. A tree-wide search confirms that path is **absent from this repository**: no `CalculationsGrpcService` directory, file or reference exists, and no gRPC path of any kind exists. The exclusion is recorded here so its absence reads as a verified fact rather than an unchecked assumption.

The **operative** half of that clause — any backend that is not part of this ServiceNow scoped application — **is** active, and it covers the entire `src/` tree: the Flask backend, the data-collection package and the React frontend are all reference-only, and none is built, run, tested, repaired or provisioned.

## Related documents

| Document | Relationship to this inventory |
| --- | --- |
| [`./data-model.md`](./data-model.md) | The closed field list this inventory measures every excluded attribute against, and the specification of both ambiguity resolutions. |
| [`./access-control.md`](./access-control.md) | The three roles, the premium field matrix and the impersonation procedure behind [F2](#f2--automatic-entitlement-transition-on-payment), [F6](#f6--inclusion-criteria-field-ambiguity--resolved) and [F10](#f10--the-administrator-access-control-override). |
| [`./api-reference.md`](./api-reference.md) | The physical base path behind [F5](#f5--a-namespace-free-api-base-path), and the property inventory behind [F3](#f3--runtime-configurable-flow-schedule-interval). |
| [`./manual-build-instructions.md`](./manual-build-instructions.md) | The index that defers the icon-system split and the requirements with no platform equivalent to this document. |
| [`./manual-build/04-service-portal-pages-and-widgets.md`](./manual-build/04-service-portal-pages-and-widgets.md) | The build mechanics for every resolution in the [Design-system gap inventory](#design-system-gap-inventory). |
| [`./validation-checklist.md`](./validation-checklist.md) | The evidence record whose criterion 2 depends on [F10](#f10--the-administrator-access-control-override) and whose criterion 4 depends on [F3](#f3--runtime-configurable-flow-schedule-interval). |
| [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md) | The single source of truth for the "why" behind every entry above. |
| [`../../docs/decisions/TRACEABILITY_MATRIX.md`](../../docs/decisions/TRACEABILITY_MATRIX.md) | The bidirectional matrix that resolves at full coverage only if every entry above is present. |
| [`../../docs/review/CRITICAL_DECISIONS.md`](../../docs/review/CRITICAL_DECISIONS.md) | The five risk-ordered review entries, three of whose call-out categories this inventory supplies. |
