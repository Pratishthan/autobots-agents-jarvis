# Scaffolding a New Project from the Jarvis Template

This guide walks you through creating your own Dynagent-based project from the **autobots-agents-jarvis** template and running the scaffold script to rename the repo and primary domain to your project.

## 1. Create Your Repo from the Jarvis Template

Choose one of the following ways to create a new repository from the Jarvis template.

### Option A: GitHub “Use this template”

1. Open the [autobots-agents-jarvis](https://github.com/your-org/autobots-agents-jarvis) repository on GitHub.
2. Click **Use this template** → **Create a new repository**.
3. Enter your new repository name (e.g. `autobots-kbe-pay` or `my-app`). You can name it with or without the `autobots-` prefix; the scaffold script will normalize it.
4. Choose visibility and create the repository.
5. Clone your new repo locally:
   ```bash
   git clone https://github.com/your-org/autobots-kbe-pay.git
   cd autobots-kbe-pay
   ```

### Option B: Clone and push to a new remote

1. Clone the template repo:
   ```bash
   git clone https://github.com/your-org/autobots-agents-jarvis.git my-project
   cd my-project
   ```
2. Create a new empty repository on GitHub (or your Git host) with the name you want (e.g. `autobots-kbe-pay`).
3. Point the local clone at your new repo and push:
   ```bash
   git remote set-url origin https://github.com/your-org/autobots-kbe-pay.git
   git push -u origin main
   ```

After this step you should be in the root of a repo that still looks like **autobots-agents-jarvis** (template state). Do **not** run the scaffold script from inside a monorepo that shares a parent with the template; run it only in this new, dedicated clone.

---

## 2. Run the Scaffold Script

The scaffold script renames the template to your project and primary domain, removes demo domains (Customer Support and Sales), cleans build artifacts, and configures the repo for standalone use (local `.venv`, no shared-lib path dependency). It must be run **from the project root** of a repo created from the Jarvis template.

### Prerequisites

- **Python 3.12+** available on your PATH (the script only uses the standard library).
- You are in the **root directory** of the cloned template repo (the directory that contains `sbin/` and `src/autobots_agents_jarvis/`).

### Basic usage

```bash
# From the project root
python3 sbin/scaffold.py <project-name>
```

**Project name** must be lowercase with hyphens (e.g. `kbe-pay`, `my-app`). The script will:

- Derive repo/package names (e.g. `autobots-kbe-pay`, `autobots_kbe_pay`).
- Use the same value as the **primary domain** unless you pass `--primary-domain` (so the “concierge” domain becomes your domain name).

**Examples:**

```bash
# Project and primary domain both "kbe-pay" → package autobots_kbe_pay, domain kbe_pay
python3 sbin/scaffold.py kbe-pay

# Project "kbe-pay", primary domain "nurture" → package autobots_kbe_pay, domain nurture
python3 sbin/scaffold.py kbe-pay --primary-domain nurture

# With display name and description
python3 sbin/scaffold.py kbe-pay --display-name "KBE Pay" --description "Payment agent for KBE"

# Custom port (default is 2337)
python3 sbin/scaffold.py kbe-pay --port 8080

# See what would be done without changing anything
python3 sbin/scaffold.py kbe-pay --dry-run
```

### Command-line options

| Option | Description |
|--------|-------------|
| `name` | **(Required)** Project name: lowercase, hyphens only (e.g. `kbe-pay`). |
| `--primary-domain` | Primary domain name (e.g. `nurture`). Defaults to the project name. This is the domain that replaces “concierge” in code and paths. |
| `--display-name` | Human-readable name (e.g. `KBE Pay`). Defaults to a capitalized version of the project name. |
| `--description` | Short description written into `pyproject.toml`. |
| `--port` | Default Chainlit port (default: `2337`). |
| `--dry-run` | Print planned renames and edits only; do not modify files or delete the script. |

### What the script does

1. **Cleans template artifacts** — Removes `.coverage`, `coverage.xml`, `htmlcov`, `.pytest_cache`, `.ruff_cache`, and `poetry.lock`.
2. **Removes demo content** — Deletes the Customer Support and Sales domains (source, configs, run scripts, and tests) so only the primary domain remains.
3. **Applies renames in content** — Replaces `autobots-agents-jarvis` / `autobots_agents_jarvis` with your project names, and `concierge` (and variants) with your primary domain name across text files.
4. **Renames paths** — Renames the top-level package directory (e.g. `autobots_agents_jarvis` → `autobots_kbe_pay`) and the primary domain directory (e.g. `concierge` → `nurture` in `src`, `agent_configs`, and tests).
5. **Standalone repo config** — Switches Makefile, `pyproject.toml`, and `.pre-commit-config.yaml` from monorepo mode to standalone (local `.venv`, no parent shared-lib).
6. **Optional overrides** — If you passed `--description` or `--port`, updates `pyproject.toml`, Makefile, domain settings, and the run script accordingly.
7. **Self-removal** — Deletes `sbin/scaffold.py` so it is not left in the scaffolded repo.

### After scaffolding

The script prints suggested next steps. Typically:

```bash
cp .env.example .env
# Edit .env with your API keys (e.g. GOOGLE_API_KEY, ANTHROPIC_API_KEY)
make install-dev
make all-checks
make chainlit-dev   # starts your domain UI on the configured port
```

Commit the scaffolded state to your new repo:

```bash
git add -A
git status   # review renames and changes
git commit -m "Scaffold from autobots-agents-jarvis template"
git push
```

---

## Summary

| Step | Action |
|------|--------|
| 1 | Create a new repo from the Jarvis template (GitHub “Use this template” or clone + new remote). |
| 2 | From the **project root**, run `python3 sbin/scaffold.py <project-name>` (add `--primary-domain`, `--display-name`, `--description`, `--port` as needed). |
| 3 | Use `--dry-run` first if you want to preview changes. |
| 4 | Copy `.env.example` to `.env`, add API keys, run `make install-dev` and `make chainlit-dev`. |

For more on the multi-domain layout and adding domains/agents, see the main [README](../../README.md) and [CLAUDE.md](../../../CLAUDE.md) in the workspace.
