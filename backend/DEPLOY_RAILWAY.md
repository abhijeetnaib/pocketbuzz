# PocketBuzz Backend - Railway Deployment

## Quick Deploy to Railway

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/pocketbuzz)

---

## Manual Deployment Steps

### 1. Install Railway CLI
```bash
npm install -g @railway/cli
railway login
```

### 2. Initialize Railway Project
```bash
cd backend
railway init
```

### 3. Configure Environment Variables

In Railway Dashboard, set these environment variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `SUPABASE_URL` | Supabase project URL | `https://xxx.supabase.co` |
| `SUPABASE_ANON_KEY` | Supabase anonymous key | `sb_publishable_xxx` |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase service role key | `sb_secret_xxx` |
| `OPENAI_API_KEY` | OpenAI API key | `sk-proj-xxx` |
| `FAL_API_KEY` | Fal.ai API key | `xxx:xxx` |
| `WHATSAPP_PHONE_NUMBER_ID` | WhatsApp Business Phone ID | `1006215249236308` |
| `WHATSAPP_ACCESS_TOKEN` | **Permanent** WhatsApp token | See below |
| `APP_URL` | Frontend URL | `https://pocketbuzz.autoskout.com` |
| `API_URL` | Backend URL (auto-set by Railway) | `https://xxx.railway.app` |
| `SECRET_KEY` | Random secret for JWT | Generate with `openssl rand -hex 32` |

### 4. Deploy
```bash
railway up
```

### 5. Get Production URL
```bash
railway domain
```

---

## Permanent WhatsApp Access Token

**IMPORTANT:** The standard WhatsApp token expires in 24 hours. For production, you need a **System User Token** that never expires.

### How to Generate a Permanent Token:

1. **Go to Meta Business Settings**
   - Visit: https://business.facebook.com/settings
   - Select your Business Account

2. **Create a System User**
   - Navigate to: Users → System Users
   - Click "Add" → Create new System User
   - Name: `PocketBuzz API`
   - Role: **Admin**

3. **Assign WhatsApp App**
   - Select the System User
   - Click "Assign Assets"
   - Choose "Apps" → Select your WhatsApp App
   - Grant **Full Control**

4. **Generate Permanent Token**
   - Click "Generate New Token"
   - Select your WhatsApp App
   - **Token Expiration: Never** ← Critical!
   - Select permissions:
     - ✅ `whatsapp_business_management`
     - ✅ `whatsapp_business_messaging`
   - Click "Generate Token"

5. **Copy and Save**
   - Copy the token immediately (shown only once!)
   - Store securely in Railway environment variables

---

## Production Checklist

- [ ] Railway project created
- [ ] All environment variables configured
- [ ] Permanent WhatsApp token generated
- [ ] Custom domain configured (optional)
- [ ] WhatsApp webhook URL updated in Meta Dashboard
- [ ] Health check passing

---

## Webhook Configuration

After deployment, update your WhatsApp webhook in Meta Developer Portal:

1. Go to: https://developers.facebook.com/apps/YOUR_APP_ID/whatsapp-business/wa-dev-console
2. Update Callback URL: `https://YOUR_RAILWAY_URL/webhook/whatsapp`
3. Verify Token: `pocketbuzz_webhook_verify_token`
4. Subscribe to: `messages`

---

## Monitoring

Railway provides built-in:
- Logs: `railway logs`
- Metrics: Dashboard → Metrics tab
- Deployments: Dashboard → Deployments tab

---

## Troubleshooting

### Token Expired Error
```
Error: Session has expired
```
**Solution:** Generate a new permanent token using System User (see above)

### CORS Error
**Solution:** Update `APP_URL` environment variable to match your frontend domain

### Webhook Not Receiving Messages
**Solution:** Verify webhook URL in Meta Dashboard matches your Railway URL
