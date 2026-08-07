# Manual build 03 — LinkedIn ingestion flow — `x_bst_startuptrk`

This guide builds the LinkedIn ingestion flow of the ServiceNow scoped application `x_bst_startuptrk` by hand, on the instance, in Flow Designer. It specifies **one** scheduled flow built from **eight** numbered steps, and for each step it states the step type, every input to set, every data pill consumed, every output produced and the branch behaviour on each outcome. It also states the trigger configuration, the activation procedure, the single manual run that confirms each step, how to read the flow execution log, and the completion criteria to satisfy before this guide is signed off.

**Authority.** The frozen prompt and the Agent Action Plan are authoritative for all application content. The Update Set XML at [`../../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml`](../../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml) is the authoritative source for every table name, column name, choice value, Script Include class name, method name and system-property key cited below; the identifiers used here match those records character for character, and the same identifiers appear in [`../data-model.md`](../data-model.md) and [`../api-reference.md`](../api-reference.md). No variant spelling of any identifier is valid. Where this guide and those records disagree, the records are checked against the prompt and the plan first; where the records match the specification, this guide is corrected to them.

This document carries **no rationale**. It states what to build and how to build it. Every decision behind this flow, every alternative considered and every risk it carries is recorded in [`../../../docs/decisions/DECISION_LOG.md` (planned)](../../../docs/decisions/DECISION_LOG.md), which is the single source of truth for "why". Four points in this guide depart from a literal reading of the requirements — the hourly trigger paired with an elapsed-time guard in place of a trigger interval read from a property, the split that assigns Founder, Executive and JobPosting to LinkedIn while Startup, Investor and FundingRound go to Crunchbase, LinkedIn's move from a static bearer token to OAuth 2.0, and the `record_type` discriminator that decides whether a person becomes a Founder or an Executive. Each is stated below as a build mechanic and cross-referenced to that log. None is argued here.

