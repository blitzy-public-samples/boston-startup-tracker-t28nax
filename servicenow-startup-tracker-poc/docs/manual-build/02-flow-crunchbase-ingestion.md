# Manual build 02 — Crunchbase ingestion flow — `x_bst_startuptrk`

This guide builds the Crunchbase ingestion flow of the ServiceNow scoped application `x_bst_startuptrk` by hand, on the instance, in Flow Designer. It specifies **one** scheduled flow built from **eight** numbered steps, and for each step it states the step type, every input to set, every data pill consumed, every output produced and the branch behaviour on each outcome. It also states the trigger configuration, the activation procedure, the single manual run that confirms each step, how to read the flow execution log, and the completion criteria to satisfy before this guide is signed off.

**Authority.** The frozen prompt and the Agent Action Plan are authoritative for all application content. The Update Set XML at [`../../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml`](../../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml) is the authoritative source for every table name, column name, choice value, Script Include class name, method name and system-property key cited below; the identifiers used here match those records character for character, and the same identifiers appear in [`../data-model.md`](../data-model.md) and [`../api-reference.md`](../api-reference.md). No variant spelling of any identifier is valid. Where this guide and those records disagree, the records are checked against the prompt and the plan first; where the records match the specification, this guide is corrected to them.

This document carries **no rationale**. It states what to build and how to build it. Every decision behind this flow, every alternative considered and every risk it carries is recorded in [`../../../docs/decisions/DECISION_LOG.md` (planned)](../../../docs/decisions/DECISION_LOG.md), which is the single source of truth for "why". Three points in this guide depart from a literal reading of the requirements — the hourly trigger paired with an elapsed-time guard in place of a trigger interval read from a property, the split that assigns Startup, Investor and FundingRound to Crunchbase while Founder, Executive and JobPosting go to LinkedIn, and the deployment-time branch between the Flow Designer REST step and a scoped script step. Each is stated below as a build mechanic and cross-referenced to that log. None is argued here.

