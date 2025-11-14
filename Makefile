.PHONY: all update render md web clean serve latex pdf

all: update render web

update:
	python scripts/orcid_pull.py
	python scripts/openalex_enrich.py
	python scripts/crossref_fill.py
	python scripts/scholar_html_import.py
	python scripts/researchgate_html_import.py
	python scripts/researchgate_import.py
	python scripts/lattes_import.py
	python scripts/lattes_comprehensive.py
	python scripts/cv_markdown_import.py
	python scripts/videns_experience_import.py
	python scripts/normalize_dedupe.py

render:
	python scripts/render.py

md:
	python scripts/render_md_only.py

web:
	python scripts/consolidate_cv_data.py

latex:
	python scripts/render_latex.py

pdf: latex
	cd output && xelatex -interaction=nonstopmode cv_publications.tex
	cd output && xelatex -interaction=nonstopmode cv_publications.tex

serve:
	cd docs && python -m http.server 8000

clean:
	rm -rf build
	rm -rf output/*.aux output/*.log output/*.out
