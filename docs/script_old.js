// Load CV data and initialize the page
let cvData = null;
let allPublications = [];
let currentFilter = 'all';
let currentSort = 'year-desc';

// Load data when page loads
document.addEventListener('DOMContentLoaded', async () => {
    await loadCVData();
    initializeTheme();
    renderAll();
    initializeEventListeners();
});

// Load CV data from JSON file
async function loadCVData() {
    try {
        // Try relative path first (for local development)
        let response = await fetch('./cv_data.json');
        if (!response.ok) {
            // Try absolute path for GitHub Pages
            response = await fetch('../data/processed/cv_data.json');
        }
        cvData = await response.json();
        console.log('CV data loaded:', cvData);
    } catch (error) {
        console.error('Error loading CV data:', error);
        document.body.innerHTML = '<div class="loading">Error loading CV data. Please ensure cv_data.json is in the docs/ directory.</div>';
    }
}

// Initialize theme from localStorage
function initializeTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);
}

// Update theme icon
function updateThemeIcon(theme) {
    const icon = document.querySelector('#theme-toggle i');
    icon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
}

// Toggle theme
function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeIcon(newTheme);
}

// Render all sections
function renderAll() {
    renderHero();
    renderAbout();
    renderMetrics();
    renderPublications();
    renderPositions();
    renderEducation();
    renderProjects();
    renderAwards();
    renderSupervisions();
    renderContact();
}

// Render hero section
function renderHero() {
    document.getElementById('cv-name').textContent = cvData.contact.name;
    
    const links = [
        { icon: 'fas fa-envelope', text: cvData.contact.email, href: `mailto:${cvData.contact.email}` },
        { icon: 'fab fa-github', text: 'GitHub', href: cvData.contact.profiles.github },
        { icon: 'fab fa-linkedin', text: 'LinkedIn', href: cvData.contact.profiles.linkedin },
        { icon: 'fab fa-researchgate', text: 'ResearchGate', href: cvData.contact.profiles.researchgate },
        { icon: 'fab fa-orcid', text: 'ORCID', href: `https://orcid.org/${cvData.contact.orcid}` }
    ];
    
    const linksHTML = links.map(link => `
        <a href="${link.href}" class="hero-link" target="_blank" rel="noopener">
            <i class="${link.icon}"></i> ${link.text}
        </a>
    `).join('');
    
    document.getElementById('hero-links').innerHTML = linksHTML;
}

// Render about section
function renderAbout() {
    document.getElementById('about-text').textContent = cvData.summary.short;
}

// Render metrics
function renderMetrics() {
    const metrics = [
        { value: cvData.metrics.total_publications, label: 'Publications' },
        { value: cvData.metrics.total_citations, label: 'Citations' },
        { value: cvData.metrics.h_index, label: 'h-index' },
        { value: cvData.metrics.phd_supervised, label: 'PhD Supervised' },
        { value: cvData.metrics.masters_supervised, label: 'Masters Supervised' },
        { value: cvData.metrics.projects_led, label: 'Research Projects' },
        { value: cvData.metrics.years_active, label: 'Years Active' },
        { value: cvData.education.length, label: 'Degrees' }
    ];
    
    const metricsHTML = metrics.map(m => `
        <div class="metric-card">
            <span class="metric-value">${m.value}</span>
            <span class="metric-label">${m.label}</span>
        </div>
    `).join('');
    
    document.getElementById('metrics-grid').innerHTML = metricsHTML;
}

// Render publications
function renderPublications() {
    // Flatten all publication types
    allPublications = [
        ...cvData.publications.journal_articles.map(p => ({ ...p, category: 'journal_articles' })),
        ...cvData.publications.conference_papers.map(p => ({ ...p, category: 'conference_papers' })),
        ...cvData.publications.book_chapters.map(p => ({ ...p, category: 'book_chapters' })),
        ...cvData.publications.technical.map(p => ({ ...p, category: 'technical' }))
    ];
    
    // Update counts
    document.getElementById('count-all').textContent = allPublications.length;
    document.getElementById('count-journal').textContent = cvData.publications.journal_articles.length;
    document.getElementById('count-conf').textContent = cvData.publications.conference_papers.length;
    document.getElementById('count-book').textContent = cvData.publications.book_chapters.length;
    document.getElementById('count-tech').textContent = cvData.publications.technical.length;
    
    updatePublicationsList();
}

