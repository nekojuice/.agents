// Recipes: .e2e/recipes/<name>.md, Markdown with a YAML front matter and one ```yaml block per step.
// Only a YAML subset is read (no third-party parser): scalars, block scalars (| and >) at the top level,
// one level of nested maps or lists, and single-line flow maps or lists ({a: 1, b: x}, [a, b]) or JSON.
// Format rules: references/recipes.md.
import { existsSync, readFileSync } from 'node:fs'
import { join, resolve } from 'node:path'

// Split a flow collection's inside on commas that are not inside quotes.
function splitFlow(inner) {
    const parts = []
    let cur = ''
    let quote = null
    for (const ch of inner) {
        if (quote) { if (ch === quote) quote = null; cur += ch; continue }
        if (ch === '"' || ch === "'") { quote = ch; cur += ch; continue }
        if (ch === ',') { parts.push(cur); cur = ''; continue }
        cur += ch
    }
    if (cur.trim()) parts.push(cur)
    return parts.map((p) => p.trim()).filter(Boolean)
}

function scalar(raw) {
    const v = raw.trim()
    if (v === '') return ''
    if (/^[[{]/.test(v)) {
        try { return JSON.parse(v) } catch { /* try the YAML flow form */ }
        if (v.startsWith('{') && v.endsWith('}'))
            return Object.fromEntries(splitFlow(v.slice(1, -1)).map((p) => {
                const i = p.indexOf(':')
                if (i <= 0) throw new Error(`recipe YAML: cannot read flow map entry "${p}"`)
                return [p.slice(0, i).trim().replace(/^(['"])(.*)\1$/, '$2'), scalar(p.slice(i + 1))]
            }))
        if (v.startsWith('[') && v.endsWith(']')) return splitFlow(v.slice(1, -1)).map(scalar)
        throw new Error(`recipe YAML: unbalanced flow value "${v}"`)
    }
    if (/^(['"]).*\1$/.test(v)) return v.slice(1, -1)
    if (v === 'true' || v === 'false') return v === 'true'
    if (v === 'null' || v === '~') return null
    if (/^-?\d+(\.\d+)?$/.test(v)) return Number(v)
    return v
}

export function parseYaml(text) {
    const out = {}
    let key = null
    let block = null // { key, fold, lines } while reading a | or > block scalar
    const endBlock = () => {
        if (!block) return
        out[block.key] = block.fold ? block.lines.join(' ').replace(/\s+/g, ' ').trim() : block.lines.join('\n').trimEnd()
        block = null
    }
    for (const line of text.split('\n')) {
        if (block && (/^\s+/.test(line) || !line.trim())) {
            block.lines.push(line.replace(/^\s{1,4}/, ''))
            continue
        }
        endBlock()
        if (!line.trim() || line.trim().startsWith('#')) continue
        const indented = /^\s+/.test(line)
        const t = line.trim()
        if (!indented) {
            const m = t.match(/^([\w-]+):\s*(.*)$/)
            if (!m) throw new Error(`recipe YAML: cannot read line "${t}"`)
            key = m[1]
            if (/^[|>][+-]?$/.test(m[2])) {
                block = { key, fold: m[2].startsWith('>'), lines: [] }
                continue
            }
            out[key] = m[2] === '' ? null : scalar(m[2])
            continue
        }
        if (!key) throw new Error(`recipe YAML: indented line without a key "${t}"`)
        if (t.startsWith('- ')) {
            if (!Array.isArray(out[key])) out[key] = []
            out[key].push(scalar(t.slice(2)))
        } else {
            const m = t.match(/^([\w-]+):\s*(.*)$/)
            if (!m) throw new Error(`recipe YAML: cannot read line "${t}"`)
            if (out[key] === null || typeof out[key] !== 'object' || Array.isArray(out[key])) out[key] = {}
            out[key][m[1]] = scalar(m[2])
        }
    }
    endBlock()
    return out
}

export function resolveRecipe(name, project) {
    const withExt = name.endsWith('.md') ? name : `${name}.md`
    const hit = [resolve(withExt), project.assets && join(project.assets, 'recipes', withExt)].filter(Boolean).find((p) => existsSync(p))
    if (!hit) throw new Error(`recipe not found: ${name}`)
    return hit
}

export function loadRecipe(file) {
    const text = readFileSync(file, 'utf8').replace(/\r\n/g, '\n')
    const fm = text.match(/^---\n([\s\S]*?)\n---/)
    const meta = fm ? parseYaml(fm[1]) : {}
    const steps = [...text.matchAll(/```ya?ml\n([\s\S]*?)```/g)].map((m) => parseYaml(m[1]))
    for (const s of steps) {
        if (!s.id) throw new Error(`${file}: a step block has no id`)
        if (s.kind !== 'script' && s.kind !== 'agent') throw new Error(`${file}#${s.id}: kind must be script or agent`)
        if (s.kind === 'script' && !s.run) throw new Error(`${file}#${s.id}: script steps need run`)
        if (s.args != null && (typeof s.args !== 'object' || Array.isArray(s.args))) throw new Error(`${file}#${s.id}: args must be a map`)
        if (!s.surface) throw new Error(`${file}#${s.id}: every step needs surface`)
        // run without a surface prefix uses the step's surface; a different prefix is an error.
        if (s.kind === 'script') {
            const m = String(s.run).match(/^([a-z][\w-]*):(?![\\/])/i)
            if (!m) s.run = `${s.surface}:${s.run}`
            else if (m[1] !== s.surface) throw new Error(`${file}#${s.id}: run targets surface ${m[1]} but the step says ${s.surface}`)
        }
    }
    const ids = steps.map((s) => s.id)
    const dup = ids.find((id, i) => ids.indexOf(id) !== i)
    if (dup) throw new Error(`${file}: duplicate step id ${dup}`)
    return { file, meta, steps }
}

// "<recipe>#<id>" → { recipe, step }
export function findStep(ref, project) {
    const [name, id] = String(ref).split('#')
    if (!id) throw new Error('step reference must be <recipe>#<id>')
    const recipe = loadRecipe(resolveRecipe(name, project))
    const step = recipe.steps.find((s) => String(s.id) === id)
    if (!step) throw new Error(`no step ${id} in ${recipe.file}`)
    return { name: name.replace(/\.md$/, ''), recipe, step }
}
