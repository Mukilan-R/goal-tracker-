const API = {
    dashboard: '/api/dashboard-data',
    habits: '/api/habits',
    streaks: '/api/streaks',
    career: '/api/career-progress',
    fear: '/api/fear-challenges',
    weekly: '/api/weekly-review',
    goals: '/api/monthly-goals',
    mood: '/api/mood',
    analytics: '/api/analytics',
    plan: '/api/transformation-plan',
};

let charts = {};
let habitsData = [];

document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initNavigation();
    initMobileMenu();
    loadDashboard();

    document.getElementById('saveHabits')?.addEventListener('click', saveHabits);
    document.getElementById('saveCareer')?.addEventListener('click', saveCareer);
    document.getElementById('addFear')?.addEventListener('click', addFearChallenge);
    document.getElementById('saveWeekly')?.addEventListener('click', saveWeeklyReview);
    document.getElementById('saveGoals')?.addEventListener('click', saveGoals);
    document.getElementById('habitDate')?.addEventListener('change', loadHabits);
});

function initTheme() {
    const saved = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-theme', saved);
    updateThemeIcon(saved);

    document.getElementById('themeToggle')?.addEventListener('click', () => {
        const current = document.documentElement.getAttribute('data-theme');
        const next = current === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', next);
        localStorage.setItem('theme', next);
        updateThemeIcon(next);
        refreshCharts();
    });
}

function updateThemeIcon(theme) {
    const btn = document.getElementById('themeToggle');
    if (btn) btn.textContent = theme === 'dark' ? '🌙' : '☀️';
}

function getChartColors() {
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    return {
        text: isDark ? '#94a3b8' : '#475569',
        grid: isDark ? '#2e3348' : '#e2e8f0',
        accent: '#6366f1',
        success: '#22c55e',
        warning: '#f59e0b',
        error: '#ef4444',
        info: '#3b82f6',
    };
}

function initNavigation() {
    const titles = {
        dashboard: 'Dashboard',
        habits: 'Daily Habits',
        streaks: 'Streak Tracking',
        career: 'Career Progress',
        fear: 'Fear Challenges',
        weekly: 'Weekly Review',
        goals: 'Monthly Goals',
        mood: 'Mood Tracker',
        analytics: 'Analytics',
        plan: '30-Day Plan',
    };

    document.querySelectorAll('.nav-item[data-section]').forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const section = item.dataset.section;

            document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
            item.classList.add('active');

            document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
            document.getElementById(`section-${section}`)?.classList.add('active');

            document.getElementById('pageTitle').textContent = titles[section] || 'Dashboard';
            document.getElementById('sidebar')?.classList.remove('open');

            loadSection(section);
        });
    });
}

function initMobileMenu() {
    document.getElementById('menuToggle')?.addEventListener('click', () => {
        document.getElementById('sidebar')?.classList.toggle('open');
    });
}

function loadSection(section) {
    const loaders = {
        dashboard: loadDashboard,
        habits: loadHabits,
        streaks: loadStreaks,
        career: loadCareer,
        fear: loadFear,
        weekly: loadWeekly,
        goals: loadGoals,
        mood: loadMood,
        analytics: loadAnalytics,
        plan: loadPlan,
    };
    loaders[section]?.();
}

async function fetchJSON(url, options = {}) {
    const res = await fetch(url, {
        headers: { 'Content-Type': 'application/json' },
        ...options,
    });
    if (!res.ok) throw new Error(`Request failed: ${res.status}`);
    return res.json();
}

function showToast(message, type = 'success') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

function setProgressRing(circleId, value) {
    const circle = document.getElementById(circleId);
    if (!circle) return;
    const circumference = 2 * Math.PI * 52;
    const offset = circumference - (value / 100) * circumference;
    circle.style.strokeDashoffset = offset;
}