// Update publications list based on filters
function updatePublicationsList() {
    // Filter publications
    let filtered = allPublications;
    
    // Apply type filter
    if (currentFilter !== 'all') {
        filtered = filtered.filter(p => p.category === currentFilter);
    }
    
    // Apply search filter
    const searchTerm = document.getElementById('pub-search')?.value.toLowerCase() || '';
    if (searchTerm) {
        filtered = filtered.filter(p => 
            p.title.toLowerCase().includes(searchTerm) ||
            (p.authors && p.authors.toLowerCase().includes(searchTerm)) ||
            (p.venue && p.venue.toLowerCase().includes(searchTerm))
        );
    }
    
    // Sort publications
    filtered = sortPublications(filtered);
    
    // Render
    const listEl = document.getElementById('publications-list');
    if (filtered.length === 0) {
        listEl.innerHTML = '<div class="no-results">No publications match your filters.</div>';
        return;
    }
    
    const pubsHTML = filtered.map(pub => `
        <div class="publication-card">
            <div class="pub-title">${pub.title}</div>
            ${pub.authors ? `<div class="pub-authors">${pub.authors}</div>` : ''}
            <div class="pub-meta">
                ${pub.venue ? `<span class="pub-venue">${pub.venue}</span>` : ''}
                ${pub.year ? `<span>• ${pub.year}</span>` : ''}
            </div>
            <div class="pub-badges">
                ${pub.year ? `<span class="badge badge-year">${pub.year}</span>` : ''}
                ${pub.citations ? `<span class="badge badge-citations"><i class="fas fa-quote-right"></i> ${pub.citations} citations</span>` : ''}
                ${pub.doi ? `<span class="badge badge-doi"><i class="fas fa-check-circle"></i> DOI</span>` : ''}
                <span class="badge badge-type">${formatCategory(pub.category)}</span>
            </div>
            ${pub.doi ? `<div style="margin-top: 0.5rem;"><a href="${pub.doi}" target="_blank" class="contact-link"><i class="fas fa-external-link-alt"></i> View Publication</a></div>` : ''}
        </div>
    `).join('');
    
    listEl.innerHTML = pubsHTML;
}

// Sort publications
function sortPublications(pubs) {
    const sorted = [...pubs];
    
    switch (currentSort) {
        case 'year-desc':
            return sorted.sort((a, b) => (b.year || 0) - (a.year || 0));
        case 'year-asc':
            return sorted.sort((a, b) => (a.year || 0) - (b.year || 0));
        case 'citations-desc':
            return sorted.sort((a, b) => (b.citations || 0) - (a.citations || 0));
        case 'title-asc':
            return sorted.sort((a, b) => a.title.localeCompare(b.title));
        default:
            return sorted;
    }
}

// Format category name
function formatCategory(category) {
    const names = {
        'journal_articles': 'Journal',
        'conference_papers': 'Conference',
        'book_chapters': 'Book Chapter',
        'technical': 'Technical'
    };
    return names[category] || category;
}

// Render positions
function renderPositions() {
    const positionsHTML = cvData.positions.map(pos => {
        const startDate = `${pos.start_month ? String(pos.start_month).padStart(2, '0') + '/' : ''}${pos.start_year || ''}`;
        const endDate = pos.end_year ? `${pos.end_month ? String(pos.end_month).padStart(2, '0') + '/' : ''}${pos.end_year}` : 'Present';
        
        let detailsHTML = '';
        
        // Add description if available
        if (pos.description) {
            detailsHTML += `<div class="timeline-details">${pos.description}</div>`;
        }
        
        // Add projects if available (for Videns position)
        if (pos.projects && pos.projects.length > 0) {
            detailsHTML += '<div class="position-projects">';
            detailsHTML += '<strong>Key Projects:</strong>';
            detailsHTML += '<ul class="project-list">';
            pos.projects.forEach(proj => {
                detailsHTML += `<li>
                    <strong>${proj.name}</strong> - ${proj.client}
                    <div class="project-details">${proj.description}</div>`;
                
                if (proj.deliverables && proj.deliverables.length > 0) {
                    detailsHTML += '<ul class="deliverables-list">';
                    proj.deliverables.slice(0, 3).forEach(d => {
                        detailsHTML += `<li>${d}</li>`;
                    });
                    if (proj.deliverables.length > 3) {
                        detailsHTML += `<li><em>...and ${proj.deliverables.length - 3} more deliverables</em></li>`;
                    }
                    detailsHTML += '</ul>';
                }
                
                detailsHTML += '</li>';
            });
            detailsHTML += '</ul>';
            detailsHTML += '</div>';
        }
        
        // Add technologies if available
        if (pos.technologies && pos.technologies.length > 0) {
            detailsHTML += `<div class="position-tech">
                <strong>Technologies:</strong> ${pos.technologies.join(', ')}
            </div>`;
        }
        
        // Add achievements if available
        if (pos.achievements && pos.achievements.length > 0) {
            detailsHTML += '<div class="position-achievements">';
            detailsHTML += '<strong>Key Achievements:</strong>';
            detailsHTML += '<ul>';
            pos.achievements.forEach(ach => {
                detailsHTML += `<li>${ach}</li>`;
            });
            detailsHTML += '</ul>';
            detailsHTML += '</div>';
        }
        
        return `
        <div class="timeline-item">
            <div class="timeline-title">${pos.role}</div>
            <div class="timeline-institution">
                ${pos.institution}${pos.location ? ` • ${pos.location}` : ''}
            </div>
            <div class="timeline-date">
                ${startDate} - ${endDate}
                ${pos.hours_per_week ? ` • ${pos.hours_per_week}h/week` : ''}
                ${pos.type ? ` • <span class="position-type">${pos.type}</span>` : ''}
            </div>
            ${detailsHTML}
        </div>
    `;
    }).join('');
    
    document.getElementById('positions-timeline').innerHTML = positionsHTML;
}

