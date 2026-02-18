const ACCESS_TOKEN_KEY = 'access_token'
const REFRESH_TOKEN_KEY = 'refresh_token'
const ORG_KEY = 'org'

export const getAccessToken = (): string | null =>
  localStorage.getItem(ACCESS_TOKEN_KEY)

export const getRefreshToken = (): string | null =>
  localStorage.getItem(REFRESH_TOKEN_KEY)

export const getOrgId = (): string | null =>
  localStorage.getItem(ORG_KEY)

export const setTokens = (access: string, refresh: string) => {
  localStorage.setItem(ACCESS_TOKEN_KEY, access)
  localStorage.setItem(REFRESH_TOKEN_KEY, refresh)
}

export const setOrgId = (orgId: string) => {
  localStorage.setItem(ORG_KEY, orgId)
}

export const clearAuth = () => {
  localStorage.removeItem(ACCESS_TOKEN_KEY)
  localStorage.removeItem(REFRESH_TOKEN_KEY)
  localStorage.removeItem(ORG_KEY)
}
