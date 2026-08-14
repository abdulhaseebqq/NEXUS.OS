export type ApiError = {
  success: false
  message: string
  error: {
    code: string
    details: unknown
  }
}

export type ApiSuccess<T> = {
  success: true
  message: string
  data: T
}

export type SignupRequest = {
  full_name: string
  email: string
  password: string
}

export type SignupData = {
  email: string
  role: string
  is_active: boolean
  is_email_verified: boolean
  verification: {
    token: string
    expires_at: string
  }
}

export type SignupResponse = ApiSuccess<SignupData>

export type VerifyEmailRequest = {
  token: string
}

export type VerifyEmailData = {
  email: string
  is_email_verified: boolean
}

export type VerifyEmailResponse = ApiSuccess<VerifyEmailData>

export type LoginRequest = {
  email: string
  password: string
}

export type LoginUser = {
  id?: number
  full_name?: string
  email: string
  role?: string
  is_active?: boolean
  is_email_verified: boolean
  profile_image?: string | null
}

export type LoginSession = {
  id: number
  device_name: string
  ip_address: string
  user_agent?: string
  last_activity?: string
}

export type LoginData = {
  access_token: string
  refresh_token: string
  token_type: string
  user: LoginUser
  session: LoginSession
}

export type LoginResponse = ApiSuccess<LoginData>