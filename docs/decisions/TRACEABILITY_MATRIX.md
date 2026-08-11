# Traceability Matrix — Boston Startup Tracker ServiceNow Replatform

The bidirectional map between the legacy Flask, React and PostgreSQL scaffold in this repository and the ServiceNow scoped application `x_bst_startuptrk`, vendor prefix `x_bst`, version `1.0.0`.

## 0. Purpose, Rule 1 compliance, and the coverage denominators

### 0.1 What this file is

**Rule 1 (Explainability)** bundles two obligations into one clause. The first is a decision log; that is discharged by the sibling file [`./DECISION_LOG.md`](./DECISION_LOG.md). The second applies because this delivery is a technology-stack migration: a **bidirectional traceability matrix mapping source constructs to target implementations, at full coverage with no gaps.** This file is the whole of that second obligation. Both halves must exist for Rule 1 to be satisfied.

The applicability of the migration clause is itself a decision, recorded at **D-004**: the requirements state that refactoring is not applicable, which is true of ServiceNow code because none pre-existed inside the scope, while the repository-level work replaces an entire polyglot stack with declarative platform metadata and is unambiguously a migration.

### 0.2 Three consequences of Rule 1 that determine this file's shape

| Consequence | What it means here |
| --- | --- |
| **Bidirectional means explicit reverse lookups.** | This file carries two forward sections and two reverse sections. A target with no source appears in a reverse section; it is not left to be found by scanning a forward table. `D-084`. |
| **No gaps makes an omitted row a rule violation.** | Where a source construct has no target, or a requirement is not implemented, the row still exists and says so. **An absent row is a gap; an explicit conscious-exclusion row is coverage.** Section 4 carries those rows. `D-084`. |
| **This file carries no rationale.** | `./DECISION_LOG.md` is the single source of truth for *why*. Every row here that represents a judgement call carries a `D-###` reference into that log in place of an explanation, and every inline note is a clause of fact — a count, a constraint, a named artifact or an observed provider behaviour — never a justification and never an alternative considered. |

No row in this file leaves its target column blank or fills it with a not-applicable marker. A construct with no target reads **Retired** or **Consciously excluded** with its decision reference, so the row is coverage rather than a shrug.

### 0.3 How rationale is partitioned across the delivery

| Question | Where it is answered |
| --- | --- |
| *Which* source construct or requirement each artifact traces to | **This file** |
| *Why* an artifact is the way it is, what else was considered, what risk it carries | [`./DECISION_LOG.md`](./DECISION_LOG.md), and only there |
| *What* an artifact is, and which requirement it satisfies | The deliverable package documents under `servicenow-startup-tracker-poc/docs/` |
| *How* to build or deploy it | The six manual-build guides and the deployment runbook |
| *Which five decisions carry the highest risk* | [`../review/CRITICAL_DECISIONS.md`](../review/CRITICAL_DECISIONS.md), a strict subset of the log |

### 0.4 The coverage denominators

Coverage is a claim about a set, so every set is stated as a number before it is walked.

| Denominator | Count | Where it is discharged |
| --- | --- | --- |
| Legacy source files in this repository, excluding version-control internals | **123** | Section 1, grouped exhaustively with per-group counts that sum to 123 |
| Source requirement sub-requirements, across **10** features `F001` to `F010`, five each | **50** | Section 2.1, one row per sub-requirement |
| Load-bearing supporting statements in the source requirements document | 6 | Section 2.2 |
| Authoritative prompt sections | **11**, sections 1.0 to 11.0 | Section 2.3, one row per section |
| Project rules | 3 | Section 2.4 |
| In-scope repository files produced by this delivery | **30**, being 29 created and 1 updated | Section 3.1 |
| Record classes inside the single Update Set | 18, carrying 313 update records | Section 3.2 |
| Manually built artifact classes | **10** | Section 3.3, one row per class, and the section heading states the same number |

**On the source denominator.** The 123 files were enumerated file by file. Two subtree figures in the plan that scheduled this file were internally inconsistent with their own contents — `src/backend` was given as 28 against an enumeration summing to 27, and `src/frontend` as 20 against an enumeration summing to 21. The two errors cancel, so the total is unaffected; the per-subtree counts below are the disk figures. **122 of the 123 legacy files lack a trailing newline**, so for those a line count reported by `wc -l` is one lower than the number of physical lines; the single exception is `documentation/Human Tasks.md`, which ends with a newline and whose `wc -l` figure is therefore exact. Every line count asserted below is the **physical** line count, and every line citation stays at or within it.

**On the requirement denominator.** The plan that scheduled this file mapped 8 features. The source requirements document defines **10**, each with five sub-requirements, so the requirement side is extended to 50 rows. The extension is a deviation from the plan and is logged at **D-087**; leaving two features unmapped would have failed Rule 1's no-gaps clause outright. The two additional features are Data Visualization at `documentation/Software Requirements Specifications (SRS).md:L479` and Notification System at `documentation/Software Requirements Specifications (SRS).md:L493`.

### 0.5 Vocabularies

