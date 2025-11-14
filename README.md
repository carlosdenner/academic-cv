# Academic CV — ORCID + OpenAlex + Crossref + Scholar + ResearchGate + Lattes (XML)

This repo consolidates your academic records and renders a CV in **Awesome-CV**, **moderncv**, or Markdown/PDF.

**Data sources**
- ORCID (identity/works) → seed
- OpenAlex (normalized graph; works by ORCID)
- Crossref (funder/license/abstracts by DOI)
- Google Scholar (BibTeX export **or** saved HTML profile page)
- ResearchGate (CSV export **or** saved HTML profile page)
- **Lattes XML** (Plataforma Lattes export you provide)
  - **Publications** (articles, books, chapters)
  - **Education** (Bachelor, Masters, PhD, Post-doc with funding agencies)
  - **Positions** (37 professional positions with dates and institutions)
  - **Projects** (21 research projects with funding details: CNPq, FAPESP, Fulbright, CAPES)
  - **Supervisions** (15 PhD/Masters supervisions: completed + ongoing)
  - **Committees** (thesis defenses, qualification exams)
  - **Awards** (8 honors and certifications)
  - **Research Areas** (6 areas of expertise)
  - **Languages** (proficiency levels)
  - **Teaching** (courses taught with dates and institutions)

**Run**
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
make update
make render   # uses profiles.yaml:template (awesome-cv | moderncv | markdown)
```

## Data Organization

All raw source files should be placed in `data/raw/`:

**Required files (configured in `profiles.yaml`):**
- `data/raw/lattes.xml` — Plataforma Lattes XML export
- `data/raw/scholar_profile.html` — Saved Google Scholar profile page **OR** `scholar_export.bib`
- `data/raw/researchgate_profile.html` — Saved ResearchGate profile page **OR** `researchgate_export.csv`
- `data/raw/cv_markdown.md` — Existing CV in markdown format (optional)

**Generated files:**
- `data/raw/scholar_html.json` — Parsed Scholar data
- `data/raw/researchgate_html.json` — Parsed ResearchGate data
- `data/processed/lattes_comprehensive.json` — Complete CV data from Lattes
- `data/processed/cv_markdown.json` — Parsed markdown CV
- `data/processed/works_merged.json` — Deduplicated publications

**File structure:**
```
data/
├── raw/                    # Raw source files (your exports/saves)
│   ├── lattes.xml
│   ├── scholar_profile.html
│   ├── researchgate_profile.html
│   ├── cv_markdown.md
│   ├── scholar_html.json
│   └── researchgate_html.json
└── processed/              # Parsed and processed data
    ├── lattes_comprehensive.json
    ├── cv_markdown.json
    └── works_merged.json
```

See `.windsurf/INSTRUCTIONS.md` for one-shot automation.
