"""
Comprehensive Lattes XML parser - extracts ALL academic information.
Extracts: education, positions, projects, supervision, committees, awards, etc.
"""
import json
import pathlib
import yaml
from lxml import etree


def parse_lattes_comprehensive(xml_path: str) -> dict:
    """
    Parse complete Lattes CV XML and extract all academic information.
    Returns a comprehensive dictionary with all CV sections.
    """
    tree = etree.parse(xml_path)
    root = tree.getroot()
    
    cv_data = {
        'personal_info': extract_personal_info(root),
        'education': extract_education(root),
        'positions': extract_positions(root),
        'research_areas': extract_research_areas(root),
        'languages': extract_languages(root),
        'awards': extract_awards(root),
        'projects': extract_projects(root),
        'supervisions': extract_supervisions(root),
        'committee_participation': extract_committees(root),
        'event_organization': extract_event_organization(root),
        'editorial_activities': extract_editorial(root),
        'teaching': extract_teaching(root),
    }
    
    return cv_data


def extract_personal_info(root):
    """Extract personal information."""
    dados = root.find('.//DADOS-GERAIS')
    if dados is None:
        return {}
    
    return {
        'name': dados.get('NOME-COMPLETO', ''),
        'citation_names': dados.get('NOME-EM-CITACOES-BIBLIOGRAFICAS', '').split(';'),
        'orcid': dados.get('ORCID-ID', ''),
        'nationality': dados.get('NACIONALIDADE', ''),
        'cpf': dados.get('CPF', ''),
        'passport': dados.get('NUMERO-DO-PASSAPORTE', ''),
        'researcher_id': dados.get('NUMERO-IDENTIFICADOR', ''),
        'summary': dados.get('TEXTO-RESUMO-CV-RH', ''),
        'summary_en': dados.get('TEXTO-RESUMO-CV-RH-EN', '')
    }


def extract_education(root):
    """Extract academic education."""
    education = []
    
    # Graduation
    for grad in root.findall('.//GRADUACAO'):
        education.append({
            'level': 'Bachelor',
            'institution': grad.get('NOME-INSTITUICAO', ''),
            'course': grad.get('NOME-CURSO', ''),
            'status': grad.get('STATUS-DO-CURSO', ''),
            'start_year': grad.get('ANO-DE-INICIO', ''),
            'end_year': grad.get('ANO-DE-CONCLUSAO', ''),
            'thesis': grad.get('TITULO-DO-TRABALHO-DE-CONCLUSAO-DE-CURSO', ''),
            'advisor': grad.get('NOME-DO-ORIENTADOR', '')
        })
    
    # Masters
    for mestrado in root.findall('.//MESTRADO'):
        education.append({
            'level': 'Masters',
            'institution': mestrado.get('NOME-INSTITUICAO', ''),
            'course': mestrado.get('NOME-CURSO', ''),
            'status': mestrado.get('STATUS-DO-CURSO', ''),
            'start_year': mestrado.get('ANO-DE-INICIO', ''),
            'end_year': mestrado.get('ANO-DE-CONCLUSAO', ''),
            'thesis': mestrado.get('TITULO-DA-DISSERTACAO-TESE', ''),
            'advisor': mestrado.get('NOME-DO-ORIENTADOR', ''),
            'scholarship': mestrado.get('FLAG-BOLSA', '') == 'SIM',
            'funding_agency': mestrado.get('NOME-AGENCIA', '')
        })
    
    # PhD
    for doutorado in root.findall('.//DOUTORADO'):
        education.append({
            'level': 'PhD',
            'institution': doutorado.get('NOME-INSTITUICAO', ''),
            'course': doutorado.get('NOME-CURSO', ''),
            'status': doutorado.get('STATUS-DO-CURSO', ''),
            'start_year': doutorado.get('ANO-DE-INICIO', ''),
            'end_year': doutorado.get('ANO-DE-CONCLUSAO', ''),
            'thesis': doutorado.get('TITULO-DA-DISSERTACAO-TESE', ''),
            'advisor': doutorado.get('NOME-DO-ORIENTADOR', ''),
            'scholarship': doutorado.get('FLAG-BOLSA', '') == 'SIM',
            'funding_agency': doutorado.get('NOME-AGENCIA', '')
        })
    
    # Post-doc
    for posdoc in root.findall('.//POS-DOUTORADO'):
        education.append({
            'level': 'Post-doc',
            'institution': posdoc.get('NOME-INSTITUICAO', ''),
            'status': posdoc.get('STATUS-DO-CURSO', ''),
            'start_year': posdoc.get('ANO-DE-INICIO', ''),
            'end_year': posdoc.get('ANO-DE-CONCLUSAO', ''),
            'scholarship': posdoc.get('FLAG-BOLSA', '') == 'SIM',
            'funding_agency': posdoc.get('NOME-AGENCIA', '')
        })
    
    return education


