# 🚀 Quick Start: Publishing Your Academic CV

## Step 1: Test Locally (Optional)

```bash
cd docs
python -m http.server 8000
```

Visit: http://localhost:8000

## Step 2: Deploy to GitHub Pages

### A. Push your code to GitHub

```bash
git add .
git commit -m "Add interactive CV website"
git push origin main
```

### B. Enable GitHub Pages

1. Go to your repository on GitHub: `https://github.com/YOUR-USERNAME/academic-cv`
2. Click **Settings** (top menu)
3. Click **Pages** (left sidebar)
4. Under "Build and deployment":
   - Source: **Deploy from a branch**
   - Branch: **main**
   - Folder: **/docs**
5. Click **Save**

### C. Access Your CV

Your CV will be live at: `https://YOUR-USERNAME.github.io/academic-cv/`

⏱️ First deployment takes 2-3 minutes.

## Step 3: Update Your CV

Whenever you add new publications or update your profile:

```bash
# Pull latest publications
make update

# Or run pipeline manually:
python scripts/orcid_pull.py
python scripts/openalex_enrich.py
python scripts/crossref_fill.py
python scripts/normalize_dedupe.py
python scripts/consolidate_cv_data.py

# Commit and push
git add .
git commit -m "Update publications"
git push
```

Your website will automatically update within 2-3 minutes.

## 🎨 Customization Tips

### Change Colors

Edit `docs/style.css`:

```css
:root {
    --primary-color: #2563eb;  /* Change this to your preferred color */
    --accent-color: #f59e0b;   /* Change accent color */
}
```

### Update Contact Info

Edit `profiles.yaml` and regenerate:

```bash
python scripts/consolidate_cv_data.py
```

### Add Custom Sections

1. Add HTML in `docs/index.html`
2. Add styling in `docs/style.css`
3. Add rendering logic in `docs/script.js`

## 🔍 SEO Optimization

Add to `docs/index.html` `<head>`:

```html
<meta name="description" content="Your description here">
<meta name="keywords" content="data science, research, publications">
<meta property="og:title" content="Your Name - Academic CV">
<meta property="og:image" content="https://your-domain.com/photo.jpg">
```

## 📊 Analytics (Optional)

Add Google Analytics by inserting before `</head>` in `docs/index.html`:

```html
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
```

## 🐛 Troubleshooting

### Website shows "Error loading CV data"

```bash
# Regenerate the data file
python scripts/consolidate_cv_data.py

# Check if cv_data.json exists in docs/
ls docs/cv_data.json
```

### Changes not appearing on GitHub Pages

1. Clear browser cache (Ctrl+F5 or Cmd+Shift+R)
2. Check GitHub Actions tab for build errors
3. Wait 2-3 minutes for deployment
4. Try incognito/private browsing mode

### Dark mode not working

Check browser console (F12) for JavaScript errors.

## 🌐 Custom Domain (Optional)

To use your own domain (e.g., cv.yourname.com):

1. Create file `docs/CNAME` with your domain:
   ```
   cv.yourname.com
   ```

2. Add DNS records at your domain provider:
   - Type: CNAME
   - Name: cv (or @)
   - Value: YOUR-USERNAME.github.io

3. Enable HTTPS in GitHub Pages settings

More info: https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site

## 📱 Share Your CV

Once deployed, share using:

- **Direct link**: `https://YOUR-USERNAME.github.io/academic-cv/`
- **QR Code**: Generate at [qr-code-generator.com](https://www.qr-code-generator.com/)
- **Short URL**: Create using [bit.ly](https://bitly.com/) or [tinyurl.com](https://tinyurl.com/)

## 🔄 Automatic Updates (Advanced)

The GitHub Action in `.github/workflows/deploy.yml` automatically:
1. Regenerates CV data from source files
2. Deploys to GitHub Pages

Every push to `main` triggers this workflow.

## 💡 Pro Tips

1. **Update regularly**: Run `make update` weekly to catch new citations
2. **Check metrics**: Monitor h-index and citation growth
3. **Backup data**: Keep raw source files (HTML, XML, JSON) in `data/raw/`
4. **Version control**: Use git tags for major CV updates
5. **Mobile test**: Always check appearance on mobile devices

## 📞 Need Help?

- Check `docs/README.md` for detailed documentation
- Review browser console (F12) for JavaScript errors
- Verify JSON structure: `python -m json.tool docs/cv_data.json`
- Test pipeline: `python scripts/normalize_dedupe.py`

---

**Happy publishing!** 🎉

Your interactive CV showcases:
- ✅ All publications with citations
- ✅ Research metrics (h-index, total citations)
- ✅ Education and experience timeline
- ✅ Research projects and funding
- ✅ Academic supervisions
- ✅ Awards and honors
- ✅ Responsive design (mobile-friendly)
- ✅ Dark mode support
- ✅ Interactive filtering and search
