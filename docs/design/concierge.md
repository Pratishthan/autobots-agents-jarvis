# Plan: Rename "jarvis" domain to "concierge"

## Context

The `autobots-agents-jarvis` repo serves as a **template** for new multi-domain projects. Both the source root package (`autobots_agents_jarvis`) and the primary demo domain (`domains/jarvis/`) use the word "jarvis", making scaffolding ambiguous — a single find-and-replace can't distinguish the two levels.

**Solution**: Rename the demo domain from "jarvis" to "concierge". The source root stays `autobots_agents_jarvis`. This gives the template two clearly distinct names, enabling clean two-pass scaffolding.

## Changes

### 1. Rename directories

| From | To |
|------|-----|
| `src/autobots_agents_jarvis/domains/jarvis/` | `domains/concierge/` |
| `agent_configs/jarvis/` | `agent_configs/concierge/` |
| `tests/unit/domains/jarvis/` | `tests/unit/domains/concierge/` |
| `tests/integration/domains/jarvis/` | `tests/integration/domains/concierge/` |
| `tests/sanity/domains/jarvis/` | `tests/sanity/domains/concierge/` |

### 2. Rename files

| From | To |
|------|-----|
| `sbin/run_jarvis.sh` | `sbin/run_concierge.sh` |
| `domains/jarvis/jarvis_batch.py` | `domains/concierge/concierge_batch.py` |

### 3. Settings refactoring (two-level pattern)

**`configs/settings.py`** — rename to shared `AppSettings`:
- `JarvisSettings` → `AppSettings`
- `get_jarvis_settings()` → `get_app_settings()`
- `init_jarvis_settings(settings)` → `init_app_settings(settings: AppSettings | None = None)` — accepts optional subclass instance
- `app_name` default stays generic (scaffold will override)
- Docstring: `"""Pydantic settings for application configuration.\nExtends DynagentSettings with app-level settings."""`

**`domains/concierge/settings.py`** — NEW file, domain-specific:
```python
class ConciergeSettings(AppSettings):
    default_city: str = Field(default="London", description="Default city for weather lookups")
    default_joke_category: str = Field(default="general", description="Default joke category")

def get_concierge_settings() -> ConciergeSettings: ...
def init_concierge_settings() -> ConciergeSettings:
    s = ConciergeSettings()
    init_app_settings(s)  # chains: concierge → app → dynagent
    return s
```

**Other domains** (`customer_support/server.py`, `sales/server.py`):
- Change `init_jarvis_settings()` → `init_app_settings()` (direct call, no domain subclass)

### 4. Content replacements (domain-level only)

Applied in order (most-specific first). **`autobots_agents_jarvis` / `autobots-agents-jarvis` are NOT touched.**

| Old | New |
|-----|-----|
| `register_jarvis_tools` | `register_concierge_tools` |
| `_get_jarvis_batch_agents` | `_get_concierge_batch_agents` |
| `jarvis_registered` | `concierge_registered` |
| `jarvis_tools_registered` | `concierge_tools_registered` |
| `jarvis_batch` | `concierge_batch` |
| `jarvis_chat` | `concierge_chat` |
| `jarvis-chat` | `concierge-chat` |
| `jarvis_tools` | `concierge_tools` |
| `jarvis-invoke-demo` | `concierge-invoke-demo` |
| `run_jarvis` | `run_concierge` |
| `setup_jarvis` | `setup_concierge` |
| `jarvis_dir` | `concierge_dir` |
| `jarvis_agents` | `concierge_agents` |
| `JARVIS_DIR` / `JARVIS` (shell vars) | `CONCIERGE_DIR` / `CONCIERGE` |
| `_JARVIS_CONFIG` | `_CONCIERGE_CONFIG` |
| `Jarvis` (display name in docs/comments/UI) | `Concierge` |
| `jarvis` (catch-all: config paths, env vars) | `concierge` |

### 5. Add `validate_email` to `register_concierge_tools`

In `domains/concierge/tools.py`, import `validate_email` from `common.tools.validation_tools` and include it in `register_concierge_tools()` to demonstrate the shared-tool-in-domain pattern.

### 6. Files affected

**Source code:**
- `src/autobots_agents_jarvis/configs/settings.py` — refactor to `AppSettings`
- `src/autobots_agents_jarvis/domains/concierge/settings.py` — NEW: `ConciergeSettings`
- `src/autobots_agents_jarvis/domains/concierge/server.py` — use `init_concierge_settings()`
- `src/autobots_agents_jarvis/domains/concierge/tools.py` — rename + add `validate_email`
- `src/autobots_agents_jarvis/domains/concierge/services.py` — docstring update
- `src/autobots_agents_jarvis/domains/concierge/concierge_batch.py` — rename + content
- `src/autobots_agents_jarvis/domains/concierge/call_invoke_agent.py` — content updates
- `src/autobots_agents_jarvis/domains/concierge/get_schema_for_agent.py` — content updates
- `src/autobots_agents_jarvis/domains/customer_support/server.py` — `init_app_settings()`
- `src/autobots_agents_jarvis/domains/sales/server.py` — `init_app_settings()`

