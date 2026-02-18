import { create } from 'zustand'
import { authApi } from '@/api/auth'
import client from '@/api/client'
import type { AuthState, Organization, Profile } from '@/types/auth'
import {
  clearAuth,
  getAccessToken,
  getOrgId,
  getRefreshToken,
  setOrgId,
  setTokens,
} from '@/utils/token'

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  profile: null,
  accessToken: getAccessToken(),
  refreshToken: getRefreshToken(),
  org: null,
  isAuthenticated: !!getAccessToken(),
  isLoading: false,

  login: async (credentials) => {
    set({ isLoading: true })
    try {
      const { data } = await authApi.login(credentials.email, credentials.password)
      setTokens(data.access, data.refresh)
      set({
        accessToken: data.access,
        refreshToken: data.refresh,
        isAuthenticated: true,
        isLoading: false,
      })
      await get().fetchProfile()
    } catch (error) {
      set({ isLoading: false })
      throw error
    }
  },

  logout: () => {
    clearAuth()
    set({
      user: null,
      profile: null,
      accessToken: null,
      refreshToken: null,
      org: null,
      isAuthenticated: false,
    })
  },

  setOrg: (org: Organization) => {
    setOrgId(org.id)
    set({ org })
  },

  refreshAccessToken: async () => {
    const refreshToken = getRefreshToken()
    if (!refreshToken) return null
    try {
      const { data } = await authApi.refresh(refreshToken)
      setTokens(data.access, data.refresh || refreshToken)
      set({ accessToken: data.access })
      return data.access
    } catch {
      get().logout()
      return null
    }
  },

  fetchProfile: async () => {
    try {
      const orgId = getOrgId()
      const { data } = await client.get<Profile>('/profile/', {
        headers: orgId ? { org: orgId } : {},
      })
      set({
        user: data.user,
        profile: data,
        org: data.org,
      })
      if (data.org) {
        setOrgId(data.org.id)
      }
    } catch {
      // Profile fetch failed - user may need to select org
    }
  },
}))
