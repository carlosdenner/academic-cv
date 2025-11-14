// ===================================
// MODERN PORTFOLIO - JAVASCRIPT
// Interactive Features & Data Visualizations
// ===================================

/* ===================================
   Configuration
   =================================== */

const CONFIG = {
    pubsPerPage: 10,
    counterSpeed: 2000,
    scrollOffset: 80,
    particleCount: 50,
    particleSpeed: 0.5,
};

/* ===================================
   State Management
   =================================== */

const state = {
    theme: localStorage.getItem('theme') || 'light',
    currentFilter: 'all',
    pubsLoaded: CONFIG.pubsPerPage,
    allPublications: [],
    filteredPublications: [],
    charts: {},
};

/* ===================================
   Theme Management
   =================================== */

function initTheme() {
    document.documentElement.setAttribute('data-theme', state.theme);
    updateThemeIcon();
}

function toggleTheme() {
    state.theme = state.theme === 'light' ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', state.theme);
    localStorage.setItem('theme', state.theme);
    updateThemeIcon();
    updateCharts();
}

function updateThemeIcon() {
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        const icon = themeToggle.querySelector('i');
        icon.className = state.theme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
    }
}

/* ===================================
   Particle Background
   =================================== */

class ParticleSystem {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.particles = [];
        this.resize();
        this.init();
        
        window.addEventListener('resize', () => this.resize());
    }
    
    resize() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
    }
    
    init() {
        for (let i = 0; i < CONFIG.particleCount; i++) {
            this.particles.push({
                x: Math.random() * this.canvas.width,
                y: Math.random() * this.canvas.height,
                vx: (Math.random() - 0.5) * CONFIG.particleSpeed,
                vy: (Math.random() - 0.5) * CONFIG.particleSpeed,
                radius: Math.random() * 2 + 1,
            });
        }
    }
    
    update() {
        this.particles.forEach(particle => {
            particle.x += particle.vx;
            particle.y += particle.vy;
            
            if (particle.x < 0 || particle.x > this.canvas.width) particle.vx *= -1;
            if (particle.y < 0 || particle.y > this.canvas.height) particle.vy *= -1;
        });
    }
    
    draw() {
        const isDark = state.theme === 'dark';
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Draw particles
        this.ctx.fillStyle = isDark ? 'rgba(148, 163, 184, 0.5)' : 'rgba(100, 116, 139, 0.3)';
        this.particles.forEach(particle => {
            this.ctx.beginPath();
            this.ctx.arc(particle.x, particle.y, particle.radius, 0, Math.PI * 2);
            this.ctx.fill();
        });
        
        // Draw connections
        this.ctx.strokeStyle = isDark ? 'rgba(148, 163, 184, 0.1)' : 'rgba(100, 116, 139, 0.1)';
        this.ctx.lineWidth = 1;
        
        for (let i = 0; i < this.particles.length; i++) {
            for (let j = i + 1; j < this.particles.length; j++) {
                const dx = this.particles[i].x - this.particles[j].x;
                const dy = this.particles[i].y - this.particles[j].y;
                const distance = Math.sqrt(dx * dx + dy * dy);
                
                if (distance < 150) {
                    this.ctx.beginPath();
                    this.ctx.moveTo(this.particles[i].x, this.particles[i].y);
                    this.ctx.lineTo(this.particles[j].x, this.particles[j].y);
                    this.ctx.stroke();
                }
            }
        }
    }
    
    animate() {
        this.update();
        this.draw();
        requestAnimationFrame(() => this.animate());
    }
}

/* ===================================
   Navigation
   =================================== */

function initNavigation() {
    const navbar = document.getElementById('navbar');
    const navToggle = document.getElementById('navToggle');
    const navMenu = document.getElementById('navMenu');
    const navLinks = document.querySelectorAll('.nav-link');
    
    // Scroll effect
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });
    
    // Mobile menu toggle
    if (navToggle) {
        navToggle.addEventListener('click', () => {
            navMenu.classList.toggle('active');
        });
    }
    
    // Smooth scroll & close mobile menu
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = link.getAttribute('href');
            const target = document.querySelector(targetId);
            
            if (target) {
                const offsetTop = target.offsetTop - CONFIG.scrollOffset;
                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });
                
                if (navMenu) {
                    navMenu.classList.remove('active');
                }
            }
        });
    });
}

/* ===================================
   Counter Animations
   =================================== */

