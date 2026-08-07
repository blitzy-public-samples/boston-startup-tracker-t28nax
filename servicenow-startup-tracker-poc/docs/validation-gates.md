# Post-commit validation gates — `x_bst_startuptrk`

These eleven gates run **after** the Update Set at [`../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml`](../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml) has committed successfully on the target instance. They are the final step of the six-step import sequence in [`./deployment-runbook.md`](./deployment-runbook.md), and they are the last check performed before a deployment is accepted. **Any** gate failure triggers the rollback, and the specific gate that failed is reported.

The post-commit step reads its gates from this exact relative path, `<deliverable-root>/docs/validation-gates.md`; this file must not be renamed, relocated or given a suffix.

The Update Set XML is **authoritative** over this document for every table name, role name and scope name below. Those identifiers are documented in [`./data-model.md`](./data-model.md) and [`./access-control.md`](./access-control.md), and the names used here match those two documents character for character. Where this document and the Update Set records disagree, the records are correct and this document is corrected to match them, never the reverse.

This document carries assertions and their pass and fail conditions only. Every decision behind this gate set is recorded in [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md), which is the single source of truth for "why". The procedure surrounding these gates is in [`./deployment-runbook.md`](./deployment-runbook.md).

## How to read a gate

Every gate below is stated with the same seven fields.

