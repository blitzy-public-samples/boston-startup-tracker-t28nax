# Manual build 05 — Automated Test Framework test suites — `x_bst_startuptrk`

This guide builds **10 Automated Test Framework test suites containing 36 tests**, by hand, on the instance, through the Automated Test Framework modules of the ServiceNow scoped application `x_bst_startuptrk`. It specifies every suite, every test within it, and every step within every test, naming the exact ATF step configuration used at each step and the exact input values that step is given. The suites cover the seven entity tables, the twenty-one premium-field-by-role access-control outcomes, the six REST resources including the nested sub-resource, and the two scheduled ingestion flows. It then specifies the three techniques the evidence depends on — impersonation, the deterministic rate-limit trip, and provenance labelling — how to assemble the suites into a runnable set, how to read the results, and which result artifacts the operator records as evidence.

**Authority.** The frozen prompt and the Agent Action Plan are authoritative for all application content. The Update Set XML at [`../../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml`](../../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml) is the authoritative source for every table name, column name, column type, mandatory flag, choice value, role name, ACL name, Script Include class name, method name, REST operation path and system-property key cited below; the identifiers used here match those records character for character. [`../access-control.md`](../access-control.md) is authoritative for the twenty-one role-by-field outcomes, and [`../api-reference.md`](../api-reference.md) for the six resource paths, the pagination contract and the exact error bodies. This guide agrees with all three and introduces no third spelling. No variant spelling of any identifier is valid.

This document carries **no rationale**. It states what to build and how to build it, suite by suite, test by test, step by step. Every decision behind these suites, every alternative considered and every risk each carries is recorded in [`../../../docs/decisions/DECISION_LOG.md`](../../../docs/decisions/DECISION_LOG.md), which is the single source of truth for "why". Three points in this procedure depart from a literal reading of the requirements — the three impersonated users being **created at run time by test setup steps** rather than shipped in the Update Set, the rate-limit counter row being **pre-seeded at the configured budget** so a single request trips the limit, and the **two separate provenance surfaces** that keep an ATF result label distinct from a scheduled run-summary record. Each is stated below as a build mechanic and cross-referenced to that log. None is argued here.

