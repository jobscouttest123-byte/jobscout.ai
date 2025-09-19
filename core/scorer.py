import os, json
from openai import OpenAI

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5-mini")
_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", "sk-test-noop"))

VALUES_PROFILE = {
    "non_negotiables": [
        "honesty","integrity","respect","responsibility","authenticity","non-judgmental"
    ],
    "positives": [
        "social impact","community wellbeing","accessibility","sustainable workloads",
        "evidence-based","transparency","inclusion"
    ]
}

SYSTEM_PROMPT = (
    "You are an assistant that scores job ads against a candidate's values. "
    "Be practical and concise. Output STRICT JSON that matches the schema."
)

def _build_user_prompt(job):
    job_json = json.dumps(job, ensure_ascii=False)
    values_json = json.dumps(VALUES_PROFILE, ensure_ascii=False)
    return f"""Score the following job ad for values alignment.
Return JSON with:
{{
 "score_total": 0-5,
 "scores": {{"integrity":0-5,"impact":0-5,"culture":0-5,"fit":0-5,"health_safeguards":0-5}},
 "reasons": ["short bullets"],
 "red_flags": ["short bullets"],
 "must_ask": ["short interview questions to verify values"]
}}

Candidate values: {values_json}

Job: {job_json}
"""

def score_job(job):
    try:
        rsp = _client.responses.create(
            model=OPENAI_MODEL,
            input=[
                {"role":"system","content": SYSTEM_PROMPT},
                {"role":"user","content": _build_user_prompt(job)}
            ],
            temperature=0.1,
            max_output_tokens=350,
            response_format={"type":"json_object"}
        )
        data = json.loads(rsp.output_text)
        data.setdefault("score_total", 0)
        data.setdefault("reasons", [])
        data.setdefault("red_flags", [])
        data.setdefault("must_ask", [])
        return data
    except Exception as e:
        return {"score_total": 0, "reasons": [f"scorer_error: {e}"], "red_flags": [], "must_ask": []}
