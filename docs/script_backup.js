// ===================================
// Configuration
// ===================================

const CONFIG = {
    pubsPerPage: 10,
    animationDuration: 300,
    scrollOffset: 80,
    counterSpeed: 2000,
};

// ===================================
// State Management
// ===================================

const state = {
    theme: localStorage.getItem('theme') || 'light',
    currentPubFilter: 'all',
    pubsLoaded: CONFIG.pubsPerPage,
    allPublications: [],
    filteredPublications: [],
};

// ===================================
// Theme Management
// ===================================

function initTheme() {
    document.documentElement.setAttribute('data-theme', state.theme);
    updateThemeIcon();
}

function toggleTheme() {
    state.theme = state.theme === 'light' ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', state.theme);
    localStorage.setItem('theme', state.theme);
    updateThemeIcon();
}

function updateThemeIcon() {
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        const icon = themeToggle.querySelector('i');
        icon.className = state.theme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
    }
}

// ===================================
// Navigation
// ===================================

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
            navToggle.classList.toggle('active');
        });
    }

    // Smooth scroll
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = link.getAttribute('href');
            const targetSection = document.querySelector(targetId);
            
            if (targetSection) {
                const offsetTop = targetSection.offsetTop - CONFIG.scrollOffset;
                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });

                // Close mobile menu
                if (navMenu) {
                    navMenu.classList.remove('active');
                }
                if (navToggle) {
                    navToggle.classList.remove('active');
                }
            }
        });
    });
}

// ===================================
// Counter Animation
// ===================================

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
    const counters = document.querySelectorAll('.stat-number[data-target]');
    
    const observerOptions = {
        threshold: 0.5,
        rootMargin: '0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && !entry.target.classList.contains('counted')) {
                entry.target.classList.add('counted');
                animateCounter(entry.target);
            }
        });
    }, observerOptions);

    counters.forEach(counter => observer.observe(counter));
}

// ===================================
// Publications Management
// ===================================

async function loadPublications() {
    try {
        const response = await fetch('cv_data.json');
        const data = await response.json();
        
        if (data.publications) {
            state.allPublications = data.publications;
            state.filteredPublications = [...state.allPublications];
            renderPublications();
        } else {
            showPublicationError('No publications found in data file');
        }
    } catch (error) {
        console.error('Error loading publications:', error);
        showPublicationError('Failed to load publications. Please try again later.');
    }
}

function filterPublications(filterType) {
    state.currentPubFilter = filterType;
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
        state.filteredPublications = [...state.allPublications];
    } else {
        state.filteredPublications = state.allPublications.filter(pub => {
            const titleMatch = pub.title.toLowerCase().includes(searchLower);
            const authorsMatch = pub.authors.toLowerCase().includes(searchLower);
            const venueMatch = pub.venue ? pub.venue.toLowerCase().includes(searchLower) : false;
            const yearMatch = pub.year ? pub.year.toString().includes(searchLower) : false;
            
            return titleMatch || authorsMatch || venueMatch || yearMatch;
        });
    }

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
            <div class="pub-placeholder">
                <i class="fas fa-search"></i>
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
        linksHTML += `<a href="https://doi.org/${pub.doi}" target="_blank" rel="noopener" class="pub-link">
            <i class="fas fa-link"></i> DOI
        </a>`;
    }
    if (pub.url) {
        linksHTML += `<a href="${pub.url}" target="_blank" rel="noopener" class="pub-link">
            <i class="fas fa-external-link-alt"></i> View
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
            ${linksHTML ? `<div class="pub-links">${linksHTML}</div>` : ''}
        </div>
    `;

    return div;
}

function getBadgeClass(type) {
    const badgeMap = {
        'journal': 'badge-journal',
        'conference': 'badge-conference',
        'book': 'badge-book',
        'dataset': 'badge-book',
        'review': 'badge-review'
    };
    return badgeMap[type] || 'badge-journal';
}

function getBadgeText(type) {
    const textMap = {
        'journal': 'Journal',
        'conference': 'Conference',
        'book': 'Book Chapter',
        'dataset': 'Dataset',
        'review': 'Review'
    };
    return textMap[type] || 'Publication';
}

function loadMorePublications() {
    state.pubsLoaded += CONFIG.pubsPerPage;
    renderPublications();
}

function showLoadMoreButton() {
    const container = document.querySelector('.load-more-container');
    if (container) {
        container.style.display = 'block';
    }
}

function hideLoadMoreButton() {
    const container = document.querySelector('.load-more-container');
    if (container) {
        container.style.display = 'none';
    }
}

function showPublicationError(message) {
    const pubList = document.getElementById('pubList');
    if (pubList) {
        pubList.innerHTML = `
            <div class="pub-placeholder">
                <i class="fas fa-exclamation-triangle"></i>
                <p>${message}</p>
            </div>
        `;
    }
}

// ===================================
// Back to Top Button
// ===================================

function initBackToTop() {
    const backToTopBtn = document.getElementById('backToTop');
    if (!backToTopBtn) return;

    window.addEventListener('scroll', () => {
        if (window.scrollY > 500) {
            backToTopBtn.classList.add('visible');
        } else {
            backToTopBtn.classList.remove('visible');
        }
    });

    backToTopBtn.addEventListener('click', () => {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

// ===================================
// Experience Timeline
// ===================================

function initExperience() {
    const showMoreBtn = document.getElementById('showMoreExp');
    if (showMoreBtn) {
        showMoreBtn.addEventListener('click', () => {
            alert('Full experience history feature coming soon! View complete CV in PDF format.');
        });
    }
}

// ===================================
// Scroll Animations
// ===================================

function initScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -100px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    const animatedElements = document.querySelectorAll('.timeline-item, .research-card, .contact-card');
    animatedElements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });
}

// ===================================
// Event Listeners Setup
// ===================================

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

    // Hero scroll indicator
    const scrollDown = document.querySelector('.scroll-down');
    if (scrollDown) {
        scrollDown.addEventListener('click', () => {
            const aboutSection = document.getElementById('about');
            if (aboutSection) {
                aboutSection.scrollIntoView({ behavior: 'smooth' });
            }
        });
    }

    // Smooth scroll for all internal links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                const offsetTop = targetElement.offsetTop - CONFIG.scrollOffset;
                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });
            }
        });
    });
}

// ===================================
// Initialization
// ===================================

function init() {
    console.log('Initializing Academic CV Portfolio...');
    
    // Initialize theme first
    initTheme();
    
    // Initialize navigation
    initNavigation();
    
    // Initialize counters
    initCounters();
    
    // Initialize back to top button
    initBackToTop();
    
    // Initialize experience section
    initExperience();
    
    // Initialize scroll animations
    initScrollAnimations();
    
    // Setup all event listeners
    setupEventListeners();
    
    // Load publications
    loadPublications();
    
    console.log('Initialization complete!');
}

// ===================================
// Start Application
// ===================================

// Wait for DOM to be ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}

// Handle page visibility for performance
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        console.log('Page hidden - pausing animations');
    } else {
        console.log('Page visible - resuming');
    }
});

// Export functions for potential external use
window.CVPortfolio = {
    toggleTheme,
    filterPublications,
    searchPublications,
    loadMorePublications,
};
