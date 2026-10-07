# Security

Step 1 is a local, single-user installation running trusted components. The
controls below protect credentials, spending and the integrity of the record, and
keep the design ready for isolated containers. Threats follow the
[OWASP Top 10 for LLM Applications](https://genai.owasp.org/llm-top-10/).

| Threat                                   | Control in step 1                                                                                   |
| ---------------------------------------- | --------------------------------------------------------------------------------------------------- |
| LLM01 Prompt injection                   | Model output never changes authorization, limits or graph structure; it is data in messages          |
| LLM02 Sensitive information disclosure   | Credentials stay in the backend; grants and credentials are never recorded; responses are redacted   |
| LLM03 Supply chain                       | Components are installed offline from hash-locked wheels; installations are verified before launch    |
| LLM04 Data and model poisoning           | Out of scope for step 1; no training or fine-tuning                                                  |
| LLM05 Improper output handling           | Payloads are JSON values; nothing from a model is executed by the platform; the interface renders text, never HTML |
| LLM06 Excessive agency                   | Components reach only the entries their configuration selects; no tools in step 1                    |
| LLM07 System prompt leakage              | Prompts are user configuration, recorded on purpose for analysis                                      |
| LLM08 Vector and embedding weaknesses    | Out of scope for step 1                                                                              |
| LLM09 Misinformation                     | Recorded evidence separates observed facts from component reports                                    |
| LLM10 Unbounded consumption              | Reservations before every call; run, daily and monthly budgets; activation, concurrency and time limits |

Additional controls:

- The operator API requires a bearer token of 32–128 characters, binds to loopback
  and checks the request host and browser origin. A server whose allowed hosts are all
  loopback addresses may opt out of the token (`operator_authentication: "none"`) for
  local use; the host and origin checks still refuse other sites in the browser, but
  any local process can then operate the server.
- Invocation grants are random, stored only as digests, scoped to one call and
  revoked when it ends.
- A Router script is user code executed in the Router's process; step 1 trusts it.
  Isolated containers will contain it later.
- [ASVS](https://owasp.org/projects/asvs) level 2 verification remains required
  before the first server deployment.
