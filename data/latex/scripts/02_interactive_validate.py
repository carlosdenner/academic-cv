#!/usr/bin/env python3
"""
Interactive Publication Validation
Review each potentially problematic publication and decide whether to keep it.
"""

import json
import pathlib
from typing import Dict, Any, List


def display_work(work: Dict[str, Any], index: int, total: int):
    """Display publication details for review."""
    print("\n" + "=" * 80)
    print(f"PUBLICATION {index}/{total}")
    print("=" * 80)
    
    print(f"\nTitle: {work.get('title', 'Unknown')}")
    print(f"Year: {work.get('publication_year', 'N/A')}")
    print(f"Type: {work.get('type', 'Unknown')}")
    
    if work.get('doi'):
        print(f"DOI: {work['doi']}")
    
    # Authors
    authorships = work.get('authorships', [])
    if authorships:
        authors = [a.get('author', {}).get('display_name', 'Unknown') for a in authorships]
        print(f"\nAuthors ({len(authors)}):")
        for i, author in enumerate(authors[:5], 1):
            # Check if this is Carlos Denner
            is_carlos = False
            auth_obj = authorships[i-1].get('author', {})
            orcid = auth_obj.get('orcid', '') or ''
            if '0000-0002-4481-0115' in orcid:
                is_carlos = True
            
            marker = " ← YOU" if is_carlos else ""
            print(f"  {i}. {author}{marker}")
        
        if len(authors) > 5:
            print(f"  ... and {len(authors) - 5} more authors")
    
    # Institutions
    institutions = []
    for auth in authorships:
        for inst in auth.get('institutions', []):
            inst_name = inst.get('display_name', 'Unknown')
            if inst_name not in institutions:
                institutions.append(inst_name)
    
    if institutions:
        print(f"\nInstitutions:")
        for inst in institutions[:5]:
            print(f"  • {inst}")
        if len(institutions) > 5:
            print(f"  ... and {len(institutions) - 5} more")
    else:
        print("\nInstitutions: None listed")
    
    # Keywords
    keywords = work.get('keywords', [])
    if keywords:
        keyword_names = [k.get('display_name', '') for k in keywords]
        print(f"\nKeywords (top 10):")
        for kw in keyword_names[:10]:
            print(f"  • {kw}")
        if len(keyword_names) > 10:
            print(f"  ... and {len(keyword_names) - 10} more")
    else:
        print("\nKeywords: None listed")
    
    # Citations
    citations = work.get('cited_by_count', 0)
    print(f"\nCitations: {citations}")
    
    # Venue
    location = work.get('primary_location', {})
    if location and location.get('source'):
        venue = location['source'].get('display_name', 'Unknown')
        print(f"Venue: {venue}")


def get_user_decision() -> str:
    """Get user's decision about the publication."""
    while True:
        response = input("\n👉 Is this YOUR publication? [y/n/s(kip)/q(uit)]: ").strip().lower()
        if response in ['y', 'yes']:
            return 'keep'
        elif response in ['n', 'no']:
            return 'exclude'
        elif response in ['s', 'skip']:
            return 'skip'
        elif response in ['q', 'quit']:
            return 'quit'
        else:
            print("   Please enter 'y' (yes, keep it), 'n' (no, exclude it), 's' (skip for now), or 'q' (quit)")


def interactive_validation():
    """Run interactive validation session."""
    script_dir = pathlib.Path(__file__).parent
    
    # Load raw works and excluded list
    works_file = script_dir / "01_works_raw.json"
    excluded_file = script_dir / "02_excluded_works.json"
    
    if not works_file.exists():
        print("❌ Raw data not found. Run 01_openalex_extract.py first.")
        return
    
    if not excluded_file.exists():
        print("❌ No excluded works found. Run 02_validate_publications.py first.")
        return
    
    with open(works_file, encoding='utf-8') as f:
        all_works = json.load(f)
    
    with open(excluded_file, encoding='utf-8') as f:
        excluded_data = json.load(f)
        excluded_works = excluded_data if isinstance(excluded_data, list) else excluded_data.get('excluded_works', [])
    
    print("=" * 80)
    print("INTERACTIVE PUBLICATION VALIDATION")
    print("=" * 80)
    print(f"\nTotal excluded publications to review: {len(excluded_works)}")
    print("\nFor each publication, decide whether it's yours (keep) or not (exclude).")
    print("Controls: y=keep, n=exclude, s=skip, q=quit\n")
    
    # Create map of titles to works
    work_map = {w.get('title'): w for w in all_works}
    
    kept = []
    excluded = []
    skipped = []
    
    for i, excluded_work in enumerate(excluded_works, 1):
        title = excluded_work.get('title')
        reason = excluded_work.get('reason', 'Unknown reason')
        
        # Find full work data
        full_work = work_map.get(title)
        if not full_work:
            print(f"\n⚠️  Warning: Could not find full data for: {title[:60]}...")
            continue
        
        print(f"\n🔍 Exclusion reason: {reason}")
        display_work(full_work, i, len(excluded_works))
        
        decision = get_user_decision()
        
        if decision == 'keep':
            kept.append(full_work)
            print("   ✅ Marked to KEEP")
        elif decision == 'exclude':
            excluded.append({
                **excluded_work,
                'confirmed': True
            })
            print("   ❌ Confirmed EXCLUDE")
        elif decision == 'skip':
            skipped.append(excluded_work)
            print("   ⏭️  Skipped (no decision)")
        elif decision == 'quit':
            print("\n\n🛑 Validation interrupted. Saving progress...")
            break
    
    # Summary
    print("\n" + "=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)
    print(f"Reviewed: {i} publications")
    print(f"Kept (to add back): {len(kept)}")
    print(f"Excluded (confirmed): {len(excluded)}")
    print(f"Skipped: {len(skipped)}")
    
    # Save results
    if kept:
        additions_file = script_dir / "02_manual_additions.json"
        with open(additions_file, 'w', encoding='utf-8') as f:
            json.dump({
                'added_at': '2025-11-12',
                'total_additions': len(kept),
                'note': 'Publications manually reviewed and approved for inclusion',
                'works': kept
            }, f, indent=2, ensure_ascii=False)
        print(f"\n✅ Saved {len(kept)} additions to: {additions_file.name}")
    
    if excluded:
        confirmed_file = script_dir / "02_confirmed_exclusions.json"
        with open(confirmed_file, 'w', encoding='utf-8') as f:
            json.dump({
                'confirmed_at': '2025-11-12',
                'total_excluded': len(excluded),
                'note': 'Publications manually reviewed and confirmed as not yours',
                'excluded_works': excluded
            }, f, indent=2, ensure_ascii=False)
        print(f"❌ Saved {len(excluded)} confirmed exclusions to: {confirmed_file.name}")
    
    if skipped:
        skipped_file = script_dir / "02_skipped_review.json"
        with open(skipped_file, 'w', encoding='utf-8') as f:
            json.dump({
                'skipped_at': '2025-11-12',
                'total_skipped': len(skipped),
                'note': 'Publications skipped during manual review',
                'skipped_works': skipped
            }, f, indent=2, ensure_ascii=False)
        print(f"⏭️  Saved {len(skipped)} skipped publications to: {skipped_file.name}")
    
    print("\n💡 Next steps:")
    if kept:
        print(f"   1. Run 02_merge_manual.py to merge {len(kept)} approved publications")
    print(f"   2. Run 03_generate_bibtex.py to create updated bibliography")
    print(f"   3. Recompile CV")


if __name__ == "__main__":
    interactive_validation()
