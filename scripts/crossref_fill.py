import json, requests, pathlib, time, yaml
cfg = yaml.safe_load(open("profiles.yaml"))
mailto = cfg.get("mailto","")
try:
    works = json.load(open("data/processed/openalex_works.json"))
except FileNotFoundError:
    works = []
by_doi = [w for w in works if w.get("doi")]
enriched = {}
for w in by_doi:
    doi = w["doi"].lower()
    r = requests.get(f"https://api.crossref.org/works/{doi}",
                     headers={"User-Agent": f"Academic-CV (mailto:{mailto})"})
    if r.status_code==200:
        enriched[doi]=r.json()["message"]
    time.sleep(0.1)
pathlib.Path("data/processed").mkdir(parents=True, exist_ok=True)
open("data/processed/crossref_by_doi.json","w").write(json.dumps(enriched, indent=2))
print(f"Crossref enriched: {len(enriched)} records")
