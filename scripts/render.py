import json, jinja2, yaml, subprocess, pathlib, sys

cfg = yaml.safe_load(open("profiles.yaml"))
template_choice = cfg.get("template","markdown")

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

pathlib.Path("build").mkdir(exist_ok=True)
env = jinja2.Environment(loader=jinja2.FileSystemLoader("templates"))

if template_choice == "markdown":
    md = env.get_template("cv.md").render(sections=sections)
    open("build/cv.md","w").write(md)
    try:
        subprocess.check_call(["pandoc","build/cv.md","-o","build/cv.pdf","--from","markdown","--pdf-engine=xelatex","--defaults","templates/pandoc.yaml"])
        print("Rendered build/cv.pdf")
    except Exception:
        print("Produced build/cv.md (no LaTeX/Pandoc).")
elif template_choice == "awesome-cv":
    tex = env.get_template("awesome-cv.tex.j2").render(sections=sections)
    open("build/cv.tex","w").write(tex)
    try:
        subprocess.check_call(["xelatex","-interaction=nonstopmode","-output-directory","build","build/cv.tex"])
        print("Rendered build/cv.pdf (Awesome-CV)")
    except Exception:
        print("Wrote build/cv.tex (xelatex not available).")
elif template_choice == "moderncv":
    tex = env.get_template("moderncv.tex.j2").render(sections=sections)
    open("build/cv.tex","w").write(tex)
    try:
        subprocess.check_call(["xelatex","-interaction=nonstopmode","-output-directory","build","build/cv.tex"])
        print("Rendered build/cv.pdf (moderncv)")
    except Exception:
        print("Wrote build/cv.tex (xelatex not available).")
else:
    print("Unknown template; use markdown, awesome-cv, or moderncv")
