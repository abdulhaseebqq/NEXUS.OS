import { apiRequest } from "./api"

import type {
  LoginRequest,
  LoginResponse,
  SignupRequest,
  SignupResponse,
  VerifyEmailRequest,
  VerifyEmailResponse,
} from "../types/auth"

export function signup(
  payload: SignupRequest,
): Promise<SignupResponse> {
  return apiRequest<SignupResponse>("/users/signup", {
    method: "POST",
    body: JSON.stringify(payload),
  })
}

export function verifyEmail(
  payload: VerifyEmailRequest,
): Promise<VerifyEmailResponse> {
  return apiRequest<VerifyEmailResponse>(
    "/users/verify-email",
    {
      method: "POST",
      body: JSON.stringify(payload),
    },
  )
}

export function login(
  payload: LoginRequest,
): Promise<LoginResponse> {
  return apiRequest<LoginResponse>("/users/login", {
    method: "POST",
    body: JSON.stringify(payload),
  })
}