# Requirements and scope

| Document control | Value                                                                                   |
| ---------------- | --------------------------------------------------------------------------------------- |
| Document ID      | REQ-CORE                                                                                |
| Revision         | 2                                                                                       |
| Owner            | Cesar Zea                                                                               |
| Date             | 2026-10-04                                                                              |
| Status           | Approved direction; step 1 scope validated through the [step 1 journeys](core-step-1-journeys/README.md) |
| Previous edition | [Revision 1](../archive/previous-implementation/specification/requirements.md) (R01–R31) |

## Purpose

Slow Thinker II is a platform where users define graphs of collaborating agents
and other components, in whatever shape their problem needs, in order to:

1. Run them under supervision, recording their internal and external activity,
   so that what happened can be analysed and improvements proposed against the
   user's own objectives: quality, speed, cost or any other criterion.
2. Run batches of experiments that test a configuration.
3. Run improvement cycles that propose and evaluate variants.
4. Execute the resulting graphs outside the laboratory: through the platform's
   API, with or without supervision, in containers, and in other forms to be
   defined. Platform execution is charged by subscription and usage.

The platform must be extensible by its vendor and by its users, and secure:
execution will run in isolated containers without losing monitoring.

## Stakeholders

| Stakeholder         | Need                                                                                     |
| ------------------- | ---------------------------------------------------------------------------------------- |
| Graph designer      | Build, configure and run collaboration graphs without technical plumbing.                |
| Component author    | Publish components that behave and configure like the platform's own.                    |
| Analyst             | See exactly what happened in a run and compare runs against chosen objectives.           |
| Platform operator   | Configure model providers, credentials and spending limits once for all graphs.          |
| Maintainer          | Evolve an inspectable, modular system under the mandatory engineering standards.         |

## Requirements

Identifiers describe requirements, not implementation. “Later” items keep their
extension boundary in the design without being implemented in step 1.

| ID   | Requirement                                                                                                                                                                                         | Step 1 boundary                                           | Revision 1 origin  |
| ---- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------- | ------------------ |
| CR01 | A graph consists of nodes, named ports and connections, in any topology including loops. Graphs are typed documents saved as immutable versions.                                                    | Trigger, LLM Call, Router and Output; one trigger         | R04, R16, R17, R19 |
| CR02 | Every interaction is mediated, supervised and recorded by default. A pass-through mode may be added later.                                                                                         | All calls recorded                                        | R05, R11, R12      |
| CR03 | Nodes exchange asynchronous messages. A node activates once per received message. One output connected to several inputs delivers to all of them concurrently.                                       | Delivery per message; no joins                            | R04, R10           |
| CR04 | Resources and platform services are called synchronously, through the platform, and recorded.                                                                                                       | LLM service only                                          | R05, R08, R09      |
| CR05 | Connections and declared service uses are the authorization. Users never author permissions; the platform may impose further restrictions.                                                         | Derived authorization                                     | R06                |
| CR06 | A node does not know where its output goes. Components may know the tools, resources and services assigned to them.                                                                                 | No tools assigned yet                                     | R09                |
| CR07 | Stateless components may run concurrent activations; stateful components reject a concurrent activation by default. Queues may later be added as components at a node's input.                    | Global running-node limit                                 | R10                |
| CR08 | Vendors and users package components independently. Each package declares its ports, configuration and configuration screens; the platform renders them with generic controls and runs no component interface code. | LLM Call and Router packages                              | R02, R03, R31      |
| CR09 | Components can be embedded in another node at declared positions; the user sees one node.                                                                                                           | Output position (Router)                                  | R30                |
| CR10 | Model providers are platform services configured by the operator; credentials stay on the server. Each provider declares its invocation parameters as JSON Schema, validated when a graph is saved and before each call. Later they may be configured per user or workspace. | OpenAI and DeepSeek                                        | R08, R23           |
| CR11 | Components report the internal activity they want analysed. Recorded evidence distinguishes what the platform observed from what a component reported. Predefined components report their internals. | LLM Call and Router reports                               | R11, R12           |
| CR12 | Runs have limits on activations, running nodes, time and budget. Daily and monthly budgets apply to all runs. Reaching a limit stops the run with an explained status.                             | All four run limits; daily and monthly budgets            | R13–R15            |
| CR13 | Token usage and cost are recorded for every model call.                                                                                                                                             | Per call and per run                                      | R14                |
| CR14 | Users build, configure and run graphs visually, and inspect each run's activity.                                                                                                                    | Journeys J1–J3 and the activity view                       | R18, R19, R31      |
| CR15 | Shared variables, shared context and memory; joins and conversation threads; tools and MCP servers for nodes; several triggers.                                                                    | Later                                                     | R09                |
| CR16 | Batch experiments, comparison against objectives and improvement cycles.                                                                                                                             | Later                                                     | R24–R26            |
| CR17 | Execution through the platform API with subscription and usage billing; multiple users; execution in containers; standalone export.                                                               | Later; design rules apply now                              | R20, R28           |
| CR18 | The mandatory [engineering standards](../../README.md#engineering-standards) apply to all code. Product text and documentation are in English.                                                     | Applies                                                   | R21, R22           |

## Step 1

Step 1 delivers the validated journeys: one agent (J1), an agent with an embedded
Router (J2) and a review loop (J3), as step 1.1, and the activity view as step 1.2.
The [step 1 delivery specification](step-1/README.md) defines its acceptance
criteria, modules and verification.

## Evidence limits

Recorded explanations or reasoning are reported evidence, not a complete account
of a component's internal computation. Mediation does not contain malicious code
until components run in isolated containers; step 1 runs trusted local components.
