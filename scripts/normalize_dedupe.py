import json, yaml, bibtexparser, pandas as pd
from rapidfuzz import process, fuzz

p = yaml.safe_load(open("profiles.yaml"))
def load_json(path, cols):
    try:
        return pd.DataFrame(json.load(open(path)))[cols]
    except Exception:
        return pd.DataFrame(columns=cols)

# Expanded columns to include authors, citations, abstract, funders
cols = ["title","year","type","venue","doi","url","authors","citations","abstract","funders"]

# Load Crossref enrichment data
try:
    crossref = json.load(open("data/processed/crossref_by_doi.json"))
except FileNotFoundError:
    crossref = {}

# OpenAlex
try:
    ox = json.load(open("data/processed/openalex_works.json"))
except FileNotFoundError:
    ox = []

rows = []
for w in ox:
    doi = (w.get("doi") or "").lower()
    
    # Extract author names from authorships
    authors = []
    for authorship in w.get("authorships", []):
        author = authorship.get("author", {})
        name = author.get("display_name", "")
        if name:
            authors.append(name)
    
    # Get citation count
    citations = w.get("cited_by_count", 0)
    
    # Merge Crossref enrichment if available
    abstract = ""
    funders = []
    if doi and doi in crossref:
        cr = crossref[doi]
        abstract = cr.get("abstract", "")
        funders = [f.get("name", "") for f in cr.get("funder", [])]
    
    rows.append({
      "title": (w.get("title") or "").strip(),
      "year": (w.get("publication_year") or w.get("from_year")),
      "type": (w.get("type") or ""),
      "venue": ((w.get("primary_location") or {}).get("source") or {}).get("display_name") or "",
      "doi": doi,
      "url": ((w.get("primary_location") or {}).get("landing_page_url") or w.get("landing_page_url") or ""),
      "authors": ", ".join(authors),
      "citations": citations,
      "abstract": abstract,
      "funders": ", ".join(funders)
    })

df_ox = pd.DataFrame(rows) if rows else pd.DataFrame(columns=cols)

# Lattes
df_lt = load_json("data/processed/lattes_works.json", cols)

# ResearchGate CSV
df_rg = load_json("data/processed/researchgate_works.json", cols)

# ResearchGate HTML
df_rg_html = load_json("data/raw/researchgate_html.json", cols)

# Scholar BibTeX
try:
    with open(p["scholar_bibtex"]) as f:
        bib = bibtexparser.load(f)
    sch = [{
        "title": e.get("title","").strip().strip("{}"),
        "year": e.get("year"),
        "type": e.get("ENTRYTYPE"),
        "venue": e.get("journal") or e.get("booktitle"),
        "doi": (e.get("doi") or "").lower(),
        "url": e.get("url") or "",
        "authors": "",
        "citations": 0,
        "abstract": "",
        "funders": ""
    } for e in bib.entries]
    df_sch = pd.DataFrame(sch)
except FileNotFoundError:
    df_sch = pd.DataFrame(columns=cols)

# Scholar HTML - includes citations
try:
    scholar_data = json.load(open("data/raw/scholar_html.json"))
    # Scholar HTML has: title, authors, venue, year, citations, url
    scholar_rows = []
    for item in scholar_data:
        scholar_rows.append({
            "title": item.get("title", ""),
            "year": item.get("year"),
            "type": "",
            "venue": item.get("venue", ""),
            "doi": "",
            "url": item.get("url", ""),
            "authors": item.get("authors", ""),
            "citations": item.get("citations", 0),  # PRESERVE CITATIONS
            "abstract": "",
            "funders": ""
        })
    df_sch_html = pd.DataFrame(scholar_rows) if scholar_rows else pd.DataFrame(columns=cols)
except Exception:
    df_sch_html = pd.DataFrame(columns=cols)

# Merge priority: OpenAlex > Lattes > Scholar BibTeX > Scholar HTML > ResearchGate CSV > ResearchGate HTML
merged = df_ox.copy()

