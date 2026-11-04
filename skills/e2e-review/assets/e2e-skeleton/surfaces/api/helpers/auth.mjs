// Log in for the api surface. Called once per account key; the session stays in memory and never enters artifacts.
// `api` is an unauthenticated client (calls are logged and redacted); cookies from responses are kept automatically.
// Return { headers } to add to every later request, e.g. { headers: { authorization: `Bearer ${token}` } }.
export default async (api, account, ctx) => {
    const res = await api.post('/auth/login', { body: { userId: account.userId, password: account.password } })
    if (res.status >= 400) throw new Error(`login failed for ${ctx.accountKey}: ${res.status}`)
    return {}
}
