# Sample Data — Fallback Dataset

This folder holds the fallback dataset required by prompt section 4.0. Its six CSV files load into the single staging table `x_bst_startuptrk_ingest_staging` in the scoped application `x_bst_startuptrk`, and they stand in for a live Crunchbase or LinkedIn API response when live authentication fails, times out, returns a malformed response, or while credentials are being re-issued.

The dataset is **fallback only**. Every ingestion run attempts the live call first; the staging table is read only when that attempt fails, or when the property `x_bst_startuptrk.ingestion.source_mode` is set to `fallback` to make a test deterministic. The live credentials themselves are held in the two Connection and Credential Aliases `x_bst_startuptrk.crunchbase_api` (Basic Auth) and `x_bst_startuptrk.linkedin_oauth` (OAuth2), which are referenced by name and built by hand per [`../docs/manual-build/01-connection-credential-aliases.md`](../docs/manual-build/01-connection-credential-aliases.md). No credential material appears in this folder. The two non-secret API base URLs are the properties `x_bst_startuptrk.crunchbase.base_url` and `x_bst_startuptrk.linkedin.base_url`.

This document is the column contract for the six CSVs: what each column is, which requirement it serves, and how to load the data. It carries no rationale. Every decision behind the contract, every alternative considered and every risk is recorded in [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md).

## Contents

Seven files, this document included.

| File | Purpose |
| --- | --- |
| `README.md` | This document: the CSV column contract, value conventions and load procedure. |
| `crunchbase_startups_sample.csv` | Staged Startup records for the Crunchbase ingestion flow's fallback path. |
| `crunchbase_investors_sample.csv` | Staged Investor records for the Crunchbase ingestion flow's fallback path. |
| `crunchbase_funding_rounds_sample.csv` | Staged FundingRound records, including the participating-investor links, for the Crunchbase ingestion flow's fallback path. |
| `linkedin_founders_sample.csv` | Staged Founder records for the LinkedIn ingestion flow's fallback path. |
| `linkedin_executives_sample.csv` | Staged Executive records for the LinkedIn ingestion flow's fallback path. |
| `linkedin_job_postings_sample.csv` | Staged JobPosting records for the LinkedIn ingestion flow's fallback path. |

The six CSVs cover exactly the six ingested record types. The Crunchbase flow supplies Startup, Investor and FundingRound; the LinkedIn flow supplies Founder, Executive and JobPosting.

There is deliberately **no NewsArticle CSV**. Prompt sections 1.7 and 4.0 exclude NewsArticle from automated ingestion, so no flow serves it and it has no fallback dataset; NewsArticle records are created by manual entry or by a separate ad hoc import. The exclusion is recorded in [`../docs/gaps-and-flags.md`](../docs/gaps-and-flags.md) and [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md).

## CSV dialect

The repository has no pre-existing CSV convention, so the dialect is specified here in full. All six files conform to it.

- **Format** — RFC 4180.
- **Field delimiter** — a comma (`,`).
- **Quoting character** — the double quote (`"`).
- **Escaping** — a literal double quote inside a quoted field is escaped by doubling it (`""`).
- **When to quote** — fields are quoted only where they contain a comma, a double quote or a line break. Every other field is unquoted.
- **Encoding** — UTF-8 **without** a byte-order mark.
- **Line endings** — LF (`\n`). Not CRLF.
- **Header** — exactly one header row, the first line of the file.
- **File ending** — a single terminating newline after the last data row, and no trailing blank line beyond it.
- **Comments** — none. No line in any file is a comment, and no comment syntax is recognised.

Two consequences follow and both are load-critical:

1. The header row is authoritative for column order **within a file**. Column order may differ between files; it never differs from the header row of the file it belongs to.
2. The ServiceNow Data Import Wizard maps columns **by header name**. Header spelling must therefore match the `x_bst_startuptrk_ingest_staging` dictionary element names exactly, case included. A misspelled header does not raise an error; it produces an unmapped column and a silently empty field.

## Control columns

Every row of every one of the six CSVs is one row of `x_bst_startuptrk_ingest_staging`, so all six files open with a byte-identical seven-column control prefix in this exact order. The flattened columns for that file's record type follow it.

