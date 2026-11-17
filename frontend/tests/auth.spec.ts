import { test, expect } from '@playwright/test'

const profile = { id: 'user-1', full_name: 'Mouad Example', email: 'owner@example.com', created_at: '2026-11-17T12:00:00Z' }
const response = { access_token: 'test-token', token_type: 'bearer', expires_in: 86400, user: profile }

test('register, login, protected account and server logout', async ({ page }) => {
  let registerBody: unknown
  let bearer = ''
  let revoked = false
  await page.route('**/api/v1/auth/**', async (route) => {
    const request = route.request()
    const endpoint = new URL(request.url()).pathname.split('/').at(-1)
    if (endpoint === 'register') registerBody = request.postDataJSON()
    if (endpoint === 'me') bearer = request.headers()['authorization'] || ''
    if (endpoint === 'logout') revoked = true
    await route.fulfill({ status: endpoint === 'register' ? 201 : endpoint === 'logout' ? 204 : 200,
      contentType: 'application/json', body: endpoint === 'logout' ? undefined : JSON.stringify(endpoint === 'login' ? response : profile) })
  })
  await page.goto('/login')
  await page.getByLabel('Email address').fill(profile.email)
  await page.getByRole('link', { name: 'Create an account' }).click()
  await expect(page.getByLabel('Email address')).toHaveValue(profile.email)
  await page.getByLabel('Full name').fill('  Mouad Example  ')
  await page.getByLabel('Password', { exact: true }).fill('a long private passphrase')
  await page.getByRole('button', { name: 'Show password' }).click()
  await expect(page.getByLabel('Password', { exact: true })).toHaveAttribute('type', 'text')
  await page.getByRole('button', { name: 'Hide password' }).click()
  await page.getByRole('button', { name: 'Create account', exact: true }).click()
  await expect(page.getByText('Your account is ready.')).toBeVisible()
  expect(registerBody).toEqual({ full_name: profile.full_name, email: profile.email, password: 'a long private passphrase' })
  await expect(page.getByLabel('Password', { exact: true })).toHaveValue('')
  await page.getByLabel('Password', { exact: true }).fill('a long private passphrase')
  await page.getByRole('button', { name: 'Sign in', exact: true }).click()
  await expect(page.getByRole('heading', { name: 'You’re signed in.' })).toBeVisible()
  expect(bearer).toBe('Bearer test-token')
  expect(await page.evaluate(() => ({ local: Object.keys(localStorage), session: Object.keys(sessionStorage) }))).toEqual({ local: [], session: [] })
  await page.getByRole('button', { name: 'Sign out' }).click()
  await expect(page.getByRole('heading', { name: 'Welcome back.' })).toBeVisible()
  expect(revoked).toBe(true)
  await page.goto('/account')
  await expect(page).toHaveURL(/\/login$/)
})

test('validation matches API, preserves non-secret fields and supports keyboard navigation', async ({ page }) => {
  let requests = 0
  await page.route('**/api/v1/**', async (route) => { requests++; await route.abort() })
  await page.goto('/register')
  await page.keyboard.press('Tab')
  await expect(page.getByLabel('Full name')).toBeFocused()
  await page.getByRole('button', { name: 'Create account', exact: true }).click()
  await expect(page.getByText('Enter your name.')).toBeVisible()
  await page.getByLabel('Full name').fill('مُعاذ')
  await page.getByLabel('Email address').fill(profile.email)
  await page.getByLabel('Password', { exact: true }).fill('short')
  await page.getByRole('button', { name: 'Create account', exact: true }).click()
  await expect(page.getByText('Use at least 15 characters.')).toBeVisible()
  expect(requests).toBe(0)
  await page.getByRole('link', { name: 'Sign in', exact: true }).click()
  await expect(page.getByLabel('Email address')).toHaveValue(profile.email)
  await expect(page.getByLabel('Password', { exact: true })).toHaveValue('')
  await page.getByRole('link', { name: 'Forgot password?' }).click()
  await expect(page.getByText('Password recovery is coming soon.')).toBeVisible()
  await expect(page.getByRole('button', { name: 'Send reset link' })).toHaveCount(0)
  expect(requests).toBe(0)
})

test('loading, invalid credentials, throttling and connection recovery', async ({ page }) => {
  let attempt = 0
  await page.route('**/api/v1/auth/login', async (route) => {
    attempt++
    if (attempt === 1) {
      await new Promise((resolve) => setTimeout(resolve, 250))
      await route.fulfill({ status: 401, json: { detail: 'Invalid or expired credentials' } })
    } else if (attempt === 2) await route.fulfill({ status: 429, headers: { 'Retry-After': '30' }, json: {} })
    else await route.abort('connectionfailed')
  })
  await page.goto('/login')
  await page.getByLabel('Email address').fill(profile.email)
  await page.getByLabel('Password', { exact: true }).fill('a long private passphrase')
  await page.getByRole('button', { name: 'Sign in', exact: true }).click()
  await expect(page.getByRole('button', { name: 'Signing in…' })).toBeDisabled()
  await expect(page.getByRole('alert')).toHaveText('Email or password is incorrect.')
  await page.getByRole('button', { name: 'Sign in', exact: true }).click()
  await expect(page.getByRole('alert')).toContainText('Too many attempts.')
  await page.getByRole('button', { name: 'Sign in', exact: true }).click()
  await expect(page.getByRole('alert')).toContainText('We couldn’t connect.')
  await expect(page.getByLabel('Email address')).toHaveValue(profile.email)
  await expect(page.getByRole('button', { name: 'Sign in', exact: true })).toBeEnabled()
})

test('registration conflict and server validation are visible', async ({ page }) => {
  let attempts = 0
  await page.route('**/api/v1/auth/register', async (route) => {
    attempts++
    await route.fulfill(attempts === 1 ? { status: 409, json: {} } : {
      status: 422, json: { detail: [{ loc: ['body', 'email'], msg: 'Invalid email', type: 'value_error' }] },
    })
  })
  await page.goto('/register')
  await page.getByLabel('Full name').fill(profile.full_name)
  await page.getByLabel('Email address').fill(profile.email)
  await page.getByLabel('Password', { exact: true }).fill('a long private passphrase')
  await page.getByRole('button', { name: 'Create account', exact: true }).click()
  await expect(page.getByRole('alert')).toContainText('already exists')
  await page.getByRole('button', { name: 'Create account', exact: true }).click()
  await expect(page.getByLabel('Email address')).toHaveAttribute('aria-invalid', 'true')
  await expect(page.getByText('Enter a valid email address.', { exact: true })).toBeVisible()
})

test('responsive reference layouts load local assets without overflow', async ({ page }) => {
  const errors: string[] = []
  page.on('pageerror', (error) => errors.push(error.message))
  const sizes = [[360, 800], [390, 844], [430, 932], [600, 960], [820, 1180], [1024, 768], [1366, 768], [1440, 900], [1920, 1080]]
  for (const [width, height] of sizes) {
    await page.setViewportSize({ width, height })
    for (const route of ['login', 'register', 'forgot-password']) {
      await page.goto(`/${route}`)
      await page.evaluate(() => document.fonts.ready)
      expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true)
      expect(await page.locator('img').evaluateAll((nodes) => nodes.every((node) => node.complete && node.naturalWidth > 0))).toBe(true)
      expect(await page.evaluate(() => document.fonts.check('16px "DM Sans"') && document.fonts.check('44px "Instrument Serif"'))).toBe(true)
      await page.screenshot({ path: `test-results/screenshots/${route}-${width}.png`, fullPage: true })
    }
  }
  expect(errors).toEqual([])
})
