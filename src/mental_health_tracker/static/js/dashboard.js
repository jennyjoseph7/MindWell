// Dashboard Initialization
document.addEventListener('DOMContentLoaded', function() {
    initMoodChart();
    repairLinks();
    setupRefreshTips();
    applyAnimations();
    setupInteractiveCards();
    updateCurrentDate();
    renderRecentMoods();
    renderQuickLinks();
    setupMoodJourneySection();
    // Auto-fetch latest moods on load to ensure real-time data
    fetchLatestMoodsAndRender('auto');
});

// Initialize Mood Chart
function initMoodChart() {
    // Support both legacy id 'moodChart' and new id 'moodJourneyChart'
    const ctx = document.getElementById('moodJourneyChart') || document.getElementById('moodChart');
    if (!ctx) return;

    const container = ctx.closest('.chart-container') || ctx.parentElement;
    showChartSkeleton(container);

    // Gracefully handle missing Chart.js
    if (typeof window.Chart === 'undefined') {
        hideChartSkeleton(container);
        return;
    }

    // Derive labels and values from global if present, else fallback
    const hasRealData = Array.isArray(window.chartScores) && window.chartScores.length > 0;
    const labels = (Array.isArray(window.chartDates) && window.chartDates.length ? window.chartDates : ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']);
    // Convert 1-5 mood scores to percentage for shared axis
    const rawScores = hasRealData ? window.chartScores.slice() : [3, 4, 5, 4, 4, 5, 4];
    const data = rawScores.map(v => Math.round((v/5)*100));

    // Expose data for other widgets on the page
    window.__moodData = { labels: labels.slice(), scores: rawScores.slice(), percentages: data.slice(), hasRealData };

    const sentimentAligned = getAlignedSentiment(labels);
    const moodData = {
        labels: labels,
        datasets: [
            {
                label: 'Mood Level',
                data: data,
                fill: true,
                backgroundColor: 'rgba(139, 195, 74, 0.2)',
                borderColor: '#8bc34a',
                tension: 0.4,
                pointBackgroundColor: '#4caf50',
                pointBorderColor: '#fff',
                pointRadius: 5,
                pointHoverRadius: 7
            },
            sentimentAligned ? {
                label: 'Journal Sentiment',
                data: sentimentAligned,
                fill: false,
                borderColor: '#2196f3',
                backgroundColor: 'rgba(33, 150, 243, 0.25)',
                borderWidth: 2,
                pointRadius: 4,
                pointHoverRadius: 6,
                tension: 0.35,
            } : null
        ].filter(Boolean)
    };

    const config = {
        type: 'line',
        data: moodData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        callback: function(value) {
                            if (value === 0) return 'Low';
                            if (value === 50) return 'Neutral';
                            if (value === 100) return 'High';
                            return '';
                        }
                    },
                    grid: {
                        color: 'rgba(200, 200, 200, 0.15)'
                    }
                },
                x: {
                    grid: {
                        color: 'rgba(200, 200, 200, 0.15)'
                    }
                }
            },
            plugins: {
                legend: { display: true },
                tooltip: {
                    backgroundColor: 'rgba(76, 175, 80, 0.8)',
                    titleFont: { size: 14 },
                    bodyFont: { size: 13 },
                    callbacks: {
                        label: function(context) {
                            let label = '';
                            const value = context.parsed.y;
                            if (value >= 80) label = 'Very Positive';
                            else if (value >= 65) label = 'Positive';
                            else if (value >= 45) label = 'Neutral';
                            else if (value >= 30) label = 'Low';
                            else label = 'Very Low';
                            return `${context.dataset.label}: ${label} (${value}%)`;
                        }
                    }
                }
            }
        }
    };

    // Create or replace the chart instance safely
    try {
        if (window.__moodChart && typeof window.__moodChart.destroy === 'function') {
            window.__moodChart.destroy();
        }
    } catch(e) { /* noop */ }
    window.__moodChart = new Chart(ctx, config);

    // Hide skeleton once drawn
    setTimeout(() => hideChartSkeleton(container), 150);

    // Hide loading spinner if present
    const spinner = container.querySelector('.loading-spinner');
    if (spinner) spinner.style.display = 'none';

    // Update sample-data indicator
    const sampleTag = container.querySelector('#sample-data-indicator');
    if (sampleTag) sampleTag.style.display = hasRealData ? 'none' : 'flex';

    // Update stats cards if present
    updateMoodStats(rawScores);
}

