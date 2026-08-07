# API reference — `x_bst_startuptrk`

This document is the REST contract reference for the ServiceNow scoped application `x_bst_startuptrk`. It states the one Scripted REST API definition, all 31 operations across six logical resources, the pagination contract, the three error contracts, the Script Include call graph that doubles as a rename-impact list, and the eleven system properties the API layer reads. Every operation is enumerated individually with its method, its path template, what it returns and its success status; every Script Include and every property is likewise listed one by one.

The Update Set XML at [`../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml`](../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml) is **authoritative** over this document. Everything below is a transcription of the one `sys_ws_definition` record, the 31 `sys_ws_operation` records, the 8 `sys_script_include` records and the 11 `sys_properties` records that file carries. Where this document and those records disagree about a path, a method, a parameter name, a response member, a status code, a class name or a property key, the records are correct and this document is corrected to match them, never the reverse.

The table names, column names and premium markers used below are the ones established in [`./data-model.md`](./data-model.md). The field-level read gate applied to every response is the one specified in [`./access-control.md`](./access-control.md); this document states where that gate applies and does not restate the access-control scheme.

This document carries no rationale. Every decision behind this contract, every alternative considered and every risk it carries is recorded in [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md), which is the single source of truth for "why".

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

### Base path

A scoped Scripted REST API always carries its namespace segment in its base path. The logical base path `/api/v1/` therefore resolves **physically** to `/api/x_bst_startuptrk/v1/`.

**Call the physical path.** Every request goes to `https://<instance>.service-now.com/api/x_bst_startuptrk/v1/<resource>`. The logical form is not served and does not resolve. No consumer may be written against it. The point is flagged in [`./gaps-and-flags.md`](./gaps-and-flags.md) so that no integration is built on the logical form.

The full request line for the first resource:

```text
GET https://<instance>.service-now.com/api/x_bst_startuptrk/v1/startups?sysparm_limit=20&sysparm_offset=0
```

Every path template in this document is written relative to that base path. `GET /startups` means `GET /api/x_bst_startuptrk/v1/startups`.

### Authentication and authorisation

Every one of the 31 operations requires **both** authentication and access-control authorisation. Each `sys_ws_operation` record carries `requires_authentication` true and `requires_acl_authorization` true. An unauthenticated request is rejected by the platform before the operation script runs.

Three enforcement rules bind every operation, and they are specified in [`./access-control.md`](./access-control.md):

- **Secured read path.** Every caller-facing read uses `GlideRecordSecure`. No operation reads through the unsecured `GlideRecord`, and no Script Include reads a premium-gated column on a caller's behalf and returns it.
- **Per-field read gate.** Response serialisation tests each field with an element-level read check and **omits the key entirely** when the check fails. A denied premium field is absent from the response object; it does not appear with a null, an empty string or a placeholder.
- **No bypass.** None of the eight Script Includes is client-callable and none runs with elevated privilege, so no operation can reach a gated field through an elevated helper.

The seven premium-gated fields, their gating roles and the twenty-one role-by-field outcomes are tabulated in [`./access-control.md`](./access-control.md) and are not restated here. This document marks, on each resource representation, which of its fields are gated.

### Content type

Requests and responses are JSON. A request carrying a body sends `Content-Type: application/json`; every response body is `application/json`. The only response without a body is `HTTP 204` on a successful delete.

### Deviations from the legacy contract

The contract stated in this document differs from the legacy Flask contract in three respects, and consumers discover the differences here:

1. The **paths** differ. The physical base path is `/api/x_bst_startuptrk/v1/`, not `/api/v1/`.
2. The **pagination parameter names** differ. They are `sysparm_limit` and `sysparm_offset`, not `page` and `per_page`.
3. The **response envelope key** differs. The count member is `total_count`, not `total`.