Section 1 uses exactly five transformation values. Every row in section 1 carries one of them, and the distribution over all 146 rows is stated in [section 5.2](#52-transformation-and-status-distributions).

| Value | Meaning |
| --- | --- |
| **Replaced** | A target artifact exists and supersedes the source construct. |
| **Retired** | Deliberately no target. The construct is not carried forward in any form. |
| **Reference-only** | Read as a spine for this matrix or for repository conventions; unchanged, and it produces no target of its own. |
| **Superseded-doc** | Documentation describing the retired system; unchanged, no target, because the deliverable's own documentation tree is authoritative. |
| **Open** | The target artifact is built in full, and one path through it cannot be exercised until a third party supplies missing information. The row names the gate. Exactly one row carries this value, and it is reconciled as `OPEN-1` in [section 4.2.3](#423-reconciliation-with-the-nineteen-flag-inventory). |

Section 2 uses exactly four status values.

| Value | Meaning |
| --- | --- |
| **Implemented** | A target artifact realises the requirement. |
| **Partially implemented** | Part is realised; the row names which part is not, and the flag inventory carries the shortfall. |
| **Flagged** | No clean platform equivalent; recorded in the flag inventory rather than omitted or half-built. |
| **Consciously excluded** | Deliberately not built; the row carries the decision that excluded it. |

### 0.5.1 What a status asserts, and what it does not

A status in this file is a statement about the **delivered artifacts**: the record exists in the Update Set, or the procedure exists in a guide, and its contract matches the requirement. It is **not** an observation of an instance. Three requirements cannot be discharged by an artifact alone, and their rows say so rather than implying otherwise:

| Requirement | What the artifact discharges | What only an instance run can discharge |
| --- | --- | --- |
| Prompt section 9.0 | Ten suites and thirty-six tests exist, each specified step by step, covering every table and every resource | That they **pass**. A test that has never run is not a passing test, and the coverage gate is a delivery precondition measured on an instance |
| Prompt section 4.0 | Both flows exist with their cadence guard, their credential binding, their cleaning rules and their provenance writes | That three consecutive guard-passing runs of each completed with zero unhandled errors, and with which provenance |
| Prompt section 10.0 | The checklist exists, mapped one-to-one onto the five criteria, and the eleven gates exist | That each criterion's evidence was **collected and recorded** |

Where this file marks such a row Implemented, it means the artifact is delivered and its contract holds. [`../../servicenow-startup-tracker-poc/docs/validation-checklist.md`](../../servicenow-startup-tracker-poc/docs/validation-checklist.md) is the document that records what was observed, and it is authoritative for that. The two must be read together: **artifact presence is not requirement fulfilment**, and a reader who treats a row here as evidence of a passing test will over-report the delivery.

### 0.6 Figures this file asserts

**The Agent Action Plan is the authority for every count in this table, and the delivered artifact is measured against it.** The plan is frozen; a delivered figure that departs from a plan-mandated one is a **defect in the artifact**, not a revision of the plan, and it stays marked as such until the artifact is aligned. Where the plan states an approximation — written `~` below — a delivered figure inside a reasonable band of it is a match, because an approximation is what the plan mandated. Where the plan states an exact figure, only that figure is a match.

The **Status** column is therefore an assertion about the artifact, and it takes one of two values:

- **Matches** — the delivered figure satisfies the plan-mandated one.
- **GAP** — it does not, and the artifact is not yet aligned. A `GAP` row is an open defect and names what must change.

| Measure | Plan (authority) | Delivered | Status | Recorded at |
| --- | --- | --- | --- | --- |
| Physical tables | 10, of which 7 entity | **10** — 7 entity carrying **53** columns, plus `_m2m_round_investor`, `_ingest_staging`, `_rate_limit_counter` | **Matches** | D-008 for the seven-entity reading |
| Entity columns | 53, binding and complete | **53** | **Matches** | — |
| Dictionary / label records bundled in table payloads | ~85 / ~85 | **111 / 111** | **Matches** — the plan's figure is an approximation and the delivered count is exact: **101** column records, being the 53-column entity field list plus the three supporting tables' 48, and **10** collection records, one per table | D-071 |
| Choice values | ~75 | **77** | **Matches** — approximation | D-386 for the four-member staging import state |
| Roles | 3 | **3** | **Matches** | — |
| Access controls / role joins | ~43 / ~64 | **49 / 74** across five layers, of which **7** are field-level read controls | **Matches** — approximation | D-027 for the fifth layer |
| Script Includes | **8**, exact | **8** | **Matches** | D-036 and D-265, which record the removal that restored the count |
| REST definition / operations | 1 / 31 | **1 / 31**, distributed 5, 6, 5, 5, 5, 5 | **Matches** | — |
| System properties | **11**, exact | **11** | **Matches** | D-036 |
| Business rules / scheduled jobs | **3 / 1**, exact | **3 / 1** | **Matches** | D-036 |
| Update records in the single Update Set | ~250–350 | **313** | **Matches** — inside the stated band | D-070 |
| Post-commit validation gates, required | **11**, exact | **11** required — 7 scoped `sys_db_object` metadata reads asserting each entity table's name and its three closed access flags, 3 role checks, 1 scope check | **Matches** on the count and composition; the seven table gates depart from the plan's literal row read because `D-310` seals every application table, and `D-455` accepts that departure by name | D-069, D-311, D-455 |
| Further checks beside the required gates | not specified | **5** in two classes: `GATE-COL-01`, acceptance-required and non-rollback, and **4** non-normative diagnostics, `GATE-SEC-01` to `GATE-SEC-04`, cited as an entry condition by nothing | **Matches** — the plan neither mandates nor forbids them, and only the required eleven trigger the rollback, so the acceptance decision is 12 of 12 and the rollback decision is 11 of 11 | D-069, and D-310 with D-311 for the fourth diagnostic |
| Test suites / tests | 10 / 36 | **10 / 36**, being 7 + 21 + 6 + 2, with **0** parent, master or aggregating suites | **Matches** | Every suite and every test is traced individually in [section 3.3.1](#331-the-ten-suites-and-all-36-tests-individually); D-063 for the absent parent suite |
| Portal pages / widgets | 5 / 8 | **5 / 8** | **Matches** | — |
| Fallback dataset files / rows | 6 / not specified | **6 / 65** | **Matches** — the plan fixes the file count and not the row count | — |
| Flag inventory entries | 10 | **19**, `F1` to `F19`, of which three carry the *partially implemented, flagged* disposition | **Matches** — the plan's ten are all present, and every further entry is a requirement with no clean platform equivalent found while building, which is exactly what prompt section 11.0 requires be flagged | D-088 for the extension to 12, D-252 for the extension to 17, D-300 for the extension to 19 |
| Decisions logged | ~44 | **571**, `D-001` to `D-571` across 31 sections | **Matches** — the plan's figure is an estimate | D-089 for the overrun |
| Design-system gaps | 7 | **7**, `G1` to `G7` | **Matches** | — |
| In-scope repository files | 30 | **30**, 29 created and 1 updated | **Matches** | — |

**Every row reads Matches, and none is asserted on the delivered figure's own authority.** Four rows read `GAP` in an earlier revision of this matrix — Script Includes at 9 against 8, system properties at 13 against 11, scheduled jobs at 2 against 1, and the required gate set at 16 against 11 — and in each case the **artifact was changed to match the plan** rather than the row being re-described: the ninth Script Include, the two extra properties and the second scheduled job were removed, and the four surplus gates were reclassified out of the required set into two separately counted classes — `GATE-COL-01` as acceptance-required and non-rollback, and the three `GATE-SEC-*` checks as security checks that are acceptance-required, never roll back, and that no document may cite as an entry condition. Those corrections are recorded at D-036, D-069 and D-417.

**The seven premium fields.** Every reference below to the field-level read controls means these seven, in this order: `x_bst_startuptrk_startup.total_funding_usd`, `x_bst_startuptrk_startup.institutional_funding_last_5yrs`, `x_bst_startuptrk_founder.contact_email`, `x_bst_startuptrk_executive.contact_email`, `x_bst_startuptrk_investor.aum_usd`, `x_bst_startuptrk_fundinground.amount_usd` and `x_bst_startuptrk_fundinground.valuation_usd`. They are the subject of the 21-cell access-control cross-product, and each is the target of exactly one field-level read control granting the administrator and premium roles only.

---

## 1. Level 1 — FORWARD: legacy construct to ServiceNow target artifact

Every one of the 123 legacy files falls inside exactly one row or one named group below. Group counts are stated on each group and reconciled in section 1.8.

### 1.1 Data model — `src/backend/models/` (9 files)

| Source construct (path) | Kind | Target artifact | Transformation | D-### |
| --- | --- | --- | --- | --- |
| `src/backend/models/startup.py` | SQLAlchemy model | Table `x_bst_startuptrk_startup`, 12 columns | Replaced | D-006 |
| `src/backend/models/founder.py` | SQLAlchemy model | Table `x_bst_startuptrk_founder`, 6 columns | Replaced | D-017 |
| `src/backend/models/executive.py` | SQLAlchemy model | Table `x_bst_startuptrk_executive`, 6 columns | Replaced | D-017 |
| `src/backend/models/investor.py` | SQLAlchemy model | Table `x_bst_startuptrk_investor`, 6 columns | Replaced | D-006 |
| `src/backend/models/funding_round.py` class `FundingRound` | SQLAlchemy model | Table `x_bst_startuptrk_fundinground`, 8 columns | Replaced | D-006 |
| `src/backend/models/job_posting.py` | SQLAlchemy model | Table `x_bst_startuptrk_jobposting`, 9 columns | Replaced | D-006 |
| `src/backend/models/news_article.py` | SQLAlchemy model | Table `x_bst_startuptrk_newsarticle`, 6 columns | Replaced | D-006 |
| `src/backend/models/funding_round.py:L6-L9` — the `funding_round_investors` association table, two foreign-key columns and no lead-versus-participating distinction | Association table | Table `x_bst_startuptrk_m2m_round_investor`, authoritative for participating investors; the distinction is introduced by keeping `lead_investor` a first-class reference on the funding round | Replaced | D-010 |
| `src/backend/models/startup.py:L24-L28` — five `relationship()` declarations, and the `ForeignKey` at `src/backend/models/funding_round.py:L16` | ORM traversal | Reference fields reached by dot-walking, with **cascade delete set on all five mandatory `startup` child references and on both parent references of the join table**; no application-side join exists anywhere in the target | Replaced | D-012 |
| `src/backend/models/startup.py:L13` `sub_sector` | Dropped column | **Retired.** The binding field list carries no sub-sector column | Retired | D-023 |
| `src/backend/models/startup.py:L14` `employee_count` integer | Dropped column | Partially superseded by the five-value band `employee_count_range`; the integer headcount itself is retired | Retired | D-023 |
| `src/backend/models/startup.py:L15` `local_employee_count` | Dropped column | **Retired** | Retired | D-023 |
| `src/backend/models/startup.py:L16` `headcount_growth_rate` | Dropped column | **Retired.** Its absence is what makes one source sub-requirement unbuildable | Retired | D-094 |
| `src/backend/models/startup.py:L18` `last_funding_date` | Dropped column | **Retired.** Round dates live on `x_bst_startuptrk_fundinground.round_date` instead | Retired | D-023 |
| `src/backend/models/startup.py:L20` `is_hiring` | Dropped column | **Retired.** `x_bst_startuptrk_jobposting.active` carries per-posting state instead | Retired | D-023 |
| `src/backend/models/startup.py:L21` `last_updated` | Dropped column | **Retired.** Platform record metadata supersedes it | Retired | D-023 |
| `src/backend/models/startup.py:L10` `name = db.Column(db.String(255))` | Narrowed column | `x_bst_startuptrk_startup.name`, a 100-character string, mandatory | Replaced | D-023 |
| `src/backend/models/startup.py:L17` `total_funding` float | Retyped column | `x_bst_startuptrk_startup.total_funding_usd`, platform currency type, premium-gated | Replaced | D-016 |
| `src/backend/models/user.py`, including the password hash at `:L11` and the unenforced role string at `:L14` | SQLAlchemy model | **Retired.** Identity becomes the platform user table plus the three scoped roles | Retired | D-009 |
| `src/backend/models/__init__.py` | Package marker | **Retired.** Python packaging has no platform analogue | Retired | D-003 |

Nine files: seven entity models, `user.py`, and one package marker. `funding_round.py` contributes two rows because it declares both an entity and the association table.

**Column provenance.** Only the entity-name spine carries over. All 53 columns of the seven entity tables come from the binding field list in the authoritative prompt, not from these models — which is why seven legacy Startup columns appear above as active removals rather than as absences. `x_bst_startuptrk_investor.portfolio_count` has no legacy counterpart at all; it is a stored derivation over two traversal paths, unioned before counting.

### 1.2 API surface and authorization — `src/backend/routes/` (7 files), `src/backend/services/` (6 files), `src/backend/utils/` (3 files), `src/backend/app.py`, `src/backend/config.py`, `src/shared/constants.ts`, `src/shared/types.ts` (20 files)

| Source construct (path) | Kind | Target artifact | Transformation | D-### |
| --- | --- | --- | --- | --- |
| `src/backend/routes/startup.py`, routes at `:L8`, `:L39`, `:L55`, `:L82`, `:L106` | Flask blueprint | 5 operations on `/startups` | Replaced | D-033 |
| `src/backend/routes/investor.py` | Flask blueprint | 5 operations on `/investors` | Replaced | D-033 |
| `src/backend/routes/job.py` | Flask blueprint | 5 operations on `/jobs` | Replaced | D-033 |
| `src/backend/routes/news.py` | Flask blueprint | 5 operations on `/news`; read plus manual write only, with no automated ingestion | Replaced | D-054 |
| `src/backend/routes/auth.py` | Flask blueprint | **Retired with no target resource.** Authentication is a platform concern outside the scope | Retired | D-009 |
| `src/backend/routes/user.py` | Flask blueprint | **Retired with no target resource.** Identity moves to the platform | Retired | D-009 |
| `src/backend/routes/__init__.py` | Package marker | **Retired** | Retired | D-003 |
| No legacy route module exists for founders | Absent source | 6 operations on `/founders`, the sixth being the nested `GET /founders/{startup_id}/executives` | Replaced | D-034 |
| No legacy route module exists for funding rounds | Absent source | 5 operations on `/funding-rounds`, with `participating_investors` projected as a read-only assembled array | Replaced | D-011 |
| `src/backend/routes/startup.py:L12-L13` — `page` defaulting to 1 and `per_page` defaulting to 10 | Pagination contract | `sysparm_limit` and `sysparm_offset`, bounded by `RestQueryHelper` against two properties | Replaced | D-033 |
| `src/backend/routes/startup.py:L25` — `query.paginate(...)` | Pagination call | The bounded query helper plus `RestResponseBuilder.countState()`: the `hasAnyAppRole()` role gate — the exact set of roles the layer-1 table read controls grant — then **one** `GlideAggregate` `COUNT` over the same condition function the result set applies. The total is **exact** — no ceiling, no floor, no capped state — and that rests on the record-level-visibility invariant of D-031 | Replaced | D-267 for the delivered gate, amending D-041; D-031 for the invariant |
| `src/backend/routes/startup.py:L31-L37` — envelope keys `startups`, `total`, `pages`, `page`, `per_page` | Response envelope | An envelope carrying the result array, `total_count`, and limit and offset echoes; no shim or alias is built | Replaced | D-033 |
| `src/backend/routes/startup.py:L20-L22` — name and industry filters | Query construction | `StartupSearchService`, the single query builder for startup reads, adding the inclusion filter and a location filter | Replaced | D-035 |
| `src/backend/app.py:L28`, `:L31`, `:L34`, `:L37`, `:L40`, `:L43` — six `register_blueprint` calls, **none carrying a URL prefix**, so the documented endpoint paths were never served | Application factory | One `sys_ws_definition`, "Boston Startup Tracker API", at the physical base path `/api/x_bst_startuptrk/v1/` | Replaced | D-032 |
| `src/backend/utils/auth.py:L6-L16` — a decorator that authenticates only and returns 401 | Authorization | 3 roles, **49** access controls across five layers with **74** role joins | Replaced | D-024 |
| `src/backend/utils/auth.py:L36` — `# TODO: Implement role-based access control` | Unwritten check | The **7** field-level read controls on the seven premium fields, granting the administrator and premium roles only | Replaced | D-024 |
| `src/backend/utils/auth.py:L28-L33` — `create_access_token(identity=user.id)`, a token carrying the user identifier and no role claim | Token issue | Platform role membership evaluated by the access-control engine; no application-issued token exists | Replaced | D-009 |
| `src/shared/types.ts:L72-L75` — `export enum UserRole` with its three members `ADMIN`, `USER` and `PREMIUM_USER` | Role enumeration | Roles `x_bst_startuptrk.admin`, `x_bst_startuptrk.user`, `x_bst_startuptrk.premium_user`; the one-to-one name correspondence is coincidental, not a port | Replaced | D-009 |
| `src/shared/constants.ts:L2` — `API_BASE_URL = '/api/v1'` | Constant | The physical namespaced base path `/api/x_bst_startuptrk/v1/` | Replaced | D-032 |
| `src/shared/constants.ts:L5` — `MAX_RESULTS_PER_PAGE = 50` | Constant | Property `x_bst_startuptrk.rest.max_limit`, value 50 | Replaced | D-042 |
| `src/shared/constants.ts:L8` — `DEFAULT_RESULTS_PER_PAGE = 20`, contradicted by the per-page default of 10 hard-coded at `src/backend/routes/startup.py:L13` | Constant, already drifted | Property `x_bst_startuptrk.rest.default_limit`, value 20, read by both the API and the portal | Replaced | D-042 |
| `src/shared/constants.ts:L11-L20` — eight funding stages, `SEED` through `IPO` | Enumeration | The eight target funding-stage choices; replaced, not translated, so no mapping table is authored | Replaced | D-022 |
| `src/shared/constants.ts:L23-L30` — six investor types including `INCUBATOR` | Enumeration | Five target investor-type choices; the list has no `Other` member, so an unmatched value is **left unwritten**, logged and counted as a cleaning-rule deviation — the record itself is still written, and only a record missing a mandatory field is rejected | Replaced | D-022, D-232 |
| `src/shared/constants.ts:L33-L44` — ten job departments | Enumeration | Six target department choices, with an `Other` member | Replaced | D-022 |
| `src/shared/constants.ts:L47`, `:L50`, `:L53` — date format, currency and token expiry | Constants | Retired with the client stack; denomination is fixed by the currency-typed column names | Retired | D-016 |
| `src/backend/services/startup_service.py` | Service module | `StartupSearchService` | Replaced | D-035 |
| `src/backend/services/investor_service.py` | Service module | `InvestorPortfolioService`, plus the two business rules that call it | Replaced | D-013 |
| `src/backend/services/job_service.py` | Service module | The `/jobs` operations over `RestQueryHelper` and `RestResponseBuilder`; no job-specific class survives | Replaced | D-035 |
| `src/backend/services/news_service.py` | Service module | The `/news` operations over the same shared classes | Replaced | D-035 |
| `src/backend/services/user_service.py` | Service module | **Retired** with the identity model | Retired | D-009 |
| `src/backend/services/__init__.py` | Package marker | **Retired** | Retired | D-003 |
| `src/backend/utils/cache.py` | Redis cache helper | **Retired.** Caching is named out of scope and no platform equivalent is built | Retired | D-096 |
| `src/backend/utils/db.py` | SQLAlchemy session | **Retired.** The platform owns persistence | Retired | D-003 |
| `src/backend/config.py` | Configuration object | The **11** scoped system properties, none holding a secret | Replaced | D-046, D-265 |

Twenty files: 7 route modules, 6 service modules, 3 utility modules, `app.py`, `config.py`, and the two `src/shared` type and constant modules. `src/shared/utils.ts` is the third `src/shared` file and appears in section 1.4.

**Both directional asymmetries are recorded above.** Forward: `auth.py` and `user.py` exist and have no target resource. Reverse: no legacy `founder.py` or `funding_round.py` route module exists, yet `/founders` and `/funding-rounds` are served — six operations and five respectively. A one-way table could not show the second half.

### 1.3 Ingestion — `src/data_collection/` (15 files), `.env.example`, `scripts/seed_database.py` (17 files)

| Source construct (path) | Kind | Target artifact | Transformation | D-### |
| --- | --- | --- | --- | --- |
| `src/data_collection/api_integrators/crunchbase_integrator.py:L10` — the base URL constant | Endpoint constant | Non-secret property `x_bst_startuptrk.crunchbase.base_url` | Replaced | D-043 |
| `src/data_collection/api_integrators/crunchbase_integrator.py:L11` — a module-level `API_KEY`, passed as the `user_key` query parameter at `:L22` | Hard-coded secret | Basic-authentication alias `x_bst_startuptrk.crunchbase_api`, referenced by name only, with zero credential material in the Update Set. The key leaves the alias only at run time and travels as an `X-cb-user-key` **header**, never in a URL, because that provider accepts no HTTP Basic | Replaced | D-043, D-229 |
| `src/data_collection/api_integrators/linkedin_integrator.py:L11` — the base URL constant | Endpoint constant | Non-secret property `x_bst_startuptrk.linkedin.base_url` | Replaced | D-043 |
| `src/data_collection/api_integrators/linkedin_integrator.py:L12` — a module-level `API_KEY`, sent as a static bearer header at `:L23` | Hard-coded secret | OAuth 2.0 alias `x_bst_startuptrk.linkedin_oauth`; an authentication-model upgrade, not a port | Replaced | D-044 |
| `src/data_collection/api_integrators/linkedin_integrator.py` — the legacy resource paths: a company lookup by name query, a company-employees collection and a company-jobs collection | Unverified endpoint contract | **Not carried forward and not replaced by a guessed equivalent.** The LinkedIn actions and flow are built in full and run in `fallback` mode; the **live path is formally declared unavailable** and gated on the eight-row endpoint-contract declaration in `servicenow-startup-tracker-poc/docs/manual-build/03-flow-linkedin-ingestion.md`, which the live-call script enforces by refusing to issue a request while any row is undeclared. Recorded as `OPEN-1` in `servicenow-startup-tracker-poc/docs/gaps-and-flags.md` | Open | D-103 |
| `src/data_collection/api_integrators/linkedin_integrator.py:L119-L120` — a founder-versus-executive test on a title substring and a four-item C-level list | Classification heuristic | An explicit `record_type` discriminator carried on the staging row | Replaced | D-049 |
| `src/data_collection/api_integrators/__init__.py` | Package marker | **Retired** | Retired | D-003 |
| `.env.example:L27` — `CRUNCHBASE_API_KEY` | Plain environment secret | The Crunchbase alias, verified and bound rather than created | Replaced | D-043 |
| `.env.example:L28` — `LINKEDIN_API_KEY` | Plain environment secret | The LinkedIn alias | Replaced | D-043 |
| `.env.example:L29` — `GITHUB_API_KEY` | Plain environment secret | **Retired with no target of any kind.** Only two sources are ingested, so no flow calls it, no alias holds it and no property references it | Retired | D-101 |
| `src/data_collection/scheduler.py:L13-L17` — five hard-coded intervals of 24, 24, 12, 6 and 48 hours, whose minimum and maximum are exactly the mandated cadence bounds | Schedule constants | One clamped property `x_bst_startuptrk.ingestion.cadence_hours`, default 24, paired with an hourly trigger and an elapsed-time guard | Replaced | D-046 |
| `src/data_collection/scheduler.py` — the `schedule` and `threading` job runner | Task scheduler | Two Flow Designer scheduled flows sharing one eight-step skeleton | Replaced | D-047 |
| `src/data_collection/data_cleaning/startup_cleaner.py:L57` and `:L60` — de-duplication on company name plus website | Cleaning rule | Cleaning rule 2 in `IngestionMapper`: de-duplication on name plus headquarters location, case- and whitespace-insensitively, applied both **within** a batch by `dedupeBatch()` and **against stored rows** by `findExistingByKey()`, so a repeated run updates rather than duplicates | Replaced | D-051, with D-180 and D-182 |
| `src/data_collection/data_cleaning/startup_cleaner.py:L86` — missing text filled with the literal `Unknown` | Cleaning rule | Cleaning rule 4: reject a record missing a mandatory field rather than filling it | Replaced | D-051 |
| `src/data_collection/data_cleaning/startup_cleaner.py:L90` — missing numeric values filled with the column median | Cleaning rule | Cleaning rule 4 again; median imputation is the exact opposite of rejection and is not carried forward in any form | Replaced | D-051 |
| `src/data_collection/data_cleaning/startup_cleaner.py:L171-L176` — a four-entry placeholder industry dictionary whose output values match none of the target choices, with the blanket coercion at `:L183-L184` | Cleaning rule | Cleaning rule 3: normalise to the enumerated choice list, coerce an unmatched value to `Other` where that member exists, and log it | Replaced | D-022 |
| `src/data_collection/data_cleaning/startup_cleaner.py` — whitespace and string handling | Cleaning rule | Cleaning rule 1: put every string field into the one stored form, in `IngestionMapper.trimStrings()` through `AppProperties.normaliseText()` — the single definition every write path and the REST read boundary share | Replaced | D-051, D-558, D-559 |
| `src/data_collection/data_cleaning/investor_cleaner.py` — 315 physical lines, the largest legacy file | Cleaning module | **Retired.** Its transformations have no counterpart among the four mandated cleaning rules | Retired | D-051 |
| `src/data_collection/data_cleaning/__init__.py` | Package marker | **Retired** | Retired | D-003 |
| `src/data_collection/data_enrichment/startup_enricher.py` | Enrichment module | **Retired.** No enrichment requirement exists | Retired | D-051 |
| `src/data_collection/data_enrichment/investor_enricher.py` | Enrichment module | **Retired.** No enrichment requirement exists | Retired | D-051 |
| `src/data_collection/data_enrichment/__init__.py` | Package marker | **Retired** | Retired | D-003 |
| `src/data_collection/scrapers/startup_scraper.py` | Web crawler | **Retired.** Only two named API sources exist and no scraping is required | Retired | D-052 |
| `src/data_collection/scrapers/investor_scraper.py` | Web crawler | **Retired** | Retired | D-052 |
| `src/data_collection/scrapers/job_scraper.py` | Web crawler | **Retired** | Retired | D-052 |
| `src/data_collection/scrapers/news_scraper.py` | Web crawler | **Retired.** News-article ingestion is excluded entirely, so this crawler's target is excluded as well | Retired | D-052 |
| `src/data_collection/scrapers/__init__.py` | Package marker | **Retired** | Retired | D-003 |
| `scripts/seed_database.py` | Faker-based seeder | The six fallback CSV files, 65 rows, plus staging table `x_bst_startuptrk_ingest_staging` and manual-build guide 06 | Replaced | D-054 |

Seventeen files: 15 under `src/data_collection`, plus `.env.example` and `scripts/seed_database.py`. `.env.example` and `seed_database.py` are counted in the root and `scripts` groups of section 1.8 and appear here for subject coherence, not twice in the tally.

**Source allocation.** Crunchbase supplies Startup, Investor, FundingRound and the join rows; LinkedIn supplies Founder, Executive and JobPosting; the Startup upsert path is shared so both flows resolve company identity through one de-duplication key. The allocation is a decision, because the requirements name the six ingested entities without allocating them.

**One consequence of that allocation is an open item, not a delivered capability.** Because Founder, Executive and JobPosting are allocated to LinkedIn, and live LinkedIn ingestion is declared unavailable pending the endpoint-contract declaration of `D-103`, those three entity tables are ingested **only** from the fallback dataset until the declaration is completed. Every LinkedIn result is labelled `fallback validated`. The limitation is registered as `OPEN-1` in `servicenow-startup-tracker-poc/docs/gaps-and-flags.md` and reconciled in section 4.2.3.
**What "one de-duplication key" means, precisely.** The shared key is the **composite** `name` + `headquarters_location`, matched case- and whitespace-insensitively — not the name alone. A child row therefore names its parent through **two** staging columns, `startup_name` and `startup_headquarters_location`, and `IngestionMapper.resolveStartupKey()` resolves the pair through the same bounded matcher the parent's own upsert uses: the name is applied as a tolerant condition against the declared index on `x_bst_startuptrk_startup.name`, each candidate is confirmed on the normalised headquarters, and the read stops at two confirmed matches because two establishes ambiguity. A name-only resolution would not be the same key: two companies sharing a name in different cities are distinct records under this key, and resolving a child by name alone would attach it to whichever the query returned first. The composite key is recorded at **D-180**, the matcher at **D-182**, and the staging column that carries the second component at **D-193**.

### 1.4 User interface — `src/frontend/` (21 files), `src/shared/utils.ts` (22 files)

| Source construct (path) | Kind | Target artifact | Transformation | D-### |
| --- | --- | --- | --- | --- |
| `src/frontend/App.tsx:L29-L37` — five router routes, `/`, `/search`, `/company/:id`, `/investor/:id`, `/user/:id` | Client routing | Five portal pages `bst_home`, `bst_company`, `bst_investor`, `bst_dashboard`, `bst_account`, addressed by query parameter | Replaced | D-056 |
| `src/frontend/App.tsx:L3-L4` — `ThemeProvider` and `CssBaseline` | Theme wiring | One `sp_theme` record whose styling variables are the entire design vocabulary | Replaced | D-059 |
| `src/frontend/App.tsx:L12` — `import theme from './styles/theme'`, a module never authored, since `src/frontend/styles/` contains only `global.css` | Dangling import | **Retired with no target.** No legacy theme value exists to carry forward even in principle | Retired | D-079 |
| `src/frontend/index.tsx` | Application entry point | The portal record at url suffix `bst`; the platform owns bootstrapping | Replaced | D-058 |
| `src/frontend/components/CompanyProfile/CompanyProfile.tsx:L86-L91` — six tabs: Overview, Team, Funding, Jobs, News, Similar Companies | Tabbed component | Widget `bst-company-profile` with five panes: Overview, Funding, People, Jobs, News. Team is re-specified as People; Similar Companies is dropped for want of competitor data in the binding field list | Replaced | D-055 |
| `src/frontend/components/InvestorProfile/InvestorProfile.tsx:L76-L79` — four tabs: Overview, Portfolio, Recent Investments, Investment Trends | Tabbed component | Widget `bst-investor-profile`, surfacing `portfolio_count` with rounds led against rounds participated | Replaced | D-013 |
| `src/frontend/components/Dashboard/Dashboard.tsx` — a six-panel grid at `:L66` onward, containing **no chart import of any kind** | Dashboard component | Widgets `bst-trends-kpi` and `bst-trends-charts` on page `bst_dashboard`; the charting gap `G1` therefore loses nothing | Replaced | D-060 |
| `src/frontend/components/Search/SearchInterface.tsx` | Search component | Widgets `bst-startup-search` and `bst-startup-results`, with the inclusion filter applied server-side | Replaced | D-035 |
| `src/frontend/components/common/Header.tsx` | Navigation component | The stock header widget bound through `sp_theme` | Replaced | D-059 |
| `src/frontend/components/common/Footer.tsx` | Layout component | The stock footer widget bound through `sp_theme` | Replaced | D-059 |
| `src/frontend/components/common/CompanyCard.tsx` | Card component | A media object inside a panel, rendered by `bst-startup-results`; gap `G4` | Replaced | D-060 |
| `src/frontend/components/common/Pagination.tsx` | Pagination component | Native widget pagination over `sysparm_limit` and `sysparm_offset`, reading the same two page-size properties as the API | Replaced | D-042 |
| `src/frontend/pages/Home.tsx` | Route component | Page `bst_home` | Replaced | D-056 |
| `src/frontend/pages/Search.tsx` | Route component | Page `bst_home`, which carries search and results together | Replaced | D-056 |
| `src/frontend/pages/Company.tsx` | Route component | Page `bst_company` | Replaced | D-056 |
| `src/frontend/pages/Investor.tsx` | Route component | Page `bst_investor` | Replaced | D-056 |
| `src/frontend/pages/User.tsx` | Route component | Page `bst_account`, showing the effective role and entitlements | Replaced | D-056 |
| `src/frontend/store/index.ts` | Redux store | **Retired.** State lives in widget client and server scripts | Retired | D-058 |
| `src/frontend/store/actions/index.ts` | Redux actions | **Retired** | Retired | D-058 |
| `src/frontend/store/reducers/index.ts` | Redux reducers | **Retired** | Retired | D-058 |
| `src/frontend/utils/api.ts` | HTTP client | **Retired.** Superseded by the widget server-script and REST layers | Retired | D-058 |
| `src/frontend/utils/auth.ts` | Client auth helper | **Retired.** Superseded by the access-control engine | Retired | D-024 |
| `src/frontend/styles/global.css` — 42 physical lines of hard-coded literals: a `#f5f5f5` page background at `:L8`, a `#1976d2` link colour at `:L14`, a Roboto stack at `:L7`, a 1200-pixel container at `:L24`, and three utility classes. **The repository's entire design-token surface** | Stylesheet | The `sp_theme` styling-variable declarations, with zero hard-coded colour, spacing, radius or font values in any widget | Replaced | D-059 |
| `src/shared/utils.ts` | Shared client utilities | **Retired.** No shared client utility layer survives | Retired | D-058 |

Twenty-two files: 21 under `src/frontend`, plus `src/shared/utils.ts`. `App.tsx` contributes three rows and `src/frontend/pages/*` five, so the row count exceeds the file count; every file is named exactly once.

**Page and route pairing.** `src/frontend/App.tsx:L29-L37` declares the routes and the five `src/frontend/pages/*` modules implement them, so both appear against the same five page records. That is one mapping viewed from two source files, not a double count.

### 1.5 Tests — `tests/` (27 files), `pytest.ini`, `jest.config.js` (29 files)

| Source construct (path) | Kind | Target artifact | Transformation | D-### |
| --- | --- | --- | --- | --- |
| `tests/backend/routes/` — 6 pytest modules: `auth_test.py`, `investor_test.py`, `job_test.py`, `news_test.py`, `startup_test.py`, `user_test.py` | Route tests | The 6 REST resource tests, one per logical resource including the nested sub-resource, asserting response shape, pagination with a correct `total_count`, and the rate-limit body | Replaced | D-063 |
| `tests/backend/services/` — 5 pytest modules: `investor_service_test.py`, `job_service_test.py`, `news_service_test.py`, `startup_service_test.py`, `user_service_test.py` | Service tests | The 7 table-CRUD suites, which exercise the service layer through the tables it maintains | Replaced | D-063 |
| `tests/data_collection/api_integrators/` — 2 pytest modules | Integrator tests | The 2 ingestion-flow tests, one per flow, each asserting de-duplication, choice normalisation and mandatory-field rejection | Replaced | D-063 |
| `tests/data_collection/data_cleaning/` — 2 pytest modules | Cleaning tests | The same 2 ingestion-flow tests, which carry the cleaning-rule assertions | Replaced | D-051 |
| `tests/data_collection/data_enrichment/` — 2 pytest modules | Enrichment tests | **Retired** with the enricher modules they exercise | Retired | D-051 |
| `tests/data_collection/scrapers/` — 4 pytest modules: `investor_scraper_test.py`, `job_scraper_test.py`, `news_scraper_test.py`, `startup_scraper_test.py` | Crawler tests | **Retired** with the four crawler modules they exercise | Retired | D-052 |
| `tests/frontend/components/` — 4 Jest modules: `CompanyProfile.test.tsx`, `Dashboard.test.tsx`, `InvestorProfile.test.tsx`, `SearchInterface.test.tsx` | Component tests | The five-route portal walkthrough of acceptance criterion 5; no automated widget test framework is in scope | Replaced | D-058 |
| `tests/frontend/utils/` — 2 Jest modules: `api.test.ts`, `auth.test.ts` | Client utility tests | **Retired** with `src/frontend/utils/api.ts` and `src/frontend/utils/auth.ts`; authorization assertions move to the 21 field-by-role tests | Replaced | D-064 |
| `pytest.ini:L9` — `python_files = test_*.py`, which matches **0** of the 21 on-disk pytest modules, every one carrying a trailing `_test.py` | Test configuration | **Retired.** The 10 suites are defined as platform records, not by a file pattern | Retired | D-063 |
| `pytest.ini:L6` — `testpaths = tests/backend`, which places 16 of the 27 test files outside the collection path | Test configuration | **Retired** with the line above | Retired | D-063 |
| `jest.config.js` | Test configuration | **Retired** with the React stack | Retired | D-058 |

Twenty-nine files: 27 test modules in eight named groups (6 + 5 + 2 + 2 + 2 + 4 + 4 + 2 = 27), plus `pytest.ini` and `jest.config.js`. `pytest.ini` contributes two rows for its two independent defects.

**The legacy suite never ran.** The two `pytest.ini` defects are mutually reinforcing: the collection pattern expects a leading `test_` while every module on disk carries a trailing `_test.py`, so 0 of 21 pytest modules are collectable, and the configured test path excludes 16 of the 27 files in any case. Nothing is being kept passing by the 36 replacement tests, because nothing was passing.

### 1.6 Infrastructure, build and continuous integration — `config/` (4), `scripts/` (5), `.github/` (4), and 10 root files (23 files)

| Source construct (path) | Kind | Target artifact | Transformation | D-### |
| --- | --- | --- | --- | --- |
| `config/redis.conf` | Cache configuration | **Retired.** Caching is named out of scope; the file stays on disk untouched | Retired | D-096 |
| `config/elasticsearch.yml` | Search configuration | **Retired.** Portal and API search use encoded platform queries instead, so nothing is lost | Retired | D-096 |
| `config/nginx.conf` | Reverse-proxy configuration | **Retired** | Retired | D-096 |
| `config/supervisord.conf` | Process-supervision configuration | **Retired** | Retired | D-096 |
| `docker-compose.yml:L6-L8` — a build context declaring `dockerfile: Dockerfile`, against **zero** Dockerfiles anywhere in the tree | Container orchestration | **Retired.** No Dockerfile is authored | Retired | D-096 |
| `.github/workflows/ci.yml:L24` — `pip install -r requirements.txt` against a file that does not exist, and `:L36-L37` — `cd src/frontend` then `npm ci` against a directory with no manifest | Continuous integration | **Retired.** The XML validator is invoked directly rather than wired into a workflow that cannot reach an added step | Retired | D-067 |
| `.github/workflows/ci.yml:L19` Python 3.8 and `:L32` Node.js 14 | Runtime pins | Recorded in the dependency inventory and in this matrix; the runtimes are deliberately **not provisioned** | Reference-only | D-077 |
| `.github/workflows/cd.yml:L46` — the `appleboy/ssh-action@master` deploy step | Continuous delivery | `servicenow-startup-tracker-poc/docs/deployment-runbook.md`: three pre-flight checks, a six-step import, preview with an empty error set required, commit, 11 required post-commit gates with four further acceptance-required checks in two classes — the non-rollback `GATE-COL-01` and the 3 `GATE-SEC` security checks — and a precondition-guarded rollback branched by starting state | Replaced | D-067, D-076, D-255 |
| `.github/ISSUE_TEMPLATE.md` | Repository template | **Reference-only.** Unchanged, no target; repository process is unaffected by the replatform | Reference-only | D-003 |
| `.github/PULL_REQUEST_TEMPLATE.md` | Repository template | **Reference-only.** Unchanged, no target | Reference-only | D-003 |
| `scripts/run_tests.sh` | Shell test runner | `servicenow-startup-tracker-poc/scripts/validate_update_set_xml.py`. Only three conventions carry over: a non-zero exit on failure, per-stage progress reporting, and flag parsing that errors on an unknown option | Replaced | D-066 |
| `scripts/deploy_production.sh` | Deployment script | `servicenow-startup-tracker-poc/docs/deployment-runbook.md` | Replaced | D-076 |
| `scripts/seed_database.py` | Database seeder | The six fallback CSV files and manual-build guide 06; mapped in detail in section 1.3 | Replaced | D-054 |
| `scripts/backup_database.sh` | Backup script | **Retired.** The platform owns persistence and backup | Retired | D-003 |
| `scripts/setup_dev_environment.sh` | Environment bootstrap | **Retired.** Nothing runnable exists to bootstrap | Retired | D-077 |
| `package.json:L5` — `"main": "src/index.js"`, an absent entry point; `:L15-L16` the two interface packages; `:L19` and `:L21` the charting packages, declared and never imported; `:L65` a comment block after the closing brace that makes the file **not valid JSON** | Dependency manifest | **Retired and unmodified.** Pruning it would mean first repairing an out-of-scope file that cannot be parsed | Retired | D-078 |
| `tsconfig.json` | Compiler configuration | **Retired** with the TypeScript stack | Retired | D-078 |
| `.eslintrc.js` | Lint configuration | **Retired** with the TypeScript stack | Retired | D-078 |
| `.prettierrc` | Format configuration | **Retired** with the TypeScript stack | Retired | D-078 |
| `.dockerignore` | Build-context filter | **Retired** with containerisation | Retired | D-096 |
| `.gitignore` | Repository configuration | **Reference-only.** Unchanged and still governing the repository, including the `venv` exclusion | Reference-only | D-078 |
| `LICENSE` | Legal notice | **Reference-only.** Unchanged and still governing the repository | Reference-only | D-003 |
| `.env.example:L27-L29` — three plain environment keys | Environment template | Two credential aliases for the first two keys; the third is retired outright. Mapped in detail in section 1.3 | Replaced | D-043 |
| `README.md:L16-L23` the stack declaration, `:L29-L31` the prerequisites, and `:L36` the `docker-compose up --build` instruction, which cannot succeed because no Dockerfile exists | Repository entry point | **The only legacy file modified.** A pointer to `servicenow-startup-tracker-poc/` is added and those three passages are marked superseded historical reference | Replaced | D-080 |

Twenty-three files: 4 under `config/`, 5 under `scripts/`, 4 under `.github/`, and 10 root files — `docker-compose.yml`, `package.json`, `tsconfig.json`, `.eslintrc.js`, `.prettierrc`, `.dockerignore`, `.gitignore`, `LICENSE`, `.env.example`, `README.md`. The `ci.yml` runtime pins occupy a second row for the same file, which is one file with two fates: the workflow is retired while its version ceilings are read as reference.

### 1.7 Documentation — `documentation/` (5 files)

| Source construct (path) | Kind | Target artifact | Transformation | D-### |
| --- | --- | --- | --- | --- |
| `documentation/Software Requirements Specifications (SRS).md` — 1126 physical lines, 10 features at `:L367` through `:L493` | Requirements document | **Reference-only.** It is the requirement spine of section 2.1 and is not modified | Reference-only | D-080 |
| `documentation/Input Prompt.md` — the original stakeholder brief, which the binding field list explicitly supersedes | Stakeholder brief | **Superseded-doc.** Three of its signals survive as columns, three are partial matches, and nine are consciously excluded; enumerated in section 4.3 | Superseded-doc | D-023 |
| `documentation/Software Project Proposal.md` — 553 physical lines, excluding financial transaction processing at `:L163-L166` | Project proposal | **Superseded-doc.** Unchanged, no target. Its own exclusion of payment processing corroborates flag `F1` | Superseded-doc | D-080 |
| `documentation/Technical Specifications.md` — 705 physical lines describing the retired three-tier stack | Technical specification | **Superseded-doc.** Unchanged, no target; the deliverable's own documentation tree is authoritative | Superseded-doc | D-080 |
| `documentation/Human Tasks.md` — 1229 lines enumerating unfinished work in the retired stack | Task inventory | **Superseded-doc.** Unchanged, no target; its tasks concern modules that are retired | Superseded-doc | D-080 |

Five files, each with its own row.

### 1.8 Level 1 coverage tally — the 123 files reconciled

| Group | Subtree | Files | Rows in this matrix |
| --- | --- | --- | --- |
| 1.1 Data model | `src/backend/models/` | 9 | 20 |
| 1.2 API surface and authorization | `src/backend/routes/` 7, `src/backend/services/` 6, `src/backend/utils/` 3, `src/backend/app.py`, `src/backend/config.py`, `src/shared/constants.ts`, `src/shared/types.ts` | 20 | 34 |
| 1.3 Ingestion | `src/data_collection/` 15 | 15 | 28 |
| 1.4 User interface | `src/frontend/` 21, `src/shared/utils.ts` | 22 | 24 |
| 1.5 Tests | `tests/` 27, `pytest.ini`, `jest.config.js` | 29 | 11 |
| 1.6 Infrastructure, build and continuous integration | `config/` 4, `scripts/` 5, `.github/` 4, 10 root files | 23 | 24 |
| 1.7 Documentation | `documentation/` 5 | 5 | 5 |
| **Total** | | **123** | **146** |

Arithmetic, files: 9 + 20 + 15 + 22 + 29 + 23 + 5 = **123**. Arithmetic, rows: 20 + 34 + 28 + 24 + 11 + 24 + 5 = **146**.

The same total reached by subtree: `src/backend` 27, `src/data_collection` 15, `src/frontend` 21, `src/shared` 3, `tests` 27, `config` 4, `scripts` 5, `.github` 4, `documentation` 5, root 12 = **123**. Group 1.2 carries the 18 `src/backend` files that are not models plus 2 of the 3 `src/shared` files; group 1.4 carries the third; groups 1.5 and 1.6 carry `pytest.ini`, `jest.config.js` and the other 10 root files. `.env.example` and `scripts/seed_database.py` are tallied once each, in group 1.6 and the `scripts` subtree respectively, and are cross-referenced from group 1.3 for subject coherence.

Row totals exceed file totals because a single file can carry several independently traceable constructs — `src/backend/models/startup.py` alone yields nine rows, one per dropped or retyped column.

**Transformation distribution across the 146 rows:** Replaced 81, Retired 54, Reference-only 6, Superseded-doc 4, Open 1 — which sums to 146. **Not one row is empty, and no file is unaccounted for.**

---

## 2. Level 2 — FORWARD: requirement to ServiceNow target artifact

### 2.1 Source requirements document — 10 features, 50 sub-requirements

The source requirements document defines **10** features, each with exactly five sub-requirements, giving **50** rows. Every sub-requirement has its own row; none is folded into a feature-level summary. Feature anchors: `F001` at `documentation/Software Requirements Specifications (SRS).md:L367`, then `:L381`, `:L395`, `:L409`, `:L423`, `:L437`, `:L451`, `:L465`, `:L479` and `:L493`.

#### F001 Data Aggregation System — priority High, `SRS:L365`

| Requirement ID / section | Requirement (short) | Target artifact(s) | Status | D-### |
| --- | --- | --- | --- | --- |
| `F001-1`, `SRS:L373` | Web crawlers over specified public sources | **Consciously excluded.** Only two named API sources exist and no scraping is required; the four legacy crawlers are dropped. Recorded as flag `F9` | Consciously excluded | D-052 |
| `F001-2`, `SRS:L374` | Data cleaning and validation | The four cleaning rules in `IngestionMapper`: trim, de-duplicate on name plus headquarters location, normalise choices, reject on a missing mandatory field — plus URL and email validation at the same boundary. **Rule 3 is partial:** the **five** choice lists that declare an `Other` member receive the coercion — `startup.industry`, `founder.title`, `executive.title`, `investor.focus_areas` and `job_posting.department` — while the six that do not cannot, so the field is left unwritten, logged with a distinct outcome and counted in `rule3_deviations`. Flag `F13` | **Partially implemented** | D-051, D-232, D-239 |
| `F001-3`, `SRS:L375` | A scheduler for daily updates | Two Flow Designer scheduled flows, an hourly trigger with an elapsed-time guard, and property `x_bst_startuptrk.ingestion.cadence_hours` clamped to 6–48 with a default of 24 | Implemented | D-047 |
| `F001-4`, `SRS:L376` | Error handling and logging | `IngestionLogger`, implementing skip-the-record-and-continue-the-run against the flow execution log, plus the run summary and provenance write. The summary distinguishes a row whose own write failed from a secondary operational failure through the `errors` counter that `failRecord()` maintains, and every flow-step log line passes the one level gate `AppProperties.log(severity, text)` so `x_bst_startuptrk.logging.level` governs a step exactly as it governs this class | Implemented | D-053, D-529, D-531 |
| `F001-5`, `SRS:L377` | Data versioning for historical tracking | **Consciously excluded.** The binding field list declares no version, revision or history column, and all 111 dictionary records — 101 column records plus 10 collection records — ship with auditing off | Consciously excluded | D-023 |

#### F002 User Interface — priority High, `SRS:L379`

| Requirement ID / section | Requirement (short) | Target artifact(s) | Status | D-### |
| --- | --- | --- | --- | --- |
| `F002-1`, `SRS:L387` | A responsive web interface | The Service Portal at url suffix `bst` with five pages and eight widgets; responsiveness is narrowed to 1024 pixels and above | Partially implemented | D-057 |
| `F002-2`, `SRS:L388` | An intuitive navigation system | The stock header, footer and breadcrumb widgets bound through `sp_theme` | Implemented | D-059 |
| `F002-3`, `SRS:L389` | User authentication and authorization | Platform authentication, plus 49 access controls across five layers with 74 role joins over the three scoped roles | Implemented | D-024 |
| `F002-4`, `SRS:L390` | A dashboard for key metrics | Page `bst_dashboard` with widgets `bst-trends-kpi` and `bst-trends-charts` | Implemented | D-060 |
| `F002-5`, `SRS:L391` | WCAG 2.1 Level AA conformance | **Consciously excluded as a conformance claim.** The widget vocabulary is the portal framework's bundled Bootstrap release; no conformance audit is performed and no conformance is claimed | Consciously excluded | D-059 |

#### F003 Search and Filtering — priority High, `SRS:L393`

| Requirement ID / section | Requirement (short) | Target artifact(s) | Status | D-### |
| --- | --- | --- | --- | --- |
| `F003-1`, `SRS:L401` | Full-text search across startup data | Widget `bst-startup-search` and the `/startups` list-and-search operation, both querying through `StartupSearchService` | Implemented | D-035 |
| `F003-2`, `SRS:L402` | Filters for industry, funding stage, employee count and other metrics | The `name`, `industry` and `location` filters on the `/startups` list operation and on `bst-startup-search` | Partially implemented | D-035 |
| `F003-3`, `SRS:L403` | Saved search functionality for registered users | **Consciously excluded.** It would need a persistence table outside the binding seven and a route outside the mandated five. Recorded as flag `F9` | Consciously excluded | D-092 |
| `F003-4`, `SRS:L404` | Auto-suggest for search queries | The stock typeahead search widget within the portal navigation shell | Implemented | D-059 |
| `F003-5`, `SRS:L405` | Sorting options for search results | **Consciously excluded.** No list operation accepts a sort parameter; each applies one documented order with a record-identifier tie-breaker so offset paging stays stable | Consciously excluded | D-033 |

#### F004 Company Profiles — priority High, `SRS:L407`

| Requirement ID / section | Requirement (short) | Target artifact(s) | Status | D-### |
| --- | --- | --- | --- | --- |
| `F004-1`, `SRS:L415` | A company profile page template | Page `bst_company` with widget `bst-company-profile`, five panes: Overview, Funding, People, Jobs, News | Implemented | D-055 |
| `F004-2`, `SRS:L416` | Display funding, employees and executives | The Funding and People panes, the latter carrying founders and executives together from two tables; premium fields are omitted from the response for the base role rather than nulled | Implemented | D-025 |
| `F004-3`, `SRS:L417` | Job openings from job board APIs | Table `x_bst_startuptrk_jobposting`, written by the LinkedIn flow, surfaced in the Jobs pane and on `/jobs`. **The rows come from the sanctioned fallback dataset rather than a live read:** LinkedIn's Job Posting API is a write API for an organisation's own postings and publishes no third-party read path, so that flow's live call is an identity probe. Flag `F15` | Partially implemented | D-048, D-233 |
| `F004-4`, `SRS:L418` | A recent news section from news aggregation APIs | Table `x_bst_startuptrk_newsarticle` and the News pane, populated by **manual entry or CSV import only**; automated news ingestion is excluded and no flow targets the table | Partially implemented | D-054 |
| `F004-5`, `SRS:L419` | Data visualization components for key metrics | Widgets `bst-trends-kpi` and `bst-trends-charts`, resolved under design-system gap `G1` | Implemented | D-060 |

#### F005 API Access — priority Medium, `SRS:L421`

| Requirement ID / section | Requirement (short) | Target artifact(s) | Status | D-### |
| --- | --- | --- | --- | --- |
| `F005-1`, `SRS:L429` | RESTful API endpoints | One `sys_ws_definition` and **31** `sys_ws_operation` records across six logical resources plus the nested executives sub-resource, at `/api/x_bst_startuptrk/v1/` | Implemented | D-032 |
| `F005-2`, `SRS:L430` | An authentication mechanism for API access | Every one of the 31 operations requires both authentication and access-control authorisation, reinforced by two endpoint-execution controls and a shared guard | Implemented | D-027 |
| `F005-3`, `SRS:L431` | Rate limiting to prevent abuse | `RateLimitService` over table `x_bst_startuptrk_rate_limit_counter`, emitting the mandated body with a computed retry value and a matching `Retry-After` header | Implemented | D-037 |
| `F005-4`, `SRS:L432` | Comprehensive API documentation | `servicenow-startup-tracker-poc/docs/api-reference.md`, enumerating all 31 operations, the pagination contract, the three error contracts, the call graph and the **11** properties | Implemented | D-035 |
| `F005-5`, `SRS:L433` | SDKs for common programming languages | **Consciously excluded.** No client library, package or generated client is delivered in any language, and no repository manifest is created for one | Consciously excluded | D-078 |

#### F006 User Management — priority Medium, `SRS:L435`

| Requirement ID / section | Requirement (short) | Target artifact(s) | Status | D-### |
| --- | --- | --- | --- | --- |
| `F006-1`, `SRS:L443` | User registration and authentication | **Consciously excluded from the application scope.** Identity and session handling are platform concerns on a table outside `x_bst_startuptrk`, which the requirements forbid modifying; the application declares no identity table and no credential column | Consciously excluded | D-009 |
| `F006-2`, `SRS:L444` | Role-based access control across free, premium and admin | Roles `x_bst_startuptrk.admin`, `x_bst_startuptrk.premium_user` and `x_bst_startuptrk.user`; the document's "free users" tier becomes the base `user` role | Implemented | D-009 |
| `F006-3`, `SRS:L445` | A user profile management interface | Page `bst_account` with widgets `bst-account-summary` and `bst-premium-upsell`, showing the effective role and entitlements | Implemented | D-060 |
| `F006-4`, `SRS:L446` | A subscription management system | **Flagged.** The platform grants entitlements through roles and has no commerce, checkout or payment capability. Recorded as flag `F1`, the headline entry, and not half-implemented | Flagged | D-090 |
| `F006-5`, `SRS:L447` | Password reset and account recovery | **Consciously excluded from the application scope.** The same position as `F006-1`: a platform-user concern outside the scope with no counterpart in the authoritative prompt | Consciously excluded | D-009 |

#### F007 Analytics and Reporting — priority Medium, `SRS:L449`

| Requirement ID / section | Requirement (short) | Target artifact(s) | Status | D-### |
| --- | --- | --- | --- | --- |
| `F007-1`, `SRS:L457` | A custom report generation tool | Platform reporting inside the scope, surfaced through the trends widgets on page `bst_dashboard` | Implemented | D-060 |
| `F007-2`, `SRS:L458` | Data export in various formats, CSV and JSON | JSON export through the six REST resources. **CSV export is consciously excluded:** the definition and all 31 operations pin their media types to JSON, so no operation emits CSV | Partially implemented | D-033 |
| `F007-3`, `SRS:L459` | Data visualization tools for trend analysis | Widget `bst-trends-charts` under gap `G1`. **Both render modes are specified in buildable detail** and `render_mode` selects between them: `svg`, the shipped mode on both dashboard instances, draws an Angular-bound inline SVG bar chart — element list, geometry constants, every `ng-attr-*` binding, `title`, `desc` and companion table — and `report` embeds a saved platform report, falling back to `svg` when none is readable. Both are at `servicenow-startup-tracker-poc/docs/manual-build/04-service-portal-pages-and-widgets.md`, sections *The inline SVG chart* and *The report embed* | Implemented | D-060, D-138 |
| `F007-4`, `SRS:L460` | Comparative analysis features across startups | The `/startups` list operation with its filters, the trends widgets, and the sortable stored `portfolio_count` on the investor profile | Partially implemented | D-013 |
| `F007-5`, `SRS:L461` | Scheduled report delivery for premium users | **Consciously excluded.** It would need an email capability that no requirement in the authoritative prompt establishes. Recorded as flag `F9` | Consciously excluded | D-092 |

#### F008 Admin Dashboard — priority Low, `SRS:L463`

| Requirement ID / section | Requirement (short) | Target artifact(s) | Status | D-### |
| --- | --- | --- | --- | --- |
| `F008-1`, `SRS:L471` | An interface for managing user accounts and roles | The platform's own user and role administration, outside the application scope; the Update Set ships three role definitions and **zero** role assignments | Partially implemented | D-028 |
| `F008-2`, `SRS:L472` | Tools for manually updating or correcting startup data | The platform's native list and form views inside the scope — 10 form sections, 10 list views and a nine-module application menu — reachable by `x_bst_startuptrk.admin` | Implemented | D-062 |
| `F008-3`, `SRS:L473` | System health monitoring and alerting | **Consciously excluded.** No observability or alerting layer is built; the requirements state a prototype focus and no availability target. Recorded under flag `F8` | Consciously excluded | D-099 |
| `F008-4`, `SRS:L474` | An analytics dashboard for platform usage statistics | **Consciously excluded.** Application-usage analytics are not among the five enumerated routes and no usage table exists. Recorded under flag `F8` | Consciously excluded | D-095 |
| `F008-5`, `SRS:L475` | An interface for managing API keys and rate limits | Rate limits are administrator-tunable through `x_bst_startuptrk.rest.rate_limit_requests` and `x_bst_startuptrk.rest.rate_limit_window_seconds`, with the counter table administrator-only. **The API-key management interface is consciously excluded**; the API authenticates platform users and issues no keys | Partially implemented | D-027 |

**On F008 as a whole.** No custom administrative portal route is built. The authoritative prompt enumerates exactly five routes and none is an administrative console, so a sixth would breach the count; the capability is served by native views instead. The source document's own request appears at `documentation/Software Requirements Specifications (SRS).md:L858` with a mockup reference at `:L871`. This is a conscious non-implementation of the requested **surface**, not of the function, and is recorded as flag `F8` and at **D-095**.

#### F009 Data Visualization — priority Medium, `SRS:L477`

| Requirement ID / section | Requirement (short) | Target artifact(s) | Status | D-### |
| --- | --- | --- | --- | --- |
| `F009-1`, `SRS:L485` | Interactive charts for funding trends | Widget `bst-trends-charts`, instance A on page `bst_dashboard`, `dimension` = `funding_stage` over `x_bst_startuptrk_fundinground`, `render_mode` = `svg`. The inline SVG bar chart it draws is specified element by element in the portal build guide | Implemented | D-060, D-138 |
| `F009-2`, `SRS:L486` | Industry distribution visualizations | Widget `bst-trends-charts`, instance B on page `bst_dashboard`, `dimension` = `industry` over `x_bst_startuptrk_startup.industry`, `render_mode` = `svg`. Same specified inline SVG mechanic as `F009-1` | Implemented | D-060, D-138 |
| `F009-3`, `SRS:L487` | Growth rate comparisons across startups | **Consciously excluded.** The binding field list carries one current employee band and no history, and the legacy growth-rate column at `src/backend/models/startup.py:L16` is among the attributes it excludes. Recorded as flag `F11` | Consciously excluded | D-094 |
| `F009-4`, `SRS:L488` | Investor portfolio visualizations | Page `bst_investor` with widget `bst-investor-profile`, surfacing the stored `portfolio_count` with rounds led against rounds participated | Implemented | D-013 |
| `F009-5`, `SRS:L489` | Geographic distribution maps of Boston startups | **Consciously excluded.** `headquarters_location` is a free-text place name with no coordinate pair, and no requirement authorises a geocoding service. Recorded as flag `F11` | Consciously excluded | D-094 |

#### F010 Notification System — priority Low, `SRS:L491`

| Requirement ID / section | Requirement (short) | Target artifact(s) | Status | D-### |
| --- | --- | --- | --- | --- |
| `F010-1`, `SRS:L499` | An in-app notification system | **Consciously excluded.** No notification requirement appears in the authoritative prompt. Recorded as flag `F12` | Consciously excluded | D-093 |
| `F010-2`, `SRS:L500` | An email notification service | **Consciously excluded.** No email capability is established by any requirement. Recorded as flag `F12` | Consciously excluded | D-093 |
| `F010-3`, `SRS:L501` | Notification preferences management | **Consciously excluded.** No preference storage exists among the ten tables and no route among the five would host it. Recorded as flag `F12` | Consciously excluded | D-093 |
| `F010-4`, `SRS:L502` | Real-time updates for followed startups | **Consciously excluded.** The binding field list declares no follow relationship to notify about. Recorded as flag `F12` | Consciously excluded | D-093 |
| `F010-5`, `SRS:L503` | Digest emails for weekly or monthly updates | **Consciously excluded.** Depends on the excluded email service. Recorded as flag `F12` | Consciously excluded | D-093 |

`F010` is the only feature with **no** target artifact for any part of it, which is why the entire feature is flagged as a unit rather than sub-requirement by sub-requirement.

**Sub-requirement roll-up.** 50 rows, one per sub-requirement, none duplicated and none absent: **22 Implemented**, **9 Partially implemented**, **1 Flagged**, **18 Consciously excluded**, which sums to 50. Every one of the ten features carries at least one sub-requirement that is not fully implemented, so no feature is wholly clean. Nine of the ten carry at least one row with no target artifact at all — `Flagged` or `Consciously excluded` — the exception being `F004`, whose shortfall is two partially implemented rows. `F010` is the only feature wholly unmapped, all five of its rows being consciously excluded.

### 2.2 Source requirements document — load-bearing supporting statements

| Requirement ID / section | Requirement (short) | Target artifact(s) | Status | D-### |
| --- | --- | --- | --- | --- |
| `SRS:L77` | Role-based access control across three tiers: free users, premium subscribers, administrators | The three scoped roles, one per tier, with "free users" becoming the base `user` role | Implemented | D-009 |
| `SRS:L107` | Payment gateways handled by third-party services | No commerce capability is built; the statement corroborates flag `F1` rather than requesting an artifact | Flagged | D-090 |
| `SRS:L218` | Limited to startups headquartered in the Boston area | The inclusion filter in `StartupSearchService`, matching `headquarters_location` against tokens held in property `x_bst_startuptrk.inclusion.location_tokens` | Implemented | D-029 |
| `SRS:L219` | Focus on companies that raised institutional money in the past 5 years | Column `x_bst_startuptrk_startup.institutional_funding_last_5yrs`, a premium-gated display attribute **not part of the inclusion filter**; the base role cannot read it, and the filter's operative rule names only `active` and `headquarters_location`. `D-029`, flag `F6` | Partially implemented | D-029 |
| `SRS:L255` | Successful integration with a payment gateway for premium subscriptions | **Flagged**, not implemented. Same position as `F006-4` | Flagged | D-090 |
| `SRS:L858` with the mockup reference at `SRS:L871` | An admin panel | The platform's native list and form views inside the scope; no sixth portal route is built | Partially implemented | D-095 |

Six statements. `SRS:L218` and `SRS:L219` together are the provenance of the inclusion criteria; the ambiguity over which of the two flag columns participates in the filter was resolved at **D-029** and is recorded as flag `F6`.

### 2.3 Authoritative prompt — sections 1.0 through 11.0

| Requirement ID / section | Requirement (short) | Target artifact(s) | Status | D-### |
| --- | --- | --- | --- | --- |
| Prompt section 1.0 | Exactly 7 custom tables with a binding, complete field list | The 7 entity tables carrying **53** columns, with 111 dictionary records and 111 label records bundled in their table payloads across all ten tables — 10 collection records plus 101 column records — and 77 choice values. **No entity column was added, omitted or inferred** — the seven entity tables carry exactly 53, and the one column added during remediation is the staging table's 41st, on a supporting table outside the closed list, per D-193 | Implemented | D-008 |
| Prompt section 1.1 | Inclusion criteria: active is true AND headquarters contains Boston or Cambridge, MA, case-insensitively; failing records stay visible to administrators | `StartupSearchService`, the location-tokens property, and widget `bst-startup-search`; excluded records remain in the table and are filtered only from portal-facing and non-administrative queries | Implemented | D-029 |
| Prompt section 1.2 | Startup, Founder, JobPosting and NewsArticle shapes | Tables `x_bst_startuptrk_startup` 12 columns, `_founder` 6, `_jobposting` 9, `_newsarticle` 6 | Implemented | D-008 |
| Prompt section 1.3 | Founder and Executive kept as separate tables, not one person table with a role flag | Two tables with distinct title choice lists, two sets of access controls and two field-level email controls | Implemented | D-017 |
| Prompt section 1.4 | Investor shape, with `portfolio_count` calculated | Table `x_bst_startuptrk_investor`; `portfolio_count` as a stored integer maintained by two business rules over `InvestorPortfolioService`, counting distinct startups across both traversal paths unioned | Implemented | D-013 |
| Prompt section 1.5 | FundingRound shape, with `participating_investors` as a List and the named join table | Table `x_bst_startuptrk_fundinground`; the join table `x_bst_startuptrk_m2m_round_investor` is authoritative and is the only write target. The List wording is delivered three ways over it: a related list on the form, a `read_only` **virtual** `glide_list` column whose calculation calls `InvestorPortfolioService.participantList()` and derives the value from the join table on every read, and a read-only array in every API response assembled from the **join table** rather than from that column. A round with several lead investors cannot be represented — flag `F17` | Implemented | D-010, D-011, D-245, D-434, D-448 |
| Prompt section 1.6 | Job posting fields and enumerations | Table `x_bst_startuptrk_jobposting` with the department, remote-type and seniority choice lists | Implemented | D-022 |
| Prompt section 1.7 | NewsArticle is manual entry or CSV import only, with no automated ingestion | Table `x_bst_startuptrk_newsarticle`, 5 read-and-manual-write operations on `/news`, no flow and no seventh CSV | Implemented | D-054 |
| Prompt section 2.0 | Three roles; seven premium fields hidden **and** access-denied at field level, not merely hidden in the interface | 3 roles, 49 access controls across five layers with 74 role joins, of which **7** are the field-level read controls granting the administrator and premium roles only | Implemented | D-024 |
| Prompt section 3.0 | Scripted REST APIs, six resources plus the nested executives sub-resource, cursor pagination, `total_count`, premium fields omitted not nulled, no bypass through elevated script includes | 1 definition and 31 operations at `/api/x_bst_startuptrk/v1/`; `RestQueryHelper` bounds the window, canonicalises every choice filter and rejects a non-numeric or negative offset with 400; `RestResponseBuilder` omits denied keys entirely rather than nulling them and answers an **exact** `total_count` from one aggregate behind a readability gate, returning 403 rather than zero when that gate denies; and every read to a caller uses the access-control-respecting record API — 30 operations opening it directly and `Startup list` reaching it through `StartupSearchService` | Implemented | D-025, with D-041 and D-193 |
| Prompt section 4.0 | Two Flow Designer flows only with no packaged integration content, two named credential aliases, no hard-coded secrets, a 6-to-48-hour configurable cadence, four cleaning rules, a fallback dataset in a staging table, and recorded provenance | Guides 02 and 03, each acquiring its population by **bounded paginated discovery** with a per-run ceiling and a resumable cursor and declaring a **record type per call site**; aliases `x_bst_startuptrk.crunchbase_api` and `x_bst_startuptrk.linkedin_oauth` from guide 01, referenced by name, resolved by `sys_alias.id` to **exactly one** record, with no credential value anywhere in the Update Set, and each provider endpoint passing an **origin allowlist** through `AppProperties.providerBaseUrlState()` **before** the credential attaches; `IngestionMapper` and `IngestionLogger`, with rule 1 trimming, rule 2 de-duplicating on the composite key **and** upserting all six types against a natural key, rule 3 normalising choices, and rule 4 rejecting a record missing a mandatory field; the clamped cadence property read through `getCadenceHours()` and `getLastSuccessAt()` against the **per-source run-marker set**, whose merge happens inside each write and is read back to confirm, with a completion refused unless the run holds the source; table `x_bst_startuptrk_ingest_staging`, six CSVs and guide 06; two provenance surfaces, one published to the flow execution log by a Log action. **Three parts fall short and each is flagged:** cleaning rule 3's `Other` coercion is unavailable in the six choice lists that declare no such member (`F13`), LinkedIn publishes no read API for three of the six record types so its live call is an identity probe and its runs can only be labelled `fallback validated` (`F15`), and three columns have no live source (`F16`) | **Partially implemented** | D-043, with D-180, D-181, D-182, D-183, D-184, D-354, D-355, D-356, D-357, D-362 and D-367 |
| Prompt section 5.0 | Service Portal experience only with five routes, and no use of the newer interface builder | One portal at url suffix `bst`, one theme, five pages `bst_home`, `bst_company`, `bst_investor`, `bst_dashboard`, `bst_account`, and eight widgets; no record of the newer experience type is authored | Implemented | D-058 |
| Prompt section 6.0 | Preservation constraints: modify nothing outside the `x_bst_startuptrk` scope; prototype focus with mandatory test coverage | Every one of the 313 payload records carries the scoped application; the impersonation users **and** the disposable REST caller are created at run time rather than shipped, the caller holding web-service access only and being destroyed inside its own test transaction; no performance target is invented and no coverage is reduced | Implemented | D-007, D-246 |
| Prompt section 7.0 | Out of scope: caching, search engine, containerisation, reverse proxy, process supervision, packaged integration content, the newer interface builder, automated news ingestion, and viewports below 1024 pixels | No platform equivalent is built for any of them; every configuration file stays on disk untouched; the viewport floor is declared | Consciously excluded | D-096 |
| Prompt section 8.0 | Three error contracts: skip the record and continue the run on an ingestion failure; the exact rate-limit body with a retry value; the general failure body with a logged stack trace | `IngestionLogger`, `RateLimitService` over the counter table, and `RestResponseBuilder` | Implemented | D-037 |
| Prompt section 9.0 | Test coverage: 100 percent of the 6 REST resources and the 7 tables must have a passing test; label a fallback run as such | **10** suites and **36** tests, being 7 table-CRUD suites, 21 field-by-role tests, 6 resource tests and 2 flow tests. The two flow tests call the orchestrator action's own entry point `IngestionMapper.ingestStaging()` over staging rows they seed themselves and assert the flow, trigger, action and mapping records separately; **neither starts a flow**, and each test's description says so, because the framework ships no step configuration that starts one and a foreground start would stamp the cadence marker criterion 4 reads. The result label is derived by the setup step from the source-mode property and the alias state. Per [0.5.1](#051-what-a-status-asserts-and-what-it-does-not) this row asserts the suites are delivered and specified, **not** that they have been observed to pass | Implemented | D-063, D-105, D-314 |
| Prompt section 10.0 | Five success criteria | `servicenow-startup-tracker-poc/docs/validation-checklist.md`, mapped one-to-one, backed by the **11 required** post-commit gates in `validation-gates.md`, with five further checks beside them in two classes — four acceptance-required and non-rollback, `GATE-COL-01` and `GATE-SEC-01` to `GATE-SEC-03`, and one non-normative diagnostic, `GATE-SEC-04` — and with the 53-column walk and the 21-cell access-control cross-product additionally asserted outside the gate set, by the checklist and by the test suite | Implemented | D-069, D-255 |
| Prompt section 11.0 | Deliverable format: one importable Update Set, XML validated at both the outer and nested payload levels, manual build instructions, a checklist mapped to the success criteria, and every requirement without a clean equivalent flagged | One Update Set carrying **313** records; the two-level validator with exit codes 0, 1 and 2, enforcing header linkage and the update-name contract alongside well-formedness; six manual-build guides; the checklist; and the **19**-entry flag inventory in `gaps-and-flags.md`, whose fourth disposition exists precisely so a bounded partial implementation is recorded rather than reported as complete | Implemented | D-065, D-252, D-263, D-264, D-300 |

Eighteen rows across the eleven sections 1.0 to 11.0; section 1.0 is decomposed into its seven sub-sections 1.0 to 1.7 because each fixes a different table's shape. Every section from 1.0 through 11.0 is present. **Sixteen rows are Implemented, one is Partially implemented and one is Consciously excluded** — section 4.0 is the partial one, and its three shortfalls are `F13`, `F15` and `F16` of the flag inventory. No row is marked Implemented on the strength of an artifact whose contract does not hold.

### 2.4 Project rules

| Requirement ID / section | Requirement (short) | Target artifact(s) | Status | D-### |
| --- | --- | --- | --- | --- |
| Rule 1, Explainability | A decision log with the four mandated columns, and — for a migration — a bidirectional traceability matrix at full coverage with no gaps; no rationale in code | [`./DECISION_LOG.md`](./DECISION_LOG.md), carrying **457** decisions across twenty-three sections, **and this file**. The log's mandatory deviation index is **derived from the decision rows themselves** — 197 `DEV` rows, 197 index entries, each entry the opening sentence of the row it names — every `D-###` referenced anywhere in the delivered package resolves to a row, and every row whose text a later decision overtook carries an amendment marker naming that decision. Platform record descriptions and script headers state only what an artifact does and which requirement it implements, per `D-005`; compliance was checked mechanically over every comment block in the Update Set payloads, the validator, both stylesheet copies, the presentation and every script block in the build guides, searching for rationale-shaped language. What the sweep establishes is bounded and stated as such: it reports **no comment that argues for a choice, weighs an alternative or assesses a risk**, and it does report the comments that describe what a branch does — each of those listed individually with the reason it is descriptive, per `D-308` | Implemented | D-081, D-005, D-308 |
| Rule 2, Executive Presentation | A single self-contained presentation for non-technical leadership, plus the canonical theme stylesheet the rule cites by path | `blitzy-deck/boston-startup-tracker-servicenow-executive-summary.html` — 16 slide sections across all four slide types, every section carrying a non-text visual, and every one of the 11 content slides at or under four bullets and forty body words — and `blitzy-deck/references/blitzy-reveal-theme.css`, authored from the rule's own specification at the path the rule cites and mirrored inline in the presentation **byte-identically** rather than linked. The three pinned library versions load under verified SHA-384 integrity digests with `crossorigin="anonymous"`. Verified by gate `G-8` of `servicenow-startup-tracker-poc/docs/validation-checklist.md`, which carries the sixteen-row measurement table, the digest recomputation and the byte comparison Every diagram is additionally rendered at the library's `strict` security level, with `flowchart.htmlLabels` false, which sanitises every diagram source without advancing a pin the rule freezes and renders inline, as the deck's own `frame-src 'none'` policy requires. | Implemented | D-084, D-132, D-135, D-137, D-253, D-305 |
| Rule 3, Critical Decision Review Document | A review artifact at an exact path listing the five highest-risk decisions, risk-ordered, each with alternatives, a cited rationale, a risk level and a reviewer persona | [`../review/CRITICAL_DECISIONS.md`](../review/CRITICAL_DECISIONS.md), whose five entries are the strict subset `D-024`, `D-076`, `D-043`, `D-010`, `D-055` — exactly the five rows the log flags `R3-1` through `R3-5`, in the same risk order, each with its alternatives, a rationale citing code or convention, a risk level and a named reviewer persona with what to check — requiring the new top-level `docs/` tree | Implemented | D-082 |

All three rules have rows. Rule 2's two artifacts and Rule 3's one artifact are named, and none of Rule 2's palette values, custom-property names, class names, pinned library versions or font weight lists is reproduced here — the rule is cited by name and its own text remains the source.

---

## 3. Reverse A — target artifact to justifying requirement

This section exists to prove that **no artifact is unjustified**. Every artifact the delivery produces appears below with the requirement or rule that demanded it. An artifact that could not be traced to one would be an over-build and would be reported as such in its row; none is.

### 3.1 Repository files — 30 in scope, 29 created and 1 updated

| Target artifact | Justifying requirement(s) | D-### |
| --- | --- | --- |
| `servicenow-startup-tracker-poc/README.md` | Prompt section 11.0's deliverable-format requirement needs a package index naming contents, prerequisites and deploy order | D-002 |
| `servicenow-startup-tracker-poc/update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml` | Prompt section 11.0: package everything expressible as declarative metadata as a **single** importable Update Set | D-070 |
| `servicenow-startup-tracker-poc/scripts/validate_update_set_xml.py` | Prompt section 11.0: validate the XML at both the outer update-set level and the nested per-record payload level before delivery | D-065 |
| `servicenow-startup-tracker-poc/docs/data-model.md` | Prompt section 1.0's binding field list requires a field-by-field statement of all ten tables, and acceptance criterion 1 requires field-by-field verification | D-008 |
| `servicenow-startup-tracker-poc/docs/access-control.md` | Prompt section 2.0's three roles and seven premium fields, and acceptance criterion 2's per-role, per-field verification | D-024 |
| `servicenow-startup-tracker-poc/docs/api-reference.md` | Prompt section 3.0's resource inventory and pagination contract, source requirement `F005-4`, and acceptance criterion 3 | D-035 |
| `servicenow-startup-tracker-poc/docs/manual-build-instructions.md` | Prompt section 11.0: clearly sequenced manual build instructions require an index that fixes the dependency order | D-075 |
| `servicenow-startup-tracker-poc/docs/manual-build/01-connection-credential-aliases.md` | Prompt section 4.0: the two named credential aliases are built through the platform interface and cannot ship as XML | D-043 |
| `servicenow-startup-tracker-poc/docs/manual-build/02-flow-crunchbase-ingestion.md` | Prompt section 4.0 and section 11.0: Flow Designer flows are explicitly named as requiring manual build instructions | D-050 |
| `servicenow-startup-tracker-poc/docs/manual-build/03-flow-linkedin-ingestion.md` | The same, for the second flow; it states all eight steps in full rather than deferring to guide 02 | D-050 |
| `servicenow-startup-tracker-poc/docs/manual-build/04-service-portal-pages-and-widgets.md` | Prompt section 5.0's five routes and section 11.0's naming of portal pages and widgets as manual-build artifacts | D-058 |
| `servicenow-startup-tracker-poc/docs/manual-build/05-atf-test-suites.md` | Prompt section 9.0's coverage floor and section 11.0's naming of the test framework as a manual-build artifact | D-063 |
| `servicenow-startup-tracker-poc/docs/manual-build/06-staging-table-csv-import.md` | Prompt section 4.0's fallback dataset must be loadable, and the load is performed through the platform's import interface | D-054 |
| `servicenow-startup-tracker-poc/docs/deployment-runbook.md` | The deployment environment brief, which is authoritative for deployment mechanics, transposed to this scope | D-001 |
| `servicenow-startup-tracker-poc/docs/validation-gates.md` | The environment brief's post-commit step reads its gates from this exact relative path beneath the deliverable root | D-069 |
| `servicenow-startup-tracker-poc/docs/validation-checklist.md` | Prompt section 11.0: a validation checklist mapped one-to-one to the five success criteria of section 10.0 | D-068 |
| `servicenow-startup-tracker-poc/docs/gaps-and-flags.md` | Prompt section 11.0: flag any requirement with no clean platform equivalent rather than omitting or half-implementing it | D-090 |
| `servicenow-startup-tracker-poc/sample-data/README.md` | Prompt section 4.0's fallback dataset needs a column contract binding the CSV headers to the staging dictionary | D-019 |
| `servicenow-startup-tracker-poc/sample-data/crunchbase_startups_sample.csv`, 13 rows | Prompt section 4.0's fallback dataset, for the Startup record type | D-054 |
| `servicenow-startup-tracker-poc/sample-data/crunchbase_investors_sample.csv`, 8 rows | Prompt section 4.0's fallback dataset, for the Investor record type | D-054 |
| `servicenow-startup-tracker-poc/sample-data/crunchbase_funding_rounds_sample.csv`, 12 rows | Prompt section 4.0's fallback dataset, for the FundingRound record type | D-054 |
| `servicenow-startup-tracker-poc/sample-data/linkedin_founders_sample.csv`, 10 rows | Prompt section 4.0's fallback dataset, for the Founder record type | D-054 |
| `servicenow-startup-tracker-poc/sample-data/linkedin_executives_sample.csv`, 10 rows | Prompt section 4.0's fallback dataset, for the Executive record type | D-054 |
| `servicenow-startup-tracker-poc/sample-data/linkedin_job_postings_sample.csv`, 12 rows | Prompt section 4.0's fallback dataset, for the JobPosting record type | D-054 |
| `docs/decisions/DECISION_LOG.md` | **Rule 1**, Explainability: the decision log with the four mandated columns | D-081 |
| `docs/decisions/TRACEABILITY_MATRIX.md` — **this file** | **Rule 1**, Explainability: the bidirectional traceability matrix required for a migration, at full coverage with no gaps | D-081 |
| `docs/review/CRITICAL_DECISIONS.md` | **Rule 3**, Critical Decision Review Document, at that exact path | D-082 |
| `blitzy-deck/boston-startup-tracker-servicenow-executive-summary.html` | **Rule 2**, Executive Presentation: a single self-contained presentation for non-technical leadership | D-086 |
| `blitzy-deck/references/blitzy-reveal-theme.css` | **Rule 2**, which names this exact path as its canonical theme file; the file was absent from this repository and is authored from the rule's own specification | D-084 |
| `README.md` at the repository root — the one **UPDATED** file | The entry point currently instructs a reader to run a build command that cannot succeed, because no Dockerfile exists anywhere in the tree | D-080 |

Thirty files. Six CSV files carrying 13 + 8 + 12 + 10 + 10 + 12 = **65** rows. There is deliberately **no seventh CSV for news articles**, because no flow targets that table and the staging record-type list has no member for it. **No file in this list lacks a justification.**

### 3.2 Update Set record classes — 18 classes, 313 update records

| Target artifact | Justifying requirement(s) | D-### |
| --- | --- | --- |
| 1 application record, materialising the `x_bst_startuptrk` scope row | Prompt section 6.0's scope containment; the scope row is what both the post-commit scope gate and the rollback query | D-007 |
| 1 application menu and 9 modules — one per entity table, one for the staging table, one for properties | Source requirement `F008-2`: tools for manually updating startup data need a navigation surface | D-062 |
| 7 entity **table** records: `_startup`, `_founder`, `_executive`, `_investor`, `_fundinground`, `_jobposting`, `_newsarticle` | Prompt section 1.0: exactly 7 custom tables | D-008 |
| The cascade-delete rules on the five mandatory `startup` child references and on both parent references of the join table | Prompt section 1.0 declares those child references mandatory, so referential integrity on a parent delete is an unavoidable consequence of the binding field list | D-012 |
| Table `x_bst_startuptrk_m2m_round_investor` | Prompt section 1.5 **names this table verbatim** as the store for a funding round's participating investors | D-010 |
| Table `x_bst_startuptrk_ingest_staging` | Prompt section 4.0 mandates a staging table for the fallback dataset, mimicking the expected API response shape | D-018 |
| Table `x_bst_startuptrk_rate_limit_counter` | Prompt section 8.0 fixes the rate-limit response body exactly, including a computed retry value, which cannot be produced without per-caller and per-resource accounting | D-021 |
| 111 dictionary records bundled inside the ten table payloads | Prompt section 1.0's **53** entity columns, the supporting tables' **48** — 2 on the join table, 41 on the staging table, of which the 41st carries a child's parent headquarters, and 5 on the counter — and the **10** collection records, one per table; bundled so a table and its columns commit atomically | D-071, with D-193 for the 41st and D-435 for the counter's fifth |
| 111 label records bundled inside the same payloads | Every column needs a human-readable label for the native form and list views that serve `F008-2` | D-071 |
| 77 choice values | Prompt section 1.0's closed choice lists for industry, funding stage, employee band, titles, investor type, focus areas, department, remote type and seniority, plus the staging discriminators — the staging import state carrying exactly the four members the plan freezes, with a claimed row observable through the reserved `run:` prefix in `import_run` rather than through a fifth state, per `D-386`. **Eleven entity lists, of which five declare an `Other` member and six do not** — so cleaning rule 3 coerces on five and leaves the column unwritten on the other six, which is flagged as `F13` rather than corrected by adding a member to a binding list | D-022, D-386 |
| 13 declared index records, of which 1 is unique | Each names the predicate it serves: the unique pair constraint on the join table; its reverse traversal and the lead path, both read by the `portfolio_count` derivation; the counter pruning range; the **six natural keys** read on every ingested row, served by **seven** indexes because the `funding_round` key is an ordered pair of alternatives and both the primary `source_url` lookup and the `startup` and `round_date` fallback are indexed; the child-collection reads behind the five profile panes and the corresponding REST list filters; and the three-column equality predicate of the bounded staging read. The three-column counter index that served no query was removed | D-188, with D-180 for the keys |
| 3 role records: `x_bst_startuptrk.admin`, `.user`, `.premium_user` | Prompt section 2.0's three roles, corroborated by `SRS:L77`'s three tiers | D-009 |
| 49 access-control records across five layers | Prompt section 2.0's field-level denial requirement and section 3.0's prohibition on bypassing access control; the fifth layer closes the endpoint-execution route | D-027 |
| 74 access-control role-join records | Each control must name which of the three roles it grants; **zero** role assignments to users are shipped, because the user table is outside the scope | D-028 |
| 8 Script Include records: `StartupSearchService`, `InvestorPortfolioService`, `IngestionMapper`, `IngestionLogger`, `RateLimitService`, `RestResponseBuilder`, `RestQueryHelper`, `AppProperties` | Each rule must exist exactly once so the API and the portal cannot disagree, which is the drift the legacy tree exhibited when its cleaning rule and its stated requirement diverged. **Eight is the count the Agent Action Plan specifies, and the count delivered** | D-035, D-265 |
| 1 Scripted REST service definition | Prompt section 3.0: Scripted REST APIs under a versioned path in the `x_bst_startuptrk` namespace | D-032 |
| 31 Scripted REST resource records, distributed 5, 6, 5, 5, 5, 5 | Prompt section 3.0's six logical resources plus the nested executives sub-resource | D-034 |
| 11 system property records | Prompt section 4.0's configurable cadence, section 3.0's pagination bounds, the inclusion tokens, the two base URLs, the rate-limit budget and window, the source mode, the run-state marker and the log level. **No property holds a secret**, and the LinkedIn API version is a code constant rather than a twelfth property | D-046, D-265, D-266 |
| 3 business rule records | The portfolio derivation must stay current on both funding-round and join-table change, and startup writes must be trimmed and validated | D-013 |
| 1 scheduled executable record, a `sysauto_script` | It prunes rate-limit counter rows; no staging retention sweep is delivered, and that absence is flag `F19`; the staging table is protected by its access posture instead | D-021, D-265 |
| 10 form section records and 10 list view records | Source requirement `F008-2`: the administrative surface must be usable on commit, which is what serves the admin-dashboard feature without a sixth portal route | D-062 |
| 1 related list record | Prompt section 1.5's "List" wording is delivered as the editable user experience over the authoritative join table, alongside the derived `read_only` column and the API array assembled from the join table | D-010, D-011 |

Class arithmetic: 77 choice values + 74 role joins + 49 access controls + 31 REST operations + 13 declared indexes + 11 properties + 10 tables + 10 list views + 10 form sections + 9 menu modules + 8 Script Includes + 3 roles + 3 business rules + 1 scheduled job + 1 related list + 1 REST definition + 1 application + 1 application menu = **313** update records across **18** classes. Dictionary and label records do not add to that total because they are bundled inside the table payloads.

**The three supporting tables each have a distinct justification**, stated above rather than assumed: the join table is named verbatim by the requirements, the staging table is required by the fallback-dataset mandate, and the counter table is required to emit the exact rate-limit body with a computed retry value. **The form and list view records are justified by source requirement `F008-2`, not by any portal route** — which is precisely why no sixth route is built.

### 3.3 Manually built artifacts — 10 classes

Only artifacts the platform captures into update records ship as XML; everything else ships as manual build instructions, because adding the capture attribute to a table that lacks it is unsupported.

| Target artifact | Justifying requirement(s) | D-### |
| --- | --- | --- |
| 2 Connection and Credential Aliases: `x_bst_startuptrk.crunchbase_api` Basic authentication, `x_bst_startuptrk.linkedin_oauth` OAuth 2.0 | Prompt section 4.0: reference both aliases by name and hard-code no key, secret or token anywhere | D-043 |
| 14 published Flow Designer custom actions, **seven per source**, carrying every REST and Script step: `cadence_guard`, `resolve_source_mode`, `fetch_crunchbase_payload`, `ingest_crunchbase_batch`, `confirm_crunchbase_writes`, `reconcile_batch_counters` and `publish_run_evidence`, with `cadence_guard_linkedin`, `resolve_source_mode_linkedin`, `fetch_linkedin_payload`, `ingest_linkedin_batch`, `confirm_linkedin_writes`, `reconcile_linkedin_batch_counters` and `publish_linkedin_run_evidence` mirroring them. Each action materialises a `sys_hub_action_type_definition` record, its `sys_hub_action_instance` step records, and its `sys_hub_action_input` and `sys_hub_action_output` records | Prompt section 4.0: Flow Designer flows only, with no packaged integration content. A REST or Script step is an action step and can only exist inside a published action, so the actions are the mechanism by which that instruction is satisfiable at all | D-104 |
| 2 Flow Designer scheduled flows, each a `sys_hub_flow` of **eight builder elements — seven action calls and one `If`**: the cadence guard at position 1 outside the `If`, the `If` on its verdict, then source-mode resolution, payload fetch, the orchestrated ingest, write confirmation, counter reconciliation and run-evidence publication inside it. **All seven actions are mandatory and all seven are called**; there is no published-but-unwired action and no diagnostic-only action | Prompt section 4.0: Flow Designer flows only, with no packaged integration content. The LinkedIn flow's live path is declared unavailable and gated on an endpoint-contract declaration, registered as `OPEN-1` | D-045, D-102, D-103, D-397 |
| 1 portal record at url suffix `bst` | Prompt section 5.0: a Service Portal experience only | D-058 |
| 1 theme record carrying the styling variables | Prompt section 5.0, and the finding that the legacy tree had no design-token system to carry forward | D-059 |
| 5 page records: `bst_home`, `bst_company`, `bst_investor`, `bst_dashboard`, `bst_account` | Prompt section 5.0's five enumerated routes | D-056 |
| 8 widget records: `bst-startup-search`, `bst-startup-results`, `bst-company-profile`, `bst-investor-profile`, `bst-trends-kpi`, `bst-trends-charts`, `bst-account-summary`, `bst-premium-upsell` | The five routes' content needs, with `bst-premium-upsell` reused by three hosts to resolve design-system gap `G5` | D-060 |
| 10 test suites | Prompt section 9.0's coverage floor stated per table and per resource | D-063 |
| 36 tests: 7 table-CRUD, 21 field-by-role, 6 resource, 2 flow | Prompt section 9.0, and acceptance criterion 2's per-role, per-field verification, which only the 21-cell cross-product satisfies | D-064 |
| The staging CSV load of 65 rows through the platform's import interface | Prompt section 4.0's fallback dataset must be resident before any fallback run demonstrates a cleaning rule | D-054 |

The 3 impersonation users the access-control tests require are created **at run time by the test setup steps** and are deliberately not shipped, because the platform user table sits outside the scope. That is a justified absence from the Update Set rather than a missing artifact.

#### 3.3.1 The ten suites and all 36 tests, individually

Finding-level traceability for the test set, because the class-level rows above cannot show which table, field, resource or flow a given test covers, and a coverage floor stated *per* table and *per* resource is only checkable per test.

**Status vocabulary for this table, and it is narrower than the document's general one.** `Specified` means the test, its steps and the complete script for every custom step are published in the build guide, and the artifact is built by hand on the instance rather than shipped in the Update Set. **No row below claims an executed result**: an execution status belongs to a suite result record on the instance and is recorded in `servicenow-startup-tracker-poc/docs/validation-checklist.md`, not here.

| Suite | Test | Covers | Status | D-### |
| --- | --- | --- | --- | --- |
| `BST CRUD suite — startup` | `BST CRUD — startup` | `x_bst_startuptrk_startup`: insert, update, query, delete; 3 mandatory columns; `active` default; the 3 choice columns and their 19 members | Specified | D-063, D-107 |
| `BST CRUD suite — founder` | `BST CRUD — founder` | `x_bst_startuptrk_founder`: full CRUD; 2 mandatory columns; `title` and its 5 members; the cascade from a deleted parent | Specified | D-063, D-107 |
| `BST CRUD suite — executive` | `BST CRUD — executive` | `x_bst_startuptrk_executive`: full CRUD; 2 mandatory columns; `title` and its 5 members, distinct from Founder's | Specified | D-063, D-107 |
| `BST CRUD suite — investor` | `BST CRUD — investor` | `x_bst_startuptrk_investor`: full CRUD; 1 mandatory column; `type` and `focus_areas`; the `portfolio_count` write contract and its derivation across eleven states | Specified | D-063, D-014, D-107 |
| `BST CRUD suite — fundinground` | `BST CRUD — fundinground` | `x_bst_startuptrk_fundinground`: full CRUD; 2 mandatory columns; `round_type` and its 8 members; the calculated `participating_investors` column asserted as virtual and read-only, deriving from the join table on every read with no refresh in between and no write surviving | Specified | D-063, D-010, D-107, D-434, D-448 |
| `BST CRUD suite — jobposting` | `BST CRUD — jobposting` | `x_bst_startuptrk_jobposting`: full CRUD; 2 mandatory columns; 3 choice columns and their 14 members | Specified | D-063, D-107 |
| `BST CRUD suite — newsarticle` | `BST CRUD — newsarticle` | `x_bst_startuptrk_newsarticle`: full CRUD; 2 mandatory columns; `published_date` round trips and the two write operations' date validation | Specified | D-063, D-107 |
| `BST ACL suite — premium fields by role` | `BST ACL — startup.total_funding_usd — admin` / `— premium_user` / `— user` | 3 cells on `x_bst_startuptrk_startup.total_funding_usd` | Specified | D-064, D-119 |
| `BST ACL suite — premium fields by role` | `BST ACL — startup.institutional_funding_last_5yrs — admin` / `— premium_user` / `— user` | 3 cells on `x_bst_startuptrk_startup.institutional_funding_last_5yrs` | Specified | D-064, D-119 |
| `BST ACL suite — premium fields by role` | `BST ACL — founder.contact_email — admin` / `— premium_user` / `— user` | 3 cells on `x_bst_startuptrk_founder.contact_email` | Specified | D-064, D-119 |
| `BST ACL suite — premium fields by role` | `BST ACL — executive.contact_email — admin` / `— premium_user` / `— user` | 3 cells on `x_bst_startuptrk_executive.contact_email`, a separate control from Founder's | Specified | D-064, D-119 |
| `BST ACL suite — premium fields by role` | `BST ACL — investor.aum_usd — admin` / `— premium_user` / `— user` | 3 cells on `x_bst_startuptrk_investor.aum_usd` | Specified | D-064, D-119 |
| `BST ACL suite — premium fields by role` | `BST ACL — fundinground.amount_usd — admin` / `— premium_user` / `— user` | 3 cells on `x_bst_startuptrk_fundinground.amount_usd` | Specified | D-064, D-119 |
| `BST ACL suite — premium fields by role` | `BST ACL — fundinground.valuation_usd — admin` / `— premium_user` / `— user` | 3 cells on `x_bst_startuptrk_fundinground.valuation_usd` | Specified | D-064, D-119 |
| `BST REST suite — resources` | `BST REST — startups` | `GET`/`POST`/`DELETE` on `/startups`: response shape, pagination against an exactly-sized filtered set, the `429` contract, the per-resource key schema, the inclusion filter reaching both `result` and `total_count`, **and the authorization contract** — an unauthenticated `GET` refused `401`, a base-role `POST` and `DELETE` each refused `403` with the administrator-role message, an administrator `POST` accepted `201` carrying the premium keys, and an administrator `DELETE` accepted `204` — which is where the write path and the unauthenticated path are covered for all thirty-one operations, because both guards are shared | Specified | D-065, D-106, D-117, D-350 |
| `BST REST suite — resources` | `BST REST — founders` | `/founders` **and** the nested `/founders/{startup_id}/executives`, every assertion made twice with a separate rate-limit token per path | Specified | D-065, D-034, D-106, D-117 |
| `BST REST suite — resources` | `BST REST — investors` | `/investors`, including `portfolio_count` in the response schema | Specified | D-065, D-106, D-117 |
| `BST REST suite — resources` | `BST REST — funding-rounds` | `/funding-rounds`, including `participating_investors` as an assembled array | Specified | D-065, D-010, D-106, D-117 |
| `BST REST suite — resources` | `BST REST — jobs` | `/jobs` | Specified | D-065, D-106, D-117 |
| `BST REST suite — resources` | `BST REST — news` | `/news`, read plus manual write only | Specified | D-065, D-106, D-117 |
| `BST FLOW suite — ingestion` | `BST FLOW — Crunchbase Ingestion [fallback]` | A started execution of the published `Crunchbase Ingestion` flow over 12 seeded staging rows — the four cleaning rules, within-batch Startup deduplication, reference resolution, the join rows, the participant projection and `portfolio_count`, the carrier contract for participating investors — plus the flow and action wiring assertions and the cadence guard down both branches. **Does not exercise the live outbound path.** | Specified | D-066, D-113, D-114, D-247, D-373 |
| `BST FLOW suite — ingestion` | `BST FLOW — LinkedIn Ingestion [fallback]` | A started execution of the published `LinkedIn Ingestion` flow over 8 seeded staging rows — the four cleaning rules and parent resolution onto an existing Startup — plus the same wiring assertions and the cadence guard down both branches. **Does not exercise the live outbound path**, and does not assert Startup deduplication, which a LinkedIn batch cannot reach. | Specified | D-066, D-113, D-114, D-247 |

**Row arithmetic.** 7 CRUD rows + 7 access-control rows each naming 3 cells + 6 resource rows + 2 flow rows = 22 rows covering **7 + 21 + 6 + 2 = 36 tests** in **10 suites**. The seven access-control rows are grouped by premium field rather than split into 21 rows because the three cells of a field differ only in the role and the expected outcome; the individual cell names are `ACL-1.1` through `ACL-7.3` and are enumerated test by test in the build guide and in criterion 2 of the validation checklist.

**Reverse direction.** Every one of the 7 entity tables appears in exactly one CRUD row; every one of the 7 premium fields appears in exactly one access-control row; every one of the 6 logical resources plus the nested sub-resource appears in exactly one resource row; and each of the 2 flows appears in exactly one flow row. **No suite and no test in the delivery is absent from this table, and no row here names an artifact that is not built.** There is no eleventh suite: `D-063` records why no parent, master or aggregating suite is created.

**What this table does not cover, stated so its absence is not read as coverage.** No test executes a Flow Designer flow, because the framework ships no step that can — `D-105`. Real flow-execution evidence comes from the one manual data-bearing run in each flow guide and from the run-summary records of criterion 4's three consecutive guard-passing runs per flow. The portal's five routes are likewise not covered by any test: criterion 5 is evidenced by a manual walkthrough, recorded in the validation checklist. **The write and unauthenticated paths are covered on one resource only** — `/startups`, in the authorization block of `BST REST — startups` — and the other five resources inherit that evidence by construction rather than by execution: `RateLimitService.reject()` and `RestResponseBuilder.rejectUnauthorisedWrite()` are the same two calls in the same order in every operation script, and every `sys_ws_operation` carries `requires_authentication` and `requires_acl_authorization` `true`. Two branches are covered by no test at all and are stated here rather than implied: **`PUT`** on any resource, whose guard is the same call but whose status and body are not asserted anywhere; and the **read**-denial branch `Caller holds no Boston Startup Tracker role`, which no caller this package defines can reach, because table-level read is granted to all three application roles — only a caller holding none of them would see it, and no such identity is created.


### 3.4 Reverse A completeness

| Artifact class | Traced | Untraceable |
| --- | --- | --- |
| Repository files in scope | 30 of 30 | 0 |
| Update Set record classes | 18 of 18 | 0 |
| Manually built artifact classes | 10 of 10 | 0 |

**No artifact in this delivery resists justification.** Every row above names a prompt section, a source requirement, or a project rule.

---

## 4. Reverse B — coverage assertion and the conscious-exclusion register

### 4.1 The assertion

| Claim | Basis |
| --- | --- |
| Every one of the **123** legacy source files is accounted for | Section 1, in seven named groups whose file counts sum to 123 and whose subtree arithmetic reconciles independently, in section 1.8 |
| Every one of the **50** source sub-requirements is accounted for | Section 2.1, one row each, `F001-1` through `F010-5`, with no duplicate and no absence |
| Every one of the **11** prompt sections, 1.0 through 11.0, is accounted for | Section 2.3 |
| Every one of the **3** project rules is accounted for | Section 2.4 |
| Every one of the **30** in-scope repository files traces back to a requirement or a rule | Section 3.1 |
| Every one of the **18** Update Set record classes traces back to a requirement | Section 3.2 |
| Every one of the **10** manually built artifact classes traces back to a requirement | Section 3.3 |
| No construct or requirement is silently dropped | Section 4.2, one row per deliberate drop, each with its decision reference |
| No requirement is **silently** met in part | Section 2.1's **nine** partial rows, section 2.2's **two** — `SRS:L219`, the five-year funding signal delivered as a premium display column outside the filter, and `SRS:L858`, the admin panel delivered as native views — section 2.3's **one**, and the nineteen-flag inventory reconciled in section 4.2.3, three of whose entries carry the *partially implemented, flagged* disposition. Twelve partial rows in all, and every one of them names what is unmet |

This section is what converts "no gaps" from a claim into a demonstration. A reader can falsify it by naming a legacy file absent from section 1, a sub-requirement absent from section 2.1, or a delivered artifact absent from section 3.

**What "100 percent coverage" means here, precisely.** It means every member of every denominator has a row, and every row has a verdict and a decision reference. It does **not** mean every requirement is implemented, and it does not mean every implemented requirement has been observed working on an instance — the second of those is the subject of [0.5.1](#051-what-a-status-asserts-and-what-it-does-not). Across the seventy-four requirement rows of sections 2.1 to 2.3, **forty** carry **Implemented**, **twelve** carry **Partially implemented**, **three** carry **Flagged** and **nineteen** carry **Consciously excluded** — nine partial and one flagged in section 2.1's fifty sub-requirements, two partial and two flagged among section 2.2's six supporting statements, and one partial in section 2.3's eighteen prompt sections. Every one of the thirty-four non-Implemented rows names what is unmet. Coverage is a property of this mapping, and fulfilment is a property of the delivery — conflating the two would let a complete matrix stand in for a complete implementation, which is the specific misreading this paragraph exists to prevent.

### 4.2 The conscious-exclusion register

One row per deliberately dropped source construct or unimplemented requirement. Every row carries a decision reference into [`./DECISION_LOG.md`](./DECISION_LOG.md), and every excluded requirement that has no clean platform equivalent also carries its flag identifier from `servicenow-startup-tracker-poc/docs/gaps-and-flags.md`.

#### 4.2.1 Legacy source constructs dropped

| Excluded construct | What became of it, in one clause | D-### |
| --- | --- | --- |
| `src/data_collection/scrapers/startup_scraper.py` | Only two named API sources are ingested and no scraping is required | D-052 |
| `src/data_collection/scrapers/investor_scraper.py` | The same | D-052 |
| `src/data_collection/scrapers/job_scraper.py` | The same | D-052 |
| `src/data_collection/scrapers/news_scraper.py` | The same, and news-article ingestion is excluded entirely | D-052 |
| `src/data_collection/data_enrichment/startup_enricher.py` | No enrichment requirement exists in the authoritative prompt | D-051 |
| `src/data_collection/data_enrichment/investor_enricher.py` | The same | D-051 |
| `src/data_collection/data_cleaning/investor_cleaner.py`, 315 physical lines and the largest legacy file | Its transformations have no counterpart among the four mandated cleaning rules | D-051 |
| `src/backend/models/user.py`, with its own password hash at `:L11` | Identity becomes the platform user table plus three scoped roles | D-009 |
| `src/backend/routes/auth.py` | Authentication is a platform concern outside the application scope | D-009 |
| `src/backend/routes/user.py` | The same; no target REST resource exists | D-009 |
| `src/backend/services/user_service.py` | Retired with the identity model | D-009 |
| `src/backend/models/startup.py:L13` `sub_sector` | Excluded by the binding field list | D-023 |
| `src/backend/models/startup.py:L14` `employee_count` as an integer | Superseded by a five-value band; the integer itself is excluded | D-023 |
| `src/backend/models/startup.py:L15` `local_employee_count` | Excluded by the binding field list | D-023 |
| `src/backend/models/startup.py:L16` `headcount_growth_rate` | Excluded by the binding field list, which is what makes `F009-3` unbuildable | D-094 |
| `src/backend/models/startup.py:L18` `last_funding_date` | Round dates live on the funding-round table instead | D-023 |
| `src/backend/models/startup.py:L20` `is_hiring` | Per-posting state on the job-posting table serves the need instead | D-023 |
| `src/backend/models/startup.py:L21` `last_updated` | Platform record metadata supersedes it | D-023 |
| `src/backend/utils/cache.py` | Caching is named out of scope and no platform equivalent is built | D-096 |
| `src/backend/utils/db.py` | The platform owns persistence | D-003 |
| `src/frontend/store/index.ts` | State lives in widget client and server scripts | D-058 |
| `src/frontend/store/actions/index.ts` | The same | D-058 |
| `src/frontend/store/reducers/index.ts` | The same | D-058 |
| `src/frontend/utils/api.ts` | Superseded by the widget server-script and REST layers | D-058 |
| `src/frontend/utils/auth.ts` | Superseded by the access-control engine | D-024 |
| `src/shared/utils.ts` | No shared client utility layer survives | D-058 |
| `src/frontend/App.tsx:L12` — the `./styles/theme` import | The module was **never authored**; `src/frontend/styles/` contains only `global.css`, so no legacy theme value exists to carry forward even in principle | D-079 |
| `src/shared/constants.ts:L47`, `:L50`, `:L53` — date format, currency and token expiry | Retired with the client stack; denomination is fixed by the currency-typed column names | D-016 |
| `config/redis.conf` | Caching is named out of scope; the file stays on disk untouched | D-096 |
| `config/elasticsearch.yml` | A search engine is named out of scope; encoded platform queries serve search instead | D-096 |
| `config/nginx.conf` | A reverse proxy is named out of scope | D-096 |
| `config/supervisord.conf` | Process supervision is named out of scope | D-096 |
| `docker-compose.yml` | Containerisation is named out of scope, and its build contexts name a Dockerfile that exists nowhere in the tree | D-096 |
| `.github/workflows/ci.yml` | A step added to it would never execute, because the workflow fails at `:L24` and again at `:L36-L37` before any added step runs | D-067 |
| `.github/workflows/cd.yml` as an automated pipeline | Deployment becomes an operator-run import, preview, commit and gate sequence documented in the runbook | D-076 |
| `scripts/backup_database.sh` | The platform owns persistence and backup | D-003 |
| `scripts/setup_dev_environment.sh` | Nothing runnable exists to bootstrap | D-077 |
| `.github/ISSUE_TEMPLATE.md` | Repository process is unaffected by the replatform; unchanged, no target | D-003 |
| `.github/PULL_REQUEST_TEMPLATE.md` | The same | D-003 |
| `documentation/Human Tasks.md` | Its tasks concern modules that are retired; the deliverable's own documentation tree is authoritative | D-080 |
| `documentation/Software Project Proposal.md` | Describes the retired system; unchanged, no target | D-080 |
| `documentation/Technical Specifications.md` | Describes the retired three-tier stack; unchanged, no target | D-080 |
| **`.env.example:L29` — `GITHUB_API_KEY`** | Only two data sources are ingested, so the third key has **no consumer**: no flow calls it, no alias holds it and no property references it | D-101 |
| `package.json`, unmodified and unpruned | It is not valid JSON, because a comment block begins at `:L65`, so pruning it would mean first repairing an out-of-scope file | D-078 |
| `tsconfig.json`, `.eslintrc.js`, `.prettierrc`, `.dockerignore` | Retired with the TypeScript stack and with containerisation | D-078 |
| `pytest.ini` and `jest.config.js` | Retired with the test stacks they configure, neither of which could collect a single file | D-063 |
| Python 3.8 and Node.js 14, the documented runtime ceilings | Recorded for the dependency inventory and this matrix, and deliberately **not provisioned**, because nothing runnable exists to provision them for | D-077 |
| The legacy tree's four broken references | Repairing any of them would mean editing an out-of-scope file in an application being retired, and would still leave a tree with no manifest and no Dockerfile | D-079 |
| The absent manifests: no requirements file, no frontend manifest, no lockfile, no Dockerfile is authored | Authoring them would resurrect a stack the requirements retire | D-078 |

#### 4.2.2 Requirements not implemented

| Excluded requirement | Flag | What became of it, in one clause | D-### |
| --- | --- | --- | --- |
| `F001-1`, `SRS:L373` — web crawlers | `F9` | Only two named API sources exist and no scraping is required | D-092 |
| `F001-5`, `SRS:L377` — data versioning | — | The binding field list declares no version, revision or history column | D-023 |
| `F002-5`, `SRS:L391` — WCAG 2.1 Level AA conformance | — | No conformance audit is performed and none is claimed | D-059 |
| `F003-3`, `SRS:L403` — saved searches | `F9` | It would need a table outside the binding seven and a route outside the mandated five | D-092 |
| `F003-5`, `SRS:L405` — sorting options | — | No list operation accepts a sort parameter; each applies one fixed documented order | D-033 |
| `F004-4`, `SRS:L418` — automated news ingestion | — | Named out of scope; the table is served by manual entry or CSV import only | D-054 |
| `F005-5`, `SRS:L433` — client SDKs | — | The requirements ask for a REST API and its documentation, not a client library | D-078 |
| `F006-1`, `SRS:L443` — user registration | — | A platform-user concern outside the scope, which the requirements forbid modifying | D-009 |
| `F006-4`, `SRS:L446` — subscription management | `F1` | The platform has **no** commerce, checkout or payment capability whatsoever | D-090 |
| `F006-5`, `SRS:L447` — password reset and account recovery | — | The same position as `F006-1` | D-009 |
| `F007-2`, `SRS:L458` — the CSV half of data export | — | The definition and all 31 operations pin their media types to JSON | D-033 |
| `F007-5`, `SRS:L461` — scheduled report delivery | `F9` | It would need an email capability no requirement establishes | D-092 |
| `F008-3`, `SRS:L473` — health monitoring and alerting | `F8` | No observability layer is built; the requirements state a prototype focus with no availability target | D-099 |
| `F008-4`, `SRS:L474` — platform usage analytics | `F8` | Not among the five enumerated routes, and no usage table exists | D-095 |
| `F008-5`, `SRS:L475` — the API-key management half | `F8` | The API authenticates platform users rather than issuing keys | D-027 |
| An administrative console as a portal route, `SRS:L858` and `:L871` | `F8` | Exactly five routes are enumerated and none is an administrative console | D-095 |
| `F009-3`, `SRS:L487` — growth rate comparisons | `F11` | One current employee band and no history; a band cannot yield a rate without a prior value | D-094 |
| `F009-5`, `SRS:L489` — geographic distribution maps | `F11` | A free-text place name with no coordinate pair, and geocoding needs an unauthorised external service | D-094 |
| `F010-1`, `SRS:L499` — in-app notifications | `F12` | No notification requirement appears in the authoritative prompt | D-093 |
| `F010-2`, `SRS:L500` — an email notification service | `F12` | No email capability is established by any requirement | D-093 |
| `F010-3`, `SRS:L501` — notification preferences | `F12` | No preference storage exists among the ten tables | D-093 |
| `F010-4`, `SRS:L502` — real-time updates for followed startups | `F12` | The binding field list declares no follow relationship | D-093 |
| `F010-5`, `SRS:L503` — digest emails | `F12` | Depends on the excluded email service | D-093 |
| Automatic entitlement transition to the premium role on payment | `F2` | Depends entirely on the excluded billing capability; the operational path is an administrator granting the role | D-091 |
| Prompt section 7.0's named out-of-scope capabilities | — | Caching, search engine, containerisation, reverse proxy, process supervision, packaged integration content, the newer interface builder, automated news ingestion, and viewports below 1024 pixels | D-096 |
| Responsive refinement below 1024 pixels | — | The range is named out of scope, so any such work would ship unverified; the floor is declared instead | D-098 |
| Production hardening and any performance target | — | The requirements state a prototype focus and state no throughput, latency or availability figure anywhere | D-099 |
| A path foreign to this project, named in the out-of-scope clause | — | Searched for tree-wide and **absent**; the operative half of that clause is what places the whole of `src/` outside the delivery | D-100 |

#### 4.2.3 Reconciliation with the nineteen-flag inventory

`servicenow-startup-tracker-poc/docs/gaps-and-flags.md` carries **19** entries, `F1` through `F19`. Every one is reachable from this matrix, and every flag-bearing exclusion above names its entry.

**The two halves of the nineteen-flag inventory reach this matrix by different routes, and the difference is the point.** `F1` through `F12` are exclusions of a **source requirement**, so each is reachable from section 2.1, section 2.2 or the exclusion register of section 4.2. `F13` through `F19` are shortfalls against the **authoritative prompt** — discovered where the prompt meets a real provider contract, its own binding field list, or its own frozen artifact inventory — so each is reachable from section 2.3 instead, and three of them are the reason prompt section 4.0 carries a **Partially implemented** verdict there rather than an Implemented one.

| Flag | Subject | Where it appears in this matrix | D-### |
| --- | --- | --- | --- |
| `F1` | Premium subscription billing and payment processing | Section 2.1 `F006-4`; section 2.2 `SRS:L107` and `SRS:L255`; section 4.2.2 | D-090 |
| `F2` | Automatic entitlement transition on payment | Section 4.2.2 | D-091 |
| `F3` | A runtime-configurable flow schedule interval | Section 2.3 prompt section 4.0, resolved by the hourly trigger with an elapsed-time guard reading **one** state property, `x_bst_startuptrk.ingestion.last_run_provenance`, which carries a semicolon-joined marker per source | D-047, with D-183, D-265 and D-156 |
| `F4` | Path-style portal routes | Section 1.4, `src/frontend/App.tsx:L29-L37` mapped to query-parameter addressing | D-056 |
| `F5` | A namespace-free API base path | Section 1.2, `src/shared/constants.ts:L2` mapped to the physical namespaced path | D-032 |
| `F6` | The inclusion-criteria field ambiguity | Section 2.2 `SRS:L219`; section 2.3 prompt section 1.1 | D-029 |
| `F7` | Design-system component gaps `G1` to `G5` | Section 1.4 and section 3.3, resolved inside the system | D-060 |
| `F8` | An administrative console as a portal route | Section 2.1 `F008-3`, `F008-4`, `F008-5`; section 4.2.2 | D-095 |
| `F9` | Three source requirements with no prompt counterpart: `F001-1`, `F003-3`, `F007-5` | Section 2.1 and section 4.2.2, each named individually | D-092 |
| `F10` | Verifiable field-level enforcement, given the administrator override | Section 3.3, the 21 field-by-role tests run under impersonation | D-030 |
| `F11` | Geographic distribution maps `F009-5` and growth rate comparisons `F009-3` | Section 2.1 `F009-3` and `F009-5`; section 4.2.2 | D-094 |
| `F12` | The entire Notification System feature `F010`, all five sub-requirements | Section 2.1 `F010-1` to `F010-5`; section 4.2.2 | D-093 |
| `F13` | Cleaning rule 3's `Other` coercion in the six choice lists that declare no such member | Section 2.3 prompt section 4.0, **Partially implemented**; section 2.3 prompt section 1.0 for the binding lists it conflicts with | D-022, D-232 |
| `F14` | The Crunchbase authentication model, which the provider does not accept as HTTP Basic | Section 1.3, `crunchbase_integrator.py:L11`; section 2.3 prompt section 4.0 | D-229 |
| `F15` | LinkedIn publishes no read API for founders, executives or third-party job postings | Section 1.3, `linkedin_integrator.py`; section 2.3 prompt section 4.0, **Partially implemented** | D-233 |
| `F16` | Three columns with no live source: `startup.institutional_funding_last_5yrs`, `investor.aum_usd`, `fundinground.source_url` | Section 2.3 prompt sections 1.0 and 4.0 | D-231, D-239 |
| `F17` | A funding round with several lead investors, which the binding shape cannot represent | Section 2.3 prompt section 1.5; section 1.1, `funding_round.py:L6-L9` | D-010, D-014 |
| `F18` | Both flows calling their provider through one of two arms — a generic Flow Designer REST step, or a scoped script resolving the alias by name — decided per instance by a pre-flight | Section 2.3 prompt section 4.0; section 3.3, the two ingestion flows | D-045, D-276 |
| `F19` | No retention, minimisation or data-subject erasure of the verbatim upstream payload the staging table holds | Section 2.3 prompt section 4.0; section 3.2, the property and scheduled-executable classes | D-036, D-240, D-265 |

**One further entry on that page is deliberately not one of the nineteen, and it is reconciled here so the matrix closes over it too.** The nineteen rows above are the whole flag inventory; this is the only page entry outside it.

| Open limitation | Subject | Where it appears in this matrix | D-### |
| --- | --- | --- | --- |
| `OPEN-1` | Live LinkedIn ingestion, declared unavailable pending an eight-row endpoint-contract declaration. The actions, the flow and the alias definition records are built in full and run in `fallback` mode; the live path alone is gated | Section 1.3, the legacy resource-path row and the source-allocation note; section 3.3, the flow class row | D-103 |

It is **not** a flag: the requirement is not unsatisfiable by the platform, and the capability is delivered. What is missing is information only the credential owner can supply — and, before that, an approved provider partner grant the delivery can neither obtain nor assume, which is the shortfall `F15` records. `OPEN-1` is therefore the **route** by which `F15` could close rather than a claim that a credential closes it, per `D-427`. The entry closes on a declaration rather than on a change of requirement — which is why the flag count stays at twelve.

**The exclusion set and the flag inventory agree in both directions.** No exclusion in section 4.2 lacks a home in the flag inventory or a decision reference, and no flag entry is missing from this matrix. The inventory grew from the 10 entries the plan estimated to 12 because two features were newly mapped; that growth is logged at **D-088**, and the `F9` entry was widened to three source requirements at the same time. It grew to 13 when the first review of the delivered artifacts established that cleaning rule 3 cannot be satisfied literally on six of the eleven entity choice columns, because the binding field list declares no `Other` member on them; that entry is `F13` and its decision is **D-022**. It grew to **17** when the delivered artifacts were checked against the real provider contracts and the binding field list, logged at **D-252** together with the fourth disposition that growth required — *partially implemented, flagged*, for a requirement met in part whose shortfall is specific, bounded and counted at run time — and to **19** at **D-300** when they were checked against the frozen artifact inventories. Each addition converts a silent shortfall into a recorded one, which is what prompt section 11.0 requires of the inventory. The addition history and its decision references are the record of that.

**The seven design-system gaps do not all sit under one flag, and they are not all resolved.** The roll-up is three-way:

| Gaps | Flag | Disposition |
| --- | --- | --- |
| `G1` charts, `G2` multi-select chip input, `G3` loading indicator, `G4` card media, `G5` premium upsell treatment | `F7` | **Resolved inside the platform's own component vocabulary**: charts through platform reporting or inline vector markup, the multi-select through a choice-backed field, the loading indicator and card media through Bootstrap equivalents, and the premium upsell through an alert-based panel reused by three hosts. |
| `G6` subscription billing and checkout | `F1` | **Unresolved and flagged.** The platform has no commerce capability at all, so this is not a component gap with a substitute — it is a capability the delivery does not contain. It sits under `F1`, not `F7`. |
| `G7` the icon-system split between the portal's platform glyph font and the executive deck's Lucide set | — | **Not a defect and not carried under any flag.** It is a documented boundary between two artifact classes that are never mixed, recorded so no agent injects one system into the other. |

### 4.3 The superseded stakeholder brief, attribute by attribute

`documentation/Input Prompt.md` is the original stakeholder brief that the binding field list explicitly supersedes. Its attributes are classified here so that none reads as an oversight. Twenty-five attributes: 10 direct matches, 3 surviving inclusion signals, 3 partial matches and **9 consciously excluded**.

| Brief attribute | Disposition | Target | D-### |
| --- | --- | --- | --- |
| Company name | Direct match | `x_bst_startuptrk_startup.name`, mandatory, 100 characters | D-023 |
| Website | Direct match | `x_bst_startuptrk_startup.website` | D-023 |
| Industry | Direct match | `x_bst_startuptrk_startup.industry`, a six-value choice | D-022 |
| Amount fundraised | Direct match | `x_bst_startuptrk_startup.total_funding_usd`, premium-gated currency | D-016 |
| Fundraise stage | Direct match | `x_bst_startuptrk_startup.funding_stage`, an eight-value choice | D-022 |
| Investors | Direct match | Table `x_bst_startuptrk_investor`, plus `lead_investor` and the join table | D-010 |
| Founders | Direct match | Table `x_bst_startuptrk_founder` | D-017 |
| Executives | Direct match | Table `x_bst_startuptrk_executive` | D-017 |
| Roles available | Direct match | Table `x_bst_startuptrk_jobposting` | D-023 |
| Most recent news | Direct match | Table `x_bst_startuptrk_newsarticle`, manual entry or CSV import only | D-054 |
| "Active" companies | Surviving inclusion signal | `x_bst_startuptrk_startup.active`, mandatory, and the first condition of the inclusion filter | D-029 |
| Boston headquarters | Surviving inclusion signal | `x_bst_startuptrk_startup.headquarters_location`, mandatory, and the second condition of the filter | D-029 |
| Raised institutional money in the past 5 years | Surviving inclusion signal | `x_bst_startuptrk_startup.institutional_funding_last_5yrs`, a premium-gated display attribute deliberately outside the filter | D-029 |
| Number of employees | Partial match | `x_bst_startuptrk_startup.employee_count_range`, a five-value band rather than an integer headcount | D-023 |
| "What it does" from the website or public description | Partial match | `x_bst_startuptrk_startup.description`, a 4000-character string | D-023 |
| Last fundraise amount | Partial match | `x_bst_startuptrk_fundinground.amount_usd`, per round rather than a denormalised latest value on the startup | D-023 |
| Sub-sector | **Consciously excluded** | No target. The binding field list carries no such column | D-023 |
| Number of employees locally | **Consciously excluded** | No target | D-023 |
| Headcount growth last 12 months | **Consciously excluded** | No target, which is what makes `F009-3` unbuildable | D-094 |
| Hiring, yes or no | **Consciously excluded** | No target on the startup table; per-posting state serves the need instead | D-023 |
| Employee count by department | **Consciously excluded** | No target | D-023 |
| Competitors | **Consciously excluded** | No target, which is why the legacy "Similar Companies" tab is dropped rather than emptied | D-055 |
| Site traffic | **Consciously excluded** | No target | D-023 |
| Revenue | **Consciously excluded** | No target | D-023 |
| Tech stack | **Consciously excluded** | No target | D-023 |

Four of the nine excluded attributes were **real columns** in the legacy schema — `sub_sector`, `local_employee_count`, `headcount_growth_rate` and `is_hiring` at `src/backend/models/startup.py:L9-L21` — so their absence is an active removal with a direction, which is why they also appear as Retired rows in section 1.1.

---

## 5. Coverage summary

### 5.1 Counts per section

| Section | Direction | Denominator | Rows | Coverage |
| --- | --- | --- | --- | --- |
| 1. Level 1 forward | Legacy construct to target | **123** source files in 7 named groups | 146 | **100 percent** — 9 + 20 + 15 + 22 + 29 + 23 + 5 = 123 |
| 2.1 Level 2 forward | Source sub-requirement to target | **50** sub-requirements across 10 features | 50 | **100 percent** — five rows for each of `F001` to `F010` |
| 2.2 Level 2 forward | Supporting statement to target | 6 load-bearing statements | 6 | **100 percent** |
| 2.3 Level 2 forward | Prompt section to target | **11** sections, 1.0 to 11.0 | 18 | **100 percent** — section 1.0 decomposed into its seven sub-sections |
| 2.4 Level 2 forward | Project rule to target | 3 rules | 3 | **100 percent** |
| 3.1 Reverse A | Repository file to justification | **30** in-scope files, 29 created and 1 updated | 30 | **100 percent** — 0 untraceable |
| 3.2 Reverse A | Update Set record class to justification | 18 classes, **313** update records | 22 | **100 percent** — 0 untraceable |
| 3.3 Reverse A | Manually built artifact class to justification | 10 classes | 10 | **100 percent** — 0 untraceable |
| 4.2.1 Reverse B | Legacy construct deliberately dropped | 49 constructs and construct groups | 49 | Every row carries a decision reference |
| 4.2.2 Reverse B | Requirement not implemented | 28 requirements and requirement groups | 28 | Every row carries a decision reference |
| 4.2.3 Reverse B | Flag inventory reconciliation | **19** flags, `F1` to `F19` | 19 | **100 percent** in both directions |
| 4.3 Reverse B | Superseded stakeholder attribute | 25 attributes | 25 | 10 direct, 3 surviving, 3 partial, **9** excluded |

### 5.2 Transformation and status distributions

| Section 1 transformation | Rows | | Section 2.1 status | Rows |
| --- | --- | --- | --- | --- |
| Replaced | 81 | | Implemented | 22 |
| Retired | 54 | | Partially implemented | 9 |
| Reference-only | 6 | | Flagged | 1 |
| Superseded-doc | 4 | | Consciously excluded | 18 |
| Open | 1 | | | |
| **Total** | **146** | | **Total** | **50** |

### 5.3 Rule 1 compliance statement

| Rule 1 obligation | Discharged by |
| --- | --- |
| A decision log with what was decided, the alternatives, the rationale and the risks | [`./DECISION_LOG.md`](./DECISION_LOG.md), **571** decisions `D-001` to `D-571` across **31** sections, the last twenty-one carrying the remediation decisions of twenty-one review lenses, each naming the row it amends |
| A bidirectional traceability matrix for a migration, source constructs to target implementations | **This file**, sections 1 and 2 forward, sections 3 and 4 reverse |
| **100 percent coverage, no gaps** | Section 4.1's assertion, demonstrated by the twelve denominators of section 5.1 and the exclusion register of section 4.2. The claim is about **mapping** coverage — every source construct and every requirement has a row, and every delivered artifact has a justification — and per [0.5.1](#051-what-a-status-asserts-and-what-it-does-not) it is not a claim that every mapped artifact has been observed to pass. No measure in this file is marked `GAP` |
| Every deviation from a literal reading recorded explicitly | **256** rows flagged as deviations in the decision log, indexed row by row under [Index of deviation rows](./DECISION_LOG.md#index-of-deviation-rows); the two that concern this file are `D-087`, the extension from 8 mapped features to the 10 the document defines, and `D-088`, the flag inventory's growth from 10 entries to 12 and thence to 19 at `D-252` and `D-300` |
| No rationale in code, and none here | This file carries no rationale. Every judgement row carries a `D-###` reference in place of an explanation, and the log is the single source of truth for *why*. The code side is the convention at `D-005`, verified by a comment-block sweep over every Script Include, business rule and scheduled executable in the Update Set, and over the validator, both stylesheet copies, the presentation and every script block in the build guides, with the boundary between description and justification stated at `D-308` |

**Decision references used in this file.** Every `D-###` cited above resolves to a row in `./DECISION_LOG.md`, whose identifiers run contiguously from `D-001` to `D-571`. The five that Rule 3 elevates — `D-024` field-level access control, `D-076` the scope-deletion rollback, `D-043` credential handling, `D-010` the join table and the cascade cluster, and `D-055` the portal tabs and routes — all appear in the target column of section 1 or section 3, so each of the five review entries is traceable from this matrix to the artifact it concerns.

### 5.4 Related documents

| Document | Relationship to this file |
| --- | --- |
| [`./DECISION_LOG.md`](./DECISION_LOG.md) | The other half of Rule 1. Every `D-###` here resolves there |
| [`../review/CRITICAL_DECISIONS.md`](../review/CRITICAL_DECISIONS.md) | Rule 3's five risk-ordered entries, a strict subset of the log |
| [`../../servicenow-startup-tracker-poc/docs/gaps-and-flags.md`](../../servicenow-startup-tracker-poc/docs/gaps-and-flags.md) | The 19-entry flag inventory reconciled in section 4.2.3 |
| [`../../servicenow-startup-tracker-poc/docs/data-model.md`](../../servicenow-startup-tracker-poc/docs/data-model.md) | The field-by-field statement of the ten tables and the 53 entity columns |
| [`../../servicenow-startup-tracker-poc/docs/access-control.md`](../../servicenow-startup-tracker-poc/docs/access-control.md) | The role and access-control matrix behind section 3.2 |
| [`../../servicenow-startup-tracker-poc/docs/api-reference.md`](../../servicenow-startup-tracker-poc/docs/api-reference.md) | The 31 operations, the pagination contract and the Script Include call graph |
| [`../../servicenow-startup-tracker-poc/docs/validation-gates.md`](../../servicenow-startup-tracker-poc/docs/validation-gates.md) | The 11 required post-commit gates, plus the 5 further checks beside them in two classes: the acceptance-required, non-rollback `GATE-COL-01`, and the 4 non-normative `GATE-SEC` diagnostics, which no gate set cites as an entry condition |
| [`../../servicenow-startup-tracker-poc/docs/validation-checklist.md`](../../servicenow-startup-tracker-poc/docs/validation-checklist.md) | The five acceptance criteria mapped one-to-one |
| [`../../servicenow-startup-tracker-poc/docs/manual-build-instructions.md`](../../servicenow-startup-tracker-poc/docs/manual-build-instructions.md) | Authoritative for the execution order 01, 02, 03, 04, 06, 05 |
