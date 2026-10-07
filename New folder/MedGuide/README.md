# 💊 MedGuide — Medicine Usage Information Web App

A clean, modern Flask web application that lets users search and browse medicine information including uses, composition, precautions, side effects, and warnings.

## 🚀 Live Demo
Deployed on Vercel — [your-project.vercel.app](#)

---

## ✨ Features
- 🔍 Search medicines by name, category, or composition
- 💊 Browse by category: Tablets, Capsules, Syrups, Ointments
- 📋 Detailed medicine info: composition, uses, purpose, precautions, side effects, warnings
- ⚙️ Admin dashboard: Add & delete medicines
- 🗄️ SQLite database with 15 pre-seeded medicines
- 🌑 Premium dark UI with glassmorphism design

---

## 🗂️ Project Structure
```
MedGuide/
├── app.py              ← Flask application (Vercel entry point)
├── vercel.json         ← Vercel deployment config
├── requirements.txt    ← Python dependencies
├── .gitignore
├── templates/
│   ├── index.html      ← Home / Search / Category page
│   ├── medicine.html   ← Medicine detail page
│   └── admin.html      ← Admin dashboard
└── static/
    └── style.css       ← Premium dark UI styles
```

---

## 🛠️ Local Development

```bash
# 1. Clone / download the project
cd MedGuide

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
python app.py

# 4. Open in browser
# → http://127.0.0.1:5000
```

---

## ☁️ Deploy to Vercel

### Method 1 — Vercel CLI (recommended)
```bash
# Install Vercel CLI
npm install -g vercel

# Deploy (from project folder)
vercel --prod
```

### Method 2 — GitHub + Vercel Dashboard
1. Push this project to GitHub
2. Go to [vercel.com](https://vercel.com) → New Project → Import from GitHub
3. Vercel auto-detects `vercel.json` and deploys

---

## ⚠️ Vercel Database Note
Vercel serverless functions use `/tmp` for writable storage, which is **ephemeral** (resets on cold starts). The app auto-seeds 15 medicines on every cold start. For full persistence, integrate a cloud DB like [Supabase](https://supabase.com) (free tier).

---

## 🏥 Medical Disclaimer
This app is for **educational and informational purposes only**. It is not a substitute for professional medical advice, diagnosis, or treatment.
