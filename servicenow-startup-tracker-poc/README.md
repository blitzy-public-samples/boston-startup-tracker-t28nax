# Boston Startup Tracker — ServiceNow deliverable package

The Boston Startup Tracker — a platform that aggregates and presents data on venture-backed companies headquartered in the Boston area — replatformed onto the ServiceNow Now Platform as a single scoped application: **`x_bst_startuptrk`**, vendor prefix **`x_bst`**, version **`1.0.0`**.

This file is the package index. It states what the package contains, what the application declares, what the target instance must supply, the order in which the package is deployed, and where every other document lives. It is the entry point for an operator working from the repository root.

## What This Package Contains

Twenty-four files.

```text
servicenow-startup-tracker-poc/
├── README.md            this index
├── update-set/          1 file   the single importable Update Set
├── scripts/             1 file   the two-level XML validator
├── docs/                14 files 8 reference documents + 6 manual-build guides
│   └── manual-build/    6 files  the artifacts built through the platform interface
└── sample-data/         7 files  the column contract + 6 fallback CSV files
```

| # | Path | What it is |
| --- | --- | --- |
| 1 | [`README.md`](./README.md) | This index — the package contents, the deploy order and the documentation map. |
| 2 | [`update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml`](./update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml) | The single importable Update Set required by prompt section 11.0 — every artifact expressible as declarative metadata, in one XML document. |
| 3 | [`scripts/validate_update_set_xml.py`](./scripts/validate_update_set_xml.py) | The two-level XML well-formedness validator required by prompt section 11.0 — gate G-1 on the outer update-set document, gate G-2 on every nested per-record payload. Python standard library only. |
| 4 | [`docs/data-model.md`](./docs/data-model.md) | The ten tables, field by field, with types, lengths, mandatory flags, choice lists, cascade rules and derivations. |
| 5 | [`docs/access-control.md`](./docs/access-control.md) | The three roles, the five access-control layers and the role-by-field matrix over the seven premium-gated fields. |
| 6 | [`docs/api-reference.md`](./docs/api-reference.md) | The REST contract — one definition, 31 operations, the pagination envelope, and every status code and error body. |
| 7 | [`docs/deployment-runbook.md`](./docs/deployment-runbook.md) | The instance prerequisites, the pre-flight checks, the six-step import sequence, the rollback and the failure-handling matrix. |
| 8 | [`docs/validation-gates.md`](./docs/validation-gates.md) | The sixteen post-commit gates, each with its target, query, expected result and pass condition. |
| 9 | [`docs/validation-checklist.md`](./docs/validation-checklist.md) | The acceptance record, mapped one to one onto the five success criteria of prompt section 10.0. |
| 10 | [`docs/gaps-and-flags.md`](./docs/gaps-and-flags.md) | The single collection point for prompt section 11.0's flag obligation — every requirement with no clean platform equivalent. |
| 11 | [`docs/manual-build-instructions.md`](./docs/manual-build-instructions.md) | The index for the six manual-build guides, authoritative for their execution order and for the Update-Set-versus-manual split rule. |
| 12 | [`docs/manual-build/01-connection-credential-aliases.md`](./docs/manual-build/01-connection-credential-aliases.md) | Guide 01 — the two Connection & Credential Aliases the ingestion flows authenticate through. |
| 13 | [`docs/manual-build/02-flow-crunchbase-ingestion.md`](./docs/manual-build/02-flow-crunchbase-ingestion.md) | Guide 02 — the Crunchbase ingestion flow, targeting Startup, Investor, Funding round and the join rows. |
| 14 | [`docs/manual-build/03-flow-linkedin-ingestion.md`](./docs/manual-build/03-flow-linkedin-ingestion.md) | Guide 03 — the LinkedIn ingestion flow, targeting Founder, Executive and Job posting. |
| 15 | [`docs/manual-build/04-service-portal-pages-and-widgets.md`](./docs/manual-build/04-service-portal-pages-and-widgets.md) | Guide 04 — the portal, the theme, the five pages and the eight widgets. |
| 16 | [`docs/manual-build/05-atf-test-suites.md`](./docs/manual-build/05-atf-test-suites.md) | Guide 05 — the ten Automated Test Framework suites and their thirty-six tests. |
| 17 | [`docs/manual-build/06-staging-table-csv-import.md`](./docs/manual-build/06-staging-table-csv-import.md) | Guide 06 — the Data Import Wizard load of the six CSV files into the one staging table. |
| 18 | [`sample-data/README.md`](./sample-data/README.md) | The staging-table column contract, the header rows of all six files and the fallback-only posture of the dataset. |
| 19 | [`sample-data/crunchbase_startups_sample.csv`](./sample-data/crunchbase_startups_sample.csv) | Fallback Startup rows, shaped to mimic the expected Crunchbase response. |
| 20 | [`sample-data/crunchbase_investors_sample.csv`](./sample-data/crunchbase_investors_sample.csv) | Fallback Investor rows. |
| 21 | [`sample-data/crunchbase_funding_rounds_sample.csv`](./sample-data/crunchbase_funding_rounds_sample.csv) | Fallback Funding round rows, including participating-investor references. |
| 22 | [`sample-data/linkedin_founders_sample.csv`](./sample-data/linkedin_founders_sample.csv) | Fallback Founder rows, shaped to mimic the expected LinkedIn response. |
| 23 | [`sample-data/linkedin_executives_sample.csv`](./sample-data/linkedin_executives_sample.csv) | Fallback Executive rows. |
| 24 | [`sample-data/linkedin_job_postings_sample.csv`](./sample-data/linkedin_job_postings_sample.csv) | Fallback Job posting rows. |

