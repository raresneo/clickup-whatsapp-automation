# Infobip WhatsApp Webhook Configuration

## Webhook URL
```
https://gunicorn-app-production-1deb.up.railway.app/webhook/whatsapp
```

## Setup Steps

### 1. Login to Infobip Dashboard
- Go to https://portal.infobip.com/
- Login with your credentials

### 2. Navigate to Webhooks
- Left menu → **Integrations** → **Webhooks**
- Or: **WhatsApp** → **Settings** → **Webhooks**

### 3. Add New Webhook
Click **Add Webhook** or **New Integration**

### 4. Configure Webhook
Fill in these fields:

| Field | Value |
|-------|-------|
| **Name** | ClickUp WhatsApp Responses |
| **Webhook URL** | `https://gunicorn-app-production-1deb.up.railway.app/webhook/whatsapp` |
| **HTTP Method** | POST |
| **Content-Type** | application/json |
| **Event Types** | Message Received, Message Status |

### 5. Authentication (Optional but Recommended)
If Infobip requires authentication headers:
- Add header: `Authorization: App {INFOBIP_API_KEY}`
- Or use API Key from Railway environment variables

### 6. Enable Webhook
- Ensure webhook is **ENABLED**
- Test button should appear → Click to test

### 7. Test Webhook
```bash
curl -X POST https://gunicorn-app-production-1deb.up.railway.app/webhook/whatsapp \
  -H "Content-Type: application/json" \
  -d '{
    "results": [
      {
        "from": "+44123456789",
        "text": {"body": "Test message"}
      }
    ]
  }'
```

Expected response:
```json
{"status": "ok"}
```

## Expected Webhook Payload from Infobip

```json
{
  "results": [
    {
      "from": "+44XXXXXXXXX",
      "to": "+44 7860 088970",
      "messageId": "string",
      "text": {
        "body": "Customer message text"
      },
      "timestamp": 1234567890,
      "receivedAt": "2024-01-01T00:00:00Z",
      "chatId": "string"
    }
  ]
}
```

## Troubleshooting

### Webhook not receiving messages
1. **Check URL accessibility**: 
   ```bash
   curl https://gunicorn-app-production-1deb.up.railway.app/health
   ```
   Should return: `{"status": "ok"}`

2. **Check Infobip logs**: In Infobip dashboard → Webhooks → View delivery logs

3. **Check Railway logs**:
   ```bash
   docker logs <container_id>
   # or check Railway dashboard → Logs
   ```

4. **Verify WhatsApp connection**: Ensure your Infobip WhatsApp business number is active

### Messages not saving to database
- Check that `/tmp/whatsapp_messages.db` exists on Railway
- View stored messages at: `https://gunicorn-app-production-1deb.up.railway.app/dashboard`

### Manual Test
Send a test message to your WhatsApp business number and check if it appears in the dashboard.

## Webhook Payload Parser
The app extracts:
- `from`: Sender's phone number
- `text.body`: Message content
- Stores in SQLite at `/tmp/whatsapp_messages.db`

Messages visible at: `https://gunicorn-app-production-1deb.up.railway.app/dashboard`