async function loadDashboard() {
    try {
        const data = await fetchJSON(API.dashboard);

        document.getElementById('todayDate').textContent = data.today;
        document.getElementById('overallProgress').textContent = `${data.overall_progress}%`;
        document.getElementById('dailyScore').textContent = `${data.daily_score}/100`;
        document.getElementById('currentStreak').textContent = `${data.current_streak} days`;
        document.getElementById('longestStreak').textContent = data.longest_streak;
        document.getElementById('motivationalQuote').textContent = `"${data.quote}"`;
        document.getElementById('userGreeting').textContent = `Hi, ${data.username}!`;

        document.getElementById('dailyRingValue').textContent = data.daily_score;
        setProgressRing('dailyRing', data.daily_score);

        const badge = document.getElementById('streakBadge');
        if (badge) {
            badge.innerHTML = `
                <span class="badge-icon">${data.streak_badge.icon}</span>
                <span class="badge-name">${data.streak_badge.name}</span>
                <span class="badge-detail">Longest: <strong>${data.longest_streak}</strong> days</span>
            `;
        }
    } catch (err) {
        console.error('Dashboard load error:', err);
    }
}

async function loadHabits() {
    const dateInput = document.getElementById('habitDate');
    if (dateInput && !dateInput.value) {
        dateInput.value = new Date().toISOString().split('T')[0];
    }
    const date = dateInput?.value || new Date().toISOString().split('T')[0];

    try {
        const data = await fetchJSON(`${API.habits}?date=${date}`);
        habitsData = data.habits;

        const grid = document.getElementById('habitsGrid');
        grid.innerHTML = habitsData.map(h => `
            <div class="habit-item ${h.completed ? 'completed' : ''}" data-name="${h.name}">
                <div class="habit-checkbox">${h.completed ? '✓' : ''}</div>
                <span class="habit-name">${h.name}</span>
            </div>
        `).join('');

        grid.querySelectorAll('.habit-item').forEach(item => {
            item.addEventListener('click', () => {
                const name = item.dataset.name;
                const habit = habitsData.find(h => h.name === name);
                if (habit) {
                    habit.completed = !habit.completed;
                    item.classList.toggle('completed', habit.completed);
                    item.querySelector('.habit-checkbox').textContent = habit.completed ? '✓' : '';
                    updateHabitScore();
                }
            });
        });

        document.getElementById('habitScore').textContent = `Daily Score: ${data.score}/100`;
    } catch (err) {
        console.error('Habits load error:', err);
    }
}

function updateHabitScore() {
    const completed = habitsData.filter(h => h.completed).length;
    const score = Math.round((completed / habitsData.length) * 100);
    document.getElementById('habitScore').textContent = `Daily Score: ${score}/100`;
}

async function saveHabits() {
    const date = document.getElementById('habitDate')?.value || new Date().toISOString().split('T')[0];
    try {
        const data = await fetchJSON(API.habits, {
            method: 'POST',
            body: JSON.stringify({ date, habits: habitsData }),
        });
        document.getElementById('habitScore').textContent = `Daily Score: ${data.score}/100`;
        showToast(`Habits saved! Score: ${data.score}/100`);
    } catch (err) {
        showToast('Failed to save habits', 'error');
    }
}

async function loadStreaks() {
    try {
        const data = await fetchJSON(API.streaks);

        document.getElementById('streakNumber').textContent = data.current_streak;

        const badgeLarge = document.getElementById('streakBadgeLarge');
        badgeLarge.innerHTML = `
            <span class="badge-icon">${data.badge.icon}</span>
            <span class="badge-name">${data.badge.name}</span>
            <span class="badge-detail">Longest streak: <strong>${data.longest_streak}</strong> days</span>
        `;

        const calendar = document.getElementById('streakCalendar');
        calendar.innerHTML = data.history.map(day => {
            let cls = 'streak-day';
            if (day.percentage >= 80) cls += ' great';
            else if (day.percentage >= 50) cls += ' good';
            else if (day.completed === 0) cls += ' none';
            return `<div class="${cls}" title="${day.date}: ${day.percentage}%">${new Date(day.date).getDate()}</div>`;
        }).join('');
    } catch (err) {
        console.error('Streaks load error:', err);
    }
}

