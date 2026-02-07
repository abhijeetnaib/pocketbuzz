# PocketBuzz Frontend - Vercel Deployment

## Quick Deploy to Vercel

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/abhijeetnaib/pocketbuzz&root-directory=frontend)

---

## Manual Deployment Steps

### 1. Install Vercel CLI
```bash
npm install -g vercel
vercel login
```

### 2. Deploy Frontend
```bash
cd frontend
vercel --prod
```

### 3. Configure Environment Variables

In Vercel Dashboard → Settings → Environment Variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `NEXT_PUBLIC_SUPABASE_URL` | Supabase project URL | `https://xxx.supabase.co` |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Supabase anonymous key | `sb_publishable_xxx` |
| `NEXT_PUBLIC_API_URL` | Backend API URL (Railway) | `https://xxx.railway.app` |

---

## Custom Domain Setup (autoskout.com)

### 1. Add Domain in Vercel
- Go to: Project Settings → Domains
- Add domain: `pocketbuzz.autoskout.com`

### 2. Configure DNS
Add these DNS records at your domain registrar:

**For subdomain (pocketbuzz.autoskout.com):**
```
Type: CNAME
Name: pocketbuzz
Value: cname.vercel-dns.com
```

**For apex domain (autoskout.com):**
```
Type: A
Name: @
Value: 76.76.21.21
```

### 3. Verify Domain
- Vercel will automatically provision SSL
- Domain should be active within 24-48 hours

---

## Production Configuration

### Update Backend CORS

After deployment, update the backend to allow requests from your production domain.

In Railway environment variables:
```
APP_URL=https://pocketbuzz.autoskout.com
```

Or update `backend/app/main.py`:
```python
allow_origins=[
    settings.app_url,
    "https://pocketbuzz.autoskout.com",
    "http://localhost:3000",
]
```

---

## Production Checklist

- [ ] Vercel project created
- [ ] Environment variables configured
- [ ] Custom domain added (pocketbuzz.autoskout.com)
- [ ] DNS records configured
- [ ] SSL certificate provisioned
- [ ] Backend CORS updated
- [ ] Production build successful

---

## Build Settings

Vercel auto-detects Next.js. Default settings:
- **Framework Preset:** Next.js
- **Root Directory:** `frontend`
- **Build Command:** `npm run build`
- **Output Directory:** `.next`

---

## Performance Optimizations

Vercel automatically provides:
- Edge caching
- Image optimization
- Automatic code splitting
- Serverless functions

---

## Monitoring

Vercel Dashboard provides:
- Real-time logs
- Performance analytics
- Error tracking
- Deployment history

---

## Troubleshooting

### API Connection Failed
**Solution:** Ensure `NEXT_PUBLIC_API_URL` points to your Railway backend URL

### CORS Error
**Solution:** Update backend `APP_URL` to include your Vercel domain

### Build Failed
**Solution:** Check build logs in Vercel Dashboard → Deployments
