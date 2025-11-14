#!/usr/bin/env python3
"""
Interactive Validation Script for Missing Publications

This script helps validate potentially missing publications by:
1. Showing detailed information about each candidate
2. Comparing with closest match in existing bibliography
3. Allowing interactive decision: ADD, SKIP, or DEFER
4. Saving decisions for batch processing later
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import re


class MissingPublicationValidator:
    def __init__(self, missing_file: Path, bib_file: Path):
        self.missing_file = missing_file
        self.bib_file = bib_file
        self.decisions = []
        self.load_data()
    
    def load_data(self):
        """Load missing publications and existing bibliography"""
        with open(self.missing_file, 'r', encoding='utf-8') as f:
            self.missing_data = json.load(f)
        
        # Parse BibTeX to get existing titles
        with open(self.bib_file, 'r', encoding='utf-8') as f:
            bib_content = f.read()
        
        self.existing_titles = self.parse_bibtex_titles(bib_content)
        
    def parse_bibtex_titles(self, bib_content: str) -> List[str]:
        """Extract titles from BibTeX file"""
        titles = []
        title_pattern = re.compile(r'title\s*=\s*[{"](.*?)[}"],', re.DOTALL | re.IGNORECASE)
        for match in title_pattern.finditer(bib_content):
            title = match.group(1).strip()
            # Clean up LaTeX commands
            title = re.sub(r'\\[a-z]+\s*', '', title)
            title = re.sub(r'[{}]', '', title)
            titles.append(title)
        return titles
    
    def normalize_title(self, title: str) -> str:
        """Normalize title for comparison"""
        if not title:
            return ""
        # Remove special characters, convert to lowercase
        normalized = title.lower()
        normalized = re.sub(r'[^\w\s]', '', normalized)
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        return normalized
    
    def show_publication(self, pub: Dict[str, Any], index: int, total: int, source_type: str):
        """Display publication details"""
        print("\n" + "="*80)
        print(f"CANDIDATE {index}/{total} - Source: {source_type.upper()}")
        print("="*80)
        
        if source_type == "researchgate":
            print(f"\nTitle: {pub.get('title', 'N/A')}")
            print(f"Year: {pub.get('year', 'Unknown')}")
            print(f"URL: {pub.get('url', 'N/A')}")
        elif source_type == "google_scholar":
            print(f"\nTitle: {pub.get('title', 'N/A')}")
            print(f"Authors: {pub.get('authors', 'N/A')}")
            print(f"Venue: {pub.get('venue', 'N/A')}")
            print(f"Year: {pub.get('year', 'Unknown')}")
            print(f"Citations: {pub.get('citations', 0)}")
            print(f"URL: {pub.get('url', 'N/A')}")
        elif source_type == "both_sources":
            # Show both ResearchGate and Google Scholar info
            rg = pub.get('researchgate', {})
            gs = pub.get('google_scholar', {})
            print(f"\n[ResearchGate]")
            print(f"Title: {rg.get('title', 'N/A')}")
            print(f"Year: {rg.get('year', 'Unknown')}")
            print(f"\n[Google Scholar]")
            print(f"Title: {gs.get('title', 'N/A')}")
            print(f"Authors: {gs.get('authors', 'N/A')}")
            print(f"Venue: {gs.get('venue', 'N/A')}")
            print(f"Year: {gs.get('year', 'Unknown')}")
            print(f"Citations: {gs.get('citations', 0)}")
        
        # Show closest match in existing bib
        closest = pub.get('closest_in_bib') or pub.get('researchgate', {}).get('closest_in_bib')
        match_score = pub.get('match_score') or pub.get('researchgate', {}).get('match_score', 0)
        
        print(f"\n{'-'*80}")
        print(f"CLOSEST MATCH IN BIB (score: {match_score:.3f}):")
        print(f"  → {closest}")
        print(f"{'-'*80}")
    
    def analyze_publication(self, pub: Dict[str, Any], source_type: str) -> Dict[str, Any]:
        """Analyze a publication and provide context for decision"""
        analysis = {
            'source': source_type,
            'title': '',
            'year': None,
            'red_flags': [],
            'green_flags': [],
            'similarity_score': 0
        }
        
        if source_type == "both_sources":
            rg = pub.get('researchgate', {})
            gs = pub.get('google_scholar', {})
            analysis['title'] = gs.get('title', rg.get('title', ''))
            analysis['year'] = gs.get('year') or rg.get('year')
            analysis['citations'] = gs.get('citations', 0)
            analysis['similarity_score'] = gs.get('match_score', 0)
            
            # Present on both sources is a green flag
            analysis['green_flags'].append("Present on BOTH ResearchGate and Google Scholar")
            
        elif source_type == "google_scholar":
            analysis['title'] = pub.get('title', '')
            analysis['year'] = pub.get('year')
            analysis['citations'] = pub.get('citations', 0)
            analysis['similarity_score'] = pub.get('match_score', 0)
            
            if analysis['citations'] >= 10:
                analysis['green_flags'].append(f"Well-cited ({analysis['citations']} citations)")
            elif analysis['citations'] >= 5:
                analysis['green_flags'].append(f"Some citations ({analysis['citations']})")
                
        else:  # researchgate
            analysis['title'] = pub.get('title', '')
            analysis['year'] = pub.get('year')
            analysis['similarity_score'] = pub.get('match_score', 0)
        
        # Check for red flags
        normalized_title = self.normalize_title(analysis['title'])
        
        # Very long titles might be metadata errors
        if len(analysis['title']) > 200:
            analysis['red_flags'].append("Unusually long title (might be metadata error)")
        
        # Check for other people's work (common names in health/medical fields)
        suspicious_keywords = [
            'pig carcass', 'meat science', 'diabetes mellitus', 'rabies', 'murciélago',
            'HIV', 'hepatitis', 'antimicrobial', 'aspergillus', 'fungal', 'mycological',
            'wine', 'vinho', 'oenological', 'viticulture', 'vitis vinifera',
            'geotechnical', 'centrifuge', 'health', 'salud pública', 'psychological'
        ]
        
        for keyword in suspicious_keywords:
            if keyword in normalized_title:
                analysis['red_flags'].append(f"Suspicious keyword: '{keyword}' (likely different author)")
                break
        
        # Check year validity
        if analysis['year']:
            if analysis['year'] < 1990 or analysis['year'] > 2025:
                analysis['red_flags'].append(f"Suspicious year: {analysis['year']}")
        
        # Low similarity score
        if analysis['similarity_score'] < 0.5:
            analysis['green_flags'].append("Very different from existing publications (likely new work)")
        
        return analysis
    
    def get_user_decision(self, pub: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        """Get user decision on whether to add this publication"""
        print(f"\nANALYSIS:")
        
        if analysis['red_flags']:
            print(f"\n⚠️  RED FLAGS:")
            for flag in analysis['red_flags']:
                print(f"   • {flag}")
        
        if analysis['green_flags']:
            print(f"\n✓ GREEN FLAGS:")
            for flag in analysis['green_flags']:
                print(f"   • {flag}")
        
        print(f"\n{'='*80}")
        print("DECISION OPTIONS:")
        print("  [A] ADD - This is my work and should be added to bibliography")
        print("  [S] SKIP - This is NOT my work (different author with same name)")
        print("  [D] DEFER - Unsure, will decide later")
        print("  [Q] QUIT - Save decisions and exit")
        print("="*80)
        
        while True:
            choice = input("\nYour decision [A/S/D/Q]: ").strip().upper()
            if choice in ['A', 'S', 'D', 'Q']:
                return choice
            print("Invalid choice. Please enter A, S, D, or Q.")
    
    def validate_category(self, category: str, publications: List[Dict[str, Any]]):
        """Validate all publications in a category"""
        total = len(publications)
        print(f"\n\n{'#'*80}")
        print(f"# VALIDATING: {category.upper()}")
        print(f"# Total candidates: {total}")
        print(f"{'#'*80}")
        
        for i, pub in enumerate(publications, 1):
            self.show_publication(pub, i, total, category)
            analysis = self.analyze_publication(pub, category)
            
            decision = self.get_user_decision(pub, analysis)
            
            if decision == 'Q':
                print("\n⏸️  Validation paused. Saving decisions...")
                return False
            
            # Record decision
            self.decisions.append({
                'category': category,
                'publication': pub,
                'analysis': analysis,
                'decision': decision,
                'timestamp': datetime.now().isoformat()
            })
            
            if decision == 'A':
                print("✅ Marked for ADDITION")
            elif decision == 'S':
                print("❌ SKIPPED (not your work)")
            elif decision == 'D':
                print("⏭️  DEFERRED (will review later)")
        
        return True
    
    def run_validation(self):
        """Run the full validation workflow"""
        print("\n" + "🔍 MISSING PUBLICATIONS VALIDATION TOOL")
        print("="*80)
        print(f"Loaded {len(self.existing_titles)} existing publications from bibliography")
        print(f"Found {self.missing_data['counts']['missing_from_researchgate']} candidates from ResearchGate")
        print(f"Found {self.missing_data['counts']['missing_from_google_scholar']} candidates from Google Scholar")
        print(f"Found {self.missing_data['counts']['present_on_both_sources_but_missing_in_bib']} on BOTH sources")
        print("="*80)
        
        # Priority 1: Publications present on BOTH sources (highest confidence)
        if self.missing_data['present_on_both_sources_but_missing_in_bib']:
            print("\n\n📌 PRIORITY 1: Publications found on BOTH ResearchGate AND Google Scholar")
            print("   (These are most likely legitimate publications)")
            input("\nPress ENTER to start reviewing...")
            
            if not self.validate_category('both_sources', 
                                         self.missing_data['present_on_both_sources_but_missing_in_bib']):
                self.save_decisions()
                return
        
        # Priority 2: Google Scholar only (has citation counts and better metadata)
        print("\n\n📌 PRIORITY 2: Publications found only on Google Scholar")
        print("   (Review carefully - may include work from others with similar names)")
        choice = input("\nDo you want to review Google Scholar publications? [Y/n]: ").strip().upper()
        
        if choice != 'N':
            if not self.validate_category('google_scholar', 
                                         self.missing_data['missing_from_google_scholar']):
                self.save_decisions()
                return
        
        # Priority 3: ResearchGate only
        print("\n\n📌 PRIORITY 3: Publications found only on ResearchGate")
        print("   (These have less metadata but may be important)")
        choice = input("\nDo you want to review ResearchGate publications? [Y/n]: ").strip().upper()
        
        if choice != 'N':
            if not self.validate_category('researchgate', 
                                         self.missing_data['missing_from_researchgate']):
                self.save_decisions()
                return
        
        # All done
        self.save_decisions()
        print("\n✅ Validation complete!")
    
    def save_decisions(self):
        """Save validation decisions to file"""
        output_file = Path('c:/academic-cv/data/processed/validation_decisions.json')
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        summary = {
            'generated_at': datetime.now().isoformat(),
            'total_reviewed': len(self.decisions),
            'to_add': sum(1 for d in self.decisions if d['decision'] == 'A'),
            'skipped': sum(1 for d in self.decisions if d['decision'] == 'S'),
            'deferred': sum(1 for d in self.decisions if d['decision'] == 'D'),
            'decisions': self.decisions
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Decisions saved to: {output_file}")
        print(f"\n📊 SUMMARY:")
        print(f"   Total reviewed: {summary['total_reviewed']}")
        print(f"   ✅ To add: {summary['to_add']}")
        print(f"   ❌ Skipped: {summary['skipped']}")
        print(f"   ⏭️  Deferred: {summary['deferred']}")


def main():
    missing_file = Path('c:/academic-cv/data/latex/missing_publications.json')
    bib_file = Path('c:/academic-cv/data/latex/publications.bib')
    
    if not missing_file.exists():
        print(f"❌ Error: Missing publications file not found: {missing_file}")
        return
    
    if not bib_file.exists():
        print(f"❌ Error: Bibliography file not found: {bib_file}")
        return
    
    validator = MissingPublicationValidator(missing_file, bib_file)
    
    try:
        validator.run_validation()
    except KeyboardInterrupt:
        print("\n\n⏸️  Interrupted by user. Saving decisions...")
        validator.save_decisions()
    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        print("Saving decisions before exit...")
        validator.save_decisions()
        raise


if __name__ == "__main__":
    main()
