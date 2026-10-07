# Requirements and scope

| Document control | Value                                                                                   |
| ---------------- | --------------------------------------------------------------------------------------- |
| Document ID      | REQ-CORE                                                                                |
| Revision         | 3                                                                                       |
| Owner            | Cesar Zea                                                                               |
| Date             | 2026-10-07                                                                              |
| Status           | Approved by the owner on 2026-10-07 after the [scope review](scope-review-2026-10-06.md) |
| Previous edition | Revision 2 in the git history; [revision 1](../archive/previous-implementation/specification/requirements.md) (R01–R31) |

## Purpose

Slow Thinker II is a laboratory and an execution platform for systems of collaborating
agents: it designs them, shows what happens inside them, improves them against each
client's objectives and puts them to work.

- **Design graphs.** A graph can be proposed by the platform, imported by the user or
  designed by them, and the three paths are on the same level: any of them is edited,
  run, analysed and improved the same way. On any graph, the platform suggests
  optimizations according to the client's particular objectives.
- **Run under supervision.** Every run records what happens inside and outside each
  agent, with time and spending limits.
- **Understand how agents collaborate.** What information flows, how ideas evolve, who
  may have influenced whom, and what each step costs in quality, time and money.
- **Test configurations.** Batches of tasks with criteria, weights and repetitions, to
  compare graph variants with data.
- **Improve automatically.** From the analysis, propose variants, run them, evaluate
  them and keep those that best meet the client's objectives.
- **Put graphs to work.** Through the API, with or without supervision, in isolated
  containers, or exported as standalone, readable Python code.

The platform is a multi-user service paid by subscription and usage. Users belong to
companies; each company's data and runs are isolated from the others, and each user
opens only the workspaces they have access to. A workspace holds what is common to its
work, such as storage, databases, API connections and their credentials, and its Labs,
one per objective, hold graphs, experiments, work sessions, runs and results. In a Lab,
experimentation is manual, supervised or automatic. A marketplace offers graphs and
components from the platform, from backed companies or professionals and from the
community.

### Why

- LLMs already outperform most people at technical work, and much faster: designing a
  graph, writing its prompts, creating synthetic test sets and searching for
  optimizations can all be done by LLMs.
- Knowing what happens inside the collaboration, including the agents' reasoning where
  the provider exposes it, makes optimization far easier.
- Every improvement is demonstrated empirically on incremental test sets the optimizer
  has never seen. Some analyses and optimizations can be checked before running them;
  many can only be proved by running them, which is why this is an experimentation lab:
  each one is a hypothesis, tested by experiment, and its result is recorded.
- Optimizing a graph that runs millions of times is an investment, not a cost, and it
  gives engineers a laboratory rather than replacing them.

## Stakeholders

| Stakeholder         | Need                                                                                       |
| ------------------- | ------------------------------------------------------------------------------------------ |
| Graph designer      | Build, configure, import or ask for graphs and run them without technical plumbing.         |
| Analyst             | See exactly what happened in a run and compare variants against chosen objectives.          |
| Company and workspace member | Work only with the workspaces and data their company gives them access to.          |
| Component author    | Publish components that behave and configure like the platform's own.                       |
| Marketplace publisher | Offer graphs and components free, for a one-off payment or per use, with or without support. |
| Platform operator   | Configure model providers, infrastructure, credits and spending limits once for all users.  |
| Maintainer          | Evolve an inspectable, modular system under the mandatory engineering standards.            |

## Requirements

Identifiers describe requirements, not implementation. The sprint column names where a
requirement is delivered, following the [roadmap](roadmap.md); a design boundary holds
from S06 even when delivery comes later.

