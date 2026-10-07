# Sprint Status Report — S06

| Document control | Value |
| --- | --- |
| Report ID | SPRINT-S06-004 |
| Report version | **0.0.6.4** — V0.0, Sprint 6, Revision 4 |
| Owner | Cesar Zea |
| Reporting date | 2026-10-03, Europe/Lisbon |
| Scope | Product workspace fidelity, configuration and retained execution |
| Delivery status | Locally verified correction; owner usability acceptance pending |
| Publication status | Uncommitted local delivery; publication not authorized |

The owner rejected [Revision 3](sprint-06-status-report-0.0.6.3.md) for insufficient
resemblance to the reviewed concept and instructed continuation. This report records
that bounded correction. Earlier passing checks retain their historical meaning;
they establish neither visual fidelity nor owner acceptance. Report versions are
separate from package versions in the [central register](../../../../CHANGELOG.md).

## Delivered correction

The full-width workspace now uses a compact contextual navigation rail, with a
clear collection return and persistent Workspace settings, illustrative credit
consumption and account preview. Its header separates the experiment name and
short draft state from exact revision details and gives Save revision a primary
action. Recovery of an uncertain command remains immediately visible.

The Collaboration panel groups editing actions, pressed visibility toggles and
layout controls. Agent cards are readable at desktop sizes; initial framing shows
the input, final output and feedback route. Polling preserves user positions and
viewport. Resource links attach to ordinary card borders and the compact resource
strip identifies actual consumers. Model infrastructure remains abstracted.

Selecting an agent opens a compact inspector beside the graph. Instructions and
model appear first, including historical example model resources whose exact
presentation profile was missing. Long prompts expand from the icon inside the
editor. Response, configured components, model details and advanced configuration
use disclosures. Add component and Connect resource remain visible; generic
schema forms and exact JSON remain accessible for unsupported presentations.
Stored incompatible values are retained with explicit repair, and pending model
selection displays coherently while preserving one atomic provider/model patch.

These changes preserve the existing canonical draft, invalid field buffers,
navigation guards, frozen commands, immutable revisions, admitted run identities,
permissions and authoritative USD accounting. Account and credit figures remain
explicitly illustrative; no account or credit transaction is implemented.

## Acceptance evidence

The [correction contract](../reviews/2026-10-03-s06-fidelity/README.md) defines
F01–F06 in addition to W01–W14 in the [S06-UX specification](../specification/s06-workspace-redesign.md).
The [workspace guide](../workspace.md) describes the resulting interaction.

| Criteria | Evidence |
| --- | --- |
| F01–F02 | Contextual navigation, separated global settings/account preview, exact identity disclosure, primary Save and unchanged command guards; shell regressions and actual desktop inspection. |
| F03 | Agent sizes, input/output/feedback geometry, pressed toolbar states, actual resource consumers and border connections; graph regressions, polling/drag journeys and actual desktop/narrow captures. |
| F04 | Declared prompt/model composition, exact-version discovery compatibility, unavailable binding repair, coherent pending model display and generic residual access; inspector regressions and actual edit/save. |
| F05 | Existing draft/flush, lossless number, uncertain command, immutable history, permissions and admitted-run tests retained; actual version comparison and retained output inspection. |
| F06 | Direct reviewed-concept comparison, actual 1440×900 / 1920×1080 / 390×844 inspection, ordinary configuration and simulated execution; unchanged mandatory verification passed. |

The unchanged complete `make verify` passed with exit 0, confirmed at **03:46:19 UTC**:
**2,280 Python tests, 791 frontend tests across 133 files and 34 browser journeys**.
Source limits, strict typing, lint, formatting, module boundaries, dead-code checks,
CodeQL, production build and independent coverage all pass. Frontend coverage is
**97.61% lines, 90.96% branches, 97.55% functions and 96.43% statements**.
Python line and branch coverage independently exceed 90%. CodeQL 2.27.1 records
no errors or warnings and 100 Python informational notes. The existing accounting
mutation baseline records 141 killed, 58 surviving and one timed out; this is not
an all-mutants-killed claim. The [verification record](../verification.md#s06-fidelity-correction--2026-10-03)
and [sanitized evidence](../evidence/s06-fidelity-verification-20261003.json) retain
results, numerators, the log digest and limitations.

The first complete attempt stopped at three browser setup omissions: Refresh
configuration is now inside a native disclosure, which those tests had not opened.
The five affected-file cases and the complete runner passed after correcting that
setup. Security, stale-reply and configuration-conflict assertions remain unchanged.
No threshold, exclusion, security protection or timeout has been relaxed.

## Actual local demonstration

A separate production HTTP/SQLite composition with simulated component providers
preserves the original local demonstration. Ordinary Reviewer prompt and model
edits saved revision `r-29cf65fcaf50411bb3d5e9b40a53abff`, derived from
`r-5604b31a965e40bdb8792300fae50ba7`. Versions retained both and compared the prompt,
provider profile and model changes. Runs retained the earlier admitted definition
even while the new design revision was selected.

New run `e82dd456cb394d30ac7d0ee46658f049` completed a proposer/reviewer feedback
loop in four activations. The final accepted output was inspected beside activation
4 before the event table. Unavailable reasoning is stated, not reconstructed.
Recorded simulated cost is USD 0.0000003; actual new provider cost is zero. Existing
user data and the authorized USD 3 real-spending ceiling remain unchanged.

Actual captures retain [1440×900 desktop](../reviews/2026-10-03-s06-fidelity/corrected-desktop-1440.jpg),
[1920×1080 desktop](../reviews/2026-10-03-s06-fidelity/corrected-desktop-1920.jpg),
[390×844 inspector](../reviews/2026-10-03-s06-fidelity/corrected-mobile-390.jpg) and
[390×844 graph](../reviews/2026-10-03-s06-fidelity/corrected-mobile-graph-390.jpg).
Dimensions are measured CSS viewport sizes; screenshots are actual UI evidence.
No document horizontal overflow was observed. Changing viewport preserves the
user's graph viewport; explicit Arrange was used to frame the narrow graph.
The browser at `http://127.0.0.1:5191/` is a transient local demonstration.

## Boundaries and owner review

Finite sequence and bounded conditional collaboration remain the supported
execution profiles. Graph nesting, direct graphical connection authoring, real
accounts/credits and S07 evaluation are not implemented by this correction.
No commit, push, merge, release or new paid validation forms part of this delivery.

[C09](../../../continuous-improvement/cycles/009-s06-fidelity/report.md) records preparation,
exclusive parallel package assignments, combined review, corrections and testing
under unchanged M06. It classifies rework and environment interruptions without
inventing activity durations or claiming a productivity improvement.
Owner usability acceptance remains pending.

## Revision history

| Version | Date | Change |
| --- | --- | --- |
| 0.0.6.4 | 2026-10-03 | Reference-based shell, graph and inspector correction; actual versioned simulated demonstration and unchanged complete mandatory verification. Owner acceptance pending. |
| 0.0.6.3 | 2026-10-03 | Redesigned workspace technically verified, then rejected by the owner for visual/usability fidelity. Preserved as a complete snapshot. |
| 0.0.6.2 | 2026-10-02 | Earlier product completion technically verified, then rejected by owner usability review. |
| 0.0.6.1 | 2026-10-02 | Initial structured workspace checkpoint, preserved as a separate snapshot. |