| Field | Meaning |
| --- | --- |
| **Gate ID** | The stable identifier for the gate. [`./deployment-runbook.md`](./deployment-runbook.md) and [`./validation-checklist.md`](./validation-checklist.md) cite gates by this identifier, and a failure report names it. |
| **Assertion** | The single condition the gate establishes, stated as a fact that must hold after the commit. |
| **Target** | The table the request is issued against. |
| **Query** | The query string appended to the target, in the form defined under [Common request shape](#common-request-shape). |
| **Expected result** | The HTTP status and response body the request returns when the gate passes. |
| **Pass condition** | The mechanical test applied to that response. A gate passes only when this test holds exactly. |
| **On failure** | The action taken when the pass condition does not hold. |

## Common request shape

Every gate is a single read against the platform Table API. The request is shown here once in full; each gate below supplies only its **Target** and its **Query**.

```text
GET {SERVICENOW_INSTANCE_URL}/api/now/table/{Target}?{Query}
Authorization: Basic base64({SERVICENOW_USERNAME}:{SERVICENOW_PASSWORD})
Accept: application/json
```

`{SERVICENOW_INSTANCE_URL}`, `{SERVICENOW_USERNAME}` and `{SERVICENOW_PASSWORD}` are the same three environment values the deployment sequence in [`./deployment-runbook.md`](./deployment-runbook.md) uses. No credential value appears in this document, in any gate, or in any evidence record.

Worked example. `GATE-TBL-01` has target `x_bst_startuptrk_startup` and query `sysparm_limit=1`, so its full request is:

```text
GET {SERVICENOW_INSTANCE_URL}/api/now/table/x_bst_startuptrk_startup?sysparm_limit=1
Authorization: Basic base64({SERVICENOW_USERNAME}:{SERVICENOW_PASSWORD})
Accept: application/json
```

Three response forms are referenced by the pass conditions below.

| Response | Meaning |
| --- | --- |
| `HTTP 200` with a body carrying a `result` array | The read succeeded. The array holds between zero and `sysparm_limit` records. |
| `HTTP 400` with body `{"error":{"message":"Invalid table <target>","detail":null},"status":"failure"}` | The named target table does not exist on the instance. |
| `HTTP 401` or `HTTP 403` | The credentials are invalid, or the account lacks access to the target. |

Each gate is evaluated on one response. No gate requires a second request, a retry, or a comparison against a previous deployment.

## Gates 1 to 7 — entity table reads

Seven gates, one per entity table, in the order the tables are declared in [`./data-model.md`](./data-model.md). Each gate establishes that its table committed and is readable with the deployment credentials, and each uses query `sysparm_limit=1`.

An **empty** `result` array is a **pass**. These gates establish that a table exists and is readable; they do not establish that it holds data.

| Gate ID | Assertion | Target | Query | Expected result | Pass condition | On failure |
| --- | --- | --- | --- | --- | --- | --- |
| `GATE-TBL-01` | A read against `x_bst_startuptrk_startup` succeeds. | `x_bst_startuptrk_startup` | `sysparm_limit=1` | `HTTP 200` with a body carrying a `result` array. | Status is exactly `200` and the body carries a `result` array. An empty `result` array passes. | Any status other than `200`, in particular `HTTP 400` with message `Invalid table x_bst_startuptrk_startup`. Report `GATE-TBL-01`; initiate rollback. |
| `GATE-TBL-02` | A read against `x_bst_startuptrk_founder` succeeds. | `x_bst_startuptrk_founder` | `sysparm_limit=1` | `HTTP 200` with a body carrying a `result` array. | Status is exactly `200` and the body carries a `result` array. An empty `result` array passes. | Any status other than `200`, in particular `HTTP 400` with message `Invalid table x_bst_startuptrk_founder`. Report `GATE-TBL-02`; initiate rollback. |
| `GATE-TBL-03` | A read against `x_bst_startuptrk_executive` succeeds. | `x_bst_startuptrk_executive` | `sysparm_limit=1` | `HTTP 200` with a body carrying a `result` array. | Status is exactly `200` and the body carries a `result` array. An empty `result` array passes. | Any status other than `200`, in particular `HTTP 400` with message `Invalid table x_bst_startuptrk_executive`. Report `GATE-TBL-03`; initiate rollback. |
| `GATE-TBL-04` | A read against `x_bst_startuptrk_investor` succeeds. | `x_bst_startuptrk_investor` | `sysparm_limit=1` | `HTTP 200` with a body carrying a `result` array. | Status is exactly `200` and the body carries a `result` array. An empty `result` array passes. | Any status other than `200`, in particular `HTTP 400` with message `Invalid table x_bst_startuptrk_investor`. Report `GATE-TBL-04`; initiate rollback. |
| `GATE-TBL-05` | A read against `x_bst_startuptrk_fundinground` succeeds. | `x_bst_startuptrk_fundinground` | `sysparm_limit=1` | `HTTP 200` with a body carrying a `result` array. | Status is exactly `200` and the body carries a `result` array. An empty `result` array passes. | Any status other than `200`, in particular `HTTP 400` with message `Invalid table x_bst_startuptrk_fundinground`. Report `GATE-TBL-05`; initiate rollback. |
| `GATE-TBL-06` | A read against `x_bst_startuptrk_jobposting` succeeds. | `x_bst_startuptrk_jobposting` | `sysparm_limit=1` | `HTTP 200` with a body carrying a `result` array. | Status is exactly `200` and the body carries a `result` array. An empty `result` array passes. | Any status other than `200`, in particular `HTTP 400` with message `Invalid table x_bst_startuptrk_jobposting`. Report `GATE-TBL-06`; initiate rollback. |
| `GATE-TBL-07` | A read against `x_bst_startuptrk_newsarticle` succeeds. | `x_bst_startuptrk_newsarticle` | `sysparm_limit=1` | `HTTP 200` with a body carrying a `result` array. | Status is exactly `200` and the body carries a `result` array. An empty `result` array passes. | Any status other than `200`, in particular `HTTP 400` with message `Invalid table x_bst_startuptrk_newsarticle`. Report `GATE-TBL-07`; initiate rollback. |

These seven gates are the machine-checkable half of prompt section 10.0 criterion 1; the field-by-field half is covered by [`./validation-checklist.md`](./validation-checklist.md).

## Gates 8 to 10 — role records

Three gates, one per role the application declares. Every role name is written fully qualified with the dot separator, exactly as [`./access-control.md`](./access-control.md) records it. No bare, abbreviated or underscore form of a role name is valid in these gates.

Each gate targets `sys_user_role` and matches its role by exact name. The pass condition is a record count: the request returns `HTTP 200` whether or not the role exists, so the count is what each gate tests.

| Gate ID | Assertion | Target | Query | Expected result | Pass condition | On failure |
| --- | --- | --- | --- | --- | --- | --- |
| `GATE-ROLE-01` | Exactly one `sys_user_role` record named `x_bst_startuptrk.admin` exists. | `sys_user_role` | `sysparm_query=name=x_bst_startuptrk.admin` | `HTTP 200` with a `result` array holding exactly 1 record whose `name` is `x_bst_startuptrk.admin`. | Status is exactly `200` and `result` holds exactly 1 record. | 0 records: the role did not commit. More than 1 record: duplicate role records. Either outcome, or any status other than `200`. Report `GATE-ROLE-01`; initiate rollback. |
| `GATE-ROLE-02` | Exactly one `sys_user_role` record named `x_bst_startuptrk.user` exists. | `sys_user_role` | `sysparm_query=name=x_bst_startuptrk.user` | `HTTP 200` with a `result` array holding exactly 1 record whose `name` is `x_bst_startuptrk.user`. | Status is exactly `200` and `result` holds exactly 1 record. | 0 records: the role did not commit. More than 1 record: duplicate role records. Either outcome, or any status other than `200`. Report `GATE-ROLE-02`; initiate rollback. |
| `GATE-ROLE-03` | Exactly one `sys_user_role` record named `x_bst_startuptrk.premium_user` exists. | `sys_user_role` | `sysparm_query=name=x_bst_startuptrk.premium_user` | `HTTP 200` with a `result` array holding exactly 1 record whose `name` is `x_bst_startuptrk.premium_user`. | Status is exactly `200` and `result` holds exactly 1 record. | 0 records: the role did not commit. More than 1 record: duplicate role records. Either outcome, or any status other than `200`. Report `GATE-ROLE-03`; initiate rollback. |

An empty `result` array is a **failure** for these three gates, and for `GATE-SCOPE-01` below. It is a pass only for `GATE-TBL-01` through `GATE-TBL-07`.

## Gate 11 — the scope record

One gate, targeting `sys_scope` and matching the application scope by exact name.

| Gate ID | Assertion | Target | Query | Expected result | Pass condition | On failure |
| --- | --- | --- | --- | --- | --- | --- |
| `GATE-SCOPE-01` | Exactly one `sys_scope` record whose `scope` is `x_bst_startuptrk` exists. | `sys_scope` | `sysparm_query=scope=x_bst_startuptrk` | `HTTP 200` with a `result` array holding exactly 1 record whose `scope` is `x_bst_startuptrk`. | Status is exactly `200` and `result` holds exactly 1 record. | 0 records: the scoped application did not commit. More than 1 record: duplicate scope records. Either outcome, or any status other than `200`. Report `GATE-SCOPE-01`; initiate rollback. |

The rollback procedure in [`./deployment-runbook.md`](./deployment-runbook.md) retrieves and deletes this same `sys_scope` record. `GATE-SCOPE-01` confirms the record that rollback acts on.

## Gate roll-up

7 table gates + 3 role gates + 1 scope gate = **11 gates**.

| # | Gate ID | Assertion |
| --- | --- | --- |
| 1 | `GATE-TBL-01` | A read against `x_bst_startuptrk_startup` succeeds. |
| 2 | `GATE-TBL-02` | A read against `x_bst_startuptrk_founder` succeeds. |
| 3 | `GATE-TBL-03` | A read against `x_bst_startuptrk_executive` succeeds. |
| 4 | `GATE-TBL-04` | A read against `x_bst_startuptrk_investor` succeeds. |
| 5 | `GATE-TBL-05` | A read against `x_bst_startuptrk_fundinground` succeeds. |
| 6 | `GATE-TBL-06` | A read against `x_bst_startuptrk_jobposting` succeeds. |
| 7 | `GATE-TBL-07` | A read against `x_bst_startuptrk_newsarticle` succeeds. |
| 8 | `GATE-ROLE-01` | Exactly one `sys_user_role` record named `x_bst_startuptrk.admin` exists. |
| 9 | `GATE-ROLE-02` | Exactly one `sys_user_role` record named `x_bst_startuptrk.user` exists. |
| 10 | `GATE-ROLE-03` | Exactly one `sys_user_role` record named `x_bst_startuptrk.premium_user` exists. |
| 11 | `GATE-SCOPE-01` | Exactly one `sys_scope` record whose `scope` is `x_bst_startuptrk` exists. |

The aggregate pass condition is that **all eleven** gates pass. There is no partial pass. No gate is advisory, and no gate may be skipped, deferred or waived.

The gate set covers the seven entity tables only. No gate is defined for `x_bst_startuptrk_m2m_round_investor`, `x_bst_startuptrk_ingest_staging` or `x_bst_startuptrk_rate_limit_counter`; those three supporting tables are documented in [`./data-model.md`](./data-model.md) and are outside this gate set.

## Failure handling

On failure of any one of the eleven gates:

1. Report the failing gate by its identifier, together with the HTTP status and the response body observed.
2. Initiate the rollback.

The failing gate is reported before the rollback is initiated. The rollback steps and the wider failure matrix are in [`./deployment-runbook.md`](./deployment-runbook.md) and are not restated here.

## Evidence record

The operator records one row per gate per deployment. [`./validation-checklist.md`](./validation-checklist.md) cites this table as the evidence for the machine-checkable gates.

| Gate ID | Result | Timestamp (UTC) | Note |
| --- | --- | --- | --- |
| `GATE-TBL-01` | | | |
| `GATE-TBL-02` | | | |
| `GATE-TBL-03` | | | |
| `GATE-TBL-04` | | | |
| `GATE-TBL-05` | | | |
| `GATE-TBL-06` | | | |
| `GATE-TBL-07` | | | |
| `GATE-ROLE-01` | | | |
| `GATE-ROLE-02` | | | |
| `GATE-ROLE-03` | | | |
| `GATE-SCOPE-01` | | | |
| **Aggregate** | | | 11 of 11 gates required |

Record `pass` or `fail` in **Result**. Record the time of the request in **Timestamp (UTC)** in `YYYY-MM-DD HH:MM:SS` form. Record the observed HTTP status and the `result` record count in **Note**, and for a failing gate also the response body. Record no credential value in any field.

## Related documents

- [`./deployment-runbook.md`](./deployment-runbook.md) — the pre-flight checks, the six-step import sequence whose final step reads this file, the rollback and the failure matrix
- [`./validation-checklist.md`](./validation-checklist.md) — the five success criteria; it cites the evidence record above and covers the field-by-field half of criterion 1
- [`./data-model.md`](./data-model.md) — the ten tables field by field, and the source of the seven entity table names gated here
- [`./access-control.md`](./access-control.md) — the three roles and the ACL matrix, and the source of the three role names gated here
- [`../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml`](../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml) — the authoritative table, role and scope records these gates verify
- [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md) — the single source of truth for every decision behind this gate set
