# Railway Deployment Troubleshooting

## Status: 502 Bad Gateway

### Debugging Checklist

#### 1. Check Railway Logs
- Go to Railway Dashboard → gunicorn app
- Click **Logs** tab
- Look for errors in "Deploy Logs" and "Runtime Logs"

#### 2. Verify Environment Variables
- Settings → Variables
- Ensure ALL required vars are set:
  - ✅ CLICKUP_API_KEY
  - ✅ CLICKUP_TEAM_ID
  - ✅ INFOBIP_API_KEY

#### 3. Check Port Configuration
- Settings → Networking
- Port should be **5000** or match `PORT` env var

#### 4. Redeploy
If no logs show errors:
- Go to Deployments
- Click on latest deployment → "Redeploy"

#### 5. Local Test
Before Railway, test locally:
```bash
docker compose up
# Then test: curl http://localhost:5000/health
```

#### 6. Common Issues

**Missing env vars** → App crashes on startup
- Fix: Add all required variables in Railway Settings

**Database permission error** → SQLite can't write to /tmp
- Fix: Switch to in-memory DB or use environment-specific path

**Port already in use** → Conflict with existing process
- Fix: Change PORT env var in Railway

**Requirements missing** → Missing dependencies
- Fix: Ensure requirements.txt is complete

### Next Steps
1. Check **Deploy Logs** in Railway dashboard
2. Share error message
3. We'll fix and redeploy
