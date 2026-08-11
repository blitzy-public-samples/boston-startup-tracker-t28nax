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
| [3](#criterion-3--all-six-rest-resources-return-correct-paginated-responses-and-a-429-with-a-retry-value) | All 6 REST resources return correct paginated responses and a 429 with a retry value | **6 of 6** resources passing all three assertions — a success envelope of exactly four members, pagination with a `total_count` that is the **exact** filtered cardinality together with exact page membership and its three boundaries, and the exact 429 body |
| [4](#criterion-4--scheduled-flows-ingest-and-clean-on-the-configured-cadence-with-zero-unhandled-errors) | Scheduled flows ingest and clean Crunchbase and LinkedIn data, or the sample-dataset substitute, on the configured cadence with zero unhandled errors across 3 consecutive scheduled runs | **3** consecutive guard-passing runs **per flow**, each with a non-zero `processed` count, **zero** unhandled errors, and the provenance of every run recorded as `live` or `fallback`. **`LinkedIn Ingestion` can only ever be `fallback`.** Not met until six executions have been observed on an instance |
| [5](#criterion-5--all-five-service-portal-routes-render-and-navigate-as-specified) | All 5 Service Portal routes render and navigate as specified, verified by walkthrough, with the startup inclusion filter confirmed active on Home / Search | **5** routes rendering and navigating, **5** tabs on the company profile, the excluded startup absent from search but present in the admin list, and the upsell treatment visible to the base role |

Three further sections carry gates the criteria depend on: [section A](#a--pre-delivery-gates-g-1-to-g-9), the nine pre-delivery gates; [section B](#b--deployment-gates), the two pre-commit checks, the eleven required post-commit gates, the one further acceptance-required check `GATE-COL-01` and the four non-normative diagnostics `GATE-SEC-01` to `GATE-SEC-04`; and [section H](#h--coverage-gate-rule-compliance-and-definition-of-done), the coverage gate, the rule-compliance items and the definition of done.

## Referenced documents

**Every document named below is delivered and readable.** Each link resolves to a file in this repository, so the checker can open any of them and read the content the statement around it describes; no link is a forward reference to something still to be written.

| Document | What this checklist takes from it |
| --- | --- |
| [`./data-model.md`](./data-model.md) | The ten tables field by field: the 53 entity columns with their types, lengths, mandatory flags and premium markers, the choice lists, and the startup inclusion predicate. The source of the criterion 1 field rows. |
| [`./access-control.md`](./access-control.md) | The three roles, the five ACL layers, the seven premium fields, the secured read path, the omitted-not-nulled rule and the impersonation requirement. The source of the criterion 2 grid. |
| [`./api-reference.md`](./api-reference.md) | The six logical resources, the nested executives sub-resource, the pagination contract, the response envelope and the error contracts. The source of the criterion 3 assertions. |
| [`./validation-gates.md`](./validation-gates.md) | The two pre-commit checks, the eleven required post-commit gates, the one further acceptance-required check `GATE-COL-01` and the four non-normative diagnostics `GATE-SEC-01` to `GATE-SEC-04` — with their targets, queries and pass conditions, and the evidence record this checklist cites. Twelve checks block acceptance; the eleven post-commit gates are the subset that also triggers rollback; the four diagnostics block nothing. |
| [`./deployment-runbook.md`](./deployment-runbook.md) | The pre-delivery validator invocation, the pre-flight checks, the six-step import sequence, the rollback, the failure matrix, the ATF prerequisite asserted before import, and the definition of a scheduled run. |
| [`./manual-build-instructions.md`](./manual-build-instructions.md) | The index and execution order of the six manual-build guides, and the eleven required post-commit gates that are their single entry condition. |
| [`./gaps-and-flags.md`](./gaps-and-flags.md) | The nineteen flags `F1` through `F19` with no clean platform equivalent or no obtainable evidence, plus the separately counted open integration limitation `OPEN-1`, which section H confirms are flagged rather than silently omitted or half-implemented. |
| [`../scripts/validate_update_set_xml.py`](../scripts/validate_update_set_xml.py) | The two-level well-formedness validator that establishes gates G-1 and G-2, and its exit-code contract. |
| [`../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml`](../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml) | The single importable Update Set the pre-delivery gates and the deployment gates are run against. |
| [`./manual-build/01-connection-credential-aliases.md`](./manual-build/01-connection-credential-aliases.md) | The two Connection & Credential Aliases, and the provisioning state that decides whether an ingestion run resolves `live` or `fallback`. |
| [`./manual-build/02-flow-crunchbase-ingestion.md`](./manual-build/02-flow-crunchbase-ingestion.md) | The Crunchbase flow, its cadence guard, the four cleaning rules and the run-summary record criterion 4 reads. |
| [`./manual-build/03-flow-linkedin-ingestion.md`](./manual-build/03-flow-linkedin-ingestion.md) | The LinkedIn flow, identical in its guard, cleaning and run-summary mechanics. |
| [`./manual-build/04-service-portal-pages-and-widgets.md`](./manual-build/04-service-portal-pages-and-widgets.md) | The portal, the five pages, the five company-profile tabs, the eight widgets, the upsell substitution rule and the 1024-pixel floor. The source of the criterion 5 walkthrough. |
| [`./manual-build/05-atf-test-suites.md`](./manual-build/05-atf-test-suites.md) | The ten suites and thirty-six tests, the twenty-one ACL cells by name, the six REST tests, the two flow tests, and the three techniques the evidence depends on. |
| [`./manual-build/06-staging-table-csv-import.md`](./manual-build/06-staging-table-csv-import.md) | The load of the six sample CSVs into the one staging table, which the fallback branch of both flows reads. |
| [`../sample-data/README.md`](../sample-data/README.md) | The staging column contract and the fallback-only posture of the dataset. |
| [`../README.md`](../README.md) | The package index and the deploy order this checklist follows. |
| [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md) | The single source of truth for every decision behind the procedures below. |
| [`../../docs/decisions/TRACEABILITY_MATRIX.md`](../../docs/decisions/TRACEABILITY_MATRIX.md) | The bidirectional matrix section H verifies for coverage in both directions. |
| [`../../docs/review/CRITICAL_DECISIONS.md`](../../docs/review/CRITICAL_DECISIONS.md) | The five risk-ordered review entries section H verifies the shape of: **1** High / Security, **2** High / DevOps, **3** High / API/Integration, **4** Medium / Data/SME, **5** Medium / UX. |
| [`../../blitzy-deck/boston-startup-tracker-servicenow-executive-summary.html`](../../blitzy-deck/boston-startup-tracker-servicenow-executive-summary.html) | The executive deck that gate G-8 and the Rule 2 item inspect. |
| [`../../blitzy-deck/references/blitzy-reveal-theme.css`](../../blitzy-deck/references/blitzy-reveal-theme.css) | The canonical deck theme whose CSS the Rule 2 item compares against the deck's inline style block. |

This document carries **criteria, evidence and pass conditions only**. It states what to check, what to record and when an item passes. Every decision behind these procedures, every alternative considered and every risk each carries is recorded in [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md), which is the single source of truth for "why". Where an item below states a procedural requirement and its failure mode, that is the requirement and its consequence, not an argument for it.

**Review.** Three items in this checklist are the observable form of the three categories [`../../docs/review/CRITICAL_DECISIONS.md`](../../docs/review/CRITICAL_DECISIONS.md) is required to call out. The **authorization decision** is verified by [criterion 2](#criterion-2--all-three-roles-enforce-field-level-acls-on-100--of-the-seven-premium-fields). The **irreversible operation** — the rollback, which deletes the `x_bst_startuptrk` scope and cascades its tables, roles and flows — is bounded by [section B](#b--deployment-gates), which is the only place in this checklist that can trigger it. The **ambiguity resolutions** are verified where each one bites: the inclusion-criteria field ambiguity by [criterion 5](#criterion-5--all-five-service-portal-routes-render-and-navigate-as-specified), the participating-investors list interpretation by [criterion 1](#criterion-1--all-seven-tables-exist-with-100--of-their-fields), and the seven-entity-table count by the counting rule stated in criterion 1. The review entries themselves are not reproduced here.

## A — pre-delivery gates G-1 to G-9

**Nine gates**, run against the repository artifacts **before anything is imported**. All nine are required. A failure at any one of them blocks delivery, and gates G-1 and G-2 additionally block the deployment: a non-zero validator exit means the file is not uploaded at all.

Run them in the order below. G-1 and G-2 come first because they are mechanical and cheap, and because the rest of the package is not worth inspecting until the artifact it describes parses.

### G-1 — outer update-set well-formedness

- [ ] **The runtime XML parser carries the disproportionate-allocation defence, and the validator refused to proceed without it.** This is checked **first** because it happens first: the validator evaluates it before any path is opened, so nothing below is meaningful until it passes. Expat releases below `2.7.2` lack the defence, and on an unmitigated parser a document far under every size ceiling the validator applies can exhaust memory before any verdict is reached — which would turn the validator itself into the denial of service it is meant to detect. Two routes satisfy the gate: an Expat at or above **`2.7.2`**, where the defence reached the upstream tree; or an Expat at **`2.7.1`** exposing both `XML_SetAllocTrackerActivationThreshold` and `XML_SetAllocTrackerMaximumAmplification`, which is how a distribution ships the defence as a patch **without moving the version string** — so a version test alone would refuse a correctly patched runtime. The gate is **fail-closed** and **cannot be overridden**: a version that cannot be established, a library that cannot be probed, and the entry points appearing on a base below `2.7.1` are all refused.

  **Evidence:** the parenthesis on the validator's first progress line, copied verbatim — `(parser <version>, <mitigation state>)`. The two states that proceed are `release carries the allocation-tracker defence upstream` and `allocation-tracker entry points present, backported`.

  **Pass condition:** the first progress line names one of those two states and the run continues into stage 1. A run that instead prints `REFUSED: parser gate, no file was validated` and exits `2` **fails this item**, and it fails it as a **runtime** defect: the remedy is a patched Python, **not** an edit to the Update Set. Recording a corrected XML file against a gate refusal would be recording a fix to something never shown to be broken. The gate has no override — `D-351` rejected one — so the fallback is the three-step procedure the refusal prints and [`./deployment-runbook.md`](./deployment-runbook.md#when-the-parser-gate-refuses) sets out: record `--self-test`, which parses nothing and runs anywhere; re-run on a conforming runtime, which is the only route that yields G-1 and G-2 evidence; and if none can be reached, leave **both gates unrecorded** and treat delivery as blocked rather than substituting a parse by eye or another tool on the same runtime. **An unrecorded gate is not a passed gate**, and this item may not be ticked from a refusal.

- [ ] **The Update Set parses as a single XML document whose root is `<unload>`, containing exactly one `<sys_remote_update_set>` header record and at least one `<sys_update_xml>` update record.** Run the validator from the repository root:

  ```text
  python3 servicenow-startup-tracker-poc/scripts/validate_update_set_xml.py
  ```

  With no path argument the validator resolves the sibling Update Set `update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml` relative to its own directory, so the delivered artifact needs no argument. The exit-code contract, exactly as [`../scripts/validate_update_set_xml.py`](../scripts/validate_update_set_xml.py) defines it and [`./deployment-runbook.md`](./deployment-runbook.md) restates it: **`0`** every validated file satisfied both gates; **`1`** at least one validation failure at either level; **`2`** usage error, a path that is missing, not a regular file, or unreadable, or a **parser gate refusal** — in which case no path was opened and no file was validated — with code `2` taking precedence over code `1`.

  **Evidence to record:** the whole of the validator's **stage 1, gate G-1** block — the reported root element, the header-record count, the update-record count, and the header-linkage line stating how many update records carry the header `sys_id` — together with the process exit status.

  **Pass condition:** stage 1 reports `gate G-1 PASS`, the root is `<unload>`, the header count is exactly `1`, the update-record count is at least `1`, and the process exits `0`.

- [ ] **The prologue check has been shown to reject as well as accept.** Run the validator's own fixtures, which read nothing from disk:

  ```text
  python3 servicenow-startup-tracker-poc/scripts/validate_update_set_xml.py --self-test
  ```

  **Pass condition:** `17 byte-prologue fixture(s), 17 passed, 0 failed`, then `12 parser-gate fixture(s), 12 passed, 0 failed`, then `29 fixture(s) in total, 29 passed, 0 failed`, then `PASS: self-test`, exiting `0`. Of the seventeen prologue fixtures, four are forms that must be accepted and thirteen are forms that must be refused, including `<?xml-stylesheet href="s.xsl"?>`, `<?xmlfoo?>` and `<?xmlversion="1.0"?>` — three inputs that carry **no** XML declaration and that a prefix test accepts. Of the twelve parser-gate fixtures, four are runtimes that must be admitted and eight are runtimes that must be refused. **Evidence:** all four fixture lines and the exit status.

- [ ] **What the prologue check establishes is stated exactly, and nothing more is claimed of it.** It establishes that no byte-order mark precedes the content, that nothing at all precedes the declaration including whitespace, and that the declaration is a declaration — the literal `<?xml`, a whitespace byte, and a `version` pseudo-attribute before the closing `?>`. It establishes **nothing** about the declaration's `version` or `encoding` values, and nothing about the document below it. **Evidence:** the stage 1 block, read against this sentence.

- [ ] **A non-zero exit blocks delivery and blocks the deployment, and the two non-zero codes have different remedies.** Exit `1` is a statement about the file: correct the XML and re-run until the validator exits `0`. Exit `2` is a statement about the invocation or the runtime: correct the path, or — for a parser gate refusal — follow [When the parser gate refuses](./deployment-runbook.md#when-the-parser-gate-refuses), which does **not** involve editing the XML. In neither case upload a file that failed validation, and in neither case proceed to the pre-flight checks. **Evidence:** for any failed run, the stderr diagnostic and the exit status, followed by the passing re-run — or, for a refusal that could not be resolved, the refusal and the `--self-test` output with both gates left unrecorded.

### G-2 — nested per-record payload well-formedness

- [ ] **Every `<payload>` element, once un-escaped, parses as an independent document whose root is `<record_update>` carrying a non-empty `table` attribute.** This is the validator's second stage and it runs in the same invocation as G-1.

  **Evidence to record:** the whole of the validator's **stage 2, gate G-2** block — the number of update records examined, the count of well-formed payloads out of the number examined, and the update-name contract line — together with the process exit status.

  **Pass condition:** stage 2 reports `gate G-2 PASS`, the well-formed payload count equals the number examined, and the process exits `0`.

- [ ] **Read a G-2 failure against the escaping arithmetic.** Content inside a nested record document is escaped once for that document and again as the text of `<payload>`, so a `&&` in a script body appears in the outer file as `&amp;amp;&amp;amp;`. A single-escaped ampersand leaves the outer file legal, because a single ampersand entity is legal there, while the un-escaped payload then contains a bare double ampersand and is not well-formed. **A single parse of the outer document cannot see that defect**, which is why the validator parses at two levels and why G-1 passing tells you nothing about G-2. The script bodies in this Update Set — the advanced access-control scripts, the eight Script Includes, the three business rules and the one scheduled job — are where this defect class lives. **Evidence:** for any failure, the payload ordinal, its `target_name` and the parser's line and column, copied from stderr.

### G-3 — referential integrity

- [ ] **Every reference among the payload records resolves.** Each of the following must hold across the whole file: every `sys_dictionary` record's collection name equals an existing table record's name; every reference column's target names an existing table; every choice record's name-and-element pair matches a real column; every access-control name is either a table name or a table-and-field pair on a real column; every access-control role join points at one of the three `sys_user_role` records; every Scripted REST operation points at the single REST definition; and every payload record names the scoped application `x_bst_startuptrk` as its scope.

  **Evidence to record:** the **empty error-type preview-problem set** from step 4 of the import sequence in [`./deployment-runbook.md`](./deployment-runbook.md) — the request issued, the `result` array observed, and its length. A dangling identifier surfaces there as a problem record of type `error`, and the preview step aborts the deployment on any such record. Record the warning-type set alongside it, which is logged and does not abort.

  **Pass condition:** the error-type preview-problem `result` array is empty. Any error-type record fails this gate, and the offending identifier is corrected in the XML before the sequence restarts.

### G-4 — scope containment

- [ ] **No payload record carries a scope other than `x_bst_startuptrk`, and no record targets a table outside the application.** Audit the delivered XML for the scope value on every payload record and for the target of every record that names a table.

  **Evidence to record:** the total payload-record count, the count carrying the `x_bst_startuptrk` scope, and the list of any record that does not — by `target_name` and `type`. Record the audit command or the query used, so the check is repeatable.

  **Pass condition:** the count carrying the `x_bst_startuptrk` scope equals the total payload-record count, and the list of exceptions is empty. A record that omits the scope lands in the Global scope on import, which breaches the containment requirement at the moment of commit.

### G-5 — secret hygiene

**Scan for a credential VALUE, not for the words that name one.** This distinction decides whether the gate is meaningful. The deliverable is *required* to talk about API keys, client secrets, refresh tokens and passwords — guide 01 does little else — so a scan for the word `password` returns hundreds of hits, every one legitimate, and a gate that returns hundreds of legitimate hits is a gate nobody reads. What must be zero is the number of places a **value** appears.

- [ ] **Every manual-build guide contains no credential material either.** The same search over all six guides under [`./manual-build/`](./manual-build/) and over [`./manual-build-instructions.md`](./manual-build-instructions.md). The two Connection & Credential Aliases are referenced **by name only** — `x_bst_startuptrk.crunchbase_api` and `x_bst_startuptrk.linkedin_oauth` — and guide 01 builds only the four definition records, which cannot hold a secret, and creates no secret on either of its two readiness paths: on Path A it verifies and binds existing credential records; on Path B it creates the alias, connection and credential metadata with every secret-bearing field left empty. **Evidence:** the file list searched, the patterns, and the hit count per file.

| Term | Definition |
| --- | --- |
| **Credential value** | A literal string that would authenticate: a key, a client secret, a refresh or access token, a password, a bearer token, a private key, or credentials embedded in a URL's authority. **Zero are permitted.** |
| **Credential reference** | A name, a field label, a variable, an environment-variable placeholder such as `{SERVICENOW_PASSWORD}`, an alias name, or prose describing where a value lives. **Unlimited and expected.** |

- [ ] **Run the value-oriented scan over the Update Set XML and all seven manual-build documents** — `../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml`, the six guides under [`./manual-build/`](./manual-build/), and [`./manual-build-instructions.md`](./manual-build-instructions.md). Seven rules, each matching a shape a real secret takes:

  | # | Rule | What it matches |
  | --: | --- | --- |
  | 1 | Quoted literal | A credential-denoting name — `api_key`, `user_key`, `client_id`, `client_secret`, `refresh_token`, `access_token`, `bearer`, `password`, `secret`, `token` — assigned a **quoted string literal** of 8 or more non-space characters. An assignment whose right-hand side is an expression is code and is deliberately **not** matched |
  | 2 | Opaque assignment | The same names followed by an **unquoted** run of 16 or more base64/URL-safe characters with no dot, bracket or space |
  | 3 | Basic-auth URL | Credentials embedded in a URL authority — `scheme://user:pass@host` |
  | 4 | Authorization header | `Authorization: Basic` or `Bearer` followed by 12 or more token characters |
  | 5 | JWT | Three dot-separated base64url segments beginning `eyJ` |
  | 6 | Opaque run | Any alphanumeric run of **32 or more** characters, anywhere, whatever precedes it. This is the rule that catches a secret pasted with no label at all |
  | 7 | Private key | A PEM `-----BEGIN … PRIVATE KEY-----` header |

  **Evidence:** the eight file paths scanned, the seven rules, and the match count per rule.

- [ ] **Reconcile every match against the reviewed allowlist below.** A match is benign only for a stated, checkable reason. **The allowlist has exactly two entries**, and anything outside them fails the gate:

  | # | Rule | Benign match | Why it is benign | Expected count |
  | --: | --- | --- | --- | --: |
  | 1 | Opaque run | A **32-character lowercase hexadecimal** string, matching `^[0-9a-f]{32}$` | Every platform record identifier is exactly this shape. The Update Set is built from them: each `sys_id`, each reference between records, and each `update_guid`. They are public identifiers of configuration records, they authenticate nothing, and they are required for the referential integrity gate `G-3` to pass | **3747** across the XML, and **0** in the seven documents |
  | 2 | Opaque run | The **57-character unambiguous-character alphabet** assigned to `var alphabet` in the disposable-caller setup of [`./manual-build/05-atf-test-suites.md`](./manual-build/05-atf-test-suites.md) | It is a fixed public character set — the printable alphanumerics less the four that read ambiguously — from which the setup step mints a 32-character password **at run time**. It carries no entropy and authenticates nothing; the value it helps build is written straight into two encrypted fields and is never returned, logged, asserted on or committed. **Checkable:** the match is the whole right-hand side of that one `var alphabet =` assignment, and it is the only occurrence in the package | **1**, in guide 05 |

  **Pass condition:** rules 1 through 5 and rule 7 return **zero** matches across all eight files, and every rule 6 match satisfies the allowlist's `^[0-9a-f]{32}$` test. As delivered: 0 matches on rules 1, 2, 3, 4, 5 and 7; **3748** on rule 6, of which **3747** are allowlisted by entry 1 and **1** by entry 2, leaving **0 unexplained**.

  **What a failure looks like, so it is not argued away.** A rule 6 match that satisfies neither allowlist entry is a secret until proven otherwise — a 40-character mixed-case run is not a `sys_id` and there is no legitimate source of one in this deliverable. A rule 1 match is a value assigned to a credential name and fails the gate even inside an example, a comment or a code block: an example key is still a key-shaped string in a committed file, and the correct form of an example is a placeholder such as `<your user key>`.

- [ ] **The two Connection & Credential Aliases are referenced by name only** — "by name" in the requirement's sense of a **named-alias reference that carries no secret**, which is satisfied by the generated **API ID**. `x_bst_startuptrk.crunchbase_api` and `x_bst_startuptrk.linkedin_oauth` appear as those references; guide 01 verifies and binds records that already exist on the instance rather than creating secret material, and no alias, connection or credential record is carried in the Update Set. **Evidence:** the two API IDs as they appear, and confirmation that the XML carries no `sys_alias`, `http_connection`, `api_key_credentials`, `basic_auth_credentials` or `oauth_*` record.

- [ ] **Every alias resolution queries `sys_alias.id`, never `sys_alias.name`.** The dotted value is the platform-generated API ID and lives in `id`; `name` holds the unprefixed label, so a query on `name` with a dotted value matches nothing and reports `alias_unresolved` for an alias that is present. **Evidence:** every `new GlideRecord('sys_alias')` in the package followed by `addQuery('id', ALIAS)` — there are four in the manual-build guides and one in the ATF guide — and zero occurrences of `addQuery('name', ALIAS)`. `D-317` carries the decision.

- [ ] **The shared `redact()` helper passed its self-test on this instance before the first probe ran.** The helper is one body reproduced character for character in five places, and the weakest copy sets the exposure. Run the script in guide 01's [redaction test vectors](./manual-build/01-connection-credential-aliases.md#the-redaction-test-vectors) and require its last line to read `leaks=0 survivals_ok=4/4`. **Evidence:** that line, verbatim, and the five file-and-line positions of the helper. `D-318` carries the decision.

### G-6 — field-list fidelity

- [ ] **The seven entity tables carry exactly the 53 columns of prompt section 1.0, with the specified types, lengths and mandatory flags — no additions, no omissions.** The evidence for this gate is the field-by-field walk of [criterion 1](#criterion-1--all-seven-tables-exist-with-100--of-their-fields): all 53 rows of section [1b](#1b--the-field-by-field-walk-all-53-columns) filled and matching. **The walk is the whole evidence, and it is a field-level check rather than a count.** A count of dictionary records can reach 53 while a column carries the wrong type, the wrong length or the wrong mandatory flag, and it can also reach 53 by adding one column and omitting another — so a count that agreed would not establish this gate and a count that disagreed would tell you only that something was wrong somewhere. The walk names every discrepancy by column.

  **Evidence to record:** the criterion 1 completion state — 53 of 53 rows filled and matching — together with the per-table subtotals of section [1c](#1c--the-walk-roll-up), which are 12, 6, 6, 6, 8, 9 and 6.

  **Pass condition:** all 53 rows match on name, type, length and mandatory flag, and the seven per-table subtotals each match. **A column present that this document does not list breaches the binding-and-complete field list as surely as a column missing**, so the walk is read in both directions: every row of section 1b is found on the instance, and every column the instance carries for those seven tables appears as a row of section 1b.

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

- [ ] **The executive deck contains between 12 and 18 `<section>` elements.** Open [`../../blitzy-deck/boston-startup-tracker-servicenow-executive-summary.html`](../../blitzy-deck/boston-startup-tracker-servicenow-executive-summary.html) in a browser and count the top-level slide sections. **Evidence:** the counted number, and the count reported by a static search of the file.

- [ ] **Every section carries at least one non-text visual element** — a Mermaid diagram, a KPI card, a styled table or a Lucide SVG icon. **Evidence:** a per-section list naming the visual each section carries. A section with no visual fails the gate by itself.

- [ ] **All four slide types are present, and every section resolves to exactly one of them.** **Read the classification rule carefully, because three of the four types are named by a class and the fourth is not.** The deck's theme defines exactly three slide-type classes — `slide-title`, `slide-divider` and `slide-closing` — and defines no `content` class at all. A `<section>` is therefore classified as follows, and there is no other case:
  - it carries `class="slide-title"`, `class="slide-divider"` or `class="slide-closing"` → that type;
  - it carries **no** slide-type class → the **content** type, which is the default and is correct rather than a missing attribute.

  A section carrying **two** slide-type classes fails the gate; a section carrying **none** does not. **Evidence:** the census — how many sections of each of the four types — and confirmation that the four counts sum to the section count. The delivered figure to reproduce is **1 title, 11 content, 3 divider, 1 closing**, which sums to 16.

- [ ] **Every `content` slide is at or under four bullets and at or under forty body words.** The two caps apply to the `content` type only; the title, divider and closing slides are not content slides and are not measured against them. **Measure both the same way every time, or the gate is not reproducible:**
  - **Bullets** — count the `<li>` elements inside the `<section>`.
  - **Body words** — from the `<section>`, first remove every Mermaid container (`<pre class="mermaid">` together with its contents) and every heading element `<h1>` to `<h4>`; then strip the remaining HTML tags, resolve HTML entities, and count whitespace-separated tokens that contain at least one letter or digit. Headings and diagram source are excluded because neither is body copy; everything else on the slide counts, including table cells, KPI card labels and the footnote.

  **Evidence:** the sixteen-row table below, completed from the file. Record the observed type, bullet count and body-word count for **every** section, not only the content ones, so an over-limit slide cannot hide behind a type label. The Within limits column reads `n/a` for the four non-content slides.

  **The closing slide is exempt from those two caps and subject to two of its own, which are checked here rather than left to the type label.** Its takeaway heading must be **3 to 6 words** and it must carry **at most 3 bullets**. Measure the heading by counting whitespace-separated tokens of the `<h2>` inside `class="slide-closing"`, and the bullets by counting the `<li>` elements inside that same section. The delivered figures to reproduce are a **5-word** heading — `Fully specified, instance validation pending` — and **3** bullets totalling 34 words. **Evidence:** the heading quoted with its token count, and the bullet count. Recorded as decision `D-380`.

| Slide | Slide type | Bullets | Body words | Visual it carries | Within limits |
| --: | --- | --: | --: | --- | --- |
| 1 | | | | | n/a — not a content slide |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | n/a — not a content slide |
| 5 | | | | | |
| 6 | | | | | n/a — not a content slide |
| 7 | | | | | |
| 8 | | | | | |
| 9 | | | | | |
| 10 | | | | | |
| 11 | | | | | |
| 12 | | | | | n/a — not a content slide |
| 13 | | | | | |
| 14 | | | | | |
| 15 | | | | | |
| 16 | | | | | n/a — not a content slide |
| | **Aggregate** | | | | **11 of 11 content slides within both caps** |

- [ ] **No emoji appears anywhere in the deck.** All icons are Lucide SVG, referenced through the `data-lucide` attribute. **Evidence:** the search performed for emoji code points and its hit count, which must be zero, plus the count of `data-lucide` references.

- [ ] **The three pinned library versions are referenced exactly:** reveal.js **5.1.0**, Mermaid **11.4.0**, Lucide **0.460.0**. **Evidence:** the three source URLs copied from the deck.

- [ ] **Every versioned static asset the deck loads is pinned by a SHA-384 digest and loaded `crossorigin="anonymous"`.** There are **five** such assets — two stylesheets and three scripts — and all five are required to carry both. This is what pins the deck to the exact reviewed bytes: a substituted or tampered file fails to load rather than executing.

  **Four of the five declare it as markup; the fifth declares it as a constant, and the check reads both.** `reveal.css`, `white.css`, `reveal.js` and `lucide.js` are parsed from the document and carry `integrity="sha384-…"` and `crossorigin="anonymous"` on the element. `mermaid.min.js` is **not parsed at all** — it is injected on demand the first time a slide carrying a diagram is reached, per `D-536` — so its URL and digest are declared as the `MERMAID_SRC` and `MERMAID_SRI` constants of the deck's inline script, and the injecting code sets `integrity`, `crossOrigin` and `referrerPolicy` on the element it creates. The pin is therefore identical in effect and the browser enforces it identically; what differs is only where the string is written. The extraction below reads **every** `sha384-` token in document order, which covers both forms, and the URL list is stated in that same document order — note that Mermaid is now **last**, after Lucide, because its constant sits in the inline script below the two parsed script tags.

  **Verify the hashes rather than merely observing that a digest is present** — a digest holding the wrong value silently blocks the asset, which looks identical to a network failure. Recompute each digest from the URL the deck names and compare it to the declared value:

  **Requires exactly two binaries: `curl` and `openssl`.** Run it from this directory, `servicenow-startup-tracker-poc/docs/`, so the relative path to the deck resolves. It downloads each asset to a temporary file, refuses an empty body, digests the file rather than a pipe, compares the result against the attribute the deck declares, and **exits non-zero on the first mismatch or download failure** — so a network error can never be mistaken for a pass.

  ```bash
  #!/usr/bin/env bash
  set -euo pipefail

  for bin in curl openssl ; do
    command -v "$bin" >/dev/null 2>&1 || { printf 'FAIL  required binary not found: %s\n' "$bin" >&2 ; exit 2 ; }
  done

  deck=../../blitzy-deck/boston-startup-tracker-servicenow-executive-summary.html
  [ -r "$deck" ] || { printf 'FAIL  deck not readable at %s\n' "$deck" >&2 ; exit 2 ; }

  tmp=$(mktemp -d) ; trap 'rm -rf "$tmp"' EXIT
  rc=0

  # The five digests the deck declares, in document order: four integrity attributes
  # and the MERMAID_SRI constant of the inline script.
  grep -o 'sha384-[A-Za-z0-9+/=]*' "$deck" > "$tmp/declared"
  declared_n=$(wc -l < "$tmp/declared" | tr -d ' ')
  [ "$declared_n" -eq 5 ] || { printf 'FAIL  expected 5 sha384 digests in the deck, found %s\n' "$declared_n" >&2 ; exit 1 ; }

  i=0
  for u in \
    https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/reveal.css \
    https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/theme/white.css \
    https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/reveal.js \
    https://unpkg.com/lucide@0.460.0/dist/umd/lucide.js \
    https://cdn.jsdelivr.net/npm/mermaid@11.4.0/dist/mermaid.min.js ; do

    i=$((i + 1))
    want=$(sed -n "${i}p" "$tmp/declared")
    f=$tmp/asset

    if ! curl --fail --silent --show-error --location \
              --connect-timeout 10 --max-time 120 \
              --retry 2 --retry-delay 3 \
              --output "$f" "$u" ; then
      printf 'FAIL  %s\n      download error\n' "$u" >&2 ; rc=1 ; continue
    fi

    if [ ! -s "$f" ] ; then
      printf 'FAIL  %s\n      empty body\n' "$u" >&2 ; rc=1 ; continue
    fi

    got=sha384-$(openssl dgst -sha384 -binary < "$f" | openssl base64 -A)
    bytes=$(wc -c < "$f" | tr -d ' ')

    if [ "$got" = "$want" ] ; then
      printf 'ok    %s\n      %s  (%s bytes)\n' "$u" "$got" "$bytes"
    else
      printf 'FAIL  %s\n      declared %s\n      computed %s  (%s bytes)\n' "$u" "$want" "$got" "$bytes" >&2
      rc=1
    fi
  done

  [ "$rc" -eq 0 ] && printf 'ok    5 of 5 assets match the declared digests\n'
  exit "$rc"
  ```

  **If `openssl` is unavailable, this standard-library equivalent does the same job and the same comparison.** It needs Python 3 and nothing else, and it applies the same bounded timeout and the same non-zero exit.

  ```bash
  python3 - <<'PY'
  import base64, hashlib, io, re, sys, urllib.request
  DECK = '../../blitzy-deck/boston-startup-tracker-servicenow-executive-summary.html'
  URLS = [
      'https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/reveal.css',
      'https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/theme/white.css',
      'https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/reveal.js',
      'https://unpkg.com/lucide@0.460.0/dist/umd/lucide.js',
      'https://cdn.jsdelivr.net/npm/mermaid@11.4.0/dist/mermaid.min.js',
  ]
  declared = re.findall(r'sha384-[A-Za-z0-9+/=]+',
                        io.open(DECK, encoding='utf-8').read())
  if len(declared) != len(URLS):
      sys.exit('FAIL  expected %d sha384 digests, found %d' % (len(URLS), len(declared)))
  rc = 0
  for url, want in zip(URLS, declared):
      try:
          body = urllib.request.urlopen(url, timeout=120).read()
      except Exception as exc:
          print('FAIL  %s\n      download error: %s' % (url, exc)) ; rc = 1 ; continue
      if not body:
          print('FAIL  %s\n      empty body' % url) ; rc = 1 ; continue
      got = 'sha384-' + base64.b64encode(hashlib.sha384(body).digest()).decode('ascii')
      if got == want:
          print('ok    %s\n      %s  (%d bytes)' % (url, got, len(body)))
      else:
          print('FAIL  %s\n      declared %s\n      computed %s  (%d bytes)'
                % (url, want, got, len(body))) ; rc = 1
  if rc == 0:
      print('ok    %d of %d assets match the declared digests' % (len(URLS), len(URLS)))
  sys.exit(rc)
  PY
  ```

  **Evidence:** the five recomputed `sha384-` values beside the five declared values as written in the deck — four attributes and the `MERMAID_SRI` constant — and confirmation that each pair matches exactly. Then, with the deck open in a browser, confirm from the network panel that **the four parsed assets returned HTTP 200 and none was blocked**, then **navigate to a slide carrying a diagram** and confirm the injected `mermaid.min.js` also returned HTTP 200 and was not blocked — it is not requested on the title slide, so a network panel read before that navigation will show four assets and not five, which is the delivered behaviour rather than a fault. From the console confirm that **no integrity or cross-origin error was reported**. A blocked stylesheet leaves the deck unstyled and a blocked script leaves it unrendered, so a passing structural count with a blocked asset is not a pass.

  **The network panel shows ten subresource requests, not five, and the reconciliation is exact — so a count of ten is not a discrepancy against the five named here.** The five are the assets the deck itself declares with a `<link>` or a `<script>` tag, and they are the only ones an `integrity` attribute can cover. A bare `file://` open fetches **1 document and 10 subresources**: the five pinned assets; the Google Fonts stylesheet, which is the one declared exception above; the **three `fonts.gstatic.com` `.woff2` binaries** that stylesheet then requests, which are `@font-face` sources rather than declared assets; and **one stylesheet the deck never declares** — `https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/theme/fonts/source-sans-pro/source-sans-pro.css`, which reveal's own `dist/theme/white.css` reaches through the `@import` on its line 6. **A transitive `@import` cannot carry an integrity attribute**, so that request sits outside this item by construction rather than by exemption. It is served from an origin the deck's Content Security Policy already admits, so it raises no violation, and it is inert: the four `Source Sans Pro` faces it registers stay `unloaded` for the life of the page, because the inline theme rebinds `--r-main-font`, `--r-heading-font` and `--r-code-font`, and the family is named nowhere in the deck. Its whole cost is 553 bytes on the wire, and **no font binary is fetched from any `cdn.jsdelivr.net` path**. **One measurement trap:** that sub-request is issued `no-cors`, so `PerformanceResourceTiming` reports its `responseStatus` as `0` — read its status from the network panel, where it is `200`, not from the timing API. **Evidence:** the request count with every request's URL and status, and confirmation that the five carrying a digest are the five named above.

- [ ] **The pinned library versions were checked against published security advisories, and any conflict is recorded as a named acceptance decision rather than left implicit.** The pins are stated verbatim by the presentation rule, so a version carrying an advisory **cannot be silently upgraded** — the rule outranks the baseline. What this gate requires is that the conflict be *known and signed off*, not that it be absent. Query the advisory database for each of the three libraries at the pinned version, and for each hit record the advisory identifier, the version that fixes it, and the disposition. **Mermaid `11.4.0` is a known open case, and its disposition record is already written.** [Disposition record](./gaps-and-flags.md#disposition-record) carries the item, the pinned and fixing versions, the authority for the pin, the assessment date, the scope of the risk, the mitigations, the residual risk, the recommended disposition and the review trigger — every field the delivery can establish. It is accompanied by an [advisory-by-advisory scope table](./gaps-and-flags.md#advisory-scope-as-re-queried) giving, for each of **thirteen** identified advisories — **nine** whose stated range includes `11.4.0` and **four** whose does not — the range it states, whether `11.4.0` falls inside that range, and whether the code path it describes is reachable in this deck. **Two of the nine were added by the re-query of 2026-08-11**, `CVE-2026-41149` and `CVE-2026-41148`, both gated on a `classDef` directive that appears zero times in the deck's five diagram sources; re-run the query rather than trusting this count, because the count is a snapshot and the gate is a re-query. **The decision itself is recorded — `B` accept, on 2026-08-09 (UTC), re-affirmed on 2026-08-11 (UTC) against the amended nine-record set, with the risk owner named as the rule owner role** — because option `A` requires amending a rule the delivery may not amend, so no genuine choice remained open. **Two fields are deliberately unfilled**, because only a human can supply them: the **name** of the person accepting the residual risk, and the **date accepted** in UTC. **This gate is satisfied only when both carry a value.** **Evidence:** the advisory set as re-queried on the acceptance date, per library at the pinned version, including anything absent from the snapshot in that table; the two supplied field values copied here; the record's `Status` reading `CLOSED — accepted`; and the decision-log row carrying the acceptance. **An unrecorded advisory fails this gate, and so does a disposition record with either remaining required field still reading `REQUIRED — not yet supplied`.** A recorded and signed acceptance passes it — but acceptance is a human act, and ticking this box is not one.

- [ ] **The three font families are referenced exactly:** **Inter**, **Space Grotesk** and **Fira Code**, loaded through a Google Fonts link. **Evidence:** the font link copied from the deck, with the weights it requests.

- [ ] **The deck's inline theme block is byte-identical to the canonical theme file.** The rule names [`../../blitzy-deck/references/blitzy-reveal-theme.css`](../../blitzy-deck/references/blitzy-reveal-theme.css) as the canonical theme and simultaneously forbids a local file dependency, so the deck mirrors that CSS inline instead of linking it. **Compare the two as bytes, not by eye:** extract the text between `<style id="blitzy-theme">` and its closing tag and diff it against the file, or compare a cryptographic digest of each. A single differing byte — a leading newline is the usual culprit — means the delivered theme and the canonical theme are not the same artifact. **Evidence:** the two byte counts, the two digests, and the diff result, which must be empty.

  **Pass condition:** the section count is within 12 to 18 inclusive; every section carries a visual; all four slide types are present and every section resolves to exactly one of them under the classification rule above; every content slide is at or under four bullets and forty body words; the emoji hit count is zero; all three library versions and all three font families are present as specified; all five versioned assets carry a verified SHA-384 digest — four as an `integrity` attribute, Mermaid as the `MERMAID_SRI` constant applied to the element the deck injects — and `crossorigin="anonymous"`, load with HTTP 200 when requested, and raise no integrity or cross-origin error; every advisory against a pinned version is either absent or recorded with a signed acceptance; and the inline theme block is byte-identical to the canonical theme file.

### G-9 — governance completeness

- [ ] **The decision log covers every decision the plan names.** [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md) is a Markdown table carrying the four mandated columns — what was decided, what alternatives existed, why this choice was made, and what risks it carries — with one row per non-trivial decision. **Evidence:** the row count, the four column headers as written, and a spot check that each of the deviations this package cross-references to the log has a row: the gate classes — 11 required gates, 1 acceptance-required non-rollback check `GATE-COL-01`, and 3 acceptance-required security checks `GATE-SEC-01` to `GATE-SEC-03` — the direct entity-table read posture that makes those eleven executable, the participating-investors projection, the run-time creation of the impersonation users, the pre-seeded rate-limit counter, the two provenance surfaces, the hourly trigger with an elapsed-time guard, the query-parameter portal routing and the 1024-pixel floor.

- [ ] **The traceability matrix has no gap in either direction.** [`../../docs/decisions/TRACEABILITY_MATRIX.md`](../../docs/decisions/TRACEABILITY_MATRIX.md) resolves legacy construct to platform artifact and requirement to platform artifact, and resolves back the other way, so no artifact exists without a justifying requirement and no requirement exists without an artifact. **Evidence:** the row count in each direction and the count of unresolved entries, which must be zero on both sides.

- [ ] **The critical-decisions document holds exactly five risk-ordered entries whose decisions all appear in the log.** **Evidence:** the five entry titles in the order they appear, their risk levels, and confirmation that each maps to a row of the decision log.

- [ ] **Every count these documents state equals the count parsed from the artifact it describes.** Each figure is derived from the artifact and stated beside its arithmetic rather than carried by hand: the Update Set's header description decomposes into its record classes and those parts sum to the `<sys_update_xml>` count, which is **313**; the decision log's total, its `DEV` count, its section count and its risk split are the parsed row totals, and its tranche table sums to the same total; the traceability matrix's section-1 row total, its five-value transformation distribution and its 50-row sub-requirement status roll-up are the parsed row totals, stated in both section 1.8 and section 5.2; and the critical-decisions document's remainder is the log total minus the five entries it carries. Recorded at `D-070` for the record count and `D-089` for the log's size. **Evidence:** for each of the four documents, every stated figure beside its parsed figure, and the count of pairs that disagree — which must be **zero**.

  **Pass condition:** the decision log carries its four columns with no named decision missing, the matrix has zero unresolved entries in either direction, the review document holds exactly five entries ordered by risk with every one present in the log, and no stated governance count disagrees with its parsed actual.

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
| `G-8` | Deck structure — sections, slide types, content-slide limits, asset integrity, advisories, theme identity | | | |
| `G-9` | Governance completeness | | | |
| **Aggregate** | | | | **9 of 9 gates required** |

Record `pass` or `fail` in **Result**, the time of the check in **Timestamp (UTC)** in `YYYY-MM-DD HH:MM:SS` form, and the observed figures in **Evidence note**. For a failing gate also record what was corrected and the passing re-run.

## B — deployment gates

These run **during** the deployment, against the instance, in the sequence [`./deployment-runbook.md`](./deployment-runbook.md) specifies: validate the environment, assert the five instance prerequisites including the release floor, validate the XML, **three** pre-flight checks, establish the run identity, upload, poll until loaded, preview and poll until previewed, require the error-type preview-problem set to be empty, the two pre-commit checks, validate the commit, commit, then the post-commit gates. Every assertion, target, query and pass condition is specified in [`./validation-gates.md`](./validation-gates.md); this section records the outcome and is not a second definition of them.

**This is the only section of this checklist that can trigger the rollback, and the rollback has two branches.** It is triggered only by the conditions [`./deployment-runbook.md`](./deployment-runbook.md) documents: a commit failure, or a failure of one of the eleven required post-commit gates. Which branch runs depends on `START_STATE`, recorded at pre-flight 2:

- **`START_STATE=clean`** — the scope did not exist before this run. Branch A deletes the `x_bst_startuptrk` scope and cascades its tables, roles, flows and all application data. **It is irreversible, and no step of the runbook restores what it removes.**
- **`START_STATE=existing`, or unknown** — the scope existed before this run. Branch B **never deletes the scope**: it backs this run's update set out, re-runs the eleven required gates to verify the pre-existing installation survived, and escalates to the application's owner.

Record `START_STATE`, the branch taken, and the specific gate or state that triggered the rollback, before the first rollback request is issued.

**Every other failure in this section resolves without the rollback**, because nothing has been committed when it occurs: an instance-prerequisite failure, a pre-flight failure, an upload failure, a load error, a preview error, a `summary` shortfall, an error-type preview problem, a rejected commit-processor response, and any load, preview or commit timeout. Each is a row of the runbook's failure-handling matrix.

- [ ] **Gates G-1 and G-2 passed before the file was uploaded.** A non-zero validator exit blocks the upload. Evidence: copy the result from [section A](#a--pre-delivery-gates-g-1-to-g-9).
- [ ] **The environment was validated before any request was issued.** Evidence: that `SERVICENOW_INSTANCE_URL` was exported and is `https` with no path and no trailing slash, and that both credential variables were confirmed non-empty. **No credential value appears in the evidence** — a password is evidenced by its presence, never by its value.
- [ ] **The release floor was established objectively, not merely recorded.** Evidence: the `glide.war` value read, the release family token extracted from it, and the comparison that places that family at or above `yokohama`. A recorded value with no comparison does not satisfy this item; nor does an unestablished release, which is treated as below the floor.
- [ ] **All three pre-flight checks ran, and checks 1 and 3 passed.** Evidence: for each, the request issued and the status or record count observed — instance reachable with valid credentials, and instance not mid-upgrade.
- [ ] **Pre-flight 2 recorded the installation mode.** Evidence: `clean install`, `upgrade install` or `ambiguous scope`, and for an upgrade the pre-existing scope's `sys_id`, `version` and `sys_created_on`. **This record is what permits or forbids the rollback**, and it cannot be re-derived after the commit — a deployment that did not record it does not roll back.
- [ ] **A unique run identity was established and the update set was captured by it.** Evidence: `{RUN_NAME}`, the empty pre-upload snapshot, and the single new `sys_id` captured as `{ruset_sys_id}`. Identifying the record by most-recent creation date does not satisfy this item: the instance is shared.
- [ ] **All three pre-flight checks were run, and checks 1 and 3 passed.** Evidence: for each, the request issued and the status or record count observed — instance reachable with a `200` **and** an `application/json` content type **and** a parseable body carrying a top-level `result`; the starting state of the scope; and the instance not mid-upgrade.
- [ ] **All five instance prerequisites were ticked before the pre-flight checks began**, including the release floor and both XML entity-resolution properties. Evidence: the `admin` role held, the `glide.war` value observed and the release confirmed at or above the Yokohama floor, ATF execution enabled with a test-designer role held, and the observed alias state recorded.
- [ ] **`START_STATE` was recorded at pre-flight 2, and where it is `existing` the upgrade precondition was satisfied before the import began.** Evidence: `clean`, or `existing` with the installed version, the scope `sys_id`, the owner's backup or written expendability statement, and the identity of the committed set that Branch B would back out.
- [ ] **One cookie jar carried the whole of steps 1, 3 and 5, an `EXIT HUP INT TERM` trap was installed immediately after it was created, and no password reached a command line.** Evidence: the statement that a single session was used, that the trap was in place before the first request, that no request carrying the jar was made verbose, that the jar is gone, and that the password was passed on stdin rather than in argv.
- [ ] **The retrieved update set was located by a run-unique identity and then renamed to carry the run marker.** Evidence: `{upload_started_at}`, the single record the correlated query returned, and the run-unique name applied by the `PATCH`.
- [ ] **ATF execution is enabled on the instance and a test-designer role is held.** The runbook asserts this **before** the import, so the condition is discovered before any deployment work is done. Without it every suite of the coverage gate is unrunnable. Evidence: the ATF runner property value and the roles held.
- [ ] **The upload returned a retrieved update set and its `sys_id` was captured.** Evidence: the `sys_id`, recorded in the sign-off header.

### B1 — instance prerequisites and pre-flight checks
Five prerequisites and three pre-flight checks, all of them before the upload. **A prerequisite is a property of the instance rather than of the artifact**, which is why none of them is a post-commit gate: a gate failure rolls the application back, and removing the application cannot correct a condition the application did not create.
- [ ] **All five instance prerequisites established.** Evidence, one line each: the operating account's `admin` role; the release and patch level, at or above the Yokohama floor; both XML-parser properties, with `glide.stax.allow_entity_resolution` `false` and `glide.stax.whitelist_enabled` `true`, where **an absent property is a failure rather than a pass by omission**; the ATF runner property enabled with a test-designer role held; and the credential posture of the two aliases determined and recorded.
- [ ] **The release was read from a property that exists.** Evidence: the `glide.war` value, naming the release and patch level. **Do not** read `glide.buildname` or `glide.buildtag` — neither exists on the instance, so the query returns an empty `result` array and the release cannot be established from it.
- [ ] **All three pre-flight checks passed. Exactly three, and no more:** instance reachable with valid credentials, scope existence logged, and instance not mid-upgrade. Evidence: for each, the request issued and the status or record count observed.
- [ ] **The mid-upgrade check matched an actual field.** Evidence: the query used, which reads `upgrade_finishedISEMPTY` and passes on zero records. **`state=executing` must not be used** — `sys_upgrade_history` carries no `state` field, so the condition is dropped, the request returns the instance's entire upgrade history, and the check aborts every deployment.
- [ ] **An existing scope was logged and not treated as an error.** The commit updates existing records and the preview surfaces any real conflict. Evidence: the record count from the scope query, and the version if a record was found.
### B2 — the import sequence
- [ ] **Gates G-1 and G-2 passed before the file was uploaded.** A non-zero validator exit blocks the upload. Evidence: copy the result from [section A](#a--pre-delivery-gates-g-1-to-g-9), together with the update-record count the validator reported.
- [ ] **The upload used the XML import route, with the file as its final part.** Evidence: the route used — a form login, the `sysparm_ck` read from the upload form, then a multipart post — and confirmation that `attachFile` was the last part. **`POST /api/now/table/sys_remote_update_set` with an XML content type must not be used**: the Table API does not accept an update-set payload and answers `HTTP 400`. A multipart request that places `attachFile` before the other parts answers `HTTP 200` while importing nothing, so the sequence then proceeds against an update set that does not exist.
- [ ] **The retrieved update set was identified by resolving a run-unique name, and exactly one record matched.** The header name carries a token unique to this run. Evidence: the name uploaded, the single `sys_id` it resolved to — recorded in the [sign-off header](#sign-off-header) — and that record's `application_scope`, which must read `x_bst_startuptrk`. **Selecting the most recently created `sys_remote_update_set`, or resolving a fixed name that a retry or a parallel clone could also have created, must not be used**: either form can select another run's record and then preview and commit it.
- [ ] **The retrieved update set reached the loaded state.** Evidence: the state observed and the elapsed poll time.
- [ ] **The preview was triggered through the preview processor, and its response was asserted before anything was polled.** Evidence: the `HTTP 200` from the processor call and the `answer` value, which must be a 32-character hexadecimal execution-tracker `sys_id`. **`PATCH {"state":"previewing"}` must not be used**: it answers `HTTP 200` and is ignored, so the sequence polls a preview that was never started. Equally, polling before the tracker identifier is established polls nothing.
- [ ] **The preview completed.** Evidence: the state observed and the elapsed poll time, **stated against the 600 s budget as `observed s / 600 s` together with the pass count**. This duration has never been observed on an instance — it is the one timing in this package carried as a prediction, `600 s` across `313` records, that is `1.92 s` per record — so the number recorded here is the first measurement of it and is required whether the preview finishes fast or slow.
- [ ] **The error-type preview-problem set is empty.** This is also the evidence for pre-delivery gate [G-3](#g-3--referential-integrity). Evidence: the `result` array and its length. Record the warning-type set alongside it; warnings are logged and do not abort.
- [ ] **The commit completed, and the commit processor's response was asserted rather than assumed.** Evidence: the processor response recorded, then the state observed and the elapsed poll time.
- [ ] **Every failure was reported from fields that exist.** Evidence: for any failure handled in this section, the `state` value, the execution tracker's `message`, and the preview-problem records. **`error_detail` must not be reported**: `sys_remote_update_set` carries no such column, so the platform drops it from the response and a step that logs it logs nothing on every failure it handles.

### B3 — the import-completeness assertion

Read on reaching `previewed`, **before** the commit. It is a precondition of the post-commit gates rather than a member of them.

| Check | Assertion | Result | Timestamp (UTC) | Observed value |
| --- | --- | --- | --- | --- |
| Import completeness | On reaching `previewed`, `summary` equals the file's `<sys_update_xml>` count, `313` | | | |

- [ ] **Both pre-commit checks pass, against the update-record count the validator reported.** Evidence: the count from the validator's stage 1, and the two observed values above, which must equal it. Neither check triggers the rollback; a failure means the commit does not happen, and the remedy is to remove the retrieved update set by the guarded, exact-identifier procedure under [Removing a failed retrieved update set](./validation-gates.md#removing-a-failed-retrieved-update-set), correct the XML and restart the sequence. **Never delete an update set by name, state or date**, and where ownership of the retrieved record cannot be proven, stop and refer the cleanup to an instance administrator.

- [ ] **`summary` equals `313`.** Evidence: the observed `summary`, together with `inserted`, `updated`, `deleted` and `collisions`, and the update-record count the validator reported, which must be the same number. **An Update Set whose customer updates did not attach to its header reaches `previewed` and then `committed` while applying no record at all**: the platform reports success, the scope is never created, and all eleven post-commit gates then fail against an application that was never installed. `summary` is the field that distinguishes the two outcomes, which is why the poll reads the content fields and not `state` alone.
- [ ] **A shortfall was not committed.** A `summary` of `0` means the preview found nothing to apply; a `summary` below `313` means it found only part of the file. On either, the commit does not happen: delete the retrieved update set, correct the XML and restart the sequence. **This check triggers no rollback** — nothing has been committed, so there is no scope to remove. Evidence: the values observed and the action taken.
- [ ] **The `inserted`, `updated` and `deleted` split is recorded, not asserted.** On a clean install `inserted` equals `summary` with the other two at `0`; re-importing the same file over records that already exist reports the same `summary` distributed across `inserted` and `updated`, so asserting the split would fail a legitimate re-deployment. `collisions` is `0` on a clean instance, and a non-zero value is surfaced by the preview problems above. Evidence: the four values.

### B4 — the eleven required post-commit gates

[`./validation-gates.md`](./validation-gates.md) defines **eleven required** gates — the seven entity-table reads, the three role-record gates and the one scope-record gate — together with **four acceptance-required, non-rollback** checks — `GATE-COL-01` and `GATE-SEC-01` to `GATE-SEC-03` — and **one non-normative diagnostic**, `GATE-SEC-04`. **The rollback decision is the eleven: `11 of 11`, with no partial pass and no waiver.** The acceptance decision is those eleven **and** the four — **fifteen checks block acceptance, of which the eleven also trigger rollback**; the one diagnostic is run and recorded on every deployment and blocks nothing. The classes are defined at [Three classes of check](./validation-gates.md#three-classes-of-check-and-what-each-one-blocks) and mirrored here.

**The eleven required gates.** Gates 1 to 7 read each entity table's `sys_db_object` record, scoped to `x_bst_startuptrk`, and assert its name together with `access` `package_private`, `read_access` `false` and `ws_access` `false`. That is a **departure from the literal text of AAP section 0.11.2**, which reads as a row read on each of the seven; a row read is not available because `D-310` seals all ten application tables closed to every external route, and `D-311` expressed the gates in this form instead. The departure is accepted explicitly, and row `12` below carries that acceptance. **An empty `result` array is a failure for those seven**: there is exactly one `sys_db_object` record per table and it exists from the moment the table commits, so an empty result means no dictionary record carries that name inside the scope and the table did not commit. It cannot mean "committed but empty" the way a row read could.

| # | Gate | Assertion | Result | Timestamp (UTC) | Observed |
| --- | --- | --- | --- | --- | --- |
| 1 | `GATE-TBL-01` | `x_bst_startuptrk_startup` committed sealed: exactly 1 definition record, `access` `package_private`, `read_access` `false`, `ws_access` `false` | | | |
| 2 | `GATE-TBL-02` | `x_bst_startuptrk_founder` committed sealed: exactly 1 definition record, `access` `package_private`, `read_access` `false`, `ws_access` `false` | | | |
| 3 | `GATE-TBL-03` | `x_bst_startuptrk_executive` committed sealed: exactly 1 definition record, `access` `package_private`, `read_access` `false`, `ws_access` `false` | | | |
| 4 | `GATE-TBL-04` | `x_bst_startuptrk_investor` committed sealed: exactly 1 definition record, `access` `package_private`, `read_access` `false`, `ws_access` `false` | | | |
| 5 | `GATE-TBL-05` | `x_bst_startuptrk_fundinground` committed sealed: exactly 1 definition record, `access` `package_private`, `read_access` `false`, `ws_access` `false` | | | |
| 6 | `GATE-TBL-06` | `x_bst_startuptrk_jobposting` committed sealed: exactly 1 definition record, `access` `package_private`, `read_access` `false`, `ws_access` `false` | | | |
| 7 | `GATE-TBL-07` | `x_bst_startuptrk_newsarticle` committed sealed: exactly 1 definition record, `access` `package_private`, `read_access` `false`, `ws_access` `false` | | | |
| 8 | `GATE-ROLE-01` | Exactly one role record named `x_bst_startuptrk.admin` | | | |
| 9 | `GATE-ROLE-02` | Exactly one role record named `x_bst_startuptrk.user` | | | |
| 10 | `GATE-ROLE-03` | Exactly one role record named `x_bst_startuptrk.premium_user` | | | |
| 11 | `GATE-SCOPE-01` | Exactly one scope record for `x_bst_startuptrk` | | | |
| | **Required aggregate** | | | | **`11 of 11` required** |

7 entity-table gates + 3 role-record gates + 1 scope-record gate = 11. That is the required gate set in full, and the rollback decision in full. It is not the whole of the acceptance decision: `GATE-COL-01` and `GATE-SEC-01` to `GATE-SEC-03` below block acceptance too, which is why the acceptance aggregate is 15 and the rollback aggregate is 11.

- [ ] **Each of the seven table gates read that table's dictionary record, scoped, and asserted all four values.** The request is `GET /api/now/table/sys_db_object?sysparm_query=name=<table>^sys_scope.scope=x_bst_startuptrk&sysparm_fields=name,access,read_access,ws_access&sysparm_limit=2`, and the pass condition is exactly `HTTP 200` with one record reading `name` `<table>`, `access` `package_private`, `read_access` `false` and `ws_access` `false`. **An empty `result` array is a failure**: there is one dictionary record per table from the moment it commits, so an empty result means the table is absent from the scope. Evidence: the four field values for each of the seven. Booleans arrive as the strings `true` and `false`, so compare against `false` as text.
- [ ] **No table gate was satisfied by a row read, and no row read of an application table returned `200`.** Confirm the negative directly, because it is the containment property the whole access-control design rests on: issue `GET /api/now/table/x_bst_startuptrk_startup?sysparm_limit=1` as the deployment administrator and record the status, which **must not** be `200`. An administrator holds every role, so a `200` here would mean the native route is open to every authenticated caller holding one of the three scoped roles, outside the application's rate limiter and outside its two endpoint execution controls. Evidence: the request issued and the status returned, for at least one entity table and for `x_bst_startuptrk_ingest_staging`.
- [ ] **A flag reading other than its closed value is read as a containment failure, not as a cosmetic one.** `access` `public`, `read_access` `true` or `ws_access` `true` on any of the ten means the delivered dictionary record did not apply and that table is reachable from outside the application scope. Evidence: for any gate that failed, which of the four values departed and what it read.
- [ ] **`GATE-SEC-04` was run and printed `valid=true can_read=true` for all seven entity tables.** This is the diagnostic that establishes the sealed tables are still readable on the ACL-respecting path — it is class 3, so it blocks nothing, but a `can_read=false` means no caller can read that table and every list response will answer `403`. Evidence: the seven log lines.
- [ ] **The three role gates and the scope gate each returned exactly one record.** Zero records means the record did not commit; more than one means duplicates. Either outcome initiates the rollback. Evidence: the four record counts.

### B4a — the substituted table-gate form, acceptance-blocking

**Gates 1 to 7 do not read the seven entity tables. They read the seven tables' dictionary records, and that is a departure from the literal text of the Agent Action Plan.** AAP section 0.11.2's post-commit step reads as "a successful read on each of" the seven entity tables. `D-310` seals all ten application tables at `access` `package_private` with `read_access` and `ws_access` `false`, because a field-level read control can be defeated by query-predicate bisection, by the Aggregate API and by an unsecured cross-scope read — and prompt section 2.0 requires the base role to receive a genuine access denial on the seven premium fields, which a route that never evaluates the field control cannot deliver. A row read of an application table is therefore unavailable by design, and `D-311` expressed these seven gates as `sys_db_object` reads instead.

**The substituted form asserts strictly more than a row read would**, which is a fact about the two forms and not a warrant for the departure: it proves the table resolved, that it belongs to `x_bst_startuptrk` rather than to Global, and that all three of its read-access flags committed closed. **The warrant is this row.** It is acceptance-blocking and unfilled on delivery; it does **not** trigger the rollback, and it is not one of the twelve acceptance-blocking *checks* — it is the named acceptance of how seven of those checks are expressed.

| # | What is being accepted | Evidence required | Recorded value | Actor and date |
| --- | --- | --- | --- | --- |
| 1 | That gates 1 to 7 read each entity table's `sys_db_object` record rather than a row of the table itself, departing from the literal text of AAP section 0.11.2 | The named actor's acceptance, and confirmation they have read `D-310`, `D-311` and [The native platform read route on the application tables, and why it is closed](./gaps-and-flags.md#the-native-platform-read-route-on-the-application-tables-and-why-it-is-closed) | | |

- [ ] **Row 1 above is filled, with an actor and a date.** Evidence: this table, complete. An unfilled row is a **failed** acceptance item, not a pending action: it means nobody has accepted that the AAP's post-commit read was satisfied in a substituted form. The row may not be answered `not applicable`, because the substitution is unconditional in this delivery.
- [ ] **The acceptance was recorded before sign-off, not after.** Evidence: the date in row 1 is on or before the date in [H4 — final sign-off](#h4--final-sign-off).

**Five further checks, in two classes. They do not carry the same weight, and the distinction is between what blocks acceptance and what triggers the irreversible rollback — those are not the same thing.** The classes are defined in [`./validation-gates.md`](./validation-gates.md#three-classes-of-check-and-what-each-one-blocks) and mirrored here.

**`GATE-COL-01` — acceptance-required, non-rollback.** Criterion 1 asks for all seven tables **with 100 % of their fields**, and this is the only machine-checkable evidence of the 53-column count. A failure therefore **blocks acceptance**. It does **not** trigger the rollback: the remedy is to correct the Update Set and re-import, because deleting a scope whose seven tables and three roles all committed correctly would discard working artifacts to fix a dictionary defect that lives in the source file.

| # | Check | Assertion | Result | Timestamp (UTC) | Observed count and per-table split |
| --- | --- | --- | --- | --- | --- |
| A1 | `GATE-COL-01` | The seven entity tables carry exactly 53 columns between them | | | expected 53 = 12 + 6 + 6 + 6 + 8 + 9 + 6 |
| | **Acceptance aggregate** | | | | **15 of 15 acceptance-blocking checks — the 11 required gates, this one and the three `GATE-SEC` access-posture checks below. `GATE-SEC-04` is recorded, never required** |

**`GATE-SEC-01` to `GATE-SEC-03` — acceptance-required, non-rollback.** All **three** are run on every deployment and their results carried with the deployment record, because each names an exposure rather than a preference: raw staged payloads reachable over an external route, an application table permitting a cross-scope write, or REST endpoints carrying no authorisation. **A failure blocks acceptance and never triggers the rollback** — the remedy is to correct the delivered records and re-import, or for the platform owner to record written acceptance of the named exposure in the evidence record.

**`GATE-SEC-04` — the one non-normative diagnostic, recorded and never required.** It is run on every deployment because it is the only check that exercises the one read path the sealed tables leave open, but it is **not** an acceptance gate: it is the one check here that is not an HTTP request but a background script a human runs in the platform UI, so no deployment pipeline can assert on it. A failure is investigated and reported, and it never triggers the rollback and never blocks acceptance. The class definition is in [`./validation-gates.md`](./validation-gates.md#three-classes-of-check-and-what-each-one-blocks), and the counts there govern: **15 checks block acceptance, 11 of them trigger rollback**.

**One external instance prerequisite.** Not a gate and not a check of this delivery: the Global-scope XML entity-resolution properties, which this application cannot set and whose remedy lies with the platform owner. Record the two values read, or their absence, and to whom a non-hardened reading was reported.

| # | Check | Assertion | Result | Timestamp (UTC) | Observed |
| --- | --- | --- | --- | --- | --- |
| D1 | `GATE-SEC-01` | All ten application tables are reachable from the `x_bst_startuptrk` scope only | | | |
| D2 | `GATE-SEC-02` | No application table permits any cross-scope write, configuration or schema operation | | | |
| D3 | `GATE-SEC-03` | Both REST endpoint access controls committed | | | |
| D4 | `GATE-SEC-04` | Each of the seven entity tables resolves and is readable through the ACL-respecting path | | | |
| | **Diagnostic aggregate** | | | | **recorded, not required** |


| Observation | Value read | Timestamp (UTC) | Reported to |
| --- | --- | --- | --- |
| `glide.stax.allow_entity_resolution` | | | |
| `glide.stax.whitelist_enabled` | | | |


- [ ] **All eleven required gates pass, `11 of 11`.** Evidence: rows 1 to 11 above. This is the rollback decision and eleven of the fifteen acceptance-blocking checks, there is no partial pass and no waiver, and no manual-build guide starts before every one of them reports a pass.
- [ ] **`GATE-COL-01` passes, returning exactly 53.** Evidence: row A1 above, with the observed count and the per-table split. **A failure blocks acceptance** and criterion 1 may not be recorded as met while it stands; the remedy is to correct the Update Set and re-import, never to roll back.
- [ ] **All four security diagnostics were run and their observed values recorded, `4 of 4` recorded.** Evidence: rows D1 to D4 above, each with its observed value. **None of the four blocks acceptance and none triggers the rollback** — they are class 3, so a failure is reported, investigated and carried with the deployment record, and no operator may hold a deployment on one. Recording all four is nonetheless mandatory, because each observes something the eleven required gates cannot see. Remedy a failure as the corresponding **On failure** cell in [`./validation-gates.md`](./validation-gates.md) directs — for `GATE-SEC-02`, correct the dictionary records and re-import.
- [ ] **No gate or check instructed a change to anything outside the `x_bst_startuptrk` scope.** No gate in this deployment has a Global-scope remedy, and none may be given one. Evidence: the statement that every remedy applied was inside the application scope.
- [ ] **A gate that returned a server error was retried exactly once after 30 seconds, and the outcome recorded is the retry's.** Evidence: for any such gate, the first status, the wait and the retry's status, recorded in the same row.
- [ ] **No rollback was required.** If one was, record `START_STATE`, the branch taken, the gate or state that triggered it, the report made before it was issued, and the outcome — the deletion and its confirmation on **all five** surfaces on Branch A, or the back-out result and the re-run gate results on Branch B. Evidence: the trigger, the branch and the outcome, or the explicit statement that no rollback was performed.
- [ ] **If Branch A ran, the dangling role grants were cleared and the count proved zero.** Deleting the scope removes the three `sys_user_role` records and **not** the `sys_user_has_role` rows that pointed at them, and the three role `sys_id`s are deterministic — so a surviving grant re-attaches silently on the next import and hands its holder the privilege it names. Step A6 of [`./deployment-runbook.md`](./deployment-runbook.md) snapshots those rows, deletes each **by `sys_id`**, and re-reads to prove zero.
  **Evidence to record:** the A6.1 snapshot — every `sys_id`, `user` and `role`, with the count — and the A6.3 re-read showing an **empty** result.
  **Pass condition:** the A6.3 re-read returns zero rows, and the zero is recorded in the deployment log alongside the number removed. **Any surviving row blocks re-deployment**, and the next run's pre-flight re-issues the same read before the upload. Where Branch A did not run, record that instead: Branch B deletes no role and creates no dangling grant.
- [ ] **The instance XML entity-resolution reading was recorded and, where it was not the hardened configuration, reported to the platform owner.** Evidence: the two values as read, and the report made. This is explicitly **not** a gate: no reading of it fails the deployment, and no reading of it triggers the rollback, because deleting this application's scope would not change a Global property.

**Three checks a reader might expect among these gates are performed elsewhere, and each is named here so its absence from this table is legible rather than silent.** None of the three is `GATE-COL-01`, which is in the gates document as an acceptance-required class 2 check; the first row below is the wider field-by-field verification that the count alone cannot deliver.

| Check | Where it is performed | What makes it a different class |
| --- | --- | --- |
| The seven entity tables carry exactly 53 columns, with the specified types, lengths and mandatory flags | The field-by-field walk of criterion 1, section [1b](#1b--the-field-by-field-walk-all-53-columns), and gate [G-6](#g-6--field-list-fidelity) | A count of dictionary records cannot distinguish a correct install from one that added a column and omitted another, nor detect a wrong type, length or mandatory flag. The walk checks what the criterion actually requires, column by column. The **count** half is machine-checked, by `GATE-COL-01` — which is why that check blocks acceptance without triggering the rollback. |
| The seven field-level read controls committed with their role joins, to `admin` and `premium_user` only | The 21 cells of criterion [2](#criterion-2--all-three-roles-enforce-field-level-acls-on-100--of-the-seven-premium-fields), under impersonation | A count of access-control and role-join records cannot distinguish a control joined to the wrong roles from one joined to the right ones. The 21 impersonated reads observe the outcome the requirement is written in terms of, which is what "verified per role per field" asks for. |
| The instance refuses XML entity resolution | An [instance prerequisite](#b1--instance-prerequisites-and-pre-flight-checks), read before the import | It is instance configuration in the Global scope, which prompt section 6.0 forbids this application from shipping. Rolling the application back could not correct it, so making it a gate would make the rollback the wrong remedy for it. |

## Criterion 1 — all seven tables exist with 100 % of their fields

> **Prompt section 10.0, criterion 1.** All 7 tables exist with 100 % of their fields, **verified field by field**.

**The counting rule.** The count of seven is evaluated against the **seven entity tables** listed below. The join table `x_bst_startuptrk_m2m_round_investor`, the staging table `x_bst_startuptrk_ingest_staging` and the rate-limit counter table `x_bst_startuptrk_rate_limit_counter` are **supporting artifacts**; they are listed separately under [Supporting tables](#supporting-tables-not-counted-in-the-seven) and are not part of this count, and their columns are not part of the 53. The resolution of the count is recorded in [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md).

### 1a — table existence, seven gates

The seven table gates of [`./validation-gates.md`](./validation-gates.md) establish existence. **Each reads that table's `sys_db_object` record within the `x_bst_startuptrk` scope** — `GET /api/now/table/sys_db_object?sysparm_query=name=<table>^sys_scope.scope=x_bst_startuptrk&sysparm_fields=name,access,read_access,ws_access&sysparm_limit=2` — and passes on exactly `HTTP 200` with one record whose `name` matches and whose `access`, `read_access` and `ws_access` read `package_private`, `false` and `false`. **An empty array is a failure**: one dictionary record exists per table from the moment it commits, so an empty result means the table is absent from the scope. A row read is not available, because all ten application tables are delivered closed to every external route. Readability is established separately by `GATE-SEC-04`, which opens each table through `GlideRecordSecure` from inside the scope. Copy each result from [section B4](#b4--the-eleven-required-post-commit-gates).

- [ ] **`GATE-TBL-01` — `x_bst_startuptrk_startup` exists in the scope and is closed.** Evidence: HTTP status, `result` record count, and the `access`, `read_access` and `ws_access` values returned.
- [ ] **`GATE-TBL-02` — `x_bst_startuptrk_founder` exists in the scope and is closed.** Evidence: HTTP status, `result` record count, and the `access`, `read_access` and `ws_access` values returned.
- [ ] **`GATE-TBL-03` — `x_bst_startuptrk_executive` exists in the scope and is closed.** Evidence: HTTP status, `result` record count, and the `access`, `read_access` and `ws_access` values returned.
- [ ] **`GATE-TBL-04` — `x_bst_startuptrk_investor` exists in the scope and is closed.** Evidence: HTTP status, `result` record count, and the `access`, `read_access` and `ws_access` values returned.
- [ ] **`GATE-TBL-05` — `x_bst_startuptrk_fundinground` exists in the scope and is closed.** Evidence: HTTP status, `result` record count, and the `access`, `read_access` and `ws_access` values returned.
- [ ] **`GATE-TBL-06` — `x_bst_startuptrk_jobposting` exists in the scope and is closed.** Evidence: HTTP status, `result` record count, and the `access`, `read_access` and `ws_access` values returned.
- [ ] **`GATE-TBL-07` — `x_bst_startuptrk_newsarticle` exists in the scope and is closed.** Evidence: HTTP status, `result` record count, and the `access`, `read_access` and `ws_access` values returned.
- [ ] **`GATE-COL-01` — the seven entity tables carry exactly 53 columns between them.** Evidence: the `result` record count, which must read exactly `53`, and the per-table split 12 + 6 + 6 + 6 + 8 + 9 + 6. This is the count-level check and the walk below is the field-level one; **both are required, and both block acceptance**. `GATE-COL-01` is acceptance-required and non-rollback — see [`./validation-gates.md`](./validation-gates.md#three-classes-of-check-and-what-each-one-blocks).

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
- [ ] **These three tables carry no required post-commit gate, and none is attempted.** They share the seven entity tables' posture — `package_private` with `read_access` and `ws_access` `false` — so no Table API read of them can succeed either; what makes them ungated is that AAP section 0.11.2 names the seven entity tables, which is why [section B4](#b4--the-eleven-required-post-commit-gates) holds eleven gates and not fourteen. `GATE-SEC-01` covers all ten in one read. Their existence is established from the dictionary, as the three ticks above do, and their behaviour is exercised by the Automated Test Framework suites of [`./manual-build/05-atf-test-suites.md`](./manual-build/05-atf-test-suites.md): the join table by criterion 4's ingestion runs, the staging table by the same runs' fallback branch, and the counter table by criterion 3's `429` assertion. Evidence: the three dictionary records observed, and the suites that exercised each.

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

- [ ] **Seven tables present and readable.** `GATE-TBL-01` through `GATE-TBL-07` all pass, each with `HTTP 200` and a `result` array. Evidence: section [1a](#1a--table-existence-seven-gates), seven results.
- [ ] **53 columns matching the binding list exactly**, on name, type, length and mandatory flag — no additions, no omissions — verified by the walk rather than by a count. Evidence: section [1b](#1b--the-field-by-field-walk-all-53-columns), 53 rows, and the roll-up of section [1c](#1c--the-walk-roll-up) with its seven per-table subtotals of 12, 6, 6, 6, 8, 9 and 6.
- [ ] **Seven table-CRUD suites passing**, 7 of 7. Evidence: the suite table of section [1d](#1d--the-seven-table-crud-suites).

Criterion 1 is met when, and only when, all three hold. This criterion also supplies the evidence for pre-delivery gate [G-6](#g-6--field-list-fidelity). The dictionary this walk is checked against is [`./data-model.md`](./data-model.md).

## Criterion 2 — all three roles enforce field-level ACLs on 100 % of the seven premium fields

> **Prompt section 10.0, criterion 2.** All 3 roles enforce field-level ACLs on 100 % of the 7 premium fields, **verified per role per field**.

### 2a — the impersonation requirement

> **Every check in this criterion must be performed under impersonation, by a user holding exactly one scoped role and none of the elevated platform roles.**
>
> **A check performed as the instance administrator does not test enforcement.** Record access controls carry an administrator override, and every operator of a personal developer instance holds the platform administrator role. A read or a walkthrough conducted as the instance administrator displays all seven premium fields and appears to prove enforcement that was never tested at all. **Evidence gathered that way is void and must not be recorded in this document.**

The requirement is procedural and applies to every one of the twenty-one cells below, to the omission spot check, to the control-column check, to the premium-role write refusal of section [2f](#2f--there-is-exactly-one-read-route-and-no-second-one-to-check) and to the criterion 5 portal walkthrough. The two containment probes of that same section are the one exception, and deliberately so: they are issued **as the deployment administrator**, because the point of them is that even the most privileged caller finds no route. Its resolution is recorded in [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md), and it is inventoried as a flag in [`./gaps-and-flags.md`](./gaps-and-flags.md).

- [ ] **Three purpose-created users exist for the run, one per role.** Each holds **exactly one** of `x_bst_startuptrk.admin`, `x_bst_startuptrk.premium_user` and `x_bst_startuptrk.user`. Evidence: the three user records and the single role held by each.
- [ ] **None of the three holds an elevated platform role** — not the platform `admin` role, not `security_admin`, not `maint`. The scoped role `x_bst_startuptrk.admin` and the platform administrator role are different roles; the test user holds the scoped one and not the platform one. Evidence: the full role set read back for each of the three users, including roles inherited by containment.
- [ ] **The role set was verified inside every cell, before that cell's read outcome was trusted.** Each cell creates its own users — the framework rolls a created user back when its test ends, so there is no persistent user another cell's verification could have covered — and verifies each one's full role set, elevated-role absence and zero group memberships in its own step. Evidence: **all 35** role-set verification step outputs from this suite, 21 at the first user and 14 at the second, one per user created.
- [ ] **The users are created by the test setup steps at run time**, not shipped in the Update Set, because `sys_user` sits outside the application scope. Evidence: confirmation that the delivered Update Set carries no `sys_user` record, and the setup-step output naming each user created.
- [ ] **After the run, `sys_user` carries no residual `BST ATF` user.** One remaining means a test transaction did not close, and no result in that run is trustworthy. Evidence: the query and its row count, expected `0`. The portal walkthrough of criterion 5 uses its own separately named `BST PORTAL` users, which it creates and deletes by hand; the two sets are never interchanged.

### 2b — the three oracles every cell must carry

**A cell is evidence only if its outcome was read from the platform's own access-control decision.** Each of the twenty-one cells therefore records **three independent oracles**, and the first of them is the authority:

| # | Oracle | How it is read | What it proves |
| --- | --- | --- | --- |
| **1** | **The platform element check** — `gr.getElement(<field>).canRead()` on a `GlideRecordSecure` read of the record | Directly, on the record, under impersonation | The access-control engine's own decision on that field for that role. **This is the authority.** |
| **2** | **Key presence on the serialised object**, tested with `Object.prototype.hasOwnProperty.call(body, <field>) === false` for a denial | On the object the response serialiser returned, and independently over HTTP in section 2e | That the denial reaches the API surface as an **omission** rather than as an empty value |
| **3** | **The control column** — a non-premium column on the same record, under **both** branches | In the same read | That the table-level grant passed, so the denial came from the field-level control rather than from nothing being readable |

- [ ] **Oracle 1 is a direct platform element check on every one of the twenty-one cells.** Evidence: for each cell, the recorded `element.canRead()` value.
- [ ] **No cell's oracle is a delivered helper asked about itself.** `RestResponseBuilder.canRead(record, field)` is a one-line wrapper around `record.getElement(field).canRead()`, so a cell that asserts the wrapper's answer against the wrapper's own behaviour asserts nothing about the access controls — it would return the same answer if every field ACL were deleted, because the wrapper simply reports whatever the engine says. The builder appears in these cells **only** as the subject of oracle 2, where its `serialize()` output is what is being checked. Evidence: confirmation, per cell, that the recorded oracle 1 value came from `getElement(...).canRead()` and not from the builder.
- [ ] **Oracles 2 and 3 are recorded independently of oracle 1**, so a single defect cannot satisfy all three. Evidence: the three recorded values per cell, and the resource and record object for oracle 2.
- [ ] **Each cell also records that the impersonation took effect**: the acting user identifier equals the user under test, and `gs.hasRole('admin')` reads `false`. A silently ineffective impersonation otherwise produces a false pass on all three oracles at once. Evidence: the two values per cell.

### 2c — the 21 cells, seven premium fields by three roles

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

### 2d — the cell roll-up

- [ ] **21 of 21 cells correct.** Evidence: the counts below, and the name of every cell whose result is anything other than a pass.

| Expectation | Cells | Count | Correct | Cells not correct |
| --- | --- | --: | --: | --- |
| Reads — administrator | `ACL-1.1` to `ACL-7.1` | 7 | | |
| Reads — premium user | `ACL-1.2` to `ACL-7.2` | 7 | | |
| Denied — base user | `ACL-1.3` to `ACL-7.3` | 7 | | |
| | **Total** | **21** | | |

7 fields x 3 roles = 21. 14 cells expect a read, 7 expect a denial. A cell that is missing, failing or in an error state counts as not correct.

- [ ] **The suite result itself passes.** Evidence: the `BST ACL suite — premium fields by role` suite result name, status and timestamp.

### 2e — omitted, not nulled

- [ ] **For a base-role caller, a denied field key is absent from the API response object.** It is **not** present with an empty string, **not** present with a null, and **not** present with a placeholder. Test this on a live response, not only inside the suite: call a list operation as a caller holding only `x_bst_startuptrk.user` and inspect the raw JSON of one record object.

  **Evidence to record:** the resource called, the record object as returned, and the explicit result of testing for key presence on each premium key of that resource — for `/startups`, `total_funding_usd` and `institutional_funding_last_5yrs`.

  **Pass condition:** the premium key does not appear in the object at all. A key present with an empty value fails this item even though the value discloses nothing, because the contract is omission.

- [ ] **A non-premium column on the same record still reads under the base role.** Read a control column — `x_bst_startuptrk_startup.headquarters_location` serves — in the same call. It must return a value.

  **Evidence to record:** the control column name and the value returned.

  **Pass condition:** the control column returns a value. That establishes that the table-level read grant passed and that the denial came from the field-level control rather than from nothing being readable at all. Both layers are load-bearing: without the table-level grant nothing is readable and the field-level rules never evaluate, and without the field-level rules every premium field is readable by every role.

### 2f — there is exactly one read route, and no second one to check

**All ten application tables are delivered `access` `package_private`, `read_access` `false` and `ws_access` `false`**, so the Scripted REST API at `/api/x_bst_startuptrk/v1/` is the only route that reaches an application row. `GET /api/now/table/x_bst_startuptrk_startup` does not serve rows on this deployment, and a script running in any other application scope — including a Global-scope background script — cannot reach a row through unsecured record access either.

- [ ] **Under `x_bst_startuptrk.user`, the native Table API does not serve the table at all.** Read `GET /api/now/table/x_bst_startuptrk_startup?sysparm_limit=5` while impersonating the base-role user.

- [ ] **A native Table API read of an entity table does not return `200`, issued as the deployment administrator.** Issue `GET /api/now/table/x_bst_startuptrk_startup?sysparm_limit=1` with the administrator credentials — deliberately the most privileged caller available, because an administrator holds every role and a `200` here would mean the route is open to every caller holding one of the three scoped roles.

  **Pass condition:** `HTTP 400` with `Invalid table x_bst_startuptrk_startup`. **An `HTTP 200` is a failure even when every premium key is absent from the body**, because the same route then accepts a `sysparm_query` predicate on a premium column, and the predicate is evaluated in the database before any field-level control is consulted.

  **Pass condition:** the status is not `200`. On this platform the response to a read of a table with `ws_access` `false` is `HTTP 400` with `Invalid table x_bst_startuptrk_startup`; `403` is also a pass. **A `200` fails this item outright** and means the delivered `ws_access` value did not commit — the seven table gates of [section B4](#b4--the-eleven-required-post-commit-gates) assert the same three flags and would have failed too.

- [ ] **The same negative holds for all ten tables, not just the one probed.** Read the ten dictionary records in one request: `GET /api/now/table/sys_db_object?sysparm_query=nameSTARTSWITHx_bst_startuptrk_&sysparm_fields=name,access,read_access,ws_access&sysparm_limit=50`.

  **Evidence to record:** the ten names with their three flag values each.

  **Pass condition:** exactly ten records, every one reading `package_private`, `false` and `false`. This is `GATE-SEC-01` of [`./validation-gates.md`](./validation-gates.md), recorded here because criterion 2 depends on it rather than merely coexisting with it.
- [ ] **Under `x_bst_startuptrk.user`, neither inference route answers.** Issue `GET /api/now/table/x_bst_startuptrk_startup?sysparm_query=total_funding_usd>0` and `GET /api/now/stats/x_bst_startuptrk_startup?sysparm_sum_fields=total_funding_usd`, then repeat both for `x_bst_startuptrk_fundinground` and `amount_usd`, and for `x_bst_startuptrk_investor` and `aum_usd`.

  **Evidence to record:** the six requests and the six statuses.

  **Pass condition:** all six answer `HTTP 400`. A `200` on a predicate request lets a base-role caller recover a premium figure by bisection; a `200` on an aggregate request returns a sum or average of a premium column with no element on which a field control could ever be evaluated.
- [ ] **Under `x_bst_startuptrk.premium_user`, no write reaches any entity table on the one route that exists.** Issue a `POST` and a `PATCH` to `/api/x_bst_startuptrk/v1/startups` while authenticated as the premium-role caller.

  **Evidence to record:** the two requests, their statuses, and confirmation that the target table holds no new record and the target record is unchanged.

  **Pass condition:** both are refused. Layer 2 grants write, create and delete to `x_bst_startuptrk.admin` alone; the `Boston Startup Tracker API write` endpoint control admits that role alone; and `create_access`, `update_access` and `delete_access` are `false` on every one of the ten dictionary records — so the premium role, which can read every premium field, must still be unable to change anything. The corresponding tests are in [`./manual-build/05-atf-test-suites.md`](./manual-build/05-atf-test-suites.md).

- [ ] **The three supporting tables refuse the native route on the same terms as the seven entity tables.** Evidence: a read of `x_bst_startuptrk_ingest_staging` over the Table API and the status it returned, which must be `HTTP 400`. The staging table is the one that matters most, because it is the only table holding verbatim upstream payloads and unvalidated personal data.

### Criterion 2 — pass condition

- [ ] **21 of 21 assertions correct**, every one gathered under impersonation by a user holding exactly one scoped role and none of the elevated platform roles. Evidence: the 21 cell rows of section [2b](#2c--the-21-cells-seven-premium-fields-by-three-roles), the roll-up of section [2c](#2d--the-cell-roll-up), and the four precondition ticks of section [2a](#2a--the-impersonation-requirement).
- [ ] **The omission spot check passes** — the denied key is absent from the response object rather than present with an empty value. Evidence: section [2d](#2e--omitted-not-nulled), the recorded record object.
- [ ] **The control-column check passes** — a non-premium column reads under the base role in the same call. Evidence: section [2d](#2e--omitted-not-nulled), the control column and the value returned.
- [ ] **No second read route exists, and no write reaches a table under a non-administrator role on the one route that does.** Evidence: section [2f](#2f--there-is-exactly-one-read-route-and-no-second-one-to-check), the three ticks — the native-route negative issued as the administrator, the ten-table posture read, and the premium-role write refusal.

Criterion 2 is met when, and only when, all four hold. The matrix, the five ACL layers and the verification procedure are specified in [`./access-control.md`](./access-control.md); the twenty-one tests, their step sequences and the impersonation technique are specified in [`./manual-build/05-atf-test-suites.md`](./manual-build/05-atf-test-suites.md). The two documents must agree cell for cell with the grid above.

## Criterion 3 — all six REST resources return correct paginated responses and a 429 with a retry value

> **Prompt section 10.0, criterion 3.** All 6 REST resources return correct paginated responses and a `429` with a retry value on rate limit.

**6 ATF tests**, one per logical resource, built as suite `BST REST suite — resources` per [`./manual-build/05-atf-test-suites.md`](./manual-build/05-atf-test-suites.md). The physical base path is **`/api/x_bst_startuptrk/v1/`**. Each test asserts **three** things, so the grid below is 6 resources x 3 assertions = 18 cells. Assertion 2 is one cell made of seven parts, `2a` through `2g`; the cell is recorded only when all seven are.

### 3a — the three assertions, stated once

**Assertion 1 — success response shape.** The call returns `200` and an envelope carrying **exactly four** members: `result` as an array, `total_count`, `limit` and `offset`. `limit` and `offset` echo the values the API actually applied. **There is no fifth member**, and in particular there is no member reporting that the count was truncated — record the member set observed, not merely that the four are present.

**Assertion 2 — pagination across `sysparm_limit` and `sysparm_offset`, with an exact `total_count` and exact page membership.**

**The filtered set must be of a known, exact size, and `total_count` must equal that size.** Seed **five** records carrying a marker value unique to the run — four the marker filter selects and one negative control it must not — each with a distinct value in the resource's sort column, and pass the marker filter on every list call. The filtered set is then exactly **4**, and the following are asserted as exact values rather than as bounds:

| # | Assertion | Exact expectation |
| --: | --- | --- |
| 1 | The page never exceeds the requested `sysparm_limit` | Rows returned on page one equals 2 at `sysparm_limit=2` |
| 2 | **`total_count` equals the size of the filtered set** | **Exactly 4**, on page one and on page two |
| 3 | **Page membership is exact and ordered** | Page one is the first two identifiers in the resource's sort order, in that order; page two is the remaining two, in that order |
| 4 | The remainder is exact | Page two returns exactly 2 rows, not "the rest, whatever that is" |
| 5 | Overlap is zero and the union is complete | No identifier appears on both pages, and the union equals the four seeded identifiers exactly |
| 6 | **The negative control is absent from every page and uncounted** | It appears in no `result` array, and `total_count` stays 4 |
| 7 | **A page past the end** returns an empty `result` with `total_count` **unchanged** | At `sysparm_offset=4` the `result` array is empty and `total_count` still reads **4**; a count derived from the page would fall to `0` here |
| 8 | **A filter matching nothing** returns `total_count` exactly `0` and an empty array | HTTP `200` with `result` `[]` and `total_count` `0` — not a `404` |
| 9 | **`sysparm_offset` `10001` is refused** | HTTP `400` with a body carrying `error` and **no** `result` or `total_count` member; a refusal carrying an empty envelope would read as a legitimate empty page |

**A `total_count` assertion of the form "at least the number of rows returned" is not acceptable here, and must not be recorded as evidence.** It passes against a count of the entire table, against a count that ignores the filter, and against a count that ignores the inclusion criteria — the three failures this assertion exists to catch. Likewise, asserting only that no row repeats across pages passes against a second page that returned unrelated rows; membership must be asserted by identifier.

The bounds are read from two properties — `x_bst_startuptrk.rest.default_limit`, shipped value `20`, applied when `sysparm_limit` does not resolve to a usable value, and `x_bst_startuptrk.rest.max_limit`, shipped value `50`, the largest page the API will serve. A `sysparm_limit` above the maximum is clamped to the value read from that property, and the clamped call must return the whole four-row filtered set on one page in sort order; a `sysparm_offset` above `10000` is refused with `400`. **Each property is itself resolved to at least `1` and at most `50`**, so neither the caller nor an administrator can widen a page beyond fifty records — setting either property to `9999` still yields `50`, including for a request that carries no pagination parameter at all.

- [ ] **The discriminator and the seeded cardinality are recorded for every resource.** Evidence: per resource, the discriminator parameter used, the token, the number of records seeded under it, and the number the request is expected to count. The parameter differs per resource — `name` for `/startups`, `/founders` and `/investors`, `startup` for `/funding-rounds`, `/jobs` **and `/news`**, and the `{startup_id}` path segment for the nested executives path. `GET /news` accepts a `source` filter as well, but the discriminator the test uses is `startup`, because the news fixtures hang off the parent startup exactly as the other child fixtures do and their negative control hangs off a **second** parent — the one mechanism that makes the control uncountable is shared by all five child resources. [`./manual-build/05-atf-test-suites.md`](./manual-build/05-atf-test-suites.md) is authoritative for the per-resource marker column. The **five** `sys_id`-keyed no-match values must be **well formed** 32-character identifiers, because a malformed one is refused with `400` rather than answered with an empty page.
- [ ] **`total_count` is exact, and the exactness rests on a stated invariant.** All seven entity tables and the join table grant table-level read to all three application roles and carry **no record-level access control**, so record-level visibility is identical for every caller and one aggregate is a correct total for all of them. **Adding a record-level rule to any of those tables makes every `total_count` in this application wrong rather than merely imprecise.** Evidence: confirmation that no record-level access control exists on those eight tables, read from [`./access-control.md`](./access-control.md).

**Assertion 3 — the `429` body, matching this example exactly:**

```json
{"error": "rate_limit_exceeded", "retry_after": 42}
```

Two members, and no others. `retry_after` is a whole number of seconds — the seconds remaining in the caller's current window, with a floor of `1` — so the value observed will differ from the `42` above while the shape does not. A standard `Retry-After` response header carries the same value and does not alter the body.

- [ ] **The counter rows were seeded against the dedicated REST caller, `bst.atf.rest` — not against the impersonated user.** The caller identifier is also the first component of `window_key`, so seeding the wrong caller produces the wrong key as well as the wrong tuple. `Send REST Request - Inbound` performs a real inbound HTTP call and establishes **its own session** from the Basic authentication profile on the step; an `Impersonate` step earlier in the test has no bearing on it. The limiter therefore accounts against `bst.atf.rest`, and seeding any other user's `sys_id` in `caller` leaves the limit untripped and returns `200` where `429` was asserted, with no other diagnostic. Evidence: the `sys_id` seeded in `caller`, and the user name it resolves to, which must read `bst.atf.rest`.
- [ ] **The REST caller's own posture was verified, and it is the account the evidence is attributed to.** `bst.atf.rest` reads `web_service_access_only` **`true`**, `active` `true`, holds **exactly** `x_bst_startuptrk.user` and no other role, and belongs to **no** group. Evidence: the four values read back from the `sys_user` record and its Roles related list. Its password was generated, appears only in that record and the Basic Auth Configuration, is rotated after acceptance, and the account is disabled or deleted at end of life; record which was done: `______`.
- [ ] **The determinism procedure was followed, and the test owned both window keys.** `x_bst_startuptrk_rate_limit_counter` carries a `window_key` column that is `string` 200, **mandatory** and **unique**, and it is the **only** column the limiter queries: `RateLimitService.windowKey(caller, apiResource, windowStart)` composes it as `<caller sys_id>|<api_resource>|<window bucket in epoch seconds>`. Two facts follow, and together they decide the procedure. Because the column is **unique**, at most one row can exist per key, so the older hazard — a second row sharing the window and the limiter finding the one the test did not seed — **cannot occur**; and because the key embeds the **window bucket**, the current window and the next are two different keys, so a boundary crossing between the seed and the request lands the request on an unseeded key. The procedure therefore acts on **both keys** throughout, is four-part, and all four parts are recorded:

  | Part | Action | Recorded value |
  | --: | --- | --- |
  | 1 | **Delete every** row carrying either candidate key — the current window boundary and the next — before the ordinary calls, and assert the row count is **0** | |
  | 2 | Confirm the ordinary calls produced a **summed** `request_count` across both keys of **1** then **2** from that zero baseline | |
  | 3 | **Delete both keys** again, then write **one row at the budget under each**, and assert **exactly 2** rows summing to twice the budget | |
  | 4 | After the `429`, confirm the sum is twice the budget **plus one** with **exactly one** row above the budget, then **delete both keys** and assert **0** | |

  Seed all five columns — `window_key`, `caller`, `api_resource`, `window_start` and `request_count` — with `window_key` produced by calling `RateLimitService.windowKey()` rather than composed by hand, `api_resource` the resource token under test, `window_start` the aligned window boundary computed as `epoch - (epoch % window_seconds)` rendered as a date/time value, and `request_count` at exactly the budget.
- [ ] **The boundary race was removed rather than narrowed, and no step slept.** The counter is a fixed window, so a seed landing near the end of one window and a request arriving in the next would resolve different keys and start a fresh count of 1. The procedure seeds **both** candidate boundaries at the budget, so whichever the request resolves to is already full and no clock is read between the seed and the request. **Evidence: confirmation that no counter step calls `gs.sleep()` and none measures the remaining window time.** A wait of that kind reintroduces the race it appears to close and blocks a held transaction.
- [ ] **The three boundary requests were made and recorded, per resource.** Evidence: for a page past the end, the offset requested, the row count returned and the `total_count`; for a filter matching nothing, the value used and the `total_count`; for `sysparm_offset` `10001`, the status and the exact body. **All three must precede the rate-limit seeding**, because each is a real inbound request that consumes budget and the seeding step leaves the counter at the budget deliberately.
- [ ] **The rate-limit resource token was seeded verbatim.** Accounting is keyed on the resource, and there are **seven** tokens across six resources: `/startups`, `/founders`, `/founders/{startup_id}/executives`, `/investors`, `/funding-rounds`, `/jobs` and `/news`. The nested sub-resource accounts **separately** from `/founders`: seeding `/founders` does not trip the nested path, and seeding the nested token does not trip `/founders`. Evidence: the token seeded for each `429` assertion, all seven listed.

### 3b — the grid, six resources by three assertions

Tick a resource only when all three of its cells carry a recorded result.

- [ ] **Resource 1 of 6 — `/startups`**, endpoint `/api/x_bst_startuptrk/v1/startups`.

| Assertion | What to record | Result |
| --- | --- | --- |
| Success shape | Status, and the four envelope members observed | |
| Pagination | Applied `limit` and `offset`; rows returned per page; **the exact `total_count` at each offset, which must read 4**; the ordered identifiers on each page; the remainder; overlap count, the three boundary results — a page past the end, a filter matching nothing and the refused `sysparm_offset` `10001` — which must read 0; and the negative control's absence | |
| `429` body | The exact body returned and the `retry_after` value | |

  This test carries two further assertions, and the exact counts are what make the first of them bite. **First, the inclusion criteria must reach the count as well as the page.** The fixture seeds **five** startups carrying the filter token, of which **four** satisfy `active` and the two location tokens; the fifth is inactive and outside both. That fifth record must not appear in `result` **and** `total_count` must read exactly **`4`**. A `total_count` of `5` alongside four rows is the precise defect the assertion exists to catch: the criteria are a query filter applied identically to the result set and to the count, so a disagreement between the two is a defect. Record the token match count, the `total_count`, and the absence of the failing record — either half can pass while the other fails. **Second**, a `sysparm_offset` of `-1` and of `abc` are each refused with **`400`** and an `error`-only body naming the parameter. Record all five values.

- [ ] **Resource 2 of 6 — `/founders`**, endpoint `/api/x_bst_startuptrk/v1/founders` **and** the nested `/api/x_bst_startuptrk/v1/founders/{startup_id}/executives`.

| Assertion | What to record | Result |
| --- | --- | --- |
| Success shape | Status and envelope members for **both** the top-level path and the nested path | |
| Pagination | For **both** paths: applied `limit` and `offset`; rows per page; **the exact `total_count`, which must read 4**; the ordered identifiers on each page; the remainder; the three boundary results — a page past the end, a filter matching nothing and the refused `sysparm_offset` `10001` — and overlap, which must read 0; and the negative control's absence | |
| `429` body | The exact body and `retry_after` for **both** tokens — `/founders` and `/founders/{startup_id}/executives` | |

  Executive records are served only through this nested sub-resource; there is no seventh top-level resource. All three assertions are made twice in this test, once per path.

- [ ] **Resource 3 of 6 — `/investors`**, endpoint `/api/x_bst_startuptrk/v1/investors`.

| Assertion | What to record | Result |
| --- | --- | --- |
| Success shape | Status, and the four envelope members observed | |
| Pagination | Applied `limit` and `offset`; rows returned per page; **the exact `total_count` at each offset, which must read 4**; the ordered identifiers on each page; the remainder; overlap count, the three boundary results — a page past the end, a filter matching nothing and the refused `sysparm_offset` `10001` — which must read 0; and the negative control's absence | |
| `429` body | The exact body returned and the `retry_after` value | |

- [ ] **Resource 4 of 6 — `/funding-rounds`**, endpoint `/api/x_bst_startuptrk/v1/funding-rounds`.

| Assertion | What to record | Result |
| --- | --- | --- |
| Success shape | Status, the four envelope members, and `participating_investors` as a JSON array | |
| Pagination | Applied `limit` and `offset`; rows returned per page; **the exact `total_count` at each offset, which must read 4**; the ordered identifiers on each page; the remainder; overlap count, the three boundary results — a page past the end, a filter matching nothing and the refused `sysparm_offset` `10001` — which must read 0; and the negative control's absence | |
| `429` body | The exact body returned and the `retry_after` value | |

- [ ] **Resource 5 of 6 — `/jobs`**, endpoint `/api/x_bst_startuptrk/v1/jobs`.

| Assertion | What to record | Result |
| --- | --- | --- |
| Success shape | Status, and the four envelope members observed | |
| Pagination | Applied `limit` and `offset`; rows returned per page; **the exact `total_count` at each offset, which must read 4**; the ordered identifiers on each page; the remainder; overlap count, the three boundary results — a page past the end, a filter matching nothing and the refused `sysparm_offset` `10001` — which must read 0; and the negative control's absence | |
| `429` body | The exact body returned and the `retry_after` value | |

- [ ] **Resource 6 of 6 — `/news`**, endpoint `/api/x_bst_startuptrk/v1/news`.

| Assertion | What to record | Result |
| --- | --- | --- |
| Success shape | Status, and the four envelope members observed | |
| Pagination | Applied `limit` and `offset`; rows returned per page; **the exact `total_count` at each offset, which must read 4**; the ordered identifiers on each page; the remainder; overlap count, the three boundary results — a page past the end, a filter matching nothing and the refused `sysparm_offset` `10001` — which must read 0; and the negative control's absence | |
| `429` body | The exact body returned and the `retry_after` value | |

### 3c — the grid roll-up

- [ ] **18 of 18 cells recorded and passing.** Evidence: the counts below, and the resource and assertion of every cell that did not pass.

| Assertion | Resources | Cells | Passing | Cells not passing |
| --- | --- | --: | --: | --- |
| Success response shape | 6 | 6 | | |
| Pagination with an exact `total_count`, exact page membership, and the three boundaries | 6 | 6 | | |
| `429` body with `retry_after` | 6 | 6 | | |
| | **Total** | **18** | | |

6 resources x 3 assertions = 18. The nested sub-resource is asserted inside resource 2 and does not add a seventh row.

- [ ] **The suite result itself passes.** Evidence: the `BST REST suite — resources` suite result name, status and timestamp, and the six named test results.
- [ ] **The REST caller used for the read assertions holds only `x_bst_startuptrk.user`.** Every `GET` in the suite succeeds under the base role, which is what lets the success-shape assertion also confirm over HTTP that the premium keys are absent from every row. Evidence: the caller's user name and its single role. **One second caller exists**, holding exactly `x_bst_startuptrk.admin`, minted and removed inside `BST REST — startups` for the write assertions of section [3d](#3d--the-authorization-assertions); it is the caller for no read assertion, and its role set is asserted to be exactly one row.
- [ ] **The REST caller carries `web_service_access_only` `true`, so it cannot sign in to the user interface.** Evidence: the flag read from the `sys_user` record.
- [ ] **The REST caller's password was generated, and no password value appears in this package, in this checklist or in any transcript.** Evidence: the statement that a generated secret was used, and the secret-material search of [G-5](#g-5--secret-hygiene) returning zero hits across the manual-build guides.
- [ ] **The persistent shell profile has a named owner and an expiry, and the expiry is the day acceptance completes.** The disposable accounts expire with the tests that mint them, so the obligation attaches to `BST ATF REST caller`. Evidence: the owner and expiry recorded in the Teardown table of [`./manual-build/05-atf-test-suites.md`](./manual-build/05-atf-test-suites.md#the-evidence-to-record).
- [ ] **The REST caller has been torn down and its absence proved by query.** Residue query `R1` returns **0 records**, `R2` shows the shell bound to `bst.atf.retired`, and `R3` returns **0 records**. Evidence: the teardown table of [`./manual-build/05-atf-test-suites.md`](./manual-build/05-atf-test-suites.md#the-evidence-to-record), with all four residue results recorded.
- [ ] **Every `GET` in the suite succeeded under the base role held by `bst.atf.rest`**, which is what lets the success-shape assertion also confirm **over HTTP** that the premium keys are absent from every row — the same contract criterion 2 asserts on the serialised object. Evidence: the caller's user name, its single role, and the premium keys tested absent per resource. The caller's full posture is recorded against the second tick of section [3a](#3a--the-three-assertions-stated-once).

- [ ] **The REST caller was disposable, and its removal was guaranteed rather than assumed.** Each test mints its own caller at step 15 with **web-service access only** and exactly one role, binds the permanent `BST ATF REST caller` shell to it, and retires both at step 190. **A trailing cleanup step alone would not be enough**, because ATF stops a test at its first failed step, so the removal is carried by three independent mechanisms: the unconditional prefix sweep at the head of every step 15, the `try`/`finally` in both steps, and the operator's post-suite residue queries.
  **Evidence to record:** for mechanism 1, the step 15 output message of the **first** test in the suite, showing the unconditional sweep of every `bst.atf.rest.` account and the shell retirement performed **before** this run minted anything; for mechanism 2, that both step 15 and step 190 carry the shell retirement in a `finally`; for mechanism 3, the four post-suite residue queries.
  **Pass condition:** `R1` — `sys_user` where `user_name` starts with `bst.atf.rest.` — returns **0 records**, and `R2` — the `BST ATF REST caller` Basic Auth Configuration — returns **1 record whose user name reads `bst.atf.retired`**, which resolves to no account. A record returned by `R1`, or any other user name in `R2`, is a live credential: delete it and its `sys_user_has_role` rows by hand, then establish which test failed before its step 190 before trusting any result in that run.
- [ ] **Every write and every restoration in those two steps was asserted, not assumed.** The rebinding of the shell, the role grant, the role count, the retirement and the absence of residue afterwards are each asserted inside the step that performs them. Evidence: the assertion outcomes named in the step 30 and step 190 output messages.

### 3d — the authorization assertions

**The three assertions of section [3a](#3a--the-three-assertions-stated-once) are read-path assertions.** Every request behind them presents credentials and every one of them is a `GET`, so on their own they leave two halves of the API's access-control contract unevidenced: what happens to a caller who presents **no** credentials, and what happens to a caller who presents valid credentials but not the administrator role and then attempts to **write**. Both are asserted in the authorization block of `BST REST — startups`, steps 230 to 290 of [`./manual-build/05-atf-test-suites.md`](./manual-build/05-atf-test-suites.md#the-authorization-assertions--bst-rest--startups-only).

**One resource carries it for all thirty-one operations, and that is a construction argument, not a shortcut.** Every `sys_ws_operation` in the delivered Update Set carries `requires_authentication` `true` and `requires_acl_authorization` `true`, and every operation script opens with the same two calls in the same order — `RateLimitService.reject()`, then `RestResponseBuilder.rejectUnauthorisedRead()` on a read or `rejectUnauthorisedWrite()` on a write. There is no per-resource variation for a per-resource test to find.

| # | Claim | Request | Expected | Recorded value |
| --: | --- | --- | --- | --- |
| 1 | Authentication precedes everything | `GET /startups`, **no credentials** | `401`; the body carries **no** `result` and **no** `total_count`; **both** window keys still hold **0** rows | |
| 2 | A write is refused to a caller holding only the base role | `POST /startups`, base caller | `403` with body exactly `{"error": "Caller holds no Boston Startup Tracker administrator role"}`; **0** records written; the request **counted** — exactly one counter row reading exactly `1` | |
| 3 | A write succeeds for the scoped administrator role | `POST /startups`, administrator caller, **identical body** | `201`; the record exists exactly once; the response carries **both** premium keys | |
| 4 | Refusal precedes existence | `DELETE /startups/00000000000000000000000000000000` from **each** caller | base caller `403`; administrator `404` with `{"error": "Record not found"}` | |
| 5 | The administrator write round trip completes | `DELETE /startups/{created}`, administrator caller | `204` with an **empty** body, and the record gone | |

- [ ] **All five claims recorded and passing.** Evidence: the step 237, 243, 252, 263, 265 and 272 output messages.
- [ ] **The `401` assertion did not assert the platform's body text.** Only the status and the absence of `result` and `total_count` are asserted, because that body is platform-owned and release-dependent. Evidence: the step 237 output message.
- [ ] **The refused `POST` was counted.** The limiter runs ahead of the write guard, so a `403` still consumes budget — which is what the counter assertion in step 243 records, and what makes the ordering visible rather than assumed. Evidence: the row count and the count value.
- [ ] **The `201` response carried the two premium keys, from the same serialiser whose base-role output omits them.** `total_funding_usd` and `institutional_funding_last_5yrs` are **present** in the administrator's `201` body and **absent** in every base-role `200` body of section [3b](#3b--the-grid-six-resources-by-three-assertions). Evidence: both key lists, side by side. **Without this pairing the six read tests cannot distinguish a working field-level ACL from a serialiser that never emits those keys**, so this is the tick that makes criterion 2's omission evidence complete over HTTP.
- [ ] **The administrator caller held exactly one role, and it was `x_bst_startuptrk.admin`.** Not the platform `admin`, not `security_admin`. Evidence: the step 230 role-set assertion and its output message. Warning `W1` of the ATF guide applies to this block exactly as it applies to criterion 2.
- [ ] **The two `POST` requests differed only in the credential.** Same method, same path, same `Content-Type: application/json` header, same body. Evidence: both step configurations.
- [ ] **No standing administrator credential was created.** The administrator caller is ephemeral, `web_service_access_only` `true`, minted at step 230 and removed by the framework rollback, by the next run's step 230 sweep and by step 290. Evidence: residue query `R1` returning **0** records for the `bst.atf.rest.` prefix, which covers both callers, and `R2` returning **two** shells each reading `bst.atf.retired`.
- [ ] **Step 290's cleanup was asserted, not assumed.** Four window keys across both callers, the created record, and the administrator shell. The counter rows and the created record are written by inbound HTTP in their own sessions and are **not** rolled back with the test. Evidence: the step 290 output message.
- [ ] **What this block does not cover is recorded rather than implied.** `PUT` is asserted on no resource; the read-denial message `Caller holds no Boston Startup Tracker role` is reachable by no caller this package defines, because table-level read is granted to all three application roles; and claim 5 is omitted where the instance's REST step will not take a run-time value in `end_point`, in which case claim 4's `404` is the administrator's passage past the guard and step 290 removes the record. Evidence: which of the two endpoint bindings was available, and the omission if any.
- [ ] **Record whether responses are served compressed. Not acceptance-blocking, and it is not part of criterion 3's pass condition.** Issue one of the six list calls with `Accept-Encoding: gzip` and record the response's `Content-Encoding` header and its transferred size against its uncompressed size. This was not observable during validation — the hibernating instance's placeholder responder returns no `Content-Encoding` — and it is a property of the instance's web tier rather than of anything in the Update Set; the requirements state no compression requirement. The uncompressed ceiling is stated in [Response size](./api-reference.md#response-size-and-why-there-is-no-projection-parameter): a page of 50 startups with every text column at its declared maximum is 244.9 KiB. Evidence: the header observed and the two sizes, or the explicit statement that it could not be captured and why.

### Criterion 3 — pass condition

- [ ] **Six of six resources passing all three assertions** — success shape, pagination with an **exact** `total_count` of 4 **exact ordered page membership** and the three boundary results, and the `429` body matching the example exactly. Evidence: the 18 cells of section [3b](#3b--the-grid-six-resources-by-three-assertions) and the roll-up of section [3c](#3c--the-grid-roll-up).
- [ ] **All seven rate-limit tokens exercised**, including the nested executives token separately from `/founders`. Evidence: the seven tokens recorded against the determinism ticks of section [3a](#3a--the-three-assertions-stated-once).
- [ ] **Every `429` was attributed to `bst.atf.rest`, and every window key was left at zero rows.** Evidence: the `caller` value seeded per resource resolving to that user name, the two `window_key` values seeded per token, and the four-part key-ownership record of section [3a](#3a--the-three-assertions-stated-once) for each of the seven tokens.

- [ ] **No standing credential was created for this criterion.** Evidence: the disposable-caller tick of section [3c](#3c--the-grid-roll-up), and the ephemeral-administrator tick of section [3d](#3d--the-authorization-assertions).

- [ ] **All five authorization claims of section [3d](#3d--the-authorization-assertions) passing**, or claim 5 recorded as omitted with the reason. An unauthenticated request, a refused write and an accepted write are each evidenced.

Criterion 3 is met when, and only when, all five hold — the three grid conditions, the no-standing-credential condition, and the five authorization claims of section [3d](#3d--the-authorization-assertions). The pagination contract, the response envelope, the six resources with their 31 operations and the error contracts are specified in [`./api-reference.md`](./api-reference.md).

## Criterion 4 — scheduled flows ingest and clean on the configured cadence with zero unhandled errors

> **Prompt section 10.0, criterion 4.** The scheduled flows ingest and clean Crunchbase and LinkedIn data — or the sample-dataset substitute — on the configured cadence with **zero unhandled errors across three consecutive scheduled runs**.

### 4.0 — the route this criterion is evidenced on, decided before any run

**Read this before filling anything else in criterion 4.** Two flags in [`./gaps-and-flags.md`](./gaps-and-flags.md) determine which route the evidence below can come from, and they are **blockers rather than workarounds**:

| Flag | What is blocked | What is not blocked |
| --- | --- | --- |
| [`F14`](./gaps-and-flags.md#f14--the-crunchbase-authentication-model) | Live Crunchbase ingestion. No v4 user key has been supplied for the target instance, so the alias has nothing to bind and a live call cannot authenticate. | The whole Crunchbase flow, built and run on its forced-fallback route. |
| [`F15`](./gaps-and-flags.md#f15--linkedin-publishes-no-read-api-for-people-or-third-party-job-postings) | Live LinkedIn ingestion, **by construction**. No approved API product has been named, so [`./manual-build/03-flow-linkedin-ingestion.md`](./manual-build/03-flow-linkedin-ingestion.md) publishes no resource path and there is no live route to build or test. | The whole LinkedIn flow, built and run on its forced-fallback route. |

- [ ] **Record which route each flow was built on** — `fallback` or `live` — before the first counted run, and record it here rather than inferring it afterwards from a passing result. Evidence: the route recorded in [`./manual-build/01-connection-credential-aliases.md`](./manual-build/01-connection-credential-aliases.md) for each source, and the value of `x_bst_startuptrk.ingestion.source_mode`.
- [ ] **While either flag stands for a source, no result for that source may be labelled `live validated`.** The label is `fallback validated`, and a `[live]` suffix on a run that fell back is a defect in the evidence, not a formatting detail. Evidence: for each source, the flag that applies and the label used.
- [ ] **Live activation is gated on the live-activation register, and the register is checked here rather than assumed elsewhere.** `x_bst_startuptrk.ingestion.source_mode` must not read `live` for either source unless **every** row `LA1` to `LA9` of [the live-activation register](./gaps-and-flags.md#the-live-activation-register) carries a named owner, a date and a reference to where the evidence is recorded. Rows `LA1` to `LA4` are the operator's staging-retention and data-subject-erasure obligations; `LA5` to `LA8` are the platform owner's flow-execution-context retention, reader-role and logging-level actions; `LA9` is `glide.export.escape_formulas`, without which exporting the staging list to inspect it can execute unvalidated upstream text as a spreadsheet formula.
  **Evidence to record:** the value of `x_bst_startuptrk.ingestion.source_mode` per source, and the register's state — either every row owned, dated and evidenced, or the specific rows that are not.
  **Pass condition:** `source_mode` reads `fallback`, **or** it reads `live` and the register is complete. **Fail condition:** `source_mode` reads `live` with any row unowned, undated or unevidenced.
  **This item does not gate the build, the fallback path, or any `fallback validated` result.** Every artifact in this package is built, published and validated in full with the register empty, and criterion 4 is satisfiable from three clean fallback runs. What it gates is the moment real third-party personal data first enters the instance. On the instance recorded for this delivery `source_mode` is `fallback` and the register is empty, so this item **passes** — and would fail the moment either source were switched to `live` without the register being filled.
- [ ] **Criterion 4 remains satisfiable on the blocked route, and only because the prompt says so.** Section 10.0 criterion 4 accepts the sample-dataset substitute explicitly, so **three consecutive clean guard-passing fallback runs per flow satisfy it in full** — with the mode recorded on every one of the six, per section [4d](#4d--provenance-and-the-two-evidence-surfaces). Nothing about this criterion is waived, reduced or partially met by the blockers; only the *route* is fixed by them. Evidence: this box ticked with the six modes from section 4b.

**What must not be concluded.** A green ingestion suite under these blockers evidences the **cleaning rules and the orchestration**, not a working provider integration. Neither the Crunchbase nor the LinkedIn live path has been exercised anywhere in this delivery, and no line of this checklist may be read as saying otherwise.

### 4a — what a scheduled run is

> **A scheduled run is a flow execution that passed the flow's cadence guard and went on to do work.**
>
> **An execution that started, found the configured cadence had not yet elapsed and exited without ingesting is a no-op.** It is not a scheduled run, it does not count towards the three consecutive runs, and it is not evidence of anything. **No-op executions must not appear in the evidence below.**

This definition is load-bearing for the zero-unhandled-errors count: with the shipped cadence of 24 hours and an hourly trigger, roughly twenty-three of every twenty-four executions are no-ops, so an evidence set that admitted them would consist almost entirely of executions that did no work. The definition is stated identically in [`./deployment-runbook.md`](./deployment-runbook.md) and in [`./manual-build/02-flow-crunchbase-ingestion.md`](./manual-build/02-flow-crunchbase-ingestion.md); the cadence mechanism is recorded in [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md) and flagged in [`./gaps-and-flags.md`](./gaps-and-flags.md).

- [ ] **The two are distinguished before any run is counted.** A no-op records the cadence-guard comparison with `outcome="no_op"` and then exits, and publishes **no** run summary. A scheduled run records `outcome="proceed"`, proceeds to the source call or the fallback read, and **publishes a run summary carrying its provenance**. Evidence: for each counted run, the guard line and the published run summary.
- [ ] **The evidence surface is named, and it is the flow execution log.** Step 8 of each flow ends in a **Log action** whose Message is bound to the rendered evidence block, so each guard-passing execution writes one flow-log record for its context carrying a `run=` header line followed by one `key="value"` line per event. Reach it by opening the flow in Flow Designer, opening **Executions**, and reading the Log action's message on the execution — the underlying table is `sys_flow_log`. **This surface is not subject to `x_bst_startuptrk.logging.level` and is retained with the execution**, which is why it is preferred over `syslog`. Evidence: for each of the six runs, the `run=` header line as published.
- [ ] **The run was closed by part `8c`, and its `run_closed` line is the evidence.** `run_closed` is the **last line of every guard-passing execution**, and it carries `run`, `source`, `published`, `healthy`, `faults`, `marker_stamped`, `marker_verified`, `stamp` and `lease_released`. **A run with no `run_closed` line did not reach the end of step 8 and does not count as one of the three, whatever else it published.** A run whose line reports `healthy="false"` does not count either, and it deliberately stamps no completion marker — so the cadence does not advance and the next hourly trigger retries the source. Evidence: the `run_closed` line per run, verbatim.
- [ ] **`healthy` is `true`, and `faults` is empty, on every counted run.** `healthy` is `true` only when every member of the health predicate holds, which includes **`skipped` being zero**; `faults` is a comma-separated list of closed fault tokens and is empty when the run is healthy. A `run_incomplete` line names the faults instead. Evidence: the two values per run, and the absence of a `run_incomplete` line.
- [ ] **The durable completion marker moved forward, which is the independent proof that the publication was real.** `marker_stamped` and `marker_verified` both read `true`, and the source's entry in `x_bst_startuptrk.ingestion.last_run_provenance` now carries `<source>=<provenance>|succeeded|<stamp>|<run>` naming **this** run. **This is a second, independent proof rather than a restatement of the first**: part `8c` cannot execute unless part `8b` completed, and it stamps the marker only when every health member holds, so a marker that moved is proof of a healthy publication and a `run_closed` line naming faults is proof of the opposite. Evidence: the property value read after each run, and the run identifier it names.
- [ ] **Nothing in this section is taken from the flow's own summary in place of the published line.** The `run_summary` event carries the counters and the provenance; it carries **no** marker outcome, because the summary writer writes no property. The marker outcome lives only in `run_completed` and in the `run_closed` line. Evidence: confirmation that the counter columns below were read from `run_summary` and the four status columns from `run_closed`.
- [ ] **The evidence is read from the published run summaries only**, never from an ATF test result. Evidence: the run identifier of each of the six records read.
- [ ] **The cadence in force at the time of the runs is recorded.** The cadence is the property `x_bst_startuptrk.ingestion.cadence_hours`, shipped value `24`, clamped to the range 6 to 48. Evidence: the property value observed and the clamped value the guard reported in its log line.

### 4b — three consecutive guard-passing runs per flow

**Three consecutive guard-passing runs per flow — six runs in total.** Fill every cell of every row. A row with an empty cell is not a counted run.

#### Every counted run needs its own pending rows, reloaded and counted first

**A guard-passing run over a settled staging table ingests nothing and reports success.** `IngestionMapper.ingestStaging()` reads only rows in state `pending`, and a completed run advances every row it touched to `processed` or `rejected`. So the second and third runs of each flow would each process **zero** rows unless the dataset is reloaded — and a run that processed zero rows is not evidence that the flow ingests and cleans, which is what this criterion asks.

Before **each** of the six counted runs: reload the source files for that flow per [`./manual-build/06-staging-table-csv-import.md`](./manual-build/06-staging-table-csv-import.md), then **count the pending rows for that `source_system` and record the count before the run starts.**

| # | Flow | Run | Pending rows counted **before** the run | Expected |
| --- | --- | --: | --: | --: |
| 1 | `Crunchbase Ingestion` | 1 | | **33** |
| 2 | `Crunchbase Ingestion` | 2 | | **33** |
| 3 | `Crunchbase Ingestion` | 3 | | **33** |
| 4 | `LinkedIn Ingestion` | 1 | | **32** |
| 5 | `LinkedIn Ingestion` | 2 | | **32** |
| 6 | `LinkedIn Ingestion` | 3 | | **32** |

- [ ] **Each of the six runs was preceded by a reload and a recorded pending count**, and every count is non-zero. Evidence: the six counts above, each observed before its run rather than inferred afterwards.
- [ ] **The cadence guard was reset between consecutive runs, by one of the two permitted mechanisms.** The guard reads `AppProperties.getLastSuccessAt('<source>')`, which is the `stamp` of that source's entry in `x_bst_startuptrk.ingestion.last_run_provenance` — **never a log record**, so deleting one resets nothing and destroys evidence this criterion needs. [Resetting the guard between counted runs](#resetting-the-guard-between-counted-runs) publishes both mechanisms, the scripts and the five obligations. Evidence: per run, the guard's reported `hours_elapsed`, the cadence in force, and the mechanism used.

#### Resetting the guard between counted runs

**The guard compares elapsed time against the cadence, so two runs minutes apart cannot both pass it.** The cadence is clamped to a floor of 6 hours, so three consecutive guard-passing runs per flow are at least 12 hours apart unless the state the guard reads is moved. There are exactly **two** permitted ways to do that, and **deleting a log record is not one of them**: the guard reads `AppProperties.getLastSuccessAt('<source>')`, which is the `stamp` of that source's entry in the scoped property `x_bst_startuptrk.ingestion.last_run_provenance`. It reads no log record at all, so removing one changes nothing and runs two and three no-op while appearing to have been reset.

| # | Mechanism | When to use it | What it costs |
| --- | --- | --- | --- |
| **1** | **Wait the cadence.** Set `x_bst_startuptrk.ingestion.cadence_hours` to its floor of `6` before the evidence window, run each flow at intervals of six hours or more, and restore the shipped `24` afterwards. | Preferred where the elapsed time is available. Nothing writes the run state but the flows themselves. | At least 12 hours per flow, and the cadence property is written twice — captured and restored like any other. |
| **2** | **Capture, reposition, restore.** Capture the property's raw value verbatim, back-date **only** the counted source's `stamp` past the cadence between runs, and restore the captured value once the last counted run has been recorded. | Where the window cannot span 12 hours. | Three obligations rather than none, all three below, and a written record of every value the property held. |

**Mechanism 2, exactly.** Run each script in **Scripts - Background** with the application picker on **Boston Startup Tracker**. Step 2 edits the **raw property string**, changing the counted source's `stamp` field and nothing else, and copies every other segment through byte for byte; it rebuilds no segment from parsed members, because `AppProperties` sanitises a run token as it parses one and recognises only the two sources plus a legacy bare value, so a rebuild could alter or drop what it did not recognise. Neither script invents a marker where none exists, and both report what they wrote.

**Step 1 — capture, before the first counted run.** Read the property and record the value verbatim in the evidence table below. `sys_properties` where `name` **is** `x_bst_startuptrk.ingestion.last_run_provenance`; copy the whole `value` including any second source's entry.

**Step 2 — reposition, between counted runs.**

```javascript
(function () {
    // ---- substitution: the source whose next run must pass the guard ----
    var SOURCE = 'crunchbase';                 // or 'linkedin'
    // ---- end of substitution ----
    var KEY = 'x_bst_startuptrk.ingestion.last_run_provenance';
    var props = new AppProperties();

    // gs.setProperty is not on the scoped GlideSystem surface, and this script runs with
    // the application picker on Boston Startup Tracker. The property record is therefore
    // read and written directly -- the same record AppProperties._readRunState() reads,
    // so the write and the read-back below cannot disagree through a cached value.
    function readRaw() {
        var row = new GlideRecord('sys_properties');
        row.addQuery('name', KEY);
        row.setLimit(1);
        row.query();
        if (!row.next()) {
            return '';
        }
        var stored = row.getValue('value');
        return String(stored === null ? '' : stored);
    }
    function writeRaw(value) {
        var row = new GlideRecord('sys_properties');
        row.addQuery('name', KEY);
        row.setLimit(1);
        row.query();
        if (!row.next()) {
            gs.info('[bst.cadence.reset] ' + KEY + ' does not exist on this instance, so ' +
                'there is nothing to reposition. Stopping without a write.');
            return false;
        }
        row.setValue('value', value);
        if (!row.update()) {
            gs.info('[bst.cadence.reset] the write to ' + KEY + ' was refused. Stopping. ' +
                'Confirm the account holds x_bst_startuptrk.admin and can write ' +
                'sys_properties.');
            return false;
        }
        return true;
    }

    // Every decision below is made against the RAW string, and every segment that is
    // not the counted source's is copied through byte for byte. Rebuilding a segment
    // from parsed members would not be safe: AppProperties sanitises a run token when
    // it parses one, and readRunMarkers() recognises only crunchbase, linkedin and a
    // legacy bare value, so a rebuild could silently alter or drop what it did not
    // recognise. This script alters exactly one field of exactly one segment.
    var raw = readRaw();
    gs.info('[bst.cadence.reset] captured verbatim: "' + raw + '"');

    var markers = props.readRunMarkers();
    if (markers.legacy !== '') {
        gs.info('[bst.cadence.reset] the property holds the legacy bare value "' +
            markers.legacy + '", which carries no stamp. getLastSuccessAt answers an ' +
            'empty value already, so the guard reports hours_elapsed=-1 and the next ' +
            'execution passes. Nothing to reposition — record this value as row 1 and ' +
            'restore it unchanged at step 3.');
        return;
    }
    var mine = markers[SOURCE];
    if (!mine) {
        gs.info('[bst.cadence.reset] ' + SOURCE + ' carries no marker, so the guard ' +
            'already reports hours_elapsed=-1 and the next execution passes. Nothing ' +
            'to reposition.');
        return;
    }
    if (mine.state !== 'succeeded') {
        gs.info('[bst.cadence.reset] ' + SOURCE + ' carries a "' + mine.state + '" claim. ' +
            'Do not reposition it: either a run is in flight, or one ended without ' +
            'releasing its lease. Resolve that first — repositioning a claim would hide it.');
        return;
    }

    // Back-date past the cadence, measured from the recorded stamp rather than from
    // now, so a stamp that is already old is not moved forward.
    var cadence = props.getCadenceHours();
    var back = new GlideDateTime(mine.stamp);
    back.addSeconds(-1 * (cadence + 1) * 3600);

    var segments = raw.split(';');
    var rewritten = 0;
    var i = 0;
    for (i = 0; i !== segments.length; i++) {
        if (segments[i].trim().toLowerCase().indexOf(SOURCE + '=') !== 0) {
            continue;                                  // copied through untouched
        }
        var head = segments[i].substring(0, segments[i].indexOf('=') + 1);
        var parts = segments[i].substring(head.length).split('|');
        if (parts.length !== 4) {
            gs.info('[bst.cadence.reset] the ' + SOURCE + ' segment does not carry four ' +
                'fields, so it is not the form this script edits. Stopping without a write.');
            return;
        }
        parts[2] = back.getValue();                    // the stamp, and only the stamp
        segments[i] = head + parts.join('|');
        rewritten++;
    }
    if (rewritten !== 1) {
        gs.info('[bst.cadence.reset] expected exactly one ' + SOURCE + ' segment, found ' +
            rewritten + '. Stopping without a write.');
        return;
    }

    var next = segments.join(';');
    if (!writeRaw(next)) {
        return;
    }

    // Read back, and prove the untouched segments really were untouched.
    var after = readRaw();
    var before_others = raw.split(';').filter(function (s) {
        return s.trim().toLowerCase().indexOf(SOURCE + '=') !== 0;
    }).join(';');
    var after_others = after.split(';').filter(function (s) {
        return s.trim().toLowerCase().indexOf(SOURCE + '=') !== 0;
    }).join(';');

    gs.info('[bst.cadence.reset] wrote: "' + after + '"');
    gs.info('[bst.cadence.reset] write_landed=' + (after === next) +
        '; other_segments_identical=' + (after_others === before_others) +
        '; getLastSuccessAt(' + SOURCE + ')=' + props.getLastSuccessAt(SOURCE) +
        '; cadence=' + cadence + 'h. Both flags must read true, and when they do the ' +
        'next execution of that flow passes the guard.');
})();
```

**Step 3 — restore, after the last counted run is recorded.**

```javascript
(function () {
    // ---- substitution: the value step 1 captured, pasted verbatim ----
    var CAPTURED = '';
    // ---- end of substitution ----
    var KEY = 'x_bst_startuptrk.ingestion.last_run_provenance';

    // gs.setProperty is not on the scoped GlideSystem surface, and this script runs with
    // the application picker on Boston Startup Tracker. The property record is written
    // directly, and read back from the record so the confirmation cannot come from a
    // cached value.
    var row = new GlideRecord('sys_properties');
    row.addQuery('name', KEY);
    row.setLimit(1);
    row.query();
    if (!row.next()) {
        gs.info('[bst.cadence.reset] ' + KEY + ' does not exist on this instance. ' +
            'Stopping without a write.');
        return;
    }
    row.setValue('value', CAPTURED);
    if (!row.update()) {
        gs.info('[bst.cadence.reset] the write to ' + KEY + ' was refused. The captured ' +
            'value has NOT been restored. Confirm the account holds ' +
            'x_bst_startuptrk.admin and can write sys_properties, then re-run this step.');
        return;
    }
    var back = new GlideRecord('sys_properties');
    back.addQuery('name', KEY);
    back.setLimit(1);
    back.query();
    var now = back.next() ? String(back.getValue('value') === null ? '' : back.getValue('value')) : '';
    gs.info('[bst.cadence.reset] restored=' + (now === CAPTURED) + '; value now: "' + now + '"');
})();
```

**Record every value the property held.** A reposition that is not recorded is indistinguishable afterwards from a run that legitimately took the interval.

| # | Point in the window | Property value, verbatim | `getLastSuccessAt` for the counted source | Recorded by |
| --- | --- | --- | --- | --- |
| 1 | Captured before the first counted run | | | |
| 2 | After repositioning for run 2 | | | |
| 3 | After repositioning for run 3 | | | |
| 4 | After the last counted run, before restoring | | | |
| 5 | Restored, and confirmed byte-identical to row 1 | | | |

- [ ] **The mechanism used is recorded, and it is 1 or 2.** Evidence: which of the two, and for mechanism 1 the cadence value in force during the window beside the six run timestamps.
- [ ] **No run-summary log record was deleted to reset anything.** The guard reads the run-state property and never a log record, so a deletion resets nothing and destroys evidence this criterion needs. Evidence: the statement that none was deleted, and the six run summaries still readable at sign-off.
- [ ] **On mechanism 2, all five rows of the table above are filled, and row 5 is byte-identical to row 1.** A restore that is asserted rather than read back is not a restore. Evidence: the two values side by side, and the `restored=true` line the step 3 script prints.
- [ ] **The other source's entry was untouched by every reposition.** Running the Crunchbase window cannot move the LinkedIn flow's cadence, and vice versa. The step 2 script edits the counted source's **stamp field alone**, inside the raw property string, and copies every other segment through byte for byte — then reads the property back and reports `other_segments_identical`. Evidence: that flag reading `true` on every reposition, and the other source's entry read from rows 1 and 4 of the table above and compared.
- [ ] **No reposition was performed over a `running` claim.** The step 2 script refuses one and says why; a claim means a run is in flight or ended without releasing its lease, and repositioning would hide it. Evidence: the script's output line for every reposition.

#### The six counted runs

**One evidence table, and every column of it comes from the run's own published `run_summary` event or from the health members part `8c` reports.** An earlier revision carried two overlapping tables for these same six runs, which made it possible to fill one and leave the other empty while both looked complete. There is now exactly one.

| # | Flow | Run | Timestamp (UTC) | Guard | `processed` | `rejected` | `duplicates` | `unmatched` | `rule3_deviations` | `skipped` | `errors` | `published` | `healthy` | `faults` | `marker_stamped` | Unhandled errors | Provenance |
| --- | --- | --: | --- | --- | --: | --: | --: | --: | --: | --: | --: | --- | --- | --- | --- | --: | --- |
| 1 | `Crunchbase Ingestion` | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 2 | `Crunchbase Ingestion` | 2 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 3 | `Crunchbase Ingestion` | 3 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 4 | `LinkedIn Ingestion` | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 5 | `LinkedIn Ingestion` | 2 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 6 | `LinkedIn Ingestion` | 3 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| | **Aggregate** | | | **6 of 6 proceed** | **must be > 0 on every row** | | | | | **must be 0** | **must be 0** | **must be `true`** | **must be `true`** | **must be empty** | **must be `true`** | **must total 0** | |

**Guard** reads `proceed` on every counted row; a `no_op` means the row records a no-op and the row is replaced by a genuine scheduled run. Every numeric column is taken **verbatim from the `run_summary` event** of that run's published block — never computed by subtraction, and never inferred from the entity tables. The four status columns — `published`, `healthy`, `faults` and `marker_stamped` — are taken **verbatim from the `run_closed` line** of the same execution, which is the last line that execution wrote. **Provenance** reads exactly `live` or `fallback`, taken from the `run_summary` event's `provenance` member; no third value is valid.

- [ ] **Every counted run is data-bearing: `Records processed` is non-zero on all six rows.** A zero means the run found nothing pending and demonstrated nothing, however cleanly it completed. **A row with `Records processed` of zero is not a counted run and must be replaced**, not explained. Evidence: the **Records processed** column, six non-zero values.
- [ ] **The counters of each run match the exact expectations for its source.** Over a full reload the flows produce the values below, derived from the designed defects catalogued in [`../sample-data/README.md`](../sample-data/README.md). A different distribution means a file was edited or the transform is mismapped, not that the criterion was met more loosely.

  | Flow | `processed` | `rejected` | `duplicates` | `unmatched` | `skipped` | `errors` |
  | --- | --: | --: | --: | --: | --: | --: |
  | `Crunchbase Ingestion` | **26** | **6** | **1** | **6** | **0** | **0** |
  | `LinkedIn Ingestion` | **26** | **6** | **0** | **5** | **0** | **0** |

  **The LinkedIn figures assume its precondition 7 holds** — the Crunchbase flow has already run, so the parent `Startup` records exist. Run the LinkedIn flow against an empty startup table and every one of its rows is **rejected** for an unresolvable parent, which is [guide 03's documented behaviour](./manual-build/03-flow-linkedin-ingestion.md#62--the-shared-startup-upsert-path) rather than a fault. Record the order the two flows were run in.

  **`skipped` of zero is the expected value, not a missing one**, because `skipped` counts an upsert failure — a row that passed every cleaning rule and then could not be written. Any non-zero `skipped` is a defect to investigate before the run is recorded. **`duplicates` for LinkedIn cannot be non-zero at all**, because within-batch deduplication inspects only `startup` entries and this flow ingests none. Evidence: the five counters per run, eighteen values in total across the six runs.

- [ ] **Every counted run reports `skipped` zero, `errors` zero, `published` `true`, `healthy` `true`, `faults` empty and `marker_stamped` `true`.** `errors` is the subset of `skipped` that is an incoming row whose own write failed, so `skipped` zero implies `errors` zero; a run reporting `errors` above zero names its fault `write_failures` rather than the wider `operational_skips`. `skipped` counts operational failures rather than cleaning outcomes — a write the platform would not complete, or a join row that would not insert — so a non-zero value is a genuine fault and a run carrying one is not fit to count. **Rejections are different and do not bear on health**: a record rejected by a cleaning rule is the specified behaviour working correctly. Evidence: the five columns above, read from the two sources named beneath the table.
- [ ] **Crunchbase Ingestion — three consecutive guard-passing runs, zero unhandled errors.** Evidence: rows 1 to 3 above.
- [ ] **LinkedIn Ingestion — three consecutive guard-passing runs, zero unhandled errors.** Evidence: rows 4 to 6 above.
- [ ] **The three runs per flow are consecutive.** No guard-passing execution of that flow falls between them unrecorded. Evidence: the run identifiers in order, and confirmation that the log holds no guard-passing execution of that flow between the first and the third.
- [ ] **The wiring-only pass of each flow guide is excluded from these six rows.** Each flow guide requires two manual runs, and only its **data-bearing pass** is evidence — see [Verification](./manual-build/02-flow-crunchbase-ingestion.md#verification--one-manual-run). A wiring pass over an empty staging table completes successfully with a row count of zero and must not be recorded here. Evidence: confirmation that each of the six rows corresponds to a run whose pending count was recorded non-zero above.

#### Isolation between the three runs

**Each of the three runs needs its own staged rows, and the run before it must have settled.** The fallback branch reads every row at `import_state` `pending` for its source, so three runs over one load would give the first run every row and the second and third none — three runs of which two processed nothing.

- [ ] **Before each counted run, the staging table holds pending rows for that source, and they are the rows intended for that run.** Load one batch per run from [`./manual-build/06-staging-table-csv-import.md`](./manual-build/06-staging-table-csv-import.md), each with its own `import_run` token. Evidence: the pending row count and the `import_run` token immediately before each of the six runs.
- [ ] **After each counted run, no row it claimed is left at `pending`.** Every claimed row carries `processed`, `rejected` or `error`. Evidence: the pending count for that source immediately after each run, which must be zero.
- [ ] **Replay is idempotent.** Re-present one batch that has already been ingested — reset those staging rows to `pending` with the same values and the same `import_run` — and confirm the next run **updates** rather than duplicates. The natural keys are `name` plus `headquarters_location` for a startup, `name` for an investor, `startup` plus `name` for a founder or executive, `startup` plus `round_date` plus `round_type` for a funding round, and `startup` plus `url` for a job posting. Evidence: the row count per entity table before and after the replay, unchanged; the replay run's `processed` count, non-zero; and the `x_bst_startuptrk_m2m_round_investor` row count, unchanged.
- [ ] **The replay run is recorded separately and does not displace one of the three.** It is an idempotency check, not a cadence run. Evidence: its run identifier, marked as such.

### 4c — per-record skips are expected behaviour, not errors

**Per-record skips arising from the four cleaning rules are expected behaviour and are not errors.** They are counted separately from unhandled errors, and **only unhandled errors bear on this criterion**. A run that rejected records and completed is a clean run. The specified failure semantics are that a per-record error is logged, that record is skipped, and the run continues — a run that halted on the first bad record is a failure of this criterion even though it reported the rejection.

Tick each rule once per flow, using the run in which it was exercised.

- [ ] **Rule 1 — trim whitespace on all string fields.** Evidence: a stored string that arrived with leading or trailing whitespace, shown trimmed.
- [ ] **Rule 2 — deduplicate incoming Startup records on `name` plus `headquarters_location`, case-insensitively. Evidenced from `Crunchbase Ingestion` only.** Evidence: the duplicate pair supplied, the single entity row that resulted, the loser's staging row carrying the outcome code `code=duplicate_in_batch` with the reason text `duplicate startup in the same batch` in the run log line for the same reference, and the negative-control pair that shares a name but differs in headquarters and was **not** deduplicated.

  **This rule cannot be evidenced from `LinkedIn Ingestion`, and a tick claiming it was is void.** Within-batch deduplication inspects only entries whose record type is `startup`. `LinkedIn Ingestion` ingests `founder`, `executive` and `job_posting` — not one of them is a `startup` — so a LinkedIn batch never reaches the deduplication key at all, and its `duplicates` counter is **0** by construction rather than by outcome.

- [ ] **Rule 2's shared-identity consequence — evidenced from `LinkedIn Ingestion`.** What the LinkedIn flow demonstrates is the other half of the shared identity: a child row **resolves onto the Startup record the Crunchbase run created** rather than creating a second one. Evidence: a founder, an executive and a job posting each carrying the `sys_id` of the same pre-existing startup; confirmation that the LinkedIn run created **no** Startup record; and two rows refused by the composite parent key — one whose complete key matches nothing, rejected with `no startup carries the name and headquarters location`, and one carrying only `startup_name`, rejected with `the row carries no parent headquarters location, and the startup key is the name together with the headquarters location`.
- [ ] **Rule 3 — normalise the choice columns to their enumerated values, and log an unmatched value.** An unmatched value is stored as `Other` on a list that declares an `Other` member and is **left unwritten** on a list that does not; either way the event is logged. Evidence: one unmatched value of each kind, the outcome observed, and the logged event naming the column and the supplied value.
- [ ] **Rule 3's unresolvable half is recorded as a flagged deviation, not as compliance.** The rule requires an unmatched value to be mapped to `Other`. **Six of the eleven delivered choice lists declare no `Other` member** — `startup.funding_stage`, `startup.employee_count_range`, `investor.type`, `fundinground.round_type`, `jobposting.remote_type` and `jobposting.seniority` — and the prompt declares its choice lists binding and complete, so on those six the rule cannot be satisfied without changing a frozen enumeration. The delivered behaviour leaves the value unwritten, logs it with `deviation="true"` and an outcome string naming the conflict, and counts it as `rule3_deviations`. **Record this as a partial implementation of rule 3.** Evidence: the `rule3_deviations` count per run from section 4b, one `choice_unmatched` event carrying `deviation="true"` with its outcome string, and the corresponding entry in [`./gaps-and-flags.md`](./gaps-and-flags.md).
- [ ] **`rule3_deviations` and `unmatched` are read as separate counters.** `unmatched` counts every unmatched value including the coerced ones, so it is greater than or equal to `rule3_deviations` on every run. A single folded counter satisfies neither requirement. Evidence: both columns of section 4b.
- [ ] **Rule 4 — reject a record missing a mandatory field rather than inserting a partial row.** Evidence: the rejected record, the reason naming the missing field, and confirmation that no partial entity record was inserted.
- [ ] **Skip and continue.** Evidence: from a single run, a non-zero processed count **and** a non-zero rejected count, which together establish that the run neither halted on the bad record nor inserted a partial one. Record also that **every record type the flow writes produced both** a rejection and a processed row, which is what proves the run continued *within* each type rather than merely across the batch — the batch is processed in a fixed record-type order, so a positional reading of the log proves nothing.

### 4d — provenance, and the two evidence surfaces

**The criterion explicitly accepts the sample-dataset substitute.** Three clean `fallback` runs per flow satisfy it — **provided the mode is recorded for every run.** Recording it is what keeps a fallback result from reading as validated live integration.

**There are two provenance surfaces and they are not interchangeable.** The mechanical reason is that the test framework rolls back the data a test creates, so a provenance row or property written inside a test does not survive the run.

| Surface | Written by | Survives the run | Read by |
| --- | --- | --- | --- |
| **Scheduled-run provenance** | **Part `8c` of action A7, `Publish <source> Run Evidence`, and nowhere else** — on a real scheduled execution it calls `IngestionLogger.markRunComplete()`, which calls `AppProperties.completeRun()` to turn this source's `running` marker in `x_bst_startuptrk.ingestion.last_run_provenance` into a `succeeded` entry. The `run_summary` event is emitted earlier and elsewhere, by `IngestionLogger.writeRunSummary()` inside `ingest()` in action A4, which **writes no property at all**. | **Yes.** It is written outside any test transaction, and the property is subject to neither the logging threshold nor log retention. | **This criterion**, section 4b above |
| **ATF result label** | The setup step of each flow test, which **derives** the mode and labels the result `fallback validated` or `live validated`, and **writes no run summary of its own** | **No.** The framework rolls back data a test creates. | The test report, and section 4e below |

**Two attributions in that table are load-bearing, and getting either wrong invalidates the evidence:**

- **The property writer and the summary writer are different actions, and only one of each exists.** `markRunComplete()` is called from part `8c` of A7 and from nowhere else — not from the flow root, not from A4, and not from the reconciliation action. `writeRunSummary()` is called from `ingest()`'s `finally` inside A4 and from nowhere else, and it writes no property. Every ingestion phase runs on **one** `IngestionLogger` instance inside A4, and the run summary carries that instance's counters, which is why a summary whose counters are all zero is the signature of a build that bypassed the single ingestion call — **treat it as an invalid evidence record, not as a clean run of an empty batch**, and check which construction the flow calls before anything else.
- **The ATF setup step writes no run summary.** It derives the mode from the source-mode property and the alias state, and labels. A setup step that called `writeRunSummary()` would write an all-zero summary before any ingestion, which a later assertion could find and pass against — reporting a successful ingestion of nothing.

- [ ] **The run-summary records read for section 4b came from executions that made the single `ingest()` call in A4**, and none of them carries all-zero counters. Evidence: per run, the action the flow invoked and the summary's counter members as published.

**`LinkedIn Ingestion` can only ever be `fallback`.** LinkedIn publishes no read API for any of that flow's three record types: no public route enumerates a company's people, and the Job Posting API is a write API rather than a route for reading a third party's postings. Its live path is an organisation-identity probe and never an acquisition. **Three `fallback` runs are therefore the best evidence that flow can produce, in any credential posture, and that is a property of the provider rather than of this instance.** It is flagged in [`./gaps-and-flags.md`](./gaps-and-flags.md) and specified in [`./manual-build/03-flow-linkedin-ingestion.md`](./manual-build/03-flow-linkedin-ingestion.md).

- [ ] **Every one of the six runs in section 4b carries a recorded provenance of `live` or `fallback`.** Read it through the delivered accessor `new AppProperties().getRunProvenance('<source>')` immediately after each counted run — it answers the empty string until that source's marker reads `succeeded`, so an empty answer is itself a finding — and cross-check it against the `provenance` member of that run's `run_summary` event. Evidence: the six values from the accessor beside the six from the log.
- [ ] **The run-state property holds one entry per source, in the delivered form, and the whole raw value is recorded.** `x_bst_startuptrk.ingestion.last_run_provenance` serialises one entry per source as `source=provenance|state|stamp|run`, joined by `;`, with `state` reading `succeeded` on a completed run and `running` while one is in flight. `stamp` is `yyyy-MM-dd HH:mm:ss` and is the value `getLastSuccessAt('<source>')` returns and the cadence guard compares. Evidence: the property's raw value read after the last counted run, entry by entry.
- [ ] **Where any run is `fallback`, the staging table held **pending** rows for it to read.** The fallback branch reads `x_bst_startuptrk_ingest_staging` and selects only rows in state `pending`, so a table whose rows a previous run already settled demonstrates nothing however cleanly the run completed. Evidence: the pending count recorded before each run in section 4b.
- [ ] **Where any run is `fallback`, the reason is recorded, and it is a member of that flow's closed set.** The two sets differ because the two providers do:
  | Flow | Closed `fallback_reason` set |
  | --- | --- |
  | `Crunchbase Ingestion` | `forced`, `alias_unresolved`, `alias_ambiguous`, `connection_unresolved`, `http_status`, `transport`, `malformed`, `budget_reached` |
  | `LinkedIn Ingestion` | `no_live_read_api`, `forced`, `alias_unresolved`, `alias_ambiguous`, `connection_unresolved`, `api_version_retired`, `http_status`, `transport`, `malformed`, `budget_reached` |
  **An empty live result is not a fallback reason on either flow.** A response that legitimately matches nothing is a successful, complete read of nothing: the run resolves `live` with an empty row set and is recorded as a clean live run that ingested nothing. Treating it as a failure would replace a correct empty live read with stale rows from the sample dataset and would then label the run `fallback` — a false statement about where the data came from. **`no_rows` and `no_organizations` are therefore not members of either set**, and a run reporting either has not been built to this specification. Evidence: the `fallback_reason` per run, checked against its flow's set above, together with the alias state that produced it — the credential posture of [`./manual-build/01-connection-credential-aliases.md`](./manual-build/01-connection-credential-aliases.md#credential-posture), or the `x_bst_startuptrk.ingestion.source_mode` property set to force it.


**`LinkedIn Ingestion` can only ever be `fallback`.** LinkedIn publishes no read API for any of that flow's three record types: no public route enumerates a company's people, and the Job Posting API is a write API rather than a route for reading a third party's postings. Its live path is an organisation-identity probe and never an acquisition. **Three `fallback` runs are therefore the best evidence that flow can produce, in any credential posture, and that is a property of the provider rather than of this instance.** It is flagged in [`./gaps-and-flags.md`](./gaps-and-flags.md) and specified in [`./manual-build/03-flow-linkedin-ingestion.md`](./manual-build/03-flow-linkedin-ingestion.md).

- [ ] **The credential posture is read from one place and restated nowhere.** [`./manual-build/01-connection-credential-aliases.md`](./manual-build/01-connection-credential-aliases.md#credential-posture) is the single factual statement of readiness for this package. Evidence: the posture recorded there at the time of the six runs — `provisioned` or `unprovisioned` per alias — and nothing inferred from any other document.

### 4e — the ATF flow tests and their labels

Two ATF tests, suite `BST FLOW suite — ingestion`, one per flow. **Neither test starts a flow.** Each calls the orchestrator action's own entry point `IngestionMapper.ingestStaging()` — the identical call, with the identical arguments, that the delivered action A4 makes — over staging rows it seeded itself, and asserts the flow's wiring separately from the platform's own flow and action records. `D-105` carries that decision, and [4f](#4f--what-the-atf-suite-does-not-evidence-and-the-evidence-that-closes-the-gap) states the boundary it leaves and the evidence that closes it. Each result is labelled `fallback validated` or `live validated`, and the label follows the setup step's derivation rather than the author's expectation.

| # | Test — canonical name | Flow | Result | Label recorded | Test result record |
| --- | --- | --- | --- | --- | --- |
| 1 | `BST FLOW — Crunchbase Ingestion [fallback]` | `Crunchbase Ingestion` | | | |
| 2 | `BST FLOW — LinkedIn Ingestion [fallback]` | `LinkedIn Ingestion` | | | |

**Both names carry a mode suffix in square brackets, and there is no unsuffixed form of either.** `BST FLOW — Crunchbase Ingestion [fallback]` and `BST FLOW — Crunchbase Ingestion [live]` are the only two permitted spellings of test 1, and exactly one is on the record at any moment. On the instance recorded for this delivery both aliases are unprovisioned, so the two names in force are the `[fallback]` forms above. A bare `BST FLOW — Crunchbase Ingestion` is not a valid test name and must not appear on a record, in a row of this document, or in any other document.

- [ ] **Both flow tests pass.** Evidence: the two test result names, their statuses and the suite result.
- [ ] **Both carry a label, and the label matches the mode the run actually used.** The suffix is not chosen by the author — it follows the setup step's derivation from the source-mode property and the alias state. If the derived provenance and the test name disagree, the name is wrong. A `[live]` name is not left on a run that fell back. Evidence: the derived provenance read from each result's step 20 output message, the label, and the test name as it stands.
- [ ] **The label appears in the two places the guide requires**, so it cannot be lost when a result is exported: the step 20 output message carrying the derivation, and the step 100 output message carrying the summary the ingestion wrote. Evidence: both messages per test.
- [ ] **The suite evidence and the run-summary evidence are recorded separately.** The suite result evidences the cleaning rules; the run-summary records of section 4b evidence the cadence and the error count. Neither substitutes for the other. Evidence: confirmation that section 4b was filled from run-summary records and not from test results.

- [ ] **Half A called the orchestrator entry point and asserted the exact object it returned.** `IngestionMapper.ingestStaging(runId, sourceSystem, importRun, provenance)` at step 40, with `accepted` and `rejected` at the **top level**, `processed` **only** under `summary`, and the summary's member named **`logged`** — `recorded` is not a member of it and asserting one compares `undefined` against `true`. Evidence: the step 40 output message of each test, and the parked object the later steps read.
- [ ] **All four cleaning rules were asserted against what the ingestion wrote**, not against a reimplementation of it: rule 2 and reference resolution at step 50, rule 3 normalisation at step 60, rule 4 mandatory-field rejection at step 70, rule 1 trimming and the ingestion effects at step 90. Evidence: the four output messages per test.
- [ ] **Every staging row the batch claimed reached a terminal state.** Step 80's `Record Query` for this test's `import_run` token with `import_state` `pending` returns **zero** rows. Evidence: the query result per test.
- [ ] **The run summary the ingestion emitted was asserted, and no second one exists.** Step 100 asserts exactly one `run_summary` line for this run's token with its exact counters, and that **no all-zero summary exists for the run** — the assertion that catches a `writeRunSummary()` call reintroduced into the setup step. Evidence: the step 100 output message per test.
- [ ] **Skip the record and continue the run was asserted per record type, not as a total.** One call reports a non-zero `accepted` **and** a non-zero `rejected`, and **every** record type in the batch produced both a rejection and a processed row — Crunchbase 2 refused and 3 processed startups, 1 and 3 investors, 1 and 1 funding round; LinkedIn 1 and 2 founders, 1 and 1 executive, 1 and 2 job postings. A halt-on-first-error implementation reports rejections and nothing processed for the type it stopped on, wherever the sort placed it. Evidence: the per-type counts from each test's step 40 and step 70 messages.
- [ ] **Half B asserted the flow and action wiring out of the platform's own tables.** Step 110 covers all eight wiring rows: both flows resolved from `sys_hub_flow` by **internal name** — `crunchbase_ingestion` and `linkedin_ingestion`, not the display labels — with **exactly one match each**, both `Published` and `Active`, their **seven** actions each present, published and ordered, the flow calling **all seven** alongside exactly one `If`, and the credential alias bound by name. Evidence: the step 110 output message per test.
  **A test without half B passes for the wrong reason**: half A exercises the mapper, and a flow that was never wired together would still let it pass. Evidence: confirmation that step 110 exists in both tests and that all eight rows hold.
- [ ] **Neither test wrote a system property, and that was verified rather than assumed.** `ingestStaging()` reaches `writeRunSummary()`, which emits the `run_summary` event and **writes no property**; the completion marker is stamped **only** by `IngestionLogger.markRunComplete()`, which **no step of either test calls**.
  **Evidence to record:** the step 120 output message of each test, which asserts no `running` claim on either source, `source_mode` still reading `fallback` and no legacy bare value, and which writes the resulting property value into the step output. Record that value verbatim.
- [ ] **The suite was run outside this criterion's evidence window.** Evidence: the timestamp of the suite run against the timestamps of the six runs in section 4b, and residue query `R4` recorded between the two.
- [ ] **The suite evidence and the scheduled-run evidence are recorded separately.** The suite result evidences the ingestion rules and the flow wiring; the published run summaries of section 4b evidence the cadence, the guard, the branch, the publication and the error count. Neither substitutes for the other, and [4f](#4f--what-the-atf-suite-does-not-evidence-and-the-evidence-that-closes-the-gap) maps which is which flow step by flow step. Evidence: both records, kept apart.

### 4f — what the ATF suite does not evidence, and the evidence that closes the gap

**The ATF flow suite starts the published flow.** Each of the two tests drives the flow record itself through `sn_fd.FlowAPI`, twice — once with the cadence marker set so the guard must refuse, once so it must proceed — and asserts on the resulting `sys_flow_context`. There is no Flow Designer ATF **step** configuration, so the start is an on-demand foreground run rather than a trigger firing. That is the boundary, and this criterion must not be signed off as though it did not exist. The construction is recorded at `D-247`, which retired `D-105`.

| Flow step | Covered by the ATF suite | Evidence required here instead |
| --- | --- | --- |
| 1 — Cadence guard | **Yes, down both branches** — the refusal and the proceed, from a real execution | — |
| 2 — Resolve the source mode | **Yes** — the branch taken is asserted from the execution's own evidence | — |
| 3 — Call the source through the alias | **No, and it cannot be** — no credential is provisioned and a test must make no live third-party call | Guide [`./manual-build/01-connection-credential-aliases.md`](./manual-build/01-connection-credential-aliases.md)'s connection test, plus the manual run |
| 4 to 8 — fall back, clean, write, log, summarise | **Yes** | The suite result, together with the six items below |
| The **scheduled trigger** starting the flow by itself | **No** — `FlowAPI` starts it on demand and bypasses the trigger | The three counted runs of section [4b](#4b--three-consecutive-guard-passing-runs-per-flow), read from published run summaries |

**A green suite is therefore not evidence that the trigger fired or that a live call succeeded.** It **is** evidence that the flow record executed, that the guard decided both ways, and that the cleaning rules held. Record it for what it is.

**Seven** items must each be recorded, because each corresponds to a way this criterion has been signed off while the thing it measures was broken. **Any one of them missing leaves the criterion unmet even with six clean runs in section 4b.**

- [ ] **The typed live envelope was driven, and its untyped control failed as specified.** The live path's single seam is the envelope that declares a `record_type` per call site. A row without one is rejected by the mapper — **every** row — so an untyped batch produces a run that accepts nothing while reporting no transport failure at all: a silent, total failure that a fallback-only test cannot see, because a staging row always carries its record type. Evidence: from the flow test's live-envelope step, the number of typed envelope rows accepted, and from its untyped control, `0` accepted with every row rejected. Record also that the step's output message names the envelope **synthetic**, so it is not read as live-integration evidence.
- [ ] **Discovery is bounded.** The bounds are declared in the discovery action's own script, not as system properties: a `PAGE_SIZE` of 100 rows per request and a `MAX_CALLS` ceiling of 200 HTTP calls across all passes, with keyset pagination that advances on the last row's identifier and terminates on a short or empty page. Evidence: the two constants as built, the number of source records one counted run acquired, the number of pages and calls it made against the 200-call ceiling, and `0` occurrences of the `cursor_missing` fault code. On the fallback path, the run-ceiling result instead: rows consumed, rows left `pending`, and `ceiling_reached`. A run whose population was a single hard-coded record is not evidence of a bounded discovery; it is evidence of no discovery. **No cursor persists between runs**, and none needs to: the natural-key matcher makes a re-enumerated population idempotent, which the repeat-batch item below is what proves.
- [ ] **The cadence state is per source and is persisted, not mined from the log.** It is held as one entry per source inside the single property `x_bst_startuptrk.ingestion.last_run_provenance`, in the form `source=provenance|state|stamp|run`, and is read through `AppProperties.getLastSuccessAt(source)`. Evidence: the `crunchbase` and `linkedin` entries read back after the counted runs, and confirmation that raising `x_bst_startuptrk.logging.level` to `warn` does **not** change the guard's decision. A guard that read the application log would be silently disabled by that property, and one flow's run would satisfy the other flow's cadence.
- [ ] **A repeat of the identical batch added nothing.** Evidence: the per-table row counts and the record identifiers before and after a second run over the same input, showing the **same set** and not merely the same count. A scheduled flow re-reads its population every cadence window, so a build without working natural keys doubles the data on the second run and this is the only item that would notice.
- [ ] **A partially linked record was reported as such, not as processed.** **There is no `partial` counter, and none may be invented**: `writeRunSummary()` publishes exactly `processed`, `rejected`, `skipped`, `errors`, `duplicates`, `unmatched`, `rule3_deviations`, `events_dropped`, `provenance` and `source_system`, where `errors` is the subset of `skipped` that is an incoming row whose own write failed. A funding round whose participant links could not all be reconciled is handled by `_applyEntry()` instead — the entry is **not** marked processed, its staging row settles at `error`, and `skipRecord()` counts it in **`skipped`**. Evidence: the `skipped` count of every counted run — `0` on a clean run — together with confirmation that no staging row of the run sits at `error`, and that the entity row count and the join row count agree. A round that was written while some of its participant links were not is not a success.
- [ ] **The unmatched-choice count was read from the counter, not derived.** Evidence: the `unmatched` member of each run summary, and confirmation it came from `IngestionLogger.counters()`. Accepted minus written is a different quantity that coincides on some batches; a build reporting the derived form leaves the real counter untested and the criterion's cleaning evidence unsupported.

- [ ] **No flow test wrote the ingestion state property, so there was nothing to restore.** Both orchestrators finish by calling `IngestionLogger.markRunComplete()` **when a flow runs them** — that call writes this source's `succeeded` entry into the single property `x_bst_startuptrk.ingestion.last_run_provenance`, and that entry's stamp is the value the cadence guard compares. **The ATF tests do not reach it**: they call `ingestStaging()`, which reaches `writeRunSummary()` and writes no property, and part `8c` — the only caller of `markRunComplete()` — exists only inside a flow execution. A test that wrote the marker would silently disable the next scheduled run of that source for up to a full cadence window while passing, which is why the design avoids the write rather than reversing it. Evidence: the step 120 output message of each test, and residue query `R4` run after the suite, showing **no `running` state for either source** and `x_bst_startuptrk.ingestion.source_mode` still reading `fallback`. A `running` state left for either source blocks the next scheduled run of that source until the cadence-aged takeover clears it, so it is recorded and corrected before any run is counted.

### Criterion 4 — pass condition

- [ ] **Three consecutive guard-passing runs per flow, six runs in total**, every row of section 4b filled. Evidence: the six run rows of section [4b](#4b--three-consecutive-guard-passing-runs-per-flow).
- [ ] **Zero unhandled errors** across all six runs, with per-record skips counted separately and not counted against this total. Evidence: the **Unhandled errors** column of section [4b](#4b--three-consecutive-guard-passing-runs-per-flow), which must total zero, and the five ticks of section [4c](#4c--per-record-skips-are-expected-behaviour-not-errors).
- [ ] **The provenance of every run recorded** as `live` or `fallback`, and every run-summary record read came from an execution that made the single `ingest()` call in A4, with its marker stamped by part `8c` of A7. Evidence: the **Provenance** column of section [4b](#the-six-counted-runs) and the ticks of section [4d](#4d--provenance-and-the-two-evidence-surfaces).
- [ ] **Every counted run was data-bearing**, with a non-zero pending count recorded before it and a non-zero `processed` after it, and its five counters matching the exact per-source expectations. Evidence: the pre-run pending table and the counter table of section [4b](#every-counted-run-needs-its-own-pending-rows-reloaded-and-counted-first).
- [ ] **All seven items of section [4f](#4f--what-the-atf-suite-does-not-evidence-and-the-evidence-that-closes-the-gap) recorded**, so the criterion cannot be met on fallback and orchestrator evidence alone while the live seam, the discovery bound, the cadence state, idempotence, partial-link reporting or the unmatched counter remains broken.

- [ ] **Every counted run did work and was closed cleanly.** `processed` is non-zero, `skipped` is zero, and `published`, `healthy` and `marker_stamped` all read `true` with `faults` empty, on all six rows. Evidence: those columns of section [4b](#4b--three-consecutive-guard-passing-runs-per-flow), with the counters read from each run's `run_summary` event and the status values read from its `run_closed` line.
- [ ] **Each counted run's completion marker moved forward.** The source's entry in `x_bst_startuptrk.ingestion.last_run_provenance` names that run with state `succeeded`. This is the independent proof that the publication was real rather than self-reported: the marker is stamped only when every health member holds. Evidence: the property value read after each of the six runs, and the run identifier each names.
- [ ] **The provenance of every run recorded** as `live` or `fallback`, with a `fallback_reason` wherever it reads `fallback`. Evidence: the **Provenance** column of section [4b](#4b--three-consecutive-guard-passing-runs-per-flow) and the ticks of section [4d](#4d--provenance-and-the-two-evidence-surfaces).
- [ ] **Rule 3 is recorded as PARTIAL, not as met.** Evidence: the flagged-deviation ticks of section [4c](#4c--per-record-skips-are-expected-behaviour-not-errors).

Criterion 4 is met when, and only when, all seven hold.

**This criterion is not met by the ATF suite, by a green build, or by the presence of the two flows.** It is met only by six recorded executions on an instance. Until section 4b carries six filled rows, criterion 4 is **NOT MET** and sign-off is blocked — there is no partial credit and no inference from artifact presence. Two things follow that a reader must not confuse:

| Situation | Criterion 4 status |
| --- | --- |
| The flows are built and published, the ATF suite passes, and no scheduled execution has been observed | **NOT MET.** Nothing in section 4b can be filled from an ATF result. |
| Six executions observed, all `fallback`, each labelled with its `fallback_reason` | **MET.** The criterion explicitly accepts the sample-dataset substitute. |
| Six executions observed, `processed` zero on any of them | **NOT MET.** That row is replaced by a run that did work. |
| `LinkedIn Ingestion` has never produced a `live` run | **Not a failure of this criterion.** No `live` run is possible for that flow; see section 4d. |

The two flows, their cadence guards, the four cleaning rules and the run-summary record are specified in [`./manual-build/02-flow-crunchbase-ingestion.md`](./manual-build/02-flow-crunchbase-ingestion.md) and [`./manual-build/03-flow-linkedin-ingestion.md`](./manual-build/03-flow-linkedin-ingestion.md); the fallback dataset the staging table holds is loaded by [`./manual-build/06-staging-table-csv-import.md`](./manual-build/06-staging-table-csv-import.md).


## Criterion 5 — all five Service Portal routes render and navigate as specified

> **Prompt section 10.0, criterion 5.** All 5 Service Portal routes render and navigate per prompt section 5.0, verified by walkthrough against the enumerated route list, **with the startup inclusion filter confirmed active on Home / Search**.

The portal URL suffix is `bst`, and routing is query-parameter based. Every route resolves at `/bst?id=<page>`, with a record-scoped page adding `&sys_id=<record>`. **Those addresses describe where a route lives; they are not how this criterion reaches it.** The criterion requires the routes to *navigate*, so the walkthrough enters every route by activating a rendered control and reads the address bar only to confirm where the click landed. The pages, their widgets and their navigation controls are specified in [`./manual-build/04-service-portal-pages-and-widgets.md`](./manual-build/04-service-portal-pages-and-widgets.md), whose routing table enumerates fifteen hops and shows every route carrying at least one incoming hop.

### 5.0 — the entry condition, checked before any route is walked

**Read this before walking anything.** Criterion 5 is the only success criterion whose subject **does not exist when the deployment finishes**. The other four are evidenced against artifacts the Update Set installs; this one is evidenced against artifacts a human builds afterwards.

The delivered Update Set carries **zero** `sp_portal`, `sp_page`, `sp_widget` and `sp_theme` records. That is a design consequence rather than an omission: only tables carrying the `update_synch` dictionary attribute are captured into `sys_update_xml`, the Service Portal tables do not carry it, and adding it to a table that lacks it out of the box is unsupported. The portal is therefore built by hand from [`./manual-build/04-service-portal-pages-and-widgets.md`](./manual-build/04-service-portal-pages-and-widgets.md), which is why that guide exists and why [`./manual-build-instructions.md`](./manual-build-instructions.md) sequences it fourth.

**The eleven post-commit gates passing does not mean the portal exists.** Every one of them reads a table, a role or the scope record; not one touches a portal record. A deployment can clear [`./validation-gates.md`](./validation-gates.md) in full, be recorded ACCEPTED by [`./deployment-runbook.md`](./deployment-runbook.md), and still have five unbuilt routes. Reading a green runbook as evidence for this criterion is the single most likely way to record criterion 5 as met without having tested anything.

Until guide 04 has been executed in full, criterion 5 is **unevaluated** — which is a distinct outcome from *not met*. Recording it as not met asserts a walkthrough happened and failed; recording it as unevaluated states the truth, that its subject had not been built. The summary table at the end of this document accepts either.

Confirm all four counts below before starting 5a. Any zero means the guide has not been run, or has not been finished, and the walkthrough cannot begin.

| # | What must exist | Expected | Built by |
| --- | --- | --- | --- |
| 1 | `sp_portal` with url suffix `bst` | exactly 1 | guide 04, step 1 |
| 2 | `sp_theme` bound to that portal | exactly 1 | guide 04, step 2 |
| 3 | `sp_page` records `bst_home`, `bst_company`, `bst_investor`, `bst_dashboard`, `bst_account` | exactly 5 | guide 04, step 3 |
| 4 | `sp_widget` records, the eight `bst-*` widgets | exactly 8 | guide 04, step 4 |

- [ ] **All four counts hold, and the portal's Main menu binding resolves.** The menu is checked here rather than in 5a because it is the only incoming control for two of the five routes: if it is unbound, three of the fifteen hops cannot be taken and 5a fails for a build reason rather than a navigation one. Evidence: the four counts as returned, and the menu record the portal's **Main menu** field points at.

### 5a — the five routes

Walk each route. Record that it rendered, that its widgets loaded, and that navigation into and out of it works.

**Every route must be entered by activating a rendered control, and a pasted address is not acceptable evidence.** The criterion is that the routes *navigate*, not merely that they resolve. A typed or pasted URL proves the page record exists and the widget renders; it proves nothing about whether a user can ever get there, and a route with no incoming control is unreachable in use however well it renders when addressed directly. So the walkthrough **starts once, at `/bst`,** and reaches all five routes from there by clicking. The address bar is read to confirm where a click landed; it is never typed into.

The single permitted exception is a **record-scoped** page — `bst_company` and `bst_investor` — in the two negative tests at the end of this section, which exist precisely to check what a malformed or missing `sys_id` does and cannot be provoked by a well-formed link.

The incoming controls are built in [`./manual-build/04-service-portal-pages-and-widgets.md`](./manual-build/04-service-portal-pages-and-widgets.md), whose routing table enumerates **fifteen navigation hops** and shows every one of the five routes carrying at least one incoming hop. Hops 13 to 15 are the three header-menu items — **Home**, **Dashboard** and **Account** — which render on every page for every one of the three scoped roles; they are the only incoming controls for `bst_dashboard` and `bst_account`, so if the portal's **Main menu** binding or those three items are missing, this section fails and the fix is a build fix, not a walkthrough workaround.

- [ ] **Entry — open `/bst` once, with no `id` parameter, and confirm it resolves to Home / Search.** Every subsequent hop in this section starts from here. Evidence: the address opened, the page it resolved to, and the three header-menu links visible on it.
- [ ] **Route 1 of 5 — Home / Search, page record `bst_home`.** Widgets `bst-startup-search` and `bst-startup-results`. Reached at entry, and re-reached later by the header-menu **Home** item from any other page. Evidence: the rendered state, the control used to return to it, and the outgoing hop taken **by clicking a result card** into `bst_company`.
- [ ] **Route 2 of 5 — Company Profile, page record `bst_company`.** Widget `bst-company-profile`. **Entered by clicking a result card on Home / Search**, not by address. Evidence: the control clicked, the resulting URL read from the address bar, the startup rendered, and the outgoing hop taken **by clicking a lead or participating investor in the Funding tab** into `bst_investor`.
- [ ] **Route 3 of 5 — Investor Profile, page record `bst_investor`.** Widget `bst-investor-profile`. **Entered by clicking an investor link on the company profile**, not by address. Evidence: the control clicked, the resulting URL, the investor rendered, the `portfolio_count` displayed, and the outgoing hop taken **by clicking a portfolio row** into `bst_company`.
- [ ] **Route 4 of 5 — Dashboard / Trends, page record `bst_dashboard`.** Widgets `bst-trends-kpi` and `bst-trends-charts`. **Entered by clicking the header-menu `Dashboard` item**, not by address. Evidence: the control clicked, the resulting URL, the rendered state including which chart mode drew, and the return hop taken **by clicking the header-menu `Home` item**.
- [ ] **Route 5 of 5 — Account Management, page record `bst_account`.** Widgets `bst-account-summary` and the embedded `bst-premium-upsell`. **Entered by clicking the header-menu `Account` item**, not by address. Evidence: the control clicked, the resulting URL, the effective role and entitlements displayed, and the return hop taken **by clicking the header-menu `Home` item**.

Record, for each route, the control that took you into it. **The Entered by column may not read "typed URL" or "pasted link" for any row.**

| # | Route | Page record | Entered by (control clicked) | Rendered | Outgoing hop taken | Note |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Home / Search | `bst_home` | | | | |
| 2 | Company Profile | `bst_company` | | | | |
| 3 | Investor Profile | `bst_investor` | | | | |
| 4 | Dashboard / Trends | `bst_dashboard` | | | | |
| 5 | Account Management | `bst_account` | | | | |
| | **Aggregate** | | **5 of 5 entered by a rendered control** | | | **5 of 5 required** |

- [ ] **The three header-menu items render on every one of the five pages.** Walk all five routes and confirm **Home**, **Dashboard** and **Account** are present and working on each, so no page is a dead end. Evidence: the five pages and the three links observed on each.
- [ ] **The three header-menu items render under each of the three scoped roles.** Repeat the check under impersonation as `x_bst_startuptrk.user`, `x_bst_startuptrk.premium_user` and `x_bst_startuptrk.admin`. A role filter on a menu item would orphan `bst_account` for the roles it filtered out, which is the specific defect these items exist to prevent, so a link missing under any one role fails this item. Evidence: the three roles and the three links observed under each.
- [ ] **Every one of the fifteen hops in the guide's routing table was exercised through its rendered control.** The five route rows above cover the primary path; walk the remainder — including hop 10, the premium treatment in the search results that reaches `bst_account` for the base role. Evidence: the hop numbers exercised, the control used for each, and the destination reached. A hop that cannot be exercised because its control is absent is a build defect and is recorded as one.
- [ ] **A record-scoped page given no `sys_id`, or one that resolves to no readable record, renders a warning and a link back to Home / Search.** It renders neither an empty panel nor an error. Test both `bst_company` and `bst_investor`. **This is the one place in this section where an address is entered directly**, because a well-formed link cannot produce the condition. Confirm the warning's own link back to Home / Search works by clicking it. Evidence: the two addresses tried, what each rendered, and the result of clicking the recovery link.

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
- [ ] **`institutional_funding_last_5yrs` takes no part in the predicate.** Seed or use a passing startup with `institutional_funding_last_5yrs` false and confirm it still appears in the results. Evidence: the record used, its flag value, and its presence in the results. The resolution of this point is recorded in [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md) and flagged in [`./gaps-and-flags.md`](./gaps-and-flags.md).
- [ ] **Record the execution plan of this query — it has never been observed. Not acceptance-blocking, and it is not part of criterion 5's pass condition.** This predicate is the one hot query in the application with no supporting predicate index, and the reasoning for why no index would serve it — a leading-wildcard `CONTAINS` on `headquarters_location` and a two-value `active` — is derived from the declared index definitions rather than from a database plan. See [Declared indexes](./data-model.md#the-inclusion-filter-carries-no-predicate-index-and-no-index-would-serve-it). On the woken instance, run the Home / Search read and capture the plan — **System Diagnostics > Stats > Slow Queries**, or a session SQL debug of the same read — and record whether an index is used and which. Evidence: the query captured and the plan observed, or the explicit statement that the plan could not be captured and why. A plan that contradicts the reasoning is a documentation defect to correct, not a criterion failure.

### 5d — the premium upsell treatment under the base role

**The walkthrough for this section is performed under impersonation**, by a user holding exactly one scoped role and none of the elevated platform roles, exactly as [criterion 2](#criterion-2--all-three-roles-enforce-field-level-acls-on-100--of-the-seven-premium-fields) requires. A walkthrough conducted as the instance administrator displays all seven premium fields and does not test enforcement; a result obtained that way must not be recorded here.

- [ ] **Under `x_bst_startuptrk.user`, every gated field or gated tab region renders the upsell treatment.** No blank, no empty cell, no zero and no dash appears where a premium field was denied. Evidence: the surfaces walked and what rendered in each gated position.
- [ ] **`bst-premium-upsell` appears on the company profile, the investor profile and the account summary.** These are its three hosts. Evidence: the three pages and the widget's presence on each.
- [ ] **Under `x_bst_startuptrk.premium_user` and under `x_bst_startuptrk.admin`, every premium field renders its value and the upsell widget does not appear.** Evidence: the seven fields observed under each of the two roles, and the absence of the upsell widget.
- [ ] **A non-premium column renders under `x_bst_startuptrk.user` on the same screen.** `x_bst_startuptrk_startup.headquarters_location` serves. Evidence: the column and the value rendered. This establishes that the denial came from the field-level control rather than from nothing being readable.

### 5e — the supported viewport

- [ ] **The walkthrough was performed at 1024 pixels wide or above.** 1024 pixels is the declared supported floor of this portal; a narrower viewport is out of scope and a defect observed only below it is not a defect of this criterion. Evidence: the viewport width used for the walkthrough.
- [ ] **The ragged lower edge on the Dashboard / Trends route was recognised as the recorded gap and not raised as a defect.** The two chart panels sit in one row at `col-md-6 col-lg-6` and are sized by their own bucket counts, so their lower edges differ — **161.00 px** at 1024 pixels and **172.11 px** at 1366 and above, the larger figure decomposing into 58.11 px of chart and 114.00 px of companion table. Confirm only that **nothing clips, scrolls vertically or overlaps** and that the whole difference is empty page inside the shorter panel's own column. This is gap **G8** in [`./gaps-and-flags.md`](./gaps-and-flags.md#g8-in-detail--the-unequal-lower-edges-of-the-two-dashboard-chart-panels), accepted as delivered because every remedy is closed by the zero-hard-coded-values or layout-primitives rule; closing it needs a written exception or an equal-height mechanism the design system does not provide. Evidence: the observation that neither panel clips or overlaps.

### 5f — the rendered quality gates at the floor

**These five are properties of the *rendered* portal, not of the guide, and each has a stated failure mode that a walkthrough performed without them would not surface.** Perform them at a 1024-pixel viewport, on a browser whose accessibility tree and colour picker are available.

- [ ] **One `h1` per route, and no skipped level.** Read the accessibility tree on each of the five routes. Exactly one first-level heading, the outline descending `h1` → `h2` → `h3`, and no heading element whose content is a bare number — the KPI figure is a `<p class="bst-kpi-value h2">`. Evidence: the outline read off each route and the element that carries its `h1`.
- [ ] **The contrast check prints `FAILURES: 0`, and the page agrees with it.** Run the check in [the portal guide](./manual-build/04-service-portal-pages-and-widgets.md#the-contrast-check) and record its last line. Then sample two values on the rendered page with the browser's colour picker: a `Premium` marker must be white on `#17607d` and `.text-muted` must be `#595959`. Finding `#5bc0de` or `#777777` means the theme did not compile or was not saved — those two defaults measure **2.09:1** and **4.11:1** and both fail WCAG 2.1 AA. Evidence: the check's last line and the two sampled values.
- [ ] **Nothing overflows with the widest data the schema permits.** Seed one startup whose `logo_url` is a 2000-by-50 wordmark, whose `website` is 255 characters and whose `name` is 100 characters with no space in it, plus one job posting with a 150-character title and one news article with a 255-character title. At 1024 pixels no card, panel, table or list item exceeds its column and the document carries no horizontal scrollbar. Evidence: the seeded records and the observation at 1024 pixels.
- [ ] **Each state is announced once.** Force a load failure on `bst-startup-results` — remove the caller's role mid-session and retry — and confirm with a screen reader that the failure is announced **once**, by the visible `.alert.alert-danger[role="alert"]`, and that the polite status region says nothing. Then confirm the premium notices are `role="region"` with an `aria-labelledby` rather than `role="alert"`. Evidence: the announcement heard and the roles read off the two notices.
- [ ] **One submit control in the search form.** Tab through `bst-startup-search` and confirm `Search, button` is announced once and `Clear, button` once. Press Enter in each of the three fields and confirm each submits the whole criteria object. Evidence: the controls announced and the three Enter submissions.

A failure in any of the five is a defect in the build, and none of them is visible to a walkthrough that only checks that a page rendered.

### Criterion 5 — pass condition

- [ ] **Five routes rendering and navigating**, 5 of 5, **each entered by activating a rendered control rather than by a pasted address**, with the three header-menu items present on every page under all three scoped roles and all fifteen hops of the guide's routing table exercised. Evidence: the completed route table of section [5a](#5a--the-five-routes), whose Entered by column names a clicked control on every row, plus the hop list and the per-role menu observation.
- [ ] **Five tabs on the company profile** — Overview, Funding, People, Jobs, News — and no sixth. Evidence: the five tab ticks and the tab-strip reading of section [5b](#5b--exactly-five-tabs-on-the-company-profile).
- [ ] **The excluded startup absent from Home / Search but present in the administrator list view**, both halves recorded. Evidence: the seeded record and both halves of section [5c](#5c--the-inclusion-filter-confirmed-active).
- [ ] **The upsell treatment visible to the base role** wherever a gated field or tab region is denied, gathered under impersonation. Evidence: the four ticks of section [5d](#5d--the-premium-upsell-treatment-under-the-base-role).
- [ ] **The rendered portal passes its own quality gates at the floor**, 5 of 5: one `<h1>` per route with no skipped level, `FAILURES: 0` from the contrast check with the `Premium` marker measured on the page, no overflow at 1024 pixels with the widest data the schema permits, one announcement per state, and one submit control in the search form. Evidence: the five ticks of section [5f](#5f--the-rendered-quality-gates-at-the-floor).

Criterion 5 is met when, and only when, all five hold. The portal, the theme, the five pages, the five tabs, the eight widgets, the upsell substitution rule and the viewport floor are specified in [`./manual-build/04-service-portal-pages-and-widgets.md`](./manual-build/04-service-portal-pages-and-widgets.md); the inclusion predicate is specified in [`./data-model.md`](./data-model.md).

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
- [ ] **Both flow tests are present, passing, labelled, and each carries both halves.** **Neither test starts its flow**, because no Automated Test Framework step configuration can: half A calls the orchestrator entry point and half B asserts the delivered flow and action records. A test carrying only half A evidences the mapper and not the flow, and does not satisfy flow coverage — so the evidence is the **step 110 wiring assertion** in each test, alongside its step 40 orchestrator assertion. What neither half reaches is recorded in section [4f](#4f--what-the-atf-suite-does-not-evidence-and-the-evidence-that-closes-the-gap) and evidenced by the manual runs of the two flow guides. Evidence: the two labelled results, and the step 40 and step 110 output messages per test, from section [4e](#4e--the-atf-flow-tests-and-their-labels).
- [ ] **Nothing usable survived the run.** All four post-suite residue queries `R1` to `R4` of [`./manual-build/05-atf-test-suites.md`](./manual-build/05-atf-test-suites.md#post-suite-residue-queries) are recorded, with `R1` and `R3` returning **zero** records, `R2` returning one record reading `bst.atf.retired`, and `R4` showing no `running` state for either source with `source_mode` still `fallback`. **An unrecorded residue query blocks this gate**: a surviving disposable caller is a live credential and a surviving impersonation user holds a scoped role. Evidence: the four query results.
- [ ] **The suite count is 10 and the test count is 36.** Evidence: the two observed totals from the table above.

**Two conditions block delivery.**

- [ ] **Blocking condition 1 — delivery is blocked if any table or any resource lacks a passing test.** A suite count of 10 with a test count below 36 means a cell, a resource or a table is uncovered. Evidence: the observed suite and test counts, and the name of anything uncovered.
- [ ] **Blocking condition 2 — if ATF execution is not enabled on the instance, this gate cannot be evaluated at all.** It is not failed and not partially met; it is unevaluable, and no delivery claim about coverage can be made. [`./deployment-runbook.md`](./deployment-runbook.md) asserts that prerequisite **before** the Update Set is imported, so the condition is discovered before any deployment work is done. Evidence: the ATF runner property value and the test-designer role held, copied from [section B](#b--deployment-gates).

### H2 — rule compliance

Three items, one per project rule. Each is a check performed against the delivered artifacts.

- [ ] **Rule 1 — Explainability.** **The structural half of this rule is checked once, at gate [G-9](#g-9--governance-completeness)**, and is not re-checked here: the decision log's four mandated columns and its coverage of every named decision, the traceability matrix resolving in both directions with zero unresolved entries, and the critical-decisions document's five risk-ordered entries all appearing in the log. Record `G-9`'s result against this item rather than repeating its evidence. What this item adds, and what `G-9` does not check, is the **placement of rationale**: **no rationale text appears anywhere in the delivery except the log and the critical-decisions document** — every code comment, platform record description and prose document states only what an artifact does or how to build it, which requirement it implements, and which decision row governs it; every *why*, alternative and risk lives in those two files alone. **The scan covers every artifact of the delivery, not only the code and the guides**: all thirty files, including the eleven prose documents that are neither code nor a manual-build guide, and including the presentation's **HTML** comments as well as its script and style blocks. Recorded at `D-384`, which amends `D-151` and `D-308`. Evidence: `G-9`'s recorded result, and two scan results — first, a search for the **announcing forms** across every file, being a heading, a bold lead-in or a table column heading naming *Why*, *Rationale* or *Alternatives*, which must report **zero** outside those two files; second, a search of every script body and every `description` and `hint` field for comparative or justifying prose such as "rather than", "because" or "trade-off", whose surviving hits must each be a statement of two outcomes of the delivered behaviour rather than an argument for a choice, per the boundary at `D-308`.

  **The scan covers all delivered code, not only the Update Set.** Three bodies of code ship in this delivery, and every one is in scope for this check:
  - **The Update Set** — the script bodies inside [`../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml`](../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml), namely the Script Includes, the business rules, the scheduled job and the advanced access-control scripts, together with every record `description` field.
  - **The executive deck** — [`../../blitzy-deck/boston-startup-tracker-servicenow-executive-summary.html`](../../blitzy-deck/boston-startup-tracker-servicenow-executive-summary.html) is delivered code as much as it is a document: it carries **HTML comments, a CSS comment set in each of its two `<style>` blocks, and JavaScript comments throughout its inline script**. The render policies that script implements — the serial render queue, the retry ceiling, the webfont wait, the animation-frame delay, the render-health thresholds, the suppressed-error posture and the deferral of a container that is not on the shown slide — are exactly the kind of non-obvious choice whose *why* the rule confines to the log. Its comments must therefore read as *what plus a pointer*, and the rationale must be found in the log instead.
  - **The validator** — [`../scripts/validate_update_set_xml.py`](../scripts/validate_update_set_xml.py), its module docstring, its function docstrings and its comments.

  **Evidence:** the four column headers as written; the log's row count and the confirmation that its identifiers run contiguously with none reused; the matrix's row count in each direction with zero unresolved entries; and, for **each** of the three bodies of code above, the scan performed and its result — the number of comment or description blocks inspected, and either zero rationale passages or the list of offenders with the correction made. A scan that covered only the Update Set does not satisfy this item.

- [ ] **Rule 2 — Executive Presentation.** Every one of the sub-items below is a separate check against the delivered deck at [`../../blitzy-deck/boston-startup-tracker-servicenow-executive-summary.html`](../../blitzy-deck/boston-startup-tracker-servicenow-executive-summary.html). **Where a sub-item restates a check gate [G-8](#g-8--deck-structure) already makes — the section count, the visual per section, the four slide types, the bullet and word ceilings, the emoji prohibition, the pinned versions and fonts, the integrity attributes, the advisory disposition and the canonical-theme identity — the two are worded identically on purpose and `G-8` is the stable identifier to record the result against. The sub-items that follow those are this rule's own, and `G-8` does not cover them.** A deck that satisfies the structural items and fails a content item is **not** compliant, so none of them may be waived.

  - [ ] **Opens with no build step and no local file dependency.** Evidence: the file opened directly in a browser, and the confirmation that it references no local asset — the theme is inlined, not linked.
  - [ ] **Section count is 12 to 18.** Evidence: the counted number of top-level `<section>` elements.
  - [ ] **Every section carries at least one non-text visual** — a Mermaid diagram, a KPI card, a styled table or a Lucide SVG icon, **the same four kinds gate [G-8](#g-8--deck-structure) admits and no others**. Evidence: one line per section naming its visual.
  - [ ] **The four slide types are all present and correctly applied**: a title slide, divider slides, content slides and a closing slide. Evidence: the class on each section, and the count of each type.
  - [ ] **Every content slide carries at most 4 bullets.** Evidence: the `<li>` count per content slide.
  - [ ] **Every content slide carries at most 40 visible body words**, counting all rendered text except the slide's own heading and except Mermaid diagram source. Evidence: the counted word total per content slide, listed one per line, with the method stated.
  - [ ] **The closing slide's takeaway heading is 3 to 6 words and it carries at most 3 bullets**, and it is not measured against the content-slide caps. Count the whitespace-separated tokens of its `<h2>` and the `<li>` elements inside `class="slide-closing"`. The delivered figures to reproduce are a **5-word** heading and **3** bullets. Evidence: its class, the heading token count with the heading quoted, and the bullet count.
  - [ ] **Zero emoji anywhere.** Evidence: the emoji scan hit count, which must be `0`.
  - [ ] **Every icon is a Lucide icon supplied through the `data-lucide` attribute**, and no other icon system or inline glyph is used. **Select the unreplaced placeholders as `i[data-lucide]`, never as `[data-lucide]`.** The library copies the attribute onto the `<svg>` it generates, so after a successful pass `[data-lucide]` still returns the full **63** — every one of them an `svg`, none an `i` — and a gate asserting that selector reaches zero fails against a correct deck. Evidence: the count of `svg.lucide` elements (**63**), the count of `i[data-lucide]` placeholders still unreplaced (**0**), and the number of distinct icon names resolved (**28**).
  - [ ] **No fenced code block appears on any slide.** The deck is for non-technical leadership; Mermaid diagram containers are not code blocks. Evidence: the confirmation that no `<pre>` element other than a `pre.mermaid` container exists.
  - [ ] **Every Mermaid diagram sits in its own dedicated container, with automatic start disabled**, and the render pass is invoked on **both** the ready event **and** every slide change — which is what confirms the render call is wired to both hooks. There are **three** registrations, not two: `ready`, `slidechanged` and `slidetransitionend`. **Rendering is gated on slide presence**, so the count to expect on first load is **0 of 5**, not 5 of 5 — the first slide carries no diagram, the ready pass iterates all five containers and skips each one, and every diagram renders when its own slide becomes current and then persists. **Measure at each diagram's own slide; a count taken from the first slide reads 0 and is not a failure.** Recorded as decisions `D-129` and `D-228`. Evidence: the `startOnLoad` value, the three hook registrations, the count on first load (0 of 5), the count after visiting each diagram's own slide (5 of 5), and the count after walking to the last slide and back to the first — still 5 of 5, with exactly one `svg` child per container, no container left showing raw source, and no error graphic.
  - [ ] **The Mermaid source in each container is raw Mermaid syntax**, so it parses when extracted from the file without HTML entity decoding. Evidence: the result of extracting each block's text and parsing it.
  - [ ] **The reveal.js configuration matches the required values**: hash routing enabled, slide transitions, the controls tutorial disabled, and a 1920 by 1080 stage. Evidence: the four configuration values as written in the initialisation call.
  - [ ] **The three library versions match the pinned values** — reveal.js **5.1.0**, Mermaid **11.4.0**, Lucide **0.460.0** — and **the three font families** — **Inter**, **Space Grotesk**, **Fira Code** — are requested at the specified weights. Evidence: the four source URLs and the font link as written.
  - [ ] **Every versioned static asset the deck loads — all five, the three scripts and the two stylesheets — carries a SHA-384 `integrity` attribute and `crossorigin="anonymous"`, exactly as gate [G-8](#g-8--deck-structure) states. The Google Fonts stylesheet carries `crossorigin` without an integrity hash, because its bytes are not stable, and it is the one documented exception**, and the document carries a Content Security Policy restricting sources to the pinned origins. The webfont stylesheet is documented as the one exception, since Google Fonts serves a per-user-agent response that no fixed hash can cover. **Two further remote responses are neither assets this deck declares nor exceptions to this item**, and both are accounted for under gate [G-8](#g-8--deck-structure): the three `fonts.gstatic.com` font binaries the webfont stylesheet requests, and the `source-sans-pro.css` that reveal's own `white.css` reaches through an `@import`, which no `integrity` attribute can reach. **The policy is a standing maintenance obligation, not a decoration.** Under `default-src 'none'` it admits `cdn.jsdelivr.net`, `unpkg.com`, `fonts.googleapis.com` and `fonts.gstatic.com` alongside `'self'` and `data:`, per `D-382`, so **an asset added later from any other origin is blocked outright rather than degraded** until the policy admits it — and whoever adds one must extend the policy in the same change. The block is observable rather than silent: it fires a `securitypolicyviolation` event naming the `blockedURI` and the `effectiveDirective`, and the browser reports it as a console error, which is why the zero-violation and zero-console-message readings corroborate each other. Evidence: the `integrity` value on each script and stylesheet, the policy as written, the statement of the font exception, and the count of `securitypolicyviolation` events across a full traversal, which must be `0`.
  - [ ] **The full brand system is applied and embedded inline** — the complete custom-property block, the slide-type classes and the component classes. Evidence: the presence of the custom-property block in the inline style element.
  - [ ] **The canonical theme file exists at [`../../blitzy-deck/references/blitzy-reveal-theme.css`](../../blitzy-deck/references/blitzy-reveal-theme.css) and its CSS is byte-identical to the deck's inline style block.** Evidence: the result of comparing the file against the inline block.
  - [ ] **Every status claim on every slide is true of the delivery as it stands.** A claim that the application is tested, that coverage is passing, or that it is ready to install is only permitted once the corresponding evidence exists in this checklist. Until then the deck says designed, specified or pending validation. Evidence: one line per status claim, naming the checklist item that substantiates it or the hedged wording used instead.
  - [ ] **The migration clause of the rule is satisfied, and each of its three elements is checked separately.** This delivery is a migration, so the rule requires more of the deck than the structural items above. A deck that renders perfectly and omits any one of these three is **not** compliant.
    - [ ] **Before-and-after architecture views.** Evidence: the slide that carries them, and the confirmation that both the legacy topology and the target scoped application are shown.
    - [ ] **A mapping summary** relating the retired constructs to the artifacts that replace them. Evidence: the slide that carries it, and the confirmation that it agrees with [`../../docs/decisions/TRACEABILITY_MATRIX.md`](../../docs/decisions/TRACEABILITY_MATRIX.md).
    - [ ] **A migration timeline**, rendered as its own diagram rather than implied by prose or by a flow chart of the deploy sequence. It states the **relative** order of the work — install, build, prove — and **fabricates no calendar date**, because authoring executed as a single phase. Evidence: **slide 15 of 16, “The migration timeline, and how it changes after”**, which carries a Mermaid `timeline` diagram; record its rendered section labels and the number of event boxes, and confirm no diagram on any slide asserts a date. The diagram type is fixed at `D-123`.
  - [ ] **The deck shows how the work continues after delivery** — how a maintainer enters the scope, which governance artifacts they read, how they change an Update Set record or a manually built record, and how they re-run validation. Evidence: the slide that carries it.

- [ ] **Rule 3 — Critical Decision Review Document.** The document exists at exactly `docs/review/CRITICAL_DECISIONS.md`, reachable from here as [`../../docs/review/CRITICAL_DECISIONS.md`](../../docs/review/CRITICAL_DECISIONS.md). It holds **exactly five** entries **ordered by risk, highest first**. The delivered index is canonical and every citing document must match it exactly:

  | # | Risk | Reviewer persona | Subject |
  | --- | --- | --- | --- |
  | 1 | **High** | Security | Field-level access control as the premium entitlement boundary |
  | 2 | **High** | DevOps | Rollback branched by starting state, behind a 313-record Update Set |
  | 3 | **High** | API/Integration | Credential handling for outbound ingestion |
  | 4 | Medium | Data/SME | The data-integrity cluster — join-table authority, cascade rules, stored portfolio count |
  | 5 | Medium | UX | Interface deviations from the legacy surface |
 Each carries a decision with its alternatives, a rationale citing the relevant code or convention, a risk level of High, Medium or Low, and a named reviewer persona together with what that reviewer should check. The **irreversible operations**, the **authorization decision** and the **ambiguity resolutions** are all called out. **All five decisions also appear in the Rule 1 log**, and exactly five log rows carry an `R3-` marker, which is how the strict-subset property is checked mechanically rather than read. Evidence: the five entry titles in order with their risk levels and personas, the three call-outs located by entry, confirmation that each of the five resolves to a decision-log row, and — because entry 5 was **replaced in place** rather than reordered — confirmation that the document records what it displaced and that every citing document was updated to match. Two documents cite entry 5 and two cite entry 4; a citing document naming a risk level or a persona that differs from the table above — for instance entry 4 as High, or entry 5 as an API/Integration entry — is a failure of this item.

### H3 — definition of done

The delivery is complete when, and only when, every one of the following holds **simultaneously**. Tick each only when the evidence above supports it.

- [ ] **All nine pre-delivery gates pass.** [Section A](#a--pre-delivery-gates-g-1-to-g-9), 9 of 9.
- [ ] **The Update Set imports, previews with an empty error-type problem set, passes both pre-commit checks, and commits.** [Section B](#b--deployment-gates), and specifically `PRE-COMMIT-01` and `PRE-COMMIT-02` of [section B3](#b3--the-import-completeness-assertion), **each of which must read `313`** — the update-record count the validator reported — before the commit is issued. Both are preconditions of the gate set rather than members of it, and neither is waivable.
- [ ] **All eleven required post-commit gates pass**, `11 of 11`, **`GATE-COL-01` and `GATE-SEC-01` to `GATE-SEC-03` pass** — 15 of 15 acceptance-blocking checks — and the one non-normative diagnostic, `GATE-SEC-04`, was run and recorded whatever its outcome. There is no partial pass, no waiver and no exempt gate among the eleven, and a failure of any one of them initiates the rollback; the four class 2 checks block acceptance without triggering it. [Section B](#b--deployment-gates), with the eleven listed at [section B4](#b4--the-eleven-required-post-commit-gates).
- [ ] **All 10 suites and 36 tests pass, with the coverage gate satisfied.** [Section H1](#h1--the-coverage-gate).
- [ ] **All five success criteria are verified with their stated evidence**, and every ingestion run's provenance is recorded as `live` or `fallback`. Criteria [1](#criterion-1--all-seven-tables-exist-with-100--of-their-fields), [2](#criterion-2--all-three-roles-enforce-field-level-acls-on-100--of-the-seven-premium-fields), [3](#criterion-3--all-six-rest-resources-return-correct-paginated-responses-and-a-429-with-a-retry-value), [4](#criterion-4--scheduled-flows-ingest-and-clean-on-the-configured-cadence-with-zero-unhandled-errors) and [5](#criterion-5--all-five-service-portal-routes-render-and-navigate-as-specified). **Verified means observed on an instance and written into an evidence field.** The presence of an artifact is not evidence that the criterion it serves is met, and no criterion may be inferred from a passing build, a green validator or a committed Update Set.
- [ ] **Every partial implementation is recorded as partial.** Cleaning rule 3 is **PARTIAL** on the six choice lists that declare no `Other` member, and `LinkedIn Ingestion` has **no generally available live acquisition path**, so a credential alone never makes it `live validated`. Both are flagged in [`./gaps-and-flags.md`](./gaps-and-flags.md), and neither is recorded as met. Evidence: the `rule3_deviations` counts from criterion 4, and the two flag entries.
- [ ] **All three rules are verified.** [Section H2](#h2--rule-compliance).
- [ ] **Every requirement with no clean platform equivalent is flagged in [`./gaps-and-flags.md`](./gaps-and-flags.md)** rather than silently omitted or half-implemented. **Nineteen** flags, `F1` through `F19`, contiguous and none zero-padded, across **four** flag dispositions that sum to nineteen:

  | Disposition | Count | Flags |
  | --- | --: | --- |
  | Flagged, not implemented | **5** | `F1`, `F2`, `F5`, `F17`, `F19` |
  | Resolved by documented workaround | **8** | `F3`, `F4`, `F6`, `F7`, `F8`, `F10`, `F14`, `F18` |
  | Partially implemented, flagged | **3** | `F13`, `F15`, `F16` |
  | Consciously excluded | **3** | `F9`, `F11`, `F12` |
  | **Total** | **19** | |

  A fifth disposition, **blocked on an external prerequisite**, is carried by the one open integration limitation `OPEN-1` and by no `F` flag. Evidence: the flag count and the disposition recorded against each in that document's own summary table, and in particular:
  - `F13` — the six choice columns that declare no `Other` member, where an unmatched value is left unwritten and logged rather than coerced, because prompt section 1.0's field list is binding.
  - `F14` — Crunchbase accepts HTTP Basic in no form, so the key lives in the Basic-authentication alias and travels as an `X-cb-user-key` header; live mode is not activated on that source until the authenticated probe returns `200` against a confirmed base URL.
  - `F15` with `OPEN-1` — together they mean **`LinkedIn Ingestion` can only ever be `fallback validated`**, and with the observed credential posture **no result in this delivery may be labelled `live validated`**. Section [4.0](#40--the-route-this-criterion-is-evidenced-on-decided-before-any-run) is where that is signed off. Neither may be recorded as a workaround.
  - `F16` — the three columns no provider response fills: `startup.institutional_funding_last_5yrs`, `investor.aum_usd` and `fundinground.source_url`. **On the live path each stays empty or at its dictionary default**, and no report may describe any of the three as populated from a provider. The fallback dataset carries all three as curated columns, so a fallback-sourced record does have them — which is why a run's provenance must be recorded before any statement is made about these columns.
  - `F19` — that **no** retention, minimisation or data-subject erasure capability is built for the verbatim upstream payload and person data staged in `x_bst_startuptrk_ingest_staging`, so an operator who runs a live ingestion and does not clear that table has left upstream person data on the instance indefinitely. The clear-down is an operator procedure in the live-activation register, not a platform capability, and it must not be reported as one.
- [ ] **The one unresolved item outside that inventory has a disposition record whose two outstanding human fields are filled.** A project rule pins a presentation library to an exact version carrying published security advisories; the rule outranks the baseline, so the pin is retained and the residual risk is disposed of rather than fixed. The record is at [Disposition record](./gaps-and-flags.md#disposition-record) and every field the delivery could establish is written there — item, pinned and fixing versions, authority, assessment date, scope, mitigations, residual risk, the **decision `B` with its date and the accountable role**, and the review trigger. **The two that remain are a human act and a gate tick does not make it:** the **name** of the accepting person, and the **date accepted** in UTC. Disposition `B` is the recorded decision because `A` — amending the rule above the fixing version and re-deriving the deck's pin and all five integrity digests — is the rule owner's act and not the delivery's; a rule owner who chooses `A` amends this record's decision and re-runs `G-8` over all five assets. Evidence: the two field values as written into the disposition record, its `Status` reading `CLOSED — accepted`, the advisory set as re-queried on the acceptance date, and the decision-log row carrying the acceptance. **A record still reading `REQUIRED — not yet supplied` in either field fails this item.**
- [ ] **Both acceptance-blocking operator obligations are discharged and their evidence is recorded.** [`OB-1` and `OB-2`](./gaps-and-flags.md#operator-obligations). Neither can be discharged by a script or a gate tick; each requires an action on the instance by a named role and a recorded observation. A blank evidence field is a **not met**, not a deferral. **`OB-3` is not among them**: it is recommended defence in depth over a route this package does not serve, nothing in the package delivers such a rule, and Agent Action Plan section 0.8.3 makes it optional — so acceptance does not depend on it. It is recorded separately below.
  - `OB-1` — retention, minimisation and data-subject erasure over `x_bst_startuptrk_ingest_staging`, owned by an operator holding `x_bst_startuptrk.admin`. Evidence: the retention period set, the date of the last clear-down, the row count before and after, and who ran it. The reason no artifact delivers this is [`F19`](./gaps-and-flags.md#f19--no-retention-minimisation-or-data-subject-erasure-of-staged-data).
  - `OB-2` — flow-execution-data retention and read-access confirmation, owned by the platform owner. Evidence: all four items of [Flow execution context retention](./gaps-and-flags.md#flow-execution-context-retention), each with the value observed and who observed it.
- [ ] **`OB-3` is recorded as adopted or declined, and either answer is acceptable.** An inbound rate-limit rule in front of the application's own endpoint, owned by the instance operator, **recommended and not required**. Evidence, whichever applies: **adopted** — the rule's identity, the endpoint and roles covered, the threshold and window, and one observed `429` from a deliberate over-budget read, since a rule that has not been seen to fire is not a control; or **declined** — the decision, the person accepting the residual risk, and the date. **An empty answer fails this item; a recorded decline passes it.**
- [ ] **No file outside the planned set has been created or modified.** 29 created files and 1 updated file, per gate [G-7](#g-7--deliverable-completeness). Evidence: the file-presence check and a review of the working tree for anything outside that set.
- [ ] **No ServiceNow artifact outside the `x_bst_startuptrk` scope has been touched.** The instance-provisioning actions the package requires — the ATF runner property, the test-designer roles, the three impersonation users, the REST caller user and its Basic Auth Configuration, and the two credential aliases — are instance state, are performed by the operator rather than by the application, and are correctly **absent** from the Update Set. The REST caller is additionally **removed** when the ATF work is finished, per the previous section. Evidence: gate [G-4](#g-4--scope-containment), plus confirmation that the delivered Update Set carries no record outside the scope.
- [ ] **All five retention obligations are recorded with an actor and a date, and the absence of an automated control is recorded as a flag rather than implied.** No property, business rule or scheduled job in this application bounds the lifetime of staged personal data; the evidence is the control. [Section H3a](#h3a--the-retention-obligations-acceptance-blocking).

### H3a — the retention obligations, acceptance-blocking

**Nothing in this application bounds how long staged personal data lives, and this section is what stops that from being discovered after acceptance.** `x_bst_startuptrk_ingest_staging` is the only table in the delivery holding unvalidated third-party personal data — `raw_payload`, up to 8,000 characters of the upstream response verbatim, alongside `name`, `title`, `bio`, `linkedin_url` and `contact_email` — and a settled row keeps all of it until an administrator deletes it. `D-205` recorded a timed control for it: a clamped `privacy.staging_pending_max_days` property with a quarantine sweep. **It is not delivered.** The Agent Action Plan fixes the property inventory at **eleven** and names all eleven, and `D-036` and `D-265` removed the ninth Script Include, its two properties and its second scheduled job to hold that frozen inventory — so no property, no business rule and no scheduled job in this application performs minimisation, age-bounded pruning or subject erasure. The five obligations of [`./data-model.md`](./data-model.md) fall to the instance operator, and the operator is not this delivery.

**Because there is no automated control, the evidence *is* the control, and it is acceptance-blocking.** Every row below must be filled before sign-off. An unfilled row is a **failed** gate, not a pending action: it means nobody has established that the data has an end. A row may be answered `not applicable`, but only with the reason written in — for example, that no staging row was ever loaded on this instance — and never left blank.

| # | Obligation, from [`./data-model.md`](./data-model.md) | Evidence required | Recorded value | Actor and date |
| --- | --- | --- | --- | --- |
| 1 | Bound how long a **settled** staging row keeps its personal payload | The retention window applied, in days, and the mechanism — a platform table-cleanup rule, a scheduled deletion, or a recorded manual procedure | | |
| 2 | Bound how long a staging row survives **at all** | The age limit applied and the mechanism, or the statement that the table is cleared per import run and the run identifier of the last clearance | | |
| 3 | Service a **data-subject erasure** request across all three surfaces | The named procedure, and confirmation it covers `contact_email` on `x_bst_startuptrk_founder` **and** `x_bst_startuptrk_executive`, the person columns on the staging table, and `raw_payload` | | |
| 4 | Bound the **flow execution context**, which is a separate surface | The flow-execution-data retention setting confirmed with the platform owner, and the access restriction applied to it | | |
| 5 | Keep `sys_user` untouched throughout | Confirmation that no `sys_user` record was created, updated or deleted by any of the above | | |

- [ ] **All five rows above are filled, with an actor and a date on each.** Evidence: this table, complete. A row reading `not applicable` carries its reason.
- [ ] **The absence of an automated control is recorded, not implied.** `D-205`'s timed control is **not delivered**; flag [`F19`](./gaps-and-flags.md#f19--no-retention-minimisation-or-data-subject-erasure-of-staged-data) is the record of that, and the delivery is not signed off as having a retention lifecycle. Evidence: the flag, and the statement above.
- [ ] **The platform owner has acknowledged obligation 4 in writing.** The flow execution tables are outside the `x_bst_startuptrk` scope, so this application cannot bound them and prompt section 6.0 forbids it from trying. Evidence: the acknowledgement, and the retention value the owner set.
- [ ] **No row of the staging table was left holding a `raw_payload` after acceptance without obligation 1 or 2 applied to it.** Evidence: the row count on `x_bst_startuptrk_ingest_staging` with a non-empty `raw_payload` at sign-off, beside the window from row 1 of the table above.

### H4 — final sign-off

| Item | Value |
| --- | --- |
| Pre-delivery gates, section A | of 9 passing |
| Post-commit gates, section B — the eleven required | of 11 passing |
| `GATE-COL-01`, section B — acceptance-required, non-rollback | pass / fail, count observed |
| Non-normative diagnostics, section B — `GATE-SEC-01`, `GATE-SEC-02`, `GATE-SEC-03`, `GATE-SEC-04` | of 4 run and recorded; none of them decides acceptance |
| Criterion 1 — tables and fields | met / not met |
| Criterion 2 — field-level access control | met / not met |
| Criterion 3 — REST resources | met / not met |
| Criterion 4 — scheduled flows | met / not met / **not evidenced** |
| Criterion 4 — executions observed | of 6 recorded |
| Criterion 5 — portal routes | met / not met / **unevaluated**, when guide 04 had not been run |
| Coverage gate — suites | of 10 passing |
| Coverage gate — tests | of 36 passing |
| Rule 1, Rule 2, Rule 3 | verified / not verified |
| `OB-1` — staging retention and erasure — retention period set | |
| `OB-1` — date of last clear-down, rows before / after, operator | |
| `OB-2` — flow-execution retention window recorded, and by whom | |
| `OB-2` — flow-execution read-access set confirmed no wider than the staging read set | yes / no |
| `OB-3` *(recommended, not blocking)* — adopted or declined | adopted / declined |
| `OB-3` — if adopted: rule identity, tables and roles covered, threshold, window and the observed `429`. If declined: who accepted the residual risk, and when | |
| Dependency advisory on the pinned presentation library — decision | **`B` — accepted**, recorded by the delivery on 2026-08-09 (UTC) per `D-407` and re-affirmed on 2026-08-11 (UTC) against the amended thirteen-record advisory set per `D-566`; `A` re-pinned is reachable only if the rule owner amends the rule, which re-derives the deck's pin and all five integrity digests |
| Dependency advisory — risk owner (role) | **The rule owner**, recorded by the delivery per `D-407` — the role that maintains the presentation rule pinning `11.4.0` verbatim; the person holding it signs the next two rows |
| Dependency advisory — accepted by (name) | **REQUIRED — not yet supplied.** Write it into the [disposition record](./gaps-and-flags.md#disposition-record) as well as here; a role name is not a signature |
| Dependency advisory — date accepted (UTC), not back-dated, within thirty days of the re-query | **REQUIRED — not yet supplied.** On or after **2026-08-11**, the date of the latest re-affirmation, and the [re-query procedure](./gaps-and-flags.md#re-query-procedure) is run before it is signed |
| Definition of done | all items ticked — yes / no |
| **Delivery accepted** | **yes / no** |
| Operator signature | |
| Date (UTC) | |

A **no** in any row is a **no** in the last row. There is no partial acceptance, and no item of this checklist may be waived.

**"Not evidenced" is not a pass.** A criterion whose evidence fields are empty is recorded as **not evidenced**, which reads as **not met** in the last row. Recording it that way is what keeps the acceptance record, and the published documentation written from it, from claiming more than was observed.