async function loadCareer() {
    try {
        const data = await fetchJSON(API.career);
        const grid = document.getElementById('careerGrid');

        grid.innerHTML = data.skills.map(s => `
            <div class="career-item">
                <div class="career-header">
                    <span class="career-name">${s.name}</span>
                    <span class="career-pct" data-name="${s.name}">${s.percentage}%</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-bar-fill" style="width: ${s.percentage}%"></div>
                </div>
                <input type="range" class="career-slider" min="0" max="100" value="${s.percentage}"
                    data-name="${s.name}">
            </div>
        `).join('');

        grid.querySelectorAll('.career-slider').forEach(slider => {
            slider.addEventListener('input', () => {
                const name = slider.dataset.name;
                const val = slider.value;
                grid.querySelector(`.career-pct[data-name="${name}"]`).textContent = `${val}%`;
                slider.previousElementSibling.querySelector('.progress-bar-fill').style.width = `${val}%`;
            });
        });
    } catch (err) {
        console.error('Career load error:', err);
    }
}

async function saveCareer() {
    const sliders = document.querySelectorAll('.career-slider');
    const skills = Array.from(sliders).map(s => ({
        name: s.dataset.name,
        percentage: parseInt(s.value),
    }));

    try {
        await fetchJSON(API.career, {
            method: 'POST',
            body: JSON.stringify({ skills }),
        });
        showToast('Career progress saved!');
    } catch (err) {
        showToast('Failed to save progress', 'error');
    }
}

async function loadFear() {
    try {
        const data = await fetchJSON(API.fear);

        const select = document.getElementById('fearType');
        select.innerHTML = data.types.map(t => `<option value="${t}">${t}</option>`).join('');

        const history = document.getElementById('fearHistory');
        if (data.history.length === 0) {
            history.innerHTML = '<div class="empty-state">No challenges logged yet. Take the first step!</div>';
        } else {
            history.innerHTML = data.history.map(c => `
                <div class="history-item">
                    <div class="history-item-info">
                        <h4>${c.type}</h4>
                        <span>${c.date}${c.notes ? ' — ' + c.notes : ''}</span>
                    </div>
                    <button class="btn-delete" data-id="${c.id}" title="Delete">✕</button>
                </div>
            `).join('');

            history.querySelectorAll('.btn-delete').forEach(btn => {
                btn.addEventListener('click', () => deleteFearChallenge(btn.dataset.id));
            });
        }
    } catch (err) {
        console.error('Fear load error:', err);
    }
}

async function addFearChallenge() {
    const type = document.getElementById('fearType').value;
    const notes = document.getElementById('fearNotes').value;

    try {
        await fetchJSON(API.fear, {
            method: 'POST',
            body: JSON.stringify({ type, notes }),
        });
        document.getElementById('fearNotes').value = '';
        showToast('Challenge logged! Great job facing your fear!');
        loadFear();
    } catch (err) {
        showToast('Failed to log challenge', 'error');
    }
}

async function deleteFearChallenge(id) {
    try {
        await fetchJSON(`${API.fear}/${id}`, { method: 'DELETE' });
        showToast('Challenge removed');
        loadFear();
    } catch (err) {
        showToast('Failed to delete', 'error');
    }
}

async function loadWeekly() {
    try {
        const data = await fetchJSON(API.weekly);
        document.getElementById('weeklyWins').value = data.wins;
        document.getElementById('weeklyMistakes').value = data.mistakes;
        document.getElementById('weeklyLessons').value = data.lessons;
        document.getElementById('weeklyGoals').value = data.goals;
    } catch (err) {
        console.error('Weekly load error:', err);
    }
}

async function saveWeeklyReview() {
    try {
        await fetchJSON(API.weekly, {
            method: 'POST',
            body: JSON.stringify({
                wins: document.getElementById('weeklyWins').value,
                mistakes: document.getElementById('weeklyMistakes').value,
                lessons: document.getElementById('weeklyLessons').value,
                goals: document.getElementById('weeklyGoals').value,
            }),
        });
        showToast('Weekly review saved!');
    } catch (err) {
        showToast('Failed to save review', 'error');
    }
}

