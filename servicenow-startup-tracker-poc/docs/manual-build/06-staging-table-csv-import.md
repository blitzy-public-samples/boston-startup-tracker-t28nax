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
| [`../../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml`](../../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml) | **Leg (b)**, and **authoritative** for every identifier this guide cites, including all forty-one staging column names. |
| [`../data-model.md`](../data-model.md) | The staging table's full column list with types and lengths, the entity choice values, the cascade rules, and the `Investor.portfolio_count` derivation and its `recalculateAll()` contract. |
| [`../validation-gates.md`](../validation-gates.md) | The eleven required post-commit gates of precondition 4, and the acceptance-required security check `GATE-SEC-01`, which records that the staging table stays closed to every external route — which is why the staged rows are verified in the list view rather than over the Table API. It blocks acceptance of the delivery but is **not** a precondition of this guide: it is read here for what it records, and its outcome gates nothing in this procedure. |
| [`02-flow-crunchbase-ingestion.md`](02-flow-crunchbase-ingestion.md) | The Crunchbase ingestion flow, whose fallback branch reads the `crunchbase` rows this guide loads. |
| [`03-flow-linkedin-ingestion.md`](03-flow-linkedin-ingestion.md) | The LinkedIn ingestion flow, whose fallback branch reads the `linkedin` rows this guide loads. |
| [`05-atf-test-suites.md`](05-atf-test-suites.md) | Runs after this guide. Its suites seed **their own** fixtures and read none of these rows; what it shares with this guide is the `fallback validated` result label. |
| [`../manual-build-instructions.md`](../manual-build-instructions.md) | The build order for the package as a whole, and the split rule between Update Set XML and manual build. |
| [`../validation-checklist.md`](../validation-checklist.md) | Success criterion 4 and its provenance evidence, which the loaded rows supply. |
| [`../access-control.md`](../access-control.md) | The role posture of the staging table, which grants read, write, create and delete to `x_bst_startuptrk.admin` alone. |
| [`../api-reference.md`](../api-reference.md) | The Script Include call graph and the full system-property inventory. |
| [`../deployment-runbook.md`](../deployment-runbook.md) | The import sequence that commits the Update Set, and the definition of [what counts as a scheduled run](../deployment-runbook.md#what-counts-as-a-scheduled-run). |
| [`../gaps-and-flags.md`](../gaps-and-flags.md) | The requirements with no clean platform equivalent, including the NewsArticle ingestion exclusion. |
| [`../../../docs/decisions/DECISION_LOG.md`](../../../docs/decisions/DECISION_LOG.md) | The single destination for every "why". |

## Position in the build order

This is **guide 06 of six**, and it is **step 5** of the execution order below. The execution order is **not** the filename order: guide **06** runs before guide **05**. Guide 04 precedes this one; guide 05 follows it, last. The order is stated in full in [`../manual-build-instructions.md`](../manual-build-instructions.md); it is repeated here so this guide can be run without it.

| Step | Guide | Dependency that fixes this position |
| --- | --- | --- |
| 1 | [`01-connection-credential-aliases.md`](01-connection-credential-aliases.md) | The two Connection and Credential Aliases the ingestion flows bind to by name. Nothing downstream can authenticate without them. |
| 2 | [`02-flow-crunchbase-ingestion.md`](02-flow-crunchbase-ingestion.md) | The Crunchbase ingestion flow, which references `x_bst_startuptrk.crunchbase_api` by name. |
| 3 | [`03-flow-linkedin-ingestion.md`](03-flow-linkedin-ingestion.md) | The LinkedIn ingestion flow, which references `x_bst_startuptrk.linkedin_oauth` by name. |
| 4 | [`04-service-portal-pages-and-widgets.md`](04-service-portal-pages-and-widgets.md) | The portal, theme, five pages and eight widgets. |
| **5** | **This guide** | **The staging-table CSV load, which puts rows into `x_bst_startuptrk_ingest_staging` and records on the instance for the portal walkthrough.** |
| 6 | [`05-atf-test-suites.md`](05-atf-test-suites.md) | The Automated Test Framework suites, **last**: they exercise everything the five preceding guides build. |

The single hop where execution order differs from filename order is this one. **The dependency is narrower than "guide 05 needs these rows".** The table below states exactly what needs them and what does not; read it before treating any of these rows as an ATF fixture.

| What needs the rows this guide loads | What it needs them for | Does guide 05's ATF suite read them? |
| --- | --- | --- |
| The **pass 2 data-bearing run** of [`02-flow-crunchbase-ingestion.md`](02-flow-crunchbase-ingestion.md) and [`03-flow-linkedin-ingestion.md`](03-flow-linkedin-ingestion.md) | The exact expected counters those guides assert, which are derived from these files' designed defects | **No** |
| **Success criterion 4** in [`../validation-checklist.md`](../validation-checklist.md) — three consecutive guard-passing scheduled runs per flow with zero unhandled errors | Real scheduled executions need real pending rows to ingest, and their run-summary records are the durable provenance evidence | **No** |
| The **portal walkthrough** of [`04-service-portal-pages-and-widgets.md`](04-service-portal-pages-and-widgets.md) and criterion 5 | Entity records to render | **No** |
| Guide 05's **CRUD, ACL and REST suites** | Nothing. Each creates its own records inside its own test transaction | **No** |
| Guide 05's **two ingestion-flow tests** | Nothing. Each **seeds its own staging rows** under a run token minted per execution and asserts exact counts against them | **No** |

**Guide 05's ingestion tests must not consume this dataset.** Each seeds its own rows under its own `import_run` token, minted per execution, and asserts exact row-for-row counts against them. The two paths cannot collide in either direction: this guide's rows are advanced to `processed` by step 8, and `IngestionMapper.ingestStaging()` reads only rows in state `pending`, so a later ATF run cannot pick them up — and an ATF run's rows are created and rolled back inside its own transaction, so they never reach this dataset's reconciliation. The construction is recorded at `D-112` in [`../../../docs/decisions/DECISION_LOG.md`](../../../docs/decisions/DECISION_LOG.md).

**The ordering holds on the three dependencies in the table above, not on the ATF fixtures.** Guides 02 and 03 are built before this guide, and their pass 2 cannot run until this guide has loaded and transformed; both guides state that and require the data-bearing pass afterwards.

## Preconditions

Do not begin this guide until every item below holds.

| # | Precondition | How to confirm |
| --- | --- | --- |
| 1 | The Update Set has been uploaded and has reached the `loaded` state. | The `sys_remote_update_set` record shows `state` `loaded`. |
| 2 | The preview has completed with an **empty error-type problem set**. | A read of `sys_update_preview_problem` filtered to this remote update set and `type=error` returns an empty `result` array. Warnings are logged and do not block. |
| 3 | The Update Set has **committed**. | The `sys_remote_update_set` record shows `state` `committed`. |
| 4 | **All eleven required post-commit gates have passed.** | Run the eleven required gates in [`../validation-gates.md`](../validation-gates.md) — the seven entity-table reads `GATE-TBL-01` through `GATE-TBL-07`, the three role-record gates `GATE-ROLE-01` through `GATE-ROLE-03`, and the one scope-record gate `GATE-SCOPE-01` — and record `pass` for all eleven in that document's required-gate evidence table. The aggregate pass condition is `11 of 11`; there is no partial pass, and no required gate may be skipped, deferred or waived. |
| 5 | `x_bst_startuptrk_ingest_staging` exists with all **forty-one** of its dictionary columns. | The table opens in the list view through the **Ingestion staging** module of the Boston Startup Tracker application menu, and `sys_dictionary` filtered to `name=x_bst_startuptrk_ingest_staging` with a non-empty `element` returns **41** records — the seven-column control prefix plus the thirty-four flattened columns of [Mapping roll-up](#mapping-roll-up). The table's own collection record carries an empty `element` and is not one of the forty-one. |
| 6 | The two tables the staging-to-entity transform writes for participation exist. | `x_bst_startuptrk_fundinground` and `x_bst_startuptrk_m2m_round_investor` both open in the list view. `GATE-TBL-05` covers the first. |
| 7 | The three Script Includes this guide calls into are on the instance. | `sys_script_include` carries `IngestionMapper`, `IngestionLogger` and `InvestorPortfolioService`, all in the `x_bst_startuptrk` scope. |
| 8 | The three business rules that maintain the derived columns are on the instance and **active**. | `sys_script` carries `Trim and validate startup`, `Recalculate investor portfolio on funding round` and `Recalculate investor portfolio on round investor link`, all `active` true, all in the `x_bst_startuptrk` scope. |
| 9 | You hold the `x_bst_startuptrk.admin` role. | The staging table grants read, write, create and delete to that role **alone**, so this procedure cannot be performed by a caller holding only `x_bst_startuptrk.user` or `x_bst_startuptrk.premium_user`. The posture is Layer 4 of [`../access-control.md`](../access-control.md). |
| 10 | You hold the platform `admin` role and can reach the System Import Sets module. | The application navigator opens **System Import Sets**, with **Load Data**, **Run Transform** and the **Administration** submodules **Data Sources**, **Transform Maps** and **Import Log** all visible. Creating a data source, an import set table and a transform map requires that role. |
| 11 | You are working in the `x_bst_startuptrk` application scope. | The application picker reads **Boston Startup Tracker**. Every data source, import set table and transform map this guide creates must carry that scope. |
| 12 | The six CSV files are available locally. | `crunchbase_startups_sample.csv`, `crunchbase_investors_sample.csv`, `crunchbase_funding_rounds_sample.csv`, `linkedin_founders_sample.csv`, `linkedin_executives_sample.csv` and `linkedin_job_postings_sample.csv`, taken from [`../../sample-data/`](../../sample-data/) **unmodified**. |

Guides 01 through 04 do not have to be complete before this guide runs. Nothing in the load path touches a credential alias, a flow or a portal record. Guides 02 and 03 do have to be complete before the loaded rows can be exercised through a flow, and guide 04 before they can be seen in the portal.

### Capture rule for this artifact class

Only tables carrying the update-synch attribute are captured into `sys_update_xml` records, and adding that attribute to a table that lacks it out of the box is unsupported. A data source, an import set table, a transform map and its field maps are all built through the platform's own interface and sit outside the captured set. The delivered Update Set therefore contains **zero** import records — no `sys_data_source`, no `sys_transform_map` and no `sys_transform_entry`. [`../manual-build-instructions.md`](../manual-build-instructions.md) owns the split rule for the package as a whole, and the decision is recorded at `D-074`.

## What this guide builds

| Artifact | Count | Table | Notes |
| --- | --- | --- | --- |
| Data source | 6 | `sys_data_source` | One per CSV file. Type **File**, format **CSV**, file retrieval method **Attachment**. |
| Import set table | 6 | one per data source, extending `sys_import_set_row` | One per record type. The wizard derives its columns from that file's header row, and the six files carry six different header sets. |
| Transform map | 6 | `sys_transform_map` | One per record type. Source is that record type's import set table; **target is `x_bst_startuptrk_ingest_staging` on all six**. |
| Field map | 19, 12, 16, 14, 14, 17 | `sys_transform_entry` | One per CSV column per map: 92 field maps in total, every one a one-to-one mapping by header name. |
| Import set | 6 | `sys_import_set` | One per load. Created by the load, not by hand. |
| Background script | 1 | not a stored record | The post-load `InvestorPortfolioService.recalculateAll()` invocation of [step 9](#step-9--recalculate-the-derived-portfolio-counts). |

The load writes **one** application table, `x_bst_startuptrk_ingest_staging`, and no other. The staging-to-entity transform of [step 8](#step-8--run-the-staging-to-entity-transform) writes the six entity tables and the one join table, through `IngestionMapper`.

## The three-way staging contract

Three artifacts describe the same set of staging columns. This guide is **leg (c)**.

| Leg | Artifact | Role | Status | Evidence a reader can check |
| --- | --- | --- | --- | --- |
| a | The header rows of the six CSVs, stated in [`../../sample-data/README.md`](../../sample-data/README.md) | The wire format | **Delivered** | Six header rows carrying **92** column positions between them — 19, 12, 16, 14, 14 and 17 — drawn from **41** distinct column names, above **65** data rows. |
| b | The `x_bst_startuptrk_ingest_staging` dictionary records in [`../../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml`](../../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml) | **Authoritative for column names** | **Delivered** | **41** `sys_dictionary` elements on that table, one for each distinct CSV column name, with no CSV header absent from them. |
| c | The field mapping in **this guide** | The load instructions | **Delivered** | [The field mapping, file by file](#the-field-mapping-file-by-file) below, carrying **92** one-to-one maps — one per column position of leg (a). |

The three counts are the check: **92 = 92 = 92** across the legs, over 41 distinct column names. A column present in one leg and absent from another is exactly the silent failure this table exists to prevent. The same table, with the same counts, is stated from leg (a)'s side in [`../../sample-data/README.md`](../../sample-data/README.md).

**Precedence.** The Update Set dictionary is authoritative for column names, types and lengths. [`../../sample-data/README.md`](../../sample-data/README.md) is authoritative for the CSV header rows and their order within each file. This guide must agree with both, and must not introduce a third spelling or a different order. Where this guide and the dictionary disagree, the dictionary is checked against the prompt and the Agent Action Plan first: where the dictionary matches the specification, this guide is corrected to it; where the dictionary departs from it, the dictionary is corrected.

**Operational warning.** A change to any one leg alone breaks the fallback path **silently**. The Data Import Wizard maps columns **by header name**: a renamed, re-cased or misspelled column is left unmapped, the target field loads empty, and **no error is raised** — the load reports success, the row count is correct, and the flows simply find nothing usable in that column. Whenever any one leg changes, re-verify all three: the CSV header row, the dictionary element name, and the field map in this guide. The check is mechanical — read the header row of the file, read `sys_dictionary` for the table, and read the Field Maps related list on the transform map, and confirm the three lists agree name for name.

## The target table

**One** table. Label **Ingestion staging**, name `x_bst_startuptrk_ingest_staging`, display column `import_run`, forty-one columns: the seven-column control prefix plus thirty-four flattened scalar columns. All six record types load into it; `record_type` is the discriminator that tells the staging-to-entity transform which entity table a row becomes and which flattened columns it reads. The full column list with every type and length is in [`../data-model.md`](../data-model.md).

Four properties of the table govern this procedure:

| Property | Value | Consequence for the load |
| --- | --- | --- |
| Mandatory columns | **None** | A row with a blank value loads successfully. The mandatory requirement is enforced per record type at transform time by cleaning rule 4, not at import time. |
| Choice lists | On the four control columns `source_system`, `record_type`, `import_state` and `run_provenance` only | None of the thirty-four flattened columns carries a choice list, so an unmatched choice value loads unchanged and is normalised later by cleaning rule 3. |
| `sys_db_object.access` | `package_private` | The table is unreachable from any other application scope. A background script that touches it must run **inside** the `x_bst_startuptrk` scope. |
| `sys_db_object.ws_access` | `false` | The table is **not** served at `/api/now/table/x_bst_startuptrk_ingest_staging`. Verify the load in the list view; a script written against that path fails whether or not the rows loaded. This posture belongs to the **three supporting tables only** — this table, `x_bst_startuptrk_m2m_round_investor` and `x_bst_startuptrk_rate_limit_counter`. The seven entity tables are delivered `public` with `read_access` and `ws_access` true, so they *are* served there and are governed by their table-level and field-level access controls. The dictionary records in the Update Set are authoritative and [`../data-model.md`](../data-model.md) states the posture table by table. |

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
| 4 | `import_state` | `string`, choice list, dictionary default `pending` | 40 | `pending`, `processed`, `rejected`, `error` — **four** members | **`pending` on every shipped row.** The transform advances it: `IngestionMapper.claimStagingRows()` leases a row it is about to read by writing `run:` plus the run identifier into `import_run`, leaving `import_state` at `pending`, and the row then settles as `processed`, `rejected` or `error`. A leased row is therefore still `pending`, and `pending` is the only value a shipped row carries — see [Returning an abandoned or rejected row to the queue](#returning-an-abandoned-or-rejected-row-to-the-queue). |
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
| Multi-valued fields | Two columns are multi-valued, and **they do not share a carrier**. `focus_areas` is comma separated inside **one RFC 4180 double-quoted field**, a bare comma between values with **no** space after it. `participating_investor_names` is a **JSON array** inside one double-quoted field, because an investor name may itself contain a comma. | `"Fintech,SaaS,Deeptech"` and `"[""Emerald Necklace Angels"", ""Chickatawbut Seed Partners""]"` |
| Integers | Digits only, unquoted, no separators. One column: `founded_year`. | `2019` |
| Designed whitespace | A field carrying an intentional leading or trailing space is **always quoted**, so the space survives the load and reaches cleaning rule 1. Fourteen fields across the six files carry designed whitespace and all fourteen are quoted; they are listed in [Designed whitespace is always quoted](../../sample-data/README.md#designed-whitespace-is-always-quoted). **Never unquote one**: many CSV readers strip surrounding whitespace from an unquoted field, which makes the rule 1 fixture pass without the trim rule doing anything. | `" Example Labs"` |
| URLs | Absolute, including the scheme. | `https://example.com/careers` |
| Empty means absent | An empty field means the value is absent. **No sentinel string is ever used** — `Unknown`, `N/A`, `null` and `None` appear nowhere in these files and must not be introduced. A blank must stay blank through the load so cleaning rule 4 can see it. | `,,` |

The CSV dialect the six files are written in, and which the data sources must be configured to read: RFC 4180; comma field delimiter; double-quote quoting character; a literal double quote inside a quoted field escaped by doubling it; UTF-8 **without** a byte-order mark; LF line endings; exactly one header row, the first line of the file; no comment syntax.

### `raw_payload`

`raw_payload` is a JSON object carried as one double-quoted CSV field with every inner double quote doubled. It uses the **source system's own key vocabulary**, not the flattened platform column names, because the staging shape is required to mimic the expected API response. **Load it verbatim.** Do not reformat it, do not re-indent it, do not re-quote it and do not parse and re-serialise it; the field map is a plain string-to-string mapping.

**The shipped envelope is not the same shape in all six files, and the two shapes below are exactly what the files carry.**

| Files | Envelope the shipped rows carry | What `IngestionMapper.unwrapLive()` reduces it to |
| --- | --- | --- |
| `crunchbase_startups_sample.csv`, `crunchbase_investors_sample.csv`, `crunchbase_funding_rounds_sample.csv` | A single top-level `properties` object: `{"properties":{ ... }}`. There is **no** `data` wrapper, **no** `items` array and **no** `elements` array on any Crunchbase row, and each row carries exactly **one** entity. | The `properties` object itself, as one source object. |
| `linkedin_founders_sample.csv`, `linkedin_executives_sample.csv`, `linkedin_job_postings_sample.csv` | `{"synthetic":true,"data":{"elements":[ ... ]}}`, with **exactly one** member in `elements` on every row. `synthetic` marks the payload as sample data and is not mapped. | Each member of `data.elements`, one source object per member — one per row here. |

`IngestionMapper.unwrapLive()` accepts more shapes than the fixtures use, and it resolves them in this fixed order. Author a new fallback row against this order, not against a remembered example:

1. If the payload carries `data`, that becomes the envelope; otherwise the payload itself is the envelope.
2. The first of `items`, `elements`, `entities` or `results` on the envelope that is an **array** wins, and every member of it becomes one source object.
3. Otherwise, if the envelope carries `properties`, that object becomes the single source object.
4. Otherwise the envelope itself becomes the single source object.

So a live Crunchbase organisation read wrapped as `{"data":{"properties":{...}}}` and a paged read shaped `{"data":{"items":[...]}}` are both accepted, which is why the live path needs no per-source unwrapper. **The shipped fixtures use step 3 for Crunchbase and step 2 for LinkedIn.**

**`raw_payload` is not what the fallback transform maps.** `IngestionMapper.mapStagingRow()` reads the flattened staging columns, which already carry the target vocabulary; nothing in the mapper parses `raw_payload`. The column exists because the staging shape is required to mimic the expected API response, and it lets a row be replayed through `unwrapLive()` and `mapLiveRecord()` to exercise the live mapping path without a live call. A malformed `raw_payload` therefore cannot break the load — and cannot be relied on to be correct either, which is why it is loaded verbatim and never regenerated.

The longest shipped `raw_payload` value is 1830 characters, well inside the column's 8000-character limit, so no value is at risk of truncation on load. Every shipped value parses as JSON, and every one is **minified** — no space follows a colon or a comma.

#### One exact example per record type

Each block below is the `raw_payload` field of the **first data row** of that file, verbatim and on one line, with the CSV's doubled inner quotes resolved to single quotes as a JSON parser sees them. Inside the CSV the same text appears in one double-quoted field with every `"` doubled.

`crunchbase_startups_sample.csv`, `record_type` `startup`, `name` `Beacon Hill Robotics`:

```json
{"properties":{"identifier":{"value":"Beacon Hill Robotics","permalink":"beacon-hill-robotics","uuid":"9ea9e675-7ef7-ddb4-2ad6-d96f177f3810","entity_def_id":"organization"},"facet_ids":["company"],"short_description":"Autonomous inspection robots for commercial building operators.","categories":[{"value":"Science and Engineering","permalink":"science-and-engineering","entity_def_id":"category_group"}],"founded_on":{"value":"2019-01-01","precision":"year"},"location_identifiers":[{"value":"Boston, MA","location_type":"city","permalink":"boston-ma"}],"website":{"value":"https://beaconhillrobotics.example.com"},"image_url":"https://cdn.example.org/logos/beacon-hill-robotics.png","last_funding_type":"series_b","funding_total":{"value":48000000,"currency":"USD","value_usd":48000000},"operating_status":"active","num_employees_enum":"c_00051_c_00200","last_funding_at":"2023-02-21","institutional_funding_last_5yrs":true}}
```

`crunchbase_investors_sample.csv`, `record_type` `investor`, `name` `Emerald Necklace Angels`:

```json
{"properties":{"identifier":{"value":"Emerald Necklace Angels","permalink":"emerald-necklace-angels","uuid":"c36e9309-e2c2-b2fb-29b0-2c836183f5d0","entity_def_id":"organization"},"facet_ids":["investor"],"short_description":"Angel collective backing consumer brands across Greater Boston","investor_type":["angel"],"categories":[{"value":"Consumer Goods","permalink":"consumer-goods","entity_def_id":"category_group"}],"website":{"value":"https://emeraldnecklaceangels.example.org"},"assets_under_management":{"value":18500000.5,"currency":"USD","value_usd":18500000.5}}}
```

`crunchbase_funding_rounds_sample.csv`, `record_type` `funding_round`, the `Seed` round of `Beacon Hill Robotics`:

```json
{"properties":{"identifier":{"value":"Beacon Hill Robotics Seed","permalink":"beacon-hill-robotics-seed","uuid":"a23952e1-bcd5-58cf-7fac-a2c1c2e0e583","entity_def_id":"funding_round"},"funded_organization_identifier":{"value":"Beacon Hill Robotics","permalink":"beacon-hill-robotics","uuid":"9ea9e675-7ef7-ddb4-2ad6-d96f177f3810","entity_def_id":"organization"},"funded_organization_location":[{"value":"Boston, MA","location_type":"city","permalink":"boston-ma"}],"investment_type":"seed","money_raised":{"value":3200000,"currency":"USD","value_usd":3200000},"announced_on":{"value":"2019-11-12","precision":"day"},"lead_investor_identifiers":[{"value":"Emerald Necklace Angels","permalink":"emerald-necklace-angels","uuid":"c36e9309-e2c2-b2fb-29b0-2c836183f5d0","entity_def_id":"organization"}],"investor_identifiers":[{"value":"Emerald Necklace Angels","permalink":"emerald-necklace-angels","uuid":"c36e9309-e2c2-b2fb-29b0-2c836183f5d0","entity_def_id":"organization"},{"value":"Chickatawbut Seed Partners","permalink":"chickatawbut-seed-partners","uuid":"f558c1cc-7cf8-271b-5054-9b305d9a5830","entity_def_id":"organization"}],"pre_money_valuation":{"value":14000000,"currency":"USD","value_usd":14000000},"permalink":"beacon-hill-robotics-seed","source_url":"https://news.example.com/rounds/beacon-hill-robotics-seed"}}
```

`linkedin_founders_sample.csv`, `record_type` `founder`, `name` `Marisol Trevanion`:

```json
{"synthetic":true,"data":{"elements":[{"id":"ln-member-40118","name":"Marisol Trevanion","title":"Chief Executive Officer","summary":"Co-founded Beacon Hill Robotics after a decade in industrial controls, and now leads its commercial strategy.","headline":"CEO at Beacon Hill Robotics","profileUrl":"https://people.example.com/in/marisol-trevanion","companyName":"Beacon Hill Robotics","companyLocation":"Boston, MA","emailAddress":"marisol.trevanion@example.com"}],"paging":{"count":1}}}
```

`linkedin_executives_sample.csv`, `record_type` `executive`, `name` `Perpetua Aldworth`:

```json
{"synthetic":true,"data":{"elements":[{"id":"ln-member-51201","name":"Perpetua Aldworth","title":"Chief Financial Officer","summary":"Oversees financial planning, treasury and investor reporting for the robotics group.","headline":"CFO at Beacon Hill Robotics","profileUrl":"https://people.example.com/in/perpetua-aldworth","companyName":"Beacon Hill Robotics","companyLocation":"Boston, MA","emailAddress":"perpetua.aldworth@example.com"}],"paging":{"count":1}}}
```

`linkedin_job_postings_sample.csv`, `record_type` `job_posting`, `title` `Senior Robotics Software Engineer`:

```json
{"synthetic":true,"data":{"elements":[{"id":"6104701","title":"Senior Robotics Software Engineer","description":"Own the motion planning stack for autonomous inspection platforms.","jobFunction":"eng","location":{"name":"Boston, MA"},"workplaceType":"HYBRID","experienceLevel":"MID_SENIOR_LEVEL","postedAt":"2026-07-21","applyUrl":"https://jobs.example.com/postings/beacon-hill-robotics/senior-robotics-software-engineer","jobState":"LISTED","companyName":"Beacon Hill Robotics","companyLocation":"Boston, MA"}],"paging":{"count":1}}}
```

Carrying **both** the flattened scalar columns and this source-vocabulary JSON column on the same row is a deviation from a literal reading of the requirements: the flattened columns are what make the CSV import a one-to-one mapping by header name, and `raw_payload` is what preserves the source response shape. Both are mapped, on every row of every file. The mechanic is stated here; the decision is recorded in [`../../../docs/decisions/DECISION_LOG.md`](../../../docs/decisions/DECISION_LOG.md).

## References travel as natural keys

A CSV cannot carry a `sys_id` for a record that does not exist yet, so **every reference travels as the target record's natural key — and no column in any of the six files carries a `sys_id`.** Four columns are natural keys, and the first two are two halves of one key:

| Column | Files that carry it | Resolves to | Written to |
| --- | --- | --- | --- |
| `startup_name` | `crunchbase_funding_rounds_sample.csv`, `linkedin_founders_sample.csv`, `linkedin_executives_sample.csv`, `linkedin_job_postings_sample.csv` | One `x_bst_startuptrk_startup` record, matched on `name` **together with** `startup_headquarters_location` | The `startup` reference on the child record. The name itself is not written to the child. |
| `startup_headquarters_location` | The same four child files | The second half of the Startup key, matched against `x_bst_startuptrk_startup.headquarters_location` | Nothing. It is a transport value that resolves the parent reference and is then discarded. |
| `lead_investor_name` | `crunchbase_funding_rounds_sample.csv` | One `x_bst_startuptrk_investor` record, matched on `name` | `x_bst_startuptrk_fundinground.lead_investor` |
| `participating_investor_names` | `crunchbase_funding_rounds_sample.csv` | One `x_bst_startuptrk_investor` record **per member of the JSON array** | One `x_bst_startuptrk_m2m_round_investor` row per resolved member |

**The import maps these three columns as plain strings into the staging columns of the same names.** No resolution happens at import time. Resolution happens in the staging-to-entity transform, in `IngestionMapper`, and this is what it does:

| Column | Resolution | When nothing matches |
| --- | --- | --- |
| `startup_name` **plus** `startup_headquarters_location` | `IngestionMapper.resolveStartupKey()` matches both halves against `x_bst_startuptrk_startup.name` and `.headquarters_location`, trimming and lowering both sides of both halves, and resolves **only when exactly one** startup carries the pair. **Both halves are required.** A row that leaves `startup_headquarters_location` blank does not identify a parent and is rejected before any read; there is no name-only fallback. | The row is **rejected** and logged as a skip, and **no entity record is created**. The reason recorded is `no startup carries the name and headquarters location` when the pair matches nothing, `the name and headquarters location already match (<n> startup records)` when the pair matches more than one, and `the row carries no parent headquarters location, and the startup key is the name together with the headquarters location` when the second half is blank — which names the remedy. In every ambiguous case **no candidate is chosen**. `startup` is a mandatory value on all four child record types, so an unresolved parent is always a rejection. |
| `lead_investor_name` | `IngestionMapper.resolveInvestor()`, on the same exactly-one-match policy against `x_bst_startuptrk_investor.name`. | The reference is **left unwritten** and a warning is logged naming the reason. **The funding round is still created**, without a lead investor. The value is not written as a blank, because an ingestion run never clears a stored value. |
| Each member of `participating_investor_names` | `IngestionMapper.resolveParticipants()` reads the field as a list in one of three accepted carriers — a JSON array, which is what the shipped file uses, a `\|`-delimited string, or a single bare name — trims each member, drops an empty member, resolves each remaining member to exactly one Investor and keeps a repeated member once. **It never splits on a comma**, because an organisation name may contain one. | An unresolved member is logged as a warning naming the reason and **contributes no join row**. The members that do resolve still become join rows, and the count of unresolved members is carried back so the round is recorded as partial rather than complete. |

**A natural key is never read as a record identifier.** A value that happens to be 32 hexadecimal characters is still matched against the `name` column, so it resolves only if a record is genuinely named that. Supplying a `sys_id` in one of these columns is a data error the transform reports, not a shortcut it honours.

Both sides of every comparison are trimmed and lowered, so a child row may spell its natural key in any case and with any surrounding whitespace. Several shipped rows deliberately do, which is what makes them evidence that trimming happens before resolution. One founders row spells its parent location `seaport, boston, ma` in lower case with a leading segment the Startup record does not carry in that case, and it still resolves, because the comparison is normalised on both sides.

**The parent key is both halves: `startup_name` and `startup_headquarters_location`.** Cleaning rule 2 deduplicates Startup records on `name` plus `headquarters_location`, so the parent is identified by that pair and a child row must state both halves of it. `startup_headquarters_location` is **never written to the child record** — the child tables carry no location column.

**No shipped row isolates the blank-second-half rejection, and that is worth stating rather than implying.** Five child rows across the four child files leave `startup_headquarters_location` blank, but every one of them also leaves a mandatory column blank — `startup_name` on four of them and `name` on the Kendall Cognition executive — so cleaning rule 4 rejects each of them **before** reference resolution runs, and the reason recorded names the missing mandatory column rather than the missing key half. The blank-second-half rejection is asserted directly against `IngestionMapper.resolveStartupKey()` in the ingestion suites of [`./05-atf-test-suites.md`](./05-atf-test-suites.md), which is where a resolver rule belongs; it is not observable from this load.

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
| **Choice action** | The four control columns `source_system`, `record_type`, `import_state` and `run_provenance` — the only staging columns carrying a choice list | **`reject`**, so an out-of-list value in a control column keeps the row out of the table and out of the flows. `create` must **not** be used: it adds a `sys_choice` record, and the choice inventory is binding and complete. |
| Choice action | The thirty-four flattened columns | Not applicable. None of them carries a choice list. |
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
| 7 | `raw_payload` | `raw_payload` | `string` 8000 | no | JSON carrying a single top-level `properties` object. Verbatim — see [`raw_payload`](#raw_payload). |
| 8 | `name` | `name` | `string` 100 | **yes** | Writes `x_bst_startuptrk_startup.name`. First half of the cleaning-rule-2 deduplication key. |
| 9 | `description` | `description` | `string` 4000 | no | Writes `x_bst_startuptrk_startup.description`. |
| 10 | `industry` | `industry` | `string` 40 | no | Target choice list `Fintech`, `Healthtech`, `SaaS`, `Consumer`, `Deeptech`, `Other`. Normalised at transform time, not here. |
| 11 | `founded_year` | `founded_year` | `integer` | no | Four-digit year. |
| 12 | `headquarters_location` | `headquarters_location` | `string` 100 | **yes** | Writes `x_bst_startuptrk_startup.headquarters_location`. Second half of the deduplication key. This column is read by the `startup` record type only. A child file states the **parent's** location in the separate `startup_headquarters_location` column and never in this one. |
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
| 7 | `raw_payload` | `raw_payload` | `string` 8000 | no | JSON carrying a single top-level `properties` object. Verbatim — see [`raw_payload`](#raw_payload). |
| 8 | `name` | `name` | `string` 100 | **yes** | Writes `x_bst_startuptrk_investor.name`. The only mandatory value for this record type, and the natural key `lead_investor_name` and `participating_investor_names` resolve against. |
| 9 | `type` | `type` | `string` 30 | no | Target choice list `VC`, `Angel`, `PE`, `Corporate`, `Accelerator`. |
| 10 | `focus_areas` | `focus_areas` | `string` 255 | no | Multi-valued: comma separated inside one quoted field, each member one of the six `Startup.industry` values. Load verbatim; the transform normalises member by member. |
| 11 | `website` | `website` | `string` 255 | **yes** | Writes `x_bst_startuptrk_investor.website`. |
| 12 | `aum_usd` | `aum_usd` | `decimal` | no | Plain USD. Premium-gated on the entity record. |

**`portfolio_count` is deliberately absent from this file, from the staging dictionary and from every field map in this guide.** `x_bst_startuptrk_investor.portfolio_count` is calculated, not imported: it is derived by `InvestorPortfolioService` and maintained by the two portfolio business rules. The column is read-only in the dictionary, so a field map that targeted it would be refused. Its value is established by [step 9](#step-9--recalculate-the-derived-portfolio-counts).

**The `Investor.type` choice list has no `Other` member.** Its five values are `VC`, `Angel`, `PE`, `Corporate` and `Accelerator`, and one shipped row deliberately carries a sixth value that matches none of them. Because the list offers no `Other` to normalise to, that value is **logged and the field left unwritten** — it is not coerced. The record is still created; an unwritten choice column is not a rejection. Do **not** add an `Other` choice to this list. Five other choice lists behave the same way: `Startup.funding_stage`, `Startup.employee_count_range`, `FundingRound.round_type`, `JobPosting.remote_type` and `JobPosting.seniority`.

One of the eight rows deliberately blanks `name`. **Seven** Investor records result.

### 3. `crunchbase_funding_rounds_sample.csv`

`source_system` is `crunchbase` and `record_type` is `funding_round` on every row. **Sixteen** columns: the seven-column control prefix plus nine flattened columns. **12** data rows.

```text
source_system,record_type,import_run,import_state,run_provenance,error_message,raw_payload,startup_name,startup_headquarters_location,round_type,amount_usd,valuation_usd,round_date,lead_investor_name,participating_investor_names,source_url
```

| # | CSV column | Target staging column | Staging type and length | Coalesce | Notes |
| --- | --- | --- | --- | --- | --- |
| 1 | `source_system` | `source_system` | `string` 40, choice | no | Constant `crunchbase`. Choice action `reject`. |
| 2 | `record_type` | `record_type` | `string` 40, choice | no | Constant `funding_round`. Choice action `reject`. |
| 3 | `import_run` | `import_run` | `string` 64 | **yes** | Constant `fallback-sample-crunchbase-funding-rounds`. |
| 4 | `import_state` | `import_state` | `string` 40, choice | no | Constant `pending`. Choice action `reject`. |
| 5 | `run_provenance` | `run_provenance` | `string` 40, choice | no | Constant `fallback`. Choice action `reject`. |
| 6 | `error_message` | `error_message` | `string` 1000 | no | Empty on every row. |
| 7 | `raw_payload` | `raw_payload` | `string` 8000 | no | JSON carrying a single top-level `properties` object, the same shape as the other two Crunchbase files. Verbatim — see [`raw_payload`](#raw_payload). |
| 8 | `startup_name` | `startup_name` | `string` 100 | **yes** | **Natural key, first half.** Resolves to `x_bst_startuptrk_fundinground.startup`. Mandatory for this record type at transform time. |
| 9 | `startup_headquarters_location` | `startup_headquarters_location` | `string` 100 | no | **Natural key, second half.** The parent Startup's `headquarters_location`, not the round's. Resolves the `startup` reference and is then discarded — it is written to no column of the funding round. Optional in the **dictionary** and required by the **resolver**: a blank identifies no parent and rejects the row. One of the twelve rows leaves it blank — the same row that also leaves `startup_name` blank, so rule 4 rejects it first. |
| 10 | `round_type` | `round_type` | `string` 40 | **yes** | Target choice list `Pre-Seed`, `Seed`, `Series A`, `Series B`, `Series C+`, `Growth`, `Public`, `Acquired`. The same eight values as `Startup.funding_stage`, and no `Other` member. |
| 11 | `amount_usd` | `amount_usd` | `decimal` | no | Plain USD. Premium-gated on the entity record. |
| 12 | `valuation_usd` | `valuation_usd` | `decimal` | no | Plain USD. Premium-gated on the entity record. |
| 13 | `round_date` | `round_date` | `glide_date` | **yes** | ISO 8601 `YYYY-MM-DD`. Field-map date format `yyyy-MM-dd`. Mandatory for this record type at transform time. |
| 14 | `lead_investor_name` | `lead_investor_name` | `string` 100 | no | **Natural key.** Resolves to `x_bst_startuptrk_fundinground.lead_investor`, a first-class single reference. Optional. |
| 15 | `participating_investor_names` | `participating_investor_names` | `string` 1000 | no | **Multi-valued natural key.** A **JSON array of investor names** inside one quoted field, the inner double quotes doubled per RFC 4180. Becomes one `x_bst_startuptrk_m2m_round_investor` row per resolved member. Optional; an empty field means no participants, and the eleventh data row leaves it empty. Load the string **verbatim** — nothing may re-format, re-quote or re-delimit it in transit, and in particular nothing may convert it to a comma-separated list, because a member name may contain a comma. |
| 16 | `source_url` | `source_url` | `string` 255 | no | Writes `x_bst_startuptrk_fundinground.source_url`. |

`lead_investor_name` and `participating_investor_names` are **distinct columns with distinct destinations**, and both must be mapped. The lead investor is a single reference column on the funding round; each participating investor becomes one row of the join table. An investor may legitimately appear in both columns on the same row. Neither is ever written to `x_bst_startuptrk_fundinground.participating_investors`, which is a read-only projection maintained by the business rule on the join table.

Two columns are mandatory for the `funding_round` record type at transform time: `startup_name` and `round_date`. Two of the twelve rows deliberately blank one each. **Ten** FundingRound records result, and **26** join rows across them. The largest single round links five participating investors.

### 4. `linkedin_founders_sample.csv`

`source_system` is `linkedin` and `record_type` is `founder` on every row. **Fourteen** columns: the seven-column control prefix plus seven flattened columns. **10** data rows.

```text
source_system,record_type,import_run,import_state,run_provenance,error_message,raw_payload,name,startup_name,startup_headquarters_location,title,bio,linkedin_url,contact_email
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
| 9 | `startup_name` | `startup_name` | `string` 100 | **yes** | **Natural key, first half.** Resolves to `x_bst_startuptrk_founder.startup`. Mandatory for this record type at transform time. Do **not** map it to `name`; see [Operational warnings](#operational-warnings). |
| 10 | `startup_headquarters_location` | `startup_headquarters_location` | `string` 100 | no | **Natural key, second half.** The parent Startup's `headquarters_location`. Resolves the `startup` reference and is then discarded — `x_bst_startuptrk_founder` has no location column. Optional in the **dictionary** and required by the **resolver**: a blank identifies no parent and rejects the row. One of the ten rows leaves it blank — the same row that also leaves `startup_name` blank, so rule 4 rejects it first — and one spells it in lower case to exercise the case-insensitive match. |
| 11 | `title` | `title` | `string` 150 | no | Target choice list `CEO`, `CTO`, `COO`, `Co-Founder`, `Other`. |
| 12 | `bio` | `bio` | `string` 2000 | no | Writes `x_bst_startuptrk_founder.bio`. |
| 13 | `linkedin_url` | `linkedin_url` | `string` 255 | no | Writes `x_bst_startuptrk_founder.linkedin_url`. |
| 14 | `contact_email` | `contact_email` | `string` 100 | no | Premium-gated on the entity record. |

Two columns are mandatory for the `founder` record type at transform time: `name` and `startup_name`. Two of the ten rows deliberately blank one each. **Eight** Founder records result.

### 5. `linkedin_executives_sample.csv`

`source_system` is `linkedin` and `record_type` is `executive` on every row. **Fourteen** columns — **the same column set as `linkedin_founders_sample.csv`**, in the same order. **10** data rows. The one substantive difference is that **the `title` choice list differs**: the target here is `Executive.title`, not `Founder.title`.

```text
source_system,record_type,import_run,import_state,run_provenance,error_message,raw_payload,name,startup_name,startup_headquarters_location,title,bio,linkedin_url,contact_email
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
| 9 | `startup_name` | `startup_name` | `string` 100 | **yes** | **Natural key, first half.** Resolves to `x_bst_startuptrk_executive.startup`. Mandatory for this record type at transform time. |
| 10 | `startup_headquarters_location` | `startup_headquarters_location` | `string` 100 | no | **Natural key, second half.** The parent Startup's `headquarters_location`. Resolves the `startup` reference and is then discarded — `x_bst_startuptrk_executive` has no location column. Optional in the **dictionary** and required by the **resolver**: a blank identifies no parent and rejects the row. Two of the ten rows leave it blank; both are rejected by rule 4 first, one for a blank `name` and one for a blank `startup_name`. |
| 11 | `title` | `title` | `string` 150 | no | Target choice list **`CFO`, `VP Engineering`, `VP Sales`, `VP Marketing`, `Head of Product`, `Other`** — a different list from the founders file. |
| 12 | `bio` | `bio` | `string` 2000 | no | Writes `x_bst_startuptrk_executive.bio`. |
| 13 | `linkedin_url` | `linkedin_url` | `string` 255 | no | Writes `x_bst_startuptrk_executive.linkedin_url`. |
| 14 | `contact_email` | `contact_email` | `string` 100 | no | Premium-gated on the entity record. |

Founder and Executive are separate entity tables and separate record types, and they stay separate through the staging layer. `record_type` is the only thing that distinguishes these two files' rows once they are in the table, so an incorrect constant in that column sends every row of the file to the wrong entity table. **Eight** Executive records result.

### 6. `linkedin_job_postings_sample.csv`

`source_system` is `linkedin` and `record_type` is `job_posting` on every row. **Seventeen** columns: the seven-column control prefix plus ten flattened columns. **12** data rows.

```text
source_system,record_type,import_run,import_state,run_provenance,error_message,raw_payload,startup_name,startup_headquarters_location,title,department,location,remote_type,seniority,posted_date,url,active
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
| 8 | `startup_name` | `startup_name` | `string` 100 | **yes** | **Natural key, first half.** Resolves to `x_bst_startuptrk_jobposting.startup`. Mandatory for this record type at transform time. |
| 9 | `startup_headquarters_location` | `startup_headquarters_location` | `string` 100 | no | **Natural key, second half.** The parent Startup's `headquarters_location`, **not** the posting's own `location`, which is a separate column further down this table. Resolves the `startup` reference and is then discarded. Optional in the **dictionary** and required by the **resolver**: a blank identifies no parent and rejects the row. One of the twelve rows leaves it blank — the same row that also leaves `startup_name` blank, so rule 4 rejects it first. |
| 10 | `title` | `title` | `string` 150 | **yes** | Free text, **not** a choice column on this record type. Writes `x_bst_startuptrk_jobposting.title`. Mandatory for this record type at transform time. |
| 11 | `department` | `department` | `string` 40 | no | Target choice list `Engineering`, `Sales`, `Marketing`, `Product`, `Operations`, `Other`. |
| 12 | `location` | `location` | `string` 100 | no | Writes `x_bst_startuptrk_jobposting.location`. |
| 13 | `remote_type` | `remote_type` | `string` 20 | no | Target choice list `Onsite`, `Hybrid`, `Remote`. No `Other` member. |
| 14 | `seniority` | `seniority` | `string` 20 | no | Target choice list `Entry`, `Mid`, `Senior`, `Lead`, `Executive`. No `Other` member. |
| 15 | `posted_date` | `posted_date` | `glide_date` | no | ISO 8601 `YYYY-MM-DD`. Field-map date format `yyyy-MM-dd`. Optional. |
| 16 | `url` | `url` | `string` 255 | no | Writes `x_bst_startuptrk_jobposting.url`. |
| 17 | `active` | `active` | `string` **10** | no | Carries the text `true` or `false`. Optional here: a blank is left unset so the `x_bst_startuptrk_jobposting.active` dictionary default `true` applies. |

Two columns are mandatory for the `job_posting` record type at transform time: `startup_name` and `title`. Two of the twelve rows deliberately blank one each. **Ten** JobPosting records result.

### The coalesce key per record type

The coalesce columns make a **re-load update the existing staging row rather than insert a second one**. Set `Coalesce` to true on exactly the columns listed for that record type, and false on every other field map of that map. Where a map coalesces on more than one column, the platform matches on the combination.

| Record type | Coalesce columns | Rows the key must separate |
| --- | --- | --- |
| `startup` | `import_run` + `name` + `headquarters_location` + `website` | 13 |
| `investor` | `import_run` + `name` + `website` | 8 |
| `funding_round` | `import_run` + `source_url`, falling back to `import_run` + `startup_name` + `round_date` | 12 |
| `founder` | `import_run` + `name` + `startup_name` | 10 |
| `executive` | `import_run` + `name` + `startup_name` | 10 |
| `job_posting` | `import_run` + `startup_name` + `title` | 12 |

Two properties of these keys are load-bearing and must survive any edit to them.

**`import_run` is in every key.** All six files load into one table, and nine columns — `name`, `website`, `active`, `title`, `bio`, `linkedin_url`, `contact_email`, `startup_name` and `startup_headquarters_location` — are shared by more than one record type. Without `import_run` in the key, a row of one file could coalesce onto a row of another: an investor and a startup that happen to share a `name`, for instance, would collapse into a single row. `import_run` is constant per file and distinct per file, so including it scopes every match to the file that supplied the row.

**The `startup` key includes `website`. Do not remove it, and do not shorten the key to match cleaning rule 2.** Cleaning rule 2 deduplicates Startup records on `name` plus `headquarters_location`, and `crunchbase_startups_sample.csv` carries a designed pair of rows matching on exactly that pair while differing on `website`. A coalesce key of `import_run` + `name` + `headquarters_location` collapses that pair into **one** staging row at import time: the file loads as 12 rows instead of 13, the rule 2 fixture is gone before the rule that exists to catch it runs, and **the load reports success**. `website` is the one column the pair differs on, so it separates them. The duplicate is resolved by cleaning rule 2 at transform time, never by the import. The choice is recorded at `D-124` in [`../../../docs/decisions/DECISION_LOG.md`](../../../docs/decisions/DECISION_LOG.md), and [`../../sample-data/README.md`](../../sample-data/README.md) is authoritative for the 13-row count.

**`startup_headquarters_location` is not a coalesce component.** It is a resolution input, not an identifying one: the four child keys above separate every shipped row without it, and a row that states the parent location and a row that omits it are the same child row. Set `Coalesce` to false on all four of its field maps.

Across all six files the keys above yield **65 distinct values over 65 rows**, with no collision within a file, no collision between files, and no row whose key is blank in every non-`import_run` component. Adding the parent-location column changed none of those counts, because it is not part of any key.

### Mapping roll-up

Every column of every file is mapped, and every mapped column is a staging dictionary element.

| File | Record type | CSV columns | Control | Flattened | Data rows |
| --- | --- | --- | --- | --- | --- |
| `crunchbase_startups_sample.csv` | `startup` | 19 | 7 | 12 | 13 |
| `crunchbase_investors_sample.csv` | `investor` | 12 | 7 | 5 | 8 |
| `crunchbase_funding_rounds_sample.csv` | `funding_round` | 16 | 7 | 9 | 12 |
| `linkedin_founders_sample.csv` | `founder` | 14 | 7 | 7 | 10 |
| `linkedin_executives_sample.csv` | `executive` | 14 | 7 | 7 | 10 |
| `linkedin_job_postings_sample.csv` | `job_posting` | 17 | 7 | 10 | 12 |
| **Total field maps** | — | **92** | 42 | 50 | **65** |

The fifty flattened field maps address **thirty-four** distinct staging columns, because nine columns are shared by more than one record type and are declared once on the table. The nine account for exactly the sixteen-map difference between 50 and 34:

| Shared staging column | Read by record types | Maps beyond the first |
| --- | --- | --- |
| `name` | `startup`, `investor`, `founder`, `executive` | 3 |
| `website` | `startup`, `investor` | 1 |
| `active` | `startup`, `job_posting` | 1 |
| `title` | `founder`, `executive`, `job_posting` | 2 |
| `bio` | `founder`, `executive` | 1 |
| `linkedin_url` | `founder`, `executive` | 1 |
| `contact_email` | `founder`, `executive` | 1 |
| `startup_name` | `funding_round`, `founder`, `executive`, `job_posting` | 3 |
| `startup_headquarters_location` | `funding_round`, `founder`, `executive`, `job_posting` | 3 |

Thirty-four flattened columns plus the seven control columns is the table's full width of forty-one. **`portfolio_count` appears in no file, in no field map and in no column of this table.**

## Load order

**The load order is a hard sequence, not a preference.** Child rows carry natural-key references to Startup and Investor records, and the staging-to-entity transform resolves a reference only against a record that **already exists as an entity record**. A staged parent row is not enough: the parent must have been transformed.

The sequence is therefore expressed as **four dependency groups**, and a group is fully finished — imported *and* transformed to entity records — before the next group begins.

| Group | Files | Record type | Depends on | What it depends on it for |
| --- | --- | --- | --- | --- |
| **A** | `crunchbase_startups_sample.csv` | `startup` | Nothing | **First**, because every other file references its `name` values through `startup_name`. Until the Startup **entity** records exist, every child row's parent reference is unresolvable and the row is rejected. |
| **B** | `crunchbase_investors_sample.csv` | `investor` | Nothing | Before group C, which references its `name` values through `lead_investor_name` and `participating_investor_names`. Run it second, in the stated sequence. |
| **C** | `crunchbase_funding_rounds_sample.csv` | `funding_round` | **A and B** | It references both parents — Startup through `startup_name`, and Investor through `lead_investor_name` and `participating_investor_names` — so both preceding groups must be imported **and transformed** first. |
| **D** | `linkedin_founders_sample.csv`, `linkedin_executives_sample.csv`, `linkedin_job_postings_sample.csv` | `founder`, `executive`, `job_posting` | **A** | Each references only `startup_name`. All three are imported, then transformed together by a single LinkedIn transform call, because none of the three references either of the others. |

Two properties of this grouping govern how the groups are run.

- **Within group D the three files are independent**, so they are imported in any order and settled by **one** transform rather than three. The transform selects on `source_system` `linkedin`, which covers all three record types in a single pass.
- **Group D depends on group A only**, so it may run before or after groups B and C. Running it last keeps the sequence linear and keeps the funding-round join rows — the check most likely to reveal a mapping fault — adjacent to the files that produce them.

[Step 7](#step-7--run-the-dependency-group-sequence) is the executable form of this table, and it is the step that interleaves the import of steps 1 through 6 with the transform of [step 8](#step-8--run-the-staging-to-entity-transform).

### There is no NewsArticle CSV

**There are exactly six CSV files, and none of them is a NewsArticle file.** Automated NewsArticle ingestion is out of scope: no ingestion flow serves `x_bst_startuptrk_newsarticle`, the staging table's `record_type` choice list contains **no** `news_article` member, and there is consequently no seventh sample file, no seventh data source, no seventh import set table and no seventh transform map. **NewsArticle records are created by manual entry** — through the **News articles** module of the Boston Startup Tracker application menu — or by a REST write to the `/news` resource. The absence is intentional. It is recorded in [`../gaps-and-flags.md`](../gaps-and-flags.md) and in [`../../../docs/decisions/DECISION_LOG.md`](../../../docs/decisions/DECISION_LOG.md).

## Steps

**The nine steps are not run strictly in numerical order, and the order they *are* run in is [step 7](#step-7--run-the-dependency-group-sequence).** Read this before starting.

| Steps | What they are | How often they run |
| --- | --- | --- |
| **1 to 6** | The import of **one** file: create the data source, create the import set table, create the transform map, map the fields, load, verify the staged rows. | Once per file, six times in total. Each file gets its own data source, its own import set table and its own transform map, because the six files carry six different header sets. |
| **7** | **The sequence.** It walks the four dependency groups of [Load order](#load-order), running steps 1 to 6 for each file of a group and then step 8 for that group. | Once. It is the outer loop. |
| **8** | The staging-to-entity transform for **one source system**, scoped to one group's `import_run` values. | Once per dependency group, four times in total. |
| **9** | The portfolio-count reconciliation. | Once, after group C and group D have both settled. |

So step 8 is reached three times before step 7 is finished, which is deliberate: a child row's parent must be an entity record, not a staged row, and only step 8 makes it one. Steps 1 to 6 and steps 8 and 9 are written as reference procedures; step 7 is the order in which they are invoked.

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

Save the record, then attach the CSV to it with the paperclip control. Attach the file **unmodified**, exactly as it sits in [`../../sample-data/`](../../sample-data/). Do not open it in a spreadsheet application and re-save it: doing so commonly rewrites the line endings to CRLF, adds a byte-order mark, re-quotes fields the dialect leaves unquoted, **unquotes or strips the designed leading and trailing spaces the rule 1 fixtures depend on**, and reformats the ISO dates into a locale format. Any one of those breaks a fixture or a field map.

### Step 2 — create the import set table

Use the **Test Load 20 Records** related link on the data source. The platform reads the header row, creates the import set table with one string column per header, and loads the file's rows into it — all 13, 8, 12, 10, 10 or 12, since no file exceeds twenty rows.

Confirm three things before continuing:

- The import set table carries **one column per CSV header**: 19, 12, 16, 14, 14 or 17 respectively.
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

With the transform map saved, use the **Auto map matching fields** related link. Because every CSV header is spelled exactly as its staging dictionary element, the automatic mapping resolves every column of every file, and the Field Maps related list should show 19, 12, 16, 14, 14 or 17 entries with nothing left over.

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

**Verify in the list view, not over the Table API.** The staging table ships with `ws_access` false, so `GET /api/now/table/x_bst_startuptrk_ingest_staging` does not serve it and a script written against that path fails whether or not the rows loaded. The posture is set by the table's dictionary record in the Update Set and is stated in [The target table](#the-target-table); no post-commit gate reads this table.

Check all six of the following on the rows of that `import_run`:

| # | Check | Expected |
| --- | --- | --- |
| 1 | Row count | The count for that file in the [Mapping roll-up](#mapping-roll-up). |
| 2 | `source_system` | The same constant on every row — `crunchbase` or `linkedin`. |
| 3 | `record_type` | The same constant on every row, and the one this file's record type requires. |
| 4 | `import_state` | **`pending`** on every row. Nothing has transformed them yet. |
| 5 | `run_provenance` | **`fallback`** on every row. No row carries `live`. |
| 6 | `error_message` | Empty on every row. |

Then spot-check that the flattened columns actually carry values. Open two or three rows and confirm the columns that file maps are populated and the columns it does not map are empty. **A column that is empty on every row of the file is the signature of an unmapped or misnamed field map**, not of missing data — the load reports success either way, which is what makes the check necessary. Confirm in particular that `raw_payload` holds a JSON object rather than an empty string, and that on the funding-rounds file `participating_investor_names` holds a JSON array — a value beginning `["` and ending `"]` — rather than a comma-separated list, which is the signature of a value re-delimited in transit.

### Step 7 — run the dependency-group sequence

**This step is the order of the whole procedure.** Run the twelve actions below exactly in this order. Each `import` action is steps 1 through 6 for that file; each `transform` action is [step 8](#step-8--run-the-staging-to-entity-transform) with the arguments named in the row.

| # | Action | File or scope | Then |
| --- | --- | --- | --- |
| 1 | **import** | `crunchbase_startups_sample.csv` | Sixty-five rows are not yet staged; thirteen are. Confirm step 6's six checks on them. |
| 2 | **transform** | source `crunchbase`, `import_run` `fallback-sample-crunchbase-startups` | Nine Startup entity records exist. Every child row's `startup_name` can now resolve. |
| 3 | **import** | `crunchbase_investors_sample.csv` | Confirm step 6's six checks. |
| 4 | **transform** | source `crunchbase`, `import_run` `fallback-sample-crunchbase-investors` | Seven Investor entity records exist. `lead_investor_name` and `participating_investor_names` can now resolve. |
| 5 | **import** | `crunchbase_funding_rounds_sample.csv` | Confirm step 6's six checks. |
| 6 | **transform** | source `crunchbase`, `import_run` `fallback-sample-crunchbase-funding-rounds` | Ten FundingRound records and twenty-six join rows exist. |
| 7 | **import** | `linkedin_founders_sample.csv` | Confirm step 6's six checks. |
| 8 | **import** | `linkedin_executives_sample.csv` | Confirm step 6's six checks. |
| 9 | **import** | `linkedin_job_postings_sample.csv` | Confirm step 6's six checks. All sixty-five rows are now staged; thirty-two of them are still `pending`. |
| 10 | **transform** | source `linkedin`, `import_run` left **empty** | One call settles all three LinkedIn files. Eight Founder, eight Executive and ten JobPosting records exist. |
| 11 | **step 9** | — | `InvestorPortfolioService.recalculateAll()` returns `0` on a load whose business rules ran. |
| 12 | **verify** | — | Run all five checks of [Verification after the load](#verification-after-the-load). |

Three rules govern the sequence, and breaking any one of them produces rejected child rows rather than an error.

1. **Never import a child file before its parent group has been transformed.** A `startup_name` resolves against `x_bst_startuptrk_startup`, not against the staging table. Importing early is harmless; *transforming* early is what rejects the rows.
2. **Pass the `import_run` on every Crunchbase transform.** Groups A, B and C all carry `source_system` `crunchbase`, so a transform called with an empty `import_run` after group A's import would settle group A's rows correctly and then, on the next call, find nothing left — or, if groups were imported ahead of time, settle a child group before its parent. Scoping each Crunchbase call to one `import_run` is what keeps the three groups separable.
3. **Leave the `import_run` empty on the LinkedIn transform.** All three group D files share `source_system` `linkedin` and none references another, so one unscoped call is correct and is one call rather than three.

A row that was rejected because the sequence was broken is recoverable: fix the ordering, return the row to the queue as [Returning an abandoned or rejected row to the queue](#returning-an-abandoned-or-rejected-row-to-the-queue) sets out, and transform again.

### Step 8 — run the staging-to-entity transform

The import of steps 1 through 6 puts rows into `x_bst_startuptrk_ingest_staging` with `import_state` `pending`. It creates **no** entity record. The staging-to-entity step is a separate operation, and it is the same code path both ingestion flows use on their fallback branch: `IngestionMapper.ingestStaging()`.

This step is invoked from [step 7](#step-7--run-the-dependency-group-sequence), once per dependency group, with the arguments that step names.

Two ways to run it, and both are acceptable evidence:

- **Through the flows.** Set the property `x_bst_startuptrk.ingestion.source_mode` to `fallback`, then run the Crunchbase flow of [`02-flow-crunchbase-ingestion.md`](02-flow-crunchbase-ingestion.md) and the LinkedIn flow of [`03-flow-linkedin-ingestion.md`](03-flow-linkedin-ingestion.md). Each claims the pending rows of its own `source_system`, applies the four cleaning rules, writes the entity records, records each row's outcome and publishes a run summary. A flow reads **every** unleased pending row of its source, so this route cannot scope a call to one `import_run` and is therefore usable only where a whole source system's groups are ready to settle together. **Leave the property at `fallback` afterwards unless the readiness rule of [Restoring `source_mode`](#restoring-source_mode-is-readiness-determined-not-a-return-to-live) requires `live`** — on the instance recorded for this delivery it requires `fallback`, so there is nothing to restore.
- **Directly, from a background script inside the scope**, one call per dependency group. This is the route [step 7](#step-7--run-the-dependency-group-sequence) uses, because it takes the `import_run` scope the sequence depends on.

#### The run identifier must begin with the source system

**`IngestionLogger.sourceOfRun(sourceSystem)` returns the supplied source system when the caller names one, and otherwise the text before the run identifier's first hyphen.** `IngestionMapper.ingest()` always names it, so a run summary written through `ingestStaging()` carries the right source whatever the identifier looks like. The prefix still matters, for two reasons that are not theoretical:

| # | What the source-system prefix establishes |
| --- | --- |
| 1 | **Any code path that has no source system to name falls back to the prefix.** An identifier such as `manual-load-<guid>` resolves to the source `manual`, which is not one of `crunchbase` or `linkedin`, so a completion marker written under it is refused and a log line attributed to it names a source that does not exist. |
| 2 | **The identifier is the correlation key across three surfaces** — the `import_run` column on the staging row, the run summary event, and every per-record log line. An identifier that does not name its source makes a log line unattributable by inspection. |

Compose the identifier as `<source>-manual-<numeric timestamp>`: the source system, the literal `manual` marking the route, and `new GlideDateTime().getNumericValue()` for uniqueness. Do **not** use `gs.generateGUID()` as the leading token, and do not use a fixed literal such as `manual-load`.

#### The script

Run this from **System Definition > Scripts - Background** with the scope selector on that page set to **Boston Startup Tracker**. Change `SOURCE` and `IMPORT_RUN` for each of the four calls [step 7](#step-7--run-the-dependency-group-sequence) names; pass `IMPORT_RUN` as the empty string for the LinkedIn call.

```javascript
(function transformOneGroup() {
    var SOURCE = 'crunchbase';
    var IMPORT_RUN = 'fallback-sample-crunchbase-startups';

    var runId = SOURCE + '-manual-' + new GlideDateTime().getNumericValue();
    var outcome = new IngestionMapper().ingestStaging(runId, SOURCE, IMPORT_RUN,
        'fallback');
    var summary = outcome.summary;

    gs.info('run ' + runId + ' source ' + outcome.source_system
        + ' accepted ' + outcome.accepted + ' rejected ' + outcome.rejected);

    if (!summary) {
        gs.error('run ' + runId + ' produced no summary: the batch did not reach its'
            + ' run summary, so its counters are unreported');
        return;
    }
    gs.info('summary logged=' + summary.logged
        + ' source_system=' + summary.source_system
        + ' provenance=' + summary.provenance
        + ' processed=' + summary.processed
        + ' rejected=' + summary.rejected
        + ' skipped=' + summary.skipped
        + ' duplicates=' + summary.duplicates
        + ' unmatched=' + summary.unmatched
        + ' rule3_deviations=' + summary.rule3_deviations
        + ' events_dropped=' + summary.events_dropped);

    if (summary.logged !== true) {
        gs.error('run ' + runId + ' refused its run summary: provenance was not'
            + ' recognised, so nothing recorded the run');
    }
    if (summary.source_system !== SOURCE) {
        gs.error('run ' + runId + ' attributed itself to source '
            + summary.source_system + ' rather than ' + SOURCE);
    }
    if (summary.provenance !== 'fallback') {
        gs.error('run ' + runId + ' recorded provenance ' + summary.provenance
            + ' rather than fallback');
    }
    if (summary.events_dropped !== 0) {
        gs.error('run ' + runId + ' dropped ' + summary.events_dropped
            + ' log event(s): the buffer ceiling was reached and the evidence is'
            + ' incomplete');
    }
    if (summary.skipped !== 0) {
        gs.error('run ' + runId + ' skipped ' + summary.skipped
            + ' record(s): a write failed for a reason other than a cleaning rule');
    }
    if (summary.processed !== outcome.accepted) {
        gs.error('run ' + runId + ' counted ' + summary.processed
            + ' processed against ' + outcome.accepted + ' accepted');
    }
})();
```

**Every one of those six checks is a required assertion, not a convenience.** `ingest()` writes its run summary inside a `finally`, so a summary exists even when the batch failed partway — which means the presence of a summary proves nothing on its own and each flag has to be read.

| Flag | What a failure means |
| --- | --- |
| `summary` absent | The batch did not reach its `finally`. Treat the group as unsettled and read the system log. |
| `logged` not `true` | The provenance argument was not `live` or `fallback`, so the summary event was refused and **the run recorded no counters at all**. |
| `source_system` not the source you passed | The batch selected the wrong source's alias and translation tables. Every value in the group was mapped against the wrong vocabulary. |
| `provenance` not `fallback` | The run will be labelled `live validated` downstream on evidence that came from a CSV. |
| `events_dropped` not `0` | The event buffer's one-thousand-event ceiling was reached and log lines were discarded, so the per-record evidence is incomplete. |
| `skipped` not `0` | A write failed for a reason other than a cleaning rule. A cleaning-rule refusal counts as `rejected`, not `skipped`; `skipped` is always a defect. |
| `processed` not equal to `accepted` | The logger's counter and the batch's counter disagree, which means an entry settled without being counted. |

`ingestStaging()` selects rows on `source_system` and `import_state` `pending`, with `import_run` as an optional further filter — pass an empty string to take every pending row of that source system, or a specific token to transform one group's rows in isolation. It does **not** read a row that is `processed`, `rejected` or `error`, and it skips a `pending` row whose `import_run` carries **another run's `run:` lease**.

Because the query is bounded to `import_state` `pending`, **a row that has already settled is never re-read**. Re-running the transform therefore cannot duplicate entity records from staging, whichever route is used.

#### Returning an abandoned or rejected row to the queue

`pending` alone does not mean unclaimed. A flow **claims** each row it is about to read by writing the reserved lease value `run:` followed by that run's identifier into `import_run`, leaving `import_state` at `pending`, so a row is never read twice within a run and a run that dies hard leaves its rows visible rather than lost. The `import_state` choice list therefore carries exactly **four** members — `pending`, `processed`, `rejected` and `error` — and [`../data-model.md`](../data-model.md) lists all four and specifies the lease under [The `import_run` run lease](../data-model.md#the-import_run-run-lease). A **leased** `pending` row is one whose `import_run` begins `run:`; an **unleased** `pending` row carries its CSV batch token, which never contains a colon.

A row is returned to the queue by hand, never automatically, and only after its cause has been dealt with.

| Row state | When to return it | How |
| --- | --- | --- |
| `pending` carrying a `run:` lease whose run is no longer executing | The run was cancelled, timed out, or the transaction was killed. Confirm in the flow execution log that the run is not still going. | In the **Ingestion staging** list view, **clear `import_run`**, or set it back to that file's batch token — `fallback-sample-<source>-<type>` — so the row is queued and its provenance is still legible. `import_state` is already `pending` and must not be edited. Leaving the dead lease in place is what keeps the next run from taking the row. |
| `error` | Only after the underlying fault is fixed — the reason is in `error_message`. | Same edit. Clear `error_message` as well, so a second failure is distinguishable from the first. |
| `rejected` because the sequence was broken, and its `error_message` names an unresolvable parent | After the parent group has been transformed. | Same edit. |
| `rejected` by a cleaning rule on the row's own content | **Never.** These are the designed fixtures. Returning one to the queue makes it fail again identically and changes the expected `import_state` distribution. | — |

**Nothing returns a row to `pending` on its own.** A row that failed one run fails the next in the same way, so there is no automatic retry. Two consequences follow, and both are safe to rely on:

- A row left `pending` under a dead lease is a **diagnostic**, not a leak. Its `import_run` names the run that abandoned it, and no later run will take it until the lease is cleared.
- Returning a row to `pending` and transforming again **re-applies the whole entity write**. For a record type whose natural key the row carries in full, that write is an update of the record the first attempt created; where the row does not carry a usable key, it is a second insert. The per-type keys are in [What it writes](#what-it-writes).

### Restoring `source_mode` is readiness-determined, not a return to `live`

**Do not set `x_bst_startuptrk.ingestion.source_mode` to `live` as a matter of course after the load.** The property selects which branch each flow attempts, and setting it to `live` on an instance whose credential aliases hold no credential makes every subsequent scheduled execution attempt an outbound call that cannot succeed, fall back, and log an authentication failure on every run. The evidence trail then carries a failure per run that is a configuration error rather than a finding.

**There is one property, and both flows read it.** `x_bst_startuptrk.ingestion.source_mode` is a single scoped property; there is **no** per-flow source mode, and no flow input carries one. Setting it for the Crunchbase flow sets it for the LinkedIn flow in the same act, and the next execution of **both** takes the branch it names. Three consequences follow and each is a rule:

| # | Rule | Why |
| --- | --- | --- |
| 1 | **Live-first is a property of `live` mode, not of every run.** In `live` mode each flow attempts its outbound call first and falls back only on a failure; in `fallback` mode neither flow attempts a call at all. A statement that the live path is attempted first on every run holds only while the property reads `live`. | The `If` block around the fetch step tests `attempt_live`, which is `false` in `fallback` mode, so the call site is not reached. |
| 2 | **A procedure that changes the value temporarily captures the observed value first and restores that value** — never an unconditional `live`. Record the value you read before you change it, beside the value you restored. | The property is shared, so an unconditional restore imposes one flow's temporary need on the other flow's steady state. |
| 3 | **The end state is branch-determined**, by the table below, and it is the same value for both flows because there is only one property to set. | A per-flow end state is not expressible. Where the two flows would want different values, the more restrictive one governs: `fallback`. |

The required end state follows from [`01-connection-credential-aliases.md`](01-connection-credential-aliases.md), which records each alias on one of two **readiness paths** — **Path A** is the provisioned posture and **Path B** is the unprovisioned one. **That vocabulary is not the runbook's `Branch A` and `Branch B`, which name the two rollback branches and have nothing to do with credentials.**

| Alias readiness path recorded in guide 01 | Required `source_mode` | What the value follows from |
| --- | --- | --- |
| **Both** aliases on **Path A**, each with a passing connection test | `live` | The live path can succeed, and fallback remains available if a call fails |
| **Either** alias on **Path B**, or either connection test not passing | **`fallback`** | The live path cannot succeed. `fallback` is the sanctioned completion path, and it is what makes every result honestly labelled `fallback validated` |

**On the instance recorded for this delivery both aliases are on Path B**, so the value the property must read when this guide is signed off is **`fallback`**. That is not a temporary setting left behind by the load — it is the correct configured state, and both flow guides state the same rule.

Record the path and the resulting value here: Crunchbase alias path `______`, LinkedIn alias path `______`, `source_mode` set to `______`.

### Step 9 — recalculate the derived portfolio counts

After the load, **invoke `InvestorPortfolioService.recalculateAll()` from a background script**. Navigate to **System Definition > Scripts - Background**, set the scope selector on that page to **Boston Startup Tracker** so the script runs inside `x_bst_startuptrk`, and run:

```javascript
var portfolio = new InvestorPortfolioService();
gs.info('investors rewritten: ' + portfolio.recalculateAll());
```

The scope selector is not optional. Cross-scope write capability is false on every application table, so a script left in the Global scope cannot update an investor row, and `InvestorPortfolioService` — a scoped Script Include — cannot be instantiated from there at all.

`recalculateAll()` reads the graph in two passes — one over the funding rounds and one over the join table — then makes a single pass over the investors, **writing only those whose stored count differs from the derived count**, and returns the number of investors it wrote. Record that number in the [Build verification](#build-verification) table.

**On a load performed with business rules running, the expected return is `0`**: the two portfolio business rules will already have maintained every count as the funding rounds and join rows were inserted, so there is nothing left to correct. A non-zero return is meaningful — it says the stored counts had drifted, which means business rules were suppressed somewhere on the write path. Investigate before signing the guide off.

## The staging-to-entity transform

### What it writes

Exhaustively, `IngestionMapper` writes seven tables from the staged rows and no others.

**Every one of the six record types has a natural key**, and `IngestionMapper.upsert()` resolves it before it writes. Startup and Investor are matched by their own dedicated lookups; the other four are matched by `findExistingByKey(recordType, data)` against the `IDENTITY_KEYS` map.

| Record type | Entity table | Existing-record lookup, so a re-run updates rather than duplicates |
| --- | --- | --- |
| `startup` | `x_bst_startuptrk_startup` | `findExistingStartup(name, headquarters_location)`, case-insensitively — the same key as cleaning rule 2. Exactly one match updates it; no match inserts; **more than one match is an ambiguity failure** and nothing is written. |
| `investor` | `x_bst_startuptrk_investor` | `findExistingInvestor(name)` — **name only**, with no location component. Same three outcomes. |
| `funding_round` | `x_bst_startuptrk_fundinground` | `findExistingByKey`, trying `startup` + `round_date` + `round_type` first and `startup` + `round_date` second. |
| `founder` | `x_bst_startuptrk_founder` | `findExistingByKey` on `startup` + `name`. |
| `executive` | `x_bst_startuptrk_executive` | `findExistingByKey` on `startup` + `name`. |
| `job_posting` | `x_bst_startuptrk_jobposting` | `findExistingByKey`, trying `startup` + `url` first and `startup` + `title` + `posted_date` second. |
| participation | `x_bst_startuptrk_m2m_round_investor` | `IngestionMapper.linkParticipants()` reconciles the round's rows to the incoming set exactly — see [Participating investors become join rows](#participating-investors-become-join-rows). A unique composite index on `funding_round` + `investor` forbids a duplicate pair whatever the write path. |

`findExistingByKey` has three properties that decide what a re-transform does, and all three are load-bearing.

| # | Property |
| --- | --- |
| 1 | **The candidate keys are tried in the order listed**, and the **first key the incoming record carries in full** decides. A funding-round row carrying `round_type` is matched on the three-field key; the same row with `round_type` blank falls through to the two-field key. |
| 2 | **A key is skipped when the record does not carry every one of its fields.** A record carrying none of its type's keys in full reports no match and is **inserted** — which is the only path on which a re-transform can duplicate a row. A `job_posting` row with a blank `url` and a blank `posted_date` is the concrete case. |
| 3 | **More than one match is an ambiguity failure, not a pick.** `upsert()` returns not-ok with `the <type> natural key is ambiguous`, the row is stamped `error`, and **nothing is written**. Values are compared *after* reference resolution, so `startup` in a key holds a resolved record identifier rather than a name. |

So **two mechanisms protect this procedure from duplicating records, and they operate at different layers.** The `import_state` transition stops a settled row from being read again at all: `ingestStaging()` reads only `pending` rows, so re-running the transform is a no-op over rows that already settled. The natural keys stop a row that *is* read again from inserting a second record: a row deliberately returned to `pending` and transformed again **updates** the record its first attempt produced, provided it carries a usable key in full. The residual case is property 2 above — a row carrying no complete key inserts a second record — and the way to avoid it is to fix the blank key field rather than to delete the entity record.

`x_bst_startuptrk_newsarticle` is written by neither the import nor the transform.

### Participating investors become join rows

**The transform materialises `x_bst_startuptrk_m2m_round_investor` rows from `participating_investor_names`.** For each accepted `funding_round` row it reads the quoted JSON array, trims each member, drops an empty member, resolves each remaining member to exactly one Investor record, keeps a repeated member once, and **reconciles the join rows to that set** through `IngestionMapper.linkParticipants()` — inserting the links the row declares and removing any link the round carries that the row does not. `InvestorPortfolioService.linkInvestorToRound()` is the administrative one-off for linking a single investor to a single round by hand; it is not on the ingestion path and this procedure never calls it. A member that resolves to no investor, or to more than one, is logged as a warning and contributes no join row; the members that do resolve still become join rows, and the round is recorded as partial. **A row whose `participating_investor_names` is empty declares nothing and removes nothing**, so an empty value never strips a round's existing participants.

**`linkParticipants()` reconciles rather than appends.** It reads the round's existing join rows, then makes the stored set equal the incoming set:

| Incoming row | What happens to it |
| --- | --- |
| Named by the incoming set and already stored | Left untouched. Counted as `kept`. |
| Named by the incoming set and not stored | Inserted. Counted as `linked`. |
| Stored but **not** named by the incoming set | **Deleted** — but only when the incoming set is *complete*. Counted as `removed`. |

**Completeness is what licenses the delete**, and it is decided per round.

| Incoming `participating_investor_names` | `complete` | Effect |
| --- | --- | --- |
| The row supplies no value at all | The set is not supplied, and `linkParticipants()` returns immediately having written nothing. An absent value never clears a stored one. | No change |
| A value whose every member resolved to exactly one investor | `true` | **Exact-set reconciliation.** Obsolete rows are deleted and `reconciled` is reported `true`. |
| A value with at least one member that resolved to no investor, or to more than one | `false` | **Additive only.** The resolved members are still inserted, obsolete rows are **kept**, and a warning names how many links were kept against an incomplete set and how many names did not resolve. Deleting against an incomplete set would discard participation the source still asserts. |

A member that resolves to no investor, or to more than one, is logged as a warning and contributes no join row; the members that do resolve still become join rows.

**A failed insert or a failed delete fails the whole funding-round row.** `linkParticipants()` counts each one in `failed`, and `IngestionMapper` then stamps the staging row `import_state` **`error`**, counts it as rejected, and logs `<n> participant link(s) ... could not be reconciled`. The funding-round entity record itself remains written — it was inserted or updated before the links were reconciled — so the row's `error` state means *its participation is incomplete*, not that no record exists. That is deliberate: a round whose participants are half-written must not be reported `processed`. Return the row to the queue as [Returning an abandoned or rejected row to the queue](#returning-an-abandoned-or-rejected-row-to-the-queue) sets out once the cause is fixed; the re-transform matches the round on its natural key and reconciles the links again.

Three further rules govern the write, and all three matter:

- **`lead_investor` remains a distinct first-class reference** on `x_bst_startuptrk_fundinground`, resolved from `lead_investor_name` and set directly on the funding-round record. It is a single reference, not a join row. An investor that both led a round and participated in it appears in both places, which is correct.
- **The join table is authoritative for participation.** It is the only table the transform writes for it.
- **`x_bst_startuptrk_fundinground.participating_investors` is never written by any path.** It is a **calculated** read-only column derived from the join table on every read — `virtual` true, with a calculation that calls `InvestorPortfolioService.participantList()` — and the mapper's write allowlist excludes it, so an attempt to set it is dropped rather than applied.

Both references on the join table are mandatory and both cascade on delete, so deleting a funding round or an investor removes its join rows with it.

### Business rules must run during the load

**Every write on the entity path must run business rules.** Three business rules are active on the tables this procedure touches, and two of them maintain the derived `x_bst_startuptrk_investor.portfolio_count` through `InvestorPortfolioService`:

| Business rule | Table | When |
| --- | --- | --- |
| `Recalculate investor portfolio on funding round` | `x_bst_startuptrk_fundinground` | After insert, update and delete. On an update it recalculates **both** the previous and the new `lead_investor`, and handles a change to the round's `startup`. |
| `Recalculate investor portfolio on round investor link` | `x_bst_startuptrk_m2m_round_investor` | After insert, update and delete. It recalculates the linked investor's `portfolio_count` and nothing else: the join table is the only store of participation, and `participating_investors` is derived from it on read rather than written. |
| `Trim and validate startup` | `x_bst_startuptrk_startup` | Before insert and update. |

Leave **Run business rules** true on all six transform maps, and do not call `setWorkflow(false)` in any script you write to load or transform this data. Two writes inside `IngestionMapper` do suppress rules, and neither is yours to change: the staging-row claim, on a table that carries no business rule at all, and each participant join row, so a round linking twelve investors recalculates once rather than twelve times. That batch closes with **one** explicit convergence step over every investor added, removed or leading, and a batch that did not converge marks the round `partial` rather than `processed`. `portfolio_count` is therefore maintained on both paths; [step 9](#step-9--recalculate-the-derived-portfolio-counts) is the independent check that it was.

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

**Operational warning — two different state columns.** The import set row carries `sys_import_state` with values such as `Pending`, `Processed`, `Ignored` and `Error`; the application row carries `import_state` with the four values `pending`, `processed`, `rejected` and `error`. They belong to adjacent layers and mean different things. `sys_import_state` describes whether the **CSV row reached the staging table**; `import_state` describes whether the **staged row became an entity record**. An import set row reading `Processed` says nothing about whether cleaning rule 4 later rejected the staged row. Always name the layer when reporting a count.

### `import_state` after the transform

Once every file has been imported and transformed, the sixty-five rows reconcile to exactly this distribution across the four `import_state` members:

| `import_state` | Rows | What they are |
| --- | --- | --- |
| `processed` | **52** | An entity record was created or updated from the row. |
| `rejected` | **13** | The row was refused by a cleaning rule: **12** rows blanking a mandatory column for their record type, plus **1** row that repeats an earlier startup's `name` plus `headquarters_location` pair within the same batch. |
| `error` | **0** | A write failed for a reason other than a cleaning rule, or a funding round's participant links could not be reconciled. |
| `pending` | **0** | Nothing left untransformed. **A `pending` row after the transform is a claim that was never settled**: read its `import_run`, and if it carries a `run:` lease the run that held it was abandoned — see [Returning an abandoned or rejected row to the queue](#returning-an-abandoned-or-rejected-row-to-the-queue). |

A different distribution means a file was edited, a field map is mismapped, or the load order was not followed. Investigate before signing off. The per-file defect inventory that produces these numbers is in [`../../sample-data/README.md`](../../sample-data/README.md).

### How `error_message` is populated

`error_message` is empty on every shipped row and is written by the transform, never by the import. It carries a **controlled outcome code and an opaque row reference, and nothing else**:

```text
code=<outcome code> ref=<opaque reference>
```

`IngestionMapper.clean()` returns the code for a refusal, `IngestionMapper.writeStagingState()` writes it with the matching `import_state` on the same staging row, and `_stateMessage()` composes the text. **No upstream response text, exception message, stack frame, field value, personal name or email address ever reaches this column** — every one of those belongs to the run's own log line, which is where the detail is. The two columns are always consistent: a row reading `rejected` or `error` always carries a code, and a row reading `processed` carries `code=processed`.

The reference is `staging:<sys_id>` for every row this procedure loads, because each row has a staging record to name. A live-sourced record with no staging row is referenced by its ordinal within the run instead. Both forms are stripped to `[0-9A-Za-z_.-]` and truncated to 64 characters, so the reference cannot carry content of its own.

**Query on the code, never on prose.** `error_messageCONTAINS code=missing_mandatory` selects the rule 4 rejections; a query written against a sentence will match nothing. The closed vocabulary is fifteen codes wide — `accepted`, `processed`, `rejected`, `duplicate_in_batch`, `missing_mandatory`, `mandatory_value_refused`, `value_over_length`, `record_type_unsupported`, `payload_unmappable`, `cleaning_refused`, `parent_unresolved`, `relationship_incomplete`, `write_failed`, `unexpected_failure` and `run_abandoned` — and a code outside it is recorded as `unexpected_failure` rather than passed through. `IngestionMapper` writes the first fourteen; `run_abandoned` is written only by a flow's terminal-state sweep, and never by this procedure's own background-script transform.

The codes a row can carry here, and what to do about each:

| `import_state` | `error_message` code | Expected here | Action |
| --- | --- | --- | --- |
| `rejected` | `code=missing_mandatory` | **Yes — 12 rows.** The cleaning-rule-4 fixtures. | None. This is the designed outcome. **Which** columns were blank is in the run's log line for the same reference, not in this column. |
| `rejected` | `code=duplicate_in_batch` | **Yes — 1 row.** The cleaning-rule-2 fixture. | None. This is the designed outcome. |
| `rejected` | `code=parent_unresolved` | **Only on a row that also blanks a mandatory column**, and then the row records the blocking refusal instead. | On any other row it means the [dependency-group sequence](#step-7--run-the-dependency-group-sequence) was broken, or the parent group was not transformed first. Transform the parent group, then return the row to the queue as [Returning an abandoned or rejected row to the queue](#returning-an-abandoned-or-rejected-row-to-the-queue) sets out. The log line says whether no startup carried the name or the name was ambiguous. |
| `rejected` | `code=mandatory_value_refused` or `code=value_over_length` | No | A mandatory column held a value cleaning refused, or a value exceeded its column. Read the run's log line for the field, correct the CSV only if the value is genuinely wrong, and re-load. |
| `rejected` | `code=record_type_unsupported` or `code=payload_unmappable` | No | The row's `record_type` is not one the source supplies, or the row carries nothing mappable. A field map or the `source_system` column is wrong. |
| `error` | `code=write_failed` | **No — the expected count is 0.** | A genuine defect. Read the log line for the run identifier and the same `ref=` token. |
| `error` | `code=relationship_incomplete` | **No — the expected count is 0.** | A lead or participating investor did not resolve, or a join-row insert, delete or the convergence step failed. The funding-round record itself **is** written; its participation is incomplete, and the batch counts the round as `partial`. Fix the cause, then return the row to the queue — the re-transform matches the round on its natural key and reconciles the links again. |
| `error` | `code=unexpected_failure` | **No — the expected count is 0.** | An exception the per-record boundary caught. The batch continued; the detail is in the log line. |
| `error` | `code=run_abandoned` | **No — impossible here.** Only a scheduled flow's sweep writes it. | A flow claimed the row and ended before settling it. Return it to the queue as [Returning an abandoned or rejected row to the queue](#returning-an-abandoned-or-rejected-row-to-the-queue) sets out, after confirming from `import_run` and the flow execution log that the run is no longer executing. |

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
| Join rows for an investor no longer named by its round's `participating_investor_names` | **None**, on a load whose every participant name resolved. `linkParticipants()` deletes an obsolete row when the incoming set is complete. |
| A round whose `lead_investor` also appears among its join rows | Permitted and present. It is not a duplicate. |
| `x_bst_startuptrk_fundinground.participating_investors` | Renders the investors of the rounds that have join rows, derived on read by the column's own calculation — nothing writes it, and the transform does not. |

An empty join table with ten funding rounds present means `participating_investor_names` was left unmapped, was re-delimited in transit — a JSON array rewritten as a comma-separated list resolves to no investor at all — or the investors file was transformed after the funding-rounds file rather than before it.

The parser side of that seam is covered by two assertions in [`05-atf-test-suites.md`](05-atf-test-suites.md): the suite-10 Crunchbase batch seeds a participant list in this file's carrier naming an investor whose own name contains a comma, and [The participant carrier assertion](05-atf-test-suites.md#the-participant-carrier-assertion) exercises all three accepted carriers plus the single-name reading directly. A build that reintroduces comma splitting fails both.

**4. The derived portfolio counts.** After [step 9](#step-9--recalculate-the-derived-portfolio-counts), `x_bst_startuptrk_investor.portfolio_count` is non-zero on **6** of the 7 investors. Exactly one investor is referenced by no funding round, as lead or as participant, and its count is correctly **0**. `recalculateAll()` returns **0** investors rewritten on a load whose business rules ran.

**5. Provenance.** Every staged row reads `run_provenance` `fallback`, and no row reads `live`. A flow run over this dataset writes that flow's entry into `x_bst_startuptrk.ingestion.last_run_provenance`, which serialises one entry per source joined by `;` in the form `<source>=<provenance>|<state>|<stamp>|<run>` — so `crunchbase=fallback|succeeded|<stamp>|<run>` or the same keyed under `linkedin`; the entry is written by `IngestionLogger.markRunComplete()` through `AppProperties.completeRun()`, **not** by the run summary — and mirrors the same values into a run summary carrying the processed, rejected and skipped counts. Any result derived from this dataset must be labelled **`fallback validated`** and never `live validated`; the labelling convention is applied by [`05-atf-test-suites.md`](05-atf-test-suites.md) and the evidence is collected by [`../validation-checklist.md`](../validation-checklist.md).

### Clearing the loaded rows — a step of this procedure, not an automatic sweep

**The sixty-five rows persist until an administrator deletes them.** The application ships **one** scheduled job — the rate-limit counter prune — and it does not touch this table. There is no automatic minimisation of `raw_payload` or of the person columns, and no automatic deletion of a settled row: the Agent Action Plan's artifact inventory is closed at eight Script Includes, eleven properties and one scheduled job, so no retention service, no retention property and no second job is delivered.

The consequences for this procedure are the ones to plan around.

| # | Consequence |
| --- | --- |
| 1 | **A settled row stays readable.** A row that reached `processed`, `rejected` or `error` keeps its `raw_payload` and its `name`, `title`, `bio`, `linkedin_url` and `contact_email` values until it is deleted. The table's administrator-only access controls and its `ws_access` false posture are what bound who can read them. |
| 2 | **Clean-up is a deliberate administrative act.** To clear the dataset, filter the **Ingestion staging** list on the `import_run` values of the [Verification after the load](#verification-after-the-load) table and delete the rows. Deleting a settled staging row removes no entity record: the entity records are separate rows and are unaffected. |
| 3 | **Re-import before repeating a flow test on a cleared table.** The CSVs in `../../sample-data/` are the reproducible source and are never modified by the platform; the table is a working copy. Re-running steps 1 through 6 restores all sixty-five rows in their `pending` state. |
| 4 | **Live data reaches this table with the same posture.** A live ingestion run stages upstream payloads into the same columns, so an operator who does not want live payloads retained must delete the settled rows as part of operating the flow. This is recorded as a delivered limitation in [`../gaps-and-flags.md`](../gaps-and-flags.md), not as a defect of this procedure. |

The table's access posture, column by column, is in [`../data-model.md`](../data-model.md).

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

These six are not rationale. They describe failures that are easy to cause and hard to see, and three of them are completely silent.

### A change to one leg of the three-way contract breaks the fallback path silently

The Data Import Wizard maps columns **by header name**. Rename, re-case or misspell a column in any one of the three legs — the CSV header row, the staging dictionary element, or the field map in this guide — and that column is simply left unmapped. **The load reports success, the row count is correct, and no error is raised**; the target field is empty on every row, and the ingestion flows find nothing usable in it. Whenever any one leg changes, re-verify all three, name for name, before loading anything. Read the header row of the file, read `sys_dictionary` for `x_bst_startuptrk_ingest_staging`, and read the Field Maps related list on the transform map, and confirm the three lists agree.

### Business rules disabled during the load leaves `portfolio_count` silently wrong

`x_bst_startuptrk_investor.portfolio_count` is a stored integer maintained by two business rules, and nothing recomputes it on read. A write that bypasses business rules — **Run business rules** cleared on a transform map, or `setWorkflow(false)` in a script — leaves the stored count stale for every investor touched by that write. **There is no error, no warning and no log record.** Leave **Run business rules** true on all six maps, never suppress rules on this path, and always run [step 9](#step-9--recalculate-the-derived-portfolio-counts) afterwards: its return value is the only signal that the counts drifted.

### `active` is a string column, and a blank must survive the load

On `x_bst_startuptrk_ingest_staging`, `active` is a **`string` of length 10** carrying the text `true` or `false`, **not** a True/False column, and it declares **no dictionary default**. A blank `active` therefore survives the import and is rejected by cleaning rule 4, instead of being silently defaulted to `true` on the way in. Two consequences: do not change the column's type or add a default to it, and do not configure the field map to substitute a value for a blank. `x_bst_startuptrk_startup.active` keeps its own dictionary default of `true`, which applies only to a Startup inserted without the field set.

### Do not open the CSVs in a spreadsheet application

Attach the files exactly as they are. A spreadsheet round trip commonly rewrites LF line endings to CRLF, adds a byte-order mark, re-quotes fields the dialect leaves unquoted, **unquotes or strips the designed leading and trailing spaces the rule 1 fixtures depend on** — all fourteen of which ship quoted for exactly this reason, reformats an ISO date into a locale format, and renders a large plain currency figure in scientific notation. Each of those either breaks a fixture or breaks a coercion, and several of them do so without any visible sign in the loaded rows.

### A staged value can become a spreadsheet formula when the table is exported

**This is an export-path risk, not an import-path one, and the two are easy to conflate.** The warning above is about a spreadsheet **corrupting the fixtures on the way in**. This one is about a staged value **executing in a spreadsheet on the way out**.

`x_bst_startuptrk_ingest_staging` is the one table in the application that holds unvalidated third-party text: `raw_payload` verbatim, and `name`, `title`, `bio`, `linkedin_url`, `contact_email` and `description` as the upstream supplied them. Every mainstream spreadsheet application treats a cell whose first character is `=`, `+`, `-`, `@`, a tab or a carriage return as a **formula** rather than as text. So an administrator who inspects a live-staged row by exporting the list to CSV or Excel — the ordinary way anyone reads sixty-five rows — can execute a payload the upstream source chose, in their own session, with their own privileges. Nothing about the ingestion is involved: the value never needs to be ingested, only staged and exported.

**The six delivered CSVs are clear, and this was checked rather than assumed.** All 65 data rows across all six files were parsed and every field examined: **zero** values begin with `=`, `+`, `-`, `@`, a tab or a carriage return. The fixtures cannot trigger this. The risk arrives with **live** data, or with a row an operator types by hand.

**The control is a platform property, and it is outside this application's scope.**

| | |
| --- | --- |
| Property | `glide.export.escape_formulas` |
| Required value | `true` |
| What it does | Prefixes an exported value whose first character is one of the six with a single quote, so the spreadsheet reads it as text. It applies to **every** export on the instance, which is why it is a platform setting rather than an application one. |
| Whose it is | The **platform owner's**. It lives in the Global scope, and prompt section 6.0 forbids this application from creating, modifying or shipping any record outside `x_bst_startuptrk` — so it is **not** in the Update Set and must not be added to it. |
| How to confirm | Read it in **System Properties** by name, or filter `sys_properties` on that name. Recent releases ship it `true`; an instance upgraded from an older release, or one where it was cleared, will not. **Confirm the value; do not assume the default.** |

**Two further mitigations belong to whoever reads the table, and neither replaces the property.**

- **Read the table in the list view rather than by exporting it.** The list view renders a leading `=` as text. [Verify in the list view, not over the Table API](#verify-in-the-list-view-not-over-the-table-api) already directs this for a different reason — `ws_access` is `false` — and it happens to be the safe habit here too.
- **Clear settled rows promptly.** A row that has been consumed and deleted cannot be exported at all. That is the same clear-down [Clearing the loaded rows — a step of this procedure, not an automatic sweep](#clearing-the-loaded-rows--a-step-of-this-procedure-not-an-automatic-sweep) already asks for, and it is why `LA1` and `LA2` of the live-activation register gate the live path.

**What this application does instead of the property it may not ship.** It never writes an upstream value into a log line, a flow output, a REST response or an error message without passing it through `AppProperties.safeText()`, which turns a double quote into a single quote, strips control characters and redacts credential-shaped, address-shaped and locator-shaped runs. That protects every surface the application owns. It does **not** protect an export of the staging table, because the staging table holds the value verbatim on purpose — that is what makes a fallback dataset a faithful stand-in for an API response.

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

**None of those literals matches the binding choice lists.** Nothing is carried forward: every value in the six CSVs is authored against the choice values the Update Set declares. The script also writes columns that exist on no target table, and it seeds NewsArticle records at `:L87-L100`, an entity this dataset excludes. The enumeration-replacement rule is recorded at `D-022` and the six-file, no-NewsArticle dataset at `D-054` in [`../../../docs/decisions/DECISION_LOG.md`](../../../docs/decisions/DECISION_LOG.md).

### The legacy cleaner's transformations are not applied

[`../../../src/data_collection/data_cleaning/startup_cleaner.py`](../../../src/data_collection/data_cleaning/startup_cleaner.py) is the pandas cleaning pipeline. **The staged data is not cleaned by any of it**, and the four cleaning rules are applied downstream by `IngestionMapper`, not by the import transform.

| Citation | What is there | What the binding rule requires instead |
| --- | --- | --- |
| `:L57` and `:L60` | Deduplication on **name + website** — `duplicated(subset=['company_name', 'website'])` and the matching `drop_duplicates`. | Cleaning rule 2 deduplicates on `name` + **`headquarters_location`**, case-insensitively. The two keys select different rows: the designed duplicate pair in `crunchbase_startups_sample.csv` differs on `website`, so a name-plus-website key does not catch it. |
| `:L90` | **Median imputation** of missing numeric values — `fillna(df[column].median())`. | Cleaning rule 4 **rejects** a record missing a mandatory field, and writes no value in its place. |

Neither transformation is reproduced, in the import or anywhere else. The same module fills missing values with the string `'Unknown'` at `:L86`, which the dataset's no-sentinel-values rule forbids. The rule that the four cleaning rules come from the requirements alone, with nothing ported from this module, is recorded at `D-051` in [`../../../docs/decisions/DECISION_LOG.md`](../../../docs/decisions/DECISION_LOG.md).

## Build verification

Do not sign this guide off until every line below is true.

| # | Check | Record |
| --- | --- | --- |
| 1 | Exactly **six** data sources exist, one per CSV file, each of type **File**, format **CSV**, retrieval method **Attachment**, delimiter `,`, header row `1`, with the correct file attached unmodified. | |
| 2 | Exactly **six** import set tables exist, one per record type, each carrying one column per that file's CSV header: 19, 12, 16, 14, 14 and 17. Derived names recorded here: `______` | |
| 3 | Exactly **six** transform maps exist, and **all six carry target table `x_bst_startuptrk_ingest_staging`**. No map targets any other table. | |
| 4 | Every map carries **Active** true, **Run business rules** true, **Enforce mandatory fields** No, **Copy empty fields** true, and **Run script** false. | |
| 5 | **92** field maps exist in total — 19, 12, 16, 14, 14 and 17 — every one a one-to-one mapping by header name, with no unmapped source column, no target column mapped twice, and no source script anywhere. | |
| 6 | The coalesce columns match [The coalesce key per record type](#the-coalesce-key-per-record-type) exactly, `import_run` is a coalesce column on all six maps, and the `startup` map includes `website` in its key. | |
| 7 | **Choice action** is `reject` on the four control-column field maps of every map, and `create` is used nowhere. | |
| 8 | **Date format** `yyyy-MM-dd` is set on `round_date` in the `funding_round` map and on `posted_date` in the `job_posting` map. | |
| 9 | `portfolio_count` appears in **no** field map, and no map targets a read-only or derived column. | |
| 10 | The twelve actions of [step 7](#step-7--run-the-dependency-group-sequence) were performed **in that order**, and no child group was transformed before the group it depends on. | |
| 10a | Each of the three Crunchbase transform calls was scoped to **one** `import_run`, and the LinkedIn call was made with an **empty** `import_run`. Four calls in total. | |
| 10b | Every transform call used a run identifier of the form `<source>-manual-<numeric timestamp>`, so its leading token is `crunchbase` or `linkedin`. No call used `gs.generateGUID()` as the leading token and none used a fixed `manual-load` prefix. | |
| 10c | For every one of the four calls, all six summary assertions of [step 8](#the-script) passed: a summary was returned, `logged` was `true`, `source_system` equalled the source passed, `provenance` was `fallback`, `events_dropped` was `0`, `skipped` was `0`, and `processed` equalled `accepted`. Recorded per call: `______` | |
| 11 | `x_bst_startuptrk_ingest_staging` holds **65** rows across the six `import_run` values, in the per-file counts of the [verification table](#verification-after-the-load). | |
| 12 | Before the transform, every staged row read `import_state` `pending`, `run_provenance` `fallback` and an empty `error_message`. | |
| 13 | After the transform, `import_state` reconciles to **52 `processed`, 13 `rejected`, 0 `error`, 0 `pending`**, and every rejected row names its reason in `error_message`. | |
| 14 | The entity record counts are **9, 7, 10, 8, 8, 10** and `x_bst_startuptrk_newsarticle` holds **0**. | |
| 15 | `x_bst_startuptrk_m2m_round_investor` holds **26** rows, the largest round links **5** investors, no `funding_round` + `investor` pair is duplicated, and no round holds a join row for an investor its `participating_investor_names` does not name. | |
| 16 | `InvestorPortfolioService.recalculateAll()` was run from a background script with the scope selector set to **Boston Startup Tracker**, and returned: `______` — expected `0`. | |
| 17 | `portfolio_count` is non-zero on **6** of the 7 investors, and the one investor no round references reads `0`. | |
| 18 | No transform map and no script **this procedure runs** cleared **Run business rules** or called `setWorkflow(false)` on an entity table. The two suppressions inside `IngestionMapper` are expected and are not defects: the staging-row claim of [Returning an abandoned or rejected row to the queue](#returning-an-abandoned-or-rejected-row-to-the-queue), on a table that carries no business rule, and each participant join row, which the batch closes with one explicit convergence step — confirm instead that check 16 returned `0`, which is what proves the convergence left nothing stale. | |
| 19 | No CSV file was edited, re-saved, trimmed or otherwise repaired, and no designed defect was corrected. | |
| 20 | No staging row was returned to `pending` except under [Returning an abandoned or rejected row to the queue](#returning-an-abandoned-or-rejected-row-to-the-queue), and no row rejected by a cleaning rule on its own content was returned at all. | |
| 21 | No retention or minimisation job was expected to clear these rows. The application ships **one** scheduled job and it does not touch this table; clearing the dataset is the administrative delete of [Clearing the loaded rows](#clearing-the-loaded-rows--a-step-of-this-procedure-not-an-automatic-sweep). | |
| 22 | **The clear-down was performed, and the count that proves it was recorded.** After the delete of [Clearing the loaded rows](#clearing-the-loaded-rows--a-step-of-this-procedure-not-an-automatic-sweep), a list-view count of `x_bst_startuptrk_ingest_staging` filtered on the six `import_run` values returns **0**. Count recorded: `______`. Leaving the rows in place is a permitted choice on a development instance holding only this synthetic dataset — record `retained by choice` and the reason — but it is **not** permitted once live data has reached the table, which is why `LA1` and `LA2` of [the live-activation register](../gaps-and-flags.md#the-live-activation-register) gate `source_mode` `live` on it. | |
| 23 | **`glide.export.escape_formulas` was read on this instance and its value recorded.** Required value `true`, per [A staged value can become a spreadsheet formula when the table is exported](#a-staged-value-can-become-a-spreadsheet-formula-when-the-table-is-exported). It is a Global-scope platform property, so it is **not** in the Update Set and is not this application's to set — confirm it, do not assume the release default. Value recorded: `______`. A value other than `true` is an instance finding to raise with the platform owner, and it blocks `source_mode` `live` as register row `LA9`. | |
| 24 | `x_bst_startuptrk.ingestion.source_mode` reads the value **the aliases' branch requires**, per [Restoring `source_mode`](#restoring-source_mode-is-readiness-determined-not-a-return-to-live) — `live` only when **both** aliases are in Branch B with a passing connection test **and** every row of [the live-activation register](../gaps-and-flags.md#the-live-activation-register) carries an owner, a date and an evidence reference; **`fallback`** otherwise. On the instance recorded for this delivery both aliases are in Branch A and the register is empty, so the required end state is **`fallback`**. Value recorded: `______` | |
| 25 | Any result derived from this dataset is labelled **`fallback validated`**, never `live validated`. | |

Guide 05 may begin once every line above is true. **Its precondition is the settled instance state this guide produces, not access to these rows** — guide 05's ingestion tests seed their own, per [Position in the build order](#position-in-the-build-order).

Success criterion 4 in [`../validation-checklist.md`](../validation-checklist.md) is satisfied separately, by three consecutive guard-passing flow runs with zero unhandled errors and the provenance of each one recorded. **Those runs do read this dataset**, so each counted run needs pending rows: reload the six files and confirm the pending count before each one, because step 8 advances every row to `processed` and a second run over a settled table ingests nothing.

## Related documents

| Document | Relationship |
| --- | --- |
| [`../../sample-data/README.md`](../../sample-data/README.md) | **Leg (a)** of the three-way contract and **authoritative for the CSV header rows and their order**, the per-file `import_run` values, the value conventions, the row counts and the per-file designed-defect inventory. |
| [`../../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml`](../../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml) | **Leg (b)**, and **authoritative for the staging column names**, types and lengths, and for every other identifier cited here. |
| [`../../sample-data/crunchbase_startups_sample.csv`](../../sample-data/crunchbase_startups_sample.csv) | Load position 1. Record type `startup`, 19 columns, 13 rows. |
| [`../../sample-data/crunchbase_investors_sample.csv`](../../sample-data/crunchbase_investors_sample.csv) | Load position 2. Record type `investor`, 12 columns, 8 rows. |
| [`../../sample-data/crunchbase_funding_rounds_sample.csv`](../../sample-data/crunchbase_funding_rounds_sample.csv) | Load position 3. Record type `funding_round`, 16 columns, 12 rows. |
| [`../../sample-data/linkedin_founders_sample.csv`](../../sample-data/linkedin_founders_sample.csv) | Load position 4. Record type `founder`, 14 columns, 10 rows. |
| [`../../sample-data/linkedin_executives_sample.csv`](../../sample-data/linkedin_executives_sample.csv) | Load position 5. Record type `executive`, 14 columns, 10 rows. |
| [`../../sample-data/linkedin_job_postings_sample.csv`](../../sample-data/linkedin_job_postings_sample.csv) | Load position 6. Record type `job_posting`, 17 columns, 12 rows. |
| [`02-flow-crunchbase-ingestion.md`](02-flow-crunchbase-ingestion.md) | A **fallback reader** of this table. Its step 4 queries the `crunchbase` rows this guide loads, and its step 6 writes the four Crunchbase tables. |
| [`03-flow-linkedin-ingestion.md`](03-flow-linkedin-ingestion.md) | A **fallback reader** of this table. Its step 4 queries the `linkedin` rows this guide loads, and its step 6 writes the three LinkedIn tables. |
| [`05-atf-test-suites.md`](05-atf-test-suites.md) | Runs after this guide. Its two ingestion-flow tests seed **their own** staging rows under a per-execution token and read **none** of this dataset; they share only the `fallback validated` result label. The dependency that fixes the order is the flows' pass 2 and criterion 4, not the ATF fixtures. |
| [`01-connection-credential-aliases.md`](01-connection-credential-aliases.md) | The two credential aliases the live path uses. Not required by this guide; the fallback path needs no credential. |
| [`04-service-portal-pages-and-widgets.md`](04-service-portal-pages-and-widgets.md) | The portal whose walkthrough reads the entity records this load produces. |
| [`../manual-build-instructions.md`](../manual-build-instructions.md) | The build order for the package and the split rule between Update Set XML and manual build. |
| [`../data-model.md`](../data-model.md) | The staging table's full column list, the entity choice values, the cascade rules and the `portfolio_count` derivation. |
| [`../validation-checklist.md`](../validation-checklist.md) | Success criterion 4 and its provenance evidence, which the loaded rows supply. |
| [`../validation-gates.md`](../validation-gates.md) | The eleven post-commit gates of precondition 4. |
| [`../access-control.md`](../access-control.md) | The staging table's administrator-only posture on all four operations. |
| [`../api-reference.md`](../api-reference.md) | The Script Include call graph and the eleven-property inventory, including `ingestion.source_mode` and `ingestion.last_run_provenance`. |
| [`../deployment-runbook.md`](../deployment-runbook.md) | The import sequence that commits the Update Set, and [what counts as a scheduled run](../deployment-runbook.md#what-counts-as-a-scheduled-run). |
| [`../gaps-and-flags.md`](../gaps-and-flags.md) | The NewsArticle ingestion exclusion, under which the dataset carries six CSVs and not seven. |
| [`../../../docs/decisions/DECISION_LOG.md`](../../../docs/decisions/DECISION_LOG.md) | **Every "why"**, including the single staging table, the flattened-columns-plus-`raw_payload` shape and the natural-key references. |
