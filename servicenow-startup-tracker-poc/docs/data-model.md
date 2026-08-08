# Data model — `x_bst_startuptrk`

This document is the field-by-field reference for the data model of the ServiceNow scoped application `x_bst_startuptrk`. It covers all ten physical tables the application declares: the seven entity tables of prompt section 1.0 and three supporting tables. For every column it states the platform type, the maximum length, the mandatory flag, the uniqueness constraint where one is declared, the dictionary default, the choice values where a choice list is attached, and whether a field-level read ACL gates the column to premium callers. It also states the access posture every table carries at the `sys_db_object` level, the derivation of the one calculated field, the cascade behaviour of every reference column, the startup inclusion criteria, and the retention, minimisation and data-subject erasure lifecycle applied to the personal data the staging and counter tables hold.

**Authority.** The frozen prompt and the Agent Action Plan are authoritative for all application content, and they govern the Update Set XML and this document alike. The Update Set XML at [`../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml`](../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml) is the implementation of that specification and the transcription source for everything below: the `sys_db_object`, `sys_dictionary`, `sys_documentation` and `sys_choice` records it carries. Where this document and those records disagree about a table name, a column name, a type, a length, a flag, a default or a choice value, the records are checked against the prompt and the plan first. Where the records match the specification, this document is corrected to them. Where the records depart from it, the records are corrected.

This document carries no rationale. Every decision behind the model, every alternative considered and every risk is recorded in [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md), which is to be the single source of truth for "why".

The identifiers established here — table names, column names, choice values, mandatory flags and premium markers — are reused verbatim by [`./access-control.md`](./access-control.md), [`./api-reference.md`](./api-reference.md) and [`./validation-gates.md`](./validation-gates.md), and are to be reused by [`./validation-checklist.md`](./validation-checklist.md) and [`./gaps-and-flags.md`](./gaps-and-flags.md).

## Referenced documents

This document is self-contained. Every table, column, type, length, flag, default, choice value, premium marker, cascade rule, derivation and predicate is stated here in full; no statement of the model requires reading another file.

**Every document named below is delivered and readable.** Each link resolves to a file in this package, among them the Update Set XML, `./access-control.md`, `./api-reference.md`, `./validation-gates.md` and `../sample-data/README.md` with its six CSVs, so a reader can follow any link and read the content the statement around it describes; no link is a forward reference to something still to be written.

**Reviewer.** This document is to be the artifact validated by **entry 4 of [`../../docs/review/CRITICAL_DECISIONS.md`](../../docs/review/CRITICAL_DECISIONS.md), reviewer persona Data/SME, risk level High**, covering the **write idempotence** of the six natural keys, the join-table authority, the cascade rules and the stored portfolio count. That entry was raised from Medium to High when idempotence was added to it: its first four checks are the ones that cannot be satisfied by running an ingestion batch once, and the first of them is simply to run the same batch twice and confirm every row count is unchanged.

## Table inventory

Ten physical tables. Seven are the entity tables declared by prompt section 1.0; three are supporting tables.

| # | Table | Label | Classification | Columns |
| --- | --- | --- | --- | --- |
| 1 | `x_bst_startuptrk_startup` | Startup | Entity | 12 |
| 2 | `x_bst_startuptrk_founder` | Founder | Entity | 6 |
| 3 | `x_bst_startuptrk_executive` | Executive | Entity | 6 |
| 4 | `x_bst_startuptrk_investor` | Investor | Entity | 6 |
| 5 | `x_bst_startuptrk_fundinground` | Funding round | Entity | 8 |
| 6 | `x_bst_startuptrk_jobposting` | Job posting | Entity | 9 |
| 7 | `x_bst_startuptrk_newsarticle` | News article | Entity | 6 |
| 8 | `x_bst_startuptrk_m2m_round_investor` | Round investor | Supporting — join table | 2 |
| 9 | `x_bst_startuptrk_ingest_staging` | Ingestion staging | Supporting — staging table | 40 |
| 10 | `x_bst_startuptrk_rate_limit_counter` | Rate limit counter | Supporting — counter table | 4 |

Prompt section 1.0 states exactly seven custom tables; the application declares ten physical tables. Prompt section 10.0 criterion 1's table count is evaluated against the seven entity tables only, and the join table, the staging table and the rate-limit counter table are supporting artifacts counted separately. The resolution of that count is recorded at `D-008` in [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md).

None of the ten tables extends another table and none is extendable. Every table name carries the full `x_bst_startuptrk_` scope prefix. Three entity table names are single words with no separating underscore between the parts: `_fundinground`, `_jobposting` and `_newsarticle`. The three supporting table names are `_m2m_round_investor`, `_ingest_staging` and `_rate_limit_counter`.

## Table access posture

**Write access is closed on all ten tables. Read access differs between the seven entity tables and the three supporting tables**, and the split is deliberate. The write, schema and configuration posture is identical across all ten:

**The seven entity tables** — `_startup`, `_founder`, `_executive`, `_investor`, `_fundinground`, `_jobposting`, `_newsarticle`:

| `sys_db_object` field | Value on all seven | Effect |
| --- | --- | --- |
| `create_access` | false | No out-of-scope caller may insert. |
| `update_access` | false | No out-of-scope caller may update. |
| `delete_access` | false | No out-of-scope caller may delete. |
| `alter_access` | false | No out-of-scope application may add, change or remove a column. |
| `configuration_access` | false | No out-of-scope application may change the table's configuration. |
| `client_scripts_access` | false | No out-of-scope client script may run against it. |
| `actions_access` | false | No out-of-scope action may target it. |
| `create_access_controls` | false | No out-of-scope application may create access controls on it. |
| `is_extendable` | false | No table may extend it, so no child table can inherit its data with a different access posture. |

The read posture is where the two groups part:

| `sys_db_object` field | Seven entity tables | Three supporting tables |
| --- | --- | --- |
| `access` | `public` | `package_private` |
| `read_access` | true | false |
| `ws_access` | true — the table **is** served at `/api/now/table/<table>` | false — the table is served by no external route at all |

**What `access` `public` opens on the seven entity tables is a read route and nothing more, and the field-level ACLs still govern it.** A field-level read ACL is evaluated on the access-controlled read path, and the Table API is such a path, so a caller holding only `x_bst_startuptrk.user` cannot see `total_funding_usd`, `institutional_funding_last_5yrs`, `contact_email`, `aum_usd`, `amount_usd` or `valuation_usd` over it. What is deliberately **not** opened is any write, configuration or schema capability: `create_access`, `update_access`, `delete_access`, `alter_access`, `configuration_access`, `actions_access`, `client_scripts_access` and `create_access_controls` are `false` on all ten tables. Unsecured record access from another scope does not evaluate access controls at all, which is why the three supporting tables — the only tables holding verbatim upstream payloads, join rows and per-caller counters — stay sealed to the scope, leaving the application's own eight Script Includes as the only code that can address them.

The three supporting tables are `x_bst_startuptrk_m2m_round_investor`, `x_bst_startuptrk_ingest_staging` and `x_bst_startuptrk_rate_limit_counter`. Sealing them matters most for the staging table, which is the only table in the application holding verbatim upstream payloads and unvalidated personal data.

**Read access controls, not table posture, are what make the field-level design meaningful.** A field-level read access control is evaluated on every access-controlled read path, and the platform Table API is one of them: it authenticates the caller, evaluates the table-level read control, and evaluates each field-level read control before returning a value. A caller holding only `x_bst_startuptrk.user` therefore cannot read `total_funding_usd`, `aum_usd` or `contact_email` over `/api/now/table/x_bst_startuptrk_startup` any more than over the application's own API — the field is omitted on both. What the seven entity tables expose is a **read** route governed by the same seven table-level and seven field-level read controls documented in [`./access-control.md`](./access-control.md). Sealing the seven entity tables instead would have hidden that fact rather than proved it: a denial a caller cannot observe is indistinguishable from a table the caller cannot reach.

**No write route is exposed anywhere.** Every cross-scope write, schema and configuration capability is `false` on all ten tables, so the Table API is read-only on the seven and absent on the three. The 31 operations of [`./api-reference.md`](./api-reference.md) remain the only programmatic route that can change application data.

**Two differences from the application's own API remain on the Table API read route, and both are recorded rather than hidden**: it is outside the application's fixed-window rate limiter, and outside the two `REST_Endpoint` execution controls. Their compensating controls — the table-level read controls that admit only the three scoped roles, and an operator-owned platform inbound rate-limit rule — are stated in [`./gaps-and-flags.md`](./gaps-and-flags.md).

**One verification consequence follows, and it is what the posture exists to serve.** Because the seven entity tables are served by the Table API, the eleven required post-commit gates are exactly the reads AAP section 0.11.2 specifies: one authenticated `sysparm_limit=1` request per entity table. The three supporting tables are not gated that way and are not reachable that way. The gate set is in [`./validation-gates.md`](./validation-gates.md).

**No write reaches any of the ten tables from outside the scope.** `create_access`, `update_access` and `delete_access` are false on all ten dictionary records, so the administrator-only grants of layer 2 cannot be circumvented by the Table API or by another scoped application. The open posture concedes a read route, and only a read route.

**The three supporting tables are sealed because nothing outside the scope has any business addressing them.** The join table is read on a caller's behalf through `InvestorPortfolioService`, and the staging and rate-limit tables are internal machinery holding upstream payloads and per-caller counters. None of the three carries a premium field, so there is no field control on them to exercise, and no gate reads them.

**One consequence for the API surface is worth recording.** With `ws_access` true, the Table API is a second read route to the entity rows, and it is not subject to the application's own **rate limiter** — which is application-level accounting in the Scripted REST operations, not an access control. Every access control this application declares applies on both routes; the request budget applies on one. That is stated in [`./api-reference.md`](./api-reference.md) so no consumer reads the budget as a security boundary.

The complete access-control scheme layered above this posture — the three roles, the five ACL layers, the 49 access controls and the 74 role joins — is in [`./access-control.md`](./access-control.md) and is not restated here. The application's own **eight** Script Includes, matching Agent Action Plan section 0.4.5, are the only code inside the scope that addresses these tables; the call graph is in [`./api-reference.md`](./api-reference.md).

## Notation

Two markers appear in the column tables below.

| Marker | Meaning |
| --- | --- |
| **M** | The column is mandatory. Its dictionary record carries `mandatory` true, so a record cannot be saved without a value. |
| **P** | The column is premium-gated. A field-level read ACL restricts read access to the `x_bst_startuptrk.admin` and `x_bst_startuptrk.premium_user` roles. A caller holding only `x_bst_startuptrk.user` is denied, and the REST serialiser omits the key from the response object. The matrix is in [`./access-control.md`](./access-control.md). |
| — | Not applicable, or no value declared. |

These are the platform types used below.

| Type | Meaning |
| --- | --- |
| `string` | Character data. The **Max length** column gives the dictionary `max_length`. |
| `string`, choice list | A `string` column with a choice list attached. The **Choice values** column lists every value. The stored value and the displayed label are identical for every choice in this application. |
| `string`, multi-choice | A `string` column with a choice list attached and the `multi_select=true` attribute, so more than one value may be selected. |
| `integer` | Whole number. |
| `boolean` | True/False. |
| `currency` | Platform currency. The column name fixes the denomination as United States dollars. |
| `decimal` | Fixed-point number. Used on the staging table only. |
| `glide_date` | Date with no time component. |
| `glide_date_time` | Date and time. |
| `reference` | Reference to a record in another table. Max length is 32, the width of a `sys_id`. Each reference column's target table and cascade rule are also collected in [Reference and cascade rules](#reference-and-cascade-rules). |

Every table also carries the platform's own `sys_id`, `sys_created_on`, `sys_created_by`, `sys_updated_on`, `sys_updated_by` and `sys_mod_count` columns. Those are supplied by the platform for every table and are not part of the counts in this document.

## Entity tables

Seven tables, 53 columns. Prompt section 1.0's field definitions are **binding and complete**: no column may be added to these tables, none may be omitted, and none may be inferred. The choice lists are equally closed.

### 1. `x_bst_startuptrk_startup`

Label **Startup**. Twelve columns. The display column is `name`.

