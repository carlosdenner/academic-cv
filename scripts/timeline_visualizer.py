"""
Academic Career Timeline Visualization
Generates a visual timeline from lattes_comprehensive.json
"""
import json
import pathlib
from collections import defaultdict


def load_data():
    """Load comprehensive Lattes data."""
    data_file = pathlib.Path("data/processed/lattes_comprehensive.json")
    with open(data_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def print_timeline(cv_data):
    """Print a text-based timeline of academic career."""
    
    print("\n" + "="*80)
    print("ACADEMIC CAREER TIMELINE")
    print("="*80)
    
    # Education
    print("\n📚 EDUCATION")
    print("-" * 80)
    for edu in cv_data['education']:
        years = f"{edu['start_year']}-{edu['end_year']}"
        level = edu['level']
        institution = edu['institution']
        funding = f" 💰 {edu['funding_agency']}" if edu.get('scholarship') else ""
        print(f"  {years:12} {level:12} {institution[:40]}{funding}")
    
    # Major Positions
    print("\n💼 PROFESSIONAL POSITIONS (Selected)")
    print("-" * 80)
    
    # Group by institution
    positions_by_inst = defaultdict(list)
    for pos in cv_data['positions']:
        key = pos['institution']
        positions_by_inst[key].append(pos)
    
    # Show only major academic positions
    major_institutions = ['Universidade Federal de Minas Gerais', 
                         'Southern Illinois University Carbondale',
                         'Universidade de São Paulo',
                         'University of Nottingham',
                         'Universidade de Brasília',
                         'Universidade Federal de Pernambuco',
                         'Université du Quebec à Montréal',
                         'Videns AI']
    
    for inst in major_institutions:
        if inst in positions_by_inst:
            positions = positions_by_inst[inst]
            # Get earliest and latest dates
            start_years = [p['start_year'] for p in positions if p['start_year']]
            end_years = [p['end_year'] for p in positions if p['end_year']]
            
            if start_years:
                earliest = min(start_years)
                latest = max(end_years) if end_years else "present"
                years = f"{earliest}-{latest}"
                # Get position types
                roles = list(set([p['position'] for p in positions if p['position']]))
                role_str = roles[0][:40] if roles else "Multiple roles"
                print(f"  {years:12} {inst[:40]:40} → {role_str}")
    
    # Projects with funding
    print("\n🔬 MAJOR FUNDED PROJECTS")
    print("-" * 80)
    for proj in cv_data['projects']:
        if proj['funding_agencies']:
            years = f"{proj['start_year']}-{proj['end_year']}"
            title = proj['title'][:50]
            agencies = ', '.join([f['name'][:20] for f in proj['funding_agencies'] if f['name']])
            if agencies:
                print(f"  {years:12} {title:50} 💰 {agencies}")
    
    # Supervisions
    print("\n👨‍🎓 STUDENT SUPERVISIONS")
    print("-" * 80)
    
    phd_completed = [s for s in cv_data['supervisions'] if s['level'] == 'PhD' and s['status'] == 'Completed']
    phd_ongoing = [s for s in cv_data['supervisions'] if s['level'] == 'PhD' and s['status'] == 'Ongoing']
    masters_completed = [s for s in cv_data['supervisions'] if s['level'] == 'Masters' and s['status'] == 'Completed']
    masters_ongoing = [s for s in cv_data['supervisions'] if s['level'] == 'Masters' and s['status'] == 'Ongoing']
    
    print(f"  PhD Completed:        {len(phd_completed)}")
    print(f"  PhD Ongoing:          {len(phd_ongoing)}")
    print(f"  Masters Completed:    {len(masters_completed)}")
    print(f"  Masters Ongoing:      {len(masters_ongoing)}")
    print(f"  TOTAL:                {len(cv_data['supervisions'])} students")
    
    # Latest supervisions
    print("\n  Recent PhD Supervisions:")
    for s in sorted(phd_completed, key=lambda x: x['year'], reverse=True)[:3]:
        print(f"    {s['year']} - {s['student']} - {s['title'][:60]}")
    
    # Awards
    print("\n🏆 AWARDS & HONORS")
    print("-" * 80)
    for award in sorted(cv_data['awards'], key=lambda x: x['year'], reverse=True):
        print(f"  {award['year']:12} {award['title'][:50]:50} - {award['institution'][:30]}")
    
    # Research Areas
    print("\n🎯 RESEARCH AREAS")
    print("-" * 80)
    for area in cv_data['research_areas']:
        if area['specialty']:
            print(f"  • {area['major_area']} → {area['area']} → {area['specialty']}")
        elif area['subarea']:
            print(f"  • {area['major_area']} → {area['area']} → {area['subarea']}")
        else:
            print(f"  • {area['major_area']} → {area['area']}")
    
    # Languages
    print("\n🌐 LANGUAGES")
    print("-" * 80)
    for lang in cv_data['languages']:
        proficiency = f"Read: {lang['reading']}, Speak: {lang['speaking']}, Write: {lang['writing']}"
        print(f"  • {lang['language']:15} - {proficiency}")
    
    # Summary Stats
    print("\n📊 CAREER SUMMARY")
    print("-" * 80)
    print(f"  Education:           {len(cv_data['education'])} degrees (1 Bachelor, 1 Masters, 1 PhD, 4 Post-docs)")
    print(f"  Positions:           {len(cv_data['positions'])} professional positions")
    print(f"  Projects:            {len(cv_data['projects'])} research projects")
    print(f"  Supervisions:        {len(cv_data['supervisions'])} students (PhD + Masters)")
    print(f"  Awards:              {len(cv_data['awards'])} honors")
    print(f"  Research Areas:      {len(cv_data['research_areas'])} areas")
    print(f"  Languages:           {len(cv_data['languages'])} languages")
    print(f"  Teaching:            {len(cv_data['teaching'])} courses")
    
    # Funding summary
    funding_agencies = set()
    for proj in cv_data['projects']:
        for f in proj['funding_agencies']:
            if f['name']:
                funding_agencies.add(f['name'])
    for edu in cv_data['education']:
        if edu.get('funding_agency'):
            funding_agencies.add(edu['funding_agency'])
    
    print(f"\n  Funding Agencies:    {len(funding_agencies)} agencies")
    print(f"    • {', '.join(sorted(funding_agencies)[:5])}")
    
    print("\n" + "="*80)


def main():
    cv_data = load_data()
    print_timeline(cv_data)


if __name__ == "__main__":
    main()