Operational warnings **are** in scope for this guide and are marked as such. The three warnings under [Operational warnings](#operational-warnings) are load-bearing and must not be skipped: one describes a failure that surfaces at run time rather than at build time, one describes a failure that is silent, and one describes a failure that corrupts company identity across both flows.

## Referenced documents

This guide is executable on its own. All eight steps, every property read, every table written, every cleaning rule, every log write, the trigger, the activation and the verification are stated here in full. An operator needs no other file to build the flow.

Documents marked **(planned)** are in-scope artifacts of this deliverable package that are authored elsewhere in the same delivery. A link to a planned document resolves once that document lands; nothing in this guide depends on reading one first, with the single exception recorded in precondition 7.

| Document | What this guide takes from it |
| --- | --- |
| [`01-connection-credential-aliases.md`](01-connection-credential-aliases.md) | The alias name `x_bst_startuptrk.linkedin_oauth` this flow binds to, and the connection test that must have passed before this flow is saved. |
| [`02-flow-crunchbase-ingestion.md`](02-flow-crunchbase-ingestion.md) | The companion flow. It is the **identical** eight-step skeleton, differing only in source system, alias and target tables. Steps 1, 2, 4, 5, 7 and 8 are the same in both guides. It also builds the Startup records this flow's parent references resolve against, through the **shared Startup upsert path** of [6.2](#62--the-shared-startup-upsert-path). |
| [`06-staging-table-csv-import.md` (planned)](06-staging-table-csv-import.md) | The load that puts rows into `x_bst_startuptrk_ingest_staging`, which step 4 reads. |
| [`05-atf-test-suites.md` (planned)](05-atf-test-suites.md) | The Automated Test Framework test that exercises this flow, and the `fallback validated` / `live validated` result label. |
| [`../manual-build-instructions.md` (planned)](../manual-build-instructions.md) | The split rule for the package as a whole: which artifacts ship as Update Set XML and which are built by hand. |
| [`../data-model.md`](../data-model.md) | The Founder and Executive column sets with their two **different** `title` choice lists, JobPosting's three choice lists, the cascade rules, and the staging table's forty columns. |
| [`../access-control.md`](../access-control.md) | The role and ACL posture of the tables this flow writes, including the two `contact_email` premium fields they carry. |
| [`../validation-checklist.md` (planned)](../validation-checklist.md) | Success criterion 4, which reads the run-summary surface step 8 writes. |
| [`../validation-gates.md`](../validation-gates.md) | The sixteen post-commit gates of precondition 4, and the eleven-gate core of precondition 5. |
| [`../deployment-runbook.md`](../deployment-runbook.md) | The definition of a scheduled run, under [What counts as a scheduled run](../deployment-runbook.md#what-counts-as-a-scheduled-run). |
| [`../gaps-and-flags.md` (planned)](../gaps-and-flags.md) | The requirements with no clean platform equivalent, including the runtime-configurable schedule interval. |
| [`../../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml`](../../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml) | **Authoritative** for every identifier this guide cites. |
| [`../../sample-data/README.md`](../../sample-data/README.md) | The column contract of the fallback dataset step 4 reads, and the three LinkedIn files that carry it. |
| [`../../../docs/decisions/DECISION_LOG.md` (planned)](../../../docs/decisions/DECISION_LOG.md) | The single destination for every "why". |

## Position in the build order

This is **guide 03 of six**, and it is **step 3** of the execution order below. It runs immediately after guide 02, because this flow binds guide 01's second alias **by name** and resolves its parent Startup references against records guide 02's flow writes. The order is stated in full in [`../manual-build-instructions.md` (planned)](../manual-build-instructions.md); it is repeated here so this guide can be run without it. The execution order is not the filename order: guide **06** runs before guide **05**.

| Step | Guide | Why it sits here |
| --- | --- | --- |
| 1 | [`01-connection-credential-aliases.md`](01-connection-credential-aliases.md) | The two Connection & Credential Aliases the ingestion flows bind to by name. Nothing downstream can authenticate without them. |
| 2 | [`02-flow-crunchbase-ingestion.md`](02-flow-crunchbase-ingestion.md) | The Crunchbase ingestion flow, which references `x_bst_startuptrk.crunchbase_api` by name. **Build it before this guide**, because it owns the Startup upsert path this flow shares. |
| **3** | **This guide** | **The LinkedIn ingestion flow, which references `x_bst_startuptrk.linkedin_oauth` by name. The identical skeleton.** |
| 4 | [`04-service-portal-pages-and-widgets.md`](04-service-portal-pages-and-widgets.md) | The portal, theme, five pages and eight widgets. |
| 5 | [`06-staging-table-csv-import.md` (planned)](06-staging-table-csv-import.md) | The staging-table CSV load. |
| 6 | [`05-atf-test-suites.md` (planned)](05-atf-test-suites.md) | The Automated Test Framework suites, **last**, because they exercise everything the five preceding guides build. |

Guide **02** precedes this one and is built from the same skeleton. A reader comparing the two guides must find **no discrepancy** in steps 1, 2, 4, 5, 7 and 8, which means:

- **Steps 1, 2, 7 and 8 are identical**, word for word in substance. The cadence guard, the source-mode resolution, the log-skip-continue contract and the run summary carry the same mechanics, the same properties and the same log events in both guides.
- **Steps 4 and 5 are identical in semantics**, with the source-system token substituted: this guide filters the staging table on `linkedin` rather than `crunchbase` and passes that token to the mapper, and the per-source translation table of pass one is the LinkedIn one. The three fallback triggers, the staging query shape, the four cleaning rules and the no-`Other` behaviour do not differ at all.
- **Only steps 3 and 6 differ substantively**: step 3 names a different alias and base URL and calls different resources, and step 6 writes `x_bst_startuptrk_founder`, `x_bst_startuptrk_executive` and `x_bst_startuptrk_jobposting` instead of guide 02's four tables.

Each of the eight steps is stated here in full rather than deferred to guide 02. Every step, every table, every cleaning rule, every property and every log write appears in both guides, so either guide alone is buildable and the traceability matrix in [`../../../docs/decisions/DECISION_LOG.md` (planned)](../../../docs/decisions/DECISION_LOG.md) has no gap at this flow.

The staging load of step 5 in the order above sits **after** this guide, which means the fallback branch of [Step 4](#step-4--fall-back-to-the-staging-table) will find no rows until guide 06 has run. That is expected. Build the flow now and re-run the fallback branch after guide 06.

## Preconditions

Do not begin this guide until every item below holds.

| # | Precondition | How to confirm |
| --- | --- | --- |
| 1 | The Update Set has been uploaded and has reached the `loaded` state. | The `sys_remote_update_set` record shows `state` `loaded`. |
| 2 | The preview has completed with an **empty error-type problem set**. | A read of `sys_update_preview_problem` filtered to this remote update set and `type=error` returns an empty `result` array. Warnings are logged and do not block. |
| 3 | The Update Set has **committed**. | The `sys_remote_update_set` record shows `state` `committed`. |
| 4 | **All sixteen post-commit gates have passed.** | Run every gate in [`../validation-gates.md`](../validation-gates.md) and record `pass` for all sixteen in that document's evidence record. The aggregate pass condition is 16 of 16; there is no partial pass. |
| 5 | The **eleven-gate core** within those sixteen has passed. | The seven entity-table gates `GATE-TBL-01` through `GATE-TBL-07`, the three role-record gates `GATE-ROLE-01` through `GATE-ROLE-03`, and the one scope-record gate `GATE-SCOPE-01`. The remaining five are `GATE-COL-01` and `GATE-SEC-01` through `GATE-SEC-04`. |
| 6 | **Guide 01 is complete and both aliases tested green.** | Both rows of the propagation table in [`01-connection-credential-aliases.md`](01-connection-credential-aliases.md#step-4--propagate-both-alias-names-into-guides-02-and-03) read `yes`, and the connection test of [Step 3 — Test both connections](01-connection-credential-aliases.md#step-3--test-both-connections) has passed for **both** aliases. Do not save this flow before that test has passed; see [Operational warnings](#operational-warnings). |
| 7 | **Guide 02 is complete and its flow is activated.** | The `Crunchbase Ingestion` flow exists and is active, per the build verification of [`02-flow-crunchbase-ingestion.md`](02-flow-crunchbase-ingestion.md#build-verification). This flow resolves its parent Startup references against records that flow writes; without them, every person and job row is rejected with `no startup carries the name`. See [6.2](#62--the-shared-startup-upsert-path). |
| 8 | The three Script Includes this flow calls into are on the instance. | `sys_script_include` carries `AppProperties`, `IngestionMapper` and `IngestionLogger`, all in the `x_bst_startuptrk` scope. |
| 9 | The four scoped system properties this flow reads or writes are on the instance. | `sys_properties` carries `x_bst_startuptrk.ingestion.cadence_hours`, `x_bst_startuptrk.ingestion.source_mode`, `x_bst_startuptrk.ingestion.last_run_provenance` and `x_bst_startuptrk.linkedin.base_url`. |
| 10 | The three tables this flow writes are on the instance, and the one it reads references against. | `x_bst_startuptrk_founder`, `x_bst_startuptrk_executive` and `x_bst_startuptrk_jobposting` all open in the list view, as does `x_bst_startuptrk_startup`. Gates `GATE-TBL-02`, `GATE-TBL-03`, `GATE-TBL-06` and `GATE-TBL-01` cover all four. |
| 11 | The staging table this flow reads on the fallback branch is on the instance. | `x_bst_startuptrk_ingest_staging` opens in the list view. It ships with `ws_access` **false**, so confirm it in the list view and not over the Table API. |
| 12 | The business rule that maintains the Startup trim-and-validate contract is on the instance and **active**. | `sys_script` carries `Trim and validate startup`, `active` true, in the `x_bst_startuptrk` scope. This flow writes no Startup record, so the two portfolio-count rules do not fire on its writes; they remain active for guide 02. |
| 13 | You are working in the `x_bst_startuptrk` application scope. | The application picker reads **Boston Startup Tracker**. Every record this guide creates must carry that scope. |
| 14 | You hold a role that can create and publish a flow. | You can open Flow Designer, create a flow in the `x_bst_startuptrk` scope, and see the **Activate** control on a saved flow. |
| 15 | You have access to the **System OAuth** module. | The **System OAuth** application appears in the navigator with its **Application Registry** and **Manage Tokens** modules, so the token state behind this flow's alias can be read when a run resolves to `fallback`. Both modules require the `oauth_admin` role, which `admin` contains. |

### Why this guide exists rather than more Update Set XML

Only tables carrying the update-synch attribute are captured into `sys_update_xml` records, and adding that attribute to a table that lacks it out of the box is unsupported. The Flow Designer tables are outside the captured set, so this flow is built through the platform interface instead — which is why the delivered Update Set contains **zero** flow records. [`../manual-build-instructions.md` (planned)](../manual-build-instructions.md) owns the split rule for the package as a whole.

## Platform constraint

**IntegrationHub spokes are forbidden.** Prompt section 4.0 binds this absolutely. Do **not** install, activate, reference or open any spoke content set, and do not use a spoke action anywhere in this flow. A generic REST step is not a spoke. This flow uses a generic REST step bound to the alias established in guide 01, or the scoped script step of [Step 3c](#3c--the-alternate-path-a-scoped-script-step) where that step is unavailable.

**No credential material appears anywhere in this flow.** Not in the flow record, not in a flow input, not in a step input, not in a script step, not in a test payload, and not in the Update Set. The alias is referenced by name and the platform resolves the secret at run time. Guide 01 holds the credential records; this guide never reads their values and never prints them. LinkedIn's secret material is an OAuth 2.0 client identifier, a client secret and a refresh token, and **no access token is ever held by, returned from or logged by this flow** — see [3d](#3d--oauth-20-token-handling-belongs-to-the-credential-record).

## What this guide builds

One record, containing eight steps.

| Artifact | Count | Table | Notes |
| --- | --- | --- | --- |
| Scheduled flow | 1 | `sys_hub_flow` | Built in Flow Designer, in the `x_bst_startuptrk` scope. |
| Flow trigger | 1 | Scheduled, **repeat hourly** | See [The trigger](#the-trigger). The hourly repeat is deliberate and is paired with the guard of step 1. |
| Flow steps | 8 | — | Numbered 1 to 8 below. Steps 2 through 8 sit inside one `If` block controlled by step 1. |

The flow reads **four** system properties, writes **one**, reads **one** staging table, reads **one** entity table for reference resolution, writes **three** entity tables, calls **three** Script Includes, and emits **fifteen** distinct kinds of log record — nine through `IngestionLogger` and six of its own step lines. Each is enumerated in its own step, and the log records are inventoried together in [7.2](#72--every-log-record-this-flow-can-write).

## The flow record

Create the flow first, with no steps, then add the steps in order.

1. Set the application picker to **Boston Startup Tracker**.
2. Open **Flow Designer**, then **New**, then **Flow**.
3. Set the fields below.

| Field | Value | Notes |
| --- | --- | --- |
| **Flow name** | `LinkedIn Ingestion` | The internal name derives from this. Guide 02 uses `Crunchbase Ingestion`. |
| **Application** | `Boston Startup Tracker` | The `x_bst_startuptrk` scope. Confirm this before saving; a flow created in Global cannot be moved into the scope afterwards. |
| **Description** | `Ingests LinkedIn people and job-posting data into x_bst_startuptrk_founder, x_bst_startuptrk_executive and x_bst_startuptrk_jobposting on the configured cadence. Implements prompt section 4.0 scheduled ingestion.` | The description convention across this package is a **pointer**: it states what the artifact does and which requirement it implements. It never states why. |
| **Run As** | **System User** | A scheduled flow has no initiating user. This setting also governs whether the alias resolves; see [Operational warnings](#operational-warnings). |
| **Protection** | `None` | |
| **Run With Roles** | leave empty | The flow must not acquire roles beyond its run-as identity. |

4. Save the flow. Do not activate it yet — activation is [its own step](#activation), after all eight steps are built and one manual run has passed.

### The run identifier

Every step of this flow carries a **run identifier**, minted once by step 1 and passed as a data pill into steps 4, 5, 6, 7 and 8. Its format is the source-system token, a hyphen, then a fourteen-digit timestamp:

```text
linkedin-20260807143000
```

Guide 02 mints `crunchbase-<yyyyMMddHHmmss>` by the same rule. The token prefix is not decorative: step 1's guard and step 8's run summary are both keyed on it, which is what keeps the two flows' cadences independent of one another. Do not shorten it, do not omit the prefix, and do not reuse an identifier across executions.

## Step 1 — Cadence guard

**Step type:** Script (Utilities → Script), followed by one `If` flow-logic block.

This is the **first action after the trigger** and it runs on every execution, including the many that do no work. It decides whether this execution is a scheduled run or a no-op.

### 1.1 — What the guard compares

The guard compares the **elapsed time since the last run summary this flow wrote** against the cadence, in hours.

The cadence is the scoped property `x_bst_startuptrk.ingestion.cadence_hours`. Its shipped value is **24**. It is **clamped to the range 6 to 48**. The clamp is owned by the `AppProperties` Script Include, which exposes it as `AppProperties.getCadenceHours()`. **Do not re-implement the clamp in the flow.** Read the value through that method and use whatever it returns: a stored value below 6 returns 6, a stored value above 48 returns 48, and a stored value that is absent or not an integer returns the default of 24. Changing the cadence at run time is done by editing that one property and nothing else — no flow edit, no re-publish.

The last-run marker is the most recent `run_summary` log record whose run identifier begins `linkedin-`. Step 8 writes that record on every execution that passes this guard and completes. A no-op writes none, so consecutive no-ops never move the marker forward.

### 1.2 — Step inputs

None. The guard takes no data pill; it reads properties and the log.

### 1.3 — Step outputs

Declare four output variables on the step.

| Output variable | Type | Meaning |
| --- | --- | --- |
| `run_id` | String | The run identifier for this execution, in the format given above. Consumed by steps 4, 5, 6, 7 and 8. |
| `cadence_hours` | Integer | The clamped cadence, as returned by `AppProperties.getCadenceHours()`. Recorded in the log line so the operator can see which value was in force. |
| `hours_elapsed` | Integer | Whole hours since the last run summary. `-1` when no marker is on record. |
| `proceed` | True/False | `true` when this execution is a scheduled run. `false` when it is a no-op. |

### 1.4 — The guard script

Set the script body to the following. It calls `AppProperties` by bare class name, which is correct inside the `x_bst_startuptrk` scope; the fully qualified form is `x_bst_startuptrk.AppProperties`.

```javascript
(function execute(inputs, outputs) {

    var props = new AppProperties();
    var cadence = props.getCadenceHours();          // clamped 6..48, default 24

    var stamp = new GlideDateTime();
    outputs.run_id = 'linkedin-' + stamp.getValue()
        .replace(/[^0-9]/g, '').substring(0, 14);
    outputs.cadence_hours = cadence;

    // Most recent run summary this flow wrote, identified by the run-id prefix.
    var marker = new GlideRecord('syslog');
    marker.addQuery('source', 'x_bst_startuptrk');
    marker.addQuery('message', 'CONTAINS', 'event="run_summary"');
    marker.addQuery('message', 'CONTAINS', 'run="linkedin-');
    marker.orderByDesc('sys_created_on');
    marker.setLimit(1);
    marker.query();

    if (!marker.next()) {
        // No marker on record: first execution, or the log has been pruned.
        outputs.hours_elapsed = -1;
        outputs.proceed = true;
        gs.info('[x_bst_startuptrk.ingestion] event="cadence_guard" run="' +
            outputs.run_id + '" cadence_hours="' + cadence +
            '" hours_elapsed="none" outcome="proceed"');
        return;
    }

    var last = new GlideDateTime(marker.getValue('sys_created_on'));
    var elapsedMs = new GlideDateTime().getNumericValue() - last.getNumericValue();
    var whole = Math.floor(elapsedMs / 3600000);

    outputs.hours_elapsed = whole;
    outputs.proceed = (whole >= cadence);

    gs.info('[x_bst_startuptrk.ingestion] event="cadence_guard" run="' +
        outputs.run_id + '" cadence_hours="' + cadence +
        '" hours_elapsed="' + whole + '" outcome="' +
        (outputs.proceed ? 'proceed' : 'no_op') + '"');

})(inputs, outputs);
```

### 1.5 — The early exit

Add one **`If`** flow-logic block immediately after the guard. Set its condition to the guard's `proceed` output **is** `true`. **Steps 2 through 8 all sit inside that block.**

When `proceed` is `false` the flow reaches its end having done no work: it makes no outbound call, reads no staging row, writes no entity record and writes no run summary. That is the intended behaviour and it is not an error.

### 1.6 — Why the trigger repeats hourly

A Flow Designer scheduled trigger takes a fixed interval and **cannot read a system property at run time**. The trigger is therefore set to repeat **hourly**, and this guard supplies the configurable cadence. The mechanic is stated here; the decision is recorded in [`../../../docs/decisions/DECISION_LOG.md` (planned)](../../../docs/decisions/DECISION_LOG.md), and the requirement is listed as having no clean platform equivalent in [`../gaps-and-flags.md` (planned)](../gaps-and-flags.md).

### 1.7 — What a scheduled run is

This definition is hard, and the acceptance evidence depends on it.

> A **scheduled run** is a flow execution that passed this guard and went on to do work. An execution that started, found the configured cadence had not yet elapsed and exited without ingesting is a **no-op**: it is not a scheduled run, it does not count towards the three consecutive runs, and it is not evidence of anything.

With the shipped cadence of 24 hours and an hourly trigger, roughly twenty-three of every twenty-four executions are no-ops. Those executions **must never appear** in the acceptance evidence for criterion 4 in [`../validation-checklist.md` (planned)](../validation-checklist.md). Collect evidence only from executions that passed this guard. The same definition is stated in [`../deployment-runbook.md`](../deployment-runbook.md#what-counts-as-a-scheduled-run) and in [`../../sample-data/README.md`](../../sample-data/README.md), and how to tell the two apart in the log is under [Reading the flow execution log](#reading-the-flow-execution-log).

## Step 2 — Resolve the source mode

**Step type:** Script (Utilities → Script).

### 2.1 — What it reads

One property: `x_bst_startuptrk.ingestion.source_mode`. It is a choice-list property whose only valid values are `live` and `fallback`, and its shipped value is **`live`**. Read it through `AppProperties.getSourceMode()`, which returns `live` for any value it does not recognise.

### 2.2 — Step inputs

| Input | Value |
| --- | --- |
| `run_id` | Data pill: **Step 1 → run_id**. |

### 2.3 — Step outputs

| Output variable | Type | Meaning |
| --- | --- | --- |
| `source_mode` | String | `live` or `fallback`. |
| `attempt_live` | True/False | `true` when `source_mode` is `live`. Controls the `If` block around step 3. |

### 2.4 — The step script

```javascript
(function execute(inputs, outputs) {

    var mode = new AppProperties().getSourceMode();   // 'live' | 'fallback'

    outputs.source_mode = mode;
    outputs.attempt_live = (mode === 'live');

    gs.info('[x_bst_startuptrk.ingestion] event="source_mode" run="' +
        inputs.run_id + '" mode="' + mode + '"');

})(inputs, outputs);
```

### 2.5 — What each value does

| Value | Behaviour |
| --- | --- |
| `live` | **The default, and what every real run attempts first.** The flow proceeds to step 3 and calls LinkedIn through the alias. If that call fails in one of the three ways listed in [Step 4](#step-4--fall-back-to-the-staging-table), the flow falls back to the staging table for that run. |
| `fallback` | The flow **skips the live attempt altogether** and goes straight to the staging read of step 4. Set this value to make a test deterministic without touching a credential. Set it back to `live` afterwards. |

Setting the property to `fallback` is the procedure [`../../sample-data/README.md`](../../sample-data/README.md) refers to as forcing the fallback path, and it is how the flow test in [`05-atf-test-suites.md` (planned)](05-atf-test-suites.md) reaches a repeatable result. The difference between the two values is only whether the live call is attempted: a run left on `live` also reads the staging dataset whenever the live call fails.

Wrap step 3 in an **`If`** block whose condition is step 2's `attempt_live` output **is** `true`. Steps 4 through 8 sit outside that inner block and run on both paths.

## Step 3 — Call LinkedIn through the alias

**Step type:** either a REST step or a Script step. **Which one you build is decided by the pre-flight check in [Step 3b](#3b--the-pre-flight-check-that-chooses-the-path), and you build exactly one of them.** This is a real deployment-time branch that depends on what the instance offers, not a hypothesis. Do not build both.

Both paths are identical in three respects that matter: each **references the alias `x_bst_startuptrk.linkedin_oauth` by name**, neither uses an IntegrationHub spoke, and neither puts a key, secret, token or password into the flow, a step input, a script body or the Update Set.

### 3a — The primary path: the Flow Designer REST step

Add the **REST** step from the **Integration** category and set the fields below.

| Field | Value | Notes |
| --- | --- | --- |
| **Connection type** | **Use Connection Alias** | Not an inline connection. An inline connection would require the endpoint and credential to be typed into the step, which this build forbids. |
| **Connection Alias** | `x_bst_startuptrk.linkedin_oauth` | **Copy this value from guide 01; never retype it.** Watch the two separators: a dot after the scope and an underscore inside the alias name. |
| **Base URL** | resolved from the alias | The alias's connection record already carries the base URL, which is the value of the property `x_bst_startuptrk.linkedin.base_url`. Leave the step's own base URL empty so the alias supplies it. |
| **HTTP method** | `GET` | All three calls are reads. |
| **Resource path** | one of the three shapes in [3a.2](#3a2--the-resources-called) | Set per call. |
| **Query parameters** | only those named in [3a.2](#3a2--the-resources-called) | **No credential travels as a query parameter.** The alias supplies the credential; see [Legacy provenance](#legacy-provenance) for what this replaces. |
| **Request headers** | `Accept: application/json` | **Do not add an `Authorization` header.** The alias and its OAuth 2.0 credential supply authentication; a hand-assembled header is the legacy anti-pattern this build removes. |
| **Request body** | empty | |
| **Connection timeout / Retry policy** | leave at the step defaults | A timeout is one of the three fallback triggers in step 4. |

#### 3a.1 — Step inputs

| Input | Value |
| --- | --- |
| `run_id` | Data pill: **Step 1 → run_id**. Carried through so the log lines correlate. |

#### 3a.2 — The resources called

Three resource-path shapes, three call sites. All are relative to the base URL the alias supplies. The **declared record type** column is the value the flow stamps on the rows it assembles from that call's response, and it is what [6.3](#63--the-record_type-discriminator) turns into a target table.

| # | Resource path | Purpose | Declared record type | Response shape |
| --- | --- | --- | --- | --- |
| 1 | `/companies?q=name&name={company_name}` | Company lookup. Resolves the company identifier the next two calls need. | **none** | An **array** under **`data.elements`**. |
| 2 | `/companies/{company_id}/employees` | The people associated with one company. Run **twice**, once per person record type; see [3a.3](#3a3--the-two-employee-passes). | `founder` on one pass, `executive` on the other | An **array** under **`data.elements`**. |
| 3 | `/companies/{company_id}/jobs` | The job postings of one company. | `job_posting` | An **array** under **`data.elements`**. |

The `elements` array is the LinkedIn response vocabulary, and it is the same `data.elements` envelope the fallback CSVs carry in their `raw_payload` column — the two paths therefore feed the mapper the same shape. [`../../sample-data/README.md`](../../sample-data/README.md) is authoritative for that envelope.

`IngestionMapper.unwrapLive()` handles the shape and needs no help from the flow: it unwraps `data` when present and returns the array it finds under `elements`, so a response that places `elements` at the root unwraps identically. Pass the response body to it whole. Do not pre-parse, pre-flatten or re-key it in the flow.

Call 1 writes **no entity record**. Its result is used for two things only: the company identifier that parameterises calls 2 and 3, and the company name that each assembled row carries as its `startup` natural key. The name is what [6.2](#62--the-shared-startup-upsert-path) resolves against an existing Startup.

#### 3a.3 — The two employee passes

Resource 2 is called **once per person record type**, and each pass declares its own record type on the rows it assembles. Narrow each request to the population it declares, using the resource's own people filter, so the same person is not assembled twice.

| Pass | Declared record type | Rows become | Request narrowing |
| --- | --- | --- | --- |
| A | `founder` | `x_bst_startuptrk_founder` records | Narrow the request to the founder population. |
| B | `executive` | `x_bst_startuptrk_executive` records | Narrow the request to the executive population. |

**The declaration is the flow's, never the payload's.** A person's `title` value plays no part in choosing the pass or the table; see [6.3](#63--the-record_type-discriminator). Confirm after the manual run that no person appears on both tables — that check is row 12 of [Build verification](#build-verification).

#### 3a.4 — Step outputs

The REST step exposes **Response Body**, **Status Code**, **Response Headers** and **Error message**. Step 4 consumes the first three.

| Output | Consumed by |
| --- | --- |
| **Status Code** | Step 4's authentication-failure and error-status test. |
| **Response Body** | Step 4's malformed-response test, then step 5 by way of `IngestionMapper.unwrapLive()`. |
| **Error message** | Step 4's timeout test, and the log line step 4 writes. |

Assemble the three call sites' responses into **one** array of envelopes, each carrying its declared record type, and hand that array to step 4:

```javascript
// One envelope per call site. record_type is declared here and nowhere else.
var envelopes = [
    { record_type: 'founder',     payload: founderPassResponseBody },
    { record_type: 'executive',   payload: executivePassResponseBody },
    { record_type: 'job_posting', payload: jobPostingsResponseBody }
];
```

Each `payload` is the **Response Body** of its call: `founderPassResponseBody` is pass A of resource 2, `executivePassResponseBody` is pass B of resource 2, and `jobPostingsResponseBody` is resource 3. Resource 1 contributes no envelope, because the company lookup writes no entity record. Pass the array to step 4 as its `envelopes` input, serialised with `JSON.stringify`.

`IngestionMapper.expandRows()` expands each envelope into one row per element of its `data.elements` array, and **every expanded row inherits its envelope's declared `record_type`**. It then orders the whole batch by record type so a referenced record is written before its referrer. Do not omit `record_type` from an envelope: a row that carries none is rejected by `IngestionMapper.prepareOne()` before any value is read.

### 3b — The pre-flight check that chooses the path

Run this check **before** adding any step, and record the answer.

1. Open Flow Designer in the `x_bst_startuptrk` scope, create a scratch flow, and attempt to add the **REST** step from the **Integration** category.
2. If the step is offered **and** its **Connection Alias** field populates with `x_bst_startuptrk.linkedin_oauth` when you search for it, the instance supports the primary path. Delete the scratch flow and build **[3a](#3a--the-primary-path-the-flow-designer-rest-step)**.
3. If the step is not offered, or it is offered but the **Connection Alias** dropdown does not populate, the instance does not support the primary path. Delete the scratch flow and build **[3c](#3c--the-alternate-path-a-scoped-script-step)**.

Record the outcome in the completion criteria at the end of this guide, because the flow test in [`05-atf-test-suites.md` (planned)](05-atf-test-suites.md) needs to know which step type it is asserting against. The mechanic of the branch is stated here; the decision is recorded in [`../../../docs/decisions/DECISION_LOG.md` (planned)](../../../docs/decisions/DECISION_LOG.md).

### 3c — The alternate path: a scoped script step

**Step type:** Script (Utilities → Script).

This path resolves the connection and the credential **at run time, by alias name**, and executes the call through the scoped outbound REST message API. It references the alias by name exactly as the REST step does, it uses no spoke, and it keeps every secret out of the flow, the script body and the Update Set — the script never contains a credential value, it asks the platform for one and hands it straight to the request.

#### 3c.1 — Step inputs

| Input | Value |
| --- | --- |
| `run_id` | Data pill: **Step 1 → run_id**. |
| `resource_path` | The resource path for this call, one of the shapes in [3a.2](#3a2--the-resources-called). |

#### 3c.2 — Step outputs

Declare four output variables so this step is drop-in compatible with the REST step's outputs.

| Output variable | Type | Meaning |
| --- | --- | --- |
| `status_code` | Integer | The HTTP status. `0` when the request never completed. |
| `response_body` | String | The raw response body. Empty on failure. |
| `error_message` | String | Empty on success. |
| `live_ok` | True/False | `true` only when the call returned a 2xx status with a body. |

#### 3c.3 — The step script

```javascript
(function execute(inputs, outputs) {

    var ALIAS = 'x_bst_startuptrk.linkedin_oauth';

    outputs.status_code = 0;
    outputs.response_body = '';
    outputs.error_message = '';
    outputs.live_ok = false;

    try {
        // Resolve the connection and its credential BY ALIAS NAME.
        var info = new sn_cc.ConnectionInfoProvider().getConnectionInfo(ALIAS);
        if (!info) {
            outputs.error_message = 'connection alias did not resolve';
            return;
        }

        var request = new sn_ws.RESTMessageV2();
        request.setHttpMethod('GET');
        request.setEndpoint(info.getAttribute('connection_url') + inputs.resource_path);

        // OAuth 2.0: the profile behind the alias supplies and renews the token.
        // Nothing here reads, stores, returns or logs a token value.
        request.setAuthenticationProfile('oauth2',
            info.getCredentialAttribute('oauth_entity_profile'));

        request.setRequestHeader('Accept', 'application/json');
        request.setHttpTimeout(30000);

        var response = request.execute();
        outputs.status_code = parseInt(response.getStatusCode(), 10) || 0;

        if (response.haveError()) {
            outputs.error_message = response.getErrorMessage();
            return;
        }

        outputs.response_body = response.getBody() || '';
        outputs.live_ok = (outputs.status_code >= 200 &&
                           outputs.status_code < 300 &&
                           outputs.response_body !== '');

    } catch (e) {
        outputs.error_message = e.message;
    }

})(inputs, outputs);
```

`info.getAttribute('connection_url')` returns the base URL the alias's connection record carries, which is the value of `x_bst_startuptrk.linkedin.base_url`. The credential attribute read is the **OAuth entity profile identifier**, not a secret: it is handed straight to `setAuthenticationProfile` without being assigned to a named variable, logged, or returned as a step output. **Never add a credential attribute, an access token or a refresh token to an output variable, a log line or a flow input.**

The profile identifier is the value guide 01 confirms on the credential record's **OAuth Entity Profile** field in [Step 2.4](01-connection-credential-aliases.md#step-24--confirm-the-oauth-20-credential-record-fields). Read it from the connection info as shown. If the instance does not expose it under that attribute name, resolve it once from the credential record the connection's **Credential** field names and pass that identifier instead — the profile it points at is the same record either way, and the substitution changes nothing else in this step. Confirm the resulting call succeeds against the connection test of guide 01's [Step 3](01-connection-credential-aliases.md#step-3--test-both-connections) before saving the flow.

Where guide 02's Crunchbase script sets Basic authentication from the credential's user name and password, this script sets an OAuth 2.0 authentication profile instead. That is the only difference between the two scripts beyond the alias name, and it is the authentication-model change recorded in [Legacy provenance](#legacy-provenance).

If the alias resolves to nothing, `getConnectionInfo` returns **`null` rather than raising** — which is why the script tests for it explicitly. See [Operational warnings](#operational-warnings) for the run-as consequence of that behaviour.

### 3d — OAuth 2.0 token handling belongs to the credential record

**Token refresh is handled by the credential record, not by the flow.** The OAuth entity profile behind `x_bst_startuptrk.linkedin_oauth` exchanges the stored refresh token for a short-lived access token and renews it without operator involvement, on both the [3a](#3a--the-primary-path-the-flow-designer-rest-step) and the [3c](#3c--the-alternate-path-a-scoped-script-step) path. Guide 01 confirms those records: the provider record holds the client identifier and client secret, the entity profile pins the grant type, and the token store holds the refresh token.

Four rules follow, and all four are absolute:

1. **The flow never holds a token.** No step input, step output, flow variable or data pill carries an access token or a refresh token.
2. **The flow never logs a token.** No `gs.info`, `gs.warn`, `gs.error` or `IngestionLogger` call takes a token value as an argument. `IngestionLogger` scrubs free-text values, but the correct build does not hand it one to scrub.
3. **The flow never refreshes a token itself.** Do not add a step that calls the LinkedIn token endpoint, and do not add a step that writes `oauth_credential`.
4. **The flow never hand-assembles an `Authorization` header.** That is the legacy pattern at `src/data_collection/api_integrators/linkedin_integrator.py:L23`, repeated at `:L42` and `:L61`, and it is removed rather than carried forward.

A token that has expired and has not refreshed presents to this flow as an **authentication failure**, which trigger 1 of [4.1](#41--the-three-fallback-triggers) routes down the fallback branch. That routing is silent by design and is the subject of the second [operational warning](#operational-warnings).

## Step 4 — Fall back to the staging table

**Step type:** Script (Utilities → Script).

This step decides the run's **provenance** and produces the row set the rest of the flow works on. It runs on both paths and always produces a provenance value.

### 4.1 — The three fallback triggers

The flow falls back when the live call fails in any of these three ways, and in no other way.

| # | Trigger | How it is detected |
| --- | --- | --- |
| 1 | **Authentication failure** | The status code is `401` or `403`. Any other non-2xx status is also treated as a failed call and falls back by the same route. |
| 2 | **Timeout** | The step's error message is non-empty and the status code is `0`, meaning the request never completed. |
| 3 | **Malformed response** | The body is empty, is not parseable as JSON, or `IngestionMapper.unwrapLive()` returns an empty list from it. |

On any of the three: **log it, set the provenance marker to `fallback`, and read `x_bst_startuptrk_ingest_staging` instead of the live payload.** The run continues; a failed live call never halts the flow.

When step 2 resolved `source_mode` to `fallback`, the live attempt is skipped entirely and the provenance is `fallback` from the outset. There is no failure to log in that case.

An expired or unrefreshed OAuth 2.0 token reaches this step as trigger 1. See [3d](#3d--oauth-20-token-handling-belongs-to-the-credential-record) and the second [operational warning](#operational-warnings).

### 4.2 — Step inputs

| Input | Value |
| --- | --- |
| `run_id` | Data pill: **Step 1 → run_id**. |
| `attempt_live` | Data pill: **Step 2 → attempt_live**. |
| `status_code` | Data pill: **Step 3 → Status Code** (REST step) or **Step 3 → status_code** (script step). Leave empty when step 3 did not run. |
| `response_body` | Data pill: **Step 3 → Response Body** or **Step 3 → response_body**. |
| `error_message` | Data pill: **Step 3 → Error message** or **Step 3 → error_message**. |
| `envelopes` | The array of `{ record_type, payload }` envelopes assembled in [3a.4](#3a4--step-outputs), as JSON. Leave empty when step 3 did not run. |

### 4.3 — Step outputs

| Output variable | Type | Meaning |
| --- | --- | --- |
| `provenance` | String | `live` or `fallback`. Nothing else is valid; step 8 rejects any other value. |
| `rows` | String | The row set to ingest, as a JSON array. Empty array when there is nothing to do. |
| `row_count` | Integer | The number of rows in `rows`. |

### 4.4 — The staging query

On the fallback branch the flow reads `x_bst_startuptrk_ingest_staging` with exactly these conditions, which are the conditions the delivered `IngestionMapper.ingestStaging()` applies:

| Condition | Value | Notes |
| --- | --- | --- |
| `source_system` | `linkedin` | Lower-cased before the query is added. This is what keeps the two flows from reading each other's rows. |
| `import_state` | `pending` | Rows already `processed`, `rejected` or `error` are never re-read. |
| `import_run` | optional | Added only when the flow is given a specific import-run token. Leave it unset for a scheduled run so every pending LinkedIn row is picked up. |
| order | `orderBy('sys_id')` | Deterministic ordering, which is what makes the batch-level deduplication of step 5 reproducible. |

**`record_type` is not a query condition.** The query returns every pending LinkedIn row and the mapper **reads `record_type` off each row**. The restriction to this flow's three record types is enforced inside the mapper by its source-to-type map, which allows `founder`, `executive` and `job_posting` for `linkedin` and rejects anything else on that source. Do not add a `record_type` filter to the query.

The effective record-type set on this branch is therefore exactly three, and a row of any other type that carries `source_system` `linkedin` is rejected before any value is read:

| `record_type` on a `linkedin` row | Outcome |
| --- | --- |
| `founder` | Accepted. Becomes an `x_bst_startuptrk_founder` record. |
| `executive` | Accepted. Becomes an `x_bst_startuptrk_executive` record. |
| `job_posting` | Accepted. Becomes an `x_bst_startuptrk_jobposting` record. |
| `startup`, `investor` or `funding_round` | **Rejected** by `IngestionMapper.prepareOne()` with the reason `linkedin does not supply record type <type>`, logged by `IngestionLogger.rejectRecord()`. Those three belong to [`02-flow-crunchbase-ingestion.md`](02-flow-crunchbase-ingestion.md). |
| blank or unrecognised | **Rejected** by the same route and reason. |

The staging table ships with `ws_access` **false**. Read it with `GlideRecord` from the script step, and inspect it by eye in the **list view** — not over the Table API.

**[`06-staging-table-csv-import.md` (planned)](06-staging-table-csv-import.md) must have loaded that table for this branch to yield rows.** Until it has run, the fallback branch completes correctly with a row count of zero. The column contract of the loaded rows is in [`../../sample-data/README.md`](../../sample-data/README.md); the three files that carry this flow's rows are `linkedin_founders_sample.csv`, `linkedin_executives_sample.csv` and `linkedin_job_postings_sample.csv`.

### 4.5 — The step script

```javascript
(function execute(inputs, outputs) {

    var logger = new IngestionLogger();
    var mapper = new IngestionMapper();
    mapper.useLogger(logger);

    var rows = [];
    var provenance = 'fallback';
    var reason = '';

    if (inputs.attempt_live === true || inputs.attempt_live === 'true') {

        var status = parseInt(inputs.status_code, 10) || 0;
        var body = inputs.response_body || '';

        if (status === 401 || status === 403) {
            reason = 'authentication failure, status ' + status;
        } else if (status === 0 && inputs.error_message) {
            reason = 'timeout or transport failure';
        } else if (status < 200 || status >= 300) {
            reason = 'unexpected status ' + status;
        } else {
            try {
                // Each envelope carries the record type declared in 3a.4. The mapper
                // expands data.elements into one row per element, and every row
                // inherits its envelope's declared record type.
                var envelopes = JSON.parse(inputs.envelopes || '[]');
                var live = [];
                var e = 0;
                for (e = 0; e !== envelopes.length; e++) {
                    var elements = mapper.unwrapLive('linkedin', envelopes[e].payload);
                    var k = 0;
                    for (k = 0; k !== elements.length; k++) {
                        live.push({
                            record_type: envelopes[e].record_type,
                            source: elements[k]
                        });
                    }
                }
                if (!live.length) {
                    reason = 'malformed response, no records found';
                } else {
                    rows = live;
                    provenance = 'live';
                }
            } catch (e2) {
                reason = 'malformed response, body is not JSON';
            }
        }

        if (reason) {
            logger.warn(inputs.run_id,
                'live LinkedIn call failed, falling back to the staging table: ' + reason);
        }
    }

    if (provenance === 'fallback') {
        var staging = new GlideRecord('x_bst_startuptrk_ingest_staging');
        staging.addQuery('source_system', 'linkedin');
        staging.addQuery('import_state', 'pending');
        staging.orderBy('sys_id');
        staging.query();
        while (staging.next()) {
            rows.push(mapper.mapStagingRow(inputs.run_id, staging));
        }
    }

    outputs.provenance = provenance;
    outputs.rows = JSON.stringify(rows);
    outputs.row_count = rows.length;

    gs.info('[x_bst_startuptrk.ingestion] event="source_resolved" run="' +
        inputs.run_id + '" provenance="' + provenance +
        '" rows="' + rows.length + '"');

})(inputs, outputs);
```

## Step 5 — Clean every record through `IngestionMapper`

**Step type:** Script (Utilities → Script).

Every record, on both the live and the fallback path, passes through the `IngestionMapper` Script Include. The four cleaning rules live there and **nowhere else**, which is what keeps this flow and the Crunchbase flow from diverging. Do not re-implement any rule in the flow.

### 5.1 — Step inputs

| Input | Value |
| --- | --- |
| `run_id` | Data pill: **Step 1 → run_id**. |
| `rows` | Data pill: **Step 4 → rows**. |

### 5.2 — Step outputs

| Output variable | Type | Meaning |
| --- | --- | --- |
| `cleaned` | String | The accepted records, as a JSON array, each carrying its record type and its resolved values. |
| `accepted_count` | Integer | Records that passed all four rules. |
| `rejected_count` | Integer | Records rejected by rule 4 or by a refused or over-length value. |
| `duplicate_count` | Integer | Records rejected by rule 2 as a within-batch duplicate. |

### 5.3 — The four cleaning rules

These are applied in the order below, which is the order the delivered `IngestionMapper.clean()` and the batch pass in the orchestrator apply them.

**Rule 1 — trim whitespace on all string fields.** `IngestionMapper.trimStrings()` applies `trim()` to every string-typed value on the record before anything else looks at it.

**Rule 2 — deduplicate incoming Startup records on `name` + `headquarters_location`, case-insensitively.** `IngestionMapper.startupKey()` forms the key as the lower-cased name, a pipe, then the lower-cased headquarters location. `IngestionMapper.dedupeBatch()` applies it at **batch scope**, after each record has been prepared and before any reference is resolved: the first occurrence of a key is accepted, and every later occurrence in the same batch is rejected with the reason `duplicate startup in the same batch` and logged by `IngestionLogger.duplicateRecord()`. The rule applies to the `startup` record type only.

This is the **shared deduplication key**. This flow ingests no `startup` record type, so rule 2 rejects nothing here — but the key is the same one this flow resolves company identity through in [6.2](#62--the-shared-startup-upsert-path), which is what lets a founder ingested from LinkedIn attach to a startup ingested from Crunchbase.

**Rule 3 — normalise `funding_stage` and `round_type` to the enumerated choice values, mapping unmatched values to `Other` and logging them.** This is two passes in sequence, and both live in the mapper.

*Pass one, source-vocabulary translation.* A live LinkedIn payload states its values in LinkedIn's own code vocabulary — `eng`, `mid_senior_level`, `on_site`, `listed` — not in the target choice values. `IngestionMapper` carries a translation table per source system and field, keyed on the lower-cased source code, and applies it **first**. A known code becomes its target value. An unknown code passes through untouched to pass two. A code known to have no target member at all resolves to nothing and is logged as a recognised source code with no target member, left unwritten. The LinkedIn side of that table covers `title` from the spelled-out officer and founder titles for both person record types, `department` from the job-function codes, `remote_type` from the workplace-type codes, `seniority` from the experience-level codes, and `active` from the job-state codes.

*Pass two, `IngestionMapper.normaliseChoice()`.* An exact match against the choice list is stored as supplied. A case-insensitive match is stored with the choice list's **own** spelling. A value that matches nothing is stored as `Other` **where the list declares an `Other` member**, and where the list declares none the field is **left unwritten**. Either way `IngestionLogger.unmatchedChoice()` records a `choice_unmatched` event naming the column, the supplied value and which outcome applied.

"Left unwritten" is precise and is not the same as "emptied": the mapper removes the field from the record it is about to write, so on an **insert** the column is simply empty, while on an **update** whatever the column already stores survives untouched.

**No value outside a column's choice list is ever stored.** The complete outcome table for the choice columns this flow writes is in [5.4](#54--the-no-other-asymmetry).

**Rule 4 — reject records missing mandatory fields rather than inserting partial rows.** `IngestionMapper.missingMandatory()` checks the record type's mandatory set and, when anything is absent, rejects the whole record with the reason `missing mandatory` followed by the field names, logged by `IngestionLogger.rejectRecord()`. Nothing partial is ever inserted. The mandatory sets for this flow's three record types are:

| Record type | Mandatory fields |
| --- | --- |
| `founder` | `name`, `startup` |
| `executive` | `name`, `startup` |
| `job_posting` | `startup`, `title` |

Two further refusals sit alongside rule 4 in the same pass and reject by the same route: a value that does not match its declared type on a **mandatory** column is refused rather than repaired, and a value longer than its column's maximum length is rejected rather than truncated.

**There is no old-to-new mapping table for the legacy enumerations, and none is to be invented.** The choice lists of this application are replacements, not translations, of the legacy ones. Pass one above translates the **source system's** vocabulary, which is a different thing entirely.

### 5.4 — The no-`Other` asymmetry

Rule 3 says unmatched values map to `Other`. That is only possible where the choice list declares an `Other` member, and **not every choice column in this application declares one.**

The columns this flow writes:

| Choice column | Declares `Other` | Outcome for an unmatched value |
| --- | --- | --- |
| `x_bst_startuptrk_founder.title` | Yes | Stored as `Other`, logged. |
| `x_bst_startuptrk_executive.title` | Yes | Stored as `Other`, logged. |
| `x_bst_startuptrk_jobposting.department` | Yes | Stored as `Other`, logged. |
| `x_bst_startuptrk_jobposting.remote_type` | **No** | **Left unwritten, logged.** |
| `x_bst_startuptrk_jobposting.seniority` | **No** | **Left unwritten, logged.** |

**Founder titles and Executive titles are two different choice lists**, and the difference is the only difference between the two tables:

| Table | `title` choice list |
| --- | --- |
| `x_bst_startuptrk_founder` | `CEO`, `CTO`, `COO`, `Co-Founder`, `Other` |
| `x_bst_startuptrk_executive` | `CFO`, `VP Engineering`, `VP Sales`, `VP Marketing`, `Head of Product`, `Other` |

Both lists carry `Other`, so an unmatched title on either table **coerces to `Other`** and is logged; it never rejects the record, because `title` is not mandatory on either table. The two lists share no member other than `Other`: `CFO` is an Executive title and not a Founder title, and `Co-Founder` is a Founder title and not an Executive title. A title valid on one table is therefore an unmatched value on the other, and normalisation happens **after** the target table has been decided by [6.3](#63--the-record_type-discriminator). Do not reuse one list for both tables and do not merge them; prompt section 1.3 requires the two tables to stay separate, and [`../data-model.md`](../data-model.md) is authoritative for both lists.

`x_bst_startuptrk_investor.type` is the asymmetry to watch across the application as a whole. An operator may expect an investor type to be coerced; it is not. Its choice list declares exactly `VC`, `Angel`, `PE`, `Corporate` and `Accelerator`, with no `Other`, so an unmatched investor type is refused, the `type` column is left unwritten, and `IngestionLogger.unmatchedChoice()` logs it. **The record itself survives and is still written** — `type` is not a mandatory column, and rejection is reserved for a record missing a mandatory field. This flow writes no Investor record, so it never exercises that column; the behaviour is stated here because the cleaning rules are one shared implementation and both guides state them identically.

**Do not add an `Other` member to any list that lacks one.** The choice records in the Update Set are exactly the values those definitions declare, and [`../data-model.md`](../data-model.md) is authoritative for all of them.

### 5.5 — The step script

```javascript
(function execute(inputs, outputs) {

    var logger = new IngestionLogger();
    logger.useRun(inputs.run_id);

    var mapper = new IngestionMapper();
    mapper.useLogger(logger);

    var incoming = JSON.parse(inputs.rows || '[]');
    var prepared = [];

    // Rules 1, 3 and 4, per record. prepareOne() always returns an entry,
    // carrying accepted, state, reason and an opaque identifier.
    for (var i = 0; i < incoming.length; i++) {
        prepared.push(mapper.prepareOne(inputs.run_id, 'linkedin', incoming[i]));
    }

    // Rule 2, at batch scope, on the startup record type only.
    mapper.dedupeBatch(inputs.run_id, prepared);

    var accepted = [];
    for (var j = 0; j < prepared.length; j++) {
        if (prepared[j].accepted) {
            accepted.push(prepared[j]);
        }
    }

    var counts = logger.counters();
    outputs.cleaned = JSON.stringify(accepted);
    outputs.accepted_count = accepted.length;
    outputs.rejected_count = counts.rejected;
    outputs.duplicate_count = counts.duplicates;

    gs.info('[x_bst_startuptrk.ingestion] event="batch_cleaned" run="' +
        inputs.run_id + '" accepted="' + accepted.length +
        '" rejected="' + counts.rejected +
        '" duplicates="' + counts.duplicates +
        '" unmatched="' + counts.unmatched + '"');

})(inputs, outputs);
```

## Step 6 — Insert or update the entity records

**Step type:** Script (Utilities → Script).

### 6.1 — The tables this flow writes

Exhaustively, this flow writes **three** tables and no others.

| # | Table | What this flow writes to it |
| --- | --- | --- |
| 1 | `x_bst_startuptrk_founder` | Founder records from the LinkedIn employees payload, on the pass that declared `founder`. |
| 2 | `x_bst_startuptrk_executive` | Executive records from the LinkedIn employees payload, on the pass that declared `executive`. |
| 3 | `x_bst_startuptrk_jobposting` | Job-posting records from the LinkedIn jobs payload. |

It **reads** a fourth table, `x_bst_startuptrk_startup`, to resolve each record's mandatory `startup` reference. **It never writes that table**; see [6.2](#62--the-shared-startup-upsert-path).

**This flow does not write `x_bst_startuptrk_newsarticle`.** Automated NewsArticle ingestion is out of scope: no flow ingests it, there is no NewsArticle sample CSV, and the staging table's `record_type` choice list contains no `news_article` member. NewsArticle records are created by manual entry or by a REST write only. The exclusion is recorded in [`../gaps-and-flags.md` (planned)](../gaps-and-flags.md).

Nor does this flow write `x_bst_startuptrk_startup`, `x_bst_startuptrk_investor`, `x_bst_startuptrk_fundinground` or `x_bst_startuptrk_m2m_round_investor`. Those four belong to [`02-flow-crunchbase-ingestion.md`](02-flow-crunchbase-ingestion.md). The split is stated here as a build mechanic; the decision is recorded in [`../../../docs/decisions/DECISION_LOG.md` (planned)](../../../docs/decisions/DECISION_LOG.md).

Two of the columns this flow writes are **premium-gated**: `x_bst_startuptrk_founder.contact_email` and `x_bst_startuptrk_executive.contact_email` each carry a field-level read access control granting `x_bst_startuptrk.admin` and `x_bst_startuptrk.premium_user` only. The flow writes them exactly as it writes any other column; the gate applies on read, not on write. [`../access-control.md`](../access-control.md) is authoritative for both.

### 6.2 — The shared Startup upsert path

**This flow shares guide 02's Startup upsert path, and it shares it by resolving against it rather than by duplicating it.** Both flows resolve company identity through the **same deduplication key** — `name` plus `headquarters_location`, case-insensitively, formed by `IngestionMapper.startupKey()` as the lower-cased name, a pipe, then the lower-cased headquarters location. That single key is what lets a founder ingested from LinkedIn attach to the startup ingested from Crunchbase.

How this flow resolves a company reference:

1. Each row arrives carrying its parent company as a **natural key** — the company name, taken from the live payload's company field or from the staging row's `startup_name` column.
2. `IngestionMapper.resolveReferences()` calls `IngestionMapper.resolveStartup(name)` for every one of this flow's three record types, because all three declare a mandatory `startup` reference.
3. `resolveStartup()` matches the name against `x_bst_startuptrk_startup.name`, **trimming and lowering both sides**, and resolves only when **exactly one** startup carries it. Trimming happens before the match, so a name with surrounding whitespace still resolves.
4. On success the resolved record identifier replaces the natural key and the row is written.

**What it does when no match exists.** It does **not** create a Startup. Every outcome is deterministic and none is approximate:

| Startups carrying the name | Outcome |
| --- | --- |
| Exactly one | **Resolved.** The `startup` reference is set to that record and the row proceeds to the write. |
| **None** | **The row is rejected**, with the reason `no startup carries the name`. `IngestionLogger.rejectRecord()` logs it, `IngestionMapper.writeStagingState()` stamps the staging row `rejected` with that reason, and the run continues to the next row. **No Startup is created and no partial record is written.** |
| **More than one** | **The row is rejected**, with the reason `the name is ambiguous across <n> startups`. **No candidate is chosen.** Logged and stamped by the same route. |
| Blank | Rejected — but cleaning rule 4 has already rejected the row for a missing mandatory `startup`, so this is the rule 4 outcome rather than a resolution failure. |

This is why precondition 7 requires guide 02's flow to have run first: a LinkedIn person or job row whose company has not yet been ingested is rejected, not queued. Re-run this flow after the Startup records exist and the row is picked up — on the fallback branch it is still `pending` only if it was never read, so re-load or re-stamp the staging row when re-running. The load order in [`../../sample-data/README.md`](../../sample-data/README.md) places the Crunchbase startups file before the three LinkedIn files for exactly this reason.

**Do not add a Startup insert to this flow.** If this flow creates its own Startup records instead of resolving against guide 02's, the two flows produce duplicate companies; that is the third [operational warning](#operational-warnings).

### 6.3 — The `record_type` discriminator

**The `record_type` value on the row decides the target table. Nothing else does.**

| `record_type` | Target table |
| --- | --- |
| `founder` | `x_bst_startuptrk_founder` |
| `executive` | `x_bst_startuptrk_executive` |
| `job_posting` | `x_bst_startuptrk_jobposting` |

`IngestionMapper.TABLES` holds that mapping, and `IngestionMapper.upsert()` reads the target table from it. Where the value comes from:

| Path | Source of `record_type` |
| --- | --- |
| Live | Declared by the flow on each envelope assembled in [3a.4](#3a4--step-outputs), one declared type per call site, with the employees resource run as the two passes of [3a.3](#3a3--the-two-employee-passes). `IngestionMapper.expandRows()` copies the envelope's declared type onto every row it expands from that envelope. |
| Fallback | Read from the staging row's `record_type` column, which the CSV load sets per file. |

**No title-substring heuristic is used.** A person's `title` value plays no part in choosing the table. It is normalised against the target table's own choice list **after** the table has been decided, under rule 3, and an unmatched title coerces to `Other` because both title lists carry that member — see [5.4](#54--the-no-other-asymmetry). A person therefore never changes table on account of what the payload calls them, and a record whose title is unrecognisable still lands on the table its declared record type named.

The consequence to check for is a **mis-declared** record type rather than a mis-read title: because the two title lists share no member other than `Other`, a person declared on the wrong pass lands on the wrong table and their title silently normalises to `Other` rather than raising anything. Row 12 of [Build verification](#build-verification) is the check.

The legacy implementation decided this by title substring, at `src/data_collection/api_integrators/linkedin_integrator.py:L119-L120`. That is named in [Legacy provenance](#legacy-provenance) as the pattern being replaced, and it is not carried forward. The replacement is recorded in [`../../../docs/decisions/DECISION_LOG.md` (planned)](../../../docs/decisions/DECISION_LOG.md).

### 6.4 — The upsert key per entity

| Entity | Lookup | Behaviour |
| --- | --- | --- |
| **Founder** | **None. Every accepted founder is inserted.** | There is no existing-record lookup for this table, so re-ingesting the same payload inserts a second record. The natural key used for log correlation is the person's name followed by the resolved startup. |
| **Executive** | **None. Every accepted executive is inserted.** | As above. |
| **JobPosting** | **None. Every accepted job posting is inserted.** | As above. The natural key used for log correlation is the posting title followed by the resolved startup. |
| **Startup** | `IngestionMapper.resolveStartup(name)`, case-insensitively, as set out in [6.2](#62--the-shared-startup-upsert-path). | Read-only for this flow. Exactly one match resolves the reference. No match or more than one match rejects the row. **No insert.** |

Because none of the three written tables has an upsert key, do not run this flow repeatedly against the same live payload or the same staging batch expecting idempotence. The staging path is protected by the `import_state` transition — a row that has been processed is no longer `pending` and is never re-read — but the live path is not.

### 6.5 — Business rules must run

**Every write this step makes must run business rules.** Use ordinary `GlideRecord` `insert()` and `update()`. **Do not call `setWorkflow(false)`, and do not disable business rules on any import path this flow uses.**

| Business rule | Table | When | Relevance to this flow |
| --- | --- | --- | --- |
| `Trim and validate startup` | `x_bst_startuptrk_startup` | Before insert and update. | Does not fire on this flow's writes, because this flow writes no Startup record. It governs the records this flow resolves against. |
| `Recalculate investor portfolio on funding round` | `x_bst_startuptrk_fundinground` | After insert, update and delete. | Does not fire on this flow's writes. |
| `Recalculate investor portfolio on round investor link` | `x_bst_startuptrk_m2m_round_investor` | After insert, update and delete. | Does not fire on this flow's writes. |

None of this flow's three tables carries a derived column, so no recalculation follows its writes. The rule remains absolute nonetheless: business rules are not suppressed on any path, because suppressing them on a shared code path is what lets `x_bst_startuptrk_investor.portfolio_count` drift for guide 02 — see that guide's operational warnings, and [`../data-model.md`](../data-model.md) for the derivation.

### 6.6 — Step inputs

| Input | Value |
| --- | --- |
| `run_id` | Data pill: **Step 1 → run_id**. |
| `cleaned` | Data pill: **Step 5 → cleaned**. |

### 6.7 — Step outputs

| Output variable | Type | Meaning |
| --- | --- | --- |
| `written_count` | Integer | Records inserted or updated. |
| `skipped_count` | Integer | Records skipped by the step-7 contract. |
| `unresolved_count` | Integer | Records rejected because their parent Startup did not resolve to exactly one record. |

### 6.8 — The step script

```javascript
(function execute(inputs, outputs) {

    var logger = new IngestionLogger();
    logger.useRun(inputs.run_id);

    var mapper = new IngestionMapper();
    mapper.useLogger(logger);

    var entries = JSON.parse(inputs.cleaned || '[]');
    var written = 0;
    var unresolved = 0;

    for (var i = 0; i < entries.length; i++) {

        var entry = entries[i];

        try {
            // Resolve the mandatory startup reference before writing. All three of
            // this flow's record types carry one. No Startup is ever created here.
            var resolved = mapper.resolveReferences(inputs.run_id,
                entry.record_type, entry.data);

            if (!resolved.ok) {
                entry.state = 'rejected';
                entry.reason = resolved.reason;
                unresolved++;
                logger.rejectRecord(inputs.run_id, entry.record_type,
                    entry.identifier, resolved.reason);
                mapper.writeStagingState(entry);
                continue;                      // step 7: skip, then continue
            }

            // The record type decides the target table. No title heuristic.
            var result = mapper.upsert(inputs.run_id, entry.record_type,
                                       resolved.data, resolved.participants);

            if (result.ok) {
                written++;
                entry.sys_id = result.sys_id;
                entry.state = 'processed';
            } else {
                entry.state = 'error';
                entry.reason = result.reason;
                logger.skipRecord(inputs.run_id, entry.record_type,
                    entry.identifier, result.reason);
            }

            mapper.writeStagingState(entry);

        } catch (e) {
            // step 7: log, skip this record, continue the run
            entry.state = 'error';
            entry.reason = e.message;
            logger.skipRecord(inputs.run_id, entry.record_type,
                entry.identifier, e.message);
        }
    }

    var counts = logger.counters();
    outputs.written_count = written;
    outputs.skipped_count = counts.skipped;
    outputs.unresolved_count = unresolved;

    gs.info('[x_bst_startuptrk.ingestion] event="batch_written" run="' +
        inputs.run_id + '" written="' + written +
        '" unresolved="' + unresolved +
        '" skipped="' + counts.skipped + '"');

})(inputs, outputs);
```

`resolved.participants` is empty for every one of this flow's three record types; it is populated only for `funding_round`, which this flow does not ingest. It is passed through so the call signature matches the one guide 02 uses and the shared implementation is called identically from both flows.

## Step 7 — Log, skip the record, continue the run

**Step type:** Script (Utilities → Script), plus the `try`/`catch` contract applied to steps 5, 6 and 8.

This is the error-handling contract of the whole flow: **log the failure, skip the affected record, continue the run.** A scheduled run is never halted by a bad record. The semantics are implemented once, in the `IngestionLogger` Script Include; the flow **calls** it and does not re-implement it.

### 7.1 — The contract every step must honour

- Each of steps 5, 6 and 8 wraps its per-record work in `try`/`catch`, exactly as shown in their scripts.
- A caught failure calls the matching `IngestionLogger` method and then **continues the loop**.
- No step re-raises. Nothing in this flow throws out of a step.
- A whole-batch failure — an unparseable `rows` payload, for instance — still reaches step 8 so the run is accounted for.

### 7.2 — Every log record this flow can write

Fifteen distinct records, and no others. **Nine** are written by `IngestionLogger` and **six** are step lines the flow writes itself. All fifteen are prefixed `[x_bst_startuptrk.ingestion]` and routed to the application log.

The nine `IngestionLogger` records, at the severity shown:

| Method called | Event name | Severity | Counter incremented |
| --- | --- | --- | --- |
| `info()` | `info` | info | — |
| `warn()` | `warning` | warn | — |
| `skipRecord()` | `record_skipped` | **error** | `skipped` |
| `rejectRecord()` | `record_rejected` | warn | `rejected` |
| `duplicateRecord()` | `record_duplicate` | warn | `duplicates` |
| `unmatchedChoice()` | `choice_unmatched` | warn | `unmatched` |
| `invalidEncoding()` | `value_undecodable` | warn | — |
| `writeRunSummary()`, valid provenance | `run_summary` | info | — |
| `writeRunSummary()`, invalid provenance | `run_summary_provenance_invalid` | **error** | — |

The six step lines the flow writes itself, all at **info** severity, one per step that produces them:

| Step | Event name | Members carried |
| --- | --- | --- |
| 1 | `cadence_guard` | `run`, `cadence_hours`, `hours_elapsed`, `outcome` — where `outcome` is `proceed` or `no_op`. |
| 2 | `source_mode` | `run`, `mode`. |
| 4 | `source_resolved` | `run`, `provenance`, `rows`. |
| 5 | `batch_cleaned` | `run`, `accepted`, `rejected`, `duplicates`, `unmatched`. |
| 6 | `batch_written` | `run`, `written`, `unresolved`, `skipped`. |
| 7 | `batch_reconciled` | `run`, `incoming`, `processed`, `rejected`, `skipped`, `duplicates`, `reconciled`. |

Every event name and every severity above is identical to [`02-flow-crunchbase-ingestion.md`](02-flow-crunchbase-ingestion.md#72--every-log-record-this-flow-can-write). One member differs, on the step-6 line only: this flow carries `unresolved` where guide 02 carries `links`, because guide 02 writes participant join rows and this flow resolves parent references. The event name, the severity and the `run` correlation key are the same on both.

Step 3 writes no line of its own; its outcome is carried by step 4's `source_resolved`, and a failed live call is recorded by `IngestionLogger.warn()`. Step 8 writes no line of its own either; its record is the `run_summary` in the table above.

`IngestionLogger` scrubs person and free-text values out of every line it writes, so a log record identifies a failing record by an opaque reference rather than by name, e-mail address or URL. That matters more on this flow than on guide 02: every row it ingests is person data or a job posting, and two of its columns are premium-gated contact addresses. **Do not add your own `gs.log` calls carrying record values** to work around that, and do not add step lines beyond the six above — the `run` member is the only correlation key any of them needs.

### 7.3 — Cleaning-rule outcomes are expected behaviour, not errors

This distinction is what makes the criterion-4 evidence readable.

- A record **rejected** by rule 4 for a missing mandatory field, **rejected** for a refused or over-length value, or **rejected** by rule 2 as a within-batch duplicate, is the cleaning rules working as specified. It increments `rejected` or `duplicates`. **It is not an unhandled error and does not count as one.**
- A record **rejected** because its parent Startup did not resolve to exactly one record is the same class of outcome. It increments `rejected` and is reported separately as `unresolved` by step 6. **It is not an unhandled error either.**
- A value **left unwritten** by rule 3 because its choice list declares no `Other` member increments `unmatched`. **It is not an error either**, and the record it belongs to is still written.
- A record **skipped** by `skipRecord()` is an operational failure — a write that would not complete. It increments `skipped` and is emitted at **error** severity.

Criterion 4 requires **zero unhandled errors** across three consecutive scheduled runs. A run whose `rejected`, `duplicates` and `unmatched` counters are non-zero while nothing escaped a `try`/`catch` still satisfies that criterion. Report the five counters separately and never fold them together.

### 7.4 — Counters accumulate on a logger instance, not globally

This is a build constraint, and it decides which construction you choose.

`IngestionLogger` holds its five counters as **instance state**. A script step that runs `new IngestionLogger()` starts from zero. Two consequences follow, and neither is a defect in the logger:

- **On the separate-step build**, each of steps 5 and 6 reports the counters of its own logger instance, and step 7 must **sum the step outputs** rather than read `counters()` from a fresh instance. That is what the script below does.
- **`writeRunSummary()` reports the counters of the instance it is called on.** On the separate-step build, step 8's instance has counted nothing, so its run summary carries zeros for `processed`, `rejected`, `skipped`, `duplicates` and `unmatched` while still carrying the correct `run` and `provenance`.

If the run summary must carry the complete counters — and it must, for the criterion-4 evidence to be readable from one record — **use the orchestrator construction of [8.6](#86--the-delivered-orchestrators)**, in which one logger instance performs the whole batch and hands its accumulated counters to `writeRunSummary()`. Build the separate steps when you want each phase's counters visible as step outputs in the execution detail, and read the totals from step 7 rather than from the run summary.

### 7.5 — Step inputs

| Input | Value |
| --- | --- |
| `run_id` | Data pill: **Step 1 → run_id**. |
| `row_count` | Data pill: **Step 4 → row_count**. |
| `accepted_count` | Data pill: **Step 5 → accepted_count**. |
| `rejected_count` | Data pill: **Step 5 → rejected_count**. |
| `duplicate_count` | Data pill: **Step 5 → duplicate_count**. |
| `written_count` | Data pill: **Step 6 → written_count**. |
| `skipped_count` | Data pill: **Step 6 → skipped_count**. |
| `unresolved_count` | Data pill: **Step 6 → unresolved_count**. |

### 7.6 — Step outputs

| Output variable | Type | Meaning |
| --- | --- | --- |
| `processed` | Integer | Records written. |
| `rejected` | Integer | Rule-4, refusal, over-length and unresolved-parent rejections. |
| `skipped` | Integer | Operational skips. |
| `duplicates` | Integer | Rule-2 within-batch duplicates. |
| `unmatched` | Integer | Rule-3 values that matched no choice member. |
| `reconciled` | True/False | `true` when every incoming row is accounted for. |

### 7.7 — The step script

This step sums the per-step counters into one set of run totals and writes a single reconciliation line, so the operator can read the outcome of one execution in one place and see that no row went missing.

```javascript
(function execute(inputs, outputs) {

    var toInt = function (v) { return parseInt(v, 10) || 0; };

    outputs.processed = toInt(inputs.written_count);
    outputs.rejected = toInt(inputs.rejected_count) + toInt(inputs.unresolved_count);
    outputs.skipped = toInt(inputs.skipped_count);
    outputs.duplicates = toInt(inputs.duplicate_count);

    // Unmatched choice values are logged per record; they never reject a record,
    // so they are reported from the accepted set rather than added to the total.
    outputs.unmatched = toInt(inputs.accepted_count) - outputs.processed -
                        toInt(inputs.unresolved_count);

    var incoming = toInt(inputs.row_count);
    var accounted = outputs.processed + outputs.rejected +
                    outputs.skipped + outputs.duplicates;

    outputs.reconciled = (accounted === incoming);

    gs.info('[x_bst_startuptrk.ingestion] event="batch_reconciled" run="' +
        inputs.run_id + '" incoming="' + incoming +
        '" processed="' + outputs.processed +
        '" rejected="' + outputs.rejected +
        '" skipped="' + outputs.skipped +
        '" duplicates="' + outputs.duplicates +
        '" reconciled="' + outputs.reconciled + '"');

})(inputs, outputs);
```

The parent-resolution rejections of [6.2](#62--the-shared-startup-upsert-path) are added into `rejected` here so the reconciliation balances, and they remain visible on their own as step 6's `unresolved_count`. Guide 02 has no equivalent term because its four record types resolve their references without a mandatory parent lookup on every row.

## Step 8 — Write the run summary and the provenance marker

**Step type:** Script (Utilities → Script).

This is the surface criterion 4 in [`../validation-checklist.md` (planned)](../validation-checklist.md) reads for each of the **three consecutive guard-passing runs** it requires. It is also the marker step 1's guard reads on the next execution. It must run on every guard-passing execution, on both the live and the fallback path.

### 8.1 — Step inputs

| Input | Value |
| --- | --- |
| `run_id` | Data pill: **Step 1 → run_id**. |
| `provenance` | Data pill: **Step 4 → provenance**. |

### 8.2 — Step outputs

| Output variable | Type | Meaning |
| --- | --- | --- |
| `recorded` | True/False | `true` when the summary was written and the property updated. |
| `provenance` | String | Echoed back as written: `live` or `fallback`. |

### 8.3 — What gets written

`IngestionLogger.writeRunSummary(run_id, provenance)` does all of it, in this order.

1. It validates the provenance against the only two valid values, `live` and `fallback`. **Any other value is refused**: the method records a `run_summary_provenance_invalid` event at **error** severity and returns without writing anything. There is no third value and no default.
2. It calls `AppProperties.setLastRunProvenance()`, which writes the scoped property **`x_bst_startuptrk.ingestion.last_run_provenance`**. This is the one property this flow writes; the other three it only reads.
3. It records a `run_summary` event at **info** severity, carrying these members:

| Member | Meaning |
| --- | --- |
| `run` | The run identifier, which begins `linkedin-`. |
| `provenance` | `live` or `fallback`. |
| `processed` | Records written. |
| `rejected` | Rule-4, refusal, over-length and unresolved-parent rejections. |
| `skipped` | Operational skips. |
| `duplicates` | Rule-2 within-batch duplicates. |
| `unmatched` | Rule-3 values that matched no choice member. |
| `events_dropped` | Events discarded because the run exceeded the logger's event ceiling. |

The property write happens **before** the log record and is independent of it, so the provenance property is updated even when the log severity threshold would suppress the summary line. The guard of step 1 reads the **log record**, not the property, which is why the severity threshold matters to the cadence; see [Operational warnings](#operational-warnings).

**`x_bst_startuptrk.ingestion.last_run_provenance` is written by both flows**, so its value reflects whichever flow completed most recently and is not a per-flow marker. Read the per-flow provenance from the `run_summary` record whose `run` member begins `linkedin-`, which is what [Reading the flow execution log](#reading-the-flow-execution-log) filters on.

The five counter members are read from the logger instance this step calls the method on. **On the separate-step build they are zeros**, because that instance counted nothing; read the run totals from step 7 instead. On the orchestrator build they carry the whole batch. See [7.4](#74--counters-accumulate-on-a-logger-instance-not-globally).

### 8.4 — The step script

```javascript
(function execute(inputs, outputs) {

    var logger = new IngestionLogger();
    logger.useRun(inputs.run_id);

    var summary = logger.writeRunSummary(inputs.run_id, inputs.provenance);

    outputs.recorded = (summary && summary.recorded === true);
    outputs.provenance = inputs.provenance;

})(inputs, outputs);
```

### 8.5 — This is not the same evidence surface as the ATF label

There are **two** provenance surfaces in this package and they must never be confused.

| Surface | Written by | Survives? | Read by |
| --- | --- | --- | --- |
| **Scheduled-run provenance** | This step, on a real scheduled execution. | **Yes.** It is outside any test transaction. | Criterion 4. |
| **ATF result label** | The test setup step in [`05-atf-test-suites.md` (planned)](05-atf-test-suites.md), which labels the result `fallback validated` or `live validated`. | **No.** The Automated Test Framework rolls back the data a test creates, so a provenance row or property written inside a test does not persist. | The test report. |

Criterion 4 therefore reads **this** step's output and not the test label. Record the provenance of each of the three consecutive scheduled runs from the `run_summary` log record of that run. Criterion 4 explicitly accepts the sample-dataset substitute, so three clean `fallback` runs satisfy it — **provided the mode is recorded for each one.**

At the time of writing, neither credential alias holds a live credential on the target instance, so every run of this flow resolves to `fallback` and every result must be labelled accordingly. Guide 01 states the escalation path and the labelling obligation.

### 8.6 — The delivered orchestrators

`IngestionMapper` ships two orchestrator methods that perform steps 5 through 8 in one call, in exactly the order specified above:

| Method | Use |
| --- | --- |
| `IngestionMapper.ingest(run_id, source_system, provenance, rows)` | The live path. Expands each declared-record-type envelope, cleans, deduplicates at batch scope, resolves the parent Startup reference, upserts, stamps staging state, and finishes by calling `IngestionLogger.writeRunSummary()`. |
| `IngestionMapper.ingestStaging(run_id, source_system, import_run, provenance)` | The fallback path. Applies the staging query of [4.4](#44--the-staging-query) itself, then does everything `ingest()` does. |

A flow may call one orchestrator in place of the four separate steps. If you build it that way, **steps 5, 6, 7 and 8 remain the four phases that call performs**, each still observable in the log through the events of [7.2](#72--every-log-record-this-flow-can-write), and every statement in those four steps still applies.

Choose between the two constructions on this basis:

| | Separate steps 5 to 8 | One orchestrator call |
| --- | --- | --- |
| Per-phase counters visible as step outputs in the execution detail | **Yes** | No |
| Run summary carries the complete batch counters | No — zeros; read step 7 instead | **Yes** |
| Number of `IngestionLogger` instances | One per step | **One for the whole batch** |
| Cleaning, deduplication, parent resolution, upsert, staging-state stamping, run summary | All present | All present |

The orchestrator is the construction to use when the criterion-4 evidence must be readable from the single `run_summary` record, which is the normal case. Both constructions honour every statement in steps 5 through 8; they differ only in where the totals are read from, for the reason given in [7.4](#74--counters-accumulate-on-a-logger-instance-not-globally).

```javascript
// The orchestrator construction, replacing the separate steps 5 to 8.
(function execute(inputs, outputs) {

    var logger = new IngestionLogger();
    var mapper = new IngestionMapper();
    mapper.useLogger(logger);

    var outcome;
    if (inputs.provenance === 'live') {
        // Each row carries the record type declared in 3a.4.
        outcome = mapper.ingest(inputs.run_id, 'linkedin', 'live',
                                JSON.parse(inputs.rows || '[]'));
    } else {
        // Applies the staging query of 4.4 itself; no import_run for a scheduled run.
        outcome = mapper.ingestStaging(inputs.run_id, 'linkedin', '', 'fallback');
    }

    var counts = logger.counters();
    outputs.processed = counts.processed;
    outputs.rejected = counts.rejected;
    outputs.skipped = counts.skipped;
    outputs.duplicates = counts.duplicates;
    outputs.unmatched = counts.unmatched;
    outputs.recorded = (outcome && outcome.summary &&
                        outcome.summary.recorded === true);

})(inputs, outputs);
```

## The trigger

Add the trigger last, after all eight steps are built.

1. Open the flow and click the **trigger** area at the top.
2. Choose the **Scheduled** trigger type.
3. Set the fields below.

| Field | Value | Notes |
| --- | --- | --- |
| **Run** | `Repeat` | Not `Daily`, not `Weekly`, not `Once`. |
| **Repeat interval** | `0` days, `1` hour, `0` minutes | **Hourly.** This is deliberate. |
| **Starting on** | any time on or after today | Pick a whole hour so the executions are easy to find in the log. Offset it from guide 02's start time by thirty minutes so the two flows' executions are easy to tell apart in the log. |
| **Time zone** | the instance default | The guard compares elapsed hours, so the zone does not affect the cadence. |

4. Click **Done**.

The hourly repeat is **not** the ingestion cadence. The ingestion cadence is the property `x_bst_startuptrk.ingestion.cadence_hours`, enforced by the guard of step 1. With the shipped cadence of 24 hours, the flow executes roughly twenty-four times a day and does work roughly once. **Every one of those executions must exit before doing any work unless it passes the guard** — that is what step 1's `If` block guarantees, and it is why the runbook defines a scheduled run as a guard-passing execution.

To change the cadence, edit the property. Do not edit the trigger, and do not edit the guard. The property is shared by both flows, so changing it changes the cadence of guide 02's flow at the same time; the two guards remain independent of one another because each reads its own run-summary marker.

## Activation

1. Confirm every precondition in [Preconditions](#preconditions) still holds, and in particular that precondition 6 holds — **both aliases tested green** — and that precondition 7 holds, **guide 02's flow built and activated**.
2. Confirm you recorded the [Step 3b](#3b--the-pre-flight-check-that-chooses-the-path) outcome and built exactly one of [3a](#3a--the-primary-path-the-flow-designer-rest-step) or [3c](#3c--the-alternate-path-a-scoped-script-step).
3. Run the manual verification below **before** activating.
4. Click **Activate**.

A flow saved and activated before its alias tests green will fail on its first execution. See [Operational warnings](#operational-warnings).

## Verification — one manual run

Run the flow once by hand and confirm each step in turn. In Flow Designer use **Test**, then open the execution detail from the link the test returns.

Before the run, force a deterministic path so the result is repeatable:

1. Set `x_bst_startuptrk.ingestion.source_mode` to **`fallback`**. This skips the live attempt.
2. Confirm `x_bst_startuptrk.logging.level` is **`info`** or `debug`, or the run summary line will not be written and step 1's guard will lose its marker.
3. Confirm [`06-staging-table-csv-import.md` (planned)](06-staging-table-csv-import.md) has loaded the staging table, so step 4 has rows to return. If it has not, the run still passes with a row count of zero, but steps 5 through 7 have nothing to demonstrate.
4. Confirm `x_bst_startuptrk_startup` holds the companies the LinkedIn rows name, which guide 02's flow or the Crunchbase startups file supplies. Without them every row is rejected with `no startup carries the name` and the run demonstrates only the rejection path.

Then check each step against the table below.

| Step | What to confirm in the execution detail |
| --- | --- |
| 1 | `run_id` begins `linkedin-`. `cadence_hours` is between 6 and 48. `proceed` is `true`. A `cadence_guard` line appears in the log. |
| 2 | `source_mode` is `fallback` and `attempt_live` is `false`. |
| 3 | **Skipped**, because it sits inside the `attempt_live` block. |
| 4 | `provenance` is `fallback`. `row_count` matches the number of `pending` rows on `x_bst_startuptrk_ingest_staging` with `source_system` `linkedin`. A `source_resolved` line appears. |
| 5 | `accepted_count` plus `rejected_count` plus `duplicate_count` accounts for every incoming row. A `batch_cleaned` line appears. Any unmatched choice value has produced a `choice_unmatched` line — the fallback dataset carries one unmatched `title` on each person file and one unmatched `department`, `remote_type` and `seniority` on the job-postings file, so all four outcomes of [5.4](#54--the-no-other-asymmetry) are exercised in a single run. |
| 6 | `written_count` is greater than zero. Open `x_bst_startuptrk_founder`, `x_bst_startuptrk_executive` and `x_bst_startuptrk_jobposting` and confirm the records exist and that each carries a populated `startup` reference. Confirm `unresolved_count` matches the number of rows whose company is not on `x_bst_startuptrk_startup`. Confirm **no new Startup record was created** by this run. |
| 7 | The five counters are reported separately, never folded together. A `batch_reconciled` line appears and `reconciled` is `true`, meaning every incoming row is accounted for. |
| 8 | `recorded` is `true`. `x_bst_startuptrk.ingestion.last_run_provenance` now reads `fallback`. A `run_summary` line appears carrying all eight members of [8.3](#83--what-gets-written), with `run` beginning `linkedin-`. On the separate-step build its counter members are zeros by design; read the totals from step 7. |

Then confirm the two behaviours that only a second look reveals:

1. **The guard works in the other direction.** Run the flow a second time immediately. Step 1 must return `proceed` `false`, steps 2 through 8 must not run, and no second `run_summary` line must appear.
2. **Founder and Executive records did not cross tables.** Query both tables for the same person name. No person may appear on both. Confirm each Founder's `title` is a member of the Founder list and each Executive's `title` is a member of the Executive list, or is `Other`; a Founder carrying `Other` where the source said `CFO` means the row was declared on the wrong pass. See [6.3](#63--the-record_type-discriminator).

Finally, set `x_bst_startuptrk.ingestion.source_mode` back to **`live`**.

## Reading the flow execution log

The operator must be able to tell a no-op from a scheduled run at a glance, because criterion 4 counts only the latter.

| | No-op | Scheduled run |
| --- | --- | --- |
| **First action after the trigger** | Step 1, the cadence guard. | Step 1, the cadence guard. |
| **Guard outcome in the log** | `event="cadence_guard" ... outcome="no_op"` | `event="cadence_guard" ... outcome="proceed"` |
| **Steps that ran** | Step 1 only. The `If` block is not entered. | Steps 2 through 8, less step 3 on the fallback path. |
| **Outbound call** | None. | Attempted on the live path. |
| **Staging read** | None. | On the fallback path. |
| **Entity writes** | None. | Present. |
| **Run summary** | **None written.** | **`event="run_summary"` present, carrying the provenance.** |
| **Duration** | A fraction of a second. | Proportional to the batch. |

The single decisive test is the **run summary**: a no-op writes none. When collecting criterion-4 evidence, filter the application log to the source `x_bst_startuptrk`, search for `event="run_summary"` together with `run="linkedin-`, and take the three most recent records. Each is one scheduled run, and each carries its own provenance. Ignore the `cadence_guard` lines whose outcome is `no_op` entirely.

The `run="linkedin-` term is what separates this flow's evidence from guide 02's. Both flows write `run_summary` records to the same log with the same source, and both write the same `x_bst_startuptrk.ingestion.last_run_provenance` property, so the run-identifier prefix is the only reliable discriminator. Do not read the property to establish this flow's provenance.

The same rule is stated in [`../deployment-runbook.md`](../deployment-runbook.md#what-counts-as-a-scheduled-run), which is authoritative for it.

## Operational warnings

These three are not rationale. They describe failures that are easy to cause and hard to see.

### The alias binding is by name, and a mismatch fails at run time

**A name mismatch does not fail at build time.** A flow that names an alias which does not exist, or names it with a typographic error, saves without complaint and activates without complaint. Nothing in the Flow Designer interface reports the fault. It surfaces only when the flow executes — and because this is a scheduled flow, it can fail silently on its cadence until someone reads the flow execution log.

Three consequences:

1. **Copy the alias name from guide 01; never retype it.**
2. **Watch the two separators.** It is `x_bst_startuptrk.linkedin_oauth` — a dot after the scope, an underscore inside the alias name. Not `x_bst_startuptrk_linkedin_oauth`, and not `x_bst_startuptrk.linkedin-oauth`.
3. **On the [3c](#3c--the-alternate-path-a-scoped-script-step) path the failure is quieter still**, because `getConnectionInfo` returns `null` rather than raising. The script tests for `null` explicitly and writes `connection alias did not resolve`; without that test the step would fail on a property access with no useful message. The same `null` is returned when the alias exists but the flow's **Run As** identity cannot read it, which is why the flow runs as **System User**.

A flow saved before its alias tests green will fail on its first execution for the same reason. Precondition 6 requires the guide 01 connection test to have passed for **both** aliases before this flow is saved. That test is the only thing that proves the credential behind the alias is present and usable. At the time of writing, neither alias holds a live credential on the target instance. Until they do, run this flow with `x_bst_startuptrk.ingestion.source_mode` set to `fallback`, and label every result `fallback validated` and never `live validated`.

### An expired OAuth 2.0 token routes the run down the fallback branch silently

This is the warning specific to this flow, and it is the one most likely to produce a false pass.

An access token that has expired and a refresh token that has expired, been revoked or was never issued all present to this flow in exactly the same way: **an authentication failure**, which is trigger 1 of [4.1](#41--the-three-fallback-triggers). The flow does what it is specified to do — it logs a warning, sets the provenance to `fallback`, reads the staging table, cleans, writes and completes. **The run is green.** No step fails, no unhandled error is raised, and the flow execution log shows a successful execution.

A green run is therefore **not** evidence of live integration. Two obligations follow:

1. **Read the provenance marker on every run.** The authoritative value is the `provenance` member of the `run_summary` record whose `run` begins `linkedin-`. `live` means the LinkedIn call succeeded; `fallback` means it did not, or was never attempted. Never infer the mode from the run completing.
2. **When the provenance is `fallback` on a run that expected `live`, read the `warning` line that precedes it.** It names which of the three triggers fired. For an authentication failure, check the token state through **System OAuth > Manage Tokens** as guide 01's [Step 2.7](01-connection-credential-aliases.md#step-27--confirm-the-refresh-token-is-on-file-and-refresh-works) specifies — confirm a `Refresh Token` record exists for the provider and note its **Expires** value. Do not open the token fields, and do not place a token value. Follow guide 01's escalation route if the refresh token is absent or expired.

The refresh token's own lifespan is recorded on the provider record and it does expire. When it does, unattended access stops and the credential owner must re-issue it; every run in the meantime completes on the fallback dataset and must be labelled `fallback validated`.

### If this flow creates its own Startup records, the two flows produce duplicate companies

`x_bst_startuptrk_startup` has an upsert key — `name` plus `headquarters_location`, case-insensitively — and **only guide 02's flow writes through it**. This flow resolves against that table and never inserts into it, as specified in [6.2](#62--the-shared-startup-upsert-path).

Adding a Startup insert to this flow breaks that in a way nothing reports:

- A LinkedIn payload carries a company **name** but no `headquarters_location`. A Startup inserted from it would carry a blank headquarters location, so its deduplication key would be the name followed by a pipe and nothing — which never equals the key of the same company ingested from Crunchbase. **Two Startup records for one company.**
- With two records carrying the name, `IngestionMapper.resolveStartup()` stops resolving: it requires **exactly one** match, so from that point every person and job row for that company is rejected with `the name is ambiguous across 2 startups`. The failure appears one run later than the cause, on rows that were previously fine.
- A blank `headquarters_location` is a missing mandatory value on `x_bst_startuptrk_startup`, so the `Trim and validate startup` business rule aborts the insert — which means the corruption may present as an unexplained skip rather than as a duplicate, depending on the write path used.
- The startup inclusion criteria test `headquarters_location`, so a company inserted without one is absent from the Service Portal search results regardless of the rest of its data. See [`../data-model.md`](../data-model.md).

The rule is therefore absolute: **this flow reads `x_bst_startuptrk_startup` and never writes it.** If a company is missing, ingest it through guide 02's flow or load it from `crunchbase_startups_sample.csv`, then re-run this flow.

## Legacy provenance

This flow replaces the following legacy constructs. **Nothing below is ported.** The four cleaning rules of [step 5](#53--the-four-cleaning-rules) come from the prompt alone, and **there is no legacy pandas code to replicate** — the legacy implementation contradicts every one of the four rules.

### The scheduler

| Citation | What is there | What replaces it |
| --- | --- | --- |
| [`src/data_collection/scheduler.py:L13-L17`](../../../src/data_collection/scheduler.py) | **Five hard-coded hour intervals: 24, 24, 12, 6, 48.** Their minimum and maximum are exactly the cadence bounds this application enforces. | All five collapse into the single clamped property `x_bst_startuptrk.ingestion.cadence_hours`, read through `AppProperties.getCadenceHours()`. |

### The LinkedIn integrator

| Citation | What is there | What replaces it |
| --- | --- | --- |
| [`src/data_collection/api_integrators/linkedin_integrator.py:L11`](../../../src/data_collection/api_integrators/linkedin_integrator.py) | The base URL as a module constant. | The property `x_bst_startuptrk.linkedin.base_url`, carried on the alias's connection record. **Carried forward as non-secret endpoint configuration.** |
| `:L12` | A module-level `API_KEY` constant holding the credential in source. | The OAuth 2.0 client identifier, client secret and refresh token behind `x_bst_startuptrk.linkedin_oauth`, resolved at run time and never present in the flow, a step input, a script body or the Update Set. |
| `:L23`, repeated at `:L42` and `:L61` | That constant sent as a **static bearer `Authorization` header** on every call, at all three call sites. | Platform-managed OAuth 2.0 token exchange behind the alias. **LinkedIn's move to OAuth 2.0 is an authentication-model change, not a port.** No header is hand-assembled; see [3d](#3d--oauth-20-token-handling-belongs-to-the-credential-record). |
| `:L119-L120` | The founder-versus-executive decision made by a **title-substring heuristic** — `"Founder" in title`, then any of `CEO`, `CTO`, `CFO`, `COO`. | The explicit `record_type` discriminator of [6.3](#63--the-record_type-discriminator), which is what preserves prompt section 1.3's binding separate-tables directive. A title never selects a table. |

The three resource-path shapes of [3a.2](#3a2--the-resources-called) are the shapes those three call sites use, and the `data.elements` response shape is the one they read.

The heuristic at `:L119-L120` is worth naming precisely, because the target replaces two distinct faults in it and not one. It tests `"Founder" in title` first, so a chief financial officer whose title happens to contain the word *Founder* becomes a Founder record; and its executive test admits `CEO`, `CTO`, `CFO` and `COO` alike, so a chief executive not caught by the first test becomes an Executive — even though `CEO`, `CTO` and `COO` are members of the **Founder** title list in this application and only `CFO` is a member of the Executive list. Both faults disappear once the target table is decided by a declared record type rather than by reading the title.

### The cleaner

Every one of these contradicts a rule this flow enforces, which is why none is carried forward.

| Citation | What is there | The rule it contradicts |
| --- | --- | --- |
| [`src/data_collection/data_cleaning/startup_cleaner.py:L57`](../../../src/data_collection/data_cleaning/startup_cleaner.py) and `:L60` | Deduplication on **`company_name` + `website`**. | Rule 2, which deduplicates on `name` + `headquarters_location`, case-insensitively — the key this flow resolves company identity through. |
| `:L86` | Missing values filled with the string **`"Unknown"`**. | Rule 4, which rejects a record missing a mandatory field rather than inventing a value for it. |
| `:L90` | **Median imputation of missing numeric values** — the exact opposite of rejecting records that lack mandatory fields. | Rule 4. |
| `:L171-L176` with `:L183-L184` | A **four-entry placeholder industry dictionary** whose values match **none** of the binding choice lists, with everything else coerced to `"Other"`. | Rule 3, whose targets are the choice values of [`../data-model.md`](../data-model.md), reached through the two passes of [5.3](#53--the-four-cleaning-rules). |

The legacy enumerations are **replaced, not translated**, so no old-to-new mapping table exists and none is to be created. The per-source translation of pass one maps **LinkedIn's** vocabulary onto the target choice values, which is a different mechanism serving a different purpose.

## Build verification

Do not sign this guide off until every line below is true.

| # | Check |
| --- | --- |
| 1 | One flow named `LinkedIn Ingestion` exists in the `x_bst_startuptrk` scope, with **Run As** `System User`. |
| 2 | The trigger is **Scheduled**, set to **repeat hourly**. |
| 3 | All **eight** steps are present and in order, with steps 2 through 8 inside the `If` block controlled by step 1's `proceed` output. |
| 4 | Exactly **one** of [3a](#3a--the-primary-path-the-flow-designer-rest-step) or [3c](#3c--the-alternate-path-a-scoped-script-step) is built, and the [3b](#3b--the-pre-flight-check-that-chooses-the-path) outcome is recorded here: `______`. |
| 5 | The alias name reads `x_bst_startuptrk.linkedin_oauth` exactly, at every occurrence in the flow. |
| 6 | No IntegrationHub spoke is installed, activated, referenced or used. |
| 7 | **No key, secret, token or password appears** in the flow record, any flow input, any step input, any script body or any test payload. No step holds, returns or logs an access token or a refresh token, and no step assembles an `Authorization` header. |
| 8 | The flow reads `x_bst_startuptrk.ingestion.cadence_hours`, `x_bst_startuptrk.ingestion.source_mode` and `x_bst_startuptrk.linkedin.base_url`, and writes `x_bst_startuptrk.ingestion.last_run_provenance`. It reads no other property except `x_bst_startuptrk.logging.level` by way of `IngestionLogger`. |
| 9 | The flow writes `x_bst_startuptrk_founder`, `x_bst_startuptrk_executive` and `x_bst_startuptrk_jobposting`, and **no other table**. It does not write `x_bst_startuptrk_newsarticle`, and it does not write `x_bst_startuptrk_startup`. |
| 10 | The flow **reads** `x_bst_startuptrk_startup` to resolve each row's mandatory `startup` reference, through the shared key of [6.2](#62--the-shared-startup-upsert-path), and inserts no record into it. The manual run created no new Startup. |
| 11 | The flow reads `x_bst_startuptrk_ingest_staging` on the fallback branch, with the query of [4.4](#44--the-staging-query) and **no `record_type` condition**. |
| 12 | Every person record carries the `record_type` its call site or staging row declared. **No person appears on both `x_bst_startuptrk_founder` and `x_bst_startuptrk_executive`**, and no step reads a `title` value to choose a table. |
| 13 | The flow calls `AppProperties`, `IngestionMapper` and `IngestionLogger`, and re-implements none of their logic — not the cadence clamp, not a cleaning rule, not a log severity decision. |
| 14 | No write uses `setWorkflow(false)`, and the `Trim and validate startup` business rule of [6.5](#65--business-rules-must-run) is active. |
| 15 | The manual run of [Verification](#verification--one-manual-run) passed every row of its table, and the immediate second run returned `proceed` `false` with no run summary. |
| 16 | `x_bst_startuptrk.ingestion.source_mode` has been set back to `live`. |
| 17 | The flow is **activated**. |

Criterion 4 in [`../validation-checklist.md` (planned)](../validation-checklist.md) is satisfied separately, by three consecutive guard-passing runs with zero unhandled errors and the provenance of each one recorded.

## Related documents

| Document | Relationship |
| --- | --- |
| [`01-connection-credential-aliases.md`](01-connection-credential-aliases.md) | Establishes `x_bst_startuptrk.linkedin_oauth`, which [step 3](#step-3--call-linkedin-through-the-alias) binds to by name, together with the OAuth 2.0 provider, entity profile and refresh-token records behind it. Must be complete first, with **both** aliases tested green. |
| [`02-flow-crunchbase-ingestion.md`](02-flow-crunchbase-ingestion.md) | The identical eight-step skeleton for Crunchbase. Steps 1, 2, 4, 5, 7 and 8 match this guide; only the alias, base URL and target tables differ. It also owns the **shared Startup upsert path** of [6.2](#62--the-shared-startup-upsert-path) and writes the Startup records this flow resolves against. Must be complete first. |
| [`04-service-portal-pages-and-widgets.md`](04-service-portal-pages-and-widgets.md) | The portal that reads the records this flow writes, including the People tab of the company profile. |
| [`06-staging-table-csv-import.md` (planned)](06-staging-table-csv-import.md) | Loads `x_bst_startuptrk_ingest_staging`, which [step 4](#step-4--fall-back-to-the-staging-table) reads, from `linkedin_founders_sample.csv`, `linkedin_executives_sample.csv` and `linkedin_job_postings_sample.csv`. |
| [`05-atf-test-suites.md` (planned)](05-atf-test-suites.md) | The flow test that exercises this flow and applies the `fallback validated` / `live validated` label. |
| [`../manual-build-instructions.md` (planned)](../manual-build-instructions.md) | The build order and the Update Set versus manual-build split rule. |
| [`../data-model.md`](../data-model.md) | The Founder and Executive column sets with their two different `title` choice lists, JobPosting's three choice lists, the staging table's forty columns, and the cascade rules on the `startup` reference. |
| [`../access-control.md`](../access-control.md) | The role and ACL posture of the three tables this flow writes, including the `contact_email` field-level read controls on Founder and Executive. |
| [`../api-reference.md`](../api-reference.md) | The Script Include call graph, the full property inventory, and the nested `GET /founders/{startup_id}/executives` sub-resource that serves the Executive records this flow writes. |
| [`../validation-checklist.md` (planned)](../validation-checklist.md) | Criterion 4, which reads [step 8](#step-8--write-the-run-summary-and-the-provenance-marker). |
| [`../validation-gates.md`](../validation-gates.md) | The sixteen post-commit gates of precondition 4, and the eleven-gate core of precondition 5. |
| [`../deployment-runbook.md`](../deployment-runbook.md) | Authoritative for [what counts as a scheduled run](../deployment-runbook.md#what-counts-as-a-scheduled-run). |
| [`../gaps-and-flags.md` (planned)](../gaps-and-flags.md) | Records the runtime-configurable schedule interval and the NewsArticle ingestion exclusion. |
| [`../../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml`](../../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml) | **Authoritative** for every identifier cited in this guide. |
| [`../../sample-data/README.md`](../../sample-data/README.md) | The column contract of the fallback dataset, the `data.elements` envelope, the load order that places the Crunchbase startups file first, and the procedure for forcing the fallback path. |
| [`../../../docs/decisions/DECISION_LOG.md` (planned)](../../../docs/decisions/DECISION_LOG.md) | Every "why" behind this flow, including the four deviations named at the top of this guide. |
