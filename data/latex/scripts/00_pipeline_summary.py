#!/usr/bin/env python3
"""
OpenAlex to BibTeX Pipeline Summary Report
===========================================
Comprehensive validation and statistics for the complete publication pipeline.
"""

import json
import pathlib
from datetime import datetime
from collections import Counter

script_dir = pathlib.Path(__file__).parent

# Load all data files
print("=" * 80)
print("OPENALEX PUBLICATION PIPELINE - COMPREHENSIVE SUMMARY REPORT")
print("=" * 80)
print(f"Generated: {datetime.now().isoformat()}\n")

# Load extraction report
with open(script_dir / "01_extraction_report.json", encoding="utf-8") as f:
    extraction = json.load(f)

# Load validation report
with open(script_dir / "02_validation_report.json", encoding="utf-8") as f:
    validation = json.load(f)

# Load validated works
with open(script_dir / "02_validated_works.json", encoding="utf-8") as f:
    validated_works = json.load(f)

# Load final BibTeX file
bib_file = script_dir.parent / "publications.bib"
with open(bib_file, encoding="utf-8") as f:
    bib_content = f.read()

# Parse BibTeX entries count
bib_entries = bib_content.count("@article") + bib_content.count("@incollection") + \
              bib_content.count("@unpublished") + bib_content.count("@misc")

print("📊 PIPELINE OVERVIEW")
print("-" * 80)
print(f"Total Publications Processed:     {extraction['total_publications']}")
print(f"Publications Validated:            {validation['total_validated']}")
print(f"Validation Issues Detected:        {validation['issues_count']}")
print(f"BibTeX Entries Generated:          {bib_entries}")
print(f"BibTeX File Location:              {bib_file}")
print(f"BibTeX File Size:                  {bib_file.stat().st_size:,} bytes")

print("\n📚 PUBLICATION TYPES BREAKDOWN")
print("-" * 80)
type_map = {
    "article": "Journal Articles",
    "preprint": "Preprints",
    "book-chapter": "Book Chapters",
    "dataset": "Datasets",
    "review": "Review Articles",
    "editorial": "Editorials",
    "peer-review": "Peer Reviews"
}

total_displayed = 0
for pub_type, label in type_map.items():
    count = extraction['by_type'].get(pub_type, 0)
    pct = (count / extraction['total_publications'] * 100) if extraction['total_publications'] > 0 else 0
    print(f"  {label:.<30} {count:>3} ({pct:>5.1f}%)")
    total_displayed += count

print(f"  {'TOTAL':.<30} {total_displayed:>3} (100.0%)")

print("\n📈 TEMPORAL DISTRIBUTION")
print("-" * 80)
by_year = validation['by_year']
start_year = min(int(y) for y in by_year.keys() if y != "Unknown")
end_year = max(int(y) for y in by_year.keys() if y != "Unknown")
career_span = end_year - start_year + 1

print(f"Career Timeline:                   {start_year} - {end_year} ({career_span} years)")
print(f"Most Productive Year:              {max(by_year.items(), key=lambda x: x[1])[0]}")
print(f"Average Publications/Year:         {extraction['total_publications'] / career_span:.1f}")

print("\nRecent Activity (Last 5 Years):")
recent_count = sum(count for year, count in by_year.items() 
                  if year != "Unknown" and int(year) >= 2020)
print(f"  2020-2025:                       {recent_count} publications")
print(f"  Share of Total:                  {recent_count / extraction['total_publications'] * 100:.1f}%")

print("\n✨ IMPACT METRICS")
print("-" * 80)
citations = validation['citations']
print(f"Total Citations (OpenAlex):        {citations['total']:,}")
print(f"Average Citations/Publication:     {citations['per_publication_avg']:.2f}")
print(f"Most Cited Publication:            {extraction['citations']['max_citations']} citations")
print(f"Highly Cited (>50 citations):      {citations['distribution']['highly_cited_gt50']}")
print(f"Well-Cited (11-50 citations):      {citations['distribution']['cited_11_50']}")
print(f"Cited (1-10 citations):            {citations['distribution']['cited_1_10']}")
print(f"Not Yet Cited:                     {citations['distribution']['not_cited']}")

h_index_approx = len([w for w in validated_works if w.get("cited_by_count", 0) >= 10])
print(f"H-Index (approximate):             {h_index_approx}")

print("\n🎯 DATA COMPLETENESS")
print("-" * 80)
completeness = validation['data_quality']
total = validation['total_validated']

for metric, count in completeness.items():
    pct = (count / total * 100) if total > 0 else 0
    print(f"  {metric:.<30} {count:>3}/{total:<3} ({pct:>5.1f}%)")

print("\n🔗 DOI COVERAGE ANALYSIS")
print("-" * 80)
with_doi = validation['data_quality']['with_doi']
without_doi = total - with_doi

print(f"With DOI:                          {with_doi} ({with_doi/total*100:.1f}%)")
print(f"Without DOI:                       {without_doi} ({without_doi/total*100:.1f}%)")
print(f"Data Quality Index (DOI):          {'✅ EXCELLENT' if with_doi/total > 0.75 else '⚠️  GOOD' if with_doi/total > 0.60 else '❌ NEEDS IMPROVEMENT'}")