def extract_positions(root):
    """Extract professional positions."""
    positions = []
    
    for atuacao in root.findall('.//ATUACAO-PROFISSIONAL'):
        institution = atuacao.get('NOME-INSTITUICAO', '')
        
        for vinculo in atuacao.findall('.//VINCULOS'):
            positions.append({
                'institution': institution,
                'position': vinculo.get('OUTRO-ENQUADRAMENTO-FUNCIONAL-INFORMADO', ''),
                'type': vinculo.get('TIPO-DE-VINCULO', ''),
                'start_month': vinculo.get('MES-INICIO', ''),
                'start_year': vinculo.get('ANO-INICIO', ''),
                'end_month': vinculo.get('MES-FIM', ''),
                'end_year': vinculo.get('ANO-FIM', ''),
                'hours_per_week': vinculo.get('CARGA-HORARIA-SEMANAL', ''),
                'exclusive_dedication': vinculo.get('FLAG-DEDICACAO-EXCLUSIVA', '') == 'SIM'
            })
    
    return positions


def extract_research_areas(root):
    """Extract research areas."""
    areas = []
    
    for area in root.findall('.//AREA-DE-ATUACAO'):
        areas.append({
            'major_area': area.get('NOME-GRANDE-AREA-DO-CONHECIMENTO', ''),
            'area': area.get('NOME-DA-AREA-DO-CONHECIMENTO', ''),
            'subarea': area.get('NOME-DA-SUB-AREA-DO-CONHECIMENTO', ''),
            'specialty': area.get('NOME-DA-ESPECIALIDADE', '')
        })
    
    return areas


def extract_languages(root):
    """Extract language proficiency."""
    languages = []
    
    for idioma in root.findall('.//IDIOMA'):
        languages.append({
            'language': idioma.get('DESCRICAO-DO-IDIOMA', ''),
            'code': idioma.get('IDIOMA', ''),
            'reading': idioma.get('PROFICIENCIA-DE-LEITURA', ''),
            'speaking': idioma.get('PROFICIENCIA-DE-FALA', ''),
            'writing': idioma.get('PROFICIENCIA-DE-ESCRITA', ''),
            'comprehension': idioma.get('PROFICIENCIA-DE-COMPREENSAO', '')
        })
    
    return languages


def extract_awards(root):
    """Extract awards and honors."""
    awards = []
    
    for premio in root.findall('.//PREMIO-TITULO'):
        awards.append({
            'title': premio.get('NOME-DO-PREMIO-OU-TITULO', ''),
            'institution': premio.get('NOME-DA-ENTIDADE-PROMOTORA', ''),
            'year': premio.get('ANO-DA-PREMIACAO', '')
        })
    
    return awards


def extract_projects(root):
    """Extract research projects."""
    projects = []
    
    for projeto in root.findall('.//PROJETO-DE-PESQUISA'):
        project = {
            'title': projeto.get('NOME-DO-PROJETO', ''),
            'start_year': projeto.get('ANO-INICIO', ''),
            'end_year': projeto.get('ANO-FIM', ''),
            'status': projeto.get('SITUACAO', ''),
            'nature': projeto.get('NATUREZA', ''),
            'description': projeto.get('DESCRICAO-DO-PROJETO', ''),
            'funding_agencies': []
        }
        
        # Extract funding
        for financiador in projeto.findall('.//FINANCIADOR-DO-PROJETO'):
            project['funding_agencies'].append({
                'name': financiador.get('NOME-INSTITUICAO', ''),
                'type': financiador.get('NATUREZA', '')
            })
        
        projects.append(project)
    
    return projects