// Render education
function renderEducation() {
    const eduHTML = cvData.education.map(edu => `
        <div class="timeline-item">
            <div class="timeline-title">${edu.level} in ${edu.course}</div>
            <div class="timeline-institution">${edu.institution}</div>
            <div class="timeline-date">${edu.start_year} - ${edu.end_year}</div>
            ${edu.advisor ? `<div class="timeline-details"><strong>Advisor:</strong> ${edu.advisor}</div>` : ''}
            ${edu.thesis ? `<div class="timeline-details"><strong>Thesis:</strong> ${edu.thesis}</div>` : ''}
            ${edu.funding_agency ? `<div class="timeline-details"><strong>Funding:</strong> ${edu.funding_agency}</div>` : ''}
        </div>
    `).join('');
    
    document.getElementById('education-list').innerHTML = eduHTML;
}

// Render projects
function renderProjects() {
    const projectsHTML = cvData.projects.slice(0, 12).map(proj => `
        <div class="project-card">
            <div class="project-title">${proj.title}</div>
            ${proj.funding_agency ? `<div class="project-funding"><i class="fas fa-dollar-sign"></i> ${proj.funding_agency}</div>` : ''}
            <div class="project-period">${proj.start_year || ''} - ${proj.end_year || 'Ongoing'}</div>
        </div>
    `).join('');
    
    document.getElementById('projects-grid').innerHTML = projectsHTML;
}

// Render awards
function renderAwards() {
    const awardsHTML = cvData.awards.map(award => `
        <div class="award-item">
            <div class="award-title">${award.title}</div>
            <div class="award-org">${award.institution} • ${award.year}</div>
        </div>
    `).join('');
    
    document.getElementById('awards-list').innerHTML = awardsHTML;
}

// Render supervisions
function renderSupervisions() {
    const supervisionsHTML = cvData.supervisions.slice(0, 20).map(sup => `
        <div class="supervision-card">
            <div class="supervision-name">${sup.student}</div>
            <div class="supervision-level">${sup.level}</div>
            <div class="supervision-status">${sup.year || sup.start_year || ''}</div>
        </div>
    `).join('');
    
    document.getElementById('supervisions-grid').innerHTML = supervisionsHTML;
}

// Render contact
function renderContact() {
    const contacts = [
        { icon: 'fas fa-phone', label: 'Phone', value: cvData.contact.phone, link: `tel:${cvData.contact.phone}` },
        ...cvData.contact.emails.map(e => ({
            icon: 'fas fa-envelope',
            label: e.type,
            value: e.address,
            link: `mailto:${e.address}`
        })),
        { icon: 'fab fa-orcid', label: 'ORCID', value: cvData.contact.orcid, link: `https://orcid.org/${cvData.contact.orcid}` }
    ];
    
    const contactHTML = contacts.map(c => `
        <div class="contact-item">
            <i class="${c.icon}"></i>
            <div class="contact-label">${c.label}</div>
            <div class="contact-value">
                ${c.link ? `<a href="${c.link}" class="contact-link">${c.value}</a>` : c.value}
            </div>
        </div>
    `).join('');
    
    document.getElementById('contact-info').innerHTML = contactHTML;
}

// Initialize event listeners
function initializeEventListeners() {
    // Theme toggle
    document.getElementById('theme-toggle').addEventListener('click', toggleTheme);
    
    // Publication filters
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            currentFilter = e.target.dataset.type;
            updatePublicationsList();
        });
    });
    
    // Publication search
    document.getElementById('pub-search').addEventListener('input', updatePublicationsList);
    
    // Publication sort
    document.getElementById('pub-sort').addEventListener('change', (e) => {
        currentSort = e.target.value;
        updatePublicationsList();
    });
    
    // Smooth scroll for navigation
    document.querySelectorAll('.nav-links a').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = link.getAttribute('href');
            const targetEl = document.querySelector(targetId);
            if (targetEl) {
                targetEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });
}
