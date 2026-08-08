# Critical decisions — Boston Startup Tracker on ServiceNow (`x_bst_startuptrk`)

## Purpose and scope

This is the review artifact required by the project rule **Critical Decision Review Document**. It lists the five highest-risk and most consequential decisions made while replatforming the Boston Startup Tracker from its non-functional Flask, React, PostgreSQL and Celery scaffold onto the ServiceNow Now Platform as the single scoped application `x_bst_startuptrk`. Each entry states what was implemented and what alternatives existed, why the choice was made with a citation a reviewer can follow, the risk it carries, and the one named reviewer who should validate it together with exactly what to check.

**This document is not the decision log.** It is a triage instrument for five reviewers, deliberately short. The authoritative record of every non-trivial decision in this delivery, with its full set of alternatives, its rationale and its risks, is [`../decisions/DECISION_LOG.md`](../decisions/DECISION_LOG.md), required by the project rule **Explainability**. The bidirectional source-to-target traceability matrix required by the same rule is [`../decisions/TRACEABILITY_MATRIX.md`](../decisions/TRACEABILITY_MATRIX.md).

Everything outside those five entries — the forty-odd further decisions this delivery made, the requirement coverage, the retired components, and the reverse lookups from artifact to justification — belongs to those two documents and is not duplicated here. A reviewer who needs the whole picture reads the log. A reviewer who needs to know what to scrutinise first reads this.

## Relationship to the decision log

These five entries are a **strict subset** of the decision log. Two properties follow, and both are checkable:

1. Every decision named here also appears in the log. This document introduces no decision the log does not carry.
2. Every entry names the log row or rows carrying its full rationale, so a reviewer can move from the summary here to the authoritative record.

That subset relation is pre-delivery gate **G-9**, governance completeness: the log covers every decision, this document covers exactly the top five, and each of the five resolves in the log.

### How the log is cited here

The decision log is **delivered**, at [`../decisions/DECISION_LOG.md`](../decisions/DECISION_LOG.md), carrying **101 decisions numbered `D-001` through `D-101`** contiguously across ten sections. Every citation below therefore names both halves of the join: an unambiguous **subject key** — a short quoted phrase naming the decision, which stays readable if the log is ever renumbered — and the **row identifier** that key resolves to, which makes the check mechanical rather than editorial.

**Twenty distinct subject keys** are cited across the five entries and the call-out section, in twenty-one citations — *The join table is authoritative and the List column is a one-way projection* (`D-010` with `D-011`) is cited twice, by entry 4 and again by the second ambiguity, because one decision resolved both. Those twenty keys resolve onto twenty rows of the log. The mapping is not quite one-to-one in two places, and both are stated where they occur: that same key spans the pair `D-010` and `D-011`, because the log separates the authority decision from the projection decision, and `D-043` carries two keys, because the boundary it draws — credential material never leaves the alias — is what makes the API base URLs ordinary non-secret configuration.

The check for gate G-9 is then a lookup a reviewer can perform in a minute: every `**Decision log:**` line below must cite at least one row that exists in the log, and no entry here may be without one. The strongest cross-check is the log's own [Index of the five Rule 3 entries](../decisions/DECISION_LOG.md#index-of-the-five-rule-3-entries), which independently names the primary row of each entry below — `D-024`, `D-076`, `D-043`, `D-010` and `D-055`, in that rank order, with those same five personas and risk levels. The two documents were written to agree on that table, and it is the first thing to re-verify if either is edited.

This convention is the one every delivered document in the package already uses for the log, so the citation style is consistent across the delivery rather than special to this file.

### Rationale here, rationale there

The **Explainability** rule makes the decision log the single source of truth for *why*, while the **Critical Decision Review Document** rule requires a Rationale element inside each entry of this file. The two are reconciled the same way every sibling document in this package reconciles them: the Rationale sections below are **review-oriented restatements written for the named reviewer** — the evidence that reviewer needs in order to judge the decision — and each entry points at the log for the complete alternatives-and-risks analysis. Neither rule is bent. This file and the log are the only two places in the delivery where rationale legitimately appears; it appears in no code comment and no platform record description.

## Referenced documents

**Every document this file links to is delivered and readable.** A reviewer can follow any link below and read the content the statement around it describes; no link is a forward reference to something still to be written.

Those documents are the decision log and traceability matrix named above, [`../../servicenow-startup-tracker-poc/docs/access-control.md`](../../servicenow-startup-tracker-poc/docs/access-control.md), [`../../servicenow-startup-tracker-poc/docs/deployment-runbook.md`](../../servicenow-startup-tracker-poc/docs/deployment-runbook.md), [`../../servicenow-startup-tracker-poc/docs/data-model.md`](../../servicenow-startup-tracker-poc/docs/data-model.md), [`../../servicenow-startup-tracker-poc/docs/api-reference.md`](../../servicenow-startup-tracker-poc/docs/api-reference.md), [`../../servicenow-startup-tracker-poc/docs/validation-gates.md`](../../servicenow-startup-tracker-poc/docs/validation-gates.md), [`../../servicenow-startup-tracker-poc/docs/validation-checklist.md`](../../servicenow-startup-tracker-poc/docs/validation-checklist.md), [`../../servicenow-startup-tracker-poc/docs/gaps-and-flags.md`](../../servicenow-startup-tracker-poc/docs/gaps-and-flags.md), [`../../servicenow-startup-tracker-poc/docs/manual-build/01-connection-credential-aliases.md`](../../servicenow-startup-tracker-poc/docs/manual-build/01-connection-credential-aliases.md), [`../../servicenow-startup-tracker-poc/docs/manual-build/04-service-portal-pages-and-widgets.md`](../../servicenow-startup-tracker-poc/docs/manual-build/04-service-portal-pages-and-widgets.md), the Update Set XML at [`../../servicenow-startup-tracker-poc/update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml`](../../servicenow-startup-tracker-poc/update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml), and the validator at [`../../servicenow-startup-tracker-poc/scripts/validate_update_set_xml.py`](../../servicenow-startup-tracker-poc/scripts/validate_update_set_xml.py).

One statement below is a **requirement on a document rather than a description of it**: the repository root [`README.md`](../../README.md) is required to link to this file by its exact path, and that link is the responsibility of the README rather than of this file.

Every path of the form `src/…`, `scripts/…`, `.github/…`, `.env.example` or `documentation/…` cited in a Rationale section below is a **legacy file, read-only, retained as historical reference**. No legacy file was modified by this delivery. Those citations exist so a reviewer can see the construct being replaced; none of them is a source of target requirements.

## Stability of the numbering

**The entry numbers below are a published contract. Entries must never be reordered or renumbered.** Five documents in this delivery point a reviewer at a specific entry number of this file, so a renumbering silently sends five reviewers to the wrong entry.

| This entry | Risk | Persona | Document that points at it |
| --- | --- | --- | --- |
| 1 | High | Security | [`access-control.md`](../../servicenow-startup-tracker-poc/docs/access-control.md), which names the Security reviewer entry and its impersonation requirement |
| 2 | High | DevOps | [`deployment-runbook.md`](../../servicenow-startup-tracker-poc/docs/deployment-runbook.md), which names "entry 2 … reviewer persona DevOps, risk level High" |
| 3 | High | API/Integration | [`manual-build/01-connection-credential-aliases.md`](../../servicenow-startup-tracker-poc/docs/manual-build/01-connection-credential-aliases.md), entry 3, risk High, API/Integration; [`api-reference.md`](../../servicenow-startup-tracker-poc/docs/api-reference.md) names the same persona entry |
| 4 | Medium | Data/SME | [`data-model.md`](../../servicenow-startup-tracker-poc/docs/data-model.md), which names the Data/SME reviewer entry covering join-table authority, cascade rules and the stored portfolio count |
| 5 | Medium | UX | [`manual-build/04-service-portal-pages-and-widgets.md`](../../servicenow-startup-tracker-poc/docs/manual-build/04-service-portal-pages-and-widgets.md), which names "entry 5 … risk Medium, reviewer persona UX" |

