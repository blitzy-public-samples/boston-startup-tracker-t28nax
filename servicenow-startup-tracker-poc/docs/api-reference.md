# API reference — `x_bst_startuptrk`

This document is the REST contract reference for the ServiceNow scoped application `x_bst_startuptrk`. It states the one Scripted REST API definition, all 31 operations across six logical resources, who may call them and how that is enforced, the JSON-only media-type contract, the pagination contract, the validation applied to every stored field, every status code and error body the API returns, the Script Include call graph that doubles as a rename-impact list, and the thirteen system properties the application reads. Every operation is enumerated individually with its method, its path template, what it returns and its success status; every Script Include and every property is likewise listed one by one.

**Authority.** The frozen prompt and the Agent Action Plan are authoritative for all application content, and they govern the Update Set XML and this document alike. The Update Set XML at [`../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml`](../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml) is the implementation of that specification and the transcription source for everything below: the one `sys_ws_definition` record, the 31 `sys_ws_operation` records, the 9 `sys_script_include` records and the 13 `sys_properties` records it carries. Where this document and those records disagree about a path, a method, a parameter name, a response member, a status code, a class name or a property key, the records are checked against the prompt and the plan first. Where the records match the specification, this document is corrected to them. Where the records depart from it, the records are corrected.


The table names, column names and premium markers used below are the ones established in [`./data-model.md`](./data-model.md). The field-level read gate applied to every response is the one specified in [`./access-control.md`](./access-control.md); this document states where that gate applies and does not restate the access-control scheme.

This document carries no rationale. Every decision behind this contract, every alternative considered and every risk it carries is to be recorded in [`../../docs/decisions/DECISION_LOG.md` (planned)](../../docs/decisions/DECISION_LOG.md), which is to be the single source of truth for "why".

## Referenced documents

This document is self-contained. The definition, all 31 operations, the pagination contract, every request filter, every response representation, all three error contracts, the call graph and the thirteen properties are stated here in full; no statement of the contract requires reading another file.

Some documents named below are **planned artifacts of this package**. Every link to one carries the marker **(planned)** in its link text. A statement about a planned document describes what that document is required to contain; it is not a claim that the content can be read from it. The delivered package documents are the Update Set XML, `./data-model.md`, `./access-control.md`, `./validation-gates.md` and `../sample-data/README.md`.

**Reviewer.** This document is to be the artifact validated by the **API/Integration** reviewer entry in [`../../docs/review/CRITICAL_DECISIONS.md` (planned)](../../docs/review/CRITICAL_DECISIONS.md), covering the credential handling of the ingestion integration and the contract stated here.

## The API definition

One `sys_ws_definition` record declares the whole surface. Thirty-one `sys_ws_operation` records hang off it.

| Attribute | Value |
| --- | --- |
| Name | `Boston Startup Tracker API` |
| API identifier | `v1` |
| Scope | `x_bst_startuptrk` |
| Physical base path | `/api/x_bst_startuptrk/v1/` |
| Operations | 31 |
| `consumes` / `consumes_customized` | `application/json` / true |
| `produces` / `produces_customized` | `application/json` / true |
| `enforce_acl` | The `Boston Startup Tracker API read` access control |
| `active` | true |

### Base path

A scoped Scripted REST API always carries its namespace segment in its base path. The logical base path `/api/v1/` therefore resolves **physically** to `/api/x_bst_startuptrk/v1/`.

**Call the physical path.** Every request goes to `https://<instance>.service-now.com/api/x_bst_startuptrk/v1/<resource>`. The logical form is not served and does not resolve. No consumer may be written against it. The namespace segment is to be flagged again in [`./gaps-and-flags.md` (planned)](./gaps-and-flags.md).

The full request line for the first resource:

```text
GET https://<instance>.service-now.com/api/x_bst_startuptrk/v1/startups?sysparm_limit=20&sysparm_offset=0
```

Every path template in this document is written relative to that base path. `GET /startups` means `GET /api/x_bst_startuptrk/v1/startups`.

### Authentication and authorisation

Every one of the 31 operations requires **both** authentication and access-control authorisation, and every one names the access control that authorisation consults. Each `sys_ws_operation` record carries `requires_authentication` true, `requires_acl_authorization` true, `requires_snc_internal_role` false, and an `enforce_acl` binding. An unauthenticated request is rejected by the platform before the operation script runs.

**Who may call this API.** Two `REST_Endpoint` access controls, both with operation `execute`, decide whether an operation runs at all:

| Access control | Roles that satisfy it | Bound to |
| --- | --- | --- |
| `Boston Startup Tracker API read` | `x_bst_startuptrk.admin`, `x_bst_startuptrk.premium_user`, `x_bst_startuptrk.user` | the `sys_ws_definition` record and all 13 `GET` operations |
| `Boston Startup Tracker API write` | `x_bst_startuptrk.admin` | all 18 `POST`, `PUT` and `DELETE` operations |

The definition-level binding applies the read control to every call and the operation-level binding then applies the method-appropriate control, so a mutation must satisfy both. A caller holding no application role receives `HTTP 403`; so does a caller holding only `x_bst_startuptrk.user` or `x_bst_startuptrk.premium_user` who attempts a mutation.

This is stated explicitly because a Scripted REST API that requires authorisation but names no control does **not** get scoped-role authorisation: evaluation falls back to the platform's default REST control, which denies the external-user role but admits any authenticated internal user. These two controls are what make the role restriction real. `GATE-SEC-03` in [`./validation-gates.md`](./validation-gates.md) confirms both committed.

The same rule is also enforced in code, so it does not depend on platform access-control evaluation alone. Every operation script calls a shared guard immediately after the rate limiter:

| Guard | Applied to | Refusal |
| --- | --- | --- |
| `RestResponseBuilder.rejectUnauthorisedRead()` | the 13 read operations | `HTTP 403` with body `{"error": "Caller holds no Boston Startup Tracker role"}` |
| `RestResponseBuilder.rejectUnauthorisedWrite()` | the 18 mutations | `HTTP 403` with body `{"error": "Caller holds no Boston Startup Tracker administrator role"}` |

Four further enforcement rules bind every operation, and they are specified in [`./access-control.md`](./access-control.md):

- **Secured read path.** Every caller-facing read uses `GlideRecordSecure`. No operation reads through the unsecured `GlideRecord`, and no Script Include reads a premium-gated column on a caller's behalf and returns it.
- **Secured counting.** `total_count` is produced by secured iteration, not by an aggregate query. Aggregate queries do not apply access controls, so they are not used for any caller-facing value; the string `GlideAggregate` does not appear in the delivered Update Set.
- **Per-field read gate.** Response serialisation tests each field with an element-level read check and **omits the key entirely** when the check fails. A denied premium field is absent from the response object; it does not appear with a null, an empty string or a placeholder.
- **No bypass.** None of the nine Script Includes is client-callable and none runs with elevated privilege, so no operation can reach a gated field through an elevated helper.

**No alternate route to the same data.** All ten application tables are delivered with `ws_access` false, so they are not served by the platform Table API at `/api/now/table/<table>`, and with `access` `package_private`, so no out-of-scope script can reach them. The operations in this document are the only programmatic route to the data, which is what makes the rate limiting, the endpoint authorisation and the per-field gate below meaningful rather than optional. The posture is gated as `GATE-SEC-01` and `GATE-SEC-02` in [`./validation-gates.md`](./validation-gates.md).

The seven premium-gated fields, their gating roles and the twenty-one role-by-field outcomes are tabulated in [`./access-control.md`](./access-control.md) and are not restated here. This document marks, on each resource representation, which of its fields are gated.

### Content type

**This API is JSON only, and the restriction is enforced rather than merely described.**

| Where | Setting |
| --- | --- |
| `sys_ws_definition` | `consumes` `application/json`, `consumes_customized` true; `produces` `application/json`, `produces_customized` true |
| every one of the 31 `sys_ws_operation` records | the same four values |

The `_customized` flags matter: without them the platform substitutes its default media-type list, which also advertises `application/xml` and `text/xml`.

A request carrying a body must send `Content-Type: application/json`. Before any operation touches the request body, `RestResponseBuilder.rejectNonJsonBody()` compares the declared media type — lower-cased, with parameters such as `; charset=utf-8` removed — against `application/json`. Anything else, **including an absent `Content-Type` header**, is refused with:

```text
HTTP 415
{"error": "Request body must be application/json"}
```

The guard runs on the 12 body-bearing operations, the six `POST` and six `PUT` resources. The 13 `GET` and six `DELETE` operations read no body and do not need it.

The reason for refusing before the body is read: had the API continued to advertise `application/xml`, a request body would be handed to the platform XML parser, exposing entity-expansion and external-entity handling to untrusted input. Narrowing the declared media types and refusing at the boundary removes that surface from this application entirely. The instance-level parser configuration — `glide.stax.allow_entity_resolution` false and `glide.stax.whitelist_enabled` true — is defence in depth beneath it and is gated as `GATE-SEC-04`; those are Global-scope properties, so the scoped application deliberately does not ship them.

Every response body is `application/json`. The only response without a body is `HTTP 204` on a successful delete.

**Output encoding is the consumer's responsibility.** Response bodies are serialised to JSON by the platform, which escapes the JSON string context correctly. Values are stored as supplied, so any consumer that renders a value into a different context must encode for that context — a Service Portal widget must bind through Angular interpolation, never through raw HTML binding. The API reduces the risk at the input boundary by allowlisting the structured fields: URL fields accept only an absolute `https` URL drawn from the RFC 3986 character set, which cannot contain `<`, `>`, a quote or a backtick, and email fields accept only characters that carry no HTML significance. See [Field validation](#field-validation).

The contract is enforced by the records themselves, not merely by convention. The `sys_ws_definition` record and every one of the 31 `sys_ws_operation` records declare `consumes` and `produces` as `application/json` alone, with `consumes_customized` and `produces_customized` both `true` so the declared value overrides the platform default of `application/json,application/xml,text/xml`. No XML media type is registered anywhere on the API, so a request sending `Accept: application/xml` or `Accept: text/xml` cannot negotiate an XML response body, and a request sending `Content-Type: application/xml` is not accepted. A consumer that requires XML is not supported.

### Deviations from the legacy contract

The contract stated in this document differs from the legacy Flask contract in three respects, and consumers discover the differences here:

1. The **paths** differ. The physical base path is `/api/x_bst_startuptrk/v1/`, not `/api/v1/`.
2. The **pagination parameter names** differ. They are `sysparm_limit` and `sysparm_offset`, not `page` and `per_page`.
3. The **response envelope key** differs. The count member is `total_count`, not `total`.

