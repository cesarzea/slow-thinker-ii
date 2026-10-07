const MAX_SLUG = 59;

/** The lowercase, hyphenated form of a name that starts with a letter. */
export function graphSlug(name: string): string {
  const words = name
    .normalize('NFKD')
    .replaceAll(/[\u0300-\u036f]/gu, '')
    .toLowerCase()
    .split(/[^a-z0-9]+/u)
    .filter((word) => word !== '');
  const slug = words.join('-');
  const lettered = /^[a-z]/u.test(slug) ? slug : ['graph', ...words].join('-');
  return lettered
    .slice(0, MAX_SLUG)
    .split('-')
    .filter((word) => word !== '')
    .join('-');
}

function randomHex(): string {
  const bytes = crypto.getRandomValues(new Uint8Array(2));
  return [...bytes].map((byte) => byte.toString(16).padStart(2, '0')).join('');
}

/** A new graph identifier: the name's slug plus four random hexadecimal characters. */
export function graphId(name: string, suffix: string = randomHex()): string {
  return `${graphSlug(name)}-${suffix}`;
}
