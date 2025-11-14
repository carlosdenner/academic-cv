# Parse a Lattes (CNPq) XML export and extract bibliographic items.
# Expected file path in profiles.yaml:lattes_xml
from lxml import etree
import yaml, json, pathlib

cfg = yaml.safe_load(open("profiles.yaml"))
xml_path = cfg.get("lattes_xml", "data/raw/lattes.xml")
out = pathlib.Path("data/processed/lattes_works.json")
try:
    tree = etree.parse(xml_path)
except Exception as e:
    print(f"Lattes XML not found or invalid ({e}); skipping.")
    out.write_text("[]")
    raise SystemExit(0)

root = tree.getroot()

def text(el, attr):
    return (el.get(attr) or "").strip()

items = []

# 1) Journal articles: PRODUCAO-BIBLIOGRAFICA/ARTIGOS-PUBLICADOS/ARTIGO-PUBLICADO/DADOS-BASICOS-DO-ARTIGO
for art in root.findall(".//ARTIGO-PUBLICADO"):
    db = art.find("./DADOS-BASICOS-DO-ARTIGO")
    det = art.find("./DETALHAMENTO-DO-ARTIGO")
    if db is None: 
        continue
    title = db.get("TITULO-DO-ARTIGO") or ""
    year = db.get("ANO-DO-ARTIGO") or ""
    doi = (db.get("DOI") or "").lower()
    journal = det.get("TITULO-DO-PERIODICO-OU-REVISTA") if det is not None else ""
    url = db.get("HOME-PAGE-DO-TRABALHO") or ""
    items.append({
        "title": title.strip(),
        "year": int(year) if year.isdigit() else None,
        "type": "journal-article",
        "venue": journal.strip(),
        "doi": doi,
        "url": url,
        "source": "lattes"
    })

# 2) Conference papers: TRABALHOS-EM-EVENTOS/TRABALHO-EM-EVENTOS/DADOS-BASICOS-DO-TRABALHO
for ev in root.findall(".//TRABALHO-EM-EVENTOS"):
    db = ev.find("./DADOS-BASICOS-DO-TRABALHO")
    det = ev.find("./DETALHAMENTO-DO-TRABALHO")
    if db is None: 
        continue
    title = db.get("TITULO-DO-TRABALHO") or ""
    year = db.get("ANO-DO-TRABALHO") or ""
    doi = (db.get("DOI") or "").lower()
    booktitle = det.get("TITULO-DOS-ANAIS-OU-PROCEEDINGS") if det is not None else ""
    url = db.get("HOME-PAGE-DO-TRABALHO") or ""
    items.append({
        "title": title.strip(),
        "year": int(year) if year.isdigit() else None,
        "type": "proceedings-article",
        "venue": booktitle.strip(),
        "doi": doi,
        "url": url,
        "source": "lattes"
    })

# 3) Books and chapters
for ch in root.findall(".//CAPITULO-DE-LIVRO-PUBLICADO"):
    db = ch.find("./DADOS-BASICOS-DO-CAPITULO")
    det = ch.find("./DETALHAMENTO-DO-CAPITULO")
    if db is None: 
        continue
    title = db.get("TITULO-DO-CAPITULO-DO-LIVRO") or ""
    year = db.get("ANO") or db.get("ANO-DO-CAPITULO") or ""
    doi = (db.get("DOI") or "").lower()
    book = det.get("TITULO-DO-LIVRO") if det is not None else ""
    url = db.get("HOME-PAGE-DO-TRABALHO") or ""
    items.append({
        "title": title.strip(),
        "year": int(year) if str(year).isdigit() else None,
        "type": "book-chapter",
        "venue": book.strip(),
        "doi": doi,
        "url": url,
        "source": "lattes"
    })

for bk in root.findall(".//LIVRO-PUBLICADO-OU-ORGANIZADO"):
    db = bk.find("./DADOS-BASICOS-DO-LIVRO")
    det = bk.find("./DETALHAMENTO-DO-LIVRO")
    if db is None:
        continue
    title = db.get("TITULO-DO-LIVRO") or ""
    year = db.get("ANO") or ""
    doi = (db.get("DOI") or "").lower()
    publisher = det.get("NOME-DA-EDITORA") if det is not None else ""
    items.append({
        "title": title.strip(),
        "year": int(year) if str(year).isdigit() else None,
        "type": "book",
        "venue": publisher.strip(),
        "doi": doi,
        "url": db.get("HOME-PAGE-DO-TRABALHO") or "",
        "source": "lattes"
    })

path = pathlib.Path("data/processed/lattes_works.json")
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(json.dumps(items, indent=2, ensure_ascii=False))
print(f"Parsed Lattes items: {len(items)} → {path}")
