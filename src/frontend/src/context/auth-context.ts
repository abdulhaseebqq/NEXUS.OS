import { createContext } from "react"

import type {
  LoginData,
  LoginUser,
} from "../types/auth"

export type AuthContextValue = {
  user: LoginUser | null
  isAuthenticated: boolean
  accessToken: string | null
  login: (data: LoginData) => void
  logout: () => void
}

export const AuthContext =
  createContext<AuthContextValue | undefined>(
    undefined,
  )