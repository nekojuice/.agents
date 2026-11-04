// Generic UI lint within `scope` (CSS selector, default whole page). Returns [{ type, rule, what, samples }].
// Rules depending on a specific component library belong to the project (.e2e/helpers/uiLintExtra.js).
async (page, scope) => {
    await page.evaluate(() => Promise.all(document.getAnimations().map((a) => a.finished.catch(() => null))))
    return await page.evaluate((scopeSel) => {
        const root = scopeSel ? document.querySelector(scopeSel) : document.body
        if (!root) return []
        const visible = (el) => {
            const r = el.getBoundingClientRect()
            const cs = getComputedStyle(el)
            // Skip screen-reader-only text (1px boxes or clipped away)
            return r.width > 2 && r.height > 2 && cs.visibility !== 'hidden' && cs.display !== 'none' && cs.clip !== 'rect(0px, 0px, 0px, 0px)' && cs.clipPath !== 'inset(50%)'
        }
        const text = (el) => (el.innerText ?? el.textContent ?? '').trim().replace(/\s+/g, ' ')
        const uniq = (arr) => [...new Set(arr)].slice(0, 5)
        const out = []
        const add = (type, rule, what, samples) => samples.length && out.push({ type, rule, what, samples: uniq(samples) })

        const leaves = [...root.querySelectorAll('*')].filter((el) => visible(el) && [...el.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim()))
        add('display', 'iso-datetime', 'Timestamp shown in raw ISO format',
            leaves.map(text).filter((t) => /\d{4}-\d{2}-\d{2}T\d{2}:\d{2}/.test(t)))
        add('layout', 'clipped-text', 'Text clipped by its container',
            leaves.filter((el) => {
                const cs = getComputedStyle(el)
                const hidden = /hidden|clip/.test(cs.overflow + cs.overflowY + cs.overflowX)
                return hidden && (el.scrollHeight > el.clientHeight + 2 || (cs.textOverflow !== 'ellipsis' && el.scrollWidth > el.clientWidth + 2))
            }).map(text).concat(
                [...root.querySelectorAll('*')].filter((box) => {
                    const cs = getComputedStyle(box)
                    return visible(box) && /hidden|clip/.test(cs.overflow + cs.overflowY) && box.scrollHeight > box.clientHeight + 2 && box.clientHeight > 0 && box.clientHeight < 60 && text(box)
                }).map(text)))
        add('layout', 'stacked-header', 'Table header squeezed into three or more lines',
            [...root.querySelectorAll('th')].filter((th) => {
                // Judge by lines the header text actually occupies, not by cell height
                const t = text(th).replace(/[↑↓⇅\s]/g, '')
                const label = th.querySelector('.p-datatable-column-title') ?? th
                const lh = parseFloat(getComputedStyle(label).lineHeight) || 20
                // Count distinct text line tops; spanning header cells are tall by design
                const tops = new Set()
                const walker = document.createTreeWalker(label, NodeFilter.SHOW_TEXT)
                for (let n = walker.nextNode(); n; n = walker.nextNode()) {
                    if (!n.textContent.trim()) continue
                    const rg = document.createRange()
                    rg.selectNodeContents(n)
                    for (const rect of rg.getClientRects()) if (rect.width > 0) tops.add(Math.round(rect.top / (lh / 2)))
                }
                const lines = tops.size
                return visible(th) && t.length >= 3 && lines >= 3 && lines >= t.length * 0.6
            }).map(text))
        add('display', 'readonly-counter', 'Read-only field still shows a character counter',
            [...root.querySelectorAll('input:disabled, textarea:disabled')].filter((inp) => {
                // Only the input's own wrapper or next sibling counts, so neighbouring fields are not picked up
                const near = [inp.parentElement, inp.nextElementSibling].filter(Boolean)
                return near.some((el) => [el, ...el.children].some((c) => /^\d+ \/ \d+$/.test(text(c))))
            }).map((inp) => (inp.id && root.querySelector(`label[for="${inp.id}"]`)?.textContent.trim()) || inp.getAttribute('aria-label') || inp.id || 'input'))
        if (!scopeSel && document.documentElement.scrollWidth > document.documentElement.clientWidth + 1)
            out.push({ type: 'layout', rule: 'overflow-x', what: 'Page has a horizontal scrollbar', samples: [] })
        return out
    }, scope ?? null)
}
