# Windsurf quickrun

Paste this into Cascade:

> Create & activate a Python venv; `pip install -r requirements.txt`; run `make update`; set `template` in `profiles.yaml` to `awesome-cv` or `moderncv` (or `markdown`); run `make render`; open `build/cv.pdf` (or `build/cv.md`). If LaTeX is missing, choose `markdown` first. Place Scholar `.bib`, ResearchGate `.csv`, and Lattes `.xml` in `data/raw/`.

Troubleshooting:
- No LaTeX: set `template: markdown` and run `make render`.
- Missing exports: add files to `data/raw/` with the exact names in `profiles.yaml`.
- Encoding issues (Lattes XML): ensure UTF-8; we use `lxml` for robust parsing.
