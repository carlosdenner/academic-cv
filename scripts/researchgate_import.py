import pandas as pd, yaml, json, pathlib
cfg = yaml.safe_load(open("profiles.yaml"))
csv_path = cfg.get("researchgate_csv","data/raw/researchgate_export.csv")
out = pathlib.Path("data/processed/researchgate_works.json")
try:
    df = pd.read_csv(csv_path)
except FileNotFoundError:
    print("No ResearchGate CSV found; skipping.")
    out.write_text("[]")
    raise SystemExit(0)

cols = {c.lower(): c for c in df.columns}
def col(name): return cols.get(name, None)

norm = []
for _, r in df.iterrows():
    norm.append({
        "title": str(r.get(col("title"),"")).strip(),
        "year": int(r.get(col("year"), 0)) if str(r.get(col("year"),"")).isdigit() else None,
        "type": "researchgate_record",
        "venue": None,
        "doi": str(r.get(col("doi"),"")).strip().lower(),
        "url": str(r.get(col("url"),"")).strip(),
        "source": "researchgate"
    })
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(norm, indent=2))
print(f"Normalized ResearchGate items: {len(norm)} → {out}")
