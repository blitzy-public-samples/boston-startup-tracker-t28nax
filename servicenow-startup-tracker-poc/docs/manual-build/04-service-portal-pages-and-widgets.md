# Manual build 04 — Service Portal pages and widgets — `x_bst_startuptrk`

This guide builds the Service Portal experience of the ServiceNow scoped application `x_bst_startuptrk` by hand, on the instance, through the platform's own interface. It specifies **one** portal record, **one** theme record, **five** pages and **eight** widgets, and for each one it states every field to set, every option in the option schema, the server-script responsibilities, the client-controller responsibilities, the HTML template structure with the Bootstrap classes it uses, and the widget CSS. It also states the design-system contract every widget author must satisfy, the access-control rules every widget server script must honour, and the verification checklist to run before this guide is signed off.

**Authority.** The frozen prompt and the Agent Action Plan are authoritative for all application content. The Update Set XML at [`../../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml`](../../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml) is the authoritative source for every table name, column name, choice value, Script Include class name, method name, system-property key and role name cited below; the identifiers used here match those records character for character, and the same identifiers appear in [`../data-model.md`](../data-model.md), [`../access-control.md`](../access-control.md) and [`../api-reference.md`](../api-reference.md). No variant spelling of any identifier is valid. Where this guide and those records disagree, the records are checked against the prompt and the plan first; where the records match the specification, this guide is corrected to them.

This document carries **no rationale**. It states what to build and how to build it. Every decision behind the portal, every alternative considered and every risk it carries is recorded in [`../../../docs/decisions/DECISION_LOG.md`](../../../docs/decisions/DECISION_LOG.md), which is the single source of truth for "why". Five points in this guide depart from a literal reading of the requirements — the five-tab company profile, the "Team" to "People" tab rename, the dropped "Similar Companies" tab, query-parameter routing in place of path-style routes, and the 1024-pixel viewport floor. Each is stated below as a build mechanic and cross-referenced to that log. None is argued here.