// Helper: align journal sentiment to chart labels (best-effort)
function getAlignedSentiment(labels) {
    const s = window.journalSentiment || { sentiments: [] };
    if (!Array.isArray(s.sentiments) || s.sentiments.length === 0) return null;
    const values = s.sentiments.slice(-labels.length);
    if (values.length < labels.length) {
        const padVal = values.length ? values[0] : 50;
        while (values.length < labels.length) values.unshift(padVal);
    }
    return values;
}

// Setup refresh tips button
function setupRefreshTips() {
    const refreshBtn = document.getElementById('refresh-tips');
    if (!refreshBtn) return;

    const tips = [
        { icon: 'seedling', title: 'Forest Bathing', text: 'Spend 20 minutes under trees to reduce stress hormones' },
        { icon: 'water', title: 'Water Sounds', text: 'Listen to flowing water to activate your parasympathetic nervous system' },
        { icon: 'cloud-sun', title: 'Morning Light', text: 'Get 10 minutes of morning sunlight to regulate your circadian rhythm' },
        { icon: 'wind', title: 'Deep Breathing', text: 'Practice 4-7-8 breathing to calm your nervous system' },
        { icon: 'leaf', title: 'Plant Therapy', text: 'Care for indoor plants to improve focus and air quality' },
        { icon: 'moon', title: 'Nature Sleep', text: 'Use nature sounds for better sleep quality and relaxation' },
        { icon: 'tree', title: 'Grounding Practice', text: 'Walk barefoot on grass for 5 minutes to reduce inflammation' },
        { icon: 'umbrella-beach', title: 'Blue Space', text: 'Spend time near water to boost your mood and creativity' },
        { icon: 'mountain', title: 'Green Exercise', text: 'Exercise outdoors for greater mental health benefits' }
    ];

    refreshBtn.addEventListener('click', function() {
        const tipsList = document.querySelector('.tips-list');
        const tipItems = tipsList.querySelectorAll('.tip-item');

        // Get current tips
        const currentTips = [];
        tipItems.forEach(item => {
            const title = item.querySelector('h5').textContent;
            currentTips.push(title);
        });

        // Filter pool and ensure at least 3 items without recursion
        let availableTips = tips.filter(tip => !currentTips.includes(tip.title));
        if (availableTips.length < 3) availableTips = tips.slice();
        const selectedTips = shuffleArray(availableTips).slice(0, 3);

        // Update DOM with new tips
        tipItems.forEach((item, index) => {
            const tip = selectedTips[index];
            const icon = item.querySelector('.tip-icon i');
            const title = item.querySelector('h5');
            const text = item.querySelector('p');

            // Add fade out class
            item.classList.add('fade-out');

            // After animation completes, update content and fade back in
            setTimeout(() => {
                icon.className = `fas fa-${tip.icon}`;
                title.textContent = tip.title;
                text.textContent = tip.text;

                // Remove fade out and add fade in
                item.classList.remove('fade-out');
                item.classList.add('fade-in');

                // Remove fade in after animation completes
                setTimeout(() => { item.classList.remove('fade-in'); }, 500);
            }, 500);
        });

        // Button animation
        refreshBtn.classList.add('rotate-animation');
        setTimeout(() => { refreshBtn.classList.remove('rotate-animation'); }, 500);
    });
}

// Apply animations to elements
function applyAnimations() {
    // Add fade-in animation to glass cards
    const glassCards = document.querySelectorAll('.glass-card');
    glassCards.forEach((card, index) => {
        card.style.animationDelay = `${0.1 * index}s`;
        card.classList.add('fade-in-up');
    });

    // Add hover effect to action cards
    const actionCards = document.querySelectorAll('.action-card, .resource-card');
    actionCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            const overlay = this.querySelector('.nature-bg');
            if (overlay) overlay.classList.add('scale-bg');
        });
        card.addEventListener('mouseleave', function() {
            const overlay = this.querySelector('.nature-bg');
            if (overlay) overlay.classList.remove('scale-bg');
        });
    });
}

