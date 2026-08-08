# Gaps and flags — `x_bst_startuptrk`

This document discharges the obligation of **prompt section 11.0**: *flag any requirement with no clean ServiceNow equivalent rather than silently omitting or half-implementing it.* It is the **single collection point** for that obligation across the whole package. Every requirement that the ServiceNow scoped application `x_bst_startuptrk` does not implement, implements only through a named workaround, or excludes outright is listed here — with its source, the platform's position on it, and what was consequently done.

The inventory is exhaustive by construction. A requirement that is neither implemented nor listed in this document is an unexplained omission, and the bidirectional traceability matrix cannot close without it. **No list below is abbreviated:** every excluded requirement, every unresolved gap and every untouched artifact is named individually, and no entry closes with an open-ended terminator standing in for items it does not name.

**Authority.** The frozen prompt and the Agent Action Plan are authoritative for all application content. This document is authoritative for one thing only: **which requirements are unimplemented, worked around or excluded, and on what factual basis.** Where a requirement is implemented, the document that owns it is authoritative for how — [`./data-model.md`](./data-model.md) for the schema, [`./access-control.md`](./access-control.md) for authorization, [`./api-reference.md`](./api-reference.md) for the API surface, and the six guides indexed by [`./manual-build-instructions.md`](./manual-build-instructions.md) for everything built by hand. Every identifier used below — table name, column name, role name, property key, page name, widget name, gap identifier — matches those documents character for character. No variant spelling is valid.

This document carries **no rationale**. It states what each requirement is, where it comes from, what the platform offers or does not offer, and what was done. Every decision behind those outcomes, every alternative considered and every risk each carries is recorded in [`../../docs/decisions/DECISION_LOG.md` (planned)](../../docs/decisions/DECISION_LOG.md), which is the single source of truth for "why". Each entry below ends with a pointer to that log, and the pointer does the work.

