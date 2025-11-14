#!/usr/bin/env python3
"""
Stage 3: BibTeX Generation
============================
Converts validated OpenAlex publications to BibTeX format.
Creates a publication-quality .bib file with proper formatting.

Features:
    - Generates valid BibTeX entries
    - Uses appropriate entry types
    - Normalizes author names
    - Handles special characters properly
    - Cross-references when available
    - Quality assurance checks
"""

import json
import pathlib
import re
from typing import List, Dict, Any, Tuple
from datetime import datetime
from collections import defaultdict


class BibTeXGenerator:
    """Generates BibTeX entries from validated OpenAlex data."""
    
    # Mapping from OpenAlex type to BibTeX entry type
    TYPE_MAPPING = {
        "article": "@article",
        "book-chapter": "@incollection",
        "review": "@article",  # Reviews are articles, will add 'review' keyword
        "preprint": "@unpublished",
        "editorial": "@article",
        "dataset": "@misc",  # Use @misc with 'dataset' keyword for biblatex compatibility
        "peer-review": "@article",  # Peer reviews are articles
    }
    
    # Required fields for each entry type
    REQUIRED_FIELDS = {
        "@article": ["author", "title", "journal", "year"],
        "@incollection": ["author", "title", "booktitle", "year"],
        "@unpublished": ["author", "title", "year"],
        "@misc": ["author", "title", "year"],
    }
    
    def __init__(self, validated_works: List[Dict[str, Any]]):
        """
        Initialize BibTeX generator with validated works.
        
        Args:
            validated_works: List of validated publication dictionaries
        """
        self.works = validated_works
        self.bibtex_entries = []
        self.generation_stats = {}
        
    @staticmethod
    def _clean_text(text: str | list) -> str:
        """
        Clean text for BibTeX by escaping special characters.
        
        Args:
            text: Raw text or list of text
            
        Returns:
            Cleaned text safe for BibTeX
        """
        if isinstance(text, list):
            text = " ".join(str(t) for t in text)
        
        if not text:
            return ""
        
        text = str(text).strip()
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove newline characters and normalize whitespace
        text = text.replace('\\n', ' ').replace('\n', ' ')
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Handle common Unicode characters that should be escaped
        replacements = {
            "á": "{\\\'a}",
            "à": "{\\`a}",
            "ã": "{\\~a}",
            "é": "{\\\'e}",
            "è": "{\\`e}",
            "ê": "{\\^e}",
            "í": "{\\\'i}",
            "ó": "{\\\'o}",
            "ô": "{\\^o}",
            "õ": "{\\~o}",
            "ú": "{\\\'u}",
            "ü": "{\\\"u}",
            "ç": "{\\c c}",
            "Á": "{\\\'A}",
            "À": "{\\`A}",
            "Ã": "{\\~A}",
            "É": "{\\\'E}",
            "È": "{\\`E}",
            "Ê": "{\\^E}",
            "Í": "{\\\'I}",
            "Ó": "{\\\'O}",
            "Ô": "{\\^O}",
            "Õ": "{\\~O}",
            "Ú": "{\\\'U}",
            "Ü": "{\\\"U}",
            "Ç": "{\\c C}",
            "‐": "-",  # Unicode hyphen to ASCII hyphen
            "–": "--",  # En dash
            "—": "---",  # Em dash
            "□": "",  # Remove box character
            "&": "\\&",  # Escape ampersand for LaTeX
        }
        
        for char, replacement in replacements.items():
            text = text.replace(char, replacement)
        
        return text
    
    @staticmethod
    def _to_sentence_case(title: str) -> str:
        """
        Convert title to sentence case (capitalize only first word and proper nouns).
        Preserves acronyms and names that are already capitalized.
        
        Args:
            title: Original title
            
        Returns:
            Sentence case title
        """
        if not title:
            return ""
        
        # Remove HTML tags first
        title = re.sub(r'<[^>]+>', '', title)
        
        # List of words that should stay capitalized (acronyms, proper nouns)
        preserve_caps = {
            'AI', 'IT', 'API', 'CRM', 'TCO', 'ORCID', 'DOI', 'IEEE', 'ACM',
            'Brazil', 'Brazilian', 'Canada', 'Canadian', 'Wikipedia', 'GitHub',
            'Python', 'Java', 'SQL', 'COVID', 'UQAM', 'UnB', 'USA', 'UK',
            'OSS', 'FLOSS', 'IoT', 'ML', 'NLP', 'ChatGPT', 'GPT'
        }
        
        words = title.split()
        result = []
        
        for i, word in enumerate(words):
            # Keep first word capitalized
            if i == 0:
                result.append(word.capitalize())
            # Keep known acronyms/proper nouns
            elif word in preserve_caps or word.upper() in preserve_caps:
                result.append(word.upper() if word.upper() in preserve_caps else word)
            # Keep words that are all caps (likely acronyms)
            elif word.isupper() and len(word) > 1:
                result.append(word)
            # Keep words with internal caps (like "ChatGPT")
            elif any(c.isupper() for c in word[1:]):
                result.append(word)
            # Lowercase everything else
            else:
                result.append(word.lower())
        
        return ' '.join(result)
    
    @staticmethod
    def _normalize_authors(authorships: List[Dict]) -> str:
        """
        Convert OpenAlex authorships to BibTeX author format.
        
        Args:
            authorships: List of authorship dictionaries
            
        Returns:
            BibTeX-formatted author string (Last, First and Last, First)
        """
        authors = []
        
        for authorship in authorships:
            author = authorship.get("author", {})
            name = author.get("display_name", "")
            
            if not name:
                continue
            
            # Try to parse name format
            # Handle "FirstName LastName" format
            parts = name.split()
            
            if len(parts) >= 2:
                # Last name is typically the last part
                last_name = parts[-1]
                first_names = " ".join(parts[:-1])
                # Format as "Last, First"
                author_str = f"{BibTeXGenerator._clean_text(last_name)}, {BibTeXGenerator._clean_text(first_names)}"
            else:
                author_str = BibTeXGenerator._clean_text(name)
            
            authors.append(author_str)
        
        return " and ".join(authors)
    
    @staticmethod
    def _generate_bibtex_key(work: Dict[str, Any], index: int) -> str:
        """
        Generate unique BibTeX citation key.
        
        Args:
            work: Work dictionary
            index: Index for uniqueness
            
        Returns:
            BibTeX key (e.g., "denner2021ai")
        """
        # Try to extract first author last name
        authorships = work.get("authorships", [])
        if authorships:
            first_author = authorships[0].get("author", {}).get("display_name", "")
            if first_author:
                last_name = first_author.split()[-1].lower()
            else:
                last_name = "unknown"
        else:
            last_name = "unknown"
        
        # Get year
        year = work.get("publication_year", "xxxx")
        
        # Get short title
        title = work.get("title", "work")
        # Take first few words, make lowercase, remove special chars
        title_words = title.lower().split()[:2]
        title_key = "".join(re.sub(r"[^a-z]", "", word) for word in title_words)
        title_key = title_key[:4] if title_key else "work"
        
        key = f"{last_name}{year}{title_key}"
        
        return re.sub(r"[^a-z0-9]", "", key)[:30]
    
    def _extract_venue_info(self, work: Dict[str, Any]) -> Tuple[str, str, str]:
        """
        Extract journal/venue information from work.
        
        Args:
            work: Work dictionary
            
        Returns:
            Tuple of (venue_name, issn, volume_issue)
        """
        location = work.get("primary_location") or {}
        source = location.get("source") or {}
        
        venue_name = source.get("display_name", "")
        issn = source.get("issn_l", "")
        
        # Get volume/issue from biblio field
        biblio = work.get("biblio") or {}
        volume_issue = ""
        if biblio.get("volume"):
            volume_issue = f"volume={biblio['volume']}"
            if biblio.get("issue"):
                volume_issue += f", number={biblio['issue']}"
        
        return venue_name, issn, volume_issue
    
    def generate_bibtex_entries(self) -> List[str]:
        """
        Generate BibTeX entries for all validated works.
        
        Returns:
            List of BibTeX entry strings
        """
        print("\n🔄 Generating BibTeX entries...")
        
        entries = []
        stats = defaultdict(int)
        
        for idx, work in enumerate(self.works, 1):
            try:
                entry = self._work_to_bibtex(work, idx)
                if entry:
                    entries.append(entry)
                    stats["success"] += 1
                    stats[f"type_{work.get('type', 'unknown')}"] += 1
                else:
                    stats["skipped"] += 1
            except Exception as e:
                print(f"   ⚠️  Work {idx}: {str(e)}")
                stats["failed"] += 1
        
        self.bibtex_entries = entries
        self.generation_stats = dict(stats)
        
        print(f"✅ Generated {stats['success']} entries")
        
        return entries
    
    def _work_to_bibtex(self, work: Dict[str, Any], index: int) -> str | None:
        """
        Convert a single work to BibTeX format.
        
        Args:
            work: Work dictionary
            index: Index for key generation
            
        Returns:
            BibTeX entry string
        """
        # Determine entry type
        work_type = work.get("type", "article")
        bibtex_type = self.TYPE_MAPPING.get(work_type, "@misc")
        
        # Generate citation key
        citation_key = self._generate_bibtex_key(work, index)
        
        # Extract basic fields
        raw_title = work.get("title", "")
        title = self._to_sentence_case(raw_title)
        title = self._clean_text(title)
        if not title:
            return None
        
        authors = self._normalize_authors(work.get("authorships", []))
        if not authors:
            authors = "Unknown"
        
        year = work.get("publication_year", "")
        
        # Build fields dictionary - ALL VALUES IN BRACES
        fields = {
            "author": f"{{{authors}}}",
            "title": f"{{{title}}}",
            "year": f"{{{year}}}" if year else "{unknown}",
        }
        
        # Track original type for later use
        original_type = work.get('type', '')
        
        # Add type-specific fields
        if bibtex_type == "@article":
            venue_name, issn, volume_issue = self._extract_venue_info(work)
            if venue_name:
                fields["journal"] = f"{{{self._clean_text(venue_name)}}}"
            if volume_issue:
                fields.update(self._parse_volume_issue(volume_issue))
            
            # Add pages if available
            biblio = work.get("biblio") or {}
            first_page = biblio.get("first_page", "")
            last_page = biblio.get("last_page", "")
            if first_page:
                if last_page:
                    fields["pages"] = f"{{{first_page}--{last_page}}}"
                else:
                    fields["pages"] = f"{{{first_page}}}"
        
        elif bibtex_type == "@incollection":
            venue_name, _, _ = self._extract_venue_info(work)
            if venue_name:
                fields["booktitle"] = f"{{{self._clean_text(venue_name)}}}"
            
            # Add pages for book chapters too
            biblio = work.get("biblio") or {}
            first_page = biblio.get("first_page", "")
            last_page = biblio.get("last_page", "")
            if first_page:
                if last_page:
                    fields["pages"] = f"{{{first_page}--{last_page}}}"
                else:
                    fields["pages"] = f"{{{first_page}}}"
        
        elif bibtex_type == "@misc":
            # For misc items (including datasets), add publisher/repository information
            venue_name, _, _ = self._extract_venue_info(work)
            if venue_name:
                fields["howpublished"] = f"{{{self._clean_text(venue_name)}}}"
            # Add note based on original type
            if work.get('type') == 'dataset':
                fields["note"] = "{Research Dataset}"
        
        # Add DOI if available
        doi = work.get("doi", "")
        if doi:
            # Clean up DOI URL if needed
            if doi.startswith("https://doi.org/"):
                doi = doi.replace("https://doi.org/", "")
            fields["doi"] = f"{{{doi}}}"
        
        # Add URL if available and no DOI
        if not doi:
            url = work.get("primary_location", {}).get("landing_page_url", "")
            if url:
                fields["url"] = f"{{{url}}}"
        
        # Add keywords if available (but limit to avoid clutter)
        # For datasets and peer-reviews, use special keywords for filtering
        if original_type == 'dataset':
            fields["keywords"] = "{dataset}"
        elif original_type == 'peer-review':
            # Only peer-reviews get the special keyword, not "review" type (which is systematic review articles)
            fields["keywords"] = "{review}"
        else:
            keywords = work.get("keywords", [])
            if keywords and bibtex_type not in ["@misc", "@unpublished"]:
                # Extract display_name from keyword objects if they exist
                kw_names = []
                for kw in keywords[:5]:
                    if isinstance(kw, dict):
                        kw_names.append(kw.get('display_name', ''))
                    else:
                        kw_names.append(str(kw))
                kw_list = ", ".join(k for k in kw_names if k)
                if kw_list:
                    fields["keywords"] = f"{{{kw_list}}}"
        
        # Add open access note (except for datasets which already have a note)
        if work.get("open_access", {}).get("is_oa") and bibtex_type != "@dataset":
            if "note" not in fields:
                fields["note"] = "{Open Access}"
        
        # Format entry
        entry_lines = [f"{bibtex_type}{{{citation_key},"]
        
        for key, value in fields.items():
            entry_lines.append(f"  {key} = {value},")
        
        entry_lines[-1] = entry_lines[-1].rstrip(",")  # Remove trailing comma
        entry_lines.append("}")
        
        return "\n".join(entry_lines)
        """
        Convert a single work to BibTeX format.
        
        Args:
            work: Work dictionary
            index: Index for key generation
            
        Returns:
            BibTeX entry string
        """
        # Determine entry type
        work_type = work.get("type", "article")
        bibtex_type = self.TYPE_MAPPING.get(work_type, "@misc")
        
        # Generate citation key
        citation_key = self._generate_bibtex_key(work, index)
        
        # Extract basic fields
        title = self._clean_text(work.get("title", ""))
        if not title:
            return None
        
        authors = self._normalize_authors(work.get("authorships", []))
        if not authors:
            authors = "Unknown"
        
        year = work.get("publication_year", "")
        
        # Build fields dictionary
        fields = {
            "author": f"{{{authors}}}",
            "title": f"{{{title}}}",
            "year": str(year) if year else "unknown",
        }
        
        # Add type-specific fields
        if bibtex_type == "@article":
            venue_name, issn, volume_issue = self._extract_venue_info(work)
            if venue_name:
                fields["journal"] = f'"{self._clean_text(venue_name)}"'
            if volume_issue:
                fields.update(self._parse_volume_issue(volume_issue))
        
        elif bibtex_type == "@incollection":
            venue_name, _, _ = self._extract_venue_info(work)
            if venue_name:
                fields["booktitle"] = f'"{self._clean_text(venue_name)}"'
        
        # Add DOI if available
        doi = work.get("doi", "")
        if doi:
            # Clean up DOI URL if needed
            if doi.startswith("https://doi.org/"):
                doi = doi.replace("https://doi.org/", "")
            fields["doi"] = f'"{doi}"'
        
        # Add URL if available and no DOI
        if not doi:
            url = work.get("primary_location", {}).get("landing_page_url", "")
            if url:
                fields["url"] = f'"{url}"'
        
        # Add keywords if available
        keywords = work.get("keywords", [])
        if keywords and isinstance(keywords, list):
            # Extract keyword names from keyword objects if needed
            kw_names = []
            for kw in keywords[:5]:
                if isinstance(kw, dict):
                    kw_names.append(kw.get("display_name", str(kw)))
                else:
                    kw_names.append(str(kw))
            kw_str = ", ".join(self._clean_text(kw) for kw in kw_names)
            if kw_str:
                fields["keywords"] = f'"{kw_str}"'
        
        # Add open access note
        if work.get("open_access", {}).get("is_oa"):
            fields["note"] = '"Open Access"'
        
        # Format entry
        entry_lines = [f"{bibtex_type}{{{citation_key},"]
        
        for key, value in fields.items():
            # Ensure values are properly quoted/braced
            if key in ['author', 'title', 'journal', 'booktitle', 'note', 'keywords', 'url', 'doi']:
                # Already quoted in value
                entry_lines.append(f"  {key} = {value},")
            else:
                # Numeric or should be in braces
                if value.startswith('"') or value.startswith('{'):
                    entry_lines.append(f"  {key} = {value},")
                else:
                    entry_lines.append(f"  {key} = {{{value}}},")
        
        entry_lines[-1] = entry_lines[-1].rstrip(",")  # Remove trailing comma
        entry_lines.append("}")
        
        return "\n".join(entry_lines)
    
    @staticmethod
    def _parse_volume_issue(volume_issue: str) -> Dict[str, str]:
        """Parse volume/issue string into dictionary."""
        result = {}
        
        # Extract volume
        vol_match = re.search(r"volume=(\d+)", volume_issue)
        if vol_match:
            result["volume"] = f"{{{vol_match.group(1)}}}"
        
        # Extract number/issue
        num_match = re.search(r"number=(\d+)", volume_issue)
        if num_match:
            result["number"] = f"{{{num_match.group(1)}}}"
        
        return result
    
    def save_bibtex(self, output_file: pathlib.Path) -> pathlib.Path:
        """
        Save BibTeX entries to file.
        
        Args:
            output_file: Output file path
            
        Returns:
            Path to saved file
        """
        output_file = pathlib.Path(output_file)
        
        # Create header
        header = [
            "% BibTeX Bibliography File",
            "% Generated from OpenAlex publication data",
            f"% Generated: {datetime.now().isoformat()}",
            "% Author: Carlos Denner dos Santos",
            "% Total Entries: " + str(len(self.bibtex_entries)),
            "%",
            "% Usage in LaTeX:",
            "%   \\bibliography{publications}",
            "%   \\bibliographystyle{plain}",
            "%",
            "",
        ]
        
        # Combine header and entries
        content = "\n".join(header) + "\n" + "\n\n".join(self.bibtex_entries) + "\n"
        
        # Save
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(content)
        
        print(f"✅ BibTeX file saved: {output_file}")
        
        return output_file