// Wire up Mood Journey section: refresh button, last-updated, and stats
function setupMoodJourneySection() {
    const refreshBtn = document.getElementById('refresh-mood-data');
    const chartEl = document.getElementById('moodJourneyChart');
    if (!refreshBtn && !chartEl) return; // Nothing to do on pages without the section

    // Initial stats compute from current global data
    if (window.__moodData && Array.isArray(window.__moodData.scores)) {
        updateMoodStats(window.__moodData.scores);
        updateLastUpdated('Just now');
        toggleSampleTag(window.__moodData.hasRealData);
    }

    if (refreshBtn) {
        refreshBtn.addEventListener('click', () => {
            console.debug('[Dashboard] Refresh clicked');
            fetchLatestMoodsAndRender('manual');
        });
    }
}

// Fetch latest moods from backend and re-render chart/insights/stats
async function fetchLatestMoodsAndRender(source) {
    const chartEl = document.getElementById('moodJourneyChart');
    const container = chartEl ? (chartEl.closest('.chart-container') || chartEl.parentElement) : null;
    const spinner = container && container.querySelector('.loading-spinner');
    if (spinner) spinner.style.display = 'block';

    try {
        const resp = await fetch('/api/moods/latest', { headers: { 'Accept': 'application/json' }, credentials: 'same-origin' });
        if (!resp.ok) throw new Error('Failed to load moods');
        const items = await resp.json();
        const labels = items.map(it => new Date(it.timestamp).toLocaleDateString(undefined, { weekday: 'short' }));
        const scores = items.map(it => it.mood);

        window.chartDates = labels;
        window.chartScores = scores;
        // Fetch journal sentiment series (optional)
        try {
            const sResp = await fetch('/api/journal/sentiment-series', { headers: { 'Accept': 'application/json' }, credentials: 'same-origin' });
            if (sResp.ok) {
                window.journalSentiment = await sResp.json();
            }
        } catch (e) { /* ignore */ }
        initMoodChart();
        updateMoodStats(scores);
        updateMoodInsights(scores);
        updateLastUpdated(new Date());
        toggleSampleTag(scores && scores.length > 0);
    } catch (e) {
        // On failure, still try to update insights/stats if we have previous globals
        if (Array.isArray(window.chartScores) && window.chartScores.length) {
            updateMoodStats(window.chartScores);
            updateMoodInsights(window.chartScores);
        }
        updateLastUpdated(new Date());
    } finally {
        if (spinner) spinner.style.display = 'none';
    }
}

function updateLastUpdated(date) {
    const el = document.getElementById('last-updated');
    if (!el) return;
    const label = (date instanceof Date) ? date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : (date || 'Just now');
    el.innerHTML = `<i class="fas fa-clock" style="font-size: 12px; margin-right: 5px; opacity: 0.7;"></i> Last updated: ${label}`;
}

function toggleSampleTag(hasRealData) {
    const tag = document.getElementById('sample-data-indicator');
    if (!tag) return;
    tag.style.display = hasRealData ? 'none' : 'flex';
}

function updateMoodStats(scores) {
    if (!Array.isArray(scores) || scores.length === 0) return;
    const todayEl = document.getElementById('today-mood');
    const avgEl = document.getElementById('average-mood');
    const rangeEl = document.getElementById('mood-range');

    const today = scores[scores.length - 1];
    const avg = (scores.reduce((a, b) => a + b, 0) / scores.length);
    const min = Math.min.apply(null, scores);
    const max = Math.max.apply(null, scores);

    if (todayEl) todayEl.textContent = `${today}/5`;
    if (avgEl) avgEl.textContent = `${avg.toFixed(1)}/5`;
    if (rangeEl) rangeEl.textContent = `${min}–${max}/5`;
}

