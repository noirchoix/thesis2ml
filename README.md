# Thesis2ML Chemistry

Chemistry-first workbench for converting dormant theses into practical ML, RAG, product, and commercialization roadmaps.

The app is built around specialist-agent orchestration rather than one large prompt:

1. Thesis extraction agent
2. Chemistry ML mapper
3. Product strategist
4. Research commercialization analyst

It uses a LightRAG-inspired pipeline at production-MVP scale: document extraction, paragraph-aware chunking, embeddings, hybrid vector/keyword retrieval, traceable context, and structured JSON outputs.

## AI stack

Generation:

- DeepSeek `deepseek-chat`
- Gemini `gemini-2.5-flash`

Embeddings:

- VoyageAI `voyage-3-large`
- Gemini `text-embedding-004`

If keys are missing, the backend falls back to local deterministic embeddings and heuristic JSON so the portfolio demo still runs.

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