Two further documents consume this one without citing an entry number: [`validation-checklist.md`](../../servicenow-startup-tracker-poc/docs/validation-checklist.md), whose criterion 2 and criterion 5 evidence is gathered by the checks in entries 1 and 5, and [`gaps-and-flags.md`](../../servicenow-startup-tracker-poc/docs/gaps-and-flags.md), which carries the administrator-override flag, the query-parameter routing deviation and the premium-billing flag that entries 1, 5 and the call-out section reference. The repository root [`README.md`](../../README.md) is required to link to this file by its exact path.

If a sixth decision ever outranks one of these five, replace the lower-ranked entry **in place**, keeping its number, and update the citing document. Do not insert, do not append, and do not renumber.

## At a glance

Ordered by risk, highest first. Three High entries precede two Medium entries.

| # | Risk | Reviewer persona | Decision (subject) | Decision log rows |
| --- | --- | --- | --- | --- |
| 1 | **High** | Security | The authorisation decision leaves application code entirely: 49 access controls in five layers, with seven field-level read ACLs as the premium gate and denied keys **omitted** from responses rather than nulled | *Field-level read ACLs as the premium gate* (`D-024`); *Omission rather than nulling in the REST serialiser* (`D-025`); *Secured read path for every caller-facing read* (`D-026`); *ATF test users created at run time rather than shipped* (`D-028`) |
| 2 | **High** | DevOps | Deployment safety is a preview-then-commit lifecycle whose only failure remedy is deleting the `x_bst_startuptrk` scope — the one irreversible operation in this delivery — behind a 309-record Update Set that will push the preview toward its 600-second timeout | *A single Update Set rather than several smaller ones* (`D-070`); *Scope deletion as the rollback mechanism* (`D-076`); *Post-commit gates read table metadata rather than the Table API* (`D-068`); *The XML validator is invoked directly rather than wired into the existing CI workflow* (`D-067`) |
| 3 | **High** | API/Integration | All outbound authentication resolves through two Connection & Credential Aliases referenced **by name**, with zero credential material in the Update Set, in any flow input or in any script step | *Credential aliases referenced by name, with no secret in the deliverable* (`D-043`); *Flow Designer REST step with a runtime connection-resolution fallback* (`D-045`); *LinkedIn moves from a static bearer token to OAuth2* (`D-044`); *API base URLs travel as non-secret properties* (`D-043`) |
| 4 | Medium | Data/SME | The join table is authoritative for participation and the `participating_investors` List column is a stored, read-only, one-way projection of it; cascade delete on every mandatory child reference; `portfolio_count` stored and derived over a distinct union of two traversal paths | *The join table is authoritative and the List column is a one-way projection* (`D-010` with `D-011`); *Cascade delete on mandatory child references* (`D-012`); *A stored portfolio count rather than a dictionary calculated value* (`D-013`) |
| 5 | Medium | UX | Three visible deviations from the legacy surface: the company profile cut from six tabs to five with "Team" re-specified as "People" and "Similar Companies" dropped, query-parameter routing in place of path-style routes, and a declared 1024-pixel viewport floor | *Five tabs with Team re-specified as People and Similar Companies dropped* (`D-055`); *Query-parameter portal routing* (`D-056`); *1024 pixels as the supported viewport floor* (`D-057`) |

Counts in this document were taken from the delivered artifacts rather than from the plan, and differ from the plan's estimates in several places. Where they do, the delivered artifact governs and the difference is noted in the entry.

## 1. Field-level access control as the premium entitlement boundary — risk High — reviewer persona Security

### Decision

**What was implemented.** The authorisation decision was moved out of application code entirely and into the platform's access-control engine. The application declares three roles, whose names are fully qualified and dotted with no underscore form: `x_bst_startuptrk.admin`, `x_bst_startuptrk.premium_user` and `x_bst_startuptrk.user`. Both non-administrative roles are read-only; `x_bst_startuptrk.admin` is the only role that can mutate a record on any surface.

Enforcement is **49 `sys_security_acl` records** — 47 of type `record` and 2 of type `REST_Endpoint` — with **74 `sys_security_acl_role` join records**, arranged in five layers:

| Layer | Scope | ACLs | Role joins | Grants |
| --- | --- | --- | --- | --- |
| 1 | Table-level read, seven entity tables | 7 | 21 | All three roles |
| 2 | Table-level write, create and delete, seven entity tables | 21 | 21 | `x_bst_startuptrk.admin` only |
| 3 | **Field-level read, the seven premium fields** | 7 | 14 | `x_bst_startuptrk.admin` and `x_bst_startuptrk.premium_user` only |
| 4 | Supporting tables, all four operations on each of three | 12 | 14 | The join table readable by all three roles so participation renders; the staging and rate-limit-counter tables administrator-only |
| 5 | REST endpoint execution | 2 | 4 | `Boston Startup Tracker API read` to all three roles; `Boston Startup Tracker API write` to `x_bst_startuptrk.admin` only |

Layer 3 is the entitlement boundary. The seven gated fields are exactly `x_bst_startuptrk_startup.total_funding_usd`, `x_bst_startuptrk_startup.institutional_funding_last_5yrs`, `x_bst_startuptrk_founder.contact_email`, `x_bst_startuptrk_executive.contact_email`, `x_bst_startuptrk_investor.aum_usd`, `x_bst_startuptrk_fundinground.amount_usd` and `x_bst_startuptrk_fundinground.valuation_usd`. There is no eighth. `contact_email` is gated on two tables and is a distinct access control on each.

Three enforcement rules bind every calling surface equally, so the API and the portal cannot disagree about what a role may see. Every caller-facing read uses the **secured** record-access path, never the unsecured one. The response serialiser applies a **per-element read check** and, where it fails, **omits the key from the response object entirely** — it is never nulled, emptied, zeroed or dashed. Every one of the 31 REST operations requires both authentication and access-control authorisation and names the layer-5 control it consults; none of the nine Script Includes is client-callable, mobile-callable or sandbox-callable, and none reads a premium field through an unsecured path on a caller's behalf.

Beneath the access controls sits a scope posture that makes them reachable in the first place: all ten application tables ship `access` `package_private` with every cross-scope operation flag false and `ws_access` false, so the native Table API is not an alternative unmetered, unfield-gated route to the same rows.

**What alternatives existed.**

- **Hide the fields in the interface only**, through form layout or display rules. Rejected: the requirement is a genuine access denial, not a hidden form field, and a hidden field is still readable by any other route to the record.
- **Keep authorisation in application code**, carrying the legacy decorator pattern forward. Rejected: it reproduces the legacy failure mode described below, and the requirements forbid the REST layer from bypassing access control.
- **Table-level ACLs only.** Rejected: the platform then falls back to the table-level grant and every premium field becomes readable by every role.
- **Field-level ACLs only.** Rejected in the opposite direction: without a table-level read grant nothing is readable at all, and the field-level rules never evaluate.
- **Return `null` or an empty string for a denied field.** Rejected: the requirement is omission, and an empty value is indistinguishable from a genuinely empty column.
- **A single premium-role check inside one serialiser, without ACLs.** Rejected: it is a single point of enforcement that any newly added read path can simply forget, and the platform would report no denial because it was never asked.

### Rationale

The legacy application had no authorisation at all, and this is verifiable rather than asserted. `src/backend/utils/auth.py:L6-L16` defines the `auth_required` decorator: it applies `@jwt_required()` at `:L8` and wraps the decorated function in a `try`/`except` returning `{"error": "Authentication required"}` with status 401 at `:L15`. Across the whole 42-line file there is no role parameter, no role argument and no role comparison of any kind. It performs authentication only.