// Update the Mood Insights card using latest scores
function updateMoodInsights(scores) {
    const container = document.querySelector('.mood-summary-card .mood-insights');
    if (!container || !Array.isArray(scores) || scores.length === 0) return;

    const recent = scores.slice(-7); // last week
    const latestAvg = average(recent.slice(-3));
    const olderAvg = average(recent.slice(0, Math.max(0, recent.length - 3)));
    const improving = !isNaN(latestAvg) && !isNaN(olderAvg) ? (latestAvg >= olderAvg) : true;
    const avgAll = average(scores);

    container.innerHTML = `
        <div class="insight-item">
            <div class="insight-icon ${improving ? 'positive' : 'negative'}">
                <i class="fas fa-${improving ? 'arrow-up' : 'arrow-down'}"></i>
            </div>
            <div class="insight-text">
                <h5>${improving ? 'Improving' : 'Declining'} Trend</h5>
                <p>Your mood has been ${improving ? 'improving' : 'declining'} over the past week</p>
            </div>
        </div>
        <div class="insight-item">
            <div class="insight-icon">
                <i class="fas fa-chart-bar"></i>
            </div>
            <div class="insight-text">
                <h5>Average Mood: ${isNaN(avgAll) ? '-' : avgAll.toFixed(1)}/5</h5>
                <p>Based on your recent mood entries</p>
            </div>
        </div>
    `;
}

function average(arr) {
    if (!arr || arr.length === 0) return NaN;
    return arr.reduce((a, b) => a + b, 0) / arr.length;
}
// Update current date
function updateCurrentDate() {
    const dateElement = document.querySelector('.welcome-text');
    if (!dateElement) return;
    const now = new Date();
    const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    const formattedDate = now.toLocaleDateString('en-US', options);
    dateElement.innerHTML = `Today is <span class="highlight-text">${formattedDate}</span>`;
}

// Add CSS animations and layout polish
document.head.insertAdjacentHTML('beforeend', `
<style>
    @keyframes fadeInUp { from { opacity: 0; transform: translateY(20px);} to { opacity: 1; transform: translateY(0);} }
    @keyframes rotate { from { transform: rotate(0deg);} to { transform: rotate(360deg);} }
    @keyframes fadeIn { from { opacity: 0;} to { opacity: 1;} }
    @keyframes fadeOut { from { opacity: 1;} to { opacity: 0;} }
    .fade-in-up { animation: fadeInUp 0.6s ease-out forwards; opacity: 0; }
    .rotate-animation { animation: rotate 0.5s ease-in-out; }
    .fade-in { animation: fadeIn 0.5s ease-out forwards; }
    .fade-out { animation: fadeOut 0.5s ease-out forwards; }
    .scale-bg { transform: scale(1.1) !important; opacity: 0.25 !important; }
    /* Equal heights for cards */
    .glass-card, .action-card, .resource-card { display: flex; flex-direction: column; height: 100%; }
    .glass-card .card-body { flex: 1; }
    /* Chart skeleton */
    .chart-skeleton { position: absolute; inset: 0; background: linear-gradient(90deg, rgba(255,255,255,0.05), rgba(255,255,255,0.12), rgba(255,255,255,0.05)); animation: shimmer 1.1s infinite; border-radius: 8px; }
    @keyframes shimmer { 0% { background-position: -200px 0;} 100% { background-position: calc(200px + 100%) 0;} }
    /* Interactive cards & ripple */
    .clickable-card { cursor: pointer; position: relative; transition: transform .08s ease, box-shadow .2s ease; outline: none; }
    .clickable-card:active { transform: translateY(1px) scale(0.997); }
    .clickable-card:focus-visible { box-shadow: 0 0 0 3px rgba(76,175,80,0.35), 0 0 0 6px rgba(76,175,80,0.15); }
    .ripple { position: absolute; border-radius: 50%; transform: scale(0); pointer-events: none; opacity: 0.5; background: currentColor; mix-blend-mode: overlay; animation: ripple 600ms ease-out forwards; }
    @keyframes ripple { to { transform: scale(12); opacity: 0; } }
    /* Minor polish for lists/buttons */
    .tips-list .tip-item { transition: transform .2s ease; }
    .tips-list .tip-item:hover { transform: translateY(-2px); }
</style>
`);

// Daily progress: replace fixed 75% with live percentage
document.addEventListener('DOMContentLoaded', function() {
    const progressCircle = document.querySelector('.progress-circle');
    if (!progressCircle) return;
    fetch('/api/daily-progress', { credentials: 'same-origin' })
        .then(r => r.ok ? r.json() : Promise.reject())
        .then(data => {
            const pct = Math.max(0, Math.min(100, parseInt(data.percentage||0)));
            const circumference = 2 * Math.PI * 54; // r=54 from SVG
            const offset = Math.round(circumference * (1 - pct / 100));
            const ring = progressCircle.querySelector('svg circle:nth-child(2)');
            if (ring) ring.setAttribute('stroke-dashoffset', String(offset));
            const label = progressCircle.querySelector('.progress-percentage');
            if (label) label.textContent = pct + '%';
        }).catch(() => { /* leave default */ });
});

