# Clean Publications CV - Generated

## Overview

A clean, professional academic CV focused on publications with clickable DOI links.

## Features

✅ **Clean Design**: Simple, elegant formatting with clear sections
✅ **Complete Publications**: ALL 82 publications included (not truncated)
✅ **Clickable Links**: DOI links, email, website all clickable
✅ **Organized by Type**: 
   - Journal Articles (59)
   - Conference Papers (16)
   - Book Chapters (4)
✅ **Research Metrics**: Citations, h-index, supervisions prominently displayed
✅ **Professional Contact**: Full contact information with icons

## Output

- **File**: `output/cv_publications.pdf`
- **Pages**: 11 pages
- **Template**: `templates/clean-publications.tex.j2`
- **Renderer**: `scripts/render_latex.py`

## Generate

```bash
# Generate LaTeX and compile to PDF
make pdf

# Or manually:
python scripts/render_latex.py
cd output
xelatex cv_publications.tex
xelatex cv_publications.tex  # Run twice for proper hyperlinks
```

## Next Steps

If you want to add more sections (education, professional experience, awards), we can:

1. **Keep it simple**: Add just the essentials (education, current position)
2. **Full CV**: Add all sections but keep clean formatting
3. **Customize**: Adjust spacing, fonts, colors

The current version focuses on what matters most for academic applications: publications with full citation details and clickable links to papers.