**There is no NewsArticle CSV.** Prompt section 1.7 and section 4.0 exclude NewsArticle from automated ingestion entirely: News article records are created by manual entry or by CSV import, and neither ingestion flow targets them.

## What Was Built

Every figure below is the count carried by the delivered Update Set at [`update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml`](./update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml) or by the guide that owns the artifact.

| Area | Inventory |
| --- | --- |
| Scoped application | 1 — `x_bst_startuptrk`, vendor prefix `x_bst`, version `1.0.0` |
| Update Set records | **309** `sys_update_xml` records in one XML document |
| Tables | **10** physical — **7 entity** tables carrying **53 columns**, plus 3 supporting tables |
| Entity tables | `x_bst_startuptrk_startup` (12), `_founder` (6), `_executive` (6), `_investor` (6), `_fundinground` (8), `_jobposting` (9), `_newsarticle` (6) |
| Supporting tables | `x_bst_startuptrk_m2m_round_investor` (2), `_ingest_staging` (40), `_rate_limit_counter` (5) |
| Dictionary and labels | 110 `sys_dictionary` records, 110 `sys_documentation` labels, 77 `sys_choice` values, 5 declared indexes |
| Roles | **3** — `x_bst_startuptrk.admin`, `x_bst_startuptrk.user`, `x_bst_startuptrk.premium_user` |
| Access control | **49** `sys_security_acl` records across **5 layers**, with **74** `sys_security_acl_role` joins, including **7 field-level read ACLs** |
| Script Includes | **9** — `StartupSearchService`, `InvestorPortfolioService`, `IngestionMapper`, `IngestionLogger`, `RateLimitService`, `RestResponseBuilder`, `RestQueryHelper`, `AppProperties`, `PrivacyRetentionService` |
| REST surface | 1 Scripted REST API definition, **31 operations** across **6 logical resources** — `/startups`, `/founders`, `/investors`, `/funding-rounds`, `/jobs`, `/news` — plus the nested `GET /founders/{startup_id}/executives` |
| REST base path | `/api/x_bst_startuptrk/v1/` — pagination through `sysparm_limit` and `sysparm_offset`, with `total_count` in every list envelope |
| Configuration and logic | 13 scoped system properties, 3 business rules, 2 scheduled jobs, 9 application menu modules, 10 form sections, 10 list views, 1 related list |
| Ingestion | **2** Flow Designer scheduled flows, authenticating through **2** Connection & Credential Aliases referenced by name |
| Fallback dataset | 6 CSV files loading into 1 staging table |
| User interface | 1 Service Portal, 1 theme, **5 pages**, **8 widgets** |
| Tests | **10** Automated Test Framework suites containing **36 tests** — 7 table-CRUD suites, 21 field-ACL tests, 6 REST tests, 2 ingestion-flow tests |

### The seven premium-gated fields

A caller holding only `x_bst_startuptrk.user` is denied each of these at field level, and the key is omitted from the API response:

| # | Field | # | Field |
| --- | --- | --- | --- |
| 1 | `startup.total_funding_usd` | 5 | `investor.aum_usd` |
| 2 | `startup.institutional_funding_last_5yrs` | 6 | `fundinground.amount_usd` |
| 3 | `founder.contact_email` | 7 | `fundinground.valuation_usd` |
| 4 | `executive.contact_email` | | |

The role-by-field matrix and the enforcement rules every calling surface honours are in [`docs/access-control.md`](./docs/access-control.md).

## Getting Started

### Prerequisites

Every item is a hard prerequisite of the target instance. [`docs/deployment-runbook.md`](./docs/deployment-runbook.md) asserts them before the Update Set is imported.

