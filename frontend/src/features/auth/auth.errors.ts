import { apiErrorMessage, parseApiError } from '../../lib/api-error'

export type FieldName = 'email' | 'password' | 'full_name'
export interface FormFeedback { message: string; fields?: Partial<Record<FieldName, string>> }

export function authError(error: unknown, registration = false): FormFeedback {
  const apiError = parseApiError(error)
  if (apiError.code === 'invalid_credentials' || apiError.status === 401) {
    return { message: 'Email or password is incorrect.' }
  }
  if (apiError.code === 'email_already_registered' || (apiError.status === 409 && registration)) {
    return { message: 'An account with this email already exists. Please sign in.' }
  }
  if (apiError.code === 'validation_error') {
    const fields: Partial<Record<FieldName, string>> = {}
    const detail = apiError.details
    if (Array.isArray(detail)) for (const item of detail) {
      const key: unknown = typeof item === 'object' && item !== null && 'loc' in item && Array.isArray(item.loc)
        ? item.loc.at(-1)
        : null
      if (key === 'email') fields.email = 'Enter a valid email address.'
      if (key === 'full_name') fields.full_name = 'Enter your name using 1–100 characters.'
      if (key === 'password') fields.password = registration
        ? 'Use a password with 8–128 characters.' : 'Enter your password using no more than 128 characters.'
    }
    return { message: 'Please check the highlighted fields.', fields }
  }
  return { message: apiErrorMessage(apiError) }
}
