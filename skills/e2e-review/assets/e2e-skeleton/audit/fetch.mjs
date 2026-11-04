// Audit adapter: return audit rows written by the tested system within [from, to].
// Contract (references/project-profile.md): export default async ({ from, to, users, actions, includeSystem, env, config }) => rows
// users: user ids; actions: action codes to keep (optional); includeSystem: also rows the system wrote without a user (optional).
// Each row: { time: 'yyyy-MM-ddTHH:mm:ss[.fff]' (local), user, action, target, detail, source }
// Use read-only access only. Delete this file if the project has no audit trail; close then warns and renders the report without audit rows.
export default async ({ from, to, users, actions, includeSystem, env, config }) => {
    throw new Error('audit adapter not implemented for this project yet')
}
