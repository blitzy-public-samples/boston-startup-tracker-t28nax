# Validation checklist — `x_bst_startuptrk`

This checklist is the **acceptance record** for the ServiceNow scoped application `x_bst_startuptrk`. It maps **one to one onto the five success criteria of prompt section 10.0**: five criteria, five sections, in order, each labelled with its criterion number. It is worked **last** — after the Update Set has been validated, imported, previewed and committed per [`./deployment-runbook.md`](./deployment-runbook.md), and after all six guides indexed by [`./manual-build-instructions.md`](./manual-build-instructions.md) have been completed in their execution order. What an operator records here **is** the delivery evidence. Nothing else in this package claims acceptance.

## How to use this document

Every item is a **checkbox with an evidence field and a pass condition**. Tick an item only after writing the observed evidence into its **Evidence** field or its table row: an HTTP status, a record count, a test-result name, a log line, a screenshot reference, or a timestamp. **Nothing is marked complete on assertion alone.** An item whose evidence field is empty is not complete, however confident the operator is. Where a section supplies a table, the table is the evidence field for the items above it, and every row is filled. Record the observed value even when it matches the expectation, because the recorded value is what a reviewer reads. Record no credential value anywhere in this document.

Work the sections in order. Section A runs against the repository before anything touches the instance; section B runs during the deployment; criteria 1 to 5 run after the manual build; section H is the closing gate. A criterion whose evidence was gathered before its prerequisites were met is void and is gathered again.

## Sign-off header

Fill this block first. It identifies the artefact and the instance the evidence below belongs to; evidence with no header is not attributable to any deployment.

| Field | Value |
| --- | --- |
| Operator | |
| Date started (UTC) | |
| Date completed (UTC) | |
| Instance URL | |
| Instance release and patch level | |
| Update Set file | `../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml` |
| Update Set update-record count reported by the validator | |
| Retrieved update set `sys_id` on the instance | |
| Scoped application version | `1.0.0` |
| Overall verdict — accepted or not accepted | |

## The five criteria at a glance

The whole acceptance shape, one line per criterion, before the detail. Each row links to the section that carries its evidence.

