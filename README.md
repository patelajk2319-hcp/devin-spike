# Devin Remediation Demo

Labels a GitHub issue → Devin fixes it → PR opened automatically.

## How it works

```
GitHub issue labeled  →  webhook  →  Devin session started  →  PR opened  →  issue commented
```

A background poller checks session status every 30s and finalises each task when Devin finishes.

## Quick start

**1. Install dependencies**
```bash
pip install -r requirements.txt
```

**2. Configure**
```bash
cp .env.example .env
# Fill in the four required values
```

| Variable | What it is |
|---|---|
| `DEVIN_API_TOKEN` | Devin API token |
| `GITHUB_TOKEN` | GitHub PAT with `repo` scope |
| `GITHUB_WEBHOOK_SECRET` | Any secret string — used to verify webhook signatures |
| `GITHUB_REPO` | Repo to monitor, e.g. `your-org/your-repo` |

**3. Expose your local server** *(skip if deployed)*
```bash
ngrok http 8000
```

**4. Add a GitHub webhook**

Repo → Settings → Webhooks → Add webhook:
- Payload URL: `https://<ngrok-url>/webhook`
- Content type: `application/json`
- Secret: your `GITHUB_WEBHOOK_SECRET`
- Events: Issues

**5. Start**
```bash
task up
```

**6. Seed issues** *(triggers the demo)*
```bash
task seed
```

Watch Devin open PRs and comment on each issue automatically.

## Commands

| Command | Description |
|---|---|
| `task up` | Start API + poller |
| `task down` | Full reset — stop, close PRs, delete branches, clear DB |
| `task seed` | Create demo issues in the repo |
| `task logs` | Tail live logs |
| `task status` | Show task table from DB |
| `task metrics` | Show task counts from API |

## API

| Endpoint | Description |
|---|---|
| `GET /health` | Health check |
| `GET /metrics` | Task counts by status |
| `GET /tasks` | All tasks |
| `POST /webhook` | GitHub webhook receiver |