def append_missing(df_source, merged):
    if df_source.empty: 
        return merged
    # 1) DOI join (outer)
    src_with_doi = df_source[df_source["doi"].astype(str)!=""]
    if not src_with_doi.empty:
        merged = pd.merge(merged, src_with_doi, on="doi", how="outer", suffixes=("","_src"))
        # coalesce fields - prefer existing, fallback to source
        for c in ["title","venue","url","year","authors","abstract","funders"]:
            merged[c] = merged[c].astype(str)
            cs = f"{c}_src"
            if cs in merged.columns:
                merged[c] = merged[c].where(merged[c].astype(bool), merged[cs])
                merged.drop(columns=[cs], inplace=True)
        # For citations, take the maximum value (most up-to-date)
        if "citations_src" in merged.columns:
            merged["citations"] = pd.to_numeric(merged["citations"], errors='coerce').fillna(0)
            merged["citations_src"] = pd.to_numeric(merged["citations_src"], errors='coerce').fillna(0)
            merged["citations"] = merged[["citations", "citations_src"]].max(axis=1)
            merged.drop(columns=["citations_src"], inplace=True)
    # 2) Title+year fuzzy for DOI-less
    no_doi_mask = merged["doi"].astype(str) == ""
    remaining = df_source[df_source["doi"].astype(str)==""]
    for i, row in merged[no_doi_mask][["title","year"]].fillna("").iterrows():
        if not remaining.empty and row["title"]:
            cand = process.extractOne(row["title"], remaining["title"], scorer=fuzz.token_set_ratio)
            if cand and cand[1] >= 92:
                idx = remaining[remaining["title"]==cand[0]].index[0]
                # Fill in missing fields from fuzzy match
                for col in ["title","venue","url","year","authors","abstract","funders"]:
                    merged.loc[i,col] = merged.loc[i,col] or str(remaining.loc[idx].get(col) or "")
                # For citations, take maximum
                if merged.loc[i,"citations"] == 0 or pd.isna(merged.loc[i,"citations"]):
                    merged.loc[i,"citations"] = remaining.loc[idx].get("citations", 0)
    # 3) Add source-only leftovers
    leftovers = remaining[~remaining["title"].isin(merged["title"])]
    if not leftovers.empty:
        merged = pd.concat([merged, leftovers], ignore_index=True)
    return merged

for df in [df_lt, df_sch, df_sch_html, df_rg, df_rg_html]:
    merged = append_missing(df, merged)

merged.fillna("", inplace=True)

# Validation: Compare with ORCID seed
try:
    orcid_seed = json.load(open("data/processed/orcid_seed.json"))
    orcid_count = len(orcid_seed.get("group", []))
    print(f"\n📊 VALIDATION CHECK:")
    print(f"  ORCID reports: {orcid_count} works")
    print(f"  OpenAlex found: {len(df_ox)} works")
    diff = len(df_ox) - orcid_count
    if diff > 0:
        print(f"  ✓ OpenAlex has {diff} additional works (good!)")
    elif diff < 0:
        print(f"  ⚠ ORCID has {abs(diff)} works not in OpenAlex")
    else:
        print(f"  ✓ Counts match perfectly")
except FileNotFoundError:
    print("\n⚠ ORCID seed not found - skipping validation")

# Statistics
path = "data/processed/works_merged.json"
open(path,"w", encoding='utf-8').write(json.dumps(merged.to_dict(orient="records"), indent=2, ensure_ascii=False))

print(f"\n📚 MERGE STATISTICS:")
print(f"  Source contributions:")
print(f"    OpenAlex:      {len(df_ox):4d} records")
print(f"    Lattes:        {len(df_lt):4d} records")
print(f"    Scholar BibTeX:{len(df_sch):4d} records")
print(f"    Scholar HTML:  {len(df_sch_html):4d} records")
print(f"    RG CSV:        {len(df_rg):4d} records")
print(f"    RG HTML:       {len(df_rg_html):4d} records")
print(f"  ─────────────────────────────")
print(f"  After deduplication: {len(merged)} unique works")
print(f"\n  Data quality:")
print(f"    With DOIs:      {merged['doi'].astype(bool).sum():4d} ({100*merged['doi'].astype(bool).sum()/len(merged):.1f}%)")
print(f"    With authors:   {merged['authors'].astype(bool).sum():4d} ({100*merged['authors'].astype(bool).sum()/len(merged):.1f}%)")
print(f"    With citations: {(pd.to_numeric(merged['citations'], errors='coerce') > 0).sum():4d}")
print(f"    With abstracts: {merged['abstract'].astype(bool).sum():4d}")
print(f"    With funders:   {merged['funders'].astype(bool).sum():4d}")
print(f"\n  ✓ Saved to: {path}")