The file records the gap in its own text. `src/backend/utils/auth.py:L36` reads `# TODO: Implement role-based access control`, and `:L42` reads `# TODO: Add additional claims to the token (e.g., user role)`. Read together these establish something stronger than "unimplemented": the access token carried no role claim, so a role check was **not possible** with the token as issued. Meanwhile `src/shared/types.ts:L72-L76` declares `export enum UserRole { ADMIN = 'ADMIN', USER = 'USER', PREMIUM_USER = 'PREMIUM_USER' }` — three entitlement tiers named in the type system and enforced nowhere. The requirement they were meant to serve is `documentation/Software Requirements Specifications (SRS).md:L77`, "Role-based access control (free users, premium subscribers, administrators)", whose "free users" tier becomes the base `x_bst_startuptrk.user` role.

Two platform conventions determine the shape of the replacement.

**The evaluation chain requires a pass at every level, and it is matched most-specific-first** — a table-and-field rule outranks a table-wide rule, which outranks a global rule. This is why both layer 1 and layer 3 are mandatory, and why omitting either fails *silently* and in opposite directions: layer 1 without layer 3 leaves every premium field readable; layer 3 without layer 1 leaves no record readable and the field rules never fire.

**The secured read path returns an empty string for a denied field rather than raising.** Serialising every column of a secured record therefore produces exactly the nulled shape the requirements forbid. Omission is not a by-product of using the secured path; it demands a deliberate per-element check and deletion of the key, which is why the gate lives exactly once and every surface is required to route through it.

The delivered scheme, its five layers, its 21-cell role-by-field matrix and its verification procedure are enumerated in [`access-control.md`](../../servicenow-startup-tracker-poc/docs/access-control.md). Note that the delivered counts — 49 access controls, 74 role joins, five layers — exceed the plan's estimate of roughly 43, 64 and four; the two additional `REST_Endpoint` controls of layer 5 are the difference, and they exist because a Scripted REST API without them falls back to a platform default that any authenticated internal user satisfies.

### Risk level

**High.** Three factors compound.

This is the authorisation boundary of the application, and the data behind it is the commercially valuable part of the dataset: funding totals, round amounts, valuations, investor assets under management, and the contact email addresses of named individuals. Getting it wrong is a data-exposure incident, not a defect report.

Both failure modes are **silent**. Nothing readable, or everything readable — neither raises an error, neither appears in a log, and neither is visible to a caller who is not specifically looking.

Worst, **the administrator override makes a naive verification actively harmful.** All 49 access controls carry `admin_overrides` true, so the platform administrator role overrides every one of them, and every operator of a personal developer instance holds that role. A walkthrough performed while signed in as the instance administrator displays all seven premium fields and **appears to prove enforcement that was never tested at all**. That is worse than no verification, because it manufactures documented false confidence. The scoped role `x_bst_startuptrk.admin` and the platform administrator role are different roles, and conflating them is the specific mistake that produces this outcome.

### Reviewer persona

**Security.** Check each of the following.

1. **Confirm all 21 field-by-role assertions run under impersonation** — the full cross-product of the seven premium fields by the three roles — by purpose-built users each holding **exactly one** scoped role and **none** of the elevated platform roles: not platform `admin`, not `security_admin`, not `maint`. Expected outcomes: `x_bst_startuptrk.admin` reads all seven, `x_bst_startuptrk.premium_user` reads all seven, `x_bst_startuptrk.user` is **denied** all seven.
2. **Reject any verification evidence produced while operating as the instance's global administrator.** This is a hard rejection criterion, not a preference. Evidence gathered that way proves nothing and must not be recorded as a pass.
3. **Confirm the seven field-level read ACLs exist and gate exactly the seven fields named above** — no more, no fewer. Confirm in particular that `x_bst_startuptrk_investor.portfolio_count` is **not** gated; it is not a premium field and treating it as one is a false positive.
4. **Confirm both layers are present and load-bearing:** the 7 table-level read ACLs granting all three roles, and the 7 field-level read ACLs granting only `x_bst_startuptrk.admin` and `x_bst_startuptrk.premium_user`. Prove the pair by reading a **non-premium** column — for example `x_bst_startuptrk_startup.headquarters_location` — under `x_bst_startuptrk.user` in the same call as a denied premium field. A value returned establishes that layer 1 passed and that the denial came from layer 3.
5. **Spot-check omission against nulling on a live response.** As a caller holding only `x_bst_startuptrk.user`, confirm the denied field's key is **absent from the JSON object** — not present with `""`, not present with `null`, not present with a placeholder. In the portal, confirm the same position renders the upsell treatment rather than a blank cell, an empty panel, a zero or a dash.
6. **Search every Script Include, REST operation script and widget server script for unsecured record reads and for client-callable flags.** The delivered documentation names a closed list of five server-side maintenance paths that read unsecured, none of which returns record data to a caller; any unsecured read outside that list is a defect. Confirm every one of the 31 operations carries both authentication and access-control authorisation and names a layer-5 control — an operation that authenticates but skips authorisation defeats the scheme however carefully its script is written.
7. **Confirm the scope posture** — `access` `package_private`, cross-scope flags false, `ws_access` false on all ten tables — since a table left reachable cross-scope or over the Table API bypasses all 49 controls without reporting a denial.
8. **Confirm the ATF test users are created by test setup at run time and are not shipped in the Update Set.** `sys_user` sits outside the application scope and the requirements forbid touching anything outside it; the delivered XML must contain three role definitions and zero role assignments.

**Decision log:** *Field-level read ACLs as the premium gate* (`D-024`); *Omission rather than nulling in the REST serialiser* (`D-025`); *Secured read path for every caller-facing read* (`D-026`); *ATF test users created at run time rather than shipped* (`D-028`).

## 2. Scope deletion as the rollback mechanism, behind a 309-record Update Set — risk High — reviewer persona DevOps

### Decision

**What was implemented.** The legacy application cannot start, so there is no working prior version to fall back to and no incremental code path to retreat along. Deployment-level safety therefore substitutes for code-level incrementalism: a validate-then-preview-then-commit lifecycle with a documented rollback.

The sequence has four stages.

**Pre-delivery validation.** The two-level XML validator runs against the file on disk before anything touches the instance, covering gates **G-1** (the outer `<unload>` document) and **G-2** (every `<payload>` un-escaped and parsed as an independent `<record_update>` document). Exit `0` proceeds; `1` is a validation failure; `2` is a usage or unreadable-path error and takes precedence over `1`. **A non-zero exit blocks the deployment.** The validator covers G-1 and G-2 only — a file that exits `0` is not thereby certified against G-3 through G-9.

**Four pre-flight checks**, all before the upload. Check 1, the instance is reachable and the credentials are valid. Check 2, the scope's existence is **logged and is never a gate**: an existing scope is not an error, because the commit updates existing records and the preview surfaces any real conflict. Check 3, the instance is not mid-upgrade. Check 4, the release is at or above the Yokohama floor, so Flow Designer, ATF, Service Portal and Connection & Credential Aliases are all generally available; below the floor the remedy is to request a new instance rather than downgrade feature usage.

**A six-step import sequence.** Upload the raw XML and capture the resulting record; poll until `loaded` at 5-second intervals with a **300 s** timeout; trigger the preview and poll until `previewed` at 5-second intervals with a **600 s** timeout; require the **error-type** preview-problem set to be **empty** while logging warning-type problems without aborting; then, as a precondition of the commit rather than a member of the gate set, require `PRE-COMMIT-01` and `PRE-COMMIT-02` to confirm all **309** records arrived and previewed; commit and poll until `committed` at 10-second intervals with a **1200 s** timeout; then run the post-commit gates.

**Sixteen post-commit gates**, all required, with no partial pass and none advisory or waivable. The eleven-gate core mandated by the deployment environment is `GATE-TBL-01` through `GATE-TBL-07` for the seven entity tables, `GATE-ROLE-01` through `GATE-ROLE-03` for the three roles, and `GATE-SCOPE-01` for the scope record. Five further gates are delivered: `GATE-COL-01`, asserting the seven entity tables carry exactly 53 columns between them, and `GATE-SEC-01` through `GATE-SEC-04` for the security posture.