**No compatibility shim, alias or legacy-contract layer exists.** No operation accepts `page` or `per_page`, no response carries `total`, and no route serves the logical `/api/v1/` form. The legacy forms, their exact source citations and the target forms they map to are tabulated under [Legacy provenance](#legacy-provenance). Each change is recorded as a row in [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md).

## The pagination contract

Every list operation in this API takes the same two request parameters and returns the same envelope. There are seven list operations: the six resource list operations and the nested executives sub-resource.

### Request parameters

| Parameter | Meaning | Type | Accepted on |
| --- | --- | --- | --- |
| `sysparm_limit` | Page size — the maximum number of records the response array carries. | Integer | Every list operation |
| `sysparm_offset` | Zero-based starting offset into the ordered result set. `0` returns the first page. | Integer | Every list operation |

Both parameters are optional. Neither is accepted on a read-one, create, update or delete operation, where a single record is addressed by its path parameter.

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
| Non-numeric | `0` |
| Negative | `0` |
| Zero or positive | The supplied value |

An out-of-range value never produces an error. The applied limit and offset are echoed in the response, so a consumer always reads back what the API actually used.

### Response envelope

`RestResponseBuilder` builds every list response. The envelope has exactly four members.

| Member | Type | Content |
| --- | --- | --- |
| `result` | Array of objects | The page of records, each serialised through the per-field read gate. |
| `total_count` | Integer | The number of records matching the query, across all pages. |
| `limit` | Integer | The applied limit, after the bounds above. |
| `offset` | Integer | The applied offset, after the bounds above. |

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

`total_count` is the number of records matching the operation's query, independent of `limit` and `offset`. It is produced by an aggregate count over the same encoded query used to build the page, not by iterating the secured result set.

**Invariant.** All seven entity tables grant table-level read to all three roles, and the role difference is at field level only, so record-level visibility is identical for `x_bst_startuptrk.admin`, `x_bst_startuptrk.premium_user` and `x_bst_startuptrk.user`. That is what makes an aggregate count a correct `total_count` for every caller. The invariant is stated in [`./access-control.md`](./access-control.md).

Operational consequence: if a record-level restriction is ever introduced on any of the seven tables, an aggregate count would over-report for restricted callers and must be replaced by a secured count.

### The inclusion criteria and the count

Where the startup inclusion criteria apply to a list operation, they are applied **identically to the result set and to `total_count`**. Both are built from one encoded query string produced by a single call to `StartupSearchService.buildQuery()`; applying the criteria to one and not the other makes the count disagree with the page contents. The predicate itself — `active` true and `headquarters_location` containing a configured location token — is specified in [`./data-model.md`](./data-model.md) and is not restated here.

## Resources

Six logical resources. Each section lists every operation on that resource, then gives the resource's JSON representation and marks the premium-gated fields. A premium-gated field is **omitted from the response object** for a caller the field-level read ACL denies; the key is absent, never present with a null.

Path templates are relative to the physical base path `/api/x_bst_startuptrk/v1/`. `{id}` is the record's `sys_id`.

### `/startups`

The Startup resource over `x_bst_startuptrk_startup`. Five operations.

| Method | Path template | Description | Success status |
| --- | --- | --- | --- |
| `GET` | `/startups` | Lists and searches startups. Returns the paginated envelope carrying a page of startup objects, `total_count`, `limit` and `offset`. | `200` |
| `GET` | `/startups/{id}` | Reads one startup by `sys_id`. Returns a single startup object. | `200` |
| `POST` | `/startups` | Creates a startup from the request body. Returns the created startup object as read back through the secured path. | `201` |
| `PUT` | `/startups/{id}` | Updates the named startup with the supplied fields. Returns the updated startup object. | `200` |
| `DELETE` | `/startups/{id}` | Deletes the named startup. Returns no body. | `204` |

`GET /startups` applies the startup inclusion criteria for unauthenticated and non-administrative callers. A caller holding `x_bst_startuptrk.admin`, or the platform administrator role, receives the unfiltered set; every other caller receives the filtered set. Records failing the criteria remain in the table and are reachable through `GET /startups/{id}` and through the platform's own list views. The predicate is in [`./data-model.md`](./data-model.md).

`GET /startups` accepts three query filters in addition to the pagination parameters. All three are optional and combine with a logical AND, and with the inclusion criteria where those apply.

| Filter | Column matched | Comparison |
| --- | --- | --- |
| `name` | `name` | Case-insensitive contains |
| `industry` | `industry` | Exact match against a choice value |
| `location` | `headquarters_location` | Case-insensitive contains |

`StartupSearchService` builds the query for both the filters and the inclusion criteria. Results are ordered by `name`.

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
| `GET` | `/founders/{startup_id}/executives` | Lists the Executive records of the startup named by `{startup_id}`, ordered by `name`. Returns the paginated envelope carrying a page of executive objects, `total_count`, `limit` and `offset`. | `200` |

`GET /founders/{startup_id}/executives` is a **nested sub-resource**, and it is how Executive records are served over REST. Executive is not a seventh top-level resource: there is no `/executives` path, and the API surface is six logical resources. `{startup_id}` is the `sys_id` of a startup; an absent `{startup_id}` returns `400`.

`GET /founders` accepts two query filters in addition to the pagination parameters.

| Filter | Column matched | Comparison |
| --- | --- | --- |
| `startup` | `startup` | Exact match against a startup `sys_id` |
| `name` | `name` | Case-insensitive contains |

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

`GET /investors` accepts two query filters in addition to the pagination parameters.

| Filter | Column matched | Comparison |
| --- | --- | --- |
| `name` | `name` | Case-insensitive contains |
| `type` | `type` | Exact match against a choice value |

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

`portfolio_count` is a **derived** integer and is **read-only from the API's perspective**. It is maintained by business rules and is not part of the writable set on `POST` or `PUT`; a value supplied for it in a request body is ignored, and a subsequent read returns the derived value. The derivation — the count of distinct startups reachable from the investor as lead investor or as participating investor, unioned before counting — is specified in [`./data-model.md`](./data-model.md).

### `/funding-rounds`

The FundingRound resource over `x_bst_startuptrk_fundinground`. Five operations. Note the hyphen in the path segment.

| Method | Path template | Description | Success status |
| --- | --- | --- | --- |
| `GET` | `/funding-rounds` | Lists funding rounds. Returns the paginated envelope carrying a page of funding-round objects, `total_count`, `limit` and `offset`. | `200` |
| `GET` | `/funding-rounds/{id}` | Reads one funding round by `sys_id`. Returns a single funding-round object. | `200` |
| `POST` | `/funding-rounds` | Creates a funding round from the request body. Returns the created funding-round object. | `201` |
| `PUT` | `/funding-rounds/{id}` | Updates the named funding round with the supplied fields. Returns the updated funding-round object. | `200` |
| `DELETE` | `/funding-rounds/{id}` | Deletes the named funding round. Returns no body. | `204` |

`GET /funding-rounds` accepts two query filters in addition to the pagination parameters.

| Filter | Column matched | Comparison |
| --- | --- | --- |
| `startup` | `startup` | Exact match against a startup `sys_id` |
| `round_type` | `round_type` | Exact match against a choice value |

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

`participating_investors` is emitted as a **JSON array of investor references assembled from `x_bst_startuptrk_m2m_round_investor`**. The operation reads that join table through the secured path for each round in the page, and emits one array element per linked investor. An empty array means the round has no participating investors recorded. The array is not a writable field: participating investors are maintained as rows of the join table, and the join table is authoritative for them.

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

`GET /jobs` accepts two query filters in addition to the pagination parameters.

| Filter | Column matched | Comparison |
| --- | --- | --- |
| `startup` | `startup` | Exact match against a startup `sys_id` |
| `department` | `department` | Exact match against a choice value |

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

Writes to this resource are **manual entry or CSV import only**. There is no automated NewsArticle ingestion: neither ingestion flow writes `x_bst_startuptrk_newsarticle`, and the fallback dataset carries no NewsArticle file. Records reach the table through the platform form, through this resource's `POST` and `PUT` operations, or through an ad hoc import. The exclusion is recorded in [`./gaps-and-flags.md`](./gaps-and-flags.md).

`GET /news` accepts two query filters in addition to the pagination parameters.

| Filter | Column matched | Comparison |
| --- | --- | --- |
| `startup` | `startup` | Exact match against a startup `sys_id` |
| `source` | `source` | Case-insensitive contains |

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

This roll-up is the operation-count evidence that criterion 3 in [`./validation-checklist.md`](./validation-checklist.md) and the API section of [`../../docs/decisions/TRACEABILITY_MATRIX.md`](../../docs/decisions/TRACEABILITY_MATRIX.md) both resolve against.

## Error contracts

Three response bodies. The two shapes below are fixed by the requirements and are reproduced here exactly; a client may parse them literally.

Every status code this API returns, in one place:

| Status | Meaning | Body |
| --- | --- | --- |
| `200` | A successful list, read or update. | The paginated envelope, or the serialised record object. |
| `201` | A successful create. | The serialised record object, read back through the secured path. |
| `204` | A successful delete. | None. |
| `400` | The request is malformed, or a create or update failed validation. | `{"error": "<message>"}` |
| `403` | The caller is authenticated but the operation's access-control authorisation denies the request. | Supplied by the platform. |
| `404` | The record named by the path parameter does not exist or is not readable by the caller. | `{"error": "<message>"}` |
| `429` | The caller has exhausted its request budget for the current window. | `{"error": "rate_limit_exceeded", "retry_after": 42}` |
| `500` | An unhandled error occurred inside the operation script. | `{"error": "<message>"}` |

### Rate limit — HTTP 429

Body:

```json
{"error": "rate_limit_exceeded", "retry_after": 42}
```

`retry_after` is a whole number of seconds, computed as the window start plus the window length minus the current time. `42` above is an illustrative value; the value returned is the seconds remaining in the caller's current window, with a floor of `1`.

Mechanism. Per-caller fixed-window accounting in the table `x_bst_startuptrk_rate_limit_counter`, maintained by the `RateLimitService` Script Include. One counter row exists per caller, per API resource, per window. `RateLimitService` resolves the current window, increments the row's request count, and rejects the request once the count exceeds the configured budget.

| Property | Shipped value | Role |
| --- | --- | --- |
| `x_bst_startuptrk.rest.rate_limit_requests` | `100` | Requests permitted per caller, per resource, per window. |
| `x_bst_startuptrk.rest.rate_limit_window_seconds` | `60` | Window length in seconds. |

Changing either property changes the limit with no code change. The scheduled job **Prune rate limit counters** runs hourly and deletes counter rows whose window has closed, so the table does not accumulate.

A standard `Retry-After` response header carries the same value as the body's `retry_after` member. The header is additive: it **does not alter the body**, which remains exactly the two members above.

The limit applies to **every one of the six resources**, and to the nested executives sub-resource. Each of the 31 operations calls `RateLimitService` before it does any other work, and accounting is keyed on the resource, so a caller's budget for `/startups` is separate from its budget for `/investors`.

### General failure

Body:

```json
{"error": "<message>"}
```

`<message>` is a human-readable string. The conditions that produce this body, with the status code for each:

| Condition | Status | `<message>` |
| --- | --- | --- |
| The record named by `{id}` does not exist, or is not readable by the caller | `404` | `Record not found` |
| A create or update request carries no body | `400` | `Request body is required` |
| A create request fails validation — a mandatory field is absent, or a choice value is not a member of the column's choice list | `400` | `Record could not be created` |
| An update request fails validation on the same grounds | `400` | `Record could not be updated` |
| The nested executives sub-resource is called without `{startup_id}` | `400` | `startup_id is required` |
| The caller is authenticated but the operation's access-control authorisation denies the request | `403` | Supplied by the platform |

An authorisation denial at the record level and an absent record are both reported as `404` by the operation script, because a record the caller may not read is not returned by the secured read path. A denial of the operation itself is reported as `403` by the platform before the operation script runs. A field-level denial is not an error at all: the field's key is omitted from an otherwise successful response.

### Server error — HTTP 500

Body, the same shape as a general failure:

```json
{"error": "<message>"}
```

`<message>` is the caught error's message. The **stack trace is written to the application log** through `gs.error` under the source `x_bst_startuptrk.RestResponseBuilder`, and is not returned to the caller. No trace, no script name, no line number and no table name beyond the message reaches the response.

This shape is produced by `RestResponseBuilder.serverError()`.

### Uniformity

Every one of the 31 operations wraps its body in error handling that delegates to `RestResponseBuilder` for the 500 shape and to `RateLimitService` for the 429 shape. No operation constructs either body itself, so the contract cannot drift between operations: a change to either shape is a change to one Script Include method.

The 404 and 400 bodies are likewise produced only by `RestResponseBuilder.notFound()` and `RestResponseBuilder.badRequest()`.

How the 429 is made deterministic under test is specified in [`./manual-build/05-atf-test-suites.md`](./manual-build/05-atf-test-suites.md), and the pass condition for the six per-resource REST tests is criterion 3 in [`./validation-checklist.md`](./validation-checklist.md). Neither is restated here.

## The Script Include call graph

Eight `sys_script_include` records carry the application's service layer. This table is the **rename-impact list**: read a row's third column to find every call site a rename touches.

| Class | Responsibility | Called by |
| --- | --- | --- |
| `StartupSearchService` | Builds the inclusion-criteria query and applies the caller's `name`, `industry` and `location` filters. Exposes `buildInclusionQuery()`, `buildFilterQuery()`, `buildQuery()`, `search()` and `appliesInclusion()`. | The `GET /startups` list operation, and the portal search widgets on the Home/Search route. One class serves both surfaces, so the filter cannot drift between them. |
| `InvestorPortfolioService` | The `portfolio_count` derivation, plus a recalculate-all method. Exposes `countPortfolio()`, `recalculate()`, `recalculateMany()` and `recalculateAll()`. | The two portfolio-count business rules — one on `x_bst_startuptrk_fundinground`, one on `x_bst_startuptrk_m2m_round_investor` — and any background script run after a bulk load. |
| `IngestionMapper` | The four cleaning rules and the source-payload-to-entity mapping. | Both ingestion flows, the Crunchbase flow and the LinkedIn flow. |
| `IngestionLogger` | Structured writes to the flow execution log implementing skip-the-record-and-continue-the-run, plus the run summary and the provenance write. | Both ingestion flows. |
| `RateLimitService` | Per-caller accounting against `x_bst_startuptrk_rate_limit_counter` and construction of the 429 body with the computed `retry_after`. Exposes `consume()`, `retryAfter()`, `body()`, `reject()` and `prune()`. | All 31 REST operations, and the **Prune rate limit counters** scheduled job. |
| `RestResponseBuilder` | The pagination envelope carrying `total_count`, the per-field read gate that omits denied keys, the aggregate count, and the 404, 400 and 500 bodies. Exposes `serialize()`, `canRead()`, `valueOf()`, `page()`, `countBy()`, `notFound()`, `badRequest()` and `serverError()`. | All 31 REST operations, and every widget server script. |
| `RestQueryHelper` | Parses and bounds `sysparm_limit` and `sysparm_offset`, and returns trimmed query parameters. Exposes `getLimit()`, `getOffset()` and `getParam()`. | All 31 REST operations. |
| `AppProperties` | Typed accessors for all eleven system properties, including the ingestion cadence clamp. | Every component of the application — the REST operations by way of `RestQueryHelper` and `RateLimitService`, `StartupSearchService`, both flows and the scheduled job. Nothing reads a property ad hoc. |

### Addressing convention

A Script Include is referenced as `x_bst_startuptrk.<ClassName>` from outside the scope and by its bare class name within it. Inside the application — in an operation script, a business rule, a flow script step or a widget server script — the call is `new RestResponseBuilder()`. From outside the scope it is `new x_bst_startuptrk.RestResponseBuilder()`. Each record's `api_name` is the qualified form.

### Privilege

**None of the eight is client-callable, and none runs with elevated privilege.** Every record carries `client_callable` false and `package_private` access. No class may be reached from a client script, and no class may read a premium-gated column through an unsecured path and return it to a caller.

### Rename impact

Renaming any class in the table above requires updating every call site listed in its **Called by** column, and — because the Automated Test Framework suites encode class names and resource paths — the corresponding steps in [`./manual-build/05-atf-test-suites.md`](./manual-build/05-atf-test-suites.md).

## System properties

Eleven `sys_properties` records externalise the application's configuration. All keys are fully qualified with the `x_bst_startuptrk.` prefix.

| Key | Type | Shipped value | Read by |
| --- | --- | --- | --- |
| `x_bst_startuptrk.ingestion.cadence_hours` | Integer | `24` | `AppProperties`, which clamps the value to the range 6 to 48; read by the cadence guard that is the first action of both ingestion flows. |
| `x_bst_startuptrk.ingestion.source_mode` | Choice — `live` or `fallback` | `live` | `AppProperties`; read by both ingestion flows to decide whether to attempt the live call or go straight to the staging table. |
| `x_bst_startuptrk.ingestion.last_run_provenance` | String — `live` or `fallback` | `fallback` | `AppProperties`; written by `IngestionLogger` at the end of each flow run and read when reporting a run's provenance. |
| `x_bst_startuptrk.rest.default_limit` | Integer | `20` | `AppProperties`; read by `RestQueryHelper.getLimit()` as the fallback page size. |
| `x_bst_startuptrk.rest.max_limit` | Integer | `50` | `AppProperties`; read by `RestQueryHelper.getLimit()` as the clamp ceiling. |
| `x_bst_startuptrk.rest.rate_limit_requests` | Integer | `100` | `AppProperties`; read by `RateLimitService.consume()` as the per-window budget. |
| `x_bst_startuptrk.rest.rate_limit_window_seconds` | Integer | `60` | `AppProperties`; read by `RateLimitService` for the window length, the `retry_after` computation and the pruning job's retention. |
| `x_bst_startuptrk.inclusion.location_tokens` | String — comma-separated tokens | `Boston,Cambridge, MA` | `AppProperties`; read by `StartupSearchService.buildInclusionQuery()` to build the location clauses. |
| `x_bst_startuptrk.crunchbase.base_url` | String | `https://api.crunchbase.com/v3.1` | `AppProperties`; read by the Crunchbase ingestion flow's REST step. |
| `x_bst_startuptrk.linkedin.base_url` | String | `https://api.linkedin.com/v2` | `AppProperties`; read by the LinkedIn ingestion flow's REST step. |
| `x_bst_startuptrk.logging.level` | Choice | `info` | `AppProperties`; read by `IngestionLogger` and `RestResponseBuilder` to decide the verbosity of their log writes. |

**No property holds a secret.** No API key, client identifier, client secret, refresh token or password value is stored in any of the eleven, and the two base-URL properties are non-secret endpoint configuration. Credentials live only in the two Connection & Credential Aliases, `x_bst_startuptrk.crunchbase_api` and `x_bst_startuptrk.linkedin_oauth`, which are referenced by name and are built on the instance rather than shipped; see [`./manual-build/01-connection-credential-aliases.md`](./manual-build/01-connection-credential-aliases.md).

## Legacy provenance

The legacy Flask tree under `src/backend/routes/` is read-only reference. It supplied the endpoint-inventory spine and nothing else: no path, no parameter name, no response key and no status code was carried forward.

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

The two page-size values are the only things this API carries forward from the legacy contract, and they carry forward as property values rather than as constants.

A legacy inconsistency, stated as a fact so the carried-forward value is unambiguous: the route hard-codes a `per_page` default of **10** at `src/backend/routes/startup.py:L13`, while the shared constant declares a default of **20** at `src/shared/constants.ts:L8`. The same disagreement holds in `src/backend/routes/investor.py:L13`, `src/backend/routes/job.py:L13`, `src/backend/routes/news.py:L13` and `src/backend/routes/user.py:L13`, each hard-coding 10. **The target takes 20**, the shared-constant value, as the shipped value of `x_bst_startuptrk.rest.default_limit`.

### The paths were never served

The legacy application registers all six blueprints **without a URL prefix** at `src/backend/app.py:L28-L43`. Each `register_blueprint` call passes the blueprint alone, and no blueprint declares a `url_prefix` of its own, so the documented `/api/v1/...` endpoint paths were never actually served by the running application. The versioned API surface described in this document is **new capability, not a migrated contract**.

**No legacy API compatibility is maintained and no shim exists.** There is no alias route, no parameter-name translation layer, no envelope adapter and no redirect from the logical base path.

### Filter provenance

The legacy `name` and `industry` filters at `src/backend/routes/startup.py:L20-L22` — a case-insensitive `ilike` match on `name` and an equality match on `industry` — become filters on the `GET /startups` list operation. They are now built by `StartupSearchService` together with the inclusion criteria and the third `location` filter, in the single encoded query used for both the result set and `total_count`.

The legacy per-resource query parameters map across as follows. The legacy `startup_id` parameter name becomes `startup` on the target, matching the reference column name.

| Legacy filter | Source | Target filter |
| --- | --- | --- |
| `name` | `src/backend/routes/startup.py:L14` | `name` on `GET /startups` |
| `industry` | `src/backend/routes/startup.py:L15` | `industry` on `GET /startups` |
| `name` | `src/backend/routes/investor.py:L14` | `name` on `GET /investors` |
| `startup_id` | `src/backend/routes/job.py:L14` | `startup` on `GET /jobs` |
| `startup_id` | `src/backend/routes/news.py:L14` | `startup` on `GET /news` |
| — | — | `location` on `GET /startups`, `type` on `GET /investors`, `department` on `GET /jobs`, `source` on `GET /news`, `startup` and `round_type` on `GET /funding-rounds`, `startup` and `name` on `GET /founders` — no legacy counterpart |

This section is the API portion of the bidirectional matrix at [`../../docs/decisions/TRACEABILITY_MATRIX.md`](../../docs/decisions/TRACEABILITY_MATRIX.md).

## Related documents

- [`../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml`](../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml) — the authoritative REST definition, operation, Script Include and property records this document transcribes
- [`./data-model.md`](./data-model.md) — the ten tables field by field, the choice values, the inclusion-criteria predicate and the `portfolio_count` derivation
- [`./access-control.md`](./access-control.md) — the three roles, the seven premium fields, the omitted-not-nulled rule and the secured read path this contract depends on
- [`./gaps-and-flags.md`](./gaps-and-flags.md) — requirements with no clean platform equivalent, including the namespace segment in the base path and the exclusion of automated NewsArticle ingestion
- [`./validation-gates.md`](./validation-gates.md) — the machine-checkable post-commit gates run after the Update Set commits
- [`./validation-checklist.md`](./validation-checklist.md) — the five success criteria; criterion 3 is the pass condition for the six per-resource REST tests
- [`./manual-build/01-connection-credential-aliases.md`](./manual-build/01-connection-credential-aliases.md) — the two Connection & Credential Aliases, the only home for credential material
- [`./manual-build/05-atf-test-suites.md`](./manual-build/05-atf-test-suites.md) — the REST resource tests, and how the 429 response is made deterministic
- [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md) — the single source of truth for every decision, alternative and risk behind this contract
- [`../../docs/decisions/TRACEABILITY_MATRIX.md`](../../docs/decisions/TRACEABILITY_MATRIX.md) — the bidirectional source-to-target matrix this section feeds
- [`../../docs/review/CRITICAL_DECISIONS.md`](../../docs/review/CRITICAL_DECISIONS.md) — the five highest-risk decisions, including the API/Integration reviewer entry