Operational warnings **are** in scope for this guide and are marked as such. The administrator-override warning under [Operational warning — the administrator override](#operational-warning--the-administrator-override) is the most important one in this file and must not be skipped.

## Referenced documents

This guide is executable on its own. The portal, the theme, **every one of the thirty-three token declarations as a literal value**, all five pages, all eight widgets, the design-system contract, the access-control rules and the verification checklist are stated here in full. An operator needs no other file, and no external stylesheet reference, to build the portal: [The complete declaration block](#the-complete-declaration-block) can be pasted into the theme record as it stands.

**Every document named below is delivered and readable.** Each link resolves to a file in this package, among them `../../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml`, `../data-model.md`, `../access-control.md`, `../api-reference.md` and `../validation-gates.md`, so a reader can follow any link and read the content the statement around it describes; no link is a forward reference to something still to be written.

**Reviewer.** This guide is the artifact validated by **entry 5 of [`../../../docs/review/CRITICAL_DECISIONS.md`](../../../docs/review/CRITICAL_DECISIONS.md), risk Medium, reviewer persona UX**, whose check is to walk all five routes and confirm the premium upsell treatment appears wherever a gated field is denied — an obligation placed on this file by the project rule **Critical Decision Review Document**.

**The UX review obligation itself survives, and this guide is still where it is discharged.** The three deviations remain fully logged — `D-055` the five-tab profile with Team re-specified as People and Similar Companies dropped, `D-056` query-parameter routing, and `D-057` the 1024-pixel viewport floor — in [`../../../docs/decisions/DECISION_LOG.md`](../../../docs/decisions/DECISION_LOG.md), each with its alternatives, rationale and risks. A UX reviewer works from those three rows and from this guide: walk all five routes, confirm the fixed five-tab strip, and confirm the premium upsell treatment appears wherever a gated field or gated tab region is denied. The route walkthrough is also required independently by criterion 5 of [`../validation-checklist.md`](../validation-checklist.md), so it is gated by the acceptance record whether or not a review entry names it.

## Position in the build order

This is **guide 04 of six**, and it is **step 4** of the execution order below. The order is stated in full in [`../manual-build-instructions.md`](../manual-build-instructions.md); it is repeated here so this guide can be run without it.

| Step | Guide | Dependency that fixes this position |
| --- | --- | --- |
| 1 | [`./01-connection-credential-aliases.md`](./01-connection-credential-aliases.md) | The two Connection and Credential Aliases the flows bind to by name. Nothing downstream can authenticate without them. |
| 2 | [`./02-flow-crunchbase-ingestion.md`](./02-flow-crunchbase-ingestion.md) | The Crunchbase ingestion flow, which requires the alias from step 1. |
| 3 | [`./03-flow-linkedin-ingestion.md`](./03-flow-linkedin-ingestion.md) | The LinkedIn ingestion flow, which requires the alias from step 1. |
| **4** | **This guide** | **The portal, theme, five pages and eight widgets.** |
| 5 | [`./06-staging-table-csv-import.md`](./06-staging-table-csv-import.md) | The staging-table CSV load, which puts records on the instance for the portal walkthrough and for the fallback ingestion path. |
| 6 | [`./05-atf-test-suites.md`](./05-atf-test-suites.md) | The Automated Test Framework suites, **last**: they exercise everything the five preceding guides build. |

Guides 01, 02 and 03 precede this one. Guide 06 follows it, then guide 05 runs last.

The portal can be built before any record exists on the instance, but it cannot be **walked through** until records exist. Run guide 06 before the walkthrough under [Build verification](#build-verification).

## Preconditions

Do not begin this guide until every item below holds.

| # | Precondition | How to confirm |
| --- | --- | --- |
| 1 | The Update Set has been uploaded and has reached the `loaded` state. | The `sys_remote_update_set` record shows `state` `loaded`. |
| 2 | The preview has completed with an **empty error-type problem set**. | A read of `sys_update_preview_problem` filtered to this remote update set and `type=error` returns an empty `result` array. Warnings are logged and do not block. |
| 3 | The Update Set has **committed**. | The `sys_remote_update_set` record shows `state` `committed`. |
| 4 | **All eleven required post-commit gates have passed.** | Run the eleven required gates in [`../validation-gates.md`](../validation-gates.md) — the seven entity-table reads `GATE-TBL-01` through `GATE-TBL-07`, the three role-record gates `GATE-ROLE-01` through `GATE-ROLE-03`, and the one scope-record gate `GATE-SCOPE-01` — and record `pass` for all eleven in that document's required-gate evidence table. The aggregate pass condition is `11 of 11`; there is no partial pass, and no required gate may be skipped, deferred or waived. Neither `GATE-COL-01` nor a non-normative diagnostic is a precondition of this guide. |
| 5 | The **eight** Script Includes this portal calls into are on the instance. | `sys_script_include` carries `AppProperties`, `RestQueryHelper`, `RestResponseBuilder`, `RateLimitService`, `StartupSearchService`, `InvestorPortfolioService`, `IngestionLogger` and `IngestionMapper`, all in the `x_bst_startuptrk` scope. The call graph is in [`../api-reference.md`](../api-reference.md). |
| 6 | The **eleven** scoped system properties are on the instance. | `sys_properties` carries all eleven `x_bst_startuptrk.*` keys, including `x_bst_startuptrk.rest.default_limit`, `x_bst_startuptrk.rest.max_limit` and `x_bst_startuptrk.inclusion.location_tokens`. The inventory is in [`../api-reference.md`](../api-reference.md). |
| 7 | You are working in the `x_bst_startuptrk` application scope. | The application picker reads **Boston Startup Tracker**. Every record this guide creates must carry that scope. |
| 8 | You hold a role that can create Service Portal records. | You can open `sp_portal`, `sp_theme`, `sp_page`, `sp_widget`, `sp_container`, `sp_row`, `sp_rectangle` and `sp_instance` and insert into each. |

The Script Include and property counts in preconditions 5 and 6 are **eight** and **eleven** delivered, of which this portal calls **four** and reads **three**. Those are the figures the Update Set delivers, the figures [`../api-reference.md`](../api-reference.md) inventories, and the figures the Agent Action Plan specifies in its sections 0.4.5 and 0.4.7; the three counts agree. A ninth Script Include or a twelfth property on the instance is a stale record from an earlier build, not an artifact of this delivery, and no widget in this guide calls or reads one.

### Capture rule for this artifact class

Only tables carrying the update-synch attribute are captured into `sys_update_xml`, and adding that attribute to a table that lacks it out of the box is unsupported. The portal, theme, page, container, row, rectangle, instance and widget tables are outside the captured set, so these artifacts are built through the platform interface. The delivered Update Set therefore contains **zero** `sp_portal`, `sp_theme`, `sp_page` and `sp_widget` records. [`../manual-build-instructions.md`](../manual-build-instructions.md) owns the split rule for the package as a whole, and the decision is recorded at `D-074`.

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
| Header menu | `sp_instance_menu` | **1** | Boston Startup Tracker header menu |
| Menu items | `sp_rectangle_menu_item` | **3** | `Home`, `Dashboard`, `Account` |
| Theme | `sp_theme` | **1** | Boston Startup Tracker |
| Pages | `sp_page` | **5** | `bst_home`, `bst_company`, `bst_investor`, `bst_dashboard`, `bst_account` |
| Widgets | `sp_widget` | **8** | `bst-startup-search`, `bst-startup-results`, `bst-company-profile`, `bst-investor-profile`, `bst-trends-kpi`, `bst-trends-charts`, `bst-account-summary`, `bst-premium-upsell` |

Eight widget names, seven of which are placed directly on a page. The eighth, `bst-premium-upsell`, is a reusable partial embedded by **three** hosts and is never given a page of its own.

Build in this order, because each step references the one before it.

1. The eight widgets — [Step 4](#step-4--the-eight-widgets). A page instance cannot name a widget that does not exist.
2. The theme — [Step 2](#step-2--the-theme-record). The portal record binds to it.
3. The five pages — [Step 3](#step-3--the-five-pages).
4. The portal, then its header menu and the three menu items — [Step 1](#step-1--the-portal-record). The portal's homepage field binds to `bst_home`, so build that page first, and the menu items name pages that must already exist.

The step numbering below follows the reading order of the artifacts, not the insertion order. Insert in the order of the four bullets above.

## Step 1 — The portal record

One record in `sp_portal`, plus the one header-menu record it binds. Set every field in the table below; the **Value** column is the value to enter, and a value of *empty* means the field is deliberately left blank.

### The portal record fields

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
| Main menu | `sp_rectangle_menu` | `Boston Startup Tracker header menu` | The menu record built in [The header menu and its items](#the-header-menu-and-its-items). **Do not leave this empty:** the Stock Header widget renders its links from this binding, and without it `bst_dashboard` and `bst_account` have no incoming navigation control on any page. |
| Direct order guest access | the guest-access fields | `false` | Not used. |
| CSS variables | `sp_css_variable` | *empty* | **Leave the portal-level variables empty.** All tokens are declared once on the theme; see [Theme and variable authoring rules](#theme-and-variable-authoring-rules). |

### The header menu and its items

One menu record and three menu items. The Stock Header widget bound through `sp_theme.header` renders the portal title and, beside it, one link per item of the menu the portal's **Main menu** field names. These three items are the **only** incoming navigation controls for `bst_dashboard` and `bst_account`, so build them before the walkthrough in [Build verification](#build-verification).

Build the menu record first, then add the items **through the menu record's own Menu Items related list**, so the platform sets each item's parent reference rather than the operator typing it.

**The menu record** — one record on `sp_instance_menu`, created from **Service Portal > Menus**:

| Field | Column | Value | Note |
| --- | --- | --- | --- |
| Title | `title` | `Boston Startup Tracker header menu` | Bound from `sp_portal.sp_rectangle_menu`. |
| Widget | `sp_widget` | `Header Menu` | The baseline Header Menu widget. Do not clone it; this portal customises the items, not the widget. |
| Application | `sys_scope` | `Boston Startup Tracker` | The `x_bst_startuptrk` scope. Confirm this before saving. |

**The three items** — three records on `sp_rectangle_menu_item`, each added from the **Menu Items** related list of the record above:

| Order | Label | Type | Href | Reaches |
| --- | --- | --- | --- | --- |
| `100` | `Home` | `URL` | `?id=bst_home` | Route 1, Home / Search |
| `200` | `Dashboard` | `URL` | `?id=bst_dashboard` | Route 4, Dashboard / Trends |
| `300` | `Account` | `URL` | `?id=bst_account` | Route 5, Account Management |

Three points govern these items.

- **Use the `URL` item type, not the page type.** A `URL` item carries the query string this portal's routing depends on. Enter the `Href` exactly as the table gives it, with the leading `?` and no leading slash, so the link resolves inside `/bst`.
- **Leave each item's role and condition fields empty.** All three destinations are readable by every one of the three scoped roles, so the three links render for every signed-in caller. A role filter here would re-orphan `bst_account` for the premium and administrator roles, which is the defect these items exist to prevent.
- **No fourth item.** `bst_company` and `bst_investor` are record-scoped and are reached from a result card, a funding row or a portfolio row, never from a menu.

After saving the portal, the menu and the three items, open `https://<instance>.service-now.com/bst` and confirm three things: the portal resolves, the `bst_home` page renders, and the header shows the three links **Home**, **Dashboard** and **Account**. Follow each link and confirm it lands on the page the table names.

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

Every token the widgets reference is declared here, in the theme's CSS-variables field, and **nowhere else**. Declare each variable in the table below with a SASS declaration of the form `$variable: value;`, one per line, grouped in the order the table gives. **The Value column below is the literal to type.** Nothing is left to be looked up elsewhere: every one of the thirty-three variables carries its exact value here, and [The complete declaration block](#the-complete-declaration-block) repeats all thirty-three as a single block that can be pasted into the field as it stands.

The thirty-three values divide into four provenance classes, and every one of them is typed as a literal here regardless of class:

- **Four are carried forward from the legacy stylesheet** — the body font stack, the page background, the link colour and the container maximum. They are marked *carried forward* below, and their provenance is recorded under [The legacy design-token surface](#the-legacy-design-token-surface).
- **One repeats a carried-forward value**: `$sp-body-bg` is declared to the same `#f5f5f5` as `$body-bg`, so the portal chrome and the page agree.
- **Two are this theme's own literals in the platform namespace**: `$sp-tagline-color` and `$sp-navbar-divider-color` are declared here rather than left to the platform default (`D-120`).
- **The remaining twenty-six are the Bootstrap 3.3.6 default, declared explicitly**, so the theme owns each value rather than inheriting it silently.

**Declare the rows in the order the table gives them.** Three rows resolve to another variable rather than to a literal — `$headings-font-family`, `$btn-primary-bg` and `$sp-body-bg` — and each references a variable declared on an earlier row. A theme variables field is compiled ahead of Bootstrap's own variable file, so a reference to a Bootstrap variable this table does not itself declare would be undefined; reference only rows above.

| Group | Variable | Governs | Value to declare |
| --- | --- | --- | --- |
| Brand | `$brand-primary` | The primary action colour behind `.btn-primary`, `.label-primary`, `.panel-primary` and link text. | `#1976d2` — the legacy link colour, **carried forward**. |
| Brand | `$brand-success` | `.alert-success`, `.label-success`, `.progress-bar-success`. Required by the alert and label components this portal uses. | `#5cb85c` |
| Brand | `$brand-info` | `.alert-info`, `.label-info`. **Used by `bst-premium-upsell`.** | `#5bc0de` |
| Brand | `$brand-warning` | `.alert-warning`, `.label-warning`. | `#f0ad4e` |
| Brand | `$brand-danger` | `.alert-danger`, `.label-danger`. | `#d9534f` |
| Surface | `$body-bg` | The page background of the whole portal. | `#f5f5f5` — the legacy page background, **carried forward**. |
| Surface | `$sp-body-bg` | The Service Portal body background, in the platform's own `$sp-*` namespace. Declared to the same value as `$body-bg` so the portal chrome and the page agree. | `#f5f5f5` — the legacy page background, **carried forward**. |
| Surface | `$panel-bg` | The fill of every `.panel`. Replaces the legacy surface elevation. | `#ffffff` |
| Surface | `$panel-default-border` | The border of every `.panel.panel-default`. | `#dddddd` |
| Typography | `$font-family-sans-serif` | The body typeface of the whole portal. | `'Roboto', 'Helvetica', 'Arial', sans-serif` — the legacy body font stack, **carried forward**. |
| Typography | `$font-size-base` | The base type size from which every heading size is computed. No legacy value existed. | `14px` |
| Typography | `$line-height-base` | The base line height and therefore the vertical rhythm. No legacy value existed. | `1.428571429` |
| Typography | `$headings-font-family` | The heading typeface. Declared to `$font-family-sans-serif` rather than repeating the stack, so the two cannot drift. | `$font-family-sans-serif` |
| Typography | `$headings-font-weight` | The heading weight. Replaces the legacy heading variant props. | `500` |
| Layout | `$container-lg` | The maximum width of `.container` at the large breakpoint, which is the widest layout this portal serves. | `1200px` — the legacy container maximum, **carried forward**. Bootstrap's own default is `1170px`; this is the one layout value the legacy stylesheet overrides. |
| Layout | `$grid-gutter-width` | The horizontal gutter between grid columns and the spacing unit widget CSS uses for block separation. | `30px` |
| Layout | `$padding-base-vertical` | The vertical padding of `.btn` and `.form-control`, and the spacing unit for inset padding in widget CSS. | `6px` |
| Layout | `$padding-base-horizontal` | The horizontal padding of `.btn` and `.form-control`, and the spacing unit for inset padding in widget CSS. | `12px` |
| Radius | `$border-radius-base` | The corner radius of `.btn`, `.form-control` and `.panel`. No legacy value existed. | `4px` |
| Radius | `$border-radius-large` | The radius of `.btn-lg` and large panels. | `6px` |
| Radius | `$border-radius-small` | The radius of `.btn-sm` and `.label`. | `3px` |
| Table | `$table-bg` | The fill of every `.table`. Replaces the legacy inline table styling. | `transparent` |
| Table | `$table-border-color` | The rule colour of every `.table` and `.table-striped`. | `#dddddd` |
| Button | `$btn-primary-bg` | The fill of `.btn-primary`. Declared to `$brand-primary` rather than repeating the hex, so the two cannot drift. | `$brand-primary` |
| Button | `$btn-primary-color` | The label colour of `.btn-primary`. | `#ffffff` |
| Navbar | `$navbar-height` | The height of the header `.navbar` the stock Header widget renders. | `50px` |
| Navbar | `$navbar-default-bg` | The fill of a default `.navbar`. | `#f8f8f8` |
| Navbar | `$navbar-inverse-bg` | The fill of `.navbar-inverse`. Declare it even if the header uses the default variant, because Bootstrap derives the inverse navbar border from it. | `#222222` |
| Breakpoint | `$screen-sm-min` | The small breakpoint. Declared for completeness; **no `.col-sm-*` class is authored in this portal.** See [Responsive stance — the 1024-pixel floor](#responsive-stance--the-1024-pixel-floor). | `768px` |
| Breakpoint | `$screen-md-min` | The medium breakpoint, at which `.col-md-*` engages. | `992px` |
| Breakpoint | `$screen-lg-min` | The large breakpoint, at which `.col-lg-*` engages. | `1200px` |
| `$sp-*` namespace | `$sp-body-bg` | Declared under Surface above. Listed again here so the namespace inventory is complete. | `#f5f5f5` |
| `$sp-*` namespace | `$sp-tagline-color` | The tagline text colour in the portal chrome. | `#333333` — Bootstrap 3.3.6's `$text-color` default, which is legible against the `#f8f8f8` navbar and the `#f5f5f5` page. Declared by this theme rather than left to the platform default (`D-120`). |
| `$sp-*` namespace | `$sp-navbar-divider-color` | The divider rule inside the portal navbar. | `#e7e7e7` — the value Bootstrap 3.3.6 derives for `$navbar-default-border`, `darken($navbar-default-bg, 6.5%)`, so the divider matches the navbar edge. Declared by this theme rather than left to the platform default (`D-120`). |

**Thirty-three declarations, and no value this portal applies resolves to a release default.** The `$sp-*` namespace carries further entries beyond the three named above. This portal applies only these three, so only these three are declared. The authoritative list for a given instance is served per portal by the compiled bootstrap stylesheet; read it from that instance if a fourth entry is ever needed, and declare it here rather than in a widget.

Bootstrap's own derivation rules mean any variable **not** in the table above is computed from the ones that are, so the set above propagates consistently without being extended. `$navbar-inverse-border`, for example, is derived from `$navbar-inverse-bg`, and `$navbar-default-border` from `$navbar-default-bg`. **Declare exactly the thirty-three variables above and no others**; an extra declaration is a value the theme then owns and must maintain.

### The complete declaration block

Paste this into the theme record's **CSS variables** field exactly as it stands. It is the table above, in the same order, with nothing omitted and nothing added — **thirty-three declarations**, which is the whole of this portal's token surface. Two of them resolve to another variable rather than to a literal, deliberately, so the pair cannot drift.

```scss
// Brand
$brand-primary: #1976d2;
$brand-success: #5cb85c;
$brand-info: #5bc0de;
$brand-warning: #f0ad4e;
$brand-danger: #d9534f;

// Surface
$body-bg: #f5f5f5;
$sp-body-bg: #f5f5f5;
$panel-bg: #ffffff;
$panel-default-border: #dddddd;

// Typography
$font-family-sans-serif: 'Roboto', 'Helvetica', 'Arial', sans-serif;
$font-size-base: 14px;
$line-height-base: 1.428571429;
$headings-font-family: $font-family-sans-serif;
$headings-font-weight: 500;

// Layout
$container-lg: 1200px;
$grid-gutter-width: 30px;
$padding-base-vertical: 6px;
$padding-base-horizontal: 12px;

// Radius
$border-radius-base: 4px;
$border-radius-large: 6px;
$border-radius-small: 3px;

// Table
$table-bg: transparent;
$table-border-color: #dddddd;

// Button
$btn-primary-bg: $brand-primary;
$btn-primary-color: #ffffff;

// Navbar
$navbar-height: 50px;
$navbar-default-bg: #f8f8f8;
$navbar-inverse-bg: #222222;

// Breakpoints
$screen-sm-min: 768px;
$screen-md-min: 992px;
$screen-lg-min: 1200px;

// Service Portal namespace
$sp-tagline-color: #333333;
$sp-navbar-divider-color: #e7e7e7;
```

Three ordering rules govern the block, and each prevents a value that silently fails to apply:

1. **`$brand-primary` is declared before `$btn-primary-bg`**, and `$font-family-sans-serif` before `$headings-font-family`. A SASS variable referenced before it is declared resolves to nothing.
2. **`$sp-body-bg` repeats `#f5f5f5` as a literal rather than referencing `$body-bg`.** The `$sp-*` namespace is compiled from the platform's own partials, and a reference across that boundary is not guaranteed to resolve; a literal always does.
3. **No CSS rule appears in the block.** Only declarations. A rule placed in a variables field is duplicated once per consumer in the compiled output — see rule 2 of [Theme and variable authoring rules](#theme-and-variable-authoring-rules).

After saving the theme, confirm the values took effect by loading the portal and reading the computed `background-color` of `body`, which must be `rgb(245, 245, 245)`, and the computed `color` of a `.btn-primary`, whose background must be `rgb(25, 118, 210)`. A default-Bootstrap `#337ab7` on the button means the field did not compile; re-check that the block contains no CSS rule and no unclosed declaration.

Bootstrap derives a variable that is left undeclared from the ones that are: `$navbar-inverse-border` is computed from `$navbar-inverse-bg`, and `$text-color` from `$gray-dark`. Those derivations remain in force for every Bootstrap variable outside the thirty-three above. `$sp-tagline-color` is therefore declared as the literal `#333333` rather than as a reference to `$text-color`: `$text-color` is not declared in this field, and a field compiled ahead of Bootstrap's own variable file cannot reference it.

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

**The inclusion criteria are applied server-side, by `StartupSearchService`, and by nothing else.** Neither widget re-implements the predicate, adds a condition of its own on `active` or `headquarters_location`, or filters the returned rows in the client controller. The one call sequence permitted is the one specified under [`bst-startup-search`](#bst-startup-search) and [`bst-startup-results`](#bst-startup-results). Criterion 5 of [`../validation-checklist.md`](../validation-checklist.md) — "inclusion filter confirmed active" — is evidenced by seeding a startup that fails the criteria and confirming it is absent from these results while still visible to the administrator in the platform list view. A client-side or widget-local filter passes that walkthrough while leaving the server predicate unexercised, so it is prohibited here. The filter's content is settled at `D-029` and its single-owner placement at `D-035` in [`../../../docs/decisions/DECISION_LOG.md`](../../../docs/decisions/DECISION_LOG.md).

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

**One rectangle in the second container, at eight columns of twelve.** Author **no** second rectangle on that row: an `sp_rectangle` carrying no `sp_instance` renders an empty grid column, and this page has nothing to put in one. The four remaining columns are simply unoccupied, which is what a Bootstrap row does with a single eight-column child.

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
| 10 | `bst-startup-results` | `.btn.btn-primary` on the premium treatment | `?id=bst_account` |
| 11 | Breadcrumbs (stock) | first crumb | `?id=bst_home` |
| 12 | Stock Header | portal title | `/bst` |
| 13 | Stock Header | menu item `Home`, on every page | `?id=bst_home` |
| 14 | Stock Header | menu item `Dashboard`, on every page | `?id=bst_dashboard` |
| 15 | Stock Header | menu item `Account`, on every page | `?id=bst_account` |

**Fifteen hops, and every route has at least one incoming hop.** Hops 13 to 15 are the header-menu items built in [The header menu and its items](#the-header-menu-and-its-items); they render on every page for every one of the three scoped roles, which is what gives `bst_dashboard` and `bst_account` an incoming control rather than a typed address. Hop 10 is the premium treatment of [`bst-startup-results`](#bst-startup-results), which reaches `bst_account` for the base role from the search results themselves.

| Route | Incoming hops |
| --- | --- |
| `bst_home` | 7, 9, 11, 12, 13 |
| `bst_company` | 1, 2, 5, 6 |
| `bst_investor` | 3, 4 |
| `bst_dashboard` | 14 |
| `bst_account` | 8, 10, 15 |

**Every navigation hop in this table must be exercised through the rendered control**, never by pasting the link into the address bar. [`../validation-checklist.md`](../validation-checklist.md) criterion 5 records the same requirement for the acceptance walkthrough.

A widget reads its own route parameters from `$location` in the client controller and from `$sp` in the server script. The two forms are given under [The Angular surface available inside a widget](#the-angular-surface-available-inside-a-widget).

A page that requires a `sys_id` and receives none, or receives one that resolves to no readable record, must render an `.alert.alert-warning` carrying a plain message and a `.btn.btn-default` link back to `?id=bst_home`. It must not render an empty panel and must not throw. This applies to `bst_company` and `bst_investor`.

## Step 4 — The eight widgets

Exactly eight `sp_widget` records. Create each in the `x_bst_startuptrk` scope, with `sp_widget.servicenow` `false`, `sp_widget.public` `false` and `sp_widget.roles` empty — access is decided by the access controls in [`../access-control.md`](../access-control.md), never by a widget role list.

Every widget is specified below with the same six parts: its **name and ID**, its **option schema**, its **server script** responsibilities, its **client controller** responsibilities, its **HTML template** structure with the Bootstrap classes it uses, and its **CSS**.

### Every listener a controller registers is released on `$destroy`

**A client controller registers nothing that outlives its scope, and dereferences nothing that an expected server path leaves absent.** Three widgets register a listener, and each of the three follows the same two-part rule.

| Widget | Listener | What it is guarded on | What releases it |
| --- | --- | --- | --- |
| `bst-company-profile` | `spUtil.recordWatch` on `x_bst_startuptrk_startup` | `c.data.startup` present **and** its `sys_id` a 32-character hexadecimal value | `$scope.$on('$destroy', ...)`, plus a release before every re-subscribe |
| `bst-investor-profile` | `spUtil.recordWatch` on `x_bst_startuptrk_investor` | `c.data.investor` present **and** its `sys_id` a 32-character hexadecimal value | `$scope.$on('$destroy', ...)`, plus a release before every re-subscribe |
| `bst-startup-results` | `$rootScope.$on('bst.search.criteria', ...)` | Nothing to guard; the payload is the event argument | The deregistration function `$rootScope.$on` returns, called from `$scope.$on('$destroy', ...)` |

Both parts are load-bearing, and each fails differently.

| Part omitted | What happens |
| --- | --- |
| The guard | Every server script in this guide has an unauthorised path and a not-found path, and on both of them the record object is **never published**. `c.data.startup.sys_id` on those paths raises a client `TypeError` before the template can render the notice it was written to render, so the caller sees a blank widget instead of "Your account holds no Boston Startup Tracker role" or "That company could not be found". These are expected paths, not error paths. |
| The release | A `$rootScope` listener is bound to the root scope and is **not** removed when the widget's own scope is destroyed. Navigating between portal routes therefore accumulates one live listener per visit, each still calling `c.server.update()` on a destroyed scope. A `recordWatch` subscription re-created by a server refresh accumulates the same way when the previous handle is not released first. |

### Rules that bind all eight

1. Every server script reads through `GlideRecordSecure` and serialises through `RestResponseBuilder.serialize()`. See [Step 6](#step-6--access-control-in-every-widget-server-script). This is not optional and has no exception.
2. No widget CSS contains a literal colour, spacing, radius or font value. See [Zero hard-coded values](#zero-hard-coded-values).
3. No widget uses an extra-small or small Bootstrap column class. See [Responsive stance — the 1024-pixel floor](#responsive-stance--the-1024-pixel-floor).
4. No widget references Lucide, and no widget uses an emoji character. Icons are the platform glyph font only. See [Iconography — the platform glyph font only](#iconography--the-platform-glyph-font-only).
5. Every widget CSS selector is scoped beneath the widget's own root class, and is at most three selectors deep.
6. A Script Include is constructed by its bare class name inside the scope — `new RestResponseBuilder()`, not `new x_bst_startuptrk.RestResponseBuilder()`.
7. Every server script **assigns** the authorisation result — `data.authorised = builder.hasAnyAppRole();` — and returns immediately when it is `false`. Calling the method without assigning it leaves `data.authorised` undefined, and every template below gates its usable content on that value.
8. Every widget implements [Busy, status and focus behaviour](#busy-status-and-focus-behaviour) and, where it loads asynchronously, [Error and empty behaviour](#error-and-empty-behaviour). Neither is optional and neither has an exception.
9. Every interpolated link uses `ng-href`, never `href`. A plain `href` carrying `{{…}}` is followed with the raw braces before Angular substitutes them.
10. **A persisted external locator is bound only where it passed the application's URL allowlist on the way in, and an address is never bound as a link target.** See [External locators in a binding](#external-locators-in-a-binding).

### External locators in a binding

Six of the values these widgets bind into an `ng-href` or `ng-src` target are **external locators stored by the application**, not internal page links: `Startup.website`, `Startup.logo_url`, `Founder.linkedin_url`, `Executive.linkedin_url`, `Investor.website` and `FundingRound.source_url`. `Founder.contact_email` and `Executive.contact_email` are the two stored addresses.

**Every one of those eight values passed `RestQueryHelper.isHttpsUrl()` or `RestQueryHelper.isEmailAddress()` before it was stored, on every write path there is.** The REST create and update contract calls those two methods, and so does `IngestionMapper.coerceField()` before any staging-to-entity write, so a locator that could not be submitted through the API cannot have been written by an ingestion run either. That single allowlist is specified in [`../api-reference.md`](../api-reference.md#one-validator-both-write-paths); its effect here is that a stored locator is an absolute `https` URL with no user information before the `@` in its authority, and can therefore carry neither a `javascript:` nor a `data:` scheme nor an embedded credential.

Three rules follow for these widgets, and each names what it prevents:

1. **Bind a stored locator only through `ng-href` or `ng-src`, never through `href`, `src`, `ng-bind-html` or `$sce.trustAsResourceUrl`.** The first two are the sanitised bindings; `href` with raw braces exposes the un-substituted value, and the last two remove the sanitisation the framework applies.
2. **Never bind a stored address as a link target.** `contact_email` renders as **text**, as the People pane below does, and not as a `mailto:` target. The address allowlist admits no scheme, so a `mailto:` target would have to be assembled in the template, and an assembled target is a second construction site for a rule that has one home.
3. **Never bind a value this widget assembled from more than one stored field into a locator position.** Concatenating a stored value into a URL re-opens the scheme question the allowlist closed. Every locator bound below is a single column's value, verbatim.

**The allowlist is an input-boundary reduction, not a substitute for the framework's own output sanitisation.** Both apply, and neither is relied on alone.

### Busy, status and focus behaviour

Applies to **all eight** widgets. Two contracts: a busy state on the widget root, and — for the four widgets whose content changes after the first render — one polite status region.

**The busy state, on all eight.** Every client controller declares `c.busy`, `true` from construction until the first `data` payload has arrived and `false` thereafter, and every widget's root element carries `aria-busy="{{c.busy}}"`. A widget that later reloads from the server sets `c.busy` back to `true` for the duration of that reload. Four widgets — `bst-startup-search`, `bst-trends-kpi`, `bst-trends-charts` and `bst-premium-upsell` — never reload after their first render, so their `c.busy` transitions to `false` once and stays there.

**The status region, on the four widgets whose content changes.** `bst-startup-results`, `bst-company-profile`, `bst-investor-profile` and `bst-account-summary` each carry exactly one region of the form below, placed as the first child of the `.panel-body` so it precedes the content it describes:

```html
<div class="sr-only" role="status" aria-live="polite" aria-atomic="true">{{c.statusText()}}</div>
```

`.sr-only` is Bootstrap's own screen-reader utility, so the region is announced without occupying layout. `c.statusText()` returns exactly one string, chosen in this order — the first condition that holds wins, so a caller never hears two states at once:

| Order | Condition | Text returned |
| --- | --- | --- |
| 1 | `c.busy` is `true` | `Loading` |
| 2 | `data.error` is set | `Could not load. Use Retry to try again.` |
| 3 | the widget's primary collection is empty | the widget's own empty wording, given in its section below |
| 4 | otherwise | the widget's own loaded wording, given in its section below |

**Failure is announced as an alert, not as a status.** The visible error panel specified under [Error and empty behaviour](#error-and-empty-behaviour) carries `role="alert"`, which is announced immediately and interrupts; the polite status region carries the same fact for a caller who reaches it later.

**Focus behaviour, defined per interaction.** Only three interactions in this portal move focus, and no other interaction moves it:

| Interaction | Focus destination |
| --- | --- |
| A search is submitted from `bst-startup-search` and the results arrive on the same page | The `<h3 class="panel-title">` of `bst-startup-results`, which carries `tabindex="-1"` so it can receive programmatic focus. The caller lands on the heading that states the result count. |
| The retry control of any error panel succeeds | The retrying widget's own **primary heading**, which carries `tabindex="-1"` for that purpose: the `.panel-title` on `bst-startup-results` and `bst-account-summary`, and the `.media-heading` carrying the record name on `bst-company-profile` and `bst-investor-profile`. |
| A tab is selected on `bst-company-profile` | The selected tab control itself, per the roving-`tabindex` contract under [The tab contract](#the-tab-contract). Focus never jumps into the panel. |

A control that disappears while it holds focus — the **Retry** button when a retry succeeds, or the **Next** pager button when it becomes the last page — must hand focus to the destination in the table above before it is removed from the document, so focus is never lost to the document body.

### Error and empty behaviour

Applies to the four widgets that load asynchronously: `bst-startup-results`, `bst-company-profile`, `bst-investor-profile` and `bst-account-summary`.

**Every server call is handled on both outcomes.** A client controller that calls `c.server.update()` attaches a success handler **and** a rejection handler, and clears the busy flag from a single helper called by both:

```javascript
c.load = function () {
    var settled = function () {
        c.busy = false;
    };

    c.busy = true;
    c.data.error = '';

    return c.server.update().then(function () {
        c.data.error = '';
        settled();
    }, function () {
        c.data.error = 'Could not load. Use Retry to try again.';
        settled();
    });
};

c.retry = function () {
    c.load();
};
```

Three properties of that shape are what the contract requires, and each closes a way for the interface to stall or mislead:

- **The rejection handler exists**, so a rejected promise sets `data.error` rather than passing silently.
- **`c.busy` is cleared on both outcomes**, by the one `settled` helper that the success handler and the rejection handler each call, so it is cleared on rejection as well as on success and the progress indicator cannot hang. Both handlers are present, so there is no third path out of the call.
- **`data.error` is cleared at the start of every attempt**, so a successful retry removes the error panel rather than leaving it beside fresh content.

**Why a helper rather than a `finally` handler.** `finally` is a reserved word in the ECMAScript 3 syntax the platform's server-side interpreter accepts, so a promise-`finally` handler has to be reached through bracket notation to parse at all. One helper called from both handlers gives the same guarantee — the busy flag is cleared exactly once on either outcome, in one place — with no reserved word and no bracket notation, and it reads the same on the server and in the client controller.

**The visible error panel**, rendered by each of the four templates immediately after its status region:

```html
<div class="alert alert-danger" role="alert" ng-if="data.error">
  <span class="icon-cross-circle" aria-hidden="true">&nbsp;</span>
  <span>{{data.error}}</span>
  <button type="button" class="btn btn-default" ng-click="c.retry()">Retry</button>
</div>
```

**Every collection renders an explicit empty state.** A collection that is empty renders a short `.alert.alert-info`, or a single `.list-group-item` where the collection is a list inside a panel, stating in plain words that there is nothing to show. **No collection renders as nothing at all**, and no count of `0` stands alone as the whole of the answer. The wording for each is given in the widget's own section.

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
| `results_page` | string | `bst_home` | The `sp_page.id` that carries `bst-startup-results`. It decides how a submitted search is delivered: see client-controller steps 3 and 4. |

#### Server script

1. Construct `var builder = new RestResponseBuilder();` and assign `data.authorised = builder.hasAnyAppRole();`. When `data.authorised` is `false`, set nothing else and return; the template then renders the not-entitled alert. **Assign the result — do not merely call the method.** A caller holding one of the three scoped roles must arrive with `data.authorised` `true`, or every gated region of the template stays hidden from a legitimate user.
2. Publish the **closed** industry choice list to the client as `data.industries`, transcribed exactly from `x_bst_startuptrk_startup.industry`: `Fintech`, `Healthtech`, `SaaS`, `Consumer`, `Deeptech`, `Other`. Do not read it from a second source and do not add a value. The same six values are the list `StartupSearchService` validates against.
3. Seed the three filter values from the URL so a shared link reproduces a search: `data.criteria = { name: $sp.getParameter('name') || '', industry: $sp.getParameter('industry') || '', location: $sp.getParameter('location') || '' }`.
4. Publish `data.appliesInclusion = new StartupSearchService().appliesInclusion()`, so the template can render the "showing Boston and Cambridge startups only" note to a non-administrative caller. This is a display note; it never becomes a client-side filter.
5. Publish `data.currentPage = $sp.getParameter('id') || 'bst_home'`, the page this instance is rendering on. Client-controller step 3 compares it with `options.results_page`.
6. Read **no** record. This widget issues no query.

#### Client controller

1. Bind the three inputs to `c.data.criteria.name`, `c.data.criteria.industry` and `c.data.criteria.location` with `ng-model`.
2. On submit, and on clear, normalise each value by trimming it.
3. **Deliver the criteria according to `options.results_page`.** The option is read on every submit and on every clear, and decides between two paths:
   - **Same page** — `options.results_page` equals `data.currentPage`, which is the shipped configuration, where both widgets sit on `bst_home`. Broadcast the criteria on the root scope with `$rootScope.$broadcast('bst.search.criteria', c.data.criteria)`, and mirror them into the URL with `$location.search()` on the same three parameter names, so the search is linkable and the widget rehydrates on reload. `bst-startup-results` listens for that event.
   - **Another page** — `options.results_page` names a different page. Navigate to it, carrying the criteria as query parameters, with `$location.url('?id=' + options.results_page + <the three parameters>)`. The results widget on the destination page then seeds itself from those parameters through `$sp.getParameter()`, which is the same rehydration path the same-page form uses on reload. Broadcast nothing: the destination is a fresh page load and no listener survives it.
   - **Empty or unknown** — `options.results_page` is empty, or names no `sp_page` record. Fall back to the same-page path. Never navigate to an unresolvable page.
4. Declare `c.busy` per [Busy, status and focus behaviour](#busy-status-and-focus-behaviour). This widget issues no server call after its first render, so `c.busy` becomes `false` when the first payload arrives and stays there. It carries **no** status region: the submission is announced by `bst-startup-results`, which owns both the status region and the focus move for the result set.
5. Reject nothing and filter nothing. The controller never evaluates `active` or `headquarters_location`; the predicate lives in `StartupSearchService`.
6. Guard the industry input against a value outside `c.data.industries` by rendering it as a `<select>` over that list rather than as free text.

#### HTML template

```html
<div class="bst-search panel panel-default" aria-busy="{{c.busy}}">
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

Where a plain paginated record list is all that is wanted, use the stock **Data Table from Instance Definition** widget instead of this one and set its `table`, `filter` and column options — pagination is native to it. Build this widget only for the result card specified below, which renders a company logo image and a row of `.label` tags; the stock data table has no column type for either. That is rung one of [the graceful degradation ladder](#the-graceful-degradation-ladder) applied to this surface, and the ladder is settled at `D-060` in [`../../../docs/decisions/DECISION_LOG.md`](../../../docs/decisions/DECISION_LOG.md).

#### Option schema

| Option | Type | Default | Purpose |
| --- | --- | --- | --- |
| `title` | string | `Startups` | The `.panel-title` text. |
| `page_size` | integer | *empty* | The page size. **Leave empty to inherit the REST default.** See the page-size note below. |
| `detail_page` | string | `bst_company` | The `sp_page.id` a result links to. |
| `show_logo` | boolean | `true` | Renders `logo_url` as the media object. |

**The page size is shared with the REST layer.** When `page_size` is empty the widget reads `x_bst_startuptrk.rest.default_limit` — shipped value `20` — through `AppProperties.getDefaultLimit()`, and it clamps any supplied value to `x_bst_startuptrk.rest.max_limit` — shipped value `50` — through `AppProperties.getMaxLimit()`. Those are the same two properties `RestQueryHelper.getLimit()` reads for the API, documented in [`../api-reference.md`](../api-reference.md), **so changing either property changes the page size on both surfaces at once.** Do not hard-code `20` or `50` in the widget.

#### Server script

1. Construct `var builder = new RestResponseBuilder();` and assign `data.authorised = builder.hasAnyAppRole();`. When `data.authorised` is `false`, return immediately and publish nothing further. **Assign the result — do not merely call the method.**
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
data.count_denied = counted.denied === true;
```

6. Publish `data.gated = { total_funding_usd: false, institutional_funding_last_5yrs: false }` and set a member to `true` when at least one returned row omitted that key, so the template knows to render the upsell note rather than a blank cell.
7. `data.total_count` must be the count produced by `countState()` under the **same** plan. Never count with a second, differently-built query, and never report `data.result.length` as the total.
8. `countState()` answers `{ total, denied }`. `total` is the **exact** cardinality of the filtered set at any magnitude — there is no counting ceiling and no truncation, so the template renders the figure plainly and never as a minimum. `denied` is `true` when the caller failed the table-level read check, in which case `total` is `0` and **the total must not be rendered at all**: publish `data.count_denied` and let the template show the no-role notice instead of a count of zero, which would otherwise tell a caller that a set it may not read is empty. The pager arithmetic in the client controller depends on the total being exact: a floor would let `c.next()` advance past the last page. There is no capped state, no `total_count_capped` member and no "more than" rendering.

The plan is built once and handed to both `countState()` and `search()`, which is what keeps the total in agreement with the page contents. `../api-reference.md` states the same invariant for the `GET /startups` list operation, and records why an exact aggregate total is correct here — every role that can read these tables can read every row of them.

#### Client controller

1. Implement `c.load()` and `c.retry()` exactly as [Error and empty behaviour](#error-and-empty-behaviour) specifies. Every server call in the steps below goes through `c.load()`, so no call is made without both handlers and the `finally` clause attached.
2. Listen for the search event: `$rootScope.$on('bst.search.criteria', function (event, criteria) { c.data.criteria = criteria; c.data.offset = 0; c.load(); })`.

   **Deregister that listener on `$destroy`.** `$rootScope.$on` binds to the root scope, which outlives this widget's scope, and it returns the deregistration function:

```javascript
var stopListening = $rootScope.$on('bst.search.criteria', function (event, criteria) {
    c.data.criteria = criteria;
    c.data.offset = 0;
    c.load();
});

$scope.$on('$destroy', function () {
    stopListening();
});

   Without the deregistration every visit to `bst_home` leaves one more live listener on the root scope, each calling `c.load()` on a scope that no longer renders.

3. Expose `c.next()` and `c.previous()`, which adjust `c.data.offset` by `c.data.limit`, clamp it to the range `0` to `c.data.total_count`, and call `c.load()`.
4. Expose `c.hasNext()` and `c.hasPrevious()` for the pager's `ng-disabled` bindings. `c.hasNext()` is `false` when `c.data.result.length` is `0`, so an empty result set offers no next page.
5. Expose the **zero-safe pager range**. The pager must never read "1 to 0 of 0":
   - `c.rangeStart()` returns `c.data.offset + 1` when `c.data.result.length` is greater than `0`, and `0` otherwise.
   - `c.rangeEnd()` returns `c.data.offset + c.data.result.length`.
   - `c.hasRange()` returns `true` only when `c.data.result.length` is greater than `0`. The template renders the range sentence only under `c.hasRange()` and renders `No results to show` otherwise.
6. Expose `c.isGated(item, field)`, `true` when `item[field] === undefined` **and** `c.data.gated[field]` is `true`. This is the single test the template uses to decide between a value and the `Premium` marker; it is specified under [The premium treatment in the result list](#the-premium-treatment-in-the-result-list).
7. Declare `c.busy` and `c.statusText()` per [Busy, status and focus behaviour](#busy-status-and-focus-behaviour). This widget's status wording is:
   - empty — `No startup matches those criteria.`
   - loaded — `{{c.data.result.length}} of {{c.data.total_count}} startups shown.` The total is exact, so it is rendered as written; there is no capped variant to present.
8. After a load that began with a search event or a retry, move focus to the `.panel-title` of this widget, per the focus table in [Busy, status and focus behaviour](#busy-status-and-focus-behaviour). Do not move focus after a pager step: the caller's focus is already on the pager button they activated, and it survives the reload.
9. Never filter, sort or re-order `c.data.result` in the client. Ordering is `name` then `sys_id`, applied by `StartupSearchService.search()`.

#### HTML template

```html
<div class="bst-results panel panel-default" aria-busy="{{c.busy}}">
  <div class="panel-heading">
    <h3 class="panel-title" tabindex="-1">
      {{::options.title}}
      <span class="text-muted" ng-if="data.authorised &amp;&amp; !data.count_denied">
        {{data.total_count}} matching
      </span>
    </h3>
  </div>
  <div class="panel-body">
    <div class="sr-only" role="status" aria-live="polite" aria-atomic="true">{{c.statusText()}}</div>

    <div class="alert alert-warning" ng-if="!data.authorised">
      <span>Your account holds no Boston Startup Tracker role.</span>
    </div>

    <div class="alert alert-danger" role="alert" ng-if="data.error">
      <span class="icon-cross-circle" aria-hidden="true">&nbsp;</span>
      <span>{{data.error}}</span>
      <button type="button" class="btn btn-default" ng-click="c.retry()">Retry</button>
    </div>

    <div class="progress" ng-if="c.busy">
      <div class="progress-bar progress-bar-striped active" role="progressbar"
           aria-label="Loading startups" aria-valuemin="0" aria-valuemax="100"
           aria-valuetext="Loading"></div>
    </div>

    <div class="alert alert-info"
         ng-if="data.authorised &amp;&amp; !c.busy &amp;&amp; !data.error &amp;&amp; data.result.length === 0">
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
              <a ng-href="?id={{::options.detail_page}}&amp;sys_id={{::item.sys_id}}">{{::item.name}}</a>
            </h4>
            <p>{{::item.description}}</p>
            <p>
              <span class="label label-primary" ng-if="::item.funding_stage">{{::item.funding_stage}}</span>
              <span class="label label-default" ng-if="::item.industry">{{::item.industry}}</span>
              <span class="label label-default" ng-if="::item.employee_count_range">{{::item.employee_count_range}}</span>
            </p>
            <ul class="list-group">
              <li class="list-group-item">
                <span class="icon-map" aria-hidden="true">&nbsp;</span>{{::item.headquarters_location}}
              </li>
              <li class="list-group-item" ng-if="item.total_funding_usd !== undefined">
                Total funding {{item.total_funding_usd}}
              </li>
              <li class="list-group-item" ng-if="c.isGated(item, 'total_funding_usd')">
                Total funding
                <span class="label label-info">Premium</span>
              </li>
              <li class="list-group-item" ng-if="item.institutional_funding_last_5yrs !== undefined">
                Institutional funding in the last five years
                <span class="label label-default">{{item.institutional_funding_last_5yrs ? 'Yes' : 'No'}}</span>
              </li>
              <li class="list-group-item" ng-if="c.isGated(item, 'institutional_funding_last_5yrs')">
                Institutional funding in the last five years
                <span class="label label-info">Premium</span>
              </li>
            </ul>
            <a class="btn btn-default"
               ng-href="?id={{::options.detail_page}}&amp;sys_id={{::item.sys_id}}">View profile</a>
          </div>
        </div>
      </div>
    </div>

    <div class="alert alert-info bst-results-upsell" role="alert"
         ng-if="data.authorised &amp;&amp; data.gatedAny">
      <h4>
        <span class="icon-locked" aria-hidden="true">&nbsp;</span>Premium fields are hidden in these results
      </h4>
      <p>
        Total funding and the institutional-funding marker are reserved for the premium tier.
        Your account reads every other column on this page.
      </p>
      <a class="btn btn-primary" ng-href="?id={{::data.upsellPage}}">See your entitlements</a>
    </div>

    <div class="bst-results-pager" ng-if="data.authorised">
      <button type="button" class="btn btn-default" ng-click="c.previous()"
              ng-disabled="!c.hasPrevious()">Previous</button>
      <button type="button" class="btn btn-default" ng-click="c.next()"
              ng-disabled="!c.hasNext()">Next</button>
      <span class="text-muted" ng-if="c.hasRange()">
        Showing {{c.rangeStart()}} to {{c.rangeEnd()}} of {{data.total_count}}
      </span>
      <span class="text-muted" ng-if="!c.hasRange()">No results to show</span>
    </div>
  </div>
</div>
```

`ng-if="item.total_funding_usd !== undefined"` is the omission test. A denied premium field has **no key** on the serialised object, so `undefined` is the correct comparison; do not test for an empty string and do not test for `null`, because a readable-but-empty currency column legitimately serialises as `null`.

##### The premium treatment in the result list

Two treatments, and both are driven by `data.gated`, which the server publishes at step 6. Without them an omitted key would leave the caller with no indication that anything was withheld, which is the one outcome the field-level access controls must not produce.

**Field level — the `Premium` marker.** Each of the two gated columns has a pair of rows in the `.list-group`: one rendered when the key is present, one rendered when `c.isGated(item, <field>)` is `true`. The second renders the column's label beside a `.label.label-info` reading `Premium`. The two conditions are mutually exclusive, so exactly one row renders per column per card. **Never render a blank cell, an empty string or a zero in place of a withheld value.**

`c.isGated()` tests the omission **and** `data.gated`, so a column that is simply not populated on a record — readable, but empty — does not masquerade as a paywalled one.

**Surface level — the gap G5 treatment.** When `data.gatedAny` is `true`, the list is followed by one `.alert.alert-info` carrying a `.btn.btn-primary` to `bst_account`, which is the treatment [`../gaps-and-flags.md`](../gaps-and-flags.md) records against gap **G5**. It renders **once** per result set, never once per card.

This widget renders that treatment **inline rather than embedding `bst-premium-upsell`**. The partial has exactly three hosts — `bst-company-profile`, `bst-investor-profile` and `bst-account-summary` — and this widget is not one of them; see the [widget roll-up](#widget-roll-up). The decision is recorded in [`../../../docs/decisions/DECISION_LOG.md`](../../../docs/decisions/DECISION_LOG.md).

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

.bst-results .bst-results-upsell {
    margin-top: $grid-gutter-width;
    border-radius: $border-radius-base;
}

.bst-results .bst-results-upsell .btn {
    margin-top: $padding-base-vertical;
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
| `funding_limit` | integer | `25` | Maximum funding rounds rendered in the Funding pane. |
| `people_limit` | integer | `50` | Maximum founders, and separately maximum executives, rendered in the People pane. |
| `jobs_limit` | integer | `25` | Maximum job postings rendered in the Jobs pane. |
| `news_limit` | integer | `10` | Maximum news articles rendered in the News pane. |

**Every one of the five child collections has a limit, and none is optional.** A profile page renders one startup, and the number of children that startup has is data the page does not control: a company with two thousand job postings or four hundred news articles would otherwise be read, serialised and shipped to the browser in full on every render, by any caller who knows the record identifier. The limits are options rather than constants so an administrator can raise one for a deliberate purpose, and each one bounds a read that is otherwise unbounded.

#### Server script

1. Construct `var builder = new RestResponseBuilder();` and assign `data.authorised = builder.hasAnyAppRole();`. When `data.authorised` is `false`, return immediately and publish nothing further. **Assign the result — do not merely call the method.**
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

4. Load the five child collections, each with its own `GlideRecordSecure`, its own `serialize()` field list, its own order, its own limit, and `addQuery('startup', sysId)`.

| Pane | Table | Fields serialised | Order | Limit |
| --- | --- | --- | --- | --- |
| Funding | `x_bst_startuptrk_fundinground` | `startup`, `round_type`, `amount_usd`, `round_date`, `lead_investor`, `valuation_usd`, `source_url` | `round_date` descending, `sys_id` ascending | `options.funding_limit` |
| People — founders | `x_bst_startuptrk_founder` | `name`, `startup`, `title`, `bio`, `linkedin_url`, `contact_email` | `name` ascending, `sys_id` ascending | `options.people_limit` |
| People — executives | `x_bst_startuptrk_executive` | `name`, `startup`, `title`, `bio`, `linkedin_url`, `contact_email` | `name` ascending, `sys_id` ascending | `options.people_limit` |
| Jobs | `x_bst_startuptrk_jobposting` | `startup`, `title`, `department`, `location`, `remote_type`, `seniority`, `posted_date`, `url`, `active` | `posted_date` descending, `sys_id` ascending | `options.jobs_limit` |
| News | `x_bst_startuptrk_newsarticle` | `startup`, `title`, `source`, `url`, `published_date`, `summary` | `published_date` descending, `sys_id` ascending | `options.news_limit` |

Write the five reads through one helper so no collection can be added later without a limit and a total:

```javascript
// Reads one bounded child collection and publishes, alongside the rows, the exact
// number of rows that exist. The count is one COUNT aggregate under the same
// condition as the read, so "showing 25 of 128" is 25 rendered rows and a true 128.
function childCollection(table, fields, orderBy, descending, limit) {
    var bound = parseInt(limit, 10);
    if (isNaN(bound) || bound < 1) {
        bound = 25;
    }
    var child = new GlideRecordSecure(table);
    child.addQuery('startup', sysId);
    if (descending) {
        child.orderByDesc(orderBy);
    } else {
        child.orderBy(orderBy);
    }
    child.orderBy('sys_id');            // ties broken deterministically
    child.setLimit(bound);
    child.query();

    var rows = [];
    while (child.next()) {
        rows.push(builder.serialize(child, fields));
    }

    var total = builder.countWith(table, function (query) {
        query.addQuery('startup', sysId);   // the SAME condition as the read
    });

    return {
        rows: rows,
        limit: bound,
        total: total,
        truncated: total > rows.length
    };
}
```

**The secondary `sys_id` order is what makes a limit honest.** `round_date`, `name` and `posted_date` all admit ties, and a limit applied to an order with ties returns an arbitrary subset of the tied rows — which can differ between two renders of the same page. Adding `sys_id` makes the boundary deterministic, so "the twenty-five most recent rounds" is the same twenty-five every time.

**Each collection publishes four members**, and the template must use all four: `rows` to render, `total` for the "showing N of M" caption, `limit` for the caption's ceiling, and `truncated` to decide whether the caption and the "open the full list" link appear at all. A pane that renders `rows` without stating `total` tells the reader that a company has twenty-five job postings when it has two hundred, which is a wrong answer rather than a truncated one.

**The cost is two queries per collection** — one bounded read and one `COUNT` aggregate — so ten queries for the five panes, whatever the size of the company. Before the limits, one profile could read every child row of the largest company in the table on every render.

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

8. Publish `data.tabs` as the five pane descriptors in order, so the tab strip is data-driven and cannot drift from the pane list: `overview` / **Overview**, `funding` / **Funding**, `people` / **People**, `jobs` / **Jobs**, `news` / **News**. Give each descriptor the `total` of the collection behind it, so the tab label can carry the true count — **People** carries the sum of the founders and executives totals — and a reader sees the size of a pane before opening it.
9. Publish every one of the **five collections** as an array, empty rather than absent when nothing matched: `data.rounds`, `data.founders`, `data.executives`, `data.jobs` and `data.news`. A template that has to distinguish "no rows" from "key missing" cannot render a reliable empty state, so publish the array unconditionally.

#### Client controller

1. Implement `c.load()` and `c.retry()` exactly as [Error and empty behaviour](#error-and-empty-behaviour) specifies. Every server call below goes through `c.load()`.
2. Initialise `c.activeTab` from `options.default_tab`, falling back to `overview` when the option names no pane.
3. Implement the whole of [The tab contract](#the-tab-contract) — `c.select(tabId)`, `c.isActive(tabId)`, `c.tabIndex(tabId)`, `c.tabId(tabId)`, `c.panelId(tabId)` and `c.onTabKey($event, tabId)`.
4. Read the record identifier from `$location.search().sys_id` when a client-side refresh is needed, and call `c.load()`.
5. Do not fetch data per tab. All five panes arrive in one server round trip.
6. **Watch the record only when there is a record to watch, and release the watch on `$destroy`.** `data.startup` is absent on both expected non-render paths — the unauthorised path of server-script item 1 and the not-found path of item 2 — so an unguarded `c.data.startup.sys_id` raises a `TypeError` on exactly the two paths the template handles. Guard the object and its identifier, keep the handle `spUtil.recordWatch` returns, and release it:

```javascript
var ID32 = /^[0-9a-f]{32}$/;
var watch = null;

function releaseWatch() {
    if (!watch) {
        return;
    }
    if (typeof watch.unsubscribe === 'function') {
        watch.unsubscribe();
    } else if (typeof watch === 'function') {
        watch();
    }
    watch = null;
}

function startWatch() {
    releaseWatch();
    var record = c.data && c.data.startup;
    if (!record || !ID32.test('' + record.sys_id)) {
        return;
    }
    watch = spUtil.recordWatch($scope, 'x_bst_startuptrk_startup', 'sys_id=' + record.sys_id);
}

startWatch();
$scope.$on('$destroy', releaseWatch);
```

   `startWatch()` runs once at controller initialisation and again from the promise callback of every `c.load()`, and it releases the previous handle before taking a new one, so a refresh cannot leave two subscriptions on one record and a refresh that stops resolving a record leaves none. `$scope.$on('$destroy', releaseWatch)` is registered unconditionally, so it is correct whether or not a watch was ever started. `releaseWatch()` tolerates either handle form the platform returns and is a no-op when there is nothing to release. The rule is stated once under [Every listener a controller registers is released on `$destroy`](#every-listener-a-controller-registers-is-released-on-destroy).
7. Declare `c.busy` and `c.statusText()` per [Busy, status and focus behaviour](#busy-status-and-focus-behaviour). This widget's status wording is:
   - empty — `No related records are recorded for this company.`, used when all five collections are empty.
   - loaded — `{{c.data.startup.name}} loaded. {{c.data.rounds.length}} funding rounds, {{c.data.founders.length + c.data.executives.length}} people, {{c.data.jobs.length}} open roles, {{c.data.news.length}} articles.`
8. Expose `c.isEmpty(collection)`, returning `true` when the named array has no entries, used by the five empty states in the template.

##### The tab contract

The five panes are a WAI-ARIA tab set, built on Bootstrap's `.nav.nav-tabs` and `.tab-content` classes. The classes supply the appearance; the attributes and the key handling below supply the behaviour, and without them the strip is a row of links that a keyboard or screen-reader caller cannot operate as tabs.

**Identifiers.** Every control and every pane needs a stable, unique `id`, because the two reference each other. Derive both from the pane identifier, and include the record identifier so two profiles rendered in one document cannot collide:

- `c.tabId(tabId)` returns `'bst-company-tab-' + tabId + '-' + c.data.startup.sys_id`.
- `c.panelId(tabId)` returns `'bst-company-panel-' + tabId + '-' + c.data.startup.sys_id`.

**Attributes.** The strip is a single `role="tablist"`. Each control is an `<a role="tab">` carrying `id="{{c.tabId(tab.id)}}"`, `aria-controls="{{c.panelId(tab.id)}}"`, `aria-selected="{{c.isActive(tab.id)}}"` and `tabindex="{{c.tabIndex(tab.id)}}"`. Each pane is a `<div role="tabpanel">` carrying `id="{{c.panelId(tab.id)}}"` and `aria-labelledby="{{c.tabId(tab.id)}}"`. The `<li>` wrapper keeps `role="presentation"`, so the list structure is not announced over the tab structure.

**Roving `tabindex`.** `c.tabIndex(tabId)` returns `0` for the selected tab and `-1` for every other. Exactly one control is therefore in the tab order, and Tab moves out of the strip rather than through it, which is the behaviour the pattern requires.

**Keys.** `c.onTabKey($event, tabId)` is bound with `ng-keydown` on every control and handles exactly these keys, calling `c.select()` on the resolved pane and then moving focus to that pane's control by its `c.tabId()` value:

| Key | Behaviour |
| --- | --- |
| `ArrowRight` | Select the next pane; wrap from `news` to `overview`. |
| `ArrowLeft` | Select the previous pane; wrap from `overview` to `news`. |
| `Home` | Select `overview`. |
| `End` | Select `news`. |
| `Enter`, `Space` | Select the focused pane. The control is an anchor, so `Enter` already activates it; handle `Space` explicitly. |

Every one of those keys calls `$event.preventDefault()`, so `ArrowLeft` and `ArrowRight` do not also scroll the page and `Space` does not page down. No other key is handled: `ArrowUp`, `ArrowDown` and `Tab` keep their default behaviour, because this strip is horizontal and automatic activation is what the pattern prescribes for a tab set whose panes are already loaded.

**Selection follows focus.** All five panes arrive in one server round trip, so selecting a pane costs nothing and the arrow keys select as they move. Focus stays on the strip; it never jumps into the pane.

#### HTML template

```html
<div class="bst-company" aria-busy="{{c.busy}}">
  <div class="sr-only" role="status" aria-live="polite" aria-atomic="true">{{c.statusText()}}</div>

  <div class="alert alert-warning" ng-if="!data.authorised">
    <span>Your account holds no Boston Startup Tracker role.</span>
  </div>

  <div class="alert alert-warning" ng-if="data.notFound">
    <span>That company could not be found.</span>
    <a class="btn btn-default" ng-href="?id=bst_home">Back to search</a>
  </div>

  <div class="alert alert-danger" role="alert" ng-if="data.error">
    <span class="icon-cross-circle" aria-hidden="true">&nbsp;</span>
    <span>{{data.error}}</span>
    <button type="button" class="btn btn-default" ng-click="c.retry()">Retry</button>
  </div>

  <div class="progress" ng-if="c.busy">
    <div class="progress-bar progress-bar-striped active" role="progressbar"
         aria-label="Loading company profile" aria-valuemin="0" aria-valuemax="100"
         aria-valuetext="Loading"></div>
  </div>

  <div ng-if="data.authorised &amp;&amp; !data.notFound &amp;&amp; !data.error">
    <div class="panel panel-default">
      <div class="panel-body">
        <div class="media">
          <div class="media-left" ng-if="::data.startup.logo_url">
            <img class="media-object bst-company-logo" ng-src="{{::data.startup.logo_url}}" alt="" />
          </div>
          <div class="media-body">
            <h2 class="media-heading" tabindex="-1">{{::data.startup.name}}</h2>
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
        <a href
           role="tab"
           id="{{c.tabId(tab.id)}}"
           aria-controls="{{c.panelId(tab.id)}}"
           aria-selected="{{c.isActive(tab.id)}}"
           tabindex="{{c.tabIndex(tab.id)}}"
           ng-click="c.select(tab.id)"
           ng-keydown="c.onTabKey($event, tab.id)">{{::tab.label}}</a>
      </li>
    </ul>

    <div class="tab-content">
      <div class="tab-pane" role="tabpanel"
           id="{{c.panelId('overview')}}" aria-labelledby="{{c.tabId('overview')}}"
           ng-class="{active: c.isActive('overview')}">
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

      <div class="tab-pane" role="tabpanel"
           id="{{c.panelId('funding')}}" aria-labelledby="{{c.tabId('funding')}}"
           ng-class="{active: c.isActive('funding')}">
        <div class="alert alert-info" ng-if="c.isEmpty('rounds')">
          <span>No funding round is recorded for this company.</span>
        </div>
        <div class="table-responsive" ng-if="!c.isEmpty('rounds')">
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
                <td ng-if="round.amount_usd === undefined"><span class="label label-info">Premium</span></td>
                <td ng-if="round.valuation_usd !== undefined">{{round.valuation_usd}}</td>
                <td ng-if="round.valuation_usd === undefined"><span class="label label-info">Premium</span></td>
                <td>
                  <a ng-if="::round.lead_investor"
                     ng-href="?id={{::options.investor_page}}&amp;sys_id={{::round.lead_investor.value}}">{{::round.lead_investor.display_value}}</a>
                </td>
                <td>
                  <a class="label label-default" ng-repeat="investor in ::round.participating_investors"
                     ng-href="?id={{::options.investor_page}}&amp;sys_id={{::investor.value}}">{{::investor.display_value}}</a>
                </td>
                <td><a ng-href="{{::round.source_url}}" ng-if="::round.source_url">Source</a></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="tab-pane" role="tabpanel"
           id="{{c.panelId('people')}}" aria-labelledby="{{c.tabId('people')}}"
           ng-class="{active: c.isActive('people')}">
        <div class="row">
          <div class="col-md-6 col-lg-6">
            <div class="panel panel-default">
              <div class="panel-heading"><h3 class="panel-title">Founders</h3></div>
              <ul class="list-group">
                <li class="list-group-item" ng-if="c.isEmpty('founders')">
                  No founder is recorded for this company.
                </li>
                <li class="list-group-item" ng-repeat="person in data.founders track by person.sys_id">
                  <strong>{{::person.name}}</strong>
                  <span class="label label-default" ng-if="::person.title">{{::person.title}}</span>
                  <p>{{::person.bio}}</p>
                  <a ng-href="{{::person.linkedin_url}}" ng-if="::person.linkedin_url">
                    <span class="icon-user" aria-hidden="true">&nbsp;</span>LinkedIn
                  </a>
                  <span ng-if="person.contact_email !== undefined">{{person.contact_email}}</span>
                  <span class="label label-info" ng-if="person.contact_email === undefined">Premium</span>
                </li>
              </ul>
            </div>
          </div>
          <div class="col-md-6 col-lg-6">
            <div class="panel panel-default">
              <div class="panel-heading"><h3 class="panel-title">Executives</h3></div>
              <ul class="list-group">
                <li class="list-group-item" ng-if="c.isEmpty('executives')">
                  No executive is recorded for this company.
                </li>
                <li class="list-group-item" ng-repeat="person in data.executives track by person.sys_id">
                  <strong>{{::person.name}}</strong>
                  <span class="label label-default" ng-if="::person.title">{{::person.title}}</span>
                  <p>{{::person.bio}}</p>
                  <a ng-href="{{::person.linkedin_url}}" ng-if="::person.linkedin_url">
                    <span class="icon-user" aria-hidden="true">&nbsp;</span>LinkedIn
                  </a>
                  <span ng-if="person.contact_email !== undefined">{{person.contact_email}}</span>
                  <span class="label label-info" ng-if="person.contact_email === undefined">Premium</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      <div class="tab-pane" role="tabpanel"
           id="{{c.panelId('jobs')}}" aria-labelledby="{{c.tabId('jobs')}}"
           ng-class="{active: c.isActive('jobs')}">
        <div class="alert alert-info" ng-if="c.isEmpty('jobs')">
          <span>No open role is recorded for this company.</span>
        </div>
        <div class="table-responsive" ng-if="!c.isEmpty('jobs')">
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

      <div class="tab-pane" role="tabpanel"
           id="{{c.panelId('news')}}" aria-labelledby="{{c.tabId('news')}}"
           ng-class="{active: c.isActive('news')}">
        <ul class="list-group">
          <li class="list-group-item" ng-if="c.isEmpty('news')">
            No news article is recorded for this company.
          </li>
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

1. Construct `var builder = new RestResponseBuilder();` and assign `data.authorised = builder.hasAnyAppRole();`. When `data.authorised` is `false`, return immediately and publish nothing further. **Assign the result — do not merely call the method.**
2. Read `$sp.getParameter('sys_id')`, validate the 32-character hexadecimal form, and open `x_bst_startuptrk_investor` with `GlideRecordSecure`. When the record does not resolve, set `data.notFound` to `true` and return.
3. Serialise the investor with `builder.serialize(investor, ['name', 'type', 'focus_areas', 'website', 'aum_usd', 'portfolio_count'])`. `portfolio_count` is a stored, read-only integer maintained by `InvestorPortfolioService`; read it, never recompute it in the widget.
4. Split `focus_areas` on the comma into an array for the `.label` chips. It is a multi-choice column and arrives as a comma-separated string.
5. Build the **rounds led** set: `GlideRecordSecure` on `x_bst_startuptrk_fundinground` with `addQuery('lead_investor', sysId)`, ordered by `round_date` descending then `sys_id`, `setLimit(options.rounds_limit)`, serialised with `['startup', 'round_type', 'amount_usd', 'round_date', 'valuation_usd', 'source_url']`. Publish its exact total from `builder.countWith('x_bst_startuptrk_fundinground', function (q) { q.addQuery('lead_investor', sysId); })`.
6. Build the **rounds participated** set in two bounded reads. The join table is authoritative for participation; do not read the derived `participating_investors` column.

```javascript
var roundsCap = bound(options.rounds_limit, 50);

// (a) the join rows for this investor, BOUNDED and deterministically ordered
var link = new GlideRecordSecure('x_bst_startuptrk_m2m_round_investor');
link.addQuery('investor', sysId);
link.orderByDesc('sys_id');
link.setLimit(roundsCap);
link.query();

var roundIds = [];
while (link.next()) {
    roundIds.push(String(link.getValue('funding_round')));
}

// (b) the exact number of join rows, whatever the cap took
var participatedTotal = builder.countWith('x_bst_startuptrk_m2m_round_investor',
    function (query) {
        query.addQuery('investor', sysId);
    });

// (c) the rounds themselves, one read for the whole set
var participated = [];
if (roundIds.length !== 0) {
    var rounds = new GlideRecordSecure('x_bst_startuptrk_fundinground');
    rounds.addQuery('sys_id', 'IN', roundIds.join(','));
    rounds.orderByDesc('round_date');
    rounds.orderBy('sys_id');
    rounds.query();
    while (rounds.next()) {
        participated.push(builder.serialize(rounds, roundFields));
    }
}
```

**The join read must carry the limit, not just the round read.** An investor that has participated in three thousand rounds would otherwise produce a three-thousand-element identifier array and an `IN` condition of that length — the read of the rounds is bounded by the array, so an unbounded array is an unbounded read wearing a bound. Capping the join read caps everything downstream of it. `participatedTotal` is what tells the reader the list is a window onto something larger, and it comes from a `COUNT` aggregate rather than from the array's length.

7. Build the **portfolio** set from the two round sets already read, bounded, and never by widening the query:

```javascript
var seen = {};
var startupIds = [];
led.concat(participated).forEach(function (round) {
    var id = round.startup && round.startup.value ? String(round.startup.value) : '';
    if (id === '' || seen[id]) {
        return;
    }
    seen[id] = true;
    if (startupIds.length !== bound(options.portfolio_limit, 50)) {
        startupIds.push(id);
    }
});

var portfolio = [];
if (startupIds.length !== 0) {
    var companies = new GlideRecordSecure('x_bst_startuptrk_startup');
    companies.addQuery('sys_id', 'IN', startupIds.join(','));
    companies.orderBy('name');
    companies.orderBy('sys_id');
    companies.query();
    while (companies.next()) {
        portfolio.push(builder.serialize(companies,
            ['name', 'industry', 'headquarters_location', 'funding_stage',
             'total_funding_usd']));
    }
}
```

**`portfolio_count` on the investor record is the authoritative figure and the list is a window onto it**, so the two need not agree and the template must not present the list's length as the count. The stored count is the distinct-startup union over **all** rounds; this list is the distinct startups among the rounds this page happened to read, which the two caps above deliberately bound. Show `portfolio_count` as the figure, show the rows as the sample, and state the cap when `portfolio.length` is below `portfolio_count`. The union-then-count semantics are specified in [`../data-model.md`](../data-model.md); nothing here recomputes them.

Declare `bound()` once at the top of the script so every cap is validated the same way:

```javascript
function bound(supplied, fallback) {
    var value = parseInt(supplied, 10);
    if (isNaN(value) || value < 1) {
        return fallback;
    }
    return value;
}
```

**The cost of this widget is fixed at seven queries** — the investor record, the led rounds and their count, the join rows and their count, the participated rounds, and the portfolio companies — regardless of how large the investor is.

   **Publish `data.portfolioTruncated` and `data.portfolioLimit` from the bounded set.** `data.portfolioTruncated` is `true` when `startupIds.length` reached `bound(options.portfolio_limit, 50)`, and `data.portfolioLimit` carries that bound, so the template can state how many rows are shown. The template renders the truncation note under this flag, so a caller is never shown a shortened list as though it were the whole portfolio.

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

1. Implement `c.load()` and `c.retry()` exactly as [Error and empty behaviour](#error-and-empty-behaviour) specifies. Every server call below goes through `c.load()`.
2. Expose `c.hasParticipated()`, `c.hasLed()` and `c.hasPortfolio()`, each `true` when the matching array holds at least one entry, so an empty collection renders its own empty state rather than an empty `<tbody>`.
3. **Watch the record only when there is a record to watch, and release the watch on `$destroy`.** `data.investor` is absent on the unauthorised path of server-script item 1 and on the not-found path of item 2, so an unguarded `c.data.investor.sys_id` raises a `TypeError` on both. The shape is identical to the company profile's, with the investor table and the investor object:

```javascript
var ID32 = /^[0-9a-f]{32}$/;
var watch = null;

function releaseWatch() {
    if (!watch) {
        return;
    }
    if (typeof watch.unsubscribe === 'function') {
        watch.unsubscribe();
    } else if (typeof watch === 'function') {
        watch();
    }
    watch = null;
}

function startWatch() {
    releaseWatch();
    var record = c.data && c.data.investor;
    if (!record || !ID32.test('' + record.sys_id)) {
        return;
    }
    watch = spUtil.recordWatch($scope, 'x_bst_startuptrk_investor', 'sys_id=' + record.sys_id);
}

startWatch();
$scope.$on('$destroy', releaseWatch);
```

   A recalculated `portfolio_count` then appears without a reload when the record is on the page, and nothing is subscribed when it is not. The rule is stated once under [Every listener a controller registers is released on `$destroy`](#every-listener-a-controller-registers-is-released-on-destroy).
4. Declare `c.busy` and `c.statusText()` per [Busy, status and focus behaviour](#busy-status-and-focus-behaviour). This widget's status wording is:
   - empty — `No portfolio company and no funding round are recorded for this investor.`
   - loaded — `{{c.data.investor.name}} loaded. {{c.data.portfolio.length}} portfolio companies shown, {{c.data.roundsLed.length}} rounds led, {{c.data.roundsParticipated.length}} rounds joined.`
5. Recompute nothing. `portfolio_count` is read, not derived, in the client.

**The three regions render together, unconditionally.** The overview panel, the portfolio panel and the two rounds tables are all present on the page at once, laid out by the widget's own two columns. There is **no** show-or-hide toggle and **no** section state on this widget: the tab control is used only on the company profile, and a caller reads this profile top to bottom.

#### HTML template

```html
<div class="bst-investor" aria-busy="{{c.busy}}">
  <div class="sr-only" role="status" aria-live="polite" aria-atomic="true">{{c.statusText()}}</div>

  <div class="alert alert-warning" ng-if="!data.authorised">
    <span>Your account holds no Boston Startup Tracker role.</span>
  </div>

  <div class="alert alert-warning" ng-if="data.notFound">
    <span>That investor could not be found.</span>
    <a class="btn btn-default" ng-href="?id=bst_home">Back to search</a>
  </div>

  <div class="alert alert-danger" role="alert" ng-if="data.error">
    <span class="icon-cross-circle" aria-hidden="true">&nbsp;</span>
    <span>{{data.error}}</span>
    <button type="button" class="btn btn-default" ng-click="c.retry()">Retry</button>
  </div>

  <div class="progress" ng-if="c.busy">
    <div class="progress-bar progress-bar-striped active" role="progressbar"
         aria-label="Loading investor profile" aria-valuemin="0" aria-valuemax="100"
         aria-valuetext="Loading"></div>
  </div>

  <div class="row" ng-if="data.authorised &amp;&amp; !data.notFound &amp;&amp; !data.error">
    <div class="col-md-4 col-lg-4">
      <div class="panel panel-default">
        <div class="panel-heading"><h3 class="panel-title" tabindex="-1">{{::data.investor.name}}</h3></div>
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
            Assets under management <span class="pull-right"><span class="label label-info">Premium</span></span>
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
          <div class="alert alert-info" ng-if="!c.hasPortfolio()">
            <span>No portfolio company is recorded for this investor.</span>
          </div>
          <div class="table-responsive" ng-if="c.hasPortfolio()">
            <table class="table table-striped table-hover">
              <thead><tr><th>Company</th><th>Industry</th><th>Headquarters</th><th>Stage</th><th>Total funding</th></tr></thead>
              <tbody>
                <tr ng-repeat="startup in data.portfolio track by startup.sys_id">
                  <td><a ng-href="?id={{::options.company_page}}&amp;sys_id={{::startup.sys_id}}">{{::startup.name}}</a></td>
                  <td>{{::startup.industry}}</td>
                  <td>{{::startup.headquarters_location}}</td>
                  <td><span class="label label-primary" ng-if="::startup.funding_stage">{{::startup.funding_stage}}</span></td>
                  <td ng-if="startup.total_funding_usd !== undefined">{{startup.total_funding_usd}}</td>
                  <td ng-if="startup.total_funding_usd === undefined"><span class="label label-info">Premium</span></td>
                </tr>
              </tbody>
            </table>
          </div>
          <p class="text-muted" ng-if="data.portfolioTruncated">
            Showing the first {{::data.portfolioLimit}} of {{::data.investor.portfolio_count}} portfolio companies.
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
                  <td><a ng-href="?id={{::options.company_page}}&amp;sys_id={{::round.startup.value}}">{{::round.startup.display_value}}</a></td>
                  <td>{{::round.round_date}}</td>
                  <td><span class="label label-primary" ng-if="::round.round_type">{{::round.round_type}}</span></td>
                  <td ng-if="round.amount_usd !== undefined">{{round.amount_usd}}</td>
                  <td ng-if="round.amount_usd === undefined"><span class="label label-info">Premium</span></td>
                  <td ng-if="round.valuation_usd !== undefined">{{round.valuation_usd}}</td>
                  <td ng-if="round.valuation_usd === undefined"><span class="label label-info">Premium</span></td>
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
                  <td><a ng-href="?id={{::options.company_page}}&amp;sys_id={{::round.startup.value}}">{{::round.startup.display_value}}</a></td>
                  <td>{{::round.round_date}}</td>
                  <td><span class="label label-primary" ng-if="::round.round_type">{{::round.round_type}}</span></td>
                  <td ng-if="round.amount_usd !== undefined">{{round.amount_usd}}</td>
                  <td ng-if="round.amount_usd === undefined"><span class="label label-info">Premium</span></td>
                  <td ng-if="round.valuation_usd !== undefined">{{round.valuation_usd}}</td>
                  <td ng-if="round.valuation_usd === undefined"><span class="label label-info">Premium</span></td>
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
2. Produce every figure with `RestResponseBuilder.countWith(table, applyConditions)`, which applies the table-level read gate and then takes one aggregate `COUNT`. **Do not write an aggregate query of your own.** The gate is the whole point: `countWith()` checks `GlideRecordSecure.canRead()` on the table before it counts anything, and answers `0` on a denial. A bare `GlideAggregate` in a widget skips that gate and reports the size of a set the caller may not read; the rule is stated in [`../access-control.md`](../access-control.md).

   **`countWith()` returns `0` on a denial and does not distinguish it from a genuine zero.** That is safe on this route only because the dashboard is behind the same no-role notice as every other widget: `data.authorised` is resolved first, and no figure is rendered when it is false. Where a widget must tell the two apart — as the results widget does — use `countState()` and read its `denied` member instead. A REST operation must always use `countState()` with `rejectDeniedCount()`, never `countWith()`.

> **An aggregate may produce a caller-facing value only when the value depends on no field the caller can be denied, and the table carries no record-level access control.** A row count satisfies both: it reads no field, and all seven entity tables grant table-level read to all three application roles with no record-level rule, so every role sees the same rows. A sum, an average, a maximum or a minimum over a **premium-gated** column satisfies neither, because the aggregate would compute over values the field-level access control exists to withhold.

The reason to route every count through `countWith()` rather than writing the aggregate inline is that the gate, the exactness and this rule then live in **one** place and cannot drift between the eight widgets and the thirty-one REST operations. [`../access-control.md`](../access-control.md) and [`../api-reference.md`](../api-reference.md) state the same rule, and [`../data-model.md`](../data-model.md) records the no-record-level-access-control invariant it rests on — **if a record-level rule is ever added to one of these tables, every count in this guide becomes wrong and must be replaced.**

**The query cost of this widget is one aggregate per panel**, so five aggregates with both optional panels shown and three with neither. No panel iterates a table, and the figures are exact rather than floors.
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

4. Publish no currency figure. `total_funding_usd`, `amount_usd` and `valuation_usd` are **premium-gated**, and a `SUM` over a gated column is exactly the case the rule in step 2 forbids: the aggregate would compute over values the field-level access control exists to withhold from the base `user` role, and would then publish the result to that role as a dashboard figure. Field-level access control is not something a total can be laundered through. **No KPI panel in this widget reports a monetary total**, and none may be added.

#### Client controller

1. Compute `c.columns($index)` as the Bootstrap column span for the panel at that position, from `c.data.kpis.length` and the index, using the table under [The KPI column spans](#the-kpi-column-spans). Choose only from `col-md-6`, `col-md-4` and `col-md-3`, and never a narrower class.
2. Expose `c.hasLink(kpi)` for the conditional `.btn.btn-link`.
3. Declare `c.busy` per [Busy, status and focus behaviour](#busy-status-and-focus-behaviour). This widget carries no status region and no error panel: it issues no server call after its first render, so it has no asynchronous state to announce and no failure to retry.
4. Read no data and issue no server call after the first render. The KPI figures are computed once, in the server script.

##### The KPI column spans

The panel count is **3, 4 or 5** — three always, plus one for each of `show_jobs` and `show_news`. A single span applied to all of them cannot total twelve at every count, so the span is chosen **per position**:

| Panels | Spans by index, `0` first | Rows |
| --- | --- | --- |
| 3 | `col-md-4`, `col-md-4`, `col-md-4` | One row of 12 |
| 4 | `col-md-3`, `col-md-3`, `col-md-3`, `col-md-3` | One row of 12 |
| 5 | `col-md-4`, `col-md-4`, `col-md-4`, `col-md-6`, `col-md-6` | 12, then 12 |

`c.columns($index)` returns `col-md-4` for any index of a three-panel row, `col-md-3` at four panels, and — at five panels — `col-md-4` for indexes `0` to `2` and `col-md-6` for indexes `3` and `4`. **Every row totals exactly twelve columns**, and the second row of the five-panel case wraps on its own because the Bootstrap grid is float-based. Return `col-md-4` for any count the table does not cover, so an unexpected count still renders a defined layout rather than none.

#### HTML template

```html
<div class="bst-kpi" aria-busy="{{c.busy}}">
  <h2>{{::options.title}}</h2>

  <div class="alert alert-warning" ng-if="!data.authorised">
    <span>Your account holds no Boston Startup Tracker role.</span>
  </div>

  <div class="row" ng-if="data.authorised">
    <div ng-class="c.columns($index)" ng-repeat="kpi in ::data.kpis track by kpi.id">
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

**Design-system gap G1.** Bootstrap 3 has no chart component. The resolution is platform reporting surfaced through a report or chart widget, or Angular-rendered inline SVG inside this custom widget. **Both mechanics are specified in full below** — the inline SVG under [The inline SVG chart](#the-inline-svg-chart), the report embed under [The report embed](#the-report-embed) — and the `render_mode` option selects between them. The gap is recorded in [`../gaps-and-flags.md`](../gaps-and-flags.md).

#### Option schema

| Option | Type | Default | Purpose |
| --- | --- | --- | --- |
| `title` | string | `Startups by funding stage` | The `.panel-title` text. |
| `dimension` | string | `funding_stage` | The `x_bst_startuptrk_startup` choice column to bucket on. One of `funding_stage`, `industry`, `employee_count_range`. |
| `render_mode` | string | `svg` | `svg` renders the inline SVG bar chart specified under [The inline SVG chart](#the-inline-svg-chart). `report` embeds a saved report instead, per [The report embed](#the-report-embed). Any other value resolves to `svg`. |
| `report_id` | string | *empty* | The `sys_report.sys_id` used when `render_mode` is `report`. Ignored when `render_mode` is `svg`. **When `render_mode` is `report` and this option is empty or names no readable report, the widget falls back to `svg`** rather than rendering an empty panel; server-script step 7 sets the fallback. |

#### Server script

1. Construct `var builder = new RestResponseBuilder();` and assign `data.authorised = builder.hasAnyAppRole();`. When `data.authorised` is `false`, return immediately and publish nothing further. **Assign the result — do not merely call the method.**
2. Resolve `options.dimension` against the closed set `funding_stage`, `industry`, `employee_count_range`. Any other value falls back to `funding_stage`. Publish the resolved value as `data.dimension`.
3. Publish the bucket labels from the **closed choice list of the resolved column**, transcribed from [`../data-model.md`](../data-model.md) and matching the `sys_choice` records the Update Set delivers:

| `data.dimension` | Bucket labels, in this order |
| --- | --- |
| `funding_stage` | `Pre-Seed`, `Seed`, `Series A`, `Series B`, `Series C+`, `Growth`, `Public`, `Acquired` |
| `industry` | `Fintech`, `Healthtech`, `SaaS`, `Consumer`, `Deeptech`, `Other` |
| `employee_count_range` | `1-10`, `11-50`, `51-200`, `201-500`, `500+` |

4. Count **every bucket in one query** with `RestResponseBuilder.countByGroup(table, field, applyConditions)`, applying the shared inclusion plan, so every chart agrees with the search results and the KPI row:

```javascript
var builder = new RestResponseBuilder();
var search = new StartupSearchService();
var plan = search.buildPlan(null, search.appliesInclusion());

// ONE grouped aggregate for the whole chart. It returns an object keyed on the
// stored choice value, carrying the exact size of each group present in the data.
var sizes = builder.countByGroup('x_bst_startuptrk_startup', data.dimension,
    function (query) {
        search.applyPlan(query, plan);
    });

// The closed label list of step 3 governs the order and the membership, so a bucket
// with no rows still appears at zero and a stored value outside the choice list is
// not charted. The query answered every bucket; this loop only reads its result.
var buckets = [];
var largest = 0;
data.labels.forEach(function (label) {
    var count = sizes[label] === undefined ? 0 : sizes[label];
    if (count > largest) {
        largest = count;
    }
    buckets.push({ label: label, count: count });
});
```

**One query, not one per bucket.** A `countWith` call inside that loop would issue a separate aggregate for every label — eight for `funding_stage`, six for `industry`, five for `employee_count_range` — each re-applying the same inclusion conditions to the same table for a result the grouped aggregate already has. Two charts on the dashboard would then cost up to sixteen queries where they now cost two. `countByGroup()` groups on the column and returns every group's exact size from a single pass, and it carries the same table-level readability gate and the same exactness guarantee as `countWith()`.

Two properties of reading the result through the closed label list matter. A bucket the data does not populate is **absent** from the returned object rather than present as zero, which is why the loop defaults it — omitting that default would drop empty buckets from the chart and silently change its shape. And a stored value outside the choice list would appear as its own key in the result; reading through the label list ignores it, which is correct, because the chart's axis is the declared choice list. Such a value should not exist — cleaning rule 3 prevents it on every ingestion path — and if one is present the count of charted rows will be lower than the KPI figure, which is the signal to look for it.

5. For each bucket publish `share`, the count divided by `largest` and expressed as a whole-number percentage — `0` when `largest` is `0`. Publish `data.buckets` and `data.largest`.
6. Compute **every** SVG coordinate on the server and publish it, so no numeric literal is written into the template or the CSS. The geometry, its five constants and the description string are specified under [The inline SVG chart](#the-inline-svg-chart).
7. Resolve the render mode last, and publish it as `data.renderMode`:
   - `options.render_mode` is `report` **and** `options.report_id` is a 32-character hexadecimal identifier that resolves to a readable `sys_report` record: publish `data.renderMode = 'report'` and `data.report = $sp.getWidget('report-chart', { sys_id: options.report_id })`. The saved report must live in the `x_bst_startuptrk` scope and read one of the application's tables.
   - `options.render_mode` is `report` but `options.report_id` is empty, malformed or resolves to no readable report: publish `data.renderMode = 'svg'` and set `data.reportUnavailable = true`. The bucket geometry is published in every case, so this fallback always has something to draw.
   - any other value of `options.render_mode`, including `svg` and including an empty option: publish `data.renderMode = 'svg'`.
8. Publish no monetary or averaged figure, for the reason stated in step 2 of [`bst-trends-kpi`](#bst-trends-kpi): a `SUM` or `AVG` over one of the four premium-gated currency columns would compute over values the field-level access control exists to withhold. A **row count**, grouped or not, reads no field and is permitted. **The query cost of this widget is one aggregate**, whatever the dimension and however many buckets it has.

##### The inline SVG chart

A horizontal bar chart, one bar per bucket, drawn as inline SVG inside the widget. It is the shipped mode: both instances on `bst_dashboard` carry `render_mode` = `svg`.

**Five constants, declared in the server script**, which is the only place a number appears — the template binds and the CSS carries none:

| Constant | Value | Governs |
| --- | --- | --- |
| `PLOT_WIDTH` | `720` | The width of the coordinate system. The rendered width comes from the `width="100%"` attribute, so this is a ratio, not a pixel promise. |
| `LABEL_WIDTH` | `210` | The band on the left that carries the bucket label. |
| `VALUE_WIDTH` | `70` | The band on the right that carries the count. |
| `BAR_HEIGHT` | `28` | The height of one bar. |
| `BAR_GAP` | `12` | The vertical space between two bars. |

**The derived geometry**, computed once from those constants and the bucket counts:

```javascript
var PLOT_WIDTH = 720, LABEL_WIDTH = 210, VALUE_WIDTH = 70, BAR_HEIGHT = 28, BAR_GAP = 12;
var barSpan = PLOT_WIDTH - LABEL_WIDTH - VALUE_WIDTH;
var height = buckets.length * BAR_HEIGHT + (buckets.length - 1) * BAR_GAP;

buckets.forEach(function (bucket, index) {
    bucket.y = index * (BAR_HEIGHT + BAR_GAP);
    bucket.textY = bucket.y + Math.round(BAR_HEIGHT * 0.7);
    bucket.barWidth = Math.round(barSpan * bucket.share / 100);
    bucket.valueX = LABEL_WIDTH + barSpan + BAR_GAP;
});

data.chart = {
    viewBox: '0 0 ' + PLOT_WIDTH + ' ' + height,
    height: height,
    barHeight: BAR_HEIGHT,
    labelWidth: LABEL_WIDTH,
    description: c_description
};
```

`bucket.barWidth` is `0` when the bucket count is `0`, which draws nothing and is correct: an empty bucket has no bar, and its count is still stated in the value band and in the companion table.

**The description string**, published as `data.chart.description` and read by the SVG's `<desc>`. Assemble it on the server from the resolved dimension, the bucket count, and the largest bucket:

> `Horizontal bar chart of startups by <dimension label>. <n> categories. Largest: <label> with <count>. Every value is also listed in the table below this chart.`

When `data.largest` is `0`, publish instead: `Horizontal bar chart of startups by <dimension label>. <n> categories, all empty.`

**The accessible wiring.** The `<svg>` carries `role="img"` with an `aria-labelledby` pointing at its own `<title>` and an `aria-describedby` pointing at its own `<desc>`, so a screen reader announces the chart's name and its summary rather than reading a tree of shapes. Both identifiers are derived from `data.dimension` by the client controller, because `bst_dashboard` renders **two** instances of this widget in one document and a repeated `id` would make both point at the first chart's text.

**The companion table is not optional.** The chart is a picture of the same numbers the table below it lists row by row, and the table is what carries the values to a caller who cannot use the picture. Both render together in `svg` mode.

##### The report embed

When `data.renderMode` is `report`, the widget renders the stock report widget through `<sp-widget>` and draws no SVG. The saved report supplies its own chart, its own title and its own accessible output, so this widget adds none. The companion table still renders, so the two modes agree on what data is stated in text.

When the report could not be resolved, `data.reportUnavailable` is `true` and the widget renders the SVG chart preceded by one `.alert.alert-warning` naming the fallback, so an operator sees that the configured report was not used.

#### Client controller

1. Expose `c.isSvg()` and `c.isReport()` from **`data.renderMode`**, not from `options.render_mode`. The server resolves the mode, including the fallback of step 7, so reading the raw option here would disagree with what the server prepared.
2. Expose `c.barStyle(bucket)`, returning `{ width: bucket.share + '%' }` for the companion table's `.progress-bar`, and `c.hasData()`, true when `data.largest` is greater than zero.
3. Expose the two identifiers the SVG's accessible wiring needs, each derived from `data.dimension` so the dashboard's two instances never collide:
   - `c.titleId()` returns `'bst-charts-title-' + c.data.dimension`.
   - `c.descId()` returns `'bst-charts-desc-' + c.data.dimension`.
4. Declare `c.busy` per [Busy, status and focus behaviour](#busy-status-and-focus-behaviour). This widget carries no status region and no error panel: it issues no server call after its first render.
5. Perform no arithmetic on record data and compute no coordinate. Every count and every coordinate arrives from the server, and the template binds them with `ng-attr-*`.

#### HTML template

```html
<div class="bst-charts panel panel-default" aria-busy="{{c.busy}}">
  <div class="panel-heading">
    <h3 class="panel-title">
      <span class="icon-chart" aria-hidden="true">&nbsp;</span>{{::options.title}}
    </h3>
  </div>
  <div class="panel-body">
    <div class="alert alert-warning" ng-if="!data.authorised">
      <span>Your account holds no Boston Startup Tracker role.</span>
    </div>

    <div class="alert alert-warning" ng-if="data.authorised &amp;&amp; data.reportUnavailable">
      <span>The configured report could not be read. Showing the built-in chart instead.</span>
    </div>

    <div class="alert alert-info" ng-if="data.authorised &amp;&amp; c.isSvg() &amp;&amp; !c.hasData()">
      <span>No startup is recorded for this breakdown yet.</span>
    </div>

    <svg class="bst-charts-svg"
         ng-if="data.authorised &amp;&amp; c.isSvg() &amp;&amp; c.hasData()"
         role="img"
         width="100%"
         preserveAspectRatio="xMinYMin meet"
         ng-attr-height="{{data.chart.height}}"
         ng-attr-view_box="{{data.chart.viewBox}}"
         ng-attr-aria-labelledby="{{c.titleId()}}"
         ng-attr-aria-describedby="{{c.descId()}}">
      <title ng-attr-id="{{c.titleId()}}">{{::options.title}}</title>
      <desc ng-attr-id="{{c.descId()}}">{{::data.chart.description}}</desc>
      <g ng-repeat="bucket in ::data.buckets track by bucket.label">
        <text class="bst-charts-text" x="0" ng-attr-y="{{bucket.textY}}">{{::bucket.label}}</text>
        <rect ng-attr-x="{{data.chart.labelWidth}}"
              ng-attr-y="{{bucket.y}}"
              ng-attr-width="{{bucket.barWidth}}"
              ng-attr-height="{{data.chart.barHeight}}"
              fill="currentColor"></rect>
        <text class="bst-charts-text" ng-attr-x="{{bucket.valueX}}"
              ng-attr-y="{{bucket.textY}}">{{::bucket.count}}</text>
      </g>
    </svg>

    <div class="table-responsive" ng-if="data.authorised &amp;&amp; c.hasData()">
      <table class="table table-striped bst-charts-table">
        <caption class="sr-only">{{::options.title}}, every value as a table</caption>
        <thead>
          <tr>
            <th scope="col">{{::data.dimensionLabel}}</th>
            <th scope="col">Share of the largest category</th>
            <th scope="col">Startups</th>
          </tr>
        </thead>
        <tbody>
          <tr ng-repeat="bucket in ::data.buckets track by bucket.label">
            <th scope="row">{{::bucket.label}}</th>
            <td class="bst-charts-bar">
              <div class="progress">
                <div class="progress-bar" role="progressbar"
                     ng-style="c.barStyle(bucket)"
                     ng-attr-aria-label="{{::bucket.label}}"
                     ng-attr-aria-valuenow="{{::bucket.share}}"
                     aria-valuemin="0" aria-valuemax="100"></div>
              </div>
            </td>
            <td><span class="label label-default">{{::bucket.count}}</span></td>
          </tr>
        </tbody>
      </table>
    </div>

    <sp-widget widget="data.report" ng-if="c.isReport() &amp;&amp; data.report"></sp-widget>
  </div>
</div>
```

Four properties of that template are what make the chart correct, and each is easy to lose in an edit.

- **Every SVG coordinate arrives through `ng-attr-*`.** `x="0"` is the one literal, and `0` is a permitted literal everywhere in this portal. No coordinate is computed in the controller and none is written in the CSS.
- **`ng-attr-view_box` is written in snake case on purpose.** The rendered attribute must be `viewBox`, and the `ng-attr-` form converts a snake-case suffix to the camel-case attribute name. `ng-attr-viewbox` would emit a lowercase `viewbox`, which the SVG specification does not define, and the chart would render at its intrinsic size with no scaling.
- **`fill="currentColor"` on every `<rect>`**, so the bar colour is inherited from the CSS `color` property of `.bst-charts-svg` and is never written as a literal.
- **The companion table carries `.table-responsive` and a `.sr-only` caption**, and every `.progress-bar` in it carries `aria-label`, `aria-valuenow`, `aria-valuemin` and `aria-valuemax`. A progress bar with no name and no value is announced as an unlabelled control, which is why the bindings are part of the specification rather than a refinement.

Publish `data.dimensionLabel` alongside `data.dimension` in the server script — `Funding stage`, `Industry` or `Employee count range` for the three resolved dimensions — so the table's first column header names what the rows are.

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

.bst-charts .bst-charts-svg {
    display: block;
    width: auto;
    height: auto;
    margin-bottom: $grid-gutter-width;
    color: $brand-primary;
}

.bst-charts .bst-charts-svg .bst-charts-text {
    fill: $sp-tagline-color;
    font-family: $font-family-sans-serif;
    font-size: $font-size-base;
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

3. Resolve the **effective role**, the most capable role held. Publish it twice, because the page states both:
   - `data.effectiveRole` — the role name, one of `x_bst_startuptrk.admin`, `x_bst_startuptrk.premium_user`, `x_bst_startuptrk.user` or `none`. This is the value an acceptance walkthrough records as evidence.
   - `data.effectiveRoleLabel` — the human label the page shows first, from this closed mapping:

| `data.effectiveRole` | `data.effectiveRoleLabel` |
| --- | --- |
| `x_bst_startuptrk.admin` | `Administrator` |
| `x_bst_startuptrk.premium_user` | `Premium subscriber` |
| `x_bst_startuptrk.user` | `Free user` |
| `none` | `No role` |
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

1. Implement `c.load()` and `c.retry()` exactly as [Error and empty behaviour](#error-and-empty-behaviour) specifies, and route the widget's initial load through `c.load()`.
2. Expose `c.roleLabel()`, returning `data.effectiveRoleLabel`, and `c.isDenied()` from `data.premiumDenied`. **The template renders `c.roleLabel()`**, never the raw role name on its own; the role name is shown beside it as supporting detail.
3. Declare `c.busy` and `c.statusText()` per [Busy, status and focus behaviour](#busy-status-and-focus-behaviour). This widget's status wording is:
   - empty — `No entitlement is granted to this account.`, used when `data.effectiveRole` is `none`.
   - loaded — `Signed in as {{c.data.user.name}}. Effective role {{c.data.effectiveRoleLabel}}.`
4. Issue no server call after the first render, other than a retry.

**This widget offers no request, upgrade or notification action, and claims no outcome it does not produce.** There is no request control, no message stating that a request has been noted, and no client-side notification: the application has no commerce, workflow or notification capability in scope, so an action of that kind would report a result that never happened. What the caller is told instead is exactly what is true — an administrator grants the role on the instance — and that wording is published once, by `bst-premium-upsell`, as `data.guidance`. See [`../gaps-and-flags.md`](../gaps-and-flags.md) flag **F1** and gap **G6**.

#### HTML template

```html
<div class="bst-account" aria-busy="{{c.busy}}">
  <div class="sr-only" role="status" aria-live="polite" aria-atomic="true">{{c.statusText()}}</div>

  <div class="alert alert-danger" role="alert" ng-if="data.error">
    <span class="icon-cross-circle" aria-hidden="true">&nbsp;</span>
    <span>{{data.error}}</span>
    <button type="button" class="btn btn-default" ng-click="c.retry()">Retry</button>
  </div>

  <div class="panel panel-default">
    <div class="panel-heading">
      <h3 class="panel-title" tabindex="-1">
        <span class="icon-user" aria-hidden="true">&nbsp;</span>{{::options.title}}
      </h3>
    </div>
    <ul class="list-group">
      <li class="list-group-item">Signed in as <span class="pull-right">{{::data.user.name}}</span></li>
      <li class="list-group-item">User name <span class="pull-right">{{::data.user.user_name}}</span></li>
      <li class="list-group-item">
        Effective role
        <span class="pull-right">
          <span class="label label-primary" ng-if="data.authorised">{{c.roleLabel()}}</span>
          <span class="label label-default" ng-if="!data.authorised">No role</span>
          <small class="text-muted bst-account-role-name">{{::data.effectiveRole}}</small>
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

  <a class="btn btn-default" ng-href="?id=bst_home">Back to search</a>
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
2. Split `options.gated_fields` on the comma, trim each entry, discard empties, and map each to a human label. Publish the result as `data.fields`.

**The allowlist is six option tokens, and they represent the seven physical access-controlled fields.** The counts differ by one on purpose: `contact_email` is one token covering **two** columns, `x_bst_startuptrk_founder.contact_email` and `x_bst_startuptrk_executive.contact_email`, which carry the same name, the same label and the same field-level access control on two tables. The seven fields themselves are listed under [Step 6](#step-6--access-control-in-every-widget-server-script).

| Option token | Label | Access-controlled field or fields it represents |
| --- | --- | --- |
| `total_funding_usd` | Total funding | `x_bst_startuptrk_startup.total_funding_usd` |
| `institutional_funding_last_5yrs` | Institutional funding in the last five years | `x_bst_startuptrk_startup.institutional_funding_last_5yrs` |
| `contact_email` | Founder and executive contact email | `x_bst_startuptrk_founder.contact_email` **and** `x_bst_startuptrk_executive.contact_email` |
| `aum_usd` | Assets under management | `x_bst_startuptrk_investor.aum_usd` |
| `amount_usd` | Round amount | `x_bst_startuptrk_fundinground.amount_usd` |
| `valuation_usd` | Round valuation | `x_bst_startuptrk_fundinground.valuation_usd` |

**Any token that is not one of those six is rejected: discard it silently and render nothing for it.** Do not fall back to the token itself as a label, and do not render an entry with an empty label — either would put an unmapped column name in front of a caller. `portfolio_count` is the token most likely to be passed by mistake and is **rejected for a specific reason**: `x_bst_startuptrk_investor.portfolio_count` is readable by all three roles and is not premium-gated, so naming it here would tell a caller that a field they can already read is withheld.

When every supplied token is rejected, `data.fields` is an empty array and the template's field list does not render. The heading, the body and the call to action still render, because the host embedded this widget only after something was in fact withheld.

3. Publish `data.body`, one of these three strings, selected from `options.context`:

| `options.context` | `data.body` |
| --- | --- |
| `company` | `This company profile has premium fields on it. Funding amounts, valuations and contact addresses are reserved for the premium tier. Everything else on this profile is available to your account.` |
| `investor` | `This investor profile has premium fields on it. Assets under management, round amounts and valuations are reserved for the premium tier. The portfolio list and the portfolio count are available to your account.` |
| `account` | `Your account reads the seven tables and every field that is not reserved for the premium tier. The fields below are reserved, and an administrator grants the premium role that reads them.` |

Apply the `account` wording for any context value that is not one of the three, so an unrecognised context still renders a sentence that is true of every surface.

4. Publish `data.callToActionLabel` — `See your entitlements` for `company` and `investor` — and `data.upsellPage` from `options.upsell_page`. **Publish no call-to-action label for `account`**, where the caller is already on the destination; publish `data.guidance` instead, the one truthful instruction this application can give:

> `An administrator grants the premium role on this instance. Ask your ServiceNow administrator to add the role x_bst_startuptrk.premium_user to your user record.`

`data.guidance` is the whole of what this widget says about obtaining the role. **It is text, not an action.** There is no request button, no notification and no message claiming that a request has been recorded: the application has no commerce, workflow or notification capability in scope, so any such control would report an outcome it did not produce. Premium subscription billing is flagged as **F1** in [`../gaps-and-flags.md`](../gaps-and-flags.md), not built.

5. Read **no** record and reference **no** field value. This widget renders column names and static wording only. It must never receive, hold or render a gated value; a partial that carried the value it exists to hide would defeat the field-level access controls entirely.

#### Client controller

1. Expose `c.isAccount()` from `options.context`, so the account host renders `data.guidance` rather than a navigation link to the page it is already on.
2. Declare `c.busy` per [Busy, status and focus behaviour](#busy-status-and-focus-behaviour). This widget carries no status region and no error panel: it renders once, from options its host supplied, and issues no server call of its own.
3. Expose **no** request, upgrade or notification function. There is nothing for such a function to do that would be true.

#### HTML template

```html
<div class="bst-upsell alert alert-info" role="alert" aria-busy="{{c.busy}}">
  <h4>
    <span class="icon-locked" aria-hidden="true">&nbsp;</span>{{::options.heading}}
  </h4>
  <p>{{::data.body}}</p>
  <ul class="list-unstyled bst-upsell-fields" ng-if="::data.fields.length > 0">
    <li ng-repeat="field in ::data.fields track by field.name">
      <span class="label label-default">{{::field.label}}</span>
    </li>
  </ul>
  <a class="btn btn-primary" ng-if="::!c.isAccount()" ng-href="?id={{::data.upsellPage}}">
    {{::data.callToActionLabel}}
  </a>
  <p class="bst-upsell-guidance" ng-if="::c.isAccount()">{{::data.guidance}}</p>
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

.bst-upsell .bst-upsell-guidance {
    margin-bottom: 0;
}
```

### Widget roll-up

| # | Widget name and ID | Options | Placed on | Embeds |
| --- | --- | --- | --- | --- |
| 1 | `bst-startup-search` | `title`, `show_industry`, `show_location`, `results_page` | `bst_home` | — |
| 2 | `bst-startup-results` | `title`, `page_size`, `detail_page`, `show_logo` | `bst_home` | — |
| 3 | `bst-company-profile` | `default_tab`, `investor_page`, `upsell_page`, `funding_limit`, `people_limit`, `jobs_limit`, `news_limit` | `bst_company` | `bst-premium-upsell` |
| 4 | `bst-investor-profile` | `company_page`, `upsell_page`, `portfolio_limit`, `rounds_limit` | `bst_investor` | `bst-premium-upsell` |
| 5 | `bst-trends-kpi` | `title`, `show_jobs`, `show_news` | `bst_dashboard` | — |
| 6 | `bst-trends-charts` | `title`, `dimension`, `render_mode`, `report_id` | `bst_dashboard`, two instances | the stock report widget when `render_mode` is `report` |
| 7 | `bst-account-summary` | `title`, `show_entitlements`, `upsell_page` | `bst_account` | `bst-premium-upsell` |
| 8 | `bst-premium-upsell` | `context`, `gated_fields`, `upsell_page`, `heading` | none — embedded only | — |

### The query budget of each page

**Every server script's query count is fixed by its code, not by the size of the data it renders.** That is the property to check, and it is checkable by reading the scripts: a page whose cost depends on how many children a record has, or on how many buckets a chart has, has an unbounded read in it.

| Page | Widgets rendered | Queries per render | Composition |
| --- | --- | ---: | --- |
| `bst_home` | search, results | **2** | one bounded, ordered, windowed read of `x_bst_startuptrk_startup` plus one `COUNT` aggregate under the identical plan. The search widget issues none — it only publishes criteria. |
| `bst_company` | company profile, upsell | **11** | one record read, then two per child collection across five collections — a bounded read and its `COUNT` — plus one batched read of the join table for every round on the page. |
| `bst_investor` | investor profile, upsell | **7** | the investor record; the led rounds and their count; the capped join rows and their count; the participated rounds; the portfolio companies. |
| `bst_dashboard` | KPI row, two chart instances | **7** | five `COUNT` aggregates for the five KPI panels, and one grouped aggregate per chart. |
| `bst_account` | account summary, upsell | **1 to 3** | the caller's role state, and a count only where the summary reports one. |

Four properties hold across the whole table, and each is what a reviewer should verify:

- **No count iterates.** Every figure comes from `countState()`, `countWith()` or `countByGroup()`, each of which answers one exact `COUNT` aggregate behind a table-level readability gate. None returns a floor, and none walks a result set to arrive at a number.
- **No collection is read without a limit.** Every child list on the two profile pages carries a limit option, and every limit is validated to a positive whole number with a fallback — an empty or malformed option resolves to the default, never to "no limit".
- **No cost is proportional to the record.** A company with two job postings and a company with twenty thousand cost the same eleven queries; only the number of **rows returned** differs, and that is capped. An investor that led one round and one that participated in three thousand cost the same seven, because the join read carries the cap and everything downstream reads from its result.
- **No chart costs more than one query**, whatever its dimension and however many buckets its choice list declares.

**Two things are deliberately not done here.** Nothing is cached: a portal page is rendered per request and a cache would introduce a staleness contract this prototype has no requirement for. And nothing is throttled at the widget layer: the REST surface has its own fixed-window rate limit, documented in [`../api-reference.md`](../api-reference.md), and the portal's protection is that a render's cost is bounded rather than that its rate is capped. Both positions are recorded in [`../../../docs/decisions/DECISION_LOG.md`](../../../docs/decisions/DECISION_LOG.md).

### The Angular surface available inside a widget

The framework inside a Service Portal widget is AngularJS 1.x with Bootstrap 3.3.6. The surface below is the whole of what these eight widgets use.

#### Template directives

| Directive | Use in this portal |
| --- | --- |
| `ng-repeat` | Every collection: result cards, table rows, list-group items, KPI panels, tab items, chart buckets, upsell field labels. Always with `track by <item>.sys_id` where the item is a record, and `track by <item>.label` or `.id` where it is not. |
| `ng-if` | Every conditional region, including **every premium-field omission test**. Prefer it over `ng-show`, so a denied field's markup is never present in the document. |
| `ng-model` | The three filter inputs of `bst-startup-search`. |
| `ng-class` | The `.active` class on `.nav-tabs` items and `.tab-pane` panes, and the computed column class in `bst-trends-kpi`. |
| `ng-click` | Tab selection, pager buttons, the search and clear buttons, and the retry button of every error panel. |
| `ng-href` / `ng-src` | Every interpolated link and image source, so a partially interpolated value is never requested. |
| `ng-style` | The `.progress-bar` width in `bst-trends-charts`, bound to a server-computed percentage. |
| `ng-disabled` | The pager buttons of `bst-startup-results`. |
| `ng-keydown` | The tab-strip key handling of `bst-company-profile`, bound on every `role="tab"` control. See [The tab contract](#the-tab-contract). |
| `ng-attr-*` | Every attribute whose value is interpolated and is **not** a link, an image source or a class: the accessible identifiers on the tab controls and panes, the `aria-valuenow` and `aria-label` of a named progress bar, and every coordinate of the inline SVG chart. A camel-case target attribute is written in snake case — `ng-attr-view_box` emits `viewBox`. |
| `aria-busy` | Bound on the root element of all eight widgets to the controller's `c.busy`. See [Busy, status and focus behaviour](#busy-status-and-focus-behaviour). |
| `sp-widget` | Rendering an embedded widget model: `<sp-widget widget="data.upsell">`. |

The one-time binding form `{{::value}}` is used for every value that does not change after the first render, which is most of them. A value that participates in an omission test is bound **without** the one-time prefix where the containing region can be re-rendered by a server refresh.

#### `spUtil`, the client service

| Member | Use in this portal |
| --- | --- |
| `spUtil.get(widgetId, data)` | Fetching an additional widget model on the client. Used only when a widget must load a partial after its first render; the three hosts here embed the upsell on the **server** with `$sp.getWidget()` instead, because the embed decision depends on an access-control outcome that must be evaluated server-side. |
| `spUtil.recordWatch($scope, table, filter)` | `bst-company-profile` on `x_bst_startuptrk_startup`, and `bst-investor-profile` on `x_bst_startuptrk_investor`, so an administrator's edit and a recalculated `portfolio_count` appear without a manual reload. **Called only behind the record-and-identifier guard, and the returned handle released on `$destroy` and before every re-subscribe** — see [Every listener a controller registers is released on `$destroy`](#every-listener-a-controller-registers-is-released-on-destroy). |
| `spUtil.addInfoMessage(message)` | `bst-account-summary` and `bst-premium-upsell`, for the premium-role request acknowledgement. |
| `spUtil.update($scope)` | An alternative form for replacing the whole widget model. Every widget above uses `$scope.server.update()` instead, which sends `$scope.data` to the server script as `input`; keep to that one form throughout. |

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
| **G1** | Charts on the Dashboard / Trends route | Both mechanics are built in [`bst-trends-charts`](#bst-trends-charts) and the `render_mode` option selects between them: `svg` renders the Angular-bound inline SVG bar chart specified under [The inline SVG chart](#the-inline-svg-chart), `report` embeds a saved platform report per [The report embed](#the-report-embed). `svg` is the shipped mode on both dashboard instances, and `report` falls back to it when no readable report is configured. |
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
- No count is an exception. Produce every count with `RestResponseBuilder.countState()` or `RestResponseBuilder.countWith()`, which apply the table-level read gate and then take one aggregate `COUNT`. **Do not write an aggregate query of your own in a widget**: a bare `GlideAggregate` skips the gate and reports the size of a set the caller may not read. `countState()` reports a denial as `denied`; `countWith()` answers `0`, so use it only where the widget already withholds every figure from an unauthorised caller.
- No Script Include in this application is client-callable, and none runs with elevated privilege. A widget must not reach a Script Include from its client controller, and must not construct one that reads a premium column through an unsecured path and returns it.
- The forbidden anti-pattern: **a helper that reads a premium-gated column with `new GlideRecord()` and hands the value to a widget bypasses the field-level access control entirely, and the access control reports no denial because it was never consulted.**

### Omitted, not nulled

- A denied field is **omitted** from the data object entirely. It is **not** nulled, **not** set to an empty string, and **not** replaced with a placeholder value.
- **The secured read returns an empty string for a denied field, not an error**, so the failure is silent. Copying every column of a secured record onto `data` produces exactly the nulled behaviour the requirements forbid, and the widget renders without complaint.
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

1. **Create three purpose-built users for this walkthrough.** They are **this walkthrough's own users**, created by hand and deleted when it finishes — they are not the users guide 05's suites use. Each holds **exactly one** of `x_bst_startuptrk.admin`, `x_bst_startuptrk.premium_user` and `x_bst_startuptrk.user`, and **none** of the elevated platform roles — not the platform `admin` role, not `security_admin`, not `maint`, not `impersonator`, not `user_admin`. Note that the scoped role `x_bst_startuptrk.admin` and the platform administrator role are different roles; the walkthrough user holds the scoped one and not the platform one.
   Name them distinctly from the automated ones so the two sets can never be confused in `sys_user`: use `BST PORTAL admin`, `BST PORTAL premium` and `BST PORTAL base`. Leave **Groups** empty — a group can carry a role, and a role inherited through a group is as real as a directly assigned one. Before impersonating, open each user's **Roles** related list and confirm it holds exactly the one scoped role and nothing else.
2. Impersonate each user in turn and walk all five routes. Do not read the fields as yourself.
3. Under `x_bst_startuptrk.user`, confirm that every one of the seven premium fields renders the `Premium` label or the upsell treatment, and that `bst-premium-upsell` appears on the company profile, the investor profile and the account summary.
4. Under `x_bst_startuptrk.premium_user` and under `x_bst_startuptrk.admin`, confirm every one of the seven renders its value and that `bst-premium-upsell` does **not** appear.
5. Confirm that a non-premium column — for example `x_bst_startuptrk_startup.headquarters_location` — renders a value under `x_bst_startuptrk.user` on the same screen. That establishes that the table-level grant passed and that the denial came from the field-level control.

6. **Delete the three users when the walkthrough is finished**, together with their role assignments. Confirm afterwards that `sys_user` carries no user whose first name is `BST PORTAL`. Leaving them behind leaves three standing accounts on the instance whose sole purpose has passed, and a later reviewer cannot tell them from a real user.

**These three users are not the ones guide 05 uses, and neither set can stand in for the other.** The two sets differ in how they are created, and therefore in what each can be used for:

| | This walkthrough's three users | Guide 05's three users |
| --- | --- | --- |
| Created by | Hand, before the walkthrough | A **Create a User** step inside each test, at run time |
| Lifetime | Until the operator deletes them, per step 6 | The test transaction. ATF rolls the record back when the test ends |
| Visible to a browser session | **Yes**. A portal walkthrough signs in as each in turn | No. There is no window in which a browser could sign in as one |
| Naming | `BST PORTAL admin`, `BST PORTAL premium`, `BST PORTAL base` | `BST ATF admin`, `BST ATF premium`, `BST ATF base` |

The walkthrough therefore cannot reuse guide 05's users — they do not exist outside their tests — and guide 05 must not reuse these, since a test bound to a hand-built account passes or fails on whether someone has deleted it. After a completed run of either, `sys_user` should carry **neither** `BST PORTAL` nor `BST ATF` users; a residual `BST ATF` user means a test transaction did not close, and a residual `BST PORTAL` user means step 6 was skipped.

The full procedure and the twenty-one field-by-role outcomes are in [`../access-control.md`](../access-control.md). The twenty-one automated assertions live in [`./05-atf-test-suites.md`](./05-atf-test-suites.md). **Neither replaces the other**: the automated cells assert the API and secured-read surfaces under impersonation, and this walkthrough asserts what a signed-in caller actually sees rendered on all five routes.

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

`src/frontend/styles/global.css` is the repository's **entire** design-token surface: **42 physical lines of hard-coded literals** — `wc -l` reports 41 because the final line carries no terminating newline — and no variable of any kind. The migration therefore introduces a token system where none was present.

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

**Four values are carried forward** — the font stack, the page background, the link colour and the container maximum — and they are declared in the theme's CSS-variables field, and nowhere else. Everything else in the file is replaced by the design system's own treatment. This section is the **provenance** of those four values; the values themselves, together with the other twenty-nine, are declared at [The CSS-variables field](#the-css-variables-field) and repeated at [The complete declaration block](#the-complete-declaration-block), which is what an operator builds from.

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

`package.json:L15-L16` declares `"@material-ui/core": "^4.12.3"` and `"@material-ui/icons": "^4.11.2"`. Both are **left untouched**: the legacy manifest is reference-mode and no repository manifest is edited by this work. That constraint is settled at `D-078` in [`../../../docs/decisions/DECISION_LOG.md`](../../../docs/decisions/DECISION_LOG.md).

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
- [ ] Exactly **1** `sp_instance_menu` menu record with exactly **3** `sp_rectangle_menu_item` items, and the portal's **Main menu** field names that record. See [The header menu and its items](#the-header-menu-and-its-items).
- [ ] Every one of those 16 records carries `sys_scope` `Boston Startup Tracker`.
- [ ] Zero `sys_ux_*` records were created, and UI Builder was not opened.
- [ ] The company profile renders exactly **five** tabs, labelled **Overview**, **Funding**, **People**, **Jobs**, **News**, in that order.
- [ ] `bst-premium-upsell` is embedded by exactly three hosts — `bst-company-profile`, `bst-investor-profile` and `bst-account-summary` — and is placed on no page. `bst-startup-results` renders the gap G5 treatment inline and is **not** a fourth host.
- [ ] `sys_script_include` in the `x_bst_startuptrk` scope holds exactly the **eight** classes of precondition 5, and `sys_properties` holds exactly the **eleven** `x_bst_startuptrk.*` keys of precondition 6.
- [ ] No widget server script names a Script Include outside the four of precondition 5, and no widget reads a property outside the three of precondition 6.
- [ ] No `sp_rectangle` anywhere in the five pages is left without an `sp_instance`.

### Behaviour every widget must show

- [ ] **Authorisation.** Under a user holding exactly one of the three scoped roles, every widget renders its content and none renders the "no Boston Startup Tracker role" alert. A widget showing that alert to a role-holding caller means its server script called `hasAnyAppRole()` without assigning the result to `data.authorised`.
- [ ] **Busy.** Every one of the eight widget roots carries `aria-busy`, and it reads `true` while a load is in flight and `false` afterwards. Confirm on `bst-startup-results` by submitting a search.
- [ ] **Status.** `bst-startup-results`, `bst-company-profile`, `bst-investor-profile` and `bst-account-summary` each carry exactly **one** `role="status"` region with `aria-live="polite"`, and its text changes as the widget loads, empties and completes.
- [ ] **Failure.** Force a rejected server call — impersonate a user, remove the role mid-session, then retry a load. Each of the four asynchronous widgets renders one `.alert.alert-danger` with `role="alert"` and a working **Retry** button, and the striped progress bar clears rather than spinning on.
- [ ] **Empty.** Load a company with no funding round, no founder, no executive, no open role and no news article. All five panes render their own empty wording, and no pane renders as nothing at all.
- [ ] **Pagination at zero.** Search for a name that matches nothing. The pager reads `No results to show` and never `1 to 0 of 0`, and **Next** is disabled.
- [ ] **Tabs.** On the company profile, exactly one tab control carries `tabindex="0"` and `aria-selected="true"` at a time; each control's `aria-controls` resolves to the `id` of its own pane; and `ArrowRight`, `ArrowLeft`, `Home` and `End` all move the selection and the focus together. Tab moves out of the strip, not through it.
- [ ] **Progress bars are named.** Every `role="progressbar"` carries a name, and every determinate bar in `bst-trends-charts` also carries `aria-valuenow`, `aria-valuemin` and `aria-valuemax`.
- [ ] **Decorative glyphs are hidden.** Every `.icon-*` span carries `aria-hidden="true"`.
- [ ] **The chart draws.** With `render_mode` `svg`, `bst-trends-charts` renders an `<svg role="img">` whose `viewBox` attribute is present and camel-cased, with one `<rect>` per bucket and a `<title>` and `<desc>` whose `id` values differ between the dashboard's two instances.
- [ ] **The chart falls back.** Set `render_mode` to `report` with an empty `report_id`. The widget renders the warning alert and the SVG chart, not an empty panel.
- [ ] **The premium treatment appears in the result list.** Under `x_bst_startuptrk.user`, each result card states `Total funding` beside a `Premium` marker, and the list is followed by exactly one `.alert.alert-info` carrying a `.btn.btn-primary` to `bst_account`.
- [ ] **The account page tells the truth.** It renders the human role label — `Administrator`, `Premium subscriber`, `Free user` or `No role` — and it offers no control that claims a request was recorded.

### Design system

- [ ] Every one of the **33** theme variables under [The CSS-variables field](#the-css-variables-field) is declared with the literal value that table gives. No value the portal applies is left to a release default.
- [ ] No widget CSS contains a literal colour, spacing, radius or font value. The only literals present are `0`, `none`, `auto`, `inherit`, `currentColor` and `transparent`. The inline SVG chart's coordinates are **not** CSS: they are server-computed and bound with `ng-attr-*`.
- [ ] No `.col-xs-*` or `.col-sm-*` class appears in any widget template, and no `size`, `size_xs` or `size_sm` is set on any `sp_rectangle`.
- [ ] The walkthrough was performed at 1024 pixels wide and above, the declared floor.
- [ ] No Lucide reference and no emoji character appears in any widget template, CSS field, client controller, option label or option default.
- [ ] Every icon is a platform glyph-font `.icon-*` class.
- [ ] No repository manifest was created or edited.

### Access control

- [ ] Every widget server script reads records through `GlideRecordSecure` and serialises through `RestResponseBuilder.serialize()`. No widget opens a `GlideRecord`, and no widget writes an aggregate inline — every count goes through `countState()`, `countWith()` or `countByGroup()`.
- [ ] No widget aggregates a premium-gated column, and no widget publishes a monetary total.
- [ ] Every child collection on the company profile and the investor profile is read under a limit, and each publishes its exact total alongside the rows it rendered.
- [ ] The charts widget issues **one** grouped aggregate, not one count per bucket.
- [ ] A denied premium field has **no key** on the serialised object, and every template test is `!== undefined` rather than a null or empty-string comparison.
- [ ] All seven premium fields were checked under impersonation by a user holding exactly one scoped role and none of the elevated platform roles.
- [ ] **The three walkthrough users were created by hand for this walkthrough**, named `BST PORTAL admin`, `BST PORTAL premium` and `BST PORTAL base`, each verified to hold exactly one scoped role and to belong to no group **before** it was impersonated. They are **not** guide 05's `BST ATF` users, which exist only inside their own test transactions.
- [ ] **The three walkthrough users were deleted when the walkthrough finished**, and `sys_user` now carries no user whose first name is `BST PORTAL`. Deleted: `______`
- [ ] `bst-premium-upsell` appeared on the company profile, the investor profile and the account summary under `x_bst_startuptrk.user`, and appeared on none of them under `x_bst_startuptrk.premium_user`.
- [ ] A non-premium column rendered a value under `x_bst_startuptrk.user` on the same screen as a denied premium field.

### Routes

- [ ] All five routes render and navigate, walked in this order: `?id=bst_home`, `?id=bst_company&sys_id=<startup>`, `?id=bst_investor&sys_id=<investor>`, `?id=bst_dashboard`, `?id=bst_account`.
- [ ] `/bst` with no `id` resolves to `bst_home`.
- [ ] Every one of the fifteen navigation hops under [Routing and navigation](#routing-and-navigation) reaches its target page with the correct `sys_id`, **activated through its rendered control** rather than by a typed address.
- [ ] Every one of the five routes has at least one incoming hop, confirmed against the incoming-hop table under [Routing and navigation](#routing-and-navigation). `bst_dashboard` and `bst_account` are reached from the header menu on every page.
- [ ] `bst_company` and `bst_investor` each render the not-found alert, and not an empty panel, when `sys_id` is absent or unresolvable.
- [ ] With the browser console open, load `?id=bst_company` with **no** `sys_id`, then with an unresolvable `sys_id`, then under `x_bst_startuptrk.user` with no scoped role granted. Repeat all three for `?id=bst_investor`. Each of the six loads renders its notice and logs **zero** console errors. A `TypeError` on any of the six means the record guard is missing.
- [ ] Navigate `bst_home` → `bst_company` → `bst_home` five times, then submit a search. The search runs **once**. More than one server round trip per submit means the `$rootScope` listener of `bst-startup-results` is not deregistered on `$destroy`.
- [ ] On `bst_company` and `bst_investor`, trigger a server refresh three times on a resolvable record. Each refresh releases the previous `recordWatch` handle before taking a new one, so the widget holds exactly one subscription.

### The inclusion filter

- [ ] Seed one startup that fails the criteria — `active` false, or a `headquarters_location` containing neither `Boston` nor `Cambridge, MA`. Load records first with [`./06-staging-table-csv-import.md`](./06-staging-table-csv-import.md).
- [ ] Under `x_bst_startuptrk.user`, that startup is **absent** from `bst_home` results and absent from the `bst_dashboard` KPI figures.
- [ ] The same startup is **present** in the platform list view for `x_bst_startuptrk_startup` under `x_bst_startuptrk.admin`, which is the administrative visibility [`../data-model.md`](../data-model.md) specifies.
- [ ] `data.total_count` on `bst-startup-results` **equals** the number of rows the pager reports across all pages. The total is exact, so a difference of even one row means the plan was applied to the result set and not to the count.
- [ ] No widget template, client controller or server script evaluates `active` or `headquarters_location` outside `StartupSearchService.applyPlan()`.

This is the evidence for criterion 5 of [`../validation-checklist.md`](../validation-checklist.md), which records the outcome.

## Related documents

- [`../../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml`](../../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml) — the authoritative table, column, choice, Script Include, property and role records this guide cites, and the artifact whose commit is precondition 3
- [`../data-model.md`](../data-model.md) — the ten tables field by field, the seven premium markers, the closed choice lists the widgets render, the `participating_investors` projection and the inclusion criteria
- [`../access-control.md`](../access-control.md) — the three roles, the five access-control layers, the role-by-field matrix, the secured read path, the omit-not-null rule and the impersonation procedure
- [`../api-reference.md`](../api-reference.md) — the Script Include call graph with every public method, the eleven system properties including the two page-size properties this portal shares with the API, and the pagination envelope
- [`../validation-gates.md`](../validation-gates.md) — the eleven required post-commit gates that are precondition 4, and the acceptance-required and non-normative checks that are not
- [`../manual-build-instructions.md`](../manual-build-instructions.md) — the index and dependency ordering of the six manual-build guides
- [`./01-connection-credential-aliases.md`](./01-connection-credential-aliases.md) — step 1, the two Connection and Credential Aliases
- [`./02-flow-crunchbase-ingestion.md`](./02-flow-crunchbase-ingestion.md) — step 2, the Crunchbase ingestion flow
- [`./03-flow-linkedin-ingestion.md`](./03-flow-linkedin-ingestion.md) — step 3, the LinkedIn ingestion flow
- [`./05-atf-test-suites.md`](./05-atf-test-suites.md) — the last step, carrying the twenty-one field-by-role assertions. Its three `BST ATF` users are created inside each test and rolled back with it; this guide's walkthrough creates and deletes its own three `BST PORTAL` users, because a browser session cannot sign in as a user that exists only inside a test transaction
- [`./06-staging-table-csv-import.md`](./06-staging-table-csv-import.md) — step 5, the staging-table CSV load that puts records on the instance before the walkthrough
- [`../validation-checklist.md`](../validation-checklist.md) — the five success criteria; criterion 5 is the pass condition for the route walkthrough and the inclusion filter
- [`../gaps-and-flags.md`](../gaps-and-flags.md) — the design-system gaps G1 through G5 and G7, the query-parameter routing deviation and the premium-billing flag
- [`../../../docs/decisions/DECISION_LOG.md`](../../../docs/decisions/DECISION_LOG.md) — the single source of truth for every decision behind this portal, including the five deviations named at the top of this guide
- [`../../../docs/review/CRITICAL_DECISIONS.md`](../../../docs/review/CRITICAL_DECISIONS.md) — the five highest-risk decisions. **Entry 5, risk Medium, reviewer persona UX**, is the entry that names this guide: it covers the three interface deviations implemented here, and its check is to walk all five routes and confirm the premium upsell treatment appears wherever a gated field is denied. The deviations themselves are reviewed against `D-055`, `D-056` and `D-057` of the decision log