- **A reachable ServiceNow Personal Developer Instance.** Basic authentication is supplied through the `SERVICENOW_USERNAME` and `SERVICENOW_PASSWORD` environment secrets. No credential value appears anywhere in this package.
- **The operating account holds the platform `admin` role.** Remote-update-set access requires it, as do the metadata reads the post-commit gates issue.
- **The Now Platform release is at or above the Yokohama floor**, so Flow Designer, the Automated Test Framework, Service Portal and Connection & Credential Aliases are all generally available. If the release predates that floor, request a new Personal Developer Instance and do not downgrade feature usage.
- **ATF execution is enabled and a test-designer role is held.** Without both, every suite of guide 05 is unrunnable, no test produces a result, and the coverage gate cannot be evaluated at all.
- **The two Connection & Credential Aliases already hold live credentials** — `x_bst_startuptrk.crunchbase_api` and `x_bst_startuptrk.linkedin_oauth`, provisioned on the instance by their owner. Guide 01 verifies and binds those existing aliases; it creates no secret. While either alias is unprovisioned, every ingestion run reads the fallback dataset and every result is labelled fallback-validated.
- **Python 3 for the validator.** [`scripts/validate_update_set_xml.py`](./scripts/validate_update_set_xml.py) uses only the standard library, so it needs no installation and no virtual environment.

### Deploy Order

Ten steps. Each names the document that owns it.

| Step | Work | Owning document |
| --- | --- | --- |
| 1 | Validate the Update Set XML. Both gate G-1 and gate G-2 must pass, and a non-zero exit blocks the deployment. | [`scripts/validate_update_set_xml.py`](./scripts/validate_update_set_xml.py) |
| 2 | Run the pre-flight checks, then upload, poll for load, preview, require an empty error-type problem set, and commit. | [`docs/deployment-runbook.md`](./docs/deployment-runbook.md) |
| 3 | Run the sixteen post-commit gates. Any failure triggers the rollback and the failing gate is reported. | [`docs/validation-gates.md`](./docs/validation-gates.md) |
| 4 | Verify and bind the two Connection & Credential Aliases, and run each connection test. | [`docs/manual-build/01-connection-credential-aliases.md`](./docs/manual-build/01-connection-credential-aliases.md) |
| 5 | Build the Crunchbase ingestion flow. | [`docs/manual-build/02-flow-crunchbase-ingestion.md`](./docs/manual-build/02-flow-crunchbase-ingestion.md) |
| 6 | Build the LinkedIn ingestion flow. | [`docs/manual-build/03-flow-linkedin-ingestion.md`](./docs/manual-build/03-flow-linkedin-ingestion.md) |
| 7 | Build the portal, the theme, the five pages and the eight widgets. | [`docs/manual-build/04-service-portal-pages-and-widgets.md`](./docs/manual-build/04-service-portal-pages-and-widgets.md) |
| 8 | Load the six fallback CSV files into the staging table. | [`docs/manual-build/06-staging-table-csv-import.md`](./docs/manual-build/06-staging-table-csv-import.md) |
| 9 | Build and run the ten ATF suites — **last**. | [`docs/manual-build/05-atf-test-suites.md`](./docs/manual-build/05-atf-test-suites.md) |
| 10 | Walk the acceptance evidence and record it against the five success criteria. | [`docs/validation-checklist.md`](./docs/validation-checklist.md) |

Four ordering constraints fix that sequence, and each is mechanical:

1. **Aliases before flows.** The flows bind their aliases **by name**, and a name mismatch fails at run time, not at build time.
2. **Staging import before any fallback exercise.** The fallback branch reads `x_bst_startuptrk_ingest_staging`, and an empty table demonstrates no cleaning rule.
3. **Pages and widgets before the portal walkthrough.** The walkthrough supplies the evidence for success criterion 5.
4. **ATF last.** Its suites exercise the tables, the access-control records, the REST resources and both flows.

Steps 8 and 9 place guide **06** before guide **05**. That is the one point at which the execution order departs from the filename order. [`docs/manual-build-instructions.md`](./docs/manual-build-instructions.md) is authoritative for this ordering and states it guide by guide with each dependency.

## Documentation Map

Fourteen documents under [`docs/`](./docs). Read the one that answers the question in hand.