**The rollback runs on exactly two conditions** and no others: a commit failure at step 5, or any post-commit gate failure at step 6 — with `GATE-SEC-04` the single exception, since it tests instance configuration this Update Set does not create and its remedy is to set the property and re-run the gate. It then retrieves the `sys_scope` record for `x_bst_startuptrk`, deletes it so its tables, roles and flows cascade, and confirms the cascade completed by reading table **metadata** for an empty result. It destroys all ten tables and all data in them, the three roles, and every artifact inside the scope — including flows, portal records and ATF suites built by hand after the commit, which means guides 01 through 06 must be re-run in full.

The failure matrix places every other condition elsewhere: abort on a pre-flight authentication or authorisation failure; retry a failed upload three times with a 10-second backoff then abort; fix and re-export on a load error, a preview error or any error-type preview problem; abort and investigate on any of the three timeouts without rolling back; retry a `HTTP 500` exactly once after 30 seconds, with no other status retried at all. A gate failure is reported **by its specific gate identifier** before the rollback is initiated.

**What alternatives existed.**

- **Split the delivery into several smaller update sets** to stay inside the practitioner comfort guideline of roughly one hundred records. Rejected: a **single** importable Update Set file is mandated.
- **Roll back by reverting individual update records** rather than deleting the scope. Rejected as unreliable for a first install, where the scope and its tables did not previously exist and there is no prior version of each record to revert to.
- **No rollback at all**, leaving a failed install in place for manual triage. Rejected: it strands a half-committed scope on the instance and leaves the next deployment attempt to collide with it.
- **Take a backup before deleting.** This is the alternative a reviewer will reach for first, and it is not available: **no snapshot or restore facility exists for a personal developer instance operator.** That absence is precisely what makes the operation irreversible rather than merely destructive.
- **Confirm the rollback by reading an application table.** Rejected because it cannot work: the native Table API is disabled on all ten tables, so such a read returns `HTTP 400`, `403` or `404` depending on the instance whether the table still exists or not, and cannot distinguish the two. Table metadata is read instead.
- **Wire the XML validation into the existing GitHub Actions workflow.** Rejected — see the rationale below.

### Rationale

The contrast with the legacy deployment is the sharpest evidence available, and it runs in both directions.

**The legacy pipeline had no rollback.** `.github/workflows/cd.yml:L46` deploys production with `uses: appleboy/ssh-action@master`, whose inline script runs `docker-compose pull`, `docker-compose up -d` and `docker system prune -f` at `:L53` through `:L55`. `.github/workflows/cd.yml:L63` then lists `Implement rollback mechanism in case of deployment failure` among the workflow's own unfinished tasks. The automated path had nothing to fall back to.

**The legacy shell script did have a rollback, and it was reversible — because a database dump existed.** `scripts/deploy_production.sh:L129-L145` defines `rollback()`, which brings the containers down, resolves `LATEST_BACKUP=$(ls -td $BACKUP_DIR/backup_* | head -1)` at `:L137`, and restores with `cp -R $LATEST_BACKUP/* $DEPLOY_DIR/` at `:L139`. That restore is underwritten by a real dump taken earlier in the same script: `:L62` runs `docker exec boston_startup_tracker_db pg_dump -U postgres boston_startup_tracker > $BACKUP_PATH/database_backup.sql`.

**This is the fact a reviewer must not let be softened into "rollback is risky".** The legacy rollback restored data because a `pg_dump` existed. Scope deletion has no dump, no snapshot and no restore path of any kind. That is the entire reason it is the one genuinely irreversible operation in this delivery, and it is why the trigger conditions are enumerated as exactly two rather than left to judgement.

Two further legacy constructs are the antecedents of the target procedure. `scripts/deploy_production.sh:L4-L5` sets `set -e` and `trap 'echo "Error occurred. Exiting."; exit 1' ERR`, which is the abort-on-error posture the failure matrix formalises. `scripts/deploy_production.sh:L104-L127` defines `post_deploy_checks()`: a running-container count at `:L109`, a health probe `curl -f http://localhost:8000/health-check` at `:L115`, and a critical-test subset at `:L121`. Those three checks are the antecedent of the sixteen post-commit gates, which are their machine-checkable equivalent against a platform that has no containers to count.

**Why the validation is not wired into CI.** `.github/workflows/ci.yml:L24` runs `pip install -r requirements.txt` against a `requirements.txt` that does not exist anywhere in the repository, and `:L36-L37` runs `cd src/frontend` then `npm ci` against a directory that contains no `package.json`. A validation step added to that workflow would never reach execution, and its presence would create the false impression of an enforced gate. The validator is therefore invoked directly, as a documented pre-delivery step whose exit code blocks the deployment, and no CI or CD workflow file was modified.

**Why preview duration is a named risk rather than a footnote.** Practitioner guidance keeps an update set under roughly one hundred records and treats five hundred to a thousand as an absolute ceiling. The delivered set carries **309** `sys_update_xml` records across about 1.3 MB — inside the hard ceiling, comfortably above the comfort guideline. The runbook states the consequence plainly: the preview is the longest step in the sequence and should be expected to approach the 600-second timeout. Slowness there is not failure, and the correct behaviour is to poll to the timeout before declaring one.

The full procedure, every request shape, both poll intervals, all three timeouts, the sixteen gates and the complete failure matrix are in [`deployment-runbook.md`](../../servicenow-startup-tracker-poc/docs/deployment-runbook.md), with the gates themselves specified in [`validation-gates.md`](../../servicenow-startup-tracker-poc/docs/validation-gates.md).

### Risk level

**High**, on two independent grounds.

The rollback **destroys the application and every row of data in it with no restore path**, and its blast radius extends beyond the Update Set to every artifact built by hand inside the scope afterwards. On an instance that is not clean, a rollback triggered by one failing gate discards the work of five manual build guides.

Separately, **a preview that runs past 600 seconds aborts a deployment that would otherwise have succeeded.** The risk here is not the timeout itself but the reaction to it: an operator who treats a slow preview as a failure and reaches for the rollback would destroy a scope over a latency problem.

### Reviewer persona

**DevOps.** Check each of the following.

1. **Confirm the rollback is triggered only by the two documented conditions** — a commit failure at step 5, or a post-commit gate failure at step 6 other than `GATE-SEC-04`. Confirm explicitly that it is **not** triggered by a warning-type preview problem, by the pre-flight finding that the scope already exists, by an upload or load failure, by an error-type preview problem, by any of the three timeouts, or by a `PRE-COMMIT` shortfall — each of those has its own non-destructive row in the failure matrix.
2. **Confirm the poll intervals and the 300 / 600 / 1200-second timeouts in the runbook match the deployment environment's specification exactly**, along with the 5-second load and preview cadence and the 10-second commit cadence.
3. **Confirm the preview step aborts on any error-type problem and logs warning-type problems without aborting**, and that both reads are actually issued rather than only the first.
4. **Count the records in the delivered XML and time a preview on a scratch instance before the real run.** Expect 309. Agree an escalation path in advance for a preview that approaches 600 seconds, and confirm the runbook's instruction to poll to the timeout rather than declare failure early. This is the check that prevents a latency event from being answered with an irreversible one.
5. **Confirm a gate failure report names the specific failing gate identifier**, with the observed HTTP status and response body, **before** the rollback is initiated. A generic failure report makes the rollback unreviewable after the fact.
6. **Confirm the retry policy**: a failed upload retried three times with a 10-second backoff then abort; a `HTTP 500` retried exactly once after 30 seconds; no other status retried, with `400`, `401` and `403` evaluated on their first response.
7. **Confirm `GATE-SEC-04` is handled as the stated exception** — set the instance property, re-run the gate, no rollback — and that every other gate failure does roll back.
8. **Confirm the rollback's completion check reads table metadata for an empty result**, not an application table directly, and that a residual table definition stops the process rather than triggering a re-deployment.
9. **Confirm no CI or CD workflow file was modified** and that the validator is invoked directly, exiting `0` before any request reaches the instance.
10. **Confirm the four instance prerequisites are asserted before import**: the operating account holds the `admin` role; the release is at or above the Yokohama floor; ATF execution is enabled with a test-designer role held, without which the coverage gate cannot be evaluated at all; and both credential aliases already hold live credentials.