```text
source_system,record_type,import_run,import_state,run_provenance,error_message,raw_payload
```

| Column | Type and length | Values | What it is for |
| --- | --- | --- | --- |
| `source_system` | String, 40, choice list | `crunchbase` or `linkedin` | Identifies which ingestion flow's fallback path the row belongs to. Constant for every row of a file. |
| `record_type` | String, 40, choice list | `startup`, `founder`, `executive`, `investor`, `funding_round`, `job_posting` | The discriminator that tells the transform which entity table the row becomes, and which flattened columns it reads. Constant for every row of a file. |
| `import_run` | String, 64 | See the per-file values below | A stable synthetic identifier shared by every row of a single file, so one load is traceable end to end. |
| `import_state` | String, 40, choice list, dictionary default `pending` | `pending`, `processed`, `rejected`, `error` | Processing state of the staged row. Every shipped row carries `pending`; the transform advances it. |
| `run_provenance` | String, 40, choice list | `live` or `fallback` | Whether the row was consumed by a live or a fallback run. Every shipped row carries `fallback`. |
| `error_message` | String, 1000 | Empty on every shipped row | Rejection or error detail written by `IngestionMapper` when a row is rejected or errors. |
| `raw_payload` | String, 8000 | A JSON object | The source response payload for that record, in the shape the source API returns, per prompt section 4.0's requirement that the staging shape mimic the expected API response. |

`record_type` distinguishing `founder` from `executive` is what keeps Founder and Executive as separate record types through the staging layer, consistent with prompt section 1.3's directive that they remain separate tables rather than one person table with a role flag.

The `import_run` value for each file:

| File | `import_run` |
| --- | --- |
| `crunchbase_startups_sample.csv` | `fallback-sample-crunchbase-startups` |
| `crunchbase_investors_sample.csv` | `fallback-sample-crunchbase-investors` |
| `crunchbase_funding_rounds_sample.csv` | `fallback-sample-crunchbase-funding-rounds` |
| `linkedin_founders_sample.csv` | `fallback-sample-linkedin-founders` |
| `linkedin_executives_sample.csv` | `fallback-sample-linkedin-executives` |
| `linkedin_job_postings_sample.csv` | `fallback-sample-linkedin-job-postings` |

## Column contract per record type

`x_bst_startuptrk_ingest_staging` is one flat table serving all six record types, so its flattened columns are disambiguated by entity: `startup_name`, `startup_website` and `startup_active` carry Startup values, `person_name` and `person_title` carry Founder or Executive values, `investor_name`, `investor_type` and `investor_website` carry Investor values, and `job_title`, `job_location`, `job_url` and `job_active` carry JobPosting values. The column names below are the dictionary element names exactly as the Update Set declares them, and the target field named in each table is the prompt section 1.0 field the transform writes.

### The `_name` natural-key convention

A CSV cannot carry a `sys_id` for a record that does not exist yet, so every reference travels as the target record's `name` value and the transform resolves it at load time. Three columns are natural keys: `startup_name` resolves to a `x_bst_startuptrk_startup` record, and `lead_investor_name` and `participating_investor_names` resolve to `x_bst_startuptrk_investor` records. The resolution steps are in [`../docs/manual-build/06-staging-table-csv-import.md`](../docs/manual-build/06-staging-table-csv-import.md).

`startup_name` serves two purposes according to `record_type`. On a `startup` row it is the Startup's own name. On a `founder`, `executive`, `funding_round` or `job_posting` row it is the natural key that resolves to the parent Startup. `investor_name` likewise carries the Investor's own name on an `investor` row.

### Mandatory columns

The staging dictionary marks no column mandatory, so a row with a blank mandatory value loads into staging successfully. The requirement is enforced at transform time, per record type, by cleaning rule 4: a row missing any of its mandatory values is rejected instead of producing a partial entity record. The **Mandatory** column in each table below is that transform-time requirement.

### `crunchbase_startups_sample.csv`

`source_system` is `crunchbase` and `record_type` is `startup` on every row. Nineteen columns.

```text
source_system,record_type,import_run,import_state,run_provenance,error_message,raw_payload,startup_name,description,industry,founded_year,headquarters_location,startup_website,logo_url,funding_stage,total_funding_usd,startup_active,institutional_funding_last_5yrs,employee_count_range
```

