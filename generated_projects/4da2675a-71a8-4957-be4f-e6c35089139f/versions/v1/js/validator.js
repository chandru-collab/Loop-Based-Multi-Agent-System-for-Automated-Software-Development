/**
 * js/validator.js
 * Purpose: Validates incoming todo payload structures for creation and updates.
 * Enforces type checks, length constraints, and allowed status values.
 */

export const TodoValidator = {
  /**
   * Validates a payload for creating a new Todo.
   * @param {Object} payload 
   * @returns {{isValid: boolean, errors: Array<{field: string, message: string}>}}
   */
  validateCreate(payload) {
    const errors = [];

    if (!payload || typeof payload !== 'object') {
      return {
        isValid: false,
        errors: [{ field: 'body', message: 'Request body must be a valid JSON object.' }]
      };
    }

    // Validate title
    if (payload.title === undefined || payload.title === null) {
      errors.push({ field: 'title', message: 'Title is required.' });
    } else if (typeof payload.title !== 'string') {
      errors.push({ field: 'title', message: 'Title must be a string.' });
    } else {
      const trimmedTitle = payload.title.trim();
      if (trimmedTitle.length === 0) {
        errors.push({ field: 'title', message: 'Title cannot be empty.' });
      } else if (trimmedTitle.length > 100) {
        errors.push({ field: 'title', message: 'Title cannot exceed 100 characters.' });
      }
    }

    // Validate description
    if (payload.description !== undefined && payload.description !== null) {
      if (typeof payload.description !== 'string') {
        errors.push({ field: 'description', message: 'Description must be a string.' });
      } else if (payload.description.length > 500) {
        errors.push({ field: 'description', message: 'Description cannot exceed 500 characters.' });
      }
    }

    // Validate status if provided on create
    if (payload.status !== undefined && payload.status !== null) {
      const validStatuses = ['pending', 'completed'];
      if (!validStatuses.includes(payload.status)) {
        errors.push({ field: 'status', message: "Status must be either 'pending' or 'completed'." });
      }
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  },

  /**
   * Validates a payload for updating an existing Todo (PUT/PATCH).
   * @param {Object} payload 
   * @param {boolean} isPartial - true for PATCH, false for PUT
   * @returns {{isValid: boolean, errors: Array<{field: string, message: string}>}}
   */
  validateUpdate(payload, isPartial = false) {
    const errors = [];

    if (!payload || typeof payload !== 'object') {
      return {
        isValid: false,
        errors: [{ field: 'body', message: 'Request body must be a valid JSON object.' }]
      };
    }

    // If full update (PUT), title is required
    if (!isPartial) {
      if (payload.title === undefined || payload.title === null) {
        errors.push({ field: 'title', message: 'Title is required for full update.' });
      }
    }

    // Validate title if present
    if (payload.title !== undefined && payload.title !== null) {
      if (typeof payload.title !== 'string') {
        errors.push({ field: 'title', message: 'Title must be a string.' });
      } else {
        const trimmedTitle = payload.title.trim();
        if (trimmedTitle.length === 0) {
          errors.push({ field: 'title', message: 'Title cannot be empty.' });
        } else if (trimmedTitle.length > 100) {
          errors.push({ field: 'title', message: 'Title cannot exceed 100 characters.' });
        }
      }
    }

    // Validate description if present
    if (payload.description !== undefined && payload.description !== null) {
      if (typeof payload.description !== 'string') {
        errors.push({ field: 'description', message: 'Description must be a string.' });
      } else if (payload.description.length > 500) {
        errors.push({ field: 'description', message: 'Description cannot exceed 500 characters.' });
      }
    }

    // Validate status if present
    if (payload.status !== undefined && payload.status !== null) {
      const validStatuses = ['pending', 'completed'];
      if (!validStatuses.includes(payload.status)) {
        errors.push({ field: 'status', message: "Status must be either 'pending' or 'completed'." });
      }
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  },

  /**
   * Sanitizes string input against basic XSS vectors.
   * @param {string} str 
   * @returns {string}
   */
  sanitize(str) {
    if (typeof str !== 'string') return '';
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }
};