**Decision log:** *A single Update Set rather than several smaller ones* (`D-070`); *Scope deletion as the rollback mechanism* (`D-076`); *Post-commit gates read table metadata rather than the Table API* (`D-068`); *The XML validator is invoked directly rather than wired into the existing CI workflow* (`D-067`).

## 3. Credential handling for outbound ingestion — risk High — reviewer persona API/Integration

### Decision

**What was implemented.** All outbound authentication resolves through two named Connection & Credential Aliases, referenced **by name** from the Flow Designer REST steps of the two ingestion flows:

| Alias | Authentication model | Holds |
| --- | --- | --- |
| `x_bst_startuptrk.crunchbase_api` | Basic Auth | The Crunchbase API key in the password field, per that provider's convention |
| `x_bst_startuptrk.linkedin_oauth` | OAuth2 | Client identifier, client secret and refresh token |

**Zero credential material appears in the Update Set XML, in any flow input, or in any script step.** The aliases are built on the instance and are not shipped. Because the live credentials are stated to be provisioned already, the manual guide **verifies and binds existing aliases rather than creating secrets**, and no step of the delivery ever writes, prints, echoes or logs a credential value — where a request or a log row must name one, it names the environment variable.

The two API endpoints travel separately as ordinary non-secret configuration: `x_bst_startuptrk.crunchbase.base_url`, shipped value `https://api.crunchbase.com/v3.1`, and `x_bst_startuptrk.linkedin.base_url`, shipped value `https://api.linkedin.com/v2`, both read through the `AppProperties` Script Include. None of the thirteen scoped properties holds an API key, client identifier, client secret, refresh token or password.

LinkedIn moves from a static bearer token to **OAuth2**. This is an authentication-model **upgrade**, not a port: the legacy module had no token endpoint, no refresh token and no expiry handling at all.

A deployment-time branch exists for an instance lacking the entitlement for the Flow Designer REST step: a scoped script step resolves the connection and its credential at run time **by alias name** and issues the call through the scoped outbound REST message API. That path is still alias-by-name, still spoke-free, and still inlines no secret.

**What alternatives existed.**

- **Carry the keys forward as system properties.** Rejected: a property is readable by anything that can read properties, and hard-coding a secret anywhere in the deliverable is forbidden outright.
- **Install an IntegrationHub spoke per source.** Forbidden by the requirements, and unnecessary in any case — a generic REST step bound to a credential alias is not a spoke, which is what makes the primary path both compliant and simple.
- **Keep LinkedIn on a static bearer token because it is simpler.** Rejected: there is no refresh path, so the token expires into a silent ingestion outage, and it would still have to live somewhere.
- **Pass credentials as flow inputs.** Explicitly forbidden, and it would place secret values in the flow definition and its execution history.
- **Commit the aliases inside the Update Set** so the deployment is self-contained. Rejected: an alias committed with credential material would put secrets in the delivered file, which is the one outcome the whole design exists to prevent.

### Rationale

The anti-pattern being eliminated is concrete, citable and worse than it first appears.

`src/data_collection/api_integrators/crunchbase_integrator.py:L11` declares the module-level constant `API_KEY: str = "your_crunchbase_api_key_here"`, and it is passed as a **query parameter** at three separate call sites — `:L22`, `:L41` and `:L60` — each reading `requests.get(endpoint, params={"user_key": API_KEY})`. A key in a query string is not merely hard-coded: it travels in the request URL, which means it lands in intermediary and server access logs, in browser and proxy history, and in any error report that quotes the failing URL. Moving it into a credential alias removes it from the URL as well as from the source.

`src/data_collection/api_integrators/linkedin_integrator.py:L12` repeats the pattern with `API_KEY: str = "your_linkedin_api_key_here"`, sent as a **static** bearer header at three call sites — `:L23`, `:L42` and `:L61` — each reading `requests.get(endpoint, headers={"Authorization": f"Bearer {API_KEY}"})`. Searching the module for a token endpoint, a refresh token or any expiry handling returns nothing. That absence is the precise antecedent of the OAuth2 upgrade: the legacy design had no mechanism by which a credential could ever be rotated without editing source.

`.env.example:L26-L29` shows the same material in plain environment form: the header `# External API Keys` followed by `CRUNCHBASE_API_KEY`, `LINKEDIN_API_KEY` and `GITHUB_API_KEY`. Both base URLs carried forward as non-secret properties are the values pinned at `crunchbase_integrator.py:L10` and `linkedin_integrator.py:L11` — the endpoint is configuration, the key is not, and the delivery separates them.

The governing platform convention is that **a credential alias resolves a connection and its credential at run time without exposing the secret to the caller**, and that the binding between a flow and an alias is **by name**. The consequence a reviewer must act on is that a name mismatch **fails at run time, not at build time**: the flow saves cleanly, the deployment reports success, and the failure surfaces only when the scheduled flow first attempts a call. This is why a connection test before either flow is saved is a requirement rather than a courtesy.

The property inventory, the statement that no property holds a secret, and the identification of the two aliases as the only home for credential material are in [`api-reference.md`](../../servicenow-startup-tracker-poc/docs/api-reference.md); the alias build procedure is [`manual-build/01-connection-credential-aliases.md`](../../servicenow-startup-tracker-poc/docs/manual-build/01-connection-credential-aliases.md).

### Risk level

**High.** A leaked third-party key is an immediate compromise of an external account, outside this instance's control and outside its audit trail — it cannot be contained by fixing the application. And because alias binding fails at run time rather than at build time, a name mismatch can sit undetected through a deployment that reported success in every gate, surfacing hours later as an ingestion outage whose cause is not where the operator will look first.

### Reviewer persona

**API/Integration.** Check each of the following.

1. **Search the delivered Update Set XML for credential material and confirm zero hits.** Search for `key`, `secret`, `token`, `password` and `bearer`, and for all four legacy placeholder strings: `your_crunchbase_api_key_here` and `your_linkedin_api_key_here` from the module constants, and `your_crunchbase_api_key` and `your_linkedin_api_key` from `.env.example`. Repeat the search across all six manual-build guides and across every document in the package. This is pre-delivery gate **G-5**.
2. **Confirm both alias names are spelled exactly** `x_bst_startuptrk.crunchbase_api` and `x_bst_startuptrk.linkedin_oauth`, character for character, in the alias guide **and** in both flow guides. A variant spelling is the exact defect that fails at run time and not at build time.
3. **Confirm the connection test passes before either flow is saved.** Treat an unsaved connection test as a blocking finding, not a deferred one.
4. **Confirm the flows reference the aliases by name only** — no inline URL carrying an embedded key, no credential in any flow input, no credential in any script step, and no credential in a flow's execution history.
5. **Confirm the LinkedIn alias is OAuth2 with a refresh token**, not a static bearer token relabelled. The absence of a refresh path is the legacy defect; an alias that merely stores a long-lived bearer reproduces it under a new name.
6. **Confirm no IntegrationHub spoke is installed or referenced**, and that the fallback path — if the instance requires it — still resolves the connection at run time by alias name rather than reading a secret from anywhere else.
7. **Confirm the two base URLs live in the non-secret properties** `x_bst_startuptrk.crunchbase.base_url` and `x_bst_startuptrk.linkedin.base_url` rather than being hard-coded into a flow step, and confirm no other property holds secret material.
8. **Confirm no credential value appears in the deployment log, the evidence record or any defect report** produced during the deployment, and that each such row names the variable instead.