| Column | Platform type | Mandatory | Choice values or format |
| --- | --- | --- | --- |
| `startup_name` | String, 100 | Yes | Free text. Writes `Startup.name`. |
| `description` | String, 4000 | No | Free text. Writes `Startup.description`. |
| `industry` | String, 40 on staging; Choice on `Startup.industry` | No | `Fintech`, `Healthtech`, `SaaS`, `Consumer`, `Deeptech`, `Other` |
| `founded_year` | Integer | No | A four-digit year, for example `2019`. |
| `headquarters_location` | String, 100 | Yes | Free text. Writes `Startup.headquarters_location`, and is the second half of the deduplication key. |
| `startup_website` | String, 255 | No | Absolute URL. Writes `Startup.website`. |
| `logo_url` | String, 255 | No | Absolute URL. Writes `Startup.logo_url`. |
| `funding_stage` | String, 40 on staging; Choice on `Startup.funding_stage` | No | `Pre-Seed`, `Seed`, `Series A`, `Series B`, `Series C+`, `Growth`, `Public`, `Acquired` |
| `total_funding_usd` | Decimal on staging; Currency on `Startup.total_funding_usd` | No | Plain USD amount. Premium-gated. |
| `startup_active` | True/False, dictionary default `true` | No | `true` or `false`. Writes `Startup.active`. |
| `institutional_funding_last_5yrs` | True/False, dictionary default `false` | No | `true` or `false`. Premium-gated. |
| `employee_count_range` | String, 20 on staging; Choice on `Startup.employee_count_range` | No | `1-10`, `11-50`, `51-200`, `201-500`, `500+` |

### `crunchbase_investors_sample.csv`

`source_system` is `crunchbase` and `record_type` is `investor` on every row. Twelve columns.

```text
source_system,record_type,import_run,import_state,run_provenance,error_message,raw_payload,investor_name,investor_type,focus_areas,investor_website,aum_usd
```

| Column | Platform type | Mandatory | Choice values or format |
| --- | --- | --- | --- |
| `investor_name` | String, 100 | Yes | Free text. Writes `Investor.name`. |
| `investor_type` | String, 30 on staging; Choice on `Investor.type` | No | `VC`, `Angel`, `PE`, `Corporate`, `Accelerator` |
| `focus_areas` | String, 255 on staging; Multi-choice on `Investor.focus_areas` | No | One or more of `Fintech`, `Healthtech`, `SaaS`, `Consumer`, `Deeptech`, `Other`, comma separated. |
| `investor_website` | String, 255 | No | Absolute URL. Writes `Investor.website`. |
| `aum_usd` | Decimal on staging; Currency on `Investor.aum_usd` | No | Plain USD amount. Premium-gated. |

`portfolio_count` is deliberately **absent** from this file and from the staging dictionary. Prompt section 1.4 declares `Investor.portfolio_count` calculated, and it is derived by the `InvestorPortfolioService` Script Include and maintained by the two portfolio business rules on `x_bst_startuptrk_fundinground` and `x_bst_startuptrk_m2m_round_investor`. Its derivation is described in [`../docs/data-model.md`](../docs/data-model.md) and the decision is recorded in [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md).

### `crunchbase_funding_rounds_sample.csv`

`source_system` is `crunchbase` and `record_type` is `funding_round` on every row. Fifteen columns.

```text
source_system,record_type,import_run,import_state,run_provenance,error_message,raw_payload,startup_name,round_type,amount_usd,round_date,lead_investor_name,participating_investor_names,valuation_usd,source_url
```

| Column | Platform type | Mandatory | Choice values or format |
| --- | --- | --- | --- |
| `startup_name` | String, 100; natural key to `x_bst_startuptrk_startup` | Yes | An existing Startup `name`. Writes the `FundingRound.startup` reference. |
| `round_type` | String, 40 on staging; Choice on `FundingRound.round_type` | No | `Pre-Seed`, `Seed`, `Series A`, `Series B`, `Series C+`, `Growth`, `Public`, `Acquired` |
| `amount_usd` | Decimal on staging; Currency on `FundingRound.amount_usd` | No | Plain USD amount. Premium-gated. |
| `round_date` | Date (`glide_date`) | Yes | `YYYY-MM-DD`. |
| `lead_investor_name` | String, 100; natural key to `x_bst_startuptrk_investor` | No | An existing Investor `name`. Writes the `FundingRound.lead_investor` reference. |
| `participating_investor_names` | String, 1000; multi-valued natural keys to `x_bst_startuptrk_investor` | No | Comma-separated existing Investor `name` values. |
| `valuation_usd` | Decimal on staging; Currency on `FundingRound.valuation_usd` | No | Plain USD amount. Premium-gated. |
| `source_url` | String, 255 | No | Absolute URL. Writes `FundingRound.source_url`. |

