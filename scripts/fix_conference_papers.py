#!/usr/bin/env python3
"""
Fix Conference Papers Misclassified as Articles

This script identifies and converts @article entries that are actually conference papers
to @inproceedings based on their journal/booktitle fields.
"""

import re
from pathlib import Path


def fix_conference_papers():
    """Convert articles that are actually conference papers to inproceedings"""
    
    bib_file = Path('c:/academic-cv/data/latex/publications.bib')
    
    with open(bib_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Patterns indicating a conference paper
    conference_indicators = [
        'AMCIS',
        'Americas Conference on Information Systems',
        'ICIS',
        'Annual Hawaii International Conference on System Sciences',
        'HICSS',
        'Proceedings of',
        'Workshop',
        'Conference',
        'Congresso',
        'CATI',
    ]
    
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
            
            # Check if this entry contains conference indicators
            is_conference = False
            found_indicator = None
            for indicator in conference_indicators:
                if indicator in entry_text:
                    is_conference = True
                    found_indicator = indicator
                    break
            
            if is_conference:
                # Convert @article to @inproceedings
                new_entry = entry_text.replace('@article{', '@inproceedings{', 1)
                
                # Also convert 'journal' field to 'booktitle' if present
                new_entry = re.sub(r'\n(\s+)journal\s*=', r'\n\1booktitle =', new_entry)
                
                changes.append({
                    'cite_key': cite_key,
                    'indicator': found_indicator,
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
        
        print(f"✅ Converted {len(changes)} articles to inproceedings:\n")
        for change in changes:
            print(f"  [{change['cite_key']}] (line {change['line']}) - Found: {change['indicator']}")
    else:
        print("No conference papers found misclassified as articles")


if __name__ == "__main__":
    fix_conference_papers()
