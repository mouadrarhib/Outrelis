import { http } from '../../../lib/http'
import type { Credentials, LoginResponse, Registration, User } from '../auth.types'

export async function registerAccount(data: Registration, signal?: AbortSignal) {
  return (await http.post<User>('/auth/register', data, { signal })).data
}
export async function loginAccount(data: Credentials, signal?: AbortSignal) {
  return (await http.post<LoginResponse>('/auth/login', data, { signal })).data
}
export async function currentUser(signal?: AbortSignal) {
  return (await http.get<User>('/auth/me', { signal })).data
}
export async function logoutAccount() { await http.post('/auth/logout') }
