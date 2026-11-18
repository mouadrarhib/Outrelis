import { test, expect } from '@playwright/test'
import { execFileSync } from 'node:child_process'
import { randomUUID } from 'node:crypto'
import { resolve } from 'node:path'

test('real FastAPI registration, profile and session revocation', async ({ page, request }) => {
  test.skip(process.env.LIVE_API !== '1', 'Opt-in local PostgreSQL integration test')
  const email = `auth-browser-${randomUUID()}@example.com`
  let token = ''
  try {
    await page.goto('/register')
    await page.getByLabel('Full name').fill('Browser Integration Test')
    await page.getByLabel('Email address').fill(email)
    await page.getByLabel('Password', { exact: true }).fill('a browser test passphrase')
    await page.getByRole('button', { name: 'Create account', exact: true }).click()
    await expect(page.getByText('Your account is ready.')).toBeVisible()
    await page.getByLabel('Password', { exact: true }).fill('a browser test passphrase')
    const loginResponse = page.waitForResponse((response) => response.url() === 'http://127.0.0.1:8000/api/v1/auth/login')
    await page.getByRole('button', { name: 'Sign in', exact: true }).click()
    token = (await (await loginResponse).json()).access_token
    await expect(page.getByRole('heading', { name: 'What would you like to do first?' })).toBeVisible()
    await page.getByRole('radio', { name: 'Find my first leads' }).click()
    await page.getByRole('button', { name: 'Continue' }).click()
    await expect(page.getByRole('heading', { name: 'You’re signed in.' })).toBeVisible()
    await expect(page.getByText(email, { exact: true })).toBeVisible()
    await page.getByRole('button', { name: 'Sign out' }).click()
    await expect(page.getByRole('heading', { name: 'Welcome back.' })).toBeVisible()
    const revoked = await request.get('http://127.0.0.1:8000/api/v1/auth/me', { headers: { Authorization: `Bearer ${token}` } })
    expect(revoked.status()).toBe(401)
  } finally {
    // Remove only this run's randomly named local test account; sessions cascade.
    execFileSync(resolve('../backend/.venv/bin/python'), ['-c', `
import sys
from sqlalchemy import delete
from app.db import get_engine
from app.features.auth.models import User
with get_engine().begin() as connection:
    connection.execute(delete(User).where(User.email == sys.argv[1]))
`, email], { cwd: resolve('../backend'), stdio: 'pipe' })
  }
})
