import axios from 'axios'

export type ApiErrorCode =
  | 'bad_request'
  | 'unauthorized'
  | 'invalid_credentials'
  | 'forbidden'
  | 'not_found'
  | 'conflict'
  | 'email_already_registered'
  | 'rate_limited'
  | 'validation_error'
  | 'database_error'
  | 'internal_error'
  | 'network_error'
  | 'request_timeout'
  | 'unknown_error'

export class ApiError extends Error {
  readonly code: ApiErrorCode
  readonly status: number | null
  readonly details: unknown
  readonly retryAfterSeconds: number | null

  constructor(
    code: ApiErrorCode,
    status: number | null,
    details: unknown = null,
    retryAfterSeconds: number | null = null,
  ) {
    super(code)
    this.name = 'ApiError'
    this.code = code
    this.status = status
    this.details = details
    this.retryAfterSeconds = retryAfterSeconds
  }
}

function fallbackCode(status: number): ApiErrorCode {
  return ({
    400: 'bad_request',
    401: 'unauthorized',
    403: 'forbidden',
    404: 'not_found',
    409: 'conflict',
    422: 'validation_error',
    429: 'rate_limited',
    500: 'internal_error',
  } as Record<number, ApiErrorCode>)[status] ?? 'unknown_error'
}

function knownCode(value: unknown, status: number): ApiErrorCode {
  const supported: ApiErrorCode[] = [
    'bad_request', 'unauthorized', 'invalid_credentials', 'forbidden', 'not_found',
    'conflict', 'email_already_registered', 'rate_limited', 'validation_error',
    'database_error', 'internal_error',
  ]
  return typeof value === 'string' && supported.includes(value as ApiErrorCode)
    ? value as ApiErrorCode
    : fallbackCode(status)
}

function retryAfterSeconds(value: unknown): number | null {
  if (typeof value !== 'string' && typeof value !== 'number') return null
  const seconds = Number(value)
  if (Number.isFinite(seconds) && seconds > 0) return Math.ceil(seconds)
  const date = Date.parse(String(value))
  if (!Number.isFinite(date)) return null
  return Math.max(1, Math.ceil((date - Date.now()) / 1000))
}

export function parseApiError(error: unknown): ApiError {
  if (error instanceof ApiError) return error
  if (!axios.isAxiosError(error)) return new ApiError('unknown_error', null)
  if (error.code === 'ECONNABORTED' || error.code === 'ETIMEDOUT') {
    return new ApiError('request_timeout', null)
  }
  if (!error.response) return new ApiError('network_error', null)

  const status = error.response.status
  const data: unknown = error.response.data
  const payload = typeof data === 'object' && data !== null
    ? data as { code?: unknown; detail?: unknown }
    : {}
  return new ApiError(
    knownCode(payload.code, status),
    status,
    payload.detail ?? null,
    retryAfterSeconds(error.response.headers['retry-after']),
  )
}

export function apiErrorMessage(error: ApiError): string {
  switch (error.code) {
    case 'network_error':
      return 'We couldn’t connect. Check your connection and try again.'
    case 'request_timeout':
      return 'The request took too long. Check your connection and try again.'
    case 'forbidden':
      return 'You don’t have access to complete this action.'
    case 'not_found':
      return 'We couldn’t find what you requested. It may have moved or been removed.'
    case 'rate_limited':
      return error.retryAfterSeconds
        ? `Too many attempts. Try again in ${error.retryAfterSeconds} seconds.`
        : 'Too many attempts. Please wait a moment and try again.'
    case 'bad_request':
    case 'validation_error':
      return 'Please check the information and try again.'
    case 'conflict':
      return 'This information changed while you were working. Refresh and try again.'
    case 'unauthorized':
      return 'Your session has expired. Sign in again to continue.'
    case 'database_error':
    case 'internal_error':
    case 'unknown_error':
    default:
      return 'We couldn’t complete your request. Please try again.'
  }
}
