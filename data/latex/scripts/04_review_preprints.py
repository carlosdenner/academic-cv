#!/usr/bin/env python3
"""
Interactive review of preprints to check if they've been published.
"""

import json
import pathlib


def review_preprints():
    """Review preprints interactively."""
    script_dir = pathlib.Path(__file__).parent
    validated_file = script_dir / "02_validated_works.json"
    
    with open(validated_file, encoding='utf-8') as f:
        data = json.load(f)
        works = data.get('works', [])
    
    preprints = [w for w in works if w.get('type') == 'preprint']
    
    print("=" * 80)
    print(f"PREPRINT REVIEW - {len(preprints)} items")
    print("=" * 80)
    
    reclassifications = []
    
    for i, work in enumerate(preprints, 1):
        print(f"\n{'='*80}")
        print(f"PREPRINT {i}/{len(preprints)}")
        print(f"{'='*80}")
        print(f"Title: {work.get('title')}")
        print(f"Year: {work.get('publication_year')}")
        print(f"DOI: {work.get('doi')}")
        
        # Show venue if available
        location = work.get('primary_location', {})
        if location and location.get('source'):
            venue = location['source'].get('display_name', 'Unknown')
            print(f"Venue: {venue}")
        
        print(f"\nCurrent type: {work.get('type')}")
        print("\nWhat should this be?")
        print("  1) article (published journal article)")
        print("  2) preprint (keep as is)")
        print("  3) incollection (book chapter)")
        print("  4) dataset")
        print("  5) peer-review")
        print("  s) skip")
        print("  q) quit")
        
        choice = input("\nYour choice: ").strip().lower()
        
        if choice == 'q':
            break
        elif choice == 's':
            continue
        elif choice == '1':
            reclassifications.append({
                'doi': work.get('doi'),
                'old_type': work.get('type'),
                'new_type': 'article'
            })
            work['type'] = 'article'
            print("   ✅ Changed to: article")
        elif choice == '2':
            print("   ⏭️  Kept as preprint")
        elif choice == '3':
            reclassifications.append({
                'doi': work.get('doi'),
                'old_type': work.get('type'),
                'new_type': 'book-chapter'
            })
            work['type'] = 'book-chapter'
            print("   ✅ Changed to: book-chapter")
        elif choice == '4':
            reclassifications.append({
                'doi': work.get('doi'),
                'old_type': work.get('type'),
                'new_type': 'dataset'
            })
            work['type'] = 'dataset'
            print("   ✅ Changed to: dataset")
        elif choice == '5':
            reclassifications.append({
                'doi': work.get('doi'),
                'old_type': work.get('type'),
                'new_type': 'peer-review'
            })
            work['type'] = 'peer-review'
            print("   ✅ Changed to: peer-review")
    
    # Save updated works
    if reclassifications:
        with open(validated_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Save reclassification log
        log_file = script_dir / "04_reclassifications.json"
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump({
                'total_reclassified': len(reclassifications),
                'reclassifications': reclassifications
            }, f, indent=2)
        
        print(f"\n✅ Saved {len(reclassifications)} reclassifications")
        print(f"   Updated: {validated_file}")
        print(f"   Log: {log_file}")
        print("\n💡 Next: Run 03_generate_bibtex.py to update bibliography")
    else:
        print("\nNo changes made.")


if __name__ == "__main__":
    review_preprints()
