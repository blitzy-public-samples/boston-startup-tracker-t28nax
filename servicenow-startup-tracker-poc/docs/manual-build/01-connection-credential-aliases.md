# Manual build 01 — Connection & Credential Aliases — `x_bst_startuptrk`

This guide establishes the **two** Connection & Credential Aliases that the two ingestion flows of the ServiceNow scoped application `x_bst_startuptrk` authenticate through: `x_bst_startuptrk.crunchbase_api` and `x_bst_startuptrk.linkedin_oauth`. For each alias it states the navigation path, every field on the alias record, every field on its connection record, every field on its credential record, the OAuth provider and profile records the second alias additionally requires, the connection test and when it is a gate, and the name-propagation step that carries both alias names into the two flow guides.

**Two record classes, and the line between them is the whole shape of this guide.** The **definition** records — the alias record and its connection record — hold no secret value of any kind, and this guide **builds** them where they are absent and **confirms** them where they already exist. The **credential** records — the Basic Auth credential, and LinkedIn's OAuth 2.0 credential with its provider, profile and refresh token — hold secret material, hold secret material, and this guide **never places a value in one** — on the unprovisioned readiness path it may build the credential **record** with every secret-bearing field left empty, and it never builds LinkedIn's OAuth provider, profile or token records at all. The secrets themselves are provisioned by the party that owns the credential, and this guide tracks that provisioning, and the live connection test that depends on it, as **pending items**.

