# CMOSynthesis

CMOSynthesis is a tool for synthesizing static CMOS transistor networks (Pull-Up and Pull-Down networks) from boolean logic expressions. It parses boolean formulas, performs logic simplification, and generates the corresponding transistor-level implementation.

## Features

- **Boolean Expression Parsing**: Supports standard boolean operators (AND `&`, OR `|`, NOT `!`).
- **Logic Simplification**: Applies algebraic rules including:
  - Constant folding
  - Identity and Annihilator laws
  - Complement logic
  - Factoring
- **CMOS Network Synthesis**:
  - Generates Pull-Down Networks (PDN) using NMOS transistors.
  - Generates Pull-Up Networks (PUN) using PMOS transistors.
  - Calculates transistor counts (including necessary inverters for inputs).
- **Visualization Data**: Exports network structure in JSON format suitable for graph visualization.

## Project Structure

The project is organized into a backend logic engine and a frontend visualization layer.

```
CMOSynthesis/
├── bool2cmos/
│   ├── backend/
│   │   ├── api/
│   │   │   └── synthesize.py    # Main synthesis pipeline and API entry point
│   │   ├── logic/               # Logic transformation rules
│   │   ├── parser/              # Expression parsing and AST definitions
│   │   ├── synthesis/           # PDN/PUN construction algorithms
│   │   └── tests/               # Unit tests
│   └── frontend/                # React-based web interface (Work in Progress)
```

## Backend Usage

The core logic is implemented in Python. The primary entry point for synthesis is `bool2cmos.backend.api.synthesize`.

### Dependencies

The backend logic requires Python 3.7+. 
Optional dependencies for the API server:
- `fastapi`
- `pydantic`

## Development (Backend + Frontend)

### One command

```bash
bash scripts/dev.sh
```

- Backend: `http://localhost:8000` (health: `GET /health`, API: `POST /synthesize`)
- Frontend: `http://localhost:3000` (proxy -> `http://localhost:8000`)

Environment variables:
- `BACKEND_PORT` (default: `8000`)
- `NO_VENV=1` to disable the auto-created `.venv/`

### Manual (as-is)

Backend:
```bash
python -m pip install -r bool2cmos/backend/requirements.txt
uvicorn bool2cmos.backend.app:app --reload --port 8000
```

Frontend:
```bash
cd bool2cmos/frontend && npm install && npm start
```

### Example

```python
from bool2cmos.backend.api.synthesize import synthesize

# Synthesize a simple expression
result = synthesize("A & (B | C)")

# Access the results
print("Simplified Expression:", result["steps"]["simplify"]["expr"])
print("Total Transistors:", result["steps"]["count"]["totalTransistors"])
print("PDN Network:", result["steps"]["pdn"]["network"])
```

### API Response Structure

The `synthesize` function returns a dictionary containing details about each step of the process:

- `parse`: The parsed expression.
- `simplify`: The simplified version of the expression.
- `nnf`: Negation Normal Form.
- `pdn` / `pun`: The resulting transistor networks (Series/Parallel structures).
- `count`: Transistor usage statistics.

## Status

- **Backend**: Functional core logic with dual implementations (monolithic and modular).
- **Frontend**: Structure initialized, currently under development.

## Notes / Caveats

- `bool2cmos/docs/*` are currently empty placeholders.
- The backend currently has two parallel implementations (`bool2cmos/backend/api/synthesize.py` vs `bool2cmos/backend/{parser,logic,synthesis,...}`) and the JSON schema is not unified; the frontend uses the `api/synthesize.py` schema (and maps it into its internal network types).
