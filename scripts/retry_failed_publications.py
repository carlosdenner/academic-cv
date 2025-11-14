#!/usr/bin/env python3
"""
Retry Failed Publications

This script retries adding the 14 failed publications with better error handling.
"""

import json
from pathlib import Path
from datetime import datetime


def retry_failed_publications():
    """Retry failed publications with manual entries"""
    
    report_file = Path('c:/academic-cv/data/processed/add_publications_report.json')
    bib_file = Path('c:/academic-cv/data/latex/publications.bib')
    
    with open(report_file, 'r', encoding='utf-8') as f:
        report = json.load(f)
    
    failed = report['failed_items']
    
    print(f"Found {len(failed)} failed publications to retry\n")
    
    # Manual entries for failed publications (based on available metadata)
    manual_entries = []
    
    for item in failed:
        index = item['index']
        title = item['title']
        
        print(f"[{index}] {title[:60]}...")
        
        # Create a simple misc entry for items without enough metadata
        # Extract a simple cite key
        words = title.lower().split()[:3]
        cite_key = ''.join(w[:4] for w in words if len(w) > 2)
        cite_key = f"{cite_key}{datetime.now().year}"
        
        # Escape special characters
        title_escaped = title.replace('&', '\\&').replace('_', '\\_')
        
        entry = f"""@misc{{{cite_key},
  title = {{{title_escaped}}},
  year = {{{datetime.now().year}}},
  note = {{Missing metadata - needs manual review}}
}}"""
        
        manual_entries.append({
            'index': index,
            'entry': entry,
            'title': title
        })
        
        print(f"  ✓ Created placeholder entry: {cite_key}\n")
    
    # Show summary
    print(f"\n{'='*80}")
    print("Generated placeholder entries for failed publications")
    print("These need manual review to add proper year, authors, and venue")
    print(f"{'='*80}\n")
    
    for entry_data in manual_entries:
        print(f"[{entry_data['index']}] {entry_data['title'][:50]}...")
        print(entry_data['entry'])
        print()
    
    response = input(f"\nAdd {len(manual_entries)} placeholder entries to .bib? [Y/n]: ").strip().upper()
    
    if response != 'N':
        with open(bib_file, 'a', encoding='utf-8') as f:
            f.write("\n\n")
            f.write(f"% Placeholder entries added on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("% These need manual review to complete metadata\n\n")
            
            for entry_data in manual_entries:
                f.write(entry_data['entry'])
                f.write("\n\n")
        
        print(f"\n✅ Added {len(manual_entries)} placeholder entries")
        print("⚠️  Remember to manually update these entries with proper metadata!")
    else:
        print("\n⏸️  Skipped adding placeholders")


if __name__ == "__main__":
    retry_failed_publications()
