// Called by `e2e.mjs sheet`: screenshot the generated contact-sheet HTML pages (local file:// only) for visual layout review.
async (page, P) => {
    const out = []
    for (let i = 1; i <= Number(P.args.n); i++) {
        await page.goto(`${P.args.base}/review/sheet-${i}.html`)
        await page.setViewportSize({ width: 1284, height: 1460 })
        await page.screenshot({ path: `${P.out}/review/sheet-${i}.png`, fullPage: true })
        out.push(`review/sheet-${i}.png`)
    }
    await page.setViewportSize({ width: 1280, height: 720 })
    return out
}
