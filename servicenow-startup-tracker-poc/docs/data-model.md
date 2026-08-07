# Data model — `x_bst_startuptrk`

This document is the field-by-field reference for the data model of the ServiceNow scoped application `x_bst_startuptrk`. It covers all ten physical tables the application declares: the seven entity tables of prompt section 1.0 and three supporting tables. For every column it states the platform type, the maximum length, the mandatory flag, the dictionary default, the choice values where a choice list is attached, and whether a field-level read ACL gates the column to premium callers. It also states the derivation of the one calculated field, the cascade behaviour of every reference column, and the startup inclusion criteria.

The Update Set XML at [`../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml`](../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml) is **authoritative** over this document. Everything below is a transcription of the `sys_db_object`, `sys_dictionary`, `sys_documentation` and `sys_choice` records that file carries. Where this document and those records disagree about a table name, a column name, a type, a length, a flag, a default or a choice value, the records are correct and this document is corrected to match them, never the reverse.

This document carries no rationale. Every decision behind the model, every alternative considered and every risk is recorded in [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md), which is the single source of truth for "why".

The identifiers established here — table names, column names, choice values, mandatory flags and premium markers — are reused verbatim by [`./access-control.md`](./access-control.md), [`./api-reference.md`](./api-reference.md), [`./validation-gates.md`](./validation-gates.md), [`./validation-checklist.md`](./validation-checklist.md) and [`./gaps-and-flags.md`](./gaps-and-flags.md).

**Reviewer.** This document is the artifact validated by the **Data/SME** reviewer entry in [`../../docs/review/CRITICAL_DECISIONS.md`](../../docs/review/CRITICAL_DECISIONS.md), covering the join-table authority, the cascade rules and the stored portfolio count.

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
| 9 | `x_bst_startuptrk_ingest_staging` | Ingestion staging | Supporting — staging table | 44 |
| 10 | `x_bst_startuptrk_rate_limit_counter` | Rate limit counter | Supporting — counter table | 4 |

Prompt section 1.0 states exactly seven custom tables; the application declares ten physical tables. Prompt section 10.0 criterion 1's table count is evaluated against the seven entity tables only, and the join table, the staging table and the rate-limit counter table are supporting artifacts counted separately. That reading is recorded in [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md).

None of the ten tables extends another table and none is extendable. Every table name carries the full `x_bst_startuptrk_` scope prefix. Three entity table names are single words with no separating underscore between the parts: `_fundinground`, `_jobposting` and `_newsarticle`. The three supporting table names are `_m2m_round_investor`, `_ingest_staging` and `_rate_limit_counter`.

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
| `funding_stage` | `string`, choice list | 40 | — | — | `Pre-Seed`, `Seed`, `Series A`, `Series B`, `Series C+`, `Growth`, `Public`, `Acquired` | — |
| `total_funding_usd` | `currency` | — | — | — | — | P |
| `active` | `boolean` | — | M | `true` | — | — |
| `institutional_funding_last_5yrs` | `boolean` | — | — | `false` | — | P |
| `employee_count_range` | `string`, choice list | 20 | — | — | `1-10`, `11-50`, `51-200`, `201-500`, `500+` | — |