| Document | Read this when |
| --- | --- |
| [`docs/data-model.md`](./docs/data-model.md) | Confirming a table, column, type, length, mandatory flag, choice value, cascade rule or the `portfolio_count` derivation. |
| [`docs/access-control.md`](./docs/access-control.md) | Establishing which role may read which field, or verifying a premium-field denial under impersonation. |
| [`docs/api-reference.md`](./docs/api-reference.md) | Calling the API — paths, methods, filters, the pagination envelope, status codes, error bodies or the Script Include call graph. |
| [`docs/deployment-runbook.md`](./docs/deployment-runbook.md) | Importing the Update Set, or recovering from a load, preview, commit or gate failure. |
| [`docs/validation-gates.md`](./docs/validation-gates.md) | Running the post-commit gates and recording their evidence. |
| [`docs/validation-checklist.md`](./docs/validation-checklist.md) | Signing off delivery against the five success criteria of prompt section 10.0. |
| [`docs/gaps-and-flags.md`](./docs/gaps-and-flags.md) | Asking whether a requirement was implemented, worked around or excluded, and on what basis. |
| [`docs/manual-build-instructions.md`](./docs/manual-build-instructions.md) | Sequencing the manual build, or deciding whether an artifact ships as XML or is built by hand. |
| [`docs/manual-build/01-connection-credential-aliases.md`](./docs/manual-build/01-connection-credential-aliases.md) | Verifying and binding the Crunchbase and LinkedIn aliases, or diagnosing a connection test. |
| [`docs/manual-build/02-flow-crunchbase-ingestion.md`](./docs/manual-build/02-flow-crunchbase-ingestion.md) | Building or debugging the Crunchbase flow, its cadence guard or its fallback branch. |
| [`docs/manual-build/03-flow-linkedin-ingestion.md`](./docs/manual-build/03-flow-linkedin-ingestion.md) | Building or debugging the LinkedIn flow and the shared Startup upsert path. |
| [`docs/manual-build/04-service-portal-pages-and-widgets.md`](./docs/manual-build/04-service-portal-pages-and-widgets.md) | Building the portal, editing a widget, or checking a design-system token or Bootstrap class. |
| [`docs/manual-build/05-atf-test-suites.md`](./docs/manual-build/05-atf-test-suites.md) | Building a suite, reading a test result, or reproducing the impersonation, rate-limit and provenance techniques. |
| [`docs/manual-build/06-staging-table-csv-import.md`](./docs/manual-build/06-staging-table-csv-import.md) | Loading the CSV files, or repairing a field mapping in the three-way staging contract. |

The column contract for those CSV files, and the fallback-only posture of the dataset, are in [`sample-data/README.md`](./sample-data/README.md).

## Legacy Repository

The repository also holds the earlier Flask and React implementation. The `src/`, `tests/`, `documentation/` and `config/` trees, together with `docker-compose.yml`, `package.json` and `pytest.ini`, remain in place as **read-only historical reference**: they are not built, not run and not tested, and the ServiceNow application depends on none of them. The retired stack comprised Flask, SQLAlchemy, PostgreSQL, Redis, Elasticsearch, Celery, React with Redux and Material-UI, Nginx, Supervisor and Docker Compose. Supersession of that stack is recorded in the repository-root [`README.md`](../README.md); the reasoning behind retiring it belongs to the decision log named below.

## Known Gaps

Premium subscription billing and payment processing have **no ServiceNow equivalent**: the platform grants entitlements through roles and offers no commerce, checkout or payment capability. That requirement is formally flagged under prompt section 11.0 — not implemented, and not half-implemented. Every other requirement with no clean platform equivalent, every documented workaround and every consciously excluded feature of the ten in the source requirements specification is inventoried in [`docs/gaps-and-flags.md`](./docs/gaps-and-flags.md), which is the single collection point for that obligation across the package.

## Design Rationale and Governance

This package states **what** each artifact is and **which requirement it implements**. Every *why*, every alternative considered and every risk carried is recorded in the **repository-level governance tree** at `../docs/` — one directory level above this package, and distinct from this package's own [`docs/`](./docs) directory, which holds the fourteen deliverable documents above.

**All three documents below are delivered and readable**, in keeping with the convention used throughout this package: every link resolves to a file in this repository, so a reader can follow any of them and read the content the statement beside it describes.

| Governance document | What it holds |
| --- | --- |
| [`../docs/decisions/DECISION_LOG.md`](../docs/decisions/DECISION_LOG.md) | Every non-trivial decision as a table row: what was decided, what alternatives existed, why that choice was made and what risks it carries. **The single source of truth for "why".** |
| [`../docs/decisions/TRACEABILITY_MATRIX.md`](../docs/decisions/TRACEABILITY_MATRIX.md) | The bidirectional mapping from legacy construct and stated requirement to delivered artifact, and back, at one hundred per cent coverage with no gaps. |
| [`../docs/review/CRITICAL_DECISIONS.md`](../docs/review/CRITICAL_DECISIONS.md) | The five highest-risk decisions, ordered by risk, each with its reviewer persona and exactly what that reviewer checks. |

## License

Licensed under the terms in the repository-root [`LICENSE`](../LICENSE) file.
