# Sample Data — Fallback Dataset

This folder holds the fallback dataset required by prompt section 4.0. Its six CSV files load into the single staging table `x_bst_startuptrk_ingest_staging` in the scoped application `x_bst_startuptrk`, and they stand in for a live Crunchbase or LinkedIn API response when live authentication fails, times out, returns a malformed response, or while credentials are being re-issued.

The dataset is **fallback only** by design. An ingestion run is required to attempt the live call first and to read the staging table only when that attempt fails, or when the property `x_bst_startuptrk.ingestion.source_mode` is set to `fallback` to make a test deterministic.

## Prerequisites for live ingestion

The live path depends on two Connection and Credential Aliases, `x_bst_startuptrk.crunchbase_api` (Basic Auth) and `x_bst_startuptrk.linkedin_oauth` (OAuth2), which the ingestion flows reference by name. **Both aliases must exist on the target instance and carry credential material provisioned by the operator — the Crunchbase API key, and the LinkedIn OAuth2 client identifier, client secret and refresh token — before any live call can succeed.** Both are built by hand; the procedure is [`../docs/manual-build/01-connection-credential-aliases.md` (planned)](../docs/manual-build/01-connection-credential-aliases.md).

While either alias is unprovisioned, **every ingestion run reads this dataset and every result must be labelled "fallback validated"**, never "live validated". Prompt section 10.0 criterion 4 accepts the sample-dataset substitute, so that condition does not block acceptance; it only constrains what the evidence may claim.

No credential material appears in this folder, in the Update Set, or in any flow input or script step. The two non-secret API base URLs are the properties `x_bst_startuptrk.crunchbase.base_url` and `x_bst_startuptrk.linkedin.base_url`.

## Referenced documents

This document is self-contained: the column contract, the value conventions, the designed-defect inventory and the load procedure are all stated here in full, and nothing in them requires reading another file.

Some documents named in this specification are **planned artifacts of this package**. Every link to one carries the marker **(planned)** in its link text. A statement about a planned document describes what that document is required to contain; it is not a claim that the content can be read from it. Links without the marker point at delivered files: the six CSVs beside this one, the Update Set XML, and `../docs/data-model.md`, `../docs/access-control.md`, `../docs/api-reference.md` and `../docs/validation-gates.md`.

This document carries no rationale. Every decision behind the contract, every alternative considered and every risk is to be recorded in [`../../docs/decisions/DECISION_LOG.md` (planned)](../../docs/decisions/DECISION_LOG.md).

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

There is deliberately **no NewsArticle CSV**. Prompt sections 1.7 and 4.0 exclude NewsArticle from automated ingestion, so no flow serves it and it has no fallback dataset; NewsArticle records are created by manual entry or by a separate ad hoc import. The exclusion is to be recorded in [`../docs/gaps-and-flags.md` (planned)](../docs/gaps-and-flags.md) and [`../../docs/decisions/DECISION_LOG.md` (planned)](../../docs/decisions/DECISION_LOG.md).

## CSV dialect

The dialect is specified here in full. All six files conform to it.

- **Format** — RFC 4180.
- **Field delimiter** — a comma (`,`).
- **Quoting character** — the double quote (`"`).
- **Escaping** — a literal double quote inside a quoted field is escaped by doubling it (`""`).
- **When to quote** — fields are quoted where they contain a comma, a double quote or a line break, and where a designed leading or trailing space must survive the round trip. Every other field is unquoted.
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
| `error_message` | String, 1000 | Empty on every shipped row | Rejection or error detail. `IngestionMapper.clean()` **returns** the reason; the ingestion flow's staging-update step is what writes it to this column, together with the matching `import_state`. |
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

`x_bst_startuptrk_ingest_staging` is one flat table serving all six record types, and its flattened columns carry the prompt section 1.0 column names of the entity each record type becomes. A column whose name is shared by more than one entity is therefore one staging column read by more than one record type, not one column per entity:

| Staging column | Read by record types | Carries |
| --- | --- | --- |
| `name` | `startup`, `investor`, `founder`, `executive` | The record's own name |
| `website` | `startup`, `investor` | The record's own website |
| `active` | `startup`, `job_posting` | The record's own active flag |
| `title` | `founder`, `executive`, `job_posting` | The person's title, or the posting's role title |
| `startup_name` | `founder`, `executive`, `funding_round`, `job_posting` | The natural key naming the **parent** Startup |
| `headquarters_location` | `startup` | The Startup's own headquarters location |

`headquarters_location` is a `startup`-row column only. No child file carries it.

The column names below are the dictionary element names exactly as the Update Set declares them, and the target field named in each table is the prompt section 1.0 field the transform writes.

### The `_name` natural-key convention