function animateCounter(element) {
    const target = parseInt(element.getAttribute('data-target'));
    const duration = CONFIG.counterSpeed;
    const increment = target / (duration / 16);
    let current = 0;
    
    const updateCounter = () => {
        current += increment;
        if (current < target) {
            element.textContent = Math.floor(current);
            requestAnimationFrame(updateCounter);
        } else {
            element.textContent = target;
        }
    };
    
    updateCounter();
}

function initCounters() {
    const counters = document.querySelectorAll('.counter[data-target], .stat-value[data-target]');
    
    if (counters.length === 0) {
        console.warn('No counters found');
        return;
    }
    
    console.log(`Found ${counters.length} counters to animate`);
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && !entry.target.classList.contains('counted')) {
                entry.target.classList.add('counted');
                animateCounter(entry.target);
            }
        });
    }, { threshold: 0.1 });
    
    counters.forEach(counter => {
        // Set initial value
        counter.textContent = '0';
        observer.observe(counter);
    });
}

/* ===================================
   Data Visualizations - Chart.js
   =================================== */

function getChartColors() {
    const isDark = state.theme === 'dark';
    return {
        primary: isDark ? '#60a5fa' : '#3b82f6',
        accent: isDark ? '#a78bfa' : '#8b5cf6',
        success: '#10b981',
        warning: '#f59e0b',
        danger: '#ef4444',
        text: isDark ? '#f1f5f9' : '#0f172a',
        textSecondary: isDark ? '#cbd5e1' : '#475569',
        grid: isDark ? '#334155' : '#e2e8f0',
    };
}

function createPublicationsChart() {
    const canvas = document.getElementById('publicationsChart');
    if (!canvas) return;
    
    const colors = getChartColors();
    const ctx = canvas.getContext('2d');
    
    if (state.charts.publications) {
        state.charts.publications.destroy();
    }
    
    state.charts.publications = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['2010', '2012', '2014', '2016', '2018', '2020', '2022', '2024'],
            datasets: [
                {
                    label: 'h-index',
                    data: [3, 5, 8, 11, 14, 16, 17, 18],
                    borderColor: colors.primary,
                    backgroundColor: colors.primary + '20',
                    tension: 0.4,
                    fill: false,
                    pointRadius: 5,
                    pointHoverRadius: 7,
                    borderWidth: 3,
                },
                {
                    label: 'i10-index',
                    data: [2, 6, 11, 16, 20, 24, 26, 28],
                    borderColor: colors.accent,
                    backgroundColor: colors.accent + '20',
                    tension: 0.4,
                    fill: false,
                    pointRadius: 5,
                    pointHoverRadius: 7,
                    borderWidth: 3,
                },
                {
                    label: 'Publications',
                    data: [5, 8, 12, 15, 18, 22, 25, 28],
                    borderColor: colors.success,
                    backgroundColor: colors.success + '20',
                    tension: 0.4,
                    fill: true,
                    pointRadius: 5,
                    pointHoverRadius: 7,
                    borderWidth: 2,
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        color: colors.text,
                        usePointStyle: true,
                        padding: 15,
                        font: {
                            size: 12,
                            weight: '500'
                        }
                    }
                },
                tooltip: {
                    backgroundColor: colors.text,
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    borderColor: colors.primary,
                    borderWidth: 1,
                    padding: 12,
                    displayColors: true,
                }
            },
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    beginAtZero: true,
                    grid: {
                        color: colors.grid,
                    },
                    ticks: {
                        color: colors.textSecondary,
                    },
                },
                x: {
                    grid: {
                        display: false,
                    },
                    ticks: {
                        color: colors.textSecondary,
                    }
                }
            }
        }
    });
}

function createAreasChart() {
    const canvas = document.getElementById('areasChart');
    if (!canvas) return;
    
    const colors = getChartColors();
    const ctx = canvas.getContext('2d');
    
    if (state.charts.areas) {
        state.charts.areas.destroy();
    }
    
    state.charts.areas = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['AI/ML', 'Data Science', 'IT Governance', 'Open Source', 'Software Eng', 'Other'],
            datasets: [{
                data: [30, 25, 20, 15, 5, 5],
                backgroundColor: [
                    colors.primary,
                    colors.accent,
                    '#06b6d4',
                    colors.success,
                    colors.warning,
                    colors.danger,
                ],
                borderWidth: 0,
                hoverOffset: 10,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: colors.textSecondary,
                        padding: 15,
                        font: {
                            size: 12,
                            family: 'Inter'
                        }
                    }
                },
                tooltip: {
                    backgroundColor: colors.text,
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    padding: 12,
                }
            }
        }
    });
}

