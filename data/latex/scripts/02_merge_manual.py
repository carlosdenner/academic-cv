#!/usr/bin/env python3
"""
Merge manually approved publications with validated publications.
"""

import json
import pathlib
from datetime import datetime


def merge_publications():
    """Merge validated works with manual additions."""
    script_dir = pathlib.Path(__file__).parent
    
    # Load validated works
    validated_file = script_dir / "02_validated_works.json"
    if not validated_file.exists():
        print("❌ Validated works not found. Run 02_validate_publications.py first.")
        return
    
    with open(validated_file, encoding='utf-8') as f:
        validated_data = json.load(f)
        validated_works = validated_data if isinstance(validated_data, list) else validated_data.get('works', [])
    
    # Load manual additions
    additions_file = script_dir / "02_manual_additions.json"
    if not additions_file.exists():
        print("❌ No manual additions found. Run 02_interactive_validate.py first.")
        return
    
    with open(additions_file, encoding='utf-8') as f:
        additions_data = json.load(f)
        manual_works = additions_data.get('works', [])
    
    if not manual_works:
        print("ℹ️  No publications to add.")
        return
    
    print("=" * 80)
    print("MERGING MANUAL ADDITIONS")
    print("=" * 80)
    
    print(f"\nValidated works: {len(validated_works)}")
    print(f"Manual additions: {len(manual_works)}")
    
    # Mark manual additions
    for work in manual_works:
        work['_validated'] = True
        work['_orcid_verified'] = True
        work['_content_verified'] = True
        work['_manually_approved'] = True
    
    # Merge (avoid duplicates by DOI)
    existing_dois = {w.get('doi') for w in validated_works if w.get('doi')}
    
    added_count = 0
    duplicate_count = 0
    
    for work in manual_works:
        doi = work.get('doi')
        if doi and doi in existing_dois:
            print(f"   ⚠️  Duplicate (already in validated): {work.get('title', 'Unknown')[:60]}...")
            duplicate_count += 1
            continue
        
        validated_works.append(work)
        added_count += 1
        print(f"   ✅ Added: {work.get('title', 'Unknown')[:60]}...")
    
    # Save merged results
    merged_file = script_dir / "02_validated_works.json"
    output = {
        "validated_at": datetime.now().isoformat(),
        "total_works": len(validated_works),
        "includes_manual_additions": added_count,
        "works": validated_works
    }
    
    with open(merged_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 80)
    print("MERGE COMPLETE")
    print("=" * 80)
    print(f"Total publications: {len(validated_works)}")
    print(f"Added from manual review: {added_count}")
    print(f"Duplicates skipped: {duplicate_count}")
    print(f"\n✅ Updated: {merged_file}")
    print("\n💡 Next: Run 03_generate_bibtex.py to create updated bibliography")


if __name__ == "__main__":
    merge_publications()
