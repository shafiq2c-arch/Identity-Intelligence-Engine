"""LLM Processor — calls Groq API to extract person name from a search result."""

import os
import json
import logging
import re
from typing import Dict, Optional

from groq import Groq
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

_client = Groq(api_key=os.getenv("GROK_API_KEY", ""))

# Primary model with fallback
_MODELS = [
    "llama-3.3-70b-versatile",
    "llama3-70b-8192",
]

_SYSTEM_PROMPT = """You are a precise information extraction assistant specializing in identifying company executives.

When given a search result (title, snippet, URL) along with a company name and designation,
extract the FULL NAME of the person currently holding that designation at that company.

IMPORTANT DESIGNATION MATCHING RULES:
- "CEO" and "Chief Executive Officer" are the SAME role — treat them as a match.
- "CTO" and "Chief Technology Officer" are the SAME role.
- "CFO" and "Chief Financial Officer" are the SAME role.
- "COO" and "Chief Operating Officer" are the SAME role.
- "MD" and "Managing Director" are the SAME role.
- "Founder" / "Co-Founder" / "Founder & CEO" are all related founder roles.
- If the snippet mentions any equivalent form of the designation, set designation_match to true.

IMPORTANT COMPANY MATCHING RULES:
- Ignore capitalization differences: "purelogics" = "PureLogics" = "Pure Logics".
- Ignore common suffixes: "PureLogics Ltd" = "PureLogics".
- If the company is clearly referenced (even spelled slightly differently), set company_match to true.

You MUST respond with a valid JSON object — no markdown, no extra text — in this exact format:
{
  "name": "<Full Name or 'Unknown'>",
  "company_match": true or false,
  "designation_match": true or false,
  "current_role": true or false,
  "reasoning": "<one sentence>"
}

Rules:
- If the snippet refers to a FORMER or EX holder, set current_role to false.
- If you cannot find a clear name, set name to "Unknown".
- Be GENEROUS in matching — if there's a reasonable chance the person holds this role, extract the name.
- Do NOT set name to "Unknown" just because you're slightly unsure. If a name appears in context with the company and a leadership role, extract it.
- company_match = true if the result is clearly about the specified company (flexible matching).
- designation_match = true if any equivalent form of the specified designation is mentioned.
"""


def _build_user_prompt(title: str, snippet: str, url: str, company: str, designation: str) -> str:
    return f"""Find the current {designation} of {company}.

Company: {company}
Designation: {designation}

Search Result:
Title: {title}
Snippet: {snippet}
URL: {url}

Note: "{designation}" may appear as an abbreviation or expanded form (e.g., CEO = Chief Executive Officer).
If this result clearly identifies a person at {company} in a leadership/executive role matching "{designation}",
extract their name even if the wording is not identical.

Return ONLY the JSON object as described."""


def _parse_response(text: str) -> Optional[Dict]:
    """Extract JSON from LLM response, even if wrapped in markdown."""
    text = re.sub(r"```(?:json)?", "", text).strip().strip("`").strip()
    try:
        data = json.loads(text)
        return {
            "name":               str(data.get("name", "Unknown")).strip(),
            "company_match":      bool(data.get("company_match", False)),
            "designation_match":  bool(data.get("designation_match", False)),
            "current_role":       bool(data.get("current_role", False)),
            "reasoning":          str(data.get("reasoning", "")),
        }
    except (json.JSONDecodeError, Exception):
        return None


def process_result(
    title: str,
    snippet: str,
    url: str,
    company: str,
    designation: str,
) -> Optional[Dict]:
    """
    Call LLM and return parsed extraction dict.
    Returns None if all models fail or response is unparseable.
    """
    user_prompt = _build_user_prompt(title, snippet, url, company, designation)

    for model in _MODELS:
        try:
            response = _client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {"role": "user",   "content": user_prompt},
                ],
                temperature=0.1,
                max_tokens=400,
            )
            raw = response.choices[0].message.content or ""
            result = _parse_response(raw)
            if result:
                return result
        except Exception as exc:
            logger.warning(f"LLM Model {model} failed: {exc}")
            continue

    return None
