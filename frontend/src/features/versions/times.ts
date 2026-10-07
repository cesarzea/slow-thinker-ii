const clock = new Intl.DateTimeFormat('en', {hour: '2-digit', minute: '2-digit', hourCycle: 'h23'});
const calendar = new Intl.DateTimeFormat('en', {month: 'short', day: 'numeric'});

function sameDay(date: Date, now: Date): boolean {
  return date.toDateString() === now.toDateString();
}

/** “10:42” for a time of today, otherwise the day, “Oct 3”. */
export function shortTime(at: string, now: Date = new Date()): string {
  const date = new Date(at);
  return sameDay(date, now) ? clock.format(date) : calendar.format(date);
}

/** “Today 10:31”, or “Oct 3 10:31” for another day. */
export function dayTime(at: string, now: Date = new Date()): string {
  const date = new Date(at);
  return `${sameDay(date, now) ? 'Today' : calendar.format(date)} ${clock.format(date)}`;
}

/** “10:42”: the time of day only. */
export function clockTime(at: string): string {
  return clock.format(new Date(at));
}
