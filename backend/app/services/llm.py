import json
import re
from typing import Any

import httpx

from app.settings import get_settings


def _extract_json(text: str) -> dict[str, Any]:
    try:
        return json.loads(text)
    except Exception:
        pass

    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except Exception:
            pass
    raise ValueError("Model did not return valid JSON")


def heuristic_json(agent_name: str, source: str) -> dict[str, Any]:
    lowered = source.lower()
    is_spectroscopy = any(term in lowered for term in ["spectroscopy", "ftir", "uv", "nmr", "raman", "chromatography"])
    is_bio = any(term in lowered for term in ["bioactivity", "toxicity", "inhibitor", "antimicrobial", "drug", "protein"])
    is_material = any(term in lowered for term in ["crystal", "polymer", "mof", "catalyst", "adsorption", "material"])

    if agent_name == "extraction":
        return {
            "field": "chemistry/materials science",
            "research_question": "Identify practical ML applications from the uploaded thesis.",
            "data_assets": ["tables", "experimental measurements", "method descriptions", "literature context"],
            "variables": ["composition", "conditions", "measured property", "performance outcome"],
            "methods": ["literature review", "experimental design", "chemical characterization"],
            "limitations": ["data may be small", "raw tables may need cleaning", "external validation required"],
            "confidence": 0.62,
        }
    if agent_name == "ml_mapper":
        family = "Spectroscopy and analytical chemistry ML" if is_spectroscopy else "QSAR and molecular property prediction" if is_bio else "Materials property prediction" if is_material else "Literature RAG and scientific extraction"
        return {
            "recommended_tracks": [
                {
                    "track": family,
                    "algorithms": ["gradient boosting", "random forest", "graph neural network", "RAG extraction"],
                    "dataset_matches": ["MoleculeNet", "ChEMBL", "Materials Project", "BigSolDB"],
                    "data_needed": ["clean tabular labels", "chemical identifiers", "train/test split", "baseline metrics"],
                    "risk": "Medium: thesis data likely needs normalization and external benchmark alignment.",
                }
            ],
            "feasibility_score": 74,
        }
    if agent_name == "product":
        return {
            "products": [
                {
                    "name": "Chemistry Thesis-to-Model Planner",
                    "user": "graduate researchers and supervisors",
                    "workflow": "upload thesis, extract datasets, recommend ML tracks, generate implementation roadmap",
                    "monetization": "paid thesis review package, university lab subscription, consulting upsell",
                    "build_scope": "RAG extraction, dataset matching, notebook generator, report export",
                }
            ],
            "portfolio_angle": "A science-first AI workbench that converts dormant research into practical ML roadmaps.",
        }
    return {
        "commercialization_paths": [
            "research assistant service for postgraduate students",
            "lab data readiness audit",
            "custom ML prototype package",
        ],
        "next_steps": [
            "digitize and clean thesis tables",
            "select one measurable target variable",
            "run baseline models before advanced AI",
            "validate against public chemistry datasets",
        ],
        "cautions": ["Do not force productization where data quality or market need is weak."],
    }


async def generate_json(agent_name: str, system: str, user: str) -> dict[str, Any]:
    settings = get_settings()
    providers = [settings.generation_provider, settings.fallback_generation_provider]
    for provider in providers:
        try:
            if provider == "deepseek" and settings.deepseek_api_key:
                async with httpx.AsyncClient(timeout=90) as client:
                    response = await client.post(
                        f"{settings.deepseek_base_url.rstrip('/')}/chat/completions",
                        headers={"Authorization": f"Bearer {settings.deepseek_api_key}"},
                        json={
                            "model": settings.deepseek_model,
                            "messages": [
                                {"role": "system", "content": system},
                                {"role": "user", "content": user},
                            ],
                            "temperature": 0.2,
                            "response_format": {"type": "json_object"},
                        },
                    )
                    response.raise_for_status()
                    return _extract_json(response.json()["choices"][0]["message"]["content"])
            if provider == "gemini" and settings.gemini_api_key:
                url = (
                    "https://generativelanguage.googleapis.com/v1beta/models/"
                    f"{settings.gemini_generation_model}:generateContent?key={settings.gemini_api_key}"
                )
                prompt = f"{system}\n\nReturn only JSON.\n\n{user}"
                async with httpx.AsyncClient(timeout=90) as client:
                    response = await client.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
                    response.raise_for_status()
                    text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
                    return _extract_json(text)
        except Exception:
            continue
    return heuristic_json(agent_name, user)
