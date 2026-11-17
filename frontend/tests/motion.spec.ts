import { test, expect } from '@playwright/test'

test('discovery animation draws the route once and responds to reduced motion', async ({ page }) => {
  const errors: string[] = []
  page.on('pageerror', (error) => errors.push(error.message))
  await page.setViewportSize({ width: 1440, height: 900 })
  await page.emulateMedia({ reducedMotion: 'no-preference' })
  await page.goto('/login')
  await expect(page.getByRole('button', { name: 'Replay illustration' })).toHaveCount(0)
  const route = page.locator('.route-mask')
  await expect.poll(async () => Number(await route.evaluate((node) => getComputedStyle(node).strokeDashoffset.replace('px', '')))).toBe(0)
  await expect.poll(async () => Number(await page.locator('.saved-check').evaluate((node) => getComputedStyle(node).strokeDashoffset.replace('px', '')))).toBe(0)
  await page.screenshot({ path: 'test-results/screenshots/motion-complete.png', fullPage: true })
  // The halo shares the pin's motion group and stays centered as it expands.
  const alignment = await page.locator('.pin-motion').evaluate((group) => {
    const halo = group.querySelector<SVGCircleElement>('.pin-halo')!
    const outline = group.querySelector<SVGPathElement>('path')!.getBBox()
    return {
      x: Math.abs(halo.cx.baseVal.value - (outline.x + outline.width / 2)),
      y: Math.abs(halo.cy.baseVal.value - (outline.y + outline.height / 2)),
      transform: getComputedStyle(halo).transform,
    }
  })
  expect(alignment.x).toBeLessThan(0.1)
  expect(alignment.y).toBeLessThan(0.1)
  expect(alignment.transform).toBe('none')
  await page.waitForTimeout(700)
  await page.screenshot({ path: 'test-results/screenshots/motion-in-progress.png', fullPage: true })
  await page.emulateMedia({ reducedMotion: 'reduce' })
  await expect(route).toHaveCSS('stroke-dasharray', 'none')
  expect(await page.locator('.pin-motion').evaluate((node) => {
    const transform = getComputedStyle(node).transform
    return transform === 'none' || new DOMMatrix(transform).isIdentity
  })).toBe(true)
  await expect(page.locator('.pin-motion')).toHaveCSS('opacity', '1')
  await expect(page.getByLabel('Email address')).toBeEnabled()
  await page.setViewportSize({ width: 820, height: 1180 })
  await page.emulateMedia({ reducedMotion: 'no-preference' })
  await page.waitForTimeout(2800)
  await page.screenshot({ path: 'test-results/screenshots/motion-tablet.png', fullPage: true })
  await page.setViewportSize({ width: 390, height: 844 })
  expect(errors).toEqual([])
})
