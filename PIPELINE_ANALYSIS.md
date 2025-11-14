# Academic CV Pipeline Analysis

## Complete Data Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          STEP 1: SEED DATA                               │
├─────────────────────────────────────────────────────────────────────────┤
│ orcid_pull.py                                                            │
│   INPUT:  profiles.yaml → ORCID ID                                      │
│   API:    https://pub.orcid.org/v3.0/{orcid}/works                     │
│   OUTPUT: data/processed/orcid_seed.json                                │
│   PURPOSE: Get initial list of works from ORCID profile                 │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                     STEP 2: OPENALEX ENRICHMENT                          │
├─────────────────────────────────────────────────────────────────────────┤
│ openalex_enrich.py                                                       │
│   INPUT:  ORCID ID from profiles.yaml                                   │
│   API:    https://api.openalex.org/authors/{orcid}                     │
│   OUTPUT: data/processed/openalex_author.json                           │
│           data/processed/openalex_works.json                             │
│   PURPOSE: Get comprehensive works list with DOIs, venues, types        │
│   QUALITY: ★★★★★ (highest quality, normalized data)                     │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                     STEP 3: CROSSREF ENRICHMENT                          │
├─────────────────────────────────────────────────────────────────────────┤
│ crossref_fill.py                                                         │
│   INPUT:  data/processed/openalex_works.json                            │
│   API:    https://api.crossref.org/works/{doi}                         │
│   OUTPUT: data/processed/crossref_by_doi.json                           │
│   PURPOSE: Get detailed metadata (funders, licenses, abstracts)         │
│   QUALITY: ★★★★★ (authoritative DOI metadata)                           │
│   NOTES:  0.1s delay between requests (polite API usage)                │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                 STEP 4: ALTERNATIVE SOURCE IMPORTS                       │
├─────────────────────────────────────────────────────────────────────────┤
│ scholar_html_import.py                                                   │
│   INPUT:  data/raw/scholar_profile.html (saved webpage)                 │
│   OUTPUT: data/raw/scholar_html.json                                    │
│   EXTRACTS: 176 publications (title, authors, venue, year, citations)   │
│   QUALITY: ★★★☆☆ (no DOIs, citation counts useful)                      │
│                                                                           │
│ researchgate_html_import.py                                              │
│   INPUT:  data/raw/researchgate_profile.html (saved webpage)            │
│   OUTPUT: data/raw/researchgate_html.json                               │
│   EXTRACTS: 65 publications (title, url, year)                          │
│   QUALITY: ★★☆☆☆ (limited metadata, many duplicates)                    │
│   FEATURES: Deduplication by title, URL cleaning                        │
│                                                                           │
│ researchgate_import.py                                                   │
│   INPUT:  data/raw/researchgate_export.csv (CSV export)                 │
│   OUTPUT: data/processed/researchgate_works.json                        │
│   QUALITY: ★★★☆☆ (better than HTML, has DOIs sometimes)                 │
│                                                                           │
│ lattes_import.py                                                         │
│   INPUT:  data/raw/lattes.xml (Plataforma Lattes XML)                   │
│   OUTPUT: data/processed/lattes_works.json                              │
│   EXTRACTS: Publications only (articles, conference, books, chapters)   │
│   QUALITY: ★★★★☆ (authoritative for Brazilian context, has DOIs)        │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                STEP 5: COMPREHENSIVE CV DATA EXTRACTION                  │
├─────────────────────────────────────────────────────────────────────────┤
│ lattes_comprehensive.py                                                  │
│   INPUT:  data/raw/lattes.xml                                           │
│   OUTPUT: data/processed/lattes_comprehensive.json                      │
│   EXTRACTS:                                                              │
│     • Personal info (name, ORCID, citation names)                       │
│     • Education (7 degrees with funding agencies)                       │
│     • Positions (37 professional positions)                             │
│     • Projects (21 research projects with funding)                      │
│     • Supervisions (15 PhD/Masters students)                            │
│     • Awards (8 honors)                                                  │
│     • Research areas (6 areas)                                          │
│     • Languages (2 languages)                                           │
│     • Teaching (7 courses)                                              │
│     • Committees (thesis defenses)                                      │
│   QUALITY: ★★★★★ (complete academic career data)                        │
│   NOTES:  NOT merged with publications (separate use case)              │
│                                                                           │
│ cv_markdown_import.py                                                    │
│   INPUT:  data/raw/cv_markdown.md                                       │
│   OUTPUT: data/processed/cv_markdown.json                               │
│   EXTRACTS: 17 sections from existing CV                                │
│   PURPOSE: Baseline/reference for CV structure                          │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│               STEP 6: PUBLICATION DEDUPLICATION & MERGE                  │
├─────────────────────────────────────────────────────────────────────────┤
│ normalize_dedupe.py                                                      │
│   INPUTS (in priority order):                                           │
│     1. data/processed/openalex_works.json      (★★★★★ highest)          │
│     2. data/processed/lattes_works.json        (★★★★☆)                  │
│     3. scholar_bibtex (if available)           (★★★☆☆)                  │
│     4. data/raw/scholar_html.json              (★★★☆☆)                  │
│     5. data/processed/researchgate_works.json  (★★★☆☆)                  │
│     6. data/raw/researchgate_html.json         (★★☆☆☆ lowest)           │
│                                                                           │
│   ALGORITHM:                                                             │
│     Phase 1: DOI-based exact matching (outer join)                      │
│       - Merge records with same DOI                                     │
│       - Coalesce missing fields from lower priority sources             │
│                                                                           │
│     Phase 2: Fuzzy title matching for non-DOI records                   │
│       - Use rapidfuzz token_set_ratio scorer                            │
│       - Threshold: 92% similarity                                       │
│       - Fill in missing venue, URL, year from matches                   │
│                                                                           │
│     Phase 3: Add unique records from each source                        │
│       - Publications not matched by DOI or title                        │
│       - Preserves source-specific publications                          │
│                                                                           │
│   OUTPUT: data/processed/works_merged.json                              │
│   RESULT: Deduplicated publication list with best metadata              │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                     STEP 7: CV RENDERING                                 │
├─────────────────────────────────────────────────────────────────────────┤
│ render.py                                                                │
│   INPUTS:                                                                │
│     • data/processed/works_merged.json (publications)                   │
│     • data/processed/lattes_comprehensive.json (CV sections)            │
│     • templates/{awesome-cv,moderncv,markdown}.tex.j2                   │
│     • profiles.yaml (template choice)                                   │
│                                                                           │
│   PROCESS:                                                               │
│     1. Load merged publications                                         │
│     2. Load comprehensive CV data                                       │
│     3. Organize by type/year                                            │
│     4. Render chosen template with Jinja2                               │
│     5. Compile LaTeX to PDF (if needed)                                 │
│                                                                           │
│   OUTPUT: build/cv.{pdf,md,tex}                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Data Quality by Source

