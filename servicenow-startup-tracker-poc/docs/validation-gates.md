# Post-commit validation gates — `x_bst_startuptrk`

These gates run **after** the Update Set at [`../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml`](../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml) has committed successfully on the target instance. They are the sixth and final step of the import sequence — upload the XML, poll for load, trigger preview, require the error-type preview-problem set to be empty, commit, then run these gates — and they are the last check performed before a deployment is accepted. That sequence is specified in full, with its polling intervals and timeouts, in [`./deployment-runbook.md`](./deployment-runbook.md).

**The acceptance contract is the eleven required gates, and only those eleven.** They are `GATE-TBL-01` through `GATE-TBL-07`, `GATE-ROLE-01` through `GATE-ROLE-03`, and `GATE-SCOPE-01` — the seven entity-table gates, the three role-record gates and the one scope-record gate that AAP section 0.11.2 and the deployment environment's definition require. Each of the seven entity-table gates reads that table's dictionary record rather than its rows, because all ten application tables are delivered closed to every route outside the application scope; see [Common request shape](#common-request-shape). A failure of any one of the eleven triggers the rollback, and the specific gate that failed is reported.

**The seven entity-table gates read table metadata rather than table rows**, because the seven entity tables are delivered sealed against every external route — `access` `package_private`, `read_access` `false`, `ws_access` `false` — so no Table API request reaches them at all. Each gate therefore asserts the same two facts a row read was asked to establish, and asserts them more precisely: that the table committed, and that it committed with the sealed posture the access-control design depends on. The ACL-respecting read path is exercised separately by `GATE-SEC-04`. The reasoning, the alternative and the residual risk are recorded at `D-027` in [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md).

**This document additionally defines five checks that are not deployment gates, and they do not all carry the same weight** — see [Three classes of check](#three-classes-of-check-and-what-each-one-blocks). `GATE-COL-01` is **acceptance-required and non-rollback**: success criterion 1 depends on it, so a failure blocks acceptance, but the remedy is to correct the Update Set and re-import rather than to delete a scope whose tables and roles all committed. `GATE-SEC-01` through `GATE-SEC-03` are **acceptance-required and non-rollback** on the same terms: each observes an access-posture fact the required eleven cannot see, and a weakened posture is not something acceptance may pass over — but the remedy is again to correct the delivered records and re-import, never to delete a scope that committed. They differ from `GATE-COL-01` in one respect only, and it is stated wherever they appear: a failure may alternatively be closed by the platform owner recording written acceptance of the named exposure in the evidence record. `GATE-SEC-04` is the single **non-normative diagnostic**: recorded on every deployment, blocking neither acceptance nor rollback, because it is the one check here that is not an HTTP request — it is a background script a human runs in the platform UI, so no deployment pipeline can assert on it. A non-normative diagnostic **must not** be cited as an entry condition by any other document in this package, and no manual-build guide may make one a precondition of its own work.

| Class | Members | Blocks acceptance? | Triggers rollback? |
| --- | --- | --- | --- |
| **1 — required deployment gate** | `GATE-TBL-01` to `-07`, `GATE-ROLE-01` to `-03`, `GATE-SCOPE-01` — **eleven** | **Yes** | **Yes** |
| **2 — acceptance-required, non-rollback** | `GATE-COL-01`, `GATE-SEC-01`, `GATE-SEC-02`, `GATE-SEC-03` — **four** | **Yes** | No |
| **3 — non-normative diagnostic** | `GATE-SEC-04` — **one** | No | No |

The rollback decision is therefore *eleven of eleven*, and the acceptance decision is *fifteen of fifteen* — the eleven, plus `GATE-COL-01` and `GATE-SEC-01` through `GATE-SEC-03`. Nothing in this package may restate either number as anything else.

One further condition is recorded and is **not a check of this delivery at all**: the instance's XML entity-resolution configuration, under [Instance prerequisite for XML entity resolution](#instance-prerequisite-for-xml-entity-resolution). There is no `GATE-SEC-05` in this gate set.

Two checks stated in this document run earlier, between the preview-problem step and the commit: [Pre-commit import completeness](#pre-commit-import-completeness) establishes that the commit has something to apply, without which every gate below fails against an instance where nothing was installed.

The post-commit step reads its gates from this exact relative path, `<deliverable-root>/docs/validation-gates.md`; this file must not be renamed, relocated or given a suffix.

**Authority.** The frozen prompt and the Agent Action Plan govern. They are authoritative for all application content, for the acceptance contract, and for the required gate set and its count. The table names, role names and scope name asserted below are taken from the Update Set XML once those records have been verified against that specification; the same identifiers are documented in [`./data-model.md`](./data-model.md) and [`./access-control.md`](./access-control.md), and the names used here match those two documents character for character. Where this document and the Update Set records disagree, the records are checked against the prompt and the plan first. Where the records match the specification, this document is corrected to them. **Where the records depart from it, the records are corrected** — a delivered artifact never governs over the specification, and a departure remains a defect until the artifact is aligned.

This document carries assertions and their pass and fail conditions only. Every decision behind this gate set is recorded in [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md), which is the single source of truth for "why".

## Referenced documents

**This document is executable on its own.** The eleven required gates, the four acceptance-required non-rollback checks, the one non-normative diagnostic, the one external instance prerequisite and the two pre-commit checks, the request shape, every target, query, expected result and pass condition, the transient-error retry rule, the failure handling and the evidence record are stated here in full. An operator needs no other file to run them and record the outcome.

**Every document named below is delivered and readable.** Each link resolves to a file in this package, among them `../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml`, `./data-model.md` and `./access-control.md`, so a reader can follow any link and read the content the statement around it describes; no link is a forward reference to something still to be written.

The wider deployment procedure — the three pre-flight checks, the polling mechanics of the five steps preceding these gates, the rollback steps and the failure matrix — is specified in [`./deployment-runbook.md`](./deployment-runbook.md). The rollback action is named under [Failure handling](#failure-handling), and the six-step sequence is named above. The nine values and routes that procedure is required to use, and the forms it must not use in their place, are stated under [Requirements carried to the deployment runbook](#requirements-carried-to-the-deployment-runbook).

## How to read a gate

Every gate below is stated with the same seven fields.

| Field | Meaning |
| --- | --- |
| **Gate ID** | The stable identifier for the gate. A failure report names it, and both [`./deployment-runbook.md`](./deployment-runbook.md) and [`./validation-checklist.md`](./validation-checklist.md) cite gates by this identifier. |
| **Assertion** | The single condition the gate establishes, stated as a fact that must hold after the commit. |
| **Target** | The table the request is issued against. |
| **Query** | The query string appended to the target, in the form defined under [Common request shape](#common-request-shape). |
| **Expected result** | The HTTP status and response body the request returns when the gate passes. |
| **Pass condition** | The mechanical test applied to that response. A gate passes only when this test holds exactly. |
| **On failure** | The action taken when the pass condition does not hold. Every **On failure** cell below is read subject to the [Transient-error retry rule](#transient-error-retry-rule): where a cell says any status other than `200` initiates the rollback, a **retryable server error** — `HTTP 500`, `502`, `503` or `504` — initiates it only after the single 30-second retry has also failed. |

## Common request shape

Every gate is a single read against a **platform** table over the Table API, issued with the deployment administrator credentials. No gate reads an application table, and none can: all ten are delivered closed to that route. The request is shown here once in full; each gate below supplies only its **Target** and its **Query**.

```text
GET {SERVICENOW_INSTANCE_URL}/api/now/table/{Target}?{Query}
Authorization: Basic base64({SERVICENOW_USERNAME}:{SERVICENOW_PASSWORD})
Accept: application/json
```

`{SERVICENOW_INSTANCE_URL}`, `{SERVICENOW_USERNAME}` and `{SERVICENOW_PASSWORD}` are the three environment values the deployment sequence is to use, and are read from the environment rather than written anywhere. No credential value appears in this document, in any gate, or in any evidence record.

**Gates 1 to 7 read the platform dictionary, not the entity tables themselves.** Each one queries `sys_db_object` for one entity table by name, within the `x_bst_startuptrk` scope, and asserts both that the table committed **and** that it committed closed. The remaining required gates target `sys_user_role` and `sys_scope`; the additive hardening checks target `sys_db_object`, `sys_dictionary` and `sys_security_acl`. Every gate in this document therefore reads a platform table, and **no gate reads an application row**.

**No external route reaches an application table, and that is the delivered design rather than an obstacle to it.** All ten tables — the seven entity tables and the three supporting tables — carry `access` `package_private`, `read_access` `false` and `ws_access` `false`, so `GET /api/now/table/x_bst_startuptrk_startup` answers `HTTP 400 Invalid table` to every caller including the deployment administrator, the native Aggregate API cannot sum or average a premium currency column, no `sysparm_query` predicate can be evaluated against a field the caller may not read, and no script in another application scope can open the rows with unsecured record access. Every write, configuration and schema flag — `create_access`, `update_access`, `delete_access`, `alter_access`, `configuration_access`, `actions_access`, `client_scripts_access` and `create_access_controls` — is `false` on all ten tables as well.

- **The native Table API serves none of the ten.** `GET /api/now/table/x_bst_startuptrk_startup` does not answer `200` on this deployment, by design. The only caller-facing read route is the Scripted REST API at `/api/x_bst_startuptrk/v1/`, which is inside the application's own fixed-window rate limiter and behind the two `REST_Endpoint` execution controls that `GATE-SEC-03` observes.
- **A script in another application scope cannot read a row either.** `access` `package_private` with `read_access` `false` is what closes the unsecured-record-access route that would otherwise evaluate no access control at all.
- **The role and field controls are unchanged and remain the enforcement point** on the one route that exists. Closing the native route removes a second, unmetered read path; it does not replace the seven table-level and seven field-level read controls, which still admit only the three scoped roles and still omit every premium field from a caller holding only `x_bst_startuptrk.user`. Those are verified by the access-control suite, not here.

**A gate that asserts the closed posture cannot be satisfied by a table that did not commit, and a table that committed open fails it.** That is why existence and containment are one assertion rather than two: an empty result means the table is absent from the scope, and a flag reading anything other than the closed value means the delivered dictionary record did not apply. Both are import failures and both initiate the rollback.

Worked example. `GATE-TBL-01` has target `sys_db_object` and query `sysparm_query=name=x_bst_startuptrk_startup^sys_scope.scope=x_bst_startuptrk&sysparm_fields=name,access,read_access,ws_access&sysparm_limit=2`, so its full request is:

```text
GET {SERVICENOW_INSTANCE_URL}/api/now/table/sys_db_object?sysparm_query=name=x_bst_startuptrk_startup^sys_scope.scope=x_bst_startuptrk&sysparm_fields=name,access,read_access,ws_access&sysparm_limit=2
Authorization: Basic base64({SERVICENOW_USERNAME}:{SERVICENOW_PASSWORD})
Accept: application/json
```

The `sys_scope.scope` term is a dot-walk from `sys_db_object` to the scope record, so a match proves the table committed **into `x_bst_startuptrk`** rather than into the Global scope. `sysparm_limit=2` is deliberate: one is the pass, and a second row is the ambiguity the gate must be able to see rather than silently truncate.

**Seven** response forms are referenced by the pass conditions below. Two of them are not gate outcomes at all, and the first is listed ahead of the other `HTTP 200` forms because it is the one that most easily passes for a real result.

| Response | Meaning |
| --- | --- |
| `HTTP 200` with a **non-JSON `Content-Type`** — an HTML hibernation notice, a login page or a redirect landing page | **Not a gate outcome. Do not evaluate the gate, do not record a failure, and do not initiate the rollback.** The instance is asleep, or the session is not authenticated, and the request never reached the application tier. See [A `200` that is not an answer](#a-200-that-is-not-an-answer). |
| A **server error that does not clear** — the same retryable status on every path, including a path that cannot exist, across repeated attempts | **Not a gate outcome either. Do not evaluate the gate, do not record a failure, and do not initiate the rollback.** No application node is answering. This is the condition observed on the target instance on 2026-08-11. See [A server error that never clears](#a-server-error-that-never-clears). |
| `HTTP 200` with a body carrying a `result` array | The read succeeded. The array holds the matching records, of which there may be zero. |
| `HTTP 200` with an **empty** `result` array | **A failure for every gate and check in this document**, because each one asserts that a named record exists. For `GATE-TBL-01` through `GATE-TBL-07` an empty array means no `sys_db_object` record carries that table name inside the `x_bst_startuptrk` scope, so the table did not commit. |
| `HTTP 400` with body `{"error":{"message":"Invalid table <target>","detail":null},"status":"failure"}` | The named target table does not exist on the instance. No gate in this document targets an application table, so on a correct deployment this form appears only if a platform table name was mistyped. It is also the expected response to a read of an application table, which is why no gate issues one — see [Common request shape](#common-request-shape). |
| `HTTP 401` or `HTTP 403` | The credentials are invalid, or the account lacks the role the target requires. Every gate in this document reads a platform table and needs `admin`, so a `401` or `403` is a credential or role problem rather than a statement about the application: correct the account and reissue before reading the response as a gate outcome. |
| A **retryable server error** — `HTTP 500`, `HTTP 502`, `HTTP 503` or `HTTP 504` | The instance, or the edge in front of it, returned a server error. This form is transient and is subject to the retry rule below. |

### A `200` that is not an answer

**Every gate below tests a record count or a field value, and every one of those tests is applied to a parsed JSON body. A response that is not JSON has no gate outcome in it — neither a pass nor a fail — and treating it as a fail is worse than treating it as nothing, because the fail path initiates the [rollback](#failure-handling), and the rollback deletes a scope.**

This is not hypothetical. It was the observed condition of the target instance: a hibernated instance answers **every** path — the Table API, the scoped Scripted REST API, `/login.do`, `/stats.do` and paths that do not exist at all — with `HTTP 200`, `Content-Type: text/html`, a byte-identical **5904**-byte hibernation page, `Server: snow_adc` (the edge tier answering because no application node is running), **no** `Set-Cookie` and **no** `WWW-Authenticate`. The content type stays `text/html` even when `Accept: application/json` is negotiated explicitly, and a valid administrator credential presented over HTTP Basic changes nothing. A logged-out or expired session produces the same shape from a live instance: an HTML login page under a `200`.

**Before evaluating any gate in this document, apply the same four-part test [`./deployment-runbook.md`](./deployment-runbook.md#pre-flight-1--instance-reachable-and-credentials-valid) applies at pre-flight 1** — the status is `200`, the `Content-Type` is `application/json`, the body parses as JSON, and the parsed body carries a top-level `result` member. A response failing any of the four is classified as this sixth form.

| Condition | Disposition |
| --- | --- |
| All four hold | Evaluate the gate against its pass condition, as written. |
| Status `200`, `Content-Type` not `application/json`, or the body does not parse, or there is no top-level `result` | **Stop the gate run.** Record the observed `Content-Type`, the body length and the first 200 characters of the body — **never** a credential. Do **not** mark any gate `pass` or `fail`; mark the run **not evaluated**. Restart from pre-flight 1 in [`./deployment-runbook.md`](./deployment-runbook.md#pre-flight-checks): wake the instance or re-authenticate, then run the whole gate set again from the first gate. |

**Do not health-check this condition on the status code.** A status-only check reports a hibernating instance as healthy, because the status is `200`. Detect it on content — the content type, the absence of a top-level `result`, or the absence of a `Set-Cookie` on a form login — exactly as the four-part test does.

**Gates already recorded in this run are not carried forward.** A gate set that stopped on this form is re-run in full rather than resumed, because the instance state that produced it is not local to one gate.

### A server error that never clears

**A retryable status is a statement about the transport on its first appearance and a statement about the instance when it never goes away, and the two must not be given the same disposition — because one disposition ends in a retry and the other would end in a rollback that deletes a scope.**

This is the second condition observed on the target instance, and it is **not** the hibernation form above. On **2026-08-11** every path answered `HTTP 502 Bad Gateway` with a byte-identical **153**-byte `text/html` body — SHA-256 `ea52f7bee5ea0e80b0f7f0b7388ab454bf6856d8865d5cefbe170976da22f54e` — and `Server: snow_adc`, with no `X-Transaction-Id` and no `Set-Cookie`. The eight paths measured were `/`, `/login.do`, `/stats.do`, `/bst?id=bst_home`, `/api/now/table/sys_remote_update_set`, `/api/now/table/sys_upgrade_history`, `/api/now/table/sys_atf_test_suite_result` and `/api/x_bst_startuptrk/v1/startups`. DNS resolved and the TLS handshake completed, so the edge was healthy and nothing behind it was: the same answer for a path that must exist and a path that cannot carries **no information about the application**, exactly as the hibernation form carries none.

**It later reverted to the hibernation form on the same day, which is why a gate run reads the condition from its own probe and never from this record.** Later on **2026-08-11** every path answered `HTTP 200` with the byte-identical **5904**-byte hibernation page instead — an authenticated Table API read, `POST /login.do`, `/stats.do` and the wake path `/?wu=true` alike — and four polls at 30-second intervals did not change it. An instance observed in both unavailable forms within one day tells a gate run only that it must **measure** the condition, so treat the two sub-sections above as the two signatures to match against rather than as a statement of where this instance stands now. Both dispositions are identical for the gate: **not a gate outcome**, recorded as unevaluable, never as a failure, because a required gate marked failed is answered by a rollback that deletes a scope.

**The discriminator, and it is credential-free.** Issue the identical request to a path that cannot exist — `/this-path-cannot-exist-<nonce>.xyz` — and repeat the gate's own request at least **six** times at 30-second intervals.

| Observation | Disposition |
| --- | --- |
| The nonexistent path answers `HTTP 404`, or the repeated request clears to a JSON `result` | The first error was **transient**. Apply the [transient-error retry rule](#transient-error-retry-rule) and evaluate the gate on the response that cleared. |
| The nonexistent path answers with the **same** status and the same body as the gate's path, and every repetition answers the same way | The instance is **unavailable**. Mark the gate run **not evaluated**, record the status, the body length, the body digest and the `Server` header, and **stop**. Do **not** mark any gate `pass` or `fail`, and do **not** initiate the [rollback](#failure-handling) — there is no evidence a commit failed, and the rollback deletes a scope. Escalate per [`./deployment-runbook.md`](./deployment-runbook.md#pre-flight-1--instance-reachable-and-credentials-valid). |

**Why this form needs its own rule rather than the retry rule.** The retry rule below makes a second retryable status **final**, and a final failure on a required gate is a gate failure, which the failure matrix answers with a rollback. Under a persistently unavailable instance that path would delete the application scope on the strength of a response that never reached the application — the same mistake [A `200` that is not an answer](#a-200-that-is-not-an-answer) exists to prevent, arriving under a different status. The rule above closes it.

**The eleven required gates, the additive hardening checks and the two pre-commit checks are all subject to this form**, because every one of them is an HTTP read of the same instance.

### Transient-error retry rule

This rule applies to every required gate, to every additive hardening check, and to the two checks under [Pre-commit import completeness](#pre-commit-import-completeness), and is stated here in full. The failure matrix in [`./deployment-runbook.md`](./deployment-runbook.md) carries the same rule, and the per-operation retry policy stated there governs the non-idempotent steps of the import sequence rather than these reads.

**A retryable server error means any of `HTTP 500`, `HTTP 502`, `HTTP 503` or `HTTP 504`.** The class is four statuses rather than one because the request does not reach the platform directly: it passes through an edge that answers in its own right, and the QA run of 2026-08-09 measured that edge returning `502 Bad Gateway` on between 21.7 % and 25.0 % of requests issued in parallel. A gate that treated only `500` as transient would fail on a `502` at its first response — and a failing required gate initiates the rollback, so a momentary edge error would destroy a deployment that had committed correctly. Every one of the four is a statement about the transport, not about the application.

- A gate that returns a **retryable server error** is **retried exactly once**, after waiting **30 seconds**. The retry reissues the identical request.
- The gate is then evaluated on the retry's response. A retry returning `HTTP 200` that satisfies the pass condition is a **pass**. A retry returning any other status that does not satisfy the pass condition is a **fail**.
- A gate is retried **at most once**. A second retryable server error is final **as a retry**, and it is then classified rather than failed: apply the discriminator of [A server error that never clears](#a-server-error-that-never-clears) before recording anything. A cleared error is a transient one and the gate stands on the response that cleared; an error that answers a nonexistent path identically and survives six repetitions is an unavailable instance, and the run is marked **not evaluated** with no gate failure and no rollback.
- No status outside that class is retried. `HTTP 400`, `HTTP 401`, `HTTP 403` and `HTTP 404` are evaluated on their first response and fail immediately. In particular a `200` carrying HTML rather than JSON is **not** retried — it is a hibernating or unauthenticated instance, which no wait resolves.
- No gate is compared against a previous deployment.

Apart from this rule, each gate is evaluated on one response.

## Pre-commit import completeness

Two checks run **before** the commit, immediately after the preview has completed and the error-type preview-problem set has been confirmed empty. They are **not** gates — neither a required gate nor an additive hardening check — and are not counted in the [Gate roll-up](#gate-roll-up); they are preconditions of it. [`./deployment-runbook.md`](./deployment-runbook.md) carries both, in its import sequence, between the preview-problem step and the commit step.

Every gate below tests state that the commit creates. An Update Set whose customer updates did not attach to its header commits without applying any record: the platform reports success, the scope is never created, and every gate then fails and initiates a rollback of an application that was never installed. The retrieved update set's `state` does not distinguish that outcome from a complete import — it reaches `previewed` and then `committed` either way — and neither does the preview-problem step, which returns an empty error-type and warning-type set for an import that will apply nothing. There is no error field to consult either: `sys_remote_update_set` carries 28 columns and none of them is `error_detail`. The two checks below are what distinguish the two outcomes, and they are read before anything is committed.

`{ruset_sys_id}` is the `sys_id` of the retrieved update set record, captured when the XML was uploaded. `{record_count}` is the number of `<sys_update_xml>` elements in the uploaded file — **313** for the Update Set delivered with this package. [`../scripts/validate_update_set_xml.py`](../scripts/validate_update_set_xml.py) reports that count as it validates the file, and it is the same number on every deployment of a given file.

Neither request fits [Common request shape](#common-request-shape), so both are given in full below: `PRE-COMMIT-01` reads the Aggregate API rather than the Table API, and `PRE-COMMIT-02` reads one Table API record by `sys_id` rather than a query. Both carry the same `Authorization` and `Accept` headers as every gate, and no credential value appears in either.

| Check ID | Assertion | Request | Expected result | Pass condition | On failure |
| --- | --- | --- | --- | --- | --- |
| `PRE-COMMIT-01` | Every customer update in the uploaded file attached to the retrieved update set header. | `GET {SERVICENOW_INSTANCE_URL}/api/now/stats/sys_update_xml?sysparm_query=remote_update_set={ruset_sys_id}&sysparm_count=true` | `HTTP 200` with body `{"result":{"stats":{"count":"313"}}}`. | Status is exactly `200` and `result.stats.count` equals `{record_count}`, that is `313`. | **Do not commit.** A count of `0` means no customer update carried the header `sys_id`, so every record loaded orphaned. A count between `1` and `{record_count}` minus one means only some of them carried it. Either outcome, or any status other than `200`. Report `PRE-COMMIT-01` with the count observed, then clear the failed import by [Removing a failed retrieved update set](#removing-a-failed-retrieved-update-set), correct the Update Set XML, and restart the import sequence from its first step. |
| `PRE-COMMIT-02` | The completed preview found that many records to apply. | `GET {SERVICENOW_INSTANCE_URL}/api/now/table/sys_remote_update_set/{ruset_sys_id}?sysparm_fields=state,summary,inserted,updated,deleted,collisions` | `HTTP 200` with `state` `previewed` and `summary` `313`. | Status is exactly `200`, `state` is exactly `previewed`, and `summary` equals `{record_count}`, that is `313`. | **Do not commit.** A `summary` of `0` means the preview found nothing to apply and the commit would install nothing. A `summary` below `{record_count}` means it found only part of the file. A `state` other than `previewed` means the preview has not completed and the check was read too early. Report `PRE-COMMIT-02` with all six field values observed; treat a `summary` shortfall as `PRE-COMMIT-01` is treated, and re-read a `state` shortfall once the preview completes. |

Neither check initiates the rollback. The rollback deletes the `sys_scope` record, and at this point in the sequence nothing has been committed and no scope exists; the remedy is to remove the retrieved update set by the procedure below and re-import.

### Removing a failed retrieved update set

This procedure deletes records, so it is stated as a sequence with an ownership proof rather than as an instruction to delete. **`{ruset_sys_id}` is the only identifier it acts on**, and it is the `sys_id` captured from the upload step of *this* run. A run that cannot produce that identifier does not use this procedure at all.

| Step | Action | Assertion before proceeding |
| --- | --- | --- |
| 1 | Confirm the identifier names one record, and read its name and state. `GET {SERVICENOW_INSTANCE_URL}/api/now/table/sys_remote_update_set/{ruset_sys_id}?sysparm_fields=sys_id,name,state,sys_created_on,sys_created_by` | `HTTP 200`, exactly one record, its `sys_id` equal to `{ruset_sys_id}`, and its `name` equal to the unique run name this run uploaded. **`HTTP 404`, a differing `sys_id` or a differing `name` stops the procedure** — the identifier does not name this run's import, and nothing is deleted. |
| 2 | Enumerate what would be removed, and record the count. `GET {SERVICENOW_INSTANCE_URL}/api/now/stats/sys_update_xml?sysparm_query=remote_update_set={ruset_sys_id}&sysparm_count=true` | `HTTP 200`. Record the count in the deployment log **before** step 3. This is the number `PRE-COMMIT-01` reported, and it is the number of customer updates the deletion will take with it. |
| 3 | Delete only the header record. `DELETE {SERVICENOW_INSTANCE_URL}/api/now/table/sys_remote_update_set/{ruset_sys_id}` | `HTTP 204`. The platform removes the header's own customer updates with it; **no request is ever issued against `sys_update_xml` directly**, and no query-based deletion is performed on any table. |
| 4 | Confirm the removal. `GET {SERVICENOW_INSTANCE_URL}/api/now/table/sys_remote_update_set/{ruset_sys_id}?sysparm_fields=sys_id` | `HTTP 404`. Record the outcome. |

**Three prohibitions apply, and each of them prevents a specific way of destroying another party's work.**

- **Never delete by name, by state, by creation date or by any other query.** A query-based deletion on `sys_remote_update_set` or `sys_update_xml` can match a retrieved update set that belongs to another deployment, another agent working the same instance in parallel, or an unrelated application. Only the exact `sys_id` from step 1 is ever deleted.
- **Never delete a record whose `name` does not match this run's unique run name.** The name carries the run identity defined under the upload step of [`./deployment-runbook.md`](./deployment-runbook.md), which is what makes ownership provable on a shared instance.
- **Where ownership cannot be proven, stop.** If `{ruset_sys_id}` was never captured, if step 1 returns a record this run did not upload, or if the instance holds orphaned customer updates with no header to attribute them to, **do not delete anything**. Report the observed state — the identifiers, counts and names read — and refer the cleanup to an instance administrator for manual remediation. An unclean instance is recoverable; a deletion that removed someone else's update set is not.

`PRE-COMMIT-02` tests `summary`, not the split beneath it. On a clean install `inserted` equals `summary` with `updated` and `deleted` `0`; re-importing the same file over records that already exist reports the same `summary` with the total distributed across `inserted` and `updated` instead. The split is recorded as evidence rather than asserted, so a legitimate re-deployment does not fail the check. `collisions` is `0` on a clean instance, and a non-zero value is surfaced by the preview-problem step that precedes these two checks.

## Requirements carried to the deployment runbook

**Each row carries a stable identifier, `REQ-RB-01` through `REQ-RB-09`, and every reference to it from [`./deployment-runbook.md`](./deployment-runbook.md) cites that identifier rather than a row position.** A row inserted or reordered therefore breaks no cross-reference.

The forms below were established against the target instance and are stated here so that [`./deployment-runbook.md`](./deployment-runbook.md) is specified against them. This document does not restate that runbook's steps; each row names one value or route the runbook is required to use, and the form that must not be used in its place.

| ID | # | Requirement on the runbook | Required form | Form that must not be used |
| --- | --- | --- | --- | --- |
| `REQ-RB-01` | 1 | The pre-flight check that the instance is not mid-upgrade must match an actual field. | `GET /api/now/table/sys_upgrade_history?sysparm_limit=1&sysparm_query=upgrade_finishedISEMPTY`, and zero records means the instance is idle. | `sysparm_query=state=executing`. `sys_upgrade_history` carries no `state` field, so the condition is dropped and the request returns the instance's entire upgrade history — which the check reads as an upgrade in progress and aborts every deployment. |
| `REQ-RB-02` | 2 | The Update Set XML must be uploaded through the platform's import route. | The XML import route: establish a session with a form login at `POST /login.do`, read `sysparm_ck` from `GET /upload.do?sysparm_referring_url=sys_remote_update_set_list.do&sysparm_target=sys_remote_update_set`, then post the file as `multipart/form-data` to `POST /sys_upload.do`. | `POST /api/now/table/sys_remote_update_set` with `Content-Type: application/xml`. The Table API does not accept an update-set payload and returns `HTTP 400`. |
| `REQ-RB-03` | 3 | The multipart upload must order its parts with the file last. | `sysparm_ck`, `sysparm_upload_prefix`, `sysparm_referring_url` and `sysparm_target` first, then `attachFile` as the final part. | Any order placing `attachFile` before the other parts. The request then returns `HTTP 200` while importing nothing, so the sequence proceeds against an update set that does not exist. |
| `REQ-RB-04` | 4 | The retrieved update set must be identified by the `sys_id` of the record the upload created, under a name unique to the run. | Upload under a run-unique `<name>`, then resolve that exact name to one `sys_id` and require exactly one match. | Selecting the most recently created `sys_remote_update_set` record, or resolving a fixed name that a retry or a parallel clone can also have created. Either form can select another run's record and then preview and commit it. |
| `REQ-RB-05` | 5 | The preview must be triggered through the platform's preview processor, and its response asserted before anything is polled. | `POST /xmlhttp.do` with `sysparm_processor=UpdateSetPreviewAjax`, `sysparm_scope=global`, `sysparm_ajax_processor_function=preview`, `sysparm_ajax_processor_sys_id={ruset_sys_id}` and `sysparm_ck`. Require `HTTP 200`, parse the response, and require the `answer` value to be a 32-character hexadecimal execution-tracker `sys_id` before polling begins. | `PATCH /api/now/table/sys_remote_update_set/{ruset_sys_id}` with body `{"state":"previewing"}`. That request returns `HTTP 200` and is ignored, so the sequence polls a preview that was never started. Equally, polling without having established the tracker identifier, which polls nothing. |
| `REQ-RB-06` | 6 | Progress must be polled on fields that reveal content, not only on status. | Poll `state` together with `summary`, `inserted`, `updated`, `deleted` and `collisions`, and require `summary` to equal the file's `<sys_update_xml>` count before the commit is issued. | Polling `state` alone. It reaches its success values for an update set that will apply nothing, so an empty import is indistinguishable from a complete one. |
| `REQ-RB-07` | 7 | Load and preview failures must be reported from fields that exist. | Report `state` — `error` is its failure value — together with the `message` of the execution tracker the preview returns, and the preview-problem records. | `sysparm_fields=state,error_detail`, and reporting `error_detail` on failure. `sys_remote_update_set` has no `error_detail` column, so the platform drops it from the response: a request for `state,error_detail` returns `state` only, and a runbook that logs `error_detail` logs nothing on every failure it handles. |
| `REQ-RB-08` | 8 | The pre-flight release check must read a property that exists. | `GET /api/now/table/sys_properties?sysparm_query=name=glide.war&sysparm_fields=value`, whose value names the release and patch level. | `glide.buildname` or `glide.buildtag`. Neither property exists on the instance, so the query returns an empty `result` array and the release cannot be established from it. |
| `REQ-RB-09` | 9 | The upload must be confirmed from the retrieved update set, not from an attachment. | Confirm the upload by reading the `sys_remote_update_set` records that carry the header name and resolving the one identifier the upload added, then read that record's `state`. | Looking for a `sys_attachment` record for the uploaded file. The XML import consumes the upload and retains no attachment row against `sys_remote_update_set`, so a step that waits for one waits indefinitely. |

## Gates 1 to 7 — entity table commit and posture (required)

Seven required gates, one per entity table, in the order the tables are declared in [`./data-model.md`](./data-model.md). Each gate establishes that its table **committed into the `x_bst_startuptrk` scope and committed closed**, by reading the table's own dictionary record rather than its rows.

Every gate uses the same shape, differing only in the table name: target `sys_db_object`, query `sysparm_query=name=<table>^sys_scope.scope=x_bst_startuptrk&sysparm_fields=name,access,read_access,ws_access&sysparm_limit=2`. `sysparm_fields` returns exactly the four values the pass condition tests and nothing else, so no application data can enter the evidence record — there is none in a dictionary row to begin with.

**This is a departure from the literal text of AAP section 0.11.2, and it is accepted explicitly rather than argued away as equivalent.** The AAP's post-commit step reads "a successful read on each of `x_bst_startuptrk_startup`, `_founder`, `_executive`, `_investor`, `_fundinground`, `_jobposting` and `_newsarticle`" — on its face a read of the table itself. What is delivered instead is a read of each table's own `sys_db_object` record. The reason a row read is not available is `D-310`, which sealed all ten application tables at `access` `package_private` with `read_access` and `ws_access` `false`, because a field-level read control can be defeated by query-predicate bisection, by the Aggregate API and by an unsecured cross-scope read, and prompt section 2.0 requires the base role to receive a genuine access denial on the seven premium fields. `D-311` is the decision that then expressed these seven gates as metadata reads. Both are recorded in [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md), and the posture, its alternative and its one residual risk are set out under [The native platform read route on the application tables, and why it is closed](./gaps-and-flags.md#the-native-platform-read-route-on-the-application-tables-and-why-it-is-closed).

**What the substituted form asserts, and what a human must sign.** The substitution is not a weakening: a row read would prove only that the table resolved, whereas this proves that the table resolved, that it belongs to the application's own scope rather than to Global, and that its three read-access flags committed at their closed values. That is stated as a fact about the two forms, not as a warrant for the departure. The warrant is a **named human acceptance**, recorded as `D-455`: [section B4a of `./validation-checklist.md`](./validation-checklist.md#b4a--the-substituted-table-gate-form-acceptance-blocking) is acceptance-blocking and unfilled on delivery, and it requires an actor and a date accepting that the seven table gates read dictionary records rather than rows. Until that row carries both, acceptance is not complete, whatever the eleven gates returned. It does not trigger the rollback, and it is not one of the fifteen acceptance-blocking checks — it is the named acceptance of how seven of those checks are expressed.

**An empty `result` array is a failure for these seven gates**, as it is for every other gate here. There is exactly one `sys_db_object` record per table, and it exists from the moment the table commits, so an empty result cannot mean "committed but empty" the way a row read could.

**Boolean fields arrive as the strings `true` and `false`.** The Table API returns `false` for a false checkbox in its default value form, so the pass conditions below compare against the four-character string `false`, not against a JSON boolean. A comparison written against `false` as a boolean will report a false failure on a correct deployment.

| Gate ID | Assertion | Target | Query | Expected result | Pass condition | On failure |
| --- | --- | --- | --- | --- | --- | --- |
| `GATE-TBL-01` | The `x_bst_startuptrk_startup` table committed into the `x_bst_startuptrk` scope and committed closed to every route outside it. | `sys_db_object` | `sysparm_query=name=x_bst_startuptrk_startup^sys_scope.scope=x_bst_startuptrk&sysparm_fields=name,access,read_access,ws_access&sysparm_limit=2` | `HTTP 200` with a `result` array holding **exactly one** record: `name` `x_bst_startuptrk_startup`, `access` `package_private`, `read_access` `false`, `ws_access` `false`. | Status is exactly `200`, `result` holds exactly one record, its `name` is exactly `x_bst_startuptrk_startup`, and its `access`, `read_access` and `ws_access` read exactly `package_private`, `false` and `false`. All four are asserted; none is recorded as evidence only. | Empty `result`: no dictionary record carries that name inside the scope, so the Startup table did not commit — or it committed into the Global scope, which the `sys_scope.scope` term excludes. Two records: the name is ambiguous on this instance; record both `sys_id` values and stop. Any of the three flags reading other than its closed value: the delivered dictionary record did not apply, and the table is reachable from outside the application. `HTTP 401` or `403`: the account lacks `admin` on `sys_db_object`. Any status other than `200`. Report `GATE-TBL-01` with the status and the four field values observed; initiate the rollback. |
| `GATE-TBL-02` | The `x_bst_startuptrk_founder` table committed into the `x_bst_startuptrk` scope and committed closed to every route outside it. | `sys_db_object` | `sysparm_query=name=x_bst_startuptrk_founder^sys_scope.scope=x_bst_startuptrk&sysparm_fields=name,access,read_access,ws_access&sysparm_limit=2` | `HTTP 200` with a `result` array holding **exactly one** record: `name` `x_bst_startuptrk_founder`, `access` `package_private`, `read_access` `false`, `ws_access` `false`. | Status is exactly `200`, `result` holds exactly one record, its `name` is exactly `x_bst_startuptrk_founder`, and its `access`, `read_access` and `ws_access` read exactly `package_private`, `false` and `false`. All four are asserted; none is recorded as evidence only. | Empty `result`: no dictionary record carries that name inside the scope, so the Founder table did not commit — or it committed into the Global scope, which the `sys_scope.scope` term excludes. Two records: the name is ambiguous on this instance; record both `sys_id` values and stop. Any of the three flags reading other than its closed value: the delivered dictionary record did not apply, and the table is reachable from outside the application. `HTTP 401` or `403`: the account lacks `admin` on `sys_db_object`. Any status other than `200`. Report `GATE-TBL-02` with the status and the four field values observed; initiate the rollback. |
| `GATE-TBL-03` | The `x_bst_startuptrk_executive` table committed into the `x_bst_startuptrk` scope and committed closed to every route outside it. | `sys_db_object` | `sysparm_query=name=x_bst_startuptrk_executive^sys_scope.scope=x_bst_startuptrk&sysparm_fields=name,access,read_access,ws_access&sysparm_limit=2` | `HTTP 200` with a `result` array holding **exactly one** record: `name` `x_bst_startuptrk_executive`, `access` `package_private`, `read_access` `false`, `ws_access` `false`. | Status is exactly `200`, `result` holds exactly one record, its `name` is exactly `x_bst_startuptrk_executive`, and its `access`, `read_access` and `ws_access` read exactly `package_private`, `false` and `false`. All four are asserted; none is recorded as evidence only. | Empty `result`: no dictionary record carries that name inside the scope, so the Executive table did not commit — or it committed into the Global scope, which the `sys_scope.scope` term excludes. Two records: the name is ambiguous on this instance; record both `sys_id` values and stop. Any of the three flags reading other than its closed value: the delivered dictionary record did not apply, and the table is reachable from outside the application. `HTTP 401` or `403`: the account lacks `admin` on `sys_db_object`. Any status other than `200`. Report `GATE-TBL-03` with the status and the four field values observed; initiate the rollback. |
| `GATE-TBL-04` | The `x_bst_startuptrk_investor` table committed into the `x_bst_startuptrk` scope and committed closed to every route outside it. | `sys_db_object` | `sysparm_query=name=x_bst_startuptrk_investor^sys_scope.scope=x_bst_startuptrk&sysparm_fields=name,access,read_access,ws_access&sysparm_limit=2` | `HTTP 200` with a `result` array holding **exactly one** record: `name` `x_bst_startuptrk_investor`, `access` `package_private`, `read_access` `false`, `ws_access` `false`. | Status is exactly `200`, `result` holds exactly one record, its `name` is exactly `x_bst_startuptrk_investor`, and its `access`, `read_access` and `ws_access` read exactly `package_private`, `false` and `false`. All four are asserted; none is recorded as evidence only. | Empty `result`: no dictionary record carries that name inside the scope, so the Investor table did not commit — or it committed into the Global scope, which the `sys_scope.scope` term excludes. Two records: the name is ambiguous on this instance; record both `sys_id` values and stop. Any of the three flags reading other than its closed value: the delivered dictionary record did not apply, and the table is reachable from outside the application. `HTTP 401` or `403`: the account lacks `admin` on `sys_db_object`. Any status other than `200`. Report `GATE-TBL-04` with the status and the four field values observed; initiate the rollback. |
| `GATE-TBL-05` | The `x_bst_startuptrk_fundinground` table committed into the `x_bst_startuptrk` scope and committed closed to every route outside it. | `sys_db_object` | `sysparm_query=name=x_bst_startuptrk_fundinground^sys_scope.scope=x_bst_startuptrk&sysparm_fields=name,access,read_access,ws_access&sysparm_limit=2` | `HTTP 200` with a `result` array holding **exactly one** record: `name` `x_bst_startuptrk_fundinground`, `access` `package_private`, `read_access` `false`, `ws_access` `false`. | Status is exactly `200`, `result` holds exactly one record, its `name` is exactly `x_bst_startuptrk_fundinground`, and its `access`, `read_access` and `ws_access` read exactly `package_private`, `false` and `false`. All four are asserted; none is recorded as evidence only. | Empty `result`: no dictionary record carries that name inside the scope, so the Funding round table did not commit — or it committed into the Global scope, which the `sys_scope.scope` term excludes. Two records: the name is ambiguous on this instance; record both `sys_id` values and stop. Any of the three flags reading other than its closed value: the delivered dictionary record did not apply, and the table is reachable from outside the application. `HTTP 401` or `403`: the account lacks `admin` on `sys_db_object`. Any status other than `200`. Report `GATE-TBL-05` with the status and the four field values observed; initiate the rollback. |
| `GATE-TBL-06` | The `x_bst_startuptrk_jobposting` table committed into the `x_bst_startuptrk` scope and committed closed to every route outside it. | `sys_db_object` | `sysparm_query=name=x_bst_startuptrk_jobposting^sys_scope.scope=x_bst_startuptrk&sysparm_fields=name,access,read_access,ws_access&sysparm_limit=2` | `HTTP 200` with a `result` array holding **exactly one** record: `name` `x_bst_startuptrk_jobposting`, `access` `package_private`, `read_access` `false`, `ws_access` `false`. | Status is exactly `200`, `result` holds exactly one record, its `name` is exactly `x_bst_startuptrk_jobposting`, and its `access`, `read_access` and `ws_access` read exactly `package_private`, `false` and `false`. All four are asserted; none is recorded as evidence only. | Empty `result`: no dictionary record carries that name inside the scope, so the Job posting table did not commit — or it committed into the Global scope, which the `sys_scope.scope` term excludes. Two records: the name is ambiguous on this instance; record both `sys_id` values and stop. Any of the three flags reading other than its closed value: the delivered dictionary record did not apply, and the table is reachable from outside the application. `HTTP 401` or `403`: the account lacks `admin` on `sys_db_object`. Any status other than `200`. Report `GATE-TBL-06` with the status and the four field values observed; initiate the rollback. |
| `GATE-TBL-07` | The `x_bst_startuptrk_newsarticle` table committed into the `x_bst_startuptrk` scope and committed closed to every route outside it. | `sys_db_object` | `sysparm_query=name=x_bst_startuptrk_newsarticle^sys_scope.scope=x_bst_startuptrk&sysparm_fields=name,access,read_access,ws_access&sysparm_limit=2` | `HTTP 200` with a `result` array holding **exactly one** record: `name` `x_bst_startuptrk_newsarticle`, `access` `package_private`, `read_access` `false`, `ws_access` `false`. | Status is exactly `200`, `result` holds exactly one record, its `name` is exactly `x_bst_startuptrk_newsarticle`, and its `access`, `read_access` and `ws_access` read exactly `package_private`, `false` and `false`. All four are asserted; none is recorded as evidence only. | Empty `result`: no dictionary record carries that name inside the scope, so the News article table did not commit — or it committed into the Global scope, which the `sys_scope.scope` term excludes. Two records: the name is ambiguous on this instance; record both `sys_id` values and stop. Any of the three flags reading other than its closed value: the delivered dictionary record did not apply, and the table is reachable from outside the application. `HTTP 401` or `403`: the account lacks `admin` on `sys_db_object`. Any status other than `200`. Report `GATE-TBL-07` with the status and the four field values observed; initiate the rollback. |

These seven gates are the machine-checkable half of prompt section 10.0 criterion 1 — they establish that each of the seven entity tables exists and carries the sealed posture. `GATE-SEC-04` establishes that the sealed tables are readable on the application's own ACL-respecting path, and `GATE-COL-01` below strengthens the existence check into a column count, as an acceptance-required check rather than as part of the rollback contract. The field-by-field half, which walks all 53 columns against the instance dictionary, is covered by [`./validation-checklist.md`](./validation-checklist.md). The per-table column split, for that walk, is Startup 12, Founder 6, Executive 6, Investor 6, Funding round 8, Job posting 9, News article 6; 12 + 6 + 6 + 6 + 8 + 9 + 6 = 53.

## Gates 8 to 10 — role records (required)

Three gates, one per role the application declares. Every role name is written fully qualified with the dot separator, exactly as [`./access-control.md`](./access-control.md) records it. No bare, abbreviated or underscore form of a role name is valid in these gates.

Each gate targets `sys_user_role` and matches its role by exact name. The pass condition is a record count: the request returns `HTTP 200` whether or not the role exists, so the count is what each gate tests.

| Gate ID | Assertion | Target | Query | Expected result | Pass condition | On failure |
| --- | --- | --- | --- | --- | --- | --- |
| `GATE-ROLE-01` | Exactly one `sys_user_role` record named `x_bst_startuptrk.admin` exists. | `sys_user_role` | `sysparm_query=name=x_bst_startuptrk.admin` | `HTTP 200` with a `result` array holding exactly 1 record whose `name` is `x_bst_startuptrk.admin`. | Status is exactly `200` and `result` holds exactly 1 record. | 0 records: the role did not commit. More than 1 record: duplicate role records. Either outcome, or any status other than `200`. Report `GATE-ROLE-01`; initiate rollback. |
| `GATE-ROLE-02` | Exactly one `sys_user_role` record named `x_bst_startuptrk.user` exists. | `sys_user_role` | `sysparm_query=name=x_bst_startuptrk.user` | `HTTP 200` with a `result` array holding exactly 1 record whose `name` is `x_bst_startuptrk.user`. | Status is exactly `200` and `result` holds exactly 1 record. | 0 records: the role did not commit. More than 1 record: duplicate role records. Either outcome, or any status other than `200`. Report `GATE-ROLE-02`; initiate rollback. |
| `GATE-ROLE-03` | Exactly one `sys_user_role` record named `x_bst_startuptrk.premium_user` exists. | `sys_user_role` | `sysparm_query=name=x_bst_startuptrk.premium_user` | `HTTP 200` with a `result` array holding exactly 1 record whose `name` is `x_bst_startuptrk.premium_user`. | Status is exactly `200` and `result` holds exactly 1 record. | 0 records: the role did not commit. More than 1 record: duplicate role records. Either outcome, or any status other than `200`. Report `GATE-ROLE-03`; initiate rollback. |

An empty `result` array is a **failure** for these three gates, as it is for `GATE-SCOPE-01` and for every gate and check in this document.

## Gate 11 — the scope record (required)

One gate, targeting `sys_scope` and matching the application scope by exact name.

| Gate ID | Assertion | Target | Query | Expected result | Pass condition | On failure |
| --- | --- | --- | --- | --- | --- | --- |
| `GATE-SCOPE-01` | Exactly one `sys_scope` record whose `scope` is `x_bst_startuptrk` exists. | `sys_scope` | `sysparm_query=scope=x_bst_startuptrk` | `HTTP 200` with a `result` array holding exactly 1 record whose `scope` is `x_bst_startuptrk`. | Status is exactly `200` and `result` holds exactly 1 record. | 0 records: the scoped application did not commit. More than 1 record: duplicate scope records. Either outcome, or any status other than `200`. Report `GATE-SCOPE-01`; initiate rollback. |

The rollback acts on this same `sys_scope` record, and this gate is where its identifier is captured: **record the `sys_id` this gate returns in the deployment log**, because the rollback deletes that exact identifier and nothing else. The rollback is permitted only on a proven clean install, only when this gate returned exactly one record, and only against the `sys_id` recorded here; a count of zero or above one blocks it. The full procedure, with every assertion and every prohibition, is specified in [`./deployment-runbook.md`](./deployment-runbook.md).

## Three classes of check, and what each one blocks

A check in this document belongs to exactly one of three classes. **The distinction is between what triggers the irreversible rollback and what blocks acceptance — those are not the same thing**, and conflating them is what would let a check that acceptance genuinely depends on be recorded as merely advisory.

| Class | Members | Blocks acceptance? | Triggers rollback? | What the class covers |
| --- | --- | --- | --- | --- |
| **1 — required deployment gate** | `GATE-TBL-01` to `-07`, `GATE-ROLE-01` to `-03`, `GATE-SCOPE-01` — **11** | **Yes** | **Yes** | These are the acceptance set AAP section 0.11.2 and the deployment environment define. A failure means the commit did not produce the application, so the scope is deleted and the deployment retried. |
| **2 — acceptance-required, non-rollback** | `GATE-COL-01`, `GATE-SEC-01`, `GATE-SEC-02`, `GATE-SEC-03` — **4** | **Yes** | **No** | `GATE-COL-01`: success criterion 1 requires all 53 binding columns, and this check is how their **count** is machine-verified. The three `GATE-SEC` checks: each observes an access-posture fact the required eleven cannot see. A failure of any of the four means the delivered artifact is wrong in a way acceptance cannot pass over — but the remedy is to correct the Update Set and re-import, not to delete a scope whose tables and roles all committed correctly. A `GATE-SEC` failure may alternatively be closed by the platform owner recording written acceptance of the named exposure; `GATE-COL-01` has no such route. |
| **3 — non-normative diagnostic** | `GATE-SEC-04` — **1** | No | No | The one check here that is not an HTTP request: a background script a human runs in the platform UI, so no deployment pipeline can assert on it. It is recorded on every deployment because it exercises the one read path the sealed tables leave open, but the posture it reports is not part of any success criterion's pass condition. A failure is reported, investigated and carried with the deployment record. |

**Class 2 exists because of a real asymmetry, not as a hedge.** Criterion 1 in [`./validation-checklist.md`](./validation-checklist.md) asks that all seven tables exist **with 100 % of their fields**, and it evidences the field list two ways: a manual field-by-field walk of all 53 columns, and this automated count. Classing the count as merely advisory would leave the only machine-checkable evidence of the binding field list carrying no weight — so a deployment that committed 45 columns would clear every check that mattered and be recorded as accepted. Classing it as a rollback trigger would be equally wrong: deleting the scope discards seven correctly committed tables and three correctly committed roles to fix a dictionary defect that lives in the Update Set.

So `GATE-COL-01` **blocks acceptance and does not trigger rollback**, and both halves of that are stated wherever it appears.

**The same asymmetry puts `GATE-SEC-01` to `GATE-SEC-03` in class 2, and it is why they are not diagnostics.** Each names an exposure rather than a preference: `GATE-SEC-01` failing means raw staged payloads are reachable over an external route, `GATE-SEC-02` failing means an application table permits a cross-scope write, and `GATE-SEC-03` failing means the REST endpoints carry no authorisation. A deployment in any of those states cannot be recorded as accepted merely because the eleven gates passed — which is exactly what classing them as advisory would permit. Deleting the scope would be equally wrong, and for the same reason it is wrong for `GATE-COL-01`: the defect lives in the delivered dictionary or access-control records, not in a scope whose tables and roles committed correctly. The one route out that `GATE-COL-01` does not have is a written acceptance of the named exposure recorded by the platform owner, because an exposure can be a knowing operational choice in a way a wrong column count cannot.

**The single class 3 diagnostic decides nothing.** Read `GATE-SEC-04`, record its outcome, and act on a failure as its own **On failure** cell directs — which is neither the rollback nor an acceptance hold. No document in this package may cite it as a precondition of any work, and no operator may hold a deployment on it.

### Acceptance-required check 1 — entity column count

One check establishing that the 53 binding columns of prompt section 1.0 committed, by counting the entity tables' `sys_dictionary` column records. `sys_dictionary` carries one record per column plus one collection record per table, so the seven entity tables contribute 53 column records and 7 collection records; the query below excludes the collection records by requiring a non-empty `element`.

| Gate ID | Assertion | Target | Query | Expected result | Pass condition | On failure |
| --- | --- | --- | --- | --- | --- | --- |
| `GATE-COL-01` | The seven entity tables carry exactly 53 columns between them. | `sys_dictionary` | `sysparm_query=nameINx_bst_startuptrk_startup,x_bst_startuptrk_founder,x_bst_startuptrk_executive,x_bst_startuptrk_investor,x_bst_startuptrk_fundinground,x_bst_startuptrk_jobposting,x_bst_startuptrk_newsarticle^elementISNOTEMPTY&sysparm_fields=name,element&sysparm_limit=200` | `HTTP 200` with a `result` array holding exactly 53 records. | Status is exactly `200` and `result` holds exactly 53 records. | Fewer than 53: one or more columns did not commit. More than 53: an unexpected column exists, which breaches the binding-and-complete field list. Either outcome, or any status other than `200`. Report `GATE-COL-01` with the count observed and the per-table split. **Acceptance is blocked**: correct the Update Set and re-import. **No rollback** — a count below 53 with all eleven required gates passing means the tables committed but at least one column did not, and deleting the scope would discard working artifacts to fix a dictionary defect that lives in the source file. |

An encoded query is written `[field][operator][value]` with **no separator between the operator and its first operand**, which is why `nameIN` runs straight into `x_bst_startuptrk_startup` above and why `elementISNOTEMPTY` carries no operand at all. A space after `IN` is not ignored: it becomes the first character of the first operand, so the first table would be looked up under a leading space, would match nothing, and the check would report 45 columns instead of 53 and raise a false alarm on a deployment that had in fact succeeded. The seven operands are separated by bare commas with no spaces, and each is spelled exactly as `sys_db_object.name` spells it — the same seven names `GATE-TBL-01` through `GATE-TBL-07` read. Confirm all seven statically against [`./data-model.md`](./data-model.md) before the deployment runs; the HTTP client URL-encodes the query, so the commas and the `^` need no manual escaping.

The per-table split, for diagnosing a count that is off: Startup 12, Founder 6, Executive 6, Investor 6, Funding round 8, Job posting 9, News article 6. 12 + 6 + 6 + 6 + 8 + 9 + 6 = 53. The three supporting tables are excluded from this check; their columns are documented in [`./data-model.md`](./data-model.md).

### The access posture and the secured read path — `GATE-SEC-01` to `GATE-SEC-04`

Four checks in total: **three acceptance-required checks** recording that the access posture the application depends on actually committed, followed by the **single class 3 diagnostic** that exercises the read path those checks leave open. The posture is **uniform across all ten tables** — every one of them is `package_private` with `read_access` and `ws_access` `false` and every write, configuration and schema flag `false` — and `GATE-SEC-01` to `GATE-SEC-03` assert it in one read each, across the ten together, rather than table by table. **All three are class 2**: recorded on every deployment, **acceptance-blocking**, and never rollback-triggering — each names an exposure rather than a preference, as [Three classes of check](#three-classes-of-check-and-what-each-one-blocks) sets out, and each may alternatively be closed by the platform owner recording written acceptance of the named exposure. `GATE-SEC-04`, below them, is the class 3 diagnostic and decides nothing.

`GATE-SEC-01` deliberately overlaps gates 1 to 7, which assert the same three flags per table. The overlap is the point: the seven gates fail one table at a time and name it, while `GATE-SEC-01` answers "are all ten closed" in a single read and is the check that would notice a supporting table drifting open, which no required gate covers.

**No check in this document touches anything outside the `x_bst_startuptrk` scope, and none instructs an operator to change instance configuration.** Prompt section 6.0 forbids the scoped application from modifying anything outside its scope, and that prohibition binds this document's remedies as much as it binds the Update Set: a check whose remedy is a Global-scope property change would breach it. Instance-level hardening, where an operator wants it, is a separate authorised activity with its own review and is not part of this deployment — which is why the XML entity-resolution configuration is recorded below as an observation rather than as a check.

| Check ID | Assertion | Target | Query | Expected result | Pass condition | On failure |
| --- | --- | --- | --- | --- | --- | --- |
| `GATE-SEC-01` | Every one of the ten application tables is reachable from the `x_bst_startuptrk` scope only, over no external route. | `sys_db_object` | `sysparm_query=nameSTARTSWITHx_bst_startuptrk_^access=package_private^read_access=false^ws_access=false&sysparm_fields=name,access,read_access,ws_access&sysparm_limit=50` | `HTTP 200` with a `result` array holding exactly 10 records — the seven entity tables and the three supporting tables, all with `access` `package_private`, `read_access` `false` and `ws_access` `false`. | Status is exactly `200` and `result` holds exactly 10 records. | Fewer than 10: at least one table is open on a route the application's own controls never see. Take the difference between the ten names in [`./data-model.md`](./data-model.md) and the names returned — each missing name is a table whose read posture did not commit. The staging table is the one that matters most, because it holds verbatim upstream payloads and unvalidated personal data. More than 10: a table outside the delivered set carries the scope prefix. Report `GATE-SEC-01` with the names observed and investigate. **Acceptance is blocked** — a table outside the scope's reach exposes raw staged payloads over an external route — until the dictionary records are corrected and re-imported, or the platform owner records written acceptance of the named exposure. **No rollback**: the defect lives in the Update Set, and a missing entity table will already have failed its own required gate. |
| `GATE-SEC-02` | No application table permits any cross-scope write, configuration or schema operation. | `sys_db_object` | `sysparm_query=nameSTARTSWITHx_bst_startuptrk_^create_access=false^update_access=false^delete_access=false^alter_access=false^configuration_access=false&sysparm_fields=name,create_access,update_access,delete_access,alter_access,configuration_access&sysparm_limit=50` | `HTTP 200` with a `result` array holding exactly 10 records. | Status is exactly `200` and `result` holds exactly 10 records. | Fewer than 10: at least one table accepts writes or schema changes from outside the scope, which would let an out-of-scope caller alter application data through a route the application's own controls never see. **This is the posture check that matters.** Report `GATE-SEC-02` with the names of the tables missing from the result and treat it as a blocking defect in the delivered artifact: correct the dictionary records, re-export and re-import, or record the platform owner's written acceptance of the exposure. **Acceptance is blocked** and the application is **not put into use** while this check is failing. **No rollback** — the defect lives in the Update Set. |
| `GATE-SEC-03` | Both REST endpoint access controls committed. | `sys_security_acl` | `sysparm_query=type=REST_Endpoint^nameSTARTSWITHBoston Startup Tracker API&sysparm_fields=name,type,operation` | `HTTP 200` with a `result` array holding exactly 2 records, `Boston Startup Tracker API read` and `Boston Startup Tracker API write`, both with `operation` `execute`. | Status is exactly `200`, `result` holds exactly 2 records, and both carry `operation` `execute`. | Fewer than 2: endpoint authorisation on the Scripted REST API falls back to the platform's broad default REST access control, which admits any authenticated internal user. Report `GATE-SEC-03` and correct it before the API is exposed. **Acceptance is blocked** until both controls are corrected and re-imported, or the exposure is accepted in writing by the platform owner. **No rollback.** |

**Why `GATE-SEC-01` expects ten and not three.** An earlier revision delivered the seven entity tables `access` `public` with `read_access` and `ws_access` `true`, so that the eleven required gates could read each table's rows directly, and `GATE-SEC-01` then expected the three supporting tables alone. That posture opened a second read route to entity data — the native Table API for an authenticated caller, and unsecured record access for a script in any other application scope — and that route sits outside the application's fixed-window rate limiter and outside the two `REST_Endpoint` execution controls. **All ten tables are now closed**, the seven required table gates read the dictionary instead of the rows, and this check expects all ten. There is no second read route to compensate for, so the residual-risk register that accompanied the open posture no longer applies; the current disposition is recorded in [`./gaps-and-flags.md`](./gaps-and-flags.md) and the decision, its alternatives and the superseded one in [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md).

#### `GATE-SEC-04` — the secured read path, after the commit

`GATE-SEC-04` is the one check in this document that is **not** an HTTP request, because the path it exercises has no external route by design. It is a background script run from **System Definition > Scripts - Background** with the application picker set to **Boston Startup Tracker**, and it prints one line per entity table.

It reads through `GlideRecordSecure`, so it evaluates the same table-level and field-level read controls every caller-facing read evaluates. Run it as the deployment administrator to establish that the tables resolve and the secured path works; the per-role, per-field half of the access-control contract is **not** this check's business and is established by the twenty-one impersonated assertions of [`../docs/manual-build/05-atf-test-suites.md`](./manual-build/05-atf-test-suites.md), because an administrator overrides record access controls and would read every premium field regardless.

```javascript
(function securedReadDiagnostic() {
    var tables = ['x_bst_startuptrk_startup', 'x_bst_startuptrk_founder',
        'x_bst_startuptrk_executive', 'x_bst_startuptrk_investor',
        'x_bst_startuptrk_fundinground', 'x_bst_startuptrk_jobposting',
        'x_bst_startuptrk_newsarticle'];
    var i = 0;
    for (i = 0; i !== tables.length; i++) {
        var rows = new GlideRecordSecure(tables[i]);
        rows.setLimit(1);
        rows.query();
        gs.info('GATE-SEC-04 ' + tables[i]
            + ' valid=' + rows.isValid()
            + ' can_read=' + rows.canRead()
            + ' rows_visible=' + rows.getRowCount());
    }
})();
```

| Check ID | Assertion | Mechanism | Expected result | Pass condition | On failure |
| --- | --- | --- | --- | --- | --- |
| `GATE-SEC-04` | Each of the seven entity tables resolves and is readable through the ACL-respecting path after the commit. | The background script above, run in the `x_bst_startuptrk` scope. | Seven log lines, each reading `valid=true can_read=true`. `rows_visible` is `0` on a clean install and is recorded as evidence, not asserted. | Seven lines are printed, and every one reads `valid=true` and `can_read=true`. | `valid=false`: the table did not commit, which `GATE-TBL-01` through `GATE-TBL-07` would already have failed on. `can_read=false`: the table committed but its table-level read control did not, so no caller can read it and every list response will answer `403`; check the seven read controls in [`./access-control.md`](./access-control.md). Report `GATE-SEC-04` with the seven lines observed. **No rollback**, and acceptance is not blocked. |

## Instance prerequisite for XML entity resolution

**This is not a gate.** It is a read-only observation of instance configuration that the application relies on and deliberately does **not** ship: the properties live in the Global scope, and prompt section 6.0 forbids the scoped application from modifying anything outside `x_bst_startuptrk`. It is recorded here so the deploying operator knows the condition exists and who owns it, and it is stated as a prerequisite rather than an acceptance criterion because **nothing in this delivery can set it, test it into compliance, or be rolled back to fix it.**

| Observation | Target | Query | Reading |
| --- | --- | --- | --- |
| Whether the instance refuses XML entity resolution. | `sys_properties` | `sysparm_query=nameINglide.stax.allow_entity_resolution,glide.stax.whitelist_enabled&sysparm_fields=name,value` | The hardened configuration is `glide.stax.allow_entity_resolution` `false` and `glide.stax.whitelist_enabled` `true`. Record both values, or their absence, in the deployment log. |

**What to do with the reading.** Record it and continue. A value other than the hardened one is **not** a deployment failure, is **not** a gate failure, and **must not** trigger the rollback — the rollback deletes this application's scope, which would not change a Global property by one byte. If the reading is not the hardened configuration, report it to the platform owner responsible for instance configuration as a finding against the instance, outside this delivery. This delivery neither sets these properties nor requires the operator to set them.

**The application removes its own endpoints from that surface, which is why this observation is defence in depth rather than a dependency.** The Scripted REST API declares `application/json` for both `consumes` and `produces` on the definition and on all 31 operations, and every body-bearing operation refuses a request that does not declare `application/json` with `HTTP 415` before the body is read, so no XML body reaches a parser through this application. **That is a statement about this application's endpoints and about nothing else**: the `glide.stax.*` properties govern the platform's own XML parsing wherever the platform parses XML — the Update Set import route among other places — and whether that is the same parser is the platform owner's question, not one this document answers. The companion allowlist property `glide.xml.entity.whitelist` is not read at all, because its value is instance-specific and no correct value can be stated for it here.

## Gate roll-up

**The acceptance contract is eleven gates.** 7 entity-table gates + 3 role-record gates + 1 scope-record gate = **11 required gates**, exactly the set AAP section 0.11.2 and the deployment environment define.

1 column-count check + 3 access-posture checks = **4 acceptance-required, non-rollback checks**, class 2.

1 secured-read check = **1 non-normative diagnostic**, class 3.

**Sixteen checks in total: 15 of them block acceptance, 11 of those 15 trigger rollback, and the 1 class 3 diagnostic blocks nothing.** 11 plus 4 plus 1 is 16, and 11 plus 4 is the 15. The classes are defined under [Three classes of check](#three-classes-of-check-and-what-each-one-blocks).

The eleven required gates, in the order they are run:

| # | Gate ID | Assertion |
| --- | --- | --- |
| 1 | `GATE-TBL-01` | The `x_bst_startuptrk_startup` table committed, and committed sealed against every external route. |
| 2 | `GATE-TBL-02` | The `x_bst_startuptrk_founder` table committed, and committed sealed against every external route. |
| 3 | `GATE-TBL-03` | The `x_bst_startuptrk_executive` table committed, and committed sealed against every external route. |
| 4 | `GATE-TBL-04` | The `x_bst_startuptrk_investor` table committed, and committed sealed against every external route. |
| 5 | `GATE-TBL-05` | The `x_bst_startuptrk_fundinground` table committed, and committed sealed against every external route. |
| 6 | `GATE-TBL-06` | The `x_bst_startuptrk_jobposting` table committed, and committed sealed against every external route. |
| 7 | `GATE-TBL-07` | The `x_bst_startuptrk_newsarticle` table committed, and committed sealed against every external route. |
| 8 | `GATE-ROLE-01` | Exactly one `sys_user_role` record named `x_bst_startuptrk.admin` exists. |
| 9 | `GATE-ROLE-02` | Exactly one `sys_user_role` record named `x_bst_startuptrk.user` exists. |
| 10 | `GATE-ROLE-03` | Exactly one `sys_user_role` record named `x_bst_startuptrk.premium_user` exists. |
| 11 | `GATE-SCOPE-01` | Exactly one `sys_scope` record whose `scope` is `x_bst_startuptrk` exists. |

**The aggregate rollback pass condition is that all eleven required gates pass — `11 of 11`.** There is no partial pass. No required gate may be skipped, deferred or waived, and no other check may be substituted for one.

The four acceptance-required, non-rollback checks:

| # | Check ID | Assertion | Blocks acceptance | Triggers rollback |
| --- | --- | --- | --- | --- |
| A1 | `GATE-COL-01` | The seven entity tables carry exactly 53 columns between them. | **Yes** | No |
| A2 | `GATE-SEC-01` | All ten application tables are reachable from the `x_bst_startuptrk` scope only. | **Yes** | No |
| A3 | `GATE-SEC-02` | No application table permits any cross-scope write, configuration or schema operation. | **Yes** | No |
| A4 | `GATE-SEC-03` | Both REST endpoint access controls committed. | **Yes** | No |

**Together with the eleven above, these four are the acceptance decision: `15 of 15`.** `A2` to `A4` are the only checks in this set whose failure has a second remedy — a written acceptance of the named exposure recorded by the platform owner — and `A1` has no such route.

The one non-normative diagnostic, recorded and never required:

| # | Check ID | Assertion |
| --- | --- | --- |
| D1 | `GATE-SEC-04` | Each of the seven entity tables resolves and is readable through the ACL-respecting path after the commit. |

**The rollback pass condition** is that all eleven class 1 gates pass. There is no partial pass among them, none is advisory, and none may be skipped, deferred or waived.

**The acceptance pass condition** is that all eleven class 1 gates pass and all four class 2 checks pass — `GATE-COL-01` and `GATE-SEC-01` through `GATE-SEC-03` — **fifteen checks in total**. The single class 3 diagnostic, `GATE-SEC-04`, is run and recorded on every deployment whatever its outcome, and it never blocks acceptance. A class 2 failure leaves the deployment in place and blocks acceptance until the delivered artifact is corrected and re-imported, or — for one of the three `GATE-SEC` checks only — until the platform owner records written acceptance of the exposure in the evidence record; neither class 2 nor class 3 ever initiates the rollback. The **rollback** condition remains the eleven class 1 gates alone.

One further condition is recorded and is **not a check of this delivery at all**: the instance's XML entity-resolution configuration, under [Instance prerequisite for XML entity resolution](#instance-prerequisite-for-xml-entity-resolution). It is owned by the platform owner, is not settable or fixable from within this application, and is reported rather than gated. There is no `GATE-SEC-05` in this gate set.

`PRE-COMMIT-01` and `PRE-COMMIT-02` are preconditions of this gate set, not members of it, so neither count above is changed by them. They are equally not waivable: the eleven required gates are evaluated only on a deployment whose commit had records to apply.

Gates 1 to 7, `GATE-COL-01` and `GATE-SEC-04` cover the seven entity tables only. `GATE-SEC-01` covers all ten — `x_bst_startuptrk_m2m_round_investor`, `x_bst_startuptrk_ingest_staging` and `x_bst_startuptrk_rate_limit_counter` — and `GATE-SEC-02` covers all ten; those three supporting tables are otherwise documented in [`./data-model.md`](./data-model.md).

The three supporting tables — `x_bst_startuptrk_m2m_round_investor`, `x_bst_startuptrk_ingest_staging` and `x_bst_startuptrk_rate_limit_counter` — carry no required gate. They are `package_private` with `ws_access` `false`, exactly as the seven entity tables now are, so no Table API read of them can succeed and none is attempted; they are documented in [`./data-model.md`](./data-model.md) and exercised by the Automated Test Framework suites built in [`./manual-build/05-atf-test-suites.md`](./manual-build/05-atf-test-suites.md).

### What a full pass does not establish

**Fifteen of fifteen is not "the application is delivered".** Every check in this document reads a record the **Update Set** committed, so a full pass establishes exactly that the declarative half of the deliverable installed correctly — the ten tables and their columns, choices and indexes, the three roles, the access controls, the eight Script Includes, the REST definition and its 31 operations, the 11 properties, the three business rules, the scheduled job, the views and the application menu.

**It establishes nothing about the artifacts the platform builds through its own interface, because the Update Set contains none of them.** The record counts in the delivered file are zero for every one of these types, and no gate here reads any of them:

| Artifact class | Record types, count in the Update Set | Built by |
| --- | --- | --- |
| The portal, its theme, the five pages and the eight widgets | `sp_portal`, `sp_theme`, `sp_page`, `sp_widget`, `sp_container`, `sp_row`, `sp_rectangle`, `sp_instance` — **0 of each** | [`./manual-build/04-service-portal-pages-and-widgets.md`](./manual-build/04-service-portal-pages-and-widgets.md) |
| The two Connection & Credential Aliases | **0** | [`./manual-build/01-connection-credential-aliases.md`](./manual-build/01-connection-credential-aliases.md) |
| The two Flow Designer ingestion flows | `sys_hub_flow` — **0** | [`./manual-build/02-flow-crunchbase-ingestion.md`](./manual-build/02-flow-crunchbase-ingestion.md) and [`./manual-build/03-flow-linkedin-ingestion.md`](./manual-build/03-flow-linkedin-ingestion.md) |
| The ten ATF suites and their 36 tests | `sys_atf_test`, `sys_atf_test_suite`, `sys_atf_step` — **0 of each** | [`./manual-build/05-atf-test-suites.md`](./manual-build/05-atf-test-suites.md) |

**The consequence to state plainly, because a reader of a green gate report will otherwise assume the opposite: immediately after the commit, none of the five Service Portal routes exists.** `/bst` resolves to nothing. That is the expected state, not a failure — **success criterion 5 is not evaluated at this point and must not be recorded as failing**, and neither may criterion 3's rate-limit assertions or criterion 4's scheduled runs, which likewise depend on artifacts built later. No check in this document is designed to detect their absence, and none should be added: the split between what travels in an Update Set and what does not is a platform constraint, and prompt section 11.0 answers it with manual build instructions rather than with more gates.

The runbook states the same boundary at the point an operator reaches it, with the consequence of each absence: [What is not installed, and what the gates deliberately do not test](./deployment-runbook.md#what-is-not-installed-and-what-the-gates-deliberately-do-not-test).

## Failure handling

On failure of any one of the **eleven required** gates:

0. **First establish that the response is a gate outcome at all.** If it is the sixth response form — `HTTP 200` with a non-JSON content type, an unparseable body, or no top-level `result` — this is **not a failure** and steps 1 to 3 do not apply: the gate is **not evaluated**, no rollback is initiated, and the run restarts from pre-flight 1 per [A `200` that is not an answer](#a-200-that-is-not-an-answer). Reaching step 3 on a sleeping or unauthenticated instance would delete a scope over a condition that is not a deployment defect.
1. Report the failing gate by its identifier, together with the HTTP status and the response body observed.
2. If the observed status is a **retryable server error** — `HTTP 500`, `502`, `503` or `504` — and the gate has not yet been retried, wait 30 seconds and reissue the identical request exactly once, per the [Transient-error retry rule](#transient-error-retry-rule). Evaluate the gate on that response and report the retry's status and body alongside the first.
3. Initiate the rollback when the pass condition still does not hold — that is, immediately for any status outside the retryable-server-error class, and for a status inside it only after the single retry has also failed. **The rollback is permitted only under the conditions [`./deployment-runbook.md`](./deployment-runbook.md) states**, which include a proven clean install and an exact scope identifier captured this run; where those conditions do not hold, report the failure and stop rather than delete.

The failing gate is reported before the rollback is initiated. A gate that passes on its retry is a pass, is recorded as such, and initiates no rollback.

**On failure of `GATE-COL-01`**, follow steps 1 and 2 above and then **stop without rolling back**. The deployment stays in place, and **acceptance is blocked**: record the observed column count and the per-table split, correct the Update Set so the seven entity tables carry exactly the 53 binding columns, and re-import. Do not delete the scope — the tables and roles committed correctly, and deleting them discards working artifacts to fix a dictionary defect that lives in the source file. Do not record criterion 1 as met while this check is failing.

**On failure of one of the three `GATE-SEC` access-posture checks**, no rollback is initiated under any circumstance, and **acceptance is blocked**. Follow steps 1 and 2 above, report the check by its identifier with the status and body observed, act on its own **On failure** cell, and record the outcome in the evidence record. The application is **not put into use** while one of them is failing: either the delivered posture is corrected and re-imported, or the platform owner records written acceptance of the named exposure in the evidence record. That policy applies to all three equally — a `GATE-SEC-01` failure exposes raw staged payloads to an external route and a `GATE-SEC-03` failure removes endpoint authorisation, neither of which is milder than the cross-scope write access `GATE-SEC-02` covers; the remedy there is to correct the dictionary records and re-import, not to destroy the installation.

`PRE-COMMIT-01` and `PRE-COMMIT-02` are handled differently, and their own rows state it: they are read before the commit, so a failure means the commit does not happen and there is no scope to roll back. The remedy is to remove the retrieved update set by [Removing a failed retrieved update set](#removing-a-failed-retrieved-update-set), correct the Update Set XML and restart the import sequence. The [Transient-error retry rule](#transient-error-retry-rule) applies to both of them as it does to the gates.

**The rollback has two branches, and the correct one depends on whether this deployment created the scope.** When the pre-flight scope check recorded a **clean** starting state, the rollback retrieves the `sys_scope` record whose `scope` is `x_bst_startuptrk` — the same record `GATE-SCOPE-01` tests, whose `sys_id` that gate records — and deletes **that exact identifier**, then confirms the seven entity tables no longer resolve, the three roles are gone and the scope record is gone. **That branch is irreversible, and it is guarded.** When the starting state was an **existing** installation, the scope is **never** deleted: the deployment's own update set is backed out, the eleven required gates are re-run to verify the pre-existing installation survived, and the failure is escalated to the application's owner. Both branches, every precondition on them, their trigger conditions and the wider failure matrix are specified in [`./deployment-runbook.md`](./deployment-runbook.md), which is authoritative for the branch selection.

## Evidence record

The operator records one row per pre-commit check, one row per required gate, one row for the acceptance-required check and one row per security check per deployment. The tables below are the evidence record for the machine-checkable gates, and [`./validation-checklist.md`](./validation-checklist.md) cites them as such.

The pre-commit checks are recorded first, because they are read before the commit that the gates below test:

| Check ID | Result | Timestamp (UTC) | Note |
| --- | --- | --- | --- |
| `PRE-COMMIT-01` | | | |
| `PRE-COMMIT-02` | | | |

For `PRE-COMMIT-01` record the count returned. For `PRE-COMMIT-02` record all six field values returned, so the `inserted`, `updated` and `deleted` split is on the record even though the pass condition tests `summary` alone. A deployment that did not reach the commit carries these two rows and no gate rows.

The eleven required gates are recorded next. **This table alone carries the acceptance decision.**

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
| **Aggregate** | | | `11 of 11` required gates must pass |

`GATE-COL-01` is recorded separately from the eleven, because it blocks acceptance without triggering rollback:

| Acceptance-required check ID | Result | Timestamp (UTC) | Observed count and per-table split |
| --- | --- | --- | --- |
| `GATE-COL-01` | | | expected 53 = 12 + 6 + 6 + 6 + 8 + 9 + 6 |
| **Aggregate** | | | 15 of 15 acceptance-blocking checks required — the 11 gates above, this one and the three `GATE-SEC` access-posture checks below. `GATE-SEC-04` is recorded, never required |

The three access-posture checks are recorded next, and they **are** part of the acceptance set:

| Security check ID | Result | Timestamp (UTC) | Note, and the written acceptance recorded for any failure |
| --- | --- | --- | --- |
| `GATE-SEC-01` | | | |
| `GATE-SEC-02` | | | |
| `GATE-SEC-03` | | | |
| **Aggregate** | | | Acceptance-required, non-rollback. A failure blocks acceptance until the delivered records are corrected and re-imported, or until the platform owner records written acceptance of the named exposure in this row. |

The single non-normative diagnostic is recorded separately again, so a reader can never mistake it for part of the acceptance set:

| Diagnostic check ID | Result | Timestamp (UTC) | Note |
| --- | --- | --- | --- |
| `GATE-SEC-04` | | | seven log lines, each `valid=true can_read=true` |
| **Aggregate** | | | Non-normative. Recorded, not required. A failure here does not fail the deployment and does not block acceptance. |

The instance prerequisite is recorded as an observation rather than a result:

| Observation | Value read | Timestamp (UTC) | Reported to |
| --- | --- | --- | --- |
| `glide.stax.allow_entity_resolution` | | | |
| `glide.stax.whitelist_enabled` | | | |

Every table is filled in the same way. Record `pass` or `fail` in **Result**. Record the time of the request in **Timestamp (UTC)** in `YYYY-MM-DD HH:MM:SS` form. Record the observed HTTP status and the `result` record count in **Note**, and for a failing gate or check also the response body. For `GATE-TBL-01` through `GATE-TBL-07` record the four field values returned — `name`, `access`, `read_access` and `ws_access` — because all four are asserted, and a `fail` is diagnosed from which of them departed. For `GATE-COL-01` record the count returned **and** the per-table split, since a count that is off is diagnosed from the split. For the instance prerequisite, record each property value as read, or `absent`, and the name of the platform owner it was reported to where it is not the hardened value. Record no credential value in any field.

Where a gate was retried under the [Transient-error retry rule](#transient-error-retry-rule), record the retry in the same row: note the first status — whichever of `HTTP 500`, `502`, `503` or `504` was observed — the 30-second wait and the retry's status, and set **Timestamp (UTC)** to the retried request. **Result** carries the outcome of the retry, so a gate that returned `HTTP 502` and then `HTTP 200` is recorded as `pass` with the retry noted. A row that shows `pass` with no note of a retry means the gate passed on its first response.

## Related documents

- [`../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml`](../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml) — the authoritative table, column, role, scope and access-control records these gates verify
- [`./data-model.md`](./data-model.md) — the ten tables field by field, and the source of the seven entity table names gated here
- [`./access-control.md`](./access-control.md) — the three roles, the access-control matrix including the two REST endpoint controls gated by `GATE-SEC-03`, and the closed table access posture gated by `GATE-TBL-01` through `GATE-TBL-07`, `GATE-SEC-01` and `GATE-SEC-02`
- [`./api-reference.md`](./api-reference.md) — the JSON-only request contract the application enforces independently of the instance XML entity-resolution configuration
- [`../scripts/validate_update_set_xml.py`](../scripts/validate_update_set_xml.py) — the pre-delivery well-formedness validator run on the Update Set before it is uploaded
- [`./deployment-runbook.md`](./deployment-runbook.md) — the pre-flight checks, the six-step import sequence whose final step reads this file, the two rollback branches and the failure matrix, carrying the two checks under [Pre-commit import completeness](#pre-commit-import-completeness) and the eight values and routes under [Requirements carried to the deployment runbook](#requirements-carried-to-the-deployment-runbook)
- [`./manual-build/05-atf-test-suites.md`](./manual-build/05-atf-test-suites.md) — the 21 per-role, per-field access-control tests that discharge criterion 2, and the suites covering the three supporting tables
- [`./validation-checklist.md`](./validation-checklist.md) — the five success criteria, citing the evidence record above, and covering the field-by-field half of criterion 1
- [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md) — the single source of truth for every decision behind this gate set
