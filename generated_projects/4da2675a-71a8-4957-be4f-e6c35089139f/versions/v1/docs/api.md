### Endpoints

- **POST /todos**: Create a new todo item with title, description, and status.
- **GET /todos**: Retrieve a paginated list of todos with optional status filtering (`pending` or `completed`).
- **GET /todos/{id}**: Retrieve a single todo item by its unique ID.
- **PUT /todos/{id}**: Fully update an existing todo item.
- **PATCH /todos/{id}**: Partially update an existing todo item.
- **DELETE /todos/{id}**: Remove a todo item by ID.