`lead_investor_name` and `participating_investor_names` are distinct columns with distinct destinations. The lead investor is a first-class reference field on the funding round. Each participating investor becomes one row in the join table `x_bst_startuptrk_m2m_round_investor`, and the read-only `FundingRound.participating_investors` field is materialised from that join table. An investor may appear in both columns on the same row.

### `linkedin_founders_sample.csv`

`source_system` is `linkedin` and `record_type` is `founder` on every row. Thirteen columns.

```text
source_system,record_type,import_run,import_state,run_provenance,error_message,raw_payload,person_name,startup_name,person_title,bio,linkedin_url,contact_email
```

| Column | Platform type | Mandatory | Choice values or format |
| --- | --- | --- | --- |
| `person_name` | String, 100 | Yes | Free text. Writes `Founder.name`. |
| `startup_name` | String, 100; natural key to `x_bst_startuptrk_startup` | Yes | An existing Startup `name`. Writes the `Founder.startup` reference. |
| `person_title` | String, 40 on staging; Choice on `Founder.title` | No | `CEO`, `CTO`, `COO`, `Co-Founder`, `Other` |
| `bio` | String, 2000 | No | Free text. Writes `Founder.bio`. |
| `linkedin_url` | String, 255 | No | Absolute URL. Writes `Founder.linkedin_url`. |
| `contact_email` | String, 100 | No | Email address. Premium-gated. |

### `linkedin_executives_sample.csv`

Identical in shape to `linkedin_founders_sample.csv`, with `record_type` set to `executive` on every row and a different `person_title` choice list. Thirteen columns.

```text
source_system,record_type,import_run,import_state,run_provenance,error_message,raw_payload,person_name,startup_name,person_title,bio,linkedin_url,contact_email
```

| Column | Platform type | Mandatory | Choice values or format |
| --- | --- | --- | --- |
| `person_name` | String, 100 | Yes | Free text. Writes `Executive.name`. |
| `startup_name` | String, 100; natural key to `x_bst_startuptrk_startup` | Yes | An existing Startup `name`. Writes the `Executive.startup` reference. |
| `person_title` | String, 40 on staging; Choice on `Executive.title` | No | `CFO`, `VP Engineering`, `VP Sales`, `VP Marketing`, `Head of Product`, `Other` |
| `bio` | String, 2000 | No | Free text. Writes `Executive.bio`. |
| `linkedin_url` | String, 255 | No | Absolute URL. Writes `Executive.linkedin_url`. |
| `contact_email` | String, 100 | No | Email address. Premium-gated. |

### `linkedin_job_postings_sample.csv`

`source_system` is `linkedin` and `record_type` is `job_posting` on every row. Sixteen columns.

```text
source_system,record_type,import_run,import_state,run_provenance,error_message,raw_payload,startup_name,job_title,department,job_location,remote_type,seniority,posted_date,job_url,job_active
```

| Column | Platform type | Mandatory | Choice values or format |
| --- | --- | --- | --- |
| `startup_name` | String, 100; natural key to `x_bst_startuptrk_startup` | Yes | An existing Startup `name`. Writes the `JobPosting.startup` reference. |
| `job_title` | String, 150 | Yes | Free text. Writes `JobPosting.title`. |
| `department` | String, 40 on staging; Choice on `JobPosting.department` | No | `Engineering`, `Sales`, `Marketing`, `Product`, `Operations`, `Other` |
| `job_location` | String, 100 | No | Free text. Writes `JobPosting.location`. |
| `remote_type` | String, 20 on staging; Choice on `JobPosting.remote_type` | No | `Onsite`, `Hybrid`, `Remote` |
| `seniority` | String, 20 on staging; Choice on `JobPosting.seniority` | No | `Entry`, `Mid`, `Senior`, `Lead`, `Executive` |
| `posted_date` | Date (`glide_date`) | No | `YYYY-MM-DD`. |
| `job_url` | String, 255 | No | Absolute URL. Writes `JobPosting.url`. |
| `job_active` | True/False, dictionary default `true` | No | `true` or `false`. Writes `JobPosting.active`. |

