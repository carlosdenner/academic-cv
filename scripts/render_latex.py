"""
Render comprehensive LaTeX CV from consolidated cv_data.json
Supports both Awesome-CV and ModernCV templates
"""
import json
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from datetime import datetime

def load_cv_data():
    """Load consolidated CV data"""
    data_path = Path('data/processed/cv_data.json')
    with open(data_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_openalex_data():
    """Load OpenAlex works for bibliographic details"""
    data_path = Path('data/processed/openalex_works.json')
    with open(data_path, 'r', encoding='utf-8') as f:
        works = json.load(f)
    # Create a lookup by DOI
    lookup = {}
    for work in works:
        doi = work.get('doi', '')
        if doi:
            lookup[doi] = work
    return lookup

def escape_latex(text):
    """Escape special LaTeX characters"""
    if not text:
        return ""
    # Replace problematic patterns first
    text = text.replace('\\n', ' ')  # Literal \n in JSON
    text = text.replace('\n', ' ')   # Actual newline
    text = text.replace('\r', '')
    
    replacements = {
        '&': '\\&',
        '%': '\\%',
        '$': '\\$',
        '#': '\\#',
        '_': '\\_',
        '{': '\\{',
        '}': '\\}',
        '~': '\\textasciitilde{}',
        '^': '\\textasciicircum{}',
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text

def format_date_range(start_year, start_month, end_year, end_month):
    """Format date range for LaTeX"""
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    # Convert to int if string
    if start_month and isinstance(start_month, str):
        start_month = int(start_month) if start_month.isdigit() else None
    if end_month and isinstance(end_month, str):
        end_month = int(end_month) if end_month.isdigit() else None
    if start_year and isinstance(start_year, str):
        start_year = int(start_year) if start_year.isdigit() else None
    if end_year and isinstance(end_year, str):
        end_year = int(end_year) if end_year.isdigit() else None
    
    start = f"{months[start_month-1] if start_month else ''} {start_year}" if start_year else ""
    
    if end_year and end_year != 9999:
        end = f"{months[end_month-1] if end_month else ''} {end_year}"
    else:
        end = "Present"
    
    if start and end:
        return f"{start} -- {end}"
    return start or end or ""

def group_publications_by_type(publications):
    """Group publications by type for organized display"""
    groups = {
        'Journal Articles': [],
        'Conference Papers': [],
        'Book Chapters': [],
        'Technical Reports': [],
        'Other': []
    }
    
    type_mapping = {
        'journal-article': 'Journal Articles',
        'proceedings-article': 'Conference Papers',
        'book-chapter': 'Book Chapters',
        'report': 'Technical Reports',
        'dataset': 'Technical Reports',
    }
    
    for pub in publications:
        pub_type = pub.get('type', 'other')
        group = type_mapping.get(pub_type, 'Other')
        groups[group].append(pub)
    
    # Remove empty groups
    return {k: v for k, v in groups.items() if v}

def prepare_template_data(cv_data):
    """Prepare CV data for template rendering"""
    
    # Contact info
    contact = {
        'name_first': 'Carlos Denner',
        'name_last': 'dos Santos Jr.',
        'email': 'carlosdenner@gmail.com',
        'phone': '+1 438-836-4116',
        'location': 'Montréal, QC, Canada',
        'website': 'datasciencetech.ca',
        'linkedin': 'linkedin.com/in/carlosdenner',
        'orcid': '0000-0002-1783-7896'
    }
    
    # Education
    education = []
    for degree in cv_data.get('education', []):
        # Determine degree name and field
        level = degree.get('level', '')
        course = degree.get('course', '')
        degree_name = level
        field = course if course else ''
        
        # Build more descriptive degree name
        if level in ['PhD', 'Post-doc']:
            degree_name = f"{level}"
        elif level == 'Masters':
            degree_name = "Master's Degree"
        elif level == 'Bachelor':
            degree_name = "Bachelor's Degree"
        
        education.append({
            'degree': escape_latex(degree_name),
            'institution': escape_latex(degree.get('institution', '')),
            'location': escape_latex(degree.get('location', '')),
            'date': format_date_range(
                degree.get('start_year'), None,
                degree.get('end_year'), None
            ),
            'field': escape_latex(field),
            'thesis': escape_latex(degree.get('thesis', ''))
        })
    
    # Professional Experience
    positions = []
    for pos in cv_data.get('positions', []):
        position = {
            'role': escape_latex(pos.get('role', '')),
            'institution': escape_latex(pos.get('institution', '')),
            'location': escape_latex(pos.get('location', '')),
            'date': format_date_range(
                pos.get('start_year'), pos.get('start_month'),
                pos.get('end_year'), pos.get('end_month')
            ),
            'type': pos.get('type', 'Academic'),
            'description': escape_latex(pos.get('description', '')),
            'projects': []
        }
        
        # Add projects for consulting positions
        if 'projects' in pos and pos['projects']:
            for proj in pos['projects'][:3]:  # Limit to top 3 projects for space
                project = {
                    'name': escape_latex(proj.get('name', '')),
                    'client': escape_latex(proj.get('client', '')),
                    'description': escape_latex(proj.get('description', ''))[:200],  # Truncate
                    'deliverables': [escape_latex(d) for d in proj.get('deliverables', [])[:3]]
                }
                position['projects'].append(project)
        
        positions.append(position)
    
    # Publications
    publications = {}
    pubs_data = cv_data.get('publications', {})
    
    # Load OpenAlex data for bibliographic details
    openalex_lookup = load_openalex_data()
    
    # Map from cv_data.json structure to display names
    pub_categories = {
        'journal_articles': 'Journal Articles',
        'conference_papers': 'Conference Papers',
        'book_chapters': 'Book Chapters',
        'technical_reports': 'Technical Reports'
    }
    
    for key, display_name in pub_categories.items():
        if key in pubs_data and pubs_data[key]:
            publications[display_name] = []
            # Include ALL publications, not just top 20
            for pub in pubs_data[key]:
                # Skip publications that are not mine
                title = pub.get('title', '')
                if 'Ralstonia syzygii' in title or 'Eucalyptus in Brazil' in title:
                    continue  # Skip this publication
                
                # Handle authors - might be string or list
                authors = pub.get('authors', '')
                if isinstance(authors, list):
                    authors_str = ', '.join(authors)
                else:
                    authors_str = str(authors)
                
                # Clean DOI URL
                doi = pub.get('doi', '')
                if doi and not doi.startswith('http'):
                    doi = f'https://doi.org/{doi}'
                
                # Get bibliographic details from OpenAlex
                volume = None
                issue = None
                pages = None
                if doi and doi in openalex_lookup:
                    biblio = openalex_lookup[doi].get('biblio', {})
                    volume = biblio.get('volume')
                    issue = biblio.get('issue')
                    first_page = biblio.get('first_page')
                    last_page = biblio.get('last_page')
                    if first_page and last_page and first_page != last_page:
                        pages = f"{first_page}--{last_page}"
                    elif first_page:
                        pages = first_page
                
                pub_data = {
                    'title': escape_latex(pub.get('title', '')),
                    'authors': escape_latex(authors_str),
                    'venue': escape_latex(pub.get('venue', '')),
                    'year': pub.get('year', ''),
                    'doi': doi,  # Keep original DOI for href
                    'citations': pub.get('citations', 0),
                    'volume': volume,
                    'issue': issue,
                    'pages': pages
                }
                publications[display_name].append(pub_data)
    
    # Research Projects
    projects = []
    for proj in cv_data.get('research_projects', [])[:10]:  # Top 10 projects
        projects.append({
            'title': escape_latex(proj.get('title', '')),
            'role': escape_latex(proj.get('role', '')),
            'funder': escape_latex(proj.get('funder', proj.get('funding_source', ''))),
            'date': format_date_range(
                proj.get('start_year'), None,
                proj.get('end_year'), None
            ),
            'description': escape_latex(proj.get('description', ''))[:150]
        })
    
    # Supervisions
    supervisions = {
        'Postdoc': [],
        'PhD': [],
        'Masters': []
    }
    for sup in cv_data.get('supervisions', []):
        sup_data = {
            'student': escape_latex(sup.get('student_name', sup.get('student', ''))),
            'thesis': escape_latex(sup.get('thesis_title', sup.get('title', '')))[:100],
            'year': sup.get('completion_year', sup.get('year', '')),
            'status': sup.get('status', '')
        }
        level = sup.get('level', '').lower()
        if 'postdoc' in level or 'pós-doutorado' in level.lower() or 'pos-doutorado' in level.lower():
            supervisions['Postdoc'].append(sup_data)
        elif 'phd' in level or 'doutorado' in level:
            supervisions['PhD'].append(sup_data)
        elif 'master' in level or 'mestrado' in level:
            supervisions['Masters'].append(sup_data)
    
    # Awards
    awards = []
    for award in sorted(cv_data.get('awards', []), 
                       key=lambda x: x.get('year', 0), 
                       reverse=True):
        awards.append({
            'title': escape_latex(award.get('title', '')),
            'organization': escape_latex(award.get('organization', '')),
            'year': award.get('year', ''),
            'description': escape_latex(award.get('description', ''))[:100]
        })
    
    # Metrics summary
    pubs_data = cv_data.get('publications', {})
    total_pubs = sum(len(v) for v in pubs_data.values() if isinstance(v, list))
    
    metrics = {
        'publications': total_pubs,
        'journal_articles': len(pubs_data.get('journal_articles', [])),
        'conference_papers': len(pubs_data.get('conference_papers', [])),
        'book_chapters': len(pubs_data.get('book_chapters', [])),
        'citations': cv_data.get('metrics', {}).get('total_citations', 0),
        'h_index': cv_data.get('metrics', {}).get('h_index', 0),
        'supervised_postdoc': len(supervisions['Postdoc']),
        'supervised_phd': len(supervisions['PhD']),
        'supervised_masters': len(supervisions['Masters']),
        'projects': len(cv_data.get('research_projects', [])),
        'awards': len(awards)
    }
    
    return {
        'contact': contact,
        'education': education,
        'positions': positions,
        'publications': publications,
        'projects': projects,
        'supervisions': supervisions,
        'awards': awards,
        'metrics': metrics,
        'generated_date': datetime.now().strftime('%B %d, %Y')
    }

def render_template(template_name, data, output_path):
    """Render Jinja2 template with data"""
    env = Environment(
        loader=FileSystemLoader('templates'),
        trim_blocks=True,
        lstrip_blocks=True
    )
    
    template = env.get_template(template_name)
    rendered = template.render(**data)
    
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(rendered, encoding='utf-8')
    
    print(f"✅ LaTeX CV rendered: {output_path}")

def main():
    print("🔄 Loading CV data...")
    cv_data = load_cv_data()
    
    print("🔄 Preparing template data...")
    template_data = prepare_template_data(cv_data)
    
    print(f"\n📊 CV Summary:")
    print(f"   Education: {len(template_data['education'])} degrees")
    print(f"   Positions: {len(template_data['positions'])} positions")
    print(f"   Publications: {template_data['metrics']['publications']} total")
    for pub_type, pubs in template_data['publications'].items():
        print(f"     - {pub_type}: {len(pubs)}")
    print(f"   Research Projects: {len(template_data['projects'])}")
    print(f"   PhD Supervised: {template_data['metrics']['supervised_phd']}")
    print(f"   Masters Supervised: {template_data['metrics']['supervised_masters']}")
    print(f"   Awards: {len(template_data['awards'])}")
    
    print("\n🔄 Rendering Clean Publications CV template...")
    render_template('clean-publications.tex.j2', template_data, 'output/cv_publications.tex')
    
    print("\n✅ LaTeX rendering complete!")
    print("\n📝 To generate PDF:")
    print("   cd output")
    print("   xelatex cv_publications.tex")
    print("   xelatex cv_publications.tex  # Run twice for hyperlinks")

if __name__ == '__main__':
    main()
