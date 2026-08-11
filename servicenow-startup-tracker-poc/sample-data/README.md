# Sample Data — Fallback Dataset

This folder holds the fallback dataset required by prompt section 4.0. Its six CSV files load into the single staging table `x_bst_startuptrk_ingest_staging` in the scoped application `x_bst_startuptrk`, and they stand in for a live Crunchbase or LinkedIn API response when live authentication fails, times out, returns a malformed response, or while credentials are being re-issued.

The dataset is **fallback only** by design. An ingestion run attempts the live call first and reads the staging table only when that attempt **fails**, or when the property `x_bst_startuptrk.ingestion.source_mode` is set to `fallback` to make a test deterministic.

**A live call that succeeds and returns no rows is not a failure, and it does not fall back to this dataset.** The two conditions are decided independently and must not be conflated:

| Condition the flow evaluates | What it means | Does it fall back? |
| --- | --- | --- |
| The transport completed and the envelope parsed — the flow's `envelope_ok` | The provider answered, and the body was the shape the flow expected | **No**, whatever the row count |
| Rows were returned — the flow's `row_count` | The provider's answer contained data | Irrelevant on its own |
| `envelope_ok` false — an authentication failure, a timeout, a non-`2xx` status, a body that did not parse, a missing envelope member, or a budget that truncated the read | The provider's answer cannot be trusted | **Yes** |
| `source_mode` is `fallback` | The operator forced determinism | **Yes**, and the live call is not attempted at all |

So a live run that legitimately finds nothing new records **zero rows ingested with provenance `live`** and leaves this dataset untouched. Treating a valid empty response as a failure would silently relabel a clean live run as a fallback run and would re-stage sixty-five CSV rows over live data. The predicate is specified in [`../docs/manual-build/02-flow-crunchbase-ingestion.md`](../docs/manual-build/02-flow-crunchbase-ingestion.md) and [`../docs/manual-build/03-flow-linkedin-ingestion.md`](../docs/manual-build/03-flow-linkedin-ingestion.md).

## Prerequisites for live ingestion

The live path depends on two Connection and Credential Aliases, `x_bst_startuptrk.crunchbase_api` (Basic Auth) and `x_bst_startuptrk.linkedin_oauth` (OAuth 2.0), which the ingestion flows reference by name. Each alias resolves through two record classes, and only one of them is built by hand here: [`../docs/manual-build/01-connection-credential-aliases.md`](../docs/manual-build/01-connection-credential-aliases.md) **builds the two alias records and the two connection records**, which hold no secret, and **confirms but never creates** the credential records behind them.

**No live call can succeed until the credential owner has provisioned the credential material** — the Crunchbase API key, and the LinkedIn OAuth 2.0 client identifier, client secret and refresh token — bound it to the alias record, and passed the connection test. **On the target instance as observed, neither credential is provisioned**, so both aliases sit on that guide's **Path B**: four definition records delivered, two credential sets outstanding as tracked pending items. A pending credential is never counted as a delivered artifact.

While either alias is unprovisioned, **every ingestion run reads this dataset and every result must be labelled "fallback validated"**, never "live validated". Prompt section 10.0 criterion 4 accepts the sample-dataset substitute, so that condition does not block acceptance; it only constrains what the evidence may claim.

No credential material appears in this folder, in the Update Set, or in any flow input or script step. The two non-secret API base URLs are the properties `x_bst_startuptrk.crunchbase.base_url` and `x_bst_startuptrk.linkedin.base_url`.

## Referenced documents

This document is self-contained: the column contract, the value conventions, the designed-defect inventory and the load procedure are all stated here in full, and nothing in them requires reading another file.

**Every document named in this specification is delivered and readable.** Each link resolves to a file in this package — the six CSVs beside this one, the Update Set XML, and `../docs/data-model.md`, `../docs/access-control.md`, `../docs/api-reference.md`, `../docs/validation-gates.md` and the remaining package documents — so a reader can follow any link and read the content the statement around it describes; no link is a forward reference to something still to be written.

This document carries no rationale. Every decision behind the contract, every alternative considered and every risk is recorded in [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md).

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

The dialect is specified here in full. All six files conform to it.