def main():
    """Main BibTeX generation execution."""
    
    script_dir = pathlib.Path(__file__).parent
    
    # Load validated data
    validated_file = script_dir / "02_validated_works.json"
    
    if not validated_file.exists():
        print("❌ Validated works file not found. Run 02_validate_publications.py first.")
        return
    
    with open(validated_file, encoding="utf-8") as f:
        data = json.load(f)
        # Handle both list and dict formats
        if isinstance(data, dict):
            validated_works = data.get('works', [])
        else:
            validated_works = data
    
    # Deduplicate by title AND type (keep published over preprint, but keep different types)
    seen = {}  # key: (title_base, type), value: work
    duplicates_removed = 0
    
    for work in validated_works:
        title = work.get('title', '').lower().strip()
        work_type = work.get('type', '')
        # Normalize: remove (preprint), special chars, extra spaces
        title_base = ' '.join(title.replace('(preprint)', '').split())
        
        if not title_base:
            continue
        
        # Use both title AND type as key - this allows article + dataset with same title
        dedup_key = (title_base, work_type)
        
        # Use both title AND type as key - this allows article + dataset with same title
        dedup_key = (title_base, work_type)
        
        if dedup_key in seen:
            # Duplicate found - prioritize: published DOI > preprint DOI > first
            existing = seen[dedup_key]
            existing_doi = existing.get('doi', '') or ''
            work_doi = work.get('doi', '') or ''
            
            # Prefer non-preprint DOI over preprint DOI
            existing_is_preprint = 'preprint' in existing_doi.lower()
            work_is_preprint = 'preprint' in work_doi.lower()
            
            if work_doi and (not existing_doi or (existing_is_preprint and not work_is_preprint)):
                # New one is better (has DOI when existing doesn't, or published when existing is preprint)
                seen[dedup_key] = work
            
            duplicates_removed += 1
        else:
            seen[dedup_key] = work
    
    deduplicated_works = list(seen.values())
    
    if duplicates_removed > 0:
        print(f"🔄 Removed {duplicates_removed} duplicate entries (by title + DOI)")
    
    validated_works = deduplicated_works
    
    print("=" * 70)
    print("STAGE 3: BibTeX Generation")
    print("=" * 70)
    
    # Generate BibTeX
    generator = BibTeXGenerator(validated_works)
    generator.generate_bibtex_entries()
    
    # Save to output directory
    output_file = script_dir.parent / "publications.bib"
    generator.save_bibtex(output_file)
    
    # Print summary
    print("\n" + "=" * 70)
    print("BIBTEX GENERATION SUMMARY")
    print("=" * 70)
    print(f"Total Entries Generated: {len(generator.bibtex_entries)}")
    print(f"Output File: {output_file}")
    print(f"\nEntry Types Generated:")
    for key, count in sorted(generator.generation_stats.items()):
        if key.startswith("type_"):
            pub_type = key.replace("type_", "")
            print(f"  {pub_type}: {count}")
    
    print(f"\nFirst 5 entries (key names):")
    for entry in generator.bibtex_entries[:5]:
        # Extract citation key
        match = re.search(r"@\w+\{([^,]+)", entry)
        if match:
            print(f"  - {match.group(1)}")
    
    print("\n✅ Stage 3 complete! BibTeX ready for use.")
    print(f"Use in your LaTeX files: \\bibliography{{{{publications}}}}")
    print(f"Add to preamble: \\bibliographystyle{{{{plain}}}}")


if __name__ == "__main__":
    main()
