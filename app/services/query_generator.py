"""Query Generator — builds a prioritized list of search queries for a given company + designation.

Strategy:
1. Primary queries  — direct, high-signal (LinkedIn, company name + role)
2. Website queries  — company's own site about/team/leadership pages
3. Alias queries    — alternate forms of the designation (CEO ↔ Chief Executive Officer)
4. Discovery queries— news, press, Crunchbase, ZoomInfo, Glassdoor
"""

from typing import List


def generate_queries(company: str, designation: str) -> List[str]:
    """Return a flat, priority-ordered list of search queries."""
    c = company.strip()
    d = designation.strip()

    aliases   = _get_aliases(d)
    alt_forms = aliases if aliases else []   # alternate designation forms

    # Company slug for site: queries
    company_slug = c.lower().replace(" ", "").replace(",", "").replace(".", "").replace("-", "")

    # ── PRIMARY (highest signal) ─────────────────────────────────────────
    primary = [
        f'"{c}" {d}',                          # exact company + designation
        f"{d} {c}",                            # simple order
        f"{d} at {c}",
        f"{d} of {c}",
        f"{c} {d} LinkedIn",
        f'site:linkedin.com/in "{c}" {d}',
        f'site:linkedin.com "{c}" {d}',
    ]

    # Add alias versions of primary queries
    alias_primary = []
    for alt in alt_forms:
        alias_primary += [
            f'"{c}" {alt}',
            f"{alt} at {c}",
            f"{c} {alt} LinkedIn",
            f'site:linkedin.com/in "{c}" {alt}',
        ]

    # ── COMPANY WEBSITE ──────────────────────────────────────────────────
    website_queries = [
        f'site:{company_slug}.com {d}',
        f'site:{company_slug}.com {alt_forms[0]}' if alt_forms else f'site:{company_slug}.com leadership',
        f'"{c}" about us team leadership {d}',
        f'"{c}" leadership team',
        f'"{c}" management team',
        f'"{c}" our team {d}',
        f'"{c}" meet the team',
    ]

    # ── DISCOVERY / NEWS ─────────────────────────────────────────────────
    discovery = [
        f'site:crunchbase.com/organization "{c}"',
        f'site:zoominfo.com "{c}" {d}',
        f'site:glassdoor.com "{c}" {d}',
        f'"{c}" press release {d}',
        f'"{c}" interview {d}',
        f'"{c}" appointed {d}',
        f'"{c}" named {d}',
        f'"{c}" announces {d}',
        f'who is the {d} of {c}',
        f'who is {d} at {c}',
        f"{c} executive team",
        f"{c} {d} profile",
        f'"{c}" founder CEO',
    ]

    # Add alias versions of discovery
    alias_discovery = []
    for alt in alt_forms:
        alias_discovery += [
            f'"{c}" {alt}',
            f'who is the {alt} of {c}',
            f'"{c}" appointed {alt}',
        ]

    return primary + alias_primary + website_queries + discovery + alias_discovery


def _get_aliases(designation: str) -> List[str]:
    """Return common alternate forms of a designation (abbreviation ↔ full title)."""
    d = designation.strip().lower()
    mapping = {
        "chief executive officer": ["CEO"],
        "ceo":                     ["Chief Executive Officer", "Chief Exec"],
        "chief financial officer":  ["CFO"],
        "cfo":                     ["Chief Financial Officer"],
        "chief technology officer": ["CTO"],
        "cto":                     ["Chief Technology Officer", "Chief Technical Officer"],
        "chief operating officer":  ["COO"],
        "coo":                     ["Chief Operating Officer"],
        "chief marketing officer":  ["CMO"],
        "cmo":                     ["Chief Marketing Officer"],
        "chief product officer":    ["CPO"],
        "cpo":                     ["Chief Product Officer"],
        "managing director":        ["MD"],
        "md":                      ["Managing Director"],
        "vp":                      ["Vice President"],
        "vice president":           ["VP"],
        "svp":                     ["Senior Vice President"],
        "evp":                     ["Executive Vice President"],
        "president":               ["President & CEO", "President and CEO"],
        "founder":                 ["Co-Founder", "Founder & CEO", "CEO"],
        "co-founder":              ["Founder", "Cofounder"],
        "director":                ["Executive Director"],
        "ciso":                    ["Chief Information Security Officer"],
        "chief information security officer": ["CISO"],
        "cdo":                     ["Chief Digital Officer", "Chief Data Officer"],
        "general manager":         ["GM"],
        "gm":                      ["General Manager"],
    }
    for key, values in mapping.items():
        if d == key:
            return values
    return []
