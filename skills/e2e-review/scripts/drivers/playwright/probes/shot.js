// @driver playwright
// Viewport screenshot to shots/<--name>.png (default final). Use --full=1 for a full-page shot; fixed layouts may repeat headers mid-image.
async (page, P, H) => {
    if (!P.out) throw new Error('shot needs a task folder')
    const name = P.args.name ?? 'final'
    await H.settle(page)
    await page.screenshot({ path: `${P.out}/shots/${name}.png`, fullPage: Boolean(P.args.full) })
    return { file: `shots/${name}.png`, url: page.url() }
}
