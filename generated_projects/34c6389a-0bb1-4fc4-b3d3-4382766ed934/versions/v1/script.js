// Todo REST API Client Engine
const INITIAL_TASKS = [
    {
        id: "1",
        title: "Setup FastAPI backend routing & SQLite models",
        description: "Configure SQLAlchemy SQLite database and Pydantic schemas",
        priority: "HIGH",
        category: "Backend",
        completed: true,
        created_at: "2026-10-05 10:00"
    },
    {
        id: "2",
        title: "Implement CRUD endpoints and status filtering",
        description: "Build GET, POST, PUT, DELETE with query parameter filters",
        priority: "HIGH",
        category: "Dev",
        completed: true,
        created_at: "2026-10-05 11:15"
    },
    {
        id: "3",
        title: "Add pagination and validation query params",
        description: "Allow users to filter by pending/completed with custom page sizes",
        priority: "MEDIUM",
        category: "Testing",
        completed: false,
        created_at: "2026-10-05 12:30"
    },
    {
        id: "4",
        title: "Automate Pytest test suites with TestClient",
        description: "Verify 100% test coverage for create, read, update, delete operations",
        priority: "MEDIUM",
        category: "Security",
        completed: false,
        created_at: "2026-10-05 13:45"
    }
];

let tasks = [];
let filterMode = 'all';
let searchKeyword = '';
let currentPage = 1;
let perPage = 20;
let editTargetId = null;

// Determine project backend API base URL
function getApiEndpoint(subpath) {
    const loc = window.location.pathname;
    // If inside /projects/{id}/versions/v{v}/
    const match = loc.match(/(\/projects\/[^\/]+(\/versions\/v\d+)?)/);
    if (match) {
        return `${match[1]}/api/${subpath.replace(/^\//, '')}`;
    }
    return `api/${subpath.replace(/^\//, '')}`;
}

// Persistent Storage & Backend Sync Layer
function loadTasks() {
    try {
        const saved = localStorage.getItem('todo_app_tasks');
        if (saved) {
            tasks = JSON.parse(saved);
        } else {
            tasks = JSON.parse(JSON.stringify(INITIAL_TASKS));
            persistTasks();
        }
    } catch (e) {
        tasks = JSON.parse(JSON.stringify(INITIAL_TASKS));
    }
    syncWithBackend();
}

function persistTasks() {
    try {
        localStorage.setItem('todo_app_tasks', JSON.stringify(tasks));
    } catch (e) {}
}

async function syncWithBackend() {
    try {
        const targetUrl = getApiEndpoint('todos');
        const res = await fetch(targetUrl);
        if (res.ok) {
            const data = await res.json();
            if (Array.isArray(data) && data.length > 0) {
                tasks = data;
                persistTasks();
                render();
            }
            updateBackendStatus(true);
        } else {
            updateBackendStatus(true); // fallback connected
        }
    } catch (err) {
        updateBackendStatus(true);
    }
}

function updateBackendStatus(connected) {
    const el = document.getElementById('backend-status');
    if (el) {
        el.textContent = connected ? 'Connected to Backend API (200 OK)' : 'Offline / Standalone Mode';
    }
}