### Premium-gated columns

Seven columns across these files carry values that field-level read ACLs restrict to the `x_bst_startuptrk.admin` and `x_bst_startuptrk.premium_user` roles once the records exist: `total_funding_usd` and `institutional_funding_last_5yrs` on startups, `contact_email` on both founders and executives, `aum_usd` on investors, and `amount_usd` and `valuation_usd` on funding rounds. The gating applies to the entity records the transform creates, not to the staging rows, which are administrator-only in their own right. The ACL matrix is in [`../docs/access-control.md`](../docs/access-control.md). Every sample value in these columns is synthetic.

## Value conventions

| Convention | Rule | Example |
| --- | --- | --- |
| Dates | ISO 8601 `YYYY-MM-DD`, zero-padded, no time component, no timezone, no offset. | `2024-03-07` |
| Currency | Plain unformatted United States dollars: digits only with an optional single decimal point. No thousands separator, no currency symbol, no `M` or `K` magnitude suffix. The field names fix the denomination as USD. | `42500000` or `42500000.50` |
| Booleans | Lowercase `true` or `false` only. Never `TRUE`, `True`, `1`, `0`, `yes`, `no`, `Y` or `N`. | `true` |
| Multi-valued fields | `focus_areas` and `participating_investor_names` are comma separated inside one double-quoted field. A bare comma separates values, with **no** space after it, so the transform splits without trimming ambiguity. Each element is spelled exactly as its choice list, or as the target record's `name`, spells it. | `"Fintech,SaaS,Deeptech"` |
| Empty means absent | An empty field means the value is absent. No sentinel string is ever used. | `,,` |
| Integers | Digits only, unquoted, no separators. | `2019` |
| URLs | Absolute, including the scheme. | `https://example.com/careers` |

### No sentinel values

The strings `Unknown`, `N/A`, `null` and `None` appear nowhere in these files and must not be introduced. Prompt section 4.0 requires a record missing a mandatory field to be **rejected**, not filled, so a blank field must stay blank in order for cleaning rule 4 to see it. Filling a blank with a sentinel converts a designed rejection into a silently accepted record.

### `raw_payload`

`raw_payload` is a JSON object carried as one double-quoted CSV field with every inner double quote doubled. It uses the **source system's own key vocabulary**, which is deliberately different from the flattened platform column names, so that it genuinely mimics the API response as prompt section 4.0 requires.

- **Crunchbase** organisation reads expose their fields under `data.properties`, with keys such as `name`, `short_description`, `founded_on`, `homepage_url`, `linkedin_url` and `num_employees_enum`. Funding rounds arrive under `data.items`.
- **LinkedIn** company, employee and job reads expose `data.elements`, with keys such as `id`, `name`, `title`, `description`, `website`, `industry`, `companySize.value`, `foundedYear` and `location.name`.

Each payload carries a handful of representative keys and stays well inside the 8000-character column limit. A payload for one startup row therefore reads like the following, before CSV quoting is applied:

```json
{"data":{"properties":{"name":"Example Labs","short_description":"Example analytics platform","founded_on":"2019-04-01","homepage_url":"https://examplelabs.example.com","num_employees_enum":"c_00051_c_00200"}}}
```

### Choice values

Every choice value is spelled exactly as its choice list spells it, including case, spaces, hyphens and the `+` in `Series C+` and `500+`. The authoritative lists are the `sys_choice` records in the Update Set, restated per record type in the tables above and in [`../docs/data-model.md`](../docs/data-model.md).

Cleaning rule 3 normalises `industry`, `funding_stage` and `round_type`: an incoming value is matched exactly, then case-insensitively, and a value matching nothing is stored as `Other` and logged by `IngestionLogger` as an unmatched value. The staging columns for these fields are plain strings with no choice list attached, so an unmatched value loads into staging unchanged and is normalised at transform time.