function createImpactChart() {
    const canvas = document.getElementById('impactChart');
    if (!canvas) return;
    
    const colors = getChartColors();
    const ctx = canvas.getContext('2d');
    
    if (state.charts.impact) {
        state.charts.impact.destroy();
    }
    
    state.charts.impact = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Q1', 'Q2', 'Q3', 'Q4'],
            datasets: [{
                label: 'Top Quartile',
                data: [35, 28, 20, 16],
                backgroundColor: colors.primary,
                borderRadius: 8,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: colors.text,
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    padding: 12,
                    displayColors: false,
                    callbacks: {
                        label: function(context) {
                            return context.parsed.y + '% of publications';
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 40,
                    grid: {
                        color: colors.grid,
                    },
                    ticks: {
                        color: colors.textSecondary,
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                },
                x: {
                    grid: {
                        display: false,
                    },
                    ticks: {
                        color: colors.textSecondary,
                    }
                }
            }
        }
    });
}

function createSkillsRadar() {
    const canvas = document.getElementById('skillsRadar');
    if (!canvas) return;
    
    const colors = getChartColors();
    const ctx = canvas.getContext('2d');
    
    if (state.charts.skills) {
        state.charts.skills.destroy();
    }
    
    state.charts.skills = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: ['AI/ML', 'Data Science', 'Governance', 'Open Source', 'Systems', 'Research'],
            datasets: [{
                label: 'Proficiency',
                data: [95, 98, 92, 90, 94, 96],
                backgroundColor: colors.primary + '30',
                borderColor: colors.primary,
                borderWidth: 3,
                pointBackgroundColor: colors.primary,
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointRadius: 5,
                pointHoverRadius: 7,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: colors.text,
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    padding: 12,
                    displayColors: false,
                    callbacks: {
                        label: function(context) {
                            return context.parsed.r + '% proficiency';
                        }
                    }
                }
            },
            scales: {
                r: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        stepSize: 20,
                        color: colors.textSecondary,
                        backdropColor: 'transparent',
                    },
                    grid: {
                        color: colors.grid,
                    },
                    pointLabels: {
                        color: colors.textSecondary,
                        font: {
                            size: 12,
                            family: 'Inter'
                        }
                    }
                }
            }
        }
    });
}

function initCharts() {
    if (typeof Chart === 'undefined') {
        console.error('Chart.js not loaded');
        return;
    }
    
    createPublicationsChart();
    createAreasChart();
    createImpactChart();
    createSkillsRadar();
}

function updateCharts() {
    initCharts();
}

/* ===================================
   Publications Management
   =================================== */

const samplePublications = [
    {
        title: "Building an LLM Firewall: Multi-Phase Defense Against Prompt Injection Attacks",
        authors: "Santos, C.D., et al.",
        venue: "Communications of the ACM",
        year: 2024,
        type: "journal",
        status: "under-review",
        doi: "",
    },
    {
        title: "Evaluating and Mitigating Hallucinations in RAG Systems",
        authors: "Santos, C.D., Johnson, M., Lee, K.",
        venue: "In Preparation",
        year: 2025,
        type: "journal",
        status: "in-preparation",
        doi: "",
    },
    {
        title: "The AI Recommendation System of Jooay.com: Enhancing Digital Inclusion",
        authors: "Santos, C.D., Research Team",
        venue: "In Preparation",
        year: 2025,
        type: "conference",
        status: "in-preparation",
        doi: "",
    },
    // Add more sample publications here
];

async function loadPublications() {
    try {
        const response = await fetch('cv_data.json');
        const data = await response.json();
        
        if (data.publications && data.publications.length > 0) {
            state.allPublications = data.publications;
        } else {
            state.allPublications = samplePublications;
        }
        
        state.filteredPublications = [...state.allPublications];
        renderPublications();
    } catch (error) {
        console.log('Using sample publications');
        state.allPublications = samplePublications;
        state.filteredPublications = [...state.allPublications];
        renderPublications();
    }
}

