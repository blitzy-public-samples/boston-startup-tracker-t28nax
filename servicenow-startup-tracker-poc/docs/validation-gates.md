# Post-commit validation gates — `x_bst_startuptrk`

These gates run **after** the Update Set at [`../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml`](../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml) has committed successfully on the target instance. They are the sixth and final step of the import sequence — upload the XML, poll for load, trigger preview, require the error-type preview-problem set to be empty, commit, then run these gates — and they are the last check performed before a deployment is accepted. That sequence is specified in full, with its polling intervals and timeouts, in [`./deployment-runbook.md`](./deployment-runbook.md).

**The acceptance contract is the eleven required gates, and only those eleven.** They are `GATE-TBL-01` through `GATE-TBL-07`, `GATE-ROLE-01` through `GATE-ROLE-03`, and `GATE-SCOPE-01` — the seven entity-table gates, the three role-record gates and the one scope-record gate that AAP section 0.11.2 and the deployment environment's definition require. Each of the seven entity-table gates reads that table's dictionary record rather than its rows, because all ten application tables are delivered closed to every route outside the application scope; see [Common request shape](#common-request-shape). A failure of any one of the eleven triggers the rollback, and the specific gate that failed is reported.

**The seven entity-table gates read table metadata rather than table rows**, because the seven entity tables are delivered sealed against every external route — `access` `package_private`, `read_access` `false`, `ws_access` `false` — so no Table API request reaches them at all. Each gate therefore asserts the same two facts a row read was asked to establish, and asserts them more precisely: that the table committed, and that it committed with the sealed posture the access-control design depends on. The ACL-respecting read path is exercised separately by `GATE-SEC-04`. The reasoning, the alternative and the residual risk are recorded at `D-027` in [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md).

**This document additionally defines five checks that are not deployment gates, and they do not all carry the same weight** — see [Three classes of check](#three-classes-of-check-and-what-each-one-blocks). `GATE-COL-01` is **acceptance-required and non-rollback**: success criterion 1 depends on it, so a failure blocks acceptance, but the remedy is to correct the Update Set and re-import rather than to delete a scope whose tables and roles all committed. `GATE-SEC-01` through `GATE-SEC-04` are **non-normative diagnostics**: recorded on every deployment because each observes something the required eleven cannot see, and blocking neither acceptance nor triggering rollback. A non-normative diagnostic **must not** be cited as an entry condition by any other document in this package, and no manual-build guide may make one a precondition of its own work.

| Class | Members | Blocks acceptance? | Triggers rollback? |
| --- | --- | --- | --- |
| **1 — required deployment gate** | `GATE-TBL-01` to `-07`, `GATE-ROLE-01` to `-03`, `GATE-SCOPE-01` — **eleven** | **Yes** | **Yes** |
| **2 — acceptance-required, non-rollback** | `GATE-COL-01` — **one** | **Yes** | No |
| **3 — non-normative diagnostic** | `GATE-SEC-01`, `GATE-SEC-02`, `GATE-SEC-03`, `GATE-SEC-04` — **four** | No | No |

The rollback decision is therefore *eleven of eleven*, and the acceptance decision is *twelve of twelve* — the eleven plus `GATE-COL-01`. Nothing in this package may restate either number as anything else.

One further condition is recorded and is **not a check of this delivery at all**: the instance's XML entity-resolution configuration, under [Instance prerequisite for XML entity resolution](#instance-prerequisite-for-xml-entity-resolution). There is no `GATE-SEC-05` in this gate set.

Two checks stated in this document run earlier, between the preview-problem step and the commit: [Pre-commit import completeness](#pre-commit-import-completeness) establishes that the commit has something to apply, without which every gate below fails against an instance where nothing was installed.

The post-commit step reads its gates from this exact relative path, `<deliverable-root>/docs/validation-gates.md`; this file must not be renamed, relocated or given a suffix.

**Authority.** The frozen prompt and the Agent Action Plan govern. They are authoritative for all application content, for the acceptance contract, and for the required gate set and its count. The table names, role names and scope name asserted below are taken from the Update Set XML once those records have been verified against that specification; the same identifiers are documented in [`./data-model.md`](./data-model.md) and [`./access-control.md`](./access-control.md), and the names used here match those two documents character for character. Where this document and the Update Set records disagree, the records are checked against the prompt and the plan first. Where the records match the specification, this document is corrected to them. **Where the records depart from it, the records are corrected** — a delivered artifact never governs over the specification, and a departure remains a defect until the artifact is aligned.

This document carries assertions and their pass and fail conditions only. Every decision behind this gate set is recorded in [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md), which is the single source of truth for "why".

## Referenced documents

**This document is executable on its own.** The eleven required gates, `GATE-COL-01`, the four non-normative diagnostics, the one external instance prerequisite and the two pre-commit checks, the request shape, every target, query, expected result and pass condition, the transient-error retry rule, the failure handling and the evidence record are stated here in full. An operator needs no other file to run them and record the outcome.

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

Five response forms are referenced by the pass conditions below.

| Response | Meaning |
| --- | --- |
| `HTTP 200` with a body carrying a `result` array | The read succeeded. The array holds the matching records, of which there may be zero. |
| `HTTP 200` with an **empty** `result` array | **A failure for every gate and check in this document**, because each one asserts that a named record exists. For `GATE-TBL-01` through `GATE-TBL-07` an empty array means no `sys_db_object` record carries that table name inside the `x_bst_startuptrk` scope, so the table did not commit. |
| `HTTP 400` with body `{"error":{"message":"Invalid table <target>","detail":null},"status":"failure"}` | The named target table does not exist on the instance. No gate in this document targets an application table, so on a correct deployment this form appears only if a platform table name was mistyped. It is also the expected response to a read of an application table, which is why no gate issues one — see [Common request shape](#common-request-shape). |
| `HTTP 401` or `HTTP 403` | The credentials are invalid, or the account lacks the role the target requires. Every gate in this document reads a platform table and needs `admin`, so a `401` or `403` is a credential or role problem rather than a statement about the application: correct the account and reissue before reading the response as a gate outcome. |
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

**AAP section 0.11.2 requires a successful read establishing that each entity table exists after the commit; it does not require that read to be a row read.** A row read is not available here, because all ten application tables are delivered `ws_access` `false` and are served by no external route. This expression satisfies the requirement on the route that exists and asserts strictly more than a row read could: a row read proves the table resolved, whereas this proves the table resolved, that it belongs to the application's own scope, and that its three read-access flags committed at their closed values. The deviation from a literal row read, and the containment reason for it, are recorded in [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md).

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
| **2 — acceptance-required, non-rollback** | `GATE-COL-01` — **1** | **Yes** | **No** | Success criterion 1 requires all 53 binding columns, and this check is how their **count** is machine-verified. A failure means the delivered schema is wrong, which acceptance cannot pass over — but the remedy is to correct the Update Set and re-import, not to delete a scope whose tables and roles all committed correctly. |
| **3 — non-normative diagnostic** | `GATE-SEC-01`, `GATE-SEC-02`, `GATE-SEC-03`, `GATE-SEC-04` — **4** | No | No | Each observes something the required eleven cannot see and is recorded on every deployment, but the posture it reports is not part of any success criterion's pass condition. A failure is reported, investigated and carried with the deployment record. |

**Class 2 exists because of a real asymmetry, not as a hedge.** Criterion 1 in [`./validation-checklist.md`](./validation-checklist.md) asks that all seven tables exist **with 100 % of their fields**, and it evidences the field list two ways: a manual field-by-field walk of all 53 columns, and this automated count. Classing the count as merely advisory would leave the only machine-checkable evidence of the binding field list carrying no weight — so a deployment that committed 45 columns would clear every check that mattered and be recorded as accepted. Classing it as a rollback trigger would be equally wrong: deleting the scope discards seven correctly committed tables and three correctly committed roles to fix a dictionary defect that lives in the Update Set.

So `GATE-COL-01` **blocks acceptance and does not trigger rollback**, and both halves of that are stated wherever it appears.

**No class 3 diagnostic decides anything.** Read the four of them, record their outcomes, and act on a failure as its own **On failure** cell directs — which in no case is the rollback. No document in this package may cite a class 3 diagnostic as a precondition of any work, and no operator may hold a deployment on one.

### Acceptance-required check 1 — entity column count

One check establishing that the 53 binding columns of prompt section 1.0 committed, by counting the entity tables' `sys_dictionary` column records. `sys_dictionary` carries one record per column plus one collection record per table, so the seven entity tables contribute 53 column records and 7 collection records; the query below excludes the collection records by requiring a non-empty `element`.

| Gate ID | Assertion | Target | Query | Expected result | Pass condition | On failure |
| --- | --- | --- | --- | --- | --- | --- |
| `GATE-COL-01` | The seven entity tables carry exactly 53 columns between them. | `sys_dictionary` | `sysparm_query=nameINx_bst_startuptrk_startup,x_bst_startuptrk_founder,x_bst_startuptrk_executive,x_bst_startuptrk_investor,x_bst_startuptrk_fundinground,x_bst_startuptrk_jobposting,x_bst_startuptrk_newsarticle^elementISNOTEMPTY&sysparm_fields=name,element&sysparm_limit=200` | `HTTP 200` with a `result` array holding exactly 53 records. | Status is exactly `200` and `result` holds exactly 53 records. | Fewer than 53: one or more columns did not commit. More than 53: an unexpected column exists, which breaches the binding-and-complete field list. Either outcome, or any status other than `200`. Report `GATE-COL-01` with the count observed and the per-table split. **Acceptance is blocked**: correct the Update Set and re-import. **No rollback** — a count below 53 with all eleven required gates passing means the tables committed but at least one column did not, and deleting the scope would discard working artifacts to fix a dictionary defect that lives in the source file. |

An encoded query is written `[field][operator][value]` with **no separator between the operator and its first operand**, which is why `nameIN` runs straight into `x_bst_startuptrk_startup` above and why `elementISNOTEMPTY` carries no operand at all. A space after `IN` is not ignored: it becomes the first character of the first operand, so the first table would be looked up under a leading space, would match nothing, and the check would report 45 columns instead of 53 and raise a false alarm on a deployment that had in fact succeeded. The seven operands are separated by bare commas with no spaces, and each is spelled exactly as `sys_db_object.name` spells it — the same seven names `GATE-TBL-01` through `GATE-TBL-07` read. Confirm all seven statically against [`./data-model.md`](./data-model.md) before the deployment runs; the HTTP client URL-encodes the query, so the commas and the `^` need no manual escaping.

The per-table split, for diagnosing a count that is off: Startup 12, Founder 6, Executive 6, Investor 6, Funding round 8, Job posting 9, News article 6. 12 + 6 + 6 + 6 + 8 + 9 + 6 = 53. The three supporting tables are excluded from this check; their columns are documented in [`./data-model.md`](./data-model.md).

### Non-normative diagnostics 1 to 4 — the access posture and the secured read path

Three checks recording that the access posture the application depends on actually committed. The posture is **uniform across all ten tables** — every one of them is `package_private` with `read_access` and `ws_access` `false` and every write, configuration and schema flag `false` — and these checks assert it in one read each, across the ten together, rather than table by table. All three are class 3: recorded on every deployment, and neither acceptance-blocking nor rollback-triggering.

`GATE-SEC-01` deliberately overlaps gates 1 to 7, which assert the same three flags per table. The overlap is the point: the seven gates fail one table at a time and name it, while `GATE-SEC-01` answers "are all ten closed" in a single read and is the check that would notice a supporting table drifting open, which no required gate covers.

**No check in this document touches anything outside the `x_bst_startuptrk` scope, and none instructs an operator to change instance configuration.** Prompt section 6.0 forbids the scoped application from modifying anything outside its scope, and that prohibition binds this document's remedies as much as it binds the Update Set: a check whose remedy is a Global-scope property change would breach it. Instance-level hardening, where an operator wants it, is a separate authorised activity with its own review and is not part of this deployment — which is why the XML entity-resolution configuration is recorded below as an observation rather than as a check.

| Check ID | Assertion | Target | Query | Expected result | Pass condition | On failure |
| --- | --- | --- | --- | --- | --- | --- |
| `GATE-SEC-01` | Every one of the ten application tables is reachable from the `x_bst_startuptrk` scope only, over no external route. | `sys_db_object` | `sysparm_query=nameSTARTSWITHx_bst_startuptrk_^access=package_private^read_access=false^ws_access=false&sysparm_fields=name,access,read_access,ws_access&sysparm_limit=50` | `HTTP 200` with a `result` array holding exactly 10 records — the seven entity tables and the three supporting tables, all with `access` `package_private`, `read_access` `false` and `ws_access` `false`. | Status is exactly `200` and `result` holds exactly 10 records. | Fewer than 10: at least one table is open on a route the application's own controls never see. Take the difference between the ten names in [`./data-model.md`](./data-model.md) and the names returned — each missing name is a table whose read posture did not commit. The staging table is the one that matters most, because it holds verbatim upstream payloads and unvalidated personal data. More than 10: a table outside the delivered set carries the scope prefix. Report `GATE-SEC-01` with the names observed and investigate. **No rollback**, and acceptance is not blocked — but a missing entity table will already have failed its own required gate, and a missing supporting table is a defect in the delivered artifact whose remedy is to correct the dictionary record and re-import. |
| `GATE-SEC-02` | No application table permits any cross-scope write, configuration or schema operation. | `sys_db_object` | `sysparm_query=nameSTARTSWITHx_bst_startuptrk_^create_access=false^update_access=false^delete_access=false^alter_access=false^configuration_access=false&sysparm_fields=name,create_access,update_access,delete_access,alter_access,configuration_access&sysparm_limit=50` | `HTTP 200` with a `result` array holding exactly 10 records. | Status is exactly `200` and `result` holds exactly 10 records. | Fewer than 10: at least one table accepts writes or schema changes from outside the scope, which would let an out-of-scope caller alter application data through a route the application's own controls never see. **This is the posture check that matters.** Report `GATE-SEC-02` with the names of the tables missing from the result and treat it as a blocking defect in the delivered artifact: correct the dictionary records, re-export and re-import. Do not put the application into use with this check failing. **No rollback** — the defect lives in the Update Set. |
| `GATE-SEC-03` | Both REST endpoint access controls committed. | `sys_security_acl` | `sysparm_query=type=REST_Endpoint^nameSTARTSWITHBoston Startup Tracker API&sysparm_fields=name,type,operation` | `HTTP 200` with a `result` array holding exactly 2 records, `Boston Startup Tracker API read` and `Boston Startup Tracker API write`, both with `operation` `execute`. | Status is exactly `200`, `result` holds exactly 2 records, and both carry `operation` `execute`. | Fewer than 2: endpoint authorisation on the Scripted REST API falls back to the platform's broad default REST access control, which admits any authenticated internal user. Report `GATE-SEC-03` and correct it before the API is exposed. **No rollback.** |

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

1 column-count check = **1 acceptance-required, non-rollback check**, class 2.

4 access-posture and secured-read checks = **4 non-normative diagnostics**, class 3.

**15 checks block acceptance; 11 of them trigger rollback.** The classes are defined under [Three classes of check](#three-classes-of-check-and-what-each-one-blocks).

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

The one acceptance-required, non-rollback check:

| # | Check ID | Assertion | Blocks acceptance | Triggers rollback |
| --- | --- | --- | --- | --- |
| A1 | `GATE-COL-01` | The seven entity tables carry exactly 53 columns between them. | **Yes** | No |

The four non-normative diagnostics, recorded and never required:

| # | Check ID | Assertion |
| --- | --- | --- |
| D1 | `GATE-SEC-01` | All ten application tables are reachable from the `x_bst_startuptrk` scope only. |
| D2 | `GATE-SEC-02` | No application table permits any cross-scope write, configuration or schema operation. |
| D3 | `GATE-SEC-03` | Both REST endpoint access controls committed. |
| D4 | `GATE-SEC-04` | Each of the seven entity tables resolves and is readable through the ACL-respecting path after the commit. |

**The rollback pass condition** is that all eleven class 1 gates pass. There is no partial pass among them, none is advisory, and none may be skipped, deferred or waived.

**The acceptance pass condition** is that all eleven class 1 gates pass and `GATE-COL-01` passes — **twelve checks in total**. The four class 3 diagnostics are run and recorded on every deployment whatever their outcome, and none of them blocks acceptance. A class 2 or class 3 failure leaves the deployment in place and blocks acceptance until the delivered artifact is corrected and re-imported, or — for a class 3 check only — until the platform owner records written acceptance of the exposure in the evidence record; neither class ever initiates the rollback. The **rollback** condition remains the eleven class 1 gates alone.

One further condition is recorded and is **not a check of this delivery at all**: the instance's XML entity-resolution configuration, under [Instance prerequisite for XML entity resolution](#instance-prerequisite-for-xml-entity-resolution). It is owned by the platform owner, is not settable or fixable from within this application, and is reported rather than gated. There is no `GATE-SEC-04` in this gate set.

`PRE-COMMIT-01` and `PRE-COMMIT-02` are preconditions of this gate set, not members of it, so neither count above is changed by them. They are equally not waivable: the eleven required gates are evaluated only on a deployment whose commit had records to apply.

Gates 1 to 7, `GATE-COL-01` and `GATE-SEC-04` cover the seven entity tables only. `GATE-SEC-01` covers all ten — `x_bst_startuptrk_m2m_round_investor`, `x_bst_startuptrk_ingest_staging` and `x_bst_startuptrk_rate_limit_counter` — and `GATE-SEC-02` covers all ten; those three supporting tables are otherwise documented in [`./data-model.md`](./data-model.md).

The three supporting tables — `x_bst_startuptrk_m2m_round_investor`, `x_bst_startuptrk_ingest_staging` and `x_bst_startuptrk_rate_limit_counter` — carry no required gate. They are `package_private` with `ws_access` `false`, exactly as the seven entity tables now are, so no Table API read of them can succeed and none is attempted; they are documented in [`./data-model.md`](./data-model.md) and exercised by the Automated Test Framework suites built in [`./manual-build/05-atf-test-suites.md`](./manual-build/05-atf-test-suites.md).

## Failure handling

On failure of any one of the **eleven required** gates:

1. Report the failing gate by its identifier, together with the HTTP status and the response body observed.
2. If the observed status is `HTTP 500` and the gate has not yet been retried, wait 30 seconds and reissue the identical request exactly once, per the [Transient-error retry rule](#transient-error-retry-rule). Evaluate the gate on that response and report the retry's status and body alongside the first.
3. Initiate the rollback when the pass condition still does not hold — that is, immediately for any status other than `HTTP 500`, and for `HTTP 500` only after the single retry has also failed. **The rollback is permitted only under the conditions [`./deployment-runbook.md`](./deployment-runbook.md) states**, which include a proven clean install and an exact scope identifier captured this run; where those conditions do not hold, report the failure and stop rather than delete.

The failing gate is reported before the rollback is initiated. A gate that passes on its retry is a pass, is recorded as such, and initiates no rollback.

**On failure of `GATE-COL-01`**, follow steps 1 and 2 above and then **stop without rolling back**. The deployment stays in place, and **acceptance is blocked**: record the observed column count and the per-table split, correct the Update Set so the seven entity tables carry exactly the 53 binding columns, and re-import. Do not delete the scope — the tables and roles committed correctly, and deleting them discards working artifacts to fix a dictionary defect that lives in the source file. Do not record criterion 1 as met while this check is failing.

**On failure of one of the four class 3 diagnostics**, no rollback is initiated under any circumstance, and **acceptance is blocked**. Follow steps 1 and 2 above, report the check by its identifier with the status and body observed, act on its own **On failure** cell, and record the outcome in the evidence record. The application is **not put into use** while a class 3 check is failing: either the delivered posture is corrected and re-imported, or the platform owner records written acceptance of the named exposure in the evidence record. That policy applies to all three equally — a `GATE-SEC-01` failure exposes raw staged payloads to an external route and a `GATE-SEC-03` failure removes endpoint authorisation, neither of which is milder than the cross-scope write access `GATE-SEC-02` covers; the remedy there is to correct the dictionary records and re-import, not to destroy the installation.

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
| **Aggregate** | | | 12 of 12 acceptance-blocking checks required — the 11 gates above and this one. The four diagnostics below are recorded, never required |

The four non-normative diagnostics are recorded separately again, so a reader can never mistake one of them for part of the acceptance set:

| Security check ID | Result | Timestamp (UTC) | Note, and the written acceptance recorded for any failure |
| --- | --- | --- | --- |
| `GATE-SEC-01` | | | |
| `GATE-SEC-02` | | | |
| `GATE-SEC-03` | | | |
| `GATE-SEC-04` | | | seven log lines, each `valid=true can_read=true` |
| **Aggregate** | | | Non-normative. Recorded, not required. A failure here does not fail the deployment and does not block acceptance. |

The instance prerequisite is recorded as an observation rather than a result:

| Observation | Value read | Timestamp (UTC) | Reported to |
| --- | --- | --- | --- |
| `glide.stax.allow_entity_resolution` | | | |
| `glide.stax.whitelist_enabled` | | | |

Every table is filled in the same way. Record `pass` or `fail` in **Result**. Record the time of the request in **Timestamp (UTC)** in `YYYY-MM-DD HH:MM:SS` form. Record the observed HTTP status and the `result` record count in **Note**, and for a failing gate or check also the response body. For `GATE-TBL-01` through `GATE-TBL-07` record the four field values returned — `name`, `access`, `read_access` and `ws_access` — because all four are asserted, and a `fail` is diagnosed from which of them departed. For `GATE-COL-01` record the count returned **and** the per-table split, since a count that is off is diagnosed from the split. For the instance prerequisite, record each property value as read, or `absent`, and the name of the platform owner it was reported to where it is not the hardened value. Record no credential value in any field.

Where a gate was retried under the [Transient-error retry rule](#transient-error-retry-rule), record the retry in the same row: note the first `HTTP 500`, the 30-second wait and the retry's status, and set **Timestamp (UTC)** to the retried request. **Result** carries the outcome of the retry, so a gate that returned `HTTP 500` and then `HTTP 200` is recorded as `pass` with the retry noted. A row that shows `pass` with no note of a retry means the gate passed on its first response.

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
