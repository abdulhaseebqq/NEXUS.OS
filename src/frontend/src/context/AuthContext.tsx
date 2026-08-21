import {
  useCallback,
  useMemo,
  useState,
} from "react"
import type { ReactNode } from "react"

import { AuthContext } from "./auth-context"
import type {
  LoginData,
  LoginUser,
} from "../types/auth"

const ACCESS_TOKEN_KEY = "nexus_access_token"
const REFRESH_TOKEN_KEY = "nexus_refresh_token"
const USER_KEY = "nexus_user"

type AuthProviderProps = {
  children: ReactNode
}

function getStoredUser(): LoginUser | null {
  const storedUser =
    sessionStorage.getItem(USER_KEY)

  if (!storedUser) {
    return null
  }

  try {
    return JSON.parse(storedUser) as LoginUser
  } catch {
    sessionStorage.removeItem(USER_KEY)
    return null
  }
}

export function AuthProvider({
  children,
}: AuthProviderProps) {
  const [user, setUser] =
    useState<LoginUser | null>(() =>
      getStoredUser(),
    )

  const [accessToken, setAccessToken] =
    useState<string | null>(() =>
      sessionStorage.getItem(
        ACCESS_TOKEN_KEY,
      ),
    )

  const login = useCallback(
    (data: LoginData) => {
      sessionStorage.setItem(
        ACCESS_TOKEN_KEY,
        data.access_token,
      )

      sessionStorage.setItem(
        REFRESH_TOKEN_KEY,
        data.refresh_token,
      )

      sessionStorage.setItem(
        USER_KEY,
        JSON.stringify(data.user),
      )

      setAccessToken(data.access_token)
      setUser(data.user)
    },
    [],
  )

  const logout = useCallback(() => {
    sessionStorage.removeItem(
      ACCESS_TOKEN_KEY,
    )

    sessionStorage.removeItem(
      REFRESH_TOKEN_KEY,
    )

    sessionStorage.removeItem(USER_KEY)

    setAccessToken(null)
    setUser(null)
  }, [])

  const isAuthenticated =
    Boolean(accessToken && user)

  const value = useMemo(
    () => ({
      user,
      isAuthenticated,
      accessToken,
      login,
      logout,
    }),
    [
      user,
      isAuthenticated,
      accessToken,
      login,
      logout,
    ],
  )

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}