function filterPublications(filterType) {
    state.currentFilter = filterType;
    state.pubsLoaded = CONFIG.pubsPerPage;
    
    // Update filter buttons
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.getAttribute('data-filter') === filterType) {
            btn.classList.add('active');
        }
    });
    
    // Apply filter
    if (filterType === 'all') {
        state.filteredPublications = [...state.allPublications];
    } else if (filterType === 'inprep') {
        state.filteredPublications = state.allPublications.filter(pub =>
            pub.status === 'under-review' || pub.status === 'in-preparation'
        );
    } else {
        state.filteredPublications = state.allPublications.filter(pub =>
            pub.type === filterType
        );
    }
    
    renderPublications();
}

function searchPublications(query) {
    const searchLower = query.toLowerCase().trim();
    
    if (!searchLower) {
        filterPublications(state.currentFilter);
        return;
    }
    
    state.filteredPublications = state.allPublications.filter(pub => {
        const titleMatch = pub.title.toLowerCase().includes(searchLower);
        const authorsMatch = pub.authors.toLowerCase().includes(searchLower);
        const venueMatch = pub.venue ? pub.venue.toLowerCase().includes(searchLower) : false;
        const yearMatch = pub.year ? pub.year.toString().includes(searchLower) : false;
        
        return titleMatch || authorsMatch || venueMatch || yearMatch;
    });
    
    state.pubsLoaded = CONFIG.pubsPerPage;
    renderPublications();
}

function renderPublications() {
    const pubList = document.getElementById('pubList');
    if (!pubList) return;
    
    pubList.innerHTML = '';
    
    const pubs = state.filteredPublications.slice(0, state.pubsLoaded);
    
    if (pubs.length === 0) {
        pubList.innerHTML = `
            <div style="text-align: center; padding: 3rem; color: var(--text-tertiary);">
                <i class="fas fa-search" style="font-size: 3rem; margin-bottom: 1rem;"></i>
                <p>No publications found matching your criteria.</p>
            </div>
        `;
        hideLoadMoreButton();
        return;
    }
    
    pubs.forEach(pub => {
        const pubElement = createPublicationElement(pub);
        pubList.appendChild(pubElement);
    });
    
    // Show/hide load more button
    if (state.pubsLoaded < state.filteredPublications.length) {
        showLoadMoreButton();
    } else {
        hideLoadMoreButton();
    }
}

function createPublicationElement(pub) {
    const div = document.createElement('div');
    div.className = 'pub-item';
    
    const badgeClass = getBadgeClass(pub.type);
    const badgeText = getBadgeText(pub.type);
    
    let linksHTML = '';
    if (pub.doi) {
        linksHTML += `<a href="https://doi.org/${pub.doi}" target="_blank" rel="noopener" style="color: var(--primary); font-size: 0.875rem; text-decoration: none;">
            <i class="fas fa-link"></i> DOI
        </a>`;
    }
    
    div.innerHTML = `
        <div class="pub-title">
            ${pub.doi ? `<a href="https://doi.org/${pub.doi}" target="_blank" rel="noopener">${pub.title}</a>` : pub.title}
        </div>
        <div class="pub-authors">${pub.authors}</div>
        ${pub.venue ? `<div class="pub-venue">${pub.venue}${pub.year ? `, ${pub.year}` : ''}</div>` : ''}
        <div class="pub-meta">
            <span class="badge ${badgeClass}">${badgeText}</span>
            ${linksHTML}
        </div>
    `;
    
    return div;
}

function getBadgeClass(type) {
    const map = {
        'journal': 'badge-journal',
        'conference': 'badge-conference',
        'book': 'badge-book',
        'review': 'badge-review'
    };
    return map[type] || 'badge-journal';
}

function getBadgeText(type) {
    const map = {
        'journal': 'Journal',
        'conference': 'Conference',
        'book': 'Book Chapter',
        'review': 'Review'
    };
    return map[type] || 'Publication';
}

function loadMorePublications() {
    state.pubsLoaded += CONFIG.pubsPerPage;
    renderPublications();
}

function showLoadMoreButton() {
    const btn = document.getElementById('loadMorePubs');
    if (btn) btn.style.display = 'inline-flex';
}

function hideLoadMoreButton() {
    const btn = document.getElementById('loadMorePubs');
    if (btn) btn.style.display = 'none';
}

/* ===================================
   Back to Top Button
   =================================== */

