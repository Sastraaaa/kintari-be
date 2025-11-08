# 🚀 Kintari Backend - Railway Deployment Guide

Backend API untuk Kintari AI dengan Gemini integration dan SQLite database.

## 📋 Prerequisites

- Railway account (sign up di [railway.app](https://railway.app))
- GitHub repository dengan kode ini
- Gemini API Key dari [Google AI Studio](https://makersuite.google.com/app/apikey)

## 🚂 Deploy ke Railway

### Step 1: Create New Project

1. Login ke Railway Dashboard
2. Click **"New Project"**
3. Pilih **"Deploy from GitHub repo"**
4. Select repository: `Sastraaaa/kintari-be`
5. Railway akan auto-detect Python project

### Step 2: Set Environment Variables

Di Railway Dashboard → Variables, tambahkan:

```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
ALLOWED_ORIGINS=https://your-frontend.railway.app
```

⚠️ **PENTING:** Ganti `your_actual_gemini_api_key_here` dengan API key asli Anda!

### Step 3: Deploy

Railway akan otomatis:
- ✅ Detect Python 3.11
- ✅ Install dependencies dari `requirements.txt`
- ✅ Create SQLite database di `/app/kintari.db`
- ✅ Start server dengan Uvicorn
- ✅ Generate public URL

## 🔧 Configuration Files

File-file berikut sudah di-configure untuk Railway:

- `Procfile` - Start command
- `railway.json` - Railway configuration
- `nixpacks.toml` - Python version & build config
- `requirements.txt` - Python dependencies

## 📊 Database

Database SQLite akan di-create otomatis di:
```
/app/kintari.db
```

Railway menggunakan **persistent disk** - data TIDAK hilang saat redeploy.

## 🌐 Access Your API

Setelah deploy selesai, Railway akan berikan URL seperti:
```
https://kintari-be-production.up.railway.app
```

Test API:
- Docs: `https://your-url.railway.app/docs`
- Health: `https://your-url.railway.app/health`

## 🔐 Environment Variables Required

| Variable | Description | Example |
|----------|-------------|---------|
| `GEMINI_API_KEY` | **REQUIRED** - Gemini API key | `AIzaSy...` |
| `ALLOWED_ORIGINS` | CORS origins | `https://fe.railway.app` |
| `PORT` | Auto-set by Railway | `8000` (don't override) |

## 📝 Update Deployment

Setiap kali push ke GitHub, Railway akan auto-redeploy:

```bash
git add .
git commit -m "Update backend"
git push origin master
```

## 🐛 Troubleshooting

### Database tidak ter-create
Railway logs:
```bash
railway logs
```

### CORS errors
Pastikan `ALLOWED_ORIGINS` sudah include frontend URL.

### Port binding error
Jangan set `PORT` manual - Railway akan set otomatis.

## 📞 Support

Issues: https://github.com/Sastraaaa/kintari-be/issues
