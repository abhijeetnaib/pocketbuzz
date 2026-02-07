# PocketBuzz 🚀

**The AI Marketing Agent that lives in a restaurant owner's pocket.**

A Mobile-First PWA to automate retention marketing for Indian SMB restaurants.

## Features

- 📧 **Auto-Ingestion**: Parse daily POS sales reports via email
- 🤖 **AI Analytics**: Identify trends & opportunities automatically
- 🎨 **Creative Generation**: AI-powered posters & Hinglish captions
- 📱 **Magic Links**: No-login approval via WhatsApp
- 💬 **WhatsApp Blasts**: One-click campaign execution

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 14 (PWA) |
| Backend | Python FastAPI |
| Database | Supabase (PostgreSQL) |
| AI | OpenAI GPT-4o-mini + Fal.ai Flux.1 |
| Messaging | Meta WhatsApp Business API |
| Email | Twilio SendGrid |

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker (optional)

### Backend Setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### Docker Setup

```bash
cp .env.example .env
# Edit .env with your API keys
docker-compose up --build
```

## Project Structure

```
pocketbuzz/
├── backend/          # Python FastAPI
├── frontend/         # Next.js PWA
├── supabase/         # Database migrations
└── docker-compose.yml
```

## License

Proprietary - PocketBuzz © 2026
