"""
Parse existing CV markdown file to extract structured information.
This provides a baseline CV structure that can be merged with other sources.
"""
import json
import pathlib
import re
import yaml


def parse_cv_markdown(md_path: str) -> dict:
    """
    Parse markdown CV and extract sections.
    Returns structured data similar to lattes_comprehensive format.
    """
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    cv_data = {
        'source': 'markdown_cv',
        'sections': {},
        'raw_content': content
    }
    
    # Split by markdown headers
    sections = re.split(r'\n##\s+', content)
    
    for section in sections:
        if not section.strip():
            continue
        
        lines = section.split('\n', 1)
        if len(lines) == 2:
            title = lines[0].strip()
            content = lines[1].strip()
            cv_data['sections'][title] = content
    
    return cv_data


def main():
    # Load configuration
    cfg = yaml.safe_load(open("profiles.yaml"))
    md_file = pathlib.Path(cfg.get("cv_markdown", "data/raw/cv_markdown.md"))
    
    if not md_file.exists():
        print(f"Markdown CV file not found: {md_file}")
        print("Skipping markdown CV import.")
        # Create empty output to prevent pipeline errors
        output = pathlib.Path("data/processed/cv_markdown.json")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text("{}", encoding='utf-8')
        return
    
    print("Parsing markdown CV...")
    cv_data = parse_cv_markdown(str(md_file))
    
    # Save parsed data
    output = pathlib.Path("data/processed/cv_markdown.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(cv_data, ensure_ascii=False, indent=2), encoding='utf-8')
    
    print(f"\n✓ Markdown CV parsed successfully!")
    print(f"  → Sections found: {len(cv_data['sections'])}")
    for section_name in cv_data['sections'].keys():
        print(f"    • {section_name}")
    print(f"\n  Saved to: {output}")


if __name__ == "__main__":
    main()
