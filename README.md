# CMOSynthesis

CMOSynthesis is a tool for synthesizing static CMOS transistor networks (Pull-Up and Pull-Down networks) from boolean logic expressions. It parses boolean formulas, performs logic simplification (including NNF + factoring), and generates the corresponding transistor-level implementation plus JSON output for visualization.

## Features

- **Boolean Expression Parsing**: Supports standard operators and aliases (AND `&`/`*`/implicit/`AND`, OR `|`/`+`/`OR`, NOT `!`/`~`/`NOT`).
- **Constants & Variables**: Supports constants `0`/`1` and identifiers with letters, digits, and underscores.
- **Logic Simplification**: Applies algebraic rules including:
  - Constant folding
  - Identity and Annihilator laws
  - Complement logic
  - Factoring
- **NNF + Complement NNF**: Produces negation-normal form for the function and its complement.
- **CMOS Network Synthesis**:
  - Generates Pull-Down Networks (PDN) using NMOS transistors.
  - Generates Pull-Up Networks (PUN) using PMOS transistors.
  - Calculates transistor counts (including necessary inverters for inputs).
- **Visualization Data**: Exports network structure in JSON format suitable for graph visualization.
- **Debugging Utilities**: Includes a debug endpoint to compare NNF/complement NNF against truth tables or randomized checks.

## Project Structure

The project is organized into a backend logic engine and a frontend visualization layer.

```
CMOSynthesis/
├── bool2cmos/
│   ├── backend/
│   │   ├── api/                 # Synthesis pipeline and optional FastAPI router
│   │   ├── app.py               # FastAPI application
│   │   ├── constraints/         # Optional guardrails (e.g., transistor limit checks)
│   │   ├── graph/               # Network graph model + JSON export helpers
│   │   ├── logic/               # Logic transformation rules
│   │   ├── parser/              # Expression parsing and AST definitions
│   │   ├── synthesis/           # PDN/PUN construction algorithms
│   │   └── tests/               # Unit tests
│   └── frontend/                # React-based web interface
```

## Backend Usage

The core logic is implemented in Python. The primary entry point for synthesis is `bool2cmos.backend.api.synthesize`.

### Expression syntax

- **NOT**: `!A`, `~A`, or `NOT A`
- **AND**: `A&B`, `A*B`, `A AND B`, or implicit `AB`/`A(B+C)`/`A!B`
- **OR**: `A|B`, `A+B`, or `A OR B`
- **Constants**: `0`, `1`
- **Identifiers**: Alphanumeric/underscore tokens (`A`, `N1`, `foo_bar`). Pure alphabetic tokens longer than one character (e.g. `AB`) are treated as shorthand `A AND B`, so use digits/underscores if you need multi-character variable names (e.g. `A1` or `A_B`).

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
- `nnfComplement`: Negation Normal Form of the complement.
- `factor` / `factorComplement`: Factored NNF forms used for network synthesis.
- `pdn` / `pun`: The resulting transistor networks (Series/Parallel structures).
- `count`: Transistor usage statistics.

### Debug endpoint

`POST /debug/nnf` (or `/debug/complement-nnf`) returns NNF/complement-NNF inspections and, when the variable count is small, a full truth-table check. For larger expressions, it falls back to randomized sampling.

## Status

- **Backend**: Functional core logic with API endpoints for synthesis and NNF inspection.
- **Frontend**: React-based UI for visualization and experimentation.