function initBackToTop() {
    const btn = document.getElementById('backToTop');
    if (!btn) return;
    
    window.addEventListener('scroll', () => {
        if (window.scrollY > 500) {
            btn.classList.add('visible');
        } else {
            btn.classList.remove('visible');
        }
    });
    
    btn.addEventListener('click', () => {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

/* ===================================
   Form Handlers
   =================================== */

async function handleContactSubmit(e) {
    e.preventDefault();
    const form = e.target;
    const formData = new FormData(form);
    const status = document.getElementById('formStatus');
    const submitBtn = form.querySelector('button[type="submit"]');
    
    // Disable button during submission
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span>Sending...</span><i class="fas fa-spinner fa-spin"></i>';
    
    try {
        const response = await fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: {
                'Accept': 'application/json'
            }
        });
        
        if (response.ok) {
            status.textContent = '✅ Message sent successfully! I\'ll get back to you soon.';
            status.className = 'form-status success';
            form.reset();
        } else {
            throw new Error('Form submission failed');
        }
    } catch (error) {
        status.textContent = '❌ Oops! There was a problem. Please email me directly.';
        status.className = 'form-status error';
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<span>Send Message</span><i class="fas fa-arrow-right"></i>';
        
        // Hide status after 5 seconds
        setTimeout(() => {
            status.className = 'form-status';
        }, 5000);
    }
}

async function handleNewsletterSubmit(e) {
    e.preventDefault();
    const form = e.target;
    const formData = new FormData(form);
    const status = document.getElementById('newsletterStatus');
    const submitBtn = form.querySelector('button[type="submit"]');
    
    // Disable button during submission
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    
    try {
        const response = await fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: {
                'Accept': 'application/json'
            }
        });
        
        if (response.ok) {
            status.textContent = '🎉 Welcome! Check your email to confirm.';
            status.className = 'form-status success';
            form.reset();
        } else {
            throw new Error('Form submission failed');
        }
    } catch (error) {
        status.textContent = '❌ Error subscribing. Please try again.';
        status.className = 'form-status error';
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="fas fa-arrow-right"></i>';
        
        // Hide status after 5 seconds
        setTimeout(() => {
            status.className = 'form-status';
        }, 5000);
    }
}

/* ===================================
   Event Listeners
   =================================== */

function setupEventListeners() {
    // Theme toggle
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }
    
    // Publication search
    const pubSearch = document.getElementById('pubSearch');
    if (pubSearch) {
        let searchTimeout;
        pubSearch.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                searchPublications(e.target.value);
            }, 300);
        });
    }
    
    // Publication filters
    const filterButtons = document.querySelectorAll('.filter-btn');
    filterButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const filter = btn.getAttribute('data-filter');
            filterPublications(filter);
        });
    });
    
    // Load more publications
    const loadMoreBtn = document.getElementById('loadMorePubs');
    if (loadMoreBtn) {
        loadMoreBtn.addEventListener('click', loadMorePublications);
    }
    
    // Contact Form
    const contactForm = document.getElementById('contactForm');
    if (contactForm) {
        contactForm.addEventListener('submit', handleContactSubmit);
    }
    
    // Newsletter Form
    const newsletterForm = document.getElementById('newsletterForm');
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', handleNewsletterSubmit);
    }
    
    // Smooth scroll for all internal links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const target = document.querySelector(targetId);
            if (target) {
                const offsetTop = target.offsetTop - CONFIG.scrollOffset;
                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });
            }
        });
    });
}

/* ===================================
   Initialization
   =================================== */

function init() {
    console.log('🚀 Initializing Modern Portfolio...');
    
    // Initialize theme
    initTheme();
    
    // Initialize particle background
    const canvas = document.getElementById('particleCanvas');
    if (canvas) {
        const particles = new ParticleSystem(canvas);
        particles.animate();
    }
    
    // Initialize navigation
    initNavigation();
    
    // Initialize counters
    initCounters();
    
    // Initialize charts
    setTimeout(() => {
        initCharts();
    }, 100);
    
    // Initialize back to top button
    initBackToTop();
    
    // Setup event listeners
    setupEventListeners();
    
    // Load publications
    loadPublications();
    
    console.log('✨ Portfolio initialized successfully!');
}

/* ===================================
   Start Application
   =================================== */

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}

// Export for external use
window.ModernPortfolio = {
    toggleTheme,
    filterPublications,
    searchPublications,
    loadMorePublications,
    updateCharts,
};
