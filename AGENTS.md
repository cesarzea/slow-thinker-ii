# Working on Slow Thinker II

Follow the [module workflow](docs/architecture/module-boundaries.md#module-documents-and-implementation-workflow)
and the mandatory [engineering standards](README.md#engineering-standards).

Every existing implementation module must have a brief `readme.md` (an existing
`README.md` fulfils this role) and a `specification.md` in its own directory.
Create `todo.md` there only when identified work remains. This applies to existing
modules as well as new ones; organizational folders are not additional modules.
For an independently packaged component, keep this set at its package root.

Define the complete sprint through delivery before launching development. Its
scope must cover the agreed delivery objective end to end, with all affected
modules, contracts, tasks, dependencies, owners and acceptance criteria specified.
Keep final project objectives in view without expanding the agreed sprint scope.

Work in distinct phases:

1. **Analysis, specification and tasks:** the coordinator resolves the sprint's
   design and feasibility questions, updates all affected module documents and
   prepares implementation tickets. Include the testing scope, responsibilities
   and acceptance criteria. Review new public interface skeletons before assigning
   their implementation. Leave internal choices open within agreed contracts.
2. **Development and delivery:** assign one or more complete components or packages
   to each implementer, grouping them by cohesion, dependencies and workload.
   Launch independent assignments in parallel with exclusive ownership. Each
   implementer follows its specifications and tickets, then reports its delivery
   and any unresolved issues. Do not repeatedly reopen the architecture or
   alternate development with functional testing.
3. **Review and corrections:** when deliveries are complete, review them against
   their contracts and review the whole result, including interactions and failure
   paths. Group corrections into module tickets, delegate them and review the
   corrected result. Repeat until the complete sprint appears ready for testing.
4. **Testing:** finalize concrete test tickets from the planned scope; implement
   module, integration and end-to-end tests, in parallel where independent. Run
   verification, analyze results together, assign correction tickets and repeat
   corrections and relevant verification until all acceptance criteria and
   mandatory checks pass.

Each implementer receives the shared rules, module documents, relevant code,
dependency contracts and a brief explanation of purpose and failure consequences.
The coordinator owns architecture, shared-contract decisions and whole-system
review. Assignment units are whole components or packages; file boundaries record
that ownership. Shared files have one assigned owner, so deliveries do not overlap
and need no separate merge phase. Whole-system review must still check that modules
work together. Implementers report ambiguities rather than invent cross-module
decisions; resolve a blocking contract issue before affected work continues, and
revisit only the affected design and tickets. Delegate tests and corrections with
the same ownership rules. Apparent coherence permits entering testing, not release.

Read the affected modules' documents first. Keep `todo.md` as an implementer's
ticket containing only unresolved work. Remove completed items; delete the file
when nothing remains. Keep contracts and usage documents current, and link shared
definitions instead of duplicating them.

Do not weaken any existing verification gate. Avoid repeating broad verification
without a relevant change or unresolved concern. Assess the method using elapsed
time to a verified delivery, rework, integration
defects and available resource usage; label estimates and do not infer efficiency
from code volume or the number of parallel implementers.
