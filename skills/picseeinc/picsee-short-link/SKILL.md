---
name: picsee-short-link
description: Shorten URLs using PicSee (pse.is). Use when the user asks to shorten a URL, create a short link, or mentions PicSee. Supports both unauthenticated mode (basic shortening) and authenticated mode (analytics, editing, search, custom thumbnails for Advanced plan users).
---

# PicSee Short Link

Quick URL shortener with optional analytics. 

## Fast Track: Shorten a URL

**For 99% of requests, use this workflow:**

1. **Check config**: Read `skills/picsee-short-link/config.json`
   - If **NOT exist** → Go to **First-Time Setup** (see below)
   - If **exists** → Check `status` field and proceed

2. **Call API**:
   - **Unauthenticated** (no token):
     ```bash
     curl -X POST https://chrome-ext.picsee.tw/v1/links \
       -H "Content-Type: application/json" \
       -d '{"url":"<LONG_URL>","domain":"pse.is","externalId":"openclaw"}'
     ```
   
   - **Authenticated** (has token):
     ```bash
     curl -X POST https://api.pics.ee/v1/links \
       -H "Authorization: Bearer $PICSEE_API_TOKEN" \
       -H "Content-Type: application/json" \
       -d '{"url":"<LONG_URL>","domain":"pse.is","externalId":"openclaw"}'
     ```
     (Token stored in `~/.openclaw/.env` as `PICSEE_API_TOKEN`)

3. **Display result** (code block for easy copying):
   ```text
   https://pse.is/abc123
   ```
   Ａsk user if they want a QR code?

4. **QR code** (ONLY if user explicitly asks):
   ```bash
   curl -o /tmp/qrcode.png "https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=<SHORT_URL>"
   ```
   Then send via `message` tool with `filePath:"/tmp/qrcode.png"`

**Done.** No need to ask about QR codes or analytics unless user requests them.

---

## First-Time Setup (if no config exists)

**Detection**: Check if `skills/picsee-short-link/config.json` exists. If NOT exist → first-time user.

**Ask user** (explain features):

> "Would you like to provide a PicSee API token to unlock advanced features? (y/n)
> 
> **With token (authenticated mode), you can:**
> - View link analytics and daily click stats
> - List your short links (filter by date range)
> - Search short links
> - Edit links (change destination URL) — **Advanced plan only**
> - Customize thumbnails/titles — **Advanced plan only**
> 
> **Without token (unauthenticated mode), you can:**
> - Create basic short links (no analytics)
> 
> **To get your API token:**
> Go to https://picsee.io/ → Click avatar (top-right) → Settings → API → Copy token"

**If user says YES**:

1. Wait for token (alphanumeric string, e.g., `abc123def456...`)

2. Save to `~/.openclaw/.env`:
   ```
   PICSEE_API_TOKEN=<user_token>
   ```

3. Create `skills/picsee-short-link/config.json`:
   ```json
   {
     "status": "authenticated",
     "setupDate": "YYYY-MM-DD"
   }
   ```

4. Verify token by calling API status:
   ```bash
   curl -X GET https://api.pics.ee/v2/my/api/status \
     -H "Authorization: Bearer $PICSEE_API_TOKEN"
   ```

5. Show user their plan tier (free/basic/advanced) and quota info.

**If user says NO**:

1. Create `skills/picsee-short-link/config.json`:
   ```json
   {
     "status": "unauthenticated",
     "setupDate": "YYYY-MM-DD"
   }
   ```

2. Explain: "You can create short links in unauthenticated mode. To unlock analytics/editing later, just ask me to add your API token."

---

## Advanced Features (Authenticated Mode Only)

### View Link Analytics

Extract `encodeId` from short URL (e.g., `pse.is/abc123` → `abc123`), then:

```bash
curl -X GET "https://api.pics.ee/v1/links/<ENCODE_ID>/overview?dailyClicks=true" \
  -H "Authorization: Bearer $PICSEE_API_TOKEN"
```