| # | Criterion (prompt section 10.0) | Pass condition in one line |
| --- | --- | --- |
| [1](#criterion-1--all-seven-tables-exist-with-100--of-their-fields) | All 7 tables exist with 100 % of their fields, verified field by field | 7 tables present, **53** columns matching the binding list exactly on name, type, length and mandatory flag, and 7 table-CRUD suites passing |
| [2](#criterion-2--all-three-roles-enforce-field-level-acls-on-100--of-the-seven-premium-fields) | All 3 roles enforce field-level ACLs on 100 % of the 7 premium fields, verified per role per field | **21 of 21** cells correct under impersonation, plus the omission spot check and the control-column check |
| [3](#criterion-3--all-six-rest-resources-return-correct-paginated-responses-and-a-429-with-a-retry-value) | All 6 REST resources return correct paginated responses and a 429 with a retry value | **6 of 6** resources passing all three assertions — success shape, pagination with an agreeing `total_count`, and the exact 429 body |
| [4](#criterion-4--scheduled-flows-ingest-and-clean-on-the-configured-cadence-with-zero-unhandled-errors) | Scheduled flows ingest and clean Crunchbase and LinkedIn data, or the sample-dataset substitute, on the configured cadence with zero unhandled errors across 3 consecutive scheduled runs | **3** consecutive guard-passing runs **per flow** with **zero** unhandled errors, and the provenance of every run recorded as `live` or `fallback` |
| [5](#criterion-5--all-five-service-portal-routes-render-and-navigate-as-specified) | All 5 Service Portal routes render and navigate as specified, verified by walkthrough, with the startup inclusion filter confirmed active on Home / Search | **5** routes rendering and navigating, **5** tabs on the company profile, the excluded startup absent from search but present in the admin list, and the upsell treatment visible to the base role |

Three further sections carry gates the criteria depend on: [section A](#a--pre-delivery-gates-g-1-to-g-9), the nine pre-delivery gates; [section B](#b--deployment-gates), the two pre-commit checks and the sixteen post-commit gates; and [section H](#h--coverage-gate-rule-compliance-and-definition-of-done), the coverage gate, the rule-compliance items and the definition of done.

## Referenced documents

Some documents named below are **planned artifacts of this package**. Every link to one carries the marker **(planned)** in its link text. A statement about a planned document describes what that document is required to contain; it is not a claim that the content can be read from it today.

| Document | What this checklist takes from it |
| --- | --- |
| [`./data-model.md`](./data-model.md) | The ten tables field by field: the 53 entity columns with their types, lengths, mandatory flags and premium markers, the choice lists, and the startup inclusion predicate. The source of the criterion 1 field rows. |
| [`./access-control.md`](./access-control.md) | The three roles, the five ACL layers, the seven premium fields, the secured read path, the omitted-not-nulled rule and the impersonation requirement. The source of the criterion 2 grid. |
| [`./api-reference.md`](./api-reference.md) | The six logical resources, the nested executives sub-resource, the pagination contract, the response envelope and the error contracts. The source of the criterion 3 assertions. |
| [`./validation-gates.md`](./validation-gates.md) | The two pre-commit checks and the sixteen post-commit gates, with their targets, queries and pass conditions, and the evidence record this checklist cites. |
| [`./deployment-runbook.md`](./deployment-runbook.md) | The pre-delivery validator invocation, the pre-flight checks, the six-step import sequence, the rollback, the failure matrix, the ATF prerequisite asserted before import, and the definition of a scheduled run. |
| [`./manual-build-instructions.md`](./manual-build-instructions.md) | The index and execution order of the six manual-build guides, and the eleven-gate core within the sixteen post-commit gates. |
| [`./gaps-and-flags.md`](./gaps-and-flags.md) | The twelve requirements with no clean platform equivalent, which section H confirms are flagged rather than silently omitted or half-implemented. |
| [`../scripts/validate_update_set_xml.py`](../scripts/validate_update_set_xml.py) | The two-level well-formedness validator that establishes gates G-1 and G-2, and its exit-code contract. |
| [`../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml`](../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml) | The single importable Update Set the pre-delivery gates and the deployment gates are run against. |
| [`./manual-build/01-connection-credential-aliases.md`](./manual-build/01-connection-credential-aliases.md) | The two Connection & Credential Aliases, and the provisioning state that decides whether an ingestion run resolves `live` or `fallback`. |
| [`./manual-build/02-flow-crunchbase-ingestion.md`](./manual-build/02-flow-crunchbase-ingestion.md) | The Crunchbase flow, its cadence guard, the four cleaning rules and the run-summary record criterion 4 reads. |
| [`./manual-build/03-flow-linkedin-ingestion.md`](./manual-build/03-flow-linkedin-ingestion.md) | The LinkedIn flow, identical in its guard, cleaning and run-summary mechanics. |
| [`./manual-build/04-service-portal-pages-and-widgets.md`](./manual-build/04-service-portal-pages-and-widgets.md) | The portal, the five pages, the five company-profile tabs, the eight widgets, the upsell substitution rule and the 1024-pixel floor. The source of the criterion 5 walkthrough. |
| [`./manual-build/05-atf-test-suites.md`](./manual-build/05-atf-test-suites.md) | The ten suites and thirty-six tests, the twenty-one ACL cells by name, the six REST tests, the two flow tests, and the three techniques the evidence depends on. |
| [`./manual-build/06-staging-table-csv-import.md`](./manual-build/06-staging-table-csv-import.md) | The load of the six sample CSVs into the one staging table, which the fallback branch of both flows reads. |
| [`../sample-data/README.md`](../sample-data/README.md) | The staging column contract and the fallback-only posture of the dataset. |
| [`../README.md` (planned)](../README.md) | The package index and the deploy order this checklist follows. |
| [`../../docs/decisions/DECISION_LOG.md` (planned)](../../docs/decisions/DECISION_LOG.md) | The single source of truth for every decision behind the procedures below. |
| [`../../docs/decisions/TRACEABILITY_MATRIX.md` (planned)](../../docs/decisions/TRACEABILITY_MATRIX.md) | The bidirectional matrix section H verifies for coverage in both directions. |
| [`../../docs/review/CRITICAL_DECISIONS.md` (planned)](../../docs/review/CRITICAL_DECISIONS.md) | The five risk-ordered review entries section H verifies the shape of. |
| [`../../blitzy-deck/boston-startup-tracker-servicenow-executive-summary.html` (planned)](../../blitzy-deck/boston-startup-tracker-servicenow-executive-summary.html) | The executive deck that gate G-8 and the Rule 2 item inspect. |
| [`../../blitzy-deck/references/blitzy-reveal-theme.css`](../../blitzy-deck/references/blitzy-reveal-theme.css) | The canonical deck theme whose CSS the Rule 2 item compares against the deck's inline style block. |

This document carries **criteria, evidence and pass conditions only**. It states what to check, what to record and when an item passes. Every decision behind these procedures, every alternative considered and every risk each carries is recorded in [`../../docs/decisions/DECISION_LOG.md` (planned)](../../docs/decisions/DECISION_LOG.md), which is the single source of truth for "why". Where an item below states a procedural requirement and its failure mode, that is the requirement and its consequence, not an argument for it.

**Review.** Three items in this checklist are the observable form of the three categories [`../../docs/review/CRITICAL_DECISIONS.md` (planned)](../../docs/review/CRITICAL_DECISIONS.md) is required to call out. The **authorization decision** is verified by [criterion 2](#criterion-2--all-three-roles-enforce-field-level-acls-on-100--of-the-seven-premium-fields). The **irreversible operation** — the rollback, which deletes the `x_bst_startuptrk` scope and cascades its tables, roles and flows — is bounded by [section B](#b--deployment-gates), which is the only place in this checklist that can trigger it. The **ambiguity resolutions** are verified where each one bites: the inclusion-criteria field ambiguity by [criterion 5](#criterion-5--all-five-service-portal-routes-render-and-navigate-as-specified), the participating-investors list interpretation by [criterion 1](#criterion-1--all-seven-tables-exist-with-100--of-their-fields), and the seven-entity-table count by the counting rule stated in criterion 1. The review entries themselves are not reproduced here.

## A — pre-delivery gates G-1 to G-9

**Nine gates**, run against the repository artifacts **before anything is imported**. All nine are required. A failure at any one of them blocks delivery, and gates G-1 and G-2 additionally block the deployment: a non-zero validator exit means the file is not uploaded at all.

Run them in the order below. G-1 and G-2 come first because they are mechanical and cheap, and because the rest of the package is not worth inspecting until the artifact it describes parses.

### G-1 — outer update-set well-formedness

- [ ] **The Update Set parses as a single XML document whose root is `<unload>`, containing exactly one `<sys_remote_update_set>` header record and at least one `<sys_update_xml>` update record.** Run the validator from the repository root:

  ```text
  python3 servicenow-startup-tracker-poc/scripts/validate_update_set_xml.py
  ```

  With no path argument the validator resolves the sibling Update Set `update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml` relative to its own directory, so the delivered artifact needs no argument. The exit-code contract, exactly as [`../scripts/validate_update_set_xml.py`](../scripts/validate_update_set_xml.py) defines it and [`./deployment-runbook.md`](./deployment-runbook.md) restates it: **`0`** every validated file satisfied both gates; **`1`** at least one validation failure at either level; **`2`** usage error, or a path that is missing, not a regular file, or unreadable, with code `2` taking precedence over code `1`.

  **Evidence to record:** the whole of the validator's **stage 1, gate G-1** block — the reported root element, the header-record count, the update-record count, and the header-linkage line stating how many update records carry the header `sys_id` — together with the process exit status.

  **Pass condition:** stage 1 reports `gate G-1 PASS`, the root is `<unload>`, the header count is exactly `1`, the update-record count is at least `1`, and the process exits `0`.

- [ ] **A non-zero exit blocks delivery and blocks the deployment.** Correct the XML and re-run until the validator exits `0`. Do not upload a file that failed validation and do not proceed to the pre-flight checks. **Evidence:** for any failed run, the stderr diagnostic and the exit status, followed by the passing re-run.

### G-2 — nested per-record payload well-formedness

- [ ] **Every `<payload>` element, once un-escaped, parses as an independent document whose root is `<record_update>` carrying a non-empty `table` attribute.** This is the validator's second stage and it runs in the same invocation as G-1.

  **Evidence to record:** the whole of the validator's **stage 2, gate G-2** block — the number of update records examined, the count of well-formed payloads out of the number examined, and the update-name contract line — together with the process exit status.

  **Pass condition:** stage 2 reports `gate G-2 PASS`, the well-formed payload count equals the number examined, and the process exits `0`.

- [ ] **Read a G-2 failure against the escaping arithmetic.** Content inside a nested record document is escaped once for that document and again as the text of `<payload>`, so a `&&` in a script body appears in the outer file as `&amp;amp;&amp;amp;`. A single-escaped ampersand leaves the outer file legal, because a single ampersand entity is legal there, while the un-escaped payload then contains a bare double ampersand and is not well-formed. **A single parse of the outer document cannot see that defect**, which is why the validator parses at two levels and why G-1 passing tells you nothing about G-2. The script bodies in this Update Set — the advanced access-control scripts, the nine Script Includes, the business rules and the scheduled job — are where this defect class lives. **Evidence:** for any failure, the payload ordinal, its `target_name` and the parser's line and column, copied from stderr.

### G-3 — referential integrity

- [ ] **Every reference among the payload records resolves.** Each of the following must hold across the whole file: every `sys_dictionary` record's collection name equals an existing table record's name; every reference column's target names an existing table; every choice record's name-and-element pair matches a real column; every access-control name is either a table name or a table-and-field pair on a real column; every access-control role join points at one of the three `sys_user_role` records; every Scripted REST operation points at the single REST definition; and every payload record names the scoped application `x_bst_startuptrk` as its scope.

  **Evidence to record:** the **empty error-type preview-problem set** from step 4 of the import sequence in [`./deployment-runbook.md`](./deployment-runbook.md) — the request issued, the `result` array observed, and its length. A dangling identifier surfaces there as a problem record of type `error`, and the preview step aborts the deployment on any such record. Record the warning-type set alongside it, which is logged and does not abort.

  **Pass condition:** the error-type preview-problem `result` array is empty. Any error-type record fails this gate, and the offending identifier is corrected in the XML before the sequence restarts.

### G-4 — scope containment

- [ ] **No payload record carries a scope other than `x_bst_startuptrk`, and no record targets a table outside the application.** Audit the delivered XML for the scope value on every payload record and for the target of every record that names a table.

  **Evidence to record:** the total payload-record count, the count carrying the `x_bst_startuptrk` scope, and the list of any record that does not — by `target_name` and `type`. Record the audit command or the query used, so the check is repeatable.

  **Pass condition:** the count carrying the `x_bst_startuptrk` scope equals the total payload-record count, and the list of exceptions is empty. A record that omits the scope lands in the Global scope on import, which breaches the containment requirement at the moment of commit.

### G-5 — secret hygiene

- [ ] **The Update Set XML contains no credential material.** No API key, no client secret, no refresh token, no password value, no bearer token and no basic-auth URL. **Evidence:** the search performed over `../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml`, the patterns searched for, and the hit count for each — zero for every one.

- [ ] **Every manual-build guide contains no credential material either.** The same search over all six guides under [`./manual-build/`](./manual-build/) and over [`./manual-build-instructions.md`](./manual-build-instructions.md). The two Connection & Credential Aliases are referenced **by name only** — `x_bst_startuptrk.crunchbase_api` and `x_bst_startuptrk.linkedin_oauth` — and guide 01 verifies and binds existing aliases rather than creating secrets. **Evidence:** the file list searched, the patterns, and the hit count per file.

  **Pass condition:** zero hits across the XML and all seven manual-build documents. A hit that is a variable name, an alias name or a placeholder is recorded as such with the line that produced it; a hit that is a value fails the gate.

### G-6 — field-list fidelity

- [ ] **The seven entity tables carry exactly the 53 columns of prompt section 1.0, with the specified types, lengths and mandatory flags — no additions, no omissions.** The evidence for this gate is the field-by-field walk of [criterion 1](#criterion-1--all-seven-tables-exist-with-100--of-their-fields): all 53 rows of that section filled, plus `GATE-COL-01` from [`./validation-gates.md`](./validation-gates.md), which counts the entity tables' column records on the instance.

  **Evidence to record:** the criterion 1 completion state — 53 of 53 rows filled and matching — and the `GATE-COL-01` record count.

  **Pass condition:** all 53 rows match on name, type, length and mandatory flag, and `GATE-COL-01` returns exactly `53` records. A count above 53 breaches the binding-and-complete field list as surely as a count below it.

### G-7 — deliverable completeness

- [ ] **Every file the plan lists as created exists, and the single updated file is updated.** Twenty-nine created files and one updated file. Evidence: the **Present** column of the table below, filled group by group, and the path of anything missing.

  | # | Group | Files | Count | Present |
  | --- | --- | --- | --: | --- |
  | 1 | Package root | `../README.md` | 1 | |
  | 2 | Update Set | `../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml` | 1 | |
  | 3 | Scripts | `../scripts/validate_update_set_xml.py` | 1 | |
  | 4 | Package docs | `./validation-gates.md`, `./validation-checklist.md`, `./manual-build-instructions.md`, `./data-model.md`, `./access-control.md`, `./api-reference.md`, `./deployment-runbook.md`, `./gaps-and-flags.md` | 8 | |
  | 5 | Manual-build guides | `./manual-build/01-connection-credential-aliases.md` through `./manual-build/06-staging-table-csv-import.md` | 6 | |
  | 6 | Sample data | `../sample-data/README.md` plus the six CSV files | 7 | |
  | 7 | Governance | `../../docs/review/CRITICAL_DECISIONS.md`, `../../docs/decisions/DECISION_LOG.md`, `../../docs/decisions/TRACEABILITY_MATRIX.md` | 3 | |
  | 8 | Executive deck | `../../blitzy-deck/boston-startup-tracker-servicenow-executive-summary.html`, `../../blitzy-deck/references/blitzy-reveal-theme.css` | 2 | |
  | | **Created total** | | **29** | |
  | 9 | Updated | the repository root `README.md`, carrying a pointer to this package and the supersession notice on the legacy stack | 1 | |

  **Evidence to record:** the observed file count per group and the path of anything missing. Record the root `README.md` change as the section added and the three passages marked superseded.

  **Pass condition:** all 29 created files present, the root `README.md` updated, and no file outside this set created or modified.

### G-8 — deck structure

- [ ] **The executive deck contains between 12 and 18 `<section>` elements.** Open [`../../blitzy-deck/boston-startup-tracker-servicenow-executive-summary.html` (planned)](../../blitzy-deck/boston-startup-tracker-servicenow-executive-summary.html) in a browser and count the top-level slide sections. **Evidence:** the counted number, and the count reported by a static search of the file.

- [ ] **Every section carries at least one non-text visual element** — a Mermaid diagram, a KPI card, a styled table or a Lucide SVG icon. **Evidence:** a per-section list naming the visual each section carries. A section with no visual fails the gate by itself.

- [ ] **No emoji appears anywhere in the deck.** All icons are Lucide SVG, referenced through the `data-lucide` attribute. **Evidence:** the search performed for emoji code points and its hit count, which must be zero, plus the count of `data-lucide` references.

- [ ] **The three pinned library versions are referenced exactly:** reveal.js **5.1.0**, Mermaid **11.4.0**, Lucide **0.460.0**. **Evidence:** the three source URLs copied from the deck.

- [ ] **The three font families are referenced exactly:** **Inter**, **Space Grotesk** and **Fira Code**, loaded through a Google Fonts link. **Evidence:** the font link copied from the deck, with the weights it requests.

  **Pass condition:** the section count is within 12 to 18 inclusive, every section carries a visual, the emoji hit count is zero, and all three library versions and all three font families are present as specified.

### G-9 — governance completeness

- [ ] **The decision log covers every decision the plan names.** [`../../docs/decisions/DECISION_LOG.md` (planned)](../../docs/decisions/DECISION_LOG.md) is a Markdown table carrying the four mandated columns — what was decided, what alternatives existed, why this choice was made, and what risks it carries — with one row per non-trivial decision. **Evidence:** the row count, the four column headers as written, and a spot check that each of the deviations this package cross-references to the log has a row: the eleven-gate core within sixteen gates, the metadata-only gate targets, the participating-investors projection, the run-time creation of the impersonation users, the pre-seeded rate-limit counter, the two provenance surfaces, the hourly trigger with an elapsed-time guard, the query-parameter portal routing and the 1024-pixel floor.

- [ ] **The traceability matrix has no gap in either direction.** [`../../docs/decisions/TRACEABILITY_MATRIX.md` (planned)](../../docs/decisions/TRACEABILITY_MATRIX.md) resolves legacy construct to platform artifact and requirement to platform artifact, and resolves back the other way, so no artifact exists without a justifying requirement and no requirement exists without an artifact. **Evidence:** the row count in each direction and the count of unresolved entries, which must be zero on both sides.

- [ ] **The critical-decisions document holds exactly five risk-ordered entries whose decisions all appear in the log.** **Evidence:** the five entry titles in the order they appear, their risk levels, and confirmation that each maps to a row of the decision log.

  **Pass condition:** the decision log carries its four columns with no named decision missing, the matrix has zero unresolved entries in either direction, and the review document holds exactly five entries ordered by risk with every one present in the log.

### Section A roll-up

Nine gates. All nine are required; there is no partial pass and no waiver.

| Gate | Subject | Result | Timestamp (UTC) | Evidence note |
| --- | --- | --- | --- | --- |
| `G-1` | Outer update-set well-formedness | | | |
| `G-2` | Nested per-record payload well-formedness | | | |
| `G-3` | Referential integrity | | | |
| `G-4` | Scope containment | | | |
| `G-5` | Secret hygiene | | | |
| `G-6` | Field-list fidelity, 53 columns | | | |
| `G-7` | Deliverable completeness, 29 created and 1 updated | | | |
| `G-8` | Deck structure, 12 to 18 sections | | | |
| `G-9` | Governance completeness | | | |
| **Aggregate** | | | | **9 of 9 gates required** |

Record `pass` or `fail` in **Result**, the time of the check in **Timestamp (UTC)** in `YYYY-MM-DD HH:MM:SS` form, and the observed figures in **Evidence note**. For a failing gate also record what was corrected and the passing re-run.

## B — deployment gates

These run **during** the deployment, against the instance, in the sequence [`./deployment-runbook.md`](./deployment-runbook.md) specifies: validate the XML, three pre-flight checks, upload, poll until loaded, preview and poll until previewed, require the error-type preview-problem set to be empty, the two pre-commit checks, commit, then the post-commit gates. Every assertion, target, query and pass condition is specified in [`./validation-gates.md`](./validation-gates.md); this section records the outcome and is not a second definition of them.

**This is the only section of this checklist that can trigger the rollback.** The rollback deletes the `x_bst_startuptrk` scope and cascades its tables, roles and flows. **It is irreversible, and no step of the runbook restores what it removes.** It is triggered only by the conditions the runbook documents: a commit failure, or a post-commit gate failure other than `GATE-SEC-04`. Record the specific gate that triggered it before it is issued.

### B1 — the import sequence

- [ ] **Gates G-1 and G-2 passed before the file was uploaded.** A non-zero validator exit blocks the upload. Evidence: copy the result from [section A](#a--pre-delivery-gates-g-1-to-g-9).
- [ ] **All pre-flight checks passed.** Evidence: for each, the request issued and the status or record count observed — instance reachable with valid credentials, scope existence logged, instance not mid-upgrade, and the release at or above the required floor.
- [ ] **ATF execution is enabled on the instance and a test-designer role is held.** The runbook asserts this **before** the import, so the condition is discovered before any deployment work is done. Without it every suite of the coverage gate is unrunnable. Evidence: the ATF runner property value and the roles held.
- [ ] **The upload returned a retrieved update set and its `sys_id` was captured.** Evidence: the `sys_id`, recorded in the sign-off header.
- [ ] **The retrieved update set reached the loaded state.** Evidence: the state observed and the elapsed poll time.
- [ ] **The preview completed.** Evidence: the state observed and the elapsed poll time.
- [ ] **The error-type preview-problem set is empty.** This is also the evidence for pre-delivery gate [G-3](#g-3--referential-integrity). Evidence: the `result` array and its length. Record the warning-type set alongside it; warnings are logged and do not abort.
- [ ] **The commit completed.** Evidence: the state observed and the elapsed poll time.

### B2 — the two pre-commit checks

Read **after** the preview problems and **before** the commit. They are preconditions of the post-commit gates, not members of them: an Update Set whose customer updates did not attach to its header commits without applying any record, and every post-commit gate then fails against an instance where nothing was installed.

| Check | Assertion | Result | Timestamp (UTC) | Observed value |
| --- | --- | --- | --- | --- |
| `PRE-COMMIT-01` | Every customer update in the uploaded file attached to the retrieved update set header — the count equals the file's update-record count | | | |
| `PRE-COMMIT-02` | The completed preview found that many records to apply — state is `previewed` and the summary equals the same count | | | |

- [ ] **Both pre-commit checks pass, against the update-record count the validator reported.** Evidence: the count from the validator's stage 1, and the two observed values above, which must equal it. Neither check triggers the rollback; a failure means the commit does not happen, and the remedy is to remove the retrieved update set, correct the XML and restart the sequence.

### B3 — the sixteen post-commit gates

[`./validation-gates.md`](./validation-gates.md) defines **sixteen** gates. **All sixteen are required; there is no partial pass and no waiver.** Within them, the **eleven-gate core** — the seven entity-table gates, the three role-record gates and the one scope-record gate — is named separately so that a partial gate run is visible as such. The remaining five are the column-count gate and the four security gates.

**The eleven-gate core.**

| # | Gate | Assertion | Result | Timestamp (UTC) | Observed |
| --- | --- | --- | --- | --- | --- |
| 1 | `GATE-TBL-01` | `x_bst_startuptrk_startup` table record exists | | | |
| 2 | `GATE-TBL-02` | `x_bst_startuptrk_founder` table record exists | | | |
| 3 | `GATE-TBL-03` | `x_bst_startuptrk_executive` table record exists | | | |
| 4 | `GATE-TBL-04` | `x_bst_startuptrk_investor` table record exists | | | |
| 5 | `GATE-TBL-05` | `x_bst_startuptrk_fundinground` table record exists | | | |
| 6 | `GATE-TBL-06` | `x_bst_startuptrk_jobposting` table record exists | | | |
| 7 | `GATE-TBL-07` | `x_bst_startuptrk_newsarticle` table record exists | | | |
| 8 | `GATE-ROLE-01` | Exactly one role record named `x_bst_startuptrk.admin` | | | |
| 9 | `GATE-ROLE-02` | Exactly one role record named `x_bst_startuptrk.user` | | | |
| 10 | `GATE-ROLE-03` | Exactly one role record named `x_bst_startuptrk.premium_user` | | | |
| 11 | `GATE-SCOPE-01` | Exactly one scope record for `x_bst_startuptrk` | | | |
| | **Core aggregate** | | | | **11 of 11 required** |

**The remaining five.**

| # | Gate | Assertion | Result | Timestamp (UTC) | Observed |
| --- | --- | --- | --- | --- | --- |
| 12 | `GATE-COL-01` | The seven entity tables carry exactly 53 columns between them | | | |
| 13 | `GATE-SEC-01` | All ten application tables are reachable from the `x_bst_startuptrk` scope only | | | |
| 14 | `GATE-SEC-02` | The native Table API is disabled on all ten application tables | | | |
| 15 | `GATE-SEC-03` | Both REST endpoint access controls committed | | | |
| 16 | `GATE-SEC-04` | The instance refuses XML entity resolution | | | |
| | **Full aggregate** | | | | **16 of 16 required** |

7 table gates + 1 column-count gate + 3 role gates + 1 scope gate + 4 security gates = 16, of which the core is 7 + 3 + 1 = 11.

- [ ] **The eleven-gate core passes, 11 of 11.** Evidence: rows 1 to 11 above. No manual-build guide starts before every one of them reports a pass.
- [ ] **All sixteen gates pass, 16 of 16.** Evidence: rows 1 to 16 above.
- [ ] **A gate that returned a server error was retried exactly once after 30 seconds, and the outcome recorded is the retry's.** Evidence: for any such gate, the first status, the wait and the retry's status, recorded in the same row.
- [ ] **`GATE-SEC-04` is the one gate whose failure does not trigger the rollback.** Its condition is instance configuration rather than an artifact of this Update Set: the remedy is to set the property on the instance and re-run the gate. Evidence: if it failed, the two property values observed and the corrective action taken.
- [ ] **No rollback was required.** If one was, record the gate that triggered it, the report made before it was issued, and the outcome of the deletion and its confirmation. Evidence: the trigger and the outcome, or the explicit statement that no rollback was performed.

## Criterion 1 — all seven tables exist with 100 % of their fields

> **Prompt section 10.0, criterion 1.** All 7 tables exist with 100 % of their fields, **verified field by field**.

**The counting rule.** The count of seven is evaluated against the **seven entity tables** listed below. The join table `x_bst_startuptrk_m2m_round_investor`, the staging table `x_bst_startuptrk_ingest_staging` and the rate-limit counter table `x_bst_startuptrk_rate_limit_counter` are **supporting artifacts**; they are listed separately under [Supporting tables](#supporting-tables-not-counted-in-the-seven) and are not part of this count, and their columns are not part of the 53. The resolution of the count is recorded in [`../../docs/decisions/DECISION_LOG.md` (planned)](../../docs/decisions/DECISION_LOG.md).

### 1a — table existence, seven gates

The seven table gates of [`./validation-gates.md`](./validation-gates.md) establish existence. Each reads the table's own `sys_db_object` record and passes on exactly one record. Copy each result from the section B roll-up rather than re-running the request.

- [ ] **`GATE-TBL-01` — `x_bst_startuptrk_startup` exists.** Evidence: HTTP status and `result` record count.
- [ ] **`GATE-TBL-02` — `x_bst_startuptrk_founder` exists.** Evidence: HTTP status and `result` record count.
- [ ] **`GATE-TBL-03` — `x_bst_startuptrk_executive` exists.** Evidence: HTTP status and `result` record count.
- [ ] **`GATE-TBL-04` — `x_bst_startuptrk_investor` exists.** Evidence: HTTP status and `result` record count.
- [ ] **`GATE-TBL-05` — `x_bst_startuptrk_fundinground` exists.** Evidence: HTTP status and `result` record count.
- [ ] **`GATE-TBL-06` — `x_bst_startuptrk_jobposting` exists.** Evidence: HTTP status and `result` record count.
- [ ] **`GATE-TBL-07` — `x_bst_startuptrk_newsarticle` exists.** Evidence: HTTP status and `result` record count.
- [ ] **`GATE-COL-01` — the seven entity tables carry exactly 53 columns between them.** Evidence: the `result` record count, which must read exactly `53`. This is the count-level check; the walk below is the field-level one, and both are required.

### 1b — the field-by-field walk, all 53 columns

The **Expected** columns below are transcribed from [`./data-model.md`](./data-model.md), which is authoritative for the dictionary. The operator fills the three **Observed** columns and **Result** from the instance dictionary, one row at a time. A single row left unfilled leaves this criterion incomplete.

Read the dictionary for one table with:

```text
GET {SERVICENOW_INSTANCE_URL}/api/now/table/sys_dictionary?sysparm_query=name=<table>^elementISNOTEMPTY&sysparm_fields=element,internal_type,max_length,mandatory&sysparm_limit=100
Authorization: Basic base64({SERVICENOW_USERNAME}:{SERVICENOW_PASSWORD})
Accept: application/json
```

The same values are readable in the platform interface under **All** > **System Definition** > **Dictionary**, filtered on **Table**. Either route is acceptable; record which was used.

Notation in the **Mandatory** column: **M** means the dictionary carries `mandatory` true; a dash means it does not. A reference column's expected length is `32`, the width of a `sys_id`. A column whose type carries no length — `integer`, `boolean`, `currency`, `glide_date` — shows a dash, and the observed length is recorded as returned.

Rows are numbered continuously from 1 to 53 across all seven blocks, so the total is verifiable without adding up the blocks.

**P** beside a column name marks it premium-gated. The seven so marked are the same seven fields [criterion 2](#criterion-2--all-three-roles-enforce-field-level-acls-on-100--of-the-seven-premium-fields) tests per role. This walk verifies that each of them **exists with the declared type, length and mandatory flag**; whether a given role may read it is criterion 2's subject and is not asserted here.

#### Table 1 of 7 — `x_bst_startuptrk_startup` (Startup), 12 columns, rows 1 to 12

- [ ] **All 12 columns of `x_bst_startuptrk_startup` verified.** Rows 1 to 12 below are filled and every **Result** reads `match`.

| # | Column | Expected type | Length | Mandatory | Observed type | Observed length | Observed mandatory | Result |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `name` | `string` | 100 | M | | | | |
| 2 | `description` | `string` | 4000 | — | | | | |
| 3 | `industry` | `string`, choice list | 40 | — | | | | |
| 4 | `founded_year` | `integer` | — | — | | | | |
| 5 | `headquarters_location` | `string` | 100 | M | | | | |
| 6 | `website` | `string` | 255 | — | | | | |
| 7 | `logo_url` | `string` | 255 | — | | | | |
| 8 | `funding_stage` | `string`, choice list | 40 | — | | | | |
| 9 | `total_funding_usd` **P** | `currency` | — | — | | | | |
| 10 | `active` | `boolean` | — | M | | | | |
| 11 | `institutional_funding_last_5yrs` **P** | `boolean` | — | — | | | | |
| 12 | `employee_count_range` | `string`, choice list | 20 | — | | | | |

#### Table 2 of 7 — `x_bst_startuptrk_founder` (Founder), 6 columns, rows 13 to 18

- [ ] **All 6 columns of `x_bst_startuptrk_founder` verified.** Rows 13 to 18 below are filled and every **Result** reads `match`.

| # | Column | Expected type | Length | Mandatory | Observed type | Observed length | Observed mandatory | Result |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 13 | `name` | `string` | 100 | M | | | | |
| 14 | `startup` | `reference` to `x_bst_startuptrk_startup` | 32 | M | | | | |
| 15 | `title` | `string`, choice list | 40 | — | | | | |
| 16 | `bio` | `string` | 2000 | — | | | | |
| 17 | `linkedin_url` | `string` | 255 | — | | | | |
| 18 | `contact_email` **P** | `string` | 100 | — | | | | |

#### Table 3 of 7 — `x_bst_startuptrk_executive` (Executive), 6 columns, rows 19 to 24

- [ ] **All 6 columns of `x_bst_startuptrk_executive` verified.** Rows 19 to 24 below are filled and every **Result** reads `match`.

| # | Column | Expected type | Length | Mandatory | Observed type | Observed length | Observed mandatory | Result |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 19 | `name` | `string` | 100 | M | | | | |
| 20 | `startup` | `reference` to `x_bst_startuptrk_startup` | 32 | M | | | | |
| 21 | `title` | `string`, choice list | 40 | — | | | | |
| 22 | `bio` | `string` | 2000 | — | | | | |
| 23 | `linkedin_url` | `string` | 255 | — | | | | |
| 24 | `contact_email` **P** | `string` | 100 | — | | | | |

#### Table 4 of 7 — `x_bst_startuptrk_investor` (Investor), 6 columns, rows 25 to 30

- [ ] **All 6 columns of `x_bst_startuptrk_investor` verified.** Rows 25 to 30 below are filled and every **Result** reads `match`.

| # | Column | Expected type | Length | Mandatory | Observed type | Observed length | Observed mandatory | Result |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 25 | `name` | `string` | 100 | M | | | | |
| 26 | `type` | `string`, choice list | 30 | — | | | | |
| 27 | `focus_areas` | `string`, multi-choice | 255 | — | | | | |
| 28 | `website` | `string` | 255 | — | | | | |
| 29 | `aum_usd` **P** | `currency` | — | — | | | | |
| 30 | `portfolio_count` | `integer`, read-only | — | — | | | | |

#### Table 5 of 7 — `x_bst_startuptrk_fundinground` (Funding round), 8 columns, rows 31 to 38

- [ ] **All 8 columns of `x_bst_startuptrk_fundinground` verified.** Rows 31 to 38 below are filled and every **Result** reads `match`.

| # | Column | Expected type | Length | Mandatory | Observed type | Observed length | Observed mandatory | Result |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 31 | `startup` | `reference` to `x_bst_startuptrk_startup` | 32 | M | | | | |
| 32 | `round_type` | `string`, choice list | 40 | — | | | | |
| 33 | `amount_usd` **P** | `currency` | — | — | | | | |
| 34 | `round_date` | `glide_date` | — | M | | | | |
| 35 | `lead_investor` | `reference` to `x_bst_startuptrk_investor` | 32 | — | | | | |
| 36 | `participating_investors` | `glide_list` to `x_bst_startuptrk_investor`, read-only | 4000 | — | | | | |
| 37 | `valuation_usd` **P** | `currency` | — | — | | | | |
| 38 | `source_url` | `string` | 255 | — | | | | |

#### Table 6 of 7 — `x_bst_startuptrk_jobposting` (Job posting), 9 columns, rows 39 to 47

- [ ] **All 9 columns of `x_bst_startuptrk_jobposting` verified.** Rows 39 to 47 below are filled and every **Result** reads `match`.

| # | Column | Expected type | Length | Mandatory | Observed type | Observed length | Observed mandatory | Result |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 39 | `startup` | `reference` to `x_bst_startuptrk_startup` | 32 | M | | | | |
| 40 | `title` | `string` | 150 | M | | | | |
| 41 | `department` | `string`, choice list | 40 | — | | | | |
| 42 | `location` | `string` | 100 | — | | | | |
| 43 | `remote_type` | `string`, choice list | 20 | — | | | | |
| 44 | `seniority` | `string`, choice list | 20 | — | | | | |
| 45 | `posted_date` | `glide_date` | — | — | | | | |
| 46 | `url` | `string` | 255 | — | | | | |
| 47 | `active` | `boolean` | — | — | | | | |

#### Table 7 of 7 — `x_bst_startuptrk_newsarticle` (News article), 6 columns, rows 48 to 53

- [ ] **All 6 columns of `x_bst_startuptrk_newsarticle` verified.** Rows 48 to 53 below are filled and every **Result** reads `match`.

| # | Column | Expected type | Length | Mandatory | Observed type | Observed length | Observed mandatory | Result |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 48 | `startup` | `reference` to `x_bst_startuptrk_startup` | 32 | M | | | | |
| 49 | `title` | `string` | 255 | M | | | | |
| 50 | `source` | `string` | 100 | — | | | | |
| 51 | `url` | `string` | 255 | — | | | | |
| 52 | `published_date` | `glide_date` | — | — | | | | |
| 53 | `summary` | `string` | 2000 | — | | | | |

### 1c — the walk roll-up

- [ ] **All 53 rows filled, all 53 reading `match`.** Evidence: the per-table counts below, which must sum to 53, and the count of rows reading anything other than `match`, which must be zero.

| # | Table | Rows | Columns expected | Columns matching | Discrepancies |
| --- | --- | --- | --: | --: | --- |
| 1 | `x_bst_startuptrk_startup` | 1 to 12 | 12 | | |
| 2 | `x_bst_startuptrk_founder` | 13 to 18 | 6 | | |
| 3 | `x_bst_startuptrk_executive` | 19 to 24 | 6 | | |
| 4 | `x_bst_startuptrk_investor` | 25 to 30 | 6 | | |
| 5 | `x_bst_startuptrk_fundinground` | 31 to 38 | 8 | | |
| 6 | `x_bst_startuptrk_jobposting` | 39 to 47 | 9 | | |
| 7 | `x_bst_startuptrk_newsarticle` | 48 to 53 | 6 | | |
| | **Total** | | **53** | | |

12 + 6 + 6 + 6 + 8 + 9 + 6 = 53.

- [ ] **No eighth column exists on any entity table.** A column present on the instance that appears in no row above is an addition, and an addition breaches the binding-and-complete field list exactly as an omission does. Evidence: for each table, the dictionary column count observed against the expected count in the table above, and the name of any extra column found. The platform's own `sys_id`, `sys_created_on`, `sys_created_by`, `sys_updated_on`, `sys_updated_by` and `sys_mod_count` columns are supplied for every table and are **not** counted here.

### Supporting tables, not counted in the seven

Three tables support the application and are **excluded from the count of seven and from the 53 columns**. They are recorded here so that their presence is visible and cannot be mistaken for an eighth entity table.

- [ ] **`x_bst_startuptrk_m2m_round_investor` exists** — the join table that is authoritative for participating investors. Evidence: dictionary record present, and its two reference columns observed.
- [ ] **`x_bst_startuptrk_ingest_staging` exists** — the staging table both flows read on their fallback branch. Evidence: dictionary record present, and the column count observed against [`./data-model.md`](./data-model.md).
- [ ] **`x_bst_startuptrk_rate_limit_counter` exists with all five of its columns** — `window_key`, `caller`, `api_resource`, `window_start` and `request_count`. Evidence: the five column names observed. [Criterion 3](#criterion-3--all-six-rest-resources-return-correct-paginated-responses-and-a-429-with-a-retry-value) writes to this table.
- [ ] **`GATE-SEC-01` and `GATE-SEC-02` cover all ten tables.** Both gates return exactly 10 records, which is the entity seven plus these three. Evidence: the two record counts, copied from the section B roll-up.

### 1d — the seven table-CRUD suites

Seven Automated Test Framework suites, one per entity table, one test in each, built by [`./manual-build/05-atf-test-suites.md`](./manual-build/05-atf-test-suites.md). Every test exercises **insert, update, query and delete** with **mandatory-field** and **choice-value** assertions, and every record step runs with security enforced.

- [ ] **`BST CRUD suite — startup`** passes. Evidence: suite result name, status, timestamp.
- [ ] **`BST CRUD suite — founder`** passes. Evidence: suite result name, status, timestamp.
- [ ] **`BST CRUD suite — executive`** passes. Evidence: suite result name, status, timestamp.
- [ ] **`BST CRUD suite — investor`** passes. Evidence: suite result name, status, timestamp.
- [ ] **`BST CRUD suite — fundinground`** passes. Evidence: suite result name, status, timestamp.
- [ ] **`BST CRUD suite — jobposting`** passes. Evidence: suite result name, status, timestamp.
- [ ] **`BST CRUD suite — newsarticle`** passes. Evidence: suite result name, status, timestamp.

| # | Suite | Table covered | Result | Timestamp (UTC) | Suite result record |
| --- | --- | --- | --- | --- | --- |
| 1 | `BST CRUD suite — startup` | `x_bst_startuptrk_startup` | | | |
| 2 | `BST CRUD suite — founder` | `x_bst_startuptrk_founder` | | | |
| 3 | `BST CRUD suite — executive` | `x_bst_startuptrk_executive` | | | |
| 4 | `BST CRUD suite — investor` | `x_bst_startuptrk_investor` | | | |
| 5 | `BST CRUD suite — fundinground` | `x_bst_startuptrk_fundinground` | | | |
| 6 | `BST CRUD suite — jobposting` | `x_bst_startuptrk_jobposting` | | | |
| 7 | `BST CRUD suite — newsarticle` | `x_bst_startuptrk_newsarticle` | | | |
| | **Aggregate** | | | | **7 of 7 required** |

- [ ] **Every record step in these seven suites ran with security enforced.** A record step with security not enforced runs unrestricted and the suite reports success while asserting nothing about the access-control layer. Evidence: for each suite, confirmation that every `Record Insert`, `Record Update`, `Record Query`, `Record Delete` and `Record Validation` step carries `enforce_security` true.

### Criterion 1 — pass condition

- [ ] **Seven tables present.** `GATE-TBL-01` through `GATE-TBL-07` all pass. Evidence: section [1a](#1a--table-existence-seven-gates), seven results.
- [ ] **53 columns matching the binding list exactly**, on name, type, length and mandatory flag — no additions, no omissions — with `GATE-COL-01` returning exactly `53`. Evidence: section [1b](#1b--the-field-by-field-walk-all-53-columns), 53 rows, and the roll-up of section [1c](#1c--the-walk-roll-up).
- [ ] **Seven table-CRUD suites passing**, 7 of 7. Evidence: the suite table of section [1d](#1d--the-seven-table-crud-suites).

Criterion 1 is met when, and only when, all three hold. This criterion also supplies the evidence for pre-delivery gate [G-6](#g-6--field-list-fidelity). The dictionary this walk is checked against is [`./data-model.md`](./data-model.md).

## Criterion 2 — all three roles enforce field-level ACLs on 100 % of the seven premium fields

> **Prompt section 10.0, criterion 2.** All 3 roles enforce field-level ACLs on 100 % of the 7 premium fields, **verified per role per field**.

### 2a — the impersonation requirement

> **Every check in this criterion must be performed under impersonation, by a user holding exactly one scoped role and none of the elevated platform roles.**
>
> **A check performed as the instance administrator does not test enforcement.** Record access controls carry an administrator override, and every operator of a personal developer instance holds the platform administrator role. A read or a walkthrough conducted as the instance administrator displays all seven premium fields and appears to prove enforcement that was never tested at all. **Evidence gathered that way is void and must not be recorded in this document.**

The requirement is procedural and applies to every one of the twenty-one cells below, to the omission spot check, to the control-column check and to the criterion 5 portal walkthrough. Its resolution is recorded in [`../../docs/decisions/DECISION_LOG.md` (planned)](../../docs/decisions/DECISION_LOG.md), and it is inventoried as a flag in [`./gaps-and-flags.md`](./gaps-and-flags.md).

- [ ] **Three purpose-created users exist for the run, one per role.** Each holds **exactly one** of `x_bst_startuptrk.admin`, `x_bst_startuptrk.premium_user` and `x_bst_startuptrk.user`. Evidence: the three user records and the single role held by each.
- [ ] **None of the three holds an elevated platform role** — not the platform `admin` role, not `security_admin`, not `maint`. The scoped role `x_bst_startuptrk.admin` and the platform administrator role are different roles; the test user holds the scoped one and not the platform one. Evidence: the full role set read back for each of the three users, including roles inherited by containment.
- [ ] **The role set was verified before the read outcomes were trusted.** The suite verifies each user's role set in its own step, and that verification is what makes a denial attributable to the field-level control rather than to a missing grant. Evidence: the two role-set verification step outputs from the suite result.
- [ ] **The three users are created by the test setup steps at run time**, not shipped in the Update Set, because `sys_user` sits outside the application scope. Evidence: confirmation that the delivered Update Set carries no `sys_user` record, and the setup-step output naming each user created.

### 2b — the 21 cells, seven premium fields by three roles

**21 tests**, the full cross-product, built as suite `BST ACL suite — premium fields by role` per [`./manual-build/05-atf-test-suites.md`](./manual-build/05-atf-test-suites.md). Every cell is a separate test with its own result, so a single failing cell is visible by name. Expected outcomes: under `x_bst_startuptrk.admin` the field **reads**, under `x_bst_startuptrk.premium_user` the field **reads**, under `x_bst_startuptrk.user` the field is **denied** and its key is **absent** from the response object. Fourteen cells expect a read; seven expect a denial.

- [ ] **Field 1 of 7 — `x_bst_startuptrk_startup.total_funding_usd`, all three cells.**

| Cell | Role | Expected outcome | Result | Test result record |
| --- | --- | --- | --- | --- |
| `ACL-1.1` | `x_bst_startuptrk.admin` | Reads — value returned, key present | | |
| `ACL-1.2` | `x_bst_startuptrk.premium_user` | Reads — value returned, key present | | |
| `ACL-1.3` | `x_bst_startuptrk.user` | **DENIED** — key absent from the response object | | |

- [ ] **Field 2 of 7 — `x_bst_startuptrk_startup.institutional_funding_last_5yrs`, all three cells.**

| Cell | Role | Expected outcome | Result | Test result record |
| --- | --- | --- | --- | --- |
| `ACL-2.1` | `x_bst_startuptrk.admin` | Reads — value returned, key present | | |
| `ACL-2.2` | `x_bst_startuptrk.premium_user` | Reads — value returned, key present | | |
| `ACL-2.3` | `x_bst_startuptrk.user` | **DENIED** — key absent from the response object | | |

- [ ] **Field 3 of 7 — `x_bst_startuptrk_founder.contact_email`, all three cells.**

| Cell | Role | Expected outcome | Result | Test result record |
| --- | --- | --- | --- | --- |
| `ACL-3.1` | `x_bst_startuptrk.admin` | Reads — value returned, key present | | |
| `ACL-3.2` | `x_bst_startuptrk.premium_user` | Reads — value returned, key present | | |
| `ACL-3.3` | `x_bst_startuptrk.user` | **DENIED** — key absent from the response object | | |

- [ ] **Field 4 of 7 — `x_bst_startuptrk_executive.contact_email`, all three cells.** This is a distinct access control on a second table; it is not covered by field 3 and neither covers the other.

| Cell | Role | Expected outcome | Result | Test result record |
| --- | --- | --- | --- | --- |
| `ACL-4.1` | `x_bst_startuptrk.admin` | Reads — value returned, key present | | |
| `ACL-4.2` | `x_bst_startuptrk.premium_user` | Reads — value returned, key present | | |
| `ACL-4.3` | `x_bst_startuptrk.user` | **DENIED** — key absent from the response object | | |

- [ ] **Field 5 of 7 — `x_bst_startuptrk_investor.aum_usd`, all three cells.**

| Cell | Role | Expected outcome | Result | Test result record |
| --- | --- | --- | --- | --- |
| `ACL-5.1` | `x_bst_startuptrk.admin` | Reads — value returned, key present | | |
| `ACL-5.2` | `x_bst_startuptrk.premium_user` | Reads — value returned, key present | | |
| `ACL-5.3` | `x_bst_startuptrk.user` | **DENIED** — key absent from the response object | | |

- [ ] **Field 6 of 7 — `x_bst_startuptrk_fundinground.amount_usd`, all three cells.**

| Cell | Role | Expected outcome | Result | Test result record |
| --- | --- | --- | --- | --- |
| `ACL-6.1` | `x_bst_startuptrk.admin` | Reads — value returned, key present | | |
| `ACL-6.2` | `x_bst_startuptrk.premium_user` | Reads — value returned, key present | | |
| `ACL-6.3` | `x_bst_startuptrk.user` | **DENIED** — key absent from the response object | | |

- [ ] **Field 7 of 7 — `x_bst_startuptrk_fundinground.valuation_usd`, all three cells.**

| Cell | Role | Expected outcome | Result | Test result record |
| --- | --- | --- | --- | --- |
| `ACL-7.1` | `x_bst_startuptrk.admin` | Reads — value returned, key present | | |
| `ACL-7.2` | `x_bst_startuptrk.premium_user` | Reads — value returned, key present | | |
| `ACL-7.3` | `x_bst_startuptrk.user` | **DENIED** — key absent from the response object | | |

### 2c — the cell roll-up

- [ ] **21 of 21 cells correct.** Evidence: the counts below, and the name of every cell whose result is anything other than a pass.

| Expectation | Cells | Count | Correct | Cells not correct |
| --- | --- | --: | --: | --- |
| Reads — administrator | `ACL-1.1` to `ACL-7.1` | 7 | | |
| Reads — premium user | `ACL-1.2` to `ACL-7.2` | 7 | | |
| Denied — base user | `ACL-1.3` to `ACL-7.3` | 7 | | |
| | **Total** | **21** | | |

7 fields x 3 roles = 21. 14 cells expect a read, 7 expect a denial. A cell that is missing, failing or in an error state counts as not correct.

- [ ] **The suite result itself passes.** Evidence: the `BST ACL suite — premium fields by role` suite result name, status and timestamp.

### 2d — omitted, not nulled

- [ ] **For a base-role caller, a denied field key is absent from the API response object.** It is **not** present with an empty string, **not** present with a null, and **not** present with a placeholder. Test this on a live response, not only inside the suite: call a list operation as a caller holding only `x_bst_startuptrk.user` and inspect the raw JSON of one record object.

  **Evidence to record:** the resource called, the record object as returned, and the explicit result of testing for key presence on each premium key of that resource — for `/startups`, `total_funding_usd` and `institutional_funding_last_5yrs`.

  **Pass condition:** the premium key does not appear in the object at all. A key present with an empty value fails this item even though the value discloses nothing, because the contract is omission.

- [ ] **A non-premium column on the same record still reads under the base role.** Read a control column — `x_bst_startuptrk_startup.headquarters_location` serves — in the same call. It must return a value.

  **Evidence to record:** the control column name and the value returned.

  **Pass condition:** the control column returns a value. That establishes that the table-level read grant passed and that the denial came from the field-level control rather than from nothing being readable at all. Both layers are load-bearing: without the table-level grant nothing is readable and the field-level rules never evaluate, and without the field-level rules every premium field is readable by every role.

### Criterion 2 — pass condition

- [ ] **21 of 21 assertions correct**, every one gathered under impersonation by a user holding exactly one scoped role and none of the elevated platform roles. Evidence: the 21 cell rows of section [2b](#2b--the-21-cells-seven-premium-fields-by-three-roles), the roll-up of section [2c](#2c--the-cell-roll-up), and the four precondition ticks of section [2a](#2a--the-impersonation-requirement).
- [ ] **The omission spot check passes** — the denied key is absent from the response object rather than present with an empty value. Evidence: section [2d](#2d--omitted-not-nulled), the recorded record object.
- [ ] **The control-column check passes** — a non-premium column reads under the base role in the same call. Evidence: section [2d](#2d--omitted-not-nulled), the control column and the value returned.

Criterion 2 is met when, and only when, all three hold. The matrix, the five ACL layers and the verification procedure are specified in [`./access-control.md`](./access-control.md); the twenty-one tests, their step sequences and the impersonation technique are specified in [`./manual-build/05-atf-test-suites.md`](./manual-build/05-atf-test-suites.md). The two documents must agree cell for cell with the grid above.

## Criterion 3 — all six REST resources return correct paginated responses and a 429 with a retry value

> **Prompt section 10.0, criterion 3.** All 6 REST resources return correct paginated responses and a `429` with a retry value on rate limit.

**6 ATF tests**, one per logical resource, built as suite `BST REST suite — resources` per [`./manual-build/05-atf-test-suites.md`](./manual-build/05-atf-test-suites.md). The physical base path is **`/api/x_bst_startuptrk/v1/`**. Each test asserts **three** things, so the grid below is 6 resources x 3 assertions = 18 cells.

### 3a — the three assertions, stated once

**Assertion 1 — success response shape.** The call returns `200` and an envelope carrying `result` as an array, `total_count`, `limit` and `offset`. `limit` and `offset` echo the values the API actually applied.

**Assertion 2 — pagination across `sysparm_limit` and `sysparm_offset`, with a `total_count` that agrees with the page contents.** Request the same operation twice, at offset `0` and at the next offset, and assert: the page never exceeds the requested `sysparm_limit`; `total_count` is at least the number of rows returned; `total_count` does not move between pages, because it is a property of the filtered set and not of the page; and no row repeats across the two pages. The bounds are read from two properties — `x_bst_startuptrk.rest.default_limit`, shipped value `20`, applied when `sysparm_limit` does not resolve to a usable value, and `x_bst_startuptrk.rest.max_limit`, shipped value `50`, the largest page the API will serve. A `sysparm_limit` above the maximum is clamped; a `sysparm_offset` above `10000` is refused with `400`.

**Assertion 3 — the `429` body, matching this example exactly:**

```json
{"error": "rate_limit_exceeded", "retry_after": 42}
```

Two members, and no others. `retry_after` is a whole number of seconds — the seconds remaining in the caller's current window, with a floor of `1` — so the value observed will differ from the `42` above while the shape does not. A standard `Retry-After` response header carries the same value and does not alter the body.

- [ ] **The determinism procedure was followed.** Before the request under test, **pre-seed a counter row in `x_bst_startuptrk_rate_limit_counter` already at the configured budget**, so the next single call trips the limit. Seed all five columns — `window_key`, `caller`, `api_resource`, `window_start` and `request_count` — with `window_key` holding the composite `<caller sys_id>|<api resource>|<window start as whole seconds since the epoch>` for the current aligned window, and `request_count` at the value of `x_bst_startuptrk.rest.rate_limit_requests`, shipped as `100`. Evidence: the seeded row's five values and the single request that followed it. The procedure is specified in [`./manual-build/05-atf-test-suites.md`](./manual-build/05-atf-test-suites.md) and recorded in [`../../docs/decisions/DECISION_LOG.md` (planned)](../../docs/decisions/DECISION_LOG.md).
- [ ] **The rate-limit resource token was seeded verbatim.** Accounting is keyed on the resource, and there are **seven** tokens across six resources: `/startups`, `/founders`, `/founders/{startup_id}/executives`, `/investors`, `/funding-rounds`, `/jobs` and `/news`. The nested sub-resource accounts **separately** from `/founders`: seeding `/founders` does not trip the nested path, and seeding the nested token does not trip `/founders`. Evidence: the token seeded for each `429` assertion, all seven listed.

### 3b — the grid, six resources by three assertions

Tick a resource only when all three of its cells carry a recorded result.

- [ ] **Resource 1 of 6 — `/startups`**, endpoint `/api/x_bst_startuptrk/v1/startups`.

| Assertion | What to record | Result |
| --- | --- | --- |
| Success shape | Status, and the four envelope members observed | |
| Pagination | Applied `limit` and `offset`, rows returned, `total_count` at each offset, overlap count | |
| `429` body | The exact body returned and the `retry_after` value | |

  This test carries one further assertion: the seeded startup that **fails** the inclusion criteria must not appear in `result`, and `total_count` must not count it. Record both. The criteria are a query filter applied identically to the result set and to the count, so a disagreement between the two is a defect.

- [ ] **Resource 2 of 6 — `/founders`**, endpoint `/api/x_bst_startuptrk/v1/founders` **and** the nested `/api/x_bst_startuptrk/v1/founders/{startup_id}/executives`.

| Assertion | What to record | Result |
| --- | --- | --- |
| Success shape | Status and envelope members for **both** the top-level path and the nested path | |
| Pagination | Applied `limit` and `offset`, rows, `total_count` and overlap for **both** paths | |
| `429` body | The exact body and `retry_after` for **both** tokens — `/founders` and `/founders/{startup_id}/executives` | |

  Executive records are served only through this nested sub-resource; there is no seventh top-level resource. All three assertions are made twice in this test, once per path.

- [ ] **Resource 3 of 6 — `/investors`**, endpoint `/api/x_bst_startuptrk/v1/investors`.

| Assertion | What to record | Result |
| --- | --- | --- |
| Success shape | Status, and the four envelope members observed | |
| Pagination | Applied `limit` and `offset`, rows returned, `total_count` at each offset, overlap count | |
| `429` body | The exact body returned and the `retry_after` value | |

- [ ] **Resource 4 of 6 — `/funding-rounds`**, endpoint `/api/x_bst_startuptrk/v1/funding-rounds`.

| Assertion | What to record | Result |
| --- | --- | --- |
| Success shape | Status, the four envelope members, and `participating_investors` as a JSON array | |
| Pagination | Applied `limit` and `offset`, rows returned, `total_count` at each offset, overlap count | |
| `429` body | The exact body returned and the `retry_after` value | |

- [ ] **Resource 5 of 6 — `/jobs`**, endpoint `/api/x_bst_startuptrk/v1/jobs`.

| Assertion | What to record | Result |
| --- | --- | --- |
| Success shape | Status, and the four envelope members observed | |
| Pagination | Applied `limit` and `offset`, rows returned, `total_count` at each offset, overlap count | |
| `429` body | The exact body returned and the `retry_after` value | |

- [ ] **Resource 6 of 6 — `/news`**, endpoint `/api/x_bst_startuptrk/v1/news`.

| Assertion | What to record | Result |
| --- | --- | --- |
| Success shape | Status, and the four envelope members observed | |
| Pagination | Applied `limit` and `offset`, rows returned, `total_count` at each offset, overlap count | |
| `429` body | The exact body returned and the `retry_after` value | |

### 3c — the grid roll-up

- [ ] **18 of 18 cells recorded and passing.** Evidence: the counts below, and the resource and assertion of every cell that did not pass.

| Assertion | Resources | Cells | Passing | Cells not passing |
| --- | --- | --: | --: | --- |
| Success response shape | 6 | 6 | | |
| Pagination with an agreeing `total_count` | 6 | 6 | | |
| `429` body with `retry_after` | 6 | 6 | | |
| | **Total** | **18** | | |

6 resources x 3 assertions = 18. The nested sub-resource is asserted inside resource 2 and does not add a seventh row.

- [ ] **The suite result itself passes.** Evidence: the `BST REST suite — resources` suite result name, status and timestamp, and the six named test results.
- [ ] **The REST caller used for this suite holds only `x_bst_startuptrk.user`.** Every `GET` in the suite succeeds under the base role, which is what lets the success-shape assertion also confirm over HTTP that the premium keys are absent from every row. Evidence: the caller's user name and its single role.

### Criterion 3 — pass condition

- [ ] **Six of six resources passing all three assertions** — success shape, pagination with a `total_count` that agrees with the page contents, and the `429` body matching the example exactly. Evidence: the 18 cells of section [3b](#3b--the-grid-six-resources-by-three-assertions) and the roll-up of section [3c](#3c--the-grid-roll-up).
- [ ] **All seven rate-limit tokens exercised**, including the nested executives token separately from `/founders`. Evidence: the seven tokens recorded against the determinism ticks of section [3a](#3a--the-three-assertions-stated-once).

Criterion 3 is met when, and only when, both hold. The pagination contract, the response envelope, the six resources with their 31 operations and the error contracts are specified in [`./api-reference.md`](./api-reference.md).

## Criterion 4 — scheduled flows ingest and clean on the configured cadence with zero unhandled errors

> **Prompt section 10.0, criterion 4.** The scheduled flows ingest and clean Crunchbase and LinkedIn data — or the sample-dataset substitute — on the configured cadence with **zero unhandled errors across three consecutive scheduled runs**.

### 4a — what a scheduled run is

> **A scheduled run is a flow execution that passed the flow's cadence guard and went on to do work.**
>
> **An execution that started, found the configured cadence had not yet elapsed and exited without ingesting is a no-op.** It is not a scheduled run, it does not count towards the three consecutive runs, and it is not evidence of anything. **No-op executions must not appear in the evidence below.**

This definition is load-bearing for the zero-unhandled-errors count: with the shipped cadence of 24 hours and an hourly trigger, roughly twenty-three of every twenty-four executions are no-ops, so an evidence set that admitted them would consist almost entirely of executions that did no work. The definition is stated identically in [`./deployment-runbook.md`](./deployment-runbook.md) and in [`./manual-build/02-flow-crunchbase-ingestion.md`](./manual-build/02-flow-crunchbase-ingestion.md); the cadence mechanism is recorded in [`../../docs/decisions/DECISION_LOG.md` (planned)](../../docs/decisions/DECISION_LOG.md) and flagged in [`./gaps-and-flags.md`](./gaps-and-flags.md).

- [ ] **The two are distinguished in the flow execution log before any run is counted.** A no-op records the cadence-guard comparison and then an early exit, and writes **no** run-summary record. A scheduled run passes the guard, proceeds to the source call or the fallback read, and **writes a run-summary record carrying its provenance**. Evidence: for each counted run, the log line showing the guard outcome and the run-summary record it wrote.
- [ ] **The evidence is read from the run-summary records only.** Evidence: the run identifier of each of the six records read.
- [ ] **The cadence in force at the time of the runs is recorded.** The cadence is the property `x_bst_startuptrk.ingestion.cadence_hours`, shipped value `24`, clamped to the range 6 to 48. Evidence: the property value observed and the clamped value the guard reported in its log line.

### 4b — three consecutive guard-passing runs per flow

**Three consecutive guard-passing runs per flow — six runs in total.** Fill every cell of every row. A row with an empty cell is not a counted run.

| # | Flow | Run | Timestamp (UTC) | Guard passed | Records processed | Records skipped | Unhandled errors | Provenance |
| --- | --- | --: | --- | --- | --: | --: | --: | --- |
| 1 | `Crunchbase Ingestion` | 1 | | | | | | |
| 2 | `Crunchbase Ingestion` | 2 | | | | | | |
| 3 | `Crunchbase Ingestion` | 3 | | | | | | |
| 4 | `LinkedIn Ingestion` | 1 | | | | | | |
| 5 | `LinkedIn Ingestion` | 2 | | | | | | |
| 6 | `LinkedIn Ingestion` | 3 | | | | | | |
| | **Aggregate** | | | **6 of 6 guard-passing** | | | **must total 0** | |

**Guard passed** reads `yes` on every counted row; a `no` means the row records a no-op and the row is replaced by a genuine scheduled run. **Records processed**, **Records skipped** and **Unhandled errors** are read from the run-summary record's members — `processed`, and the sum of `rejected`, `skipped` and `duplicates`, against unhandled errors counted separately from all of them. **Provenance** reads exactly `live` or `fallback`, taken from the record's `provenance` member; no third value is valid.

- [ ] **Crunchbase Ingestion — three consecutive guard-passing runs, zero unhandled errors.** Evidence: rows 1 to 3 above.
- [ ] **LinkedIn Ingestion — three consecutive guard-passing runs, zero unhandled errors.** Evidence: rows 4 to 6 above.
- [ ] **The three runs per flow are consecutive.** No guard-passing execution of that flow falls between them unrecorded. Evidence: the run identifiers in order, and confirmation that the log holds no guard-passing execution of that flow between the first and the third.

### 4c — per-record skips are expected behaviour, not errors

**Per-record skips arising from the four cleaning rules are expected behaviour and are not errors.** They are counted separately from unhandled errors, and **only unhandled errors bear on this criterion**. A run that rejected records and completed is a clean run. The specified failure semantics are that a per-record error is logged, that record is skipped, and the run continues — a run that halted on the first bad record is a failure of this criterion even though it reported the rejection.

Tick each rule once per flow, using the run in which it was exercised.

- [ ] **Rule 1 — trim whitespace on all string fields.** Evidence: a stored string that arrived with leading or trailing whitespace, shown trimmed.
- [ ] **Rule 2 — deduplicate incoming Startup records on `name` plus `headquarters_location`, case-insensitively.** Evidence: the duplicate pair supplied, the single entity row that resulted, and the loser's rejection reason.
- [ ] **Rule 3 — normalise the choice columns to their enumerated values, and log an unmatched value.** An unmatched value is stored as `Other` on a list that declares an `Other` member and is **left unwritten** on a list that does not; either way the event is logged. Evidence: one unmatched value of each kind, the outcome observed, and the logged event naming the column and the supplied value.
- [ ] **Rule 4 — reject a record missing a mandatory field rather than inserting a partial row.** Evidence: the rejected record, the reason naming the missing field, and confirmation that no partial entity record was inserted.
- [ ] **Skip and continue.** Evidence: from a single run, a non-zero processed count **and** a non-zero rejected count, which together establish that the run neither halted on the bad record nor inserted a partial one.

### 4d — provenance, and the two evidence surfaces

**The criterion explicitly accepts the sample-dataset substitute.** Three clean `fallback` runs per flow satisfy it — **provided the mode is recorded for every run.** Recording it is what keeps a fallback result from reading as validated live integration.

**There are two provenance surfaces and they are not interchangeable.** The mechanical reason is that the test framework rolls back the data a test creates, so a provenance row or property written inside a test does not survive the run.

| Surface | Written by | Survives the run | Read by |
| --- | --- | --- | --- |
| **Scheduled-run provenance** | Step 8 of the flow, on a real scheduled execution — the run-summary record and the property `x_bst_startuptrk.ingestion.last_run_provenance` | **Yes.** It is written outside any test transaction. | **This criterion**, section 4b above |
| **ATF result label** | The setup step of each flow test, labelling the result `fallback validated` or `live validated` | **No.** The framework rolls back data a test creates. | The test report, and section 4e below |

- [ ] **Every one of the six runs in section 4b carries a recorded provenance of `live` or `fallback`.** Evidence: the six values, read from the `provenance` member of each run-summary record.
- [ ] **The property `x_bst_startuptrk.ingestion.last_run_provenance` reads the provenance of the most recent run.** Evidence: the property value observed after the last counted run.
- [ ] **Where any run is `fallback`, the staging table held rows for it to read.** The fallback branch reads `x_bst_startuptrk_ingest_staging`, and an empty table cannot demonstrate the cleaning rules. Evidence: the staging row count before the run, and confirmation that the load of [`./manual-build/06-staging-table-csv-import.md`](./manual-build/06-staging-table-csv-import.md) had completed.
- [ ] **Where any run is `fallback`, the reason is recorded.** Evidence: the alias state that produced it — an unprovisioned or failing Connection & Credential Alias per [`./manual-build/01-connection-credential-aliases.md`](./manual-build/01-connection-credential-aliases.md), or the `x_bst_startuptrk.ingestion.source_mode` property set to force it.

### 4e — the ATF flow tests and their labels

Two ATF tests, suite `BST FLOW suite — ingestion`, one per flow. **A flow test result is labelled `fallback validated` or `live validated`**, so a passing result can never be mistaken for validated live integration. The label appears in three places: the test name suffix, the test description, and the setup step's output message.

| # | Test | Flow | Result | Label recorded | Test result record |
| --- | --- | --- | --- | --- | --- |
| 1 | `BST FLOW — Crunchbase Ingestion` | `Crunchbase Ingestion` | | | |
| 2 | `BST FLOW — LinkedIn Ingestion` | `LinkedIn Ingestion` | | | |

- [ ] **Both flow tests pass.** Evidence: the two test result names, their statuses and the suite result.
- [ ] **Both carry a label, and the label matches the mode the run actually used.** A `[live]` name is not left on a run that fell back. Evidence: the label read from each result, and the test name as it stands.
- [ ] **The suite evidence and the run-summary evidence are recorded separately.** The suite result evidences the cleaning rules; the run-summary records of section 4b evidence the cadence and the error count. Neither substitutes for the other. Evidence: confirmation that section 4b was filled from run-summary records and not from test results.

### Criterion 4 — pass condition

- [ ] **Three consecutive guard-passing runs per flow, six runs in total**, every row of section 4b filled. Evidence: the six run rows of section [4b](#4b--three-consecutive-guard-passing-runs-per-flow).
- [ ] **Zero unhandled errors** across all six runs, with per-record skips counted separately and not counted against this total. Evidence: the **Unhandled errors** column of section [4b](#4b--three-consecutive-guard-passing-runs-per-flow), which must total zero, and the five ticks of section [4c](#4c--per-record-skips-are-expected-behaviour-not-errors).
- [ ] **The provenance of every run recorded** as `live` or `fallback`. Evidence: the **Provenance** column of section [4b](#4b--three-consecutive-guard-passing-runs-per-flow) and the ticks of section [4d](#4d--provenance-and-the-two-evidence-surfaces).

Criterion 4 is met when, and only when, all three hold. The two flows, their cadence guards, the four cleaning rules and the run-summary record are specified in [`./manual-build/02-flow-crunchbase-ingestion.md`](./manual-build/02-flow-crunchbase-ingestion.md) and [`./manual-build/03-flow-linkedin-ingestion.md`](./manual-build/03-flow-linkedin-ingestion.md); the fallback dataset the staging table holds is loaded by [`./manual-build/06-staging-table-csv-import.md`](./manual-build/06-staging-table-csv-import.md).

## Criterion 5 — all five Service Portal routes render and navigate as specified

> **Prompt section 10.0, criterion 5.** All 5 Service Portal routes render and navigate per prompt section 5.0, verified by walkthrough against the enumerated route list, **with the startup inclusion filter confirmed active on Home / Search**.

The portal URL suffix is `bst`, and routing is query-parameter based. Every route is reached as `/bst?id=<page>`, with a record-scoped page adding `&sys_id=<record>`. The pages, their widgets and their navigation links are specified in [`./manual-build/04-service-portal-pages-and-widgets.md`](./manual-build/04-service-portal-pages-and-widgets.md).

### 5a — the five routes

Walk each route. Record that it rendered, that its widgets loaded, and that navigation into and out of it works.

- [ ] **Route 1 of 5 — Home / Search, page record `bst_home`**, reached at `/bst?id=bst_home` and also at `/bst` with no `id`, which resolves to the portal homepage. Widgets `bst-startup-search` and `bst-startup-results`. Evidence: the URL used, the rendered state, and the navigation hop taken from a result card into `bst_company`.
- [ ] **Route 2 of 5 — Company Profile, page record `bst_company`**, reached at `/bst?id=bst_company&sys_id=<startup sys_id>`. Widget `bst-company-profile`. Evidence: the URL used, the startup rendered, and the navigation hop taken from the Funding tab into `bst_investor`.
- [ ] **Route 3 of 5 — Investor Profile, page record `bst_investor`**, reached at `/bst?id=bst_investor&sys_id=<investor sys_id>`. Widget `bst-investor-profile`. Evidence: the URL used, the investor rendered, the `portfolio_count` displayed, and the navigation hop taken from the portfolio list into `bst_company`.
- [ ] **Route 4 of 5 — Dashboard / Trends, page record `bst_dashboard`**, reached at `/bst?id=bst_dashboard`. Widgets `bst-trends-kpi` and `bst-trends-charts`. Evidence: the URL used, the rendered state, and the navigation hop back to `bst_home`.
- [ ] **Route 5 of 5 — Account Management, page record `bst_account`**, reached at `/bst?id=bst_account`. Widgets `bst-account-summary` and the embedded `bst-premium-upsell`. Evidence: the URL used, the effective role and entitlements displayed, and the navigation hop back to `bst_home`.

| # | Route | Page record | Rendered | Navigated | Note |
| --- | --- | --- | --- | --- | --- |
| 1 | Home / Search | `bst_home` | | | |
| 2 | Company Profile | `bst_company` | | | |
| 3 | Investor Profile | `bst_investor` | | | |
| 4 | Dashboard / Trends | `bst_dashboard` | | | |
| 5 | Account Management | `bst_account` | | | |
| | **Aggregate** | | | | **5 of 5 required** |

- [ ] **A record-scoped page given no `sys_id`, or one that resolves to no readable record, renders a warning and a link back to Home / Search.** It renders neither an empty panel nor an error. Test both `bst_company` and `bst_investor`. Evidence: the two URLs tried and what each rendered.

### 5b — exactly five tabs on the company profile

**The company profile shows exactly five tabs, in this order and with these labels.** Tick each one and record what it rendered. A sixth tab is a failure of this criterion as surely as a missing one.

- [ ] **Tab 1 of 5 — Overview.** Evidence: the pane rendered and the fields shown.
- [ ] **Tab 2 of 5 — Funding.** Evidence: the pane rendered, the funding rounds listed, and `participating_investors` rendered as labels.
- [ ] **Tab 3 of 5 — People.** Founders and executives together in one pane. Evidence: the pane rendered and both record types present.
- [ ] **Tab 4 of 5 — Jobs.** Evidence: the pane rendered and the job postings listed.
- [ ] **Tab 5 of 5 — News.** Evidence: the pane rendered and the news articles listed.
- [ ] **There is no sixth tab.** Evidence: the tab labels read off the rendered tab strip, in order, and their count.

### 5c — the inclusion filter, confirmed active

**Both halves of this test are required.** The first half establishes that the filter excludes; the second establishes that it excludes by **query filter** and not by access control, because a record removed by an access control would be invisible to the administrator too.

The predicate is `active` true **AND** `headquarters_location` containing `Boston` **OR** `Cambridge, MA`, matched as a case-insensitive substring, with the tokens read from the property `x_bst_startuptrk.inclusion.location_tokens`. It tests those two columns and no others. The predicate is specified in [`./data-model.md`](./data-model.md).

- [ ] **Seed one startup that fails the criteria.** Either `active` false, or a `headquarters_location` outside Boston and Cambridge — `Providence, RI` serves. Evidence: the record's `sys_id`, `name`, `active` and `headquarters_location` as seeded.
- [ ] **Half 1 — the seeded startup is absent from the Home / Search results.** Search on its name from `bst_home` and confirm it does not appear, and that the result count does not include it. Evidence: the search term used, the results returned, and the explicit absence of the seeded record.
- [ ] **Half 2 — the same startup is still visible to an administrator in the platform list view.** Open the `x_bst_startuptrk_startup` list inside the scoped application and confirm the record is present and readable. Evidence: the list view used and the record shown. A record failing the criteria **remains in the table for administrative visibility**; if it is absent here, the criteria have been implemented as an access control rather than as a query filter, which is a defect. **This half is a visibility check on the query filter and is not an access-control check**; it is the one place in this checklist where an observation made as the administrator is valid evidence, and it establishes nothing about field-level enforcement. Enforcement is the subject of [criterion 2](#criterion-2--all-three-roles-enforce-field-level-acls-on-100--of-the-seven-premium-fields) and of section [5d](#5d--the-premium-upsell-treatment-under-the-base-role), both of which require impersonation.
- [ ] **Control — a startup that passes the criteria does appear in Home / Search.** Evidence: the record used and the search that returned it. Without this, half 1 could pass because the search returns nothing at all.
- [ ] **`institutional_funding_last_5yrs` takes no part in the predicate.** Seed or use a passing startup with `institutional_funding_last_5yrs` false and confirm it still appears in the results. Evidence: the record used, its flag value, and its presence in the results. The resolution of this point is recorded in [`../../docs/decisions/DECISION_LOG.md` (planned)](../../docs/decisions/DECISION_LOG.md) and flagged in [`./gaps-and-flags.md`](./gaps-and-flags.md).

### 5d — the premium upsell treatment under the base role

**The walkthrough for this section is performed under impersonation**, by a user holding exactly one scoped role and none of the elevated platform roles, exactly as [criterion 2](#criterion-2--all-three-roles-enforce-field-level-acls-on-100--of-the-seven-premium-fields) requires. A walkthrough conducted as the instance administrator displays all seven premium fields and does not test enforcement; a result obtained that way must not be recorded here.

- [ ] **Under `x_bst_startuptrk.user`, every gated field or gated tab region renders the upsell treatment.** No blank, no empty cell, no zero and no dash appears where a premium field was denied. Evidence: the surfaces walked and what rendered in each gated position.
- [ ] **`bst-premium-upsell` appears on the company profile, the investor profile and the account summary.** These are its three hosts. Evidence: the three pages and the widget's presence on each.
- [ ] **Under `x_bst_startuptrk.premium_user` and under `x_bst_startuptrk.admin`, every premium field renders its value and the upsell widget does not appear.** Evidence: the seven fields observed under each of the two roles, and the absence of the upsell widget.
- [ ] **A non-premium column renders under `x_bst_startuptrk.user` on the same screen.** `x_bst_startuptrk_startup.headquarters_location` serves. Evidence: the column and the value rendered. This establishes that the denial came from the field-level control rather than from nothing being readable.

### 5e — the supported viewport

- [ ] **The walkthrough was performed at 1024 pixels wide or above.** 1024 pixels is the declared supported floor of this portal; a narrower viewport is out of scope and a defect observed only below it is not a defect of this criterion. Evidence: the viewport width used for the walkthrough.

### Criterion 5 — pass condition

- [ ] **Five routes rendering and navigating**, 5 of 5. Evidence: the route table of section [5a](#5a--the-five-routes).
- [ ] **Five tabs on the company profile** — Overview, Funding, People, Jobs, News — and no sixth. Evidence: the five tab ticks and the tab-strip reading of section [5b](#5b--exactly-five-tabs-on-the-company-profile).
- [ ] **The excluded startup absent from Home / Search but present in the administrator list view**, both halves recorded. Evidence: the seeded record and both halves of section [5c](#5c--the-inclusion-filter-confirmed-active).
- [ ] **The upsell treatment visible to the base role** wherever a gated field or tab region is denied, gathered under impersonation. Evidence: the four ticks of section [5d](#5d--the-premium-upsell-treatment-under-the-base-role).

Criterion 5 is met when, and only when, all four hold. The portal, the theme, the five pages, the five tabs, the eight widgets, the upsell substitution rule and the viewport floor are specified in [`./manual-build/04-service-portal-pages-and-widgets.md`](./manual-build/04-service-portal-pages-and-widgets.md); the inclusion predicate is specified in [`./data-model.md`](./data-model.md).

## H — coverage gate, rule compliance and definition of done

### H1 — the coverage gate

**The hard minimum is 100 % of the six REST resources and 100 % of the seven tables with a passing Automated Test Framework test before delivery.** The suite inventory satisfies it with margin. Fill the two right-hand columns from the suite results.

| Suite group | Suites | Tests | Suites passing | Tests passing |
| --- | --: | --: | --: | --: |
| Table CRUD — one suite per entity table | 7 | 7 | | |
| Premium field access control | 1 | 21 | | |
| REST resources | 1 | 6 | | |
| Ingestion flows | 1 | 2 | | |
| **Total** | **10** | **36** | | |

7 + 21 + 6 + 2 = 36 tests across 10 suites. Both totals must hold at delivery.

- [ ] **Every one of the 7 entity tables has at least one passing test.** Evidence: the seven suite results from [criterion 1](#criterion-1--all-seven-tables-exist-with-100--of-their-fields).
- [ ] **Every one of the 6 logical resources has at least one passing test, and the nested `GET /founders/{startup_id}/executives` is tested.** Evidence: the six test results from [criterion 3](#criterion-3--all-six-rest-resources-return-correct-paginated-responses-and-a-429-with-a-retry-value).
- [ ] **All 21 access-control cells are present and passing.** Evidence: the roll-up from [criterion 2](#criterion-2--all-three-roles-enforce-field-level-acls-on-100--of-the-seven-premium-fields).
- [ ] **Both flow tests are present, passing and labelled.** Evidence: the two labelled results from [criterion 4](#criterion-4--scheduled-flows-ingest-and-clean-on-the-configured-cadence-with-zero-unhandled-errors).
- [ ] **The suite count is 10 and the test count is 36.** Evidence: the two observed totals from the table above.

**Two conditions block delivery.**

- [ ] **Blocking condition 1 — delivery is blocked if any table or any resource lacks a passing test.** A suite count of 10 with a test count below 36 means a cell, a resource or a table is uncovered. Evidence: the observed suite and test counts, and the name of anything uncovered.
- [ ] **Blocking condition 2 — if ATF execution is not enabled on the instance, this gate cannot be evaluated at all.** It is not failed and not partially met; it is unevaluable, and no delivery claim about coverage can be made. [`./deployment-runbook.md`](./deployment-runbook.md) asserts that prerequisite **before** the Update Set is imported, so the condition is discovered before any deployment work is done. Evidence: the ATF runner property value and the test-designer role held, copied from [section B](#b--deployment-gates).

### H2 — rule compliance

Three items, one per project rule. Each is a check performed against the delivered artifacts.

- [ ] **Rule 1 — Explainability.** The decision log at [`../../docs/decisions/DECISION_LOG.md` (planned)](../../docs/decisions/DECISION_LOG.md) exists as a Markdown table carrying its four columns — what was decided, what alternatives existed, why this choice was made, and what risks it carries — and covers every decision the plan names. The traceability matrix at [`../../docs/decisions/TRACEABILITY_MATRIX.md` (planned)](../../docs/decisions/TRACEABILITY_MATRIX.md) resolves in both directions with no gap: every legacy construct and every requirement maps to at least one artifact, and every artifact maps back to at least one justification. **No rationale text appears in any code comment or platform record description** — comments and descriptions state only what an artifact does and which requirement it implements. Evidence: the four column headers as written, the log's row count, the matrix's row count in each direction with zero unresolved entries, and the result of a scan of the Update Set's script bodies and record descriptions for rationale prose.

- [ ] **Rule 2 — Executive Presentation.** The deck at [`../../blitzy-deck/boston-startup-tracker-servicenow-executive-summary.html` (planned)](../../blitzy-deck/boston-startup-tracker-servicenow-executive-summary.html) opens in a browser **with no build step and no local file dependency**. It carries **12 to 18** slide sections. **Every** section carries at least one non-text visual. **Zero emoji** appear, and all icons are Lucide. **Every Mermaid diagram renders**, after both the ready event and a slide change, which is what confirms the render call is wired to both hooks. The three library versions — reveal.js **5.1.0**, Mermaid **11.4.0**, Lucide **0.460.0** — and the three font families — **Inter**, **Space Grotesk**, **Fira Code** — match the pinned values. The canonical theme file exists at [`../../blitzy-deck/references/blitzy-reveal-theme.css`](../../blitzy-deck/references/blitzy-reveal-theme.css) and **its CSS is identical to the deck's inline style block**. Evidence: the section count, the per-section visual list, the emoji hit count, the three source URLs, the font link, the outcome of navigating past a slide and back to confirm the diagrams still render, and the result of comparing the theme file against the inline block.

- [ ] **Rule 3 — Critical Decision Review Document.** The document exists at exactly `docs/review/CRITICAL_DECISIONS.md`, reachable from here as [`../../docs/review/CRITICAL_DECISIONS.md` (planned)](../../docs/review/CRITICAL_DECISIONS.md). It holds **exactly five** entries **ordered by risk, highest first**. Each carries a decision with its alternatives, a rationale citing the relevant code or convention, a risk level of High, Medium or Low, and a named reviewer persona together with what that reviewer should check. The **irreversible operation**, the **authorization decision** and the **ambiguity resolutions** are all called out. **All five decisions also appear in the Rule 1 log.** Evidence: the five entry titles in order with their risk levels and personas, the three call-outs located by entry, and confirmation that each of the five resolves to a decision-log row.

### H3 — definition of done

The delivery is complete when, and only when, every one of the following holds **simultaneously**. Tick each only when the evidence above supports it.

- [ ] **All nine pre-delivery gates pass.** [Section A](#a--pre-delivery-gates-g-1-to-g-9), 9 of 9.
- [ ] **The Update Set imports, previews with an empty error-type problem set, and commits.** [Section B](#b--deployment-gates), including both pre-commit checks.
- [ ] **All post-commit gates pass** — the eleven-gate core, 11 of 11, within the full set of 16 of 16. [Section B](#b--deployment-gates).
- [ ] **All 10 suites and 36 tests pass, with the coverage gate satisfied.** [Section H1](#h1--the-coverage-gate).
- [ ] **All five success criteria are verified with their stated evidence**, and every ingestion run's provenance is recorded as `live` or `fallback`. Criteria [1](#criterion-1--all-seven-tables-exist-with-100--of-their-fields), [2](#criterion-2--all-three-roles-enforce-field-level-acls-on-100--of-the-seven-premium-fields), [3](#criterion-3--all-six-rest-resources-return-correct-paginated-responses-and-a-429-with-a-retry-value), [4](#criterion-4--scheduled-flows-ingest-and-clean-on-the-configured-cadence-with-zero-unhandled-errors) and [5](#criterion-5--all-five-service-portal-routes-render-and-navigate-as-specified).
- [ ] **All three rules are verified.** [Section H2](#h2--rule-compliance).
- [ ] **Every requirement with no clean platform equivalent is flagged in [`./gaps-and-flags.md`](./gaps-and-flags.md)** rather than silently omitted or half-implemented. Twelve flags, `F1` through `F12`. Evidence: the flag count and the disposition recorded against each.
- [ ] **No file outside the planned set has been created or modified.** 29 created files and 1 updated file, per gate [G-7](#g-7--deliverable-completeness). Evidence: the file-presence check and a review of the working tree for anything outside that set.
- [ ] **No ServiceNow artifact outside the `x_bst_startuptrk` scope has been touched.** The instance-provisioning actions the package requires — the ATF runner property, the test-designer roles, the three impersonation users, the REST caller user and its Basic Auth Configuration, and the two credential aliases — are instance state and are correctly **absent** from the Update Set. Evidence: gate [G-4](#g-4--scope-containment), plus confirmation that the delivered Update Set carries no record outside the scope.

### H4 — final sign-off

| Item | Value |
| --- | --- |
| Pre-delivery gates, section A | of 9 passing |
| Post-commit gates, section B — core | of 11 passing |
| Post-commit gates, section B — full set | of 16 passing |
| Criterion 1 — tables and fields | met / not met |
| Criterion 2 — field-level access control | met / not met |
| Criterion 3 — REST resources | met / not met |
| Criterion 4 — scheduled flows | met / not met |
| Criterion 5 — portal routes | met / not met |
| Coverage gate — suites | of 10 passing |
| Coverage gate — tests | of 36 passing |
| Rule 1, Rule 2, Rule 3 | verified / not verified |
| Definition of done | all items ticked — yes / no |
| **Delivery accepted** | **yes / no** |
| Operator signature | |
| Date (UTC) | |

A **no** in any row is a **no** in the last row. There is no partial acceptance, and no item of this checklist may be waived.
