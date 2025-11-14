#!/usr/bin/env python3
"""
Remove True Duplicate Entries from publications.bib

This script removes entries that are actual duplicates (same paper, same content),
but keeps different language versions of the same paper.
"""

from pathlib import Path
import re


def remove_duplicates():
    """Remove true duplicate entries from publications.bib"""
    
    bib_file = Path('c:/academic-cv/data/latex/publications.bib')
    
    with open(bib_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # These are TRUE duplicates (same paper, same language, same DOI)
    # We'll remove the ones with "2" suffix since we want to keep the first occurrence
    true_duplicates = [
        'jr2009open2',        # PhD dissertation - exact duplicate
        'jr2011inex2',        # Inextricable Role paper - exact duplicate
        'barbalho2019capí2',  # Book chapter - exact duplicate
        'franco2013adoç2',    # Security practices paper - same DOI
    ]
    
    # These are DIFFERENT language versions - KEEP BOTH
    # santos2017estu (Spanish) vs santos2017estu2 (Portuguese)
    # oliveira2019cons (Spanish) vs oliveira2019cons2 (Portuguese)
    
    lines = content.split('\n')
    
    # Find and remove entries for true duplicates
    i = 0
    removed_count = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Check if this line starts an entry we want to remove
        for dup_key in true_duplicates:
            if re.match(rf'^@\w+\{{{re.escape(dup_key)},', line):
                # Found a duplicate to remove
                print(f"Removing duplicate: {dup_key}")
                
                # Remove lines until we hit the closing brace
                start_i = i
                while i < len(lines):
                    if lines[i].strip() == '}':
                        i += 1  # Include the closing brace
                        # Also remove following blank line if present
                        if i < len(lines) and lines[i].strip() == '':
                            i += 1
                        break
                    i += 1
                
                # Remove the entry
                del lines[start_i:i]
                i = start_i  # Reset to check same position again
                removed_count += 1
                break
        else:
            i += 1
    
    # Write back
    new_content = '\n'.join(lines)
    
    with open(bib_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"\n✅ Removed {removed_count} true duplicate entries")
    print("\n✓ Kept both language versions:")
    print("  - santos2017estu (Spanish) and santos2017estu2 (Portuguese)")
    print("  - oliveira2019cons (Spanish) and oliveira2019cons2 (Portuguese)")
    
    # Count remaining entries
    remaining = len(re.findall(r'^@\w+\{', new_content, re.MULTILINE))
    print(f"\n📊 Total entries now: {remaining} (was 105)")


if __name__ == "__main__":
    remove_duplicates()
