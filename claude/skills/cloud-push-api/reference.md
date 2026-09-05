# CloudPush FCM contract

Source of truth: the `cloudflare_notifier` repo (`src/index.js`, `src/fcm.js`, `README.md`,
`docs/cloudpush-action-spec.md`, `docs/cloudpush-reply-spec.md`). Verified 2026-09-05.
If that repo is on disk, re-read it before you trust a number here.

Base URL: `https://cloudflare-notifier.arifin-reinaldo.workers.dev`

## Authentication

Send the key in the `key` header. `x-api-key` and an `apiKey` body field also work. The GET
endpoint also accepts `?key=`, for devices that cannot set a header. A key in a URL lands in
server logs and browser history.

A wrong or missing key returns `401`.

## Endpoints

| Method | Path | Use |
|---|---|---|
| `POST` | `/push-fcm` | Title, body, action buttons, reply target |
| `GET` | `/push-simple-fcm` | One-line message from a bare URL |

`/push` and `/push-simple` are the ntfy endpoints. They are deferred and return `503` in
production. Do not use them.

## POST /push-fcm

The body is `multipart/form-data`, `application/x-www-form-urlencoded`, or
`application/json`. All three flatten to the same field set.

| Field | Required | Rule |
|---|---|---|
| `title` | yes | 1..256 chars, not blank |
| `body` | yes | 1..4096 chars, not blank. Plain text or HTML |
| `fcm-topic` | see note | `^[A-Za-z0-9._~%-]{1,900}$`. Falls back to the worker `FCM_TOPIC` var. Required when neither is set |
| `action` | no | Up to 3 buttons. See **Actions** |
| `reply-url` | no | `https://` only (scheme case-insensitive), printable ASCII, max 2048 chars |
| `reply-token` | with `reply-url` | `^[\x21-\x7E]{1,512}$` - printable ASCII, no spaces. It rides an `Authorization` header verbatim. Sent alone it is a `422` |
| `reply-label` | no | 1..40 chars after trim. The phone shows "Reply" when absent |

Unknown fields are ignored, not forwarded.

The worker flattens `body` to plain text before it goes out, because the app renders no
markup. It then truncates the text to 3500 bytes, minus the bytes that actions and the
reply target already use.

```bash
curl -X POST https://cloudflare-notifier.arifin-reinaldo.workers.dev/push-fcm \
  -H "key: YOUR_KEY" \
  -F "title=Deploy 42" \
  -F "body=<p>Build <b>42</b> is live</p>" \
  -F "fcm-topic=my-topic"
```

## Actions

An action is a button. There are two forms:

- **String form** - `https://example.com/open`, or `Open|https://example.com/open`. Put
  several in one field, comma separated. The label is optional and caps at 40 chars; the
  URL hostname is the fallback. This form carries a URL only.
- **Object form** - `{ "url", "label", "method", "token", "body" }`. This is the only form
  that carries `method`, `token` or `body`. It is also the only way to send a URL that
  contains a comma or a pipe.

**The object form needs a JSON request body.** In form-data every value is a string, and
the parser splits a string on commas. Send `Content-Type: application/json` with `action`
as an array of objects.

| Key | Required | Rule |
|---|---|---|
| `url` | yes | `http(s)`. Must be `https://`, printable ASCII, max 2048 chars when `token` is present |
| `label` | no | Max 40 chars. The hostname is the fallback |
| `method` | no | Absent or `GET` is a link button. `POST`, `PUT`, `PATCH`, `DELETE` is a background action. Case-insensitive input, normalised before it goes out |
| `token` | no | `^[\x21-\x7E]{1,512}$`. Needs a background `method` and an `https://` url |
| `body` | no | A JSON object or array. Serialised to at most 1024 bytes. Needs a background `method` |

Budget: all actions plus the reply target together must serialise to at most 3000 bytes.
This leaves at least 500 bytes for the message body. Over budget is a `422` on
`errors.action`.

The notification tap target is the URL of the first link action. A token-protected
background URL is never a tap target.

The background actions of one push are alternatives ("I am here" / "I am not here"). The
phone lets the user complete at most one, then locks the rest on that push. Link buttons
stay usable. Put independent operations in separate pushes.

```bash
curl -X POST https://cloudflare-notifier.arifin-reinaldo.workers.dev/push-fcm \
  -H "key: YOUR_KEY" -H "content-type: application/json" \
  -d '{
    "title": "Trip 42",
    "body": "Driver is at the door",
    "fcm-topic": "my-topic",
    "action": [
      { "url": "https://app.example.com/trips/42", "label": "Open" },
      { "url": "https://api.example.com/trips/42", "label": "I have arrived",
        "method": "PATCH", "token": "opaque-token", "body": { "status": "arrived" } }
    ]
  }'
```

## Reply target

`reply-url` plus `reply-token`, and optionally `reply-label`, adds a reply box to the
notification. The phone posts the typed text back:

```
POST <reply-url>
Authorization: Bearer <reply-token>
Content-Type: application/json; charset=utf-8
Accept: application/json

{"text":"<reply text>"}
```

The worker rejects `http://`. A bearer token over cleartext is a leaked credential.

```bash
curl -X POST https://cloudflare-notifier.arifin-reinaldo.workers.dev/push-fcm \
  -H "key: YOUR_KEY" \
  -F "title=Question" -F "body=Are you on site?" -F "fcm-topic=my-topic" \
  -F "reply-url=https://api.example.com/replies/42" \
  -F "reply-token=opaque-token" \
  -F "reply-label=Answer"
```

## GET /push-simple-fcm

| Query param | Required | Rule |
|---|---|---|
| `fcm-message` | yes | 1..4096 chars |
| `fcm-topic` | see note | Same charset as `fcm-topic` above. Overrides the worker `FCM_TOPIC` var, and is required when neither is set. It doubles as the title when `fcm-title` is absent |
| `fcm-title` | no | 1..256 chars |
| `key` | no | The key in the query string, when a header is impossible |

```bash
curl -H "key: YOUR_KEY" \
  "https://cloudflare-notifier.arifin-reinaldo.workers.dev/push-simple-fcm?fcm-topic=my-topic&fcm-title=Disk&fcm-message=disk%2091%25"
```

## Response contract

Success:

```json
{ "message": "sent", "data": { "results": [ { "channel": "fcm", "ok": true } ] } }
```

Failure:

```json
{ "message": "Validation failed",
  "errors": { "title": "required, 1..256 chars" },
  "retryable": false,
  "request_id": "0f1c..." }
```

Every response carries an `X-Request-Id` header. Log it. It is the only handle on a failed
push in the worker logs.

| Status | Meaning | Retry |
|---|---|---|
| `200` | FCM accepted the message | - |
| `401` | Wrong or missing API key | No |
| `404` | Wrong path | No |
| `405` | Wrong method for that path | No |
| `422` | A field failed validation. Read `errors` | No. Fix the field |
| `500` | The worker is misconfigured (no API key, no service account) | No |
| `502` | FCM rejected the message | No. A retry cannot fix it |
| `503` | FCM is down or throttling | Yes, after `Retry-After` seconds |

Retry only when `retryable` is `true`. The worker sets that flag for `429` and `503` only.
Honour the `Retry-After` header. The worker sends 30 seconds.

`200` means FCM accepted the message. It does not mean a phone showed it. A topic that
nobody subscribes to still answers `200`.

## Limits

| Thing | Limit |
|---|---|
| `title` | 256 chars |
| `body` | 4096 chars in, 3500 bytes out, minus action and reply bytes |
| Actions per push | 3 |
| Action label | 40 chars |
| Action `body` | 1024 bytes serialised |
| Actions plus reply target, together | 3000 bytes serialised |
| `reply-token`, action `token` | 512 printable ASCII chars, no spaces |
| `reply-url`, action `url` with a token | 2048 chars, https, printable ASCII |
| FCM topic | 900 chars, `A-Za-z0-9._~%-` |

## Receiver contract

This applies only when the project sends a reply target, or a background action with a
token. The project must expose that endpoint. CloudPush never calls it. The phone does.

- **Authentication**: the token arrives as `Authorization: Bearer <token>`. The sender
  mints it and the sender verifies it. CloudPush treats it as opaque and never logs it.
- **Reply body**: `{"text": "..."}` with `Content-Type: application/json; charset=utf-8`.
- **Background action body**: the `body` object from the action, verbatim. A `POST`, `PUT`
  or `PATCH` always carries a `Content-Type` header, with or without a body. Do not
  dispatch on `Content-Type` for a request that has no body.
- **Answer 2xx** to record success. `204` is fine. The phone ignores the response body.
- **Stay idempotent per token**: a second request with a consumed token must return the
  same 2xx and record nothing new. Never answer `409` or `410`. The phone shows those as a
  failure. The token is the idempotency key. It closes the one race the phone cannot: a
  request that succeeded, but whose response was lost.
- **4xx** is terminal for that attempt. The phone shows the status and leaves the button
  usable.
- **5xx, 3xx, a timeout, or no network** queues a retry. The phone tries 5 times with 30 s
  exponential backoff, which spans about one hour.
- **Never redirect.** The phone does not follow a 3xx, and a followed redirect would
  forward the bearer token to another host.
- **Token TTL** is the sender choice. A reply can wait in the phone offline queue, so a TTL
  under 24 hours makes a queued reply land as a failure.
- **No CORS needed.** The caller is an app, not a browser.

## Gotchas

- The app must subscribe to the topic. Nothing in the API tells you whether it did.
- Object-form actions need a JSON body. Form-data cannot carry them.
- `token` and `body` on an action are `/push-fcm` only. On `/push` they are a `422`.
- The worker flattens HTML in `body`. Use it for readability at the source, not for
  formatting on the phone.
- A key in a query string reaches server logs and browser history. Use the header.