// Modal Helpers
function openModal(id) {
    document.getElementById(id)?.classList.add('active');
}
function closeModal(id) {
    document.getElementById(id)?.classList.remove('active');
}

async function loadGoals() {
    try {
        const data = await fetchJSON(API.goals);
        const grid = document.getElementById('goalsGrid');
        
        // Add listener for create plan button if not already added
        const btnCreatePlan = document.getElementById('btnCreatePlan');
        if (btnCreatePlan && !btnCreatePlan.dataset.listenerAdded) {
            btnCreatePlan.addEventListener('click', () => {
                document.getElementById('newPlanName').value = '';
                openModal('modalCreatePlan');
            });
            btnCreatePlan.dataset.listenerAdded = 'true';
            
            // Close buttons listeners
            document.getElementById('btnCloseCreatePlan')?.addEventListener('click', () => closeModal('modalCreatePlan'));
            document.getElementById('btnCloseAddGoal')?.addEventListener('click', () => closeModal('modalAddGoal'));
            document.getElementById('btnCloseEditGoal')?.addEventListener('click', () => closeModal('modalEditGoal'));
            
            // Submit buttons listeners
            document.getElementById('submitCreatePlan')?.addEventListener('click', submitCreatePlan);
            document.getElementById('submitAddGoal')?.addEventListener('click', submitAddGoal);
            document.getElementById('submitEditGoal')?.addEventListener('click', submitEditGoal);
        }

        if (data.plans.length === 0) {
            grid.innerHTML = `
                <div class="empty-state card" style="grid-column: 1 / -1; padding: 40px; text-align: center;">
                    <span style="font-size: 3rem; display: block; margin-bottom: 16px;">🎯</span>
                    <h3>No Monthly Plans Yet</h3>
                    <p style="color: var(--text-secondary); margin-bottom: 20px;">Create your first custom monthly plan to map out your career goals!</p>
                    <button class="btn btn-primary" onclick="openModal('modalCreatePlan')">+ Create First Month</button>
                </div>
            `;
            return;
        }

        grid.innerHTML = data.plans.map(plan => {
            const isCompleted = plan.completed;
            const statusClass = isCompleted ? 'done' : 'active';
            const statusLabel = isCompleted ? '✓ Completed' : '🔥 Active';
            
            const goalsHTML = plan.goals.map(g => `
                <div class="goal-row ${g.completed ? 'completed' : ''}" data-goal-id="${g.id}">
                    <div class="goal-checkbox" data-goal-id="${g.id}">${g.completed ? '✓' : ''}</div>
                    <div class="goal-info">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span class="goal-name-text">${g.name}</span>
                            <span class="goal-pct-text" data-goal-id="${g.id}">${g.current}%</span>
                        </div>
                        <input type="range" class="career-slider goal-slider" min="0" max="100" value="${g.current}" data-id="${g.id}" style="margin-top: 4px;">
                    </div>
                    <div class="goal-controls">
                        <button class="btn-action btn-edit-goal" data-id="${g.id}" data-name="${g.name}" title="Edit Goal">✏️</button>
                        <button class="btn-action delete btn-delete-goal" data-id="${g.id}" title="Delete Goal">✕</button>
                    </div>
                </div>
            `).join('');

            const addGoalHTML = plan.goals.length < 6 ? `
                <div class="btn-add-goal-placeholder" data-plan-id="${plan.id}">
                    <span>+ Add Goal (${plan.goals.length}/6)</span>
                </div>
            ` : '';

            return `
                <div class="goal-item card ${isCompleted ? 'completed' : ''}" data-plan-id="${plan.id}">
                    <div class="plan-card-header">
                        <div class="plan-card-title">
                            <span>📅</span>
                            <span>${plan.name}</span>
                            <span class="goal-status ${statusClass}" style="margin-left: 8px; font-size: 0.75rem;">${statusLabel}</span>
                        </div>
                        <div class="plan-card-actions">
                            <button class="btn-action delete btn-delete-plan" data-id="${plan.id}" title="Delete Month Plan">🗑️</button>
                        </div>
                    </div>
                    <div class="progress-bar" style="margin-bottom: 20px;">
                        <div class="progress-bar-fill" style="width: ${plan.progress}%"></div>
                    </div>
                    <div style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 12px; display: flex; justify-content: space-between;">
                        <span>Monthly Completion</span>
                        <strong>${plan.progress}%</strong>
                    </div>
                    <div class="goals-list">
                        ${goalsHTML}
                        ${addGoalHTML}
                    </div>
                </div>
            `;
        }).join('');

        // Setup dynamic listeners
        // 1. Goal sliders updating percentages
        grid.querySelectorAll('.goal-slider').forEach(slider => {
            slider.addEventListener('input', () => {
                const id = slider.dataset.id;
                const val = parseInt(slider.value);
                grid.querySelector(`.goal-pct-text[data-goal-id="${id}"]`).textContent = `${val}%`;
                
                const goalRow = slider.closest('.goal-row');
                const checkbox = goalRow.querySelector('.goal-checkbox');
                if (val >= 100) {
                    goalRow.classList.add('completed');
                    checkbox.textContent = '✓';
                } else {
                    goalRow.classList.remove('completed');
                    checkbox.textContent = '';
                }
            });
        });

        // 2. Goal checkbox click (toggles 0% vs 100%)
        grid.querySelectorAll('.goal-checkbox').forEach(cb => {
            cb.addEventListener('click', () => {
                const id = cb.dataset.goalId;
                const goalRow = cb.closest('.goal-row');
                const slider = goalRow.querySelector('.goal-slider');
                const isCompleted = goalRow.classList.contains('completed');
                
                if (isCompleted) {
                    goalRow.classList.remove('completed');
                    cb.textContent = '';
                    slider.value = 0;
                    grid.querySelector(`.goal-pct-text[data-goal-id="${id}"]`).textContent = '0%';
                } else {
                    goalRow.classList.add('completed');
                    cb.textContent = '✓';
                    slider.value = 100;
                    grid.querySelector(`.goal-pct-text[data-goal-id="${id}"]`).textContent = '100%';
                }
            });
        });

        // 3. Add Goal button placeholder click
        grid.querySelectorAll('.btn-add-goal-placeholder').forEach(btn => {
            btn.addEventListener('click', () => {
                document.getElementById('addGoalPlanId').value = btn.dataset.planId;
                document.getElementById('newGoalName').value = '';
                openModal('modalAddGoal');
            });
        });

        // 4. Edit Goal click
        grid.querySelectorAll('.btn-edit-goal').forEach(btn => {
            btn.addEventListener('click', () => {
                document.getElementById('editGoalId').value = btn.dataset.id;
                document.getElementById('editGoalName').value = btn.dataset.name;
                openModal('modalEditGoal');
            });
        });

        // 5. Delete Goal click
        grid.querySelectorAll('.btn-delete-goal').forEach(btn => {
            btn.addEventListener('click', () => deleteGoal(btn.dataset.id));
        });

        // 6. Delete Plan click
        grid.querySelectorAll('.btn-delete-plan').forEach(btn => {
            btn.addEventListener('click', () => deletePlan(btn.dataset.id));
        });

    } catch (err) {
        console.error('Goals load error:', err);
    }
}

