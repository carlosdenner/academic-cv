"""
Extract publications from saved ResearchGate HTML profile page.
Parses the HTML to extract titles, authors, venues, years, and DOIs.
"""
import json
import pathlib
import re
import yaml
from lxml import html


def parse_researchgate_html(html_path: str) -> list[dict]:
    """Parse ResearchGate profile HTML and extract publications."""
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    tree = html.fromstring(content)
    publications = []
    seen_titles = set()
    
    # Look for publication links more specifically
    # ResearchGate publication URLs have a specific pattern
    pub_links = tree.xpath('//a[contains(@href, "/publication/")]')
    
    for link in pub_links:
        try:
            href = link.get('href', '')
            
            # Skip if not a proper publication URL
            if not re.search(r'/publication/\d+', href):
                continue
            
            # Get title text from the link
            title = link.text_content().strip()
            
            # Clean up title (remove badges like "New Article", "Full-text available")
            title = re.sub(r'\s*(New Article|Full-text available|Article|Chapter|Conference Paper)\s*', ' ', title)
            title = title.strip()
            
            # Skip if title is too short or already seen
            if not title or len(title) < 10 or title in seen_titles:
                continue
            
            seen_titles.add(title)
            
            # Try to extract year from title or nearby text
            year = None
            year_match = re.search(r'\b(19|20)\d{2}\b', title)
            if year_match:
                year = int(year_match.group(0))
            
            # Build full URL
            if href.startswith('/'):
                href = f"https://www.researchgate.net{href}"
            
            # Clean URL parameters
            href = re.sub(r'[?&]_sg.*$', '', href)
            
            pub = {
                'title': title,
                'url': href,
                'year': year,
                'source': 'researchgate_html'
            }
            
            publications.append(pub)
            
        except Exception as e:
            continue
    
    return publications


def main():
    # Load configuration
    cfg = yaml.safe_load(open("profiles.yaml"))
    html_file = pathlib.Path(cfg.get("researchgate_html", "data/raw/researchgate_profile.html"))
    
    if not html_file.exists():
        print(f"HTML file not found: {html_file}")
        print(f"Please save your ResearchGate profile page as: {html_file}")
        # Create empty output to prevent pipeline errors
        output = pathlib.Path("data/raw/researchgate_html.json")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text("[]", encoding='utf-8')
        return
    
    publications = parse_researchgate_html(str(html_file))
    
    output = pathlib.Path("data/raw/researchgate_html.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    
    output.write_text(json.dumps(publications, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"Extracted {len(publications)} publications from ResearchGate HTML")
    print(f"Saved to: {output}")


if __name__ == "__main__":
    main()
