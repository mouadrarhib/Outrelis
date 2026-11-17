export interface User {
  id: string
  full_name: string | null
  email: string
  created_at: string
}
export interface Credentials { email: string; password: string }
export interface Registration extends Credentials { full_name: string }
export interface LoginResponse {
  access_token: string
  token_type: 'bearer'
  expires_in: number
  user: User
}
