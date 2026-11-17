import axios from 'axios'

export type FieldName = 'email' | 'password' | 'full_name'
export interface FormFeedback { message: string; fields?: Partial<Record<FieldName, string>> }

export function authError(error: unknown, registration = false): FormFeedback {
  if (!axios.isAxiosError(error)) return { message: 'Something went wrong. Please try again.' }
  if (!error.response) return { message: 'We couldn’t connect. Check your connection and try again.' }
  const status = error.response.status
  if (status === 401) return { message: 'Email or password is incorrect.' }
  if (status === 409 && registration) return { message: 'An account with this email already exists. Please sign in.' }
  if (status === 429) {
    const seconds = Number(error.response.headers['retry-after'])
    return { message: Number.isFinite(seconds) && seconds > 0
      ? `Too many attempts. Try again in ${Math.ceil(seconds)} seconds.`
      : 'Too many attempts. Please wait a moment and try again.' }
  }
  if (status === 422) {
    const fields: Partial<Record<FieldName, string>> = {}
    const detail: unknown = error.response.data?.detail
    if (Array.isArray(detail)) for (const item of detail) {
      const key: unknown = item.loc?.at(-1)
      if (key === 'email') fields.email = 'Enter a valid email address.'
      if (key === 'full_name') fields.full_name = 'Enter your name using 1–100 characters.'
      if (key === 'password') fields.password = registration
        ? 'Use a password with 15–128 characters.' : 'Enter your password using no more than 128 characters.'
    }
    return { message: 'Please check the highlighted fields.', fields }
  }
  return { message: 'We couldn’t complete your request. Please try again.' }
}