`active` and `headquarters_location` are the two columns the startup inclusion criteria test. `institutional_funding_last_5yrs` is a premium-gated display attribute and is not part of that predicate. See [The startup inclusion criteria](#the-startup-inclusion-criteria).

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
| `type` | `string`, choice list | 30 | — | — | `VC`, `Angel`, `PE`, `Corporate`, `Accelerator` | — |
| `focus_areas` | `string`, multi-choice | 255 | — | — | `Fintech`, `Healthtech`, `SaaS`, `Consumer`, `Deeptech`, `Other` | — |
| `website` | `string` | 255 | — | — | — | — |
| `aum_usd` | `currency` | — | — | — | — | P |
| `portfolio_count` | `integer` | — | — | `0` | — | — |

`focus_areas` carries the same six values as `x_bst_startuptrk_startup.industry`, and more than one may be selected.

`portfolio_count` is a **calculated** value, declared Integer by prompt section 1.4. It is stored on the record and maintained by business rules. Its definition, its owning Script Include and its maintenance triggers are in [Investor.portfolio_count](#investorportfolio_count).

The `type` choice list has **no `Other` member**. See [Enumerations are replaced, not translated](#enumerations-are-replaced-not-translated).

### 5. `x_bst_startuptrk_fundinground`

Label **Funding round**. Eight columns. The table declares no display column; a funding round is identified in the interface by its `startup` and `round_date`.

| Column | Platform type | Max length | Mandatory | Default | Choice values | Premium |
| --- | --- | --- | --- | --- | --- | --- |
| `startup` | `reference` to `x_bst_startuptrk_startup` | 32 | M | — | — | — |
| `round_type` | `string`, choice list | 40 | — | — | `Pre-Seed`, `Seed`, `Series A`, `Series B`, `Series C+`, `Growth`, `Public`, `Acquired` | — |
| `amount_usd` | `currency` | — | — | — | — | P |
| `round_date` | `glide_date` | — | M | — | — | — |
| `lead_investor` | `reference` to `x_bst_startuptrk_investor` | 32 | — | — | — | — |
| `participating_investors` | `string`, read-only, virtual, calculated | 1000 | — | — | — | — |
| `valuation_usd` | `currency` | — | — | — | — | P |
| `source_url` | `string` | 255 | — | — | — | — |

`round_type` carries the same eight values as `x_bst_startuptrk_startup.funding_stage`.

`lead_investor` is a first-class reference and carries the lead-versus-participating distinction. `participating_investors` is read-only and virtual: its value is computed at read time from the join table `x_bst_startuptrk_m2m_round_investor`, which reads that table through `GlideRecordSecure` and returns the linked investors' display values joined by a comma and a space. The join table is authoritative for participating investors; see [8. `x_bst_startuptrk_m2m_round_investor`](#8-x_bst_startuptrk_m2m_round_investor).

### 6. `x_bst_startuptrk_jobposting`

Label **Job posting**. Nine columns. The display column is `title`.

| Column | Platform type | Max length | Mandatory | Default | Choice values | Premium |
| --- | --- | --- | --- | --- | --- | --- |
| `startup` | `reference` to `x_bst_startuptrk_startup` | 32 | M | — | — | — |
| `title` | `string` | 150 | M | — | — | — |
| `department` | `string`, choice list | 40 | — | — | `Engineering`, `Sales`, `Marketing`, `Product`, `Operations`, `Other` | — |
| `location` | `string` | 100 | — | — | — | — |
| `remote_type` | `string`, choice list | 20 | — | — | `Onsite`, `Hybrid`, `Remote` | — |
| `seniority` | `string`, choice list | 20 | — | — | `Entry`, `Mid`, `Senior`, `Lead`, `Executive` | — |
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

This roll-up is the field-count evidence that prompt section 10.0 criterion 1 depends on. The criterion's verification steps are in [`./validation-checklist.md`](./validation-checklist.md), and the machine-checkable table reads are in [`./validation-gates.md`](./validation-gates.md).

## Supporting tables

The three tables in this section are **not** entity tables and are not counted towards prompt section 10.0 criterion 1. Each exists to support the entity model: one join table materialises a many-to-many relationship, one staging table holds the fallback ingestion dataset, and one counter table holds per-caller rate-limit accounting. Fifty columns in total: 2, 44 and 4.

### 8. `x_bst_startuptrk_m2m_round_investor`

Label **Round investor**. Two columns. The table declares no display column. It is named verbatim by prompt section 1.5.

| Column | Platform type | Max length | Mandatory | Default | Choice values | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `funding_round` | `reference` to `x_bst_startuptrk_fundinground` | 32 | M | — | — | Cascade delete |
| `investor` | `reference` to `x_bst_startuptrk_investor` | 32 | M | — | — | Cascade delete |

This table is **authoritative** for the participating investors of a funding round. One row links one funding round to one participating investor. Three surfaces read it:

- The funding round form surfaces it as a **related list**, so an administrator adds and removes participating investors there.
- `x_bst_startuptrk_fundinground.participating_investors` is materialised from it at read time and is read-only.
- The REST layer emits `participating_investors` as a **JSON array** of investor references assembled from it. The response shape is in [`./api-reference.md`](./api-reference.md).

The lead-versus-participating distinction is carried by `x_bst_startuptrk_fundinground.lead_investor`, a first-class reference column on the funding round and not a row in this table. The same investor may be both the lead investor of a round and a participating investor in it. The decision behind this table's authority is recorded in [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md).

Rows in this table drive the second maintenance trigger for `x_bst_startuptrk_investor.portfolio_count`; see [Investor.portfolio_count](#investorportfolio_count).

### 9. `x_bst_startuptrk_ingest_staging`

Label **Ingestion staging**. Forty-four columns. The display column is `import_run`. This is the single staging table required by prompt section 4.0, and it is the home of the fallback dataset both ingestion flows read when a live call fails, times out, returns a malformed response, or when the property `x_bst_startuptrk.ingestion.source_mode` is set to `fallback`.

One flat table serves all six ingested record types. `record_type` is the discriminator that tells the transform which entity table a row becomes and which flattened columns it reads. No staging column is mandatory, so a row with a blank value loads successfully; the mandatory requirement is enforced per record type at transform time by cleaning rule 4, which rejects the row and creates no entity record.

Forty-four columns is seven control columns plus thirty-seven flattened scalar columns: 7 + 37 = 44.

#### Control columns

Seven columns, present on every row whatever its record type.

| Column | Platform type | Max length | Mandatory | Default | Choice values | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `source_system` | `string`, choice list | 40 | — | — | `crunchbase`, `linkedin` | Which ingestion flow's dataset the row belongs to |
| `record_type` | `string`, choice list | 40 | — | — | `startup`, `founder`, `executive`, `investor`, `funding_round`, `job_posting` | Discriminator for the transform |
| `raw_payload` | `string` | 8000 | — | — | — | The source response payload in the shape the source API returns, per prompt section 4.0 |
| `import_state` | `string`, choice list | 40 | — | `pending` | `pending`, `processed`, `rejected`, `error` | Processing state of the staged row |
| `error_message` | `string` | 1000 | — | — | — | Rejection or error detail written by `IngestionMapper` |
| `run_provenance` | `string`, choice list | 40 | — | — | `live`, `fallback` | Whether the row was consumed by a live or a fallback run |
| `import_run` | `string` | 64 | — | — | — | Run identifier shared by every row of one load |

#### Flattened scalar columns, by record type

Thirty-seven columns. They mirror the prompt section 1.0 column names of the entity table each record type becomes, with references expressed as the natural keys `startup_name`, `lead_investor_name` and `participating_investor_names`. A CSV cannot carry a `sys_id` for a record that does not exist yet, so every reference travels as the target record's `name` value and the transform resolves it at load time. Where a staging column name would collide across record types it is disambiguated by an entity prefix: `startup_`, `person_`, `investor_` and `job_`.

None of these thirty-seven columns carries a choice list. Choice normalisation happens at transform time under cleaning rule 3, so an unmatched incoming value loads into staging unchanged. The four money columns are `decimal` here and `currency` on the entity tables.

`startup_name` is declared once, in the `startup` group below, and is read by five record types: it is the Startup's own name on a `startup` row and the natural key to the parent Startup on a `founder`, `executive`, `funding_round` or `job_posting` row.

Record type `startup` — twelve columns.

| Column | Platform type | Max length | Default | Target field |
| --- | --- | --- | --- | --- |
| `startup_name` | `string` | 100 | — | `x_bst_startuptrk_startup.name` |
| `description` | `string` | 4000 | — | `x_bst_startuptrk_startup.description` |
| `industry` | `string` | 40 | — | `x_bst_startuptrk_startup.industry` |
| `founded_year` | `integer` | — | — | `x_bst_startuptrk_startup.founded_year` |
| `headquarters_location` | `string` | 100 | — | `x_bst_startuptrk_startup.headquarters_location` |
| `startup_website` | `string` | 255 | — | `x_bst_startuptrk_startup.website` |
| `logo_url` | `string` | 255 | — | `x_bst_startuptrk_startup.logo_url` |
| `funding_stage` | `string` | 40 | — | `x_bst_startuptrk_startup.funding_stage` |
| `total_funding_usd` | `decimal` | — | — | `x_bst_startuptrk_startup.total_funding_usd` |
| `startup_active` | `boolean` | — | `true` | `x_bst_startuptrk_startup.active` |
| `institutional_funding_last_5yrs` | `boolean` | — | `false` | `x_bst_startuptrk_startup.institutional_funding_last_5yrs` |
| `employee_count_range` | `string` | 20 | — | `x_bst_startuptrk_startup.employee_count_range` |

Record types `founder` and `executive` — five columns, shared by both, plus `startup_name` as the natural key to the parent Startup. The target table is `x_bst_startuptrk_founder` on a `founder` row and `x_bst_startuptrk_executive` on an `executive` row.

| Column | Platform type | Max length | Default | Target field |
| --- | --- | --- | --- | --- |
| `person_name` | `string` | 100 | — | `name` on Founder or Executive |
| `person_title` | `string` | 40 | — | `title` on Founder or Executive |
| `bio` | `string` | 2000 | — | `bio` on Founder or Executive |
| `linkedin_url` | `string` | 255 | — | `linkedin_url` on Founder or Executive |
| `contact_email` | `string` | 100 | — | `contact_email` on Founder or Executive |

Record type `investor` — five columns.

| Column | Platform type | Max length | Default | Target field |
| --- | --- | --- | --- | --- |
| `investor_name` | `string` | 100 | — | `x_bst_startuptrk_investor.name` |
| `investor_type` | `string` | 30 | — | `x_bst_startuptrk_investor.type` |
| `focus_areas` | `string` | 255 | — | `x_bst_startuptrk_investor.focus_areas` |
| `investor_website` | `string` | 255 | — | `x_bst_startuptrk_investor.website` |
| `aum_usd` | `decimal` | — | — | `x_bst_startuptrk_investor.aum_usd` |

`x_bst_startuptrk_investor.portfolio_count` has no staging column. It is calculated, not staged.

Record type `funding_round` — seven columns, plus `startup_name` as the natural key to the parent Startup.

| Column | Platform type | Max length | Default | Target field |
| --- | --- | --- | --- | --- |
| `round_type` | `string` | 40 | — | `x_bst_startuptrk_fundinground.round_type` |
| `amount_usd` | `decimal` | — | — | `x_bst_startuptrk_fundinground.amount_usd` |
| `round_date` | `glide_date` | — | — | `x_bst_startuptrk_fundinground.round_date` |
| `lead_investor_name` | `string` | 100 | — | `x_bst_startuptrk_fundinground.lead_investor`, resolved from the Investor `name` |
| `participating_investor_names` | `string` | 1000 | — | One `x_bst_startuptrk_m2m_round_investor` row per comma-separated Investor `name` |
| `valuation_usd` | `decimal` | — | — | `x_bst_startuptrk_fundinground.valuation_usd` |
| `source_url` | `string` | 255 | — | `x_bst_startuptrk_fundinground.source_url` |

Record type `job_posting` — eight columns, plus `startup_name` as the natural key to the parent Startup.

| Column | Platform type | Max length | Default | Target field |
| --- | --- | --- | --- | --- |
| `job_title` | `string` | 150 | — | `x_bst_startuptrk_jobposting.title` |
| `department` | `string` | 40 | — | `x_bst_startuptrk_jobposting.department` |
| `job_location` | `string` | 100 | — | `x_bst_startuptrk_jobposting.location` |
| `remote_type` | `string` | 20 | — | `x_bst_startuptrk_jobposting.remote_type` |
| `seniority` | `string` | 20 | — | `x_bst_startuptrk_jobposting.seniority` |
| `posted_date` | `glide_date` | — | — | `x_bst_startuptrk_jobposting.posted_date` |
| `job_url` | `string` | 255 | — | `x_bst_startuptrk_jobposting.url` |
| `job_active` | `boolean` | — | `true` | `x_bst_startuptrk_jobposting.active` |

12 + 5 + 5 + 7 + 8 = 37 flattened columns, and 7 + 37 = 44.

#### The three-way staging contract

The column names above bind three artifacts, and all three must change together.

| Leg | Artifact | Role |
| --- | --- | --- |
| a | The header rows of the six CSVs under `../sample-data/`, documented in [`../sample-data/README.md`](../sample-data/README.md) | The wire format |
| b | The `x_bst_startuptrk_ingest_staging` dictionary records in [`../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml`](../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml) | **Authoritative** |
| c | The field mapping in [`./manual-build/06-staging-table-csv-import.md`](./manual-build/06-staging-table-csv-import.md) | The load instructions |

A change to any one leg alone breaks the fallback path **silently**: the Data Import Wizard maps columns by header name, so a renamed or misspelled column is left unmapped, the field loads empty, and no error is raised.

[`../sample-data/README.md`](../sample-data/README.md) is the authoritative statement of the CSV header rows, including their order within each file, and it is not restated here.

### 10. `x_bst_startuptrk_rate_limit_counter`

Label **Rate limit counter**. Four columns. The display column is `api_resource`.

| Column | Platform type | Max length | Mandatory | Default | Choice values | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `caller` | `reference` to `sys_user` | 32 | — | — | — | The authenticated caller the window belongs to |
| `window_start` | `glide_date_time` | — | — | — | — | Start of the fixed window |
| `request_count` | `integer` | — | — | `0` | — | Requests counted in the window |
| `api_resource` | `string` | 100 | — | — | — | The logical REST resource the window applies to |

This table backs the fixed-window, per-caller request accounting behind the rate-limit response documented in [`./api-reference.md`](./api-reference.md). `RateLimitService` finds or creates the current window row for a caller and resource, increments `request_count`, and compares the count against the configured budget. Two shipped system properties govern the accounting: `x_bst_startuptrk.rest.rate_limit_requests` is `100` and `x_bst_startuptrk.rest.rate_limit_window_seconds` is `60`. The response body and status the service returns when the budget is exhausted are specified in [`./api-reference.md`](./api-reference.md) and are not restated here.

The scheduled job **Prune rate limit counters** runs hourly and deletes rows whose window has closed, so the table does not grow without bound.

`caller` references `sys_user`, which sits outside the `x_bst_startuptrk` scope. The reference is read-only in effect: the application creates counter rows and never creates, updates or deletes a `sys_user` record. This table and the staging table are readable and writable by the `x_bst_startuptrk.admin` role only; see [`./access-control.md`](./access-control.md).

## Derivations

### Investor.portfolio_count

`x_bst_startuptrk_investor.portfolio_count` is the count of **distinct** startups reachable from an investor by **either** of two paths:

- **a.** a funding round whose `lead_investor` is that investor, reached as `x_bst_startuptrk_fundinground.lead_investor`; or
- **b.** a row of `x_bst_startuptrk_m2m_round_investor` whose `investor` is that investor, giving a funding round the investor participated in.

Each path yields a set of `x_bst_startuptrk_startup` identifiers, taken from the `startup` reference of the funding rounds it reaches. The two sets are **unioned before counting**, and the count is the size of the union. An investor that led one round of a company and participated in another round of the **same** company therefore counts that company **once**. An investor with no rounds on either path has a `portfolio_count` of `0`, which is also the dictionary default.

The `InvestorPortfolioService` Script Include owns the derivation. Its methods are `countPortfolio(investorId)`, which returns the derived count for one investor; `recalculate(investorId)`, which derives the count and writes it to the record; `recalculateMany(investorIds)`, which recalculates a set of investors; and `recalculateAll()`, which recalculates every investor and is the method to invoke after a bulk load.

Two business rules maintain the stored value. Both delegate to `InvestorPortfolioService`, and each recalculates only the investors its trigger affects.

| Business rule | Table | When | Operations | What it recalculates |
| --- | --- | --- | --- | --- |
| Recalculate investor portfolio on funding round | `x_bst_startuptrk_fundinground` | After | Insert, update, delete | The round's `lead_investor`. On an update it recalculates **both** the previous and the new `lead_investor`, and it handles a change to the round's `startup` reference. On a delete it recalculates the lead investor of the deleted round and every investor linked to it through the join table. |
| Recalculate investor portfolio on round investor link | `x_bst_startuptrk_m2m_round_investor` | After | Insert, delete | The `investor` named on the affected row. |

Two operational instructions follow. Both are requirements.

- Any ingestion or import path that writes `x_bst_startuptrk_fundinground` or `x_bst_startuptrk_m2m_round_investor` **must run business rules**, otherwise the stored count is not maintained for the records it writes.
- `InvestorPortfolioService.recalculateAll()` **must be invoked from a background script after any bulk load**, including every load of the fallback dataset described in [`./manual-build/06-staging-table-csv-import.md`](./manual-build/06-staging-table-csv-import.md).

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

### Dot-walking, not joins

Related data is reached by **dot-walking a reference column**, never by an application-side join. `x_bst_startuptrk_fundinground.startup.name` is the startup name of a funding round; `x_bst_startuptrk_m2m_round_investor.funding_round.startup.name` is the startup name behind a participation row. Dot-walked reads are subject to the same access control as direct reads, so a dot-walk cannot be used to reach a premium-gated column that the caller's roles do not grant.

Physical table names are always fully scope-prefixed. A query, a reference qualifier, a REST operation, a widget server script or an ATF step names `x_bst_startuptrk_startup`, never the bare entity name `startup`. Script Includes are addressed as `x_bst_startuptrk.<ClassName>` from outside the scope and by bare class name within it.

## The startup inclusion criteria

A startup is eligible for Service Portal search results only if:

> `active` = true **AND** `headquarters_location` contains **"Boston"** OR **"Cambridge, MA"** (case-insensitive substring).

Records failing these criteria **remain in the table for administrative visibility** and are excluded from all portal-facing and non-administrative list and search queries.

The filter tests **only** two columns: `x_bst_startuptrk_startup.active` and `x_bst_startuptrk_startup.headquarters_location`. `x_bst_startuptrk_startup.institutional_funding_last_5yrs` is a premium-gated display attribute and is **not** part of the predicate. The resolution of that point is recorded in [`./gaps-and-flags.md`](./gaps-and-flags.md).

`StartupSearchService` is the single Script Include that builds the query. Both callers use it, so the filter cannot drift between the two surfaces: the `/startups` REST list operation documented in [`./api-reference.md`](./api-reference.md), and the portal search widget on the Home/Search route.

The two location tokens are read from the system property `x_bst_startuptrk.inclusion.location_tokens`, whose shipped value is `Boston,Cambridge, MA`. Changing the property changes the tokens the predicate tests, with no code change.

In encoded-query form the criteria are built as three clauses joined by `^`:

```text
active=true^headquarters_locationLIKEBoston^ORheadquarters_locationLIKECambridge, MA
```

The `^OR` operator binds to the **immediately preceding condition**, so the second location clause is an or-condition on the first location clause and not on the whole query. That binding is what produces the required and-of-or grouping: `active` true, and either location token matching. `LIKE` is a case-insensitive contains comparison.

One operational requirement applies to every caller of the filter: **the criteria are a query filter, not an ACL.** The platform does not apply them, so they must be applied identically to the result set **and** to the `total_count` returned with a paginated response. Applying them to one and not the other makes the count disagree with the page contents. Record-level read access to all seven entity tables is granted to all three roles, and the role difference is at field level only; see [`./access-control.md`](./access-control.md).

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

Consequently **no old-to-new mapping table exists**. Cleaning rule 3 normalises an incoming value by exact match, then by case-insensitive match; a value matching nothing is stored as `Other` and logged by `IngestionLogger` as an unmatched value.

One asymmetry matters operationally. The `x_bst_startuptrk_investor.type` choice list is `VC`, `Angel`, `PE`, `Corporate`, `Accelerator` and has **no `Other` member**, so an unmatched investor type has no value to normalise to. An unmatched investor type is rejected and logged, not coerced. No `Other` choice may be added to that list: prompt section 1.0's field and choice definitions are binding and complete.

## Related documents

- [`../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml`](../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml) — the authoritative dictionary, choice and ACL records this document transcribes
- [`./access-control.md`](./access-control.md) — the three roles and the premium field ACL matrix
- [`./api-reference.md`](./api-reference.md) — the six REST resources, the nested sub-resource, the pagination envelope and the error bodies
- [`./validation-gates.md`](./validation-gates.md) — the machine-checkable post-commit gates, including a read on each of the seven entity tables
- [`./validation-checklist.md`](./validation-checklist.md) — the five success criteria and the evidence each requires
- [`./gaps-and-flags.md`](./gaps-and-flags.md) — requirements with no clean platform equivalent, and the excluded legacy attributes
- [`./manual-build/06-staging-table-csv-import.md`](./manual-build/06-staging-table-csv-import.md) — the staging-table load and its transform map
- [`../sample-data/README.md`](../sample-data/README.md) — the authoritative CSV header rows and column contract for the fallback dataset
- [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md) — the single source of truth for every decision, alternative and risk behind this model
- [`../../docs/decisions/TRACEABILITY_MATRIX.md`](../../docs/decisions/TRACEABILITY_MATRIX.md) — the bidirectional source-to-target matrix this section feeds
- [`../../docs/review/CRITICAL_DECISIONS.md`](../../docs/review/CRITICAL_DECISIONS.md) — the five highest-risk decisions, including the Data/SME reviewer entry for this document
