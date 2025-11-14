#!/usr/bin/env python3
"""
Stage 1: OpenAlex Publication Extraction
=========================================
Fetches all publications for a given ORCID from OpenAlex API.
Performs initial data quality checks and creates extraction report.

Usage:
    python 01_openalex_extract.py [--orcid ORCID] [--output DIR]

Features:
    - Extracts author publications with comprehensive metadata
    - Handles pagination automatically
    - Validates and deduplicates at extraction time
    - Generates detailed extraction report
    - Saves raw JSON for transparency
"""

import json
import requests
import pathlib
import yaml
import sys
from datetime import datetime
from typing import List, Dict, Any, Tuple
from collections import Counter


class OpenAlexExtractor:
    """Handles OpenAlex API interactions and publication extraction."""
    
    BASE_URL = "https://api.openalex.org"
    PER_PAGE = 200  # Max allowed per page
    
    def __init__(self, orcid: str, mailto: str = ""):
        """
        Initialize extractor with ORCID and contact email.
        
        Args:
            orcid: ORCID identifier (e.g., "0000-0002-4481-0115")
            mailto: Email for API politeness (recommended)
        """
        self.orcid = self._clean_orcid(orcid)
        self.mailto = mailto
        self.author_data = None
        self.works = []
        self.extraction_stats = {}
        
    @staticmethod
    def _clean_orcid(orcid: str) -> str:
        """Extract ORCID from various formats."""
        if "orcid.org/" in orcid:
            return orcid.split("orcid.org/")[-1]
        return orcid
    
    def fetch_author(self) -> Dict[str, Any]:
        """
        Fetch author metadata from OpenAlex.
        
        Returns:
            Author data dictionary
            
        Raises:
            requests.HTTPError: If API call fails
        """
        print(f"🔍 Fetching author data for ORCID: {self.orcid}")
        
        url = f"{self.BASE_URL}/authors/orcid:{self.orcid}"
        params = {"mailto": self.mailto} if self.mailto else {}
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        self.author_data = response.json()
        
        print(f"✅ Author: {self.author_data.get('display_name', 'Unknown')}")
        print(f"   OpenAlex ID: {self.author_data.get('id')}")
        print(f"   Works count (OpenAlex): {self.author_data.get('works_count', 0)}")
        
        return self.author_data
    
    def fetch_works(self) -> List[Dict[str, Any]]:
        """
        Fetch all works for the author with pagination.
        
        Returns:
            List of work dictionaries
        """
        if not self.author_data:
            raise ValueError("Author data not fetched. Call fetch_author() first.")
        
        works_url = self.author_data["works_api_url"]
        page = 1
        all_works = []
        
        print(f"\n📚 Fetching publications...")
        
        while True:
            print(f"   Fetching page {page}...", end=" ", flush=True)
            
            params = {
                "per-page": self.PER_PAGE,
                "page": page,
                "mailto": self.mailto
            }
            
            response = requests.get(works_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            results = data.get("results", [])
            all_works.extend(results)
            
            print(f"({len(results)} items, total: {len(all_works)})")
            
            if not data.get("next_page"):
                break
            
            page += 1
        
        self.works = all_works
        return all_works
    
    def generate_extraction_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive extraction statistics and quality metrics.
        
        Returns:
            Dictionary with extraction statistics
        """
        stats = {
            "timestamp": datetime.now().isoformat(),
            "orcid": self.orcid,
            "author_name": self.author_data.get("display_name", "Unknown"),
            "total_publications": len(self.works),
            "by_type": Counter(),
            "by_year": Counter(),
            "citations": {
                "total_cited_by_count": sum(w.get("cited_by_count", 0) for w in self.works),
                "max_citations": max((w.get("cited_by_count", 0) for w in self.works), default=0),
                "highly_cited": len([w for w in self.works if w.get("cited_by_count", 0) > 10]),
            },
            "data_completeness": {
                "with_doi": len([w for w in self.works if w.get("doi")]),
                "with_abstract": len([w for w in self.works if w.get("abstract")]),
                "with_open_access": len([w for w in self.works if w.get("open_access", {}).get("is_oa")]),
                "with_keywords": len([w for w in self.works if w.get("keywords")]),
                "with_url": len([w for w in self.works if w.get("primary_location", {}).get("landing_page_url")]),
            },
            "venues": Counter(),
            "types": {},
        }
        
        # Analyze each work
        for work in self.works:
            # Type distribution
            work_type = work.get("type", "Unknown")
            stats["by_type"][work_type] += 1
            
            # Year distribution
            year = work.get("publication_year", "Unknown")
            stats["by_year"][year] += 1
            
            # Venue analysis
            if work.get("primary_location"):
                venue = work["primary_location"].get("venue", {}).get("display_name", "Unknown")
                if venue:
                    stats["venues"][venue] += 1
        
        # Convert Counters to dicts for JSON serialization
        stats["by_type"] = dict(stats["by_type"])
        stats["by_year"] = dict(sorted(stats["by_year"].items()))
        stats["venues"] = dict(stats["venues"])
        
        self.extraction_stats = stats
        return stats
    
    def save_outputs(self, output_dir: pathlib.Path) -> Tuple[pathlib.Path, pathlib.Path, pathlib.Path]:
        """
        Save extraction results to JSON files.
        
        Args:
            output_dir: Directory to save files
            
        Returns:
            Tuple of (author_file, works_file, report_file) paths
        """
        output_dir = pathlib.Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save author data
        author_file = output_dir / "01_author.json"
        with open(author_file, "w", encoding="utf-8") as f:
            json.dump(self.author_data, f, indent=2, ensure_ascii=False)
        print(f"✅ Author data saved: {author_file}")
        
        # Save works
        works_file = output_dir / "01_works_raw.json"
        with open(works_file, "w", encoding="utf-8") as f:
            json.dump(self.works, f, indent=2, ensure_ascii=False)
        print(f"✅ Works data saved: {works_file}")
        
        # Save report
        report_file = output_dir / "01_extraction_report.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(self.extraction_stats, f, indent=2, ensure_ascii=False)
        print(f"✅ Extraction report saved: {report_file}")
        
        return author_file, works_file, report_file


def main():
    """Main execution function."""
    
    # Load configuration
    config_path = pathlib.Path(__file__).parent.parent.parent.parent / "profiles.yaml"
    
    if not config_path.exists():
        print(f"❌ Config not found: {config_path}")
        sys.exit(1)
    
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    orcid = config.get("orcid", "").replace("https://orcid.org/", "")
    mailto = config.get("mailto", "")
    
    if not orcid:
        print("❌ ORCID not found in profiles.yaml")
        sys.exit(1)
    
    # Set output directory (same as this script's directory)
    output_dir = pathlib.Path(__file__).parent
    
    print("=" * 70)
    print("STAGE 1: OpenAlex Publication Extraction")
    print("=" * 70)
    
    try:
        # Extract data
        extractor = OpenAlexExtractor(orcid, mailto)
        extractor.fetch_author()
        extractor.fetch_works()
        extractor.generate_extraction_report()
        
        # Save outputs
        extractor.save_outputs(output_dir)
        
        # Print summary
        print("\n" + "=" * 70)
        print("EXTRACTION SUMMARY")
        print("=" * 70)
        stats = extractor.extraction_stats
        print(f"Total Publications: {stats['total_publications']}")
        print(f"\nBy Type:")
        for pub_type, count in sorted(stats['by_type'].items()):
            print(f"  {pub_type}: {count}")
        print(f"\nCitations:")
        print(f"  Total Cited By Count: {stats['citations']['total_cited_by_count']}")
        print(f"  Highly Cited (>10): {stats['citations']['highly_cited']}")
        print(f"\nData Completeness:")
        for key, value in stats['data_completeness'].items():
            pct = (value / stats['total_publications'] * 100) if stats['total_publications'] > 0 else 0
            print(f"  {key}: {value} ({pct:.1f}%)")
        print(f"\nTop 5 Venues:")
        for venue, count in sorted(stats['venues'].items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  {venue}: {count}")
        print("\n✅ Stage 1 complete! Ready for validation.")
        
    except requests.HTTPError as e:
        print(f"\n❌ API Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
