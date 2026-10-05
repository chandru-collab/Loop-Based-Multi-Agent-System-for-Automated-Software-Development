/**
 * Comprehensive automated test suite for Todo API Simulation
 * Tests CRUD operations, status filtering, pagination, and validation.
 */

import { api } from '../js/api.js';
import { storage } from '../js/storage.js';
import { validator } from '../js/validator.js';

class TestRunner {
  constructor() {
    this.results = [];
    this.passed = 0;
    this.failed = 0;
  }

  async assert(name, assertionFn) {
    try {
      // Clear storage before each test for test isolation
      storage.clear();
      await assertionFn();
      this.results.push({ name, status: 'PASS' });
      this.passed++;
      console.log(`%c[PASS] ${name}`, 'color: green; font-weight: bold;');
    } catch (error) {
      this.results.push({ name, status: 'FAIL', error: error.message });
      this.failed++;
      console.error(`%c[FAIL] ${name}: ${error.message}`, 'color: red; font-weight: bold;');
    }
  }

  assertEqual(actual, expected, message = '') {
    const actualStr = JSON.stringify(actual);
    const expectedStr = JSON.stringify(expected);
    if (actualStr !== expectedStr) {
      throw new Error(`Assertion failed: ${message} | Expected ${expectedStr}, got ${actualStr}`);
    }
  }

  assertTrue(condition, message = '') {
    if (!condition) {
      throw new Error(`Assertion failed: ${message} | Expected true, got false`);
    }
  }

  assertThrows(fn, expectedMessage = '') {
    let threw = false;
    try {
      fn();
    } catch (error) {
      threw = true;
      if (expectedMessage && !error.message.includes(expectedMessage)) {
        throw new Error(`Expected error message to include "${expectedMessage}", got "${error.message}"`);
      }
    }
    if (!threw) {
      throw new Error('Expected function to throw an error, but it did not.');
    }
  }

  summary() {
    console.log('%c----------------------------------------', 'color: cyan;');
    console.log(`%cTest Suite Completed. Passed: ${this.passed}, Failed: ${this.failed}`, this.failed === 0 ? 'color: green; font-weight: bold;' : 'color: red; font-weight: bold;');
    console.log('%c----------------------------------------', 'color: cyan;');
    return { passed: this.passed, failed: this.failed, results: this.results };
  }
}

export async function runAllTests() {
  const runner = new TestRunner();

  console.log('%cStarting Todo REST API Test Suite...', 'color: blue; font-weight: bold;');

  // 1. Validation Tests
  await runner.assert('Validator catches missing title', () => {
    runner.assertThrows(() => {
      validator.validateTodoPayload({ description: 'No title here' });
    }, 'Title is required');
  });

  await runner.assert('Validator catches invalid status', () => {
    runner.assertThrows(() => {
      validator.validateTodoPayload({ title: 'Test', status: 'unknown_status' });
    }, 'Invalid status');
  });

  await runner.assert('Validator passes valid payload', () => {
    const validData = { title: 'Buy milk', description: '2 percent organic', status: 'pending' };
    const result = validator.validateTodoPayload(validData);
    runner.assertTrue(result.isValid, 'Payload should be valid');
  });

  // 2. CRUD API Tests
  await runner.assert('POST /todos creates a todo successfully (201 Created)', async () => {
    const res = await api.createTodo({
      title: 'Integration Test Todo',
      description: 'Testing POST endpoint',
      status: 'pending'
    });
    runner.assertEqual(res.status, 201, 'Status code should be 201');
    runner.assertTrue(res.data.id !== undefined, 'Todo should have generated ID');
    runner.assertEqual(res.data.title, 'Integration Test Todo');
    runner.assertEqual(res.data.status, 'pending');
  });

  await runner.assert('POST /todos with invalid payload returns 400 Bad Request', async () => {
    const res = await api.createTodo({ title: '' });
    runner.assertEqual(res.status, 400, 'Status code should be 400');
    runner.assertTrue(res.error !== undefined, 'Should return error message');
  });

  await runner.assert('GET /todos returns list of todos with pagination', async () => {
    // Seed 3 items
    await api.createTodo({ title: 'Task 1' });
    await api.createTodo({ title: 'Task 2' });
    await api.createTodo({ title: 'Task 3' });

    const res = await api.getTodos({ page: 1, limit: 2 });
    runner.assertEqual(res.status, 200);
    runner.assertEqual(res.data.length, 2, 'Should respect pagination limit of 2');
    runner.assertEqual(res.pagination.total, 3, 'Total count should be 3');
    runner.assertEqual(res.pagination.pages, 2, 'Total pages should be 2');
  });

  await runner.assert('GET /todos?status=completed filters correctly', async () => {
    const t1 = await api.createTodo({ title: 'Pending task', status: 'pending' });
    const t2 = await api.createTodo({ title: 'Completed task', status: 'completed' });

    const res = await api.getTodos({ status: 'completed' });
    runner.assertEqual(res.status, 200);
    runner.assertEqual(res.data.length, 1, 'Should return only 1 completed task');
    runner.assertEqual(res.data[0].id, t2.data.id);
  });

  await runner.assert('GET /todos/{id} returns specific todo or 404', async () => {
    const created = await api.createTodo({ title: 'Find me' });
    const todoId = created.data.id;

    const res = await api.getTodoById(todoId);
    runner.assertEqual(res.status, 200);
    runner.assertEqual(res.data.title, 'Find me');

    const notFoundRes = await api.getTodoById('non-existent-id');
    runner.assertEqual(notFoundRes.status, 404, 'Should return 404 for missing resource');
  });

  await runner.assert('PUT /todos/{id} updates todo completely', async () => {
    const created = await api.createTodo({ title: 'Old Title', description: 'Old Desc', status: 'pending' });
    const todoId = created.data.id;

    const updateRes = await api.updateTodo(todoId, {
      title: 'New Title',
      description: 'New Desc',
      status: 'completed'
    });

    runner.assertEqual(updateRes.status, 200);
    runner.assertEqual(updateRes.data.title, 'New Title');
    runner.assertEqual(updateRes.data.description, 'New Desc');
    runner.assertEqual(updateRes.data.status, 'completed');
  });

  await runner.assert('PATCH /todos/{id} updates todo partially', async () => {
    const created = await api.createTodo({ title: 'Static Title', status: 'pending' });
    const todoId = created.data.id;

    const patchRes = await api.patchTodo(todoId, { status: 'completed' });

    runner.assertEqual(patchRes.status, 200);
    runner.assertEqual(patchRes.data.title, 'Static Title', 'Title should remain unchanged');
    runner.assertEqual(patchRes.data.status, 'completed', 'Status should be updated');
  });

  await runner.assert('DELETE /todos/{id} removes todo successfully', async () => {
    const created = await api.createTodo({ title: 'Delete me' });
    const todoId = created.data.id;

    const deleteRes = await api.deleteTodo(todoId);
    runner.assertTrue(deleteRes.status === 200 || deleteRes.status === 204, 'Delete status should be 200 or 204');

    const getRes = await api.getTodoById(todoId);
    runner.assertEqual(getRes.status, 404, 'Deleted todo should return 404');
  });

  storage.clear();
  return runner.summary();
}
