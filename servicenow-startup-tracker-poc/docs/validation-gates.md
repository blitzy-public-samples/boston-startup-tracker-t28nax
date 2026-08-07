# Post-commit validation gates — `x_bst_startuptrk`

These sixteen gates run **after** the Update Set at [`../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml`](../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml) has committed successfully on the target instance. They are the sixth and final step of the import sequence — upload the XML, poll for load, trigger preview, require the error-type preview-problem set to be empty, commit, then run these gates — and they are the last check performed before a deployment is accepted. That sequence is to be specified in full, with its polling intervals and timeouts, in [`./deployment-runbook.md` (planned)](./deployment-runbook.md). **Any** gate failure triggers the rollback, and the specific gate that failed is reported.

The post-commit step reads its gates from this exact relative path, `<deliverable-root>/docs/validation-gates.md`; this file must not be renamed, relocated or given a suffix.

**Authority.** The frozen prompt and the Agent Action Plan are authoritative for all application content. The table names, role names and scope name asserted below are taken from the Update Set XML once those records have been verified against that specification; the same identifiers are documented in [`./data-model.md`](./data-model.md) and [`./access-control.md`](./access-control.md), and the names used here match those two documents character for character. Where this document and the Update Set records disagree, the records are checked against the prompt and the plan first. Where the records match the specification, this document is corrected to them. Where the records depart from it, the records are corrected.

This document carries assertions and their pass and fail conditions only. Every decision behind this gate set is to be recorded in [`../../docs/decisions/DECISION_LOG.md` (planned)](../../docs/decisions/DECISION_LOG.md), which is to be the single source of truth for "why".

## Referenced documents

**This document is executable on its own.** All sixteen gates, the request shape, every target, query, expected result and pass condition, the transient-error retry rule, the failure handling and the evidence record are stated here in full. An operator needs no other file to run the gates and record the outcome.

Some documents named below are **planned artifacts of this package**. Every link to one carries the marker **(planned)** in its link text. A statement about a planned document describes what that document is required to contain; it is not a claim that the content can be read from it. The delivered files referenced from here are `../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml`, `./data-model.md` and `./access-control.md`.