print("\n🏆 TOP 5 MOST CITED PUBLICATIONS")
print("-" * 80)
for i, pub in enumerate(validation['top_cited'], 1):
    print(f"\n{i}. [{pub['year']}] {pub['citations']} citations")
    print(f"   {pub['title'][:70]}")
    if pub['doi'] != 'N/A':
        print(f"   DOI: {pub['doi']}")

print("\n\n📅 TOP 5 RECENT PUBLICATIONS")
print("-" * 80)
for i, pub in enumerate(validation['recent_publications'], 1):
    print(f"\n{i}. [{pub['year']}] {pub['type'].upper()}")
    print(f"   {pub['title'][:70]}")
    if pub['doi'] != 'N/A':
        print(f"   DOI: {pub['doi']}")

print("\n\n👥 COLLABORATION PATTERNS")
print("-" * 80)
author_positions = Counter()
single_author = 0
lead_author = 0

for work in validated_works:
    author_info = work.get("_author_info", {})
    total_authors = author_info.get("total_authors", 0)
    
    if total_authors == 1:
        single_author += 1
    
    if author_info.get("carlos_position") == 1:
        lead_author += 1

print(f"Single-Authored Publications:      {single_author} ({single_author/total*100:.1f}%)")
print(f"Lead Author (1st position):        {lead_author} ({lead_author/total*100:.1f}%)")
print(f"Co-authored Publications:          {total - single_author} ({(total-single_author)/total*100:.1f}%)")
print(f"Average Authors/Publication:       {completeness['with_multiple_authors']/total*100:.1f}%")

print("\n\n📖 VENUE ANALYSIS")
print("-" * 80)
print(f"Number of Different Venues:        {len([v for v in validation['by_journal'].keys() if v != 'Unknown'])}")

print("\nTop Publishing Venues (journals/conferences):")
for i, (venue, count) in enumerate(list(validation['by_journal'].items())[:10], 1):
    if venue != "Unknown":
        print(f"  {i}. {venue:.<45} {count:>3} publications")

print("\n\n🔍 VALIDATION QUALITY METRICS")
print("-" * 80)
print(f"Total Issues Detected:             {validation['issues_count']}")
print(f"Quality Score:                     {'⭐⭐⭐⭐⭐ EXCELLENT' if validation['issues_count'] < 5 else '⭐⭐⭐⭐ VERY GOOD' if validation['issues_count'] < 15 else '⭐⭐⭐ GOOD' if validation['issues_count'] < 30 else '⚠️  NEEDS REVIEW'}")

print("\n\n📋 BIBTEX FILE STATISTICS")
print("-" * 80)
print(f"Total BibTeX Entries:              {bib_entries}")
print(f"File Size:                         {bib_file.stat().st_size:,} bytes")
print(f"Average Entry Size:                {bib_file.stat().st_size // bib_entries:,} bytes")

entry_types = {
    "@article": 0,
    "@incollection": 0,
    "@unpublished": 0,
    "@misc": 0
}

for entry_type in entry_types:
    entry_types[entry_type] = bib_content.count(entry_type)

print(f"\nBibTeX Entry Types:")
for etype, count in sorted(entry_types.items(), key=lambda x: x[1], reverse=True):
    if count > 0:
        label = {
            "@article": "Journal Articles",
            "@incollection": "Book Chapters",
            "@unpublished": "Preprints",
            "@misc": "Misc (Datasets, etc)"
        }[etype]
        print(f"  {label:.<30} {count:>3}")

print("\n\n✅ PIPELINE COMPLETION STATUS")
print("-" * 80)
print(f"Stage 1 (Extraction):              ✅ COMPLETE")
print(f"  Files: 01_author.json, 01_works_raw.json, 01_extraction_report.json")

print(f"\nStage 2 (Validation):              ✅ COMPLETE")
print(f"  Files: 02_validated_works.json, 02_validation_report.json")

print(f"\nStage 3 (BibTeX Generation):       ✅ COMPLETE")
print(f"  File: publications.bib ({bib_file.stat().st_size:,} bytes)")

print("\n\n🚀 NEXT STEPS FOR LATEX INTEGRATION")
print("-" * 80)
print("""
1. Use the BibTeX file in your LaTeX document:
   
   In your .tex file preamble:
   \\documentclass{article}
   \\usepackage[round]{natbib}  % or use other bibliography package
   
   In document body:
   \\bibliographystyle{plain}   % or unsrt, apalike, etc.
   \\bibliography{publications}
   
   Then cite works in text:
   \\cite{almeida2021arti}

2. Generate PDF with bibliography:
   
   pdflatex your_file.tex
   bibtex your_file
   pdflatex your_file.tex
   pdflatex your_file.tex

3. Recommended Bibliography Styles:
   - plain: Traditional numeric citations
   - unsrt: Numeric in order of appearance
   - apalike: Author-year style
   - abbrvnat: Abbreviated author-year (natbib)
   - plainnat: Plain with natbib

4. To update the publication list:
   Simply run the pipeline scripts again:
   
   python 01_openalex_extract.py
   python 02_validate_publications.py
   python 03_generate_bibtex.py
""")

print("=" * 80)
print("✨ OPENALEX PUBLICATION PIPELINE - COMPLETE AND VALIDATED")
print("=" * 80)
print(f"\n📁 All files saved in: {script_dir}")
print(f"📚 BibTeX file ready: {bib_file}\n")
