# Boston Startup Tracker

A comprehensive web-based platform designed to aggregate, analyze, and present data on venture-backed companies headquartered in Boston.

## ServiceNow Implementation (Current Deliverable)

The active implementation of this platform is the ServiceNow scoped application **`x_bst_startuptrk`**, which lives under [`servicenow-startup-tracker-poc/`](servicenow-startup-tracker-poc/). Everything below this section describes the earlier Flask and React stack, which is retained as historical reference only and is not built, run, or tested.

Start with the package index, which links every document in the deliverable:

- [`servicenow-startup-tracker-poc/README.md`](servicenow-startup-tracker-poc/README.md) — package contents, prerequisites, deploy order, and the full documentation map.

The paths an operator needs directly:

- [`servicenow-startup-tracker-poc/update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml`](servicenow-startup-tracker-poc/update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml) — the single importable Update Set.
- [`servicenow-startup-tracker-poc/docs/deployment-runbook.md`](servicenow-startup-tracker-poc/docs/deployment-runbook.md) — how to import it: pre-flight checks, the import sequence, the post-commit gates, and the rollback.
- [`servicenow-startup-tracker-poc/scripts/validate_update_set_xml.py`](servicenow-startup-tracker-poc/scripts/validate_update_set_xml.py) — the two-level Update Set XML validator, invoked directly.
- [`servicenow-startup-tracker-poc/docs/manual-build-instructions.md`](servicenow-startup-tracker-poc/docs/manual-build-instructions.md) — the index for the artifacts built through the ServiceNow interface.

Repository-level governance lives under [`docs/`](docs/):

- [`docs/review/CRITICAL_DECISIONS.md`](docs/review/CRITICAL_DECISIONS.md) — the five highest-risk decisions and the reviewer for each.
- [`docs/decisions/DECISION_LOG.md`](docs/decisions/DECISION_LOG.md) — the single source of truth for why every choice was made.
- [`docs/decisions/TRACEABILITY_MATRIX.md`](docs/decisions/TRACEABILITY_MATRIX.md) — the bidirectional map from legacy construct to delivered artifact.

## Features

- Comprehensive startup profiles with enriched data
- Advanced search and filtering capabilities
- Real-time updates on funding rounds, job openings, and news
- Interactive data visualizations and trend analysis tools
- User account management with role-based access control
- API access for programmatic data retrieval

## Technology Stack (Legacy — Superseded)

> **Superseded — historical reference.** The stack below is the retired Flask and React implementation. It is replaced by a single ServiceNow scoped application, `x_bst_startuptrk`, on the ServiceNow Now Platform. See [`docs/decisions/DECISION_LOG.md`](docs/decisions/DECISION_LOG.md) for the rationale.

- Frontend: React.js with Redux
- Backend: Python with Flask
- Database: PostgreSQL
- Caching: Redis
- Search: Elasticsearch
- Task Queue: Celery
- Containerization: Docker
- Cloud Infrastructure: AWS

## Getting Started

### Prerequisites

> **Superseded — historical reference.** The three items below apply only to the retired stack and are deliberately not provisioned. The current prerequisite is access to a ServiceNow instance with the administrator role, on a release at or above Yokohama; [`servicenow-startup-tracker-poc/docs/deployment-runbook.md`](servicenow-startup-tracker-poc/docs/deployment-runbook.md) states the full set. See [`docs/decisions/DECISION_LOG.md`](docs/decisions/DECISION_LOG.md) for the rationale.

- Docker and Docker Compose
- Node.js 14+
- Python 3.8+

### Installation

> **Superseded — historical reference.** The steps below are non-functional: no Dockerfile exists anywhere in this repository, so `docker-compose up --build` cannot succeed and nothing is served at `http://localhost:3000`. To install the current implementation, follow the Update Set import procedure in [`servicenow-startup-tracker-poc/docs/deployment-runbook.md`](servicenow-startup-tracker-poc/docs/deployment-runbook.md). See [`docs/decisions/DECISION_LOG.md`](docs/decisions/DECISION_LOG.md) for the rationale.

1. Clone the repository
2. Run `docker-compose up --build`
3. Access the application at http://localhost:3000

## Development

> **Superseded — historical reference.** The retired stack is not built, run, or tested. Work on the current implementation is covered by [`servicenow-startup-tracker-poc/docs/manual-build-instructions.md`](servicenow-startup-tracker-poc/docs/manual-build-instructions.md).

Instructions for setting up a development environment and running tests.

## Deployment

> **Superseded — historical reference.** Deploying the current implementation is covered by [`servicenow-startup-tracker-poc/docs/deployment-runbook.md`](servicenow-startup-tracker-poc/docs/deployment-runbook.md).

Overview of the deployment process and required environment variables.

## Contributing

Guidelines for contributing to the project, including coding standards and pull request process.

## License

Information about the project's license.

<!-- Human Tasks:
- Add more detailed installation instructions, including any required environment variables
- Expand the Development section with instructions for running tests and linters
- Provide more information about the project's architecture and component interactions
- Include troubleshooting tips for common issues
- Add badges for build status, test coverage, and other relevant metrics
- Include information about the data sources used and any necessary attributions
- Add a section on security considerations and data privacy
- Include contact information or links to project management tools (e.g., issue tracker)
- Provide examples of API usage if applicable
- Add a changelog or link to release notes

Superseded — historical reference: the items above pertain to the retired Flask and React stack. The current implementation is documented under servicenow-startup-tracker-poc/.
-->