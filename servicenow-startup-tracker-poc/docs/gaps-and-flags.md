# Gaps and flags — `x_bst_startuptrk`

This document discharges the obligation of **prompt section 11.0**: *flag any requirement with no clean ServiceNow equivalent rather than silently omitting or half-implementing it.* It is the **single collection point** for that obligation across the whole package. Every requirement that the ServiceNow scoped application `x_bst_startuptrk` does not implement, implements only through a named workaround, or excludes outright is listed here — with its source, the platform's position on it, and what was consequently done.

**Read this document before reporting any part of the package as complete.** Seven of the nineteen flags below are places where the delivery is **less**, or more conditional, than a first reading of the requirements would suggest, and three of those carry the `Partially implemented, flagged` disposition — a requirement met in part that must never be claimed as met in full. Counts of delivered artifacts elsewhere in the package are counts of **artifacts**, not assertions that every requirement behind them is satisfied; where the two differ, this document governs.

The inventory is exhaustive by construction. A requirement that is neither implemented nor listed in this document is an unexplained omission, and the bidirectional traceability matrix cannot close without it. **No list below is abbreviated:** every excluded requirement, every unresolved gap and every untouched artifact is named individually, and no entry closes with an open-ended terminator standing in for items it does not name.

**On the word "exhaustive".** It is a claim about a construction, not about omniscience: every requirement was walked, and each one is either implemented, or listed here. Seven entries were added **after** the artifacts were first delivered: five when the artifacts were checked against the real provider contracts and the binding field list, and two when they were checked against the frozen artifact inventories — which is precisely the case the claim has to survive. A reader who finds an eighth should treat its absence as a defect in this document rather than as evidence that the shortfall was intended.

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
| [`./validation-gates.md`](./validation-gates.md) | The eleven required post-commit gates, and the acceptance-required `GATE-COL-01` and `GATE-SEC-01` through `GATE-SEC-03`. Fifteen checks block acceptance; the eleven post-commit gates are the subset that also triggers rollback. Also the external instance prerequisite for XML entity resolution. |
| [`./validation-checklist.md`](./validation-checklist.md) | The evidence record for the five success criteria, including criterion 2 for the access-control checks and criterion 4 for the scheduled runs. |
| [`../sample-data/README.md`](../sample-data/README.md) | The fallback-only posture of the sample dataset. |
| [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md) | The single source of truth for every "why" behind every entry in this document. |
| [`../../docs/decisions/TRACEABILITY_MATRIX.md`](../../docs/decisions/TRACEABILITY_MATRIX.md) | The bidirectional matrix this inventory closes the unimplemented half of. |
| [`../../docs/review/CRITICAL_DECISIONS.md`](../../docs/review/CRITICAL_DECISIONS.md) | The five risk-ordered review entries, three of whose call-out categories intersect this inventory. |

## Numbering convention

**Five identifier schemes appear on this page, and the first two are easily confused.** Read the padding.