def extract_supervisions(root):
    """Extract student supervisions (orientações)."""
    supervisions = []
    
    # Postdoc supervisions
    for orient in root.findall('.//ORIENTACOES-CONCLUIDAS-PARA-POS-DOUTORADO'):
        for detalhe in orient.findall('.//DETALHAMENTO-DE-ORIENTACOES-CONCLUIDAS-PARA-POS-DOUTORADO'):
            supervisions.append({
                'level': 'Post-doc',
                'status': 'Completed',
                'student': detalhe.get('NOME-DO-ORIENTADO', ''),
                'title': orient.find('.//DADOS-BASICOS-DE-ORIENTACOES-CONCLUIDAS-PARA-POS-DOUTORADO').get('TITULO-DO-TRABALHO', '') if orient.find('.//DADOS-BASICOS-DE-ORIENTACOES-CONCLUIDAS-PARA-POS-DOUTORADO') is not None else '',
                'year': orient.find('.//DADOS-BASICOS-DE-ORIENTACOES-CONCLUIDAS-PARA-POS-DOUTORADO').get('ANO', '') if orient.find('.//DADOS-BASICOS-DE-ORIENTACOES-CONCLUIDAS-PARA-POS-DOUTORADO') is not None else '',
                'institution': detalhe.get('NOME-DA-INSTITUICAO', ''),
                'course': ''
            })
    
    # PhD supervisions
    for orient in root.findall('.//ORIENTACOES-CONCLUIDAS-PARA-DOUTORADO'):
        for detalhe in orient.findall('.//DETALHAMENTO-DE-ORIENTACOES-CONCLUIDAS-PARA-DOUTORADO'):
            supervisions.append({
                'level': 'PhD',
                'status': 'Completed',
                'student': detalhe.get('NOME-DO-ORIENTADO', ''),
                'title': orient.find('.//DADOS-BASICOS-DE-ORIENTACOES-CONCLUIDAS-PARA-DOUTORADO').get('TITULO', ''),
                'year': orient.find('.//DADOS-BASICOS-DE-ORIENTACOES-CONCLUIDAS-PARA-DOUTORADO').get('ANO', ''),
                'institution': detalhe.get('NOME-DA-INSTITUICAO', ''),
                'course': detalhe.get('NOME-CURSO', '')
            })
    
    # Masters supervisions
    for orient in root.findall('.//ORIENTACOES-CONCLUIDAS-PARA-MESTRADO'):
        for detalhe in orient.findall('.//DETALHAMENTO-DE-ORIENTACOES-CONCLUIDAS-PARA-MESTRADO'):
            supervisions.append({
                'level': 'Masters',
                'status': 'Completed',
                'student': detalhe.get('NOME-DO-ORIENTADO', ''),
                'title': orient.find('.//DADOS-BASICOS-DE-ORIENTACOES-CONCLUIDAS-PARA-MESTRADO').get('TITULO', ''),
                'year': orient.find('.//DADOS-BASICOS-DE-ORIENTACOES-CONCLUIDAS-PARA-MESTRADO').get('ANO', ''),
                'institution': detalhe.get('NOME-DA-INSTITUICAO', ''),
                'course': detalhe.get('NOME-CURSO', '')
            })
    
    # Ongoing PhD
    for orient in root.findall('.//ORIENTACOES-EM-ANDAMENTO-DE-DOUTORADO'):
        for detalhe in orient.findall('.//DETALHAMENTO-DE-ORIENTACOES-EM-ANDAMENTO-DE-DOUTORADO'):
            supervisions.append({
                'level': 'PhD',
                'status': 'Ongoing',
                'student': detalhe.get('NOME-DO-ORIENTANDO', ''),
                'title': orient.find('.//DADOS-BASICOS-DA-ORIENTACAO-EM-ANDAMENTO-DE-DOUTORADO').get('TITULO-DO-TRABALHO', ''),
                'year': orient.find('.//DADOS-BASICOS-DA-ORIENTACAO-EM-ANDAMENTO-DE-DOUTORADO').get('ANO', ''),
                'institution': detalhe.get('NOME-DA-INSTITUICAO', ''),
                'course': detalhe.get('NOME-DO-CURSO', '')
            })
    
    # Ongoing Masters
    for orient in root.findall('.//ORIENTACOES-EM-ANDAMENTO-DE-MESTRADO'):
        for detalhe in orient.findall('.//DETALHAMENTO-DE-ORIENTACOES-EM-ANDAMENTO-DE-MESTRADO'):
            supervisions.append({
                'level': 'Masters',
                'status': 'Ongoing',
                'student': detalhe.get('NOME-DO-ORIENTANDO', ''),
                'title': orient.find('.//DADOS-BASICOS-DA-ORIENTACAO-EM-ANDAMENTO-DE-MESTRADO').get('TITULO-DO-TRABALHO', ''),
                'year': orient.find('.//DADOS-BASICOS-DA-ORIENTACAO-EM-ANDAMENTO-DE-MESTRADO').get('ANO', ''),
                'institution': detalhe.get('NOME-DA-INSTITUICAO', ''),
                'course': detalhe.get('NOME-DO-CURSO', '')
            })
    
    return supervisions


