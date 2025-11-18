# CV Synchronization Guide

## Overview
You now have two CV files that must stay in sync:
- **English (source)**: `data/latex/CarlosDenner_CV_resume.tex`
- **French (translated)**: `data/latex/CarlosDenner_CV_resume_FR.tex`

This guide explains how to keep both versions synchronized efficiently.

---

## Quick Sync Workflow

### When You Update the English CV:

1. **Identify the section(s) you changed**
   - Example: You updated "Professional Experience" or added a new publication

2. **Update the French version with the same changes**
   - Translate only the new/changed text
   - Keep the structure identical
   - Use the same date formats, spacing, and formatting

3. **Verify both files compile**
   ```bash
   cd data/latex
   xelatex -interaction=nonstopmode CarlosDenner_CV_resume.tex
   xelatex -interaction=nonstopmode CarlosDenner_CV_resume_FR.tex
   ```

---

## Section Mapping (English → French)

To make translation quick, here's the section mapping:

| English Section | French Section |
|---|---|
| Research Interests | Domaines de Recherche |
| Education | Formation |
| Professional Experience | Expérience Professionnelle |
| Academic Supervisions | Encadrements Académiques |
| Publications | Publications |
| Research Grants | Subventions de Recherche |
| Awards & Honors | Prix et Distinctions |
| Professional Service | Service Professionnel |
| Professional Memberships | Adhésions Professionnelles |

---

## Line-by-Line Comparison for Sync

### Common Changes and Their Translations

**Job Titles:**
- "AI Expert" → "Expert en IA"
- "Data Scientist" → "Scientifique des Données"
- "Research Associate" → "Chercheur Associé"
- "Associate Professor" → "Professeur Associé"
- "Postdoctoral Researcher" → "Chercheur Postdoctoral"

**Academic Roles:**
- "PhD Supervisions" → "Encadrements de Doctorat"
- "MSc Supervisions" → "Encadrements de Maîtrise"
- "Postdoctoral Supervisions" → "Encadrements Postdoctoraux"

**Publication Categories:**
- "Journal Articles" → "Articles de Revue"
- "Conference Papers" → "Articles de Conférence"
- "Book Chapters" → "Chapitres de Livre"
- "Datasets" → "Ensembles de Données"
- "Open Peer Reviews" → "Examens Évaluation Ouverts"
- "Under Review & In Preparation" → "En Révision et En Préparation"

**Service Categories:**
- "Editorial Board Member" → "Membre du Comité Éditorial"
- "Ad-hoc Reviewer" → "Examinateur ad-hoc"
- "Board Member" → "Membre du Conseil d'Administration"
- "Peer Reviewer" → "Examinateur"

---

## Key Translation Rules

1. **Dates remain the same** (e.g., "December 2010 - December 2011" → "Décembre 2010 - Décembre 2011")
2. **Names of people remain unchanged**
3. **Names of universities** are NOT translated (keep as is: "Southern Illinois University", "University of São Paulo")
4. **Location names**: Keep original names but use French region/country names where appropriate:
   - "England" → "Angleterre"
   - "United States" → "États-Unis"
   - "Brazil" → "Brésil"
   - Specific city names remain unchanged (e.g., "Montréal", "Brasília")
5. **Journal names and publication titles** remain in their original language

---

## Sync Checklist

Before committing changes, verify:

- [ ] All sections translated completely
- [ ] Date formats match
- [ ] No English text mixed in French document (except proper nouns, journal names)
- [ ] Both PDFs generate without errors
- [ ] File sizes are similar (if one is significantly larger, you may have missed something)
- [ ] Line structure is preserved (sections in same order, subsections aligned)

---

## Common Pitfalls to Avoid

1. **Partial translations**: Don't leave English phrases in French sections. Either translate or mark as [TO TRANSLATE]
2. **Format changes**: Keep the same TeX formatting, spacing, and line breaks
3. **Inconsistent terminology**: Use the section mapping above for consistency
4. **Missing updates**: If you change something in English, ALWAYS update French
5. **Different structures**: Both files should be nearly identical structurally

---

## Efficient Workflow with Git

If using Git, you can:

1. **Use conditional markup** (optional, for advanced users):
   ```latex
   % Mark sections that were just updated
   % UPDATED: 2025-11-18 - Added new publication
   ```

2. **Commit strategy**:
   ```bash
   git add data/latex/CarlosDenner_CV_resume.tex
   git add data/latex/CarlosDenner_CV_resume_FR.tex
   git commit -m "Update CV (both EN and FR): Added new publication"
   ```

3. **Always commit both files together** to keep them in sync historically

---

## When to Regenerate Bibliography

If you modify `publications.bib`:

1. Update both CV files to ensure they compile correctly
2. Regenerate PDFs:
   ```bash
   cd data/latex
   biber CarlosDenner_CV_resume
   biber CarlosDenner_CV_resume_FR
   xelatex CarlosDenner_CV_resume.tex
   xelatex CarlosDenner_CV_resume_FR.tex
   ```

---

## Quick Reference: French Technical Terms

- Supervisor → Superviseur
- Award → Prix
- Fellowship → Bourse
- Research → Recherche
- Department → Département
- Faculty → Faculté
- Grant → Subvention
- Team → Équipe
- Project → Projet
- Committee → Comité
- Board → Conseil
- Organization → Organisme / Organisation
- Institute → Institut
- University → Université
- School → École
- Course → Cours
- Teaching → Enseignement
- Learning → Apprentissage
- Management → Gestion

---

## Example: Adding a New Position

### English (add to Professional Experience):
```latex
\textbf{New Title} \hfill \textit{Start Date - End Date} \\
Employer Name \hfill City, Country
```

### French (add to Expérience Professionnelle in same position):
```latex
\textbf{Titre Traduit} \hfill \textit{Date de Début - Date de Fin} \\
Nom de l'Employeur \hfill Ville, Pays
```

Both should maintain the same visual order and spacing.

---

## Automating Checks (Optional)

You can create a simple script to compare both files:
```bash
# Check if both files have same number of lines
wc -l CarlosDenner_CV_resume.tex CarlosDenner_CV_resume_FR.tex

# Look for common structural markers
grep -n "\\\\begin{rSection}" CarlosDenner_CV_resume.tex
grep -n "\\\\begin{rSection}" CarlosDenner_CV_resume_FR.tex
```

If one file has more sections than the other, you've likely missed a translation.

---

## Support

If you need to make a major restructuring:
1. Update the English version first
2. Document the changes in this guide
3. Apply the same structure to French version
4. Test both compile without errors
5. Commit both together

For any changes, always remember: **Synchronize. Test. Commit together.**