| ID   | Requirement                                                                                                                                                                                                 | Sprint                                         | Revision 1 origin  |
| ---- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------- | ------------------ |
| CR01 | A graph consists of nodes, named ports and connections, in any topology including loops. Every change is saved; changes can be activated as versions on branches.                                           | S06                                            | R04, R16, R17, R19 |
| CR02 | Every interaction is mediated, supervised and recorded by default. A mode without supervision skips the detailed record but still meters every billable call.                                               | S06; mode without supervision S21              | R05, R11, R12      |
| CR03 | Nodes exchange asynchronous messages. A node activates once per received message. One output connected to several inputs delivers to all of them concurrently. Joins and conversation threads are added later. | S06; joins and threads S14                     | R04, R10           |
| CR04 | Resources and platform services are called synchronously, through the platform, and recorded.                                                                                                               | S06 (LLM service); tools S13                   | R05, R08, R09      |
| CR05 | Connections and declared service uses are the authorization. Users never author permissions; the platform may impose further restrictions.                                                                 | S06                                            | R06                |
| CR06 | A node does not know where its output goes. Components may know the tools, resources and services assigned to them.                                                                                         | S06                                            | R09                |
| CR07 | Stateless components may run concurrent activations; a stateful node takes one activation at a time until ordered queues at node inputs hold further messages.                                               | S06; queues S14                                | R10                |
| CR08 | Components are packaged independently, run in their own process or thread behind the component protocol, and declare their ports, configuration and configuration screens; the platform renders them with generic controls and runs no component interface code. | S06                                            | R02, R03, R31      |
| CR09 | Components can be embedded in another node at declared positions (output, memory); the user sees one node.                                                                                                 | S06                                            | R30                |
| CR10 | Model providers are platform services configured by the operator; credentials stay on the server. Each provider declares its invocation parameters as JSON Schema, validated when a graph is saved and before each call. | S06                                            | R08, R23           |
| CR11 | Components report the internal activity they want analysed. Recorded evidence distinguishes what the platform observed from what a component reported. Predefined components report their internals.         | S06                                            | R11, R12           |
| CR12 | Runs have limits on activations, running nodes, time and budget; daily and monthly budgets apply to all runs and work sessions have their own budget. Deadlines per call and per run include waits and retries. | S06; session budgets S07; deadlines S15        | R13–R15            |
| CR13 | Token usage and cost are recorded for every model call. Tariffs are updated automatically and each run keeps the tariff revision it used.                                                                   | S06; automatic tariffs S10                     | R14, Q03           |
| CR14 | Users build, configure and run graphs visually and inspect each run's activity; experts edit, import and export graphs as JSON; graphs can be created and changed with a prompt, with visible changes and explicit acceptance. | S06; JSON S09; prompt S12                      | R17–R19, R31       |
| CR15 | Tools and MCP servers assigned to nodes through a permission-filtered proxy; shared context and variables; memory as private or shared persistent resources, validated first with mem0.                    | mem0 S09; the rest S13                         | R06, R09           |
| CR16 | Evaluation: task sets, including synthetic ones; criteria and weights; repetitions; batch runs; comparisons proved on incremental test sets never seen by the optimizer; calibration of LLM evaluators; an experiment log of hypotheses and results. | S10–S11                                        | R24, Q15           |
| CR17 | Execution of graphs through the platform API in production, with API triggers.                                                                                                                              | S21                                            | R20, R28           |
| CR18 | The mandatory [engineering standards](../../README.md#engineering-standards) apply to all code. Product text and documentation are in English.                                                            | Always                                         | R21, R22           |
| CR19 | Companies, users and workspaces: every request is authorized against the user's access, each company's data and runs are isolated, and a user may access several workspaces. Self-service registration and member management come later. | S07; registration S19                          | R20                |
| CR20 | Workspaces hold shared resources: storage, databases, API connections and their credentials. A resources view shows what a workspace offers.                                                               | S07; resources view S09                        | R09, R31           |
| CR21 | Labs, one per objective, hold graphs, experiments, variants with provenance and work sessions; experimentation is manual, supervised or automatic.                                                          | S07                                            | R16, R24           |
| CR22 | Runs execute in isolated containers that never mix workspaces, without losing monitoring. By default the nodes of a run share a container; the user can give any node its own, and third-party code always runs apart. | Local S08; AWS S17–S18                         | Q16                |
| CR23 | Design and automatic improvement: the platform proposes graphs and optimizations against the client's objectives; manual, supervised and automatic improvement cycles; interchangeable optimizers.           | S12                                            | R24                |
| CR24 | Execution control: pause and resume runs; graphs that change while they run; reusable subgraphs.                                                                                                            | Pause S15; dynamic graphs and subgraphs S16    | R04, Q16           |
| CR25 | Prepaid credits per user or workspace, priced per call and per compute time; subscriptions and payments; infrastructure cost control per workspace.                                                       | S19–S20                                        | R14                |
| CR26 | Teams bring their own agents: OpenAI, LangChain and LangGraph clients work under the same supervision; users publish components; a component can build on another with recorded versions.               | S22                                            | R08, R27           |
| CR27 | Deep analysis: an analysis plan per graph, proposed by an LLM and validated by the user, executed by interchangeable analyzer components and linked to evidence; its findings feed the optimizer. An idea may have several sources; convergence is not correctness; similarity does not prove causality. | S23                                            | R25, R26           |
| CR28 | Standalone export as readable, professional, reviewable Python code without platform supervision.                                                                                                          | S24                                            | R28                |
| CR29 | A marketplace of graphs and components, horizontal and vertical, official, backed or from the community, free, one-off or paid per use, with reviews and ratings; a library of collaboration patterns.    | S25                                            | R03                |

## Changes from revision 2

No requirement is removed. Changed: CR01 (every change saved, versions and branches);
CR02 (metering without supervision); CR07, CR08, CR09, CR12, CR13, CR14 (recovered or
extended scope); CR15 and CR16 (split from the former "later" items and made concrete);
CR17 (now execution through the API; users, containers and export moved to CR19, CR22
and CR28). Added: CR19–CR29. The [scope review](scope-review-2026-10-06.md) lists every
item that revision 2 had dropped or reduced and the owner's decision on each.

## Evidence limits

Recorded explanations or reasoning are reported evidence, not a complete account of a
component's internal computation. The platform does not promise the best graph or
guarantee finding a better one; it lets the client search for one with demonstrated
comparisons. Mediation does not contain malicious code until components run in isolated
containers; S06 runs trusted local components.
