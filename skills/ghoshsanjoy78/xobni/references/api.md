# Xobni.ai REST API Reference

Base URL: `https://api.xobni.ai/api/v1`

All requests require `Authorization: Bearer xobni_<key>` header.

**Important:** All endpoints are scoped to the agent associated with your API key. Parameters like `account_id` and `agent_id` are auto-resolved — you don't need to pass them.

## Emails

### List Emails
```
GET /emails
```
Query params: `status` (received|read|sent|draft|archived), `limit` (1-100, default 20), `offset`

### Get Email
```
GET /emails/{email_id}
```
Returns full email with headers, body (text + HTML), attachments list.

### Send Email
```
POST /emails/send
Content-Type: application/json

{
  "to": ["recipient@example.com"],
  "subject": "Subject line",
  "body_text": "Plain text content",
  "body_html": "<p>Optional HTML</p>",
  "cc": ["cc@example.com"],
  "bcc": ["bcc@example.com"],
  "in_reply_to_email_id": "uuid-for-threading",
  "attachments": [
    {
      "filename": "report.pdf",
      "data": "<base64-encoded-content>",
      "content_type": "application/pdf"
    }
  ]
}
```

**Attachments:** Max 10 files, 10MB total. `content_type` is optional (auto-detected from filename).

### Update Email
```
PATCH /emails/{email_id}
Content-Type: application/json

{"status": "read"}  // or "archived", "is_starred": true/false
```

### Get Attachment URL
```
GET /emails/attachments/{attachment_id}/url
```
Returns pre-signed download URL valid for 15 minutes.

### Get Storage Usage
```
GET /emails/storage-usage
```
Returns mailbox storage usage stats.

## Threads

### List Threads
```
GET /emails/threads
```

### Get Thread
```
GET /emails/threads/{thread_id}
```
Returns all emails in conversation, sorted chronologically.

## Search

### Semantic Search
```
POST /search
Content-Type: application/json

{
  "query": "natural language search query",
  "limit": 10
}
```
Searches email bodies AND document attachments (PDF, DOCX, XLSX, PPTX, CSV, TXT).
Results include `source_type` (email_body|attachment) and `attachment_id` when matching attachments.

## Agents

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /agents | Get your agent's info |
| GET | /agents/{id} | Get agent details |
| PATCH | /agents/{id} | Update agent |

Response includes agent name, email address, slug, description, and status.

## Event Hooks (Webhooks)

### List Webhooks
```
GET /event-hooks
```
Lists webhooks for your agent.

### Create Webhook
```
POST /event-hooks
Content-Type: application/json

{
  "url": "https://your-endpoint.com/webhook",
  "events": ["email.received", "email.sent"],
  "description": "Optional label"
}
```
Returns webhook with `secret` (shown only once) for HMAC verification.

### Get Webhook
```
GET /event-hooks/{id}
```

### Update Webhook
```
PATCH /event-hooks/{id}
Content-Type: application/json

{"url": "https://new-url.com", "is_active": false}
```

### Delete Webhook
```
DELETE /event-hooks/{id}
```

### List Deliveries
```
GET /event-hooks/{id}/deliveries
```

### Test Webhook
```
POST /event-hooks/{id}/test
```

## Webhook Payload Format

When Xobni calls your webhook, it sends:

### email.received
```json
{
  "event": "email.received",
  "timestamp": "2026-02-12T01:00:00Z",
  "email_id": "uuid",
  "thread_id": "uuid",
  "from_address": "sender@example.com",
  "to_addresses": ["agent@xobni.ai"],
  "cc_addresses": [],
  "subject": "Subject line",
  "body_text": "Plain text content",
  "body_html": "<p>HTML content</p>",
  "has_attachments": false,
  "received_at": "2026-02-12T01:00:00Z"
}
```

### email.sent
```json
{
  "event": "email.sent",
  "timestamp": "2026-02-12T01:00:00Z",
  "email_id": "uuid",
  "thread_id": "uuid",
  "from_address": "agent@xobni.ai",
  "to_addresses": ["recipient@example.com"],
  "subject": "Subject line",
  "body_text": "Plain text content",
  "sent_at": "2026-02-12T01:00:00Z"
}
```

### Webhook Signature
Xobni includes a signature header for verification:
```
X-Xobni-Signature: sha256=<hmac-signature>
```
Compute HMAC-SHA256 of the raw request body using your webhook `secret` to verify authenticity.

## Response Format

All responses are JSON. Errors return:
```json
{
  "detail": "Error message"
}
```

Or for validation errors:
```json
{
  "detail": [
    {"type": "missing", "loc": ["body", "field"], "msg": "Field required"}
  ]
}
```

### Access Denied
Attempting to access another agent's resources returns:
```json
{
  "detail": "Forbidden"
}
```
(HTTP 403)
