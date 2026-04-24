# YouTube Data ELT Pipeline

An automated ELT (Extract, Load, Transform) pipeline that pulls video analytics from a YouTube channel, stores them in a PostgreSQL data warehouse, and validates data quality — orchestrated with Apache Airflow and containerized with Docker.

---

## Overview

```
YouTube API
    ↓
[produce_json DAG]  →  Fetch playlist & video stats  →  Save to JSON
    ↓
[update_db DAG]     →  Load to staging  →  Transform to core schema
    ↓
[data_quality DAG]  →  Validate staging & core with Soda checks
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Orchestration | Apache Airflow 2.9.2 (CeleryExecutor) |
| Data Warehouse | PostgreSQL 13 |
| Message Broker | Redis 7.2 |
| Data Quality | Soda Core 3.3.14 |
| Containerization | Docker & Docker Compose |
| CI/CD | GitHub Actions |
| Language | Python 3.10 |

---

## DAGs

### `produce_json` — Daily at 2 PM
Fetches data from the YouTube Data API and saves it as a JSON file.

```
get_playlist_id → get_video_ids → extract_video_data → save_to_json → trigger_update_db
```

### `update_db` — Triggered by `produce_json`
Loads the JSON file into the staging schema, then transforms and promotes data to the core schema.

```
update_staging → update_core → trigger_data_quality
```

### `data_quality` — Triggered by `update_db`
Runs Soda checks on both schemas to catch NULLs, duplicates, and logical inconsistencies (e.g. likes > views).

```
soda_test_staging → soda_test_core
```

---

## Database Schema

Three PostgreSQL databases are provisioned automatically:

- `airflow_metadata_db` — Airflow internal state
- `celery_results_db` — Celery task results
- `elt_db` — Application data warehouse

### Staging Schema (`yt_api`)

| Column | Type | Notes |
|---|---|---|
| Video_ID | VARCHAR(11) | Primary key |
| Video_Title | TEXT | |
| Upload_Date | TIMESTAMP | |
| Duration | VARCHAR(20) | ISO 8601 format |
| Video_Views | INT | |
| Likes_Count | INT | |
| Comments_Count | INT | |

### Core Schema (`yt_api`)

| Column | Type | Notes |
|---|---|---|
| Video_ID | VARCHAR(11) | Primary key |
| Video_Title | TEXT | |
| Upload_Date | TIMESTAMP | |
| Duration | TIME | Parsed from ISO 8601 |
| Video_Type | VARCHAR(10) | `"Shorts"` (≤60s) or `"Normal"` |
| Video_Views | INT | |
| Likes_Count | INT | |
| Comments_Count | INT | |

---

## Project Structure

```
DataEngineer/
├── dags/
│   ├── main.py                          # DAG definitions
│   ├── api/
│   │   └── video_stats.py               # YouTube API integration
│   ├── datawarehouse/
│   │   ├── dwh.py                       # Staging & core task orchestration
│   │   ├── data_loading.py              # JSON parsing
│   │   ├── data_modification.py         # INSERT / UPDATE / DELETE logic
│   │   ├── data_transformation.py       # Duration parsing, video type classification
│   │   └── data_utils.py               # DB connections, schema/table creation
│   └── dataquality/
│       └── soda.py                      # Soda wrapper
├── include/
│   └── soda/
│       ├── checks.yml                   # Data quality rules
│       └── configuration.yml            # Soda datasource config
├── tests/
│   ├── unit_test.py                     # DAG integrity, task counts
│   ├── integration_test.py             # YouTube API & PostgreSQL connectivity
│   └── conftest.py                     # Fixtures (mocks, DB connections)
├── docker/
│   └── postgres/
│       └── init-multiple-databases.sh   # Initializes 3 PostgreSQL databases
├── docker-compose.yaml
├── Dockerfile
├── requirements.txt
└── .env                                 # (not committed — see below)
```

---

## Getting Started

### Prerequisites

- Docker & Docker Compose
- A YouTube Data API v3 key
- A DockerHub account (for CI/CD image push)

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd DataEngineer
```

### 2. Create your `.env` file

```env
# YouTube API
API_KEY=your_youtube_api_key
CHANNEL_HANDLE=@channelhandle

# PostgreSQL connection (used inside containers)
POSTGRES_CONN_USERNAME=postgres
POSTGRES_CONN_PASSWORD=postgres
POSTGRES_CONN_HOST=postgres
POSTGRES_CONN_PORT=5432

# Airflow metadata database
METADATA_DATABASE_NAME=airflow_metadata_db
METADATA_DATABASE_USERNAME=airflow_metadata_user
METADATA_DATABASE_PASSWORD=airflow_metadata_pass

# Celery result backend database
CELERY_BACKEND_NAME=celery_results_db
CELERY_BACKEND_USERNAME=celery_results_user
CELERY_BACKEND_PASSWORD=celery_results_pass

# ELT application database
ELT_DATABASE_NAME=elt_db
ELT_DATABASE_USERNAME=elt_user
ELT_DATABASE_PASSWORD=elt_pass

# Airflow settings
AIRFLOW_UID=50000
AIRFLOW_WWW_USER_USERNAME=admin
AIRFLOW_WWW_USER_PASSWORD=admin
FERNET_KEY=your_fernet_key

# DockerHub (CI/CD only)
DOCKERHUB_NAMESPACE=your_dockerhub_username
DOCKERHUB_REPOSITORY=your_repo_name
IMAGE_TAG=latest
```

> Generate a Fernet key with: `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`

### 3. Start the stack

```bash
docker compose up -d
```

Airflow UI will be available at http://localhost:8080 using the credentials from your `.env`.

### 4. Trigger the pipeline

Enable and trigger the `produce_json` DAG from the Airflow UI. The remaining DAGs will be triggered automatically.

---

## CI/CD

The GitHub Actions workflow (`.github/workflows/ci-cd_yt-elt.yaml`) runs on every push to `main` or `feature/*` branches and on pull requests to `main`.

**Job 1 — Build & Push Docker Image**
- Only runs if `Dockerfile` or `requirements.txt` changed (or on manual dispatch)
- Tags the image with the commit SHA and pushes to DockerHub

**Job 2 — Tests**
- Depends on a successful image build
- Runs unit, integration, and end-to-end DAG tests
- Sets `AIRFLOW_SKIP_TRIGGERS=true` to prevent cross-DAG triggers during CI

### Required GitHub Secrets

Add these in your repository's **Settings → Secrets and Variables**:

| Secret | Description |
|---|---|
| `API_KEY` | YouTube Data API key |
| `DOCKERHUB_USERNAME` | DockerHub username |
| `DOCKERHUB_TOKEN` | DockerHub access token |
| All `.env` database credentials | Same as your local `.env` |

---

## Testing

```bash
# Unit tests
pytest tests/unit_test.py

# Integration tests (requires running stack)
pytest tests/integration_test.py
```

- **Unit tests** — DAG import integrity, task counts, fixture validation
- **Integration tests** — YouTube API reachability, PostgreSQL connectivity

---

## Data Quality Checks

Soda checks run after every load and validate:

- No NULL `Video_ID` values in staging or core
- No duplicate `Video_ID` values
- `Likes_Count` and `Comments_Count` do not exceed `Video_Views`
