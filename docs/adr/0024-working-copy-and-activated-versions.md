# 0024. Working copy with change history and activated versions

| Decision control | Value                                                        |
| ---------------- | ------------------------------------------------------------ |
| Status           | Accepted                                                     |
| Date             | 2026-10-04                                                   |
| Deciders         | Cesar Zea (owner)                                            |
| Supersedes       | The explicit Save of validated journey point V10             |
| Amended by       | [ADR 0025](0025-runs-of-changes-and-run-mode.md): runs execute a version or a change |

## Context and problem

In step 1 as validated, edits stayed in the browser until Save created a new version,
and leaving the editor warned about unsaved changes. During the step 1 review the owner
asked that every change be saved when it is made, into a history that allows going
back, and that the user activate the version to use, normally the latest, as a new
numbered version whose number is visible. The owner then asked for branches that can
be visualized, without merge for now.

## Decision

- Each graph has a working copy whose every edit is stored as a numbered change with
  its full document. Changes are append-only; restoring an earlier change or version
  stores its document as a new change.
- Activating a change creates the next immutable version. The highest version is the
  active version; runs use it unless an earlier version is chosen.
- A change may hold a document with diagnostics; only a document without error
  diagnostics can be activated.
- The interface shows the active version number and whether the working copy has
  changes since it.
- A graph has branches, `main` first. A branch starts from any version or change and
  has its own working copy; versions record their branch and the version they follow.
  Change and version numbers are unique per graph. There is no merge.

## Consequences

- No edit is lost when leaving the editor, and no unsaved-changes warning is needed.
- Storage grows with every edit. The documents are small, so step 1 keeps each change
  in full; compaction can come later.
- Journeys J1–J3 activate a version instead of saving one.
