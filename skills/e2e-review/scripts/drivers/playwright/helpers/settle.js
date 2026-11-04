// Wait for network idle and running CSS animations/transitions before screenshots or layout checks
async (page) => {
    await page.waitForLoadState('networkidle')
    await page.evaluate(() => Promise.all(document.getAnimations().map((a) => a.finished.catch(() => null))))
    await page.waitForTimeout(150)
}
