import { BrowserRouter, Navigate, Route, Routes } from 'react-router'
import { AuthLayout } from './components/layout/AuthLayout'
import { AuthProvider } from './features/auth/AuthProvider'
import { AuthPage } from './features/auth/components/AuthPage'
import { AccountPage } from './features/auth/components/AccountPage'
import './App.css'

export default function App() {
  return <BrowserRouter><AuthProvider><Routes>
    <Route element={<AuthLayout />}>
      <Route path="/login" element={<AuthPage mode="login" />} />
      <Route path="/register" element={<AuthPage mode="register" />} />
      <Route path="/forgot-password" element={<AuthPage mode="recovery" />} />
      <Route path="/account" element={<AccountPage />} />
    </Route>
    <Route path="*" element={<Navigate to="/login" replace />} />
  </Routes></AuthProvider></BrowserRouter>
}
