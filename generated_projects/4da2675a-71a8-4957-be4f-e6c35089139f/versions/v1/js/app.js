/**
 * Production Task & Todo Application Controller
 * Provides real-time synchronization with FastAPI REST API endpoints
 * with automatic fallback to persistent browser localStorage.
 */

const STORAGE_KEY = 'enterprise_todo_platform_data';
const INITIAL_TASKS = [
    {
        id: "task-101",
        title: "Architect High-Throughput REST Endpoints",
        description: "Standardize JSON schema, pagination, status filtering, and defensive validation.",
        status: "completed",
        priority: "urgent",
        category: "Engineering",
        created_at: new Date(Date.now() - 3600000 * 24).toISOString(),
        updated_at: new Date(Date.now() - 3600000 * 24).toISOString()
    },
    {
        id: "task-102",
        title: "Implement Role-Based Access Control (RBAC)",
        description: "Enforce bearer token authentication and scope-based permission gates.",
        status: "pending",
        priority: "high",
        category: "Security",
        created_at: new Date(Date.now() - 3600000 * 12).toISOString(),
        updated_at: new Date(Date.now() - 3600000 * 12).toISOString()
    },
    {
        id: "task-103",
        title: "Automate Database Migration & Backup Pipeline",
        description: "Configure persistent SQLite volume mounts and automated WAL replication.",
        status: "completed",
        priority: "medium",
        category: "Operations",
        created_at: new Date(Date.now() - 3600000 * 6).toISOString(),
        updated_at: new Date(Date.now() - 3600000 * 6).toISOString()
    },
    {
        id: "task-104",
        title: "Design Responsive Dark-Mode User Dashboard",
        description: "Deliver a fluid, glassmorphic UI with live event telemetry and statistics.",
        status: "pending",
        priority: "medium",
        category: "Design",
        created_at: new Date(Date.now() - 3600000 * 2).toISOString(),
        updated_at: new Date(Date.now() - 3600000 * 2).toISOString()
    }
];

let appState = {
    todos: [],
    filter: 'all',
    search: '',
    editingId: null,
    backendOnline: false,
    logs: []
};

// ---- Logging & UI Feedback ----
function addLog(message, type = 'info') {
    const time = new Date().toLocaleTimeString();
    const colorClass = type === 'error' ? 'text-rose-400' : type === 'success' ? 'text-emerald-400' : type === 'warn' ? 'text-amber-400' : 'text-slate-300';
    appState.logs.unshift({ time, message, colorClass });
    if (appState.logs.length > 50) appState.logs.pop();

    const logContainer = document.getElementById('event-logs');
    if (logContainer) {
        logContainer.innerHTML = appState.logs.map(log => `
            <div class="flex items-start gap-2">
                <span class="text-slate-500 shrink-0">[${log.time}]</span>
                <span class="${log.colorClass} break-all">${escapeHtml(log.message)}</span>
            </div>
        `).join('');
    }
}

function clearLogs() {
    appState.logs = [];
    const logContainer = document.getElementById('event-logs');
    if (logContainer) logContainer.innerHTML = '<div class="text-slate-500 italic">Event logs cleared.</div>';
}

function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    if (!toast) return;

    const bgColors = {
        success: 'bg-emerald-600 text-white shadow-emerald-900/50',
        error: 'bg-rose-600 text-white shadow-rose-900/50',
        info: 'bg-indigo-600 text-white shadow-indigo-900/50',
        warn: 'bg-amber-600 text-white shadow-amber-900/50'
    };

    const icons = {
        success: '<i class="fa-solid fa-circle-check"></i>',
        error: '<i class="fa-solid fa-circle-xmark"></i>',
        info: '<i class="fa-solid fa-circle-info"></i>',
        warn: '<i class="fa-solid fa-triangle-exclamation"></i>'
    };

    toast.className = `fixed bottom-5 right-5 z-50 transition-all duration-300 px-4 py-3 rounded-xl shadow-2xl text-xs font-medium flex items-center gap-2.5 ${bgColors[type] || bgColors.info} show`;
    toast.innerHTML = `${icons[type] || icons.info} <span>${escapeHtml(message)}</span>`;

    setTimeout(() => {
        toast.classList.remove('show');
    }, 2800);
}

function escapeHtml(str) {
    if (!str) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

// ---- Storage & Backend Sync ----
function saveLocalTodos() {
    try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(appState.todos));
    } catch (e) {
        console.warn('LocalStorage save failed:', e);
    }
}

function loadLocalTodos() {
    try {
        const raw = localStorage.getItem(STORAGE_KEY);
        if (raw) {
            const parsed = JSON.parse(raw);
            if (Array.isArray(parsed) && parsed.length > 0) {
                return parsed;
            }
        }
    } catch (e) {
        console.warn('LocalStorage load error:', e);
    }
    return [...INITIAL_TASKS];
}