**Tests:**
- `tests/conftest.py` — `AppSettings`, `_CONCIERGE_CONFIG_*`, docstring
- `tests/helpers.py` — `concierge_tools_registered()`
- `tests/unit/domains/concierge/conftest.py`
- `tests/unit/domains/concierge/test_tools.py`
- `tests/integration/domains/concierge/conftest.py`
- `tests/integration/domains/concierge/test_batch.py`
- `tests/sanity/domains/concierge/conftest.py`
- `tests/sanity/domains/concierge/test_dynagent_canary.py`

**Config/infra:**
- `Makefile`
- `Dockerfile`
- `docker-compose.yml`
- `.env.example`
- `sbin/run_concierge.sh` (renamed from `run_jarvis.sh`)
- `sbin/run_all_domains.sh`
- `sbin/sanity_test.sh`
- `agent_configs/concierge/agents.yaml`

**Docs:**
- `README.md` — all domain-level "Jarvis" → "Concierge", keep repo name untouched

### 7. Docker: parameterize for per-domain images

**Dockerfile** — add `DOMAIN` build arg:
```dockerfile
ARG DOMAIN=concierge
ENV APP_DOMAIN=${DOMAIN}
# ... rest of build unchanged ...
CMD ["sh", "-c", "bash sbin/run_${APP_DOMAIN}.sh"]
```

**docker-compose.yml** — three services with shared env via YAML anchors:
```yaml
x-common-env: &common-env
  GOOGLE_API_KEY: ${GOOGLE_API_KEY}
  LANGFUSE_PUBLIC_KEY: ${LANGFUSE_PUBLIC_KEY:-}
  # ... etc ...

services:
  concierge-chat:
    build: { context: ., args: { DOMAIN: concierge } }
    ports: ["1337:1337"]
    environment:
      <<: *common-env
      DYNAGENT_CONFIG_ROOT_DIR: /app/agent_configs/concierge

  customer-support-chat:
    build: { context: ., args: { DOMAIN: customer_support } }
    ports: ["1338:1338"]
    environment:
      <<: *common-env
      DYNAGENT_CONFIG_ROOT_DIR: /app/agent_configs/customer-support

  sales-chat:
    build: { context: ., args: { DOMAIN: sales } }
    ports: ["1339:1339"]
    environment:
      <<: *common-env
      DYNAGENT_CONFIG_ROOT_DIR: /app/agent_configs/sales
```

**Makefile** — parameterize docker targets:
```makefile
DOMAIN ?= concierge
docker-build:
    docker build --build-arg DOMAIN=$(DOMAIN) -t $(DOCKER_IMAGE_NAME)-$(DOMAIN) .
```

### 8. Update scaffold.py for two-level scaffolding

After rename, scaffold.py handles TWO independent name spaces:

1. **Source root**: `autobots_agents_jarvis` → `autobots_<name>`
2. **Domain**: `concierge` → `<primary_domain>`

Add `--primary-domain` flag (defaults to `<name>` for backward compat):
```
python3 sbin/scaffold.py kbe-pay                           # both levels = kbe_pay
python3 sbin/scaffold.py kbe-pay --primary-domain nurture   # src_root=kbe_pay, domain=nurture
```

Changes to scaffold.py:
- Add `--primary-domain` CLI arg
- Add `derive_domain_names()` for domain-level name variants (concierge → new domain)
- Split `build_replacements()` into source-root replacements + domain replacements
- Update `rename_paths()` to handle `concierge` → `<domain>` directory renames
- Update `PATHS_TO_REMOVE` to reference `concierge` instead of `jarvis`
- Update domain settings: rename `ConciergeSettings` → `<Domain>Settings`, `concierge_settings.py` → `<domain>_settings.py`

### 9. Update CLAUDE.md

Update workspace-level `CLAUDE.md` to reflect:
- Domain rename (jarvis → concierge in domain references)
- New `AppSettings` / `ConciergeSettings` pattern
- Updated Docker multi-domain support
- Keep `autobots_agents_jarvis` as source root unchanged

### 10. Phase 2 note (future)

Move hardcoded `APP_NAME` values to `app_constants.py` (shared) and `concierge_constants.py` (domain). Not in scope for this change.

## Execution order

1. Rename directories (bottom-up to avoid breaking paths)
2. Rename files (`run_jarvis.sh`, `jarvis_batch.py`)
3. Refactor `configs/settings.py` → `AppSettings`
4. Create `domains/concierge/settings.py` with `ConciergeSettings`
5. Apply content replacements across all text files
6. Update `customer_support/server.py` and `sales/server.py` → `init_app_settings()`
7. Add `validate_email` to `register_concierge_tools()`
8. Update Dockerfile and docker-compose.yml for per-domain builds
9. Update scaffold.py for two-level support
10. Update README.md and CLAUDE.md
11. Run verification

## Verification

```bash
cd autobots-agents-jarvis
make all-checks    # format, lint, type-check, test
```

Confirm no remaining domain-level "jarvis" references (excluding repo/package name):
```bash
grep -rn "jarvis" --include="*.py" --include="*.yaml" --include="*.sh" --include="*.toml" \
  src/ tests/ sbin/ agent_configs/ \
  | grep -v "autobots_agents_jarvis" \
  | grep -v "autobots-agents-jarvis"
```

Docker build test:
```bash
make docker-build DOMAIN=concierge
make docker-build DOMAIN=customer_support
make docker-build DOMAIN=sales
```
