# Manual build 04 — Service Portal pages and widgets — `x_bst_startuptrk`

This guide builds the Service Portal experience of the ServiceNow scoped application `x_bst_startuptrk` by hand, on the instance, through the platform's own interface. It specifies **one** portal record, **one** theme record, **five** pages and **eight** widgets, and for each one it states every field to set, every option in the option schema, the server-script responsibilities, the client-controller responsibilities, the HTML template structure with the Bootstrap classes it uses, and the widget CSS. It also states the design-system contract every widget author must satisfy, the access-control rules every widget server script must honour, and the verification checklist to run before this guide is signed off.

**Authority.** The frozen prompt and the Agent Action Plan are authoritative for all application content. The Update Set XML at [`../../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml`](../../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml) is the authoritative source for every table name, column name, choice value, Script Include class name, method name, system-property key and role name cited below; the identifiers used here match those records character for character, and the same identifiers appear in [`../data-model.md`](../data-model.md), [`../access-control.md`](../access-control.md) and [`../api-reference.md`](../api-reference.md). No variant spelling of any identifier is valid. Where this guide and those records disagree, the records are checked against the prompt and the plan first; where the records match the specification, this guide is corrected to them.

This document carries **no rationale**. It states what to build and how to build it. Every decision behind the portal, every alternative considered and every risk it carries is recorded in [`../../../docs/decisions/DECISION_LOG.md`](../../../docs/decisions/DECISION_LOG.md), which is the single source of truth for "why". Five points in this guide depart from a literal reading of the requirements — the five-tab company profile, the "Team" to "People" tab rename, the dropped "Similar Companies" tab, query-parameter routing in place of path-style routes, and the 1024-pixel viewport floor. Each is stated below as a build mechanic and cross-referenced to that log. None is argued here.

