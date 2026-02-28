# quizme-fast-api

A FastAPI application for quiz management.

## Prerequisites

- Python 3.7 or higher
- [uv](https://github.com/astral-sh/uv) - Fast Python package manager and installer

## Installation

### 1. Install uv (if not already installed)

On Windows:
```bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

On macOS/Linux:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Install dependencies

Navigate to the project directory and install all dependencies specified in `pyproject.toml`:

```bash
uv sync
```

This command will:
- Create a virtual environment (if needed)
- Install all dependencies listed in `pyproject.toml`
- Install the project in editable mode

### 3. Add new packages

To add a new package to the project:

```bash
uv add package_name
```

Example:
```bash
uv add requests
uv add fastapi
```

To add a development dependency:
```bash
uv add --dev pytest
```

## Running the App

### Development Mode

Start the FastAPI development server with hot-reload:

```bash
uv run fastapi dev
```

The server will start at `http://localhost:8000`

### Interactive API Documentation

Once the server is running, access the interactive API docs:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Project Structure

```
quizme-fast-api/
├── main.py                    # FastAPI app and router setup
├── pyproject.toml             # Project dependencies and metadata
├── README.md                  # This file
└── src/
    ├── controller/            # (Future) HTTP request handlers
    └── service/
        └── process-file.py    # Chat routes and business logic
```

## Common uv Commands

| Command | Description |
|---------|-------------|
| `uv sync` | Install all dependencies |
| `uv add <package>` | Add a new package |
| `uv remove <package>` | Remove a package |
| `uv pip list` | List installed packages |
| `uv run <command>` | Run a command in the project environment |
| `uv python list` | List available Python installations |

## Troubleshooting

### If `uv run fastapi dev` fails with Exit Code 1

1. Ensure all dependencies are installed:
   ```bash
   uv sync
   ```

2. Check if fastapi is installed:
   ```bash
   uv pip list | grep fastapi
   ```

3. Reinstall dependencies:
   ```bash
   uv sync --reinstall
   ```