Operational warnings **are** in scope for this guide and are marked as such. The eight warnings under [Operational warnings](#operational-warnings) are load-bearing and must not be skipped. Two of them describe failures that are completely silent, in the sense that every test reports `success` while the property under test was never exercised at all.

## Referenced documents

This guide is executable on its own. Every suite, every test, every step, every input value, the assembly order, the run procedure and the verification are stated here in full. An operator needs no other file to build and run the suites.

**Every document linked from this guide is delivered and readable**, so no link is a forward reference; each one is an in-scope artifact of this deliverable package. Nothing in this guide depends on reading another document first.

| Document | What this guide takes from it |
| --- | --- |
| [`../../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml`](../../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml) | **Authoritative** for every identifier this guide cites: the ten table names, the fifty-three entity columns and their mandatory flags, the sixty-three entity choice values, the three role names, the seven field-level ACL names, the nine Script Include class names and their method signatures, the thirty-one REST operation paths, and the thirteen system-property keys. |
| [`../access-control.md`](../access-control.md) | The 3 x 7 role-by-field matrix this guide asserts cell by cell, the secured read path, the omit-not-nulled rule, and the impersonation requirement together with the reviewer entry that owns it. |
| [`../api-reference.md`](../api-reference.md) | The six logical resources and the nested sub-resource, the physical base path, the pagination contract and its envelope members, the exact 429 and 500 bodies, the result ordering per operation, and the Script Include call graph that serves as the rename-impact list. |
| [`../data-model.md`](../data-model.md) | The fifty-three columns with types and lengths, the fourteen mandatory columns, all eleven choice columns and their members, the `Investor.type` asymmetry, and the type-refusal rules the CRUD suites assert against. |
| [`../validation-gates.md`](../validation-gates.md) | The post-commit gates of precondition 4, including the eleven-gate core, and `GATE-SEC-01` and `GATE-SEC-02`, whose table posture determines how the record steps in this guide must be scoped. |
| [`../deployment-runbook.md`](../deployment-runbook.md) | The import sequence that commits the Update Set, the assertion of the ATF prerequisite before import, and the definition of [what counts as a scheduled run](../deployment-runbook.md#what-counts-as-a-scheduled-run). |
| [`02-flow-crunchbase-ingestion.md`](02-flow-crunchbase-ingestion.md) | The `Crunchbase Ingestion` flow under test: its eight steps, its cadence guard, its run-identifier format, its mandatory sets and its run-summary write. |
| [`03-flow-linkedin-ingestion.md`](03-flow-linkedin-ingestion.md) | The `LinkedIn Ingestion` flow under test, and the shared startup deduplication key that lets a LinkedIn founder attach to a Crunchbase startup. |
| [`04-service-portal-pages-and-widgets.md`](04-service-portal-pages-and-widgets.md) | The five portal pages and eight widgets, and the three impersonated users this guide creates that the portal walkthrough also requires. |
| [`06-staging-table-csv-import.md`](06-staging-table-csv-import.md) | The staged fallback rows the two flow tests act on, their six `import_run` tokens and their expected reconciliation counts. |
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
| The two flow tests | The two ingestion flows, the two credential aliases, and the staged rows in `x_bst_startuptrk_ingest_staging` | Guides 01, 02, 03 and 06 |

The flow tests are the binding constraint on the one hop where execution order differs from filename order: they exercise the fallback branch of both flows, and that branch reads `x_bst_startuptrk_ingest_staging`. **The staged rows must exist before this guide runs**, or the two flow tests have no rows to act on and report a processed count of zero.

## Preconditions

Do not begin this guide until every item below holds.

| # | Precondition | How to confirm |
| --- | --- | --- |
| 1 | The Update Set has been uploaded and has reached the `loaded` state. | The `sys_remote_update_set` record shows `state` `loaded`. |
| 2 | The preview has completed with an **empty error-type problem set**. | A read of `sys_update_preview_problem` filtered to this remote update set and `type=error` returns an empty `result` array. Warnings are logged and do not block. |
| 3 | The Update Set has **committed**. | The `sys_remote_update_set` record shows `state` `committed`. |
| 4 | **All eleven post-commit gates of the core gate set have passed.** | The seven entity-table gates `GATE-TBL-01` through `GATE-TBL-07`, the three role-record gates `GATE-ROLE-01` through `GATE-ROLE-03`, and the one scope-record gate `GATE-SCOPE-01`, all recorded `pass` in [`../validation-gates.md`](../validation-gates.md). That document carries sixteen gates in total; these eleven are its core, and the remaining five are `GATE-COL-01` and `GATE-SEC-01` through `GATE-SEC-04`. There is no partial pass. |
| 5 | **ATF execution is enabled on the instance and you hold a test-designer role.** | See [Instance prerequisite: ATF execution must be enabled](#instance-prerequisite-atf-execution-must-be-enabled) immediately below. This is the hard prerequisite of this guide. Without it **every suite here is unrunnable and the coverage gate cannot be evaluated at all**. |
| 6 | Guides 01, 02, 03, 04 and 06 are complete. | The two credential aliases exist, both flows are `Published` and `Active`, the portal resolves, and `x_bst_startuptrk_ingest_staging` holds the sixty-five staged rows described in [`06-staging-table-csv-import.md`](06-staging-table-csv-import.md). |
| 7 | The seven entity tables carry all **fifty-three** dictionary columns. | `GATE-COL-01` recorded `pass`. Column counts per table: `x_bst_startuptrk_startup` 12, `x_bst_startuptrk_founder` 6, `x_bst_startuptrk_executive` 6, `x_bst_startuptrk_investor` 6, `x_bst_startuptrk_fundinground` 8, `x_bst_startuptrk_jobposting` 9, `x_bst_startuptrk_newsarticle` 6. |
| 8 | The nine Script Includes this guide calls into are on the instance. | `sys_script_include` carries `AppProperties`, `RestQueryHelper`, `RestResponseBuilder`, `RateLimitService`, `StartupSearchService`, `InvestorPortfolioService`, `IngestionLogger`, `IngestionMapper` and `PrivacyRetentionService`, all in the `x_bst_startuptrk` scope. |
| 9 | The three business rules are on the instance and **active**. | `sys_script` carries `Trim and validate startup`, `Recalculate investor portfolio on funding round` and `Recalculate investor portfolio on round investor link`, all `active` true, all in the `x_bst_startuptrk` scope. |
| 10 | The rate-limit counter table exists with all **five** of its columns. | `x_bst_startuptrk_rate_limit_counter` carries `window_key`, `caller`, `api_resource`, `window_start` and `request_count`. The REST suite's 429 assertion writes to this table. |
| 11 | You hold the platform `admin` role. | Required to create the three test users, to read `sys_user_has_role`, and to reach the Automated Test Framework modules. Note this is the **platform** administrator role, which is **not** the scoped `x_bst_startuptrk.admin` role; the two are different records and both are needed. |
| 12 | You are working in the `x_bst_startuptrk` application scope. | The application picker reads **Boston Startup Tracker**. Every test and every suite this guide creates must carry that scope — see [Naming and scope conventions](#naming-and-scope-conventions), where the reason this is a build constraint rather than a preference is stated as a mechanic. |
| 13 | No other operator is running suites on this instance. | ATF serialises execution against a single runner. A concurrent run competes for the runner and for the impersonation context, and the two flow tests write to the same staging rows. |

### Why this guide exists rather than more Update Set XML

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

If a run reports that the test runner is unavailable or appears to hang without producing a result, the client-side test runner is not attached. Open **All** > **Automated Test Framework** > **Run Client Test Runner** in a second browser tab and leave it open for the duration of the run. Every step in this guide is a server-side or REST step, so the runner window needs no interaction — but it must be present for the run to be scheduled.

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

**The application scope is a build constraint, not a preference.** All ten tables ship with `access` `package_private` and with `read_access`, `create_access`, `update_access`, `delete_access` and `ws_access` all false — the posture `GATE-SEC-01` and `GATE-SEC-02` verify. A test built in the **Global** scope is an out-of-scope caller, and its record steps are refused by that posture before any ACL is consulted. Where a record step is still refused after the scope is correct, the in-scope route is a **Run Server Side Script** step, which compiles in the test's own scope. The REST suite is unaffected either way, because it calls the Scripted REST API at `/api/x_bst_startuptrk/v1/` rather than the Table API — `ws_access` false is exactly why the Table API is not an option for these tables.

## What this guide builds

| Artifact | Count | Table |
| --- | --- | --- |
| Test suites | **10** | `sys_atf_test_suite` |
| Tests | **36** | `sys_atf_test` |
| Test steps | approximately 400 | `sys_atf_step` |
| Suite test membership rows | 36 | `sys_atf_test_suite_test` |
| New step configurations | **0** | `sys_atf_step_config` — every step below uses a stock configuration |

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

## Suites 1 to 7 — table CRUD

Seven suites, one per entity table, one test in each. Every test follows the same twelve-to-fifteen-step skeleton below; the per-table sections that follow give the values that differ.

Build the skeleton once for `x_bst_startuptrk_startup`, confirm it passes, then copy the test six times through **Copy Test** on the test form and substitute the per-table values. Copying carries the steps with it.

### The shared CRUD skeleton

| Step | Step configuration | Category | Inputs |
| --- | --- | --- | --- |
| 5 | **Create a User** | Server - Independent | `first_name` = `BST ATF`, `last_name` = `admin`, `roles` = **exactly** `x_bst_startuptrk.admin`, `groups` empty, `impersonate` false. Created at run time; see [Technique (a)](#technique-a--impersonation) for the full input list. |
| 10 | **Impersonate** | Server - Independent | `user` = the step 5 output. Writes to all seven tables are granted to `x_bst_startuptrk.admin` alone, so a test that omits this step fails at step 30 for the wrong reason. |
| 20 | **Record Insert** | Server - Independent | The parent fixture, on tables that carry a mandatory `startup` reference. `table` = `x_bst_startuptrk_startup`; `field_values` = `name`, `headquarters_location`, `active` `true`; `enforce_security` = **true**; `assert_type` = **Record successfully inserted**. Omit this step in suite 1 and suite 4. |
| 30 | **Record Insert** | Server - Independent | The subject record. `table` = the table under test; `field_values` = every mandatory column plus one declared member of each choice column under test; `enforce_security` = **true**; `assert_type` = **Record successfully inserted**. Bind any reference to the step 20 output `record_id`. |
| 40 | **Record Validation** | Server - Independent | `table` = the table under test; `record_id` = the step 30 output `record_id`; `field_values` = conditions asserting each value written at step 30 was stored verbatim, including the exact choice string; `enforce_security` = **true**; `assert_type` = **Record successfully validated**. |
| 50 | **Record Query** | Server - Independent | `table` = the table under test; `field_values` = a condition matching the step 30 record on its display column; `enforce_security` = **true**; `assert_type` = **There is at least one record matching the query**. |
| 60 | **Record Update** | Server - Independent | `table` = the table under test; `record_id` = the step 30 output; `field_values` = one non-choice column changed plus a **second** declared member of the choice column; `enforce_security` = **true**; `assert_type` = **Record successfully updated**. |
| 70 | **Record Validation** | Server - Independent | Asserts the step 60 values are stored and the untouched columns are unchanged. `assert_type` = **Record successfully validated**. |
| 80 | **Record Insert** | Server - Independent | Mandatory-field assertion, first mandatory column. `field_values` = every mandatory column **except** this one; `enforce_security` = **true**; `assert_type` = **Record was not inserted**. |
| 90 | **Record Insert** | Server - Independent | Mandatory-field assertion, second mandatory column, same pattern. Present on every table except `x_bst_startuptrk_investor`, which has one mandatory column. |
| 100 | **Run Server Side Script** | Server - Independent | Choice-value assertion. Calls the single specified normaliser and asserts the specified outcome per choice column. The script pattern is given under [The choice-value assertion](#the-choice-value-assertion). |
| 110 | **Record Delete** | Server - Independent | `table` = the table under test; `record_id` = the step 30 output; `enforce_security` = **true**; `assert_type` = **Record successfully deleted**. |
| 120 | **Record Query** | Server - Independent | Re-queries the step 50 condition; `assert_type` = **No records match the query**. Confirms the delete took effect rather than merely reporting success. |

No teardown step is required, and none is added. ATF rolls back the data a test creates when the test finishes, so the fixture at step 20 and the subject record at step 30 do not persist. That rollback is also why [Technique (c)](#technique-c--provenance-labelling) treats an in-test provenance write as a separate evidence surface from a scheduled one.

`enforce_security` is **true** on every record step above. With it false the step runs unrestricted, step 30 succeeds regardless of the ACLs, and the suite reports `success` while proving nothing about the access-control layer. It is set true here for the same reason it is set true in suite 8, where the entire assertion depends on it.

### The choice-value assertion

A value outside a choice list is handled by the specified normaliser, `IngestionMapper.normaliseChoice()`, whose contract is fixed in [`../data-model.md`](../data-model.md) and whose behaviour splits on whether the target list declares an `Other` member:

| Case | Specified outcome |
| --- | --- |
| Exact match against a declared member | Stored as supplied. |
| Case-insensitive match against a declared member | Stored using the choice list's **own** spelling — `vp engineering` is stored as `VP Engineering`. |
| No match, list **declares** `Other` | Stored as `Other`, and an `IngestionMapper` unmatched-choice event is logged naming the column and the supplied value. |
| No match, list **does not declare** `Other` | **Left unwritten**, and the same event is logged. Left unwritten is not the same as emptied: on an insert the column is empty, and on an update the previously stored value survives. |

**Five of the eleven choice columns declare `Other` and six do not.** The step 100 script asserts the correct branch for every choice column on the table under test. Note that the physical table name and the normaliser's record type are **not** the same string for two of the seven tables:

| # | Physical column | Normaliser key | Declares `Other` | Members |
| --: | --- | --- | --- | --: |
| 1 | `x_bst_startuptrk_startup.industry` | `startup.industry` | **Yes** | 6 |
| 2 | `x_bst_startuptrk_startup.funding_stage` | `startup.funding_stage` | No | 8 |
| 3 | `x_bst_startuptrk_startup.employee_count_range` | `startup.employee_count_range` | No | 5 |
| 4 | `x_bst_startuptrk_founder.title` | `founder.title` | **Yes** | 5 |
| 5 | `x_bst_startuptrk_executive.title` | `executive.title` | **Yes** | 6 |
| 6 | `x_bst_startuptrk_investor.type` | `investor.type` | No | 5 |
| 7 | `x_bst_startuptrk_investor.focus_areas` | `investor.focus_areas` | **Yes** | 6 |
| 8 | `x_bst_startuptrk_fundinground.round_type` | `funding_round.round_type` | No | 8 |
| 9 | `x_bst_startuptrk_jobposting.department` | `job_posting.department` | **Yes** | 6 |
| 10 | `x_bst_startuptrk_jobposting.remote_type` | `job_posting.remote_type` | No | 3 |
| 11 | `x_bst_startuptrk_jobposting.seniority` | `job_posting.seniority` | No | 5 |

`x_bst_startuptrk_investor.focus_areas` is the only **multi-choice** column, and the normaliser routes it through a multi-value path that normalises each member independently. Assert it with a two-member input where one member matches and one does not.

The normaliser is addressed by **record type**, not by physical table name. Its signature is `normaliseChoice(runId, recordType, field, value)`, and the six record types are `startup`, `founder`, `executive`, `investor`, `funding_round` and `job_posting`. Its internal choice map is keyed `<recordType>.<field>`, so `startup.industry` and `funding_round.round_type` are the lookup keys — not the scope-prefixed table names.

Use this script shape at step 100, substituting the record type, the columns and the expectations. Set **Jasmine version** to the value the field defaults to.

```javascript
(function(outputs, steps, params, stepResult, assertEqual) {
    var RECORD_TYPE = 'startup';        // not the physical table name
    var RUN = 'atf-choice-' + new GlideDateTime().getNumericValue();

    var mapper = new IngestionMapper();
    mapper.log().reset(RUN);            // clear the counters so they measure this step only

    // Case-insensitive match resolves to the choice list's OWN spelling.
    assertEqual({
        name: 'industry accepts a case-insensitive member',
        shouldbe: 'Fintech',
        value: mapper.normaliseChoice(RUN, RECORD_TYPE, 'industry', 'fintech')
    });

    // No match, and this list DECLARES Other, so the value coerces to Other.
    assertEqual({
        name: 'industry coerces an unmatched value to Other',
        shouldbe: 'Other',
        value: mapper.normaliseChoice(RUN, RECORD_TYPE, 'industry', 'Quantum Widgets')
    });

    // No match on a list with NO Other member returns an empty string. normaliseChoices()
    // then removes the key from the payload, which is what "left unwritten" means.
    assertEqual({
        name: 'funding_stage leaves an unmatched value unwritten',
        shouldbe: '',
        value: mapper.normaliseChoice(RUN, RECORD_TYPE, 'funding_stage', 'Series Q')
    });

    // Both unmatched branches must be LOGGED, not silently applied.
    var events = mapper.log().getEvents().filter(function(e) {
        return e.event === 'choice_unmatched';
    });
    assertEqual({ name: 'two choice_unmatched events logged', shouldbe: 2, value: events.length });
    assertEqual({ name: 'unmatched counter agrees', shouldbe: 2,
                  value: mapper.log().counters().unmatched });

    stepResult.setOutputMessage('Choice normalisation asserted for record type ' +
        RECORD_TYPE + '; unmatched=' + mapper.log().counters().unmatched);
    return true;
})(outputs, steps, params, stepResult, assertEqual);
```

The `choice_unmatched` event is recorded at **warn** severity and carries the record type, the field, the supplied value and an `outcome` member reading either `stored as Other` or `left unwritten`. Assert the outcome string as well as the count when a test needs to distinguish the two branches.

**Do not add an `Other` member to any of the six lists that lack one.** The delivered `sys_choice` inventory is exactly the sixty-three entity choice values; adding a member changes the schema the CRUD suites assert against and breaks `GATE-COL-01`.

### Suite 1 — `BST CRUD suite — startup`

One test, `BST CRUD — startup`. Table `x_bst_startuptrk_startup`, 12 columns, display column `name`. Step 20 is omitted; this table has no parent.

| Skeleton step | Value for this table |
| --- | --- |
| 30 insert | `name` = `ATF Startup Alpha`, `headquarters_location` = `Boston, MA`, `active` = `true`, `industry` = `Fintech`, `funding_stage` = `Seed`, `employee_count_range` = `11-50`, `founded_year` = `2021` |
| 40 validation | `name` `is` `ATF Startup Alpha`; `headquarters_location` `is` `Boston, MA`; `active` `is` `true`; `industry` `is` `Fintech`; `funding_stage` `is` `Seed`; `employee_count_range` `is` `11-50` |
| 50 query | `name` `is` `ATF Startup Alpha` |
| 60 update | `description` = `Updated by ATF`, `industry` = `SaaS`, `funding_stage` = `Series A` |
| 80 mandatory | `name` omitted, `headquarters_location` and `active` supplied — **Record was not inserted** |
| 90 mandatory | `headquarters_location` omitted, `name` and `active` supplied — **Record was not inserted** |
| 100 choice | `industry` (declares `Other`), `funding_stage` and `employee_count_range` (do not) |

Two additions specific to this table, appended after step 120:

| Step | Step configuration | Purpose |
| --- | --- | --- |
| 130 | **Record Insert** then **Record Validation** | The third mandatory column, `active`, is a true/false column carrying a default of `true`, so it cannot be left blank in the way `name` and `headquarters_location` can. Assert its **default** instead: insert with `name` and `headquarters_location` only, then validate `active` `is` `true`. |
| 140 | **Run Server Side Script** | Cascade assertion. Insert a startup, insert one child in each of the five tables that carry a mandatory `startup` reference, delete the startup, then assert every child row is gone. This is the cascade-delete rule that keeps `portfolio_count` from counting rounds belonging to a deleted startup. |

The startup inclusion criteria are **not** asserted here. They are a query filter, not a table constraint: a record failing them is stored normally and is excluded only from portal-facing and non-administrative list queries. Their assertion belongs to the `/startups` test in [suite 9](#suite-9--bst-rest-suite--resources) and to the portal walkthrough in [`04-service-portal-pages-and-widgets.md`](04-service-portal-pages-and-widgets.md).

### Suite 2 — `BST CRUD suite — founder`

One test, `BST CRUD — founder`. Table `x_bst_startuptrk_founder`, 6 columns, display column `name`. Step 20 creates the parent startup.

| Skeleton step | Value for this table |
| --- | --- |
| 30 insert | `name` = `ATF Founder Alpha`, `startup` = step 20 `record_id`, `title` = `CEO`, `bio` = `Seeded by ATF` |
| 40 validation | `name` `is` `ATF Founder Alpha`; `startup` `is` the step 20 record; `title` `is` `CEO` |
| 50 query | `name` `is` `ATF Founder Alpha` |
| 60 update | `linkedin_url` = `https://example.invalid/in/atf-founder`, `title` = `Co-Founder` |
| 80 mandatory | `name` omitted, `startup` supplied — **Record was not inserted** |
| 90 mandatory | `startup` omitted, `name` supplied — **Record was not inserted** |
| 100 choice | `title` — declares `Other`; assert `cto` resolves to `CTO` and `Chief Vibes Officer` coerces to `Other` |

`contact_email` is written at step 30 but **not** asserted here. It is a premium field, and its read outcome per role is asserted in [suite 8](#suite-8--bst-acl-suite--premium-fields-by-role), cells 3.1 to 3.3.

### Suite 3 — `BST CRUD suite — executive`

One test, `BST CRUD — executive`. Table `x_bst_startuptrk_executive`, 6 columns, display column `name`. Step 20 creates the parent startup. The column set matches Founder; only the `title` choice list differs, and the two tables remain separate as specified.

| Skeleton step | Value for this table |
| --- | --- |
| 30 insert | `name` = `ATF Executive Alpha`, `startup` = step 20 `record_id`, `title` = `VP Engineering` |
| 40 validation | `name` `is` `ATF Executive Alpha`; `startup` `is` the step 20 record; `title` `is` `VP Engineering` |
| 50 query | `name` `is` `ATF Executive Alpha` |
| 60 update | `bio` = `Updated by ATF`, `title` = `Head of Product` |
| 80 mandatory | `name` omitted, `startup` supplied — **Record was not inserted** |
| 90 mandatory | `startup` omitted, `name` supplied — **Record was not inserted** |
| 100 choice | `title` — declares `Other`; assert `vp engineering` resolves to `VP Engineering` and `Grand Vizier` coerces to `Other` |

### Suite 4 — `BST CRUD suite — investor`

One test, `BST CRUD — investor`. Table `x_bst_startuptrk_investor`, 6 columns, display column `name`. Step 20 is omitted; this table has no parent. Step 90 is omitted; `name` is the only mandatory column.

| Skeleton step | Value for this table |
| --- | --- |
| 30 insert | `name` = `ATF Capital Partners`, `type` = `VC`, `focus_areas` = `Fintech,SaaS` |
| 40 validation | `name` `is` `ATF Capital Partners`; `type` `is` `VC`; `portfolio_count` `is` `0` |
| 50 query | `name` `is` `ATF Capital Partners` |
| 60 update | `website` = `https://example.invalid/atf-capital`, `type` = `Accelerator` |
| 80 mandatory | `name` omitted — **Record was not inserted** |
| 100 choice | `type` — **does not** declare `Other`; assert `vc` resolves to `VC` and `Sovereign Wealth` is left unwritten and logged. `focus_areas` — declares `Other`. |

Two additions specific to this table, appended after step 120:

| Step | Step configuration | Purpose |
| --- | --- | --- |
| 130 | **Record Update** | `portfolio_count` is a read-only derived column with a default of `0`. Attempt to set it to `99` and assert the stored value remains the derived one, not `99`. |
| 140 | **Run Server Side Script** | The `portfolio_count` derivation. Create one startup, one funding round with this investor as `lead_investor`, and one `x_bst_startuptrk_m2m_round_investor` row linking the same investor to a **second** round of the **same** startup. Then assert `portfolio_count` is **1**, not 2 — the two traversal paths are unioned on distinct startup before counting. Call `InvestorPortfolioService` for the recalculation rather than reimplementing it. |

**`x_bst_startuptrk_investor.type` is the choice asymmetry.** Its list is `VC`, `Angel`, `PE`, `Corporate`, `Accelerator` and declares **no** `Other`. An unmatched investor type is therefore left unwritten and logged, and because `type` is **not** a mandatory column, **the record itself still inserts**. Rejection is reserved for a record missing a mandatory field. Step 100 must assert exactly that: the event is logged, the column is empty, and the row exists.

### Suite 5 — `BST CRUD suite — fundinground`

One test, `BST CRUD — fundinground`. Table `x_bst_startuptrk_fundinground`, 8 columns. Step 20 creates the parent startup, and a second **Record Insert** at step 25 creates an investor for `lead_investor`.

| Skeleton step | Value for this table |
| --- | --- |
| 30 insert | `startup` = step 20 `record_id`, `round_date` = `2025-06-30`, `round_type` = `Series A`, `amount_usd` = `12000000`, `lead_investor` = step 25 `record_id`, `source_url` = `https://example.invalid/round/atf` |
| 40 validation | `startup` `is` the step 20 record; `round_date` `is` `2025-06-30`; `round_type` `is` `Series A`; `lead_investor` `is` the step 25 record |
| 50 query | `startup` `is` the step 20 record |
| 60 update | `valuation_usd` = `90000000`, `round_type` = `Series B` |
| 80 mandatory | `startup` omitted, `round_date` supplied — **Record was not inserted** |
| 90 mandatory | `round_date` omitted, `startup` supplied — **Record was not inserted** |
| 100 choice | `round_type` — **does not** declare `Other`; assert `series a` resolves to `Series A` and `Series Q` is left unwritten and logged |

One addition specific to this table, appended after step 120:

| Step | Step configuration | Purpose |
| --- | --- | --- |
| 130 | **Run Server Side Script** | `participating_investors` is a read-only list column materialised from `x_bst_startuptrk_m2m_round_investor`, not written directly. Insert two m2m rows against one round and assert the column resolves to both investors, and that a direct write to it does not take. `lead_investor` is a first-class reference and stays distinct from the participant set. |

`amount_usd` and `valuation_usd` are written at step 30 and step 60 but **not** asserted for readability here. Both are premium fields, asserted per role in [suite 8](#suite-8--bst-acl-suite--premium-fields-by-role), cells 6.1 to 6.3 and 7.1 to 7.3.

### Suite 6 — `BST CRUD suite — jobposting`

One test, `BST CRUD — jobposting`. Table `x_bst_startuptrk_jobposting`, 9 columns, display column `title`. Step 20 creates the parent startup. This table carries **three** choice columns, only one of which declares `Other`.

| Skeleton step | Value for this table |
| --- | --- |
| 30 insert | `startup` = step 20 `record_id`, `title` = `ATF Staff Engineer`, `department` = `Engineering`, `remote_type` = `Hybrid`, `seniority` = `Senior`, `location` = `Boston, MA`, `posted_date` = `2026-01-15` |
| 40 validation | `title` `is` `ATF Staff Engineer`; `department` `is` `Engineering`; `remote_type` `is` `Hybrid`; `seniority` `is` `Senior`; `active` `is` `true` |
| 50 query | `title` `is` `ATF Staff Engineer` |
| 60 update | `active` = `false`, `department` = `Product`, `seniority` = `Lead` |
| 80 mandatory | `startup` omitted, `title` supplied — **Record was not inserted** |
| 90 mandatory | `title` omitted, `startup` supplied — **Record was not inserted** |
| 100 choice | `department` declares `Other`, so `platform engineering` coerces to `Other`. `remote_type` and `seniority` do **not**, so `Anywhere` and `Principal` are left unwritten and logged. |

`active` carries a default of `true` and is **not** mandatory on this table, unlike `x_bst_startuptrk_startup.active`. Step 40 asserts the default applied without being supplied.

### Suite 7 — `BST CRUD suite — newsarticle`

One test, `BST CRUD — newsarticle`. Table `x_bst_startuptrk_newsarticle`, 6 columns, display column `title`. Step 20 creates the parent startup. This table has **no** choice column, so step 100 is replaced.

| Skeleton step | Value for this table |
| --- | --- |
| 30 insert | `startup` = step 20 `record_id`, `title` = `ATF covers Startup Alpha`, `source` = `ATF Wire`, `published_date` = `2026-02-01`, `url` = `https://example.invalid/news/atf` |
| 40 validation | `title` `is` `ATF covers Startup Alpha`; `startup` `is` the step 20 record; `source` `is` `ATF Wire`; `published_date` `is` `2026-02-01` |
| 50 query | `title` `is` `ATF covers Startup Alpha` |
| 60 update | `summary` = `Updated by ATF` |
| 80 mandatory | `startup` omitted, `title` supplied — **Record was not inserted** |
| 90 mandatory | `title` omitted, `startup` supplied — **Record was not inserted** |
| 100 replaced | **Run Server Side Script** asserting `published_date` accepts the specified date forms — `YYYY-MM-DD`, a full ISO 8601 timestamp whose date part is taken, and a ten-digit or thirteen-digit epoch — and that a value which is not a real calendar day is refused. |

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

### The step sequence for a `*.1` cell — administrator, expected to read

Seven tests use this shape. The role under test is `x_bst_startuptrk.admin`, which is also the role that writes the fixtures, so one user serves both purposes.

| Step | Step configuration | Category | Inputs |
| --- | --- | --- | --- |
| 5 | **Create a User** | Server - Independent | `first_name` = `BST ATF`, `last_name` = `admin`, `roles` = **exactly** `x_bst_startuptrk.admin`, `groups` empty, `impersonate` false. Full input list under [Technique (a)](#technique-a--impersonation). |
| 8 | **Run Server Side Script** | Server - Independent | Role-set verification for the step 5 user: exactly one scoped role, and none of the elevated platform roles. |
| 10 | **Impersonate** | Server - Independent | `user` = the step 5 output. |
| 20 | **Record Insert** | Server - Independent | The parent fixture, on the tables that need one. `enforce_security` = **true**; `assert_type` = **Record successfully inserted**. Omit for fields 1, 2 and 5. |
| 30 | **Record Insert** | Server - Independent | The subject record, with the premium field **populated to a known non-empty value**. `enforce_security` = **true**; `assert_type` = **Record successfully inserted**. |
| 50 | **Run Server Side Script** | Server - Independent | The read assertion. Asserts the element-level read check returns **true**, that the serialised object **carries** the key, and that the value equals what step 30 wrote. |

### The step sequence for a `*.2` cell — premium user, expected to read

Seven tests use this shape. Two users are needed: the administrator writes the fixtures, then the premium user attempts the read.

| Step | Step configuration | Category | Inputs |
| --- | --- | --- | --- |
| 5 | **Create a User** | Server - Independent | `roles` = **exactly** `x_bst_startuptrk.admin`. The fixture writer. |
| 8 | **Run Server Side Script** | Server - Independent | Role-set verification for the step 5 user. |
| 10 | **Impersonate** | Server - Independent | `user` = the step 5 output. |
| 20 | **Record Insert** | Server - Independent | Parent fixture where required; `enforce_security` = **true**. Omit for fields 1, 2 and 5. |
| 30 | **Record Insert** | Server - Independent | Subject record with the premium field populated; `enforce_security` = **true**; `assert_type` = **Record successfully inserted**. |
| 35 | **Create a User** | Server - Independent | `last_name` = `premium`, `roles` = **exactly** `x_bst_startuptrk.premium_user`, `groups` empty. |
| 38 | **Run Server Side Script** | Server - Independent | Role-set verification for the step 35 user. |
| 40 | **Impersonate** | Server - Independent | `user` = the step 35 output. |
| 50 | **Run Server Side Script** | Server - Independent | The read assertion, as for a `*.1` cell. |

### The step sequence for a `*.3` cell — base user, expected to be DENIED

Seven tests use this shape. It is identical to a `*.2` cell except that step 35 grants `x_bst_startuptrk.user` and step 50 carries the denial assertion instead of the read assertion.

| Step | Step configuration | Category | Inputs |
| --- | --- | --- | --- |
| 5 | **Create a User** | Server - Independent | `roles` = **exactly** `x_bst_startuptrk.admin`. The fixture writer. |
| 8 | **Run Server Side Script** | Server - Independent | Role-set verification for the step 5 user. |
| 10 | **Impersonate** | Server - Independent | `user` = the step 5 output. |
| 20 | **Record Insert** | Server - Independent | Parent fixture where required; `enforce_security` = **true**. Omit for fields 1, 2 and 5. |
| 30 | **Record Insert** | Server - Independent | Subject record with the premium field populated; `enforce_security` = **true**; `assert_type` = **Record successfully inserted**. |
| 35 | **Create a User** | Server - Independent | `last_name` = `base`, `roles` = **exactly** `x_bst_startuptrk.user`, `groups` empty. This is the user that must be denied. |
| 38 | **Run Server Side Script** | Server - Independent | Role-set verification for the step 35 user. **This step is what makes the denial meaningful**; a user that silently acquired `admin` turns the cell into a false pass. |
| 40 | **Impersonate** | Server - Independent | `user` = the step 35 output, holding `x_bst_startuptrk.user` and nothing else. |
| 50 | **Run Server Side Script** | Server - Independent | The denial assertion, script below. Asserts the element-level read check returns **false**, that the serialised object **does not carry the key at all**, and — as a control — that a non-premium column on the same record still returns a value. |

Use this script at step 50 of a `*.3` cell, substituting the table, the premium field and the control column:

```javascript
(function(outputs, steps, params, stepResult, assertEqual) {
    var TABLE   = 'x_bst_startuptrk_startup';
    var FIELD   = 'total_funding_usd';
    var CONTROL = 'name';

    var builder = new RestResponseBuilder();
    var gr = new GlideRecordSecure(TABLE);

    if (!gr.get(steps('30').record_id)) {
        stepResult.setFailed('Record not readable under x_bst_startuptrk.user. ' +
            'The table-level read ACL of Layer 1 is not granting, so the field ACL never evaluates.');
        return false;
    }

    // 1. The field-level read check must deny.
    assertEqual({
        name: FIELD + ' element read is denied',
        shouldbe: false,
        value: builder.canRead(gr, FIELD)
    });

    // 2. Omitted, NOT nulled. The serialised object must not carry the key at all.
    var body = builder.serialize(gr, [FIELD, CONTROL]);
    assertEqual({
        name: FIELD + ' key is absent from the response object',
        shouldbe: false,
        value: Object.prototype.hasOwnProperty.call(body, FIELD)
    });

    // 3. Control: the denial is field-scoped, so a non-premium column still returns a value.
    assertEqual({
        name: CONTROL + ' is still readable, proving Layer 1 granted',
        shouldbe: true,
        value: body[CONTROL] !== undefined && body[CONTROL] !== ''
    });

    stepResult.setOutputMessage(FIELD + ' omitted for x_bst_startuptrk.user; ' +
        CONTROL + ' readable; both ACL layers load-bearing.');
    return true;
})(outputs, steps, params, stepResult, assertEqual);
```

Assertion 2 is the one that matters, and it is not pedantry. **The secured read returns an empty string for a denied field, not an error.** A test that checked the value were falsy, empty, or `null` would therefore pass against a response carrying `"total_funding_usd": ""` — which is precisely the nulled behaviour the requirements forbid. Only a `hasOwnProperty` check distinguishes omitted from nulled. Use `Object.prototype.hasOwnProperty.call(body, FIELD)` and assert it is `false`.

Assertion 3 is the second half of the same proof. Both the table-level read ACL and the field-level read ACL must grant for a premium field to be readable, so the two failure modes are opposite and both silent: with the table-level ACL missing, nothing is readable and the field ACLs never evaluate at all; with the field-level ACL missing, everything is readable because the platform falls back to the table-level grant. Asserting the control column returns a value while the premium key is absent proves Layer 1 granted and Layer 3 denied, which is the only combination that satisfies the requirement.

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

`Send REST Request - Inbound` performs a genuine inbound HTTP call and establishes its **own** session. An `Impersonate` step earlier in the test does **not** carry into it, so the request must present credentials of its own through the step's **Basic authentication** input.

Build these two records **once, by hand, as a precondition** — they are instance provisioning, like the ATF runner property, and they are correctly absent from the delivered Update Set:

| Record | Table | Values |
| --- | --- | --- |
| REST caller user | `sys_user` | `user_name` = `bst.atf.rest`, `first_name` = `BST ATF`, `last_name` = `REST caller`, a password you set, **`web_service_access_only` false**, and exactly one role: **`x_bst_startuptrk.user`**. No platform `admin`, no `security_admin`, no `snc_internal` beyond what the platform assigns by default. |
| Basic Auth Configuration | `sys_auth_profile_basic` | `name` = `BST ATF REST caller`, `username` = `bst.atf.rest`, `password` = the password above. This is the record the step's **Basic authentication** field references. |

The REST caller holds the **base** role deliberately. All thirteen read operations are granted to all three roles by the `Boston Startup Tracker API read` endpoint ACL and by the Layer 1 table-read ACLs, so every `GET` in this suite succeeds — and because the caller is the base role, the success-shape assertion in each test can additionally confirm end-to-end over HTTP that the premium keys are **absent** from the response body. The six tests assert response shape, pagination and the 429 contract, none of which is role-differentiated, so no administrator credential is needed anywhere in this suite. Mutations are not exercised here.

This persistent, password-holding caller is distinct from the three run-time impersonation users of [Technique (a)](#technique-a--impersonation), which need no password because `Impersonate` needs none. The split is recorded in [`../../../docs/decisions/DECISION_LOG.md`](../../../docs/decisions/DECISION_LOG.md).

### The shared REST step sequence

Each of the six tests follows this shape. Substitute the resource path, the fixture table and the `api_resource` token.

| Step | Step configuration | Category | Inputs |
| --- | --- | --- | --- |
| 5 | **Create a User** | Server - Independent | `roles` = **exactly** `x_bst_startuptrk.admin`, so the fixtures can be written. |
| 10 | **Impersonate** | Server - Independent | `user` = the step 5 output. |
| 20 | **Run Server Side Script** | Server - Independent | Seed **three** records on the table under test, with any parent fixture they require, so a page size of 2 yields more than one page. For `/startups` seed records that **satisfy** the inclusion criteria — `active` `true` and a `headquarters_location` containing `Boston` or `Cambridge, MA` — plus one that **fails** them. |
| 30 | **Send REST Request - Inbound** | Server - REST | `http_method` = **GET**; `end_point` = the resource path; `basic_auth` = `BST ATF REST caller`; `query_params` = `sysparm_limit` `2`, `sysparm_offset` `0`. |
| 40 | **Assert Status Code** | Server - REST | `response_operation` = **is**; `status_code` = `200`. |
| 50 | **Assert Response JSON Payload Is Valid** | Server - REST | No inputs. Fails the test if the body is not parseable JSON. |
| 60 | **Assert JSON Response Payload Element** | Server - REST | `element_name` = `total_count`; `response_operation` = **is not empty**. |
| 70 | **Run Server Side Script** | Server - Independent | The success-shape and page-one assertions, script below. |
| 80 | **Send REST Request - Inbound** | Server - REST | Page two. Identical to step 30 with `sysparm_offset` `2`. |
| 90 | **Assert Status Code** | Server - REST | `response_operation` = **is**; `status_code` = `200`. |
| 100 | **Run Server Side Script** | Server - Independent | The page-two assertions: `total_count` is **identical** to page one, the returned rows do **not** repeat page one's rows, and `offset` echoes `2`. |
| 110 | **Send REST Request - Inbound** | Server - REST | Bounds check. `query_params` = `sysparm_limit` `9999`. |
| 120 | **Run Server Side Script** | Server - Independent | Asserts the echoed `limit` is clamped to the value of `x_bst_startuptrk.rest.max_limit`, which is `50`, and not `9999`. |
| 130 | **Run Server Side Script** | Server - Independent | Pre-seeds the rate-limit counter row at the configured budget. Script under [Technique (b)](#technique-b--deterministic-429). |
| 140 | **Send REST Request - Inbound** | Server - REST | Identical to step 30. This single call trips the limit. |
| 150 | **Assert Status Code** | Server - REST | `response_operation` = **is**; `status_code` = `429`. |
| 160 | **Assert JSON Response Payload Element** | Server - REST | `element_name` = `error`; `response_operation` = **is**; `element_value` = `rate_limit_exceeded`. |
| 170 | **Run Server Side Script** | Server - Independent | Asserts `retry_after` is present and is a **positive integer**, and that the body carries exactly the two members `error` and `retry_after`. |

The `BST REST — founders` test repeats steps 30 to 120 for the nested path `/api/x_bst_startuptrk/v1/founders/{startup_id}/executives`, substituting the step 20 startup's `sys_id` for `{startup_id}`, and repeats steps 130 to 170 seeding the token `/founders/{startup_id}/executives`. That test therefore runs roughly twice the step count of the other five.

### The success-shape and pagination assertions

Use this script at step 70. The envelope members and the ordering it asserts are fixed by [`../api-reference.md`](../api-reference.md).

```javascript
(function(outputs, steps, params, stepResult, assertEqual) {
    var body = JSON.parse(steps('30').response_body);

    // 1. Envelope shape: result, total_count, limit, offset are always present.
    assertEqual({ name: 'result is an array',   shouldbe: true, value: Array.isArray(body.result) });
    assertEqual({ name: 'limit echoes 2',       shouldbe: 2,    value: parseInt(body.limit, 10) });
    assertEqual({ name: 'offset echoes 0',      shouldbe: 0,    value: parseInt(body.offset, 10) });

    // 2. total_count must AGREE WITH THE PAGE CONTENTS: it counts the whole filtered
    //    set, so it is at least the number of rows on this page, and the page is capped
    //    at the requested limit.
    var total = parseInt(body.total_count, 10);
    assertEqual({ name: 'total_count is a non-negative integer',
                  shouldbe: true, value: !isNaN(total) && total >= 0 });
    assertEqual({ name: 'page size does not exceed the requested limit',
                  shouldbe: true, value: body.result.length <= 2 });
    assertEqual({ name: 'total_count is at least the rows returned',
                  shouldbe: true, value: total >= body.result.length });
    assertEqual({ name: 'a full first page implies more or equal total',
                  shouldbe: true, value: body.result.length < 2 || total >= body.result.length });

    // 3. The caller holds x_bst_startuptrk.user only, so every premium key must be
    //    ABSENT from every row - omitted, not nulled.
    var PREMIUM = ['total_funding_usd', 'institutional_funding_last_5yrs'];
    for (var i = 0; i < body.result.length; i++) {
        for (var p = 0; p < PREMIUM.length; p++) {
            assertEqual({
                name: 'row ' + i + ' omits ' + PREMIUM[p],
                shouldbe: false,
                value: Object.prototype.hasOwnProperty.call(body.result[i], PREMIUM[p])
            });
        }
    }

    outputs.page_one_ids = body.result.map(function(r) { return r.sys_id; }).join(',');
    outputs.total_count  = total;
    stepResult.setOutputMessage('Shape valid; total_count=' + total +
        '; rows=' + body.result.length + '; premium keys omitted.');
    return true;
})(outputs, steps, params, stepResult, assertEqual);
```

Substitute the premium list per resource: `total_funding_usd` and `institutional_funding_last_5yrs` for `/startups`; `contact_email` for `/founders` and for the nested executives path; `aum_usd` for `/investors`; `amount_usd` and `valuation_usd` for `/funding-rounds`. `/jobs` and `/news` carry no premium column, so those two tests assert the envelope and pagination only and skip block 3.

Step 100 closes the pagination assertion by comparing the two pages:

```javascript
(function(outputs, steps, params, stepResult, assertEqual) {
    var pageTwo = JSON.parse(steps('80').response_body);
    var firstIds = String(steps('70').page_one_ids).split(',').filter(String);
    var twoIds = pageTwo.result.map(function(r) { return r.sys_id; });

    // total_count is a property of the filtered set, not of the page, so it must not move.
    assertEqual({ name: 'total_count is stable across pages',
        shouldbe: parseInt(steps('70').total_count, 10),
        value: parseInt(pageTwo.total_count, 10) });
    assertEqual({ name: 'offset echoes 2', shouldbe: 2, value: parseInt(pageTwo.offset, 10) });

    // Deterministic ordering means page two shares no row with page one.
    var overlap = twoIds.filter(function(id) { return firstIds.indexOf(id) !== -1; });
    assertEqual({ name: 'no row repeats across pages', shouldbe: 0, value: overlap.length });

    stepResult.setOutputMessage('Pagination consistent across offsets 0 and 2.');
    return true;
})(outputs, steps, params, stepResult, assertEqual);
```

The no-overlap assertion is only meaningful because every list operation applies a deterministic sort with a `sys_id` ascending tie-breaker: `name` ascending for `/startups`, `/founders`, the nested executives path and `/investors`; `round_date` descending for `/funding-rounds`; `posted_date` descending for `/jobs`; `published_date` descending for `/news`. Seed the step 20 fixtures with **distinct** values in the sort column of the resource under test, or two rows can legitimately tie and the pages may overlap for a reason that is not a defect.

The `BST REST — startups` test carries one further assertion at step 70: the record seeded at step 20 that **fails** the inclusion criteria must **not** appear in `result`, and `total_count` must not count it. The inclusion criteria are a query filter applied identically to the result set and to the count, so a mismatch between the two is a defect in `StartupSearchService` and not in the test.

## Suite 10 — `BST FLOW suite — ingestion`

One suite, **2 tests**, one per flow.

| Test | Flow under test | Entities it writes | Guide |
| --- | --- | --- | --- |
| `BST FLOW — Crunchbase Ingestion` | `Crunchbase Ingestion` | `x_bst_startuptrk_startup`, `x_bst_startuptrk_investor`, `x_bst_startuptrk_fundinground`, `x_bst_startuptrk_m2m_round_investor` | [`02-flow-crunchbase-ingestion.md`](02-flow-crunchbase-ingestion.md) |
| `BST FLOW — LinkedIn Ingestion` | `LinkedIn Ingestion` | `x_bst_startuptrk_founder`, `x_bst_startuptrk_executive`, `x_bst_startuptrk_jobposting` | [`03-flow-linkedin-ingestion.md`](03-flow-linkedin-ingestion.md) |

There is **no Flow Designer ATF step configuration**. Both tests therefore drive the flow's own logic through its orchestrating Script Include rather than by triggering the flow record: `IngestionMapper.ingestStaging(run_id, source_system, import_run, provenance)` on the fallback path, and `IngestionMapper.ingest(run_id, source_system, provenance, rows)` on the live path. This is the same entry point the flow's step 5 calls, so the four cleaning rules under test are the ones the flow actually runs, not a copy of them.

Each test asserts three things, all four cleaning rules being exercised in the process.

### The shared flow step sequence

| Step | Step configuration | Category | Inputs |
| --- | --- | --- | --- |
| 5 | **Create a User** | Server - Independent | `roles` = **exactly** `x_bst_startuptrk.admin`. |
| 10 | **Impersonate** | Server - Independent | `user` = the step 5 output. The staging table grants read, write, create and delete to `x_bst_startuptrk.admin` alone. |
| 20 | **Run Server Side Script** | Server - Independent | **Writes the run-provenance marker and sets the result label.** See [Technique (c)](#technique-c--provenance-labelling). This is the setup step the requirements mandate. |
| 30 | **Run Server Side Script** | Server - Independent | Seeds the staging rows this test acts on: a clean row, a **duplicate pair** differing only by letter case, a row carrying an **unmatched choice value**, and a row **missing a mandatory field**. Written directly to `x_bst_startuptrk_ingest_staging` with `import_state` `pending` and a test-specific `import_run` token so the run cannot pick up rows loaded by [`06-staging-table-csv-import.md`](06-staging-table-csv-import.md). |
| 40 | **Run Server Side Script** | Server - Independent | Calls `IngestionMapper.ingestStaging()` with the test's `run_id`, the `source_system`, the test-specific `import_run` and provenance `fallback`. Captures the returned counts. |
| 50 | **Run Server Side Script** | Server - Independent | **Rule 2 — deduplication.** Asserts the duplicate pair produced **one** entity row, that the survivor is the first occurrence, and that the loser's staging row is `rejected` carrying the reason `duplicate startup in the same batch`. |
| 60 | **Run Server Side Script** | Server - Independent | **Rule 3 — choice normalisation.** Asserts the unmatched value was coerced to `Other` on a list that declares it, was **left unwritten** on a list that does not, and that a `choice_unmatched` event was **logged** in both cases naming the column and the supplied value. |
| 70 | **Run Server Side Script** | Server - Independent | **Rule 4 — mandatory-field rejection.** Asserts the row missing a mandatory field produced **no** entity record at all, that its staging row is `rejected` with a reason naming the missing field, and that nothing partial was inserted. |
| 80 | **Record Query** | Server - Independent | `table` = `x_bst_startuptrk_ingest_staging`; `field_values` = `import_run` `is` the test token **and** `import_state` `is` `pending`; `assert_type` = **No records match the query**. Every seeded row reached a terminal state. |
| 90 | **Run Server Side Script** | Server - Independent | **Rule 1 — trimming**, plus the run summary. Asserts the leading and trailing whitespace seeded at step 30 is absent from every stored string, and that `IngestionLogger.writeRunSummary()` emitted a `run_summary` event whose `provenance` member matches the marker written at step 20. |

### Rule 2 — deduplication on `name` plus `headquarters_location`

The deduplication key is `IngestionMapper.startupKey()`, which lowercases and joins the two columns: `lower(name)` + `|` + `lower(headquarters_location)`. It is applied at **batch scope** by `dedupeBatch()`, after preparation and before reference resolution. The first occurrence is accepted; every later occurrence is rejected with the reason `duplicate startup in the same batch` and logged through `IngestionLogger.duplicateRecord()`.

Seed this pair at step 30 so the match is **case-insensitive** and cannot pass by accident:

| Row | `name` | `headquarters_location` | Expected |
| --- | --- | --- | --- |
| A | `ATF Dedupe Target` | `Boston, MA` | Accepted; one `x_bst_startuptrk_startup` row |
| B | `atf dedupe target` | `boston, ma` | **Rejected** as a duplicate; no second entity row |
| C | `ATF Dedupe Target` | `Cambridge, MA` | **Accepted** — a different headquarters means a different key, so this is not a duplicate |

Row C is the negative control. Without it the test would pass equally against a deduplicator keyed on `name` alone, which is not the specified rule.

The rule applies to the `startup` record type only, and the same key is what lets a LinkedIn founder attach to a startup that Crunchbase created. Both flow tests therefore assert it, and the `BST FLOW — LinkedIn Ingestion` test additionally asserts that a founder whose parent startup already exists resolves onto the **existing** row rather than creating a second one.

### Rule 3 — choice normalisation, and the `Investor.type` asymmetry

Assert both branches in each test:

| Seeded value | Column | Expected |
| --- | --- | --- |
| `fintech` | `x_bst_startuptrk_startup.industry` | Case-insensitive match, stored as `Fintech` |
| `Quantum Widgets` | `x_bst_startuptrk_startup.industry` | No match, list declares `Other`, so stored as **`Other`** and **logged** |
| `Series Q` | `x_bst_startuptrk_fundinground.round_type` | No match, list declares no `Other`, so **left unwritten** and **logged** |
| `Sovereign Wealth` | `x_bst_startuptrk_investor.type` | No match, list declares no `Other`, so **left unwritten** and **logged** — and **the investor row still inserts** |

**The `x_bst_startuptrk_investor.type` asymmetry must be asserted explicitly.** That choice list is `VC`, `Angel`, `PE`, `Corporate`, `Accelerator` and has **no `Other` member**, so an unmatched investor type cannot be coerced. It is left unwritten and logged. Because `type` is **not** a mandatory column, the record itself survives — rejection is reserved for a record missing a mandatory field. The step 60 assertion for this case is therefore threefold: the `choice_unmatched` event is logged, `type` is empty on the stored row, and the row **exists**. A test that asserted rejection here would fail against correct behaviour.

Left unwritten is not the same as emptied. On an insert the column is empty; on an update the previously stored value survives. Seed one update case to assert the second half.

### Rule 4 — rejection of records missing mandatory fields

The check is `IngestionMapper.missingMandatory()`, which produces the reason `missing mandatory` followed by the offending field names and logs through `IngestionLogger.rejectRecord()`. Nothing partial is ever inserted. Seed one row per record type the flow under test writes, each missing exactly one mandatory field:

| Flow | Record type | Mandatory set | Seed one row omitting |
| --- | --- | --- | --- |
| `Crunchbase Ingestion` | `startup` | `name`, `headquarters_location`, `active` | `headquarters_location` |
| `Crunchbase Ingestion` | `investor` | `name` | `name` |
| `Crunchbase Ingestion` | `funding_round` | `startup`, `round_date` | `round_date` |
| `LinkedIn Ingestion` | `founder` | `name`, `startup` | `startup` |
| `LinkedIn Ingestion` | `executive` | `name`, `startup` | `name` |
| `LinkedIn Ingestion` | `job_posting` | `startup`, `title` | `title` |

Assert per row that the entity table gained no record, that the staging row is `rejected`, and that its `error_message` names the omitted field.

### Skip the record, continue the run

Both tests assert the specified failure semantics as well as the counts: a per-record error is logged, **that record is skipped**, and **the run continues**. Step 40's captured counts are the assertion — with the seed of step 30 the run must report a non-zero `processed` count **and** a non-zero `rejected` count from the same call. A run that halted on the first bad row would report the rejection and no processed records, and a run that inserted partial rows would report no rejections. Neither is acceptable.

Per-record skips arising from the four cleaning rules are **expected behaviour and are not errors**. They are counted separately from unhandled errors, and only unhandled errors bear on success criterion 4.

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

Add this **Run Server Side Script** step immediately after **Create a User** in each of the three role-specific tests, or once per suite. It is the step that makes the impersonation claim checkable rather than assumed.

```javascript
(function(outputs, steps, params, stepResult, assertEqual) {
    var EXPECTED = 'x_bst_startuptrk.user';           // the single scoped role for this test
    var FORBIDDEN = ['admin', 'security_admin', 'maint', 'atf_test_admin', 'atf_test_designer'];

    var userId = steps('10').user;
    var held = [];
    var gr = new GlideRecord('sys_user_has_role');
    gr.addQuery('user', userId);
    gr.query();
    while (gr.next())
        held.push(gr.role.name.toString());

    // Exactly one scoped role, and it is the expected one.
    var scoped = held.filter(function(r) { return r.indexOf('x_bst_startuptrk.') === 0; });
    assertEqual({ name: 'holds exactly one scoped role', shouldbe: 1, value: scoped.length });
    assertEqual({ name: 'the scoped role is ' + EXPECTED, shouldbe: EXPECTED, value: scoped[0] });

    // None of the elevated platform roles, directly or inherited.
    var elevated = held.filter(function(r) { return FORBIDDEN.indexOf(r) !== -1; });
    assertEqual({ name: 'holds no elevated platform role', shouldbe: 0, value: elevated.length });

    stepResult.setOutputMessage('Role set verified: [' + held.join(', ') + ']');
    return true;
})(outputs, steps, params, stepResult, assertEqual);
```

### Step 3 — the impersonation step

**Impersonate** (Server - Independent), `user` = the **Create a User** output. Place it after every fixture-writing step and before the assertion step, because the fixture must be written by `x_bst_startuptrk.admin` while the read must be attempted by the role under test. A test may carry more than one **Impersonate** step; the later one supersedes.

### Step 4 — teardown

**No teardown step is required, and none is added.** ATF rolls back the data a test creates when the test finishes, so the three users, their role assignments and every fixture record are removed automatically. Two consequences follow, and both are load-bearing:

- Do **not** rely on a user created by one test being present in another. Each test that impersonates creates its own.
- After a run, `sys_user` must carry **no** residual `BST ATF` user. If it does, a test errored in a way that left the transaction open; investigate before trusting any result in that run.

### Operational warning — the administrator ACL override

**Record ACLs by default allow the platform administrator role to override them, and every operator of a personal developer instance holds that role.** A walkthrough performed as the instance administrator will therefore display **all seven premium fields** and **appear to prove enforcement that was never tested**. The suite reports `success`, the fields are visible, and nothing about the field-level ACLs has been exercised at all.

All forty-nine delivered ACLs carry the administrator-override flag, so this is the default and expected behaviour of the platform, not a defect in the ACLs.

Three rules follow, and none of them is optional:

1. **Never read a premium field as yourself.** Every read assertion sits after an **Impersonate** step.
2. **The scoped `x_bst_startuptrk.admin` role is not the platform administrator role.** They are two different records. `BST ATF admin` holds the scoped role only, which is why the `ACL-*.1` cells prove something; a user holding the platform role would pass those cells by override.
3. **Verify the role set, do not assume it.** The step 2 script above exists for this reason. A `BST ATF base` user that silently acquired `admin` turns all seven denied cells into false passes.

[`../access-control.md`](../access-control.md) states the same impersonation requirement and names the reviewer entry that owns it; read its verification procedure alongside this section. The trap is also recorded in [`../gaps-and-flags.md`](../gaps-and-flags.md) as a gap in any naive verification procedure rather than a gap in the platform.

## Technique (b) — deterministic 429

The rate-limit assertion is made deterministic by **pre-seeding a counter row in `x_bst_startuptrk_rate_limit_counter` already at the configured budget**, so the very next call trips the limit in a **single request**. No loop of a hundred calls is needed and no test depends on timing out a real budget. The mechanic is stated here; the decision is recorded in [`../../../docs/decisions/DECISION_LOG.md`](../../../docs/decisions/DECISION_LOG.md).

### Where the budget and window come from

| Property | Delivered value | Role |
| --- | --- | --- |
| `x_bst_startuptrk.rest.rate_limit_requests` | `100` | The budget. Seed `request_count` to exactly this value. |
| `x_bst_startuptrk.rest.rate_limit_window_seconds` | `60` | The fixed window length in seconds. Determines the window boundary the seeded row must fall on. |

Read both through `AppProperties` rather than hard-coding them, so a tuned instance does not silently break the test.

### The five columns to seed

| Column | Value |
| --- | --- |
| `caller` | The `sys_id` of **`bst.atf.rest`** — the user the inbound REST request authenticates as, **not** the impersonated user. `Send REST Request - Inbound` establishes its own session, so an earlier `Impersonate` step has no bearing on which caller the limiter accounts against. Seeding the wrong caller is the single most common reason this assertion fails to trip. |
| `api_resource` | The exact token for the resource under test, from the table in [suite 9](#suite-9--bst-rest-suite--resources). Seven tokens exist; the nested executives sub-resource has its own. |
| `window_start` | The **current window boundary**: the current epoch second floored to a multiple of the window length. Not "now". |
| `request_count` | The budget itself — `100` by default. The service rejects when the incremented count is **strictly greater than** the budget, so a row seeded at `100` becomes `101` on the next call and trips; a row seeded at `99` becomes `100` and does **not** trip. |
| `window_key` | The composite key described immediately below, truncated at 200 characters. This column is **mandatory and unique**. Build it with `RateLimitService.windowKey()` rather than by string concatenation, so it matches the key the service computes. |

The composite key joins three parts with pipe characters:

```text
<caller sys_id>|<api_resource>|<window start as whole seconds since epoch>
```

### The seeding script

Use this at step 130 of each REST test, substituting `API_RESOURCE`.

```javascript
(function(outputs, steps, params, stepResult, assertEqual) {
    var API_RESOURCE = '/startups';       // one of the seven tokens

    var props = new AppProperties();
    var budget = props.getRateLimitRequests();          // x_bst_startuptrk.rest.rate_limit_requests
    var windowSeconds = props.getRateLimitWindowSeconds(); // x_bst_startuptrk.rest.rate_limit_window_seconds

    var caller = new GlideRecord('sys_user');
    if (!caller.get('user_name', 'bst.atf.rest')) {
        stepResult.setFailed('REST caller bst.atf.rest not found. Build it as a precondition.');
        return false;
    }

    // Floor the current second to the window boundary, exactly as the service does.
    var nowSeconds = Math.floor(new GlideDateTime().getNumericValue() / 1000);
    var bucket = nowSeconds - (nowSeconds % windowSeconds);
    var windowStart = new GlideDateTime();
    windowStart.setNumericValue(bucket * 1000);

    // Guard the boundary: if the window is about to roll, wait for the next one.
    var remaining = (bucket + windowSeconds) - nowSeconds;
    if (remaining < 10) {
        gs.sleep(remaining * 1000 + 500);
        nowSeconds = Math.floor(new GlideDateTime().getNumericValue() / 1000);
        bucket = nowSeconds - (nowSeconds % windowSeconds);
        windowStart.setNumericValue(bucket * 1000);
    }

    var key = new RateLimitService().windowKey(caller.getUniqueValue(), API_RESOURCE, windowStart);

    var row = new GlideRecord('x_bst_startuptrk_rate_limit_counter');
    row.initialize();
    row.setValue('window_key', key);
    row.setValue('caller', caller.getUniqueValue());
    row.setValue('api_resource', API_RESOURCE);
    row.setValue('window_start', windowStart);
    row.setValue('request_count', budget);      // exactly at budget; the next call makes it budget + 1
    var sysId = row.insert();

    assertEqual({ name: 'counter row seeded', shouldbe: true, value: !!sysId });
    outputs.window_key = key;
    outputs.budget = budget;
    stepResult.setOutputMessage('Seeded ' + API_RESOURCE + ' at request_count=' + budget +
        ', window_start=' + windowStart.getDisplayValue() + '. The next call trips the limit.');
    return true;
})(outputs, steps, params, stepResult, assertEqual);
```

### The assertions on the response

| Assertion | Step | Detail |
| --- | --- | --- |
| Status | **Assert Status Code**, `response_operation` **is**, `status_code` `429` | Not 415 and not 403. The rate limiter runs **first** in every operation, ahead of the in-script role guard, the media-type guard and all parameter validation, so a caller over budget reads 429 rather than any other refusal. |
| Error member | **Assert JSON Response Payload Element**, `element_name` `error`, `response_operation` **is**, `element_value` `rate_limit_exceeded` | The exact string. |
| Retry member | **Run Server Side Script** | `retry_after` is present and is a **positive integer**. |
| Body shape | Same script step | The body carries **exactly** the two members `error` and `retry_after` and nothing else. |

```javascript
(function(outputs, steps, params, stepResult, assertEqual) {
    var body = JSON.parse(steps('140').response_body);

    assertEqual({ name: 'error is rate_limit_exceeded',
        shouldbe: 'rate_limit_exceeded', value: body.error });

    var retry = body.retry_after;
    assertEqual({ name: 'retry_after is present',
        shouldbe: true, value: Object.prototype.hasOwnProperty.call(body, 'retry_after') });
    assertEqual({ name: 'retry_after is an integer',
        shouldbe: true, value: typeof retry === 'number' && retry === Math.floor(retry) });
    assertEqual({ name: 'retry_after is positive',
        shouldbe: true, value: retry > 0 });

    // Exactly two members, no more.
    assertEqual({ name: 'body carries exactly error and retry_after',
        shouldbe: 2, value: Object.keys(body).length });

    stepResult.setOutputMessage('429 contract satisfied; retry_after=' + retry);
    return true;
})(outputs, steps, params, stepResult, assertEqual);
```

`retry_after` is always at least `1`, because the service floors the remaining window at one second. An assertion of "greater than zero" therefore holds for every window position, including a request that arrives in the final fraction of a second of a window.

A standard `Retry-After` response header carries the same value. It may be asserted with **Assert Response Header** as a supplementary check; it does not change the body, and the body is what the contract fixes.

## Technique (c) — provenance labelling

Each flow test's **setup step writes the run-provenance marker**, and the test result is labelled either **`live validated`** or **`fallback validated`**. The mechanic is stated here; the decision is recorded in [`../../../docs/decisions/DECISION_LOG.md`](../../../docs/decisions/DECISION_LOG.md).

### Why the label is a separate evidence surface

**ATF rolls back the data a test creates.** A provenance row or a property value written **inside** a test therefore does **not** survive the run. The marker written at step 20 is real for the duration of the test and gone afterwards, so it cannot serve as the durable evidence success criterion 4 reads. The label on the test result carries that meaning instead.

The two surfaces are distinct and must not be conflated:

| Surface | Written by | Survives the run? | Read by |
| --- | --- | --- | --- |
| **Scheduled-run provenance** | Step 8 of the flow, on a real scheduled execution — the run-summary record and `x_bst_startuptrk.ingestion.last_run_provenance` | **Yes.** It is written outside any test transaction. | [`../validation-checklist.md`](../validation-checklist.md), success criterion 4 |
| **ATF result label** | The step 20 setup step in this guide, labelling the result `fallback validated` or `live validated` | **No.** ATF rolls back the data a test creates, so a provenance row or property written inside a test does not persist. | The test report, and this guide's evidence record |

This table is stated identically in [`02-flow-crunchbase-ingestion.md`](02-flow-crunchbase-ingestion.md) and [`03-flow-linkedin-ingestion.md`](03-flow-linkedin-ingestion.md). The three documents must agree.

### The setup step

```javascript
(function(outputs, steps, params, stepResult, assertEqual) {
    // 'live' only if the credential alias resolves; otherwise 'fallback'.
    var PROVENANCE = 'fallback';
    var SOURCE = 'crunchbase';                       // or 'linkedin'
    var RUN_ID = SOURCE + '-' + new GlideDateTime().getNumericValue();

    // writeRunSummary validates provenance against 'live' and 'fallback' only; any other
    // value logs run_summary_provenance_invalid and writes nothing at all.
    assertEqual({ name: 'provenance is a permitted value', shouldbe: true,
        value: PROVENANCE === 'live' || PROVENANCE === 'fallback' });

    new IngestionLogger().writeRunSummary(RUN_ID, PROVENANCE);

    outputs.run_id = RUN_ID;
    outputs.provenance = PROVENANCE;
    outputs.label = PROVENANCE === 'live' ? 'live validated' : 'fallback validated';

    // The label is stamped onto the step output so it appears in the result record.
    stepResult.setOutputMessage('RESULT LABEL: ' + outputs.label +
        ' | run_id=' + RUN_ID + ' | provenance=' + PROVENANCE);
    return true;
})(outputs, steps, params, stepResult, assertEqual);
```

`writeRunSummary()` accepts **only** `live` and `fallback`. Any other value logs a `run_summary_provenance_invalid` event at error level and writes nothing, so a typo produces a run with no summary rather than a run with a wrong one.

### The naming and annotation convention

So that a passing result can never be mistaken for validated live integration, apply all three:

| Where | Convention |
| --- | --- |
| Test name | Suffix the mode: `BST FLOW — Crunchbase Ingestion [fallback]`. Rename to `[live]` only when the run genuinely used a live call. |
| Test description | End with the sentence `Result label: fallback validated.` — or `live validated`. |
| Step output | The step 20 script writes `RESULT LABEL: fallback validated` into the step output message, so the label appears in `sys_atf_test_result_step` and cannot be lost when the result is exported. |

### When live authentication fails

**If live authentication fails, re-run the test with the fallback sample dataset and label the result `fallback validated` rather than `live validated`.** Set `PROVENANCE` to `fallback`, point step 40 at the staged rows, and rename the test to the `[fallback]` suffix. Do not leave a `[live]` name on a run that fell back.

On the target instance **neither credential alias currently holds a live credential**, so every flow run resolves to `fallback` and **both flow tests are labelled `fallback validated`**. Success criterion 4 explicitly accepts the sample-dataset substitute, so this satisfies the criterion — **provided the mode is recorded**. Recording it is the whole point of the convention above.

## Assembling and running the suites

### Assemble

Build the ten suites, then a single parent suite that runs them in order.

| Order | Suite | Child of |
| --- | --- | --- |
| 1 | `BST CRUD suite — startup` | `BST — full delivery suite` |
| 2 | `BST CRUD suite — founder` | `BST — full delivery suite` |
| 3 | `BST CRUD suite — executive` | `BST — full delivery suite` |
| 4 | `BST CRUD suite — investor` | `BST — full delivery suite` |
| 5 | `BST CRUD suite — fundinground` | `BST — full delivery suite` |
| 6 | `BST CRUD suite — jobposting` | `BST — full delivery suite` |
| 7 | `BST CRUD suite — newsarticle` | `BST — full delivery suite` |
| 8 | `BST ACL suite — premium fields by role` | `BST — full delivery suite` |
| 9 | `BST REST suite — resources` | `BST — full delivery suite` |
| 10 | `BST FLOW suite — ingestion` | `BST — full delivery suite` |

To create a suite: **All** > **Automated Test Framework** > **Test Suites** > **New**. Set **Name**, confirm the application picker reads **Boston Startup Tracker**, and **Save**. Then add tests through the **Test Suite Tests** related list, setting **Order** in tens so a test can be inserted later. To nest, set the child suite's **Parent** field to `BST — full delivery suite`.

The parent suite is a convenience for a single run. **Suite membership does not make one test depend on another**: each of the 36 tests is self-contained, creates its own users and its own fixtures, and is rolled back independently. Any test can be run on its own from its own form, and a single failing test can be re-run without re-running the other 35.

The order above is the diagnostic order, not a dependency order. If the CRUD suites fail, the ACL and REST results are not worth reading yet, because the tables themselves are wrong.

### Run

| Action | How |
| --- | --- |
| Run one test | Open the test and click **Run Test**. |
| Run one suite | Open the suite and click **Run Test Suite**. |
| Run everything | Open `BST — full delivery suite` and click **Run Test Suite**. |
| Client test runner | Open **All** > **Automated Test Framework** > **Run Client Test Runner** in a second browser tab and leave it open for the duration. Every step in this guide is server-side or REST and needs no interaction, but the runner must be attached for a run to be scheduled. |

Run the suites **serially**. ATF serialises execution against a single runner, and the two flow tests write to the same staging table.

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
| **2** — field-level ACLs on 100 % of the 7 premium fields, verified per role per field | The `BST ACL suite — premium fields by role` suite result, plus all **21** named test results | All 21 cells passing. For each of the seven `ACL-*.3` cells, the step 50 output message confirming the key was **absent** and the control column still readable. Plus the step 8 and step 38 role-set verifications, which are what prove the reads were not performed under an overriding role. |
| **3** — 6 REST resources return correct paginated responses and a 429 with a retry value | The `BST REST suite — resources` suite result, plus all **6** named test results | Per resource: the 200 status, the envelope carrying `result`, `total_count`, `limit` and `offset`, the step 70 output message with the `total_count` and row count, the step 100 cross-page comparison, the clamped-limit assertion, and the 429 step output with the `retry_after` value. For `BST REST — founders`, both the `/founders` and the nested `/founders/{startup_id}/executives` blocks. |
| **4** — flows ingest and clean on the configured cadence with zero unhandled errors across three consecutive scheduled runs | The `BST FLOW suite — ingestion` suite result, plus both named test results **with their labels** | Both tests passing, each carrying `RESULT LABEL: fallback validated` or `live validated`. **This is not sufficient on its own.** Criterion 4's durable evidence is the run-summary records written by three consecutive guard-passing scheduled executions of each flow, which are a separate surface — see [Technique (c)](#technique-c--provenance-labelling) and [what counts as a scheduled run](../deployment-runbook.md#what-counts-as-a-scheduled-run). The suite result evidences the cleaning rules; the run summaries evidence the cadence and the error count. |
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
- The suite count is below 10 or the test count is below 36.
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
| System-property keys | 3 | `x_bst_startuptrk.rest.rate_limit_requests`, `x_bst_startuptrk.rest.rate_limit_window_seconds`, `x_bst_startuptrk.rest.max_limit` |
| Choice member strings | 63 | The choice-value assertions of suites 1 to 7 and the normalisation assertions of suite 10 |
| Flow names | 2 | `Crunchbase Ingestion`, `LinkedIn Ingestion`, in suite 10's test names and descriptions |
| Provenance labels | 2 | `live validated`, `fallback validated` |

[`../api-reference.md`](../api-reference.md) carries the Script Include call graph, which is the authoritative rename-impact list for the service layer; a class renamed there breaks every caller, including the scripts in this guide. The Update Set XML at [`../../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml`](../../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml) remains authoritative for every spelling.

## Operational warnings

Eight warnings. **W1 and W2 are completely silent** — every test reports `success` while the property under test was never exercised at all.

**W1. The administrator ACL override makes suite 8 pass without testing anything. SILENT.**
Record ACLs by default allow the platform administrator role to override them, and every operator of a personal developer instance holds that role. Read a premium field as yourself and all seven appear, the suite reports `success`, and the field-level ACLs were never consulted. Without impersonation, success criterion 2 is not weakly evidenced — **it is not evidenced at all**. Every read assertion must follow an **Impersonate** step, and the impersonated user's role set must be verified by the step 8 and step 38 scripts rather than assumed. Full detail under [Technique (a)](#technique-a--impersonation).

**W2. `enforce_security` left `false` makes every record step pass vacuously. SILENT.**
`Record Insert`, `Record Update`, `Record Query`, `Record Delete` and `Record Validation` each expose an `enforce_security` input. With it `false` the step runs unrestricted, ignores every ACL, and reports `success`. Set it **true** on every record step in this guide. In suite 8 the entire assertion depends on it; in suites 1 to 7 it is what proves the write ACLs grant `x_bst_startuptrk.admin` and no one else.

**W3. `Assert JSON Response Payload Element` cannot prove a key is absent.**
Its nearest presence operator is `exists`, whose label in the form is literally **"is not empty"**. It does not distinguish a key that is missing from a key that is present holding an empty string — and an empty string is exactly what the secured read returns for a denied field. Using it for the omission assertion would pass against the forbidden nulled behaviour. Assert key absence in a **Run Server Side Script** step with `Object.prototype.hasOwnProperty.call(body, FIELD) === false`. `does_not_contain` against the raw payload is a weaker supplementary check only, and must not be the primary assertion.

**W4. Seeding the rate-limit row against the wrong caller stops the 429 from firing.**
`Send REST Request - Inbound` performs a real inbound HTTP call and establishes its **own** session. An `Impersonate` step earlier in the test has no bearing on it. The limiter accounts against `bst.atf.rest`, the user in the step's **Basic authentication** profile — seed that user's `sys_id` in `caller`, not the impersonated user's. The symptom is a 200 where a 429 was asserted, with no other diagnostic.

**W5. A window boundary crossing between the seed step and the request stops the 429 from firing.**
The counter is a fixed window. If the seed lands near the end of a window and the request arrives in the next one, the service computes a different `window_key`, finds no row, and starts a fresh count at 1. The seeding script guards this by measuring the remaining window and waiting for the next boundary when fewer than ten seconds remain. Keep that guard. The symptom is an intermittent 200 where a 429 was asserted — passing on most runs and failing on a few.

**W6. Provenance written inside a test does not survive the run.**
ATF rolls back the data a test creates, so the marker written by suite 10's step 20 is gone once the test finishes. It cannot serve as criterion 4's durable evidence. The ATF **result label** carries that meaning, and the scheduled run-summary records are the separate, surviving surface. Do not substitute one for the other. Full detail under [Technique (c)](#technique-c--provenance-labelling).

**W7. A test built in the Global scope has its record steps refused.**
All ten tables ship `access` `package_private` with `read_access`, `create_access`, `update_access`, `delete_access` and `ws_access` all false — the posture `GATE-SEC-01` and `GATE-SEC-02` verify. A test created while the application picker reads **Global** is an out-of-scope caller and is refused before any ACL is consulted, which looks like an ACL failure but is not one. Confirm the picker reads **Boston Startup Tracker** before creating any test or suite. Where a record step is still refused, use a **Run Server Side Script** step, which compiles in the test's own scope.

**W8. A residual `BST ATF` user after a run means a transaction did not close.**
The three impersonation users are created at run time and rolled back with the rest of the test data. After a completed run, `sys_user` must carry no user whose first name is `BST ATF`. If one remains, a test errored in a way that left its transaction open, and no result in that run should be trusted until the cause is found. `bst.atf.rest` is the exception: it is a hand-built precondition artifact and is **expected** to persist.

## Legacy provenance

The legacy repository carries a test tree that never ran. These suites replace it. **Nothing about its structure, fixtures or assertions is carried forward.**

| Legacy artifact | Verified fact | Replaced by |
| --- | --- | --- |
| `pytest.ini:L6` | `testpaths = tests/backend`, which confines collection to one of the three test trees and so **excludes 16 of the 27** test files — all 10 under `tests/data_collection/` and all 6 under `tests/frontend/`. | One `BST — full delivery suite` covering all four suite groups, with nothing excluded by configuration. |
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
- [ ] `bst.atf.rest` exists holding **exactly** `x_bst_startuptrk.user`, and the `BST ATF REST caller` Basic Auth Configuration references it.

**Inventory**

- [ ] **10** suites exist, named exactly as in [What this guide builds](#what-this-guide-builds).
- [ ] **36** tests exist: 7 + 21 + 6 + 2.
- [ ] Every one of the 36 tests is a member of its suite with an explicit **Order**.
- [ ] **0** new step configurations were created.

**Suites 1 to 7 — table CRUD**

- [ ] One suite per entity table, covering `x_bst_startuptrk_startup`, `x_bst_startuptrk_founder`, `x_bst_startuptrk_executive`, `x_bst_startuptrk_investor`, `x_bst_startuptrk_fundinground`, `x_bst_startuptrk_jobposting` and `x_bst_startuptrk_newsarticle`.
- [ ] Each asserts insert, update, query and delete.
- [ ] Each asserts a mandatory-field omission with **Record was not inserted** — one step per mandatory column, 13 such steps across the seven tables, plus the `active` default assertion in suite 1.
- [ ] Each asserts choice values, with the `Other` and no-`Other` branches correct per column.
- [ ] `enforce_security` is **true** on every record step.
- [ ] No `Other` member was added to any of the six lists that lack one.

**Suite 8 — premium fields by role**

- [ ] All **21** cells `ACL-1.1` through `ACL-7.3` exist as separate tests.
- [ ] The 7 field names and 3 role names match [`../access-control.md`](../access-control.md) exactly.
- [ ] The 14 `*.1` and `*.2` cells assert the value is **read** and the key is **present**.
- [ ] The 7 `*.3` cells assert the key is **absent** via `hasOwnProperty`, not that the value is falsy.
- [ ] Every cell impersonates a user holding **exactly one** scoped role and **none** of the elevated platform roles, verified by script rather than assumed.
- [ ] Each `*.3` cell carries the control assertion proving Layer 1 granted while Layer 3 denied.

**Suite 9 — REST resources**

- [ ] All **6** resources have a test, and the nested `GET /founders/{startup_id}/executives` is exercised inside `BST REST — founders`.
- [ ] Every `end_point` uses the physical base path `/api/x_bst_startuptrk/v1/`.
- [ ] Pagination uses exactly `sysparm_limit` and `sysparm_offset`.
- [ ] `total_count` is asserted to **agree with the page contents** and to be stable across offsets.
- [ ] The over-limit request is asserted to clamp to `50`.
- [ ] Each test asserts status `429`, `error` is `rate_limit_exceeded`, and `retry_after` is a positive integer.
- [ ] The counter row is seeded against `bst.atf.rest` at `request_count` equal to the budget, with the correct one of the **seven** `api_resource` tokens.
- [ ] The window-boundary guard is present in every seeding script.

**Suite 10 — ingestion flows**

- [ ] Both `Crunchbase Ingestion` and `LinkedIn Ingestion` have a test.
- [ ] Deduplication is asserted on `name` plus `headquarters_location`, case-insensitively, including the differing-location negative control.
- [ ] Choice normalisation is asserted for both branches, with unmatched values coerced to `Other` where declared and **logged** in every case.
- [ ] The `x_bst_startuptrk_investor.type` asymmetry is asserted: left unwritten, logged, **and the row still inserts**.
- [ ] Records missing a mandatory field are asserted to be rejected with nothing partial inserted.
- [ ] Each test reports a non-zero `processed` **and** a non-zero `rejected` count from one call, proving skip-and-continue.
- [ ] Each test's setup step writes the provenance marker, and each result is labelled exactly `fallback validated` or `live validated`.

**Run and evidence**

- [ ] `BST — full delivery suite` runs to completion with **36 of 36** tests passing and **0** in the **Error** state.
- [ ] No residual `BST ATF` user remains in `sys_user`.
- [ ] The suite results, test results and step results for criteria 2, 3 and 4 are recorded against [`../validation-checklist.md`](../validation-checklist.md).
- [ ] Criterion 4's three consecutive guard-passing scheduled runs per flow are recorded from the **run-summary records**, not from the ATF results.
- [ ] The [Coverage gate](#coverage-gate) is met: 100 % of the 7 tables and 100 % of the 6 resources have a passing test.

## Related documents

- [`../../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml`](../../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml) — authoritative for every identifier cited in this guide
- [`../access-control.md`](../access-control.md) — the 3 x 7 role-by-field matrix, the secured read path, the omit-not-nulled rule and the impersonation requirement
- [`../api-reference.md`](../api-reference.md) — the 6 resources, the nested sub-resource, the pagination contract, the exact 429 and 500 bodies, and the Script Include call graph
- [`../data-model.md`](../data-model.md) — the 53 columns, the 14 mandatory flags and all 11 choice lists the CRUD suites assert against
- [`../validation-gates.md`](../validation-gates.md) — the sixteen post-commit gates and the eleven-gate core of precondition 4
- [`../deployment-runbook.md`](../deployment-runbook.md) — the import sequence, the ATF prerequisite assertion, and [what counts as a scheduled run](../deployment-runbook.md#what-counts-as-a-scheduled-run)
- [`01-connection-credential-aliases.md`](01-connection-credential-aliases.md) — the two aliases whose state decides the flow-test label
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
