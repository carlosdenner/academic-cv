#!/usr/bin/env python3
"""
Consolidate all CV data sources into a unified JSON file for web rendering.
"""
import json
from pathlib import Path
import yaml

def load_json(filepath):
    """Load JSON file safely."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"⚠️  Warning: {filepath} not found, skipping")
        return None
    except json.JSONDecodeError as e:
        print(f"⚠️  Warning: {filepath} has invalid JSON: {e}")
        return None

def translate_position_title(title_pt):
    """Translate Portuguese position titles to English."""
    translations = {
        # Academic positions
        "Professor Associado": "Associate Professor",
        "Professor Adjunto": "Adjunct Professor",
        "Professor Visitante": "Visiting Professor",
        "Pesquisador": "Researcher",
        "Pesquisador Associado": "Research Associate",
        "Pós-Doutorado": "Postdoctoral Researcher",
        "Diretor": "Director",
        "Diretor Adjunto": "Associate Director",
        "Coordenador": "Coordinator",
        
        # Consulting/Industry
        "Consultor": "Consultant",
        "Cientista de Dados": "Data Scientist",
        "Analista": "Analyst",
        "Especialista": "Specialist",
    }
    
    # Try exact match first
    if title_pt in translations:
        return translations[title_pt]
    
    # Try partial matches
    for pt, en in translations.items():
        if pt.lower() in title_pt.lower():
            return title_pt.replace(pt, en)
    
    return title_pt  # Return original if no translation found

def translate_institution(inst_pt):
    """Translate Portuguese institution names to English."""
    translations = {
        "Universidade de Brasília": "University of Brasilia",
        "Universidade de São Paulo": "University of Sao Paulo",
        "Universidade Federal": "Federal University",
        "Universidade Estadual": "State University",
        "Ministério": "Ministry",
        "Tribunal de Contas": "Court of Accounts",
    }
    
    for pt, en in translations.items():
        if pt in inst_pt:
            inst_pt = inst_pt.replace(pt, en)
    
    return inst_pt

def load_profiles():
    """Load profiles.yaml for contact info."""
    with open('profiles.yaml', 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def consolidate_cv():
    """Merge all CV data sources."""
    
    # Load all data sources
    works = load_json('data/processed/works_merged.json') or []
    lattes = load_json('data/processed/lattes_comprehensive.json') or {}
    cv_markdown = load_json('data/processed/cv_markdown.json') or {}
    videns_exp = load_json('data/processed/videns_experience.json')
    profiles = load_profiles()
    
    # Extract contact info from profiles
    contact_info = {
        "name": lattes.get('personal_info', {}).get('name', 'Carlos Denner dos Santos Jr.'),
        "orcid": profiles.get('orcid_id', ''),
        "email": "carlosdenner@gmail.com",
        "phone": "(438) 836-4116",
        "emails": [
            {"type": "Personal", "address": "carlosdenner@gmail.com"},
            {"type": "UnB", "address": "carlosdenner@unb.br"},
            {"type": "Bell Canada", "address": "carlos.denner@bell.ca"},
            {"type": "USherbrooke", "address": "carlos.denner.dos.santos.junior@usherbrooke.ca"}
        ],
        "profiles": {
            "github": "https://github.com/carlosdenner",
            "linkedin": "https://www.linkedin.com/in/carlosdenner",
            "google_scholar": "https://scholar.google.com/citations?user=YOUR_ID",
            "researchgate": "https://www.researchgate.net/profile/Carlos-Denner-Dos-Santos"
        }
    }
    
    # Professional summary
    summary = {
        "text": cv_markdown.get('sections', {}).get('## [CARLOSDENNER@GMAIL.COM](mailto:CARLOSDENNER@GMAIL.COM), (438) 836-4116', ''),
        "short": "Information systems researcher, university professor, and data science consultant with 20+ years experience in decision support systems, open source software, and AI governance."
    }
    
    # Education
    education = lattes.get('education', [])
    
    # Professional positions - consolidate from multiple sources
    all_positions = []
    
    # 1. From Lattes (most comprehensive for academic positions)
    lattes_positions = lattes.get('positions', [])
    for pos in lattes_positions:
        # Translate and enrich
        position = {
            "role": translate_position_title(pos.get('role', pos.get('title', ''))),
            "role_original": pos.get('role', pos.get('title', '')),
            "institution": translate_institution(pos.get('institution', '')),
            "institution_original": pos.get('institution', ''),
            "type": pos.get('type', 'Academic'),
            "start_year": pos.get('start_year', ''),
            "start_month": pos.get('start_month', ''),
            "end_year": pos.get('end_year', ''),
            "end_month": pos.get('end_month', ''),
            "hours_per_week": pos.get('hours_per_week', ''),
            "description": pos.get('description', ''),
            "location": pos.get('location', 'Brazil')
        }
        all_positions.append(position)
    
    # 2. From CV Markdown (for recent consulting positions 2019-2021)
    # Parse the RESEARCH, SERVICE EXPERIENCE section
    if cv_markdown.get('sections'):
        # Add Bell Canada (from CV markdown)
        all_positions.append({
            "role": "Data Scientist Consultant",
            "role_original": "Data Scientist Consultant",
            "institution": "Bell Canada",
            "institution_original": "Bell Canada",
            "type": "Consulting",
            "start_year": "2021",
            "start_month": "11",
            "end_year": "2025",  # Overlaps with Videns
            "end_month": None,
            "hours_per_week": "",
            "description": "Data analytics and visualization for 5G migration, IoT, big data (Hadoop, MongoDB), AI for management automation",
            "location": "Montreal, Canada"
        })
        
        # Add Jooay App (from CV markdown)
        all_positions.append({
            "role": "Co-Principal Investigator",
            "role_original": "Co-Principal Investigator",
            "institution": "Jooay App, McGill University",
            "institution_original": "Jooay App, McGill University",
            "type": "Research",
            "start_year": "2020",
            "start_month": "02",
            "end_year": None,
            "end_month": None,
            "hours_per_week": "",
            "description": "Data analytics and visualization, content management systems for accessibility app",
            "location": "Montreal, Canada"
        })
    
    # 3. Add Videns experience (2025 - current)
    if videns_exp:
        all_positions.append({
            "role": videns_exp.get('role', 'AI Expert'),
            "role_original": videns_exp.get('role', 'AI Expert'),
            "institution": videns_exp.get('institution', 'Videns Analytics'),
            "institution_original": videns_exp.get('institution', 'Videns Analytics'),
            "type": videns_exp.get('type', 'Consulting'),
            "start_year": videns_exp.get('start_year', '2025'),
            "start_month": videns_exp.get('start_month', '07'),
            "end_year": videns_exp.get('end_year'),
            "end_month": videns_exp.get('end_month'),
            "hours_per_week": "",
            "description": videns_exp.get('description', ''),
            "location": videns_exp.get('location', 'Montreal, Canada'),
            "projects": videns_exp.get('projects', []),
            "technologies": videns_exp.get('technologies', []),
            "achievements": videns_exp.get('achievements', [])
        })
    
    # Sort positions by date (most recent first)
    def position_sort_key(pos):
        year = int(pos.get('start_year') or 0)
        month = int(pos.get('start_month') or 1)
        return (year, month)
    
    all_positions.sort(key=position_sort_key, reverse=True)
    
    positions = all_positions
    
    # Research projects
    projects = lattes.get('projects', [])
    
    # Academic supervisions
    supervisions = lattes.get('supervisions', [])
    
    # Awards and honors
    awards = lattes.get('awards', [])
    
    # Research areas
    research_areas = lattes.get('research_areas', [])
    
    # Languages
    languages = lattes.get('languages', [])
    
    # Publications - categorize by type
    publications = {
        "journal_articles": [],
        "book_chapters": [],
        "conference_papers": [],
        "technical": []
    }
    
    for work in works:
        pub_type = work.get('type', '').lower()
        
        # Determine category
        if 'journal' in pub_type or 'article' in pub_type:
            category = 'journal_articles'
        elif 'book' in pub_type or 'chapter' in pub_type:
            category = 'book_chapters'
        elif pub_type in ['dataset', 'software', 'other']:
            category = 'technical'
        else:
            category = 'conference_papers'
        
        publications[category].append({
            "title": work.get('title', ''),
            "authors": work.get('authors', ''),
            "year": work.get('year'),
            "venue": work.get('venue', ''),
            "type": work.get('type', ''),
            "doi": work.get('doi', ''),
            "url": work.get('url', ''),
            "citations": work.get('citations', 0),
            "abstract": work.get('abstract', ''),
            "funders": work.get('funders', [])
        })
    
    # Sort publications by year (descending)
    for category in publications:
        publications[category].sort(key=lambda x: (x.get('year') or 0), reverse=True)
    
    # Calculate metrics
    total_citations = sum(work.get('citations', 0) for work in works if work.get('citations'))
    publications_with_citations = [w.get('citations', 0) for w in works if w.get('citations', 0) > 0]
    publications_with_citations.sort(reverse=True)
    
    # Calculate h-index
    h_index = 0
    for i, citations in enumerate(publications_with_citations, start=1):
        if citations >= i:
            h_index = i
        else:
            break
    
    metrics = {
        "total_publications": len(works),
        "journal_articles": len(publications['journal_articles']),
        "conference_papers": len(publications['conference_papers']),
        "book_chapters": len(publications['book_chapters']),
        "technical_outputs": len(publications['technical']),
        "total_citations": total_citations,
        "h_index": h_index,
        "with_doi": sum(1 for w in works if w.get('doi')),
        "with_abstract": sum(1 for w in works if w.get('abstract')),
        "phd_supervised": len([s for s in supervisions if 'PhD' in s.get('level', '')]),
        "masters_supervised": len([s for s in supervisions if 'Masters' in s.get('level', '')]),
        "projects_led": len(projects),
        "years_active": 2025 - 2003  # From first MSc to now
    }
    
    # Consolidate everything
    cv_data = {
        "contact": contact_info,
        "summary": summary,
        "metrics": metrics,
        "education": education,
        "positions": positions,
        "publications": publications,
        "projects": projects,
        "supervisions": supervisions,
        "awards": awards,
        "research_areas": research_areas,
        "languages": languages,
        "generated": "2025-11-11"
    }
    
    # Save consolidated data
    output_path = Path('data/processed/cv_data.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(cv_data, f, indent=2, ensure_ascii=False)
    
    # Also copy to docs folder for website
    docs_path = Path('docs/cv_data.json')
    with open(docs_path, 'w', encoding='utf-8') as f:
        json.dump(cv_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Consolidated CV data saved to: {output_path}")
    print(f"✅ Website data copied to: {docs_path}")
    print(f"\n📊 CV Statistics:")
    print(f"   Education degrees: {len(education)}")
    print(f"   Positions: {len(positions)}")
    print(f"   Total publications: {metrics['total_publications']}")
    print(f"   - Journal articles: {metrics['journal_articles']}")
    print(f"   - Conference papers: {metrics['conference_papers']}")
    print(f"   - Book chapters: {metrics['book_chapters']}")
    print(f"   - Technical outputs: {metrics['technical_outputs']}")
    print(f"   Total citations: {metrics['total_citations']}")
    print(f"   h-index: {metrics['h_index']}")
    print(f"   Research projects: {metrics['projects_led']}")
    print(f"   PhD supervised: {metrics['phd_supervised']}")
    print(f"   Masters supervised: {metrics['masters_supervised']}")
    print(f"   Awards: {len(awards)}")

if __name__ == '__main__':
    consolidate_cv()
