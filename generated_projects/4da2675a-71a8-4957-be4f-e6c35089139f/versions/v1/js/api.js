/**
 * Simulated REST API Client for Todo Management
 * Wraps LocalStorage operations into asynchronous REST-like endpoints
 * supporting pagination, status filtering, validation, and structured error responses.
 */

import { StorageService } from './storage.js';
import { Validator } from './validator.js';

export const ApiService = {
    /**
     * Helper to wrap responses in standard REST format with simulated network delay
     */
    async _respond(data, status = 200, error = null) {
        return new Promise((resolve, reject) => {
            setTimeout(() => {
                if (status >= 400) {
                    reject({
                        status,
                        error: error || 'An error occurred',
                        timestamp: new Date().toISOString()
                    });
                } else {
                    resolve({
                        status,
                        data,
                        timestamp: new Date().toISOString()
                    });
                }
            }, 150); // Simulate network latency
        });
    },

    /**
     * GET /todos
     * Retrieves a paginated list of todos with optional status filtering
     * @param {Object} params - Query parameters { status, page, limit }
     */
    async getTodos(params = {}) {
        try {
            let todos = StorageService.getAllTodos();

            // Status filtering
            if (params.status && params.status !== 'all') {
                todos = todos.filter(t => t.status === params.status);
            }

            // Pagination parameters
            const page = parseInt(params.page, 10) || 1;
            const limit = parseInt(params.limit, 10) || 5;
            const startIndex = (page - 1) * limit;
            const endIndex = startIndex + limit;

            const paginatedItems = todos.slice(startIndex, endIndex);

            const responsePayload = {
                items: paginatedItems,
                meta: {
                    total: todos.length,
                    page,
                    limit,
                    totalPages: Math.ceil(todos.length / limit) || 1
                }
            };

            return await this._respond(responsePayload, 200);
        } catch (err) {
            return await this._respond(null, 500, err.message || 'Internal Server Error');
        }
    },

    /**
     * GET /todos/{id}
     * Retrieves a single todo item by ID
     * @param {string} id 
     */
    async getTodoById(id) {
        try {
            const todo = StorageService.getTodoById(id);
            if (!todo) {
                return await this._respond(null, 404, `Todo with id '${id}' not found`);
            }
            return await this._respond(todo, 200);
        } catch (err) {
            return await this._respond(null, 500, err.message || 'Internal Server Error');
        }
    },

    /**
     * POST /todos
     * Creates a new todo item
     * @param {Object} payload - { title, description, status }
     */
    async createTodo(payload) {
        try {
            // Validate incoming payload
            const validation = Validator.validateTodoCreation(payload);
            if (!validation.isValid) {
                return await this._respond({ errors: validation.errors }, 400, 'Validation Error');
            }

            const newTodo = StorageService.createTodo({
                title: payload.title.trim(),
                description: payload.description ? payload.description.trim() : '',
                status: payload.status || 'pending'
            });

            return await this._respond(newTodo, 201);
        } catch (err) {
            return await this._respond(null, 500, err.message || 'Internal Server Error');
        }
    },

    /**
     * PUT /todos/{id}
     * Fully updates an existing todo item
     * @param {string} id 
     * @param {Object} payload 
     */
    async updateTodo(id, payload) {
        try {
            const existing = StorageService.getTodoById(id);
            if (!existing) {
                return await this._respond(null, 404, `Todo with id '${id}' not found`);
            }

            const validation = Validator.validateTodoCreation(payload);
            if (!validation.isValid) {
                return await this._respond({ errors: validation.errors }, 400, 'Validation Error');
            }

            const updated = StorageService.updateTodo(id, {
                title: payload.title.trim(),
                description: payload.description ? payload.description.trim() : '',
                status: payload.status || existing.status
            });

            return await this._respond(updated, 200);
        } catch (err) {
            return await this._respond(null, 500, err.message || 'Internal Server Error');
        }
    },

    /**
     * PATCH /todos/{id}
     * Partially updates a todo item (e.g. toggling status or editing title)
     * @param {string} id 
     * @param {Object} payload 
     */
    async patchTodo(id, payload) {
        try {
            const existing = StorageService.getTodoById(id);
            if (!existing) {
                return await this._respond(null, 404, `Todo with id '${id}' not found`);
            }

            const validation = Validator.validateTodoUpdate(payload);
            if (!validation.isValid) {
                return await this._respond({ errors: validation.errors }, 400, 'Validation Error');
            }

            const updated = StorageService.updateTodo(id, payload);
            return await this._respond(updated, 200);
        } catch (err) {
            return await this._respond(null, 500, err.message || 'Internal Server Error');
        }
    },

    /**
     * DELETE /todos/{id}
     * Removes a todo item by ID
     * @param {string} id 
     */
    async deleteTodo(id) {
        try {
            const existing = StorageService.getTodoById(id);
            if (!existing) {
                return await this._respond(null, 404, `Todo with id '${id}' not found`);
            }

            StorageService.deleteTodo(id);
            return await this._respond({ message: `Todo ${id} successfully deleted` }, 200);
        } catch (err) {
            return await this._respond(null, 500, err.message || 'Internal Server Error');
        }
    }
};