A CSV cannot carry a `sys_id` for a record that does not exist yet, so every reference travels as the target record's natural key — its `name` value — and the transform resolves it at load time. No column carries a `sys_id`. Three columns are natural keys: `startup_name` resolves to a `x_bst_startuptrk_startup` record, and `lead_investor_name` and `participating_investor_names` resolve to `x_bst_startuptrk_investor` records. The transform's resolution steps are to be specified in [`../docs/manual-build/06-staging-table-csv-import.md` (planned)](../docs/manual-build/06-staging-table-csv-import.md); the resolution `IngestionMapper` performs is described under [Natural keys](#natural-keys).

`startup_name` appears only on the four child record types, where it names the parent Startup. A `startup` row carries its own name in `name`, and an `investor` row likewise carries its own name in `name`.

#### Parent resolution is by `startup_name` alone

`IngestionMapper.resolveStartup()` matches `startup_name` against `x_bst_startuptrk_startup.name`, trimming and lowering both sides, and resolves only when exactly one startup carries the name. Resolution is deterministic in every case, and never approximate:

| Row carries | Startups matching | Outcome |
| --- | --- | --- |
| `startup_name` | Exactly one carrying that name | Resolved. |
| `startup_name` | More than one carrying that name | Logged as a skip reporting the parent as **ambiguous**; no entity record is created. |
| `startup_name` | None | Logged as a skip naming the value; no entity record is created. |
| `startup_name` blank | Not attempted | Cleaning rule 4 rejects the row for a missing mandatory `startup`, which is the documented rule 4 outcome rather than a resolution failure. |

Cleaning rule 2 de-duplicates Startup records on `name` **plus** `headquarters_location`, so a Startup's identity within the startups file is that pair. A resolved parent is consequently the single record that survived that de-duplication, and a child row needs only its name to reach it.

Both sides are trimmed and lowered before comparison, so a child row may spell `startup_name` in any case and with any surrounding whitespace. Several rows in these files deliberately do: `linkedin_founders_sample.csv` carries `"Copley Grid Systems "` with a trailing space, `linkedin_executives_sample.csv` carries `"Seaport Ledger "`, `linkedin_job_postings_sample.csv` carries `"Kendall Cognition "`, and `crunchbase_funding_rounds_sample.csv` carries `" Muddy River Diagnostics"` with a leading space. Each resolves, which is what makes those rows evidence that trimming happens **before** natural-key resolution.

No row in this dataset exercises the ambiguous branch, because no two startups here share a name. That branch is covered by the mapper's logic and by the manual build guide's test steps rather than by a fixture; adding a second same-named startup would change the row counts and the rule 2 fixture design recorded below.

### Mandatory columns

The staging dictionary marks no column mandatory, so a row with a blank mandatory value loads into staging successfully. The requirement is enforced at transform time, per record type, by cleaning rule 4: a row missing any of its mandatory values is rejected instead of producing a partial entity record. The **Mandatory** column in each table below is that transform-time requirement, and it is the set `IngestionMapper.MANDATORY` registers for that record type.

Twelve mandatory columns across the six record types:

| Record type | Mandatory columns | Count |
| --- | --- | --- |
| `startup` | `name`, `headquarters_location`, `active` | 3 |
| `investor` | `name` | 1 |
| `funding_round` | `startup_name`, `round_date` | 2 |
| `founder` | `name`, `startup_name` | 2 |
| `executive` | `name`, `startup_name` | 2 |
| `job_posting` | `startup_name`, `title` | 2 |

`active` is a String column of length 10 on staging, carrying the text `true` or `false`, and it declares no dictionary default. A blank field therefore reaches the transform as a blank and cleaning rule 4 observes the absent mandatory value; the **Trim and validate startup** business rule likewise aborts an insert or update whose `active` is empty. `x_bst_startuptrk_startup.active` keeps its own dictionary default of `true`, which applies to a Startup inserted without the field set. Per prompt section 4.0 a record missing a mandatory value is rejected, not filled. The column-type decision and the alternative considered are to be recorded in [`../../docs/decisions/DECISION_LOG.md` (planned)](../../docs/decisions/DECISION_LOG.md).

### `crunchbase_startups_sample.csv`

`source_system` is `crunchbase` and `record_type` is `startup` on every row. Nineteen columns.

```text
source_system,record_type,import_run,import_state,run_provenance,error_message,raw_payload,name,description,industry,founded_year,headquarters_location,website,logo_url,funding_stage,total_funding_usd,active,institutional_funding_last_5yrs,employee_count_range
```

| Column | Platform type | Mandatory | Choice values or format |
| --- | --- | --- | --- |
| `name` | String, 100 | Yes | Free text. Writes `Startup.name`, and is the first half of the deduplication key. |
| `description` | String, 4000 | No | Free text. Writes `Startup.description`. |
| `industry` | String, 40 on staging; Choice on `Startup.industry` | No | `Fintech`, `Healthtech`, `SaaS`, `Consumer`, `Deeptech`, `Other` |
| `founded_year` | Integer | No | A four-digit year, for example `2019`. |
| `headquarters_location` | String, 100 | Yes | Free text. Writes `Startup.headquarters_location`, and is the second half of the deduplication key. |
| `website` | String, 255 | No | Absolute URL. Writes `Startup.website`. |
| `logo_url` | String, 255 | No | Absolute URL. Writes `Startup.logo_url`. |
| `funding_stage` | String, 40 on staging; Choice on `Startup.funding_stage` | No | `Pre-Seed`, `Seed`, `Series A`, `Series B`, `Series C+`, `Growth`, `Public`, `Acquired` |
| `total_funding_usd` | Decimal on staging; Currency on `Startup.total_funding_usd` | No | Plain USD amount. Premium-gated. |
| `active` | String, 10 on staging; True/False on `Startup.active` | **Yes** | `true` or `false`, lowercase. Writes `Startup.active`, which prompt section 1.0 declares mandatory. The staging column is a plain string with no dictionary default, so a blank field stays blank through the load and cleaning rule 4 rejects the row; `x_bst_startuptrk_startup.active` keeps its own dictionary default of `true`. |
| `institutional_funding_last_5yrs` | True/False, dictionary default `false` | No | `true` or `false`. Premium-gated. |
| `employee_count_range` | String, 20 on staging; Choice on `Startup.employee_count_range` | No | `1-10`, `11-50`, `51-200`, `201-500`, `500+` |

### `crunchbase_investors_sample.csv`

`source_system` is `crunchbase` and `record_type` is `investor` on every row. Twelve columns.

```text
source_system,record_type,import_run,import_state,run_provenance,error_message,raw_payload,name,type,focus_areas,website,aum_usd
```

| Column | Platform type | Mandatory | Choice values or format |
| --- | --- | --- | --- |
| `name` | String, 100 | Yes | Free text. Writes `Investor.name`. |
| `type` | String, 30 on staging; Choice on `Investor.type` | No | `VC`, `Angel`, `PE`, `Corporate`, `Accelerator` |
| `focus_areas` | String, 255 on staging; Multi-choice on `Investor.focus_areas` | No | One or more of `Fintech`, `Healthtech`, `SaaS`, `Consumer`, `Deeptech`, `Other`, comma separated. |
| `website` | String, 255 | No | Absolute URL. Writes `Investor.website`. |
| `aum_usd` | Decimal on staging; Currency on `Investor.aum_usd` | No | Plain USD amount. Premium-gated. |

`portfolio_count` is deliberately **absent** from this file and from the staging dictionary. Prompt section 1.4 declares `Investor.portfolio_count` calculated, and it is derived by the `InvestorPortfolioService` Script Include and maintained by the two portfolio business rules on `x_bst_startuptrk_fundinground` and `x_bst_startuptrk_m2m_round_investor`. The column is read-only in the dictionary, so an import that mapped a staged value onto it would be refused; the value is established by running `InvestorPortfolioService.recalculateAll()` from a background script once the funding rounds and join rows have loaded, as [`../docs/manual-build/06-staging-table-csv-import.md`](../docs/manual-build/06-staging-table-csv-import.md) requires. Its derivation is described in [`../docs/data-model.md`](../docs/data-model.md) and the decision is recorded in [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md).

### `crunchbase_funding_rounds_sample.csv`

`source_system` is `crunchbase` and `record_type` is `funding_round` on every row. Fifteen columns.

```text
source_system,record_type,import_run,import_state,run_provenance,error_message,raw_payload,startup_name,round_type,amount_usd,valuation_usd,round_date,lead_investor_name,participating_investor_names,source_url
```

| Column | Platform type | Mandatory | Choice values or format |
| --- | --- | --- | --- |
| `startup_name` | String, 100; natural key to `x_bst_startuptrk_startup` | Yes | An existing Startup `name`, matched case-insensitively after trimming. Resolves to the `FundingRound.startup` reference and is not written to the child record. |
| `round_type` | String, 40 on staging; Choice on `FundingRound.round_type` | No | `Pre-Seed`, `Seed`, `Series A`, `Series B`, `Series C+`, `Growth`, `Public`, `Acquired` |
| `amount_usd` | Decimal on staging; Currency on `FundingRound.amount_usd` | No | Plain USD amount. Premium-gated. |
| `valuation_usd` | Decimal on staging; Currency on `FundingRound.valuation_usd` | No | Plain USD amount. Premium-gated. |
| `round_date` | Date (`glide_date`) | Yes | `YYYY-MM-DD`. |
| `lead_investor_name` | String, 100; natural key to `x_bst_startuptrk_investor` | No | An existing Investor `name`. Writes the `FundingRound.lead_investor` reference. |
| `participating_investor_names` | String, 1000; multi-valued natural keys to `x_bst_startuptrk_investor` | No | **Comma separated** Investor `name` values inside one double-quoted field, each separated by a bare comma with no following space, for example `"Emerald Necklace Angels,Chickatawbut Seed Partners"`. `IngestionMapper.parseInvestorNames()` splits on the comma, trims each member, drops an empty member and keeps a repeated member once. An empty field means no participants. |
| `source_url` | String, 255 | No | Absolute URL. Writes `FundingRound.source_url`. |

`lead_investor_name` and `participating_investor_names` are distinct columns with distinct destinations. The lead investor is a first-class reference field on the funding round. Each participating investor becomes one row in the join table `x_bst_startuptrk_m2m_round_investor`, which is the **only** table the transform writes for participation. An investor may appear in both columns on the same row.

The join table is authoritative. Two surfaces are derived from it and neither is a second place to write: the read-only `FundingRound.participating_investors` column, a stored list of investor references that the round-investor-link business rule projects from the join table, and the REST `participating_investors` array, which the API assembles from the join table directly. The transform must therefore create join rows and must **not** attempt to write `FundingRound.participating_investors`; the column is read-only and the projection maintains itself. `InvestorPortfolioService.linkInvestorToRound()` is the method to create a join row: it is idempotent, so re-running a load cannot create a duplicate pair, and a unique composite index on `(funding_round, investor)` enforces that whatever the write path. The semantics are in [`../docs/data-model.md`](../docs/data-model.md).

### `linkedin_founders_sample.csv`

`source_system` is `linkedin` and `record_type` is `founder` on every row. Thirteen columns.

```text
source_system,record_type,import_run,import_state,run_provenance,error_message,raw_payload,name,startup_name,title,bio,linkedin_url,contact_email
```

| Column | Platform type | Mandatory | Choice values or format |
| --- | --- | --- | --- |
| `name` | String, 100 | Yes | Free text. Writes `Founder.name`. |
| `startup_name` | String, 100; natural key to `x_bst_startuptrk_startup` | Yes | An existing Startup `name`, matched case-insensitively after trimming. Resolves to the `Founder.startup` reference and is not written to the child record. |
| `title` | String, 150 on staging; Choice on `Founder.title` | No | `CEO`, `CTO`, `COO`, `Co-Founder`, `Other` |
| `bio` | String, 2000 | No | Free text. Writes `Founder.bio`. |
| `linkedin_url` | String, 255 | No | Absolute URL. Writes `Founder.linkedin_url`. |
| `contact_email` | String, 100 | No | Email address. Premium-gated. |

### `linkedin_executives_sample.csv`

Identical in shape to `linkedin_founders_sample.csv`, with `record_type` set to `executive` on every row and a different `title` choice list. Thirteen columns.

```text
source_system,record_type,import_run,import_state,run_provenance,error_message,raw_payload,name,startup_name,title,bio,linkedin_url,contact_email
```

| Column | Platform type | Mandatory | Choice values or format |
| --- | --- | --- | --- |
| `name` | String, 100 | Yes | Free text. Writes `Executive.name`. |
| `startup_name` | String, 100; natural key to `x_bst_startuptrk_startup` | Yes | An existing Startup `name`, matched case-insensitively after trimming. Resolves to the `Executive.startup` reference and is not written to the child record. |
| `title` | String, 150 on staging; Choice on `Executive.title` | No | `CFO`, `VP Engineering`, `VP Sales`, `VP Marketing`, `Head of Product`, `Other` |
| `bio` | String, 2000 | No | Free text. Writes `Executive.bio`. |
| `linkedin_url` | String, 255 | No | Absolute URL. Writes `Executive.linkedin_url`. |
| `contact_email` | String, 100 | No | Email address. Premium-gated. |

### `linkedin_job_postings_sample.csv`

`source_system` is `linkedin` and `record_type` is `job_posting` on every row. Sixteen columns.

```text
source_system,record_type,import_run,import_state,run_provenance,error_message,raw_payload,startup_name,title,department,location,remote_type,seniority,posted_date,url,active
```

| Column | Platform type | Mandatory | Choice values or format |
| --- | --- | --- | --- |
| `startup_name` | String, 100; natural key to `x_bst_startuptrk_startup` | Yes | An existing Startup `name`, matched case-insensitively after trimming. Resolves to the `JobPosting.startup` reference and is not written to the child record. |
| `title` | String, 150 | Yes | Free text. Writes `JobPosting.title`. |
| `department` | String, 40 on staging; Choice on `JobPosting.department` | No | `Engineering`, `Sales`, `Marketing`, `Product`, `Operations`, `Other` |
| `location` | String, 100 | No | Free text. Writes `JobPosting.location`. |
| `remote_type` | String, 20 on staging; Choice on `JobPosting.remote_type` | No | `Onsite`, `Hybrid`, `Remote` |
| `seniority` | String, 20 on staging; Choice on `JobPosting.seniority` | No | `Entry`, `Mid`, `Senior`, `Lead`, `Executive` |
| `posted_date` | Date (`glide_date`) | No | `YYYY-MM-DD`. |
| `url` | String, 255 | No | Absolute URL. Writes `JobPosting.url`. |
| `active` | True/False, no staging default | No | `true` or `false`. Writes `JobPosting.active`. A blank value is left unset so the `JobPosting.active` dictionary default `true` applies. |

### Premium-gated columns

Seven columns across these files carry values that field-level read ACLs restrict to the `x_bst_startuptrk.admin` and `x_bst_startuptrk.premium_user` roles once the records exist: `total_funding_usd` and `institutional_funding_last_5yrs` on startups, `contact_email` on both founders and executives, `aum_usd` on investors, and `amount_usd` and `valuation_usd` on funding rounds. The ACL matrix is in [`../docs/access-control.md`](../docs/access-control.md). Every sample value in these columns is synthetic.

**Field-level gating applies to the entity records the transform creates, not to the staging rows** — a staging row carries every value in the clear. The staging table is protected at the table level instead, and in every direction:

| Control | `x_bst_startuptrk_ingest_staging` |
| --- | --- |
| Read | `x_bst_startuptrk.admin` only |
| Write | `x_bst_startuptrk.admin` only |
| Create | `x_bst_startuptrk.admin` only |
| Delete | `x_bst_startuptrk.admin` only |
| `sys_db_object.access` | `package_private` — unreachable from any other application scope |
| `sys_db_object.ws_access` | false — **not served at `/api/now/table/x_bst_startuptrk_ingest_staging`** |

All four operations carry an explicit access control rather than relying on the platform's default deny, and the table is sealed to the scope and withheld from the Table API, so there is no path by which a caller holding `x_bst_startuptrk.user` or `x_bst_startuptrk.premium_user` can read a premium value out of a staging row that the entity-level gate would have denied them. The twelve supporting-table controls are Layer 4 of [`../docs/access-control.md`](../docs/access-control.md); the table posture is under [`../docs/data-model.md`](../docs/data-model.md).

## Value conventions

| Convention | Rule | Example |
| --- | --- | --- |
| Dates | ISO 8601 `YYYY-MM-DD`, zero-padded, no time component, no timezone, no offset. | `2024-03-07` |
| Currency | Plain unformatted United States dollars: digits only with an optional single decimal point. No thousands separator, no currency symbol, no `M` or `K` magnitude suffix. The field names fix the denomination as USD. | `42500000` or `42500000.50` |
| Booleans | Lowercase `true` or `false` only. Never `TRUE`, `True`, `1`, `0`, `yes`, `no`, `Y` or `N`. | `true` |
| Multi-valued choice fields | `focus_areas` is comma separated inside one double-quoted field. A bare comma separates values, with **no** space after it. Each element is spelled exactly as its choice list spells it. A comma is safe here because no choice value contains one. | `"Fintech,SaaS,Deeptech"` |
| Multi-valued natural keys | `participating_investor_names` is comma separated inside one double-quoted field, on the same convention as `focus_areas`. A bare comma separates values, with **no** space after it. Each element is an Investor `name` spelled as that record spells it. An empty field means no participants. | `"Emerald Necklace Angels,Chickatawbut Seed Partners"` |
| Empty means absent | An empty field means the value is absent. No sentinel string is ever used. On `active`, a String column on staging, a blank therefore reaches the transform as a blank and cleaning rule 4 rejects the row. On `institutional_funding_last_5yrs`, a True/False column carrying a dictionary default of `false`, a blank resolves to that default — it is not mandatory, and every shipped row supplies it, so no row relies on the distinction. | `,,` |
| Integers | Digits only, unquoted, no separators. | `2019` |
| URLs | Absolute, including the scheme. | `https://example.com/careers` |

### No sentinel values

The strings `Unknown`, `N/A`, `null` and `None` appear nowhere in these files and must not be introduced. Prompt section 4.0 requires a record missing a mandatory field to be **rejected**, not filled, so a blank field must stay blank in order for cleaning rule 4 to see it.

### `raw_payload`

`raw_payload` is a JSON object carried as one double-quoted CSV field with every inner double quote doubled. It uses the **source system's own key vocabulary**, not the flattened platform column names. Prompt section 4.0 requires the staging shape to mimic the expected API response, and this column carries that shape.

- **Crunchbase** organisation reads expose their fields under `data.properties`, with keys such as `name`, `short_description`, `founded_on`, `homepage_url`, `linkedin_url` and `num_employees_enum`. Funding rounds arrive under `data.items`.
- **LinkedIn** company, employee and job reads expose an `elements` array with keys such as `id`, `name`, `title`, `description`, `website`, `industry`, `companySize.value`, `foundedYear` and `location.name`. In this dataset that array is carried under the same `data` wrapper the Crunchbase fixtures use, so all six files share one envelope shape. `IngestionMapper.unwrapLive()` accepts the collection at the root of the payload or under `data`, so a live LinkedIn response that places `elements` at the root — as the reader at `src/data_collection/api_integrators/linkedin_integrator.py:L31`, `:L50` and `:L69` does — is unwrapped identically.

`participating_investor_names` does **not** use the JSON convention. It is a comma separated list of investor names, and `IngestionMapper.parseInvestorNames()` splits it on the comma, trims each member, drops an empty member and keeps a repeated member once. A value that yields no name at all is logged by `IngestionLogger.invalidEncoding()`. The delimiter is safe for this dataset because no investor name in `crunchbase_investors_sample.csv` contains a comma; an incoming live name that did would have to be corrected at source before it could be staged.

Each payload carries a handful of representative keys and stays well inside the 8000-character column limit. A payload for one startup row therefore reads like the following, before CSV quoting is applied:

```json
{"data":{"properties":{"name":"Example Labs","short_description":"Example analytics platform","founded_on":"2019-04-01","homepage_url":"https://examplelabs.example.com","num_employees_enum":"c_00051_c_00200"}}}
```

A LinkedIn payload for one founder row reads like this, with no wrapper above `elements`:

```json
{"elements":[{"id":"ln-member-40118","name":"Example Person","title":"CEO","headline":"CEO at Example Labs","profileUrl":"https://people.example.com/in/example-person"}]}
```

### Choice values

Every choice value is spelled exactly as its choice list spells it, including case, spaces, hyphens and the `+` in `Series C+` and `500+`. The authoritative lists are the `sys_choice` records in the Update Set, restated per record type in the tables above and in [`../docs/data-model.md`](../docs/data-model.md).

Cleaning rule 3 normalises **every** closed-choice column, not just some of them. `IngestionMapper.normaliseChoice()` matches an incoming value exactly, then case-insensitively, and where nothing matches it applies one of two outcomes:

- The value is stored as `Other` **where the target choice list declares an `Other` member**.
- The field is **left empty** where the target list declares no `Other` member.

`IngestionLogger` records a `choice_unmatched` event either way, naming the record type, the column and which outcome was applied. **No value outside a choice list is ever stored on an entity record.** The staging columns for choice fields are plain strings with no choice list attached, so an unmatched value loads into staging unchanged and is normalised at transform time.

**The supplied value itself is logged only when it is safe to log.** `IngestionLogger` applies one rule to every unmatched choice value before it reaches a log line:

| Case | What the log line carries |
| --- | --- |
| The value is empty | The literal `(blank)` |
| The column is one that can carry personal or free-text data | `fp:` followed by an eight-character run-salted fingerprint |
| The value has the shape of a short enumeration label — begins with a letter or digit, is at most 40 characters, and uses only letters, digits, spaces and `+ . _ / -` | The value **verbatim**, so an operator can see exactly what the source sent and correct the mapping |
| Anything else — longer than 40 characters, or containing a comma, an `@`, a quote or any other character outside that set | `fp:` followed by the fingerprint |

The ten choice columns cleaning rule 3 normalises — `industry`, `funding_stage`, `employee_count_range`, `title`, `type`, `focus_areas`, `round_type`, `department`, `remote_type` and `seniority` — are all closed enumerations that carry no personal data, so a genuinely mis-spelled choice value such as `series-a` or `Chief Technology Officer` is logged in full and is directly actionable. A value that arrives in one of them looking nothing like an enumeration label — a pasted biography, an address, a comma-joined list — is fingerprinted instead, because a value that shape is far more likely to be misplaced person data than a mis-spelled choice.

The fingerprint is salted with the run identifier, so the same value fingerprints identically **within** one run and differently between runs: an operator can count how many rows shared one bad value without the value itself, or any cross-run identifier for it, ever being recorded. It is a correlation aid, not a cryptographic digest, and it is not reversible to the original value.

The same policy governs every other log line the ingestion pipeline writes. **No external name, email address, biography, URL, upstream message or raw payload fragment reaches the flow execution log or the system log.** Records are identified by an opaque reference — a kind prefix and a sanitised token, such as `startup:fp:1a2b3c4d` or `record:` followed by a platform record identifier — and never by name. Anyone reading a log line therefore cannot recover who a skipped record was about, which is why the erasure procedure in [`../docs/data-model.md`](../docs/data-model.md) covers three data surfaces and not the logs.

Six of the eleven choice lists declare no `Other` member — `Startup.funding_stage`, `Startup.employee_count_range`, `Investor.type`, `FundingRound.round_type`, `JobPosting.remote_type` and `JobPosting.seniority` — and an unmatched value in any of them is logged and the field left empty. The other five — `Startup.industry`, `Investor.focus_areas`, `Founder.title`, `Executive.title` and `JobPosting.department` — declare `Other`, and an unmatched value in any of them is stored as `Other` and logged. **Do not add an `Other` choice to any of the six lists that lack one**: prompt section 1.0 declares the field and choice definitions binding and complete, and the `sys_choice` inventory in the Update Set is exactly the 63 entity choice values those definitions declare. The full column-by-column outcome table is in [`../docs/data-model.md`](../docs/data-model.md).

## Row counts and designed defects

### Row counts

Sixty-five data rows in total, excluding header rows.

| File | Data rows |
| --- | --- |
| `crunchbase_startups_sample.csv` | 13 |
| `crunchbase_investors_sample.csv` | 8 |
| `crunchbase_funding_rounds_sample.csv` | 12 |
| `linkedin_founders_sample.csv` | 10 |
| `linkedin_executives_sample.csv` | 10 |
| `linkedin_job_postings_sample.csv` | 12 |

The count an operator sees in the import set after a load must equal the number above. A different count means the file was truncated, or a quoted field containing a line break was split.

After the transform has run over all sixty-five rows, `x_bst_startuptrk_ingest_staging.import_state` reconciles to **52 `processed`, 13 `rejected`, 0 `error` and 0 `pending`**. The thirteen rejected rows are the twelve blank-mandatory fixtures plus the one batch duplicate, and `error_message` names the reason on each. `IngestionLogger` records eleven `choice_unmatched` events across the run pair, one for each of the eleven choice-backed columns. A different distribution means a file was edited or the transform map is mismapped.

All of the data is synthetic. It contains no real personal data, no real contact details and no real financial figures. Every `contact_email` value is an obviously synthetic address on an example domain, and every `linkedin_url` value is an obviously synthetic profile URL.

### Designed defects

Some rows are **deliberately defective** so that a load exercises all four of the prompt section 4.0 cleaning rules. They are intentional fixtures, not authoring errors.

| Rule | Which file demonstrates it | How to recognise the row | Expected outcome |
| --- | --- | --- | --- |
| 1. Trim whitespace on all string fields | All six files: the three `crunchbase_*_sample.csv` files and the three `linkedin_*_sample.csv` files, at least one row each | A quoted string value with leading or trailing space, for example `" Example Labs"` | The value is trimmed and the row loads and transforms normally. The trimmed value is what reaches the entity record. |
| 2. Deduplicate Startup records on `name` plus `headquarters_location`, case-insensitively | `crunchbase_startups_sample.csv` only | A pair of rows whose `name` and `headquarters_location` match when both are lowercased and trimmed, but whose `website` values differ | One Startup record survives the pair. The second row is recognised as a duplicate and does not create a second record. |
| 3. Normalise every choice-backed column, mapping an unmatched value to `Other` where the list defines one and logging it | All six files. Eleven values across ten rows carry an unmatched choice value; they are listed row by row in [Unmatched values in choice columns](#unmatched-values-in-choice-columns) | A value that appears in no choice list, for example a `funding_stage` of `Series C` without the `+`, an `employee_count_range` of `50-100`, or a `title` of `Founding Engineer` | The value becomes `Other` when the target list defines an `Other` member and is left empty when it does not; either way `IngestionLogger` records the value and names the outcome. The row otherwise loads and transforms normally. |
| 4. Reject records missing mandatory fields rather than inserting partial records | All six files: the three `crunchbase_*_sample.csv` files and the three `linkedin_*_sample.csv` files. Each file carries one row per mandatory column of its record type, so `crunchbase_investors_sample.csv`, whose only mandatory column is `name`, carries one row and each of the other five files carries two | A blank in a column marked mandatory for that record type: `name`, `headquarters_location` or `active` on startups, `name` on investors, `startup_name` or `round_date` on funding rounds, `name` or `startup_name` on founders and executives, `startup_name` or `title` on job postings | `import_state` becomes `rejected`, `error_message` names **every** missing mandatory column on that row, and **no** entity record is created. |

Rule 2's duplicate pair differs on `website` on purpose: the pair is the fixture that distinguishes a deduplication keyed on name plus headquarters location, which is what prompt section 4.0 specifies, from one keyed on name plus website, which would not catch this pair.

### Per-file defect map

Which fixture sits in which file, so a count can be reconciled file by file.

| File | Rule 1 whitespace | Rule 2 duplicate pair | Rule 3 unmatched `funding_stage` or `round_type` | Rule 4 blank mandatory |
| --- | --- | --- | --- | --- |
| `crunchbase_startups_sample.csv` | Three rows | One pair | Three values across two rows: one row carries an unmatched `industry` **and** an unmatched `funding_stage`, a second row an unmatched `employee_count_range` | Three rows covering all three mandatory columns: `Jamaica Plain Sensorworks` blanks both `headquarters_location` and `active`, one row blanks `name`, and `Charles River Telemetry` blanks `active` on its own |
| `crunchbase_investors_sample.csv` | Two rows | Not applicable | Two rows: one unmatched `type`, one unmatched `focus_areas` member | One row |
| `crunchbase_funding_rounds_sample.csv` | Two rows | Not applicable | One row: an unmatched `round_type` | Two rows: one blank `startup_name`, one blank `round_date` |
| `linkedin_founders_sample.csv` | Two rows | Not applicable | One row: an unmatched `title` | Two rows: one blank `name`, one blank `startup_name` |
| `linkedin_executives_sample.csv` | Two rows | Not applicable | One row: an unmatched `title` | Two rows: one blank `name`, one blank `startup_name` |
| `linkedin_job_postings_sample.csv` | Two rows | Not applicable | Three rows: one unmatched `department`, one unmatched `remote_type`, one unmatched `seniority` | Two rows: one blank `startup_name`, one blank `title` |

The shape of that map follows from the rules themselves. Rule 2 deduplicates Startup records, so only the startups file carries a rule 2 fixture. Rule 3 covers every choice-backed column: all six files carry at least one rule 3 fixture, and the fixtures between them cover both halves of the unmatched-value policy. Rule 4 covers every mandatory column of every record type: `crunchbase_investors_sample.csv` has one mandatory column and carries one fixture row; `crunchbase_startups_sample.csv` has three mandatory columns and carries three fixture rows; and each of the remaining four files has two mandatory columns and carries two fixture rows. Two of the startups fixtures are worth separating, because they exercise `active` differently: `Jamaica Plain Sensorworks` blanks `headquarters_location` **and** `active` on the same row, so `error_message` names both, which is the rule 4 outcome for a row missing more than one mandatory value; `Charles River Telemetry` blanks only `active`, which is the narrower case that proves `active` is rejected on its own rather than being quietly defaulted. Of the sixty-five rows loaded, thirteen are not accepted: twelve are rejected for a blank mandatory value and one is rejected as an in-batch duplicate. Fifty-two are accepted.

### Unmatched values in choice columns

Eleven values across ten rows match no member of their target choice list. All eleven are rule 3 fixtures, and the outcome depends on one thing only: whether the target list defines an `Other` member. Two of the eleven sit on one row — data row 8 of `crunchbase_startups_sample.csv` carries an unmatched `industry` and an unmatched `funding_stage` — which is why ten rows carry eleven values.

| File | Data row | Value carried | Column | Target choice list | Has `Other` | Outcome |
| --- | --- | --- | --- | --- | --- | --- |
| `crunchbase_startups_sample.csv` | 8 | `Cleantech` | `industry` | `Startup.industry` | Yes | Stored as `Other` and logged. |
| `crunchbase_startups_sample.csv` | 8 | `Series C` | `funding_stage` | `Startup.funding_stage` | No | Logged; the field is left empty on the entity record. |
| `crunchbase_startups_sample.csv` | 10 | `50-100` | `employee_count_range` | `Startup.employee_count_range` | No | Logged; the field is left empty on the entity record. |
| `crunchbase_investors_sample.csv` | 6 | `Cleantech` | `focus_areas` | `Investor.focus_areas` | Yes | The member becomes `Other` and is logged. The row's remaining member `Fintech` is unaffected, so the stored list is `Fintech,Other`. |
| `crunchbase_investors_sample.csv` | 7 | `Family Office` | `type` | `Investor.type` | No | Logged; the field is left empty on the entity record. |
| `crunchbase_funding_rounds_sample.csv` | 8 | `Series C` | `round_type` | `FundingRound.round_type` | No | Logged; the field is left empty on the entity record. |
| `linkedin_founders_sample.csv` | 8 | `Founding Engineer` | `title` | `Founder.title` | Yes | Stored as `Other` and logged. |
| `linkedin_executives_sample.csv` | 8 | `Chief Revenue Officer` | `title` | `Executive.title` | Yes | Stored as `Other` and logged. |
| `linkedin_job_postings_sample.csv` | 10 | `Customer Success` | `department` | `JobPosting.department` | Yes | Stored as `Other` and logged. |
| `linkedin_job_postings_sample.csv` | 11 | `Flexible` | `remote_type` | `JobPosting.remote_type` | No | Logged; the field is left empty on the entity record. |
| `linkedin_job_postings_sample.csv` | 12 | `Principal` | `seniority` | `JobPosting.seniority` | No | Logged; the field is left empty on the entity record. |

Every file carries at least one of these fixtures, and the eleven between them cover both halves of the policy: five values coerce to `Other` and six are logged and left empty.

`Series C` appears twice on purpose, once on a startup and once on a funding round, because `Startup.funding_stage` and `FundingRound.round_type` share the same eight values and both must behave identically. `Cleantech` likewise appears twice, once as a `Startup.industry` value and once as a member of `Investor.focus_areas`, because `focus_areas` reuses the six `Startup.industry` values and both must behave identically — the difference being that `focus_areas` normalises member by member, so only the unmatched member becomes `Other`.

`Investor.type` is the one column in this dataset whose unmatched value is neither coerced nor part of a list: the list is `VC`, `Angel`, `PE`, `Corporate`, `Accelerator` with no `Other` member, so `Family Office` on data row 7 is logged and `type` is left empty. Data row 7 is `Menotomy Capital Group`, the one investor no funding round references, so the row is otherwise unencumbered and its outcome is observable in isolation.

A list with no `Other` member offers no value to normalise to, so the unmatched value is logged and the field left empty rather than coerced into a value the dictionary does not define. **Do not add an `Other` choice to any of these lists**: prompt section 1.0 declares the field and choice definitions binding and complete. Each of the ten rows is otherwise valid and transforms normally — an emptied choice column is not a rejection, and the record is still created.

### Non-resolving references

Every `startup_name` value, and every `lead_investor_name` and `participating_investor_names` value, in every child file resolves to a record present in `crunchbase_startups_sample.csv` or `crunchbase_investors_sample.csv`, with one class of exception.

The exception is the rule 4 fixtures. A row authored to be rejected for a blank mandatory field is the **only** kind of row whose natural-key reference may fail to resolve, and in those rows the failure is the blank itself: a blank `startup_name` on a founder, executive, funding round or job posting row cannot resolve to a Startup, which is precisely the condition rule 4 rejects. Recognise them by the blank column. Each child file carries exactly one such row, the fixture whose `startup_name` is blank; that file's other rule 4 fixture blanks a different mandatory column — `round_date` on funding rounds, `name` on founders and executives, `title` on job postings — and its `startup_name` still resolves. A non-resolving reference in any row that is **not** a rule 4 fixture is a mistake, not a designed defect, and should be reported.

The three rejected startup rows create no Startup record, so no child row may reference them. Two of the three carry a blank `startup_name` or a blank `headquarters_location` and so have no usable name; the third names `Charles River Telemetry`, and **no row in any child file references that name**.

## Data Import Wizard procedure

This section is a complete, self-contained load procedure: the prerequisites, the load order, the wizard steps and the post-load verification below are sufficient to stage all six files without reading another document. The transform map and its field-by-field script are a separate, larger artifact and are to be specified in [`../docs/manual-build/06-staging-table-csv-import.md` (planned)](../docs/manual-build/06-staging-table-csv-import.md).

### Prerequisites

- The Update Set has been committed to the target instance, so `x_bst_startuptrk_ingest_staging` exists. The commit sequence is to be specified in [`../docs/deployment-runbook.md` (planned)](../docs/deployment-runbook.md); the post-commit gates that confirm the tables exist are in [`../docs/validation-gates.md`](../docs/validation-gates.md), which is present today.
- The operator holds the `x_bst_startuptrk.admin` role. The staging table grants **read, write, create and delete to that role alone**, so this procedure cannot be performed by a caller holding only `x_bst_startuptrk.user` or `x_bst_startuptrk.premium_user`. Creating the import set table and the transform map additionally requires the platform `admin` role.

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
7. Run the transform. Its map and script are to be specified in [`../docs/manual-build/06-staging-table-csv-import.md` (planned)](../docs/manual-build/06-staging-table-csv-import.md); the behaviour it must implement is the four cleaning rules stated above, applied through `IngestionMapper`.

### Verification after each load

Check all four of the following on the staged rows before running the transform. The staged rows are reachable through the **Ingestion staging** module of the Boston Startup Tracker application menu.

**Verify in the list view, not over the Table API.** The staging table ships with `ws_access` false, so `GET /api/now/table/x_bst_startuptrk_ingest_staging` does not serve it and a script written against that path will fail whether or not the rows loaded. The application menu module and the platform list view are the supported route; the reason for the posture is in [`../docs/data-model.md`](../docs/data-model.md).

- The row count matches the count stated for that file.
- Every row shows `import_state` of `pending`.
- Every row shows `run_provenance` of `fallback`.
- Every row has an empty `error_message`.

After the transform, `import_state` is `processed` on the fifty-two accepted rows and `rejected` on the thirteen that are not accepted — the twelve rule 4 fixtures plus the one rule 2 duplicate — and `error_message` names the reason on each rejected row: for example `missing mandatory active` on `Charles River Telemetry`, whose `active` is blank, and `duplicate startup in the same batch` on the second member of the duplicate pair.

### Forcing the fallback path

Set the property `x_bst_startuptrk.ingestion.source_mode` to `fallback` to make both ingestion flows read this dataset instead of attempting a live call, which is how a flow test is made deterministic without touching credentials. Set it back to `live` afterwards. A run left on `live` also reads this dataset whenever the live call fails; the difference is that forcing `fallback` skips the live attempt altogether. The flow-side steps are to be specified in [`../docs/manual-build/02-flow-crunchbase-ingestion.md` (planned)](../docs/manual-build/02-flow-crunchbase-ingestion.md) and [`../docs/manual-build/03-flow-linkedin-ingestion.md` (planned)](../docs/manual-build/03-flow-linkedin-ingestion.md).

## Retention of the loaded rows

**The 65 rows this dataset loads are not permanent, and no manual clean-up step is required.** The staging table holds verbatim upstream payloads in `raw_payload` and unvalidated person data in `name`, `title`, `bio`, `linkedin_url` and `contact_email`, so its contents are bounded automatically by two administrator-controlled properties and one scheduled job. The full policy is in [`../docs/data-model.md`](../docs/data-model.md); what an operator of this dataset needs to know is here.

| Property | Shipped value | Clamped to | What it bounds |
| --- | --- | --- | --- |
| `x_bst_startuptrk.privacy.staging_minimise_hours` | `24` | 1 to 8760 | How long after a row **settles** its payload and person columns survive |
| `x_bst_startuptrk.privacy.staging_retention_days` | `30` | 1 to 365 | How long after a row is **created** the row itself survives |

Both are readable and writable by `x_bst_startuptrk.admin` alone, and `AppProperties` clamps them, so neither can be set to a value that disables the policy or extends retention indefinitely.

The scheduled job **Prune ingestion staging rows** runs daily and applies two sweeps through `PrivacyRetentionService.runRetention()`:

1. **Minimisation.** A row whose `import_state` is `processed`, `rejected` or `error`, and which was last updated more than `staging_minimise_hours` ago, has eleven columns cleared: `raw_payload`, `name`, `title`, `bio`, `linkedin_url`, `contact_email`, `description`, `website`, `logo_url`, `url` and `source_url`. `import_state`, `import_run` and `error_message` are kept, so the row remains evidence of what was seen and how it settled. A row still `pending` is never touched.
2. **Deletion.** A row created more than `staging_retention_days` ago is deleted outright, whatever its state.

Three consequences matter to anyone using this dataset:

- **Reload before re-testing after a day.** With the shipped values, a settled row's payload and person columns are gone about 24 hours after the run that consumed it, and the row itself about 30 days after it was loaded. A fallback flow test run against a minimised row will reject it under cleaning rule 4 for missing mandatory fields — which is correct behaviour, not a defect. Re-run the import from the CSVs in this folder before repeating a flow test.
- **The designed defects are reproducible from the CSVs, not from the table.** The rejection, deduplication and unmatched-value cases documented above live in the CSV files, which are version-controlled and never modified by the job. The table is a working copy.
- **An erasure request is serviced without waiting for retention.** `PrivacyRetentionService.eraseSubject()` deletes matching staging rows immediately, whatever their state or age, alongside clearing the contact address on the matching Founder and Executive records and deleting the caller's rate-limit counter rows. The procedure is in [`../docs/data-model.md`](../docs/data-model.md).

Because the sample values are synthetic, nothing in this folder is subject to an erasure request in practice. The policy exists for the live path, which loads the same table from the same shape of data.

## Run provenance and criterion 4 evidence

Every row shipped in this folder carries `run_provenance` of `fallback`. A flow run that reads this dataset records the same provenance for the run as a whole: `IngestionLogger.writeRunSummary` sets the property `x_bst_startuptrk.ingestion.last_run_provenance` to `fallback` and writes a run summary to the application log — through `gs.info`, prefixed `[x_bst_startuptrk.ingestion]` — carrying the run identifier, the provenance, and the processed, rejected and skipped counts. A run that completed a live call records `live` by the same path.

Prompt section 10.0 criterion 4 accepts the sample-dataset substitute for live ingestion, so three consecutive clean fallback runs of each flow satisfy it **provided the mode is recorded** for each run. The recording is itself part of the acceptance evidence: an Automated Test Framework result that exercised this dataset must be labelled **"fallback validated"**, and only a result from a successful live call may be labelled **"live validated"**, so the two can never be confused after the fact. **A result may carry the "live validated" label only when both credential aliases are provisioned and the run completed a live call**; otherwise the label is "fallback validated". The labelling convention is to be applied by [`../docs/manual-build/05-atf-test-suites.md` (planned)](../docs/manual-build/05-atf-test-suites.md) and the evidence collected by [`../docs/validation-checklist.md` (planned)](../docs/validation-checklist.md).

For criterion 4 purposes a **scheduled run** means a flow execution that passed the flow's cadence guard and went on to do work. An execution that started, found the configured cadence had not yet elapsed and exited without ingesting is a no-op and does not count towards the three consecutive runs. That definition is stated here; how to distinguish the two in the execution log is to be specified in [`../docs/deployment-runbook.md` (planned)](../docs/deployment-runbook.md).

## The three-way contract

Three artifacts describe the same set of staging columns, and all three must be changed together. Changing one alone breaks the fallback path without raising an error: the wizard leaves the renamed column unmapped, the field loads empty, and the transform produces incomplete records or rejects valid ones.

| Leg | Artifact | Role | Present today |
| --- | --- | --- | --- |
| a | The header rows of the six CSVs in this folder, documented above | The wire format | Yes |
| b | The `x_bst_startuptrk_ingest_staging` dictionary records in [`../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml`](../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml) | **Authoritative** | Yes |
| c | The field mapping in [`../docs/manual-build/06-staging-table-csv-import.md` (planned)](../docs/manual-build/06-staging-table-csv-import.md) | The load instructions | No |

Leg b is authoritative over the other two legs, and the frozen prompt and the Agent Action Plan are authoritative over all three. Where this document and the dictionary disagree about a column name, type, length or choice value, the dictionary is checked against the prompt and the plan first. Where the dictionary matches the specification, this document is corrected to it. Where the dictionary departs from it, the dictionary is corrected.

Two columns are load-bearing across all three legs:

- The five shared columns `name`, `website`, `active`, `title` and `startup_name` are each one staging column read by more than one record type, so the wizard maps them once per file according to that file's record type. `name` is the record's own name on a `startup`, `investor`, `founder` or `executive` row; `startup_name` is the parent's name on a `founder`, `executive`, `funding_round` or `job_posting` row. Mapping a child file's `startup_name` to `name`, or the reverse, silently detaches every child row from its parent.
- `participating_investor_names` carries a comma separated list. The wizard must load it verbatim into the string column; nothing may re-format, re-quote or re-delimit it in transit. The transform splits it on the comma and trims each member.

Leg c must be authored against legs a and b as they stand, and must honour one property of leg b in particular: `active` is a **String** column of length 10 carrying the text `true` or `false`, not a True/False column, and it carries no dictionary default. That is what lets a blank `active` survive the load and be rejected by cleaning rule 4 rather than being silently defaulted to `true`.

## Related documents

Delivered with this package:

- [`../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml`](../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml) — the authoritative staging dictionary and the `IngestionMapper` and `IngestionLogger` records this contract depends on
- [`../docs/data-model.md`](../docs/data-model.md) — all ten tables field by field, the table access posture, and the staging retention, minimisation and data-subject erasure lifecycle
- [`../docs/access-control.md`](../docs/access-control.md) — the three roles, the premium field ACL matrix, and the twelve supporting-table controls that make the staging table administrator-only on all four operations
- [`../docs/api-reference.md`](../docs/api-reference.md) — the six REST resources and the thirteen system properties, including `ingestion.source_mode` and `ingestion.last_run_provenance`
- [`../docs/validation-gates.md`](../docs/validation-gates.md) — the post-commit gates that confirm the staging table's parent tables exist

Planned artifacts of this package:

- [`../README.md` (planned)](../README.md) — package index for the ServiceNow deliverable
- [`../docs/manual-build/06-staging-table-csv-import.md` (planned)](../docs/manual-build/06-staging-table-csv-import.md) — the detailed import and transform guide
- [`../docs/manual-build/01-connection-credential-aliases.md` (planned)](../docs/manual-build/01-connection-credential-aliases.md) — the two credential aliases the live path uses
- [`../docs/manual-build/02-flow-crunchbase-ingestion.md` (planned)](../docs/manual-build/02-flow-crunchbase-ingestion.md) — the Crunchbase ingestion flow
- [`../docs/manual-build/03-flow-linkedin-ingestion.md` (planned)](../docs/manual-build/03-flow-linkedin-ingestion.md) — the LinkedIn ingestion flow
- [`../docs/manual-build/05-atf-test-suites.md` (planned)](../docs/manual-build/05-atf-test-suites.md) — the test suites, including the provenance labelling
- [`../docs/validation-checklist.md` (planned)](../docs/validation-checklist.md) — the success criteria and their evidence
- [`../docs/gaps-and-flags.md` (planned)](../docs/gaps-and-flags.md) — requirements with no clean platform equivalent
- [`../docs/deployment-runbook.md` (planned)](../docs/deployment-runbook.md) — import sequence, gates and rollback
- [`../../docs/decisions/DECISION_LOG.md` (planned)](../../docs/decisions/DECISION_LOG.md) — the single source of truth for every decision, alternative and risk behind this contract

