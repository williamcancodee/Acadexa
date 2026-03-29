# Acadexa 2.0 Release Notes

Release Date: 2026-03-28
Release Name: `acadexa 2.0`

## Summary
Acadexa 2.0 introduces a full UI/UX overhaul, stronger level-aware resource curation, broader learning-source coverage, cleaner PDF exports, and a database-backed app path for persistence features.

## Major Highlights

### 1. Product and Design Overhaul
- New modern academic visual identity across the app.
- Doodle-style educational background and refined interface.
- Custom bold Acadexa logo integrated across pages.
- New brand placement pattern with `Academia Reimagined` as the core motto.

### 2. Better Curation Quality by Learner Level
- Level-specific recommendation profiles added for:
  - Elementary school
  - Middle school
  - High school
  - College/University
- Level-aware scoring and filtering to reduce overlap between beginner and advanced recommendations.
- Improved deduplication of repeated results.

### 3. Broader Source Coverage
Expanded source aggregation for wider academic material access:
- Open Library
- Google Books
- Project Gutenberg links
- YouTube
- Wikipedia
- arXiv
- OpenAlex
- GitHub repositories
- OER Commons links
- Academic PDF links

### 4. PDF Export 2.0
- Branded cover page.
- Compact table of contents.
- Cleaner grouped sections by resource type.
- Alternating visual blocks for readability.
- Better text wrapping/truncation and spacing.

### 5. New Interactivity and Feedback Loop
- Subject search/filter in selection UI.
- Select-all / clear-subject controls.
- Post-download review popup.
- Rating + comment API endpoint for feedback submission.

### 6. Database-Backed App Path
- `main_db.py` and `main_fixed.py` support database-backed workflows.
- Caching, search history, downloads, authentication, and review persistence paths available.

## Stability and Debug Notes
- Key modules compile cleanly (`py_compile`).
- App startup and root-route smoke tests completed successfully.
- Recent runtime fixes include:
  - Missing import correction for `ResourceRating`.
  - Review persistence path updated to avoid foreign-key mismatch in `main_db.py`.

## Deployment Notes (Render)
- Recommended start command: `python main_db.py` or `gunicorn main_fixed:app` based on chosen entrypoint.
- Ensure required env vars are set: `SECRET_KEY`, `DATABASE_URL`.
- For Postgres, prefer `postgresql://` URI format.

## Known Scope
- Local workspace currently has no `.git` repository metadata available, so no local git tag/release object was created here.
- This release file is ready to be committed and uploaded.