async function loadTodos() {
    const syncBadge = document.getElementById('sync-mode-badge');
    const syncText = document.getElementById('sync-status-text');
    const persistenceText = document.getElementById('persistence-type');

    // Attempt backend connection first with short timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 1200);

    try {
        const res = await fetch('/todos', { signal: controller.signal });
        clearTimeout(timeoutId);

        if (res.ok) {
            const data = await res.json();
            const items = Array.isArray(data) ? data : (data.data || []);
            appState.backendOnline = true;
            appState.todos = items;

            if (syncBadge && syncText) {
                syncBadge.className = 'inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30';
                syncText.textContent = 'REST API Online';
            }
            if (persistenceText) persistenceText.textContent = 'FastAPI SQLite Database';

            addLog(`HTTP GET /todos -> 200 OK (${items.length} records loaded from backend)`, 'success');
            render();
            return;
        }
    } catch (err) {
        // Backend offline (e.g. static preview mode)
    }

    // Graceful offline fallback
    appState.backendOnline = false;
    appState.todos = loadLocalTodos();

    if (syncBadge && syncText) {
        syncBadge.className = 'inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-cyan-500/10 text-cyan-400 border border-cyan-500/30';
        syncText.textContent = 'Local Sync Mode';
    }
    if (persistenceText) persistenceText.textContent = 'Browser Persistent Store';

    addLog(`System active. Running with persistent local synchronization (${appState.todos.length} tasks ready)`, 'info');
    render();
}

// ---- Task CRUD Operations ----
async function handleFormSubmit(e) {
    e.preventDefault();

    const titleInput = document.getElementById('todo-title');
    const descInput = document.getElementById('todo-desc');
    const prioritySelect = document.getElementById('todo-priority');
    const categorySelect = document.getElementById('todo-category');
    const editIdInput = document.getElementById('edit-id');

    const title = titleInput.value.trim();
    if (!title) return;

    const description = descInput.value.trim();
    const priority = prioritySelect.value;
    const category = categorySelect.value;
    const isEdit = Boolean(editIdInput.value);
    const targetId = editIdInput.value;

    const payload = {
        title,
        description,
        priority,
        category,
        status: isEdit ? (appState.todos.find(t => t.id === targetId)?.status || 'pending') : 'pending'
    };

    if (isEdit) {
        // Update existing task
        let updated = null;
        if (appState.backendOnline) {
            try {
                const res = await fetch(`/todos/${targetId}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                if (res.ok) {
                    updated = await res.json();
                    addLog(`HTTP PUT /todos/${targetId} -> 200 OK ("${title}")`, 'success');
                }
            } catch (err) {
                console.warn('Backend update failed:', err);
            }
        }

        const idx = appState.todos.findIndex(t => t.id === targetId);
        if (idx !== -1) {
            appState.todos[idx] = updated || {
                ...appState.todos[idx],
                ...payload,
                updated_at: new Date().toISOString()
            };
        }

        saveLocalTodos();
        cancelEditing();
        showToast('✓ Task updated successfully', 'success');
        render();
    } else {
        // Create new task
        let created = null;
        if (appState.backendOnline) {
            try {
                const res = await fetch('/todos', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                if (res.ok) {
                    created = await res.json();
                    addLog(`HTTP POST /todos -> 201 Created ("${title}")`, 'success');
                }
            } catch (err) {
                console.warn('Backend create failed:', err);
            }
        }

        const newTask = created || {
            id: 'task-' + Date.now(),
            ...payload,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString()
        };

        appState.todos.unshift(newTask);
        saveLocalTodos();

        titleInput.value = '';
        descInput.value = '';
        showToast('✓ Task created successfully', 'success');
        if (!appState.backendOnline) {
            addLog(`Created task: "${title}" [${priority.toUpperCase()}]`, 'success');
        }
        render();
    }
}

async function toggleStatus(id) {
    const task = appState.todos.find(t => t.id === id);
    if (!task) return;

    const newStatus = task.status === 'completed' ? 'pending' : 'completed';
    task.status = newStatus;
    task.updated_at = new Date().toISOString();

    if (appState.backendOnline) {
        try {
            const res = await fetch(`/todos/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ status: newStatus })
            });
            if (res.ok) {
                addLog(`HTTP PUT /todos/${id} -> 200 OK (Status: ${newStatus})`, 'info');
            }
        } catch (err) {
            console.warn('Backend status toggle failed:', err);
        }
    }

    saveLocalTodos();
    showToast(newStatus === 'completed' ? '✓ Task marked as completed' : 'Task marked as pending', 'info');
    render();
}

