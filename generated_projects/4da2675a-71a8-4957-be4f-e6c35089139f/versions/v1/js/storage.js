/**
 * Storage & Persistence Module
 * Manages browser localStorage interactions, data schema validation/initialization,
 * and raw CRUD operations for Todo entities.
 */

const STORAGE_KEY = 'todo_rest_api_items';

export const StorageService = {
  /**
   * Initializes default seed data if localStorage is empty.
   */
  init() {
    try {
      const existing = localStorage.getItem(STORAGE_KEY);
      if (!existing) {
        const defaultTodos = [
          {
            id: '1',
            title: 'Setup Project Repository',
            description: 'Initialize base project structure and development dependencies',
            status: 'completed',
            created_at: new Date(Date.now() - 86400000 * 2).toISOString(),
            updated_at: new Date(Date.now() - 86400000 * 2).toISOString(),
          },
          {
            id: '2',
            title: 'Implement REST API Simulation',
            description: 'Build simulated endpoints for CRUD, pagination, and status filtering',
            status: 'completed',
            created_at: new Date(Date.now() - 86400000).toISOString(),
            updated_at: new Date(Date.now() - 86400000).toISOString(),
          },
          {
            id: '3',
            title: 'Write Comprehensive Test Suite',
            description: 'Implement automated test runner covering all acceptance criteria',
            status: 'pending',
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          },
        ];
        localStorage.setItem(STORAGE_KEY, JSON.stringify(defaultTodos));
      }
    } catch (error) {
      console.error('Failed to initialize storage:', error);
    }
  },

  /**
   * Retrieves all todo items from localStorage.
   * @returns {Array<Object>}
   */
  getAllTodos() {
    try {
      const data = localStorage.getItem(STORAGE_KEY);
      return data ? JSON.parse(data) : [];
    } catch (error) {
      console.error('Failed to read todos from storage:', error);
      return [];
    }
  },

  /**
   * Retrieves a single todo by ID.
   * @param {string} id 
   * @returns {Object|null}
   */
  getTodoById(id) {
    const todos = this.getAllTodos();
    return todos.find((todo) => todo.id === id) || null;
  },

  /**
   * Saves a new todo item into storage.
   * @param {Object} todoData 
   * @returns {Object}
   */
  createTodo(todoData) {
    const todos = this.getAllTodos();
    const now = new Date().toISOString();
    
    const newTodo = {
      id: Date.now().toString(),
      title: todoData.title.trim(),
      description: (todoData.description || '').trim(),
      status: todoData.status || 'pending',
      created_at: now,
      updated_at: now,
    };

    todos.unshift(newTodo);
    this.saveAllTodos(todos);
    return newTodo;
  },

  /**
   * Updates an existing todo item fully or partially.
   * @param {string} id 
   * @param {Object} updateData 
   * @returns {Object|null}
   */
  updateTodo(id, updateData) {
    const todos = this.getAllTodos();
    const index = todos.findIndex((todo) => todo.id === id);

    if (index === -1) {
      return null;
    }

    const existing = todos[index];
    const updatedTodo = {
      ...existing,
      title: updateData.title !== undefined ? updateData.title.trim() : existing.title,
      description: updateData.description !== undefined ? updateData.description.trim() : existing.description,
      status: updateData.status !== undefined ? updateData.status : existing.status,
      updated_at: new Date().toISOString(),
    };

    todos[index] = updatedTodo;
    this.saveAllTodos(todos);
    return updatedTodo;
  },

  /**
   * Deletes a todo item by ID.
   * @param {string} id 
   * @returns {boolean} true if deleted, false if not found
   */
  deleteTodo(id) {
    const todos = this.getAllTodos();
    const index = todos.findIndex((todo) => todo.id === id);

    if (index === -1) {
      return false;
    }

    todos.splice(index, 1);
    this.saveAllTodos(todos);
    return true;
  },

  /**
   * Persists the array of todos to localStorage.
   * @param {Array<Object>} todos 
   */
  saveAllTodos(todos) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(todos));
    } catch (error) {
      console.error('Failed to save todos to storage:', error);
      throw new Error('Storage quota exceeded or unavailable.');
    }
  },

  /**
   * Clears all storage items (useful for testing reset).
   */
  clear() {
    try {
      localStorage.removeItem(STORAGE_KEY);
    } catch (error) {
      console.error('Failed to clear storage:', error);
    }
  }
}; 