**Decision log:** *Credential aliases referenced by name, with no secret in the deliverable* (`D-043`); *Flow Designer REST step with a runtime connection-resolution fallback* (`D-045`); *LinkedIn moves from a static bearer token to OAuth2* (`D-044`); *API base URLs travel as non-secret properties* (`D-043`).

## 4. The data-integrity cluster — join-table authority, cascade rules and the stored portfolio count — risk Medium — reviewer persona Data/SME

### Decision

Three related choices, each of which a competent engineer could reasonably have made differently, and each of which the requirements left open.

**4a. `x_bst_startuptrk_m2m_round_investor` is authoritative for participation, and the List column is a one-way projection of it.** The join table holds one row per funding-round-to-participating-investor link, and it is **the only table written when participation changes**. A unique composite index on `(funding_round, investor)` is declared in the Update Set, so the same investor cannot be linked to the same round twice by any write path, and the programmatic writer is idempotent.

Three surfaces read it. The funding-round form surfaces it as a **related list**, which is the editable participant surface. The REST layer assembles `participating_investors` as a **JSON array** from the join table directly, one batched query per page rather than one per round. And `x_bst_startuptrk_fundinground.participating_investors` exists as a `glide_list` column that is **stored, read-only and derived** — a **one-way projection** refreshed from the join table by a single service method whenever a link row is inserted, updated or deleted. Its dictionary entry carries `read_only` true, so a write arriving through the Table API, the native form or an import transform is refused. **Nothing writes both.** The projection is bounded and the bound is enforced: at 33 characters per member the declared length of 4000 holds 121 investors, and beyond that the service **empties the projection and logs the overflow** rather than storing a partial list, because a truncated identifier list is indistinguishable from a complete one when read.

`lead_investor` remains a first-class reference column on the funding round, which is how the lead-versus-participating distinction is carried at all.

**4b. Cascade delete on every mandatory child reference, and on both join-table parents.** Nine reference columns exist across the ten tables. The five mandatory `startup` references on Founder, Executive, Funding round, Job posting and News article cascade, as do both mandatory join-table references. The two **non-mandatory** references deliberately do **not** cascade: `x_bst_startuptrk_fundinground.lead_investor`, so deleting an investor leaves a round that named it as lead standing rather than destroying funding history; and `x_bst_startuptrk_rate_limit_counter.caller`, whose closed windows are removed by a scheduled pruning job instead. A cascade delete fires the portfolio business rules, so the derived count stays correct through a cascade.

**4c. `portfolio_count` is a stored integer maintained by business rules.** It is the count of **distinct** startups over the **union** of two traversal paths: funding rounds whose `lead_investor` is the investor, and funding rounds reached through the join table. The lead path is a grouped read over the funding rounds keyed by startup; the participation path resolves the investor's link rows to startups in batches of at most 200 round identifiers, so no query is handed an unbounded list. **The two result sets are keyed into one set before the size is taken**, which is what makes a company reached by both paths count once. The column is `read_only`, and the REST investor create and update operations separate the fields they accept from the fields they return, so a request body naming `portfolio_count` is ignored rather than applied.

Two business rules maintain it, both delegating to one service so the derivation exists in exactly one place, and each recalculating only the investors its trigger affects. The funding-round rule fires after insert, update and delete: on an update it recalculates **both** the previous and the new `lead_investor` and handles a change to the round's `startup`; on a delete it recalculates the deleted round's lead investor and every investor linked to it through the join table. The join-table rule fires after insert, update and delete: it recalculates the row's investor and, on an update, the previous row's investor, and it refreshes the projection on **both** the current and the previous funding round. A recalculate-all method reads the graph in two passes and then writes only investors whose stored value differs, so a recalculation over an already-correct table performs zero writes and returns the number it did write.

**What alternatives existed.**

- For 4a: **a list-reference column alone**, storing delimited identifiers on the funding round and creating no table at all. Rejected because the requirements name the physical join table explicitly. And **implementing both as independent records of participation** — the obvious reading, and the one that fails: two writable representations of the same fact drift apart. The delivered design keeps both mechanisms the requirements name while making one of them strictly derived and read-only, which is what removes the dual write rather than merely documenting it.
- For 4b: **clearing the reference** instead of cascading, or **blocking the delete** outright. Either is a defensible engineering choice, which is exactly why this needs an entry. Clearing was rejected because a mandatory reference cannot legally be left empty, and orphaned funding rounds would corrupt the portfolio-count derivation by counting rounds belonging to deleted startups. Blocking was rejected as making routine data correction impossible. Cascading on the non-mandatory references was also rejected, in the other direction: it would have let deleting one investor destroy funding history.
- For 4c: **a dictionary-level calculated value**, evaluated on read. Rejected: it re-runs a two-table traversal on every read and can be neither queried nor sorted efficiently. **Recomputing every investor on any change.** Rejected as quadratic in the data volume. **Counting without unioning first.** Rejected because it double-counts, which is the specific error the reviewer check below is designed to catch.

### Rationale

Every part of this cluster is new semantics rather than a port, and the legacy schema is the evidence.

`src/backend/models/funding_round.py:L6-L9` defines the legacy association table `funding_round_investors` with **exactly two foreign-key columns**, `funding_round_id` and `investor_id`, **and nothing else** — no lead flag, no role column, no ordering. `:L23` declares a single undifferentiated `investors` relationship, and `:L40` serialises it as a **flat list of names**, `result['investor_names'] = [investor.name for investor in self.investors]`. A consumer of the legacy API could not tell a lead investor from a participant, because the schema did not record the difference. The lead-versus-participating distinction is therefore introduced by this delivery, which is why it needed a decision at all.

`src/backend/models/investor.py:L9-L12` declares the entire legacy Investor model: `id`, `name`, `type` and `website`. There is **no `portfolio_count`, no `aum_usd` and no `focus_areas`** anywhere in it. The derivation has no legacy precedent of any kind, so every element of its semantics — which paths count, whether they union, whether the value is stored or computed, and when it is refreshed — is a fresh decision rather than a transcription.

`src/backend/models/startup.py:L24-L28` declares exactly the five child relationships `founders`, `executives`, `funding_rounds`, `job_postings` and `news_articles`. A search across every model file for `cascade` or `delete-orphan` returns **nothing**: the legacy schema left orphan behaviour entirely undefined. The requirements are equally silent on it. A cascade decision was therefore unavoidable rather than optional — the only way to avoid making it would have been to ship a schema in which deleting a startup produces rows whose mandatory reference points at nothing.

The delivered model, its nine reference columns with their individual cascade settings, the projection's enumerated one-way write paths, and the two-path derivation with its batching are specified field by field in [`data-model.md`](../../servicenow-startup-tracker-poc/docs/data-model.md).

### Risk level

**Medium**, and the placement is deliberate in both directions.

It sits **below** the three High entries because the failure modes are data-correctness problems, not exposures: a wrong count misinforms, an orphaned row confuses, and both are repairable by re-running a recalculation. No credential leaks and no entitlement boundary moves.

It is **not Low** for two reasons. First, a stored aggregate **drifts silently** if data arrives through a path that skips business rules — an import transform with rule execution disabled is the realistic case, and nothing about the resulting wrong number looks wrong. Second, the union-before-count rule is easy to implement in a way that double-counts an investor's company when that investor both led one round and participated in another round of the same company; the delivered implementation keys both result sets into one set before taking the size, and a reviewer should verify that behaviour rather than assume it.

### Reviewer persona

**Data/SME.** Check each of the following.