| Scheme | Form | Meaning | Examples |
| --- | --- | --- | --- |
| **This document's flag identifiers** | `F` followed by **one or two** digits, never zero-padded | A flag in this inventory. There are exactly nineteen, `F1` through `F19`. | `F1`, `F6`, `F13`, `F19` |
| **Source requirement identifiers** | `F` followed by **three** zero-padded digits, optionally then a hyphen and a sub-number | A feature or a requirement in the source requirements document, `documentation/Software Requirements Specifications (SRS).md`. There are ten features, `F001` through `F010`, each carrying five requirements. | `F009`, `F009-5`, `F010-1`, `F001-1`, `F003-3`, `F006-4`, `F007-5` |
| **Design-system gap identifiers** | `G` followed by one digit | A gap in the user-interface design system. There are exactly seven, `G1` through `G7`. | `G1`, `G6`, `G7` |
| **Operator obligation identifiers** | `OB-` followed by one digit | An action owned by a human operator or platform owner rather than by a delivered artifact. There are exactly three, `OB-1` through `OB-3`, collected under [Operator obligations](#operator-obligations). | `OB-1`, `OB-3` |
| **Open integration limitation identifiers** | `OPEN-` followed by one digit | A capability built in full that cannot be exercised against its live source until a third party supplies missing information. There is exactly one, and it is **not** a flag and **not** counted into the nineteen. | `OPEN-1` |

Every source requirement identifier in this document is written in its three-digit padded form. `F1` is this document's first flag; `F001` is the source document's first feature; `F001-1` is that feature's first requirement. The three are distinct and are never interchangeable.

Source requirement identifiers are cited as `SRS:L<line>` against `documentation/Software Requirements Specifications (SRS).md`. Repository source files are cited as `<path>:L<line>` or `<path>:L<first>-L<last>`.

## Dispositions

Every **flag** in this document carries exactly one of the **first four** dispositions below. The fifth, **Blocked on an external prerequisite**, is carried by **no flag**: it is the vocabulary the single open integration limitation `OPEN-1` uses, and it is defined here so the two vocabularies sit side by side and cannot be conflated. Which flag carries which is stated in the [Flag summary](#flag-summary) table and totalled beneath it.

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

No flow, Script Include, business rule or scheduled job in `x_bst_startuptrk` fetches or parses an HTML page. The two ingestion flows call the two named APIs through **generic Flow Designer REST steps bound to a credential alias by name — the primary path — with a scoped script step resolving the same alias by name as the documented fallback**. **Which arm is built is decided by the pre-flight, not by this page:** the two conditions are stated in [F18](#f18--the-outbound-path-branch-between-the-rest-step-and-a-scoped-script-step), the selection table and the recording obligation are section 3.1 of each flow guide, and the arm actually chosen is an **observed value the operator records there before the flow is activated**. Neither arm involves a spoke and neither is HTML scraping, which is all this flag needs to establish. See [`./manual-build/02-flow-crunchbase-ingestion.md) and [`./manual-build/03-flow-linkedin-ingestion.md`](./manual-build/03-flow-linkedin-ingestion.md). Neither arm is a spoke; the branch is [F18](#f18--the-outbound-path-branch-between-the-rest-step-and-a-scoped-script-step).

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

**All three are asserted by the Automated Test Framework**, and the assertions are named so the claim is checkable: step 90 of each suite-10 test reads the published `choice_unmatched` events and asserts `deviation="true"` on exactly the values whose list declares no `Other` member — two per source — each carrying the exact outcome text above, and `deviation="false"` on the rest; step 100 asserts the `rule3_deviations` counter as its own figure and asserts it never exceeds `unmatched`. Before those assertions existed this flag's shortfall could have fallen to zero without any test noticing. Adding an `Other` member to any of the six is **forbidden**: the field-list fidelity gate counts columns and choice values against the binding list, so the addition would fail the gate it was meant to satisfy. Anyone who believes the lists were intended to be extensible should reopen that gate rather than edit the mapper — the permanent zero in `rule3_deviations` afterwards is what would confirm the reading.

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

**The platform position.** This is a **provider** limitation and not a platform one, and no instance, entitlement or credential of this delivery can work around it. **No generally available LinkedIn resource enumerates an arbitrary company's people**, so founders and executives have no generally available read path. The Job Posting API is a **write** API for publishing an organisation's own postings, not a read API for third-party postings. What *is* generally available is organisation identity — `GET /rest/organizationsLookup` and the versioned organisation endpoints — which confirms the credential, the two mandatory versioning headers and the company identity, and returns none of the three record types. The only route to a read path for the three record types is **admission to an approved provider partner programme that grants read resources for them**; such a grant is a provider act, its resources and response shapes are determined by the programme rather than published generally, and this delivery can neither obtain nor assume it.

**The disposition — partially implemented, flagged.** The flow exists, runs on the cadence, authenticates through its alias and writes all three record types; its **live call is an organisation-identity probe rather than an acquisition**, and the rows themselves come from the sanctioned fallback dataset. The consequence must be stated wherever a run is reported: **a credential alone never makes `LinkedIn Ingestion` `live validated`.** An organisation-identity probe proves the credential, not acquisition, so a run whose rows came from the fallback dataset is labelled `fallback validated` however good the credential is. The one route that would change that label is the partner grant described above, tracked as `OPEN-1` and gated on the eight-row endpoint-contract declaration in [`./manual-build/03-flow-linkedin-ingestion.md`](./manual-build/03-flow-linkedin-ingestion.md); **as delivered, and for as long as no such grant exists, the label is `fallback validated` on every instance.** Prompt section 10.0 criterion 4 explicitly accepts the sample-dataset substitute, so this does not block acceptance; it constrains only what the evidence may claim.

**Where this is stated.** [`./manual-build/03-flow-linkedin-ingestion.md`](./manual-build/03-flow-linkedin-ingestion.md); the labelling rule in [`../sample-data/README.md`](../sample-data/README.md) and in criterion 4d of [`./validation-checklist.md`](./validation-checklist.md).

**Decision log.** [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md) — `D-233`.

### F16 — Three columns the live path cannot fill

**The requirement.** Populate every column of the binding field list from the named sources.

**The source.** Prompt section 1.0 for the columns, prompt section 4.0 for the sources.

**The platform position.** Three columns have no counterpart in what the providers publish.

| Column | What the provider publishes for it | What the flow does |
| --- | --- | --- |
| `startup.institutional_funding_last_5yrs` | Crunchbase exposes no such field. The five-year window is expressible only as a **query predicate**, not as a returned value. | Left unset by the live path. The fallback dataset carries it as a column, so a fallback-sourced startup has it. |
| `investor.aum_usd` | Crunchbase v4 publishes no assets-under-management field. | Left unset by the live path. The fallback dataset carries it as a column, so a fallback-sourced investor has it. |
| `fundinground.source_url` | The funding-round search response carries no public round URL; `permalink` is a slug rather than an `https` URL and the boundary validation would refuse it. | Left unset by the live path rather than filled with a value that is not a URL. The fallback dataset carries a real `https` locator per round. |

**The disposition — partially implemented, flagged.** The columns exist, carry their specified types, and are readable and writable by hand and by the fallback path; what is unavailable is **live population**. No placeholder, sentinel or inferred value is written into any of the three: an unset column is honest where a fabricated one would be indistinguishable from data. Two of the three are premium-gated, so a base-role caller cannot tell an unset value from a denied one in any case.

**The fallback fixtures now agree with this entry, and once did not.** Earlier revisions of `crunchbase_startups_sample.csv` and `crunchbase_funding_rounds_sample.csv` published `institutional_funding_last_5yrs` and `source_url` **inside the `raw_payload` envelopes**, as though Crunchbase returned them — 13 and 11 occurrences respectively. A fixture that supplies a key the provider does not publish exercises the mapper against a shape it will never meet, and it contradicted this entry and section 3.4 of guide 02 directly. Both keys have been **removed from every payload**; the flattened staging columns keep their values, because the staging table is an application shape rather than a provider echo. The resulting live-versus-fallback differences are catalogued as rows 5 and 6 of [`../sample-data/README.md`](../sample-data/README.md).

**Two further specifics, stated because a reader can otherwise assume more capability than exists.** `D-210` decided an entitlement-gated derivation of `institutional_funding_last_5yrs` from funding-round evidence; the delivered `IngestionMapper.LIVE_ALIASES` declares a **single** alias for that field — the application's own column name — and implements **no** derivation, so the decision is recorded rather than built and the live path leaves the column unset, which is the behaviour `D-210`'s own risk clause describes for a plan without the entitlement. And `source_url`'s alias chain is `['source_url', 'permalink']`, whose second member is a bare slug that `isHttpsUrl()` refuses, so that fallback alias is **inert** rather than a working second route. Neither is a defect to repair by inventing provider data; both are bounded and named here.

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

| # | Condition | What it determines |
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

> **Marked for prominence.** An operator who runs a live ingestion and does not clear the staging table has left verbatim upstream person data on the instance indefinitely. **No delivered artifact removes it**, and the only controls over it are access controls. The obligation that closes this is [`OB-1`](#ob-1--retention-and-erasure-over-the-staging-table), and it blocks acceptance.

**The requirement.** Not a stated requirement. It is a consequence of one that *is* stated: prompt section 4.0 requires a staging table whose shape mimics the expected API response, and Agent Action Plan section 0.4.3 gives that table a `raw_payload` column holding the upstream response verbatim alongside the flattened person columns `name`, `title`, `bio`, `linkedin_url` and `contact_email`. Nothing in the prompt or the plan says how long that data lives.

**The source.** Prompt section 4.0 and Agent Action Plan sections 0.4.3 and 0.4.7.

**The platform position.** The platform would support it readily — a scheduled job and a Script Include would do it — but the **artifact inventories are closed**. Agent Action Plan section 0.4.5 declares exactly eight Script Includes, section 0.4.7 exactly eleven system properties, and section 0.4.2 exactly three business rules and one scheduled job, and that one job is the rate-limit counter prune. A retention capability would need a ninth Script Include, at least two further properties and a second scheduled job, so it cannot be delivered without departing from the frozen plan.

**The disposition — flagged, not implemented.** No delivered artifact minimises, prunes or erases a staging row, and there is no data-subject erasure method. Three delivered mechanisms bound the exposure instead, and they are access controls and one narrow window rather than a retention policy:

| Mechanism | Table | Effect |
| --- | --- | --- |
| `access` `package_private` and `ws_access` false | `x_bst_startuptrk_ingest_staging`, `x_bst_startuptrk_rate_limit_counter` — and, with the same posture but no personal data, `x_bst_startuptrk_m2m_round_investor` | None of the three is addressable from another application scope and none is served by the platform Table API. **All three supporting tables carry this posture**, which is what `GATE-SEC-01` in [`./validation-gates.md`](./validation-gates.md) asserts by expecting exactly three `package_private` tables; the two named first are the two this gap is about, because they are the two that hold personal data. |
| Read, write, create and delete controls granting `x_bst_startuptrk.admin` alone | Both | No caller holding only `x_bst_startuptrk.user` or `x_bst_startuptrk.premium_user` can reach a row on either table by any route. |
| The hourly `Prune rate limit counters` job | Counter only | Every row whose window has closed is deleted, so the counter table's retention is the window length — sixty seconds at the shipped value. The `caller` references it holds survive minutes. |

**The gap is transferred to a gated operator obligation, not left open.** [`OB-1`](#ob-1--retention-and-erasure-over-the-staging-table) names the owner role, the schedule, the retention period and the evidence, and **acceptance is blocked until that evidence is recorded**. What follows is the residual gap that obligation exists to cover.

**The staging table has no equivalent, and that is the residual gap:** a settled row keeps its `raw_payload` and its five person columns until an administrator deletes it, on a live run exactly as on a fallback run. **What a human must do:** clear settled staging rows as part of operating the flows. The two supported routes, and the two rules that bind either of them, are in [`./data-model.md`](./data-model.md) and [`./manual-build/06-staging-table-csv-import.md`](./manual-build/06-staging-table-csv-import.md).

**The gap is closed procedurally, and the procedure is acceptance-blocking rather than advisory.** Because no property, business rule or scheduled job in this application bounds the lifetime of staged personal data, the **evidence is the control**: [section H3a of `../docs/validation-checklist.md`](./validation-checklist.md#h3a--the-retention-obligations-acceptance-blocking) carries one row per operator obligation, each requiring the window applied, the mechanism, an actor and a date, and **an unfilled row is a failed gate rather than a pending action**. A row may read `not applicable` only with its reason written in. Obligation 4, the flow execution context, additionally requires the platform owner's written acknowledgement, because those tables sit outside the `x_bst_startuptrk` scope and prompt section 6.0 forbids this application from reaching them. `D-205`'s timed control remains **recorded and not delivered**, and `D-324` is the decision that made the evidence blocking instead. **What a human must do:** clear settled staging rows as part of operating the flows. The two supported routes, and the two rules that bind either of them, are in [`./data-model.md`](./data-model.md) and [`./manual-build/06-staging-table-csv-import.md`](./manual-build/06-staging-table-csv-import.md).

**One surface is not affected, and it is worth saying so.** The **logs** hold nothing to erase. `IngestionLogger` records an identifier only when it is a platform record identifier or an opaque `<kind>:<token>` reference, and a value only when it is a short enumeration label; everything else becomes the literal `(redacted)` or `(blank)`, and nothing derived from a dropped **field value** — no hash, no digest, no fingerprint — is recorded on any surface. The one fingerprint the application computes, `AppProperties.fingerprint()`, is over the text of a **caught fault** and exists so that text need not be stored: what is written is a closed code, an eight-character reference and the text's length. It identifies the fault, not a value that text might quote, and as a 32-bit rolling hash over arbitrary-length input it is far too collision-prone to identify one. So no name, address, biography, URL or upstream message reaches the flow execution log or the system log in the first place.

**Decision log.** [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md).

## Open integration limitations

**These are not flags, and they are counted separately from the nineteen.** A flag records a *requirement* the platform cannot cleanly satisfy. An open integration limitation records a *capability that is built in full but cannot be exercised against its live source* until a third party supplies information this delivery cannot obtain. The distinction matters operationally: a flag closes only if the requirement changes, whereas an open limitation closes the moment the missing information arrives, with no code change and no rebuild.

There is exactly **one**, and it carries the `OPEN-` prefix so it can never be mistaken for an `F` flag or counted into the nineteen.

### OPEN-1 — Live LinkedIn ingestion, pending an endpoint-contract declaration

**The capability.** Ingestion of Founder, Executive and JobPosting records from LinkedIn, on the configured cadence, through the `x_bst_startuptrk.linkedin_oauth` alias.

**What is delivered.** All of it, except the live call. The five LinkedIn custom actions are built and published, the scheduled flow is assembled, activated and validated, the alias and connection definition records are built, and the ingestion runs end to end in `fallback` mode against [`../sample-data/`](../sample-data/). Nothing about the build is provisional.

**What is unavailable, and why.** **Live LinkedIn ingestion is formally declared unavailable, on the provider grounds stated in [F15](#f15--linkedin-publishes-no-read-api-for-people-or-third-party-job-postings).** The endpoint contract for this source is undetermined: current company resources are versioned and product-gated and reject a request that omits the version header, no generally available resource enumerates an arbitrary company's employees, and job-posting resources require a separate approved partnership whose granted resources and response shapes depend on which partnership is granted. The legacy resource paths in `src/data_collection/api_integrators/linkedin_integrator.py` descend from a scaffold that cannot run and are **not** a verified contract, so they are not shipped as though they were.

**The gate.** The live path is gated on an **eight-row endpoint-contract declaration** the credential owner completes in [`./manual-build/03-flow-linkedin-ingestion.md`](./manual-build/03-flow-linkedin-ingestion.md): product or partner programme, API version header and value, base URL, granted scopes, resource path per record type, response envelope, pagination contract and rate limit. **The live-call script refuses to issue a request while any row is undeclared**, so an incomplete declaration cannot produce a silent partial call.

**Disposition — open, with the build complete.** Founder, Executive and JobPosting records arrive **only** from the fallback dataset until the declaration is completed, so live coverage of those three entity tables is an open item rather than a delivered capability. Every LinkedIn result is labelled `fallback validated` and never `live validated`. The declaration may never be completed, in which case the limitation persists.

**How it closes, and what closing it actually costs.** The credential owner completes the eight rows and provisions the credential; guide 03's resumption procedure is followed. **Completing the declaration is necessary and not sufficient**, and the difference matters to anyone planning the work: row 5 of the declaration permits the answer that a record type has **no** available resource, which on the evidence of [F15](#f15--linkedin-publishes-no-read-api-for-people-or-third-party-job-postings) is the expected answer for all three — in which case the declaration confirms the limitation rather than lifting it. If a real resource does exist, live acquisition additionally requires **editing `IngestionMapper`**, whose `unwrapLive()` expects a `data.elements` envelope and whose `linkedin.*` alias chains are written against a synthetic member shape — a Script Include **inside the Update Set**, so a code change with its own preview and commit — and **new flow-test fixtures** built from the real envelope, because the shipped LinkedIn fixtures are synthetic rather than captured. Then, and only then, `x_bst_startuptrk.ingestion.source_mode` moves to `live` only once the connection test passes. No artifact of this delivery is rewritten.

**Distinguish it from the credential gap.** The Crunchbase source has a **published, verified** contract and needs only its credential. LinkedIn needs the credential **and** the contract declaration, and the declaration needs the partner grant. The two shortfalls are different in kind, and only LinkedIn's is recorded here. **The observed readiness of each alias — and therefore which source is in `fallback` mode on a given instance — is stated in exactly one place, dated: [the recorded posture for this delivery](./manual-build/01-connection-credential-aliases.md#the-recorded-posture-for-this-delivery) in guide 01.** This entry does not restate it.

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

### The seven flags that are not source-requirement exclusions

The roll-up above walks the **source requirements document**, so it reaches F1 through F12 and no further. **F13** through **F19** are not exclusions of a source requirement at all: each is a shortfall against the **authoritative prompt**, discovered where the prompt meets a real provider contract or its own binding field list. They are reached through the prompt-section side of the traceability matrix rather than through this roll-up.

| Flag | Prompt section it falls short of | Nature of the shortfall |
| --- | --- | --- |
| [F13](#f13--cleaning-rule-3s-other-coercion-in-six-choice-lists) | 4.0 cleaning rule 3, against 1.0's binding choice lists | Two requirements of the same authority conflict; the rule is applied in four of ten lists and the shortfall is counted at run time |
| [F14](#f14--the-crunchbase-authentication-model) | 4.0 credential aliases | The specified authentication model is not one the provider accepts; the alias is retained as the key's only home and the transport changes |
| [F15](#f15--linkedin-publishes-no-read-api-for-people-or-third-party-job-postings) | 4.0 ingested entities | The provider publishes no read API for three of the six record types; the sanctioned fallback dataset supplies them |
| [F16](#f16--three-columns-the-live-path-cannot-fill) | 1.0 field list, against 4.0's sources | Three columns exist and are writable but have no live source |
| [F17](#f17--a-round-with-several-lead-investors) | 1.5 `lead_investor` | The binding shape cannot represent what the provider reports; nothing wrong is stored in its place |
| [F18](#f18--the-outbound-path-branch-between-the-rest-step-and-a-scoped-script-step) | 4.0 Flow Designer REST steps referencing the aliases by name | The platform resolves a credential alias for only one of the two transports the two sources need, so one source's outbound call is a scoped script step rather than the declarative REST step |
| [F19](#f19--no-retention-minimisation-or-data-subject-erasure-of-staged-data) | 4.0 staging table, against the eleven-property inventory of the plan | Staged personal data has no shipped retention control, because the property inventory is fixed at eleven and a twelfth cannot be added; the control is an acceptance-blocking operator obligation instead |

None of the seven is a platform limitation in the sense of a missing capability. Four are provider or requirement-conflict limitations, one is a consequence of the field list being binding, one is a transport asymmetry in how a credential alias resolves, and the last is a consequence of the plan freezing the property inventory at eleven — so none is closable by building more inside `x_bst_startuptrk` under the plan as frozen.

## Design-system gap inventory

The user-interface design system is **platform-native**: Service Portal's AngularJS 1.x with **Bootstrap 3.3.6**, both already present on the instance. It is not an npm or PyPI package, there is nothing to install, and it cannot be pinned from this repository — its version is bound to the platform release. UI Builder is forbidden by prompt section 5.0, so no `sys_ux_*` record of any kind is authored.

Seven gaps exist between what the five portal routes need and what that library provides. Six are resolved inside the system. One has no resolution.

| ID | Gap | Resolution |
| --- | --- | --- |
| **G1** | **Charts** for the Dashboard / Trends route. Bootstrap 3 has no chart component. | Platform reporting surfaced through a report or chart widget, or Angular-rendered inline SVG in a custom widget. **Both mechanics are specified in buildable detail** in [`./manual-build/04-service-portal-pages-and-widgets.md`](./manual-build/04-service-portal-pages-and-widgets.md) and the `render_mode` option of `bst-trends-charts` selects between them: `svg` renders the Angular-bound inline SVG bar chart of [The inline SVG chart](./manual-build/04-service-portal-pages-and-widgets.md#the-inline-svg-chart), carrying its element list, its five geometry constants, every `ng-attr-*` binding and its accessible `title`, `desc` and companion table; `report` embeds one of **two allowlisted, protected, count-only** saved reports per [The report embed](./manual-build/04-service-portal-pages-and-widgets.md#the-report-embed) — an arbitrary readable report is inadmissible, because a report aggregating a premium-gated currency column would publish a figure the field-level access control exists to withhold. **`svg` is the shipped mode** on both dashboard instances, and `report` falls back to `svg` whenever the allowlist check, the count-only check or the `report-chart` availability check does not pass, so a chart renders in every configuration and no configuration can embed an unvetted query. **Nothing is lost in the migration:** the legacy manifest declared `chart.js` at `package.json:L19` and `react-chartjs-2` at `package.json:L21` but **never imported either**, and the legacy dashboard at `src/frontend/components/Dashboard/Dashboard.tsx:L68-L106` is a six-panel grid-and-paper layout — QuickStats, RecentUpdates, TrendingStartups, FeaturedCompanies, LatestNews and JobOpenings — with **no chart import at all**. |
| **G2** | **Multi-select chip input** for `x_bst_startuptrk_investor.focus_areas`. No multiselect and no chip control exists in the library. | **Read display and write entry are served by different surfaces, and only one of them is the portal.** The portal renders the value read-only as `.label` chips inside a `.panel-body`, built in `bst-investor-profile`. The **write** path is the platform's own form view on `x_bst_startuptrk_investor`, which renders a multi-choice column natively and is reached from the application menu the Update Set delivers — the same surface that serves the administrative interface without a sixth portal route. The stock **Form** widget would be the in-portal alternative, and this build places one on no page and opens one from no widget: all eight widgets are read-only, and layer 2 of the access controls grants `write` to `x_bst_startuptrk.admin` alone, so a form offered to either non-administrative role would present a save control the platform then refuses. |
| **G3** | **Loading indicator.** Bootstrap 3 has no spinner. | Service Portal's own loading indicator, or a striped progress bar — `.progress` containing `.progress-bar.progress-bar-striped.active`. The striped form is built in `bst-startup-results`. |
| **G4** | **Card media**, the image surface of a result card. | A Bootstrap media object image — `.media-left` containing `img.media-object` — bound to `x_bst_startuptrk_startup.logo_url`. `.thumbnail` is the alternative container. Built in `bst-startup-results` and in the company-profile header. |
| **G5** | **Premium upsell and paywall treatment** for `x_bst_startuptrk.user`. No library component exists for the pattern. | **Two forms, one for each granularity, and both present together on a surface that has a denied field.** In the denied field's own position — the table cell, list-group row or list item where the value would have been — a `<span class="label label-info">Premium</span>`, so the caller can see *which* value is withheld. Once per surface, at the end of it, an informational alert panel carrying a primary call to action — `.alert.alert-info` containing a `.btn.btn-primary` — so the caller can see *why* and what to do; packaged as the reusable `bst-premium-upsell` widget and embedded by `bst-company-profile`, `bst-investor-profile` and `bst-account-summary`, with `bst-startup-results` rendering the same notice inline because it is not one of the partial's three declared hosts. **Never a blank, an empty cell, a zero or a dash**, and never the alert repeated per field or the marker used as the surface treatment. The marker's fill is `$label-info-bg`, chosen for WCAG 2.1 AA contrast against white; `.label-default` is reserved for *categories* and is never the premium marker. |
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

### The native platform read route on the application tables, and why it is closed

**This entry is not one of the nineteen flags, and it is deliberately not numbered.** The `F` inventory discharges prompt section 11.0's obligation, which concerns requirements with no clean ServiceNow equivalent. This is a delivered design decision and its residual risk, recorded here because the earlier build made the opposite choice and a reader of that build's documentation would otherwise be misled.

**What is delivered.** All ten application tables carry `access` `package_private`, `read_access` `false` and `ws_access` `false`, and every cross-scope write, schema and configuration capability is `false` on all ten. `GET /api/now/table/x_bst_startuptrk_<entity>` therefore serves nothing, and a script in another application scope — including a Global-scope background script an operator pastes in — cannot read a row either. **One caller-facing read route exists**, the Scripted REST API at `/api/x_bst_startuptrk/v1/`, and every control this application defines applies to it: the two `REST_Endpoint` execution controls, the fixed-window rate limiter, the inclusion filter, the secured read path and the per-field omission gate.

**What the earlier revision accepted, and what closing the route removed.** The seven entity tables were previously `access` `public` with `read_access` and `ws_access` `true`, so that the eleven required post-commit gates could read rows directly. Three residual risks were recorded against that posture, and all three are now removed rather than compensated:

| # | Risk under the earlier posture | Status now |
| --- | --- | --- |
| 1 | The Table API route sat outside the application's fixed-window rate limiter, so a caller holding a scoped role could issue reads the `x_bst_startuptrk.rate_limit_requests` budget never counted. | **Removed.** The route does not serve these tables. Every caller-facing read now passes through `RateLimitService`. The platform inbound rate-limit rule that was recommended as defence in depth is no longer needed for this purpose, and is neither required nor gated. |
| 2 | The Table API route sat outside the two `REST_Endpoint` execution controls, whose particular contribution is that the platform's own default REST control admits any authenticated internal user. | **Removed.** Both controls now govern the only route. `GATE-SEC-03` records that they committed. |
| 3 | `access` `public` with `read_access` `true` let a script in another application scope read entity rows through unsecured record access, which evaluates **no** access control — so all seven premium fields were readable by a path the field-level controls never saw. | **Removed.** `package_private` with `read_access` `false` denies the cross-scope read at the scope boundary. This was the material one: prompt section 2.0 requires the base role to receive an access denial on those seven fields, and a route that never evaluates the field control cannot deliver one. |

**Why it was accepted before, and why that reasoning did not hold.** The stated ground was that removing the exposure meant setting `ws_access` `false`, which would make the eleven required gates unexecutable. That was a real constraint and a wrong conclusion: AAP section 0.11.2 requires a successful read establishing that each entity table exists after the commit, and it does not require that read to be a row read. `GATE-TBL-01` through `GATE-TBL-07` now read each table's `sys_db_object` record within the scope and assert its name together with the three closed flags — strictly more than a row read established, since it also proves scope membership and the containment posture. The eleven gate identifiers, the eleven-of-eleven rollback decision and the acceptance contract are all unchanged. A second ground, that a cross-scope script must already be privileged, conflated writing such a script with being a caller of one; the counter-argument is set out in [`./access-control.md`](./access-control.md#why-every-table-is-sealed-including-the-seven-a-caller-does-read).

Two further consequences were closed with them: a native list route sat outside `StartupSearchService`'s inclusion plan, so a record prompt section 1.1 excludes from search results was returned anyway; and it sat outside the fixed-window rate limiter, so the `x_bst_startuptrk.rest.rate_limit_requests` budget did not count those reads.

**What the closure costs, and how the cost is met.** A sealed table cannot be verified by reading a row over the Table API, so the seven required post-commit gates read each table's `sys_db_object` definition record instead — asserting both its presence and its three posture values — and the class-3 diagnostic `GATE-SEC-04` opens each entity table through `GlideRecordSecure` from inside the scope to establish that the ACL-respecting path still serves it. [`./validation-gates.md`](./validation-gates.md) carries both. Nothing at run time is affected: the portal widgets, the two flows, the three business rules and the ten test suites all execute inside the scope, and a Scripted REST API is unaffected by a table's `ws_access` value.

**The one residual risk, stated plainly.** An operator with instance-level privilege can still change a table's posture after the commit, and can still read any table on the instance by other means that privilege affords. That is a property of instance administration rather than of this application, and it is bounded rather than eliminated: `GATE-SEC-01` records the posture of all ten tables on every deployment, so a posture that drifted from the delivered one is visible in the deployment record rather than silent. The decision, its alternative and this risk are recorded at `D-027` and `D-254` in [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md).

### Flow execution context retention

**This entry is not one of the nineteen flags, and it is deliberately not numbered.** It is a **platform-owner procedure** that this delivery is forbidden from implementing, recorded in full so the obligation is legible and actionable rather than assumed to be handled.

**The surface.** Flow Designer persists each execution's step inputs and outputs in the platform's own flow execution tables. **Exactly one step output of one flow carries upstream content into them**, and it is worth being precise about which, because an overstatement here is as misleading as an omission:

| Flow | Output | Step | What it actually carries |
| --- | --- | --- | --- |
| Crunchbase | `rows` | 3, consumed by 4 and 5 | The typed row envelopes of the live read: organisation, funding-round and investor payloads. **Commercial content — company names, locators, amounts, dates. No personal data**, because Crunchbase supplies only the `startup`, `investor` and `funding_round` record types (`IngestionMapper.SOURCE_TYPES`). |
| Crunchbase | `rows` | 4 | On the fallback branch, one `{ record_type, staging_id }` envelope per claimed row. **No content of any kind** — a record type and a platform identifier. |
| LinkedIn | `rows` | 3 | **Always `[]`.** That flow's step 3 is a probe and emits no row set at all; its build-verification criterion 7 asserts the empty array. |
| LinkedIn | `rows` | 4 | One `{ record_type, staging_id }` envelope per claimed row. **No content of any kind.** |

**No step of either flow declares a `response_body` output, and neither ever publishes an upstream response body.** Guide 02's step 3 declares eleven outputs and none of them is the body; guide 03 states in terms that it has no `response_body` input and emits no response body. Two consequences follow, and both are checkable rather than asserted:

- **The person-bearing record types cannot reach the flow execution history at all.** `founder`, `executive` and `job_posting` are supplied only by LinkedIn, LinkedIn has **no live read route** (`F15`), and its rows therefore only ever travel as a record type and a staging identifier. The personal values themselves move from the staging table into the entity tables **inside one script step call**, never across a step boundary.
- **What remains on the surface is commercial, not personal.** The Crunchbase live `rows` output is the one place upstream content is published, and it is organisation data. The procedure below still applies to it — a competitor's funding position is not public because it is not personal — but it is not a data-subject exposure.

The Crunchbase `rows` output cannot be removed without breaking the pipeline: step 4 evaluates it and step 5 cleans it. Everything else those flows emit is a run identifier, an opaque record reference, a bounded code, a counter, a per-run arrival ordinal or the literal `(redacted)` — the five permitted classes, enforced by `IngestionLogger` and enumerated in **What the execution context retains** in [`./manual-build/02-flow-crunchbase-ingestion.md`](./manual-build/02-flow-crunchbase-ingestion.md#what-the-execution-context-retains) and [`./manual-build/03-flow-linkedin-ingestion.md`](./manual-build/03-flow-linkedin-ingestion.md#what-the-execution-context-retains).

**Where the obligation sits.** The flow execution tables are platform tables outside the `x_bst_startuptrk` scope, and prompt section 6.0 forbids this application from modifying anything outside its scope. Their retention window, their cleanup schedule and their read access are the platform owner's to set — recorded at `D-378`. **Clearing the staging table does not clear them**, and neither does the one scheduled job this delivery ships, which prunes only rate-limit counter rows. Any statement that this application's retention posture covers its own logs is true and says nothing about this surface.

**What the platform owner is asked to do.** Four items. None is satisfied by anything in this package.

| # | Action | How to confirm it was done |
| --- | --- | --- |
| 1 | **Record the instance's current flow-execution-data retention window** — how long a completed flow execution context and its step data survive before the platform's own cleanup removes them. | The retention configuration and the cleanup schedule, captured as observed values with the date observed. |
| 2 | **Set that window to the shortest value the instance's own operational needs allow**, and record the value set and who set it. Ingestion troubleshooting needs days, not months. | The before and after values. |
| 3 | **Record who can read a flow execution context on this instance**, by role, and confirm that the set is no wider than the set that may read `x_bst_startuptrk_ingest_staging` — which is `x_bst_startuptrk.admin` alone, because that table is `package_private` with `ws_access` `false`. Where the flow-execution reader set is wider, record the difference as an accepted exposure with a named owner. | The role list, and either an equality statement or a recorded exposure. |
| 4 | **Confirm each ingestion flow's own logging level is at the least verbose setting that still records step outcomes.** Guides 02 and 03 require this to be set before activation; this item verifies it independently, because a verbose setting multiplies what item 1's window is retaining. | The logging level of each flow, read from the flow record. |

**The delivered side of the boundary, so the split is unambiguous.** This application minimises what it contributes to that surface, and those parts are delivered rather than deferred: every error output of step 3 is a bounded closed code and never the platform's own message text, which can quote the endpoint, the composed request and a fragment of the body; a thrown orchestrator publishes a closed code, an opaque eight-character diagnostic reference and the caught text's length, and never the caught text; no step output other than the Crunchbase live `rows` carries upstream content, and widening any output to add one is forbidden; neither of the two is ever copied into a log line, an annotation or a third output; and the orchestrator construction is the recommended one partly because it keeps every per-record intermediate value — each cleaned record, each resolved reference, each upsert result — inside a single step call, so none of them enters the execution context at all.

**Status: flagged, unmet, and now blocking.** No evidence for items 1 to 4 has been recorded, because the actions belong to the platform owner and are outside this delivery's scope. What has changed is that the obligation is no longer discharged by being written down: it is a **precondition on live activation**, recorded in the register below alongside the staging and erasure obligations, and the two are gated together because they are the same exposure reached by two routes.

## The live-activation register

**`x_bst_startuptrk.ingestion.source_mode` must not be set to `live` for either source until every row of this register carries a named owner, a date and a reference to where the evidence is recorded.** That property is the single act that turns the live path on — a flow whose source mode is `fallback` reads only the synthetic dataset under [`../sample-data/`](../sample-data/) — so it is the one place a precondition can be attached without shipping automation the frozen inventory does not allow.

**This register does not gate the build, the fallback path, or `fallback validated` evidence.** Every artifact in this package is built, published and validated in full with the register empty, and criterion 4 of prompt section 10.0 is satisfiable from three clean fallback runs. What the register gates is the moment real third-party personal data first enters the instance.

| # | Precondition | Source of the obligation | Owner | Date | Evidence recorded at |
| --- | --- | --- | --- | --- | --- |
| LA1 | A maximum age is chosen for a **settled** staging row's personal payload, and the clear-down has been performed at least once against that age | [`./data-model.md`](./data-model.md#what-the-operator-owns) obligation 1 | *unassigned* | — | *none* |
| LA2 | A maximum age is chosen for a staging row's **existence**, whatever its state, and the deletion has been performed at least once | [`./data-model.md`](./data-model.md#what-the-operator-owns) obligation 2 | *unassigned* | — | *none* |
| LA3 | A **data-subject erasure runbook** exists naming all three surfaces — `contact_email` on `x_bst_startuptrk_founder` and `x_bst_startuptrk_executive`, the person columns and `raw_payload` on `x_bst_startuptrk_ingest_staging`, and `bio` and `linkedin_url` wherever they were written — and has been walked once end to end against a test subject | [`./data-model.md`](./data-model.md#what-the-operator-owns) obligation 3 | *unassigned* | — | *none* |
| LA4 | The clear-down and erasure routes have been confirmed to leave `sys_user` untouched | [`./data-model.md`](./data-model.md#what-the-operator-owns) obligation 5 | *unassigned* | — | *none* |
| LA5 | The instance's current flow-execution-data retention window is recorded | Item 1 above | *unassigned* | — | *none* |
| LA6 | That window is set to the shortest value operational needs allow, with the before and after values and the person who set them recorded | Item 2 above | *unassigned* | — | *none* |
| LA7 | The set of roles that can read a flow execution context is recorded and confirmed to be no wider than the set that may read `x_bst_startuptrk_ingest_staging` — which is `x_bst_startuptrk.admin` alone | Item 3 above | *unassigned* | — | *none* |
| LA8 | Each ingestion flow's logging level is confirmed at the least verbose setting that still records step outcomes | Item 4 above | *unassigned* | — | *none* |
| LA9 | **`glide.export.escape_formulas` is confirmed `true` on the instance.** The staging table holds unvalidated upstream text verbatim, and every mainstream spreadsheet treats a value beginning with `=`, `+`, `-`, `@`, a tab or a carriage return as a formula — so exporting the list to inspect it can execute a payload the upstream source chose, in the reader's own session. The property prefixes such values on export. It is a **Global-scope** property, so prompt section 6.0 forbids shipping it in the Update Set; it is confirmed, not set, by this application. | [`./manual-build/06-staging-table-csv-import.md`](./manual-build/06-staging-table-csv-import.md#a-staged-value-can-become-a-spreadsheet-formula-when-the-table-is-exported), completion row 23 | *unassigned* | — | *none* |

**Every row reads `unassigned` on this delivery, and that is the accurate state.** The register is published empty rather than omitted, because an empty row with a named obligation is a gate, whereas an unwritten obligation is an assumption. A reviewer checks the register, not the prose.

### How the gate is enforced, given that nothing can enforce it in code

The frozen inventory permits no ninth Script Include, no twelfth property and no second scheduled job — the artifacts that would have made this a runtime check were removed for exactly that reason (`D-036`, `D-265`). So the gate is procedural, and it is enforced by being **the same gate in every document that could otherwise be read as permission to go live**:

| Where | What it says |
| --- | --- |
| [`./validation-checklist.md`](./validation-checklist.md) | Live activation is a checklist item conditional on the register, so a completed checklist cannot coexist with an empty register and a live source mode. |
| [`./manual-build/01-connection-credential-aliases.md`](./manual-build/01-connection-credential-aliases.md#step-0--establish-the-credential-posture) | Its live-activation criterion already required a provider probe returning `code=ok`; it now also requires the register. |
| [`./manual-build/06-staging-table-csv-import.md`](./manual-build/06-staging-table-csv-import.md) | Its clear-down step is the procedure `LA1` and `LA2` are evidenced by, and completion row 22 asks for the count that proves it. Completion row 23 asks for the `glide.export.escape_formulas` value `LA9` is evidenced by, and row 24 makes `source_mode` `live` conditional on the whole register. |
| [`./data-model.md`](./data-model.md#staging-and-counter-data-retention--an-operator-owned-procedure) | The obligations themselves, stated in full, with the register named as where their discharge is recorded. |
| [`../sample-data/README.md`](../sample-data/README.md) | States that the synthetic dataset is outside the register's scope, so nobody reads the register as a reason not to test. |

**What a reviewer should conclude from an empty register.** Not that the delivery is incomplete — the register's contents are not this delivery's to fill — but that **the live path is not authorised yet**, and that any instance found with `source_mode` `live` and an empty register is operating outside the documented procedure. That is a finding about the instance, not about the package.

The related operator-owned staging and counter procedure is in [`./data-model.md`](./data-model.md); the redaction and reference contract the logger applies is specified there and in [`./api-reference.md`](./api-reference.md).

### Repository manifests are unchanged

**Zero dependencies are added to any repository manifest.** No `package.json`, `requirements.txt`, `pyproject.toml`, lock file, `go.mod` or `Gemfile` is created, updated or removed by this work.

- The design system **ships with the platform** and has no package identity, so it cannot be expressed in a manifest.
- The retired Material-UI packages — `"@material-ui/core": "^4.12.3"` at `package.json:L15` and `"@material-ui/icons": "^4.11.2"` at `package.json:L16` — are **left in place, untouched**, together with the declared-and-never-imported `chart.js` and `react-chartjs-2`. The legacy manifest is read-only reference.
- The two-level Update Set XML validator at [`../scripts/validate_update_set_xml.py`](../scripts/validate_update_set_xml.py) is written against the Python standard library only — `xml.etree.ElementTree`, `xml.parsers.expat`, `codecs`, `re`, `argparse`, `pathlib` and `ctypes`, the last used to probe the parser library for the allocation-tracker entry points its parser gate requires — so it introduces no dependency either. Where `ctypes` is unavailable the gate refuses rather than proceeding unprobed, so the probe never becomes a soft requirement.

**Decision log.** [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md).

### Rule-mandated dependency pins and their known advisories

**This entry is not one of the nineteen flags, and it is deliberately not numbered `F20`.** The `F` inventory discharges prompt section 11.0's obligation, which concerns **requirements with no clean ServiceNow equivalent**. What follows is a different kind of item: a conflict between a **project rule** and the **published security baseline** of a third-party library that rule pins by exact version. It is recorded here so the conflict is visible at the same place a reader looks for everything the delivery could not resolve cleanly, without disturbing the nineteen-flag count that this document, [`./validation-checklist.md`](./validation-checklist.md) and the decision log all assert.

**The scope of the pins.** Exactly one delivered artifact loads third-party code: the executive presentation at [`../../blitzy-deck/boston-startup-tracker-servicenow-executive-summary.html`](../../blitzy-deck/boston-startup-tracker-servicenow-executive-summary.html). Its three libraries are pinned to **exact versions stated verbatim by the presentation rule** — reveal.js `5.1.0`, Mermaid `11.4.0`, Lucide `0.460.0` — across five versioned files, two stylesheets and three scripts. **No part of the ServiceNow application loads any of them**: the scoped application's user interface is Service Portal with the platform's own AngularJS and Bootstrap, and the deck is never served by the instance, never loaded by the portal and carries no application data. The pins are also **not expressible in a repository manifest**, because the rule requires the deck to run with no build step and no local file dependency, so the libraries are referenced by `script` and `link` tag from a content delivery network.

**The conflict.** As of the re-assessment of **2026-08-09**, the pinned Mermaid release `11.4.0` is affected by published advisories that are fixed in later releases of the same major line, the highest of which is `11.16.1`. Upgrading is the ordinary remedy. **It is not available to this delivery**, because the version is not an implementation choice: the presentation rule states `11.4.0` verbatim, and the authority model forbids deviating from a rule to satisfy a heuristic or a baseline. The pin is therefore **retained deliberately**, and the residual risk is **accepted and disclosed** rather than silently carried.

#### Advisory scope, as re-queried

**Re-queried on 2026-08-09 (UTC).** The heading of this section carries no date, deliberately: the date belongs in the body and in the disposition record, so that a future re-query replaces the content without breaking every inbound link to it.

**Eleven advisory records were identified** against the pinned Mermaid release and its distributed build: **seven whose stated range includes `11.4.0`** — six first-party and one transitive — and **four whose range does not**. For each one the table records the range the advisory states, whether the pinned `11.4.0` falls inside it, and whether the code path the advisory describes is reachable in this deck. **The reachability answer is a fact about the delivered file, and every one of them is independently checkable in it.** This table replaces the six-record snapshot of the previous assessment: two of that snapshot's cells read `Re-query at acceptance` and both are now answered, one of them **reversing** what the snapshot implied.

**In range for `11.4.0` — seven records, none reachable.**

| Advisory | Subject | Stated affected range | Fixed in | Reachable here | Basis for the reachability answer |
| --- | --- | --- | --- | --- | --- |
| `CVE-2026-71438`, `GHSA-c4c3-pg64-4m4v` | Prototype pollution through the configuration setters `mermaid.initialize`, `mermaidAPI.setConfig` and `mermaidAPI.updateSiteConfig`, which deep-merge caller-supplied configuration. Rated **Low** by the maintainer, on the ground that those entry points are documented as receiving configuration the integrating application controls. | Before `10.9.8`; and from `11.0.0-alpha.1` up to but excluding `11.16.1`. | `10.9.8`, `11.16.1` | **No** | The deck calls `mermaid.initialize` **exactly once**, with an object literal written into the file. It never calls `setConfig` or `updateSiteConfig`, and no diagram source carries a `%%{init: ...}%%` directive or YAML frontmatter. No caller-supplied, fetched or typed value reaches any configuration entry point. |
| `CVE-2025-54881`, `GHSA-7rqq-prvp-x9jh` | Cross-site scripting through unsanitised sequence-diagram labels, rendered by way of a mathematics typesetter's `innerHTML`. | From `11.0.0-alpha.1` up to but excluding `11.10.0`; and from `10.9.0-rc.1` up to but excluding `10.9.4`. | `10.9.4`, `11.10.0` | **No** | The deck contains no `sequenceDiagram`. Its five diagrams are **four `flowchart` and one `timeline`**. |
| `CVE-2025-54880`, `GHSA-8gwm-58g9-j8pw` | Cross-site scripting through an architecture-diagram icon, written into the document by a data-binding library's `html()` call. | Introduced in `11.1.0`; fixed in `11.10.0`. | `11.10.0` | **No** | The deck contains no architecture diagram of either spelling, and loads no icon pack into Mermaid. |
| `GHSA-87f9-hvmw-gh4p` | Cascading-stylesheet injection through the configuration keys `fontFamily`, `altFontFamily`, `themeCSS` and `themeVariables`, whose values are emitted into the rendered stylesheet. | Up to and including `11.14.0` from `11.0.0-alpha.1`; and up to and including `10.9.5`. | `10.9.6`, `11.15.0` | **No** | **The deck does set two of those keys** — `fontFamily` and `themeVariables` — which is why this row states its basis precisely rather than by category: both are **object and string literals authored into the file**, no value reaching either key is fetched, parameterised, typed or read from a URL, and no diagram source carries `%%{init: ...}%%`, which is the other route to the same keys. There is no `themeCSS` and no `altFontFamily`. An attacker with the ability to edit the deck file already has the ability to edit its `<script>` block, so this key surface adds no reachable path. |
| `CVE-2026-41150`, `GHSA-6m6c-36f7-fhxh` | Denial of service — an unbounded loop — when a Gantt diagram's `excludes` directive is parsed. | Before `10.9.6`; and from `11.0.0-alpha.1` up to but excluding `11.15.0`. | `10.9.6`, `11.15.0` | **No** | The deck contains no Gantt diagram and no `excludes` directive. |
| `CVE-2026-71436` | Denial of service — an unbounded loop — in the XY-chart axis range setter. | From `10.6.0` up to but excluding `10.9.8`; and from `11.0.0-alpha.1` up to but excluding `11.16.1`. | `10.9.8`, `11.16.1` | **No** | The deck contains no `xychart` diagram. |
| `CVE-2026-4800` and `CVE-2026-2950` in `lodash-es` | Two advisories against the utility library Mermaid bundles into its distributed build. **Transitive rather than first-party**, and reached only through the bundling. | Remediated in `lodash-es` `4.18.1`. The version bundled into `11.4.0`'s `dist/mermaid.min.js` precedes it. | `lodash-es 4.18.1`, carried by a later Mermaid release | **No reachable sink identified** | The deck's only interaction with the bundle is `mermaid.initialize` with a literal and `mermaid.run` over nodes already in the document. **This row is stated as "no reachable sink identified" rather than "no", because a bundled dependency's surface is not fully enumerable from the calling file** — which is the honest answer and the one the re-query date exists to revisit. |

**Not in range for `11.4.0` — four records.**

| Advisory | Subject | Stated affected range | Why the pin is outside it |
| --- | --- | --- | --- |
| `CVE-2026-71437`, `GHSA-3rrr-jr9j-h3q3` | Prototype pollution when an untrusted `architecture-beta` diagram is rendered. | From `11.5.0` up to but excluding `11.16.1`. | The pin precedes the first affected release. The deck also contains no such diagram. |
| `CVE-2026-71439`, `GHSA-rhh3-jpg6-66xh` | Denial of service when a radar diagram is rendered. | From `11.6.0`. | The pin precedes the first affected release. **This answers a `Re-query at acceptance` cell of the previous snapshot.** The deck also contains no radar diagram. |
| `GHSA-m4gq-x24j-jpmf` | Prototype pollution and cross-site scripting through the sanitiser version bundled into the distributed builds. | Up to and including `10.9.2`; fixed in `10.9.3`. | The pin is on the `11.x` line, above the whole affected range. **This answers the second `Re-query at acceptance` cell and reverses what the previous snapshot implied**: that record asked whether the `11.x` line was affected, and the answer is that the advisory's range ends in the `10.x` line. The bundled sanitiser the deck loads is not the affected one. |
| `GHSA-x3vm-38hw-55wf` | Cascading-stylesheet injection reaching elements outside the diagram container. | Fixed in `9.1.2`. | The pin is four major-minor lines above the fix. |

**One record from the previous snapshot has been withdrawn from this table.** It cited `CVE-2026-50159` for a stylesheet-injection defect. That identifier **could not be substantiated** against any advisory for this library on re-query, so it is replaced by `GHSA-87f9-hvmw-gh4p` above, which is the substantiated record describing that class of defect and which states a range that includes the pin. Carrying an unsubstantiated identifier in a security record is worse than carrying none: it cannot be re-queried, it cannot be closed, and it makes the rest of the table look equally unverifiable.

**The advisory database is live and the table above is a snapshot.** The re-query procedure is stated under [Re-query procedure](#re-query-procedure) below and its output is a required field of the disposition record. A record that appears after this date is a **new input to this decision**, not a defect in this record.

#### Exposure

Five properties of the delivered file bound the exposure, and each is checkable in it without running anything.

1. **Five diagrams — four `flowchart` and one `timeline` — all literal.** Every diagram source is written into the file between `<pre class="mermaid ...">` and its closing tag. The five and their types are the whole inventory, and each is named by the slide that carries it: two `flowchart` on slide 3, *Before and after*, being the legacy-and-target architecture pair; one `flowchart` on slide 10, *How data arrives and leaves*; one `flowchart` on slide 13, *How it will be proven*; and one `timeline` on slide 15, *The migration timeline, and how it changes after*. The access-control slide carries a table rather than a diagram. There is no `sequenceDiagram`, no radar diagram, no Gantt diagram, no `xychart` and no architecture diagram of either spelling — which between them account for **five** of the seven in-range advisories.
2. **One configuration call, with a literal argument — and it does set two of the keys an advisory names.** `mermaid.initialize` is called once, with an object literal carrying `startOnLoad: false`, `securityLevel: 'strict'`, `theme: 'base'`, a `themeVariables` object, `fontFamily`, `htmlLabels: false` and a `flowchart` block. `themeVariables` and `fontFamily` are the two keys `GHSA-87f9-hvmw-gh4p` names; both hold literals authored into the file. `setConfig`, `updateSiteConfig`, `themeCSS`, `altFontFamily` and the in-diagram `%%{init: ...}%%` directive appear **nowhere**, which is verifiable by a single search of the file.
3. **No input surface at all.** The deck reads no query parameter, accepts no form field, fetches no data and stores nothing. Rendering is driven by `mermaid.run` over the nodes already in the document.
4. **No privileged context.** The deck is opened as a local file over `file://`. It has no server, no session, no cookie, no credential and no privileged origin, and it carries no application data.
5. **Nothing depends on it.** No part of the ServiceNow application, the Update Set or the instance loads the deck or any of its three libraries. The portal runs on the platform's own AngularJS and Bootstrap.

**One limit of property 2, stated so it is not over-read.** `securityLevel: 'strict'` is not the setting the stylesheet-injection and document-object-model-injection advisories name as their workaround; those name `sandbox`, which draws the diagram inside a sandboxed frame. **`sandbox` is not available to this deck**: the frame it creates has a `data:` URL source, which the deck's own content-security policy forbids with `frame-src 'none'`, so every diagram is blocked from display while rendering correctly inside the document. `strict` sanitises the same source and renders inline, which the policy permits unchanged, and `flowchart.htmlLabels` is `false` besides, so no label is parsed as markup. `strict` is therefore stated here as an observed property of the file, **not** as a mitigation for those three records. Their reachability answer rests on property 1 and property 3 — no `classDef`, no caller-supplied configuration — and on nothing else. The security-level choice and the policy constraint behind it are recorded in [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md).

#### Compensating controls, all delivered

- **Byte-pinning.** All five versioned assets carry a **SHA-384 `integrity` attribute** and `crossorigin="anonymous"`, so the exact reviewed bytes are the only bytes the browser will execute. A substituted or tampered file fails to load rather than running. The verification command and the expected digests are in the deck's own comment block.
- **No untrusted input reaches the library.** Every one of the five diagram sources is authored literally in the deck file. The deck accepts no user input, no query parameter, no form field and no fetched data, so no caller-supplied text ever reaches a Mermaid parser or its configuration setter.
- **`securityLevel: 'strict'`, not the default.** The configuration literal sets the library's strictest rendering mode rather than leaving the default, so HTML labels are disabled and script-bearing label content is not rendered even if a diagram source carried it. `htmlLabels: false` is set both globally and inside the `flowchart` block. The decision is `D-305`.
- **No in-diagram configuration.** A `%%{init: ...}%%` directive is the one route by which a diagram *source* can reach a configuration key, and the file contains **zero** of them. That is what keeps the configuration surface of `GHSA-87f9-hvmw-gh4p` and `CVE-2026-71438` confined to the single literal call.
- **A minimal blast radius.** The deck is a **static local file**. It has no server, no session, no credential, no cookie and no privileged origin, and it reads and writes nothing outside the page. Nothing in the ServiceNow instance, the scoped application or the Update Set depends on it.

#### Residual risk

Two residues remain after the compensating controls, and both are bounded.

- **The library stays un-upgraded for as long as the rule pins it.** If a future advisory describes a path the deck *does* exercise — a `flowchart` or `timeline` parser defect, or a defect in the rendering of a literal source — the compensating controls do not remove it, and the only remedy is re-pinning, which is an amendment to the rule.
- **A content-network compromise fails closed, not silently.** The SHA-384 digests mean substituted bytes do not execute; the asset is blocked instead. The consequence is a deck that does not render, which gate `G-8` detects, rather than a deck that renders hostile code.

#### The two available dispositions

Exactly two dispositions are available, and choosing between them is the rule owner's act rather than the delivery's.

| Option | What it requires | What results |
| --- | --- | --- |
| **A — re-pin** | The presentation rule is amended to a Mermaid release at or above `11.16.1`, which is the highest of the fixing releases in the table above. The deck's pin, its `script` source and its SHA-384 `integrity` digest are re-derived, and gate `G-8` is re-run over all five assets. | All five applicable advisories close. The deck no longer carries the version the rule states verbatim, so the rule text and the artifact are re-aligned by amending the rule. |
| **B — accept** | The pin is retained, this record is signed by a named owner, and the review trigger below is set. | The five applicable advisories stay open and disclosed. Nothing in the deck or the application changes. |

**Recommended disposition: B.** The recommendation rests on the reachability column above rather than on convenience. Of the **eleven** records identified, **four** state ranges the pin falls outside entirely. Of the **seven** in range, **five** describe diagram types the deck does not contain, **one** describes configuration entry points the deck reaches exactly once with a literal and never through a diagram directive, and **one** is a transitive bundled-library record for which no reachable sink was identified — which is the only row of the seven whose answer is bounded by what the calling file can establish, and is why the re-query below is a required field rather than a suggestion.

**Option A is not available to this delivery, which is what makes the disposition a decision rather than an open question.** The presentation rule states `11.4.0` verbatim, and in this project's authority model a rule outranks a security baseline — so amending the pin is the rule owner's act and no agent may perform it. The delivery is therefore in disposition **B** by construction, and it records that as its decision below rather than leaving the field blank and calling the matter undecided. What remains outstanding is not the choice but the **countersignature**: a named person accepting the residual risk on a stated date. Two fields, not four.

#### Disposition record

The delivery has completed every field it can establish, **including the decision and the accountable role**. **The two fields marked `REQUIRED — not yet supplied` are a countersignature, and no gate tick, script or agent can supply them.** Until both carry a value this record's status is `DECIDED — B, pending countersignature`, and the corresponding row of [`./validation-checklist.md`](./validation-checklist.md) fails.

| Field | Value |
| --- | --- |
| Item | Mermaid, loaded by the executive presentation as `dist/mermaid.min.js` over a content delivery network. |
| Pinned version | `11.4.0`. |
| Fixing release for the advisories that apply | **`11.16.1`** is the highest fixing release among the seven in-range records, and is therefore the release Option A would have to reach. The individual fixes are `11.10.0` for the sequence-diagram and architecture-icon records, `11.15.0` for the stylesheet-injection and Gantt records, `11.16.1` for the configuration-setter and XY-chart records, and `lodash-es 4.18.1` — carried by a later Mermaid release — for the two transitive records. |
| Authority for the pin | The presentation rule, which states `11.4.0` verbatim. A rule outranks a security baseline in this project's authority model, so the version is **not** an implementation choice and re-pinning is not the delivery's to make. |
| Assessment date | **2026-08-09** (UTC), superseding the assessment of 2026-08-08. |
| Assessed by | The delivery, as part of the remediation of the final security review. The assessment is the two advisory tables, the exposure list and the compensating controls above. |
| Scope of the risk | One artifact: `blitzy-deck/boston-startup-tracker-servicenow-executive-summary.html`. **Not** the scoped application, **not** the Update Set, **not** the instance, **not** any portal page, and no application data. |
| Mitigations in place | SHA-384 byte-pinning with `crossorigin="anonymous"` on all five assets; diagram sources authored literally in the file, none containing a `classDef`; a single `mermaid.initialize` call with a literal argument; no input surface; static local file with no privileged context. Stated in full under [Compensating controls, all delivered](#compensating-controls-all-delivered) above and verified by gate `G-8`. |
| Residual risk after mitigation | As stated under [Residual risk](#residual-risk) above: an un-upgraded library for as long as the rule pins it, and a fail-closed content-network compromise. |
| Recommended disposition | **B — accept**, on the reachability finding rather than on convenience. |
| Review trigger | Re-run this assessment when **any** of the following occurs, whichever comes first: the presentation rule is next amended; a new advisory names a `flowchart` **or** `timeline` parsing or rendering path; a new advisory names the configuration keys `fontFamily`, `altFontFamily`, `themeCSS` or `themeVariables`; or a new advisory names the bundled `lodash-es`. The first three are the paths this deck exercises; the fourth is the row whose reachability the calling file cannot fully establish. |
| **Decision — `A` or `B`** | **`B` — accept.** Recorded by the delivery on **2026-08-09** (UTC), on the reachability finding above and on the fact that option `A` requires amending a rule the delivery may not amend. This is the decision; the row below is who accepts the residual risk it leaves. |
| **Risk owner — the role accountable for the decision** | **The rule owner** — the role that maintains the presentation rule pinning `11.4.0` verbatim, because the pin is a rule and only that role can amend it. Named here as a role; the person filling it signs in the row below. |
| **Accepted by — name of the person** | **REQUIRED — not yet supplied.** The person holding the risk-owner role above. A role name is not a signature and does not satisfy this field. |
| **Date accepted (UTC)** | **REQUIRED — not yet supplied.** It must be the date the named person signed, on or after the decision date of **2026-08-09**, and it may **not** be back-dated. If more than thirty days separate it from the advisory re-query in the row below, the acceptance is stale and the assessment is re-run before it is signed. |
| Advisory set re-queried on the acceptance date | Record the query date and what it returned, including any record absent from the snapshot above. |
| Status | **`DECIDED — B, pending countersignature`.** Set to `CLOSED — accepted` only when both remaining required fields carry a value. `CLOSED — re-pinned` is reachable only if the rule owner amends the rule, which converts this record's decision to `A` and requires the deck's pin and all five integrity digests to be re-derived. |

**Where this record is enforced.** [`./validation-checklist.md`](./validation-checklist.md) carries the advisory gate inside `G-8`, the definition-of-done item that refuses to be satisfied by a tick, and the final sign-off row that names the five required fields. The acceptance, its alternatives and its residual risk are logged as a **High**-rated decision in [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md).

#### Re-query procedure

The advisory tables above are a snapshot taken on a date, and a snapshot ages. This procedure is what the acceptor runs to replace it, and it exists because the disposition record makes a re-query a **required field** rather than a suggestion: an acceptance signed against a stale snapshot accepts a risk nobody measured.

Run it in full. It is four queries and one comparison, and it does not require the instance, the Update Set or any credential.

**1. Query the advisory databases.** Two sources, because neither is complete on its own — the ecosystem database carries the version ranges in machine-readable form, and the national database carries records that have not yet been mirrored.

| # | Source | Query | What to capture |
| --- | --- | --- | --- |
| Q1 | GitHub Advisory Database | The `npm` ecosystem, package `mermaid`, all severities, **including withdrawn records** | Every advisory identifier, its severity, its stated vulnerable range and its first fixing release |
| Q2 | GitHub Advisory Database | The `npm` ecosystem, package `lodash-es` | The same four fields. `lodash-es` is bundled into `dist/mermaid.min.js`, so its advisories are in scope even though the deck never names it |
| Q3 | National Vulnerability Database | Keyword `mermaid`, restricted to the JavaScript diagramming library rather than the many unrelated products of that name | Any `CVE` identifier absent from Q1, and any range that disagrees with Q1 |
| Q4 | The library's own release notes | Releases published since the snapshot date | Any security fix described in a release note but carrying no advisory identifier — this is the class Q1 to Q3 cannot return |

**2. Classify each record returned against the pin.** The pin is `11.4.0`. A record is **in range** when `11.4.0` satisfies its stated vulnerable range, and **not in range** otherwise. Do not classify by severity, and do not classify by whether the record sounds relevant — the range is the only test at this step.

**3. Establish reachability for every in-range record, by searching the deck.** Reachability is a property of the calling file, not of the advisory, so it is answered by searching `blitzy-deck/boston-startup-tracker-servicenow-executive-summary.html` and not by reading the advisory text a second time. Five searches answer every in-range record found so far, and each returns a count that is either zero or a small enumerable set:

| Search | Snapshot value | What a change means |
| --- | --- | --- |
| The diagram-type keyword the advisory names — `sequenceDiagram`, `gantt`, `xychart`, `radar`, `architecture`, `architecture-beta`, `timeline`, `flowchart` | 4 × `flowchart`, 1 × `timeline`, 0 of every other type | A non-zero count for a newly-named type moves that record from *not reachable* to **reachable**, and the disposition must be re-taken |
| `%%{init` | **0** | Any occurrence hands a diagram source a route to a configuration key, which is the precondition for the configuration and stylesheet records. Treat a non-zero count as reachable without further analysis |
| `setConfig` and `updateSiteConfig` | **0** each | The same, through the programmatic route |
| `themeCSS` and `altFontFamily` | **0** each | Both are named by the stylesheet-injection record and neither is set. `themeVariables` and `fontFamily` **are** set, as literals in the file, which is the basis on which that record is judged not reachable |
| `securityLevel` | **1**, with the value `'strict'` | A change away from `'strict'` weakens the control that makes label-rendering records not reachable |

For a bundled transitive record such as the `lodash-es` pair, record **“no reachable sink identified”** rather than “not reachable”, and say which sinks were searched for. The distinction is not pedantry: a bundled dependency's surface is not fully enumerable from the calling file, so the stronger claim would be one the evidence does not support.

**4. Compare against the snapshot and record the delta.** Write the result into the disposition record's re-query field as: the query date in UTC, the four sources as actually queried, the count in range and not in range, and — explicitly — **every record that is new since the snapshot, every record whose stated range has changed, and every record the snapshot listed that has since been withdrawn**. A re-query that returns exactly the snapshot is a valid and useful result; record it as such rather than leaving the field empty.

**5. Apply the outcome rule.**

- Every in-range record is not reachable, and no new diagram type, configuration route or lowered `securityLevel` appears in the deck → **disposition `B` remains available**, and the acceptor may sign.
- Any in-range record is reachable → **disposition `B` is no longer available on the reachability finding**. The record must be escalated to the rule owner, because the only remaining remedy is Option A, and amending a version a rule states verbatim is the rule owner's act and no one else's.
- Q4 returns a security fix with no advisory identifier → treat it as an in-range record of unknown reachability and escalate, since an unidentified fix cannot be range-tested.

**What this procedure deliberately does not do.** It does not change the pin, and it does not authorise changing the pin. `11.4.0` is stated verbatim by the presentation rule and by the plan's dependency inventory, and a rule outranks a security baseline in this project's authority model. The procedure's entire output is evidence for a human decision.

**Decision log.** [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md).

## Operator obligations

**Three obligations belong to a human operator or platform owner rather than to any delivered artifact. Two of them block acceptance; the third is recommended defence in depth and does not.**

| ID | Class | Why |
| --- | --- | --- |
| **`OB-1`** | **Acceptance-blocking** | This delivery stages verbatim upstream person data and ships no artifact that prunes or erases it, so the exposure exists the moment ingestion runs |
| **`OB-2`** | **Acceptance-blocking** | This delivery contributes that same person data to flow execution contexts whose retention and readership it cannot set |
| **`OB-3`** | **Recommended, not blocking** | Agent Action Plan section 0.8.3 makes an inbound platform rate-limit rule optional defence in depth. Nothing in this package delivers one and nothing could, so acceptance cannot depend on it. It is a **recorded residual risk** with a procedure for the operator who adopts it |

**The two blocking obligations block acceptance until their evidence is recorded.** They are collected here because each was previously stated only as a residual risk or an unmet status, with no owner, no schedule and no evidence — which is indistinguishable from an oversight when read later.

Each carries an `OB-` identifier so the acceptance checklist can reference it by name. None can be discharged by a script, a gate tick or an agent: every one requires an action on the instance by a named role, and a recorded observation of the result. [`./validation-checklist.md`](./validation-checklist.md) carries a definition-of-done item and a final-sign-off row for each, and a blank row there is a **no** in the acceptance row.

| ID | Obligation | Owner role | When | Evidence to record |
| --- | --- | --- | --- | --- |
| **`OB-1`** | Retention, minimisation and data-subject erasure over `x_bst_startuptrk_ingest_staging` | Application administrator, holding `x_bst_startuptrk.admin` | A schedule the operator sets and records, at most **monthly**, and on demand for an erasure request | The retention period set, the date of the last clear-down, the row count before and after, and the identity of the operator who ran it |
| **`OB-2`** | Flow-execution-data retention and read-access confirmation | Platform owner, holding `admin` on the instance | Once before acceptance, and again whenever the instance's flow-execution retention configuration changes | The four items of [Flow execution context retention](#flow-execution-context-retention), each with the value observed and who observed it |
| **`OB-3`** *(recommended, not blocking)* | An inbound rate-limit rule in front of the application's own endpoint | Instance operator, holding `admin` | At deployment time or later, at the operator's discretion | **Either** the rule's identity, the endpoint and roles it covers, the threshold and window set, and one observed `429` from a deliberate over-budget read — **or** a recorded decision not to adopt it, with the residual risk accepted by a named person |

### `OB-1` — retention and erasure over the staging table

**What is delivered for it, and what is not.** [`F19`](#f19--no-retention-minimisation-or-data-subject-erasure-of-staged-data) records that the artifact inventories the Agent Action Plan freezes leave no room for a retention Script Include, a scheduled job or a retention property. No mechanism is delivered; the obligation below is, and it is acceptance-blocking. `D-377` records the decision, its alternatives and its residual risks.

**The procedure.** Four steps, all performed as a caller holding `x_bst_startuptrk.admin`, which is the only role the table's controls admit.

| # | Step | Detail |
| --- | --- | --- |
| 1 | **Set and record a retention period.** | The shortest period that still supports ingestion troubleshooting. Days, not months. Record the value and the date it was set. |
| 2 | **Delete every settled row older than that period.** | A settled row is one whose `import_state` is `processed`, `rejected` or `error`. A `pending` row is either in flight or the residue of an interrupted run and is handled by step 4. Delete from the list view of the staging table, filtered on `import_state` and `sys_updated_on`; there is no delivered method for this. |
| 3 | **Service an erasure request by `raw_payload` and the five person columns.** | Query the staging table for the subject across `raw_payload`, `name`, `contact_email`, `bio`, `linkedin_url` and `url`, delete every match, and record the count. **An erasure is complete only for the data present when it runs**: nothing in this delivery suppresses a later ingestion run from recreating the subject, so the request is fully serviced only once the upstream source has also removed them. Record that limitation with the erasure. |
| 4 | **Confirm no `pending` row predates the retention period.** | A `pending` row older than the period is residue from an interrupted run. Investigate before deleting, because a row an active run has claimed must not be removed under it. |

**What is already delivered, so the obligation is bounded rather than open-ended.** The staging table is `package_private` with `ws_access` false, so it is unreachable from another application scope and from the native Table API; its read, write, create and delete controls admit `x_bst_startuptrk.admin` alone; and `IngestionLogger` records no personal value in any log line. The uncontrolled surface is **the rows themselves and nothing else**.

### `OB-2` — flow-execution retention and read access

The four actions, the reason they fall to the platform owner, and how to confirm each are stated in full under [Flow execution context retention](#flow-execution-context-retention). This obligation is the acceptance gate over them: **the delivery is not accepted while any of the four is unrecorded.**

**What this delivery contributes, so the split is unambiguous.** The two flow outputs that carry upstream content — `response_body` at step 3 and `rows` at step 4 — cannot be removed, because step 4 parses the first and step 5 cleans the second. Everything else either flow emits is a run identifier, an opaque reference or a counter. Both flow guides additionally require the flow's own logging level to be set to the least verbose setting that still records step outcomes, **before activation**, which is the one minimisation available inside the application's control. `D-378` records the decision.

### `OB-3` — an inbound rate-limit rule in front of the application's endpoint

**What is delivered for it, and what is not.** An inbound rate-limit rule is instance configuration outside the `x_bst_startuptrk` scope, and prompt section 6.0 forbids the scoped application from creating anything outside its scope, so it cannot travel in the Update Set. Agent Action Plan section 0.8.3 sanctions it as **optional** defence in depth and states that it does not affect the rate-limit contract. Nothing is delivered for it, and **acceptance of this package does not depend on it**: the delivered rate-limit contract is the application-level accounting on the Scripted REST API, which suite 9 asserts. What follows is the procedure for an operator who adopts the rule, and the alternative of recording a decision not to. `D-379` records the decision and its alternatives.

**What it closes.** Nothing that the delivered posture leaves open, and that is the point of recording it as optional. The Table API read route the rule was originally proposed for is **closed** on all ten tables — `ws_access` `false`, per [Why every table is sealed](./access-control.md#why-every-table-is-sealed-including-the-seven-a-caller-does-read) — so no route now reaches a table without passing the application's own fixed-window counter. What the rule adds is a **platform-level** backstop in front of `/api/x_bst_startuptrk/v1/`, which refuses a flood before any application script runs and therefore before the counter is read or written.

| # | Step | Detail |
| --- | --- | --- |
| 1 | **Create one inbound rate-limit rule covering the seven entity tables.** | Scope it to the three application roles, so an unauthenticated or unroled caller is refused by access control before the rule is reached. |
| 2 | **Set a threshold at or above the application's own budget.** | The shipped application values are `x_bst_startuptrk.rest.rate_limit_requests` `100` per `x_bst_startuptrk.rest.rate_limit_window_seconds` `60`. A platform threshold **below** the application budget would refuse requests the application's own API would have served, so set it at or above. Record both numbers. |
| 3 | **Verify it fires.** | Issue reads past the threshold against one entity table and record the observed `429`. A rule that exists but does not fire is not a control. |
| 4 | **Record the rule's identity and coverage.** | So a later reader can confirm the rule still covers all seven tables rather than the one that was tested. |

**The platform's `429` body is not the application's, and that is expected.** The application's rate-limit contract — `{"error": "rate_limit_exceeded", "retry_after": N}` — is produced by `RateLimitService` on the application's own endpoints and is asserted by the REST test suite. A platform rule returns the platform's own body on the Table API route. The two are different surfaces with different contracts, and this obligation does not change the application contract.

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
