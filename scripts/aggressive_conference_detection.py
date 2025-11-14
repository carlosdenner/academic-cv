#!/usr/bin/env python3
"""
Aggressive Conference Paper Detection

This script converts ALL @article entries to @inproceedings UNLESS they have
clear journal indicators (DOI, volume, number, or recognized journal names).
"""

import re
from pathlib import Path


def is_likely_journal(entry_text):
    """Check if entry has clear journal indicators"""
    
    # Strong journal indicators
    journal_indicators = [
        r'doi\s*=\s*\{10\.',  # Has DOI starting with 10.
        r'volume\s*=\s*\{[0-9]+\}',  # Has volume number
        r'number\s*=\s*\{[0-9]+\}',  # Has issue number
        r'journal\s*=\s*\{[^}]*(?:Revista|Journal|Review|Transactions|Letters|Magazine)[^}]*\}',  # Has "journal" keyword in journal field
        r'journal\s*=\s*\{[^}]*(?:IEEE|ACM|Science|Nature|PLOS|BMC|Springer)[^}]*\}',  # Major publishers
    ]
    
    for indicator in journal_indicators:
        if re.search(indicator, entry_text, re.IGNORECASE):
            return True
    
    return False


def aggressive_conference_conversion():
    """Convert articles to inproceedings unless they have clear journal markers"""
    
    bib_file = Path('c:/academic-cv/data/latex/publications.bib')
    
    with open(bib_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    i = 0
    changes = []
    
    while i < len(lines):
        line = lines[i]
        
        # Check if this is an @article entry
        article_match = re.match(r'^@article\{([^,]+),', line)
        if article_match:
            cite_key = article_match.group(1)
            start_line = i
            
            # Read the entire entry
            entry_lines = [line]
            i += 1
            while i < len(lines) and not lines[i].strip() == '}':
                entry_lines.append(lines[i])
                i += 1
            if i < len(lines):
                entry_lines.append(lines[i])  # Include closing }
            
            entry_text = '\n'.join(entry_lines)
            
            # Check if this is likely a journal article
            if not is_likely_journal(entry_text):
                # Convert to conference paper
                new_entry = entry_text.replace('@article{', '@inproceedings{', 1)
                
                # Convert 'journal' field to 'booktitle'
                new_entry = re.sub(r'\n(\s+)journal\s*=', r'\n\1booktitle =', new_entry)
                
                changes.append({
                    'cite_key': cite_key,
                    'line': start_line + 1
                })
                
                # Replace in the lines list
                new_lines = new_entry.split('\n')
                lines[start_line:i+1] = new_lines
                i = start_line + len(new_lines) - 1
        
        i += 1
    
    if changes:
        # Write back
        new_content = '\n'.join(lines)
        
        with open(bib_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ Converted {len(changes)} articles to inproceedings (when in doubt, it's a conference):\n")
        for i, change in enumerate(changes[:30], 1):
            print(f"  {i}. [{change['cite_key']}] (line {change['line']})")
        
        if len(changes) > 30:
            print(f"\n  ... and {len(changes) - 30} more")
    else:
        print("No articles need conversion - all have clear journal indicators")


if __name__ == "__main__":
    aggressive_conference_conversion()
