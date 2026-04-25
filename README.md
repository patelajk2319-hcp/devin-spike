# Event-Driven Vulnerability Remediation System

Watches a GitHub repository for issues labeled `automation:remediation`, spawns a [Devin](https://devin.ai) session to fix each one, and reports back via PR links and issue comments.

## Architecture

```
GitHub Issue (labeled) → POST /webhook → task_service → devin_service
                                              ↓
                                          SQLite DB
                                              ↓
                                    worker/poller (every 30s)
                                              ↓
                               GitHub PR comment + issue update
                                              ↓
                                     GET /metrics endpoint
```

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env and fill in your tokens
```

Required variables:

| Variable | Description |
|---|---|
| `DEVIN_API_TOKEN` | Devin API token for `patelajk-devin` |
| `GITHUB_TOKEN` | GitHub PAT with `repo` scope |
| `GITHUB_WEBHOOK_SECRET` | Secret for validating webhook signatures |
| `GITHUB_REPO` | Fork to monitor, e.g. `patelajk/superset` |

### 3. Seed issues

```bash
task seed
# or: python scripts/create_issues.py
```

### 4. Start the system

```bash
task up
```

This starts the FastAPI server (port 8000) and the background poller. Watch for `ready` in the output.

### 5. Configure a GitHub webhook

In your fork → Settings → Webhooks → Add webhook:
- **Payload URL:** `https://<your-host>/webhook` (or use [ngrok](https://ngrok.com) locally)
- **Content type:** `application/json`
- **Secret:** value of `GITHUB_WEBHOOK_SECRET`
- **Events:** Issues

## Task commands

| Command | Description |
|---|---|
| `task up` | Start API + poller, wait for ready |
| `task down` | Stop processes, delete non-main branches, clear DB |
| `task stop` | Stop background processes only |
| `task seed` | Create remediation issues in the fork |
| `task clean-branches` | Delete all branches except main/master |
| `task clean-db` | Wipe the tasks table |
| `task metrics` | Print current metrics from the API |
| `task tasks-list` | List all tasks from the API |
| `task docker-up` | Start via Docker Compose |
| `task docker-down` | Stop Docker Compose |

## API Endpoints

| Endpoint | Description |
|---|---|
| `POST /webhook` | GitHub webhook receiver |
| `GET /health` | Health check |
| `GET /metrics` | Task counts by status |
| `GET /tasks` | All tasks |
| `GET /tasks/{id}` | Single task detail |

## Local development with ngrok

```bash
ngrok http 8000
# Copy the https URL → set as webhook payload URL in GitHub
```

## Docker

```bash
task docker-up
```