async function saveGoals() {
    const sliders = document.querySelectorAll('.goal-slider');
    const goals = Array.from(sliders).map(s => ({
        id: parseInt(s.dataset.id),
        current: parseInt(s.value),
    }));

    try {
        await fetchJSON(API.goals, {
            method: 'POST',
            body: JSON.stringify({ goals }),
        });
        showToast('Goals progress saved!');
        loadGoals();
    } catch (err) {
        showToast('Failed to save goals', 'error');
    }
}

// Action submits
async function submitCreatePlan() {
    const monthName = document.getElementById('newPlanName').value.trim();
    if (!monthName) {
        showToast('Please enter a month name', 'error');
        return;
    }
    try {
        await fetchJSON(`${API.goals}/create-plan`, {
            method: 'POST',
            body: JSON.stringify({ month_name: monthName }),
        });
        closeModal('modalCreatePlan');
        showToast(`Month '${monthName}' created successfully!`);
        loadGoals();
    } catch (err) {
        showToast('Failed to create monthly plan. It might already exist.', 'error');
    }
}

async function submitAddGoal() {
    const planId = document.getElementById('addGoalPlanId').value;
    const goalName = document.getElementById('newGoalName').value.trim();
    if (!goalName) {
        showToast('Please enter a goal description', 'error');
        return;
    }
    try {
        await fetchJSON(`${API.goals}/add-goal`, {
            method: 'POST',
            body: JSON.stringify({ plan_id: parseInt(planId), goal_name: goalName }),
        });
        closeModal('modalAddGoal');
        showToast('Goal added successfully!');
        loadGoals();
    } catch (err) {
        showToast('Failed to add goal (check duplicates or the 6 goals limit).', 'error');
    }
}

