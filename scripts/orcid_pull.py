import json, yaml, requests, pathlib
cfg = yaml.safe_load(open("profiles.yaml"))
orcid = cfg["orcid"]
out = pathlib.Path("data/processed/orcid_seed.json")
r = requests.get(f"https://pub.orcid.org/v3.0/{orcid.split('/')[-1]}/works",
                 headers={"Accept":"application/json"})
r.raise_for_status()
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(r.json(), ensure_ascii=False, indent=2))
print(f"Wrote {out}")