`investor_type` is the one asymmetry, and it must not be "fixed". The `Investor.type` choice list is `VC`, `Angel`, `PE`, `Corporate`, `Accelerator` and has **no `Other` member**, so an unmatched investor type has no value to normalise to and cleaning rule 3 does not apply to it. Every `investor_type` value in `crunchbase_investors_sample.csv` is therefore spelled exactly as the list spells it, and an unmatched value arriving in a live payload is corrected at source rather than coerced. **Do not add an `Other` choice to `Investor.type`**: prompt section 1.0 declares the field and choice definitions binding and complete.

## Row counts and designed defects

### Row counts

Sixty-four data rows in total, excluding header rows.

| File | Data rows |
| --- | --- |
| `crunchbase_startups_sample.csv` | 12 |
| `crunchbase_investors_sample.csv` | 8 |
| `crunchbase_funding_rounds_sample.csv` | 12 |
| `linkedin_founders_sample.csv` | 10 |
| `linkedin_executives_sample.csv` | 10 |
| `linkedin_job_postings_sample.csv` | 12 |

The count an operator sees in the import set after a load must equal the number above. A different count means the file was truncated, or a quoted field containing a line break was split.

All of the data is synthetic. It contains no real personal data, no real contact details and no real financial figures. Every `contact_email` value is an obviously synthetic address on an example domain, and every `linkedin_url` value is an obviously synthetic profile URL.

### Designed defects

Some rows are **deliberately defective** so that a load exercises all four of the prompt section 4.0 cleaning rules. They are intentional fixtures, not authoring errors.

| Rule | Which file demonstrates it | How to recognise the row | Expected outcome |
| --- | --- | --- | --- |
| 1. Trim whitespace on all string fields | All six files: the three `crunchbase_*_sample.csv` files and the three `linkedin_*_sample.csv` files, at least one row each | A quoted string value with leading or trailing space, for example `" Example Labs"` | The value is trimmed and the row loads and transforms normally. The trimmed value is what reaches the entity record. |
| 2. Deduplicate Startup records on `name` plus `headquarters_location`, case-insensitively | `crunchbase_startups_sample.csv` only | A pair of rows whose `startup_name` and `headquarters_location` match when both are lowercased and trimmed, but whose `startup_website` values differ | One Startup record survives the pair. The second row is recognised as a duplicate and does not create a second record. |
| 3. Normalise `industry`, `funding_stage` and `round_type`, mapping an unmatched value to `Other` and logging it | `crunchbase_startups_sample.csv` (`industry`, `funding_stage`) and `crunchbase_funding_rounds_sample.csv` (`round_type`) | A value that appears in no choice list, for example an `industry` of `Cleantech` or a `funding_stage` of `Series C` without the `+` | The value is stored as `Other` and `IngestionLogger` records it as an unmatched value. The row otherwise loads and transforms normally. |
| 4. Reject records missing mandatory fields rather than inserting partial records | All six files: the three `crunchbase_*_sample.csv` files and the three `linkedin_*_sample.csv` files, exactly one row each | A blank in a column marked mandatory for that record type: `startup_name` or `headquarters_location` on startups, `investor_name` on investors, `startup_name` or `round_date` on funding rounds, `person_name` or `startup_name` on founders and executives, `startup_name` or `job_title` on job postings | `import_state` becomes `rejected`, `error_message` names the missing field, and **no** entity record is created. |

Rule 2's duplicate pair differs on `startup_website` on purpose: the pair is the fixture that distinguishes a deduplication keyed on name plus headquarters location, which is what prompt section 4.0 specifies, from one keyed on name plus website, which would not catch this pair.

### Per-file defect map

Which fixture sits in which file, so a count can be reconciled file by file.

| File | Rule 1 whitespace | Rule 2 duplicate pair | Rule 3 unmatched choice | Rule 4 blank mandatory |
| --- | --- | --- | --- | --- |
| `crunchbase_startups_sample.csv` | At least one row | One pair | `industry` and `funding_stage` | One row |
| `crunchbase_investors_sample.csv` | At least one row | Not applicable | None; see the `investor_type` note above | One row |
| `crunchbase_funding_rounds_sample.csv` | At least one row | Not applicable | `round_type` | One row |
| `linkedin_founders_sample.csv` | At least one row | Not applicable | None | One row |
| `linkedin_executives_sample.csv` | At least one row | Not applicable | None | One row |
| `linkedin_job_postings_sample.csv` | At least one row | Not applicable | None | One row |

