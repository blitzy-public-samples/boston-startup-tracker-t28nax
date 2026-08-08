# Manual build 04 — Service Portal pages and widgets — `x_bst_startuptrk`

This guide builds the Service Portal experience of the ServiceNow scoped application `x_bst_startuptrk` by hand, on the instance, through the platform's own interface. It specifies **one** portal record, **one** theme record, **five** pages and **eight** widgets, and for each one it states every field to set, every option in the option schema, the server-script responsibilities, the client-controller responsibilities, the HTML template structure with the Bootstrap classes it uses, and the widget CSS. It also states the design-system contract every widget author must satisfy, the access-control rules every widget server script must honour, and the verification checklist to run before this guide is signed off.

**Authority.** The frozen prompt and the Agent Action Plan are authoritative for all application content. The Update Set XML at [`../../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml`](../../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml) is the authoritative source for every table name, column name, choice value, Script Include class name, method name, system-property key and role name cited below; the identifiers used here match those records character for character, and the same identifiers appear in [`../data-model.md`](../data-model.md), [`../access-control.md`](../access-control.md) and [`../api-reference.md`](../api-reference.md). No variant spelling of any identifier is valid. Where this guide and those records disagree, the records are checked against the prompt and the plan first; where the records match the specification, this guide is corrected to them.

This document carries **no rationale**. It states what to build and how to build it. Every decision behind the portal, every alternative considered and every risk it carries is recorded in [`../../../docs/decisions/DECISION_LOG.md`](../../../docs/decisions/DECISION_LOG.md), which is the single source of truth for "why". Five points in this guide depart from a literal reading of the requirements — the five-tab company profile, the "Team" to "People" tab rename, the dropped "Similar Companies" tab, query-parameter routing in place of path-style routes, and the 1024-pixel viewport floor. Each is stated below as a build mechanic and cross-referenced to that log. None is argued here.

