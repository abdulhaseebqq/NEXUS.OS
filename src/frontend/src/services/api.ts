import type { ApiError } from "../types/auth"

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000/api/v1"

export class ApiRequestError extends Error {
  status: number
  code: string
  details: unknown

  constructor(
    message: string,
    status: number,
    code = "HTTP_ERROR",
    details: unknown = null,
  ) {
    super(message)

    this.name = "ApiRequestError"
    this.status = status
    this.code = code
    this.details = details
  }
}

export async function apiRequest<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  })

  const body = (await response.json()) as T | ApiError

  if (!response.ok) {
    const errorBody = body as ApiError

    throw new ApiRequestError(
      errorBody.message || "Request failed",
      response.status,
      errorBody.error?.code,
      errorBody.error?.details,
    )
  }

  return body as T
}