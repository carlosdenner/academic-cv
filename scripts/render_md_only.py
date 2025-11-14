import json, jinja2, pathlib
items = json.load(open("data/processed/works_merged.json"))
def bucket(w):
    t = (w.get("type") or "").lower()
    if "journal" in t: return "Journal Articles"
    if "proceeding" in t or "conference" in t: return "Conference Papers"
    if "preprint" in t or "repository" in t: return "Preprints"
    if "dataset" in t or "software" in t: return "Datasets & Software"
    if "book-chapter" in t: return "Book Chapters"
    if "book" in t: return "Books"
    return "Other"
sections = {}
for w in items:
    sections.setdefault(bucket(w), []).append(w)
env = jinja2.Environment(loader=jinja2.FileSystemLoader("templates"))
md = env.get_template("cv.md").render(sections=sections)
pathlib.Path("build").mkdir(exist_ok=True)
open("build/cv.md","w").write(md)
print("Rendered build/cv.md")
