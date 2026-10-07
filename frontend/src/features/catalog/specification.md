# features/catalog: specification

The components page, route `#/components`: what this server offers, read only.

- Reads `GET /catalog` and `GET /usage` when the page opens.
- A note says: “Read only. The operator installs components with `make components` and
  enables them, the LLMs and the budgets in the server configuration file. They cannot be
  edited from the interface yet.”
- **Components:** every catalog component, platform and installed packages, in catalog
  order, as a card: label, `type@version`, origin (“Platform” or “Installed package”),
  description and these facts:
  - Use, from `placements`: “As a node”, “Embedded at a node's outputs”, or “As a node,
    or embedded at a node's outputs”.
  - Inputs and Outputs: the port names, “None”, or “Outputs from its configuration” for
    `outputs_from`.
  - State: “Stateless” or “Stateful”.
  - LLM: “None”, or for each service use “Chosen for each node in <section title>”, the
    section holding the field at the use's pointer (“its configuration” when no section
    does).
  - Configuration: the section titles, or “None”.
- **LLMs:** each catalog LLM: label, provider, identifier and a Parameters table from
  the `properties` of its parameter schema: title (the property name without one),
  range (the enumerated choices; “<min>–<max>”, “At least <min>” or “At most <max>”;
  “true or false” for a boolean; otherwise “—”) and default (“—” without one). Numbers
  use English digit grouping, for example “1–384,000”.
- **Budgets:** the daily and monthly budgets with their period key, limit and amount
  used, exactly as `moneyLabel` shows them.
- States: “Loading the catalog…”; “No components are available.”; “No LLMs are
  configured.”; “Loading the budgets…”.

Acceptance: unit tests render the contract catalog fixture and check component facts,
LLM parameters, budgets, empty states and failed reads.

## Accessible names

| Element    | Role and name                                                                                                                                            |
| ---------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Page       | heading “Components”, level 1                                                                                                                            |
| Components | region “Components” with its heading at level 2; a list item per component named by its label (heading level 3), with its facts as terms and definitions |
| LLMs       | region “LLMs”; a list item per LLM named by its label; table “Parameters” with columns “Parameter”, “Range”, “Default”                                   |
| Budgets    | region “Budgets”; table “Budgets” with columns “Budget”, “Period”, “Limit”, “Used” and rows “Daily”, “Monthly”                                           |
| Failures   | alert “Could not load the catalog. <message>” with button “Try again”; alert “Could not load the budgets. <message>”                                     |

## Public interface (`features/catalog/index.ts`)

`ComponentsPage({client})`.

## Implementation decisions

- The page uses the application's shared page classes; each component card shows its
  icon as a coloured tile like the editor's palette (decorative).

- Budgets show exact amounts on this page; the banner's three-decimal format belongs to
  the application shell.
- A catalog read that fails replaces the Components and LLMs sections; the Budgets
  section is read and reported separately.