**Reviewer.** Three of the call-out categories that [`../../docs/review/CRITICAL_DECISIONS.md` (planned)](../../docs/review/CRITICAL_DECISIONS.md) is required to raise intersect this inventory: the authorization decision, recorded here as [F10](#f10--the-administrator-access-control-override), and the ambiguity resolutions, recorded here as [F6](#f6--inclusion-criteria-field-ambiguity--resolved) and under [Ambiguity resolutions besides F6](#ambiguity-resolutions-besides-f6). That document's five entries are not reproduced here.

## Referenced documents

Some documents named below are **planned artifacts of this package**. Every link to one carries the marker **(planned)** in its link text. A statement about a planned document describes what that document is required to contain; it is not a claim that the content can be read from it today.

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
| [`./validation-gates.md`](./validation-gates.md) | The sixteen post-commit gates and the eleven-gate core. |
| [`./validation-checklist.md` (planned)](./validation-checklist.md) | The evidence record for the five success criteria, including criterion 2 for the access-control checks and criterion 4 for the scheduled runs. |
| [`../sample-data/README.md`](../sample-data/README.md) | The fallback-only posture of the sample dataset. |
| [`../../docs/decisions/DECISION_LOG.md` (planned)](../../docs/decisions/DECISION_LOG.md) | The single source of truth for every "why" behind every entry in this document. |
| [`../../docs/decisions/TRACEABILITY_MATRIX.md` (planned)](../../docs/decisions/TRACEABILITY_MATRIX.md) | The bidirectional matrix this inventory closes the unimplemented half of. |
| [`../../docs/review/CRITICAL_DECISIONS.md` (planned)](../../docs/review/CRITICAL_DECISIONS.md) | The five risk-ordered review entries, three of whose call-out categories intersect this inventory. |

## Numbering convention

**Three identifier schemes appear on this page, and the first two are easily confused.** Read the padding.

| Scheme | Form | Meaning | Examples |
| --- | --- | --- | --- |
| **This document's flag identifiers** | `F` followed by **one or two** digits, never zero-padded | A flag in this inventory. There are exactly twelve, `F1` through `F12`. | `F1`, `F6`, `F10`, `F12` |
| **Source requirement identifiers** | `F` followed by **three** zero-padded digits, optionally then a hyphen and a sub-number | A feature or a requirement in the source requirements document, `documentation/Software Requirements Specifications (SRS).md`. There are ten features, `F001` through `F010`, each carrying five requirements. | `F009`, `F009-5`, `F010-1`, `F001-1`, `F003-3`, `F006-4`, `F007-5` |
| **Design-system gap identifiers** | `G` followed by one digit | A gap in the user-interface design system. There are exactly seven, `G1` through `G7`. | `G1`, `G6`, `G7` |

Every source requirement identifier in this document is written in its three-digit padded form. `F1` is this document's first flag; `F001` is the source document's first feature; `F001-1` is that feature's first requirement. The three are distinct and are never interchangeable.

Source requirement identifiers are cited as `SRS:L<line>` against `documentation/Software Requirements Specifications (SRS).md`. Repository source files are cited as `<path>:L<line>` or `<path>:L<first>-L<last>`.

## Dispositions

Every entry in this document carries exactly one of three dispositions.

| Disposition | Meaning |
| --- | --- |
| **Flagged, not implemented** | No platform equivalent exists. The requirement is not built, and it is not partially built. |
| **Resolved by documented workaround** | A platform equivalent exists only indirectly. The requirement is met by a named mechanism that is specified in a document of this package. |
| **Consciously excluded** | The requirement has no counterpart in the authoritative prompt. It is not built, and its absence is recorded so that it reads as a decision rather than an oversight. |

## Flag summary

Twelve flags. Every one has a detail section below.

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

By disposition: three are **flagged, not implemented** — F1, F2 and F5; six are **resolved by documented workaround** — F3, F4, F6, F7, F8 and F10; three are **consciously excluded** — F9, F11 and F12. Three plus six plus three is twelve.

Two flags are marked for prominence because a later reader acting on a partial understanding of either would introduce a defect: **[F6](#f6--inclusion-criteria-field-ambiguity--resolved)**, which must not be "corrected" by adding the premium-gated column to the inclusion predicate, and **[F10](#f10--the-administrator-access-control-override)**, which invalidates any access-control verification performed as the instance administrator.

## The twelve flags

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

**Decision log.** [`../../docs/decisions/DECISION_LOG.md` (planned)](../../docs/decisions/DECISION_LOG.md).

### F2 — Automatic entitlement transition on payment

**The requirement.** On successful payment, a caller holding the base role becomes entitled to the premium dataset without administrative action; on lapse or cancellation, the entitlement is withdrawn the same way.

**The source.** Requirement `F006-4` at `SRS:L446`, read together with the three role tiers at `SRS:L77`, "Role-based access control (free users, premium subscribers, administrators)". The transition between the first two tiers is the subject of this flag.

**The platform position.** The entitlement itself exists and works: `x_bst_startuptrk.premium_user` is a real role, and holding it grants read access to all seven premium-gated columns exactly as the matrix in [`./access-control.md`](./access-control.md) specifies. What has no platform equivalent is the **trigger** for granting it. This flag depends entirely on [F1](#f1--premium-subscription-billing-and-payment-processing): there is no payment event on the instance for a rule to react to, so there is nothing for an automatic transition to be automatic about.

**Disposition — flagged, not implemented.** The delivered Update Set contains three `sys_user_role` definitions and **zero** `sys_user_has_role` assignments, and no business rule, flow or Script Include in the application grants, revokes or schedules the expiry of a role. `sys_user` and `sys_user_has_role` sit outside the `x_bst_startuptrk` scope, and prompt section 6.0 forbids modifying anything outside it.

**The operational path.** Entitlement is granted **manually**: an administrator adds `x_bst_startuptrk.premium_user` to the person's `sys_user` record on the instance, and removes it to withdraw entitlement. That act takes effect immediately on both surfaces, because both consult the caller's effective roles on every read. The role, its capability and the seven columns it unlocks are specified in [`./access-control.md`](./access-control.md).

**Decision log.** [`../../docs/decisions/DECISION_LOG.md` (planned)](../../docs/decisions/DECISION_LOG.md).

### F3 — Runtime-configurable flow schedule interval

**The requirement.** The two ingestion flows run on a cadence that is **configurable between 6 and 48 hours, with a default of 24** — configurable at run time, without editing the flow.

**The source.** Prompt section 4.0. The bound values and the default are stated there and are transcribed unchanged into the property inventory of [`./api-reference.md`](./api-reference.md).

**The platform position.** A Flow Designer **scheduled trigger takes a fixed interval and cannot read a system property at run time.** The interval is part of the trigger's own configuration, so a cadence expressed as a property is not natively expressible: changing it would mean editing and re-publishing the flow, which is not run-time configuration.

**Disposition — resolved by documented workaround.** The trigger repeats **hourly**, and the flow's **first action after the trigger** is a cadence guard. The guard compares the elapsed time since the last successful run against `x_bst_startuptrk.ingestion.cadence_hours`, whose value `AppProperties` clamps to the range 6 to 48 and which ships at 24. When the configured interval has not elapsed, the execution exits before doing any work. The cadence therefore changes at run time by editing one property, which is what the requirement asks for. The guard is built per [`./manual-build/02-flow-crunchbase-ingestion.md`](./manual-build/02-flow-crunchbase-ingestion.md) and [`./manual-build/03-flow-linkedin-ingestion.md`](./manual-build/03-flow-linkedin-ingestion.md), and the property is one of the thirteen in [`./api-reference.md`](./api-reference.md).

**The operational consequence.** Because the trigger fires hourly and the guard admits one execution per cadence window, most executions do no work. The number of no-op executions between two consecutive scheduled runs is one fewer than the configured cadence in hours: **23 at the shipped cadence of 24 hours**, 5 at the minimum of 6, and 47 at the maximum of 48.

**Consequently, a "scheduled run" means an execution that passed the cadence guard.** An execution that started, found the cadence had not elapsed and exited without ingesting is a no-op: it is not a scheduled run, it does not count towards the three consecutive runs the fourth success criterion requires, and it must not appear in that criterion's evidence. The same definition is stated in [`./deployment-runbook.md`](./deployment-runbook.md), in both flow guides, and in criterion 4 of [`./validation-checklist.md` (planned)](./validation-checklist.md).

**Decision log.** [`../../docs/decisions/DECISION_LOG.md` (planned)](../../docs/decisions/DECISION_LOG.md).

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

**Decision log.** [`../../docs/decisions/DECISION_LOG.md` (planned)](../../docs/decisions/DECISION_LOG.md).

### F5 — A namespace-free API base path

**The requirement.** Serve the REST API under the base path `/api/v1/`.

**The source.** Prompt section 3.0 states the logical base path `/api/v1/` and, in the same clause, names the API namespace `x_bst_startuptrk`. The logical form has a provenance in the legacy tree: `src/shared/constants.ts:L2` declares `export const API_BASE_URL = '/api/v1';`.

**The platform position.** **A scoped Scripted REST API always carries its namespace segment in its base path.** The namespace is not optional and cannot be removed, so `/api/v1/` cannot be served by a scoped application. The logical path resolves **physically** to `/api/x_bst_startuptrk/v1/`. The prompt's own phrasing anticipates this by naming the namespace alongside the version.

**Disposition — flagged, not implemented.** The logical path is **not served and does not resolve.** No route, alias, rewrite or compatibility shim maps it to the physical path, and none is built. Every consumer calls:

```text
https://<instance>.service-now.com/api/x_bst_startuptrk/v1/<resource>
```

Every path template in [`./api-reference.md`](./api-reference.md) is relative to that physical base, so `GET /startups` means `GET /api/x_bst_startuptrk/v1/startups`. **No consumer may be written against the logical form.**

**Decision log.** [`../../docs/decisions/DECISION_LOG.md` (planned)](../../docs/decisions/DECISION_LOG.md).

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

**Decision log.** [`../../docs/decisions/DECISION_LOG.md` (planned)](../../docs/decisions/DECISION_LOG.md).

### F7 — Design-system component gaps

**The requirement.** Build the five-route portal experience from Service Portal widgets and Bootstrap components. UI Builder is forbidden by prompt section 5.0, so no `sys_ux_*` record of any kind is authored.

**The source.** Prompt section 5.0 for the mandate, and the legacy component vocabulary for the elements needing an equivalent: the Material-UI v4 set imported across `src/frontend/components/`, including the card, card-media, tabs, circular-progress and typography components.

**The platform position.** Service Portal's design system is **AngularJS with Bootstrap 3.3.6**, which is platform-native, is not installable and has no npm or PyPI identity. Five of the elements the portal needs have **no component in that library**: a chart, a multi-select chip input, a spinner, a card-media surface and a paywall treatment.

**Disposition — resolved by documented workaround, all five inside the design system.** The five are recorded as gaps **G1** through **G5** in the [Design-system gap inventory](#design-system-gap-inventory), each with the platform mechanism that resolves it and the widget that carries it. No gap is left as a placeholder and none is resolved by importing an outside library. The build mechanics are in [`./manual-build/04-service-portal-pages-and-widgets.md`](./manual-build/04-service-portal-pages-and-widgets.md).

Two further gaps are recorded in the same inventory and are **not** covered by this flag: **G6**, premium billing and checkout, which has no resolution and is [F1](#f1--premium-subscription-billing-and-payment-processing); and **G7**, the icon-system split, which is not a missing component.

**Decision log.** [`../../docs/decisions/DECISION_LOG.md` (planned)](../../docs/decisions/DECISION_LOG.md).

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

**Decision log.** [`../../docs/decisions/DECISION_LOG.md` (planned)](../../docs/decisions/DECISION_LOG.md).

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

No flow, Script Include, business rule or scheduled job in `x_bst_startuptrk` fetches or parses an HTML page. The two ingestion flows call the two named APIs through generic REST steps bound to credential aliases by name, per [`./manual-build/02-flow-crunchbase-ingestion.md`](./manual-build/02-flow-crunchbase-ingestion.md) and [`./manual-build/03-flow-linkedin-ingestion.md`](./manual-build/03-flow-linkedin-ingestion.md).

**`F003-3`, saved search.** The binding field list declares **no saved-search entity**: no saved-search table, no stored-query column and no per-user search-history record exists on any of the ten tables of [`./data-model.md`](./data-model.md), and prompt section 1.0's field definitions are closed, so none may be added. Search filters are supplied per request — as query parameters on the `/startups` list operation in [`./api-reference.md`](./api-reference.md), and as widget inputs on the Home / Search route — and are not persisted.

**`F007-5`, scheduled report delivery.** No report definition, subscription, delivery schedule or outbound email is authored in the application. The two scheduled jobs the Update Set ships are the rate-limit counter prune and the ingestion-staging prune; neither delivers a report.

**Disposition — consciously excluded, all three.** They are recorded here so that their absence reads as a decision rather than an oversight. Their positions in the feature roll-up are shown in [SRS feature coverage roll-up](#srs-feature-coverage-roll-up).

**Decision log.** [`../../docs/decisions/DECISION_LOG.md` (planned)](../../docs/decisions/DECISION_LOG.md).

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

The three users are created by Automated Test Framework setup steps at run time rather than shipped in the Update Set, because `sys_user` sits outside the application scope. The full procedure is in [`./access-control.md`](./access-control.md), the suite that executes it is built per [`./manual-build/05-atf-test-suites.md`](./manual-build/05-atf-test-suites.md), and the evidence is recorded against criterion 2 of [`./validation-checklist.md` (planned)](./validation-checklist.md).

**Any access-control result obtained without impersonation must not be recorded as evidence.** This is the point the **Security** reviewer entry in [`../../docs/review/CRITICAL_DECISIONS.md` (planned)](../../docs/review/CRITICAL_DECISIONS.md) is required to check above all others.

**Decision log.** [`../../docs/decisions/DECISION_LOG.md` (planned)](../../docs/decisions/DECISION_LOG.md).

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

**Decision log.** [`../../docs/decisions/DECISION_LOG.md` (planned)](../../docs/decisions/DECISION_LOG.md).

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

**Decision log.** [`../../docs/decisions/DECISION_LOG.md` (planned)](../../docs/decisions/DECISION_LOG.md).

## SRS feature coverage roll-up

Ten rows, one per feature of `documentation/Software Requirements Specifications (SRS).md`. Every feature is either mapped to a target artifact or explicitly excluded, so all ten are accounted for in one place.

**This roll-up is at feature level.** The **Not covered** column names every sub-requirement of that feature with no target artifact; a sub-requirement not named there is served by the artifacts in the **Target coverage** column. A dash in the **Not covered** column means every sub-requirement of that feature has a target.

| Feature | Title | Target coverage | Not covered |
| --- | --- | --- | --- |
| `F001` | Data Aggregation System, `SRS:L365` | The two Flow Designer ingestion flows, the four cleaning rules, the staging table `x_bst_startuptrk_ingest_staging`, and the cadence property `x_bst_startuptrk.ingestion.cadence_hours` | `F001-1` web crawlers — [F9](#f9--srs-requirements-with-no-prompt-counterpart) |
| `F002` | User Interface, `SRS:L379` | The five Service Portal routes — `bst_home`, `bst_company`, `bst_investor`, `bst_dashboard`, `bst_account` — with responsive support narrowed to **1024 pixels and above** | `F002-5` WCAG 2.1 Level AA conformance — see [Responsive stance](#responsive-stance--the-1024-pixel-floor) |
| `F003` | Search and Filtering, `SRS:L393` | The Home / Search route, the startup inclusion filter built by `StartupSearchService`, and the `/startups` list-and-search operation with its `name`, `industry` and `location` filters | `F003-3` saved search — [F9](#f9--srs-requirements-with-no-prompt-counterpart) |
| `F004` | Company Profiles, `SRS:L407` | The Company Profile route, page `bst_company`, with its five tabs — Overview, Funding, People, Jobs, News | `F004-4` is served by **manual entry or CSV import only**; automated news ingestion is excluded — see [Capabilities named out of scope](#capabilities-named-out-of-scope) |
| `F005` | API Access, `SRS:L421` | One `sys_ws_definition` with **31 operations** across six resources plus the nested executives sub-resource, documented in [`./api-reference.md`](./api-reference.md) | `F005-5` client SDKs — no SDK is delivered in any language |
| `F006` | User Management, `SRS:L435` | The three roles `x_bst_startuptrk.admin`, `x_bst_startuptrk.premium_user` and `x_bst_startuptrk.user`, with the table-level and field-level access controls of [`./access-control.md`](./access-control.md) | `F006-4` subscription management — [F1](#f1--premium-subscription-billing-and-payment-processing). `F006-1` registration and `F006-5` account recovery are platform concerns outside the application scope. |
| `F007` | Analytics and Reporting, `SRS:L449` | The Dashboard / Trends route, page `bst_dashboard`, and JSON export through the REST resources | `F007-5` scheduled report delivery — [F9](#f9--srs-requirements-with-no-prompt-counterpart) |
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
| `F005-5`, `F006-1`, `F006-5` | The three residuals immediately below |

Three sub-requirements are named in the roll-up and belong to no flag section. They are recorded here.

| Sub-requirement | Text as it appears | Position |
| --- | --- | --- |
| `F005-5` | "Develop SDKs for common programming languages (JavaScript, Python)" — `SRS:L433` | **Consciously excluded.** The prompt requires a Scripted REST API and its documentation; it requires no client library. No SDK, package or generated client is delivered in any language, and no repository manifest is created for one. The API contract in [`./api-reference.md`](./api-reference.md) is the sole consumer-facing artifact. |
| `F006-1` | "Implement user registration and authentication system" — `SRS:L443` | **Consciously excluded from the application scope.** Identity, authentication and session handling are platform concerns on `sys_user`, which sits outside `x_bst_startuptrk`, and prompt section 6.0 forbids modifying anything outside the scope. The application declares no identity table and no credential column; see [`./access-control.md`](./access-control.md). |
| `F006-5` | "Develop password reset and account recovery mechanisms" — `SRS:L447` | **Consciously excluded from the application scope.** Same position as `F006-1`: a `sys_user` concern outside the scope, with no counterpart in the authoritative prompt. |

**Decision log.** [`../../docs/decisions/DECISION_LOG.md` (planned)](../../docs/decisions/DECISION_LOG.md).

## Design-system gap inventory

The user-interface design system is **platform-native**: Service Portal's AngularJS 1.x with **Bootstrap 3.3.6**, both already present on the instance. It is not an npm or PyPI package, there is nothing to install, and it cannot be pinned from this repository — its version is bound to the platform release. UI Builder is forbidden by prompt section 5.0, so no `sys_ux_*` record of any kind is authored.

Seven gaps exist between what the five portal routes need and what that library provides. Six are resolved inside the system. One has no resolution.

| ID | Gap | Resolution |
| --- | --- | --- |
| **G1** | **Charts** for the Dashboard / Trends route. Bootstrap 3 has no chart component. | Platform reporting surfaced through a report or chart widget, or Angular-rendered inline SVG in a custom widget. Built as `bst-trends-charts`, whose `render_mode` option selects between the two mechanics. **Nothing is lost in the migration:** the legacy manifest declared `chart.js` at `package.json:L19` and `react-chartjs-2` at `package.json:L21` but **never imported either**, and the legacy dashboard at `src/frontend/components/Dashboard/Dashboard.tsx:L68-L106` is a six-panel grid-and-paper layout — QuickStats, RecentUpdates, TrendingStartups, FeaturedCompanies, LatestNews and JobOpenings — with **no chart import at all**. |
| **G2** | **Multi-select chip input** for `x_bst_startuptrk_investor.focus_areas`. No multiselect and no chip control exists in the library. | A platform **multi-choice** field rendered through the stock **Form** widget for write paths, and `.label` chips inside a `.panel-body` for read-only portal display. The read-only chips are built in `bst-investor-profile`. |
| **G3** | **Loading indicator.** Bootstrap 3 has no spinner. | Service Portal's own loading indicator, or a striped progress bar — `.progress` containing `.progress-bar.progress-bar-striped.active`. The striped form is built in `bst-startup-results`. |
| **G4** | **Card media**, the image surface of a result card. | A Bootstrap media object image — `.media-left` containing `img.media-object` — bound to `x_bst_startuptrk_startup.logo_url`. `.thumbnail` is the alternative container. Built in `bst-startup-results` and in the company-profile header. |
| **G5** | **Premium upsell and paywall treatment** for `x_bst_startuptrk.user`. No library component exists for the pattern. | An informational alert panel carrying a primary call to action — `.alert.alert-info` containing a `.btn.btn-primary` — rendered **in place of** each gated field or gated tab region wherever the read ACL denies, never as a blank, an empty cell or a zero. Packaged as the reusable `bst-premium-upsell` widget, embedded by `bst-company-profile`, `bst-investor-profile` and `bst-account-summary`. |
| **G6** | **Premium subscription billing and checkout.** The platform grants entitlement through roles and has no commerce capability. | **No resolution.** This is [F1](#f1--premium-subscription-billing-and-payment-processing): flagged, not implemented, not half-implemented. It is the only one of these seven gaps with no resolution. |
| **G7** | **Icon-system split.** The executive deck uses **Lucide 0.460.0** by rule mandate; the portal uses the **platform glyph font** — `.icon-search`, `.icon-user`, `.icon-chart` and the further `.icon-*` classes the release provides. | **Not unifiable, and not a defect.** The boundary runs both ways and is recorded so no agent crosses it: **no widget may reference Lucide** — no Lucide script tag, stylesheet, `data-lucide` attribute or Lucide SVG in any widget template, client controller, CSS field or theme field; and **no platform glyph may appear in the deck**, whose icons are Lucide SVG only. Both surfaces additionally carry a zero-emoji rule. |

Six gaps resolve inside the system; **G6** does not. The five component gaps G1 through G5 are collected as [F7](#f7--design-system-component-gaps); G6 is [F1](#f1--premium-subscription-billing-and-payment-processing); G7 is a boundary rather than a missing component and belongs to no flag. Every resolution above is built per [`./manual-build/04-service-portal-pages-and-widgets.md`](./manual-build/04-service-portal-pages-and-widgets.md), which carries the markup, the option schemas and the class lists.

**Decision log.** [`../../docs/decisions/DECISION_LOG.md` (planned)](../../docs/decisions/DECISION_LOG.md).

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

### Repository manifests are unchanged

**Zero dependencies are added to any repository manifest.** No `package.json`, `requirements.txt`, `pyproject.toml`, lock file, `go.mod` or `Gemfile` is created, updated or removed by this work.

- The design system **ships with the platform** and has no package identity, so it cannot be expressed in a manifest.
- The retired Material-UI packages — `"@material-ui/core": "^4.12.3"` at `package.json:L15` and `"@material-ui/icons": "^4.11.2"` at `package.json:L16` — are **left in place, untouched**, together with the declared-and-never-imported `chart.js` and `react-chartjs-2`. The legacy manifest is read-only reference.
- The two-level Update Set XML validator at [`../scripts/validate_update_set_xml.py`](../scripts/validate_update_set_xml.py) is written against the Python standard library only, so it introduces no dependency either.

**Decision log.** [`../../docs/decisions/DECISION_LOG.md` (planned)](../../docs/decisions/DECISION_LOG.md).

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

**Decision log.** [`../../docs/decisions/DECISION_LOG.md` (planned)](../../docs/decisions/DECISION_LOG.md).

### Capabilities named out of scope

Prompt section 7.2 names these capabilities as out of scope. Each row gives the repository artifacts left untouched and the one-line consequence for the delivered application.

| Capability | Repository artifacts left untouched | Consequence |
| --- | --- | --- |
| **Redis caching** | `config/redis.conf`, `src/backend/utils/cache.py`, the `redis` service in `docker-compose.yml` | **No platform cache layer is built.** No caching Script Include, no cached response and no cache-invalidation rule exists in the application. |
| **Elasticsearch** | `config/elasticsearch.yml`, the `elasticsearch` service in `docker-compose.yml` | **Search runs on encoded GlideRecord queries.** The portal search and the `/startups` list-and-search operation use case-insensitive `CONTAINS` and exact-match conditions built by `StartupSearchService`; no search index, analyser or full-text engine is configured. |
| **Docker, Nginx and Supervisor configuration** | `docker-compose.yml`, `config/nginx.conf`, `config/supervisord.conf`, `.dockerignore` | **No Dockerfile is authored** and no container, reverse proxy or process supervisor is part of the deliverable. The application runs on the Now Platform, whose runtime is the instance. |
| **IntegrationHub spokes** | — | **Generic REST steps bound to credential aliases only.** No spoke content set is installed, activated, referenced or opened, and no spoke action appears in either flow. A generic REST step is not a spoke. |
| **UI Builder** | — | **No experience or component record exists.** Zero `sys_ux_*` records of any kind are authored, and the UI Builder designer is not opened. The five routes are Service Portal pages. |
| **Automated NewsArticle ingestion** | — | **News articles are created by manual entry or CSV import only, and there is no sample CSV.** No flow writes `x_bst_startuptrk_newsarticle`, the staging table's `record_type` choice list carries no news member, and there are exactly six sample CSV files rather than seven. Manual entry is through the **News articles** module of the application menu, or a write to the `/news` REST resource. This is the position behind the `F004-4` cell of the roll-up above. |
| **Responsive design below 1024 pixels** | — | **No small-viewport refinement is authored.** See [Responsive stance — the 1024-pixel floor](#responsive-stance--the-1024-pixel-floor). |

The six sample CSV files and the import procedure are in [`./manual-build/06-staging-table-csv-import.md`](./manual-build/06-staging-table-csv-import.md) and [`../sample-data/README.md`](../sample-data/README.md); the flow build rules that forbid spokes are in [`./manual-build/02-flow-crunchbase-ingestion.md`](./manual-build/02-flow-crunchbase-ingestion.md) and [`./manual-build/03-flow-linkedin-ingestion.md`](./manual-build/03-flow-linkedin-ingestion.md).

**Decision log.** [`../../docs/decisions/DECISION_LOG.md` (planned)](../../docs/decisions/DECISION_LOG.md).

### Ambiguity resolutions besides F6

Two further ambiguities in the requirements were resolved. Both are stated here as resolutions and nothing more.

**`participating_investors` — a List field and a named join table.** Prompt section 1.5 describes the attribute as a **List** and, in the same clause, names a physical table `x_bst_startuptrk_m2m_round_investor`. **Resolution: the join table is authoritative and is the only write target for participation.** `x_bst_startuptrk_fundinground.participating_investors` exists as a `glide_list` of references to `x_bst_startuptrk_investor` — the platform's List type, which is what the requirement declares — and it is **stored, read-only and derived**: a one-way projection of the join table, refreshed by the round-investor-link business rule. **Nothing writes both**, so there is no dual write and nothing to drift. The funding-round form surfaces the **related list** over the join table as the place an administrator adds and removes participants, and the REST layer emits `participating_investors` as a **JSON array** assembled from the join table rather than from the projected column.

**"Exactly 7 custom tables" against ten physical tables.** Prompt section 1.0 states exactly seven custom tables; the application declares ten. **Resolution: the seven-table count governs the entity tables**, and prompt section 10.0 criterion 1 is evaluated against those seven only. The other three are documented separately as **supporting artifacts**: `x_bst_startuptrk_m2m_round_investor`, named verbatim by prompt section 1.5; `x_bst_startuptrk_ingest_staging`, required by prompt section 4.0's fallback dataset; and `x_bst_startuptrk_rate_limit_counter`, required to emit prompt section 8.0's rate-limit response body with a computed retry interval.

Both resolutions are specified in full in [`./data-model.md`](./data-model.md), and both are among the ambiguity resolutions that [`../../docs/review/CRITICAL_DECISIONS.md` (planned)](../../docs/review/CRITICAL_DECISIONS.md) is required to call out.

**Decision log.** [`../../docs/decisions/DECISION_LOG.md` (planned)](../../docs/decisions/DECISION_LOG.md).

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
| [`./validation-checklist.md` (planned)](./validation-checklist.md) | The evidence record whose criterion 2 depends on [F10](#f10--the-administrator-access-control-override) and whose criterion 4 depends on [F3](#f3--runtime-configurable-flow-schedule-interval). |
| [`../../docs/decisions/DECISION_LOG.md` (planned)](../../docs/decisions/DECISION_LOG.md) | The single source of truth for the "why" behind every entry above. |
| [`../../docs/decisions/TRACEABILITY_MATRIX.md` (planned)](../../docs/decisions/TRACEABILITY_MATRIX.md) | The bidirectional matrix that resolves at full coverage only if every entry above is present. |
| [`../../docs/review/CRITICAL_DECISIONS.md` (planned)](../../docs/review/CRITICAL_DECISIONS.md) | The five risk-ordered review entries, three of whose call-out categories this inventory supplies. |
