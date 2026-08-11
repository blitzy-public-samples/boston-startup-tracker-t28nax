# API reference — `x_bst_startuptrk`

This document is the REST contract reference for the ServiceNow scoped application `x_bst_startuptrk`. It states the one Scripted REST API definition, all 31 operations across six logical resources, who may call them and how that is enforced, the JSON-only media-type contract, the pagination contract, the validation applied to every stored field, every status code and error body the API returns, the Script Include call graph that doubles as a rename-impact list, and the eleven system properties the application reads. Every operation is enumerated individually with its method, its path template, what it returns and its success status; every Script Include and every property is likewise listed one by one.

**Authority.** The frozen prompt and the Agent Action Plan are authoritative for all application content, and they govern the Update Set XML and this document alike. The Update Set XML at [`../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml`](../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml) is the implementation of that specification and the transcription source for everything below: the **1** `sys_ws_definition` record, the **31** `sys_ws_operation` records, the **8** `sys_script_include` records and the **11** `sys_properties` records it carries — counts taken from the file itself, where they are the whole of each class. Where this document and those records disagree about a path, a method, a parameter name, a response member, a status code, a class name or a property key, the records are checked against the prompt and the plan first. Where the records match the specification, this document is corrected to them. Where the records depart from it, the records are corrected.

The table names, column names and premium markers used below are the ones established in [`./data-model.md`](./data-model.md). The field-level read gate applied to every response is the one specified in [`./access-control.md`](./access-control.md); this document states where that gate applies and does not restate the access-control scheme.

This document carries no rationale. Every decision behind this contract, every alternative considered and every risk it carries is recorded in [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md), which is to be the single source of truth for "why".

## Referenced documents

This document is self-contained. The definition, all 31 operations, the pagination contract, every request filter, every response representation, all three error contracts, the call graph and the eleven properties are stated here in full; no statement of the contract requires reading another file.

**Every document named below is delivered and readable.** Each link resolves to a file in this package, among them the Update Set XML, `./data-model.md`, `./access-control.md`, `./validation-gates.md` and `../sample-data/README.md`, so a reader can follow any link and read the content the statement around it describes; no link is a forward reference to something still to be written.

**Reviewer.** This document is the artifact validated by the **API/Integration** reviewer entry in [`../../docs/review/CRITICAL_DECISIONS.md`](../../docs/review/CRITICAL_DECISIONS.md), covering the credential handling of the ingestion integration and the contract stated here.

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

**Call the physical path.** Every request goes to `https://<instance>.service-now.com/api/x_bst_startuptrk/v1/<resource>`. The logical form is not served and does not resolve. No consumer may be written against it. The namespace segment is to be flagged again in [`./gaps-and-flags.md`](./gaps-and-flags.md).

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

This is stated explicitly because a Scripted REST API that requires authorisation but names no control does **not** get scoped-role authorisation: evaluation falls back to the platform's default REST control, which denies the external-user role but admits any authenticated internal user. These two controls are what make the role restriction real. Both are confirmed by inspecting the two `sys_security_acl` records of type `REST_Endpoint` in the delivered Update Set; no post-commit gate reads them.

The same rule is also enforced in code, so it does not depend on platform access-control evaluation alone. Every operation script calls a shared guard immediately after the rate limiter:

| Guard | Applied to | Refusal |
| --- | --- | --- |
| `RestResponseBuilder.rejectUnauthorisedRead()` | the 13 read operations | `HTTP 403` with body `{"error": "Caller holds no Boston Startup Tracker role"}` |
| `RestResponseBuilder.rejectUnauthorisedWrite()` | the 18 mutations | `HTTP 403` with body `{"error": "Caller holds no Boston Startup Tracker administrator role"}` |

Four further enforcement rules bind every operation, and they are specified in [`./access-control.md`](./access-control.md):

- **Secured read path.** Every caller-facing read uses `GlideRecordSecure`. No operation reads through the unsecured `GlideRecord`, and no Script Include reads a premium-gated column on a caller's behalf and returns it.
- **Readability-gated counting.** `total_count` is produced by **one aggregate `COUNT` behind a readability gate**, and it is exact. `RestResponseBuilder.countState()` gates on `hasAnyAppRole()` — three sequential `gs.hasRole` checks against the scoped roles — and answers `{ total: 0, denied: true }` when none holds, which the operation turns into a `403` rather than a zero, so a caller who may not read the table learns nothing about its size; having established the role it counts once, over the same conditions the page applies. **The gate is a role test, not a probe read on a secured record**: a probe was the original design and was replaced under `D-267`, because on an empty table, a newly loaded table or a table whose rows the caller's plan filters away it answers exactly as a denial does. An aggregate counts rows rather than readable rows, so the exactness rests on a stated invariant — **all seven entity tables and the join table grant table-level read to all three roles and carry no record-level access control**, so rows matching a query are rows every caller may read, and the roles differ only at field level. The invariant, the rule it generalises to, and the condition under which a future change would invalidate every `total_count` are stated in full under [`total_count` semantics](#total_count-semantics) and in [`./access-control.md`](./access-control.md). The three aggregate paths that legitimately produce a caller-facing value are `RestResponseBuilder.countState()`, `countWith()` and `countByGroup()`; every other aggregate in the application is an internal maintenance or derivation count in `RateLimitService` or `InvestorPortfolioService`, and all are tabulated in [`./access-control.md`](./access-control.md).
- **Per-field read gate.** Response serialisation tests each field with an element-level read check and **omits the key entirely** when the check fails. A denied premium field is absent from the response object; it does not appear with a null, an empty string or a placeholder.
- **No bypass.** None of the eight Script Includes is client-callable and none runs with elevated privilege, so no operation can reach a gated field through an elevated helper.

**There is exactly one read route to application data, and this API is it.** All ten application tables — the seven entity tables and the three supporting tables — are delivered `access` `package_private` with `read_access` and `ws_access` `false`, so `GET /api/now/table/x_bst_startuptrk_startup` returns `HTTP 400` `Invalid table` and a script in another application scope cannot reach a row either. Consumers therefore have one contract to write against, and every control this document describes applies to every caller-facing read without exception.

That matters because a native route would carry none of the five controls above. Field-level read controls omit a premium *value* from a response, but a query predicate on that same column leaks it anyway: a caller who cannot read `total_funding_usd` could still recover it by bisecting `total_funding_usd>N`, and an aggregate over it needs no predicate at all. A native list route would also sit outside `StartupSearchService`'s inclusion plan and outside the fixed-window rate limiter. Sealing the tables is what makes the thirty-one operations below the **whole** of the caller-facing surface rather than one of two surfaces that would have to be kept in agreement. The decision, the alternative and the consequence for the deployment gates are recorded at `D-027` in [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md); the gates themselves read table metadata and exercise the secured path, as [`./validation-gates.md`](./validation-gates.md) specifies.

Two properties of the sealed posture are worth stating so no consumer misreads either:

| Property | Detail |
| --- | --- |
| **The native Table API serves none of the ten** | `ws_access` is `false` on all ten dictionary records. There is no second representation of these resources, no second pagination convention and no second field-omission behaviour to reconcile. |
| **No write reaches any of the ten tables from outside the scope** | `create_access`, `update_access` and `delete_access` are `false` on all ten, so layer 2's administrator-only write grant cannot be circumvented, and the `Boston Startup Tracker API write` endpoint control governs the only route that can write. |
| **The request budget applies to every caller-facing read** | Rate limiting is application-level accounting inside the 31 operation scripts. Because no other route reaches these tables, no read escapes it. An earlier revision left the native route open, and reads over it were never counted; that route is closed and the gap it created is closed with it. |
| **The inclusion filter applies to every caller-facing startup read** | It is a query filter in `StartupSearchService`, not an access control, so it never applied on the native route. With that route closed, the filter and the `total_count` beside it govern every startup list a caller can obtain. |

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

The refusal happens **before the body is read**, so no request body reaches an XML parser through this application. The instance-level parser configuration — `glide.stax.allow_entity_resolution` false and `glide.stax.whitelist_enabled` true — is defence in depth beneath it. Those are Global-scope properties, so the scoped application deliberately does not ship them and no post-commit gate reads them; they are asserted as an **instance prerequisite** before the import, in [`./deployment-runbook.md`](./deployment-runbook.md).

Every response body is `application/json`. The only response without a body is `HTTP 204` on a successful delete.

**Output encoding is the consumer's responsibility.** Response bodies are serialised to JSON by the platform, which escapes the JSON string context correctly. Values are stored as supplied, so any consumer that renders a value into a different context must encode for that context — a Service Portal widget must bind through Angular interpolation, never through raw HTML binding. The API reduces the risk at the input boundary by allowlisting the structured fields: URL fields accept only an absolute `https` URL drawn from the RFC 3986 character set, which cannot contain `<`, `>`, a quote or a backtick, and email fields accept only characters that carry no HTML significance. See [Field validation](#field-validation).

The contract is enforced by the records themselves, not merely by convention. The `sys_ws_definition` record and every one of the 31 `sys_ws_operation` records declare `consumes` and `produces` as `application/json` alone, with `consumes_customized` and `produces_customized` both `true` so the declared value overrides the platform default of `application/json,application/xml,text/xml`. No XML media type is registered anywhere on the API, so a request sending `Accept: application/xml` or `Accept: text/xml` cannot negotiate an XML response body, and a request sending `Content-Type: application/xml` is not accepted. A consumer that requires XML is not supported.

### Deviations from the legacy contract

The contract stated in this document differs from the legacy Flask contract in three respects, and consumers discover the differences here:

1. The **paths** differ. The physical base path is `/api/x_bst_startuptrk/v1/`, not `/api/v1/`.
2. The **pagination parameter names** differ. They are `sysparm_limit` and `sysparm_offset`, not `page` and `per_page`.
3. The **response envelope key** differs. The count member is `total_count`, not `total`.

