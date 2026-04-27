# Devin Remediation Demo

Label a GitHub issue → Devin fixes it → PR opened automatically.

## How It Works

```
GitHub issue labeled  →  webhook  →  Devin session started  →  PR opened  →  issue commented
```

A background poller checks session status every 30s and finalises each task when Devin finishes.

## Prerequisites

### Required Tools (install via Homebrew)
```bash
brew install go-task
brew install python
brew install --cask ngrok
```

### Python Dependencies
```bash
pip install -r requirements.txt
```

## Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/<your-org>/devin-spike.git
cd devin-spike
```

### 2. Create `.env` File
```bash
cp .env.example .env
```

Fill in the four required values:

```bash
# Devin API token
DEVIN_API_TOKEN=<your-devin-api-token>

# GitHub personal access token with repo scope
GITHUB_TOKEN=<your-github-pat>

# Secret used to verify webhook signatures
GITHUB_WEBHOOK_SECRET=<your-webhook-secret>

# Repo to monitor, e.g. your-org/your-repo
GITHUB_REPO=<your-org/your-repo>
```

### 3. Generate a Webhook Secret
```bash
openssl rand -hex 32
```

Copy the output into `GITHUB_WEBHOOK_SECRET` in your `.env` file.

### 4. Expose Your Local Server *(skip if deployed)*

ngrok creates a public HTTPS tunnel to your local server so GitHub can deliver webhooks to it.

1. Sign up at [ngrok.com](https://ngrok.com) and get your auth token
2. Authenticate the CLI:
```bash
ngrok config add-authtoken <your-auth-token>
```
3. Start the tunnel:
```bash
ngrok http 8000
```
4. Copy the `Forwarding` URL (e.g. `https://abc123.ngrok-free.app`) — you'll need it in the next step

### 5. Add a GitHub Webhook

Repo → Settings → Webhooks → Add webhook:
- Payload URL: `https://<ngrok-url>/webhook`
- Content type: `application/json`
- Secret: your `GITHUB_WEBHOOK_SECRET`
- Events: Issues

### 6. Start the Stack
```bash
task up
```

### 7. Seed Issues *(triggers the demo)*
```bash
task seed
```

Watch Devin open PRs and comment on each issue automatically.

## Available Commands

Run `task --list` to see all available commands.

| Command | Description |
|---|---|
| `task up` | Start API + poller |
| `task down` | Full reset — stop, close PRs, delete branches, clear DB |
| `task seed` | Create demo issues in the repo |
| `task logs` | Tail live logs |
| `task status` | Show task table from DB |
| `task metrics` | Show task counts from API |

## Architecture

- **FastAPI**: Webhook receiver and REST API
- **SQLite**: Lightweight task state store
- **Devin API**: AI agent that fixes issues and opens PRs
- **GitHub Webhooks**: Triggers on issue label events
- **Background Poller**: Checks Devin session status every 30s

## API

| Endpoint | Description |
|---|---|
| `GET /health` | Health check |
| `GET /metrics` | Task counts by status |
| `GET /tasks` | All tasks |
| `POST /webhook` | GitHub webhook receiver |

## Notes

- Devin is triggered only when an issue is labeled — not on every issue event
- Task state is persisted in a local SQLite database (`data/`)
- All sensitive values are stored in `.env` (gitignored)
