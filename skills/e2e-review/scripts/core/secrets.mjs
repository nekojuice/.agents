// Value-based redaction: every artifact passes through redact() so passwords, tokens, and cookies never land on disk.
const values = new Set()

// Register a secret value (account password, token, cookie). Short values are ignored to avoid masking ordinary text.
export function addSecret(v) {
    const s = v == null ? '' : String(v)
    if (s.length >= 4) values.add(s)
}

// Every string field of an account entry is secret except userId and note (e.g. password, a second password for a change test).
export const PUBLIC_ACCOUNT_FIELDS = ['userId', 'note']
export function addAccountSecrets(accounts) {
    for (const a of Object.values(accounts ?? {}))
        for (const [k, v] of Object.entries(a ?? {})) if (!PUBLIC_ACCOUNT_FIELDS.includes(k) && typeof v === 'string') addSecret(v)
}

// Key names that hold secrets: exact short names, or names ending in a secret word (camelCase, snake_case, kebab-case).
// Ordinary fields such as passed, passDate, passport, or tokenCount stay readable.
const SECRET_KEY = /^(pass|pwd|jwt|sid)$|(password|passwd|secret|token|credential|cookie|authorization|apikey|api[_-]key|session[_-]?id)$/i

// Replace registered secret values anywhere in strings; values under secret-looking keys are masked whole.
export function redact(x) {
    if (typeof x === 'string') {
        let s = x
        for (const v of values) if (s.includes(v)) s = s.split(v).join('<redacted>')
        return s
    }
    if (Array.isArray(x)) return x.map(redact)
    if (x && typeof x === 'object')
        return Object.fromEntries(Object.entries(x).map(([k, v]) => [k, SECRET_KEY.test(k) && v != null && v !== '' ? '<redacted>' : redact(v)]))
    return x
}

export const isSecretKey = (k) => SECRET_KEY.test(k)
