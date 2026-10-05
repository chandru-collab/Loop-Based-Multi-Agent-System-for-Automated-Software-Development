# Todo REST API Simulator

This project is a 100% client-side Todo management application that simulates a REST API using browser `localStorage`. It provides a clean, responsive interface for managing tasks with full CRUD capabilities, pagination, and status filtering.

## Architecture

- **Frontend**: Vanilla JavaScript (ES6+), HTML5, Tailwind CSS.
- **Persistence**: Browser `localStorage` acting as the data store.
- **API Simulation**: A modular service layer that mimics RESTful endpoints.
- **Validation**: Client-side schema validation for all incoming requests.

## API Simulation Routes

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/todos` | Create a new todo item |
| `GET` | `/todos` | List todos (supports `page`, `limit`, `status` query params) |
| `GET` | `/todos/:id` | Retrieve a single todo by ID |
| `PUT` | `/todos/:id` | Full update of a todo item |
| `PATCH` | `/todos/:id` | Partial update (e.g., toggle status) |
| `DELETE` | `/todos/:id` | Remove a todo item |

## Features

- **CRUD Operations**: Create, Read, Update, and Delete tasks.
- **Filtering**: Filter tasks by 'pending' or 'completed' status.
- **Pagination**: Navigate through large lists of todos.
- **Validation**: Robust input checking for titles and descriptions.
- **Responsive UI**: Built with Tailwind CSS for mobile and desktop compatibility.

## Setup Instructions

1. Clone this repository to your local machine.
2. Open `index.html` in any modern web browser.
3. No backend server or database installation is required.

## Testing

- The project includes a `tests/app.test.js` file.
- To run tests, open the browser console while viewing the application or use a local development server to execute the test suite against the `api.js` module.

## Deployment

This application is fully static. You can deploy it to any static hosting provider:
- **GitHub Pages**: Push to a repository and enable Pages.
- **Netlify/Vercel**: Drag and drop the project folder into their dashboards.