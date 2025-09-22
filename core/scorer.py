# core/scorer.py
import json
import os
from typing import Dict, Any, List

from openai import OpenAI

_OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

_SYSTEM = """You are JobScoutAI, a career assistant for a mid-senior UX/Service Designer
who values social impact, wellbeing, accessibility, and positive work culture.

Return ONLY compact JSON with this shape:
{
  "score_total": <0-100>,
  "reasons": [string, ...],
  "red_flags": [string, ...],
  "must_ask": [string, ...]
}

Guidance:
- Prioritize roles in UX design, service design, product design, or strategy.
- Give extra weight to roles mentioning social impact, wellbeing, accessibility,
  ethical tech, or community benefit.
- Down-rank jobs that are pure sales, commission-only, engineering-only, or irrelevant.
- Flag red flags like vague pay, exploitative terms, unpaid internships, or toxic clues.
- Suggest 1–3 sharp interview questions under "must_ask" (e.g., team culture, scope,
  impact alignment).
"""


def _job_to_text(job: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append(f"Title: {job.get('title')}")
    lines.append(f"Company: {job.get('company')}")
    lines.append(f"Source: {job.get('source')}")
    lines.append(f"Location: {job.get('location')}")
    lines.append(f"Remote: {job.get('remote')}")
    lines.append(f"Link: {job.get('link')}")
    desc = job.get("description") or ""
    if len(desc) > 2000:
        desc = desc[:2000] + "..."
    lines.append(f"Description:\n{desc}")
    return "\n".join(lines)

def score_job(job: Dict[str, Any]) -> Dict[str, Any]:
    """
    Returns:
      {
        "score_total": int,
        "reasons": [str],
        "red_flags": [str],
        "must_ask": [str]
      }
    On failure, returns empty fields and puts the error message under 'error'.
    """
    try:
        user_prompt = (
            "Score this job for alignment with general values "
            "(work-life balance, positive impact, healthy culture). "
            "Only return JSON as described.\n\n"
            + _job_to_text(job)
        )

        resp = _client.chat.completions.create(
            model=_OPENAI_MODEL,
            temperature=0.2,
            messages=[
                {"role": "system", "content": _SYSTEM},
                {"role": "user", "content": user_prompt},
            ],
        )

        content = resp.choices[0].message.content.strip()
        # The model should return pure JSON. Try to parse; if it fails,
        # try to extract a JSON object heuristically.
        try:
            data = json.loads(content)
        except Exception:
            # simple fallback: find the first {...} block
            start = content.find("{")
            end = content.rfind("}")
            if start != -1 and end != -1 and end > start:
                data = json.loads(content[start:end+1])
            else:
                raise

        # Normalize fields
        out = {
            "score_total": int(data.get("score_total", 0)),
            "reasons": list(data.get("reasons", [])),
            "red_flags": list(data.get("red_flags", [])),
            "must_ask": list(data.get("must_ask", [])),
        }
        # Clamp score
        out["score_total"] = max(0, min(100, out["score_total"]))
        return out

    except Exception as e:
        return {
            "score_total": 0,
            "reasons": [],
            "red_flags": [],
            "must_ask": [],
            "error": f"{type(e).__name__}: {e}",
        }
