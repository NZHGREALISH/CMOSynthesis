# CMOSynthesis

Bool-to-CMOS synthesis demo with a Python (FastAPI) backend and a React frontend.

## Run

Backend:

- `python -m pip install -r bool2cmos/backend/requirements.txt`
- `uvicorn bool2cmos.backend.app:app --reload --port 8000`

Frontend:

- `cd bool2cmos/frontend`
- `npm install`
- `npm start`

Then open `http://localhost:3000`.

## API

- `POST /synthesize` with JSON body `{"expr": "A & (B | !C)"}`.
