import {FakeApi} from './fake-api.ts';
import {catalogBody, j3} from './contract.ts';
import {j3Events} from './j3-events.ts';
import {runDetail, versionBody} from './runs.ts';

export const graphId = 'funny-story-with-review';

/** A fake operator API serving the recorded J3 run and the version it executed. */
export function activityApi(): FakeApi {
  return new FakeApi()
    .on('GET /catalog', {status: 200, body: catalogBody})
    .on('GET /runs/run-1', {status: 200, body: runDetail()})
    .on(`GET /graphs/${graphId}/versions/1`, {status: 200, body: versionBody(j3)})
    .on('GET /runs/run-1/events', {
      status: 200,
      body: {events: j3Events, last_seq: j3Events.length, finished: true},
    })
    .install();
}