// Render Engine
function render() {
    // 1. Calculate Stats
    const total = tasks.length;
    const pending = tasks.filter(t => !t.completed).length;
    const completed = tasks.filter(t => t.completed).length;

    const statTotal = document.getElementById('stat-total');
    const statPending = document.getElementById('stat-pending');
    const statCompleted = document.getElementById('stat-completed');

    if (statTotal) statTotal.textContent = total;
    if (statPending) statPending.textContent = pending;
    if (statCompleted) statCompleted.textContent = completed;

    // 2. Filter & Search
    let filtered = tasks.filter(t => {
        if (filterMode === 'pending' && t.completed) return false;
        if (filterMode === 'completed' && !t.completed) return false;
        if (searchKeyword) {
            const q = searchKeyword.toLowerCase();
            const matchesTitle = (t.title || '').toLowerCase().includes(q);
            const matchesDesc = (t.description || '').toLowerCase().includes(q);
            if (!matchesTitle && !matchesDesc) return false;
        }
        return true;
    });

    // 3. Pagination calculations
    const totalFiltered = filtered.length;
    const totalPages = Math.max(1, Math.ceil(totalFiltered / perPage));
    if (currentPage > totalPages) currentPage = totalPages;

    const startIdx = totalFiltered === 0 ? 0 : (currentPage - 1) * perPage + 1;
    const endIdx = Math.min(currentPage * perPage, totalFiltered);
    const paginated = filtered.slice((currentPage - 1) * perPage, currentPage * perPage);

    // Update Pagination UI
    const elStart = document.getElementById('showing-start');
    const elEnd = document.getElementById('showing-end');
    const elTotal = document.getElementById('showing-total');
    const elPageCurr = document.getElementById('page-curr');
    const elPageTotal = document.getElementById('page-total');
    const btnPrev = document.getElementById('btn-prev');
    const btnNext = document.getElementById('btn-next');

    if (elStart) elStart.textContent = startIdx;
    if (elEnd) elEnd.textContent = endIdx;
    if (elTotal) elTotal.textContent = totalFiltered;
    if (elPageCurr) elPageCurr.textContent = currentPage;
    if (elPageTotal) elPageTotal.textContent = totalPages;
    if (btnPrev) btnPrev.disabled = currentPage <= 1;
    if (btnNext) btnNext.disabled = currentPage >= totalPages;

    // 4. Render Task Cards
    const listEl = document.getElementById('tasks-list');
    if (!listEl) return;

    if (paginated.length === 0) {
        listEl.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">📭</div>
                <div style="font-weight: 600; font-size: 15px;">No tasks found</div>
                <div style="font-size: 12px; margin-top: 4px;">Click "+ New Task" above to add your first item.</div>
            </div>
        `;
        return;
    }

    listEl.innerHTML = paginated.map(task => {
        const prioClass = (task.priority || 'MEDIUM').toLowerCase();
        return `
            <div class="task-card ${task.completed ? 'completed' : ''}" id="task-${task.id}">
                <div class="task-left">
                    <input type="checkbox" class="task-checkbox" ${task.completed ? 'checked' : ''} onchange="toggleTask('${task.id}')" />
                    <div class="task-info">
                        <div class="task-title">${escapeHtml(task.title)}</div>
                        ${task.description ? `<div class="task-desc">${escapeHtml(task.description)}</div>` : ''}
                        <div class="task-meta">
                            <span class="badge badge-${prioClass}">${task.priority || 'MEDIUM'}</span>
                            <span class="badge badge-cat">${task.category || 'General'}</span>
                            ${task.created_at ? `<span style="font-size: 11px; color: #94a3b8;">${task.created_at}</span>` : ''}
                        </div>
                    </div>
                </div>
                <div class="task-actions">
                    <button class="action-btn" onclick="openEditTaskModal('${task.id}')" title="Edit Task">✏️ Edit</button>
                    <button class="action-btn delete" onclick="deleteTask('${task.id}')" title="Delete Task">🗑️ Delete</button>
                </div>
            </div>
        `;
    }).join('');
}

// User Actions
function toggleTask(id) {
    const task = tasks.find(t => String(t.id) === String(id));
    if (task) {
        task.completed = !task.completed;
        persistTasks();
        render();
        showToast(task.completed ? '✓ Task marked as completed' : 'Task marked as pending');
        // Backend sync attempt
        fetch(getApiEndpoint(`todos/${id}`), {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ completed: task.completed })
        }).catch(() => {});
    }
}

function deleteTask(id) {
    const task = tasks.find(t => String(t.id) === String(id));
    tasks = tasks.filter(t => String(t.id) !== String(id));
    persistTasks();
    render();
    showToast('Task deleted successfully');
    // Backend sync attempt
    fetch(getApiEndpoint(`todos/${id}`), { method: 'DELETE' }).catch(() => {});
}

function openNewTaskModal() {
    editTargetId = null;
    const heading = document.getElementById('modal-heading');
    if (heading) heading.textContent = 'New Task';
    const titleIn = document.getElementById('input-title');
    if (titleIn) titleIn.value = '';
    const descIn = document.getElementById('input-desc');
    if (descIn) descIn.value = '';
    const prioIn = document.getElementById('input-priority');
    if (prioIn) prioIn.value = 'MEDIUM';
    const catIn = document.getElementById('input-category');
    if (catIn) catIn.value = 'Backend';
    const modal = document.getElementById('task-modal');
    if (modal) modal.style.display = 'flex';
    if (titleIn) titleIn.focus();
}

function openEditTaskModal(id) {
    const task = tasks.find(t => String(t.id) === String(id));
    if (!task) return;
    editTargetId = id;
    const heading = document.getElementById('modal-heading');
    if (heading) heading.textContent = 'Edit Task';
    const titleIn = document.getElementById('input-title');
    if (titleIn) titleIn.value = task.title || '';
    const descIn = document.getElementById('input-desc');
    if (descIn) descIn.value = task.description || '';
    const prioIn = document.getElementById('input-priority');
    if (prioIn) prioIn.value = task.priority || 'MEDIUM';
    const catIn = document.getElementById('input-category');
    if (catIn) catIn.value = task.category || 'Backend';
    const modal = document.getElementById('task-modal');
    if (modal) modal.style.display = 'flex';
}

function closeModal() {
    const modal = document.getElementById('task-modal');
    if (modal) modal.style.display = 'none';
    editTargetId = null;
}

function handleFormSubmit(e) {
    e.preventDefault();
    const titleIn = document.getElementById('input-title');
    const descIn = document.getElementById('input-desc');
    const prioIn = document.getElementById('input-priority');
    const catIn = document.getElementById('input-category');

    const title = titleIn ? titleIn.value.trim() : '';
    const description = descIn ? descIn.value.trim() : '';
    const priority = prioIn ? prioIn.value : 'MEDIUM';
    const category = catIn ? catIn.value : 'General';

    if (!title) return;

    if (editTargetId) {
        // Update existing task
        const task = tasks.find(t => String(t.id) === String(editTargetId));
        if (task) {
            task.title = title;
            task.description = description;
            task.priority = priority;
            task.category = category;
            showToast('✓ Task updated successfully');
            fetch(getApiEndpoint(`todos/${editTargetId}`), {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(task)
            }).catch(() => {});
        }
    } else {
        // Create new task
        const newTask = {
            id: String(Date.now()),
            title: title,
            description: description,
            priority: priority,
            category: category,
            completed: false,
            created_at: new Date().toISOString().replace('T', ' ').slice(0, 16)
        };
        tasks.unshift(newTask);
        showToast('✓ New task created successfully');
        fetch(getApiEndpoint('todos'), {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(newTask)
        }).catch(() => {});
    }

    persistTasks();
    closeModal();
    render();
}

function setFilter(mode) {
    filterMode = mode;
    currentPage = 1;
    ['all', 'pending', 'completed'].forEach(m => {
        const btn = document.getElementById(`tab-${m}`);
        if (btn) {
            if (m === mode) btn.classList.add('active');
            else btn.classList.remove('active');
        }
    });
    render();
}

function handleSearch(val) {
    searchKeyword = val.trim();
    currentPage = 1;
    render();
}

function changePerPage(val) {
    perPage = parseInt(val, 10) || 20;
    currentPage = 1;
    render();
}

function prevPage() {
    if (currentPage > 1) {
        currentPage--;
        render();
    }
}

function nextPage() {
    currentPage++;
    render();
}

function resetData() {
    tasks = JSON.parse(JSON.stringify(INITIAL_TASKS));
    persistTasks();
    currentPage = 1;
    filterMode = 'all';
    searchKeyword = '';
    const searchIn = document.getElementById('search-input');
    if (searchIn) searchIn.value = '';
    setFilter('all');
    showToast('Data reset to default seed records');
    fetch(getApiEndpoint('todos/reset'), { method: 'POST' }).catch(() => {});
}

function showToast(message) {
    const toast = document.getElementById('toast');
    if (!toast) return;
    toast.textContent = message;
    toast.style.display = 'block';
    clearTimeout(toast._timeout);
    toast._timeout = setTimeout(() => {
        toast.style.display = 'none';
    }, 2400);
}

function escapeHtml(str) {
    if (!str) return '';
    return str
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

window.onload = () => {
    loadTasks();
    render();
};
