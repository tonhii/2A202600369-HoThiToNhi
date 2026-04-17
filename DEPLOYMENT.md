# Deployment Information

## Public URL
https://2a202600369-hothitonhi-production.up.railway.app

## Platform
Railway

## Test Commands

### Health Check
```bash
curl https://2a202600369-hothitonhi-production.up.railway.app/health
# Expected: {"status": "ok", "uptime_seconds": "..."}
```

### API Test (with authentication)
```powershell
$URL = "https://2a202600369-hothitonhi-production.up.railway.app"
$headers = @{ "X-API-Key" = "tonhi-agent-day12" }
Invoke-RestMethod -Uri "$URL/ask?question=Hello" -Method Post -Headers $headers
```

## Environment Variables Set
- PORT (Dynamic by Railway)
- REDIS_URL (${{Redis.REDIS_URL}})
- AGENT_API_KEY (tonhi-agent-day12)
- ENVIRONMENT (production)

## Screenshots
- [Railway Deployment](railway_deployment.png)