def extract_committees(root):
    """Extract committee participation (bancas)."""
    committees = []
    
    # PhD committees
    for banca in root.findall('.//PARTICIPACAO-EM-BANCA-DE-DOUTORADO'):
        for detalhe in banca.findall('.//DETALHAMENTO-DE-PARTICIPACAO-EM-BANCA-DE-DOUTORADO'):
            committees.append({
                'type': 'PhD Defense',
                'candidate': detalhe.get('NOME-DO-CANDIDATO', ''),
                'title': banca.find('.//DADOS-BASICOS-DA-PARTICIPACAO-EM-BANCA-DE-DOUTORADO').get('TITULO', ''),
                'year': banca.find('.//DADOS-BASICOS-DA-PARTICIPACAO-EM-BANCA-DE-DOUTORADO').get('ANO', ''),
                'institution': detalhe.get('NOME-DA-INSTITUICAO', '')
            })
    
    # Masters committees
    for banca in root.findall('.//PARTICIPACAO-EM-BANCA-DE-MESTRADO'):
        for detalhe in banca.findall('.//DETALHAMENTO-DE-PARTICIPACAO-EM-BANCA-DE-MESTRADO'):
            committees.append({
                'type': 'Masters Defense',
                'candidate': detalhe.get('NOME-DO-CANDIDATO', ''),
                'title': banca.find('.//DADOS-BASICOS-DA-PARTICIPACAO-EM-BANCA-DE-MESTRADO').get('TITULO', ''),
                'year': banca.find('.//DADOS-BASICOS-DA-PARTICIPACAO-EM-BANCA-DE-MESTRADO').get('ANO', ''),
                'institution': detalhe.get('NOME-DA-INSTITUICAO', '')
            })
    
    # Qualification exams
    for banca in root.findall('.//PARTICIPACAO-EM-BANCA-DE-EXAMES-DE-QUALIFICACAO'):
        for detalhe in banca.findall('.//DETALHAMENTO-DE-PARTICIPACAO-EM-BANCA-DE-EXAMES-DE-QUALIFICACAO'):
            committees.append({
                'type': 'Qualification Exam',
                'candidate': detalhe.get('NOME-DO-CANDIDATO', ''),
                'title': banca.find('.//DADOS-BASICOS-DA-PARTICIPACAO-EM-BANCA-DE-EXAMES-DE-QUALIFICACAO').get('TITULO', ''),
                'year': banca.find('.//DADOS-BASICOS-DA-PARTICIPACAO-EM-BANCA-DE-EXAMES-DE-QUALIFICACAO').get('ANO', ''),
                'institution': detalhe.get('NOME-DA-INSTITUICAO', '')
            })
    
    return committees


def extract_event_organization(root):
    """Extract event organization activities."""
    events = []
    
    for evento in root.findall('.//PARTICIPACAO-EM-EVENTOS-CONGRESSOS'):
        dados_basicos = evento.find('.//DADOS-BASICOS-DA-PARTICIPACAO-EM-EVENTOS-CONGRESSOS')
        detalhe = evento.find('.//DETALHAMENTO-DA-PARTICIPACAO-EM-EVENTOS-CONGRESSOS')
        
        if dados_basicos is not None:
            events.append({
                'title': dados_basicos.get('TITULO', ''),
                'nature': dados_basicos.get('NATUREZA', ''),
                'year': dados_basicos.get('ANO', ''),
                'event_name': detalhe.get('NOME-DO-EVENTO', '') if detalhe is not None else '',
                'institution': detalhe.get('INSTITUICAO-PROMOTORA', '') if detalhe is not None else ''
            })
    
    return events


