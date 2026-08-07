# Manual build 01 — Connection & Credential Aliases — `x_bst_startuptrk`

This guide establishes the **two** Connection & Credential Aliases that the two ingestion flows of the ServiceNow scoped application `x_bst_startuptrk` authenticate through: `x_bst_startuptrk.crunchbase_api` and `x_bst_startuptrk.linkedin_oauth`. For each alias it states the navigation path, every field on the alias record, every field on its connection record, every field on its credential record, the OAuth provider and profile records the second alias additionally requires, the mandatory connection test, and the name-propagation step that carries both alias names into the two flow guides.

The aliases are **verified and bound**, not created. The live Crunchbase and LinkedIn credentials are provisioned on the instance by their owner before this guide runs. Every step below locates an existing record, confirms its identifiers and bindings, and tests it. **No step places a credential value, and no credential value appears anywhere in this file.**

**Authority.** The frozen prompt and the Agent Action Plan are authoritative for all application content. The Update Set XML at [`../../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml`](../../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml) is the authoritative source for the scope name and for the two non-secret base-URL system-property keys cited below; the identifiers used here match those records character for character, and the same alias names appear in [`../api-reference.md`](../api-reference.md), [`../deployment-runbook.md`](../deployment-runbook.md) and [`../../sample-data/README.md`](../../sample-data/README.md). No variant spelling of any identifier is valid. The platform table, column and choice identifiers below are those of the target instance release.

This document carries **no rationale**. It states what to verify and how. Every decision behind these aliases — the authentication type chosen for each source, and the verify-and-bind posture in place of creation — is recorded in [`../../../docs/decisions/DECISION_LOG.md` (planned)](../../../docs/decisions/DECISION_LOG.md), which is the single source of truth for "why". Requirements with no clean platform equivalent are flagged in [`../gaps-and-flags.md` (planned)](../gaps-and-flags.md) and are not restated here.

