# Quality scenarios

| ID   | Quality       | Stimulus                                                         | Expected response                                                                    | Check                                   |
| ---- | ------------- | ---------------------------------------------------------------- | ------------------------------------------------------------------------------------ | --------------------------------------- |
| QS01 | Recording     | Any run of J1–J3                                                  | Every message, activation, component call, model call and report appears in order, with gapless sequence numbers | Integration and journey tests           |
| QS02 | Recording     | A component reports a step                                       | It appears as reported evidence of its activation                                     | Integration test                        |
| QS03 | Boundedness   | A loop never reaches acceptance                                  | The run stops at `max_activations` with status and reason shown                       | Engine test and journey J3 limit case   |
| QS04 | Boundedness   | A reservation would exceed the run, day or month budget          | No provider call is made; the run stops naming the budget                            | Gateway and ledger tests                |
| QS05 | Boundedness   | A component exceeds its time budget                              | The activation fails and the run fails within one second of the budget                | Engine and host tests                   |
| QS06 | Authorization | A component calls an LLM other than the one configured           | `403 model_not_allowed`, no provider call, recorded                                   | Gateway test                            |
| QS07 | Authorization | A grant is used after its call ended                             | Rejected with `401 invalid_grant`; no provider call                                   | Access and gateway tests                |
| QS08 | Extensibility | A new component package with its declaration is installed        | It appears in the palette and its dialog renders without platform changes             | Catalog and interface tests             |
| QS09 | Usability     | A user configures an LLM Call                                     | No permissions, slots, wrappers or JSON appear in ordinary configuration             | Journey tests J1–J3                     |
| QS10 | Integrity     | The backend restarts during a run                                 | The run is marked failed with `interrupted`; open reservations are settled as estimated | Integration test                        |
| QS11 | Concurrency   | One output feeds several stateless nodes                          | Activations run concurrently up to `max_running_nodes`                                | Engine test                             |
| QS12 | Performance   | J3 with the simulated provider                                    | The run completes within 10 s on the reference machine, including host startup       | Journey test                            |
