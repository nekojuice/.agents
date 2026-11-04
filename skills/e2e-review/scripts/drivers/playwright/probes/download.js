// @driver playwright
// Capture a file download started by a control on the current page and save it to downloads/ in the step's folder.
// Args: --button=<accessible name> or --link=<text> (first match is clicked), --name=<file name> (default: the suggested name),
// --timeout=<ms> (default 30000). Returns { file, suggested, url }. Read the saved file with a project tool (see tools.md).
async (page, P) => {
    if (!P.out) throw new Error('download needs a task folder')
    const target = P.args.button ? page.getByRole('button', { name: P.args.button }) : P.args.link ? page.getByRole('link', { name: P.args.link }) : null
    if (!target) throw new Error('download needs --button=<name> or --link=<text>')
    const timeout = Number(P.args.timeout ?? 30000)
    const [dl] = await Promise.all([page.waitForEvent('download', { timeout }), target.first().click({ timeout })])
    const suggested = dl.suggestedFilename()
    const name = String(P.args.name ?? suggested).replace(/[\\/:*?"<>|]+/g, '_')
    await dl.saveAs(`${P.out}/downloads/${name}`)
    return { file: `downloads/${name}`, suggested, url: dl.url() }
}