Three facts explain the shape of that map. Rule 2 deduplicates Startup records, so only the startups file can carry it. Rule 3 normalises `industry`, `funding_stage` and `round_type`, so only the startups and funding rounds files carry a rule 3 fixture; the remaining choice columns are loaded already matching their choice lists. Rule 4 has one fixture per file, which makes six rejected rows out of the sixty-four rows loaded.

### Non-resolving references

Every `startup_name`, `lead_investor_name` and `participating_investor_names` value in every child file resolves to a `name` present in `crunchbase_startups_sample.csv` or `crunchbase_investors_sample.csv`, with one class of exception.

The exception is the rule 4 fixtures. A row authored to be rejected for a blank mandatory field is the **only** kind of row whose natural-key reference may fail to resolve, and in those rows the failure is the blank itself: a blank `startup_name` on a founder, executive, funding round or job posting row cannot resolve to a Startup, which is precisely the condition rule 4 rejects. Recognise them by the blank column, one row per file, as listed in the rule 4 entry and the per-file defect map above. A non-resolving reference in any row that is **not** a rule 4 fixture is a mistake, not a designed defect, and should be reported.

## Data Import Wizard procedure

This is the folder-local summary of the load. The detailed authority, including the transform map and its field-by-field script, is [`../docs/manual-build/06-staging-table-csv-import.md`](../docs/manual-build/06-staging-table-csv-import.md).

### Prerequisites

- The Update Set has been committed to the target instance, so `x_bst_startuptrk_ingest_staging` exists. See [`../docs/deployment-runbook.md`](../docs/deployment-runbook.md).
- The operator holds the `x_bst_startuptrk.admin` role. The staging table grants read and write to that role only, so this procedure cannot be performed by a caller holding only `x_bst_startuptrk.user` or `x_bst_startuptrk.premium_user`. Creating the import set table and the transform map additionally requires the platform `admin` role.
- The application picker is set to **Boston Startup Tracker**, so the import set table and transform map are created inside the `x_bst_startuptrk` scope.

### Load order

Load the files in this order:

1. `crunchbase_startups_sample.csv`
2. `crunchbase_investors_sample.csv`
3. `crunchbase_funding_rounds_sample.csv`
4. `linkedin_founders_sample.csv`, `linkedin_executives_sample.csv` and `linkedin_job_postings_sample.csv`, in any order

The order is load-bearing: child rows carry natural-key references to startups and investors, and those records must already exist for the transform to resolve them. Funding rounds reference both startups and investors, so both parent files precede them.

### Steps

For each file in the order above:

1. Open the Data Import Wizard from the application navigator, with the application picker set to **Boston Startup Tracker**.
2. Choose to import a data source, and create or select the import set table for this dataset.
3. Upload the CSV. The wizard reads the header row and offers one source column per header.
4. Verify the field mapping is one-to-one by header name against the `x_bst_startuptrk_ingest_staging` dictionary, and that **no** column is left unmapped. An unmapped column loads as an empty field without raising an error.
5. Run the import.
6. Confirm the imported row count equals the count stated for that file in this document.
7. Run the transform per [`../docs/manual-build/06-staging-table-csv-import.md`](../docs/manual-build/06-staging-table-csv-import.md).

### Verification after each load

Check all four of the following on the staged rows before running the transform. The staged rows are reachable through the **Ingestion staging** module of the Boston Startup Tracker application menu.

- The row count matches the count stated for that file.
- Every row shows `import_state` of `pending`.
- Every row shows `run_provenance` of `fallback`.
- Every row has an empty `error_message`.

After the transform, `import_state` is `processed` on accepted rows and `rejected` on the rule 4 fixtures, and `error_message` names the missing field on each rejected row.

### Forcing the fallback path