**No compatibility shim, alias or legacy-contract layer exists.** No operation accepts `page` or `per_page`, no response carries `total`, and no route serves the logical `/api/v1/` form. Every element of this contract — each path, each parameter name, each response member and each status code — is specified by the prompt and the Agent Action Plan. The legacy forms are recorded under [Legacy provenance](#legacy-provenance) as historical antecedents only. Each change is to be recorded as a row in [`../../docs/decisions/DECISION_LOG.md` (planned)](../../docs/decisions/DECISION_LOG.md).

## The pagination contract

Every list operation in this API takes the same two request parameters and returns the same envelope. There are seven list operations: the six resource list operations and the nested executives sub-resource.

### Request parameters

| Parameter | Meaning | Type | Accepted on |
| --- | --- | --- | --- |
| `sysparm_limit` | Page size — the maximum number of records the response array carries. | Integer | Every list operation |
| `sysparm_offset` | Zero-based starting offset into the ordered result set. `0` returns the first page. | Integer | Every list operation |

Both parameters are optional. Neither is accepted on a read-one, create, update or delete operation, where a single record is addressed by its path parameter.

### Filter parameter validation

Every filter parameter is **validated and then bound as a query operand**. No caller value is ever concatenated into encoded-query grammar, so a `^`, `^OR` or `^NQ` inside a supplied value is matched as an ordinary character and cannot introduce a condition or displace the startup inclusion criteria.

| Parameter kind | Validation | Behaviour on a value that fails validation |
| --- | --- | --- |
| Record identifier — `startup`, and the `{startup_id}` path parameter of the nested sub-resource | Must match 32 lower-case hexadecimal characters | `400` with `<parameter> must be a 32 character sys_id` |
| Choice value — `industry`, `type`, `round_type`, `department` | Must be a member of the column's choice list, matched case-insensitively | `400` with `<parameter> must be one of <choice list>` |
| Free text — `name`, `location`, `source` | Control characters replaced with a space, trimmed, truncated to 100 characters, then bound as a `CONTAINS` operand | Never fails; an unmatchable value simply returns no rows |

`{id}` path parameters on the read-one, update and delete operations are validated the same way as a record-identifier filter, so a malformed identifier answers `400` rather than `404`.

### Bounds

`RestQueryHelper` parses and clamps both parameters. It reads its bounds from two system properties through `AppProperties`:

| Property | Shipped value | Role |
| --- | --- | --- |
| `x_bst_startuptrk.rest.default_limit` | `20` | The page size applied when `sysparm_limit` does not resolve to a usable value. |
| `x_bst_startuptrk.rest.max_limit` | `50` | The largest page size the API will serve. |

The resolution rules are exact:

| Supplied `sysparm_limit` | Applied limit |
| --- | --- |
| Absent | `x_bst_startuptrk.rest.default_limit` |
| Non-numeric | `x_bst_startuptrk.rest.default_limit` |
| `0` or negative | `x_bst_startuptrk.rest.default_limit` |
| Greater than `x_bst_startuptrk.rest.max_limit` | Clamped to `x_bst_startuptrk.rest.max_limit` |
| Between `1` and `x_bst_startuptrk.rest.max_limit` inclusive | The supplied value |

| Supplied `sysparm_offset` | Applied offset |
| --- | --- |
| Absent | `0` |
| Non-numeric, including a negative value | `0` |
| Between `0` and `10000` inclusive | The supplied value |
| Greater than `10000` | **Refused** — `400` with `sysparm_offset must not exceed 10000` |

A malformed `sysparm_limit` or `sysparm_offset` is normalised rather than refused. **An offset above the page-depth ceiling is the one exception**, and it is refused rather than clamped.

**The `sysparm_offset` ceiling is `10000`.** The offset is passed to the platform's result-window API, which must walk the result set to reach the requested position, so an arbitrarily deep offset lets one request consume unbounded query time. The ceiling is a fixed constant in `RestQueryHelper`, not a property, because it is a resource-consumption bound rather than a tuning knob. It is checked before any query is built, so a refused request performs no database work:

```text
HTTP 400
{"error": "sysparm_offset must not exceed 10000"}
```

Clamping to the ceiling instead would silently return the ten-thousandth page for every deeper request, which a consumer paging forward could not distinguish from having reached the end. Refusing makes the boundary visible. A consumer that needs to reach beyond record 10,000 narrows the result set with the resource's filter parameters rather than paging deeper; every list operation carries at least one filter.

All seven list operations apply the ceiling identically, and each checks the parsed result before it builds a query. The applied limit and offset are echoed in the response, so a consumer always reads back what the API actually used.

Both page-size properties are themselves validated. If `x_bst_startuptrk.rest.max_limit` does not resolve to a positive whole number the API falls back to a ceiling of `50`; if `x_bst_startuptrk.rest.default_limit` does not, it falls back to `20`. The resolved default is then clamped to the resolved maximum, so a default larger than the maximum can never widen a page.

### Result ordering

Every list operation applies a **documented order followed by an always-unique `sys_id` tie-breaker**, so paging by `sysparm_offset` over records that share an order value neither repeats nor omits a row.

| List operation | Order |
| --- | --- |
| `GET /startups` | `name` ascending, then `sys_id` ascending |
| `GET /founders` | `name` ascending, then `sys_id` ascending |
| `GET /founders/{startup_id}/executives` | `name` ascending, then `sys_id` ascending |
| `GET /investors` | `name` ascending, then `sys_id` ascending |
| `GET /funding-rounds` | `round_date` **descending**, then `sys_id` ascending |
| `GET /jobs` | `posted_date` **descending**, then `sys_id` ascending |
| `GET /news` | `published_date` **descending**, then `sys_id` ascending |

A record with an empty date sorts last on the three descending orders. The `participating_investors` array of a funding round is likewise ordered by the join row's `sys_id`, so it is stable between reads.

### Ordering

Every list operation sorts on a documented column **and then on `sys_id`**, which is unique. Each result set therefore has exactly one total order, and offset paging over it is stable across requests even where the primary sort column ties.

| List operation | Primary sort | Tie breaker |
| --- | --- | --- |
| `GET /startups` | `name` ascending | `sys_id` ascending |
| `GET /founders` | `name` ascending | `sys_id` ascending |
| `GET /founders/{startup_id}/executives` | `name` ascending | `sys_id` ascending |
| `GET /investors` | `name` ascending | `sys_id` ascending |
| `GET /funding-rounds` | `round_date` descending | `sys_id` ascending |
| `GET /jobs` | `posted_date` descending | `sys_id` ascending |
| `GET /news` | `published_date` descending | `sys_id` ascending |

The ordering is not caller-configurable: no operation accepts a sort parameter. A consumer paging a resource to exhaustion may rely on each record appearing exactly once for as long as the underlying rows are unchanged.

### Query values

Every caller-supplied filter value is **validated before it reaches a query**, and every condition is bound through `addQuery` and `addOrCondition` rather than concatenated into an encoded query string. `RestQueryHelper` owns the validation and the binding; the operations pass it validated values and never assemble query text.

| Value class | Accepted form | Rejected |
| --- | --- | --- |
| Record identifier — `startup` on `/founders`, `/funding-rounds`, `/jobs` and `/news`, and `{startup_id}` on the nested executives sub-resource | Exactly 32 hexadecimal characters, matched case-insensitively and applied lowercased | Anything else, including a partial identifier, an encoded query fragment or an empty path segment |
| Choice value — `industry` on `/startups`, `type` on `/investors`, `round_type` on `/funding-rounds`, `department` on `/jobs` | An exact member of that column's choice list, case-sensitive | Any value absent from the list |
| Free text — `name` on `/startups`, `/founders` and `/investors`, `location` on `/startups`, `source` on `/news` | Up to 100 characters, no control characters, no `^` | Over-length values, control characters, and the `^` clause separator |

A rejected value returns `400` with the general failure body and a message naming the parameter. An **absent** filter is not a rejection: the filter is simply not applied.

Two properties of that validation are part of the contract. `^`, `^OR` and `^NQ` are encoded-query operators: every filter value is bound as a parameter and any value carrying the clause separator is rejected outright, so **no filter value can become query syntax**. Identifiers and choice values are matched against their exact permitted forms, so every filtered read runs on the intended, indexed predicate.

### Response envelope

`RestResponseBuilder` builds every list response. The envelope has four members that are always present, and one that appears conditionally.

| Member | Type | Always present | Content |
| --- | --- | --- | --- |
| `result` | Array of objects | Yes | The page of records, each serialised through the per-field read gate. |
| `total_count` | Integer | Yes | The number of records the caller may read that match the query, across all pages. |
| `limit` | Integer | Yes | The applied limit, after the bounds above. |
| `offset` | Integer | Yes | The applied offset, after the bounds above. |
| `total_count_capped` | Boolean, always `true` when present | No | Present **only** when the matching set reached the counting ceiling of `10000`, in which case `total_count` reads exactly `10000` and is a floor rather than an exact figure. Absent whenever `total_count` is exact. |

A consumer that ignores `total_count_capped` reads `total_count` as `10000` and pages until the `result` array comes back short, which is correct behaviour; a consumer that displays a total should test for the member and render the figure as a minimum. The member is added only when the ceiling was reached, so its mere presence carries the meaning and it never appears as `false`.

Each object in `result` carries `sys_id` plus one key per readable field of the resource. Values are encoded as follows:

| Column type | JSON encoding |
| --- | --- |
| `string`, choice list, multi-choice | String, or `null` when the column is empty |
| `integer` | Whole number, or `null` when the column is empty |
| `boolean` | `true` or `false` |
| `currency` | The stored amount as a string, or `null` when the column is empty |
| `glide_date` | String, or `null` when the column is empty |
| `reference` | An object carrying `value`, the referenced record's `sys_id`, and `display_value`, its display label — or `null` when the reference is empty |

A worked `/startups` list response, requested with `sysparm_limit=2&sysparm_offset=0` by a caller who can read the premium fields:

```json
{
  "result": [
    {
      "sys_id": "3d5e9c1b7a2f4e08b6c14d0392fa5e77",
      "name": "Beacon Hill Robotics",
      "description": "Autonomous inspection robots for commercial building operators.",
      "industry": "Deeptech",
      "founded_year": 2019,
      "headquarters_location": "Boston, MA",
      "website": "https://beaconhillrobotics.example.com",
      "logo_url": "https://cdn.example.org/logos/beacon-hill-robotics.png",
      "funding_stage": "Series B",
      "total_funding_usd": "48000000",
      "active": true,
      "institutional_funding_last_5yrs": true,
      "employee_count_range": "51-200"
    },
    {
      "sys_id": "9b04f2ea61c74d3fa8570e1cb3d6924c",
      "name": "Seaport Ledger",
      "description": "Treasury reconciliation for mid-market lenders, built on an event log.",
      "industry": "Fintech",
      "founded_year": 2021,
      "headquarters_location": "Seaport, Boston, MA",
      "website": "https://www.seaportledger.example.com",
      "logo_url": "https://cdn.example.net/logos/seaport-ledger.svg",
      "funding_stage": "Series A",
      "total_funding_usd": "16500000",
      "active": true,
      "institutional_funding_last_5yrs": true,
      "employee_count_range": "11-50"
    }
  ],
  "total_count": 37,
  "limit": 2,
  "offset": 0
}
```

The same request made by a caller holding only `x_bst_startuptrk.user` returns the same envelope with the same two records, and each record object is missing the `total_funding_usd` and `institutional_funding_last_5yrs` keys. The keys are absent, not null. `total_count`, `limit` and `offset` are unchanged.

### `total_count` semantics

`total_count` is the number of records the **caller may read** that match the operation's query, independent of `limit` and `offset`.

**It is produced on the access-controlled read path, by bounded iteration — never by an aggregate query.** `RestResponseBuilder.countState()` opens the table through `GlideRecordSecure`, returns zero immediately if the caller fails the table-level read check, applies the same conditions the page applies, bounds the query at the counting ceiling plus one, and counts the rows the secured cursor actually yields. Each list operation builds its conditions once, as a single function, and passes that one function to both the count and the record query, so the count and the page cannot be built from different filters.

**Why not an aggregate.** Aggregate queries do not evaluate access controls. An aggregate count therefore reports the number of rows in the table, which for a caller who may not read them all is a disclosure: the caller learns the size of a result set it cannot see. The string `GlideAggregate` does not appear anywhere in the delivered Update Set, and no caller-facing value in this API is derived from an unsecured query.

**The counting ceiling is `10000`.** Iterating a secured cursor costs one row-level access evaluation per row, so an unbounded count is an unbounded cost — the same resource-consumption concern that bounds `sysparm_offset`. `countState()` stops at the ceiling and reports that it stopped; the envelope then carries `total_count` `10000` together with `total_count_capped` `true`, as specified under [Response envelope](#response-envelope). `total_count` is never silently understated: either it is exact, or the envelope says it is a floor.

**This makes `total_count` correct under any access-control posture, present or future.** The seven entity tables currently grant table-level read to all three roles and differ only at field level, so today every caller counts the same rows; a secured count and an aggregate count would agree. Counting on the secured path means that if a record-level restriction is ever added to any table, `total_count` continues to report what the caller may read, with no change to this contract and no change to any operation script. The access-control posture itself is specified in [`./access-control.md`](./access-control.md).

### The inclusion criteria and the count

Where the startup inclusion criteria apply to a list operation, they are applied **identically to the result set and to `total_count`**. `StartupSearchService.buildPlan()` produces one query plan, and one `applyConditions` function wrapping `StartupSearchService.applyPlan()` is handed to both the secured count and the secured result set, so the criteria reach both through the platform condition API from a single definition; applying the criteria to one and not the other makes the count disagree with the page contents. The predicate itself — `active` true and `headquarters_location` containing a configured location token — is specified in [`./data-model.md`](./data-model.md) and is not restated here.

Because the plan is applied through the condition API rather than assembled as a query string, a caller cannot reach the predicate: supplying `name=^ORactive=false` matches startups whose name literally contains that text, which is none of them, rather than widening the result set.

## Resources

Six logical resources. Each section lists every operation on that resource, then gives the resource's JSON representation and marks the premium-gated fields. A premium-gated field is **omitted from the response object** for a caller the field-level read ACL denies; the key is absent, never present with a null.

Path templates are relative to the physical base path `/api/x_bst_startuptrk/v1/`. `{id}` is the record's `sys_id`.

Each resource that pages also accepts query filters. The six per-resource tables below define **thirteen filters** in total, and each states its semantics in a **Comparison** column. That column takes one of exactly three values, each of which names a platform encoded-query operator, so every claim in it is checkable against the operation script:

| Comparison | Encoded-query operator | Count | Applies to |
| --- | --- | --- | --- |
| Case-insensitive contains | `LIKE` | 5 | `name` on `/startups`, `/founders` and `/investors`; `location` on `/startups`; `source` on `/news` |
| Exact match against a choice value | `=` | 4 | `industry` on `/startups`; `type` on `/investors`; `round_type` on `/funding-rounds`; `department` on `/jobs` |
| Exact match against a startup `sys_id` | `=` | 4 | `startup` on `/founders`, `/funding-rounds`, `/jobs` and `/news` |

A filter whose value is absent or empty after trimming contributes no clause. Filters combine with a logical AND, and the same encoded query serves both the returned page and `total_count`. The three `/startups` filters are assembled by `StartupSearchService`; the other ten are assembled in their own operation script.

### `/startups`

The Startup resource over `x_bst_startuptrk_startup`. Five operations.

| Method | Path template | Description | Success status |
| --- | --- | --- | --- |
| `GET` | `/startups` | Lists and searches startups. Returns the paginated envelope carrying a page of startup objects, `total_count`, `limit` and `offset`. | `200` |
| `GET` | `/startups/{id}` | Reads one startup by `sys_id`. Returns a single startup object. | `200` |
| `POST` | `/startups` | Creates a startup from the request body. Returns the created startup object as read back through the secured path. | `201` |
| `PUT` | `/startups/{id}` | Updates the named startup with the supplied fields. Returns the updated startup object. | `200` |
| `DELETE` | `/startups/{id}` | Deletes the named startup. Returns no body. | `204` |

`GET /startups` applies the startup inclusion criteria for **authenticated non-administrative callers**. There is no unauthenticated caller of this operation, or of any other: every operation requires authentication, as recorded under [Authentication and authorisation](#authentication-and-authorisation). A caller holding `x_bst_startuptrk.admin`, or the platform administrator role, receives the unfiltered set; every other authenticated caller receives the filtered set. Records failing the criteria remain in the table and are reachable through `GET /startups/{id}` and through the platform's own list views. The predicate is in [`./data-model.md`](./data-model.md).

`GET /startups` accepts three query filters in addition to the pagination parameters. All three are optional and combine with a logical AND, and with the inclusion criteria where those apply.

| Filter | Column matched | Comparison | Accepted form |
| --- | --- | --- | --- |
| `name` | `name` | Case-insensitive contains | Free text, per [Query values](#query-values) |
| `industry` | `industry` | Exact match against a choice value | A member of `Startup.industry` |
| `location` | `headquarters_location` | Case-insensitive contains | Free text, per [Query values](#query-values) |

`StartupSearchService` builds the query for both the filters and the inclusion criteria, and the same query plan produces `total_count`. Results are ordered by `name`, then by `sys_id`; see [Result ordering](#result-ordering).

Representation. Twelve fields plus `sys_id`.

| Field | Type | Premium-gated |
| --- | --- | --- |
| `sys_id` | String | — |
| `name` | String | — |
| `description` | String | — |
| `industry` | String, choice value | — |
| `founded_year` | Integer | — |
| `headquarters_location` | String | — |
| `website` | String | — |
| `logo_url` | String | — |
| `funding_stage` | String, choice value | — |
| `total_funding_usd` | String, currency amount | **Premium** |
| `active` | Boolean | — |
| `institutional_funding_last_5yrs` | Boolean | **Premium** |
| `employee_count_range` | String, choice value | — |

`total_funding_usd` and `institutional_funding_last_5yrs` are omitted from the response object for a caller holding only `x_bst_startuptrk.user`. The same twelve fields are the writable set on `POST` and `PUT`; a field absent from the request body is left unchanged.

### `/founders`

The Founder resource over `x_bst_startuptrk_founder`, plus one nested sub-resource serving Executive records. Six operations.

| Method | Path template | Description | Success status |
| --- | --- | --- | --- |
| `GET` | `/founders` | Lists founders. Returns the paginated envelope carrying a page of founder objects, `total_count`, `limit` and `offset`. | `200` |
| `GET` | `/founders/{id}` | Reads one founder by `sys_id`. Returns a single founder object. | `200` |
| `POST` | `/founders` | Creates a founder from the request body. Returns the created founder object. | `201` |
| `PUT` | `/founders/{id}` | Updates the named founder with the supplied fields. Returns the updated founder object. | `200` |
| `DELETE` | `/founders/{id}` | Deletes the named founder. Returns no body. | `204` |
| `GET` | `/founders/{startup_id}/executives` | Lists the Executive records of the startup named by `{startup_id}`, ordered by `name` then `sys_id`. Returns the paginated envelope carrying a page of executive objects, `total_count`, `limit` and `offset`. | `200` |

`GET /founders/{startup_id}/executives` is a **nested sub-resource**, and it is how Executive records are served over REST. Executive is not a seventh top-level resource: there is no `/executives` path, and the API surface is six logical resources. `{startup_id}` is the `sys_id` of a startup; a `{startup_id}` that is absent or is not a 32-character hexadecimal identifier returns `400`.

`GET /founders` accepts two query filters in addition to the pagination parameters. Results are ordered by `name`, then by `sys_id`.

| Filter | Column matched | Comparison | Accepted form |
| --- | --- | --- | --- |
| `startup` | `startup` | Exact match against a startup `sys_id` | 32 hexadecimal characters, per [Query values](#query-values) |
| `name` | `name` | Case-insensitive contains | Free text, per [Query values](#query-values) |

Founder representation. Six fields plus `sys_id`.

| Field | Type | Premium-gated |
| --- | --- | --- |
| `sys_id` | String | — |
| `name` | String | — |
| `startup` | Reference object carrying `value` and `display_value` | — |
| `title` | String, choice value | — |
| `bio` | String | — |
| `linkedin_url` | String | — |
| `contact_email` | String | **Premium** |

Executive representation, returned by the nested sub-resource. The same six field names plus `sys_id`; the `title` choice values differ, and they are listed in [`./data-model.md`](./data-model.md).

| Field | Type | Premium-gated |
| --- | --- | --- |
| `sys_id` | String | — |
| `name` | String | — |
| `startup` | Reference object carrying `value` and `display_value` | — |
| `title` | String, choice value | — |
| `bio` | String | — |
| `linkedin_url` | String | — |
| `contact_email` | String | **Premium** |

`contact_email` is premium-gated on **both** representations and is omitted from the response object for a caller holding only `x_bst_startuptrk.user`. The two field-level read ACLs are separate records, one per table.

### `/investors`

The Investor resource over `x_bst_startuptrk_investor`. Five operations.

| Method | Path template | Description | Success status |
| --- | --- | --- | --- |
| `GET` | `/investors` | Lists investors. Returns the paginated envelope carrying a page of investor objects, `total_count`, `limit` and `offset`. | `200` |
| `GET` | `/investors/{id}` | Reads one investor by `sys_id`. Returns a single investor object. | `200` |
| `POST` | `/investors` | Creates an investor from the request body. Returns the created investor object. | `201` |
| `PUT` | `/investors/{id}` | Updates the named investor with the supplied fields. Returns the updated investor object. | `200` |
| `DELETE` | `/investors/{id}` | Deletes the named investor. Returns no body. | `204` |

`GET /investors` accepts two query filters in addition to the pagination parameters. Results are ordered by `name`, then by `sys_id`.

| Filter | Column matched | Comparison | Accepted form |
| --- | --- | --- | --- |
| `name` | `name` | Case-insensitive contains | Free text, per [Query values](#query-values) |
| `type` | `type` | Exact match against a choice value | A member of `Investor.type` |

Representation. Six fields plus `sys_id`.

| Field | Type | Premium-gated |
| --- | --- | --- |
| `sys_id` | String | — |
| `name` | String | — |
| `type` | String, choice value | — |
| `focus_areas` | String, comma-separated multi-choice values | — |
| `website` | String | — |
| `aum_usd` | String, currency amount | **Premium** |
| `portfolio_count` | Integer | — |

`aum_usd` is omitted from the response object for a caller holding only `x_bst_startuptrk.user`.

`portfolio_count` is a **derived** integer and is **read-only from the API's perspective**. It is maintained by business rules and is not part of the writable set on `POST` or `PUT`; a value supplied for it in a request body is ignored, and a subsequent read returns the derived value. Two independent mechanisms hold that contract: the operation scripts accept a narrower field set than they return, and the dictionary entry itself is read-only, which also refuses a write arriving through the platform Table API or the native form. The derivation — the count of distinct startups reachable from the investor as lead investor or as participating investor, unioned before counting — is specified in [`./data-model.md`](./data-model.md).

### `/funding-rounds`

The FundingRound resource over `x_bst_startuptrk_fundinground`. Five operations. Note the hyphen in the path segment.

| Method | Path template | Description | Success status |
| --- | --- | --- | --- |
| `GET` | `/funding-rounds` | Lists funding rounds. Returns the paginated envelope carrying a page of funding-round objects, `total_count`, `limit` and `offset`. | `200` |
| `GET` | `/funding-rounds/{id}` | Reads one funding round by `sys_id`. Returns a single funding-round object. | `200` |
| `POST` | `/funding-rounds` | Creates a funding round from the request body. Returns the created funding-round object. | `201` |
| `PUT` | `/funding-rounds/{id}` | Updates the named funding round with the supplied fields. Returns the updated funding-round object. | `200` |
| `DELETE` | `/funding-rounds/{id}` | Deletes the named funding round. Returns no body. | `204` |

`GET /funding-rounds` accepts two query filters in addition to the pagination parameters. Results are ordered by `round_date` descending, then by `sys_id`.

| Filter | Column matched | Comparison | Accepted form |
| --- | --- | --- | --- |
| `startup` | `startup` | Exact match against a startup `sys_id` | 32 hexadecimal characters, per [Query values](#query-values) |
| `round_type` | `round_type` | Exact match against a choice value | A member of `FundingRound.round_type` |

Representation. Seven serialised fields plus `sys_id` plus the assembled `participating_investors` array.

| Field | Type | Premium-gated |
| --- | --- | --- |
| `sys_id` | String | — |
| `startup` | Reference object carrying `value` and `display_value` | — |
| `round_type` | String, choice value | — |
| `amount_usd` | String, currency amount | **Premium** |
| `round_date` | String, date | — |
| `lead_investor` | Reference object carrying `value` and `display_value`, or `null` | — |
| `participating_investors` | Array of reference objects, each carrying `value` and `display_value` | — |
| `valuation_usd` | String, currency amount | **Premium** |
| `source_url` | String | — |

`amount_usd` and `valuation_usd` are omitted from the response object for a caller holding only `x_bst_startuptrk.user`.

`participating_investors` is emitted as a **JSON array of investor references assembled from `x_bst_startuptrk_m2m_round_investor`**, one array element per linked investor, de-duplicated. An empty array means the round has no participating investors recorded. The array is not a writable field: participating investors are maintained as rows of the join table, and the join table is authoritative for them.

The join table is read through the secured path **once per page, not once per round**. The list operation collects the identifiers of the rounds on the page, calls `InvestorPortfolioService.participantsForRounds()` with all of them, and receives a map from round identifier to participant array; the read-one operation calls the same method with a single identifier. That method issues one query per batch of at most 200 rounds, so a 50-record page costs one join-table query.

`lead_investor` is a **separate single reference** on the funding round and is not a member of `participating_investors`. The same investor may be both the lead investor of a round and a participating investor in it, in which case it appears in `lead_investor` and as an element of `participating_investors`.

A worked single funding-round response, read by a caller who can read the premium fields:

```json
{
  "sys_id": "c71a8be402f94d6cbb35e9147d0a6f28",
  "startup": {
    "value": "3d5e9c1b7a2f4e08b6c14d0392fa5e77",
    "display_value": "Beacon Hill Robotics"
  },
  "round_type": "Series B",
  "amount_usd": "32000000",
  "round_date": "2024-06-18",
  "lead_investor": {
    "value": "5a9d3c07be124f88a4e6021d7fc3b590",
    "display_value": "Charles River Ventures Fund IV"
  },
  "participating_investors": [
    {
      "value": "e2470b5d9c8a41f6ab13d5028e6f7c41",
      "display_value": "Back Bay Angels"
    },
    {
      "value": "7fb1c604a95d42e39c08b7213de5a06f",
      "display_value": "Harbor Growth Partners"
    }
  ],
  "valuation_usd": "185000000",
  "source_url": "https://news.example.org/beacon-hill-robotics-series-b"
}
```

### `/jobs`

The JobPosting resource over `x_bst_startuptrk_jobposting`. Five operations.

| Method | Path template | Description | Success status |
| --- | --- | --- | --- |
| `GET` | `/jobs` | Lists job postings. Returns the paginated envelope carrying a page of job-posting objects, `total_count`, `limit` and `offset`. | `200` |
| `GET` | `/jobs/{id}` | Reads one job posting by `sys_id`. Returns a single job-posting object. | `200` |
| `POST` | `/jobs` | Creates a job posting from the request body. Returns the created job-posting object. | `201` |
| `PUT` | `/jobs/{id}` | Updates the named job posting with the supplied fields. Returns the updated job-posting object. | `200` |
| `DELETE` | `/jobs/{id}` | Deletes the named job posting. Returns no body. | `204` |

`GET /jobs` accepts two query filters in addition to the pagination parameters. Results are ordered by `posted_date` descending, then by `sys_id`.

| Filter | Column matched | Comparison | Accepted form |
| --- | --- | --- | --- |
| `startup` | `startup` | Exact match against a startup `sys_id` | 32 hexadecimal characters, per [Query values](#query-values) |
| `department` | `department` | Exact match against a choice value | A member of `JobPosting.department` |

Representation. Nine fields plus `sys_id`. **No field on this resource is premium-gated**, so every field is readable by all three roles.

| Field | Type | Premium-gated |
| --- | --- | --- |
| `sys_id` | String | — |
| `startup` | Reference object carrying `value` and `display_value` | — |
| `title` | String | — |
| `department` | String, choice value | — |
| `location` | String | — |
| `remote_type` | String, choice value | — |
| `seniority` | String, choice value | — |
| `posted_date` | String, date | — |
| `url` | String | — |
| `active` | Boolean | — |

`active` on this resource is the job posting's own column and is unrelated to the startup's `active` column and to the startup inclusion criteria.

### `/news`

The NewsArticle resource over `x_bst_startuptrk_newsarticle`. Five operations.

| Method | Path template | Description | Success status |
| --- | --- | --- | --- |
| `GET` | `/news` | Lists news articles. Returns the paginated envelope carrying a page of news-article objects, `total_count`, `limit` and `offset`. | `200` |
| `GET` | `/news/{id}` | Reads one news article by `sys_id`. Returns a single news-article object. | `200` |
| `POST` | `/news` | Creates a news article from the request body. Returns the created news-article object. | `201` |
| `PUT` | `/news/{id}` | Updates the named news article with the supplied fields. Returns the updated news-article object. | `200` |
| `DELETE` | `/news/{id}` | Deletes the named news article. Returns no body. | `204` |

Writes to this resource are **manual entry or CSV import only**. There is no automated NewsArticle ingestion: neither ingestion flow writes `x_bst_startuptrk_newsarticle`, and the fallback dataset carries no NewsArticle file. Records reach the table through the platform form, through this resource's `POST` and `PUT` operations, or through an ad hoc import. The exclusion is stated here and is to be recorded again in [`./gaps-and-flags.md` (planned)](./gaps-and-flags.md).

`GET /news` accepts two query filters in addition to the pagination parameters. Results are ordered by `published_date` descending, then by `sys_id`.

| Filter | Column matched | Comparison | Accepted form |
| --- | --- | --- | --- |
| `startup` | `startup` | Exact match against a startup `sys_id` | 32 hexadecimal characters, per [Query values](#query-values) |
| `source` | `source` | Case-insensitive contains | Free text, per [Query values](#query-values) |

Representation. Six fields plus `sys_id`. No field on this resource is premium-gated.

| Field | Type | Premium-gated |
| --- | --- | --- |
| `sys_id` | String | — |
| `startup` | Reference object carrying `value` and `display_value` | — |
| `title` | String | — |
| `source` | String | — |
| `url` | String | — |
| `published_date` | String, date | — |
| `summary` | String | — |

### Operation roll-up

| # | Resource | Operations | Running total |
| --- | --- | --- | --- |
| 1 | `/startups` | 5 | 5 |
| 2 | `/founders` | 6 | 11 |
| 3 | `/investors` | 5 | 16 |
| 4 | `/funding-rounds` | 5 | 21 |
| 5 | `/jobs` | 5 | 26 |
| 6 | `/news` | 5 | 31 |
| | **Total** | **31** | **31** |

5 + 6 + 5 + 5 + 5 + 5 = 31.

Six logical resources, 31 operations, one `sys_ws_definition`. `/founders` carries six operations rather than five because the nested sub-resource `GET /founders/{startup_id}/executives` is counted inside it; that is the one operation of the 31 that is not a plain CRUD operation on a top-level resource. Executive has no top-level resource of its own.

By method: 13 `GET` operations — seven list operations and six read-one operations — 6 `POST`, 6 `PUT` and 6 `DELETE`. 13 + 6 + 6 + 6 = 31.

This roll-up is the operation-count evidence that criterion 3 in [`./validation-checklist.md` (planned)](./validation-checklist.md) and the API section of [`../../docs/decisions/TRACEABILITY_MATRIX.md` (planned)](../../docs/decisions/TRACEABILITY_MATRIX.md) are each to resolve against.

## Field validation

Every value in a create or update body is validated **before any write is attempted**, by `RestQueryHelper.validateBody()`. Each of the 12 body-bearing operations declares a specification listing, for each writable field, its validation type, its declared length, whether it is mandatory on create, and — for a choice or a reference — its choice list or target table. Validation is not a formality applied to some fields: a body member that names no field in the specification is ignored, a body naming no writable field at all is a `400`, and **no field is written on a type the specification does not declare**. The `_coerce` step has no permissive default; an unrecognised type answers `<field> has an unsupported type` rather than storing the value.

Every value is first passed through the same normalisation: it is coerced to a string, trimmed, and stripped of control characters, zero-width characters, bidirectional overrides and a byte-order mark — the character class `\u0000-\u001f`, `\u007f`, `\u200b-\u200f`, `\u202a-\u202e`, `\u2028`, `\u2029`, `\ufeff`. Those characters are removed rather than refused, so a value cannot smuggle an invisible direction override or line separator into stored data and cannot use one to defeat the pattern checks below. A value that normalises to empty is treated as absent.

### Validation types

| Type | Rule | Refusal message on a value that fails |
| --- | --- | --- |
| `string` | Length after trimming must not exceed the column's declared maximum. | `<field> exceeds <n> characters` |
| `url` | Length must not exceed **255**, and the value must match the absolute-`https` allowlist below. | `<field> exceeds 255 characters`, then `<field> must be an absolute https URL` |
| `email` | Length must not exceed **254**, and the value must match the email allowlist below. | `<field> exceeds 254 characters`, then `<field> must be an email address` |
| `date` | Must be `yyyy-MM-dd` in shape **and** must name a day that exists in the calendar. | `<field> must be a yyyy-MM-dd date`, then `<field> must be a date that exists in the calendar` |
| `integer` | Optionally signed whole number. | `<field> must be a whole number` |
| `currency` | A decimal amount. | `<field> must be an amount` |
| `boolean` | JSON `true`/`false`, or the strings `true`, `false`, `1`, `0`. | `<field> must be true or false` |
| `choice` | Must be a member of the column's choice list, matched case-insensitively; the stored value is the canonical member, not the supplied casing. | `<field> must be one of <choice list>` |
| `multichoice` | Every comma-separated token must be a member of the column's choice list. | `<field> must contain only <choice list>` |
| `reference` | Must be 32 lower-case hexadecimal characters **and** must name a record the caller can read, tested through `GlideRecordSecure`. | `<field> must be a 32 character sys_id`, then `<field> does not name a readable record` |

The reference-failure message is deliberately generic. The physical table the reference was tested against is **not** disclosed to the caller; it is written to the application log through `gs.info`, tagged `[x_bst_startuptrk.RestQueryHelper]`, together with the supplied identifier and the field name. A caller cannot use a sequence of failed writes to enumerate the schema, and an operator retains the detail needed to diagnose one.

### URL fields — absolute `https` only

A `url` value must match, in full:

- Scheme `https://`, matched case-insensitively. **`http`, `ftp`, `file`, `data`, `javascript` and every other scheme is refused**, as is a scheme-relative `//host/path` and a bare `host/path`.
- A host of at least two dot-separated labels, each label starting and ending with a letter or digit and containing only letters, digits and hyphens. A single-label host such as `localhost`, a label with a leading or trailing hyphen, and an empty label are all refused.
- An optional port of one to five digits.
- An optional path, query and fragment drawn only from the RFC 3986 character set `A-Z a-z 0-9 - . _ ~ % ! $ & ( ) * + , ; = : @ / ? # [ ]`.

The allowlist is what makes the field safe for a consumer to render as a link target. The permitted set contains **no `<`, no `>`, no single or double quote, no backtick, no whitespace, no backslash and no brace**, so a stored URL cannot close an HTML attribute or open a tag, and the scheme restriction means it cannot carry `javascript:` or `data:`. This is an input-boundary reduction, not a substitute for output encoding — see [Content type](#content-type).

### Email fields — allowlisted local part and host

An `email` value must be a local part of 1 to 64 characters drawn from `A-Z a-z 0-9 . _ % + -`, an `@`, then a host of at least two dot-separated labels under the same label grammar as a URL host. Quoted local parts, address comments, display names and angle brackets are refused. As with a URL, the permitted set carries no character with HTML or script significance.

### Date fields — the day must exist

A `date` value passes a shape check and then a **calendar** check. The year must be between `1900` and `2999`, the month between `1` and `12`, and the day between `1` and the number of days that month actually has, with February resolved by the full Gregorian leap rule — divisible by 400 is a leap year, otherwise divisible by 100 is not, otherwise divisible by 4 is. `2026-13-45`, `2026-02-30`, `2027-02-29`, `2026-04-31` and `2026-00-10` are all refused; `2024-02-29` and `2000-02-29` are accepted. A shape-only check would store an impossible date that the platform then reads back as something else, so the two checks are separate and both apply.

### Which fields carry which type

The structured types apply as follows. Every other writable field is a `string`, `choice`, `multichoice`, `integer`, `currency`, `boolean` or `reference` as tabulated on its resource above.

| Type | Resource and field | Operations |
| --- | --- | --- |
| `url` | `/startups` — `website`, `logo_url` | `POST`, `PUT` |
| `url` | `/founders` — `linkedin_url` | `POST`, `PUT` |
| `url` | `/investors` — `website` | `POST`, `PUT` |
| `url` | `/funding-rounds` — `source_url` | `POST`, `PUT` |
| `url` | `/jobs` — `url` | `POST`, `PUT` |
| `url` | `/news` — `url` | `POST`, `PUT` |
| `email` | `/founders` — `contact_email` | `POST`, `PUT` |
| `date` | `/funding-rounds` — `round_date` | `POST`, `PUT` |
| `date` | `/jobs` — `posted_date` | `POST`, `PUT` |
| `date` | `/news` — `published_date` | `POST`, `PUT` |

That is 14 `url` specifications, 2 `email` and 6 `date` across the 12 body-bearing operations. `x_bst_startuptrk_executive.contact_email` carries no entry because Executive has no create or update operation — it is served only by the nested read sub-resource — so the only route that writes an executive is an ingestion flow or the platform form, both of which validate through the dictionary rather than through this API.

Filter parameters on the list operations are validated separately and by different rules, because they are matched rather than stored; those rules are under [Filter parameter validation](#filter-parameter-validation).

## Error contracts

**Every error body this API produces is one of exactly two JSON shapes** — the rate-limit shape and the general-failure shape. Both are fixed by the requirements and are reproduced below exactly; a client may parse them literally. The only status without a body is `204`.

Every status code this API returns, in one place:

| Status | Meaning | Body |
| --- | --- | --- |
| `200` | A successful list, read or update. | The paginated envelope, or the serialised record object. |
| `201` | A successful create. | The serialised record object, read back through the secured path. |
| `204` | A successful delete. | None. |
| `400` | A path or filter parameter is malformed, `sysparm_offset` exceeds the page-depth ceiling, the body is absent or not JSON, a create or update failed field validation, or a create, update or delete was refused by the platform. | `{"error": "<message>"}` |
| `403` | The caller is authenticated but is not authorised to run the operation. Produced on two independent paths: by the platform, when a bound `REST_Endpoint` access control denies the call before the operation script runs; and by the operation script itself, when the shared in-script role guard refuses. | Platform-supplied on the first path. On the second, `{"error": "Caller holds no Boston Startup Tracker role"}` for the 13 reads and `{"error": "Caller holds no Boston Startup Tracker administrator role"}` for the 18 mutations. |
| `404` | The record named by the path parameter does not exist or is not readable by the caller. | `{"error": "<message>"}` |
| `415` | A body-bearing operation was called with a `Content-Type` that is not `application/json`, or with no `Content-Type` header at all. | `{"error": "Request body must be application/json"}` |
| `429` | The caller has exhausted its request budget for the current window, **or** the request could not be accounted for. | `{"error": "rate_limit_exceeded", "retry_after": 42}` |
| `500` | An unhandled error occurred inside the operation script. | `{"error": "<message>"}` |

The order in which an operation applies its checks is fixed and identical across all 31, because it determines which status a request that fails more than one check receives: the rate limiter first, then the in-script role guard, then — on a body-bearing operation — the media-type guard, then parameter and body validation, then the record access. A caller over budget therefore reads `429` rather than `415`, and an unauthorised caller reads `403` rather than a validation `400`, so no error message reveals anything to a caller not entitled to reach that stage.

### Rate limit — HTTP 429

Body:

```json
{"error": "rate_limit_exceeded", "retry_after": 42}
```

`retry_after` is a whole number of seconds, computed as the window start plus the window length minus the current time. `42` above is an illustrative value; the value returned is the seconds remaining in the caller's current window, with a floor of `1`.

Mechanism. Per-caller fixed-window accounting in the table `x_bst_startuptrk_rate_limit_counter`, maintained by the `RateLimitService` Script Include. `RateLimitService` resolves the current window, records the request against it, and rejects the request once the count exceeds the configured budget. Both properties are validated before use: a value that is not a positive whole number falls back to `100` requests and a `60` second window.

**One counter row per caller, per resource, per window — enforced by the database, not by convention.** The counter table carries a `window_key` column that is mandatory and **declared unique**, holding the composite `<caller sys_id>|<api resource>|<window start as whole seconds since the epoch>`, truncated at 200 characters. Windows are aligned buckets, so the third component is `epoch - (epoch % window_seconds)` and every request inside one window derives the identical key. A unique column is what makes the one-row-per-tuple statement true: without it two requests arriving together each find no row and each insert one, and the two counts then diverge unnoticed.

The accounting write is applied as follows, and each step exists to close a specific race:

| Step | Behaviour | Race it closes |
| --- | --- | --- |
| Query by `window_key` | Reads **every** row carrying the key, sums all their counts for the decision, and holds the lowest-`sys_id` row as the one to increment. Two or more rows for one key are logged at `error` with the row count. | Duplicate rows left by a pre-existing window or a lost race are counted rather than ignored, so a duplicate can never be used to double a budget. |
| Insert, when no row exists | Inserts with count `1`. **A rejected insert is treated as a lost race, not a failure** — a concurrent request won the unique key — and the attempt is retried against the row that request created. | Two callers inserting the same window simultaneously. |
| Increment, when a row exists | A **checked update**: the row is re-queried on `sys_id` **and** on `request_count` still equal to the value this request observed. A missed match means another request incremented in between, and the attempt is retried. | A read-modify-write that would otherwise overwrite a concurrent increment and lose a count. |
| Retry bound | At most **three** attempts. A retry is taken only when the outcome says a retry can resolve it. | An unbounded retry loop under sustained contention. |

**The policy on an unaccountable request is fail-closed.** If, after three attempts, the counted write did not persist, the failure is written to the application log at `error`, tagged `[x_bst_startuptrk.RateLimitService]`, naming the window key and the attempt count — and **the request is refused with the `429` body above**. It is not admitted. A request whose accounting cannot be persisted is exactly the request an attacker would try to manufacture in volume, so admitting it would make the limit optional; refusing it makes a counter-table outage a denial of service against the API rather than a bypass of its limit. The trade-off is deliberate and is recorded in [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md).

**Platform backstop.** Because this accounting is application-level, an operator may additionally configure a platform inbound rate-limit rule in `sys_rate_limit_rules` against this API as a hard ceiling beneath the application limit. That table is Global scope, so it **cannot be shipped in this scoped Update Set** and is not part of the deliverable; it is an instance-side hardening step. It is optional and does not alter the contract: the platform's own `429` carries a platform-controlled body, which is why the application limit — and not the platform rule — is what the `429` shape above and the criterion 3 test assert against.

| Property | Shipped value | Role |
| --- | --- | --- |
| `x_bst_startuptrk.rest.rate_limit_requests` | `100` | Requests permitted per caller, per resource, per window. |
| `x_bst_startuptrk.rest.rate_limit_window_seconds` | `60` | Window length in seconds. |

Changing either property changes the limit with no code change. The scheduled job **Prune rate limit counters** runs hourly and deletes counter rows whose `window_start` is older than one configured window length — that is, every row whose window has certainly closed — so the table does not accumulate. It also deletes, **regardless of age**, any row carrying no `window_key` — a row that predates the column or that a direct data load created — because the accounting query matches on `window_key` alone, so such a row can never be found, incremented or counted and serves no purpose. Its total is the sum of both sweeps. It counts only the deletions that actually succeeded and logs any row it could not remove. The same property governs the window length, the `retry_after` computation and the pruning cutoff, so one value controls all three.

A standard `Retry-After` response header carries the same value as the body's `retry_after` member. The header is additive: it **does not alter the body**, which remains exactly the two members above.

The limit applies to **every one of the six resources**, and to the nested executives sub-resource. Each of the 31 operations calls `RateLimitService` first, **inside** its own `try` block, before it does any other work. Placing the limiter inside the error-handling boundary is what guarantees that a counter-table, configuration or limiter runtime failure produces the controlled `500` body below rather than escaping the operation. Accounting is keyed on the resource, so a caller's budget for `/startups` is separate from its budget for `/investors`.

### General failure

Body:

```json
{"error": "<message>"}
```

`<message>` is a human-readable string. The table below is the **complete set** of conditions that produce this body: every `<message>` an operation script can produce appears in it, with its status code, and the **Emitted by** column names exactly which of the 31 operations produce it.

| Condition | Status | `<message>` |
| --- | --- | --- |
| The record named by `{id}` does not exist, or is not readable by the caller | `404` | `Record not found` |
| A path or filter parameter that must be a record identifier is malformed | `400` | `<parameter> must be a 32 character sys_id` |
| A filter parameter that must be a choice value is not a member of the list | `400` | `<parameter> must be one of <choice list>` |
| `sysparm_offset` exceeds the page-depth ceiling | `400` | `sysparm_offset must not exceed 10000` |
| A create or update request declares a `Content-Type` that is not `application/json`, or declares none | `415` | `Request body must be application/json` |
| A create or update request carries no body | `400` | `Request body is required` |
| A create or update request body cannot be read as JSON | `400` | `Request body is required and must be JSON` |
| A request body carries no field the resource accepts. On a create this is reached only when every mandatory field is present and no other writable field is supplied, because an absent mandatory field is reported first. | `400` | `Request body carries no writable field` |
| A create request omits a mandatory field, or supplies it blank | `400` | `<field> is required` |
| A supplied value is not a member of its column's choice list | `400` | `<field> must be one of <choice list>` |
| A supplied multi-choice value contains a non-member token | `400` | `<field> must contain only <choice list>` |
| A supplied string exceeds the column's declared length | `400` | `<field> exceeds <n> characters` |
| A supplied integer is not a whole number | `400` | `<field> must be a whole number` |
| A supplied currency value is not an amount | `400` | `<field> must be an amount` |
| A supplied date is not `yyyy-MM-dd` | `400` | `<field> must be a yyyy-MM-dd date` |
| A supplied date is well shaped but names a day that does not exist | `400` | `<field> must be a date that exists in the calendar` |
| A supplied URL is not an absolute `https` URL drawn from the allowlisted character set | `400` | `<field> must be an absolute https URL` |
| A supplied email address fails the allowlist | `400` | `<field> must be an email address` |
| A supplied boolean is not `true`, `false`, `1` or `0` | `400` | `<field> must be true or false` |
| A supplied reference is not a 32-character identifier | `400` | `<field> must be a 32 character sys_id` |
| A supplied reference names no record the caller can read. **The physical table is deliberately not named** — it is logged server-side instead, so a caller cannot enumerate the schema by probing | `400` | `<field> does not name a readable record` |
| A field specification declares a type the validator does not implement — unreachable in the delivered specifications, and present so an unvalidated value can never be stored | `400` | `<field> has an unsupported type` |
| The platform refused the insert | `400` | `Record could not be created` |
| The platform refused the update, for example because a business rule aborted it | `400` | `Record could not be updated` |
| The platform refused the delete | `400` | `Record could not be deleted` |
| The nested executives sub-resource is called without `{startup_id}` | `400` | `startup_id is required` |
| A bound `REST_Endpoint` access control denies the call before the operation script runs | `403` | Supplied by the platform |
| The in-script role guard refuses a read from a caller holding none of the three application roles | `403` | `Caller holds no Boston Startup Tracker role` |
| The in-script role guard refuses a create, update or delete from a caller without the application administrator role | `403` | `Caller holds no Boston Startup Tracker administrator role` |

The normalisation and mandatory-rejection guarantees described in [`./data-model.md`](./data-model.md) and [`../sample-data/README.md`](../sample-data/README.md) belong to `IngestionMapper`, which is on the ingestion path only. **No REST operation calls `IngestionMapper`**, so a create or update through this API is not trimmed, not deduplicated and not choice-normalised by the mapper. What a create or update *is* subject to is `RestQueryHelper.validateBody()`, whose per-field rules are the `400` rows above, and the secured record's own field-level write control: `GlideRecordSecure` is the write path in every create and update operation, so a column the caller may not write is not written.

**A refused write is never reported as a success.** Each create checks the insert result, each update checks the update result, and each delete checks the delete result; a `2xx` on any of the 18 write operations — six creates, six updates and six deletes — means the write reached the database. A create and an update both serialise the record **re-read through the secured path after the write**, not the in-memory copy, so the response body is what was committed. A create whose record is committed but not readable by the caller answers `201` with a body carrying `sys_id` alone.

Mandatory columns that carry a dictionary default — `x_bst_startuptrk_startup.active` and `x_bst_startuptrk_jobposting.active` — are not demanded on create, because the default applies. Supplying either of them **blank** is still a `400`.

An authorisation denial at the record level and an absent record are both reported as `404` by the operation script, because a record the caller may not read is not returned by the secured read path. A denial of the **operation** is reported as `403` — by the platform before the operation script runs when a bound endpoint access control denies it, and by the in-script role guard within the first few lines of the script otherwise. A field-level denial is not an error at all: the field's key is omitted from an otherwise successful response.

### Server error — HTTP 500

Body, the same shape as a general failure:

```json
{"error": "<message>"}
```

`<message>` is a **stable public string carrying a correlation identifier**, of the form:

```text
Internal server error (error_id 3f9a1c04b7de)
```

The caught error's own message, and its **stack trace**, are written to the application log through `gs.error`, tagged `[x_bst_startuptrk.RestResponseBuilder]`, against the same `error_id`. Neither reaches the caller. No trace, no script name, no line number, no table name, no field name and no query fragment appears in the response, so a failing request cannot be used to enumerate the schema; an operator correlates the response to the log line by its `error_id`.

This shape is produced by `RestResponseBuilder.serverError()`, and `error_id` is a twelve-character hexadecimal value from `RestResponseBuilder.errorId()`.

### Uniformity

Every one of the 31 operations wraps its body in error handling that delegates to `RestResponseBuilder` for the 500 shape and to `RateLimitService` for the 429 shape. No operation constructs either body itself, so the contract cannot drift between operations: a change to either shape is a change to one Script Include method.

Every other body is likewise produced by exactly one method, so no status shape can drift between operations:

| Status | Sole producer |
| --- | --- |
| `400` | `RestResponseBuilder.badRequest()` |
| `403` from the in-script guard | `RestResponseBuilder.forbidden()`, reached only through `rejectUnauthorisedRead()` and `rejectUnauthorisedWrite()` |
| `404` | `RestResponseBuilder.notFound()` |
| `415` | `RestResponseBuilder.unsupportedMediaType()`, reached only through `rejectNonJsonBody()` |
| `429` | `RateLimitService.body()`, reached only through `RateLimitService.reject()` |
| `500` | `RestResponseBuilder.serverError()` |
| The list envelope | `RestResponseBuilder.page()` |

How the 429 is made deterministic under test — by pre-seeding a counter row already at the configured budget, so the next single call trips the limit — is to be specified step by step in [`./manual-build/05-atf-test-suites.md` (planned)](./manual-build/05-atf-test-suites.md), and the pass condition for the six per-resource REST tests is to be criterion 3 of [`./validation-checklist.md` (planned)](./validation-checklist.md). Neither document restates the contract above.

## The Script Include call graph

Nine `sys_script_include` records carry the application's service layer. This table is the **rename-impact list**: read a row's third column to find every call site a rename touches.

| Class | Responsibility and public methods | Called by |
| --- | --- | --- |
| `StartupSearchService` | Builds one inclusion-criteria and filter query plan and applies it through the platform condition API. Exposes `readFilters()`, `buildPlan()`, `applyPlan()`, `search()` and `appliesInclusion()`. | The `GET /startups` list operation, and the portal search widgets on the Home/Search route. One class serves both surfaces, so the filter cannot drift between them. |
| `InvestorPortfolioService` | The `portfolio_count` derivation and its stored maintenance, plus a recalculate-all method. Exposes `countPortfolio()`, `recalculate()`, `recalculateMany()` and `recalculateAll()`. | The two portfolio-count business rules — one on `x_bst_startuptrk_fundinground`, one on `x_bst_startuptrk_m2m_round_investor` — and any background script run after a bulk load. |
| `IngestionMapper` | The four cleaning rules, live and fallback source mapping, reference resolution and the batch upsert. Its entry points are `ingest()` and `ingestStaging()`; it also exposes `useLogger()`, `log()`, `trimStrings()`, `applyDefaults()`, `normaliseChoice()`, `normaliseChoices()`, `startupKey()`, `findExistingStartup()`, `dedupeBatch()`, `missingMandatory()`, `clean()`, `mapStagingRow()`, `mapLiveRecord()`, `unwrapLive()`, `resolveReferences()`, `resolveStartup()`, `resolveInvestor()`, `resolveParticipants()`, `upsert()`, `linkParticipants()`, `prepareOne()`, `mapRow()`, `expandRows()` and `writeStagingState()`. | Both ingestion flows, the Crunchbase flow and the LinkedIn flow. |
| `IngestionLogger` | Structured run-scoped events for the flow execution log, implementing skip-the-record-and-continue-the-run, plus the run summary and the provenance write. **Every identifier and detail it writes is an opaque reference or a run-salted fingerprint**, never an external name, email address, biography or URL. Exposes `reset()`, `useRun()`, `drainEvents()`, `getEvents()`, `counters()`, `fingerprint()`, `reference()`, `info()`, `warn()`, `skipRecord()`, `rejectRecord()`, `duplicateRecord()`, `unmatchedChoice()`, `countProcessed()` and `writeRunSummary()`. | Both ingestion flows, which inject their own instance into `IngestionMapper.useLogger()` so mapper and flow share one set of counters, and whose Log step writes `drainEvents()` to the flow execution log. |
| `RateLimitService` | Per-caller accounting against `x_bst_startuptrk_rate_limit_counter` under a unique composite window key, with checked counter writes, bounded retry, duplicate coalescing and a fail-closed persistence policy, plus construction of the 429 body with the computed `retry_after`. Exposes `windowKey()`, `consume()`, `retryAfter()`, `body()`, `reject()` and `prune()`. | All 31 REST operations, and the **Prune rate limit counters** scheduled job. |
| `RestResponseBuilder` | The pagination envelope carrying `total_count`, the per-field read gate that omits denied keys, the **secured** bounded count, the in-script role guard, the JSON media-type guard, and the 400, 403, 404, 415 and 500 bodies. Exposes `serialize()`, `canRead()`, `valueOf()`, `page()`, `countState()`, `countWith()`, `hasAnyAppRole()`, `forbidden()`, `rejectUnauthorisedRead()`, `rejectUnauthorisedWrite()`, `bodyMediaType()`, `unsupportedMediaType()`, `rejectNonJsonBody()`, `notFound()`, `badRequest()`, `serverError()` and `errorId()`. | All 31 REST operations, and every widget server script. |
| `RestQueryHelper` | Parses, bounds and validates request parameters, path identifiers and create and update body values, including the page-depth ceiling, the `https`-only URL allowlist, the email allowlist and real calendar-date checking. Exposes `getLimit()`, `getOffset()`, `getTextParam()`, `getSysIdParam()`, `getChoiceParam()`, `getPathSysId()`, `isCalendarDate()`, `isSysId()`, `validateBody()` and `referenceExists()`. | **All 31 REST operations construct one.** The seven list operations use it for pagination and filter parameters; the 19 operations that carry a path identifier — the 18 `{id}` operations plus the nested executives sub-resource — use it to validate that identifier; the 12 create and update operations use it to validate the request body. The three counts overlap: each `PUT` is in both the second group and the third. |
| `PrivacyRetentionService` | The staging-table privacy lifecycle: age-bounded pruning, raw-payload and person-field minimisation of rows that have already been processed, and data-subject erasure across the entity tables, the staging table and the rate-limit counters. Exposes `minimiseStaging()`, `pruneStaging()`, `runRetention()` and `eraseSubject()`. | The **Prune ingestion staging rows** scheduled job, which calls `runRetention()`; and an administrator background script, which calls `eraseSubject()` to service an erasure request. No REST operation and no widget calls it. |
| `AppProperties` | Typed accessors for all thirteen system properties, including the ingestion cadence clamp and the two retention bounds. Exposes `get()`, `getInt()`, `getBounded()`, `getCadenceHours()`, `getSourceMode()`, `getLastRunProvenance()`, `setLastRunProvenance()`, `getDefaultLimit()`, `getMaxLimit()`, `getRateLimitRequests()`, `getRateLimitWindowSeconds()`, `getInclusionLocationTokens()`, `getCrunchbaseBaseUrl()`, `getLinkedinBaseUrl()`, `getStagingRetentionDays()`, `getStagingMinimiseHours()` and `getLoggingLevel()`. | Every component of the application — the REST operations by way of `RestQueryHelper` and `RateLimitService`, `StartupSearchService`, `IngestionLogger`, `PrivacyRetentionService`, both flows and both scheduled jobs. Nothing reads a property ad hoc. |

Each class also carries private helpers prefixed with an underscore. Those are implementation detail and no call site outside the class may use them.

### Addressing convention

A Script Include is referenced as `x_bst_startuptrk.<ClassName>` from outside the scope and by its bare class name within it. Inside the application — in an operation script, a business rule, a flow script step or a widget server script — the call is `new RestResponseBuilder()`. From outside the scope it is `new x_bst_startuptrk.RestResponseBuilder()`. Each record's `api_name` is the qualified form.

### Privilege

**None of the nine is client-callable, and none runs with elevated privilege.** Every record carries `client_callable` false and `package_private` access. No class may be reached from a client script, and no class may read a premium-gated column through an unsecured path and return it to a caller.

Four of the nine do read through the unsecured `GlideRecord`, because their work is not performed on a caller's behalf: `RateLimitService` maintains counter rows the caller must never see, `InvestorPortfolioService` derives a stored aggregate from rows outside any request, `IngestionMapper` writes ingested records under the flow's own identity, and `PrivacyRetentionService` prunes and erases rows an ordinary caller cannot reach. **None of the four returns a record or a field value to a REST response or a widget.** Which classes may use which read path, and why, is tabulated in [`./access-control.md`](./access-control.md).

### Rename impact

Renaming any class in the table above requires updating every call site listed in its **Called by** column. Because the Automated Test Framework suites encode class names and resource paths, the rename must also propagate into the suite steps that [`./manual-build/05-atf-test-suites.md` (planned)](./manual-build/05-atf-test-suites.md) is to specify.

## System properties

Thirteen `sys_properties` records externalise the application's configuration. All keys are fully qualified with the `x_bst_startuptrk.` prefix.

| Key | Type | Shipped value | Read by |
| --- | --- | --- | --- |
| `x_bst_startuptrk.ingestion.cadence_hours` | Integer | `24` | `AppProperties`, which clamps the value to the range 6 to 48; read by the cadence guard that is the first action of both ingestion flows. |
| `x_bst_startuptrk.ingestion.source_mode` | Choice — `live` or `fallback` | `live` | `AppProperties`; read by both ingestion flows to decide whether to attempt the live call or go straight to the staging table. |
| `x_bst_startuptrk.ingestion.last_run_provenance` | String — `live` or `fallback` | **empty** | `AppProperties`; written by `IngestionLogger.writeRunSummary()` at the end of each flow run and read when reporting a run's provenance. It ships **empty**, and a non-empty value therefore means at least one run has completed on this instance. `IngestionLogger` writes it only after validating the value against `live` or `fallback`; anything else is logged as `run_summary_provenance_invalid` and the property is left untouched. |
| `x_bst_startuptrk.rest.default_limit` | Integer | `20` | `AppProperties`; read by `RestQueryHelper.getLimit()` as the fallback page size. A value that is not a whole decimal integer of 1 or more resolves to the shipped `20`. |
| `x_bst_startuptrk.rest.max_limit` | Integer | `50` | `AppProperties`; read by `RestQueryHelper.getLimit()` as the clamp ceiling. A value that is not a whole decimal integer of 1 or more resolves to the shipped `50`. A maximum below the effective default page size is raised to that default, so the ceiling is never below the fallback. |
| `x_bst_startuptrk.rest.rate_limit_requests` | Integer | `100` | `AppProperties`; read by `RateLimitService.consume()` as the per-window budget. A value that is not a whole decimal integer of 1 or more resolves to the shipped `100`. |
| `x_bst_startuptrk.rest.rate_limit_window_seconds` | Integer | `60` | `AppProperties`; read by `RateLimitService` for the window length and the `retry_after` computation, and by the pruning job as its retention. Windows are aligned buckets, so a row whose `window_start` is older than one window length is never the live window; that is the pruning boundary. A value that is not a whole decimal integer of 1 or more resolves to the shipped `60`. |
| `x_bst_startuptrk.privacy.staging_retention_days` | Integer, readable and writable by `x_bst_startuptrk.admin` only | `30` | `AppProperties.getStagingRetentionDays()`, which clamps the value to the range 1 to 365; read by `PrivacyRetentionService.pruneStaging()` as the age after which an ingestion staging row is deleted. |
| `x_bst_startuptrk.privacy.staging_minimise_hours` | Integer, readable and writable by `x_bst_startuptrk.admin` only | `24` | `AppProperties.getStagingMinimiseHours()`, which clamps the value to the range 1 to 8760; read by `PrivacyRetentionService.minimiseStaging()` as the age after which a settled staging row has its raw payload and person columns cleared. |
| `x_bst_startuptrk.inclusion.location_tokens` | String — comma-separated tokens | `Boston,Cambridge, MA` | `AppProperties`; read by `StartupSearchService.buildPlan()`, which turns each token into one `CONTAINS` condition on `headquarters_location`. |
| `x_bst_startuptrk.crunchbase.base_url` | String | `https://api.crunchbase.com/v3.1` | `AppProperties`; read by the Crunchbase ingestion flow's REST step. |
| `x_bst_startuptrk.linkedin.base_url` | String | `https://api.linkedin.com/v2` | `AppProperties`; read by the LinkedIn ingestion flow's REST step. |
| `x_bst_startuptrk.logging.level` | Choice — `debug`, `info`, `warn` or `error` | `info` | `AppProperties.getLoggingLevel()` and `AppProperties.isLogLevelEnabled()`, the single severity gate. `IngestionLogger` routes every system-log write through it and suppresses any write below the configured threshold; an event below the threshold is still buffered for the flow's Log step, so the flow execution log carries every event regardless. `RestResponseBuilder.serverError()` also consults the gate before writing its diagnostics, which are written at `error` and are therefore permitted at every configured level. The skipped, rejected and processed counters, the response statuses and the response bodies are unaffected. A value outside the four choices resolves to `info`. |

The two `privacy.*` properties are the only two of the thirteen whose read and write are restricted to a role: both carry `read_roles` and `write_roles` of `x_bst_startuptrk.admin`, because a retention window is an administrative control and a caller who could read it learns how long person data survives on the instance. The retention lifecycle they drive is specified in [`./data-model.md`](./data-model.md).

**No property holds a secret.** No API key, client identifier, client secret, refresh token or password value is stored in any of the thirteen, and the two base-URL properties are non-secret endpoint configuration. Credentials live only in the two Connection & Credential Aliases, `x_bst_startuptrk.crunchbase_api` and `x_bst_startuptrk.linkedin_oauth`, which are referenced by name and are built on the instance rather than shipped; see [`./manual-build/01-connection-credential-aliases.md`](./manual-build/01-connection-credential-aliases.md).

### Inventory beyond the planned counts

Three inventories in this application are larger than the Agent Action Plan's stated figures. Each addition is listed in full above; this note records the difference so a reader comparing the deliverable to the plan does not read it as an accounting error.

| Inventory | AAP figure | Shipped | The addition |
| --- | --- | --- | --- |
| Script Includes | 8, AAP section 0.4.5 | 9 | `PrivacyRetentionService`, which implements the staging minimisation, age-bounded pruning and data-subject erasure described in [`./data-model.md`](./data-model.md) |
| Scoped system properties | 11, AAP section 0.4.7 | 13 | `x_bst_startuptrk.privacy.staging_retention_days` and `x_bst_startuptrk.privacy.staging_minimise_hours`, the two bounds that service reads |
| Scheduled jobs | 1, AAP section 0.4.2 | 2 | **Prune ingestion staging rows**, which runs that service's two sweeps; the counter-pruning job is unchanged |

All three additions serve the staging-table privacy lifecycle, which exists because `x_bst_startuptrk_ingest_staging` is the only table in the application that holds verbatim upstream payloads and unvalidated personal data. Each is to be recorded in [`../../docs/decisions/DECISION_LOG.md` (planned)](../../docs/decisions/DECISION_LOG.md).

## Legacy provenance

**This section is historical traceability only. It is not a specification of target behaviour, and nothing in it confers authority.** Every element of the contract above — each path, each parameter name, each response member, each status code and each filter — is specified by the prompt and the Agent Action Plan; the preceding sections are the normative statement of it. The legacy Flask tree under `src/backend/routes/` is read-only reference, consulted for one purpose only: to record which target operations have a legacy antecedent and which do not.

What the legacy tree contributed is the **endpoint-inventory spine**: the list of entities that needed a resource. Two shipped property values also match legacy constants, recorded as rows 4 and 5 of the contract-change table below. No legacy path, parameter name, response key, status code or envelope shape is reproduced by any operation.

### Legacy route module to target resource

| Legacy route module | Target resource |
| --- | --- |
| `src/backend/routes/startup.py` | `/startups` |
| `src/backend/routes/investor.py` | `/investors` |
| `src/backend/routes/job.py` | `/jobs` |
| `src/backend/routes/news.py` | `/news` |
| `src/backend/routes/user.py` | **No target resource** — platform identity replaces it |
| `src/backend/routes/auth.py` | **No target resource** — platform authentication replaces it |
| — | `/founders`, including the nested `GET /founders/{startup_id}/executives` — **no legacy route module** |
| — | `/funding-rounds` — **no legacy route module** |

`src/backend/routes/__init__.py` exports exactly six blueprints: `startup_routes`, `investor_routes`, `job_routes`, `news_routes`, `user_routes` and `auth_routes`. **The source tree contains no founder route, no executive route and no funding-round route.** `src/backend/models/founder.py`, `src/backend/models/executive.py` and `src/backend/models/funding_round.py` exist as models with no route module over them. `/founders`, its nested executives sub-resource and `/funding-rounds` are therefore new surface, not a port — 11 of the 31 operations have no legacy counterpart of any kind.

`src/backend/routes/auth.py` served `/login`, `/refresh`, `/logout` and `/change-password` against a custom JWT identity. None of the four has a target operation; authentication is a platform concern, and the authorisation the legacy tree never implemented is now in the access-control records described in [`./access-control.md`](./access-control.md).

### Contract changes

One row per change. Each states the legacy form with its source citation, the target form, and the decision-log pointer.

| # | Legacy form | Target form | Decision log |
| --- | --- | --- | --- |
| 1 | Request parameters `page` and `per_page`, `src/backend/routes/startup.py:L12-L13` | Request parameters `sysparm_limit` and `sysparm_offset` | [`../../docs/decisions/DECISION_LOG.md` (planned)](../../docs/decisions/DECISION_LOG.md) |
| 2 | Response envelope `{'startups', 'total', 'pages', 'page', 'per_page'}`, `src/backend/routes/startup.py:L31-L37` | Response envelope `result` array plus `total_count` plus the `limit` and `offset` echoes | [`../../docs/decisions/DECISION_LOG.md` (planned)](../../docs/decisions/DECISION_LOG.md) |
| 3 | Logical base path `API_BASE_URL = '/api/v1'`, `src/shared/constants.ts:L2` | Physical base path `/api/x_bst_startuptrk/v1/` | [`../../docs/decisions/DECISION_LOG.md` (planned)](../../docs/decisions/DECISION_LOG.md) |
| 4 | Maximum page size `MAX_RESULTS_PER_PAGE = 50`, `src/shared/constants.ts:L5` | Property `x_bst_startuptrk.rest.max_limit`, shipped value `50` — value carried forward | [`../../docs/decisions/DECISION_LOG.md` (planned)](../../docs/decisions/DECISION_LOG.md) |
| 5 | Default page size `DEFAULT_RESULTS_PER_PAGE = 20`, `src/shared/constants.ts:L8` | Property `x_bst_startuptrk.rest.default_limit`, shipped value `20` — value carried forward | [`../../docs/decisions/DECISION_LOG.md` (planned)](../../docs/decisions/DECISION_LOG.md) |
| 6 | Per-record success bodies returning the record dictionary directly, and a `{'message': ...}` body on delete, `src/backend/routes/startup.py:L121` | The serialised record object on read, create and update; **no body** on delete, with `HTTP 204` | [`../../docs/decisions/DECISION_LOG.md` (planned)](../../docs/decisions/DECISION_LOG.md) |

Rows 4 and 5 are the only rows whose target **value** matches its legacy counterpart, and each arrives as a system property rather than as a source constant. Every other row replaces the legacy form outright. Neither row makes the legacy constant authoritative: both shipped values are specified by the Agent Action Plan, and the match is recorded here because it is a fact worth tracing, not because it is a reason.

The legacy tree disagrees with itself about the default page size, recorded here so row 5 is not read as a single unambiguous antecedent: the route hard-codes a `per_page` default of **10** at `src/backend/routes/startup.py:L13`, while the shared constant declares **20** at `src/shared/constants.ts:L8`. The same disagreement holds in `src/backend/routes/investor.py:L13`, `src/backend/routes/job.py:L13`, `src/backend/routes/news.py:L13` and `src/backend/routes/user.py:L13`, each hard-coding 10. The shipped value of `x_bst_startuptrk.rest.default_limit` is **20**, specified by the Agent Action Plan; that it coincides with one of the two legacy values and not the other is an observation, not the basis for it.

### The paths were never served

The legacy application registers all six blueprints **without a URL prefix** at `src/backend/app.py:L28-L43`. Each `register_blueprint` call passes the blueprint alone, and no blueprint declares a `url_prefix` of its own, so the documented `/api/v1/...` endpoint paths were never actually served by the running application. The versioned API surface described in this document is **new capability, not a migrated contract**.

**No legacy API compatibility is maintained and no shim exists.** There is no alias route, no parameter-name translation layer, no envelope adapter and no redirect from the logical base path.

### Filter provenance

The legacy `name` and `industry` filters at `src/backend/routes/startup.py:L20-L22` — a case-insensitive `ilike` match on `name` and an equality match on `industry` — become filters on the `GET /startups` list operation. They are now built by `StartupSearchService` together with the inclusion criteria and the third `location` filter, into the single query plan applied to both the secured result set and the secured count behind `total_count`. The legacy routes interpolated request values straight into an ORM filter with no validation; every target filter value is validated and bound instead, per [Query values](#query-values).

The legacy per-resource query parameters map across as follows. The legacy `startup_id` parameter name becomes `startup` on the target, matching the reference column name.

| Legacy filter | Source | Target filter |
| --- | --- | --- |
| `name` | `src/backend/routes/startup.py:L14` | `name` on `GET /startups` |
| `industry` | `src/backend/routes/startup.py:L15` | `industry` on `GET /startups` |
| `name` | `src/backend/routes/investor.py:L14` | `name` on `GET /investors` |
| `startup_id` | `src/backend/routes/job.py:L14` | `startup` on `GET /jobs` |
| `startup_id` | `src/backend/routes/news.py:L14` | `startup` on `GET /news` |
| — | — | `location` on `GET /startups`, `type` on `GET /investors`, `department` on `GET /jobs`, `source` on `GET /news`, `startup` and `round_type` on `GET /funding-rounds`, `startup` and `name` on `GET /founders` — no legacy counterpart |

This section is the API portion of the bidirectional matrix that [`../../docs/decisions/TRACEABILITY_MATRIX.md` (planned)](../../docs/decisions/TRACEABILITY_MATRIX.md) is to carry.

## Related documents

Delivered with this package:

- [`../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml`](../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml) — the authoritative REST definition, operation, Script Include and property records this document transcribes
- [`./data-model.md`](./data-model.md) — the ten tables field by field, the choice values, the inclusion-criteria predicate and the `portfolio_count` derivation
- [`./access-control.md`](./access-control.md) — the five ACL layers including the two `REST_Endpoint` controls bound here, the three roles, the seven premium fields, the omitted-not-nulled rule, the table access posture and the secured read and count paths this contract depends on
- [`./gaps-and-flags.md`](./gaps-and-flags.md) — requirements with no clean platform equivalent, including the namespace segment in the base path and the exclusion of automated NewsArticle ingestion
- [`./validation-gates.md`](./validation-gates.md) — the machine-checkable post-commit gates run after the Update Set commits
- [`../sample-data/README.md`](../sample-data/README.md) — the fallback dataset and the ingestion-path cleaning guarantees that the create and update operations do **not** apply
- [`../scripts/validate_update_set_xml.py`](../scripts/validate_update_set_xml.py) — the two-level well-formedness validator for the Update Set this document transcribes

Planned artifacts of this package:

- [`./gaps-and-flags.md` (planned)](./gaps-and-flags.md) — to record requirements with no clean platform equivalent, including the namespace segment in the base path and the exclusion of automated NewsArticle ingestion
- [`./validation-checklist.md` (planned)](./validation-checklist.md) — to specify the five success criteria, criterion 3 being the pass condition for the six per-resource REST tests
- [`./manual-build/01-connection-credential-aliases.md` (planned)](./manual-build/01-connection-credential-aliases.md) — to specify how the two Connection & Credential Aliases are built and bound; they are the only home for credential material
- [`./manual-build/05-atf-test-suites.md` (planned)](./manual-build/05-atf-test-suites.md) — to specify the REST resource tests and how the 429 response is made deterministic
- [`../../docs/decisions/DECISION_LOG.md` (planned)](../../docs/decisions/DECISION_LOG.md) — to be the single source of truth for every decision, alternative and risk behind this contract
- [`../../docs/decisions/TRACEABILITY_MATRIX.md` (planned)](../../docs/decisions/TRACEABILITY_MATRIX.md) — to carry the bidirectional source-to-target matrix this section feeds
- [`../../docs/review/CRITICAL_DECISIONS.md` (planned)](../../docs/review/CRITICAL_DECISIONS.md) — to carry the five highest-risk decisions, including the API/Integration reviewer entry
