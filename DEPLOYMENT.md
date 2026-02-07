# PocketBuzz Production Deployment Guide

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    User's WhatsApp                               │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                Meta WhatsApp Cloud API                           │
│                (graph.facebook.com)                              │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│              Railway (Backend API)                               │
│           api.pocketbuzz.autoskout.com                           │
│                                                                  │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────────┐   │
│  │   FastAPI      │  │   AI Engine    │  │  WhatsApp Service│   │
│  │   Endpoints    │  │   (GPT + Fal)  │  │  (Messaging)     │   │
│  └────────────────┘  └────────────────┘  └──────────────────┘   │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Supabase                                     │
│                   (PostgreSQL)                                   │
└─────────────────────────────────────────────────────────────────┘
                           
                           ▲
                           │
┌──────────────────────────┴──────────────────────────────────────┐
│              Vercel (Frontend)                                   │
│           pocketbuzz.autoskout.com                               │
│                                                                  │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────────┐   │
│  │   Dashboard    │  │   Campaign     │  │   Login/Auth     │   │
│  │     Page       │  │   Studio       │  │                  │   │
│  └────────────────┘  └────────────────┘  └──────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Step 1: Generate Permanent WhatsApp Token

**This is CRITICAL - tokens expire in 24 hours otherwise!**

### Create System User for Permanent Token

1. **Go to Meta Business Manager**
   ```
   https://business.facebook.com/settings/system-users
   ```

2. **Create System User**
   - Click "Add" → "Create new system user"
   - Name: `PocketBuzz Production`
   - Role: **Admin** (required for full access)

3. **Assign WhatsApp App**
   - Select the System User
   - Click "Assign Assets" → "Apps"
   - Select your WhatsApp Business App
   - Permission: **Full Control**

4. **Generate Token with NEVER Expiration**
   - Click "Generate New Token"
   - Select your App
   - **Expiration: Never** ← IMPORTANT!
   - Permissions:
     - ✅ `whatsapp_business_messaging`
     - ✅ `whatsapp_business_management`
   - Click "Generate"
   - **COPY THE TOKEN IMMEDIATELY** (shown once!)

5. **Save Token**
   Store in Railway environment as `WHATSAPP_ACCESS_TOKEN`

---

## Step 2: Deploy Backend to Railway

### Option A: CLI Deployment

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize in backend directory
cd backend
railway init

# Link to existing project or create new
railway link

# Deploy
railway up
```

### Option B: GitHub Integration (Recommended)

1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Click "New Project" → "Deploy from GitHub"
3. Select `abhijeetnaib/pocketbuzz`
4. Set root directory: `backend`
5. Railway auto-detects Python and deploys

### Configure Environment Variables

In Railway Dashboard → Variables:

```env
# Supabase (get from Supabase Dashboard → Settings → API)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=<your-supabase-anon-key>
SUPABASE_SERVICE_ROLE_KEY=<your-supabase-service-role-key>

# AI Services
OPENAI_API_KEY=sk-proj-xxx
FAL_API_KEY=xxx:xxx

# WhatsApp (USE PERMANENT TOKEN!)
WHATSAPP_PHONE_NUMBER_ID=<your-whatsapp-phone-id>
WHATSAPP_ACCESS_TOKEN=<YOUR_PERMANENT_SYSTEM_USER_TOKEN>

