# 0027. Functional Source License

| Decision control | Value                                                        |
| ---------------- | ------------------------------------------------------------ |
| Status           | Accepted                                                     |
| Date             | 2026-10-05                                                   |
| Deciders         | Cesar Zea (owner)                                            |
| Supersedes       | The Apache 2.0 choice recorded as Q19 in the [archived open questions](../archive/previous-implementation/specification/open-questions.md) |

## Context and problem

The repository has been public under the Apache License 2.0 since 2026-09-28. The
owner intends to offer Slow Thinker II as a paid service and does not want anyone to
use its code to offer the same service, or a substantially similar one. Apache 2.0
allows both. The code stays public, and internal use by others is acceptable.

## Considered options

- **Apache 2.0 or AGPL 3.0.** Neither prevents a competing service.
- **Elastic License 2.0.** Prevents a managed service of the software, not a similar
  product built from it.
- **PolyForm Small Business.** Lets small companies build a competing service.
- **PolyForm Noncommercial.** Prevents competition but also internal commercial use.
- **PolyForm Shield.** Prevents competition permanently; less widely recognized.
- **Functional Source License 1.1 with an Apache 2.0 future license (FSL-1.1-ALv2).**
  Prevents competing use, allows internal use, and is used by Sentry, Codecov and
  Liquibase. The owner accepts that each version becomes Apache 2.0 after two years.

## Decision

- The repository is licensed under FSL-1.1-ALv2 from this change, with the notice
  `Copyright 2026 Cesar Zea`. The [license](../../LICENSE) is the unchanged template.
- Every package declares the SPDX identifier `FSL-1.1-ALv2`.
- Contributions are accepted under the terms in the
  [contributing guide](../../CONTRIBUTING.md#license-of-contributions), which keep the
  owner able to license the project commercially.

## Consequences

- Slow Thinker II is source-available, not open source as the OSI defines it. Others
  may use, change and redistribute it for internal use, non-commercial education and
  research, and professional services to a licensee; they may not make it available
  in a commercial product or service that substitutes for it or offers the same or
  substantially similar functionality.
- Each version becomes available under Apache 2.0 two years after it is published.
- Versions published before this change remain available under Apache 2.0 to anyone
  who received them.
- Third-party dependencies keep their licenses. `obstacle-router` (LGPL-2.1) must stay
  replaceable by users, and `elkjs` (EPL-2.0) is used unmodified.
