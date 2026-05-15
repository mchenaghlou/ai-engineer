# Virtual Environments in Python (AI Engineering Cheatsheet)

## 1. venv (standard library)

### Create environment
```bash
python -m venv .venv
```

Creates a local isolated environment in `.venv/`.

---

### Activate environment

**Linux / Mac**
```bash
source .venv/bin/activate
```

**Windows (PowerShell)**
```bash
.venv\Scripts\Activate.ps1
```

---

### Install packages
```bash
pip install numpy pandas fastapi
```

---

### List installed packages
```bash
pip list
```

```bash
pip freeze
```

- `pip list` → readable installed packages
- `pip freeze` → exact versions for reproducibility

---

### Save dependencies
```bash
pip freeze > requirements.txt
```

---

### Install from file
```bash
pip install -r requirements.txt
```

---

### Remove environment
```bash
rm -rf .venv
```

---

## 2. Poetry (project + dependency manager)

Manages:
- Virtual environments
- Dependencies
- Lockfiles for deterministic builds

---

### Create project
```bash
poetry new my_project
cd my_project
poetry install
```

For existing project:
```bash
poetry init
```

---

### Activate environment
```bash
poetry shell
```

Or run without activation:
```bash
poetry run python app.py
```

---

### Install dependencies
```bash
poetry add numpy pandas
```

Dev dependencies:
```bash
poetry add pytest --group dev
```

---

### List dependencies
```bash
poetry show
```

Tree view:
```bash
poetry show --tree
```

---

### Remove dependency
```bash
poetry remove pandas
```

---

### Export requirements
```bash
poetry export -f requirements.txt > requirements.txt
```

---

### Remove environment
```bash
poetry env list
poetry env remove python
```

Or:
```bash
poetry env remove <env-id>
```

---

## 3. uv (fast modern tooling)

Replaces:
- pip
- venv (workflow simplification)
- dependency resolution (high speed)

---

### Create environment
```bash
uv venv
```

---

### Activate environment
```bash
source .venv/bin/activate
```

---

### Install packages
```bash
uv pip install numpy pandas fastapi
```

From requirements:
```bash
uv pip install -r requirements.txt
```

---

### List packages
```bash
uv pip list
uv pip freeze
```

---

### Lock dependencies
```bash
uv pip compile requirements.in -o requirements.txt
```

---

### Remove package
```bash
uv pip uninstall pandas
```

---

### Remove environment
```bash
rm -rf .venv
```

---

## Tool Comparison

### venv
- Built-in standard tool
- Manual dependency management
- Maximum compatibility

### Poetry
- Full project management
- Lockfile-based reproducibility
- Strong for team development

### uv
- Extremely fast
- Modern pip/venv replacement
- CI/CD optimized

---

## Typical Workflows

### venv
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Poetry
```bash
poetry new model-service
cd model-service
poetry add fastapi torch
poetry run python app.py
```

### uv
```bash
uv venv
uv pip install fastapi torch
uv pip freeze > requirements.txt
```
