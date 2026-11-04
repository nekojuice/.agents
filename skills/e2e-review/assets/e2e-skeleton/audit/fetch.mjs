// Audit adapter: return audit rows written by the tested system within [from, to] for the given users.
// Contract (references/project-profile.md): export default async ({ from, to, users, env, config }) => rows
// Each row: { time: 'yyyy-MM-ddTHH:mm:ss[.fff]' (local), user, action, target, detail, source }
// Use read-only access only. Delete this file if the project has no audit trail; the report then skips trace mapping.
export default async ({ from, to, users, env, config }) => {
    throw new Error('audit adapter not implemented for this project yet')
}