def extract_editorial(root):
    """Extract editorial activities (reviewer, editor)."""
    editorial = []
    
    # As reviewer
    for atividade in root.findall('.//PARTICIPACAO-EM-CORPO-EDITORIAL'):
        dados = atividade.find('.//DADOS-BASICOS-DA-PARTICIPACAO-EM-CORPO-EDITORIAL')
        detalhe = atividade.find('.//DETALHAMENTO-DA-PARTICIPACAO-EM-CORPO-EDITORIAL')
        
        if dados is not None:
            editorial.append({
                'type': 'Editorial Board',
                'journal': dados.get('NOME-DO-PERIODICO-OU-REVISTA', ''),
                'start_year': detalhe.get('ANO-INICIO', '') if detalhe is not None else '',
                'end_year': detalhe.get('ANO-FIM', '') if detalhe is not None else ''
            })
    
    return editorial


def extract_teaching(root):
    """Extract teaching activities."""
    teaching = []
    
    for ensino in root.findall('.//ENSINO'):
        teaching.append({
            'type': ensino.get('TIPO-ENSINO', ''),
            'start_month': ensino.get('MES-INICIO', ''),
            'start_year': ensino.get('ANO-INICIO', ''),
            'end_month': ensino.get('MES-FIM', ''),
            'end_year': ensino.get('ANO-FIM', ''),
            'course': ensino.get('NOME-CURSO', ''),
            'disciplines': [d.text for d in ensino.findall('.//DISCIPLINA')]
        })
    
    return teaching


def main():
    # Load configuration
    cfg = yaml.safe_load(open("profiles.yaml"))
    xml_file = pathlib.Path(cfg.get("lattes_xml", "data/raw/lattes.xml"))
    
    if not xml_file.exists():
        print(f"XML file not found: {xml_file}")
        print(f"Please export your Lattes CV as XML and save it as: {xml_file}")
        # Create empty output to prevent pipeline errors
        output = pathlib.Path("data/processed/lattes_comprehensive.json")
        output.parent.mkdir(parents=True, exist_ok=True)
        empty_data = {
            'personal_info': {},
            'education': [],
            'positions': [],
            'research_areas': [],
            'languages': [],
            'awards': [],
            'projects': [],
            'supervisions': [],
            'committee_participation': [],
            'event_organization': [],
            'editorial_activities': [],
            'teaching': []
        }
        output.write_text(json.dumps(empty_data, ensure_ascii=False, indent=2), encoding='utf-8')
        return
    
    print("Parsing comprehensive Lattes CV data...")
    cv_data = parse_lattes_comprehensive(str(xml_file))
    
    # Save complete CV data
    output = pathlib.Path("data/processed/lattes_comprehensive.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(cv_data, ensure_ascii=False, indent=2), encoding='utf-8')
    
    # Print summary
    print(f"\n✓ Comprehensive Lattes CV parsed successfully!")
    print(f"  → Personal info: {cv_data['personal_info']['name']}")
    print(f"  → Education: {len(cv_data['education'])} degrees")
    print(f"  → Positions: {len(cv_data['positions'])} positions")
    print(f"  → Research areas: {len(cv_data['research_areas'])} areas")
    print(f"  → Languages: {len(cv_data['languages'])} languages")
    print(f"  → Awards: {len(cv_data['awards'])} awards")
    print(f"  → Projects: {len(cv_data['projects'])} projects")
    print(f"  → Supervisions: {len(cv_data['supervisions'])} supervisions")
    print(f"  → Committees: {len(cv_data['committee_participation'])} committees")
    print(f"  → Event organization: {len(cv_data['event_organization'])} events")
    print(f"  → Editorial activities: {len(cv_data['editorial_activities'])} activities")
    print(f"  → Teaching: {len(cv_data['teaching'])} courses")
    print(f"\n  Saved to: {output}")


if __name__ == "__main__":
    main()