**No compatibility shim, alias or legacy-contract layer exists.** No operation accepts `page` or `per_page`, no response carries `total`, and no route serves the logical `/api/v1/` form. Every element of this contract — each path, each parameter name, each response member and each status code — is specified by the prompt and the Agent Action Plan. The legacy forms are recorded under [Legacy provenance](#legacy-provenance) as historical antecedents only. Each change is recorded as a row in [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md).

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
| Record identifier — `startup`, and the `{startup_id}` path parameter of the nested sub-resource | Must match 32 hexadecimal characters, accepted in **either** case and bound lowercased, which is the only form stored | `400` with `<parameter> must be a 32 character sys_id` |
| Choice value — `industry`, `type`, `round_type`, `department` | Must be a member of the column's choice list, matched case-insensitively; the **canonical** member is what reaches the query | `400` with `<parameter> must be one of <choice list>` |
| Free text — `name`, `location`, `source` | the value is put into the one stored form by `AppProperties.normaliseText()`, then truncated to 100 characters and bound as a `CONTAINS` operand. That normalisation applies two actions to two disjoint character classes, listed in full in [Two character classes, two actions](#two-character-classes-two-actions): every **zero-width and directional formatting** character is **removed**, every remaining **control** character is **replaced with one space**, and the result is trimmed. The C1 range `U+0080`–`U+009F` is left alone because the characters that could break out of a `CONTAINS` operand or forge a log line — the newline, the carriage return, and the bidirectional overrides and isolates — are all members of one of the two classes, and a C1 byte in a search term is an unmatchable character rather than a hostile one. Because the filter and the write path share that one definition, a filter value carrying an invisible character finds the record whose stored value carried the same one. | Never fails; an unmatchable value simply returns no rows |

`{id}` path parameters on the read-one, update and delete operations are validated the same way as a record-identifier filter, so a malformed identifier answers `400` rather than `404`.

### Bounds

`RestQueryHelper` parses and clamps both parameters. It reads its bounds from two system properties through `AppProperties`:

| Property | Shipped value | Role |
| --- | --- | --- |
| `x_bst_startuptrk.rest.default_limit` | `20` | The page size applied when `sysparm_limit` does not resolve to a usable value. |
| `x_bst_startuptrk.rest.max_limit` | `50` | The largest page size the API will serve. |

**Neither property can widen a page beyond `50`.** Both are read through `AppProperties`, which resolves each to at least `1` and **at most `50`** — the absolute ceiling `PAGE_SIZE_CEILING`, a code constant equal to the value prompt section 3.0 fixes for the maximum page. `RestQueryHelper.getLimit()` applies the same ceiling again where the page is built. A property may therefore **narrow** a page, which is a legitimate tuning move, and may not widen one: setting `x_bst_startuptrk.rest.max_limit` to `9999` resolves to `50`, and setting `x_bst_startuptrk.rest.default_limit` to `9999` resolves to `50` as well, so a request that carries no pagination parameter at all still returns at most fifty records rather than the whole table.

The resolution rules are exact. `max_limit` below means the **resolved** maximum — the property clamped to `1..50`:

| Supplied `sysparm_limit` | Applied limit |
| --- | --- |
| Absent | The resolved `x_bst_startuptrk.rest.default_limit` |
| Non-numeric | The resolved `x_bst_startuptrk.rest.default_limit` |
| `0` or negative | The resolved `x_bst_startuptrk.rest.default_limit` |
| Greater than the resolved `x_bst_startuptrk.rest.max_limit` | Clamped to the resolved `x_bst_startuptrk.rest.max_limit` |
| Between `1` and the resolved `x_bst_startuptrk.rest.max_limit` inclusive | The supplied value |

| Supplied `sysparm_offset` | Applied offset |
| --- | --- |
| Absent | `0` |
| Not a whole number — including a negative value, a decimal, and any value carrying a non-digit character | **Refused** — `400` with `sysparm_offset must be a whole number between 0 and 10000` |
| Between `0` and `10000` inclusive | The supplied value |
| Greater than `10000` | **Refused** — `400` with `sysparm_offset must not exceed 10000` |

**`sysparm_limit` is normalised; `sysparm_offset` is refused.** The two parameters are not symmetric, and the asymmetry is the contract: a limit that cannot be read resolves to the shipped page size — whereas an offset that cannot be read has none, because silently substituting `0` would answer a request for page 40 with page 1 and the caller would have no way to tell. An offset is therefore refused with a `400` in both of its failure modes, and the two messages are distinct so a caller can tell a malformed value from an out-of-range one:

| Failure mode | Exact message |
| --- | --- |
| Not a whole number | `sysparm_offset must be a whole number between 0 and 10000` |
| A whole number above the ceiling | `sysparm_offset must not exceed 10000` |

Those two strings are the whole `sysparm_offset` error vocabulary, they are the strings `RestQueryHelper.getOffset()` returns, and they are repeated verbatim under [General failure](#general-failure).

**The `sysparm_offset` ceiling is `10000`.** The offset is passed to the platform's result-window API, which walks the result set to reach the requested position. The ceiling is a fixed constant in `RestQueryHelper`, not a property, because it is a resource-consumption bound rather than a tuning knob. It is checked before any query is built, so a refused request performs no database work:

```text
HTTP 400
{"error": "sysparm_offset must not exceed 10000"}
```

Clamping to the ceiling instead would silently return the ten-thousandth page for every deeper request, which a consumer paging forward could not distinguish from having reached the end. Refusing makes the boundary visible. A consumer that needs to reach beyond record 10,000 narrows the result set with the resource's filter parameters rather than paging deeper; every list operation carries at least one filter.

All seven list operations apply the ceiling identically, and each checks the parsed result before it builds a query. The applied limit and offset are echoed in the response, so a consumer always reads back what the API actually used.

**Each list operation performs exactly one count, and the windowed query performs none.** The page is positioned with `chooseWindow(offset, offset + limit)`, which by default makes the query report the size of its own unwindowed result set — a second count over the same conditions the aggregate has already counted, on every list request. Every one of the seven windowed queries therefore calls **`setNoCount()`** immediately after `chooseWindow()`, which suppresses that count. The consequence is exact and worth stating:

| Query | Counts | What reads the number |
| --- | --- | --- |
| The `GlideAggregate` `COUNT` behind `total_count` | **Once** | The envelope's `total_count` member. It is exact at any magnitude. |
| The windowed record query | **Never** | Nothing. `setNoCount()` is set, the page's own length is the array length, and the total came from the aggregate. |

`setNoCount()` changes no result and no envelope member. It removes a duplicated count, so a list request performs one counting operation rather than two.

Both page-size properties are themselves validated, at both ends. If `x_bst_startuptrk.rest.max_limit` does not resolve to a positive whole number the API falls back to a ceiling of `50`; if `x_bst_startuptrk.rest.default_limit` does not, it falls back to `20`. Each resolved value is then capped at `PAGE_SIZE_CEILING`, which is `50`, and the resolved default is clamped to the resolved maximum. **The pagination bound is therefore a property of the contract rather than of the configuration:** a floor stops a property from removing the page size, and the ceiling stops a property from removing the page. The largest page any of the seven list operations can serve is fifty records, whatever the two properties hold and whatever the caller sends.

**That validation is a floor, not a range, and the absence of a ceiling is stated positively so it is not mistaken for one.** `AppProperties.getBoundedInt()` enforces a **minimum only**: a value below the minimum resolves to the shipped fallback, and a value above it is returned as supplied at any magnitude. Neither page-size property therefore carries an upper clamp, and the consequence is exact — an administrator who sets `x_bst_startuptrk.rest.max_limit` to `1000000` raises the ceiling to a million rows, and `x_bst_startuptrk.rest.default_limit` set to the same value makes that the size of a page nobody asked for. **No upper bound is imposed**, for two reasons a reader can check: the requirements fix the two shipped values at `50` and `20` and state no ceiling anywhere, so any figure invented here would be this document's rather than the contract's; and both properties are `x_bst_startuptrk.admin` read **and** write, so the only account that can move them is the one entitled to change the API's behaviour deliberately. The bound that does exist independently of them is `sysparm_offset`'s fixed `10000` ceiling, which is a constant in `RestQueryHelper` rather than a property and cannot be raised by configuration at all. An operator widening either property should treat it as a resource-consumption decision and re-read [Bounds](#bounds) first.

### Result ordering

Every list operation sorts on a **documented primary column and then on `sys_id`**, which is unique. Each result set therefore has exactly one total order, and offset paging over it neither repeats nor omits a row even where the primary column ties.

| List operation | Primary sort | Tie breaker |
| --- | --- | --- |
| `GET /startups` | `name` ascending | `sys_id` ascending |
| `GET /founders` | `name` ascending | `sys_id` ascending |
| `GET /founders/{startup_id}/executives` | `name` ascending | `sys_id` ascending |
| `GET /investors` | `name` ascending | `sys_id` ascending |
| `GET /funding-rounds` | `round_date` **descending** | `sys_id` ascending |
| `GET /jobs` | `posted_date` **descending** | `sys_id` ascending |
| `GET /news` | `published_date` **descending** | `sys_id` ascending |

A record with an empty date sorts last on the three descending orders. The `participating_investors` array of a funding round is ordered by the **`investor` reference** of the join row — `InvestorPortfolioService.participantsForRounds()` applies `orderBy('investor')` — so it too is stable between reads.

The ordering is **not caller-configurable**: no operation accepts a sort parameter. A consumer paging a resource to exhaustion may rely on each record appearing exactly once for as long as the underlying rows are unchanged.

### Query values

Every caller-supplied filter value is **validated before it reaches a query**, and every condition is bound through `addQuery` and `addOrCondition` rather than concatenated into an encoded query string. `RestQueryHelper` owns the validation and the binding; the operations pass it validated values and never assemble query text.

| Value class | Accepted form | Rejected |
| --- | --- | --- |
| Record identifier — `startup` on `/founders`, `/funding-rounds`, `/jobs` and `/news`, and `{startup_id}` on the nested executives sub-resource | Exactly 32 hexadecimal characters, matched case-insensitively and applied lowercased | Anything else, including a partial identifier, an encoded query fragment or an empty path segment |
| Choice value — `industry` on `/startups`, `type` on `/investors`, `round_type` on `/funding-rounds`, `department` on `/jobs` | A member of that column's choice list, matched **case-insensitively** and then bound as the **canonical** member of the list | Any value absent from the list, whatever its casing |
| Free text — `name` on `/startups`, `/founders` and `/investors`, `location` on `/startups`, `source` on `/news` | the value is put into the one stored form — every zero-width and directional formatting character removed, every remaining control character replaced with one space, then trimmed — and truncated to 100 characters. Truncation is applied by `_text()`, which every filter and body value is read through; `_normalise()` is the underlying normalisation step and deliberately preserves full length, because it is what the length checks themselves measure. `_normalise()` holds no character inventory of its own: it delegates to `AppProperties.normaliseText()`, the application's one definition, which is the same method the ingestion write path and the startup insert-and-update rule apply. The two character classes and the reason each receives a different action are set out in [Two character classes, two actions](#two-character-classes-two-actions). | Nothing. A free-text filter never fails validation |

A rejected value returns `400` with the general failure body and a message naming the parameter. An **absent** filter is not a rejection: the filter is simply not applied.

**A free-text filter is never rejected, and `^` is not special to it.** That is worth stating precisely, because the opposite is a natural assumption. `^`, `^OR` and `^NQ` are the clause separators of the platform's **encoded-query string syntax**, and they matter only to a query assembled by concatenating text. This API assembles no such query: every operand reaches the database through `addQuery()` or `addOrCondition()` on the condition API, as a bound value. A `^` in a `name` filter is therefore matched as the literal character `^` inside a `CONTAINS` operand — it finds the startups whose name contains a caret, which is almost certainly none, and it cannot begin a new clause, negate a condition or reach a column the operation did not name.

**The guarantee is structural, not a denylist.** No filter value can become query syntax because no filter value is ever concatenated into query syntax. A denylist would be the weaker construction: it would have to enumerate every operator the encoded form recognises, and it would silently reject legitimate values that happen to contain one. What the free-text handling does do is normalise — zero-width and directional formatting characters are removed and every remaining control character becomes a space, so a value can neither break a log line nor disguise what it says; the value is trimmed; and it is truncated at 100 characters so an over-long operand cannot be used to force an expensive scan. Identifiers and choice values are matched against their exact permitted forms, so every filtered read runs on the intended, indexed predicate.

### Response envelope

`RestResponseBuilder` builds every list response. The envelope has **exactly four members**, all of them always present. There is no fifth member under any condition.

| Member | Type | Always present | Content |
| --- | --- | --- | --- |
| `result` | Array of objects | Yes | The page of records, each serialised through the per-field read gate. |
| `total_count` | Integer | Yes | The **exact** number of records matching the query, across all pages. Never a floor, never truncated, at any magnitude. |
| `limit` | Integer | Yes | The applied limit, after the bounds above. |
| `offset` | Integer | Yes | The applied offset, after the bounds above. |

**There is no fifth member.** A consumer may read `total_count` as an exact figure and render it as one — no capping flag has to be tested, because there is no condition under which the count is inexact. A consumer paging to the end will find the last `result` array short, exactly as `total_count` predicts. **A consumer may treat `total_count` as exact and page arithmetic on it.** The last page is `ceil(total_count / limit)`, and the page at the final offset carries `total_count` modulo `limit` rows. Earlier drafts of this contract carried a `total_count_capped` member reporting that the count had stopped at a ceiling; **that member does not exist** and no response ever carries it. A client written against it would test a key that is never present, which is harmless, but no client should be written to expect an inexact total.

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

`total_count` is the **exact** number of records matching the operation's query, independent of `limit` and `offset`, and independent of the caller's role.

**It is produced by one aggregate count, behind a role gate.** `RestResponseBuilder.countState()` does two things in order. First it calls `hasAnyAppRole()`, which is three `gs.hasRole()` tests against `x_bst_startuptrk.admin`, `x_bst_startuptrk.premium_user` and `x_bst_startuptrk.user`; a caller holding none of the three receives a **denial** rather than a number, and the operation answers `403` through `rejectDeniedCount()` — it does not answer `200` with a total of zero, which would tell a caller that a set it may not read is empty. Second, having established that the caller holds a role the table-level read control grants, it opens a `GlideAggregate` over the same table, applies the **same** conditions the page applies, and takes a single `COUNT`. Each list operation builds its conditions once, as a single function, and hands that one function to both the count and the record query, so the count and the page cannot be built from different filters.

**The gate is a role test, not a secured-read probe.** `canRead()` on a secured record answers for the record the object is currently positioned on, so on an un-queried, unpositioned object its answer is not a table-level right. The role test is exact and needs no query, and it holds because every one of the seven table-level read controls grants exactly the three scoped roles and no other: "holds one of the three" and "may read this table" are the same statement. The invariant, and the change that would invalidate it, are recorded in [`./access-control.md`](./access-control.md); the gate itself is recorded at `D-267`, which amends `D-225`.

**The count is an aggregate, and its exactness is unconditional.** An aggregate count is one database operation at any magnitude, and every list response carries an exact total. Secured iteration and a bounded count are the two rejected alternatives, recorded at `D-225`.

**This rests on a documented invariant, and the invariant is load-bearing.** All seven entity tables grant **table-level** read to all three roles, and the roles differ only at **field** level. Record-level visibility is therefore identical for the administrator, the base user and the premium user, so an aggregate count is a correct `total_count` for every caller. **The moment a record-level restriction is added to any of these tables, that stops being true**: an aggregate would over-report for a restricted caller, and `countState()` would have to be replaced by a secured count with whatever cost that carries. The invariant is recorded here, in [`./access-control.md`](./access-control.md) and in [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md) precisely so a future change cannot break the contract silently.

**No record data reaches a caller through an unsecured query.** The aggregate counts rows; it never returns a field value. Every value in `result` is read through `GlideRecordSecure` and passed through the per-field read gate. The other aggregate queries the delivered Update Set carries are internal maintenance counts — closed rate-limit windows in `RateLimitService._countClosed()` and `_observed()`, and the distinct-startup count behind `portfolio_count` in `InvestorPortfolioService._startupsForInvestor()`. None of them returns record data to a caller; all are tabulated in [`./access-control.md`](./access-control.md).

**A caller who may not read the table is refused, not given a zero.** `403` with the general failure body and a message that names no physical table is the answer in that case, for all seven list operations. It is listed under [Error contracts](#error-contracts).

### The inclusion criteria and the count

Where the startup inclusion criteria apply to a list operation, they are applied **identically to the result set and to `total_count`**. `StartupSearchService.buildPlan()` produces one query plan, and one `applyConditions` function wrapping `StartupSearchService.applyPlan()` is handed to both the secured count and the secured result set, so the criteria reach both through the platform condition API from a single definition; applying the criteria to one and not the other makes the count disagree with the page contents. The predicate itself — `active` true and `headquarters_location` containing a configured location token — is specified in [`./data-model.md`](./data-model.md) and is not restated here.

Because the plan is applied through the condition API rather than assembled as a query string, a caller cannot reach the predicate: supplying `name=^ORactive=false` matches startups whose name literally contains that text, which is none of them, rather than widening the result set.

### Response size, and why there is no projection parameter

**A page carries the resource's whole field list.** There is no `sysparm_fields`-style projection in this contract: the only request parameters a list operation accepts are `sysparm_limit` and `sysparm_offset`, plus that resource's own filters. This is a deliberate consequence of two binding statements — prompt section 1.0 declares the field list **binding and complete**, and section 3.0 requires a denied premium field to be **omitted** rather than nulled — so what a caller receives is the full list minus whatever its roles do not grant, and nothing else varies. A client that wants fewer fields discards them.

**What that costs is measured, over the delivered operation scripts.**

| Measurement | Value |
| --- | --- |
| `/startups?sysparm_limit=50`, representative content | **21,781 bytes** over 50 records, 13 keys per record |
| The same 50 records reduced to a four-field client-side projection — `name`, `industry`, `headquarters_location`, `funding_stage` | **5,251 bytes** |
| Ratio | **4.15×** |

**The worst case is bounded by the dictionary, and it is worth stating in absolute terms.** Fifty startups with every text column at its declared maximum — a 4,000-character `description`, a 100-character `name`, 255-character `website` and `logo_url` — produce **250,791 bytes, 244.9 KiB**, that is **5,016 bytes per record**, for a caller holding `x_bst_startuptrk.admin` or `x_bst_startuptrk.premium_user`. The same page for a caller holding only `x_bst_startuptrk.user` is **247,241 bytes, 241.4 KiB** across 11 keys rather than 13, because `total_funding_usd` and `institutional_funding_last_5yrs` are omitted. That is the ceiling: `sysparm_limit` cannot exceed `50` (see [Bounds](#bounds)) and no column can exceed the length [`./data-model.md`](./data-model.md) declares, so no page of any resource can be larger than its own field list times fifty.

With representative rather than maximal content the same page is a fraction of that — **430** bytes per startup record, **317** per founder, **192** per investor, **337** per job posting and **343** per news article, each measured at page size 20 through the delivered scripts.

**Transport compression is the platform's, and it is unverified here.** Whether a response is served with `Content-Encoding: gzip` is a property of the instance's web tier rather than of anything in this Update Set, and it could not be observed during validation — the instance was hibernating and its placeholder responder returns no `Content-Encoding` at all. The requirements state no compression requirement. Confirming it on a woken instance is recorded as an open item in [`./validation-checklist.md`](./validation-checklist.md), and it is not an acceptance gate.

## Resources

Six logical resources. Each section lists every operation on that resource, then gives the resource's JSON representation and marks the premium-gated fields. A premium-gated field is **omitted from the response object** for a caller the field-level read ACL denies; the key is absent, never present with a null.

Path templates are relative to the physical base path `/api/x_bst_startuptrk/v1/`. `{id}` is the record's `sys_id`.

Each resource that pages also accepts query filters. The six per-resource tables below define **thirteen filters** in total, and each states its semantics in a **Comparison** column. That column takes one of exactly three values, each of which names a platform encoded-query operator, so every claim in it is checkable against the operation script:

| Comparison | Encoded-query operator | Count | Applies to |
| --- | --- | --- | --- |
| Case-insensitive contains | `LIKE` | 5 | `name` on `/startups`, `/founders` and `/investors`; `location` on `/startups`; `source` on `/news` |
| Exact match against a choice value | `=` | 4 | `industry` on `/startups`; `type` on `/investors`; `round_type` on `/funding-rounds`; `department` on `/jobs` |
| Exact match against a startup `sys_id` | `=` | 4 | `startup` on `/founders`, `/funding-rounds`, `/jobs` and `/news` |
| Exact match against a provider locator | `=` | 1 | `source_url` on `/funding-rounds` |

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

`GET /funding-rounds` accepts three query filters in addition to the pagination parameters. Results are ordered by `round_date` descending, then by `sys_id`.

| Filter | Column matched | Comparison | Accepted form |
| --- | --- | --- | --- |
| `startup` | `startup` | Exact match against a startup `sys_id` | 32 hexadecimal characters, per [Query values](#query-values) |
| `round_type` | `round_type` | Exact match against a choice value | A member of `FundingRound.round_type` |
| `source_url` | `source_url` | Exact match against the provider locator | An absolute `https` URL, validated by `RestQueryHelper.getUrlParam()`; anything else answers `400` with `source_url must be an absolute https URL` |

**`source_url` is an equality filter and not a search.** It exists so a round ingested from a named provider record can be looked up by that record's locator during provenance reconciliation, and it is the predicate the declared `source_url` index serves. It is never bound as a `CONTAINS` operand, which is why a value that is not an absolute `https` URL is refused rather than trimmed into a substring scan.

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

`participating_investors` is emitted as a **JSON array of investor references assembled from `x_bst_startuptrk_m2m_round_investor`**, one array element per linked investor, de-duplicated. An empty array means the round has no participating investors recorded. The array is not a writable field: participating investors are maintained as rows of the join table, and the join table is authoritative for them. The mechanism is recorded at `D-010` and the array projection at `D-011` in [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md).

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

Writes to this resource are **manual entry or CSV import only**. There is no automated NewsArticle ingestion: neither ingestion flow writes `x_bst_startuptrk_newsarticle`, and the fallback dataset carries no NewsArticle file. Records reach the table through the platform form, through this resource's `POST` and `PUT` operations, or through an ad hoc import. The exclusion is stated here and is recorded again in [`./gaps-and-flags.md`](./gaps-and-flags.md).

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

This roll-up is the operation-count evidence that criterion 3 in [`./validation-checklist.md`](./validation-checklist.md) and the API section of [`../../docs/decisions/TRACEABILITY_MATRIX.md`](../../docs/decisions/TRACEABILITY_MATRIX.md) are each to resolve against.

## Field validation

Every value in a create or update body is validated **before any write is attempted**, by `RestQueryHelper.validateBody()`. Each of the 12 body-bearing operations declares a specification listing, for each writable field, its validation type, its declared length, whether it is mandatory on create, and — for a choice or a reference — its choice list or target table. Validation is not a formality applied to some fields: a body member that names no field in the specification is ignored, a body naming no writable field at all is a `400`, and **no field is written on a type the specification does not declare**. The `_coerce` step has no permissive default; an unrecognised type answers `<field> has an unsupported type` rather than storing the value.

Every value is first passed through the same normalisation the filter parameters of [Filter parameter validation](#filter-parameter-validation) use, so a value is treated identically whether it arrives as a query parameter or in a body. `RestQueryHelper._normalise()` is the boundary's entry point; it holds no character inventory of its own and delegates to **`AppProperties.normaliseText()`, the application's one definition**, which is the same method `IngestionMapper` applies to every value an ingestion run maps and the same method the `Trim and validate startup` rule applies to every string field written through a form. A value that normalises to empty, or to spaces alone, is treated as absent.

#### Two character classes, two actions

`normaliseText()` recognises two disjoint classes and applies a different action to each, because the two classes fail differently. Both actions run before the value is trimmed, and the whole normalisation is idempotent.

| Class | Members | Action | Why this action |
| --- | --- | --- | --- |
| **Zero-width and directional formatting** | soft hyphen `U+00AD`; Arabic letter mark `U+061C`; Mongolian vowel separator `U+180E`; zero-width space, non-joiner and joiner and the two directional marks `U+200B`–`U+200F`; the bidirectional embeddings and overrides `U+202A`–`U+202E`; word joiner and the four invisible operators `U+2060`–`U+2064`; the four bidirectional isolates `U+2066`–`U+2069`; byte order mark `U+FEFF`; the three interlinear annotation marks `U+FFF9`–`U+FFFB` | **Removed** | Every member paints nothing, so removing it leaves the rendered string unchanged and makes the stored value equal the value a reader sees. Replacing one with a space would **fabricate** a word boundary the source never had: `Wid<U+00AD>get` would become `Wid get` rather than `Widget` |
| **Remaining control characters** | the C0 controls `U+0000`–`U+001F` including tab, newline and carriage return; `DEL` `U+007F`; line separator `U+2028`; paragraph separator `U+2029` | **Replaced with one space** each | These are not zero width — they occupy or force layout — so deleting one can **join** two tokens the original separated, turning two words into one word that was never supplied. A body carrying `Acme\u0001Corp` therefore stores `Acme Corp`, not `AcmeCorp` |

The C1 range `U+0080`–`U+009F` is a member of neither class and is left alone: a C1 byte in a supplied value is an unmatchable character rather than a hostile one.

**Neither class is refused.** These characters most often arrive from a copy-and-paste or an upstream export rather than from an attacker, and refusing a whole record over one invisible character would reject data that is otherwise correct. What the normalisation guarantees instead is that no supplied value can break a log line, smuggle an invisible direction override into stored data, use one to defeat the pattern checks below, or present two records whose names render identically. Because it runs **before** the length check, a value whose control characters expand to spaces is measured at its post-normalisation length.

**A value consisting only of these characters is empty.** That is what makes cleaning rule 4 and the mandatory-field checks correct rather than nominal: a `name` of `U+200B U+00AD` is *missing*, not present-but-invisible, so the record is rejected by ingestion and the insert is aborted by the startup rule.

**The length check runs on the normalised value at its full length, before anything shortens it.** `RestQueryHelper._ceiling()` resolves the field's ceiling as the column's own declared maximum, bounded by the type's ceiling only where the type has one that is smaller — 255 for a `url`, 254 for an `email` — and falling back to 100 for a field that declares no maximum. A value longer than that ceiling is **refused**, never trimmed to fit. The ordering matters concretely: `contact_email` is `string(100)`, so a 101-character address is answered `contact_email exceeds 100 characters` rather than being shortened to its first 100 characters and validated in that shortened form, which would have stored an address the caller never supplied.

### Validation types

| Type | Rule | Refusal message on a value that fails |
| --- | --- | --- |
| `string` | The value must be a **primitive**, and its length after trimming must not exceed the column's declared maximum. A JSON object or array is refused rather than stringified — without this an object would be stored as `[object Object]` and an array as its comma-joined members, both of which satisfy a length check. | `<field> exceeds <n> characters`, or `<field> must be text` |
| `url` | Length must not exceed the column's declared maximum, which is **255** on every `url` field the API exposes, and the value must match the absolute-`https` allowlist below. | `<field> exceeds 255 characters`, then `<field> must be an absolute https URL` |
| `email` | Length must not exceed the column's declared maximum, which is **100** on `contact_email`, the only writable email field; the type's own ceiling of 254 applies only where a column declares no smaller maximum. The value must then match the email allowlist below. | `<field> exceeds 100 characters`, then `<field> must be an email address` |
| `date` | Must be `yyyy-MM-dd` in shape **and** must name a day that exists in the calendar. | `<field> must be a yyyy-MM-dd date`, then `<field> must be a date that exists in the calendar` |
| `integer` | Optionally signed whole number. | `<field> must be a whole number` |
| `currency` | A decimal amount. | `<field> must be an amount` |
| `boolean` | JSON `true`/`false`, or the strings `true`, `false`, `1`, `0`. | `<field> must be true or false` |
| `choice` | Must be a member of the column's choice list, matched case-insensitively; the stored value is the canonical member, not the supplied casing. | `<field> must be one of <choice list>` |
| `multichoice` | Every comma-separated token must be a member of the column's choice list. | `<field> must contain only <choice list>` |
| `reference` | Must be 32 hexadecimal characters, accepted in **either** case and stored lowercased, **and** must name a record the caller can read, tested through `GlideRecordSecure`. | `<field> must be a 32 character sys_id`, then `<field> does not name a readable record` |

The reference-failure message is deliberately generic. The physical table the reference was tested against is **not** disclosed to the caller; it is written to the application log through `gs.info`, tagged `[x_bst_startuptrk.RestQueryHelper]`, together with the supplied identifier and the field name. A caller cannot use a sequence of failed writes to enumerate the schema, and an operator retains the detail needed to diagnose one.

### URL fields — absolute `https` only

A `url` value must match, in full:

- Scheme `https://`, matched case-insensitively. **`http`, `ftp`, `file`, `data`, `javascript` and every other scheme is refused**, as is a scheme-relative `//host/path` and a bare `host/path`.
- A host of at least two dot-separated labels, each label starting and ending with a letter or digit and containing only letters, digits and hyphens. A single-label host such as `localhost`, a label with a leading or trailing hyphen, and an empty label are all refused.
- An optional port of one to five digits.
- An optional path, query and fragment drawn only from the RFC 3986 character set `A-Z a-z 0-9 - . _ ~ % ! $ & ( ) * + , ; = : @ / ? # [ ]`.

- **No user information before an `@` in the authority.** `https://user:pass@evil.example.com/` and `https://evil.example.com@good.example.com/` are refused. The check reads the authority component — everything after `://` up to the first `/`, `?` or `#` — and refuses it outright if it contains an `@`. An `@` later in the path or query is legitimate and is permitted.
- A total length within `255` characters, or the column's own `max_length` where that is smaller.

The allowlist is what makes the field safe for a consumer to render as a link target. The permitted set contains **no `<`, no `>`, no single or double quote, no backtick, no whitespace, no backslash and no brace**, so a stored URL cannot close an HTML attribute or open a tag, and the scheme restriction means it cannot carry `javascript:` or `data:`. This is an input-boundary reduction, not a substitute for output encoding — see [Content type](#content-type).

#### One validator, both write paths

**`RestQueryHelper.isHttpsUrl()` is the single canonical URL allowlist of the application, and `RestQueryHelper.isEmailAddress()` is the single canonical address allowlist.** Both are public methods, and both are called from exactly two places:

| Caller | When |
| --- | --- |
| `RestQueryHelper._coerce()` | Every `url` and `email` value a REST create or update supplies. |
| `IngestionMapper.coerceField()` | Every `url` and `email` value an ingestion run maps, on both the live and the fallback path, **before** any staging-to-entity write. |

`IngestionMapper` reaches them through its `helper()` accessor, which resolves one `RestQueryHelper` instance also used for the calendar rule. The nine columns that carry a `url` or `email` kind are `Startup.website`, `Startup.logo_url`, `Founder.linkedin_url`, `Founder.contact_email`, `Executive.linkedin_url`, `Executive.contact_email`, `Investor.website`, `FundingRound.source_url` and `JobPosting.url` — seven URLs and two addresses.

**What the shared validator covers, and what a refusal costs.** These nine columns are read back and rendered by the Service Portal, whose widgets bind persisted values into link and image targets, and the portal cannot tell which write path a stored value arrived by. Both write paths therefore check a value against the one definition. Ingestion refusals are **not** fatal to a run: a refused value is dropped with a bounded reason — `<field> is not an absolute https URL without an embedded credential`, or `<field> is not an email address` — the reason is logged, and the run continues, exactly as every other cleaning refusal does. A refused value on a **mandatory** field rejects that record, as cleaning rule 4 requires; none of these nine is mandatory.

### Email fields — allowlisted local part and host

An `email` value must be a local part of 1 to 64 characters drawn from `A-Z a-z 0-9 . _ % + -`, an `@`, then a host of at least two dot-separated labels under the same label grammar as a URL host, within `254` characters in total or the column's own `max_length` where that is smaller. Quoted local parts, address comments, display names, angle brackets, a leading `mailto:` and any value carrying more than one `@` are refused. As with a URL, the permitted set carries no character with HTML or script significance. The same method validates the REST write path and the ingestion path — see [One validator, both write paths](#one-validator-both-write-paths).

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

That is 14 `url` specifications, 2 `email` and 6 `date` across the 12 body-bearing operations. `x_bst_startuptrk_executive.contact_email` carries no entry because Executive has no create or update operation — it is served only by the nested read sub-resource — so the only two routes that write an executive are an ingestion flow and the platform form. **The two do not validate alike, and the difference is an operator obligation rather than a delivered control.** An ingestion write passes through `IngestionMapper.coerceField()`, which applies the same `RestQueryHelper.isHttpsUrl()` and `isEmailAddress()` allowlists this API applies. A platform-form or list-editor write does not: `linkedin_url` and `contact_email` are ordinary length-constrained strings in the dictionary, which enforces the column length and nothing about the value's shape, and no business rule validates them. Only `x_bst_startuptrk.admin` holds write access on any application table, so the exposure is bounded to an administrator typing directly into the form — but a value entered that way can reach the portal's link and image targets unvalidated. **What an operator must do:** enter these two columns through the API or an ingestion run, or check any value typed into the form against the allowlists above. The same obligation applies to the seven URL columns on the other tables.

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
| `429` | The caller has exhausted its request budget for the current window. A request that could **not** be accounted for answers `500`, not `429` — see the row below and `D-274`. | `{"error": "rate_limit_exceeded", "retry_after": 42}` |
| `500` | An unhandled error occurred inside the operation script, **or** rate-limit accounting could not be persisted for the request. | `{"error": "<message>"}` |

The order in which an operation applies its checks is fixed and identical across all 31, because it determines which status a request that fails more than one check receives: the rate limiter first, then the in-script role guard, then — on a body-bearing operation — the media-type guard, then parameter and body validation, then the record access. A caller over budget therefore reads `429` rather than `415`, and an unauthorised caller reads `403` rather than a validation `400`, so no error message reveals anything to a caller not entitled to reach that stage.

### Rate limit — HTTP 429

Body:

```json
{"error": "rate_limit_exceeded", "retry_after": 42}
```

`retry_after` is a whole number of seconds, computed as the window start plus the window length minus the current time. `42` above is an illustrative value; the value returned is the seconds remaining in the caller's current window, with a floor of `1`.

Mechanism. Per-caller fixed-window accounting in the table `x_bst_startuptrk_rate_limit_counter`, maintained by the `RateLimitService` Script Include. `RateLimitService` resolves the current window, records the request against it, and rejects the request once the count exceeds the configured budget. Both properties are validated before use: a value that is not a positive whole number falls back to `100` requests and a `60` second window.

**The accounting is keyed, and the increment is the database's own.** `window_start` is the current time truncated to a whole multiple of the window length — `epoch - (epoch % window_seconds)` — so every request inside one window derives the identical value, and `windowKey(caller, apiResource, windowStart)` joins the caller `sys_id`, the resource token and that window start with `|` separators into the `window_key` column, truncated to its 200-character length. `consume()` queries **`window_key` alone**, raises `request_count` on the lowest-`sys_id` row carrying the key with `GlideRecord.addValue()`, and inserts a row carrying `1` when the key has none. The window total is then re-read as a `SUM` aggregate over every row carrying the key, and a total **strictly greater** than the budget sets the `429` response above. `window_key` is **mandatory** and **unique**, so it is both the query's index and the constraint that keeps one window to one row.

**The unique key bounds what concurrency can do, and does not eliminate it.** Two requests arriving together cannot both insert — the unique `window_key` refuses the loser, which retries against the row the winner created — and the increment itself is the database's own atomic add rather than a read followed by a write. What remains is that each request decides against the total as it stood after its own increment landed, so under genuine concurrency the effective limit can overshoot slightly. That outcome is accepted under the prototype scope rather than engineered away; the decision, the alternatives and the mitigation paths deliberately left unbuilt are recorded at `D-040` in [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md).

| Step | Behaviour |
| --- | --- |
| Query the window key | `_apply()` queries **`window_key` alone**, ordered by `sys_id`, and holds the lowest-`sys_id` row as the one to write. The other four columns are written on insert and are never part of the lookup. A second row on one key is reported in one bounded `error` line, and because the total is read by aggregate its count is summed into the decision rather than ignored, so a duplicate can never be used to double a budget. |
| Insert, when no row exists | Inserts one row with `request_count` `1`. A refused insert is logged at `error` and reported as unpersisted. |
| Increment, when a row exists | Raises `request_count` on that row by one with the platform's **atomic numeric increment**, `GlideRecord.addValue('request_count', 1)`, so the database applies the addition rather than the script writing a total it read earlier. |
| Read the total back | `_observed()` then reads the window total with **one `GlideAggregate` SUM over every row carrying that `window_key`**. That total, not the value the script read before incrementing, is what the budget decision uses. |

**What the accounting costs is measured rather than estimated, and it is the larger half of a small list call.** Executing the delivered operation scripts four times inside one window and attributing every database operation to its table:

| Call | Counter-table operations | Total operations for `/investors?sysparm_limit=1` | Accounting share |
| --- | --- | --- | --- |
| The **first** request in a window | **2** — one `window_key` query and one insert | **4** | 50 % |
| **Every request after it** in the same window | **4** — one `window_key` query, one row fetch, one atomic increment and one `SUM` aggregate | **6** | **67 %** |

**The share does not fall as the page grows.** The data side of a list call is fixed at two operations whatever the page holds — one windowed secured read and one `COUNT` aggregate — so a page of 50 costs the same four accounting operations as a page of 1; what grows with the page is rows read, not operations. That invariance is the property the API was built for, and it is why the accounting share is a constant rather than a scaling cost.

**This is the price of the three correctness properties above, and it is recorded as a baseline rather than as a defect.** Each of the four steady-state operations exists for a stated reason: the keyed query finds the window without scanning, the row fetch positions the increment on a specific row, the increment is the database's own atomic add so no count is lost, and the `SUM` read-back is what makes the decision use the post-increment total rather than a value read earlier. Dropping the read-back would halve the steady-state cost and reintroduce exactly the contention error the read-back removes. Under Agent Action Plan section 6.0's prototype focus no performance target is stated for this API and none is invented, so no reduction is delivered; the trade is recorded at `D-040`.

**Behaviour under contention is stated rather than glossed.** No increment is lost: the addition is applied by the database, and the total the decision uses is read back after it, so `n` requests arriving concurrently against a fresh window end at exactly `n`. What remains is that the **first** request in a window inserts rather than increments, so two simultaneous first requests can produce two rows on one tuple — which the aggregate read-back makes correct rather than lossy, and which is reported in one bounded warning. The mechanism and the residual behaviour are recorded at `D-040` and `D-387` in [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md). Sequential traffic — which is what the criterion 3 test issues — is counted exactly.

**The policy on an unaccountable request is fail-closed, and it answers `500` rather than `429`.** If, after three attempts, the counted write did not persist, **two** lines are written to the application log at `error` and **the request is refused with the [`500` body](#server-error--http-500)**. `RateLimitService` writes the first, tagged `[x_bst_startuptrk.RateLimitService]`, naming the window key and the attempt count. It then hands `RestResponseBuilder.serverError()` an error reading `Rate limit accounting could not be persisted for window <key> after <n> attempt(s)`, which writes the second line, tagged `[x_bst_startuptrk.RestResponseBuilder]` and carrying the correlation identifier as `error_id=`. Only the correlation identifier reaches the caller — the body is the generic `Internal server error (error_id …)`, never the accounting message. The request is not admitted.

**The distinction between the two refusals is part of the contract, not an implementation detail.** They mean different things to a caller and they demand different responses from one:

| Condition | Status | Body | What the caller should do |
| --- | --- | --- | --- |
| The caller's counted requests in the current window exceed the configured budget | `429` | `{"error": "rate_limit_exceeded", "retry_after": <n>}` | Wait `retry_after` seconds and retry. The request was well formed and the service is healthy; the caller is over quota. |
| The accounting write did not persist | `500` | `{"error": "Internal server error (error_id <id>)"}` | Treat it as a server fault and escalate with the `error_id`. **The caller is not over quota**, and waiting will not help — nothing about the caller's own behaviour caused it. |

Answering `429` for a persistence failure would tell a caller under its budget that it had exhausted a quota, and would hand it a `retry_after` that means nothing, so a well-behaved client would back off for a fault that back-off cannot clear while the real fault — a counter table that is not writable — went unreported as a server error. The service is nonetheless still **fail-closed**: an unaccountable request is exactly the request an attacker would try to manufacture in volume, so it is refused rather than admitted, which makes a counter-table outage a denial of service against the API rather than a bypass of its limit. Both halves of that — refusing, and refusing with the right status — are recorded in [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md).

**Platform backstop, and the two surfaces it applies to are not the same.** A platform inbound rate-limit rule lives in `sys_rate_limit_rules`, which is Global scope, so it **cannot be shipped in this scoped Update Set** on either surface; it is an instance-side action.

| Surface | Status | Threshold |
| --- | --- | --- |
| **This Scripted REST API** | **Optional.** The application's own accounting is the contract here, and it is asserted by the criterion 3 test. | Set it **above** the application budget, never beneath it. A rule beneath the budget fires first and returns the platform's own body, pre-empting the `{"error": "rate_limit_exceeded", "retry_after": N}` contract the test asserts — so a "hard ceiling beneath the application limit" would break criterion 3 rather than harden it. |
| **A platform rule in front of this API** | **Optional defence in depth**, recorded as obligation [`OB-3`](./gaps-and-flags.md#ob-3--an-inbound-rate-limit-rule-in-front-of-the-applications-endpoint) and owned by the instance operator. It refuses a flood before any application script runs, so it is a backstop rather than a substitute — **stated as a recommendation rather than as an acceptance gate**, because no artifact in this package delivers such a rule and AAP section 0.8.3 makes the platform rule optional. Acceptance of this package does not depend on it. | At or above the application budget. An operator who adopts it records the rule and one **observed** `429`; one who declines records that decision. |

Neither rule alters the application contract: the platform's own `429` carries a platform-controlled body, which is why the application limit — and not any platform rule — is what the `429` shape above and the criterion 3 test assert against.

| Property | Shipped value | Role |
| --- | --- | --- |
| `x_bst_startuptrk.rest.rate_limit_requests` | `100` | Requests permitted per caller, per resource, per window. |
| `x_bst_startuptrk.rest.rate_limit_window_seconds` | `60` | Window length in seconds. |

Changing either property changes the limit with no code change. The scheduled job **Prune rate limit counters** runs hourly and deletes counter rows whose `window_start` is older than one configured window length — that is, every row whose window has certainly closed — so the table does not accumulate. It counts only the deletions that actually succeeded and logs any row it could not remove. The same property governs the window length, the `retry_after` computation and the pruning cutoff, so one value controls all three.

A standard `Retry-After` response header carries the same value as the body's `retry_after` member. The header is additive: it **does not alter the body**, which remains exactly the two members above.

The limit applies to **every one of the six resources**, and to the nested executives sub-resource. Each of the 31 operations calls `RateLimitService` first, **inside** its own `try` block, before it does any other work. Placing the limiter inside the error-handling boundary is what guarantees that a counter-table, configuration or limiter runtime failure produces the controlled `500` body below rather than escaping the operation. Accounting is keyed on the resource, so a caller's budget for `/startups` is separate from its budget for `/investors`.

### General failure

Body:

```json
{"error": "<message>"}
```

`<message>` is a human-readable string. The table below is the **complete set** of conditions that produce this body: every `<message>` an operation script can produce appears in it, with its status code, and the **Emitted by** column names exactly which of the 31 operations produce it.

| Condition | Status | `<message>` | Emitted by |
| --- | --- | --- | --- |
| The record named by `{id}` does not exist, or is not readable by the caller | `404` | `Record not found` | The 6 reads, the 6 updates and the 6 deletes — 18 operations |
| A filter parameter that must be a provider locator is not an absolute `https` URL | `400` | `source_url must be an absolute https URL` | 1 list operation: `source_url` on `/funding-rounds` |
| A path or filter parameter that must be a record identifier is malformed | `400` | `<parameter> must be a 32 character sys_id` | Every operation taking `{id}`, plus the `startup` filter on `/founders`, `/funding-rounds`, `/jobs` and `/news`, and `{startup_id}` on the nested executives path |
| A filter parameter that must be a choice value is not a member of the list | `400` | `<parameter> must be one of <choice list>` | 4 list operations: `industry` on `/startups`, `type` on `/investors`, `round_type` on `/funding-rounds`, `department` on `/jobs` |
| `sysparm_limit` does not resolve to a usable value | none | none — the shipped default of `20` is applied and echoed | All 7 list operations. This is not an error; it is recorded here because a caller may expect one |
| **`sysparm_offset` is negative or not a whole number** | `400` | `sysparm_offset must be a whole number between 0 and 10000` | All 7 list operations. **It is refused, not silently read as `0`** — see [Bounds](#bounds) |
| `sysparm_offset` exceeds the page-depth ceiling | `400` | `sysparm_offset must not exceed 10000` | All 7 list operations |
| A create or update request declares a `Content-Type` that is not `application/json`, or declares none | `415` | `Request body must be application/json` | The 6 creates and the 6 updates |
| A create or update request carries no body | `400` | `Request body is required` | The 6 creates and the 6 updates |
| A create or update request body cannot be read as JSON | `400` | `Request body is required and must be JSON` | The 6 creates and the 6 updates |
| A request body carries no field the resource accepts. On a create this is reached only when every mandatory field is present and no other writable field is supplied, because an absent mandatory field is reported first. | `400` | `Request body carries no writable field` | The 6 creates and the 6 updates |
| A create request omits a mandatory field, or supplies it blank | `400` | `<field> is required` | The 6 creates |
| A supplied value is not a member of its column's choice list | `400` | `<field> must be one of <choice list>` | The 6 creates and the 6 updates |
| A supplied multi-choice value contains a non-member token | `400` | `<field> must contain only <choice list>` | `POST /investors` and `PUT /investors/{id}` — `focus_areas` is the only multi-choice column |
| A supplied string exceeds the column's declared length | `400` | `<field> exceeds <n> characters` | The 6 creates and the 6 updates |
| A supplied integer is not a whole number | `400` | `<field> must be a whole number` | The startup creates and updates — `founded_year` is the only integer column a caller may write |
| A supplied currency value is not an amount | `400` | `<field> must be an amount` | The startup, investor and funding-round creates and updates |
| A supplied date is not `yyyy-MM-dd` | `400` | `<field> must be a yyyy-MM-dd date` | The funding-round, job-posting and news-article creates and updates |
| A supplied date is well shaped but names a day that does not exist | `400` | `<field> must be a date that exists in the calendar` | The same 6 operations |
| A supplied URL is not an absolute `https` URL drawn from the allowlisted character set | `400` | `<field> must be an absolute https URL` | Every create and update carrying a `website`, `logo_url`, `linkedin_url`, `source_url` or `url` column — 12 operations |
| A supplied email address fails the allowlist | `400` | `<field> must be an email address` | The founder create and the founder update — **2 operations**. `x_bst_startuptrk_executive.contact_email` is not writable over this API: Executive has no create and no update operation, as the specification table above states |
| A supplied boolean is not `true`, `false`, `1` or `0` | `400` | `<field> must be true or false` | The startup and job-posting creates and updates |
| A supplied reference is not a 32-character identifier | `400` | `<field> must be a 32 character sys_id` | The founder, funding-round, job-posting and news-article creates and updates — **8 operations**. Executive is absent because it has no create and no update; startup and investor are absent because neither carries a writable reference column |
| A supplied reference names no record the caller can read. **The physical table is deliberately not named** — it is logged server-side instead, so a caller cannot enumerate the schema by probing | `400` | `<field> does not name a readable record` | The same **8 operations** |
| A field specification declares a type the validator does not implement — unreachable in the delivered specifications, and present so an unvalidated value can never be stored | `400` | `<field> has an unsupported type` | The 6 creates and the 6 updates |
| The platform refused the insert | `400` | `Record could not be created` | The 6 creates |
| The platform refused the update, for example because a business rule aborted it | `400` | `Record could not be updated` | The 6 updates |
| The platform refused the delete | `400` | `Record could not be deleted` | The 6 deletes |
| The nested executives sub-resource is called without `{startup_id}` | `400` | `startup_id is required` | `GET /founders/{startup_id}/executives` |
| A bound `REST_Endpoint` access control denies the call before the operation script runs | `403` | Supplied by the platform | All 31 operations, before any script runs |
| The in-script role guard refuses a read from a caller holding none of the three application roles | `403` | `Caller holds no Boston Startup Tracker role` | The 13 read operations |
| The in-script role guard refuses a create, update or delete from a caller without the application administrator role | `403` | `Caller holds no Boston Startup Tracker administrator role` | The 18 write operations |
| **The caller fails the table-level read check when the total is counted** | `403` | `Caller may not read this resource` | All 7 list operations, through `RestResponseBuilder.rejectDeniedCount()`. **A denial is refused, not answered `200` with a total of zero**, and the message names no physical table |

**Every row of that table carries its emitters, and the counts add up to the 31 operations.** The 13 reads are the 6 list operations, the 6 single-record reads and the nested executives sub-resource; the 18 writes are 6 creates, 6 updates and 6 deletes. The 7 list operations are the 6 top-level lists plus the nested sub-resource, which paginates like the others.

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

Two conditions produce it, and the second is the one a caller is most likely to misread:

| Condition | Logged message |
| --- | --- |
| An uncaught failure inside an operation script | The caught error's own message and stack trace |
| **The rate-limit accounting write did not persist** | `Rate limit accounting could not be persisted for caller <sys_id> on <resource> in the window starting <window start>` |

The second is emitted by `RateLimitService.reject()`, which delegates to `RestResponseBuilder.serverError()` rather than composing a body of its own. **It is not a `429`**: the caller is not over quota. See [Rate limit — HTTP 429](#rate-limit--http-429).

### Uniformity

Every one of the 31 operations wraps its body in error handling that delegates to `RestResponseBuilder` for the 500 shape and to `RateLimitService` for the 429 shape. No operation constructs either body itself, so the contract cannot drift between operations: a change to either shape is a change to one Script Include method.

Every other body is likewise produced by exactly one method, so no status shape can drift between operations:

| Status | Sole producer |
| --- | --- |
| `400` | `RestResponseBuilder.badRequest()` |
| `403` from the in-script guard | `RestResponseBuilder.forbidden()`, reached only through `rejectUnauthorisedRead()` and `rejectUnauthorisedWrite()` |
| `404` | `RestResponseBuilder.notFound()` |
| `415` | `RestResponseBuilder.unsupportedMediaType()`, reached only through `rejectNonJsonBody()` |
| `429` | `RateLimitService.body()`, reached only through `RateLimitService.reject()`, and only when the budget is genuinely exceeded |
| `500` | `RestResponseBuilder.serverError()`, reached from every operation's `catch` and from `RateLimitService.reject()` when the accounting write did not persist |
| The list envelope | `RestResponseBuilder.page()` |

How the `429` is made deterministic under test is specified step by step in [`./manual-build/05-atf-test-suites.md`](./manual-build/05-atf-test-suites.md), and the pass condition for the six per-resource REST tests is criterion 3 of [`./validation-checklist.md`](./validation-checklist.md). Neither document restates the contract above.

**Pre-seeding a row at the budget is necessary but not on its own sufficient**, and the reason is the `window_key` column rather than the tuple: the key is **mandatory**, so a seed that omits it is refused or is invisible to `consume()`, and it embeds the **window bucket**, so the current window and the next are two different keys and a boundary crossing lands the request on an unseeded one. Determinism therefore requires four things, and the guide specifies all four:

| # | Requirement | What happens when it is omitted |
| --: | --- | --- |
| 1 | **Delete every row under both keys** — the current bucket's and the next bucket's — before seeding, and assert the count is `0` under each | A row left by an earlier run holds the key the request will resolve to, and the seed cannot be inserted over it because the key is unique |
| 2 | Insert **exactly one at-budget row per key**, each with `window_key` set from `RateLimitService.windowKey()`, and assert the count is `1` under each | A row without `window_key` is refused or is never found by `consume()`; seeding only the current bucket leaves the boundary race open |
| 3 | Seed `caller` with the **user the inbound request authenticates as** — not an impersonated user, because an inbound REST call establishes its own session from its authentication profile | The limiter accounts against the request's own caller; any other `sys_id` leaves the limit untripped |
| 4 | **Delete every row under both keys** afterwards, and assert `0` under each | Counter rows are not rolled back with a test, so leaked rows corrupt the next run's baseline |

There are **seven** resource tokens across the six resources, because the nested executives sub-resource accounts separately from `/founders`: `api_resource` is part of `window_key`, so seeding one does not trip the other. Each of the four requirements applies per token.

## The Script Include call graph

Eight `sys_script_include` records carry the application's service layer. This table is the **rename-impact list**: read a row's third column to find every call site a rename touches.

| Class | Responsibility and public methods | Called by |
| --- | --- | --- |
| `StartupSearchService` | Builds one inclusion-criteria and filter query plan and applies it through the platform condition API. Exposes `readFilters()`, `buildPlan()`, `applyPlan()`, `search()` and `appliesInclusion()`. | The `GET /startups` list operation, and the portal search widgets on the Home/Search route. One class serves both surfaces, so the filter cannot drift between them. |
| `InvestorPortfolioService` | The `portfolio_count` derivation and its stored maintenance, a recalculate-all method, the **one** batched reader of the participating-investor join table, and the reader the calculated `participating_investors` column's own calculation calls. Exposes `countPortfolio()`, `recalculate()`, `recalculateMany()`, `recalculateAll()`, `participantsForRounds()`, `participantList()` and `linkInvestorToRound()`. `participantList()` answers one round's participating investors as the string that column renders, and **writes nothing** — the column is calculated, so there is no stored projection to refresh and no second write target to drift. `participantsForRounds()` takes an array of funding-round identifiers and answers a map from each to its investor references in one query, which is why no operation script, business rule or widget carries its own `x_bst_startuptrk_m2m_round_investor` loop. `linkInvestorToRound()` inserts **one** idempotent pair and is for an administrative one-off link; it is **not** on the ingestion path, which reconciles participation as an exact set through `IngestionMapper.linkParticipants()`. | The two portfolio-count business rules — one on `x_bst_startuptrk_fundinground`, one on `x_bst_startuptrk_m2m_round_investor` — the `participating_investors` column's own calculation, the four funding-round operations that surface that column (`list`, `read`, `create` and `update`), the investor-profile and funding-round widgets, and any background script run after a bulk load. |
| `IngestionMapper` | The four cleaning rules, live and fallback source mapping, source-code translation, reference resolution and the batch upsert. Every write is projected through the record type's own `TARGET_FIELDS` allowlist, so no ingestion path can reach a derived or read-only column. Its entry points are `ingest()` and `ingestStaging()`; it also exposes `helper()`, `useLogger()`, `log()`, `trimStrings()`, `normaliseChoice()`, `normaliseChoices()`, `startupKey()`, `findExistingStartup()`, `findExistingInvestor()`, `findExistingByKey()`, `dedupeBatch()`, `missingMandatory()`, `overlengthFields()`, `clean()`, `coerceField()`, `calendar()`, `mapStagingRow()`, `mapSuppliedRow()`, `mapLiveRecord()`, `unwrapLive()`, `resolveReferences()`, `resolveStartupKey()`, `resolveInvestor()`, `resolveParticipants()`, `upsert()`, `linkParticipants()`, `prepareOne()`, `mapRow()`, `expandRows()` and `writeStagingState()`. `findExistingByKey()` is what makes a replayed batch idempotent for the four record types that have no name-based lookup: it matches a founder or executive on `startup` plus `name`, a funding round on `startup` plus `round_date` plus `round_type` and then on `startup` plus `round_date`, and a job posting on `startup` plus `url` and then on `startup` plus `title` plus `posted_date`, resolving only on exactly one match. `helper()` resolves `RestQueryHelper` so the URL and address allowlists have one home rather than two copies, and `props()` resolves `AppProperties` so the provider-origin allowlist, the sanitiser and the fingerprint have one home likewise. `readNameList()` is the **single reader of the participant name carrier**: it accepts a real array, a JSON array in text, a pipe-delimited string or a single name, and it never splits on a comma — a comma is a legal character inside an investor name. `upsert()` returns the participant link counts it applied, so no caller links twice. `resolveStartupKey()`, `resolveInvestor()`, `findExistingByKey()`, `findExistingStartup()` and `findExistingInvestor()` each answer `{ ok, sys_id, matches, reason }` rather than a bare identifier, because each resolves only on exactly one match and has to report which of the two failure modes — no match, or an ambiguous name — it hit. There is no `applyDefaults()`: a column default is declared once in the dictionary and applied by the platform on insert. | Both ingestion flows, the Crunchbase flow and the LinkedIn flow. |
| `IngestionLogger` | Structured run-scoped events for the flow execution log, implementing skip-the-record-and-continue-the-run, plus the run summary and the run-completion marker. **Every identifier and every value it writes is either an opaque reference, a short enumeration label, or the literal `(redacted)` or `(blank)`** — never an external name, email address, biography, URL or upstream message, and never a hash or fingerprint of one. Exposes `reset()`, `useRun()`, `drainEvents()`, `getEvents()`, `counters()`, `ordinal()`, `reference()`, `info()`, `warn()`, `skipRecord()`, `failRecord()`, `rejectRecord()`, `duplicateRecord()`, `invalidEncoding()`, `unmatchedChoice()`, `countProcessed()`, `writeRunSummary()`, `markRunComplete()`, `sourceOfRun()` and `safeText()`. `counters()` answers `processed`, `rejected`, `skipped`, `errors`, `duplicates`, `unmatched` and `rule3_deviations`. `rule3_deviations` counts only the unmatched choice values that could not be stored as `Other` because their choice list declares no such member, which is the flagged cleaning-rule-3 deviation. `errors` counts the incoming rows whose **own** write failed and is a **subset of `skipped`**, which also carries a join row or a staging state that would not write: `processed` plus `rejected` plus `duplicates` plus `errors` is the number of rows a batch carried, and `failRecord()` is the one method that increments it. **`writeRunSummary()` writes no property**: it validates the provenance, records the `run_summary` event and answers the counters with a `logged` flag. **`markRunComplete()` is the only property write**, stamping the source's marker inside `x_bst_startuptrk.ingestion.last_run_provenance` through `AppProperties.completeRun()`, reading it back and reporting `verified`; it is called only once every one of a run's final checks has passed, so a marker is evidence of a run that finished cleanly rather than of one that started. `reference(kind, token)` and `ordinal(kind)` are the two correlation forms — the first names a platform record, the second a per-run arrival ordinal — and both are computed from nothing the record contains. | Both ingestion flows, which inject their own instance into `IngestionMapper.useLogger()` so mapper and flow share one set of counters. **Publication is a separate step**: `IngestionLogger` writes each event to the application log, `syslog`, subject to the severity threshold, and *buffers* the same events. Step 8 of each flow renders `drainEvents()` into one `key="value"` block and a **Utilities → Log action** writes it to the **flow execution log**, the `sys_flow_log` records reachable from the flow's **Executions** view. That surface is not subject to the severity threshold and is retained with the execution, which is why it — and not `syslog` — is what success criterion 4's evidence is read from. |
| `RateLimitService` | Per-caller accounting against `x_bst_startuptrk_rate_limit_counter` under a unique composite window key, with an **atomic** counter increment, a read-back of the window total by aggregate `SUM`, bounded retry on a lost insert race, duplicate coalescing and a fail-closed persistence policy, plus construction of the 429 body with the computed `retry_after`. Exposes `windowKey()`, `consume()`, `retryAfter()`, `body()`, `reject()` and `prune()`. | All 31 REST operations, and the **Prune rate limit counters** scheduled job. |
| `RestResponseBuilder` | The four-member pagination envelope carrying an **exact** `total_count`, the per-field read gate that omits denied keys, the **role-gated** aggregate count and its denial, the in-script role guard, the JSON media-type guard, and the 400, 403, 404, 415 and 500 bodies. Exposes `serialize()`, `canRead()`, `valueOf()`, `page()`, `countState()`, `rejectDeniedCount()`, `countWith()`, `countByGroup()`, `hasAnyAppRole()`, `forbidden()`, `rejectUnauthorisedRead()`, `rejectUnauthorisedWrite()`, `bodyMediaType()`, `unsupportedMediaType()`, `rejectNonJsonBody()`, `notFound()`, `badRequest()`, `serverError()` and `errorId()`. `page()` takes the rows, the total, the limit and the offset — there is no fifth argument and no fifth envelope member. `countState()` answers `{ total, denied }`, and its gate is `hasAnyAppRole()` — three `gs.hasRole()` tests — rather than a `GlideRecordSecure.canRead()` probe, because `canRead()` on an unpositioned secured record does not answer a table-level question; the reasoning and the invariant that licenses the role test are in [`./access-control.md`](./access-control.md). `rejectDeniedCount()` turns a denial into the `403` and answers whether it wrote one, so each list operation returns immediately when it does. `countWith()` is the widget-facing convenience form: it answers a bare number and returns `0` on a denial, which is safe **only** because no widget renders a total to a caller who was refused the table — a REST operation must use `countState()` with `rejectDeniedCount()` instead. | All 31 REST operations, and every widget server script. |
| `RestQueryHelper` | Parses, bounds and validates request parameters, path identifiers and create and update body values, including the page-depth ceiling, the per-field length ceiling applied before anything truncates, the `https`-only URL allowlist, the email allowlist and real calendar-date checking. Exposes `getLimit()`, `getOffset()`, `getTextParam()`, `getSysIdParam()`, `getChoiceParam()`, `getPathSysId()`, `isCalendarDate()`, `isSysId()`, `isHttpsUrl()`, `isEmailAddress()`, `validateBody()` and `referenceExists()`. `getOffset()` **refuses** a negative or non-numeric `sysparm_offset` with a `400` rather than resolving it to `0`, and returns `{ ok, value, error }` so the operation can emit the exact message. `isHttpsUrl()` and `isEmailAddress()` expose the same regular expressions and the same 255- and 254-character limits `validateBody()` applies, so the ingestion boundary and the REST boundary cannot diverge on what a valid URL or address is. `isCalendarDate()` has a second caller outside the REST layer: `IngestionMapper.calendar()` resolves this class so the Gregorian leap-year rule has one home rather than two copies. | **All 31 REST operations construct one.** The seven list operations use it for pagination and filter parameters; the 19 operations that carry a path identifier — the 18 `{id}` operations plus the nested executives sub-resource — use it to validate that identifier; the 12 create and update operations use it to validate the request body. The three counts overlap: each `PUT` is in both the second group and the third. |
| `AppProperties` | Typed accessors for all **eleven** system properties, plus the run-state marker API the two flows lease and stamp. **`getSourceMode()` fails closed**: the stored value is trimmed and lower-cased, only the token `live` selects the live path, an absent or blank property resolves to `fallback` silently, and any other value resolves to `fallback` and is reported in one line naming what was refused. Exposes `get()`, `getInt()`, `getBoundedInt()`, `getCadenceHours()`, `getSourceMode()`, `readRunMarkers()`, `acquireRunLease()`, `completeRun()`, `releaseRunLease()`, `getLastRunProvenance()`, `getRunProvenance()`, `getLastSuccessAt()`, `getDefaultLimit()`, `getMaxLimit()`, `getRateLimitRequests()`, `getRateLimitWindowSeconds()`, `getInclusionLocationTokens()`, `providerBaseUrl()`, `providerBaseUrlState()`, `getCrunchbaseBaseUrl()`, `getLinkedinBaseUrl()`, `getLinkedinApiVersion()`, `getLoggingLevel()`, `normaliseSeverity()`, `isLogLevelEnabled()`, `normaliseText()`, `safeText()` and `fingerprint()`. **`normaliseText(value)` is the single text-normalisation definition** — the two character classes and the two actions of [Two character classes, two actions](#two-character-classes-two-actions) — and it is what `RestQueryHelper._normalise()`, `IngestionMapper._string()`, the `Trim and validate startup` rule and `safeText()` itself all read their text through, so a value written through the REST boundary, a value written by an ingestion run and a value typed into a form are stored in one form and compare equal. **Three further members are the diagnostic and allowlist primitives every other component routes through**: `safeText(value, limit)` is the **single** sanitiser — it neutralises the characters that would let a value forge a `key="value"` log field or a line break, caps the result and marks a capped value `...(truncated)`; `fingerprint(value)` answers eight hexadecimal characters that correlate two occurrences of one value without disclosing it; and `providerBaseUrlState(sourceSystem)` answers `{ allowed, reason, effective, origin }` against the pinned provider origin, with `providerBaseUrl()` the accessor that returns the allowlisted value or the pinned fallback. A component that re-implements any of the three is a second copy of a security decision. `normaliseSeverity()` is the **single** unknown-severity policy — an unrecognised severity resolves to `error`, so an event is never lost by being silently downgraded below the threshold — and both `isLogLevelEnabled()` and `IngestionLogger` route through it. **`getLinkedinApiVersion()` reads no property**: it returns the class constant `LINKEDIN_API_VERSION`, shipped at `202606`. **The per-source run state is one property, not two.** `x_bst_startuptrk.ingestion.last_run_provenance` holds a semicolon-joined set of `source=provenance\|state\|stamp\|run` markers, one per source; `readRunMarkers()` parses it, `acquireRunLease()` takes a source's lease with a compare-and-set so two executions of one flow cannot run concurrently, `completeRun()` stamps the marker once a run's final checks have passed, and `releaseRunLease()` gives the lease back when they have not. `getLastSuccessAt(source)` answers the stamp of a **succeeded** marker and the empty string otherwise, which is what the cadence guard compares against, and it is a property rather than a log record so the cadence is unaffected by the severity threshold and by log retention. There is no `setLastSuccessAt()`: the run markers are written only by `acquireRunLease()`, `completeRun()` and `releaseRunLease()`. | Every component of the application — the REST operations by way of `RestQueryHelper` and `RateLimitService`, `StartupSearchService`, `IngestionMapper`, `IngestionLogger`, both flows and the one scheduled job. Nothing reads a property ad hoc. |

**Four members of `IngestionMapper` matter to a caller beyond the two entry points.** `findExistingByKey()` is the **natural-key lookup every write performs first**, for all six record types, which is what makes a recurring run update the record it wrote before rather than insert another. `resolveStartupKey()` resolves a child's parent on the **composite** key — name plus headquarters — the same pair the de-duplication enforces. `expandRows()` is the seam a live batch must pass through: it copies each typed envelope's `record_type` onto every source object it unwraps and orders the batch so a referenced record is written before its referrer, and a batch handed straight to `prepareOne()` without it is rejected in full. `upsert()` returns `{ ok, reason, sys_id, created, links }`, and the `links` member — `{ linked, removed, kept, failed, reconciled, converged, recalculated }` — is what lets a caller report a round that was written while some of its participant links were not. `claimStagingRows()` claims each `pending` staging row with a guarded conditional update and then compares the owner it reads back, so two overlapping runs cannot both process a row; `ingestStaging()` claims every row it is about to read, and `writeStagingState()` refuses to settle a row whose `import_run` names another run. **Both staging reads are bounded at `STAGING_BATCH_LIMIT` — `200` rows — so a run's cost follows the batch size and not the queue depth**; a run that filled its batch returns a `claim_batch_bounded` note and the remainder stays pending for the next run, which the `import_state` filter picks up without a cursor.

`resolveStartupKey()`, `resolveInvestor()`, `findExistingByKey()`, `findExistingStartup()` and `findExistingInvestor()` each answer `{ ok, sys_id, matches, reason }` rather than a bare identifier, because each resolves only on exactly one match and has to report which failure mode it hit — no match, an ambiguous key, or a candidate set that exceeded its bound. **None of them ever picks a candidate.** There is no `applyDefaults()`: a column default is declared once in the dictionary and applied by the platform on insert. **The staging claim is a lease on `import_run`, not a fifth `import_state` value**: `claimStagingRows()` writes `run:<run identifier>` on each row it takes and reads it back, `import_state` stays `pending` until `writeStagingState()` settles it, and `leaseHolder()` is what tells a lease apart from a CSV batch token. The four `import_state` values are the only ones the dictionary carries.

Each class also carries private helpers prefixed with an underscore. Those are implementation detail and no call site outside the class may use them.

### Addressing convention

A Script Include is referenced as `x_bst_startuptrk.<ClassName>` from outside the scope and by its bare class name within it. Inside the application — in an operation script, a business rule, a flow script step or a widget server script — the call is `new RestResponseBuilder()`. From outside the scope it is `new x_bst_startuptrk.RestResponseBuilder()`. Each record's `api_name` is the qualified form.

### Privilege

**None of the eight is client-callable, and none runs with elevated privilege.** Every record carries `client_callable` false and `package_private` access. No class may be reached from a client script, and no class may read a premium-gated column through an unsecured path and return it to a caller. Eight is the whole inventory, matching Agent Action Plan section 0.4.5.

Three of the eight do read through the unsecured `GlideRecord`, because their work is not performed on a caller's behalf: `RateLimitService` maintains counter rows the caller must never see, `InvestorPortfolioService` derives a stored aggregate from rows outside any request, and `IngestionMapper` writes ingested records under the flow's own identity. **None of the three returns a record or a field value to a REST response or a widget.** Which classes may use which read path, and why, is tabulated in [`./access-control.md`](./access-control.md).

### Rename impact

Renaming any class in the table above requires updating every call site listed in its **Called by** column. Because the Automated Test Framework suites encode class names, method names and resource paths, the rename must also propagate into the suite steps [`./manual-build/05-atf-test-suites.md`](./manual-build/05-atf-test-suites.md) specifies, whose own **Rename impact** table lists what it encodes.


**Two `AppProperties` members are referenced from outside the class and belong in this list.** `SANITISERS` is the one home of the redaction pattern set, reached by every caller through `safeText()` rather than directly. `PROVIDER_ORIGINS` is the provider origin allowlist, and it is read **directly** by the live step of each ingestion flow: each derives its own `APPROVED_ROOT` and `APPROVED_HOST` from the entry for its source system rather than restating the pinned origin as a literal, so renaming the member or changing an entry's shape breaks both step scripts as well as this class. Moving an entry's `prefix` or `origin` is a deliberate act with immediate effect on what each flow will call — which is the point of keeping it in one place.
## System properties

Eleven `sys_properties` records externalise the application's configuration — the eleven AAP section 0.4.7 specifies, and no others. All keys are fully qualified with the `x_bst_startuptrk.` prefix.

**Every one of the eleven carries `read_roles` and `write_roles` of `x_bst_startuptrk.admin`, and no other role.** The policy is uniform: there is no property that a non-administrative caller may read, and none that a non-administrative caller may write. That is deliberate — a configuration value is an administrative control even when the value itself is unremarkable, and a caller who can read the rate-limit budget or the inclusion tokens learns how the application decides what to serve. The **Read by** column below names the Script Include that reads each property *on the application's own behalf*; a scoped Script Include runs inside the scope and is not subject to the role check that governs an external caller.

| Key | Type | Shipped value | Read by |
| --- | --- | --- | --- |
| `x_bst_startuptrk.ingestion.cadence_hours` | Integer, `x_bst_startuptrk.admin` read and write | `24` | `AppProperties`, which clamps the value to the range 6 to 48; read by the cadence guard that is the first action of both ingestion flows. |
| `x_bst_startuptrk.ingestion.source_mode` | Choice — `live` or `fallback`, `x_bst_startuptrk.admin` read and write | `live` | `AppProperties`; read by both ingestion flows to decide whether to attempt the live call or go straight to the staging table. |
| `x_bst_startuptrk.ingestion.last_run_provenance` | String, `x_bst_startuptrk.admin` read and write | **empty** | `AppProperties`; written **only** by its own three run-state methods — `acquireRunLease()`, which stamps a source `running`, `completeRun()`, which stamps it `succeeded`, and `releaseRun()`, which removes that source's entry — and read by each flow's cadence guard and by every provenance report. `IngestionLogger.markRunComplete()` reaches it through `completeRun()`; **`IngestionLogger.writeRunSummary()` writes no property at all**, so a run summary in the log is not evidence that the marker was stamped. It ships **empty**, and a non-empty value therefore means at least one run has claimed a source on this instance. Once written it holds one `source=provenance|state|stamp|run` entry per source, entries joined by `;` and ordered `crunchbase` then `linkedin`, where `state` is `running` or `succeeded` and `stamp` is the marker's timestamp; an entry that is not well formed, or that names neither source, is discarded on read rather than half-parsed. A bare `live` or `fallback` value — the pre-marker format — is read as a `legacy` provenance carrying no source, no state and no run. Every marker write re-reads the property inside the write, merges the **other** source's entry forward from that read rather than from the caller's snapshot, and then reads its own entry back; a mismatch reapplies the merge once and is logged if it survives, so one flow's write can never erase the other's. Provenance is validated against `live` or `fallback` before any of this: a summary carrying anything else is logged as `run_summary_provenance_invalid` and a completion carrying anything else as `run_completion_provenance_invalid`, and in both cases the property is left untouched; a refused completion is logged as `run_completion_refused` carrying the refusal reason. **This is the durable cadence and provenance state: nothing reads the application log to establish either.** |
| `x_bst_startuptrk.rest.default_limit` | Integer, `x_bst_startuptrk.admin` read and write | `20` | `AppProperties`; read by `RestQueryHelper.getLimit()` as the fallback page size. A value that is not a whole decimal integer of 1 or more resolves to the shipped `20`, and a value above `PAGE_SIZE_CEILING` — `50` — resolves to `50`, so a request carrying no pagination parameter can never be answered with more than fifty records. |
| `x_bst_startuptrk.rest.max_limit` | Integer, `x_bst_startuptrk.admin` read and write | `50` | `AppProperties`; read by `RestQueryHelper.getLimit()` as the clamp ceiling. A value that is not a whole decimal integer of 1 or more resolves to the shipped `50`, and a value above `PAGE_SIZE_CEILING` — `50` — resolves to `50`. **This value is the ceiling unconditionally**: a `rest.default_limit` set above it does not widen a page, because the default is clamped down to this maximum, so a misconfigured default serves fewer rows rather than more. The property can narrow a page and cannot widen one: the largest page the API serves is fifty records whatever this property holds. |
| `x_bst_startuptrk.rest.rate_limit_requests` | Integer, `x_bst_startuptrk.admin` read and write | `100` | `AppProperties`; read by `RateLimitService.consume()` as the per-window budget. A value that is not a whole decimal integer of 1 or more resolves to the shipped `100`. |
| `x_bst_startuptrk.rest.rate_limit_window_seconds` | Integer, `x_bst_startuptrk.admin` read and write | `60` | `AppProperties`; read by `RateLimitService` for the window length and the `retry_after` computation, and by the pruning job as its retention. Windows are aligned buckets, so a row whose `window_start` is older than one window length is never the live window; that is the pruning boundary. A value that is not a whole decimal integer of 1 or more resolves to the shipped `60`. |
| `x_bst_startuptrk.inclusion.location_tokens` | String — comma-separated tokens, `x_bst_startuptrk.admin` read and write | `Boston,Cambridge, MA` | `AppProperties`; read by `StartupSearchService.buildPlan()`, which turns each token into one `CONTAINS` condition on `headquarters_location`. **A two-letter upper-case piece rejoins the piece before it into one token only when it was written with whitespace after the comma** — which is exactly how the shipped default writes `Cambridge, MA`, yielding the two tokens `Boston` and `Cambridge, MA`. Written without that space, `Boston,NY` is two tokens, `Boston` and `NY`; written with it, `Boston, NY` is the single token `Boston, NY`. The space is therefore significant, and it is the only thing that distinguishes a state suffix from a token of its own. A value that yields no token at all falls back to `Boston` and `Cambridge, MA`. |
| `x_bst_startuptrk.crunchbase.base_url` | String | `https://api.crunchbase.com/api/v4` | `AppProperties.getCrunchbaseBaseUrl()`; read by the Crunchbase ingestion flow's REST step. This is the base of the **current** Crunchbase Data API v4. It is non-secret endpoint configuration and carries no user key: the key lives only in the credential bound to `x_bst_startuptrk.crunchbase_api` and is sent as the `X-cb-user-key` header. |
| `x_bst_startuptrk.linkedin.base_url` | String | `https://api.linkedin.com/rest` | `AppProperties.getLinkedinBaseUrl()`; read by the LinkedIn ingestion flow's REST step **only when the live path has been enabled**. The LinkedIn live path is contract-gated and ships disabled — no approved LinkedIn product grants this application the company-employee, member-profile or public job reads its design assumed. See [`./gaps-and-flags.md`](./gaps-and-flags.md). |
| `x_bst_startuptrk.logging.level` | Choice — `debug`, `info`, `warn` or `error`, `x_bst_startuptrk.admin` read and write | `info` | `AppProperties.getLoggingLevel()` and `AppProperties.isLogLevelEnabled()`, the single severity gate. `IngestionLogger` routes every system-log write through it and suppresses any write below the configured threshold; an event below the threshold is still buffered for the flow's Log step, so the flow execution log carries every event regardless. `RestResponseBuilder.serverError()` also consults the gate before writing its diagnostics, which are written at `error` and are therefore permitted at every configured level. The skipped, rejected and processed counters, the response statuses and the response bodies are unaffected. A value outside the four choices resolves to `info`. |

**The base-URL properties are the single endpoint authority.** `x_bst_startuptrk.crunchbase.base_url` and `x_bst_startuptrk.linkedin.base_url` are where every outbound endpoint this application calls is defined, and both ingestion flows construct their request URLs as `AppProperties.getCrunchbaseBaseUrl()` or `AppProperties.getLinkedinBaseUrl()` concatenated with the resource path. **A flow must never take its base URL from anywhere else** — not from a literal in a script step, not from a flow input, and not from the Connection record behind its credential alias.

### The provider origin allowlist

**The base-URL properties are authoritative, and they are also administrator-editable — so they are not trusted.** Every read of either one passes through a provider origin allowlist held in code, and the value a flow actually calls is the allowlist's decision rather than the property's contents.

| Member of `AppProperties` | Returns |
| --- | --- |
| `providerBaseUrl(sourceSystem)` | The URL to call: the configured property value when the allowlist accepts it, otherwise the **pinned origin** for that source. It cannot return anything else. |
| `providerBaseUrlState(sourceSystem)` | `{ allowed, reason, effective, origin }` — the same decision with its reason exposed, so a caller can report a refusal without disclosing what was refused. |
| `getCrunchbaseBaseUrl()` and `getLinkedinBaseUrl()` | Thin accessors that delegate to `providerBaseUrl('crunchbase')` and `providerBaseUrl('linkedin')`. Neither reads the property directly. |
| `PROVIDER_ORIGINS` | The allowlist itself: host, path prefix and pinned fallback per source. It is a Script Include member, so it travels in the Update Set and changing it is a scoped code change — not a property edit an operator can make at run time. |

A value is accepted only when the source system is known, the value is non-empty, it parses as an absolute URL, its scheme is `https`, its authority carries no `user:password@` prefix, its port is the scheme default, its host is exactly the allowed host, and its path is exactly the allowed prefix. Each failure has its own closed reason — `unknown_source`, `empty`, `malformed`, `scheme_not_https`, `userinfo_present`, `port_not_default`, `host_not_allowed`, `path_not_allowed` — and **no code path ever logs or returns the refused value**, because a base URL is somewhere a credential can hide: a key in a query string is a credential in a URL.

**Why this matters more than it looks.** A credential travels to whatever host the endpoint names, and both places that name a host are editable rows. Without the allowlist, editing one row would send the Crunchbase API key, or a LinkedIn access token, to a host of the editor's choosing — and every alias, connection and credential would still resolve, so nothing would look wrong. With it, a refused value degrades to the real provider, the refusal is reported as `endpoint_refused` with its reason, and a connection record that has drifted from the property is reported as `connection_url_divergent`. Both flows apply the check **before** any credential is attached to a request; the construction is in [3.5a of guide 02](./manual-build/02-flow-crunchbase-ingestion.md#35a--the-provider-origin-allowlist-and-why-the-endpoint-is-fixed-first) and [3.9 of guide 03](./manual-build/03-flow-linkedin-ingestion.md#39--the-provider-origin-allowlist-and-why-the-endpoint-is-fixed-first).

The Connection record does carry a URL field, because the platform requires one on a connection, so **two places on the instance name the same host**. The property is authoritative and the connection field is a **required mirror** of it. Guide 01 checks them for equality when the alias is verified, and guides 02 and 03 re-check before their flows are saved; the procedure is at [Step 1.3](./manual-build/01-connection-credential-aliases.md#step-13--build-or-confirm-the-connection-record-fields) and [Step 2.3](./manual-build/01-connection-credential-aliases.md#step-23--build-or-confirm-the-connection-record-fields). A divergence between them is a configuration defect, not a choice: it means the credential is being presented to one host while the flow addresses another.

**No property holds a secret.** No API key, client identifier, client secret, refresh token or password value is stored in any of the eleven, and the two base-URL properties are non-secret endpoint configuration. Credentials live only in the two Connection & Credential Aliases, `x_bst_startuptrk.crunchbase_api` and `x_bst_startuptrk.linkedin_oauth`, which are referenced by name and are built on the instance rather than shipped; see [`./manual-build/01-connection-credential-aliases.md`](./manual-build/01-connection-credential-aliases.md).


### Inventory against the planned counts

The delivered inventory matches the Agent Action Plan exactly. The plan governs; where the delivery once exceeded it, the delivery has been corrected to it rather than the figure being restated.

| Inventory | AAP figure | Shipped | Status |
| --- | --- | --- | --- |
| Script Includes | 8, AAP section 0.4.5 | **8** | Matches. `StartupSearchService`, `InvestorPortfolioService`, `IngestionMapper`, `IngestionLogger`, `RateLimitService`, `RestResponseBuilder`, `RestQueryHelper`, `AppProperties`. |
| Scoped system properties | 11, AAP section 0.4.7 | **11** | Matches. The eleven keys tabulated above, and no others. |
| Scheduled jobs | 1, AAP section 0.4.2 | **1** | Matches. **Prune rate limit counters**. |
| Business rules | 3, AAP section 0.4.2 | **3** | Matches. |
| REST definition and operations | 1 and 31, AAP section 0.4.6 | **1 and 31** | Matches. |
| Declared indexes | 5, AAP section 0.4.2 | 13 | Eight added for predicates the application issues on every ingested row or every profile pane — the six natural keys, which take seven indexes because the `funding_round` key is an ordered pair of alternatives, and the news-by-startup read — and one dead index removed. The full set, each tied to its predicate, is in [`./data-model.md`](./data-model.md) |
| Scripted REST definitions and operations | 1 and 31, AAP section 0.4.6 | **1** and **31** | [Operation roll-up](#operation-roll-up) |
| Roles | 3, AAP section 0.4.4 | **3** | [`./access-control.md`](./access-control.md) |

**No staging-table privacy lifecycle is shipped**, and the inventory figures above are the plan's exact figures. The staging table's retention and the servicing of an erasure request are **operator-owned procedures** rather than shipped artifacts, specified in [`./data-model.md`](./data-model.md) and [`./manual-build/06-staging-table-csv-import.md`](./manual-build/06-staging-table-csv-import.md). The removal and its reasoning are recorded in [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md).

Two consequences of holding the property count at eleven are worth reading off, because each replaced something a larger inventory would have carried:

| # | Consequence |
| --- | --- |
| 1 | **The LinkedIn API version is a code constant, not a property.** `AppProperties.LINKEDIN_API_VERSION` is `202606`. Correcting a retired version is a scoped-code change travelling in an Update Set, which is a heavier operation than a property edit and is stated as such in [`./manual-build/01-connection-credential-aliases.md`](./manual-build/01-connection-credential-aliases.md). |
| 2 | **The per-source run state is one property, not two.** `x_bst_startuptrk.ingestion.last_run_provenance` holds a `source=provenance\|state\|stamp\|run` marker for each source, joined by semicolons, so the two flows keep independent cadences and independent leases inside a single key. The parse, lease and stamp API is on `AppProperties`; the format is stated in its row of [The Script Include call graph](#the-script-include-call-graph). |

A third consequence is a stated limitation rather than a substitution: **no retention, minimisation or data-subject erasure capability is delivered**, because it would have required a ninth Script Include, further properties and a second scheduled job. What bounds the staging and counter tables instead is in [`./data-model.md`](./data-model.md), and the limitation is flagged in [`./gaps-and-flags.md`](./gaps-and-flags.md).

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
| 1 | Request parameters `page` and `per_page`, `src/backend/routes/startup.py:L12-L13` | Request parameters `sysparm_limit` and `sysparm_offset` | [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md) |
| 2 | Response envelope `{'startups', 'total', 'pages', 'page', 'per_page'}`, `src/backend/routes/startup.py:L31-L37` | Response envelope `result` array plus `total_count` plus the `limit` and `offset` echoes | [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md) |
| 3 | Logical base path `API_BASE_URL = '/api/v1'`, `src/shared/constants.ts:L2` | Physical base path `/api/x_bst_startuptrk/v1/` | [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md) |
| 4 | Maximum page size `MAX_RESULTS_PER_PAGE = 50`, `src/shared/constants.ts:L5` | Property `x_bst_startuptrk.rest.max_limit`, shipped value `50` — value carried forward | [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md) |
| 5 | Default page size `DEFAULT_RESULTS_PER_PAGE = 20`, `src/shared/constants.ts:L8` | Property `x_bst_startuptrk.rest.default_limit`, shipped value `20` — value carried forward | [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md) |
| 6 | Per-record success bodies returning the record dictionary directly, and a `{'message': ...}` body on delete, `src/backend/routes/startup.py:L121` | The serialised record object on read, create and update; **no body** on delete, with `HTTP 204` | [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md) |

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
| — | — | `location` on `GET /startups`, `type` on `GET /investors`, `department` on `GET /jobs`, `source` on `GET /news`, `startup`, `round_type` and `source_url` on `GET /funding-rounds`, `startup` and `name` on `GET /founders` — no legacy counterpart |

This section is the API portion of the bidirectional matrix that [`../../docs/decisions/TRACEABILITY_MATRIX.md`](../../docs/decisions/TRACEABILITY_MATRIX.md) is to carry.

## Related documents

- [`../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml`](../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml) — the authoritative REST definition, operation, Script Include and property records this document transcribes
- [`./data-model.md`](./data-model.md) — the ten tables field by field, the choice values, the inclusion-criteria predicate and the `portfolio_count` derivation
- [`./access-control.md`](./access-control.md) — the five ACL layers including the two `REST_Endpoint` controls bound here, the three roles, the seven premium fields, the omitted-not-nulled rule, the table access posture and the secured read and count paths this contract depends on
- [`./gaps-and-flags.md`](./gaps-and-flags.md) — requirements with no clean platform equivalent, including the namespace segment in the base path and the exclusion of automated NewsArticle ingestion
- [`./validation-gates.md`](./validation-gates.md) — the machine-checkable post-commit gates run after the Update Set commits
- [`../sample-data/README.md`](../sample-data/README.md) — the fallback dataset and the ingestion-path cleaning guarantees that the create and update operations do **not** apply
- [`../scripts/validate_update_set_xml.py`](../scripts/validate_update_set_xml.py) — the two-level well-formedness validator for the Update Set this document transcribes
- [`./validation-checklist.md`](./validation-checklist.md) — the five success criteria, criterion 3 being the pass condition for the six per-resource REST tests
- [`./manual-build/01-connection-credential-aliases.md`](./manual-build/01-connection-credential-aliases.md) — how the two Connection & Credential Aliases are built and bound; they are the only home for credential material
- [`./manual-build/05-atf-test-suites.md`](./manual-build/05-atf-test-suites.md) — the REST resource tests and how the 429 response is made deterministic
- [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md) — the single source of truth for every decision, alternative and risk behind this contract
- [`../../docs/decisions/TRACEABILITY_MATRIX.md`](../../docs/decisions/TRACEABILITY_MATRIX.md) — the bidirectional source-to-target matrix this section feeds
- [`../../docs/review/CRITICAL_DECISIONS.md`](../../docs/review/CRITICAL_DECISIONS.md) — the five highest-risk decisions, including **entry 3**, risk High, reviewer persona API/Integration, which is the entry this document is the artifact for — entry 3 on credential handling and entry 5 on the live ingestion path