# URLs (update after deployment)
APP_URL=https://pocketbuzz.autoskout.com
API_URL=https://pocketbuzz-backend.railway.app
SECRET_KEY=<generate-random-32-char-string>
```

### Add Custom Domain (Optional)

1. Railway Dashboard → Settings → Domains
2. Add: `api.pocketbuzz.autoskout.com`
3. Configure DNS CNAME to Railway domain

---

## Step 3: Deploy Frontend to Vercel

### Option A: CLI Deployment

```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy
cd frontend
vercel --prod
```

### Option B: GitHub Integration (Recommended)

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click "New Project" → Import from GitHub
3. Select `abhijeetnaib/pocketbuzz`
4. Set root directory: `frontend`
5. Vercel auto-detects Next.js

### Configure Environment Variables

In Vercel Dashboard → Settings → Environment Variables:

```env
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=<your-supabase-anon-key>
NEXT_PUBLIC_API_URL=https://pocketbuzz-backend.railway.app
```

### Add Custom Domain

1. Vercel Dashboard → Settings → Domains
2. Add: `pocketbuzz.autoskout.com`
3. Configure DNS:
   ```
   Type: CNAME
   Name: pocketbuzz
   Value: cname.vercel-dns.com
   ```

---

## Step 4: Configure WhatsApp Webhook

After deploying backend, update Meta callback URL:

1. Go to [Meta Developer Portal](https://developers.facebook.com/)
2. Select your App → WhatsApp → Configuration
3. **Callback URL:** 
   ```
   https://pocketbuzz-backend.railway.app/webhook/whatsapp
   ```
   (or `https://api.pocketbuzz.autoskout.com/webhook/whatsapp`)
4. **Verify Token:** `pocketbuzz_webhook_verify_token`
5. Click "Verify and Save"
6. Subscribe to: `messages`

---

## Step 5: DNS Configuration for autoskout.com

Add these DNS records:

### Frontend (Vercel)
```
Type: CNAME
Name: pocketbuzz
Value: cname.vercel-dns.com
TTL: Auto
```

### Backend API (Railway) - Optional
```
Type: CNAME
Name: api.pocketbuzz
Value: <your-railway-domain>.railway.app
TTL: Auto
```

---

## Final Checklist

### Backend (Railway)
- [ ] Deployed successfully
- [ ] Health check passing: `https://YOUR_URL/health`
- [ ] All environment variables set
- [ ] Permanent WhatsApp token configured
- [ ] Webhook endpoint accessible

### Frontend (Vercel)  
- [ ] Deployed successfully
- [ ] Environment variables set
- [ ] Can reach backend API
- [ ] Login works

### WhatsApp
- [ ] Permanent System User token generated
- [ ] Webhook URL updated in Meta Dashboard
- [ ] `messages` webhook subscribed
- [ ] Test message delivery working

### Domain
- [ ] DNS propagated (may take 24-48 hours)
- [ ] SSL certificates active
- [ ] Custom domain accessible

---

## Testing Production

### 1. Health Check
```bash
curl https://pocketbuzz-backend.railway.app/health
```

### 2. Test Campaign Send (via API)
```bash
curl -X POST https://pocketbuzz-backend.railway.app/api/campaigns/YOUR_CAMPAIGN_ID/send
```

### 3. Test WhatsApp Webhook
```bash
curl "https://pocketbuzz-backend.railway.app/webhook/whatsapp?hub.mode=subscribe&hub.verify_token=pocketbuzz_webhook_verify_token&hub.challenge=test"
```

---

## Monitoring & Logs

### Railway
```bash
railway logs -f
```

### Vercel
- Dashboard → Deployments → View Logs

### WhatsApp API
- Meta Developer Portal → App → Webhooks → Recent Deliveries

---

## Rollback

### Railway
```bash
railway rollback
```

### Vercel
- Dashboard → Deployments → Click deployment → "..." → Promote to Production

---

## Cost Estimates

| Service | Free Tier | Paid |
|---------|-----------|------|
| Railway | $5/month credit | ~$10-20/month |
| Vercel | 100GB bandwidth | ~$20/month (Pro) |
| Supabase | 500MB storage | ~$25/month (Pro) |
| OpenAI | Pay-per-use | ~$5-20/month |
| Fal.ai | Pay-per-use | ~$5-10/month |
| WhatsApp | 1000 free/month | Pay-per-message |

**Total Estimated:** $25-75/month for moderate usage

---

## Support

- Railway: https://docs.railway.app
- Vercel: https://vercel.com/docs
- WhatsApp Business API: https://developers.facebook.com/docs/whatsapp

---

*Last Updated: 2026-02-07*