// Make cards clickable and keyboard-accessible
function setupInteractiveCards() {
    const cards = document.querySelectorAll('.action-card, .resource-card, .glass-card');
    cards.forEach(card => {
        // Determine target: data-href, first anchor href, or data-action
        const anchor = card.querySelector('a[href]');
        const href = card.getAttribute('data-href') || (anchor ? anchor.getAttribute('href') : '');
        const action = card.getAttribute('data-action');
        if (!href && !action) return;

        card.classList.add('clickable-card');
        card.setAttribute('tabindex', '0');
        card.setAttribute('role', href ? 'link' : 'button');

        function activate(e) {
            if (href) {
                window.location.assign(href);
            } else if (action) {
                card.dispatchEvent(new CustomEvent('card:action', { bubbles: true, detail: { action } }));
            }
        }

        card.addEventListener('click', function(e) {
            // Allow inner anchors to work normally
            if (e.defaultPrevented) return;
            const isInnerLink = (e.target && (e.target.closest && e.target.closest('a[href]')));
            if (isInnerLink) return;
            activate(e);
            addRipple(e, card);
        });

        card.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                activate(e);
            }
        });
    });
}

// Ripple helper
function addRipple(e, el) {
    const rect = el.getBoundingClientRect();
    const ripple = document.createElement('span');
    ripple.className = 'ripple';
    const size = Math.max(rect.width, rect.height);
    ripple.style.width = ripple.style.height = `${size}px`;
    const x = (e.clientX || (rect.left + rect.width / 2)) - rect.left - size / 2;
    const y = (e.clientY || (rect.top + rect.height / 2)) - rect.top - size / 2;
    ripple.style.left = `${x}px`;
    ripple.style.top = `${y}px`;
    el.appendChild(ripple);
    setTimeout(() => ripple.remove(), 650);
}

// Fix common route links after template changes
function repairLinks() {
    const anchors = Array.from(document.querySelectorAll('a[href]'));
    anchors.forEach(a => {
        const href = a.getAttribute('href');
        if (href === '/games-dashboard') a.setAttribute('href', '/games/dashboard');
        if (/gratitude[- ]?wordle/i.test((a.textContent||'')) && !/\/games\/gratitude-wordle/.test(href)) {
            a.setAttribute('href', '/games/gratitude-wordle');
        }
    });
}

// Utility: shuffle
function shuffleArray(arr) {
    const a = arr.slice();
    for (let i = a.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
}

// Show/hide chart skeleton
function showChartSkeleton(container) {
    if (!container) return;
    container.style.position = container.style.position || 'relative';
    const sk = document.createElement('div');
    sk.className = 'chart-skeleton';
    sk.setAttribute('data-skeleton', 'true');
    container.appendChild(sk);
}
function hideChartSkeleton(container) {
    if (!container) return;
    const sk = container.querySelector('[data-skeleton="true"]');
    if (sk) sk.remove();
}

// Optional: Render recent moods mini-list if container exists
function renderRecentMoods() {
    const target = document.getElementById('recent-moods');
    if (!target || !(window.chartDates && window.chartScores)) return;
    const items = window.chartDates.slice(-5).map((d, i) => ({ d, s: window.chartScores.slice(-5)[i] }));
    target.innerHTML = items.map(it => `<div class="d-flex justify-content-between small"><span>${it.d}</span><span>${it.s}/5</span></div>`).join('');
}

// Optional: Render quick links if container exists
function renderQuickLinks() {
    const target = document.getElementById('quick-links');
    if (!target) return;
    const links = [
        { href: '/mood-tracker/new', label: 'Log Mood' },
        { href: '/journal/new', label: 'New Journal' },
        { href: '/music-therapy', label: 'Music Therapy' },
        { href: '/games', label: 'Games' }
    ];
    target.innerHTML = links.map(l => `<a class="btn btn-sm btn-outline-success me-2 mb-2" href="${l.href}">${l.label}</a>`).join('');
}
