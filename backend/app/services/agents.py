import json
import uuid

from app.services.chemistry_knowledge import ALGORITHM_FAMILIES, CHEMISTRY_DATASET_CATEGORIES, chemistry_context_text
from app.services.documents import get_document, get_document_text
from app.services.llm import generate_json
from app.services.retrieval import retrieve
from app.services.store import db, utc_now
from app.settings import get_settings


SPECIALIST_SYSTEM = (
    "You are a specialist in a multi-agent thesis-to-ML analysis workflow. "
    "Return valid JSON only. Be concrete, evidence-aware, and avoid forcing commercialization "
    "when the thesis data does not support it."
)


def _context_from_chunks(chunks: list[dict]) -> str:
    settings = get_settings()
    context = "\n\n".join(
        f"[chunk {chunk['chunk_index']} score={chunk['score']}]\n{chunk['text']}" for chunk in chunks
    )
    return context[: settings.max_context_chars]


async def extraction_agent(thesis_context: str, query: str) -> dict:
    prompt = f"""
Specialist role: Thesis extraction agent.

Extract a structured research inventory from the thesis context.

Required JSON shape:
{{
  "field": "short field label",
  "research_question": "main research problem",
  "data_assets": ["data/table/measurement assets"],
  "variables": ["input/output variables"],
  "methods": ["experimental/theoretical/computational methods"],
  "findings": ["major findings"],
  "limitations": ["limitations"],
  "ml_readiness": "low|medium|high",
  "confidence": 0.0
}}

User intent: {query}

Thesis context:
{thesis_context}
"""
    return await generate_json("extraction", SPECIALIST_SYSTEM, prompt)


async def ml_mapper_agent(extraction: dict, thesis_context: str) -> dict:
    prompt = f"""
Specialist role: Chemistry ML mapper.

Use the chemistry dataset and algorithm catalogue below to map this thesis to practical ML tracks.
Do not invent unavailable raw data. Separate thesis-native data from public benchmark data.

Chemistry context:
{chemistry_context_text()}

Algorithm families:
{json.dumps(ALGORITHM_FAMILIES, indent=2)}

Extraction:
{json.dumps(extraction, indent=2)}

Thesis context:
{thesis_context}

Required JSON shape:
{{
  "recommended_tracks": [
    {{
      "track": "ML application track",
      "algorithms": ["specific algorithms"],
      "dataset_matches": ["specific public datasets"],
      "thesis_data_to_extract": ["needed thesis data"],
      "data_needed": ["missing data or labels"],
      "baseline_experiment": "first model experiment",
      "evaluation_metrics": ["metrics"],
      "risk": "technical risk"
    }}
  ],
  "feasibility_score": 0
}}
"""
    return await generate_json("ml_mapper", SPECIALIST_SYSTEM, prompt)


async def product_agent(extraction: dict, ml_plan: dict) -> dict:
    prompt = f"""
Specialist role: Product strategist.

Convert only feasible research/ML tracks into realistic product opportunities.
Favor narrow, buildable tools that could be used by students, labs, analysts, or small companies.

Extraction:
{json.dumps(extraction, indent=2)}

ML plan:
{json.dumps(ml_plan, indent=2)}

Required JSON shape:
{{
  "products": [
    {{
      "name": "product concept",
      "user": "specific user",
      "problem": "specific problem",
      "workflow": "how it works",
      "data_dependency": "what data is needed",
      "build_scope": "MVP scope",
      "monetization": "practical route",
      "portfolio_strength": "low|medium|high"
    }}
  ],
  "portfolio_angle": "how to present this project"
}}
"""
    return await generate_json("product", SPECIALIST_SYSTEM, prompt)


async def commercialization_agent(extraction: dict, ml_plan: dict, product_plan: dict) -> dict:
    prompt = f"""
Specialist role: Research commercialization analyst.

Assess routes to academic follow-up, service work, startup productization, and practical constraints.
Be especially realistic for under-resourced chemistry research environments.

Extraction:
{json.dumps(extraction, indent=2)}

ML plan:
{json.dumps(ml_plan, indent=2)}

Product plan:
{json.dumps(product_plan, indent=2)}

Required JSON shape:
{{
  "commercialization_paths": ["path"],
  "research_paths": ["path"],
  "next_steps": ["ordered next step"],
  "data_readiness_checklist": ["check"],
  "cautions": ["risk or blocker"]
}}
"""
    return await generate_json("commercialization", SPECIALIST_SYSTEM, prompt)


async def run_analysis(document_id: str, query: str, mode: str = "full") -> dict:
    document = get_document(document_id)
    if not document:
        raise ValueError("Document not found")

    retrieved, retrieval_trace = await retrieve(document_id, query)
    thesis_context = _context_from_chunks(retrieved)
    if not thesis_context:
        thesis_context = get_document_text(document_id)

    extraction = await extraction_agent(thesis_context, query)
    ml_plan = await ml_mapper_agent(extraction, thesis_context)
    product_plan = await product_agent(extraction, ml_plan)
    commercialization = await commercialization_agent(extraction, ml_plan, product_plan)

    result = {
        "document": document,
        "query": query,
        "orchestration": {
            "pattern": "sequential specialist handoff with parallel product/commercial preview",
            "agents": ["thesis_extractor", "chemistry_ml_mapper", "product_strategist", "commercialization_analyst"],
        },
        "extraction": extraction,
        "ml_plan": ml_plan,
        "product_strategy": product_plan,
        "commercialization": commercialization,
        "chemistry_datasets": CHEMISTRY_DATASET_CATEGORIES,
    }
    run_id = str(uuid.uuid4())
    trace = {"retrieval": retrieval_trace, "chunks": retrieved}
    with db() as conn:
        conn.execute(
            "insert into analysis_runs values (?, ?, ?, ?, ?, ?, ?)",
            (run_id, document_id, query, mode, json.dumps(result), json.dumps(trace), utc_now()),
        )
    return {"id": run_id, "result": result, "trace": trace}


def list_runs(document_id: str | None = None) -> list[dict]:
    sql = "select id, document_id, query, mode, result_json, trace_json, created_at from analysis_runs"
    params: tuple = ()
    if document_id:
        sql += " where document_id = ?"
        params = (document_id,)
    sql += " order by created_at desc"
    with db() as conn:
        rows = conn.execute(sql, params).fetchall()
    return [
        {
            "id": row["id"],
            "document_id": row["document_id"],
            "query": row["query"],
            "mode": row["mode"],
            "result": json.loads(row["result_json"]),
            "trace": json.loads(row["trace_json"]),
            "created_at": row["created_at"],
        }
        for row in rows
    ]