| Record class | Records | This guide's action | Counted as delivered when |
| --- | --- | --- | --- |
| **Definition** — holds no secret | `sys_alias` x2, `http_connection` x2 | **Build if absent, confirm if present.** Identical on both readiness paths. | The record exists with the specified field values |
| **Credential metadata** — the record, with every secret-bearing field empty | `basic_auth_credentials` x1 — or `api_key_credentials` x1 under the alternate binding of [Step 1.4](#step-14--confirm-the-credential-record-that-holds-the-user-key) — and `oauth_2_0_credentials` x1 | **Confirm if present.** Where it is absent, built **empty** by [B.2](#b2--create-the-crunchbase-alias-metadata) or [B.3](#b3--create-the-linkedin-alias-metadata) on Path B only | The record exists, is bound to its alias, and its secret-bearing field is empty |
| **Credential secret** — the value itself, and LinkedIn's OAuth chain | The `password` or `api_key` value; `oauth_entity` x1, `oauth_entity_profile` x1, `oauth_credential` x1 or more | **Confirm only. Never created, never populated, on either path.** | Its owner has provisioned it and [Step 3](#step-3--test-both-connections) reads `pass` |

**The build-versus-confirm rule, per provider and per record class.** This table is the authority; where any other statement in this package disagrees with it, this one governs.

| Provider | Record | Table / class | Path A — provisioned | Path B — not provisioned |
| --- | --- | --- | --- | --- |
| Crunchbase | Alias | `sys_alias` | Build if absent, confirm if present | Build if absent, confirm if present |
| Crunchbase | Connection | `http_connection` | Build if absent, confirm if present | Build if absent, confirm if present |
| Crunchbase | Credential | `basic_auth_credentials` — or `api_key_credentials` under the alternate binding | **Confirm only** | Build **empty** if absent, per [B.2](#b2--create-the-crunchbase-alias-metadata); never populate |
| LinkedIn | Alias | `sys_alias` | Build if absent, confirm if present | Build if absent, confirm if present |
| LinkedIn | Connection | `http_connection` | Build if absent, confirm if present | Build if absent, confirm if present |
| LinkedIn | Credential | `oauth_2_0_credentials` | **Confirm only** | Build **empty** if absent, per [B.3](#b3--create-the-linkedin-alias-metadata); never populate |
| LinkedIn | OAuth provider, profile and token | `oauth_entity`, `oauth_entity_profile`, `oauth_credential` | **Confirm only** | **Never created on either path.** Each requires a client identifier, a client secret or a refresh token only the credential owner can supply, so an empty or invented one would be a fabricated binding — [B.3](#b3--create-the-linkedin-alias-metadata) states this as a prohibition |

**Neither path skips a provider.** Both aliases and both connections are established on both paths, and LinkedIn's alias chain is established as far as its credential metadata on Path B — only the OAuth provider, profile and token records stop there, and they stop for the reason above rather than because the path skips them.

**No step in this guide types, pastes or records a credential value, and no credential value appears anywhere in this file.**

Which work you actually perform on the credential half depends on the state of the target instance, and **there are two supported readiness paths rather than one**, determined independently per alias, set out under [Readiness paths](#readiness-paths--live-and-sanctioned-fallback). **The path in force is decided by the posture recorded under [The recorded posture for this delivery](#the-recorded-posture-for-this-delivery), which is the only place in this package that observation is stated.** On Path B this guide **builds the four definition records and the two empty credential containers**, and leaves the secret-bearing OAuth chain, every credential value and both connection tests **pending on the credential owner**. Path A applies to an alias whose credential the owner has already provisioned, and it is the path every credential confirmation step below is written for.

**Live connection success is not a prerequisite for building this package.** Guides 02 and 03 are built, published and validated in full in either path. What the path determines is which ingestion path can execute and therefore which evidence label a run carries — `live validated` or `fallback validated`. Live credential provisioning and live validation are later credential-owner actions, tracked as their own pending items, never gates on construction. **A pending item is never reported as a delivered artifact.**

**No step in this guide places a credential value, and no credential value appears anywhere in this file.** That property is absolute and holds on both of the readiness paths below.

This guide has **two readiness paths**, and its first act is to establish which one applies on the instance in front of you. On **Path A** the live Crunchbase and LinkedIn credentials are already provisioned by their owner: every step locates an existing record, confirms its identifiers and bindings, and tests it. On **Path B** they are not provisioned: the alias, connection and credential **metadata** records are created here with every secret-bearing field left empty, ingestion is forced onto the sanctioned fallback dataset, and every result is labelled `fallback validated`. **Neither path is a failure state and neither path stops the build.** Both are specified in full under [Readiness paths — live and sanctioned fallback](#readiness-paths--live-and-sanctioned-fallback).

**The observed condition on the target instance is recorded once, with its date, under [Credential posture](#credential-posture), and is not restated here or in any sibling document.** Re-establish the condition yourself at [Step 1.1](#step-11--locate-the-alias-record) and [Step 2.1](#step-21--locate-the-alias-record) rather than taking this sentence on trust: the instance can change without this file changing.

**Authority.** The frozen prompt and the Agent Action Plan are authoritative for all application content. The Update Set XML at [`../../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml`](../../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml) is the authoritative source for the scope name and for the two non-secret base-URL system-property keys cited below; the identifiers used here match those records character for character, and the same alias names appear in [`../api-reference.md`](../api-reference.md), [`../deployment-runbook.md`](../deployment-runbook.md) and [`../../sample-data/README.md`](../../sample-data/README.md). No variant spelling of any identifier is valid. The platform table, column and choice identifiers below are those of the target instance release.

This document carries **no rationale**. It states what to build, what to confirm and how. Every decision behind these aliases — the authentication type chosen for each source (`D-043`, `D-044`), the outbound path each one fixes (`D-045`), and the split that builds the definition records while deferring every credential to its owner (`D-043`) — is recorded in [`../../../docs/decisions/DECISION_LOG.md`](../../../docs/decisions/DECISION_LOG.md), which is the single source of truth for "why". Requirements with no clean platform equivalent are flagged in [`../gaps-and-flags.md`](../gaps-and-flags.md) and are not restated here.

Operational warnings **are** in scope for this guide and are marked as such. [Operational warning — the binding is by name](#operational-warning--the-binding-is-by-name) is the most important one in this file and must not be skipped.

## Referenced documents

This guide is executable on its own. Both aliases, every record, every field, the escalation path, the connection test and the completion criteria are stated here in full. An operator needs no other file to run it.

**Every document named below is delivered and readable.** Each link resolves to a file in this package, among them `../../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml`, `../validation-gates.md`, `../deployment-runbook.md`, `../api-reference.md` and `../../sample-data/README.md`, so a reader can follow any link and read the content the statement around it describes; no link is a forward reference to something still to be written.

**Reviewer.** This guide is the artifact validated by **entry 3 of [`../../../docs/review/CRITICAL_DECISIONS.md`](../../../docs/review/CRITICAL_DECISIONS.md), risk High, reviewer persona API/Integration**, whose check is to search the delivered Update Set XML for credential material and to confirm both alias names bind before the flows are saved — an obligation placed on this file by the project rule **Critical Decision Review Document**.

## Position in the build order

This is **guide 01 of six**, and it is **step 1** of the execution order below. Nothing in the manual build precedes it. The order is stated in full in [`../manual-build-instructions.md`](../manual-build-instructions.md); it is repeated here so this guide can be run without it. The execution order is not the filename order: guide **06** runs before guide **05**.

| Step | Guide | What it builds, and what it depends on |
| --- | --- | --- |
| **1** | **This guide** | **The two Connection & Credential Aliases the ingestion flows bind to by name. Nothing downstream can authenticate without them.** |
| 2 | [`02-flow-crunchbase-ingestion.md`](02-flow-crunchbase-ingestion.md) | The Crunchbase ingestion flow, which references `x_bst_startuptrk.crunchbase_api` by name. |
| 3 | [`03-flow-linkedin-ingestion.md`](03-flow-linkedin-ingestion.md) | The LinkedIn ingestion flow, which references `x_bst_startuptrk.linkedin_oauth` by name. |
| 4 | [`04-service-portal-pages-and-widgets.md`](04-service-portal-pages-and-widgets.md) | The portal, theme, five pages and eight widgets. |
| 5 | [`06-staging-table-csv-import.md`](06-staging-table-csv-import.md) | The staging-table CSV load. |
| 6 | [`05-atf-test-suites.md`](05-atf-test-suites.md) | The Automated Test Framework suites, **last**, because they exercise everything the five preceding guides build. |

Guides **02** and **03** follow this one immediately and both depend on it. Neither may be started until this guide is complete — which means complete **for the readiness path that applies**, as [Step 3 — Test both connections](#step-3--test-both-connections) sets out. On Path A that is both connection tests reporting `pass`; on Path B it is both alias record sets existing, bound and name-propagated with the source mode forced to `fallback`. **On neither path does an unprovisioned credential halt the build.**

## Preconditions

Do not begin this guide until every item below holds.

| # | Precondition | How to confirm |
| --- | --- | --- |
| 1 | The Update Set has been uploaded and has reached the `loaded` state. | The `sys_remote_update_set` record shows `state` `loaded`. The upload route is specified in [`../deployment-runbook.md`](../deployment-runbook.md). |
| 2 | The preview has completed with an **empty error-type problem set**. | A read of `sys_update_preview_problem` filtered to this remote update set and `type=error` returns an empty `result` array. Warnings are logged and do not block. |
| 3 | The Update Set has **committed**. | The `sys_remote_update_set` record shows `state` `committed`. |
| 4 | **All eleven required post-commit gates have passed.** | Run the eleven required gates in [`../validation-gates.md`](../validation-gates.md) — the seven entity-table reads `GATE-TBL-01` through `GATE-TBL-07`, the three role-record gates `GATE-ROLE-01` through `GATE-ROLE-03`, and the one scope-record gate `GATE-SCOPE-01` — and record `pass` for all eleven in that document's required-gate evidence table. The aggregate pass condition is `11 of 11`; there is no partial pass, and no required gate may be skipped, deferred or waived. |
| 5 | **`GATE-COL-01`** has passed. The four **non-normative security diagnostics** are recorded beside it and are **not** a condition of this guide. | Both are recorded in the evidence record of [`../validation-gates.md`](../validation-gates.md), in the two tables that document keeps separate from the eleven. **`GATE-COL-01` is acceptance-required and non-rollback**: it is the machine check on the 53 binding columns, so a failure blocks acceptance and this guide does not begin until the Update Set has been corrected and re-imported — but it never triggers rollback, because the tables and roles all committed. `GATE-SEC-01` through `GATE-SEC-04` are **class 3, non-normative**: all four are run and recorded on every deployment because each observes something the eleven cannot see, but none of them blocks acceptance, none triggers rollback, and none may be cited as an entry condition by this or any other guide. See [Three classes of check](../validation-gates.md#three-classes-of-check-and-what-each-one-blocks). |
| 6 | The two non-secret base-URL properties are on the instance. | `sys_properties` carries `x_bst_startuptrk.crunchbase.base_url` and `x_bst_startuptrk.linkedin.base_url`. Both committed with the Update Set. The full property inventory is in [`../api-reference.md`](../api-reference.md). |
| 7 | You hold the **`admin`** role on the target Personal Developer Instance. | The application picker and the **System Definition** application are reachable. |
| 8 | You have access to the **Connections & Credentials** module. | The **Connections & Credentials** application appears in the navigator with its four modules: **Connection & Credential Aliases**, **Credentials**, **Connections** and **Authentication Algorithms**. That application requires the `credential_admin` and `connection_admin` roles; the `admin` role of precondition 7 contains both. |
| 9 | You have access to the **System OAuth** module. | The **System OAuth** application appears in the navigator with its **Application Registry** and **Manage Tokens** modules. Both require the `oauth_admin` role, which `admin` contains. This precondition applies to [Step 2](#step-2--alias-2-linkedin) only. |
| 10 | **The readiness path for this instance has been determined and recorded.** | Search `sys_alias` for both names as directed at [Step 1.1](#step-11--locate-the-alias-record) and [Step 2.1](#step-21--locate-the-alias-record), and record the outcome per alias in the readiness table under [Readiness paths](#readiness-paths--live-and-sanctioned-fallback). This is a **decision point, not a gate**: both outcomes are valid, and neither holds this guide up. The observed condition on the target instance is **Path B**. |

Preconditions 1 through 5 are shared by every guide in this folder. Preconditions 6 through 10 are specific to this one. **No precondition requires a live partner credential.**

**Precondition 10 is deliberately not a hard prerequisite, and this is the one thing to understand before reading further.** The target instance has **neither alias and no credential material for either source**, and the LinkedIn live path is additionally gated on a product entitlement that has not been granted — see [Step 2.0](#step-20--the-product-contract-gate-which-decides-whether-step-2-runs-at-all). If a live credential were a prerequisite of this guide, and this guide were a prerequisite of guides 02 and 03, then nothing downstream of it could be built at all: not the flows, not their ATF suites, not the criterion-4 ingestion evidence — including the fallback evidence that the success criteria explicitly accept. That ordering would be a deadlock, and it would be a deadlock created by the documentation rather than by the instance.

So the ordering is stated once, here, and every downstream guide follows it: **this guide establishes the live path where a live path exists, and the flows are built either way.** A source with a green alias is built live-first with fallback on failure. A source without one is built on the forced-fallback route, which needs no alias, no credential and no REST step, and whose results are labelled `fallback validated`. Nothing waits on a credential that does not exist.

### Capture rule for this artifact class

Only tables carrying the update-synch attribute are captured into `sys_update_xml` records, and adding that attribute to a table that lacks it out of the box is unsupported. The alias, connection, credential and OAuth tables are outside the captured set, so these artifacts are established through the platform interface. [`../manual-build-instructions.md`](../manual-build-instructions.md) owns the split rule for the package as a whole, and the decision is recorded at `D-074`.

The delivered Update Set therefore contains **zero** credential material and **zero** alias records. Both alias records and both connection records are consequently **built here, by hand**, and are counted as delivered only once they exist on the instance.

The consequence is the property this guide exists to preserve: the delivered Update Set contains **zero** credential material and **zero** alias records, and the flows still resolve their alias by its generated API ID.

## Credential posture

**This is the one factual statement of credential readiness for the whole package.** Guides 02 and 03, [`../deployment-runbook.md`](../deployment-runbook.md), [`../manual-build-instructions.md`](../manual-build-instructions.md), [`../../README.md`](../../README.md), [`../validation-checklist.md`](../validation-checklist.md) and [`../gaps-and-flags.md`](../gaps-and-flags.md) point here rather than restating it. Where any other document appears to assert readiness, this section governs.

Three gates are separate, and conflating them is the reporting defect this section exists to prevent.

| Gate | What it asserts | What it needs | Blocked by an unprovisioned alias |
| --- | --- | --- | --- |
| **Build gate** | The two aliases have been located and confirmed, or their absence has been recorded and escalated. Both flows, the portal, the API and the test suites are built and their static contracts hold. | This guide run to completion, in either posture. | **No.** |
| **Fallback-validation gate** | Both flows execute end to end on the sanctioned sample dataset, with each result labelled `fallback validated`. | The staging table loaded by [`06-staging-table-csv-import.md`](06-staging-table-csv-import.md) and `x_bst_startuptrk.ingestion.source_mode` set to `fallback`. | **No.** No credential is involved. |
| **Live-validation gate** | Both flows execute end to end against the real providers, with each result labelled `live validated`. | Both aliases provisioned, the provider-correct authenticated probes of [Step 3](#step-3--test-both-connections) each returning `code=ok` with status `200`, and `x_bst_startuptrk.ingestion.source_mode` set to `live` **only after** those two results are recorded. | **Yes.** This gate stays open until the credential owner provisions the material, and stays open on a `404` or `410` root even when the credential is present. |

Prompt section 4.0 states that live credentials are already provisioned and that this work verifies and binds them rather than creating secrets. **That statement is an input to the design, not an observation of any particular instance.** On an instance where either alias is absent, the design is unchanged and the build is unaffected: only the live-validation gate is held open. No document in this package may report the live-validation gate as met on the strength of the build gate or the fallback-validation gate.

The two postures, and what each one means for the rest of the package:

| Posture | Observed at [Step 0](#step-0--establish-the-credential-posture) | Consequence |
| --- | --- | --- |
| **Provisioned** | Both aliases resolve to exactly one `sys_alias` record each. | Run this guide in full. On both probes returning `code=ok` with status `200` against the base URL each property currently holds, the live-validation gate is available, live mode may be activated and ingestion results may be labelled `live validated`. |
| **Unprovisioned** | Either alias resolves to zero records, or a probe does not return `code=ok` with status `200`. | Record the posture, escalate through [If an alias is genuinely absent](#path-b--a-credential-is-not-provisioned), and continue the build. Every ingestion result is labelled `fallback validated` and never `live validated`. Success criterion 4 of [`../validation-checklist.md`](../validation-checklist.md) is met by three clean labelled fallback runs; the live-validation gate remains open and is listed in [`../gaps-and-flags.md`](../gaps-and-flags.md). |

### The recorded posture for this delivery

**This table is the single dated record of the target instance's credential posture, and it is the only place in the package where that observation is stated.** Every sibling document links to this section rather than restating it. The observation is a fact about an instance at a moment, so it carries its date and it must be **re-established** by [Step 0](#step-0--establish-the-credential-posture) before any live claim is made.

| Field | Recorded value |
| --- | --- |
| Instance | `https://dev351809.service-now.com` |
| Date observed (UTC) | **2026-08-08** |
| `x_bst_startuptrk.crunchbase_api` | absent — `sys_alias` returned 0 records |
| `x_bst_startuptrk.linkedin_oauth` | absent — `sys_alias` returned 0 records |
| Crunchbase API key supplied | no |
| LinkedIn client identifier, client secret and refresh token supplied | no |
| Posture | **Unprovisioned — Path B** |
| Consequence | Every ingestion result is labelled `fallback validated`. The build gate and the fallback-validation gate are available; the live-validation gate is not. |

**Re-run [Step 0](#step-0--establish-the-credential-posture) and rewrite the two date-bearing rows above before relying on this record.** A posture older than the instance state in front of you is not evidence.


## Step 0 — Establish the credential posture

Run this before Step 1 and record the outcome. It is two list reads and no edits.

1. Set the application picker to **Boston Startup Tracker**.
2. Open **Connections & Credentials > Connection & Credential Aliases**, the `sys_alias` table.
3. Filter on **Name** `is` `x_bst_startuptrk.crunchbase_api` and record the record count.
4. Filter on **Name** `is` `x_bst_startuptrk.linkedin_oauth` and record the record count.

| # | Alias name | Records found | Posture |
| --- | --- | --- | --- |
| 1 | `x_bst_startuptrk.crunchbase_api` | | |
| 2 | `x_bst_startuptrk.linkedin_oauth` | | |

Record `provisioned` where the count is exactly `1`, and `unprovisioned` where it is `0`. A count above `1` is a duplicate-name condition: record `duplicate` and escalate through [If an alias is genuinely absent](#path-b--a-credential-is-not-provisioned). Carry the recorded posture into guide 02's and guide 03's own posture rows, and into the evidence record of [`../validation-checklist.md`](../validation-checklist.md).

### What is not captured into the Update Set

Only tables carrying the update-synch attribute are captured into `sys_update_xml` records, and adding that attribute to a table that lacks it out of the box is unsupported. The alias, connection, credential and OAuth tables are outside the captured set, so these artifacts are established through the platform interface instead. [`../manual-build-instructions.md`](../manual-build-instructions.md) owns the split rule for the package as a whole.

The consequence is the property this guide exists to preserve: the delivered Update Set contains **zero** credential material and **zero** alias records, and the flows still authenticate.

## Platform constraint

- **Aliases only.** This guide establishes Connection & Credential Aliases, their connections and their credentials. It installs nothing else.
- **IntegrationHub spokes are forbidden.** Prompt section 4.0 binds this absolutely. Do **not** install, activate, reference or open any spoke content set, and do not use a spoke action anywhere in this build. The flows of guides 02 and 03 use generic REST steps bound to the aliases established here.
- **Scope containment.** Prompt section 6.0 forbids modifying anything outside `x_bst_startuptrk`. Every alias, connection and credential record confirmed below must carry the `x_bst_startuptrk` scope, which the platform displays as **Boston Startup Tracker**. Confirm the scope on each record before leaving it.
- **No secret is written.** No step in this guide types, pastes, prints, echoes, logs, screenshots or transcribes a credential value. Where a step inspects a secret-bearing field it records only whether the field is **populated** or **empty**, and never its value. This holds on both readiness paths, and it is the one property of this guide that has no exception.

## What this guide establishes

Exactly two aliases. For each, this guide **builds the alias record and its connection record** where they are absent and confirms them where they are present, then confirms — never creates — the credential records behind them and tests the connection.

On Path A both are located, confirmed and tested. On Path B both are created as metadata only — no secret, no credential test as a gate — as [Path B](#path-b--a-credential-is-not-provisioned) specifies.

### Three identifiers, and which is which

**An alias carries three distinct identifiers, and confusing them is the single most common way to bind the wrong record.** Read this table before Step 1 and keep it in view throughout.

| Identifier | Column on `sys_alias` | Who sets it | Value for alias 1 | Value for alias 2 | What it is used for |
| --- | --- | --- | --- | --- | --- |
| **Name** | `name` | The operator, when the alias is created. **Editable.** | `crunchbase_api` | `linkedin_oauth` | The human label shown in the Connection & Credential Aliases list. It is **not** scope-prefixed. |
| **API ID** | `id` | **The platform**, from the scope plus the Name. Read-only; **never edit it and never type a value into it.** | `x_bst_startuptrk.crunchbase_api` | `x_bst_startuptrk.linkedin_oauth` | The value a flow, an action or a script uses to refer to the alias. Every "reference the alias by name" instruction in this package means **this** value. |
| **sys_id** | `sys_id` | The platform, on insert. | *as provisioned* | *as provisioned* | The argument `ConnectionInfoProvider.getConnectionInfo()` requires. A scoped script that needs a connection resolves the alias record by its **API ID** and then passes this value. |

Two consequences follow, and both are steps rather than cautions:

1. **Do not type a dotted value into the Name field.** A Name of `x_bst_startuptrk.crunchbase_api` produces a generated API ID of `x_bst_startuptrk.x_bst_startuptrk.crunchbase_api`, and every flow that refers to the correct identifier then resolves nothing. Confirm the Name is the **unprefixed** form.
2. **Confirm the generated API ID rather than setting it.** If the API ID does not read the expected value, the Name is wrong: correct the **Name** and let the platform regenerate the identifier.

| # | Alias Name | Generated API ID | Alias type | Credential type | Secret material held by its owner | Base-URL property |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `crunchbase_api` | `x_bst_startuptrk.crunchbase_api` | Connection and Credential | **Basic Auth**, used as an encrypted store rather than as a wire protocol | The Crunchbase **user key**, in the credential's **Password** field, sent as the `X-cb-user-key` request header. Under the alternate binding of [Step 1.4](#step-14--confirm-the-credential-record-that-holds-the-user-key) the key sits in an `API Key` credential's **API Key** field instead; the header is the same either way | `x_bst_startuptrk.crunchbase.base_url` |
| 2 | `linkedin_oauth` | `x_bst_startuptrk.linkedin_oauth` | Connection and Credential | OAuth 2.0 | The LinkedIn OAuth 2.0 client identifier, client secret and refresh token | `x_bst_startuptrk.linkedin.base_url` |

Each alias resolves to a record set of three or six records. The **Built here** column states which of them this guide produces and which it only confirms.

| Alias, by API ID | Records | Built here | Confirmed only |
| --- | --- | --- | --- |
| `x_bst_startuptrk.crunchbase_api` | 1 alias record in `sys_alias`, 1 connection record in `http_connection`, 1 credential record in `basic_auth_credentials` — or in `api_key_credentials` under the recorded alternate binding. | The `sys_alias` record and the `http_connection` record. | The credential record. |
| `x_bst_startuptrk.linkedin_oauth` | 1 alias record in `sys_alias`, 1 connection record in `http_connection`, 1 credential record in `oauth_2_0_credentials`, 1 provider record in `oauth_entity`, 1 profile record in `oauth_entity_profile`, and at least 1 token record in `oauth_credential`. | The `sys_alias` record and the `http_connection` record. | The `oauth_2_0_credentials`, `oauth_entity`, `oauth_entity_profile` and `oauth_credential` records. |

**Four records built, five or more confirmed.** Every record in the *Built here* column is created from field values stated in this guide, none of which is a secret. Every record in the *Confirmed only* column either holds secret material or is bound to a record that does; where one is absent, the credential owner provisions it and this guide records it as a **pending item**.

The platform names the **Application** field differently on each of the three tables below, and all three must read **Boston Startup Tracker** — on a record this guide builds, set it; on a record it confirms, verify it.

| Record class | Table | Application column |
| --- | --- | --- |
| Alias | `sys_alias` | `sys_scope` |
| Connection | `http_connection`, extending `sys_connection` | `app_scope` |
| Credential | `basic_auth_credentials`, `api_key_credentials` and `oauth_2_0_credentials`, all extending `discovery_credentials` | `application` |

## The provider wire contract

**Read this before Step 1. It is the single most consequential correction in this guide.** The alias's *credential type* and the provider's *wire protocol* are two different things, and each provider here needs them decoupled.

| Provider | Base URL property value | How the provider authenticates a request **on the wire** | What the alias record type is, and why |
| --- | --- | --- | --- |
| Crunchbase | `https://api.crunchbase.com/api/v4` | An **`X-cb-user-key` request header** carrying the API key. The provider also accepts the same key as a `user_key` query parameter; **this application forbids that transport** — see the prohibition at the end of [Step 1.4](#step-14--confirm-the-credential-record-that-holds-the-user-key), and `D-229` for the reasoning. **Crunchbase does not accept HTTP Basic authentication at all.** | `Basic Auth`. The credential record is used purely as an **encrypted secret store**: the key sits in its **Password** field and the flow's script step reads it through the alias at run time and places it in the `X-cb-user-key` header itself. The platform's own Basic-Auth header assembly is **not** used for this provider. |
| LinkedIn | `https://api.linkedin.com/rest` | An `Authorization: Bearer <access token>` header, **plus two further mandatory headers**: `X-Restli-Protocol-Version: 2.0.0` and `LinkedIn-Version: <YYYYMM>`. A request missing either of the latter two is rejected regardless of the token. | `OAuth 2.0`. The platform's OAuth 2.0 handling does assemble the `Authorization` header and does renew the access token from the refresh token. The two versioning headers are **not** platform-assembled and are set explicitly by the flow. |

Three consequences follow, and each is acted on later in this guide or in guides 02 and 03.

1. **The platform's generic connection test cannot exercise either provider's real authentication.** It composes neither the `X-cb-user-key` header nor the two LinkedIn versioning headers. A green generic test therefore proves that the alias, connection and credential chain resolves and decrypts — nothing more — and a red one may mean only that the provider rejected a request the test had no way to form correctly. It is retained here as a **diagnostic** and is not a completion criterion. [Step 3](#step-3--test-both-connections) supplies the provider-correct probe that is.
2. **The `LinkedIn-Version` value is a scoped code constant, not a system property.** It is `AppProperties.LINKEDIN_API_VERSION`, currently `202606`, and is read by `AppProperties.getLinkedinApiVersion()`. No `x_bst_startuptrk.*` property holds it, so there is nothing to confirm in `sys_properties` and nothing an operator can edit at run time. LinkedIn retires versions on a rolling schedule; when the delivered value is retired, the constant is changed in the Script Include and the change travels in an Update Set like any other scoped code change. [Step 3.2](#step-32--probe-linkedin-with-all-three-required-headers) is what detects a retired value.
3. **The base URLs carried forward from the legacy source were both stale and are corrected here.** `https://api.crunchbase.com/v3.1` and `https://api.linkedin.com/v2` are the values the retired Python integrators pinned; neither is the current entitled base. The corrected values are the ones in the table above and are the defaults of `AppProperties.getCrunchbaseBaseUrl()` and `AppProperties.getLinkedinBaseUrl()`.

### Product entitlement each alias requires

An alias that resolves and decrypts still fails if the key or token behind it is not entitled to the data the flow asks for. Confirm the entitlement with the credential owner and record the answer; the flows of guides 02 and 03 name the specific operations.

| Alias | Entitlement required | Operations guides 02 and 03 call | If the entitlement is absent |
| --- | --- | --- | --- |
| `x_bst_startuptrk.crunchbase_api` | A Crunchbase **Basic** or **Pro** API licence granting the v4 Search and Entity endpoints. The key is a single long-lived string; there is no scope list. | `POST /api/v4/searches/organizations`, `POST /api/v4/searches/funding_rounds`, `GET /api/v4/entities/organizations/{permalink}` | The provider answers `403` on the search endpoints even though the key authenticates. Record this as an entitlement fault, not a credential fault, and hold the live-validation gate open. |
| `x_bst_startuptrk.linkedin_oauth` | A LinkedIn developer application with an approved product granting an organization read scope — `r_organization_social` or `rw_organization_admin` for a page the application administers, or a partner product for `organizationsLookup` on pages it does not. The scopes granted at consent are fixed in the refresh token and **cannot be widened without re-issuing it**. | `GET /rest/organizationsLookup`, `GET /rest/organizations/{id}` | The provider answers `403` with a scope message. Re-issuing the refresh token under a wider consent is the credential owner's action, not this guide's. |

**Neither provider exposes a public read API for two of this application's six ingested record types.** LinkedIn publishes no endpoint that enumerates a company's people, so `founder` and `executive` have no live acquisition route at all; and its Job Posting API is a *write* API for an employer posting its own vacancies, not a read route over a third party's vacancies, so `job_posting` has none either. This is a provider limitation, not a build defect, and it is not worked around: those three record types are served from the sanctioned fallback dataset in every posture. The flag is recorded in [`../gaps-and-flags.md`](../gaps-and-flags.md) and the routing is specified in [`03-flow-linkedin-ingestion.md`](03-flow-linkedin-ingestion.md).

## Readiness paths — live and sanctioned fallback

**Path A is the provisioned posture and Path B is the unprovisioned posture**, as recorded at [Step 0](#step-0--establish-the-credential-posture). The two names are one concept: [Credential posture](#credential-posture) states what each posture means for the rest of the package, and this section states the per-alias procedure each one selects.

### Two facts, never conflated

**"The alias exists" and "the live credential test passes" are different facts, and this package never treats one as evidence of the other.**

| Fact | What establishes it | What it proves |
| --- | --- | --- |
| **The alias exists** | The `sys_alias`, `http_connection` and credential records are present, named character for character as specified, bound to one another, and carried in the `x_bst_startuptrk` scope. | That a flow naming the alias will **resolve** it at run time. Nothing about whether the call will authenticate. |
| **The provider probe passes** | The provider-correct authenticated probe of [Step 3.1](#step-31--probe-crunchbase-with-the-provider-correct-header) or [Step 3.2](#step-32--probe-linkedin-with-all-three-required-headers) returns `code=ok` at status `200`. The platform's generic **Test connection** link is a diagnostic and is not this fact. | That the connection resolved and decrypted a real credential, reached the endpoint at **Connection URL**, and the endpoint **accepted** the authentication. |

Path A establishes both. Path B establishes the first and **explicitly does not establish the second**. No document in this package may cite alias existence as evidence of live authentication, and **no result obtained on Path B may be labelled `live validated`** — the only permitted label is `fallback validated`.

### The two paths

| | **Path A — live credentials provisioned** | **Path B — no credential provisioned** |
| --- | --- | --- |
| **Instance condition** | Both aliases exist and their credential records hold material provisioned by the credential owner. | One or both aliases are absent, or exist with an empty or invalid credential. **This is the observed condition on the target instance.** |
| **What this guide does** | Locates and confirms the definition records, **building either if it is absent**, then confirms the credential records and tests. | Locates and confirms the definition records, **building either if it is absent** — the same rule — then, where the credential record itself is absent, creates the credential **metadata** record of [B.2](#b2--create-the-crunchbase-alias-metadata) or [B.3](#b3--create-the-linkedin-alias-metadata) with every secret-bearing field left **empty**. Creates no secret and invents no placeholder. |
| **Connection test of [Step 3](#step-3--test-both-connections)** | **Mandatory, and it is the gate.** Both must report success. | **Run once for the record if you wish, expect failure, and record `not applicable — no credential provisioned`.** It is not a gate on this path, because there is nothing for it to authenticate with. |
| **`x_bst_startuptrk.ingestion.source_mode`** | Left at its shipped value `live`. | Set to **`fallback`** before either flow is activated. |
| **Guides 02 and 03** | Start after both tests report success. | **Start after the metadata records exist, are bound and have had their API IDs propagated.** Path B does not block them. |
| **Result labelling** | `live validated` is permitted for a run that completed a live call. | **`fallback validated`, always.** `live validated` is forbidden. |
| **Escalation** | None required. | Runs **in parallel**, not instead: the credential owner is asked to provision the material while the build proceeds. |

**Path B is a sanctioned route through this guide.** Prompt section 4.0 designates the sample dataset the fallback for exactly the condition Path B describes — live authentication failing, timing out, or credentials being re-issued — and an alias whose credential has never been provisioned is that condition. The dataset, its column contract and the property that forces the fallback are specified in [`../../sample-data/README.md`](../../sample-data/README.md); the load procedure is [`06-staging-table-csv-import.md`](06-staging-table-csv-import.md). Recorded at `D-054` and `D-103`.

### Determining and recording the path

Do this before Step 1, and record it.

1. Open **Connections & Credentials > Connection & Credential Aliases**, the `sys_alias` table.
2. Filter on **ID** `is` `x_bst_startuptrk.crunchbase_api` — the generated API ID, not the editable **Name**, per [Three identifiers, and which is which](#three-identifiers-and-which-is-which). Record the row count.
3. Repeat for `x_bst_startuptrk.linkedin_oauth`. Record the row count.
4. Where an alias returns exactly one record, open it and check whether its credential record's secret-bearing fields are populated — the **Password** field for Crunchbase, the **OAuth Entity Profile** binding for LinkedIn. Record `populated` or `empty`, and **no value**.
5. Assign the path per alias from the table below, and take the **lower** of the two for the build as a whole: if either alias is on Path B, the ingestion evidence for both flows is `fallback validated`.

| Alias | `sys_alias` row count | Secret-bearing field | Path |
| --- | --- | --- | --- |
| `x_bst_startuptrk.crunchbase_api` | | | |
| `x_bst_startuptrk.linkedin_oauth` | | | |
| | | **Build path** | |

A row count above one is neither path: it is a duplicate-name condition, and it is handled under [B.7](#b7--a-duplicate-name-condition).

## The establish rule

An alias's **credential** is either provisioned on this instance or it is not, and **each alias is determined independently** — one may be provisioned while the other is not. Determine the state per alias at [Step 1.1](#step-11--locate-the-alias-record) and [Step 2.1](#step-21--locate-the-alias-record), record it in the register below, then follow the path that state selects for that alias.

1. **Locate** the record. On Path A do not create one. On Path B create it exactly as [Path B](#path-b--a-credential-is-not-provisioned) specifies, and create nothing beyond that.
2. **Confirm** its **Name** matches the specified value character for character. A near-match is a failure, not a variant — on either path.
3. **Confirm** its **Type**, its **Application** scope, and every binding to the other records in its set.
4. **Confirm** the state of each secret-bearing field. Secret-bearing fields are stored encrypted and render masked; masked is the expected appearance. On Path A record only that the field is **populated**. On Path B record that it is **empty**. On neither path may you reveal, decrypt, copy, transcribe or record a value.
5. **Test** the connection. On Path A a success is what makes the alias established. On Path B record the outcome as `not applicable — no credential provisioned` and carry on.
6. If a record is missing, or a name does not match, or a credential is empty or invalid, **you are on Path B**. Do not rename an unrelated record to fit, do not point a connection at a different credential to make a test pass, and do not place, invent or approximate a credential value. Follow [Path B](#path-b--a-credential-is-not-provisioned).

**The readiness path decides nothing about the definition records.** The alias record and the connection record are built or confirmed on **both** paths, by [Step 1.1](#step-11--locate-the-alias-record) and [Step 1.3](#step-13--build-or-confirm-the-connection-record-fields), and by [Step 2.1](#step-21--locate-the-alias-record) and [Step 2.3](#step-23--build-or-confirm-the-connection-record-fields). What the path decides is what happens to the **credential** half.

| | **Path B — credential not provisioned** | **Path A — credential provisioned** |
| --- | --- | --- |
| **How you reach it** | The credential record the alias needs does not exist, or exists but fails a confirmation step, or its connection test fails against definition records that are otherwise correctly bound. | Every credential record in the alias's set exists and confirms, and the alias record found or built at the locate step carries the specified **Name** and generated **API ID** character for character. |
| **Definition records — both paths** | **Built if absent, confirmed if present.** The alias record per [Step 1.1](#step-11--locate-the-alias-record) or [Step 2.1](#step-21--locate-the-alias-record); the connection record per [Step 1.3](#step-13--build-or-confirm-the-connection-record-fields) or [Step 2.3](#step-23--build-or-confirm-the-connection-record-fields). Leave the connection's **Credential** field empty until the credential exists. | Built or confirmed identically, with the **Credential** field populated by the confirmed credential record. |
| **Credential records** | Record the state in the register below, then work that alias's **pending-item** procedure at [Path B](#path-b--a-credential-is-not-provisioned). Create only the credential **metadata** record specified at [B.2](#b2--create-the-crunchbase-alias-metadata) or [B.3](#b3--create-the-linkedin-alias-metadata), leaving every secret-bearing field empty, and do **not** place a credential value. | Work that alias's credential confirmation sequence — Steps 1.4 to 1.5, or Steps 2.4 to 2.7 — and then its connection test in [Step 3](#step-3--test-both-connections). |
| **Alias API ID used downstream** | The **ID** field read off the alias record built or confirmed at the locate step — copied, never retyped — per [Step 4](#step-4--propagate-both-alias-names-into-guides-02-and-03). It equals the canonical value stated in this guide, because the platform derives it from the application scope and the alias Name. | Identical. |
| **Guides 02 and 03** | **Built, published and validated in full.** Their actions reference the alias by its API ID, and their ingestion runs take the sanctioned fallback path against the staging table. | Built, published and validated identically, and additionally able to execute the live path once [Step 3](#step-3--test-both-connections) reads `pass`. |
| **Ingestion source mode** | `fallback`, forced through the `x_bst_startuptrk.ingestion.source_mode` property. The dataset and its column contract are in [`../../sample-data/README.md`](../../sample-data/README.md); the load procedure is [`06-staging-table-csv-import.md`](06-staging-table-csv-import.md). | `live` becomes available. `fallback` remains available for deterministic testing. |
| **Evidence label for every ingestion run** | `fallback validated`. Never `live validated`. | `live validated` once a live call has succeeded; `fallback validated` otherwise. |
| **This guide's completion criteria** | Criteria 1 to 4 and criterion 11 apply unchanged, because they cover the definition records. Criteria 5 to 10 are recorded `not applicable — no credential provisioned` for that alias and are joined by criterion 12. | Criteria 1 to 11 all apply to that alias. |

**On the target Personal Developer Instance recorded for this delivery, both aliases are in Path B.** Neither partner credential is available, and neither `sys_alias` record existed when this guide was written — so on that instance this guide **builds all four definition records** and records both credential sets, both **Credential** bindings and both connection tests as pending items. That is the instance state recorded in [`../deployment-runbook.md`](../deployment-runbook.md) and in [`../../README.md`](../../README.md). Confirm it yourself rather than assuming it: a credential may have been provisioned since this guide was written, which moves that alias to Path A.

Record the determination for both aliases before starting Step 1.4 or Step 2.4.

| # | Alias, by API ID | Alias records returned at the locate step | Alias record built here | Connection record built here | Credential records present | Path selected | Timestamp (UTC) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `x_bst_startuptrk.crunchbase_api` | | | | | | |
| 2 | `x_bst_startuptrk.linkedin_oauth` | | | | | | |

Record the record count as an integer, `yes` or `no` in the two *built here* columns and in the *credential records present* column, `A` or `B` in the path column, and the timestamp in `YYYY-MM-DD HH:MM:SS` form. **Record no credential value in any field of this table.**

## The build-or-confirm rule

This rule governs every step below. Read it before Step 1. Items 1 and 2 are the **definition** half and run on both paths; items 3 to 6 are the **credential** half, and an alias in Path B takes item 7 instead.

1. **Locate** the definition record. If it does not exist, **build** it from the field table in the step that names it, then continue as though it had been found. Every field value in those tables is stated in this guide and none is a secret.
2. **Confirm** the definition record's **Name** and its generated **API ID** each match the specified value character for character, per [Three identifiers, and which is which](#three-identifiers-and-which-is-which). A near-match is a failure, not a variant. Confirm its **Type**, its **Application** scope, and every binding to another definition record.
3. **Locate** the credential record. **Do not create one**, and do not rename an unrelated record to fit.
4. **Confirm** its **Type**, its **Application** scope, and every binding to the other records in its set.
5. **Confirm** that each secret-bearing field is **populated**. Secret-bearing fields are stored encrypted and render masked; that is the expected appearance. Record that the field is populated. Do **not** attempt to reveal, decrypt, copy or transcribe the value, and do not record it.
6. **Test** the connection, and only then treat the alias as ready for a live call.
7. If a credential record is missing, or one of its bindings does not resolve, **stop the credential half for that alias**. Create only the metadata record specified at [B.2](#b2--create-the-crunchbase-alias-metadata) or [B.3](#b3--create-the-linkedin-alias-metadata), leaving every secret-bearing field empty, and do not place a credential value. Record it at [Path B](#path-b--a-credential-is-not-provisioned) and continue the build.

A field documented below as *empty* is deliberately blank and must be left blank on both paths. A field documented as *as provisioned* holds a value set by the credential owner: on Path A confirm it is populated, confirm nothing further about it, and change nothing; on Path B it is empty, and leaving it empty is correct.

## Step 1 — Alias 1, Crunchbase

The alias **Name** is `crunchbase_api`, its generated **API ID** is `x_bst_startuptrk.crunchbase_api`, and its credential type is **Basic Auth, used as an encrypted store rather than as a wire protocol** — the alternate `API Key` binding of [Step 1.4](#step-14--confirm-the-credential-record-that-holds-the-user-key) is used only where the release supports it. Three records make up the set: the alias and its connection, both **built here if absent**, and its credential, **confirmed only**.

**The Crunchbase Data API v4 authenticates with a user key, and it does not accept HTTP Basic.** Two facts follow, and this build depends on both:

| Fact | What this build does |
| --- | --- |
| The key travels as an **`X-cb-user-key` request header**. The provider also accepts a `user_key` query parameter. | The flow's script step sets the header itself. Query-parameter transport is **forbidden** — the prohibition is at the end of [Step 1.4](#step-14--confirm-the-credential-record-that-holds-the-user-key). |
| The platform's automatic `Authorization: Basic` header authenticates against **nothing** here: the provider ignores it and answers `401`. | The credential's class is **Basic Auth**, and it is used **only** as the encrypted store for the key. The platform's Basic-Auth header assembly is not used for this provider. |

**The credential type is therefore `Basic Auth`, and the store is not the protocol.** [Step 1.4](#step-14--confirm-the-credential-record-that-holds-the-user-key) builds that record as the **primary** binding and documents one **alternate** store for a release that exposes an API Key credential class able to send a named header. `D-043` and `D-229` carry the decision, its alternatives and its risks.

### Step 1.1 — Locate the alias record

1. Set the application picker to **Boston Startup Tracker**, so that every record you open or create is in the `x_bst_startuptrk` scope.
2. In the navigator, open **Connections & Credentials > Connection & Credential Aliases**. The list is the `sys_alias` table.
3. Filter the list on **ID** `is` `x_bst_startuptrk.crunchbase_api`. Filter on the generated identifier rather than on **Name**, because it is the value every flow and action refers to. If the **ID** column is not on the list, add it from the list-control menu.
4. Count the records the list returns and write the count into the readiness register of [Readiness paths](#readiness-paths--live-and-sanctioned-fallback). Then act on the count:
   - **Exactly one** record — open it and continue at [Step 1.2](#step-12--build-or-confirm-the-alias-record-fields) to confirm its fields. Record `no` in the *alias record built here* column.
   - **Zero** records — **build the record now**, at [Step 1.2](#step-12--build-or-confirm-the-alias-record-fields), then continue through the guide exactly as though it had been found. Record `yes` in the *alias record built here* column. Building this record places no credential value: every field it carries is stated in Step 1.2's table.
   - **More than one** record — a duplicate-identifier condition. Do **not** build another and do not delete either. Record the count, and escalate to the instance administrator at [B.7](#b7--a-duplicate-name-condition), because a flow cannot be bound safely until exactly one record answers to the identifier.
5. Open the record you found or created.

To build the record: click **New** on the Connection & Credential Aliases list, complete the fields of [Step 1.2](#step-12--build-or-confirm-the-alias-record-fields), and **Submit**. The platform generates **ID** from the application scope plus **Name** on insert, so `x_bst_startuptrk.crunchbase_api` is the value it produces without being typed. Reopen the record and confirm the generated **ID** before leaving it.

### Step 1.2 — Build or confirm the alias record fields

One record in `sys_alias`, **built here if [Step 1.1](#step-11--locate-the-alias-record) returned none**. Enter every field in the table below on a new record, or confirm every field on an existing one. The **Required value** column is what the field must read; a value of *empty* means the field must be blank. **No field in this table is a credential.**

| Field | Column | Required value | Note |
| --- | --- | --- | --- |
| Name | `name` | `crunchbase_api` | Mandatory, editable, and **not** scope-prefixed. **Character for character.** |
| Type | `type` | `Connection and Credential` | Mandatory. Stored value `connection`. A value of `Credential`, stored `credential`, carries no connection record and cannot supply the connection URL. |
| Connection type | `connection_type` | `HTTP` | Stored value `http_connection`. This is what makes the connection record an HTTP(s) Connection. |
| Application | `sys_scope` | `Boston Startup Tracker` | The `x_bst_startuptrk` scope. |
| Support Multiple Active Connection | `multiple_connections` | `false` | One active connection serves this alias. |
| Parent Alias | `parent` | *empty* | This alias is not a child of another alias. |
| Default Retry Policy | `retry_policy` | *empty* | Retry behaviour is not set on the alias. |
| Configuration Template | `configuration_template` | *empty* | No template is applied. |
| ID | `id` | `x_bst_startuptrk.crunchbase_api` | **Platform-generated from the scope plus the Name. Read-only — confirm it, never type it.** This is the value the Crunchbase actions of guide 02 resolve at run time. If it reads anything else, correct the **Name** above and let the platform regenerate it. |
| Is internal | `is_internal` | `false` | This is not a platform-internal alias. |

Two related lists at the bottom of the alias form carry the rest of the record set:

| Related list | Shows | Confirm |
| --- | --- | --- |
| **Connections** | Records in `sys_connection` whose **Connection alias** names this alias. | **Exactly one** record. Open it for [Step 1.3](#step-13--build-or-confirm-the-connection-record-fields). **Zero** records means the connection has not been built yet: build it at Step 1.3. |
| **Credentials** | Records in `discovery_credentials` whose **Credential alias** list names this alias. | **Exactly one** record in Path A, and the same record the connection's **Credential** field names in [Step 1.3](#step-13--build-or-confirm-the-connection-record-fields). **Zero** records selects Path B for this alias: the credential is not provisioned, so record it at [Path B](#path-b--a-credential-is-not-provisioned) and create only the metadata record specified at [B.2](#b2--create-the-crunchbase-alias-metadata) or [B.3](#b3--create-the-linkedin-alias-metadata), with every secret-bearing field left empty. If this list is empty while the connection's **Credential** field is populated, the credential-side half of the binding is missing; record that the same way. |

### Step 1.3 — Build or confirm the connection record fields

One record in `http_connection`, the HTTP(s) Connection class of `sys_connection`. It can also be reached from **Connections & Credentials > Connections**, filtered on **Connection alias** `is` `x_bst_startuptrk.crunchbase_api`.

**Build it if it does not exist.** From the alias record's **Connections** related list click **New**, choose **HTTP(s) Connection** if the platform asks for a class, complete the fields of the table below and **Submit**. Building this record places no credential value: its only secret-adjacent field is **Credential**, which is a *reference* to a credential record and is left **empty** until that record exists. Where the connection already exists, confirm the same fields instead.

Before entering or confirming the **Connection URL**, read the authoritative value from the system property:

1. Open **System Definition > System Properties**, or the `sys_properties` list.
2. Filter on **Name** `is` `x_bst_startuptrk.crunchbase.base_url`.
3. Confirm exactly one record, and read its **Value**. That property committed with the Update Set and holds `https://api.crunchbase.com/api/v4`, the base of the current Crunchbase Data API v4. It is non-secret endpoint configuration; it is not a credential.
4. The connection record's **Connection URL** must equal that value exactly. If the two differ, correct the **connection record** to match the property. The property is the source of the value.

| Field | Column | Required value | Note |
| --- | --- | --- | --- |
| Name | `name` | `Crunchbase API` *set on build* | Mandatory. A human-readable label; on an existing record leave it as provisioned. It is **not** the binding: the flow binds through **Connection alias**, never through this field. |
| Connection alias | `connection_alias` | `x_bst_startuptrk.crunchbase_api` | Mandatory. Must reference the alias record built or confirmed in [Step 1.2](#step-12--build-or-confirm-the-alias-record-fields). This is the binding that makes the alias resolvable. |
| Credential | `credential` | The Basic Auth credential of [Step 1.4](#step-14--confirm-the-credential-record-that-holds-the-user-key) — or the `API Key` credential under that step's alternate binding — or *empty* in Path B | In Path A it must be populated and must reference that record; an empty **Credential** field is the single most common cause of a run-time authentication failure. In Path B it is left empty. |
| Connection URL | `connection_url` | The value of `x_bst_startuptrk.crunchbase.base_url` | `https://api.crunchbase.com/api/v4`. Confirm against the property as set out above. The v4 resource paths — `searches/organizations`, `entities/organizations/{permalink}` — are appended by the flow's REST step, not by this field. |
| Base path | `base_path` | *empty* | Per-request paths are supplied by the flow's REST step, not by the connection. |
| Application | `app_scope` | `Boston Startup Tracker` | Mandatory. The `x_bst_startuptrk` scope. |
| Active | `active` | `true` | An inactive connection is not selected at run time and the flow fails to authenticate. |
| Order | `order` | `100` | The platform default. It orders candidate connections when an alias has more than one; this alias has one. |
| Use MID server | `use_mid` | `false` | The call is made from the instance. No MID server is involved. |
| MID Selection | `mid_selection` | `auto_select` | Not applied while **Use MID server** is `false`. |
| MID Server | `mid_server` | *empty* | Not applied while **Use MID server** is `false`. |
| MID Cluster | `mid_cluster` | *empty* | Not applied while **Use MID server** is `false`. |
| MID Application | `application` | *as provisioned* | The MID application default. Not applied while **Use MID server** is `false`. Leave as found. |
| Capabilities | `capabilities` | *empty* | A MID capability list. Not applied while **Use MID server** is `false`. |
| Host | `host` | *empty* | Derived from **Connection URL**. Leave blank. |
| Protocol | `protocol` | *empty* | Derived from **Connection URL**. Leave blank. |
| Override default port | `port` | *empty* | The default port for the URL scheme is used. |
| Connection timeout | `connection_timeout` | *empty* | Deliberately empty. **The timeout that governs a call is set per request, not here**: guides 02 and 03 each set an explicit 30-second whole-request budget on every outbound call, so the moment a run gives up is a property of the build rather than of the connection record or the instance default. |
| Connection retries | `connection_retries` | `0` | Deliberately zero. **The flows make each outbound call exactly once**: there is no in-call retry, no backoff and no `Retry-After` honouring anywhere in guide 02 or guide 03. A `429`, a `5xx` or a transport failure is classified into a closed code and ends the read, and recovery is the next hourly trigger, which re-runs the source because an unhealthy run never stamps its completion marker. A connection-level retry would reintroduce hidden attempts under a policy the flows do not have and would make the total attempt count per window unknowable. |
| Mutual authentication | `mutual_auth` | `false` | No client certificate is presented. Authentication is the **user key** carried by the credential record and sent as the `X-cb-user-key` header, not a transport-level identity. |
| Protocol profile | `protocol_profile` | *empty* | Not applied while **Mutual authentication** is `false`. |
| MID protocol profile | `mid_protocol_profile` | *empty* | Not applied while **Use MID server** is `false`. |
| URL builder | `url_builder` | `false` | The URL is taken from **Connection URL** as entered. |
| Extended Attributes | `extended_attributes` | *empty* | No connection attributes are required. |
| Is internal | `is_internal` | `false` | This is not a platform-internal connection. |
| Connection type | `sys_class_name` | `HTTP(s) Connection` | Read-only. It must read `HTTP(s) Connection`, matching the alias's **Connection type** of `HTTP`. |

### Step 1.4 — Confirm the credential record that holds the user key

**The provider contract decides this step, and it is worth stating before any field name.** Crunchbase v4 validates a request by a **user key**, presented as an `X-cb-user-key` header or a `user_key` query parameter. It has no notion of a user name and password pair, so an `Authorization: Basic` header — which is what the platform composes automatically from a Basic Auth credential — is not authentication as far as the provider is concerned. Two bindings satisfy the contract, and **the Basic Auth credential is the primary store for this delivery**: it is the store the Agent Action Plan names, the store [Step 1.3](#step-13--build-or-confirm-the-connection-record-fields)'s **Credential** field points at, and the store every verification row in this guide is written against. Build or confirm the primary binding. The alternate API Key binding exists only for a release whose API Key credential class can be made to send a named request header, and it is a different **store** for the same key, never a different wire protocol. Record which binding is in force.


#### Primary binding — a Basic Auth credential holding the key

One record in `basic_auth_credentials`, the Basic Auth class of `discovery_credentials`. Reach it by clicking through the connection record's **Credential** field, or from **Connections & Credentials > Credentials** filtered on **Type** `is` `Basic Auth`.

**The Basic Auth credential record is an encrypted secret store for this provider, not a wire protocol.** The API key is held in the **Password** field, and the **User name** field does not hold the key. Crunchbase does not accept HTTP Basic authentication; the Crunchbase flow reads the key out of this record through the alias at run time and places it in an `X-cb-user-key` request header. See [The provider wire contract](#the-provider-wire-contract) for the consequences, and [`02-flow-crunchbase-ingestion.md`](02-flow-crunchbase-ingestion.md) for the step that composes the header.

| Field | Column | Required value | Note |
| --- | --- | --- | --- |
| Name | `name` | *as provisioned* | A human-readable label. Not a binding. |
| Type | `type` | `Basic Auth` | Stored value `basic_auth`. Set by the record's class; confirm, do not edit. |
| User name | `user_name` | *as provisioned* | The account identifier recorded by the credential owner. **It is not the API key.** Confirm the field is populated and record only that it is populated. |
| Password | `password` | *as provisioned* | **This field holds the Crunchbase API key**, and it is the only place the key exists on this instance. It is stored encrypted and renders masked; masked is the expected appearance. Confirm it is populated. Do not reveal, copy, transcribe or re-enter it. The flow reads it through the alias and never through this form. |
| Credential alias | `tag` | Includes `x_bst_startuptrk.crunchbase_api` | A list field referencing `sys_alias`. The alias must appear in it. This is the credential-side half of the binding; the connection's **Credential** field is the other half. Both must be present. |
| Applies to | `applies_to` | `All MID servers` | Stored value `all`. No MID server is used, so no MID restriction applies. |
| Active | `active` | `true` | An inactive credential is not selected and authentication fails. |
| Order | `order` | `100` | The platform default. It orders candidate credentials; this connection names one explicitly. |
| Application | `application` | `Boston Startup Tracker` | Mandatory. The `x_bst_startuptrk` scope. |
| MID servers | `mid_list` | *empty* | Not applied while **Applies to** is `All MID servers`. |
| Authentication Key | `authentication_key` | *empty* | Not used by the Basic Auth class. |
| Use Context | `use_context` | `false` | No credential context is applied. |
| Context Name | `context_name` | *empty* | Not applied while **Use Context** is `false`. |

#### Alternate binding — an API Key credential where the release provides one

**This is not the primary binding.** Use it **only** where the release provides an `api_key_credentials` class **and** that class can be made to send a named request header, and record that it is in force in the completion table of [Step 4](#step-4--propagate-both-alias-names-into-guides-02-and-03). It is an alternate **store**, not an alternate wire protocol: the transport is the `X-cb-user-key` header either way.

One record in `api_key_credentials`, the API Key class of `discovery_credentials`. Reach it by clicking through the connection record's **Credential** field, or from **Connections & Credentials > Credentials** filtered on **Type** `is` `API Key`.

| Field | Column | Required value | Note |
| --- | --- | --- | --- |
| Name | `name` | *as provisioned* | A human-readable label. Not a binding. |
| Type | `type` | `API Key` | Set by the record's class; confirm, do not edit. |
| API Key | `api_key` | *as provisioned* | **This field holds the Crunchbase user key.** It is stored encrypted and renders masked; masked is the expected appearance. Confirm it is populated. Do not reveal, copy, transcribe or re-enter it. |
| Credential alias | `tag` | Includes `x_bst_startuptrk.crunchbase_api` | A list field referencing `sys_alias`. The alias must appear in it. This is the credential-side half of the binding; the connection's **Credential** field is the other half. Both must be present. |
| Applies to | `applies_to` | `All MID servers` | Stored value `all`. No MID server is used, so no MID restriction applies. |
| Active | `active` | `true` | An inactive credential is not selected and authentication fails. |
| Order | `order` | `100` | The platform default. It orders candidate credentials; this connection names one explicitly. |
| Application | `application` | `Boston Startup Tracker` | Mandatory. The `x_bst_startuptrk` scope. |
| MID servers | `mid_list` | *empty* | Not applied while **Applies to** is `All MID servers`. |
| Use Context | `use_context` | `false` | No credential context is applied. |
| Context Name | `context_name` | *empty* | Not applied while **Use Context** is `false`. |

**Confirm on your release where the API Key credential places the key.** Releases differ: some send it as a named header configured on the credential or the connection, some as a named query parameter. Read the record's own field labels and the connection's **Extended Attributes**, and confirm that the composed request carries `X-cb-user-key`. If the release places the key in the query string and offers no header option, this binding is unusable: return to the [primary Basic Auth binding](#primary-binding--a-basic-auth-credential-holding-the-key), which controls the placement explicitly because the flow composes the header itself. Record the outcome in the completion table of [Step 4](#step-4--propagate-both-alias-names-into-guides-02-and-03).

**Under either binding the flow must not rely on the platform's automatic header.** The flow's script step resolves the connection and its credential by alias identifier, reads the key, and sets `X-cb-user-key` itself; it sends no `Authorization` header at all. That path is specified in [`02-flow-crunchbase-ingestion.md`](02-flow-crunchbase-ingestion.md), and it is the same alias-by-name resolution the primary binding uses, so no secret reaches a flow input, a script literal or the Update Set either way.
**Neither binding is a licence to place a key in a URL.** Do not configure the `user_key` query parameter on the connection, in a flow input, or in a REST step's query string. A URL is logged; a header is not.

### Step 1.5 — Test the credential

1. On the credential record, click the **Test credential** related link.
2. Supply the target the dialog asks for, using the **Connection URL** value confirmed in [Step 1.3](#step-13--build-or-confirm-the-connection-record-fields).
3. Record the result and read it as follows.

| Result | What it proves | What it does **not** prove |
| --- | --- | --- |
| Success | The credential record resolves and its **Password** decrypts. | Nothing about Crunchbase. The test sends an HTTP Basic `Authorization` header, which Crunchbase does not accept. |
| Failure | Either the credential does not resolve or decrypt, **or** the provider rejected a Basic-authenticated request — which it always will. | Which of the two it was. |

**This test is a diagnostic and is not a completion criterion**, because a failure is the expected provider response and a success says nothing about the provider. Its only actionable outcome is a platform-side error such as an inactive credential or a broken alias binding; act on that, and ignore a provider-side `401` or `403`. The completion criterion for this alias is the provider-correct probe in [Step 3](#step-3--test-both-connections). The reasoning is in [The provider wire contract](#the-provider-wire-contract).

## Step 2 — Alias 2, LinkedIn

The alias **Name** is `linkedin_oauth`, its generated **API ID** is `x_bst_startuptrk.linkedin_oauth`, and its credential type is **OAuth 2.0**. Six records make up the set: the alias and its connection, both **built here if absent**, and its OAuth 2.0 credential, the OAuth provider, the OAuth entity profile and the token record set, all four **confirmed only**.

**LinkedIn authenticates through OAuth 2.0, not a static bearer token.** The secret material is a client identifier, a client secret and a refresh token, held across the provider and token records rather than in a credential password field. Precondition 9 applies to this step.

### Step 2.0 — The product-contract gate, which decides whether Step 2 runs at all

**Do not build this alias until the table below is filled in.** OAuth 2.0 describes *how* a caller authenticates; it does not grant a caller anything. What this application's LinkedIn design needs is a **product entitlement**: permission to read a company's employees, to read the profiles of members who are not the authenticated member, and to read a company's job postings. LinkedIn's published material does not grant those reads to a generic OAuth 2.0 client. Member profile access centres on the **authenticated member** and restricts the storage of another member's data; job posting access is **partner-controlled**; organisation lookup is a **versioned, access-controlled** API. An alias built without a named product behind it authenticates successfully and is then refused by every endpoint the flow calls — and, worse, if some endpoint does answer, the application would be storing another member's personal data with no authority to do so.

The gate is therefore contractual rather than technical, and it is recorded here so that the person building the alias is the person who confirms it:

| # | What must be recorded before Step 2.1 | Value | Confirmed by | Date |
| --: | --- | --- | --- | --- |
| 1 | The **named LinkedIn product or partner programme** granting this application its reads | | | |
| 2 | The **exact scopes** granted, one per read the flow performs | | | |
| 3 | The **grant type** and token lifetime the product authorises | | | |
| 4 | The **API version header** value the product requires | | | |
| 5 | The **data storage and retention terms** authorising this application to store another member's name, title, biography, profile locator and contact address | | | |
| 6 | The **rate limits and quotas** the product applies | | | |

**Until every row carries a value, LinkedIn is formally a fallback-only source.** That is not a workaround: it is the honest state of the integration, and it is flagged as such in [`../gaps-and-flags.md`](../gaps-and-flags.md). In that state:

- **Skip Steps 2.1 to 2.7 and the LinkedIn half of Step 3 entirely.** Do not create an alias, a connection, a credential, a provider or a profile record. Do not invent a client identifier or a placeholder that resembles one.
- **Build the LinkedIn flow on the forced-fallback route** of [`03-flow-linkedin-ingestion.md`](03-flow-linkedin-ingestion.md), which requires no credential and no alias.
- **Label every LinkedIn result `fallback validated`.** `live validated` is not available for LinkedIn and must not be recorded, whatever a run appears to show.
- Record `n/a — contract-gated, fallback only` against `x_bst_startuptrk.linkedin_oauth` in the outcome tables of [Step 3](#step-3--test-both-connections) and [Step 4](#step-4--propagate-both-alias-names-into-guides-02-and-03), rather than `fail`. A gate that has not been satisfied is not a defect in the build.

Once the table is complete, run Steps 2.1 to 2.7 as written, and re-read [`03-flow-linkedin-ingestion.md`](03-flow-linkedin-ingestion.md) first: the endpoints, the scopes and the version header the product grants govern that flow's REST steps, and the paths in the guide are marked as requiring confirmation against the product for exactly this reason.

### Step 2.1 — Locate the alias record

1. Confirm the application picker still reads **Boston Startup Tracker**.
2. In the navigator, open **Connections & Credentials > Connection & Credential Aliases**.
3. Filter the list on **ID** `is` `x_bst_startuptrk.linkedin_oauth`, for the reason given in [Step 1.1](#step-11--locate-the-alias-record).
4. Count the records the list returns and write the count into the readiness register of [Readiness paths](#readiness-paths--live-and-sanctioned-fallback). Then act on the count, exactly as [Step 1.1](#step-11--locate-the-alias-record) item 4 directs: **exactly one** record means confirm it at [Step 2.2](#step-22--build-or-confirm-the-alias-record-fields) and record `no` in the *alias record built here* column; **zero** records means **build it now** at Step 2.2 and record `yes`; **more than one** is a duplicate-identifier condition to escalate rather than build around.
5. Open the record you found or created.

To build the record: click **New** on the Connection & Credential Aliases list, complete the fields of [Step 2.2](#step-22--build-or-confirm-the-alias-record-fields), and **Submit**. The platform generates **ID** from the scope plus **Name**, so `x_bst_startuptrk.linkedin_oauth` is produced without being typed. Reopen the record and confirm the generated **ID** before leaving it.

### Step 2.2 — Build or confirm the alias record fields

One record in `sys_alias`, **built here if [Step 2.1](#step-21--locate-the-alias-record) returned none**. The field set is the same as [Step 1.2](#step-12--build-or-confirm-the-alias-record-fields); only the **Name** and the generated **ID** differ. **No field in this table is a credential.**

| Field | Column | Required value | Note |
| --- | --- | --- | --- |
| Name | `name` | `linkedin_oauth` | Mandatory, editable, and **not** scope-prefixed. **Character for character.** |
| Type | `type` | `Connection and Credential` | Mandatory. Stored value `connection`. |
| Connection type | `connection_type` | `HTTP` | Stored value `http_connection`. |
| Application | `sys_scope` | `Boston Startup Tracker` | The `x_bst_startuptrk` scope. |
| Support Multiple Active Connection | `multiple_connections` | `false` | One active connection serves this alias. |
| Parent Alias | `parent` | *empty* | This alias is not a child of another alias. |
| Default Retry Policy | `retry_policy` | *empty* | Retry behaviour is not set on the alias. |
| Configuration Template | `configuration_template` | *empty* | No template is applied. |
| ID | `id` | `x_bst_startuptrk.linkedin_oauth` | **Platform-generated from the scope plus the Name. Read-only — confirm it, never type it.** This is the value the LinkedIn actions of guide 03 resolve at run time. If it reads anything else, correct the **Name** above and let the platform regenerate it. |
| Is internal | `is_internal` | `false` | This is not a platform-internal alias. |

Confirm the same two related lists at the bottom of the alias form as in [Step 1.2](#step-12--build-or-confirm-the-alias-record-fields):

| Related list | Shows | Confirm |
| --- | --- | --- |
| **Connections** | Records in `sys_connection` whose **Connection alias** names this alias. | **Exactly one** record. Open it for [Step 2.3](#step-23--build-or-confirm-the-connection-record-fields). **Zero** records means the connection has not been built yet: build it at Step 2.3. |
| **Credentials** | Records in `discovery_credentials` whose **Credential alias** list names this alias. | **Exactly one** record in Path A, and the same record the connection's **Credential** field names in [Step 2.3](#step-23--build-or-confirm-the-connection-record-fields). **Zero** records selects Path B for this alias: record it at [Path B](#path-b--a-credential-is-not-provisioned) and create only the metadata record specified at [B.2](#b2--create-the-crunchbase-alias-metadata) or [B.3](#b3--create-the-linkedin-alias-metadata), with every secret-bearing field left empty. |

### Step 2.3 — Build or confirm the connection record fields

One record in `http_connection`, **built here if absent** by the same route as [Step 1.3](#step-13--build-or-confirm-the-connection-record-fields): **New** from the alias record's **Connections** related list, class **HTTP(s) Connection**, the fields below, **Submit**. Building it places no credential value. Read the authoritative URL from the property first:

1. Open the `sys_properties` list and filter on **Name** `is` `x_bst_startuptrk.linkedin.base_url`.
2. Confirm exactly one record and read its **Value**. It holds `https://api.linkedin.com/rest` — the versioned base, not the retired `https://api.linkedin.com/v2` — and is non-secret endpoint configuration.
3. The connection record's **Connection URL** must equal that value exactly. If they differ, correct the connection record to match the property.

| Field | Column | Required value | Note |
| --- | --- | --- | --- |
| Name | `name` | `LinkedIn API` *set on build* | A human-readable label, not a binding; on an existing record leave it as provisioned. |
| Connection alias | `connection_alias` | `x_bst_startuptrk.linkedin_oauth` | Mandatory. Must reference the alias built or confirmed in [Step 2.2](#step-22--build-or-confirm-the-alias-record-fields). |
| Credential | `credential` | The OAuth 2.0 credential of [Step 2.4](#step-24--confirm-the-oauth-20-credential-record-fields), or *empty* in Path B | In Path A it must be populated and must reference that record. **In Path B leave it empty** and record the binding as a pending item at [Path B](#path-b--a-credential-is-not-provisioned). |
| Connection URL | `connection_url` | The value of `x_bst_startuptrk.linkedin.base_url` | `https://api.linkedin.com/rest`. Confirm against the property as set out above. |
| Base path | `base_path` | *empty* | Per-request paths are supplied by the flow's REST step. |
| Application | `app_scope` | `Boston Startup Tracker` | Mandatory. The `x_bst_startuptrk` scope. |
| Active | `active` | `true` | An inactive connection is not selected at run time. |
| Order | `order` | `100` | The platform default. |
| Use MID server | `use_mid` | `false` | The call is made from the instance. |
| MID Selection | `mid_selection` | `auto_select` | Not applied while **Use MID server** is `false`. |
| MID Server | `mid_server` | *empty* | Not applied while **Use MID server** is `false`. |
| MID Cluster | `mid_cluster` | *empty* | Not applied while **Use MID server** is `false`. |
| MID Application | `application` | *as provisioned* | The MID application default. Not applied while **Use MID server** is `false`. Leave as found. |
| Capabilities | `capabilities` | *empty* | A MID capability list. Not applied while **Use MID server** is `false`. |
| Host | `host` | *empty* | Derived from **Connection URL**. |
| Protocol | `protocol` | *empty* | Derived from **Connection URL**. |
| Override default port | `port` | *empty* | The default port for the URL scheme is used. |
| Connection timeout | `connection_timeout` | *empty* | Deliberately empty. The 30-second whole-request budget is set per request in guide 03, for the reason given against the same field in [Step 1.3](#step-13--build-or-confirm-the-connection-record-fields). |
| Connection retries | `connection_retries` | `0` | Deliberately zero, for the reason given against the same field in [Step 1.3](#step-13--build-or-confirm-the-connection-record-fields): guide 03 makes each call exactly once and recovers on the next hourly trigger rather than by retrying. |
| Mutual authentication | `mutual_auth` | `false` | Authentication is OAuth 2.0 through the credential record. |
| Protocol profile | `protocol_profile` | *empty* | Not applied while **Mutual authentication** is `false`. |
| MID protocol profile | `mid_protocol_profile` | *empty* | Not applied while **Use MID server** is `false`. |
| URL builder | `url_builder` | `false` | The URL is taken from **Connection URL** as entered. |
| Extended Attributes | `extended_attributes` | *empty* | No connection attributes are required. |
| Is internal | `is_internal` | `false` | This is not a platform-internal connection. |
| Connection type | `sys_class_name` | `HTTP(s) Connection` | Read-only. Must match the alias's **Connection type** of `HTTP`. |

### Step 2.4 — Confirm the OAuth 2.0 credential record fields

One record in `oauth_2_0_credentials`, the OAuth 2.0 class of `discovery_credentials`. **Confirmed on Path A; on Path B created as metadata only, with every secret-bearing field left empty.** Reach it through the connection record's **Credential** field, or from **Connections & Credentials > Credentials** filtered on **Type** `is` `OAuth 2.0`. If the record does not exist, this alias is in Path B: stop here and record it at [Path B](#path-b--a-credential-is-not-provisioned).

The OAuth 2.0 credential class holds **no password**. It carries a pointer to an OAuth entity profile, and the secret material lives on the provider and token records confirmed in the three steps that follow.

| Field | Column | Required value | Note |
| --- | --- | --- | --- |
| Name | `name` | *as provisioned* | A human-readable label, not a binding. |
| Type | `type` | `OAuth 2.0` | Stored value `oauth_2_0`. Set by the record's class; confirm, do not edit. |
| OAuth Entity Profile | `oauth_entity_profile` | The profile of [Step 2.6](#step-26--confirm-the-oauth-entity-profile) | Must be populated. This is the pointer from the credential to the OAuth configuration; an empty value leaves the connection with no token source. |
| Integration Type | `integration_type` | `System` | Stored value `system`. A value of `Personal`, stored `personal`, ties the token to an individual user and a scheduled flow then has no token to use. |
| Credential alias | `tag` | Includes `x_bst_startuptrk.linkedin_oauth` | A list field referencing `sys_alias`. The alias must appear in it. |
| Applies to | `applies_to` | `All MID servers` | Stored value `all`. |
| Active | `active` | `true` | An inactive credential is not selected. |
| Order | `order` | `100` | The platform default. |
| Application | `application` | `Boston Startup Tracker` | Mandatory. The `x_bst_startuptrk` scope. |
| User name | `user_name` | *empty* | Not used by the OAuth 2.0 class. |
| Password | `password` | *empty* | Not used by the OAuth 2.0 class. **The client secret does not go here**; it is held on the provider record of [Step 2.5](#step-25--confirm-the-oauth-provider-record). |
| MID servers | `mid_list` | *empty* | Not applied while **Applies to** is `All MID servers`. |
| Authentication Key | `authentication_key` | *empty* | Not used by the OAuth 2.0 class. |
| Use Context | `use_context` | `false` | No credential context is applied. |
| Context Name | `context_name` | *empty* | Not applied while **Use Context** is `false`. |

### Step 2.5 — Confirm the OAuth provider record

One record in `oauth_entity`. Open **System OAuth > Application Registry** and locate the record referenced by the profile of [Step 2.6](#step-26--confirm-the-oauth-entity-profile) — the profile's **OAuth provider** field names it. **This record holds the client identifier and the client secret.**

| Field | Column | Required value | Note |
| --- | --- | --- | --- |
| Name | `name` | *as provisioned* | Mandatory. The provider label the credential owner registered. |
| Type | `type` | `OAuth Provider` | Stored value `oauth_provider`. This is the outbound third-party provider type. `OAuth Client`, stored `client`, is for inbound access to this instance and is the wrong record class here. |
| Client ID | `client_id` | *as provisioned* | Mandatory. **This field holds the LinkedIn OAuth 2.0 client identifier.** Confirm it is populated. Record only that it is populated. |
| Client Secret | `client_secret` | *as provisioned* | **This field holds the LinkedIn OAuth 2.0 client secret.** Stored encrypted and rendered masked; masked is the expected appearance. Confirm it is populated. Do not reveal, copy or transcribe it. |
| Default Grant type | `default_grant_type` | *as provisioned* | Mandatory. Must be the grant type the credential owner registered with LinkedIn, and must be a grant type that issues a refresh token. It must equal the profile's **Grant type** in [Step 2.6](#step-26--confirm-the-oauth-entity-profile). |
| Token URL | `token_url` | *as provisioned* | The LinkedIn token endpoint. Must be populated, or no token can be obtained or refreshed. |
| Refresh Token URL | `refresh_token_url` | *as provisioned* | The endpoint used to exchange the refresh token for a new access token. Must be populated for unattended refresh to work. |
| Authorization URL | `auth_url` | *as provisioned* | Used when the refresh token was first obtained. |
| Redirect URL | `redirect_url` | *as provisioned* | Must match the redirect URL registered with LinkedIn. |
| Send Credentials | `send_client_credentials_as` | *as provisioned* | Must match what the provider expects: `As Basic Authorization Header`, stored `basic_authorization_header`, or `In Request Body (Form URL-Encoded)`, stored `request_body_parameter`. A mismatch fails token refresh with a provider-side authentication error. |
| Access Token Lifespan | `access_token_lifespan` | *as provisioned* | Mandatory, in seconds. |
| Refresh Token Lifespan | `refresh_token_lifespan` | *as provisioned* | Mandatory, in seconds. Note the value: the refresh token stops working when this elapses, and the credential owner must re-issue it. |
| OAuth API Script | `oauth_api_script` | *as provisioned* | A Script Include reference, populated only if the provider needs non-standard request handling. Leave as found. |
| Active | `active` | `true` | An inactive provider yields no token. |
| Comments | `comments` | *as provisioned* | Free text. **Confirm it contains no credential value.** If it does, report it through [Path B](#path-b--a-credential-is-not-provisioned) as a credential-hygiene defect. |

### Step 2.6 — Confirm the OAuth entity profile

One record in `oauth_entity_profile`. There is no navigator module for this table: open it from the **OAuth Entity Profiles** related list at the bottom of the provider record of [Step 2.5](#step-25--confirm-the-oauth-provider-record), or through the **OAuth Entity Profile** field of the credential record of [Step 2.4](#step-24--confirm-the-oauth-20-credential-record-fields).

| Field | Column | Required value | Note |
| --- | --- | --- | --- |
| Name | `name` | *as provisioned* | Mandatory. |
| OAuth provider | `oauth_entity` | The provider of [Step 2.5](#step-25--confirm-the-oauth-provider-record) | Mandatory. Confirm it references that exact record and no other. |
| Grant type | `grant_type` | *as provisioned* | Mandatory. **Must equal the provider's Default Grant type.** A divergence between the two is a run-time token failure. |
| Is default | `default` | `true` | Confirm this profile is the default for its provider, so the credential resolves it without ambiguity. |
| OAuth Resources | `oauth_resources` | *as provisioned* | The scopes requested from LinkedIn. Leave as found. |
| JWT Provider | `jwt_provider` | *empty* | Not used by this grant type. |
| Assertion Producer | `saml2_assertion_producer` | *empty* | Not used by this grant type. |

Confirm the credential record of [Step 2.4](#step-24--confirm-the-oauth-20-credential-record-fields) points at **this** profile. The chain must close: credential to profile, profile to provider.

### Step 2.7 — Confirm the refresh token is on file and refresh works

The refresh token is the third piece of secret material and it lives in the token store, not on a form field you fill in.

1. Open **System OAuth > Manage Tokens**. The list is the `oauth_credential` table.
2. Filter on **Peer** `is` the provider record confirmed in [Step 2.5](#step-25--confirm-the-oauth-provider-record).
3. Confirm at least one record whose **Type** is `Refresh Token`, stored value `refresh_token`. Its presence is the confirmation that the refresh token has been issued and stored. **Do not open the token fields to read a value**; confirm the row exists and note its **Expires** value.
4. Note whether an **Access Token** record, stored value `access_token`, is also present, and note its **Expires** value.
5. Confirm the refresh behaviour after the connection test of [Step 3](#step-3--test-both-connections): re-read this list and confirm that the **Access Token** record's **Expires** has moved forward, or that an **Access Token** record now exists where none did. Either outcome confirms the platform exchanged the refresh token for a new access token without operator involvement.
6. If no **Refresh Token** record exists, the token has not been issued or has been revoked. Stop the credential half and follow [Path B](#path-b--a-credential-is-not-provisioned). **Do not attempt to obtain a token yourself**, and do not place a token value.

| Field | Column | What to confirm |
| --- | --- | --- |
| Type | `type` | `Refresh Token`, stored `refresh_token`, for the token that sustains unattended access. `Access Token`, stored `access_token`, for the short-lived token derived from it. |
| Peer | `peer` | References the provider record of [Step 2.5](#step-25--confirm-the-oauth-provider-record). |
| Expires | `expires` | Present. Record the value. For the access token, it must move forward across a successful connection test. |
| Grant Type | `grant_type` | Matches the provider's **Default Grant type** and the profile's **Grant type**. |
| Last time the token was accessed | `last_access` | Updates after a successful connection test. |
| Token | `token` | **Do not read this field.** Confirm the row exists; nothing more. |
| Token issued | `token_issued` | **Do not read this field.** Stored encrypted. |
| Token received | `token_received` | **Do not read this field.** Stored encrypted. |
| User | `user` | Empty or the service account the credential owner registered. A populated personal user together with an **Integration Type** of `System` is a mismatch: report it through the escalation route. |

## Step 3 — Test both connections

**This step, not the platform's generic connection test, is the completion criterion for the live-validation gate, and it is also the activation gate for live ingestion on each source.** The reason is in [The provider wire contract](#the-provider-wire-contract): the generic test composes neither the `X-cb-user-key` header nor LinkedIn's two mandatory versioning headers, so it cannot exercise either provider's real authentication in either direction. Run the two diagnostics first if you have not, then read [Step 3.0a](#step-30a--the-closed-fault-codes-and-the-redaction-rule-both-probes-share), which defines the closed fault codes, the redaction rule and the exception boundary both probe scripts share, and then run the probes.

**An alias in Path B has a connection record but no credential behind it, so neither the generic test nor the probe can authenticate.** Run neither as a gate for that alias: record `not applicable — no credential provisioned` in the register of [Step 3.3](#step-33--record-the-probe-outcomes) and continue. Run the generic test once if you want the platform's own failure text for the escalation record of [B.1](#b1--record-the-condition).

### Step 3.0 — Run the generic connection test as a diagnostic

For each of the two connection records confirmed in [Step 1.3](#step-13--build-or-confirm-the-connection-record-fields) and [Step 2.3](#step-23--build-or-confirm-the-connection-record-fields):

1. Open the connection record from **Connections & Credentials > Connections**, filtered on **Connection alias**.
2. Confirm the record is saved with no unsaved changes pending. An unsaved edit is not covered by the test.
3. Click the **Test connection** related link at the foot of the form. It is a related link, not a form button.
4. Record the result and classify it.

| Result | Classification | Action |
| --- | --- | --- |
| Success | Platform chain resolves. | Note it and continue to the probe. It says nothing about the provider. |
| A platform-side error — alias not found, credential not found, credential inactive, decryption failure, MID selection failure | **Actionable.** One link in the chain did not resolve. | Do not proceed to the probe. Work back through the chain: connection **Connection alias**, connection **Credential**, credential **Active** and **Credential alias**, and for LinkedIn the profile, provider and refresh-token records. Then follow [If an alias is genuinely absent](#path-b--a-credential-is-not-provisioned). |
| A provider-side `401`, `403` or `400` | **Expected, not actionable.** For Crunchbase this is the provider refusing Basic authentication, which it always does. For LinkedIn it is the missing versioning headers. | Note it and continue to the probe. **Do not treat it as a defect and do not attempt to make it pass.** |

### Step 3.0a — The closed fault codes and the redaction rule both probes share

**Both probe scripts below report a closed code, never provider text, and never an uncaught exception.** A provider error message can echo the request that produced it, and a request composed from a credential can therefore echo the credential; a message can also be arbitrarily long, and a transport failure can arrive as a thrown exception rather than as a status. Each script maps every outcome onto exactly one of the codes below and carries at most a bounded, redacted detail alongside it.

| `code` printed | Meaning | Detail carried |
| --- | --- | --- |
| `ok` | The call completed with a `2xx` status. | None. |
| `alias_unresolved` | The alias **API ID** — the value in `sys_alias.id`, not the editable `name` — matched no `sys_alias` record. | None. |
| `alias_ambiguous` | The alias **API ID** matched more than one `sys_alias` record. | The number of matches. |
| `connection_unresolved` | The alias resolved but yielded no active connection. | None. |
| `credential_unreadable` | The connection resolved but the credential attribute the provider needs came back empty. | The **name** of the attribute. Never its value. |
| `transport` | The call did not complete — a timeout, a DNS failure or a TLS failure. | One closed reason, classified from the transport error by `faultReason()`: `reason=timeout`, `reason=dns`, `reason=tls`, `reason=connect` or `reason=other`. The error text itself is not recorded. |
| `http_status` | The call completed with a non-`2xx` status. | The status code only. |
| `internal` | The probe itself threw before it could classify anything. | The exception class name only, redacted and capped. The exception message is not recorded. |

`DETAIL_LIMIT` is **120** characters, and the cap is the **last** thing the sanitiser does rather than the only thing it does — a secret shorter than the cap would otherwise pass through whole. `AppProperties.safeText()` runs its ordered pattern set before capping: control characters are flattened, whole credential-bearing headers are removed value and all, scheme-qualified values are removed, **labelled values are removed whatever delimiter separates them — including a plain space**, locators and addresses are removed, and any opaque run of 20 or more characters that survived is removed, apart from the two diagnostic shapes it keeps. The passes, what each removes and the two shapes deliberately kept are in [The redaction rule, in order](#the-redaction-rule-in-order-and-what-each-pass-removes), and [The redaction test vectors](#the-redaction-test-vectors) is the script that proves it on this instance before the first probe runs.

**There is exactly one sanitiser in this application, and every diagnostic in this package passes through it.** It is `AppProperties.safeText(value, limit)`, a method of the Script Include that ships in the Update Set, and every probe script and every flow script calls it rather than carrying a copy of it. It replaces control, zero-width and bidirectional-override characters; redacts web tokens, credential-shaped assignments — `key`, `token`, `secret`, `password`, `authorization` and their siblings, **whatever delimiter separates a label from its value, a plain space included** — bare authentication scheme words together with the value that follows them, addresses, locators, opaque runs of 20 or more characters other than the two diagnostic shapes it deliberately keeps, and quoted runs of 24 or more; turns a double quote into a single quote so a value cannot break a quoted field; collapses whitespace; and caps the result at the limit it is given, appending `...(truncated)` so a truncation is visible rather than silent. The delivered pattern set and its order are in the `SANITISERS` member of that Script Include, which is the one place they exist.

Both probes below therefore call `SAFE.safeText(detail, DETAIL_LIMIT)`, where `SAFE` is one `x_bst_startuptrk.AppProperties` instance, and the flow steps of [`02-flow-crunchbase-ingestion.md`](02-flow-crunchbase-ingestion.md) and [`03-flow-linkedin-ingestion.md`](03-flow-linkedin-ingestion.md) make the identical call. A detail recorded by a probe and a detail recorded by a flow are therefore sanitised by the same code, not by matching copies of it — and a correction made to the sanitiser reaches every caller at once instead of having to be applied in five places.

Four rules bind both scripts.

1. **Every statement that can throw is inside the `try` block, and the `catch` block reports rather than rethrows.** A probe that ends in an uncaught exception leaves the operator with a stack trace instead of a fault class, and a stack trace is not a classified result.
2. **Exactly one line reaches the log per run**, written by `report()`, carrying the status, the body length, the code and the redacted detail. Nothing else is printed.
3. **No credential value, no header value, no endpoint and no response body is printed**, in any branch, including the exception branch.
4. **The alias is resolved on `sys_alias.id`, the API ID column, and the row count is asserted to be exactly one.** The `ALIAS` constant in each script holds the dotted, scope-prefixed form — `x_bst_startuptrk.crunchbase_api` and `x_bst_startuptrk.linkedin_oauth` — which is the value the `id` column carries, per [Three identifiers, and which is which](#three-identifiers-and-which-is-which). Matching that value against `name` returns zero rows on a correctly built alias, because `name` holds the **unprefixed** label; a probe written that way reports `alias_unresolved` on every run and is indistinguishable from a genuinely absent alias.


#### The redaction rule, in order, and what each pass removes

**The passes below are the delivered `SANITISERS` member of `AppProperties`, in the order it declares them.** There is no second copy of them anywhere in the package: every probe script in this guide, the Crunchbase live step of [`02-flow-crunchbase-ingestion.md`](02-flow-crunchbase-ingestion.md) and both LinkedIn live steps of [`03-flow-linkedin-ingestion.md`](03-flow-linkedin-ingestion.md) reach them by calling `SAFE.safeText(value, DETAIL_LIMIT)`, so a correction made in the Script Include reaches all five call sites at once and no copy can set the exposure. Read this table to understand what the sanitiser removes; change the behaviour only in `SANITISERS`. **The ordering is load-bearing, not stylistic:** pass 1 must run first so nothing later that reasons about a line can be evaded by a value carrying its own newline, and pass 6 must run last so it only sees what the labelled passes did not already remove.

| Pass | What it removes | Why it is not sufficient alone |
| --- | --- | --- |
| 1 | Control characters, flattened to a space. | A value split across a line boundary would otherwise escape pass 2's line-bounded match. |
| 2 | Credential-bearing headers — `Authorization`, `Proxy-Authorization`, `Cookie`, `Set-Cookie` — with their **value removed and the name kept**, so the line still says which header it was. Each of those names ends in a label pass 4 recognises, which is how one rule covers them all. | The header name alone is harmless; it is the value after the colon that is the credential. |
| 3 | Scheme-qualified credentials: `Bearer`, `Basic` or `ApiKey` followed by whatever comes next. | Catches a scheme that arrives without its header name, which pass 2 cannot see. |
| 4 | Labelled values, with **any** delimiter — colon, equals, or a plain space — for the labels `key`, `token`, `secret`, `password`, `passwd`, `pwd`, `credential`, `authorization`, `auth`, `bearer`, `signature`, `cookie` and `session`, each matched as the tail of a longer name so `x-cb-user-key`, `refresh_token`, `client_secret` and `Proxy-Authorization` are all covered. After a colon or an equals the value goes whatever it looks like; after a plain space it goes when it is quoted, scheme-qualified, carries a digit, mixes case or reaches twelve characters. | **This is the pass the original rule lacked.** It required a colon or an equals, so `user_key abc123def456` and `password hunter2` survived with their values intact — the two vectors below that no length-based floor reaches either. |
| 5 | Locators, any scheme, and address-shaped tokens. | A query string can carry a key, and an address is personal data in its own right. |
| 6 | Any remaining **opaque run**: 20 or more characters drawn from `A-Z a-z 0-9 + / = _ . -` that mixes character classes. | The catch-all for a value that arrived with no label and no scheme at all. |
| — | Runs collapsed, ends trimmed, then the result capped at `DETAIL_LIMIT`. | The cap alone leaks: a secret shorter than the cap is not truncated at all. |

**Pass 6 deliberately keeps two shapes, because both are diagnostics rather than secrets:** a same-case run carrying no digit, such as a closed code, and a **dotted** run carrying no digit, such as `com.glide.rest.SocketTimeoutException` or `x_bst_startuptrk.crunchbase_api`. Without that carve-out the `internal` code's own detail — the exception class name — would be redacted, and the operator would lose the only diagnostic that code carries.

**Pass 4 accepts a plain space, and it is shape-gated when it does.** After a colon or an equals sign the value is removed whatever it looks like, because the delimiter already says it is a value. After a plain space the value is removed when it is quoted, scheme-qualified, carries a digit, mixes case, or runs to twelve characters or more — and is kept when it is a short single-case word. `password hunter2`, `user_key abc123def456`, `client_secret WpL9x` and `api_key deadbeefcafe` all go; `the natural key could not be resolved` survives as written. Accepting only a colon or an equals leaves `password hunter2` intact, which is exactly the case pass 6's 20-character floor cannot reach either; accepting any following word without the shape gate mangles this package's own diagnostics, which an operator reads. **The residual gap is narrow and stated rather than hidden:** a secret that is a single-case run of fewer than twelve characters carrying no digit, following a credential label separated by a space, is indistinguishable from prose and survives.

#### The redaction test vectors

**Run this before the first probe, and again after any edit to `AppProperties.SANITISERS`.** It is a background script in the `x_bst_startuptrk` scope from **System Definition > Scripts - Background**, with the application picker on **Boston Startup Tracker**. It calls the delivered sanitiser directly — nothing is pasted into it and there is no second copy to keep in step — and it requires the last line to read `leaks=0 survivals_ok=4`. **A failing vector means the sanitiser is wrong, not that the vector is wrong.**

**Every value in `VECTORS` below is synthetic.** They are strings shaped like credentials so that the sanitiser has something credential-shaped to redact; not one of them is, was, or resembles a credential issued to this application, and the required outcome of each is that the value is **absent** from the output. A secret scanner run over this package will match them, and that match is the fixture working as designed — do not replace a synthetic vector with a real value to "test it properly", which would place a live credential in a repository file and in `syslog` at once. Add new vectors by inventing new synthetic values in the same shape.

```javascript
(function testRedact() {
    var DETAIL_LIMIT = 120;

    // The one application sanitiser, called exactly as every probe and every flow step
    // calls it. See Step 3.0a.
    var SAFE = new x_bst_startuptrk.AppProperties();
    function redact(text) {
        return SAFE.safeText(text, DETAIL_LIMIT);
    }

    var VECTORS = [
        ['Authorization: Bearer AQVJlLm9DUlRfSk5xYlRnMkJ3', 'AQVJlLm9DUlRfSk5xYlRnMkJ3'],
        ['authorization: Basic YWRtaW46aHVudGVyMg==',       'YWRtaW46aHVudGVyMg=='],
        ['Bearer AQVJlLm9DUlRfSk5xYlRnMkJ3',                'AQVJlLm9DUlRfSk5xYlRnMkJ3'],
        ['user_key abc123def456ghi789',                     'abc123def456ghi789'],
        ['user_key = abc123def456ghi789',                   'abc123def456ghi789'],
        ['X-cb-user-key: 7f3a9c1e2b5d',                     '7f3a9c1e2b5d'],
        ['password hunter2',                                'hunter2'],
        ['client_secret\nWpL9x',                            'WpL9x'],
        ['refresh_token=AQXsl0K9',                          'AQXsl0K9'],
        ['api-key: k-9912-aa',                              'k-9912-aa'],
        ['https://api.crunchbase.com/v4/entities?user_key=zz', 'user_key=zz'],
        ['ops@example.com',                                 'ops@example.com'],
        ['nJ8kQ2vX7pL1mW4tR6yB',                            'nJ8kQ2vX7pL1mW4tR6yB']
    ];

    // Each of these must come back byte-identical: they are diagnostics, not secrets.
    var SURVIVALS = [
        'alias_unresolved',
        'x_bst_startuptrk.crunchbase_api',
        'matches=2',
        'com.glide.rest.SocketTimeoutException'
    ];

    var leaks = 0;
    var i = 0;
    for (i = 0; i !== VECTORS.length; i++) {
        var out = redact(VECTORS[i][0]);
        if (out.indexOf(VECTORS[i][1]) !== -1) {
            leaks++;
            gs.info('[bst.redact.test] LEAK vector ' + (i + 1) + ': "' + VECTORS[i][1] +
                '" survived as "' + out + '"');
        }
    }

    var survivalsOk = 0;
    for (i = 0; i !== SURVIVALS.length; i++) {
        var kept = redact(SURVIVALS[i]);
        if (kept === SURVIVALS[i]) {
            survivalsOk++;
        } else {
            gs.info('[bst.redact.test] OVER-REDACTED: "' + SURVIVALS[i] +
                '" became "' + kept + '"');
        }
    }

    gs.info('[bst.redact.test] vectors=' + VECTORS.length +
        ' leaks=' + leaks + ' survivals_ok=' + survivalsOk + '/' + SURVIVALS.length);
})();
```

| # | Input | Required outcome |
| --- | --- | --- |
| 1 | `Authorization: Bearer AQVJlLm9DUlRfSk5xYlRnMkJ3` | The token is absent. Recorded as `Authorization: (redacted)`. |
| 2 | `authorization: Basic YWRtaW46aHVudGVyMg==` | The encoded pair is absent. |
| 3 | `Bearer AQVJlLm9DUlRfSk5xYlRnMkJ3` | The token is absent even with no header name. |
| 4 | `user_key abc123def456ghi789` | The value is absent — **space-separated, no delimiter**. |
| 5 | `user_key = abc123def456ghi789` | The value is absent. |
| 6 | `X-cb-user-key: 7f3a9c1e2b5d` | The value is absent. |
| 7 | `password hunter2` | The value is absent, though it is far shorter than pass 6's floor. |
| 8 | `client_secret` then a newline then `WpL9x` | The value is absent — pass 1 removed the newline it hid behind. |
| 9 | `refresh_token=AQXsl0K9` | The value is absent. |
| 10 | `api-key: k-9912-aa` | The value is absent, hyphenated label and all. |
| 11 | `https://api.crunchbase.com/v4/entities?user_key=zz` | Neither the locator nor the query value survives. |
| 12 | `ops@example.com` | The address is absent. |
| 13 | `nJ8kQ2vX7pL1mW4tR6yB` | An unlabelled opaque run is absent. |
| S1 | `alias_unresolved` | Returned **byte-identical**. |
| S2 | `x_bst_startuptrk.crunchbase_api` | Returned **byte-identical**. |
| S3 | `matches=2` | Returned **byte-identical**. |
| S4 | `com.glide.rest.SocketTimeoutException` | Returned **byte-identical** — the `internal` code's only diagnostic. |

### Step 3.1 — Probe Crunchbase with the provider-correct header

Run this as a background script in the `x_bst_startuptrk` scope, from **System Definition > Scripts - Background** with the application picker set to **Boston Startup Tracker**. It composes the header Crunchbase actually requires, reads the key through the alias, and prints one line: the status code, the response length, the closed code of [Step 3.0a](#step-30a--the-closed-fault-codes-and-the-redaction-rule-both-probes-share) and its bounded detail.

```javascript
(function probeCrunchbase() {
    var ALIAS = 'x_bst_startuptrk.crunchbase_api';
    var TIMEOUT_MS = 30000;
    var DETAIL_LIMIT = 120;

    var status = 0;
    var bodyLength = 0;
    var code = '';
    var detail = '';

    // The one application sanitiser. Applied to every detail before it is recorded. See Step 3.0a.
    var SAFE = new x_bst_startuptrk.AppProperties();

    // Classifies a transport failure into one closed reason, so no provider, platform or
    // exception message text is ever recorded as a detail.
    function faultReason(text) {
        var value = String(text === null || text === undefined ? '' : text).toLowerCase();
        if (value.indexOf('time') !== -1) {
            return 'reason=timeout';
        }
        if (value.indexOf('unknown host') !== -1 || value.indexOf('unknownhost') !== -1) {
            return 'reason=dns';
        }
        if (value.indexOf('ssl') !== -1 || value.indexOf('tls') !== -1
                || value.indexOf('certificate') !== -1) {
            return 'reason=tls';
        }
        if (value.indexOf('connect') !== -1 || value.indexOf('refused') !== -1
                || value.indexOf('reset') !== -1) {
            return 'reason=connect';
        }
        return 'reason=other';
    }

    function fail(faultCode, faultDetail) {
        code = faultCode;
        detail = SAFE.safeText(faultDetail, DETAIL_LIMIT);
    }

    function report() {
        gs.info('probe crunchbase: status=' + status
            + ' body_length=' + bodyLength
            + ' code=' + (code || 'ok')
            + ' detail=' + detail);
    }

    try {
        var alias = new GlideRecord('sys_alias');
        // The scoped API ID lives in `id`; `name` holds the unprefixed label, so querying
        // `name` with a dotted value matches nothing and the probe would report
        // `alias_unresolved` for a reason that is not the alias state. Guide 01's
        // "Three identifiers" table is authoritative.
        alias.addQuery('id', ALIAS);
        alias.query();
        var matches = alias.getRowCount();
        if (matches !== 1) {
            fail(matches === 0 ? 'alias_unresolved' : 'alias_ambiguous', 'matches=' + matches);
            report();
            return;
        }
        alias.next();

        var info = new sn_cc.ConnectionInfoProvider().getConnectionInfo(alias.getUniqueValue());
        if (!info) {
            fail('connection_unresolved', '');
            report();
            return;
        }

        var userKey = info.getCredentialAttribute('password');
        if (!userKey) {
            fail('credential_unreadable', 'attribute=password');
            report();
            return;
        }

        var base = new x_bst_startuptrk.AppProperties().getCrunchbaseBaseUrl();
        var request = new sn_ws.RESTMessageV2();
        request.setHttpMethod('get');
        request.setEndpoint(base + '/entities/organizations/crunchbase?field_ids=identifier');
        request.setRequestHeader('X-cb-user-key', userKey);
        request.setRequestHeader('Accept', 'application/json');
        request.setHttpTimeout(TIMEOUT_MS);

        var response = request.execute();
        if (response.haveError()) {
            fail('transport', faultReason(response.getErrorMessage()));
            report();
            return;
        }

        status = parseInt(response.getStatusCode(), 10) || 0;
        var body = response.getBody();
        bodyLength = body ? ('' + body).length : 0;
        if (status < 200 || status > 299) {
            fail('http_status', 'status=' + status);
        }
        report();
    } catch (error) {
        status = 0;
        fail('internal', error && error.name ? error.name : 'Error');
        report();
    }
})();
```

**The script prints one line carrying a status, a length, a closed code and a bounded redacted detail. It never prints the key, the header, the endpoint, the query string, the body, or any provider or exception message text.** Read the code and status together.

| `code` and status | Meaning | Action |
| --- | --- | --- |
| `ok`, `200` | The key authenticates and is entitled to the Entity endpoint on the root the property currently holds. | Record `pass`. |
| `http_status`, `401` | The key is absent, wrong, or revoked. | Record `fail`, fault class `credential`, and escalate through [If an alias is genuinely absent](#path-b--a-credential-is-not-provisioned). |
| `http_status`, `403` | The key authenticates but the licence does not cover the endpoint. | Record `fail`, fault class **`entitlement`**, quoting the entitlement row under [Product entitlement each alias requires](#product-entitlement-each-alias-requires). |
| `http_status`, `404` or `410` | The **root itself** is not served. This says nothing about the key. | Record `fail`, fault class **`configuration`**, and follow [Updating the non-secret base URL](#updating-the-non-secret-base-url) before re-running. |
| `http_status`, `429` | The provider's own rate limit, 200 requests per minute, is exhausted by other traffic. | Wait sixty seconds and re-run. This is not a defect and is not recorded as a fault. |
| `alias_unresolved` or `alias_ambiguous` | The alias **API ID** matched zero `sys_alias` records, or more than one. | Record `fail`, fault class `credential`, and follow [Step 0](#step-0--establish-the-credential-posture) and [If an alias is genuinely absent](#path-b--a-credential-is-not-provisioned). |
| `connection_unresolved` or `credential_unreadable` | The alias exists but its connection or credential chain does not resolve. | Record `fail`, fault class `credential`, and work back through the chain as set out in [Step 3.0](#step-30--run-the-generic-connection-test-as-a-diagnostic). |
| `transport`, status `0` | The instance cannot reach the provider. | Record `fail`, fault class `connectivity`, and check outbound connectivity before concluding anything about the credential or the root. |
| `internal`, status `0` | The probe threw. The class name is in the detail. | Record `fail`, fault class `connectivity` where the class names a network or socket condition, otherwise `configuration`. Re-run once before escalating. |

#### Step 3.1 is the activation gate for the Crunchbase base URL

`x_bst_startuptrk.crunchbase.base_url` is delivered holding `https://api.crunchbase.com/api/v4`, which is also the fallback inside `AppProperties.getCrunchbaseBaseUrl()`. **The provider labels that root a legacy v4 root and publishes newer roots alongside it, so the delivered value is a candidate endpoint and not a confirmed one.**

**Live mode is not activated on Crunchbase until this probe returns `code=ok` with status `200` against the value the property currently holds.** Concretely, that means all three of the following are true before `x_bst_startuptrk.ingestion.source_mode` is set to `live` or any Crunchbase result is labelled `live validated`:

| # | Condition |
| --- | --- |
| 1 | [Step 3.1](#step-31--probe-crunchbase-with-the-provider-correct-header) printed `code=ok` and `status=200`. |
| 2 | The `status=200` was obtained against the value `x_bst_startuptrk.crunchbase.base_url` holds **at that moment**, not against a value that was subsequently changed. |
| 3 | The property value and the connection record's **Connection URL** of [Step 1.3](#step-13--build-or-confirm-the-connection-record-fields) are equal. |

A `404` or a `410` from this probe is a **configuration** fault and not a credential fault: it says the root is no longer served. A `401` or a `403` is the opposite — the root is served and it is the key or the licence that is at fault, so the root needs no change.

#### Updating the non-secret base URL

Follow this only when [Step 3.1](#step-31--probe-crunchbase-with-the-provider-correct-header) returned `http_status` with `404` or `410`. The same five items apply to `x_bst_startuptrk.linkedin.base_url` if [Step 3.2](#step-32--probe-linkedin-with-all-three-required-headers) returns the same pair.

1. Obtain the currently published root from the provider's own API documentation. Record where you read it and the date you read it.
2. Open **System Definition > System Properties**, filter on **Name** `is` `x_bst_startuptrk.crunchbase.base_url`, and set **Value** to that root with **no trailing slash**. The property is declared `is_private` `false` and holds no credential, so this is an ordinary configuration edit.
3. Open the connection record of [Step 1.3](#step-13--build-or-confirm-the-connection-record-fields) and set **Connection URL** to the same value. The two must be equal and the property is the source of the value.
4. Re-run [Step 3.1](#step-31--probe-crunchbase-with-the-provider-correct-header). Record `pass` only on `code=ok` with `status=200`.
5. Record the change in the evidence table of [Step 3.3](#step-33--record-the-probe-outcomes): the previous value, the new value, the documentation source and its date, and the probe status obtained afterwards.

This is an **instance configuration change, not a code change**. The Update Set is not re-exported and `AppProperties` is not edited: the delivered fallback stays `https://api.crunchbase.com/api/v4` and is used only when the property is absent or empty.

### Step 3.2 — Probe LinkedIn with all three required headers

Run the same way, with the same exception boundary and the same closed codes. The three headers are all mandatory; omitting either versioning header fails the call regardless of the token. Substitute a numeric organization identifier the developer application is entitled to read for `<ORGANIZATION_ID>`; the credential owner supplies it.

```javascript
(function probeLinkedin() {
    var ALIAS = 'x_bst_startuptrk.linkedin_oauth';
    var ORGANIZATION_ID = '<ORGANIZATION_ID>';
    var TIMEOUT_MS = 30000;
    var DETAIL_LIMIT = 120;

    var status = 0;
    var bodyLength = 0;
    var code = '';
    var detail = '';

    // The one application sanitiser. Applied to every detail before it is recorded. See Step 3.0a.
    var SAFE = new x_bst_startuptrk.AppProperties();

    // Classifies a transport failure into one closed reason, so no provider, platform or
    // exception message text is ever recorded as a detail.
    function faultReason(text) {
        var value = String(text === null || text === undefined ? '' : text).toLowerCase();
        if (value.indexOf('time') !== -1) {
            return 'reason=timeout';
        }
        if (value.indexOf('unknown host') !== -1 || value.indexOf('unknownhost') !== -1) {
            return 'reason=dns';
        }
        if (value.indexOf('ssl') !== -1 || value.indexOf('tls') !== -1
                || value.indexOf('certificate') !== -1) {
            return 'reason=tls';
        }
        if (value.indexOf('connect') !== -1 || value.indexOf('refused') !== -1
                || value.indexOf('reset') !== -1) {
            return 'reason=connect';
        }
        return 'reason=other';
    }

    function fail(faultCode, faultDetail) {
        code = faultCode;
        detail = SAFE.safeText(faultDetail, DETAIL_LIMIT);
    }

    function report() {
        gs.info('probe linkedin: status=' + status
            + ' body_length=' + bodyLength
            + ' code=' + (code || 'ok')
            + ' detail=' + detail);
    }

    try {
        var alias = new GlideRecord('sys_alias');
        // The scoped API ID lives in `id`; `name` holds the unprefixed label, so querying
        // `name` with a dotted value matches nothing and the probe would report
        // `alias_unresolved` for a reason that is not the alias state. Guide 01's
        // "Three identifiers" table is authoritative.
        alias.addQuery('id', ALIAS);
        alias.query();
        var matches = alias.getRowCount();
        if (matches !== 1) {
            fail(matches === 0 ? 'alias_unresolved' : 'alias_ambiguous', 'matches=' + matches);
            report();
            return;
        }
        alias.next();

        var info = new sn_cc.ConnectionInfoProvider().getConnectionInfo(alias.getUniqueValue());
        if (!info) {
            fail('connection_unresolved', '');
            report();
            return;
        }

        var profile = info.getCredentialAttribute('oauth_entity_profile');
        if (!profile) {
            fail('credential_unreadable', 'attribute=oauth_entity_profile');
            report();
            return;
        }

        var props = new x_bst_startuptrk.AppProperties();
        var request = new sn_ws.RESTMessageV2();
        request.setHttpMethod('get');
        request.setEndpoint(props.getLinkedinBaseUrl()
            + '/organizationsLookup?ids=List(' + ORGANIZATION_ID + ')');
        request.setAuthenticationProfile('oauth2', profile);
        request.setRequestHeader('X-Restli-Protocol-Version', '2.0.0');
        request.setRequestHeader('LinkedIn-Version', props.getLinkedinApiVersion());
        request.setRequestHeader('Accept', 'application/json');
        request.setHttpTimeout(TIMEOUT_MS);

        var response = request.execute();
        if (response.haveError()) {
            fail('transport', faultReason(response.getErrorMessage()));
            report();
            return;
        }

        status = parseInt(response.getStatusCode(), 10) || 0;
        var body = response.getBody();
        bodyLength = body ? ('' + body).length : 0;
        if (status < 200 || status > 299) {
            fail('http_status', 'status=' + status);
        }
        report();
    } catch (error) {
        status = 0;
        fail('internal', error && error.name ? error.name : 'Error');
        report();
    }
})();
```

| `code` and status | Meaning | Action |
| --- | --- | --- |
| `ok`, `200` | The token authenticates, both versioning headers are accepted, and the scope covers the organization. | Record `pass`. |
| `http_status`, `401` | The access token could not be obtained from the refresh token, or the refresh token has expired or been revoked. | Record `fail`, fault class `credential`, re-check [Step 2.7](#step-27--confirm-the-refresh-token-is-on-file-and-refresh-works), then escalate. |
| `http_status`, `403` | The token is valid but its scope does not cover an organization read. | Record `fail`, fault class **`scope`**. Widening the scope requires re-issuing the refresh token; see the **OAuth Resources** row in [Step 2.6](#step-26--confirm-the-oauth-entity-profile). |
| `http_status`, `404` or `410` | The **root itself** is not served. | Record `fail`, fault class **`configuration`**, and follow [Updating the non-secret base URL](#updating-the-non-secret-base-url) against `x_bst_startuptrk.linkedin.base_url` before re-running. |
| `http_status`, `426` or a version error | The `LinkedIn-Version` value is retired or malformed. | Record `fail` with the fault class `configuration`. The value is the code constant `AppProperties.LINKEDIN_API_VERSION`, so the correction is a scoped-code change: set it to a currently supported `YYYYMM`, capture it in an Update Set, commit, and re-run this probe. This is not a credential fault. |
| `alias_unresolved`, `alias_ambiguous`, `connection_unresolved` or `credential_unreadable` | The alias, its connection or its credential chain does not resolve. | Record `fail`, fault class `credential`, and work back through the chain of [Step 2.3](#step-23--build-or-confirm-the-connection-record-fields) through [Step 2.7](#step-27--confirm-the-refresh-token-is-on-file-and-refresh-works). |
| `transport`, status `0` | The instance cannot reach the provider. | Record `fail`, fault class `connectivity`. |
| `internal`, status `0` | The probe threw. The class name is in the detail. | Record `fail`, fault class `connectivity` where the class names a network or socket condition, otherwise `configuration`. Re-run once before escalating. |

**Live mode is not activated on LinkedIn until this probe returns `code=ok` with status `200`**, on the same three conditions [Step 3.1](#step-31--probe-crunchbase-with-the-provider-correct-header) states, read against `x_bst_startuptrk.linkedin.base_url` and the connection record of [Step 2.3](#step-23--build-or-confirm-the-connection-record-fields).

### Step 3.3 — Record the probe outcomes

| # | Alias | Generic connection test (diagnostic) | Probe `code` | Probe status | Base URL the probe ran against | Probe outcome | Fault class if failed | Timestamp (UTC) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `x_bst_startuptrk.crunchbase_api` | | | | | | | |
| 2 | `x_bst_startuptrk.linkedin_oauth` | | | | | | | |

Record the closed `code` exactly as the probe printed it, the numeric status, the value the base-URL property held **at the moment the probe ran**, `pass` or `fail`, one of `credential`, `entitlement`, `scope`, `configuration`, `connectivity` or `none` as the fault class, and the timestamp in `YYYY-MM-DD HH:MM:SS` form. The closed codes are defined in [Step 3.0a](#step-30a--the-closed-fault-codes-and-the-redaction-rule-both-probes-share). **Record no credential value, no header value, no probe `detail` string and no response body in any field of this table.**

Where a base URL was changed under [Updating the non-secret base URL](#updating-the-non-secret-base-url), add one row per change below, and keep the row above as the outcome of the **final** probe.

| # | Property changed | Previous value | New value | Documentation source and date read | Probe status afterwards |
| --- | --- | --- | --- | --- | --- |
| 1 | | | | | |

**Both probes returning `code=ok` with status `200` is the condition for the live-validation gate, and for nothing else.** Guides 02 and 03 are **not** blocked by a failed probe: build both flows in either posture, and let the recorded posture decide how their results are labelled. See [Credential posture](#credential-posture) for the three separate gates. Building a flow against an unprovisioned alias is expected in the unprovisioned posture; what must never happen is a run labelled `live validated` without two `code=ok` rows above.

**And the same two rows are the activation gate for live ingestion.** `x_bst_startuptrk.ingestion.source_mode` is not set to `live`, on either source, until that source's probe row reads `code=ok` and `status=200` against the base URL recorded beside it. A probe that returned `http_status` with `404` or `410` is a configuration fault on the root itself, and activating live mode on an unserved root produces a run that fails for a reason unrelated to the credential.

For LinkedIn, return to [Step 2.7](#step-27--confirm-the-refresh-token-is-on-file-and-refresh-works) after a `200` probe and complete its item 5, confirming that the access token was refreshed without operator involvement.

### The route each outcome selects, and the entry condition for guides 02 and 03

The route each outcome selects is exact:

| Outcome for a source | Which route to build | Which label its results carry |
| --- | --- | --- |
| `pass` | Live-first, with fallback on authentication failure, timeout or malformed response | `live validated` when the run used the live call, `fallback validated` when it fell back |
| `fail` | Forced fallback: `x_bst_startuptrk.ingestion.source_mode` set to `fallback`, no REST step enabled | `fallback validated`, always |
| `n/a — contract-gated, fallback only` | Forced fallback, and the live step is not built at all until the gate of [Step 2.0](#step-20--the-product-contract-gate-which-decides-whether-step-2-runs-at-all) is satisfied | `fallback validated`, always |

The entry condition for [`02-flow-crunchbase-ingestion.md`](02-flow-crunchbase-ingestion.md) and [`03-flow-linkedin-ingestion.md`](03-flow-linkedin-ingestion.md) depends on the path, and is stated once here:

| Path | Entry condition for guides 02 and 03 | What the flows may claim |
| --- | --- | --- |
| **A** | **Both aliases test green.** Both outcomes read `pass`. A flow built against an alias that has not tested green fails at its first execution, and the failure presents as a flow defect rather than as the credential fault it is. | The live path may be exercised, and a run that completed a live call may be labelled `live validated`. |
| **B** | **Both alias record sets exist, are bound, and are name-propagated**, and `x_bst_startuptrk.ingestion.source_mode` reads `fallback`. The connection-test outcome is recorded, not passed. | The live path is not exercised. Every run reads the staging table and **every result is labelled `fallback validated`**. |


On Path A, for LinkedIn, return to [Step 2.7](#step-27--confirm-the-refresh-token-is-on-file-and-refresh-works) after a successful test and complete its item 5, confirming that the access token was refreshed without operator involvement. On Path B there is no refresh token, so item 5 does not apply and is recorded as such.

## Path B — a credential is not provisioned

**This section is the credential half of Path B of [Readiness paths](#readiness-paths--live-and-sanctioned-fallback).** It records what the credential owner still has to supply, and it is the one place in this guide that produces a **pending item** rather than a built record. On the instance recorded for this delivery it is reached for both aliases.

This section applies when an alias, a connection, a credential, an OAuth provider, an OAuth profile or a refresh token cannot be found; when a record is present but its name does not match; when a secret-bearing field is empty; or when a connection test fails against records that are otherwise correctly bound. **It is the observed condition on the target instance**, and it is a documented route through this guide rather than a halt.

It applies when a credential record, an OAuth provider, an OAuth profile or a refresh token cannot be found, or when one is present but a binding does not resolve, or when a connection test fails against definition records that are otherwise correctly bound. It also applies to the duplicate-identifier condition of [Step 1.1](#step-11--locate-the-alias-record) item 4, which is an administrator action rather than a credential one.

**The build proceeds. The claim does not.** Path B produces a working, resolvable alias binding and a fully built ingestion pipeline; what it does not produce is evidence of live integration. Those two statements are the whole of it.

**Two absolutes hold on this path.** No credential value is placed, invented, approximated or copied from anywhere — the credentials are the property of their owner. And no result obtained on this path is labelled `live validated`.

### B.1 — Record the condition

Record the following, precisely and **without any credential value**: the alias **API ID** searched for, and the column searched (`id`); the `sys_alias` row count returned; which of the six record classes did not resolve; whether a secret-bearing field was empty; and, for a connection-test failure, the failure text the platform returned. This record is the input to the escalation of [B.5](#b5--escalate-in-parallel) and the evidence for the `fallback validated` label.

### B.2 — Create the Crunchbase alias metadata

Three records, **no secret**. Create them in this order, because each binds to the one before it.

1. **The credential record.** **Connections & Credentials > Credentials**, **New**, class **Basic Auth Credentials** — or **API Key Credentials** under the alternate binding of [Step 1.4](#step-14--confirm-the-credential-record-that-holds-the-user-key). Set **Name** to a human-readable label such as `Crunchbase API key`, set **Application** to `Boston Startup Tracker`, set **Active** to `true`, and leave the secret-bearing field — **Password**, or **API Key** under the alternate binding — **empty**. Save. Every other field takes the value the table of [Step 1.4](#step-14--confirm-the-credential-record-that-holds-the-user-key) specifies.
2. **The alias record.** **Connections & Credentials > Connection & Credential Aliases**, **New**. Set **Name** to `crunchbase_api` — the **unprefixed** label, exactly as the table of [Step 1.2](#step-12--build-or-confirm-the-alias-record-fields) requires; typing the dotted form here produces a generated API ID of `x_bst_startuptrk.x_bst_startuptrk.crunchbase_api` and nothing resolves. Confirm the generated **ID** reads `x_bst_startuptrk.crunchbase_api` rather than setting it. Then set **Type** to `Connection and Credential`, **Connection type** to `HTTP`, and **Application** to `Boston Startup Tracker`. Every other field takes the value the table of [Step 1.2](#step-12--build-or-confirm-the-alias-record-fields) specifies. Save, then set the credential record's **Credential alias** list to include this alias.
3. **The connection record.** **Connections & Credentials > Connections**, **New**, class **HTTP(s) Connection**. Set **Connection alias** to the alias just created, **Credential** to the credential record of item 1, **Connection URL** to the **exact value** of the `x_bst_startuptrk.crunchbase.base_url` property read as [Step 1.3](#step-13--build-or-confirm-the-connection-record-fields) directs, **Application** to `Boston Startup Tracker`, and **Active** to `true`. Every other field takes the value the table of [Step 1.3](#step-13--build-or-confirm-the-connection-record-fields) specifies. **The property is the authority for the URL and this field is its mirror**; guides 02 and 03 assert the two are equal character for character.

Then walk [Step 1.2](#step-12--build-or-confirm-the-alias-record-fields), [Step 1.3](#step-13--build-or-confirm-the-connection-record-fields) and [Step 1.4](#step-14--confirm-the-credential-record-that-holds-the-user-key) as written, confirming every field. The only permitted difference from Path A is that the credential's secret-bearing field — **Password**, or **API Key** under the alternate binding — reads *empty* rather than *as provisioned*.

### B.3 — Create the LinkedIn alias metadata

Two records, **no secret**, and deliberately **not** the OAuth provider, profile or refresh-token records.

1. **The credential record.** **Connections & Credentials > Credentials**, **New**, class **OAuth 2.0 Credentials**. Set **Name** to a label such as `LinkedIn OAuth 2.0`, **Integration Type** to `System`, **Application** to `Boston Startup Tracker`, **Active** to `true`, and leave **OAuth Entity Profile** **empty**. Save.
2. **The alias record**, then **the connection record**, exactly as [B.2](#b2--create-the-crunchbase-alias-metadata) items 2 and 3, substituting the **unprefixed** alias Name `linkedin_oauth` — whose generated API ID is confirmed to read `x_bst_startuptrk.linkedin_oauth` — and the `x_bst_startuptrk.linkedin.base_url` property.

**Do not create the `oauth_entity` provider record, the `oauth_entity_profile` record or any `oauth_credential` token record.** Every one of them requires a client identifier, a client secret or a refresh token that only the credential owner can supply, and creating an empty or invented one would be a fabricated binding. [Step 2.5](#step-25--confirm-the-oauth-provider-record), [Step 2.6](#step-26--confirm-the-oauth-entity-profile) and [Step 2.7](#step-27--confirm-the-refresh-token-is-on-file-and-refresh-works) are therefore **not performed on Path B**; record each as `not applicable — no credential provisioned`.

### B.4 — Force the fallback and label the evidence

1. Open `sys_properties`, filter on **Name** `is` `x_bst_startuptrk.ingestion.source_mode`, and set its **Value** to **`fallback`**. This is the only property changed on this path, and it holds no secret. Do this **before** either flow is activated, so no scheduled execution attempts a live call it cannot complete.
2. Load the staging table before running either flow, per [`06-staging-table-csv-import.md`](06-staging-table-csv-import.md). The fallback path reads `x_bst_startuptrk_ingest_staging`, and an empty table demonstrates none of the cleaning rules.
3. **Label every ingestion result `fallback validated` and never `live validated`.** The labelling rule and its effect on the acceptance evidence are stated in [`../../sample-data/README.md`](../../sample-data/README.md); the flow tests apply it per [`05-atf-test-suites.md`](05-atf-test-suites.md); the flagged items of this delivery are listed in [`../gaps-and-flags.md`](../gaps-and-flags.md).
4. Record the connection-test outcome for both aliases as `not applicable — no credential provisioned` in the table under [Step 3](#step-3--test-both-connections), and complete [Step 4](#step-4--propagate-both-alias-names-into-guides-02-and-03) as written — name propagation is a Path B requirement, because the flows resolve the alias by name whichever path the build is on.

### B.5 — Escalate in parallel

Escalation runs alongside the build, not instead of it. **Escalate to the credential owner** — the party that holds the Crunchbase API key, or the LinkedIn OAuth 2.0 client identifier, client secret and refresh token. Supply the record of [B.1](#b1--record-the-condition), ask them to provision or re-issue the material on this instance, and ask them to confirm the alias name they bound it to. Do not invent a key, a token, a client identifier, a client secret or anything that resembles one; do not rename an unrelated alias to match; and do not point a connection at a different credential to make a test pass.

**Do not modify anything outside `x_bst_startuptrk`** while waiting. Prompt section 6.0 forbids it. Creating the alias, connection and credential records of [B.2](#b2--create-the-crunchbase-alias-metadata) and [B.3](#b3--create-the-linkedin-alias-metadata) does not breach that: each carries the `x_bst_startuptrk` scope, which is what the **Application** field on all three record classes asserts.

### B.6 — Crossing over to Path A later

When the owner confirms the material is in place, the credential record already exists and only needs its secret-bearing fields populated **by the owner**, plus the LinkedIn provider, profile and token records they supply. Then:

1. Re-run the confirmation sequence for that alias from [Step 1.1](#step-11--locate-the-alias-record) or [Step 2.1](#step-21--locate-the-alias-record) in full.
2. Run the connection test of [Step 3](#step-3--test-both-connections) and require `pass`.
3. Set `x_bst_startuptrk.ingestion.source_mode` back to **`live`**.
4. Re-run the ingestion evidence. **A `fallback validated` result is not retrospectively upgraded**: the runs recorded on Path B stay labelled as they were, and live validation requires its own runs.

### B.7 — A duplicate-name condition

More than one `sys_alias` record carrying one of the two names is neither Path A nor Path B. Do not delete either record and do not rename one: an alias you did not create may belong to another application. Record both `sys_id` values, stop, and escalate to the instance owner for a decision on which record is authoritative.

**The definition records are not affected and are not deferred.** The alias record and the connection record are built or confirmed for this alias before this section is reached, per Steps 1.1 and 1.3 or Steps 2.1 and 2.3. What is deferred is the credential itself, the connection's **Credential** binding, and the connection test.

**Do not place a credential value.** On Path B the credential **metadata** record is created by [B.2](#b2--create-the-crunchbase-alias-metadata) or [B.3](#b3--create-the-linkedin-alias-metadata) with every secret-bearing field left empty; the values themselves are never created here. The credentials are the property of their owner and are provisioned by that owner.

1. **Stop the credential sequence for this alias.** Skip its remaining credential confirmation steps and its connection test, and record `not applicable — no credential provisioned` for both. Do **not** stop the guide and do **not** stop the build: the definition records are already built, the other alias is worked to whichever path its own state selects, and guides 02 and 03 proceed as item 6 sets out.
2. **Record what is missing**, precisely and without any credential value: the alias **API ID** searched for, and the column searched (`id`); which of the credential record classes did not resolve; and, for a connection-test failure, the failure text the platform returned. Record it in the pending-item register below.
3. **Escalate to the credential owner** — the party that holds the Crunchbase API key, or the LinkedIn OAuth 2.0 client identifier, client secret and refresh token. Ask them to provision or re-issue the material on this instance, to bind it to the alias record this guide built, and to populate the connection's **Credential** field.
4. **Do not invent a key, a token, a client identifier, a client secret or a placeholder that resembles one.** Do not rename an existing unrelated alias to match. Do not point the connection at a different credential to make the test pass.
5. **Do not modify anything outside `x_bst_startuptrk`** while waiting. Prompt section 6.0 forbids it.
6. **Proceed to guides 02 and 03. Neither is blocked.** Build, publish and validate both flows in full, then force the source mode by setting `x_bst_startuptrk.ingestion.source_mode` to `fallback`. Ingestion then takes its sanctioned fallback path, which requires no live credential: it reads the staging table loaded from the sample dataset. The dataset, its column contract and that property are specified in [`../../sample-data/README.md`](../../sample-data/README.md), and the load procedure is [`06-staging-table-csv-import.md`](06-staging-table-csv-import.md). Wherever those guides direct an alias name into an action, take the **API ID** off the alias record built or confirmed here, per [Step 4](#step-4--propagate-both-alias-names-into-guides-02-and-03).
7. **Label the evidence accordingly.** While either credential is unprovisioned, every ingestion run reads the fallback dataset, and every result must be labelled `fallback validated` and never `live validated`. That labelling rule and its effect on the acceptance evidence are stated in [`../../sample-data/README.md`](../../sample-data/README.md); the flagged items of this delivery are listed in [`../gaps-and-flags.md`](../gaps-and-flags.md).
8. **Resume at [Step 1.4](#step-14--confirm-the-credential-record-that-holds-the-user-key) or [Step 2.4](#step-24--confirm-the-oauth-20-credential-record-fields)** once the owner confirms the material is in place — not at the locate step, because the alias and connection records already exist and are correct. That alias then moves to Path A: revise its readiness register entry, populate the connection's **Credential** field with the provisioned record, run the credential confirmation sequence and the connection test, and only then may a run of the corresponding flow be relabelled `live validated`. Nothing built in the meantime is discarded or rebuilt — the flow already references the alias by the same API ID.

Record every pending item here, one row per alias, and carry the same rows into the completion criteria:

| # | Alias, by API ID | Credential records still to be provisioned | Connection **Credential** field populated | Connection test | Escalated on (UTC) | Owner acknowledged |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `x_bst_startuptrk.crunchbase_api` | | | | | |
| 2 | `x_bst_startuptrk.linkedin_oauth` | | | | | |

Name the record classes by table name in the third column, record `yes` or `no` in the fourth, `pass`, `fail` or `pending` in the fifth, and a timestamp in `YYYY-MM-DD HH:MM:SS` form. **Record no credential value in any field of this table.**

**This is the live-credential hand-off.** It is a credential-owner action tracked separately from the package build, and the build is complete and acceptable without it — but it is tracked as **outstanding**, not closed, and no document of this package may report a pending credential as a delivered artifact. The acceptance consequence — a criterion satisfied by three clean `fallback validated` runs — is stated in [`../validation-checklist.md`](../validation-checklist.md).

## Operational warning — the binding is by name

**The flow-to-alias binding is by name, and a name mismatch fails at run time, not at build time.**

A flow that names an alias that does not exist, or that names it with a typographic error, saves without complaint and publishes without complaint. Nothing in the Flow Designer interface reports the fault. It surfaces only when the flow executes: the execution fails, and the failure presents as a flow error rather than as the missing binding it is. A scheduled flow can therefore fail silently on its cadence until someone reads the flow execution log.

Three consequences follow, and each is a step to take rather than a caution to note:

1. **Copy, never retype, and copy the API ID.** The value a flow or an action binds to is the generated **API ID**, not the **Name** — see [Three identifiers, and which is which](#three-identifiers-and-which-is-which). Copy the **ID** field character for character from the alias record built or confirmed in [Step 1.2](#step-12--build-or-confirm-the-alias-record-fields) or [Step 2.2](#step-22--build-or-confirm-the-alias-record-fields). This is the same on both paths, because the alias record exists in both. Do not type the value from memory and do not rely on autocomplete.
2. **Watch the two separators.** The scope prefix is joined by a **dot** and the resource part by an **underscore**: `x_bst_startuptrk.crunchbase_api`, not `x_bst_startuptrk_crunchbase_api` and not `x_bst_startuptrk.crunchbase-api`. The same applies to `x_bst_startuptrk.linkedin_oauth`.
3. **Test before running the flow against the live source.** For an alias in Path A, guides 02 and 03 each require the connection test of [Step 3](#step-3--test-both-connections) to have passed before that flow is executed live; neither guide requires it before the flow is built, published or validated in `fallback` mode. **On Path B there is no test to pass**, so the protection against a mismatch is items 1 and 2 above plus the character-for-character comparison of [Step 4](#step-4--propagate-both-alias-names-into-guides-02-and-03) — run that comparison with extra care, because on Path B nothing else will catch a typographic error before the credential is eventually provisioned.

## Step 4 — Propagate both alias names into guides 02 and 03

Carry the alias **API ID** forward — not the **Name**, per [Three identifiers, and which is which](#three-identifiers-and-which-is-which). Run this step for **both** aliases regardless of path. The source of the value is the same in both: the alias record, which this guide has built or confirmed by the time this step runs.

**This step is required on both readiness paths**, because the flows resolve the alias by its API ID whichever path the build is on.

- **Path A.** Do this immediately after [Step 3](#step-3--test-both-connections) reads `pass`, while the record is still open.
- **Path B.** Do it as soon as [Step 1.2](#step-12--build-or-confirm-the-alias-record-fields) or [Step 2.2](#step-22--build-or-confirm-the-alias-record-fields) is complete. The value the platform generated equals the canonical value stated throughout this guide, because it is derived from the application scope and the alias **Name** — so nothing built against it now is rebuilt when the credential arrives.

1. For the Crunchbase alias, put the API ID on the clipboard: open the alias record of [Step 1.2](#step-12--build-or-confirm-the-alias-record-fields) and copy its **ID** field.
2. Paste it into the alias field of the Crunchbase ingestion action as directed by [`02-flow-crunchbase-ingestion.md`](02-flow-crunchbase-ingestion.md). Paste; do not type.
3. Compare the pasted value against `x_bst_startuptrk.crunchbase_api` character for character, including both separators.
4. Repeat items 1 to 3 for the LinkedIn alias — the record of [Step 2.2](#step-22--build-or-confirm-the-alias-record-fields) — and [`03-flow-linkedin-ingestion.md`](03-flow-linkedin-ingestion.md), comparing against `x_bst_startuptrk.linkedin_oauth`.
5. Record the source and the comparison outcome for both.

| # | Alias API ID placed downstream | Path | Consuming guide | Values match character for character |
| --- | --- | --- | --- | --- |
| 1 | `x_bst_startuptrk.crunchbase_api` | | [`02-flow-crunchbase-ingestion.md`](02-flow-crunchbase-ingestion.md) | |
| 2 | `x_bst_startuptrk.linkedin_oauth` | | [`03-flow-linkedin-ingestion.md`](03-flow-linkedin-ingestion.md) | |

Record `A` or `B` in the path column. In both paths the value is read off the alias record's **ID** field. **Both rows must read `yes` before either flow is saved.**

## The authentication-model change

**LinkedIn moves from a static bearer token to OAuth 2.0.** The legacy integrator sent a fixed module-level constant as a bearer `Authorization` header on every request. The alias `x_bst_startuptrk.linkedin_oauth` authenticates through an OAuth 2.0 client identifier, client secret and refresh token, and the platform exchanges the refresh token for a short-lived access token and renews it without operator involvement. `D-044` carries the decision.

**Crunchbase moves from a URL query parameter to an encrypted secret store plus a request header.** The legacy integrator appended the key as a `user_key` query parameter at three call sites, so the key was written into every access log, proxy log and browser history that saw the URL. It now lives in the **Password** field of the Basic Auth credential behind `x_bst_startuptrk.crunchbase_api`, and the flow reads it through the alias and sends it in an `X-cb-user-key` request header. The key remains a single long-lived string; what changed is that it never appears in a URL and never appears in source.

**What did *not* change is the wire protocol's name.** The credential record's type is `Basic Auth` because that is the platform class that stores a password; Crunchbase itself does not accept HTTP Basic authentication and no Basic `Authorization` header is ever sent to it. [The provider wire contract](#the-provider-wire-contract) states this decoupling and the two consequences that follow from it.

## What this replaces

The two aliases replace the credential handling of the legacy data-collection package. **Nothing in the table below is ported.** The only values carried forward are the two non-secret base URLs; every key, token and header construction is discarded.

| Legacy construct | Location | Replaced by |
| --- | --- | --- |
| Base URL `https://api.crunchbase.com/v3.1` as a module constant | `src/data_collection/api_integrators/crunchbase_integrator.py:L10` | The non-secret system property `x_bst_startuptrk.crunchbase.base_url`, confirmed against the connection record in [Step 1.3](#step-13--build-or-confirm-the-connection-record-fields). **The value is corrected, not carried forward:** the property holds `https://api.crunchbase.com/api/v4`, because the v3.1 base the legacy constant pinned is not the current entitled base. |
| A module-level `API_KEY` string constant | `src/data_collection/api_integrators/crunchbase_integrator.py:L11` | The **Password** field of the Basic Auth credential behind `x_bst_startuptrk.crunchbase_api`, confirmed in [Step 1.4](#step-14--confirm-the-credential-record-that-holds-the-user-key). Held encrypted, never in source. |
| That constant passed as a `user_key` **query parameter**, at three call sites | `src/data_collection/api_integrators/crunchbase_integrator.py:L22`, repeated at `:L41` and `:L60` | An `X-cb-user-key` request header whose value the flow reads through the alias at run time. No key appears in any URL, any flow input, any script step or any Update Set record. A header is not written into the access logs a query parameter reaches. |
| Base URL `https://api.linkedin.com/v2` as a module constant | `src/data_collection/api_integrators/linkedin_integrator.py:L11` | The non-secret system property `x_bst_startuptrk.linkedin.base_url`, confirmed against the connection record in [Step 2.3](#step-23--build-or-confirm-the-connection-record-fields). **The value is corrected, not carried forward:** the property holds `https://api.linkedin.com/rest`, the versioned base. The `/v2` marketing paths the legacy constant pinned are sunset. |
| A module-level `API_KEY` string constant | `src/data_collection/api_integrators/linkedin_integrator.py:L12` | The OAuth 2.0 client identifier and client secret on the provider record of [Step 2.5](#step-25--confirm-the-oauth-provider-record), together with the refresh token of [Step 2.7](#step-27--confirm-the-refresh-token-is-on-file-and-refresh-works), all behind `x_bst_startuptrk.linkedin_oauth`. |
| That constant sent as a **static bearer** `Authorization` header, at two call sites | `src/data_collection/api_integrators/linkedin_integrator.py:L23`, repeated at `:L42` | Platform-managed OAuth 2.0 token exchange. The access token is derived from the refresh token and renewed automatically, and the `Authorization` header is not hand-assembled. The two mandatory versioning headers, `X-Restli-Protocol-Version` and `LinkedIn-Version`, **are** set explicitly by the flow; the legacy integrator sent neither, which is one reason its endpoints no longer resolve. |
| `CRUNCHBASE_API_KEY`, `LINKEDIN_API_KEY` and `GITHUB_API_KEY` as plain environment values | `.env.example:L27-L29` | No environment variable holds an ingestion credential. Both aliases resolve their own credentials on the instance. `GITHUB_API_KEY` has **no counterpart**: this application ingests from Crunchbase and LinkedIn only. |

Both endpoint-configuration properties — `x_bst_startuptrk.crunchbase.base_url` and `x_bst_startuptrk.linkedin.base_url` — are declared with `is_private` `false` and are readable and writable by the `x_bst_startuptrk.admin` role. The LinkedIn API version is not among them: it is the scoped code constant `AppProperties.LINKEDIN_API_VERSION`. **No property in this application holds a secret**; the full eleven-property inventory is in [`../api-reference.md`](../api-reference.md).

## Completion criteria

This guide is complete when every item below holds. All are objectively checkable. The criteria are in three groups: **both paths**, **Path A only**, and **Path B only**. Read the group that applies and record every criterion in it.

**Both paths — all thirteen numbered criteria must hold, together with the five lettered sub-criteria `4a`, `9a`, `9b`, `9c` and `10a`.** **Criteria 1 to 4 cover the four definition records this guide builds and apply on both paths, to both aliases, unconditionally.** Criteria 5 to 10 cover the credential half and apply to an alias in Path A; for an alias in Path B they are recorded `not applicable — no credential provisioned` and are joined by criterion 12. Criterion 11 applies unconditionally, and `9c` applies unconditionally because it is a precondition on activation rather than on a credential.

| # | Group | Criterion |
| --- | --- | --- |
| 1 | Definition | Exactly one `sys_alias` record exists whose **Name** is `crunchbase_api` and whose generated **ID** is `x_bst_startuptrk.crunchbase_api`, with **Type** `Connection and Credential`, **Connection type** `HTTP`, and **Application** `Boston Startup Tracker` — built by [Step 1.2](#step-12--build-or-confirm-the-alias-record-fields) if it was absent. |
| 2 | Definition | Exactly one `sys_alias` record exists whose **Name** is `linkedin_oauth` and whose generated **ID** is `x_bst_startuptrk.linkedin_oauth`, with the same **Type**, **Connection type** and **Application** — built by [Step 2.2](#step-22--build-or-confirm-the-alias-record-fields) if it was absent. |
| 3 | Definition | Each alias has exactly one **active** connection record whose **Connection alias** references it — built by [Step 1.3](#step-13--build-or-confirm-the-connection-record-fields) or [Step 2.3](#step-23--build-or-confirm-the-connection-record-fields) if it was absent. Its **Credential** field is populated in Path A and empty in Path B, where it is a pending item. |
| 4 | Definition | Each connection's **Connection URL** equals the value of its base-URL property: `x_bst_startuptrk.crunchbase.base_url` and `x_bst_startuptrk.linkedin.base_url` respectively. |
| 4a | Definition | `AppProperties.getLinkedinApiVersion()` returns a six-digit `YYYYMM` value that LinkedIn currently supports, and **no** `x_bst_startuptrk.linkedin.api_version` property exists. The value is the scoped code constant `AppProperties.LINKEDIN_API_VERSION`, per [The provider wire contract](#the-provider-wire-contract). |
| 5 | Credential | The Crunchbase credential is of type `Basic Auth`, its **Password** field is populated — or, under the recorded alternate binding, of type `API Key` with its **API Key** field populated, and its **Credential alias** list includes `x_bst_startuptrk.crunchbase_api`. |
| 6 | Credential | The LinkedIn credential is of type `OAuth 2.0` with **Integration Type** `System`, its **OAuth Entity Profile** is populated, and its **Credential alias** list includes `x_bst_startuptrk.linkedin_oauth`. |
| 7 | Credential | The LinkedIn provider record has **Client ID** and **Client Secret** populated, and its **Default Grant type** equals the profile's **Grant type**. |
| 8 | Credential | At least one `oauth_credential` record of type `Refresh Token` exists for that provider. |
| 9 | Credential | **Both provider probes return `code=ok` at status `200`**, both generic connection tests have been run and classified as diagnostics, and every outcome is recorded in the register under [Step 3.3](#step-33--record-the-probe-outcomes). |
| 9a | Credential | **Neither probe ended in an uncaught exception and neither printed provider text.** Each probe produced exactly one log line carrying a status, a body length, one of the closed codes of [Step 3.0a](#step-30a--the-closed-fault-codes-and-the-redaction-rule-both-probes-share) and a redacted detail capped at 120 characters, followed by the `...(truncated)` marker where the sanitiser cut it. |
| 9b | Credential | **Live mode was not activated on either source before that source's probe read `code=ok` at status `200`**, and each recorded status was obtained against the base URL the property held at the time of the probe, per [Updating the non-secret base URL](#updating-the-non-secret-base-url). |
| 9c | Credential | **Live mode was not activated on either source before [the live-activation register](../gaps-and-flags.md#the-live-activation-register) was complete.** Every row `LA1` to `LA9` carries a named owner, a date and a reference to where the evidence is recorded — the operator's staging-retention and erasure obligations, the platform owner's flow-execution-context retention, reader-role and logging-level actions, and `glide.export.escape_formulas`. A passing probe is **necessary and not sufficient**: the probe says the credential works, the register says the instance is ready to hold what the credential fetches. On the instance recorded for this delivery the register is empty, so `x_bst_startuptrk.ingestion.source_mode` remains `fallback` and this criterion is satisfied by that value rather than by the register. |
| 10 | Credential | Both connection records' **Credential** fields are populated, each referencing the credential confirmed for that alias. |
| 10a | Always | The product entitlement behind each alias has been confirmed with the credential owner and recorded against [Product entitlement each alias requires](#product-entitlement-each-alias-requires). |
| 11 | Always | No credential value has been written into any record, any document of this package, any log, any terminal transcript or any evidence table. |
| 12 | Path B | **For each alias in Path B:** the readiness register of [Readiness paths](#readiness-paths--live-and-sanctioned-fallback) records `B`, its counts and a timestamp; the pending-item register of [Path B](#path-b--a-credential-is-not-provisioned) has been completed, carries no credential value, and has been sent to the credential owner; and `x_bst_startuptrk.ingestion.source_mode` reads `fallback`. |
| 13 | Always | Both alias **API IDs** have been propagated and compared character for character, and both rows of the table under [Step 4](#step-4--propagate-both-alias-names-into-guides-02-and-03) read `yes`. |

**Criterion 9 gates the live execution path of guides 02 and 03 for a Path A alias. It gates neither guide's construction, publication nor fallback validation, and for a Path B alias it is a pending item rather than a satisfied one.** **Criterion 11 — no credential value written anywhere — is the one gate the reviewer named under [Referenced documents](#referenced-documents) will check**, and it is the same criterion on both paths.

**What "complete" means on the instance whose posture is recorded under [The recorded posture for this delivery](#the-recorded-posture-for-this-delivery).** All nine both-paths criteria and all seven Path B criteria are satisfied — **two alias records, two connection records and two empty credential containers built**, both API IDs propagated, no credential value anywhere. All eight Path A criteria stand open as pending items against the credential owner for both aliases. That is the accurate statement of this guide's outcome, and it is the statement every document of this package uses: **four definition records delivered, two credential sets outstanding.**

**Path A only — all eight must hold.**

**Criteria A1 to A8 are conditional on a live path being available for that source.** Each reads "either the criterion holds, or that source is recorded `n/a` with its reason and its flow is built on the forced-fallback route." Criteria 10 to 12 are unconditional.

| # | Criterion |
| --- | --- |
| A1 | The Crunchbase credential is of type `Basic Auth` with its **Password** field **populated** — or, under the recorded alternate binding, of type `API Key` with its **API Key** field **populated** — and its **Credential alias** list includes `x_bst_startuptrk.crunchbase_api`. |
| A2 | The LinkedIn credential is of type `OAuth 2.0` with **Integration Type** `System`, its **OAuth Entity Profile** is **populated**, and its **Credential alias** list includes `x_bst_startuptrk.linkedin_oauth`. |
| A3 | The LinkedIn provider record has **Client ID** and **Client Secret** populated, and its **Default Grant type** equals the profile's **Grant type**. |
| A4 | At least one `oauth_credential` record of type `Refresh Token` exists for that provider. |
| A5 | **Both provider probes report `code=ok` at status `200`** against the base URL each property held at the time of the probe, and every outcome is recorded in the register under [Step 3.3](#step-33--record-the-probe-outcomes). |
| A6 | `x_bst_startuptrk.ingestion.source_mode` reads `live`. |
| A7 | **Neither probe ended in an uncaught exception and neither printed provider text.** Each probe produced exactly one log line carrying a status, a body length, one of the closed codes of [Step 3.0a](#step-30a--the-closed-fault-codes-and-the-redaction-rule-both-probes-share) and a redacted detail capped at 120 characters. |
| A8 | **Live mode was not activated on either source before that source's probe read `code=ok` at status `200`**, and each recorded status was obtained against the base URL the property held at the time of the probe, per [Updating the non-secret base URL](#updating-the-non-secret-base-url). |

**Path B only — all seven must hold.** This is the group that applies on the instance whose posture is recorded above.

| # | Criterion |
| --- | --- |
| B1 | The Crunchbase credential record exists, is of type `Basic Auth`, is `active`, carries the `x_bst_startuptrk` scope, has `x_bst_startuptrk.crunchbase_api` in its **Credential alias** list, and its **Password** field is **empty**. |
| B2 | The LinkedIn credential record exists, is of type `OAuth 2.0` with **Integration Type** `System`, is `active`, carries the `x_bst_startuptrk` scope, has `x_bst_startuptrk.linkedin_oauth` in its **Credential alias** list, and its **OAuth Entity Profile** field is **empty**. |
| B3 | **No `oauth_entity`, `oauth_entity_profile` or `oauth_credential` record has been created**, and Steps 2.5, 2.6 and 2.7 are each recorded `not applicable — no credential provisioned`. |
| B4 | Both probe outcomes and both connection-test outcomes are recorded as `not applicable — no credential provisioned` in the register under [Step 3.3](#step-33--record-the-probe-outcomes). |
| B5 | `x_bst_startuptrk.ingestion.source_mode` reads **`fallback`**, and it was set before either flow was activated. |
| B6 | The condition record of [B.1](#b1--record-the-condition) exists, the escalation of [B.5](#b5--escalate-in-parallel) has been raised, and **every ingestion result produced from here on is labelled `fallback validated`**. No artifact of this build claims `live validated`. |
| B7 | **For each alias in Path B:** the readiness register of [Readiness paths](#readiness-paths--live-and-sanctioned-fallback) records `B`, its counts and a timestamp; the pending-item register of [Path B](#path-b--a-credential-is-not-provisioned) has been completed, carries no credential value, and has been sent to the credential owner; and `x_bst_startuptrk.ingestion.source_mode` reads `fallback`. |

Criterion A5 is the gate on guides 02 and 03 on Path A; criteria B1 through B5 are the gate on Path B. The reviewer gate is criterion 11 of the both-paths group, and it is identical on both paths.

## Related documents

| Document | Role |
| --- | --- |
| [`../manual-build-instructions.md`](../manual-build-instructions.md) | The index for this folder and the authoritative execution order. It owns the rule that splits the Update Set from the manual build. |
| [`../deployment-runbook.md`](../deployment-runbook.md) | The import, preview and commit procedure that must complete before this guide starts, with its pre-flight checks, polling intervals, timeouts, rollback and failure matrix. |
| [`../validation-gates.md`](../validation-gates.md) | The eleven required post-commit gates of precondition 4, and the acceptance-required `GATE-COL-01` with `GATE-SEC-01` to `GATE-SEC-03`, plus the one non-normative diagnostic `GATE-SEC-04`, of precondition 5. |
| [`02-flow-crunchbase-ingestion.md`](02-flow-crunchbase-ingestion.md) | Consumes `x_bst_startuptrk.crunchbase_api` by name. Runs after this guide. |
| [`03-flow-linkedin-ingestion.md`](03-flow-linkedin-ingestion.md) | Consumes `x_bst_startuptrk.linkedin_oauth` by name. Runs after this guide. |
| [`../../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml`](../../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml) | Authoritative for the scope name `x_bst_startuptrk` and for the two base-URL property keys. Contains no alias record and no credential material. |
| [`../api-reference.md`](../api-reference.md) | The system-property inventory, including both base-URL properties and the statement that no property holds a secret. |
| [`../../sample-data/README.md`](../../sample-data/README.md) | The fallback dataset used while either credential is unprovisioned, and the `fallback validated` labelling rule. |
| [`../validation-checklist.md`](../validation-checklist.md) | The acceptance criterion satisfied by three clean `fallback validated` ingestion runs, which is what a Path B alias delivers against. |
| [`06-staging-table-csv-import.md`](06-staging-table-csv-import.md) | Loads that fallback dataset into the staging table. |
| [`../gaps-and-flags.md`](../gaps-and-flags.md) | The flagged items of this delivery. Not restated here. |
| [`../../../docs/decisions/DECISION_LOG.md`](../../../docs/decisions/DECISION_LOG.md) | The single source of truth for every "why" behind this guide. |
| [`../../../docs/review/CRITICAL_DECISIONS.md`](../../../docs/review/CRITICAL_DECISIONS.md) | The five highest-risk decisions of this delivery. Its entry 3 is the one this guide is written to satisfy; the reviewer pointer is stated once, under [Referenced documents](#referenced-documents). |