async function submitEditGoal() {
    const goalId = document.getElementById('editGoalId').value;
    const goalName = document.getElementById('editGoalName').value.trim();
    if (!goalName) {
        showToast('Please enter a goal description', 'error');
        return;
    }
    try {
        await fetchJSON(`${API.goals}/edit-goal`, {
            method: 'POST',
            body: JSON.stringify({ goal_id: parseInt(goalId), goal_name: goalName }),
        });
        closeModal('modalEditGoal');
        showToast('Goal updated successfully!');
        loadGoals();
    } catch (err) {
        showToast('Failed to edit goal.', 'error');
    }
}

async function deleteGoal(id) {
    if (!confirm('Are you sure you want to delete this goal?')) return;
    try {
        await fetchJSON(`${API.goals}/delete-goal/${id}`, { method: 'DELETE' });
        showToast('Goal deleted');
        loadGoals();
    } catch (err) {
        showToast('Failed to delete goal', 'error');
    }
}

async function deletePlan(id) {
    if (!confirm('Are you sure you want to delete this monthly plan and all its goals?')) return;
    try {
        await fetchJSON(`${API.goals}/delete-plan/${id}`, { method: 'DELETE' });
        showToast('Monthly plan deleted');
        loadGoals();
    } catch (err) {
        showToast('Failed to delete monthly plan', 'error');
    }
}

const MOOD_EMOJIS = { Happy: '😊', Normal: '😐', Tired: '😴', Stressed: '😰' };
const MOOD_COLORS = { Happy: '#22c55e', Normal: '#3b82f6', Tired: '#f59e0b', Stressed: '#ef4444' };

async function loadMood() {
    try {
        const data = await fetchJSON(API.mood);

        const selector = document.getElementById('moodSelector');
        selector.innerHTML = data.options.map(m => `
            <button class="mood-btn ${data.today === m ? 'selected' : ''}" data-mood="${m}">
                <span class="mood-emoji">${MOOD_EMOJIS[m]}</span>
                <span class="mood-label">${m}</span>
            </button>
        `).join('');

        selector.querySelectorAll('.mood-btn').forEach(btn => {
            btn.addEventListener('click', () => saveMood(btn.dataset.mood));
        });

        renderMoodChart(data.counts);
        renderMoodTrendChart(data.history);
    } catch (err) {
        console.error('Mood load error:', err);
    }
}

async function saveMood(mood) {
    try {
        await fetchJSON(API.mood, {
            method: 'POST',
            body: JSON.stringify({ mood }),
        });
        document.querySelectorAll('.mood-btn').forEach(b => {
            b.classList.toggle('selected', b.dataset.mood === mood);
        });
        showToast(`Mood recorded: ${mood}`);
        loadMood();
    } catch (err) {
        showToast('Failed to save mood', 'error');
    }
}

