#!/usr/bin/env python3
"""
Add Validated Publications to .bib

This script:
1. Loads publications marked for addition (excluding known duplicates)
2. Searches OpenAlex for each publication to get proper metadata
3. Generates correct BibTeX entries with proper types and fields
4. Appends to publications.bib
"""

import json
import requests
import time
import re
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


class PublicationAdder:
    def __init__(self, decisions_file: Path, duplicate_report: Path, bib_file: Path):
        self.decisions_file = decisions_file
        self.duplicate_report = duplicate_report
        self.bib_file = bib_file
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'mailto:your@email.com Academic CV Builder'
        })
        
    def load_publications_to_add(self) -> List[Dict]:
        """Load publications, excluding duplicates"""
        # Load validation decisions
        with open(self.decisions_file, 'r', encoding='utf-8') as f:
            decisions = json.load(f)
        
        # Load duplicate report
        with open(self.duplicate_report, 'r', encoding='utf-8') as f:
            dup_report = json.load(f)
        
        # Get indices to skip (duplicates)
        skip_indices = {41, 45}  # [41] and [45] are duplicates
        
        # Filter publications
        to_add = []
        for i, decision in enumerate(decisions['decisions'], 1):
            if decision['decision'] == 'A' and i not in skip_indices:
                to_add.append({
                    'index': i,
                    'decision': decision
                })
        
        print(f"Loaded {len(to_add)} publications to add (excluded 2 duplicates)")
        return to_add
    
    def extract_publication_info(self, pub_data: Dict) -> Dict:
        """Extract title, authors, year from publication data"""
        analysis = pub_data['decision']['analysis']
        pub = pub_data['decision']['publication']
        
        if analysis['source'] == 'both_sources':
            gs = pub['google_scholar']
            return {
                'title': gs['title'],
                'authors': gs.get('authors', ''),
                'year': str(gs.get('year', '')),
                'venue': gs.get('venue', ''),
                'citations': gs.get('citations', 0),
                'url': gs.get('url', '')
            }
        elif analysis['source'] == 'google_scholar':
            return {
                'title': pub['title'],
                'authors': pub.get('authors', ''),
                'year': str(pub.get('year', '')),
                'venue': pub.get('venue', ''),
                'citations': pub.get('citations', 0),
                'url': pub.get('url', '')
            }
        else:  # researchgate
            return {
                'title': pub['title'],
                'authors': '',
                'year': str(pub.get('year', '')),
                'venue': '',
                'citations': 0,
                'url': pub.get('url', '')
            }
    
    def search_openalex(self, title: str, year: Optional[str] = None) -> Optional[Dict]:
        """Search OpenAlex for work by title"""
        # Clean title for search
        search_title = re.sub(r'[^\w\s]', ' ', title)
        search_title = re.sub(r'\s+', ' ', search_title).strip()
        
        # Build query
        query = f'title.search:"{search_title}"'
        if year and year.isdigit() and 1990 <= int(year) <= 2025:
            # Allow +/- 1 year for flexibility
            year_int = int(year)
            query += f',publication_year:{year_int-1}|{year_int}|{year_int+1}'
        
        url = 'https://api.openalex.org/works'
        params = {
            'filter': query,
            'per_page': 5,
            'select': 'id,doi,title,publication_year,type,primary_location,authorships,biblio'
        }
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data['results']:
                return data['results'][0]  # Return best match
            
        except Exception as e:
            print(f"  ⚠️  OpenAlex search failed: {e}")
        
        return None
    
    def generate_cite_key(self, authors: str, year: str, title: str) -> str:
        """Generate BibTeX citation key"""
        # Extract first author surname
        if authors:
            # Handle various author formats
            first_author = authors.split(',')[0].split(' and ')[0].strip()
            # Get last word (usually surname)
            surname = first_author.split()[-1].lower()
            surname = re.sub(r'[^\w]', '', surname)
        else:
            # Use first word of title
            surname = title.split()[0].lower()[:6]
            surname = re.sub(r'[^\w]', '', surname)
        
        # Get year (use first 4 digits)
        year_str = re.search(r'\d{4}', year)
        year_str = year_str.group() if year_str else '0000'
        
        # Get first significant word from title (not stopword)
        stopwords = {'a', 'an', 'the', 'of', 'in', 'on', 'at', 'to', 'for', 'and', 'or'}
        title_words = re.findall(r'\w+', title.lower())
        title_word = next((w[:4] for w in title_words if w not in stopwords and len(w) > 3), 'work')
        
        return f"{surname}{year_str}{title_word}"
    
    def escape_latex(self, text: str) -> str:
        """Escape special characters for LaTeX"""
        if not text:
            return ""
        
        # Escape special characters
        text = text.replace('&', '\\&')
        text = text.replace('%', '\\%')
        text = text.replace('$', '\\$')
        text = text.replace('#', '\\#')
        text = text.replace('_', '\\_')
        
        # Handle accented characters (basic ones)
        accents = {
            'á': "{\\'a}", 'à': "{\\`a}", 'â': "{\\^a}", 'ã': "{\\~a}",
            'é': "{\\'e}", 'è': "{\\`e}", 'ê': "{\\^e}",
            'í': "{\\'i}", 'ì': "{\\`i}", 'î': "{\\^i}",
            'ó': "{\\'o}", 'ò': "{\\`o}", 'ô': "{\\^o}", 'õ': "{\\~o}",
            'ú': "{\\'u}", 'ù': "{\\`u}", 'û': "{\\^u}",
            'ç': "{\\c c}",
            'Á': "{\\'A}", 'À': "{\\`A}", 'Â': "{\\^A}", 'Ã': "{\\~A}",
            'É': "{\\'E}", 'È': "{\\`E}", 'Ê': "{\\^E}",
            'Í': "{\\'I}", 'Ì': "{\\`I}", 'Î': "{\\^I}",
            'Ó': "{\\'O}", 'Ò': "{\\`O}", 'Ô': "{\\^O}", 'Õ': "{\\~O}",
            'Ú': "{\\'U}", 'Ù': "{\\`U}", 'Û': "{\\^U}",
            'Ç': "{\\c C}",
        }
        
        for char, latex in accents.items():
            text = text.replace(char, latex)
        
        return text
    
    def format_authors_bibtex(self, authors: str) -> str:
        """Format authors for BibTeX"""
        if not authors:
            return ""
        
        # Split by 'and' or comma
        author_list = re.split(r'\s+and\s+|,\s*(?=[A-Z])', authors)
        
        formatted = []
        for author in author_list:
            author = author.strip()
            if not author:
                continue
            
            # If already in "Last, First" format, keep it
            if ',' in author:
                formatted.append(author)
            else:
                # Try to convert "First Last" to "Last, First"
                parts = author.split()
                if len(parts) >= 2:
                    last = parts[-1]
                    first = ' '.join(parts[:-1])
                    formatted.append(f"{last}, {first}")
                else:
                    formatted.append(author)
        
        return ' and '.join(formatted)
    
    def determine_entry_type(self, openalex_data: Optional[Dict], venue: str, title: str) -> str:
        """Determine BibTeX entry type"""
        if openalex_data:
            oa_type = openalex_data.get('type', '')
            
            # Map OpenAlex types to BibTeX types
            type_map = {
                'article': 'article',
                'book-chapter': 'incollection',
                'proceedings-article': 'inproceedings',
                'dataset': 'misc',
                'preprint': 'article',  # Treat preprints as articles
                'book': 'book',
                'dissertation': 'phdthesis'
            }
            
            if oa_type in type_map:
                return type_map[oa_type]
        
        # Heuristics based on venue
        venue_lower = venue.lower() if venue else ''
        title_lower = title.lower() if title else ''
        
        if any(x in venue_lower for x in ['conference', 'proceedings', 'congress', 'workshop', 'symposium']):
            return 'inproceedings'
        elif any(x in title_lower for x in ['capítulo', 'chapter']):
            return 'incollection'
        elif 'dataset' in title_lower:
            return 'misc'
        
        # Default to article
        return 'article'
    
    def generate_bibtex_entry(self, pub_info: Dict, openalex_data: Optional[Dict]) -> str:
        """Generate BibTeX entry"""
        title = pub_info['title']
        authors = pub_info['authors']
        year = pub_info['year']
        
        # Validate year
        if not year or not year.isdigit() or int(year) < 1990 or int(year) > 2025:
            # Try to get from OpenAlex
            if openalex_data:
                year = str(openalex_data.get('publication_year', ''))
            
            # If still invalid, use current year
            if not year or not year.isdigit() or int(year) < 1990:
                year = str(datetime.now().year)
        
        # Generate citation key
        cite_key = self.generate_cite_key(authors, year, title)
        
        # Determine entry type
        entry_type = self.determine_entry_type(openalex_data, pub_info['venue'], title)
        
        # Extract metadata
        if openalex_data:
            doi = openalex_data.get('doi', '')
            if doi:
                doi = doi.replace('https://doi.org/', '')
            
            # Get venue from primary_location
            location = openalex_data.get('primary_location', {}) or {}
            source = location.get('source', {}) or {}
            venue = source.get('display_name', pub_info['venue'])
            
            # Get biblio metadata
            biblio = openalex_data.get('biblio', {}) or {}
            volume = biblio.get('volume', '')
            issue = biblio.get('issue', '')
            pages = biblio.get('first_page', '')
            if pages and biblio.get('last_page'):
                pages += f"--{biblio.get('last_page')}"
            
            # Get authors from OpenAlex (better format)
            authorships = openalex_data.get('authorships', []) or []
            if authorships:
                oa_authors = []
                for auth in authorships:
                    author = auth.get('author', {}) or {}
                    name = author.get('display_name', '')
                    if name:
                        oa_authors.append(name)
                if oa_authors:
                    authors = ', '.join(oa_authors)
        else:
            doi = ''
            venue = pub_info['venue']
            volume = ''
            issue = ''
            pages = ''
        
        # Format authors
        authors_bibtex = self.format_authors_bibtex(authors)
        
        # Escape LaTeX special characters
        title_escaped = self.escape_latex(title)
        venue_escaped = self.escape_latex(venue)
        
        # Build entry
        entry_lines = [f"@{entry_type}{{{cite_key},"]
        
        if authors_bibtex:
            entry_lines.append(f"  author = {{{authors_bibtex}}},")
        
        entry_lines.append(f"  title = {{{title_escaped}}},")
        entry_lines.append(f"  year = {{{year}}},")
        
        if entry_type == 'article' and venue:
            entry_lines.append(f"  journal = {{{venue_escaped}}},")
        elif entry_type in ['inproceedings', 'incollection'] and venue:
            entry_lines.append(f"  booktitle = {{{venue_escaped}}},")
        
        if volume:
            entry_lines.append(f"  volume = {{{volume}}},")
        if issue:
            entry_lines.append(f"  number = {{{issue}}},")
        if pages:
            entry_lines.append(f"  pages = {{{pages}}},")
        if doi:
            entry_lines.append(f"  doi = {{{doi}}},")
        
        entry_lines.append("}")
        
        return '\n'.join(entry_lines)
    
    def process_publications(self):
        """Process all publications and generate BibTeX entries"""
        publications = self.load_publications_to_add()
        
        print(f"\n{'='*80}")
        print("PROCESSING PUBLICATIONS")
        print(f"{'='*80}\n")
        
        new_entries = []
        failed = []
        
        for i, pub_data in enumerate(publications, 1):
            index = pub_data['index']
            pub_info = self.extract_publication_info(pub_data)
            
            print(f"[{i}/{len(publications)}] #{index}: {pub_info['title'][:60]}...")
            
            # Search OpenAlex
            openalex_data = self.search_openalex(pub_info['title'], pub_info['year'])
            
            if openalex_data:
                print(f"  ✓ Found in OpenAlex: {openalex_data.get('doi', 'no DOI')}")
            else:
                print(f"  ⚠️  Not found in OpenAlex, using metadata from source")
            
            # Generate BibTeX entry
            try:
                entry = self.generate_bibtex_entry(pub_info, openalex_data)
                new_entries.append({
                    'index': index,
                    'entry': entry,
                    'title': pub_info['title']
                })
                print(f"  ✓ Generated BibTeX entry")
            except Exception as e:
                print(f"  ❌ Failed: {e}")
                failed.append({'index': index, 'title': pub_info['title'], 'error': str(e)})
            
            # Rate limiting
            time.sleep(0.2)
            
            print()
        
        return new_entries, failed
    
    def append_to_bib(self, entries: List[Dict]):
        """Append new entries to .bib file"""
        if not entries:
            print("No entries to add!")
            return
        
        # Read existing bib
        with open(self.bib_file, 'r', encoding='utf-8') as f:
            existing_content = f.read()
        
        # Append new entries
        with open(self.bib_file, 'a', encoding='utf-8') as f:
            f.write("\n\n")
            f.write(f"% Added on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("% Validated publications from ResearchGate and Google Scholar\n\n")
            
            for entry_data in entries:
                f.write(entry_data['entry'])
                f.write("\n\n")
        
        print(f"✅ Added {len(entries)} new entries to {self.bib_file}")
    
    def save_report(self, new_entries: List[Dict], failed: List[Dict]):
        """Save processing report"""
        report = {
            'generated_at': datetime.now().isoformat(),
            'total_processed': len(new_entries) + len(failed),
            'successful': len(new_entries),
            'failed': len(failed),
            'entries': new_entries,
            'failed_items': failed
        }
        
        output_file = Path('c:/academic-cv/data/processed/add_publications_report.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Report saved to: {output_file}")


def main():
    decisions_file = Path('c:/academic-cv/data/processed/validation_decisions.json')
    duplicate_report = Path('c:/academic-cv/data/processed/duplicate_check_report.json')
    bib_file = Path('c:/academic-cv/data/latex/publications.bib')
    
    adder = PublicationAdder(decisions_file, duplicate_report, bib_file)
    new_entries, failed = adder.process_publications()
    
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    print(f"✓ Successfully processed: {len(new_entries)}")
    print(f"❌ Failed: {len(failed)}")
    
    if failed:
        print("\nFailed items:")
        for item in failed:
            print(f"  #{item['index']}: {item['title'][:50]}... - {item['error']}")
    
    print(f"{'='*80}\n")
    
    # Ask for confirmation
    if new_entries:
        response = input(f"Add {len(new_entries)} entries to publications.bib? [Y/n]: ").strip().upper()
        
        if response != 'N':
            adder.append_to_bib(new_entries)
            adder.save_report(new_entries, failed)
            print("\n✅ Done! Publications added to .bib file")
        else:
            print("\n⏸️  Cancelled. No changes made to .bib file")
            adder.save_report(new_entries, failed)


if __name__ == "__main__":
    main()
