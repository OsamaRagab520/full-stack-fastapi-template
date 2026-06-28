const TOKEN_KEY = "access_token"

// Single home for the access-token persistence mechanism. Everything that
// reads, writes, or clears the token goes through here, so switching storage
// (e.g. to cookies) is a one-file change.
export const tokenStore = {
  get(): string | null {
    return localStorage.getItem(TOKEN_KEY)
  },
  set(token: string): void {
    localStorage.setItem(TOKEN_KEY, token)
  },
  clear(): void {
    localStorage.removeItem(TOKEN_KEY)
  },
  isAuthenticated(): boolean {
    return localStorage.getItem(TOKEN_KEY) !== null
  },
}
