export interface User {
  id: string
  email: string
  profile_pic: string | null
  is_active: boolean
}

export interface Profile {
  id: string
  user: User
  role: 'ADMIN' | 'USER'
  phone: string | null
  org: Organization
  is_organization_admin: boolean
}

export interface Organization {
  id: string
  name: string
  api_key: string
}

export interface LoginCredentials {
  email: string
  password: string
}

export interface TokenResponse {
  access: string
  refresh: string
}

export interface AuthState {
  user: User | null
  profile: Profile | null
  accessToken: string | null
  refreshToken: string | null
  org: Organization | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (credentials: LoginCredentials) => Promise<void>
  logout: () => void
  setOrg: (org: Organization) => void
  refreshAccessToken: () => Promise<string | null>
  fetchProfile: () => Promise<void>
}
