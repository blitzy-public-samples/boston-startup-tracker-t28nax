# Manual build 06 — Staging-table CSV import — `x_bst_startuptrk`

This guide loads the six fallback-dataset CSV files under [`../../sample-data/`](../../sample-data/) into the single staging table `x_bst_startuptrk_ingest_staging` of the ServiceNow scoped application `x_bst_startuptrk`, by hand, on the instance, through the Data Import Wizard and the System Import Sets modules. It specifies one data source, one import set table and one transform map **per record type** — six of each — every transform map targeting that one staging table. For each file it states every column, the target staging column it maps to, the coalesce key that makes a re-load update rather than duplicate, the choice action, the date format, the load position in the referential sequence, and the row count to expect. It then specifies the staging-to-entity transform, the post-load recalculation, how to read the run results, and the verification to perform before this guide is signed off.

**Authority.** The frozen prompt and the Agent Action Plan are authoritative for all application content. The Update Set XML at [`../../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml`](../../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml) is the authoritative source for every table name, column name, column type, column length, choice value, Script Include class name, method name and system-property key cited below; the identifiers used here match those records character for character. [`../../sample-data/README.md`](../../sample-data/README.md) is authoritative for the CSV header rows and their order within each file. This guide agrees with both and introduces no third spelling and no different order. No variant spelling of any identifier is valid.

This document carries **no rationale**. It states what to load and how to load it. Every decision behind this procedure, every alternative considered and every risk it carries is recorded in [`../../../docs/decisions/DECISION_LOG.md`](../../../docs/decisions/DECISION_LOG.md), which is the single source of truth for "why". Three points in this procedure depart from a literal reading of the requirements — the **single** staging table serving all six record types, the shape that carries **both** flattened scalar columns and a `raw_payload` JSON column on the same row, and references expressed as **natural keys** rather than record identifiers. Each is stated below as a load mechanic and cross-referenced to that log. None is argued here.

