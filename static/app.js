document.addEventListener('DOMContentLoaded', () => {
    
    // --- State and DOM Elements ---
    const API_URL = 'http://localhost:8000';
    let entryData = [];
    const token = localStorage.getItem('token');
    const userEmail = localStorage.getItem('user_email');

    // Modal elements
    const logModal = document.getElementById('log-modal');
    const openLogBtns = [document.getElementById('open-log-btn'), document.getElementById('open-log-btn-2')];
    const closeModalBtn = document.getElementById('close-modal');
    
    // Form elements
    const form = document.getElementById('tracker-form');
    const analyzeBtn = document.getElementById('analyze-btn');
    const btnText = analyzeBtn.querySelector('span');
    const loader = analyzeBtn.querySelector('.loader');

    // Dashboard Widget Elements
    const perfFill = document.getElementById('perf-fill');
    const perfScoreText = document.getElementById('perf-score-text');
    
    const avgStudyEl = document.getElementById('avg-study');
    const studyRing = document.getElementById('study-ring');
    const avgSleepEl = document.getElementById('avg-sleep');
    const sleepRing = document.getElementById('sleep-ring');
    const avgPhoneEl = document.getElementById('avg-phone');
    const phoneRing = document.getElementById('phone-ring');
    
    const curRiskEl = document.getElementById('cur-risk');
    
    const suggestionText = document.querySelector('.suggestion-text');
    const historyContainer = document.getElementById('history-container');
    const routineContainer = document.getElementById('routine-container');
    const logCountEl = document.getElementById('log-count');
    const streakCountEl = document.getElementById('streak-count');

    // Navigation logic
    const navLinks = document.querySelectorAll('.nav-link');
    const views = document.querySelectorAll('.view-content');

    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            // Ignore modal links
            if(link.id === 'open-log-btn') return;

            // Remove active from all links and views
            navLinks.forEach(l => l.classList.remove('active'));
            views.forEach(v => v.classList.add('hidden'));

            // Set active
            link.classList.add('active');
            const targetId = link.getAttribute('data-target');
            document.getElementById(targetId).classList.remove('hidden');

            // If routine, rebuild it
            if(targetId === 'routine-view') {
                generateRoutine();
            }
        });
    });

    // --- Modal Logic ---
    openLogBtns.forEach(btn => {
        if(btn) {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                logModal.classList.remove('hidden');
            });
        }
    });

    closeModalBtn.addEventListener('click', () => {
        logModal.classList.add('hidden');
    });

    // Close banner
    document.querySelector('.close-banner').addEventListener('click', function() {
        this.parentElement.style.display = 'none';
    });

    // --- Initialization ---
    // Update User Name
    if(userEmail) {
        document.getElementById('display-user-name').textContent = userEmail.split('@')[0];
    }

    // Logout logic
    document.getElementById('logout-btn').addEventListener('click', () => {
        localStorage.removeItem('token');
        localStorage.removeItem('user_email');
        window.location.href = 'login.html';
    });

    initDashboard();

    async function initDashboard() {
        await fetchEntries();
        await fetchInsights();
        updateDashboardWidgets();
    }

    async function fetchInsights() {
        try {
            const response = await fetch(`${API_URL}/entries/insights`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (response.ok) {
                const data = await response.json();
                document.getElementById('insights-container').innerHTML = `<p class="suggestion-text">${data.insights}</p>`;
            }
        } catch (e) { console.error("Insights Error:", e); }
    }

    // --- API Fetching ---
    async function fetchEntries() {
        try {
            const response = await fetch(`${API_URL}/entries/`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            if (response.status === 401) {
                window.location.href = 'login.html';
                return;
            }
            if (!response.ok) throw new Error('Failed to fetch stats');
            entryData = await response.json();
        } catch (error) {
            console.error("Fetch Error:", error);
            historyContainer.innerHTML = '<tr><td colspan="5" class="empty-state">Failed to connect to API</td></tr>';
        }
    }

    // --- Form Submission ---
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        btnText.classList.add('hidden');
        loader.classList.remove('hidden');
        analyzeBtn.disabled = true;

        const formData = {
            mood: document.querySelector('input[name="mood"]:checked').value,
            study_hours: parseFloat(document.getElementById('study-hours').value),
            sleep_hours: parseFloat(document.getElementById('sleep-hours').value),
            sleep_bedtime: document.getElementById('sleep-bedtime').value,
            sleep_quality: parseInt(document.getElementById('sleep-quality').value, 10),
            phone_usage_hours: parseFloat(document.getElementById('phone-hours').value),
            stress_level: parseInt(document.getElementById('stress-level').value, 10),
            comment: document.getElementById('comment').value
        };

        try {
            const response = await fetch(`${API_URL}/entries/`, {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(formData)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Network error');
            }

            await response.json(); // Log saved
            
            // Re-fetch and update
            await initDashboard();

            // Clear and close modal
            form.reset();
            logModal.classList.add('hidden');

        } catch (error) {
            console.error("Submit Error:", error);
            alert(error.message);
        } finally {
            btnText.classList.remove('hidden');
            loader.classList.add('hidden');
            analyzeBtn.disabled = false;
        }
    });

    // --- Update UI ---
    function updateDashboardWidgets() {
        if (entryData.length === 0) {
            historyContainer.innerHTML = '<tr><td colspan="5" class="empty-state">No logs yet. Click "Log Day" to start!</td></tr>';
            return;
        }

        // 1. Calculate Averages
        let totalStudy = 0, totalSleep = 0, totalPhone = 0, totalProd = 0;
        
        entryData.forEach(e => {
            totalStudy += e.study_hours;
            totalSleep += e.sleep_hours;
            totalPhone += e.phone_usage_hours;
            totalProd += e.productivity_score;
        });

        const count = entryData.length;
        const avgS = (totalStudy / count).toFixed(1);
        const avgSl = (totalSleep / count).toFixed(1);
        const avgP = (totalPhone / count).toFixed(1);
        const avgProd = Math.round(totalProd / count);

        // Update Stat Cards
        avgStudyEl.textContent = `${avgS}h`;
        studyRing.textContent = `${Math.round((avgS/10)*100)}%`; // arbitrary max 10 for dummy %

        avgSleepEl.textContent = `${avgSl}h`;
        sleepRing.textContent = `${Math.round((avgSl/8)*100)}%`; 

        avgPhoneEl.textContent = `${avgP}h`;
        phoneRing.textContent = `${Math.round((avgP/5)*100)}%`; 

        // Update Performance Semi-circle
        // 0% -> 45deg, 100% -> 225deg. Angle = 45 + (180 * score/100)
        const angle = 45 + (180 * (avgProd / 100));
        perfFill.style.transform = `rotate(${angle}deg)`;
        animateValue(perfScoreText, 0, avgProd, 1000, '%');

        // Recent Risk and Suggestion (from latest entry, index 0 since decscending)
        const latestEntry = entryData[0];
        curRiskEl.textContent = latestEntry.burnout_risk;
        
        const suggArr = latestEntry.suggestions ? latestEntry.suggestions.split(' | ') : ["Keep up the good work!"];
        suggestionText.textContent = suggArr[0]; // grab the most prominent suggestion

        // Update Table
        logCountEl.textContent = `(${count})`;
        streakCountEl.textContent = count; // dummy streak logic for now just uses count
        
        historyContainer.innerHTML = '';
        
        // Show up to 5 recent
        const recentLogs = entryData.slice(0, 5);
        recentLogs.forEach(entry => {
            let emoji = '😐';
            if (entry.mood === 'bad') emoji = '😫';
            if (entry.mood === 'great') emoji = '🚀';

            let riskClass = 'badge-low';
            if (entry.burnout_risk === 'High') riskClass = 'badge-high';
            else if (entry.burnout_risk === 'Medium') riskClass = 'badge-medium';

            const dateStr = new Date(entry.date + "Z").toLocaleDateString(undefined, { 
                month: 'short', day: 'numeric' 
            });

            const scorePercent = Math.round(entry.productivity_score);

            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>
                    <div class="log-date">
                        <span class="emoji">${emoji}</span>
                        <span>
                            <div>${dateStr}</div>
                            <div style="font-size:0.75rem; color:var(--text-light)">Study ${entry.study_hours}h</div>
                        </span>
                    </div>
                </td>
                <td style="text-transform: capitalize;">${entry.mood}</td>
                <td>
                    <div class="flex-align">
                        <div class="progress-bar"><div class="progress-fill" style="width: ${scorePercent}%"></div></div>
                        <span>${scorePercent}%</span>
                    </div>
                </td>
                <td><span class="status-badge ${riskClass}">${entry.burnout_risk}</span></td>
                <td><a href="#" style="color:var(--text-muted)"><i class="fa-solid fa-chevron-right"></i></a></td>
            `;
            historyContainer.appendChild(tr);
        });
    }

    // --- ML Routine Generation ---
    function generateRoutine() {
        routineContainer.innerHTML = '';
        if (entryData.length === 0) {
            routineContainer.innerHTML = '<div class="empty-state">Load a log to generate an ML routine.</div>';
            return;
        }

        const latest = entryData[0];
        let routineHTML = '';

        if (latest.burnout_risk === 'High') {
            routineHTML = `
                <div class="routine-card" style="border-left: 4px solid var(--red);">
                    <div class="routine-time">09:00 AM</div>
                    <div class="routine-details">
                        <h4>Light Review Session</h4>
                        <p>Limit study to 1 hour blocks. Review only, no new complex concepts.</p>
                    </div>
                </div>
                <div class="routine-card" style="border-left: 4px solid var(--primary);">
                    <div class="routine-time">10:30 AM</div>
                    <div class="routine-details">
                        <h4>Mandatory Rest / Walk</h4>
                        <p>Your ML analysis indicates high burnout. Step away from the screen for at least 45 minutes.</p>
                    </div>
                </div>
                <div class="routine-card" style="border-left: 4px solid var(--orange);">
                    <div class="routine-time">01:00 PM</div>
                    <div class="routine-details">
                        <h4>Digital Detox Lunch</h4>
                        <p>No phone usage during lunch. Yesterday you logged ${latest.phone_usage_hours} hours. Aim for half today.</p>
                    </div>
                </div>
                <div class="routine-card" style="border-left: 4px solid var(--blue);">
                    <div class="routine-time">08:00 PM</div>
                    <div class="routine-details">
                        <h4>Early Wind Down</h4>
                        <p>Prepare for sleep. Your average productivity plummets without adequate rest.</p>
                    </div>
                </div>
            `;
        } else if (latest.burnout_risk === 'Medium') {
            routineHTML = `
                <div class="routine-card" style="border-left: 4px solid var(--green);">
                    <div class="routine-time">08:30 AM</div>
                    <div class="routine-details">
                        <h4>Deep Work Block</h4>
                        <p>2 hour focused study session on your hardest tasks.</p>
                    </div>
                </div>
                <div class="routine-card" style="border-left: 4px solid var(--orange);">
                    <div class="routine-time">11:00 AM</div>
                    <div class="routine-details">
                        <h4>Pomodoro Break</h4>
                        <p>15 minute break before your next subject. Stretch and hydrate.</p>
                    </div>
                </div>
                <div class="routine-card" style="border-left: 4px solid var(--blue);">
                    <div class="routine-time">10:00 PM</div>
                    <div class="routine-details">
                        <h4>Sleep Prep</h4>
                        <p>Targeting 8 hours based on your model predictions to maintain focus.</p>
                    </div>
                </div>
            `;
        } else {
             routineHTML = `
                <div class="routine-card" style="border-left: 4px solid var(--green);">
                    <div class="routine-time">08:00 AM</div>
                    <div class="routine-details">
                        <h4>Max Productivity Zone</h4>
                        <p>Your burnout risk is Low! Tackle those big projects.</p>
                    </div>
                </div>
                <div class="routine-card" style="border-left: 4px solid var(--primary);">
                    <div class="routine-time">01:00 PM</div>
                    <div class="routine-details">
                        <h4>Maintain Rhythm</h4>
                        <p>Keep the momentum going with a solid afternoon block. Ensure you break every 90 minutes.</p>
                    </div>
                </div>
            `;
        }

        // Parse the personalized plan if it exists
        let planHTML = '';
        if (latest.suggestions.includes('|| PLAN:')) {
            const parts = latest.suggestions.split('|| PLAN:');
            const suggestions = parts[0].trim();
            const planSteps = parts[1].trim().split('|');
            
            planHTML = `
                <div class="card plan-card" style="margin-top: 20px; background: #e3f2fd; border: none;">
                    <h4 style="color: #1976d2; margin-bottom: 12px;"><i class="fa-solid fa-sparkles"></i> AI Personalized Routine</h4>
                    <div class="plan-steps">
                        ${planSteps.map(step => `
                            <div class="plan-step" style="display: flex; gap: 10px; margin-bottom: 10px; align-items: flex-start;">
                                <div class="step-bullet" style="color: #1976d2; font-weight: bold;">•</div>
                                <p style="font-size: 0.95rem; line-height: 1.4;">${step.trim()}</p>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
            
            // Update the suggestion text in the header to just show the core tips
            suggestionText.textContent = suggestions;
        }

        routineContainer.innerHTML = routineHTML + planHTML;
    }

    // Number Anim util
    function animateValue(obj, start, end, duration, suffix = '') {
        let startTimestamp = null;
        const step = (timestamp) => {
            if (!startTimestamp) startTimestamp = timestamp;
            const progress = Math.min((timestamp - startTimestamp) / duration, 1);
            obj.innerHTML = Math.floor(progress * (end - start) + start) + suffix;
            if (progress < 1) {
                window.requestAnimationFrame(step);
            }
        };
        window.requestAnimationFrame(step);
    }
});
