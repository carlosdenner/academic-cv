import json, yaml, requests, pathlib
cfg = yaml.safe_load(open("profiles.yaml"))
orcid = cfg["orcid"]
mailto = cfg.get("mailto","")
a = requests.get(f"https://api.openalex.org/authors/{orcid}", params={"mailto": mailto}).json()
works_url = a["works_api_url"]
items, page = [], 1
while True:
    resp = requests.get(works_url, params={"per-page":200, "page":page, "mailto": mailto}).json()
    items.extend(resp.get("results", []))
    if not resp.get("next_page"): break
    page += 1
pathlib.Path("data/processed").mkdir(parents=True, exist_ok=True)
open("data/processed/openalex_author.json","w").write(json.dumps(a, indent=2))
open("data/processed/openalex_works.json","w").write(json.dumps(items, indent=2))
print(f"OpenAlex author & {len(items)} works saved.")
