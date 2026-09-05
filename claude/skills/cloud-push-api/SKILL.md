---
name: cloud-push-api
description: Write a ready-to-integrate CloudPush push-notification manual into a project - endpoint contract, payload shapes, error handling, .env entries, receiver contract. Use when integrating push notifications through CloudPush (the cloudflare-notifier worker) into any project in any language, or when the user says "integrate cloudpush", "add cloud push", "call the push API".
---

# cloud-push-api

Produces a **manual**, not code. The manual stays in the target project, so whoever writes
the call later - you, another agent, or the user - has the full contract without this skill.

The contract lives in `reference.md` next to this file. Read it before you write anything.

FCM endpoints only. `/push` and `/push-simple` (ntfy) are deferred: they return 503 in
production. Never offer them.

## Steps

### 1. Interview

Ask all four questions in one `AskUserQuestion` call. Bold is the default - a user who says
"just do it" gets the defaults. Skip a question the repo already answers, and say which
default you took.

| Question | Options |
|---|---|
| Which push shapes does this project send? (multi-select) | **Simple message (GET, one line)**, Rich message (title + body, POST), With action buttons, With a reply box |
| FCM topic for this project | Free text. Suggest a kebab-case name from the repo name |
| Env var names | **`CLOUDPUSH_URL` / `CLOUDPUSH_KEY`**, or match the project's existing convention |
| Fire one live test push now? | **Yes** (needs the real key, pasted in chat, never written to a file), No |

### 2. Write the manual

Write `docs/cloudpush-integration.md`, or the folder this project already uses for docs.

Include **only** the sections for the shapes picked. Copy the field tables from
`reference.md` verbatim. Do not paraphrase a limit.

Sections, in order:

1. **What CloudPush is** - one paragraph. State that the phone app must subscribe to the
   topic, or the push goes nowhere and the API still answers 200.
2. **Endpoint and auth** - base URL, the `key` header.
3. **Environment variables** - the names chosen in the interview.
4. **Request shapes** - one subsection per picked shape, each with a worked `curl` that
   uses this project's real topic.
5. **Response contract** - success envelope, error envelope, status table, the retry rule.
6. **Limits** - the numbers table.
7. **Receiver contract** - only when the project picked action buttons with a token, or a
   reply box. This project must build that endpoint; the manual states its rules.
8. **Gotchas**.

Rules for the manual:

- Language-independent. `curl` is the reference shape, plus one line that says any HTTP
  client sends the same request.
- Never invent a field. A field absent from `reference.md` does not exist.
- Use the real topic and the real URL, not placeholders, wherever the interview gave one.
- ASD-STE100 prose: short sentences, active voice, one term per concept.

### 3. Environment entries

Append to the project's `.env.example`. Create the file if it is absent. **Never** write to
`.env` itself.

```
CLOUDPUSH_URL=https://cloudflare-notifier.arifin-reinaldo.workers.dev
CLOUDPUSH_KEY=
```

The key stays empty because `.env.example` gets committed. Tell the user to put the real
key in their own `.env`. Use the chosen variable names if they differ.

### 4. Verify

Only when the user said yes. Ask for the key, then send one real push:

```bash
curl -sS -i -H "key: <API_KEY>" \
  "https://cloudflare-notifier.arifin-reinaldo.workers.dev/push-simple-fcm?fcm-topic=<topic>&fcm-title=CloudPush&fcm-message=integration%20verified"
```

Show the raw response. `200` with `{"message":"sent"}` is the proof. On any other status,
read the `errors` object and say which field is wrong. Never write the key to a file, and
never echo it back in the manual.

## Do not

- Generate client code. The manual is the deliverable. Write code only if the user asks
  for it in a separate request.
- Offer `/push` or `/push-simple`.
- Put the API key in a query string in the manual. The `key` header is the documented way;
  the query form exists for devices that cannot set a header, and it leaks into server logs.
