# Post-commit validation gates — `x_bst_startuptrk`

These gates run **after** the Update Set at [`../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml`](../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml) has committed successfully on the target instance. They are the sixth and final step of the import sequence — upload the XML, poll for load, trigger preview, require the error-type preview-problem set to be empty, commit, then run these gates — and they are the last check performed before a deployment is accepted. That sequence is specified in full, with its polling intervals and timeouts, in [`./deployment-runbook.md`](./deployment-runbook.md).

**The acceptance contract is the eleven required gates, and only those eleven.** They are `GATE-TBL-01` through `GATE-TBL-07`, `GATE-ROLE-01` through `GATE-ROLE-03`, and `GATE-SCOPE-01` — the seven entity-table reads, the three role-record gates and the one scope-record gate that AAP section 0.11.2 and the deployment environment's definition require. A failure of any one of the eleven triggers the rollback, and the specific gate that failed is reported.

**This document additionally defines four checks that are not deployment gates, and they do not all carry the same weight** — see [Three classes of check](#three-classes-of-check-and-what-each-one-blocks). `GATE-COL-01` is **acceptance-required and non-rollback**: success criterion 1 depends on it, so a failure blocks acceptance, but the remedy is to correct the Update Set and re-import rather than to delete a scope whose tables and roles all committed. `GATE-SEC-01` through `GATE-SEC-03` are **non-normative diagnostics**: recorded on every deployment because each observes something the required eleven cannot see, and blocking neither acceptance nor triggering rollback. A non-normative diagnostic **must not** be cited as an entry condition by any other document in this package, and no manual-build guide may make one a precondition of its own work.

| Class | Members | Blocks acceptance? | Triggers rollback? |
| --- | --- | --- | --- |
| **1 — required deployment gate** | `GATE-TBL-01` to `-07`, `GATE-ROLE-01` to `-03`, `GATE-SCOPE-01` — **eleven** | **Yes** | **Yes** |
| **2 — acceptance-required, non-rollback** | `GATE-COL-01` — **one** | **Yes** | No |
| **3 — non-normative diagnostic** | `GATE-SEC-01`, `GATE-SEC-02`, `GATE-SEC-03` — **three** | No | No |

The rollback decision is therefore *eleven of eleven*. Nothing in this package may restate that number as anything else.

One further condition is recorded and is **not a check of this delivery at all**: the instance's XML entity-resolution configuration, under [Instance prerequisite for XML entity resolution](#instance-prerequisite-for-xml-entity-resolution). There is no `GATE-SEC-04` in this gate set.

Two checks stated in this document run earlier, between the preview-problem step and the commit: [Pre-commit import completeness](#pre-commit-import-completeness) establishes that the commit has something to apply, without which every gate below fails against an instance where nothing was installed.

The post-commit step reads its gates from this exact relative path, `<deliverable-root>/docs/validation-gates.md`; this file must not be renamed, relocated or given a suffix.

**Authority.** The frozen prompt and the Agent Action Plan govern. They are authoritative for all application content, for the acceptance contract, and for the required gate set and its count. The table names, role names and scope name asserted below are taken from the Update Set XML once those records have been verified against that specification; the same identifiers are documented in [`./data-model.md`](./data-model.md) and [`./access-control.md`](./access-control.md), and the names used here match those two documents character for character. Where this document and the Update Set records disagree, the records are checked against the prompt and the plan first. Where the records match the specification, this document is corrected to them. **Where the records depart from it, the records are corrected** — a delivered artifact never governs over the specification, and a departure remains a defect until the artifact is aligned.

This document carries assertions and their pass and fail conditions only. Every decision behind this gate set is recorded in [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md), which is the single source of truth for "why".

## Referenced documents

**This document is executable on its own.** The eleven required gates, `GATE-COL-01`, the three non-normative diagnostics, the one external instance prerequisite and the two pre-commit checks, the request shape, every target, query, expected result and pass condition, the transient-error retry rule, the failure handling and the evidence record are stated here in full. An operator needs no other file to run them and record the outcome.

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
| **On failure** | The action taken when the pass condition does not hold. Every **On failure** cell below is read subject to the [Transient-error retry rule](#transient-error-retry-rule): where a cell says any status other than `200` initiates the rollback, an `HTTP 500` initiates it only after the single 30-second retry has also failed. |

## Common request shape

Every gate is a single read against the platform Table API, issued with the deployment administrator credentials. The request is shown here once in full; each gate below supplies only its **Target** and its **Query**.

```text
GET {SERVICENOW_INSTANCE_URL}/api/now/table/{Target}?{Query}
Authorization: Basic base64({SERVICENOW_USERNAME}:{SERVICENOW_PASSWORD})
Accept: application/json
```

`{SERVICENOW_INSTANCE_URL}`, `{SERVICENOW_USERNAME}` and `{SERVICENOW_PASSWORD}` are the three environment values the deployment sequence is to use, and are read from the environment rather than written anywhere. No credential value appears in this document, in any gate, or in any evidence record.

**Gates 1 to 7 target the seven entity tables directly**, as AAP section 0.11.2 and the deployment environment require: `GET /api/now/table/x_bst_startuptrk_startup?sysparm_limit=1` and its six siblings. The remaining required gates target `sys_user_role` and `sys_scope`; the additive hardening checks target `sys_db_object`, `sys_dictionary` and `sys_security_acl`.

Reaching an application table over the Table API requires three dictionary settings on that table, and the seven entity tables are delivered with all three: `access` `public`, `read_access` `true` and `ws_access` `true`. **What is deliberately not delivered is any write capability on that route** — `create_access`, `update_access`, `delete_access`, `alter_access`, `configuration_access`, `actions_access`, `client_scripts_access` and `create_access_controls` are all `false` on all ten tables, so the Table API is a read-only surface. The three supporting tables — `x_bst_startuptrk_m2m_round_investor`, `x_bst_startuptrk_ingest_staging` and `x_bst_startuptrk_rate_limit_counter` — keep `access` `package_private` and `ws_access` `false` and are reachable over no external route at all.

**The read is access-controlled, which is what makes it safe to expose.** The Table API evaluates the same access controls as every other read path, so the seven table-level read controls still admit only the three scoped roles and the seven field-level read controls still omit every premium field from a caller holding only `x_bst_startuptrk.user`. A gate read succeeds because the deployment administrator holds `admin`; it does not create an unguarded route for anyone else. The two residual differences from the Scripted REST API — the Table API is outside the application's own fixed-window rate limiter, and outside the two REST endpoint execution controls — are recorded with their compensating controls in [`./gaps-and-flags.md`](./gaps-and-flags.md), and the decision itself in [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md).

Worked example. `GATE-TBL-01` has target `x_bst_startuptrk_startup` and query `sysparm_limit=1&sysparm_fields=sys_id`, so its full request is:

```text
GET {SERVICENOW_INSTANCE_URL}/api/now/table/x_bst_startuptrk_startup?sysparm_limit=1&sysparm_fields=sys_id
Authorization: Basic base64({SERVICENOW_USERNAME}:{SERVICENOW_PASSWORD})
Accept: application/json
```

Five response forms are referenced by the pass conditions below.

| Response | Meaning |
| --- | --- |
| `HTTP 200` with a body carrying a `result` array | The read succeeded. The array holds the matching records, of which there may be zero. |
| `HTTP 200` with an **empty** `result` array | For `GATE-TBL-01` through `GATE-TBL-07` this is a **pass**: the table exists and is readable, and it holds no rows because a freshly committed application carries no data. **For every other gate and check in this document an empty array is a failure**, because each of those asserts that a named record exists. Each gate's **Pass condition** states which reading applies to it, and no gate is read against the general rule where its own cell is explicit. |
| `HTTP 400` with body `{"error":{"message":"Invalid table <target>","detail":null},"status":"failure"}` | The named target table does not exist on the instance. For `GATE-TBL-01` through `GATE-TBL-07` this is the status the instance returns when the table did not commit, and it is a **failure**. |
| `HTTP 401` or `HTTP 403` | The credentials are invalid, or the account lacks the role the target requires — `admin` for the metadata tables, and one of the three scoped roles for an entity table. A `403` on `GATE-TBL-01` through `GATE-TBL-07` means the table committed but is not readable over this route: report it as a gate failure rather than a credential problem, and check the table's `ws_access`, `access` and `read_access` values and its read access control. |
| `HTTP 500` | The instance returned a server error. This form is transient and is subject to the retry rule below. |

### Transient-error retry rule

This rule applies to every required gate, to every additive hardening check, and to the two checks under [Pre-commit import completeness](#pre-commit-import-completeness), and is stated here in full. The failure matrix in [`./deployment-runbook.md`](./deployment-runbook.md) carries the same rule, and the per-operation retry policy stated there governs the non-idempotent steps of the import sequence rather than these reads.

- A gate that returns `HTTP 500` is **retried exactly once**, after waiting **30 seconds**. The retry reissues the identical request.
- The gate is then evaluated on the retry's response. A retry returning `HTTP 200` that satisfies the pass condition is a **pass**. A retry returning `HTTP 500` again, or any other status that does not satisfy the pass condition, is a **fail**.
- A gate is retried **at most once**. A second `HTTP 500` is final.
- No status other than `HTTP 500` is retried. `HTTP 400`, `HTTP 401` and `HTTP 403` are evaluated on their first response and fail immediately.
- No gate is compared against a previous deployment.

Apart from this rule, each gate is evaluated on one response.

## Pre-commit import completeness

Two checks run **before** the commit, immediately after the preview has completed and the error-type preview-problem set has been confirmed empty. They are **not** gates — neither a required gate nor an additive hardening check — and are not counted in the [Gate roll-up](#gate-roll-up); they are preconditions of it. [`./deployment-runbook.md`](./deployment-runbook.md) carries both, in its import sequence, between the preview-problem step and the commit step.

Every gate below tests state that the commit creates. An Update Set whose customer updates did not attach to its header commits without applying any record: the platform reports success, the scope is never created, and every gate then fails and initiates a rollback of an application that was never installed. The retrieved update set's `state` does not distinguish that outcome from a complete import — it reaches `previewed` and then `committed` either way — and neither does the preview-problem step, which returns an empty error-type and warning-type set for an import that will apply nothing. There is no error field to consult either: `sys_remote_update_set` carries 28 columns and none of them is `error_detail`. The two checks below are what distinguish the two outcomes, and they are read before anything is committed.

`{ruset_sys_id}` is the `sys_id` of the retrieved update set record, captured when the XML was uploaded. `{record_count}` is the number of `<sys_update_xml>` elements in the uploaded file — **305** for the Update Set delivered with this package. [`../scripts/validate_update_set_xml.py`](../scripts/validate_update_set_xml.py) reports that count as it validates the file, and it is the same number on every deployment of a given file.

Neither request fits [Common request shape](#common-request-shape), so both are given in full below: `PRE-COMMIT-01` reads the Aggregate API rather than the Table API, and `PRE-COMMIT-02` reads one Table API record by `sys_id` rather than a query. Both carry the same `Authorization` and `Accept` headers as every gate, and no credential value appears in either.

| Check ID | Assertion | Request | Expected result | Pass condition | On failure |
| --- | --- | --- | --- | --- | --- |
| `PRE-COMMIT-01` | Every customer update in the uploaded file attached to the retrieved update set header. | `GET {SERVICENOW_INSTANCE_URL}/api/now/stats/sys_update_xml?sysparm_query=remote_update_set={ruset_sys_id}&sysparm_count=true` | `HTTP 200` with body `{"result":{"stats":{"count":"305"}}}`. | Status is exactly `200` and `result.stats.count` equals `{record_count}`, that is `305`. | **Do not commit.** A count of `0` means no customer update carried the header `sys_id`, so every record loaded orphaned. A count between `1` and `{record_count}` minus one means only some of them carried it. Either outcome, or any status other than `200`. Report `PRE-COMMIT-01` with the count observed, then clear the failed import by [Removing a failed retrieved update set](#removing-a-failed-retrieved-update-set), correct the Update Set XML, and restart the import sequence from its first step. |
| `PRE-COMMIT-02` | The completed preview found that many records to apply. | `GET {SERVICENOW_INSTANCE_URL}/api/now/table/sys_remote_update_set/{ruset_sys_id}?sysparm_fields=state,summary,inserted,updated,deleted,collisions` | `HTTP 200` with `state` `previewed` and `summary` `305`. | Status is exactly `200`, `state` is exactly `previewed`, and `summary` equals `{record_count}`, that is `305`. | **Do not commit.** A `summary` of `0` means the preview found nothing to apply and the commit would install nothing. A `summary` below `{record_count}` means it found only part of the file. A `state` other than `previewed` means the preview has not completed and the check was read too early. Report `PRE-COMMIT-02` with all six field values observed; treat a `summary` shortfall as `PRE-COMMIT-01` is treated, and re-read a `state` shortfall once the preview completes. |

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

The forms below were established against the target instance and are stated here so that [`./deployment-runbook.md`](./deployment-runbook.md) is specified against them. This document does not restate that runbook's steps; each row names one value or route the runbook is required to use, and the form that must not be used in its place.

| # | Requirement on the runbook | Required form | Form that must not be used |
| --- | --- | --- | --- |
| 1 | The pre-flight check that the instance is not mid-upgrade must match an actual field. | `GET /api/now/table/sys_upgrade_history?sysparm_limit=1&sysparm_query=upgrade_finishedISEMPTY`, and zero records means the instance is idle. | `sysparm_query=state=executing`. `sys_upgrade_history` carries no `state` field, so the condition is dropped and the request returns the instance's entire upgrade history — which the check reads as an upgrade in progress and aborts every deployment. |
| 2 | The Update Set XML must be uploaded through the platform's import route. | The XML import route: establish a session with a form login at `POST /login.do`, read `sysparm_ck` from `GET /upload.do?sysparm_referring_url=sys_remote_update_set_list.do&sysparm_target=sys_remote_update_set`, then post the file as `multipart/form-data` to `POST /sys_upload.do`. | `POST /api/now/table/sys_remote_update_set` with `Content-Type: application/xml`. The Table API does not accept an update-set payload and returns `HTTP 400`. |
| 3 | The multipart upload must order its parts with the file last. | `sysparm_ck`, `sysparm_upload_prefix`, `sysparm_referring_url` and `sysparm_target` first, then `attachFile` as the final part. | Any order placing `attachFile` before the other parts. The request then returns `HTTP 200` while importing nothing, so the sequence proceeds against an update set that does not exist. |
| 4 | The retrieved update set must be identified by the `sys_id` of the record the upload created, under a name unique to the run. | Upload under a run-unique `<name>`, then resolve that exact name to one `sys_id` and require exactly one match. | Selecting the most recently created `sys_remote_update_set` record, or resolving a fixed name that a retry or a parallel clone can also have created. Either form can select another run's record and then preview and commit it. |
| 5 | The preview must be triggered through the platform's preview processor, and its response asserted before anything is polled. | `POST /xmlhttp.do` with `sysparm_processor=UpdateSetPreviewAjax`, `sysparm_scope=global`, `sysparm_ajax_processor_function=preview`, `sysparm_ajax_processor_sys_id={ruset_sys_id}` and `sysparm_ck`. Require `HTTP 200`, parse the response, and require the `answer` value to be a 32-character hexadecimal execution-tracker `sys_id` before polling begins. | `PATCH /api/now/table/sys_remote_update_set/{ruset_sys_id}` with body `{"state":"previewing"}`. That request returns `HTTP 200` and is ignored, so the sequence polls a preview that was never started. Equally, polling without having established the tracker identifier, which polls nothing. |
| 6 | Progress must be polled on fields that reveal content, not only on status. | Poll `state` together with `summary`, `inserted`, `updated`, `deleted` and `collisions`, and require `summary` to equal the file's `<sys_update_xml>` count before the commit is issued. | Polling `state` alone. It reaches its success values for an update set that will apply nothing, so an empty import is indistinguishable from a complete one. |
| 7 | Load and preview failures must be reported from fields that exist. | Report `state` — `error` is its failure value — together with the `message` of the execution tracker the preview returns, and the preview-problem records. | `sysparm_fields=state,error_detail`, and reporting `error_detail` on failure. `sys_remote_update_set` has no `error_detail` column, so the platform drops it from the response: a request for `state,error_detail` returns `state` only, and a runbook that logs `error_detail` logs nothing on every failure it handles. |
| 8 | The pre-flight release check must read a property that exists. | `GET /api/now/table/sys_properties?sysparm_query=name=glide.war&sysparm_fields=value`, whose value names the release and patch level. | `glide.buildname` or `glide.buildtag`. Neither property exists on the instance, so the query returns an empty `result` array and the release cannot be established from it. |
| 9 | The upload must be confirmed from the retrieved update set, not from an attachment. | Confirm the upload by reading the `sys_remote_update_set` records that carry the header name and resolving the one identifier the upload added, then read that record's `state`. | Looking for a `sys_attachment` record for the uploaded file. The XML import consumes the upload and retains no attachment row against `sys_remote_update_set`, so a step that waits for one waits indefinitely. |

## Gates 1 to 7 — entity table reads (required)

Seven required gates, one per entity table, in the order the tables are declared in [`./data-model.md`](./data-model.md). Each gate establishes that its table committed **and is readable**, by issuing the read AAP section 0.11.2 specifies: a single authenticated `sysparm_limit=1` request against the table itself.

Every gate uses the same query, `sysparm_limit=1&sysparm_fields=sys_id`. `sysparm_limit=1` bounds the read to one row so the gate is cheap on a populated instance, and `sysparm_fields=sys_id` keeps application data out of the response body and therefore out of the evidence record — the gate asserts readability, and reading a row's contents is no part of it.

**An empty `result` array is a pass for these seven gates**, and for these seven only. A freshly committed application holds no rows, so `{"result":[]}` with status `200` is the expected response on a clean install and is the proof the gate seeks: the table resolved, the caller was authorised, and the platform executed the query. What the gate rejects is a status other than `200`.

| Gate ID | Assertion | Target | Query | Expected result | Pass condition | On failure |
| --- | --- | --- | --- | --- | --- | --- |
| `GATE-TBL-01` | The `x_bst_startuptrk_startup` table committed and is readable over the Table API. | `x_bst_startuptrk_startup` | `sysparm_limit=1&sysparm_fields=sys_id` | `HTTP 200` with a body carrying a `result` array, holding either zero rows on a clean install or one row where the Startup table already holds data. | Status is exactly `200` and the body carries a `result` array. The number of rows in that array is recorded as evidence and is **not** asserted. | `HTTP 400` with `Invalid table x_bst_startuptrk_startup`: the table did not commit. `HTTP 403`: the table committed but is not readable over this route — check its `ws_access`, `access` and `read_access` values and its read access control. `HTTP 401`: the credentials are invalid. Any status other than `200`. Report `GATE-TBL-01` with the status and body observed; initiate the rollback. |
| `GATE-TBL-02` | The `x_bst_startuptrk_founder` table committed and is readable over the Table API. | `x_bst_startuptrk_founder` | `sysparm_limit=1&sysparm_fields=sys_id` | `HTTP 200` with a body carrying a `result` array, holding either zero rows on a clean install or one row where the Founder table already holds data. | Status is exactly `200` and the body carries a `result` array. The number of rows in that array is recorded as evidence and is **not** asserted. | `HTTP 400` with `Invalid table x_bst_startuptrk_founder`: the table did not commit. `HTTP 403`: the table committed but is not readable over this route — check its `ws_access`, `access` and `read_access` values and its read access control. `HTTP 401`: the credentials are invalid. Any status other than `200`. Report `GATE-TBL-02` with the status and body observed; initiate the rollback. |
| `GATE-TBL-03` | The `x_bst_startuptrk_executive` table committed and is readable over the Table API. | `x_bst_startuptrk_executive` | `sysparm_limit=1&sysparm_fields=sys_id` | `HTTP 200` with a body carrying a `result` array, holding either zero rows on a clean install or one row where the Executive table already holds data. | Status is exactly `200` and the body carries a `result` array. The number of rows in that array is recorded as evidence and is **not** asserted. | `HTTP 400` with `Invalid table x_bst_startuptrk_executive`: the table did not commit. `HTTP 403`: the table committed but is not readable over this route — check its `ws_access`, `access` and `read_access` values and its read access control. `HTTP 401`: the credentials are invalid. Any status other than `200`. Report `GATE-TBL-03` with the status and body observed; initiate the rollback. |
| `GATE-TBL-04` | The `x_bst_startuptrk_investor` table committed and is readable over the Table API. | `x_bst_startuptrk_investor` | `sysparm_limit=1&sysparm_fields=sys_id` | `HTTP 200` with a body carrying a `result` array, holding either zero rows on a clean install or one row where the Investor table already holds data. | Status is exactly `200` and the body carries a `result` array. The number of rows in that array is recorded as evidence and is **not** asserted. | `HTTP 400` with `Invalid table x_bst_startuptrk_investor`: the table did not commit. `HTTP 403`: the table committed but is not readable over this route — check its `ws_access`, `access` and `read_access` values and its read access control. `HTTP 401`: the credentials are invalid. Any status other than `200`. Report `GATE-TBL-04` with the status and body observed; initiate the rollback. |
| `GATE-TBL-05` | The `x_bst_startuptrk_fundinground` table committed and is readable over the Table API. | `x_bst_startuptrk_fundinground` | `sysparm_limit=1&sysparm_fields=sys_id` | `HTTP 200` with a body carrying a `result` array, holding either zero rows on a clean install or one row where the Funding round table already holds data. | Status is exactly `200` and the body carries a `result` array. The number of rows in that array is recorded as evidence and is **not** asserted. | `HTTP 400` with `Invalid table x_bst_startuptrk_fundinground`: the table did not commit. `HTTP 403`: the table committed but is not readable over this route — check its `ws_access`, `access` and `read_access` values and its read access control. `HTTP 401`: the credentials are invalid. Any status other than `200`. Report `GATE-TBL-05` with the status and body observed; initiate the rollback. |
| `GATE-TBL-06` | The `x_bst_startuptrk_jobposting` table committed and is readable over the Table API. | `x_bst_startuptrk_jobposting` | `sysparm_limit=1&sysparm_fields=sys_id` | `HTTP 200` with a body carrying a `result` array, holding either zero rows on a clean install or one row where the Job posting table already holds data. | Status is exactly `200` and the body carries a `result` array. The number of rows in that array is recorded as evidence and is **not** asserted. | `HTTP 400` with `Invalid table x_bst_startuptrk_jobposting`: the table did not commit. `HTTP 403`: the table committed but is not readable over this route — check its `ws_access`, `access` and `read_access` values and its read access control. `HTTP 401`: the credentials are invalid. Any status other than `200`. Report `GATE-TBL-06` with the status and body observed; initiate the rollback. |
| `GATE-TBL-07` | The `x_bst_startuptrk_newsarticle` table committed and is readable over the Table API. | `x_bst_startuptrk_newsarticle` | `sysparm_limit=1&sysparm_fields=sys_id` | `HTTP 200` with a body carrying a `result` array, holding either zero rows on a clean install or one row where the News article table already holds data. | Status is exactly `200` and the body carries a `result` array. The number of rows in that array is recorded as evidence and is **not** asserted. | `HTTP 400` with `Invalid table x_bst_startuptrk_newsarticle`: the table did not commit. `HTTP 403`: the table committed but is not readable over this route — check its `ws_access`, `access` and `read_access` values and its read access control. `HTTP 401`: the credentials are invalid. Any status other than `200`. Report `GATE-TBL-07` with the status and body observed; initiate the rollback. |

These seven gates are the machine-checkable half of prompt section 10.0 criterion 1 — they establish that each of the seven entity tables exists and is readable. `GATE-COL-01` below strengthens the existence check into a column count, as an additive hardening check rather than as part of the acceptance contract. The field-by-field half, which walks all 53 columns against the instance dictionary, is covered by [`./validation-checklist.md`](./validation-checklist.md). The per-table column split, for that walk, is Startup 12, Founder 6, Executive 6, Investor 6, Funding round 8, Job posting 9, News article 6; 12 + 6 + 6 + 6 + 8 + 9 + 6 = 53.

## Gates 8 to 10 — role records (required)

Three gates, one per role the application declares. Every role name is written fully qualified with the dot separator, exactly as [`./access-control.md`](./access-control.md) records it. No bare, abbreviated or underscore form of a role name is valid in these gates.

Each gate targets `sys_user_role` and matches its role by exact name. The pass condition is a record count: the request returns `HTTP 200` whether or not the role exists, so the count is what each gate tests.

| Gate ID | Assertion | Target | Query | Expected result | Pass condition | On failure |
| --- | --- | --- | --- | --- | --- | --- |
| `GATE-ROLE-01` | Exactly one `sys_user_role` record named `x_bst_startuptrk.admin` exists. | `sys_user_role` | `sysparm_query=name=x_bst_startuptrk.admin` | `HTTP 200` with a `result` array holding exactly 1 record whose `name` is `x_bst_startuptrk.admin`. | Status is exactly `200` and `result` holds exactly 1 record. | 0 records: the role did not commit. More than 1 record: duplicate role records. Either outcome, or any status other than `200`. Report `GATE-ROLE-01`; initiate rollback. |
| `GATE-ROLE-02` | Exactly one `sys_user_role` record named `x_bst_startuptrk.user` exists. | `sys_user_role` | `sysparm_query=name=x_bst_startuptrk.user` | `HTTP 200` with a `result` array holding exactly 1 record whose `name` is `x_bst_startuptrk.user`. | Status is exactly `200` and `result` holds exactly 1 record. | 0 records: the role did not commit. More than 1 record: duplicate role records. Either outcome, or any status other than `200`. Report `GATE-ROLE-02`; initiate rollback. |
| `GATE-ROLE-03` | Exactly one `sys_user_role` record named `x_bst_startuptrk.premium_user` exists. | `sys_user_role` | `sysparm_query=name=x_bst_startuptrk.premium_user` | `HTTP 200` with a `result` array holding exactly 1 record whose `name` is `x_bst_startuptrk.premium_user`. | Status is exactly `200` and `result` holds exactly 1 record. | 0 records: the role did not commit. More than 1 record: duplicate role records. Either outcome, or any status other than `200`. Report `GATE-ROLE-03`; initiate rollback. |

An empty `result` array is a **failure** for these three gates and for `GATE-SCOPE-01`.

## Gate 11 — the scope record (required)

One gate, targeting `sys_scope` and matching the application scope by exact name.

| Gate ID | Assertion | Target | Query | Expected result | Pass condition | On failure |
| --- | --- | --- | --- | --- | --- | --- |
| `GATE-SCOPE-01` | Exactly one `sys_scope` record whose `scope` is `x_bst_startuptrk` exists. | `sys_scope` | `sysparm_query=scope=x_bst_startuptrk` | `HTTP 200` with a `result` array holding exactly 1 record whose `scope` is `x_bst_startuptrk`. | Status is exactly `200` and `result` holds exactly 1 record. | 0 records: the scoped application did not commit. More than 1 record: duplicate scope records. Either outcome, or any status other than `200`. Report `GATE-SCOPE-01`; initiate rollback. |

The rollback acts on this same `sys_scope` record, and this gate is where its identifier is captured: **record the `sys_id` this gate returns in the deployment log**, because the rollback deletes that exact identifier and nothing else. The rollback is permitted only on a proven clean install, only when this gate returned exactly one record, and only against the `sys_id` recorded here; a count of zero or above one blocks it. The full procedure, with every assertion and every prohibition, is specified in [`./deployment-runbook.md`](./deployment-runbook.md).

## Three classes of check, and what each one blocks

A check in this document belongs to exactly one of three classes. **The distinction is between what triggers the irreversible rollback and what blocks acceptance — those are not the same thing**, and conflating them is what would let a check that acceptance genuinely depends on be recorded as merely advisory.

| Class | Members | Blocks acceptance? | Triggers rollback? | Why |
| --- | --- | --- | --- | --- |
| **1 — required deployment gate** | `GATE-TBL-01` to `-07`, `GATE-ROLE-01` to `-03`, `GATE-SCOPE-01` — **11** | **Yes** | **Yes** | These are the acceptance set AAP section 0.11.2 and the deployment environment define. A failure means the commit did not produce the application, so the scope is deleted and the deployment retried. |
| **2 — acceptance-required, non-rollback** | `GATE-COL-01` — **1** | **Yes** | **No** | Success criterion 1 requires all 53 binding columns, and this check is how their **count** is machine-verified. A failure means the delivered schema is wrong, which acceptance cannot pass over — but the remedy is to correct the Update Set and re-import, not to delete a scope whose tables and roles all committed correctly. |
| **3 — non-normative diagnostic** | `GATE-SEC-01`, `GATE-SEC-02`, `GATE-SEC-03` — **3** | No | No | Each observes something the required eleven cannot see and is recorded on every deployment, but the posture it reports is not part of any success criterion's pass condition. A failure is reported, investigated and carried with the deployment record. |

**Class 2 exists because of a real asymmetry, not as a hedge.** Criterion 1 in [`./validation-checklist.md`](./validation-checklist.md) asks that all seven tables exist **with 100 % of their fields**, and it evidences the field list two ways: a manual field-by-field walk of all 53 columns, and this automated count. Classing the count as merely advisory would leave the only machine-checkable evidence of the binding field list carrying no weight — so a deployment that committed 45 columns would clear every check that mattered and be recorded as accepted. Classing it as a rollback trigger would be equally wrong: deleting the scope discards seven correctly committed tables and three correctly committed roles to fix a dictionary defect that lives in the Update Set.

So `GATE-COL-01` **blocks acceptance and does not trigger rollback**, and both halves of that are stated wherever it appears.

**No class 3 diagnostic decides anything.** Read the three of them, record their outcomes, and act on a failure as its own **On failure** cell directs — which in no case is the rollback. No document in this package may cite a class 3 diagnostic as a precondition of any work, and no operator may hold a deployment on one.

### Acceptance-required check 1 — entity column count

One check establishing that the 53 binding columns of prompt section 1.0 committed, by counting the entity tables' `sys_dictionary` column records. `sys_dictionary` carries one record per column plus one collection record per table, so the seven entity tables contribute 53 column records and 7 collection records; the query below excludes the collection records by requiring a non-empty `element`.

| Gate ID | Assertion | Target | Query | Expected result | Pass condition | On failure |
| --- | --- | --- | --- | --- | --- | --- |
| `GATE-COL-01` | The seven entity tables carry exactly 53 columns between them. | `sys_dictionary` | `sysparm_query=nameINx_bst_startuptrk_startup,x_bst_startuptrk_founder,x_bst_startuptrk_executive,x_bst_startuptrk_investor,x_bst_startuptrk_fundinground,x_bst_startuptrk_jobposting,x_bst_startuptrk_newsarticle^elementISNOTEMPTY&sysparm_fields=name,element&sysparm_limit=200` | `HTTP 200` with a `result` array holding exactly 53 records. | Status is exactly `200` and `result` holds exactly 53 records. | Fewer than 53: one or more columns did not commit. More than 53: an unexpected column exists, which breaches the binding-and-complete field list. Either outcome, or any status other than `200`. Report `GATE-COL-01` with the count observed and the per-table split. **Acceptance is blocked**: correct the Update Set and re-import. **No rollback** — a count below 53 with all eleven required gates passing means the tables committed but at least one column did not, and deleting the scope would discard working artifacts to fix a dictionary defect that lives in the source file. |

An encoded query is written `[field][operator][value]` with **no separator between the operator and its first operand**, which is why `nameIN` runs straight into `x_bst_startuptrk_startup` above and why `elementISNOTEMPTY` carries no operand at all. A space after `IN` is not ignored: it becomes the first character of the first operand, so the first table would be looked up under a leading space, would match nothing, and the check would report 45 columns instead of 53 and raise a false alarm on a deployment that had in fact succeeded. The seven operands are separated by bare commas with no spaces, and each is spelled exactly as `sys_db_object.name` spells it — the same seven names `GATE-TBL-01` through `GATE-TBL-07` read. Confirm all seven statically against [`./data-model.md`](./data-model.md) before the deployment runs; the HTTP client URL-encodes the query, so the commas and the `^` need no manual escaping.

The per-table split, for diagnosing a count that is off: Startup 12, Founder 6, Executive 6, Investor 6, Funding round 8, Job posting 9, News article 6. 12 + 6 + 6 + 6 + 8 + 9 + 6 = 53. The three supporting tables are excluded from this check; their columns are documented in [`./data-model.md`](./data-model.md).

### Non-normative diagnostics 1 to 3 — the access posture

Three checks recording that the access posture the application depends on actually committed. The posture is **not uniform across the ten tables**, and these checks assert the split as delivered: the seven entity tables are readable over the Table API under their access controls, the three supporting tables are reachable over no external route, and no table permits any write, configuration or schema operation from outside the scope. All three are class 3: recorded on every deployment, and neither acceptance-blocking nor rollback-triggering.

**No check in this document touches anything outside the `x_bst_startuptrk` scope, and none instructs an operator to change instance configuration.** Prompt section 6.0 forbids the scoped application from modifying anything outside its scope, and that prohibition binds this document's remedies as much as it binds the Update Set: a check whose remedy is a Global-scope property change would breach it. Instance-level hardening, where an operator wants it, is a separate authorised activity with its own review and is not part of this deployment — which is why the XML entity-resolution configuration is recorded below as an observation rather than as a check.

| Check ID | Assertion | Target | Query | Expected result | Pass condition | On failure |
| --- | --- | --- | --- | --- | --- | --- |
| `GATE-SEC-01` | The three supporting tables are reachable from the `x_bst_startuptrk` scope only. | `sys_db_object` | `sysparm_query=nameSTARTSWITHx_bst_startuptrk_^access=package_private&sysparm_fields=name,access&sysparm_limit=50` | `HTTP 200` with a `result` array holding exactly 3 records: `x_bst_startuptrk_m2m_round_investor`, `x_bst_startuptrk_ingest_staging` and `x_bst_startuptrk_rate_limit_counter`. | Status is exactly `200`, `result` holds exactly 3 records, and their names are those three. | More than 3, or a different set of names: a table that should be open is closed, or one that should be closed is open — compare against [`./data-model.md`](./data-model.md). Fewer than 3: a supporting table is `public`, so an out-of-scope script can reach its rows. The staging table is the one that matters most here, because it holds verbatim upstream payloads. Report `GATE-SEC-01` with the names observed and investigate. **No rollback**, and acceptance is not blocked. |
| `GATE-SEC-02` | No application table permits any cross-scope write, configuration or schema operation. | `sys_db_object` | `sysparm_query=nameSTARTSWITHx_bst_startuptrk_^create_access=false^update_access=false^delete_access=false^alter_access=false^configuration_access=false&sysparm_fields=name,create_access,update_access,delete_access,alter_access,configuration_access&sysparm_limit=50` | `HTTP 200` with a `result` array holding exactly 10 records. | Status is exactly `200` and `result` holds exactly 10 records. | Fewer than 10: at least one table accepts writes or schema changes from outside the scope, which would let an out-of-scope caller alter application data through a route the application's own controls never see. **This is the posture check that matters.** Report `GATE-SEC-02` with the names of the tables missing from the result and treat it as a blocking defect in the delivered artifact: correct the dictionary records, re-export and re-import. Do not put the application into use with this check failing. **No rollback** — the defect lives in the Update Set. |
| `GATE-SEC-03` | Both REST endpoint access controls committed. | `sys_security_acl` | `sysparm_query=type=REST_Endpoint^nameSTARTSWITHBoston Startup Tracker API&sysparm_fields=name,type,operation` | `HTTP 200` with a `result` array holding exactly 2 records, `Boston Startup Tracker API read` and `Boston Startup Tracker API write`, both with `operation` `execute`. | Status is exactly `200`, `result` holds exactly 2 records, and both carry `operation` `execute`. | Fewer than 2: endpoint authorisation on the Scripted REST API falls back to the platform's broad default REST access control, which admits any authenticated internal user. Report `GATE-SEC-03` and correct it before the API is exposed. **No rollback.** |

**Why `GATE-SEC-01` expects three rather than ten.** The seven entity tables are delivered `access` `public` with `read_access` `true` and `ws_access` `true`, because AAP section 0.11.2 requires the eleven required gates to read each entity table directly and the Table API cannot reach a `package_private` table. What that opens is a **read** route, evaluated under the same seven table-level and seven field-level read access controls as every other read path, so a caller holding only `x_bst_startuptrk.user` still cannot see a premium field over it. What it does not open is any write route, which is what `GATE-SEC-02` asserts across all ten tables. The two residual differences from the Scripted REST API — no application-level rate limiting and no endpoint execution control on this route — are recorded with their compensating controls in [`./gaps-and-flags.md`](./gaps-and-flags.md), and the decision in [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md).

## Instance prerequisite for XML entity resolution

**This is not a gate.** It is a read-only observation of instance configuration that the application relies on and deliberately does **not** ship: the properties live in the Global scope, and prompt section 6.0 forbids the scoped application from modifying anything outside `x_bst_startuptrk`. It is recorded here so the deploying operator knows the condition exists and who owns it, and it is stated as a prerequisite rather than an acceptance criterion because **nothing in this delivery can set it, test it into compliance, or be rolled back to fix it.**

| Observation | Target | Query | Reading |
| --- | --- | --- | --- |
| Whether the instance refuses XML entity resolution. | `sys_properties` | `sysparm_query=nameINglide.stax.allow_entity_resolution,glide.stax.whitelist_enabled&sysparm_fields=name,value` | The hardened configuration is `glide.stax.allow_entity_resolution` `false` and `glide.stax.whitelist_enabled` `true`. Record both values, or their absence, in the deployment log. |

**What to do with the reading.** Record it and continue. A value other than the hardened one is **not** a deployment failure, is **not** a gate failure, and **must not** trigger the rollback — the rollback deletes this application's scope, which would not change a Global property by one byte. If the reading is not the hardened configuration, report it to the platform owner responsible for instance configuration as a finding against the instance, outside this delivery. This delivery neither sets these properties nor requires the operator to set them.

**The application closes the same vector independently**, which is why this observation is defence in depth rather than a dependency: the Scripted REST API declares `application/json` for both `consumes` and `produces` on the definition and on all 31 operations, and every body-bearing operation refuses a request that does not declare `application/json` with `HTTP 415` before the body is read. The companion allowlist property `glide.xml.entity.whitelist` is not read at all, because its value is instance-specific and no correct value can be stated for it here.

## Gate roll-up

**The acceptance contract is eleven gates.** 7 entity-table reads + 3 role-record gates + 1 scope-record gate = **11 required gates**, exactly the set AAP section 0.11.2 and the deployment environment define.

1 column-count check = **1 acceptance-required, non-rollback check**, class 2.

3 access-posture checks = **3 non-normative diagnostics**, class 3.

**12 checks block acceptance; 11 of them trigger rollback.** The classes are defined under [Three classes of check](#three-classes-of-check-and-what-each-one-blocks).

The eleven required gates, in the order they are run:

| # | Gate ID | Assertion |
| --- | --- | --- |
| 1 | `GATE-TBL-01` | The `x_bst_startuptrk_startup` table committed and is readable over the Table API. |
| 2 | `GATE-TBL-02` | The `x_bst_startuptrk_founder` table committed and is readable over the Table API. |
| 3 | `GATE-TBL-03` | The `x_bst_startuptrk_executive` table committed and is readable over the Table API. |
| 4 | `GATE-TBL-04` | The `x_bst_startuptrk_investor` table committed and is readable over the Table API. |
| 5 | `GATE-TBL-05` | The `x_bst_startuptrk_fundinground` table committed and is readable over the Table API. |
| 6 | `GATE-TBL-06` | The `x_bst_startuptrk_jobposting` table committed and is readable over the Table API. |
| 7 | `GATE-TBL-07` | The `x_bst_startuptrk_newsarticle` table committed and is readable over the Table API. |
| 8 | `GATE-ROLE-01` | Exactly one `sys_user_role` record named `x_bst_startuptrk.admin` exists. |
| 9 | `GATE-ROLE-02` | Exactly one `sys_user_role` record named `x_bst_startuptrk.user` exists. |
| 10 | `GATE-ROLE-03` | Exactly one `sys_user_role` record named `x_bst_startuptrk.premium_user` exists. |
| 11 | `GATE-SCOPE-01` | Exactly one `sys_scope` record whose `scope` is `x_bst_startuptrk` exists. |

**The aggregate rollback pass condition is that all eleven required gates pass — `11 of 11`.** There is no partial pass. No required gate may be skipped, deferred or waived, and no other check may be substituted for one.

The one acceptance-required, non-rollback check:

| # | Check ID | Assertion | Blocks acceptance | Triggers rollback |
| --- | --- | --- | --- | --- |
| A1 | `GATE-COL-01` | The seven entity tables carry exactly 53 columns between them. | **Yes** | No |

The three non-normative diagnostics, recorded and never required:

| # | Check ID | Assertion |
| --- | --- | --- |
| D1 | `GATE-SEC-01` | The three supporting tables are reachable from the `x_bst_startuptrk` scope only. |
| D2 | `GATE-SEC-02` | No application table permits any cross-scope write, configuration or schema operation. |
| D3 | `GATE-SEC-03` | Both REST endpoint access controls committed. |

**The rollback pass condition** is that all eleven class 1 gates pass. There is no partial pass among them, none is advisory, and none may be skipped, deferred or waived.

**The acceptance pass condition** is that all eleven class 1 gates pass **and** `GATE-COL-01` passes — twelve checks in total. A `GATE-COL-01` failure leaves the deployment in place and blocks acceptance until the Update Set is corrected and re-imported; it never initiates the rollback. The three class 3 diagnostics are run and recorded, and their results enter neither condition.

One further condition is recorded and is **not a check of this delivery at all**: the instance's XML entity-resolution configuration, under [Instance prerequisite for XML entity resolution](#instance-prerequisite-for-xml-entity-resolution). It is owned by the platform owner, is not settable or fixable from within this application, and is reported rather than gated. There is no `GATE-SEC-04` in this gate set.

`PRE-COMMIT-01` and `PRE-COMMIT-02` are preconditions of this gate set, not members of it, so neither count above is changed by them. They are equally not waivable: the eleven required gates are evaluated only on a deployment whose commit had records to apply.

Gates 1 to 7 and `GATE-COL-01` cover the seven entity tables only. `GATE-SEC-01` covers the three supporting tables — `x_bst_startuptrk_m2m_round_investor`, `x_bst_startuptrk_ingest_staging` and `x_bst_startuptrk_rate_limit_counter` — and `GATE-SEC-02` covers all ten; those three supporting tables are otherwise documented in [`./data-model.md`](./data-model.md).

The three supporting tables — `x_bst_startuptrk_m2m_round_investor`, `x_bst_startuptrk_ingest_staging` and `x_bst_startuptrk_rate_limit_counter` — carry no gate. They are deliberately `package_private` with `ws_access` set to `false`, so no Table API read of them can succeed and none is attempted; they are documented in [`./data-model.md`](./data-model.md) and exercised by the Automated Test Framework suites built in [`./manual-build/05-atf-test-suites.md`](./manual-build/05-atf-test-suites.md).

## Failure handling

On failure of any one of the **eleven required** gates:

1. Report the failing gate by its identifier, together with the HTTP status and the response body observed.
2. If the observed status is `HTTP 500` and the gate has not yet been retried, wait 30 seconds and reissue the identical request exactly once, per the [Transient-error retry rule](#transient-error-retry-rule). Evaluate the gate on that response and report the retry's status and body alongside the first.
3. Initiate the rollback when the pass condition still does not hold — that is, immediately for any status other than `HTTP 500`, and for `HTTP 500` only after the single retry has also failed. **The rollback is permitted only under the conditions [`./deployment-runbook.md`](./deployment-runbook.md) states**, which include a proven clean install and an exact scope identifier captured this run; where those conditions do not hold, report the failure and stop rather than delete.

The failing gate is reported before the rollback is initiated. A gate that passes on its retry is a pass, is recorded as such, and initiates no rollback.

**On failure of `GATE-COL-01`**, follow steps 1 and 2 above and then **stop without rolling back**. The deployment stays in place, and **acceptance is blocked**: record the observed column count and the per-table split, correct the Update Set so the seven entity tables carry exactly the 53 binding columns, and re-import. Do not delete the scope — the tables and roles committed correctly, and deleting them discards working artifacts to fix a dictionary defect that lives in the source file. Do not record criterion 1 as met while this check is failing.

**On failure of one of the three non-normative diagnostics**, no rollback is initiated under any circumstance. Follow steps 1 and 2 above, report the check by its identifier with the status and body observed, act on its own **On failure** cell, and record the outcome in the evidence record. `GATE-SEC-02` is the one whose failure should stop the application being put into use, and its own row says so; the remedy there is to correct the dictionary records and re-import, not to destroy the installation.

`PRE-COMMIT-01` and `PRE-COMMIT-02` are handled differently, and their own rows state it: they are read before the commit, so a failure means the commit does not happen and there is no scope to roll back. The remedy is to remove the retrieved update set by [Removing a failed retrieved update set](#removing-a-failed-retrieved-update-set), correct the Update Set XML and restart the import sequence. The [Transient-error retry rule](#transient-error-retry-rule) applies to both of them as it does to the gates.

**The rollback has two branches, and the correct one depends on whether this deployment created the scope.** When the pre-flight scope check recorded a **clean** starting state, the rollback retrieves the `sys_scope` record whose `scope` is `x_bst_startuptrk` — the same record `GATE-SCOPE-01` tests, whose `sys_id` that gate records — and deletes **that exact identifier**, then confirms the seven entity tables no longer resolve, the three roles are gone and the scope record is gone. **That branch is irreversible, and it is guarded.** When the starting state was an **existing** installation, the scope is **never** deleted: the deployment's own update set is backed out, the eleven required gates are re-run to verify the pre-existing installation survived, and the failure is escalated to the application's owner. Both branches, every precondition on them, their trigger conditions and the wider failure matrix are specified in [`./deployment-runbook.md`](./deployment-runbook.md), which is authoritative for the branch selection.

## Evidence record

The operator records one row per pre-commit check, one row per required gate, one row for the acceptance-required check and one row per non-normative diagnostic per deployment. The tables below are the evidence record for the machine-checkable gates, and [`./validation-checklist.md`](./validation-checklist.md) cites them as such.

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
| **Aggregate** | | | 12 of 12 acceptance-blocking checks required — the 11 gates above plus this one |

The three non-normative diagnostics are recorded separately again, so a reader can never mistake one of them for part of the acceptance set:

| Diagnostic check ID | Result | Timestamp (UTC) | Note |
| --- | --- | --- | --- |
| `GATE-SEC-01` | | | |
| `GATE-SEC-02` | | | |
| `GATE-SEC-03` | | | |
| **Aggregate** | | | Non-normative. Recorded, not required. A failure here does not fail the deployment and does not block acceptance. |

The instance prerequisite is recorded as an observation rather than a result:

| Observation | Value read | Timestamp (UTC) | Reported to |
| --- | --- | --- | --- |
| `glide.stax.allow_entity_resolution` | | | |
| `glide.stax.whitelist_enabled` | | | |

Every table is filled in the same way. Record `pass` or `fail` in **Result**. Record the time of the request in **Timestamp (UTC)** in `YYYY-MM-DD HH:MM:SS` form. Record the observed HTTP status and the `result` record count in **Note**, and for a failing gate or check also the response body. For `GATE-TBL-01` through `GATE-TBL-07` the row count is evidence and is not asserted, so record it in **Note** and leave **Result** governed by the status alone. For `GATE-COL-01` record the count returned **and** the per-table split, since a count that is off is diagnosed from the split. For the instance prerequisite, record each property value as read, or `absent`, and the name of the platform owner it was reported to where it is not the hardened value. Record no credential value in any field.

Where a gate was retried under the [Transient-error retry rule](#transient-error-retry-rule), record the retry in the same row: note the first `HTTP 500`, the 30-second wait and the retry's status, and set **Timestamp (UTC)** to the retried request. **Result** carries the outcome of the retry, so a gate that returned `HTTP 500` and then `HTTP 200` is recorded as `pass` with the retry noted. A row that shows `pass` with no note of a retry means the gate passed on its first response.

## Related documents

- [`../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml`](../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml) — the authoritative table, column, role, scope and access-control records these gates verify
- [`./data-model.md`](./data-model.md) — the ten tables field by field, and the source of the seven entity table names gated here
- [`./access-control.md`](./access-control.md) — the three roles, the access-control matrix including the two REST endpoint controls gated by `GATE-SEC-03`, and the table access posture gated by `GATE-SEC-01` and `GATE-SEC-02`
- [`./api-reference.md`](./api-reference.md) — the JSON-only request contract the application enforces independently of the instance XML entity-resolution configuration
- [`../scripts/validate_update_set_xml.py`](../scripts/validate_update_set_xml.py) — the pre-delivery well-formedness validator run on the Update Set before it is uploaded
- [`./deployment-runbook.md`](./deployment-runbook.md) — the pre-flight checks, the six-step import sequence whose final step reads this file, the two rollback branches and the failure matrix, carrying the two checks under [Pre-commit import completeness](#pre-commit-import-completeness) and the eight values and routes under [Requirements carried to the deployment runbook](#requirements-carried-to-the-deployment-runbook)
- [`./manual-build/05-atf-test-suites.md`](./manual-build/05-atf-test-suites.md) — the 21 per-role, per-field access-control tests that discharge criterion 2, and the suites covering the three supporting tables
- [`./validation-checklist.md`](./validation-checklist.md) — the five success criteria, citing the evidence record above, and covering the field-by-field half of criterion 1
- [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md) — the single source of truth for every decision behind this gate set