**Response includes:**
- `totalClicks`, `uniqueClicks`
- `dailyClicks` array (date + click counts)

**Generate chart** (if user asks for visualization):
- Use matplotlib
- All text in ENGLISH
- Line chart with total/unique clicks over time
- Save to `/tmp/<encodeId>_analytics.png` and send via `message` tool

---

### List Recent Links

```bash
curl -X POST "https://api.pics.ee/v2/links/overview?isAPI=false&limit=50&startTime=<ISO8601_DATE>" \
  -H "Authorization: Bearer $PICSEE_API_TOKEN" \
  -H "Content-Type: application/json"
```

**Date format**: `YYYY-MM-DDTHH:MM:SS` (no timezone suffix)

**⚠️ IMPORTANT: startTime Parameter Behavior**

The `startTime` parameter **FILTERS results backwards from that timestamp**. It returns links created **on or before** the specified date, in reverse chronological order (newest first).

**Examples:**

- **To query December 2025**:
  - Use: `startTime=2025-12-31T00:00:00` (last day of month, not first!)
  - This returns all links up to Dec 31, including Dec 1–31
  
- **To query a specific month**:
  - Use the **LAST DAY** of that month at `00:00:00`
  - December → `2025-12-31T00:00:00`
  - January → `2026-01-31T00:00:00`

- **To query a specific date range**:
  - Use `startTime` = **end date of range**
  - Combine with `limit` to control how many results returned
  - Adjust limit if you need older entries

**Common mistake**: Using the **first day** of a month will miss data from that month.

---

### Check Plan Tier

```bash
curl -X GET https://api.pics.ee/v2/my/api/status \
  -H "Authorization: Bearer $PICSEE_API_TOKEN"
```

**Plan values**: `"free"`, `"basic"`, `"advanced"`

**Feature restrictions**:
- **Free/Basic**: Create links, view analytics, list links
- **Advanced only**: Edit links, custom thumbnails/titles, UTM params, tracking pixels

---

### Edit Short Link (Advanced plan only)

```bash
curl -X PUT https://api.pics.ee/v2/links/<ENCODE_ID> \
  -H "Authorization: Bearer $PICSEE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"url":"<NEW_DESTINATION_URL>"}'
```

**If user is NOT on Advanced plan**: Block and suggest creating a new link instead.

---

### Delete Short Link

```bash
curl -X POST https://api.pics.ee/v2/links/<ENCODE_ID>/delete \
  -H "Authorization: Bearer $PICSEE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"value":"delete"}'
```

(Use `"recover"` to restore)

---

## Mode Summary

| Mode | Base URL | Auth Required | Features |
|------|----------|---------------|----------|
| **Unauthenticated** | `chrome-ext.picsee.tw` | No | Create links only |
| **Authenticated** | `api.pics.ee` | Yes | Create + analytics + list + edit (plan-dependent) |

**Default**: Unauthenticated (fastest, no setup).

---

## Output Guidelines

- **Short URLs**: Always in code blocks for easy copying
- **Language**: All responses in user's language
- **No jargon**: Avoid "API call", "endpoint", "JSON" in user-facing messages
- **Charts**: English labels, professional styling, save to `/tmp/` and send via `message` tool

---

## Quick Reference

**Token location**: `~/.openclaw/.env` → `PICSEE_API_TOKEN=...`  
**Config location**: `skills/picsee-short-link/config.json`  
**Default domain**: `pse.is`  
**externalId**: Always `openclaw`

---

## Error Handling

- **Unauthenticated mode + user requests analytics**: Reply: "This feature requires login. Provide your PicSee API token to unlock it."
- **Non-Advanced plan + user requests edit**: Reply: "Editing links requires the Advanced plan. You can create a new link instead."
- **Invalid token**: Reply: "Invalid API token. Get a new one from https://picsee.io/ → Settings → API"