Operational warnings **are** in scope for this guide and are marked as such. The administrator-override warning under [Operational warning — the administrator override](#operational-warning--the-administrator-override) is the most important one in this file and must not be skipped.

## Referenced documents

This guide is executable on its own. The portal, the theme, **every one of the fifty-four token declarations as a literal value**, all five pages, all eight widgets, the design-system contract, the access-control rules and the verification checklist are stated here in full. An operator needs no other file, and no external stylesheet reference, to build the portal: [The complete declaration block](#the-complete-declaration-block) can be pasted into the theme record as it stands.

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
| 4 | **All eleven required post-commit gates have passed.** | Run the eleven required gates in [`../validation-gates.md`](../validation-gates.md) — the seven entity-table reads `GATE-TBL-01` through `GATE-TBL-07`, the three role-record gates `GATE-ROLE-01` through `GATE-ROLE-03`, and the one scope-record gate `GATE-SCOPE-01` — and record `pass` for all eleven in that document's required-gate evidence table. The aggregate pass condition is `11 of 11`; there is no partial pass, and no required gate may be skipped, deferred or waived. Neither `GATE-COL-01` nor any `GATE-SEC` check is a precondition of this guide, though all four block acceptance of the delivery. |
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

Every token the widgets reference is declared here, in the theme's CSS-variables field, and **nowhere else**. Declare each variable in the table below with a SASS declaration of the form `$variable: value;`, one per line, grouped in the order the table gives. **The Value column below is the literal to type.** Nothing is left to be looked up elsewhere: every one of the fifty-four variables carries its exact value here, and [The complete declaration block](#the-complete-declaration-block) repeats all fifty-four as a single block that can be pasted into the field as it stands.

The fifty-four values divide into five provenance classes, and every one of them is typed as a literal here regardless of class:

- **Four are carried forward from the legacy stylesheet** — the body font stack, the page background, the link colour and the container maximum. They are marked *carried forward* below, and their provenance is recorded under [The legacy design-token surface](#the-legacy-design-token-surface).
- **One repeats a carried-forward value**: `$sp-body-bg` is declared to the same `#f5f5f5` as `$body-bg`, so the portal chrome and the page agree.
- **Two are this theme's own literals in the platform namespace**: `$sp-tagline-color` and `$sp-navbar-divider-color` are declared here rather than left to the platform default (`D-120`).
- **Twenty-six are the Bootstrap 3.3.6 default, declared explicitly**, so the theme owns each value rather than inheriting it silently.
- **Twenty-one are component tokens, each chosen against WCAG 2.1 AA.** Fifteen restate the Bootstrap default because the measured pair already passes; **six replace a default that fails** — `$text-muted`, `$link-color`, `$link-hover-color`, `$label-default-bg`, `$label-info-bg` and `$badge-bg`. Every ratio is stated in the row and verified by [The contrast check](#the-contrast-check).

**Declare the rows in the order the table gives them.** Six rows resolve to another variable rather than to a literal — `$headings-font-family`, `$btn-primary-bg`, `$label-primary-bg`, `$badge-color`, `$badge-bg` and `$progress-bar-bg` — and each references a variable declared on an earlier row. A theme variables field is compiled ahead of Bootstrap's own variable file, so a reference to a Bootstrap variable this table does not itself declare would be undefined; reference only rows above.

| Group | Variable | Governs | Value to declare |
| --- | --- | --- | --- |
| Brand | `$brand-primary` | The primary action colour: the fill of `.btn-primary`, `.label-primary` and every `.progress-bar`. **Link text no longer resolves to it** — `$link-color` is declared separately below, because `#1976d2` measures only **4.22:1** on the page background. | `#1976d2` — the legacy link colour, **carried forward**. |
| Brand | `$brand-success` | Declared so the theme owns the value. **No component this portal applies resolves to it**: no `.alert-success`, `.label-success` or `.progress-bar-success` appears in any widget template. | `#5cb85c` |
| Brand | `$brand-info` | Declared so the theme owns the value. **No component this portal applies resolves to it**: the `Premium` marker's fill is `$label-info-bg` and `.alert-info` takes its fill from `$state-info-bg`, both declared below. White on this value measures **2.09:1**, which is why nothing textual is placed on it. | `#5bc0de` |
| Brand | `$brand-warning` | Declared so the theme owns the value. **No component this portal applies resolves to it**: `.alert-warning` takes its fill from `$state-warning-bg` and its text from `$state-warning-text`, both declared below. | `#f0ad4e` |
| Brand | `$brand-danger` | Declared so the theme owns the value. **No component this portal applies resolves to it**: `.alert-danger` takes its fill from `$state-danger-bg` and its text from `$state-danger-text`, both declared below. | `#d9534f` |
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
| Text | `$text-color` | The body text colour of the whole portal, inherited by every panel, table cell and list item. | `#333333` — Bootstrap 3.3.6's own default, declared explicitly so the theme owns it. **11.59:1** on `$body-bg`, **12.63:1** on `$panel-bg`. |
| Text | `$text-muted` | `.text-muted`, which carries every secondary caption in this portal: the pager range, the five truncation captions and the news byline. | `#595959` — **replaces** Bootstrap's `#777777`, which measures **4.11:1** on `$body-bg` and fails AA. This value measures **6.42:1** on `$body-bg` and **7.00:1** on `$panel-bg`. |
| Link | `$link-color` | Every `<a>` in a widget template, and `.btn-link`. | `#1565c0` — **replaces** the derived `$brand-primary`, which measures **4.22:1** on `$body-bg` and fails AA. This value measures **5.27:1** on `$body-bg` and **5.75:1** on `$panel-bg`. It is a darkened form of the carried-forward `#1976d2`, so the brand family is unchanged. |
| Link | `$link-hover-color` | The hover and focus colour of every link. | `#0d47a1` — declared explicitly rather than left to Bootstrap's `darken($link-color, 15%)`. **7.92:1** on `$body-bg`. |
| Label | `$label-color` | The text colour of every `.label`. | `#ffffff` — Bootstrap's default, declared explicitly, because every label fill below is chosen against **this** foreground. |
| Label | `$label-primary-bg` | `.label-primary`: the funding-stage, round-type and working-pattern markers. | `$brand-primary` — referenced rather than repeated. White on `#1976d2` measures **4.60:1** and passes AA. |
| Label | `$label-default-bg` | `.label-default`: the job-title, seniority and focus-area markers. | `#595959` — **replaces** Bootstrap's `#777777`, on which white measures **4.48:1** and fails AA by 0.02. White on this value measures **7.00:1**. |
| Label | `$label-info-bg` | `.label-info`: **the `Premium` marker**, the single most repeated gated-field treatment in the portal. | `#17607d` — **replaces** the derived `$brand-info` `#5bc0de`, on which white measures **2.09:1** and fails AA outright. White on this value measures **6.99:1**. |
| Badge | `$badge-color` | The text colour of every `.badge`: the four collection totals in the company profile's tab strip. | `$label-color` — referenced rather than repeated, because a badge is the same chip treatment as a label and the two must not drift. Resolves to `#ffffff`. |
| Badge | `$badge-bg` | The fill of every `.badge`. | `$label-default-bg` — referenced rather than repeated. **Replaces** Bootstrap's `$gray-light` `#777777`, on which white measures **4.48:1** and fails AA by 0.02 — the same failing default this table already replaces for `.label-default`, which `.badge` would otherwise keep because it reads a variable of its own. White on this value measures **7.00:1**. |
| Button | `$btn-default-color` | The label colour of `.btn-default`, which is every **Retry**, **Clear**, pager and tab-strip control. | `#333333` — Bootstrap's default, declared explicitly. **12.63:1** on `$btn-default-bg`. |
| Button | `$btn-default-bg` | The fill of `.btn-default`. | `#ffffff` |
| Button | `$btn-default-border` | The border of `.btn-default`. | `#cccccc` — a non-text boundary, not a text pair. |
| Alert | `$state-info-text` | The text colour of `.alert-info`, which carries every premium upsell and every empty state. | `#31708f` — Bootstrap's default, declared explicitly. **4.53:1** on `$state-info-bg`. |
| Alert | `$state-info-bg` | The fill of `.alert-info`. | `#d9edf7` |
| Alert | `$state-warning-text` | The text colour of `.alert-warning`, which carries the no-role and report-fallback notices. | `#8a6d3b` — Bootstrap's default, declared explicitly. **4.54:1** on `$state-warning-bg`. |
| Alert | `$state-warning-bg` | The fill of `.alert-warning`. | `#fcf8e3` |
| Alert | `$state-danger-text` | The text colour of `.alert-danger`, the error panel of all six widgets that can fail. | `#a94442` — Bootstrap's default, declared explicitly. **4.53:1** on `$state-danger-bg`. |
| Alert | `$state-danger-bg` | The fill of `.alert-danger`. | `#f2dede` |
| Progress | `$progress-bg` | The track of every `.progress`, in the results loading indicator and the chart's companion table. | `#f5f5f5` |
| Progress | `$progress-bar-bg` | The fill of every `.progress-bar`. | `$brand-primary` — **4.22:1** against the track, above the 3:1 that WCAG 2.1 requires of a meaningful non-text graphic. |

**Fifty-four declarations, and no value this portal applies resolves to a release default — foregrounds included.** The `$sp-*` namespace carries further entries beyond the three named above. This portal applies only these three, so only these three are declared. The authoritative list for a given instance is served per portal by the compiled bootstrap stylesheet; read it from that instance if a fourth entry is ever needed, and declare it here rather than in a widget.

Bootstrap's own derivation rules mean any variable **not** in the table above is computed from the ones that are, so the set above propagates consistently without being extended. `$navbar-inverse-border`, for example, is derived from `$navbar-inverse-bg`, and `$navbar-default-border` from `$navbar-default-bg`. **Declare exactly the fifty-four variables above and no others**; an extra declaration is a value the theme then owns and must maintain.

### The complete declaration block

Paste this into the theme record's **CSS variables** field exactly as it stands. It is the table above, in the same order, with nothing omitted and nothing added — **fifty-four declarations**, which is the whole of this portal's token surface. Six of them resolve to another variable rather than to a literal, deliberately, so each pair cannot drift.

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

// Text
$text-color: #333333;
$text-muted: #595959;

// Links
$link-color: #1565c0;
$link-hover-color: #0d47a1;

// Labels
$label-color: #ffffff;
$label-primary-bg: $brand-primary;
$label-default-bg: #595959;
$label-info-bg: #17607d;

// Badge
$badge-color: $label-color;
$badge-bg: $label-default-bg;

// Default button
$btn-default-color: #333333;
$btn-default-bg: #ffffff;
$btn-default-border: #cccccc;

// Alert states
$state-info-text: #31708f;
$state-info-bg: #d9edf7;
$state-warning-text: #8a6d3b;
$state-warning-bg: #fcf8e3;
$state-danger-text: #a94442;
$state-danger-bg: #f2dede;

// Progress
$progress-bg: #f5f5f5;
$progress-bar-bg: $brand-primary;
```

Three ordering rules govern the block, and each prevents a value that silently fails to apply:

1. **`$brand-primary` is declared before `$btn-primary-bg`**, and `$font-family-sans-serif` before `$headings-font-family`. A SASS variable referenced before it is declared resolves to nothing.
2. **`$sp-body-bg` repeats `#f5f5f5` as a literal rather than referencing `$body-bg`.** The `$sp-*` namespace is compiled from the platform's own partials, and a reference across that boundary is not guaranteed to resolve; a literal always does.
3. **No CSS rule appears in the block.** Only declarations. A rule placed in a variables field is duplicated once per consumer in the compiled output — see rule 2 of [Theme and variable authoring rules](#theme-and-variable-authoring-rules).

After saving the theme, confirm the values took effect by loading the portal and reading the computed `background-color` of `body`, which must be `rgb(245, 245, 245)`, and the computed `color` of a `.btn-primary`, whose background must be `rgb(25, 118, 210)`. A default-Bootstrap `#337ab7` on the button means the field did not compile; re-check that the block contains no CSS rule and no unclosed declaration.

Bootstrap derives a variable that is left undeclared from the ones that are: `$navbar-inverse-border` is computed from `$navbar-inverse-bg`. Those derivations remain in force for every Bootstrap variable outside the fifty-four above. `$sp-tagline-color` is still declared as the literal `#333333` rather than as a reference to `$text-color`, for two reasons that each hold on their own: `$text-color` is declared **after** it in the block, and a SASS reference to a variable declared later resolves to nothing; and the `$sp-*` namespace is compiled from the platform's own partials, across which a reference is not guaranteed to resolve. The two carry the same literal deliberately, which the contrast table below records as one pair rather than two.

### The contrast check

**Every text pair this portal renders is measured, and the measurement is reproducible.** A colour choice defended in prose is a colour choice nobody checked; the twenty-one pairs below are the complete set of foreground-on-background combinations the eight widgets produce, and the script that follows recomputes every ratio from the declared token values. Run it whenever a token in the Text, Link, Label, Button, Alert or Progress group changes.

| # | Pair | Foreground | Background | Ratio | Threshold | Result |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Body text on the page | `$text-color` `#333333` | `$body-bg` `#f5f5f5` | 11.59:1 | 4.5:1 | PASS |
| 2 | Body text in a panel | `$text-color` `#333333` | `$panel-bg` `#ffffff` | 12.63:1 | 4.5:1 | PASS |
| 3 | Muted caption on the page | `$text-muted` `#595959` | `$body-bg` `#f5f5f5` | 6.42:1 | 4.5:1 | PASS |
| 4 | Muted caption in a panel | `$text-muted` `#595959` | `$panel-bg` `#ffffff` | 7.00:1 | 4.5:1 | PASS |
| 5 | Link on the page | `$link-color` `#1565c0` | `$body-bg` `#f5f5f5` | 5.27:1 | 4.5:1 | PASS |
| 6 | Link in a panel | `$link-color` `#1565c0` | `$panel-bg` `#ffffff` | 5.75:1 | 4.5:1 | PASS |
| 7 | Link, hover and focus | `$link-hover-color` `#0d47a1` | `$body-bg` `#f5f5f5` | 7.92:1 | 4.5:1 | PASS |
| 8 | The `Premium` marker | `$label-color` `#ffffff` | `$label-info-bg` `#17607d` | 6.99:1 | 4.5:1 | PASS |
| 9 | Default marker | `$label-color` `#ffffff` | `$label-default-bg` `#595959` | 7.00:1 | 4.5:1 | PASS |
| 10 | Primary marker | `$label-color` `#ffffff` | `$label-primary-bg` `#1976d2` | 4.60:1 | 4.5:1 | PASS |
| 11 | Tab total badge | `$badge-color` `#ffffff` | `$badge-bg` `#595959` | 7.00:1 | 4.5:1 | PASS |
| 12 | Primary button | `$btn-primary-color` `#ffffff` | `$btn-primary-bg` `#1976d2` | 4.60:1 | 4.5:1 | PASS |
| 13 | Default button | `$btn-default-color` `#333333` | `$btn-default-bg` `#ffffff` | 12.63:1 | 4.5:1 | PASS |
| 14 | Info alert | `$state-info-text` `#31708f` | `$state-info-bg` `#d9edf7` | 4.53:1 | 4.5:1 | PASS |
| 15 | Warning alert | `$state-warning-text` `#8a6d3b` | `$state-warning-bg` `#fcf8e3` | 4.54:1 | 4.5:1 | PASS |
| 16 | Danger alert | `$state-danger-text` `#a94442` | `$state-danger-bg` `#f2dede` | 4.53:1 | 4.5:1 | PASS |
| 17 | Chart label text | `$sp-tagline-color` `#333333` | `$panel-bg` `#ffffff` | 12.63:1 | 4.5:1 | PASS |
| 18 | Chart bar | `$brand-primary` `#1976d2` via `currentColor` | `$panel-bg` `#ffffff` | 4.60:1 | 3:1 graphic | PASS |
| 19 | Progress bar on its track | `$progress-bar-bg` `#1976d2` | `$progress-bg` `#f5f5f5` | 4.22:1 | 3:1 graphic | PASS |
| 20 | KPI figure | `$brand-primary` `#1976d2` | `$panel-bg` `#ffffff` | 4.60:1 | 4.5:1 | PASS |
| 21 | Chart zero line | `$text-muted` `#595959` | `$panel-bg` `#ffffff` | 7.00:1 | 3:1 graphic | PASS |
| 22 | Focus ring, worst background | `$brand-primary` `#1976d2` | `$panel-default-heading-bg` `#f5f5f5` | 4.22:1 | 3:1 graphic | PASS |

Row 22 carries no number that rows 18 and 19 do not already produce — the ring is `$brand-primary`, so on a panel it is row 18's 4.60:1 and on a panel heading it is row 19's 4.22:1. It is listed anyway because it is a **different requirement**, not a different colour: rows 18 to 21 are graphics that convey data, whereas the ring is the focus indicator that [Busy, status and focus behaviour](#busy-status-and-focus-behaviour) puts a 3:1 floor under, and it is the only pair in this table whose background varies by widget. The row is entered at the worse of its two backgrounds so that the check fails if either surface regresses. The two headings that receive focus — `bst-company-profile`'s and `bst-investor-profile`'s — sit on `.panel-heading`, which is why `#f5f5f5` is the governing case even though `$panel-bg` is white.

Row 11 is a pair in its own right rather than a repeat of row 9, even though both resolve to white on `#595959`: `.badge` reads `$badge-bg` and `$badge-color`, which are variables of their own, so a theme that declares only the label tokens leaves every badge on Bootstrap's `#777777` and **4.48:1**. The two rows are declared as a reference pair for exactly that reason, and this row is what proves the reference took effect.

Rows 17 and 18 are separate because the chart draws two things on one background: `.bst-charts-text` fills from `$sp-tagline-color`, and every `<rect>` fills from `currentColor`, which resolves to `$brand-primary` through `.bst-charts .bst-charts-svg { color: $brand-primary; }`. The bar is a meaningful non-text graphic, so 3:1 applies to it and 4.5:1 to the text beside it; both clear their own threshold.

**The check.** Paste this into a shell — it needs Python 3 and nothing else, writes no file, and prints one line per pair followed by a failure count. It is the arithmetic of the table above rather than a restatement of it: the ratios are computed from the hex values, so a token edited in the declaration block but not here is caught by the mismatch rather than by review.

```bash
python3 - <<'EOF'
def lin(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def luminance(h):
    h = h.lstrip('#')
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


def ratio(fg, bg):
    a, b = luminance(fg), luminance(bg)
    hi, lo = max(a, b), min(a, b)
    return (hi + 0.05) / (lo + 0.05)


# The twenty-one pairs the eight widgets render, each named as the table names it.
# The last column is the WCAG 2.1 floor: 4.5 for text, 3.0 for a meaningful
# non-text graphic.
PAIRS = [
    ('body text on page',     '#333333', '#f5f5f5', 4.5),
    ('body text in panel',    '#333333', '#ffffff', 4.5),
    ('muted on page',         '#595959', '#f5f5f5', 4.5),
    ('muted in panel',        '#595959', '#ffffff', 4.5),
    ('link on page',          '#1565c0', '#f5f5f5', 4.5),
    ('link in panel',         '#1565c0', '#ffffff', 4.5),
    ('link hover on page',    '#0d47a1', '#f5f5f5', 4.5),
    ('Premium marker',        '#ffffff', '#17607d', 4.5),
    ('default marker',        '#ffffff', '#595959', 4.5),
    ('primary marker',        '#ffffff', '#1976d2', 4.5),
    ('tab total badge',       '#ffffff', '#595959', 4.5),
    ('primary button',        '#ffffff', '#1976d2', 4.5),
    ('default button',        '#333333', '#ffffff', 4.5),
    ('info alert',            '#31708f', '#d9edf7', 4.5),
    ('warning alert',         '#8a6d3b', '#fcf8e3', 4.5),
    ('danger alert',          '#a94442', '#f2dede', 4.5),
    ('chart label text',      '#333333', '#ffffff', 4.5),
    ('chart bar',             '#1976d2', '#ffffff', 3.0),
    ('progress bar on track', '#1976d2', '#f5f5f5', 3.0),
    ('KPI figure in panel',   '#1976d2', '#ffffff', 4.5),
    ('chart zero line',       '#595959', '#ffffff', 3.0),
    ('focus ring, worst bg',  '#1976d2', '#f5f5f5', 3.0),
]

failures = 0
for name, fg, bg, floor in PAIRS:
    value = ratio(fg, bg)
    verdict = 'PASS' if value >= floor else 'FAIL'
    if verdict == 'FAIL':
        failures += 1
    print('%-22s %-8s on %-8s %6.2f:1  needs %.1f:1  %s'
          % (name, fg, bg, value, floor, verdict))
print('FAILURES: %d' % failures)
EOF
```

The expected last line is `FAILURES: 0`. Three release defaults are deliberately **absent** from `PAIRS` because this theme replaces them, and any one reintroduced would fail: white on `$brand-info` `#5bc0de` measures **2.09:1**, `#777777` on `$body-bg` measures **4.11:1**, and white on `$gray-light` `#777777` — the default `.badge` and `.label-default` fill — measures **4.48:1**. Add them to `PAIRS` to watch the check reject them.

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
| `bst-company-profile` | `spUtil.recordWatch` on `x_bst_startuptrk_startup` | `c.data.startup` present **and** its `sys_id` a 32-character hexadecimal value | Destroying the child scope the watch was registered against — from `$scope.$on('$destroy', ...)`, and on a change of watched `sys_id`. `spUtil.recordWatch()` answers a promise, so there is no handle to unsubscribe |
| `bst-investor-profile` | `spUtil.recordWatch` on `x_bst_startuptrk_investor` | `c.data.investor` present **and** its `sys_id` a 32-character hexadecimal value | Destroying the child scope the watch was registered against — from `$scope.$on('$destroy', ...)`, and on a change of watched `sys_id`. `spUtil.recordWatch()` answers a promise, so there is no handle to unsubscribe |
| `bst-startup-results` | `$rootScope.$on('bst.search.criteria', ...)` | Nothing to guard; the payload is the event argument | The deregistration function `$rootScope.$on` returns, called from `$scope.$on('$destroy', ...)` |

Both parts are load-bearing, and each fails differently.

| Part omitted | What happens |
| --- | --- |
| The guard | Every server script in this guide has an unauthorised path and a not-found path, and on both of them the record object is **never published**. `c.data.startup.sys_id` on those paths raises a client `TypeError` before the template can render the notice it was written to render, so the caller sees a blank widget instead of "Your account holds no Boston Startup Tracker role" or "That company could not be found". These are expected paths, not error paths. |
| The release | A `$rootScope` listener is bound to the root scope and is **not** removed when the widget's own scope is destroyed. Navigating between portal routes therefore accumulates one live listener per visit, each still calling `c.server.update()` on a destroyed scope. A `recordWatch` subscription accumulates the same way when a server refresh registers a second one: `spUtil.recordWatch()` answers a **promise**, so there is no handle to release, and re-registering on every refresh leaves one live subscription per refresh. Registering once per watched `sys_id` against a child scope, and destroying that child scope, is what bounds it at one. |

### Rules that bind all eight

1. Every server script reads through `GlideRecordSecure` and serialises through `RestResponseBuilder.serialize()`. See [Step 6](#step-6--access-control-in-every-widget-server-script). This is not optional and has no exception.
2. No widget CSS contains a literal colour, spacing, radius or font value. See [Zero hard-coded values](#zero-hard-coded-values).
3. No widget uses an extra-small or small Bootstrap column class. See [Responsive stance — the 1024-pixel floor](#responsive-stance--the-1024-pixel-floor).
4. No widget references Lucide, and no widget uses an emoji character. Icons are the platform glyph font only. See [Iconography — the platform glyph font only](#iconography--the-platform-glyph-font-only).
5. Every widget CSS selector is scoped beneath the widget's own root class, and is at most three selectors deep.
6. A Script Include is constructed by its bare class name inside the scope — `new RestResponseBuilder()`, not `new x_bst_startuptrk.RestResponseBuilder()`.
7. Every server script **assigns** the authorisation result — `data.authorised = builder.hasAnyAppRole();` — and returns immediately when it is `false`. Calling the method without assigning it leaves `data.authorised` undefined, and every template below gates its usable content on that value.
8. Every widget implements [Busy, status and focus behaviour](#busy-status-and-focus-behaviour) and, where it loads asynchronously, [Error and empty behaviour](#error-and-empty-behaviour). Neither is optional and neither has an exception.
9. **Headings state structure, never size.** Each page renders exactly one `<h1>`, every panel heading is an `<h2 class="panel-title">`, and a heading inside a panel body is an `<h3>`. A value is never a heading: where a figure needs heading-scale type it is a `<p>` carrying the Bootstrap `.h2` utility class. The five `h1` owners and the nesting rule are under [Heading hierarchy](#heading-hierarchy).
10. Every interpolated link uses `ng-href`, never `href`. A plain `href` carrying `{{…}}` is followed with the raw braces before Angular substitutes them.
11. **A persisted external locator is bound only where it passed the application's URL allowlist on the way in, and an address is never bound as a link target.** See [External locators in a binding](#external-locators-in-a-binding).
12. **Every widget that renders a Bootstrap `.label` chip carries the forced-colours border rule for it.** Six of the eight do — `bst-startup-results`, `bst-company-profile`, `bst-investor-profile`, `bst-trends-charts`, `bst-account-summary` and `bst-premium-upsell` — and each declares it scoped to its own root:

    ```scss
    @media (forced-colors: active) {
        .bst-<widget> .label {
            border-style: solid;
        }
    }
    ```

    A `.label` conveys itself entirely by `background-color`, and forced colours discards that, so without the rule every chip in the family — including the `Premium` marker that is the visible face of the field-gating design — computes to plain bold text with `border: 0px none` and is indistinguishable from the words beside it. The declaration names only the style so that `border-width` stays the initial `medium` and `border-color` the initial `currentColor`: no measured literal enters the stylesheet, and the border is drawn in the caller's own resolved text colour, which is guaranteed to contrast with the caller's own background. The rule is repeated per widget rather than written once because rule 5 above scopes every selector beneath its widget's root; that repetition is the cost of the scoping rule and is accepted. **`forced-color-adjust: none` is not the alternative** — see the reasoning under [the results widget's CSS](#css-1).

13. **A `.label` that carries free text, rather than a fixed marker word, is allowed to wrap.** Bootstrap's `.label` sets `white-space: nowrap`, which suits `Premium` and suits a choice value of one or two words, and defeats anything longer: the chip becomes one unbreakable inline box, and a box that cannot break inside a container that cannot grow overflows its container and is painted over by whatever is laid out after it. Four of the eight widgets place a chip inside a `.list-group-item` — `bst-startup-results`, `bst-company-profile`, `bst-investor-profile` and `bst-account-summary` — and each of those whose chip text comes from data rather than from a fixed word declares:

    ```scss
    .bst-<widget> .list-group-item .label {
        white-space: normal;
        overflow-wrap: break-word;
    }
    ```

    `break-word` rather than `anywhere` is correct **here**, and the distinction is not cosmetic: these chips sit inside a `.list-group-item`, a block whose width the grid has already fixed, so the line box is bounded and `break-word` fires — measured, a 46-character unbreakable token wrapped to two fragments and then to three. The same declaration is inert in a shrink-to-fit context, which is why the upsell's chips use `anywhere` instead; [rule 16](#rules-that-bind-all-eight) sets out that case and why the two must not be harmonised onto one keyword.

    Both are behaviour keywords, so neither introduces a measured value. The rule matters most where the chip renders a **Multi-choice** value or a **role name**, because those are the two chip texts in this guide with no length bound: a focus area reading `Financial technology and payments infrastructure` overflowed its column by 97.63px at the 1024px floor, and a fully-qualified role name is longer still. It is stated separately from rule 12 because the two failures are unrelated — rule 12 restores a chip's shape when forced colours removes its background, and this rule keeps a chip inside the box it was given — and a widget can need one without the other. See the reasoning under [the investor widget's CSS](#css-3).

14. **Every `.table-responsive` carries `tabindex="0"`.** All six of them do — two in `bst-company-profile`, three in `bst-investor-profile`, one in `bst-trends-charts`. Bootstrap makes the wrapper `overflow-x: auto` below its small breakpoint, and a region that scrolls but cannot be focused cannot be scrolled from the keyboard at all: the content is reachable with a mouse or a touch drag and by no other means, which is WCAG 2.1.1. Adding the attribute costs one tab stop before the table's own links and makes the region focusable and therefore arrow-scrollable.

    The honest caveat is that **this portal's supported floor is 1024px** and the wrapper only overflows below Bootstrap's `768px`, so on the supported range the condition never arises. It is applied anyway, for two reasons. The construct is identical in all six places, and a rule that holds in one of six identical constructs is the kind of drift this section exists to prevent. And the floor is a statement about what is *designed for*, not a guarantee about what a caller's window will be — a browser zoomed to 200% at 1024 reports a 512px layout viewport, which is inside the overflow range without the caller ever resizing anything.

15. **Every widget that renders an `.sr-only` node re-declares the three properties that hide it.** Five of the eight do — `bst-startup-results`, `bst-company-profile`, `bst-investor-profile`, `bst-trends-charts` and `bst-account-summary`. The other three carry no such rule, because they render no such node, and the roster is stated per widget so it can be audited by grep rather than trusted: `bst-startup-search` renders neither a status region nor a table caption — the status region belongs to [the four widgets whose content changes](#busy-status-and-focus-behaviour), and this widget submits a query rather than displaying a result; `bst-trends-kpi` renders no table and no status region; and `bst-premium-upsell` renders neither. A rule with no node to act on is dead weight in a stylesheet, so none of the three carries one:

    ```scss
    .bst-<widget> .sr-only {
        position: absolute;
        overflow: hidden;
        clip: rect(0, 0, 0, 0);
    }
    ```

    `.sr-only` is a **Bootstrap** class, so a widget that renders one is depending on a stylesheet it does not own to keep that text off the screen. When that stylesheet is absent the class means nothing, the node reverts to a static full-width block, and the status text becomes ordinary body copy — measured, `position: static; clip: auto; width: 1200px`, with the screen-reader sentence rendered as visible prose in the middle of the page. Re-declaring the three properties that do the hiding makes each widget self-sufficient for the one thing it cannot afford to get wrong.

    The three declarations are chosen to be **exactly** Bootstrap's own values for those properties, so when Bootstrap *is* present — which is every real render — the computed style is unchanged and the rule is invisible. Width, height and the negative margin are deliberately **not** re-declared: they are what shrink the box, and re-declaring `width: 1px` would put a measured literal in widget CSS, which [zero hard-coded values](#zero-hard-coded-values) forbids. They are not needed either, because an absolutely positioned box clipped to `rect(0, 0, 0, 0)` is out of flow and paints nothing, whatever its intrinsic size. All three values here are `0` or behaviour keywords, both of which that rule permits.

16. **Each host re-states the two `bst-premium-upsell` declarations that nothing else supplies, because an embedded partial's CSS field is not guaranteed to reach the page.** Service Portal compiles widget CSS per page and prefixes every rule with a class derived from the widget record, so what arrives is the CSS of the widgets *instanced on that page*. This partial is instanced nowhere: all three hosts build it in their server script with `$sp.getWidget()` and render it through `<sp-widget>`, which creates no instance record, so its CSS field may never be compiled in. Measured in a render where it was not, exactly two of its declarations were the sole source of their effect and both were lost — the alert heading sat flush against the body text at a **`0px`** gap instead of one spacing step, and a field chip computed Bootstrap's `white-space: nowrap` instead of wrapping. Each host re-states those two, scoped to the partial inside its own root:

    ```scss
    .bst-<host> .bst-upsell {
        margin-bottom: $grid-gutter-width;
    }

    .bst-<host> .bst-upsell .panel-title {
        margin-bottom: $padding-base-vertical;
    }

    .bst-<host> .bst-upsell .bst-upsell-fields {
        margin-top: $padding-base-vertical;
        margin-bottom: $padding-base-vertical;
    }

    .bst-<host> .bst-upsell .bst-upsell-fields .label {
        margin-right: $padding-base-vertical;
        white-space: normal;
        overflow-wrap: anywhere;
    }
    ```

    **The test each rule had to pass to be on that list is that nothing else on the host supplies its effect**, and it was applied by measuring the host render against the partial rendered on its own rather than by reading the stylesheets. Two of the partial's seven rules failed the test and are deliberately **not** re-stated, because they would change nothing: `.bst-upsell .btn:focus { outline-style: auto }`, since Bootstrap's own `a:focus` and `.btn:focus` already draw that ring on an `<a class="btn">`; and the `@media (forced-colors: active)` chip border, which the host's [rule 12](#rules-that-bind-all-eight) block already supplies to every `.label` under its root. `border-radius` is dropped from the first rule for the same reason — Bootstrap's `.alert` already resolves it to the same token value — while `margin-bottom` is kept, because `.alert` sets a different one. A fifth rule, `.bst-upsell .bst-upsell-guidance { margin-bottom: 0 }`, is re-stated by **`bst-account-summary` only**: the guidance paragraph renders under `c.isAccount()`, so on the other two hosts that selector would match no node, and a rule with nothing to act on is the dead weight [rule 15](#rules-that-bind-all-eight) exists to keep out of a stylesheet.

    The last rule is the partial's own chip rule **selector for selector**, with the host root prepended. That is deliberate on two counts. It targets exactly the same elements — chips in the field list, not every `.label` the partial might ever render — so the host cannot restyle something the partial did not intend. And prepending the root makes it one class more specific than the original, so where a page does load both, the cascade resolves on specificity rather than on stylesheet append order; a bare `.bst-<host> .bst-upsell .label` would have tied the partial's rule at three classes and been decided by whichever sheet happened to be appended last.

    **All three declarations in that rule are load-bearing, and `margin-right` is the one that is easy to get wrong.** Only `bst-company-profile` has a `.label` rule broad enough to reach a chip in the partial; the investor and account stylesheets scope theirs to `.list-group-item .label`, which a `ul.list-inline` chip is not inside, so on those two hosts the chips separated by Bootstrap's `10px` of `li` padding alone instead of the `16px` the reference render shows. Re-stating `margin-right` is what makes the three hosts agree with each other and with the partial rendered on its own.

    The partial keeps every one of these rules in its own CSS as well, so it remains correct on its own terms, and the duplicates are inert wherever the platform does compile it in: the declarations are identical and resolve from the same tokens, so the two sources cannot disagree on a value.

    **The coupling runs in both directions, and the second direction is the easier one to miss.** A host rule written against a **Bootstrap** class rather than an application class reaches every node under the host root — including the embedded partial's, which the partial's own stylesheet may not be present to defend. Measured, `.bst-investor .panel-title { line-height: normal }` did exactly that: it outranks Bootstrap's `h1, h2 { line-height: 1.1 }` on specificity, so it applied to the partial's `<h2 class="panel-title">`, rendered it **19.000px** tall instead of **17.594px**, and displaced every element below it in the alert by **1.406px** — a difference invisible to the eye and unambiguous to a measurement, and one the other two hosts did not have. That rule exists for the investor's `<h1>`, which carries the record's **name** and can therefore wrap; the three `<h2>` panel titles beneath it are fixed one-line copy that never needed it, and the partial's heading is not this widget's to style at all. It is now scoped `.bst-investor h1.panel-title`, which is the heading it was written for and the one heading the partial cannot own — a case where the element genuinely matters and the class alone is too broad, notwithstanding that [`.panel-title` is a class rather than a level](#heading-hierarchy) everywhere else in this guide.

    Auditing the other two hosts the same way leaves two rules that reach the partial and are **deliberately** left doing so, because each supplies exactly what the partial asks for: `.bst-company .label { margin-right: $padding-base-vertical }` gives the chips the margin the partial's own rule gives them, and the host's `@media (forced-colors: active)` block gives them the border — the second of the two omissions above depends on precisely that reach. Both are now also stated explicitly by the re-statement at a higher specificity, so neither is relied on by accident. No other host rule matches any node the partial renders: its nodes are `.alert`, `.panel-title`, `.list-inline`, `.label`, `.btn` and one paragraph, and every remaining host rule is scoped to `.nav-tabs`, `.media-heading`, `.list-group-item`, `.list-group-item-heading`, `.table-responsive`, `.sr-only`, `.panel` or an application class, none of which the partial uses.

    `bst-startup-results` is outside this rule entirely: it renders the same gap **G5** notice *inline* rather than embedding the partial, so its equivalent rules live in its own stylesheet and are compiled with the widget that is on the page.

    **Why these chips use `overflow-wrap: anywhere` where [rule 13](#rules-that-bind-all-eight) uses `break-word`.** The two keywords differ in one respect that decides this case: `anywhere` contributes to a box's intrinsic **min-content** width and `break-word` does not. Rule 13's chips sit inside a `.list-group-item`, a block whose width the grid has already fixed, so the line box is bounded no matter what the text does and `break-word` fires — measured, a 46-character unbreakable token wrapped to two fragments and then three. These chips sit inside a `.list-inline > li`, which Bootstrap makes `display: inline-block` and which is therefore **shrink-to-fit**: its width is `min(max(min-content, available), max-content)`. With `break-word` the min-content width is still the whole token, so the `li` takes the token's full max-content width, the line box inside it is exactly as wide as the token, the text never overflows its own line box, and the declaration can never fire — measured, a 240-character token rendered as one fragment and overflowed the alert by **96.31px** with the rule fully present, and deleting the rule changed the layout by nothing at all. `anywhere` lowers min-content to a single character, so the `li` shrinks to the space available and the token breaks inside it — measured, the same token wrapped to two fragments and stayed inside the alert. Both are behaviour keywords, so neither introduces a measured value. **Do not harmonise the two rules onto one keyword**: `break-word` is inert here, and `anywhere` in a rule-13 position would let an ordinary multi-word value break mid-word when wrapping at its spaces would have sufficed.

### External locators in a binding

Six of the values these widgets bind into an `ng-href` or `ng-src` target are **external locators stored by the application**, not internal page links: `Startup.website`, `Startup.logo_url`, `Founder.linkedin_url`, `Executive.linkedin_url`, `Investor.website` and `FundingRound.source_url`. `Founder.contact_email` and `Executive.contact_email` are the two stored addresses.

**Every one of those eight values passed `RestQueryHelper.isHttpsUrl()` or `RestQueryHelper.isEmailAddress()` before it was stored, on every write path there is.** The REST create and update contract calls those two methods, and so does `IngestionMapper.coerceField()` before any staging-to-entity write, so a locator that could not be submitted through the API cannot have been written by an ingestion run either. That single allowlist is specified in [`../api-reference.md`](../api-reference.md#one-validator-both-write-paths); its effect here is that a stored locator is an absolute `https` URL with no user information before the `@` in its authority, and can therefore carry neither a `javascript:` nor a `data:` scheme nor an embedded credential.

Three rules follow for these widgets, and each names what it prevents:

1. **Bind a stored locator only through `ng-href` or `ng-src`, never through `href`, `src`, `ng-bind-html` or `$sce.trustAsResourceUrl`.** The first two are the sanitised bindings; `href` with raw braces exposes the un-substituted value, and the last two remove the sanitisation the framework applies.
2. **Never bind a stored address as a link target.** `contact_email` renders as **text**, as the People pane below does, and not as a `mailto:` target. The address allowlist admits no scheme, so a `mailto:` target would have to be assembled in the template, and an assembled target is a second construction site for a rule that has one home.
3. **Never bind a value this widget assembled from more than one stored field into a locator position.** Concatenating a stored value into a URL re-opens the scheme question the allowlist closed. Every locator bound below is a single column's value, verbatim.
4. **Guard every locator anchor on the presence of its own value, and render no anchor when the value is empty.** All six locator columns are `mandatory=false`, so empty is an ordinary state rather than an edge case, and an `ng-href` that interpolates to the empty string makes the framework **remove the `href` attribute altogether** — leaving an element that is styled as a link, announced as text, and not reachable by keyboard, which promises a destination that does not exist. Where the anchor's text is a record's own title, as in the Jobs and News panes, render that title in a `<span>` on the empty branch so the row keeps its title and loses only the link; where the anchor's text is a fixed label, as in the two Website rows, render `Not recorded` in a `.text-muted` span instead. Both branches are always present, so no cell is ever blank and no cell is ever a dead link.

**The allowlist is an input-boundary reduction, not a substitute for the framework's own output sanitisation.** Both apply, and neither is relied on alone.

### Busy, status and focus behaviour

Applies to **all eight** widgets. Two contracts: a busy state on the widget root, and — for the four widgets whose content changes after the first render — one polite status region.

**The busy state, on all eight.** Every client controller declares `c.busy`, `true` while there is no `data` payload to render and `false` once there is one, and every widget's root element carries `aria-busy="{{c.busy}}"`. A widget that later reloads from the server sets `c.busy` back to `true` for the duration of that reload. Four widgets — `bst-startup-search`, `bst-trends-kpi`, `bst-trends-charts` and `bst-premium-upsell` — never reload after their first render, so their `c.busy` transitions to `false` once and stays there.

**Derive the construction-time value from the payload; do not assert it.** In Service Portal the widget's server script runs *before* the widget is delivered, so `c.data` is **already populated when the client controller constructs** — the first payload has arrived by the time there is a controller to observe it. A controller that opens with a bare `c.busy = true` therefore never clears it, because the only thing that clears the flag is `c.load()`, and `c.load()` is called by `c.retry()` and by user-initiated reloads, never by the initial render. The consequence is not subtle and it is not confined to assistive technology: the indeterminate progress bar is gated on `ng-if="c.busy"`, so it stays in the DOM on every route for the life of the page, the widget root reports `aria-busy="true"` forever, and `c.statusText()` returns `Loading` from row 1 of the ordering table above and so **never announces any outcome at all** — not the loaded state, not an empty collection, not a not-found record. The one declaration that closes it:

```javascript
// The first payload is already on `c.data`, because the server script ran before this
// widget was delivered. So the flag is DERIVED from the payload rather than asserted
// true: there is nothing to wait for on the initial render, and c.load() owns every
// true-then-false cycle after it.
c.busy = !c.data;
```

Verify it rather than assume it: on each of the five routes, with the page settled, `aria-busy` must read `false` on every widget root, no `[role="progressbar"]` may remain in the document, and the polite region must state the widget's loaded or empty wording rather than `Loading`.

**The visible busy affordance, on the three widgets that reload.** `bst-startup-results`, `bst-company-profile` and `bst-investor-profile` each render one indeterminate striped progress bar under `ng-if="c.busy"`, which is the gap **G3** resolution recorded in [`../gaps-and-flags.md`](../gaps-and-flags.md). The delivered markup is this, and the width is the load-bearing part of it:

```html
<div class="progress" ng-if="c.busy">
  <div class="progress-bar progress-bar-striped active" role="progressbar"
       ng-style="c.indeterminate()"
       aria-label="Loading startups" aria-valuemin="0" aria-valuemax="100"
       aria-valuetext="Loading"></div>
</div>
```

Three properties of that markup, each of which closes a way for the affordance to be present in the document and invisible on screen:

- **A full width is required, and it is bound on the element with `ng-style="c.indeterminate()"` rather than declared in widget CSS.** Bootstrap 3.3.6 declares `.progress-bar { float: left; width: 0; height: 100%; … }`, so a bar with no width is **zero pixels wide**: the stripe animation runs on a zero-area box, the trough's `overflow: hidden` guarantees nothing can escape it, and the caller sees an empty grey trough during every load and every retry. The value sits on the element for the same reason the chart's `width="100%"` does — [zero hard-coded values](#zero-hard-coded-values) forbids a percentage literal in **widget CSS**, and this is the same element-attribute route that rule already sanctions for `.bst-charts-svg`. It is also Bootstrap's own documented markup for an indeterminate bar.
- **No `aria-valuenow`.** The bar reports no determinate position, so the attribute is omitted and `aria-valuetext="Loading"` carries the state instead. A `progressbar` with a full width and `aria-valuenow="100"` would announce a completed load.
- **The stripe animation is switched off under `prefers-reduced-motion`.** Each of the three widgets carries the rule below in its own CSS, scoped beneath its own root class. Without it, giving the bar a width converts a motionless defect into a real WCAG 2.3.3 one: `progress-bar-stripes` is a 2-second infinite animation that would then be genuinely visible.

```scss
@media (prefers-reduced-motion: reduce) {
    .bst-results .progress-bar {
        animation: none;
    }
}
```

`animation: none` is one of the permitted literals, so the guard adds no measured value to any widget CSS. `.progress-bar-striped` keeps its gradient, so the bar remains visibly a progress bar; only the movement stops.

**The status region, on the four widgets whose content changes.** `bst-startup-results`, `bst-company-profile`, `bst-investor-profile` and `bst-account-summary` each carry exactly one region of the form below, placed as the first child of the `.panel-body` so it precedes the content it describes:

```html
<div class="sr-only" role="status" aria-live="polite" aria-atomic="true">{{c.statusText()}}</div>
```

`.sr-only` is Bootstrap's own screen-reader utility, so the region is announced without occupying layout. `c.statusText()` returns exactly one string, chosen in this order — the first condition that holds wins, so a caller never hears two states at once:

**A widget that shows a busy affordance hides the stale view behind it.** All three reloading widgets gate their success block on `!c.busy`, not on `data` alone:

```html
<div ng-if="data.authorised &amp;&amp; !c.busy &amp;&amp; !data.error">
  <!-- the whole success view, including every count, caption and truncation notice -->
</div>
```

Without that term the progress bar and the previous payload render **at the same time**, under a root that is simultaneously announcing `aria-busy="true"` and a status region reading `Loading`. The result contradicts itself in three ways at once: a screen reader is told the region is busy while the accessibility tree still exposes the whole of the old record; a sighted caller sees a loading bar above content that looks current and has no way to tell which parts are stale; and every count, caption and truncation notice in the view is asserting a total that belongs to the *previous* record. The last of those is the dangerous one on the two profile widgets, because a reload here is how the caller moves **from one record to another** — so the figures on screen during the reload are not merely out of date, they belong to a different company or investor.

`c.busy` is the only correct discriminator for this, and `data` is not: `data` still holds the previous payload for the whole duration of the reload, which is exactly why gating on it fails. The three widgets must agree, because a caller who learns the loading behaviour on one screen carries that expectation to the other two.

| Order | Condition | Text returned |
| --- | --- | --- |
| 1 | `c.busy` is `true` | `Loading` |
| 2 | `data.authorised` is `false` | the empty string — **nothing**. The visible `.alert.alert-warning` carries `role="alert"` and owns this state. |
| 3 | `c.errorText()` returns a message | the empty string — **nothing**. The visible `.alert.alert-danger` carries `role="alert"` and owns this state. |
| 4 | the widget's primary collection is empty | the empty string — **nothing**. The visible empty-state `.alert.alert-info`, or the single `.list-group-item` where the collection is a list inside a panel, carries `role="status"` and owns this state. |
| 5 | otherwise | the widget's own loaded wording, given in its section below |

**One fact, one announcer.** Every row above but the last returns the **empty string**, because in each of those three states a *visible* element already carries the fact and already carries the live-region role that announces it. Two live regions carrying one fact are announced as two events, and a caller then hears the same state twice with no way to tell whether it happened twice. The visible element wins in all three cases for the same reason: it is the element a sighted caller reads, it is the element that carries the recovery control where there is one — **Retry** on the error panel — and it persists, whereas the polite region is a transient announcement of a change.

The three states and their owners:

| State | The element that owns it | Its role | Why it, and not the status region |
| --- | --- | --- | --- |
| Not entitled | the `.alert.alert-warning` | `role="alert"` | The denial is the one message a denied caller most needs, and it must interrupt rather than wait. Without this row `statusText()` would fall through to row 4 and announce the *empty-collection* wording to a caller who was denied by role, contradicting the visible warning on the same screen. |
| Failed | the `.alert.alert-danger` | `role="alert"` | It interrupts, and it is the only one of the two that carries **Retry**. |
| Empty | the empty-state `.alert.alert-info`, or the `.list-group-item` | `role="status"` | An empty result is not an error and must not interrupt, so it is `status` rather than `alert`. Announcing it from the visible element rather than from the polite region is what keeps the caller from being told the same sentence twice. |

**The polite region therefore speaks in exactly one state: loaded.** It resumes at row 5 once a retry settles, and its wording is a summary — a count against a total — that no visible element duplicates verbatim.

**The three visible owners are live regions; no other alert is.** An `.alert` that merely restates something the loaded status wording or a visible heading already carries takes **no** role and **no** `aria-live`, or the caller hears it twice. Each widget's section names which of its alerts carry a role, and the [error and empty behaviour](#error-and-empty-behaviour) section states the rule once.

**Focus behaviour, defined per interaction.** Only three interactions in this portal move focus, and no other interaction moves it:

| Interaction | Focus destination |
| --- | --- |
| A search is submitted from `bst-startup-search` and the results arrive on the same page | The `<h2 class="panel-title">` of `bst-startup-results`, which carries `tabindex="-1"` so it can receive programmatic focus. The caller lands on the heading that states the result count. |
| The retry control of any error panel succeeds | The retrying widget's own **primary heading**, which carries `tabindex="-1"` for that purpose: the `<h2 class="panel-title">` on `bst-startup-results`, the `<h1 class="panel-title">` on `bst-account-summary`, the `<h1 class="media-heading">` carrying the company name on `bst-company-profile` and the `<h1 class="panel-title">` carrying the investor name on `bst-investor-profile`. |
| A tab is selected on `bst-company-profile` | The selected tab control itself, per the roving-`tabindex` contract under [The tab contract](#the-tab-contract). Focus never jumps into the panel. |

**A control that stops being operable while it holds focus hands focus on before it does.** Two ways a control stops being operable, and the rule covers both:

| How it stops being operable | Where it happens | What must happen first |
| --- | --- | --- |
| It is **removed from the document** | the **Retry** button when a retry succeeds; a pager button inside a region an `ng-if` drops | It hands focus to the destination in the table above before the removal. |
| It is **disabled in place** by `ng-disabled` | **Previous** when a load lands on the first page; **Next** when a load lands on the last page | It hands focus to the **other** pager button when that one is still operable, and to the widget's primary heading when neither is. |

The second row exists because the pager buttons are never removed — they are `ng-disabled`, so they stay in the document and simply become inert. A browser drops focus from an element that becomes `disabled` while focused, and it drops it to the document body, from which a keyboard caller on `bst-startup-results` must Tab past every card link in the set to reach the pager again. Handing focus to the sibling pager button keeps the caller where they were working; handing it to the primary heading when both buttons are inert puts them at the top of the answer rather than at the top of the document.

**The handoff is conditional on the control holding focus *from the keyboard*, and `document.activeElement` alone cannot establish that.** A pager step the caller made with a pointer, or a load no control initiated, must move nothing. The obvious test — is `document.activeElement` the control about to stop being operable — does not deliver that, because a mouse press on a `<button>` makes it the active element in Blink and in Firefox on Windows. Testing `activeElement` therefore hands focus onward for a pointer caller too, dragging them to a control they never asked for, and the fault is invisible on the platforms that do not focus a button on press.

**The discriminator is `:focus-visible`.** The control is asked, synchronously and before anything changes, whether the browser considers its focus worth *showing* — which is true for a keyboard caller and false for a pointer caller, on every engine, by the same heuristic the browser already uses to decide whether to paint a ring. So the handoff runs exactly when a visible focus indicator is about to disappear, which is the harm the rule exists to prevent, and it stays still when there was no indicator to lose. A browser too old to evaluate `:focus-visible` moves nothing, which is the safe direction.

**The handoff is a `.focus()` call, and prose alone does not make it happen.** Each of the six widgets that renders a **Retry** declares the helper below. `c.retry()` calls it **before** `c.load()`, because the Retry button is removed the instant `data.error` clears and a handoff scheduled only for after the load would be reaching for an element that has already gone; `c.load()` then schedules it again once the payload has rendered, so focus finishes on the heading that states the new content rather than on the button that no longer exists.

```javascript
// The record-bound heading does not exist while the error panel is showing, so the
// destination is resolved at the moment of the move rather than captured once: the
// primary heading if it is in the document, otherwise the widget root, which carries
// tabindex="-1" for exactly this case. Either way focus never falls to document.body.
c.focusDestination = function () {
    var heading = $element[0].querySelector('[tabindex="-1"]');
    var target = heading || $element[0];
    if (target && target.focus) {
        target.focus();
    }
};
```

Each of the six widget roots therefore carries `tabindex="-1"` as well, as the fallback destination, and **the destination must show a visible focus indicator when it receives focus programmatically**. A heading moved into focus with no ring is a caller who has been silently relocated: the reading position has changed and nothing on screen says so. Bootstrap styles no indicator for `[tabindex="-1"]`, so each widget declares one, scoped to itself:

```scss
.bst-results [tabindex="-1"]:focus {
    outline: $border-radius-small solid $brand-primary;
    outline-offset: $border-radius-small;
}
```

The `$brand-primary`-on-`$panel-bg` pair is measured at 4.60:1 in [The contrast check](#the-contrast-check), comfortably past the 3:1 a non-text indicator needs. Repeat the rule for `.bst-company`, `.bst-investor`, `.bst-account`, `.bst-kpi` and `.bst-charts` — and pair each with the root-level form `.bst-results[tabindex="-1"]:focus`, because on `bst-trends-kpi` and `bst-trends-charts` the root **is** the destination: neither renders a heading that carries the attribute, so a descendant-only selector would never match them.

**The width and the offset are taken from the radius scale, and that is a deliberate choice rather than an oversight.** Bootstrap 3.3.6 publishes no outline-width variable — the framework removes the outline rather than styling it — so there is no semantically-matching token to reach for. `$border-radius-base` and `$border-radius-small` are the only 4-pixel and 3-pixel lengths the scale defines, and [Design system](#design-system) admits no measured literal, so the alternatives were a hard-coded `4px`, which the checklist forbids, or a spacing token whose smallest values are 1 and 5 pixels and whose meaning is padding rather than a rule width. Using the radius pair keeps the ring on the scale and keeps the declaration literal-free; the cost is that the token names describe a corner rather than a stroke, which is recorded here so a later reader does not "correct" it into a literal.

The same pair sizes the search controls' ring under [`bst-startup-search`](#bst-startup-search), so every focus indicator in the portal is one width and one offset.

**An `<a class="btn">` must answer SPACE as well as ENTER.** A native `<button>` answers both; an anchor answers only ENTER, and SPACE instead performs its default page scroll — so a caller who has learned that the control is a button presses SPACE, the page jumps, and nothing is activated. Seven controls in this portal are anchors styled as buttons: **View profile** on every result card and the results upsell call to action, **Back to search** on the company, investor and account widgets, **Browse startups** on the KPI panel, and the upsell partial's own call to action. Each binds the shared handler:

```javascript
// Space on an anchor scrolls the page and activates nothing. preventDefault() stops the
// scroll; click() activates the control the caller believes they are pressing. Enter
// needs nothing - the browser already activates an anchor on Enter.
c.onButtonKey = function (event) {
    if (event.which === 32 || event.keyCode === 32) {
        event.preventDefault();
        event.currentTarget.click();
    }
};
```

bound as `ng-keydown="c.onButtonKey($event)"`. The tab strip on `bst-company-profile` already does this for its own keys and is the precedent; these seven are the controls it was never extended to.

**The indeterminate progress bar needs a width, or it paints nothing.** Bootstrap's `.progress-bar` ships `width: 0%` so that a determinate bar can be driven by an inline width, and the four widgets that render an indeterminate striped bar — `bst-startup-results`, `bst-company-profile`, `bst-investor-profile` and `bst-account-summary` — supply none — which means the stripe animation runs inside a bar that is zero pixels wide, and the caller sees an empty trough. The width comes from the controller, not the widget CSS, for the same reason `c.barStyle()` does under [`bst-trends-charts`](#bst-trends-charts): a percentage is a measured value and [Design system](#design-system) admits none in widget CSS, but a bound value is not a declaration.

```javascript
// An indeterminate bar fills its trough: there is no proportion to express, so the
// full width plus the stripe animation is the convention, and the alternative - a
// bar of zero width - communicates nothing at all.
c.indeterminate = function () {
    return { width: '100%' };
};
```

bound as `ng-style="c.indeterminate()"` on each of the four `.progress-bar.progress-bar-striped.active` elements. **Each of those four widgets' controller items must name `c.indeterminate()` explicitly, and the template markup alone is not enough.** AngularJS guards a null callee, so `ng-style="c.indeterminate()"` on a controller that never declared the method evaluates to `undefined` and applies nothing — without throwing, without a console message, and with the element still in the DOM carrying every one of its ARIA attributes. Bootstrap's `width: 0%` then stands and the caller sees an empty trough, which is indistinguishable from the defect this whole section exists to fix. A build that adds the bar to a template and forgets the controller half has moved from an absent element to an invisible one and fixed nothing. **All four asynchronous widgets carry one.** `bst-account-summary` declares `c.busy` and reflects it in `aria-busy`, so a build that gave it no bar told assistive technology that work was in progress and showed a sighted caller nothing at all on that route; the two channels must agree. The bar's `$progress-bar-bg` on `$progress-bg` is row 19 of [The contrast check](#the-contrast-check) at 4.22:1.

### Controller dependencies

**Four platform services are injected into every client controller that uses the shared helpers**, and a helper referencing a service the controller did not ask for throws at construction rather than at the moment of use — so the injection list is part of the contract, not a detail:

| Service | Used by | Where it is specified |
| --- | --- | --- |
| `$scope` | the record watches on both profile widgets | [Every listener a controller registers is released on `$destroy`](#every-listener-a-controller-registers-is-released-on-destroy) |
| `$element` | `c.focusDestination()`, to find this widget's own focus destination rather than another widget's | [Busy, status and focus behaviour](#busy-status-and-focus-behaviour) |
| `$timeout` | `c.load()`, to move focus after the digest that renders the payload | [Error and empty behaviour](#error-and-empty-behaviour) |
| `$filter` | `c.money()`, `c.day()` and `c.count()` | [The display contract](#the-display-contract) |
| `spUtil` | `spUtil.recordWatch()` on both profile widgets | [Every listener a controller registers is released on `$destroy`](#every-listener-a-controller-registers-is-released-on-destroy) |

`$element` is what scopes the focus move: `bst_dashboard` renders **two** instances of `bst-trends-charts` and `bst_home` renders two widgets side by side, so a destination resolved with a document-wide query would move focus into whichever widget happens to appear first in the document rather than the one the caller acted on.

### The display contract

**A figure or a date is formatted by the widget, never by the payload.** `RestResponseBuilder.valueOf()` returns a currency element as `String(record.getValue(field))` — the **raw stored value**, which on a ServiceNow currency element carries its denomination as a prefix, so `{{round.amount_usd}}` renders `USD;56700000`. It returns a `glide_date` through its plain branch, so `{{round.round_date}}` renders `2024-01-10`. And it returns an integer as a JavaScript number, so a count renders with no thousands separator. None of those three is wrong as a *value*; all three are wrong as *output*, and the defect they share is that presentation ends up depending on the shape of the payload rather than on a decision the portal made. That dependency is what makes it dangerous: a fixture or a single record that happens to carry a pre-formatted string makes the surface look correct while every other record on the same page does not, and the inconsistency reads as data quality rather than as a missing filter.

Three helpers, declared by every widget that renders a figure or a date, and used in **every** such position:

```javascript
// The stored currency value may arrive as "USD;56700000" or as "56700000". Take the
// part after the last semicolon, which is the amount under both shapes, and reject
// anything non-numeric rather than printing NaN.
c.money = function (value) {
    if (value === undefined || value === null || value === '') {
        return '';
    }
    var raw = String(value);
    var amount = parseFloat(raw.substring(raw.lastIndexOf(';') + 1));
    if (isNaN(amount)) {
        return '';
    }
    return $filter('currency')(amount, '$', 0);
};

c.day = function (value) {
    return value ? $filter('date')(value, 'mediumDate') : '';
};

c.count = function (value) {
    return (value === undefined || value === null || value === '')
        ? ''
        : $filter('number')(value, 0);
};
```

**The empty string, not a zero and not a dash.** A denied premium field is an *absent key*, and every template already branches on `=== undefined` to render its `Premium` marker, so these helpers only ever see a value that is present. They still return the empty string on an unparseable one, because a figure the portal cannot read is better shown as nothing than as `NaN` or as a `$0` that the caller would take for a real amount.

**Where each is used**, exhaustively — a position left unformatted is the defect returning. The truncation captions are the easiest to miss and were: they print a total rather than a field value, so they do not look like currency-or-date positions, and on a fixture whose totals are all below a thousand an unformatted caption is **indistinguishable from a formatted one**. Two of the eight rendered four-digit totals with no separator beside a page that formatted every other figure.

| Helper | Every position that uses it |
| --- | --- |
| `c.money` | `bst-startup-results` card `total_funding_usd`; `bst-company-profile` overview `total_funding_usd` and its funding table's `amount_usd` and `valuation_usd`; `bst-investor-profile` overview `aum_usd`, its portfolio table's `total_funding_usd`, and `amount_usd` and `valuation_usd` in **both** rounds tables |
| `c.day` | `bst-company-profile` funding table `round_date`, jobs table `posted_date`, news list `published_date`; `bst-investor-profile` `round_date` in both rounds tables |
| `c.count` | `bst-trends-kpi` panel values; `bst-investor-profile` `portfolio_count`; `bst-startup-results` `total_count` and its `Showing x to y of z` pager; every chart bucket count in `bst-trends-charts` and its companion table; **and every truncation caption** — the five on `bst-company-profile` (rounds, founders, executives, jobs, news) and the three on `bst-investor-profile` (portfolio, rounds led, rounds participated in), each of which prints a shown count, a total and a limit |

`c.count` on the chart buckets is what makes the KPI and the chart agree: a four-digit bucket would otherwise render `1284` beside a KPI reading `1,284`, and the two numbers would look like different kinds of quantity.

### Heading hierarchy

**Exactly one `<h1>` per page, and no level skipped below it.** A portal page is assembled from widgets, so no page record can carry the heading: the widget that *is* the page's subject renders it, and every other widget on that page starts at `<h2>`. Without this, four of the five routes would open with an `<h3 class="panel-title">` as their highest heading and none would have a first-level heading at all.

| Route | The `h1`, and the widget that renders it | The `h2` level on that page | Below that |
| --- | --- | --- | --- |
| `bst_home` | `bst-startup-search`, its `<h1 class="panel-title">` carrying `options.title` | `bst-startup-results`, its `<h2 class="panel-title">` carrying the result count | `<h3 class="media-heading">` per result card; `<h3 id="bst-results-upsell-title">` for the premium notice |
| `bst_company` | `bst-company-profile`, its `<h1 class="media-heading">` carrying the company name | The **Founders** and **Executives** panel titles, and the embedded `bst-premium-upsell` heading | `<h3 class="list-group-item-heading">` per news article |
| `bst_investor` | `bst-investor-profile`, its `<h1 class="panel-title">` carrying the investor name | **Portfolio**, **Rounds led**, **Rounds participated in**, and the embedded upsell heading | none |
| `bst_dashboard` | `bst-trends-kpi`, its `<h1 class="h2">` carrying `options.title` | Each KPI panel title, and each of the two `bst-trends-charts` panel titles | none |
| `bst_account` | `bst-account-summary`, its `<h1 class="panel-title">` | **Entitlements**, and the embedded upsell heading | none |

Three consequences follow, and each is checkable by reading a template:

- **`bst-premium-upsell` heads its alert with an `<h2>`**, because all three hosts embed it as a top-level sibling of their own `h1`. `bst-startup-results` renders its own equivalent notice at `<h3>` instead, because that notice sits *inside* the results panel and is therefore one level deeper. The treatment is the same; the level follows the nesting, which is what a heading level means.
- **`.panel-title` is a class, not a level.** Bootstrap 3.3.6 sets `margin-top: 0`, `margin-bottom: 0`, `color: inherit` and a fixed `font-size: ceil($font-size-base * 1.125)` on it, which is **16px** at this theme's 14px base. Because that size is a literal rather than the element default, the class renders identically on an `h1`, an `h2` or an `h3` and the element can be chosen for structure alone. That is why the same class appears at three different levels in the table above with no visual difference.
- **`<h1 class="h2">` on `bst-trends-kpi`** is a first-level heading rendered at second-level size, because the dashboard's title sits above a row of panels rather than above a document. The class controls the type scale and the element controls the outline; they are separate on purpose.

**`bst-account-summary` needs the same fallback for a different reason, and it is the one case the record-binding argument below does not cover.** Its own `h1` binds `options.title`, which is static, so no missing record can empty it — but it sits **inside** the `.bst-account-body` wrapper that [Error and empty behaviour](#error-and-empty-behaviour) gates away on failure, so the gate removes the heading along with the stale content it exists to remove. Without a fallback the error state renders **no heading of any level**, the page loses its only first-level heading, and `c.focusDestination()` finds no marked descendant and falls back to the widget root — whose accessible name is then computed from the only link inside it, so the focused region announces itself as *Back to search*. The fallback carries `tabindex="-1"` for exactly that reason: it restores the destination as well as the outline entry.

**The `h1` is present in every state, including the three that render no record.** Two of the five page-owning headings bind a value off the record — the company name and the investor name — and the record is not published on the unauthorised path, the not-found path or a failed load. A heading that binds it therefore has to sit inside the gate that those three paths close, which would leave the page with **no first-level heading at all** in exactly the states where a caller most needs to know which page they are on. Each of those two widgets therefore renders a **second, static** `h1`, gated on the complement of the same condition, so exactly one of the two is in the document at any moment:

```html
<h1 class="h2" tabindex="-1"
    ng-if="!data.authorised || data.notFound || data.error">Company profile</h1>
```

Three properties make this the right shape rather than a patch, and each is checkable:

- **The two are mutually exclusive by construction.** One is gated on `data.authorised && !data.notFound && !data.error` and the other on its exact negation, so no state renders two `h1` elements and no state renders none. Counting `h1` on the rendered page returns `1` in all four states.
- **The static heading dereferences nothing.** Its text is a literal, so it cannot raise the `TypeError` that a record-bound heading raises on the two paths that publish no record.
- **It carries `.h2`, not `.panel-title`, because it stands alone.** `.panel-title` zeroes both vertical margins and pins the size at 16px, which is right for a heading inside a `.panel-heading` that supplies the box and the spacing, and wrong for a heading that is the first element on the page: it renders barely above body size with **no margin at all**, so its rect starts at the very top of the content box and its ascenders sit against whatever is above it. The bare-heading precedent in this portal is `bst-trends-kpi`'s `<h1 class="h2">`, so this heading follows it and takes the second-level type scale and its margins from the utility class while the element keeps the first-level outline position.
- **It carries `tabindex="-1"`, which is what makes the retry handoff possible.** [Busy, status and focus behaviour](#busy-status-and-focus-behaviour) sends focus to the widget's primary heading when a **Retry** succeeds, and the **Retry** control lives inside the error panel — so at the moment focus has to move, the record-bound heading does not yet exist. The static heading is the destination that does. Without it the handoff has nowhere to land and focus falls to the document body.

The three widgets whose `h1` is a literal already — `bst-startup-results`, `bst-trends-kpi` and `bst-account-summary` — need no second heading, and each keeps its single `h1` **outside** the error gate for the same reason.

### Error and empty behaviour

Applies to the four widgets that load asynchronously — `bst-startup-results`, `bst-company-profile`, `bst-investor-profile` and `bst-account-summary` — **and to the initial load of the two dashboard widgets**, `bst-trends-kpi` and `bst-trends-charts`. Those two issue no server call after their first render, but the first render is itself a server call: every figure they publish comes from an aggregate, and an aggregate that throws would leave them rendering an empty panel, a bare `0` or a chart with no bars, with nothing to retry. They therefore carry the error panel and a working `c.retry()`, and no status region, because neither has a user-initiated action to announce.

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
        // After the payload has rendered, so the destination heading exists to receive
        // it. $timeout runs after the digest that inserts the content.
        $timeout(c.focusDestination, 0);
    }, function () {
        c.data.error = 'Could not load. Use Retry to try again.';
        settled();
        $timeout(c.focusDestination, 0);
    });
};

c.retry = function () {
    // BEFORE the load, because clearing data.error removes the Retry button from the
    // document and focus would otherwise be lost to the body in the gap before the
    // response arrives. c.load() moves it again once the new content is rendered.
    c.focusDestination();
    c.load();
};

c.errorText = function () {
    return c.data.error || c.data.serverError || '';
};
```

Four properties of that shape are what the contract requires, and each closes a way for the interface to stall or mislead:

- **The rejection handler exists**, so a rejected promise sets `data.error` rather than passing silently.
- **`c.busy` is cleared on both outcomes**, by the one `settled` helper that the success handler and the rejection handler each call, so it is cleared on rejection as well as on success and the progress indicator cannot hang. Both handlers are present, so there is no third path out of the call.
- **`data.error` is cleared at the start of every attempt**, so a successful retry removes the error panel rather than leaving it beside fresh content.
- **Focus is handed off on both outcomes, and once before the attempt**, per [Busy, status and focus behaviour](#busy-status-and-focus-behaviour). The pre-attempt move is what stops focus reaching the body while the request is in flight, and the post-settle move is what puts it on the heading that states the outcome — including a *second* failure, where the destination is the static heading rather than a record-bound one.
- **`c.errorText()` is the only thing a template asks about the error state**, and it answers either of the two members that can carry one.

**Two members can carry a failure, and each has exactly one owner.** `data.error` belongs to `c.load()` and to nothing else: it reports a call that did not settle successfully — a rejected promise. `data.serverError` belongs to a **server script** that caught its own failure and chose to report it, which is what the two dashboard widgets do when an aggregate throws; `c.load()` never reads it and never clears it, and the server script re-publishes it on every run, so it is empty again as soon as a run succeeds.

**That split is what makes a failing retry recoverable.** A server script that catches its own failure leaves `c.server.update()` **resolved**, so `c.load()`'s *success* handler runs and clears `data.error`. Were the server's message in `data.error`, the retry would erase it — and with it the panel the **Retry** control lives inside, leaving a widget with no data, no error and nothing to try again. Because the message is in `data.serverError` instead, the panel and its control survive a failing retry and disappear only when a run actually succeeds.

**Every template asks `c.errorText()` rather than reading either member**, in all seven error panels and in every gate that has to stand down while a failure is showing. The guarantee that follows is the one that matters and it is exact: **no empty-collection notice can ever stand in for a failure.** Each of the nine such notices is suppressed during an error either by its own gate — the results widget's *No startup matches those criteria* and the chart's *No startup is recorded for this breakdown yet* both test `!c.errorText()` directly — or by the content-region `ng-if` it sits inside, which is how the company and investor profiles suppress their five per-panel notices at once.

Two widgets are outside that shape, both deliberately, and they are named here so the guarantee is not read as more than it is. [`bst-premium-upsell`](#bst-premium-upsell) has no error panel at all, as its controller records: it renders from options and an embedded model, makes no server call that can fail, and its notice *is* its content. And [`bst-startup-results`](#bst-startup-results) has no single content-region gate — its result cards, its premium notice and its pager are siblings of its error panel rather than children of one wrapper. A **first** load that fails therefore shows the message over an empty region, which is correct; but a refresh that fails after a successful load — a page step or a new search, which are this widget's ordinary round trips — leaves the previous page's rows on screen beneath the message. The rows are real data honestly labelled by the error above them, and no empty-state text appears, so the guarantee above still holds; what a reader should not assume is that this widget clears its results when a refresh fails, because it does not.

**A value that is already defined when a retry begins is never bound one-time.** The `::` prefix stops watching an expression as soon as that expression has a **defined** value, and this single sentence decides every case in this portal, so the discipline is stated as the three cases rather than as a slogan:

| Where the expression sits | One-time binding | Why |
| --- | --- | --- |
| Inside an `ng-repeat` clone — `::item.name`, `::round.round_date`, `::row.label` | **Permitted, and used throughout** | The binding is per clone. When the collection changes, `ng-repeat` destroys the clones and builds new ones, and each new clone evaluates its own expressions once. The repeat expression itself is what must stay watched; the properties read inside it need not be. |
| Directly on a `data.*` member that only a **successful** load ever defines — `::data.startup.name`, `::data.roundsLedTotal`, `::data.entitlements` | **Permitted, and used throughout** | These widgets do not catch their own failure, so a failed load leaves the member `undefined`, a one-time binding on an undefined value has not deregistered, and a later successful retry still paints. There is no state in which the member holds one defined value and must later show another. |
| Directly on a `data.*` member whose server script publishes a **defined** value even when it fails — the two dashboard collections and everything derived from them | **Forbidden** | This is the only case that breaks, and it is why the rule exists. Both dashboard scripts catch their own aggregate failure and still publish their collections, as empty arrays, *before* the first paint — so a one-time repeat over them deregisters immediately and can never repaint. That cuts both ways and both ways mislead: after a failed retry the widget goes on showing the figures of the run before it, and after a **successful** retry it shows nothing new at all, which is the opposite of what a Retry control promises. |

The test to apply is therefore not "can a retry change this value" but **"is this value already defined at the moment the retry starts"** — and the answer is yes exactly when the widget's own server script publishes it on the failing path too. That is the property `data.serverError` marks: a widget that publishes `serverError` also publishes defined defaults beside it — the KPI script assigns `data.kpis = []` both before its `try` and inside its `catch`, and the charts script builds `data.buckets` from the closed choice list it published *before* the aggregate, so a caught failure still yields a full set of zero-count buckets. That last detail is why an unguarded charts template rendered its empty-data notice on a failure rather than an error: the collection was not empty, it was zeroed.

Every member either dashboard publishes **after** its aggregate is therefore bound normally. One member is exempt and named here so the exemption is not mistaken for an oversight: `data.dimensionLabel` keeps the one-time form, because the charts script resolves it in step 2 from `options.dimension`, before it queries anything at all. It is an `options`-derived value wearing a `data` name, no round trip can alter it, and `D-554` records it staying one-time for that reason. `options.*` and values derived from them keep the one-time form on the same grounds. The cost is a handful of watchers on widgets that render at most five panels or eight bars.

One member is published unconditionally for this reason rather than bound normally: `data.upsellPage` on [`bst-startup-results`](#bst-startup-results), as its server script's own note records. Either treatment closes the gap; publishing it always is the cheaper of the two because the value is a page name that never varies.

**One helper, called from both handlers.** `finally` is a reserved word in the ECMAScript 3 syntax the platform's server-side interpreter accepts, so a promise-`finally` handler has to be reached through bracket notation to parse at all. The delivered form is one helper called from both handlers: the busy flag is cleared exactly once on either outcome, in one place, with no reserved word and no bracket notation, and it reads the same on the server and in the client controller. Recorded at `D-178`.

**The visible error panel**, rendered by each of the four templates immediately after its status region:

```html
<div class="alert alert-danger" role="alert" ng-if="c.errorText()">
  <span class="icon-cross-circle" aria-hidden="true">&nbsp;</span>
  <span>{{c.errorText()}}</span>
  <button type="button" class="btn btn-default" ng-click="c.retry()">Retry</button>
</div>
```

**Every collection renders an explicit empty state.** A collection that is empty renders a short `.alert.alert-info` **carrying `role="status"`**, or a single `.list-group-item` carrying `role="status"` where the collection is a list inside a panel, stating in plain words that there is nothing to show. **No collection renders as nothing at all**, and no count of `0` stands alone as the whole of the answer. The wording for each is given in the widget's own section.

#### Which alerts are live regions, and which are not

**Three states are announced from a visible element, and every other alert is silent.** The rule is the one stated under [Busy, status and focus behaviour](#busy-status-and-focus-behaviour): one fact, one announcer. Applied to markup it gives exactly three roles per template, and their absence elsewhere is as deliberate as their presence:

| Alert | Role | Reason |
| --- | --- | --- |
| The not-entitled `.alert.alert-warning` | **`role="alert"`** | The denial must interrupt. `statusText()` returns nothing in this state, so without the role the denial is announced by nothing at all — the one message a denied caller most needs would be the least likely to be heard. |
| The failure `.alert.alert-danger` | **`role="alert"`** | Already carried. It interrupts and it owns **Retry**. |
| The not-found `.alert.alert-warning` — the company and investor profiles | **`role="alert"`** | Same reasoning as the denial, and the same gap without it: the caller asked for a specific record, the answer is that it does not exist, and `statusText()` returns nothing in this state. |
| The empty-state `.alert.alert-info`, or the empty `.list-group-item`, **where the emptiness is the answer to something the caller just did** | **`role="status"`** | Polite, because an empty result is an answer rather than a fault. `statusText()` returns nothing in this state, so this element is the sole announcer. |
| The same empty-state element **where the collection was empty on arrival** — the five per-pane messages of `bst-company-profile`, the three of `bst-investor-profile` | **no role** | Nothing changed: these panes arrive in one round trip and a caller reaches each message in reading order when they open that pane. A role would announce, on load, an emptiness the caller has not asked about yet — and on the company profile there are five of them, so five announcements would fire for one arrival. The **all-empty** case is the one worth stating, and the widget's own `statusText()` states it once. |
| Any other `.alert` — an explanatory note, a truncation notice, the premium upsell, a withheld-count substitute | **no role, no `aria-live`** | Each restates something a visible heading, the loaded status wording or an adjacent control already carries. A role here is a second announcement of one fact. |

**The distinction in rows three and four is between an answer and a description.** `bst-startup-results` renders its empty state *because the caller submitted a search*, so the emptiness is the response to an action and has to reach them without their going looking for it. A company profile's Funding pane is empty *as a property of the record*, in a tab set that was fully loaded before the caller touched anything; it is content, and content is read. Applying row three's role to row four's elements is the most likely mistake here, and it produces a load-time burst of announcements about panes the caller has not opened.

**A truncation notice and a withheld-count substitute are read, not announced.** Both are permanent explanatory text beside the thing they qualify, not state changes, and both are reached in reading order by every caller. Giving either a live-region role would interrupt a caller mid-sentence to restate a caption they are about to read anyway.

#### Rendered rows and model rows must agree

**A repeat that fails to render is silent, and every count on the screen keeps asserting the data it did not draw.** This is the one failure mode this widget family cannot see, so two rules close it — one that stops it happening, and one that makes it visible if it happens anyway.

**Rule 1 — every repeat is keyed on something that is present and unique, or it is keyed on `$index`.** AngularJS throws `ngRepeat:dupes` and renders **zero** clones for the whole collection — not just the offending row — when a `track by` expression repeats a value or evaluates to `undefined`. Three consequences follow, and each has bitten a repeat in this portal:

| Collection | Its key | Why that key is safe |
| --- | --- | --- |
| A collection of records this application wrote | `track by item.sys_id` | `sys_id` is present on every row a `GlideRecordSecure` query returns and is unique by construction. This is the correct key and it stays. |
| A collection of **primitives** — `Investor.focus_areas`, and any other Multi-choice value rendered as chips | `track by $index` | A repeat over primitives with **no** `track by` keys each item as `type:value`, so two identical strings collide and the whole collection renders as nothing. `focus_areas` is a Multi-choice column and the [cleaning rules](#the-cleaning-rules-these-widgets-depend-on) de-duplicate on name and headquarters location, not on the members of a multi-choice value, so a fallback import can legitimately write the same member twice. `$index` is the correct key for a primitive collection: it is always present and always unique. |
| A collection assembled by the application from **more than one traversal path** — the investor portfolio, which is a de-duplicated union per AAP §0.8.5 | `track by item.sys_id`, **plus** rule 2 below | The key is right, but the de-duplication that guarantees its uniqueness is application logic rather than a database constraint, so it is the one collection where the guarantee could regress. |

**Rule 2 — every widget that renders a collection reconciles what rendered against what it holds.** Each of the four templates that repeats a collection carries one reconciliation notice per collection, immediately after the repeat:

```html
<div class="alert alert-warning" role="alert"
     ng-if="data.authorised &amp;&amp; !data.error &amp;&amp; c.unrendered('result')">
  <span class="icon-warning-triangle" aria-hidden="true">&nbsp;</span>
  <span>{{c.unrendered('result')}} of {{data.result.length}} rows could not be displayed. Reload the page; if it recurs, report it with this page address.</span>
</div>
```

**The leading terms of that `ng-if` are not decoration: the notice must carry the same guard as the region that contains the repeat it reconciles.** The helper compares a model length against a rendered-row count, and both a withheld region and a failed repeat produce the same arithmetic — a populated collection and no rows on the screen. So a notice with only `c.unrendered(...)` in its guard fires in every state where the repeat was *deliberately* not rendered, and reports a fault where there is none. The two instances in this family are:

| Template | The repeat's enclosing guard | The notice's guard |
| --- | --- | --- |
| `bst-startup-results` | `data.authorised && !data.error` on the wrapper around the card repeat | `data.authorised && !data.error && c.unrendered('result')` |
| `bst-company-profile`, each of its five collections | `!c.isEmpty('<collection>')` on the table or list that holds the repeat | `!c.isEmpty('<collection>') && c.unrendered('<collection>')` |
| `bst-investor-profile` | `c.hasPortfolio()` on the `.table-responsive` around the portfolio repeat | `c.hasPortfolio() && c.unrendered('portfolio')` |

The rule generalises: copy the guard of the repeat's nearest enclosing conditional and append the helper. A notice that can outlive its own repeat is worse than no notice, because it teaches a caller to disbelieve the one message in the family that reports a real rendering fault.

and each client controller exposes the one helper that drives it:

```javascript
c.unrendered = function (collection) {
    var model = c.data[collection];

    // Two collection shapes exist in this family: a bare array, and the four-member
    // {rows,total,limit,truncated} envelope the company profile publishes. Reading
    // `.length` off an envelope yields undefined, so a helper that did not normalise
    // would return 0 for every envelope collection -- silently disabling itself on the
    // one widget whose repeats have actually failed this way.
    if (model && !angular.isArray(model) && model.rows) {
        model = model.rows;
    }

    var modelLength = model && model.length ? model.length : 0;
    var drawn = $element[0].querySelectorAll('[data-bst-row="' + collection + '"]').length;

    return modelLength > drawn ? modelLength - drawn : 0;
};
```

`$element` is injected into the controller for this and for nothing else — it is the widget's own root, so the query cannot see another widget's rows. Four properties make the helper safe to call from a template binding:

- **It counts a marker attribute, not a class.** Every repeated element carries `data-bst-row="<collection>"` — added to the repeat's root element, alongside its `track by` — so the count is of *that* repeat's clones and cannot be inflated by a nested list or a sibling panel that happens to share a class.
- **It normalises the two collection shapes**, so the same helper is correct for a bare array and for the four-member envelope. The marker value is the **member name** on `data`, not a path into it: `data-bst-row="rounds"` against `c.data.rounds.rows`. Keeping the marker at the member name is what lets one string identify the collection in the template, in the guard, in the notice's wording and in the helper.
- **It returns a number, and `0` is falsy**, so the notice is absent from the document whenever the two agree. It renders only on a genuine shortfall.
- **It never returns a negative number**, so a transient mid-digest state where more elements exist than the model holds reads as agreement rather than as a shortfall.
- **It is called once per collection per template, and its notice carries `role="alert"`.** This is the fourth live region in the family and the only one added beyond the three states above, because it reports a fault in the rendering itself rather than a state of the data: nothing else on the screen carries it, so no other announcer can.

This is what turns a silent blank region into a stated failure. It does not repair the row that failed; it stops every other surface on the screen from asserting a row the caller cannot see.

#### The cleaning rules these widgets depend on

**Two classes of character reach these widgets through stored text and change what the caller sees, and neither is handled by trimming.** The four cleaning rules of the ingestion contract — trim, de-duplicate on name and headquarters location, normalise choice values, reject a record missing a mandatory field — do not by themselves address either, so both are stated here as the display-side contract.

**One definition enforces both, on every write path.** `AppProperties.normaliseText()` is the single implementation, and there is no second copy of the character inventory anywhere in the application. Three write paths read their text through it and no other:

| Write path | Where it calls the one definition |
| --- | --- |
| An ingestion run, live or fallback | `IngestionMapper._string()`, which every mapped value, every comparison and every de-duplication key in that class is read through — including `trimStrings()`, which **is** cleaning rule 1, and `startupKey()`, which **is** the cleaning rule 2 key |
| A `POST` or `PUT` on any of the six REST resources | `RestQueryHelper._normalise()`, which every body value and every free-text filter is read through |
| A `Startup` record inserted or updated through a form or a script | the `Trim and validate startup` before rule, which applies it to each of its eight whitelisted string fields **and** to the three mandatory-field checks |

`AppProperties.safeText()` — the one diagnostic sanitiser — reads its text through the same definition, so a value cannot be neutralised in a stored field and left intact in the log line that reports it. The complete inventory and the reason each class receives a different action are set out once, in [`../api-reference.md` → Two character classes, two actions](../api-reference.md#two-character-classes-two-actions).

**Class one — characters that are invisible but not whitespace.** `String.prototype.trim` removes none of U+200B zero-width space, U+200C zero-width non-joiner, U+200D zero-width joiner, U+2060 word joiner, U+00AD soft hyphen or U+FEFF byte-order mark. Two startups whose names differ only by a zero-width space would therefore render **identically** while de-duplication, which compares the stored strings, treated them as two companies. **Every value written through the three paths above has those six code points, and the rest of the zero-width and directional formatting class, removed outright before it is trimmed and before any key is built from it.** Removal precedes trimming because a leading zero-width space otherwise protects the whitespace behind it from the trim, and removal rather than space-substitution is what makes the stored value equal the value a reader sees: a soft hyphen inside `Wid<U+00AD>get` becomes `Widget`, not `Wid get`.

**The invariant this establishes, stated exactly.** De-duplication now converges on the **rendered** name rather than on the byte sequence, so **no two accepted rows can render identically** — which is the property that matters on these widgets, because it is the only one a caller can check. Note what it does and does not merge: `Widget Works`, `widget works`, `   Widget Works   `, `<U+FEFF>Widget Works` and `Widget Works<U+202E>` all render as `Widget Works` and collapse to **one** row; `Widget<U+200B>Works` and `Widget<U+00AD>Works` both render as `WidgetWorks` and collapse to **one** row of their own. Two rows survive because two visibly different names were supplied, and a reader can tell them apart. Collapsing those two groups together would require substituting a space for the invisible character, which would also merge two genuinely distinct company names, so it is not done.

**Class two — characters that reorder the text around them.** U+202A to U+202E and U+2066 to U+2069 are bidirectional embedding, override and isolate controls. An unterminated U+202E right-to-left override in a stored name makes the rendered string differ from the stored string — `Alpha desrever Beta` for a stored `Alpha reversed Beta` — so the value a caller reads is not the value an administrator would read on the platform form view. **Those ten code points are removed on the same three write paths, by the same one definition, for the same reason: a stored value must render as itself.** Removal rather than escaping is the right treatment because none of the ten carries meaning in a company name, a location or a job title, and an escaped control would render as visible mojibake.

**Why the three display rules below are still required.** They are not redundant with the write-path removal, and the order of the two arguments matters. The write path is what guarantees no *stored* value carries a control; the display rules are what make *genuine* right-to-left content render correctly, and they are the only protection for any value that predates the control or arrives by a route outside the three paths above — a direct `sys_import_set` load, or a form write on one of the six tables that carries no before rule. Measured on the delivered markup, `<bdi>`, `dir="auto"` and `unicode-bidi: isolate` **contain** a U+202E to its own element but do **not** undo it: with the control present, the heading still painted `AcmedtL proc` for a stored `Acmecorp Ltd`, and the inline row still swept the widget's own `42,000,000 USD` figure into the reversed run. Only removing the character at the write path fixed that. Keep both.

**Genuine right-to-left text is supported, and is isolated rather than stripped.** Removing the *controls* does not remove the ability to store Arabic or Hebrew; it removes the ability to hijack the surrounding layout. Three display rules carry that:

- **`dir="auto"` on every element that renders a stored free-text value.** The browser then takes the paragraph direction from the value's own first strong character, so an Arabic company name is flush right inside a left-to-right page and a Latin one is flush left. Without it every value inherits `direction: ltr` from the page and a right-to-left name renders against the wrong edge. It is applied to the elements that render `name`, `description`, `headquarters_location`, a job or article `title`, an article `summary` and an article `source`.
- **`<bdi>` around a stored value rendered inline beside product wording.** `Total funding <bdi>{{…}}</bdi>` keeps a right-to-left value from reordering the label in front of it. The element exists for exactly this and needs no attribute.
- **`unicode-bidi: isolate` on the containers that hold both product wording and a stored value.** It is a keyword naming a behaviour, not a measured value, so it is permitted in widget CSS. The UA stylesheet already applies it to `<bdi>`; declaring it on the container is what extends the same guarantee to a list item that interpolates a value directly.

**One further display guard, for stacked combining marks.** A grapheme carrying several combining marks is taller than the font's nominal ascent, and a fixed heading line height clips it into the line below. Every element that renders a stored name or title therefore takes `line-height: normal`, which lets the line box grow to the content. `normal` names a behaviour rather than a measurement, so it introduces no literal, and for text without combining marks it is visually indistinguishable from Bootstrap's own `$headings-line-height`.

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

#### Data contract

**Every member below is assigned onto `data` by the server script named in its row, and read by the consumer named in its row. There is no third source and no other member**: a template expression naming anything absent from this table renders nothing at best and raises a runtime expression error at worst, and a member published with no consumer is a dead output. `data.error` is not in any widget's table — it is set on the client by the shared `c.load()` helper of [Error and empty behaviour](#error-and-empty-behaviour) and by nothing on the server. A widget whose own server script catches a failure and reports it publishes that message as **`data.serverError`**, which **is** in that widget's table, and which `c.load()` never touches; the error panel renders `c.errorText()`, which answers either of the two.

| Member | Type | Published by | Consumed by |
| --- | --- | --- | --- |
| `authorised` | True/False | server item 1 | Template — the not-entitled alert and the `ng-if` on the form |
| `industries` | Array of string | server item 2 | Template — the industry `<select>`; controller item 6 validates against it |
| `criteria` | Object of three strings | server item 3 | Template `ng-model` on the three inputs; controller items 1 to 3 |
| `appliesInclusion` | True/False | server item 4 | Template — the "limited to the Boston area" note |
| `currentPage` | String | server item 5 | Controller item 3, compared with `options.results_page` |

#### Client controller

1. Bind the three inputs to `c.data.criteria.name`, `c.data.criteria.industry` and `c.data.criteria.location` with `ng-model`.
2. Expose `c.submit()`, bound by `ng-submit` on the `<form>`, and `c.clear()`, bound by `ng-click` on the **Clear** button — those two are the whole of this widget's interaction surface, and the form carries exactly one `type="submit"` control. On submit, and on clear, normalise each value by trimming it, and **assign the trimmed value back onto the model**:

```javascript
var normalise = function () {
    var criteria = c.data.criteria;

    criteria.name = (criteria.name || '').trim();
    criteria.industry = (criteria.industry || '').trim();
    criteria.location = (criteria.location || '').trim();
};
```

   **The two text inputs carry `ng-trim="false"`, and that is what makes the assignment visible.** The framework trims a text input's value on its way *into* the model by default, so a field holding only spaces yields an empty model while the field still visibly holds the spaces — the view and the model then disagree, and assigning the already-empty value back changes nothing and re-renders nothing. With `ng-trim="false"` the model holds what the caller typed, `normalise()` genuinely changes it, and the framework writes the trimmed value back to the field. The criteria that leave this widget are identical either way; what changes is that the caller can see what was submitted.
3. **Deliver the criteria according to `options.results_page`.** The option is read on every submit and on every clear, and decides between two paths:
   - **Same page** — `options.results_page` equals `data.currentPage`, which is the shipped configuration, where both widgets sit on `bst_home`. Broadcast the criteria on the root scope with `$rootScope.$broadcast('bst.search.criteria', c.data.criteria)`, and mirror them into the URL with `$location.search()` on the same three parameter names, so the search is linkable and the widget rehydrates on reload. `bst-startup-results` listens for that event.
   - **Another page** — `options.results_page` names a different page. Navigate to it, carrying the criteria as query parameters, with `$location.url('?id=' + options.results_page + <the three parameters>)`. The results widget on the destination page then seeds itself from those parameters through `$sp.getParameter()`, which is the same rehydration path the same-page form uses on reload. Broadcast nothing: the destination is a fresh page load and no listener survives it.
   - **Empty or unknown** — `options.results_page` is empty, or names no `sp_page` record. Fall back to the same-page path. Never navigate to an unresolvable page.
4. Declare `c.busy` per [Busy, status and focus behaviour](#busy-status-and-focus-behaviour). This widget issues no server call after its first render, so `c.busy` becomes `false` when the first payload arrives and stays there. It carries **no** status region: the submission is announced by `bst-startup-results`, which owns both the status region and the focus move for the result set.
5. Reject nothing and filter nothing. The controller never evaluates `active` or `headquarters_location`; the predicate lives in `StartupSearchService`.
6. Guard the industry input against a value outside `c.data.industries` by rendering it as a `<select>` over that list rather than as free text.
7. **Expose `c.submitting`, and disable the submit control while a search is outstanding.** This widget makes no server call of its own, so its own `c.busy` is `false` for the whole of its life and cannot carry this state. The state belongs to `bst-startup-results`, which is the widget that loads, so it publishes it and this widget listens:

```javascript
c.submitting = false;

var stopBusy = $rootScope.$on('bst.search.busy', function (event, busy) {
    c.submitting = !!busy;
});

$scope.$on('$destroy', function () {
    stopBusy();
});
```

   `bst-startup-results` broadcasts `bst.search.busy` with `true` at the start of every load it performs and with `false` when that load settles, from the same `c.load()` helper that owns its own busy flag, so the two can never disagree. **The deregistration is not optional**, for the reason given for the criteria listener: `$rootScope.$on` outlives this widget's scope.

   Without the guard, six clicks in a second are six submissions and therefore six concurrent searches against the instance, each one racing the others to be the result set the caller ends up looking at. **On the another-page path there is no listener**, because the destination is a fresh page load and no listener survives it; a second click during that navigation re-requests the same address, which is idempotent, so nothing is needed there.

8. **Expose `c.filterColumns()`, which returns the column class the three filters share, so the row always totals twelve.** Both optional filters are configurable, so the row carries one, two or three columns, and a fixed `col-md-4` leaves two thirds of the row empty when it carries one:

```javascript
c.filterColumns = function () {
    var shown = 1
        + (c.options.show_industry ? 1 : 0)
        + (c.options.show_location ? 1 : 0);

    if (shown === 1) {
        return 'col-md-12 col-lg-12';
    }

    if (shown === 2) {
        return 'col-md-6 col-lg-6';
    }

    return 'col-md-4 col-lg-4';
};
```

   Twelve divides by one, two and three exactly, so every configuration totals twelve with no remainder and no extra-small or small class. The name field is always shown, which is why the count starts at one.

#### HTML template

```html
<div class="bst-search panel panel-default" aria-busy="{{c.busy}}">
  <div class="panel-heading">
    <h1 class="panel-title">{{::options.title}}</h1>
  </div>
  <div class="panel-body">
    <div class="alert alert-warning" role="alert" ng-if="!data.authorised">
      <span class="icon-info" aria-hidden="true"></span>
      <span>Your account holds no Boston Startup Tracker role.</span>
    </div>
    <form name="bstSearchForm" novalidate ng-if="data.authorised" ng-submit="c.submit()">
      <div class="row">
        <div ng-class="c.filterColumns()">
          <div class="form-group">
            <label for="bst-search-name">Company name</label>
            <div class="input-group">
              <input id="bst-search-name" type="text" class="form-control"
                     dir="auto" ng-trim="false"
                     ng-model="data.criteria.name" />
              <span class="input-group-btn">
                <button type="submit" class="btn btn-primary" ng-disabled="c.submitting">
                  <span class="icon-search" aria-hidden="true"></span>
                  <span>Search</span>
                </button>
              </span>
            </div>
          </div>
        </div>
        <div ng-class="c.filterColumns()" ng-if="::options.show_industry">
          <div class="form-group">
            <label for="bst-search-industry">Industry</label>
            <select id="bst-search-industry" class="form-control"
                    ng-model="data.criteria.industry">
              <option value="">All industries</option>
              <option ng-repeat="choice in ::data.industries track by $index" value="{{::choice}}">{{::choice}}</option>
            </select>
          </div>
        </div>
        <div ng-class="c.filterColumns()" ng-if="::options.show_location">
          <div class="form-group">
            <label for="bst-search-location">Location</label>
            <input id="bst-search-location" type="text" class="form-control"
                   dir="auto" ng-trim="false"
                   ng-model="data.criteria.location" />
          </div>
        </div>
      </div>
      <div class="bst-search-actions">
        <button type="button" class="btn btn-default" ng-click="c.clear()">Clear</button>
        <span class="text-muted" ng-if="data.appliesInclusion">
          Results are limited to active startups headquartered in the Boston area.
        </span>
      </div>
    </form>
  </div>
</div>
```

**One submit control, and the form owns the submission.** The `.input-group-btn` beside the name field is the only `type="submit"` button: `ng-submit="c.submit()"` on the `<form>` means the Enter key in *any* of the three fields submits the whole criteria object, so a second identically-labelled **Search** button in the actions row would add no behaviour and would announce `Search, button` twice to a screen reader with no way to tell the two apart. The actions row therefore carries only **Clear**, which is `type="button"` because it must not submit, and the inclusion note. The button's position beside the name field is the Bootstrap search idiom; it submits all three filters, not the name alone.

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

/* Bootstrap's .form-control:focus removes the browser's own ring (outline: 0) and
   replaces it with a border-colour change plus a glow, both in a pale blue that
   measures 2.37:1 against the adjacent white and 1.47:1 against the unfocused
   border - so on both readings of the non-text contrast requirement the focused
   state is not distinguishable. The ring is restored in the brand colour, which is
   4.60:1 on the panel; the glow is left alone, so the focused state now has two
   independent cues rather than one that cannot be seen. The width and offset come
   from the radius scale for the reason recorded under "Busy, status and focus
   behaviour": Bootstrap publishes no outline-width token, and these are the only
   3- and 4-pixel lengths available without writing a literal. */
.bst-search .form-control:focus {
    outline: $border-radius-base solid $brand-primary;
    outline-offset: $border-radius-small;
}
```

The `.panel-body` rule is scoped beneath `.bst-search`, which is what keeps it out of every other panel on the instance.

**The focus rule is the only focus declaration in this portal, and it exists because Bootstrap removes the one the browser draws.** `.form-control:focus` in Bootstrap 3.3.6 sets `outline: 0` and compensates with colour alone — the border moves from one grey to one blue, plus a soft blue glow. That substitution is weaker than it looks, and it fails outright in one mode:

| Rendering mode | What Bootstrap's compensation delivers | Consequence |
| --- | --- | --- |
| Ordinary | The border recolours from `#cccccc` to `#66afe9` and an outer `box-shadow` glow appears. Measured against the control's own white background, that focused border is **2.37:1** — below the 3:1 floor for a non-text indicator — and the glow is fainter still. | An indication exists but is tonal only and thin. |
| `forced-colors: active` | **Nothing.** That mode rewrites every border to a single system colour and removes `box-shadow` entirely, so both compensations are discarded. | A focused text input, a focused select and an unfocused one compute **identically in every property** — same outline, same border, same background, same shadow. The only differing pixel is the text caret, which a `<select>` does not have. A caller navigating by keyboard in that mode cannot tell which of the three fields they are in. |

`outline-style: auto` restores the browser's own focus ring, and it is declared **unconditionally** rather than inside a `@media (forced-colors: active)` block. One rule then answers both rows of that table: it is the indicator forced colours *does* honour and recolours to `Highlight`, and in ordinary rendering it puts the platform ring back beside Bootstrap's glow instead of leaving a 2.37:1 border to carry the state alone. Scoping it to a media query would have fixed only the row where the indication vanished and left the row where it was merely weak.

Three further properties of the declaration are worth stating:

- **It introduces no measured literal.** `auto` is a permitted keyword and no width or colour is stated. Bootstrap's `outline: 0` leaves `outline-width` at `0px` and that computed value survives — but a browser draws the `auto` ring at its own platform width and ignores the declared width entirely, so the ring paints regardless. The computed `outline-width: 0px` beside a painted ring is expected and is not a symptom.
- **The ring the platform draws is the one the caller already recognises** everywhere else on the instance, which is worth more to a keyboard caller than any authored ring would be.
- **It is scoped to `.form-control` and nothing else**, because the buttons and links in these widgets never lost their ring: Bootstrap leaves `:focus` alone on `.btn` and on `<a>`.

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
| `upsell_page` | string | `bst_account` | The `sp_page.id` the surface-level premium alert's call to action targets. Published as `data.upsellPage`; this widget renders the alert inline rather than embedding `bst-premium-upsell`. |

**The page size is shared with the REST layer.** When `page_size` is empty the widget reads `x_bst_startuptrk.rest.default_limit` — shipped value `20` — through `AppProperties.getDefaultLimit()`, and it clamps any supplied value to `x_bst_startuptrk.rest.max_limit` — shipped value `50` — through `AppProperties.getMaxLimit()`. Those are the same two properties `RestQueryHelper.getLimit()` reads for the API, documented in [`../api-reference.md`](../api-reference.md), **so changing either property changes the page size on both surfaces at once.** Do not hard-code `20` or `50` in the widget.

**Both accessors cap at `50`, so a property can narrow this widget's page and cannot widen it.** `AppProperties` resolves each page-size property to at least `1` and at most `PAGE_SIZE_CEILING`, which is `50`. Raising `x_bst_startuptrk.rest.max_limit` to `200` therefore does **not** produce a 200-row widget page: it resolves to `50`, here exactly as in the API. If a larger portal page is ever wanted, the ceiling is a code constant in `AppProperties` and changing it is an Update Set change, not a configuration change — which is the point, because the same constant is what stops a mistyped property from rendering an entire table into a widget.

#### Server script

1. Construct `var builder = new RestResponseBuilder();` and assign `data.authorised = builder.hasAnyAppRole();`. When `data.authorised` is `false`, return immediately and publish nothing further. **Assign the result — do not merely call the method.**
2. Resolve the page size: start from `options.page_size`; when it is empty or not a whole number of 1 or more, use `new AppProperties().getDefaultLimit()`; then clamp to `new AppProperties().getMaxLimit()`. Store the resolved value as `data.limit`.
3. Resolve the offset: take `input.offset` when the widget was refreshed from the client, otherwise `$sp.getParameter('offset')`, otherwise `0`. Coerce to a whole number of 0 or more and store as `data.offset`.
4. Resolve the criteria: take `input.criteria` when present, otherwise read `name`, `industry` and `location` with `$sp.getParameter()`. Trim each. Discard an `industry` value that is not one of the six values of `x_bst_startuptrk_startup.industry`. Store the resolved object as `data.criteria`, with all three keys always present and an unsupplied filter held as an empty string — step 5 reads it, and the controller sends it back as `input.criteria`, so a missing key would resolve to `undefined` on the round trip and reintroduce the filter this step just discarded.
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

6. Publish `data.gated = { total_funding_usd: false, institutional_funding_last_5yrs: false }` and set a member to `true` when at least one returned row omitted that key, so the template knows to render the `Premium` marker rather than a blank cell. Then publish the two members the surface-level treatment reads:

```javascript
data.gated = {
    total_funding_usd: rows.some(function (row) { return row.total_funding_usd === undefined; }),
    institutional_funding_last_5yrs: rows.some(function (row) {
        return row.institutional_funding_last_5yrs === undefined;
    })
};
// Read by the one surface-level alert. It is a separate member from data.gated so the
// template tests a boolean rather than reducing an object in an expression.
data.gatedAny = data.gated.total_funding_usd ||
                data.gated.institutional_funding_last_5yrs;
// The page the surface-level alert's call to action targets.
data.upsellPage = options.upsell_page || 'bst_account';
```

   **`data.upsellPage` is published even when nothing is gated**, because the template binds it with a one-time expression; publishing it conditionally would leave the link's `href` empty on a later render that did find a gated field.
7. `data.total_count` must be the count produced by `countState()` under the **same** plan. Never count with a second, differently-built query, and never report `data.result.length` as the total.
8. `countState()` answers `{ total, denied }`. `total` is the **exact** cardinality of the filtered set at any magnitude — there is no counting ceiling and no truncation, so the template renders the figure plainly and never as a minimum. `denied` is `true` when the caller failed the table-level read check, in which case `total` is `0` and **the total must not be rendered at all**: publish `data.count_denied` and let the template show the no-role notice instead of a count of zero, which would otherwise tell a caller that a set it may not read is empty. The pager arithmetic in the client controller depends on the total being exact: a floor would let `c.next()` advance past the last page. There is no capped state, no `total_count_capped` member and no "more than" rendering.

The plan is built once and handed to both `countState()` and `search()`, which is what keeps the total in agreement with the page contents. `../api-reference.md` states the same invariant for the `GET /startups` list operation. The exact aggregate total rests on one condition, stated there and in [`../data-model.md`](../data-model.md): no table in this application carries a record-level access control, so every role that can read these tables can read every row of them.

#### Data contract

**Every member below is assigned onto `data` by the server script named in its row, and read by the consumer named in its row. There is no third source and no other member**: a template expression naming anything absent from this table renders nothing at best and raises a runtime expression error at worst, and a member published with no consumer is a dead output. `data.error` is not in any widget's table — it is set on the client by the shared `c.load()` helper of [Error and empty behaviour](#error-and-empty-behaviour) and by nothing on the server. A widget whose own server script catches a failure and reports it publishes that message as **`data.serverError`**, which **is** in that widget's table, and which `c.load()` never touches; the error panel renders `c.errorText()`, which answers either of the two.

| Member | Type | Published by | Consumed by |
| --- | --- | --- | --- |
| `authorised` | True/False | server item 1 | Template — the not-entitled alert and every `ng-if` on the result region |
| `limit` | Integer | server item 2 | Controller item 3's pager arithmetic; the caption's ceiling |
| `offset` | Integer | server item 3 | Controller items 2 and 3; sent back as `input.offset` on refresh |
| `criteria` | Object of three strings | server item 4 | Controller item 2's event handler; sent back as `input.criteria` |
| `result` | Array of serialised startups | server item 5 | Template — the card `ng-repeat`; controller `c.rangeStart()` and `c.rangeEnd()` |
| `total_count` | Integer | server item 5 | Template — the pager caption; controller item 3's clamp |
| `count_denied` | True/False | server item 5 | Template — suppresses the caption when the count could not be read |
| `gated` | Object of two booleans | server item 6 | Controller `c.isGated()`, and through it the `Premium` markers |
| `gatedAny` | True/False | server item 6 | Template — the one surface-level premium alert |
| `upsellPage` | String | server item 6 | Template — the `href` of that alert's call to action |

#### Client controller

1. Implement `c.load()` and `c.retry()` exactly as [Error and empty behaviour](#error-and-empty-behaviour) specifies. Every server call in the steps below goes through `c.load()`, so no call is made without both handlers and the `finally` clause attached.

   **This widget's `c.load()` additionally publishes its busy state on the root scope**, because `bst-startup-search` disables its submit control from it and has no load of its own to derive it from:

```javascript
$rootScope.$broadcast('bst.search.busy', true);   // immediately before c.server.update()
$rootScope.$broadcast('bst.search.busy', false);  // inside the settled helper
```

   Both go in the one place the busy flag is already written — the broadcast of `true` beside `c.busy = true`, and the broadcast of `false` inside the single `settled` helper that both handlers call — so the published state cannot diverge from the real one on either outcome.
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
```

   Without the deregistration every visit to `bst_home` leaves one more live listener on the root scope, each calling `c.load()` on a scope that no longer renders.

3. Expose `c.next()` and `c.previous()`, which adjust `c.data.offset` by `c.data.limit`, clamp it to the range `0` to the **last page's offset**, call `c.load()`, and **carry the `ng-disabled` half of the [focus handoff](#busy-status-and-focus-behaviour)**. Both go through one private stepper, because the handoff is identical in both directions and a rule written twice is a rule that drifts:

```javascript
// The pager buttons are ng-disabled, never removed, so they stay in the document and
// simply become inert — and a browser drops focus from an element it disables, to the
// document body. The handoff therefore runs AFTER the digest that applies `disabled`
// (which is what $timeout waits for), and only for a caller who actually held focus
// on the button that just stopped being operable.
function step(delta) {
    // Both questions are asked NOW, before anything changes: which control the caller
    // was on, and whether the browser was showing that focus. After the digest the
    // answer to the second is unrecoverable, because focus has already left.
    var source = document.activeElement;
    var wasKeyboardFocused = !!source
        && typeof source.matches === 'function'
        && (function () { try { return source.matches(':focus-visible'); } catch (e) { return false; } }());

    c.data.offset = clampOffset(c.data.offset + delta);
    c.load();

    $timeout(function () {
        if (!wasKeyboardFocused || !source.disabled) {
            return;                       // pointer caller, or still operable: move nothing
        }
        var pager = $element[0].querySelectorAll('.bst-results-pager button');
        for (var i = 0; i < pager.length; i++) {
            if (pager[i] !== source && !pager[i].disabled) {
                pager[i].focus();         // the other pager button, per the rule's first destination
                return;
            }
        }
        var heading = $element[0].querySelector('h2.panel-title');
        if (heading) {
            heading.focus();              // neither button is operable: the widget's primary heading
        }
    });
}

c.previous = function () { step(-c.data.limit); };
c.next = function () { step(c.data.limit); };
```

   `$timeout` and `$element` are injected for this; `$element` is already injected for item 11.

   **Why the two questions are asked at different times.** `source.disabled` is read *inside* the callback because that is the only place it is known: the whole point is that the digest may have disabled the button. `:focus-visible` is read *outside* it because by then the answer is gone — the browser has already dropped focus to the document body, so `activeElement` reads `<body>` in the pointer case and the keyboard case alike and can no longer tell them apart. One question belongs after the digest and the other before it, and swapping either is a defect.

   **`clampOffset` is the offset arithmetic, and its ceiling is the last page rather than the count.** `Math.min(offset, total_count)` looks equivalent and is not: with a count of 1 and a limit of 20 it yields an offset of `1`, and `c.rangeStart()` — `offset + 1` — then prints the impossible `Showing 2 to 2 of 1`. The ceiling has to be page-aligned, and it has to stand down entirely when the count was withheld, because a withheld count is `0` and would otherwise pin every caller to the first page:

```javascript
function clampOffset(offset) {
    var floored = Math.max(0, offset);
    if (c.data.count_denied) {
        return floored;               // no ceiling is knowable; c.hasNext()'s full-page test governs
    }
    var lastPage = Math.max(0, Math.floor((c.data.total_count - 1) / c.data.limit) * c.data.limit);
    return Math.min(floored, lastPage);
}
```

   Neither button can overshoot while the count is known, because each is disabled at its own end of the range — so this arithmetic is reached only when the data changed under the caller between loads, which is exactly the case a clamp is for.
4. Expose `c.hasNext()` and `c.hasPrevious()` for the pager's `ng-disabled` bindings. `c.hasNext()` is `false` when `c.data.result.length` is `0`, so an empty result set offers no next page. **When the count was withheld it must not be derived from the total**:

```javascript
c.hasNext = function () {
    var page = c.data.result ? c.data.result.length : 0;

    if (page === 0) {
        return false;
    }

    // The total is unreadable, so a full page is the only evidence that more
    // may exist. A short page is the last page.
    if (c.data.count_denied) {
        return page === c.data.limit;
    }

    return c.data.offset + c.data.limit < c.data.total_count;
};
```

   `c.data.total_count` is `0` whenever the count could not be read, so the arithmetic form evaluates `offset + limit < 0` — always `false` — and **Next stays disabled on every page**, locking a count-denied caller inside the first page of a set that may be arbitrarily long. The full-page test is the standard substitute: a page holding exactly `limit` rows may have more behind it, and a page holding fewer cannot.

5. Expose the **zero-safe pager range**. The pager must never read "1 to 0 of 0":
   - `c.rangeStart()` returns `c.data.offset + 1` when `c.data.result.length` is greater than `0`, and `0` otherwise.
   - `c.rangeEnd()` returns `c.data.offset + c.data.result.length`.
   - `c.hasRange()` returns `true` only when `c.data.result.length` is greater than `0`. The template renders the range sentence only under `c.hasRange()` and renders `No results to show` otherwise.
   - **The total is part of the sentence only when it is readable.** The template selects between two range sentences on `data.count_denied`, so `data.total_count` is never interpolated when the server could not read it. A range with no total is a complete sentence; a range against a total of `0` is a false one.
6. Expose `c.isGated(item, field)`, `true` when `item[field] === undefined` **and** `c.data.gated[field]` is `true`. This is the single test the template uses to decide between a value and the `Premium` marker; it is specified under [The premium treatment in the result list](#the-premium-treatment-in-the-result-list).
7. Declare `c.busy` and `c.statusText()` per [Busy, status and focus behaviour](#busy-status-and-focus-behaviour), and also declare `c.focusDestination()` and `c.onButtonKey($event)` per that same section, `c.indeterminate()` for the striped bar, and `c.money()` and `c.count()` per [The display contract](#the-display-contract). Only the **loaded** state produces a string here; the other three return the empty string because a visible element owns each of them:
   - not entitled — the empty string. The `.alert-warning` carries `role="alert"`.
   - failed — the empty string. The `.alert-danger` carries `role="alert"`.
   - empty — the empty string. The `.alert-info` reading `No startup matches those criteria.` carries `role="status"`.
   - loaded, count readable — `{{c.data.result.length}} of {{c.data.total_count}} startups shown.`, both figures grouped with the `number` filter.
   - loaded, count withheld — `{{c.data.result.length}} startups shown. The total is not available to your account.` The total is **never** stated as `0` in this state.

   Returning the empty string in the first three states is what stops the region announcing the empty wording to a caller who was **denied by role**: without the not-entitled row the function falls through to the empty-collection row and tells that caller `No startup matches those criteria.`, contradicting the warning on the same screen. It is also what stops the empty wording being announced twice, once from here and once from the visible alert.

10. Expose `c.uid`, a value unique to this widget instance, used to suffix the id of the premium notice's heading. `$scope.$id` is the framework's own per-scope identifier and is already unique on the page, so `c.uid = $scope.$id;` is the whole of it. Nothing else on this widget needs an id.

11. Expose `c.unrendered(collection)` exactly as [rendered rows and model rows must agree](#rendered-rows-and-model-rows-must-agree) specifies, and inject `$element` into the controller so it can count the rendered rows of its own widget. The card repeat carries `data-bst-row="result"`, which is what the helper counts.
8. After a load that began with a search event or a retry, move focus to the `.panel-title` of this widget, per the focus table in [Busy, status and focus behaviour](#busy-status-and-focus-behaviour). Do not move focus after a pager step: the caller's focus is already on the pager button they activated, and it survives the reload.
9. Never filter, sort or re-order `c.data.result` in the client. Ordering is `name` then `sys_id`, applied by `StartupSearchService.search()`.

#### HTML template

```html
<div class="bst-results panel panel-default" tabindex="-1" aria-busy="{{c.busy}}">
  <div class="panel-heading">
    <h2 class="panel-title" tabindex="-1">
      {{::options.title}}
      <span class="text-muted"
            ng-if="data.authorised &amp;&amp; !c.busy &amp;&amp; !data.error &amp;&amp; !data.count_denied">
        {{c.count(data.total_count)}} matching
      </span>
    </h2>
  </div>
  <div class="panel-body">
    <div class="sr-only" role="status" aria-live="polite" aria-atomic="true">{{c.statusText()}}</div>

    <div class="alert alert-warning" role="alert" ng-if="!data.authorised">
      <span>Your account holds no Boston Startup Tracker role.</span>
    </div>

    <div class="alert alert-danger" role="alert" ng-if="c.errorText()">
      <span class="icon-cross-circle" aria-hidden="true">&nbsp;</span>
      <span>{{c.errorText()}}</span>
      <button type="button" class="btn btn-default" ng-click="c.retry()">Retry</button>
    </div>

    <div class="progress" ng-if="c.busy">
      <div class="progress-bar progress-bar-striped active" role="progressbar"
           ng-style="c.indeterminate()"
           aria-label="Loading startups" aria-valuemin="0" aria-valuemax="100"
           aria-valuetext="Loading"></div>
    </div>

    <div class="alert alert-info" role="status"
         ng-if="data.authorised &amp;&amp; !c.busy &amp;&amp; !c.errorText() &amp;&amp; data.result.length === 0">
      <span>No startup matches those criteria.</span>
    </div>

    <div class="alert alert-info"
         ng-if="data.authorised &amp;&amp; !c.busy &amp;&amp; !data.error &amp;&amp; data.count_denied">
      <span class="icon-locked" aria-hidden="true">&nbsp;</span>
      <span>The total number of matches is not available to your account, so this page states
        the range it is showing rather than a total. Paging continues while a full page arrives.</span>
    </div>

    <div class="bst-results-list" ng-if="data.authorised &amp;&amp; !data.error">
      <div class="panel panel-default bst-results-card" data-bst-row="result"
           ng-repeat="item in data.result track by item.sys_id">
        <div class="panel-body">
          <div class="media">
            <div class="media-left" ng-if="::options.show_logo">
              <img class="media-object" ng-if="::item.logo_url"
                   ng-src="{{::item.logo_url}}" alt="{{::item.name}} logo" />
              <span class="icon-image bst-results-logo-placeholder" ng-if="::!item.logo_url"
                    aria-hidden="true">&nbsp;</span>
            </div>
            <div class="media-body">
              <h3 class="media-heading">
                <a dir="auto"
                   ng-href="?id={{::options.detail_page}}&amp;sys_id={{::item.sys_id}}">{{::item.name}}</a>
              </h3>
              <p dir="auto">{{::item.description}}</p>
              <p>
                <span class="label label-primary" ng-if="::item.funding_stage">{{::item.funding_stage}}</span>
                <span class="label label-default" ng-if="::item.industry">{{::item.industry}}</span>
                <span class="label label-default" ng-if="::item.employee_count_range">{{::item.employee_count_range}}</span>
              </p>
              <ul class="list-group">
                <li class="list-group-item">
                  <span class="icon-map" aria-hidden="true">&nbsp;</span><bdi dir="auto">{{::item.headquarters_location}}</bdi>
                </li>
                <li class="list-group-item" ng-if="item.total_funding_usd !== undefined">
                  Total funding
                  <bdi ng-if="item.total_funding_usd !== null">{{c.money(item.total_funding_usd)}}</bdi>
                  <span class="text-muted" ng-if="item.total_funding_usd === null">Not recorded</span>
                </li>
                <li class="list-group-item" ng-if="c.isGated(item, 'total_funding_usd')">
                  Total funding
                  <span class="label label-info">Premium</span>
                </li>
                <li class="list-group-item" ng-if="item.institutional_funding_last_5yrs !== undefined">
                  Institutional funding in the last five years
                  <span class="label label-default"
                        ng-if="item.institutional_funding_last_5yrs !== null">{{item.institutional_funding_last_5yrs ? 'Yes' : 'No'}}</span>
                  <span class="text-muted"
                        ng-if="item.institutional_funding_last_5yrs === null">Not recorded</span>
                </li>
                <li class="list-group-item" ng-if="c.isGated(item, 'institutional_funding_last_5yrs')">
                  Institutional funding in the last five years
                  <span class="label label-info">Premium</span>
                </li>
              </ul>
              <a class="btn btn-default" aria-label="View the {{::item.name}} profile" ng-keydown="c.onButtonKey($event)"
                 ng-href="?id={{::options.detail_page}}&amp;sys_id={{::item.sys_id}}">View profile</a>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="alert alert-warning" role="alert"
         ng-if="data.authorised &amp;&amp; !data.error &amp;&amp; c.unrendered('result')">
      <span class="icon-warning-triangle" aria-hidden="true">&nbsp;</span>
      <span>{{c.unrendered('result')}} of {{data.result.length}} rows could not be displayed.
        Reload the page; if it recurs, report it with this page address.</span>
    </div>

    <div class="alert alert-info bst-results-upsell" role="region"
         aria-labelledby="bst-results-upsell-title-{{::c.uid}}"
         ng-if="data.authorised &amp;&amp; !data.error &amp;&amp; data.gatedAny &amp;&amp; data.result.length &gt; 0">
      <h3 class="panel-title" id="bst-results-upsell-title-{{::c.uid}}">
        <span class="icon-locked" aria-hidden="true">&nbsp;</span>Premium fields are hidden in these results
      </h3>
      <p>
        Total funding and the institutional-funding marker are reserved for the premium tier.
        Your account reads every other column on this page.
      </p>
      <a class="btn btn-primary" ng-keydown="c.onButtonKey($event)"
         ng-href="?id={{::data.upsellPage}}">Go to account management</a>
    </div>

    <hr ng-if="data.authorised &amp;&amp; !c.busy &amp;&amp; !data.error" />

    <div class="bst-results-pager"
         ng-if="data.authorised &amp;&amp; !c.busy &amp;&amp; !data.error">
      <button type="button" class="btn btn-default" ng-click="c.previous()"
              ng-disabled="!c.hasPrevious()">Previous</button>
      <button type="button" class="btn btn-default" ng-click="c.next()"
              ng-disabled="!c.hasNext()">Next</button>
      <span class="text-muted" ng-if="c.hasRange() &amp;&amp; !data.count_denied">
        Showing {{c.count(c.rangeStart())}} to {{c.count(c.rangeEnd())}} of {{c.count(data.total_count)}}
      </span>
      <span class="text-muted" ng-if="c.hasRange() &amp;&amp; data.count_denied">
        Showing {{c.count(c.rangeStart())}} to {{c.count(c.rangeEnd())}}
      </span>
      <span class="text-muted" ng-if="!c.hasRange()">No results to show</span>
    </div>
  </div>
</div>
```

`ng-if="item.total_funding_usd !== undefined"` is the omission test. A denied premium field has **no key** on the serialised object, so `undefined` is the correct comparison; do not test for an empty string and do not test for `null`, because a readable-but-empty currency column legitimately serialises as `null`.

##### Three states per gated column, and each renders words

The omission test splits the field into two branches; a readable column then splits again on whether it holds a value. **All three branches render something a caller can read** — the state a value is in is never conveyed by an empty row:

| State | Serialised as | What renders |
| --- | --- | --- |
| Withheld by the field-level access control | the key is **absent** | the column label beside a `.label.label-info` reading `Premium` |
| Readable and populated | a value | the column label beside the value, wrapped in `<bdi>` |
| Readable and empty | `null` | the column label beside `Not recorded` in `.text-muted` |

**The third row is the one an empty interpolation loses.** `{{item.total_funding_usd}}` on a `null` interpolates to the empty string, so the row renders as a fully bordered `.list-group-item` carrying a label and nothing else — indistinguishable from a rendering fault, and easy to read as "zero". `Not recorded` states which of the three it is. The same three-way split applies to `institutional_funding_last_5yrs`, where the trap is sharper still: a bare `{{value ? 'Yes' : 'No'}}` renders a `null` as **`No`**, asserting a fact the record does not carry.

##### What every surface must agree about

**A count, a range and a card set are three assertions about one query, and they are guarded together or they contradict each other.** Four states break the naive template, and the guards below are what the template carries:

| State | Without the guards | The guard, and where |
| --- | --- | --- |
| **Loading** | the heading asserts `0 matching` and the pager asserts `No results to show`, both derived from a `data` payload that has not arrived | `!c.busy` on the heading count span, on the pager region and on the `<hr>` above it. The empty-state alert already carried it. |
| **Failed, with a previous result set still in `data`** | a small banner sits above twenty detailed cards, a fresh total, a live pager and a blanked status region: past the first screenful the page is indistinguishable from a successful load, while premium figures are on screen and the caller has been told nothing was retracted | `!data.error` on the card repeat's wrapper, on the heading count span, on the upsell, on the pager region and on the `<hr>`. Only the failure alert, the not-entitled alert and the status region render. **A stale set is not shown at all** — showing it under a caption would still leave the caller deciding which parts of the screen to trust. |
| **Count withheld** (`count_denied`) | the heading count is correctly suppressed, but the pager still interpolates the raw total and reads `Showing 1 to 20 of 0`, and `c.hasNext()` compares `offset + limit < total_count` — `20 < 0` — so **Next is disabled and the caller can never page past the first page** | `!data.count_denied` selects between two range sentences, so the withheld total is never printed; `c.hasNext()` falls back to a full-page test, which is what restores paging; and one `.alert-info` states that the total is unavailable. |
| **Empty, with fields gated** | the upsell asserts *"Premium fields are hidden in these results"* and *"Your account reads every other column on this page"* over zero results, zero columns and no page content, three times the height of the actual answer and carrying the only saturated call to action on screen — inviting the caller to read it as the reason the search returned nothing | `data.result.length > 0` on the upsell. A statement about the fields in a result set is rendered only when there is a result set. |

**A withheld count is stated, not implied.** Suppressing the total and leaving everything else unchanged tells a caller nothing about *why* the number is missing, and when the page is also empty it reads as a definite "there are none". The `.alert-info` says which it is. It carries **no** live-region role, per [which alerts are live regions](#which-alerts-are-live-regions-and-which-are-not): it is permanent explanatory text beside the range it qualifies, and the range is announced by the loaded status wording.

**Large numbers are grouped.** `{{c.count(data.total_count)}}` in the heading, both range sentences and the loaded status wording. Without the filter a seven-digit total prints as `1234567` in three places on a page whose currency values on the same card carry separators — the inconsistency reads as two different kinds of number.

##### The logo cell, and what a broken image renders

**`.media-left` renders whenever `options.show_logo` is true, whether or not the record has a `logo_url`.** A cell that is present for some cards and absent for others moves the text of every card it is absent from left by the cell's width plus its gutter, so a mixed set renders a ragged left edge down the whole list. Rendering the cell unconditionally keeps one text edge; a record with no logo fills it with a platform glyph.

**The image's `alt` is the company name and the word `logo`, not the empty string.** A decorative `alt=""` is the correct choice for an image that duplicates adjacent text — but it also means a `logo_url` whose target has gone renders as **nothing at all**: no box, no text, no node in the accessibility tree, and a caller has no way to tell a missing logo from a broken one. A meaningful `alt` makes the browser's own broken-image fallback the fallback, which is why no `onerror` handler is needed: the alternative text is what paints when the fetch fails. `ng-src` is still the only binding used, so the [external locator rules](#external-locators-in-a-binding) are unchanged.

##### Two links per card, distinguished

Every card carries two targets to the same profile: the heading link, whose accessible name is the company name, and a `.btn` reading `View profile`. **The second carries `aria-label="View the {{::item.name}} profile"`**, because twenty cards otherwise contribute twenty links named `View profile` to a links list with nothing to choose between them. The pair is deliberate — the heading is the reading-order target and the button is the scanning target — and naming them differently is what makes both usable rather than one being noise.

**The `View profile` control is an `<a>`, not a `<button>`, because it navigates.** It therefore activates on Enter and not on Space, which differs from the pager's real `<button>` elements. That difference is correct rather than an inconsistency to paper over: a control that changes the address is a link and a control that acts on this page is a button, and swapping either would misreport what the control does.

##### The upsell heading's id is unique per instance

`aria-labelledby` resolves by id against the whole document, so a fixed `id="bst-results-upsell-title"` breaks the moment a page carries two instances of this widget — two identical ids, and the attribute resolves to whichever the parser saw first. The id is therefore suffixed with `c.uid`, the controller's own per-instance value, exactly as `bst-company-profile` suffixes its ids with the record's `sys_id`.

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
    max-width: $navbar-height;
    width: auto;
    height: auto;
}

.bst-results .media-left {
    min-width: $navbar-height;
    padding-right: 0;
    overflow: hidden;
}

.bst-results .media-body {
    overflow-wrap: break-word;
    padding-left: $padding-base-horizontal;
}

.bst-results .media-heading {
    line-height: normal;
}

.bst-results .list-group-item {
    unicode-bidi: isolate;
}

.bst-results .media-body .label {
    margin-right: $padding-base-vertical;
}

.bst-results .bst-results-pager {
    margin-top: $grid-gutter-width;
}

.bst-results .bst-results-upsell {
    margin-top: $grid-gutter-width;
    border-radius: $border-radius-base;
}

.bst-results .bst-results-upsell .panel-title {
    margin-bottom: $padding-base-vertical;
}

.bst-results .sr-only {
    position: absolute;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
}

.bst-results .bst-results-upsell .btn {
    margin-top: $padding-base-vertical;
}

/* A heading moved into focus programmatically with no ring is a caller who has
   been silently relocated: the reading position changed and nothing on screen
   says so. Bootstrap styles no indicator for [tabindex="-1"], so each widget
   declares its own, scoped to itself. The widget root carries the attribute too,
   as the fallback destination for a retry whose heading does not yet exist.
   See "Busy, status and focus behaviour". */
.bst-results [tabindex="-1"]:focus,
.bst-results[tabindex="-1"]:focus {
    outline: $border-radius-base solid $brand-primary;
    outline-offset: $border-radius-small;
}

@media (prefers-reduced-motion: reduce) {
    .bst-results .progress-bar {
        animation: none;
    }
}

@media (forced-colors: active) {
    .bst-results .label {
        border-style: solid;
    }
}
```

Five of those rules exist for a reason that is not visible in the declaration, so each is stated:

- **`.media-left { min-width: $navbar-height; padding-right: 0; overflow: hidden }` with the gutter moved to `.media-body { padding-left: $padding-base-horizontal }`.** The purpose is one text edge down the whole list: a card whose logo is a narrow glyph placeholder, a card whose logo is a wide wordmark and a card whose `logo_url` is dead must all start their text at the same x. `min-width` alone does not achieve that, and the reason is arithmetic worth stating because it is invisible in the declaration. Bootstrap gives `.media-left` `padding-right: 10px`, and the framework sets `box-sizing: border-box` globally, so a `min-width` of `$navbar-height` leaves a **content box narrower than the token** — 40px, not 50px. The image cap above is the full `$navbar-height`, so a logo that fills its cap needs 50px of content and forces the cell to 60px, moving that one card's text 10px right of every other card's. A dead `logo_url` does exactly that: the browser's own fallback renders the `alt` text in the replaced box, which wants more room than the cap allows, so the box settles at precisely `max-width` and the cell grows. Taking the padding out of the cell makes the content box equal to the token, so all three cases resolve to the same 50px, and the gutter is re-established on the other cell where it cannot compete with the cap. `overflow: hidden` then bounds the fallback text to the slot it was given rather than letting it bleed into the row beneath; the accessible name is carried by `alt` and is unaffected by the clip.
- **`.media-heading { line-height: normal }`** lets the line box grow to a grapheme carrying stacked combining marks instead of clipping it into the description below. See [the cleaning rules these widgets depend on](#the-cleaning-rules-these-widgets-depend-on).
- **`.list-group-item { unicode-bidi: isolate }`** stops a right-to-left value interpolated beside product wording — `Total funding`, `Institutional funding in the last five years` — from reordering the label in front of it. The `<bdi>` elements in the template carry the same guarantee for the values themselves; the rule extends it to a row that interpolates directly.
- **The pager carries no border declaration.** The separator above it is an `<hr>`, which Bootstrap already draws with a width, a style and a colour. The rule this replaces set `border-top-color` with no `border-top-width` and no `border-top-style`, so the computed width stayed `0` and the separator was **never drawn** — a colour with nothing to colour. Reaching for the framework's own separator element is both the [library-components](#library-components-over-raw-html) answer and the one that adds no measured literal, because a border width would have had to be one.
- **`border-style: solid` on `.label` under forced colours** restores the chip's shape. Bootstrap's `.label` carries no border and conveys itself entirely by `background-color`, which that mode discards — so without this rule the `Premium` marker computes to black-on-white bold text with `border: 0px none` and becomes indistinguishable from the words around it. That marker is the visible face of the whole field-gating design, so it has to survive. Two properties of the declaration are deliberate. It names only the **style**: `border-width` is then the initial `medium` and `border-color` the initial `currentColor`, so the rule introduces no measured literal and the border is drawn in whatever colour the caller's own palette resolves `color` to — guaranteed to contrast with their own background, which is the entire point of the mode. And it does **not** use `forced-color-adjust: none` to hold the authored fills instead. That was the first approach and it was wrong twice over: it opts the chips out of the palette the caller deliberately chose, and it hands them Bootstrap's white-on-`.label-info` pairing, which measures **2.09:1** — below every WCAG threshold — precisely in the mode a caller reaches for because they need contrast. A border costs the grouping cue that colour gave and keeps the information, because **no chip conveys its meaning by colour alone**: each carries its own text.

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
| `full_list_page` | string | *empty* | The `sp_page.id` the "open the full list" link of a truncated pane targets, carrying that pane's table and this record's `sys_id` as query parameters. **Leave it empty on this delivery**: the five portal routes of [`../../../docs/review/CRITICAL_DECISIONS.md`](../../../docs/review/CRITICAL_DECISIONS.md) do not include a full-list page, so no link is rendered and each truncated pane states its totals in the caption instead. Set it only if a full-list page is added later. |

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

**Every `ng-repeat` over one of these five collections iterates `<collection>.rows`, never the collection itself.** The published value is the four-member object, so `ng-repeat="round in data.rounds"` would iterate that object's own keys — `rows`, `limit`, `total`, `truncated` — and `track by round.sys_id` would evaluate to `undefined` on each of them, which raises `[ngRepeat:dupes]` on the second key and **abandons the whole repeater**: the pane renders no rows at all while its caption still advertises the total. All five repeats therefore name `.rows`, and every caption in the same pane reads the sibling members off the same object.

**The cost is two queries per collection** — one bounded read and one `COUNT` aggregate — so ten queries for the five panes, whatever the size of the company. With the record read and the batched join read that is the twelve of [The query budget of each page](#the-query-budget-of-each-page). Before the limits, one profile could read every child row of the largest company in the table on every render.

5. Assemble `participating_investors` for each funding round **from the join table**, `x_bst_startuptrk_m2m_round_investor`, and never from the derived `x_bst_startuptrk_fundinground.participating_investors` column. Call `new InvestorPortfolioService().participantsForRounds(roundIds)` with the identifiers of the rounds on the page — one batched read for the whole page, not one read per round — and attach the result to each round as `round.participating_investors`. **The identifiers come from `data.rounds.rows`**, and the attachment is onto those same row objects, so the template's `ng-repeat` over `round.participating_investors` reads what this item wrote:

```javascript
var roundIds = data.rounds.rows.map(function (round) { return String(round.sys_id); });
var participants = new InvestorPortfolioService().participantsForRounds(roundIds);
data.rounds.rows.forEach(function (round) {
    round.participating_investors = participants[round.sys_id] || [];
});
```

   The default of an empty array matters: a round with no participant then renders nothing rather than leaving the expression undefined.
6. Compute the gate flags the template needs, each by testing the serialised object for the **absence of the key**:

```javascript
data.gated = {
    total_funding_usd: data.startup.total_funding_usd === undefined,
    institutional_funding_last_5yrs: data.startup.institutional_funding_last_5yrs === undefined,
    founder_contact_email: data.founders.rows.some(function (f) { return f.contact_email === undefined; }),
    executive_contact_email: data.executives.rows.some(function (e) { return e.contact_email === undefined; }),
    amount_usd: data.rounds.rows.some(function (r) { return r.amount_usd === undefined; }),
    valuation_usd: data.rounds.rows.some(function (r) { return r.valuation_usd === undefined; })
};
data.gatedAny = Object.keys(data.gated).some(function (key) { return data.gated[key]; });
```

7. Embed the upsell partial when anything is gated:

```javascript
if (data.gatedAny) {
    data.upsell = $sp.getWidget('bst-premium-upsell', {
        context: 'company',
        gated_fields: 'total_funding_usd,institutional_funding_last_5yrs,amount_usd,valuation_usd,contact_email',
        upsell_page: options.upsell_page,
        heading: 'Premium data is hidden on this profile'
    });
}
```

8. Publish `data.tabs` as the five pane descriptors in order, so the tab strip is data-driven and cannot drift from the pane list: `overview` / **Overview**, `funding` / **Funding**, `people` / **People**, `jobs` / **Jobs**, `news` / **News**. Give each descriptor an `id`, a `label` and a `total`:

```javascript
data.tabs = [
    { id: 'overview', label: 'Overview', total: null },
    { id: 'funding',  label: 'Funding',  total: data.rounds.total },
    { id: 'people',   label: 'People',   total: data.founders.total + data.executives.total },
    { id: 'jobs',     label: 'Jobs',     total: data.jobs.total },
    { id: 'news',     label: 'News',     total: data.news.total }
];
```

**Every published `total` is rendered**, as a `.badge` inside that tab's control — see the tab strip in the template below. `overview` carries `null` rather than a number because it is not a collection, and the template renders no badge where the total is `null`. A total that is published and not rendered is a dead output; a badge whose number came from anywhere other than this descriptor would disagree with the pane it labels.
9. Publish every one of the **five collections** as the four-member object `childCollection()` returns — **never as a bare array** — and publish it unconditionally, with `rows` empty rather than absent when nothing matched:

```javascript
data.rounds     = childCollection('x_bst_startuptrk_fundinground', roundFields,   'round_date',     true,  options.funding_limit);
data.founders   = childCollection('x_bst_startuptrk_founder',      personFields,  'name',           false, options.people_limit);
data.executives = childCollection('x_bst_startuptrk_executive',    personFields,  'name',           false, options.people_limit);
data.jobs       = childCollection('x_bst_startuptrk_jobposting',   jobFields,     'posted_date',    true,  options.jobs_limit);
data.news       = childCollection('x_bst_startuptrk_newsarticle',  newsFields,    'published_date', true,  options.news_limit);
```

Each of the five therefore carries `rows`, `total`, `limit` and `truncated`. A template that has to distinguish "no rows" from "key missing" cannot render a reliable empty state, so the object and its `rows` array are both published on every path that reaches this item.

**Publish the full-list route once, as `data.fullListPage`**, from `options.full_list_page` falling back to the empty string. It is the `sp_page.id` the "open the full list" link of each truncated pane targets, and the link carries the pane's own table and this record's `sys_id` as query parameters so the destination opens filtered to this company. When the option is empty no full-list link is rendered and the truncation caption still states the totals, which is the honest degradation: the reader is told the list is a window even where there is no wider view to open.

#### Data contract

**Every member below is assigned onto `data` by the server script named in its row, and read by the consumer named in its row. There is no third source and no other member**: a template expression naming anything absent from this table renders nothing at best and raises a runtime expression error at worst, and a member published with no consumer is a dead output. `data.error` is not in any widget's table — it is set on the client by the shared `c.load()` helper of [Error and empty behaviour](#error-and-empty-behaviour) and by nothing on the server. A widget whose own server script catches a failure and reports it publishes that message as **`data.serverError`**, which **is** in that widget's table, and which `c.load()` never touches; the error panel renders `c.errorText()`, which answers either of the two.

| Member | Type | Published by | Consumed by |
| --- | --- | --- | --- |
| `authorised` | True/False | server item 1 | Template — the not-entitled alert and the `ng-if` on the profile |
| `notFound` | True/False | server item 2 | Template — the not-found alert |
| `startup` | Serialised record | server item 3 | Template — the heading, the overview list and the description |
| `rounds` | `{rows,total,limit,truncated}` | server items 4 and 9 | Template — the Funding pane's table, caption and full-list link |
| `founders` | `{rows,total,limit,truncated}` | server items 4 and 9 | Template — the People pane's founders list and caption |
| `executives` | `{rows,total,limit,truncated}` | server items 4 and 9 | Template — the People pane's executives list and caption |
| `jobs` | `{rows,total,limit,truncated}` | server items 4 and 9 | Template — the Jobs pane's table, caption and full-list link |
| `news` | `{rows,total,limit,truncated}` | server items 4 and 9 | Template — the News pane's list and caption |
| `fullListPage` | String | server item 9 | Template — the `ng-if` and `href` of every pane's full-list link |
| `gated` | Object of six booleans | server item 6 | **Server-side only** — item 6 reduces it into `gatedAny`. The template tests each serialised object for the absent key directly, so no expression reads this member |
| `gatedAny` | True/False | server item 6 | **Server-side only** — item 7's embed decision |
| `upsell` | Widget model | server item 7 | Template — `<sp-widget widget="data.upsell">` |
| `tabs` | Array of `{id,label,total}` | server item 8 | Template — the tab strip and its `.badge` totals |

#### Client controller

1. Implement `c.load()` and `c.retry()` exactly as [Error and empty behaviour](#error-and-empty-behaviour) specifies. Every server call below goes through `c.load()`.
2. **Initialise `c.activeTab` from `$location.search().tab`**, falling back to `options.default_tab`, and then to `overview`. The URL wins over the option because a caller who was given a link to a specific pane asked for that pane; the option is the default for a caller who arrived without one. An unrecognised value in either falls through to `overview` rather than leaving the widget with no active pane — the five identifiers are fixed by the route specification and are validated against that list, not against `data.tabs`, which has not arrived yet when this runs.
3. Implement the whole of [The tab contract](#the-tab-contract) — `c.select(tabId, replaceHistory)`, `c.isActive(tabId)`, `c.tabIndex(tabId)`, `c.tabId(tabId)`, `c.panelId(tabId)` and `c.onTabKey($event, tabId)`, **including the URL mirroring under [the selected pane is in the URL](#the-selected-pane-is-in-the-url)**.
4. Read the record identifier from `$location.search().sys_id` when a client-side refresh is needed, and call `c.load()`.
5. Do not fetch data per tab. All five panes arrive in one server round trip.
6. **Watch the record only when there is a record to watch, and let scope destruction release the watch.** `data.startup` is absent on both expected non-render paths — the unauthorised path of server-script item 1 and the not-found path of item 2 — so an unguarded `c.data.startup.sys_id` raises a `TypeError` on exactly the two paths the template handles. Guard the object and its identifier, register the watch against a child scope this controller owns, and destroy that child scope to release it:

```javascript
var ID32 = /^[0-9a-f]{32}$/;
var watchScope = null;
var watchedId = '';

// spUtil.recordWatch() returns a PROMISE, not an unsubscribe handle: there is nothing
// on its result to call. The supported release is scope destruction, so the watch is
// registered against a CHILD scope this controller owns and destroying that child is
// what releases it. Registering on every load would accumulate one live subscription
// per refresh, which is what re-subscribing with a promise as a handle actually did.
function releaseWatch() {
    if (watchScope) {
        watchScope.$destroy();
        watchScope = null;
    }
    watchedId = '';
}

function startWatch() {
    var record = c.data && c.data.startup;
    var id = record ? '' + record.sys_id : '';
    if (!id || !ID32.test(id)) {
        releaseWatch();
        return;
    }
    if (id === watchedId) {
        return;                       // already watching exactly this record
    }
    releaseWatch();                   // a different record: drop the old subscription
    watchScope = $scope.$new();
    watchedId = id;
    spUtil.recordWatch(watchScope, 'x_bst_startuptrk_startup', 'sys_id=' + id);
}

startWatch();
$scope.$on('$destroy', releaseWatch);
```

   `startWatch()` runs at controller initialisation and again from the promise callback of every `c.load()`, and it is **idempotent**: a load that yields the same `sys_id` returns without touching the subscription, so a refresh leaves exactly one live watch rather than one more. Only a change of record identity, or a load that publishes no record, destroys the child scope — which is what releases the subscription, because `spUtil.recordWatch()` answers a promise and there is no handle to unsubscribe.
7. Declare `c.busy` and `c.statusText()` per [Busy, status and focus behaviour](#busy-status-and-focus-behaviour), and also declare `c.focusDestination()` and `c.onButtonKey($event)` per that same section, `c.indeterminate()` for the striped bar, and `c.money()` and `c.day()` per [The display contract](#the-display-contract). **Six states, tested in this order, and every one of them answered** — an order that stops before the end returns whichever branch it last matched, which is how a caller who was denied the record, or told it does not exist, ends up hearing a sentence about related records instead:

   | # | Condition | Returns | Who announces this state instead |
   | --- | --- | --- | --- |
   | 1 | `c.busy` | `Loading` | — |
   | 2 | `!c.data.authorised` | **the empty string** | the not-entitled `.alert-warning`, which carries `role="alert"` |
   | 3 | `c.data.error` | **the empty string** | the failure `.alert-danger`, which carries `role="alert"` and owns **Retry** |
   | 4 | `c.data.notFound` | **the empty string** | the not-found `.alert-warning`, which carries `role="alert"` |
   | 5 | all five collections empty | `No related records are recorded for this company.` | this region — the five per-pane messages carry no role, per [which alerts are live regions](#which-alerts-are-live-regions-and-which-are-not) |
   | 6 | otherwise | `{{c.data.startup.name}} loaded. {{c.data.rounds.total}} funding rounds, {{c.data.founders.total + c.data.executives.total}} people, {{c.data.jobs.total}} open roles, {{c.data.news.total}} articles.` | this region |

   Rows 2, 3 and 4 return nothing **because a visible element with a live-region role already owns each of those states**; a sentence here would be a second announcement of one fact. Row 6 states the collection **`total`, not `rows.length`**, so a screen-reader caller is told the size of the record rather than the size of the window; each pane's caption then states how much of it is rendered.
8. **Expose `c.stateHeading()`, which names the page on the three paths that render no record.** The success path's `<h1>` is the company name inside the profile header, and that element is inside the `ng-if` that the unauthorised, not-found and failed paths all exclude — so on each of those three the document previously had **no heading at all**, and a caller navigating by heading landed on a page with nothing to land on. The helper returns a string on exactly those three paths and the empty string on the success path, so the `<h1 ng-if="c.stateHeading()">` and the profile header's `<h1>` are mutually exclusive and the page always renders **exactly one** `<h1>`, as [rule 9](#rules-that-bind-all-eight) requires:

```javascript
c.stateHeading = function () {
    if (!c.data.authorised) { return 'Company profile'; }
    if (c.data.error)       { return 'Company profile'; }
    if (c.data.notFound)    { return 'Company not found'; }
    return '';                        // the profile header's own h1 is the heading
};
```

   The not-found wording differs because that state is the answer to a specific request rather than a condition of the caller's account, and a heading that says so saves them reading the alert to find out. The other two return the page's own name: the reason the record is absent is the alert's job to state, not the heading's.
9. Expose `c.unrendered(collection)` exactly as [rendered rows and model rows must agree](#rendered-rows-and-model-rows-must-agree) specifies, and inject `$element` into the controller so it can count the rendered rows of its own widget. **All five collections are reconciled here, and this is the widget that proves why the rule exists**: its three table-and-list repeats once iterated the four-member envelope instead of its `rows` array, which raises `ngRepeat:dupes` and abandons the repeat, and because `c.isEmpty()` reads `rows` correctly the empty state stayed hidden while every caption above the blank region kept asserting the rows it had. Each repeat's root element carries `data-bst-row="<collection>"` — `rounds`, `founders`, `executives`, `jobs`, `news` — and each notice carries its own region's guard as that section's table specifies.
10. Expose `c.isEmpty(collection)`, returning `true` when the named collection's `rows` array has no entries, used by the five empty states in the template. It reads the four-member object, so it is defensive about a collection that never arrived:

```javascript
c.isEmpty = function (collection) {
    var published = c.data && c.data[collection];
    return !published || !published.rows || published.rows.length === 0;
};
```

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
| `Enter`, `Space` | Select the focused pane, **as an explicit activation** — `c.select(pane)` with no second argument, so it adds a history entry. The control is an anchor, so `Enter` already activates it; handle `Space` explicitly. |

The four movement keys call `c.select(pane, true)`, which amends the current history entry instead of adding one; `ng-click` and the two activation keys call `c.select(pane)`. See [the selected pane is in the URL](#the-selected-pane-is-in-the-url).

Every one of those keys calls `$event.preventDefault()`, so `ArrowLeft` and `ArrowRight` do not also scroll the page and `Space` does not page down. No other key is handled: `ArrowUp`, `ArrowDown` and `Tab` keep their default behaviour, because this strip is horizontal and automatic activation is what the pattern prescribes for a tab set whose panes are already loaded.

**Selection follows focus.** All five panes arrive in one server round trip, so selecting a pane costs nothing and the arrow keys select as they move. Focus stays on the strip; it never jumps into the pane.

##### The selected pane is in the URL

**A tab set that writes nothing to the address bar breaks the browser's own back button, and the failure is worse than it sounds.** With the selection held only in `c.activeTab`, opening a pane changes neither the URL nor `history.length` — so **Back leaves the record entirely**, and a caller four panes deep loses their place with one keystroke. Forward can appear to restore the pane, but only because the browser served the same document from its back-forward cache; anything that evicts the document lands the caller on `overview` with nothing in the URL, in storage or in the DOM able to rebuild what they had chosen. A pane is also then unlinkable: there is no address that opens a profile at its Funding tab. This portal already mirrors search criteria into `$location.search()` for exactly that reason, and applying the value to one widget and not another is the inconsistency being closed.

**`c.select(tabId, replaceHistory)` mirrors the selection into `$location.search('tab', tabId)`.** The second argument decides whether the step is a history entry, and the distinction matters because this strip activates automatically:

```javascript
var PANES = ['overview', 'funding', 'people', 'jobs', 'news'];

function resolvePane(candidate) {
    return PANES.indexOf('' + candidate) === -1 ? '' : '' + candidate;
}

c.select = function (tabId, replaceHistory) {
    var pane = resolvePane(tabId);
    if (!pane || pane === c.activeTab) {
        return;                       // unknown pane, or already there: write nothing
    }
    c.activeTab = pane;
    if (replaceHistory) {
        $location.replace();          // arrow traversal: amend the entry, do not add one
    }
    $location.search('tab', pane);
};

// Back and Forward change the URL without passing through c.select(), so the pane has
// to follow the URL as well as lead it. Registered on $scope, and released with it.
var stopLocationWatch = $scope.$on('$locationChangeSuccess', function () {
    var pane = resolvePane($location.search().tab) || 'overview';
    if (pane !== c.activeTab) {
        c.activeTab = pane;
    }
});
$scope.$on('$destroy', stopLocationWatch);
```

**Why arrow keys replace and a click pushes.** `ArrowRight` four times is one traversal of the strip, not four destinations; pushing an entry per press would mean four Back presses to leave the record, which trades the reported fault for its mirror image. An explicit activation — a pointer click, or `Enter` or `Space` — is a destination the caller chose, so it earns an entry and Back returns them to the pane they were on. `Home` and `End` replace for the same reason as the arrows: they are movements within the strip.

**The early return on `pane === c.activeTab` is load-bearing**, not an optimisation. Automatic activation fires `c.select()` on every arrow press, and `Enter` on an already-selected pane fires it again; without the guard, re-selecting the current pane would write a duplicate entry that Back would appear to ignore.

**One parameter serves the page, because the page renders one profile.** The pane identifiers are namespaced per record in `c.tabId()` and `c.panelId()` so two profiles in one document cannot collide on their element ids, but `tab` is a page-level parameter and the route specification gives `bst_company` exactly one profile.

#### HTML template

```html
<div class="bst-company" tabindex="-1" aria-busy="{{c.busy}}">
  <div class="sr-only" role="status" aria-live="polite" aria-atomic="true">{{c.statusText()}}</div>

  <h1 class="bst-company-state-heading" tabindex="-1" ng-if="c.stateHeading()">{{c.stateHeading()}}</h1>

  <div class="alert alert-warning" role="alert" ng-if="!data.authorised">
    <span>Your account holds no Boston Startup Tracker role.</span>
  </div>

  <div class="alert alert-warning" role="alert" ng-if="data.notFound">
    <span>That company could not be found.</span>
    <a class="btn btn-default" ng-keydown="c.onButtonKey($event)"
       ng-href="?id=bst_home">Back to search</a>
  </div>

  <div class="alert alert-danger" role="alert" ng-if="c.errorText()">
    <span class="icon-cross-circle" aria-hidden="true">&nbsp;</span>
    <span>{{c.errorText()}}</span>
    <button type="button" class="btn btn-default" ng-click="c.retry()">Retry</button>
  </div>

  <div class="progress" ng-if="c.busy">
    <div class="progress-bar progress-bar-striped active" role="progressbar"
         ng-style="c.indeterminate()"
         aria-label="Loading company profile" aria-valuemin="0" aria-valuemax="100"
         aria-valuetext="Loading"></div>
  </div>

  <div ng-if="data.authorised &amp;&amp; !c.busy &amp;&amp; !data.notFound &amp;&amp; !c.errorText()">
    <div class="panel panel-default">
      <div class="panel-body">
        <div class="media">
          <div class="media-left" ng-if="::data.startup.logo_url">
            <img class="media-object bst-company-logo" ng-src="{{::data.startup.logo_url}}" alt="" />
          </div>
          <div class="media-body">
            <h1 class="media-heading" dir="auto" tabindex="-1">{{::data.startup.name}}</h1>
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
      <li ng-repeat="tab in ::data.tabs track by tab.id" ng-class="{active: c.isActive(tab.id)}" role="presentation">
        <a href
           role="tab"
           id="{{c.tabId(tab.id)}}"
           aria-controls="{{c.panelId(tab.id)}}"
           aria-selected="{{c.isActive(tab.id)}}"
           tabindex="{{c.tabIndex(tab.id)}}"
           ng-click="c.select(tab.id)"
           ng-keydown="c.onTabKey($event, tab.id)">
          <span>{{::tab.label}}</span>
          <span class="badge" ng-if="tab.total !== null">{{tab.total}}</span>
        </a>
      </li>
    </ul>

    <div class="tab-content">
      <div class="tab-pane" role="tabpanel"
           id="{{c.panelId('overview')}}" aria-labelledby="{{c.tabId('overview')}}"
           ng-class="{active: c.isActive('overview')}">
        <ul class="list-group">
          <li class="list-group-item">Headquarters <span class="pull-right"><bdi dir="auto">{{::data.startup.headquarters_location}}</bdi></span></li>
          <li class="list-group-item">Founded <span class="pull-right">{{::data.startup.founded_year}}</span></li>
          <li class="list-group-item">Employees <span class="pull-right">{{::data.startup.employee_count_range}}</span></li>
          <li class="list-group-item">Website <span class="pull-right">
            <a ng-href="{{::data.startup.website}}" ng-if="::data.startup.website">Visit the company website</a>
            <span class="text-muted" ng-if="::!data.startup.website">Not recorded</span>
          </span></li>
          <li class="list-group-item" ng-if="data.startup.total_funding_usd !== undefined">
            Total funding <span class="pull-right">{{c.money(data.startup.total_funding_usd)}}</span>
          </li>
          <li class="list-group-item" ng-if="data.startup.institutional_funding_last_5yrs !== undefined">
            Institutional funding in the last five years
            <span class="pull-right"><span class="label label-default">{{data.startup.institutional_funding_last_5yrs ? 'Yes' : 'No'}}</span></span>
          </li>
        </ul>
        <p dir="auto">{{::data.startup.description}}</p>
      </div>

      <div class="tab-pane" role="tabpanel"
           id="{{c.panelId('funding')}}" aria-labelledby="{{c.tabId('funding')}}"
           ng-class="{active: c.isActive('funding')}">
        <div class="alert alert-info" ng-if="c.isEmpty('rounds')">
          <span>No funding round is recorded for this company.</span>
        </div>
        <div class="table-responsive" tabindex="0" ng-if="!c.isEmpty('rounds')">
          <table class="table table-striped table-hover">
            <caption class="sr-only">Funding rounds for this company, most recent first, one row per round</caption>
            <thead>
              <tr>
                <th scope="col">Date</th><th scope="col">Round</th><th scope="col">Amount</th><th scope="col">Valuation</th>
                <th scope="col">Lead investor</th><th scope="col">Participating investors</th><th scope="col">Source</th>
              </tr>
            </thead>
            <tbody>
              <tr data-bst-row="rounds"
                  ng-repeat="round in data.rounds.rows track by round.sys_id">
                <th scope="row">{{c.day(round.round_date)}}</th>
                <td><span class="label label-primary" ng-if="::round.round_type">{{::round.round_type}}</span></td>
                <td ng-if="round.amount_usd !== undefined">{{c.money(round.amount_usd)}}</td>
                <td ng-if="round.amount_usd === undefined"><span class="label label-info">Premium</span></td>
                <td ng-if="round.valuation_usd !== undefined">{{c.money(round.valuation_usd)}}</td>
                <td ng-if="round.valuation_usd === undefined"><span class="label label-info">Premium</span></td>
                <td>
                  <a dir="auto" ng-if="::round.lead_investor"
                     ng-href="?id={{::options.investor_page}}&amp;sys_id={{::round.lead_investor.value}}">{{::round.lead_investor.display_value}}</a>
                </td>
                <td>
                  <a class="label label-default" ng-repeat="investor in ::round.participating_investors track by $index"
                     ng-href="?id={{::options.investor_page}}&amp;sys_id={{::investor.value}}">{{::investor.display_value}}</a>
                </td>
                <td><a ng-href="{{::round.source_url}}" ng-if="::round.source_url">Source</a></td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="alert alert-warning" role="alert"
             ng-if="!c.isEmpty('rounds') &amp;&amp; c.unrendered('rounds')">
          <span class="icon-warning-triangle" aria-hidden="true">&nbsp;</span>
          <span>{{c.unrendered('rounds')}} of {{data.rounds.rows.length}} funding rounds could not be displayed.
            Reload the page; if it recurs, report it with this page address.</span>
        </div>
          <p class="text-muted bst-collection-caption" ng-if="data.rounds.truncated">
            <span>Showing {{c.count(data.rounds.rows.length)}} of {{c.count(data.rounds.total)}}, the {{c.count(data.rounds.limit)}} most recent.</span>
            <a ng-if="::data.fullListPage"
               ng-href="?id={{::data.fullListPage}}&amp;table=x_bst_startuptrk_fundinground&amp;startup={{::data.startup.sys_id}}">Open the full list</a>
          </p>
      </div>

      <div class="tab-pane" role="tabpanel"
           id="{{c.panelId('people')}}" aria-labelledby="{{c.tabId('people')}}"
           ng-class="{active: c.isActive('people')}">
        <div class="row">
          <div class="col-md-6 col-lg-6">
            <div class="panel panel-default">
              <div class="panel-heading"><h2 class="panel-title">Founders</h2></div>
              <ul class="list-group">
                <li class="list-group-item" ng-if="c.isEmpty('founders')">
                  No founder is recorded for this company.
                </li>
                <li class="list-group-item" data-bst-row="founders"
                    ng-repeat="person in data.founders.rows track by person.sys_id">
                  <strong dir="auto">{{::person.name}}</strong>
                  <span class="label label-default" ng-if="::person.title">{{::person.title}}</span>
                  <p dir="auto">{{::person.bio}}</p>
                  <a ng-href="{{::person.linkedin_url}}" ng-if="::person.linkedin_url">
                    <span class="icon-user" aria-hidden="true">&nbsp;</span>LinkedIn
                  </a>
                  <span ng-if="person.contact_email !== undefined"><bdi dir="auto">{{person.contact_email}}</bdi></span>
                  <span class="label label-info" ng-if="person.contact_email === undefined">Premium</span>
                </li>
              </ul>
              <div class="alert alert-warning" role="alert"
                   ng-if="!c.isEmpty('founders') &amp;&amp; c.unrendered('founders')">
                <span class="icon-warning-triangle" aria-hidden="true">&nbsp;</span>
                <span>{{c.unrendered('founders')}} of {{data.founders.rows.length}} founders could not be displayed.
                  Reload the page; if it recurs, report it with this page address.</span>
              </div>
          <p class="text-muted bst-collection-caption" ng-if="data.founders.truncated">
            <span>Showing {{c.count(data.founders.rows.length)}} of {{c.count(data.founders.total)}}, the {{c.count(data.founders.limit)}} most recent.</span>
            <a ng-if="::data.fullListPage"
               ng-href="?id={{::data.fullListPage}}&amp;table=x_bst_startuptrk_founder&amp;startup={{::data.startup.sys_id}}">Open the full list</a>
          </p>
            </div>
          </div>
          <div class="col-md-6 col-lg-6">
            <div class="panel panel-default">
              <div class="panel-heading"><h2 class="panel-title">Executives</h2></div>
              <ul class="list-group">
                <li class="list-group-item" ng-if="c.isEmpty('executives')">
                  No executive is recorded for this company.
                </li>
                <li class="list-group-item" data-bst-row="executives"
                    ng-repeat="person in data.executives.rows track by person.sys_id">
                  <strong dir="auto">{{::person.name}}</strong>
                  <span class="label label-default" ng-if="::person.title">{{::person.title}}</span>
                  <p dir="auto">{{::person.bio}}</p>
                  <a ng-href="{{::person.linkedin_url}}" ng-if="::person.linkedin_url">
                    <span class="icon-user" aria-hidden="true">&nbsp;</span>LinkedIn
                  </a>
                  <span ng-if="person.contact_email !== undefined"><bdi dir="auto">{{person.contact_email}}</bdi></span>
                  <span class="label label-info" ng-if="person.contact_email === undefined">Premium</span>
                </li>
              </ul>
              <div class="alert alert-warning" role="alert"
                   ng-if="!c.isEmpty('executives') &amp;&amp; c.unrendered('executives')">
                <span class="icon-warning-triangle" aria-hidden="true">&nbsp;</span>
                <span>{{c.unrendered('executives')}} of {{data.executives.rows.length}} executives could not be displayed.
                  Reload the page; if it recurs, report it with this page address.</span>
              </div>
          <p class="text-muted bst-collection-caption" ng-if="data.executives.truncated">
            <span>Showing {{c.count(data.executives.rows.length)}} of {{c.count(data.executives.total)}}, the {{c.count(data.executives.limit)}} most recent.</span>
            <a ng-if="::data.fullListPage"
               ng-href="?id={{::data.fullListPage}}&amp;table=x_bst_startuptrk_executive&amp;startup={{::data.startup.sys_id}}">Open the full list</a>
          </p>
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
        <div class="table-responsive" tabindex="0" ng-if="!c.isEmpty('jobs')">
          <table class="table table-striped table-hover">
            <caption class="sr-only">Open roles at this company, one row per posting</caption>
            <thead>
              <tr><th scope="col">Title</th><th scope="col">Department</th><th scope="col">Location</th><th scope="col">Working pattern</th>
                  <th scope="col">Seniority</th><th scope="col">Posted</th><th scope="col">Open</th></tr>
            </thead>
            <tbody>
                <tr data-bst-row="jobs"
                    ng-repeat="job in data.jobs.rows track by job.sys_id">
                  <th scope="row">
                    <a dir="auto" ng-href="{{::job.url}}" ng-if="::job.url">{{::job.title}}</a>
                    <span dir="auto" ng-if="::!job.url">{{::job.title}}</span>
                  </th>
                <td>{{::job.department}}</td>
                <td dir="auto">{{::job.location}}</td>
                <td><span class="label label-default" ng-if="::job.remote_type">{{::job.remote_type}}</span></td>
                <td>{{::job.seniority}}</td>
                  <td>{{c.day(job.posted_date)}}</td>
                  <td>
                    <span class="label label-primary" ng-if="::job.active">Open</span>
                    <span class="label label-default" ng-if="::!job.active">Closed</span>
                  </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="alert alert-warning" role="alert"
             ng-if="!c.isEmpty('jobs') &amp;&amp; c.unrendered('jobs')">
          <span class="icon-warning-triangle" aria-hidden="true">&nbsp;</span>
          <span>{{c.unrendered('jobs')}} of {{data.jobs.rows.length}} open roles could not be displayed.
            Reload the page; if it recurs, report it with this page address.</span>
        </div>
          <p class="text-muted bst-collection-caption" ng-if="data.jobs.truncated">
            <span>Showing {{c.count(data.jobs.rows.length)}} of {{c.count(data.jobs.total)}}, the {{c.count(data.jobs.limit)}} most recent.</span>
            <a ng-if="::data.fullListPage"
               ng-href="?id={{::data.fullListPage}}&amp;table=x_bst_startuptrk_jobposting&amp;startup={{::data.startup.sys_id}}">Open the full list</a>
          </p>
      </div>

      <div class="tab-pane" role="tabpanel"
           id="{{c.panelId('news')}}" aria-labelledby="{{c.tabId('news')}}"
           ng-class="{active: c.isActive('news')}">
        <ul class="list-group">
          <li class="list-group-item" ng-if="c.isEmpty('news')">
            No news article is recorded for this company.
          </li>
          <li class="list-group-item" data-bst-row="news"
              ng-repeat="article in data.news.rows track by article.sys_id">
            <h3 class="list-group-item-heading">
                <a dir="auto" ng-href="{{::article.url}}" ng-if="::article.url">{{::article.title}}</a>
                <span dir="auto" ng-if="::!article.url">{{::article.title}}</span>
            </h3>
            <p class="list-group-item-text" dir="auto">{{::article.summary}}</p>
            <span class="text-muted"><bdi dir="auto">{{::article.source}}</bdi> &middot; {{c.day(article.published_date)}}</span>
          </li>
        </ul>
        <div class="alert alert-warning" role="alert"
             ng-if="!c.isEmpty('news') &amp;&amp; c.unrendered('news')">
          <span class="icon-warning-triangle" aria-hidden="true">&nbsp;</span>
          <span>{{c.unrendered('news')}} of {{data.news.rows.length}} news articles could not be displayed.
            Reload the page; if it recurs, report it with this page address.</span>
        </div>
          <p class="text-muted bst-collection-caption" ng-if="data.news.truncated">
            <span>Showing {{c.count(data.news.rows.length)}} of {{c.count(data.news.total)}}, the {{c.count(data.news.limit)}} most recent.</span>
            <a ng-if="::data.fullListPage"
               ng-href="?id={{::data.fullListPage}}&amp;table=x_bst_startuptrk_newsarticle&amp;startup={{::data.startup.sys_id}}">Open the full list</a>
          </p>
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
    max-width: $navbar-height;
    width: auto;
    height: auto;
}

.bst-company .media-heading {
    overflow-wrap: break-word;
}

/* Same float containment as the investor overview, for the same reason: four of
   these items carry a .pull-right, and Employees, Founded and Headquarters can
   each arrive wide enough to wrap. */
.bst-company .list-group-item {
    display: flow-root;
    overflow-wrap: break-word;
}

.bst-company .label {
    margin-right: $padding-base-vertical;
}

.bst-company .table-responsive {
    margin-bottom: 0;
}

.bst-company .sr-only {
    position: absolute;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
}

.bst-company .list-group-item {
    unicode-bidi: isolate;
}

.bst-company .media-heading,
.bst-company .list-group-item-heading {
    line-height: normal;
}

.bst-company .bst-company-state-heading {
    margin-bottom: $grid-gutter-width;
}

.bst-company .bst-upsell {
    margin-bottom: $grid-gutter-width;
}

.bst-company .bst-upsell .panel-title {
    margin-bottom: $padding-base-vertical;
}

.bst-company .bst-upsell .bst-upsell-fields {
    margin-top: $padding-base-vertical;
    margin-bottom: $padding-base-vertical;
}

.bst-company .bst-upsell .bst-upsell-fields .label {
    margin-right: $padding-base-vertical;
    white-space: normal;
    overflow-wrap: anywhere;
}


@media (prefers-reduced-motion: reduce) {
    .bst-company .progress-bar {
        animation: none;
    }
}

@media (forced-colors: active) {
    .bst-company .label {
        border-style: solid;
    }
}

.bst-company [tabindex="-1"]:focus,
.bst-company[tabindex="-1"]:focus {
    outline: $border-radius-base solid $brand-primary;
    outline-offset: $border-radius-small;
}
```

Four of those rules exist for a reason that is not visible in the declaration:

- **`.list-group-item { unicode-bidi: isolate }` and `.media-heading, .list-group-item-heading { line-height: normal }`** are this template's share of [the cleaning rules these widgets depend on](#the-cleaning-rules-these-widgets-depend-on) — the first stops a right-to-left value reordering the product wording beside it in the Overview list, the second lets a line box grow to a grapheme carrying stacked combining marks instead of clipping it into the text below.
- **The reduced-motion guard** exists because the busy bar now has a rendered width. Before it did, the striped animation ran on a zero-width element and no caller could perceive it, so the omission was latent rather than real; giving the bar its width is what turns the omission into a defect, and the two changes therefore belong together.
- **The `.bst-upsell` rules** are [rule 16](#rules-that-bind-all-eight): this widget embeds `bst-premium-upsell` with `$sp.getWidget()`, which creates no instance, so the partial's own CSS field may never be compiled into this page and these declarations would otherwise have no source at all. They are exactly the partial's rules that nothing else on this page supplies — measured against the partial rendered on its own, not inferred — and the chip rule is the partial's own selector with this widget's root prepended, so the cascade resolves on specificity rather than on sheet order.
- **The forced-colours chip border** is [rule 12](#rules-that-bind-all-eight). This template renders twelve `.label` chips, including the `Premium` marker on four People rows and on the Funding pane's Amount and Valuation cells.

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
3. Serialise the investor into a local, `var investor = builder.serialize(record, ['name', 'type', 'focus_areas', 'website', 'aum_usd', 'portfolio_count']);`, where `record` is the `GlideRecordSecure` of item 2. `portfolio_count` is a stored, read-only integer maintained by `InvestorPortfolioService`; read it, never recompute it in the widget.
4. Split `focus_areas` on the comma into a local array for the `.label` chips — `var focusAreas = String(investor.focus_areas || '').split(',')`, each entry trimmed, empty entries dropped. It is a multi-choice column and arrives as a comma-separated string. **When `focus_areas` is absent or empty the array is empty**, never `undefined`, so the template's `ng-repeat` renders nothing rather than failing.
5. Build the **rounds led** set into a local `led`: `GlideRecordSecure` on `x_bst_startuptrk_fundinground` with `addQuery('lead_investor', sysId)`, ordered by `round_date` descending then `sys_id`, `setLimit(roundsCap)`, each row serialised with `var roundFields = ['startup', 'round_type', 'amount_usd', 'round_date', 'valuation_usd', 'source_url'];`. Take its exact total into a local `ledTotal` from `builder.countWith('x_bst_startuptrk_fundinground', function (q) { q.addQuery('lead_investor', sysId); })`. `roundsCap` and `roundFields` are declared once, before item 5, and are the same values items 6 and 7 use.
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

// (d) keep the total. It is published onto `data` by item 7's block below,
//     together with the five other window members, so that all six names are
//     assigned in one place under one scheme.
var participatedCount = participatedTotal;
```

**Every window member is published once, from item 7, under one naming scheme.** An earlier revision assigned `data.roundsLimit`, `data.participatedTotal` and `data.participatedTruncated` here *as well as* the six `roundsLed*` and `roundsParticipated*` members below, which is two schemes for the same three concepts and three names the [Data contract](#data-contract) does not declare. That is precisely the state the contract's own preamble warns about, and it had already cost a caption: the Rounds-led note was written against `data.ledTruncated` and `data.ledTotal`, which no step ever assigned, so `ng-if` evaluated `undefined`, the `<p>` was never inserted, and an investor whose led-rounds set was capped rendered a capped table **stating no total at all** — a wrong figure rather than a short one, which is the failure the window members exist to prevent. Its structurally identical sibling twenty-seven lines later worked, which is what makes the asymmetry an oversight rather than a design. The rule that prevents a recurrence is mechanical: **the only place a member is assigned onto `data` is item 7's publication block, and the only names that appear there are the names the contract table declares.** Check it by searching the template for every `data.` expression and confirming each one appears in that table.

**The join read must carry the limit, not just the round read.** An investor that has participated in three thousand rounds would otherwise produce a three-thousand-element identifier array and an `IN` condition of that length — the read of the rounds is bounded by the array, so an unbounded array is an unbounded read wearing a bound. Capping the join read caps everything downstream of it. `participatedCount` is what tells the reader the list is a window onto something larger, and it comes from a `COUNT` aggregate rather than from the array's length. Item 7 publishes it as `data.roundsParticipatedTotal`.

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

   **Then publish every set and every total the template reads. Nothing above this line is visible to the client until it is assigned onto `data`:**

```javascript
data.investor            = investor;              // the serialised record of item 3
data.focusAreas          = focusAreas;            // the split array of item 4
data.roundsLed           = led;                   // item 5
data.roundsLedTotal      = ledTotal;              // item 5's COUNT aggregate
data.roundsLedLimit      = roundsCap;
data.roundsLedTruncated  = ledTotal > led.length;
data.roundsParticipated          = participated;  // item 6(c)
data.roundsParticipatedTotal     = participatedCount;   // item 6(b)
data.roundsParticipatedLimit     = roundsCap;
data.roundsParticipatedTruncated = participatedCount > participated.length;
data.portfolio           = portfolio;             // item 7
```

   **This block is the only place any of those members is assigned.** Item 6(d) establishes the window and publishes nothing, so each fact reaches the client under exactly one name — the names the template binds and the Data Contract table below documents. Two names for one fact is how a caption comes to read a member nobody publishes, which renders as no caption at all.

   **The two rounds tables carry the same shape the company profile's child collections carry** — a bounded set, its exact total, the limit that bounded it, and a truncation flag — and for the same reason: a table that renders fifty of three thousand rounds without stating the total answers the reader's question wrongly rather than partially. The **limit is one member, shared by both tables**, because item 6(a)'s single `roundsCap` bounds both reads; two members carrying the same value would be two places for one figure to disagree. Each table keeps its own total and its own truncation flag, because those differ. `data.portfolio` is deliberately **not** given a total of its own: the authoritative figure is `data.investor.portfolio_count`, and `data.portfolioTruncated` with `data.portfolioLimit` says how much of it this page read.

8. Compute the gate flags by absence of key: `aum_usd` on `data.investor`, and `amount_usd` and `valuation_usd` across `data.roundsLed` and `data.roundsParticipated`. Set `data.gatedAny` accordingly — the same spelling the results and company widgets publish, so one flag has one name across all three. **It is read by item 9 and by the template's premium note**, so it is a published member rather than a local.
9. When `data.gatedAny` is true, embed the partial:

```javascript
data.upsell = $sp.getWidget('bst-premium-upsell', {
    context: 'investor',
    gated_fields: 'aum_usd,amount_usd,valuation_usd',
    upsell_page: options.upsell_page,
    heading: 'Premium investor data is hidden'
});
```

#### Data contract

**Every member below is assigned onto `data` by the server script named in its row, and read by the consumer named in its row. There is no third source and no other member**: a template expression naming anything absent from this table renders nothing at best and raises a runtime expression error at worst, and a member published with no consumer is a dead output. `data.error` is not in any widget's table — it is set on the client by the shared `c.load()` helper of [Error and empty behaviour](#error-and-empty-behaviour) and by nothing on the server. A widget whose own server script catches a failure and reports it publishes that message as **`data.serverError`**, which **is** in that widget's table, and which `c.load()` never touches; the error panel renders `c.errorText()`, which answers either of the two.

| Member | Type | Published by | Consumed by |
| --- | --- | --- | --- |
| `authorised` | True/False | server item 1 | Template — the not-entitled alert and the `ng-if` on the profile |
| `notFound` | True/False | server item 2 | Template — the not-found alert |
| `investor` | Serialised record | server item 7's publication block | Template — the overview panel, including `portfolio_count`; controller item 3's record watch |
| `focusAreas` | Array of string | server item 7's publication block | Template — the focus-area `.label` chips |
| `roundsLed` | Array of serialised rounds | server item 7's publication block | Template — the Rounds led table; controller `c.hasLed()` |
| `ledTotal` | Integer | server item 7's publication block | Template — the Rounds led caption |
| `ledTruncated` | True/False | server item 7's publication block | Template — whether the Rounds led caption renders |
| `roundsParticipated` | Array of serialised rounds | server item 7's publication block | Template — the Rounds participated table; controller `c.hasParticipated()` |
| `participatedTotal` | Integer | server item 7's publication block | Template — the Rounds participated caption |
| `participatedTruncated` | True/False | server item 7's publication block | Template — whether the Rounds participated caption renders |
| `roundsLimit` | Integer | server item 7's publication block | Template — the ceiling stated in **both** rounds captions; one member, because one bound governs both reads |
| `portfolio` | Array of serialised startups | server item 7's publication block | Template — the Portfolio table; controller `c.hasPortfolio()` |
| `portfolioTruncated` | True/False | server item 7 | Template — whether the portfolio cap note renders |
| `portfolioLimit` | Integer | server item 7 | Template — that note's figure |
| `gatedAny` | True/False | server item 8 | Template — the premium note beside the upsell; server item 9's embed decision |
| `upsell` | Widget model | server item 9 | Template — `<sp-widget widget="data.upsell">` |

#### Client controller

1. Implement `c.load()` and `c.retry()` exactly as [Error and empty behaviour](#error-and-empty-behaviour) specifies. Every server call below goes through `c.load()`.
2. Expose `c.hasParticipated()`, `c.hasLed()` and `c.hasPortfolio()`, each `true` when the matching array holds at least one entry, so an empty collection renders its own empty state rather than an empty `<tbody>`. **`focusAreas` is the fourth collection on this widget and it needs no helper**, because it is rendered inline rather than in a table: its empty state is the `ng-if="!data.focusAreas.length"` beside its repeat, which renders a muted `Not recorded` in the same cell the chips would have occupied. Before it existed that cell rendered blank at full row height, which reads as a deliberately empty value rather than as an absent one — and the rule that every collection states its own emptiness applies to a cell as much as to a table.
3. **Watch the record only when there is a record to watch, and release the watch on `$destroy`.** `data.investor` is absent on the unauthorised path of server-script item 1 and on the not-found path of item 2, so an unguarded `c.data.investor.sys_id` raises a `TypeError` on both. The shape is identical to the company profile's, with the investor table and the investor object:

```javascript
var ID32 = /^[0-9a-f]{32}$/;
var watchScope = null;
var watchedId = '';

// spUtil.recordWatch() returns a PROMISE, not an unsubscribe handle: there is nothing
// on its result to call. The supported release is scope destruction, so the watch is
// registered against a CHILD scope this controller owns and destroying that child is
// what releases it. Registering on every load would accumulate one live subscription
// per refresh, which is what re-subscribing with a promise as a handle actually did.
function releaseWatch() {
    if (watchScope) {
        watchScope.$destroy();
        watchScope = null;
    }
    watchedId = '';
}

function startWatch() {
    var record = c.data && c.data.investor;
    var id = record ? '' + record.sys_id : '';
    if (!id || !ID32.test(id)) {
        releaseWatch();
        return;
    }
    if (id === watchedId) {
        return;                       // already watching exactly this record
    }
    releaseWatch();                   // a different record: drop the old subscription
    watchScope = $scope.$new();
    watchedId = id;
    spUtil.recordWatch(watchScope, 'x_bst_startuptrk_investor', 'sys_id=' + id);
}

startWatch();
$scope.$on('$destroy', releaseWatch);
```

   A recalculated `portfolio_count` then appears without a reload when the record is on the page, and nothing is subscribed when it is not. `startWatch()` is called at controller initialisation and again from the promise callback of every `c.load()`, and it is **idempotent**: a load that yields the same `sys_id` returns without touching the subscription, and only a change of record identity destroys the child scope and registers again. The rule is stated once under [Every listener a controller registers is released on `$destroy`](#every-listener-a-controller-registers-is-released-on-destroy).
4. Declare `c.busy` and `c.statusText()` per [Busy, status and focus behaviour](#busy-status-and-focus-behaviour), and also declare `c.focusDestination()` and `c.onButtonKey($event)` per that same section, `c.indeterminate()` for the striped bar, and `c.money()`, `c.day()` and `c.count()` per [The display contract](#the-display-contract). **Six states, tested in this order, and every one of them answered:**

   | # | Condition | Returns | Who announces this state instead |
   | --- | --- | --- | --- |
   | 1 | `c.busy` | `Loading` | — |
   | 2 | `!c.data.authorised` | **the empty string** | the not-entitled `.alert-warning`, which carries `role="alert"` |
   | 3 | `c.data.error` | **the empty string** | the failure `.alert-danger`, which carries `role="alert"` and owns **Retry** |
   | 4 | `c.data.notFound` | **the empty string** | the not-found `.alert-warning`, which carries `role="alert"` |
   | 5 | no portfolio company and no round in either table | `No portfolio company and no funding round are recorded for this investor.` | this region |
   | 6 | otherwise | `{{c.data.investor.name}} loaded. {{c.data.investor.portfolio_count}} portfolio companies, {{c.data.roundsLedTotal}} rounds led, {{c.data.roundsParticipatedTotal}} rounds joined.` | this region |

   Rows 2, 3 and 4 return nothing because a visible element with a live-region role already owns each of those states; without them the order fell through to row 5 and announced a sentence about recorded rounds on a screen showing no record at all.

   **Row 6 states the totals, not the rendered array lengths.** With the caps in force, `roundsLed.length` and `roundsParticipated.length` are both the page limit, so the old wording announced "50 rounds led, 50 rounds joined" for an investor with 88 and 61 — telling a screen-reader caller the size of the window and calling it the size of the record. `portfolio_count` is the authoritative distinct-startup count of AAP §0.8.5 and is already on the record. Each table's own caption then states how much of its collection is rendered, which is the division the company profile uses for the same reason.
5. **Expose `c.stateHeading()`**, returning `Investor profile` when the caller is not entitled or the load failed, `Investor not found` on the not-found path, and the empty string otherwise. The success path's `<h1>` is the investor name inside the panel heading, and that element sits inside the `ng-if` all three of those paths exclude — so each of them rendered **no heading at all**. Returning the empty string on the success path is what keeps the two sources mutually exclusive, so the page always renders exactly one `<h1>` as [rule 9](#rules-that-bind-all-eight) requires. The not-found wording differs because that state answers a specific request; the other two name the page and leave the reason to the alert.
6. Recompute nothing. `portfolio_count` is read, not derived, in the client.
7. Expose `c.unrendered(collection)` exactly as [rendered rows and model rows must agree](#rendered-rows-and-model-rows-must-agree) specifies, and inject `$element` into the controller so it can count the rendered rows of its own widget. The portfolio repeat carries `data-bst-row="portfolio"`, which is what the helper counts, and it is the **only** collection on this widget that is reconciled: it is the one assembled from two traversal paths, so it is the one whose key uniqueness rests on application logic rather than on a database constraint. The two rounds tables and the focus-area chips are single-path collections and are not reconciled.

**The three regions render together, unconditionally.** The overview panel, the portfolio panel and the two rounds tables are all present on the page at once, laid out by the widget's own two columns. There is **no** show-or-hide toggle and **no** section state on this widget: the tab control is used only on the company profile, and a caller reads this profile top to bottom.

#### HTML template

```html
<div class="bst-investor" tabindex="-1" aria-busy="{{c.busy}}">
  <div class="sr-only" role="status" aria-live="polite" aria-atomic="true">{{c.statusText()}}</div>

  <h1 class="bst-investor-state-heading" tabindex="-1" ng-if="c.stateHeading()">{{c.stateHeading()}}</h1>

  <div class="alert alert-warning" role="alert" ng-if="!data.authorised">
    <span>Your account holds no Boston Startup Tracker role.</span>
    <a class="btn btn-default" ng-href="?id=bst_home">Back to search</a>
  </div>

  <div class="alert alert-warning" role="alert" ng-if="data.notFound">
    <span>That investor could not be found.</span>
    <a class="btn btn-default" ng-keydown="c.onButtonKey($event)"
       ng-href="?id=bst_home">Back to search</a>
  </div>

  <div class="alert alert-danger" role="alert" ng-if="c.errorText()">
    <span class="icon-cross-circle" aria-hidden="true">&nbsp;</span>
    <span>{{c.errorText()}}</span>
    <button type="button" class="btn btn-default" ng-click="c.retry()">Retry</button>
  </div>

  <div class="progress" ng-if="c.busy">
    <div class="progress-bar progress-bar-striped active" role="progressbar"
         ng-style="c.indeterminate()"
         aria-label="Loading investor profile" aria-valuemin="0" aria-valuemax="100"
         aria-valuetext="Loading"></div>
  </div>

  <div class="row" ng-if="data.authorised &amp;&amp; !c.busy &amp;&amp; !data.notFound &amp;&amp; !c.errorText()">
    <div class="col-md-4 col-lg-4">
      <div class="panel panel-default">
        <div class="panel-heading"><h1 class="panel-title" dir="auto" tabindex="-1">{{::data.investor.name}}</h1></div>
        <ul class="list-group">
          <li class="list-group-item">
            <div class="row">
              <div class="col-md-5 col-lg-5">Type</div>
              <div class="col-md-7 col-lg-7 text-right">
                <span class="label label-primary" ng-if="::data.investor.type">{{::data.investor.type}}</span>
              </div>
            </div>
          </li>
          <li class="list-group-item">
            <div class="row">
              <div class="col-md-5 col-lg-5">Focus areas</div>
              <div class="col-md-7 col-lg-7 text-right">
                <span class="label label-default" ng-repeat="area in ::data.focusAreas track by $index"
                      dir="auto">{{::area}}</span>
                <span class="text-muted" ng-if="!data.focusAreas.length">Not recorded</span>
              </div>
            </div>
          </li>
          <li class="list-group-item">
            <div class="row">
              <div class="col-md-5 col-lg-5">Portfolio companies</div>
              <div class="col-md-7 col-lg-7 text-right">{{c.count(data.investor.portfolio_count)}}</div>
            </div>
          </li>
          <li class="list-group-item" ng-if="data.investor.aum_usd !== undefined">
            <div class="row">
              <div class="col-md-5 col-lg-5">Assets under management</div>
              <div class="col-md-7 col-lg-7 text-right">
                <bdi ng-if="data.investor.aum_usd !== null">{{c.money(data.investor.aum_usd)}}</bdi>
                <span class="text-muted" ng-if="data.investor.aum_usd === null">Not recorded</span>
              </div>
            </div>
          </li>
          <li class="list-group-item" ng-if="data.investor.aum_usd === undefined">
            <div class="row">
              <div class="col-md-5 col-lg-5">Assets under management</div>
              <div class="col-md-7 col-lg-7 text-right"><span class="label label-info">Premium</span></div>
            </div>
          </li>
          <li class="list-group-item">
            <div class="row">
              <div class="col-md-5 col-lg-5">Website</div>
              <div class="col-md-7 col-lg-7 text-right">
                <a ng-href="{{::data.investor.website}}"
                   ng-if="::data.investor.website">Visit the investor website</a>
                <span class="text-muted" ng-if="::!data.investor.website">Not recorded</span>
              </div>
            </div>
          </li>
        </ul>
      </div>
      <p class="text-muted" ng-if="data.gatedAny">
        Some figures on this profile are premium data and are shown as
        <span class="label label-info">Premium</span>.
      </p>
      <sp-widget widget="data.upsell" ng-if="data.upsell"></sp-widget>
    </div>

    <div class="col-md-8 col-lg-8">
      <div class="panel panel-default">
        <div class="panel-heading"><h2 class="panel-title">Portfolio</h2></div>
        <div class="panel-body">
          <div class="alert alert-info" ng-if="!c.hasPortfolio()">
            <span>No portfolio company is recorded for this investor.</span>
          </div>
          <div class="table-responsive" tabindex="0" ng-if="c.hasPortfolio()">
            <table class="table table-striped table-hover">
              <caption class="sr-only">Portfolio companies reached through the rounds on this page, one row per company</caption>
              <thead><tr><th scope="col">Company</th><th scope="col">Industry</th><th scope="col">Headquarters</th><th scope="col">Stage</th><th scope="col">Total funding</th></tr></thead>
              <tbody>
                <tr data-bst-row="portfolio" ng-repeat="startup in data.portfolio track by startup.sys_id">
                  <th scope="row"><a ng-href="?id={{::options.company_page}}&amp;sys_id={{::startup.sys_id}}">{{::startup.name}}</a></th>
                  <td><span class="label label-default" ng-if="::startup.industry">{{::startup.industry}}</span></td>
                  <td>{{::startup.headquarters_location}}</td>
                  <td><span class="label label-primary" ng-if="::startup.funding_stage">{{::startup.funding_stage}}</span></td>
                  <td ng-if="startup.total_funding_usd !== undefined">{{c.money(startup.total_funding_usd)}}</td>
                  <td ng-if="startup.total_funding_usd === undefined"><span class="label label-info">Premium</span></td>
                </tr>
              </tbody>
            </table>
          </div>
          <p class="text-muted" ng-if="data.portfolioTruncated">
            Showing the first {{c.count(data.portfolioLimit)}} of {{c.count(data.investor.portfolio_count)}} portfolio companies. Open the record in the platform list to see them all.
          </p>
          <div class="alert alert-warning" role="alert"
               ng-if="c.hasPortfolio() &amp;&amp; c.unrendered('portfolio')">
            <span class="icon-warning-triangle" aria-hidden="true">&nbsp;</span>
            <span>{{c.unrendered('portfolio')}} of {{data.portfolio.length}} rows could not be displayed.
              Reload the page; if it recurs, report it with this page address.</span>
          </div>
        </div>
      </div>

      <div class="panel panel-default">
        <div class="panel-heading"><h2 class="panel-title">Rounds led</h2></div>
        <div class="panel-body">
          <div class="alert alert-info" ng-if="!c.hasLed()"><span>This investor has led no recorded round.</span></div>
          <div class="table-responsive" tabindex="0" ng-if="c.hasLed()">
            <table class="table table-striped table-hover">
              <caption class="sr-only">Funding rounds this investor led, one row per round</caption>
              <thead><tr><th scope="col">Company</th><th scope="col">Date</th><th scope="col">Round</th><th scope="col">Amount</th><th scope="col">Valuation</th></tr></thead>
              <tbody>
                <tr ng-repeat="round in data.roundsLed track by round.sys_id">
                  <th scope="row"><a dir="auto" ng-href="?id={{::options.company_page}}&amp;sys_id={{::round.startup.value}}">{{::round.startup.display_value}}</a></th>
                  <td>{{c.day(round.round_date)}}</td>
                  <td><span class="label label-primary" ng-if="::round.round_type">{{::round.round_type}}</span></td>
                  <td ng-if="round.amount_usd !== undefined">{{c.money(round.amount_usd)}}</td>
                  <td ng-if="round.amount_usd === undefined"><span class="label label-info">Premium</span></td>
                  <td ng-if="round.valuation_usd !== undefined">{{c.money(round.valuation_usd)}}</td>
                  <td ng-if="round.valuation_usd === undefined"><span class="label label-info">Premium</span></td>
                </tr>
              </tbody>
            </table>
          </div>
          <p class="text-muted" ng-if="data.roundsLedTruncated">
            Showing the first {{c.count(data.roundsLedLimit)}} of {{c.count(data.roundsLedTotal)}} rounds this investor led. Open the record in the platform list to see them all.
          </p>
        </div>
      </div>

      <div class="panel panel-default">
        <div class="panel-heading"><h2 class="panel-title">Rounds participated in</h2></div>
        <div class="panel-body">
          <div class="alert alert-info" ng-if="!c.hasParticipated()"><span>This investor has participated in no recorded round.</span></div>
          <div class="table-responsive" tabindex="0" ng-if="c.hasParticipated()">
            <table class="table table-striped table-hover">
              <caption class="sr-only">Funding rounds this investor participated in, one row per round</caption>
              <thead><tr><th scope="col">Company</th><th scope="col">Date</th><th scope="col">Round</th><th scope="col">Amount</th><th scope="col">Valuation</th></tr></thead>
              <tbody>
                <tr ng-repeat="round in data.roundsParticipated track by round.sys_id">
                  <th scope="row"><a dir="auto" ng-href="?id={{::options.company_page}}&amp;sys_id={{::round.startup.value}}">{{::round.startup.display_value}}</a></th>
                  <td>{{c.day(round.round_date)}}</td>
                  <td><span class="label label-primary" ng-if="::round.round_type">{{::round.round_type}}</span></td>
                  <td ng-if="round.amount_usd !== undefined">{{c.money(round.amount_usd)}}</td>
                  <td ng-if="round.amount_usd === undefined"><span class="label label-info">Premium</span></td>
                  <td ng-if="round.valuation_usd !== undefined">{{c.money(round.valuation_usd)}}</td>
                  <td ng-if="round.valuation_usd === undefined"><span class="label label-info">Premium</span></td>
                </tr>
              </tbody>
            </table>
          </div>
          <p class="text-muted" ng-if="data.roundsParticipatedTruncated">
            Showing the first {{c.count(data.roundsParticipatedLimit)}} of {{c.count(data.roundsParticipatedTotal)}} rounds this investor participated in. Open the record in the platform list to see them all.
          </p>
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

/* flow-root establishes a block formatting context, which is what makes a
   wrapped .pull-right float contribute to this item's height. Without it the
   float is out of flow, the item keeps the height of its label line alone, and
   the float's second line hangs below the item where the NEXT item's opaque
   background paints over it - see Float containment in Overflow guards at the
   floor. overflow-wrap is a separate guard, for an unbreakable single word. */
.bst-investor .list-group-item {
    display: flow-root;
    overflow-wrap: break-word;
    unicode-bidi: isolate;
}

/* inline-block, not Bootstrap's inline, so the chip run can WRAP. white-space:
   nowrap on .label forbids a break inside a chip; between chips there is no break
   opportunity at all, because ng-repeat clones its element with no whitespace text
   node between the clones. A run of inline boxes with no break opportunity has
   min-content == max-content, and a float's shrink-to-fit is floored at min-content,
   so the float is forced to its full 342px inside a 291px column and overhangs off
   the LEFT of the window - where a left-to-right document generates no scrollbar and
   the content cannot be reached. An atomic inline-level box creates the break
   opportunity, min-content collapses to the widest single chip, and the run wraps.
   text-align keeps the wrapped run against the right edge, where the float put it;
   it has no effect on a single short value, whose float shrink-wraps to its content. */
.bst-investor .list-group-item .pull-right {
    text-align: right;
}

.bst-investor .list-group-item .label {
    display: inline-block;
    margin-left: $padding-base-vertical;
    white-space: normal;
    overflow-wrap: break-word;
}

.bst-investor h1.panel-title {
    line-height: normal;
}

.bst-investor .bst-investor-state-heading {
    margin-bottom: $grid-gutter-width;
}

.bst-investor .table-responsive {
    margin-bottom: 0;
}

.bst-investor .sr-only {
    position: absolute;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
}

.bst-investor .bst-upsell {
    margin-bottom: $grid-gutter-width;
}

.bst-investor .bst-upsell .panel-title {
    margin-bottom: $padding-base-vertical;
}

.bst-investor .bst-upsell .bst-upsell-fields {
    margin-top: $padding-base-vertical;
    margin-bottom: $padding-base-vertical;
}

.bst-investor .bst-upsell .bst-upsell-fields .label {
    margin-right: $padding-base-vertical;
    white-space: normal;
    overflow-wrap: anywhere;
}


@media (prefers-reduced-motion: reduce) {
    .bst-investor .progress-bar {
        animation: none;
    }
}

@media (forced-colors: active) {
    .bst-investor .label {
        border-style: solid;
    }
}

.bst-investor [tabindex="-1"]:focus,
.bst-investor[tabindex="-1"]:focus {
    outline: $border-radius-base solid $brand-primary;
    outline-offset: $border-radius-small;
}
```

**The overview list is laid out on the grid, and the reason is the one defect in this widget that made content genuinely unreachable.** Each of its rows used a Bootstrap `.pull-right` float for its value, and a float is removed from flow: `.list-group-item` has `overflow: visible` and no clearfix, so the row never grew to contain it and the next row — which has an opaque background — painted straight over the top. The focus-area chips are the worst case because they are a repeat and wrap to several lines: measured at 1366 the float overflowed its row by **29px** with two of four chips completely invisible and the other two about 70% hidden, and at 1024 — the declared floor — by **69px** with three of four completely invisible. Worse, a float wider than its container escapes to the **left**: the chip span measured 341.75px inside a 291.33px row at x = **−22.42**, running off the left edge of the viewport. Browsers do not extend `scrollWidth` for left-side overflow, so **no scrollbar appeared and the content could not be reached by any means**. The same float bisected the premium `aum_usd` figure and inflated the neighbouring row's height.

Two of the three obvious remedies are unavailable here. A clearfix alone contains the float vertically but does nothing about a float wider than its row, so the left-side escape survives it. Capping the float with `max-width: 60%` fixes both — and is forbidden, because [zero hard-coded values](#zero-hard-coded-values) admits no percentage literal in widget CSS. The remaining answer is the one the same rule set prescribes anyway: **[layout through system primitives](#layout-through-system-primitives-only)**. A `.row` holding `.col-md-5` and `.col-md-7` gives the label and the value real columns that total twelve, carries Bootstrap's own clearfix so the row always grows to its tallest cell, and cannot overflow because a grid column is width-constrained by construction. The value keeps its right alignment through the `.text-right` utility rather than through a float. **No literal of any kind is introduced**, and the `.row`'s negative margins land exactly in the `.list-group-item`'s own 15px horizontal padding, so the row neither overflows its item nor shifts the content's left edge.

Four of the CSS rules above also deserve a word:

- **`unicode-bidi: isolate` on `.list-group-item` and `line-height: normal` on `h1.panel-title`** are this widget's share of [the cleaning rules these widgets depend on](#the-cleaning-rules-these-widgets-depend-on). The focus areas are Multi-choice values and the investor name is free text, so either can arrive right-to-left or carrying stacked combining marks.
- **The reduced-motion guard** pairs with the busy bar's new rendered width, exactly as on the two sibling widgets: the width is what makes the striped animation perceptible, and therefore what turns the missing guard from a latent omission into a real one.
- **The forced-colours chip border** is [rule 12](#rules-that-bind-all-eight). This widget renders the `Premium` marker in three places — the `aum_usd` row and the Amount and Valuation columns of both rounds tables — plus the type chip, the focus-area chips and every stage chip.
- **The `.bst-upsell` rules** are [rule 16](#rules-that-bind-all-eight): this widget embeds `bst-premium-upsell` with `$sp.getWidget()`, which creates no instance, so the partial's own CSS field may never be compiled into this page and these declarations would otherwise have no source at all. They are exactly the partial's rules that nothing else on this page supplies — measured against the partial rendered on its own, not inferred — and the chip rule is the partial's own selector with this widget's root prepended, so the cascade resolves on specificity rather than on sheet order.
- **`white-space: normal` and `overflow-wrap: break-word` on the chips** are [rule 13](#rules-that-bind-all-eight), and they are what stops the grid from being defeated from the inside. Bootstrap gives `.label` a `white-space: nowrap`, which is right for a one-word status marker and wrong for a Multi-choice value: it removes every soft-wrap opportunity, so the chip becomes a single unbreakable inline box that is intrinsically wider than the column it sits in. The column still cannot overflow — but its *content* can, and it escapes to the **right** into the neighbouring `.col-md-8`, which is a later sibling and therefore paints over it. Measured on a focus area reading `Financial technology and payments infrastructure`, the chip ran **58.73px** past its cell at 1366 and **97.63px** at 1024, losing **17.7%** and **33.5%** of its own width to over-painting and cutting the label mid-word. Restoring `normal` gives the text its break opportunities back and the chip then wraps inside the cell; `overflow-wrap: break-word` covers the remaining case of a single token longer than the cell. Both are behaviour keywords, so neither introduces a literal.

  This is a milder failure than the float it sits beside — it escapes right rather than off the viewport edge, and the chip's centre stays clickable — but it is the same underlying mistake, which is **content that cannot be broken inside a container that cannot grow**. It is worth naming because the grid fix alone does not reach it: a grid column constrains its own box, not the intrinsic width of what it contains.

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
2. Produce every figure with `RestResponseBuilder.countWith(table, applyConditions)`, which applies the `hasAnyAppRole()` role gate and then takes one aggregate `COUNT`. **Do not write an aggregate query of your own.** The gate is the whole point: `countWith()` delegates to `countState()`, which first calls `hasAnyAppRole()` — three `gs.hasRole()` tests against the three application roles — and only then takes the aggregate, answering `0` when the caller holds none of the three. It is a **role** test rather than a `GlideRecordSecure.canRead()` probe, because `canRead()` answers for the record a secured object is positioned on and is therefore not a table-level right; the reasoning is in [`../access-control.md`](../access-control.md). A bare `GlideAggregate` in a widget skips that gate and reports the size of a set the caller may not read; the rule is stated in [`../access-control.md`](../access-control.md).

   **`countWith()` returns `0` on a denial and does not distinguish it from a genuine zero.** That is safe on this route only because the dashboard is behind the same no-role notice as every other widget: `data.authorised` is resolved first, and no figure is rendered when it is false. Where a widget must tell the two apart — as the results widget does — use `countState()` and read its `denied` member instead. A REST operation must always use `countState()` with `rejectDeniedCount()`, never `countWith()`.

> **An aggregate may produce a caller-facing value only when the value depends on no field the caller can be denied, and the table carries no record-level access control.** A row count satisfies both: it reads no field, and all seven entity tables grant table-level read to all three application roles with no record-level rule, so every role sees the same rows. A sum, an average, a maximum or a minimum over a **premium-gated** column satisfies neither, because the aggregate would compute over values the field-level access control exists to withhold.

**Route every count through `countWith()`; never write the aggregate inline.** The gate, the exactness and this rule then have one home for all eight widgets and all thirty-one REST operations. [`../access-control.md`](../access-control.md) and [`../api-reference.md`](../api-reference.md) state the same rule, and [`../data-model.md`](../data-model.md) states the no-record-level-access-control invariant it rests on — **if a record-level rule is ever added to one of these tables, every count in this guide becomes wrong and must be replaced.**

**The query cost of this widget is one aggregate per panel**, so five aggregates with both optional panels shown and three with neither. No panel iterates a table, and the figures are exact rather than floors.
3. Apply the inclusion criteria to the startup figure through the shared service, so the dashboard and the search results agree:

```javascript
var builder = new RestResponseBuilder();
var search = new StartupSearchService();
var plan = search.buildPlan(null, search.appliesInclusion());

// Every figure in this widget comes from an aggregate, and this is the widget's
// only server round trip: an unhandled failure would publish an empty kpis array
// and the row would render as nothing with no error and nothing to retry. The
// message goes in data.serverError, which the shared c.load() helper never touches,
// so a failing Retry keeps the panel that carries the Retry control.
data.kpis = [];
data.serverError = '';
try {
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
} catch (aggregateFailure) {
    data.kpis = [];
    data.serverError = 'Could not load the dashboard figures. Use Retry to try again.';
    gs.error('[bst-trends-kpi] KPI aggregate failed: ' + aggregateFailure);
}
```

4. Publish no currency figure. `total_funding_usd`, `amount_usd` and `valuation_usd` are **premium-gated**, and a `SUM` over a gated column is exactly the case the rule in step 2 forbids: the aggregate would compute over values the field-level access control exists to withhold from the base `user` role, and would then publish the result to that role as a dashboard figure. Field-level access control is not something a total can be laundered through. **No KPI panel in this widget reports a monetary total**, and none may be added.

#### Data contract

**Every member below is assigned onto `data` by the server script named in its row, and read by the consumer named in its row. There is no third source and no other member**: a template expression naming anything absent from this table renders nothing at best and raises a runtime expression error at worst, and a member published with no consumer is a dead output. `data.error` is not in any widget's table — it is set on the client by the shared `c.load()` helper of [Error and empty behaviour](#error-and-empty-behaviour) and by nothing on the server. A widget whose own server script catches a failure and reports it publishes that message as **`data.serverError`**, which **is** in that widget's table, and which `c.load()` never touches; the error panel renders `c.errorText()`, which answers either of the two.

| Member | Type | Published by | Consumed by |
| --- | --- | --- | --- |
| `authorised` | True/False | server item 1 | Template — the not-entitled alert and the `ng-if` on the panel row |
| `kpis` | Array of panel descriptors | the server script's `data.kpis.push()` calls | Template — the panel `ng-repeat`; controller `c.columns($index)` |
| `serverError` | String | the server script's `catch` block, empty on every successful run | Controller `c.errorText()` — and through that helper the error panel, its **Retry** control, and the `ng-if` on the panel row. No expression reads this member directly |

#### Client controller

1. Compute `c.columns($index)` as the Bootstrap column span for the panel at that position, from `c.data.kpis.length` and the index, using the table under [The KPI column spans](#the-kpi-column-spans). Choose only from `col-md-12`, `col-md-6`, `col-md-4` and `col-md-3`, and never a narrower class.
2. Expose `c.breaksAfter($index)`, true only at the index the same table names in its **Break after index** column — index `2` when there are five panels, and nothing otherwise. The template renders a `.clearfix` where it is true; the reason it is needed at all is under that table.
3. Expose `c.hasLink(kpi)` for the conditional `.btn.btn-link`.
4. Declare `c.busy` per [Busy, status and focus behaviour](#busy-status-and-focus-behaviour), and implement `c.load()` and `c.retry()` exactly as [Error and empty behaviour](#error-and-empty-behaviour) specifies. This widget issues no server call **after** its first render, but that first render *is* a server call and its five aggregates can fail, so it carries the error panel and a working **Retry**. It carries no status region, because it has no user-initiated action to announce.
5. Read no data and issue no server call after the first render **except** `c.retry()`. The KPI figures are computed once, in the server script; `c.retry()` re-runs that script through `c.load()` and is the only later call this widget makes.

##### The KPI column spans

The panel count is **3, 4 or 5** in any shipped configuration — three always, plus one for each of `show_jobs` and `show_news`. A single span applied to all of them cannot total twelve at every count, so the span is chosen **per position**:

| Panels | Spans by index, `0` first | Rows | Break after index |
| --- | --- | --- | --- |
| 1 | `col-md-12` | One row of 12 | — |
| 2 | `col-md-6`, `col-md-6` | One row of 12 | — |
| 3 | `col-md-4`, `col-md-4`, `col-md-4` | One row of 12 | — |
| 4 | `col-md-3`, `col-md-3`, `col-md-3`, `col-md-3` | One row of 12 | — |
| 5 | `col-md-4`, `col-md-4`, `col-md-4`, `col-md-6`, `col-md-6` | 12, then 12 | **`2`** |

`c.columns($index)` returns `col-md-12` at one panel, `col-md-6` at two, `col-md-4` at three, `col-md-3` at four, and — at five — `col-md-4` for indexes `0` to `2` and `col-md-6` for indexes `3` and `4`. **Every row totals exactly twelve columns.** Return `col-md-4` for any count the table does not cover, so an unexpected count still renders a defined layout rather than none.

**Twelve columns per row is necessary and not sufficient, and the five-panel case is where that bites.** The Bootstrap grid is float-based, and a float can only drop to the next line if there is room for it beside the floats already placed — which depends on their **heights**, not on their column arithmetic. The five panels are not the same height: `c.hasLink(kpi)` is true for the startups KPI alone, so that one panel carries a `.btn.btn-link` and measures **34px taller** than the other four. Float 3 therefore cannot clear float 0, and instead of starting a second row it wedges into the gap beside it — measured as a lone `col-md-6` **indented by 390px** at 1366 and 1920 and by 323px at 1024, with float 4 then orphaned below it. The result was three ragged rows where the arithmetic promised two, at every viewport.

`c.breaksAfter($index)` closes it, and the template renders a **Bootstrap clearfix** where it returns true:

```html
<div ng-repeat-start="kpi in data.kpis track by kpi.id" ng-class="c.columns($index)">
  … the panel …
</div>
<div ng-repeat-end ng-class="{ clearfix: c.breaksAfter($index) }"></div>
```

`.clearfix` clears the floats placed before it, so float 3 begins on a fresh line at the container's left edge whatever the heights above it. This is Bootstrap 3's own documented remedy for uneven float wrapping, it is a **stock utility class** rather than custom layout CSS, and it introduces no measured value — which matters, because the two alternatives both do. Equalising the panels with a `min-height` would write a pixel literal into widget CSS, and equal-height columns by flexbox would be custom layout on a raw `<div>`; [zero hard-coded values](#zero-hard-coded-values) forbids the first and [layout through system primitives](#layout-through-system-primitives-only) the second. Moving the `.btn-link` out of the panel body would work too, and was rejected because the link belongs with the figure it acts on.

`c.breaksAfter($index)` returns true only where the table's **Break after index** column names a value, so among the covered counts it is false for every count but five, and false at five for every index but `2`. A clearfix emitted anywhere else would break a row that was wrapping correctly.

The **fallback** count needs the same treatment, for the same reason. A count the table does not cover renders at `col-md-4`, three to a row, and three-to-a-row wraps by float exactly as the five-panel case does — so it inherits the same failure: measured at six panels, panels 3 and 4 wedged into the shelf beside the taller float at an indent of 390px and panel 5 was orphaned on a third row. The guide's own promise is that an uncovered count "still renders a defined layout rather than none", and three ragged rows is not a defined layout. `c.breaksAfter` therefore also returns true after every third panel when the count exceeds five, and never after the last one, where a break would add an empty row:

```javascript
c.breaksAfter = function (index) {
    var count = c.data.kpis.length;
    if (count === 5) { return index === 2; }
    if (count > 5) { return index % 3 === 2 && index < count - 1; }
    return false;
};
```

No shipped configuration reaches six — the count is three plus one for each of the two optional panels, so five is the maximum — and that is precisely why the branch is worth writing rather than reasoning away: it is the branch no acceptance test will exercise, and the one an operator meets first if a seventh KPI is ever added.

**Two details of that markup are deliberate.** The repeat is written as `ng-repeat-start` / `ng-repeat-end` because one iteration must emit **two siblings** — the column and the break that may follow it — and a plain `ng-repeat` repeats a single element and its descendants only. Putting the break inside the column would be useless, since a clearfix inside a float clears nothing for that float's siblings.

And the break is toggled with **`ng-class`, not `ng-if`**. `ng-if` on an `ng-repeat-end` element asks AngularJS to transclude the element that terminates the repeated range, which is a fragile interaction between two structural directives and the kind of thing that works until a version bump. `ng-class` avoids it completely: the element is always emitted, and it is either a clearfix or an empty in-flow block. An empty block of zero height between floated columns changes nothing — the floats are out of flow and it has no content to displace — so the inert case is genuinely inert, and the only behaviour that varies is the one the class supplies.

#### HTML template

```html
<div class="bst-kpi" tabindex="-1" aria-busy="{{c.busy}}">
  <h1 class="h2">{{::options.title}}</h1>

  <div class="alert alert-warning" role="alert" ng-if="!data.authorised">
    <span>Your account holds no Boston Startup Tracker role.</span>
  </div>

  <div class="alert alert-danger" role="alert" ng-if="c.errorText()">
    <span class="icon-cross-circle" aria-hidden="true">&nbsp;</span>
    <span>{{c.errorText()}}</span>
    <button type="button" class="btn btn-default" ng-click="c.retry()">Retry</button>
  </div>

  <div class="row" ng-if="data.authorised &amp;&amp; !c.errorText()">
    <div ng-repeat-start="kpi in data.kpis track by kpi.id" ng-class="c.columns($index)">
      <div class="panel panel-default bst-kpi-panel">
        <div class="panel-heading">
          <h2 class="panel-title">
            <span class="{{kpi.glyph}}" aria-hidden="true">&nbsp;</span>{{kpi.label}}
          </h2>
        </div>
        <div class="panel-body">
          <p class="bst-kpi-value h2">{{c.count(kpi.value)}}</p>
          <a class="btn btn-link" ng-if="c.hasLink(kpi)" ng-keydown="c.onButtonKey($event)"
             ng-href="{{kpi.link}}">Browse startups</a>
        </div>
      </div>
    </div>
    <div ng-repeat-end ng-class="{ clearfix: c.breaksAfter($index) }"></div>
  </div>
</div>
```

**The figure is a value, not a heading.** It is rendered in a `<p class="bst-kpi-value h2">`: the Bootstrap `.h2` utility class supplies the heading scale without making the number an outline entry, so no `font-size` declaration appears in this widget's CSS and the page outline reads one `h1` followed by one `h2` per panel with nothing beneath it. Rendering it in an `<h2>` would place a bare number in the outline underneath the panel's own heading, which is a heading element used for size alone.

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

/* Lays the panel row out by flex wrapping instead of by floats, so the rows are
   decided by the declared column widths alone and every panel on a line takes that
   line's height. Without this the one panel that carries a link is taller than its
   siblings, the fourth panel cannot clear it, and five panels render as three ragged
   rows. Bootstrap's own clearfix pseudo-elements would become flex items carrying the
   width of the space in their `content`, which is enough to wrap a row one column
   early, so they are dropped for the duration. Guarded at the medium breakpoint,
   below which col-md-* carries no width and the float stack is correct. */
@media (min-width: $screen-md-min) {
    .bst-kpi .row {
        display: flex;
        flex-wrap: wrap;
        align-items: stretch;
    }

    .bst-kpi .row:before,
    .bst-kpi .row:after {
        display: none;
    }

    .bst-kpi .row > div {
        display: flex;
    }

    .bst-kpi .bst-kpi-panel {
        flex: auto;
    }
}

.bst-kpi [tabindex="-1"]:focus,
.bst-kpi[tabindex="-1"]:focus {
    outline: $border-radius-base solid $brand-primary;
    outline-offset: $border-radius-small;
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
| `render_mode` | string | `svg` | `svg` renders the inline SVG bar chart specified under [The inline SVG chart](#the-inline-svg-chart). `report` embeds an **allowlisted** saved report instead, per [The report embed](#the-report-embed), and falls back to `svg` when the allowlist or the reporting-widget check does not pass. Any other value resolves to `svg`. |
| `report_id` | string | *empty* | The `sys_report.sys_id` used when `render_mode` is `report`. Ignored when `render_mode` is `svg`. **The report must be one of the two allowlisted, protected, count-only reports** of [The report embed](#the-report-embed), and the stock `report-chart` widget must resolve; when the option is empty or malformed, the report is outside the allowlist, or the reporting widget is absent, the widget falls back to `svg` and states the fallback rather than rendering an empty panel. Server-script step 7 is the gate. |

#### Server script

1. Construct `var builder = new RestResponseBuilder();` and assign `data.authorised = builder.hasAnyAppRole();`. When `data.authorised` is `false`, return immediately and publish nothing further. **Assign the result — do not merely call the method.**
2. Resolve `options.dimension` against the closed set `funding_stage`, `industry`, `employee_count_range`. Any other value falls back to `funding_stage`. Publish the resolved value as `data.dimension`, **and its human label as `data.dimensionLabel`** from this closed mapping, because the companion table's first column header and the chart's `<desc>` both name the dimension in words:

| `data.dimension` | `data.dimensionLabel` |
| --- | --- |
| `funding_stage` | `Funding stage` |
| `industry` | `Industry` |
| `employee_count_range` | `Employee count range` |
3. Publish the bucket labels as `data.labels`, from the **closed choice list of the resolved column**, transcribed from [`../data-model.md`](../data-model.md) and matching the `sys_choice` records the Update Set delivers. **It is read by item 4's bucket loop rather than by the template** — the template renders `data.buckets`, each of whose entries already carries its label — and it is published so the axis the chart was drawn against is visible in the widget's own data payload when a chart's shape is questioned:

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
// The aggregate is the one thing in this widget that can fail, and this is the
// widget's only server round trip: an unhandled failure would publish no buckets
// and the template would render an empty panel with nothing to retry. The message
// goes in data.serverError, which the shared c.load() helper never touches, so a
// failing Retry keeps the panel that carries the Retry control.
var sizes = {};
data.serverError = '';
try {
    sizes = builder.countByGroup('x_bst_startuptrk_startup', data.dimension,
        function (query) {
            search.applyPlan(query, plan);
        });
} catch (aggregateFailure) {
    data.serverError = 'Could not load this breakdown. Use Retry to try again.';
    gs.error('[bst-trends-charts] countByGroup failed for dimension '
        + data.dimension + ': ' + aggregateFailure);
}

// The closed label list of step 3 governs the order and the membership, so a bucket
// with no rows still appears at zero and a stored value outside the choice list is
// not charted. The query answered every bucket; this loop only reads its result.
var buckets = [];
var largest = 0;
var largestLabel = '';
data.labels.forEach(function (label) {
    var count = sizes[label] === undefined ? 0 : sizes[label];
    if (count > largest) {
        largest = count;
        largestLabel = label;
    }
    buckets.push({ label: label, count: count });
});

data.largest = largest;
data.largestLabel = largestLabel;
```

**One query, not one per bucket.** A `countWith` call inside that loop would issue a separate aggregate for every label — eight for `funding_stage`, six for `industry`, five for `employee_count_range` — each re-applying the same inclusion conditions to the same table for a result the grouped aggregate already has. Two charts on the dashboard would then cost up to sixteen queries where they now cost two. `countByGroup()` groups on the column and returns every group's exact size from a single pass, and it carries the same `hasAnyAppRole()` role gate and the same exactness guarantee as `countWith()`.

Two properties of reading the result through the closed label list matter. A bucket the data does not populate is **absent** from the returned object rather than present as zero, which is why the loop defaults it — omitting that default would drop empty buckets from the chart and silently change its shape. And a stored value outside the choice list would appear as its own key in the result; reading through the label list ignores it, which is correct, because the chart's axis is the declared choice list. Such a value should not exist — cleaning rule 3 prevents it on every ingestion path — and if one is present the count of charted rows will be lower than the KPI figure, which is the signal to look for it.

5. For each bucket publish **three** share members, and never one. Publish `data.buckets`, `data.largest` and **`data.largestLabel`** — the label of the largest bucket, or the empty string when `largest` is `0` — because the accessible description names it and has no other source.

   ```javascript
   buckets.forEach(function (bucket) {
       // share: the true ratio to one decimal place, so a small non-zero bucket is not
       // reported as zero. This is what aria-valuenow publishes, so it must be the
       // honest figure rather than a display convenience.
       bucket.share = largest === 0
           ? 0
           : Math.round(bucket.count / largest * 1000) / 10;

       // barPercent: the companion table's CSS width. Floored at one percent for any
       // non-zero count, because a width below that renders as no bar at all and the
       // share column is this chart's declared accessible alternative.
       bucket.barPercent = bucket.count === 0
           ? 0
           : Math.max(1, Math.round(bucket.count / largest * 100));

       // shareText: the share as words, and the one member that can say 'present but
       // very small'. A bucket whose true share is below 0.05 rounds to 0 at one
       // decimal place, and printing '0%' beside a non-zero count contradicts it.
       bucket.shareText = bucket.count === 0
           ? '0%'
           : (bucket.share === 0 ? 'less than 0.1%' : bucket.share + '%');
   });
   ```

   **Three members rather than one, because the three questions have three different right answers.** A single whole-number percentage was asked to be the bar's width, the accessible value and the printed figure at once, and it fails all three for a small bucket: `Math.round(4 / 1000 * 100)` is `0`, so the bar disappears, `aria-valuenow` announces a measured zero, and nothing on the page distinguishes *four startups* from *none*. Rounding twice compounds it — the SVG width was `Math.round(barSpan * share / 100)`, so a share already rounded to `0` produced a width of `0` however wide the plot area was. Six of eight non-zero buckets vanished this way in one measured scenario, including, in another, a bucket of **13,579** startups.

   Each member now answers exactly one question. `share` is the honest ratio and is what assistive technology receives. `barPercent` and the SVG's `barWidth` are *rendering* quantities, floored so that presence is always visible — a floor is legitimate there precisely because those two are pictures of the value rather than the value itself. `shareText` is the printed figure, and it is the only one able to say `less than 0.1%`, which is the truthful thing to show when a real share rounds away. **The floor never applies to a genuine zero**: every one of the three tests `count === 0` first, so an empty bucket still renders no bar and still prints `0%`, and the distinction the chart existed to draw is preserved in both directions.
6. Compute **every** SVG coordinate on the server and publish it, so no numeric literal is written into the template or the CSS. The geometry, its five constants and the description string are specified under [The inline SVG chart](#the-inline-svg-chart).
7. Resolve the render mode last, and publish it as `data.renderMode`. **`report` is published only when every one of six conditions holds**; any failure publishes `svg` and sets `data.reportUnavailable`. The allowlist and the reasoning are under [The report embed](#the-report-embed):

```javascript
// Two reports, allowlisted BY TITLE and each protected against edit. An arbitrary
// readable report is not admissible: a report aggregating SUM(amount_usd) would
// publish a figure step 8 forbids this widget from computing, and 'readable' does
// not exclude it because an administrator can read every report on the instance.
var ALLOWED_REPORTS = ['BST Startups by funding stage (count)',
                       'BST Startups by industry (count)'];
var ID32 = /^[0-9a-f]{32}$/;

data.renderMode = 'svg';
data.reportUnavailable = false;

if (String(options.render_mode || '') === 'report') {
    var reportId = String(options.report_id || '');
    var admissible = false;

    if (ID32.test(reportId)) {
        var report = new GlideRecordSecure('sys_report');
        if (report.get(reportId)) {
            admissible =
                ALLOWED_REPORTS.indexOf(String(report.getValue('title'))) !== -1 &&
                String(report.getValue('table')) === 'x_bst_startuptrk_startup' &&
                String(report.getValue('aggregate')).toUpperCase() === 'COUNT' &&
                !report.getValue('sum_field') &&
                !report.getValue('aggregation_source');
        }
    }

    if (admissible) {
        // Reporting is a plugin: an instance without it carries no 'report-chart'
        // widget, and an unguarded embed renders a blank panel where a chart was
        // promised. Validate the model before committing to report mode.
        var model = null;
        try {
            model = $sp.getWidget('report-chart', { sys_id: reportId });
        } catch (e) {
            model = null;
        }
        if (model && model.sys_id) {
            data.report = model;
            data.renderMode = 'report';
        } else {
            data.reportUnavailable = true;
        }
    } else {
        data.reportUnavailable = true;
    }
}
```

    Every other value of `options.render_mode`, including `svg` and including an empty option, leaves the two initial assignments in place: `svg` with no warning. `data.reportUnavailable` is published as `false` rather than left absent, so the template's `ng-if` tests a defined value.
8. Publish no monetary or averaged figure, for the reason stated in step 2 of [`bst-trends-kpi`](#bst-trends-kpi): a `SUM` or `AVG` over one of the four premium-gated currency columns would compute over values the field-level access control exists to withhold. A **row count**, grouped or not, reads no field and is permitted. **The query cost of this widget is one aggregate**, whatever the dimension and however many buckets it has.

##### The inline SVG chart

A horizontal bar chart, one bar per bucket, drawn as inline SVG inside the widget. It is the shipped mode: both instances on `bst_dashboard` carry `render_mode` = `svg`.

**Five constants, declared in the server script**, which is the only place a number appears — the template binds and the CSS carries none:

| Constant | Value | Governs |
| --- | --- | --- |
| `PLOT_WIDTH` | `720` | The width of the coordinate system. The rendered width comes from the `width="100%"` attribute, so this is a ratio, not a pixel promise. |
| `LABEL_WIDTH` | `210` | The band on the left that carries the bucket label. |
| `VALUE_WIDTH` | `70` | The **minimum** band on the right that carries the count. The band actually used is derived from the widest count — see below. |
| `VALUE_DIGIT_WIDTH` | `11` | The width of one digit at the label type size, used to widen the value band when a count needs more than the minimum. A digit measures 10.113 units at `$font-size-large` in the portal's sans stack, so `11` is a deliberate upper bound rather than an exact metric. |
| `BAR_HEIGHT` | `28` | The height of one bar. |
| `BAR_GAP` | `12` | The vertical space between two bars. |

**The derived geometry**, computed once from those constants and the bucket counts:

```javascript
var PLOT_WIDTH = 720, LABEL_WIDTH = 210, VALUE_WIDTH = 70;
var BAR_HEIGHT = 28, BAR_GAP = 12, VALUE_DIGIT_WIDTH = 11;

// The value band must fit the widest count it will carry, and the widest count is
// always the largest bucket. A fixed 70-unit band is enough for five digits and not
// for eight, and a band that is too narrow does not clip the value - it pushes the
// end-anchored text leftward onto its own bar. Deriving the band keeps the two apart.
var valueWidth = Math.max(VALUE_WIDTH,
    String(largest).length * VALUE_DIGIT_WIDTH + BAR_GAP);
var barSpan = PLOT_WIDTH - LABEL_WIDTH - valueWidth;
var height = buckets.length * BAR_HEIGHT + (buckets.length - 1) * BAR_GAP;

buckets.forEach(function (bucket, index) {
    bucket.y = index * (BAR_HEIGHT + BAR_GAP);
    bucket.textY = bucket.y + Math.round(BAR_HEIGHT * 0.7);

    // Computed from the raw count, not from the rounded share, and floored at one
    // unit for any non-zero count so a populated bucket is never drawn as empty.
    bucket.barWidth = bucket.count === 0
        ? 0
        : Math.max(1, Math.round(barSpan * bucket.count / largest));

    // Anchored at the right edge of the coordinate system and drawn right-to-left by
    // text-anchor="end", so a count of any length grows into the plot area instead of
    // past the viewBox. Left-anchored at LABEL_WIDTH + barSpan + BAR_GAP, an eight-digit
    // count reached 724.95 against a 720-unit box and was clipped.
    bucket.valueX = PLOT_WIDTH;
});

// The accessible description, assembled here rather than referenced from nowhere. An
// earlier revision read a `c_description` variable that no step ever assigned, which
// throws a ReferenceError on the server and leaves the chart unbuilt.
var dimensionLabel = data.dimensionLabel;
var chartDescription = data.largest === 0
    ? 'Horizontal bar chart of startups by ' + dimensionLabel + '. '
        + buckets.length + ' categories, all empty.'
    : 'Horizontal bar chart of startups by ' + dimensionLabel + '. '
        + buckets.length + ' categories. Largest: ' + data.largestLabel
        + ' with ' + data.largest
        + '. Every value is also listed in the table below this chart.';

data.chart = {
    viewBox: '0 0 ' + PLOT_WIDTH + ' ' + height,
    height: height,
    barHeight: BAR_HEIGHT,
    labelWidth: LABEL_WIDTH,
    axisX: LABEL_WIDTH,       // every bar starts here, so this is the zero line
    axisY1: 0,
    axisY2: height,
    description: chartDescription
};
```

`bucket.barWidth` is `0` when, and only when, the bucket count is `0`, which draws nothing and is correct: an empty bucket has no bar, and its count is still stated in the value band and in the companion table. Every non-zero count draws at least one unit, so **no bar width is ever zero for a bucket that has records** — which is the whole distinction the picture is there to make.

**The clamp is applied to `bucket.share` itself, not to a local copy of it.** `share` is published on every bucket and is read in three places — the `width` attribute of the SVG `<rect>`, the inline width of the companion table's `.progress-bar`, and that bar's `aria-valuenow`. Clamping a local variable bounds only the first of the three and leaves the other two reading the raw figure, so a negative aggregate would paint nothing while announcing a value below the `aria-valuemin="0"` the same element declares — a control whose stated value lies outside its own stated range. Assigning the clamped value back onto the bucket bounds all three at once, from one statement, and leaves `bucket.count` alone so the number the caller actually reads is still the unmodified aggregate.

**An unclamped negative does not leave a negative width in the DOM to find, which is what makes it worth guarding rather than debugging later.** `ng-style` assigns the returned width to `element.style.width`, and `-13%` is not a valid CSS length, so the declaration is rejected outright and the element ends up with **no `style` attribute at all** rather than a visible `width: -13%`. The bar collapses to zero and the markup carries no trace of why. The only surviving evidence is the `aria-valuenow` the same element publishes, because an ARIA attribute is a string and is not validated against its own declared range — so the one symptom that does persist is the one nobody looks at. Guarding the value where it is computed is therefore the only place the defect is visible at all.

**The description string**, published as `data.chart.description` and read by the SVG's `<desc>`. Assemble it on the server from the resolved dimension, the bucket count, and the largest bucket:

> `Horizontal bar chart of startups by <dimension label>. <n> categories. Largest: <label> with <count>. Every value is also listed in the table below this chart.`

When `data.largest` is `0`, publish instead: `Horizontal bar chart of startups by <dimension label>. <n> categories, all empty.`

**The accessible wiring.** The `<svg>` carries `role="img"` with an `aria-labelledby` pointing at its own `<title>` and an `aria-describedby` pointing at its own `<desc>`, so a screen reader announces the chart's name and its summary rather than reading a tree of shapes. Both identifiers are derived from `data.dimension` by the client controller, because `bst_dashboard` renders **two** instances of this widget in one document and a repeated `id` would make both point at the first chart's text.

**The companion table is not optional.** The chart is a picture of the same numbers the table below it lists row by row, and the table is what carries the values to a caller who cannot use the picture. Both render together in `svg` mode.

**The two dashboard chart panels do not end level, and that is a flagged design-system gap rather than a defect to be worked around.** Container 3 of [`bst_dashboard`](#bst_dashboard--dashboard--trends) puts two instances of this widget side by side, and they hold different numbers of buckets — eight for funding stage, six for industry — so their panels are different heights. Measured, the difference is **161px at 1024 and 172px at 1366 and above**, decomposing exactly into 58px of SVG (the two extra bars, at the rendered scale) and 114px of companion table (two extra rows at 57px each). Removing the SVG's fixed `height` attribute reduced it — the SVG's share now scales with the viewport instead of contributing a fixed 80 units — but it cannot remove it, because the remaining difference is real content.

**Equal-height columns have no resolution inside this design system**, which is why the graceful-degradation ladder ends at a flag here rather than at a component. Bootstrap 3 is float-based and ships no equal-height row utility. The three ways to force it are all closed: a `min-height` on the panel is a pixel literal, which [zero hard-coded values](#zero-hard-coded-values) forbids; `display: flex` on the row is custom layout on a raw container, which [layout through system primitives](#layout-through-system-primitives-only) forbids; and choosing a spacing token as a stand-in height would be a measured value wearing a token's name, which is the same violation with the evidence hidden. A ragged lower edge between two independent panels in two independent rectangles is ordinary Bootstrap behaviour, it hides nothing and clips nothing, and **no caller-facing content is affected** — so it is recorded in [`../gaps-and-flags.md`](../gaps-and-flags.md) and left as it renders, rather than closed by breaking a rule the rest of this guide keeps.

##### The report embed

When `data.renderMode` is `report`, the widget renders the stock report widget through `<sp-widget>` and draws no SVG. The saved report supplies its own chart, its own title and its own accessible output, so this widget adds none. The companion table still renders, so the two modes agree on what data is stated in text.

**Report mode embeds from a closed allowlist, never from an arbitrary readable report.** `report_id` is an option an operator types, and a saved report is a *query* — a report that aggregates `SUM(amount_usd)` would compute over a premium-gated currency column and publish a figure the field-level access control exists to withhold, which is precisely what server-script step 8 forbids this widget from doing. "Readable" is not a sufficient gate, because the administrator who configures the instance can read every report on it. Two reports are therefore allowlisted **by title**, and the allowlist lives in the widget's server script as a closed array:

| Report `title` | `table` | `type` | `field` (group by) | `aggregate` | Aggregation source | `sys_policy` |
| --- | --- | --- | --- | --- | --- | --- |
| `BST Startups by funding stage (count)` | `x_bst_startuptrk_startup` | `bar` | `funding_stage` | `COUNT` | *empty* | `protected` |
| `BST Startups by industry (count)` | `x_bst_startuptrk_startup` | `bar` | `industry` | `COUNT` | *empty* | `protected` |

Both are created by the operator inside the `x_bst_startuptrk` scope, in the platform's report designer, before `report` mode is configured on any instance. `sys_policy` is set to `protected` so neither can later be edited into a `SUM` or `AVG` — an allowlist whose entries are mutable is an allowlist in name only. Creating them is **optional**: both dashboard instances ship with `render_mode` = `svg`, and nothing on the acceptance path requires report mode to be configured.

**Report mode is also gated on the reporting widget being present.** `$sp.getWidget('report-chart', ...)` resolves a Global-scope `sp_widget` record that a given instance need not carry: reporting is a plugin, and an instance without it has no `report-chart` widget to embed. An unguarded call therefore renders a blank panel where a chart was promised. The call is made inside a `try` and its result is validated before `report` mode is published.

When any one of those checks does not pass — the mode is not `report`, the identifier is malformed, the report does not resolve, its title is outside the allowlist, its table is not the startup table, its aggregate is not `COUNT`, an aggregation source is populated, or the reporting widget did not resolve — `data.reportUnavailable` is `true`, `data.renderMode` is `svg`, and the widget renders the SVG chart preceded by one `.alert.alert-warning` naming the fallback, so an operator sees that the configured report was not used. The bucket geometry is published in every case, so the fallback always has something to draw.

#### Data contract

**Every member below is assigned onto `data` by the server script named in its row, and read by the consumer named in its row. There is no third source and no other member**: a template expression naming anything absent from this table renders nothing at best and raises a runtime expression error at worst, and a member published with no consumer is a dead output. `data.error` is not in any widget's table — it is set on the client by the shared `c.load()` helper of [Error and empty behaviour](#error-and-empty-behaviour) and by nothing on the server. A widget whose own server script catches a failure and reports it publishes that message as **`data.serverError`**, which **is** in that widget's table, and which `c.load()` never touches; the error panel renders `c.errorText()`, which answers either of the two.

| Member | Type | Published by | Consumed by |
| --- | --- | --- | --- |
| `authorised` | True/False | server item 1 | Template — the not-entitled alert and the `ng-if` on the chart region |
| `dimension` | String | server item 2 | Controller — the derived `id` values for `aria-labelledby` and `aria-describedby` |
| `dimensionLabel` | String | server item 2 | Template — the companion table's first column header, and the `<desc>` text assembled on the server |
| `labels` | Array of string | server item 3 | **Server-side only** — item 4's bucket loop. Published so the axis the chart was drawn against is visible in the widget's data payload |
| `buckets` | Array of `{label,count,share,barPercent,shareText,y,textY,barWidth,valueX}` | server items 4, 5 and 6 | Template — the SVG bars, the printed share and the companion table rows. `share` is the true ratio to one decimal and is read **only** by `aria-valuenow`; `barPercent` is read **only** by `c.barStyle()`; `shareText` is read by the printed share and by `aria-valuetext`. The three are not interchangeable — see server item 5 |
| `largest` | Integer | server item 5 | Controller `c.hasData()`; the server's own `<desc>` selection |
| `largestLabel` | String | server item 5 | **Server-side only** — item 6's `<desc>` assembly names it; the empty string when `largest` is `0` |
| `chart` | `{viewBox,height,barHeight,labelWidth,axisX,axisY1,axisY2,description}` | server item 6 | Template — the `<svg>` attributes, its `<desc>`, the zero line's coordinates and the label `clipPath`. `height` composes `viewBox` on the server and sizes the clip rectangle; it is **not** bound as an `svg` height attribute, for the reason under the template |
| `renderMode` | String | server item 7 | Controller `c.isReport()`; the template's two render branches |
| `report` | Widget model | server item 7, report branch only | Template — `<sp-widget widget="data.report">` |
| `reportUnavailable` | True/False | server item 7, fallback branch only | Template — the fallback `.alert.alert-warning` |
| `serverError` | String | the server script's `catch` block around the grouped aggregate, empty on every successful run | Controller `c.errorText()` — and through that helper the error panel, its **Retry** control, and every `ng-if` on the chart region. No expression reads this member directly |

#### Client controller

1. Expose `c.isSvg()` and `c.isReport()` from **`data.renderMode`**, not from `options.render_mode`. The server resolves the mode, including the fallback of step 7, so reading the raw option here would disagree with what the server prepared.
2. Expose `c.barStyle(bucket)`, returning `{ width: bucket.barPercent + '%' }` for the companion table's `.progress-bar`, and `c.hasData()`, true when `data.largest` is greater than zero. **Bind `barPercent` here and never `share`**: `share` is the honest ratio to one decimal place and is what `aria-valuenow` publishes, so using it as a CSS width would render a small bucket at a fraction of a percent — which is no bar at all, and reintroduces in the table exactly the invisibility that server item 5 removes from the chart.
3. Expose the three identifiers the SVG needs, each derived from `data.dimension` so the dashboard's two instances never collide:
   - `c.titleId()` returns `'bst-charts-title-' + c.data.dimension`.
   - `c.descId()` returns `'bst-charts-desc-' + c.data.dimension`.
   - `c.labelClipId()` returns `'bst-charts-labelclip-' + c.data.dimension`, and is referenced by every label `<text>` in that chart. A `clipPath` is resolved by identifier from the whole document, not from the enclosing `<svg>`, so two instances sharing one identifier would clip the second chart's labels against the first chart's rectangle — a rectangle whose height is the *other* chart's bucket count, which silently erases labels below that row.
4. Declare `c.busy` per [Busy, status and focus behaviour](#busy-status-and-focus-behaviour), and implement `c.load()` and `c.retry()` exactly as [Error and empty behaviour](#error-and-empty-behaviour) specifies. This widget issues no server call **after** its first render, but that first render *is* a server call and its aggregate can fail, so it carries the error panel and a working **Retry** — `c.retry()` re-runs the server script through `c.load()`. It carries no status region, because it has no user-initiated action to announce.
5. Perform no arithmetic on record data and compute no coordinate. Every count and every coordinate arrives from the server, and the template binds them with `ng-attr-*`.

#### HTML template

```html
<div class="bst-charts panel panel-default" tabindex="-1" aria-busy="{{c.busy}}">
  <div class="panel-heading">
    <h2 class="panel-title">
      <span class="icon-chart" aria-hidden="true">&nbsp;</span>{{::options.title}}
    </h2>
  </div>
  <div class="panel-body">
    <div class="alert alert-warning" role="alert" ng-if="!data.authorised">
      <span>Your account holds no Boston Startup Tracker role.</span>
    </div>

    <div class="alert alert-danger" role="alert" ng-if="c.errorText()">
      <span class="icon-cross-circle" aria-hidden="true">&nbsp;</span>
      <span>{{c.errorText()}}</span>
      <button type="button" class="btn btn-default" ng-click="c.retry()">Retry</button>
    </div>

    <div class="alert alert-warning" ng-if="data.authorised &amp;&amp; data.reportUnavailable">
      <span>The configured report could not be read. Showing the built-in chart instead.</span>
    </div>

    <div class="alert alert-info" role="status" ng-if="data.authorised &amp;&amp; !c.errorText() &amp;&amp; c.isSvg() &amp;&amp; !c.hasData()">
      <span>No startup is recorded for this breakdown yet.</span>
    </div>

    <svg class="bst-charts-svg"
         ng-if="data.authorised &amp;&amp; !c.errorText() &amp;&amp; c.isSvg() &amp;&amp; c.hasData()"
         role="img"
         width="100%"
         preserveAspectRatio="xMinYMin meet"
         ng-attr-view_box="{{data.chart.viewBox}}"
         ng-attr-aria-labelledby="{{c.titleId()}}"
         ng-attr-aria-describedby="{{c.descId()}}">
      <title ng-attr-id="{{c.titleId()}}">{{::options.title}}</title>
      <desc ng-attr-id="{{c.descId()}}">{{data.chart.description}}</desc>
      <line class="bst-charts-axis"
            ng-attr-x1="{{data.chart.axisX}}" ng-attr-y1="{{data.chart.axisY1}}"
            ng-attr-x2="{{data.chart.axisX}}" ng-attr-y2="{{data.chart.axisY2}}"></line>

      <defs>
        <clipPath ng-attr-id="{{c.labelClipId()}}">
          <rect x="0" y="0"
                ng-attr-width="{{data.chart.labelWidth}}"
                ng-attr-height="{{data.chart.height}}"></rect>
        </clipPath>
      </defs>
      <g ng-repeat="bucket in data.buckets track by bucket.label">
        <text class="bst-charts-text" x="0"
              ng-attr-clip-path="url(#{{c.labelClipId()}})"
              ng-attr-y="{{bucket.textY}}">{{bucket.label}}</text>
        <rect ng-attr-x="{{data.chart.labelWidth}}"
              ng-attr-y="{{bucket.y}}"
              ng-attr-width="{{bucket.barWidth}}"
              ng-attr-height="{{data.chart.barHeight}}"
              fill="currentColor"></rect>
        <text class="bst-charts-text" text-anchor="end"
              ng-attr-x="{{bucket.valueX}}"
              ng-attr-y="{{bucket.textY}}">{{c.count(bucket.count)}}</text>
      </g>
    </svg>

    <div class="table-responsive" tabindex="0"
         ng-if="data.authorised &amp;&amp; !c.errorText() &amp;&amp; c.hasData()">
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
          <tr ng-repeat="bucket in data.buckets track by bucket.label">
            <th scope="row">{{bucket.label}}</th>
            <td class="bst-charts-bar">
              <div class="progress">
                <div class="progress-bar" role="progressbar"
                     ng-style="c.barStyle(bucket)"
                     ng-attr-aria-label="{{bucket.label}}"
                     ng-attr-aria-valuenow="{{bucket.share}}"
                     ng-attr-aria-valuetext="{{bucket.shareText}} of the largest category"
                     aria-valuemin="0" aria-valuemax="100"></div>
              </div>
              <span class="bst-charts-share">{{::bucket.shareText}}</span>
            </td>
            <td><span class="label label-default">{{c.count(bucket.count)}}</span></td>
          </tr>
        </tbody>
      </table>
    </div>

    <sp-widget widget="data.report" ng-if="c.isReport() &amp;&amp; data.report"></sp-widget>
  </div>
</div>
```

Seven properties of that template are what make the chart correct, and each is easy to lose in an edit.

- **Every SVG coordinate arrives through `ng-attr-*`.** `x="0"` and `y="0"` are the only literals, and `0` is a permitted literal everywhere in this portal. No coordinate is computed in the controller and none is written in the CSS.
- **`ng-attr-view_box` is written in snake case on purpose.** The rendered attribute must be `viewBox`, and the `ng-attr-` form converts a snake-case suffix to the camel-case attribute name. `ng-attr-viewbox` would emit a lowercase `viewbox`, which the SVG specification does not define, and the chart would render at its intrinsic size with no scaling.
- **`fill="currentColor"` on every `<rect>`**, so the bar colour is inherited from the CSS `color` property of `.bst-charts-svg` and is never written as a literal.
- **One `<line>` draws the zero line**, at `data.chart.axisX`, which is `LABEL_WIDTH` — the x every bar starts from. It is what makes an empty bucket legible: a bucket of `0` has a bar of width `0` and so draws nothing, and without the line there is no mark at all to read the `0` against. Its four coordinates are published by the server like every other coordinate, and its stroke comes from `$text-muted`.
- **The companion table carries `.table-responsive` and a `.sr-only` caption**, and every `.progress-bar` in it carries `aria-label`, `aria-valuenow`, `aria-valuemin` and `aria-valuemax`. A progress bar with no name and no value is announced as an unlabelled control, which is why the bindings are part of the specification rather than a refinement. `aria-valuenow` binds `bucket.share`, which the server clamps to `0`-`100` in place for exactly this reason, so the announced value always lies inside the range the same element declares.

- **There is deliberately no `height` attribute on the `<svg>`.** With `width="100%"`, a `viewBox` and `preserveAspectRatio="… meet"`, an element that *also* carries a height equal to its viewBox height pins its scale at `min(renderedWidth / 720, 1)` and then keeps its full unscaled height regardless: below 720 rendered units the drawing shrinks inside a box that does not, and the difference is dead space. Measured, that was **127.05px and 94.05px** of permanently blank area in the two dashboard charts at 1024, and 35.0% of the box in a twenty-bucket case. Omitting the height lets the viewBox supply the intrinsic aspect ratio, so the box is exactly as tall as the drawing at every width and the scale is no longer capped at 1:1. This is also half of what makes the labels legible at the 1024 floor — see the CSS note below.
- **The label `<text>` is clipped to the label band.** SVG paints in document order and each group is ordered label, bar, value, so an opaque bar draws **on top of** a label that overruns its 210-unit band — measured, an 83-character label lost **62.0%** of its rendered width behind its own bar, leaving a fragment that reads as a complete but wrong label. The `clipPath` cuts the label cleanly at the band edge instead, so an overrun is visibly an overrun. The clip is declared **once per chart** in `<defs>` and referenced by every row, and its identifier is derived from `data.dimension` for the same reason the title and description identifiers are: `bst_dashboard` renders **two** instances in one document, and a repeated `id` would make the second chart's labels clip against the first chart's rectangle. **No per-element `<title>` is added** to recover the full string: this chart is tooltip-free by design, a `<title>` child is exactly how an SVG tooltip is created, and the companion table already carries every label in full as the declared accessible alternative.
- **The value `<text>` is anchored at the right edge, not the left.** `text-anchor="end"` with `x` at `PLOT_WIDTH` grows a long count leftward into the plot area. Left-anchored, the design's own 70-unit value budget implied text reaching 732 in a 720-unit box, and an eight-digit count measured 724.95 — clipped by the viewBox with no warning at any viewport, because the overflow is in user units rather than CSS pixels.

  **Anchoring at the right edge moves the problem rather than removing it, which is why the value band is derived.** Left-anchored, the design's own 70-unit value budget implied text reaching 732 in a 720-unit box, and an eight-digit count measured 724.95 — clipped by the viewBox with no warning at any viewport, because the overflow is in user units and therefore invisible to every CSS overflow check. End-anchored, the same count cannot leave the box, but it grows **inward**: measured, an eight-digit count reached 10.9 units past the bar's right edge, putting one digit on top of a `$brand-primary` bar at **2.75:1** where the rest of the string sits on white at 12.6:1. The digit is legible — the value text is the last child of its group, so it paints over the bar rather than under it — but it is the one character in the chart that fails contrast. Deriving `valueWidth` from `String(largest).length` reserves the room the count actually needs, so the bar ends before the value begins. **The derivation is a no-op for realistic data**: any count of five digits or fewer keeps `valueWidth` at the 70-unit minimum and `barSpan` at exactly 440, which is the geometry every other state is measured against.
- **The companion table carries `.table-responsive`, `tabindex="0"` and a `.sr-only` caption**, and every `.progress-bar` in it carries `aria-label`, `aria-valuenow`, `aria-valuetext`, `aria-valuemin` and `aria-valuemax`. A progress bar with no name and no value is announced as an unlabelled control, and one with a bare number is announced without a unit — `aria-valuetext` is what supplies both, and assistive technology prefers it over `aria-valuenow` when it is present. The share is **also printed as text** in the same cell, because a bar is a picture and this column is the chart's declared accessible alternative: a column headed "Share of the largest category" that states no number anywhere is not one. `tabindex="0"` is required by [rule 14](#rules-that-bind-all-eight).

`data.dimensionLabel` is published by server-script item 2 and is what this header binds, so the table's first column names what the rows are.

#### CSS

```scss
.bst-charts {
    margin-bottom: $grid-gutter-width;
}

.bst-charts .bst-charts-table {
    margin-bottom: 0;
}

.bst-charts .bst-charts-bar {
    width: auto;
}

/* No WIDTH here: the element carries width="100%" and a CSS width would override
   that presentation attribute. `height: auto` is deliberate and does override the
   bound ng-attr-height, which stays on the element as the no-CSS fallback. With a
   percentage width and a fixed pixel height the two disagree: preserveAspectRatio
   fits the drawing to the smaller of the two ratios, so the drawing filled the box
   horizontally and left roughly a quarter of its height empty, and the box's height
   no longer tracked its width. Letting the viewBox decide the height removes the
   empty band and makes the box's aspect ratio the drawing's own. */
.bst-charts .bst-charts-svg {
    display: block;
    height: auto;
    margin-bottom: $grid-gutter-width;
    color: $brand-primary;
}

.bst-charts .bst-charts-svg .bst-charts-text {
    fill: $sp-tagline-color;
    font-family: $font-family-sans-serif;
    font-size: $font-size-large;
}

/* The zero line every bar starts from. */
.bst-charts .bst-charts-svg .bst-charts-axis {
    stroke: $text-muted;
}

/* The track and the fill are left to the theme's own $progress-bg and
   $progress-bar-bg, which is what makes the rendered pair equal row 19 of
   The contrast check. An earlier revision overrode the track to $table-bg
   (transparent) and the fill to currentColor - and currentColor on a
   .progress-bar resolves against Bootstrap's own .progress-bar { color: #fff },
   not against the cell around it, so the fill painted white on a transparent
   track and measured 1.00:1. Neither override is reinstated. */
.bst-charts .bst-charts-bar .progress {
    margin-bottom: 0;
}

.bst-charts [tabindex="-1"]:focus,
.bst-charts[tabindex="-1"]:focus {
    outline: $border-radius-base solid $brand-primary;
    outline-offset: $border-radius-small;
}

.bst-charts .bst-charts-bar .progress-bar {
    background-color: $brand-primary;
}

.bst-charts .bst-charts-share {
    color: $sp-tagline-color;
}

.bst-charts .sr-only {
    position: absolute;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
}

@media (forced-colors: active) {
    .bst-charts .label {
        border-style: solid;
    }
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
        heading: 'Premium fields are reserved'
    });
}
```

6. Read **no** application record. This widget reports entitlements, not data.
7. Publish nothing about billing, payment, price or checkout. The platform grants entitlement through roles and has no commerce capability; the requirement is flagged as **G6** in [`../gaps-and-flags.md`](../gaps-and-flags.md), and the operational path is an administrator granting `x_bst_startuptrk.premium_user` on the instance.

#### Data contract

**Every member below is assigned onto `data` by the server script named in its row, and read by the consumer named in its row. There is no third source and no other member**: a template expression naming anything absent from this table renders nothing at best and raises a runtime expression error at worst, and a member published with no consumer is a dead output. `data.error` is not in any widget's table — it is set on the client by the shared `c.load()` helper of [Error and empty behaviour](#error-and-empty-behaviour) and by nothing on the server. A widget whose own server script catches a failure and reports it publishes that message as **`data.serverError`**, which **is** in that widget's table, and which `c.load()` never touches; the error panel renders `c.errorText()`, which answers either of the two.

| Member | Type | Published by | Consumed by |
| --- | --- | --- | --- |
| `authorised` | True/False | server item 2 | Template — the not-entitled alert and the `ng-if` on the summary |
| `user` | `{name,user_name}` | server item 1 | Template — the signed-in heading; controller `c.statusText()` |
| `roles` | Object of three booleans | server item 2 | **Server-side only** — items 3 and 4 derive the effective role and the entitlement rows from it |
| `effectiveRole` | String | server item 3 | Template — the supporting role name; controller `c.statusText()` |
| `effectiveRoleLabel` | String | server item 3 | Controller `c.roleLabel()`, which the template renders |
| `entitlements` | Array of `{label,granted}` | server item 4 | Template — the entitlements list group |
| `premiumDenied` | True/False | server item 5 | Controller `c.isDenied()`; server item 5's embed decision |
| `upsell` | Widget model | server item 5 | Template — `<sp-widget widget="data.upsell">` |

#### Client controller

1. Implement `c.load()` and `c.retry()` exactly as [Error and empty behaviour](#error-and-empty-behaviour) specifies, and route the widget's initial load through `c.load()`.
2. Expose `c.roleLabel()`, returning `data.effectiveRoleLabel`, and `c.isDenied()` from `data.premiumDenied`. **The template renders `c.roleLabel()`**, never the raw role name on its own; the role name is shown beside it as supporting detail.
3. Declare `c.busy` and `c.statusText()` per [Busy, status and focus behaviour](#busy-status-and-focus-behaviour), and also declare `c.focusDestination()` and `c.onButtonKey($event)` per [Busy, status and focus behaviour](#busy-status-and-focus-behaviour), and `c.indeterminate()` for the striped bar. This widget's status wording is:
   - empty — `No entitlement is granted to this account.`, used when `data.effectiveRole` is `none`.
   - loaded — `Signed in as {{c.data.user.name}}. Effective role {{c.data.effectiveRoleLabel}}.`
4. Issue no server call after the first render, other than a retry.

**This widget offers no request, upgrade or notification action, and claims no outcome it does not produce.** There is no request control, no message stating that a request has been noted, and no client-side notification: the application has no commerce, workflow or notification capability in scope, so an action of that kind would report a result that never happened. What the caller is told instead is exactly what is true — an administrator grants the role on the instance — and that wording is published once, by the embedded `bst-premium-upsell` partial, as **that widget's** `guidance` member. This widget publishes no `guidance` of its own and its template reads none; the wording reaches the page through `data.upsell`. See [`../gaps-and-flags.md`](../gaps-and-flags.md) flag **F1** and gap **G6**.

#### HTML template

```html
<div class="bst-account" tabindex="-1" aria-busy="{{c.busy}}">
  <div class="sr-only" role="status" aria-live="polite" aria-atomic="true">{{c.statusText()}}</div>

  <div class="progress" ng-if="c.busy">
    <div class="progress-bar progress-bar-striped active" role="progressbar"
         ng-style="c.indeterminate()"
         aria-label="Loading your account" aria-valuemin="0" aria-valuemax="100"
         aria-valuetext="Loading"></div>
  </div>

  <h1 class="h2" tabindex="-1" ng-if="c.errorText()">Your account</h1>

  <div class="alert alert-danger" role="alert" ng-if="c.errorText()">
    <span class="icon-cross-circle" aria-hidden="true">&nbsp;</span>
    <span>{{c.errorText()}}</span>
    <button type="button" class="btn btn-default" ng-click="c.retry()">Retry</button>
  </div>

  <div class="panel panel-default" ng-if="!data.error">
    <div class="panel-heading">
      <h1 class="panel-title" tabindex="-1">
        <span class="icon-user" aria-hidden="true">&nbsp;</span>{{::options.title}}
      </h1>
    </div>
    <ul class="list-group">
      <li class="list-group-item">
        <div class="row">
          <div class="col-md-5 col-lg-5">Signed in as</div>
          <div class="col-md-7 col-lg-7 text-right"><bdi dir="auto">{{::data.user.name}}</bdi></div>
        </div>
      </li>
      <li class="list-group-item">
        <div class="row">
          <div class="col-md-5 col-lg-5">User name</div>
          <div class="col-md-7 col-lg-7 text-right"><bdi dir="auto">{{::data.user.user_name}}</bdi></div>
        </div>
      </li>
      <li class="list-group-item">
        <div class="row">
          <div class="col-md-5 col-lg-5">Effective role</div>
          <div class="col-md-7 col-lg-7 text-right">
            <span class="label label-primary" ng-if="data.authorised">{{c.roleLabel()}}</span>
            <span class="label label-default" ng-if="!data.authorised">No role</span>
            <small class="text-muted bst-account-role-name"
                   ng-if="::data.effectiveRole">{{::data.effectiveRole}}</small>
          </div>
        </div>
      </li>
    </ul>
  </div>

  <div class="alert alert-warning" role="alert" ng-if="!data.error &amp;&amp; !data.authorised">
    <span>Your account holds none of the three Boston Startup Tracker roles. An administrator grants one on the instance.</span>
  </div>

  <div class="panel panel-default" ng-if="!data.error &amp;&amp; options.show_entitlements">
    <div class="panel-heading"><h2 class="panel-title">Entitlements</h2></div>
    <ul class="list-group">
      <li class="list-group-item" ng-repeat="row in ::data.entitlements track by row.label">
        <div class="row">
          <div class="col-md-8 col-lg-8">{{::row.label}}</div>
          <div class="col-md-4 col-lg-4 text-right">
            <span class="label label-primary" ng-if="::row.granted">Granted</span>
            <span class="label label-default" ng-if="::!row.granted">Not granted</span>
          </div>
        </div>
      </li>
    </ul>
  </div>

  <sp-widget widget="data.upsell" ng-if="!data.error &amp;&amp; data.upsell"></sp-widget>

  <a class="btn btn-default" ng-keydown="c.onButtonKey($event)"
     ng-href="?id=bst_home">Back to search</a>
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

/* Same float containment and the same word guard as the company and investor
   overviews. Signed in as and User name both carry a .pull-right, and a
   sys_user name is not length-bounded by this application. */
.bst-account .list-group-item {
    display: flow-root;
    overflow-wrap: break-word;
    unicode-bidi: isolate;
}

.bst-account .list-group-item .label {
    margin-left: $padding-base-vertical;
    white-space: normal;
    overflow-wrap: break-word;
}

.bst-account .sr-only {
    position: absolute;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
}

.bst-account .btn:focus {
    outline-style: auto;
}

.bst-account .bst-upsell {
    margin-bottom: $grid-gutter-width;
}

.bst-account .bst-upsell .panel-title {
    margin-bottom: $padding-base-vertical;
}

.bst-account .bst-upsell .bst-upsell-fields {
    margin-top: $padding-base-vertical;
    margin-bottom: $padding-base-vertical;
}

.bst-account .bst-upsell .bst-upsell-fields .label {
    margin-right: $padding-base-vertical;
    white-space: normal;
    overflow-wrap: anywhere;
}

.bst-account .bst-upsell .bst-upsell-guidance {
    margin-bottom: 0;
}


@media (forced-colors: active) {
    .bst-account .label {
        border-style: solid;
    }
}

.bst-account [tabindex="-1"]:focus,
.bst-account[tabindex="-1"]:focus {
    outline: $border-radius-base solid $brand-primary;
    outline-offset: $border-radius-small;
}
```

- **`overflow-wrap: break-word` and `unicode-bidi: isolate` on `.list-group-item`** are this widget's share of [the cleaning rules these widgets apply at render](#rules-that-bind-all-eight). Every value in the identity and entitlement rows is data — a display name, a user name, a role name — so any of them can arrive as one unbreakable token or in a right-to-left script.
- **`white-space: normal` and `overflow-wrap: break-word` on a chip in a list row** are [rule 13](#rules-that-bind-all-eight). This widget's chips carry **role names**, and a fully qualified scoped role name such as `x_bst_startuptrk.premium_user` is the longest chip text anywhere in the portal; Bootstrap's `.label { white-space: nowrap }` would make it an unbreakable box wider than its own cell.
- **`.sr-only`** is [rule 15](#rules-that-bind-all-eight), acting on the status region this widget renders.
- **`.btn:focus { outline-style: auto }`** restores a focus indicator that is not the hover treatment. Bootstrap resolves `.btn:focus` and `.btn:hover` to the **same** background, so measured on this widget keyboard focus and pointer hover computed an identical `background-color` and the only difference was an inset ring at roughly 2.8:1. The ring is declared unconditionally, for the reason given for the [search widget's focus rule](#bst-startup-search): a media-query scope would fix only the mode where the indication vanishes and leave the mode where it is merely weak.
- **The forced-colours chip border** is [rule 12](#rules-that-bind-all-eight). This widget renders ten `.label` chips — the effective role, three entitlement markers and the six withheld field names — and forced colours discards `background-color`, which is the only thing distinguishing `Granted` from `Not granted`.
- **The `.bst-upsell` rules** are [rule 16](#rules-that-bind-all-eight): this widget embeds `bst-premium-upsell` with `$sp.getWidget()`, which creates no instance, so the partial's own CSS field may never be compiled into this page and these declarations would otherwise have no source at all. They are exactly the partial's rules that nothing else on this page supplies — measured against the partial rendered on its own, not inferred — and the chip rule is the partial's own selector with this widget's root prepended, so the cascade resolves on specificity rather than on sheet order.

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
| `heading` | `Premium data is hidden on this profile` | `Premium investor data is hidden` | `Premium fields are reserved` |

Each host embeds it **only** when at least one key was omitted from its own serialised data, or — on the account summary — when the caller holds neither `x_bst_startuptrk.admin` nor `x_bst_startuptrk.premium_user`.

#### Server script

1. Read `options.context`, `options.gated_fields`, `options.upsell_page` and `options.heading`. Apply the defaults above for any that arrive empty, then **publish the resolved context as `data.context`** — the client controller derives the region's accessible identifier from it, and reading `options.context` in the controller would read the unresolved value.
2. Split `options.gated_fields` on the comma, trim each entry, discard empties, and map each surviving token to an object carrying the token as `name` and its human label as `label`. Publish that array as `data.fields`.

**Publish objects, not bare label strings.** The template repeats with `track by field.name` and renders `{{::field.label}}`, so a string array breaks it twice over: every `field.name` evaluates to `undefined`, which AngularJS treats as one repeated tracking key and rejects with a `ngRepeat:dupes` error the moment two or more fields are withheld, and every `{{::field.label}}` renders empty, so the chips appear blank. The token is kept alongside the label rather than discarded because it is the stable identity — two different columns can share a display label, as `contact_email` does across two tables, whereas the token is unique within the allowlist.

**The allowlist is six option tokens, and they represent the seven physical access-controlled fields.** The counts differ by one on purpose: `contact_email` is one token covering **two** columns, `x_bst_startuptrk_founder.contact_email` and `x_bst_startuptrk_executive.contact_email`, which carry the same name, the same label and the same field-level access control on two tables. The seven fields themselves are listed under [Step 6](#step-6--access-control-in-every-widget-server-script).

| Option token | Label | Access-controlled field or fields it represents |
| --- | --- | --- |
| `total_funding_usd` | Total funding | `x_bst_startuptrk_startup.total_funding_usd` |
| `institutional_funding_last_5yrs` | Institutional funding in the last five years | `x_bst_startuptrk_startup.institutional_funding_last_5yrs` |
| `contact_email` | Founder and executive contact email | `x_bst_startuptrk_founder.contact_email` **and** `x_bst_startuptrk_executive.contact_email` |
| `aum_usd` | Assets under management | `x_bst_startuptrk_investor.aum_usd` |
| `amount_usd` | Round amount | `x_bst_startuptrk_fundinground.amount_usd` |
| `valuation_usd` | Round valuation | `x_bst_startuptrk_fundinground.valuation_usd` |

**Any token that is not one of those six is rejected: discard it silently and render nothing for it.** Do not fall back to the token itself as a label, and do not render an entry with an empty label — either would put an unmapped column name in front of a caller. `portfolio_count` is the token most likely to be passed by mistake and is **rejected**: `x_bst_startuptrk_investor.portfolio_count` is readable by all three roles and is not premium-gated, so it is never withheld and never named here.

When every supplied token is rejected, `data.fields` is an empty array and the template's field list does not render. The heading, the body and the call to action still render, because the host embedded this widget only after something was in fact withheld.

3. Publish `data.body`, one of these three strings, selected from `options.context`:

| `options.context` | `data.body` |
| --- | --- |
| `company` | `This company profile has premium fields on it. Funding amounts, valuations and contact addresses are reserved for the premium tier. Everything else on this profile is available to your account.` |
| `investor` | `This investor profile has premium fields on it. Assets under management, round amounts and valuations are reserved for the premium tier. The portfolio list and the portfolio count are available to your account.` |
| `account` | `Your account reads the seven tables and every field that is not reserved for the premium tier. The fields below are reserved, and an administrator grants the premium role that reads them.` |

Apply the `account` wording for any context value that is not one of the three, so an unrecognised context still renders a sentence that is true of every surface.

4. Publish `data.callToActionLabel` — `Go to account management` for `company` and `investor` — and `data.upsellPage` from `options.upsell_page`. **Publish no call-to-action label for `account`**, where the caller is already on the destination; publish `data.guidance` instead, the one truthful instruction this application can give:

> `An administrator grants the premium role on this instance. Ask your ServiceNow administrator to add the role x_bst_startuptrk.premium_user to your user record.`

`data.guidance` is the whole of what this widget says about obtaining the role. **It is text, not an action.** There is no request button, no notification and no message claiming that a request has been recorded: the application has no commerce, workflow or notification capability in scope, so any such control would report an outcome it did not produce. Premium subscription billing is flagged as **F1** in [`../gaps-and-flags.md`](../gaps-and-flags.md), not built.

5. Read **no** record and reference **no** field value. This widget renders column names and static wording only. It must never receive, hold or render a gated value; a partial that carried the value it exists to hide would defeat the field-level access controls entirely.

#### Data contract

**Every member below is assigned onto `data` by the server script named in its row, and read by the consumer named in its row. There is no third source and no other member**: a template expression naming anything absent from this table renders nothing at best and raises a runtime expression error at worst, and a member published with no consumer is a dead output. `data.error` is not in any widget's table — it is set on the client by the shared `c.load()` helper of [Error and empty behaviour](#error-and-empty-behaviour) and by nothing on the server. A widget whose own server script catches a failure and reports it publishes that message as **`data.serverError`**, which **is** in that widget's table, and which `c.load()` never touches; the error panel renders `c.errorText()`, which answers either of the two.

| Member | Type | Published by | Consumed by |
| --- | --- | --- | --- |
| `fields` | Array of `{name, label}` objects | server item 2 | Template — the withheld-field list, repeated `track by field.name` and rendered from `field.label` |
| `body` | String | server item 3 | Template — the alert body |
| `callToActionLabel` | String | server item 4 | Template — the call-to-action button, on the `company` and `investor` contexts only |
| `upsellPage` | String | server item 4 | Template — that button's `href` |
| `guidance` | String | server item 4 | Template — the guidance paragraph on the `account` context. **This is the single published wording** for how the premium role is obtained; `bst-account-summary` renders it through this embed rather than publishing its own |

#### Client controller

1. Expose `c.isAccount()` from **`data.context`**, so the account host renders `data.guidance` rather than a navigation link to the page it is already on. Read the **resolved** context and never `options.context`, for the reason server item 1 gives: the server applies the default before publishing, so an option that arrives empty or misspelled reaches the controller as the resolved value through `data` and as the raw value through `options`. `c.headingId()` already reads `data.context`, and the two must agree — a controller that resolves the same question from two different sources will eventually answer it two different ways.
2. Declare `c.busy` per [Busy, status and focus behaviour](#busy-status-and-focus-behaviour). This widget carries no status region and no error panel: it renders once, from options its host supplied, and issues no server call of its own.
3. Expose **no** request, upgrade or notification function. There is nothing for such a function to do that would be true.
4. Expose `c.headingId()`, returning `'bst-upsell-title-' + (c.data.context || 'default')`. The template's root is a **labelled region**, not an alert: this notice is present from the first render and states a standing fact about the caller's entitlement, so announcing it assertively would interrupt for something that did not just happen. `role="region"` with an `aria-labelledby` gives it a name and a place in the landmark list instead. The identifier is derived from the context because the three hosts pass three different values and two upsells must never share an `id`.

#### HTML template

```html
<div class="bst-upsell alert alert-info" role="region" aria-labelledby="{{::c.headingId()}}" aria-busy="{{c.busy}}">
  <h2 class="panel-title" ng-attr-id="{{::c.headingId()}}">
    <span class="icon-locked" aria-hidden="true">&nbsp;</span>{{::options.heading}}
  </h2>
  <p>{{::data.body}}</p>
  <ul class="list-inline bst-upsell-fields" ng-if="::data.fields.length > 0">
    <li ng-repeat="field in ::data.fields track by field.name">
      <span class="label label-default">{{::field.label}}</span>
    </li>
  </ul>
  <a class="btn btn-primary" ng-if="::!c.isAccount()" ng-keydown="c.onButtonKey($event)"
     ng-href="?id={{::data.upsellPage}}">
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

/* The chips stack one per line, so the separation they need is vertical and it
   belongs on the list item. A horizontal margin has no adjacent sibling to
   separate from, because each .label is the only inline child of its own block
   <li>; and a vertical margin on the inline .label itself would not affect the
   line box either. The list item is the only element that can carry it. */
.bst-upsell .bst-upsell-fields > li + li {
    margin-top: $padding-base-vertical;
}

.bst-upsell .bst-upsell-fields .label {
    margin-right: $padding-base-vertical;
    white-space: normal;
    overflow-wrap: anywhere;
}

.bst-upsell .panel-title {
    margin-bottom: $padding-base-vertical;
}

.bst-upsell .bst-upsell-guidance {
    margin-bottom: 0;
}

.bst-upsell .btn:focus {
    outline-style: auto;
}

@media (forced-colors: active) {
    .bst-upsell .label {
        border-style: solid;
    }
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
| `bst_company` | company profile, upsell | **12** | one record read (1), then two per child collection across five collections — a bounded read and its `COUNT` (10), plus one batched read of the join table covering every round on the page (1). 1 + 10 + 1 = 12. |
| `bst_investor` | investor profile, upsell | **7** | the investor record; the led rounds and their count; the capped join rows and their count; the participated rounds; the portfolio companies. |
| `bst_dashboard` | KPI row, two chart instances | **5 to 7** | one `COUNT` aggregate per KPI panel — three with neither optional panel shown, five with both, per [`bst-trends-kpi`](#bst-trends-kpi) — plus exactly one grouped aggregate per chart instance, so 3 + 2 = 5 at the low end and 5 + 2 = 7 at the high end. |
| `bst_account` | account summary, upsell | **1 to 3** | the caller's role state, and a count only where the summary reports one. |

Four properties hold across the whole table, and each is what a reviewer should verify:

- **No count iterates.** Every figure comes from `countState()`, `countWith()` or `countByGroup()`, each of which answers one exact `COUNT` aggregate behind the `hasAnyAppRole()` role gate that mirrors the layer-1 table read controls. None returns a floor, and none walks a result set to arrive at a number.
- **No collection is read without a limit.** Every child list on the two profile pages carries a limit option, and every limit is validated to a positive whole number with a fallback — an empty or malformed option resolves to the default, never to "no limit".
- **No cost is proportional to the record.** A company with two job postings and a company with twenty thousand cost the same twelve queries; only the number of **rows returned** differs, and that is capped. An investor that led one round and one that participated in three thousand cost the same seven, because the join read carries the cap and everything downstream reads from its result.
- **No chart costs more than one query**, whatever its dimension and however many buckets its choice list declares.

**Two things are out of scope for every widget in this guide: caching and throttling.** No widget caches a read, and no widget rate-limits its own server script. The fixed-window rate limit belongs to the REST surface and is documented in [`../api-reference.md`](../api-reference.md). Both positions are settled in [`../../../docs/decisions/DECISION_LOG.md`](../../../docs/decisions/DECISION_LOG.md).

### The Angular surface available inside a widget

The framework inside a Service Portal widget is AngularJS 1.x with Bootstrap 3.3.6. The surface below is the whole of what these eight widgets use.

#### Template directives

| Directive | Use in this portal |
| --- | --- |
| `ng-repeat` | Every collection: result cards, table rows, list-group items, KPI panels, tab items, chart buckets, upsell field labels. Always with `track by <item>.sys_id` where the item is a record, and `track by <item>.label` or `.id` where it is not. |
| `ng-if` | Every conditional region, including **every premium-field omission test**. Prefer it over `ng-show`, so a denied field's markup is never present in the document. |
| `ng-model` | The three filter inputs of `bst-startup-search`. |
| `ng-class` | The `.active` class on `.nav-tabs` items and `.tab-pane` panes, and the computed column class in `bst-trends-kpi`. |
| `ng-click` | Tab selection, pager buttons, the **Clear** button, and the retry button of every error panel. **Not** the search control: the form submits through `ng-submit="c.submit()"` on the `<form>`, so the Enter key in any of the three fields does exactly what the button does. |
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
| `spUtil.addInfoMessage(message)` | **Not used by any widget in this portal.** It is listed so its absence is deliberate rather than an oversight: neither `bst-account-summary` nor `bst-premium-upsell` acknowledges a premium-role request, because neither offers one — the application has no request, approval or entitlement-change workflow, and a message claiming a request had been noted would assert an outcome nothing produces. Both widgets state the guidance as text instead. See [`bst-premium-upsell`](#bst-premium-upsell) and [`bst-account-summary`](#bst-account-summary), and flag [`F2`](../gaps-and-flags.md#f2--automatic-entitlement-transition-on-payment). |
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
| `spModal.open(options)` | **Not called by any widget in this portal.** It would open a Bootstrap `.modal` carrying a widget — the stock **Form** widget, for instance — but no widget here writes, and the administrative write path is the platform's own form view on the scoped table rather than a portal surface. |
| `spModal.alert(message)` | **Not called by any widget in this portal.** There is no action to acknowledge: all eight widgets are read-only. |
| `spModal.confirm(message)` | **Not called by any widget in this portal.** No path here writes, so there is nothing destructive to confirm. |
**All three are listed as unused deliberately.** They are the framework's dialogue API and an operator who needs one will look for it here; recording that no widget calls one, and why, is what stops a later change from adding a modal write path that the access controls would refuse and this guide never specified.


#### `$location`

`$location` reads and writes the query string of the current portal route.

| Call | Use in this portal |
| --- | --- |
| `$location.search()` | Reading the whole parameter object — `$location.search().sys_id` on the company and investor profiles. |
| `$location.search(name, value)` | Writing one parameter — `bst-startup-search` mirroring each filter so the search is linkable. |
| `$location.search(object)` | Writing the whole filter set in one call. |

Never assemble a portal URL by string concatenation in a controller, and never write the `bst` suffix into a widget. A template link is relative — `?id=bst_company&sys_id={{item.sys_id}}` — and `$location` handles the rest.

#### The framework is end-of-life — what must never be introduced

**Read this before adding anything to a widget that is not already in the tables above.** AngularJS 1.x reached its final release, `1.8.3`, in April 2022 and is end-of-life: **no patch will ever be issued for it**. Bootstrap 3.3.6 is likewise a superseded line. Both are supplied by the platform's Service Portal framework, not by this application — there is no version to bump, no dependency to pin, and prompt section 6.0 forbids the scoped application from modifying anything outside `x_bst_startuptrk`. **The framework version is not a variable any operator of this application controls.**

The consequence follows directly, and it is the reason this subsection exists rather than a note in a decision record. For every published defect in these two libraries, the only control available to this application is **not reaching the sink**. Today no sink is reached. That is a property of **these eight templates and their scripts**, not a property of the platform — which means an ordinary-looking edit can remove it, silently, with no build error, no lint failure and no test that currently watches for it. What follows is that property written down as a rule, so a later author has to decide to break it rather than break it by not knowing.

**Measured on the delivered widgets.** Every token below returns **zero** occurrences across all eight widget bodies in this guide, with the two stated exceptions:

| Never introduce | What the published defects in it concern | Use instead |
| --- | --- | --- |
| `srcset`, `ng-srcset`, `ng-attr-srcset` | A sanitisation bypass in `srcset` handling, and a regular-expression denial of service in the `ng-srcset` parser. | `ng-src` with a single source. The only image in this portal is the startup logo in `bst-startup-results` and `bst-company-profile`, and one source is all it needs. |
| `ng-bind-html`, `$sce.trustAsHtml`, `$sce.trustAsResourceUrl`, `trustAs`, `$compile` on caller data | Each one **removes** the framework's own sanitisation, which is the single control standing between record data and markup execution. The entire cross-site-scripting argument for these eight widgets is that none of them renders data as markup. | `{{ }}` interpolation or `ng-bind`, which escape. For a locator, `ng-href` or `ng-src`. **One prohibition of this form already appears above** — see rule 1 of [External locators in a binding](#external-locators-in-a-binding) — and this row is the general case of it. |
| `innerHTML`, `outerHTML`, `insertAdjacentHTML`, `document.write`, `eval(`, `new Function` | These bypass the framework entirely, so no framework fix would ever protect them. | Nothing in a widget needs them. Build a document fragment with `createElement` and `textContent` if an element must be constructed at all. |
| `angular.merge`, `angular.extend` with a caller-controlled source object | Prototype pollution through a crafted `__proto__` key in the merged object. | Copy the fields you want by name. Every widget model in this guide is assembled field by field for exactly this reason. |
| `$locale` overrides, `NUMBER_FORMATS` replacement | A regular-expression denial of service in locale-driven number formatting. | Format server-side. Every figure a widget renders is already formatted by the server script that produced it. |
| `ng-model-options` with a `debounce` on a caller-supplied expression, `ng-jq` | Neither is needed by any widget here, and each widens the surface for no gain. | The three filter inputs use plain `ng-model` and a single `ng-submit`. |
| Any Bootstrap JavaScript plugin — `carousel`, `tooltip`, `popover`, `collapse`, `affix`, `tab`, `data-loading-text` | The published cross-site-scripting records against this Bootstrap line are reached through `data-*` attributes that these plugins read and inject. **No plugin is enabled in this portal**, which is why the tab strip is driven by `ng-class` and `ng-click` rather than by Bootstrap's own `data-toggle="tab"`. | The Angular directives in the tables above. The tab contract is specified at [The tab contract](#the-tab-contract) and uses no Bootstrap behaviour at all. |
| An **interpolated** value inside any `data-*` attribute | The same Bootstrap records: the injection arrives as attribute content. | `ng-attr-*`, which is the form for every interpolated attribute that is not a link, an image source or a class. |

**The two exceptions, stated exactly so the rule above stays checkable.**

- The seven `data-bst-row="…"` markers in the templates are **static string literals** — `result`, `rounds`, `founders`, `executives`, `jobs`, `news`, `portfolio`. None is interpolated, and none carries record data.
- `c.unrendered(collection)` builds a `querySelectorAll` selector by concatenating one of those seven literal collection names. That is a **selector string evaluated against the widget's own subtree**, not markup and not an attribute value, and its input is a literal from the widget's own template rather than anything a caller supplies. See [Rendered rows and model rows must agree](#rendered-rows-and-model-rows-must-agree).

**Verify it rather than trust it.** Before saving any widget, search its template, client script and server script for the tokens in the first column above. The expected result is zero for every one of them, and the two exceptions are the only interpolation-adjacent constructs in the set. A non-zero count is not automatically a defect — but it is a decision that has to be made deliberately, recorded, and justified against the fact that **no patch for either library will ever arrive**.

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
- [ ] The **only** permitted literals in widget CSS are `0`, `none`, `auto`, `inherit`, `currentColor` and `transparent`. This governs *measured* values — colours, lengths, radii and font sizes. A CSS **keyword** that names a behaviour rather than a measurement is not a measured value and is permitted: `display: block`, `overflow-wrap: break-word`, `border-color` resolving to a token, and the like. The test is whether the value could have been a token and was not.
- [ ] No hex colour, `rgb()`, `rgba()`, `hsl()`, pixel, point, em, rem or percentage literal appears in any widget CSS. A percentage that varies with data is bound with `ng-style` from a server-computed value, never written as a literal.
- [ ] No `font-size` declaration appears in any widget CSS **except on SVG text**, where there is exactly one: `.bst-charts .bst-charts-svg .bst-charts-text`. Everywhere else type size comes from the Bootstrap heading elements and utility classes. The exception is stated because SVG text is the one place where no Bootstrap class can supply the size — `.h1` through `.h6`, `.small` and `.lead` all set a size on an HTML element, and none of them targets an SVG `<text>` node, which takes its size from the inherited CSS `font-size` and nothing else. The declaration is therefore unavoidable, and it names the **token** `$font-size-large`, so no measured literal enters the stylesheet.
- [ ] No `!important` appears in any widget CSS.
- [ ] The theme's CSS-variables field is the single site where a value is written. Every other literal is a defect.

### Library components over raw HTML

- [ ] `.btn` — with `.btn-primary`, `.btn-default` or `.btn-link` — rather than a styled `<div>` or an unclassed `<button>`.
- [ ] `.form-control` inside a `.form-group`, and `.input-group` with `.input-group-btn` where a button sits against the field, rather than a bare `<input>`.
- [ ] `.nav.nav-tabs` with `.tab-content` and `.tab-pane` rather than a hand-rolled tab control.
- [ ] `.table.table-striped.table-hover` inside `.table-responsive` rather than an unclassed `<table>`.
- [ ] `.panel.panel-default` with `.panel-heading`, `.panel-title` and `.panel-body` rather than a bare container.
- [ ] `.list-group` with `.list-group-item` for key-and-value detail lists.
- [ ] `.label.label-primary` and `.label.label-default` for status, category and multi-valued chips, assigned by [One chip class per logical field type](#one-chip-class-per-logical-field-type) and never by which template is being written.
- [ ] `.media` with `.media-left`, `.media-body` and `.media-heading` for a result card.
- [ ] `.alert` with `.alert-info`, `.alert-warning` or `.alert-danger` for every notice.
- [ ] `.breadcrumb`, rendered by the stock Breadcrumbs widget, for the trail.
- [ ] The stock **Data Table from Instance Definition** widget wherever a plain paginated record list suffices, rather than a bespoke widget.

### One chip class per logical field type

**A field renders in the same chip class on every surface it appears on, and the class is decided by what the field means rather than by which template is being written.** Four widgets render `Startup.industry`, three render `FundingRound.round_type`, and two render `Startup.institutional_funding_last_5yrs`. Without a single assignment the same value acquires a different treatment on each surface, and a reader who has learned that a blue chip means a stage has to unlearn it one page later. The assignment below is the whole of it.

| Logical field type | Chip class | Every field of that type in this portal |
| --- | --- | --- |
| A **state** — where the record currently sits in a lifecycle | `.label.label-primary` | `Startup.funding_stage`, `FundingRound.round_type`, `JobPosting.active` rendered as `Open`, `Investor.type`, the caller's effective role, an entitlement's `Granted` |
| A **category or attribute** — a classification the record carries | `.label.label-default` | `Startup.industry`, `Startup.employee_count_range`, `Startup.institutional_funding_last_5yrs` rendered as `Yes` or `No`, `Founder.title`, `Executive.title`, `JobPosting.remote_type`, `Investor.focus_areas`, a participating investor's name, a chart bucket's count, `No role`, `Not granted`, a withheld field's label in the upsell list |
| A **withheld premium value** | `.label.label-info` | Reserved. The word `Premium` and nothing else — see [Upsell substitution](#upsell-substitution) |

Four rules follow, and each names the defect it prevents:

- [ ] **A field carries one class portal-wide.** `Startup.industry` is `.label-default` on the result card, in the profile header, in the investor's portfolio table and nowhere as plain text; `FundingRound.round_type` is `.label-primary` in all three of its tables.
- [ ] **A True/False field renders as a `Yes` or `No` chip, never as its stored value.** `RestResponseBuilder.valueOf()` returns a boolean field as a JavaScript boolean, so `{{record.field}}` renders the literal `true` or `false` — which is a value from the database rather than an answer to the reader's question. Both surfaces that render `institutional_funding_last_5yrs` use `{{… ? 'Yes' : 'No'}}` inside a `.label-default`.
- [ ] **A figure is not a chip.** `Investor.portfolio_count`, `Investor.aum_usd`, `Startup.total_funding_usd`, `Startup.founded_year` and every currency and count render as text, because a chip reads as a classification and a quantity is not one. The one deliberate exception is a chart bucket's count, which is a legend beside its bar rather than a figure in a sentence.
- [ ] **`.label-info` is never used for data.** It marks a value the caller may not read, so a category rendered in it would read as withheld.

### Layout through system primitives only

- [ ] Page composition uses the `sp_container` → `sp_row` → `sp_rectangle` → `sp_instance` model and nothing else.
- [ ] Layout inside a widget uses `.container`, `.row` and `.col-md-*` / `.col-lg-*`.
- [ ] The column spans in any one row total 12.
- [ ] **Never** apply a custom `display: flex`, `display: grid`, `float` or absolute-position rule to a raw `<div>` to achieve a layout the grid already provides.
- [ ] **One exception, and it is the only one:** `bst-trends-kpi` sets `display: flex` with `flex-wrap: wrap` and `align-items: stretch` on its own `.row`, above `$screen-md-min`. **Equal-height columns are not a layout the Bootstrap 3 grid provides** — the grid is float-based, and a float clears every preceding float or none, so a row containing one taller panel cannot wrap cleanly. The rule replaces nothing the grid does; it supplies the one thing it cannot. Any further use of a custom `display` on a grid element is a violation, and the widths stay on `.col-md-*` / `.col-lg-*` classes rather than moving into flex properties.

### Responsive stance — the 1024-pixel floor

- [ ] **1024 pixels is the supported viewport floor of this portal.** Viewports below it are out of scope.
- [ ] Use **medium and large column classes only**: `.col-md-*` and `.col-lg-*`.
- [ ] Author **no** extra-small or small refinement: no `.col-xs-*`, no `.col-sm-*`, no `.hidden-xs`, no `.visible-sm-*`, and no media query keyed to `$screen-xs-min` or `$screen-sm-min`.
- [ ] On every `sp_rectangle`, set `size_md` and `size_lg` and leave `size`, `size_xs` and `size_sm` empty.
- [ ] Verify the walkthrough at 1024 pixels wide and above. A narrower viewport is not a defect.

The mechanic is stated here; the decision behind the floor is recorded in [`../../../docs/decisions/DECISION_LOG.md`](../../../docs/decisions/DECISION_LOG.md).

#### Overflow guards at the floor

**A floor is a promise about the narrowest supported viewport, and it is only kept if the widest possible *data* also fits.** Three columns can carry a value far wider than the column that renders it, and each is guarded explicitly rather than left to the browser:

| Value | How wide it can be | Guard | Where |
| --- | --- | --- | --- |
| `x_bst_startuptrk_startup.logo_url` | The image behind it has no declared dimensions at all. A 2000-by-50 wordmark satisfies a height cap and stays two thousand pixels wide. | `max-height: $navbar-height` **and** `max-width: $navbar-height`, with `width: auto` and `height: auto` so the image scales inside that box rather than being squashed into it. | `.bst-results .media-object` and `.bst-company .bst-company-logo` |
| `x_bst_startuptrk_startup.website`, `x_bst_startuptrk_investor.website` | 255 characters, and a URL has no spaces, so it is one unbreakable word. | The link is labelled **`Visit the company website`** and **`Visit the investor website`** rather than with the address itself. The address remains the `ng-href` target. | The Website row of the company and investor overview list groups |
| `name` at 100, `title` at 150, news `title` and `summary` at 255 | Any of them may arrive with no space in it. | `overflow-wrap: break-word` on the containers that render them. | `.bst-results .media-body`, `.bst-company .list-group-item`, `.bst-company .media-heading`, `.bst-investor .list-group-item` and `.bst-account .list-group-item` |
| Any value rendered in a `.pull-right` inside a `.list-group-item` — `aum_usd` as `$1,250,000,000`, a four-or-more-value `focus_areas` chip set, `employee_count_range`, a `sys_user` name | Wide enough to wrap onto a second line inside the float, at any viewport where the column is narrow. `Investor.focus_areas` is a multi-choice over six values, so the widest legitimate value is all six chips. | `display: flow-root`, which establishes a block formatting context so the float's full height is counted. | `.bst-company .list-group-item`, `.bst-investor .list-group-item` and `.bst-account .list-group-item` |
| `x_bst_startuptrk_investor.focus_areas` rendered as a chip run — the only multi-valued field in any list item | Six chips measure about 342 pixels. The column's content box is about 291 at the `md` tier, so the run is wider than the box it sits in. | `display: inline-block` on the chip, which is what makes the run breakable at all, plus `text-align: right` on the float so the wrapped run stays where the float put it. | `.bst-investor .list-group-item .label` and `.bst-investor .list-group-item .pull-right` |

**Float containment is a different guard from word breaking, and the two are not interchangeable.** `overflow-wrap: break-word` decides where a single unbreakable *word* may be split; it has nothing to say about a float. A `.pull-right` is `float: right`, so it is out of normal flow and contributes no height to the item that contains it. While its content fits on the label's own line the item looks correct by accident. The moment the content needs a second line the float extends below the item's box, the item keeps the height of its label line alone, and the next `.list-group-item` — which has an opaque background and paints later in document order — covers the overhanging half. The value is not pushed aside, it is **occluded**: the reader sees the top half of a figure and no indication that a bottom half exists. Establishing a block formatting context on the item makes the float's height part of the item's height, which is the only thing that fixes it; neither `overflow-wrap` nor a wider column does. Verify it by measuring rather than by eye — see the checklist row under [Overflow guards at the floor](#overflow-guards-at-the-floor).

`display: flow-root` is a permitted value under [Design system](#design-system): it names a containment behaviour rather than a measured length, in the same way `overflow-wrap: break-word` does, and it is not a substitute for a layout the grid provides. The grid lays out columns; nothing in it contains a float inside a list item.

**Containing the float vertically does not narrow it, and the horizontal half has its own cause.** A float's width is shrink-to-fit — `min(max(min-content, available), max-content)` — so it is *floored at its min-content width* and will exceed its container whenever min-content does. Bootstrap's `.label` carries `white-space: nowrap`, which forbids a break **inside** a chip; and `ng-repeat` clones its element with **no whitespace text node between the clones**, so there is no break opportunity **between** chips either. The whole six-chip run is therefore one unbreakable inline box: min-content equals max-content, the float is forced to its full width inside a narrower column, and because it is right-floated the excess hangs off the **left**, which in a left-to-right document produces no scrollbar and cannot be scrolled to. Measured on the delivered markup: min-content and max-content are both 355 pixels as authored, and injecting a single space between two chips collapses min-content to 72. So the fix is to restore the break opportunity — `display: inline-block` makes each chip an atomic inline-level box, between which a line may break, min-content falls to the widest single chip, and the run wraps inside the column. Three other candidates were measured and rejected: `max-width: none` and `display: inline-block` on the float itself are provable no-ops, rendering byte-identically to no fix at all, because the float's `max-width` is already `none` and `float: right` blockifies `inline-block` straight back to `block`; and making the item a flex container relocates the overhang from the left to the right without ever wrapping the run, and would additionally have to *replace* the `display: flow-root` above rather than sit beside it.

Two further guards are already in place for the same reason and are recorded here so they are not removed as redundant: every wide table is wrapped in `.table-responsive`, which scrolls the table rather than the page; and the inline SVG chart carries `width="100%"` with a `viewBox`, so it scales to its column instead of overflowing it.

**A concise link label is the accessible choice as well as the narrow one.** A screen reader announcing a 255-character address character by character conveys nothing a caller can act on, whereas `Visit the company website` states the destination. Nothing is hidden: the address is still the link target, and an administrator reads the stored value on the platform form view.

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
| **G1** | Charts on the Dashboard / Trends route | Both mechanics are built in [`bst-trends-charts`](#bst-trends-charts) and the `render_mode` option selects between them: `svg` renders the Angular-bound inline SVG bar chart specified under [The inline SVG chart](#the-inline-svg-chart), `report` embeds one of **two allowlisted, protected, count-only** saved reports per [The report embed](#the-report-embed). `svg` is the shipped mode on both dashboard instances, and `report` falls back to it whenever the allowlist, the count-only check or the reporting-widget check does not pass. |
| **G2** | Multi-select chip input for `x_bst_startuptrk_investor.focus_areas` | **Read-only in this portal:** `.label` chips inside a `.panel-body`, built in [`bst-investor-profile`](#bst-investor-profile). The **write** path is the platform's own form view on `x_bst_startuptrk_investor`, which renders the choice-backed multi-select natively and is reached from the application menu — not the stock **Form** widget, which this portal places nowhere and opens nowhere. |
| **G3** | Loading indicator, replacing the legacy circular progress component | Service Portal's own loading indicator, or `.progress` containing `.progress-bar.progress-bar-striped.active`. The striped form is built in [`bst-startup-results`](#bst-startup-results). |
| **G4** | Card media, replacing the legacy card-media component | `.media-left` containing `img.media-object`, bound to `x_bst_startuptrk_startup.logo_url`. `.thumbnail` is the alternative container. Built in [`bst-startup-results`](#bst-startup-results) and in the company-profile header. |
| **G5** | Premium upsell and paywall treatment for `x_bst_startuptrk.user` | **Two forms, one each per granularity.** In the denied field's own position: `<span class="label label-info">Premium</span>`. Once per surface that has any denied field: `.alert.alert-info` carrying a `.btn.btn-primary`, packaged as [`bst-premium-upsell`](#bst-premium-upsell) and embedded by its three hosts, with [`bst-startup-results`](#bst-startup-results) rendering the same notice inline. Never a blank, an empty cell, a zero or a dash. See [Upsell substitution](#upsell-substitution). |
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
| **Form** (`sp-form`) | **Available, and placed on no page and opened by no widget in this build.** The administrative write path is the platform's own form view on the scoped table, not a portal surface — see the paragraph below this table | Bootstrap form classes | `table` and `sys_id`, were one ever placed. |
| **Report / chart widget** | Embedded by `bst-trends-charts` when `render_mode` is `report` | — | The saved report identifier. |

A stock widget is instantiated, never edited. Editing a stock widget changes it for every portal on the instance. Where a stock widget needs different behaviour, clone it into the `x_bst_startuptrk` scope under a `bst-` name and edit the clone.

**No write path is built inside this portal, by any widget, for any role.** All eight widgets are read-only: every server script opens `GlideRecordSecure` for reading and none calls `insert()`, `update()` or `deleteRecord()`. An administrator who needs to edit a record uses the platform's own form view on the scoped table, reached from the application menu the Update Set delivers — which is also how the administrative surface is served without a sixth portal route, as [Step 3](#step-3--the-five-pages) states. That is deliberate and it is what layer 2 of the access controls expects: `write`, `create` and `delete` are granted to `x_bst_startuptrk.admin` alone, so a form presented to `x_bst_startuptrk.user` or `x_bst_startuptrk.premium_user` would offer a save control the platform then refuses. The row above therefore records the **Form** widget as available and unplaced; placing one is a change to this guide, not a detail of it.

## Step 6 — Access control in every widget server script

Do not soften any item in this section. The portal and the REST API must not disagree about what a role may see, and the only way to guarantee that is for both to use the same read path and the same serialiser.

### The secured read path

- Every caller-facing read in every widget server script uses **`GlideRecordSecure`**. Never `GlideRecord`.
- Ordinary record access does not guarantee access-control enforcement on a server-side read; the secured variant does.
- The complete list of paths in this application that read through the unsecured `GlideRecord` is in [`../access-control.md`](../access-control.md), and **no widget is on it**. A widget server script that opens a `GlideRecord` is a defect.
- No count is an exception. Produce every count with `RestResponseBuilder.countState()` or `RestResponseBuilder.countWith()`, which apply the `hasAnyAppRole()` role gate — the exact set of roles the layer-1 table read controls grant — and then take one aggregate `COUNT`. **Do not write an aggregate query of your own in a widget**: a bare `GlideAggregate` skips the gate and reports the size of a set the caller may not read. `countState()` reports a denial as `denied`; `countWith()` answers `0`, so use it only where the widget already withholds every figure from an unauthorised caller.
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

**The treatment has exactly two forms, and which one applies is decided by granularity, not by taste.** Both are always present together on a surface that has a denied field: the marker says *which* value is withheld, the partial says *why* and *what to do*. Neither substitutes for the other, and neither is repeated at the other's granularity.

| Granularity | The one form | Rendered | Never |
| --- | --- | --- | --- |
| **Field** | `<span class="label label-info">Premium</span>` | Once in **each** denied field's own position — the table cell, the list-group row or the list item where the value would have been | Not an alert, not `.label-default`, and not a blank, an empty cell, a zero or a dash |
| **Surface** | `bst-premium-upsell` — one `.alert.alert-info` carrying one `.btn.btn-primary` | **Once per surface**, at the end of it, when *anything* on that surface is denied | Not once per denied field, and not once per denied column |

- **The marker is `.label-info`, at every one of the twelve field positions that can render it — two in `bst-startup-results`, four in `bst-company-profile` and six in `bst-investor-profile`.** Not `.label-default`, which this portal uses for a *category* — a job title, a seniority, a working pattern, a focus area — and which would make a withheld value read as one more attribute of the record. The two are visually distinct by design, and `$label-info-bg` is chosen for AA contrast against `$label-color` under [The contrast check](#the-contrast-check).
- **The partial renders once for the surface, gated on one flag.** `data.gatedAny` on `bst-company-profile` and `bst-investor-profile`, and the equivalent on `bst-account-summary`; each host embeds it with `$sp.getWidget()` and renders it as a single `<sp-widget>` at the end of the widget, outside every `ng-repeat`. An upsell inside a repeat would render once per row.
- **`bst-startup-results` is the one surface that renders its own notice inline** rather than embedding the partial, for the reason given under [`bst-startup-results`](#bst-startup-results): it is the only host that is not one of the partial's three declared hosts. Its notice is the same `.alert.alert-info` with the same `.btn.btn-primary`, rendered once after the result list — the pattern is identical, only the packaging differs.
- **Render no blank, no empty cell, no zero and no dash where a premium field was denied.** An empty cell is indistinguishable from a genuinely empty column and hides the entitlement boundary from the caller.
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
| *no legacy equivalent* | Modal dialogue | **Nothing in this portal opens one.** `spModal` is part of the framework and is listed under [`spModal`](#spmodal) as available, with the reason no widget calls it. |
| *no legacy equivalent* | Administrative write form | **Not a portal surface.** The platform's own form view on the seven scoped tables, reached from the application menu the Update Set delivers. No `sp-form` instance and no `spModal` appears in this portal. |

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
- [ ] **Every published member has a consumer, and every consumed member is published.** For each of the eight widgets, read its **Data contract** table against its own server script, controller and template: every member the table names is assigned by the server item it names, and every `data.` expression in the controller and the template names a member in the table. The only expression exempt is `data.error`, which the shared `c.load()` helper sets on the client. A template expression naming an unpublished member is the failure this check exists to catch: Angular renders it as empty, so the widget looks merely sparse rather than broken.
- [ ] **Bounded child collections state their size.** On a company with more funding rounds than `funding_limit`, the Funding pane renders the caption `Showing N of M, the L most recent`, and the same holds for the People, Jobs and News panes against their own limits. Each of the five collections is published as `{rows,total,limit,truncated}`, and **no pane renders `rows` without its `total`**. On the investor profile the two rounds tables carry the same caption from their own `Total`, `Limit` and `Truncated` members, and the portfolio panel states its cap against `data.investor.portfolio_count`.
- [ ] **The tab badges agree with the panes.** Each of the four collection tabs carries a `.badge` whose number equals the `total` of the collection its pane renders, **People** carries the sum of the founders and executives totals, and **Overview** carries no badge.
- [ ] **Pagination at zero.** Search for a name that matches nothing. The pager reads `No results to show` and never `1 to 0 of 0`, and **Next** is disabled.
- [ ] **Tabs.** On the company profile, exactly one tab control carries `tabindex="0"` and `aria-selected="true"` at a time; each control's `aria-controls` resolves to the `id` of its own pane; and `ArrowRight`, `ArrowLeft`, `Home` and `End` all move the selection and the focus together. Tab moves out of the strip, not through it.
- [ ] **Nothing overflows at 1024 pixels, with the widest data the schema permits.** Seed one startup whose `logo_url` is a 2000-by-50 wordmark, whose `website` is 255 characters, and whose `name` is 100 characters with no space in it; seed one job posting with a 150-character title and one news article with a 255-character title. At a 1024-pixel viewport no card, panel, table or list item is wider than its column, and no horizontal scrollbar appears on the document. The guards are listed under [Overflow guards at the floor](#overflow-guards-at-the-floor).
- [ ] **No floated value escapes its list item, at the floor, with the widest data the schema permits.** For every `li.list-group-item` that contains a `.pull-right`, on the company, investor and account overviews, measure `floatRect.bottom − liRect.bottom`. It must be **negative** on every row. A positive value means the item is not a block formatting context and the value's second line is hanging below the row, where the next item's opaque background covers it — the reader then sees the top half of a figure with nothing to indicate a bottom half exists. Probe the 992-to-1199 pixel band directly rather than by zooming out: at 200 percent zoom a 1024-pixel viewport becomes a 960-pixel one, which is below the `md` breakpoint, so the columns stack full-width and the defect disappears without being fixed.
- [ ] **The widest chip run fits its column.** Seed an investor with all six `focus_areas` values and read the `.pull-right` in that row at a 1024-pixel viewport. Its `left` must be **greater than or equal to** the column's content-box left, and the chips must occupy two or more lines. A float `left` below zero means the run is unbreakable and part of it is off the left edge of the window, which no scrollbar can reach, so the value is permanently unreadable rather than merely awkward.
- [ ] **Every data table names itself and its axes.** All six tables — funding rounds and open roles on the company profile, portfolio and the two rounds tables on the investor profile, and the chart's companion table — carry a `<caption class="sr-only">`, a `scope="col"` on every column header, and a `<th scope="row">` as the first cell of every body row. No `<th>` without a `scope` appears in any template.
- [ ] **Each state is announced once, by one region.** With the error panel showing — `c.errorText()` returning a message — only the visible `.alert.alert-danger[role="alert"]` announces; `c.statusText()` returns the empty string and the polite region says nothing. Confirm with a screen reader that a failed load is announced once, not twice.
- [ ] **No static notice claims to be an alert.** `bst-premium-upsell` and the results premium notice are `role="region"` with an `aria-labelledby` pointing at their own heading. Search the eight templates for `role="alert"`: it appears only on the six error panels, each of which is rendered in response to a failure.
- [ ] **One submit control per form.** `bst-startup-search` renders exactly one `type="submit"` button — the `.input-group-btn` beside the name field — and one `type="button"` **Clear**. Tab through the form and confirm a screen reader announces `Search, button` once, not twice.
- [ ] **One `h1` per page, and no skipped level.** Each of the five routes renders exactly one `<h1>` — the `.panel-title` of `bst-startup-search` on `bst_home`, the `.media-heading` carrying the company name on `bst_company`, the `.panel-title` carrying the investor name on `bst_investor`, the `<h1 class="h2">` of `bst-trends-kpi` on `bst_dashboard`, and the `.panel-title` of `bst-account-summary` on `bst_account`. Read the outline with the browser's accessibility tree and confirm it descends `h1` → `h2` → `h3` with no level skipped and no second `h1`. The owners are listed under [Heading hierarchy](#heading-hierarchy).
- [ ] **One `h1` per page in every state, not only the loaded one.** On `bst_company` and `bst_investor`, drive each of the four states in turn — loaded, unauthorised, not found and a failed load — and confirm `document.querySelectorAll('h1').length` is **1** on all four. The record-bound heading and the static `Company profile` / `Investor profile` heading are gated on exact complements, so a count of `0` means one gate is wrong and a count of `2` means they overlap.
- [ ] **The retry handoff has a destination during the failure it is retrying.** With `data.error` set, confirm the static `h1.h2` is in the document and carries `tabindex="-1"`, then press **Retry** and confirm focus lands on a heading rather than on `document.body`.
- [ ] **Focus is never lost to the document body, and the destination is visible when it arrives.** Three interactions remove the control that holds focus: **Retry** when a retry succeeds, the **Next** pager button when it becomes the last page, and **Previous** when it becomes the first. Drive each and read `document.activeElement` afterwards: it must be an element inside the acting widget, never `document.body`. Then screenshot the destination while it holds focus and confirm a ring is visible — a programmatic move with no indicator relocates the reading position and says nothing about it. Measure the ring against its background: at least 3:1.
- [ ] **The indeterminate bar paints.** During the busy window on `bst-startup-results`, `bst-company-profile` and `bst-investor-profile`, read the `.progress-bar.progress-bar-striped.active`'s rendered width. It must equal its trough's width, not zero. `document.elementFromPoint()` at the trough's centre must return the bar rather than the `.progress` track behind it. Bootstrap ships `.progress-bar { width: 0% }`, so a bar with no bound width animates its stripes across nothing at all.
- [ ] **SPACE activates every control that looks like a button.** Tab to each of the seven `a.btn` controls — **View profile** on each result card, the results upsell call to action, **Back to search** on the company, investor and account widgets, **Browse startups** on the KPI panel, and the upsell partial's call to action — and press SPACE. Each must activate, and `window.scrollY` must not change: an unhandled SPACE scrolls the page and activates nothing, which is the opposite of what a caller pressing a button expects. Then press ENTER on each and confirm the same result.
- [ ] **The three search controls show a focus ring that can be seen.** Focus the name input, the industry select and the location input in turn and measure the computed `outline` against the adjacent background. Bootstrap's own `.form-control:focus` sets `outline: 0` and substitutes a pale blue border and glow measuring 2.37:1 against white and 1.47:1 against the unfocused border, so both readings of the non-text contrast requirement fail unless the ring is restored.
- [ ] **Error gating is substitutive on every widget, not additive on some.** Set `data.error` on each of the six widgets that carry a **Retry** and confirm that the stale content is **gone** rather than sitting under the error alert: on `bst-startup-results` no `.bst-results-card`, no upsell and no pager; on `bst-account-summary` no identity panel, no entitlements and no upsell, with only the **Back to search** escape hatch remaining. A widget that leaves its previous result set on screen beside a failure tells the caller that data is current when it is not.
- [ ] **Every figure and every date is formatted by the widget.** Read every currency, date and count position listed in [The display contract](#the-display-contract) and confirm none renders a raw stored value: no `USD;` prefix anywhere, no bare ISO date, and a thousands separator on every four-digit-or-larger figure. Check the KPI panel and a four-digit chart bucket **together** — if one separates and the other does not, the formatting is coming from the payload rather than from the portal, and it will diverge again on the next record.
- [ ] **The visible input, the model and the URL agree.** Type a value with leading and trailing spaces into the name field, submit, then compare the input's `value` property, the Angular model and the decoded URL parameter. All three must be the trimmed value. AngularJS trims into the model by default, which makes the model and the URL agree while leaving the visible field untrimmed — a three-way divergence in which the field shows something the search did not use, so the two text inputs carry `ng-trim="false"` and the submit-time trim writes back through the model.
- [ ] **No heading element carries a value or is used for size.** The KPI figure is a `<p class="bst-kpi-value h2">`, not an `<h2>`. Search the eight templates for a heading element whose content is a number or a bare field value: there must be none.
- [ ] **Progress bars are named.** Every `role="progressbar"` carries a name, and every determinate bar in `bst-trends-charts` also carries `aria-valuenow`, `aria-valuemin` and `aria-valuemax`.
- [ ] **Every announced progress value is inside its declared range.** Read `aria-valuenow` off every `.progress-bar` in both `bst-trends-charts` instances and confirm each is between the `aria-valuemin` and `aria-valuemax` on the same element. A figure outside that range means the server published an unclamped `bucket.share`; the geometry can look correct while this is broken, because the width attribute and the ARIA value are separate bindings.
- [ ] **Decorative glyphs are hidden.** Every `.icon-*` span carries `aria-hidden="true"`.
- [ ] **The chart draws.** With `render_mode` `svg`, `bst-trends-charts` renders an `<svg role="img">` whose `viewBox` attribute is present and camel-cased, with one `<rect>` per bucket and a `<title>` and `<desc>` whose `id` values differ between the dashboard's two instances.
- [ ] **The chart honours its aspect ratio at the 1024-pixel floor.** At a 1024-pixel viewport the `<svg>` fills the width of its `col-md-6` column, and its rendered height is that width divided by the viewBox's own aspect ratio rather than the bound `data.chart.height` — so the drawing fills the box on **both** axes and no band of empty canvas is left below it. Measure it: `rect.height / rect.width` must equal `viewBoxHeight / 720` to within a pixel, and the drawing's ink must reach the bottom of the box. No widget CSS declares `width` on `.bst-charts-svg` — the width comes from the element's `width="100%"` attribute — while `height: auto` **is** declared and deliberately overrides `ng-attr-height`, which remains on the element as the no-CSS fallback. No bar is clipped at either end.
- [ ] **The zero line is drawn and every bar starts on it.** One `<line class="bst-charts-axis">` per chart, at `x = data.chart.labelWidth`, spanning the full viewBox height. Confirm each `<rect>`'s `x` equals that same value, so a bucket of `0` reads as a mark on the line rather than as nothing at all.
- [ ] **Each count sits beside its own bar.** For every bucket, the value `<text>`'s `x` equals `data.chart.labelWidth + barWidth + 12`, so the gap between a bar's end and its number is one `BAR_GAP` on every row rather than a fixed column the short bars never reach.
- [ ] **The companion table's bars are visible.** Sample the fill of any `.bst-charts-bar .progress-bar`: it must be `rgb(25, 118, 210)` on an `rgb(245, 245, 245)` track — the `$progress-bar-bg` and `$progress-bg` pair that row 19 of [The contrast check](#the-contrast-check) measures at 4.22:1. A white fill means a widget rule has reintroduced `background-color: currentColor`, which on a `.progress-bar` resolves against Bootstrap's own `color: #fff`.
- [ ] **Two clean KPI rows, and no ragged edge.** At any viewport at or above 992 pixels, with five panels, read every KPI column's rect: there must be exactly **two** distinct `top` values, the second row must start at `left` equal to the first column's `left`, and every column on a row must report the same `height`. Three distinct `top` values means the flex rule under [`bst-trends-kpi`](#bst-trends-kpi) is not in force and the float staircase is back.
- [ ] **Both dashboard widgets state an initial failure.** Temporarily rename `RestResponseBuilder` so `countWith()` and `countByGroup()` throw, then load `bst_dashboard`. `bst-trends-kpi` and `bst-trends-charts` each render one `.alert.alert-danger` with a working **Retry**, and neither renders an empty panel, a zero, nor a chart with no bars. Restore the name and use Retry: both widgets render their figures without a page reload.
- [ ] **Both dashboard widgets state an initial failure.** Temporarily rename `RestResponseBuilder` so `countWith()` and `countByGroup()` throw, then load `bst_dashboard`. `bst-trends-kpi` and `bst-trends-charts` each render one `.alert.alert-danger` with a working **Retry**, and neither renders an empty panel, a zero, a chart with no bars, nor the "No startup is recorded for this breakdown yet" notice — a data-availability message may never stand in for a failure.
- [ ] **A failing retry stays recoverable, and a succeeding one repaints.** With the name still renamed, press **Retry** on each widget. The aggregate fails again, and each widget **still** renders its `.alert.alert-danger` and its **Retry** button — a widget left showing only its heading, with no figures, no error and nothing to press, is the failure this step exists to catch. Now restore the name and press **Retry** again: the panel disappears and the figures and bars appear, without a page reload. Both directions are required; a widget that recovers only on reload fails this step.
- [ ] **The chart falls back on an unconfigured report.** Set `render_mode` to `report` with an empty `report_id`. The widget renders the warning alert and the SVG chart, not an empty panel.
- [ ] **The chart falls back on a report outside the allowlist.** Set `render_mode` to `report` and `report_id` to a readable report whose `title` is not one of the two allowlisted names — any stock report will do. The widget renders the warning alert and the SVG chart, and embeds nothing. Repeat with an allowlisted report whose `aggregate` has been changed away from `COUNT`: same result. Neither case may embed.
- [ ] **The chart falls back when the reporting widget is absent.** Set `render_mode` to `report` and `report_id` to an allowlisted report, then temporarily rename the `report-chart` widget's `id`. The widget renders the warning alert and the SVG chart rather than a blank panel or a server error. Restore the `id` afterwards.
- [ ] **No allowlisted report aggregates a premium column.** For each of the two allowlisted reports, confirm `aggregate` reads `COUNT`, no aggregation-source field is populated, and `sys_policy` is `protected` so it cannot be edited into a `SUM` after acceptance.
- [ ] **The premium treatment appears in the result list.** Under `x_bst_startuptrk.user`, each result card states `Total funding` beside a `Premium` marker, and the list is followed by exactly one `.alert.alert-info` carrying a `.btn.btn-primary` to `bst_account`.
- [ ] **The account page tells the truth.** It renders the human role label — `Administrator`, `Premium subscriber`, `Free user` or `No role` — and it offers no control that claims a request was recorded.

### Design system

- [ ] Every one of the **54** theme variables under [The CSS-variables field](#the-css-variables-field) is declared with the literal value that table gives. No value the portal applies is left to a release default — **including every component foreground**, which is where a release default most easily hides.
- [ ] **Every text pair the portal renders reaches WCAG 2.1 AA.** Run the check under [The contrast check](#the-contrast-check) and confirm it prints `FAILURES: 0`. Then confirm on the rendered portal, with the browser's colour picker, that a `Premium` marker is white on `#17607d` and not white on `#5bc0de`, that `.text-muted` is `#595959` and not `#777777`, and that a tab-strip `.badge` is white on `#595959` and not white on `#777777`. Those three release defaults measure 2.09:1, 4.11:1 and 4.48:1, and all three fail.
- [ ] No widget CSS contains a literal colour, spacing, radius or font value. The only literals present are `0`, `none`, `auto`, `inherit`, `currentColor` and `transparent`. The inline SVG chart's coordinates are **not** CSS: they are server-computed and bound with `ng-attr-*`.
- [ ] No `.col-xs-*` or `.col-sm-*` class appears in any widget template, and no `size`, `size_xs` or `size_sm` is set on any `sp_rectangle`.
- [ ] The walkthrough was performed at 1024 pixels wide and above, the declared floor.
- [ ] No Lucide reference and no emoji character appears in any widget template, CSS field, client controller, option label or option default.
- [ ] Every icon is a platform glyph-font `.icon-*` class.
- [ ] No repository manifest was created or edited.

### Access control

- [ ] Every widget server script reads records through `GlideRecordSecure` and serialises through `RestResponseBuilder.serialize()`. No widget opens a `GlideRecord`, and no widget writes an aggregate inline — every count goes through `countState()`, `countWith()` or `countByGroup()`.
- [ ] No widget aggregates a premium-gated column, and no widget publishes a monetary total.
- [ ] Every child collection on the company profile and the investor profile is read under a limit, each publishes its exact total alongside the rows it rendered, and **every collection whose total exceeds the rows it rendered displays a showing-N-of-M caption**. Seed one company with more job postings than `jobs_limit` and one investor with more join rows than `rounds_limit`, and confirm both captions appear with the true totals. A truncated list with no caption is a wrong answer, not a short one.
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
- [ ] On `bst_company` and `bst_investor`, trigger a server refresh three times on a resolvable record. Each refresh resolves the same `sys_id`, so `startWatch()` returns without touching the subscription and the widget still holds exactly one `recordWatch`. Then navigate to a second record of the same type and confirm the first subscription stopped delivering — the child scope carrying it was destroyed. No step asserts a released handle: `spUtil.recordWatch()` answers a promise, and scope destruction is the release.

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
- [`../validation-gates.md`](../validation-gates.md) — the eleven required post-commit gates that are precondition 4, and the four further acceptance-required checks that are not
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