Operational warnings **are** in scope for this guide and are marked as such. The three warnings under [Operational warnings](#operational-warnings) are load-bearing and must not be skipped: two of them describe failures that surface at run time rather than at build time, and the third describes a failure that is silent.

## Referenced documents

This guide is executable on its own. All eight steps, every property read, every table written, every cleaning rule, every log write, the trigger, the activation and the verification are stated here in full. An operator needs no other file to build the flow.

Documents marked **(planned)** are in-scope artifacts of this deliverable package that are authored elsewhere in the same delivery. A link to a planned document resolves once that document lands; nothing in this guide depends on reading one first, with the single exception recorded in precondition 7.

| Document | What this guide takes from it |
| --- | --- |
| [`01-connection-credential-aliases.md`](01-connection-credential-aliases.md) | The alias name `x_bst_startuptrk.crunchbase_api` this flow binds to, and the connection test that must have passed before this flow is saved. |
| [`03-flow-linkedin-ingestion.md` (planned)](03-flow-linkedin-ingestion.md) | The companion flow. It is the **identical** eight-step skeleton, differing only in source system, alias and target tables. Steps 1, 2, 4, 5, 7 and 8 are the same in both guides. |
| [`06-staging-table-csv-import.md` (planned)](06-staging-table-csv-import.md) | The load that puts rows into `x_bst_startuptrk_ingest_staging`, which step 4 reads. |
| [`05-atf-test-suites.md` (planned)](05-atf-test-suites.md) | The Automated Test Framework test that exercises this flow, and the `fallback validated` / `live validated` result label. |
| [`../manual-build-instructions.md` (planned)](../manual-build-instructions.md) | The split rule for the package as a whole: which artifacts ship as Update Set XML and which are built by hand. |
| [`../data-model.md`](../data-model.md) | The tables, columns, choice values, cascade rules and the `Investor.portfolio_count` derivation. |
| [`../access-control.md`](../access-control.md) | The role and ACL posture of the tables this flow writes. |
| [`../validation-checklist.md` (planned)](../validation-checklist.md) | Success criterion 4, which reads the run-summary surface step 8 writes. |
| [`../validation-gates.md`](../validation-gates.md) | The sixteen post-commit gates of precondition 4, and the eleven-gate core of precondition 5. |
| [`../deployment-runbook.md`](../deployment-runbook.md) | The definition of a scheduled run, under [What counts as a scheduled run](../deployment-runbook.md#what-counts-as-a-scheduled-run). |
| [`../gaps-and-flags.md` (planned)](../gaps-and-flags.md) | The requirements with no clean platform equivalent, including the runtime-configurable schedule interval. |
| [`../../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml`](../../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml) | **Authoritative** for every identifier this guide cites. |
| [`../../sample-data/README.md`](../../sample-data/README.md) | The column contract of the fallback dataset step 4 reads. |
| [`../../../docs/decisions/DECISION_LOG.md` (planned)](../../../docs/decisions/DECISION_LOG.md) | The single destination for every "why". |

## Position in the build order

This is **guide 02 of six**, and it is **step 2** of the execution order below. It runs immediately after guide 01, because this flow binds guide 01's alias **by name**. The order is stated in full in [`../manual-build-instructions.md` (planned)](../manual-build-instructions.md); it is repeated here so this guide can be run without it. The execution order is not the filename order: guide **06** runs before guide **05**.

| Step | Guide | Why it sits here |
| --- | --- | --- |
| 1 | [`01-connection-credential-aliases.md`](01-connection-credential-aliases.md) | The two Connection & Credential Aliases the ingestion flows bind to by name. Nothing downstream can authenticate without them. |
| **2** | **This guide** | **The Crunchbase ingestion flow, which references `x_bst_startuptrk.crunchbase_api` by name.** |
| 3 | [`03-flow-linkedin-ingestion.md` (planned)](03-flow-linkedin-ingestion.md) | The LinkedIn ingestion flow, which references `x_bst_startuptrk.linkedin_oauth` by name. The identical skeleton. |
| 4 | [`04-service-portal-pages-and-widgets.md`](04-service-portal-pages-and-widgets.md) | The portal, theme, five pages and eight widgets. |
| 5 | [`06-staging-table-csv-import.md` (planned)](06-staging-table-csv-import.md) | The staging-table CSV load. |
| 6 | [`05-atf-test-suites.md` (planned)](05-atf-test-suites.md) | The Automated Test Framework suites, **last**, because they exercise everything the five preceding guides build. |

Guide **03** follows this one and is built from the same skeleton. A reader comparing the two guides must find **no discrepancy** in steps 1, 2, 4, 5, 7 and 8, which means:

- **Steps 1, 2, 7 and 8 are identical**, word for word in substance. The cadence guard, the source-mode resolution, the log-skip-continue contract and the run summary carry the same mechanics, the same properties and the same log events in both guides.
- **Steps 4 and 5 are identical in semantics**, with the source-system token substituted: guide 03 filters the staging table on `linkedin` rather than `crunchbase` and passes that token to the mapper, and the per-source translation table of pass one is the LinkedIn one. The three fallback triggers, the staging query shape, the four cleaning rules and the no-`Other` behaviour do not differ at all.
- **Only steps 3 and 6 differ substantively**: step 3 names a different alias and base URL and calls different resources, and step 6 writes `x_bst_startuptrk_founder`, `x_bst_startuptrk_executive` and `x_bst_startuptrk_jobposting` instead of this guide's four tables.

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
| 7 | The four Script Includes this flow calls into are on the instance. | `sys_script_include` carries `AppProperties`, `IngestionMapper`, `IngestionLogger` and `InvestorPortfolioService`, all in the `x_bst_startuptrk` scope. |
| 8 | The four scoped system properties this flow reads or writes are on the instance. | `sys_properties` carries `x_bst_startuptrk.ingestion.cadence_hours`, `x_bst_startuptrk.ingestion.source_mode`, `x_bst_startuptrk.ingestion.last_run_provenance` and `x_bst_startuptrk.crunchbase.base_url`. |
| 9 | The four tables this flow writes are on the instance. | `x_bst_startuptrk_startup`, `x_bst_startuptrk_investor`, `x_bst_startuptrk_fundinground` and `x_bst_startuptrk_m2m_round_investor` all open in the list view. Gates `GATE-TBL-01`, `GATE-TBL-04` and `GATE-TBL-05` cover three of the four. |
| 10 | The staging table this flow reads on the fallback branch is on the instance. | `x_bst_startuptrk_ingest_staging` opens in the list view. It ships with `ws_access` **false**, so confirm it in the list view and not over the Table API. |
| 11 | The three business rules that maintain the derived columns are on the instance and **active**. | `sys_script` carries `Trim and validate startup`, `Recalculate investor portfolio on funding round` and `Recalculate investor portfolio on round investor link`, all `active` true, all in the `x_bst_startuptrk` scope. |
| 12 | You are working in the `x_bst_startuptrk` application scope. | The application picker reads **Boston Startup Tracker**. Every record this guide creates must carry that scope. |
| 13 | You hold a role that can create and publish a flow. | You can open Flow Designer, create a flow in the `x_bst_startuptrk` scope, and see the **Activate** control on a saved flow. |

### Why this guide exists rather than more Update Set XML

Only tables carrying the update-synch attribute are captured into `sys_update_xml` records, and adding that attribute to a table that lacks it out of the box is unsupported. The Flow Designer tables are outside the captured set, so this flow is built through the platform interface instead — which is why the delivered Update Set contains **zero** flow records. [`../manual-build-instructions.md` (planned)](../manual-build-instructions.md) owns the split rule for the package as a whole.

## Platform constraint

**IntegrationHub spokes are forbidden.** Prompt section 4.0 binds this absolutely. Do **not** install, activate, reference or open any spoke content set, and do not use a spoke action anywhere in this flow. A generic REST step is not a spoke. This flow uses a generic REST step bound to the alias established in guide 01, or the scoped script step of [Step 3c](#3c--the-alternate-path-a-scoped-script-step) where that step is unavailable.

**No credential material appears anywhere in this flow.** Not in the flow record, not in a flow input, not in a step input, not in a script step, not in a test payload, and not in the Update Set. The alias is referenced by name and the platform resolves the secret at run time. Guide 01 holds the credential records; this guide never reads their values and never prints them.

## What this guide builds

One record, containing eight steps.

| Artifact | Count | Table | Notes |
| --- | --- | --- | --- |
| Scheduled flow | 1 | `sys_hub_flow` | Built in Flow Designer, in the `x_bst_startuptrk` scope. |
| Flow trigger | 1 | Scheduled, **repeat hourly** | See [The trigger](#the-trigger). The hourly repeat is deliberate and is paired with the guard of step 1. |
| Flow steps | 8 | — | Numbered 1 to 8 below. Steps 2 through 8 sit inside one `If` block controlled by step 1. |

The flow reads **four** system properties, writes **one**, reads **one** staging table, writes **four** entity and join tables, calls **four** Script Includes, and emits **fifteen** distinct kinds of log record — nine through `IngestionLogger` and six of its own step lines. Each is enumerated in its own step, and the log records are inventoried together in [7.2](#72--every-log-record-this-flow-can-write).

## The flow record

Create the flow first, with no steps, then add the steps in order.

1. Set the application picker to **Boston Startup Tracker**.
2. Open **Flow Designer**, then **New**, then **Flow**.
3. Set the fields below.

| Field | Value | Notes |
| --- | --- | --- |
| **Flow name** | `Crunchbase Ingestion` | The internal name derives from this. Guide 03 uses `LinkedIn Ingestion`. |
| **Application** | `Boston Startup Tracker` | The `x_bst_startuptrk` scope. Confirm this before saving; a flow created in Global cannot be moved into the scope afterwards. |
| **Description** | `Ingests Crunchbase organisation and funding-round data into x_bst_startuptrk_startup, x_bst_startuptrk_investor, x_bst_startuptrk_fundinground and x_bst_startuptrk_m2m_round_investor on the configured cadence. Implements prompt section 4.0 scheduled ingestion.` | The description convention across this package is a **pointer**: it states what the artifact does and which requirement it implements. It never states why. |
| **Run As** | **System User** | A scheduled flow has no initiating user. This setting also governs whether the alias resolves; see [Operational warnings](#operational-warnings). |
| **Protection** | `None` | |
| **Run With Roles** | leave empty | The flow must not acquire roles beyond its run-as identity. |

4. Save the flow. Do not activate it yet — activation is [its own step](#activation), after all eight steps are built and one manual run has passed.

### The run identifier

Every step of this flow carries a **run identifier**, minted once by step 1 and passed as a data pill into steps 4, 5, 6, 7 and 8. Its format is the source-system token, a hyphen, then a fourteen-digit timestamp:

```text
crunchbase-20260807143000
```

Guide 03 mints `linkedin-<yyyyMMddHHmmss>` by the same rule. The token prefix is not decorative: step 1's guard and step 8's run summary are both keyed on it, which is what keeps the two flows' cadences independent of one another. Do not shorten it, do not omit the prefix, and do not reuse an identifier across executions.

## Step 1 — Cadence guard

**Step type:** Script (Utilities → Script), followed by one `If` flow-logic block.

This is the **first action after the trigger** and it runs on every execution, including the many that do no work. It decides whether this execution is a scheduled run or a no-op.

### 1.1 — What the guard compares

The guard compares the **elapsed time since the last run summary this flow wrote** against the cadence, in hours.

The cadence is the scoped property `x_bst_startuptrk.ingestion.cadence_hours`. Its shipped value is **24**. It is **clamped to the range 6 to 48**. The clamp is owned by the `AppProperties` Script Include, which exposes it as `AppProperties.getCadenceHours()`. **Do not re-implement the clamp in the flow.** Read the value through that method and use whatever it returns: a stored value below 6 returns 6, a stored value above 48 returns 48, and a stored value that is absent or not an integer returns the default of 24. Changing the cadence at run time is done by editing that one property and nothing else — no flow edit, no re-publish.

The last-run marker is the most recent `run_summary` log record whose run identifier begins `crunchbase-`. Step 8 writes that record on every execution that passes this guard and completes. A no-op writes none, so consecutive no-ops never move the marker forward.

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
    outputs.run_id = 'crunchbase-' + stamp.getValue()
        .replace(/[^0-9]/g, '').substring(0, 14);
    outputs.cadence_hours = cadence;

    // Most recent run summary this flow wrote, identified by the run-id prefix.
    var marker = new GlideRecord('syslog');
    marker.addQuery('source', 'x_bst_startuptrk');
    marker.addQuery('message', 'CONTAINS', 'event="run_summary"');
    marker.addQuery('message', 'CONTAINS', 'run="crunchbase-');
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
| `live` | **The default, and what every real run attempts first.** The flow proceeds to step 3 and calls Crunchbase through the alias. If that call fails in one of the three ways listed in [Step 4](#step-4--fall-back-to-the-staging-table), the flow falls back to the staging table for that run. |
| `fallback` | The flow **skips the live attempt altogether** and goes straight to the staging read of step 4. Set this value to make a test deterministic without touching a credential. Set it back to `live` afterwards. |

Setting the property to `fallback` is the procedure [`../../sample-data/README.md`](../../sample-data/README.md) refers to as forcing the fallback path, and it is how the flow test in [`05-atf-test-suites.md` (planned)](05-atf-test-suites.md) reaches a repeatable result. The difference between the two values is only whether the live call is attempted: a run left on `live` also reads the staging dataset whenever the live call fails.

Wrap step 3 in an **`If`** block whose condition is step 2's `attempt_live` output **is** `true`. Steps 4 through 8 sit outside that inner block and run on both paths.

## Step 3 — Call Crunchbase through the alias

**Step type:** either a REST step or a Script step. **Which one you build is decided by the pre-flight check in [Step 3b](#3b--the-pre-flight-check-that-chooses-the-path), and you build exactly one of them.** This is a real deployment-time branch that depends on what the instance offers, not a hypothesis. Do not build both.

Both paths are identical in three respects that matter: each **references the alias `x_bst_startuptrk.crunchbase_api` by name**, neither uses an IntegrationHub spoke, and neither puts a key, secret, token or password into the flow, a step input, a script body or the Update Set.

### 3a — The primary path: the Flow Designer REST step

Add the **REST** step from the **Integration** category and set the fields below.

| Field | Value | Notes |
| --- | --- | --- |
| **Connection type** | **Use Connection Alias** | Not an inline connection. An inline connection would require the endpoint and credential to be typed into the step, which this build forbids. |
| **Connection Alias** | `x_bst_startuptrk.crunchbase_api` | **Copy this value from guide 01; never retype it.** Watch the two separators: a dot after the scope and an underscore inside the alias name. |
| **Base URL** | resolved from the alias | The alias's connection record already carries the base URL, which is the value of the property `x_bst_startuptrk.crunchbase.base_url`. Leave the step's own base URL empty so the alias supplies it. |
| **HTTP method** | `GET` | All three calls are reads. |
| **Resource path** | one of the two shapes in [3a.2](#3a2--the-resources-called) | Set per call. |
| **Query parameters** | none | **The API key is not a query parameter.** The alias supplies the credential; see [Legacy provenance](#legacy-provenance) for what this replaces. |
| **Request headers** | `Accept: application/json` | |
| **Request body** | empty | |
| **Connection timeout / Retry policy** | leave at the step defaults | A timeout is one of the three fallback triggers in step 4. |

#### 3a.1 — Step inputs

| Input | Value |
| --- | --- |
| `run_id` | Data pill: **Step 1 → run_id**. Carried through so the log lines correlate. |

#### 3a.2 — The resources called

Two resource-path shapes, three call sites. Both are relative to the base URL the alias supplies.

| # | Resource path | Purpose | Response shape |
| --- | --- | --- | --- |
| 1 | `/organizations/{permalink}` | The organisation record for a startup. | A single object under **`data.properties`**. |
| 2 | `/organizations/{permalink}` | The organisation record for an investor. The same resource; Crunchbase models investors as organisations. | A single object under **`data.properties`**. |
| 3 | `/organizations/{permalink}/funding_rounds` | The funding rounds of one organisation. | An **array** under **`data.items`**. |

`IngestionMapper.unwrapLive()` handles both shapes and needs no help from the flow: it unwraps `data` when present, returns the array it finds under `items` if there is one, and otherwise returns the single object under `properties` as a one-element list. Pass the response body to it whole. Do not pre-parse, pre-flatten or re-key it in the flow.

#### 3a.3 — Step outputs

The REST step exposes **Response Body**, **Status Code**, **Response Headers** and **Error message**. Step 4 consumes the first three.

| Output | Consumed by |
| --- | --- |
| **Status Code** | Step 4's authentication-failure and error-status test. |
| **Response Body** | Step 4's malformed-response test, then step 5 by way of `IngestionMapper.unwrapLive()`. |
| **Error message** | Step 4's timeout test, and the log line step 4 writes. |

### 3b — The pre-flight check that chooses the path

Run this check **before** adding any step, and record the answer.

1. Open Flow Designer in the `x_bst_startuptrk` scope, create a scratch flow, and attempt to add the **REST** step from the **Integration** category.
2. If the step is offered **and** its **Connection Alias** field populates with `x_bst_startuptrk.crunchbase_api` when you search for it, the instance supports the primary path. Delete the scratch flow and build **[3a](#3a--the-primary-path-the-flow-designer-rest-step)**.
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

    var ALIAS = 'x_bst_startuptrk.crunchbase_api';

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
        request.setBasicAuth(info.getCredentialAttribute('user_name'),
                             info.getCredentialAttribute('password'));
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

`info.getAttribute('connection_url')` returns the base URL the alias's connection record carries, which is the value of `x_bst_startuptrk.crunchbase.base_url`. The two `getCredentialAttribute` calls hand the credential straight into `setBasicAuth` without assigning it to a named variable, without logging it and without returning it as a step output. **Never add the credential to an output variable, a log line or a flow input.**

If the alias resolves to nothing, `getConnectionInfo` returns **`null` rather than raising** — which is why the script tests for it explicitly. See [Operational warnings](#operational-warnings) for the run-as consequence of that behaviour.

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

### 4.2 — Step inputs

| Input | Value |
| --- | --- |
| `run_id` | Data pill: **Step 1 → run_id**. |
| `attempt_live` | Data pill: **Step 2 → attempt_live**. |
| `status_code` | Data pill: **Step 3 → Status Code** (REST step) or **Step 3 → status_code** (script step). Leave empty when step 3 did not run. |
| `response_body` | Data pill: **Step 3 → Response Body** or **Step 3 → response_body**. |
| `error_message` | Data pill: **Step 3 → Error message** or **Step 3 → error_message**. |

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
| `source_system` | `crunchbase` | Lower-cased before the query is added. This is what keeps the two flows from reading each other's rows. |
| `import_state` | `pending` | Rows already `processed`, `rejected` or `error` are never re-read. |
| `import_run` | optional | Added only when the flow is given a specific import-run token. Leave it unset for a scheduled run so every pending Crunchbase row is picked up. |
| order | `orderBy('sys_id')` | Deterministic ordering, which is what makes the batch-level deduplication of step 5 reproducible. |

**`record_type` is not a query condition.** The query returns every pending Crunchbase row and the mapper **reads `record_type` off each row**. The restriction to this flow's three record types is enforced inside the mapper by its source-to-type map, which allows `startup`, `investor` and `funding_round` for `crunchbase` and rejects anything else on that source. Do not add a `record_type` filter to the query.

The staging table ships with `ws_access` **false**. Read it with `GlideRecord` from the script step, and inspect it by eye in the **list view** — not over the Table API.

**[`06-staging-table-csv-import.md` (planned)](06-staging-table-csv-import.md) must have loaded that table for this branch to yield rows.** Until it has run, the fallback branch completes correctly with a row count of zero. The column contract of the loaded rows is in [`../../sample-data/README.md`](../../sample-data/README.md).

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
                var live = mapper.unwrapLive('crunchbase', JSON.parse(body));
                if (!live || !live.length) {
                    reason = 'malformed response, no records found';
                } else {
                    rows = live;
                    provenance = 'live';
                }
            } catch (e) {
                reason = 'malformed response, body is not JSON';
            }
        }

        if (reason) {
            logger.warn(inputs.run_id,
                'live Crunchbase call failed, falling back to the staging table: ' + reason);
        }
    }

    if (provenance === 'fallback') {
        var staging = new GlideRecord('x_bst_startuptrk_ingest_staging');
        staging.addQuery('source_system', 'crunchbase');
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

Every record, on both the live and the fallback path, passes through the `IngestionMapper` Script Include. The four cleaning rules live there and **nowhere else**, which is what keeps this flow and the LinkedIn flow from diverging. Do not re-implement any rule in the flow.

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

This is the **shared deduplication key**. [`03-flow-linkedin-ingestion.md` (planned)](03-flow-linkedin-ingestion.md) resolves company identity through the same key, which is what lets a founder ingested from LinkedIn attach to a startup ingested from Crunchbase.

**Rule 3 — normalise `funding_stage` and `round_type` to the enumerated choice values, mapping unmatched values to `Other` and logging them.** This is two passes in sequence, and both live in the mapper.

*Pass one, source-vocabulary translation.* A live Crunchbase payload states its values in Crunchbase's own code vocabulary — `series_b`, `private_equity`, `c_00051_c_00200`, `Science and Engineering` — not in the target choice values. `IngestionMapper` carries a translation table per source system and field, keyed on the lower-cased source code, and applies it **first**. A known code becomes its target value. An unknown code passes through untouched to pass two. A code known to have no target member at all — `debt_financing`, `grant`, `initial_coin_offering` and their siblings — resolves to nothing and is logged as a recognised source code with no target member, left unwritten. The Crunchbase side of that table covers `funding_stage` and `round_type` from the funding-type vocabulary, `industry` and `focus_areas` from the category-group vocabulary, `employee_count_range` from the head-count bucket codes, `active` from the operating-status codes, and `type` from the investor-type codes.

*Pass two, `IngestionMapper.normaliseChoice()`.* An exact match against the choice list is stored as supplied. A case-insensitive match is stored with the choice list's **own** spelling. A value that matches nothing is stored as `Other` **where the list declares an `Other` member**, and where the list declares none the field is **left unwritten**. Either way `IngestionLogger.unmatchedChoice()` records a `choice_unmatched` event naming the column, the supplied value and which outcome applied.

"Left unwritten" is precise and is not the same as "emptied": the mapper removes the field from the record it is about to write, so on an **insert** the column is simply empty, while on an **update** whatever the column already stores survives untouched.

**No value outside a column's choice list is ever stored.** The complete outcome table for the choice columns this flow writes is in [5.4](#54--the-no-other-asymmetry).

**Rule 4 — reject records missing mandatory fields rather than inserting partial rows.** `IngestionMapper.missingMandatory()` checks the record type's mandatory set and, when anything is absent, rejects the whole record with the reason `missing mandatory` followed by the field names, logged by `IngestionLogger.rejectRecord()`. Nothing partial is ever inserted. The mandatory sets for this flow's three record types are:

| Record type | Mandatory fields |
| --- | --- |
| `startup` | `name`, `headquarters_location`, `active` |
| `investor` | `name` |
| `funding_round` | `startup`, `round_date` |

Two further refusals sit alongside rule 4 in the same pass and reject by the same route: a value that does not match its declared type on a **mandatory** column is refused rather than repaired, and a value longer than its column's maximum length is rejected rather than truncated.

**There is no old-to-new mapping table for the legacy enumerations, and none is to be invented.** The choice lists of this application are replacements, not translations, of the legacy ones. Pass one above translates the **source system's** vocabulary, which is a different thing entirely.

### 5.4 — The no-`Other` asymmetry

Rule 3 says unmatched values map to `Other`. That is only possible where the choice list declares an `Other` member, and **four of the choice columns this flow writes declare none.**

| Choice column | Declares `Other` | Outcome for an unmatched value |
| --- | --- | --- |
| `x_bst_startuptrk_startup.industry` | Yes | Stored as `Other`, logged. |
| `x_bst_startuptrk_startup.funding_stage` | **No** | **Left unwritten, logged.** |
| `x_bst_startuptrk_startup.employee_count_range` | **No** | **Left unwritten, logged.** |
| `x_bst_startuptrk_investor.type` | **No** | **Left unwritten, logged.** |
| `x_bst_startuptrk_investor.focus_areas` | Yes | Each unmatched token becomes `Other`, then the tokens are de-duplicated, logged. |
| `x_bst_startuptrk_fundinground.round_type` | **No** | **Left unwritten, logged.** |

`x_bst_startuptrk_investor.type` is the asymmetry to watch. An operator may expect an investor type to be coerced; it is not. Its choice list declares exactly `VC`, `Angel`, `PE`, `Corporate` and `Accelerator`, with no `Other`, so an unmatched investor type is refused, the `type` column is left unwritten, and `IngestionLogger.unmatchedChoice()` logs it. **The record itself survives and is still written** — `type` is not a mandatory column, and rejection is reserved for a record missing a mandatory field.

**Do not add an `Other` member to any of the four lists that lack one.** The choice records in the Update Set are exactly the values those definitions declare, and [`../data-model.md`](../data-model.md) is authoritative for all of them.

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
        prepared.push(mapper.prepareOne(inputs.run_id, 'crunchbase', incoming[i]));
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

Exhaustively, this flow writes **four** tables and no others.

| # | Table | What this flow writes to it |
| --- | --- | --- |
| 1 | `x_bst_startuptrk_startup` | Startup records from the Crunchbase organisation payload. |
| 2 | `x_bst_startuptrk_investor` | Investor records from the Crunchbase organisation payload. |
| 3 | `x_bst_startuptrk_fundinground` | Funding-round records from the Crunchbase funding-rounds payload, including the `lead_investor` reference. |
| 4 | `x_bst_startuptrk_m2m_round_investor` | One **participant row** per participating investor per funding round. |

**This flow does not write `x_bst_startuptrk_newsarticle`.** Automated NewsArticle ingestion is out of scope: no flow ingests it, there is no NewsArticle sample CSV, and the staging table's `record_type` choice list contains no `news_article` member. NewsArticle records are created by manual entry or by a REST write only. The exclusion is recorded in [`../gaps-and-flags.md` (planned)](../gaps-and-flags.md).

Nor does this flow write `x_bst_startuptrk_founder`, `x_bst_startuptrk_executive` or `x_bst_startuptrk_jobposting`. Those three belong to [`03-flow-linkedin-ingestion.md` (planned)](03-flow-linkedin-ingestion.md). The split is stated here as a build mechanic; the decision is recorded in [`../../../docs/decisions/DECISION_LOG.md` (planned)](../../../docs/decisions/DECISION_LOG.md).

### 6.2 — The upsert key per entity

| Entity | Lookup | Behaviour |
| --- | --- | --- |
| **Startup** | `IngestionMapper.findExistingStartup(name, headquarters_location)`, case-insensitively, using the same key as cleaning rule 2. | Exactly one match updates it. No match inserts. **More than one match is an ambiguity failure**: the record is not written, and the reason logged ends `is ambiguous`. |
| **Investor** | `IngestionMapper.findExistingInvestor(name)` — **name only**, with no location component. | Exactly one match updates it. No match inserts. More than one match is an ambiguity failure. |
| **FundingRound** | **None. Every accepted funding round is inserted.** | There is no existing-record lookup for this table, so re-ingesting the same payload inserts a second round. The natural key used for log correlation is the startup followed by the round date. |
| **Participant row** | `IngestionMapper.linkParticipants(run_id, roundId, investorIds)` reads the existing rows for that round first. | Only missing `funding_round` + `investor` pairs are inserted, so the call is idempotent. A failed insert calls `IngestionLogger.skipRecord()` with the record type `round_investor_link` and the reason `join row insert failed`. |

Because the funding-round table has no upsert key, do not run this flow repeatedly against the same live payload or the same staging batch expecting idempotence. The staging path is protected by the `import_state` transition — a row that has been processed is no longer `pending` and is never re-read — but the live path is not.

### 6.3 — Lead investor versus participating investors

These are two different mechanisms and both must be written.

- **`lead_investor` is a first-class reference column on `x_bst_startuptrk_fundinground`.** It holds exactly one investor and is set directly on the funding-round record.
- **Participating investors are materialised as rows of `x_bst_startuptrk_m2m_round_investor`.** That join table is authoritative for participation. Each row carries a mandatory `funding_round` reference and a mandatory `investor` reference, both cascading on delete.
- **`participating_investors` on the funding round is a derived, read-only projection.** Do not write it. It carries `read_only` true and is refreshed by the business rule on the join table. The mapper's write allowlist excludes it, so an attempt to set it from an ingestion path is dropped rather than applied.

An investor that both led a round and participated in it appears in both places. That is correct, and the `portfolio_count` derivation counts the company once regardless; see [`../data-model.md`](../data-model.md).

### 6.4 — Business rules must run

**Every write this step makes must run business rules.** Two of the three business rules maintain the derived `x_bst_startuptrk_investor.portfolio_count` column through `InvestorPortfolioService`:

| Business rule | Table | When |
| --- | --- | --- |
| `Recalculate investor portfolio on funding round` | `x_bst_startuptrk_fundinground` | After insert, update and delete. On an update it recalculates **both** the previous and the new `lead_investor`, and handles a change to the round's `startup`. |
| `Recalculate investor portfolio on round investor link` | `x_bst_startuptrk_m2m_round_investor` | After insert, update and delete. It also refreshes the derived `participating_investors` projection on the affected funding round. |
| `Trim and validate startup` | `x_bst_startuptrk_startup` | Before insert and update. |

Use ordinary `GlideRecord` `insert()` and `update()`. **Do not call `setWorkflow(false)`, and do not disable business rules on any import path this flow uses.** If business rules are suppressed during a write, `portfolio_count` silently drifts — see [Operational warnings](#operational-warnings).

After any **bulk** load, invoke `InvestorPortfolioService.recalculateAll()` from a background script. It reads the graph in two passes and writes only the investors whose stored count differs, so it costs nothing on an already-correct table and returns the number of investors it wrote.

### 6.5 — Step inputs

| Input | Value |
| --- | --- |
| `run_id` | Data pill: **Step 1 → run_id**. |
| `cleaned` | Data pill: **Step 5 → cleaned**. |

### 6.6 — Step outputs

| Output variable | Type | Meaning |
| --- | --- | --- |
| `written_count` | Integer | Records inserted or updated. |
| `skipped_count` | Integer | Records skipped by the step-7 contract. |
| `links_written` | Integer | Participant rows inserted. |

### 6.7 — The step script

```javascript
(function execute(inputs, outputs) {

    var logger = new IngestionLogger();
    logger.useRun(inputs.run_id);

    var mapper = new IngestionMapper();
    mapper.useLogger(logger);

    var entries = JSON.parse(inputs.cleaned || '[]');
    var written = 0;
    var links = 0;

    for (var i = 0; i < entries.length; i++) {

        var entry = entries[i];

        try {
            // Resolve the startup and investor references before writing.
            var resolved = mapper.resolveReferences(inputs.run_id,
                entry.record_type, entry.data);

            if (!resolved.ok) {
                entry.state = 'rejected';
                entry.reason = resolved.reason;
                logger.rejectRecord(inputs.run_id, entry.record_type,
                    entry.identifier, resolved.reason);
                mapper.writeStagingState(entry);
                continue;                      // step 7: skip, then continue
            }

            var result = mapper.upsert(inputs.run_id, entry.record_type,
                                       resolved.data, resolved.participants);

            if (result.ok) {
                written++;
                entry.sys_id = result.sys_id;
                entry.state = 'processed';

                if (entry.record_type === 'funding_round' &&
                    resolved.participants.length) {
                    links += mapper.linkParticipants(inputs.run_id,
                        result.sys_id, resolved.participants).linked;
                }
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
    outputs.links_written = links;

    gs.info('[x_bst_startuptrk.ingestion] event="batch_written" run="' +
        inputs.run_id + '" written="' + written +
        '" links="' + links +
        '" skipped="' + counts.skipped + '"');

})(inputs, outputs);
```

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
| 6 | `batch_written` | `run`, `written`, `links`, `skipped`. |
| 7 | `batch_reconciled` | `run`, `incoming`, `processed`, `rejected`, `skipped`, `duplicates`, `reconciled`. |

Step 3 writes no line of its own; its outcome is carried by step 4's `source_resolved`, and a failed live call is recorded by `IngestionLogger.warn()`. Step 8 writes no line of its own either; its record is the `run_summary` in the table above.

`IngestionLogger` scrubs person and free-text values out of every line it writes, so a log record identifies a failing record by an opaque reference rather than by name, e-mail address or URL. **Do not add your own `gs.log` calls carrying record values** to work around that, and do not add step lines beyond the six above — the `run` member is the only correlation key any of them needs.

### 7.3 — Cleaning-rule outcomes are expected behaviour, not errors

This distinction is what makes the criterion-4 evidence readable.

- A record **rejected** by rule 4 for a missing mandatory field, **rejected** for a refused or over-length value, or **rejected** by rule 2 as a within-batch duplicate, is the cleaning rules working as specified. It increments `rejected` or `duplicates`. **It is not an unhandled error and does not count as one.**
- A value **left unwritten** by rule 3 because its choice list declares no `Other` member increments `unmatched`. **It is not an error either**, and the record it belongs to is still written.
- A record **skipped** by `skipRecord()` is an operational failure — a write that would not complete, a join row that would not insert. It increments `skipped` and is emitted at **error** severity.

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

### 7.6 — Step outputs

| Output variable | Type | Meaning |
| --- | --- | --- |
| `processed` | Integer | Records written. |
| `rejected` | Integer | Rule-4, refusal and over-length rejections. |
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
    outputs.rejected = toInt(inputs.rejected_count);
    outputs.skipped = toInt(inputs.skipped_count);
    outputs.duplicates = toInt(inputs.duplicate_count);

    // Unmatched choice values are logged per record; they never reject a record,
    // so they are reported from the accepted set rather than added to the total.
    outputs.unmatched = toInt(inputs.accepted_count) - outputs.processed;

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
| `run` | The run identifier, which begins `crunchbase-`. |
| `provenance` | `live` or `fallback`. |
| `processed` | Records written. |
| `rejected` | Rule-4, refusal and over-length rejections. |
| `skipped` | Operational skips. |
| `duplicates` | Rule-2 within-batch duplicates. |
| `unmatched` | Rule-3 values that matched no choice member. |
| `events_dropped` | Events discarded because the run exceeded the logger's event ceiling. |

The property write happens **before** the log record and is independent of it, so the provenance property is updated even when the log severity threshold would suppress the summary line. The guard of step 1 reads the **log record**, not the property, which is why the severity threshold matters to the cadence; see [Operational warnings](#operational-warnings).

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
| `IngestionMapper.ingest(run_id, source_system, provenance, rows)` | The live path. Cleans, deduplicates at batch scope, resolves references, upserts, links participants, stamps staging state, and finishes by calling `IngestionLogger.writeRunSummary()`. |
| `IngestionMapper.ingestStaging(run_id, source_system, import_run, provenance)` | The fallback path. Applies the staging query of [4.4](#44--the-staging-query) itself, then does everything `ingest()` does. |

A flow may call one orchestrator in place of the four separate steps. If you build it that way, **steps 5, 6, 7 and 8 remain the four phases that call performs**, each still observable in the log through the events of [7.2](#72--every-log-record-this-flow-can-write), and every statement in those four steps still applies.

Choose between the two constructions on this basis:

| | Separate steps 5 to 8 | One orchestrator call |
| --- | --- | --- |
| Per-phase counters visible as step outputs in the execution detail | **Yes** | No |
| Run summary carries the complete batch counters | No — zeros; read step 7 instead | **Yes** |
| Number of `IngestionLogger` instances | One per step | **One for the whole batch** |
| Cleaning, deduplication, reference resolution, upsert, participant linking, staging-state stamping, run summary | All present | All present |

The orchestrator is the construction to use when the criterion-4 evidence must be readable from the single `run_summary` record, which is the normal case. Both constructions honour every statement in steps 5 through 8; they differ only in where the totals are read from, for the reason given in [7.4](#74--counters-accumulate-on-a-logger-instance-not-globally).

```javascript
// The orchestrator construction, replacing the separate steps 5 to 8.
(function execute(inputs, outputs) {

    var logger = new IngestionLogger();
    var mapper = new IngestionMapper();
    mapper.useLogger(logger);

    var outcome;
    if (inputs.provenance === 'live') {
        outcome = mapper.ingest(inputs.run_id, 'crunchbase', 'live',
                                JSON.parse(inputs.rows || '[]'));
    } else {
        // Applies the staging query of 4.4 itself; no import_run for a scheduled run.
        outcome = mapper.ingestStaging(inputs.run_id, 'crunchbase', '', 'fallback');
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
| **Starting on** | any time on or after today | Pick a whole hour so the executions are easy to find in the log. |
| **Time zone** | the instance default | The guard compares elapsed hours, so the zone does not affect the cadence. |

4. Click **Done**.

The hourly repeat is **not** the ingestion cadence. The ingestion cadence is the property `x_bst_startuptrk.ingestion.cadence_hours`, enforced by the guard of step 1. With the shipped cadence of 24 hours, the flow executes roughly twenty-four times a day and does work roughly once. **Every one of those executions must exit before doing any work unless it passes the guard** — that is what step 1's `If` block guarantees, and it is why the runbook defines a scheduled run as a guard-passing execution.

To change the cadence, edit the property. Do not edit the trigger, and do not edit the guard.

## Activation

1. Confirm every precondition in [Preconditions](#preconditions) still holds, and in particular that precondition 6 holds — **both aliases tested green**.
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

Then check each step against the table below.

| Step | What to confirm in the execution detail |
| --- | --- |
| 1 | `run_id` begins `crunchbase-`. `cadence_hours` is between 6 and 48. `proceed` is `true`. A `cadence_guard` line appears in the log. |
| 2 | `source_mode` is `fallback` and `attempt_live` is `false`. |
| 3 | **Skipped**, because it sits inside the `attempt_live` block. |
| 4 | `provenance` is `fallback`. `row_count` matches the number of `pending` rows on `x_bst_startuptrk_ingest_staging` with `source_system` `crunchbase`. A `source_resolved` line appears. |
| 5 | `accepted_count` plus `rejected_count` plus `duplicate_count` accounts for every incoming row. A `batch_cleaned` line appears. Any unmatched choice value has produced a `choice_unmatched` line. |
| 6 | `written_count` is greater than zero. Open `x_bst_startuptrk_startup`, `x_bst_startuptrk_investor` and `x_bst_startuptrk_fundinground` and confirm the records exist. Open `x_bst_startuptrk_m2m_round_investor` and confirm `links_written` participant rows exist. Confirm `x_bst_startuptrk_investor.portfolio_count` is non-zero for an investor that led or joined a round — that proves the business rules ran. |
| 7 | The five counters are reported separately, never folded together. A `batch_reconciled` line appears and `reconciled` is `true`, meaning every incoming row is accounted for. |
| 8 | `recorded` is `true`. `x_bst_startuptrk.ingestion.last_run_provenance` now reads `fallback`. A `run_summary` line appears carrying all eight members of [8.3](#83--what-gets-written). On the separate-step build its counter members are zeros by design; read the totals from step 7. |

Then confirm the guard works in the other direction: run the flow a second time immediately. Step 1 must return `proceed` `false`, steps 2 through 8 must not run, and no second `run_summary` line must appear.

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

The single decisive test is the **run summary**: a no-op writes none. When collecting criterion-4 evidence, filter the application log to the source `x_bst_startuptrk`, search for `event="run_summary"` together with `run="crunchbase-`, and take the three most recent records. Each is one scheduled run, and each carries its own provenance. Ignore the `cadence_guard` lines whose outcome is `no_op` entirely.

The same rule is stated in [`../deployment-runbook.md`](../deployment-runbook.md#what-counts-as-a-scheduled-run), which is authoritative for it.

## Operational warnings

These three are not rationale. They describe failures that are easy to cause and hard to see.

### The alias binding is by name, and a mismatch fails at run time

**A name mismatch does not fail at build time.** A flow that names an alias which does not exist, or names it with a typographic error, saves without complaint and activates without complaint. Nothing in the Flow Designer interface reports the fault. It surfaces only when the flow executes — and because this is a scheduled flow, it can fail silently on its cadence until someone reads the flow execution log.

Three consequences:

1. **Copy the alias name from guide 01; never retype it.**
2. **Watch the two separators.** It is `x_bst_startuptrk.crunchbase_api` — a dot after the scope, an underscore inside the alias name. Not `x_bst_startuptrk_crunchbase_api`, and not `x_bst_startuptrk.crunchbase-api`.
3. **On the [3c](#3c--the-alternate-path-a-scoped-script-step) path the failure is quieter still**, because `getConnectionInfo` returns `null` rather than raising. The script tests for `null` explicitly and writes `connection alias did not resolve`; without that test the step would fail on a property access with no useful message. The same `null` is returned when the alias exists but the flow's **Run As** identity cannot read it, which is why the flow runs as **System User**.

### A flow saved before its alias tests green will fail on first execution

Precondition 6 requires the guide 01 connection test to have passed for **both** aliases before this flow is saved. That test is the only thing that proves the credential behind the alias is present and usable. Building the flow first and testing the alias afterwards inverts the dependency and produces a flow whose first scheduled execution fails for a reason the flow itself cannot report.

At the time of writing, neither alias holds a live credential on the target instance. Until they do, run this flow with `x_bst_startuptrk.ingestion.source_mode` set to `fallback`, and label every result `fallback validated` and never `live validated`.

### If business rules are suppressed during a write, `portfolio_count` silently drifts

`x_bst_startuptrk_investor.portfolio_count` is a **stored** integer maintained by the two business rules of [6.4](#64--business-rules-must-run). Nothing recomputes it on read. Any write to `x_bst_startuptrk_fundinground` or `x_bst_startuptrk_m2m_round_investor` that bypasses business rules — `setWorkflow(false)` in a script, or an import transform with rule execution disabled — leaves the stored count stale for every investor touched by that write. **There is no error, no warning and no log record.** The column simply disagrees with the data.

Two obligations follow. Never suppress business rules on an ingestion or import path that writes either table. And after any bulk load, invoke `InvestorPortfolioService.recalculateAll()` from a background script; it writes only the investors whose count differs and returns how many it corrected.

## Legacy provenance

This flow replaces the following legacy constructs. **Nothing below is ported.** The four cleaning rules of [step 5](#53--the-four-cleaning-rules) come from the prompt alone, and **there is no legacy pandas code to replicate** — the legacy implementation contradicts every one of the four rules.

### The scheduler

| Citation | What is there | What replaces it |
| --- | --- | --- |
| [`src/data_collection/scheduler.py:L13-L17`](../../../src/data_collection/scheduler.py) | **Five hard-coded hour intervals: 24, 24, 12, 6, 48.** Their minimum and maximum are exactly the cadence bounds this application enforces. | All five collapse into the single clamped property `x_bst_startuptrk.ingestion.cadence_hours`, read through `AppProperties.getCadenceHours()`. |

That module also starts five threads and then loops forever with no shutdown path, its own trailing notes recording the graceful-shutdown mechanism as outstanding work. The scheduled trigger of this flow needs no equivalent.

### The Crunchbase integrator

| Citation | What is there | What replaces it |
| --- | --- | --- |
| [`src/data_collection/api_integrators/crunchbase_integrator.py:L10`](../../../src/data_collection/api_integrators/crunchbase_integrator.py) | The base URL as a module constant. | The property `x_bst_startuptrk.crunchbase.base_url`, carried on the alias's connection record. |
| `:L11` | A module-level `API_KEY` constant holding the credential in source. | The credential behind `x_bst_startuptrk.crunchbase_api`, resolved at run time and never present in the flow, a step input, a script body or the Update Set. |
| `:L22`, repeated at `:L41` and `:L60` | The key passed as a **`user_key` query parameter** on every call. | Nothing. The alias supplies the credential, and [3a](#3a--the-primary-path-the-flow-designer-rest-step) sets **no** query parameters. |
| `:L27-L30` and `:L49` | The organisation response read from **`data.properties`**. | `IngestionMapper.unwrapLive()`, which returns the single object under `properties` as a one-element list. |
| `:L68` | The funding-rounds response read from **`data.items`**. | `IngestionMapper.unwrapLive()`, which returns the array it finds under `items`. |

The two resource-path shapes of [3a.2](#3a2--the-resources-called) are the shapes those three call sites use.

### The cleaner

Every one of these contradicts a rule this flow enforces, which is why none is carried forward.

| Citation | What is there | The rule it contradicts |
| --- | --- | --- |
| [`src/data_collection/data_cleaning/startup_cleaner.py:L57`](../../../src/data_collection/data_cleaning/startup_cleaner.py) and `:L60` | Deduplication on **name + website**. | Rule 2, which deduplicates on `name` + `headquarters_location`, case-insensitively. |
| `:L86` | Missing values filled with the string **`"Unknown"`**. | Rule 4, which rejects a record missing a mandatory field rather than inventing a value for it. |
| `:L90` | **Median imputation of missing numeric values** — the exact opposite of rejecting records that lack mandatory fields. | Rule 4. |
| `:L171-L176` with `:L183-L184` | A **four-entry placeholder industry dictionary** whose values match **none** of the binding choice lists, with everything else coerced to `"Other"`. | Rule 3, whose targets are the choice values of [`../data-model.md`](../data-model.md), reached through the two passes of [5.3](#53--the-four-cleaning-rules). |

The legacy enumerations are **replaced, not translated**, so no old-to-new mapping table exists and none is to be created. The per-source translation of pass one maps **Crunchbase's** vocabulary onto the target choice values, which is a different mechanism serving a different purpose.

## Build verification

Do not sign this guide off until every line below is true.

| # | Check |
| --- | --- |
| 1 | One flow named `Crunchbase Ingestion` exists in the `x_bst_startuptrk` scope, with **Run As** `System User`. |
| 2 | The trigger is **Scheduled**, set to **repeat hourly**. |
| 3 | All **eight** steps are present and in order, with steps 2 through 8 inside the `If` block controlled by step 1's `proceed` output. |
| 4 | Exactly **one** of [3a](#3a--the-primary-path-the-flow-designer-rest-step) or [3c](#3c--the-alternate-path-a-scoped-script-step) is built, and the [3b](#3b--the-pre-flight-check-that-chooses-the-path) outcome is recorded here: `______`. |
| 5 | The alias name reads `x_bst_startuptrk.crunchbase_api` exactly, at every occurrence in the flow. |
| 6 | No IntegrationHub spoke is installed, activated, referenced or used. |
| 7 | **No key, secret, token or password appears** in the flow record, any flow input, any step input, any script body or any test payload. |
| 8 | The flow reads `x_bst_startuptrk.ingestion.cadence_hours`, `x_bst_startuptrk.ingestion.source_mode` and `x_bst_startuptrk.crunchbase.base_url`, and writes `x_bst_startuptrk.ingestion.last_run_provenance`. It reads no other property except `x_bst_startuptrk.logging.level` by way of `IngestionLogger`. |
| 9 | The flow writes `x_bst_startuptrk_startup`, `x_bst_startuptrk_investor`, `x_bst_startuptrk_fundinground` and `x_bst_startuptrk_m2m_round_investor`, and **no other table**. It does not write `x_bst_startuptrk_newsarticle`. |
| 10 | The flow reads `x_bst_startuptrk_ingest_staging` on the fallback branch, with the query of [4.4](#44--the-staging-query) and **no `record_type` condition**. |
| 11 | The flow calls `AppProperties`, `IngestionMapper`, `IngestionLogger` and `InvestorPortfolioService`, and re-implements none of their logic. |
| 12 | No write uses `setWorkflow(false)`, and the three business rules of [6.4](#64--business-rules-must-run) are active. |
| 13 | The manual run of [Verification](#verification--one-manual-run) passed every row of its table, and the immediate second run returned `proceed` `false` with no run summary. |
| 14 | `x_bst_startuptrk.ingestion.source_mode` has been set back to `live`. |
| 15 | The flow is **activated**. |

Criterion 4 in [`../validation-checklist.md` (planned)](../validation-checklist.md) is satisfied separately, by three consecutive guard-passing runs with zero unhandled errors and the provenance of each one recorded.

## Related documents

| Document | Relationship |
| --- | --- |
| [`01-connection-credential-aliases.md`](01-connection-credential-aliases.md) | Establishes `x_bst_startuptrk.crunchbase_api`, which [step 3](#step-3--call-crunchbase-through-the-alias) binds to by name. Must be complete first. |
| [`03-flow-linkedin-ingestion.md` (planned)](03-flow-linkedin-ingestion.md) | The identical eight-step skeleton for LinkedIn. Steps 1, 2, 4, 5, 7 and 8 match this guide; only the alias, base URL and target tables differ. |
| [`04-service-portal-pages-and-widgets.md`](04-service-portal-pages-and-widgets.md) | The portal that reads the records this flow writes. |
| [`06-staging-table-csv-import.md` (planned)](06-staging-table-csv-import.md) | Loads `x_bst_startuptrk_ingest_staging`, which [step 4](#step-4--fall-back-to-the-staging-table) reads. |
| [`05-atf-test-suites.md` (planned)](05-atf-test-suites.md) | The flow test that exercises this flow and applies the `fallback validated` / `live validated` label. |
| [`../manual-build-instructions.md` (planned)](../manual-build-instructions.md) | The build order and the Update Set versus manual-build split rule. |
| [`../data-model.md`](../data-model.md) | The tables, columns, choice values, cascade rules and the `portfolio_count` derivation. |
| [`../access-control.md`](../access-control.md) | The role and ACL posture of the four tables this flow writes. |
| [`../api-reference.md`](../api-reference.md) | The Script Include call graph and the full property inventory. |
| [`../validation-checklist.md` (planned)](../validation-checklist.md) | Criterion 4, which reads [step 8](#step-8--write-the-run-summary-and-the-provenance-marker). |
| [`../validation-gates.md`](../validation-gates.md) | The sixteen post-commit gates of precondition 4, and the eleven-gate core of precondition 5. |
| [`../deployment-runbook.md`](../deployment-runbook.md) | Authoritative for [what counts as a scheduled run](../deployment-runbook.md#what-counts-as-a-scheduled-run). |
| [`../gaps-and-flags.md` (planned)](../gaps-and-flags.md) | Records the runtime-configurable schedule interval and the NewsArticle ingestion exclusion. |
| [`../../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml`](../../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml) | **Authoritative** for every identifier cited in this guide. |
| [`../../sample-data/README.md`](../../sample-data/README.md) | The column contract of the fallback dataset, and the procedure for forcing the fallback path. |
| [`../../../docs/decisions/DECISION_LOG.md` (planned)](../../../docs/decisions/DECISION_LOG.md) | Every "why" behind this flow, including the three deviations named at the top of this guide. |