| Column | Platform type | Max length | Mandatory | Default | Choice values | Premium |
| --- | --- | --- | --- | --- | --- | --- |
| `name` | `string` | 100 | M | — | — | — |
| `description` | `string` | 4000 | — | — | — | — |
| `industry` | `string`, choice list | 40 | — | — | `Fintech`, `Healthtech`, `SaaS`, `Consumer`, `Deeptech`, `Other` | — |
| `founded_year` | `integer` | — | — | — | — | — |
| `headquarters_location` | `string` | 100 | M | — | — | — |
| `website` | `string` | 255 | — | — | — | — |
| `logo_url` | `string` | 255 | — | — | — | — |
| `funding_stage` | `string`, choice list | 40 | — | — | `Pre-Seed`, `Seed`, `Series A`, `Series B`, `Series C+`, `Growth`, `Public`, `Acquired` — **no `Other` member** | — |
| `total_funding_usd` | `currency` | — | — | — | — | P |
| `active` | `boolean` | — | M | `true` | — | — |
| `institutional_funding_last_5yrs` | `boolean` | — | — | `false` | — | P |
| `employee_count_range` | `string`, choice list | 20 | — | — | `1-10`, `11-50`, `51-200`, `201-500`, `500+` — **no `Other` member** | — |

`active` and `headquarters_location` are the two columns the startup inclusion criteria test. `institutional_funding_last_5yrs` is a premium-gated display attribute and is not part of that predicate. See [The startup inclusion criteria](#the-startup-inclusion-criteria).

`active` is mandatory **and** carries the dictionary default `true`, and those two facts belong to two different surfaces. **Dictionary defaulting is a write-time platform behaviour**: when a record is inserted without the column being set — through the REST create operation, whose specification does not mark `active` mandatory, through a platform form, or through an ingestion insert that supplies no value — the platform applies `true`, and the mandatory flag is satisfied by the defaulted value. **Cleaning rule 4 is a transform-time application behaviour** and it does not default anything: `IngestionMapper` declares `active` in `MANDATORY.startup` and rejects an incoming row that leaves it blank, rather than inventing a value for a column the source did not report. A blank `active` therefore behaves differently by route, deliberately: an omitted key in a REST create body means "use the declared default", while a blank `active` on a staged row or a live payload means "the source did not tell us", which rule 4 refuses. Two shipped fixtures encode exactly that refusal, both in `crunchbase_startups_sample.csv`: `Jamaica Plain Sensorworks` on data row 11 blanks `headquarters_location` **and** `active`, so the rejection names both, and `Charles River Telemetry` on data row 13 blanks `active` alone, which is the narrower case proving `active` is rejected on its own rather than quietly defaulted. Their expected outcomes are recorded in [`../sample-data/README.md`](../sample-data/README.md).

The same split holds for `x_bst_startuptrk_jobposting.active`, with one difference that follows from the same rule: it is **not** mandatory, so `MANDATORY.job_posting` does not list it and a blank value neither rejects the row nor is defaulted by the transform — the column is simply left unset and the platform's `true` applies on insert.

The consequence for an **update** is what makes the split matter beyond documentation: because the transform defaults nothing, an ingestion run that does not carry `active` cannot overwrite a stored `false` with the dictionary's `true`. The same applies to `institutional_funding_last_5yrs`, whose default is `false` and which neither source system publishes.

Five child tables reference this table through a mandatory `startup` column: `_founder`, `_executive`, `_fundinground`, `_jobposting` and `_newsarticle`.

### 2. `x_bst_startuptrk_founder`

Label **Founder**. Six columns. The display column is `name`.

| Column | Platform type | Max length | Mandatory | Default | Choice values | Premium |
| --- | --- | --- | --- | --- | --- | --- |
| `name` | `string` | 100 | M | — | — | — |
| `startup` | `reference` to `x_bst_startuptrk_startup` | 32 | M | — | — | — |
| `title` | `string`, choice list | 40 | — | — | `CEO`, `CTO`, `COO`, `Co-Founder`, `Other` | — |
| `bio` | `string` | 2000 | — | — | — | — |
| `linkedin_url` | `string` | 255 | — | — | — | — |
| `contact_email` | `string` | 100 | — | — | — | P |

### 3. `x_bst_startuptrk_executive`

Label **Executive**. Six columns. The display column is `name`.

Prompt section 1.3 requires Founder and Executive to remain two separate tables and forbids collapsing them into one person table carrying a role flag. The two tables declare the same six column names with the same types, lengths, mandatory flags and premium marker; the `title` choice list is the only difference between them.

| Column | Platform type | Max length | Mandatory | Default | Choice values | Premium |
| --- | --- | --- | --- | --- | --- | --- |
| `name` | `string` | 100 | M | — | — | — |
| `startup` | `reference` to `x_bst_startuptrk_startup` | 32 | M | — | — | — |
| `title` | `string`, choice list | 40 | — | — | `CFO`, `VP Engineering`, `VP Sales`, `VP Marketing`, `Head of Product`, `Other` | — |
| `bio` | `string` | 2000 | — | — | — | — |
| `linkedin_url` | `string` | 255 | — | — | — | — |
| `contact_email` | `string` | 100 | — | — | — | P |

Executive records are served over REST by the nested sub-resource `GET /founders/{startup_id}/executives`, documented in [`./api-reference.md`](./api-reference.md).

### 4. `x_bst_startuptrk_investor`

Label **Investor**. Six columns. The display column is `name`.

| Column | Platform type | Max length | Mandatory | Default | Choice values | Premium |
| --- | --- | --- | --- | --- | --- | --- |
| `name` | `string` | 100 | M | — | — | — |
| `type` | `string`, choice list | 30 | — | — | `VC`, `Angel`, `PE`, `Corporate`, `Accelerator` — **no `Other` member** | — |
| `focus_areas` | `string`, multi-choice | 255 | — | — | `Fintech`, `Healthtech`, `SaaS`, `Consumer`, `Deeptech`, `Other` | — |
| `website` | `string` | 255 | — | — | — | — |
| `aum_usd` | `currency` | — | — | — | — | P |
| `portfolio_count` | `integer`, read-only | — | — | `0` | — | — |

`focus_areas` carries the same six values as `x_bst_startuptrk_startup.industry`, and more than one may be selected.

`portfolio_count` is a **calculated** value, declared Integer by prompt section 1.4. It is stored on the record, maintained by business rules, and **read-only in the dictionary** so that `InvestorPortfolioService` is its only writer. Its definition, its owning Script Include, its maintenance triggers and the precise reach of that read-only flag are in [Investor.portfolio_count](#investorportfolio_count).

The `type` choice list has **no `Other` member**, so an unmatched incoming investor type is logged and the field left unwritten rather than coerced. See [One closed-choice rule for all eleven choice columns](#one-closed-choice-rule-for-all-eleven-choice-columns).

### 5. `x_bst_startuptrk_fundinground`

Label **Funding round**. Eight columns. The table declares no display column; a funding round is identified in the interface by its `startup` and `round_date`.

| Column | Platform type | Max length | Mandatory | Default | Choice values | Premium |
| --- | --- | --- | --- | --- | --- | --- |
| `startup` | `reference` to `x_bst_startuptrk_startup` | 32 | M | — | — | — |
| `round_type` | `string`, choice list | 40 | — | — | `Pre-Seed`, `Seed`, `Series A`, `Series B`, `Series C+`, `Growth`, `Public`, `Acquired` — **no `Other` member** | — |
| `amount_usd` | `currency` | — | — | — | — | P |
| `round_date` | `glide_date` | — | M | — | — | — |
| `lead_investor` | `reference` to `x_bst_startuptrk_investor` | 32 | — | — | — | — |
| `participating_investors` | `glide_list` to `x_bst_startuptrk_investor`, read-only | 4000 | — | — | — | — |
| `valuation_usd` | `currency` | — | — | — | — | P |
| `source_url` | `string` | 255 | — | — | — | — |

`round_type` carries the same eight values as `x_bst_startuptrk_startup.funding_stage`.

`lead_investor` is a first-class reference and carries the lead-versus-participating distinction.

`participating_investors` is a **list of references** to `x_bst_startuptrk_investor` — the platform's List type, which is what prompt section 1.5 declares — and it is **stored, read-only and derived**. It is a one-way projection of the join table `x_bst_startuptrk_m2m_round_investor`, which stays authoritative and remains the only write target for participation; `InvestorPortfolioService.refreshRoundParticipants()` rewrites the column whenever a link row is inserted, updated or deleted. Nothing writes both. The mechanism — the join table authoritative, this column a stored read-only projection of it — is recorded at `D-010` in [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md), and the array the API projects from the join table at `D-011`.

**Prompt section 1.5 names both mechanisms in one clause** — a List field *and* a physical join table — and on this platform they are two different things: a list-reference column stores delimited identifiers inside the funding-round row and creates no table, while a many-to-many relationship generates a join table. Implementing both as independent write targets would be a dual write that drifts. The resolution delivered here is that **the join table is authoritative** because section 1.5 names it explicitly, the column is a read-only projection of it that delivers the List reading, and the REST layer assembles its `participating_investors` array from the join table rather than from the column. Both halves of the clause are satisfied and nothing is written twice. The decision, the rejected alternatives and the drift risk are recorded in [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md); the reviewer entry that owns it is in [`../../docs/review/CRITICAL_DECISIONS.md`](../../docs/review/CRITICAL_DECISIONS.md).

**The projection is bounded, and the bound is enforced rather than assumed.** A `glide_list` stores its members as comma-separated 32-character identifiers, so each member costs 33 characters and the declared `max_length` of 4000 holds **121** investors. The join table itself is unbounded, so a round could in principle link more. `refreshRoundParticipants()` therefore measures the derived value against the declared length before writing it: within the bound it stores the complete list, and beyond the bound it **empties the projection and records the overflow** through `gs.error` tagged `[x_bst_startuptrk.InvestorPortfolioService]`, naming the round, the number of investors linked and the capacity. It never stores a partial identifier list, because a partial list is indistinguishable from a complete one when read and would misrepresent participation. The two numbers are declared once, as `PROJECTION_LENGTH` with `PROJECTION_CAPACITY` derived from it, so raising the column length raises the capacity with it.

Nothing downstream depends on the projection: the four funding-round REST operations assemble their `participating_investors` array from the join table, and `countPortfolio()` unions the lead-investor and join-table paths. An emptied projection therefore costs the platform list view its inline display for that one round and costs the API nothing.

The one-way property is enumerable, and the enumeration is the check to repeat after any change to this table or to the join table:

| Path | Direction | Mechanism |
| --- | --- | --- |
| `InvestorPortfolioService.refreshRoundParticipants()` | Write | The **only** write to the column in the application. It reads the join table through `InvestorPortfolioService.participantsForRounds()`, compares the derived value with the stored one, and writes with business rules suppressed so the projection cannot recurse. |
| `IngestionMapper.linkParticipants()` | Write | Writes the **join table**, never the column. It is the ingestion path's only participation writer and it reconciles the round's rows to the incoming set exactly. |
| `InvestorPortfolioService.linkInvestorToRound()` | Write | Writes the **join table**, never the column. A single idempotent pair, for an administrative one-off link. |
| `IngestionMapper` | Write | Decodes `participating_investor_names` into investor names and hands them to the join-table writer. It never writes the column. |
| The four funding-round REST operations | Read | Assemble the `participating_investors` response array from the join table, never from the column. |
| The funding-round form's related list | Read and write | Reads and writes the **join table**. |
| The column's dictionary entry | — | `read_only` is `true`, so a write arriving through the platform Table API, the native form or an import transform is refused. |

The column is **not** a calculated value evaluated at read time. It is stored, which makes it queryable and sortable, and it is written by the business rule alone. One operational requirement applies, and it is the same one `portfolio_count` carries: any ingestion or import path that writes the join table must run business rules, or the projection stays stale until the rule next runs. See [Investor.portfolio_count](#investorportfolio_count).

The funding-round form surfaces **the related list**, not this column, as the place an administrator adds and removes participating investors, and the column is absent from the default list view. See [8. `x_bst_startuptrk_m2m_round_investor`](#8-x_bst_startuptrk_m2m_round_investor).

### 6. `x_bst_startuptrk_jobposting`

Label **Job posting**. Nine columns. The display column is `title`.

| Column | Platform type | Max length | Mandatory | Default | Choice values | Premium |
| --- | --- | --- | --- | --- | --- | --- |
| `startup` | `reference` to `x_bst_startuptrk_startup` | 32 | M | — | — | — |
| `title` | `string` | 150 | M | — | — | — |
| `department` | `string`, choice list | 40 | — | — | `Engineering`, `Sales`, `Marketing`, `Product`, `Operations`, `Other` | — |
| `location` | `string` | 100 | — | — | — | — |
| `remote_type` | `string`, choice list | 20 | — | — | `Onsite`, `Hybrid`, `Remote` — **no `Other` member** | — |
| `seniority` | `string`, choice list | 20 | — | — | `Entry`, `Mid`, `Senior`, `Lead`, `Executive` — **no `Other` member** | — |
| `posted_date` | `glide_date` | — | — | — | — | — |
| `url` | `string` | 255 | — | — | — | — |
| `active` | `boolean` | — | — | `true` | — | — |

`x_bst_startuptrk_jobposting.active` and `x_bst_startuptrk_startup.active` are separate columns on separate tables. The job posting's `active` is not mandatory and takes no part in the startup inclusion criteria.

### 7. `x_bst_startuptrk_newsarticle`

Label **News article**. Six columns. The display column is `title`.

| Column | Platform type | Max length | Mandatory | Default | Choice values | Premium |
| --- | --- | --- | --- | --- | --- | --- |
| `startup` | `reference` to `x_bst_startuptrk_startup` | 32 | M | — | — | — |
| `title` | `string` | 255 | M | — | — | — |
| `source` | `string` | 100 | — | — | — | — |
| `url` | `string` | 255 | — | — | — | — |
| `published_date` | `glide_date` | — | — | — | — | — |
| `summary` | `string` | 2000 | — | — | — | — |

Prompt sections 1.7 and 4.0 exclude NewsArticle from automated ingestion. Neither ingestion flow writes this table, and the fallback dataset carries no NewsArticle file; records are created by manual entry or by a separate ad hoc import. The REST resource `/news` serves read plus manual write only. The exclusion is recorded in [`./gaps-and-flags.md`](./gaps-and-flags.md).

### Column count roll-up

| # | Table | Columns |
| --- | --- | --- |
| 1 | `x_bst_startuptrk_startup` | 12 |
| 2 | `x_bst_startuptrk_founder` | 6 |
| 3 | `x_bst_startuptrk_executive` | 6 |
| 4 | `x_bst_startuptrk_investor` | 6 |
| 5 | `x_bst_startuptrk_fundinground` | 8 |
| 6 | `x_bst_startuptrk_jobposting` | 9 |
| 7 | `x_bst_startuptrk_newsarticle` | 6 |
| | **Total** | **53** |

12 + 6 + 6 + 6 + 8 + 9 + 6 = 53.

Seven columns across four of those tables are premium-gated: `x_bst_startuptrk_startup.total_funding_usd`, `x_bst_startuptrk_startup.institutional_funding_last_5yrs`, `x_bst_startuptrk_founder.contact_email`, `x_bst_startuptrk_executive.contact_email`, `x_bst_startuptrk_investor.aum_usd`, `x_bst_startuptrk_fundinground.amount_usd` and `x_bst_startuptrk_fundinground.valuation_usd`. Fourteen columns are mandatory: `name`, `headquarters_location` and `active` on Startup; `name` and `startup` on Founder; `name` and `startup` on Executive; `name` on Investor; `startup` and `round_date` on Funding round; `startup` and `title` on Job posting; `startup` and `title` on News article.

This roll-up is the field-count evidence that prompt section 10.0 criterion 1 depends on. The machine-checkable table reads are in [`./validation-gates.md`](./validation-gates.md); the criterion's field-by-field verification steps are specified in [`./validation-checklist.md`](./validation-checklist.md).

## Supporting tables

The three tables in this section are **not** entity tables and are not counted towards prompt section 10.0 criterion 1. Each exists to support the entity model: one join table materialises a many-to-many relationship, one staging table holds the fallback ingestion dataset, and one counter table holds per-caller rate-limit accounting. **Forty-six** columns in total: 2 on the join table, 40 on the staging table and 4 on the counter table. 2 + 40 + 4 = 46. The counter table's four columns are `caller`, `window_start`, `request_count` and `api_resource`, enumerated under [10. `x_bst_startuptrk_rate_limit_counter`](#10-x_bst_startuptrk_rate_limit_counter), and the inventory table at the head of this document records the same count of 4.

All three carry the sealed posture of [Table access posture](#table-access-posture), and all three are additionally restricted by access control on **all four operations**. The join table is readable by every application role, because a caller reading a funding round must be able to see its participating investors; the staging table and the counter table are administrator-only in every direction, because they hold ingestion working data and per-caller accounting that no ordinary caller has any reason to reach:

| Table | Read | Write | Create | Delete |
| --- | --- | --- | --- | --- |
| `x_bst_startuptrk_m2m_round_investor` | all three roles | `x_bst_startuptrk.admin` | `x_bst_startuptrk.admin` | `x_bst_startuptrk.admin` |
| `x_bst_startuptrk_ingest_staging` | `x_bst_startuptrk.admin` | `x_bst_startuptrk.admin` | `x_bst_startuptrk.admin` | `x_bst_startuptrk.admin` |
| `x_bst_startuptrk_rate_limit_counter` | `x_bst_startuptrk.admin` | `x_bst_startuptrk.admin` | `x_bst_startuptrk.admin` | `x_bst_startuptrk.admin` |

**All four operations carry an explicit access control on every one of the three tables — twelve in total.** Declaring only read and write and relying on the platform's default deny for create and delete would leave the intent implicit, and an implicit deny is one that a later table-wide or global control can satisfy without anyone noticing the tables were never named. The twelve controls are Layer 4 of [`./access-control.md`](./access-control.md).

### 8. `x_bst_startuptrk_m2m_round_investor`

Label **Round investor**. Two columns. The table declares no display column. It is named verbatim by prompt section 1.5.

| Column | Platform type | Max length | Mandatory | Default | Choice values | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `funding_round` | `reference` to `x_bst_startuptrk_fundinground` | 32 | M | — | — | Cascade delete |
| `investor` | `reference` to `x_bst_startuptrk_investor` | 32 | M | — | — | Cascade delete |

This table is **authoritative** for the participating investors of a funding round, and it is the **only** table written when participation changes. One row links one funding round to one participating investor. Three surfaces read it:

- The funding round form surfaces it as a **related list**, which is the editable participant surface: an administrator adds and removes participating investors there.
- `x_bst_startuptrk_fundinground.participating_investors` is a stored, read-only list of references **projected** from it, refreshed by the round-investor-link business rule. It is a derived copy, never an independent record of participation.
- The REST layer emits `participating_investors` as a **JSON array** of investor references assembled from this table directly — one batched query per page of funding rounds, not one query per round. The response shape is in [`./api-reference.md`](./api-reference.md).

**The `(funding_round, investor)` pair is unique.** A unique composite database index on the two columns is declared in the Update Set, so the same investor cannot be linked to the same round twice, whatever the write path. The indexes this application declares are listed under [Declared indexes](#declared-indexes).

**Two programmatic writers exist, and they do different things.**

| Writer | Semantics | Used by |
| --- | --- | --- |
| `IngestionMapper.linkParticipants(runId, roundId, investorIds, participation)` | **Exact-set reconciliation.** It reads the round's existing rows, keeps those the incoming set names, inserts those it names and the round lacks, and **deletes those the incoming set no longer names** — the delete only when the incoming set is *complete*, meaning the incoming record supplied a value and every member of it resolved to exactly one investor. Where a member did not resolve, the write is additive only and the obsolete rows are kept, because deleting against an incomplete set would discard participation the source still asserts. An absent incoming value writes nothing at all. Every failed insert and every failed delete is counted, and a non-zero count stamps the funding round's staging row `error` rather than `processed`. | Both ingestion flows, through `IngestionMapper.upsert()`. It is the **only** join-table writer on the ingestion path. |
| `InvestorPortfolioService.linkInvestorToRound(roundId, investorId)` | **A single idempotent pair.** Given a pair that already exists it returns the existing row rather than attempting a second insert; otherwise it inserts one. It deletes nothing and reconciles nothing. | An administrative one-off link from a background script. Nothing on the ingestion path calls it. |

The lead-versus-participating distinction is carried by `x_bst_startuptrk_fundinground.lead_investor`, a first-class reference column on the funding round and not a row in this table. The same investor may be both the lead investor of a round and a participating investor in it. The decision behind this table's authority, and behind the read-only projection it feeds, is recorded at `D-010` in [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md).

Rows in this table drive the second maintenance trigger for `x_bst_startuptrk_investor.portfolio_count`; see [Investor.portfolio_count](#investorportfolio_count).

### 9. `x_bst_startuptrk_ingest_staging`

Label **Ingestion staging**. Forty-one columns. The display column is `import_run`. This is the single staging table required by prompt section 4.0, and it is the home of the fallback dataset both ingestion flows read when a live call fails, times out, returns a malformed response, or when the property `x_bst_startuptrk.ingestion.source_mode` is set to `fallback`.

One flat table serves all six ingested record types. `record_type` is the discriminator that tells the transform which entity table a row becomes and which flattened columns it reads. No staging column is mandatory, so a row with a blank value loads successfully; the mandatory requirement is enforced per record type at transform time by cleaning rule 4, which rejects the row and creates no entity record.

Forty-one columns is seven control columns plus thirty-four flattened scalar columns: 7 + 34 = 41.

#### Control columns

Seven columns, present on every row whatever its record type.

| Column | Platform type | Max length | Mandatory | Default | Choice values | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `source_system` | `string`, choice list | 40 | — | — | `crunchbase`, `linkedin` | Which ingestion flow's dataset the row belongs to |
| `record_type` | `string`, choice list | 40 | — | — | `startup`, `founder`, `executive`, `investor`, `funding_round`, `job_posting` | Discriminator for the transform |
| `raw_payload` | `string` | 8000 | — | — | — | The source response payload in the shape the source API returns, per prompt section 4.0 |
| `import_state` | `string`, choice list | 40 | — | `pending` | `pending`, `in_progress`, `processed`, `rejected`, `error` | Processing state of the staged row. `in_progress` is written by a flow's claim step; the four settled and unsettled remainder are written by `IngestionMapper.writeStagingState()` at the end of each row |
| `error_message` | `string` | 1000 | — | — | — | Rejection or error detail. `IngestionMapper.clean()` returns the reason and `IngestionMapper.writeStagingState()` writes it here alongside the matching `import_state` |
| `run_provenance` | `string`, choice list | 40 | — | — | `live`, `fallback` | Whether the row was consumed by a live or a fallback run |
| `import_run` | `string` | 64 | — | — | — | Run identifier shared by every row of one load |

#### The five `import_state` members

The choice list carries five members, and the distinction between the two pre-settlement states is what makes a run safe to re-execute.

| Member | Written by | Meaning | Read by `ingestStaging()` |
| --- | --- | --- | --- |
| `pending` | The dictionary default, on import | The row has been staged and no run has taken it | **Yes.** This is the only state the transform selects on |
| `in_progress` | A flow's claim step, together with `import_run` set to that run's identifier | A run has claimed the row and has not yet settled it | No |
| `processed` | `IngestionMapper.writeStagingState()` | An entity record was created or updated from the row | No |
| `rejected` | `IngestionMapper.writeStagingState()` | A cleaning rule refused the row. Expected behaviour, not an error | No |
| `error` | `IngestionMapper.writeStagingState()` | A write failed for a reason other than a cleaning rule, or a funding round's participant links could not be reconciled | No |

**`in_progress` exists so that a row is read exactly once per run and an abandoned run leaves a trace.** The claim moves the row out of the `pending` query before any work is done, so a re-read within the run cannot pick it up, and a run that dies hard leaves its rows carrying the identifier of the run that abandoned them. **Nothing returns a row to `pending` automatically** — a row that killed one run would kill the next — so the return is an administrative edit. The procedure is in [`./manual-build/06-staging-table-csv-import.md`](./manual-build/06-staging-table-csv-import.md).

#### Flattened scalar columns, by record type

Thirty-three columns. They carry the prompt section 1.0 column names of the entity table each record type becomes, with references expressed as the natural keys `startup_name`, `lead_investor_name` and `participating_investor_names`. A CSV cannot carry a `sys_id` for a record that does not exist yet, so every reference travels as the target record's natural key and the transform resolves it at load time.

`participating_investor_names` carries **a list, in one of three accepted carriers, and never a comma-separated one**. `IngestionMapper.resolveParticipants()` accepts a real JSON array, a JSON array serialised as text — which is what the shipped CSV uses — or a `|`-delimited string, and a value carrying none of those is read as **one single name**. Each member is trimmed, an empty member is dropped, each remaining member is resolved to exactly one Investor record, a repeated member is kept once, and a member that resolves to none or to more than one is logged and left unlinked while the count of unresolved members is carried back to the caller. A value that yields no name in any carrier is logged against `participating_investor_names` with the reason naming all three accepted carriers.

**The comma is not a delimiter here, and treating it as one was a defect.** Investor names legitimately contain commas — `Beacon Hill Ventures, LP` is one investor, not two — so splitting on the comma silently fabricated names that resolved to nothing and dropped a real participant from the round. The `|` delimiter and the JSON array were chosen because neither occurs inside an organisation name.

Because the column names are the entity column names, a name shared by more than one entity is **one** staging column read by more than one record type rather than one column per entity. Six columns are shared:

| Column | Read by record types | Carries |
| --- | --- | --- |
| `name` | `startup`, `investor`, `founder`, `executive` | The record's own name |
| `website` | `startup`, `investor` | The record's own website |
| `active` | `startup`, `job_posting` | The record's own active flag |
| `title` | `founder`, `executive`, `job_posting` | The person's title, or the posting's role title |
| `startup_name` | `founder`, `executive`, `funding_round`, `job_posting` | The **first half** of the natural key naming the parent Startup |
| `startup_headquarters_location` | `founder`, `executive`, `funding_round`, `job_posting` | The **second half** of that key. Not read by the `startup` record type, which carries its own `headquarters_location` |

A shared column is declared once and takes the widest type its readers need: `title` is `string` 150 because `x_bst_startuptrk_jobposting.title` is 150 while the two people titles are choice values. The tables below list every column each record type reads, so a shared column appears in more than one table; the physical column count is 34, not the sum of the table lengths.

None of these thirty-four columns carries a choice list. Choice normalisation happens at transform time under cleaning rule 3, so an unmatched incoming value loads into staging unchanged. The four money columns are `decimal` here and `currency` on the entity tables. `active` carries no staging default, so a blank incoming value stays blank and cleaning rule 4 can see it; the `active` defaults on `x_bst_startuptrk_startup` and `x_bst_startuptrk_jobposting` are unaffected.

`headquarters_location` is read by the `startup` record type only, and it is the second half of a Startup's identity. Cleaning rule 2 de-duplicates Startup records on `name` **plus** `headquarters_location`, so that pair — not the name alone — is a Startup's identity within one load, and the record that survives de-duplication is the one a child row resolves to.

**A child row therefore names its parent with the same pair, through two columns.** `startup_name` carries the name and `startup_headquarters_location` carries the headquarters, and `IngestionMapper.resolveStartupKey()` resolves the pair through the same bounded matcher the natural-key upsert uses: the name is matched case- and whitespace-insensitively against `x_bst_startuptrk_startup.name`, each candidate is confirmed on the normalised headquarters, and the read stops at two confirmed matches because two establishes ambiguity.

Resolving on the name alone would be a different key from the one the de-duplication enforces, and the failure is not hypothetical: two startups may legitimately share a name across `Boston, MA` and `Cambridge, MA`, and a name-only resolver would attach the child to whichever one it happened to read first, or refuse both as ambiguous. **There is therefore no name-only path**: both halves are required, and a child row that carries only a name does not identify a parent at all. The outcomes are explicit:

| The child row supplies | Outcome |
| --- | --- |
| Both halves, matching exactly one startup | **Resolved** onto that startup |
| Both halves, matching none | **Rejected**, reason `no startup carries the name and headquarters location` |
| Both halves, matching more than one startup | **Rejected as ambiguous**, reason `the name and headquarters location already match (<n> startup records)`. Nothing is guessed and no candidate is picked |
| A name with no headquarters | **Rejected before any read**, reason `the row carries no parent headquarters location, and the startup key is the name together with the headquarters location`. The rejection names the remedy rather than resolving on a narrower key |
| No name | **Rejected**, reason `the value is blank` |

The middle row is the one that would previously have resolved. A blank second half used to fall back to a name-only match, which meant the resolver silently used a **different** key from the one rule 2 de-duplicates on; a child row could then attach to a company that was never the one the source named. The fallback is removed rather than narrowed, because there is no threshold at which guessing a parent is preferable to reporting that the row did not identify one.

`x_bst_startuptrk_ingest_staging.startup_headquarters_location` is `string` 100, matching the entity column it confirms against. It is a **transport** column: it is never written to any entity table, it exists only to carry the second half of the key, and the per-branch outcomes are tabulated in [`../sample-data/README.md`](../sample-data/README.md).

Record type `startup` — twelve columns.

| Column | Platform type | Max length | Default | Target field |
| --- | --- | --- | --- | --- |
| `name` | `string` | 100 | — | `x_bst_startuptrk_startup.name` |
| `description` | `string` | 4000 | — | `x_bst_startuptrk_startup.description` |
| `industry` | `string` | 40 | — | `x_bst_startuptrk_startup.industry` |
| `founded_year` | `integer` | — | — | `x_bst_startuptrk_startup.founded_year` |
| `headquarters_location` | `string` | 100 | — | `x_bst_startuptrk_startup.headquarters_location` |
| `website` | `string` | 255 | — | `x_bst_startuptrk_startup.website` |
| `logo_url` | `string` | 255 | — | `x_bst_startuptrk_startup.logo_url` |
| `funding_stage` | `string` | 40 | — | `x_bst_startuptrk_startup.funding_stage` |
| `total_funding_usd` | `decimal` | — | — | `x_bst_startuptrk_startup.total_funding_usd` |
| `active` | `string` | 10 | — | `x_bst_startuptrk_startup.active` |
| `institutional_funding_last_5yrs` | `boolean` | — | `false` | `x_bst_startuptrk_startup.institutional_funding_last_5yrs` |
| `employee_count_range` | `string` | 20 | — | `x_bst_startuptrk_startup.employee_count_range` |

Record types `founder` and `executive` — seven columns, shared by both. The target table is `x_bst_startuptrk_founder` on a `founder` row and `x_bst_startuptrk_executive` on an `executive` row.

| Column | Platform type | Max length | Default | Target field |
| --- | --- | --- | --- | --- |
| `name` | `string` | 100 | — | `name` on Founder or Executive |
| `startup_name` | `string` | 100 | — | The `startup` reference on Founder or Executive, resolved from the Startup `name` **plus** `startup_headquarters_location` |
| `startup_headquarters_location` | `string` | 100 | — | Not written. Confirms the parent Startup during reference resolution |
| `title` | `string` | 150 | — | `title` on Founder or Executive |
| `bio` | `string` | 2000 | — | `bio` on Founder or Executive |
| `linkedin_url` | `string` | 255 | — | `linkedin_url` on Founder or Executive |
| `contact_email` | `string` | 100 | — | `contact_email` on Founder or Executive |

Record type `investor` — five columns.

| Column | Platform type | Max length | Default | Target field |
| --- | --- | --- | --- | --- |
| `name` | `string` | 100 | — | `x_bst_startuptrk_investor.name` |
| `type` | `string` | 30 | — | `x_bst_startuptrk_investor.type` |
| `focus_areas` | `string` | 255 | — | `x_bst_startuptrk_investor.focus_areas` |
| `website` | `string` | 255 | — | `x_bst_startuptrk_investor.website` |
| `aum_usd` | `decimal` | — | — | `x_bst_startuptrk_investor.aum_usd` |

`x_bst_startuptrk_investor.portfolio_count` has no staging column. It is calculated, not staged.

Record type `funding_round` — nine columns.

| Column | Platform type | Max length | Default | Target field |
| --- | --- | --- | --- | --- |
| `startup_name` | `string` | 100 | — | `x_bst_startuptrk_fundinground.startup`, resolved from the Startup `name` **plus** `startup_headquarters_location` |
| `startup_headquarters_location` | `string` | 100 | — | Not written. Confirms the parent Startup during reference resolution |
| `round_type` | `string` | 40 | — | `x_bst_startuptrk_fundinground.round_type` |
| `amount_usd` | `decimal` | — | — | `x_bst_startuptrk_fundinground.amount_usd` |
| `round_date` | `glide_date` | — | — | `x_bst_startuptrk_fundinground.round_date` |
| `lead_investor_name` | `string` | 100 | — | `x_bst_startuptrk_fundinground.lead_investor`, resolved from the Investor `name` |
| `participating_investor_names` | `string` | 1000 | — | One `x_bst_startuptrk_m2m_round_investor` row per Investor `name` in a **comma separated list** |
| `valuation_usd` | `decimal` | — | — | `x_bst_startuptrk_fundinground.valuation_usd` |
| `source_url` | `string` | 255 | — | `x_bst_startuptrk_fundinground.source_url` |

Record type `job_posting` — ten columns.

| Column | Platform type | Max length | Default | Target field |
| --- | --- | --- | --- | --- |
| `startup_name` | `string` | 100 | — | `x_bst_startuptrk_jobposting.startup`, resolved from the Startup `name` **plus** `startup_headquarters_location` |
| `startup_headquarters_location` | `string` | 100 | — | Not written. Confirms the parent Startup during reference resolution |
| `title` | `string` | 150 | — | `x_bst_startuptrk_jobposting.title` |
| `department` | `string` | 40 | — | `x_bst_startuptrk_jobposting.department` |
| `location` | `string` | 100 | — | `x_bst_startuptrk_jobposting.location` |
| `remote_type` | `string` | 20 | — | `x_bst_startuptrk_jobposting.remote_type` |
| `seniority` | `string` | 20 | — | `x_bst_startuptrk_jobposting.seniority` |
| `posted_date` | `glide_date` | — | — | `x_bst_startuptrk_jobposting.posted_date` |
| `url` | `string` | 255 | — | `x_bst_startuptrk_jobposting.url` |
| `active` | `string` | 10 | — | `x_bst_startuptrk_jobposting.active` |

Nine columns are read by more than one record type, and six of those are skipped as already counted when the types are walked in the order below — `name`, `website`, `startup_name`, `startup_headquarters_location`, `title` and `active`; the other three, `bio`, `linkedin_url` and `contact_email`, are shared only between `founder` and `executive`, which this walk counts as one contributor. Each shared column is counted once: the `startup` type contributes 12, `investor` adds `type`, `focus_areas` and `aum_usd`, `founder` and `executive` add `startup_name`, `startup_headquarters_location`, `title`, `bio`, `linkedin_url` and `contact_email`, `funding_round` adds `round_type`, `amount_usd`, `round_date`, `lead_investor_name`, `participating_investor_names`, `valuation_usd` and `source_url`, and `job_posting` adds `department`, `location`, `remote_type`, `seniority`, `posted_date` and `url`. 12 + 3 + 6 + 7 + 6 = 34 flattened columns, and 7 + 34 = 41.

#### The three-way staging contract

The column names above bind three artifacts, and all three must change together.

| Leg | Artifact | Role |
| --- | --- | --- |
| a | The header rows of the six CSVs under `../sample-data/`, documented in [`../sample-data/README.md`](../sample-data/README.md) | The wire format |
| b | The `x_bst_startuptrk_ingest_staging` dictionary records in [`../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml`](../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml) | **Authoritative** |
| c | The field mapping in [`./manual-build/06-staging-table-csv-import.md`](./manual-build/06-staging-table-csv-import.md) | The load instructions |

A change to any one leg alone breaks the fallback path **silently**: the Data Import Wizard maps columns by header name, so a renamed or misspelled column is left unmapped, the field loads empty, and no error is raised.

[`../sample-data/README.md`](../sample-data/README.md) is the authoritative statement of the CSV header rows, including their order within each file, and it is not restated here.

#### Retention

**Rows in this table are not meant to be permanent, and no shipped artifact removes them.** It is the only table in the application holding verbatim upstream payloads and unvalidated person data, and bounding how long it keeps them is an **operator-owned obligation** rather than a delivered mechanism — no Script Include, property or scheduled job in this delivery clears or deletes a staging row. The obligation is stated in full, with the columns worth clearing, the three worth keeping and the data-subject erasure surfaces, under [Staging and counter data retention — an operator-owned procedure](#staging-and-counter-data-retention--an-operator-owned-procedure). The routine form of it is the clear-down step of [`./manual-build/06-staging-table-csv-import.md`](./manual-build/06-staging-table-csv-import.md). The absence of any delivered retention, minimisation or erasure mechanism is flagged in [`./gaps-and-flags.md`](./gaps-and-flags.md).

### 10. `x_bst_startuptrk_rate_limit_counter`

Label **Rate limit counter**. Four columns. The display column is `api_resource`.

| Column | Platform type | Max length | Mandatory | Default | Choice values | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `caller` | `reference` to `sys_user` | 32 | — | — | — | The authenticated caller the window belongs to |
| `window_start` | `glide_date_time` | — | — | — | — | Start of the fixed window |
| `request_count` | `integer` | — | — | `0` | — | Requests counted in the window |
| `api_resource` | `string` | 100 | — | — | — | The logical REST resource the window applies to |

This table backs the fixed-window, per-caller request accounting behind the rate-limit response documented in [`./api-reference.md`](./api-reference.md). Two shipped system properties govern the accounting: `x_bst_startuptrk.rest.rate_limit_requests` is `100` and `x_bst_startuptrk.rest.rate_limit_window_seconds` is `60`. The response body and status the service returns when the budget is exhausted are specified in [`./api-reference.md`](./api-reference.md) and are not restated here.

**One row is intended per caller, per resource, per window, and the counter is a plain read-increment-write.** Windows are aligned buckets: `window_start` is the current time truncated to a whole multiple of `x_bst_startuptrk.rest.rate_limit_window_seconds`, so every request inside one window derives the identical value. `RateLimitService` queries the three columns `caller`, `api_resource` and `window_start` together, increments `request_count` on the row it finds, and inserts a row with `1` when the window has none. A non-unique composite index on those three columns serves that query and is listed under [Declared indexes](#declared-indexes).

**No uniqueness is enforced on the tuple, and the increment is not concurrency-safe.** Two requests arriving together can each find no row and each insert one, or each read the same count and each write the same increment, so under genuine concurrency the effective limit can overshoot slightly. That is an accepted prototype-scope outcome, not an oversight; the decision and the mitigation paths deliberately left unbuilt are recorded at `D-040` in [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md).

The scheduled job **Prune rate limit counters** runs hourly and deletes every row whose `window_start` is further in the past than `x_bst_startuptrk.rest.rate_limit_window_seconds` — every row whose window has closed. Retention is therefore the window length itself: at the shipped `60`, a closed row is removed by the next hourly pass, and the table does not grow without bound.

`caller` references `sys_user`, which sits outside the `x_bst_startuptrk` scope. The reference is read-only in effect: the application creates counter rows and never creates, updates or deletes a `sys_user` record. Because `caller` is the only column on any of the ten tables that identifies a natural person by reference, counter rows are one of the three surfaces an operator clears when servicing an erasure request; see [Staging and counter data retention — an operator-owned procedure](#staging-and-counter-data-retention--an-operator-owned-procedure).

This table is readable, writable, creatable and deletable by the `x_bst_startuptrk.admin` role only, and by no other role on any operation; the full matrix is under [Supporting tables](#supporting-tables) and in [`./access-control.md`](./access-control.md).

## Staging and counter data retention — an operator-owned procedure

`x_bst_startuptrk_ingest_staging` is the only table in the application that holds **unvalidated third-party personal data**: `raw_payload`, up to 8,000 characters of the upstream response verbatim, alongside `name`, `title`, `bio`, `linkedin_url` and `contact_email`. Nothing about the ingestion pipeline requires that data to survive the run that consumed it. `x_bst_startuptrk_rate_limit_counter` is the only table that identifies a natural person by reference, through `caller`.

**No artifact in this delivery bounds its lifetime, and that is a deliberate scope decision rather than an oversight.** Neither the frozen prompt nor the Agent Action Plan asks for a retention lifecycle, and the plan's inventories are binding: eight Script Includes at section 0.4.5, eleven system properties at section 0.4.7, one scheduled job at section 0.4.2. An earlier revision shipped a ninth Script Include, two further properties and a second scheduled job to implement one; all four records were removed to hold the delivered inventory to the plan, and the removal is recorded in [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md).

What follows is therefore addressed to the **instance operator**, who owns it. It is stated in full so the obligation is legible and actionable, not so that it can be assumed to be handled.

### What the operator owns

| # | Obligation | Why it falls to the operator |
| --- | --- | --- |
| 1 | **Bound how long a settled staging row keeps its personal payload.** A row whose `import_state` is `processed`, `rejected` or `error` has been read; its `raw_payload`, `name`, `title`, `bio`, `linkedin_url`, `contact_email`, `description`, `website`, `logo_url`, `url` and `source_url` serve no further purpose and can be cleared. A row still `pending` must **never** be touched: the transform has not consumed it, and clearing it destroys the input. | The application ships no sweep. A scheduled cleanup, or a periodic manual clear from the list view, is instance housekeeping. |
| 2 | **Bound how long a staging row survives at all.** Deleting rows beyond a chosen age, whatever their state, keeps the table from growing without bound. Guide 06 already tells the operator to clear the staged rows once a load has been reconciled — see [`./manual-build/06-staging-table-csv-import.md`](./manual-build/06-staging-table-csv-import.md) — and that step is the routine form of this obligation. | Same. |
| 3 | **Service a data-subject erasure request.** Person data is reachable on three surfaces and clearing one alone leaves the subject present: `contact_email` on matching `x_bst_startuptrk_founder` and `x_bst_startuptrk_executive` rows; every matching `x_bst_startuptrk_ingest_staging` row, which is working data and is deleted outright; and every `x_bst_startuptrk_rate_limit_counter` row whose `caller` resolves to the subject's `sys_user` record — that surface needs an address, because a counter row identifies its caller by reference and not by name. | An erasure request is a legal and operational act with a decision in it — whether a published Founder or Executive record is removed as well as cleared — and it is not automated by this delivery. |
| 4 | **Bound the flow execution context, which is a separate retention surface.** Flow Designer persists each execution's step inputs and outputs in the platform's own flow execution tables, and two step outputs of each ingestion flow carry upstream content into them: the verbatim response body of step 3 and the mapped row set of step 5. Those tables sit **outside** the `x_bst_startuptrk` scope, so nothing in this delivery's access control or retention posture reaches them, and clearing the staging table does **not** clear them. The full procedure is recorded under **Flow execution context retention** in [`./gaps-and-flags.md`](./gaps-and-flags.md). | The flow execution tables are platform tables. Prompt section 6.0 forbids this application from modifying anything outside its scope, so the retention window, the cleanup schedule and the read access on those tables are all the platform owner's to set. |
| 5 | **Keep `sys_user` untouched while doing any of it.** Prompt section 6.0 forbids this application from modifying anything outside the `x_bst_startuptrk` scope. The user table is **read** to resolve an address to a caller identifier; no `sys_user` record is created, updated or deleted. | The prohibition binds the application; the operator is asked to honour it in the procedure too. |

### Three columns worth preserving when clearing a settled row

Where the operator does implement obligation 1, three columns are worth keeping rather than clearing, because they carry no personal data and are what makes a past run reconstructable: `import_state` and `import_run`, which record that a record was seen, by which run, and how it settled; and `error_message`, which is not upstream text at all — the application constructs it from opaque tokens, being a record-type token, an opaque record reference, a physical table name, or the names of the mandatory fields a row was missing. It identifies the failure without identifying the person. The scalar columns carrying no personal or free-text data — `source_system`, `record_type`, `run_provenance`, `startup_name`, `headquarters_location`, `location`, `lead_investor_name`, `participating_investor_names`, and the choice, amount and date columns — are likewise worth keeping.

### Clearing staging rows

Clearing the table is an administrative act with two supported routes, and both are ordinary platform operations rather than application code.

1. **The list view.** Open the **Ingestion staging** module of the Boston Startup Tracker application menu as a caller holding `x_bst_startuptrk.admin`, filter on `import_run`, on `import_state`, or on `sys_created_on`, and delete the selected rows. Deleting a staging row removes no entity record: the entity records are separate rows and the staging table holds no reference to them.
2. **A background script inside the scope.** A `GlideRecord` on `x_bst_startuptrk_ingest_staging` with the same filter and `deleteMultiple()`. It must be run with the scope selector set to **Boston Startup Tracker**, because the table is `package_private`.

Two rules bind either route.

- **A row still `pending` or `in_progress` must not be deleted while a run may read it.** A `pending` row is the transform's input and an `in_progress` row is claimed by a run; deleting either mid-run removes the input before it is consumed. Settle the run first, or return the claimed rows to the queue as guide 06 specifies.
- **`sample-data/` is the reproducible source.** The six CSVs are version-controlled and nothing on the instance modifies them, so a cleared table is restored by re-running the import.

### What needs no retention procedure

**The counter table bounds itself.** The scheduled job **Prune rate limit counters** — the one scheduled job this delivery ships — runs hourly and deletes every row whose window has closed, so `x_bst_startuptrk_rate_limit_counter` does not grow without bound and needs no separate policy. Only obligation 3 touches it, and only for a named subject.

**No personal data reaches the logs, so no log erasure procedure is needed.** `IngestionLogger` writes no external name, email address, biography, URL or upstream message into the flow execution log or the system log in the first place. Two rules produce that property, and both are unconditional:

| Rule | Mechanism | Outcome |
| --- | --- | --- |
| An identifier is opaque or it is dropped | `_identifier()` passes a value through only when it is a 32-character platform record identifier or a `<kind>:<token>` opaque reference; anything else becomes the literal `(redacted)` | A log line names a **record**, never a person |
| A value is a short enumeration label or it is dropped | `_choiceValue()` passes a value through only when its field is not one of the sensitive names **and** the value matches a short-label shape — first character alphanumeric, at most 40 characters, drawn from letters, digits, spaces and `+ . _ / -`; anything else becomes `(redacted)`, and an empty value becomes `(blank)` | A mis-spelled choice value is actionable; a pasted biography or address is not recorded at all |

**Nothing derived from a dropped value is recorded.** There is no hash, digest or fingerprint of any supplied value anywhere in the pipeline, so there is nothing an offline guess could be tested against. Correlation across the log lines of one row comes from two mechanisms that are computed from nothing the record contains: `IngestionLogger.reference(kind, token)`, which names the **platform record**, and `IngestionLogger.ordinal(kind)`, a per-run arrival ordinal used where no platform identifier exists yet. Both are per-run, so neither correlates a row across runs. The policy is specified in [`../sample-data/README.md`](../sample-data/README.md).

**The flow execution context is not the log, and it does need a procedure.** The sentence above is about what the application *writes*; it says nothing about what the platform *records around* it. Flow Designer persists step inputs and outputs, and two of each ingestion flow's step outputs carry upstream content by necessity — the verbatim response body step 3 returns, and the mapped row set step 5 produces. That is obligation 4 above and it is a genuinely separate surface: it is outside this application's scope, it is untouched by clearing the staging table, and no artifact of this delivery bounds it.

## Derivations

### Investor.portfolio_count

`x_bst_startuptrk_investor.portfolio_count` is the count of **distinct** startups reachable from an investor by **either** of two paths:

- **a.** a funding round whose `lead_investor` is that investor, reached as `x_bst_startuptrk_fundinground.lead_investor`; or
- **b.** a row of `x_bst_startuptrk_m2m_round_investor` whose `investor` is that investor, giving a funding round the investor participated in.

Each path yields a set of `x_bst_startuptrk_startup` identifiers, taken from the `startup` reference of the funding rounds it reaches. The two sets are **unioned before counting**, and the count is the size of the union. An investor that led one round of a company and participated in another round of the **same** company therefore counts that company **once**. An investor with no rounds on either path has a `portfolio_count` of `0`, which is also the dictionary default.

The `InvestorPortfolioService` Script Include owns the derivation. Its methods are `countPortfolio(investorId)`, which returns the derived count for one investor; `recalculate(investorId)`, which derives the count and writes it to the record only when the derived value differs from the stored one; `recalculateMany(investorIds)`, which recalculates a de-duplicated set of investors; and `recalculateAll()`, which recalculates every investor and is the method to invoke after a bulk load. The same class owns the participation reads that share its two-table traversal — `participantsForRounds(roundIds)` and `refreshRoundParticipants(roundId)` — plus the single-pair helper `linkInvestorToRound(roundId, investorId)`, so the join table's derived surfaces are read in one place. The ingestion path's participation write is `IngestionMapper.linkParticipants()`; see [8. `x_bst_startuptrk_m2m_round_investor`](#8-x_bst_startuptrk_m2m_round_investor).

#### The column is read-only, and what that means precisely

The `portfolio_count` dictionary entry carries `read_only = true`. On the target release that flag makes the column non-editable on the form, in the list editor and through the Table API, while leaving unsecured server-side `GlideRecord` writes unaffected. The two business rules and `InvestorPortfolioService` write the column through `GlideRecord`; every other path — an administrator typing into the native form, a list edit, a Table API `PUT` — is refused. The column still appears on the investor form and list, rendered as a read-only display of the derived value.

The REST layer is closed independently of the dictionary flag: the investor `create` and `update` operations separate the fields they will accept from the fields they will return, and `portfolio_count` appears only in the returned set. A request body naming `portfolio_count` is ignored rather than applied. This is stated as a contract in [`./api-reference.md`](./api-reference.md).

#### How the derivation is queried

Both paths are read with bounded queries, and **one constraint governs every one of them**: a grouped aggregate groups only by a field of the table it aggregates, never by a dot-walked field. `GlideAggregate.groupBy()` is documented against a field of the aggregated table, and grouping a join-table aggregate by `funding_round.startup` is outside that contract — a row the traversal must see can be dropped, which silently removes a participation-only company from the count. The participation path is therefore expressed as a **two-stage traversal**, and the second stage is an ordinary bounded read rather than a grouping.

- The **lead** path is a grouped aggregate over `x_bst_startuptrk_fundinground` filtered on `lead_investor`, grouped by `startup` — a column of the table being aggregated. It returns one row per distinct startup: an investor that led forty rounds of one company reads one row.
- The **participation** path is two stages. **Stage one** is a grouped aggregate over `x_bst_startuptrk_m2m_round_investor` filtered on `investor` and grouped by `funding_round` — again a column of the table being aggregated — which returns one row per distinct round the investor participated in. **Stage two** reads those rounds from `x_bst_startuptrk_fundinground` with `sys_id IN` over batches of at most **200** identifiers and takes each round's `startup`. The batch size is the `BATCH_SIZE` constant on the Script Include. No query is handed the investor's complete round list, and no participation row depends on a dot-walked grouping.
- The two result sets are keyed into one set, so the union is formed before the size is taken and a company reached by both path **a.** and path **b.** counts once.

`recalculateAll()` derives every investor's count with the same two-stage shape, from three bounded passes. One grouped aggregate over `x_bst_startuptrk_fundinground`, grouped by `lead_investor` and `startup`, yields the lead contribution. One windowed pass over the same table, in windows of `BATCH_SIZE` rows, builds the **round-to-startup map**. One grouped aggregate over the join table, grouped by `investor` and `funding_round`, yields every investor-and-round pair, and each pair is resolved to a startup through that map. The method then makes a single windowed pass over the investors, writing only those whose stored value differs from the derived value, so a recalculation over an already-correct table performs **zero** writes. The method returns the number of investors it wrote, which is the figure to record after a bulk load.

**What to verify.** The case that distinguishes a correct traversal from the unsupported grouping is an investor that **only** participates: it leads no round at all, and reaches its companies exclusively through join rows. Create one, link it to a round of a company it has never led, and confirm both `countPortfolio()` and `recalculateAll()` report that company. Under the dot-walked grouping that investor can read `0`.

Two business rules maintain the stored value. Both delegate to `InvestorPortfolioService`, and each recalculates only the investors its trigger affects.

| Business rule | Table | When | Operations | What it recalculates |
| --- | --- | --- | --- | --- |
| Recalculate investor portfolio on funding round | `x_bst_startuptrk_fundinground` | After | Insert, update, delete | The round's `lead_investor`. On an update it recalculates **both** the previous and the new `lead_investor`, and it handles a change to the round's `startup` reference. On a delete it recalculates the lead investor of the deleted round and every investor linked to it through the join table. |
| Recalculate investor portfolio on round investor link | `x_bst_startuptrk_m2m_round_investor` | After | Insert, **update**, delete | The `investor` named on the affected row **and**, on an update, the `investor` named on the previous row. The same rule refreshes the derived `participating_investors` projection on the current **and** the previous `funding_round`, so re-pointing a link maintains both ends. |

Two operational instructions follow. Both are requirements.

- Any ingestion or import path that writes `x_bst_startuptrk_fundinground` or `x_bst_startuptrk_m2m_round_investor` **must run business rules**, otherwise the stored count is not maintained for the records it writes.
- `InvestorPortfolioService.recalculateAll()` **must be invoked from a background script after any bulk load**, including every load of the fallback dataset whose files and load order are documented in [`../sample-data/README.md`](../sample-data/README.md) and whose transform is specified in [`./manual-build/06-staging-table-csv-import.md`](./manual-build/06-staging-table-csv-import.md).

The decision behind the derivation is recorded in [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md).

## Referential rules

### Reference and cascade rules

Nine reference columns exist across the ten tables. Every mandatory child reference and both join-table parent references are set to **cascade delete**. The two references that are not mandatory carry no cascade rule.

| Source table | Column | Target table | Mandatory | Cascade behaviour |
| --- | --- | --- | --- | --- |
| `x_bst_startuptrk_founder` | `startup` | `x_bst_startuptrk_startup` | M | Cascade delete |
| `x_bst_startuptrk_executive` | `startup` | `x_bst_startuptrk_startup` | M | Cascade delete |
| `x_bst_startuptrk_fundinground` | `startup` | `x_bst_startuptrk_startup` | M | Cascade delete |
| `x_bst_startuptrk_jobposting` | `startup` | `x_bst_startuptrk_startup` | M | Cascade delete |
| `x_bst_startuptrk_newsarticle` | `startup` | `x_bst_startuptrk_startup` | M | Cascade delete |
| `x_bst_startuptrk_fundinground` | `lead_investor` | `x_bst_startuptrk_investor` | — | None |
| `x_bst_startuptrk_m2m_round_investor` | `funding_round` | `x_bst_startuptrk_fundinground` | M | Cascade delete |
| `x_bst_startuptrk_m2m_round_investor` | `investor` | `x_bst_startuptrk_investor` | M | Cascade delete |
| `x_bst_startuptrk_rate_limit_counter` | `caller` | `sys_user` | — | None |

The operational consequences are these:

- Deleting a startup deletes its founders, its executives, its funding rounds, its job postings and its news articles. Deleting the funding rounds in turn deletes the join-table rows that reference them.
- Deleting a funding round deletes the join-table rows that reference it.
- Deleting an investor deletes the join-table rows that reference it.
- Deleting an investor does **not** delete a funding round that names it as `lead_investor`; that column is not mandatory and carries no cascade rule, so the reference is left as it stands.
- Deleting a `sys_user` record does not delete rate-limit counter rows. `caller` is not mandatory and carries no cascade rule. The **Prune rate limit counters** scheduled job removes closed windows.

A delete that cascades into funding rounds or join-table rows fires the two portfolio business rules, so `portfolio_count` is maintained through a cascade.

The decision behind the cascade setting is recorded in [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md).

### Declared indexes

The Update Set declares database indexes as `sys_index` records alongside the table definitions, so they are created by the same commit that creates the tables rather than added by hand afterwards. Each record names its table, the ordered columns of the index, and whether the index is unique.

**Thirteen** indexes are declared. Column order is significant and is reflected in each record's name.

**Every index here exists for a predicate the application actually issues, and each row names that predicate.** An index declared for a query nobody runs is not free: it is written on every insert and update of its table and read by nothing, so it is pure cost. One such index was declared and has been removed — a three-column index on the counter table's `caller`, `api_resource` and `window_start`, which never served a query because `RateLimitService` looks a counter row up by its composite `window_key` and not by those three columns.

| # | Table | Columns, in order | Unique | The predicate it serves |
| --: | --- | --- | --- | --- |
| 1 | `x_bst_startuptrk_m2m_round_investor` | `funding_round`, `investor` | **Yes** | Pair uniqueness, and the round-to-investors read behind the REST participant array and the `participating_investors` projection |
| 2 | `x_bst_startuptrk_m2m_round_investor` | `investor`, `funding_round` | No | The reverse traversal: the participation path of the `portfolio_count` derivation |
| 3 | `x_bst_startuptrk_fundinground` | `lead_investor`, `startup` | No | The lead path of the `portfolio_count` derivation. Because `startup` is the second column, the grouped aggregate is answered from the index without reading the rounds |
| 4 | `x_bst_startuptrk_rate_limit_counter` | `window_start` | No | The pruning range scan in `RateLimitService.prune()`, and the aggregate count that precedes it |
| 5 | `x_bst_startuptrk_startup` | `name` | No | The `startup` natural key, and the `name` filter of `/startups` and the portal search. Read on **every** ingested row of every type, because a child's parent resolves through it |
| 6 | `x_bst_startuptrk_investor` | `name` | No | The `investor` natural key, the `name` filter of `/investors`, and lead and participant resolution |
| 7 | `x_bst_startuptrk_founder` | `startup`, `name` | No | The `founder` natural key, and the founders pane of the company profile |
| 8 | `x_bst_startuptrk_executive` | `startup`, `name` | No | The `executive` natural key, and the nested `GET /founders/{startup_id}/executives` |
| 9 | `x_bst_startuptrk_jobposting` | `startup`, `title` | No | The `job_posting` natural key, and the jobs pane and `/jobs` filtered by startup |
| 10 | `x_bst_startuptrk_fundinground` | `startup`, `round_date` | No | The **fallback** `funding_round` natural key, and the funding pane and `/funding-rounds` filtered by startup and ordered by date |
| 11 | `x_bst_startuptrk_fundinground` | `source_url` | No | The **primary** `funding_round` natural key. Every ingested round is looked up on its provider locator first, and only a round that carries none falls back to index 10 |
| 12 | `x_bst_startuptrk_newsarticle` | `startup`, `published_date` | No | The news pane and `/news` filtered by startup and ordered by date |
| 13 | `x_bst_startuptrk_ingest_staging` | `source_system`, `import_state`, `import_run` | No | The bounded staging read in `IngestionMapper.ingestStaging()`, which matches all three for equality, and the settled-state filters of the operator-owned clear-down |

Index 1 is a **constraint**, not an optimisation: it enforces "one row links one funding round to one participating investor" on every write path, including a direct form or import write. `InvestorPortfolioService.linkInvestorToRound()` checks for the pair before inserting.

The other twelve are optimisations, and they fall into four groups. Indexes 2, 3 and 6 serve the derivation described in [Investor.portfolio_count](#investorportfolio_count). Indexes 5 to 11 are the **natural keys** every ingestion write looks up before deciding to insert or update, which is what makes a recurring run update rather than duplicate; their leading columns are the equality components of each key, with the text component matched case- and whitespace-insensitively against a candidate set the index bounds. Two of them cover one record type between them, because the `funding_round` key is an ordered pair of alternatives: index 11 serves the primary lookup on `source_url` and index 10 the fallback on `startup` and `round_date`. Indexes 7 to 10 and index 12 also serve the child-collection reads of the Service Portal profile panes and the corresponding REST list filters, each of which is a query on the parent reference ordered by the pane's sort column, while indexes 5 and 6 serve the `name` filters of `/startups` and `/investors` and the portal search. Indexes 4 and 13 serve the maintenance sweeps: the counter pruning described in [10. `x_bst_startuptrk_rate_limit_counter`](#10-x_bst_startuptrk_rate_limit_counter) and the staging read described in [Staging and counter data retention — an operator-owned procedure](#staging-and-counter-data-retention--an-operator-owned-procedure).

### Dot-walking, not joins

Related data is reached by **dot-walking a reference column**, never by an application-side join. `x_bst_startuptrk_fundinground.startup.name` is the startup name of a funding round; `x_bst_startuptrk_m2m_round_investor.funding_round.startup.name` is the startup name behind a participation row. Dot-walked reads are subject to the same access control as direct reads, so a dot-walk cannot be used to reach a premium-gated column that the caller's roles do not grant.

Physical table names are always fully scope-prefixed. A query, a reference qualifier, a REST operation, a widget server script or an ATF step names `x_bst_startuptrk_startup`, never the bare entity name `startup`. Script Includes are addressed as `x_bst_startuptrk.<ClassName>` from outside the scope and by bare class name within it.

## The startup inclusion criteria

A startup is eligible for Service Portal search results only if:

> `active` = true **AND** `headquarters_location` contains **"Boston"** OR **"Cambridge, MA"** (case-insensitive substring).

Records failing these criteria **remain in the table for administrative visibility** and are excluded from all portal-facing and non-administrative list and search queries.

The filter tests **only** two columns: `x_bst_startuptrk_startup.active` and `x_bst_startuptrk_startup.headquarters_location`. `x_bst_startuptrk_startup.institutional_funding_last_5yrs` is a premium-gated display attribute and is **not** part of the predicate. The resolution of that point is stated here and is recorded in [`./gaps-and-flags.md`](./gaps-and-flags.md).

`StartupSearchService` is the single Script Include that builds the query. Both callers use it, so the filter cannot drift between the two surfaces: the `/startups` REST list operation documented in [`./api-reference.md`](./api-reference.md), and the portal search widget on the Home/Search route.

The two location tokens are read from the system property `x_bst_startuptrk.inclusion.location_tokens`, whose shipped value is `Boston,Cambridge, MA`. Changing the property changes the tokens the predicate tests, with no code change.

The predicate is built and applied in two steps, and the split is what lets one predicate serve both the page and its count. `StartupSearchService.buildPlan(filters, applyInclusion)` returns a **query plan** — a plain object carrying the inclusion flag, the location tokens read from the property, and the validated `name`, `industry` and `location` filters:

```text
{ inclusion: true,
  tokens: [ 'Boston', 'Cambridge, MA' ],
  name: '', industry: '', location: '' }
```

`StartupSearchService.applyPlan(query, plan)` then applies that plan to a `GlideRecordSecure` through the condition API: `addQuery('active', true)`, then `addQuery('headquarters_location', 'CONTAINS', tokens[0])` whose returned condition carries an `addOrCondition('headquarters_location', 'CONTAINS', …)` for every remaining token, then one `addQuery` per supplied caller filter. `search(plan, limit, offset)` applies the plan, orders by `name` then `sys_id` and positions the window; the count applies **the same plan object** to its own query, which is what makes `total_count` agree with the page contents by construction rather than by coincidence.

**The count is authorized by a role test, not by a probe read.** `total_count` is produced by a `GlideAggregate` `COUNT`, and an aggregate does not evaluate access controls — so the count needs a gate of its own. `RestResponseBuilder.countState(table, applyConditions)` calls **`hasAnyAppRole()`** before it constructs the aggregate, which tests `gs.hasRole()` against `x_bst_startuptrk.admin`, then `x_bst_startuptrk.premium_user`, then `x_bst_startuptrk.user`. A caller holding none of the three gets `{ total: 0, denied: true }` and the aggregate is never built; the operation then answers `403` through `rejectDeniedCount()`. A role test is the correct gate here because record-level read on all seven entity tables is granted to exactly those three roles and to nothing else, so holding one of them *is* permission to read the rows being counted — the invariant is stated in [`./access-control.md`](./access-control.md).

The rejected alternative was to open a `GlideRecordSecure` on the table and call `canRead()` before the aggregate. That cannot serve as a table-right check: it answers a question about one record the query may not have returned at all, so on an empty table, a newly loaded table, or a table whose first row is filtered out by the plan, it is **inconclusive** rather than permitting or denying. Reading an inconclusive answer as a denial would suppress a legitimate zero; reading it as a grant would gate nothing. The role test answers the question that was actually being asked.

**The windowed query counts nothing.** `search()` positions the page with `chooseWindow(offset, offset + limit)` and then calls **`setNoCount()`**. The exact total has already come from the aggregate, so the windowed query is told not to count its own result set — without `setNoCount()` every list read would count the same conditions twice, once in the aggregate and once in the record query. The two calls are paired at all seven list sites. The caller-facing pagination contract is in [`./api-reference.md`](./api-reference.md).

The or-group carries the and-of-or grouping the criteria require: `active` true, and either location token matching. `CONTAINS` is a case-insensitive substring comparison.

In encoded-query form the equivalent predicate is `active=true^headquarters_locationLIKEBoston^ORheadquarters_locationLIKECambridge, MA`, where the grouping comes from `^OR` binding to the immediately preceding clause. The application does not build the predicate that way: every filter value is validated and bound as a parameter, and the validation contract is in [`./api-reference.md`](./api-reference.md).

One operational requirement applies to every caller of the filter: **the criteria are a query filter, not an ACL.** The platform does not apply them, so they must be applied identically to the result set **and** to the `total_count` returned with a paginated response. Applying them to one and not the other makes the count disagree with the page contents. Record-level read access to all seven entity tables is granted to all three roles, and the role difference is at field level only; see [`./access-control.md`](./access-control.md).

## How the ingestion transform respects this dictionary

Everything above is a declaration. This section is the contract the one writer that builds records dynamically — `IngestionMapper`, serving both flows and the staging transform — holds itself to, so a declaration here and a write there cannot disagree. The REST layer's equivalent contract, which validates a caller-supplied body rather than a source payload, is in [`./api-reference.md`](./api-reference.md).

### How an existing record is found before a write

Every write is an upsert, and each record type has a natural key the mapper resolves before it decides between an insert and an update. There are two lookup families and one matching rule, and the matching rule is what keeps the result independent of the database's collation.

| Record type | Natural key | Method |
| --- | --- | --- |
| `startup` | `name` **plus** `headquarters_location`, the cleaning-rule-2 key | `findExistingStartup(name, headquarters)` |
| `investor` | `name` alone | `findExistingInvestor(name)` |
| `founder`, `executive` | `startup` plus `name` | `findExistingByKey()` |
| `funding_round` | `startup` plus `round_date` plus `round_type`; falling back to `startup` plus `round_date` | `findExistingByKey()` |
| `job_posting` | `startup` plus `url`; falling back to `startup` plus `title` plus `posted_date` | `findExistingByKey()` |

Three properties are common to all of them.

1. **A candidate key is used only when the incoming record carries every one of its fields**, and the candidates are tried in the order listed, so the first complete key decides. A record carrying no complete key reports no match and is inserted. Values are compared **after** reference resolution, so `startup` in a key holds a resolved 32-character identifier rather than a name.
2. **Exactly one match updates; no match inserts; more than one match is refused.** An ambiguous key returns not-ok with a reason naming the count, the row is stamped `error` and **nothing is written** — no caller picks one of several matches arbitrarily.
3. **The comparison is case-insensitive and does not depend on the database collation.** This is the property worth stating precisely, because the obvious implementation gets it wrong.

**Why the query is a `STARTSWITH` pair and not an equality.** A case-insensitive match cannot be delegated to an `addQuery(field, value)` equality, because whether that comparison folds case is a property of the column's collation rather than of the application — on a case-sensitive collation a row differing only in case never comes back, and the deduplication silently inserts a second record. The mapper therefore narrows in the database and decides in script:

| Stage | What it does |
| --- | --- |
| Narrow | `_narrowText()` adds `STARTSWITH <first character, lower-cased>` and, when the character has a distinct upper case, an or-condition `STARTSWITH <first character, upper-cased>`. `STARTSWITH` is a substring comparison, so the narrowing is collation-independent in both arms. |
| Decide | Every candidate row the narrowing returns is compared in script by `_sameText()`, which lower-cases both sides and tests equality. **This comparison, not the query, is the key.** |

The consequence is that a case-differing row is always a candidate and is always matched, on any collation. The cost is that the narrowing is a first-character prefix rather than a full-value equality, so a name beginning with a very common letter returns more candidate rows than it matches; the candidates are ordered by `sys_id` and compared in one pass, and no stored normalised-key column is added because prompt section 1.0 declares the field list binding and complete.

### Only the columns of this document are writable, and only the writable ones

The mapper does not write whatever keys a source happens to send. It carries a **target field allowlist per record type**, and the write loop iterates the allowlist rather than the incoming record, so a key with no entry is read and discarded rather than written. Two consequences are the point of it:

- **`Investor.portfolio_count` is unreachable from ingestion.** It has no allowlist entry, so no payload key, no flattened staging column and no crafted `raw_payload` can set it. It is a derived column, and its only writers are the two business rules and `InvestorPortfolioService`, as described under [Investor.portfolio_count](#investorportfolio_count). This closes the gap that the dictionary `read_only` flag alone leaves open, since that flag does not stop an unsecured server-side write.
- **`FundingRound.participating_investors` is unreachable too.** It is the read-only projection of the join table. The mapper carries the incoming participant list as a **transport** value that is resolved into join rows and then removed before the write, so participation is only ever recorded where it is authoritative. See [5. `x_bst_startuptrk_fundinground`](#5-x_bst_startuptrk_fundinground).

Between them, the allowlist is what makes "the join table stays authoritative" and "the derivation is derived" enforceable rather than merely intended.

### A value that does not match its declared type is refused, never repaired

Each of the three non-string scalar kinds is parsed strictly, and a value that does not match is **refused**: it is logged, and the field is not written. Nothing is coerced into a plausible-looking substitute, because a repaired value is indistinguishable from a correct one once stored.

| Kind | Accepted exactly | Refused |
| --- | --- | --- |
| `currency` — `total_funding_usd`, `aum_usd`, `amount_usd`, `valuation_usd` | Optionally signed digits, at most 15 of them, with at most two decimal places | Anything else, including a thousands separator, a currency symbol, and a magnitude suffix such as `4.2M` or `900K` |
| `glide_date` — `round_date`, `posted_date`, `published_date` | `YYYY-MM-DD`; a full ISO 8601 timestamp, whose date part is taken; or an epoch value of exactly 10 digits (seconds) or 13 digits (milliseconds), which is what LinkedIn publishes for `listedAt`. The result must be a **real calendar day** | A date-like prefix inside longer text such as `2024-03-07 or thereabouts`, a digit run of any other length, and an impossible day such as `2023-02-30` or `2025-02-29` |
| `founded_year` | Four digits forming a year between 1900 and 2999 | A four-digit prefix of something longer, and a year outside the range |

The calendar check has exactly one implementation: `IngestionMapper.calendar()` resolves `RestQueryHelper` and calls its `isCalendarDate()`, so the Gregorian leap-year rule lives in one place and the ingestion path and the REST path can never disagree about whether a day exists. That single-home discipline is the same one applied to the inclusion criteria and the cleaning rules.

A refusal is not automatically a rejection. The field is dropped and the run continues; the record is rejected **only if the refused field was mandatory** — a funding round whose `round_date` will not parse has no usable identity and is rejected, while a startup whose `founded_year` will not parse is created without one. This is the same skip-the-record-and-continue-the-run semantics prompt section 8.0 requires.

### A value longer than its column is rejected, never truncated

Every allowlisted string value is measured against the `max_length` this document declares for its column **before** anything is written. An over-length value rejects the row, with a reason naming the field and the limit — `name exceeds 100 characters` — and the run continues. Nothing is shortened.

Truncating would be the more convenient behaviour and is the wrong one, for a specific reason rather than a general preference: several of these columns are **identity**. `Startup.name` at 100 characters and `headquarters_location` at 100 are the de-duplication key of cleaning rule 2, and a truncated name silently becomes a *different* startup — one that will not match the record a later run means to update, and that no child row's `startup_name` will resolve to. A rejected row is visible in the log and fixable at source; a truncated one is invisible and corrupts identity.

A natural key is measured against the column it **resolves against**, not against the reference column that stores the result. A `startup_name` of 140 characters is rejected with `startup exceeds 100 characters` — the 100 being what `Startup.name` declares — rather than being measured against the 32-character reference column that will hold the resolved identifier, which would be meaningless. The reason names the **target** field, `startup`, because that is the field the record carries by the time it is measured.

## Legacy provenance

This section records what the migration carried over from the legacy Flask and SQLAlchemy tree under `src/backend/models/`, and what it did not. The legacy tree is read-only reference: it supplied the entity-name spine, and no legacy field name, type, length, default or enumeration value was carried forward. It is the source side of the bidirectional traceability matrix at [`../../docs/decisions/TRACEABILITY_MATRIX.md`](../../docs/decisions/TRACEABILITY_MATRIX.md).

### Legacy model to target table

| Legacy source | Target table |
| --- | --- |
| `src/backend/models/startup.py` | `x_bst_startuptrk_startup` |
| `src/backend/models/founder.py` | `x_bst_startuptrk_founder` |
| `src/backend/models/executive.py` | `x_bst_startuptrk_executive` |
| `src/backend/models/investor.py` | `x_bst_startuptrk_investor` |
| `src/backend/models/funding_round.py` | `x_bst_startuptrk_fundinground` |
| `src/backend/models/job_posting.py` | `x_bst_startuptrk_jobposting` |
| `src/backend/models/news_article.py` | `x_bst_startuptrk_newsarticle` |
| The `funding_round_investors` association table at `src/backend/models/funding_round.py:L6-L9` | `x_bst_startuptrk_m2m_round_investor` |
| `src/backend/models/user.py` | **No target table** |

`src/backend/models/user.py` has no target table. The platform `sys_user` table plus the three scoped roles `x_bst_startuptrk.admin`, `x_bst_startuptrk.user` and `x_bst_startuptrk.premium_user` replace it, and `sys_user` sits outside the `x_bst_startuptrk` scope. The two supporting tables `x_bst_startuptrk_ingest_staging` and `x_bst_startuptrk_rate_limit_counter` have no legacy source construct at all.

### Startup columns the legacy model never had

`src/backend/models/startup.py:L9-L21` defines exactly these columns:

```text
id, name, website, industry, sub_sector, employee_count, local_employee_count,
headcount_growth_rate, total_funding, last_funding_date, funding_stage,
is_hiring, last_updated
```

That list contains **none** of the following seven target columns: `headquarters_location`, `active`, `institutional_funding_last_5yrs`, `description`, `logo_url`, `founded_year` and `employee_count_range`.

Two of those seven are the columns the inclusion criteria test — `headquarters_location` and `active` — so the inclusion criteria are new capability and not a port of anything the legacy schema could express.

### Legacy Startup columns with no target column

Seven legacy columns have no target column: `sub_sector`, `employee_count`, `local_employee_count`, `headcount_growth_rate`, `is_hiring`, `last_funding_date` and `last_updated`.

Prompt section 1.0's field list is binding and complete, so none of these becomes a column on `x_bst_startuptrk_startup`. Their exclusion is recorded in [`./gaps-and-flags.md`](./gaps-and-flags.md) and in [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md).

### Founder and Executive

`src/backend/models/founder.py:L8-L12` and `src/backend/models/executive.py:L8-L12` carry **identical** column sets: `id`, `startup_id`, `name`, `title` and `linkedin_url`. The target adds `bio` and `contact_email` to both tables, and `contact_email` is premium-gated on both.

### Investor

`src/backend/models/investor.py:L9-L12` carries only `id`, `name`, `type` and `website`. The target adds `focus_areas`, `aum_usd` and `portfolio_count`. `aum_usd` is premium-gated, and `portfolio_count` is calculated.

### FundingRound

`src/backend/models/funding_round.py:L15-L19` carries `id`, `startup_id`, `amount`, `date` and `round_type`. The target adds `lead_investor`, `valuation_usd` and `source_url`, and makes `round_date` mandatory where the legacy `date` column was nullable.

The association table at `src/backend/models/funding_round.py:L6-L9` carries only `funding_round_id` and `investor_id` — **no lead-versus-participating distinction**. The target introduces that distinction by keeping `lead_investor` as a first-class reference column on `x_bst_startuptrk_fundinground` while `x_bst_startuptrk_m2m_round_investor` carries participation.

### Type and length divergences

Each row below is a divergence from the legacy schema. Every one is recorded in [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md).

| Legacy declaration | Target declaration |
| --- | --- |
| `Startup.name` is `String(255)` | `x_bst_startuptrk_startup.name` is `string` with max length 100 |
| `JobPosting.title` is `String(255)` | `x_bst_startuptrk_jobposting.title` is `string` with max length 150 |
| `JobPosting.is_active` | `x_bst_startuptrk_jobposting.active` |
| `NewsArticle.url` is `String(512)` | `x_bst_startuptrk_newsarticle.url` is `string` with max length 255 |
| `NewsArticle.published_date` is `nullable=False` | `x_bst_startuptrk_newsarticle.published_date` is **not** mandatory |
| `Float` money columns, such as `Startup.total_funding` and `FundingRound.amount` | Platform `currency`: `total_funding_usd`, `aum_usd`, `amount_usd` and `valuation_usd` |
| `Date` and `DateTime` columns | `glide_date`: `round_date`, `posted_date` and `published_date`. The one exception is `x_bst_startuptrk_rate_limit_counter.window_start`, which is `glide_date_time` |
| `String(n)` columns | `string` with `max_length` n, at the lengths prompt section 1.0 declares |

### Enumerations are replaced, not translated

The legacy enumerations are **replaced, not translated**. `src/shared/constants.ts:L11-L44` declares eight funding stages with different labels, six investor types including `INCUBATOR`, and ten job departments. The target choice lists declare eight funding stages with the prompt section 1.0 labels, five investor types, and six job departments.

Consequently **no old-to-new mapping table exists**.

### One closed-choice rule for all eleven choice columns

Two steps run in sequence, and the order matters: a source vocabulary is translated **before** anything is judged unmatched.

**Step 1 — source-vocabulary translation.** A live payload states its values in the source system's own code vocabulary, not in target values. Crunchbase publishes `series_b`, `c_00051_c_00200`, `private_equity` and `Science and Engineering`; LinkedIn publishes `eng`, `HYBRID` and `MID_SENIOR_LEVEL`. `IngestionMapper` carries a translation table per source system and field, keyed on the lowercased source code, and applies it first. A code the table knows becomes its target value — `series_b` becomes `Series B`, `c_00051_c_00200` becomes `51-200`. A code the table does not know is passed through untouched, so it reaches step 2 and is judged there. A code the table knows to have **no** target member — `debt_financing`, `grant` and `initial_coin_offering` are funding types that correspond to no member of the eight-value stage list — resolves to nothing, and the event is logged as `recognised <source> code with no target member, left unwritten` so it reads distinctly from a genuinely unrecognised value.

Without this step every live value on a closed-choice column would fall to step 3 below, and the columns would populate with `Other` or with nothing at all across the board. The tables cover the documented upstream vocabularies; a source that adds a code later simply falls through to step 2 and is logged, which is the intended degradation.

**Step 2 — `IngestionMapper.normaliseChoice()`,** applied to every closed-choice column, in this order:

1. **Exact match** against the column's choice list. The value is stored as supplied.
2. **Case-insensitive match**. The value is stored with the choice list's own spelling, so `vp engineering` is stored as `VP Engineering`.
3. **No match.** The value is stored as `Other` **only where the column's choice list declares an `Other` member**. Where the list declares no `Other`, the field is **left unwritten**. Either way `IngestionLogger` records a `choice_unmatched` event naming the column, the supplied value and which of the two outcomes was applied.

"Left unwritten" is precise, and it is not the same as "emptied". The mapper removes the field from the record it is about to write rather than writing an empty value into it, so on an **insert** the column is simply empty, while on an **update** whatever the column already stores survives. An unmatched incoming value therefore never destroys a good stored value — which is the same no-clear rule that governs absent fields generally, described under [`../sample-data/README.md`](../sample-data/README.md). Clearing one of these columns is an administrative act through a REST update or the platform form, never an ingestion outcome.

**No value outside a column's choice list is ever stored.** None of the eleven columns is mandatory, so an unmatched value never rejects the record: rejection is reserved for a record missing a mandatory field.

Which columns take which outcome:

| Choice column | Declares `Other` | Outcome for an unmatched value |
| --- | --- | --- |
| `x_bst_startuptrk_startup.industry` | Yes | Stored as `Other`, logged |
| `x_bst_startuptrk_startup.funding_stage` | **No** | Left unwritten, logged |
| `x_bst_startuptrk_startup.employee_count_range` | **No** | Left unwritten, logged |
| `x_bst_startuptrk_founder.title` | Yes | Stored as `Other`, logged |
| `x_bst_startuptrk_executive.title` | Yes | Stored as `Other`, logged |
| `x_bst_startuptrk_investor.type` | **No** | Left unwritten, logged |
| `x_bst_startuptrk_investor.focus_areas` | Yes | Each unmatched token stored as `Other`, de-duplicated, logged |
| `x_bst_startuptrk_fundinground.round_type` | **No** | Left unwritten, logged |
| `x_bst_startuptrk_jobposting.department` | Yes | Stored as `Other`, logged |
| `x_bst_startuptrk_jobposting.remote_type` | **No** | Left unwritten, logged |
| `x_bst_startuptrk_jobposting.seniority` | **No** | Left unwritten, logged |

**Do not add an `Other` member to any of the six lists that lack one** — `startup.funding_stage`, `startup.employee_count_range`, `investor.type`, `fundinground.round_type`, `jobposting.remote_type` and `jobposting.seniority`. Prompt section 1.0's field and choice definitions are binding and complete, and the `sys_choice` inventory in the Update Set is exactly the 63 entity choice values those definitions declare.

`focus_areas` is the one multi-valued column. Its value is normalised token by token and the surviving tokens are de-duplicated, so two unmatched tokens on one investor yield a single `Other`.

**No value outside a declared choice list reaches an entity record through the ingestion path.** That guarantee is `IngestionMapper`'s, and it extends exactly as far as the mapper is called: both ingestion flows and the staging transform. It does **not** extend to the REST create and update operations, which call no mapper — see the create-and-update contract in [`./api-reference.md`](./api-reference.md) — nor to a direct write on the platform form. The fixtures that exercise each branch of this policy, and their measured outcomes, are inventoried in [`../sample-data/README.md`](../sample-data/README.md).

## Related documents

- [`../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml`](../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml) — the authoritative dictionary, choice and ACL records this document transcribes
- [`./access-control.md`](./access-control.md) — the three roles, the premium field ACL matrix, the five ACL layers and the twelve supporting-table controls layered above the access posture stated here
- [`./api-reference.md`](./api-reference.md) — the six REST resources, the nested sub-resource, the pagination envelope, the JSON-only media-type contract, the field validation applied to every stored value and the error bodies
- [`./validation-gates.md`](./validation-gates.md) — the machine-checkable post-commit gates, including the `sys_db_object` metadata check on each of the seven entity tables, the 53-column count and the two access-posture gates
- [`../sample-data/README.md`](../sample-data/README.md) — the authoritative CSV header rows and column contract for the fallback dataset, and the measured inventory of every unmatched choice value
- [`./validation-checklist.md`](./validation-checklist.md) — the five success criteria and the evidence each requires
- [`./gaps-and-flags.md`](./gaps-and-flags.md) — requirements with no clean platform equivalent, and the excluded legacy attributes
- [`./manual-build/06-staging-table-csv-import.md`](./manual-build/06-staging-table-csv-import.md) — the staging-table load and its transform map
- [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md) — the single source of truth for every decision, alternative and risk behind this model
- [`../../docs/decisions/TRACEABILITY_MATRIX.md`](../../docs/decisions/TRACEABILITY_MATRIX.md) — the bidirectional source-to-target matrix this section feeds
- [`../../docs/review/CRITICAL_DECISIONS.md`](../../docs/review/CRITICAL_DECISIONS.md) — the five highest-risk decisions, including entry 4, the Data/SME reviewer entry for this document
