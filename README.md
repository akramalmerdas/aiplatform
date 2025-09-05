# AI Business Plan Generator

This project is a Django-based web application that uses AI to generate business plans based on user input from a guided interview.

## Quickstart

### 1. Set up the environment

You need Python 3.11 or higher.

```bash
# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
```

### 2. Install dependencies

Install the application dependencies and the developer tools.

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 3. Set up pre-commit hooks

Install the pre-commit hooks to automatically format and lint your code before each commit.

```bash
pre-commit install
```

You can also run the hooks on all files at any time:

```bash
pre-commit run --all-files
```

### 4. Create a `.env` file

Copy the `.env.example` to `.env` and fill in the required environment variables. At a minimum, you will need `DJANGO_SECRET_KEY` and `OPENAI_API_KEY`.

```bash
cp .env.example .env
```

### 5. Run database migrations

```bash
python server/manage.py migrate
```

### 6. Run the development server

```bash
python server/manage.py runserver 127.0.0.1:8080
```

The application will be available at `http://127.0.0.1:8080`.

## Usage

-   Navigate to `/chat` to start the guided interview.
-   Answer the questions one by one.
-   When the interview is complete, type `RESULTS`.
-   Navigate to `/results` to see your generated business plan.
-   Navigate to `/api/health` to check the status of the AI modules.
