# Manual build 05 — Automated Test Framework test suites — `x_bst_startuptrk`

This guide builds **10 Automated Test Framework test suites containing 36 tests**, by hand, on the instance, through the Automated Test Framework modules of the ServiceNow scoped application `x_bst_startuptrk`. It specifies every suite, every test within it, and every step within every test, naming the exact ATF step configuration used at each step and the exact input values that step is given. The suites cover the seven entity tables, the twenty-one premium-field-by-role access-control outcomes, the six REST resources including the nested sub-resource, and the two scheduled ingestion flows. It then specifies the three techniques the evidence depends on — impersonation, the deterministic rate-limit trip, and provenance labelling — how to assemble the suites into a runnable set, how to read the results, and which result artifacts the operator records as evidence.

**Authority.** The frozen prompt and the Agent Action Plan are authoritative for all application content. The Update Set XML at [`../../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml`](../../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml) is the authoritative source for every table name, column name, column type, mandatory flag, choice value, role name, ACL name, Script Include class name, method name, REST operation path and system-property key cited below; the identifiers used here match those records character for character. [`../access-control.md`](../access-control.md) is authoritative for the twenty-one role-by-field outcomes, and [`../api-reference.md`](../api-reference.md) for the six resource paths, the pagination contract and the exact error bodies. This guide agrees with all three and introduces no third spelling. No variant spelling of any identifier is valid.

This document carries **no rationale**. It states what to build and how to build it, suite by suite, test by test, step by step. Every decision behind these suites, every alternative considered and every risk each carries is recorded in [`../../../docs/decisions/DECISION_LOG.md`](../../../docs/decisions/DECISION_LOG.md), which is the single source of truth for "why". Three points in this procedure depart from a literal reading of the requirements — the three impersonated users being **created at run time by test setup steps** rather than shipped in the Update Set, the rate-limit counter row being **pre-seeded at the configured budget** so a single request trips the limit, and the **two separate provenance surfaces** that keep an ATF result label distinct from a scheduled run-summary record. Each is stated below as a build mechanic and cross-referenced to that log. None is argued here.

Operational warnings **are** in scope for this guide and are marked as such. The **eleven** warnings under [Operational warnings](#operational-warnings) — `W1`, `W2`, `W3`, `W4`, `W4b`, `W5`, `W6`, `W6b`, `W6c`, `W7` and `W8` — are load-bearing and must not be skipped. **Four** of them, `W1`, `W2`, `W6` and `W6c`, describe failures that are completely silent, in the sense that every test reports `success` while the property under test was never exercised at all; `W4b` is silent until the run in which it is not.

## Referenced documents

This guide is executable on its own. Every suite, every test, every step, every input value, the assembly order, the run procedure and the verification are stated here in full. An operator needs no other file to build and run the suites.

**Every document linked from this guide is delivered and readable**, so no link is a forward reference; each one is an in-scope artifact of this deliverable package. Nothing in this guide depends on reading another document first.

| Document | What this guide takes from it |
| --- | --- |
| [`../../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml`](../../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml) | **Authoritative** for every identifier this guide cites: the ten table names, the fifty-three entity columns and their mandatory flags, the sixty-three entity choice values, the three role names, the seven field-level ACL names, the eight Script Include class names and their method signatures, the thirty-one REST operation paths, and the eleven system-property keys. |
| [`../access-control.md`](../access-control.md) | The 3 x 7 role-by-field matrix this guide asserts cell by cell, the secured read path, the omit-not-nulled rule, and the impersonation requirement together with the reviewer entry that owns it. |
| [`../api-reference.md`](../api-reference.md) | The six logical resources and the nested sub-resource, the physical base path, the pagination contract and its envelope members, the exact 429 and 500 bodies, the result ordering per operation, and the Script Include call graph that serves as the rename-impact list. |
| [`../data-model.md`](../data-model.md) | The fifty-three columns with types and lengths, the fourteen mandatory columns, all eleven choice columns and their members, the `Investor.type` asymmetry, and the type-refusal rules the CRUD suites assert against. |
| [`../validation-gates.md`](../validation-gates.md) | The eleven required post-commit gates of precondition 4, and the non-normative diagnostics `GATE-SEC-01` and `GATE-SEC-02`, whose recorded table posture is why every record step in this guide must be built inside the application scope. Neither is a precondition of this guide: they are read for what they record, and their outcome gates nothing here. |
| [`../deployment-runbook.md`](../deployment-runbook.md) | The import sequence that commits the Update Set, the assertion of the ATF prerequisite before import, and the definition of [what counts as a scheduled run](../deployment-runbook.md#what-counts-as-a-scheduled-run). |
| [`02-flow-crunchbase-ingestion.md`](02-flow-crunchbase-ingestion.md) | The `Crunchbase Ingestion` flow under test: its eight steps, its cadence guard, its run-identifier format, its mandatory sets and its run-summary write. |
| [`03-flow-linkedin-ingestion.md`](03-flow-linkedin-ingestion.md) | The `LinkedIn Ingestion` flow under test, and the shared startup deduplication key that lets a LinkedIn founder attach to a Crunchbase startup. |
| [`04-service-portal-pages-and-widgets.md`](04-service-portal-pages-and-widgets.md) | The five portal pages and eight widgets, and the three impersonated users this guide creates that the portal walkthrough also requires. |
| [`06-staging-table-csv-import.md`](06-staging-table-csv-import.md) | The post-load state of `x_bst_startuptrk_ingest_staging` and its six `import_run` tokens — which suite 10 **avoids**, seeding its own test-owned token instead. That load supplies the scheduled-run evidence of criterion 4, not this guide's fixtures; see [Why guide 06 runs before this one](#guide-06-runs-before-this-one-and-this-guide-reads-none-of-its-rows). |
| [`01-connection-credential-aliases.md`](01-connection-credential-aliases.md) | The two Connection and Credential Aliases, and the alias state that determines whether a flow test is labelled `live validated` or `fallback validated`. |
| [`../validation-checklist.md`](../validation-checklist.md) | Success criteria 2, 3 and 4, whose evidence these suites produce. |
| [`../manual-build-instructions.md`](../manual-build-instructions.md) | The build order for the package as a whole, and the split rule between Update Set XML and manual build. |
| [`../gaps-and-flags.md`](../gaps-and-flags.md) | The requirements with no clean platform equivalent, including the administrator ACL override recorded as a verification-procedure gap. |
| [`../../../docs/decisions/DECISION_LOG.md`](../../../docs/decisions/DECISION_LOG.md) | The single destination for every "why". |

## Position in the build order

This is **guide 05 of six**, and it is **step 6** of the execution order below — the **last** step. The execution order is **not** the filename order: guide **06** runs before this one. Guides 01, 02, 03, 04 and 06 must all be complete before this guide begins. The order is stated in full in [`../manual-build-instructions.md`](../manual-build-instructions.md); it is repeated here so this guide can be run without it.

| Step | Guide | Why it sits here |
| --- | --- | --- |
| 1 | [`01-connection-credential-aliases.md`](01-connection-credential-aliases.md) | The two Connection and Credential Aliases the ingestion flows bind to by name. Nothing downstream can authenticate without them. |
| 2 | [`02-flow-crunchbase-ingestion.md`](02-flow-crunchbase-ingestion.md) | The `Crunchbase Ingestion` flow, which references `x_bst_startuptrk.crunchbase_api` by name. |
| 3 | [`03-flow-linkedin-ingestion.md`](03-flow-linkedin-ingestion.md) | The `LinkedIn Ingestion` flow, which references `x_bst_startuptrk.linkedin_oauth` by name. |
| 4 | [`04-service-portal-pages-and-widgets.md`](04-service-portal-pages-and-widgets.md) | The portal, theme, five pages and eight widgets. |
| 5 | [`06-staging-table-csv-import.md`](06-staging-table-csv-import.md) | The staging-table CSV load, which puts rows into `x_bst_startuptrk_ingest_staging`. |
| **6** | **This guide** | **The Automated Test Framework suites, last, because they exercise everything the five preceding guides build.** |

The ordering is a factual dependency, not a preference. Each of the four suite groups reads an artifact that an earlier guide creates:

| Suite group | Depends on | Built by |
| --- | --- | --- |
| The seven table-CRUD suites | The seven entity tables and their dictionary columns, mandatory flags and choice lists | The committed Update Set |
| The field-ACL suite | The seven field-level read ACLs and the three roles | The committed Update Set |
| The REST suite | The thirty-one Scripted REST operations, the two REST endpoint ACLs and the rate-limit counter table | The committed Update Set |
| The two flow tests | The two ingestion flows, their ten published actions, and the two credential aliases with their branch recorded | Guides 01, 02 and 03 |

### Guide 06 runs before this one, and this guide reads none of its rows

**The two tests in suite 10 do not read the rows guide 06 loads, and this guide does not depend on them for its fixtures.** Every fixture those two tests act on is written by their own step 30, into `x_bst_startuptrk_ingest_staging`, under a **test-owned `import_run` token** that no guide-06 row carries. Two mechanics keep the two row sets apart, and both are build rules rather than observations: a guide-06 row is advanced to `processed` by guide 06's own transform step, and `IngestionMapper.ingestStaging()` reads only rows in state `pending`. **Do not point a test at a guide-06 row, and do not seed a test row under a guide-06 token.** `D-065` carries the decision.

Guide 06 nonetheless runs first, for a different and equally factual reason:

| What needs guide 06's rows | Why |
| --- | --- |
| **Success criterion 4's three consecutive guard-passing scheduled runs, per flow** | Those are real scheduled executions of the flow record, outside any test transaction. They read whatever `pending` rows the staging table holds, so an empty table produces three clean runs that processed nothing and demonstrate no cleaning rule. This evidence is collected by [`../validation-checklist.md`](../validation-checklist.md), **not** by this guide. |
| **The data-bearing rerun of the fallback branch in guides 02 and 03** | Both guides require a rerun over loaded rows after guide 06 completes, because their pre-activation check runs against an empty table and proves wiring only. |
| **This guide's precondition 6** | Not for fixtures — for **environment consistency**. A staging table in its post-guide-06 state is the state the flows were validated in, and a run of suite 10 against a half-loaded table produces per-record outcomes that are harder to read against the counts published below. |

So the dependency is real but it is **not** a fixture dependency of these 36 tests. State it that way wherever it appears: **guide 06 supplies the scheduled-run and fallback acceptance evidence; suite 10 supplies its own isolated fixtures.** [`06-staging-table-csv-import.md`](06-staging-table-csv-import.md) and [`../manual-build-instructions.md`](../manual-build-instructions.md) state the same split.

### Why this guide exists rather than more Update Set XML

Only tables carrying the update-synch attribute are captured into `sys_update_xml` records, and adding that attribute to a table that lacks it out of the box is unsupported. Tests, test steps, test suites and their ordered membership are built through the platform's own interface and sit outside the captured set, which is why the delivered Update Set contains **zero** test records — no `sys_atf_test`, no `sys_atf_step`, no `sys_atf_test_suite` and no `sys_atf_test_suite_test`. [`../manual-build-instructions.md`](../manual-build-instructions.md) owns the split rule for the package as a whole.


## Preconditions

Do not begin this guide until every item below holds.

| # | Precondition | How to confirm |
| --- | --- | --- |
| 1 | The Update Set has been uploaded and has reached the `loaded` state. | The `sys_remote_update_set` record shows `state` `loaded`. |
| 2 | The preview has completed with an **empty error-type problem set**. | A read of `sys_update_preview_problem` filtered to this remote update set and `type=error` returns an empty `result` array. Warnings are logged and do not block. |
| 3 | The Update Set has **committed**. | The `sys_remote_update_set` record shows `state` `committed`. |
| 4 | **All eleven required post-commit gates have passed.** | Run the eleven required gates in [`../validation-gates.md`](../validation-gates.md) — the seven entity-table reads `GATE-TBL-01` through `GATE-TBL-07`, the three role-record gates `GATE-ROLE-01` through `GATE-ROLE-03`, and the one scope-record gate `GATE-SCOPE-01` — and record `pass` for all eleven in that document's required-gate evidence table. The aggregate pass condition is `11 of 11`; there is no partial pass, and no required gate may be skipped, deferred or waived. |
| 5 | **ATF execution is enabled on the instance and you hold a test-designer role.** | See [Instance prerequisite: ATF execution must be enabled](#instance-prerequisite-atf-execution-must-be-enabled) immediately below. This is the hard prerequisite of this guide. Without it **every suite here is unrunnable and the coverage gate cannot be evaluated at all**. |
| 6 | Guides 01, 02, 03, 04 and 06 are complete. | Both credential aliases have a recorded branch, **all ten ingestion custom actions read `Published`** and both flows are **Active**, the portal resolves, and guide 06's load and transform have both run so `x_bst_startuptrk_ingest_staging` is in its published post-load state. Guides 02 and 03 each publish five actions; the counts are in [`../manual-build-instructions.md`](../manual-build-instructions.md). **Suite 10 does not read guide 06's rows** — it seeds its own, under a test-owned `import_run` token — so this precondition is about environment consistency and about criterion 4's separate evidence, not about this guide's fixtures. See [Why guide 06 runs before this one](#guide-06-runs-before-this-one-and-this-guide-reads-none-of-its-rows). |
| 7 | The seven entity tables carry all **fifty-three** dictionary columns. | `GATE-COL-01` recorded `pass`. Column counts per table: `x_bst_startuptrk_startup` 12, `x_bst_startuptrk_founder` 6, `x_bst_startuptrk_executive` 6, `x_bst_startuptrk_investor` 6, `x_bst_startuptrk_fundinground` 8, `x_bst_startuptrk_jobposting` 9, `x_bst_startuptrk_newsarticle` 6. |
| 8 | The **eight** Script Includes this guide calls into are on the instance. | `sys_script_include` carries `AppProperties`, `RestQueryHelper`, `RestResponseBuilder`, `RateLimitService`, `StartupSearchService`, `InvestorPortfolioService`, `IngestionLogger` and `IngestionMapper`, all in the `x_bst_startuptrk` scope. Eight is the whole delivered service layer; there is no ninth. |
| 9 | The three business rules are on the instance and **active**. | `sys_script` carries `Trim and validate startup`, `Recalculate investor portfolio on funding round` and `Recalculate investor portfolio on round investor link`, all `active` true, all in the `x_bst_startuptrk` scope. |
| 10 | The rate-limit counter table exists with all **four** of its columns. | `x_bst_startuptrk_rate_limit_counter` carries `caller`, `api_resource`, `window_start` and `request_count`, and nothing else. The REST suite's 429 assertion writes to this table. |
| 11 | You hold the platform `admin` role. | Required to create the three test users, to read `sys_user_has_role`, and to reach the Automated Test Framework modules. Note this is the **platform** administrator role, which is **not** the scoped `x_bst_startuptrk.admin` role; the two are different records and both are needed. |
| 12 | You are working in the `x_bst_startuptrk` application scope. | The application picker reads **Boston Startup Tracker**. Every test and every suite this guide creates must carry that scope — see [Naming and scope conventions](#naming-and-scope-conventions), where the reason this is a build constraint rather than a preference is stated as a mechanic. |
| 13 | No other operator is running suites on this instance. | ATF serialises execution against a single runner. A concurrent run competes for the runner and for the impersonation context, and the two flow tests write to the same staging rows. |

### Capture rule for this artifact class

Only tables carrying the update-synch attribute are captured into `sys_update_xml` records, and adding that attribute to a table that lacks it out of the box is unsupported. Tests, test steps, test suites and their ordered membership are built through the platform's own interface and sit outside the captured set, which is why the delivered Update Set contains **zero** test records — no `sys_atf_test`, no `sys_atf_step`, no `sys_atf_test_suite` and no `sys_atf_test_suite_test`. [`../manual-build-instructions.md`](../manual-build-instructions.md) owns the split rule for the package as a whole.

## Instance prerequisite: ATF execution must be enabled

**This is the hard prerequisite of this guide. If ATF execution is not enabled on the instance, every one of the 10 suites below is unrunnable, no test produces a result, and the coverage gate of [Coverage gate](#coverage-gate) cannot be evaluated at all — not failed, not partially met, but unevaluable.** [`../deployment-runbook.md`](../deployment-runbook.md) asserts this prerequisite **before** the Update Set is imported, precisely so the condition is discovered before any deployment work is done rather than after.

Two things must hold. Check and set both.

**1. The runner-enabled system property must be `true`.**

| Item | Value |
| --- | --- |
| Property | `sn_atf.runner.enabled` |
| Type | `true` or `false` |
| Required value | `true` |
| Default on a new instance | `false` |
| Navigation, form | **All** > **Automated Test Framework** > **Administration** > **Properties**, then tick **Enable test/test suite execution** and click **Save**. |
| Navigation, raw | **All** > **System Properties** > **All Properties**, filter `Name` `is` `sn_atf.runner.enabled`, set **Value** to `true`, click **Update**. |

This property is **private**: a change to its value does not travel between instances in an update set or in team development. It is therefore an instance-provisioning action on every instance the suites are run against, and it is correctly **absent** from the delivered Update Set. Do not add it.

**2. You must hold a test-designer role.**

| Role | What it permits |
| --- | --- |
| `atf_test_designer` | Create and edit tests, test steps and test suites. The minimum role for building the suites in this guide. |
| `atf_test_admin` | The above, plus administering step configurations and the ATF properties. Required to set `sn_atf.runner.enabled` from the ATF **Properties** form. |

Confirm the grant at **All** > **User Administration** > **Users**, open your own user record, and read the **Roles** related list. Both roles are granted on the target instance already.

Once both hold, the **Automated Test Framework** application menu exposes the modules this guide uses:

| Module | Table | Used for |
| --- | --- | --- |
| **Tests** | `sys_atf_test` | Creating each of the 36 tests and its steps. |
| **Test Suites** | `sys_atf_test_suite` | Creating each of the 10 suites and its ordered test membership (`sys_atf_test_suite_test`). |
| **Test Results** | `sys_atf_test_result` | Reading a single test's outcome and its per-step results (`sys_atf_test_result_step`). |
| **Suite Results** | `sys_atf_test_suite_result` | Reading a suite's rolled-up outcome; the evidence artifact this guide records. |
| **Administration** > **Step Configurations** | `sys_atf_step_config` | Reading the available step configurations. This guide creates **no** new step configuration. |

**The client test runner is not required by this suite set.** Every one of the roughly 400 steps built below uses a **Server - Independent** or **Server - REST** step configuration. Not one is a client-side step, so no run here needs a browser session to drive a form, and the client runner is **not** a prerequisite: a server-only test or suite is scheduled and executed without one.

Open **All** > **Automated Test Framework** > **Run Client Test Runner** in a second browser tab **only** in the one case where it is genuinely needed — if you add a client-side step to a test in this guide, or if a run reports that it is waiting for a client test runner. A run that waits for a runner while every step is server-side is the symptom of a client-side step having been added by accident; find and remove it rather than attaching a runner to work around it. The [Build verification](#build-verification) prerequisites carry the box that confirms no client-side step exists.

## Naming and scope conventions

Apply these to every record created in this guide, without exception.

| Convention | Rule |
| --- | --- |
| Application scope | Every test and every suite is created with the application picker on **Boston Startup Tracker**, so the record carries `sys_scope` `x_bst_startuptrk`. |
| Test name | `BST <group> — <subject>`, for example `BST CRUD — startup` or `BST ACL — startup.total_funding_usd — user`. |
| Suite name | `BST <group> suite — <subject>`, for example `BST CRUD suite — startup`. |
| Description | One sentence stating what the test asserts and which requirement it satisfies. State no rationale. |
| Step order | Steps are numbered in tens (10, 20, 30, ...) so a step can be inserted later without renumbering. |
| `enforce_security` | Set **true** on every `Record Insert`, `Record Update`, `Record Query`, `Record Delete` and `Record Validation` step in this guide. This is the input that makes a record step honour ACLs; with it false, the field-ACL suite passes vacuously. |
| Failure assertions | Expressed through the step's own **Assert type** input, never by expecting the test to error. The exact choice labels are given per step below. |

**The application scope is a build constraint, not a preference.** Cross-scope `create_access`, `update_access` and `delete_access` are false on all ten tables, and the three supporting tables are additionally `package_private` with `read_access` false — the posture the non-normative diagnostics `GATE-SEC-01` and `GATE-SEC-02` record. Every suite in this guide inserts, updates or deletes records, so a test built in the **Global** scope is an out-of-scope caller, and its record steps are refused by that posture before any ACL is consulted. Where a record step is still refused after the scope is correct, the in-scope route is a **Run Server Side Script** step, which compiles in the test's own scope. The REST suite is unaffected either way, because it calls the Scripted REST API at `/api/x_bst_startuptrk/v1/` rather than the Table API — `ws_access` false is exactly why the Table API is not an option for these tables.

## Two ATF contracts every script in this guide depends on

Read both before transcribing any script. Each governs how a step reaches a value another step produced, and getting either wrong produces a test that runs and then asserts against `undefined`.

### Contract 1 — `steps()` takes a step **sys_id**, never a display order number

`steps()` resolves a **step record**, and its argument is that record's generated 32-character `sys_id`. The step's display order — the `10`, `20`, `30` this guide numbers steps by — is a separate field and is **not** an identifier. `steps('30')` therefore resolves nothing, and every property read off it is `undefined`.

**The value is generated when you create the step, so no document can contain it.** Every script below declares its step references as named constants at the top of the script, each carrying the display order it corresponds to:

```javascript
// Substitute the generated sys_id of the step at display order 30.
var STEP_30_INSERT = '';   // <- paste the sys_id here
```

Three build steps follow, and all three are mandatory:

1. **Create the steps first, in order, then fill in the constants.** A constant cannot be filled in before its step exists.
2. **Read the sys_id off the step record.** Open the step from the test's **Test Steps** related list and copy the `sys_id` from the URL, or add the **Sys ID** column to that list. The **Data pill picker** in the script editor inserts the same reference and is the less error-prone route: pick the step from the picker rather than typing anything.
3. **Leave no constant empty.** An empty constant reads as `steps('')`, which resolves nothing and produces the same `undefined` as a display number. Row 4 of [Build verification](#build-verification) is the check for this.

### Contract 2 — a **Run Server Side Script** step exposes only its two stock outputs, and no custom one

A `Run Server Side Script` step ships with exactly **two** declared outputs, `record_id` and `table`, and **you cannot add a third**. Assigning `outputs.<some new name>` inside the script does not create a value a later step can read: the assignment is discarded, and `steps(<that step>).<some new name>` is `undefined` in the consuming step. The two stock outputs are real and readable, so the rule is narrower than "nothing may be read out of one" — it is **no invented output may be read out of one**.

| Step configuration | Outputs it genuinely exposes | Read as |
| --- | --- | --- |
| **Create a User** | The created user reference | `steps(STEP_X).user` |
| **Record Insert** | The inserted record's identifier, and the table it was inserted into | `steps(STEP_X).record_id`, `.table` |
| **Send REST Request - Inbound** | The response body, status code and headers | `steps(STEP_X).response_body`, `.status_code` |
| **Record Query** | The matched record set | The step's own assert type |
| **Run Server Side Script** | **`record_id` and `table` only** — the two stock outputs, set by assigning `outputs.record_id` and `outputs.table` | `steps(STEP_X).record_id`, `.table` |

Two scripts in this guide use the stock pair deliberately, and both are marked where they appear: the run-token step of suite 10 writes the token record's identifier to `outputs.record_id` and its table to `outputs.table`, and the counter-seeding step of suite 9 writes the seeded row's identifier the same way so its cleanup step can delete exactly that row. **Every other value moved between steps uses one of the three mechanisms below.** No script in this guide assigns any other output name.

Three permitted ways to move a value between steps, in order of preference. Every script in this guide uses one of them and none invents an output name:

1. **Read the stock output of the step that produced it.** Where two script steps both need a REST response, each reads `steps(<REST step>).response_body` directly rather than one script handing a derived value to the other. This is what the pagination assertions do, and it is why a `Record Insert` step's `record_id` — not a display value — is the identity every CRUD query, validation, update and delete binds to.
2. **Declare the value as a literal constant, identically, in every script that needs it.** A resource token or a table name is fixed for the test, so every script that needs it declares the same constant. This is what the seven `api_resource` tokens of suite 9 do.
3. **Write it to a record the test creates and read it back through the stock `record_id` output.** ATF rolls back records a test creates, so a scoped record written in one step is readable in a later step of the same test and leaves nothing behind. This is the **only** mechanism that carries a value **computed at run time** — a generated run token, a captured baseline count — from one script step to another, and suite 10's run token uses it for exactly that reason.

`stepResult.setOutputMessage()` is **not** a fourth mechanism. It writes human-readable text into the step result, which is where an operator reads the evidence — the result label of [Technique (c)](#technique-e--provenance-labelling) is carried this way — but no script can read it back.

## What this guide builds

| Artifact | Count | Table |
| --- | --- | --- |
| Test suites | **10** | `sys_atf_test_suite` |
| Tests | **36** | `sys_atf_test` |
| Test steps | approximately 400 | `sys_atf_step` |
| Suite test membership rows | 36 | `sys_atf_test_suite_test` |
| New step configurations | **0** | `sys_atf_step_config` — every step below uses a stock configuration |
| Parent, master or aggregating suites | **0** | There is no eleventh suite. See [Assemble](#assemble). |

**Exactly ten `sys_atf_test_suite` records exist when this guide is complete, and the ten are the ten below.** No parent suite, no master suite and no suite-of-suites is created: the ten are run as an ordered batch by hand, in the order given under [Assemble](#assemble). A suite record whose only purpose is to nest the others would be an eleventh suite record and would put the delivered inventory at 11 against a specification of 10.

| # | Suite | Tests | Covers |
| --- | --- | --: | --- |
| 1 | `BST CRUD suite — startup` | 1 | `x_bst_startuptrk_startup` |
| 2 | `BST CRUD suite — founder` | 1 | `x_bst_startuptrk_founder` |
| 3 | `BST CRUD suite — executive` | 1 | `x_bst_startuptrk_executive` |
| 4 | `BST CRUD suite — investor` | 1 | `x_bst_startuptrk_investor` |
| 5 | `BST CRUD suite — fundinground` | 1 | `x_bst_startuptrk_fundinground` |
| 6 | `BST CRUD suite — jobposting` | 1 | `x_bst_startuptrk_jobposting` |
| 7 | `BST CRUD suite — newsarticle` | 1 | `x_bst_startuptrk_newsarticle` |
| 8 | `BST ACL suite — premium fields by role` | 21 | 7 premium fields x 3 roles |
| 9 | `BST REST suite — resources` | 6 | 6 logical resources including the nested sub-resource |
| 10 | `BST FLOW suite — ingestion` | 2 | `Crunchbase Ingestion`, `LinkedIn Ingestion` |
| | **Total** | **36** | |

### The canonical test names, and the one that carries a mode suffix

Every test name below is canonical: it is the spelling used in this guide, in [`../validation-checklist.md`](../validation-checklist.md), in the evidence record and in the traceability matrix, and no document uses a second spelling for the same test.

| Suite | Test name or naming pattern | Count |
| --- | --- | --: |
| 1 to 7 | `BST CRUD — <table suffix>`: `startup`, `founder`, `executive`, `investor`, `fundinground`, `jobposting`, `newsarticle` | 7 |
| 8 | `BST ACL — <table suffix>.<field> — <role suffix>`, for example `BST ACL — startup.total_funding_usd — user` | 21 |
| 9 | `BST REST — <resource>`: `startups`, `founders`, `investors`, `funding-rounds`, `jobs`, `news` | 6 |
| 10 | `BST FLOW — Crunchbase Ingestion [<mode>]` and `BST FLOW — LinkedIn Ingestion [<mode>]`, where `<mode>` is **`fallback`** or **`live`** | 2 |

**The two suite-10 tests always carry a mode suffix in square brackets, and there is no unsuffixed form of either name.** `BST FLOW — Crunchbase Ingestion [fallback]` and `BST FLOW — Crunchbase Ingestion [live]` are the only two permitted spellings of that test, and exactly one of them is the name on the record at any moment. On the instance recorded for this delivery both aliases are in Branch A, so **the two names in force are `BST FLOW — Crunchbase Ingestion [fallback]` and `BST FLOW — LinkedIn Ingestion [fallback]`**. Renaming to `[live]` happens only when the run genuinely used a live call, per [Technique (c)](#technique-e--provenance-labelling). A bare `BST FLOW — Crunchbase Ingestion` with no suffix is not a valid test name and must not appear on a record, in an evidence row, or in any other document.

## Suites 1 to 7 — table CRUD

Seven suites, one per entity table, one test in each. Every test follows the same twelve-to-fifteen-step skeleton below; the per-table sections that follow give the values that differ.

Build the skeleton once for `x_bst_startuptrk_startup`, confirm it passes, then copy the test six times through **Copy Test** on the test form and substitute the per-table values. Copying carries the steps with it.

### Identity rule — bind to `record_id`, never to a display value

**Every query, validation, update and delete in suites 1 to 7 identifies its subject record by the `record_id` output of the `Record Insert` step that created it.** Not by its name, not by its title, not by any other display value.

The reason is mechanical, not stylistic. A query written as `name` `is` `ATF Startup Alpha` matches **any** row carrying that name, including a row left behind by an earlier aborted run whose transaction did not roll back. Such a query produces both failure modes and neither is diagnosable from the result:

| Situation | With a display-value query | With a `record_id` query |
| --- | --- | --- |
| A stale row of the same name exists | Step 50 passes on the stale row even if step 30 inserted nothing readable — a **false pass** | Fails, naming the identifier that was not found |
| Step 110 deletes the subject and step 120 re-queries | The stale row still matches, so step 120 reports records where none should remain — a **false failure** | Passes, because the deleted identifier is gone |

**A per-run suffix is a secondary assertion, never the identity.** Every fixture value below carries the literal suffix `ATF` in its display column so a residual row is recognisable by eye in a list view, and the display-column assertion at step 40 confirms the value was **stored verbatim** — which is a real assertion about the column. It is not what selects the row.

The one place a display-value condition is unavoidable is the mandatory-field steps 80 and 90, where **no record is expected to exist** and therefore no `record_id` can be bound. Those steps assert **Record was not inserted** through the step's own assert type, so they need no identity at all.

### The shared CRUD skeleton

| Step | Step configuration | Category | Inputs |
| --- | --- | --- | --- |
| 5 | **Create a User** | Server - Independent | `first_name` = `BST ATF`, `last_name` = `admin`, `roles` = **exactly** `x_bst_startuptrk.admin`, `groups` empty, `impersonate` false. Created at run time; see [Technique (a)](#technique-a--impersonation) for the full input list. |
| 8 | **Run Server Side Script** | Server - Independent | Role-set verification for the step 5 user, script under [Step 2 — verify the role set](#step-2--verify-the-role-set-before-trusting-the-test). `EXPECTED` = `x_bst_startuptrk.admin`. Without it, a step-5 user that silently acquired the platform `admin` role would make steps 80 and 90 pass by override rather than by the mandatory flag. |
| 10 | **Impersonate** | Server - Independent | `user` = the step 5 output. Writes to all seven tables are granted to `x_bst_startuptrk.admin` alone, so a test that omits this step fails at step 30 for the wrong reason. |
| 20 | **Record Insert** | Server - Independent | The parent fixture, on tables that carry a mandatory `startup` reference. `table` = `x_bst_startuptrk_startup`; `field_values` = `name`, `headquarters_location`, `active` `true`; `enforce_security` = **true**; `assert_type` = **Record successfully inserted**. Omit this step in suite 1 and suite 4. |
| 30 | **Record Insert** | Server - Independent | The subject record. `table` = the table under test; `field_values` = every mandatory column plus one declared member of each choice column on the table; `enforce_security` = **true**; `assert_type` = **Record successfully inserted**. Bind any reference to the step 20 output `record_id`. **This step's `record_id` is the identity every later step binds to.** |
| 40 | **Record Validation** | Server - Independent | `table` = the table under test; `record_id` = **the step 30 output `record_id`**; `field_values` = conditions asserting each value written at step 30 was stored verbatim, **including the exact choice string of every choice column and the exact display value**; `enforce_security` = **true**; `assert_type` = **Record successfully validated**. |
| 50 | **Record Query** | Server - Independent | `table` = the table under test; `field_values` = the single condition `Sys ID` `is` **the step 30 output `record_id`**; `enforce_security` = **true**; `assert_type` = **There is exactly one record matching the query**. Exactly one, not at least one: at-least-one cannot distinguish the subject from a stale row. |
| 60 | **Record Update** | Server - Independent | `table` = the table under test; `record_id` = **the step 30 output**; `field_values` = one non-choice column changed plus a **second** declared member of every choice column on the table; `enforce_security` = **true**; `assert_type` = **Record successfully updated**. |
| 70 | **Record Validation** | Server - Independent | `record_id` = **the step 30 output**. Asserts the step 60 values are stored — including each choice column's second member — and that the columns step 60 did not touch are unchanged. `assert_type` = **Record successfully validated**. |
| 80 | **Record Insert** | Server - Independent | Mandatory-field assertion, first mandatory column. `field_values` = every mandatory column **except** this one; `enforce_security` = **true**; `assert_type` = **Record was not inserted**. No identity is bound; nothing is expected to exist. |
| 90 | **Record Insert** | Server - Independent | Mandatory-field assertion, second mandatory column, same pattern. Present on every table except `x_bst_startuptrk_investor`, which has one mandatory column. |
| 100 | **Run Server Side Script** | Server - Independent | **The record-layer choice assertion.** Writes a non-member value to every choice column of the table under test **through the record layer** and asserts what the dictionary and the choice list actually do with it. Script and per-table expectations under [The choice-value assertion](#the-choice-value-assertion). |
| 110 | **Record Delete** | Server - Independent | `table` = the table under test; `record_id` = **the step 30 output**; `enforce_security` = **true**; `assert_type` = **Record successfully deleted**. |
| 120 | **Record Query** | Server - Independent | `field_values` = `Sys ID` `is` **the step 30 output**; `assert_type` = **No records match the query**. Confirms the delete took effect on the record the test created rather than merely reporting success. |

No teardown step is required, and none is added. ATF rolls back the data a test creates when the test finishes, so the fixture at step 20 and the subject record at step 30 do not persist. That rollback is also why [Technique (c)](#technique-e--provenance-labelling) treats an in-test provenance write as a separate evidence surface from a scheduled one.

`enforce_security` is **true** on every record step above. With it false the step runs unrestricted, step 30 succeeds regardless of the ACLs, and the suite reports `success` while proving nothing about the access-control layer. It is set true here for the same reason it is set true in suite 8, where the entire assertion depends on it.

### The choice-value assertion

**Step 100 asserts the table's own choice contract, at the record layer.** It reads the delivered `sys_choice` inventory for each choice column of the table under test, writes values through `GlideRecord` on a record the step creates, and asserts what the **dictionary and the choice list** actually do. It calls no ingestion class and asserts nothing about `IngestionMapper`: the mapper's normalisation contract is a property of the ingestion pipeline, and it is asserted in [suite 10](#suite-10--bst-flow-suite--ingestion), where the pipeline is what is under test.

That separation matters because the two layers behave differently, and conflating them hides the reason the mapper exists:

| Layer | What it does with a value outside the choice list | Asserted by |
| --- | --- | --- |
| **The record layer** — `GlideRecord.setValue()` on a `choice` `1` column | **Stores it.** A choice list on a string column is a dictionary-driven picker for form and list interfaces; it is **not** a server-side write constraint, so an out-of-list value written by a script is persisted as supplied, subject only to `max_length`. | **Step 100 of suites 1 to 7** |
| **The ingestion layer** — `IngestionMapper.normaliseChoice()` | **Normalises it** before any write: a case-insensitive match resolves to the list's own spelling, an unmatched value coerces to `Other` where the list declares one and is left unwritten where it does not, and every unmatched value is logged. | **Suite 10** |

**The record layer storing an out-of-list value is correct platform behaviour and step 100 asserts it as such.** It is exactly why normalisation has to happen in the mapper before the write, and a step-100 assertion that expected the record layer to reject the value would fail against a correctly built table.

### The eleven choice columns and their delivered lists

Step 100 asserts every choice column of the table under test. There are **eleven** across the seven tables, carrying **63** choice values between them. `max_length` and the member list below are transcribed from the delivered dictionary and `sys_choice` records and are what step 100 asserts against.

| # | Physical column | `max_length` | Declares `Other` | Members, in delivered sequence |
| --: | --- | --: | --- | --- |
| 1 | `x_bst_startuptrk_startup.industry` | 40 | **Yes** | `Fintech`, `Healthtech`, `SaaS`, `Consumer`, `Deeptech`, `Other` |
| 2 | `x_bst_startuptrk_startup.funding_stage` | 40 | No | `Pre-Seed`, `Seed`, `Series A`, `Series B`, `Series C+`, `Growth`, `Public`, `Acquired` |
| 3 | `x_bst_startuptrk_startup.employee_count_range` | 20 | No | `1-10`, `11-50`, `51-200`, `201-500`, `500+` |
| 4 | `x_bst_startuptrk_founder.title` | 40 | **Yes** | `CEO`, `CTO`, `COO`, `Co-Founder`, `Other` |
| 5 | `x_bst_startuptrk_executive.title` | 40 | **Yes** | `CFO`, `VP Engineering`, `VP Sales`, `VP Marketing`, `Head of Product`, `Other` |
| 6 | `x_bst_startuptrk_investor.type` | 30 | No | `VC`, `Angel`, `PE`, `Corporate`, `Accelerator` |
| 7 | `x_bst_startuptrk_investor.focus_areas` | 255 | **Yes** | `Fintech`, `Healthtech`, `SaaS`, `Consumer`, `Deeptech`, `Other` — **multi-valued**, stored comma-separated |
| 8 | `x_bst_startuptrk_fundinground.round_type` | 40 | No | `Pre-Seed`, `Seed`, `Series A`, `Series B`, `Series C+`, `Growth`, `Public`, `Acquired` |
| 9 | `x_bst_startuptrk_jobposting.department` | 40 | **Yes** | `Engineering`, `Sales`, `Marketing`, `Product`, `Operations`, `Other` |
| 10 | `x_bst_startuptrk_jobposting.remote_type` | 20 | No | `Onsite`, `Hybrid`, `Remote` |
| 11 | `x_bst_startuptrk_jobposting.seniority` | 20 | No | `Entry`, `Mid`, `Senior`, `Lead`, `Executive` |

6 + 8 + 5 + 5 + 6 + 5 + 6 + 8 + 6 + 3 + 5 = **63**. Every member's `value` and its `label` are the same string on all eleven columns, and every column carries `choice` `1` — a dropdown including a blank option — so none of the eleven is mandatory and a blank is a legal stored value.

**Do not add an `Other` member to any of the six lists that lack one**, and do not add, remove or reorder a member of any of the eleven. `x_bst_startuptrk_ingest_staging` contributes a further 14 choice values across `source_system`, `record_type`, `import_state` and `run_provenance`, which is why the delivered `sys_choice` count is 77 and not 63. Step 100 asserts only the 63 belonging to the seven entity tables.

### The step 100 script

Use this at step 100. Substitute `TABLE`, `PARENT_FIELD_VALUES` and the `COLUMNS` array; nothing else changes between the seven tables. Leave **Jasmine version** at the value the field defaults to.

```javascript
(function(outputs, steps, params, stepResult, assertEqual) {
    // ---- per-table substitution, and the only part that differs across suites 1 to 7 ----
    var TABLE = 'x_bst_startuptrk_startup';

    // Every mandatory column of TABLE except the choice columns, so a record can be
    // inserted. On a child table, bind 'startup' to the step 20 parent instead: replace
    // the literal with steps(STEP_20_PARENT).record_id and declare that constant here.
    var PARENT_FIELD_VALUES = { name: 'ATF Choice Probe', headquarters_location: 'Boston, MA', active: true };

    var COLUMNS = [
        { field: 'industry',             max_length: 40, declares_other: true,
          members: ['Fintech', 'Healthtech', 'SaaS', 'Consumer', 'Deeptech', 'Other'] },
        { field: 'funding_stage',        max_length: 40, declares_other: false,
          members: ['Pre-Seed', 'Seed', 'Series A', 'Series B', 'Series C+', 'Growth', 'Public', 'Acquired'] },
        { field: 'employee_count_range', max_length: 20, declares_other: false,
          members: ['1-10', '11-50', '51-200', '201-500', '500+'] }
    ];
    // ---- end of per-table substitution ----

    var NON_MEMBER = 'ATF not a member 12345';
    var probe = new GlideRecord(TABLE);
    probe.initialize();
    var f = '';
    for (f in PARENT_FIELD_VALUES) {
        if (PARENT_FIELD_VALUES.hasOwnProperty(f)) {
            probe.setValue(f, PARENT_FIELD_VALUES[f]);
        }
    }
    var probeId = probe.insert();
    if (!probeId) {
        stepResult.setFailed('Could not insert the choice probe record on ' + TABLE +
            '. Check PARENT_FIELD_VALUES covers every mandatory column.');
        return false;
    }

    var i = 0;
    var c = 0;
    for (c = 0; c !== COLUMNS.length; c++) {
        var col = COLUMNS[c];

        // 1. The dictionary contract: the column is a choice-1 string of the declared length.
        var dict = new GlideRecord('sys_dictionary');
        dict.addQuery('name', TABLE);
        dict.addQuery('element', col.field);
        dict.setLimit(1);
        dict.query();
        assertEqual({ name: col.field + ' has a dictionary record',
            shouldbe: true, value: dict.next() });
        assertEqual({ name: col.field + ' is a string column',
            shouldbe: 'string', value: dict.getValue('internal_type') });
        assertEqual({ name: col.field + ' max_length is ' + col.max_length,
            shouldbe: col.max_length, value: parseInt(dict.getValue('max_length'), 10) });
        assertEqual({ name: col.field + ' carries a dropdown choice list',
            shouldbe: '1', value: String(dict.getValue('choice')) });

        // 2. The choice list holds exactly the declared members, in the declared sequence.
        var listed = [];
        var choices = new GlideRecord('sys_choice');
        choices.addQuery('name', TABLE);
        choices.addQuery('element', col.field);
        choices.orderBy('sequence');
        choices.query();
        while (choices.next()) {
            listed.push(choices.getValue('value'));
            assertEqual({ name: col.field + ' member ' + choices.getValue('value') +
                    ' uses its value as its label',
                shouldbe: choices.getValue('value'), value: choices.getValue('label') });
        }
        assertEqual({ name: col.field + ' declares exactly ' + col.members.length + ' members',
            shouldbe: col.members.length, value: listed.length });
        assertEqual({ name: col.field + ' members match in order',
            shouldbe: col.members.join('|'), value: listed.join('|') });
        assertEqual({ name: col.field + ' Other membership is ' + col.declares_other,
            shouldbe: col.declares_other, value: listed.indexOf('Other') !== -1 });

        // 3. Every declared member is storable and is stored VERBATIM, on insert and on update.
        for (i = 0; i !== col.members.length; i++) {
            var wanted = col.members[i];
            var writer = new GlideRecord(TABLE);
            writer.get(probeId);
            writer.setValue(col.field, wanted);
            writer.update();
            var reader = new GlideRecord(TABLE);
            reader.get(probeId);
            assertEqual({ name: col.field + ' stores member ' + wanted + ' verbatim',
                shouldbe: wanted, value: String(reader.getValue(col.field)) });
        }

        // 4. A blank is a legal stored value on a choice-1 column.
        var clearer = new GlideRecord(TABLE);
        clearer.get(probeId);
        clearer.setValue(col.field, '');
        clearer.update();
        var cleared = new GlideRecord(TABLE);
        cleared.get(probeId);
        assertEqual({ name: col.field + ' accepts a blank',
            shouldbe: '', value: String(cleared.getValue(col.field) || '') });

        // 5. The record layer does NOT police the list: a non-member written by a script is
        //    STORED. This is correct platform behaviour, and it is why normalisation lives in
        //    IngestionMapper ahead of the write - asserted in suite 10, not here.
        var loose = new GlideRecord(TABLE);
        loose.get(probeId);
        loose.setValue(col.field, NON_MEMBER);
        loose.update();
        var stored = new GlideRecord(TABLE);
        stored.get(probeId);
        assertEqual({ name: col.field + ' record layer stores a non-member as supplied',
            shouldbe: NON_MEMBER, value: String(stored.getValue(col.field)) });
        assertEqual({ name: col.field + ' non-member is genuinely outside the list',
            shouldbe: -1, value: listed.indexOf(NON_MEMBER) });

        // 6. max_length is enforced on the stored value.
        var overlong = '';
        while (overlong.length < col.max_length + 20) {
            overlong = overlong + 'X';
        }
        var truncator = new GlideRecord(TABLE);
        truncator.get(probeId);
        truncator.setValue(col.field, overlong);
        truncator.update();
        var truncated = new GlideRecord(TABLE);
        truncated.get(probeId);
        assertEqual({ name: col.field + ' stores at most max_length characters',
            shouldbe: true,
            value: String(truncated.getValue(col.field)).length <= col.max_length });

        // Leave the column on a declared member so the probe ends in a valid state.
        var restore = new GlideRecord(TABLE);
        restore.get(probeId);
        restore.setValue(col.field, col.members[0]);
        restore.update();
    }

    var cleanup = new GlideRecord(TABLE);
    if (cleanup.get(probeId)) {
        cleanup.deleteRecord();
    }

    stepResult.setOutputMessage('Choice contract asserted at the record layer for ' +
        COLUMNS.length + ' column(s) on ' + TABLE +
        '; mapper normalisation is asserted in suite 10.');
    return true;
})(outputs, steps, params, stepResult, assertEqual);
```

The probe record is created and deleted inside the step, and ATF rolls back anything the delete missed, so step 100 leaves nothing behind and does not disturb the step 30 subject record.

**`x_bst_startuptrk_investor.focus_areas` is the one multi-valued column**, so suite 4 substitutes one further block after the loop: write two declared members as `Fintech,SaaS`, assert both survive the round trip in that order, then write `Fintech,ATF not a member 12345` and assert the record layer stores that string too — a second demonstration that the guarantee belongs to the mapper. Its per-member normalisation is asserted in suite 10.

### Suite 1 — `BST CRUD suite — startup`

One test, `BST CRUD — startup`. Table `x_bst_startuptrk_startup`, 12 columns, display column `name`. Step 20 is omitted; this table has no parent.

| Skeleton step | Value for this table |
| --- | --- |
| 30 insert | `name` = `ATF Startup Alpha`, `headquarters_location` = `Boston, MA`, `active` = `true`, `industry` = `Fintech`, `funding_stage` = `Seed`, `employee_count_range` = `11-50`, `founded_year` = `2021` |
| 40 validation | `record_id` = step 30 `record_id`. `name` `is` `ATF Startup Alpha`; `headquarters_location` `is` `Boston, MA`; `active` `is` `true`; `industry` `is` `Fintech`; `funding_stage` `is` `Seed`; `employee_count_range` `is` `11-50`; `founded_year` `is` `2021` |
| 50 query | `Sys ID` `is` step 30 `record_id` — **exactly one record** |
| 60 update | `description` = `Updated by ATF`, `industry` = `SaaS`, `funding_stage` = `Series A`, `employee_count_range` = `51-200` |
| 70 validation | `record_id` = step 30 `record_id`. `description` `is` `Updated by ATF`; `industry` `is` `SaaS`; `funding_stage` `is` `Series A`; `employee_count_range` `is` `51-200`; and the untouched `name` `is` `ATF Startup Alpha`, `headquarters_location` `is` `Boston, MA`, `founded_year` `is` `2021` |
| 80 mandatory | `name` omitted, `headquarters_location` and `active` supplied — **Record was not inserted** |
| 90 mandatory | `headquarters_location` omitted, `name` and `active` supplied — **Record was not inserted** |
| 100 choice | `COLUMNS` = `industry`, `funding_stage`, `employee_count_range`, exactly as the script above is written |
| 110 delete / 120 re-query | `record_id` = step 30 `record_id`; then `Sys ID` `is` that same identifier — **No records match** |

Three additions specific to this table, appended after step 120. **Steps 130 and 135 are two separate steps**, because one ATF step carries one configuration: a `Record Insert` step cannot also perform a `Record Validation`.

| Step | Step configuration | Purpose and inputs |
| --- | --- | --- |
| 130 | **Record Insert** | The `active` default. `table` = `x_bst_startuptrk_startup`; `field_values` = `name` = `ATF Startup Default`, `headquarters_location` = `Boston, MA` and **nothing else** — in particular `active` is **not** supplied; `enforce_security` = **true**; `assert_type` = **Record successfully inserted**. `active` is mandatory but carries a default of `true`, so unlike `name` and `headquarters_location` it cannot be left blank by omission — the default satisfies the mandatory flag. |
| 135 | **Record Validation** | `table` = `x_bst_startuptrk_startup`; `record_id` = **the step 130 output `record_id`**; `field_values` = `active` `is` `true`; `enforce_security` = **true**; `assert_type` = **Record successfully validated**. Bound to step 130's output, not step 30's, and not to a name condition. |
| 140 | **Run Server Side Script** | The cascade-delete assertion, script below. |

#### Step 140 — the cascade-delete assertion

```javascript
(function(outputs, steps, params, stepResult, assertEqual) {
    var CHILDREN = [
        { table: 'x_bst_startuptrk_founder',      values: { name: 'ATF Cascade Founder' } },
        { table: 'x_bst_startuptrk_executive',    values: { name: 'ATF Cascade Executive' } },
        { table: 'x_bst_startuptrk_fundinground', values: { round_date: '2025-06-30' } },
        { table: 'x_bst_startuptrk_jobposting',   values: { title: 'ATF Cascade Job' } },
        { table: 'x_bst_startuptrk_newsarticle',  values: { title: 'ATF Cascade Article' } }
    ];

    // A parent of its own, so this assertion is independent of the step 30 subject record.
    var parent = new GlideRecord('x_bst_startuptrk_startup');
    parent.initialize();
    parent.setValue('name', 'ATF Cascade Parent');
    parent.setValue('headquarters_location', 'Boston, MA');
    parent.setValue('active', true);
    var parentId = parent.insert();
    assertEqual({ name: 'cascade parent inserted', shouldbe: true, value: !!parentId });

    var created = [];
    var i = 0;
    var f = '';
    for (i = 0; i !== CHILDREN.length; i++) {
        var child = new GlideRecord(CHILDREN[i].table);
        child.initialize();
        child.setValue('startup', parentId);
        for (f in CHILDREN[i].values) {
            if (CHILDREN[i].values.hasOwnProperty(f)) {
                child.setValue(f, CHILDREN[i].values[f]);
            }
        }
        var childId = child.insert();
        assertEqual({ name: CHILDREN[i].table + ' child inserted',
            shouldbe: true, value: !!childId });
        created.push({ table: CHILDREN[i].table, sys_id: childId });
    }
    assertEqual({ name: 'five children created, one per referencing table',
        shouldbe: 5, value: created.length });

    // Delete the parent. Every mandatory startup reference carries a cascade rule, so
    // no child may survive with a dangling mandatory reference.
    var doomed = new GlideRecord('x_bst_startuptrk_startup');
    assertEqual({ name: 'cascade parent is readable before the delete',
        shouldbe: true, value: doomed.get(parentId) });
    doomed.deleteRecord();

    var gone = new GlideRecord('x_bst_startuptrk_startup');
    assertEqual({ name: 'cascade parent is gone', shouldbe: false, value: gone.get(parentId) });

    for (i = 0; i !== created.length; i++) {
        var survivor = new GlideRecord(created[i].table);
        assertEqual({ name: created[i].table + ' child was cascaded away',
            shouldbe: false, value: survivor.get(created[i].sys_id) });
    }

    stepResult.setOutputMessage('Cascade asserted: 1 parent and ' + created.length +
        ' children deleted, 0 orphans left with a dangling mandatory reference.');
    return true;
})(outputs, steps, params, stepResult, assertEqual);
```

The startup inclusion criteria are **not** asserted here. They are a query filter, not a table constraint: a record failing them is stored normally and is excluded only from portal-facing and non-administrative list queries. Their assertion belongs to the `/startups` test in [suite 9](#suite-9--bst-rest-suite--resources) and to the portal walkthrough in [`04-service-portal-pages-and-widgets.md`](04-service-portal-pages-and-widgets.md).

### Suite 2 — `BST CRUD suite — founder`

One test, `BST CRUD — founder`. Table `x_bst_startuptrk_founder`, 6 columns, display column `name`. Step 20 creates the parent startup with `name` = `ATF Founder Parent`, `headquarters_location` = `Boston, MA`, `active` = `true`.

| Skeleton step | Value for this table |
| --- | --- |
| 30 insert | `name` = `ATF Founder Alpha`, `startup` = step 20 `record_id`, `title` = `CEO`, `bio` = `Seeded by ATF`, `contact_email` = `atf.founder@example.invalid` |
| 40 validation | `record_id` = step 30 `record_id`. `name` `is` `ATF Founder Alpha`; `startup` `is` the step 20 `record_id`; `title` `is` `CEO`; `bio` `is` `Seeded by ATF` |
| 50 query | `Sys ID` `is` step 30 `record_id` — **exactly one record** |
| 60 update | `linkedin_url` = `https://example.invalid/in/atf-founder`, `title` = `Co-Founder` |
| 70 validation | `record_id` = step 30 `record_id`. `linkedin_url` `is` `https://example.invalid/in/atf-founder`; `title` `is` `Co-Founder`; and the untouched `name` `is` `ATF Founder Alpha`, `startup` `is` the step 20 `record_id`, `bio` `is` `Seeded by ATF` |
| 80 mandatory | `name` omitted, `startup` supplied — **Record was not inserted** |
| 90 mandatory | `startup` omitted, `name` supplied — **Record was not inserted** |
| 100 choice | `TABLE` = `x_bst_startuptrk_founder`; `PARENT_FIELD_VALUES` = `{ name: 'ATF Choice Probe', startup: steps(STEP_20_PARENT).record_id }`; `COLUMNS` = one entry: `title`, `max_length` 40, `declares_other` **true**, members `CEO`, `CTO`, `COO`, `Co-Founder`, `Other` |
| 110 delete / 120 re-query | `record_id` = step 30 `record_id`; then `Sys ID` `is` that same identifier — **No records match** |

**`contact_email` is written at step 30 and is deliberately not read back at step 40 or step 70.** Both statements are true at once and neither contradicts the other: writing it is what gives [suite 8](#suite-8--bst-acl-suite--premium-fields-by-role) cells `ACL-3.1` to `ACL-3.3` a non-empty value to gate, and **reading** it is what those three cells do, per role, under impersonation. A read assertion here would add nothing that they do not already make — the test user at step 5 holds `x_bst_startuptrk.admin`, so it would only ever assert the administrator outcome, which is cell `ACL-3.1`. The value written here is `atf.founder@example.invalid`, the same reserved-domain address the ACL cells use.

### Suite 3 — `BST CRUD suite — executive`

One test, `BST CRUD — executive`. Table `x_bst_startuptrk_executive`, 6 columns, display column `name`. Step 20 creates the parent startup with `name` = `ATF Executive Parent`, `headquarters_location` = `Cambridge, MA`, `active` = `true`. The column set matches Founder; only the `title` choice list differs, and the two tables remain separate as specified.

| Skeleton step | Value for this table |
| --- | --- |
| 30 insert | `name` = `ATF Executive Alpha`, `startup` = step 20 `record_id`, `title` = `VP Engineering`, `contact_email` = `atf.exec@example.invalid` |
| 40 validation | `record_id` = step 30 `record_id`. `name` `is` `ATF Executive Alpha`; `startup` `is` the step 20 `record_id`; `title` `is` `VP Engineering` |
| 50 query | `Sys ID` `is` step 30 `record_id` — **exactly one record** |
| 60 update | `bio` = `Updated by ATF`, `title` = `Head of Product` |
| 70 validation | `record_id` = step 30 `record_id`. `bio` `is` `Updated by ATF`; `title` `is` `Head of Product`; and the untouched `name` `is` `ATF Executive Alpha`, `startup` `is` the step 20 `record_id` |
| 80 mandatory | `name` omitted, `startup` supplied — **Record was not inserted** |
| 90 mandatory | `startup` omitted, `name` supplied — **Record was not inserted** |
| 100 choice | `TABLE` = `x_bst_startuptrk_executive`; `PARENT_FIELD_VALUES` = `{ name: 'ATF Choice Probe', startup: steps(STEP_20_PARENT).record_id }`; `COLUMNS` = one entry: `title`, `max_length` 40, `declares_other` **true**, members `CFO`, `VP Engineering`, `VP Sales`, `VP Marketing`, `Head of Product`, `Other` |
| 110 delete / 120 re-query | `record_id` = step 30 `record_id`; then `Sys ID` `is` that same identifier — **No records match** |

`contact_email` is written and not read back here, for the same reason as in suite 2: cells `ACL-4.1` to `ACL-4.3` own its read outcome. **The two `contact_email` columns are two distinct access-control records on two distinct tables**, so suite 2's value does not stand in for suite 3's, and neither suite's fixture covers the other.

### Suite 4 — `BST CRUD suite — investor`

One test, `BST CRUD — investor`. Table `x_bst_startuptrk_investor`, 6 columns, display column `name`. Step 20 is omitted; this table has no parent. Step 90 is omitted; `name` is the only mandatory column.

| Skeleton step | Value for this table |
| --- | --- |
| 30 insert | `name` = `ATF Capital Partners`, `type` = `VC`, `focus_areas` = `Fintech,SaaS`, `aum_usd` = `450000000` |
| 40 validation | `record_id` = step 30 `record_id`. `name` `is` `ATF Capital Partners`; `type` `is` `VC`; `focus_areas` `is` `Fintech,SaaS`; `portfolio_count` `is` `0` |
| 50 query | `Sys ID` `is` step 30 `record_id` — **exactly one record** |
| 60 update | `website` = `https://example.invalid/atf-capital`, `type` = `Accelerator`, `focus_areas` = `Healthtech,Other` |
| 70 validation | `record_id` = step 30 `record_id`. `website` `is` `https://example.invalid/atf-capital`; `type` `is` `Accelerator`; `focus_areas` `is` `Healthtech,Other`; and the untouched `name` `is` `ATF Capital Partners`, `portfolio_count` `is` `0` |
| 80 mandatory | `name` omitted — **Record was not inserted** |
| 100 choice | `TABLE` = `x_bst_startuptrk_investor`; `PARENT_FIELD_VALUES` = `{ name: 'ATF Choice Probe' }`; `COLUMNS` = two entries: `type`, `max_length` 30, `declares_other` **false**, members `VC`, `Angel`, `PE`, `Corporate`, `Accelerator`; and `focus_areas`, `max_length` 255, `declares_other` **true**, members `Fintech`, `Healthtech`, `SaaS`, `Consumer`, `Deeptech`, `Other`. Append the multi-valued block named under [The step 100 script](#the-step-100-script). |
| 110 delete / 120 re-query | `record_id` = step 30 `record_id`; then `Sys ID` `is` that same identifier — **No records match** |

Two additions specific to this table, appended after step 120.

| Step | Step configuration | Purpose |
| --- | --- | --- |
| 130 | **Run Server Side Script** | The `portfolio_count` **write contract**: what the dictionary declares, what a server-side write can actually do, and what the REST write allowlist refuses. Script below. |
| 140 | **Run Server Side Script** | The `portfolio_count` **derivation**, across all six states the count can take. Script below. |

#### Step 130 — the `portfolio_count` write contract

**A server-side `GlideRecord` write to a read-only dictionary column succeeds.** The `read_only` dictionary attribute governs form and list editing; it is not a server-side write barrier, and a test that expected `setValue('portfolio_count', 99)` followed by `update()` to be refused would fail against a correctly built table. What actually protects the column from a caller is the **write allowlist of the REST operation**, and that is what this step asserts, alongside the dictionary declaration itself.

```javascript
(function(outputs, steps, params, stepResult, assertEqual) {
    var TABLE = 'x_bst_startuptrk_investor';
    var FIELD = 'portfolio_count';

    // 1. The dictionary declaration: derived, read-only, integer, defaulting to 0.
    var dict = new GlideRecord('sys_dictionary');
    dict.addQuery('name', TABLE);
    dict.addQuery('element', FIELD);
    dict.setLimit(1);
    dict.query();
    assertEqual({ name: FIELD + ' has a dictionary record', shouldbe: true, value: dict.next() });
    assertEqual({ name: FIELD + ' is an integer column',
        shouldbe: 'integer', value: dict.getValue('internal_type') });
    assertEqual({ name: FIELD + ' is declared read-only',
        shouldbe: true, value: String(dict.getValue('read_only')) === 'true' });
    assertEqual({ name: FIELD + ' defaults to 0',
        shouldbe: '0', value: String(dict.getValue('default_value')) });

    // 2. The REST write allowlist of PUT /investors/{id} carries portfolio_count as a
    //    READABLE field and NOT as a writable one. Read the delivered operation script and
    //    assert both halves, so the allowlist is checked against the artifact rather than
    //    against a transcription of it.
    var op = new GlideRecord('sys_ws_operation');
    op.addQuery('relative_path', '/investors/{id}');
    op.addQuery('http_method', 'PUT');
    op.setLimit(1);
    op.query();
    assertEqual({ name: 'PUT /investors/{id} exists', shouldbe: true, value: op.next() });
    var script = String(op.getValue('operation_script'));
    var fieldsLine = script.substring(script.indexOf('var fields ='), script.indexOf('var writable'));
    var writableBlock = script.substring(script.indexOf('var writable'), script.indexOf('rejectNonJsonBody'));
    assertEqual({ name: FIELD + ' is in the serialised field list',
        shouldbe: true, value: fieldsLine.indexOf("'" + FIELD + "'") !== -1 });
    assertEqual({ name: FIELD + ' is NOT in the write allowlist',
        shouldbe: -1, value: writableBlock.indexOf("'" + FIELD + "'") });

    // 3. The allowlist gate itself, exercised through the same helper every write
    //    operation calls, with the investor spec exactly as the operation declares it.
    var spec = [
        { field: 'name', type: 'string', max: 100, mandatory: true },
        { field: 'type', type: 'choice', choices: ['VC', 'Angel', 'PE', 'Corporate', 'Accelerator'] },
        { field: 'focus_areas', type: 'multichoice',
          choices: ['Fintech', 'Healthtech', 'SaaS', 'Consumer', 'Deeptech', 'Other'] },
        { field: 'website', type: 'url', max: 255 },
        { field: 'aum_usd', type: 'currency' }
    ];
    var helper = new RestQueryHelper();

    // 3a. A body carrying ONLY portfolio_count reaches no writable field, so the request
    //     is refused with 400 rather than silently ignored.
    var only = helper.validateBody({ portfolio_count: 99 }, spec, false);
    assertEqual({ name: 'a body of only ' + FIELD + ' is refused',
        shouldbe: false, value: only.ok });
    assertEqual({ name: 'the refusal names the missing writable field',
        shouldbe: 'Request body carries no writable field', value: only.error });

    // 3b. A mixed body applies the writable field and DROPS portfolio_count entirely.
    var mixed = helper.validateBody(
        { website: 'https://example.invalid/atf-allowlist', portfolio_count: 99 }, spec, false);
    assertEqual({ name: 'a mixed body is accepted', shouldbe: true, value: mixed.ok });
    assertEqual({ name: 'the writable field is carried through',
        shouldbe: 'https://example.invalid/atf-allowlist', value: mixed.values.website });
    assertEqual({ name: FIELD + ' is dropped and never reaches the record',
        shouldbe: false,
        value: Object.prototype.hasOwnProperty.call(mixed.values, FIELD) });

    // 4. The honest server-side position, asserted rather than assumed: a script write
    //    DOES land, which is why the projection is owned by InvestorPortfolioService and
    //    the allowlist above is the caller-facing guard.
    var probe = new GlideRecord(TABLE);
    probe.initialize();
    probe.setValue('name', 'ATF Allowlist Probe');
    var probeId = probe.insert();
    var writer = new GlideRecord(TABLE);
    writer.get(probeId);
    writer.setValue(FIELD, 99);
    writer.update();
    var read = new GlideRecord(TABLE);
    read.get(probeId);
    assertEqual({ name: 'a server-side write to ' + FIELD + ' is not blocked by read_only',
        shouldbe: 99, value: parseInt(read.getValue(FIELD), 10) });

    // ...and the service restores the derived value, which for this probe is 0.
    new InvestorPortfolioService().recalculate(probeId);
    var restored = new GlideRecord(TABLE);
    restored.get(probeId);
    assertEqual({ name: 'the service restores the derived value',
        shouldbe: 0, value: parseInt(restored.getValue(FIELD), 10) });

    var cleanup = new GlideRecord(TABLE);
    if (cleanup.get(probeId)) {
        cleanup.deleteRecord();
    }

    stepResult.setOutputMessage(FIELD + ' write contract asserted: read-only in the ' +
        'dictionary, absent from the REST write allowlist, restored by the service.');
    return true;
})(outputs, steps, params, stepResult, assertEqual);
```

#### Step 140 — the `portfolio_count` derivation, every state and every transition

The derivation is the count of **distinct** startups an investor reaches by **either** path — as `lead_investor` on a funding round, or through an `x_bst_startuptrk_m2m_round_investor` row against a funding round — with the two sets unioned **before** counting. A single expected value of `1` would pass against an implementation that always returned `1`, so this step walks the count up and back down to zero and asserts the **transition** each mutation causes, on the investor that changed **and** on the investor that should not have changed.

Every assertion reads `portfolio_count` **off the investor record** without calling the service first, so what is under test is the pair of business rules that maintain the stored value. The final assertions then compare the stored value with `countPortfolio()` to establish that the two agree.

Three investors and two startups make every transition observable. `subject` is the investor under test, `holder` leads the rounds `subject` participates in, and `sink` starts empty so a repointed lead produces a visible rise rather than a value that was already correct.

| # | Mutation | `subject` | `holder` | `sink` | What it rules out |
| --: | --- | --: | --: | --: | --- |
| 1 | Nothing created yet | **0** | 0 | 0 | An implementation that never reaches zero |
| 2 | `r1` on `s1`, lead `subject` | **1** | 0 | 0 | The baseline |
| 3 | `r2` on `s1`, lead `holder` | 1 | **1** | 0 | A rule that recalculates the wrong investor |
| 4 | Join row links `subject` to `r2` — a second round of the **same** startup | **1** | 1 | 0 | Counting rounds instead of distinct startups; double-counting the union |
| 5 | `r3` on `s2`, lead `holder` | 1 | **2** | 0 | — |
| 6 | Join row links `subject` to `r3` — a **second** startup | **2** | 2 | 0 | An implementation that always returns 1 |
| 7 | The join row to `r3` is deleted | **1** | 2 | 0 | A participation path never re-evaluated on delete |
| 8 | The join row to `r2` is deleted | **1** | 2 | 0 | A lead path that quietly depends on a participation row |
| 9 | `r1`'s `lead_investor` is repointed from `subject` to `sink` | **0** | 2 | **1** | A `previous` lead never recalculated, **and** a new lead never recalculated |
| 10 | `r2` is deleted outright | 0 | **1** | 1 | A round delete that leaves the lead's count stale |
| 11 | `r1` is deleted outright | 0 | 1 | **0** | A count that cannot return to zero once it has risen |

```javascript
(function(outputs, steps, params, stepResult, assertEqual) {
    var INVESTOR = 'x_bst_startuptrk_investor';
    var ROUND = 'x_bst_startuptrk_fundinground';
    var LINK = 'x_bst_startuptrk_m2m_round_investor';

    function startup(name) {
        var gr = new GlideRecord('x_bst_startuptrk_startup');
        gr.initialize();
        gr.setValue('name', name);
        gr.setValue('headquarters_location', 'Boston, MA');
        gr.setValue('active', true);
        return gr.insert();
    }
    function investor(name) {
        var gr = new GlideRecord(INVESTOR);
        gr.initialize();
        gr.setValue('name', name);
        gr.setValue('type', 'VC');
        return gr.insert();
    }
    function round(startupId, day, leadId) {
        var gr = new GlideRecord(ROUND);
        gr.initialize();
        gr.setValue('startup', startupId);
        gr.setValue('round_date', day);
        gr.setValue('round_type', 'Series A');
        gr.setValue('lead_investor', leadId);
        return gr.insert();
    }
    function link(roundId, investorId) {
        var gr = new GlideRecord(LINK);
        gr.initialize();
        gr.setValue('funding_round', roundId);
        gr.setValue('investor', investorId);
        return gr.insert();
    }
    function drop(table, sysId) {
        var gr = new GlideRecord(table);
        if (gr.get(sysId)) {
            gr.deleteRecord();
        }
    }
    function stored(investorId) {
        var gr = new GlideRecord(INVESTOR);
        if (!gr.get(investorId)) {
            return -1;
        }
        return parseInt(gr.getValue('portfolio_count'), 10);
    }
    function state(label, subjectId, holderId, sinkId, expected) {
        assertEqual({ name: label + ': subject is ' + expected[0],
            shouldbe: expected[0], value: stored(subjectId) });
        assertEqual({ name: label + ': holder is ' + expected[1],
            shouldbe: expected[1], value: stored(holderId) });
        assertEqual({ name: label + ': sink is ' + expected[2],
            shouldbe: expected[2], value: stored(sinkId) });
    }

    var subject = investor('ATF Portfolio Subject');
    var holder = investor('ATF Portfolio Holder');
    var sink = investor('ATF Portfolio Sink');
    var s1 = startup('ATF Portfolio S1');
    var s2 = startup('ATF Portfolio S2');

    state('state 1 nothing created', subject, holder, sink, [0, 0, 0]);

    var r1 = round(s1, '2025-01-31', subject);
    state('state 2 subject leads r1 on s1', subject, holder, sink, [1, 0, 0]);

    var r2 = round(s1, '2025-02-28', holder);
    state('state 3 holder leads r2 on s1', subject, holder, sink, [1, 1, 0]);

    var l2 = link(r2, subject);
    state('state 4 subject participates in a second round of s1',
        subject, holder, sink, [1, 1, 0]);

    var r3 = round(s2, '2025-03-31', holder);
    state('state 5 holder leads r3 on s2', subject, holder, sink, [1, 2, 0]);

    var l3 = link(r3, subject);
    state('state 6 subject participates in a round of s2', subject, holder, sink, [2, 2, 0]);

    drop(LINK, l3);
    state('state 7 the s2 participation is deleted', subject, holder, sink, [1, 2, 0]);

    drop(LINK, l2);
    state('state 8 the s1 participation is deleted, the lead path stands',
        subject, holder, sink, [1, 2, 0]);

    // The repoint is the only mutation that must recalculate TWO investors: the previous
    // lead loses its last path and the new lead gains its first.
    var repoint = new GlideRecord(ROUND);
    repoint.get(r1);
    repoint.setValue('lead_investor', sink);
    repoint.update();
    state('state 9 r1 is repointed from subject to sink', subject, holder, sink, [0, 2, 1]);

    drop(ROUND, r2);
    state('state 10 r2 is deleted', subject, holder, sink, [0, 1, 1]);

    drop(ROUND, r1);
    state('state 11 r1 is deleted', subject, holder, sink, [0, 1, 0]);

    // Stored and derived must agree for all three investors, with no recalculation between
    // the last mutation and the comparison.
    var service = new InvestorPortfolioService();
    assertEqual({ name: 'stored equals derived for subject',
        shouldbe: service.countPortfolio(subject), value: stored(subject) });
    assertEqual({ name: 'stored equals derived for holder',
        shouldbe: service.countPortfolio(holder), value: stored(holder) });
    assertEqual({ name: 'stored equals derived for sink',
        shouldbe: service.countPortfolio(sink), value: stored(sink) });

    drop(ROUND, r3);
    stepResult.setOutputMessage('portfolio_count walked subject 0-1-1-1-1-2-1-1-0-0-0, ' +
        'holder 0-0-1-1-2-2-2-2-2-1-1 and sink 0-0-0-0-0-0-0-0-1-1-0 across lead insert, ' +
        'participation insert and delete, lead repoint and round delete; stored agrees ' +
        'with derived for all three.');
    return true;
})(outputs, steps, params, stepResult, assertEqual);
```

Every record this step creates is created inside the test and is rolled back with it, so the two startups, the three investors, the three rounds and the two join rows leave nothing behind.

**`x_bst_startuptrk_investor.type` is the choice asymmetry, and step 100 asserts it as a property of the choice list rather than of the mapper.** Its list is `VC`, `Angel`, `PE`, `Corporate`, `Accelerator` and declares **no** `Other` member, so there is no value an unmatched investor type could be coerced to. Step 100 asserts the list holds exactly those five and that `Other` is absent from it. What the **ingestion pipeline** does with an unmatched type — leave the column unwritten, log the event, and still insert the row, because `type` is not mandatory — is asserted in [suite 10](#suite-10--bst-flow-suite--ingestion), which is where the pipeline is under test.

### Suite 5 — `BST CRUD suite — fundinground`

One test, `BST CRUD — fundinground`. Table `x_bst_startuptrk_fundinground`, 8 columns. Step 20 creates the parent startup with `name` = `ATF Round Parent`, `headquarters_location` = `Boston, MA`, `active` = `true`, and a second **Record Insert** at step 25 creates an investor `ATF Round Lead` for `lead_investor`.

| Skeleton step | Value for this table |
| --- | --- |
| 30 insert | `startup` = step 20 `record_id`, `round_date` = `2025-06-30`, `round_type` = `Series A`, `amount_usd` = `12000000`, `lead_investor` = step 25 `record_id`, `source_url` = `https://example.invalid/round/atf` |
| 40 validation | `record_id` = step 30 `record_id`. `startup` `is` the step 20 `record_id`; `round_date` `is` `2025-06-30`; `round_type` `is` `Series A`; `lead_investor` `is` the step 25 `record_id`; `source_url` `is` `https://example.invalid/round/atf` |
| 50 query | `Sys ID` `is` step 30 `record_id` — **exactly one record** |
| 60 update | `valuation_usd` = `90000000`, `round_type` = `Series B`, `source_url` = `https://example.invalid/round/atf-b` |
| 70 validation | `record_id` = step 30 `record_id`. `round_type` `is` `Series B`; `source_url` `is` `https://example.invalid/round/atf-b`; and the untouched `startup` `is` the step 20 `record_id`, `round_date` `is` `2025-06-30`, `lead_investor` `is` the step 25 `record_id` |
| 80 mandatory | `startup` omitted, `round_date` supplied — **Record was not inserted** |
| 90 mandatory | `round_date` omitted, `startup` supplied — **Record was not inserted** |
| 100 choice | `TABLE` = `x_bst_startuptrk_fundinground`; `PARENT_FIELD_VALUES` = `{ startup: steps(STEP_20_PARENT).record_id, round_date: '2025-06-30' }`; `COLUMNS` = one entry: `round_type`, `max_length` 40, `declares_other` **false**, members `Pre-Seed`, `Seed`, `Series A`, `Series B`, `Series C+`, `Growth`, `Public`, `Acquired` |
| 110 delete / 120 re-query | `record_id` = step 30 `record_id`; then `Sys ID` `is` that same identifier — **No records match** |

One addition specific to this table, appended after step 120.

| Step | Step configuration | Purpose |
| --- | --- | --- |
| 130 | **Run Server Side Script** | The `participating_investors` projection: the join table is authoritative, the column is maintained by the business rule, and `lead_investor` stays distinct from the participant set. Script below. |

#### Step 130 — the `participating_investors` projection

`participating_investors` is a **read-only `glide_list` column of `max_length` 4000** referencing `x_bst_startuptrk_investor`. It is not written by a caller: `x_bst_startuptrk_m2m_round_investor` is authoritative, and the column is a projection refreshed by `InvestorPortfolioService.refreshRoundParticipants()` from the business rule on the join table. As with `portfolio_count`, the `read_only` attribute does not stop a server-side script write — so this step asserts what actually protects the projection, which is that the business rule **recomputes it from the join table** and overwrites anything a script put there.

```javascript
(function(outputs, steps, params, stepResult, assertEqual) {
    var ROUND = 'x_bst_startuptrk_fundinground';
    var LINK = 'x_bst_startuptrk_m2m_round_investor';
    var FIELD = 'participating_investors';

    // 1. The dictionary declaration.
    var dict = new GlideRecord('sys_dictionary');
    dict.addQuery('name', ROUND);
    dict.addQuery('element', FIELD);
    dict.setLimit(1);
    dict.query();
    assertEqual({ name: FIELD + ' has a dictionary record', shouldbe: true, value: dict.next() });
    assertEqual({ name: FIELD + ' is a list column',
        shouldbe: 'glide_list', value: dict.getValue('internal_type') });
    assertEqual({ name: FIELD + ' references the investor table',
        shouldbe: 'x_bst_startuptrk_investor', value: dict.getValue('reference') });
    assertEqual({ name: FIELD + ' is declared read-only',
        shouldbe: true, value: String(dict.getValue('read_only')) === 'true' });
    assertEqual({ name: FIELD + ' holds 4000 characters',
        shouldbe: 4000, value: parseInt(dict.getValue('max_length'), 10) });

    // Fixtures of this step's own.
    var parent = new GlideRecord('x_bst_startuptrk_startup');
    parent.initialize();
    parent.setValue('name', 'ATF Participants Parent');
    parent.setValue('headquarters_location', 'Boston, MA');
    parent.setValue('active', true);
    var parentId = parent.insert();

    function investor(name) {
        var gr = new GlideRecord('x_bst_startuptrk_investor');
        gr.initialize();
        gr.setValue('name', name);
        gr.setValue('type', 'VC');
        return gr.insert();
    }
    var lead = investor('ATF Participants Lead');
    var p1 = investor('ATF Participants One');
    var p2 = investor('ATF Participants Two');

    var round = new GlideRecord(ROUND);
    round.initialize();
    round.setValue('startup', parentId);
    round.setValue('round_date', '2025-09-30');
    round.setValue('round_type', 'Series B');
    round.setValue('lead_investor', lead);
    var roundId = round.insert();

    function projection() {
        var gr = new GlideRecord(ROUND);
        if (!gr.get(roundId)) {
            return '~missing~';
        }
        return String(gr.getValue(FIELD) || '');
    }
    function members() {
        var raw = projection();
        if (raw === '') {
            return [];
        }
        return raw.split(',');
    }

    // 2. A round with no join rows projects nothing, even though it has a lead investor.
    assertEqual({ name: 'no join rows means an empty projection', shouldbe: '', value: projection() });

    // 3. Two join rows project both investors, and the join table is authoritative.
    var l1 = new GlideRecord(LINK);
    l1.initialize();
    l1.setValue('funding_round', roundId);
    l1.setValue('investor', p1);
    var link1 = l1.insert();

    var l2 = new GlideRecord(LINK);
    l2.initialize();
    l2.setValue('funding_round', roundId);
    l2.setValue('investor', p2);
    l2.insert();

    var projected = members();
    assertEqual({ name: 'two join rows project two members', shouldbe: 2, value: projected.length });
    assertEqual({ name: 'the first participant is projected',
        shouldbe: true, value: projected.indexOf(p1) !== -1 });
    assertEqual({ name: 'the second participant is projected',
        shouldbe: true, value: projected.indexOf(p2) !== -1 });

    // 4. lead_investor is a first-class reference and is NOT a member of the participant set.
    assertEqual({ name: 'the lead investor is not projected as a participant',
        shouldbe: -1, value: projected.indexOf(lead) });
    var leadCheck = new GlideRecord(ROUND);
    leadCheck.get(roundId);
    assertEqual({ name: 'lead_investor is still the lead',
        shouldbe: lead, value: String(leadCheck.getValue('lead_investor')) });

    // 5. A direct script write to the projection does not survive: the next join-table
    //    change recomputes the column from the join rows and discards it.
    var tamper = new GlideRecord(ROUND);
    tamper.get(roundId);
    tamper.setValue(FIELD, lead);
    tamper.update();
    var l3 = new GlideRecord(LINK);
    l3.initialize();
    l3.setValue('funding_round', roundId);
    l3.setValue('investor', lead);
    l3.insert();
    var recomputed = members();
    assertEqual({ name: 'the projection is recomputed from the join table, not from the write',
        shouldbe: 3, value: recomputed.length });

    // 6. Deleting a join row removes exactly that member.
    var drop = new GlideRecord(LINK);
    drop.get(link1);
    drop.deleteRecord();
    var afterDelete = members();
    assertEqual({ name: 'deleting a join row drops one member',
        shouldbe: 2, value: afterDelete.length });
    assertEqual({ name: 'the deleted participant is gone from the projection',
        shouldbe: -1, value: afterDelete.indexOf(p1) });

    stepResult.setOutputMessage('participating_investors projection asserted: join table ' +
        'authoritative, lead_investor distinct, projection recomputed on every join change.');
    return true;
})(outputs, steps, params, stepResult, assertEqual);
```

`amount_usd` and `valuation_usd` are written at step 30 and step 60 and are **not** asserted for readability here. Both are premium fields, and their read outcome per role is asserted in [suite 8](#suite-8--bst-acl-suite--premium-fields-by-role), cells 6.1 to 6.3 and 7.1 to 7.3.

### Suite 6 — `BST CRUD suite — jobposting`

One test, `BST CRUD — jobposting`. Table `x_bst_startuptrk_jobposting`, 9 columns, display column `title`. Step 20 creates the parent startup with `name` = `ATF Job Parent`, `headquarters_location` = `Boston, MA`, `active` = `true`. This table carries **three** choice columns, only one of which declares `Other`.

| Skeleton step | Value for this table |
| --- | --- |
| 30 insert | `startup` = step 20 `record_id`, `title` = `ATF Staff Engineer`, `department` = `Engineering`, `remote_type` = `Hybrid`, `seniority` = `Senior`, `location` = `Boston, MA`, `posted_date` = `2026-01-15`, `url` = `https://example.invalid/jobs/atf` — `active` is **not** supplied |
| 40 validation | `record_id` = step 30 `record_id`. `title` `is` `ATF Staff Engineer`; `department` `is` `Engineering`; `remote_type` `is` `Hybrid`; `seniority` `is` `Senior`; `posted_date` `is` `2026-01-15`; and **`active` `is` `true`**, the default applied without being supplied |
| 50 query | `Sys ID` `is` step 30 `record_id` — **exactly one record** |
| 60 update | `active` = `false`, `department` = `Product`, `seniority` = `Lead`, `remote_type` = `Remote` |
| 70 validation | `record_id` = step 30 `record_id`. `active` `is` `false`; `department` `is` `Product`; `seniority` `is` `Lead`; `remote_type` `is` `Remote`; and the untouched `title` `is` `ATF Staff Engineer`, `startup` `is` the step 20 `record_id`, `posted_date` `is` `2026-01-15` |
| 80 mandatory | `startup` omitted, `title` supplied — **Record was not inserted** |
| 90 mandatory | `title` omitted, `startup` supplied — **Record was not inserted** |
| 100 choice | `TABLE` = `x_bst_startuptrk_jobposting`; `PARENT_FIELD_VALUES` = `{ startup: steps(STEP_20_PARENT).record_id, title: 'ATF Choice Probe' }`; `COLUMNS` = three entries: `department`, 40, **true**, members `Engineering`, `Sales`, `Marketing`, `Product`, `Operations`, `Other`; `remote_type`, 20, **false**, members `Onsite`, `Hybrid`, `Remote`; `seniority`, 20, **false**, members `Entry`, `Mid`, `Senior`, `Lead`, `Executive` |
| 110 delete / 120 re-query | `record_id` = step 30 `record_id`; then `Sys ID` `is` that same identifier — **No records match** |

`active` carries a default of `true` and is **not** mandatory on this table, unlike `x_bst_startuptrk_startup.active` which is both. Step 40 asserts the default applied without being supplied, and step 60 then sets it to `false` so step 70 asserts a supplied value overrides the default. Together those two make the default checkable in both directions on a column that has no mandatory-omission step.

### Suite 7 — `BST CRUD suite — newsarticle`

One test, `BST CRUD — newsarticle`. Table `x_bst_startuptrk_newsarticle`, 6 columns, display column `title`. Step 20 creates the parent startup with `name` = `ATF News Parent`, `headquarters_location` = `Boston, MA`, `active` = `true`. This table has **no** choice column, so step 100 is replaced by the date-column assertion below.

| Skeleton step | Value for this table |
| --- | --- |
| 30 insert | `startup` = step 20 `record_id`, `title` = `ATF covers Startup Alpha`, `source` = `ATF Wire`, `published_date` = `2026-02-01`, `url` = `https://example.invalid/news/atf` |
| 40 validation | `record_id` = step 30 `record_id`. `title` `is` `ATF covers Startup Alpha`; `startup` `is` the step 20 `record_id`; `source` `is` `ATF Wire`; `published_date` `is` `2026-02-01`; `url` `is` `https://example.invalid/news/atf` |
| 50 query | `Sys ID` `is` step 30 `record_id` — **exactly one record** |
| 60 update | `summary` = `Updated by ATF`, `published_date` = `2026-02-29` — a real day in a leap year |
| 70 validation | `record_id` = step 30 `record_id`. `summary` `is` `Updated by ATF`; `published_date` `is` `2026-02-29`; and the untouched `title` `is` `ATF covers Startup Alpha`, `startup` `is` the step 20 `record_id`, `source` `is` `ATF Wire` |
| 80 mandatory | `startup` omitted, `title` supplied — **Record was not inserted** |
| 90 mandatory | `title` omitted, `startup` supplied — **Record was not inserted** |
| 100 replaced | **Run Server Side Script** — the `published_date` round trip and refusal, script below |
| 110 delete / 120 re-query | `record_id` = step 30 `record_id`; then `Sys ID` `is` that same identifier — **No records match** |

#### Step 100 — the `published_date` round trip and refusal

**This is a record-and-API test, not an ingestion test.** NewsArticle is excluded from ingestion entirely — neither flow writes it and there is no NewsArticle sample CSV — so no ingestion date parser is in this table's path and none is called here. What is in its path is the `glide_date` column itself and the date validation of the two NewsArticle write operations, `POST /news` and `PUT /news/{id}`, both of which declare `published_date` with validation type `date`. Both are asserted.

```javascript
(function(outputs, steps, params, stepResult, assertEqual) {
    var TABLE = 'x_bst_startuptrk_newsarticle';
    var FIELD = 'published_date';

    // 1. The dictionary declaration: a date column, not a date/time column.
    var dict = new GlideRecord('sys_dictionary');
    dict.addQuery('name', TABLE);
    dict.addQuery('element', FIELD);
    dict.setLimit(1);
    dict.query();
    assertEqual({ name: FIELD + ' has a dictionary record', shouldbe: true, value: dict.next() });
    assertEqual({ name: FIELD + ' is a date column, carrying no time part',
        shouldbe: 'glide_date', value: dict.getValue('internal_type') });
    assertEqual({ name: FIELD + ' is not mandatory',
        shouldbe: false, value: String(dict.getValue('mandatory')) === 'true' });

    var parent = new GlideRecord('x_bst_startuptrk_startup');
    parent.initialize();
    parent.setValue('name', 'ATF Date Parent');
    parent.setValue('headquarters_location', 'Boston, MA');
    parent.setValue('active', true);
    var parentId = parent.insert();

    function roundTrip(day) {
        var gr = new GlideRecord(TABLE);
        gr.initialize();
        gr.setValue('startup', parentId);
        gr.setValue('title', 'ATF date ' + day);
        gr.setValue(FIELD, day);
        var id = gr.insert();
        var read = new GlideRecord(TABLE);
        if (!read.get(id)) {
            return { id: '', stored: '~not inserted~' };
        }
        return { id: id, stored: String(read.getValue(FIELD) || '') };
    }

    // 2. The record round trip: a stored yyyy-MM-dd value reads back byte for byte, on an
    //    ordinary day, on a leap day, and at both ends of a month.
    var days = ['2026-02-01', '2026-02-28', '2024-02-29', '2025-12-31', '2026-01-01'];
    var i = 0;
    var created = [];
    for (i = 0; i !== days.length; i++) {
        var trip = roundTrip(days[i]);
        created.push(trip.id);
        assertEqual({ name: FIELD + ' round trips ' + days[i],
            shouldbe: days[i], value: trip.stored });
    }

    // 3. A blank is legal, because the column is not mandatory.
    var blank = roundTrip('');
    created.push(blank.id);
    assertEqual({ name: FIELD + ' accepts a blank', shouldbe: '', value: blank.stored });

    // 4. The API refusal, through the same validation the two NewsArticle write operations
    //    declare for this column. A malformed value and a value that is not a real calendar
    //    day are refused with two DIFFERENT messages, so a caller can tell them apart.
    var spec = [
        { field: 'title', type: 'string', max: 255, mandatory: true },
        { field: FIELD, type: 'date' }
    ];
    var helper = new RestQueryHelper();

    var malformed = ['01/02/2026', '2026-2-1', '20260201', 'yesterday', '2026-02-01T09:00:00'];
    for (i = 0; i !== malformed.length; i++) {
        var badShape = helper.validateBody({ title: 'ATF', published_date: malformed[i] },
            spec, false);
        assertEqual({ name: FIELD + ' refuses the malformed value ' + malformed[i],
            shouldbe: false, value: badShape.ok });
        assertEqual({ name: FIELD + ' names the required format for ' + malformed[i],
            shouldbe: FIELD + ' must be a yyyy-MM-dd date', value: badShape.error });
    }

    var impossible = ['2026-02-30', '2026-13-01', '2026-00-10', '2026-04-31', '2025-02-29'];
    for (i = 0; i !== impossible.length; i++) {
        var badDay = helper.validateBody({ title: 'ATF', published_date: impossible[i] },
            spec, false);
        assertEqual({ name: FIELD + ' refuses the impossible day ' + impossible[i],
            shouldbe: false, value: badDay.ok });
        assertEqual({ name: FIELD + ' names the calendar failure for ' + impossible[i],
            shouldbe: FIELD + ' must be a date that exists in the calendar', value: badDay.error });
    }

    // 5. The two accepted forms above are accepted by the same validation, so the refusals
    //    are not a blanket rejection.
    var good = helper.validateBody({ title: 'ATF', published_date: '2024-02-29' }, spec, false);
    assertEqual({ name: FIELD + ' accepts a real leap day', shouldbe: true, value: good.ok });
    assertEqual({ name: FIELD + ' passes the accepted value through unchanged',
        shouldbe: '2024-02-29', value: good.values.published_date });

    // 6. The refusal is declared by both NewsArticle write operations, not just asserted here.
    var paths = [{ p: '/news', m: 'POST' }, { p: '/news/{id}', m: 'PUT' }];
    for (i = 0; i !== paths.length; i++) {
        var op = new GlideRecord('sys_ws_operation');
        op.addQuery('relative_path', paths[i].p);
        op.addQuery('http_method', paths[i].m);
        op.setLimit(1);
        op.query();
        assertEqual({ name: paths[i].m + ' ' + paths[i].p + ' exists',
            shouldbe: true, value: op.next() });
        assertEqual({ name: paths[i].m + ' ' + paths[i].p + ' validates ' + FIELD + ' as a date',
            shouldbe: true,
            value: String(op.getValue('operation_script'))
                .indexOf("{ field: '" + FIELD + "', type: 'date' }") !== -1 });
    }

    for (i = 0; i !== created.length; i++) {
        var cleanup = new GlideRecord(TABLE);
        if (created[i]) {
            if (cleanup.get(created[i])) {
                cleanup.deleteRecord();
            }
        }
    }

    stepResult.setOutputMessage(FIELD + ' asserted: ' + days.length + ' round trips, a blank, ' +
        malformed.length + ' malformed and ' + impossible.length +
        ' impossible values refused with distinct messages, both write operations declared.');
    return true;
})(outputs, steps, params, stepResult, assertEqual);
```

This table is **manual-entry and CSV-import only**. Neither ingestion flow writes it, there is no NewsArticle sample CSV, and no flow test in [suite 10](#suite-10--bst-flow-suite--ingestion) references it. The exclusion is recorded in [`../gaps-and-flags.md`](../gaps-and-flags.md).

## Suite 8 — `BST ACL suite — premium fields by role`

One suite, **21 tests**: the full cross-product of the **7 premium fields** by the **3 roles**. Every cell is a separate test with its own result, so a single failing cell is visible by name rather than hidden inside an aggregate.

### The seven premium fields

Field-level read ACLs are named in `table.field` form. These are the seven, spelled exactly:

| # | Field-level read ACL |
| --- | --- |
| 1 | `x_bst_startuptrk_startup.total_funding_usd` |
| 2 | `x_bst_startuptrk_startup.institutional_funding_last_5yrs` |
| 3 | `x_bst_startuptrk_founder.contact_email` |
| 4 | `x_bst_startuptrk_executive.contact_email` |
| 5 | `x_bst_startuptrk_investor.aum_usd` |
| 6 | `x_bst_startuptrk_fundinground.amount_usd` |
| 7 | `x_bst_startuptrk_fundinground.valuation_usd` |

`contact_email` is a **distinct ACL on each of two tables**, fields 3 and 4. They are two records, two tests per role, and neither covers the other.

### The three roles

| # | Role | Expected read of a premium field |
| --- | --- | --- |
| 1 | `x_bst_startuptrk.admin` | **Reads** |
| 2 | `x_bst_startuptrk.premium_user` | **Reads** |
| 3 | `x_bst_startuptrk.user` | **Denied** |

### The 21 cells

Each row is one test. Build all twenty-one.

| Cell | Test name | Field | Role | Expected outcome |
| --- | --- | --- | --- | --- |
| ACL-1.1 | `BST ACL — startup.total_funding_usd — admin` | `x_bst_startuptrk_startup.total_funding_usd` | `x_bst_startuptrk.admin` | **Reads** — value returned, key present |
| ACL-1.2 | `BST ACL — startup.total_funding_usd — premium_user` | `x_bst_startuptrk_startup.total_funding_usd` | `x_bst_startuptrk.premium_user` | **Reads** — value returned, key present |
| ACL-1.3 | `BST ACL — startup.total_funding_usd — user` | `x_bst_startuptrk_startup.total_funding_usd` | `x_bst_startuptrk.user` | **DENIED** — key absent from the response object |
| ACL-2.1 | `BST ACL — startup.institutional_funding_last_5yrs — admin` | `x_bst_startuptrk_startup.institutional_funding_last_5yrs` | `x_bst_startuptrk.admin` | **Reads** — value returned, key present |
| ACL-2.2 | `BST ACL — startup.institutional_funding_last_5yrs — premium_user` | `x_bst_startuptrk_startup.institutional_funding_last_5yrs` | `x_bst_startuptrk.premium_user` | **Reads** — value returned, key present |
| ACL-2.3 | `BST ACL — startup.institutional_funding_last_5yrs — user` | `x_bst_startuptrk_startup.institutional_funding_last_5yrs` | `x_bst_startuptrk.user` | **DENIED** — key absent from the response object |
| ACL-3.1 | `BST ACL — founder.contact_email — admin` | `x_bst_startuptrk_founder.contact_email` | `x_bst_startuptrk.admin` | **Reads** — value returned, key present |
| ACL-3.2 | `BST ACL — founder.contact_email — premium_user` | `x_bst_startuptrk_founder.contact_email` | `x_bst_startuptrk.premium_user` | **Reads** — value returned, key present |
| ACL-3.3 | `BST ACL — founder.contact_email — user` | `x_bst_startuptrk_founder.contact_email` | `x_bst_startuptrk.user` | **DENIED** — key absent from the response object |
| ACL-4.1 | `BST ACL — executive.contact_email — admin` | `x_bst_startuptrk_executive.contact_email` | `x_bst_startuptrk.admin` | **Reads** — value returned, key present |
| ACL-4.2 | `BST ACL — executive.contact_email — premium_user` | `x_bst_startuptrk_executive.contact_email` | `x_bst_startuptrk.premium_user` | **Reads** — value returned, key present |
| ACL-4.3 | `BST ACL — executive.contact_email — user` | `x_bst_startuptrk_executive.contact_email` | `x_bst_startuptrk.user` | **DENIED** — key absent from the response object |
| ACL-5.1 | `BST ACL — investor.aum_usd — admin` | `x_bst_startuptrk_investor.aum_usd` | `x_bst_startuptrk.admin` | **Reads** — value returned, key present |
| ACL-5.2 | `BST ACL — investor.aum_usd — premium_user` | `x_bst_startuptrk_investor.aum_usd` | `x_bst_startuptrk.premium_user` | **Reads** — value returned, key present |
| ACL-5.3 | `BST ACL — investor.aum_usd — user` | `x_bst_startuptrk_investor.aum_usd` | `x_bst_startuptrk.user` | **DENIED** — key absent from the response object |
| ACL-6.1 | `BST ACL — fundinground.amount_usd — admin` | `x_bst_startuptrk_fundinground.amount_usd` | `x_bst_startuptrk.admin` | **Reads** — value returned, key present |
| ACL-6.2 | `BST ACL — fundinground.amount_usd — premium_user` | `x_bst_startuptrk_fundinground.amount_usd` | `x_bst_startuptrk.premium_user` | **Reads** — value returned, key present |
| ACL-6.3 | `BST ACL — fundinground.amount_usd — user` | `x_bst_startuptrk_fundinground.amount_usd` | `x_bst_startuptrk.user` | **DENIED** — key absent from the response object |
| ACL-7.1 | `BST ACL — fundinground.valuation_usd — admin` | `x_bst_startuptrk_fundinground.valuation_usd` | `x_bst_startuptrk.admin` | **Reads** — value returned, key present |
| ACL-7.2 | `BST ACL — fundinground.valuation_usd — premium_user` | `x_bst_startuptrk_fundinground.valuation_usd` | `x_bst_startuptrk.premium_user` | **Reads** — value returned, key present |
| ACL-7.3 | `BST ACL — fundinground.valuation_usd — user` | `x_bst_startuptrk_fundinground.valuation_usd` | `x_bst_startuptrk.user` | **DENIED** — key absent from the response object |

Twenty-one cells: **14 read** (cells `*.1` and `*.2`) and **7 denied** (cells `*.3`). The same matrix is stated in [`../access-control.md`](../access-control.md), which also names the reviewer entry that owns it; the two documents must agree cell for cell.

### Three independent oracles per cell, and the helper that is never one of them

Every one of the 21 cells asserts its outcome through **three separate oracles**, checked in this order. Build all three into every cell.

| # | Oracle | What it asks | What it catches that the others do not |
| --: | --- | --- | --- |
| 1 | **The platform element check** — `gr.getElement(FIELD).canRead()` on a `GlideRecordSecure` read | Does the **access-control engine** grant this element to this caller? | It is the engine's own answer, with no application code between the assertion and the decision. |
| 2 | **The serialised response object** — `new RestResponseBuilder().serialize(gr, fields)` | Does the object a caller receives **carry the key at all**? | A serialiser that leaked or nulled a denied field, which oracle 1 passes. |
| 3 | **The control column** — a non-premium column on the same record | Did the **table-level** grant pass, so that oracle 1's answer is about the field rather than about the record? | Nothing being readable at all, which oracles 1 and 2 cannot distinguish on their own. |

**Do not use `RestResponseBuilder.canRead()` as an oracle anywhere in this suite. Assert `gr.getElement(FIELD).canRead()` directly.** The consequence of the shortcut is a silent one: that method is a one-line wrapper around the same element check, so a helper hard-coded to return `true`, or one that swallowed the element check, passes all 21 cells while the platform access control is wrong in either direction. Oracle 2 is the only place the helper may appear, and there it is the **subject** of the assertion rather than its authority. `D-119` carries the decision.

The API-level spot check that [`../validation-checklist.md`](../validation-checklist.md) requires for criterion 2 reads raw JSON off a live response, so it is a fourth oracle sitting outside this suite entirely.

### The step sequence for a `*.1` cell — administrator, expected to read

Seven tests use this shape. The role under test is `x_bst_startuptrk.admin`, which is also the role that writes the fixtures, so one user serves both purposes.

| Step | Step configuration | Category | Inputs |
| --- | --- | --- | --- |
| 5 | **Create a User** | Server - Independent | `first_name` = `BST ATF`, `last_name` = `admin`, `roles` = **exactly** `x_bst_startuptrk.admin`, `groups` empty, `impersonate` false. Full input list under [Technique (a)](#technique-a--impersonation). |
| 8 | **Run Server Side Script** | Server - Independent | Role-set verification for the step 5 user. `EXPECTED` = `x_bst_startuptrk.admin`, `STEP_CREATE_USER` = the step 5 `sys_id`. **Present in this test, not inherited from another.** |
| 10 | **Impersonate** | Server - Independent | `user` = the step 5 output. |
| 20 | **Record Insert** | Server - Independent | The parent fixture, on the tables that need one. `enforce_security` = **true**; `assert_type` = **Record successfully inserted**. Omit for fields 1, 2 and 5. |
| 30 | **Record Insert** | Server - Independent | The subject record, with the premium field **populated to a known non-empty value**. `enforce_security` = **true**; `assert_type` = **Record successfully inserted**. |
| 50 | **Run Server Side Script** | Server - Independent | The **read** assertion, script under [The read-assertion script](#the-read-assertion-script-one-script-for-all-21-cells). `EXPECT_READABLE` = `true`. |

### The step sequence for a `*.2` cell — premium user, expected to read

Seven tests use this shape. Two users are needed: the administrator writes the fixtures, then the premium user attempts the read.

| Step | Step configuration | Category | Inputs |
| --- | --- | --- | --- |
| 5 | **Create a User** | Server - Independent | `roles` = **exactly** `x_bst_startuptrk.admin`. The fixture writer. |
| 8 | **Run Server Side Script** | Server - Independent | Role-set verification for the step 5 user. `EXPECTED` = `x_bst_startuptrk.admin`. |
| 10 | **Impersonate** | Server - Independent | `user` = the step 5 output. |
| 20 | **Record Insert** | Server - Independent | Parent fixture where required; `enforce_security` = **true**. Omit for fields 1, 2 and 5. |
| 30 | **Record Insert** | Server - Independent | Subject record with the premium field populated; `enforce_security` = **true**; `assert_type` = **Record successfully inserted**. |
| 35 | **Create a User** | Server - Independent | `last_name` = `premium`, `roles` = **exactly** `x_bst_startuptrk.premium_user`, `groups` empty. |
| 38 | **Run Server Side Script** | Server - Independent | Role-set verification for the **step 35** user. `EXPECTED` = `x_bst_startuptrk.premium_user`, `STEP_CREATE_USER` = the step 35 `sys_id`. |
| 40 | **Impersonate** | Server - Independent | `user` = the step 35 output. |
| 50 | **Run Server Side Script** | Server - Independent | The read assertion. `EXPECT_READABLE` = `true`. |

### The step sequence for a `*.3` cell — base user, expected to be DENIED

Seven tests use this shape. It is identical to a `*.2` cell except that step 35 grants `x_bst_startuptrk.user` and step 50 runs with `EXPECT_READABLE` = `false`.

| Step | Step configuration | Category | Inputs |
| --- | --- | --- | --- |
| 5 | **Create a User** | Server - Independent | `roles` = **exactly** `x_bst_startuptrk.admin`. The fixture writer. |
| 8 | **Run Server Side Script** | Server - Independent | Role-set verification for the step 5 user. `EXPECTED` = `x_bst_startuptrk.admin`. |
| 10 | **Impersonate** | Server - Independent | `user` = the step 5 output. |
| 20 | **Record Insert** | Server - Independent | Parent fixture where required; `enforce_security` = **true**. Omit for fields 1, 2 and 5. |
| 30 | **Record Insert** | Server - Independent | Subject record with the premium field populated; `enforce_security` = **true**; `assert_type` = **Record successfully inserted**. |
| 35 | **Create a User** | Server - Independent | `last_name` = `base`, `roles` = **exactly** `x_bst_startuptrk.user`, `groups` empty. This is the user that must be denied. |
| 38 | **Run Server Side Script** | Server - Independent | Role-set verification for the **step 35** user. `EXPECTED` = `x_bst_startuptrk.user`. **This step is what makes the denial meaningful**; a user that silently acquired `admin` turns the cell into a false pass. |
| 40 | **Impersonate** | Server - Independent | `user` = the step 35 output, holding `x_bst_startuptrk.user` and nothing else. |
| 50 | **Run Server Side Script** | Server - Independent | The read assertion with `EXPECT_READABLE` = `false`, which switches every expectation to the denial branch. |

**Every one of the 21 tests carries its own step 8, and the 14 two-user cells carry their own step 38 as well.** Verification is never done once for a suite and relied on by the other cells: each `Create a User` step creates a **new** `sys_user` record inside that test's transaction, and the framework rolls it back when the test ends, so there is no shared user for a suite-level check to have verified. A cell that skipped its own verification would be asserting a denial against a user whose role set nothing in that test had established. That is 21 step-8 verifications and 14 step-38 verifications, 35 in total.

### The read-assertion script, one script for all 21 cells

One script serves all 21 cells. `EXPECT_READABLE` selects the branch: `true` for the 14 read cells, `false` for the 7 denied cells. Substitute the table, the premium field and the control column from [Per-cell fixture and control values](#per-cell-fixture-and-control-values).

```javascript
(function(outputs, steps, params, stepResult, assertEqual) {
    // ---- per-cell substitution ----
    var TABLE = 'x_bst_startuptrk_startup';
    var FIELD = 'total_funding_usd';
    var CONTROL = 'name';
    var EXPECT_READABLE = false;          // true for a *.1 or *.2 cell, false for a *.3 cell

    // Contract 1: the generated sys_ids of two steps of this test.
    var STEP_30_SUBJECT = '';             // <- the Record Insert step at display order 30
    var STEP_USER_UNDER_TEST = '';        // <- the Create a User step whose role is under
                                          //    test: display order 5 on a *.1 cell,
                                          //    display order 35 on a *.2 or *.3 cell
    // ---- end of per-cell substitution ----

    var subjectId = steps(STEP_30_SUBJECT).record_id;
    var gr = new GlideRecordSecure(TABLE);

    if (!gr.get(subjectId)) {
        stepResult.setFailed('Record ' + subjectId + ' is not readable by the impersonated ' +
            'user. The table-level read control of Layer 1 is not granting, so the ' +
            'field-level control never evaluates and this cell proves nothing either way.');
        return false;
    }

    // ORACLE 1 - the access-control engine, asked directly. Not through
    // RestResponseBuilder.canRead(), which wraps this same call and would be asserting
    // the helper against itself.
    var element = gr.getElement(FIELD);
    assertEqual({ name: FIELD + ' resolves to an element on ' + TABLE,
        shouldbe: true, value: !!element });
    assertEqual({ name: 'platform element read on ' + FIELD + ' is ' + EXPECT_READABLE,
        shouldbe: EXPECT_READABLE, value: element.canRead() });

    // ORACLE 2 - the response object a caller receives. The builder is the SUBJECT here,
    // never the authority: a serialiser that leaked or nulled a denied field fails this
    // block even though oracle 1 passed.
    var body = new RestResponseBuilder().serialize(gr, [FIELD, CONTROL]);
    var present = Object.prototype.hasOwnProperty.call(body, FIELD);
    assertEqual({ name: FIELD + ' key presence in the response object is ' + EXPECT_READABLE,
        shouldbe: EXPECT_READABLE, value: present });

    if (EXPECT_READABLE) {
        // The value must be the one written at step 30, not a blank standing in for it.
        assertEqual({ name: FIELD + ' returns a non-empty value',
            shouldbe: true,
            value: body[FIELD] !== null && body[FIELD] !== undefined && String(body[FIELD]) !== '' });
        assertEqual({ name: FIELD + ' element value agrees with the serialised value',
            shouldbe: String(gr.getValue(FIELD)), value: String(body[FIELD]) });
    } else {
        // OMITTED, NOT NULLED. The secured read returns an EMPTY STRING for a denied field
        // rather than an error, so a falsy, empty or null check would pass against a
        // response carrying "total_funding_usd": "" - the exact behaviour the contract
        // forbids. Only hasOwnProperty distinguishes omitted from nulled.
        assertEqual({ name: FIELD + ' key is absent, not present and empty',
            shouldbe: false, value: present });
        assertEqual({ name: FIELD + ' is not present under any falsy value either',
            shouldbe: 'undefined', value: typeof body[FIELD] });
    }

    // ORACLE 3 - the control column. It must read under BOTH branches: on a denied cell it
    // proves Layer 1 granted and Layer 3 denied, which is the only combination that
    // satisfies the requirement; on a read cell it proves the fixture is intact.
    assertEqual({ name: CONTROL + ' element read is granted',
        shouldbe: true, value: gr.getElement(CONTROL).canRead() });
    assertEqual({ name: CONTROL + ' key is present in the response object',
        shouldbe: true, value: Object.prototype.hasOwnProperty.call(body, CONTROL) });
    assertEqual({ name: CONTROL + ' returns a value',
        shouldbe: true, value: String(body[CONTROL] || '') !== '' });

    // The impersonation actually took effect. A cell whose Impersonate step silently failed
    // would be reading as the operator, and on a *.3 cell that is a false pass with no
    // other symptom.
    assertEqual({ name: 'the session is the user whose role is under test',
        shouldbe: String(steps(STEP_USER_UNDER_TEST).user), value: String(gs.getUserID()) });
    assertEqual({ name: 'the session does not hold the platform administrator role',
        shouldbe: false, value: gs.hasRole('admin') });
    assertEqual({ name: 'the session holds no elevated platform role',
        shouldbe: false,
        value: gs.hasRole('security_admin') || gs.hasRole('maint') });

    // Fixture integrity: the step 30 insert landed on the table this cell is about. This
    // reads the stock `table` output of a Record Insert step, per Contract 2.
    assertEqual({ name: 'the subject record was inserted into ' + TABLE,
        shouldbe: TABLE, value: String(steps(STEP_30_SUBJECT).table) });

    stepResult.setOutputMessage((EXPECT_READABLE ? 'READ' : 'DENIED') + ' ' + TABLE + '.' +
        FIELD + ' | element.canRead()=' + element.canRead() +
        ' | key present=' + present +
        ' | control ' + CONTROL + '=' + String(body[CONTROL] || '') +
        ' | platform admin held=false');
    return true;
})(outputs, steps, params, stepResult, assertEqual);
```

Three properties of that script are load-bearing and none is optional.

**The `hasOwnProperty` check is the whole omission assertion.** The secured read returns an **empty string** for a denied field, not an error. A test that checked the value were falsy, empty or `null` would therefore pass against a response carrying `"total_funding_usd": ""` — which is precisely the nulled behaviour the requirements forbid. The denial branch asserts both that the key is absent and that `typeof body[FIELD]` is `undefined`, so a key present holding any value at all fails.

**Oracle 3 runs on read cells too.** On a denied cell it separates "the field was denied" from "nothing was readable"; on a read cell it establishes that the fixture the assertion depends on is intact. Both the table-level and the field-level controls must grant for a premium field to be readable, so the two failure modes are opposite and both silent: with the table-level control missing, nothing is readable and the field-level rules never evaluate; with the field-level rules missing, everything is readable because the platform falls back to the table-level grant.

**The final pair of assertions closes the impersonation loop.** `gs.hasRole('admin')` must be `false` inside every cell. Record access controls allow the platform administrator role to override them, so a cell whose `Impersonate` step silently did not take effect would be reading as the operator — and on a denied cell that is a false pass with no other symptom.

### Per-cell fixture and control values

| Field | Parent fixture at step 20 | Subject record at step 30 | Control column at step 50 |
| --- | --- | --- | --- |
| `x_bst_startuptrk_startup.total_funding_usd` | none | `name`, `headquarters_location`, `active` `true`, `total_funding_usd` = `12000000` | `name` |
| `x_bst_startuptrk_startup.institutional_funding_last_5yrs` | none | `name`, `headquarters_location`, `active` `true`, `institutional_funding_last_5yrs` = `true` | `headquarters_location` |
| `x_bst_startuptrk_founder.contact_email` | one `x_bst_startuptrk_startup` | `name`, `startup`, `contact_email` = `atf.founder@example.invalid` | `name` |
| `x_bst_startuptrk_executive.contact_email` | one `x_bst_startuptrk_startup` | `name`, `startup`, `contact_email` = `atf.exec@example.invalid` | `name` |
| `x_bst_startuptrk_investor.aum_usd` | none | `name`, `aum_usd` = `450000000` | `name` |
| `x_bst_startuptrk_fundinground.amount_usd` | one `x_bst_startuptrk_startup` | `startup`, `round_date` = `2025-06-30`, `amount_usd` = `12000000` | `round_date` |
| `x_bst_startuptrk_fundinground.valuation_usd` | one `x_bst_startuptrk_startup` | `startup`, `round_date` = `2025-06-30`, `valuation_usd` = `90000000` | `round_date` |

`institutional_funding_last_5yrs` is a true/false column, so its `*.3` cell needs care: a denied true/false field also reads back as an empty string, which is indistinguishable from `false` by value. The `hasOwnProperty` assertion is the only reliable check for this field, and it is the reason the same script shape is used for all seven denied cells rather than a value comparison tailored per type.

`institutional_funding_last_5yrs` is also, deliberately, **not** part of the startup inclusion filter. The filter tests `active` and `headquarters_location` only. Were it otherwise, a caller holding `x_bst_startuptrk.user` could not read the column the filter depends on and the portal list would be unbuildable for that role. Do not add it to the filter.

## Suite 9 — `BST REST suite — resources`

One suite, **6 tests**, one per logical resource. The physical base path is **`/api/x_bst_startuptrk/v1/`** — a scoped Scripted REST API always carries its namespace segment, so the logical `/api/v1/` of the requirements resolves to that path on the instance. Every `end_point` below uses it.

| Test | Logical resource | `end_point` under test | Rate-limit `api_resource` token |
| --- | --- | --- | --- |
| `BST REST — startups` | `/startups` | `/api/x_bst_startuptrk/v1/startups` | `/startups` |
| `BST REST — founders` | `/founders` | `/api/x_bst_startuptrk/v1/founders` **and** the nested `/api/x_bst_startuptrk/v1/founders/{startup_id}/executives` | `/founders` **and** `/founders/{startup_id}/executives` |
| `BST REST — investors` | `/investors` | `/api/x_bst_startuptrk/v1/investors` | `/investors` |
| `BST REST — funding-rounds` | `/funding-rounds` | `/api/x_bst_startuptrk/v1/funding-rounds` | `/funding-rounds` |
| `BST REST — jobs` | `/jobs` | `/api/x_bst_startuptrk/v1/jobs` | `/jobs` |
| `BST REST — news` | `/news` | `/api/x_bst_startuptrk/v1/news` | `/news` |

**There are seven rate-limit `api_resource` tokens, not six.** The nested executives sub-resource accounts **separately** from `/founders`. A 429 assertion against the nested path must seed the token `/founders/{startup_id}/executives` verbatim; seeding `/founders` does not trip it, and seeding the nested token does not trip `/founders`. The `BST REST — founders` test therefore carries two independent 429 blocks.

### The REST caller and its Basic Auth Configuration

`Send REST Request - Inbound` performs a genuine inbound HTTP call and establishes its **own** session. An `Impersonate` step earlier in the test does **not** carry into it, so the request must present credentials of its own through the step's **Basic authentication** input. That is the only reason this suite needs a password-holding identity at all; the other nine suites need none.

**A password-holding account is an authentication surface, and this one exists only for the duration of a test run.** Five properties bind it whichever construction you use, and none of them is optional:

| # | Property | What it prevents |
| --- | --- | --- |
| 1 | **Least privilege: exactly one role, `x_bst_startuptrk.user`.** No platform `admin`, no `security_admin`, no `itil`, no `rest_service`, nothing beyond what the platform assigns to every user by default. | An account whose credential is worth more than the assertion it serves. |
| 2 | **Web-service access only: `web_service_access_only` = `true`.** The account authenticates inbound API requests and **cannot sign in to the user interface**, cannot be impersonated and gets no session in the browser. | A standing interactive login. This is the single most important of the five, and the earlier revision of this guide had it backwards. |
| 3 | **A generated secret, never written down here.** The password is generated at creation time — at least 24 characters from a random source — and exists in exactly two places: the `sys_user` record's own encrypted password field and the `sys_auth_profile_basic` record's encrypted password field. **No password value appears in this guide, in any other document of this package, in an evidence table, in a screenshot or in a terminal transcript.** Do not choose a memorable value, do not reuse one from another instance, and do not record it "temporarily". | A credential published alongside the account that uses it. |
| 4 | **A named owner and an expiry.** Record both in the table under [Teardown](#teardown--the-rest-caller-must-not-outlive-the-run) before the first run: who owns the account, and the date it must be gone by. The expiry is **the day the ATF run completes**, not a quarter away. | An account nobody is responsible for outliving the work it was made for. |
| 5 | **A verified teardown.** The account is removed and its absence is **proved by query**, not asserted. See [Teardown](#teardown--the-rest-caller-must-not-outlive-the-run). | The default outcome, which is that it is still there next year. |

#### Construction A — an ephemeral identity, created and rolled back inside the test (**preferred**)

Use this where the step supports it, because it makes properties 4 and 5 automatic: the framework's own rollback removes the account, so there is no standing surface between runs and nothing to remember to delete.

**Design-time check, before you build anything.** Open a `Send REST Request - Inbound` step and try to bind its **Basic authentication** input to a **previous step's output** rather than picking a `sys_auth_profile_basic` record from the reference list. If the input accepts the binding, Construction A is available. If it accepts only a record chosen at design time, it is not, and you use Construction B. **Record which it was**, because it determines which teardown applies.

Where it is available, add this as step 1 of each of the six REST tests, ahead of the fixture steps.

| Step | Step configuration | Category | Purpose |
| --- | --- | --- | --- |
| 1 | **Run Server Side Script** | Server - Independent | Creates the ephemeral user, grants it exactly `x_bst_startuptrk.user`, creates its Basic Auth Configuration, and outputs the configuration's `sys_id` for the REST step to consume. |

```javascript
(function(outputs, steps, params, stepResult, assertEqual) {

    // A run-unique name, so two concurrent runs cannot collide and a residual
    // account is traceable to the run that created it.
    var token = new GlideDateTime().getNumericValue().toString(36)
        + Math.floor(Math.random() * 1679616).toString(36);
    var userName = 'bst.rest.caller.' + token;

    // A generated secret. It is never returned, logged or asserted on: it is written
    // into the two encrypted fields that need it and then goes out of scope.
    var secret = '';
    var alphabet = 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789';
    var i = 0;
    for (i = 0; i !== 32; i++) {
        secret = secret + alphabet.charAt(Math.floor(Math.random() * alphabet.length));
    }

    var caller = new GlideRecord('sys_user');
    caller.initialize();
    caller.setValue('user_name', userName);
    caller.setValue('first_name', 'BST REST');
    caller.setValue('last_name', 'caller ' + token);
    caller.setValue('user_password', secret);
    caller.setValue('web_service_access_only', true);   // NO interactive login
    caller.setValue('locked_out', false);
    caller.setValue('active', true);
    var callerId = caller.insert();
    if (!callerId) {
        stepResult.setFailed('could not create the ephemeral REST caller');
        return false;
    }

    // Exactly one role, and nothing else.
    var role = new GlideRecord('sys_user_role');
    if (!role.get('name', 'x_bst_startuptrk.user')) {
        stepResult.setFailed('role x_bst_startuptrk.user not found');
        return false;
    }
    var grant = new GlideRecord('sys_user_has_role');
    grant.initialize();
    grant.setValue('user', callerId);
    grant.setValue('role', role.getUniqueValue());
    if (!grant.insert()) {
        stepResult.setFailed('could not grant x_bst_startuptrk.user to the caller');
        return false;
    }

    var profile = new GlideRecord('sys_auth_profile_basic');
    profile.initialize();
    profile.setValue('name', 'BST REST caller ' + token);
    profile.setValue('username', userName);
    profile.setValue('password', secret);
    var profileId = profile.insert();
    if (!profileId) {
        stepResult.setFailed('could not create the Basic Auth Configuration');
        return false;
    }

    outputs.caller_user_name = userName;      // consumed by the 429 seeding script
    outputs.caller_sys_id = callerId;         // consumed by the 429 seeding script
    outputs.basic_auth_profile = profileId;   // consumed by the REST step
    stepResult.setSuccess();
    return true;

})(outputs, steps, params, stepResult, assertEqual);
```

Bind the REST step's **Basic authentication** input to this step's `basic_auth_profile` output, and the seeding script's caller to its `caller_sys_id` output. **The secret is never an output**, so it never reaches a step result, an execution record or an evidence table.

#### Construction B — a persistent identity, hardened (fallback only)

Use this only when the design-time check above showed the step cannot take a run-time binding. Build these two records **once, by hand, as a precondition**; they are instance provisioning, like the ATF runner property, and they are correctly absent from the delivered Update Set.

| Record | Table | Values |
| --- | --- | --- |
| REST caller user | `sys_user` | `user_name` = `bst.rest.caller`, `first_name` = `BST REST`, `last_name` = `caller`, **`web_service_access_only` = `true`**, `active` = `true`, `locked_out` = `false`, a **generated** password per property 3, and exactly one role: **`x_bst_startuptrk.user`**. |
| Basic Auth Configuration | `sys_auth_profile_basic` | `name` = `BST REST caller`, `username` = `bst.rest.caller`, `password` = the generated secret. This is the record the step's **Basic authentication** field references. |

Two further obligations attach to this construction and not to Construction A: keep the account `active` **only while a run is in progress** — set `active` to `false` between runs, which leaves the records intact for the next run while removing the authentication surface — and complete the teardown below when the ATF work is finished.


The REST caller holds the **base** role deliberately. All thirteen read operations are granted to all three roles by the `Boston Startup Tracker API read` endpoint ACL and by the Layer 1 table-read ACLs, so every `GET` in this suite succeeds — and because the caller is the base role, the success-shape assertion in each test can additionally confirm end-to-end over HTTP that the premium keys are **absent** from the response body. The six tests assert response shape, pagination and the 429 contract, none of which is role-differentiated, so no administrator credential is needed anywhere in this suite. Mutations are not exercised here.

The user name is `bst.rest.caller` and its first name is `BST REST`, **not** `BST ATF`. That is deliberate: warning **W8** asserts that no user whose first name is `BST ATF` survives a run, and giving the REST caller a different name means that assertion needs no exception and stays a clean signal.

#### Why the base role, on both constructions

The REST caller holds the **base** role deliberately. All thirteen read operations are granted to all three roles by the `Boston Startup Tracker API read` endpoint ACL and by the Layer 1 table-read ACLs, so every `GET` in this suite succeeds — and because the caller is the base role, the success-shape assertion in each test can additionally confirm end-to-end over HTTP that the premium keys are **absent** from the response body. The six tests assert response shape, pagination and the 429 contract, none of which is role-differentiated, so **no administrator credential is needed anywhere in this suite**. Mutations are not exercised here.

This password-holding caller is distinct from the three run-time impersonation users of [Technique (a)](#technique-a--impersonation), which need no password because `Impersonate` needs none. The split, and the choice between the two constructions, are recorded in [`../../../docs/decisions/DECISION_LOG.md`](../../../docs/decisions/DECISION_LOG.md).

### Teardown — the REST caller must not outlive the run

**This is a required step of this guide, not a tidy-up suggestion.** Record the owner and the expiry before the first run, and record the teardown evidence after the last one.

| Field | Value |
| --- | --- |
| Construction in use (A or B) | |
| Design-time check outcome — does `Send REST Request - Inbound` accept a run-time binding? | |
| Account owner (named person) | |
| Expiry date — the day the ATF run completes | |
| Teardown performed on (date, UTC) | |
| Teardown verified by (named person) | |

**On Construction A** the framework removes the account, and the teardown is the verification:

1. After the last run, query `sys_user` for `user_name` **starts with** `bst.rest.caller.` and confirm the result is **empty**.
2. Query `sys_auth_profile_basic` for `name` **starts with** `BST REST caller ` and confirm the result is **empty**.
3. A residual record from either query means a test errored in a way that left its transaction open. Delete the residual records by hand, and treat every result in that run as untrusted until the cause is found — the same rule warning **W8** applies to the impersonation users.

**On Construction B** the teardown is performed by hand, in this order, and each step is confirmed:

1. Delete the `sys_auth_profile_basic` record named `BST REST caller`. Confirm a query for that name returns **empty**.
2. Delete the `sys_user_has_role` row granting `x_bst_startuptrk.user` to `bst.rest.caller`. Confirm the user's **Roles** related list is empty.
3. Delete the `sys_user` record `bst.rest.caller`. Confirm a query on `user_name` = `bst.rest.caller` returns **empty**.
4. Confirm no other `sys_auth_profile_basic` record references the user name `bst.rest.caller`.

**Deleting, not deactivating, is the completion condition.** A deactivated account with a live credential is still a credential on the instance; the guide's own between-runs measure is deactivation precisely because it is the weaker, temporary form. Only the four-step deletion above closes the surface.

**`sys_user` is outside the `x_bst_startuptrk` scope.** Creating and deleting this account is **instance provisioning performed by the operator**, exactly like enabling the ATF runner property, and it is not an act of the scoped application — which is why no `sys_user` record appears in the Update Set. Prompt section 6.0 binds the application, and this guide keeps that boundary: nothing here asks the application to write a user.

#### Lifecycle of a Construction B account

Two further actions attach to Construction B and are recorded, not assumed:

**Rotate the password after acceptance.** Once criterion 3's evidence is recorded, regenerate the password in both records. The suite is re-runnable afterwards without any edit, because every step references the configuration by name.

**Then delete it.** The account exists to produce criterion 3's evidence. When the suite will not be re-run, complete the four-step deletion above; deactivation is the between-runs measure and is not the completion condition.

| # | Lifecycle stage | Action | Recorded where |
| --: | --- | --- | --- |
| 1 | Before the first run | Create both records; generate the password; confirm `web_service_access_only` is `true`, one role, no groups; record the owner and the expiry | [Teardown](#teardown--the-rest-caller-must-not-outlive-the-run) and [Build verification](#build-verification) |
| 2 | Between runs | Set `active` `false`, which leaves the records intact while removing the authentication surface | The evidence record |
| 3 | During a run | Every REST step references `BST REST caller` by name; no script reads or prints the password | The step inputs |
| 4 | After acceptance | Rotate the password in both records | The evidence record |
| 5 | End of life | Delete the Basic Auth Configuration, the role grant and the user, and verify each by query | [Teardown](#teardown--the-rest-caller-must-not-outlive-the-run) |

### The shared REST step sequence

Each of the six tests follows this shape. Substitute the resource path, the fixture table, the `api_resource` token and the per-resource schema.

**Two properties of this sequence are what make its two weakest oracles strong**, and both were deliberate additions rather than conveniences:

- **The fixtures are uniquely filterable.** Every seeded record carries a per-run marker in the resource's filter column, and every list call passes that marker as a filter, so `total_count` is an **exact** expected number rather than a floor. Without it, a `total_count` that counted the whole table — or counted an unfiltered set while the page was filtered — would pass a greater-than-or-equal assertion.
- **The counter is owned and cleaned.** The test deletes every counter row for its tuple before it starts, asserts a known baseline, asserts the increment on ordinary calls, and only then seeds the threshold. Without that, a counter row left behind by a previous run makes both the 200 assertions and the 429 assertion depend on state the test did not create.

| Step | Step configuration | Category | Inputs |
| --- | --- | --- | --- |
| 5 | **Create a User** | Server - Independent | `roles` = **exactly** `x_bst_startuptrk.admin`, so the fixtures can be written. This user writes the fixtures; it is **not** the caller the REST steps authenticate as. |
| 8 | **Run Server Side Script** | Server - Independent | Role-set verification for the step 5 user, per [Step 2](#step-2--verify-the-role-set-before-trusting-the-test). `EXPECTED` = `x_bst_startuptrk.admin`. |
| 10 | **Impersonate** | Server - Independent | `user` = the step 5 output. |
| 20 | **Run Server Side Script** | Server - Independent | **Seed the uniquely filterable fixture set** and write the run marker to a record the test creates, so later steps read the same marker. Script under [The fixture and marker step](#the-fixture-and-marker-step). |
| 25 | **Run Server Side Script** | Server - Independent | **Own the counter tuple.** Delete **every** `x_bst_startuptrk_rate_limit_counter` row for this test's caller, resource token and current window, assert **zero** remain, and record that baseline. Script under [Technique (b)](#technique-c--the-deterministic-429). |
| 30 | **Send REST Request - Inbound** | Server - REST | `http_method` = **GET**; `end_point` = the resource path; `basic_auth` = `BST ATF REST caller`; `query_params` = `sysparm_limit` `2`, `sysparm_offset` `0`, **plus the marker filter** for this resource. |
| 40 | **Assert Status Code** | Server - REST | `response_operation` = **is**; `status_code` = `200`. |
| 50 | **Assert Response JSON Payload Is Valid** | Server - REST | No inputs. Fails the test if the body is not parseable JSON. |
| 60 | **Run Server Side Script** | Server - Independent | **The per-resource schema assertion** — every declared key present with its declared type, no undeclared key, and every premium key absent. Script under [The per-resource schema assertion](#the-per-resource-schema-assertion). |
| 70 | **Run Server Side Script** | Server - Independent | **The exact-count and exact-membership assertions** for page one. Script under [The exact pagination assertions](#the-exact-pagination-assertions). |
| 75 | **Run Server Side Script** | Server - Independent | **The increment assertion, first call.** Exactly one inbound call has been made since the zero baseline of step 25, so assert the tuple holds **exactly one** row reading **exactly 1**. `EXPECTED_CALLS` = `1`. Script under [Technique (b)](#technique-c--the-deterministic-429). |
| 80 | **Send REST Request - Inbound** | Server - REST | Page two. Identical to step 30 with `sysparm_offset` `2`. |
| 90 | **Assert Status Code** | Server - REST | `response_operation` = **is**; `status_code` = `200`. |
| 100 | **Run Server Side Script** | Server - Independent | **The page-two assertions**: `total_count` identical to page one, `offset` echoes `2`, the page holds the **exact** remainder, its rows are the exact expected identifiers in the exact expected order, and the two pages together are the whole filtered set exactly once each. Same script as step 70, run in its page-two branch. |
| 105 | **Run Server Side Script** | Server - Independent | **The increment assertion, second call.** Two inbound calls have now been made since the baseline, so assert the tuple still holds **exactly one** row and that it now reads **exactly 2** — the transition 0 to 1 to 2 that proves the limiter increments its own row rather than inserting a second. `EXPECTED_CALLS` = `2`. Same script as step 75. |
| 110 | **Send REST Request - Inbound** | Server - REST | Bounds check. `query_params` = `sysparm_limit` `9999` plus the marker filter. |
| 120 | **Run Server Side Script** | Server - Independent | Asserts the echoed `limit` is clamped to the value of `x_bst_startuptrk.rest.max_limit`, which is `50`, and not `9999`, and that the page holds every seeded record because the whole filtered set now fits on one page. |
| 121 | **Send REST Request - Inbound** | Server - REST | **Boundary 1 — a page past the end.** Identical to step 30 with `sysparm_offset` = `4`, one past the last of the four selected rows. |
| 122 | **Run Server Side Script** | Server - Independent | Asserts `result` is an **empty** array, `total_count` is **still exactly `4`**, and `offset` echoes `4`. A count derived from the page would fall to `0` here, so this is the assertion that distinguishes a real count from a page-derived one. |
| 123 | **Send REST Request - Inbound** | Server - REST | **Boundary 2 — a filter matching nothing.** Identical to step 30 but with the marker filter set to the step 20 marker suffixed `ZZZ`, a value no seeded record carries. |
| 124 | **Run Server Side Script** | Server - Independent | Asserts status `200`, `total_count` **exactly `0`** and `result` an empty array — an empty set is a `200`, never a `404`. |
| 125 | **Send REST Request - Inbound** | Server - REST | **Boundary 3 — the offset ceiling.** `sysparm_offset` `10001`, one above the ceiling `RestQueryHelper` enforces. |
| 126 | **Assert Status Code** | Server - REST | `response_operation` = **is**; `status_code` = `400`. |
| 127 | **Run Server Side Script** | Server - Independent | Asserts the refusal body carries `error` naming the offset ceiling and **no** `result` and **no** `total_count` member, so a refused request can never be mistaken for a legitimate empty page. |
| 130 | **Run Server Side Script** | Server - Independent | **Seed the threshold deterministically**: delete every row for the tuple again, insert **exactly one** at-budget row, and assert exactly one exists. Script under [Technique (b)](#technique-c--the-deterministic-429). |
| 140 | **Send REST Request - Inbound** | Server - REST | Identical to step 30. This single call trips the limit. |
| 150 | **Assert Status Code** | Server - REST | `response_operation` = **is**; `status_code` = `429`. |
| 160 | **Assert JSON Response Payload Element** | Server - REST | `element_name` = `error`; `response_operation` = **is**; `element_value` = `rate_limit_exceeded`. |
| 170 | **Run Server Side Script** | Server - Independent | Asserts `retry_after` is present and a **positive integer**, that the body carries exactly the two members `error` and `retry_after`, and then **deletes the counter rows this test created**, leaving the tuple as it found it. Script under [Technique (b)](#technique-c--the-deterministic-429). |

The `BST REST — founders` test runs the whole sequence **twice**, once per token — `/founders` and the nested `/founders/{startup_id}/executives` — because the two account separately in the counter. The second pass substitutes the step 20 startup's `sys_id` for `{startup_id}` in the `end_point`, uses the path parameter itself as the filter, and sets `API_RESOURCE` to `/founders/{startup_id}/executives` in **all four** of its counter steps. Each pass takes its own ownership baseline, asserts its own increments, seeds its own threshold and cleans up after itself, so neither pass can affect the other's counts. That test therefore runs roughly twice the step count of the other five.

#### The isolating filter per resource

**`total_count` is the cardinality of the whole filtered set, not of the page, so asserting an exact value requires a filter that no record outside the fixture can satisfy.** Every list operation accepts filter parameters, and the operation applies the same conditions to the count and to the result set. Seed a unique token into the filtered column and the expected total is exactly the number of rows seeded.

| Test | Isolating filter passed in `query_params` | Seeded so the filtered total is exactly 3 |
| --- | --- | --- |
| `BST REST — startups` | `name` = `ATF-REST-<run token>` | Three startups whose `name` begins with the token and which **satisfy** the inclusion criteria, plus a fourth carrying the token that **fails** them |
| `BST REST — founders` | `startup` = the step 20 startup's `sys_id` | Three founders on that startup and no others |
| `BST REST — founders`, nested path | the startup `sys_id` in the path itself | Three executives on that startup and no others |
| `BST REST — investors` | `name` = `ATF-REST-<run token>` | Three investors whose `name` begins with the token |
| `BST REST — funding-rounds` | `startup` = the step 20 startup's `sys_id` | Three funding rounds on that startup, with **distinct** `round_date` values |
| `BST REST — jobs` | `startup` = the step 20 startup's `sys_id` | Three job postings on that startup, with **distinct** `posted_date` values |
| `BST REST — news` | `startup` = the step 20 startup's `sys_id` | Three news articles on that startup, with **distinct** `published_date` values |

Use a `<run token>` that is unique per execution — the numeric value of a `GlideDateTime` is sufficient — so a residue left by an earlier failed run cannot be selected by a later one. **Do not assert an exact `total_count` against an unfiltered request.** These tables are written to by the ingestion flows and by the portal walkthrough, and their unfiltered cardinality is not knowable from inside a test.

For `BST REST — startups` the exact total is what proves the inclusion filter reaches the count as well as the page: four records carry the filter token, three satisfy the inclusion criteria, and `total_count` must be **3**. A `total_count` of 4 with three rows returned means the filter was applied to the result set and not to the count, which is the defect this assertion exists to catch.


### The fixture and marker step

Every resource is seeded with **five** records: four that the marker filter selects and one **negative control** that it does not. Five and a page size of 2 give three pages, so the second page holds an exact remainder of 2 and a third page would hold exactly 1 — enough for an exact assertion at every offset.

The marker is a per-run token. It goes into the column the resource filters on, so the filter is one the API genuinely supports rather than one invented for the test:

| Resource | Marker column | Filter parameter on the request | Sort column, then `sys_id` |
| --- | --- | --- | --- |
| `/startups` | `name`, prefixed with the marker | `name=<marker>` | `name` ascending |
| `/founders` | `name`, prefixed with the marker | `name=<marker>` | `name` ascending |
| `/founders/{startup_id}/executives` | the parent `startup` reference | the path parameter itself | `name` ascending |
| `/investors` | `name`, prefixed with the marker | `name=<marker>` | `name` ascending |
| `/funding-rounds` | the parent `startup` reference | `startup=<sys_id>` | `round_date` **descending** |
| `/jobs` | the parent `startup` reference | `startup=<sys_id>` | `posted_date` **descending** |
| `/news` | the parent `startup` reference | `startup=<sys_id>` | `published_date` **descending** |

**Seed distinct values in the sort column of the resource under test.** Two rows tying on the sort column would order only by their `sys_id` tie-breaker, and the exact-membership assertion would fail for a reason that is not a defect.

```javascript
(function(outputs, steps, params, stepResult, assertEqual) {
    // ---- per-resource substitution ----
    var RESOURCE = '/startups';
    // ---- end of per-resource substitution ----

    // The marker is generated here and read by every later step out of the record this
    // step creates, per Contract 2 mechanism 3. It is never hard-coded.
    var marker = 'ATFR' + new GlideDateTime().getNumericValue();

    function startup(name, hq, active) {
        var gr = new GlideRecord('x_bst_startuptrk_startup');
        gr.initialize();
        gr.setValue('name', name);
        gr.setValue('headquarters_location', hq);
        gr.setValue('active', active);
        gr.setValue('industry', 'Fintech');
        return gr.insert();
    }

    var seeded = [];      // the four records the filter must select, in sort order
    var control = '';     // the one record the filter must NOT select
    var parentId = '';

    if (RESOURCE === '/startups') {
        // Four that satisfy the inclusion criteria, in name order, plus a negative control
        // that fails them: inactive AND outside the two location tokens.
        seeded.push(startup(marker + ' A Startup', 'Boston, MA', true));
        seeded.push(startup(marker + ' B Startup', 'Cambridge, MA', true));
        seeded.push(startup(marker + ' C Startup', 'Boston, MA', true));
        seeded.push(startup(marker + ' D Startup', 'Boston, MA', true));
        control = startup(marker + ' E Startup', 'Austin, TX', false);
    } else {
        // Every other resource hangs off one parent startup, which is also the filter.
        parentId = startup(marker + ' Parent', 'Boston, MA', true);
        var other = startup(marker + ' Other Parent', 'Boston, MA', true);
        var rows = {
            '/founders': { table: 'x_bst_startuptrk_founder', sort: 'name',
                values: [{ name: marker + ' A Founder' }, { name: marker + ' B Founder' },
                         { name: marker + ' C Founder' }, { name: marker + ' D Founder' }],
                controlValues: { name: marker + ' E Founder' } },
            '/founders/{startup_id}/executives': { table: 'x_bst_startuptrk_executive', sort: 'name',
                values: [{ name: marker + ' A Exec' }, { name: marker + ' B Exec' },
                         { name: marker + ' C Exec' }, { name: marker + ' D Exec' }],
                controlValues: { name: marker + ' E Exec' } },
            '/investors': { table: 'x_bst_startuptrk_investor', sort: 'name',
                values: [{ name: marker + ' A Capital', type: 'VC' },
                         { name: marker + ' B Capital', type: 'Angel' },
                         { name: marker + ' C Capital', type: 'PE' },
                         { name: marker + ' D Capital', type: 'Corporate' }],
                controlValues: { name: marker + ' E Capital', type: 'VC' } },
            '/funding-rounds': { table: 'x_bst_startuptrk_fundinground', sort: 'round_date',
                values: [{ round_date: '2025-04-30', round_type: 'Series C+' },
                         { round_date: '2025-03-31', round_type: 'Series B' },
                         { round_date: '2025-02-28', round_type: 'Series A' },
                         { round_date: '2025-01-31', round_type: 'Seed' }],
                controlValues: { round_date: '2024-12-31', round_type: 'Pre-Seed' } },
            '/jobs': { table: 'x_bst_startuptrk_jobposting', sort: 'posted_date',
                values: [{ title: marker + ' A Job', posted_date: '2026-01-04' },
                         { title: marker + ' B Job', posted_date: '2026-01-03' },
                         { title: marker + ' C Job', posted_date: '2026-01-02' },
                         { title: marker + ' D Job', posted_date: '2026-01-01' }],
                controlValues: { title: marker + ' E Job', posted_date: '2025-12-31' } },
            '/news': { table: 'x_bst_startuptrk_newsarticle', sort: 'published_date',
                values: [{ title: marker + ' A Story', published_date: '2026-02-04' },
                         { title: marker + ' B Story', published_date: '2026-02-03' },
                         { title: marker + ' C Story', published_date: '2026-02-02' },
                         { title: marker + ' D Story', published_date: '2026-02-01' }],
                controlValues: { title: marker + ' E Story', published_date: '2026-01-31' } }
        }[RESOURCE];

        var i = 0;
        var f = '';
        for (i = 0; i !== rows.values.length; i++) {
            var child = new GlideRecord(rows.table);
            child.initialize();
            child.setValue('startup', parentId);
            for (f in rows.values[i]) {
                if (rows.values[i].hasOwnProperty(f)) {
                    child.setValue(f, rows.values[i][f]);
                }
            }
            seeded.push(child.insert());
        }
        // The negative control hangs off the OTHER parent, so the filter cannot select it.
        var ctl = new GlideRecord(rows.table);
        ctl.initialize();
        ctl.setValue('startup', other);
        for (f in rows.controlValues) {
            if (rows.controlValues.hasOwnProperty(f)) {
                ctl.setValue(f, rows.controlValues[f]);
            }
        }
        control = ctl.insert();
    }

    assertEqual({ name: 'four filterable records seeded', shouldbe: 4, value: seeded.length });
    assertEqual({ name: 'one negative control seeded', shouldbe: true, value: control !== '' });

    // Contract 2 mechanism 3: park the marker, the expected identifiers in sort order, the
    // control identifier and the parent identifier on a record this test creates, so steps
    // 60, 70, 100 and 120 read exactly the values this step generated.
    var handoff = new GlideRecord('x_bst_startuptrk_ingest_staging');
    handoff.initialize();
    handoff.setValue('source_system', 'crunchbase');
    handoff.setValue('record_type', 'startup');
    handoff.setValue('import_state', 'rejected');
    handoff.setValue('run_provenance', 'fallback');
    handoff.setValue('import_run', marker);
    handoff.setValue('error_message', 'ATF REST fixture handoff, not an ingestion row');
    handoff.setValue('raw_payload', new global.JSON().encode({
        marker: marker,
        expected: seeded,
        control: control,
        parent: parentId
    }));
    outputs.record_id = handoff.insert();
    outputs.table = 'x_bst_startuptrk_ingest_staging';

    stepResult.setOutputMessage('Seeded 4 filterable + 1 control for ' + RESOURCE +
        ' under marker ' + marker + '; handoff row ' + outputs.record_id);
    return true;
})(outputs, steps, params, stepResult, assertEqual);
```

The handoff row is written to the staging table with `import_state` `rejected` and an `error_message` saying what it is, so it can never be picked up by an ingestion run — which only reads `pending` rows — and it is rolled back with the test in any case. It is the only mechanism that can carry a value **generated at run time** from one `Run Server Side Script` step to another, per Contract 2.

### The per-resource schema assertion

Step 60 asserts the **exact** representation of each resource, not merely that an envelope was returned. Every declared key must be present with its declared type, no undeclared key may appear, and every premium key must be absent because the caller holds only the base role.

The declared representations, transcribed from [`../api-reference.md`](../api-reference.md). `sys_id` is present on every row of every resource. **P** marks a premium key, which must be **absent** for this caller.

| Resource | Keys, in the order the operation serialises them |
| --- | --- |
| `/startups` | `sys_id`, `name`, `description`, `industry`, `founded_year`, `headquarters_location`, `website`, `logo_url`, `funding_stage`, `total_funding_usd` **P**, `active`, `institutional_funding_last_5yrs` **P**, `employee_count_range` |
| `/founders` | `sys_id`, `name`, `startup`, `title`, `bio`, `linkedin_url`, `contact_email` **P** |
| `/founders/{startup_id}/executives` | `sys_id`, `name`, `startup`, `title`, `bio`, `linkedin_url`, `contact_email` **P** |
| `/investors` | `sys_id`, `name`, `type`, `focus_areas`, `website`, `aum_usd` **P**, `portfolio_count` |
| `/funding-rounds` | `sys_id`, `startup`, `round_type`, `amount_usd` **P**, `round_date`, `lead_investor`, `valuation_usd` **P**, `source_url`, **plus `participating_investors`** |
| `/jobs` | `sys_id`, `startup`, `title`, `department`, `location`, `remote_type`, `seniority`, `posted_date`, `url`, `active` |
| `/news` | `sys_id`, `startup`, `title`, `source`, `url`, `published_date`, `summary` |

Type rules, which the same operation code produces uniformly across all seven paths:

| Declared type | Shape in the response | Assertion |
| --- | --- | --- |
| `string`, `glide_date` | a JSON string | `typeof value === 'string'` |
| `boolean` | a JSON boolean | `typeof value === 'boolean'` |
| `integer` | a JSON number, or `null` when unset | a number, or `null` |
| `currency` | a JSON string, or `null` when unset | a string, or `null` |
| `reference` | an **object** carrying `value` and `display_value`, or `null` when unset | both members present, or `null` |
| `glide_list` projection | absent from the serialised row; **`participating_investors` is added by the operation as an array of reference objects** | `Array.isArray(value)`, and every member carries `value` and `display_value` |

**A key whose value is unset is still present.** The serialiser omits a key only when the caller may not read it, so absence means denial and never emptiness — which is exactly what makes the premium assertions below meaningful.

```javascript
(function(outputs, steps, params, stepResult, assertEqual) {
    // ---- per-resource substitution ----
    var RESOURCE = '/startups';
    var STEP_30_PAGE_ONE = '';   // <- the Send REST Request step at display order 30
    // ---- end of per-resource substitution ----

    var SCHEMA = {
        '/startups': {
            keys: { sys_id: 'string', name: 'string', description: 'string', industry: 'string',
                founded_year: 'integer', headquarters_location: 'string', website: 'string',
                logo_url: 'string', funding_stage: 'string', active: 'boolean',
                employee_count_range: 'string' },
            premium: ['total_funding_usd', 'institutional_funding_last_5yrs'],
            extra: [] },
        '/founders': {
            keys: { sys_id: 'string', name: 'string', startup: 'reference', title: 'string',
                bio: 'string', linkedin_url: 'string' },
            premium: ['contact_email'], extra: [] },
        '/founders/{startup_id}/executives': {
            keys: { sys_id: 'string', name: 'string', startup: 'reference', title: 'string',
                bio: 'string', linkedin_url: 'string' },
            premium: ['contact_email'], extra: [] },
        '/investors': {
            keys: { sys_id: 'string', name: 'string', type: 'string', focus_areas: 'string',
                website: 'string', portfolio_count: 'integer' },
            premium: ['aum_usd'], extra: [] },
        '/funding-rounds': {
            keys: { sys_id: 'string', startup: 'reference', round_type: 'string',
                round_date: 'string', lead_investor: 'reference', source_url: 'string',
                participating_investors: 'array' },
            premium: ['amount_usd', 'valuation_usd'], extra: [] },
        '/jobs': {
            keys: { sys_id: 'string', startup: 'reference', title: 'string',
                department: 'string', location: 'string', remote_type: 'string',
                seniority: 'string', posted_date: 'string', url: 'string', active: 'boolean' },
            premium: [], extra: [] },
        '/news': {
            keys: { sys_id: 'string', startup: 'reference', title: 'string', source: 'string',
                url: 'string', published_date: 'string', summary: 'string' },
            premium: [], extra: [] }
    }[RESOURCE];

    function typeOk(declared, value) {
        if (declared === 'string') {
            return typeof value === 'string';
        }
        if (declared === 'boolean') {
            return typeof value === 'boolean';
        }
        if (declared === 'integer') {
            return value === null || typeof value === 'number';
        }
        if (declared === 'currency') {
            return value === null || typeof value === 'string';
        }
        if (declared === 'reference') {
            if (value === null) {
                return true;
            }
            if (typeof value !== 'object') {
                return false;
            }
            return Object.prototype.hasOwnProperty.call(value, 'value')
                && Object.prototype.hasOwnProperty.call(value, 'display_value');
        }
        if (declared === 'array') {
            if (!Array.isArray(value)) {
                return false;
            }
            var m = 0;
            for (m = 0; m !== value.length; m++) {
                if (typeof value[m] !== 'object') {
                    return false;
                }
                if (!Object.prototype.hasOwnProperty.call(value[m], 'value')) {
                    return false;
                }
                if (!Object.prototype.hasOwnProperty.call(value[m], 'display_value')) {
                    return false;
                }
            }
            return true;
        }
        return false;
    }

    var body = JSON.parse(steps(STEP_30_PAGE_ONE).response_body);

    // The envelope, exactly four members on a page that is not capped.
    var envelope = Object.keys(body).sort().join(',');
    assertEqual({ name: 'the envelope carries exactly result, total_count, limit and offset',
        shouldbe: 'limit,offset,result,total_count', value: envelope });
    assertEqual({ name: 'result is an array', shouldbe: true, value: Array.isArray(body.result) });
    assertEqual({ name: 'the page is not empty', shouldbe: true, value: body.result.length > 0 });

    var declared = Object.keys(SCHEMA.keys);
    var r = 0;
    var k = 0;
    for (r = 0; r !== body.result.length; r++) {
        var row = body.result[r];

        // Every declared key present, with its declared type.
        for (k = 0; k !== declared.length; k++) {
            var key = declared[k];
            assertEqual({ name: 'row ' + r + ' carries ' + key,
                shouldbe: true, value: Object.prototype.hasOwnProperty.call(row, key) });
            assertEqual({ name: 'row ' + r + ' ' + key + ' is a ' + SCHEMA.keys[key],
                shouldbe: true, value: typeOk(SCHEMA.keys[key], row[key]) });
        }

        // Every premium key ABSENT - omitted, not nulled - because the caller holds only
        // x_bst_startuptrk.user.
        for (k = 0; k !== SCHEMA.premium.length; k++) {
            assertEqual({ name: 'row ' + r + ' omits the premium key ' + SCHEMA.premium[k],
                shouldbe: false,
                value: Object.prototype.hasOwnProperty.call(row, SCHEMA.premium[k]) });
            assertEqual({ name: 'row ' + r + ' ' + SCHEMA.premium[k] + ' is not present empty',
                shouldbe: 'undefined', value: typeof row[SCHEMA.premium[k]] });
        }

        // No undeclared key. This is what catches a field added to an operation without
        // being added to the contract.
        var expected = declared.concat(SCHEMA.extra);
        var actual = Object.keys(row);
        var unexpected = actual.filter(function(key) { return expected.indexOf(key) === -1; });
        assertEqual({ name: 'row ' + r + ' carries no undeclared key',
            shouldbe: '', value: unexpected.join(',') });
    }

    stepResult.setOutputMessage(RESOURCE + ' schema asserted on ' + body.result.length +
        ' row(s): ' + declared.length + ' declared keys typed, ' + SCHEMA.premium.length +
        ' premium keys absent, 0 undeclared keys.');
    return true;
})(outputs, steps, params, stepResult, assertEqual);
```

### The exact pagination assertions

One script serves step 70 and step 100. `PAGE` selects the branch. The assertions are **exact** at every point: an exact `total_count`, the exact set of identifiers, in the exact order the operation's sort produces, with the negative control proved absent.

| Assertion | Page one, `sysparm_offset` `0` | Page two, `sysparm_offset` `2` |
| --- | --- | --- |
| `total_count` | exactly **4** | exactly **4**, identical to page one |
| Rows returned | exactly **2** | exactly **2** — the exact remainder of 4 at a limit of 2 |
| Membership | expected identifiers **0 and 1**, in that order | expected identifiers **2 and 3**, in that order |
| `limit` echo | `2` | `2` |
| `offset` echo | `0` | `2` |
| Negative control | absent | absent |
| Overlap with the other page | 0 rows | 0 rows |

```javascript
(function(outputs, steps, params, stepResult, assertEqual) {
    // ---- per-step substitution ----
    var PAGE = 1;                  // 1 at display order 70, 2 at display order 100
    var STEP_20_FIXTURE = '';      // <- the fixture step at display order 20
    var STEP_30_PAGE_ONE = '';     // <- the REST step at display order 30
    var STEP_80_PAGE_TWO = '';     // <- the REST step at display order 80
    // ---- end of per-step substitution ----

    var EXPECTED_TOTAL = 4;
    var PAGE_SIZE = 2;

    // Read the marker, the expected identifiers in sort order and the control identifier
    // out of the handoff record the fixture step created.
    var handoff = new GlideRecord('x_bst_startuptrk_ingest_staging');
    assertEqual({ name: 'the fixture handoff row is readable',
        shouldbe: true, value: handoff.get(steps(STEP_20_FIXTURE).record_id) });
    var fixture = new global.JSON().decode(String(handoff.getValue('raw_payload')));
    assertEqual({ name: 'the handoff names four expected identifiers',
        shouldbe: EXPECTED_TOTAL, value: fixture.expected.length });

    var one = JSON.parse(steps(STEP_30_PAGE_ONE).response_body);
    var ids = function(payload) {
        return payload.result.map(function(row) { return String(row.sys_id); });
    };

    if (PAGE === 1) {
        assertEqual({ name: 'total_count is EXACTLY the filtered set size',
            shouldbe: EXPECTED_TOTAL, value: parseInt(one.total_count, 10) });
        assertEqual({ name: 'limit echoes ' + PAGE_SIZE,
            shouldbe: PAGE_SIZE, value: parseInt(one.limit, 10) });
        assertEqual({ name: 'offset echoes 0', shouldbe: 0, value: parseInt(one.offset, 10) });
        assertEqual({ name: 'page one holds exactly ' + PAGE_SIZE + ' rows',
            shouldbe: PAGE_SIZE, value: one.result.length });
        assertEqual({ name: 'page one is the first two expected identifiers, in order',
            shouldbe: fixture.expected.slice(0, PAGE_SIZE).join(','), value: ids(one).join(',') });
        assertEqual({ name: 'the negative control is absent from page one',
            shouldbe: -1, value: ids(one).indexOf(String(fixture.control)) });

        stepResult.setOutputMessage('page 1: total_count=' + one.total_count + ' (exactly ' +
            EXPECTED_TOTAL + '), rows=' + ids(one).join(',') + ', control absent.');
        return true;
    }

    var two = JSON.parse(steps(STEP_80_PAGE_TWO).response_body);
    assertEqual({ name: 'total_count is identical on page two',
        shouldbe: parseInt(one.total_count, 10), value: parseInt(two.total_count, 10) });
    assertEqual({ name: 'total_count is still EXACTLY the filtered set size',
        shouldbe: EXPECTED_TOTAL, value: parseInt(two.total_count, 10) });
    assertEqual({ name: 'offset echoes 2', shouldbe: PAGE_SIZE, value: parseInt(two.offset, 10) });
    assertEqual({ name: 'page two holds the exact remainder',
        shouldbe: EXPECTED_TOTAL - PAGE_SIZE, value: two.result.length });
    assertEqual({ name: 'page two is the last two expected identifiers, in order',
        shouldbe: fixture.expected.slice(PAGE_SIZE).join(','), value: ids(two).join(',') });
    assertEqual({ name: 'the negative control is absent from page two',
        shouldbe: -1, value: ids(two).indexOf(String(fixture.control)) });

    var overlap = ids(two).filter(function(id) { return ids(one).indexOf(id) !== -1; });
    assertEqual({ name: 'no row repeats across the two pages', shouldbe: 0, value: overlap.length });

    // The two pages together are the whole filtered set, exactly once each.
    var union = ids(one).concat(ids(two)).sort().join(',');
    assertEqual({ name: 'the two pages are the whole filtered set',
        shouldbe: fixture.expected.slice().sort().join(','), value: union });

    stepResult.setOutputMessage('page 2: total_count=' + two.total_count + ' (stable and ' +
        'exactly ' + EXPECTED_TOTAL + '), rows=' + ids(two).join(',') + ', remainder exact, ' +
        'overlap 0, union complete.');
    return true;
})(outputs, steps, params, stepResult, assertEqual);
```

**The exact-membership assertion depends on the sort being deterministic**, which it is: every list operation orders by its sort column and then by `sys_id` as a tie-breaker — `name` ascending for `/startups`, `/founders`, the nested executives path and `/investors`; `round_date` descending for `/funding-rounds`; `posted_date` descending for `/jobs`; `published_date` descending for `/news`. The fixture step seeds distinct values in that column and lists `expected` in the same order the operation will return them, so a mismatch is a defect in the ordering rather than an artifact of the test.

**The `/startups` test carries one further assertion at step 70**, because that resource applies the inclusion criteria: the seeded negative control is **inactive and located outside both location tokens**, so it must be absent from `result` **and** uncounted in `total_count`. The exact-count assertion of `4` against five seeded records is what proves the criteria were applied to the count and to the page identically — a `total_count` of `5` with four rows on the page would mean the filter reached the result set and not the count, which is a defect in `StartupSearchService` rather than in the test.

Step 120 asserts the clamp with the same fixture:

```javascript
(function(outputs, steps, params, stepResult, assertEqual) {
    var STEP_20_FIXTURE = '';      // <- the fixture step at display order 20
    var STEP_110_OVER_LIMIT = '';  // <- the REST step at display order 110, sysparm_limit 9999

    var props = new AppProperties();
    var ceiling = props.getMaxLimit();          // x_bst_startuptrk.rest.max_limit, shipped 50

    var handoff = new GlideRecord('x_bst_startuptrk_ingest_staging');
    handoff.get(steps(STEP_20_FIXTURE).record_id);
    var fixture = new global.JSON().decode(String(handoff.getValue('raw_payload')));

    var body = JSON.parse(steps(STEP_110_OVER_LIMIT).response_body);

    assertEqual({ name: 'the requested 9999 was clamped to the configured ceiling',
        shouldbe: ceiling, value: parseInt(body.limit, 10) });
    assertEqual({ name: 'the echoed limit is not 9999',
        shouldbe: true, value: parseInt(body.limit, 10) !== 9999 });
    assertEqual({ name: 'total_count is unchanged by the larger page',
        shouldbe: 4, value: parseInt(body.total_count, 10) });
    assertEqual({ name: 'the whole filtered set now fits on one page',
        shouldbe: 4, value: body.result.length });

    var ids = body.result.map(function(row) { return String(row.sys_id); });
    assertEqual({ name: 'the single page is the whole filtered set, in sort order',
        shouldbe: fixture.expected.join(','), value: ids.join(',') });
    assertEqual({ name: 'the negative control is still absent',
        shouldbe: -1, value: ids.indexOf(String(fixture.control)) });

    stepResult.setOutputMessage('limit 9999 clamped to ' + ceiling + '; one page carried the ' +
        'whole filtered set of 4 in sort order; control absent.');
    return true;
})(outputs, steps, params, stepResult, assertEqual);
```

### The invalid-offset assertion

Add these two steps to **one** of the six tests — `BST REST — startups` by convention — because the parameter is parsed by the shared `RestQueryHelper` and one resource evidences it for all seven operations.

| Step | Step configuration | Category | Inputs |
| --- | --- | --- | --- |
| 200 | **Send REST Request - Inbound** | Server - REST | Identical to step 40 with `query_params` `sysparm_offset` `-1`. |
| 210 | **Run Server Side Script** | Server - Independent | Asserts the status is **400**, that the body carries exactly one member named `error`, and that the message names `sysparm_offset`. |

A non-numeric or negative `sysparm_offset` is refused with `400`, not silently treated as `0`. Repeat step 200 with `sysparm_offset` `abc` to cover the non-numeric branch. These steps run **before** step 190 retires the caller; renumber the retirement step to `220` in this one test.


## Suite 10 — `BST FLOW suite — ingestion`

One suite, **2 tests**, one per flow. Their canonical names carry a mode suffix and the two in force on this instance are:

| Test | Flow it covers | Entities it writes | Guide |
| --- | --- | --- | --- |
| `BST FLOW — Crunchbase Ingestion [fallback]` | `Crunchbase Ingestion` | `x_bst_startuptrk_startup`, `x_bst_startuptrk_investor`, `x_bst_startuptrk_fundinground`, `x_bst_startuptrk_m2m_round_investor` | [`02-flow-crunchbase-ingestion.md`](02-flow-crunchbase-ingestion.md) |
| `BST FLOW — LinkedIn Ingestion [fallback]` | `LinkedIn Ingestion` | `x_bst_startuptrk_founder`, `x_bst_startuptrk_executive`, `x_bst_startuptrk_jobposting` | [`03-flow-linkedin-ingestion.md`](03-flow-linkedin-ingestion.md) |

### What each test drives, and what it asserts

**Both tests start the published flow.** Neither calls the flow's orchestrating Script Include in place of the flow. There is no stock ATF step configuration that starts a flow, so each test starts it from a **Run Server Side Script** step through `sn_fd.FlowAPI` — the mechanic is under [Technique (d)](#technique-d--starting-the-flow-under-test) — and every assertion that follows is made against what that execution actually did.

Each test starts the flow **twice**: once with the cadence marker set so the guard must refuse, and once with it set so the guard must proceed. That is what makes the guard itself assertable rather than assumed.

| # | What the test asserts | Why the flow has to run for it to be assertable at all |
| --- | --- | --- |
| 1 | The cadence guard **refuses** when less than the cadence has elapsed: no staging row is claimed, no entity row is written, and the marker does not move. | The guard is step 1 of the flow and an `If` block. Nothing outside the flow evaluates it. |
| 2 | The cadence guard **proceeds** when more than the cadence has elapsed, mints a run identifier of the form `<source>-<yyyyMMddHHmmss>`, and resolves the source mode. | Same. The run identifier is minted by step 1 and consumed by five later steps. |
| 3 | The **branch taken** is the fallback branch, and the reason is recorded. | The branch is chosen by steps 2 to 4 of the flow from the alias state and the source-mode property. |
| 4 | The step `8b` **Log action published** the rendered evidence block, and that block carries the `run=` header and at least the `run_summary` event. | Publication is an action in the flow. A build missing it logs to `syslog` only and shows a clean execution with no detail, which is exactly the defect this assertion catches. |
| 5 | The evidence is **complete, not merely present**: the published header reports `summary_logged=true`, `events_dropped=0`, `skipped=0` and `reconciled=true`, and the `run_summary` event is on the line **directly beneath** the header. | `8a` renders the summary first precisely so truncation cannot remove it, and reports `events_omitted` when it removes anything. A test that asserted only "a block exists" would pass on a block whose summary had been cut. |
| 5a | Part **`8c` closed the run**: its `run_closed` line reports `published=true`, `healthy=true`, `faults=none` and `marker_stamped=true`, and the durable marker for this source has **moved forward** past the value step 60 wrote. | These are the only two independent proofs that the run was fit to count. `8c` cannot execute unless `8b` completed, and it stamps the marker only when all of its health members hold — so a marker that moved is proof of a healthy publication, and a `run_closed` line naming faults is proof of the opposite. |
| 6 | All **four cleaning rules**, asserted against the records the flow wrote and the events it published. | The rules run inside the mapper, but the batch, the run identifier and the provenance they run under come from the flow. |
| 7 | **Skip the record, continue the run**: one execution reports a non-zero `processed` count **and** a non-zero `rejected` count, with `skipped` **exactly zero**. | A halt-on-first-error build reports the rejection and nothing processed; only a whole-flow execution distinguishes the two. `skipped` is asserted at zero rather than merely reported, because a non-zero `skipped` is an operational fault and is a member of `8c`'s health predicate. |
| 8 | Every staging row the run claimed carries a **terminal state**. | The mapper stamps most of them and step 7 of the flow sweeps the rest. Both are flow-side. |

**A direct call to `IngestionMapper.ingestStaging()` is not a substitute for any row of that table.** It exercises the mapper and nothing else — no guard, no branch, no run identifier, no publication, no property write, no flow-level error handling — so a suite built on it reports success against a flow that was never wired together. Keep the direct call, if you want it, as a **diagnostic** to run after a flow test fails, to establish whether the fault is in the mapper or in the flow wiring. It is not a test in this suite and it produces no evidence for any success criterion.


### What these two tests cover, and what they cannot

**State this plainly, because it bounds what a passing result means.** There is **no Flow Designer step configuration in the Automated Test Framework**: no step triggers a flow, waits on a flow execution, or asserts on a flow's execution detail. A test in this framework therefore cannot *execute* a flow. Each of these two tests is consequently made of two halves, and both halves are required:

**Both paths are driven, and that is not optional.** A suite that only ever called `ingestStaging()` would leave the live seam — the typed envelope of [4.3](02-flow-crunchbase-ingestion.md#43--step-outputs) — completely unexercised, and that seam has a **silent total-failure mode**: a row carrying no `record_type` is rejected by `prepareOne()`, so a batch of untyped rows accepts nothing while reporting no transport failure at all. A fallback-only suite reports `success` against that defect, because a staging row always carries its record type. Step 45 exists to close it.

| Half | What it does | What it proves | What it cannot prove |
| --- | --- | --- | --- |
| **A — the orchestrator entry point**, steps 40 to 100 | Calls `IngestionMapper.ingestStaging(runId, sourceSystem, importRun, provenance)` — **the identical call the delivered orchestrator action A4 makes**, with the identical arguments the flow maps onto it | Every rule inside the ingestion: the four cleaning rules, reference resolution, the upsert, the join rows, the derived projections, the counters and the run summary. A defect in any of them fails these tests. | That the flow **reaches** that call. A broken trigger, an unpublished action, a missing `If`, a mis-mapped data pill or an unbound alias leaves half A passing. |
| **B — the wiring assertions**, step 110 | Reads the delivered flow and action records out of the platform's own tables and asserts the shape the flow guide specifies | That the flow, its trigger, its five published actions, its four action calls, its `If` block, its alias reference and its A4 input mappings are all as built | That an execution **succeeds end to end**. Only a real run does that. |

**What neither half covers, and where that coverage comes from instead:**

| Not covered here | Covered by |
| --- | --- |
| A flow execution that actually runs, and its execution detail | The one manual run in [`02-flow-crunchbase-ingestion.md`](02-flow-crunchbase-ingestion.md) and [`03-flow-linkedin-ingestion.md`](03-flow-linkedin-ingestion.md), section by section |
| The cadence guard admitting one execution per window and no-opping the rest | The second manual run of the same guides, which asserts `proceed` `false` |
| Three consecutive guard-passing scheduled runs with zero unhandled errors | Success criterion 4 in [`../validation-checklist.md`](../validation-checklist.md), read from **run-summary records**, never from these test results |
| A live outbound call and its authentication | Nothing in this delivery. Both aliases are in Branch A on this instance, so the live path is unexercised and both results are labelled `fallback validated` |

**Build both halves.** Half A calls the orchestrator's entry point rather than a copy of the ingestion logic, so the four cleaning rules under test are the ones the ingestion actually runs; half B asserts the wiring, which half A cannot fail for. `D-065` and `D-066` carry the decision, its alternatives and the coverage this construction does not reach.

### This suite does not impersonate

Suites 1 to 9 impersonate. **Suite 10 does not**, and the omission is deliberate rather than an oversight.

| Reason | Detail |
| --- | --- |
| The flow does not run as the caller | Both flows carry **Run As: System User**, so who started them has no bearing on what they may write. Impersonating a scoped role before starting the flow changes nothing about the execution under test. |
| The assertions read platform tables | Steps 70 and 80 read `sys_flow_context`, `sys_flow_log` and `syslog`. A user holding only `x_bst_startuptrk.admin` cannot read those, so an impersonation would make the publication assertion fail for a reason that is not a defect. |
| Nothing here is access control | Access control is suite 8's subject, cell by cell, and suite 9 confirms the same outcome over HTTP. This suite asserts flow behaviour, so an impersonation here would add no coverage while removing the publication evidence of step 70. |

The fixture writes are **Run Server Side Script** steps compiled in the `x_bst_startuptrk` scope, so they reach the staging table directly and need no role grant.

### The control state each test borrows, and what it can and cannot return

Driving the guard down both branches means writing the one scoped property the flow's guard reads. **Two of the three properties an earlier build wrote are no longer written by the test at all**, which removes two restore obligations rather than promising to honour them.

| Property | Written by the test? | Why |
| --- | --- | --- |
| `x_bst_startuptrk.ingestion.source_mode` | **No.** Set to `fallback` by the operator as **precondition 16**, before the suite runs, and left there. | A property this suite writes is a property this suite must restore, and a restore that runs only on the happy path is not a restore. The steady-state value for both flows is `fallback` anyway — guide 03's flow acquires nothing live in any posture — so making it a precondition removes the write, removes the restore, and removes the failure mode together. |
| `x_bst_startuptrk.ingestion.cadence_hours` | **No.** Read only, and used to compute the two marker stamps. | Never written, so never restored. |
| `x_bst_startuptrk.ingestion.last_run_provenance` | **Yes**, and unavoidably. Steps 40 and 60 position this source's entry so the guard must take the branch under test. | The guard reads this property and nothing else. There is no other way to make the guard assertable. |

**The marker cannot be "restored", and this guide no longer claims it can.** The passing branch *runs the flow*, and a healthy execution legitimately stamps a new `succeeded` entry through `markRunComplete()`. Whatever entry existed before the suite is therefore gone by design, not by accident — the suite's whole purpose is to make the flow write it. The honest obligations are different ones, and all three are enforced:

| # | Obligation | Where it is enforced |
| --- | --- | --- |
| 1 | **This suite must not run inside a criterion-4 evidence window.** Its executions are guard-passing runs and would otherwise be counted as evidence. | Precondition 15, and [W10](#operational-warnings). |
| 2 | **The suite must leave the property in a defined, recorded state** — no `running` claim left behind, and the resulting value written into the test output so the operator knows what it is. | Step 160, whose script is [The teardown step](#the-teardown-step). |
| 3 | **The operator must confirm that state after the suite**, by query, not by assumption. | [Post-suite residue queries](#post-suite-residue-queries), which the coverage gate reads. |

**The test touches only its own source's entry.** The property carries one entry per source system, and steps 40, 60 and 160 all preserve the other source's entry verbatim. Running the Crunchbase test therefore cannot move the LinkedIn flow's cadence, and vice versa.


### The shared test step sequence

| Step | Step configuration | Category | Inputs |
| --- | --- | --- | --- |
| 5 | **Create a User** | Server - Independent | `roles` = **exactly** `x_bst_startuptrk.admin`. The staging table grants read, write, create and delete to that role alone. |
| 8 | **Run Server Side Script** | Server - Independent | Role-set verification for the step 5 user, per [Step 2](#step-2--verify-the-role-set-before-trusting-the-test). `EXPECTED` = `x_bst_startuptrk.admin`. |
| 10 | **Impersonate** | Server - Independent | `user` = the step 5 output. |
| 20 | **Run Server Side Script** | Server - Independent | **Mint the run token and derive the provenance. Writes no run summary.** Generates a token unique to this execution, derives `live` or `fallback` from the **actual** state of the source-mode property and the alias, parks both on a record the test creates, and writes the result label into the step output message. Script under [Technique (c)](#technique-e--provenance-labelling). |
| 30 | **Run Server Side Script** | Server - Independent | **Seed this test's own staging rows** under the minted `import_run` token, exactly as tabulated per source below. Script under [The fixture step](#the-fixture-step). |
| 40 | **Run Server Side Script** | Server - Independent | **Call the orchestrator entry point** and assert the **exact returned object**. Script under [The ingest step and the exact returned object](#the-ingest-step-and-the-exact-returned-object). |
| 50 | **Run Server Side Script** | Server - Independent | **Rule 2 and reference resolution**, per source. Crunchbase asserts within-batch Startup deduplication; LinkedIn asserts parent resolution onto an existing Startup. Scripts under [Rule 2](#rule-2--deduplication-crunchbase-and-parent-resolution-linkedin). |
| 60 | **Run Server Side Script** | Server - Independent | **Rule 3 — choice normalisation**, both branches across five columns for Crunchbase and six for LinkedIn, with the unmatched count asserted from the **parked returned object** and the log line asserted under a level guard. Script under [Rule 3](#rule-3--choice-normalisation-and-the-investortype-asymmetry). |
| 70 | **Run Server Side Script** | Server - Independent | **Rule 4 — mandatory-field rejection**, one row per record type the flow writes. Script under [Rule 4](#rule-4--rejection-of-records-missing-mandatory-fields). |
| 80 | **Record Query** | Server - Independent | `table` = `x_bst_startuptrk_ingest_staging`; `field_values` = `import_run` `is` this test's token **and** `import_state` `is` `pending`; `assert_type` = **No records match the query**. Every seeded row reached a terminal state. |
| 90 | **Run Server Side Script** | Server - Independent | **Rule 1 — trimming**, plus **the ingestion effects**: for Crunchbase the join rows, the participant projection and `portfolio_count`; for LinkedIn the parent references. Scripts under [Rule 1 and the ingestion effects](#rule-1--trimming-and-the-ingestion-effects). |
| 100 | **Run Server Side Script** | Server - Independent | **The run summary the ingestion wrote** — every counter exact, reconciled against the staging records, with the emitted line and the absence of an all-zero summary asserted under a level guard. Never anything the setup step wrote. Script under [Technique (c)](#technique-e--provenance-labelling). |
| 110 | **Run Server Side Script** | Server - Independent | **Half B — the flow and action wiring assertions.** Script under [The wiring assertions](#the-wiring-assertions). |

### The fixture step

Each test seeds its own rows under the `import_run` token minted at step 20, so the run cannot pick up a row loaded by [`06-staging-table-csv-import.md`](06-staging-table-csv-import.md) and cannot be affected by whatever else is in the staging table. Guide 06's rows are `processed` and the ingestion query is bounded to `import_state` `pending`, so they would not be re-read in any case.

**The row counts, states and returned counters below are exact.** They are what step 40 asserts, so a fixture changed without changing them fails the test rather than silently weakening it.

#### Crunchbase — 11 rows

`crunchbase` ingests `startup`, `investor` and `funding_round`, in that order — `TYPE_ORDER` sorts the batch so parents exist before children.

| # | `record_type` | Columns set on the staging row | Purpose | Expected outcome |
| --: | --- | --- | --- | --- |
| 1 | `startup` | `name` = `  <T> Dedupe Target  `, `headquarters_location` = `  Boston, MA  `, `active` = `true`, `industry` = `fintech` | Rule 1 whitespace, rule 3 case-insensitive match | **processed**; stored trimmed, `industry` = `Fintech` |
| 2 | `startup` | `name` = `<t> dedupe target`, `headquarters_location` = `boston, ma`, `active` = `true` | Rule 2 duplicate, differing only by case | **rejected**, reason `duplicate startup in the same batch` |
| 3 | `startup` | `name` = `<T> Dedupe Target`, `headquarters_location` = `Cambridge, MA`, `active` = `true` | Rule 2 negative control — a different headquarters is a different key | **processed** |
| 4 | `startup` | `name` = `<T> Choice Coerce`, `headquarters_location` = `Boston, MA`, `active` = `true`, `industry` = `Quantum Widgets` | Rule 3, list **declares** `Other` | **processed**; `industry` = `Other`, one `choice_unmatched` event |
| 5 | `startup` | `name` = `<T> Missing HQ`, `active` = `true` — **no `headquarters_location`** | Rule 4 | **rejected**, reason naming `headquarters_location` |
| 6 | `investor` | `name` = `  <T> Lead Capital  `, `type` = `vc` | Rule 1, rule 3 case-insensitive | **processed**; `type` = `VC` |
| 7 | `investor` | `name` = `<T> Participant One`, `type` = `Sovereign Wealth` | Rule 3 on a list with **no** `Other`, and the asymmetry | **processed**; `type` **empty**, one `choice_unmatched` event, **the row still exists** |
| 8 | `investor` | `name` = `<T> Participant Two`, `type` = `Angel` | The second participant | **processed** |
| 9 | `investor` | `type` = `PE` — **no `name`** | Rule 4 | **rejected**, reason naming `name` |
| 10 | `funding_round` | `startup_name` = `<T> Choice Coerce`, `round_date` = `2025-06-30`, `round_type` = `series a`, `amount_usd` = `12000000`, `lead_investor_name` = `<T> Lead Capital`, `participating_investor_names` = `<T> Participant One,<T> Participant Two` | Reference resolution, rule 3, and the join rows | **processed**; `round_type` = `Series A`; **2** join rows |
| 11 | `funding_round` | `startup_name` = `<T> Choice Coerce`, `round_type` = `Series Q` — **no `round_date`** | Rule 4, and rule 3 with no `Other` | **rejected**, reason naming `round_date`, **and one `choice_unmatched` event before the rejection** |

`<T>` is the minted run token, so every value in the batch is unique to the execution.

**The funding rounds must point at row 4's name, not row 1's.** Rows 1 and 3 share the `name` `<T> Dedupe Target` and differ only in headquarters, which is what makes row 3 the deduplication negative control; two startups therefore carry that name after the run, so a child row naming that name resolves only when it also carries the matching `startup_headquarters_location` — the composite key is what disambiguates them, and a child row that leaves the location blank is rejected with `the row carries no parent headquarters location, and the startup key is the name together with the headquarters location`. Rows 10 and 11 resolve against `<T> Choice Coerce`, row 4's name, which is unique in the batch. **Pointing them at the ambiguous name rejects both rounds for the wrong reason and breaks the join-row and `portfolio_count` assertions at step 90.**

**The batch is processed in `TYPE_ORDER`, not in seeded order.** `expandRows()` sorts every row so `startup` precedes `investor`, which precedes `funding_round` — which is what lets row 10 resolve a lead investor that row 6 created in the same batch. `outcome.entries` is in that sorted order, so no assertion below depends on the order rows were seeded in.

**Expected returned object for Crunchbase**, every member exact:

| Member | Value | Made up of |
| --- | --: | --- |
| `accepted` (top level) | **7** | Rows 1, 3, 4, 6, 7, 8, 10 |
| `rejected` (top level) | **4** | Rows 2, 5, 9, 11 |
| `entries.length` | **11** | Every seeded row |
| `summary.processed` | **7** | The logger's processed counter |
| `summary.rejected` | **3** | Rows 5, 9, 11 — the duplicate is counted separately |
| `summary.duplicates` | **1** | Row 2 |
| `summary.skipped` | **0** | No upsert failed |
| `summary.unmatched` | **3** | Row 4's `industry`, row 7's `type`, **and row 11's `round_type`** — normalisation runs before the mandatory-field check, so a row rejected for a missing field can still have logged an unmatched choice |

#### LinkedIn — 8 rows

`linkedin` ingests `founder`, `executive` and `job_posting`. **None of them is a `startup`**, so the LinkedIn batch cannot exercise Startup deduplication at all — see [Rule 2](#rule-2--deduplication-crunchbase-and-parent-resolution-linkedin). Its parent must therefore already exist, and the test creates it at step 30 as an ordinary Startup record rather than as a staging row.

| # | `record_type` | Columns set on the staging row | Purpose | Expected outcome |
| --: | --- | --- | --- | --- |
| — | *(not a staging row)* | An `x_bst_startuptrk_startup` record `name` = `<T> LinkedIn Parent`, `headquarters_location` = `Boston, MA`, `active` = `true`, inserted directly | The pre-existing parent every child resolves onto | exists before step 40 |
| 1 | `founder` | `name` = `  <T> Founder Alpha  `, `startup_name` = `<T> LinkedIn Parent`, `title` = `ceo`, `contact_email` = `atf.founder@example.invalid` | Rule 1, rule 3 case-insensitive, parent resolution | **processed**; name trimmed, `title` = `CEO`, `startup` = the parent |
| 2 | `founder` | `name` = `<T> Founder Beta`, `startup_name` = `<T> LinkedIn Parent`, `title` = `Chief Vibes Officer` | Rule 3, list **declares** `Other` | **processed**; `title` = `Other`, one `choice_unmatched` event |
| 3 | `founder` | `name` = `<T> Founder Orphan`, `startup_name` = `<T> No Such Startup` | Reference resolution failure | **rejected**, reason `no startup carries the name` |
| 4 | `executive` | `name` = `<T> Exec Alpha`, `startup_name` = `<T> LinkedIn Parent`, `title` = `vp engineering`, `contact_email` = `atf.exec@example.invalid` | Rule 3 case-insensitive on a second table | **processed**; `title` = `VP Engineering` |
| 5 | `executive` | `startup_name` = `<T> LinkedIn Parent`, `title` = `CFO` — **no `name`** | Rule 4 | **rejected**, reason naming `name` |
| 6 | `job_posting` | `startup_name` = `<T> LinkedIn Parent`, `title` = `  <T> Staff Engineer  `, `department` = `platform engineering`, `remote_type` = `Anywhere`, `seniority` = `Principal`, `posted_date` = `2026-01-15` | Rule 1, and rule 3 across **three** columns with different `Other` membership | **processed**; `title` trimmed, `department` = `Other`, `remote_type` **empty**, `seniority` **empty**, **three** `choice_unmatched` events |
| 7 | `job_posting` | `startup_name` = `<T> LinkedIn Parent`, `department` = `Sales` — **no `title`** | Rule 4 | **rejected**, reason naming `title` |
| 8 | `job_posting` | `startup_name` = `<T> LinkedIn Parent`, `title` = `<T> Sales Lead`, `department` = `Sales`, `remote_type` = `Remote`, `seniority` = `Lead`, `posted_date` = `2026-01-16` | A clean row, so the run demonstrably continued after the rejections around it | **processed** |

**Expected returned object for LinkedIn**, every member exact:

| Member | Value | Made up of |
| --- | --: | --- |
| `accepted` (top level) | **5** | Rows 1, 2, 4, 6, 8 |
| `rejected` (top level) | **3** | Rows 3, 5, 7 |
| `entries.length` | **8** | Every seeded row |
| `summary.processed` | **5** | The logger's processed counter |
| `summary.rejected` | **3** | Rows 3, 5, 7 |
| `summary.duplicates` | **0** | `dedupeBatch()` inspects no LinkedIn record type |
| `summary.skipped` | **0** | No upsert failed |
| `summary.unmatched` | **4** | Row 2's `title`, and row 6's `department`, `remote_type` and `seniority` |

**One instance precondition applies to both tests.** `IngestionLogger` writes a line to the application log only when `x_bst_startuptrk.logging.level` permits the line's severity: `run_summary` is emitted at **info**, `choice_unmatched` at **warn**. Leave the property at its delivered `info` while suite 10 runs, so both classes reach `syslog`. Every counter assertion below reads the **returned object** rather than the log and so holds at any level; the log assertions are additionally guarded by `AppProperties.isLogLevelEnabled()` and skip themselves rather than fail when the level suppresses the line.

```javascript
(function(outputs, steps, params, stepResult, assertEqual) {
    // ---- per-test substitution ----
    var SOURCE = 'crunchbase';          // or 'linkedin'
    var STEP_20_TOKEN = '';             // <- the run-token step at display order 20
    // ---- end of per-test substitution ----

    var STAGING = 'x_bst_startuptrk_ingest_staging';

    // The token is read out of the record step 20 created; it is never re-derived here,
    // so every step of this test acts on exactly the same rows.
    var tokenRow = new GlideRecord(STAGING);
    assertEqual({ name: 'the run-token row is readable',
        shouldbe: true, value: tokenRow.get(steps(STEP_20_TOKEN).record_id) });
    var minted = new global.JSON().decode(String(tokenRow.getValue('raw_payload')));
    var T = String(minted.token);
    assertEqual({ name: 'the token is non-empty', shouldbe: true, value: T !== '' });

    function stage(recordType, values) {
        var gr = new GlideRecord(STAGING);
        gr.initialize();
        gr.setValue('source_system', SOURCE);
        gr.setValue('record_type', recordType);
        gr.setValue('import_state', 'pending');
        gr.setValue('run_provenance', String(minted.provenance));
        gr.setValue('import_run', T);
        var f = '';
        for (f in values) {
            if (values.hasOwnProperty(f)) {
                gr.setValue(f, values[f]);
            }
        }
        return gr.insert();
    }

    var seeded = 0;
    if (SOURCE === 'crunchbase') {
        stage('startup', { name: '  ' + T + ' Dedupe Target  ',
            headquarters_location: '  Boston, MA  ', active: 'true', industry: 'fintech' });
        stage('startup', { name: T.toLowerCase() + ' dedupe target',
            headquarters_location: 'boston, ma', active: 'true' });
        stage('startup', { name: T + ' Dedupe Target',
            headquarters_location: 'Cambridge, MA', active: 'true' });
        stage('startup', { name: T + ' Choice Coerce',
            headquarters_location: 'Boston, MA', active: 'true', industry: 'Quantum Widgets' });
        stage('startup', { name: T + ' Missing HQ', active: 'true' });
        stage('investor', { name: '  ' + T + ' Lead Capital  ', type: 'vc' });
        stage('investor', { name: T + ' Participant One', type: 'Sovereign Wealth' });
        stage('investor', { name: T + ' Participant Two', type: 'Angel' });
        stage('investor', { type: 'PE' });
        stage('funding_round', { startup_name: T + ' Choice Coerce', round_date: '2025-06-30',
            round_type: 'series a', amount_usd: '12000000',
            lead_investor_name: T + ' Lead Capital',
            participating_investor_names: T + ' Participant One,' + T + ' Participant Two' });
        stage('funding_round', { startup_name: T + ' Choice Coerce', round_type: 'Series Q' });
        seeded = 11;
    } else {
        // LinkedIn writes no Startup, so its parent is created directly rather than staged.
        var parent = new GlideRecord('x_bst_startuptrk_startup');
        parent.initialize();
        parent.setValue('name', T + ' LinkedIn Parent');
        parent.setValue('headquarters_location', 'Boston, MA');
        parent.setValue('active', true);
        var parentId = parent.insert();
        assertEqual({ name: 'the pre-existing parent startup was created',
            shouldbe: true, value: !!parentId });

        stage('founder', { name: '  ' + T + ' Founder Alpha  ',
            startup_name: T + ' LinkedIn Parent', title: 'ceo',
            contact_email: 'atf.founder@example.invalid' });
        stage('founder', { name: T + ' Founder Beta',
            startup_name: T + ' LinkedIn Parent', title: 'Chief Vibes Officer' });
        stage('founder', { name: T + ' Founder Orphan', startup_name: T + ' No Such Startup' });
        stage('executive', { name: T + ' Exec Alpha', startup_name: T + ' LinkedIn Parent',
            title: 'vp engineering', contact_email: 'atf.exec@example.invalid' });
        stage('executive', { startup_name: T + ' LinkedIn Parent', title: 'CFO' });
        stage('job_posting', { startup_name: T + ' LinkedIn Parent',
            title: '  ' + T + ' Staff Engineer  ', department: 'platform engineering',
            remote_type: 'Anywhere', seniority: 'Principal', posted_date: '2026-01-15' });
        stage('job_posting', { startup_name: T + ' LinkedIn Parent', department: 'Sales' });
        stage('job_posting', { startup_name: T + ' LinkedIn Parent', title: T + ' Sales Lead',
            department: 'Sales', remote_type: 'Remote', seniority: 'Lead',
            posted_date: '2026-01-16' });
        seeded = 8;
    }

    // Exactly the tabulated number of pending rows carries this token, and nothing else does.
    var counted = new GlideAggregate(STAGING);
    counted.addQuery('import_run', T);
    counted.addQuery('import_state', 'pending');
    counted.addAggregate('COUNT');
    counted.query();
    var pending = 0;
    if (counted.next()) {
        pending = parseInt(counted.getAggregate('COUNT'), 10) || 0;
    }
    assertEqual({ name: 'exactly ' + seeded + ' pending rows carry this run token',
        shouldbe: seeded, value: pending });

    stepResult.setOutputMessage('Seeded ' + seeded + ' pending ' + SOURCE +
        ' staging row(s) under import_run ' + T + '; guide 06 rows are untouched.');
    return true;
})(outputs, steps, params, stepResult, assertEqual);
```

The token row itself is written to the staging table by step 20 with `import_state` `rejected`, so it is never one of the rows the ingestion reads.

### The ingest step and the exact returned object

`IngestionMapper.ingestStaging()` returns the object `ingest()` builds, and **its shape is exact**. The counter names differ between the top level and the summary, and asserting the wrong one is the defect this section exists to prevent:

| Member | Where it lives | Meaning |
| --- | --- | --- |
| `run` | top level | The run identifier passed in |
| `source_system` | top level | The source, lower-cased |
| **`accepted`** | **top level** | Rows that produced an entity record |
| **`rejected`** | **top level** | Rows that did not, for any reason |
| `entries` | top level | One entry per expanded row, each carrying `record_type`, `accepted`, `state`, `reason`, `identifier` and, when written, `sys_id` |
| **`processed`** | **under `summary`** | The logger's processed counter — **there is no top-level `processed`** |
| `rejected`, `skipped`, `duplicates`, `unmatched` | under `summary` | The logger's other counters |
| `provenance` | under `summary` | `live` or `fallback`, as written |
| `recorded` | under `summary` | `true` when the summary was written and the property updated |

```javascript
(function(outputs, steps, params, stepResult, assertEqual) {
    // ---- per-test substitution: the Crunchbase values are shown; the LinkedIn values
    //      are in the LinkedIn expected-object table above ----
    var SOURCE = 'crunchbase';
    var EXPECT = {
        accepted: 7, rejected: 4, entries: 11,
        summary: { processed: 7, rejected: 3, duplicates: 1, skipped: 0, unmatched: 3 }
    };
    var STEP_20_TOKEN = '';             // <- the run-token step at display order 20
    // ---- end of per-test substitution ----

    var tokenRow = new GlideRecord('x_bst_startuptrk_ingest_staging');
    assertEqual({ name: 'the run-token row is readable', shouldbe: true,
        value: tokenRow.get(steps(STEP_20_TOKEN).record_id) });
    var minted = new global.JSON().decode(String(tokenRow.getValue('raw_payload')));
    var T = String(minted.token);
    var PROVENANCE = String(minted.provenance);

    // THE call the delivered orchestrator action A4 makes, with the arguments the flow maps.
    var outcome = new IngestionMapper().ingestStaging(T, SOURCE, T, PROVENANCE);

    // The exact returned object. accepted and rejected are TOP LEVEL; processed is under
    // summary and there is no top-level processed.
    assertEqual({ name: 'run echoes the token', shouldbe: T, value: String(outcome.run) });
    assertEqual({ name: 'source_system echoes the source',
        shouldbe: SOURCE, value: String(outcome.source_system) });
    assertEqual({ name: 'accepted is exactly ' + EXPECT.accepted,
        shouldbe: EXPECT.accepted, value: outcome.accepted });
    assertEqual({ name: 'rejected is exactly ' + EXPECT.rejected,
        shouldbe: EXPECT.rejected, value: outcome.rejected });
    assertEqual({ name: 'entries holds one per expanded row',
        shouldbe: EXPECT.entries, value: outcome.entries.length });
    assertEqual({ name: 'there is NO top-level processed member',
        shouldbe: false,
        value: Object.prototype.hasOwnProperty.call(outcome, 'processed') });
    assertEqual({ name: 'summary is present', shouldbe: true, value: !!outcome.summary });
    assertEqual({ name: 'summary.run echoes the token',
        shouldbe: T, value: String(outcome.summary.run) });
    assertEqual({ name: 'accepted plus rejected accounts for every expanded row',
        shouldbe: EXPECT.entries, value: outcome.accepted + outcome.rejected });

    // Every summary counter, exactly. summary.rejected excludes the duplicate, which
    // summary.duplicates carries instead - so the two differ from the top-level rejected.
    var member = '';
    for (member in EXPECT.summary) {
        if (EXPECT.summary.hasOwnProperty(member)) {
            assertEqual({ name: 'summary.' + member + ' is exactly ' + EXPECT.summary[member],
                shouldbe: EXPECT.summary[member], value: outcome.summary[member] });
        }
    }
    assertEqual({ name: 'summary.provenance is the derived mode',
        shouldbe: PROVENANCE, value: String(outcome.summary.provenance) });
    assertEqual({ name: 'summary.recorded is true, so the property was written',
        shouldbe: true, value: outcome.summary.recorded === true });

    // Skip the record, continue the run: a non-zero accepted AND a non-zero rejected from
    // ONE call. A run that halted on the first bad row would report rejections and no
    // accepted rows; a run that inserted partial rows would report no rejections.
    assertEqual({ name: 'accepted is non-zero, so the run continued past every rejection',
        shouldbe: true, value: outcome.accepted > 0 });
    assertEqual({ name: 'rejected is non-zero, so bad rows were refused rather than written',
        shouldbe: true, value: outcome.rejected > 0 });

    // The order-independent form of the same proof: EVERY record type that produced a
    // rejection also produced a processed row, so the run continued WITHIN each type and
    // not merely across the batch. expandRows sorts by TYPE_ORDER, so this cannot be
    // asserted by position.
    var byType = {};
    var e = 0;
    for (e = 0; e !== outcome.entries.length; e++) {
        var entry = outcome.entries[e];
        var key = String(entry.record_type);
        if (!byType[key]) {
            byType[key] = { processed: 0, refused: 0, pending: 0 };
        }
        if (entry.state === 'processed') {
            byType[key].processed = byType[key].processed + 1;
        } else if (entry.state === 'rejected' || entry.state === 'error') {
            byType[key].refused = byType[key].refused + 1;
        } else {
            byType[key].pending = byType[key].pending + 1;
        }
    }
    var typeName = '';
    var typesSeen = 0;
    for (typeName in byType) {
        if (!byType.hasOwnProperty(typeName)) {
            continue;
        }
        typesSeen++;
        assertEqual({ name: 'no ' + typeName + ' entry was left in a non-terminal state',
            shouldbe: 0, value: byType[typeName].pending });
        if (byType[typeName].refused > 0) {
            assertEqual({ name: 'the run continued past a rejected ' + typeName +
                ' and processed another one', shouldbe: true,
                value: byType[typeName].processed > 0 });
        }
    }
    assertEqual({ name: 'all three record types of this source are represented',
        shouldbe: 3, value: typesSeen });

    // Park the returned object on the token record so steps 60 and 100 assert against the
    // counters THIS call produced rather than re-deriving them. Contract 2, mechanism 3.
    minted.outcome = {
        accepted: outcome.accepted, rejected: outcome.rejected,
        entries: outcome.entries.length, summary: outcome.summary
    };
    tokenRow.setValue('raw_payload', new global.JSON().encode(minted));
    tokenRow.update();

    stepResult.setOutputMessage(SOURCE + ' ingest returned accepted=' + outcome.accepted +
        ' rejected=' + outcome.rejected + ' entries=' + outcome.entries.length +
        ' summary.processed=' + outcome.summary.processed +
        ' summary.rejected=' + outcome.summary.rejected +
        ' summary.duplicates=' + outcome.summary.duplicates +
        ' summary.unmatched=' + outcome.summary.unmatched +
        ' summary.skipped=' + outcome.summary.skipped +
        ' summary.provenance=' + outcome.summary.provenance +
        ' summary.recorded=' + outcome.summary.recorded);
    return true;
})(outputs, steps, params, stepResult, assertEqual);
```

**Steps 50 to 100 re-run the same call? No.** `ingestStaging()` is called exactly once per test, at step 40 — its query is bounded to `import_state` `pending`, so a second call would find nothing and would produce a second, empty run summary. Every later step reads one of three surfaces the single call left behind:

| Surface | Read by | Why |
| --- | --- | --- |
| The **entity and staging records** | Steps 50, 70, 80, 90, 100 | The durable effect of the run |
| The **returned object**, parked by step 40 on the token record and read back through the stock `record_id` output | Steps 60 and 100 | The counters, which no query can reconstruct exactly — `summary.rejected` excludes the duplicate that `summary.duplicates` carries |
| The **application log** | Steps 60 and 100, **guarded** by `AppProperties.isLogLevelEnabled()` | The emitted events, which the configured level may suppress |

The one deliberate exception is the update case inside the rule 3 step, which calls `ingestStaging()` a second time under a **different** token (`<T>-update`) to prove that an uncoercible value leaves a previously stored value in place. It touches no row of the main batch.

### Rule 2 — deduplication (Crunchbase) and parent resolution (LinkedIn)

The deduplication key is `IngestionMapper.startupKey()`, which lowercases and joins two columns: `lower(name)` + `|` + `lower(headquarters_location)`. It is applied at **batch scope** by `dedupeBatch()`, after preparation and before reference resolution. The first occurrence is accepted; every later occurrence is rejected with the reason `duplicate startup in the same batch` and logged through `IngestionLogger.duplicateRecord()`.

**`dedupeBatch()` skips every entry whose `record_type` is not `startup`.** That single fact decides which test asserts what:

| Source | Record types it ingests | Can it reach Startup deduplication? |
| --- | --- | --- |
| `crunchbase` | `startup`, `investor`, `funding_round` | **Yes** — the `startup` rows are the only rows the deduplicator inspects |
| `linkedin` | `founder`, `executive`, `job_posting` | **No.** Not one of the three is a `startup`, so `dedupeBatch()` skips every entry in a LinkedIn batch and the key is never computed |

So **Startup deduplication is asserted in the Crunchbase test only**, and asserting it in the LinkedIn test would be asserting against a code path a LinkedIn batch cannot enter. What the LinkedIn test asserts instead is the behaviour that actually makes the shared identity work: **parent resolution onto the existing Startup row**, via `resolveStartupKey()` on the same `name` plus `headquarters_location` key cleaning rule 2 de-duplicates on, which is the mechanism by which a LinkedIn founder attaches to a company Crunchbase created rather than creating a second one.

#### The Crunchbase assertion — within-batch deduplication

Fixture rows 1, 2 and 3 form the triple. Row 3 is the negative control: without it the test would pass equally against a deduplicator keyed on `name` alone, which is not the specified rule.

```javascript
(function(outputs, steps, params, stepResult, assertEqual) {
    // ---- per-test substitution ----
    var STEP_20_TOKEN = '';             // <- the run-token step at display order 20
    // ---- end of per-test substitution ----

    var tokenRow = new GlideRecord('x_bst_startuptrk_ingest_staging');
    tokenRow.get(steps(STEP_20_TOKEN).record_id);
    var T = String(new global.JSON().decode(String(tokenRow.getValue('raw_payload'))).token);

    function startupsNamed(name) {
        var found = [];
        var gr = new GlideRecord('x_bst_startuptrk_startup');
        gr.addQuery('name', name);
        gr.orderBy('headquarters_location');
        gr.query();
        while (gr.next()) {
            found.push({ sys_id: String(gr.getUniqueValue()),
                hq: String(gr.getValue('headquarters_location')) });
        }
        return found;
    }

    // Rows 1 and 2 share the key differing only by case: exactly ONE row survives, and its
    // headquarters is Boston, MA — row 1, the first occurrence, is the one that was kept.
    var boston = startupsNamed(T + ' Dedupe Target').filter(function(r) {
        return r.hq === 'Boston, MA';
    });
    assertEqual({ name: 'the case-differing duplicate produced exactly one Boston row',
        shouldbe: 1, value: boston.length });

    // Row 3 is the negative control: same name, different headquarters, therefore a
    // different key, therefore NOT a duplicate.
    var cambridge = startupsNamed(T + ' Dedupe Target').filter(function(r) {
        return r.hq === 'Cambridge, MA';
    });
    assertEqual({ name: 'the same name with a different headquarters was NOT deduplicated',
        shouldbe: 1, value: cambridge.length });
    assertEqual({ name: 'exactly two startups carry that name — one per distinct key',
        shouldbe: 2, value: startupsNamed(T + ' Dedupe Target').length });

    // The loser is rejected with the specified reason, not silently dropped.
    var loser = new GlideRecord('x_bst_startuptrk_ingest_staging');
    loser.addQuery('import_run', T);
    loser.addQuery('record_type', 'startup');
    loser.addQuery('error_message', 'CONTAINS', 'duplicate startup in the same batch');
    loser.query();
    assertEqual({ name: 'exactly one staging row was rejected as a within-batch duplicate',
        shouldbe: 1, value: loser.getRowCount() });
    assertEqual({ name: 'the duplicate row is in the rejected state', shouldbe: 'rejected',
        value: loser.next() ? String(loser.getValue('import_state')) : 'NOT FOUND' });

    stepResult.setOutputMessage('Dedupe key verified: 1 Boston row kept, 1 case-variant ' +
        'rejected as a duplicate, 1 Cambridge row kept as a distinct key.');
    return true;
})(outputs, steps, params, stepResult, assertEqual);
```

#### The LinkedIn assertion — parent resolution, and its failure

`resolveStartupKey(name, headquarters)` returns `{ok, sys_id, matches, reason}`. A blank name gives `the value is blank`; a blank headquarters gives `the row carries no parent headquarters location, and the startup key is the name together with the headquarters location`; no match gives `no startup carries the name and headquarters location`; more than one gives `the name and headquarters location are ambiguous across N startups`. The test asserts the success path against the parent it created at step 30 — supplying both `startup_name` and `startup_headquarters_location` — and the two failure paths against a name that matches nothing and against a row whose parent headquarters is blank.

```javascript
(function(outputs, steps, params, stepResult, assertEqual) {
    // ---- per-test substitution ----
    var STEP_20_TOKEN = '';             // <- the run-token step at display order 20
    // ---- end of per-test substitution ----

    var tokenRow = new GlideRecord('x_bst_startuptrk_ingest_staging');
    tokenRow.get(steps(STEP_20_TOKEN).record_id);
    var T = String(new global.JSON().decode(String(tokenRow.getValue('raw_payload'))).token);

    // Exactly one parent startup exists, and the test created it — LinkedIn wrote none.
    var parents = new GlideRecord('x_bst_startuptrk_startup');
    parents.addQuery('name', T + ' LinkedIn Parent');
    parents.query();
    assertEqual({ name: 'exactly one parent startup carries the name',
        shouldbe: 1, value: parents.getRowCount() });
    assertEqual({ name: 'the parent record is readable', shouldbe: true, value: parents.next() });
    var parentId = String(parents.getUniqueValue());

    // The three accepted children resolved onto THAT row rather than creating another.
    function childParent(table, name) {
        var gr = new GlideRecord(table);
        gr.addQuery('name', name);
        gr.query();
        return gr.next() ? String(gr.getValue('startup')) : 'NOT FOUND';
    }
    assertEqual({ name: 'the founder resolved onto the existing parent',
        shouldbe: parentId, value: childParent('x_bst_startuptrk_founder', T + ' Founder Alpha') });
    assertEqual({ name: 'the executive resolved onto the same parent',
        shouldbe: parentId, value: childParent('x_bst_startuptrk_executive', T + ' Exec Alpha') });
    var job = new GlideRecord('x_bst_startuptrk_jobposting');
    job.addQuery('title', T + ' Sales Lead');
    job.query();
    assertEqual({ name: 'the job posting resolved onto the same parent', shouldbe: parentId,
        value: job.next() ? String(job.getValue('startup')) : 'NOT FOUND' });

    // No LinkedIn row created a Startup: the only startup carrying the token is the parent.
    var anyStartup = new GlideRecord('x_bst_startuptrk_startup');
    anyStartup.addQuery('name', 'STARTSWITH', T);
    anyStartup.query();
    assertEqual({ name: 'the LinkedIn batch created no additional startup',
        shouldbe: 1, value: anyStartup.getRowCount() });

    // The unresolvable parent is rejected with the resolver's own reason, and wrote nothing.
    var orphan = new GlideRecord('x_bst_startuptrk_ingest_staging');
    orphan.addQuery('import_run', T);
    orphan.addQuery('name', T + ' Founder Orphan');
    orphan.query();
    assertEqual({ name: 'the orphan staging row is readable', shouldbe: true, value: orphan.next() });
    assertEqual({ name: 'the orphan row is rejected',
        shouldbe: 'rejected', value: String(orphan.getValue('import_state')) });
    assertEqual({ name: 'its error names the unresolved parent', shouldbe: true,
        value: String(orphan.getValue('error_message')).indexOf('no startup carries the name') !== -1 });
    var orphanFounder = new GlideRecord('x_bst_startuptrk_founder');
    orphanFounder.addQuery('name', T + ' Founder Orphan');
    orphanFounder.query();
    assertEqual({ name: 'no founder record was written for the orphan',
        shouldbe: 0, value: orphanFounder.getRowCount() });

    stepResult.setOutputMessage('Parent resolution verified: 3 children on the existing ' +
        'startup ' + parentId + ', 0 startups created, 1 unresolvable parent rejected.');
    return true;
})(outputs, steps, params, stepResult, assertEqual);
```

**Do not assert which of A and B survives.** "First in the entries array" is a true statement about `dedupeBatch()` and tells you nothing about which staging row lands first, for two independent reasons:

| Cause | Why it makes the order undetermined |
| --- | --- |
| `ingestStaging()` reads the pending rows with `orderBy('sys_id')` | A `sys_id` is a random 32-character identifier, not a monotonic insert sequence, so ordering by it does **not** reproduce the order the rows were written |
| `expandRows()` then sorts the whole batch by record type | The comparator returns `0` for two rows of the same type, and the relative order of equal elements is not specified, so even a fixed read order would not fix the order within a type |


### Rule 3 — choice normalisation, and the `Investor.type` asymmetry

Both branches are asserted in each test, and **the logged event is asserted in every case** — a normalisation that coerced silently would satisfy the stored value but not the rule.
Assert all three branches in each test — a case-insensitive match, an unmatched value on a list that declares `Other`, and an unmatched value on a list that does not. **The columns differ per flow, because each flow writes only the record types its source supplies.**

`Crunchbase Ingestion`:

| Seeded value | Column | `Other` in the list? | Expected |
| --- | --- | --- | --- |
| `fintech` | `x_bst_startuptrk_startup.industry` | Yes | Case-insensitive match, stored as `Fintech`, **no** event |
| `Quantum Widgets` | `x_bst_startuptrk_startup.industry` | Yes | Stored as **`Other`**, and **logged** |
| `Series Q` | `x_bst_startuptrk_fundinground.round_type` | No | **Left unwritten**, and **logged** |
| `Sovereign Wealth` | `x_bst_startuptrk_investor.type` | No | **Left unwritten**, **logged**, and **the investor row still inserts** |
| `ceo` | `x_bst_startuptrk_founder.title` | Yes | Match, stored as `CEO`, **no** event |
| `Chief Vibes Officer` | `x_bst_startuptrk_founder.title` | Yes | Stored as **`Other`**, and **logged** |
| `vp engineering` | `x_bst_startuptrk_executive.title` | Yes | Match, stored as `VP Engineering`, **no** event |
| `platform engineering` | `x_bst_startuptrk_jobposting.department` | Yes | Stored as **`Other`**, and **logged** |
| `Anywhere` | `x_bst_startuptrk_jobposting.remote_type` | No | **Left unwritten**, and **logged** |
| `Principal` | `x_bst_startuptrk_jobposting.seniority` | No | **Left unwritten**, and **logged** |

**The asymmetry must be asserted explicitly.** `x_bst_startuptrk_investor.type` is `VC`, `Angel`, `PE`, `Corporate`, `Accelerator` and has **no `Other` member**, so an unmatched value cannot be coerced. It is left unwritten and logged, and because `type` is **not** mandatory the record itself survives — rejection is reserved for a record missing a mandatory field. The assertion is therefore threefold: the event is logged, `type` is empty on the stored row, and **the row exists**. A test that asserted rejection here would fail against correct behaviour. The same three-part shape applies to `remote_type` and `seniority` in the LinkedIn batch.

`LinkedIn Ingestion`. **None of the four columns above is reachable from this flow**: `linkedin` supplies `founder`, `executive` and `job_posting` only, so a seeded `startup` or `investor` row is rejected as an unsupplied record type and asserts nothing about normalisation. Use this flow's own columns, which carry the same asymmetry:

Left unwritten is not the same as emptied. On an insert the column is empty; on an update the previously stored value survives. The script asserts the update half directly by re-ingesting one row.

```javascript
(function(outputs, steps, params, stepResult, assertEqual) {
    // ---- per-test substitution ----
    var SOURCE = 'crunchbase';              // or 'linkedin'
    var EXPECT_UNMATCHED = 3;               // 3 for crunchbase, 4 for linkedin
    var REJECTED_ROW_UNMATCHED = 1;         // crunchbase row 11's round_type; 0 for linkedin
    var STEP_20_TOKEN = '';                 // <- the run-token step at display order 20
    // ---- end of per-test substitution ----

    var tokenRow = new GlideRecord('x_bst_startuptrk_ingest_staging');
    assertEqual({ name: 'the run-token row is readable', shouldbe: true,
        value: tokenRow.get(steps(STEP_20_TOKEN).record_id) });
    var minted = new global.JSON().decode(String(tokenRow.getValue('raw_payload')));
    var T = String(minted.token);
    assertEqual({ name: 'step 40 parked its returned object on the token record',
        shouldbe: true, value: !!(minted.outcome && minted.outcome.summary) });

    // ---- the coerced branch, and the left-unwritten branch, per source ----
    // Each row of CASES is: table, the column under test, the lookup column, the lookup
    // value, the expected stored value ('' means left unwritten), and whether the run
    // should have logged a choice_unmatched event for it.
    var CASES = SOURCE === 'crunchbase' ? [
        ['x_bst_startuptrk_startup',      'industry',   'name', T + ' Dedupe Target', 'Fintech', false],
        ['x_bst_startuptrk_startup',      'industry',   'name', T + ' Choice Coerce', 'Other',   true],
        ['x_bst_startuptrk_investor',     'type',       'name', T + ' Lead Capital',  'VC',      false],
        ['x_bst_startuptrk_investor',     'type',       'name', T + ' Participant One', '',      true],
        ['x_bst_startuptrk_fundinground', 'round_type', 'startup.name', T + ' Choice Coerce', 'Series A', false]
    ] : [
        ['x_bst_startuptrk_founder',    'title',       'name',  T + ' Founder Alpha',  'CEO',            false],
        ['x_bst_startuptrk_founder',    'title',       'name',  T + ' Founder Beta',   'Other',          true],
        ['x_bst_startuptrk_executive',  'title',       'name',  T + ' Exec Alpha',     'VP Engineering', false],
        ['x_bst_startuptrk_jobposting', 'department',  'title', T + ' Staff Engineer', 'Other',          true],
        ['x_bst_startuptrk_jobposting', 'remote_type', 'title', T + ' Staff Engineer', '',               true],
        ['x_bst_startuptrk_jobposting', 'seniority',   'title', T + ' Staff Engineer', '',               true]
    ];

    var unmatchedExpected = 0;
    var c = 0;
    for (c = 0; c !== CASES.length; c++) {
        var table = CASES[c][0], column = CASES[c][1];
        var lookupField = CASES[c][2], lookupValue = CASES[c][3];
        var expected = CASES[c][4], logged = CASES[c][5];

        var gr = new GlideRecord(table);
        gr.addQuery(lookupField, lookupValue);
        gr.query();
        // The row EXISTS. For the left-unwritten cases this is the assertion that an
        // uncoercible value did not cause a rejection.
        assertEqual({ name: table + ' row for ' + lookupValue + ' exists',
            shouldbe: 1, value: gr.getRowCount() });
        assertEqual({ name: table + ' row is readable', shouldbe: true, value: gr.next() });
        assertEqual({ name: table + '.' + column + ' normalised to "' + expected + '"',
            shouldbe: expected, value: String(gr.getValue(column) || '') });
        if (logged) {
            unmatchedExpected++;
        }
    }

    // Every uncoercible or coerced value was COUNTED. The primary oracle is the unmatched
    // counter on the summary the ingestion wrote, parked by step 40 - it is independent of
    // the configured log level, so a silent coercion fails here even though every stored
    // value above is correct.
    assertEqual({ name: 'summary.unmatched is exactly ' + EXPECT_UNMATCHED,
        shouldbe: EXPECT_UNMATCHED, value: minted.outcome.summary.unmatched });

    // EXPECT_UNMATCHED exceeds the CASES tally by the value on a row that was rejected for a
    // missing mandatory field: normalisation runs BEFORE the mandatory check, so the event is
    // logged and then the record is refused. Crunchbase row 11 is that case; LinkedIn has none.
    assertEqual({ name: 'the CASES tally plus the rejected-row values equals summary.unmatched',
        shouldbe: EXPECT_UNMATCHED, value: unmatchedExpected + REJECTED_ROW_UNMATCHED });

    // Secondary oracle: the log line itself, asserted only when the configured level permits
    // a warn line. It skips itself rather than failing when the level suppresses the line.
    if (new AppProperties().isLogLevelEnabled('warn')) {
        var log = new GlideRecord('syslog');
        log.addQuery('message', 'CONTAINS', '[x_bst_startuptrk.ingestion]');
        log.addQuery('message', 'CONTAINS', 'run="' + T + '"');
        log.addQuery('message', 'CONTAINS', 'event="choice_unmatched"');
        log.query();
        assertEqual({ name: 'exactly ' + EXPECT_UNMATCHED +
            ' choice_unmatched line(s) reached the application log',
            shouldbe: EXPECT_UNMATCHED, value: log.getRowCount() });
    } else {
        stepResult.setOutputMessage('logging.level suppresses warn; the log assertion was ' +
            'skipped and summary.unmatched carried the oracle.');
    }

    // Left unwritten is not emptied: re-ingesting a row that carries a MATCHING value writes
    // it, and a subsequent uncoercible value leaves the stored value in place.
    if (SOURCE === 'crunchbase') {
        var inv = new GlideRecord('x_bst_startuptrk_investor');
        inv.addQuery('name', T + ' Participant One');
        inv.query();
        assertEqual({ name: 'the uncoercible investor is readable', shouldbe: true, value: inv.next() });
        inv.setValue('type', 'PE');
        inv.update();

        var again = new GlideRecord('x_bst_startuptrk_ingest_staging');
        again.initialize();
        again.setValue('source_system', 'crunchbase');
        again.setValue('record_type', 'investor');
        again.setValue('import_state', 'pending');
        again.setValue('import_run', T + '-update');
        again.setValue('name', T + ' Participant One');
        again.setValue('type', 'Sovereign Wealth');
        again.insert();
        new IngestionMapper().ingestStaging(T + '-update', 'crunchbase', T + '-update', 'fallback');

        var after = new GlideRecord('x_bst_startuptrk_investor');
        after.addQuery('name', T + ' Participant One');
        after.query();
        assertEqual({ name: 'the update case still resolves to one investor',
            shouldbe: 1, value: after.getRowCount() });
        assertEqual({ name: 'an uncoercible value left the stored value in place, not emptied',
            shouldbe: 'PE', value: after.next() ? String(after.getValue('type')) : 'NOT FOUND' });
    }

    stepResult.setOutputMessage('Choice normalisation verified across ' + CASES.length +
        ' column(s) with ' + unmatchedExpected + ' logged unmatched value(s).');
    return true;
})(outputs, steps, params, stepResult, assertEqual);
```

### Rule 4 — rejection of records missing mandatory fields

The check is `IngestionMapper.missingMandatory()`, which produces the reason `missing mandatory` followed by the offending field names and logs through `IngestionLogger.rejectRecord()`. **Nothing partial is ever inserted.** One row per record type the flow under test writes, each missing exactly one mandatory field:

| Flow | Record type | Mandatory set | The seeded row omits | Fixture row |
| --- | --- | --- | --- | --: |
| `Crunchbase Ingestion` | `startup` | `name`, `headquarters_location`, `active` | `headquarters_location` | 5 |
| `Crunchbase Ingestion` | `investor` | `name` | `name` | 9 |
| `Crunchbase Ingestion` | `funding_round` | `startup`, `round_date` | `round_date` | 11 |
| `LinkedIn Ingestion` | `founder` | `name`, `startup` | *(the parent, via an unresolvable name)* | 3 |
| `LinkedIn Ingestion` | `executive` | `name`, `startup` | `name` | 5 |
| `LinkedIn Ingestion` | `job_posting` | `startup`, `title` | `title` | 7 |

The founder case is the reference-resolution failure rather than a blank column, because a blank `startup_name` and an unresolvable one both end in the same place — `rejected`, nothing written — and the unresolvable name additionally proves the resolver's own reason text.

```javascript
(function(outputs, steps, params, stepResult, assertEqual) {
    // ---- per-test substitution ----
    var SOURCE = 'crunchbase';          // or 'linkedin'
    var STEP_20_TOKEN = '';             // <- the run-token step at display order 20
    // ---- end of per-test substitution ----

    var tokenRow = new GlideRecord('x_bst_startuptrk_ingest_staging');
    tokenRow.get(steps(STEP_20_TOKEN).record_id);
    var T = String(new global.JSON().decode(String(tokenRow.getValue('raw_payload'))).token);

    // record_type, the field name the error must name, the entity table, the column to look
    // the would-be record up by, and the value that must NOT exist there.
    var CASES = SOURCE === 'crunchbase' ? [
        ['startup',       'headquarters_location', 'x_bst_startuptrk_startup',      'name', T + ' Missing HQ'],
        ['investor',      'name',                  'x_bst_startuptrk_investor',     'name', ''],
        ['funding_round', 'round_date',            'x_bst_startuptrk_fundinground', 'round_type', 'Series Q']
    ] : [
        ['founder',     'no startup carries the name', 'x_bst_startuptrk_founder',    'name',  T + ' Founder Orphan'],
        ['executive',   'name',                        'x_bst_startuptrk_executive',  'name',  ''],
        ['job_posting', 'title',                       'x_bst_startuptrk_jobposting', 'title', '']
    ];

    var c = 0;
    for (c = 0; c !== CASES.length; c++) {
        var recordType = CASES[c][0], mustName = CASES[c][1];
        var table = CASES[c][2], column = CASES[c][3], absentValue = CASES[c][4];

        // The staging row for this record type reached the rejected state, and its
        // error_message names the offending field.
        var staged = new GlideRecord('x_bst_startuptrk_ingest_staging');
        staged.addQuery('import_run', T);
        staged.addQuery('record_type', recordType);
        staged.addQuery('import_state', 'rejected');
        staged.addQuery('error_message', 'CONTAINS', mustName);
        staged.query();
        assertEqual({ name: 'a ' + recordType + ' row was rejected naming ' + mustName,
            shouldbe: true, value: staged.getRowCount() >= 1 });
        assertEqual({ name: 'the rejected ' + recordType + ' row is readable',
            shouldbe: true, value: staged.next() });
        assertEqual({ name: 'the rejected ' + recordType + ' row carries no sys_id of an entity',
            shouldbe: '', value: String(staged.getValue('raw_payload') === null ? '' : '') });

        // NOTHING partial was inserted for it.
        if (absentValue !== '') {
            var entity = new GlideRecord(table);
            entity.addQuery(column, absentValue);
            entity.query();
            assertEqual({ name: 'no ' + table + ' record exists for the rejected row',
                shouldbe: 0, value: entity.getRowCount() });
        }
    }

    // No entity row anywhere carries an empty mandatory column, which is the general form of
    // "nothing partial is ever inserted".
    var MANDATORY = SOURCE === 'crunchbase' ? [
        ['x_bst_startuptrk_startup', 'name'], ['x_bst_startuptrk_startup', 'headquarters_location'],
        ['x_bst_startuptrk_investor', 'name'], ['x_bst_startuptrk_fundinground', 'round_date']
    ] : [
        ['x_bst_startuptrk_founder', 'name'], ['x_bst_startuptrk_founder', 'startup'],
        ['x_bst_startuptrk_executive', 'name'], ['x_bst_startuptrk_executive', 'startup'],
        ['x_bst_startuptrk_jobposting', 'title'], ['x_bst_startuptrk_jobposting', 'startup']
    ];
    var m = 0;
    for (m = 0; m !== MANDATORY.length; m++) {
        var blank = new GlideRecord(MANDATORY[m][0]);
        blank.addQuery('sys_created_by', gs.getUserName());
        blank.addNullQuery(MANDATORY[m][1]);
        blank.query();
        assertEqual({ name: 'no ' + MANDATORY[m][0] + ' row this run created has an empty ' +
            MANDATORY[m][1], shouldbe: 0, value: blank.getRowCount() });
    }

    stepResult.setOutputMessage('Mandatory-field rejection verified for ' + CASES.length +
        ' record type(s); no partial record was written.');
    return true;
})(outputs, steps, params, stepResult, assertEqual);
```

### Rule 1 — trimming, and the ingestion effects

Step 90 asserts the first cleaning rule and then the consequences the ingestion leaves behind — for Crunchbase the join rows, the participant projection and `portfolio_count`; for LinkedIn the parent references already asserted at step 50, plus the trimmed columns.

```javascript
(function(outputs, steps, params, stepResult, assertEqual) {
    // ---- per-test substitution ----
    var SOURCE = 'crunchbase';          // or 'linkedin'
    var STEP_20_TOKEN = '';             // <- the run-token step at display order 20
    // ---- end of per-test substitution ----

    var tokenRow = new GlideRecord('x_bst_startuptrk_ingest_staging');
    tokenRow.get(steps(STEP_20_TOKEN).record_id);
    var T = String(new global.JSON().decode(String(tokenRow.getValue('raw_payload'))).token);

    // ---- Rule 1: every string column is trimmed on the way in ----
    // Each row: table, the trimmed column, the lookup column, the exact expected value.
    var TRIMMED = SOURCE === 'crunchbase' ? [
        ['x_bst_startuptrk_startup',  'name', 'name', T + ' Dedupe Target'],
        ['x_bst_startuptrk_startup',  'headquarters_location', 'name', T + ' Dedupe Target'],
        ['x_bst_startuptrk_investor', 'name', 'name', T + ' Lead Capital']
    ] : [
        ['x_bst_startuptrk_founder',    'name',  'name',  T + ' Founder Alpha'],
        ['x_bst_startuptrk_jobposting', 'title', 'title', T + ' Staff Engineer']
    ];
    var t = 0;
    for (t = 0; t !== TRIMMED.length; t++) {
        var gr = new GlideRecord(TRIMMED[t][0]);
        gr.addQuery(TRIMMED[t][2], TRIMMED[t][3]);
        gr.query();
        assertEqual({ name: TRIMMED[t][0] + ' row found by its trimmed ' + TRIMMED[t][2],
            shouldbe: true, value: gr.next() });
        var stored = String(gr.getValue(TRIMMED[t][1]) || '');
        assertEqual({ name: TRIMMED[t][0] + '.' + TRIMMED[t][1] + ' has no leading space',
            shouldbe: stored, value: stored.replace(/^\s+/, '') });
        assertEqual({ name: TRIMMED[t][0] + '.' + TRIMMED[t][1] + ' has no trailing space',
            shouldbe: stored, value: stored.replace(/\s+$/, '') });
    }
    // The headquarters seeded as '  Boston, MA  ' is stored exactly, which is also what makes
    // the dedupe key match the Cambridge negative control on headquarters rather than padding.
    if (SOURCE === 'crunchbase') {
        var hq = new GlideRecord('x_bst_startuptrk_startup');
        hq.addQuery('name', T + ' Dedupe Target');
        hq.addQuery('headquarters_location', 'Boston, MA');
        hq.query();
        assertEqual({ name: 'the padded headquarters was stored trimmed and is queryable',
            shouldbe: 1, value: hq.getRowCount() });
    }

    if (SOURCE === 'linkedin') {
        stepResult.setOutputMessage('Rule 1 trimming verified across ' + TRIMMED.length +
            ' column(s); parent references were asserted at step 50.');
        return true;
    }

    // ---- The Crunchbase ingestion effects: join rows, projection, portfolio_count ----
    var round = new GlideRecord('x_bst_startuptrk_fundinground');
    round.addQuery('startup.name', T + ' Choice Coerce');
    round.addQuery('round_type', 'Series A');
    round.query();
    assertEqual({ name: 'exactly one funding round was written', shouldbe: 1, value: round.getRowCount() });
    assertEqual({ name: 'the funding round is readable', shouldbe: true, value: round.next() });
    var roundId = String(round.getUniqueValue());

    function investorId(name) {
        var gr = new GlideRecord('x_bst_startuptrk_investor');
        gr.addQuery('name', name);
        gr.query();
        return gr.next() ? String(gr.getUniqueValue()) : '';
    }
    var leadId = investorId(T + ' Lead Capital');
    var p1 = investorId(T + ' Participant One');
    var p2 = investorId(T + ' Participant Two');
    assertEqual({ name: 'the lead investor resolved', shouldbe: true, value: leadId !== '' });
    assertEqual({ name: 'the round carries the resolved lead investor',
        shouldbe: leadId, value: String(round.getValue('lead_investor')) });

    // Exactly two m2m rows, one per participating investor named in the staging row, and the
    // lead is NOT among them — the lead is a first-class reference, not a participant row.
    var m2m = new GlideRecord('x_bst_startuptrk_m2m_round_investor');
    m2m.addQuery('funding_round', roundId);
    m2m.query();
    assertEqual({ name: 'exactly two participant join rows exist', shouldbe: 2, value: m2m.getRowCount() });
    var linked = [];
    while (m2m.next()) {
        linked.push(String(m2m.getValue('investor')));
    }
    assertEqual({ name: 'participant one is linked', shouldbe: true, value: linked.indexOf(p1) !== -1 });
    assertEqual({ name: 'participant two is linked', shouldbe: true, value: linked.indexOf(p2) !== -1 });
    assertEqual({ name: 'the lead investor did not become a participant row',
        shouldbe: -1, value: linked.indexOf(leadId) });

    // The read-only projection the business rule maintains names both participants.
    round = new GlideRecord('x_bst_startuptrk_fundinground');
    round.get(roundId);
    var projection = String(round.getValue('participating_investors') || '');
    assertEqual({ name: 'the projection names participant one',
        shouldbe: true, value: projection.indexOf(p1) !== -1 });
    assertEqual({ name: 'the projection names participant two',
        shouldbe: true, value: projection.indexOf(p2) !== -1 });

    // portfolio_count: one startup for each of the three investors — the lead through
    // lead_investor, the two participants through the join rows.
    function portfolio(id) {
        var gr = new GlideRecord('x_bst_startuptrk_investor');
        return gr.get(id) ? parseInt(gr.getValue('portfolio_count'), 10) : -1;
    }
    assertEqual({ name: 'the lead investor portfolio_count is 1', shouldbe: 1, value: portfolio(leadId) });
    assertEqual({ name: 'participant one portfolio_count is 1', shouldbe: 1, value: portfolio(p1) });
    assertEqual({ name: 'participant two portfolio_count is 1', shouldbe: 1, value: portfolio(p2) });

    // Repointing the round to a second startup moves the count rather than accumulating it,
    // and deleting the round returns every investor to zero.
    var second = new GlideRecord('x_bst_startuptrk_startup');
    second.initialize();
    second.setValue('name', T + ' Second Portfolio Co');
    second.setValue('headquarters_location', 'Boston, MA');
    second.setValue('active', true);
    var secondId = second.insert();
    round.setValue('startup', secondId);
    round.update();
    assertEqual({ name: 'repointing the round keeps the lead count at 1, it does not accumulate',
        shouldbe: 1, value: portfolio(leadId) });
    assertEqual({ name: 'repointing keeps participant one at 1', shouldbe: 1, value: portfolio(p1) });

    round.deleteRecord();
    assertEqual({ name: 'deleting the round returns the lead to 0', shouldbe: 0, value: portfolio(leadId) });
    assertEqual({ name: 'deleting the round returns participant one to 0', shouldbe: 0, value: portfolio(p1) });
    assertEqual({ name: 'deleting the round returns participant two to 0', shouldbe: 0, value: portfolio(p2) });
    var orphanLinks = new GlideRecord('x_bst_startuptrk_m2m_round_investor');
    orphanLinks.addQuery('funding_round', roundId);
    orphanLinks.query();
    assertEqual({ name: 'the join rows cascaded with the deleted round',
        shouldbe: 0, value: orphanLinks.getRowCount() });

    stepResult.setOutputMessage('Ingestion effects verified: 2 join rows, projection naming ' +
        'both participants, portfolio_count 1/1/1 then 0/0/0 after deletion, join rows cascaded.');
    return true;
})(outputs, steps, params, stepResult, assertEqual);
```

### Skip the record, continue the run

Both tests assert the specified failure semantics as well as the counts: a per-record error is logged, **that record is skipped**, and **the run continues**. Three assertions already made carry it, and they are listed together here because the semantics matter more than any one of them:

| Where | The assertion | What a violation would look like |
| --- | --- | --- |
| Step 40 | `accepted` is non-zero **and** `rejected` is non-zero from one call | A run that halted on the first bad row reports rejections and no accepted rows |
| Step 40 | **Every record type that produced a rejection also produced a processed row** | A run that halted on the first bad row of a type refuses that type entirely |
| Step 40 | No entry of any record type was left in a non-terminal state | A run that halted mid-batch leaves later entries unresolved |
| Step 80 | **No** row carrying this token is still `pending` | Same, read from the records rather than the returned object |
| Rule 4's step | No entity row this run created carries an empty mandatory column | A run that inserted partial rows reports no rejections |

**The per-type assertion is what makes this a continuation proof rather than a total.** `expandRows()` sorts the batch into `TYPE_ORDER`, so no assertion can rely on the order rows were seeded in — a positional check would be asserting against the sort, not against the behaviour. Every one of the three record types in each batch therefore carries **both** a rejection and an acceptance: Crunchbase has 2 refused and 3 processed startups, 1 refused and 3 processed investors, 1 refused and 1 processed funding round; LinkedIn has 1 refused and 2 processed founders, 1 refused and 1 processed executive, 1 refused and 2 processed job postings. A run that stopped at the first bad row of any type would fail that type's assertion no matter where the sort placed it.

Per-record skips arising from the four cleaning rules are **expected behaviour and are not errors**. They are counted separately from unhandled errors, and only unhandled errors bear on success criterion 4.

### The wiring assertions

Half B, at step 110. It reads the delivered flow and action records out of the platform's own tables and asserts the shape [`02-flow-crunchbase-ingestion.md`](02-flow-crunchbase-ingestion.md) and [`03-flow-linkedin-ingestion.md`](03-flow-linkedin-ingestion.md) specify. This is the half that fails when the orchestrator is correct but nothing reaches it.

| # | What it asserts | Why it is here |
| --: | --- | --- |
| 1 | The flow record exists in the `x_bst_startuptrk` scope and is **active** | An inactive flow never runs |
| 2 | Its trigger is **scheduled**, repeating, on a **1 hour** interval | The cadence guard pattern depends on an hourly trigger; a daily trigger silently changes the cadence contract |
| 3 | All **five** actions exist in the scope and every one is **published** | An unpublished action cannot be called by a flow |
| 4 | The flow calls exactly **four** actions and contains exactly **one** `If` | The delivered decomposition of [`02-flow-crunchbase-ingestion.md`](02-flow-crunchbase-ingestion.md) and [`03-flow-linkedin-ingestion.md`](03-flow-linkedin-ingestion.md): the cadence guard outside the `If`, then source-mode resolution, payload fetch and the orchestrator inside it. A fifth call, a third call or a missing `If` is a different flow |
| 5 | The **orchestrator action is among the four called** | The action half A tests must be the action the flow invokes |
| 6 | The orchestrator's declared outputs are exactly the **six** counters | A missing output breaks the downstream reconciliation |
| 7 | The fetch action references the credential alias **by name**, and **no credential value appears** in any action or flow record | The alias-by-name binding, and the secret-hygiene gate |
| 8 | The cadence-guard action declares its **four** outputs, including `proceed` | The `If` tests `proceed`; an absent output makes the guard unconditional |

```javascript
(function(outputs, steps, params, stepResult, assertEqual) {
    // ---- per-test substitution ----
    var FLOW_NAME   = 'Crunchbase Ingestion';        // or 'LinkedIn Ingestion'
    var ALIAS_NAME  = 'x_bst_startuptrk.crunchbase_api';  // or x_bst_startuptrk.linkedin_oauth
    var GUARD       = 'Cadence Guard';
    var FETCH       = 'Fetch Crunchbase Payload';    // or 'Fetch LinkedIn Payload'
    var ORCHESTRATE = 'Ingest Crunchbase Batch';     // or 'Ingest LinkedIn Batch'
    var RECONCILE   = 'Reconcile Batch Counters';
    var RESOLVE     = 'Resolve Source Mode';
    // ---- end of per-test substitution ----

    var SCOPE = 'x_bst_startuptrk';

    // 1. The flow exists in the scope and is active.
    var flow = new GlideRecord('sys_hub_flow');
    flow.addQuery('name', FLOW_NAME);
    flow.addQuery('sys_scope.scope', SCOPE);
    flow.query();
    assertEqual({ name: 'the flow ' + FLOW_NAME + ' exists in ' + SCOPE,
        shouldbe: 1, value: flow.getRowCount() });
    assertEqual({ name: 'the flow record is readable', shouldbe: true, value: flow.next() });
    assertEqual({ name: 'the flow is active',
        shouldbe: true, value: String(flow.getValue('active')) === '1' });
    var flowId = String(flow.getUniqueValue());

    // 2. A scheduled trigger repeating every 1 hour.
    var trigger = new GlideRecord('sys_hub_trigger_instance');
    trigger.addQuery('flow', flowId);
    trigger.query();
    assertEqual({ name: 'the flow carries exactly one trigger', shouldbe: 1, value: trigger.getRowCount() });
    assertEqual({ name: 'the trigger is readable', shouldbe: true, value: trigger.next() });
    var triggerType = String(trigger.trigger_type.name || trigger.getValue('trigger_type') || '');
    assertEqual({ name: 'the trigger is a scheduled trigger',
        shouldbe: true, value: triggerType.toLowerCase().indexOf('schedul') !== -1 });
    var triggerValues = String(trigger.getValue('values') || '');
    assertEqual({ name: 'the schedule repeats hourly', shouldbe: true,
        value: triggerValues.indexOf('hour') !== -1 || triggerValues.indexOf('3600') !== -1 });

    // 3. All five actions exist in the scope and every one is published.
    var ACTIONS = [GUARD, RESOLVE, FETCH, ORCHESTRATE, RECONCILE];
    var a = 0;
    for (a = 0; a !== ACTIONS.length; a++) {
        var action = new GlideRecord('sys_hub_action_type_base');
        action.addQuery('name', ACTIONS[a]);
        action.addQuery('sys_scope.scope', SCOPE);
        action.query();
        assertEqual({ name: 'the action ' + ACTIONS[a] + ' exists in ' + SCOPE,
            shouldbe: 1, value: action.getRowCount() });
        assertEqual({ name: ACTIONS[a] + ' is readable', shouldbe: true, value: action.next() });
        assertEqual({ name: ACTIONS[a] + ' is Published',
            shouldbe: 'published', value: String(action.getValue('status') || '').toLowerCase() });
    }

    // 4 and 5. Exactly four action calls and one If, and the orchestrator is one of them.
    var calls = 0, ifs = 0, callsOrchestrator = false;
    var instance = new GlideRecord('sys_hub_action_instance');
    instance.addQuery('flow', flowId);
    instance.query();
    while (instance.next()) {
        var called = String(instance.action_type_id.name || '');
        if (called === 'If') {
            ifs++;
        } else {
            calls++;
            if (called === ORCHESTRATE) {
                callsOrchestrator = true;
            }
        }
    }
    assertEqual({ name: 'the flow calls exactly four actions', shouldbe: 4, value: calls });
    assertEqual({ name: 'the flow contains exactly one If', shouldbe: 1, value: ifs });
    assertEqual({ name: 'the orchestrator action ' + ORCHESTRATE + ' is one of the four called',
        shouldbe: true, value: callsOrchestrator });

    // 6 and 8. The declared outputs of the two actions the test depends on.
    function declaredOutputs(actionName) {
        var names = [];
        var owner = new GlideRecord('sys_hub_action_type_base');
        owner.addQuery('name', actionName);
        owner.addQuery('sys_scope.scope', SCOPE);
        owner.query();
        if (!owner.next()) {
            return names;
        }
        var io = new GlideRecord('sys_hub_action_output');
        io.addQuery('model', String(owner.getUniqueValue()));
        io.query();
        while (io.next()) {
            names.push(String(io.getValue('element')));
        }
        return names;
    }
    var orchestratorOut = declaredOutputs(ORCHESTRATE);
    var EXPECT_OUT = ['processed', 'rejected', 'skipped', 'duplicates', 'unmatched', 'recorded'];
    assertEqual({ name: ORCHESTRATE + ' declares exactly six outputs',
        shouldbe: 6, value: orchestratorOut.length });
    var o = 0;
    for (o = 0; o !== EXPECT_OUT.length; o++) {
        assertEqual({ name: ORCHESTRATE + ' declares the output ' + EXPECT_OUT[o],
            shouldbe: true, value: orchestratorOut.indexOf(EXPECT_OUT[o]) !== -1 });
    }
    var guardOut = declaredOutputs(GUARD);
    assertEqual({ name: GUARD + ' declares exactly four outputs', shouldbe: 4, value: guardOut.length });
    assertEqual({ name: GUARD + ' declares proceed, which the If tests',
        shouldbe: true, value: guardOut.indexOf('proceed') !== -1 });

    // 7. The alias is referenced BY NAME, and no credential material appears anywhere in the
    //    flow or its actions.
    var aliasReferenced = false, secretFound = '';
    var SECRET_HINTS = ['api_key=', 'apikey=', 'client_secret', 'refresh_token', 'Bearer ',
        'password='];
    var scripts = new GlideRecord('sys_hub_action_type_base');
    scripts.addQuery('sys_scope.scope', SCOPE);
    scripts.query();
    while (scripts.next()) {
        var body = '';
        var step = new GlideRecord('sys_hub_step_instance');
        step.addQuery('action_type', String(scripts.getUniqueValue()));
        step.query();
        while (step.next()) {
            body += String(step.getValue('values') || '');
        }
        if (body.indexOf(ALIAS_NAME) !== -1) {
            aliasReferenced = true;
        }
        var h = 0;
        for (h = 0; h !== SECRET_HINTS.length; h++) {
            if (body.indexOf(SECRET_HINTS[h]) !== -1) {
                secretFound = SECRET_HINTS[h] + ' in ' + String(scripts.getValue('name'));
            }
        }
    }
    assertEqual({ name: 'the alias ' + ALIAS_NAME + ' is referenced by name',
        shouldbe: true, value: aliasReferenced });
    assertEqual({ name: 'no credential material appears in any action of this scope',
        shouldbe: '', value: secretFound });

    stepResult.setOutputMessage('Wiring verified for ' + FLOW_NAME + ': active, hourly ' +
        'scheduled trigger, 5 published actions, 4 action calls plus 1 If, ' + ORCHESTRATE +
        ' called with 6 declared outputs, ' + GUARD + ' declaring proceed, alias ' +
        ALIAS_NAME + ' bound by name, no credential material.');
    return true;
})(outputs, steps, params, stepResult, assertEqual);
```

Assertion 7 sweeps every action in the scope rather than only the two this flow calls, so the secret-hygiene half holds for the whole application and not merely for the flow under test. It is the same gate the delivery checks statically against the Update Set; asserting it at run time catches a secret introduced by hand on the instance after import.

### The published-evidence assertion

Use this script at step 70. It is the assertion that proves the step `8b` Log action of the two flow guides exists, is bound to `8a`'s `log_text` output, and published a **complete** block rather than merely a block.

```javascript
(function(outputs, steps, params, stepResult, assertEqual) {
    var contextId = String(steps('60').run_context);

    // The flow log column that carries an action's message is release-dependent.
    // Probe a short candidate list; whichever one holds it, the rendered block
    // always opens with the run= header line.
    var CANDIDATES = ['message', 'log_message', 'log', 'text', 'value'];
    var header = '';
    var log = new GlideRecord('sys_flow_log');
    log.addQuery('context', contextId);
    log.query();
    while (log.next() && header === '') {
        for (var c = 0; c < CANDIDATES.length; c++) {
            var candidate = String(log.getValue(CANDIDATES[c]) || '');
            if (candidate.indexOf('run=') > -1) {
                header = candidate;
                break;
            }
        }
    }

    assertEqual({ name: 'the Log action published an evidence block',
        shouldbe: true, value: header !== '' });
    if (header === '') {
        stepResult.setOutputMessage('No flow log record for context ' + contextId +
            ' carries a run= header. Either step 8b has no Log action, or its Message ' +
            'input is not bound to the step 8a script output log_text.');
        return false;
    }

    var lines = header.split('\n');
    var firstLine = lines[0];
    function member(name) {
        var found = firstLine.match(new RegExp(name + '=([^\\s]+)'));
        return found ? found[1] : '';
    }

    assertEqual({ name: 'provenance is fallback',        shouldbe: 'fallback', value: member('provenance') });
    assertEqual({ name: 'the run summary was recorded',  shouldbe: 'true',     value: member('summary_logged') });
    assertEqual({ name: 'no event was dropped',          shouldbe: '0',        value: member('events_dropped') });
    assertEqual({ name: 'no record was skipped',         shouldbe: '0',        value: member('skipped') });
    assertEqual({ name: 'the batch reconciled',          shouldbe: 'true',     value: member('reconciled') });
    assertEqual({ name: 'at least one event was published',
        shouldbe: true, value: parseInt(member('events'), 10) > 0 });

    // The mandatory summary is rendered FIRST, directly beneath the header, precisely
    // so truncation can never remove it. Assert its position, not just its presence.
    assertEqual({ name: 'the run_summary event is the first event line',
        shouldbe: true,
        value: lines.length > 1 && lines[1].indexOf('event="run_summary"') > -1 });

    // An omitted= line means the block ceiling removed events. That is required-data
    // truncation and it clears the flow's evidence_complete output.
    assertEqual({ name: 'no event was omitted from the block',
        shouldbe: -1, value: header.indexOf('omitted="') });

    outputs.run_id      = member('run');
    outputs.log_text    = header;
    outputs.event_count = parseInt(member('events'), 10);

    assertEqual({ name: 'the run identifier was parsed from the block',
        shouldbe: true, value: /^[a-z]+-[0-9]{14}-[0-9a-f]{16}$/.test(outputs.run_id) });

    stepResult.setOutputMessage('Published: ' + firstLine);
    return true;
})(outputs, steps, params, stepResult, assertEqual);
```

**`run=` is parsed rather than chosen.** The run identifier is minted by step 1 of the flow, not by the test, so the test learns it from the published block and uses it to correlate every later assertion. A test that invents its own run identifier is not observing the flow. Its shape is asserted too — source token, fourteen digits, sixteen hexadecimal characters — because a run identifier without the GUID suffix is a build that did not take the flow guides' step 1 script.

### The run-closure assertion

Use this script at step 75. Step 70 proves the evidence reached the flow execution log; **this step proves the flow itself judged the run fit to count.**

The two are different claims and both are needed. `8a` renders and `8b` publishes; only `8c` evaluates the health predicate, and only `8c` stamps the completion marker. An earlier build asserted neither, and took `published` and `healthy` from a step that set them before the Log action had run — so a suite could report a passing flow test against an execution whose evidence never left the flow.

```javascript
(function(outputs, steps, params, stepResult, assertEqual) {
    var runId = String(steps('70').run_id);

    assertEqual({ name: 'step 70 supplied a run identifier',
        shouldbe: true, value: runId !== '' });
    if (runId === '') { return false; }

    function lineFor(eventName) {
        var log = new GlideRecord('syslog');
        log.addQuery('source', 'x_bst_startuptrk');
        log.addQuery('message', 'CONTAINS', 'event="' + eventName + '"');
        log.addQuery('message', 'CONTAINS', 'run="' + runId + '"');
        log.orderByDesc('sys_created_on');
        log.setLimit(1);
        log.query();
        return log.next() ? String(log.getValue('message')) : '';
    }

    var closed = lineFor('run_closed');
    assertEqual({ name: 'part 8c wrote a run_closed line',
        shouldbe: true, value: closed !== '' });
    if (closed === '') {
        stepResult.setOutputMessage('No run_closed line for ' + runId +
            '. Part 8c did not execute, which means part 8b did not complete.');
        return false;
    }

    function member(name) {
        var found = closed.match(new RegExp(name + '="([^"]*)"'));
        return found ? found[1] : '';
    }

    assertEqual({ name: '8c asserted publication',      shouldbe: 'true', value: member('published') });
    assertEqual({ name: 'the run is healthy',           shouldbe: 'true', value: member('healthy') });
    assertEqual({ name: 'no fault token was raised',    shouldbe: 'none', value: member('faults') });
    assertEqual({ name: 'the completion marker was stamped',
        shouldbe: 'true', value: member('marker_stamped') });
    assertEqual({ name: 'the completion marker read back',
        shouldbe: 'true', value: member('marker_verified') });
    assertEqual({ name: 'the lease was not released, because the run succeeded',
        shouldbe: 'false', value: member('lease_released') });

    // The complementary proof: an unhealthy run writes this line instead.
    assertEqual({ name: 'no run_incomplete line exists for this run',
        shouldbe: '', value: lineFor('run_incomplete') });

    outputs.completion_stamp = member('stamp');
    stepResult.setOutputMessage('Run closed healthy; stamp=' + outputs.completion_stamp +
        '; faults=' + member('faults'));
    return true;
})(outputs, steps, params, stepResult, assertEqual);
```

**`faults` is asserted equal to `none`, not merely non-empty.** `8c` joins its fault tokens with commas and the log line prints `none` when the list is empty, so an equality assertion catches every one of the thirteen members of the health predicate — including the two, `operational_skips` and `claim_parse`, that an execution can raise while still writing every record it was asked to.

### The teardown step

Use this script at step 160. It is the last step of each flow test and its body is wrapped in `try`/`finally`, so the claim release happens even when an assertion inside it throws.

```javascript
(function(outputs, steps, params, stepResult, assertEqual) {
    var SOURCE = 'crunchbase';                       // or 'linkedin'
    var OTHER  = SOURCE === 'crunchbase' ? 'linkedin' : 'crunchbase';
    var props  = new AppProperties();
    var released = false;

    try {
        // 1. Release any claim this suite's executions could have left running. The
        //    run identifier is the one step 40 and step 60 wrote into the marker.
        released = props.releaseRunLease(SOURCE, SOURCE + '-atf') === true;

        var markers = props.readRunMarkers();
        var mine = markers[SOURCE];
        var other = markers[OTHER];

        // 2. This source's entry must be absent or settled: absent, or state
        //    succeeded.
        assertEqual({ name: 'this source carries no running claim',
            shouldbe: true, value: !mine || mine.state === 'succeeded' });

        // 3. The other source's entry must be exactly what step 20 captured.
        assertEqual({ name: "the other source's entry is untouched",
            shouldbe: String(steps('20').other_entry),
            value: other ? (OTHER + '=' + other.provenance + '|' + other.state + '|' +
                other.stamp + '|' + other.run) : '' });

        // 4. The source mode is a precondition, not a test write. It must be unchanged.
        assertEqual({ name: 'the source mode is still fallback',
            shouldbe: 'fallback', value: props.getSourceMode() });

        outputs.final_marker = mine ? (mine.provenance + '|' + mine.state + '|' +
            mine.stamp + '|' + mine.run) : '(absent)';
        outputs.claim_released = released;
    } finally {
        stepResult.setOutputMessage('Control state left defined: ' + SOURCE + '=' +
            String(outputs.final_marker || '(unread)') +
            '; claim_released=' + released +
            '; source_mode=' + props.getSourceMode() +
            '. Record this in the post-suite residue queries.');
    }
    return true;
})(outputs, steps, params, stepResult, assertEqual);
```

**The teardown asserts a defined state; it does not claim to have restored a previous one.** [The control state](#the-control-state-each-test-borrows-and-what-it-can-and-cannot-return) sets out why a restore is not available here and what is enforced instead. The `finally` guarantees the output message — and therefore the recorded value — even when one of the four assertions fails, so an operator reading a failed teardown still learns what the property holds.

Steps 80 to 130 correlate through `syslog` as well as through the published block, because [`02-flow-crunchbase-ingestion.md`](02-flow-crunchbase-ingestion.md#72--every-log-record-this-flow-can-write) records that every `IngestionLogger` event appears on **both** surfaces. Filter `syslog` on `message` `contains` the step 70 `run_id` and read the events from there; the published block is the authority for the header line and for the fact of publication.


## Suite and test roll-up

| Suite group | Suites | Tests | Requirement satisfied |
| --- | --: | --: | --- |
| Table CRUD — one suite per entity table | 7 | 7 | 100 % of the 7 tables have a passing test; success criterion 1's field-by-field coverage |
| Premium field access control | 1 | 21 | 7 premium fields under each of 3 roles, verified per role per field; success criterion 2 |
| REST resources | 1 | 6 | 100 % of the 6 logical resources including the nested sub-resource, with pagination and the 429 contract; success criterion 3 |
| Ingestion flows | 1 | 2 | One test per flow, with all four cleaning rules and provenance labelling; success criterion 4 |
| **Total** | **10** | **36** | |

The arithmetic is **7 + 21 + 6 + 2 = 36 tests across 10 suites**. Both totals must hold at delivery. A suite count of 10 with a test count below 36 means a cell, a resource or a table is uncovered, and the [Coverage gate](#coverage-gate) blocks delivery.

## Technique (a) — impersonation

Every one of the 21 tests in suite 8 **impersonates a purpose-created user holding exactly one scoped role and none of the elevated platform roles**. The three users are **created by the test setup steps at run time**, not shipped in the Update Set, because `sys_user` sits outside the application scope and the requirements forbid modifying anything outside `x_bst_startuptrk`. The mechanic is stated here; the decision is recorded in [`../../../docs/decisions/DECISION_LOG.md`](../../../docs/decisions/DECISION_LOG.md).

### The three users

| User | First / last name | The one role it holds | Used by |
| --- | --- | --- | --- |
| `BST ATF admin` | `BST ATF` / `admin` | `x_bst_startuptrk.admin` | Every fixture-writing step in all ten suites, and the seven `ACL-*.1` cells |
| `BST ATF premium` | `BST ATF` / `premium` | `x_bst_startuptrk.premium_user` | The seven `ACL-*.2` cells |
| `BST ATF base` | `BST ATF` / `base` | `x_bst_startuptrk.user` | The seven `ACL-*.3` cells |

### Step 1 — the setup step that creates the user and assigns exactly one role

**Create a User** (Server - Independent) does both in one step. Add it as the first step of any test that needs the user.

| Input | Value |
| --- | --- |
| `first_name` | `BST ATF` |
| `last_name` | `base` — or `admin`, or `premium` |
| `roles` | **Exactly one** entry: `x_bst_startuptrk.user` — or `x_bst_startuptrk.admin`, or `x_bst_startuptrk.premium_user`. Add nothing else. |
| `groups` | Leave **empty**. A group can carry roles, and a role inherited through a group is as real as a directly assigned one. |
| `impersonate` | Leave **false**. Impersonate through an explicit step so the switch is visible in the step results. |
| `table` | `sys_user` |
| Output | `user`, a reference this test's later steps bind to. |

### Step 2 — verify the role set before trusting the test

Add this **Run Server Side Script** step immediately after **every** `Create a User` step, **in every test that creates a user**. It is the step that makes the impersonation claim checkable rather than assumed.

**It is never shared across tests, and never done once for a suite.** Each `Create a User` step creates a **new** `sys_user` record inside its own test's transaction, and the framework rolls that record back when the test ends — so there is no persistent user that a suite-level verification could have verified, and a later test's user is a different record with its own role assignments. A cell that relied on another cell's verification would be asserting against a user that no longer exists.

The counts that follow from that rule, per suite:

| Suite group | Tests | `Create a User` steps per test | Verification steps |
| --- | --: | --: | --: |
| 1 to 7, table CRUD | 7 | 1, at display order 5 | **7** |
| 8, the `*.1` cells | 7 | 1, at display order 5 | **7** |
| 8, the `*.2` and `*.3` cells | 14 | 2, at display orders 5 and 35 | **28** |
| 9, REST resources | 6 | 1, at display order 5 | **6** |
| 10, ingestion | 2 | 1, at display order 5 | **2** |
| | | **Total** | **50** |

```javascript
(function(outputs, steps, params, stepResult, assertEqual) {
    // ---- per-step substitution ----
    var EXPECTED = 'x_bst_startuptrk.user';   // the single scoped role this user must hold
    // Contract 1: the generated sys_id of the Create a User step THIS step verifies.
    var STEP_CREATE_USER = '';                // <- display order 5, or 35 for the second user
    // ---- end of per-step substitution ----

    var SCOPE_PREFIX = 'x_bst_startuptrk.';
    var FORBIDDEN = ['admin', 'security_admin', 'maint', 'atf_test_admin',
        'atf_test_designer', 'impersonator', 'user_admin', 'personalize_dictionary'];

    var userId = String(steps(STEP_CREATE_USER).user || '');
    assertEqual({ name: 'the Create a User step produced a user reference',
        shouldbe: true, value: userId !== '' });

    var user = new GlideRecord('sys_user');
    assertEqual({ name: 'the created user record exists', shouldbe: true, value: user.get(userId) });
    assertEqual({ name: 'the created user is active',
        shouldbe: true, value: String(user.getValue('active')) === '1' });

    // Every role the user holds, directly assigned or inherited through containment or a
    // group. sys_user_has_role carries both, and `inherited` distinguishes them.
    var held = [];
    var inherited = [];
    var link = new GlideRecord('sys_user_has_role');
    link.addQuery('user', userId);
    link.query();
    while (link.next()) {
        var roleName = String(link.role.name);
        held.push(roleName);
        if (String(link.getValue('inherited')) === '1') {
            inherited.push(roleName);
        }
    }

    // 1. Exactly one scoped role, and it is the expected one.
    var scoped = held.filter(function(r) { return r.indexOf(SCOPE_PREFIX) === 0; });
    assertEqual({ name: 'holds exactly one scoped role', shouldbe: 1, value: scoped.length });
    assertEqual({ name: 'the scoped role is ' + EXPECTED,
        shouldbe: EXPECTED, value: scoped.length === 1 ? scoped[0] : held.join(',') });

    // 2. None of the elevated platform roles, directly or inherited. Named individually so
    //    the failure message says which one was found.
    var i = 0;
    for (i = 0; i !== FORBIDDEN.length; i++) {
        assertEqual({ name: 'does not hold the platform role ' + FORBIDDEN[i],
            shouldbe: -1, value: held.indexOf(FORBIDDEN[i]) });
    }

    // 3. No group membership, because a group can carry roles and an inherited role is as
    //    real as a directly assigned one.
    var groups = new GlideAggregate('sys_user_grmember');
    groups.addQuery('user', userId);
    groups.addAggregate('COUNT');
    groups.query();
    var groupCount = 0;
    if (groups.next()) {
        groupCount = parseInt(groups.getAggregate('COUNT'), 10) || 0;
    }
    assertEqual({ name: 'belongs to no group', shouldbe: 0, value: groupCount });

    stepResult.setOutputMessage('Role set verified for ' + user.getValue('user_name') +
        ': scoped=[' + scoped.join(', ') + '] all=[' + held.join(', ') +
        '] inherited=[' + inherited.join(', ') + '] groups=' + groupCount);
    return true;
})(outputs, steps, params, stepResult, assertEqual);
```

The forbidden list names the platform administrator role first because it is the one that matters most: record access controls allow it to override them, so a user holding it passes every read and fails no denial. `impersonator`, `user_admin` and `personalize_dictionary` are included because each grants a way around the boundary this suite exists to prove.

### Step 3 — the impersonation step

**Impersonate** (Server - Independent), `user` = the **Create a User** output. Place it after every fixture-writing step and before the assertion step, because the fixture must be written by `x_bst_startuptrk.admin` while the read must be attempted by the role under test. A test may carry more than one **Impersonate** step; the later one supersedes.

### Step 4 — teardown

**No teardown step is required for the impersonation users, and none is added.** ATF rolls back the data a test creates when the test finishes, so the three users, their role assignments and every fixture record are removed automatically. Two consequences follow, and both are load-bearing:

- Do **not** rely on a user created by one test being present in another. Each test that impersonates creates its own.
- After a run, `sys_user` must carry **no** residual `BST ATF` user. If it does, a test errored in a way that left the transaction open; investigate before trusting any result in that run.

**The system properties suite 10 writes are the exception, and they need explicit teardown.** Rollback covers records a test *created*; a property is a pre-existing record the test *updated*, so it stays changed. That is why suite 10 alone carries steps 15 and 95 and the out-of-band restoration of [Protecting the cadence state](#the-fixture-step). Suites 1 to 9 write no property and need none.

### Operational warning — the administrator ACL override

**Record ACLs by default allow the platform administrator role to override them, and every operator of a personal developer instance holds that role.** A walkthrough performed as the instance administrator will therefore display **all seven premium fields** and **appear to prove enforcement that was never tested**. The suite reports `success`, the fields are visible, and nothing about the field-level ACLs has been exercised at all.

All forty-nine delivered ACLs carry the administrator-override flag, so this is the default and expected behaviour of the platform, not a defect in the ACLs.

Three rules follow, and none of them is optional:

1. **Never read a premium field as yourself.** Every read assertion sits after an **Impersonate** step.
2. **The scoped `x_bst_startuptrk.admin` role is not the platform administrator role.** They are two different records. `BST ATF admin` holds the scoped role only, which is why the `ACL-*.1` cells prove something; a user holding the platform role would pass those cells by override.
3. **Verify the role set, do not assume it.** The step 2 script above exists for this reason. A `BST ATF base` user that silently acquired `admin` turns all seven denied cells into false passes.

[`../access-control.md`](../access-control.md) states the same impersonation requirement and names the reviewer entry that owns it; read its verification procedure alongside this section. The trap is also recorded in [`../gaps-and-flags.md`](../gaps-and-flags.md) as a gap in any naive verification procedure rather than a gap in the platform.

## Technique (b) — the disposable REST caller

Suite 9 needs an authenticating identity, because `Send REST Request - Inbound` performs a real inbound HTTP request. **No standing account with a working password is created for it.** The identity is minted at step 30 of each REST test and destroyed at step 190 of the same test. The mechanic is stated here; the decision is recorded in [`../../../docs/decisions/DECISION_LOG.md`](../../../docs/decisions/DECISION_LOG.md).

### Exactly one record persists, and it holds nothing usable

The step's **Basic authentication** input is a reference to a `sys_auth_profile_basic` record, and a step input is bound when the step is built rather than when it runs. A profile created inside the test cannot be referenced by a step that already exists, so **one** profile record has to pre-exist. Nothing else does.

| Artifact | Persists | What it holds between runs |
| --- | --- | --- |
| `BST ATF REST caller` (`sys_auth_profile_basic`) | **Yes** — one record, built once by hand | A user name that resolves to **no** `sys_user`, and a random password nobody holds. It authenticates nothing. |
| The caller account (`sys_user`) | **No** | — |
| Its role grant (`sys_user_has_role`) | **No** | — |

Build the shell once: **All** > **System Web Services** > **Outbound** > **Basic Auth Configurations** > **New**, `Name` = `BST ATF REST caller`, **User name** = `bst.atf.retired`, **Password** = any 32-character random string you discard. Save. It is now precondition 14.

**The step resolves the referenced profile when it runs, not when it was built**, which is what lets a test rebind the shell to the identity it just minted. If step 50 of a REST test returns `401` rather than `200`, that resolution is not happening on this instance: check the step's `authentication_type` is **Basic authentication** and that step 30 reported the rebinding succeeded.

**Suite 9's six tests share the shell, so they must not run concurrently.** ATF serialises execution against a single runner and [Run](#run) requires serial execution, which is sufficient — but a second operator running a suite in parallel would have two tests rebinding one record. Precondition 13 forbids it.

### Cleanup is guaranteed by convergence, not by a trailing step

**ATF stops a test at its first failed step.** A cleanup step placed last therefore does not run when an earlier step fails, so a design that relies on one is a design that leaks a live credential exactly when something has gone wrong. This suite closes that three ways, and each is independent of the others.

| # | Mechanism | What it guarantees |
| --- | --- | --- |
| 1 | **Every test's step 30 retires the shell and deletes every earlier disposable caller before minting its own.** The sweep is unconditional and keys on the `bst.atf.rest.` user-name prefix rather than on any prior step's output. | Residue from a crashed run is removed at the head of the next run, whether or not that run's own teardown ever executes. This is what makes the cleanup **converge**. |
| 2 | **Both step 30 and step 190 wrap their record work in `try`/`finally`, with the shell retirement in the `finally`.** | A throw part-way through minting or asserting still leaves the shell holding a user name that resolves to no account and a secret nobody holds. This is the literal guaranteed-finally. |
| 3 | **[Post-suite residue queries](#post-suite-residue-queries)** are run by the operator after the suite and read by the coverage gate. | Detection. If mechanisms 1 and 2 both somehow failed, the gate refuses to pass rather than the leak going unnoticed. |

**Every write and every restoration is asserted**, in both steps — the rebinding, the role grant, the role count, the retirement, and the absence of residue afterwards. Nothing in this technique is assumed.

### Step 30 — mint the caller and bind the shell

```javascript
(function(outputs, steps, params, stepResult, assertEqual) {
    var SHELL = 'BST ATF REST caller';
    var ROLE  = 'x_bst_startuptrk.user';

    // The Basic Auth Configuration user-name column is spelled differently across
    // releases, so write whichever one this instance carries.
    function setIfPresent(gr, names, value) {
        var i = 0;
        for (i = 0; i < names.length; i++) {
            if (gr.isValidField(names[i])) {
                gr.setValue(names[i], value);
                return names[i];
            }
        }
        return '';
    }

    var token    = String(new GlideDateTime().getNumericValue());
    var userName = 'bst.atf.rest.' + token;

    // A cryptographically secure 40-character random string from the platform's secure
    // random utility, with a four-character supplement so the value spans lower case,
    // upper case, digit and symbol and a default complexity policy accepts it.
    // GUID generation is NOT used: gs.generateGUID() is an identifier generator, its
    // output is not guaranteed to be drawn from a cryptographically secure source, and
    // a live password must be. The value is never written to a step output or a log line.
    function newSecret() {
        return GlideSecureRandomUtil.getSecureRandomString(40) + 'aA1!';
    }
    var secret = newSecret();
    assertEqual({ name: 'the generated secret is at least 40 characters',
        shouldbe: true, value: secret.length >= 40 });

    // Unconditional convergence sweep: retire the shell and remove every disposable
    // caller an earlier run may have left behind, before minting this run's own.
    var priorShell = new GlideRecord('sys_auth_profile_basic');
    if (priorShell.get('name', SHELL)) {
        setIfPresent(priorShell, ['user_name', 'username'], 'bst.atf.retired');
        priorShell.setValue('password', newSecret());
        priorShell.update();
    }
    var stale = new GlideRecord('sys_user');
    stale.addQuery('user_name', 'STARTSWITH', 'bst.atf.rest.');
    stale.query();
    var swept = 0;
    while (stale.next()) {
        var staleGrants = new GlideRecord('sys_user_has_role');
        staleGrants.addQuery('user', stale.getUniqueValue());
        staleGrants.deleteMultiple();
        stale.deleteRecord();
        swept = swept + 1;
    }
    assertEqual({ name: 'no disposable caller remains from an earlier run',
        shouldbe: 0, value: (function () {
            var left = new GlideRecord('sys_user');
            left.addQuery('user_name', 'STARTSWITH', 'bst.atf.rest.');
            left.query();
            return left.getRowCount();
        })() });

    var role = new GlideRecord('sys_user_role');
    if (!role.get('name', ROLE)) {
        stepResult.setFailed('Role ' + ROLE + ' not found. The Update Set did not commit.');
        return false;
    }

    var user = new GlideRecord('sys_user');
    user.initialize();
    user.setValue('user_name', userName);
    user.setValue('first_name', 'BST ATF');
    user.setValue('last_name', 'REST caller');
    user.setValue('user_password', secret);
    user.setValue('web_service_access_only', true);   // non-interactive use only
    user.setValue('locked_out', false);
    user.setValue('active', true);
    var userId = user.insert();
    assertEqual({ name: 'disposable caller created', shouldbe: true, value: !!userId });
    if (!userId) { return false; }

    var grant = new GlideRecord('sys_user_has_role');
    grant.initialize();
    grant.setValue('user', userId);
    grant.setValue('role', role.getUniqueValue());
    grant.insert();

    // The caller must hold exactly one role, or the premium-omission assertion of
    // step 80 could pass for the wrong reason.
    var held = [];
    var check = new GlideRecord('sys_user_has_role');
    check.addQuery('user', userId);
    check.query();
    while (check.next()) { held.push(String(check.role.name)); }
    assertEqual({ name: 'caller holds exactly one role', shouldbe: 1, value: held.length });
    assertEqual({ name: 'and it is the base role',       shouldbe: ROLE, value: held.join(',') });

    var shell = new GlideRecord('sys_auth_profile_basic');
    if (!shell.get('name', SHELL)) {
        stepResult.setFailed('Basic Auth Configuration "' + SHELL +
            '" not found. Build the shell as precondition 14.');
        return false;
    }
    var boundField = setIfPresent(shell, ['user_name', 'username'], userName);
    shell.setValue('password', secret);
    var rebound = shell.update();
    assertEqual({ name: 'shell user-name column resolved', shouldbe: true, value: boundField !== '' });
    assertEqual({ name: 'shell rebound to the disposable caller', shouldbe: true, value: !!rebound });

    outputs.caller_id        = userId;
    outputs.caller_user_name = userName;
    stepResult.setOutputMessage('Swept ' + swept + ' stale caller(s); minted ' + userName +
        ' (web_service_access_only, 1 role) and bound it to "' + SHELL +
        '" via column ' + boundField + '. The password is not recorded anywhere.');
    return true;
})(outputs, steps, params, stepResult, assertEqual);
```

**The password appears in no step output, no output message and no log line.** It exists in the two records for the duration of one test and is discarded.

**Wrap the body from the mint onwards in `try`/`finally`, with the shell retirement in the `finally`.** The script above is written linearly for readability; when you enter it into the step, place everything from `var role = new GlideRecord('sys_user_role');` inside a `try` whose `finally` re-reads the shell and, **only when `outputs.caller_id` is empty**, returns it to `bst.atf.retired` with a fresh `newSecret()`. That way a throw during minting or asserting never leaves the shell bound to a live secret, while a successful mint leaves the binding in place for step 50 to use.

### Step 190 — retire the caller

```javascript
(function(outputs, steps, params, stepResult, assertEqual) {
    var SHELL    = 'BST ATF REST caller';
    var callerId = String(steps('30').caller_id);
    var retired  = false;

    function setIfPresent(gr, names, value) {
        var i = 0;
        for (i = 0; i < names.length; i++) {
            if (gr.isValidField(names[i])) { gr.setValue(names[i], value); return names[i]; }
        }
        return '';
    }
    function newSecret() {
        return GlideSecureRandomUtil.getSecureRandomString(40) + 'aA1!';
    }
    function retireShell() {
        var shell = new GlideRecord('sys_auth_profile_basic');
        if (!shell.get('name', SHELL)) {
            return false;
        }
        setIfPresent(shell, ['user_name', 'username'], 'bst.atf.retired');
        shell.setValue('password', newSecret());
        return shell.update() ? true : false;
    }

    try {
        // 1. Return the shell to an unusable state, with a fresh secret nobody holds.
        retired = retireShell();
        assertEqual({ name: 'shell retired', shouldbe: true, value: retired });

        // 2. Remove the role grant, then the account. Both keyed on the prefix as well
        //    as on the step output, so a lost output cannot strand an account.
        var grants = new GlideRecord('sys_user_has_role');
        grants.addQuery('user', callerId);
        grants.deleteMultiple();
        var user = new GlideRecord('sys_user');
        if (user.get(callerId)) { user.deleteRecord(); }

        var others = new GlideRecord('sys_user');
        others.addQuery('user_name', 'STARTSWITH', 'bst.atf.rest.');
        others.query();
        while (others.next()) {
            var otherGrants = new GlideRecord('sys_user_has_role');
            otherGrants.addQuery('user', others.getUniqueValue());
            otherGrants.deleteMultiple();
            others.deleteRecord();
        }

        // 3. Assert nothing usable is left behind.
        var gone = new GlideRecord('sys_user');
        assertEqual({ name: 'disposable caller removed',
            shouldbe: false, value: gone.get(callerId) });
        var residue = new GlideRecord('sys_user');
        residue.addQuery('user_name', 'STARTSWITH', 'bst.atf.rest.');
        residue.query();
        assertEqual({ name: 'no disposable caller of any run remains',
            shouldbe: 0, value: residue.getRowCount() });
        var orphan = new GlideRecord('sys_user');
        orphan.addQuery('user_name', 'bst.atf.retired');
        orphan.query();
        assertEqual({ name: 'the shell no longer names a live account',
            shouldbe: 0, value: orphan.getRowCount() });

        var check = new GlideRecord('sys_auth_profile_basic');
        var bound = check.get('name', SHELL)
            ? String(check.getValue('user_name') || check.getValue('username') || '')
            : '';
        assertEqual({ name: 'the shell user name reads bst.atf.retired',
            shouldbe: 'bst.atf.retired', value: bound });
    } finally {
        // Guaranteed: whatever failed above, the shell does not stay bound to a live
        // secret. Re-running the retirement is harmless and idempotent.
        if (!retired) {
            retired = retireShell();
        }
        stepResult.setOutputMessage('Caller ' + callerId +
            ' deleted; shell returned to bst.atf.retired with a discarded secret' +
            ' (retired=' + retired + ').');
    }
    return true;
})(outputs, steps, params, stepResult, assertEqual);
```

The framework rollback would remove the account anyway. **The retirement does not depend on rollback and does not depend on this step being reached**, because the shell's `user_name` and `password` are an *update* to a persistent record: the `finally` above covers a throw inside this step, and step 30's unconditional sweep covers a test that never reached this step at all.

### Post-suite residue queries

Run these four after suite 9 and suite 10, every time, and record the result. **The coverage gate reads them**, and a non-zero row count or an unexpected property state blocks it. They are the detection half of the convergence design above; mechanisms 1 and 2 make residue unlikely, and these make it impossible to miss.

| # | Query | Expected |
| --- | --- | --- |
| R1 | `sys_user` where `user_name` **starts with** `bst.atf.rest.` | **0 records.** Any row is a live disposable caller. Delete it and its `sys_user_has_role` rows by hand, then investigate which test failed before its step 190. |
| R2 | `sys_auth_profile_basic` where `name` **is** `BST ATF REST caller` | **1 record**, whose user name reads `bst.atf.retired`. Any other value means the shell is still bound to an account name a test minted. |
| R3 | `sys_user` where `first_name` **is** `BST ATF` | **0 records.** These are suite 8's impersonation users, created by the stock **Create a User** step with a generated user name and no password; see [Technique (a)](#technique-a--impersonation). A survivor holds a scoped role, so delete it and its `sys_user_has_role` rows by hand. |
| R4 | `sys_properties` where `name` **is** `x_bst_startuptrk.ingestion.last_run_provenance` | A value carrying **no `running` state** for either source, and `x_bst_startuptrk.ingestion.source_mode` still reading `fallback`. Record the value verbatim; the flow tests' step 160 output message states what it should be. |

Record all four in [Evidence to record](#evidence-to-record).

### Rotation

There is no rotation schedule to keep, because **every run rotates the credential**: step 30 mints a new user name and a new secret, and step 190 replaces the secret with another one nobody holds. The residual exposure is a single 32-character password that is live only while its own test is running and is never recorded. Nothing in this guide, in the delivered Update Set, or in any other document names a password value.


## Technique (c) — the deterministic 429

The rate-limit assertion is made deterministic by **owning the counter tuple for the duration of the test**: the test deletes every row for its `caller` + `api_resource` + current-window triple, asserts none remains, asserts the ordinary increment from that known baseline, then seeds **exactly one** row already at the configured budget so the very next call trips the limit in a **single request**, and finally deletes what it created. No loop of a hundred calls is needed and no test depends on timing out a real budget. The mechanic is stated here; the decision is recorded in [`../../../docs/decisions/DECISION_LOG.md`](../../../docs/decisions/DECISION_LOG.md).

### Own the tuple; do not merely write to it

**The triple `caller` + `api_resource` + `window_start` carries no uniqueness constraint**, and `x_bst_startuptrk_rate_limit_counter` has no key column. `RateLimitService` finds its row by querying that triple with a limit of one, and inserts a fresh row at `1` when the query returns nothing. **A test that only writes to the tuple therefore fails in two ways, both of them quiet:**

| Situation | What a write-only test does | What actually happens |
| --- | --- | --- |
| **Several rows already share the tuple** — from a previous run, or from two concurrent inserts the design accepts | Updates one arbitrary row to the budget | The limiter's own query has a limit of one and may select a **different** row, whose count is low. The request returns `200` where `429` was asserted. |
| **A row from a previous run is at some middling count** | Seeds the budget and expects the next call to trip | It does trip, but the increment assertions before it were measured against a baseline the test did not establish, so a broken increment would pass unnoticed |

**Build the four ownership steps below instead.** They are what make both the `200` assertions and the `429` assertion depend only on state the test created. `D-067` carries the decision.

| Step | Action | Assertion |
| --: | --- | --- |
| 25 | **Delete every row for the tuple** | **Exactly 0** rows remain for the triple |
| 75 and 105 | After the first ordinary call, then after the second | **Exactly 1** row exists both times, reading **exactly 1** and then **exactly 2** |
| 130 | **Delete every row again, then insert exactly one at the budget** | **Exactly 1** row exists and it reads exactly the budget |
| 170 | After the `429` assertions, **delete every row for the tuple** | **Exactly 0** rows remain, so the tuple is left as it was found |

### Where the budget and window come from

| Property | Delivered value | Role |
| --- | --- | --- |
| `x_bst_startuptrk.rest.rate_limit_requests` | `100` | The budget. Seed `request_count` to exactly this value. |
| `x_bst_startuptrk.rest.rate_limit_window_seconds` | `60` | The fixed window length in seconds. Determines the window boundary the seeded row must fall on. |

Read both through `AppProperties` rather than hard-coding them, so a tuned instance does not silently break the test.

### The four columns, and which caller they name

| Column | Value |
| --- | --- |
| `caller` | The `sys_id` of **the REST caller** — the user the inbound REST request authenticates as, **not** the impersonated user. On [Construction A](#construction-a--an-ephemeral-identity-created-and-rolled-back-inside-the-test-preferred) that is step 1's `caller_sys_id` output; on [Construction B](#construction-b--a-persistent-identity-hardened-fallback-only) it is the `sys_id` of `bst.rest.caller`. `Send REST Request - Inbound` establishes its own session, so an earlier `Impersonate` step has no bearing on which caller the limiter accounts against. Seeding the wrong caller is the single most common reason this assertion fails to trip. |
| `api_resource` | The exact token for the resource under test, from the table in [suite 9](#suite-9--bst-rest-suite--resources). Seven tokens exist; the nested executives sub-resource has its own. |
| `window_start` | The **current window boundary**: the current epoch second floored to a multiple of the window length. Not "now". |
| `request_count` | The budget itself — `100` by default. The service rejects when the incremented count is **strictly greater than** the budget, so a row seeded at `100` becomes `101` on the next call and trips; a row seeded at `99` becomes `100` and does **not** trip. |

### The shared helper every counter step declares

All five counter steps — 25, 75, 105, 130 and 170 — open with the same block. **Paste it verbatim at the top of each of the five scripts**, above the step-specific code shown below: it is declared identically in each, per Contract 2 mechanism 2, because a `Run Server Side Script` step cannot hand a function to another step. Where a script below reads `// [ the shared helper block goes here ]`, that line is replaced by the whole block.

```javascript
    // ---- per-test substitution, identical in steps 25, 75, 130 and 170 ----
    var API_RESOURCE = '/startups';        // one of the seven tokens
    // ---- end of per-test substitution ----

    var COUNTER = 'x_bst_startuptrk_rate_limit_counter';
    var props = new AppProperties();
    var budget = props.getRateLimitRequests();
    var windowSeconds = props.getRateLimitWindowSeconds();

    // Construction A: read the ephemeral caller from step 1's output.
    // Construction B: set CALLER_USER_NAME to 'bst.rest.caller' and use the lookup.
    var CALLER_USER_NAME = steps('1') ? steps('1').caller_user_name : 'bst.rest.caller';

    var caller = new GlideRecord('sys_user');
    if (!caller.get('user_name', CALLER_USER_NAME)) {
        stepResult.setFailed('REST caller ' + CALLER_USER_NAME
            + ' not found. See "The REST caller and its Basic Auth Configuration".');
        return false;
    }
    var callerId = caller.getUniqueValue();

    // The window boundary the service will compute, not "now".
    function boundary() {
        var seconds = Math.floor(new GlideDateTime().getNumericValue() / 1000);
        var bucket = seconds - (seconds % windowSeconds);
        var start = new GlideDateTime();
        start.setNumericValue(bucket * 1000);
        return { start: start, remaining: (bucket + windowSeconds) - seconds };
    }
    function rowsForTuple(windowStart) {
        var found = [];
        var gr = new GlideRecord(COUNTER);
        gr.addQuery('caller', callerId);
        gr.addQuery('api_resource', API_RESOURCE);
        gr.addQuery('window_start', windowStart.getValue());
        gr.query();
        while (gr.next()) {
            found.push({ sys_id: gr.getUniqueValue(),
                count: parseInt(gr.getValue('request_count'), 10) });
        }
        return found;
    }
    function deleteTuple(windowStart) {
        var gr = new GlideRecord(COUNTER);
        gr.addQuery('caller', callerId);
        gr.addQuery('api_resource', API_RESOURCE);
        gr.addQuery('window_start', windowStart.getValue());
        gr.deleteMultiple();
    }
```

### Step 25 — take ownership and establish the baseline

```javascript
(function(outputs, steps, params, stepResult, assertEqual) {
    // [ the shared helper block goes here ]

    var window = boundary();

    // Wait out a window that is about to roll, so steps 30 to 80 and step 140 all land in
    // the same window as this baseline. See operational warning W5.
    if (window.remaining < 20) {
        gs.sleep(window.remaining * 1000 + 500);
        window = boundary();
    }

    // Take the tuple. Every row, not one row.
    deleteTuple(window.start);
    var remaining = rowsForTuple(window.start);
    assertEqual({ name: 'the tuple is owned by this test: zero rows remain',
        shouldbe: 0, value: remaining.length });

    stepResult.setOutputMessage('Counter baseline established for ' + API_RESOURCE +
        ' at window_start=' + window.start.getDisplayValue() + ': 0 rows, budget=' + budget +
        ', window=' + windowSeconds + 's, ' + window.remaining + 's remaining.');
    return true;
})(outputs, steps, params, stepResult, assertEqual);
```

### Step 75 — assert the ordinary increment from that baseline

**This is the step that makes the `429` assertion meaningful rather than circular.** The threshold branch is exercised against a hand-seeded row, so on its own it would still pass if the increment logic were broken while the comparison was correct. This step closes that gap by asserting the transition the ordinary calls caused, from a baseline the test itself established.

Place it after the calls whose increments it counts, and use it **twice**: at display order 75 with `EXPECTED_CALLS` `1`, after the single call of step 30, and again at display order 105 with `EXPECTED_CALLS` `2`, after the second call of step 80. The pair asserts the transition **0 to 1 to 2**, which is what a broken increment cannot produce.

```javascript
(function(outputs, steps, params, stepResult, assertEqual) {
    // [ the shared helper block goes here ]

    var EXPECTED_CALLS = 2;      // inbound calls made against this token since step 25

    var window = boundary();
    var rows = rowsForTuple(window.start);

    // Exactly one row: the limiter must find and increment its row rather than insert a
    // second one for the same tuple.
    assertEqual({ name: 'the ordinary calls produced exactly one counter row',
        shouldbe: 1, value: rows.length });
    assertEqual({ name: 'request_count equals the ' + EXPECTED_CALLS + ' calls made',
        shouldbe: EXPECTED_CALLS, value: rows.length === 1 ? rows[0].count : -1 });

    // The count is well below the budget, so those calls returned 200 for the right reason.
    assertEqual({ name: 'the count is below the budget, as the 200 responses imply',
        shouldbe: true, value: rows.length === 1 && rows[0].count <= budget });

    stepResult.setOutputMessage('Increment asserted: ' + EXPECTED_CALLS + ' call(s) since a ' +
        'zero baseline produced 1 row reading ' + (rows.length === 1 ? rows[0].count : 'n/a') +
        ' of a ' + budget + ' budget.');
    return true;
})(outputs, steps, params, stepResult, assertEqual);
```

### Step 130 — seed exactly one row at the budget

```javascript
(function(outputs, steps, params, stepResult, assertEqual) {
    // [ the shared helper block goes here ]

    var window = boundary();

    // Guard the boundary again: the seed and the request of step 140 must share a window.
    if (window.remaining < 10) {
        gs.sleep(window.remaining * 1000 + 500);
        window = boundary();
    }

    // Clear the tuple completely, INCLUDING the row the ordinary calls created, so exactly
    // one row exists and the limiter cannot select a different one.
    deleteTuple(window.start);
    assertEqual({ name: 'the tuple is empty before the seed',
        shouldbe: 0, value: rowsForTuple(window.start).length });

    var seed = new GlideRecord(COUNTER);
    seed.initialize();
    seed.setValue('caller', callerId);
    seed.setValue('api_resource', API_RESOURCE);
    seed.setValue('window_start', window.start.getValue());
    seed.setValue('request_count', budget);      // the next call makes it budget + 1
    var seededId = seed.insert();
    assertEqual({ name: 'the at-budget row was inserted', shouldbe: true, value: !!seededId });

    // The state the next request will meet: exactly one row, reading exactly the budget.
    var rows = rowsForTuple(window.start);
    assertEqual({ name: 'exactly one row exists for the tuple', shouldbe: 1, value: rows.length });
    assertEqual({ name: 'that row reads exactly the budget',
        shouldbe: budget, value: rows.length === 1 ? rows[0].count : -1 });
    assertEqual({ name: 'the row the limiter will find is the row this step seeded',
        shouldbe: seededId, value: rows.length === 1 ? rows[0].sys_id : '' });

    // Contract 2: the seeded row's identifier travels to step 170 through the stock outputs.
    outputs.record_id = seededId;
    outputs.table = COUNTER;

    stepResult.setOutputMessage('Seeded exactly 1 row for ' + API_RESOURCE + ' at ' +
        'request_count=' + budget + ', window_start=' + window.start.getDisplayValue() +
        ', ' + window.remaining + 's remaining. The next call trips the limit.');
    return true;
})(outputs, steps, params, stepResult, assertEqual);
```

### The assertions on the response, and the cleanup

| Assertion | Step | Detail |
| --- | --- | --- |
| Status | **Assert Status Code**, `response_operation` **is**, `status_code` `429` | Not 415 and not 403. The rate limiter runs **first** in every operation, ahead of the in-script role guard, the media-type guard and all parameter validation, so a caller over budget reads 429 rather than any other refusal. |
| Error member | **Assert JSON Response Payload Element**, `element_name` `error`, `response_operation` **is**, `element_value` `rate_limit_exceeded` | The exact string. |
| Retry member | **Run Server Side Script** at 170 | `retry_after` is present and is a **positive integer**. |
| Body shape | Same script step | The body carries **exactly** the two members `error` and `retry_after` and nothing else. |
| Counter state | Same script step | The seeded row was incremented past the budget, and then **every row for the tuple is deleted**, so the test leaves the counter as it found it. |

```javascript
(function(outputs, steps, params, stepResult, assertEqual) {
    // [ the shared helper block goes here ]

    var STEP_140_OVER_BUDGET = '';   // <- the Send REST Request step at display order 140
    var STEP_130_SEED = '';          // <- the seeding step at display order 130

    var body = JSON.parse(steps(STEP_140_OVER_BUDGET).response_body);

    assertEqual({ name: 'error is rate_limit_exceeded',
        shouldbe: 'rate_limit_exceeded', value: body.error });

    var retry = body.retry_after;
    assertEqual({ name: 'retry_after is present',
        shouldbe: true, value: Object.prototype.hasOwnProperty.call(body, 'retry_after') });
    assertEqual({ name: 'retry_after is an integer',
        shouldbe: true, value: typeof retry === 'number' && retry === Math.floor(retry) });
    assertEqual({ name: 'retry_after is positive', shouldbe: true, value: retry > 0 });
    assertEqual({ name: 'retry_after is no longer than the window',
        shouldbe: true, value: retry <= windowSeconds });

    // Exactly two members, no more.
    assertEqual({ name: 'body carries exactly error and retry_after',
        shouldbe: 'error,retry_after', value: Object.keys(body).sort().join(',') });

    // The row the limiter incremented is the row step 130 seeded, and it went past the budget.
    var window = boundary();
    var rows = rowsForTuple(window.start);
    assertEqual({ name: 'still exactly one row for the tuple', shouldbe: 1, value: rows.length });
    assertEqual({ name: 'the incremented row is the seeded row',
        shouldbe: String(steps(STEP_130_SEED).record_id),
        value: rows.length === 1 ? rows[0].sys_id : '' });
    assertEqual({ name: 'the count is strictly greater than the budget, which is why it tripped',
        shouldbe: budget + 1, value: rows.length === 1 ? rows[0].count : -1 });

    // Leave the tuple as it was found. ATF rolls back records a test creates, but this row
    // was inserted by an inbound REST request in its own session, so it is deleted here.
    deleteTuple(window.start);
    assertEqual({ name: 'the tuple is empty again after cleanup',
        shouldbe: 0, value: rowsForTuple(window.start).length });

    stepResult.setOutputMessage('429 contract satisfied for ' + API_RESOURCE +
        '; retry_after=' + retry + 's; seeded row reached ' + (budget + 1) +
        '; counter tuple cleaned to 0 rows.');
    return true;
})(outputs, steps, params, stepResult, assertEqual);
```

`retry_after` is always at least `1`, because the service floors the remaining window at one second, and never more than the window length. An assertion of "greater than zero and no greater than the window" therefore holds for every window position, including a request that arrives in the final fraction of a second of a window.

**The cleanup at step 170 is not optional.** Steps 30, 80, 110 and 140 are inbound HTTP requests in their own sessions, so the counter rows they cause are **not** part of the test's transaction and the framework does not roll them back. Without the delete, the next run of the same test in the same window meets a populated tuple, and step 25's baseline assertion is what would catch it — one run later than the run that caused it.

### Why two rows, and no sleep

The window is a **fixed** window: the service floors the current epoch second to a multiple of the window length and accounts against that bucket. A test that seeds only the current bucket has a race it cannot close — the boundary can roll between the seeding step and the REST request, and the request then lands in an empty bucket and returns `200` instead of `429`.

An earlier build tried to close it by measuring the remaining time and calling `gs.sleep()` when the boundary was near. That is wrong twice over.

| Problem | Why it matters |
| --- | --- |
| `gs.sleep()` blocks the whole transaction | On a sixty-second window it can block for up to ten seconds by design, and the ATF runner holds the transaction open throughout. A blocking wait inside a test step is a reliability hazard on a shared instance and makes the suite's duration depend on when it happened to start. |
| It does not actually close the race | Sleeping moves the request to the *start* of the next window, which is safer, but the check-then-sleep-then-seed sequence still reads the clock three times. Any of the three can straddle a boundary, so the window the row is seeded in and the window the request lands in are still only probably the same. |

**Seeding two rows removes the race instead of narrowing it.** One row sits on the current boundary and one on the next, both at the budget, so whichever bucket the inbound request resolves to is already full. There is no clock reading to get wrong, no wait, and no dependence on where in the window the suite happens to start. Both rows are inserts, so the framework rollback removes them, and step 150's sweep removes them again by `window_key`.

The counter table's `window_key` column is **unique**, so seeding the same two boundaries twice within one window would collide. The script therefore uses `RateLimitService.windowKey()` — the same computation the service performs — and updates a row that already exists rather than inserting a duplicate.


## Technique (d) — starting the flow under test

**There is no stock ATF step configuration that starts a Flow Designer flow**, and this guide creates none. Both flow tests start their flow from a **Run Server Side Script** step using the platform's Flow API, then assert against the execution that produced.

### The two calls, and why only one of them is usable

| Call | What it does | Usable in a test? |
| --- | --- | --- |
| `sn_fd.FlowAPI.getRunner().flow('<scope>.<internal_name>').withInputs({}).inForeground().run()` | Runs the flow **synchronously** in the calling transaction and returns a result object once its last action has completed. | **Yes. Use this.** The execution finishes before the next step runs, so the assertions have something to read, and the flow's writes are inside the test's transaction. |
| `…​.inBackground().run()` | Queues the flow to run **asynchronously** in a separate transaction. | **No.** The next step runs before the flow has done anything, every assertion reads an empty result, and the flow's writes land outside the test's rollback and stay on the instance. See [W9](#operational-warnings). |

**`.run()` is the terminal call, and omitting it is a silent no-op.** `getRunner()`, `.flow()`, `.withInputs()` and `.inForeground()` are all **builder** methods: each returns the builder so the next one can be chained. Nothing executes until `.run()` is called, and `.run()` is what returns the result object. Two consequences follow, and the second is what makes the omission dangerous rather than merely wrong.

| The mistake | What happens |
| --- | --- |
| Ending the chain at `.inForeground()` | **No flow runs at all.** The builder is constructed and discarded. |
| Calling `getContextId()` on the builder | The builder carries no context, because no execution exists. Depending on the release it throws or answers an empty value — and a test that treats an empty value as "no context yet" then reports a passing flow test against a flow that never started. |

The chain must therefore end `…​.inForeground().run()`, and `getContextId()` must be called on **the object `.run()` returned**, never on the builder. The start script below asserts the returned object is present and that the identifier it yields is a real thirty-two-character record identifier, so neither mistake can pass.

**The flow is named by its `internal_name`, not by its display label.** The runner resolves `<scope>.<internal_name>`, and the internal name is the display label lower-cased with spaces replaced by underscores. For these two flows that is:

| Flow record — **Name** | Flow record — **Internal name** | The string to pass to `.flow()` |
| --- | --- | --- |
| `Crunchbase Ingestion` | `crunchbase_ingestion` | `x_bst_startuptrk.crunchbase_ingestion` |
| `LinkedIn Ingestion` | `linkedin_ingestion` | `x_bst_startuptrk.linkedin_ingestion` |

**Read the internal name off the record rather than deriving it by hand.** Open the flow in Flow Designer, use the **Flow properties** panel, and copy the internal name exactly; the derivation rule above is the platform's, but a flow renamed after creation keeps its original internal name, so the two can legitimately differ. The start script resolves it from `sys_hub_flow` and asserts exactly one match, so a wrong string fails the step with a message that names the problem instead of reporting an empty result. Both flows must be **Published** and **Active** — precondition 6.

**A scheduled trigger does not prevent a flow being started on demand.** The trigger decides when the platform starts the flow by itself; it places no restriction on starting it from a script. The two flows also carry **Run As: System User**, so the started execution has system privilege regardless of who started it — which is why [this suite does not impersonate](#this-suite-does-not-impersonate).

### The start script

Use this at step 40 and again at step 60, with the marker value each of those steps requires.

```javascript
(function(outputs, steps, params, stepResult, assertEqual) {
    var INTERNAL = 'crunchbase_ingestion';   // or 'linkedin_ingestion'
    var SOURCE   = 'crunchbase';             // or 'linkedin'
    var MODE     = 'noop';                   // 'noop' at step 40, 'run' at step 60
    var ID32     = /^[0-9a-f]{32}$/;

    var props = new AppProperties();
    var cadence = props.getCadenceHours();

    // 1. Resolve the flow by internal name and assert exactly one match. A wrong
    //    string fails this step.
    var flow = new GlideRecord('sys_hub_flow');
    flow.addQuery('internal_name', INTERNAL);
    flow.addQuery('sys_scope.scope', 'x_bst_startuptrk');
    flow.query();
    assertEqual({ name: 'the flow resolves to exactly one record',
        shouldbe: 1, value: flow.getRowCount() });
    if (!flow.next()) {
        stepResult.setFailed('No sys_hub_flow named ' + INTERNAL +
            ' in x_bst_startuptrk. Check the internal name on the flow record.');
        return false;
    }
    assertEqual({ name: 'the flow is active', shouldbe: true, value: flow.active == true });

    // 2. Position this source's cadence marker so the guard must take the branch under
    //    test. The marker lives inside the single run-state property as one entry per
    //    source, in the form source=provenance|state|stamp|run. completeRun always
    //    stamps the current time, so a back-dated stamp is composed here and written
    //    directly, preserving whatever entry the other source holds.
    var stamp = new GlideDateTime();
    if (MODE === 'run') {
        stamp.addSeconds(-1 * (cadence + 1) * 3600);
    }
    var markers = props.readRunMarkers();
    var entries = [];
    var order = ['crunchbase', 'linkedin'];
    var i = 0;
    for (i = 0; i < order.length; i++) {
        if (order[i] === SOURCE) {
            entries.push(SOURCE + '=fallback|succeeded|' + stamp.getValue() +
                '|' + SOURCE + '-atf');
        } else if (markers[order[i]]) {
            var other = markers[order[i]];
            entries.push(order[i] + '=' + other.provenance + '|' + other.state +
                '|' + other.stamp + '|' + other.run);
        }
    }
    gs.setProperty('x_bst_startuptrk.ingestion.last_run_provenance', entries.join(';'));
    assertEqual({ name: 'cadence marker positioned',
        shouldbe: stamp.getValue(), value: props.getLastSuccessAt(SOURCE) });

    // 3. Start the flow. .run() is the terminal call; getContextId() belongs to what
    //    it returns. Neither may be omitted. See the two calls above.
    var result = sn_fd.FlowAPI.getRunner()
        .flow('x_bst_startuptrk.' + INTERNAL)
        .withInputs({})
        .inForeground()
        .run();

    assertEqual({ name: 'run() returned a result object',
        shouldbe: true, value: result !== null && result !== undefined });
    if (!result) {
        stepResult.setFailed('The runner returned nothing. The chain must end in .run().');
        return false;
    }

    var contextId = String(result.getContextId() || '');
    assertEqual({ name: 'the result carries a 32-character context identifier',
        shouldbe: true, value: ID32.test(contextId) });
    if (!ID32.test(contextId)) {
        stepResult.setFailed('getContextId() answered "' + contextId +
            '". That is the builder answering, not a result: the chain is missing .run().');
        return false;
    }

    // 4. The context must be a readable record that reached a non-error state.
    var context = new GlideRecord('sys_flow_context');
    var found = context.get(contextId);
    assertEqual({ name: 'the execution context is readable', shouldbe: true, value: found });
    var state = found ? String(context.getValue('state')) : '';
    assertEqual({ name: 'the execution did not error',
        shouldbe: true, value: state !== 'ERROR' && state !== 'CANCELLED' });

    outputs[MODE === 'run' ? 'run_context' : 'noop_context'] = contextId;
    outputs.cadence_hours = cadence;
    outputs.marker_written = stamp.getValue();
    outputs.flow_internal_name = INTERNAL;
    stepResult.setOutputMessage('Started x_bst_startuptrk.' + INTERNAL + ' (' + MODE +
        '); context=' + contextId + ' state=' + state + '; cadence=' + cadence +
        'h; marker=' + stamp.getValue());
    return true;
})(outputs, steps, params, stepResult, assertEqual);
```

`withInputs({})` is passed explicitly and empty because a scheduled flow declares no trigger inputs. **Do not invent inputs for it**; the flow reads its configuration from the properties of [The control state](#the-control-state-each-test-borrows-and-what-it-can-and-cannot-return).

**The context identifier is asserted against a thirty-two-character lower-case hexadecimal pattern, not merely against emptiness.** That is the assertion that distinguishes a real execution from the builder answering, and it is why an omitted `.run()` now fails the step with a message naming the cause rather than passing with a hollow result.

### If the Flow API is unavailable

`sn_fd.FlowAPI` is generally available from the release floor this application requires, so an unavailability is a misconfiguration rather than a version gap. If the call fails to resolve, the test **fails** — it does not fall back to calling `IngestionMapper` directly, because that would report success against an unexercised flow. Record the failure and resolve it before reading any other result in the run; the coverage gate treats an unrunnable flow test the same way it treats a missing one.


## Technique (e) — provenance labelling

Each flow test's setup step **derives** the provenance from the state the run will actually take, **labels** the result accordingly, and **writes no run summary of its own**. The only run summary either test asserts is the one the ingestion itself wrote. The mechanic is stated here; the decision is recorded in [`../../../docs/decisions/DECISION_LOG.md`](../../../docs/decisions/DECISION_LOG.md).

### The setup step must not write a run summary

**Do not call `IngestionLogger.writeRunSummary()` from a setup step.** It is not an inert label: it validates the mode, emits a `run_summary` event that a later assertion will read, emits the `run_summary` event, and returns `{provenance, recorded, processed, rejected, skipped, duplicates, unmatched}`. Calling it from setup does three harmful things at once, and the first is silent:

| Harm | Consequence |
| --- | --- |
| It writes a summary carrying **all-zero counters**, before any ingestion has run | An assertion that later reads "the run summary" can find the setup's zeroed one and pass against it. The test reports a successful ingestion of nothing. |
| It sets the provenance property from the **test's assumption** rather than from the run | The label stops being evidence. It says what the author expected, not what happened. |
| It emits a `run_summary` event that a log-reading assertion cannot distinguish from the real one | Two summaries per run, one meaningless. |

**The setup step therefore derives and labels only**, and every summary assertion in the test binds to `outcome.summary` — the object `ingest()` returned at step 40, which `writeRunSummary()` produced **after** the batch was processed. That is the sole summary surface these tests assert. `D-066` carries the decision.

### The label and the run summary are two different evidence surfaces

**ATF rolls back the data a test creates.** A provenance row or a property value written **inside** a test therefore does **not** survive the run: the property write `ingest()` performs at step 40 is real for the duration of the test and gone afterwards, so it cannot serve as the durable evidence success criterion 4 reads. The label on the test result carries that meaning instead.

The two surfaces are distinct and must not be conflated:

| Surface | Written by | Survives the run? | Read by |
| --- | --- | --- | --- |
| **Scheduled-run provenance** | The final phase of the orchestrator action A4, on a real scheduled execution — the per-flow entry it writes into `x_bst_startuptrk.ingestion.last_run_provenance`, mirrored into the run-summary log record | **Yes.** It is written outside any test transaction. | [`../validation-checklist.md`](../validation-checklist.md), success criterion 4 |
| **ATF result label** | The step 20 setup step in this guide, labelling the result `fallback validated` or `live validated`, plus the mode suffix on the test name | **No.** ATF rolls back the data a test creates, so the summary `ingest()` writes inside a test does not persist. | The test report, and this guide's evidence record |

This table is stated identically in [`02-flow-crunchbase-ingestion.md`](02-flow-crunchbase-ingestion.md) and [`03-flow-linkedin-ingestion.md`](03-flow-linkedin-ingestion.md). The three documents must agree.

**Non-durable is not the same as harmless.** `markRunComplete(runId, provenance, sourceSystem)` calls `AppProperties.completeRun()`, which turns this source's entry in the single property `x_bst_startuptrk.ingestion.last_run_provenance` into a `succeeded` marker — and that marker's stamp is the value the flow's cadence guard compares against. `writeRunSummary()` takes the same three arguments, emits the `run_summary` event and writes **no** property at all. A flow test that consumed staging rows and left that property stamped would turn the next real execution into a no-op for a full cadence window, so the three consecutive guard-passing runs criterion 4 requires would never begin. Rollback is not the answer: ATF reverts records a test creates, whereas a property is a pre-existing record the test updates, and the property cache is a separate concern from the record. Steps 15 and 95 capture and restore that property explicitly, step 15 aborts the test if a previous run left it unrestored, and the guide publishes an out-of-band restoration for the abort case — all three under [Protecting the cadence state](#the-fixture-step). **Do not build a flow test without them.**

### The setup step

Three jobs, in order: mint a token unique to **this execution**, derive the provenance from the **actual** state the run will take, and park both on a record the test creates so every later step reads the same pair.

**The token must be unique per execution, not a fixed string.** A fixed `atf-crunchbase-001` collides with itself: the staging rows of one execution are indistinguishable from the previous one's in any query that survives a partial rollback, the log events of two runs share a run identifier, and two tests running in the same window cannot be told apart. The token is therefore derived from the current time in milliseconds and the test's own execution identifier.

**The provenance must be derived, not declared.** It is read from `AppProperties.getSourceMode()` and from whether the alias the flow uses actually carries a credential. On this instance both aliases are in Branch A, so both derivations resolve to `fallback` — but the test asserts the derivation rather than assuming its result, so the same script tells the truth on an instance where a live credential has since been provisioned.

```javascript
(function(outputs, steps, params, stepResult, assertEqual) {
    // ---- per-test substitution ----
    var SOURCE = 'crunchbase';                             // or 'linkedin'
    var ALIAS = 'x_bst_startuptrk.crunchbase_api';         // or x_bst_startuptrk.linkedin_oauth
    // ---- end of per-test substitution ----

    // 1. A token unique to THIS execution. A fixed token collides with earlier runs of the
    //    same test and with a concurrent run of the other one.
    var stamp = new GlideDateTime().getNumericValue();
    var T = 'atf-' + SOURCE + '-' + stamp + '-' +
        Math.floor(Math.random() * 100000);

    // 2. Derive the provenance from the state the run will ACTUALLY take, rather than
    //    declaring it. Two independent inputs must agree before 'live' is claimed:
    //    the source-mode property, and whether the alias carries a usable credential.
    var props = new AppProperties();
    var declaredMode = String(props.getSourceMode() || '').toLowerCase();
    assertEqual({ name: 'the source-mode property holds a permitted value', shouldbe: true,
        value: declaredMode === 'live' || declaredMode === 'fallback' });

    var aliasHasCredential = false;
    var alias = new GlideRecord('sys_alias');
    alias.addQuery('name', ALIAS);
    alias.query();
    var aliasExists = alias.next();
    if (aliasExists) {
        var conn = new GlideRecord('sys_connection');
        conn.addQuery('connection_alias', String(alias.getUniqueValue()));
        conn.addQuery('active', true);
        conn.query();
        while (conn.next()) {
            if (String(conn.getValue('credential') || '') !== '') {
                aliasHasCredential = true;
            }
        }
    }

    var PROVENANCE = (declaredMode === 'live' && aliasHasCredential) ? 'live' : 'fallback';

    // writeRunSummary accepts ONLY these two values; any other logs
    // run_summary_provenance_invalid and writes nothing. The derivation cannot produce a third.
    assertEqual({ name: 'the derived provenance is a permitted value', shouldbe: true,
        value: PROVENANCE === 'live' || PROVENANCE === 'fallback' });

    // On an instance whose alias is unprovisioned, 'live' is not reachable. Assert the
    // derivation rather than the expected answer, so this holds either way.
    assertEqual({ name: 'live is claimed only when the alias carries a credential',
        shouldbe: true, value: PROVENANCE === 'fallback' || aliasHasCredential });

    // 3. Park the pair on a record THIS test creates. Contract 2, mechanism 3: this is the
    //    only way a run-time-computed value reaches a later script step. The row is written
    //    to the staging table in a terminal state, so the ingestion's pending-only query
    //    can never read it as input.
    var parked = new GlideRecord('x_bst_startuptrk_ingest_staging');
    parked.initialize();
    parked.setValue('source_system', SOURCE);
    parked.setValue('record_type', 'startup');
    parked.setValue('import_state', 'rejected');
    parked.setValue('error_message', 'ATF run token record; not ingestion input.');
    parked.setValue('run_provenance', PROVENANCE);
    parked.setValue('import_run', T + '-token');
    parked.setValue('raw_payload', new global.JSON().encode({
        token: T, provenance: PROVENANCE, source: SOURCE,
        declared_mode: declaredMode, alias: ALIAS,
        alias_exists: aliasExists, alias_has_credential: aliasHasCredential
    }));
    var parkedId = parked.insert();
    assertEqual({ name: 'the run-token record was created', shouldbe: true, value: !!parkedId });

    // The two stock outputs of a Run Server Side Script step, and the only two it has.
    outputs.record_id = parkedId;
    outputs.table = 'x_bst_startuptrk_ingest_staging';

    // No run summary is written here. The only summary this test asserts is the one
    // ingest() writes at step 40, after the batch has been processed.
    var LABEL = PROVENANCE === 'live' ? 'live validated' : 'fallback validated';
    stepResult.setOutputMessage('RESULT LABEL: ' + LABEL + ' | run_id=' + T +
        ' | provenance=' + PROVENANCE + ' (derived: source_mode=' + declaredMode +
        ', alias_exists=' + aliasExists + ', alias_has_credential=' + aliasHasCredential +
        ') | no run summary written by setup');
    return true;
})(outputs, steps, params, stepResult, assertEqual);
```

### The summary assertion at step 100

The only summary asserted, and it is the one the ingestion wrote. Its provenance must equal the derived value, its `processed` must equal the accepted count, and the property it set must carry the same mode **while the test is still running**.

```javascript
(function(outputs, steps, params, stepResult, assertEqual) {
    // ---- per-test substitution ----
    var SOURCE = 'crunchbase';          // or 'linkedin'
    var EXPECT_PROCESSED = 7;           // 7 for crunchbase, 5 for linkedin
    var EXPECT_REJECTED = 3;            // summary.rejected: 3 for both sources
    var EXPECT_DUPLICATES = 1;          // 1 for crunchbase (the case-variant row), 0 for linkedin
    var EXPECT_UNMATCHED = 3;           // 3 for crunchbase, 4 for linkedin
    var STEP_20_TOKEN = '';             // <- the run-token step at display order 20
    // ---- end of per-test substitution ----

    var tokenRow = new GlideRecord('x_bst_startuptrk_ingest_staging');
    assertEqual({ name: 'the run-token row is readable', shouldbe: true,
        value: tokenRow.get(steps(STEP_20_TOKEN).record_id) });
    var minted = new global.JSON().decode(String(tokenRow.getValue('raw_payload')));
    var T = String(minted.token);
    var DERIVED = String(minted.provenance);
    assertEqual({ name: 'step 40 parked its returned object on the token record',
        shouldbe: true, value: !!(minted.outcome && minted.outcome.summary) });

    // The ingestion is the ONLY summary writer. Its returned summary was parked by step 40,
    // and it is the object this step asserts. Re-calling the entry point here would find
    // nothing pending and produce a second, empty summary.
    var summary = minted.outcome.summary;
    assertEqual({ name: 'the parked summary carries the derived provenance ' + DERIVED,
        shouldbe: DERIVED, value: String(summary.provenance) });
    assertEqual({ name: 'the parked summary was recorded',
        shouldbe: true, value: summary.recorded === true });
    assertEqual({ name: 'the parked summary reports processed=' + EXPECT_PROCESSED,
        shouldbe: EXPECT_PROCESSED, value: summary.processed });
    assertEqual({ name: 'the parked summary reports rejected=' + EXPECT_REJECTED,
        shouldbe: EXPECT_REJECTED, value: summary.rejected });
    assertEqual({ name: 'the parked summary reports duplicates=' + EXPECT_DUPLICATES,
        shouldbe: EXPECT_DUPLICATES, value: summary.duplicates });
    assertEqual({ name: 'the parked summary reports unmatched=' + EXPECT_UNMATCHED,
        shouldbe: EXPECT_UNMATCHED, value: summary.unmatched });
    assertEqual({ name: 'the parked summary reports skipped=0',
        shouldbe: 0, value: summary.skipped });

    // The records agree with the summary, which is what makes the summary evidence rather
    // than a self-report. processed rows exclude the token row, which is rejected by design.
    var terminal = new GlideAggregate('x_bst_startuptrk_ingest_staging');
    terminal.addQuery('import_run', T);
    terminal.addQuery('import_state', 'processed');
    terminal.addAggregate('COUNT');
    terminal.query();
    var processedRows = terminal.next() ? (parseInt(terminal.getAggregate('COUNT'), 10) || 0) : 0;
    assertEqual({ name: 'exactly ' + EXPECT_PROCESSED + ' staging rows reached processed',
        shouldbe: EXPECT_PROCESSED, value: processedRows });

    var refused = new GlideAggregate('x_bst_startuptrk_ingest_staging');
    refused.addQuery('import_run', T);
    refused.addQuery('import_state', 'rejected');
    refused.addAggregate('COUNT');
    refused.query();
    var rejectedRows = refused.next() ? (parseInt(refused.getAggregate('COUNT'), 10) || 0) : 0;
    // The staging rejections are the summary's rejected count plus its duplicates count:
    // a within-batch duplicate reaches the rejected state but is counted as a duplicate.
    assertEqual({ name: 'rejected staging rows equal summary.rejected plus summary.duplicates',
        shouldbe: EXPECT_REJECTED + EXPECT_DUPLICATES, value: rejectedRows });

    // The property the ingestion set matches the derived mode, while the test still runs.
    assertEqual({ name: 'last_run_provenance carries the derived mode during the test',
        shouldbe: DERIVED, value: String(new AppProperties().getLastRunProvenance() || '') });

    // Secondary oracle: the emitted run_summary line, asserted only when the configured
    // level permits an info line. run_summary is emitted at info; choice_unmatched at warn.
    var logged = 'skipped (logging.level suppresses info)';
    if (new AppProperties().isLogLevelEnabled('info')) {
        var summaries = new GlideRecord('syslog');
        summaries.addQuery('message', 'CONTAINS', '[x_bst_startuptrk.ingestion]');
        summaries.addQuery('message', 'CONTAINS', 'run="' + T + '"');
        summaries.addQuery('message', 'CONTAINS', 'event="run_summary"');
        summaries.query();
        assertEqual({ name: 'the ingestion emitted exactly one run_summary for this run',
            shouldbe: 1, value: summaries.getRowCount() });
        assertEqual({ name: 'the run_summary line is readable',
            shouldbe: true, value: summaries.next() });
        var emitted = String(summaries.getValue('message'));
        assertEqual({ name: 'the emitted summary carries provenance="' + DERIVED + '"',
            shouldbe: true, value: emitted.indexOf('provenance="' + DERIVED + '"') !== -1 });
        assertEqual({ name: 'the emitted summary carries processed="' + EXPECT_PROCESSED + '"',
            shouldbe: true,
            value: emitted.indexOf('processed="' + EXPECT_PROCESSED + '"') !== -1 });

        // The setup step wrote NO summary, so no all-zero one exists for this run. This is
        // the assertion that catches a writeRunSummary call reintroduced into step 20.
        var zeroed = new GlideRecord('syslog');
        zeroed.addQuery('message', 'CONTAINS', '[x_bst_startuptrk.ingestion]');
        zeroed.addQuery('message', 'CONTAINS', 'run="' + T + '"');
        zeroed.addQuery('message', 'CONTAINS', 'event="run_summary"');
        zeroed.addQuery('message', 'CONTAINS', 'processed="0"');
        zeroed.query();
        assertEqual({ name: 'no all-zero run summary exists for this run',
            shouldbe: 0, value: zeroed.getRowCount() });
        logged = 'asserted: exactly 1 run_summary line, none all-zero';
    }

    var LABEL = DERIVED === 'live' ? 'live validated' : 'fallback validated';
    stepResult.setOutputMessage('RESULT LABEL: ' + LABEL + ' | run_id=' + T +
        ' | the ingestion wrote the only summary: processed=' + summary.processed +
        ' rejected=' + summary.rejected + ' duplicates=' + summary.duplicates +
        ' unmatched=' + summary.unmatched + ' skipped=' + summary.skipped +
        ' provenance=' + DERIVED + ' recorded=' + summary.recorded +
        ' | staging processed=' + processedRows + ' rejected=' + rejectedRows +
        ' | setup wrote none | log ' + logged);
    return true;
})(outputs, steps, params, stepResult, assertEqual);
```

`writeRunSummary()` accepts **only** `live` and `fallback`. Any other value logs a `run_summary_provenance_invalid` event at error level and writes nothing, so a typo would produce a run with no summary rather than a run with a wrong one — which is why the setup step asserts its derived value against that pair before parking it.

**This step calls `writeRunSummary()` and never `markRunComplete()`, and that is deliberate.** It establishes the result label; it has not run a batch. `markRunComplete()` would stamp this source's `succeeded` entry in `x_bst_startuptrk.ingestion.last_run_provenance` at the top of the test, which is the exact damage steps 15 and 95 exist to undo — and it would do so before step 15's captured value could help, since step 15 runs first. Step 40's and step 45's orchestrator calls pass the real `succeeded` from their own outcome; this one does not.

### The naming and annotation convention

So that a passing result can never be mistaken for validated live integration, apply all three. The canonical names are the ones in [The canonical test names](#the-canonical-test-names-and-the-one-that-carries-a-mode-suffix) and the two in force on this instance both carry `[fallback]`:

| Where | Convention |
| --- | --- |
| Test name | Suffix the mode: `BST FLOW — Crunchbase Ingestion [fallback]`, `BST FLOW — LinkedIn Ingestion [fallback]`. Rename to `[live]` only when the derivation at step 20 resolved to `live`. |
| Test description | Two mandatory sentences, in this order. First, the coverage boundary: `Integration test over the ingestion orchestrator entry point IngestionMapper.ingestStaging, the call the Crunchbase Ingestion flow's orchestrator action makes, plus flow and action wiring assertions. It does not execute the flow.` — substituting the flow name. Second, the label: `Result label: fallback validated.` — or `live validated`. |
| Step output message | Steps 20 and 100 both write `RESULT LABEL: fallback validated` into the step output message, so the label appears twice in `sys_atf_test_result_step` — once from the derivation and once from the summary the ingestion wrote — and cannot be lost when the result is exported. |

**The suffix is not chosen by the author; it follows the derivation.** If step 20's derived provenance and the test's name disagree, the name is wrong. The check is in the suite 10 block of [Build verification](#build-verification).

### When live authentication fails

**If live authentication fails, re-run the test with the fallback sample dataset and label the result `fallback validated` rather than `live validated`.** Nothing in the script changes: the derivation at step 20 reads the source-mode property and the alias, resolves to `fallback`, and every later step follows. Rename the test to the `[fallback]` suffix. Do not leave a `[live]` name on a run that fell back.

On the target instance **neither credential alias currently holds a live credential**, so the derivation resolves to `fallback` for both flows and **both flow tests are named and labelled `fallback validated`**. Success criterion 4 explicitly accepts the sample-dataset substitute, so this satisfies the criterion — **provided the mode is recorded**. Recording it is the whole point of the convention above.

### Why the label is a separate evidence surface

**ATF rolls back the data a test creates.** A property value written **inside** a test therefore does **not** survive the run. The provenance the flow writes during the test is real for the duration of the test and gone afterwards, so it cannot serve as the durable evidence success criterion 4 reads. The label on the test result carries that meaning instead.

The two surfaces are distinct and must not be conflated:

| Surface | Written by | Survives the run? | Read by |
| --- | --- | --- | --- |
| **Scheduled-run provenance** | Part `8c` of the flow, on a real scheduled execution — the `succeeded` entry it writes into `x_bst_startuptrk.ingestion.last_run_provenance`, with the run summary `8b` published as its detail | **Yes.** It is written outside any test transaction. | [`../validation-checklist.md`](../validation-checklist.md), success criterion 4 |
| **ATF result label** | The step 20 setup step in this guide, labelling the result `fallback validated` or `live validated` | **No.** ATF rolls back the data a test creates, so the provenance the flow wrote inside the test does not persist. | The test report, and this guide's evidence record |

This table is stated identically in [`02-flow-crunchbase-ingestion.md`](02-flow-crunchbase-ingestion.md) and [`03-flow-linkedin-ingestion.md`](03-flow-linkedin-ingestion.md). The three documents must agree.

### The teardown is a defined state, not a restore

Step 160's script is [The teardown step](#the-teardown-step) in suite 10 and is not repeated here. What matters for the labelling convention is the reason it does not attempt a restore: **the passing branch runs the flow, and a healthy execution stamps a new completion marker.** That is the behaviour under test, so the pre-suite marker value is gone by design.

**Do not rely on the framework rollback to reverse a property write.** ATF rolls back the data a test records, and a `sys_properties` update may or may not be inside that set on a given release — so this suite is built so that the question does not arise: it writes exactly one property, it writes only that property's own source entry, and its teardown asserts the resulting state rather than promising a previous one. [The control state](#the-control-state-each-test-borrows-and-what-it-can-and-cannot-return) sets out the three obligations that replace the restore, and [W10](#operational-warnings) states what an unread teardown costs.


## Assembling and running the suites

### Assemble

Build the ten suites. **Build no eleventh.** There is no parent suite, no master suite and no suite-of-suites in this delivery, and no suite record below carries a value in its **Parent** field.

To create a suite: **All** > **Automated Test Framework** > **Test Suites** > **New**. Set **Name**, confirm the application picker reads **Boston Startup Tracker**, leave **Parent** **empty**, and **Save**. Then add that suite's tests through the **Test Suite Tests** related list, setting **Order** in tens so a test can be inserted later without renumbering.

| Batch order | Suite | Tests in it | Parent |
| --- | --- | --: | --- |
| 1 | `BST CRUD suite — startup` | 1 | *empty* |
| 2 | `BST CRUD suite — founder` | 1 | *empty* |
| 3 | `BST CRUD suite — executive` | 1 | *empty* |
| 4 | `BST CRUD suite — investor` | 1 | *empty* |
| 5 | `BST CRUD suite — fundinground` | 1 | *empty* |
| 6 | `BST CRUD suite — jobposting` | 1 | *empty* |
| 7 | `BST CRUD suite — newsarticle` | 1 | *empty* |
| 8 | `BST ACL suite — premium fields by role` | 21 | *empty* |
| 9 | `BST REST suite — resources` | 6 | *empty* |
| 10 | `BST FLOW suite — ingestion` | 2 | *empty* |
| | **Total** | **36** | **no parent suite exists** |

**Batch order is an operator procedure, not a platform record.** The ten suites are run one after another in the order above, and the ten suite results are recorded together as one batch. Nothing on the instance encodes that order: it lives in this table and in the evidence record, which is exactly why it costs no suite record to express.

**Suite membership does not make one test depend on another.** Each of the 36 tests is self-contained, creates its own users and its own fixtures, and is rolled back independently. Any test runs on its own from its own form, and a single failing test is re-run without re-running the other 35.

The batch order is the **diagnostic** order, not a dependency order. If the CRUD suites fail, the ACL and REST results are not worth reading yet, because the tables themselves are wrong.

### Run

| Action | How |
| --- | --- |
| Run one test | Open the test and click **Run Test**. |
| Run one suite | Open the suite and click **Run Test Suite**. |
| Run the whole batch | Open each of the ten suites in the [batch order](#assemble) and click **Run Test Suite**, waiting for each to reach a terminal status before starting the next. Record the ten suite results together. There is no single record to run, because there is no parent suite. |
| Client test runner | **Not required.** Every step in this guide is a **Server - Independent** or **Server - REST** step, and a server-only suite is scheduled and executed without a client runner. Attach one only if you have added a client-side step, or if a run reports that it is waiting for one — in which case find the client-side step and remove it. See [Instance prerequisite](#instance-prerequisite-atf-execution-must-be-enabled). |

Run the suites **serially, one at a time**. ATF serialises execution against a single runner, and suite 9 and suite 10 each own instance-wide state for the duration of a test — the rate-limit counter tuple and the staging rows under their own `import_run` token respectively. Two batches running at once corrupt both.

### Read the results

| Artifact | Table | What to read |
| --- | --- | --- |
| Suite result | `sys_atf_test_suite_result` | The rolled-up **Status**. A suite passes only if every test in it passes. |
| Test result | `sys_atf_test_result` | Per-test **Status**, and the **Output** message. |
| Step result | `sys_atf_test_result_step` | Per-step **Status** and **Output message** — where the assertion detail lives, including the `RESULT LABEL:` line from the flow tests and the `total_count` and `retry_after` values from the REST tests. |

A test whose status is **Error** rather than **Failure** did not assert anything: it stopped before reaching its assertion. Treat an error as an unevaluated test, not a failed one, and fix the cause before reading any other result in that run.

### Evidence to record

Record these artifacts against [`../validation-checklist.md`](../validation-checklist.md).

| Criterion | Evidence artifact | What it must show |
| --- | --- | --- |
| **2** — field-level ACLs on 100 % of the 7 premium fields, verified per role per field | The `BST ACL suite — premium fields by role` suite result, plus all **21** named test results | All 21 cells passing. For each of the seven `ACL-*.3` cells, the step 50 output message carrying `element.canRead()=false`, `key present=false`, the control column's value, and `platform admin held=false` — the three independent oracles plus the impersonation check in one line. Plus **all 35** role-set verification outputs of this suite, 21 at step 8 and 14 at step 38, one per created user, which are what prove no read was performed under an overriding role. |
| **3** — 6 REST resources return correct paginated responses and a 429 with a retry value | The `BST REST suite — resources` suite result, plus all **6** named test results | Per resource: the 200 status; the step 60 output message naming the declared keys typed, the premium keys absent and **0 undeclared keys**; the step 70 and step 100 output messages carrying the **exact** `total_count` of 4, the exact row identifiers in sort order, the exact remainder and an overlap of 0; the step 120 clamp line naming the ceiling read from the property; the step 75 and step 105 increment lines showing 1 then 2 from a zero baseline; and the step 170 line carrying `retry_after`, the seeded row reaching budget + 1, and the tuple cleaned to 0 rows. For `BST REST — founders`, all of it twice — once for `/founders` and once for the nested `/founders/{startup_id}/executives` token. |
| **4** — flows ingest and clean on the configured cadence with zero unhandled errors across three consecutive scheduled runs | The `BST FLOW suite — ingestion` suite result, plus the results of `BST FLOW — Crunchbase Ingestion [fallback]` and `BST FLOW — LinkedIn Ingestion [fallback]` **with their labels** | Both tests passing under their mode-suffixed names. Per test: the step 20 output message carrying `RESULT LABEL:` with the **derived** provenance and the three inputs it was derived from, and `no run summary written by setup`; the step 40 message carrying the exact `accepted`, `rejected`, `entries` and `summary.processed`; the step 100 message showing **exactly one** run summary for the run and **no** all-zero one; and the step 110 message naming the trigger type, the five published actions, the four action calls plus one `If`, the orchestrator's six declared outputs and the alias bound by name with no credential material. **This is not sufficient on its own.** Criterion 4's durable evidence is the run-summary records written by three consecutive guard-passing scheduled executions of each flow, which are a separate surface — see [Technique (c)](#technique-e--provenance-labelling) and [what counts as a scheduled run](../deployment-runbook.md#what-counts-as-a-scheduled-run). The suite result evidences the cleaning rules and the wiring; the run summaries evidence the cadence and the error count. |
| **1** — all 7 tables exist with 100 % of their fields | The seven `BST CRUD suite — *` suite results | One passing suite per table. Combined with `GATE-COL-01` and `GATE-TBL-01` through `GATE-TBL-07` from [`../validation-gates.md`](../validation-gates.md). |

An execution that exited on the cadence guard is a **no-op**: it is not a scheduled run and is not evidence of anything. Do not count it among the three consecutive runs criterion 4 requires.

## Coverage gate

**The hard minimum is 100 % of the 6 REST resources and 100 % of the 7 tables with a passing ATF test before delivery.**

| Gate | Requirement | Satisfied by |
| --- | --- | --- |
| Table coverage | Each of the 7 entity tables has at least one passing test | Suites 1 to 7, one per table |
| REST coverage | Each of the 6 logical resources has at least one passing test | Suite 9, one test per resource, including the nested sub-resource inside `BST REST — founders` |
| ACL coverage | Each of the 7 premium fields has a passing test under each of the 3 roles | Suite 8, all 21 cells |
| Flow coverage | Each of the 2 flows has a passing test | Suite 10, one test per flow |

Delivery is **blocked** if any of the following holds:

- Any of the 7 entity tables lacks a passing test.
- Any of the 6 logical resources lacks a passing test, or the nested `GET /founders/{startup_id}/executives` is untested.
- Any of the 21 ACL cells is missing, failing, or in the **Error** state.
- Either flow test is missing, failing, or unlabelled.
- The suite count is **not exactly 10**, or the test count is **not exactly 36**. Eleven suites blocks delivery as surely as nine does: the specification fixes the number, and an aggregating parent record is the usual way the count reaches 11.
- **ATF execution is not enabled on the instance.** In that case the gate cannot be evaluated **at all** — it is not failed and not partially met, it is unevaluable, and no delivery claim about coverage can be made. See [Instance prerequisite](#instance-prerequisite-atf-execution-must-be-enabled).

## Rename impact

**These suites encode identifiers as literal values in step inputs and in script bodies. A rename anywhere in the following list must propagate into this guide, or the affected tests fail against correct behaviour.**

| Encoded here | Count | Where it appears |
| --- | --: | --- |
| Premium field names | 7 | Suite 8's cell table, its per-cell fixture table, the step 50 scripts, and the premium-omission block of suite 9's step 70 script |
| Role names | 3 | Every **Create a User** `roles` input, every role-set verification script, and suite 8's cell table |
| Logical resource paths | 6 | Every `end_point` input in suite 9 |
| The nested sub-resource path | 1 | `BST REST — founders`, both as an `end_point` and as a rate-limit token |
| Rate-limit `api_resource` tokens | 7 | The seeding script of every REST test |
| Pagination parameter names | 2 | **`sysparm_limit`** and **`sysparm_offset`**, in every `query_params` input in suite 9 |
| Envelope member names | 4 | `result`, `total_count`, `limit`, `offset`, in suite 9's assertion scripts |
| Entity table names | 7 | Every `table` input across suites 1 to 8 |
| Supporting table names | 3 | `x_bst_startuptrk_m2m_round_investor`, `x_bst_startuptrk_ingest_staging`, `x_bst_startuptrk_rate_limit_counter` |
| Script Include class and method names | 6 classes | `IngestionMapper`, `IngestionLogger`, `RestResponseBuilder`, `RateLimitService`, `AppProperties`, `InvestorPortfolioService` |
| System-property keys | 5 | `x_bst_startuptrk.rest.rate_limit_requests`, `x_bst_startuptrk.rest.rate_limit_window_seconds` and `x_bst_startuptrk.rest.max_limit` in suite 9; `x_bst_startuptrk.ingestion.source_mode` and `x_bst_startuptrk.ingestion.last_run_provenance` in suite 10, read through `AppProperties` rather than by key, so a **key** rename is absorbed and an **accessor** rename is not |
| Choice member strings | 63 | The choice-value assertions of suites 1 to 7 and the normalisation assertions of suite 10 |
| Flow names | 2 | `Crunchbase Ingestion`, `LinkedIn Ingestion`, in suite 10's test names, descriptions and step 110 wiring assertions |
| Flow action names | 5 per flow | `Cadence Guard`, `Resolve Source Mode`, `Fetch <source> Payload`, `Ingest <source> Batch`, `Reconcile Batch Counters`, in suite 10's step 110 script. A renamed action fails the wiring assertion, which is the intended behaviour — but the constant must be updated to match the rename before the test is trusted again |
| Declared action output names | 6 + 4 | The orchestrator's `processed`, `rejected`, `skipped`, `duplicates`, `unmatched`, `recorded` and the cadence guard's four including `proceed`, in suite 10's step 110 script |
| Credential alias names | 2 | `x_bst_startuptrk.crunchbase_api`, `x_bst_startuptrk.linkedin_oauth`, in suite 10's step 20 derivation and step 110 alias-binding assertion |
| Orchestrator entry-point signature | 1 | `IngestionMapper.ingestStaging(runId, sourceSystem, importRun, provenance)`, called at suite 10's step 40. A change to its parameter order or its returned members breaks half A of both flow tests |
| Provenance labels | 2 | `live validated`, `fallback validated` |

[`../api-reference.md`](../api-reference.md) carries the Script Include call graph, which is the authoritative rename-impact list for the service layer; a class renamed there breaks every caller, including the scripts in this guide. The Update Set XML at [`../../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml`](../../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml) remains authoritative for every spelling.

## Operational warnings

**Eleven** warnings: `W1`, `W2`, `W3`, `W4`, `W4b`, `W5`, `W6`, `W6b`, `W6c`, `W7` and `W8`. **W1, W2, W6 and W6c are completely silent** — every test reports `success` while the property under test was never exercised at all — and `W4b` is silent until the run in which it is not.

**W1. The administrator ACL override makes suite 8 pass without testing anything. SILENT.**
Record ACLs by default allow the platform administrator role to override them, and every operator of a personal developer instance holds that role. Read a premium field as yourself and all seven appear, the suite reports `success`, and the field-level ACLs were never consulted. Without impersonation, success criterion 2 is not weakly evidenced — **it is not evidenced at all**. Every read assertion must follow an **Impersonate** step, and the impersonated user's role set must be verified by that test's own step 8 and step 38 scripts rather than assumed or borrowed from another test. Full detail under [Technique (a)](#technique-a--impersonation).

**W2. `enforce_security` left `false` makes every record step pass vacuously. SILENT.**
`Record Insert`, `Record Update`, `Record Query`, `Record Delete` and `Record Validation` each expose an `enforce_security` input. With it `false` the step runs unrestricted, ignores every ACL, and reports `success`. Set it **true** on every record step in this guide. In suite 8 the entire assertion depends on it; in suites 1 to 7 it is what proves the write ACLs grant `x_bst_startuptrk.admin` and no one else.

**W3. `Assert JSON Response Payload Element` cannot prove a key is absent.**
Its nearest presence operator is `exists`, whose label in the form is literally **"is not empty"**. It does not distinguish a key that is missing from a key that is present holding an empty string — and an empty string is exactly what the secured read returns for a denied field. Using it for the omission assertion would pass against the forbidden nulled behaviour. Assert key absence in a **Run Server Side Script** step with `Object.prototype.hasOwnProperty.call(body, FIELD) === false`. `does_not_contain` against the raw payload is a weaker supplementary check only, and must not be the primary assertion.

**W4. Seeding the rate-limit row against the wrong caller stops the 429 from firing.**
`Send REST Request - Inbound` performs a real inbound HTTP call and establishes its **own** session. An `Impersonate` step earlier in the test has no bearing on it. The limiter accounts against **the REST caller**, the user in the step's **Basic authentication** profile — seed that user's `sys_id` in `caller`, not the impersonated user's. The symptom is a 200 where a 429 was asserted, with no other diagnostic.

**W4b. Updating one row of the tuple is not the same as owning the tuple. SILENT until it is not.**
The triple `caller` + `api_resource` + `window_start` carries **no uniqueness constraint**, and the limiter finds its row with a query limited to one. If several rows share the tuple, the row it selects may not be the row the test seeded, and the request returns 200. Worse, a run that leaves rows behind makes the *next* run's baseline wrong rather than its own — so the failure surfaces one run after the run that caused it. Delete every row for the tuple at step 25, seed exactly one at step 130, assert the count of rows both times, and delete every row again at step 170. Counter rows are created by inbound HTTP requests in their own sessions and are **not** rolled back with the test.

**W5. A window boundary crossing between the seed step and the request stops the 429 from firing.**
The counter is a fixed window. If the seed lands near the end of a window and the request arrives in the next one, the service computes a different `window_start` boundary, finds no row for the triple, and starts a fresh count at 1. Every counter step guards this by measuring the remaining window and waiting for the next boundary — step 25 when fewer than twenty seconds remain, so the whole sequence of ordinary calls shares one window, and step 130 when fewer than ten remain, so the seed and the request of step 140 share one. Keep both guards. The symptom is an intermittent 200 where a 429 was asserted — passing on most runs and failing on a few.

**W6. A setup step that writes a run summary makes the run summary worthless. SILENT.**
`IngestionLogger.writeRunSummary()` is not an inert label: it validates the provenance, emits the `run_summary` event and returns the counters. Called from a setup step, before any ingestion has run, it writes a summary carrying **all-zero counters** — and a later assertion that reads "the run summary" can find that one and pass against it, reporting a successful ingestion of nothing. Suite 10's step 20 therefore **derives and labels only**, and every summary assertion binds to `outcome.summary`, the object the single `ingest()` call at step 40 returned. Step 100 additionally asserts that **no all-zero summary exists for the run**, which is the check that catches a reintroduction.

**W6b. Provenance written inside a test does not survive the run.**
ATF rolls back the data a test creates, so the property `ingest()` sets during suite 10 is gone once the test finishes. It cannot serve as criterion 4's durable evidence. The ATF **result label** carries that meaning, and the run-summary records of real scheduled executions are the separate, surviving surface. Do not substitute one for the other. Full detail under [Technique (c)](#technique-e--provenance-labelling).

**W6c. A fixed run token collides with itself. SILENT.**
A token such as `atf-crunchbase-001`, hard-coded identically in every step, cannot distinguish this execution from the previous one or from a concurrent run of the other flow test: staging rows, log events and run summaries all share the identifier. Every exact-count assertion in suite 10 is then counting rows two runs contributed to. The token is minted once per execution at step 20 from the current time in milliseconds plus a random component, parked on a record the test creates, and read back by every later step through the stock `record_id` output — Contract 2, mechanism 3.

**W7. A test built in the Global scope has its record steps refused.**
Cross-scope `create_access`, `update_access` and `delete_access` are false on all ten tables, and the three supporting tables are additionally `package_private` with `read_access` false — the posture the non-normative diagnostics `GATE-SEC-01` and `GATE-SEC-02` record. Every record step in this guide writes, so a test created while the application picker reads **Global** is an out-of-scope caller and is refused before any ACL is consulted, which looks like an ACL failure but is not one. Confirm the picker reads **Boston Startup Tracker** before creating any test or suite. Where a record step is still refused, use a **Run Server Side Script** step, which compiles in the test's own scope.

**W9. A flow test that does not restore the cadence properties silently disables the next scheduled run. SILENT.**
`ingest()` ends in `writeRunSummary()`, which emits the `run_summary` event and writes no property; the orchestrator's final phase then calls `markRunComplete()`, which stamps this source's `succeeded` entry in `x_bst_startuptrk.ingestion.last_run_provenance`. That entry's stamp is the value the flow's cadence guard compares, so a suite run at 09:00 makes every execution of that flow a no-op until the cadence has elapsed — up to 48 hours. The flow test passes, the flow then does nothing, and success criterion 4's three consecutive guard-passing runs never start. Nothing reports an error at any point. **A batch that rejects rows does not protect you**: rejections are cleaning-rule outcomes rather than errors, so `succeeded` is still `true` and the marker is still written. Steps 15 and 95 capture and restore that one ingestion property, step 95 runs last and unconditionally, step 15 **aborts** the next run if a previous one did not reach step 95, and the guide publishes an out-of-band restoration for that case. Full detail under [Protecting the cadence state](#the-fixture-step).

**W8. A residual `BST ATF` user after a run means a transaction did not close.**
The three impersonation users are created at run time and rolled back with the rest of the test data. After a completed run, `sys_user` must carry no user whose first name is `BST ATF`. If one remains, a test errored in a way that left its transaction open, and no result in that run should be trusted until the cause is found. **This assertion has no exception.** The REST caller of suite 9 carries the first name `BST REST` precisely so that it never muddies this signal: on [Construction A](#construction-a--an-ephemeral-identity-created-and-rolled-back-inside-the-test-preferred) it is also rolled back and its own residual check is the second and third items under [Teardown](#teardown--the-rest-caller-must-not-outlive-the-run); on [Construction B](#construction-b--a-persistent-identity-hardened-fallback-only) it persists between runs by design and is deleted by that teardown when the ATF work is finished.

## Legacy provenance

The legacy repository carries a test tree that never ran. These suites replace it. **Nothing about its structure, fixtures or assertions is carried forward.**

| Legacy artifact | Verified fact | Replaced by |
| --- | --- | --- |
| `pytest.ini:L6` | `testpaths = tests/backend`, which confines collection to one of the three test trees and so **excludes 16 of the 27** test files — all 10 under `tests/data_collection/` and all 6 under `tests/frontend/`. | The ten-suite [batch order](#assemble), which covers all four suite groups explicitly. Nothing is excluded by configuration, because nothing is selected by configuration. |
| `pytest.ini:L9` | `python_files = test_*.py`, a collection pattern that matches **zero files on disk**, because every Python test in the tree is named `*_test.py`. | ATF suite membership is explicit: 36 rows in `sys_atf_test_suite_test`, each naming its test. Nothing is discovered by pattern, so nothing can silently fail to be discovered. |
| `tests/**` | **27 test files whose discovery never matched**, split **11 backend** (6 route tests — auth, investor, job, news, startup, user; and 5 service tests — investor, job, news, startup, user), **10 data_collection** (2 API-integrator, 2 data-cleaning, 2 data-enrichment, 4 scraper), and **6 frontend** (4 `*.test.tsx` component tests and 2 `*.test.ts` utility tests). | 10 suites, 36 tests. The 4 scraper tests have no counterpart: the scrapers are retired and no requirement replaces them. |
| `tests/backend/routes/startup_test.py:L4-L6` | Imports `from app import app`, `from db import db` and `from Startup import Startup` — flat module names that resolve nowhere in the tree, so **even with a corrected collection pattern the suite would fail at import**. | **27 files, zero executable tests.** Every one of the 36 tests in this guide runs on the instance against real records. |

No legacy fixture pattern, assertion helper, mocking approach or test-naming convention appears anywhere in this guide.

## Build verification

Work through every box before this guide is signed off.

**Prerequisites**

- [ ] `sn_atf.runner.enabled` reads `true` on the instance.
- [ ] You hold `atf_test_designer`, and `atf_test_admin` if you needed to set the property.
- [ ] The application picker reads **Boston Startup Tracker** for every test and suite created.
- [ ] **Every step in all 36 tests is a `Server - Independent` or `Server - REST` step, and no client-side step exists.** Filter `sys_atf_step` on these tests and confirm no step's configuration carries a client-side category. This is what makes the client test runner unnecessary; a run that waits for a runner means this check was not done.
- [ ] The REST caller construction has been chosen and recorded, together with the design-time check outcome, in the table under [Teardown](#teardown--the-rest-caller-must-not-outlive-the-run).
- [ ] The REST caller holds **exactly** `x_bst_startuptrk.user` and carries `web_service_access_only` `true`, so it cannot sign in to the user interface.
- [ ] Its Basic Auth Configuration references it, and **no password value appears in this guide, in any other document of this package, in an evidence table or in any transcript**.
- [ ] The account owner and the expiry date are recorded before the first run.
- [ ] The teardown has been performed **and verified by query** after the last run, and the evidence is recorded. On Construction A both residual queries return empty; on Construction B all four deletion confirmations hold.
- [ ] The REST caller's password was **generated**, is at least 24 characters, and appears **only** in the `sys_user` record and the Basic Auth Configuration — not in any script, step input, evidence row, defect report or the Update Set. Confirm by searching the guide and the evidence record for the value and expecting zero hits.
- [ ] On Construction B, the rotation and end-of-life actions of [Lifecycle of a Construction B account](#lifecycle-of-a-construction-b-account) are scheduled and recorded: rotate after acceptance, then delete. Record which was done: `______`

**Inventory**

- [ ] **10** suites exist, named exactly as in [What this guide builds](#what-this-guide-builds).
- [ ] **Exactly 10** `sys_atf_test_suite` records exist in the `x_bst_startuptrk` scope, and **every one of them has an empty Parent field**. Count them: `______`. A count of 11 means a parent suite was built; delete it and record the ten suite results as a batch instead.
- [ ] **36** tests exist: 7 + 21 + 6 + 2.
- [ ] Every one of the 36 tests is a member of its suite with an explicit **Order**.
- [ ] Every test name matches [The canonical test names](#the-canonical-test-names-and-the-one-that-carries-a-mode-suffix) exactly, and **both suite-10 tests carry a `[fallback]` or `[live]` suffix** — neither exists in an unsuffixed form.
- [ ] **0** new step configurations were created.

**The two ATF contracts**

- [ ] **Every `steps(...)` reference passes a filled-in 32-character step `sys_id` constant, never a display order number and never an empty string.** Search every script for `steps('` and confirm no literal digit string and no empty string remains. Count the references you filled in: `______`.
- [ ] **No script assigns an output name other than `outputs.record_id` or `outputs.table`.** Those two are the stock outputs of a `Run Server Side Script` step; any other name is discarded silently. Search every script for `outputs.` and confirm every hit is one of those two, and that each one is in a script this guide marks as using them — suite 9's counter-seeding step and suite 10's run-token step.
- [ ] Every value shared between steps arrives by one of the three permitted mechanisms: a stock output of the producing step, an identically declared constant, or a record the test creates and reads back through `record_id`.
- [ ] **Every run-time-computed value crossing a step boundary uses mechanism 3**, never a hard-coded stand-in. Suite 10's run token and suite 9's baseline counts are the two cases.

**Suites 1 to 7 — table CRUD**

- [ ] One suite per entity table, covering `x_bst_startuptrk_startup`, `x_bst_startuptrk_founder`, `x_bst_startuptrk_executive`, `x_bst_startuptrk_investor`, `x_bst_startuptrk_fundinground`, `x_bst_startuptrk_jobposting` and `x_bst_startuptrk_newsarticle`.
- [ ] Each asserts insert, update, query and delete.
- [ ] **Every query, validation, update and delete binds to the `record_id` output of the step that inserted the record**, per [Identity rule](#identity-rule--bind-to-record_id-never-to-a-display-value). Search every record step's inputs for a display-value condition and confirm the only ones left are steps 80 and 90, where no record is expected to exist. Steps 50 and 120 assert **exactly one** and **no** records respectively, both on `Sys ID`.
- [ ] Each asserts a mandatory-field omission with **Record was not inserted** — one step per mandatory column, 13 such steps across the seven tables.
- [ ] **Suite 1's `active` default is asserted by two separate steps**, a `Record Insert` at 130 and a `Record Validation` at 135 bound to step 130's `record_id`. Confirm no single step is configured as both.
- [ ] **Step 100 asserts the choice contract at the record layer on every choice column of the table under test** — the dictionary declaration, the exact member list and its order, verbatim storage of every member, a blank, `max_length` truncation, and that the record layer stores a non-member as supplied. Confirm step 100 **instantiates** no ingestion class: search each step-100 script for `new IngestionMapper` and `new IngestionLogger` and expect zero hits. The one prose mention of the mapper inside the script is a comment pointing at suite 10 and is not a call.
- [ ] All **eleven** choice columns are covered across the seven suites, and their member lists match [The eleven choice columns](#the-eleven-choice-columns-and-their-delivered-lists) exactly: 3 on startup, 1 on founder, 1 on executive, 2 on investor, 1 on funding round, 3 on job posting, 0 on news article.
- [ ] Suite 4's step 130 asserts the `portfolio_count` write contract, **including that a server-side write is not blocked** and that the field is absent from the `PUT /investors/{id}` write allowlist. Suite 5's step 130 asserts the `participating_investors` projection is recomputed from the join table. Neither step asserts that a script write is refused.
- [ ] Suite 4's step 140 walks **all seven `portfolio_count` states** — 0, 1, 1, 2, 1, 1, 0 — reading the stored value without calling the service, and then asserts stored equals derived.
- [ ] Suite 7's step 100 asserts `published_date` through record round trips and the two write operations' date validation, with malformed and impossible values refused by **different** messages. Confirm it calls no ingestion date parser.
- [ ] `enforce_security` is **true** on every record step.
- [ ] No `Other` member was added to any of the six lists that lack one, and no member of any of the eleven lists was added, removed or reordered.

**Suite 8 — premium fields by role**

- [ ] All **21** cells `ACL-1.1` through `ACL-7.3` exist as separate tests.
- [ ] The 7 field names and 3 role names match [`../access-control.md`](../access-control.md) exactly.
- [ ] **Every cell asserts oracle 1 as `gr.getElement(FIELD).canRead()` on a `GlideRecordSecure` read.** Search every step-50 script for `canRead` and confirm **no hit is `RestResponseBuilder`'s** wrapper: the builder appears in these scripts only as the argument of `serialize()`, where it is the subject of oracle 2 rather than the authority. A cell whose oracle is the builder's own `canRead()` is asserting a helper against itself and must be rewritten.
- [ ] Every cell asserts oracle 2 independently of oracle 1 — key presence on the object `serialize()` returned — and oracle 3, the control column, under **both** branches.
- [ ] The 14 `*.1` and `*.2` cells assert the key is **present**, the value is **non-empty**, and the serialised value equals the element value.
- [ ] The 7 `*.3` cells assert the key is **absent** via `hasOwnProperty` **and** that `typeof body[FIELD]` is `undefined` — never that the value is falsy, empty or null, either of which passes against the forbidden nulled response.
- [ ] **Every one of the 21 cells carries its own role-set verification step**, and the 14 two-user cells carry two: 21 at display order 8 and 14 at display order 38, **35 in suite 8** and **50 across the whole guide**, per the table under [Step 2](#step-2--verify-the-role-set-before-trusting-the-test). Confirm no cell relies on another cell's verification and none is done once for the suite.
- [ ] Each verification asserts exactly one scoped role, names each forbidden platform role individually, and asserts **zero** group memberships.
- [ ] Every cell asserts inside its step 50 that `gs.getUserID()` is the user under test and that `gs.hasRole('admin')` is `false`, so a silently ineffective `Impersonate` step cannot produce a false pass.

**Suite 9 — REST resources**

- [ ] All **6** resources have a test, and the nested `GET /founders/{startup_id}/executives` is exercised inside `BST REST — founders` as a full second pass with its own counter token.
- [ ] Every `end_point` uses the physical base path `/api/x_bst_startuptrk/v1/`.
- [ ] Pagination uses exactly `sysparm_limit` and `sysparm_offset`.
- [ ] **Each test seeds five records — four the filter selects and one negative control it must not** — with distinct values in the resource's sort column, and passes the marker filter on every list call.
- [ ] **`total_count` is asserted to be EXACTLY 4** on page one and page two, not "at least the rows returned" and not merely stable. A greater-than-or-equal assertion is not acceptable here: it passes against a count of the whole table.
- [ ] **Membership is asserted exactly**: page one is expected identifiers 0 and 1 in order, page two is 2 and 3 in order, the remainder is exactly 2, overlap is 0, the union is the whole filtered set, and the negative control is absent from every page.
- [ ] The `/startups` test's negative control is **inactive and outside both location tokens**, and is proved absent from `result` **and** uncounted in `total_count` — the assertion that the inclusion filter reached the count and the page identically.
- [ ] **Each test asserts the per-resource schema**: every declared key present with its declared type, **no undeclared key**, and every premium key **absent** with `typeof` `undefined`. The key lists match [The per-resource schema assertion](#the-per-resource-schema-assertion), including `participating_investors` as an array of reference objects on `/funding-rounds`.
- [ ] The over-limit request is asserted to clamp to the value of `x_bst_startuptrk.rest.max_limit`, read through `AppProperties`, and to return the whole filtered set on one page in sort order.
- [ ] **The counter tuple is owned, not merely written to.** Step 25 deletes every row for the triple and asserts **0**; steps 75 and 105 assert **exactly one** row reading **1** then **2**; step 130 deletes again and asserts **exactly one** row reading exactly the budget; step 170 asserts the incremented row is the seeded row at budget + 1 and then deletes every row, asserting **0** again.
- [ ] The increment assertions at 75 and 105 are present. Without them the `429` assertion is made against a hand-seeded row and would pass with the increment logic broken.
- [ ] Each test asserts status `429`, `error` is `rate_limit_exceeded`, `retry_after` is a positive integer no greater than the window, and the body carries **exactly** `error,retry_after`.
- [ ] The counter row is seeded against **the REST caller** — step 1's `caller_sys_id` on Construction A, `bst.rest.caller` on Construction B — at `request_count` equal to the budget, with the correct one of the **seven** `api_resource` tokens.
- [ ] The window-boundary guard is present in **both** step 25 (20 seconds) and step 130 (10 seconds).
- [ ] The three boundary requests are present and pass: a page past the end returns no rows with the total unchanged, a filter matching nothing returns `total_count` `0`, and `sysparm_offset` `10001` is refused with `400` and a body carrying no `result` member.
- [ ] **The no-match filter value is well formed and simply matches nothing** — the step 20 marker suffixed `ZZZ` — so boundary 2 exercises the empty-set path and not the refusal path.
- [ ] The over-limit request is asserted to clamp to `50`.

**Suite 10 — ingestion flows**

- [ ] Both `Crunchbase Ingestion` and `LinkedIn Ingestion` have a test, and **both test names carry the mode suffix** the step 20 derivation produced. Neither exists in an unsuffixed form.
- [ ] **Each test's description states the coverage boundary before its label**, naming `IngestionMapper.ingestStaging` as the entry point under test and stating in terms that it does **not** execute the flow, per [The naming and annotation convention](#the-naming-and-annotation-convention). A reader of the test record must not be able to mistake it for an end-to-end flow execution test.
- [ ] **Half A calls the orchestrator entry point, not a copy of its logic.** Each test's step 40 calls `IngestionMapper.ingestStaging(runId, sourceSystem, importRun, provenance)` — the identical call the delivered orchestrator action makes — exactly **once**. Search each test's scripts for `ingestStaging(` and confirm the only hits are step 40 and the deliberate second call inside the rule 3 update case.
- [ ] **Half B exists.** Each test carries a step 110 wiring assertion covering all eight rows of [The wiring assertions](#the-wiring-assertions). A test without it passes for a flow that never reaches its orchestrator.
- [ ] **The exact returned object is asserted**, not a loose truthiness check: `accepted` and `rejected` at the **top level**, `processed` **only** under `summary`, and an explicit assertion that **no top-level `processed` member exists**.
- [ ] **Every summary counter is asserted exactly** — `processed`, `rejected`, `duplicates`, `skipped`, `unmatched`, `provenance` and `recorded` — and `summary.rejected` is **not** confused with the top-level `rejected`: for Crunchbase they are 3 and 4, because the within-batch duplicate is counted under `duplicates`.
- [ ] **`summary.unmatched` accounts for the rejected row that still logged an unmatched choice.** Crunchbase expects **3**, not 2: normalisation runs before the mandatory-field check, so row 11's `Series Q` is logged before the row is refused for its missing `round_date`. LinkedIn expects **4**.
- [ ] **Step 40 parks its returned object on the token record**, and steps 60 and 100 read the counters from there rather than re-deriving them. No step calls `ingestStaging()` a second time except the rule 3 update case, which uses a **different** token.
- [ ] **Every log assertion is guarded by `AppProperties.isLogLevelEnabled()`** and skips itself rather than failing when the configured level suppresses the line. `x_bst_startuptrk.logging.level` reads `info` while suite 10 runs, so both `run_summary` (info) and `choice_unmatched` (warn) reach `syslog`.
- [ ] **Continuation is asserted per record type**, not by position: every record type that produced a rejection also produced a processed row, and no entry was left in a non-terminal state. `expandRows()` sorts into `TYPE_ORDER`, so a positional assertion would be asserting against the sort.
- [ ] The counts asserted at step 40 match the fixture tables exactly — Crunchbase `accepted` 7, `rejected` 4, `entries` 11; LinkedIn `accepted` 5, `rejected` 3, `entries` 8. A fixture changed without changing these numbers fails the test rather than weakening it silently.
- [ ] **The run token is minted per execution** at step 20 from the current time plus a random component, parked on a record the test creates, and read back by every later step through the stock `record_id` output. Search every suite-10 script for a hard-coded token such as `atf-crunchbase-001` and expect **zero** hits.
- [ ] **The setup step writes no run summary.** Search every suite-10 script for `writeRunSummary` and confirm the only hits are inside comments. A call there produces an all-zero summary a later assertion can pass against.
- [ ] **The provenance is derived, not declared**: step 20 reads the source-mode property and the alias's credential state, claims `live` only when both agree, and records all three values in its output message.
- [ ] Step 100 asserts **exactly one** run summary for the run, that it carries the derived provenance and the expected `processed`, and that **no all-zero summary exists** for the run.
- [ ] Each test seeds **its own** staging rows under the minted `import_run` token — Crunchbase 11 rows, LinkedIn 8 rows plus one directly inserted parent startup — and asserts the pending row count before ingesting. No test depends on a row loaded by [`06-staging-table-csv-import.md`](06-staging-table-csv-import.md).
- [ ] **The Crunchbase funding rounds resolve against `<T> Choice Coerce`, never `<T> Dedupe Target`.** Two startups carry the latter name by design, so a round pointing at it resolves only on the full composite key, and a round that carries the name without the matching `startup_headquarters_location` is rejected for the wrong reason.
- [ ] **Startup deduplication is asserted in the Crunchbase test only**, because `dedupeBatch()` skips every entry whose `record_type` is not `startup` and a LinkedIn batch contains none. Confirm the LinkedIn test asserts **parent resolution** onto the pre-existing startup instead, plus the `no startup carries the name and headquarters location` failure. A LinkedIn dedupe assertion is asserting against an unreachable path.
- [ ] Deduplication is asserted on `name` plus `headquarters_location`, case-insensitively, including the differing-location negative control and the loser's `duplicate startup in the same batch` reason.
- [ ] Choice normalisation is asserted across **five columns for Crunchbase and six for LinkedIn**, both branches, with the unmatched count asserted **exactly** from the parked summary — a silent coercion fails even where every stored value is right.
- [ ] The `x_bst_startuptrk_investor.type` asymmetry is asserted threefold: left unwritten, logged, **and the row still inserts**. The same shape is asserted for `remote_type` and `seniority` in the LinkedIn batch.
- [ ] Left unwritten is distinguished from emptied: the Crunchbase test re-ingests one investor to prove a previously stored value survives an uncoercible one.
- [ ] Records missing a mandatory field are asserted to be rejected with nothing partial inserted, **one row per record type the flow writes** — three per test — plus the general sweep that no row the run created carries an empty mandatory column.
- [ ] Each test reports a non-zero `accepted` **and** a non-zero `rejected` from one call, and step 80 finds **no** row still `pending`.
- [ ] **The Crunchbase test asserts the ingestion effects**: exactly two m2m join rows, the lead investor absent from them, the `participating_investors` projection naming both participants, `portfolio_count` of 1 for all three investors, no accumulation when the round is repointed, and 0 for all three with the join rows cascaded after the round is deleted.
- [ ] Each result is labelled exactly `fallback validated` or `live validated` in **both** the step 20 and step 100 output messages, and the label agrees with the test name's suffix.

**Run and evidence**

- [ ] All **ten** suites were run in the [batch order](#assemble), each to a terminal status, with **36 of 36** tests passing and **0** in the **Error** state. Record all ten suite result identifiers together.
- [ ] No residual `BST ATF` user remains in `sys_user`.
- [ ] The suite results, test results and step results for criteria 2, 3 and 4 are recorded against [`../validation-checklist.md`](../validation-checklist.md).
- [ ] Criterion 4's three consecutive guard-passing scheduled runs per flow are recorded from the **run-summary records**, not from the ATF results.
- [ ] The [Coverage gate](#coverage-gate) is met: 100 % of the 7 tables and 100 % of the 6 resources have a passing test.

## Related documents

- [`../../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml`](../../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml) — authoritative for every identifier cited in this guide
- [`../access-control.md`](../access-control.md) — the 3 x 7 role-by-field matrix, the secured read path, the omit-not-nulled rule and the impersonation requirement
- [`../api-reference.md`](../api-reference.md) — the 6 resources, the nested sub-resource, the pagination contract, the exact 429 and 500 bodies, and the Script Include call graph
- [`../data-model.md`](../data-model.md) — the 53 columns, the 14 mandatory flags and all 11 choice lists the CRUD suites assert against
- [`../validation-gates.md`](../validation-gates.md) — the eleven required post-commit gates of precondition 4, and the acceptance-required `GATE-COL-01` and three non-normative diagnostics recorded beside them
- [`../deployment-runbook.md`](../deployment-runbook.md) — the import sequence, the ATF prerequisite assertion, and [what counts as a scheduled run](../deployment-runbook.md#what-counts-as-a-scheduled-run)
- [`01-connection-credential-aliases.md`](01-connection-credential-aliases.md) — the two aliases and the LinkedIn product-contract gate, whose recorded route decides the flow-test label
- [`02-flow-crunchbase-ingestion.md`](02-flow-crunchbase-ingestion.md) — the `Crunchbase Ingestion` flow under test
- [`03-flow-linkedin-ingestion.md`](03-flow-linkedin-ingestion.md) — the `LinkedIn Ingestion` flow under test
- [`04-service-portal-pages-and-widgets.md`](04-service-portal-pages-and-widgets.md) — the five pages and eight widgets, and the walkthrough that reuses the three impersonated users
- [`06-staging-table-csv-import.md`](06-staging-table-csv-import.md) — the staged fallback rows the flow tests act on
- [`../../sample-data/README.md`](../../sample-data/README.md) — the CSV column contract behind those rows
- [`../../scripts/validate_update_set_xml.py`](../../scripts/validate_update_set_xml.py) — the two-level XML validator run before import
- [`../../README.md`](../../README.md) — the package index
- [`../validation-checklist.md`](../validation-checklist.md) — success criteria 2, 3 and 4, whose evidence these suites produce
- [`../manual-build-instructions.md`](../manual-build-instructions.md) — the build order and the Update Set versus manual-build split rule
- [`../gaps-and-flags.md`](../gaps-and-flags.md) — the requirements with no clean platform equivalent, including the administrator ACL override
- [`../../../docs/decisions/DECISION_LOG.md`](../../../docs/decisions/DECISION_LOG.md) — the single destination for every "why"
- [`../../../docs/decisions/TRACEABILITY_MATRIX.md`](../../../docs/decisions/TRACEABILITY_MATRIX.md) — the bidirectional legacy-to-platform and requirement-to-artifact mapping
