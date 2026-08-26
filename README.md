# Thesis2ML Chemistry Workbench

A chemistry-focused document-to-opportunity workbench that persists theses and chunk embeddings, combines vector and lexical retrieval, and orchestrates sequential specialist stages for thesis extraction, chemistry/ML mapping, product strategy, and commercialization. Provider fallbacks preserve deterministic function when external models are unavailable.

## Engineering profile

This repository demonstrates:

- SQLite persistence for documents, chunks, embeddings, and analysis runs
- Paragraph-aware chunking with overlap
- Voyage embeddings with Gemini fallback and deterministic hash fallback
- Hybrid retrieval combining cosine-vector and keyword scores with traceable components
- Sequential specialist-agent stages with structured JSON contracts
- Deterministic heuristic fallbacks on provider failure
- Explicit distinction between thesis-native evidence and public benchmark context
- FastAPI + SvelteKit domain workbench

## Reliability and scope

This is a strong orchestration/retrieval/domain-product system.

## Run backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

On Windows PowerShell:

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

## Run frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Open `http://localhost:5173`.

## Supported uploads

- PDF
- TXT
- MD

## API

- `GET /health`
- `GET /v1/chemistry/datasets`
- `POST /v1/documents/upload`
- `GET /v1/documents`
- `GET /v1/documents/{document_id}`
- `POST /v1/query`
- `POST /v1/analyze`
- `GET /v1/runs`

## Portfolio positioning

This is not a generic thesis summarizer. It is a chemistry-specific applied AI workbench for:

- extracting research assets from theses
- matching those assets to realistic public chemistry datasets
- planning baseline ML experiments
- proposing buildable science products
- identifying commercialization paths and blockers