function renderMoodChart(counts) {
    const ctx = document.getElementById('moodChart');
    if (!ctx) return;
    const colors = getChartColors();

    if (charts.mood) charts.mood.destroy();

    charts.mood = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: Object.keys(counts),
            datasets: [{
                data: Object.values(counts),
                backgroundColor: Object.keys(counts).map(m => MOOD_COLORS[m]),
                borderWidth: 0,
            }],
        },
        options: {
            responsive: true,
            plugins: {
                legend: { labels: { color: colors.text } },
            },
        },
    });
}

function renderMoodTrendChart(history) {
    const ctx = document.getElementById('moodTrendChart');
    if (!ctx) return;
    const colors = getChartColors();
    const moodValues = { Happy: 4, Normal: 3, Tired: 2, Stressed: 1 };

    const reversed = [...history].reverse();
    if (charts.moodTrend) charts.moodTrend.destroy();

    charts.moodTrend = new Chart(ctx, {
        type: 'line',
        data: {
            labels: reversed.map(h => h.date.slice(5)),
            datasets: [{
                label: 'Mood Level',
                data: reversed.map(h => h.mood ? moodValues[h.mood] : null),
                borderColor: colors.accent,
                backgroundColor: 'rgba(99, 102, 241, 0.1)',
                fill: true,
                tension: 0.4,
                spanGaps: true,
            }],
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    min: 0, max: 5,
                    ticks: { color: colors.text, stepSize: 1 },
                    grid: { color: colors.grid },
                },
                x: { ticks: { color: colors.text }, grid: { color: colors.grid } },
            },
            plugins: { legend: { display: false } },
        },
    });
}

async function loadAnalytics() {
    try {
        const data = await fetchJSON(API.analytics);
        renderBarChart('habitChart', data.habit_rate.map(d => d.date), data.habit_rate.map(d => d.rate), 'Completion %');
        renderBarChart('consistencyChart', data.weekly_consistency.map(d => d.week), data.weekly_consistency.map(d => d.rate), 'Consistency %');
        renderLineChart('monthlyChart', data.monthly_progress.map(d => d.month), data.monthly_progress.map(d => d.progress), 'Progress %');
        renderRadarChart('technicalChart', data.technical_skills);
        renderRadarChart('communicationChart', data.communication_skills);
    } catch (err) {
        console.error('Analytics load error:', err);
    }
}

function renderBarChart(canvasId, labels, values, label) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    const colors = getChartColors();
    if (charts[canvasId]) charts[canvasId].destroy();

    charts[canvasId] = new Chart(ctx, {
        type: 'bar',
        data: {
            labels,
            datasets: [{
                label,
                data: values,
                backgroundColor: 'rgba(99, 102, 241, 0.7)',
                borderRadius: 6,
            }],
        },
        options: {
            responsive: true,
            scales: {
                y: { beginAtZero: true, max: 100, ticks: { color: colors.text }, grid: { color: colors.grid } },
                x: { ticks: { color: colors.text }, grid: { display: false } },
            },
            plugins: { legend: { display: false } },
        },
    });
}

function renderLineChart(canvasId, labels, values, label) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    const colors = getChartColors();
    if (charts[canvasId]) charts[canvasId].destroy();

    charts[canvasId] = new Chart(ctx, {
        type: 'line',
        data: {
            labels,
            datasets: [{
                label,
                data: values,
                borderColor: colors.accent,
                backgroundColor: 'rgba(99, 102, 241, 0.1)',
                fill: true,
                tension: 0.4,
            }],
        },
        options: {
            responsive: true,
            scales: {
                y: { beginAtZero: true, max: 100, ticks: { color: colors.text }, grid: { color: colors.grid } },
                x: { ticks: { color: colors.text }, grid: { color: colors.grid } },
            },
            plugins: { legend: { display: false } },
        },
    });
}

