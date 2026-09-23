# APEX Schema Normalization FastAPI

FastAPI backend for the APEX Schema Normalization project.

The application will provide APIs for processing sample/unstructured JSON data, cleaning and normalizing the data, and generating recommended target table schemas.

---

## Prerequisites

The project currently uses:

- Python 3.12+
- FastAPI
- Uvicorn
- Git

> **Important:** Use Python 3.12 for this project. A different Python version may cause dependency compatibility issues.

---

## 1. Clone the Repository

Clone the repository using HTTPS:

```bash
git clone https://github.com/SaketTricon/Apex_SchemaNorm_FastAPI.git
```

Move into the project:

```bash
cd Apex_SchemaNorm_FastAPI
```

---

## 2. Create Python Virtual Environment

Create the virtual environment using Python 3.12:

### Mac/Linux

```bash
python3.12 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

### Windows

```bash
py -3.12 -m venv .venv
```

Activate it:

```bash
.venv\Scripts\activate
```

After activation, verify:

```bash
python --version
```

Expected:

```text
Python 3.12.x
```

You should also see `(.venv)` at the beginning of your terminal prompt.

---

## 3. Install Dependencies

Make sure the virtual environment is activated.

Then run:

```bash
pip install -r requirements.txt
```

---

## 4. Run the Application

From the project root directory:

```bash
uvicorn app.main:app --reload
```

The application will start at:

```text
http://127.0.0.1:8000
```

---

## 5. API Documentation

FastAPI automatically provides Swagger UI.

Open:

```text
http://127.0.0.1:8000/docs
```

Alternative API documentation:

```text
http://127.0.0.1:8000/redoc
```

---

## 6. Health Check

The application currently provides:

```text
GET /health
```

Example:

```bash
curl http://127.0.0.1:8000/health
```

Expected response:

```json
{
  "status": "healthy"
}
```

---

## 7. Project Structure

```text
Apex_SchemaNorm_FastAPI/
│
├── app/
│   ├── api/
│   │   └── routes/
│   │
│   ├── core/
│   │
│   ├── models/
│   │
│   ├── services/
│   │
│   └── main.py
│
├── tests/
│
├── .gitignore
├── requirements.txt
└── README.md
```

### Directory Responsibilities

| Directory | Purpose |
|---|---|
| `app/main.py` | FastAPI application entry point |
| `app/api/` | API routes/endpoints |
| `app/core/` | Application configuration and common components |
| `app/models/` | Pydantic/data models |
| `app/services/` | Business logic and processing |
| `tests/` | Unit and integration tests |

---

## 8. Development Workflow

Create a new branch before making changes:

```bash
git checkout main
git pull origin main
git checkout -b feature/<feature-name>
```

Example:

```bash
git checkout -b feature/schema-parser
```

Make your changes and test locally.

Check your changes:

```bash
git status
```

Stage the changes:

```bash
git add .
```

Commit:

```bash
git commit -m "Add schema parser"
```

Push your branch:

```bash
git push -u origin feature/schema-parser
```

Then create a Pull Request on GitHub.

---

## 9. Getting Latest Changes

Before starting new work:

```bash
git checkout main
git pull origin main
```

Then create your feature branch:

```bash
git checkout -b feature/<feature-name>
```

If you already have a feature branch and need the latest `main` changes:

```bash
git checkout main
git pull origin main
git checkout <your-branch>
```

---

## 10. Important Git Rules

### Do not commit the virtual environment

The `.venv/` directory is ignored by Git.

Do not force-add it.

### Do not commit secrets

Do not commit:

- API keys
- Passwords
- Tokens
- `.env` files
- Private credentials

Use environment variables for secrets.

### Do not work directly on `main`

Create a feature branch for your changes and raise a Pull Request.

---

## 11. Deactivate Virtual Environment

When finished working:

```bash
deactivate
```

To start working again:

```bash
cd Apex_SchemaNorm_FastAPI
source .venv/bin/activate
```

---

## 12. Quick Start

For an existing contributor, the complete setup is:

```bash
git clone https://github.com/SaketTricon/Apex_SchemaNorm_FastAPI.git

cd Apex_SchemaNorm_FastAPI

python3.12 -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt

uvicorn app.main:app --reload
```

Then open:

```text
http://127.0.0.1:8000/docs
```

---

## APEX Project

The backend will be extended to support:

1. Sample/unstructured JSON input
2. JSON cleaning and normalization
3. Schema analysis
4. Entity identification
5. Target table recommendations
6. Column mapping
7. Data type recommendations
8. AI/LLM-based analysis
9. RAG and/or local/hosted LLM integration
10. Final schema recommendation

These components will be added incrementally as the project develops.
