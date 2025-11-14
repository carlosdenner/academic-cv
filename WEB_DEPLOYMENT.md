# 🌐 Interactive Web Portfolio - Live!

## ✨ View Online
**Your beautiful interactive CV is now live at:**
### [https://carlosdenner-videns.github.io/academic-cv/](https://carlosdenner-videns.github.io/academic-cv/)

## 🎉 What's New

I've created a **stunning, modern web portfolio** to showcase your academic achievements:

### Key Features
- 🎨 **Modern UI/UX**: Clean, professional design with smooth animations
- 🌓 **Dark/Light Theme**: Toggle between themes with persistence
- 📱 **Fully Responsive**: Perfect on desktop, tablet, and mobile
- 🔍 **Smart Search**: Real-time search across 99 publications
- 🎯 **Advanced Filtering**: Filter by journal, conference, book, or in-prep
- 📊 **Animated Stats**: Eye-catching counters for your achievements
- ⚡ **Lightning Fast**: Optimized performance with lazy loading
- ♿ **Accessible**: WCAG compliant with proper ARIA labels

### Sections Included
1. **Hero Section**: Compelling intro with social links and CTA buttons
2. **Stats Banner**: 99 publications, 28 positions, 14 supervisions, 26 years
3. **About**: Highlights, research interests, and expertise
4. **Experience**: Interactive timeline with key positions
5. **Publications**: Searchable, filterable list with badges and links
6. **Research**: Current AI projects (LLM security, RAG, Jooay)
7. **Contact**: Multiple contact methods and social links

## 🚀 How to Use

### View Online (Recommended)
Just visit: [https://carlosdenner-videns.github.io/academic-cv/](https://carlosdenner-videns.github.io/academic-cv/)

### Run Locally
```bash
cd docs
# Start a local server (required for JSON loading)
python -m http.server 8000
# Visit http://localhost:8000 in your browser
```

## 📝 Customization

### Update Publications
Edit `docs/cv_data.json` to add/modify publications:
```json
{
  "publications": [
    {
      "title": "Your Paper Title",
      "authors": "Author Names",
      "venue": "Journal/Conference Name",
      "year": 2025,
      "type": "journal",
      "doi": "10.xxxx/xxxxx",
      "url": "https://..."
    }
  ]
}
```

### Change Theme Colors
Edit CSS variables in `docs/style.css`:
```css
:root {
    --primary: #2563eb;  /* Your brand color */
    --accent: #8b5cf6;   /* Accent color */
}
```

### Add Content
- **New sections**: Add HTML in `docs/index.html`
- **New styles**: Extend `docs/style.css`
- **New features**: Enhance `docs/script.js`

## 🛠️ Technical Stack

- **HTML5**: Semantic markup
- **CSS3**: Modern styling with animations
- **Vanilla JavaScript**: No frameworks, pure performance
- **Font Awesome 6.4.0**: Icon library
- **Google Fonts**: Inter & JetBrains Mono
- **GitHub Pages**: Free hosting

## 📊 Repository Status

- ✅ **Repository**: Public (required for GitHub Pages)
- ✅ **GitHub Pages**: Enabled on master branch
- ✅ **Source**: `/docs` folder
- ✅ **HTTPS**: Enforced
- 🌐 **URL**: [carlosdenner-videns.github.io/academic-cv](https://carlosdenner-videns.github.io/academic-cv/)

## 🎯 Next Steps

### Recommended Improvements
1. **Google Scholar ID**: Update placeholder in `index.html` line 71
2. **cv_data.json**: Add actual publication data (currently loads from JSON)
3. **Custom Domain**: (Optional) Configure custom domain in GitHub settings
4. **Analytics**: Add Google Analytics for visitor tracking
5. **PDF Download**: Link to your LaTeX CV PDF

### Share Your Portfolio
- Add URL to your email signature
- Include on business cards
- Link from LinkedIn profile
- Share on ResearchGate
- Add to conference presentations

## 📧 Support

For questions or issues:
- Check GitHub Issues
- Review documentation
- Contact: carlosdenner@gmail.com

---

**🎉 Congratulations!** Your academic portfolio is now live and looking amazing!

*Generated: January 2025 | GitHub Pages Deployment*
