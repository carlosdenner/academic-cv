"""
Extract publications from saved Google Scholar HTML profile page.
Parses the HTML to extract titles, authors, venues, years, and citations.
"""
import json
import pathlib
import re
import yaml
from lxml import html


def parse_scholar_html(html_path: str) -> list[dict]:
    """Parse Google Scholar profile HTML and extract publications."""
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    tree = html.fromstring(content)
    publications = []
    
    # Find all publication rows in the table
    rows = tree.xpath('//tr[@class="gsc_a_tr"]')
    
    for row in rows:
        try:
            # Extract title and link
            title_elem = row.xpath('.//a[@class="gsc_a_at"]')
            if not title_elem:
                continue
            
            title = title_elem[0].text_content().strip()
            link = title_elem[0].get('href', '')
            
            # Extract authors and venue from gray text divs
            gray_divs = row.xpath('.//div[@class="gs_gray"]')
            authors = gray_divs[0].text_content().strip() if len(gray_divs) > 0 else ""
            venue_year = gray_divs[1].text_content().strip() if len(gray_divs) > 1 else ""
            
            # Parse venue and year
            venue = venue_year
            year = None
            year_match = re.search(r'(\d{4})', venue_year)
            if year_match:
                year = int(year_match.group(1))
                venue = venue_year[:year_match.start()].strip().rstrip(',')
            
            # Extract citation count
            citations_elem = row.xpath('.//a[@class="gsc_a_ac gs_ibl"]')
            citations = 0
            if citations_elem and citations_elem[0].text_content().strip():
                try:
                    citations = int(citations_elem[0].text_content().strip())
                except ValueError:
                    citations = 0
            
            # Extract year from separate column if not found
            if not year:
                year_elem = row.xpath('.//span[@class="gsc_a_h gsc_a_hc gs_ibl"]')
                if year_elem and year_elem[0].text_content().strip():
                    try:
                        year = int(year_elem[0].text_content().strip())
                    except ValueError:
                        pass
            
            pub = {
                'title': title,
                'authors': authors,
                'venue': venue if venue else None,
                'year': year,
                'citations': citations,
                'url': f"https://scholar.google.com{link}" if link.startswith('/') else link,
                'source': 'google_scholar_html'
            }
            
            publications.append(pub)
            
        except Exception as e:
            print(f"Error parsing row: {e}")
            continue
    
    return publications


def main():
    # Load configuration
    cfg = yaml.safe_load(open("profiles.yaml"))
    html_file = pathlib.Path(cfg.get("scholar_html", "data/raw/scholar_profile.html"))
    
    if not html_file.exists():
        print(f"HTML file not found: {html_file}")
        print(f"Please save your Google Scholar profile page as: {html_file}")
        # Create empty output to prevent pipeline errors
        output = pathlib.Path("data/raw/scholar_html.json")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text("[]", encoding='utf-8')
        return
    
    publications = parse_scholar_html(str(html_file))
    
    output = pathlib.Path("data/raw/scholar_html.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    
    output.write_text(json.dumps(publications, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"Extracted {len(publications)} publications from Google Scholar HTML")
    print(f"Saved to: {output}")


if __name__ == "__main__":
    main()
