#!/usr/bin/env python3
"""
Fix Duplicate Keys in publications.bib

This script finds duplicate citation keys and renames the second occurrence
by adding a numeric suffix.
"""

import re
from pathlib import Path
from collections import defaultdict


def fix_duplicate_keys(bib_file: Path):
    """Find and fix duplicate citation keys"""
    
    # Read the file
    with open(bib_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find all citation keys and their line numbers
    key_pattern = re.compile(r'^@(\w+)\{([^,]+),')
    keys_found = defaultdict(list)
    
    for i, line in enumerate(lines):
        match = key_pattern.match(line)
        if match:
            entry_type = match.group(1)
            key = match.group(2)
            keys_found[key].append((i, entry_type, line))
    
    # Find duplicates
    duplicates = {k: v for k, v in keys_found.items() if len(v) > 1}
    
    if not duplicates:
        print("No duplicates found!")
        return
    
    print(f"Found {len(duplicates)} duplicate keys:")
    for key, occurrences in duplicates.items():
        print(f"  - {key}: {len(occurrences)} occurrences")
    
    # Fix duplicates by renaming second+ occurrences
    fixed_count = 0
    for key, occurrences in duplicates.items():
        # Keep first occurrence, rename others
        for idx, (line_num, entry_type, original_line) in enumerate(occurrences[1:], start=2):
            new_key = f"{key}{idx}"
            new_line = original_line.replace(f"{{{key},", f"{{{new_key},")
            lines[line_num] = new_line
            fixed_count += 1
            print(f"  Line {line_num + 1}: {key} → {new_key}")
    
    # Write back
    with open(bib_file, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f"\n✅ Fixed {fixed_count} duplicate keys")


def main():
    bib_file = Path('c:/academic-cv/data/latex/publications.bib')
    
    if not bib_file.exists():
        print(f"❌ File not found: {bib_file}")
        return
    
    fix_duplicate_keys(bib_file)


if __name__ == "__main__":
    main()
