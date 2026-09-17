---
name: pushfcm
description: Send a push notification through the CloudPush worker's FCM endpoint (POST /push-fcm), and resolve which fcm-topic to use before sending. Use this whenever Yu wants to send an FCM/push notification, wire up "PushFCM", set up or configure CloudPush FCM, migrate an ntfy push to FCM, or asks to "notify me / push this / send an alert" via the CloudPush worker. Trigger even when Yu says "push this to my phone" or names an existing ntfy topic and wants it delivered over FCM instead. Always resolve the topic (ask or reuse) before the first send in a session.
---

# PushFCM

Send notifications via the CloudPush worker `POST /push-fcm`. Before the first send in a session, resolve the `fcm-topic` (below), then send. Reuse the resolved topic for every later send in the same session without asking again.

## Config (from environment — never hardcode)

- `$CLOUDPUSH_URL` — worker base URL, e.g. `https://<worker>.workers.dev`
- `$CLOUDPUSH_KEY` — API key, sent in the `key` header

Guard before the first send; abort loudly if unset:

```
: "${CLOUDPUSH_URL:?CLOUDPUSH_URL not set}"
: "${CLOUDPUSH_KEY:?CLOUDPUSH_KEY not set}"
```

If the routine wraps everything in one shell without `set -e`, add `set -e` too, or the guard sets a non-zero exit but execution continues.

## Resolve the fcm-topic (do this once, before the first send)

Anchor the question in a proposed default — never a blank prompt.

1. **Look for an existing topic** in the current task context, the conversation, or a referenced file — most often an ntfy topic name (e.g. `rei-tech-news`, `rei-tech-subscribe`, `rei-briefing`).
2. **If a topic is found**, ask which to use, defaulting to reuse:
   > "I'll send to `<found-topic>` unless you say otherwise — keep it, use a different topic, or fall back to the worker's `FCM_TOPIC` default?"
3. **If nothing is found**, ask directly, offering the server default:
   > "What `fcm-topic` should I send to? Or leave it blank to use the worker's `FCM_TOPIC` default."
4. **"Use the default"** means omit the `-F "fcm-topic=..."` line entirely so the worker applies its `FCM_TOPIC`.

Note: an ntfy topic name and the FCM topic are independent — reusing the same string only matters if Yu's app actually subscribes to that FCM topic. If unsure, say so.

## Send — one notification per call

Write the body to a file first (backticks / `$()` in snippets get mangled or executed if inlined):

```
curl -s -X POST \
  -H "key: $CLOUDPUSH_KEY" \
  -F "title=<short headline, ASCII, no emoji, use '-' not em dashes>" \
  -F "body=<body.txt" \
  -F "action=<label>|<https URL>" \
  -F "fcm-topic=<resolved topic>" \
  "$CLOUDPUSH_URL/push-fcm"
```

Field rules:
- `title` — required, 1..256 chars. Keep it short for the notification shade.
- `body` — `-F "body=<body.txt"` reads the field VALUE from the file (the `<` is not a redirect and not an `@` upload). Plain text or HTML; the app flattens it to text, so markdown / fenced code blocks do NOT render — write snippets as plain indented lines. Max 4096 chars.
- `action` — optional, `label|url`, http(s) only (non-http → 422), label max 40 chars. Up to 3, comma-separated. Omit the line if there's no link.
- `fcm-topic` — omit to use the worker default (see resolution step).

## Verify each send

Expect HTTP 200 with JSON where `data.results[0].ok` is `true`. On failure, read the envelope:
- **401** — wrong/missing key.
- **422** — a field is invalid; the offending field is named under `errors`. Fix and retry once.
- **429 / 503** (`retryable: true`) — wait a few seconds, retry once.

## Quick connectivity probe (optional)

The GET endpoint confirms auth + topic wiring without composing a full message:

```
curl -s "$CLOUDPUSH_URL/push-simple-fcm?key=$CLOUDPUSH_KEY&fcm-topic=<topic>&fcm-title=Probe&fcm-message=hello"
```

Expect `200` and `"ok":true` in `data.results[0]`.