function renderRadarChart(canvasId, skills) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    const colors = getChartColors();
    if (charts[canvasId]) charts[canvasId].destroy();

    charts[canvasId] = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: skills.map(s => s.name),
            datasets: [{
                label: 'Skill Level',
                data: skills.map(s => s.value),
                backgroundColor: 'rgba(99, 102, 241, 0.2)',
                borderColor: colors.accent,
                pointBackgroundColor: colors.accent,
            }],
        },
        options: {
            responsive: true,
            scales: {
                r: {
                    beginAtZero: true,
                    max: 100,
                    ticks: { color: colors.text, backdropColor: 'transparent' },
                    grid: { color: colors.grid },
                    pointLabels: { color: colors.text, font: { size: 11 } },
                },
            },
            plugins: { legend: { display: false } },
        },
    });
}

function refreshCharts() {
    const activeSection = document.querySelector('.section.active');
    if (!activeSection) return;
    const id = activeSection.id.replace('section-', '');
    if (id === 'mood') loadMood();
    if (id === 'analytics') loadAnalytics();
}

async function loadPlan() {
    try {
        const data = await fetchJSON(API.plan);

        document.getElementById('planPercentage').textContent = `${data.percentage}%`;

        const grid = document.getElementById('planGrid');
        grid.innerHTML = data.plan.map(day => `
            <div class="plan-day ${day.completed ? 'completed' : ''}" data-day="${day.day}">
                <div class="plan-day-header">
                    <span class="plan-day-number">Day ${day.day}</span>
                    <span class="plan-day-title">${day.title}</span>
                </div>
                <ul class="plan-tasks">
                    ${day.tasks.map(t => `<li>${t}</li>`).join('')}
                </ul>
                <label class="plan-toggle">
                    <input type="checkbox" ${day.completed ? 'checked' : ''} data-day="${day.day}">
                    Mark as complete
                </label>
                <div class="plan-notes-container">
                    <textarea class="plan-notes" data-day="${day.day}" placeholder="Add notes or links...">${day.notes || ''}</textarea>
                    <button class="btn-save-notes" data-day="${day.day}" title="Save Notes">💾</button>
                </div>
            </div>
        `).join('');

        grid.querySelectorAll('.plan-toggle input').forEach(cb => {
            cb.addEventListener('change', () => {
                const day = cb.dataset.day;
                const notesVal = grid.querySelector(`.plan-notes[data-day="${day}"]`).value;
                updatePlanDay(day, cb.checked, notesVal);
            });
        });

        grid.querySelectorAll('.btn-save-notes').forEach(btn => {
            btn.addEventListener('click', () => {
                const day = btn.dataset.day;
                const cb = grid.querySelector(`.plan-toggle input[data-day="${day}"]`);
                const notesVal = grid.querySelector(`.plan-notes[data-day="${day}"]`).value;
                updatePlanDay(day, cb.checked, notesVal);
                showToast(`Saved notes for Day ${day}!`);
            });
        });

        grid.querySelectorAll('.plan-notes').forEach(textarea => {
            textarea.addEventListener('blur', () => {
                const day = textarea.dataset.day;
                const cb = grid.querySelector(`.plan-toggle input[data-day="${day}"]`);
                updatePlanDay(day, cb.checked, textarea.value, true); // Silent save
            });
        });
    } catch (err) {
        console.error('Plan load error:', err);
    }
}

async function updatePlanDay(day, completed, notes, silent = false) {
    try {
        const data = await fetchJSON(API.plan, {
            method: 'POST',
            body: JSON.stringify({ day: parseInt(day), completed, notes }),
        });
        document.getElementById('planPercentage').textContent = `${data.percentage}%`;
        const dayEl = document.querySelector(`.plan-day[data-day="${day}"]`);
        dayEl?.classList.toggle('completed', completed);
        if (!silent) {
            showToast(completed ? `Day ${day} completed!` : `Day ${day} updated`);
        }
    } catch (err) {
        showToast('Failed to update plan', 'error');
    }
}