- **Format** — RFC 4180.
- **Field delimiter** — a comma (`,`).
- **Quoting character** — the double quote (`"`).
- **Escaping** — a literal double quote inside a quoted field is escaped by doubling it (`""`).
- **When to quote** — a field is quoted where it contains a comma, a double quote or a line break, and where it carries a **designed leading or trailing space** that must survive the round trip. Every other field is unquoted. **Fourteen fields across the six files carry designed whitespace and all fourteen are quoted**: the twelve listed in [Designed whitespace is always quoted](#designed-whitespace-is-always-quoted) plus two `headquarters_location` values that would be quoted for their comma in any case. An unquoted leading space is stripped by many CSV readers, so quoting is what makes a rule 1 fixture test the trim rule rather than the reader.
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
| `import_run` | String, 64 | See the per-file values below | The batch token: a stable synthetic identifier shared by every row of a single file, so one load is traceable end to end. **An ingestion run overwrites it with its own run lease** — the reserved prefix `run:` followed by the run identifier — for every row it claims, and the lease stays on the row after it settles, naming the run that consumed it. The mechanism is specified under [The `import_run` run lease](../docs/data-model.md#the-import_run-run-lease). |
| `import_state` | String, 40, choice list, dictionary default `pending` | `pending`, `processed`, `rejected`, `error` — **four** members | Processing state of the staged row. Every shipped row carries `pending`; the transform advances it. |
| `run_provenance` | String, 40, choice list | `live` or `fallback` | Whether the row was consumed by a live or a fallback run. Every shipped row carries `fallback`. |
| `error_message` | String, 1000 | Empty on every shipped row | The settled row's outcome, written as exactly two controlled tokens — `code=<code>` naming one member of `IngestionMapper.STATE_CODES`, and `ref=<kind>:<token>` naming the opaque row reference that correlates the row with the run log line carrying the detail. `IngestionMapper.writeStagingState()` is what writes it, together with the matching `import_state`; a flow's terminal-state sweep writes the same two tokens with `code=run_abandoned` when a run ended before settling a row it had claimed. Neither upstream text nor exception text is ever persisted here. |
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
| `startup_name` | `founder`, `executive`, `funding_round`, `job_posting` | The first half of the natural key naming the **parent** Startup |
| `startup_headquarters_location` | `founder`, `executive`, `funding_round`, `job_posting` | The second half of that key: the parent Startup's headquarters location |
| `headquarters_location` | `startup` | The Startup's own headquarters location |

`headquarters_location` is a `startup`-row column only: it is the row's own location. A child row states its **parent's** location in `startup_headquarters_location`, which is a different column precisely so the two can never be confused.

The column names below are the dictionary element names exactly as the Update Set declares them, and the target field named in each table is the prompt section 1.0 field the transform writes.

### The `_name` natural-key convention

A CSV cannot carry a `sys_id` for a record that does not exist yet, so every reference travels as the target record's natural key — its `name` value — and the transform resolves it at load time. No column carries a `sys_id`. Four columns are natural keys: `startup_name` together with `startup_headquarters_location` resolves to a `x_bst_startuptrk_startup` record, and `lead_investor_name` and `participating_investor_names` resolve to `x_bst_startuptrk_investor` records. The transform's resolution steps are specified in [`../docs/manual-build/06-staging-table-csv-import.md`](../docs/manual-build/06-staging-table-csv-import.md); the resolution `IngestionMapper` performs is described under [Parent resolution uses the full Startup key](#parent-resolution-uses-the-full-startup-key).

`startup_name` and `startup_headquarters_location` appear only on the four child record types, where together they name the parent Startup. A `startup` row carries its own name in `name` and its own location in `headquarters_location`, and an `investor` row carries its own name in `name`.

#### Parent resolution uses the full Startup key

**A Startup's identity is `name` plus `headquarters_location`, so a child row states both.** `IngestionMapper.resolveStartupKey()` reads `startup_headquarters_location` alongside `startup_name` and resolves the parent on the same key cleaning rule 2 de-duplicates on, trimming and lowering both sides of both halves. That is what lets two genuinely different companies share a name — which the de-duplication rule explicitly permits when their locations differ — without a child row of one attaching to the other.

**Both halves are required, and there is no name-only path.** A child row that leaves `startup_headquarters_location` blank does not identify a parent: `resolveStartupKey()` reports it unresolved with the reason `the row carries no parent headquarters location, and the startup key is the name together with the headquarters location`, and the row is rejected rather than attached to a record that merely shares a name. Resolution is deterministic in every case, and never approximate:

| Row carries | Startups matching | Outcome |
| --- | --- | --- |
| Both halves of the key | Exactly one carrying that name and location | Resolved. `{ ok: true, sys_id: <that record>, matches: 1 }`. |
| Both halves of the key | None carrying that pair | Unresolved, reason `no startup carries the name and headquarters location`. The row is rejected and logged as a skip; no entity record is created. |
| Both halves of the key | More than one carrying that pair | Unresolved, `matches` reporting how many, reason `the name and headquarters location already match <n> startup records`. **No candidate is chosen.** This cannot arise from a de-duplicated load, because rule 2 admits one record per pair. |
| `startup_name` only, `startup_headquarters_location` blank | Not attempted | Unresolved, reason `the row carries no parent headquarters location, and the startup key is the name together with the headquarters location`. No query is issued and no candidate is chosen, however many startups carry the name. The row is rejected and logged as a skip. |
| `startup_name` blank | Not attempted | Reason `the value is blank`, though cleaning rule 4 has already rejected the row for a missing mandatory `startup`, so this is the rule 4 outcome rather than a resolution failure. |

`startup_headquarters_location` is **never written to the child record**. It is a transport value that resolves the parent reference and is then discarded, exactly as `startup_name` is.

`resolveStartupKey()`, `resolveInvestor()`, `findExistingStartup()`, `findExistingInvestor()` and the generic `findExistingByKey()` all answer the same object — `{ ok, sys_id, matches, reason }` — rather than a bare identifier or an empty string. A caller cannot therefore mistake "no match" for "one match that happens to be empty", and the reason is what the skip log reports, so a rejected row always names which of the two failure modes it hit. `resolveInvestor()` reports `no investor carries the name` and `the name is ambiguous across <n> investors` on the same policy.

**A natural key is never read as a record identifier.** These columns carry names, and only names. A value that happens to be 32 hexadecimal characters is still matched against the `name` column, so it resolves only if a record is genuinely named that, and otherwise reports `no startup carries the name and headquarters location` like any other unmatched value. No column in these files may carry a `sys_id`, and supplying one is a data error the transform reports rather than a shortcut it honours.

Two references are optional rather than mandatory, so an unresolved value there does not reject the row:

- `lead_investor_name`, on a `funding_round` row. An unresolved value is logged as a warning naming the reason, and the reference is **left unwritten** — the funding round is still created, without a lead investor. It is not written as a blank, because an ingestion run never clears a stored value.
- Each member of `participating_investor_names`. An unresolved member is logged as a warning naming the reason and contributes no join row; the members that do resolve still become join rows.

Cleaning rule 2 de-duplicates Startup records on `name` **plus** `headquarters_location`, so a Startup's identity within the startups file is that pair. A resolved parent is consequently the single record that survived that de-duplication, and a child row reaches it by stating that same pair.

Both sides are trimmed and lowered before comparison, so a child row may spell `startup_name` in any case and with any surrounding whitespace. Several rows in these files deliberately do: `linkedin_founders_sample.csv` carries `"Copley Grid Systems "` with a trailing space, `linkedin_executives_sample.csv` carries `"Seaport Ledger "`, `linkedin_job_postings_sample.csv` carries `"Kendall Cognition "`, and `crunchbase_funding_rounds_sample.csv` carries `" Muddy River Diagnostics"` with a leading space. Each resolves, which is what makes those rows evidence that trimming happens **before** natural-key resolution.

`startup_headquarters_location` is compared the same way, and one row deliberately exercises it: `linkedin_founders_sample.csv` states `seaport, boston, ma` in lower case against a Startup stored as `Seaport, Boston, MA`, and it still resolves.

**Both halves are required, and there is no name-only path.** A child row that leaves `startup_headquarters_location` blank does not identify a parent, and `resolveStartupKey()` rejects it before reading anything, with the reason `the row carries no parent headquarters location, and the startup key is the name together with the headquarters location`. Five rows across the four child files do leave the column blank, but **none of them isolates that rejection**: each also leaves a mandatory column blank — `startup_name` on four of them and `name` on the Kendall Cognition executive — so cleaning rule 4 rejects them first and the recorded reason names the missing mandatory column instead. The blank-second-half rejection is therefore asserted against the mapper in the ingestion suites rather than observed from this load, and the reconciliation counts below are unaffected by it.

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

`active` is a String column of length 10 on staging, carrying the text `true` or `false`, and it declares no dictionary default. A blank field therefore reaches the transform as a blank and cleaning rule 4 observes the absent mandatory value; the **Trim and validate startup** business rule likewise aborts an insert or update whose `active` is empty. `x_bst_startuptrk_startup.active` keeps its own dictionary default of `true`, which applies to a Startup inserted without the field set. Per prompt section 4.0 a record missing a mandatory value is rejected, not filled. The column-type decision and the alternative considered are recorded in [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md).

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

`source_system` is `crunchbase` and `record_type` is `funding_round` on every row. Sixteen columns.

```text
source_system,record_type,import_run,import_state,run_provenance,error_message,raw_payload,startup_name,startup_headquarters_location,round_type,amount_usd,valuation_usd,round_date,lead_investor_name,participating_investor_names,source_url
```

| Column | Platform type | Mandatory | Choice values or format |
| --- | --- | --- | --- |
| `startup_name` | String, 100; first half of the natural key to `x_bst_startuptrk_startup` | Yes | An existing Startup `name`, matched case-insensitively after trimming. Resolves to the `FundingRound.startup` reference and is not written to the child record. |
| `startup_headquarters_location` | String, 100; second half of the natural key to `x_bst_startuptrk_startup` | Yes | The parent Startup's `headquarters_location`, matched case-insensitively after trimming. Completes the `name` plus `headquarters_location` key the parent is resolved by. Left blank, the row does not identify a parent and is rejected — there is no name-only path. Never written to the child record. |
| `round_type` | String, 40 on staging; Choice on `FundingRound.round_type` | No | `Pre-Seed`, `Seed`, `Series A`, `Series B`, `Series C+`, `Growth`, `Public`, `Acquired` |
| `amount_usd` | Decimal on staging; Currency on `FundingRound.amount_usd` | No | Plain USD amount. Premium-gated. |
| `valuation_usd` | Decimal on staging; Currency on `FundingRound.valuation_usd` | No | Plain USD amount. Premium-gated. |
| `round_date` | Date (`glide_date`) | Yes | `YYYY-MM-DD`. |
| `lead_investor_name` | String, 100; natural key to `x_bst_startuptrk_investor` | No | An existing Investor `name`. Writes the `FundingRound.lead_investor` reference. |
| `participating_investor_names` | String, 1000; multi-valued natural keys to `x_bst_startuptrk_investor` | No | **A JSON array** of Investor `name` values inside one double-quoted field, for example `"[""Emerald Necklace Angels"", ""Chickatawbut Seed Partners""]"` before CSV quoting is applied. `IngestionMapper.resolveParticipants()` accepts a real array, a JSON array string, or a `\|` delimited string; **it never splits on a comma**, so a name containing one survives intact. It trims each member, drops an empty member, resolves each remaining member to exactly one Investor and keeps a repeated member once. An empty field means no participants. |
| `source_url` | String, 255 | No | Absolute URL. Writes `FundingRound.source_url`. |

`lead_investor_name` and `participating_investor_names` are distinct columns with distinct destinations. The lead investor is a first-class reference field on the funding round. Each participating investor becomes one row in the join table `x_bst_startuptrk_m2m_round_investor`, which is the **only** table the transform writes for participation. An investor may appear in both columns on the same row.

The join table is authoritative. Two surfaces are derived from it and neither is a second place to write: the read-only `FundingRound.participating_investors` column, a **calculated, virtual** list of investor references whose value is derived from the join table on every read, and the REST `participating_investors` array, which the API assembles from the join table directly. The transform must therefore create join rows and must **not** attempt to write `FundingRound.participating_investors`; the column is read-only and virtual, so there is no stored value for a write to occupy, and `IngestionMapper` cannot reach it in any case because the column is absent from the record type's target-field allowlist. The column renders 121 investors — the declared 4000-character length divided by the 33 characters each member costs — and a round linking more is rendered cut at a whole identifier with the overflow logged at `warn`, while a value that exceeds the declared length even so is rendered empty at `error` rather than part way through an identifier; the join table remains the complete record in every case. The largest round in this dataset links five investors, so no shipped row approaches the bound.

**`IngestionMapper.linkParticipants(runId, roundId, investorIds, participation)` is the method the ingestion path uses, and it reconciles rather than appends.** For each accepted funding round it makes the stored join rows equal the incoming set: rows the incoming set names and the round lacks are inserted, rows present on both sides are left untouched, and rows the incoming set no longer names are **deleted** — but only when the incoming set is complete, meaning the row supplied a value and every member of it resolved to exactly one investor. Where a member did not resolve, the write is additive only and the obsolete rows are kept, because deleting against an incomplete set would discard participation the source still asserts. A failed insert or delete is counted and fails the whole funding-round row, which is stamped `error` rather than `processed`. Re-running a load therefore cannot create a duplicate pair, and a unique composite index on `(funding_round, investor)` enforces that whatever the write path.

`InvestorPortfolioService.linkInvestorToRound(roundId, investorId, suppressRules)` is the single-pair helper on the portfolio service: it returns the existing join row when the pair is already present and inserts one otherwise. It is **the one insert implementation for the join table**, so an administrator linking a pair by hand calls it directly and `linkParticipants()` delegates its own insert step to it with `suppressRules` `true`. What the reconciler adds over it is the *set* semantics — the deletes, the keeps and the single convergence step; the row insert itself is not duplicated. The semantics of both are in [`../docs/data-model.md`](../docs/data-model.md), and the load procedure is [`../docs/manual-build/06-staging-table-csv-import.md`](../docs/manual-build/06-staging-table-csv-import.md).

### `linkedin_founders_sample.csv`

`source_system` is `linkedin` and `record_type` is `founder` on every row. Fourteen columns.

```text
source_system,record_type,import_run,import_state,run_provenance,error_message,raw_payload,name,startup_name,startup_headquarters_location,title,bio,linkedin_url,contact_email
```

| Column | Platform type | Mandatory | Choice values or format |
| --- | --- | --- | --- |
| `name` | String, 100 | Yes | Free text. Writes `Founder.name`. |
| `startup_name` | String, 100; first half of the natural key to `x_bst_startuptrk_startup` | Yes | An existing Startup `name`, matched case-insensitively after trimming. Resolves to the `Founder.startup` reference and is not written to the child record. |
| `startup_headquarters_location` | String, 100; second half of the natural key to `x_bst_startuptrk_startup` | Yes | The parent Startup's `headquarters_location`, matched case-insensitively after trimming. Completes the `name` plus `headquarters_location` key the parent is resolved by. Left blank, the row does not identify a parent and is rejected — there is no name-only path. Never written to the child record. |
| `title` | String, 150 on staging; Choice on `Founder.title` | No | `CEO`, `CTO`, `COO`, `Co-Founder`, `Other` |
| `bio` | String, 2000 | No | Free text. Writes `Founder.bio`. |
| `linkedin_url` | String, 255 | No | Absolute URL. Writes `Founder.linkedin_url`. |
| `contact_email` | String, 100 | No | Email address. Premium-gated. |

### `linkedin_executives_sample.csv`

Identical in shape to `linkedin_founders_sample.csv`, with `record_type` set to `executive` on every row and a different `title` choice list. Fourteen columns.

```text
source_system,record_type,import_run,import_state,run_provenance,error_message,raw_payload,name,startup_name,startup_headquarters_location,title,bio,linkedin_url,contact_email
```

| Column | Platform type | Mandatory | Choice values or format |
| --- | --- | --- | --- |
| `name` | String, 100 | Yes | Free text. Writes `Executive.name`. |
| `startup_name` | String, 100; first half of the natural key to `x_bst_startuptrk_startup` | Yes | An existing Startup `name`, matched case-insensitively after trimming. Resolves to the `Executive.startup` reference and is not written to the child record. |
| `startup_headquarters_location` | String, 100; second half of the natural key to `x_bst_startuptrk_startup` | Yes | The parent Startup's `headquarters_location`, matched case-insensitively after trimming. Completes the `name` plus `headquarters_location` key the parent is resolved by. Left blank, the row does not identify a parent and is rejected — there is no name-only path. Never written to the child record. |
| `title` | String, 150 on staging; Choice on `Executive.title` | No | `CFO`, `VP Engineering`, `VP Sales`, `VP Marketing`, `Head of Product`, `Other` |
| `bio` | String, 2000 | No | Free text. Writes `Executive.bio`. |
| `linkedin_url` | String, 255 | No | Absolute URL. Writes `Executive.linkedin_url`. |
| `contact_email` | String, 100 | No | Email address. Premium-gated. |

### `linkedin_job_postings_sample.csv`

`source_system` is `linkedin` and `record_type` is `job_posting` on every row. Seventeen columns.

```text
source_system,record_type,import_run,import_state,run_provenance,error_message,raw_payload,startup_name,startup_headquarters_location,title,department,location,remote_type,seniority,posted_date,url,active
```

| Column | Platform type | Mandatory | Choice values or format |
| --- | --- | --- | --- |
| `startup_name` | String, 100; first half of the natural key to `x_bst_startuptrk_startup` | Yes | An existing Startup `name`, matched case-insensitively after trimming. Resolves to the `JobPosting.startup` reference and is not written to the child record. |
| `startup_headquarters_location` | String, 100; second half of the natural key to `x_bst_startuptrk_startup` | Yes | The parent Startup's `headquarters_location`, matched case-insensitively after trimming. Completes the `name` plus `headquarters_location` key the parent is resolved by. Left blank, the row does not identify a parent and is rejected — there is no name-only path. Never written to the child record. |
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

All four operations carry an explicit access control rather than relying on the platform's default deny, and the table is sealed to the scope and withheld from the Table API, so there is no path by which a caller holding `x_bst_startuptrk.user` or `x_bst_startuptrk.premium_user` can read a premium value out of a staging row that the entity-level gate would have denied them. **This posture belongs to the three supporting tables, not to the seven entity tables**, which are delivered `public` with `read_access` and `ws_access` true and are governed by their table-level and field-level access controls instead. The supporting-table controls are Layer 4 of [`../docs/access-control.md`](../docs/access-control.md); the posture table by table is under [`../docs/data-model.md`](../docs/data-model.md).

## Value conventions

| Convention | Rule | Example |
| --- | --- | --- |
| Dates | ISO 8601 `YYYY-MM-DD`, zero-padded, no time component, no timezone, no offset. | `2024-03-07` |
| Currency | Plain unformatted United States dollars: digits only with an optional single decimal point. No thousands separator, no currency symbol, no `M` or `K` magnitude suffix. The field names fix the denomination as USD. | `42500000` or `42500000.50` |
| Booleans | Lowercase `true` or `false` only. Never `TRUE`, `True`, `1`, `0`, `yes`, `no`, `Y` or `N`. | `true` |
| Multi-valued choice fields | `focus_areas` is comma separated inside one double-quoted field. A bare comma separates values, with **no** space after it. Each element is spelled exactly as its choice list spells it. A comma is safe here because no choice value contains one. | `"Fintech,SaaS,Deeptech"` |
| Multi-valued natural keys | `participating_investor_names` is a **JSON array**, not a comma separated list, because an investor name may itself contain a comma. Each element is an Investor `name` spelled as that record spells it. An empty field means no participants. This is the one multi-valued column that does **not** share the `focus_areas` convention, and the difference is deliberate: `focus_areas` members come from a closed choice list that contains no comma. | `"[""Emerald Necklace Angels"", ""Chickatawbut Seed Partners""]"` |
| Empty means absent | An empty field means the value is absent. No sentinel string is ever used. On `active` — a String column on staging — a blank therefore reaches the transform as a blank, and cleaning rule 4 rejects a `startup` row for it because `active` is mandatory there. On `institutional_funding_last_5yrs` — a True/False column on staging carrying a dictionary default of `false` — a blank cell is defaulted **by the staging dictionary at import time**, so the transform reads `false` as a value the row supplied rather than as an absence. Every shipped row supplies it explicitly, so no row relies on that. | `,,` |
| Integers | Digits only, unquoted, no separators. | `2019` |
| URLs | Absolute, including the scheme. | `https://example.com/careers` |

These conventions are enforced, and violating one has a defined outcome rather than an approximate one. **A value that does not match its declared type is refused, not repaired**: a currency of `4.2M` or `42,500,000`, a date of `2023-02-30`, and a year of `2019x` are each logged and the field left unwritten, and the row is rejected only where the refused field is mandatory. **A value longer than its target column is rejected, not truncated**: a `name` of 101 characters rejects the row with `name exceeds 100 characters`. Nothing is shortened, because a truncated `name` would silently become a different startup under the rule 2 de-duplication key. Both contracts, with the accepted and refused forms field by field, are stated in [`../docs/data-model.md`](../docs/data-model.md).

### No sentinel values

The strings `Unknown`, `N/A`, `null` and `None` appear nowhere in these files and must not be introduced. Prompt section 4.0 requires a record missing a mandatory field to be **rejected**, not filled, so a blank field must stay blank in order for cleaning rule 4 to see it.

### Absent is not blank, and ingestion never clears a stored value

A source that does not supply a field and a source that supplies an empty value are two different statements, and the transform keeps them apart. `IngestionMapper` reads every field through one accessor that reports whether the source carried the key at all; a key the source did not carry, and a key whose coerced value comes out empty, are both **omitted from the write** rather than written as an empty string.

The consequence is the one that matters on an update, and it is deliberate: **an ingestion run can add and change values, but it can never clear one.** A startup that already stores a `website`, a founder that already stores a `contact_email`, or an investor that already stores an `aum_usd` keeps that value when a later run's payload omits the field — which is the normal case for a partial API response, and for every one of the optional-field differences catalogued under [Live and fallback are not identical in their optional fields](#live-and-fallback-are-not-identical-in-their-optional-fields). Two further paths behave the same way for the same reason: an unmatched value on a choice list with no `Other` member leaves the column unwritten rather than emptying it, and an unresolvable optional reference such as `lead_investor_name` is left unwritten rather than blanked.

Clearing a value is therefore an **explicit administrative act**, not an ingestion side effect. It is performed by a `PUT` to the resource naming the field with an empty value, or on the platform form by an administrator holding `x_bst_startuptrk.admin`. The REST layer draws the same absent-versus-blank distinction from the other side: a field the request body omits is left alone, while a field the body supplies as empty is written as empty. A **mandatory** field cannot be cleared by either route — a `PUT` supplying `name` as empty is refused with `name is required` — so the columns that carry identity are safe from being emptied at all. A blank cell in these files never clears anything, and adding one to request it will not work.

**No delivered mechanism removes data on a timer or on request, and live activation is gated on the operator's own procedure instead.** There is no retention job, no minimisation sweep and no erasure service in this delivery — the frozen inventory permits no second scheduled job and no ninth Script Include — so the obligations are the operator's and are gated by [the live-activation register](../docs/gaps-and-flags.md#the-live-activation-register), which `source_mode` `live` must not precede; a staged row is removed only by an administrator deleting it, and an entity value is cleared only by the explicit administrative act described above. The one path that removes data is therefore the operator clearing staged rows, which is an administrative act rather than a mapping outcome and is described under [The loaded rows persist until a run settles them](#the-loaded-rows-persist-until-a-run-settles-them).

### `raw_payload`

`raw_payload` is a JSON object carried as one double-quoted CSV field with every inner double quote doubled. It uses the **source system's own key vocabulary**, not the flattened platform column names. Prompt section 4.0 requires the staging shape to mimic the expected API response, and this column carries that shape.

- **Crunchbase** payloads follow the **v4 entity contract**: an entity read returns a top-level `properties` object, and a search returns `{ "count", "entities": [ { "uuid", "properties" } ] }`. The three Crunchbase fixtures carry the `properties` form, which is what both shapes reduce to once `IngestionMapper.unwrapLive()` has unwrapped them. Three v4 value shapes recur and are the reason the payloads look nested: a **money** field is `{ "value", "currency", "value_usd" }`, an **identifier** field is `{ "value", "permalink", "uuid", "entity_def_id" }`, and a **date** field is `{ "value", "precision" }`. `IngestionMapper` flattens each to the scalar the column holds, taking `value_usd` first on a money object so every currency column is in United States dollars.
- **LinkedIn** payloads are **declared synthetic**, and each carries `"synthetic": true` as its first member to say so in the data itself. LinkedIn publishes no general-purpose company-people or company-jobs read API: what is reachable is reachable only through an approved product, whose paths, envelope and retention terms are fixed by that product's documentation. No such product is provisioned for this deliverable, so **no LinkedIn response has been captured and none is reproduced here.** These three fixtures carry an `elements` array under the same `data` wrapper the Crunchbase fixtures use, so all six files share one envelope shape and one mapper path. `IngestionMapper.unwrapLive()` accepts the collection at the root of the payload or under `data`, so a product that places `elements` at the root unwraps identically; a product that names its array anything else must be recorded in the contract table of [`../docs/manual-build/03-flow-linkedin-ingestion.md`](../docs/manual-build/03-flow-linkedin-ingestion.md#34--step-outputs) and the flow must hand `unwrapLive()` the sub-object that holds `elements`.

#### Every payload supplies every mandatory value its record type needs

This is a **contract, not a convenience**, and it is what makes these files usable as a live-path fixture rather than only as a fallback dataset. The live path never reads a flattened column: `IngestionMapper.mapLiveRecord()` reads `raw_payload` alone, through `LIVE_ALIASES`. A payload that omits the source key behind a mandatory field therefore produces a row that cleaning rule 4 rejects — the record is skipped, the run continues, and the file silently exercises none of the live path for that record type. Each payload consequently carries the source key every mandatory field resolves through:

| File | Envelope | Source keys supplying the mandatory values | Mandatory fields they satisfy |
| --- | --- | --- | --- |
| `crunchbase_startups_sample.csv` | `properties` | `identifier`, `location_identifiers`, `operating_status` | `name`, `headquarters_location`, `active` |
| `crunchbase_investors_sample.csv` | `properties` | `identifier` | `name` |
| `crunchbase_funding_rounds_sample.csv` | `properties` | `funded_organization_identifier`, `announced_on` | `startup`, `round_date` |
| `linkedin_founders_sample.csv` | `data.elements` | `name`, `companyName`, `companyLocation` | `name`, `startup` |
| `linkedin_executives_sample.csv` | `data.elements` | `name`, `companyName`, `companyLocation` | `name`, `startup` |
| `linkedin_job_postings_sample.csv` | `data.elements` | `companyName`, `companyLocation`, `title` | `startup`, `title` |

`identifier` is a v4 identifier object, and the mapper reads its `value` as the organisation's name. `location_identifiers` is an ordered array of `{ "value", "location_type", "permalink" }` objects, which is the shape a v4 organisation read returns; `IngestionMapper` flattens it to the location string the `headquarters_location` column holds. `funded_organization_identifier` is an identifier object naming the funded company, and the mapper reads its `value` as the parent Startup's natural key.

**Both halves of the parent Startup key are required, so a person or job payload carries `companyLocation` as well as `companyName`.** A Startup's identity is the pair, and `IngestionMapper` resolves the parent on the pair alone — a payload carrying only the company name resolves nothing and the row is rejected for a missing mandatory `startup`. `facet_ids` is carried on every Crunchbase organisation payload for the same class of reason: the source publishes companies, investors, schools and events in one collection, and a payload that declares no facet at all is mapped, but a payload whose facet contradicts the declared record type is refused before any value is read.

Every alias chain named here is declared in `IngestionMapper.LIVE_ALIASES`, which is authoritative.

#### The rule these payloads follow

A payload **carries the source system's own key wherever the source publishes one, and the source's own code as its value.** Where a flattened column carries a value the source publishes no code for, the payload carries the value verbatim rather than a translated one — which is exactly what a mis-spelled or out-of-vocabulary live value looks like, and is how the out-of-list rule 3 fixtures reach the live path. Where a flattened column is blank, the payload publishes no key for it, so the field is absent rather than blank.

**No payload names a key Crunchbase v4 does not publish.** That rule has no exceptions, and it is worth stating because the shipped fixtures once broke it twice. `institutional_funding_last_5yrs` is an application field with no provider counterpart, and `source_url` is not a v4 funding-round field; earlier revisions of these files published both keys inside the payloads so the live path would populate the columns. Both have been **removed**, because a fixture that supplies a key the real API does not would prove the mapper works against a shape it will never meet — which is the one thing these payloads exist to disprove. What the provider does publish is still carried: `last_funding_at` and `last_funding_type` remain on every organisation payload, and `permalink` remains on every funding-round payload. Neither reaches its column on the live path in this delivery — `IngestionMapper` declares a single alias for `institutional_funding_last_5yrs` and implements no derivation, and `source_url`'s `permalink` fallback is a bare slug that fails the field's `isHttpsUrl()` validation — so both columns are left unwritten on the live path, which rows 5 and 6 of [Live and fallback are not identical](#live-and-fallback-are-not-identical-in-their-optional-fields) record and [`../docs/gaps-and-flags.md`](../docs/gaps-and-flags.md) flags.

Each payload stays far inside the 8000-character column limit; the largest shipped payload is 1,830 characters, on the funding-round row carrying five participating investors.

#### The designed partial-response fixture

One payload deliberately omits optional keys the others carry: the `crunchbase_investors_sample.csv` row for **Menotomy Capital Group** publishes `identifier`, `facet_ids`, `short_description` and `website`, and **no** `investor_type`, `categories` or `assets_under_management`. A real API read returns partial objects, and this row is the fixture that proves the absent-versus-blank rule holds under one: the flattened columns on the same staging row do carry a type, focus areas and an AUM, so the fallback path writes what it can while the live path writes neither the focus areas nor the AUM — and, critically, a later live run over this payload leaves both stored values untouched rather than clearing them. Restoring the omitted keys would remove the only coverage of that behaviour.

This row does double duty, and the second job is worth naming because it is easy to misread as a bug. Its flattened `type` is `Family Office`, which is **not** a member of the `type` choice list — and that list, unlike `focus_areas`, declares no `Other` member. Cleaning rule 3 therefore normalises the value to nothing and the column is left unwritten, so `type` is absent on the **fallback** path too, not only on the live one. The row is consequently both the partial-response fixture and the fixture for an unmatched value on a list with no `Other` member; the two behaviours meet here deliberately.

Two other investor payloads omit a key as well, and those omissions are consistent rather than partial: `Nahanton Square Accelerator` omits `categories` and `Chickatawbut Seed Partners` omits `assets_under_management`, and in both rows the matching flattened column is blank. Where a flattened column carries no value, the payload publishes no key for it, so the two paths agree.

`participating_investor_names` **is a JSON array of investor names**, and a comma inside it is data rather than a delimiter. `IngestionMapper.resolveParticipants()` reads three carriers, in this order: a real array, a JSON array string, and a string delimited by `|`. **Anything else is one name.** For each member it then trims it, drops it if it is empty, resolves it through `resolveInvestor()`, keeps it once if the same investor is named twice, and — if it resolves to no Investor or to more than one — logs a warning naming the reason and links no join row for it. The remaining members become the join rows. A value that yields no name at all is logged by `IngestionLogger.invalidEncoding()`.

**A comma is never a delimiter on this column**, because an investor name may contain one — a legal suffix such as `Ltd, LLC`, or a place name. The `|` form is available for a tool that cannot emit JSON, and the mapper accepts it identically.

The live payloads carry the same list under the source's own `investor_identifiers` key as an array of v4 identifier objects. `IngestionMapper._flattenNameList()` flattens that array to a **JSON array of names serialised as text** — never to a comma-joined string — which is the same carrier the shipped CSV uses, so both routes reach `resolveParticipants()` through an accepted carrier and neither can split a name in half.

#### Worked examples

The three payloads below are the **first data row of three of the shipped files**, verbatim and before CSV quoting is applied, so each can be checked against the file it came from. A Crunchbase v4 organisation read:

```json
{"properties":{"identifier":{"value":"Beacon Hill Robotics","permalink":"beacon-hill-robotics","uuid":"9ea9e675-7ef7-ddb4-2ad6-d96f177f3810","entity_def_id":"organization"},"facet_ids":["company"],"short_description":"Autonomous inspection robots for commercial building operators.","categories":[{"value":"Science and Engineering","permalink":"science-and-engineering","entity_def_id":"category_group"}],"founded_on":{"value":"2019-01-01","precision":"year"},"location_identifiers":[{"value":"Boston, MA","location_type":"city","permalink":"boston-ma"}],"website":{"value":"https://beaconhillrobotics.example.com"},"image_url":"https://cdn.example.org/logos/beacon-hill-robotics.png","last_funding_type":"series_b","funding_total":{"value":48000000,"currency":"USD","value_usd":48000000},"operating_status":"active","num_employees_enum":"c_00051_c_00200","last_funding_at":"2023-02-21","institutional_funding_last_5yrs":true}}
```

Every choice value here is a source-vocabulary code rather than a target value: `c_00051_c_00200` becomes `51-200`, `series_b` becomes `Series B`, `Science and Engineering` becomes `Deeptech`, and an `operating_status` of `active` becomes the boolean `true`. Three v4 value shapes are visible too: `identifier` and each `categories` member are identifier objects, flattened to their `value`; `founded_on` is a date object, flattened to `2019-01-01` and then reduced to the year `2019`; and `funding_total` is a money object, flattened to `48000000` by taking `value_usd` first. `location_identifiers` flattens to `Boston, MA`. `facet_ids` declares this organisation a `company`, which is what allows it to be mapped as a Startup at all. `last_funding_at` and `last_funding_type` are the two signals the live path derives `institutional_funding_last_5yrs` from when the flag is absent; here the flag is present, so the derivation is skipped and the two signals are readable as its justification. The translation tables are listed under [Choice values](#choice-values).

A Crunchbase v4 funding-round read, which names its parent company through an identifier object rather than flat:

```json
{"properties":{"identifier":{"value":"Beacon Hill Robotics Seed","permalink":"beacon-hill-robotics-seed","uuid":"a23952e1-bcd5-58cf-7fac-a2c1c2e0e583","entity_def_id":"funding_round"},"funded_organization_identifier":{"value":"Beacon Hill Robotics","permalink":"beacon-hill-robotics","uuid":"9ea9e675-7ef7-ddb4-2ad6-d96f177f3810","entity_def_id":"organization"},"funded_organization_location":[{"value":"Boston, MA","location_type":"city","permalink":"boston-ma"}],"investment_type":"seed","money_raised":{"value":3200000,"currency":"USD","value_usd":3200000},"announced_on":{"value":"2019-11-12","precision":"day"},"lead_investor_identifiers":[{"value":"Emerald Necklace Angels","permalink":"emerald-necklace-angels","uuid":"c36e9309-e2c2-b2fb-29b0-2c836183f5d0","entity_def_id":"organization"}],"investor_identifiers":[{"value":"Emerald Necklace Angels","permalink":"emerald-necklace-angels","uuid":"c36e9309-e2c2-b2fb-29b0-2c836183f5d0","entity_def_id":"organization"},{"value":"Chickatawbut Seed Partners","permalink":"chickatawbut-seed-partners","uuid":"f558c1cc-7cf8-271b-5054-9b305d9a5830","entity_def_id":"organization"}],"pre_money_valuation":{"value":14000000,"currency":"USD","value_usd":14000000},"permalink":"beacon-hill-robotics-seed","source_url":"https://news.example.com/rounds/beacon-hill-robotics-seed"}}
```

`money_raised` and `pre_money_valuation` are money objects; `announced_on` is a date object; `lead_investor_identifiers` and `investor_identifiers` are arrays of identifier objects. The participant array flattens to a **JSON array of names**, which is the same carrier the flattened `participating_investor_names` column uses, so neither route can split a name that contains a comma. `permalink` is what the provider publishes; `source_url` is the announcement URL the application stores, and the alias chain prefers it.

A **synthetic** LinkedIn member record. It is not a captured LinkedIn response — see the second bullet at the top of this section — and it says so in its own first member:

```json
{"synthetic":true,"data":{"elements":[{"id":"ln-member-40118","name":"Marisol Trevanion","title":"Chief Executive Officer","summary":"Co-founded Beacon Hill Robotics after a decade in industrial controls, and now leads its commercial strategy.","headline":"CEO at Beacon Hill Robotics","profileUrl":"https://people.example.com/in/marisol-trevanion","companyName":"Beacon Hill Robotics","companyLocation":"Boston, MA","emailAddress":"marisol.trevanion@example.com"}],"paging":{"count":1}}}
```

`companyName` **and** `companyLocation` together are what make this row's mandatory `startup` reference resolvable; either alone resolves nothing. `id` is carried because a read of this shape would return one, and the mapper's allowlist has no target field for it, so it is read and discarded rather than written anywhere. `paging` is carried for the same reason.

### Choice values

Every choice value is spelled exactly as its choice list spells it, including case, spaces, hyphens and the `+` in `Series C+` and `500+`. The authoritative lists are the `sys_choice` records in the Update Set, restated per record type in the tables above and in [`../docs/data-model.md`](../docs/data-model.md).

Cleaning rule 3 normalises **every** closed-choice column, not just some of them. `IngestionMapper.normaliseChoice()` matches an incoming value exactly, then case-insensitively, and where nothing matches it applies one of two outcomes:

- The value is stored as `Other` **where the target choice list declares an `Other` member**.
- The field is **left unwritten** where the target list declares no `Other` member.

`IngestionLogger` records a `choice_unmatched` event either way, naming the record type, the column and which outcome was applied. **No value outside a choice list is ever stored on an entity record.** The staging columns for choice fields are plain strings with no choice list attached, so an unmatched value loads into staging unchanged and is normalised at transform time.

#### Source vocabulary is translated before anything is judged unmatched

The flattened columns in these files are authored in **target** vocabulary — `Series B`, `51-200`, `Hybrid` — so they match a choice list directly. `raw_payload` is authored in **source** vocabulary, and a source publishes codes, not target values. A step ahead of cleaning rule 3 therefore translates every source code to its target value, and only what survives untranslated is judged unmatched. Without it every live choice value would land on `Other` or on nothing.

These are the codes the shipped payloads actually carry, and what each becomes. Each row is verifiable by running the payload through the mapper:

| Source key | Target column | Codes in these files | Becomes |
| --- | --- | --- | --- |
| `num_employees_enum` | `Startup.employee_count_range` | `c_00001_c_00010`, `c_00011_c_00050`, `c_00051_c_00200`, `c_00201_c_00500`, `c_00501_c_01000` | `1-10`, `11-50`, `51-200`, `201-500`, `500+` |
| `last_funding_type` | `Startup.funding_stage` | `pre_seed`, `seed`, `series_a`, `series_b`, `series_c`, `corporate_round` | `Pre-Seed`, `Seed`, `Series A`, `Series B`, `Series C+`, `Growth` |
| `investment_type` | `FundingRound.round_type` | the same six | the same six |
| `categories` | `Startup.industry`, `Investor.focus_areas` | `Science and Engineering`, `Software`, `Financial Services`, `Health Care`, `Consumer Goods`, `Other` | `Deeptech`, `SaaS`, `Fintech`, `Healthtech`, `Consumer`, `Other` |
| `operating_status` | `Startup.active` | `active`, `closed` | `true`, `false` |
| `investor_type` | `Investor.type` | `angel`, `venture_capital`, `private_equity_firm`, `corporate_venture_capital`, `accelerator` | `Angel`, `VC`, `PE`, `Corporate`, `Accelerator` |
| `title` | `Founder.title`, `Executive.title` | `Chief Executive Officer`, `Chief Technology Officer`, `Chief Operating Officer`, `Chief Financial Officer`, `Co-Founder`, `Vice President of Engineering`, `Vice President of Sales`, `Vice President of Marketing`, `Head of Product Management` | `CEO`, `CTO`, `COO`, `CFO`, `Co-Founder`, `VP Engineering`, `VP Sales`, `VP Marketing`, `Head of Product` |
| `jobFunction` | `JobPosting.department` | `eng`, `sale`, `mrkt`, `prdm`, `prjm`, `othr` | `Engineering`, `Sales`, `Marketing`, `Product`, `Operations`, `Other` |
| `workplaceType` | `JobPosting.remote_type` | `ON_SITE`, `HYBRID`, `REMOTE` | `Onsite`, `Hybrid`, `Remote` |
| `experienceLevel` | `JobPosting.seniority` | `ENTRY_LEVEL`, `ASSOCIATE`, `MID_SENIOR_LEVEL`, `DIRECTOR`, `EXECUTIVE` | `Entry`, `Mid`, `Senior`, `Lead`, `Executive` |
| `jobState` | `JobPosting.active` | `LISTED`, `CLOSED` | `true`, `false` |

Three consequences are worth reading off that table. Crunchbase's employee bands are **finer** than the target's, so `c_00051_c_00100` and `c_00051_c_00200` both land on `51-200` — a deliberate many-to-one collapse, not a mistake — and the same holds for `series_c` through `series_j`, all of which land on `Series C+`. `corporate_round`, `private_equity` and `secondary_market` all land on `Growth`, for the same reason. And a Crunchbase category group is a free-form name rather than a closed enumeration, which is why the out-of-list industry fixture works at all.

**Eight values in these payloads are deliberately out of vocabulary, and every one is carried verbatim.** Each is the live-path half of a rule 3 fixture whose flattened column carries the same value, so the two routes reach the same outcome and the fixture proves the rule rather than the transport. The table records two neighbouring cases alongside them — one value that looks out of vocabulary and is not, and one that is out of vocabulary and reaches the pipeline through the flattened column alone:

| Payload value | Source key | Target column | Outcome |
| --- | --- | --- | --- |
| `Cleantech` | `categories` | `Startup.industry` | Stored as `Other` — that list declares an `Other` member. |
| `Series C` | `last_funding_type`, `investment_type` | `Startup.funding_stage`, `FundingRound.round_type` | Left **unwritten** — neither list declares `Other`. Note that `Series C+` is the member and `Series C` is not. |
| `Acquired` | `last_funding_type`, `investment_type` | the same two | **Matched.** It is a member of both lists, and the provider publishes no code for it, so the payload carries the application's own value. |
| `50-100` | `num_employees_enum` | `Startup.employee_count_range` | Left **unwritten** — no `Other` member. |
| `Family Office` | — | `Investor.type` | Not in the payload at all. The Menotomy row is the [partial-response fixture](#the-designed-partial-response-fixture); the value reaches the pipeline through the flattened column only, and is left unwritten there. |
| `Founding Engineer` | `title` | `Founder.title` | Stored as `Other`. |
| `Chief Revenue Officer` | `title` | `Executive.title` | Stored as `Other`. |
| `Customer Success` | `jobFunction` | `JobPosting.department` | Stored as `Other`. |
| `Flexible` | `workplaceType` | `JobPosting.remote_type` | Left **unwritten** — no `Other` member. |
| `Principal` | `experienceLevel` | `JobPosting.seniority` | Left **unwritten** — no `Other` member. |

The tables cover more codes than these files use, including the funding types that correspond to no target member at all: `debt_financing`, `grant`, `non_equity_assistance`, `initial_coin_offering` and `undisclosed` are recognised and resolve to nothing, logged as `recognised crunchbase code with no target member, left unwritten` so an operator can tell a known-but-unmappable code from one nobody has seen before. No shipped payload carries one, because these files are a mapping fixture rather than an exhaustive vocabulary test; that coverage belongs to the ATF suites.

**The supplied value itself is logged only when it is safe to log, and a value that is not safe is omitted rather than transformed.** `IngestionLogger._choiceValue()` applies one rule to every unmatched choice value before it reaches a log line:

| Case | What the log line carries |
| --- | --- |
| The value is empty | The literal `(blank)` |
| The **field name** is one that can carry personal or free-text data | The literal `(redacted)` |
| The value has the shape of a short enumeration label — begins with a letter or digit, is at most 40 characters, and uses only letters, digits, spaces and `+ . _ / -` | The value **verbatim**, so an operator can see exactly what the source sent and correct the mapping |
| Anything else — longer than 40 characters, or containing a comma, an `@`, a quote or any other character outside that set | The literal `(redacted)` |

The eleven choice columns cleaning rule 3 normalises — `industry`, `funding_stage`, `employee_count_range`, `title` on `founder`, `title` on `executive`, `type`, `focus_areas`, `round_type`, `department`, `remote_type` and `seniority`, which is eleven columns under ten distinct names — are all closed enumerations that carry no personal data, so a genuinely mis-spelled choice value such as `series-a` or `Chief Technology Officer` is logged in full and is directly actionable. A value that arrives in one of them looking nothing like an enumeration label — a pasted biography, an address, a comma-joined list — is replaced by `(redacted)`, because a value of that shape is far more likely to be misplaced person data than a mis-spelled choice.

**No hash, digest or fingerprint of any supplied value is computed anywhere in the pipeline.** A redacted value is *dropped*, not encoded: nothing derived from it is recorded, so there is nothing an offline guess could be tested against. The application computes one fingerprint, `AppProperties.fingerprint()`, and it is over the text of a **caught fault** rather than over a field value — it is what lets a failure be recorded as a closed code plus an eight-character reference plus a length instead of as the caught text. It identifies the fault, not a value, and as a 32-bit rolling hash over arbitrary-length input it collides far too readily to identify one. Correlation across the log lines of one row is provided instead by two mechanisms that are derived from nothing the record contains:

| Mechanism | Form | What it correlates |
| --- | --- | --- |
| `IngestionLogger.reference(kind, token)` | `<kind>:<token>` — for example `staging:` followed by a 32-character platform record identifier, or `record:` followed by one | Every log line about one row, by the identifier of the **platform record** rather than by anything the source sent |
| `IngestionLogger.ordinal(kind)` | `<kind>:<n>` — an arrival ordinal counted from one within the run | Every log line about one row where no platform identifier exists yet, such as a row rejected before it was written |

Both are per-run and neither is computed from a value, so neither can be reversed to one and neither correlates a row across runs.

The same policy governs every other log line the ingestion pipeline writes, and the narrowing is exact rather than absolute. An identifier that is not an opaque reference or a platform record identifier is replaced by `(redacted)` before it is recorded; the whole value of every field named as sensitive — among them `contact_email`, `bio`, `linkedin_url` and `raw_payload` — is replaced by `(redacted)`; and free text has **address-like and locator-like substrings** replaced. Free text that is neither, such as an ordinary personal name, is recorded as it stands. **A log erasure procedure is therefore an operator-owned obligation**, stated with the others in [`../docs/data-model.md`](../docs/data-model.md).

Six of the eleven choice lists declare no `Other` member — `Startup.funding_stage`, `Startup.employee_count_range`, `Investor.type`, `FundingRound.round_type`, `JobPosting.remote_type` and `JobPosting.seniority` — and an unmatched value in any of them is logged and the field left unwritten. The other five — `Startup.industry`, `Investor.focus_areas`, `Founder.title`, `Executive.title` and `JobPosting.department` — declare `Other`, and an unmatched value in any of them is stored as `Other` and logged. **Do not add an `Other` choice to any of the six lists that lack one**: prompt section 1.0 declares the field and choice definitions binding and complete, and the `sys_choice` inventory in the Update Set is exactly the 63 entity choice values those definitions declare. The full column-by-column outcome table is in [`../docs/data-model.md`](../docs/data-model.md).

## Row counts and designed defects

### Row counts

Sixty-five data rows in total, excluding header rows. **This table is the authoritative row count for every document of this package**; where any other statement of a per-file count differs, this table governs and the other statement is corrected to it.

| File | Data rows |
| --- | --- |
| `crunchbase_startups_sample.csv` | 13 |
| `crunchbase_investors_sample.csv` | 8 |
| `crunchbase_funding_rounds_sample.csv` | 12 |
| `linkedin_founders_sample.csv` | 10 |
| `linkedin_executives_sample.csv` | 10 |
| `linkedin_job_postings_sample.csv` | 12 |

The count an operator sees in the import set after a load must equal the number above. A different count means the file was truncated, or a quoted field containing a line break was split.

**On the startups file's thirteenth row.** `crunchbase_startups_sample.csv` carries **13** data rows rather than the 12 an early planning estimate assumed. The extra row is deliberate and load-bearing: it is the second half of the [cleaning rule 2](#designed-defects) duplicate pair, matching another row on `name` and `headquarters_location` while differing on `website`, and it is the only fixture in the dataset that lets the deduplication rule be observed doing its work. **Do not delete it to reach 12.** The reconciliation is stated once here so the discrepancy reads as a designed fixture and not as an authoring error: 13 is correct, 12 is stale, and both the sixty-five-row total and the 52 accepted / 13 rejected reconciliation are computed from 13. The transform map's **92** field maps are unaffected by the row count, being one per CSV column position — 19, 12, 16, 14, 14 and 17 across the six files — rather than one per row.

After the transform has run over all sixty-five rows, `x_bst_startuptrk_ingest_staging.import_state` reconciles to **52 `processed`, 13 `rejected`, 0 `error` and 0 `pending`**. The thirteen rejected rows are the twelve blank-mandatory fixtures plus the one batch duplicate, and `error_message` names each one's outcome code. `IngestionLogger` records eleven `choice_unmatched` events across the run pair, one for each of the eleven choice-backed columns. A different distribution means a file was edited or the transform map is mismapped.

All of the data is synthetic. It contains no real personal data, no real contact details and no real financial figures. Every `contact_email` value is an obviously synthetic address on an example domain, and every `linkedin_url` value is an obviously synthetic profile URL.

### Designed defects

Some rows are **deliberately defective** so that a load exercises all four of the prompt section 4.0 cleaning rules. They are intentional fixtures, not authoring errors.

| Rule | Which file demonstrates it | How to recognise the row | Expected outcome |
| --- | --- | --- | --- |
| 1. Trim whitespace on all string fields | All six files: the three `crunchbase_*_sample.csv` files and the three `linkedin_*_sample.csv` files, at least one row each | A **quoted** string value with leading or trailing space, for example `" Example Labs"`. Every one of the fourteen is quoted — see [Designed whitespace is always quoted](#designed-whitespace-is-always-quoted) | The value is trimmed and the row loads and transforms normally. The trimmed value is what reaches the entity record. |
| 2. Deduplicate Startup records on `name` plus `headquarters_location`, case-insensitively | `crunchbase_startups_sample.csv` only | A pair of rows whose `name` and `headquarters_location` match when both are lowercased and trimmed, but whose `website` values differ | One Startup record survives the pair. The second row is recognised as a duplicate and does not create a second record. |
| 3. Normalise every choice-backed column, mapping an unmatched value to `Other` where the list defines one and logging it | All six files. Eleven values across ten rows carry an unmatched choice value; they are listed row by row in [Unmatched values in choice columns](#unmatched-values-in-choice-columns) | A value that appears in no choice list, for example a `funding_stage` of `Series C` without the `+`, an `employee_count_range` of `50-100`, or a `title` of `Founding Engineer` | The value becomes `Other` when the target list defines an `Other` member and is left unwritten when it does not; either way `IngestionLogger` records the value and names the outcome. The row otherwise loads and transforms normally. |
| 4. Reject records missing mandatory fields rather than inserting partial records | All six files: the three `crunchbase_*_sample.csv` files and the three `linkedin_*_sample.csv` files. Each file carries one row per mandatory column of its record type, which gives **twelve** such rows in total: `crunchbase_investors_sample.csv`, whose only mandatory column is `name`, carries one; `crunchbase_startups_sample.csv`, whose mandatory columns are `name`, `headquarters_location` and `active`, carries three; and the remaining four files carry two each. The `startup` reference of a child record type is one mandatory field carried by two staging columns, so it accounts for one such row rather than two | A blank in a column marked mandatory for that record type: `name`, `headquarters_location` or `active` on startups, `name` on investors, `startup_name` or `round_date` on funding rounds, `name` or `startup_name` on founders and executives, `startup_name` or `title` on job postings | `import_state` becomes `rejected`, `error_message` names **every** missing mandatory column on that row, and **no** entity record is created. |

#### Designed whitespace is always quoted

Fourteen fields carry designed leading or trailing whitespace, and every one of them is quoted. Twelve are quoted **only** for their whitespace; the remaining two, `headquarters_location` on data rows 7 and 10 of `crunchbase_startups_sample.csv`, contain a comma and would be quoted for that alone. The twelve are:

| File | Line | Column | Value as shipped |
| --- | ---: | --- | --- |
| `crunchbase_startups_sample.csv` | 7 | `name` | `"  Neponset Analytics Labs"` |
| `crunchbase_startups_sample.csv` | 8 | `name` | `"neponset analytics labs "` |
| `crunchbase_investors_sample.csv` | 6 | `name` | `"  Nahanton Square Accelerator"` |
| `crunchbase_investors_sample.csv` | 7 | `website` | `"https://chickatawbutseed.example.com "` |
| `crunchbase_funding_rounds_sample.csv` | 10 | `startup_name` | `" Muddy River Diagnostics"` |
| `crunchbase_funding_rounds_sample.csv` | 11 | `lead_investor_name` | `"Wompatuck Corporate Ventures "` |
| `linkedin_founders_sample.csv` | 6 | `name` | `" Anselm Quintero-Vale"` |
| `linkedin_founders_sample.csv` | 7 | `startup_name` | `"Copley Grid Systems "` |
| `linkedin_executives_sample.csv` | 3 | `title` | `" VP Engineering"` |
| `linkedin_executives_sample.csv` | 6 | `startup_name` | `"Seaport Ledger "` |
| `linkedin_job_postings_sample.csv` | 7 | `title` | `" Product Marketing Manager"` |
| `linkedin_job_postings_sample.csv` | 8 | `startup_name` | `"Kendall Cognition "` |

Line numbers are file lines, so line 2 is the first data row. **Every designed-whitespace field is quoted, and none is left bare.** RFC 4180 treats a space inside an unquoted field as part of the field, but real CSV readers vary: many strip surrounding whitespace from an unquoted field, and the platform's own import behaviour on that point is not something this package controls. A stripped fixture does not fail loudly — it loads a clean value, the trim rule has nothing to do, and the rule 1 assertion passes for the wrong reason. Quoting takes the reader out of the question. Recorded at `D-177`.

Rule 2's duplicate pair differs on `website`, so it is caught by a deduplication keyed on name plus headquarters location — what prompt section 4.0 specifies — and not by one keyed on name plus website.

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

Eleven values across ten rows match no member of their target choice list. All eleven are rule 3 fixtures, and the outcome depends on one thing only: whether the target list defines an `Other` member.

**Cleaning rule 3 requires an unmatched value to be mapped to `Other` and logged. Six of the eleven delivered choice lists declare no `Other` member**, and the prompt declares its choice lists binding and complete, so on those six the rule cannot be satisfied without changing a frozen enumeration. The delivered behaviour on those columns is to leave the value unwritten, log it with an outcome string that names the conflict, and count it as **`rule3_deviations`** in the run summary — so the deviation is observable and countable on every run rather than silent. **This is a flagged partial implementation of rule 3, not compliance with it**, and it is recorded in [`../docs/gaps-and-flags.md`](../docs/gaps-and-flags.md) and in [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md). The six lists that lack an `Other` member are `Startup.funding_stage`, `Startup.employee_count_range`, `Investor.type`, `FundingRound.round_type`, `JobPosting.remote_type` and `JobPosting.seniority`. **Do not add an `Other` member to any of them to make the count read zero**: that is a change to a frozen enumeration and only a human may authorise it. Two of the eleven sit on one row — data row 8 of `crunchbase_startups_sample.csv` carries an unmatched `industry` and an unmatched `funding_stage` — which is why ten rows carry eleven values.

| File | Data row | Value carried | Column | Target choice list | Has `Other` | Outcome |
| --- | --- | --- | --- | --- | --- | --- |
| `crunchbase_startups_sample.csv` | 8 | `Cleantech` | `industry` | `Startup.industry` | Yes | Stored as `Other` and logged. |
| `crunchbase_startups_sample.csv` | 8 | `Series C` | `funding_stage` | `Startup.funding_stage` | No | Logged; the field is left unwritten on the entity record. |
| `crunchbase_startups_sample.csv` | 10 | `50-100` | `employee_count_range` | `Startup.employee_count_range` | No | Logged; the field is left unwritten on the entity record. |
| `crunchbase_investors_sample.csv` | 6 | `Cleantech` | `focus_areas` | `Investor.focus_areas` | Yes | The member becomes `Other` and is logged. The row's remaining member `Fintech` is unaffected, so the stored list is `Fintech,Other`. |
| `crunchbase_investors_sample.csv` | 7 | `Family Office` | `type` | `Investor.type` | No | Logged; the field is left unwritten on the entity record. |
| `crunchbase_funding_rounds_sample.csv` | 8 | `Series C` | `round_type` | `FundingRound.round_type` | No | Logged; the field is left unwritten on the entity record. |
| `linkedin_founders_sample.csv` | 8 | `Founding Engineer` | `title` | `Founder.title` | Yes | Stored as `Other` and logged. |
| `linkedin_executives_sample.csv` | 8 | `Chief Revenue Officer` | `title` | `Executive.title` | Yes | Stored as `Other` and logged. |
| `linkedin_job_postings_sample.csv` | 10 | `Customer Success` | `department` | `JobPosting.department` | Yes | Stored as `Other` and logged. |
| `linkedin_job_postings_sample.csv` | 11 | `Flexible` | `remote_type` | `JobPosting.remote_type` | No | Logged; the field is left unwritten on the entity record. |
| `linkedin_job_postings_sample.csv` | 12 | `Principal` | `seniority` | `JobPosting.seniority` | No | Logged; the field is left unwritten on the entity record. |

Every file carries at least one of these fixtures, and the eleven between them cover both halves of the policy: **five** values coerce to `Other`, and **six** are logged, left unwritten and counted as `rule3_deviations`. A full load of all six files therefore produces `unmatched` of `11` and `rule3_deviations` of `6` across the two flows — four of the six on the Crunchbase side and two on the LinkedIn side. Those two figures are the fixture's own assertion: a run reporting `rule3_deviations` of `0` after a full load has either lost the count or gained an `Other` member somewhere it should not have. Every event carries a `deviation` member, `true` on the six and `false` on the five, so the two halves are distinguishable in the log as well as in the totals.

`Series C` appears twice on purpose, once on a startup and once on a funding round, because `Startup.funding_stage` and `FundingRound.round_type` share the same eight values and both must behave identically. `Cleantech` likewise appears twice, once as a `Startup.industry` value and once as a member of `Investor.focus_areas`, because `focus_areas` reuses the six `Startup.industry` values and both must behave identically — the difference being that `focus_areas` normalises member by member, so only the unmatched member becomes `Other`.

`Investor.type` is the one column in this dataset whose unmatched value is neither coerced nor part of a list: the list is `VC`, `Angel`, `PE`, `Corporate`, `Accelerator` with no `Other` member, so `Family Office` on data row 7 is logged and `type` is left unwritten. Data row 7 is `Menotomy Capital Group`, the one investor no funding round references, so the row is otherwise unencumbered and its outcome is observable in isolation.

A list with no `Other` member offers no value to normalise to, so the unmatched value is logged and the field left unwritten rather than coerced into a value the dictionary does not define. **Do not add an `Other` choice to any of these lists**: prompt section 1.0 declares the field and choice definitions binding and complete. Each of the ten rows is otherwise valid and transforms normally — an unwritten choice column is not a rejection, and the record is still created.

**Left unwritten is not the same as emptied.** The mapper removes the field from the record it is about to write rather than writing an empty value into it. On an insert the column is simply empty; on an **update** whatever the column already stores survives, so an unmatched incoming value never destroys a good stored value. That is the same rule described under [Absent is not blank, and ingestion never clears a stored value](#absent-is-not-blank-and-ingestion-never-clears-a-stored-value), and it is why the flow execution log names this outcome `left unwritten` rather than `left empty`.

### Non-resolving references

Every `startup_name` value, and every `lead_investor_name` and `participating_investor_names` value, in every child file resolves to a record present in `crunchbase_startups_sample.csv` or `crunchbase_investors_sample.csv`, with one class of exception.

The exception is the rule 4 fixtures. A row authored to be rejected for a blank mandatory field is the **only** kind of row whose natural-key reference may fail to resolve, and in those rows the failure is the blank itself: a blank `startup_name` on a founder, executive, funding round or job posting row cannot resolve to a Startup, which is precisely the condition rule 4 rejects. Recognise them by the blank column. Each child file carries exactly one such row, the fixture whose `startup_name` is blank; that file's other rule 4 fixture blanks a different mandatory column — `round_date` on funding rounds, `name` on founders and executives, `title` on job postings — and its `startup_name` still resolves. A non-resolving reference in any row that is **not** a rule 4 fixture is a mistake, not a designed defect, and should be reported.

The three rejected startup rows create no Startup record, so no child row may reference them. Two of the three carry a blank `startup_name` or a blank `headquarters_location` and so have no usable name; the third names `Charles River Telemetry`, and **no row in any child file references that name**.

### Live and fallback are not identical in their optional fields

Both paths over this dataset accept the same 52 rows and reject the same 13, and every accepted record carries the same identity on both — the same `name`, `headquarters_location` and `active` on a startup, the same parent and `round_date` on a funding round, the same parent and `title` on a job posting. The two paths therefore describe the same entities, and the rule 2 de-duplication keys agree.

They differ in the **six** cases catalogued below — one of which, row 3, is listed because it looks like a divergence and is not. Every one is a designed consequence of the two paths reading different things rather than a defect. The payloads carry the source system's own code wherever the source publishes one and the fixture's own value verbatim wherever it does not, so the two routes agree on every closed-choice column — including all eight of the out-of-vocabulary rule 3 fixtures, which now reach the same outcome on both routes. What remains are the cases where one route has evidence the other does not. The full catalogue:

| # | Records | Field | Fallback writes | Live writes | What the provider publishes for it |
| --- | --- | --- | --- | --- | --- |
| 1 | `Menotomy Capital Group` | `focus_areas` | `Healthtech,Deeptech` | nothing | The designed [partial-response fixture](#the-designed-partial-response-fixture) omits `categories`. |
| 2 | `Menotomy Capital Group` | `aum_usd` | `95000000` | nothing | The same fixture omits `assets_under_management`. |
| 3 | `Menotomy Capital Group` | `type` | nothing | nothing | **Not a divergence, and listed because it looks like one.** The fixture omits `investor_type`, and the flattened column carries `Family Office`, which is not a member of a list that declares no `Other`. Both routes therefore leave the column unwritten, by two different mechanisms. |
| 4 | `Casimir Pellworth`, `Rosalind Ebersole`, `Guinevere Halstrom` — **3** people | `bio` | nothing | the person's `headline` | These three rows carry no flattened `bio` and their payloads publish no `summary`. The `bio` alias chain declares `summary` then `headline`, so the live path falls back to the headline — which is the documented alias behaviour, and the only case in this dataset where a live value exists because of a second-choice alias. |
| 5 | Every accepted startup — **9** | `institutional_funding_last_5yrs` | the flattened column's `true` or `false` | nothing | **Crunchbase v4 publishes no field that answers this question**, and the payloads therefore no longer name one. `IngestionMapper.LIVE_ALIASES` declares a single alias for this field — the application's own column name — and implements **no** derivation, so on the live path the value is left unwritten. `D-210` decided an entitlement-gated derivation from funding-round evidence; it is **not implemented in this delivery** and is flagged in [`../docs/gaps-and-flags.md`](../docs/gaps-and-flags.md). The fallback column stands, because the staging table is an application shape rather than a provider echo. |
| 6 | Every accepted funding round carrying a flattened `source_url` | `source_url` | the flattened column's URL | nothing | **v4 publishes no `source_url` on a funding round**, and the payloads no longer name one. The alias chain is `['source_url', 'permalink']`, and `permalink` is a bare slug such as `beacon-hill-robotics-seed` while the field is declared `kind: 'url'` and validated by `isHttpsUrl()` — so the fallback alias cannot satisfy the validation and the live path leaves the column unwritten. That inert alias is flagged in [`../docs/gaps-and-flags.md`](../docs/gaps-and-flags.md) rather than hidden. |

**One field group deserves a note because a reader may expect it to diverge and it does not.**

`institutional_funding_last_5yrs` has no provider counterpart. Every payload carries the value **together with the two signals the live path derives it from** — `last_funding_at` and `last_funding_type` — and `IngestionMapper` skips the derivation when the flag is supplied, so the flattened column and the payload agree and the signals stand as the flag's evidence rather than as a second source of it.

`funding_stage` and `round_type` on the `Esplanade Learning` records carry `Acquired`, which is a member of both target lists and a value Crunchbase's funding-type vocabulary has no code for — an acquisition is not a funding round. The payload therefore carries `Acquired` verbatim, it falls through translation untouched, and the choice list matches it. Both routes write it.

**Do not "repair" a flattened column to match its payload, or a payload to match its column.** Either edit deletes a cleaning-rule-3 fixture, and the counts under [Unmatched values in choice columns](#unmatched-values-in-choice-columns) then no longer hold.

None of the six is a value **conflict**: there is no field where the two paths write two different non-empty values. Every difference is one path writing and the other leaving unwritten. That matters because of the no-clear rule — running the fallback import and then a live run, in either order, is additive, and neither run removes what the other wrote.

## Data Import Wizard procedure

This section is a complete, self-contained load procedure: the prerequisites, the load order, the wizard steps and the post-load verification below are sufficient to stage all six files without reading another document. The transform map and its field-by-field script are a separate, larger artifact and are specified in [`../docs/manual-build/06-staging-table-csv-import.md`](../docs/manual-build/06-staging-table-csv-import.md).

### Prerequisites

- The Update Set has been committed to the target instance, so `x_bst_startuptrk_ingest_staging` exists. The commit sequence is specified in [`../docs/deployment-runbook.md`](../docs/deployment-runbook.md); the post-commit gates that confirm the tables exist are in [`../docs/validation-gates.md`](../docs/validation-gates.md), which is delivered with this package.
- The operator holds the `x_bst_startuptrk.admin` role. The staging table grants **read, write, create and delete to that role alone**, so this procedure cannot be performed by a caller holding only `x_bst_startuptrk.user` or `x_bst_startuptrk.premium_user`. Creating the import set table and the transform map additionally requires the platform `admin` role.

- The application picker is set to **Boston Startup Tracker**, so the import set table and transform map are created inside the `x_bst_startuptrk` scope.

### Load order

The files load in **four dependency groups**, and a group is imported *and* transformed to entity records before the next group begins:

| Group | Files | Depends on |
| --- | --- | --- |
| **A** | `crunchbase_startups_sample.csv` | Nothing |
| **B** | `crunchbase_investors_sample.csv` | Nothing |
| **C** | `crunchbase_funding_rounds_sample.csv` | A and B |
| **D** | `linkedin_founders_sample.csv`, `linkedin_executives_sample.csv`, `linkedin_job_postings_sample.csv`, in any order | A |

The grouping is load-bearing: child rows carry natural-key references to startups and investors, and a reference resolves against the **entity** record, not against the staged row. A staged parent is not enough — the parent group must have been transformed. Funding rounds reference both parents, so groups A and B both precede group C. The executable twelve-action sequence is [step 7 of `../docs/manual-build/06-staging-table-csv-import.md`](../docs/manual-build/06-staging-table-csv-import.md#step-7--run-the-dependency-group-sequence).

### Steps

For each file in the order above:

1. Open the Data Import Wizard from the application navigator, with the application picker set to **Boston Startup Tracker**.
2. Choose to import a data source, and create or select the import set table for this dataset.
3. Upload the CSV. The wizard reads the header row and offers one source column per header.
4. Verify the field mapping is one-to-one by header name against the `x_bst_startuptrk_ingest_staging` dictionary, and that **no** column is left unmapped. An unmapped column loads as an empty field without raising an error.
5. Run the import.
6. Confirm the imported row count equals the count stated for that file in this document.
7. Run the transform for the **group**, not for the file, once every file of that group has been imported. Its map, its arguments and the twelve-action sequence are specified in [`../docs/manual-build/06-staging-table-csv-import.md`](../docs/manual-build/06-staging-table-csv-import.md); the behaviour it implements is the four cleaning rules stated above, applied through `IngestionMapper`. Each Crunchbase group is transformed with its own `import_run`; the three group D files are transformed together by one call with an empty `import_run`.

### Verification after each load

Check all four of the following on the staged rows before running the transform. The staged rows are reachable through the **Ingestion staging** module of the Boston Startup Tracker application menu.

**Verify in the list view, not over the Table API.** The staging table ships with `ws_access` false, so `GET /api/now/table/x_bst_startuptrk_ingest_staging` does not serve it and a script written against that path will fail whether or not the rows loaded. The application menu module and the platform list view are the supported route; the reason for the posture is in [`../docs/data-model.md`](../docs/data-model.md).

- The row count matches the count stated for that file.
- Every row shows `import_state` of `pending`, and `import_run` carries this file's batch token. A `pending` row whose `import_run` begins `run:` is held by a flow run that never settled it; the recovery procedure is in [`../docs/manual-build/06-staging-table-csv-import.md`](../docs/manual-build/06-staging-table-csv-import.md#returning-an-abandoned-or-rejected-row-to-the-queue).
- Every row shows `run_provenance` of `fallback`.
- Every row has an empty `error_message`.

After the transform, `import_state` is `processed` on the fifty-two accepted rows, `rejected` on the thirteen that are not accepted — the twelve rule 4 fixtures plus the one rule 2 duplicate — and `error` and `pending` on none, while `import_run` on every settled row carries the lease of the run that settled it. `error_message` names the reason on each rejected row: for example `missing mandatory active` on `Charles River Telemetry`, whose `active` is blank, and `duplicate startup in the same batch` on the second member of the duplicate pair.

### Forcing the fallback path

Set the property `x_bst_startuptrk.ingestion.source_mode` to `fallback` to make both ingestion flows read this dataset instead of attempting a live call, which is how a flow test is made deterministic without touching credentials. **Capture the value the property held before you set it, and restore that value afterwards** rather than returning it to `live`: the end state is branch-determined — `live` only when both credential aliases are provisioned with a passing connection test — and the property is **one shared setting that both flows read**, so changing it for one changes it for the other. The rule is in [`../docs/manual-build/06-staging-table-csv-import.md#restoring-source_mode-is-readiness-determined-not-a-return-to-live`](../docs/manual-build/06-staging-table-csv-import.md#restoring-source_mode-is-readiness-determined-not-a-return-to-live). A run left on `live` also reads this dataset whenever the live call **fails**; the difference is that forcing `fallback` skips the live attempt altogether. **A run left on `live` whose call succeeds does not read this dataset even when the provider returned no rows** — see the table under the heading of this document. The flow-side steps are specified in [`../docs/manual-build/02-flow-crunchbase-ingestion.md`](../docs/manual-build/02-flow-crunchbase-ingestion.md) and [`../docs/manual-build/03-flow-linkedin-ingestion.md`](../docs/manual-build/03-flow-linkedin-ingestion.md).

## The loaded rows persist until a run settles them

**The 65 rows this dataset loads are not permanent, and clearing them is the operator's job.** No scheduled job prunes, minimises or deletes a staged row, and none is delivered. The rows persist on `x_bst_startuptrk_ingest_staging` until an ingestion run moves each one out of `pending` into `processed`, `rejected` or `error`, and then until an administrator removes them. There is no retention property, no retention service and no retention job: the Agent Action Plan freezes the inventory at eleven system properties, eight Script Includes and one scheduled job — that job maintains the rate-limit counter — and none of the three is a retention mechanism. Both inventories are in [`../docs/api-reference.md`](../docs/api-reference.md), and the obligation is stated in full under [Staging and counter data retention](../docs/data-model.md#staging-and-counter-data-retention--an-operator-owned-procedure) in [`../docs/data-model.md`](../docs/data-model.md).

The table's access posture is what protects its contents in the meantime. It holds verbatim upstream payloads in `raw_payload` and unvalidated person data in `name`, `title`, `bio`, `linkedin_url` and `contact_email`, and it ships administrator-only on all four operations with `ws_access` **false** — so no non-administrative caller, and no Table API request, can read a staged row at all. That posture is specified in [`../docs/access-control.md`](../docs/access-control.md).

Six consequences matter to anyone using this dataset:

- **A settled row is never re-read, so reload before re-testing.** The transform selects on `import_state` `pending`, so a second run over the same load finds nothing to do and creates no duplicate entity records. Re-run the import from the CSVs in this folder before repeating a flow test; that puts fresh rows on the table in `pending` carrying their batch tokens again.
- **A row a run abandoned is not re-read either, and returning it to the queue is one edit.** It stays `pending` carrying that run's lease in `import_run`, so the next run skips it. Clear `import_run`, or set it back to the batch token in the table above, and the next run claims it. The procedure is in [`../docs/manual-build/06-staging-table-csv-import.md`](../docs/manual-build/06-staging-table-csv-import.md#returning-an-abandoned-or-rejected-row-to-the-queue).
- **Clean-up is a deliberate administrative act.** To clear an unclaimed dataset, filter the **Ingestion staging** list on the six batch tokens documented above and delete the rows. Rows a run has already claimed or settled carry that run's lease instead, so filter those on `import_state` **is not** `pending`, or on the run's lease value. Deleting a staging row removes no entity record.
- **Clear the staged rows once a load has been reconciled.** Guide 06 already asks for this — see [`../docs/manual-build/06-staging-table-csv-import.md`](../docs/manual-build/06-staging-table-csv-import.md) — and doing it is what keeps the sample payloads from accumulating across runs. It is a list-view delete on `x_bst_startuptrk_ingest_staging`, filtered to the batch token or the run lease of the load being cleared, performed by an administrator holding `x_bst_startuptrk.admin`. Nothing in this delivery deletes a row on your behalf, and nothing expires one on a timer.
- **The designed defects are reproducible from the CSVs, not from the table.** The rejection, deduplication and unmatched-value cases documented above live in the six CSV files, which are version-controlled and are never modified by any load or job. Clearing the staged rows loses nothing: re-import the CSVs and every designed defect is back, identically.
- **This dataset is outside the live-activation register, and that is deliberate.** [the live-activation register](../docs/gaps-and-flags.md#the-live-activation-register) gates the moment **live** data first enters the instance; it does not gate loading, ingesting or validating these six files, because every value in them is synthetic. Read the register as a precondition on `source_mode` `live`, never as a reason to defer a fallback test.
- **Nothing in this folder is subject to an erasure request.** Every value in the six files is synthetic. The erasure procedure exists for the live path, which loads the same table from the same shape of data, and it is the operator's obligation 3 in the section linked above.
- **Live data reaches the same columns with the same posture.** An operator who does not want live upstream payloads retained must delete the settled rows as part of operating the flow. That is a delivered limitation and is inventoried in [`../docs/gaps-and-flags.md`](../docs/gaps-and-flags.md), not a defect of this dataset.

The load and clean-up procedure is [`../docs/manual-build/06-staging-table-csv-import.md`](../docs/manual-build/06-staging-table-csv-import.md); the table's posture column by column is in [`../docs/data-model.md`](../docs/data-model.md).

## Run provenance and criterion 4 evidence

Every row shipped in this folder carries `run_provenance` of `fallback`. A flow run that reads this dataset records the same provenance for the run as a whole, through **two** writes that happen at different moments and must not be confused. `IngestionLogger.writeRunSummary` publishes the run summary — through `gs.info`, prefixed `[x_bst_startuptrk.ingestion]` — carrying the run identifier, the provenance, and the processed, rejected, skipped, duplicate and unmatched counts, and it **writes no property**. `IngestionLogger.markRunComplete` then stamps the source system's marker inside `x_bst_startuptrk.ingestion.last_run_provenance` and reads it back, and it is called **only once every one of the run's final health checks has passed**. A run that completed a live call records `live` by the same path. The consequence is the one to rely on: **a marker in that property is evidence of a run that finished cleanly**, not merely of a run that started.

Prompt section 10.0 criterion 4 accepts the sample-dataset substitute for live ingestion, so three consecutive clean fallback runs of each flow satisfy it **provided the mode is recorded** for each run. The recording is itself part of the acceptance evidence: an Automated Test Framework result that exercised this dataset must be labelled **"fallback validated"**, and only a result from a successful live call may be labelled **"live validated"**, so the two can never be confused after the fact. **A result may carry the "live validated" label only when the flow's alias is provisioned and the run completed a live read**; otherwise the label is "fallback validated". That label is available to `Crunchbase Ingestion` only: **`LinkedIn Ingestion` can never be `live validated` in any posture**, because LinkedIn publishes no read API for founders, executives or job postings, so its three record types come from this dataset on every run. The limitation is a property of the provider rather than of an instance, and it is inventoried in [`../docs/gaps-and-flags.md`](../docs/gaps-and-flags.md). The labelling convention is applied by [`../docs/manual-build/05-atf-test-suites.md`](../docs/manual-build/05-atf-test-suites.md) and the evidence collected by [`../docs/validation-checklist.md`](../docs/validation-checklist.md).

For criterion 4 purposes a **scheduled run** means a flow execution that passed the flow's cadence guard and went on to do work. An execution that started, found the configured cadence had not yet elapsed and exited without ingesting is a no-op and does not count towards the three consecutive runs. That definition is stated here; how to distinguish the two in the execution log is specified under [What counts as a scheduled run](../docs/deployment-runbook.md#what-counts-as-a-scheduled-run) in [`../docs/deployment-runbook.md`](../docs/deployment-runbook.md).

## The three-way contract

Three artifacts describe the same set of staging columns, and all three must be changed together. Changing one alone breaks the fallback path without raising an error: the wizard leaves the renamed column unmapped, the field loads empty, and the transform produces incomplete records or rejects valid ones.

**All three legs are delivered.** Each row below names the evidence a reader can check directly, so the status is verifiable rather than asserted.

| Leg | Artifact | Role | Status | Evidence a reader can check |
| --- | --- | --- | --- | --- |
| a | The header rows of the six CSVs in this folder, documented above | The wire format | **Delivered** | Six header rows carrying **92** column positions between them — 19, 12, 16, 14, 14 and 17 — drawn from **41** distinct header names, above **65** data rows in total. Read the first line of each file. |
| b | The `x_bst_startuptrk_ingest_staging` dictionary records in [`../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml`](../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml) | **Authoritative** | **Delivered** | The `sys_dictionary` elements bundled inside the `x_bst_startuptrk_ingest_staging` table payload — **41** columns, one for every distinct CSV header name, with none left over on either side. |
| c | The field mapping in [`../docs/manual-build/06-staging-table-csv-import.md`](../docs/manual-build/06-staging-table-csv-import.md) | The load instructions | **Delivered** | Section [The field mapping, file by file](../docs/manual-build/06-staging-table-csv-import.md#the-field-mapping-file-by-file): six data sources, six import set tables, six transform maps and one target table, carrying **92** one-to-one field maps — one per column position of leg a, distributed 19, 12, 16, 14, 14 and 17. That guide states the same three-way contract in its own [three-way staging contract](../docs/manual-build/06-staging-table-csv-import.md#the-three-way-staging-contract) section. |

The three counts are the check: **92 = 92 = 92** across the legs, over 41 distinct column names, and a column present in one leg and absent from another is exactly the silent failure this table exists to prevent.

Leg b is authoritative over the other two legs, and the frozen prompt and the Agent Action Plan are authoritative over all three. Where this document and the dictionary disagree about a column name, type, length or choice value, the dictionary is checked against the prompt and the plan first. Where the dictionary matches the specification, this document is corrected to it. Where the dictionary departs from it, the dictionary is corrected.

Two groups of columns are load-bearing across all three legs:

- **Nine** staging columns are read by more than one record type, so the wizard maps each of them once per file according to that file's record type: `name`, `website`, `active`, `title`, `startup_name`, `startup_headquarters_location`, `bio`, `linkedin_url` and `contact_email`. `name` is the record's own name on a `startup`, `investor`, `founder` or `executive` row; `startup_name` and `startup_headquarters_location` are the **parent's** two identity halves on a `founder`, `executive`, `funding_round` or `job_posting` row. Mapping a child file's `startup_name` to `name`, or the reverse, silently detaches every child row from its parent; omitting `startup_headquarters_location` rejects every child row of that file, because the parent key is the pair.
- `participating_investor_names` carries a **JSON array**. The wizard must load it verbatim into the string column; nothing may re-format, re-quote, re-delimit or pretty-print it in transit — a transform that strips the brackets turns the whole array into one investor name. The mapper parses the array and trims each member.

**All three legs are delivered and in agreement.** Leg c is authored against legs a and b as they stand, and it honours one property of leg b in particular: `active` is a **String** column of length 10 carrying the text `true` or `false`, not a True/False column, and it carries no dictionary default. That is what lets a blank `active` survive the load and be rejected by cleaning rule 4 rather than being silently defaulted to `true`. Verify the agreement whenever any leg changes: the header rows here, the dictionary records in the Update Set, and guide 06's field-mapping table must name the same columns.

## Related documents

- [`../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml`](../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml) — the authoritative staging dictionary and the `IngestionMapper` and `IngestionLogger` records this contract depends on
- [`../docs/data-model.md`](../docs/data-model.md) — all ten tables field by field, including the staging table's full column list, the table access posture, and the operator-owned staging and counter retention procedure
- [`../docs/access-control.md`](../docs/access-control.md) — the three roles, the premium field ACL matrix, and the twelve supporting-table controls that make the staging table administrator-only on all four operations
- [`../docs/api-reference.md`](../docs/api-reference.md) — the six REST resources and the eleven system properties, including `ingestion.source_mode` and `ingestion.last_run_provenance`
- [`../docs/validation-gates.md`](../docs/validation-gates.md) — the post-commit gates that confirm the staging table's parent tables exist
- [`../README.md`](../README.md) — package index for the ServiceNow deliverable
- [`../docs/manual-build/06-staging-table-csv-import.md`](../docs/manual-build/06-staging-table-csv-import.md) — the detailed import and transform guide
- [`../docs/manual-build/01-connection-credential-aliases.md`](../docs/manual-build/01-connection-credential-aliases.md) — the two credential aliases the live path uses
- [`../docs/manual-build/02-flow-crunchbase-ingestion.md`](../docs/manual-build/02-flow-crunchbase-ingestion.md) — the Crunchbase ingestion flow
- [`../docs/manual-build/03-flow-linkedin-ingestion.md`](../docs/manual-build/03-flow-linkedin-ingestion.md) — the LinkedIn ingestion flow
- [`../docs/manual-build/05-atf-test-suites.md`](../docs/manual-build/05-atf-test-suites.md) — the test suites, including the provenance labelling
- [`../docs/validation-checklist.md`](../docs/validation-checklist.md) — the success criteria and their evidence
- [`../docs/gaps-and-flags.md`](../docs/gaps-and-flags.md) — requirements with no clean platform equivalent
- [`../docs/deployment-runbook.md`](../docs/deployment-runbook.md) — import sequence, gates and rollback
- [`../../docs/decisions/DECISION_LOG.md`](../../docs/decisions/DECISION_LOG.md) — the single source of truth for every decision, alternative and risk behind this contract

