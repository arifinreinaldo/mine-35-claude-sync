# API Standard — canonical directive (backend projects)

Single source of truth for how every backend that exposes **JSON endpoints** shapes
responses and errors, so a caller can always tell success from failure and, on
failure, **whether a retry is safe**.

---

## Instantiation — what `/init` and scaffolding MUST do

When initializing (`/init`) or scaffolding a backend project that exposes JSON API endpoints:

1. Create **`docs/api-standard.md`** in the project = the **Contract** below, plus a
   stack-specific **Implementation** section (see the per-stack cheatsheet).
2. Add a trigger line to the project's **`CLAUDE.md`**:
   > **When creating or generating any JSON API endpoint, follow `docs/api-standard.md`.**
3. Tailor, don't fight: if the project already has a response convention (macros,
   helpers, an envelope), **extend** it to satisfy the Contract rather than replacing it.

**Skip** for projects with no machine-facing JSON API — pure static sites, or HTML-only
apps that only redirect/render templates. Server-rendered routes are always exempt even
in a project that also has a JSON API.

---

## The Contract (stack-agnostic)

### Success — 2xx
```json
{ "message": "", "data": { } }
```
`data` is the payload; omit it for pure acknowledgements (`{ "message": "deleted" }`).

### Error — 4xx / 5xx
```json
{ "message": "human-readable reason", "errors": { }, "retryable": false, "request_id": "…" }
```
- `errors` — optional detail (per-field validation). Omit/`null` when empty.
- `retryable` — **required**; derived from the status code (table below).
- `request_id` — mirrors the `X-Request-Id` response header.

> **#1 rule: an error is NEVER sent with HTTP 200.** The status code is the primary
> retry signal; the body mirrors it.

### Status code → retryability

| Situation | Status | `retryable` | `Retry-After` |
|---|---|---|---|
| OK | 200 / 201 / 204 | — | — |
| Bad input / malformed | 400 | false | — |
| Validation failed | 422 | false | — |
| Not authenticated | 401 | false | — |
| Forbidden | 403 | false | — |
| Not found | 404 | false | — |
| Conflict | 409 | false | — |
| Rate limited | 429 | **true** | ✅ seconds |
| Unhandled bug | 500 | false | — |
| Dependency down (DB, upstream timeout) | 503 | **true** | ✅ seconds |

`retryable: true` is exactly `{429, 503}` (add 502/504 if you proxy). **500 is `false`** —
a bug won't fix itself on retry; reserve 503 for genuinely transient conditions.

### Headers
- `X-Request-Id` on **every** response — echo inbound, else generate.
- `Retry-After` (integer seconds) on **429 and 503**.

### Idempotency (where it matters)
State-changing endpoints (`POST`/`PUT`/`PATCH`/`DELETE`) where a duplicate causes harm
SHOULD honor an `Idempotency-Key` header: store the result keyed by it, replay on repeat.
Skip for `GET`. Add only where a double-execute is genuinely harmful — not blanket.

---

## Per-stack implementation cheatsheet

**Go (`net/http`, stdlib only):** add `writeData(w, status, msg, data)` and
`writeError(w, r, status, msg, details)` helpers (derive `retryable` from status; set
`Retry-After` on 429/503); a `requestID` middleware wrapping the mux that echoes/sets
`X-Request-Id`. Never `writeJSON(..., {"error": …})` with an implicit 200. Reference
implementation: `simplr-23-mssql-logger/docs/api-standard.md`.

**Laravel (12+, slim skeleton):** extend the `success`/`data`/`fail` response macros in
`AppServiceProvider` — `fail` gains `retryable` + `request_id` and sets `Retry-After` on
429/503; normalize 404/403/500/429 in `bootstrap/app.php` → `withExceptions` so they stay
in the envelope; a `RequestId` middleware on the API group; route validation through the
`fail` envelope. Reference implementation: `laravel-8-template/docs/api-standard.md`.

**Node/Express (or similar):** one central error middleware that emits the envelope with
`res.status(code)`; a request-id middleware; `Retry-After` on 429/503. Same Contract.

---

## New-endpoint checklist (any stack)

- [ ] Success is `{message, data}` with a 2xx code
- [ ] Every error goes through the one central error path — **never** HTTP 200 on failure
- [ ] Status code matches the table; `retryable` follows from it
- [ ] `Retry-After` on 429/503; `X-Request-Id` on every response
- [ ] Harmful mutations honor `Idempotency-Key` (skip for GETs)
- [ ] A test asserts status + envelope for one success and one error path
