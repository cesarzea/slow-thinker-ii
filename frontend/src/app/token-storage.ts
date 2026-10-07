const KEY = 'slow-thinker-ii.operator-token';

/** The operator token kept for this tab, or `null` when none is kept or storage fails. */
export function storedToken(): string | null {
  try {
    const token = sessionStorage.getItem(KEY)?.trim() ?? '';
    return token === '' ? null : token;
  } catch {
    return null;
  }
}

/** Keep the operator token for this tab, so that a reload reconnects; failures are ignored. */
export function storeToken(token: string): void {
  try {
    sessionStorage.setItem(KEY, token);
  } catch {
    return;
  }
}

export function forgetToken(): void {
  try {
    sessionStorage.removeItem(KEY);
  } catch {
    return;
  }
}