The wider deployment procedure — the pre-flight checks, the polling mechanics of the five steps preceding these gates, the rollback steps and the failure matrix — is to be specified in [`./deployment-runbook.md` (planned)](./deployment-runbook.md). The rollback action is named under [Failure handling](#failure-handling), and the six-step sequence is named above.

## How to read a gate

Every gate below is stated with the same seven fields.

| Field | Meaning |
| --- | --- |
| **Gate ID** | The stable identifier for the gate. A failure report names it, and [`./deployment-runbook.md` (planned)](./deployment-runbook.md) and [`./validation-checklist.md` (planned)](./validation-checklist.md) are to cite gates by this identifier. |
| **Assertion** | The single condition the gate establishes, stated as a fact that must hold after the commit. |
| **Target** | The table the request is issued against. |
| **Query** | The query string appended to the target, in the form defined under [Common request shape](#common-request-shape). |
| **Expected result** | The HTTP status and response body the request returns when the gate passes. |
| **Pass condition** | The mechanical test applied to that response. A gate passes only when this test holds exactly. |
| **On failure** | The action taken when the pass condition does not hold. Every **On failure** cell below is read subject to the [Transient-error retry rule](#transient-error-retry-rule): where a cell says any status other than `200` initiates the rollback, an `HTTP 500` initiates it only after the single 30-second retry has also failed. |

## Common request shape

Every gate is a single read against the platform Table API, issued with the deployment administrator credentials. The request is shown here once in full; each gate below supplies only its **Target** and its **Query**.

```text
GET {SERVICENOW_INSTANCE_URL}/api/now/table/{Target}?{Query}
Authorization: Basic base64({SERVICENOW_USERNAME}:{SERVICENOW_PASSWORD})
Accept: application/json
```

`{SERVICENOW_INSTANCE_URL}`, `{SERVICENOW_USERNAME}` and `{SERVICENOW_PASSWORD}` are the three environment values the deployment sequence is to use, and are read from the environment rather than written anywhere. No credential value appears in this document, in any gate, or in any evidence record.

Every **Target** in this gate set is a platform metadata table — `sys_db_object`, `sys_dictionary`, `sys_user_role` or `sys_scope`. **No gate targets an application table.** This is a deliberate departure from AAP section 0.11.2, which specified a `sysparm_limit=1` read against each of the seven entity tables. The application's ten tables are delivered with `access` set to `package_private`, every cross-scope capability flag set to `false`, and `ws_access` set to `false`, so they are deliberately **not** reachable over `/api/now/table/*` at all. Restoring those reads would mean re-enabling the native Table API on every application table — an alternate, unrate-limited, unfield-gated route to the data that exists alongside the Scripted REST API. The gates below establish the same facts through metadata the deployment administrator can already read. The decision, its alternatives and its consequences are recorded in [`../../docs/decisions/DECISION_LOG.md` (planned)](../../docs/decisions/DECISION_LOG.md).

Worked example. `GATE-TBL-01` has target `sys_db_object` and query `sysparm_query=name=x_bst_startuptrk_startup&sysparm_fields=name,access,ws_access`, so its full request is:

```text
GET {SERVICENOW_INSTANCE_URL}/api/now/table/sys_db_object?sysparm_query=name=x_bst_startuptrk_startup&sysparm_fields=name,access,ws_access
Authorization: Basic base64({SERVICENOW_USERNAME}:{SERVICENOW_PASSWORD})
Accept: application/json
```

Four response forms are referenced by the pass conditions below.

| Response | Meaning |
| --- | --- |
| `HTTP 200` with a body carrying a `result` array | The read succeeded. The array holds the matching metadata records, of which there may be zero. |
| `HTTP 200` with an **empty** `result` array | The queried metadata record does not exist. For every gate in this document that is a **failure**. |
| `HTTP 400` with body `{"error":{"message":"Invalid table <target>","detail":null},"status":"failure"}` | The named target table does not exist on the instance. |
| `HTTP 401` or `HTTP 403` | The credentials are invalid, or the account lacks the `admin` role the metadata tables require. |
| `HTTP 500` | The instance returned a server error. This form is transient and is subject to the retry rule below. |

### Transient-error retry rule

This rule applies to every one of the sixteen gates and is stated here in full. The failure matrix to be specified in [`./deployment-runbook.md` (planned)](./deployment-runbook.md) is required to carry the same rule.

- A gate that returns `HTTP 500` is **retried exactly once**, after waiting **30 seconds**. The retry reissues the identical request.
- The gate is then evaluated on the retry's response. A retry returning `HTTP 200` that satisfies the pass condition is a **pass**. A retry returning `HTTP 500` again, or any other status that does not satisfy the pass condition, is a **fail**.
- A gate is retried **at most once**. A second `HTTP 500` is final.
- No status other than `HTTP 500` is retried. `HTTP 400`, `HTTP 401` and `HTTP 403` are evaluated on their first response and fail immediately.
- No gate is compared against a previous deployment.

Apart from this rule, each gate is evaluated on one response.

## Gates 1 to 7 — entity table metadata

Seven gates, one per entity table, in the order the tables are declared in [`./data-model.md`](./data-model.md). Each gate establishes that its table committed, by reading the table's own dictionary record from `sys_db_object`.

An **empty** `result` array is a **failure**: it means the table did not commit. Every gate uses query `sysparm_query=name=<table>&sysparm_fields=name,access,ws_access`, and the returned `access` and `ws_access` values feed `GATE-SEC-01` and `GATE-SEC-02` below, so no extra request is needed for them.

| Gate ID | Assertion | Target | Query | Expected result | Pass condition | On failure |
| --- | --- | --- | --- | --- | --- | --- |
| `GATE-TBL-01` | A `sys_db_object` record named `x_bst_startuptrk_startup` exists. | `sys_db_object` | `sysparm_query=name=x_bst_startuptrk_startup&sysparm_fields=name,access,ws_access` | `HTTP 200` with a `result` array holding exactly 1 record whose `name` is `x_bst_startuptrk_startup`. | Status is exactly `200` and `result` holds exactly 1 record. | 0 records: the table did not commit. More than 1 record: duplicate table definitions. Either outcome, or any status other than `200`. Report `GATE-TBL-01`; initiate rollback. |
| `GATE-TBL-02` | A `sys_db_object` record named `x_bst_startuptrk_founder` exists. | `sys_db_object` | `sysparm_query=name=x_bst_startuptrk_founder&sysparm_fields=name,access,ws_access` | `HTTP 200` with a `result` array holding exactly 1 record whose `name` is `x_bst_startuptrk_founder`. | Status is exactly `200` and `result` holds exactly 1 record. | 0 records: the table did not commit. More than 1 record: duplicate table definitions. Either outcome, or any status other than `200`. Report `GATE-TBL-02`; initiate rollback. |
| `GATE-TBL-03` | A `sys_db_object` record named `x_bst_startuptrk_executive` exists. | `sys_db_object` | `sysparm_query=name=x_bst_startuptrk_executive&sysparm_fields=name,access,ws_access` | `HTTP 200` with a `result` array holding exactly 1 record whose `name` is `x_bst_startuptrk_executive`. | Status is exactly `200` and `result` holds exactly 1 record. | 0 records: the table did not commit. More than 1 record: duplicate table definitions. Either outcome, or any status other than `200`. Report `GATE-TBL-03`; initiate rollback. |
| `GATE-TBL-04` | A `sys_db_object` record named `x_bst_startuptrk_investor` exists. | `sys_db_object` | `sysparm_query=name=x_bst_startuptrk_investor&sysparm_fields=name,access,ws_access` | `HTTP 200` with a `result` array holding exactly 1 record whose `name` is `x_bst_startuptrk_investor`. | Status is exactly `200` and `result` holds exactly 1 record. | 0 records: the table did not commit. More than 1 record: duplicate table definitions. Either outcome, or any status other than `200`. Report `GATE-TBL-04`; initiate rollback. |
| `GATE-TBL-05` | A `sys_db_object` record named `x_bst_startuptrk_fundinground` exists. | `sys_db_object` | `sysparm_query=name=x_bst_startuptrk_fundinground&sysparm_fields=name,access,ws_access` | `HTTP 200` with a `result` array holding exactly 1 record whose `name` is `x_bst_startuptrk_fundinground`. | Status is exactly `200` and `result` holds exactly 1 record. | 0 records: the table did not commit. More than 1 record: duplicate table definitions. Either outcome, or any status other than `200`. Report `GATE-TBL-05`; initiate rollback. |
| `GATE-TBL-06` | A `sys_db_object` record named `x_bst_startuptrk_jobposting` exists. | `sys_db_object` | `sysparm_query=name=x_bst_startuptrk_jobposting&sysparm_fields=name,access,ws_access` | `HTTP 200` with a `result` array holding exactly 1 record whose `name` is `x_bst_startuptrk_jobposting`. | Status is exactly `200` and `result` holds exactly 1 record. | 0 records: the table did not commit. More than 1 record: duplicate table definitions. Either outcome, or any status other than `200`. Report `GATE-TBL-06`; initiate rollback. |
| `GATE-TBL-07` | A `sys_db_object` record named `x_bst_startuptrk_newsarticle` exists. | `sys_db_object` | `sysparm_query=name=x_bst_startuptrk_newsarticle&sysparm_fields=name,access,ws_access` | `HTTP 200` with a `result` array holding exactly 1 record whose `name` is `x_bst_startuptrk_newsarticle`. | Status is exactly `200` and `result` holds exactly 1 record. | 0 records: the table did not commit. More than 1 record: duplicate table definitions. Either outcome, or any status other than `200`. Report `GATE-TBL-07`; initiate rollback. |

These seven gates are the machine-checkable half of prompt section 10.0 criterion 1 — they establish that each of the seven entity tables exists and is readable. `GATE-COL-01` below strengthens the existence check into a column count. The field-by-field half, which walks all 53 columns against the instance dictionary, is to be covered by [`./validation-checklist.md` (planned)](./validation-checklist.md) and is not performed here.

## Gate 8 — entity column count

One gate establishing that the 53 binding columns of prompt section 1.0 committed, by counting the entity tables' `sys_dictionary` column records. `sys_dictionary` carries one record per column plus one collection record per table, so the seven entity tables contribute 53 column records and 7 collection records; the query below excludes the collection records by requiring a non-empty `element`.

| Gate ID | Assertion | Target | Query | Expected result | Pass condition | On failure |
| --- | --- | --- | --- | --- | --- | --- |
| `GATE-COL-01` | The seven entity tables carry exactly 53 columns between them. | `sys_dictionary` | `sysparm_query=nameINx_bst_startuptrk_startup,x_bst_startuptrk_founder,x_bst_startuptrk_executive,x_bst_startuptrk_investor,x_bst_startuptrk_fundinground,x_bst_startuptrk_jobposting,x_bst_startuptrk_newsarticle^elementISNOTEMPTY&sysparm_fields=name,element&sysparm_limit=200` | `HTTP 200` with a `result` array holding exactly 53 records. | Status is exactly `200` and `result` holds exactly 53 records. | Fewer than 53: one or more columns did not commit. More than 53: an unexpected column exists, which breaches the binding-and-complete field list. Either outcome, or any status other than `200`. Report `GATE-COL-01`; initiate rollback. |

An encoded query is written `[field][operator][value]` with **no separator between the operator and its first operand**, which is why `nameIN` runs straight into `x_bst_startuptrk_startup` above and why `elementISNOTEMPTY` carries no operand at all. A space after `IN` is not ignored: it becomes the first character of the first operand, so the first table would be looked up under a leading space, would match nothing, and the gate would report 45 columns instead of 53 and trigger a rollback on a deployment that had in fact succeeded. The seven operands are separated by bare commas with no spaces, and each is spelled exactly as `sys_db_object.name` spells it — the same seven names `GATE-TBL-01` through `GATE-TBL-07` read. Confirm all seven statically against [`./data-model.md`](./data-model.md) before the deployment runs; the HTTP client URL-encodes the query, so the commas and the `^` need no manual escaping.

The per-table split, for diagnosing a count that is off: Startup 12, Founder 6, Executive 6, Investor 6, Funding round 8, Job posting 9, News article 6. 12 + 6 + 6 + 6 + 8 + 9 + 6 = 53. The three supporting tables are excluded from this gate; their columns are documented in [`./data-model.md`](./data-model.md).

## Gates 9 to 11 — role records

Three gates, one per role the application declares. Every role name is written fully qualified with the dot separator, exactly as [`./access-control.md`](./access-control.md) records it. No bare, abbreviated or underscore form of a role name is valid in these gates.

Each gate targets `sys_user_role` and matches its role by exact name. The pass condition is a record count: the request returns `HTTP 200` whether or not the role exists, so the count is what each gate tests.

| Gate ID | Assertion | Target | Query | Expected result | Pass condition | On failure |
| --- | --- | --- | --- | --- | --- | --- |
| `GATE-ROLE-01` | Exactly one `sys_user_role` record named `x_bst_startuptrk.admin` exists. | `sys_user_role` | `sysparm_query=name=x_bst_startuptrk.admin` | `HTTP 200` with a `result` array holding exactly 1 record whose `name` is `x_bst_startuptrk.admin`. | Status is exactly `200` and `result` holds exactly 1 record. | 0 records: the role did not commit. More than 1 record: duplicate role records. Either outcome, or any status other than `200`. Report `GATE-ROLE-01`; initiate rollback. |
| `GATE-ROLE-02` | Exactly one `sys_user_role` record named `x_bst_startuptrk.user` exists. | `sys_user_role` | `sysparm_query=name=x_bst_startuptrk.user` | `HTTP 200` with a `result` array holding exactly 1 record whose `name` is `x_bst_startuptrk.user`. | Status is exactly `200` and `result` holds exactly 1 record. | 0 records: the role did not commit. More than 1 record: duplicate role records. Either outcome, or any status other than `200`. Report `GATE-ROLE-02`; initiate rollback. |
| `GATE-ROLE-03` | Exactly one `sys_user_role` record named `x_bst_startuptrk.premium_user` exists. | `sys_user_role` | `sysparm_query=name=x_bst_startuptrk.premium_user` | `HTTP 200` with a `result` array holding exactly 1 record whose `name` is `x_bst_startuptrk.premium_user`. | Status is exactly `200` and `result` holds exactly 1 record. | 0 records: the role did not commit. More than 1 record: duplicate role records. Either outcome, or any status other than `200`. Report `GATE-ROLE-03`; initiate rollback. |

An empty `result` array is a **failure** for these three gates, and for every other gate in this document.

## Gate 12 — the scope record

One gate, targeting `sys_scope` and matching the application scope by exact name.

| Gate ID | Assertion | Target | Query | Expected result | Pass condition | On failure |
| --- | --- | --- | --- | --- | --- | --- |
| `GATE-SCOPE-01` | Exactly one `sys_scope` record whose `scope` is `x_bst_startuptrk` exists. | `sys_scope` | `sysparm_query=scope=x_bst_startuptrk` | `HTTP 200` with a `result` array holding exactly 1 record whose `scope` is `x_bst_startuptrk`. | Status is exactly `200` and `result` holds exactly 1 record. | 0 records: the scoped application did not commit. More than 1 record: duplicate scope records. Either outcome, or any status other than `200`. Report `GATE-SCOPE-01`; initiate rollback. |

The rollback acts on this same `sys_scope` record: it retrieves the record by this query and deletes it, which on a clean instance cascades the application's tables, roles and flows. `GATE-SCOPE-01` therefore confirms the record that rollback acts on. The full procedure, with its assertions, is to be specified in [`./deployment-runbook.md` (planned)](./deployment-runbook.md).

## Gates 13 to 16 — the security posture

Four gates establishing that the access posture the application depends on actually committed. `GATE-SEC-01` and `GATE-SEC-02` cover **all ten** tables, entity and supporting alike, because the posture is uniform across them. `GATE-SEC-03` covers the two endpoint access controls. `GATE-SEC-04` covers the instance-level XML parser configuration, which the application relies on but deliberately does **not** ship: those properties live in the Global scope, and prompt section 6.0 forbids the scoped application from modifying anything outside `x_bst_startuptrk`.

| Gate ID | Assertion | Target | Query | Expected result | Pass condition | On failure |
| --- | --- | --- | --- | --- | --- | --- |
| `GATE-SEC-01` | All ten application tables are reachable from the `x_bst_startuptrk` scope only. | `sys_db_object` | `sysparm_query=nameSTARTSWITHx_bst_startuptrk_^access=package_private&sysparm_fields=name,access&sysparm_limit=50` | `HTTP 200` with a `result` array holding exactly 10 records. | Status is exactly `200` and `result` holds exactly 10 records. | Fewer than 10: at least one table is `public`, so an out-of-scope script can reach its rows through unsecured record access and bypass the 47 record access controls. Report `GATE-SEC-01`; initiate rollback. |
| `GATE-SEC-02` | The native Table API is disabled on all ten application tables. | `sys_db_object` | `sysparm_query=nameSTARTSWITHx_bst_startuptrk_^ws_access=false&sysparm_fields=name,ws_access&sysparm_limit=50` | `HTTP 200` with a `result` array holding exactly 10 records. | Status is exactly `200` and `result` holds exactly 10 records. | Fewer than 10: at least one table is served by `/api/now/table/*`, giving callers a route that skips the rate limiter, the per-field read gate and the endpoint access controls. Report `GATE-SEC-02`; initiate rollback. |
| `GATE-SEC-03` | Both REST endpoint access controls committed. | `sys_security_acl` | `sysparm_query=type=REST_Endpoint^nameSTARTSWITHBoston Startup Tracker API&sysparm_fields=name,type,operation` | `HTTP 200` with a `result` array holding exactly 2 records, `Boston Startup Tracker API read` and `Boston Startup Tracker API write`, both with `operation` `execute`. | Status is exactly `200`, `result` holds exactly 2 records, and both carry `operation` `execute`. | Fewer than 2: endpoint authorisation falls back to the platform's broad default REST access control, which admits any authenticated internal user. Report `GATE-SEC-03`; initiate rollback. |
| `GATE-SEC-04` | The instance refuses XML entity resolution. | `sys_properties` | `sysparm_query=nameINglide.stax.allow_entity_resolution,glide.stax.whitelist_enabled&sysparm_fields=name,value` | `HTTP 200` with a `result` array holding 2 records: `glide.stax.allow_entity_resolution` with value `false` and `glide.stax.whitelist_enabled` with value `true`. | Status is exactly `200` and both values are as stated. | Either value differs, or a property is absent. Report `GATE-SEC-04`; **do not** roll back — set the property on the instance and re-run the gate. This is an instance configuration gate, not an artifact gate. |

`GATE-SEC-04` is the only gate in this document whose failure does **not** trigger a rollback, because the condition it tests is not created by the Update Set and cannot be fixed by removing it. The application closes the same vector independently: its Scripted REST API declares `application/json` for both `consumes` and `produces` on the definition and on all 31 operations, and every body-bearing operation refuses a request that does not declare `application/json` with `HTTP 415` before the body is read. `GATE-SEC-04` is defence in depth over that. The companion allowlist property `glide.xml.entity.whitelist` is not gated because its value is instance-specific.

## Gate roll-up

7 table-metadata gates + 1 column-count gate + 3 role gates + 1 scope gate + 4 security gates = **16 gates**.

| # | Gate ID | Assertion |
| --- | --- | --- |
| 1 | `GATE-TBL-01` | A `sys_db_object` record named `x_bst_startuptrk_startup` exists. |
| 2 | `GATE-TBL-02` | A `sys_db_object` record named `x_bst_startuptrk_founder` exists. |
| 3 | `GATE-TBL-03` | A `sys_db_object` record named `x_bst_startuptrk_executive` exists. |
| 4 | `GATE-TBL-04` | A `sys_db_object` record named `x_bst_startuptrk_investor` exists. |
| 5 | `GATE-TBL-05` | A `sys_db_object` record named `x_bst_startuptrk_fundinground` exists. |
| 6 | `GATE-TBL-06` | A `sys_db_object` record named `x_bst_startuptrk_jobposting` exists. |
| 7 | `GATE-TBL-07` | A `sys_db_object` record named `x_bst_startuptrk_newsarticle` exists. |
| 8 | `GATE-COL-01` | The seven entity tables carry exactly 53 columns between them. |
| 9 | `GATE-ROLE-01` | Exactly one `sys_user_role` record named `x_bst_startuptrk.admin` exists. |
| 10 | `GATE-ROLE-02` | Exactly one `sys_user_role` record named `x_bst_startuptrk.user` exists. |
| 11 | `GATE-ROLE-03` | Exactly one `sys_user_role` record named `x_bst_startuptrk.premium_user` exists. |
| 12 | `GATE-SCOPE-01` | Exactly one `sys_scope` record whose `scope` is `x_bst_startuptrk` exists. |
| 13 | `GATE-SEC-01` | All ten application tables are reachable from the `x_bst_startuptrk` scope only. |
| 14 | `GATE-SEC-02` | The native Table API is disabled on all ten application tables. |
| 15 | `GATE-SEC-03` | Both REST endpoint access controls committed. |
| 16 | `GATE-SEC-04` | The instance refuses XML entity resolution. |

The aggregate pass condition is that **all sixteen** gates pass. There is no partial pass. No gate is advisory, and no gate may be skipped, deferred or waived.

Gates 1 to 8 cover the seven entity tables only. `GATE-SEC-01` and `GATE-SEC-02` additionally cover `x_bst_startuptrk_m2m_round_investor`, `x_bst_startuptrk_ingest_staging` and `x_bst_startuptrk_rate_limit_counter`, since the access posture applies to all ten; those three supporting tables are otherwise documented in [`./data-model.md`](./data-model.md).

## Failure handling

On failure of any one of the sixteen gates:

1. Report the failing gate by its identifier, together with the HTTP status and the response body observed.
2. If the observed status is `HTTP 500` and the gate has not yet been retried, wait 30 seconds and reissue the identical request exactly once, per the [Transient-error retry rule](#transient-error-retry-rule). Evaluate the gate on that response and report the retry's status and body alongside the first.
3. Initiate the rollback when the pass condition still does not hold — that is, immediately for any status other than `HTTP 500`, and for `HTTP 500` only after the single retry has also failed. `GATE-SEC-04` is the one exception: its remedy is to correct the instance property and re-run the gate, as stated in its own row.

The failing gate is reported before the rollback is initiated. A gate that passes on its retry is a pass, is recorded as such, and initiates no rollback.

The rollback action: retrieve the `sys_scope` record whose `scope` is `x_bst_startuptrk` — the same record `GATE-SCOPE-01` tests — and delete it, then confirm the seven entity tables no longer resolve. **This is an irreversible operation.** Its full step-by-step form, its assertions and the wider failure matrix are to be specified in [`./deployment-runbook.md` (planned)](./deployment-runbook.md).

## Evidence record

The operator records one row per gate per deployment. This table is the evidence record for the machine-checkable gates, and [`./validation-checklist.md` (planned)](./validation-checklist.md) is to cite it as such.

| Gate ID | Result | Timestamp (UTC) | Note |
| --- | --- | --- | --- |
| `GATE-TBL-01` | | | |
| `GATE-TBL-02` | | | |
| `GATE-TBL-03` | | | |
| `GATE-TBL-04` | | | |
| `GATE-TBL-05` | | | |
| `GATE-TBL-06` | | | |
| `GATE-TBL-07` | | | |
| `GATE-COL-01` | | | |
| `GATE-ROLE-01` | | | |
| `GATE-ROLE-02` | | | |
| `GATE-ROLE-03` | | | |
| `GATE-SCOPE-01` | | | |
| `GATE-SEC-01` | | | |
| `GATE-SEC-02` | | | |
| `GATE-SEC-03` | | | |
| `GATE-SEC-04` | | | |
| **Aggregate** | | | 16 of 16 gates required |

Record `pass` or `fail` in **Result**. Record the time of the request in **Timestamp (UTC)** in `YYYY-MM-DD HH:MM:SS` form. Record the observed HTTP status and the `result` record count in **Note**, and for a failing gate also the response body. For `GATE-COL-01` record the count returned; for `GATE-SEC-04` record both property values. Record no credential value in any field.

Where a gate was retried under the [Transient-error retry rule](#transient-error-retry-rule), record the retry in the same row: note the first `HTTP 500`, the 30-second wait and the retry's status, and set **Timestamp (UTC)** to the retried request. **Result** carries the outcome of the retry, so a gate that returned `HTTP 500` and then `HTTP 200` is recorded as `pass` with the retry noted. A row that shows `pass` with no note of a retry means the gate passed on its first response.

## Related documents

Delivered with this package:

- [`../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml`](../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml) — the authoritative table, column, role, scope and access-control records these gates verify
- [`./data-model.md`](./data-model.md) — the ten tables field by field, and the source of the seven entity table names gated here
- [`./access-control.md`](./access-control.md) — the three roles, the access-control matrix including the two REST endpoint controls gated by `GATE-SEC-03`, and the table access posture gated by `GATE-SEC-01` and `GATE-SEC-02`
- [`./api-reference.md`](./api-reference.md) — the JSON-only request contract the application enforces independently of `GATE-SEC-04`
- [`../scripts/validate_update_set_xml.py`](../scripts/validate_update_set_xml.py) — the pre-delivery well-formedness validator run on the Update Set before it is uploaded

Planned artifacts of this package:

- [`./deployment-runbook.md` (planned)](./deployment-runbook.md) — to specify the pre-flight checks, the six-step import sequence whose final step reads this file, the rollback and the failure matrix
- [`./validation-checklist.md` (planned)](./validation-checklist.md) — to specify the five success criteria, to cite the evidence record above, and to cover the field-by-field half of criterion 1
- [`../../docs/decisions/DECISION_LOG.md` (planned)](../../docs/decisions/DECISION_LOG.md) — to be the single source of truth for every decision behind this gate set