function startEditing(id) {
    const task = appState.todos.find(t => t.id === id);
    if (!task) return;

    appState.editingId = id;
    document.getElementById('edit-id').value = id;
    document.getElementById('todo-title').value = task.title;
    document.getElementById('todo-desc').value = task.description || '';
    document.getElementById('todo-priority').value = task.priority || 'medium';
    document.getElementById('todo-category').value = task.category || 'General';

    document.getElementById('form-heading').innerHTML = '<i class="fa-solid fa-pen-to-square text-amber-400"></i><span>Edit Task</span>';
    document.getElementById('submit-btn-text').textContent = 'Save Changes';
    document.getElementById('cancel-edit-btn').classList.remove('hidden');

    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function cancelEditing() {
    appState.editingId = null;
    document.getElementById('edit-id').value = '';
    document.getElementById('todo-title').value = '';
    document.getElementById('todo-desc').value = '';
    document.getElementById('form-heading').innerHTML = '<i class="fa-solid fa-plus-circle text-indigo-400"></i><span>Create New Task</span>';
    document.getElementById('submit-btn-text').textContent = 'Add Task';
    document.getElementById('cancel-edit-btn').classList.add('hidden');
}

async function deleteTodo(id) {
    const task = appState.todos.find(t => t.id === id);
    const title = task ? task.title : id;

    if (appState.backendOnline) {
        try {
            const res = await fetch(`/todos/${id}`, { method: 'DELETE' });
            if (res.ok) {
                addLog(`HTTP DELETE /todos/${id} -> 200 OK`, 'warn');
            }
        } catch (err) {
            console.warn('Backend delete failed:', err);
        }
    }

    appState.todos = appState.todos.filter(t => t.id !== id);
    saveLocalTodos();
    showToast('Task removed', 'warn');
    if (!appState.backendOnline) {
        addLog(`Deleted task "${title}"`, 'warn');
    }
    render();
}

function clearCompleted() {
    const completedCount = appState.todos.filter(t => t.status === 'completed').length;
    if (completedCount === 0) {
        showToast('No completed tasks to clear', 'info');
        return;
    }

    appState.todos = appState.todos.filter(t => t.status !== 'completed');
    saveLocalTodos();
    showToast(`Cleared ${completedCount} completed tasks`, 'info');
    addLog(`Cleared ${completedCount} completed tasks`, 'info');
    render();
}

function seedSampleData() {
    appState.todos = [...INITIAL_TASKS];
    saveLocalTodos();
    showToast('✓ Demo data loaded', 'success');
    addLog('Loaded 4 realistic demo tasks into workspace', 'info');
    render();
}

// ---- Filters & Search ----
function setFilter(filter) {
    appState.filter = filter;
    ['all', 'pending', 'completed'].forEach(f => {
        const btn = document.getElementById(`filter-${f}`);
        if (!btn) return;
        if (f === filter) {
            btn.className = 'px-3 py-1 text-xs font-medium rounded-md bg-indigo-600 text-white transition';
        } else {
            btn.className = 'px-3 py-1 text-xs font-medium rounded-md text-slate-400 hover:text-white transition';
        }
    });
    render();
}

function handleSearch(val) {
    appState.search = val.trim().toLowerCase();
    render();
}

// ---- Diagnostics & Health ----
async function pingHealthCheck() {
    const startTime = performance.now();
    const latencyEl = document.getElementById('ping-latency');

    try {
        const res = await fetch('/health');
        const duration = (performance.now() - startTime).toFixed(1);
        if (latencyEl) latencyEl.textContent = `${duration} ms`;
        addLog(`HTTP GET /health -> ${res.status} OK (${duration} ms)`, 'success');
        showToast(`✓ Server healthy (${duration} ms)`, 'success');
    } catch (e) {
        try {
            const res2 = await fetch('/api/health');
            const duration = (performance.now() - startTime).toFixed(1);
            if (latencyEl) latencyEl.textContent = `${duration} ms`;
            addLog(`HTTP GET /api/health -> ${res2.status} OK (${duration} ms)`, 'success');
            showToast(`✓ Server healthy (${duration} ms)`, 'success');
            return;
        } catch (e2) {}

        const duration = (performance.now() - startTime).toFixed(1);
        if (latencyEl) latencyEl.textContent = 'Offline';
        addLog(`HTTP GET /health -> Offline (${duration} ms) [Operating in Local Sync Mode]`, 'warn');
        showToast('Server offline. Operating in persistent local mode.', 'warn');
    }
}

// ---- Rendering ----
function render() {
    // 1. Calculate Stats
    const total = appState.todos.length;
    const pending = appState.todos.filter(t => t.status === 'pending').length;
    const completed = appState.todos.filter(t => t.status === 'completed').length;
    const rate = total > 0 ? Math.round((completed / total) * 100) : 0;

    const totalEl = document.getElementById('stat-total');
    const pendingEl = document.getElementById('stat-pending');
    const completedEl = document.getElementById('stat-completed');
    const rateEl = document.getElementById('stat-rate');
    const progressBar = document.getElementById('stat-progress-bar');

    if (totalEl) totalEl.textContent = total;
    if (pendingEl) pendingEl.textContent = pending;
    if (completedEl) completedEl.textContent = completed;
    if (rateEl) rateEl.textContent = `${rate}%`;
    if (progressBar) progressBar.style.width = `${rate}%`;

    // 2. Filter & Search
    let filtered = appState.todos;
    if (appState.filter === 'pending') {
        filtered = filtered.filter(t => t.status === 'pending');
    } else if (appState.filter === 'completed') {
        filtered = filtered.filter(t => t.status === 'completed');
    }

    if (appState.search) {
        filtered = filtered.filter(t => 
            (t.title && t.title.toLowerCase().includes(appState.search)) ||
            (t.description && t.description.toLowerCase().includes(appState.search)) ||
            (t.category && t.category.toLowerCase().includes(appState.search))
        );
    }

    // 3. Render List
    const container = document.getElementById('todo-list');
    if (!container) return;

    if (filtered.length === 0) {
        container.innerHTML = `
            <div class="bg-slate-800/40 border border-dashed border-slate-700 rounded-2xl p-8 text-center">
                <div class="w-12 h-12 rounded-full bg-slate-800 text-slate-500 mx-auto flex items-center justify-center mb-3 text-lg">
                    <i class="fa-solid fa-inbox"></i>
                </div>
                <h3 class="text-sm font-semibold text-slate-300">No tasks found</h3>
                <p class="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
                    ${appState.search ? 'No tasks match your search filter.' : 'Your task queue is clear. Create a new task above or load demo data!'}
                </p>
            </div>
        `;
        return;
    }

    const priorityBadges = {
        urgent: 'bg-rose-500/10 text-rose-400 border-rose-500/20',
        high: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
        medium: 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20',
        low: 'bg-slate-500/10 text-slate-400 border-slate-500/20'
    };

    container.innerHTML = filtered.map(task => {
        const isCompleted = task.status === 'completed';
        const priorityClass = priorityBadges[task.priority?.toLowerCase()] || priorityBadges.medium;

        return `
            <div class="task-card bg-slate-800/80 border ${isCompleted ? 'border-slate-800 bg-slate-800/40 opacity-75' : 'border-slate-700/80'} rounded-2xl p-4 transition-all duration-200 hover:border-slate-600 shadow-sm flex items-start gap-3.5">
                <button onclick="toggleStatus('${task.id}')" class="mt-1 w-5 h-5 rounded-md border ${isCompleted ? 'bg-emerald-500 border-emerald-500 text-white' : 'border-slate-600 hover:border-indigo-400 bg-slate-900'} flex items-center justify-center transition shrink-0" title="Toggle completed">
                    ${isCompleted ? '<i class="fa-solid fa-check text-xs"></i>' : ''}
                </button>

                <div class="flex-1 min-w-0">
                    <div class="flex flex-wrap items-center gap-2 mb-1">
                        <span class="text-sm font-semibold text-white ${isCompleted ? 'line-through text-slate-400' : ''}">${escapeHtml(task.title)}</span>
                        <span class="px-2 py-0.5 rounded-full text-[10px] font-semibold border ${priorityClass} uppercase tracking-wider">${escapeHtml(task.priority || 'Medium')}</span>
                        <span class="px-2 py-0.5 rounded-full text-[10px] font-medium bg-slate-700/60 text-slate-300 border border-slate-600/60">${escapeHtml(task.category || 'General')}</span>
                    </div>
                    ${task.description ? `<p class="text-xs text-slate-400 line-clamp-2 mb-2 ${isCompleted ? 'line-through text-slate-500' : ''}">${escapeHtml(task.description)}</p>` : ''}
                    <div class="text-[10px] text-slate-500 flex items-center gap-2">
                        <span><i class="fa-regular fa-clock text-[9px] mr-1"></i>${new Date(task.created_at || Date.now()).toLocaleDateString()}</span>
                        <span>•</span>
                        <span class="${isCompleted ? 'text-emerald-400' : 'text-amber-400'} font-medium capitalize">${task.status}</span>
                    </div>
                </div>

                <div class="flex items-center gap-1 shrink-0">
                    <button onclick="startEditing('${task.id}')" class="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-700/60 transition" title="Edit task">
                        <i class="fa-solid fa-pencil text-xs"></i>
                    </button>
                    <button onclick="deleteTodo('${task.id}')" class="p-1.5 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 transition" title="Delete task">
                        <i class="fa-regular fa-trash-can text-xs"></i>
                    </button>
                </div>
            </div>
        `;
    }).join('');
}

// Initial Boot
document.addEventListener('DOMContentLoaded', () => {
    addLog('Initializing Enterprise Task Management Client...', 'info');
    loadTodos();
});