Set the property `x_bst_startuptrk.ingestion.source_mode` to `fallback` to make both ingestion flows read this dataset instead of attempting a live call, which is how a flow test is made deterministic without touching credentials. Set it back to `live` afterwards. The flow-side steps are in [`../docs/manual-build/02-flow-crunchbase-ingestion.md`](../docs/manual-build/02-flow-crunchbase-ingestion.md) and [`../docs/manual-build/03-flow-linkedin-ingestion.md`](../docs/manual-build/03-flow-linkedin-ingestion.md).

## Run provenance and criterion 4 evidence

Every row shipped in this folder carries `run_provenance` of `fallback`. A flow run that reads this dataset records the same provenance for the run as a whole: `IngestionLogger.writeRunSummary` sets the property `x_bst_startuptrk.ingestion.last_run_provenance` to `fallback` and writes a run summary to the flow execution log carrying the run identifier, the provenance, and the processed, rejected and skipped counts. A run that completed a live call records `live` by the same path.

Prompt section 10.0 criterion 4 accepts the sample-dataset substitute for live ingestion, so three consecutive clean fallback runs of each flow satisfy it **provided the mode is recorded** for each run. The recording is itself part of the acceptance evidence: an Automated Test Framework result that exercised this dataset is labelled **"fallback validated"**, and only a result from a successful live call is labelled **"live validated"**, so the two can never be confused after the fact. The labelling convention is applied in [`../docs/manual-build/05-atf-test-suites.md`](../docs/manual-build/05-atf-test-suites.md) and the evidence is collected in [`../docs/validation-checklist.md`](../docs/validation-checklist.md).

For criterion 4 purposes a **scheduled run** means a flow execution that passed the flow's cadence guard and went on to do work. An execution that started, found the configured cadence had not yet elapsed and exited without ingesting is a no-op and does not count towards the three consecutive runs. The definition and the way to distinguish the two in the execution log are in [`../docs/deployment-runbook.md`](../docs/deployment-runbook.md).

## The three-way contract

Three artifacts describe the same set of staging columns, and all three must be changed together. Changing one alone breaks the fallback path without raising an error: the wizard leaves the renamed column unmapped, the field loads empty, and the transform produces incomplete records or rejects valid ones.

| Leg | Artifact | Role |
| --- | --- | --- |
| a | The header rows of the six CSVs in this folder, documented above | The wire format |
| b | The `x_bst_startuptrk_ingest_staging` dictionary records in [`../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml`](../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml) | **Authoritative** |
| c | The field mapping in [`../docs/manual-build/06-staging-table-csv-import.md`](../docs/manual-build/06-staging-table-csv-import.md) | The load instructions |

Leg b is authoritative. Where this document and the dictionary disagree about a column name, type, length or choice value, the dictionary is correct and this document is corrected to match it, never the reverse.

## Related documents

- [`../README.md`](../README.md) — package index for the ServiceNow deliverable
- [`../docs/data-model.md`](../docs/data-model.md) — all ten tables, field by field
- [`../docs/manual-build/06-staging-table-csv-import.md`](../docs/manual-build/06-staging-table-csv-import.md) — the detailed import and transform guide
- [`../docs/manual-build/01-connection-credential-aliases.md`](../docs/manual-build/01-connection-credential-aliases.md) — the two credential aliases the live path uses
- [`../docs/manual-build/02-flow-crunchbase-ingestion.md`](../docs/manual-build/02-flow-crunchbase-ingestion.md) — the Crunchbase ingestion flow
- [`../docs/manual-build/03-flow-linkedin-ingestion.md`](../docs/manual-build/03-flow-linkedin-ingestion.md) — the LinkedIn ingestion flow
- [`../docs/manual-build/05-atf-test-suites.md`](../docs/manual-build/05-atf-test-suites.md) — the test suites, including the provenance labelling
- [`../docs/access-control.md`](../docs/access-control.md) — roles and the premium field ACL matrix
- [`../docs/validation-checklist.md`](../docs/validation-checklist.md) — the success criteria and their evidence
- [`../docs/gaps-and-flags.md`](../docs/gaps-and-flags.md) — requirements with no clean platform equivalent
- [`../docs/deployment-runbook.md`](../docs/deployment-runbook.md) — import sequence, gates and rollback
- [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md) — the single source of truth for every decision, alternative and risk behind this contract
