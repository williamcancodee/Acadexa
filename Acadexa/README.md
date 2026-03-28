# AcaDexa 2.0 - Curated Academic Resources

Release notes: `RELEASE_NOTES_ACADEXA_2.0.md`

## Overview
Acadexa generates tailored PDF study packs from books, videos, articles, and open-source libraries based on grade/subject selections. Now with full PostgreSQL backend for users, search history, caching, ratings, and downloads.

## Entrypoint Cleanup
- Canonical app entrypoint: `main_fixed.py`
- Compatibility launchers retained (not deleted): `main.py`, `main_db.py`
- Recommended local run command: `python main_fixed.py`
- Recommended production start command: `gunicorn main_fixed:app`

## Local Setup
1. Copy `.env.example` to `.env`:
   ```
   DATABASE_URL=sqlite:///instance/acadexa.db
   SECRET_KEY=your-super-secret-key
   ```
   For PostgreSQL: `DATABASE_URL=postgresql://user:pass@localhost/acadexa`

2. Install deps:
   ```
   pip install -r requirements.txt
   ```

3. Init DB:
   ```
   flask --app main_fixed db init
   flask --app main_fixed db migrate -m "Initial"
   flask --app main_fixed db upgrade
   ```
   Or dev quick:
   ```
   python main_fixed.py  # Auto-creates tables
   ```

4. Create superuser:
   ```
   flask --app main_fixed create-superuser
   ```

5. Run:
   ```
   python main_fixed.py
   ```
   Visit `http://localhost:5000`

## Production (Render/Heroku)
- Set `DATABASE_URL` (PostgreSQL).
- `Procfile`: `web: gunicorn main_fixed:app`
- `requirements.txt` has gunicorn.

## Features
- **Auth**: Register/Login/Logout.
- **Caching**: Search results cached (24h).
- **Persistence**: History, downloads, ratings stored.
- **PDF Export**: Tracked with stats.

## CLI
```
flask --app main_fixed init-db
flask --app main_fixed create-superuser
```

DB ready! Use `python main_fixed.py` for dev (SQLite auto-init), or set PostgreSQL in .env.

