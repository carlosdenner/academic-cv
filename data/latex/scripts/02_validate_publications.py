#!/usr/bin/env python3
"""
Stage 2: Publication Validation & Analysis
============================================
Validates, deduplicates, and analyzes OpenAlex publication data.
Ensures data quality and ownership verification.

Features:
    - Cross-references author name variations
    - Detects and flags duplicate entries
    - Validates required fields
    - Categorizes publications
    - Generates comprehensive validation report
    - Identifies potential false positives/negatives
"""

import json
import pathlib
from typing import List, Dict, Any, Tuple
from datetime import datetime
from collections import Counter
from difflib import SequenceMatcher


class PublicationValidator:
    """Validates and analyzes publication data from OpenAlex."""
    
    # Expected name variations for author
    AUTHOR_NAME_VARIATIONS = [
        "Carlos Denner",
        "Carlos Denner dos Santos",
        "Carlos Denner dos Santos Jr",
        "Carlos Denner dos Santos Junior",
        "Denner, Carlos",
        "Denner, Carlos D.",
        "dos Santos, Carlos Denner",
    ]
    
    # Your typical research areas (for content validation)
    EXPECTED_RESEARCH_AREAS = [
        "information systems", "software engineering", "open source", 
        "IT governance", "artificial intelligence", "AI governance",
        "crowdsourcing", "software quality", "management information systems",
        "data science", "business intelligence", "public sector IT",
        "free software", "FOSS", "software metrics", "source code",
        "technology governance", "information technology"
    ]
    
    # Research areas that indicate likely false positive
    UNLIKELY_RESEARCH_AREAS = [
        "bacteria", "plant disease", "eucalyptus", "phytopathology",
        "microbiology", "botany", "agriculture", "forestry",
        "medical", "clinical", "surgery", "pharmaceutical"
    ]
    
    # Your typical affiliations
    EXPECTED_INSTITUTIONS = [
        "University of Brasília", "Universidade de Brasília", "UnB",
        "Southern Illinois University", "UQAM",  
        "Université du Québec à Montréal", "UFMG",
        "Universidade Federal de Minas Gerais",
        "Université de Sherbrooke", "Bell Canada"
    ]
    
    # Publication types to keep
    VALID_TYPES = {
        "article": "Journal Article",
        "review": "Review Article",
        "book-chapter": "Book Chapter",
        "preprint": "Preprint",
        "editorial": "Editorial",
        "dataset": "Dataset",
        "peer-review": "Peer Review",
    }
    
    def __init__(self, works_data: List[Dict[str, Any]], author_data: Dict[str, Any]):
        """
        Initialize validator with OpenAlex data.
        
        Args:
            works_data: List of work dictionaries from OpenAlex
            author_data: Author metadata from OpenAlex
        """
        self.works = works_data
        self.author_data = author_data
        self.validated_works = []
        self.excluded_works = []
        self.issues = []
        self.statistics = {}
        
    def _is_author_in_work(self, work: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Verify that the target author is actually an author of the work.
        
        Args:
            work: Work dictionary from OpenAlex
            
        Returns:
            Tuple of (is_author, author_names_found)
        """
        authorships = work.get("authorships", [])
        found_names = []
        is_author = False
        
        target_orcid = "0000-0002-4481-0115"
        
        for authorship in authorships:
            author = authorship.get("author", {})
            author_name = author.get("display_name", "")
            author_orcid = author.get("orcid", "") or ""
            
            # Check ORCID match (most reliable)
            if author_orcid and target_orcid in author_orcid:
                is_author = True
                found_names.append(author_name)
            
            # Check name similarity
            elif self._name_similarity(author_name) > 0.7:
                # Could be Carlos Denner but not confirmed
                found_names.append(author_name)
        
        return is_author, found_names
    
    @staticmethod
    def _name_similarity(name: str) -> float:
        """Calculate similarity to author name variations."""
        if not name:
            return 0.0
        
        name_lower = name.lower()
        max_sim = 0.0
        
        for variation in PublicationValidator.AUTHOR_NAME_VARIATIONS:
            sim = SequenceMatcher(None, name_lower, variation.lower()).ratio()
            max_sim = max(max_sim, sim)
        
        return max_sim
    
    def _validate_content(self, work: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate that the publication content matches your research profile.
        Checks keywords, title, abstract, and institutions.
        
        Returns:
            Tuple of (is_valid, reason)
        """
        title = work.get("title", "").lower()
        keywords = work.get("keywords", [])
        
        # Extract keyword display names
        keyword_texts = []
        for kw in keywords:
            if isinstance(kw, dict):
                keyword_texts.append(kw.get("display_name", "").lower())
            else:
                keyword_texts.append(str(kw).lower())
        
        all_text = title + " " + " ".join(keyword_texts)
        
        # Check for unlikely research areas (biology, medicine, etc.)
        unlikely_matches = [area for area in self.UNLIKELY_RESEARCH_AREAS 
                           if area.lower() in all_text]
        
        if unlikely_matches:
            return False, f"Unlikely research area: {', '.join(unlikely_matches)}"
        
        # Check for expected research areas
        expected_matches = [area for area in self.EXPECTED_RESEARCH_AREAS 
                           if area.lower() in all_text]
        
        # Check institutions
        authorships = work.get("authorships", [])
        institution_names = []
        for authorship in authorships:
            institutions = authorship.get("institutions", [])
            for inst in institutions:
                inst_name = inst.get("display_name", "")
                institution_names.append(inst_name)
        
        expected_inst_matches = [inst for inst in self.EXPECTED_INSTITUTIONS
                                if any(inst.lower() in name.lower() 
                                      for name in institution_names)]
        
        # Decision logic
        if expected_matches or expected_inst_matches:
            return True, "Content matches research profile"
        
        # No clear matches - flag for review
        return False, f"No matching research areas/institutions found"
    
    def _extract_author_info(self, work: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract author information from work.
        
        Args:
            work: Work dictionary
            
        Returns:
            Dictionary with author info
        """
        authorships = work.get("authorships", [])
        author_count = len(authorships)
        
        # Find position of Carlos Denner
        carlos_position = None
        carlos_name = None
        
        target_orcid = "0000-0002-4481-0115"
        
        for i, authorship in enumerate(authorships):
            author = authorship.get("author", {})
            orcid = author.get("orcid", "") or ""
            if target_orcid in orcid:
                carlos_position = i + 1
                carlos_name = author.get("display_name", "")
                break
        
        # Extract lead authors
        lead_authors = []
        for i, authorship in enumerate(authorships[:3]):
            author = authorship.get("author", {})
            lead_authors.append(author.get("display_name", "Unknown"))
        
        return {
            "total_authors": author_count,
            "carlos_position": carlos_position,
            "carlos_name": carlos_name,
            "lead_authors": lead_authors,
        }
    
    def validate(self) -> Tuple[List[Dict[str, Any]], List[str]]:
        """
        Validate all works and return validated list.
        STRICT MODE: ORCID verification + content validation.
        
        Returns:
            Tuple of (validated_works, issues_list)
        """
        print("\n🔍 Validating publications (STRICT: ORCID + content validation)...")
        
        validated = []
        excluded = []
        issues = []
        
        for i, work in enumerate(self.works, 1):
            work_id = work.get("id", f"work_{i}")
            title = work.get("title", "Unknown")
            
            # Check 1: STRICT ORCID verification - MUST have ORCID match
            is_author, found_names = self._is_author_in_work(work)
            if not is_author:
                issue = f"❌ EXCLUDED {i}: '{title[:60]}...' - No ORCID match found"
                issues.append(issue)
                excluded.append({
                    "title": title,
                    "year": work.get("publication_year"),
                    "type": work.get("type"),
                    "reason": "No ORCID match",
                    "authors": found_names
                })
                print(f"   {issue}")
                continue  # SKIP this publication
            
            # Check 2: Content validation - does this match your research profile?
            content_valid, content_reason = self._validate_content(work)
            if not content_valid:
                issue = f"❌ EXCLUDED {i}: '{title[:60]}...' - {content_reason}"
                issues.append(issue)
                excluded.append({
                    "title": title,
                    "year": work.get("publication_year"),
                    "type": work.get("type"),
                    "reason": content_reason,
                    "authors": found_names,
                    "orcid_found": True  # Had ORCID but failed content check
                })
                print(f"   {issue}")
                continue  # SKIP this publication
            
            # Check 3: Required fields
            if not work.get("doi") and work.get("type") != "dataset":
                issue = f"⚠️  Work {i}: Missing DOI - {title[:50]}..."
                issues.append(issue)
            
            if not work.get("title"):
                issue = f"❌ Work {i}: Missing title (skipping)"
                issues.append(issue)
                continue
            
            # Check 4: Extract author info
            author_info = self._extract_author_info(work)
            
            # Check 5: Duplicates (same title in same year)
            year = work.get("publication_year", 0)
            for prev_work in validated:
                if (prev_work.get("title").lower() == title.lower() and 
                    prev_work.get("publication_year") == year):
                    issue = f"⚠️  Work {i}: Potential duplicate - {title[:50]}..."
                    issues.append(issue)
            
            # Add validation metadata
            validated_work = {
                **work,
                "_validated": True,
                "_orcid_verified": True,  # Confirmed ORCID match
                "_content_verified": True,  # Confirmed content match
                "_author_info": author_info,
                "_validation_notes": [],
            }
            
            validated.append(validated_work)
        
        self.validated_works = validated
        self.issues = issues
        self.excluded_works = excluded
        
        print(f"✅ Validation complete: {len(validated)} works included")
        print(f"❌ Excluded: {len(excluded)} works (failed ORCID or content validation)")
        
        return validated, issues
    
    def generate_statistics(self) -> Dict[str, Any]:
        """
        Generate comprehensive statistics about validated publications.
        
        Returns:
            Dictionary with detailed statistics
        """
        stats = {
            "timestamp": datetime.now().isoformat(),
            "total_validated": len(self.validated_works),
            "issues_count": len(self.issues),
            "by_type": Counter(),
            "by_year": Counter(),
            "by_journal": Counter(),
            "author_position": Counter(),
            "citations": {
                "total": 0,
                "per_publication_avg": 0,
                "distribution": {
                    "highly_cited_gt50": 0,
                    "cited_11_50": 0,
                    "cited_1_10": 0,
                    "not_cited": 0,
                }
            },
            "data_quality": {
                "with_doi": 0,
                "with_open_access": 0,
                "with_keywords": 0,
                "with_multiple_authors": 0,
            },
            "top_cited": [],
            "recent_publications": [],
        }
        
        # Process each work
        for work in self.validated_works:
            # Type distribution
            work_type = work.get("type", "unknown")
            stats["by_type"][work_type] += 1
            
            # Year distribution
            year = work.get("publication_year", 0)
            if year:
                stats["by_year"][year] += 1
            
            # Venue (from primary location)
            location = work.get("primary_location", {})
            if location and location.get("venue"):
                venue = location["venue"].get("display_name", "Unknown")
                stats["by_journal"][venue] += 1
            
            # Author position
            author_info = work.get("_author_info", {})
            if author_info.get("carlos_position"):
                stats["author_position"][author_info["carlos_position"]] += 1
            
            # Citations
            citations = work.get("cited_by_count", 0)
            stats["citations"]["total"] += citations
            
            if citations > 50:
                stats["citations"]["distribution"]["highly_cited_gt50"] += 1
            elif citations >= 11:
                stats["citations"]["distribution"]["cited_11_50"] += 1
            elif citations >= 1:
                stats["citations"]["distribution"]["cited_1_10"] += 1
            else:
                stats["citations"]["distribution"]["not_cited"] += 1
            
            # Data quality
            if work.get("doi"):
                stats["data_quality"]["with_doi"] += 1
            if work.get("open_access", {}).get("is_oa"):
                stats["data_quality"]["with_open_access"] += 1
            if work.get("keywords"):
                stats["data_quality"]["with_keywords"] += 1
            if author_info.get("total_authors", 0) > 1:
                stats["data_quality"]["with_multiple_authors"] += 1
        
        # Calculate averages
        if stats["total_validated"] > 0:
            stats["citations"]["per_publication_avg"] = round(
                stats["citations"]["total"] / stats["total_validated"], 2
            )
        
        # Top cited works
        top_cited = sorted(
            self.validated_works,
            key=lambda x: x.get("cited_by_count", 0),
            reverse=True
        )[:5]
        
        stats["top_cited"] = [
            {
                "title": w.get("title", "Unknown"),
                "year": w.get("publication_year", 0),
                "citations": w.get("cited_by_count", 0),
                "doi": w.get("doi", "N/A"),
            }
            for w in top_cited
        ]
        
        # Recent works
        recent = sorted(
            self.validated_works,
            key=lambda x: x.get("publication_year", 0),
            reverse=True
        )[:5]
        
        stats["recent_publications"] = [
            {
                "title": w.get("title", "Unknown"),
                "year": w.get("publication_year", 0),
                "type": w.get("type", "Unknown"),
                "doi": w.get("doi", "N/A"),
            }
            for w in recent
        ]
        
        # Convert Counters to dicts
        stats["by_type"] = dict(stats["by_type"])
        stats["by_year"] = dict(sorted(stats["by_year"].items()))
        stats["by_journal"] = dict(sorted(
            stats["by_journal"].items(),
            key=lambda x: x[1],
            reverse=True
        )[:10])
        stats["author_position"] = dict(sorted(stats["author_position"].items()))
        
        self.statistics = stats
        return stats


def main():
    """Main validation execution."""
    
    script_dir = pathlib.Path(__file__).parent
    
    # Load raw data
    works_file = script_dir / "01_works_raw.json"
    author_file = script_dir / "01_author.json"
    
    if not works_file.exists() or not author_file.exists():
        print("❌ Raw data files not found. Run 01_openalex_extract.py first.")
        return
    
    with open(works_file, encoding="utf-8") as f:
        works = json.load(f)
    
    with open(author_file, encoding="utf-8") as f:
        author = json.load(f)
    
    print("=" * 70)
    print("STAGE 2: Publication Validation & Analysis")
    print("=" * 70)
    
    # Validate
    validator = PublicationValidator(works, author)
    validated, issues = validator.validate()
    stats = validator.generate_statistics()
    
    # Save validated works
    validated_file = script_dir / "02_validated_works.json"
    with open(validated_file, "w", encoding="utf-8") as f:
        json.dump(validated, f, indent=2, ensure_ascii=False)
    print(f"\n✅ Validated works saved: {validated_file}")
    
    # Save excluded works for review
    if validator.excluded_works:
        excluded_file = script_dir / "02_excluded_works.json"
        with open(excluded_file, "w", encoding="utf-8") as f:
            json.dump(validator.excluded_works, f, indent=2, ensure_ascii=False)
        print(f"❌ Excluded works saved: {excluded_file} ({len(validator.excluded_works)} items)")
    
    # Save statistics
    stats_file = script_dir / "02_validation_report.json"
    with open(stats_file, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    print(f"✅ Validation report saved: {stats_file}")
    
    # Print comprehensive summary
    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)
    
    print(f"\n📊 Publication Breakdown:")
    print(f"   Total Processed: {len(works)}")
    print(f"   Total Validated: {stats['total_validated']}")
    print(f"   Excluded (no ORCID): {len(validator.excluded_works)}")
    print(f"   Validation Issues: {stats['issues_count']}")
    
    print(f"\n📚 By Type:")
    for ptype, count in sorted(stats['by_type'].items(), key=lambda x: x[1], reverse=True):
        label = PublicationValidator.VALID_TYPES.get(ptype, ptype)
        print(f"   {label}: {count}")
    
    print(f"\n📈 Citation Impact:")
    print(f"   Total Citations: {stats['citations']['total']}")
    print(f"   Avg per Publication: {stats['citations']['per_publication_avg']}")
    print(f"   Highly Cited (>50): {stats['citations']['distribution']['highly_cited_gt50']}")
    print(f"   Citations 11-50: {stats['citations']['distribution']['cited_11_50']}")
    print(f"   Citations 1-10: {stats['citations']['distribution']['cited_1_10']}")
    print(f"   Not Cited: {stats['citations']['distribution']['not_cited']}")
    
    print(f"\n✨ Data Quality:")
    total = stats['total_validated']
    for key, count in stats['data_quality'].items():
        pct = (count / total * 100) if total > 0 else 0
        print(f"   {key}: {count} ({pct:.1f}%)")
    
    print(f"\n🏆 Top 5 Most Cited:")
    for i, pub in enumerate(stats['top_cited'], 1):
        print(f"   {i}. [{pub['year']}] {pub['citations']} citations")
        print(f"      {pub['title'][:60]}...")
    
    print(f"\n📅 Recent Publications (Last 5):")
    for i, pub in enumerate(stats['recent_publications'], 1):
        print(f"   {i}. [{pub['year']}] {pub['type']}")
        print(f"      {pub['title'][:60]}...")
    
    print(f"\n🔍 Top Venues (Last 10):")
    for venue, count in list(stats['by_journal'].items())[:10]:
        if venue != "Unknown":
            print(f"   {venue}: {count}")
    
    if issues:
        print(f"\n⚠️  Validation Issues:")
        for issue in issues[:10]:
            print(f"   {issue}")
        if len(issues) > 10:
            print(f"   ... and {len(issues) - 10} more issues")
    
    if validator.excluded_works:
        print(f"\n❌ EXCLUDED WORKS (No ORCID Match):")
        for i, excluded in enumerate(validator.excluded_works[:10], 1):
            print(f"   {i}. [{excluded['year']}] {excluded['type']}")
            print(f"      {excluded['title'][:60]}...")
            if excluded.get('authors'):
                print(f"      Authors found: {', '.join(excluded['authors'][:3])}")
        if len(validator.excluded_works) > 10:
            print(f"   ... and {len(validator.excluded_works) - 10} more excluded")
        print(f"\n   ℹ️  These works were excluded because they don't have your ORCID")
        print(f"   ℹ️  Review 02_excluded_works.json to verify these are correct")
    
    print("\n✅ Stage 2 complete! Ready for BibTeX generation.")


if __name__ == "__main__":
    main()
