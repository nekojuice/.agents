// Run generic UI lint (H.uiLint) plus the project's extra rules (H.uiLintExtra, optional) on the current screen.
// Args: --scope=<CSS selector>, --shot=<name>. Returns { findings, shot }.
async (page, P, H) => {
    await H.settle(page)
    const findings = [...(await H.uiLint(page, P.args.scope)), ...(H.uiLintExtra ? await H.uiLintExtra(page, P.args.scope) : [])]
    const shot = P.out && P.args.shot ? `shots/${P.args.shot}.png` : null
    if (shot) await page.screenshot({ path: `${P.out}/${shot}` })
    return { findings, shot }
}
