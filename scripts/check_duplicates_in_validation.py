#!/usr/bin/env python3
"""
Check for Duplicates in Validation Decisions

This script compares the 51 publications marked for addition with existing
.bib entries to identify potential duplicates, including:
- Same paper in different languages (English vs Portuguese/Spanish)
- Different versions (preprint vs published, conference vs journal)
- Slight title variations
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple
from difflib import SequenceMatcher


class DuplicateChecker:
    def __init__(self, decisions_file: Path, bib_file: Path):
        self.decisions_file = decisions_file
        self.bib_file = bib_file
        self.load_data()
    
    def load_data(self):
        """Load validation decisions and existing bibliography"""
        with open(self.decisions_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Filter only publications marked to ADD
        self.to_add = [d for d in data['decisions'] if d['decision'] == 'A']
        
        # Parse BibTeX entries
        with open(self.bib_file, 'r', encoding='utf-8') as f:
            bib_content = f.read()
        
        self.bib_entries = self.parse_bibtex_entries(bib_content)
        
        print(f"Loaded {len(self.to_add)} publications to add")
        print(f"Loaded {len(self.bib_entries)} existing .bib entries")
    
    def parse_bibtex_entries(self, bib_content: str) -> List[Dict[str, str]]:
        """Parse BibTeX file and extract key metadata"""
        entries = []
        
        # Split by entry type (@article, @inproceedings, etc.)
        entry_pattern = re.compile(r'@(\w+)\{([^,]+),\s*(.*?)\n\}', re.DOTALL)
        
        for match in entry_pattern.finditer(bib_content):
            entry_type = match.group(1)
            entry_key = match.group(2)
            entry_body = match.group(3)
            
            # Extract fields
            fields = {}
            field_pattern = re.compile(r'(\w+)\s*=\s*[{"]([^}"]*)[\}"]', re.DOTALL)
            
            for field_match in field_pattern.finditer(entry_body):
                field_name = field_match.group(1).lower()
                field_value = field_match.group(2).strip()
                fields[field_name] = field_value
            
            entry = {
                'type': entry_type,
                'key': entry_key,
                'title': fields.get('title', ''),
                'author': fields.get('author', ''),
                'year': fields.get('year', ''),
                'doi': fields.get('doi', ''),
                'journal': fields.get('journal', ''),
                'booktitle': fields.get('booktitle', ''),
                'venue': fields.get('journal') or fields.get('booktitle', '')
            }
            
            entries.append(entry)
        
        return entries
    
    def normalize_text(self, text: str) -> str:
        """Normalize text for comparison"""
        if not text:
            return ""
        
        # Remove LaTeX commands
        text = re.sub(r'\\[a-z]+\s*', '', text)
        text = re.sub(r'[{}\\]', '', text)
        
        # Normalize unicode (NFKD)
        import unicodedata
        text = unicodedata.normalize('NFKD', text)
        
        # Convert to ASCII (removes accents)
        text = text.encode('ascii', 'ignore').decode('ascii')
        
        # Lowercase and remove punctuation
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def extract_keywords(self, text: str) -> set:
        """Extract significant keywords from text"""
        normalized = self.normalize_text(text)
        
        # Remove common stopwords
        stopwords = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'will', 'with', 'na', 'no', 'em', 'da', 'do', 'de',
            'dos', 'das', 'para', 'com', 'por', 'e', 'o', 'os', 'as', 'um',
            'uma', 'ao', 'aos', 'se', 'sobre', 'entre', 'study', 'analysis',
            'using', 'based', 'case', 'research', 'paper', 'article'
        }
        
        words = normalized.split()
        keywords = {w for w in words if len(w) > 3 and w not in stopwords}
        
        return keywords
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity ratio between two texts"""
        norm1 = self.normalize_text(text1)
        norm2 = self.normalize_text(text2)
        
        if not norm1 or not norm2:
            return 0.0
        
        return SequenceMatcher(None, norm1, norm2).ratio()
    
    def calculate_keyword_overlap(self, text1: str, text2: str) -> float:
        """Calculate Jaccard similarity of keywords"""
        kw1 = self.extract_keywords(text1)
        kw2 = self.extract_keywords(text2)
        
        if not kw1 or not kw2:
            return 0.0
        
        intersection = len(kw1 & kw2)
        union = len(kw1 | kw2)
        
        return intersection / union if union > 0 else 0.0
    
    def extract_author_surnames(self, author_string: str) -> set:
        """Extract surnames from author string"""
        if not author_string:
            return set()
        
        # Handle both BibTeX format (Last, F.) and plain format (F Last)
        surnames = set()
        
        # Split by 'and' or comma
        authors = re.split(r'\s+and\s+|,', author_string)
        
        for author in authors:
            author = author.strip()
            # Get first word (usually surname in BibTeX)
            words = author.split()
            if words:
                surname = self.normalize_text(words[0])
                if len(surname) > 2:
                    surnames.add(surname)
        
        return surnames
    
    def check_author_match(self, pub_authors: str, bib_entry: Dict) -> bool:
        """Check if there's significant author overlap"""
        if not pub_authors or not bib_entry.get('author'):
            return False
        
        pub_surnames = self.extract_author_surnames(pub_authors)
        bib_surnames = self.extract_author_surnames(bib_entry['author'])
        
        if not pub_surnames or not bib_surnames:
            return False
        
        # Check if Santos is in both (your name)
        santos_in_both = 'santos' in pub_surnames and 'santos' in bib_surnames
        
        # Check overlap
        overlap = len(pub_surnames & bib_surnames)
        
        return santos_in_both and overlap >= 1
    
    def find_potential_duplicates(self, pub: Dict, bib_entry: Dict) -> Dict:
        """Check if publication is a potential duplicate of bib entry"""
        # Extract publication metadata
        if pub['analysis']['source'] == 'both_sources':
            pub_title = pub['publication']['google_scholar']['title']
            pub_authors = pub['publication']['google_scholar'].get('authors', '')
            pub_year = pub['publication']['google_scholar'].get('year')
            pub_venue = pub['publication']['google_scholar'].get('venue', '')
        elif pub['analysis']['source'] == 'google_scholar':
            pub_title = pub['publication']['title']
            pub_authors = pub['publication'].get('authors', '')
            pub_year = pub['publication'].get('year')
            pub_venue = pub['publication'].get('venue', '')
        else:  # researchgate
            pub_title = pub['publication']['title']
            pub_authors = ''
            pub_year = pub['publication'].get('year')
            pub_venue = ''
        
        bib_title = bib_entry['title']
        bib_year = bib_entry['year']
        
        # Calculate similarities
        title_similarity = self.calculate_similarity(pub_title, bib_title)
        keyword_overlap = self.calculate_keyword_overlap(pub_title, bib_title)
        
        # Check various duplicate indicators
        indicators = {
            'title_similarity': title_similarity,
            'keyword_overlap': keyword_overlap,
            'same_year': pub_year == bib_year if pub_year and bib_year else False,
            'year_close': abs(int(pub_year or 0) - int(bib_year or 0)) <= 1 if pub_year and bib_year else False,
            'author_match': self.check_author_match(pub_authors, bib_entry)
        }
        
        # Determine if it's a likely duplicate
        # More sensitive thresholds to catch translations and variations
        # Don't rely heavily on year matching since some years are incorrect
        is_likely_duplicate = (
            (title_similarity >= 0.80) or
            (title_similarity >= 0.65 and indicators['author_match']) or
            (keyword_overlap >= 0.65 and indicators['author_match']) or
            (title_similarity >= 0.55 and keyword_overlap >= 0.55) or
            (keyword_overlap >= 0.75)  # High keyword overlap even without exact title match
        )
        
        return {
            'is_duplicate': is_likely_duplicate,
            'confidence': max(title_similarity, keyword_overlap),
            'indicators': indicators,
            'bib_entry': bib_entry
        }
    
    def analyze_all(self):
        """Analyze all publications marked for addition"""
        results = []
        
        print("\n" + "="*80)
        print("DUPLICATE CHECK ANALYSIS")
        print("="*80)
        
        for i, pub_decision in enumerate(self.to_add, 1):
            pub = pub_decision['publication']
            analysis = pub_decision['analysis']
            
            # Get publication title
            if analysis['source'] == 'both_sources':
                pub_title = pub['google_scholar']['title']
                pub_year = pub['google_scholar'].get('year')
                pub_authors = pub['google_scholar'].get('authors', '')
            elif analysis['source'] == 'google_scholar':
                pub_title = pub['title']
                pub_year = pub.get('year')
                pub_authors = pub.get('authors', '')
            else:  # researchgate
                pub_title = pub['title']
                pub_year = pub.get('year')
                pub_authors = ''
            
            # Find best matches in existing bib
            matches = []
            for bib_entry in self.bib_entries:
                match_result = self.find_potential_duplicates(pub_decision, bib_entry)
                if match_result['confidence'] >= 0.5:  # Only consider matches above 50%
                    matches.append(match_result)
            
            # Sort by confidence
            matches.sort(key=lambda x: x['confidence'], reverse=True)
            
            result = {
                'index': i,
                'publication': {
                    'title': pub_title,
                    'year': pub_year,
                    'authors': pub_authors,
                    'source': analysis['source']
                },
                'matches': matches[:3],  # Top 3 matches
                'has_likely_duplicate': any(m['is_duplicate'] for m in matches)
            }
            
            results.append(result)
        
        return results
    
    def display_results(self, results: List[Dict]):
        """Display analysis results interactively"""
        likely_duplicates = [r for r in results if r['has_likely_duplicate']]
        
        # Also show high-similarity matches that didn't meet duplicate threshold
        high_similarity = [r for r in results 
                          if not r['has_likely_duplicate'] 
                          and r['matches'] 
                          and r['matches'][0]['confidence'] >= 0.60]
        
        no_duplicates = [r for r in results 
                        if not r['has_likely_duplicate'] 
                        and (not r['matches'] or r['matches'][0]['confidence'] < 0.60)]
        
        print(f"\n{'='*80}")
        print(f"SUMMARY")
        print(f"{'='*80}")
        print(f"Total publications to add: {len(results)}")
        print(f"✓ Definitely NEW (low similarity): {len(no_duplicates)}")
        print(f"⚠️  HIGH SIMILARITY (manual review needed): {len(high_similarity)}")
        print(f"⛔ LIKELY DUPLICATES: {len(likely_duplicates)}")
        print(f"{'='*80}\n")
        
        if likely_duplicates:
            print(f"\n{'#'*80}")
            print(f"# LIKELY DUPLICATES - SHOULD SKIP")
            print(f"{'#'*80}\n")
            
            for result in likely_duplicates:
                pub = result['publication']
                print(f"\n{'-'*80}")
                print(f"[{result['index']}/{len(results)}] CANDIDATE:")
                print(f"  Title: {pub['title'][:80]}...")
                print(f"  Year: {pub['year']}")
                print(f"  Authors: {pub['authors'][:60]}..." if pub['authors'] else "  Authors: N/A")
                print(f"  Source: {pub['source']}")
                
                print(f"\n  ⚠️  POTENTIAL MATCHES IN EXISTING .BIB:")
                
                for j, match in enumerate(result['matches'], 1):
                    if match['is_duplicate']:
                        bib = match['bib_entry']
                        ind = match['indicators']
                        
                        print(f"\n  Match {j}: [{bib['key']}]")
                        print(f"    Title: {bib['title'][:70]}...")
                        print(f"    Year: {bib['year']}")
                        print(f"    Type: @{bib['type']}")
                        print(f"    Confidence: {match['confidence']:.2%}")
                        print(f"    → Title similarity: {ind['title_similarity']:.2%}")
                        print(f"    → Keyword overlap: {ind['keyword_overlap']:.2%}")
                        print(f"    → Same year: {ind['same_year']}")
                        print(f"    → Author match: {ind['author_match']}")
        
        if high_similarity:
            print(f"\n{'#'*80}")
            print(f"# HIGH SIMILARITY - MANUAL REVIEW NEEDED")
            print(f"# (60%+ similarity but not flagged as duplicate)")
            print(f"{'#'*80}\n")
            
            for result in high_similarity:
                pub = result['publication']
                closest = result['matches'][0]
                bib = closest['bib_entry']
                
                print(f"\n{'-'*80}")
                print(f"[{result['index']}/{len(results)}]")
                print(f"CANDIDATE: {pub['title'][:70]}... ({pub['year']})")
                print(f"  Authors: {pub['authors'][:60]}..." if pub['authors'] else "  Authors: N/A")
                print(f"\nCLOSEST MATCH: [{bib['key']}] {bib['title'][:70]}... ({bib['year']})")
                print(f"  Similarity: {closest['confidence']:.1%}")
                print(f"  Title match: {closest['indicators']['title_similarity']:.1%}")
                print(f"  Keyword match: {closest['indicators']['keyword_overlap']:.1%}")
                print(f"  Author match: {closest['indicators']['author_match']}")
        
        if no_duplicates:
            print(f"\n{'#'*80}")
            print(f"# CONFIRMED NEW PUBLICATIONS (Low similarity to existing)")
            print(f"{'#'*80}\n")
            
            for result in no_duplicates:
                pub = result['publication']
                similarity = result['matches'][0]['confidence'] if result['matches'] else 0
                print(f"[{result['index']}] {pub['title'][:70]}... ({pub['year']}) [{similarity:.0%}]")
        
        return likely_duplicates, high_similarity, no_duplicates
    
    def save_report(self, results: List[Dict], likely_duplicates: List[Dict], no_duplicates: List[Dict]):
        """Save detailed report to JSON"""
        output_file = Path('c:/academic-cv/data/processed/duplicate_check_report.json')
        
        report = {
            'generated_at': self.decisions_file.stat().st_mtime,
            'summary': {
                'total_to_add': len(results),
                'likely_new': len(no_duplicates),
                'potential_duplicates': len(likely_duplicates)
            },
            'likely_duplicates': likely_duplicates,
            'confirmed_new': no_duplicates
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Detailed report saved to: {output_file}")


def main():
    decisions_file = Path('c:/academic-cv/data/processed/validation_decisions.json')
    bib_file = Path('c:/academic-cv/data/latex/publications.bib')
    
    if not decisions_file.exists():
        print(f"❌ Error: Validation decisions file not found: {decisions_file}")
        return
    
    if not bib_file.exists():
        print(f"❌ Error: Bibliography file not found: {bib_file}")
        return
    
    checker = DuplicateChecker(decisions_file, bib_file)
    results = checker.analyze_all()
    likely_duplicates, high_similarity, no_duplicates = checker.display_results(results)
    checker.save_report(results, likely_duplicates, no_duplicates)
    
    print(f"\n{'='*80}")
    print("NEXT STEPS:")
    print("="*80)
    print(f"1. Review the {len(likely_duplicates)} potential duplicates above")
    print(f"2. Decide which ones are truly new vs already in .bib")
    print(f"3. The {len(no_duplicates)} confirmed new publications can be added directly")
    print("="*80)


if __name__ == "__main__":
    main()