Operational warnings **are** in scope for this guide and are marked as such. The administrator-override warning under [Operational warning — the administrator override](#operational-warning--the-administrator-override) is the most important one in this file and must not be skipped.

## Referenced documents

This guide is executable on its own. The portal, the theme, the token declarations, all five pages, all eight widgets, the design-system contract, the access-control rules and the verification checklist are stated here in full. An operator needs no other file to build the portal.

**Every document named below is delivered and readable.** Each link resolves to a file in this package, among them `../../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml`, `../data-model.md`, `../access-control.md`, `../api-reference.md` and `../validation-gates.md`, so a reader can follow any link and read the content the statement around it describes; no link is a forward reference to something still to be written.

**Reviewer.** This guide is the artifact validated by **entry 5 of [`../../../docs/review/CRITICAL_DECISIONS.md`](../../../docs/review/CRITICAL_DECISIONS.md), risk Medium, reviewer persona UX**, whose check is to walk all five routes and confirm the premium upsell treatment appears wherever a gated field is denied — an obligation placed on this file by the project rule **Critical Decision Review Document**.

## Position in the build order

This is **guide 04 of six**, and it is **step 4** of the execution order below. The order is stated in full in [`../manual-build-instructions.md`](../manual-build-instructions.md); it is repeated here so this guide can be run without it.

| Step | Guide | Why it sits here |
| --- | --- | --- |
| 1 | [`./01-connection-credential-aliases.md`](./01-connection-credential-aliases.md) | The two Connection and Credential Aliases the flows bind to by name. Nothing downstream can authenticate without them. |
| 2 | [`./02-flow-crunchbase-ingestion.md`](./02-flow-crunchbase-ingestion.md) | The Crunchbase ingestion flow, which requires the alias from step 1. |
| 3 | [`./03-flow-linkedin-ingestion.md`](./03-flow-linkedin-ingestion.md) | The LinkedIn ingestion flow, which requires the alias from step 1. |
| **4** | **This guide** | **The portal, theme, five pages and eight widgets.** |
| 5 | [`./06-staging-table-csv-import.md`](./06-staging-table-csv-import.md) | The staging-table CSV load, which puts records on the instance for the portal walkthrough and for the fallback ingestion path. |
| 6 | [`./05-atf-test-suites.md`](./05-atf-test-suites.md) | The Automated Test Framework suites, **last**, because they exercise everything the five preceding guides build. |

Guides 01, 02 and 03 precede this one. Guide 06 follows it, then guide 05 runs last.

The portal can be built before any record exists on the instance, but it cannot be **walked through** until records exist. Run guide 06 before the walkthrough under [Build verification](#build-verification).

## Preconditions

Do not begin this guide until every item below holds.

| # | Precondition | How to confirm |
| --- | --- | --- |
| 1 | The Update Set has been uploaded and has reached the `loaded` state. | The `sys_remote_update_set` record shows `state` `loaded`. |
| 2 | The preview has completed with an **empty error-type problem set**. | A read of `sys_update_preview_problem` filtered to this remote update set and `type=error` returns an empty `result` array. Warnings are logged and do not block. |
| 3 | The Update Set has **committed**. | The `sys_remote_update_set` record shows `state` `committed`. |
| 4 | **All sixteen post-commit gates have passed.** | Run every gate in [`../validation-gates.md`](../validation-gates.md) and record `pass` for all sixteen in that document's evidence record. The aggregate pass condition is 16 of 16; there is no partial pass. |
| 5 | The nine Script Includes this portal calls into are on the instance. | `sys_script_include` carries `AppProperties`, `RestQueryHelper`, `RestResponseBuilder`, `RateLimitService`, `StartupSearchService`, `InvestorPortfolioService`, `IngestionLogger`, `IngestionMapper` and `PrivacyRetentionService`, all in the `x_bst_startuptrk` scope. The call graph is in [`../api-reference.md`](../api-reference.md). |
| 6 | The thirteen scoped system properties are on the instance. | `sys_properties` carries all thirteen `x_bst_startuptrk.*` keys, including `x_bst_startuptrk.rest.default_limit`, `x_bst_startuptrk.rest.max_limit` and `x_bst_startuptrk.inclusion.location_tokens`. The inventory is in [`../api-reference.md`](../api-reference.md). |
| 7 | You are working in the `x_bst_startuptrk` application scope. | The application picker reads **Boston Startup Tracker**. Every record this guide creates must carry that scope. |
| 8 | You hold a role that can create Service Portal records. | You can open `sp_portal`, `sp_theme`, `sp_page`, `sp_widget`, `sp_container`, `sp_row`, `sp_rectangle` and `sp_instance` and insert into each. |

The Script Include and property counts in preconditions 5 and 6 are **nine** and **thirteen**, which is what the Update Set delivers. [`../api-reference.md`](../api-reference.md) records, under its inventory note, that both figures exceed the Agent Action Plan's planned 8 and 11; the addition is `PrivacyRetentionService` together with the two `x_bst_startuptrk.privacy.*` properties. No widget in this guide calls `PrivacyRetentionService` or reads either privacy property.

### Why this guide exists rather than more Update Set XML

Only tables carrying the update-synch attribute are captured into `sys_update_xml`, and adding that attribute to a table that lacks it out of the box is unsupported. The portal, theme, page, container, row, rectangle, instance and widget tables are outside the captured set, so these artifacts are built through the platform interface instead — which is why the delivered Update Set contains **zero** `sp_portal`, `sp_theme`, `sp_page` and `sp_widget` records.

## Platform constraint

**Service Portal only. UI Builder is forbidden.** Prompt section 5.0 binds this absolutely.

- Author **no** `sys_ux_*` record of any kind — no experience record, no page macroponent, no component, no page registry entry, no route, no theme record in the UI Builder tables.
- Do **not** open the UI Builder designer to create any part of this application.
- Every artifact in this guide is a Service Portal record: `sp_portal`, `sp_theme`, `sp_page`, `sp_container`, `sp_row`, `sp_rectangle`, `sp_instance` and `sp_widget`.
- The only framework surfaces used inside a widget are AngularJS 1.x and Bootstrap 3.3.6, both of which the platform already provides.

## What this guide builds

| Artifact class | Table | Count | Names |
| --- | --- | --- | --- |
| Portal | `sp_portal` | **1** | url suffix `bst` |
| Theme | `sp_theme` | **1** | Boston Startup Tracker |
| Pages | `sp_page` | **5** | `bst_home`, `bst_company`, `bst_investor`, `bst_dashboard`, `bst_account` |
| Widgets | `sp_widget` | **8** | `bst-startup-search`, `bst-startup-results`, `bst-company-profile`, `bst-investor-profile`, `bst-trends-kpi`, `bst-trends-charts`, `bst-account-summary`, `bst-premium-upsell` |

Eight widget names, seven of which are placed directly on a page. The eighth, `bst-premium-upsell`, is a reusable partial embedded by **three** hosts and is never given a page of its own.

Build in this order, because each step references the one before it.

1. The eight widgets — [Step 4](#step-4--the-eight-widgets). A page instance cannot name a widget that does not exist.
2. The theme — [Step 2](#step-2--the-theme-record). The portal record binds to it.
3. The five pages — [Step 3](#step-3--the-five-pages).
4. The portal — [Step 1](#step-1--the-portal-record). Its homepage field binds to `bst_home`, so build that page first.

The step numbering below follows the reading order of the artifacts, not the insertion order. Insert in the order of the four bullets above.

## Step 1 — The portal record

One record in `sp_portal`. Set every field in the table below; the **Value** column is the value to enter, and a value of *empty* means the field is deliberately left blank.

| Field | Column | Value | Note |
| --- | --- | --- | --- |
| Title | `title` | `Boston Startup Tracker` | The portal title. The Stock Header widget renders it. |
| URL suffix | `url_suffix` | `bst` | **Exactly `bst`.** The portal is then reached at `/bst`. Every link in [Routing and navigation](#routing-and-navigation) is written against this suffix. |
| Homepage | `homepage` | `bst_home` | The `sp_page` record whose `id` is `bst_home`. Build that page before this record. |
| Theme | `theme` | `Boston Startup Tracker` | The `sp_theme` record built in [Step 2](#step-2--the-theme-record). |
| Application | `sys_scope` | `Boston Startup Tracker` | The `x_bst_startuptrk` scope. Confirm this before saving. |
| Login page | `login_page` | `login` | The stock login page. The portal has no custom sign-in surface. |
| Default title | `default_title` | `Boston Startup Tracker` | Applied to a page that declares no title of its own. |
| Hompage dashboard | `homepage_dashboard` | *empty* | No dashboard homepage. The homepage is the `bst_home` page. |
| Knowledge base | `kb_knowledge_base` | *empty* | The application ships no knowledge base. Leave blank so the stock header renders no knowledge link. |
| Catalog | `sc_catalog` | *empty* | The application ships no service catalog. |
| Quick start configuration | `quick_start_config` | *empty* | Not used. |
| Icon | `icon` | *empty* | No favicon override. |
| Logo | `logo` | *empty* | No image attachment. The header renders `title` as text. |
| Notification email script | `notification_email_script` | *empty* | The portal sends no notifications. |
| Enable AI Search | `enable_ais` | `false` | Search is served by `bst-startup-search` through `StartupSearchService`, not by a platform search engine. |
| Hide portal name in header | `hide_portal_name` | `false` | The title is the primary navigation anchor. |
| Direct order guest access | `sp_rectangle_menu` and the guest-access fields | *empty* / `false` | Not used. |
| CSS variables | `sp_css_variable` | *empty* | **Leave the portal-level variables empty.** All tokens are declared once on the theme; see [Theme and variable authoring rules](#theme-and-variable-authoring-rules). |

After saving, open `https://<instance>.service-now.com/bst` and confirm the portal resolves and the `bst_home` page renders.

## Step 2 — The theme record

### The theme record fields

Create a **new** `sp_theme` record. Do not edit, clone or extend a stock theme; a stock theme is shared by the stock portals on the instance, and editing one changes them.

| Field | Column | Value | Note |
| --- | --- | --- | --- |
| Name | `name` | `Boston Startup Tracker` | Bound from `sp_portal.theme`. |
| Application | `sys_scope` | `Boston Startup Tracker` | The `x_bst_startuptrk` scope. |
| Header | `header` | Stock Header | The stock header widget. It renders Bootstrap `.navbar`. |
| Footer | `footer` | Stock Footer | The stock footer widget. |
| Navigation page | `navigation_page` | *empty* | The portal uses no side navigation. |
| CSS variables | `css_variables` | The declarations in [The CSS-variables field](#the-css-variables-field) | **The single declaration site for every token in this portal.** |
| Style sheet | `style_sheet` | *empty* | No attached stylesheet. Any global rule goes in a CSS include, subject to the shallow-selector rule below. |

### The CSS-variables field

Every token the widgets reference is declared here, in the theme's CSS-variables field, and **nowhere else**. Declare each variable in the table below with a SASS declaration of the form `$variable: value;`, one per line, grouped in the order the table gives.

**Four** values are carried forward from the legacy stylesheet — the body font stack, the page background, the link colour and the container maximum. They are cited under [The legacy design-token surface](#the-legacy-design-token-surface), which is the only place in this guide where a literal value appears; read them from there and declare them here. Every other variable takes its Bootstrap 3.3.6 default, declared **explicitly** so the theme owns the value rather than inheriting it silently.

| Group | Variable | Governs | Value to declare |
| --- | --- | --- | --- |
| Brand | `$brand-primary` | The primary action colour behind `.btn-primary`, `.label-primary`, `.panel-primary` and link text. | The legacy link colour, carried forward. See [The legacy design-token surface](#the-legacy-design-token-surface). |
| Brand | `$brand-success` | `.alert-success`, `.label-success`, `.progress-bar-success`. Required by the alert and label components this portal uses. | Bootstrap 3.3.6 default. |
| Brand | `$brand-info` | `.alert-info`, `.label-info`. **Used by `bst-premium-upsell`.** | Bootstrap 3.3.6 default. |
| Brand | `$brand-warning` | `.alert-warning`, `.label-warning`. | Bootstrap 3.3.6 default. |
| Brand | `$brand-danger` | `.alert-danger`, `.label-danger`. | Bootstrap 3.3.6 default. |
| Surface | `$body-bg` | The page background of the whole portal. | The legacy page background, carried forward. See [The legacy design-token surface](#the-legacy-design-token-surface). |
| Surface | `$sp-body-bg` | The Service Portal body background, in the platform's own `$sp-*` namespace. Declare it to the same value as `$body-bg` so the portal chrome and the page agree. | The legacy page background, carried forward. |
| Surface | `$panel-bg` | The fill of every `.panel`. Replaces the legacy surface elevation. | Bootstrap 3.3.6 default. |
| Surface | `$panel-default-border` | The border of every `.panel.panel-default`. | Bootstrap 3.3.6 default. |
| Typography | `$font-family-sans-serif` | The body typeface of the whole portal. | The legacy body font stack, carried forward. See [The legacy design-token surface](#the-legacy-design-token-surface). |
| Typography | `$font-size-base` | The base type size from which every heading size is computed. No legacy value existed. | Bootstrap 3.3.6 default. |
| Typography | `$line-height-base` | The base line height and therefore the vertical rhythm. No legacy value existed. | Bootstrap 3.3.6 default. |
| Typography | `$headings-font-family` | The heading typeface. Declare it to `$font-family-sans-serif` unless a display face is introduced. | `$font-family-sans-serif`. |
| Typography | `$headings-font-weight` | The heading weight. Replaces the legacy heading variant props. | Bootstrap 3.3.6 default. |
| Layout | `$container-lg` | The maximum width of `.container` at the large breakpoint, which is the widest layout this portal serves. | The legacy container maximum, carried forward. See [The legacy design-token surface](#the-legacy-design-token-surface). |
| Layout | `$grid-gutter-width` | The horizontal gutter between grid columns and the spacing unit widget CSS uses for block separation. | Bootstrap 3.3.6 default. |
| Layout | `$padding-base-vertical` | The vertical padding of `.btn` and `.form-control`, and the spacing unit for inset padding in widget CSS. | Bootstrap 3.3.6 default. |
| Layout | `$padding-base-horizontal` | The horizontal padding of `.btn` and `.form-control`, and the spacing unit for inset padding in widget CSS. | Bootstrap 3.3.6 default. |
| Radius | `$border-radius-base` | The corner radius of `.btn`, `.form-control` and `.panel`. No legacy value existed. | Bootstrap 3.3.6 default. |
| Radius | `$border-radius-large` | The radius of `.btn-lg` and large panels. | Bootstrap 3.3.6 default. |
| Radius | `$border-radius-small` | The radius of `.btn-sm` and `.label`. | Bootstrap 3.3.6 default. |
| Table | `$table-bg` | The fill of every `.table`. Replaces the legacy inline table styling. | Bootstrap 3.3.6 default. |
| Table | `$table-border-color` | The rule colour of every `.table` and `.table-striped`. | Bootstrap 3.3.6 default. |
| Button | `$btn-primary-bg` | The fill of `.btn-primary`. Declare it to `$brand-primary`. | `$brand-primary`. |
| Button | `$btn-primary-color` | The label colour of `.btn-primary`. | Bootstrap 3.3.6 default. |
| Navbar | `$navbar-height` | The height of the header `.navbar` the stock Header widget renders. | Bootstrap 3.3.6 default. |
| Navbar | `$navbar-default-bg` | The fill of a default `.navbar`. | Bootstrap 3.3.6 default. |
| Navbar | `$navbar-inverse-bg` | The fill of `.navbar-inverse`. Declare it even if the header uses the default variant, because Bootstrap derives the inverse navbar border from it. | Bootstrap 3.3.6 default. |
| Breakpoint | `$screen-sm-min` | The small breakpoint. Declared for completeness; **no `.col-sm-*` class is authored in this portal.** See [Responsive stance — the 1024-pixel floor](#responsive-stance--the-1024-pixel-floor). | Bootstrap 3.3.6 default. |
| Breakpoint | `$screen-md-min` | The medium breakpoint, at which `.col-md-*` engages. | Bootstrap 3.3.6 default. |
| Breakpoint | `$screen-lg-min` | The large breakpoint, at which `.col-lg-*` engages. | Bootstrap 3.3.6 default. |
| `$sp-*` namespace | `$sp-body-bg` | Declared under Surface above. | As above. |
| `$sp-*` namespace | `$sp-tagline-color` | The tagline text colour in the portal chrome. | Platform default for the release. |
| `$sp-*` namespace | `$sp-navbar-divider-color` | The divider rule inside the portal navbar. | Platform default for the release. |

The `$sp-*` namespace carries further entries beyond the three named above. The authoritative list for a given instance is served per portal by the compiled bootstrap stylesheet; read it from that instance rather than from this guide, and declare only the entries this portal actually applies.

Bootstrap's own derivation rules reduce the declaration burden: a variable left undeclared is computed from the ones that are, so declaring the small primary set above propagates consistently. `$navbar-inverse-border`, for example, is derived from `$navbar-inverse-bg`.

### Theme and variable authoring rules

Follow all five. Each one prevents a failure that is silent — the portal compiles and renders, and the defect surfaces later as a style that cannot be overridden or a stylesheet that has grown many times larger than it should be.

1. **Declare variables only in the portal and theme CSS-variables fields; apply them in CSS includes and in widget CSS.** In this portal the theme's field is the single declaration site and the portal's field is left empty.
2. **Never place a CSS *rule* in a variables field.** A variables field is concatenated into the compiled stylesheet once per consumer, so a rule placed there is duplicated many times in the output. Put rules in a CSS include or in the widget's own CSS field.
3. **Mark any SASS variable declared inside a widget with `!default`.** A widget-local declaration is then a fallback, and the theme's value wins.
4. **A variable defined in a widget record is not visible to a widget-instance record.** Do not declare a variable in a widget and expect to reference it from an instance's option values or from another widget.
5. **Keep global CSS shallow — two or three selectors deep at most — and never globally restyle Bootstrap's `panel`, `well`, `form` or `alert` classes.** A global rule on one of those leaks into every widget on every page, including the stock widgets. Scope such a rule to the widget's own root class instead.

## Step 3 — The five pages

Exactly five `sp_page` records. No sixth page is authored: the administrative surface is served by the platform's own list and form views inside the scoped app, reached from the application menu the Update Set delivers, and not by a portal route.

### The page composition model

Every page is composed through the same four-level record chain. Build it top down.

| Level | Table | Parent field | Fields to set |
| --- | --- | --- | --- |
| 1 | `sp_page` | — | `id`, `title`, `sys_scope`, `public`, `roles` |
| 2 | `sp_container` | `sp_page` | `order`, `name`, `width`, `sys_scope` |
| 3 | `sp_row` | `sp_container` | `order`, `sys_scope` |
| 4 | `sp_rectangle` | `sp_row` | `order`, `size_md`, `size_lg`, `sys_scope` |
| 5 | `sp_instance` | `sp_column` — the reference to the `sp_rectangle` | `sp_widget`, `order`, `title`, `sys_scope`, and the option values under **Widget Options** |

Rules that apply to every page below.

- `sp_container.width` is `container` on every container in this portal. Never `container-fluid`: the layout is bounded by `$container-lg`.
- On every `sp_rectangle`, set **`size_md` and `size_lg` only**. Leave `size`, `size_xs` and `size_sm` empty, so no extra-small or small refinement is authored. The rectangle then emits `.col-md-*` and `.col-lg-*` and nothing narrower.
- The column spans in one row must total 12.
- `sp_page.public` is `false` on all five pages, and `sp_page.roles` is left empty. Access is decided by the access controls in [`../access-control.md`](../access-control.md), not by a page role list; a caller holding none of the three application roles reaches the page and sees no data.
- `sp_instance.sys_scope` is `Boston Startup Tracker` on every instance, including instances of stock widgets.
- Option values are entered on the `sp_instance` record under **Widget Options**, and the widget server script reads them as `options.<name>`.

Two stock widgets are **instantiated** on these pages but are not authored by this guide, so they are not part of the count of eight: **Breadcrumbs**, placed on the four non-home pages, and the **Stock Header** and **Stock Footer**, which are bound through the theme rather than placed on a page.

### `bst_home` — Home / Search

| `sp_page` field | Value |
| --- | --- |
| `id` | `bst_home` |
| `title` | `Boston Startup Tracker` |
| `public` | `false` |
| `roles` | *empty* |

| Container | Row | Rectangle | `size_md` | `size_lg` | Widget instance | Instance options |
| --- | --- | --- | --- | --- | --- | --- |
| 1 `Search` | 1 | 1 | `12` | `12` | `bst-startup-search` | `title` = `Find a Boston startup`, `show_industry` = `true`, `show_location` = `true`, `results_page` = `bst_home` |
| 2 `Results` | 1 | 1 | `12` | `12` | `bst-startup-results` | `title` = `Startups`, `page_size` = *empty*, `detail_page` = `bst_company`, `show_logo` = `true` |

The search widget lays its three filters out internally as three `.col-md-4` columns inside one `.row`; the page supplies one full-width rectangle.

Leaving `page_size` empty on the results instance makes the widget read `x_bst_startuptrk.rest.default_limit` through `AppProperties`. See [`bst-startup-results`](#bst-startup-results).

**The inclusion criteria are applied server-side, by `StartupSearchService`, and by nothing else.** Neither widget re-implements the predicate, adds a condition of its own on `active` or `headquarters_location`, or filters the returned rows in the client controller. The one call sequence permitted is the one specified under [`bst-startup-search`](#bst-startup-search) and [`bst-startup-results`](#bst-startup-results). This is what makes criterion 5 of [`../validation-checklist.md`](../validation-checklist.md) — "inclusion filter confirmed active" — verifiable by seeding a failing startup and observing its absence, rather than merely assertable.

### `bst_company` — Company Profile

| `sp_page` field | Value |
| --- | --- |
| `id` | `bst_company` |
| `title` | `Company profile` |
| `public` | `false` |
| `roles` | *empty* |

| Container | Row | Rectangle | `size_md` | `size_lg` | Widget instance | Instance options |
| --- | --- | --- | --- | --- | --- | --- |
| 1 `Trail` | 1 | 1 | `12` | `12` | Breadcrumbs (stock) | Defaults |
| 2 `Profile` | 1 | 1 | `12` | `12` | `bst-company-profile` | `default_tab` = `overview`, `investor_page` = `bst_investor`, `upsell_page` = `bst_account`, `jobs_limit` = `25`, `news_limit` = `10` |

`bst-premium-upsell` is **embedded by `bst-company-profile`**, not placed on this page. The host builds it in its server script with `$sp.getWidget()` and renders it with `<sp-widget>`; see [`bst-premium-upsell`](#bst-premium-upsell).

**Exactly five tabs**, in this order and with these labels: **Overview**, **Funding**, **People**, **Jobs**, **News**. "People" carries founders and executives together in one pane. The tab strip is built with Bootstrap `.nav.nav-tabs` and `.tab-content` / `.tab-pane` — never a hand-rolled tab control. The legacy component rendered six tabs; the mechanic of the reduction, the "Team" to "People" rename and the dropped "Similar Companies" tab is recorded under [Tab inventory](#tab-inventory) and the decisions behind them are in [`../../../docs/decisions/DECISION_LOG.md`](../../../docs/decisions/DECISION_LOG.md).

### `bst_investor` — Investor Profile

| `sp_page` field | Value |
| --- | --- |
| `id` | `bst_investor` |
| `title` | `Investor profile` |
| `public` | `false` |
| `roles` | *empty* |

| Container | Row | Rectangle | `size_md` | `size_lg` | Widget instance | Instance options |
| --- | --- | --- | --- | --- | --- | --- |
| 1 `Trail` | 1 | 1 | `12` | `12` | Breadcrumbs (stock) | Defaults |
| 2 `Profile` | 1 | 1 | `12` | `12` | `bst-investor-profile` | `company_page` = `bst_company`, `upsell_page` = `bst_account`, `portfolio_limit` = `50`, `rounds_limit` = `50` |

The widget lays out its own two columns internally — a `.col-md-4` overview panel and a `.col-md-8` region carrying the portfolio table and the rounds tables — so the page supplies one full-width rectangle. `x_bst_startuptrk_investor.portfolio_count` is surfaced in the overview panel. `bst-premium-upsell` is embedded by this widget.

### `bst_dashboard` — Dashboard / Trends

| `sp_page` field | Value |
| --- | --- |
| `id` | `bst_dashboard` |
| `title` | `Dashboard and trends` |
| `public` | `false` |
| `roles` | *empty* |

| Container | Row | Rectangle | `size_md` | `size_lg` | Widget instance | Instance options |
| --- | --- | --- | --- | --- | --- | --- |
| 1 `Trail` | 1 | 1 | `12` | `12` | Breadcrumbs (stock) | Defaults |
| 2 `KPIs` | 1 | 1 | `12` | `12` | `bst-trends-kpi` | `title` = `At a glance`, `show_jobs` = `true`, `show_news` = `true` |
| 3 `Trends` | 1 | 1 | `6` | `6` | `bst-trends-charts` — instance A | `title` = `Startups by funding stage`, `dimension` = `funding_stage`, `render_mode` = `svg` |
| 3 `Trends` | 1 | 2 | `6` | `6` | `bst-trends-charts` — instance B | `title` = `Startups by industry`, `dimension` = `industry`, `render_mode` = `svg` |

Container 3 carries **two instances of the same widget** in one row, each with a different `dimension` option. The two rectangles are `6` and `6`, totalling 12.

### `bst_account` — Account Management

| `sp_page` field | Value |
| --- | --- |
| `id` | `bst_account` |
| `title` | `Account management` |
| `public` | `false` |
| `roles` | *empty* |

| Container | Row | Rectangle | `size_md` | `size_lg` | Widget instance | Instance options |
| --- | --- | --- | --- | --- | --- | --- |
| 1 `Trail` | 1 | 1 | `12` | `12` | Breadcrumbs (stock) | Defaults |
| 2 `Account` | 1 | 1 | `8` | `8` | `bst-account-summary` | `title` = `Your account`, `show_entitlements` = `true`, `upsell_page` = `bst_account` |
| 2 `Account` | 1 | 2 | `4` | `4` | *empty rectangle* | Reserved. Leave with no instance so the summary occupies eight columns of twelve. |

The page shows the caller's **effective role** and the entitlements that follow from it. `bst-premium-upsell` is embedded by `bst-account-summary` and is rendered whenever the caller holds `x_bst_startuptrk.user` without `x_bst_startuptrk.premium_user`.

### Page roll-up

| # | `sp_page.id` | Title | Custom widget instances | Stock widget instances |
| --- | --- | --- | --- | --- |
| 1 | `bst_home` | Boston Startup Tracker | `bst-startup-search`, `bst-startup-results` | — |
| 2 | `bst_company` | Company profile | `bst-company-profile` (embeds `bst-premium-upsell`) | Breadcrumbs |
| 3 | `bst_investor` | Investor profile | `bst-investor-profile` (embeds `bst-premium-upsell`) | Breadcrumbs |
| 4 | `bst_dashboard` | Dashboard and trends | `bst-trends-kpi`, `bst-trends-charts` × 2 | Breadcrumbs |
| 5 | `bst_account` | Account management | `bst-account-summary` (embeds `bst-premium-upsell`) | Breadcrumbs |

Five pages. Seven of the eight custom widgets are placed on a page; `bst-premium-upsell` is embedded by three hosts and placed on none.

### Routing and navigation

**Routing is query-parameter based.** A Service Portal page is addressed as `?id=<page>` on the portal's URL suffix, and a record-scoped page adds `&sys_id=<record>`. The portal suffix is `bst`, so the base of every link is `/bst`.

Path-style routes such as `/company/<id>` are **not** reproducible without URL rewriting, so they are not used. Prompt section 5.0 mandates five routes and does not mandate their URL syntax. The deviation is flagged in [`../gaps-and-flags.md`](../gaps-and-flags.md) and its decision is recorded in [`../../../docs/decisions/DECISION_LOG.md`](../../../docs/decisions/DECISION_LOG.md).

| Route | Link form | Record parameter |
| --- | --- | --- |
| Home / Search | `/bst?id=bst_home` | — |
| Company Profile | `/bst?id=bst_company&sys_id=<startup sys_id>` | `x_bst_startuptrk_startup.sys_id` |
| Investor Profile | `/bst?id=bst_investor&sys_id=<investor sys_id>` | `x_bst_startuptrk_investor.sys_id` |
| Dashboard / Trends | `/bst?id=bst_dashboard` | — |
| Account Management | `/bst?id=bst_account` | — |

`/bst` with no `id` resolves to `sp_portal.homepage`, which is `bst_home`.

Every navigation hop between pages, with the exact link to author. Inside a widget template, write the link relative — `?id=…` — so it resolves against the current portal and the portal suffix is never hard-coded in a widget.

| # | From | Element | Link to author |
| --- | --- | --- | --- |
| 1 | `bst-startup-results` result card | `.media-heading` anchor on the startup name | `?id=bst_company&sys_id={{item.sys_id}}` |
| 2 | `bst-startup-results` result card | `.btn.btn-default` "View profile" | `?id=bst_company&sys_id={{item.sys_id}}` |
| 3 | `bst-company-profile` Funding tab | `lead_investor` cell anchor | `?id=bst_investor&sys_id={{round.lead_investor.value}}` |
| 4 | `bst-company-profile` Funding tab | each participating-investor `.label` anchor | `?id=bst_investor&sys_id={{investor.value}}` |
| 5 | `bst-investor-profile` portfolio table | startup name cell anchor | `?id=bst_company&sys_id={{startup.sys_id}}` |
| 6 | `bst-investor-profile` rounds tables | startup name cell anchor | `?id=bst_company&sys_id={{round.startup.value}}` |
| 7 | `bst-trends-kpi` KPI panel | `.btn.btn-link` "Browse startups" | `?id=bst_home` |
| 8 | `bst-premium-upsell` | `.btn.btn-primary` call to action | `?id={{options.upsell_page}}`, whose value is `bst_account` on every host |
| 9 | `bst-account-summary` | `.btn.btn-default` "Back to search" | `?id=bst_home` |
| 10 | Breadcrumbs (stock) | first crumb | `?id=bst_home` |
| 11 | Stock Header | portal title | `/bst` |

A widget reads its own route parameters from `$location` in the client controller and from `$sp` in the server script. The two forms are given under [The Angular surface available inside a widget](#the-angular-surface-available-inside-a-widget).

A page that requires a `sys_id` and receives none, or receives one that resolves to no readable record, must render an `.alert.alert-warning` carrying a plain message and a `.btn.btn-default` link back to `?id=bst_home`. It must not render an empty panel and must not throw. This applies to `bst_company` and `bst_investor`.

## Step 4 — The eight widgets

Exactly eight `sp_widget` records. Create each in the `x_bst_startuptrk` scope, with `sp_widget.servicenow` `false`, `sp_widget.public` `false` and `sp_widget.roles` empty — access is decided by the access controls in [`../access-control.md`](../access-control.md), never by a widget role list.

Every widget is specified below with the same six parts: its **name and ID**, its **option schema**, its **server script** responsibilities, its **client controller** responsibilities, its **HTML template** structure with the Bootstrap classes it uses, and its **CSS**.

### Rules that bind all eight

1. Every server script reads through `GlideRecordSecure` and serialises through `RestResponseBuilder.serialize()`. See [Step 6](#step-6--access-control-in-every-widget-server-script). This is not optional and has no exception.
2. No widget CSS contains a literal colour, spacing, radius or font value. See [Zero hard-coded values](#zero-hard-coded-values).
3. No widget uses an extra-small or small Bootstrap column class. See [Responsive stance — the 1024-pixel floor](#responsive-stance--the-1024-pixel-floor).
4. No widget references Lucide, and no widget uses an emoji character. Icons are the platform glyph font only. See [Iconography — the platform glyph font only](#iconography--the-platform-glyph-font-only).
5. Every widget CSS selector is scoped beneath the widget's own root class, and is at most three selectors deep.
6. A Script Include is constructed by its bare class name inside the scope — `new RestResponseBuilder()`, not `new x_bst_startuptrk.RestResponseBuilder()`.

### `bst-startup-search`

| `sp_widget` field | Value |
| --- | --- |
| `name` | `Startup search` |
| `id` | `bst-startup-search` |
| `sys_scope` | `Boston Startup Tracker` |

#### Option schema

| Option | Type | Default | Purpose |
| --- | --- | --- | --- |
| `title` | string | `Find a Boston startup` | The `.panel-title` text. |
| `show_industry` | boolean | `true` | Renders the industry filter. |
| `show_location` | boolean | `true` | Renders the location filter. |
| `results_page` | string | `bst_home` | The `sp_page.id` the results widget sits on. Used only when the criteria are mirrored into the URL. |

#### Server script

1. Construct `new RestResponseBuilder()` and call `hasAnyAppRole()`. When it returns false, set `data.authorised` to `false`, set nothing else, and return; the template then renders the not-entitled alert.
2. Publish the **closed** industry choice list to the client as `data.industries`, transcribed exactly from `x_bst_startuptrk_startup.industry`: `Fintech`, `Healthtech`, `SaaS`, `Consumer`, `Deeptech`, `Other`. Do not read it from a second source and do not add a value. The same six values are the list `StartupSearchService` validates against.
3. Seed the three filter values from the URL so a shared link reproduces a search: `data.criteria = { name: $sp.getParameter('name') || '', industry: $sp.getParameter('industry') || '', location: $sp.getParameter('location') || '' }`.
4. Publish `data.appliesInclusion = new StartupSearchService().appliesInclusion()`, so the template can render the "showing Boston and Cambridge startups only" note to a non-administrative caller. This is a display note; it never becomes a client-side filter.
5. Read **no** record. This widget issues no query.

#### Client controller

1. Bind the three inputs to `c.data.criteria.name`, `c.data.criteria.industry` and `c.data.criteria.location` with `ng-model`.
2. On submit, and on clear, normalise each value by trimming it, then broadcast the criteria on the root scope: `$rootScope.$broadcast('bst.search.criteria', c.data.criteria)`. `bst-startup-results` listens for that event.
3. Mirror the criteria into the URL with `$location.search()` on the same three parameter names, so the search is linkable and the widget rehydrates on reload.
4. Reject nothing and filter nothing. The controller never evaluates `active` or `headquarters_location`; the predicate lives in `StartupSearchService`.
5. Guard the industry input against a value outside `c.data.industries` by rendering it as a `<select>` over that list rather than as free text.

#### HTML template

```html
<div class="bst-search panel panel-default">
  <div class="panel-heading">
    <h3 class="panel-title">{{::options.title}}</h3>
  </div>
  <div class="panel-body">
    <div class="alert alert-warning" ng-if="!data.authorised">
      <span class="icon-info" aria-hidden="true"></span>
      <span>Your account holds no Boston Startup Tracker role.</span>
    </div>
    <form ng-if="data.authorised" ng-submit="c.submit()">
      <div class="row">
        <div class="col-md-4 col-lg-4">
          <div class="form-group">
            <label for="bst-search-name">Company name</label>
            <div class="input-group">
              <input id="bst-search-name" type="text" class="form-control"
                     ng-model="data.criteria.name" />
              <span class="input-group-btn">
                <button type="submit" class="btn btn-primary">
                  <span class="icon-search" aria-hidden="true"></span>
                  <span>Search</span>
                </button>
              </span>
            </div>
          </div>
        </div>
        <div class="col-md-4 col-lg-4" ng-if="::options.show_industry">
          <div class="form-group">
            <label for="bst-search-industry">Industry</label>
            <select id="bst-search-industry" class="form-control"
                    ng-model="data.criteria.industry">
              <option value="">All industries</option>
              <option ng-repeat="choice in ::data.industries" value="{{::choice}}">{{::choice}}</option>
            </select>
          </div>
        </div>
        <div class="col-md-4 col-lg-4" ng-if="::options.show_location">
          <div class="form-group">
            <label for="bst-search-location">Location</label>
            <input id="bst-search-location" type="text" class="form-control"
                   ng-model="data.criteria.location" />
          </div>
        </div>
      </div>
      <div class="bst-search-actions">
        <button type="submit" class="btn btn-primary">Search</button>
        <button type="button" class="btn btn-default" ng-click="c.clear()">Clear</button>
        <span class="text-muted" ng-if="data.appliesInclusion">
          Results are limited to active startups headquartered in the Boston area.
        </span>
      </div>
    </form>
  </div>
</div>
```

#### CSS

```scss
.bst-search {
    margin-bottom: $grid-gutter-width;
}

.bst-search .panel-body {
    padding-bottom: $padding-base-vertical;
}

.bst-search .bst-search-actions {
    margin-top: $padding-base-vertical;
}

.bst-search .bst-search-actions .text-muted {
    margin-left: $padding-base-horizontal;
}
```

The `.panel-body` rule is scoped beneath `.bst-search`, which is what keeps it out of every other panel on the instance.

### `bst-startup-results`

| `sp_widget` field | Value |
| --- | --- |
| `name` | `Startup results` |
| `id` | `bst-startup-results` |
| `sys_scope` | `Boston Startup Tracker` |

Where a plain paginated record list is all that is wanted, use the stock **Data Table from Instance Definition** widget instead of this one and set its `table`, `filter` and column options — pagination is native to it. This widget exists because the result card carries a company logo and a set of `.label` tags, which the stock data table cannot render.

#### Option schema

| Option | Type | Default | Purpose |
| --- | --- | --- | --- |
| `title` | string | `Startups` | The `.panel-title` text. |
| `page_size` | integer | *empty* | The page size. **Leave empty to inherit the REST default.** See the page-size note below. |
| `detail_page` | string | `bst_company` | The `sp_page.id` a result links to. |
| `show_logo` | boolean | `true` | Renders `logo_url` as the media object. |

**The page size is shared with the REST layer.** When `page_size` is empty the widget reads `x_bst_startuptrk.rest.default_limit` — shipped value `20` — through `AppProperties.getDefaultLimit()`, and it clamps any supplied value to `x_bst_startuptrk.rest.max_limit` — shipped value `50` — through `AppProperties.getMaxLimit()`. Those are the same two properties `RestQueryHelper.getLimit()` reads for the API, documented in [`../api-reference.md`](../api-reference.md), **so changing either property changes the page size on both surfaces at once.** Do not hard-code `20` or `50` in the widget.

#### Server script

1. Construct `new RestResponseBuilder()`. Call `hasAnyAppRole()`; when false set `data.authorised` to `false` and return.
2. Resolve the page size: start from `options.page_size`; when it is empty or not a whole number of 1 or more, use `new AppProperties().getDefaultLimit()`; then clamp to `new AppProperties().getMaxLimit()`. Store the resolved value as `data.limit`.
3. Resolve the offset: take `input.offset` when the widget was refreshed from the client, otherwise `$sp.getParameter('offset')`, otherwise `0`. Coerce to a whole number of 0 or more and store as `data.offset`.
4. Resolve the criteria: take `input.criteria` when present, otherwise read `name`, `industry` and `location` with `$sp.getParameter()`. Trim each. Discard an `industry` value that is not one of the six values of `x_bst_startuptrk_startup.industry`.
5. Build one query plan and apply it to **both** the result set and the count:

```javascript
var search = new StartupSearchService();
var builder = new RestResponseBuilder();
var plan = search.buildPlan(data.criteria, search.appliesInclusion());

var counted = builder.countState('x_bst_startuptrk_startup', function (query) {
    search.applyPlan(query, plan);
});

var rows = [];
var fields = ['name', 'description', 'industry', 'founded_year', 'headquarters_location',
              'website', 'logo_url', 'funding_stage', 'total_funding_usd', 'active',
              'institutional_funding_last_5yrs', 'employee_count_range'];
var startups = search.search(plan, data.limit, data.offset);
while (startups.next()) {
    rows.push(builder.serialize(startups, fields));
}

data.result = rows;
data.total_count = counted.total;
data.total_count_capped = counted.capped;
```

6. Publish `data.gated = { total_funding_usd: false, institutional_funding_last_5yrs: false }` and set a member to `true` when at least one returned row omitted that key, so the template knows to render the upsell note rather than a blank cell.
7. `data.total_count` must be the count produced by `countState()` under the **same** plan. Never count with a second, differently-built query, and never report `data.result.length` as the total.
8. When `counted.capped` is `true`, the template renders the total as a minimum. Do not present a capped total as exact.

The plan is built once and handed to both `countState()` and `search()`, which is what keeps the total in agreement with the page contents. `../api-reference.md` states the same invariant for the `GET /startups` list operation.

#### Client controller

1. Listen for the search event: `$rootScope.$on('bst.search.criteria', function (event, criteria) { c.data.criteria = criteria; c.data.offset = 0; c.server.update(); })`.
2. Expose `c.next()` and `c.previous()`, which adjust `c.data.offset` by `c.data.limit`, clamp it to the range `0` to `c.data.total_count`, and call `c.server.update()`.
3. Expose `c.hasNext()` and `c.hasPrevious()` for the pager's `ng-disabled` bindings.
4. Set `c.loading` to `true` before each `c.server.update()` and to `false` in its promise callback, so the striped progress bar shows while the server script runs.
5. Never filter, sort or re-order `c.data.result` in the client. Ordering is `name` then `sys_id`, applied by `StartupSearchService.search()`.

#### HTML template

```html
<div class="bst-results panel panel-default">
  <div class="panel-heading">
    <h3 class="panel-title">
      {{::options.title}}
      <span class="text-muted" ng-if="data.authorised">
        <span ng-if="!data.total_count_capped">{{data.total_count}} matching</span>
        <span ng-if="data.total_count_capped">more than {{data.total_count}} matching</span>
      </span>
    </h3>
  </div>
  <div class="panel-body">
    <div class="alert alert-warning" ng-if="!data.authorised">
      <span>Your account holds no Boston Startup Tracker role.</span>
    </div>

    <div class="progress" ng-if="c.loading">
      <div class="progress-bar progress-bar-striped active" role="progressbar"></div>
    </div>

    <div class="alert alert-info" ng-if="data.authorised &amp;&amp; !c.loading &amp;&amp; data.result.length === 0">
      <span>No startup matches those criteria.</span>
    </div>

    <div class="panel panel-default bst-results-card"
         ng-repeat="item in data.result track by item.sys_id">
      <div class="panel-body">
        <div class="media">
          <div class="media-left" ng-if="::options.show_logo &amp;&amp; item.logo_url">
            <img class="media-object" ng-src="{{::item.logo_url}}" alt="" />
          </div>
          <div class="media-body">
            <h4 class="media-heading">
              <a href="?id={{::options.detail_page}}&amp;sys_id={{::item.sys_id}}">{{::item.name}}</a>
            </h4>
            <p>{{::item.description}}</p>
            <p>
              <span class="label label-primary" ng-if="::item.funding_stage">{{::item.funding_stage}}</span>
              <span class="label label-default" ng-if="::item.industry">{{::item.industry}}</span>
              <span class="label label-default" ng-if="::item.employee_count_range">{{::item.employee_count_range}}</span>
            </p>
            <ul class="list-group">
              <li class="list-group-item">
                <span class="icon-map">&nbsp;</span>{{::item.headquarters_location}}
              </li>
              <li class="list-group-item" ng-if="item.total_funding_usd !== undefined">
                Total funding {{item.total_funding_usd}}
              </li>
            </ul>
            <a class="btn btn-default"
               href="?id={{::options.detail_page}}&amp;sys_id={{::item.sys_id}}">View profile</a>
          </div>
        </div>
      </div>
    </div>

    <div class="bst-results-pager" ng-if="data.authorised">
      <button type="button" class="btn btn-default" ng-click="c.previous()"
              ng-disabled="!c.hasPrevious()">Previous</button>
      <button type="button" class="btn btn-default" ng-click="c.next()"
              ng-disabled="!c.hasNext()">Next</button>
      <span class="text-muted">
        Showing {{data.offset + 1}} to {{data.offset + data.result.length}} of {{data.total_count}}
      </span>
    </div>
  </div>
</div>
```

`ng-if="item.total_funding_usd !== undefined"` is the omission test. A denied premium field has **no key** on the serialised object, so `undefined` is the correct comparison; do not test for an empty string and do not test for `null`, because a readable-but-empty currency column legitimately serialises as `null`.

#### CSS

```scss
.bst-results {
    margin-bottom: $grid-gutter-width;
}

.bst-results .bst-results-card {
    margin-bottom: $padding-base-vertical;
}

.bst-results .media-object {
    max-height: $navbar-height;
    width: auto;
}

.bst-results .media-body .label {
    margin-right: $padding-base-vertical;
}

.bst-results .bst-results-pager {
    margin-top: $grid-gutter-width;
    border-top-color: $panel-default-border;
}
```

### `bst-company-profile`

| `sp_widget` field | Value |
| --- | --- |
| `name` | `Company profile` |
| `id` | `bst-company-profile` |
| `sys_scope` | `Boston Startup Tracker` |

#### Option schema

| Option | Type | Default | Purpose |
| --- | --- | --- | --- |
| `default_tab` | string | `overview` | Which of the five panes opens first. One of `overview`, `funding`, `people`, `jobs`, `news`. |
| `investor_page` | string | `bst_investor` | The `sp_page.id` an investor link targets. |
| `upsell_page` | string | `bst_account` | Passed straight through to the embedded `bst-premium-upsell`. |
| `jobs_limit` | integer | `25` | Maximum job postings rendered in the Jobs pane. |
| `news_limit` | integer | `10` | Maximum news articles rendered in the News pane. |

#### Server script

1. Construct `new RestResponseBuilder()`. Call `hasAnyAppRole()`; when false set `data.authorised` to `false` and return.
2. Read the record identifier with `$sp.getParameter('sys_id')`. When it is empty, or does not match a 32-character hexadecimal identifier, set `data.notFound` to `true` and return.
3. Open the startup on the secured path and serialise it:

```javascript
var builder = new RestResponseBuilder();
var startup = new GlideRecordSecure('x_bst_startuptrk_startup');
if (!startup.get(sysId)) {
    data.notFound = true;
    return;
}
data.startup = builder.serialize(startup, [
    'name', 'description', 'industry', 'founded_year', 'headquarters_location',
    'website', 'logo_url', 'funding_stage', 'total_funding_usd', 'active',
    'institutional_funding_last_5yrs', 'employee_count_range'
]);
```

4. Load the four child collections, each with its own `GlideRecordSecure` and its own `serialize()` field list, each ordered, and each queried with `addQuery('startup', sysId)`.

| Pane | Table | Fields serialised | Order |
| --- | --- | --- | --- |
| Funding | `x_bst_startuptrk_fundinground` | `startup`, `round_type`, `amount_usd`, `round_date`, `lead_investor`, `valuation_usd`, `source_url` | `round_date` descending |
| People — founders | `x_bst_startuptrk_founder` | `name`, `startup`, `title`, `bio`, `linkedin_url`, `contact_email` | `name` ascending |
| People — executives | `x_bst_startuptrk_executive` | `name`, `startup`, `title`, `bio`, `linkedin_url`, `contact_email` | `name` ascending |
| Jobs | `x_bst_startuptrk_jobposting` | `startup`, `title`, `department`, `location`, `remote_type`, `seniority`, `posted_date`, `url`, `active` | `posted_date` descending, limited to `options.jobs_limit` |
| News | `x_bst_startuptrk_newsarticle` | `startup`, `title`, `source`, `url`, `published_date`, `summary` | `published_date` descending, limited to `options.news_limit` |

5. Assemble `participating_investors` for each funding round **from the join table**, `x_bst_startuptrk_m2m_round_investor`, and never from the derived `x_bst_startuptrk_fundinground.participating_investors` column. Call `new InvestorPortfolioService().participantsForRounds(roundIds)` with the identifiers of the rounds on the page — one batched read for the whole page, not one read per round — and attach the result to each round as `round.participating_investors`.
6. Compute the gate flags the template needs, each by testing the serialised object for the **absence of the key**:

```javascript
data.gated = {
    total_funding_usd: data.startup.total_funding_usd === undefined,
    institutional_funding_last_5yrs: data.startup.institutional_funding_last_5yrs === undefined,
    founder_contact_email: data.founders.some(function (f) { return f.contact_email === undefined; }),
    executive_contact_email: data.executives.some(function (e) { return e.contact_email === undefined; }),
    amount_usd: data.rounds.some(function (r) { return r.amount_usd === undefined; }),
    valuation_usd: data.rounds.some(function (r) { return r.valuation_usd === undefined; })
};
data.anyGated = Object.keys(data.gated).some(function (key) { return data.gated[key]; });
```

7. Embed the upsell partial when anything is gated:

```javascript
if (data.anyGated) {
    data.upsell = $sp.getWidget('bst-premium-upsell', {
        context: 'company',
        gated_fields: 'total_funding_usd,institutional_funding_last_5yrs,amount_usd,valuation_usd,contact_email',
        upsell_page: options.upsell_page,
        heading: 'Premium data is hidden on this profile'
    });
}
```

8. Publish `data.tabs` as the five pane descriptors in order, so the tab strip is data-driven and cannot drift from the pane list: `overview` / **Overview**, `funding` / **Funding**, `people` / **People**, `jobs` / **Jobs**, `news` / **News**.

#### Client controller

1. Initialise `c.activeTab` from `options.default_tab`, falling back to `overview` when the option names no pane.
2. Expose `c.select(tabId)`, which sets `c.activeTab`, and `c.isActive(tabId)`, which drives both the `.active` class on the `<li>` and the `.active` class on the matching `.tab-pane`.
3. Read the record identifier from `$location.search().sys_id` when a client-side refresh is needed, and call `c.server.update()`.
4. Do not fetch data per tab. All five panes arrive in one server round trip.
5. Use `spUtil.recordWatch($scope, 'x_bst_startuptrk_startup', 'sys_id=' + c.data.startup.sys_id)` so an administrator editing the record in the platform sees the profile refresh without a manual reload.

#### HTML template

```html
<div class="bst-company">
  <div class="alert alert-warning" ng-if="!data.authorised">
    <span>Your account holds no Boston Startup Tracker role.</span>
  </div>

  <div class="alert alert-warning" ng-if="data.notFound">
    <span>That company could not be found.</span>
    <a class="btn btn-default" href="?id=bst_home">Back to search</a>
  </div>

  <div ng-if="data.authorised &amp;&amp; !data.notFound">
    <div class="panel panel-default">
      <div class="panel-body">
        <div class="media">
          <div class="media-left" ng-if="::data.startup.logo_url">
            <img class="media-object bst-company-logo" ng-src="{{::data.startup.logo_url}}" alt="" />
          </div>
          <div class="media-body">
            <h2 class="media-heading">{{::data.startup.name}}</h2>
            <p>
              <span class="label label-primary" ng-if="::data.startup.funding_stage">{{::data.startup.funding_stage}}</span>
              <span class="label label-default" ng-if="::data.startup.industry">{{::data.startup.industry}}</span>
            </p>
          </div>
        </div>
      </div>
    </div>

    <sp-widget widget="data.upsell" ng-if="data.upsell"></sp-widget>

    <ul class="nav nav-tabs" role="tablist">
      <li ng-repeat="tab in ::data.tabs" ng-class="{active: c.isActive(tab.id)}" role="presentation">
        <a href ng-click="c.select(tab.id)">{{::tab.label}}</a>
      </li>
    </ul>

    <div class="tab-content">
      <div class="tab-pane" ng-class="{active: c.isActive('overview')}">
        <ul class="list-group">
          <li class="list-group-item">Headquarters <span class="pull-right">{{::data.startup.headquarters_location}}</span></li>
          <li class="list-group-item">Founded <span class="pull-right">{{::data.startup.founded_year}}</span></li>
          <li class="list-group-item">Employees <span class="pull-right">{{::data.startup.employee_count_range}}</span></li>
          <li class="list-group-item">Website <span class="pull-right"><a ng-href="{{::data.startup.website}}">{{::data.startup.website}}</a></span></li>
          <li class="list-group-item" ng-if="data.startup.total_funding_usd !== undefined">
            Total funding <span class="pull-right">{{data.startup.total_funding_usd}}</span>
          </li>
          <li class="list-group-item" ng-if="data.startup.institutional_funding_last_5yrs !== undefined">
            Institutional funding in the last five years
            <span class="pull-right">{{data.startup.institutional_funding_last_5yrs}}</span>
          </li>
        </ul>
        <p>{{::data.startup.description}}</p>
      </div>

      <div class="tab-pane" ng-class="{active: c.isActive('funding')}">
        <div class="table-responsive">
          <table class="table table-striped table-hover">
            <thead>
              <tr>
                <th>Date</th><th>Round</th><th>Amount</th><th>Valuation</th>
                <th>Lead investor</th><th>Participating investors</th><th>Source</th>
              </tr>
            </thead>
            <tbody>
              <tr ng-repeat="round in data.rounds track by round.sys_id">
                <td>{{::round.round_date}}</td>
                <td><span class="label label-primary" ng-if="::round.round_type">{{::round.round_type}}</span></td>
                <td ng-if="round.amount_usd !== undefined">{{round.amount_usd}}</td>
                <td ng-if="round.amount_usd === undefined"><span class="label label-default">Premium</span></td>
                <td ng-if="round.valuation_usd !== undefined">{{round.valuation_usd}}</td>
                <td ng-if="round.valuation_usd === undefined"><span class="label label-default">Premium</span></td>
                <td>
                  <a ng-if="::round.lead_investor"
                     href="?id={{::options.investor_page}}&amp;sys_id={{::round.lead_investor.value}}">{{::round.lead_investor.display_value}}</a>
                </td>
                <td>
                  <a class="label label-default" ng-repeat="investor in ::round.participating_investors"
                     href="?id={{::options.investor_page}}&amp;sys_id={{::investor.value}}">{{::investor.display_value}}</a>
                </td>
                <td><a ng-href="{{::round.source_url}}" ng-if="::round.source_url">Source</a></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="tab-pane" ng-class="{active: c.isActive('people')}">
        <div class="row">
          <div class="col-md-6 col-lg-6">
            <div class="panel panel-default">
              <div class="panel-heading"><h3 class="panel-title">Founders</h3></div>
              <ul class="list-group">
                <li class="list-group-item" ng-repeat="person in data.founders track by person.sys_id">
                  <strong>{{::person.name}}</strong>
                  <span class="label label-default" ng-if="::person.title">{{::person.title}}</span>
                  <p>{{::person.bio}}</p>
                  <a ng-href="{{::person.linkedin_url}}" ng-if="::person.linkedin_url">
                    <span class="icon-user">&nbsp;</span>LinkedIn
                  </a>
                  <span ng-if="person.contact_email !== undefined">{{person.contact_email}}</span>
                  <span class="label label-default" ng-if="person.contact_email === undefined">Premium</span>
                </li>
              </ul>
            </div>
          </div>
          <div class="col-md-6 col-lg-6">
            <div class="panel panel-default">
              <div class="panel-heading"><h3 class="panel-title">Executives</h3></div>
              <ul class="list-group">
                <li class="list-group-item" ng-repeat="person in data.executives track by person.sys_id">
                  <strong>{{::person.name}}</strong>
                  <span class="label label-default" ng-if="::person.title">{{::person.title}}</span>
                  <p>{{::person.bio}}</p>
                  <a ng-href="{{::person.linkedin_url}}" ng-if="::person.linkedin_url">
                    <span class="icon-user">&nbsp;</span>LinkedIn
                  </a>
                  <span ng-if="person.contact_email !== undefined">{{person.contact_email}}</span>
                  <span class="label label-default" ng-if="person.contact_email === undefined">Premium</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      <div class="tab-pane" ng-class="{active: c.isActive('jobs')}">
        <div class="table-responsive">
          <table class="table table-striped table-hover">
            <thead>
              <tr><th>Title</th><th>Department</th><th>Location</th><th>Working pattern</th>
                  <th>Seniority</th><th>Posted</th><th>Open</th></tr>
            </thead>
            <tbody>
              <tr ng-repeat="job in data.jobs track by job.sys_id">
                <td><a ng-href="{{::job.url}}">{{::job.title}}</a></td>
                <td>{{::job.department}}</td>
                <td>{{::job.location}}</td>
                <td><span class="label label-default" ng-if="::job.remote_type">{{::job.remote_type}}</span></td>
                <td>{{::job.seniority}}</td>
                <td>{{::job.posted_date}}</td>
                <td><span class="label label-primary" ng-if="::job.active">Open</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="tab-pane" ng-class="{active: c.isActive('news')}">
        <ul class="list-group">
          <li class="list-group-item" ng-repeat="article in data.news track by article.sys_id">
            <h4 class="list-group-item-heading">
              <a ng-href="{{::article.url}}">{{::article.title}}</a>
            </h4>
            <p class="list-group-item-text">{{::article.summary}}</p>
            <span class="text-muted">{{::article.source}} &middot; {{::article.published_date}}</span>
          </li>
        </ul>
      </div>
    </div>
  </div>
</div>
```

#### CSS

```scss
.bst-company {
    margin-bottom: $grid-gutter-width;
}

.bst-company .nav-tabs {
    margin-bottom: $grid-gutter-width;
}

.bst-company .bst-company-logo {
    max-height: $navbar-height;
    width: auto;
}

.bst-company .label {
    margin-right: $padding-base-vertical;
}

.bst-company .table-responsive {
    margin-bottom: 0;
    border-color: $table-border-color;
}
```

### `bst-investor-profile`

| `sp_widget` field | Value |
| --- | --- |
| `name` | `Investor profile` |
| `id` | `bst-investor-profile` |
| `sys_scope` | `Boston Startup Tracker` |

#### Option schema

| Option | Type | Default | Purpose |
| --- | --- | --- | --- |
| `company_page` | string | `bst_company` | The `sp_page.id` a portfolio row links to. |
| `upsell_page` | string | `bst_account` | Passed through to the embedded `bst-premium-upsell`. |
| `portfolio_limit` | integer | `50` | Maximum portfolio rows rendered. |
| `rounds_limit` | integer | `50` | Maximum rounds rendered in each of the two rounds tables. |

#### Server script

1. Construct `new RestResponseBuilder()`; call `hasAnyAppRole()`; when false set `data.authorised` to `false` and return.
2. Read `$sp.getParameter('sys_id')`, validate the 32-character hexadecimal form, and open `x_bst_startuptrk_investor` with `GlideRecordSecure`. When the record does not resolve, set `data.notFound` to `true` and return.
3. Serialise the investor with `builder.serialize(investor, ['name', 'type', 'focus_areas', 'website', 'aum_usd', 'portfolio_count'])`. `portfolio_count` is a stored, read-only integer maintained by `InvestorPortfolioService`; read it, never recompute it in the widget.
4. Split `focus_areas` on the comma into an array for the `.label` chips. It is a multi-choice column and arrives as a comma-separated string.
5. Build the **rounds led** set: `GlideRecordSecure` on `x_bst_startuptrk_fundinground` with `addQuery('lead_investor', sysId)`, ordered by `round_date` descending, limited to `options.rounds_limit`, serialised with `['startup', 'round_type', 'amount_usd', 'round_date', 'valuation_usd', 'source_url']`.
6. Build the **rounds participated** set: read `x_bst_startuptrk_m2m_round_investor` with `GlideRecordSecure` and `addQuery('investor', sysId)` to collect the `funding_round` identifiers, then read those rounds with `GlideRecordSecure` and `addQuery('sys_id', 'IN', ids)` and serialise them with the same field list. The join table is authoritative for participation; do not read the derived `participating_investors` column.
7. Build the **portfolio** set as the union of the `startup` identifiers reached by the two paths above, de-duplicated, then read those startups with `GlideRecordSecure` and serialise with `['name', 'industry', 'headquarters_location', 'funding_stage', 'total_funding_usd']`, limited to `options.portfolio_limit`. The union-then-count semantics are specified in [`../data-model.md`](../data-model.md); the widget displays `portfolio_count` for the authoritative figure and its own list for the visible rows, and states the limit when the list is truncated.
8. Compute the gate flags by absence of key: `aum_usd` on the investor, and `amount_usd` and `valuation_usd` across both rounds sets. Set `data.anyGated` accordingly.
9. When `data.anyGated` is true, embed the partial:

```javascript
data.upsell = $sp.getWidget('bst-premium-upsell', {
    context: 'investor',
    gated_fields: 'aum_usd,amount_usd,valuation_usd',
    upsell_page: options.upsell_page,
    heading: 'Premium investor data is hidden'
});
```

#### Client controller

1. Expose `c.section` with the value `portfolio` or `rounds`, and `c.show(section)` / `c.isShown(section)` to toggle the two regions of the right-hand column. Both regions are rendered as panels, not as tabs; the tab control is used only on the company profile.
2. Expose `c.hasParticipated()` and `c.hasLed()` so an empty rounds table renders an `.alert.alert-info` rather than an empty `<tbody>`.
3. Use `spUtil.recordWatch($scope, 'x_bst_startuptrk_investor', 'sys_id=' + c.data.investor.sys_id)` so a recalculated `portfolio_count` appears without a reload.
4. Recompute nothing. `portfolio_count` is read, not derived, in the client.

#### HTML template

```html
<div class="bst-investor">
  <div class="alert alert-warning" ng-if="!data.authorised">
    <span>Your account holds no Boston Startup Tracker role.</span>
  </div>

  <div class="alert alert-warning" ng-if="data.notFound">
    <span>That investor could not be found.</span>
    <a class="btn btn-default" href="?id=bst_home">Back to search</a>
  </div>

  <div class="row" ng-if="data.authorised &amp;&amp; !data.notFound">
    <div class="col-md-4 col-lg-4">
      <div class="panel panel-default">
        <div class="panel-heading"><h3 class="panel-title">{{::data.investor.name}}</h3></div>
        <ul class="list-group">
          <li class="list-group-item">Type <span class="pull-right"><span class="label label-primary" ng-if="::data.investor.type">{{::data.investor.type}}</span></span></li>
          <li class="list-group-item">
            Focus areas
            <span class="pull-right">
              <span class="label label-default" ng-repeat="area in ::data.focusAreas">{{::area}}</span>
            </span>
          </li>
          <li class="list-group-item">Portfolio companies <span class="pull-right">{{::data.investor.portfolio_count}}</span></li>
          <li class="list-group-item" ng-if="data.investor.aum_usd !== undefined">
            Assets under management <span class="pull-right">{{data.investor.aum_usd}}</span>
          </li>
          <li class="list-group-item" ng-if="data.investor.aum_usd === undefined">
            Assets under management <span class="pull-right"><span class="label label-default">Premium</span></span>
          </li>
          <li class="list-group-item">Website <span class="pull-right"><a ng-href="{{::data.investor.website}}">{{::data.investor.website}}</a></span></li>
        </ul>
      </div>
      <sp-widget widget="data.upsell" ng-if="data.upsell"></sp-widget>
    </div>

    <div class="col-md-8 col-lg-8">
      <div class="panel panel-default">
        <div class="panel-heading"><h3 class="panel-title">Portfolio</h3></div>
        <div class="panel-body">
          <div class="alert alert-info" ng-if="data.portfolio.length === 0">
            <span>No portfolio company is recorded for this investor.</span>
          </div>
          <div class="table-responsive" ng-if="data.portfolio.length > 0">
            <table class="table table-striped table-hover">
              <thead><tr><th>Company</th><th>Industry</th><th>Headquarters</th><th>Stage</th><th>Total funding</th></tr></thead>
              <tbody>
                <tr ng-repeat="startup in data.portfolio track by startup.sys_id">
                  <td><a href="?id={{::options.company_page}}&amp;sys_id={{::startup.sys_id}}">{{::startup.name}}</a></td>
                  <td>{{::startup.industry}}</td>
                  <td>{{::startup.headquarters_location}}</td>
                  <td><span class="label label-primary" ng-if="::startup.funding_stage">{{::startup.funding_stage}}</span></td>
                  <td ng-if="startup.total_funding_usd !== undefined">{{startup.total_funding_usd}}</td>
                  <td ng-if="startup.total_funding_usd === undefined"><span class="label label-default">Premium</span></td>
                </tr>
              </tbody>
            </table>
          </div>
          <p class="text-muted" ng-if="data.portfolioTruncated">
            Showing the first {{::options.portfolio_limit}} of {{::data.investor.portfolio_count}} portfolio companies.
          </p>
        </div>
      </div>

      <div class="panel panel-default">
        <div class="panel-heading"><h3 class="panel-title">Rounds led</h3></div>
        <div class="panel-body">
          <div class="alert alert-info" ng-if="!c.hasLed()"><span>This investor has led no recorded round.</span></div>
          <div class="table-responsive" ng-if="c.hasLed()">
            <table class="table table-striped table-hover">
              <thead><tr><th>Company</th><th>Date</th><th>Round</th><th>Amount</th><th>Valuation</th></tr></thead>
              <tbody>
                <tr ng-repeat="round in data.roundsLed track by round.sys_id">
                  <td><a href="?id={{::options.company_page}}&amp;sys_id={{::round.startup.value}}">{{::round.startup.display_value}}</a></td>
                  <td>{{::round.round_date}}</td>
                  <td><span class="label label-primary" ng-if="::round.round_type">{{::round.round_type}}</span></td>
                  <td ng-if="round.amount_usd !== undefined">{{round.amount_usd}}</td>
                  <td ng-if="round.amount_usd === undefined"><span class="label label-default">Premium</span></td>
                  <td ng-if="round.valuation_usd !== undefined">{{round.valuation_usd}}</td>
                  <td ng-if="round.valuation_usd === undefined"><span class="label label-default">Premium</span></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div class="panel panel-default">
        <div class="panel-heading"><h3 class="panel-title">Rounds participated in</h3></div>
        <div class="panel-body">
          <div class="alert alert-info" ng-if="!c.hasParticipated()"><span>This investor has participated in no recorded round.</span></div>
          <div class="table-responsive" ng-if="c.hasParticipated()">
            <table class="table table-striped table-hover">
              <thead><tr><th>Company</th><th>Date</th><th>Round</th><th>Amount</th><th>Valuation</th></tr></thead>
              <tbody>
                <tr ng-repeat="round in data.roundsParticipated track by round.sys_id">
                  <td><a href="?id={{::options.company_page}}&amp;sys_id={{::round.startup.value}}">{{::round.startup.display_value}}</a></td>
                  <td>{{::round.round_date}}</td>
                  <td><span class="label label-primary" ng-if="::round.round_type">{{::round.round_type}}</span></td>
                  <td ng-if="round.amount_usd !== undefined">{{round.amount_usd}}</td>
                  <td ng-if="round.amount_usd === undefined"><span class="label label-default">Premium</span></td>
                  <td ng-if="round.valuation_usd !== undefined">{{round.valuation_usd}}</td>
                  <td ng-if="round.valuation_usd === undefined"><span class="label label-default">Premium</span></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
```

#### CSS

```scss
.bst-investor {
    margin-bottom: $grid-gutter-width;
}

.bst-investor .panel {
    margin-bottom: $grid-gutter-width;
}

.bst-investor .list-group-item .label {
    margin-left: $padding-base-vertical;
}

.bst-investor .table-responsive {
    margin-bottom: 0;
    border-color: $table-border-color;
}
```

### `bst-trends-kpi`

| `sp_widget` field | Value |
| --- | --- |
| `name` | `Trends KPIs` |
| `id` | `bst-trends-kpi` |
| `sys_scope` | `Boston Startup Tracker` |

#### Option schema

| Option | Type | Default | Purpose |
| --- | --- | --- | --- |
| `title` | string | `At a glance` | The heading above the KPI row. |
| `show_jobs` | boolean | `true` | Renders the open-job-postings KPI panel. |
| `show_news` | boolean | `true` | Renders the news-articles KPI panel. |

#### Server script

1. Construct `new RestResponseBuilder()`; call `hasAnyAppRole()`; when false set `data.authorised` to `false` and return.
2. Produce every figure with `RestResponseBuilder.countWith(table, applyConditions)`, which counts on the secured read path under a bound. **Do not use an aggregate query.** An aggregate does not apply access controls, so it is not a permitted caller-facing read anywhere in this application; the rule is stated in [`../access-control.md`](../access-control.md).
3. Apply the inclusion criteria to the startup figure through the shared service, so the dashboard and the search results agree:

```javascript
var builder = new RestResponseBuilder();
var search = new StartupSearchService();
var plan = search.buildPlan(null, search.appliesInclusion());

data.kpis = [];
data.kpis.push({
    id: 'startups',
    label: 'Startups in scope',
    glyph: 'icon-book',
    value: builder.countWith('x_bst_startuptrk_startup', function (query) {
        search.applyPlan(query, plan);
    }),
    link: '?id=bst_home'
});
data.kpis.push({
    id: 'rounds', label: 'Funding rounds', glyph: 'icon-chart',
    value: builder.countWith('x_bst_startuptrk_fundinground', null), link: ''
});
data.kpis.push({
    id: 'investors', label: 'Investors', glyph: 'icon-user',
    value: builder.countWith('x_bst_startuptrk_investor', null), link: ''
});
if (options.show_jobs) {
    data.kpis.push({
        id: 'jobs', label: 'Open roles', glyph: 'icon-catalog',
        value: builder.countWith('x_bst_startuptrk_jobposting', function (query) {
            query.addQuery('active', true);
        }),
        link: ''
    });
}
if (options.show_news) {
    data.kpis.push({
        id: 'news', label: 'News articles', glyph: 'icon-document',
        value: builder.countWith('x_bst_startuptrk_newsarticle', null), link: ''
    });
}
```

4. Publish no currency figure. A sum over `total_funding_usd`, `amount_usd` or `valuation_usd` would require an aggregate, which is not permitted, and those three columns are premium-gated. **No KPI panel in this widget reports a monetary total.**

#### Client controller

1. Compute `c.columns()` as the Bootstrap column span for one panel from `c.data.kpis.length`, choosing from `col-md-6`, `col-md-4` and `col-md-3` only, so the row always totals twelve and never uses a narrower class.
2. Expose `c.hasLink(kpi)` for the conditional `.btn.btn-link`.
3. Read no data and issue no server call after the first render. The KPI figures are computed once, in the server script.

#### HTML template

```html
<div class="bst-kpi">
  <h2>{{::options.title}}</h2>

  <div class="alert alert-warning" ng-if="!data.authorised">
    <span>Your account holds no Boston Startup Tracker role.</span>
  </div>

  <div class="row" ng-if="data.authorised">
    <div ng-class="c.columns()" ng-repeat="kpi in ::data.kpis track by kpi.id">
      <div class="panel panel-default bst-kpi-panel">
        <div class="panel-heading">
          <h3 class="panel-title">
            <span class="{{::kpi.glyph}}" aria-hidden="true">&nbsp;</span>{{::kpi.label}}
          </h3>
        </div>
        <div class="panel-body">
          <h2 class="bst-kpi-value">{{::kpi.value}}</h2>
          <a class="btn btn-link" ng-if="c.hasLink(kpi)" ng-href="{{::kpi.link}}">Browse startups</a>
        </div>
      </div>
    </div>
  </div>
</div>
```

The figure is rendered inside an `<h2>` so the Bootstrap heading scale supplies the size. No font-size declaration appears in this widget's CSS.

#### CSS

```scss
.bst-kpi {
    margin-bottom: $grid-gutter-width;
}

.bst-kpi .bst-kpi-panel {
    margin-bottom: $grid-gutter-width;
    border-color: $panel-default-border;
}

.bst-kpi .bst-kpi-value {
    margin-top: 0;
    margin-bottom: 0;
    font-family: $headings-font-family;
    font-weight: $headings-font-weight;
    color: $brand-primary;
}
```

### `bst-trends-charts`

| `sp_widget` field | Value |
| --- | --- |
| `name` | `Trends charts` |
| `id` | `bst-trends-charts` |
| `sys_scope` | `Boston Startup Tracker` |

**Design-system gap G1.** Bootstrap 3 has no chart component. The resolution is platform reporting surfaced through a report or chart widget, or Angular-rendered inline SVG inside this custom widget. Both mechanics are specified below and are selected by the `render_mode` option. The gap is recorded in [`../gaps-and-flags.md`](../gaps-and-flags.md).

#### Option schema

| Option | Type | Default | Purpose |
| --- | --- | --- | --- |
| `title` | string | `Startups by funding stage` | The `.panel-title` text. |
| `dimension` | string | `funding_stage` | The `x_bst_startuptrk_startup` choice column to bucket on. One of `funding_stage`, `industry`, `employee_count_range`. |
| `render_mode` | string | `svg` | `svg` renders the inline SVG bar chart in this widget. `report` embeds a saved report instead; see below. |
| `report_id` | string | *empty* | The `sys_report.sys_id` used when `render_mode` is `report`. Ignored when `render_mode` is `svg`. |

#### Server script

1. Construct `new RestResponseBuilder()`; call `hasAnyAppRole()`; when false set `data.authorised` to `false` and return.
2. Resolve `options.dimension` against the closed set `funding_stage`, `industry`, `employee_count_range`. Any other value falls back to `funding_stage`. Publish the resolved value as `data.dimension`.
3. Publish the bucket labels from the **closed choice list of the resolved column**, transcribed from [`../data-model.md`](../data-model.md) and matching the `sys_choice` records the Update Set delivers:

| `data.dimension` | Bucket labels, in this order |
| --- | --- |
| `funding_stage` | `Pre-Seed`, `Seed`, `Series A`, `Series B`, `Series C+`, `Growth`, `Public`, `Acquired` |
| `industry` | `Fintech`, `Healthtech`, `SaaS`, `Consumer`, `Deeptech`, `Other` |
| `employee_count_range` | `1-10`, `11-50`, `51-200`, `201-500`, `500+` |

4. Count each bucket with `countWith`, applying the shared inclusion plan **and** the bucket condition, so every chart agrees with the search results and the KPI row:

```javascript
var builder = new RestResponseBuilder();
var search = new StartupSearchService();
var plan = search.buildPlan(null, search.appliesInclusion());

var buckets = [];
var largest = 0;
data.labels.forEach(function (label) {
    var count = builder.countWith('x_bst_startuptrk_startup', function (query) {
        search.applyPlan(query, plan);
        query.addQuery(data.dimension, label);
    });
    if (count > largest) {
        largest = count;
    }
    buckets.push({ label: label, count: count });
});
```

5. Compute the SVG geometry on the **server**, from the counts, so no numeric literal is written into the template or the CSS. For each bucket publish `share`, the count divided by `largest` and expressed as a whole-number percentage — `0` when `largest` is `0`. Publish `data.buckets` and `data.largest`.
6. When `render_mode` is `report`, publish `data.report = $sp.getWidget('report-chart', { sys_id: options.report_id })` and publish no bucket geometry. The embedded stock report widget then renders the chart, and the saved report must live in the `x_bst_startuptrk` scope and read one of the application's tables.
7. Produce no figure with an aggregate query, for the reason stated under `bst-trends-kpi`.

#### Client controller

1. Expose `c.isSvg()` and `c.isReport()` from `options.render_mode`.
2. Expose `c.barStyle(bucket)`, returning `{ width: bucket.share + '%' }` for the `.progress-bar` fallback row, and `c.hasData()`, true when `data.largest` is greater than zero.
3. Perform no arithmetic on record data beyond that. Every count arrives from the server.
4. Bind SVG geometry with `ng-attr-width` and `ng-attr-y` against the server-computed values. Do not compute pixel positions in the controller.

#### HTML template

```html
<div class="bst-charts panel panel-default">
  <div class="panel-heading">
    <h3 class="panel-title">
      <span class="icon-chart" aria-hidden="true">&nbsp;</span>{{::options.title}}
    </h3>
  </div>
  <div class="panel-body">
    <div class="alert alert-warning" ng-if="!data.authorised">
      <span>Your account holds no Boston Startup Tracker role.</span>
    </div>

    <div class="alert alert-info" ng-if="data.authorised &amp;&amp; c.isSvg() &amp;&amp; !c.hasData()">
      <span>No startup is recorded for this breakdown yet.</span>
    </div>

    <table class="table table-striped bst-charts-table"
           ng-if="data.authorised &amp;&amp; c.isSvg() &amp;&amp; c.hasData()">
      <tbody>
        <tr ng-repeat="bucket in ::data.buckets track by bucket.label">
          <th scope="row">{{::bucket.label}}</th>
          <td class="bst-charts-bar">
            <div class="progress">
              <div class="progress-bar" role="progressbar" ng-style="c.barStyle(bucket)"></div>
            </div>
          </td>
          <td><span class="label label-default">{{::bucket.count}}</span></td>
        </tr>
      </tbody>
    </table>

    <sp-widget widget="data.report" ng-if="c.isReport() &amp;&amp; data.report"></sp-widget>
  </div>
</div>
```

The bar itself is a Bootstrap `.progress` / `.progress-bar` pair, so the bar geometry is a system component and the only computed value is the width percentage the server supplied. Where the inline-SVG form is preferred instead of `.progress`, render a single `<svg>` per widget with one `<rect>` per bucket, bind every `width`, `y` and `height` attribute with `ng-attr-*` to a server-computed value, and set `fill="currentColor"` so the bar colour is inherited from the CSS `color` property rather than written as a literal.

#### CSS

```scss
.bst-charts {
    margin-bottom: $grid-gutter-width;
}

.bst-charts .bst-charts-table {
    margin-bottom: 0;
    border-color: $table-border-color;
}

.bst-charts .bst-charts-bar {
    color: $brand-primary;
    width: auto;
}

.bst-charts .bst-charts-bar .progress {
    margin-bottom: 0;
    background-color: $table-bg;
}

.bst-charts .bst-charts-bar .progress-bar {
    background-color: currentColor;
}
```

### `bst-account-summary`

| `sp_widget` field | Value |
| --- | --- |
| `name` | `Account summary` |
| `id` | `bst-account-summary` |
| `sys_scope` | `Boston Startup Tracker` |

#### Option schema

| Option | Type | Default | Purpose |
| --- | --- | --- | --- |
| `title` | string | `Your account` | The `.panel-title` text. |
| `show_entitlements` | boolean | `true` | Renders the entitlements list group. |
| `upsell_page` | string | `bst_account` | Passed through to the embedded `bst-premium-upsell`. |

#### Server script

1. Publish the caller's identity from the platform session, not from any application table: `data.user = { name: gs.getUserDisplayName(), user_name: gs.getUserName() }`. **The application declares no identity table**; identity is a platform concern, as [`../access-control.md`](../access-control.md) records.
2. Test each of the three scoped roles and publish the results individually:

```javascript
data.roles = {
    admin: gs.hasRole('x_bst_startuptrk.admin'),
    premium_user: gs.hasRole('x_bst_startuptrk.premium_user'),
    user: gs.hasRole('x_bst_startuptrk.user')
};
data.authorised = new RestResponseBuilder().hasAnyAppRole();
```

3. Resolve the **effective role**, the most capable role held, and publish it as `data.effectiveRole` with one of the four values `x_bst_startuptrk.admin`, `x_bst_startuptrk.premium_user`, `x_bst_startuptrk.user` or `none`.
4. Publish `data.entitlements` as one row per capability, each with a label and a boolean, derived from `data.roles` and matching the capability column of [`../access-control.md`](../access-control.md):

| Entitlement label | True when |
| --- | --- |
| Read the seven entity tables | any of the three roles is held |
| Read the seven premium fields | `x_bst_startuptrk.admin` or `x_bst_startuptrk.premium_user` |
| Call the thirteen read REST operations | any of the three roles is held |
| Call the eighteen write REST operations | `x_bst_startuptrk.admin` |
| Create, update and delete records | `x_bst_startuptrk.admin` |
| Read the ingestion staging table and the rate-limit counters | `x_bst_startuptrk.admin` |

5. Publish `data.premiumDenied`, true when the caller holds neither `x_bst_startuptrk.admin` nor `x_bst_startuptrk.premium_user`. Embed the partial when it is true:

```javascript
if (data.premiumDenied) {
    data.upsell = $sp.getWidget('bst-premium-upsell', {
        context: 'account',
        gated_fields: 'total_funding_usd,institutional_funding_last_5yrs,contact_email,aum_usd,amount_usd,valuation_usd',
        upsell_page: options.upsell_page,
        heading: 'Upgrade to read premium fields'
    });
}
```

6. Read **no** application record. This widget reports entitlements, not data.
7. Publish nothing about billing, payment, price or checkout. The platform grants entitlement through roles and has no commerce capability; the requirement is flagged as **G6** in [`../gaps-and-flags.md`](../gaps-and-flags.md), and the operational path is an administrator granting `x_bst_startuptrk.premium_user` on the instance.

#### Client controller

1. Expose `c.roleLabel()`, mapping `data.effectiveRole` to a human label, and `c.isDenied()` from `data.premiumDenied`.
2. Expose `c.notifyRequest()`, which calls `spUtil.addInfoMessage('Your request has been noted. An administrator grants the premium role on the instance.')` when the caller activates the upgrade prompt from this page. It performs no write.
3. Issue no server call after the first render.

#### HTML template

```html
<div class="bst-account">
  <div class="panel panel-default">
    <div class="panel-heading">
      <h3 class="panel-title">
        <span class="icon-user" aria-hidden="true">&nbsp;</span>{{::options.title}}
      </h3>
    </div>
    <ul class="list-group">
      <li class="list-group-item">Signed in as <span class="pull-right">{{::data.user.name}}</span></li>
      <li class="list-group-item">User name <span class="pull-right">{{::data.user.user_name}}</span></li>
      <li class="list-group-item">
        Effective role
        <span class="pull-right">
          <span class="label label-primary" ng-if="data.authorised">{{::data.effectiveRole}}</span>
          <span class="label label-default" ng-if="!data.authorised">none</span>
        </span>
      </li>
    </ul>
  </div>

  <div class="alert alert-warning" ng-if="!data.authorised">
    <span>Your account holds none of the three Boston Startup Tracker roles. An administrator grants one on the instance.</span>
  </div>

  <div class="panel panel-default" ng-if="::options.show_entitlements">
    <div class="panel-heading"><h3 class="panel-title">Entitlements</h3></div>
    <ul class="list-group">
      <li class="list-group-item" ng-repeat="row in ::data.entitlements track by row.label">
        {{::row.label}}
        <span class="pull-right">
          <span class="label label-primary" ng-if="::row.granted">Granted</span>
          <span class="label label-default" ng-if="::!row.granted">Not granted</span>
        </span>
      </li>
    </ul>
  </div>

  <sp-widget widget="data.upsell" ng-if="data.upsell"></sp-widget>

  <a class="btn btn-default" href="?id=bst_home">Back to search</a>
</div>
```

#### CSS

```scss
.bst-account {
    margin-bottom: $grid-gutter-width;
}

.bst-account .panel {
    margin-bottom: $grid-gutter-width;
}

.bst-account .list-group-item .label {
    margin-left: $padding-base-vertical;
}
```

### `bst-premium-upsell`

| `sp_widget` field | Value |
| --- | --- |
| `name` | `Premium upsell` |
| `id` | `bst-premium-upsell` |
| `sys_scope` | `Boston Startup Tracker` |

**The reusable partial.** It is embedded by **three** hosts — `bst-company-profile`, `bst-investor-profile` and `bst-account-summary` — and is placed on no page. Its option schema must therefore satisfy all three. It resolves design-system gap **G5**, recorded in [`../gaps-and-flags.md`](../gaps-and-flags.md): no library component exists for a paywall treatment, so it is built as a Bootstrap alert carrying a call to action.

#### Option schema

| Option | Type | Default | Purpose |
| --- | --- | --- | --- |
| `context` | string | `company` | Which host embedded it. One of `company`, `investor`, `account`. Selects the body wording. |
| `gated_fields` | string | *empty* | Comma-separated column names hidden in this host, used to render the "what you are missing" list. Values are column names only, never values. |
| `upsell_page` | string | `bst_account` | The `sp_page.id` the call to action targets. |
| `heading` | string | `Premium data is hidden` | The alert heading. |

Every option is supplied by the host; none is read from a URL parameter, and none is set on an `sp_instance` record, because this widget has no instance of its own.

#### Options each host passes

| Option | `bst-company-profile` passes | `bst-investor-profile` passes | `bst-account-summary` passes |
| --- | --- | --- | --- |
| `context` | `company` | `investor` | `account` |
| `gated_fields` | `total_funding_usd,institutional_funding_last_5yrs,amount_usd,valuation_usd,contact_email` | `aum_usd,amount_usd,valuation_usd` | `total_funding_usd,institutional_funding_last_5yrs,contact_email,aum_usd,amount_usd,valuation_usd` |
| `upsell_page` | `options.upsell_page` of the host instance, `bst_account` | `options.upsell_page` of the host instance, `bst_account` | `options.upsell_page` of the host instance, `bst_account` |
| `heading` | `Premium data is hidden on this profile` | `Premium investor data is hidden` | `Upgrade to read premium fields` |

Each host embeds it **only** when at least one key was omitted from its own serialised data, or — on the account summary — when the caller holds neither `x_bst_startuptrk.admin` nor `x_bst_startuptrk.premium_user`.

#### Server script

1. Read `options.context`, `options.gated_fields`, `options.upsell_page` and `options.heading`. Apply the defaults above for any that arrive empty.
2. Split `options.gated_fields` on the comma, trim each entry, discard empties, and map each to a human label. Publish the result as `data.fields`. The permitted entries and their labels are exactly these seven, and nothing else is accepted:

| Column name | Label |
| --- | --- |
| `total_funding_usd` | Total funding |
| `institutional_funding_last_5yrs` | Institutional funding in the last five years |
| `contact_email` | Founder and executive contact email |
| `aum_usd` | Assets under management |
| `amount_usd` | Round amount |
| `valuation_usd` | Round valuation |
| `portfolio_count` | *Not accepted. `portfolio_count` is not premium-gated.* |

3. Publish `data.body`, selected from `options.context`: `company` gives the company-profile wording, `investor` the investor wording, `account` the account wording.
4. Publish `data.callToActionLabel` — `See your entitlements` for `company` and `investor`, `Request the premium role` for `account` — and `data.upsellPage` from `options.upsell_page`.
5. Read **no** record and reference **no** field value. This widget renders column names and static wording only. It must never receive, hold or render a gated value; a partial that carried the value it exists to hide would defeat the field-level access controls entirely.

#### Client controller

1. Expose `c.isAccount()` from `options.context`, so the account host renders the request prompt rather than a navigation link to itself.
2. Expose `c.request()`, which calls `spUtil.addInfoMessage()` with the same message as `bst-account-summary` and performs no write. Bind it only when `c.isAccount()` is true.
3. Issue no server call. This widget is stateless after its first render.

#### HTML template

```html
<div class="bst-upsell alert alert-info" role="alert">
  <h4>
    <span class="icon-locked" aria-hidden="true">&nbsp;</span>{{::options.heading}}
  </h4>
  <p>{{::data.body}}</p>
  <ul class="list-unstyled bst-upsell-fields" ng-if="::data.fields.length > 0">
    <li ng-repeat="field in ::data.fields track by field.name">
      <span class="label label-default">{{::field.label}}</span>
    </li>
  </ul>
  <a class="btn btn-primary" ng-if="::!c.isAccount()" href="?id={{::data.upsellPage}}">
    {{::data.callToActionLabel}}
  </a>
  <button type="button" class="btn btn-primary" ng-if="::c.isAccount()" ng-click="c.request()">
    {{::data.callToActionLabel}}
  </button>
</div>
```

#### CSS

```scss
.bst-upsell {
    margin-bottom: $grid-gutter-width;
    border-radius: $border-radius-base;
}

.bst-upsell .bst-upsell-fields {
    margin-top: $padding-base-vertical;
    margin-bottom: $padding-base-vertical;
}

.bst-upsell .bst-upsell-fields .label {
    margin-right: $padding-base-vertical;
}
```

### Widget roll-up

| # | Widget name and ID | Options | Placed on | Embeds |
| --- | --- | --- | --- | --- |
| 1 | `bst-startup-search` | `title`, `show_industry`, `show_location`, `results_page` | `bst_home` | — |
| 2 | `bst-startup-results` | `title`, `page_size`, `detail_page`, `show_logo` | `bst_home` | — |
| 3 | `bst-company-profile` | `default_tab`, `investor_page`, `upsell_page`, `jobs_limit`, `news_limit` | `bst_company` | `bst-premium-upsell` |
| 4 | `bst-investor-profile` | `company_page`, `upsell_page`, `portfolio_limit`, `rounds_limit` | `bst_investor` | `bst-premium-upsell` |
| 5 | `bst-trends-kpi` | `title`, `show_jobs`, `show_news` | `bst_dashboard` | — |
| 6 | `bst-trends-charts` | `title`, `dimension`, `render_mode`, `report_id` | `bst_dashboard`, two instances | the stock report widget when `render_mode` is `report` |
| 7 | `bst-account-summary` | `title`, `show_entitlements`, `upsell_page` | `bst_account` | `bst-premium-upsell` |
| 8 | `bst-premium-upsell` | `context`, `gated_fields`, `upsell_page`, `heading` | none — embedded only | — |

### The Angular surface available inside a widget

The framework inside a Service Portal widget is AngularJS 1.x with Bootstrap 3.3.6. The surface below is the whole of what these eight widgets use.

#### Template directives

| Directive | Use in this portal |
| --- | --- |
| `ng-repeat` | Every collection: result cards, table rows, list-group items, KPI panels, tab items, chart buckets, upsell field labels. Always with `track by <item>.sys_id` where the item is a record, and `track by <item>.label` or `.id` where it is not. |
| `ng-if` | Every conditional region, including **every premium-field omission test**. Prefer it over `ng-show`, so a denied field's markup is never present in the document. |
| `ng-model` | The three filter inputs of `bst-startup-search`. |
| `ng-class` | The `.active` class on `.nav-tabs` items and `.tab-pane` panes, and the computed column class in `bst-trends-kpi`. |
| `ng-click` | Tab selection, pager buttons, the clear button, the account request button. |
| `ng-href` / `ng-src` | Every interpolated link and image source, so a partially interpolated value is never requested. |
| `ng-style` | The `.progress-bar` width in `bst-trends-charts`, bound to a server-computed percentage. |
| `ng-disabled` | The pager buttons of `bst-startup-results`. |
| `ng-attr-*` | SVG geometry attributes, when the inline-SVG chart form is used. |
| `sp-widget` | Rendering an embedded widget model: `<sp-widget widget="data.upsell">`. |

The one-time binding form `{{::value}}` is used for every value that does not change after the first render, which is most of them. A value that participates in an omission test is bound **without** the one-time prefix where the containing region can be re-rendered by a server refresh.

#### `spUtil`, the client service

| Member | Use in this portal |
| --- | --- |
| `spUtil.get(widgetId, data)` | Fetching an additional widget model on the client. Used only when a widget must load a partial after its first render; the three hosts here embed the upsell on the **server** with `$sp.getWidget()` instead, because the embed decision depends on an access-control outcome that must be evaluated server-side. |
| `spUtil.recordWatch($scope, table, filter)` | `bst-company-profile` on `x_bst_startuptrk_startup`, and `bst-investor-profile` on `x_bst_startuptrk_investor`, so an administrator's edit and a recalculated `portfolio_count` appear without a manual reload. |
| `spUtil.addInfoMessage(message)` | `bst-account-summary` and `bst-premium-upsell`, for the premium-role request acknowledgement. |
| `spUtil.update($scope)` | An alternative to `$scope.server.update()` where the whole widget model is to be replaced. Either form is acceptable; `$scope.server.update()` is used above because it sends `$scope.data` as the server script's `input`. |

#### `$sp`, the server-side API

| Member | Use in this portal |
| --- | --- |
| `$sp.getParameter(name)` | Reading `sys_id`, `name`, `industry`, `location` and `offset` from the URL in a server script. |
| `$sp.getWidget(widgetId, options)` | Embedding `bst-premium-upsell` from its three hosts, and embedding the stock report widget from `bst-trends-charts`. |
| `$sp.getDisplayValue(fieldName)` | Permitted for a **non-premium display column only** — `x_bst_startuptrk_startup.name`, `x_bst_startuptrk_jobposting.title`, `x_bst_startuptrk_newsarticle.title` — for example when setting a page heading. |
| `$sp.getRecordValues(data, record, fieldList)` | **Available but not used in this portal, and not to be used on any table carrying a premium column.** It copies each field's value onto `data` without an element-level read check, so a denied premium column is copied as the empty string the secured read returns — which is the nulled behaviour the requirements forbid. `RestResponseBuilder.serialize()` is the only permitted way to put record data into `data`. See [Omitted, not nulled](#omitted-not-nulled). |

#### `spModal`

| Member | Use in this portal |
| --- | --- |
| `spModal.open(options)` | Opening a Bootstrap `.modal` carrying a widget — for example the stock **Form** widget for an administrative edit from within the portal. |
| `spModal.alert(message)` | A blocking acknowledgement. |
| `spModal.confirm(message)` | Confirming a destructive administrative action before it is sent. No non-administrative path in this portal writes, so no confirmation is required outside an administrative edit. |

#### `$location`

`$location` reads and writes the query string of the current portal route.

| Call | Use in this portal |
| --- | --- |
| `$location.search()` | Reading the whole parameter object — `$location.search().sys_id` on the company and investor profiles. |
| `$location.search(name, value)` | Writing one parameter — `bst-startup-search` mirroring each filter so the search is linkable. |
| `$location.search(object)` | Writing the whole filter set in one call. |

Never assemble a portal URL by string concatenation in a controller, and never write the `bst` suffix into a widget. A template link is relative — `?id=bst_company&sys_id={{item.sys_id}}` — and `$location` handles the rest.

## Step 5 — The design-system contract

This is a checklist. Every widget author satisfies every item before a widget is saved.

### The design system

- [ ] The design system is the **ServiceNow Service Portal framework — AngularJS 1.x with Bootstrap 3.3.6**, which Service Portal uses as its foundational stylesheet.
- [ ] It is **platform-native and already present** on the instance. **Nothing is installed.**
- [ ] It is neither an npm nor a PyPI package and has no registry identity, so **no repository manifest changes** are made. No `package.json`, `requirements.txt`, `pyproject.toml` or lock file is created or edited for this portal.
- [ ] Its version is bound to the platform release, not pinned from the repository.
- [ ] The `@material-ui/core` and `@material-ui/icons` entries at `package.json:L15-L16` are **left untouched**. The legacy manifest is reference-mode.

### Zero hard-coded values

- [ ] Every colour, spacing, radius and font value in widget CSS resolves to a Bootstrap 3.3.6 or `$sp-*` SASS variable declared in the theme's CSS-variables field.
- [ ] The **only** permitted literals in widget CSS are `0`, `none`, `auto`, `inherit`, `currentColor` and `transparent`.
- [ ] No hex colour, `rgb()`, `rgba()`, `hsl()`, pixel, point, em, rem or percentage literal appears in any widget CSS. A percentage that varies with data is bound with `ng-style` from a server-computed value, never written as a literal.
- [ ] No `font-size` declaration appears in any widget CSS. Type size comes from the Bootstrap heading elements and utility classes.
- [ ] No `!important` appears in any widget CSS.
- [ ] The theme's CSS-variables field is the single site where a value is written. Every other literal is a defect.

### Library components over raw HTML

- [ ] `.btn` — with `.btn-primary`, `.btn-default` or `.btn-link` — rather than a styled `<div>` or an unclassed `<button>`.
- [ ] `.form-control` inside a `.form-group`, and `.input-group` with `.input-group-btn` where a button sits against the field, rather than a bare `<input>`.
- [ ] `.nav.nav-tabs` with `.tab-content` and `.tab-pane` rather than a hand-rolled tab control.
- [ ] `.table.table-striped.table-hover` inside `.table-responsive` rather than an unclassed `<table>`.
- [ ] `.panel.panel-default` with `.panel-heading`, `.panel-title` and `.panel-body` rather than a bare container.
- [ ] `.list-group` with `.list-group-item` for key-and-value detail lists.
- [ ] `.label.label-primary` and `.label.label-default` for status, category and multi-valued chips.
- [ ] `.media` with `.media-left`, `.media-body` and `.media-heading` for a result card.
- [ ] `.alert` with `.alert-info`, `.alert-warning` or `.alert-danger` for every notice.
- [ ] `.breadcrumb`, rendered by the stock Breadcrumbs widget, for the trail.
- [ ] The stock **Data Table from Instance Definition** widget wherever a plain paginated record list suffices, rather than a bespoke widget.

### Layout through system primitives only

- [ ] Page composition uses the `sp_container` → `sp_row` → `sp_rectangle` → `sp_instance` model and nothing else.
- [ ] Layout inside a widget uses `.container`, `.row` and `.col-md-*` / `.col-lg-*`.
- [ ] The column spans in any one row total 12.
- [ ] **Never** apply a custom `display: flex`, `display: grid`, `float` or absolute-position rule to a raw `<div>` to achieve a layout the grid already provides.

### Responsive stance — the 1024-pixel floor

- [ ] **1024 pixels is the supported viewport floor of this portal.** Viewports below it are out of scope.
- [ ] Use **medium and large column classes only**: `.col-md-*` and `.col-lg-*`.
- [ ] Author **no** extra-small or small refinement: no `.col-xs-*`, no `.col-sm-*`, no `.hidden-xs`, no `.visible-sm-*`, and no media query keyed to `$screen-xs-min` or `$screen-sm-min`.
- [ ] On every `sp_rectangle`, set `size_md` and `size_lg` and leave `size`, `size_xs` and `size_sm` empty.
- [ ] Verify the walkthrough at 1024 pixels wide and above. A narrower viewport is not a defect.

The mechanic is stated here; the decision behind the floor is recorded in [`../../../docs/decisions/DECISION_LOG.md`](../../../docs/decisions/DECISION_LOG.md).

### The graceful degradation ladder

For each interface element, stop at the **first** viable rung.

| Rung | Action |
| --- | --- |
| 1 | Use an exact stock widget directly — Header, Footer, Breadcrumbs, Typeahead Search, Faceted Search, Data Table from Instance Definition, Form, report widget. |
| 2 | Use a Bootstrap 3 component with class adjustments, and annotate the adjustment in the widget's `docs` field. |
| 3 | Use a generic `.panel` or `.well` container styled with system tokens only. |
| 4 | Render a placeholder carrying an explicit gap flag, and add the gap to [`../gaps-and-flags.md`](../gaps-and-flags.md) as requiring design-system follow-up. |

No element in this portal reaches rung 4.

### Iconography — the platform glyph font only

- [ ] Icons come from the **platform glyph font** and from nothing else: `.icon-search`, `.icon-user`, `.icon-chart`, and the further `.icon-*` classes the release provides.
- [ ] **NEVER Lucide.** Do not add a Lucide script tag, a Lucide stylesheet, a `data-lucide` attribute or a Lucide SVG to any widget template, client controller, CSS field or theme field.
- [ ] **Zero emoji.** No emoji character appears in any widget template, option label, option default, alert wording, page title or CSS comment.
- [ ] The executive deck uses Lucide 0.460.0 by rule mandate, and this portal uses the platform glyph font. **The split is deliberate and permanent, and it is recorded as gap G7** in [`../gaps-and-flags.md`](../gaps-and-flags.md).
- [ ] The instruction runs both ways: **do not inject Lucide into a widget, and do not use platform glyphs in the deck.**

### Resolved design-system gaps

Each gap below is resolved inside the system. The full inventory is in [`../gaps-and-flags.md`](../gaps-and-flags.md) and is not restated here.

| Gap | Element | Resolution to build |
| --- | --- | --- |
| **G1** | Charts on the Dashboard / Trends route | Platform reporting surfaced through a report or chart widget, or Angular-rendered inline SVG inside the custom widget. Built as [`bst-trends-charts`](#bst-trends-charts) with the `render_mode` option selecting between the two. |
| **G2** | Multi-select chip input for `x_bst_startuptrk_investor.focus_areas` | A **choice-backed multi-select** rendered through the stock **Form** widget for write paths; `.label` chips inside a `.panel-body` for read-only display. The read-only chips are built in [`bst-investor-profile`](#bst-investor-profile). |
| **G3** | Loading indicator, replacing the legacy circular progress component | Service Portal's own loading indicator, or `.progress` containing `.progress-bar.progress-bar-striped.active`. The striped form is built in [`bst-startup-results`](#bst-startup-results). |
| **G4** | Card media, replacing the legacy card-media component | `.media-left` containing `img.media-object`, bound to `x_bst_startuptrk_startup.logo_url`. `.thumbnail` is the alternative container. Built in [`bst-startup-results`](#bst-startup-results) and in the company-profile header. |
| **G5** | Premium upsell and paywall treatment for `x_bst_startuptrk.user` | `.alert.alert-info` carrying a `.btn.btn-primary` call to action, rendered in place of each gated field or gated tab region. Packaged as [`bst-premium-upsell`](#bst-premium-upsell). |
| **G7** | Icon-system split between the deck and the portal | Platform glyph font in the portal, Lucide in the deck. Stated under [Iconography — the platform glyph font only](#iconography--the-platform-glyph-font-only). |

### Stock widgets used for the shell

| Stock widget | Bound or placed | Bootstrap class it renders | Options to set |
| --- | --- | --- | --- |
| **Stock Header** | Bound through `sp_theme.header` | `.navbar` | None. It renders `sp_portal.title`. |
| **Stock Footer** | Bound through `sp_theme.footer` | — | None. |
| **Breadcrumbs** | Placed as the first `sp_instance` on `bst_company`, `bst_investor`, `bst_dashboard` and `bst_account` | `.breadcrumb` | Defaults. |
| **Typeahead Search** | Optional substitute for the name filter of `bst-startup-search` where a plain typeahead suffices | `.form-control` in an `.input-group` | Its table and display-field options, set to `x_bst_startuptrk_startup` and `name`. |
| **Faceted Search** | Optional substitute for the industry and location filters of `bst-startup-search` | — | Its facet definitions, over `industry` and `headquarters_location`. |
| **Data Table from Instance Definition** | Substitute for `bst-startup-results` where a plain paginated record list suffices | `.table` with native pagination | `table`, `filter` and the column list. |
| **Form** (`sp-form`) | Placed or opened in an `spModal` for an **administrative** write path inside the portal | Bootstrap form classes | `table` and `sys_id`. |
| **Report / chart widget** | Embedded by `bst-trends-charts` when `render_mode` is `report` | — | The saved report identifier. |

A stock widget is instantiated, never edited. Editing a stock widget changes it for every portal on the instance. Where a stock widget needs different behaviour, clone it into the `x_bst_startuptrk` scope under a `bst-` name and edit the clone.

The **Form** widget is the write path for an administrator working inside the portal. Only `x_bst_startuptrk.admin` can write, because layer 2 of the access controls grants `write`, `create` and `delete` to that role alone; a caller holding `x_bst_startuptrk.user` or `x_bst_startuptrk.premium_user` who reaches a form widget is refused by the platform, and the widget must not present a save control to them.

## Step 6 — Access control in every widget server script

Do not soften any item in this section. The portal and the REST API must not disagree about what a role may see, and the only way to guarantee that is for both to use the same read path and the same serialiser.

### The secured read path

- Every caller-facing read in every widget server script uses **`GlideRecordSecure`**. Never `GlideRecord`.
- Ordinary record access does not guarantee access-control enforcement on a server-side read; the secured variant does.
- The complete list of paths in this application that read through the unsecured `GlideRecord` is in [`../access-control.md`](../access-control.md), and **no widget is on it**. A widget server script that opens a `GlideRecord` is a defect.
- No count is an exception. Produce every count with `RestResponseBuilder.countState()` or `RestResponseBuilder.countWith()`, which count by secured iteration under a bound. **Do not use an aggregate query in a widget**; an aggregate does not apply access controls.
- No Script Include in this application is client-callable, and none runs with elevated privilege. A widget must not reach a Script Include from its client controller, and must not construct one that reads a premium column through an unsecured path and returns it.
- The forbidden anti-pattern: **a helper that reads a premium-gated column with `new GlideRecord()` and hands the value to a widget bypasses the field-level access control entirely, and the access control reports no denial because it was never consulted.**

### Omitted, not nulled

- A denied field is **omitted** from the data object entirely. It is **not** nulled, **not** set to an empty string, and **not** replaced with a placeholder value.
- The mechanism matters because the failure is silent: **the secured read returns an empty string for a denied field, not an error.** Copying every column of a secured record onto `data` therefore produces exactly the nulled behaviour the requirements forbid, and the widget renders without complaint.
- To omit, the serialiser tests each field with an element-level read check and skips the key entirely when the check fails. That gate lives once, in `RestResponseBuilder.serialize()`, which obtains the element with `getElement()`, evaluates `canRead()` on it, and continues past the field without assigning a key when the evaluation is false.
- **`RestResponseBuilder.serialize(record, fields)` is the only permitted way to put record data into a widget's `data` object.** A data object built by any other means is not permitted, including one built with `$sp.getRecordValues()`.
- The template tests for **absence of the key**: `ng-if="item.total_funding_usd !== undefined"`. Do not test for an empty string, and do not test for `null` — a readable-but-empty currency, integer, string, date or reference column legitimately serialises as `null`, and confusing the two makes an empty premium field look denied and a denied field look empty.

### The seven premium fields the widgets must gate

Exactly seven, and there is no eighth. Each is gated by a field-level read access control granting `x_bst_startuptrk.admin` and `x_bst_startuptrk.premium_user` only, and denying `x_bst_startuptrk.user`.

| # | Premium field | Widgets that must gate it |
| --- | --- | --- |
| 1 | `startup.total_funding_usd` — `x_bst_startuptrk_startup.total_funding_usd` | `bst-startup-results`, `bst-company-profile`, `bst-investor-profile` |
| 2 | `startup.institutional_funding_last_5yrs` — `x_bst_startuptrk_startup.institutional_funding_last_5yrs` | `bst-company-profile` |
| 3 | `founder.contact_email` — `x_bst_startuptrk_founder.contact_email` | `bst-company-profile` |
| 4 | `executive.contact_email` — `x_bst_startuptrk_executive.contact_email` | `bst-company-profile` |
| 5 | `investor.aum_usd` — `x_bst_startuptrk_investor.aum_usd` | `bst-investor-profile` |
| 6 | `fundinground.amount_usd` — `x_bst_startuptrk_fundinground.amount_usd` | `bst-company-profile`, `bst-investor-profile` |
| 7 | `fundinground.valuation_usd` — `x_bst_startuptrk_fundinground.valuation_usd` | `bst-company-profile`, `bst-investor-profile` |

`contact_email` is gated on **two** tables and is a distinct access control on each. `x_bst_startuptrk_investor.portfolio_count` is **not** premium-gated and must not be treated as though it were. The full role-by-field matrix is in [`../access-control.md`](../access-control.md).

### Upsell substitution

- Wherever a gated field or a gated tab region is denied, render `bst-premium-upsell` in its place.
- Render **no blank, no empty cell, no zero and no dash** where a premium field was denied. An empty cell is indistinguishable from a genuinely empty column and hides the entitlement boundary from the caller.
- At field granularity, render a `.label.label-default` reading `Premium` in the cell, and render the `bst-premium-upsell` partial once for the surface. The three hosts and the options each passes are enumerated under [`bst-premium-upsell`](#bst-premium-upsell).
- The partial must never receive the value it exists to hide. It renders column names and static wording only.

### Operational warning — the administrator override

**An access-control check performed while signed in as the instance administrator does not test enforcement.** Record access controls allow the platform administrator role to override them, and every operator of a personal developer instance holds that role. A walkthrough conducted as the instance administrator displays all seven premium fields and **appears to prove enforcement that was never tested at all**. A result obtained that way must not be recorded as evidence.

Verify under **impersonation**, as follows.

1. Create three purpose-built users. Each holds **exactly one** of `x_bst_startuptrk.admin`, `x_bst_startuptrk.premium_user` and `x_bst_startuptrk.user`, and **none** of the elevated platform roles — not the platform `admin` role, not `security_admin`, not `maint`. Note that the scoped role `x_bst_startuptrk.admin` and the platform administrator role are different roles; the test user holds the scoped one and not the platform one.
2. Impersonate each user in turn and walk all five routes. Do not read the fields as yourself.
3. Under `x_bst_startuptrk.user`, confirm that every one of the seven premium fields renders the `Premium` label or the upsell treatment, and that `bst-premium-upsell` appears on the company profile, the investor profile and the account summary.
4. Under `x_bst_startuptrk.premium_user` and under `x_bst_startuptrk.admin`, confirm every one of the seven renders its value and that `bst-premium-upsell` does **not** appear.
5. Confirm that a non-premium column — for example `x_bst_startuptrk_startup.headquarters_location` — renders a value under `x_bst_startuptrk.user` on the same screen. That establishes that the table-level grant passed and that the denial came from the field-level control.

The full procedure, the twenty-one field-by-role outcomes and the reason each step is required are in [`../access-control.md`](../access-control.md). The three users are created by test setup steps at run time, specified in [`./05-atf-test-suites.md`](./05-atf-test-suites.md), which is also where the twenty-one automated assertions live. The manual walkthrough above does not replace them.

## Legacy provenance

The legacy React tree under `src/frontend/` is read-only historical reference. **Nothing in it is ported.** This section exists so the migration is traceable in reverse — from each legacy construct to the portal artifact that replaced it — and it is the only place in this guide where a literal value appears. Every route, tab label, layout and component vocabulary item in the target comes from prompt section 5.0 and from the design system, not from these files.

### The five legacy routes

`src/frontend/App.tsx:L29-L37` declares five `react-router` routes: `/`, `/search`, `/company/:id`, `/investor/:id` and `/user/:id`. They are the route-inventory antecedent of the five pages, and of nothing else.

| # | Legacy route | Target page | Target link form |
| --- | --- | --- | --- |
| 1 | `/` and `/search` | `bst_home` | `?id=bst_home` |
| 2 | `/company/:id` | `bst_company` | `?id=bst_company&sys_id=<startup sys_id>` |
| 3 | `/investor/:id` | `bst_investor` | `?id=bst_investor&sys_id=<investor sys_id>` |
| 4 | `/user/:id` | `bst_account` | `?id=bst_account` |
| 5 | *no legacy route* | `bst_dashboard` | `?id=bst_dashboard` |

The legacy tree collapsed `/` and `/search` into two routes rendering related surfaces, and had no dashboard route; the target has one Home / Search page and one Dashboard / Trends page. The path-to-query-parameter change is stated under [Routing and navigation](#routing-and-navigation) and its decision is in [`../../../docs/decisions/DECISION_LOG.md`](../../../docs/decisions/DECISION_LOG.md).

`src/frontend/App.tsx:L12` reads `import theme from './styles/theme';` — **a module that was never authored.** `src/frontend/styles/` contains only `global.css`. There was consequently no legacy theme object, so **no legacy theme value exists to carry forward even in principle**, and the theme built in [Step 2](#step-2--the-theme-record) is authored from the design system.

### The legacy design-token surface

`src/frontend/styles/global.css` is the repository's **entire** design-token surface: **41 lines of hard-coded literals** and no variable of any kind. The migration therefore introduces a token system where none was present.

Its complete contents, and the target token each value maps to:

| Legacy declaration | Legacy value | Target token |
| --- | --- | --- |
| `body { font-family: … }` | `'Roboto', 'Helvetica', 'Arial', sans-serif` | `$font-family-sans-serif` |
| `body { background-color: … }` | `#f5f5f5` | `$body-bg` **and** `$sp-body-bg` |
| `a { color: … }` | `#1976d2` | `$brand-primary`, and through it `$btn-primary-bg` |
| `.container { max-width: … }` | `1200px` | `$container-lg` |
| `body { margin; padding }` | `0` | Bootstrap's own normalisation. Not carried forward. |
| `a { text-decoration }`, `a:hover { text-decoration }` | `none`, `underline` | Bootstrap's own link treatment. Not carried forward. |
| `.container { margin; padding }` | `0 auto`, `20px` | `$grid-gutter-width` and the `$padding-base-*` pair. The literal is **not** carried forward. |
| `.text-center` | `text-align: center` | Bootstrap's `.text-center` utility, which is identical. |
| `.mt-20` | `margin-top: 20px` | `$grid-gutter-width` or `$padding-base-vertical`, applied in scoped widget CSS. The ad-hoc 20-pixel utility class is **replaced by the Bootstrap spacing scale**, not carried forward. |
| `.mb-20` | `margin-bottom: 20px` | As `.mt-20`. |

**Four values are carried forward** — the font stack, the page background, the link colour and the container maximum — and they are declared in the theme's CSS-variables field, and nowhere else. Everything else in the file is replaced by the design system's own treatment.

### Tab inventory

`src/frontend/components/CompanyProfile/CompanyProfile.tsx:L86-L91` declares **six** Material-UI tabs: **Overview**, **Team**, **Funding**, **Jobs**, **News**, **Similar Companies**.

The target company profile has **five** tabs, specified by prompt section 5.0. The mechanics of the difference:

| Legacy tab | Target pane | Mechanic |
| --- | --- | --- |
| Overview | **Overview** | Unchanged in name. Rendered as `.list-group` / `.list-group-item`. |
| Team | **People** | Re-specified as "People", and it now carries founders **and** executives together in one pane, sourced from `x_bst_startuptrk_founder` and `x_bst_startuptrk_executive`. |
| Funding | **Funding** | Unchanged in name. Rendered as `.table.table-striped.table-hover` inside `.table-responsive`. |
| Jobs | **Jobs** | Unchanged in name. |
| News | **News** | Unchanged in name. |
| Similar Companies | *no target pane* | **Dropped.** The binding schema of prompt section 1.0 declares no competitor or similarity column on any of the seven entity tables, so there is no data to render. |

The reduction from six panes to five, the "Team" to "People" rename and the dropped "Similar Companies" pane are deviations from a literal reading of the legacy surface. Their decisions are recorded in [`../../../docs/decisions/DECISION_LOG.md`](../../../docs/decisions/DECISION_LOG.md).

`src/frontend/components/InvestorProfile/InvestorProfile.tsx:L76-L79` declares **four** tabs: **Overview**, **Portfolio**, **Recent Investments**, **Investment Trends**. The target investor profile uses **no tab control**; it renders an overview panel, a portfolio table, and two rounds tables — rounds led and rounds participated in — all as `.panel` regions in a two-column `.col-md-4` / `.col-md-8` layout, with `x_bst_startuptrk_investor.portfolio_count` surfaced in the overview panel.

| Legacy tab | Target region |
| --- | --- |
| Overview | The `.col-md-4` overview `.panel`, carrying `type`, `focus_areas` chips, `portfolio_count`, `aum_usd` and `website`. |
| Portfolio | The Portfolio `.panel`, a `.table.table-striped.table-hover` over the union of the startups reached by the lead and participation paths. |
| Recent Investments | The two rounds `.panel` regions, split by lead versus participation, each ordered by `round_date` descending. |
| Investment Trends | No investor-scoped trend region. Trends are served portal-wide by `bst_dashboard`. |

### The dashboard

`src/frontend/components/Dashboard/Dashboard.tsx:L68-L106` is a six-panel Grid and Paper layout: **QuickStats**, **RecentUpdates**, **TrendingStartups**, **FeaturedCompanies**, **LatestNews** and **JobOpenings** — and it carries **no chart import at all**. Its imports at `src/frontend/components/Dashboard/Dashboard.tsx:L3` are `Grid`, `Typography` and `Paper` only. The target `bst_dashboard` renders `bst-trends-kpi` as a row of `.panel.panel-default` KPI panels and `bst-trends-charts` as two chart panels, so design-system gap **G1** loses nothing that existed.

### The representative composition

`src/frontend/components/Search/SearchInterface.tsx:L64-L103` is the representative legacy composition: a `Paper` wrapping a `Grid container` that holds a `TextField`, a `Button variant="contained" color="primary"`, a `CircularProgress`, a `Typography` result count and a pagination control. Its target equivalent is `bst-startup-search` plus `bst-startup-results` on `bst_home`: a `.panel.panel-default` containing a `.row` of three `.col-md-4` filters with `.form-control` inputs and a `.btn.btn-primary`, and a results panel carrying a `.progress` striped indicator, a `.text-muted` count and a `.btn.btn-default` pager.

`src/frontend/components/common/Header.tsx` composes `AppBar`, `Toolbar`, `Typography`, `Button`, `IconButton`, `Menu` and `MenuItem` from `@material-ui/core` at `src/frontend/components/common/Header.tsx:L4`, together with `@material-ui/icons` at `src/frontend/components/common/Header.tsx:L6`. All of it is replaced by the **stock Header widget** bound through `sp_theme.header`, which renders Bootstrap `.navbar`, and by the **platform glyph font**.

`src/frontend/components/common/CompanyCard.tsx:L3` composes `Card`, `CardContent`, `CardMedia`, `Typography` and `Button`, with the card media bound to the company logo. It is replaced by the `.panel` and `.media` object composition of `bst-startup-results`. `src/frontend/components/common/Pagination.tsx:L2` imports a pagination component from `@material-ui/lab`; it is replaced by the native pagination of the stock Data Table widget, or by the two `.btn.btn-default` pager buttons of `bst-startup-results`.

`package.json:L15-L16` declares `"@material-ui/core": "^4.12.3"` and `"@material-ui/icons": "^4.11.2"`. Both are **left untouched**, because the legacy manifest is reference-mode and is not edited by this work.

### Component mapping

Every legacy Material-UI component actually imported across `src/frontend/`, and its Bootstrap 3.3.6 equivalent in this portal.

| Legacy component | Target | Reference path or class |
| --- | --- | --- |
| `AppBar`, `Toolbar` | Stock Header widget rendering a navbar | `sp_theme.header`; `.navbar` |
| `IconButton`, `Menu`, `MenuItem` | Stock Header widget's own menu | `sp_theme.header` |
| `Grid` container and item | Bootstrap grid | `.container`, `.row`, `.col-md-*`, `.col-lg-*` |
| `Container` | Bootstrap container bounded by `$container-lg` | `.container` |
| `Paper` | Bootstrap panel | `.panel.panel-default` with `.panel-heading` / `.panel-title` / `.panel-body` |
| `Button variant="contained" color="primary"` | Bootstrap primary button | `.btn.btn-primary` |
| `Button` secondary and text variants | Bootstrap default and link buttons | `.btn.btn-default`, `.btn.btn-link` |
| `TextField` | Bootstrap form control | `.form-control` inside `.form-group`, with `.input-group` and `.input-group-btn` where a button abuts the field |
| `Card`, `CardContent` | Bootstrap panel with a media object | `.panel` + `.media` / `.media-body` / `.media-heading` |
| `CardMedia` | Bootstrap media object image | `.media-left > img.media-object`, bound to `logo_url`; `.thumbnail` as the alternative |
| `Tabs`, `Tab` | Bootstrap tabs | `.nav.nav-tabs` + `.tab-content` / `.tab-pane` |
| `Typography` | Bootstrap heading elements and text utilities | `<h2>`, `<h3>`, `.panel-title`, `.media-heading`, `.text-muted` |
| `CircularProgress` | Service Portal loading indicator, or a striped progress bar | `.progress > .progress-bar.progress-bar-striped.active` |
| Pagination from `@material-ui/lab` | Native pagination of the stock Data Table widget, or two pager buttons | `.btn.btn-default` |
| `@material-ui/icons` | Platform glyph font | `.icon-search`, `.icon-user`, `.icon-chart`, and the release's further `.icon-*` classes |
| `ThemeProvider`, `CssBaseline` | The `sp_theme` record and its CSS-variables field | `sp_theme.css_variables` |
| `makeStyles` JSS objects | The widget's own CSS field, scoped beneath the widget root class | `sp_widget.css` |
| Tabular data rendered inline | Bootstrap table | `.table.table-striped.table-hover` inside `.table-responsive` |
| Status and category text | Bootstrap label | `.label.label-primary`, `.label.label-default` |
| Key-and-value detail blocks | Bootstrap list group | `.list-group` / `.list-group-item` |
| Notices rendered as text | Bootstrap alert | `.alert.alert-info`, `.alert.alert-warning` |
| *no legacy equivalent* | Breadcrumb trail | Breadcrumbs widget; `.breadcrumb` |
| *no legacy equivalent* | Modal dialogue | `spModal.open()` / `.alert()` / `.confirm()`; Bootstrap `.modal` |
| *no legacy equivalent* | Administrative write form | Form widget (`sp-form`) with `table` and `sys_id` |

## Build verification

Run every check before this guide is signed off. A failed check is a defect in this build, not an exception to be recorded.

### Inventory

- [ ] Exactly **1** `sp_portal` record, and its `url_suffix` reads exactly `bst`.
- [ ] Exactly **1** `sp_theme` record, newly created, with the stock Header and stock Footer bound and its CSS-variables field populated.
- [ ] Exactly **5** `sp_page` records, whose `id` values read exactly `bst_home`, `bst_company`, `bst_investor`, `bst_dashboard` and `bst_account`.
- [ ] Exactly **8** `sp_widget` records, whose `id` values read exactly `bst-startup-search`, `bst-startup-results`, `bst-company-profile`, `bst-investor-profile`, `bst-trends-kpi`, `bst-trends-charts`, `bst-account-summary` and `bst-premium-upsell`.
- [ ] Every one of those 15 records carries `sys_scope` `Boston Startup Tracker`.
- [ ] Zero `sys_ux_*` records were created, and UI Builder was not opened.
- [ ] The company profile renders exactly **five** tabs, labelled **Overview**, **Funding**, **People**, **Jobs**, **News**, in that order.
- [ ] `bst-premium-upsell` is embedded by exactly three hosts and is placed on no page.

### Design system

- [ ] No widget CSS contains a literal colour, spacing, radius or font value. The only literals present are `0`, `none`, `auto`, `inherit`, `currentColor` and `transparent`.
- [ ] No `.col-xs-*` or `.col-sm-*` class appears in any widget template, and no `size`, `size_xs` or `size_sm` is set on any `sp_rectangle`.
- [ ] The walkthrough was performed at 1024 pixels wide and above, the declared floor.
- [ ] No Lucide reference and no emoji character appears in any widget template, CSS field, client controller, option label or option default.
- [ ] Every icon is a platform glyph-font `.icon-*` class.
- [ ] No repository manifest was created or edited.

### Access control

- [ ] Every widget server script reads through `GlideRecordSecure` and serialises through `RestResponseBuilder.serialize()`. No widget opens a `GlideRecord`, and no widget issues an aggregate query.
- [ ] A denied premium field has **no key** on the serialised object, and every template test is `!== undefined` rather than a null or empty-string comparison.
- [ ] All seven premium fields were checked under impersonation by a user holding exactly one scoped role and none of the elevated platform roles.
- [ ] `bst-premium-upsell` appeared on the company profile, the investor profile and the account summary under `x_bst_startuptrk.user`, and appeared on none of them under `x_bst_startuptrk.premium_user`.
- [ ] A non-premium column rendered a value under `x_bst_startuptrk.user` on the same screen as a denied premium field.

### Routes

- [ ] All five routes render and navigate, walked in this order: `?id=bst_home`, `?id=bst_company&sys_id=<startup>`, `?id=bst_investor&sys_id=<investor>`, `?id=bst_dashboard`, `?id=bst_account`.
- [ ] `/bst` with no `id` resolves to `bst_home`.
- [ ] Every one of the eleven navigation hops under [Routing and navigation](#routing-and-navigation) reaches its target page with the correct `sys_id`.
- [ ] `bst_company` and `bst_investor` each render the not-found alert, and not an empty panel, when `sys_id` is absent or unresolvable.

### The inclusion filter

- [ ] Seed one startup that fails the criteria — `active` false, or a `headquarters_location` containing neither `Boston` nor `Cambridge, MA`. Load records first with [`./06-staging-table-csv-import.md`](./06-staging-table-csv-import.md).
- [ ] Under `x_bst_startuptrk.user`, that startup is **absent** from `bst_home` results and absent from the `bst_dashboard` KPI figures.
- [ ] The same startup is **present** in the platform list view for `x_bst_startuptrk_startup` under `x_bst_startuptrk.admin`, which is the administrative visibility [`../data-model.md`](../data-model.md) specifies.
- [ ] `data.total_count` on `bst-startup-results` agrees with the number of rows the pager reports across all pages. A count that disagrees with the page contents means the plan was applied to one and not the other.
- [ ] No widget template, client controller or server script evaluates `active` or `headquarters_location` outside `StartupSearchService.applyPlan()`.

This is the evidence for criterion 5 of [`../validation-checklist.md`](../validation-checklist.md), which records the outcome.

## Related documents

- [`../../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml`](../../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml) — the authoritative table, column, choice, Script Include, property and role records this guide cites, and the artifact whose commit is precondition 3
- [`../data-model.md`](../data-model.md) — the ten tables field by field, the seven premium markers, the closed choice lists the widgets render, the `participating_investors` projection and the inclusion criteria
- [`../access-control.md`](../access-control.md) — the three roles, the five access-control layers, the role-by-field matrix, the secured read path, the omit-not-null rule and the impersonation procedure
- [`../api-reference.md`](../api-reference.md) — the Script Include call graph with every public method, the thirteen system properties including the two page-size properties this portal shares with the API, and the pagination envelope
- [`../validation-gates.md`](../validation-gates.md) — the sixteen post-commit gates that are precondition 4
- [`../manual-build-instructions.md`](../manual-build-instructions.md) — the index and dependency ordering of the six manual-build guides
- [`./01-connection-credential-aliases.md`](./01-connection-credential-aliases.md) — step 1, the two Connection and Credential Aliases
- [`./02-flow-crunchbase-ingestion.md`](./02-flow-crunchbase-ingestion.md) — step 2, the Crunchbase ingestion flow
- [`./03-flow-linkedin-ingestion.md`](./03-flow-linkedin-ingestion.md) — step 3, the LinkedIn ingestion flow
- [`./05-atf-test-suites.md`](./05-atf-test-suites.md) — the last step, carrying the twenty-one field-by-role assertions and the run-time creation of the three impersonated users this guide's walkthrough also requires
- [`./06-staging-table-csv-import.md`](./06-staging-table-csv-import.md) — step 5, the staging-table CSV load that puts records on the instance before the walkthrough
- [`../validation-checklist.md`](../validation-checklist.md) — the five success criteria; criterion 5 is the pass condition for the route walkthrough and the inclusion filter
- [`../gaps-and-flags.md`](../gaps-and-flags.md) — the design-system gaps G1 through G5 and G7, the query-parameter routing deviation and the premium-billing flag
- [`../../../docs/decisions/DECISION_LOG.md`](../../../docs/decisions/DECISION_LOG.md) — the single source of truth for every decision behind this portal, including the five deviations named at the top of this guide
- [`../../../docs/review/CRITICAL_DECISIONS.md`](../../../docs/review/CRITICAL_DECISIONS.md) — the five highest-risk decisions, whose entry 5 is the UX reviewer entry for this guide
