import xml.etree.ElementTree as ET

tree = ET.parse('data/raw/lattes.xml')
root = tree.getroot()

# Find postdoc supervisions
postdocs = root.findall('.//ORIENTACOES-CONCLUIDAS-PARA-POS-DOUTORADO')
print(f"Postdoc supervisions: {len(postdocs)}")

for i, pd in enumerate(postdocs, 1):
    details = pd.find('DETALHAMENTO-DE-ORIENTACOES-CONCLUIDAS-PARA-POS-DOUTORADO')
    if details is not None:
        name = details.get('NOME-DO-ORIENTADO', 'Unknown')
        year = details.get('ANO', 'Unknown')
        title = details.get('TITULO-DO-TRABALHO', 'No title')
        print(f"{i}. {name} ({year})")
        print(f"   {title}")