Operational warnings **are** in scope for this guide and are marked as such. [Operational warning — the binding is by name](#operational-warning--the-binding-is-by-name) is the most important one in this file and must not be skipped.

## Referenced documents

This guide is executable on its own. Both aliases, every record, every field, the escalation path, the connection test and the completion criteria are stated here in full. An operator needs no other file to run it.

Some documents named below are **planned artifacts of this package**. Every link to one carries the marker **(planned)** in its link text. A statement about a planned document describes what that document is required to contain; it is not a claim that the content can be read from it. The delivered files referenced from here are `../../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml`, `../validation-gates.md`, `../deployment-runbook.md`, `../api-reference.md` and `../../sample-data/README.md`.

**Reviewer.** This guide is the artifact validated by **entry 3 of [`../../../docs/review/CRITICAL_DECISIONS.md` (planned)](../../../docs/review/CRITICAL_DECISIONS.md), risk High, reviewer persona API/Integration**, whose check is to search the delivered Update Set XML for credential material and to confirm both alias names bind before the flows are saved — an obligation placed on this file by the project rule **Critical Decision Review Document**.

## Position in the build order

This is **guide 01 of six**, and it is **step 1** of the execution order below. Nothing in the manual build precedes it. The order is stated in full in [`../manual-build-instructions.md` (planned)](../manual-build-instructions.md); it is repeated here so this guide can be run without it. The execution order is not the filename order: guide **06** runs before guide **05**.

| Step | Guide | Why it sits here |
| --- | --- | --- |
| **1** | **This guide** | **The two Connection & Credential Aliases the ingestion flows bind to by name. Nothing downstream can authenticate without them.** |
| 2 | [`02-flow-crunchbase-ingestion.md` (planned)](02-flow-crunchbase-ingestion.md) | The Crunchbase ingestion flow, which references `x_bst_startuptrk.crunchbase_api` by name. |
| 3 | [`03-flow-linkedin-ingestion.md` (planned)](03-flow-linkedin-ingestion.md) | The LinkedIn ingestion flow, which references `x_bst_startuptrk.linkedin_oauth` by name. |
| 4 | [`04-service-portal-pages-and-widgets.md`](04-service-portal-pages-and-widgets.md) | The portal, theme, five pages and eight widgets. |
| 5 | [`06-staging-table-csv-import.md` (planned)](06-staging-table-csv-import.md) | The staging-table CSV load. |
| 6 | [`05-atf-test-suites.md` (planned)](05-atf-test-suites.md) | The Automated Test Framework suites, **last**, because they exercise everything the five preceding guides build. |

Guides **02** and **03** follow this one immediately and both depend on it. Neither may be started until this guide is complete, for the reason given under [Step 3 — Test both connections](#step-3--test-both-connections).

## Preconditions

Do not begin this guide until every item below holds.

| # | Precondition | How to confirm |
| --- | --- | --- |
| 1 | The Update Set has been uploaded and has reached the `loaded` state. | The `sys_remote_update_set` record shows `state` `loaded`. The upload route is specified in [`../deployment-runbook.md`](../deployment-runbook.md). |
| 2 | The preview has completed with an **empty error-type problem set**. | A read of `sys_update_preview_problem` filtered to this remote update set and `type=error` returns an empty `result` array. Warnings are logged and do not block. |
| 3 | The Update Set has **committed**. | The `sys_remote_update_set` record shows `state` `committed`. |
| 4 | **All sixteen post-commit gates have passed.** | Run every gate in [`../validation-gates.md`](../validation-gates.md) and record `pass` for all sixteen in that document's evidence record. The aggregate pass condition is 16 of 16; there is no partial pass, and no gate may be skipped, deferred or waived. |
| 5 | The **eleven-gate core** within those sixteen has passed. | The seven entity-table gates `GATE-TBL-01` through `GATE-TBL-07`, the three role-record gates `GATE-ROLE-01` through `GATE-ROLE-03`, and the one scope-record gate `GATE-SCOPE-01`. The remaining five are `GATE-COL-01` and `GATE-SEC-01` through `GATE-SEC-04`. All sixteen are required; this row names the eleven so a partial gate run is visible as such. |
| 6 | The two non-secret base-URL properties are on the instance. | `sys_properties` carries `x_bst_startuptrk.crunchbase.base_url` and `x_bst_startuptrk.linkedin.base_url`. Both committed with the Update Set. The full property inventory is in [`../api-reference.md`](../api-reference.md). |
| 7 | You hold the **`admin`** role on the target Personal Developer Instance. | The application picker and the **System Definition** application are reachable. |
| 8 | You have access to the **Connections & Credentials** module. | The **Connections & Credentials** application appears in the navigator with its four modules: **Connection & Credential Aliases**, **Credentials**, **Connections** and **Authentication Algorithms**. That application requires the `credential_admin` and `connection_admin` roles; the `admin` role of precondition 7 contains both. |
| 9 | You have access to the **System OAuth** module. | The **System OAuth** application appears in the navigator with its **Application Registry** and **Manage Tokens** modules. Both require the `oauth_admin` role, which `admin` contains. This precondition applies to [Step 2](#step-2--alias-2-linkedin) only. |
| 10 | The live Crunchbase and LinkedIn credentials have been provisioned on this instance by their owner. | Both aliases resolve at [Step 1.1](#step-11--locate-the-alias-record) and [Step 2.1](#step-21--locate-the-alias-record). If either does not, stop and follow [If an alias is genuinely absent](#if-an-alias-is-genuinely-absent). |

Preconditions 1 through 5 are shared by every guide in this folder. Preconditions 6 through 10 are specific to this one.

### Why this guide exists rather than more Update Set XML

Only tables carrying the update-synch attribute are captured into `sys_update_xml` records, and adding that attribute to a table that lacks it out of the box is unsupported. The alias, connection, credential and OAuth tables are outside the captured set, so these artifacts are established through the platform interface instead. [`../manual-build-instructions.md` (planned)](../manual-build-instructions.md) owns the split rule for the package as a whole.

The consequence is the property this guide exists to preserve: the delivered Update Set contains **zero** credential material and **zero** alias records, and the flows still authenticate.

## Platform constraint

- **Aliases only.** This guide establishes Connection & Credential Aliases, their connections and their credentials. It installs nothing else.
- **IntegrationHub spokes are forbidden.** Prompt section 4.0 binds this absolutely. Do **not** install, activate, reference or open any spoke content set, and do not use a spoke action anywhere in this build. The flows of guides 02 and 03 use generic REST steps bound to the aliases established here.
- **Scope containment.** Prompt section 6.0 forbids modifying anything outside `x_bst_startuptrk`. Every alias, connection and credential record confirmed below must carry the `x_bst_startuptrk` scope, which the platform displays as **Boston Startup Tracker**. Confirm the scope on each record before leaving it.
- **No secret is written.** No step in this guide types, pastes, prints, echoes, logs, screenshots or transcribes a credential value. Where a step confirms that a secret-bearing field is populated, it records only that it is populated.

## What this guide establishes

Exactly two aliases. Neither is created by this guide; both are located, confirmed and tested.

| # | Alias name | Alias type | Credential type | Secret material held by its owner | Base-URL property |
| --- | --- | --- | --- | --- | --- |
| 1 | `x_bst_startuptrk.crunchbase_api` | Connection and Credential | Basic Auth | The Crunchbase API key, in the credential's **Password** field | `x_bst_startuptrk.crunchbase.base_url` |
| 2 | `x_bst_startuptrk.linkedin_oauth` | Connection and Credential | OAuth 2.0 | The LinkedIn OAuth 2.0 client identifier, client secret and refresh token | `x_bst_startuptrk.linkedin.base_url` |

Each alias resolves to a record set of three or six records.

| Alias | Records to confirm |
| --- | --- |
| `x_bst_startuptrk.crunchbase_api` | 1 alias record in `sys_alias`, 1 connection record in `http_connection`, 1 credential record in `basic_auth_credentials`. |
| `x_bst_startuptrk.linkedin_oauth` | 1 alias record in `sys_alias`, 1 connection record in `http_connection`, 1 credential record in `oauth_2_0_credentials`, 1 provider record in `oauth_entity`, 1 profile record in `oauth_entity_profile`, and at least 1 token record in `oauth_credential`. |

The platform names the **Application** field differently on each of the three record classes, and all three must read **Boston Startup Tracker**.

| Record class | Table | Application column |
| --- | --- | --- |
| Alias | `sys_alias` | `sys_scope` |
| Connection | `http_connection`, extending `sys_connection` | `app_scope` |
| Credential | `basic_auth_credentials` and `oauth_2_0_credentials`, both extending `discovery_credentials` | `application` |

## The verify-and-bind rule

This rule governs every step of this guide. Read it before Step 1.

1. **Locate** the record. Do not create one.
2. **Confirm** its **Name** matches the specified value character for character. A near-match is a failure, not a variant.
3. **Confirm** its **Type**, its **Application** scope, and every binding to the other records in its set.
4. **Confirm** that each secret-bearing field is **populated**. Secret-bearing fields are stored encrypted and render masked; that is the expected appearance. Record that the field is populated. Do **not** attempt to reveal, decrypt, copy or transcribe the value, and do not record it.
5. **Test** the connection, and only then treat the alias as established.
6. If the record is missing, or a name does not match, **stop**. Do not create the record, do not rename an existing record to fit, and do not place a credential value. Follow [If an alias is genuinely absent](#if-an-alias-is-genuinely-absent).

A field documented below as *empty* is deliberately blank and must be left blank. A field documented as *as provisioned* holds a value set by the credential owner: confirm it is populated, confirm nothing further about it, and change nothing.

## Step 1 — Alias 1, Crunchbase

The alias name is **`x_bst_startuptrk.crunchbase_api`** and its credential type is **Basic Auth**. Three records are confirmed: the alias, its connection, and its Basic Auth credential.

### Step 1.1 — Locate the alias record

1. Set the application picker to **Boston Startup Tracker**, so that every record you open is read in the `x_bst_startuptrk` scope.
2. In the navigator, open **Connections & Credentials > Connection & Credential Aliases**. The list is the `sys_alias` table.
3. Filter the list on **Name** `is` `x_bst_startuptrk.crunchbase_api`.
4. Confirm the list returns **exactly one** record. Zero records means the alias is absent: stop and follow [If an alias is genuinely absent](#if-an-alias-is-genuinely-absent). More than one record is a duplicate-name condition: stop and escalate by the same route.
5. Open the record.

### Step 1.2 — Confirm the alias record fields

One record in `sys_alias`. Confirm every field in the table below. The **Required value** column is what the field must read; a value of *empty* means the field must be blank.

| Field | Column | Required value | Note |
| --- | --- | --- | --- |
| Name | `name` | `x_bst_startuptrk.crunchbase_api` | Mandatory. **Character for character.** This is the string the Crunchbase flow of guide 02 resolves at run time. |
| Type | `type` | `Connection and Credential` | Mandatory. Stored value `connection`. A value of `Credential`, stored `credential`, carries no connection record and cannot supply the connection URL. |
| Connection type | `connection_type` | `HTTP` | Stored value `http_connection`. This is what makes the connection record an HTTP(s) Connection. |
| Application | `sys_scope` | `Boston Startup Tracker` | The `x_bst_startuptrk` scope. |
| Support Multiple Active Connection | `multiple_connections` | `false` | One active connection serves this alias. |
| Parent Alias | `parent` | *empty* | This alias is not a child of another alias. |
| Default Retry Policy | `retry_policy` | *empty* | Retry behaviour is not set on the alias. |
| Configuration Template | `configuration_template` | *empty* | No template is applied. |
| ID | `id` | *as provisioned* | Platform-managed. Do not edit. |
| Is internal | `is_internal` | `false` | This is not a platform-internal alias. |

Two related lists at the bottom of the alias form carry the rest of the record set:

| Related list | Shows | Confirm |
| --- | --- | --- |
| **Connections** | Records in `sys_connection` whose **Connection alias** names this alias. | **Exactly one** record. Open it for [Step 1.3](#step-13--confirm-the-connection-record-fields). |
| **Credentials** | Records in `discovery_credentials` whose **Credential alias** list names this alias. | **Exactly one** record, and the same record the connection's **Credential** field names in [Step 1.3](#step-13--confirm-the-connection-record-fields). If this list is empty while the connection's **Credential** field is populated, the credential-side half of the binding is missing; treat that as a failure and follow [If an alias is genuinely absent](#if-an-alias-is-genuinely-absent). |

### Step 1.3 — Confirm the connection record fields

One record in `http_connection`, the HTTP(s) Connection class of `sys_connection`. It can also be reached from **Connections & Credentials > Connections**, filtered on **Connection alias** `is` `x_bst_startuptrk.crunchbase_api`.

Before confirming the **Connection URL**, read the authoritative value from the system property:

1. Open **System Definition > System Properties**, or the `sys_properties` list.
2. Filter on **Name** `is` `x_bst_startuptrk.crunchbase.base_url`.
3. Confirm exactly one record, and read its **Value**. That property committed with the Update Set and holds `https://api.crunchbase.com/v3.1`. It is non-secret endpoint configuration; it is not a credential.
4. The connection record's **Connection URL** must equal that value exactly. If the two differ, correct the **connection record** to match the property. The property is the source of the value.

| Field | Column | Required value | Note |
| --- | --- | --- | --- |
| Name | `name` | *as provisioned* | Mandatory. A human-readable label. It is **not** the binding: the flow binds through **Connection alias**, never through this field. |
| Connection alias | `connection_alias` | `x_bst_startuptrk.crunchbase_api` | Mandatory. Must reference the alias record confirmed in [Step 1.2](#step-12--confirm-the-alias-record-fields). This is the binding that makes the alias resolvable. |
| Credential | `credential` | The Basic Auth credential of [Step 1.4](#step-14--confirm-the-basic-auth-credential-record-fields) | Must be populated and must reference that record. An empty **Credential** field is the single most common cause of an alias that resolves but cannot authenticate. |
| Connection URL | `connection_url` | The value of `x_bst_startuptrk.crunchbase.base_url` | `https://api.crunchbase.com/v3.1`. Confirm against the property as set out above. |
| Base path | `base_path` | *empty* | Per-request paths are supplied by the flow's REST step, not by the connection. |
| Application | `app_scope` | `Boston Startup Tracker` | Mandatory. The `x_bst_startuptrk` scope. |
| Active | `active` | `true` | An inactive connection is not selected at run time and the flow fails to authenticate. |
| Order | `order` | `100` | The platform default. It orders candidate connections when an alias has more than one; this alias has one. |
| Use MID server | `use_mid` | `false` | The call is made from the instance. No MID server is involved. |
| MID Selection | `mid_selection` | `auto_select` | Not applied while **Use MID server** is `false`. |
| MID Server | `mid_server` | *empty* | Not applied while **Use MID server** is `false`. |
| MID Cluster | `mid_cluster` | *empty* | Not applied while **Use MID server** is `false`. |
| MID Application | `application` | *as provisioned* | The MID application default. Not applied while **Use MID server** is `false`. Leave as found. |
| Capabilities | `capabilities` | *empty* | A MID capability list. Not applied while **Use MID server** is `false`. |
| Host | `host` | *empty* | Derived from **Connection URL**. Leave blank. |
| Protocol | `protocol` | *empty* | Derived from **Connection URL**. Leave blank. |
| Override default port | `port` | *empty* | The default port for the URL scheme is used. |
| Connection timeout | `connection_timeout` | *empty* | The platform default applies. Guides 02 and 03 own the flow-level timeout handling. |
| Connection retries | `connection_retries` | `0` | Retry behaviour on failure is owned by the flows, not by the connection. |
| Mutual authentication | `mutual_auth` | `false` | Authentication is Basic Auth through the credential record. |
| Protocol profile | `protocol_profile` | *empty* | Not applied while **Mutual authentication** is `false`. |
| MID protocol profile | `mid_protocol_profile` | *empty* | Not applied while **Use MID server** is `false`. |
| URL builder | `url_builder` | `false` | The URL is taken from **Connection URL** as entered. |
| Extended Attributes | `extended_attributes` | *empty* | No connection attributes are required. |
| Is internal | `is_internal` | `false` | This is not a platform-internal connection. |
| Connection type | `sys_class_name` | `HTTP(s) Connection` | Read-only. It must read `HTTP(s) Connection`, matching the alias's **Connection type** of `HTTP`. |

### Step 1.4 — Confirm the Basic Auth credential record fields

One record in `basic_auth_credentials`, the Basic Auth class of `discovery_credentials`. Reach it by clicking through the connection record's **Credential** field, or from **Connections & Credentials > Credentials** filtered on **Type** `is` `Basic Auth`.

**Per Crunchbase convention the API key is the password.** The key is held in the **Password** field; the **User name** field does not hold the key.

| Field | Column | Required value | Note |
| --- | --- | --- | --- |
| Name | `name` | *as provisioned* | A human-readable label. Not a binding. |
| Type | `type` | `Basic Auth` | Stored value `basic_auth`. Set by the record's class; confirm, do not edit. |
| User name | `user_name` | *as provisioned* | The account identifier recorded by the credential owner. **It is not the API key.** Confirm the field is populated and record only that it is populated. |
| Password | `password` | *as provisioned* | **This field holds the Crunchbase API key.** It is stored encrypted and renders masked; masked is the expected appearance. Confirm it is populated. Do not reveal, copy, transcribe or re-enter it. |
| Credential alias | `tag` | Includes `x_bst_startuptrk.crunchbase_api` | A list field referencing `sys_alias`. The alias must appear in it. This is the credential-side half of the binding; the connection's **Credential** field is the other half. Both must be present. |
| Applies to | `applies_to` | `All MID servers` | Stored value `all`. No MID server is used, so no MID restriction applies. |
| Active | `active` | `true` | An inactive credential is not selected and authentication fails. |
| Order | `order` | `100` | The platform default. It orders candidate credentials; this connection names one explicitly. |
| Application | `application` | `Boston Startup Tracker` | Mandatory. The `x_bst_startuptrk` scope. |
| MID servers | `mid_list` | *empty* | Not applied while **Applies to** is `All MID servers`. |
| Authentication Key | `authentication_key` | *empty* | Not used by the Basic Auth class. |
| Use Context | `use_context` | `false` | No credential context is applied. |
| Context Name | `context_name` | *empty* | Not applied while **Use Context** is `false`. |

### Step 1.5 — Test the credential

1. On the credential record, click the **Test credential** related link.
2. Supply the target the dialog asks for, using the **Connection URL** value confirmed in [Step 1.3](#step-13--confirm-the-connection-record-fields).
3. A successful test confirms the credential resolves and decrypts. A failure here is a credential-side fault, not a connection-side one: stop and follow [If an alias is genuinely absent](#if-an-alias-is-genuinely-absent), which covers a present-but-invalid credential as well as a missing one.

This test is diagnostic. The completion criterion for the alias is the **connection** test in [Step 3](#step-3--test-both-connections), not this one.

## Step 2 — Alias 2, LinkedIn

The alias name is **`x_bst_startuptrk.linkedin_oauth`** and its credential type is **OAuth 2.0**. Six records are confirmed: the alias, its connection, its OAuth 2.0 credential, the OAuth provider, the OAuth entity profile, and the token record set.

**LinkedIn authenticates through OAuth 2.0, not a static bearer token.** The secret material is a client identifier, a client secret and a refresh token, held across the provider and token records rather than in a credential password field. Precondition 9 applies to this step.

### Step 2.1 — Locate the alias record

1. Confirm the application picker still reads **Boston Startup Tracker**.
2. In the navigator, open **Connections & Credentials > Connection & Credential Aliases**.
3. Filter the list on **Name** `is` `x_bst_startuptrk.linkedin_oauth`.
4. Confirm the list returns **exactly one** record. Zero records, or more than one, means stop and follow [If an alias is genuinely absent](#if-an-alias-is-genuinely-absent).
5. Open the record.

### Step 2.2 — Confirm the alias record fields

One record in `sys_alias`. The field set is the same as [Step 1.2](#step-12--confirm-the-alias-record-fields); only the **Name** differs.

| Field | Column | Required value | Note |
| --- | --- | --- | --- |
| Name | `name` | `x_bst_startuptrk.linkedin_oauth` | Mandatory. **Character for character.** This is the string the LinkedIn flow of guide 03 resolves at run time. |
| Type | `type` | `Connection and Credential` | Mandatory. Stored value `connection`. |
| Connection type | `connection_type` | `HTTP` | Stored value `http_connection`. |
| Application | `sys_scope` | `Boston Startup Tracker` | The `x_bst_startuptrk` scope. |
| Support Multiple Active Connection | `multiple_connections` | `false` | One active connection serves this alias. |
| Parent Alias | `parent` | *empty* | This alias is not a child of another alias. |
| Default Retry Policy | `retry_policy` | *empty* | Retry behaviour is not set on the alias. |
| Configuration Template | `configuration_template` | *empty* | No template is applied. |
| ID | `id` | *as provisioned* | Platform-managed. Do not edit. |
| Is internal | `is_internal` | `false` | This is not a platform-internal alias. |

Confirm the same two related lists at the bottom of the alias form as in [Step 1.2](#step-12--confirm-the-alias-record-fields):

| Related list | Shows | Confirm |
| --- | --- | --- |
| **Connections** | Records in `sys_connection` whose **Connection alias** names this alias. | **Exactly one** record. Open it for [Step 2.3](#step-23--confirm-the-connection-record-fields). |
| **Credentials** | Records in `discovery_credentials` whose **Credential alias** list names this alias. | **Exactly one** record, and the same record the connection's **Credential** field names in [Step 2.3](#step-23--confirm-the-connection-record-fields). |

### Step 2.3 — Confirm the connection record fields

One record in `http_connection`. Read the authoritative URL from the property first:

1. Open the `sys_properties` list and filter on **Name** `is` `x_bst_startuptrk.linkedin.base_url`.
2. Confirm exactly one record and read its **Value**. It holds `https://api.linkedin.com/v2` and is non-secret endpoint configuration.
3. The connection record's **Connection URL** must equal that value exactly. If they differ, correct the connection record to match the property.

| Field | Column | Required value | Note |
| --- | --- | --- | --- |
| Name | `name` | *as provisioned* | A human-readable label, not a binding. |
| Connection alias | `connection_alias` | `x_bst_startuptrk.linkedin_oauth` | Mandatory. Must reference the alias confirmed in [Step 2.2](#step-22--confirm-the-alias-record-fields). |
| Credential | `credential` | The OAuth 2.0 credential of [Step 2.4](#step-24--confirm-the-oauth-20-credential-record-fields) | Must be populated and must reference that record. |
| Connection URL | `connection_url` | The value of `x_bst_startuptrk.linkedin.base_url` | `https://api.linkedin.com/v2`. Confirm against the property as set out above. |
| Base path | `base_path` | *empty* | Per-request paths are supplied by the flow's REST step. |
| Application | `app_scope` | `Boston Startup Tracker` | Mandatory. The `x_bst_startuptrk` scope. |
| Active | `active` | `true` | An inactive connection is not selected at run time. |
| Order | `order` | `100` | The platform default. |
| Use MID server | `use_mid` | `false` | The call is made from the instance. |
| MID Selection | `mid_selection` | `auto_select` | Not applied while **Use MID server** is `false`. |
| MID Server | `mid_server` | *empty* | Not applied while **Use MID server** is `false`. |
| MID Cluster | `mid_cluster` | *empty* | Not applied while **Use MID server** is `false`. |
| MID Application | `application` | *as provisioned* | The MID application default. Not applied while **Use MID server** is `false`. Leave as found. |
| Capabilities | `capabilities` | *empty* | A MID capability list. Not applied while **Use MID server** is `false`. |
| Host | `host` | *empty* | Derived from **Connection URL**. |
| Protocol | `protocol` | *empty* | Derived from **Connection URL**. |
| Override default port | `port` | *empty* | The default port for the URL scheme is used. |
| Connection timeout | `connection_timeout` | *empty* | The platform default applies. |
| Connection retries | `connection_retries` | `0` | Retry behaviour on failure is owned by the flows. |
| Mutual authentication | `mutual_auth` | `false` | Authentication is OAuth 2.0 through the credential record. |
| Protocol profile | `protocol_profile` | *empty* | Not applied while **Mutual authentication** is `false`. |
| MID protocol profile | `mid_protocol_profile` | *empty* | Not applied while **Use MID server** is `false`. |
| URL builder | `url_builder` | `false` | The URL is taken from **Connection URL** as entered. |
| Extended Attributes | `extended_attributes` | *empty* | No connection attributes are required. |
| Is internal | `is_internal` | `false` | This is not a platform-internal connection. |
| Connection type | `sys_class_name` | `HTTP(s) Connection` | Read-only. Must match the alias's **Connection type** of `HTTP`. |

### Step 2.4 — Confirm the OAuth 2.0 credential record fields

One record in `oauth_2_0_credentials`, the OAuth 2.0 class of `discovery_credentials`. Reach it through the connection record's **Credential** field, or from **Connections & Credentials > Credentials** filtered on **Type** `is` `OAuth 2.0`.

The OAuth 2.0 credential class holds **no password**. It carries a pointer to an OAuth entity profile, and the secret material lives on the provider and token records confirmed in the three steps that follow.

| Field | Column | Required value | Note |
| --- | --- | --- | --- |
| Name | `name` | *as provisioned* | A human-readable label, not a binding. |
| Type | `type` | `OAuth 2.0` | Stored value `oauth_2_0`. Set by the record's class; confirm, do not edit. |
| OAuth Entity Profile | `oauth_entity_profile` | The profile of [Step 2.6](#step-26--confirm-the-oauth-entity-profile) | Must be populated. This is the pointer from the credential to the OAuth configuration; an empty value leaves the connection with no token source. |
| Integration Type | `integration_type` | `System` | Stored value `system`. A value of `Personal`, stored `personal`, ties the token to an individual user and a scheduled flow then has no token to use. |
| Credential alias | `tag` | Includes `x_bst_startuptrk.linkedin_oauth` | A list field referencing `sys_alias`. The alias must appear in it. |
| Applies to | `applies_to` | `All MID servers` | Stored value `all`. |
| Active | `active` | `true` | An inactive credential is not selected. |
| Order | `order` | `100` | The platform default. |
| Application | `application` | `Boston Startup Tracker` | Mandatory. The `x_bst_startuptrk` scope. |
| User name | `user_name` | *empty* | Not used by the OAuth 2.0 class. |
| Password | `password` | *empty* | Not used by the OAuth 2.0 class. **The client secret does not go here**; it is held on the provider record of [Step 2.5](#step-25--confirm-the-oauth-provider-record). |
| MID servers | `mid_list` | *empty* | Not applied while **Applies to** is `All MID servers`. |
| Authentication Key | `authentication_key` | *empty* | Not used by the OAuth 2.0 class. |
| Use Context | `use_context` | `false` | No credential context is applied. |
| Context Name | `context_name` | *empty* | Not applied while **Use Context** is `false`. |

### Step 2.5 — Confirm the OAuth provider record

One record in `oauth_entity`. Open **System OAuth > Application Registry** and locate the record referenced by the profile of [Step 2.6](#step-26--confirm-the-oauth-entity-profile) — the profile's **OAuth provider** field names it. **This record holds the client identifier and the client secret.**

| Field | Column | Required value | Note |
| --- | --- | --- | --- |
| Name | `name` | *as provisioned* | Mandatory. The provider label the credential owner registered. |
| Type | `type` | `OAuth Provider` | Stored value `oauth_provider`. This is the outbound third-party provider type. `OAuth Client`, stored `client`, is for inbound access to this instance and is the wrong record class here. |
| Client ID | `client_id` | *as provisioned* | Mandatory. **This field holds the LinkedIn OAuth 2.0 client identifier.** Confirm it is populated. Record only that it is populated. |
| Client Secret | `client_secret` | *as provisioned* | **This field holds the LinkedIn OAuth 2.0 client secret.** Stored encrypted and rendered masked; masked is the expected appearance. Confirm it is populated. Do not reveal, copy or transcribe it. |
| Default Grant type | `default_grant_type` | *as provisioned* | Mandatory. Must be the grant type the credential owner registered with LinkedIn, and must be a grant type that issues a refresh token. It must equal the profile's **Grant type** in [Step 2.6](#step-26--confirm-the-oauth-entity-profile). |
| Token URL | `token_url` | *as provisioned* | The LinkedIn token endpoint. Must be populated, or no token can be obtained or refreshed. |
| Refresh Token URL | `refresh_token_url` | *as provisioned* | The endpoint used to exchange the refresh token for a new access token. Must be populated for unattended refresh to work. |
| Authorization URL | `auth_url` | *as provisioned* | Used when the refresh token was first obtained. |
| Redirect URL | `redirect_url` | *as provisioned* | Must match the redirect URL registered with LinkedIn. |
| Send Credentials | `send_client_credentials_as` | *as provisioned* | Must match what the provider expects: `As Basic Authorization Header`, stored `basic_authorization_header`, or `In Request Body (Form URL-Encoded)`, stored `request_body_parameter`. A mismatch fails token refresh with a provider-side authentication error. |
| Access Token Lifespan | `access_token_lifespan` | *as provisioned* | Mandatory, in seconds. |
| Refresh Token Lifespan | `refresh_token_lifespan` | *as provisioned* | Mandatory, in seconds. Note the value: the refresh token stops working when this elapses, and the credential owner must re-issue it. |
| OAuth API Script | `oauth_api_script` | *as provisioned* | A Script Include reference, populated only if the provider needs non-standard request handling. Leave as found. |
| Active | `active` | `true` | An inactive provider yields no token. |
| Comments | `comments` | *as provisioned* | Free text. **Confirm it contains no credential value.** If it does, report it through [If an alias is genuinely absent](#if-an-alias-is-genuinely-absent) as a credential-hygiene defect. |

### Step 2.6 — Confirm the OAuth entity profile

One record in `oauth_entity_profile`. There is no navigator module for this table: open it from the **OAuth Entity Profiles** related list at the bottom of the provider record of [Step 2.5](#step-25--confirm-the-oauth-provider-record), or through the **OAuth Entity Profile** field of the credential record of [Step 2.4](#step-24--confirm-the-oauth-20-credential-record-fields).

| Field | Column | Required value | Note |
| --- | --- | --- | --- |
| Name | `name` | *as provisioned* | Mandatory. |
| OAuth provider | `oauth_entity` | The provider of [Step 2.5](#step-25--confirm-the-oauth-provider-record) | Mandatory. Confirm it references that exact record and no other. |
| Grant type | `grant_type` | *as provisioned* | Mandatory. **Must equal the provider's Default Grant type.** A divergence between the two is a run-time token failure. |
| Is default | `default` | `true` | Confirm this profile is the default for its provider, so the credential resolves it without ambiguity. |
| OAuth Resources | `oauth_resources` | *as provisioned* | The scopes requested from LinkedIn. Leave as found. |
| JWT Provider | `jwt_provider` | *empty* | Not used by this grant type. |
| Assertion Producer | `saml2_assertion_producer` | *empty* | Not used by this grant type. |

Confirm the credential record of [Step 2.4](#step-24--confirm-the-oauth-20-credential-record-fields) points at **this** profile. The chain must close: credential to profile, profile to provider.

### Step 2.7 — Confirm the refresh token is on file and refresh works

The refresh token is the third piece of secret material and it lives in the token store, not on a form field you fill in.

1. Open **System OAuth > Manage Tokens**. The list is the `oauth_credential` table.
2. Filter on **Peer** `is` the provider record confirmed in [Step 2.5](#step-25--confirm-the-oauth-provider-record).
3. Confirm at least one record whose **Type** is `Refresh Token`, stored value `refresh_token`. Its presence is the confirmation that the refresh token has been issued and stored. **Do not open the token fields to read a value**; confirm the row exists and note its **Expires** value.
4. Note whether an **Access Token** record, stored value `access_token`, is also present, and note its **Expires** value.
5. Confirm the refresh behaviour after the connection test of [Step 3](#step-3--test-both-connections): re-read this list and confirm that the **Access Token** record's **Expires** has moved forward, or that an **Access Token** record now exists where none did. Either outcome confirms the platform exchanged the refresh token for a new access token without operator involvement.
6. If no **Refresh Token** record exists, the token has not been issued or has been revoked. Stop and follow [If an alias is genuinely absent](#if-an-alias-is-genuinely-absent). **Do not attempt to obtain a token yourself**, and do not place a token value.

| Field | Column | What to confirm |
| --- | --- | --- |
| Type | `type` | `Refresh Token`, stored `refresh_token`, for the token that sustains unattended access. `Access Token`, stored `access_token`, for the short-lived token derived from it. |
| Peer | `peer` | References the provider record of [Step 2.5](#step-25--confirm-the-oauth-provider-record). |
| Expires | `expires` | Present. Record the value. For the access token, it must move forward across a successful connection test. |
| Grant Type | `grant_type` | Matches the provider's **Default Grant type** and the profile's **Grant type**. |
| Last time the token was accessed | `last_access` | Updates after a successful connection test. |
| Token | `token` | **Do not read this field.** Confirm the row exists; nothing more. |
| Token issued | `token_issued` | **Do not read this field.** Stored encrypted. |
| Token received | `token_received` | **Do not read this field.** Stored encrypted. |
| User | `user` | Empty or the service account the credential owner registered. A populated personal user together with an **Integration Type** of `System` is a mismatch: report it through the escalation route. |

## Step 3 — Test both connections

**The connection test is mandatory and it is the completion criterion of this guide.** Run it for both aliases.

For each of the two connection records confirmed in [Step 1.3](#step-13--confirm-the-connection-record-fields) and [Step 2.3](#step-23--confirm-the-connection-record-fields):

1. Open the connection record from **Connections & Credentials > Connections**, filtered on **Connection alias**.
2. Confirm the record is saved with no unsaved changes pending. An unsaved edit is not covered by the test.
3. Click the **Test connection** related link at the foot of the form. It is a related link, not a form button.
4. Read the result.

| Result | Meaning | Action |
| --- | --- | --- |
| The test reports **success** | The connection resolved its alias, resolved and decrypted its credential, reached the endpoint at **Connection URL**, and the endpoint accepted the authentication. | The alias is established. Record the outcome. |
| The test reports a **failure** | One link in the chain did not resolve. | Do not proceed. Work back through the chain: connection **Connection alias**, connection **Credential**, credential **Active** and **Credential alias**, and for LinkedIn the profile, provider and refresh-token records. Then follow [If an alias is genuinely absent](#if-an-alias-is-genuinely-absent), which also covers a present-but-invalid credential. |

Record the two outcomes:

| # | Alias | Connection test outcome | Timestamp (UTC) |
| --- | --- | --- | --- |
| 1 | `x_bst_startuptrk.crunchbase_api` | | |
| 2 | `x_bst_startuptrk.linkedin_oauth` | | |

Record `pass` or `fail`, the timestamp in `YYYY-MM-DD HH:MM:SS` form, and nothing else. **Record no credential value in any field of this table.**

**Neither [`02-flow-crunchbase-ingestion.md` (planned)](02-flow-crunchbase-ingestion.md) nor [`03-flow-linkedin-ingestion.md` (planned)](03-flow-linkedin-ingestion.md) may be started until both aliases test green.** Both outcomes must read `pass`. A flow built against an alias that has not tested green fails at its first execution, and the failure appears as a flow defect rather than as the credential fault it is.

For LinkedIn, return to [Step 2.7](#step-27--confirm-the-refresh-token-is-on-file-and-refresh-works) after a successful test and complete its item 5, confirming that the access token was refreshed without operator involvement.

## If an alias is genuinely absent

This section applies when an alias, a connection, a credential, an OAuth provider, an OAuth profile or a refresh token cannot be found, or when a record is present but its name does not match, or when a connection test fails against records that are otherwise correctly bound.

**Do not create the missing record, and do not place a credential value.** The credentials are the property of their owner and are provisioned by that owner.

1. **Stop this guide.** Do not proceed to guides 02 or 03. Do not partially build the other alias in the meantime beyond the confirmation steps already completed.
2. **Record what is missing**, precisely and without any credential value: the alias name searched for; which of the six record classes did not resolve; and, for a connection-test failure, the failure text the platform returned.
3. **Escalate to the credential owner** — the party that holds the Crunchbase API key, or the LinkedIn OAuth 2.0 client identifier, client secret and refresh token. Ask them to provision or re-issue the material on this instance and to confirm the alias name they bound it to.
4. **Do not invent a key, a token, a client identifier, a client secret or a placeholder that resembles one.** Do not rename an existing unrelated alias to match. Do not point the connection at a different credential to make the test pass.
5. **Do not modify anything outside `x_bst_startuptrk`** while waiting. Prompt section 6.0 forbids it.
6. **The ingestion work is not blocked while you wait.** Ingestion has a sanctioned fallback path that requires no live credential: it reads the staging table loaded from the sample dataset. The dataset, its column contract and the property that forces the fallback are specified in [`../../sample-data/README.md`](../../sample-data/README.md), and the load procedure is [`06-staging-table-csv-import.md` (planned)](06-staging-table-csv-import.md).
7. **Label the evidence accordingly.** While either alias is unprovisioned, every ingestion run reads the fallback dataset, and every result must be labelled `fallback validated` and never `live validated`. That labelling rule and its effect on the acceptance evidence are stated in [`../../sample-data/README.md`](../../sample-data/README.md); the flagged items of this delivery are listed in [`../gaps-and-flags.md` (planned)](../gaps-and-flags.md).
8. **Resume at [Step 1.1](#step-11--locate-the-alias-record) or [Step 2.1](#step-21--locate-the-alias-record)** once the owner confirms the material is in place, and run the full confirmation and test sequence for that alias from the beginning.

## Operational warning — the binding is by name

**The flow-to-alias binding is by name, and a name mismatch fails at run time, not at build time.**

A flow that names an alias that does not exist, or that names it with a typographic error, saves without complaint and publishes without complaint. Nothing in the Flow Designer interface reports the fault. It surfaces only when the flow executes: the execution fails, and the failure presents as a flow error rather than as the missing binding it is. A scheduled flow can therefore fail silently on its cadence until someone reads the flow execution log.

Three consequences follow, and each is a step to take rather than a caution to note:

1. **Copy, never retype.** Copy both alias names character for character from the records confirmed in [Step 1.2](#step-12--confirm-the-alias-record-fields) and [Step 2.2](#step-22--confirm-the-alias-record-fields). Do not type them from memory and do not rely on autocomplete.
2. **Watch the two separators.** The scope prefix is joined by a **dot** and the resource part by an **underscore**: `x_bst_startuptrk.crunchbase_api`, not `x_bst_startuptrk_crunchbase_api` and not `x_bst_startuptrk.crunchbase-api`. The same applies to `x_bst_startuptrk.linkedin_oauth`.
3. **Test before saving the flow.** Guides 02 and 03 each require the connection test of [Step 3](#step-3--test-both-connections) to have passed before the flow is saved.

## Step 4 — Propagate both alias names into guides 02 and 03

Carry the confirmed names forward. Do this immediately after [Step 3](#step-3--test-both-connections) passes, while the records are still open.

1. Open the alias record of [Step 1.2](#step-12--confirm-the-alias-record-fields) and copy the **Name** field to the clipboard.
2. Paste it into the alias-name field of the Crunchbase flow's REST step as directed by [`02-flow-crunchbase-ingestion.md` (planned)](02-flow-crunchbase-ingestion.md). Paste; do not type.
3. Compare the pasted value against `x_bst_startuptrk.crunchbase_api` character for character, including both separators.
4. Repeat items 1 to 3 for the alias record of [Step 2.2](#step-22--confirm-the-alias-record-fields) and [`03-flow-linkedin-ingestion.md` (planned)](03-flow-linkedin-ingestion.md), comparing against `x_bst_startuptrk.linkedin_oauth`.
5. Record the comparison outcome for both.

| # | Alias name as confirmed on the alias record | Consuming guide | Names match character for character |
| --- | --- | --- | --- |
| 1 | `x_bst_startuptrk.crunchbase_api` | [`02-flow-crunchbase-ingestion.md` (planned)](02-flow-crunchbase-ingestion.md) | |
| 2 | `x_bst_startuptrk.linkedin_oauth` | [`03-flow-linkedin-ingestion.md` (planned)](03-flow-linkedin-ingestion.md) | |

Both rows must read `yes` before either flow is saved.

## The authentication-model change

**LinkedIn moves from a static bearer token to OAuth 2.0.** The legacy integrator sent a fixed module-level constant as a bearer `Authorization` header on every request. The alias `x_bst_startuptrk.linkedin_oauth` authenticates through an OAuth 2.0 client identifier, client secret and refresh token, and the platform exchanges the refresh token for a short-lived access token and renews it without operator involvement.

Crunchbase remains a single long-lived key. It moves from a query parameter to the **Password** field of a Basic Auth credential behind `x_bst_startuptrk.crunchbase_api`.

## What this replaces

The two aliases replace the credential handling of the legacy data-collection package. **Nothing in the table below is ported.** The only values carried forward are the two non-secret base URLs; every key, token and header construction is discarded.

| Legacy construct | Location | Replaced by |
| --- | --- | --- |
| Base URL `https://api.crunchbase.com/v3.1` as a module constant | `src/data_collection/api_integrators/crunchbase_integrator.py:L10` | The non-secret system property `x_bst_startuptrk.crunchbase.base_url`, confirmed against the connection record in [Step 1.3](#step-13--confirm-the-connection-record-fields). **Carried forward.** |
| A module-level `API_KEY` string constant | `src/data_collection/api_integrators/crunchbase_integrator.py:L11` | The **Password** field of the Basic Auth credential behind `x_bst_startuptrk.crunchbase_api`, confirmed in [Step 1.4](#step-14--confirm-the-basic-auth-credential-record-fields). Held encrypted, never in source. |
| That constant passed as a `user_key` **query parameter**, at three call sites | `src/data_collection/api_integrators/crunchbase_integrator.py:L22`, repeated at `:L41` and `:L60` | The connection resolves its credential at run time. No key appears in any request the flow composes, and no flow input, script step or Update Set record carries one. |
| Base URL `https://api.linkedin.com/v2` as a module constant | `src/data_collection/api_integrators/linkedin_integrator.py:L11` | The non-secret system property `x_bst_startuptrk.linkedin.base_url`, confirmed against the connection record in [Step 2.3](#step-23--confirm-the-connection-record-fields). **Carried forward.** |
| A module-level `API_KEY` string constant | `src/data_collection/api_integrators/linkedin_integrator.py:L12` | The OAuth 2.0 client identifier and client secret on the provider record of [Step 2.5](#step-25--confirm-the-oauth-provider-record), together with the refresh token of [Step 2.7](#step-27--confirm-the-refresh-token-is-on-file-and-refresh-works), all behind `x_bst_startuptrk.linkedin_oauth`. |
| That constant sent as a **static bearer** `Authorization` header, at two call sites | `src/data_collection/api_integrators/linkedin_integrator.py:L23`, repeated at `:L42` | Platform-managed OAuth 2.0 token exchange. The access token is derived from the refresh token and renewed automatically; no header is hand-assembled. |
| `CRUNCHBASE_API_KEY`, `LINKEDIN_API_KEY` and `GITHUB_API_KEY` as plain environment values | `.env.example:L27-L29` | No environment variable holds an ingestion credential. Both aliases resolve their own credentials on the instance. `GITHUB_API_KEY` has **no counterpart**: this application ingests from Crunchbase and LinkedIn only. |

Both base-URL properties are declared with `is_private` `false` and are readable and writable by the `x_bst_startuptrk.admin` role. **No property in this application holds a secret**; the full inventory is in [`../api-reference.md`](../api-reference.md).

## Completion criteria

This guide is complete when every item below holds. All are objectively checkable.

| # | Criterion |
| --- | --- |
| 1 | Exactly one `sys_alias` record named `x_bst_startuptrk.crunchbase_api` exists, with **Type** `Connection and Credential`, **Connection type** `HTTP`, and **Application** `Boston Startup Tracker`. |
| 2 | Exactly one `sys_alias` record named `x_bst_startuptrk.linkedin_oauth` exists, with the same **Type**, **Connection type** and **Application**. |
| 3 | Each alias has exactly one active connection record whose **Connection alias** references it and whose **Credential** is populated. |
| 4 | Each connection's **Connection URL** equals the value of its base-URL property: `x_bst_startuptrk.crunchbase.base_url` and `x_bst_startuptrk.linkedin.base_url` respectively. |
| 5 | The Crunchbase credential is of type `Basic Auth`, its **Password** field is populated, and its **Credential alias** list includes `x_bst_startuptrk.crunchbase_api`. |
| 6 | The LinkedIn credential is of type `OAuth 2.0` with **Integration Type** `System`, its **OAuth Entity Profile** is populated, and its **Credential alias** list includes `x_bst_startuptrk.linkedin_oauth`. |
| 7 | The LinkedIn provider record has **Client ID** and **Client Secret** populated, and its **Default Grant type** equals the profile's **Grant type**. |
| 8 | At least one `oauth_credential` record of type `Refresh Token` exists for that provider. |
| 9 | **Both connection tests pass**, and both outcomes are recorded in the table under [Step 3](#step-3--test-both-connections). |
| 10 | Both alias names have been propagated and compared character for character, and both rows of the table under [Step 4](#step-4--propagate-both-alias-names-into-guides-02-and-03) read `yes`. |
| 11 | No credential value has been written into any record, any document of this package, any log, any terminal transcript or any evidence table. |

Criterion 9 is the gate on guides 02 and 03. Criterion 11 is the gate the reviewer named under [Referenced documents](#referenced-documents) will check.

## Related documents

| Document | Role |
| --- | --- |
| [`../manual-build-instructions.md` (planned)](../manual-build-instructions.md) | The index for this folder and the authoritative execution order. It owns the rule that splits the Update Set from the manual build. |
| [`../deployment-runbook.md`](../deployment-runbook.md) | The import, preview and commit procedure that must complete before this guide starts, with its pre-flight checks, polling intervals, timeouts, rollback and failure matrix. |
| [`../validation-gates.md`](../validation-gates.md) | The sixteen post-commit gates of precondition 4, and the eleven-gate core of precondition 5. |
| [`02-flow-crunchbase-ingestion.md` (planned)](02-flow-crunchbase-ingestion.md) | Consumes `x_bst_startuptrk.crunchbase_api` by name. Runs after this guide. |
| [`03-flow-linkedin-ingestion.md` (planned)](03-flow-linkedin-ingestion.md) | Consumes `x_bst_startuptrk.linkedin_oauth` by name. Runs after this guide. |
| [`../../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml`](../../update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml) | Authoritative for the scope name `x_bst_startuptrk` and for the two base-URL property keys. Contains no alias record and no credential material. |
| [`../api-reference.md`](../api-reference.md) | The system-property inventory, including both base-URL properties and the statement that no property holds a secret. |
| [`../../sample-data/README.md`](../../sample-data/README.md) | The fallback dataset used while either alias is unprovisioned, and the `fallback validated` labelling rule. |
| [`06-staging-table-csv-import.md` (planned)](06-staging-table-csv-import.md) | Loads that fallback dataset into the staging table. |
| [`../gaps-and-flags.md` (planned)](../gaps-and-flags.md) | The flagged items of this delivery. Not restated here. |
| [`../../../docs/decisions/DECISION_LOG.md` (planned)](../../../docs/decisions/DECISION_LOG.md) | The single source of truth for every "why" behind this guide. |
| [`../../../docs/review/CRITICAL_DECISIONS.md` (planned)](../../../docs/review/CRITICAL_DECISIONS.md) | The five highest-risk decisions of this delivery. Its entry 3 is the one this guide is written to satisfy; the reviewer pointer is stated once, under [Referenced documents](#referenced-documents). |
