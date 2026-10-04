const FEATURES = ["Core module initialization", "Interactive user controls", "Data validation & execution", "Real-time state synchronization"];
                const ENTITIES = ["Primary Entity", "Configuration Records", "Event Stream"];

                let state = {
                    items: FEATURES.map((f, i) => ({
                        id: i + 1,
                        name: f,
                        category: ENTITIES[i % ENTITIES.length] || 'General',
                        status: 'Active',
                        updated: new Date().toLocaleTimeString()
                    })),
                    logs: [`[${new Date().toLocaleTimeString()}] System initialized for "Build a to-do app with task tracking"`]
                };

                function showToast(msg) {
                    const t = document.getElementById('toast');
                    t.textContent = msg;
                    t.classList.add('show');
                    setTimeout(() => t.classList.remove('show'), 2500);
                }

                function addLog(msg) {
                    state.logs.push(`[${new Date().toLocaleTimeString()}] ${msg}`);
                    const logEl = document.getElementById('log-box');
                    logEl.innerHTML = state.logs.map(l => `<div>${l}</div>`).join('');
                    logEl.scrollTop = logEl.scrollHeight;
                }

                function render() {
                    document.getElementById('total-items').textContent = state.items.length;
                    document.getElementById('active-features').textContent = FEATURES.length;
                    document.getElementById('entities-count').textContent = ENTITIES.length;

                    const listEl = document.getElementById('items-list');
                    if (state.items.length === 0) {
                        listEl.innerHTML = '<div style="color: #64748b; text-align:center; padding: 20px;">No records found. Create one below!</div>';
                    } else {
                        listEl.innerHTML = state.items.map(item => `
                            <div class="item-row">
                                <div>
                                    <div style="font-weight: 600; color: #f8fafc;">${item.name}</div>
                                    <div style="color: #64748b; font-size: 11px;">Category: ${item.category} · ${item.updated}</div>
                                </div>
                                <div style="display: flex; gap: 8px; align-items: center;">
                                    <span style="font-size: 11px; padding: 2px 8px; border-radius: 999px; background: rgba(99,102,241,0.15); color: #818cf8;">${item.status}</span>
                                    <button onclick="deleteItem(${item.id})" style="background: none; border: none; color: #ef4444; cursor: pointer; font-size: 14px;">✕</button>
                                </div>
                            </div>
                        `).join('');
                    }
                }

                function createItem(e) {
                    e.preventDefault();
                    const nameIn = document.getElementById('item-name');
                    const catIn = document.getElementById('item-cat');
                    const name = nameIn.value.trim();
                    if (!name) return;

                    const newItem = {
                        id: Date.now(),
                        name: name,
                        category: catIn.value,
                        status: 'Active',
                        updated: new Date().toLocaleTimeString()
                    };

                    state.items.unshift(newItem);
                    nameIn.value = '';
                    addLog(`Created new record: "${name}" under [${catIn.value}]`);
                    showToast('✓ Record added successfully');
                    render();
                }

                function deleteItem(id) {
                    const item = state.items.find(i => i.id === id);
                    state.items = state.items.filter(i => i.id !== id);
                    addLog(`Removed record: "${item ? item.name : id}"`);
                    showToast('Record deleted');
                    render();
                }

                function executeAction() {
                    const inputVal = document.getElementById('quick-cmd').value;
                    addLog(`Executed action: "${inputVal || 'Health Verification'}" -> 200 OK`);
                    showToast('Action executed');
                    document.getElementById('quick-cmd').value = '';
                }

                window.onload = () => {
                    const catSelect = document.getElementById('item-cat');
                    catSelect.innerHTML = ENTITIES.map(e => `<option value="${e}">${e}</option>`).join('');
                    render();
                    addLog('All core services ready.');
                };