1. **Verify the distinct union directly with the double-count case.** Create an investor that **leads** one round of company A and **participates**, through the join table, in a second round of the **same** company A. Confirm `portfolio_count` reads **1**, not 2. This single test is the highest-value check in this entry.
2. **Verify each traversal path independently**: an investor reachable only as a lead, and an investor reachable only through the join table. Both must count.
3. **Verify the update triggers.** Change a round's `lead_investor` and confirm **both** the previous and the new investor are recalculated. Change a round's `startup` and confirm the count follows. Re-point an existing join row and confirm both the previous and the new investor are recalculated **and** that the projection is refreshed on both the previous and the new funding round.
4. **Exercise a startup deletion end to end.** Confirm its founders, executives, funding rounds, job postings and news articles are all removed; that no join-table row survives pointing at a deleted round; and that the affected investors' counts are corrected by the cascade rather than left stale.
5. **Verify the deliberate non-cascades.** Delete an investor that is named as `lead_investor` on a round and confirm the **round survives** with its reference as it stands — this is intended behaviour, not a dangling-reference defect. Confirm rate-limit counter rows are removed by the pruning job and not by a `sys_user` deletion.
6. **Verify the one-way projection rather than assuming it.** Confirm `participating_investors` carries `read_only` true; confirm the REST array is assembled from the **join table** and not from the column; confirm the form's related list reads and writes the **join table**; and confirm exactly one code path writes the column. **Do not raise the existence of the List column as a defect** — it is present by design as a derived projection, and the requirement it satisfies is the List type the specification declares. The defect to look for is the opposite: any second writer to that column, or any consumer that reads the column where it should read the join table.
7. **Verify the projection's overflow behaviour** by linking more investors to one round than the declared length can hold. The projection must be **emptied and the overflow logged**, never truncated to a partial list, and the REST array and the count must both remain correct because neither depends on the projection.
8. **Verify the composite uniqueness constraint** by attempting to link the same investor to the same round twice through each available write path, including the programmatic one.
9. **Verify drift control after a bulk load.** Confirm business rules ran during the staging CSV load, confirm the recalculate-all method was invoked from a background script afterwards, and then compare the stored counts against a freshly recomputed set. A recalculation over a correct table should report zero investors written; a non-zero figure is the drift signal.

**Decision log:** *The join table is authoritative and the List column is a one-way projection* (`D-010` with `D-011`); *Cascade delete on mandatory child references* (`D-012`); *A stored portfolio count rather than a dictionary calculated value* (`D-013`).

## 5. Interface deviations from the legacy surface — risk Medium — reviewer persona UX

### Decision

**What was implemented.** A Service Portal experience — one portal on the url suffix `bst`, one theme, five pages `bst_home`, `bst_company`, `bst_investor`, `bst_dashboard` and `bst_account`, and eight widgets — carrying three deliberate deviations from the legacy React surface.

**5a. The company profile is cut from six tabs to five.** The delivered tab strip is exactly **Overview, Funding, People, Jobs, News**, in that order and with those labels. Three things changed at once, and all three must be stated: "Similar Companies" is **dropped outright**; "Team" is **re-specified as "People"** and now carries founders **and** executives together in one pane; and the **order changed**, so Funding moves from third position to second and People sits third.

**5b. Routing is query-parameter based.** Pages are addressed as `/bst?id=<page>`, and a record-scoped page adds `&sys_id=<record>`. `/bst` with no `id` resolves to the home page. Inside a widget template links are written relatively as `?id=…`, so the portal suffix is never hard-coded into a widget.

**5c. 1024 pixels is the declared supported viewport floor.** Only medium and large Bootstrap column classes are authored. No extra-small or small refinement exists: no `col-xs-*`, no `col-sm-*`, no `hidden-xs`, no `visible-sm-*`, and no media query keyed to the extra-small or small breakpoint. A viewport narrower than 1024 pixels is out of scope and is not a defect.

Two supporting points belong to this entry because they are what a UX reviewer will look for. The reusable `bst-premium-upsell` widget renders **in place of** each gated field or gated tab region wherever the read access control denies — never a blank, an empty cell, a zero or a dash — with a `Premium` label at field granularity and the partial rendered once for the surface; it has three hosts, the company profile, the investor profile and the account summary, and is placed on no page of its own. And the portal's sole icon source is the **platform glyph font**: never Lucide, which is confined by rule to the executive deck. The instruction runs both ways.

**What alternatives existed.**

- For 5a: **keep six tabs**, leaving "Similar Companies" empty or populating it from a heuristic such as shared industry. Rejected — an empty tab advertises missing functionality, and a heuristic would present invented data as fact. **Keep the label "Team"** rather than renaming. Rejected: the five tab names are specified, and the pane's contents changed anyway, since it now carries executives as well as founders. **Keep the legacy tab order.** Rejected: the specified order is part of the specified tab list.
- For 5b: **implement URL rewriting** to preserve path-style routes such as `/company/<id>`. Rejected as disproportionate — five routes are mandated, their URL syntax is not, and a rewriting layer would add a failure mode to every deep link in exchange for cosmetic parity with an application that never ran.
- For 5c: **author extra-small and small breakpoints anyway.** Rejected: viewports below 1024 pixels are explicitly out of scope, and as the rationale shows there was no responsive behaviour to preserve.
- On the upsell: **hide gated fields silently.** Rejected — a blank cell is indistinguishable from a genuinely empty column, so silent hiding conceals the entitlement boundary from the very user it applies to and makes the product look broken rather than tiered.

### Rationale

**The dropped tab was forced, not chosen.** `src/frontend/components/CompanyProfile/CompanyProfile.tsx:L86-L91` renders six tabs in the order Overview, Team, Funding, Jobs, News, Similar Companies. `:L112` binds the sixth to `companyProfile?.similarCompanies` — a field with **no counterpart anywhere in the binding schema**, which declares no competitor or similarity column on any of the seven entity tables. There is no data to render. That absence *is* the rationale; keeping the tab would have required either an empty pane or invented data.

**The routing change replaces routes that were never served.** `src/frontend/App.tsx:L29-L37` declares five path-style routes with `:id` parameters — `/`, `/search`, `/company/:id`, `/investor/:id` and `/user/:id` — which is the antecedent of the five target pages and of the query-parameter form that replaces them. The platform convention is decisive here: Service Portal addresses pages by query parameter, so the path form is not reproducible without URL rewriting. Worth noting alongside it, `src/frontend/App.tsx:L12` imports `./styles/theme`, a module that was never authored — the styles directory contains only `global.css` — so the legacy application could not have rendered any of those five routes in the first place.

**The 1024-pixel floor discards nothing.** `src/frontend/styles/global.css` is the repository's entire design-token and responsive surface: 42 lines, of which a search for `media` returns **not one match**. There was no responsive behaviour at any breakpoint, so declaring a floor removes no existing capability and closes no previously supported viewport. The same file hard-codes `background-color: #f5f5f5` at `:L8`, `color: #1976d2` at `:L14` and `max-width: 1200px` at `:L24`, which is why the target declares design tokens in the theme record instead of literals in widget CSS — and why the Material-UI component vocabulary has no carry-over at all, the platform design system being Bootstrap 3.3.6 with AngularJS.

The portal build, the fixed tab list, the routing table with its eleven navigation hops, the floor's exact mechanics, the upsell substitution rules and the iconography constraint are specified in [`manual-build/04-service-portal-pages-and-widgets.md`](../../servicenow-startup-tracker-poc/docs/manual-build/04-service-portal-pages-and-widgets.md).

### Risk level

**Medium.** These deviations are visible to every user and to any stakeholder comparing the result against the legacy screens, so they carry real expectation-management risk and should not be discovered at a demonstration. The upsell treatment additionally sits directly on the entitlement boundary: if it renders where it should not, or fails to render where it should, a user's understanding of what they are entitled to is wrong.

They are nonetheless **reversible and non-destructive**, which keeps them below the three High entries. A tab can be added, a route rewritten, a breakpoint authored, a label changed. Nothing is lost that cannot be restored, and no data or credential is at stake.

### Reviewer persona

**UX.** Check each of the following.

