import { api } from './api.js';

export const UI = {
  elements: {
    todoList: document.getElementById('todo-list'),
    todoForm: document.getElementById('todo-form'),
    statusFilter: document.getElementById('status-filter'),
    pagination: document.getElementById('pagination'),
    toast: document.getElementById('toast')
  },

  showToast(message, type = 'info') {
    const toast = this.elements.toast;
    toast.textContent = message;
    toast.className = `fixed bottom-4 right-4 p-4 rounded shadow-lg text-white ${type === 'error' ? 'bg-red-500' : 'bg-green-500'}`;
    toast.classList.remove('hidden');
    setTimeout(() => toast.classList.add('hidden'), 3000);
  },

  renderTodos(todos) {
    const container = this.elements.todoList;
    container.innerHTML = '';

    if (todos.length === 0) {
      container.innerHTML = '<div class="p-4 text-center text-gray-500">No todos found.</div>';
      return;
    }

    todos.forEach(todo => {
      const div = document.createElement('div');
      div.className = 'p-4 border-b flex justify-between items-center hover:bg-gray-50';
      div.innerHTML = `
        <div>
          <h3 class="font-bold ${todo.status === 'completed' ? 'line-through text-gray-400' : ''}">${this.escapeHtml(todo.title)}</h3>
          <p class="text-sm text-gray-600">${this.escapeHtml(todo.description)}</p>
        </div>
        <div class="flex gap-2">
          <button onclick="window.toggleTodo('${todo.id}')" class="text-blue-500">${todo.status === 'pending' ? 'Complete' : 'Undo'}</button>
          <button onclick="window.deleteTodo('${todo.id}')" class="text-red-500">Delete</button>
        </div>
      `;
      container.appendChild(div);
    });
  },

  renderPagination(currentPage, totalPages) {
    const container = this.elements.pagination;
    container.innerHTML = '';
    for (let i = 1; i <= totalPages; i++) {
      const btn = document.createElement('button');
      btn.textContent = i;
      btn.className = `px-3 py-1 mx-1 border rounded ${i === currentPage ? 'bg-blue-500 text-white' : 'bg-white'}`;
      btn.onclick = () => window.loadTodos(i);
      container.appendChild(btn);
    }
  },

  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  },

  initForm(callback) {
    this.elements.todoForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const formData = new FormData(e.target);
      const data = {
        title: formData.get('title'),
        description: formData.get('description')
      };
      try {
        await callback(data);
        e.target.reset();
      } catch (err) {
        this.showToast(err.message, 'error');
      }
    });
  }
};