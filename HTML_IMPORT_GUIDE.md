# HTML Import Guide

Your academic CV pipeline now supports importing publications from **saved HTML pages** of your Google Scholar and ResearchGate profiles!

## ✅ What's New

Two new scripts have been added:
- **`scripts/scholar_html_import.py`** - Extracts publications from saved Google Scholar profile pages
- **`scripts/researchgate_html_import.py`** - Extracts publications from saved ResearchGate profile pages

These scripts automatically run as part of `make update`.

## 📥 How to Use

### Option 1: Google Scholar HTML (Alternative to BibTeX)

1. **Open your Google Scholar profile** in a browser
2. **Save the page**: `Ctrl+S` (Windows) or `Cmd+S` (Mac)
3. **Save as**: "Webpage, Complete" or "HTML only"
4. **Place the HTML file** in the root directory with the name it was saved as (e.g., `_Carlos Denner dos Santos_ - _Google Académico_.html`)
5. Run `make update` or `python scripts/scholar_html_import.py`

**What it extracts:**
- ✅ Title
- ✅ Authors
- ✅ Venue
- ✅ Year
- ✅ Citation count
- ✅ Google Scholar URL

### Option 2: ResearchGate HTML (Alternative to CSV)

1. **Open your ResearchGate profile** → Research tab
2. **Save the page**: `Ctrl+S` (Windows) or `Cmd+S` (Mac)
3. **Save as**: "Webpage, Complete" or "HTML only"
4. **Place the HTML file** in the root directory as `ResearchGate.html`
5. Run `make update` or `python scripts/researchgate_html_import.py`

**What it extracts:**
- ✅ Title
- ✅ ResearchGate URL
- ⚠️ Year (if present in title)

## 🔄 Integration with Pipeline

The HTML sources are integrated into the deduplication process with this priority:

1. **ORCID** (seed data)
2. **OpenAlex** (highest priority - most complete metadata)
3. **Lattes** (Brazilian CV platform)
4. **Google Scholar BibTeX** (if provided)
5. **Google Scholar HTML** ← NEW!
6. **ResearchGate CSV** (if provided)
7. **ResearchGate HTML** ← NEW! (lowest priority)

Publications are deduplicated by:
- **DOI matching** (exact)
- **Title + Year fuzzy matching** (92% similarity threshold)

## 🎯 Current Status

**Your saved files:**
- ✅ `_Carlos Denner dos Santos_ - _Google Académico_.html` - **176 publications extracted**
- ✅ `ResearchGate.html` - **65 publications extracted**

## 🚀 Next Steps

Run the full pipeline to merge everything:

```bash
make update
make render
```

Or step by step:
```bash
python scripts/scholar_html_import.py
python scripts/researchgate_html_import.py
python scripts/normalize_dedupe.py
python scripts/render.py
```

## 💡 Tips

- **Google Scholar HTML** is better than BibTeX for most users - it includes citation counts!
- **HTML imports work offline** - no API keys needed
- You can use **both** BibTeX/CSV and HTML sources - the pipeline will merge and deduplicate
- Re-save and re-run whenever your profiles are updated

## 🐛 Limitations

- **ResearchGate HTML parsing** may miss some metadata (authors, DOI, abstract) - the CSV export is more complete if available
- **Year extraction** for ResearchGate HTML is limited - only extracted if present in title
- HTML structure changes could break parsing - tested on Nov 2025 format
