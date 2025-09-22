import os
import json
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def score_job(job: dict) -> dict:
    """
    Ask the LLM to score a job against user values and return structured JSON.
    """

    prompt = f"""
You are JobScoutAI. Analyse this job and return structured JSON.

Job:
Title: {job.get("title")}
Company: {job.get("company")}
Location: {job.get("location")}
Country: {job.get("country")}
Remote: {job.get("remote")}
Employment type: {job.get("employment_type")}
Salary text: {job.get("salary_text")}
Link: {job.get("link")}
Description: {job.get("description")}

Return JSON with fields:
- score_total (0–100)
- reasons (list of strings: why it aligns with values)
- red_flags (list of strings)
- must_ask (list of interview questions)
"""

    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        content = resp.choices[0].message.content
        return json.loads(content)

    except Exception as e:
        print(f"[scorer] error: {e}")
        # Safe fallback so the pipeline doesn’t crash
        return {
            "score_total": 0,
            "reasons": [f"scorer_error: {e}"],
            "red_flags": [],
            "must_ask": []
        }
