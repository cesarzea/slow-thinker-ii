# features/versions: specification

The History panel of the editor, under
[ADR 0024](../../../../docs/adr/0024-working-copy-and-activated-versions.md) and the
Graphs section of the [operator API](../../../../docs/contracts/operator-api.md). The
application composes it through the editor's `renderHistory(context)`; it follows the
redesign mockup's history panel.

- **Reads.** `GET /graphs/{id}` (branches, versions, active version), the open branch's
  changes `GET /graphs/{id}/changes?branch=&limit=31` (30 shown, the 31st describes the
  oldest shown), each listed change's document once (`GET /graphs/{id}/changes/{n}`;
  changes never change) and the catalog. It reads again whenever the context's
  `latestChange` or `activeVersion` changes, and after each of its actions.
- **Working copy card.** “Working copy” with the branch, “<n> changes since version
  <h>”, “No changes since version <h>” or “<n> changes, no version yet” (“<n>+” when
  more changes exist than were read), “· saved <time>”, and “Activate as v<next>”,
  enabled while the latest change is not a version: it activates that change and calls
  `onActivated(version)`.
- **Branches.** The “Branch” select opens another branch through `onBranchChange`. “New
  branch” asks for a name (the API's rule: 1–40 ASCII letters, digits, spaces, `.`, `_`,
  `-`, starting with a letter or digit) and a start: any version, or any listed change of
  the open branch; by default the open branch's version, else the active version, else
  its latest change. Creating calls `onBranchChange(name)`; refusals stay in the dialog.
- **Versions.** Every version, newest first, one lane per branch that has versions
  (oldest branch leftmost), a dot per version and a line to the version it follows
  (`parent`), forking from the parent's lane for a branch's first version. The active
  version has a filled dot, a filled badge and “· Active”. Each row: “Version <n>”, its
  branch, day and time and change; “Activate as v<next>” (not on the active one), which
  saves the version's document as a change on its branch, activates it, calls
  `onRestore(document)` when that branch is open, then `onActivated`; “Branch from here”;
  “Open read-only”, a dialog with the version's canvas drawn by `renderGraph`.
- **Changes.** The open branch's changes, newest first: time (“10:42” today, else the
  day), a description and the version activated from it (“v3”). The newest is “Current”;
  the others offer Restore, which calls `onRestore` with that change's document. “Show
  earlier changes” reads the previous page.
- **Descriptions** come from `ui` `describeChange(before, after, catalog)`, applied to each change and the previous change of the branch, joining at
  most two parts and “and <n> more”: “Renamed the graph to <name>”, “Limits edited”,
  “Added <node> (<component label>)”, “Removed …”, “Renamed <old> to <new>”,
  “<node> · <section titles> edited” (sections whose declared fields differ;
  “Configuration” without a declaration), “<node> · added <label> at its outputs”,
  “Connected <node> · <port> → <node> · <port>”, “Disconnected …”, “Moved <node>” or
  “Arranged the graph” (several nodes moved), otherwise “No visible change”. A branch's
  first change reads “Created the graph”, “Started from v<n>” or “Started from change
  <n>”; a document not read yet shows “Change <n>”.
- Failed actions show an alert “<Action> failed. <first diagnostic or message>”; one
  action runs at a time.

Acceptance: unit tests for the lane layout, the descriptions, the panel's rendering,
activation of the working copy and of an earlier version, a refused activation, restore,
branch selection and creation, and the read-only view.

## Accessible names

| Element      | Role and name                                                                                                                                                       |
| ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Panel        | region “History” with heading “History” (level 2); button “Close history”                                                                                           |
| Working copy | region “Working copy”; button “Activate as v<n>”                                                                                                                    |
| Branches     | combobox “Branch”; button “New branch”; dialog “New branch” with textbox “Name”, combobox “Start from”, buttons “Create branch”, “Cancel”                           |
| Versions     | heading “Versions”; list “Versions” with items named “Version <n>”, each with buttons “Activate as v<n>” (not the active one), “Branch from here”, “Open read-only” |
| Read only    | dialog “Version <n> · read only” with button “Close”                                                                                                                |
| Changes      | heading “Changes”; list “Changes” with items named “Change <n>”, each with button “Restore” or the text “Current”; button “Show earlier changes”                    |

The lanes are decorative (`aria-hidden`); each row's text names its branch.

## Public interface (`features/versions/index.ts`)

`HistoryPanel({client, graphId, branch, latestChange, activeVersion, onRestore,
onBranchChange, onActivated, onClose, renderGraph})`: the editor's `HistoryContext`
plus the client and `renderGraph({document, catalog})`, which draws a document read
only (the application passes the editor's `GraphPreview`).
