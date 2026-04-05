document.addEventListener('DOMContentLoaded', () => {
    const analyzeBtn = document.getElementById('analyzeBtn');
    const ticketInput = document.getElementById('ticketMessage');
    const resultsGrid = document.querySelector('.results-grid');
    const responseBox = document.querySelector('.response-box');
    const themeBtn = document.getElementById('themeBtn');
    const ticketList = document.getElementById('ticketList');
    const ticketCountEl = document.getElementById('ticketCount');

    let tickets = []; // Global store for tickets

    // Theme Switcher Logic
    let currentTheme = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-theme', currentTheme);
    themeBtn.innerText = currentTheme === 'light' ? '🌙' : '☀️';

    themeBtn.addEventListener('click', () => {
        currentTheme = currentTheme === 'light' ? 'dark' : 'light';
        document.documentElement.setAttribute('data-theme', currentTheme);
        localStorage.setItem('theme', currentTheme);
        themeBtn.innerText = currentTheme === 'light' ? '🌙' : '☀️';
    });

    // --- Analytics & Charts Logic ---

    let categoryChart, priorityChart, sentimentChart;
    const toastContainer = document.getElementById('toastContainer');

    function showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        const icon = type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️';
        
        toast.innerHTML = `
            <span class="toast-icon">${icon}</span>
            <span class="toast-message">${message}</span>
        `;
        
        toastContainer.appendChild(toast);
        
        // Auto remove after 3 seconds
        setTimeout(() => {
            toast.classList.add('fade-out');
            setTimeout(() => {
                toast.remove();
            }, 300);
        }, 3000);
    }

    function initCharts() {
        const commonOptions = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { color: '#64748b', font: { family: 'Inter', size: 12 } }
                }
            }
        };

        // Category Pie Chart
        categoryChart = new Chart(document.getElementById('categoryChart'), {
            type: 'pie',
            data: { labels: [], datasets: [{ data: [], backgroundColor: ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'] }] },
            options: commonOptions
        });

        // Priority Bar Chart
        priorityChart = new Chart(document.getElementById('priorityChart'), {
            type: 'bar',
            data: { labels: [], datasets: [{ label: 'Tickets', data: [], backgroundColor: '#6366f1', borderRadius: 6 }] },
            options: {
                ...commonOptions,
                scales: {
                    y: { beginAtZero: true, grid: { display: false }, ticks: { stepSize: 1, color: '#64748b' } },
                    x: { grid: { display: false }, ticks: { color: '#64748b' } }
                }
            }
        });

        // Sentiment Doughnut Chart
        sentimentChart = new Chart(document.getElementById('sentimentChart'), {
            type: 'doughnut',
            data: { labels: [], datasets: [{ data: [], backgroundColor: ['#10b981', '#64748b', '#ef4444'], cutout: '70%' }] },
            options: commonOptions
        });
    }

    async function updateAnalytics() {
        try {
            const response = await fetch('/analytics');
            if (!response.ok) throw new Error('Failed to fetch analytics');
            const data = await response.json();

            // Update Category Chart
            categoryChart.data.labels = Object.keys(data.category_distribution);
            categoryChart.data.datasets[0].data = Object.values(data.category_distribution);
            categoryChart.update();

            // Update Priority Chart
            priorityChart.data.labels = Object.keys(data.priority_distribution);
            priorityChart.data.datasets[0].data = Object.values(data.priority_distribution);
            priorityChart.update();

            // Update Sentiment Chart
            sentimentChart.data.labels = Object.keys(data.sentiment_distribution);
            sentimentChart.data.datasets[0].data = Object.values(data.sentiment_distribution);
            sentimentChart.update();

        } catch (error) {
            console.error('Analytics Error:', error);
        }
    }

    // --- History Logic ---

    async function fetchHistory() {
        try {
            const response = await fetch('/tickets');
            if (!response.ok) throw new Error('Failed to fetch history');
            const data = await response.json();
            tickets = data.tickets || [];
            renderTicketList();
        } catch (error) {
            console.error('History Error:', error);
        }
    }

    function renderTicketList() {
        ticketCountEl.innerText = tickets.length;
        if (tickets.length === 0) {
            ticketList.innerHTML = '<div class="empty-state">No tickets yet</div>';
            return;
        }

        // Sort by timestamp descending
        const sortedTickets = [...tickets].sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));

        ticketList.innerHTML = sortedTickets.map(t => {
            const date = new Date(t.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            return `
                <div class="ticket-item" data-id="${t.ticket_id}">
                    <div class="ticket-meta">
                        <span class="ticket-category">${t.category}</span>
                        <span class="ticket-date">${date}</span>
                    </div>
                    <div class="ticket-snippet">${t.message}</div>
                </div>
            `;
        }).join('');

        // Add event listeners to items
        document.querySelectorAll('.ticket-item').forEach(item => {
            item.addEventListener('click', () => {
                const ticketId = item.getAttribute('data-id');
                const ticket = tickets.find(t => t.ticket_id === ticketId);
                if (ticket) selectTicket(ticket, item);
            });
        });
    }

    function selectTicket(ticket, element) {
        // Update UI active state
        document.querySelectorAll('.ticket-item').forEach(i => i.classList.remove('active'));
        element.classList.add('active');

        // Display results
        displayResults(ticket);
    }

    // --- Analysis Logic ---

    async function handleAnalysis() {
        const message = ticketInput.value.trim();
        if (!message || message.length < 10) {
            alert('Please enter a valid ticket message (min 10 chars).');
            return;
        }

        // UI Loading State
        analyzeBtn.disabled = true;
        document.getElementById('spinner').style.display = 'block';
        document.getElementById('btnText').innerText = 'Analyzing...';
        
        // Clear previous selection highlight when starting new analysis
        document.querySelectorAll('.ticket-item').forEach(i => i.classList.remove('active'));

        try {
            const response = await fetch('/step', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: message,
                    user_id: 'saas_user_1'
                })
            });

            if (!response.ok) throw new Error('Backend error. Is the server running?');

            const data = await response.json();
            
            // Refresh history and analytics for real-time updates
            await fetchHistory();
            await updateAnalytics();
            
            displayResults(data);
            showToast('Analysis completed successfully!', 'success');
            ticketInput.value = ''; // Clear input on success
        } catch (error) {
            showToast('Error: ' + error.message, 'error');
        } finally {
            analyzeBtn.disabled = false;
            document.getElementById('spinner').style.display = 'none';
            document.getElementById('btnText').innerText = 'Submit for Analysis';
        }
    }

    function displayResults(data) {
        // Extract observation data from API response
        const observation = data.observation || data;
        
        // Map DOM elements
        document.getElementById('resCategory').innerText = observation.category || 'N/A';
        
        const priorityBadge = document.getElementById('resPriority');
        priorityBadge.innerText = observation.priority || 'Medium';
        priorityBadge.className = 'badge ' + (observation.priority ? observation.priority.toLowerCase() : 'medium');

        const sentimentEl = document.getElementById('resSentiment');
        sentimentEl.innerText = observation.sentiment || 'Neutral';
        sentimentEl.style.color = getSentimentColor(observation.sentiment || 'Neutral');

        document.getElementById('resResponse').innerText = '"' + (observation.response || 'No response generated.') + '"';

        // --- Escalation Logic ---
        const escBadge = document.getElementById('resEscalationBadge');
        const escReason = document.getElementById('resEscalationReason');

        if (observation.requires_escalation) {
            escBadge.style.display = 'flex';
            escReason.style.display = 'block';
            escReason.innerHTML = `<strong>Escalation Reason:</strong> ${observation.escalation_reason || 'Manual review required.'}`;
        } else {
            escBadge.style.display = 'none';
            escReason.style.display = 'none';
        }

        // Show segments with animation
        resultsGrid.style.display = 'grid';
        responseBox.style.display = 'block';
        
        resultsGrid.classList.remove('fade-in');
        responseBox.classList.remove('fade-in');
        void resultsGrid.offsetWidth; // Trigger reflow
        resultsGrid.classList.add('fade-in');
        responseBox.classList.add('fade-in');
    }

    function getSentimentColor(sentiment) {
        switch(sentiment.toLowerCase()) {
            case 'positive': return 'var(--green)';
            case 'negative': return 'var(--red)';
            default: return 'var(--text-secondary)';
        }
    }

    analyzeBtn.addEventListener('click', handleAnalysis);

    // Initial Load
    initCharts();
    fetchHistory();
    updateAnalytics();
});