Operational warnings **are** in scope for this guide and are marked as such. The five warnings under [Operational warnings](#operational-warnings) are load-bearing and must not be skipped: three of them describe failures that are completely silent, in the sense that the load reports success and the defect surfaces later somewhere else.

## Referenced documents

This guide is executable on its own. Every data source, every import set table, every transform map, every field map, the load order, the transform, the recalculation and the verification are stated here in full. An operator needs no other file to perform the load.

**Every document linked from this guide is delivered and readable**, so no link is a forward reference; each one is an in-scope artifact of this deliverable package. Nothing in this guide depends on reading another document first.

| Document | What this guide takes from it |
| --- | --- |
| [`../../sample-data/README.md`](../../sample-data/README.md) | **Leg (a)** of the three-way contract: the authoritative CSV header rows and their order, the per-file `import_run` values, the value conventions, the row counts and the designed-defect inventory. |
| [`../../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml`](../../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml) | **Leg (b)**, and **authoritative** for every identifier this guide cites, including all forty staging column names. |
| [`../data-model.md`](../data-model.md) | The staging table's full column list with types and lengths, the entity choice values, the cascade rules, and the `Investor.portfolio_count` derivation and its `recalculateAll()` contract. |
| [`../validation-gates.md`](../validation-gates.md) | The post-commit gates of precondition 4, including the eleven-gate core, and `GATE-SEC-02`, which is why the staged rows are verified in the list view rather than over the Table API. |
| [`02-flow-crunchbase-ingestion.md`](02-flow-crunchbase-ingestion.md) | The Crunchbase ingestion flow, whose fallback branch reads the `crunchbase` rows this guide loads. |
| [`03-flow-linkedin-ingestion.md`](03-flow-linkedin-ingestion.md) | The LinkedIn ingestion flow, whose fallback branch reads the `linkedin` rows this guide loads. |
| [`05-atf-test-suites.md`](05-atf-test-suites.md) | The two flow tests that depend on this data, and the `fallback validated` result label they apply. |
| [`../manual-build-instructions.md`](../manual-build-instructions.md) | The build order for the package as a whole, and the split rule between Update Set XML and manual build. |
| [`../validation-checklist.md`](../validation-checklist.md) | Success criterion 4 and its provenance evidence, which the loaded rows supply. |
| [`../access-control.md`](../access-control.md) | The role posture of the staging table, which grants read, write, create and delete to `x_bst_startuptrk.admin` alone. |
| [`../api-reference.md`](../api-reference.md) | The Script Include call graph and the full system-property inventory. |
| [`../deployment-runbook.md`](../deployment-runbook.md) | The import sequence that commits the Update Set, and the definition of [what counts as a scheduled run](../deployment-runbook.md#what-counts-as-a-scheduled-run). |
| [`../gaps-and-flags.md`](../gaps-and-flags.md) | The requirements with no clean platform equivalent, including the NewsArticle ingestion exclusion. |
| [`../../../docs/decisions/DECISION_LOG.md`](../../../docs/decisions/DECISION_LOG.md) | The single destination for every "why". |

## Position in the build order

This is **guide 06 of six**, and it is **step 5** of the execution order below. The execution order is **not** the filename order: guide **06** runs before guide **05**. Guide 04 precedes this one; guide 05 follows it, last. The order is stated in full in [`../manual-build-instructions.md`](../manual-build-instructions.md); it is repeated here so this guide can be run without it.

| Step | Guide | Why it sits here |
| --- | --- | --- |
| 1 | [`01-connection-credential-aliases.md`](01-connection-credential-aliases.md) | The two Connection and Credential Aliases the ingestion flows bind to by name. Nothing downstream can authenticate without them. |
| 2 | [`02-flow-crunchbase-ingestion.md`](02-flow-crunchbase-ingestion.md) | The Crunchbase ingestion flow, which references `x_bst_startuptrk.crunchbase_api` by name. |
| 3 | [`03-flow-linkedin-ingestion.md`](03-flow-linkedin-ingestion.md) | The LinkedIn ingestion flow, which references `x_bst_startuptrk.linkedin_oauth` by name. |
| 4 | [`04-service-portal-pages-and-widgets.md`](04-service-portal-pages-and-widgets.md) | The portal, theme, five pages and eight widgets. |
| **5** | **This guide** | **The staging-table CSV load, which puts rows into `x_bst_startuptrk_ingest_staging` and records on the instance for the portal walkthrough.** |
| 6 | [`05-atf-test-suites.md`](05-atf-test-suites.md) | The Automated Test Framework suites, **last**, because they exercise everything the five preceding guides build. |

The single hop where execution order differs from filename order is this one, and the dependency that fixes it is factual: the two ingestion flows read `x_bst_startuptrk_ingest_staging` on their fallback branch, and the flow tests in guide 05 exercise that branch. **The staging data must exist before guide 05 runs**, or those tests have no rows to act on. Guides 02 and 03 are built before this guide and their fallback branch returns a row count of zero until this guide has run; both guides state that and require the fallback branch to be re-run afterwards.

## Preconditions

Do not begin this guide until every item below holds.

| # | Precondition | How to confirm |
| --- | --- | --- |
| 1 | The Update Set has been uploaded and has reached the `loaded` state. | The `sys_remote_update_set` record shows `state` `loaded`. |
| 2 | The preview has completed with an **empty error-type problem set**. | A read of `sys_update_preview_problem` filtered to this remote update set and `type=error` returns an empty `result` array. Warnings are logged and do not block. |
| 3 | The Update Set has **committed**. | The `sys_remote_update_set` record shows `state` `committed`. |
| 4 | **All eleven post-commit gates of the core gate set have passed.** | The seven entity-table gates `GATE-TBL-01` through `GATE-TBL-07`, the three role-record gates `GATE-ROLE-01` through `GATE-ROLE-03`, and the one scope-record gate `GATE-SCOPE-01`, all recorded `pass` in [`../validation-gates.md`](../validation-gates.md). That document carries sixteen gates in total; these eleven are its core, and the remaining five are `GATE-COL-01` and `GATE-SEC-01` through `GATE-SEC-04`. There is no partial pass. |
| 5 | `x_bst_startuptrk_ingest_staging` exists with all **forty** of its dictionary columns. | The table opens in the list view through the **Ingestion staging** module of the Boston Startup Tracker application menu, and `sys_dictionary` filtered to `name=x_bst_startuptrk_ingest_staging` with a non-empty `element` returns 40 records. |
| 6 | The two tables the staging-to-entity transform writes for participation exist. | `x_bst_startuptrk_fundinground` and `x_bst_startuptrk_m2m_round_investor` both open in the list view. `GATE-TBL-05` covers the first. |
| 7 | The three Script Includes this guide calls into are on the instance. | `sys_script_include` carries `IngestionMapper`, `IngestionLogger` and `InvestorPortfolioService`, all in the `x_bst_startuptrk` scope. |
| 8 | The three business rules that maintain the derived columns are on the instance and **active**. | `sys_script` carries `Trim and validate startup`, `Recalculate investor portfolio on funding round` and `Recalculate investor portfolio on round investor link`, all `active` true, all in the `x_bst_startuptrk` scope. |
| 9 | You hold the `x_bst_startuptrk.admin` role. | The staging table grants read, write, create and delete to that role **alone**, so this procedure cannot be performed by a caller holding only `x_bst_startuptrk.user` or `x_bst_startuptrk.premium_user`. The posture is Layer 4 of [`../access-control.md`](../access-control.md). |
| 10 | You hold the platform `admin` role and can reach the System Import Sets module. | The application navigator opens **System Import Sets**, with **Load Data**, **Run Transform** and the **Administration** submodules **Data Sources**, **Transform Maps** and **Import Log** all visible. Creating a data source, an import set table and a transform map requires that role. |
| 11 | You are working in the `x_bst_startuptrk` application scope. | The application picker reads **Boston Startup Tracker**. Every data source, import set table and transform map this guide creates must carry that scope. |
| 12 | The six CSV files are available locally. | `crunchbase_startups_sample.csv`, `crunchbase_investors_sample.csv`, `crunchbase_funding_rounds_sample.csv`, `linkedin_founders_sample.csv`, `linkedin_executives_sample.csv` and `linkedin_job_postings_sample.csv`, taken from [`../../sample-data/`](../../sample-data/) **unmodified**. |

Guides 01 through 04 do not have to be complete before this guide runs. Nothing in the load path touches a credential alias, a flow or a portal record. Guides 02 and 03 do have to be complete before the loaded rows can be exercised through a flow, and guide 04 before they can be seen in the portal.

### Why this guide exists rather than more Update Set XML

Only tables carrying the update-synch attribute are captured into `sys_update_xml` records, and adding that attribute to a table that lacks it out of the box is unsupported. A data source, an import set table, a transform map and its field maps are all built through the platform's own interface and sit outside the captured set, which is why the delivered Update Set contains **zero** import records — no `sys_data_source`, no `sys_transform_map` and no `sys_transform_entry`. [`../manual-build-instructions.md`](../manual-build-instructions.md) owns the split rule for the package as a whole.

## What this guide builds

| Artifact | Count | Table | Notes |
| --- | --- | --- | --- |
| Data source | 6 | `sys_data_source` | One per CSV file. Type **File**, format **CSV**, file retrieval method **Attachment**. |
| Import set table | 6 | one per data source, extending `sys_import_set_row` | One per record type. The wizard derives its columns from that file's header row, and the six files carry six different header sets. |
| Transform map | 6 | `sys_transform_map` | One per record type. Source is that record type's import set table; **target is `x_bst_startuptrk_ingest_staging` on all six**. |
| Field map | 19, 12, 15, 13, 13, 16 | `sys_transform_entry` | One per CSV column per map: 88 field maps in total, every one a one-to-one mapping by header name. |
| Import set | 6 | `sys_import_set` | One per load. Created by the load, not by hand. |
| Background script | 1 | not a stored record | The post-load `InvestorPortfolioService.recalculateAll()` invocation of [step 9](#step-9--recalculate-the-derived-portfolio-counts). |

The load writes **one** application table, `x_bst_startuptrk_ingest_staging`, and no other. The staging-to-entity transform of [step 8](#step-8--run-the-staging-to-entity-transform) writes the six entity tables and the one join table, through `IngestionMapper`.

## The three-way staging contract

Three artifacts describe the same set of staging columns. This guide is **leg (c)**.

| Leg | Artifact | Role | Present today |
| --- | --- | --- | --- |
| a | The header rows of the six CSVs, stated in [`../../sample-data/README.md`](../../sample-data/README.md) | The wire format | Yes |
| b | The `x_bst_startuptrk_ingest_staging` dictionary records in [`../../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml`](../../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml) | **Authoritative for column names** | Yes |
| c | The field mapping in **this guide** | The load instructions | Yes |

**Precedence.** The Update Set dictionary is authoritative for column names, types and lengths. [`../../sample-data/README.md`](../../sample-data/README.md) is authoritative for the CSV header rows and their order within each file. This guide must agree with both, and must not introduce a third spelling or a different order. Where this guide and the dictionary disagree, the dictionary is checked against the prompt and the Agent Action Plan first: where the dictionary matches the specification, this guide is corrected to it; where the dictionary departs from it, the dictionary is corrected.

**Operational warning.** A change to any one leg alone breaks the fallback path **silently**. The Data Import Wizard maps columns **by header name**: a renamed, re-cased or misspelled column is left unmapped, the target field loads empty, and **no error is raised** — the load reports success, the row count is correct, and the flows simply find nothing usable in that column. Whenever any one leg changes, re-verify all three: the CSV header row, the dictionary element name, and the field map in this guide. The check is mechanical — read the header row of the file, read `sys_dictionary` for the table, and read the Field Maps related list on the transform map, and confirm the three lists agree name for name.

## The target table

**One** table. Label **Ingestion staging**, name `x_bst_startuptrk_ingest_staging`, display column `import_run`, forty columns: the seven-column control prefix plus thirty-three flattened scalar columns. All six record types load into it; `record_type` is the discriminator that tells the staging-to-entity transform which entity table a row becomes and which flattened columns it reads. The full column list with every type and length is in [`../data-model.md`](../data-model.md).

Four properties of the table govern this procedure:

| Property | Value | Consequence for the load |
| --- | --- | --- |
| Mandatory columns | **None** | A row with a blank value loads successfully. The mandatory requirement is enforced per record type at transform time by cleaning rule 4, not at import time. |
| Choice lists | On the four control columns `source_system`, `record_type`, `import_state` and `run_provenance` only | None of the thirty-three flattened columns carries a choice list, so an unmatched choice value loads unchanged and is normalised later by cleaning rule 3. |
| `sys_db_object.access` | `package_private` | The table is unreachable from any other application scope. A background script that touches it must run **inside** the `x_bst_startuptrk` scope. |
| `sys_db_object.ws_access` | `false` | The table is **not** served at `/api/now/table/x_bst_startuptrk_ingest_staging`. Verify the load in the list view; a script written against that path fails whether or not the rows loaded. `GATE-SEC-02` asserts this posture across all ten application tables. |

One table serving six record types is a deviation from a literal reading of the requirements. It is stated here as a load mechanic; the decision is recorded in [`../../../docs/decisions/DECISION_LOG.md`](../../../docs/decisions/DECISION_LOG.md).

## The shared control prefix

Seven columns, present on every row of every one of the six files, in **this exact order** — the leg-(a) order, which is the order the header row of each file uses:

```text
source_system,record_type,import_run,import_state,run_provenance,error_message,raw_payload
```

| # | Column | Platform type | Length | Choice values | Value in the shipped rows |
| --- | --- | --- | --- | --- | --- |
| 1 | `source_system` | `string`, choice list | 40 | `crunchbase`, `linkedin` | Constant per file. `crunchbase` on the three `crunchbase_*` files, `linkedin` on the three `linkedin_*` files. It is the column each ingestion flow filters its fallback query on. |
| 2 | `record_type` | `string`, choice list | 40 | `startup`, `founder`, `executive`, `investor`, `funding_round`, `job_posting` | Constant per file, one value per file. The discriminator for the staging-to-entity transform. There is **no** `news_article` member. |
| 3 | `import_run` | `string` | 64 | — | Constant per file, a stable synthetic token that makes one load traceable end to end. The six values are tabulated below. This is the table's display column. |
| 4 | `import_state` | `string`, choice list, dictionary default `pending` | 40 | `pending`, `processed`, `rejected`, `error` | **`pending` on every shipped row.** The transform advances it. |
| 5 | `run_provenance` | `string`, choice list | 40 | `live`, `fallback` | **`fallback` on every shipped row.** No shipped row carries `live`. |
| 6 | `error_message` | `string` | 1000 | — | **Empty on every shipped row.** Written by `IngestionMapper.writeStagingState()` when a row is rejected or errors. |
| 7 | `raw_payload` | `string` | 8000 | — | A JSON object in the source system's own key vocabulary. Loaded verbatim. |

The `import_run` value per file, exactly as the CSVs carry it:

| File | `import_run` |
| --- | --- |
| `crunchbase_startups_sample.csv` | `fallback-sample-crunchbase-startups` |
| `crunchbase_investors_sample.csv` | `fallback-sample-crunchbase-investors` |
| `crunchbase_funding_rounds_sample.csv` | `fallback-sample-crunchbase-funding-rounds` |
| `linkedin_founders_sample.csv` | `fallback-sample-linkedin-founders` |
| `linkedin_executives_sample.csv` | `fallback-sample-linkedin-executives` |
| `linkedin_job_postings_sample.csv` | `fallback-sample-linkedin-job-postings` |

Do not edit these values, and do not invent a new one for a re-load. `import_run` is part of the coalesce key of every transform map, so changing it turns a re-load into a second set of rows instead of an update of the first.

## Value conventions

Every one of the six files honours all of these. They are stated in full in [`../../sample-data/README.md`](../../sample-data/README.md) and restated here because the field maps depend on them.

| Convention | Rule | Example |
| --- | --- | --- |
| Dates | **ISO 8601 `YYYY-MM-DD`**, zero-padded, no time component, no timezone and no offset. Both date columns, `round_date` and `posted_date`, are `glide_date`, and their field maps carry the date format `yyyy-MM-dd`. | `2024-03-07` |
| Currency | **Plain unformatted United States dollars**: digits only with an optional single decimal point. No thousands separator, no currency symbol, no `M` or `K` magnitude suffix. The column names fix the denomination as USD. The four money columns are `decimal` on staging and `currency` on the entity tables. | `42500000` or `42500000.50` |
| Booleans | **Lowercase `true` or `false` only.** Never `TRUE`, `True`, `1`, `0`, `yes`, `no`, `Y` or `N`. | `true` |
| Multi-valued fields | Comma separated inside **one RFC 4180 double-quoted field**, a bare comma between values with **no** space after it. Two columns are multi-valued: `focus_areas` and `participating_investor_names`. | `"Fintech,SaaS,Deeptech"` |
| Integers | Digits only, unquoted, no separators. One column: `founded_year`. | `2019` |
| URLs | Absolute, including the scheme. | `https://example.com/careers` |
| Empty means absent | An empty field means the value is absent. **No sentinel string is ever used** — `Unknown`, `N/A`, `null` and `None` appear nowhere in these files and must not be introduced. A blank must stay blank through the load so cleaning rule 4 can see it. | `,,` |

The CSV dialect the six files are written in, and which the data sources must be configured to read: RFC 4180; comma field delimiter; double-quote quoting character; a literal double quote inside a quoted field escaped by doubling it; UTF-8 **without** a byte-order mark; LF line endings; exactly one header row, the first line of the file; no comment syntax.

### `raw_payload`

`raw_payload` is a JSON object carried as one double-quoted CSV field with every inner double quote doubled. It uses the **source system's own key vocabulary**, not the flattened platform column names, because the staging shape is required to mimic the expected API response. **Load it verbatim.** Do not reformat it, do not re-indent it, do not re-quote it and do not parse and re-serialise it; the field map is a plain string-to-string mapping.

| Source | Files | Payload shape |
| --- | --- | --- |
| Crunchbase organisation reads | `crunchbase_startups_sample.csv`, `crunchbase_investors_sample.csv` | `data.properties` |
| Crunchbase funding-round reads | `crunchbase_funding_rounds_sample.csv` | `data.items` |
| LinkedIn company, employee and job reads | `linkedin_founders_sample.csv`, `linkedin_executives_sample.csv`, `linkedin_job_postings_sample.csv` | `data.elements` |

The longest shipped `raw_payload` value is well inside the column's 8000-character limit, so no value is at risk of truncation on load. Every shipped value parses as JSON.

Carrying **both** the flattened scalar columns and this source-vocabulary JSON column on the same row is a deviation from a literal reading of the requirements: the flattened columns are what make the CSV import a one-to-one mapping by header name, and `raw_payload` is what preserves the source response shape. Both are mapped, on every row of every file. The mechanic is stated here; the decision is recorded in [`../../../docs/decisions/DECISION_LOG.md`](../../../docs/decisions/DECISION_LOG.md).

## References travel as natural keys

A CSV cannot carry a `sys_id` for a record that does not exist yet, so **every reference travels as the target record's natural key — its `name` value — and no column in any of the six files carries a `sys_id`.** Three columns are natural keys:

| Column | Files that carry it | Resolves to | Written to |
| --- | --- | --- | --- |
| `startup_name` | `crunchbase_funding_rounds_sample.csv`, `linkedin_founders_sample.csv`, `linkedin_executives_sample.csv`, `linkedin_job_postings_sample.csv` | One `x_bst_startuptrk_startup` record, matched on `name` | The `startup` reference on the child record. The name itself is not written to the child. |
| `lead_investor_name` | `crunchbase_funding_rounds_sample.csv` | One `x_bst_startuptrk_investor` record, matched on `name` | `x_bst_startuptrk_fundinground.lead_investor` |
| `participating_investor_names` | `crunchbase_funding_rounds_sample.csv` | One `x_bst_startuptrk_investor` record **per comma-separated member** | One `x_bst_startuptrk_m2m_round_investor` row per resolved member |

**The import maps these three columns as plain strings into the staging columns of the same names.** No resolution happens at import time. Resolution happens in the staging-to-entity transform, in `IngestionMapper`, and this is what it does:

| Column | Resolution | When nothing matches |
| --- | --- | --- |
| `startup_name` | `IngestionMapper.resolveStartup()` matches the value against `x_bst_startuptrk_startup.name`, trimming and lowering both sides, and resolves **only when exactly one** startup carries the name. | The row is **rejected** and logged as a skip, and **no entity record is created**. The reason recorded is `no startup carries the name` when nothing matches, or `the name is ambiguous across <n> startups` when more than one does — and in the ambiguous case **no candidate is chosen**. `startup` is a mandatory value on all four child record types, so an unresolved parent is always a rejection. |
| `lead_investor_name` | `IngestionMapper.resolveInvestor()`, on the same exactly-one-match policy against `x_bst_startuptrk_investor.name`. | The reference is **left unwritten** and a warning is logged naming the reason. **The funding round is still created**, without a lead investor. The value is not written as a blank, because an ingestion run never clears a stored value. |
| Each member of `participating_investor_names` | `IngestionMapper.resolveParticipants()` splits the field on the comma, trims each member, drops an empty member, resolves each remaining member to exactly one Investor and keeps a repeated member once. | An unresolved member is logged as a warning naming the reason and **contributes no join row**. The members that do resolve still become join rows. |

**A natural key is never read as a record identifier.** A value that happens to be 32 hexadecimal characters is still matched against the `name` column, so it resolves only if a record is genuinely named that. Supplying a `sys_id` in one of these columns is a data error the transform reports, not a shortcut it honours.

Both sides of every comparison are trimmed and lowered, so a child row may spell its natural key in any case and with any surrounding whitespace. Several shipped rows deliberately do, which is what makes them evidence that trimming happens before resolution.

The natural-key shape is a deviation from a literal reading of the requirements. It is stated here as a load mechanic; the decision is recorded in [`../../../docs/decisions/DECISION_LOG.md`](../../../docs/decisions/DECISION_LOG.md).

## The field mapping, file by file

Six data sources, six import set tables, six transform maps, and **one** target table on all six. Every field map is a one-to-one mapping by header name: the source field is the import set column the wizard derived from the CSV header, and the target field is the staging dictionary element of the same name. There is no computed field map, no source script and no reference qualifier anywhere in this procedure.

### Common transform-map settings

Set these on all six `sys_transform_map` records. Only the **Name** and **Source table** differ between them.

| Field | Value | Effect on the load |
| --- | --- | --- |
| Name | Per the table in [step 3](#step-3--create-the-transform-map) | — |
| Source table | That record type's import set table | — |
| **Target table** | **`x_bst_startuptrk_ingest_staging`** | The same on all six maps. |
| Active | true | — |
| Order | `100` | One map per source table, so relative order never arises. |
| **Run business rules** | **true** | The staging table carries no business rule, so this setting changes nothing during the import itself. Leave it true so the setting is never confused with the entity-write path, where suppressing rules is a defect. See [Operational warnings](#operational-warnings). |
| Enforce mandatory fields | **No** | The staging dictionary marks **no** column mandatory. Enforcing here would reject the twelve deliberate blank-mandatory fixture rows at the wrong layer; rule 4 must see them. |
| **Copy empty fields** | **true** | An empty CSV field is written as empty to the staging column, so a blank stays blank on both an insert and a coalesce update, and the staged row mirrors the file exactly. This is what lets cleaning rule 4 observe an absent mandatory value. |
| Run script | false | No `onBefore`, `onAfter`, `onStart` or `onComplete` script is used. The transform map is declarative. |

### Common field-map settings

| Field-map setting | Where it applies | Value |
| --- | --- | --- |
| **Choice action** | The four control columns `source_system`, `record_type`, `import_state` and `run_provenance` — the only staging columns carrying a choice list | **`reject`**. An out-of-list value in a control column is a data error: rejecting the row keeps it out of the table and out of the flows. `create` must **not** be used, because it would add a `sys_choice` record and mutate a choice inventory the prompt declares binding and complete. |
| Choice action | The thirty-three flattened columns | Not applicable. None of them carries a choice list. |
| **Date format** | `round_date` and `posted_date` | **`yyyy-MM-dd`**, matching the ISO 8601 form the files use. |
| Coalesce | The columns named in [The coalesce key per record type](#the-coalesce-key-per-record-type) | `true` on exactly those columns of that map, `false` on every other field map. |
| Use source script | Every field map | `false`. |

### 1. `crunchbase_startups_sample.csv`

`source_system` is `crunchbase` and `record_type` is `startup` on every row. **Nineteen** columns: the seven-column control prefix plus twelve flattened columns. **13** data rows.

```text
source_system,record_type,import_run,import_state,run_provenance,error_message,raw_payload,name,description,industry,founded_year,headquarters_location,website,logo_url,funding_stage,total_funding_usd,active,institutional_funding_last_5yrs,employee_count_range
```

| # | CSV column | Target staging column | Staging type and length | Coalesce | Notes |
| --- | --- | --- | --- | --- | --- |
| 1 | `source_system` | `source_system` | `string` 40, choice | no | Constant `crunchbase`. Choice action `reject`. |
| 2 | `record_type` | `record_type` | `string` 40, choice | no | Constant `startup`. Choice action `reject`. |
| 3 | `import_run` | `import_run` | `string` 64 | **yes** | Constant `fallback-sample-crunchbase-startups`. |
| 4 | `import_state` | `import_state` | `string` 40, choice | no | Constant `pending`. Choice action `reject`. |
| 5 | `run_provenance` | `run_provenance` | `string` 40, choice | no | Constant `fallback`. Choice action `reject`. |
| 6 | `error_message` | `error_message` | `string` 1000 | no | Empty on every row. |
| 7 | `raw_payload` | `raw_payload` | `string` 8000 | no | JSON in the `data.properties` shape. Verbatim. |
| 8 | `name` | `name` | `string` 100 | **yes** | Writes `x_bst_startuptrk_startup.name`. First half of the cleaning-rule-2 deduplication key. |
| 9 | `description` | `description` | `string` 4000 | no | Writes `x_bst_startuptrk_startup.description`. |
| 10 | `industry` | `industry` | `string` 40 | no | Target choice list `Fintech`, `Healthtech`, `SaaS`, `Consumer`, `Deeptech`, `Other`. Normalised at transform time, not here. |
| 11 | `founded_year` | `founded_year` | `integer` | no | Four-digit year. |
| 12 | `headquarters_location` | `headquarters_location` | `string` 100 | **yes** | Writes `x_bst_startuptrk_startup.headquarters_location`. Second half of the deduplication key. This column is read by the `startup` record type only; no child file carries it. |
| 13 | `website` | `website` | `string` 255 | **yes** | Writes `x_bst_startuptrk_startup.website`. |
| 14 | `logo_url` | `logo_url` | `string` 255 | no | Writes `x_bst_startuptrk_startup.logo_url`. |
| 15 | `funding_stage` | `funding_stage` | `string` 40 | no | Target choice list `Pre-Seed`, `Seed`, `Series A`, `Series B`, `Series C+`, `Growth`, `Public`, `Acquired`. |
| 16 | `total_funding_usd` | `total_funding_usd` | `decimal` | no | Plain USD. Premium-gated on the entity record. |
| 17 | `active` | `active` | `string` **10** | no | Carries the text `true` or `false`. A **string** column with **no** dictionary default — see [Operational warnings](#operational-warnings). Mandatory for this record type at transform time. |
| 18 | `institutional_funding_last_5yrs` | `institutional_funding_last_5yrs` | `boolean`, default `false` | no | `true` or `false`. Premium-gated on the entity record. |
| 19 | `employee_count_range` | `employee_count_range` | `string` 20 | no | Target choice list `1-10`, `11-50`, `51-200`, `201-500`, `500+`. |

Three columns are mandatory for the `startup` record type at transform time: `name`, `headquarters_location` and `active`. Three of the thirteen rows deliberately blank one or more of them, and one further row deliberately repeats an earlier row's `name` plus `headquarters_location` pair while differing on `website`. **Nine** Startup records result. Do not attempt to correct either fixture; see [This guide stages raw rows; the flows clean them](#this-guide-stages-raw-rows-the-flows-clean-them).

### 2. `crunchbase_investors_sample.csv`

`source_system` is `crunchbase` and `record_type` is `investor` on every row. **Twelve** columns: the seven-column control prefix plus five flattened columns. **8** data rows.

```text
source_system,record_type,import_run,import_state,run_provenance,error_message,raw_payload,name,type,focus_areas,website,aum_usd
```

| # | CSV column | Target staging column | Staging type and length | Coalesce | Notes |
| --- | --- | --- | --- | --- | --- |
| 1 | `source_system` | `source_system` | `string` 40, choice | no | Constant `crunchbase`. Choice action `reject`. |
| 2 | `record_type` | `record_type` | `string` 40, choice | no | Constant `investor`. Choice action `reject`. |
| 3 | `import_run` | `import_run` | `string` 64 | **yes** | Constant `fallback-sample-crunchbase-investors`. |
| 4 | `import_state` | `import_state` | `string` 40, choice | no | Constant `pending`. Choice action `reject`. |
| 5 | `run_provenance` | `run_provenance` | `string` 40, choice | no | Constant `fallback`. Choice action `reject`. |
| 6 | `error_message` | `error_message` | `string` 1000 | no | Empty on every row. |
| 7 | `raw_payload` | `raw_payload` | `string` 8000 | no | JSON in the `data.properties` shape. Verbatim. |
| 8 | `name` | `name` | `string` 100 | **yes** | Writes `x_bst_startuptrk_investor.name`. The only mandatory value for this record type, and the natural key `lead_investor_name` and `participating_investor_names` resolve against. |
| 9 | `type` | `type` | `string` 30 | no | Target choice list `VC`, `Angel`, `PE`, `Corporate`, `Accelerator`. |
| 10 | `focus_areas` | `focus_areas` | `string` 255 | no | Multi-valued: comma separated inside one quoted field, each member one of the six `Startup.industry` values. Load verbatim; the transform normalises member by member. |
| 11 | `website` | `website` | `string` 255 | **yes** | Writes `x_bst_startuptrk_investor.website`. |
| 12 | `aum_usd` | `aum_usd` | `decimal` | no | Plain USD. Premium-gated on the entity record. |

**`portfolio_count` is deliberately absent from this file, from the staging dictionary and from every field map in this guide.** `x_bst_startuptrk_investor.portfolio_count` is calculated, not imported: it is derived by `InvestorPortfolioService` and maintained by the two portfolio business rules. The column is read-only in the dictionary, so a field map that targeted it would be refused. Its value is established by [step 9](#step-9--recalculate-the-derived-portfolio-counts).

**The `Investor.type` choice list has no `Other` member.** Its five values are `VC`, `Angel`, `PE`, `Corporate` and `Accelerator`, and one shipped row deliberately carries a sixth value that matches none of them. Because the list offers no `Other` to normalise to, that value is **logged and the field left unwritten** — it is not coerced. The record is still created; an unwritten choice column is not a rejection. Do **not** add an `Other` choice to this list. Five other choice lists behave the same way: `Startup.funding_stage`, `Startup.employee_count_range`, `FundingRound.round_type`, `JobPosting.remote_type` and `JobPosting.seniority`.

One of the eight rows deliberately blanks `name`. **Seven** Investor records result.

### 3. `crunchbase_funding_rounds_sample.csv`

`source_system` is `crunchbase` and `record_type` is `funding_round` on every row. **Fifteen** columns: the seven-column control prefix plus eight flattened columns. **12** data rows.

```text
source_system,record_type,import_run,import_state,run_provenance,error_message,raw_payload,startup_name,round_type,amount_usd,valuation_usd,round_date,lead_investor_name,participating_investor_names,source_url
```

| # | CSV column | Target staging column | Staging type and length | Coalesce | Notes |
| --- | --- | --- | --- | --- | --- |
| 1 | `source_system` | `source_system` | `string` 40, choice | no | Constant `crunchbase`. Choice action `reject`. |
| 2 | `record_type` | `record_type` | `string` 40, choice | no | Constant `funding_round`. Choice action `reject`. |
| 3 | `import_run` | `import_run` | `string` 64 | **yes** | Constant `fallback-sample-crunchbase-funding-rounds`. |
| 4 | `import_state` | `import_state` | `string` 40, choice | no | Constant `pending`. Choice action `reject`. |
| 5 | `run_provenance` | `run_provenance` | `string` 40, choice | no | Constant `fallback`. Choice action `reject`. |
| 6 | `error_message` | `error_message` | `string` 1000 | no | Empty on every row. |
| 7 | `raw_payload` | `raw_payload` | `string` 8000 | no | JSON in the `data.items` shape. Verbatim. |
| 8 | `startup_name` | `startup_name` | `string` 100 | **yes** | **Natural key.** Resolves to `x_bst_startuptrk_fundinground.startup`. Mandatory for this record type at transform time. |
| 9 | `round_type` | `round_type` | `string` 40 | **yes** | Target choice list `Pre-Seed`, `Seed`, `Series A`, `Series B`, `Series C+`, `Growth`, `Public`, `Acquired`. The same eight values as `Startup.funding_stage`, and no `Other` member. |
| 10 | `amount_usd` | `amount_usd` | `decimal` | no | Plain USD. Premium-gated on the entity record. |
| 11 | `valuation_usd` | `valuation_usd` | `decimal` | no | Plain USD. Premium-gated on the entity record. |
| 12 | `round_date` | `round_date` | `glide_date` | **yes** | ISO 8601 `YYYY-MM-DD`. Field-map date format `yyyy-MM-dd`. Mandatory for this record type at transform time. |
| 13 | `lead_investor_name` | `lead_investor_name` | `string` 100 | no | **Natural key.** Resolves to `x_bst_startuptrk_fundinground.lead_investor`, a first-class single reference. Optional. |
| 14 | `participating_investor_names` | `participating_investor_names` | `string` 1000 | no | **Multi-valued natural key.** Comma separated inside one quoted field, no space after the comma. Becomes one `x_bst_startuptrk_m2m_round_investor` row per resolved member. Optional; an empty field means no participants. Load the string **verbatim** — nothing may re-format, re-quote or re-delimit it in transit. |
| 15 | `source_url` | `source_url` | `string` 255 | no | Writes `x_bst_startuptrk_fundinground.source_url`. |

`lead_investor_name` and `participating_investor_names` are **distinct columns with distinct destinations**, and both must be mapped. The lead investor is a single reference column on the funding round; each participating investor becomes one row of the join table. An investor may legitimately appear in both columns on the same row. Neither is ever written to `x_bst_startuptrk_fundinground.participating_investors`, which is a read-only projection maintained by the business rule on the join table.

Two columns are mandatory for the `funding_round` record type at transform time: `startup_name` and `round_date`. Two of the twelve rows deliberately blank one each. **Ten** FundingRound records result, and **26** join rows across them. The largest single round links five participating investors.

### 4. `linkedin_founders_sample.csv`

`source_system` is `linkedin` and `record_type` is `founder` on every row. **Thirteen** columns: the seven-column control prefix plus six flattened columns. **10** data rows.

```text
source_system,record_type,import_run,import_state,run_provenance,error_message,raw_payload,name,startup_name,title,bio,linkedin_url,contact_email
```

| # | CSV column | Target staging column | Staging type and length | Coalesce | Notes |
| --- | --- | --- | --- | --- | --- |
| 1 | `source_system` | `source_system` | `string` 40, choice | no | Constant `linkedin`. Choice action `reject`. |
| 2 | `record_type` | `record_type` | `string` 40, choice | no | Constant `founder`. Choice action `reject`. |
| 3 | `import_run` | `import_run` | `string` 64 | **yes** | Constant `fallback-sample-linkedin-founders`. |
| 4 | `import_state` | `import_state` | `string` 40, choice | no | Constant `pending`. Choice action `reject`. |
| 5 | `run_provenance` | `run_provenance` | `string` 40, choice | no | Constant `fallback`. Choice action `reject`. |
| 6 | `error_message` | `error_message` | `string` 1000 | no | Empty on every row. |
| 7 | `raw_payload` | `raw_payload` | `string` 8000 | no | JSON in the `data.elements` shape. Verbatim. |
| 8 | `name` | `name` | `string` 100 | **yes** | Writes `x_bst_startuptrk_founder.name`. Mandatory for this record type at transform time. |
| 9 | `startup_name` | `startup_name` | `string` 100 | **yes** | **Natural key.** Resolves to `x_bst_startuptrk_founder.startup`. Mandatory for this record type at transform time. Do **not** map it to `name`; see [Operational warnings](#operational-warnings). |
| 10 | `title` | `title` | `string` 150 | no | Target choice list `CEO`, `CTO`, `COO`, `Co-Founder`, `Other`. |
| 11 | `bio` | `bio` | `string` 2000 | no | Writes `x_bst_startuptrk_founder.bio`. |
| 12 | `linkedin_url` | `linkedin_url` | `string` 255 | no | Writes `x_bst_startuptrk_founder.linkedin_url`. |
| 13 | `contact_email` | `contact_email` | `string` 100 | no | Premium-gated on the entity record. |

Two columns are mandatory for the `founder` record type at transform time: `name` and `startup_name`. Two of the ten rows deliberately blank one each. **Eight** Founder records result.

### 5. `linkedin_executives_sample.csv`

`source_system` is `linkedin` and `record_type` is `executive` on every row. **Thirteen** columns — **the same column set as `linkedin_founders_sample.csv`**, in the same order. **10** data rows. The one substantive difference is that **the `title` choice list differs**: the target here is `Executive.title`, not `Founder.title`.

```text
source_system,record_type,import_run,import_state,run_provenance,error_message,raw_payload,name,startup_name,title,bio,linkedin_url,contact_email
```

| # | CSV column | Target staging column | Staging type and length | Coalesce | Notes |
| --- | --- | --- | --- | --- | --- |
| 1 | `source_system` | `source_system` | `string` 40, choice | no | Constant `linkedin`. Choice action `reject`. |
| 2 | `record_type` | `record_type` | `string` 40, choice | no | Constant **`executive`**. Choice action `reject`. This is the discriminator that sends the row to `x_bst_startuptrk_executive` rather than `x_bst_startuptrk_founder`. |
| 3 | `import_run` | `import_run` | `string` 64 | **yes** | Constant `fallback-sample-linkedin-executives`. |
| 4 | `import_state` | `import_state` | `string` 40, choice | no | Constant `pending`. Choice action `reject`. |
| 5 | `run_provenance` | `run_provenance` | `string` 40, choice | no | Constant `fallback`. Choice action `reject`. |
| 6 | `error_message` | `error_message` | `string` 1000 | no | Empty on every row. |
| 7 | `raw_payload` | `raw_payload` | `string` 8000 | no | JSON in the `data.elements` shape. Verbatim. |
| 8 | `name` | `name` | `string` 100 | **yes** | Writes `x_bst_startuptrk_executive.name`. Mandatory for this record type at transform time. |
| 9 | `startup_name` | `startup_name` | `string` 100 | **yes** | **Natural key.** Resolves to `x_bst_startuptrk_executive.startup`. Mandatory for this record type at transform time. |
| 10 | `title` | `title` | `string` 150 | no | Target choice list **`CFO`, `VP Engineering`, `VP Sales`, `VP Marketing`, `Head of Product`, `Other`** — a different list from the founders file. |
| 11 | `bio` | `bio` | `string` 2000 | no | Writes `x_bst_startuptrk_executive.bio`. |
| 12 | `linkedin_url` | `linkedin_url` | `string` 255 | no | Writes `x_bst_startuptrk_executive.linkedin_url`. |
| 13 | `contact_email` | `contact_email` | `string` 100 | no | Premium-gated on the entity record. |

Founder and Executive are separate entity tables and separate record types, and they stay separate through the staging layer. `record_type` is the only thing that distinguishes these two files' rows once they are in the table, so an incorrect constant in that column sends every row of the file to the wrong entity table. **Eight** Executive records result.

### 6. `linkedin_job_postings_sample.csv`

`source_system` is `linkedin` and `record_type` is `job_posting` on every row. **Sixteen** columns: the seven-column control prefix plus nine flattened columns. **12** data rows.

```text
source_system,record_type,import_run,import_state,run_provenance,error_message,raw_payload,startup_name,title,department,location,remote_type,seniority,posted_date,url,active
```

| # | CSV column | Target staging column | Staging type and length | Coalesce | Notes |
| --- | --- | --- | --- | --- | --- |
| 1 | `source_system` | `source_system` | `string` 40, choice | no | Constant `linkedin`. Choice action `reject`. |
| 2 | `record_type` | `record_type` | `string` 40, choice | no | Constant `job_posting`. Choice action `reject`. |
| 3 | `import_run` | `import_run` | `string` 64 | **yes** | Constant `fallback-sample-linkedin-job-postings`. |
| 4 | `import_state` | `import_state` | `string` 40, choice | no | Constant `pending`. Choice action `reject`. |
| 5 | `run_provenance` | `run_provenance` | `string` 40, choice | no | Constant `fallback`. Choice action `reject`. |
| 6 | `error_message` | `error_message` | `string` 1000 | no | Empty on every row. |
| 7 | `raw_payload` | `raw_payload` | `string` 8000 | no | JSON in the `data.elements` shape. Verbatim. |
| 8 | `startup_name` | `startup_name` | `string` 100 | **yes** | **Natural key.** Resolves to `x_bst_startuptrk_jobposting.startup`. Mandatory for this record type at transform time. |
| 9 | `title` | `title` | `string` 150 | **yes** | Free text, **not** a choice column on this record type. Writes `x_bst_startuptrk_jobposting.title`. Mandatory for this record type at transform time. |
| 10 | `department` | `department` | `string` 40 | no | Target choice list `Engineering`, `Sales`, `Marketing`, `Product`, `Operations`, `Other`. |
| 11 | `location` | `location` | `string` 100 | no | Writes `x_bst_startuptrk_jobposting.location`. |
| 12 | `remote_type` | `remote_type` | `string` 20 | no | Target choice list `Onsite`, `Hybrid`, `Remote`. No `Other` member. |
| 13 | `seniority` | `seniority` | `string` 20 | no | Target choice list `Entry`, `Mid`, `Senior`, `Lead`, `Executive`. No `Other` member. |
| 14 | `posted_date` | `posted_date` | `glide_date` | no | ISO 8601 `YYYY-MM-DD`. Field-map date format `yyyy-MM-dd`. Optional. |
| 15 | `url` | `url` | `string` 255 | no | Writes `x_bst_startuptrk_jobposting.url`. |
| 16 | `active` | `active` | `string` **10** | no | Carries the text `true` or `false`. Optional here: a blank is left unset so the `x_bst_startuptrk_jobposting.active` dictionary default `true` applies. |

Two columns are mandatory for the `job_posting` record type at transform time: `startup_name` and `title`. Two of the twelve rows deliberately blank one each. **Ten** JobPosting records result.

### The coalesce key per record type

The coalesce columns make a **re-load update the existing staging row rather than insert a second one**. Set `Coalesce` to true on exactly the columns listed for that record type, and false on every other field map of that map. Where a map coalesces on more than one column, the platform matches on the combination.

| Record type | Coalesce columns | Rows the key must separate |
| --- | --- | --- |
| `startup` | `import_run` + `name` + `headquarters_location` + `website` | 13 |
| `investor` | `import_run` + `name` + `website` | 8 |
| `funding_round` | `import_run` + `startup_name` + `round_date` + `round_type` | 12 |
| `founder` | `import_run` + `name` + `startup_name` | 10 |
| `executive` | `import_run` + `name` + `startup_name` | 10 |
| `job_posting` | `import_run` + `startup_name` + `title` | 12 |

Two properties of these keys are load-bearing and must survive any edit to them.

**`import_run` is in every key.** All six files load into one table, and five columns — `name`, `website`, `active`, `title` and `startup_name` — are shared by more than one record type. Without `import_run` in the key, a row of one file could coalesce onto a row of another: an investor and a startup that happen to share a `name`, for instance, would collapse into a single row. `import_run` is constant per file and distinct per file, so including it scopes every match to the file that supplied the row.

**The `startup` key includes `website`, and it must.** Cleaning rule 2 deduplicates Startup records on `name` plus `headquarters_location`, and `crunchbase_startups_sample.csv` deliberately carries a pair of rows that match on exactly that pair while differing on `website`. A coalesce key of `import_run` + `name` + `headquarters_location` would therefore collapse that pair into **one** staging row at import time: the row count would come out as 12 instead of 13, and the rule 2 fixture would be destroyed before the cleaning rule that exists to catch it ever ran. Adding `website` separates the pair, because the two rows differ there. The duplicate must be resolved by cleaning rule 2 at transform time, not by the import.

Across all six files the keys above yield **65 distinct values over 65 rows**, with no collision within a file, no collision between files, and no row whose key is blank in every non-`import_run` component.

### Mapping roll-up

Every column of every file is mapped, and every mapped column is a staging dictionary element.

| File | Record type | CSV columns | Control | Flattened | Data rows |
| --- | --- | --- | --- | --- | --- |
| `crunchbase_startups_sample.csv` | `startup` | 19 | 7 | 12 | 13 |
| `crunchbase_investors_sample.csv` | `investor` | 12 | 7 | 5 | 8 |
| `crunchbase_funding_rounds_sample.csv` | `funding_round` | 15 | 7 | 8 | 12 |
| `linkedin_founders_sample.csv` | `founder` | 13 | 7 | 6 | 10 |
| `linkedin_executives_sample.csv` | `executive` | 13 | 7 | 6 | 10 |
| `linkedin_job_postings_sample.csv` | `job_posting` | 16 | 7 | 9 | 12 |
| **Total field maps** | — | **88** | 42 | 46 | **65** |

The forty-six flattened field maps address **thirty-three** distinct staging columns, because five columns are shared by more than one record type and are declared once on the table:

| Shared staging column | Read by record types |
| --- | --- |
| `name` | `startup`, `investor`, `founder`, `executive` |
| `website` | `startup`, `investor` |
| `active` | `startup`, `job_posting` |
| `title` | `founder`, `executive`, `job_posting` |
| `startup_name` | `founder`, `executive`, `funding_round`, `job_posting` |

Thirty-three flattened columns plus the seven control columns is the table's full width of forty. **`portfolio_count` appears in no file, in no field map and in no column of this table.**

## Load order

**The load order is a hard sequence, not a preference.** Child rows carry natural-key references to Startup and Investor records, and the staging-to-entity transform resolves a reference only against a record that already exists. Load and transform each file in this order, completing the transform for one file before starting the next:

| Order | File | Record type | Why it sits here |
| --- | --- | --- | --- |
| **1** | `crunchbase_startups_sample.csv` | `startup` | **First**, because every other file references its `name` values through `startup_name`. Until the Startup records exist, every child row's parent reference is unresolvable and the row is rejected. |
| **2** | `crunchbase_investors_sample.csv` | `investor` | **Second**, because `crunchbase_funding_rounds_sample.csv` references its `name` values through `lead_investor_name` and `participating_investor_names`. |
| **3** | `crunchbase_funding_rounds_sample.csv` | `funding_round` | **Third.** It references both parents — Startup through `startup_name`, and Investor through `lead_investor_name` and `participating_investor_names` — so both preceding files must be loaded and transformed first. |
| **4** | `linkedin_founders_sample.csv` | `founder` | After the startups file. Its only reference is `startup_name`. |
| **5** | `linkedin_executives_sample.csv` | `executive` | After the startups file. Its only reference is `startup_name`. |
| **6** | `linkedin_job_postings_sample.csv` | `job_posting` | After the startups file. Its only reference is `startup_name`. |

Positions 4, 5 and 6 depend only on position 1, so the three LinkedIn files may be loaded in any order relative to one another provided all three come after `crunchbase_startups_sample.csv`. Positions 1, 2 and 3 are strictly ordered.

### There is no NewsArticle CSV

**There are exactly six CSV files, and none of them is a NewsArticle file.** Automated NewsArticle ingestion is out of scope: no ingestion flow serves `x_bst_startuptrk_newsarticle`, the staging table's `record_type` choice list contains **no** `news_article` member, and there is consequently no seventh sample file, no seventh data source, no seventh import set table and no seventh transform map. **NewsArticle records are created by manual entry** — through the **News articles** module of the Boston Startup Tracker application menu — or by a REST write to the `/news` resource. The absence is intentional. It is recorded in [`../gaps-and-flags.md`](../gaps-and-flags.md) and in [`../../../docs/decisions/DECISION_LOG.md`](../../../docs/decisions/DECISION_LOG.md).

## Steps

Perform steps 1 through 8 once per file, in the [load order](#load-order) above, then step 9 once at the end.

### Step 1 — create the data source

**System Import Sets > Administration > Data Sources**, then **New**. One record per file.

| Field | Value |
| --- | --- |
| Name | Per the table below. |
| Import set table label | Per the table below. |
| Import set table name | Per the table below. Enter it exactly; if the platform applies the application-scope prefix, record the derived name in the [Build verification](#build-verification) table. |
| Type | **File** |
| Format | **CSV** |
| File retrieval method | **Attachment** |
| Delimiter | `,` — a single comma |
| Header row | `1` |

| Order | File | Data source name | Import set table label | Import set table name |
| --- | --- | --- | --- | --- |
| 1 | `crunchbase_startups_sample.csv` | `BST fallback sample - Crunchbase startups` | `BST staging import - Crunchbase startups` | `u_bst_stg_cb_startups` |
| 2 | `crunchbase_investors_sample.csv` | `BST fallback sample - Crunchbase investors` | `BST staging import - Crunchbase investors` | `u_bst_stg_cb_investors` |
| 3 | `crunchbase_funding_rounds_sample.csv` | `BST fallback sample - Crunchbase funding rounds` | `BST staging import - Crunchbase funding rounds` | `u_bst_stg_cb_funding_rounds` |
| 4 | `linkedin_founders_sample.csv` | `BST fallback sample - LinkedIn founders` | `BST staging import - LinkedIn founders` | `u_bst_stg_li_founders` |
| 5 | `linkedin_executives_sample.csv` | `BST fallback sample - LinkedIn executives` | `BST staging import - LinkedIn executives` | `u_bst_stg_li_executives` |
| 6 | `linkedin_job_postings_sample.csv` | `BST fallback sample - LinkedIn job postings` | `BST staging import - LinkedIn job postings` | `u_bst_stg_li_job_postings` |

Save the record, then attach the CSV to it with the paperclip control. Attach the file **unmodified**, exactly as it sits in [`../../sample-data/`](../../sample-data/). Do not open it in a spreadsheet application and re-save it: doing so commonly rewrites the line endings to CRLF, adds a byte-order mark, re-quotes fields the dialect leaves unquoted, strips the designed leading and trailing spaces the rule 1 fixtures depend on, and reformats the ISO dates into a locale format. Any one of those breaks a fixture or a field map.

### Step 2 — create the import set table

Use the **Test Load 20 Records** related link on the data source. The platform reads the header row, creates the import set table with one string column per header, and loads the file's rows into it — all 13, 8, 12, 10, 10 or 12, since no file exceeds twenty rows.

Confirm three things before continuing:

- The import set table carries **one column per CSV header**: 19, 12, 15, 13, 13 or 16 respectively.
- The loaded row count equals the count in the [Mapping roll-up](#mapping-roll-up).
- No row was split. A row count higher than expected means a quoted field containing a line break was mis-parsed; a count lower than expected means the file was truncated.

The import set table holds every value as a string. Coercion to `integer`, `decimal`, `boolean` and `glide_date` happens in the transform, on the way into `x_bst_startuptrk_ingest_staging`, which is why the value conventions of the CSVs matter.

### Step 3 — create the transform map

**System Import Sets > Administration > Transform Maps**, then **New**. One record per record type, with the [common transform-map settings](#common-transform-map-settings).

| Order | Transform map name | Source table | Target table |
| --- | --- | --- | --- |
| 1 | `BST staging map - startup` | `u_bst_stg_cb_startups` | `x_bst_startuptrk_ingest_staging` |
| 2 | `BST staging map - investor` | `u_bst_stg_cb_investors` | `x_bst_startuptrk_ingest_staging` |
| 3 | `BST staging map - funding_round` | `u_bst_stg_cb_funding_rounds` | `x_bst_startuptrk_ingest_staging` |
| 4 | `BST staging map - founder` | `u_bst_stg_li_founders` | `x_bst_startuptrk_ingest_staging` |
| 5 | `BST staging map - executive` | `u_bst_stg_li_executives` | `x_bst_startuptrk_ingest_staging` |
| 6 | `BST staging map - job_posting` | `u_bst_stg_li_job_postings` | `x_bst_startuptrk_ingest_staging` |

All six target the same table. That is correct: there is **one** staging table, and `record_type` is what separates the record types inside it.

### Step 4 — map the fields

With the transform map saved, use the **Auto map matching fields** related link. Because every CSV header is spelled exactly as its staging dictionary element, the automatic mapping resolves every column of every file, and the Field Maps related list should show 19, 12, 15, 13, 13 or 16 entries with nothing left over.

Then correct and complete each map by hand:

1. **Verify the count.** The Field Maps related list must hold exactly one entry per CSV column, with no unmapped source column and no target column mapped twice. Compare it against that file's table in [The field mapping, file by file](#the-field-mapping-file-by-file), row by row.
2. **Set `Coalesce` to true** on exactly the columns in [The coalesce key per record type](#the-coalesce-key-per-record-type), and confirm it is false everywhere else.
3. **Set `Choice action` to `reject`** on the four control-column field maps: `source_system`, `record_type`, `import_state` and `run_provenance`. Leave it untouched on the flattened columns, none of which carries a choice list.
4. **Set `Date format` to `yyyy-MM-dd`** on `round_date` in the `funding_round` map and on `posted_date` in the `job_posting` map. No other file carries a date column.
5. **Confirm `Use source script` is false** on all of them. No field map in this procedure computes a value.

Do **not** map any source column to a target column of a different name, and never map a child file's `startup_name` to `name` or the reverse. `name` is the record's own name; `startup_name` is the parent's name. Swapping them detaches every child row from its parent, and it does so silently.

### Step 5 — load the data

If the test load of step 2 already staged the file's rows into the import set table, run the transform against that import set with **System Import Sets > Run Transform**: select the import set and the matching transform map, then run it. Otherwise use **System Import Sets > Load Data**, choose the existing data source, choose the existing transform map, and submit.

Either route produces a `sys_import_set` record and a run whose progress is shown on screen.

### Step 6 — verify the staged rows

Open the staged rows through the **Ingestion staging** module of the Boston Startup Tracker application menu, filtered to that file's `import_run`.

**Verify in the list view, not over the Table API.** The staging table ships with `ws_access` false, so `GET /api/now/table/x_bst_startuptrk_ingest_staging` does not serve it and a script written against that path fails whether or not the rows loaded. `GATE-SEC-02` in [`../validation-gates.md`](../validation-gates.md) asserts that posture deliberately.

Check all six of the following on the rows of that `import_run`:

| # | Check | Expected |
| --- | --- | --- |
| 1 | Row count | The count for that file in the [Mapping roll-up](#mapping-roll-up). |
| 2 | `source_system` | The same constant on every row — `crunchbase` or `linkedin`. |
| 3 | `record_type` | The same constant on every row, and the one this file's record type requires. |
| 4 | `import_state` | **`pending`** on every row. Nothing has transformed them yet. |
| 5 | `run_provenance` | **`fallback`** on every row. No row carries `live`. |
| 6 | `error_message` | Empty on every row. |

Then spot-check that the flattened columns actually carry values. Open two or three rows and confirm the columns that file maps are populated and the columns it does not map are empty. **A column that is empty on every row of the file is the signature of an unmapped or misnamed field map**, not of missing data — the load reports success either way, which is what makes the check necessary. Confirm in particular that `raw_payload` holds a JSON object rather than an empty string, and that on the funding-rounds file `participating_investor_names` holds a comma-separated list with no space after the comma.

### Step 7 — repeat for the remaining files

Repeat steps 1 through 6 for each remaining file, in the [load order](#load-order). Do not begin a child file before the file it depends on has been loaded **and** transformed to entity records by step 8: a natural key resolves against the entity table, not against the staging table.

### Step 8 — run the staging-to-entity transform

The import of steps 1 through 6 puts rows into `x_bst_startuptrk_ingest_staging` with `import_state` `pending`. It creates **no** entity record. The staging-to-entity step is a separate operation, and it is the same code path both ingestion flows use on their fallback branch: `IngestionMapper.ingestStaging()`.

Two ways to run it, and both are acceptable evidence:

- **Through the flows.** Set the property `x_bst_startuptrk.ingestion.source_mode` to `fallback`, then run the Crunchbase flow of [`02-flow-crunchbase-ingestion.md`](02-flow-crunchbase-ingestion.md) and the LinkedIn flow of [`03-flow-linkedin-ingestion.md`](03-flow-linkedin-ingestion.md). Each reads the pending rows of its own `source_system`, applies the four cleaning rules, writes the entity records, records each row's outcome and writes a run summary. Set the property back to `live` afterwards.
- **Directly, from a background script inside the scope**, one call per source system:

```javascript
var mapper = new IngestionMapper();
var crunchbase = mapper.ingestStaging('manual-load-' + gs.generateGUID(), 'crunchbase', '', 'fallback');
var linkedin = mapper.ingestStaging('manual-load-' + gs.generateGUID(), 'linkedin', '', 'fallback');
gs.info('crunchbase accepted ' + crunchbase.accepted + ' rejected ' + crunchbase.rejected);
gs.info('linkedin accepted ' + linkedin.accepted + ' rejected ' + linkedin.rejected);
```

`ingestStaging()` selects rows on `source_system` and `import_state` `pending`, with `import_run` as an optional further filter — pass an empty string to take every pending row of that source system, or a specific token to transform one file's rows in isolation. Run `crunchbase` before `linkedin`, so the Startup records the LinkedIn rows resolve against already exist.

Because the query is bounded to `import_state` `pending`, **a row that has already been processed is never re-read**. Re-running the transform therefore cannot duplicate entity records from staging, whichever route is used.

### Step 9 — recalculate the derived portfolio counts

After the load, **invoke `InvestorPortfolioService.recalculateAll()` from a background script**. Navigate to **System Definition > Scripts - Background**, set the scope selector on that page to **Boston Startup Tracker** so the script runs inside `x_bst_startuptrk`, and run:

```javascript
var portfolio = new InvestorPortfolioService();
gs.info('investors rewritten: ' + portfolio.recalculateAll());
```

The scope selector is not optional. The application's tables are `package_private`, so a script left in the Global scope cannot reach them and `InvestorPortfolioService` cannot be instantiated from there.

`recalculateAll()` reads the graph in two passes — one over the funding rounds and one over the join table — then makes a single pass over the investors, **writing only those whose stored count differs from the derived count**, and returns the number of investors it wrote. Record that number in the [Build verification](#build-verification) table.

**On a load performed with business rules running, the expected return is `0`**: the two portfolio business rules will already have maintained every count as the funding rounds and join rows were inserted, so there is nothing left to correct. A non-zero return is meaningful — it says the stored counts had drifted, which means business rules were suppressed somewhere on the write path. Investigate before signing the guide off.

## The staging-to-entity transform

### What it writes

Exhaustively, `IngestionMapper` writes seven tables from the staged rows and no others.

| Record type | Entity table | Existing-record lookup, so a re-run updates rather than duplicates |
| --- | --- | --- |
| `startup` | `x_bst_startuptrk_startup` | `findExistingStartup(name, headquarters_location)`, case-insensitively — the same key as cleaning rule 2. Exactly one match updates it; no match inserts; **more than one match is an ambiguity failure** and nothing is written. |
| `investor` | `x_bst_startuptrk_investor` | `findExistingInvestor(name)` — **name only**, with no location component. Same three outcomes. |
| `funding_round` | `x_bst_startuptrk_fundinground` | **None. Every accepted funding round is inserted.** |
| `founder` | `x_bst_startuptrk_founder` | **None. Every accepted founder is inserted.** |
| `executive` | `x_bst_startuptrk_executive` | **None. Every accepted executive is inserted.** |
| `job_posting` | `x_bst_startuptrk_jobposting` | **None. Every accepted job posting is inserted.** |
| participation | `x_bst_startuptrk_m2m_round_investor` | `linkParticipants()` reads the round's existing rows first and inserts only the missing `funding_round` + `investor` pairs, so the call is idempotent. A unique composite index on that pair enforces it whatever the write path. |

Four of the six record types have no upsert key, so **what protects this procedure from duplicating them is the `import_state` transition, not the entity tables.** A staged row that has been processed is no longer `pending`, and `ingestStaging()` only ever reads pending rows. Two consequences follow: re-running the transform is safe, and **re-importing the CSVs and then transforming again is not** — a coalesce update returns a row to no particular state, so if a row is deliberately reset to `pending` to be re-transformed, the funding rounds, founders, executives and job postings it produces are inserted a second time. Delete the entity records first, or accept the duplicates.

`x_bst_startuptrk_newsarticle` is written by neither the import nor the transform.

### Participating investors become join rows

**The transform materialises `x_bst_startuptrk_m2m_round_investor` rows from `participating_investor_names`.** For each accepted `funding_round` row it splits the quoted comma-separated list on the comma, trims each member, drops an empty member, resolves each remaining member to exactly one Investor record, keeps a repeated member once, and **creates one join row per resolved investor** through `InvestorPortfolioService.linkInvestorToRound()`. A member that resolves to no investor, or to more than one, is logged as a warning and contributes no join row; the members that do resolve still become join rows.

Three rules govern the write, and all three matter:

- **`lead_investor` remains a distinct first-class reference** on `x_bst_startuptrk_fundinground`, resolved from `lead_investor_name` and set directly on the funding-round record. It is a single reference, not a join row. An investor that both led a round and participated in it appears in both places, which is correct.
- **The join table is authoritative for participation.** It is the only table the transform writes for it.
- **`x_bst_startuptrk_fundinground.participating_investors` is never written by this path.** It is a read-only projection that the business rule on the join table refreshes, and the mapper's write allowlist excludes it, so an attempt to set it is dropped rather than applied.

Both references on the join table are mandatory and both cascade on delete, so deleting a funding round or an investor removes its join rows with it.

### Business rules must run during the load

**Every write on the entity path must run business rules.** Three business rules are active on the tables this procedure touches, and two of them maintain the derived `x_bst_startuptrk_investor.portfolio_count` through `InvestorPortfolioService`:

| Business rule | Table | When |
| --- | --- | --- |
| `Recalculate investor portfolio on funding round` | `x_bst_startuptrk_fundinground` | After insert, update and delete. On an update it recalculates **both** the previous and the new `lead_investor`, and handles a change to the round's `startup`. |
| `Recalculate investor portfolio on round investor link` | `x_bst_startuptrk_m2m_round_investor` | After insert, update and delete. It also refreshes the derived `participating_investors` projection on the affected funding round. |
| `Trim and validate startup` | `x_bst_startuptrk_startup` | Before insert and update. |

Leave **Run business rules** true on all six transform maps, and do not call `setWorkflow(false)` in any script used to load or transform this data.

**Operational warning.** `portfolio_count` is a **stored** integer. Nothing recomputes it on read. A load performed with rule execution disabled — an import transform with **Run business rules** cleared, or a `setWorkflow(false)` in a background script — leaves the stored aggregate **silently wrong** for every investor touched by that write. There is no error, no warning and no log record; the column simply disagrees with the data, and the portal and the API both report the wrong number. The only signal is the return value of [step 9](#step-9--recalculate-the-derived-portfolio-counts).

## Reading the run results

Two layers report on the load, and they must not be confused.

### The import set and the import log

| Surface | Where | What it tells you |
| --- | --- | --- |
| Import set | **System Import Sets > Import Sets** | One record per load, carrying the data source, the state and the row count. The place to confirm the file loaded at all. |
| Import set rows | The import set table itself, `u_bst_stg_*` | The raw string rows the wizard read from the CSV, one per data row, each carrying its own `sys_import_state` and `sys_import_state_comment`, plus `sys_target_sys_id` naming the staging row it produced. |
| Import log | **System Import Sets > Administration > Import Log** | Per-row and per-run messages from the import itself: an unmapped column, a coercion refusal, a rejected choice value, a truncated value. Read it after every load, not only after a failure. |
| Staged rows | The **Ingestion staging** module | The application rows, carrying `import_state` and `error_message`. The place to read the outcome of the cleaning rules. |

**Operational warning — two different state columns.** The import set row carries `sys_import_state` with values such as `Pending`, `Processed`, `Ignored` and `Error`; the application row carries `import_state` with values `pending`, `processed`, `rejected` and `error`. They belong to adjacent layers and mean different things. `sys_import_state` describes whether the **CSV row reached the staging table**; `import_state` describes whether the **staged row became an entity record**. An import set row reading `Processed` says nothing about whether cleaning rule 4 later rejected the staged row. Always name the layer when reporting a count.

### `import_state` after the transform

Once every file has been imported and transformed, the sixty-five rows reconcile to exactly this distribution:

| `import_state` | Rows | What they are |
| --- | --- | --- |
| `processed` | **52** | An entity record was created or updated from the row. |
| `rejected` | **13** | The row was refused by a cleaning rule: **12** rows blanking a mandatory column for their record type, plus **1** row that repeats an earlier startup's `name` plus `headquarters_location` pair within the same batch. |
| `error` | **0** | A write failed for a reason other than a cleaning rule. |
| `pending` | **0** | Nothing left untransformed. |

A different distribution means a file was edited, a field map is mismapped, or the load order was not followed. Investigate before signing off. The per-file defect inventory that produces these numbers is in [`../../sample-data/README.md`](../../sample-data/README.md).

### How `error_message` is populated

`error_message` is empty on every shipped row and is written by the transform, never by the import. `IngestionMapper.clean()` **returns** the reason a row was refused, and `IngestionMapper.writeStagingState()` writes it to `error_message` — truncated to the column's 1000 characters — together with the matching `import_state`, on the same staging row. The two columns are therefore always consistent: a row reading `rejected` or `error` always names its reason, and a row reading `processed` always has an empty `error_message`.

The reasons a row can carry, and what to do about each:

| `import_state` | `error_message` names | Expected here | Action |
| --- | --- | --- | --- |
| `rejected` | Every missing mandatory column on the row, so a row blanking two of them names both | **Yes — 12 rows.** These are the cleaning-rule-4 fixtures. | None. This is the designed outcome. |
| `rejected` | `duplicate startup in the same batch` | **Yes — 1 row.** The cleaning-rule-2 fixture. | None. This is the designed outcome. |
| `rejected` | `no startup carries the name`, or `the name is ambiguous across <n> startups` | **Only on a row that also blanks a mandatory column.** | On any other row it means the load order was not followed, or the parent file was not transformed first. Re-run the parent, reset the row to `pending`, transform again. |
| `rejected` | A natural key reported as ambiguous | No | Two records share a name. Resolve the collision on the entity table, then re-transform. |
| `error` | An insert or update failure, or a refused value | **No — the expected count is 0.** | A genuine defect. Read the reason, then read the flow execution log for the run identifier. |

A per-record skip arising from a cleaning rule is **expected behaviour, not an error**. Counting the twelve rule 4 rejections or the one duplicate as errors would misreport a clean run. Only `import_state` `error` and an unhandled exception in the flow execution log count as errors for success criterion 4.

## Verification after the load

Perform all five checks. Every figure below is fixed by the shipped files, so any deviation is a defect in the load rather than a property of the data.

**1. Staged row counts, per `import_run`.** In the **Ingestion staging** list view, group by `import_run`:

| `import_run` | Rows |
| --- | --- |
| `fallback-sample-crunchbase-startups` | 13 |
| `fallback-sample-crunchbase-investors` | 8 |
| `fallback-sample-crunchbase-funding-rounds` | 12 |
| `fallback-sample-linkedin-founders` | 10 |
| `fallback-sample-linkedin-executives` | 10 |
| `fallback-sample-linkedin-job-postings` | 12 |
| **Total** | **65** |

**2. Entity record counts after the transform.** Open each table through its module on the Boston Startup Tracker application menu:

| Table | Records | From |
| --- | --- | --- |
| `x_bst_startuptrk_startup` | **9** | 13 staged rows, less 3 rule 4 rejections and 1 rule 2 duplicate |
| `x_bst_startuptrk_investor` | **7** | 8 staged rows, less 1 rule 4 rejection |
| `x_bst_startuptrk_fundinground` | **10** | 12 staged rows, less 2 rule 4 rejections |
| `x_bst_startuptrk_founder` | **8** | 10 staged rows, less 2 rule 4 rejections |
| `x_bst_startuptrk_executive` | **8** | 10 staged rows, less 2 rule 4 rejections |
| `x_bst_startuptrk_jobposting` | **10** | 12 staged rows, less 2 rule 4 rejections |
| `x_bst_startuptrk_newsarticle` | **0** | No file, no flow, no transform writes it |
| **Total entity records** | **52** | Equal to the `processed` row count |

**3. The join rows were created — spot-check `x_bst_startuptrk_m2m_round_investor`.** This is the check most likely to reveal a silent mapping fault, because an unmapped `participating_investor_names` column produces funding rounds that look complete and a join table that is simply empty.

| Check | Expected |
| --- | --- |
| Total rows in the join table | **26** |
| Rows for the round with the largest participant list | **5** |
| Every row's `funding_round` and `investor` | Both populated. Neither is nullable. |
| Duplicate `funding_round` + `investor` pairs | **None.** The unique composite index forbids them. |
| A round whose `lead_investor` also appears among its join rows | Permitted and present. It is not a duplicate. |
| `x_bst_startuptrk_fundinground.participating_investors` | Populated on the rounds that have join rows, by the projection business rule — **not** by the transform. |

An empty join table with ten funding rounds present means `participating_investor_names` was left unmapped, was re-delimited in transit, or the investors file was transformed after the funding-rounds file rather than before it.

**4. The derived portfolio counts.** After [step 9](#step-9--recalculate-the-derived-portfolio-counts), `x_bst_startuptrk_investor.portfolio_count` is non-zero on **6** of the 7 investors. Exactly one investor is referenced by no funding round, as lead or as participant, and its count is correctly **0**. `recalculateAll()` returns **0** investors rewritten on a load whose business rules ran.

**5. Provenance.** Every staged row reads `run_provenance` `fallback`, and no row reads `live`. A flow run over this dataset sets `x_bst_startuptrk.ingestion.last_run_provenance` to `fallback` and writes a run summary carrying the run identifier, the provenance and the processed, rejected and skipped counts. Any result derived from this dataset must be labelled **`fallback validated`** and never `live validated`; the labelling convention is applied by [`05-atf-test-suites.md`](05-atf-test-suites.md) and the evidence is collected by [`../validation-checklist.md`](../validation-checklist.md).

### Retention of the loaded rows

The sixty-five rows are **not permanent**, and no manual clean-up step is required. A daily scheduled job, `Prune ingestion staging rows`, clears the payload and person columns of a settled row once it is older than `x_bst_startuptrk.privacy.staging_minimise_hours` — shipped at 24 — and deletes a row outright once it is older than `x_bst_startuptrk.privacy.staging_retention_days`, shipped at 30. A row still `pending` is never touched.

The consequence for this procedure: **re-run the import before repeating a flow test after a day has passed.** A fallback run over a minimised row rejects it under cleaning rule 4 for missing mandatory fields, which is correct behaviour rather than a defect. The CSVs are the reproducible source; the table is a working copy. The full policy is in [`../data-model.md`](../data-model.md).

## This guide stages raw rows; the flows clean them

The division of labour is exact, and the import must not cross it.

| Concern | Where it happens |
| --- | --- |
| Reading the CSV, mapping by header name, coercing to the staging column types, coalescing a re-load | **This guide.** Steps 1 through 6. |
| Trimming whitespace, deduplicating startups, normalising choice values, rejecting records missing mandatory fields | **`IngestionMapper`**, at transform time — the four cleaning rules, run by the flows of [`02-flow-crunchbase-ingestion.md`](02-flow-crunchbase-ingestion.md) and [`03-flow-linkedin-ingestion.md`](03-flow-linkedin-ingestion.md), or by `ingestStaging()` directly. |
| Logging a skip, a rejection, a duplicate or an unmatched choice value | **`IngestionLogger`**, at transform time. |
| Deriving `portfolio_count` | **`InvestorPortfolioService`**, through the two business rules and the post-load recalculation. |

**The import transform must not pre-clean the data.** It does not trim, it does not deduplicate, it does not normalise a choice value, and it does not reject a row for a blank column. The four cleaning rules exist downstream, and **the shipped rows are deliberately defective in specific places precisely so that a load exercises them**: rows carrying leading and trailing whitespace, a pair of startups matching on name plus headquarters location while differing on website, eleven unmatched choice values across ten rows, and twelve rows each blanking a mandatory column. Every one of those is an intentional fixture, not an authoring error.

Do not repair them, and do not configure the import to compensate for them. Trimming a value in the field map would delete a rule 1 fixture; coalescing on the rule 2 key would delete the rule 2 fixture; enforcing mandatory fields on the transform map would move the rule 4 rejections to the wrong layer and change the expected `import_state` distribution. The inventory of which fixture sits in which file is in [`../../sample-data/README.md`](../../sample-data/README.md).

## Operational warnings

These five are not rationale. They describe failures that are easy to cause and hard to see, and three of them are completely silent.

### A change to one leg of the three-way contract breaks the fallback path silently

The Data Import Wizard maps columns **by header name**. Rename, re-case or misspell a column in any one of the three legs — the CSV header row, the staging dictionary element, or the field map in this guide — and that column is simply left unmapped. **The load reports success, the row count is correct, and no error is raised**; the target field is empty on every row, and the ingestion flows find nothing usable in it. Whenever any one leg changes, re-verify all three, name for name, before loading anything. Read the header row of the file, read `sys_dictionary` for `x_bst_startuptrk_ingest_staging`, and read the Field Maps related list on the transform map, and confirm the three lists agree.

### Business rules disabled during the load leaves `portfolio_count` silently wrong

`x_bst_startuptrk_investor.portfolio_count` is a stored integer maintained by two business rules, and nothing recomputes it on read. A write that bypasses business rules — **Run business rules** cleared on a transform map, or `setWorkflow(false)` in a script — leaves the stored count stale for every investor touched by that write. **There is no error, no warning and no log record.** Leave **Run business rules** true on all six maps, never suppress rules on this path, and always run [step 9](#step-9--recalculate-the-derived-portfolio-counts) afterwards: its return value is the only signal that the counts drifted.

### `active` is a string column, and a blank must survive the load

On `x_bst_startuptrk_ingest_staging`, `active` is a **`string` of length 10** carrying the text `true` or `false`, **not** a True/False column, and it declares **no dictionary default**. That is deliberate, and it is what lets a blank `active` survive the import and be rejected by cleaning rule 4 rather than being silently defaulted to `true`. Two consequences: do not change the column's type or add a default to it, and do not configure the field map to substitute a value for a blank. `x_bst_startuptrk_startup.active` keeps its own dictionary default of `true`, which applies only to a Startup inserted without the field set.

### Do not open the CSVs in a spreadsheet application

Attach the files exactly as they are. A spreadsheet round trip commonly rewrites LF line endings to CRLF, adds a byte-order mark, re-quotes fields the dialect leaves unquoted, **strips the designed leading and trailing spaces the rule 1 fixtures depend on**, reformats an ISO date into a locale format, and renders a large plain currency figure in scientific notation. Each of those either breaks a fixture or breaks a coercion, and several of them do so without any visible sign in the loaded rows.

### Verify in the list view, not over the Table API

`x_bst_startuptrk_ingest_staging` ships with `ws_access` false and `access` `package_private`, so it is **not** served at `/api/now/table/x_bst_startuptrk_ingest_staging` and is unreachable from any other application scope. A verification script written against that path fails identically whether the rows loaded or not, so it can neither confirm nor deny the load. Use the **Ingestion staging** module and the platform list view, and run any script that touches the table from a background script whose scope selector reads **Boston Startup Tracker**.

## Legacy provenance

This procedure replaces the following legacy constructs. **Nothing below is ported.**

### The Faker seeder this procedure replaces

[`../../../scripts/seed_database.py`](../../../scripts/seed_database.py), 135 lines, generated synthetic records directly into a database through the Django ORM. The six CSVs and this import replace it in full.

| Citation | What is there | What replaces it |
| --- | --- | --- |
| `:L3-L4` | `import django` and `from faker import Faker` — the script's two third-party dependencies. | Nothing. The fallback dataset is six static, version-controlled CSV files, and the load needs no runtime and no package. |
| `:L13-L17` | `setup_django()`, which points `DJANGO_SETTINGS_MODULE` at a `boston_startup_tracker.settings` module and calls `django.setup()`. The Django ORM packages it depends on — `startups.models` at `:L21`, `investors.models` at `:L40` and `funding.models` at `:L58` — **do not exist in this repository**, so the script cannot run at all. | The platform's own import pipeline: a data source, an import set table and a transform map per record type, all targeting `x_bst_startuptrk_ingest_staging`. |
| `:L19-L36` | `create_startups`, generating `industry` from `['Tech', 'Biotech', 'Fintech', 'Edtech', 'Cleantech']` at `:L30` and `funding_stage` from `['Seed', 'Series A', 'Series B', 'Series C', 'IPO']` at `:L32`. | The authored values of `crunchbase_startups_sample.csv`. Of those five industries only `Fintech` is a member of the binding `Startup.industry` list, and of those five funding stages `Series C` and `IPO` are members of no binding list at all. |
| `:L38-L54` | `create_investors`, generating `type` from `['VC', 'Angel', 'Corporate', 'Accelerator']` at `:L45`. | The authored values of `crunchbase_investors_sample.csv`. That list omits `PE`, which the binding `Investor.type` list requires. |

**None of those literals matches the binding choice lists**, which is why nothing is carried forward and the CSVs are authored fresh against the choice values the Update Set declares. The script also writes columns that exist on no target table, and it seeds NewsArticle records at `:L87-L100` for an entity this dataset deliberately excludes.

### The cleaner whose transformations are deliberately not applied

[`../../../src/data_collection/data_cleaning/startup_cleaner.py`](../../../src/data_collection/data_cleaning/startup_cleaner.py) is the pandas cleaning pipeline. **The staged data is deliberately not cleaned by any of it**, and the four cleaning rules are applied downstream by `IngestionMapper`, not by the import transform.

| Citation | What is there | Why it is not applied |
| --- | --- | --- |
| `:L57` and `:L60` | Deduplication on **name + website** — `duplicated(subset=['company_name', 'website'])` and the matching `drop_duplicates`. | Cleaning rule 2 deduplicates on `name` + **`headquarters_location`**, case-insensitively. The two keys select different rows: the deliberate duplicate pair in `crunchbase_startups_sample.csv` differs on `website`, so a name-plus-website key would not catch it at all. |
| `:L90` | **Median imputation** of missing numeric values — `fillna(df[column].median())`. | Cleaning rule 4 **rejects** a record missing a mandatory field. Imputing a value is the opposite operation: it would manufacture data and let a partial record through. |

Neither transformation is reproduced, in the import or anywhere else. The same module fills missing values with the string `'Unknown'` at `:L86`, which the dataset's no-sentinel-values rule forbids for the same reason.

## Build verification

Do not sign this guide off until every line below is true.

| # | Check | Record |
| --- | --- | --- |
| 1 | Exactly **six** data sources exist, one per CSV file, each of type **File**, format **CSV**, retrieval method **Attachment**, delimiter `,`, header row `1`, with the correct file attached unmodified. | |
| 2 | Exactly **six** import set tables exist, one per record type, each carrying one column per that file's CSV header: 19, 12, 15, 13, 13 and 16. Derived names recorded here: `______` | |
| 3 | Exactly **six** transform maps exist, and **all six carry target table `x_bst_startuptrk_ingest_staging`**. No map targets any other table. | |
| 4 | Every map carries **Active** true, **Run business rules** true, **Enforce mandatory fields** No, **Copy empty fields** true, and **Run script** false. | |
| 5 | **88** field maps exist in total — 19, 12, 15, 13, 13 and 16 — every one a one-to-one mapping by header name, with no unmapped source column, no target column mapped twice, and no source script anywhere. | |
| 6 | The coalesce columns match [The coalesce key per record type](#the-coalesce-key-per-record-type) exactly, `import_run` is a coalesce column on all six maps, and the `startup` map includes `website` in its key. | |
| 7 | **Choice action** is `reject` on the four control-column field maps of every map, and `create` is used nowhere. | |
| 8 | **Date format** `yyyy-MM-dd` is set on `round_date` in the `funding_round` map and on `posted_date` in the `job_posting` map. | |
| 9 | `portfolio_count` appears in **no** field map, and no map targets a read-only or derived column. | |
| 10 | The files were loaded in the [load order](#load-order): startups, then investors, then funding rounds, with the three LinkedIn files after startups. | |
| 11 | `x_bst_startuptrk_ingest_staging` holds **65** rows across the six `import_run` values, in the per-file counts of the [verification table](#verification-after-the-load). | |
| 12 | Before the transform, every staged row read `import_state` `pending`, `run_provenance` `fallback` and an empty `error_message`. | |
| 13 | After the transform, `import_state` reconciles to **52 `processed`, 13 `rejected`, 0 `error`, 0 `pending`**, and every rejected row names its reason in `error_message`. | |
| 14 | The entity record counts are **9, 7, 10, 8, 8, 10** and `x_bst_startuptrk_newsarticle` holds **0**. | |
| 15 | `x_bst_startuptrk_m2m_round_investor` holds **26** rows, the largest round links **5** investors, and no `funding_round` + `investor` pair is duplicated. | |
| 16 | `InvestorPortfolioService.recalculateAll()` was run from a background script with the scope selector set to **Boston Startup Tracker**, and returned: `______` — expected `0`. | |
| 17 | `portfolio_count` is non-zero on **6** of the 7 investors, and the one investor no round references reads `0`. | |
| 18 | No transform map, script or import path used `setWorkflow(false)` or ran with business rules suppressed. | |
| 19 | No CSV file was edited, re-saved, trimmed or otherwise repaired, and no designed defect was corrected. | |
| 20 | `x_bst_startuptrk.ingestion.source_mode` has been set back to `live` if it was set to `fallback` for [step 8](#step-8--run-the-staging-to-entity-transform). | |
| 21 | Any result derived from this dataset is labelled **`fallback validated`**, never `live validated`. | |

Guide 05 may begin once every line above is true. Success criterion 4 in [`../validation-checklist.md`](../validation-checklist.md) is satisfied separately, by three consecutive guard-passing flow runs with zero unhandled errors and the provenance of each one recorded.

## Related documents

| Document | Relationship |
| --- | --- |
| [`../../sample-data/README.md`](../../sample-data/README.md) | **Leg (a)** of the three-way contract and **authoritative for the CSV header rows and their order**, the per-file `import_run` values, the value conventions, the row counts and the per-file designed-defect inventory. |
| [`../../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml`](../../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml) | **Leg (b)**, and **authoritative for the staging column names**, types and lengths, and for every other identifier cited here. |
| [`../../sample-data/crunchbase_startups_sample.csv`](../../sample-data/crunchbase_startups_sample.csv) | Load position 1. Record type `startup`, 19 columns, 13 rows. |
| [`../../sample-data/crunchbase_investors_sample.csv`](../../sample-data/crunchbase_investors_sample.csv) | Load position 2. Record type `investor`, 12 columns, 8 rows. |
| [`../../sample-data/crunchbase_funding_rounds_sample.csv`](../../sample-data/crunchbase_funding_rounds_sample.csv) | Load position 3. Record type `funding_round`, 15 columns, 12 rows. |
| [`../../sample-data/linkedin_founders_sample.csv`](../../sample-data/linkedin_founders_sample.csv) | Load position 4. Record type `founder`, 13 columns, 10 rows. |
| [`../../sample-data/linkedin_executives_sample.csv`](../../sample-data/linkedin_executives_sample.csv) | Load position 5. Record type `executive`, 13 columns, 10 rows. |
| [`../../sample-data/linkedin_job_postings_sample.csv`](../../sample-data/linkedin_job_postings_sample.csv) | Load position 6. Record type `job_posting`, 16 columns, 12 rows. |
| [`02-flow-crunchbase-ingestion.md`](02-flow-crunchbase-ingestion.md) | A **fallback reader** of this table. Its step 4 queries the `crunchbase` rows this guide loads, and its step 6 writes the four Crunchbase tables. |
| [`03-flow-linkedin-ingestion.md`](03-flow-linkedin-ingestion.md) | A **fallback reader** of this table. Its step 4 queries the `linkedin` rows this guide loads, and its step 6 writes the three LinkedIn tables. |
| [`05-atf-test-suites.md`](05-atf-test-suites.md) | The two ingestion-flow tests that **depend on this data**, and the `fallback validated` result label. Runs after this guide. |
| [`01-connection-credential-aliases.md`](01-connection-credential-aliases.md) | The two credential aliases the live path uses. Not required by this guide; the fallback path needs no credential. |
| [`04-service-portal-pages-and-widgets.md`](04-service-portal-pages-and-widgets.md) | The portal whose walkthrough reads the entity records this load produces. |
| [`../manual-build-instructions.md`](../manual-build-instructions.md) | The build order for the package and the split rule between Update Set XML and manual build. |
| [`../data-model.md`](../data-model.md) | The staging table's full column list, the entity choice values, the cascade rules, the `portfolio_count` derivation and the staging retention lifecycle. |
| [`../validation-checklist.md`](../validation-checklist.md) | Success criterion 4 and its provenance evidence, which the loaded rows supply. |
| [`../validation-gates.md`](../validation-gates.md) | The post-commit gates of precondition 4, and `GATE-SEC-02`, which fixes the list-view verification route. |
| [`../access-control.md`](../access-control.md) | The staging table's administrator-only posture on all four operations. |
| [`../api-reference.md`](../api-reference.md) | The Script Include call graph and the system-property inventory, including `ingestion.source_mode` and the two privacy properties. |
| [`../deployment-runbook.md`](../deployment-runbook.md) | The import sequence that commits the Update Set, and [what counts as a scheduled run](../deployment-runbook.md#what-counts-as-a-scheduled-run). |
| [`../gaps-and-flags.md`](../gaps-and-flags.md) | The NewsArticle ingestion exclusion, which is why there are six CSVs and not seven. |
| [`../../../docs/decisions/DECISION_LOG.md`](../../../docs/decisions/DECISION_LOG.md) | **Every "why"**, including the single staging table, the flattened-columns-plus-`raw_payload` shape and the natural-key references. |