| Source | DOIs | Venues | Years | Authors | Citations | Abstracts | Funders |
|--------|------|--------|-------|---------|-----------|-----------|---------|
| OpenAlex | ✓✓✓ | ✓✓✓ | ✓✓✓ | ✓✓✓ | ✓✓ | ✗ | ✗ |
| Crossref | ✓✓✓ | ✓✓✓ | ✓✓✓ | ✓✓ | ✓✓ | ✓✓✓ | ✓✓✓ |
| Lattes | ✓✓ | ✓✓ | ✓✓✓ | ✗ | ✗ | ✗ | ✗ |
| Scholar HTML | ✗ | ✓ | ✓✓ | ✓ | ✓✓✓ | ✗ | ✗ |
| RG HTML | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ |
| RG CSV | ✓ | ✓✓ | ✓✓ | ✓ | ✗ | ✗ | ✗ |

## Current Issues & Recommendations

### ✅ Strengths:
1. **Smart priority system** — OpenAlex first, then authoritative sources
2. **Robust deduplication** — DOI exact match + 92% fuzzy title matching
3. **Multiple fallbacks** — HTML parsing when exports unavailable
4. **Comprehensive data** — Beyond publications (education, projects, etc.)
5. **Clean organization** — All raw files in `data/raw/`

### ⚠️ Potential Issues:

1. **Crossref data not used in merge**
   - Crossref enrichment stored in `crossref_by_doi.json`
   - But `normalize_dedupe.py` doesn't read it
   - **Missing:** Abstracts, funders, licenses
   - **Fix:** Merge crossref data into OpenAlex records before deduplication

2. **ORCID seed data not used**
   - `orcid_pull.py` creates `orcid_seed.json`
   - But never consumed by pipeline
   - **Impact:** Minimal (OpenAlex gets same data via ORCID anyway)
   - **Fix:** Could remove or use as validation check

3. **Lattes comprehensive vs lattes_works duplication**
   - Two parsers reading same XML file
   - `lattes_import.py` → publications only
   - `lattes_comprehensive.py` → everything including publications
   - **Fix:** Could extract publications from comprehensive parse

4. **No integration of markdown CV**
   - `cv_markdown_import.py` parses existing CV
   - But data not used in rendering
   - **Purpose:** Unclear (baseline? validation?)

5. **Missing fields in merged output**
   - No author names in final merge (except from Scholar)
   - No citation counts (except from Scholar)
   - No abstracts (Crossref has them)
   - **Impact:** Less rich CV metadata

### 🔧 Recommended Improvements:

**Priority 1: Integrate Crossref enrichment**
```python
# In normalize_dedupe.py, after loading OpenAlex:
crossref = json.load(open("data/processed/crossref_by_doi.json"))
for work in ox:
    doi = work.get("doi","").lower()
    if doi in crossref:
        # Add abstract, funders, license
        work["abstract"] = crossref[doi].get("abstract")
        work["funders"] = crossref[doi].get("funder", [])
        work["license"] = crossref[doi].get("license", [])
```

**Priority 2: Extract authors from OpenAlex**
```python
# OpenAlex has authorships with names
for w in ox:
    authors = [a.get("author",{}).get("display_name") 
               for a in w.get("authorships",[])]
    rows.append({
        # ... existing fields ...
        "authors": ", ".join(authors)
    })
```

**Priority 3: Add citation counts**
```python
# Merge Scholar citation counts into final output
# Scholar HTML has "citations" field
# Could add to merged records for metrics
```

**Priority 4: Validation reporting**
```python
# Add summary statistics at end of normalize_dedupe.py
print(f"\nSource contributions:")
print(f"  OpenAlex: {len(df_ox)} records")
print(f"  Lattes: {len(df_lt)} records")
print(f"  Scholar: {len(df_sch_html)} records")
print(f"  ResearchGate: {len(df_rg_html)} records")
print(f"  After dedup: {len(merged)} records")
print(f"  Unique DOIs: {merged['doi'].astype(bool).sum()}")
```

## Pipeline Execution Time Estimate

| Step | Time | Notes |
|------|------|-------|
| ORCID pull | ~1s | Single API call |
| OpenAlex | ~5-10s | Paginated (200 per page) |
| Crossref | ~5-30s | 0.1s × number of DOIs |
| Scholar HTML | <1s | Local file parse |
| RG HTML | <1s | Local file parse |
| Lattes works | ~1s | XML parse |
| Lattes comprehensive | ~2s | Full XML parse |
| Markdown import | <1s | Text parse |
| Normalize/dedupe | ~2-5s | Fuzzy matching intensive |
| **TOTAL** | **~20-50s** | Depends on record count |

## Next Steps

Would you like me to:
1. **Fix Crossref integration** — Add abstracts/funders to merged output
2. **Add author extraction** — Get author names from OpenAlex
3. **Add validation stats** — Show deduplication metrics
4. **Optimize lattes parsing** — Single parser for publications + CV data
5. **Test full pipeline** — Run `make update` and check all outputs