1. **Walk all five routes** and confirm each renders and navigates: `?id=bst_home`, `?id=bst_company&sys_id=<startup>`, `?id=bst_investor&sys_id=<investor>`, `?id=bst_dashboard`, `?id=bst_account`. Confirm `/bst` with no `id` resolves to the home page, and confirm every navigation hop between pages reaches its target with the correct record identifier.
2. **Confirm the company profile shows exactly five tabs**, labelled and ordered **Overview, Funding, People, Jobs, News**, and that the People pane shows founders **and** executives together. Confirm no sixth tab and no "Team" label survives anywhere.
3. **Confirm the premium upsell treatment appears wherever a gated field or gated tab region is denied — and check it as the base user.** Impersonate a user holding only `x_bst_startuptrk.user` and confirm the treatment appears in all three host surfaces: the company profile, the investor profile and the account summary. Then confirm under `x_bst_startuptrk.premium_user` that it appears in **none** of them. Never perform this check as an administrator; the override described in entry 1 will show every premium field and prove nothing.
4. **Confirm nothing is silently blank.** Where a premium field is denied, the position must carry the upsell treatment or the `Premium` label — not an empty cell, not a zero, not a dash, not an empty panel. Confirm the upsell partial never receives the value it exists to hide.
5. **Confirm no path-style route survives** and that every deep link, including those generated inside widget templates, takes the `?id=<page>&sys_id=<record>` form with no hard-coded portal suffix.
6. **Confirm the layout is usable at exactly 1024 pixels wide**, that no extra-small or small column class or breakpoint refinement was authored, and that 1024 pixels is stated as the supported floor in the portal documentation. Do not raise a narrower viewport as a defect.
7. **Confirm the record-not-found path** on the two record-scoped pages: with an absent or unresolvable `sys_id`, each must render an explicit not-found message rather than an empty panel.
8. **Confirm the icon split holds in both directions:** no Lucide script tag, stylesheet, `data-lucide` attribute or Lucide SVG appears in any widget template, controller, CSS field or theme field; and no platform glyph appears in the executive deck. Confirm zero emoji anywhere in the portal, including option labels, alert wording and CSS comments.
9. **Confirm widget CSS contains no hard-coded colour, spacing, radius or font literal** beyond the permitted `0`, `none`, `auto`, `inherit`, `currentColor` and `transparent`; every other value must resolve to a design token declared in the theme.

**Decision log:** *Five tabs with Team re-specified as People and Similar Companies dropped* (`D-055`); *Query-parameter portal routing* (`D-056`); *1024 pixels as the supported viewport floor* (`D-057`).

## Rule 3 call-out coverage

The **Critical Decision Review Document** rule requires three categories to be called out explicitly. All three are discharged below, so a reviewer does not have to infer the coverage.

### Irreversible operations — entry 2

**The scope-deletion rollback of entry 2 is the one genuinely irreversible operation in this delivery.** Deleting the `x_bst_startuptrk` scope record cascades its ten tables, all data in them, its three roles and every artifact built inside it. No snapshot, dump or restore facility is available to a personal developer instance operator, which is exactly what distinguishes it from the legacy rollback it replaces — that one restored data because a `pg_dump` existed at `scripts/deploy_production.sh:L62`.

The claim is bounded deliberately, because an unbounded warning is ignored. Everything else in this delivery is recoverable:

- **Nothing is deleted from the repository.** The entire legacy tree is retained read-only, and the repository `README.md` is the only legacy file this delivery modifies at all.
- **The Update Set import is preview-then-commit.** A problem found at preview costs nothing: the set has not been applied, and the remedy is to fix the source and re-import. Every failure condition before the commit resolves without touching the scope.
- **The pre-delivery gates run against files, not against the instance.** A file that fails validation has never reached the instance, so a failure there has no blast radius at all.
- **A `GATE-SEC-04` failure does not roll back.** It is instance configuration this Update Set does not own, and its remedy is to set the property and re-run the gate.

### Authorization decisions — entry 1, with entry 3 adjacent

**Entry 1 is the authorization decision**: moving the entitlement boundary out of application code and into 49 platform access controls, with seven field-level read ACLs as the premium gate and denied keys omitted rather than nulled. Its most consequential property is that both of its failure modes are silent and that the administrator override makes a careless verification produce documented false confidence.

**Entry 3 is the adjacent authentication and credential decision**: how the application proves its own identity to Crunchbase and LinkedIn, and why no secret appears anywhere in the deliverable. The two are separate concerns and are reviewed by different people — entry 1 governs what a caller may read from this application, entry 3 governs what this application may read from elsewhere — but a reviewer of either should be aware of the other, because a bypass in one makes the other's controls moot.

### Assumptions that resolved an ambiguity in the request

Three requirements were internally ambiguous. Each was resolved by an explicit assumption rather than by silent choice, and each is stated here with what would change if the assumption is wrong.

**Ambiguity 1 — `institutional_funding_last_5yrs` appears in two mutually awkward lists.** It is named both among the fields relevant to the startup inclusion criteria and among the seven premium-gated fields.

*Assumption.* The operative inclusion rule names only two conditions: `active` = true, **and** `headquarters_location` containing "Boston" or "Cambridge, MA" as a case-insensitive substring. The filter therefore tests **exactly those two columns**, and `institutional_funding_last_5yrs` remains a premium-gated **display** attribute that takes no part in the predicate. The two location tokens are read from a system property, so they are configurable without a code change.

*Why this matters concretely.* The base `x_bst_startuptrk.user` role **cannot read** `institutional_funding_last_5yrs` — that is the point of entry 1. Had the inclusion filter depended on it, the portal search results would have been unbuildable for precisely the role that uses them most: the filter would have needed a value its caller is denied. The two requirements are only simultaneously satisfiable under this reading.

*If the assumption is wrong* — if the field was genuinely intended as a third condition — then either the field must cease to be premium-gated, or the filter must be evaluated with elevated privilege on the caller's behalf, which would be the first deliberate hole in entry 1's enforcement. Neither is a small change, which is why this is flagged rather than quietly adjusted. **Nobody should "correct" the filter to add the field without reopening entry 1.** The corresponding flag is carried in [`gaps-and-flags.md`](../../servicenow-startup-tracker-poc/docs/gaps-and-flags.md).

**Ambiguity 2 — `participating_investors` is described as a "List" field while a physical join table is named in the same clause.** These are two different platform mechanisms: a list column stores delimited identifiers inside the funding-round row and creates no table, whereas a join table is a separate physical table with its own rows.

*Assumption.* Both statements are honoured without a dual write. The **join table is authoritative** and is the only write target for participation; the **related list** on the funding-round form delivers the List user experience; the **REST array** delivers the list-valued attribute an API consumer expects; and the **List column exists as a stored, read-only, one-way projection** of the join table. Nothing writes both.

*If the assumption is wrong* — if the List column was intended as the authoritative store — the join table becomes redundant, and the projection's single writer becomes the participation writer instead. The migration is mechanical but it inverts the direction of every write path enumerated in entry 4. See **entry 4**, and note its explicit instruction not to raise the column's existence as a defect.

**Ambiguity 3 — "exactly 7 custom tables" is stated while an eighth join table is named and a staging table is separately required.**

*Assumption.* The seven-table count governs **entity** tables. The join table, the ingestion staging table and the rate-limit counter table are **supporting artifacts**, documented separately and counted separately. Ten physical tables ship, and the success criterion is evaluated against the seven entity tables — which is why the delivered gate set contains exactly seven table gates plus `GATE-COL-01` counting columns across those same seven, while `GATE-SEC-01` and `GATE-SEC-02` assert the access posture across all ten.

*If the assumption is wrong* — if the count was meant to bind the physical table total — the delivery is three tables over budget, and no combination of the three can be removed without losing a stated requirement: the join table is named explicitly in the requirements, the staging table is mandated as the fallback dataset's home, and the counter table is what makes the specified rate-limit response body expressible with a computed retry value. The count would have to be renegotiated rather than met.

**Decision log:** *The startup inclusion filter tests only active and headquarters_location* (`D-029`); *The join table is authoritative and the List column is a one-way projection* (`D-010` with `D-011`); *Exactly seven entity tables, with three supporting tables counted separately* (`D-008`).
