# text_cleaner.py
# Normalize resume and job description text before NLP processing.
# All functions are pure — they take a string and return a string.
# Call clean() as the single public entry point.

import re


# ── Alias normalization ───────────────────────────────────────────────────────
# Maps variant spellings to canonical forms recognised by skill_map.SKILL_KEYWORDS.
# Order matters: more specific patterns must come before broader ones.

_ALIAS_PATTERNS: list[tuple[str, str]] = [
    # JavaScript frameworks
    (r"\breactjs\b",                  "react"),
    (r"\bnext[\s\-]?js\b",            "next.js"),
    (r"\bnextjs\b",                   "next.js"),
    (r"\bvue[\s\-]?js\b",             "vue.js"),
    (r"\bvuejs\b",                    "vue.js"),
    (r"\bangularjs\b",                "angular"),
    # Node / Express
    (r"\bnode[\s\-]?js\b",            "node.js"),
    (r"\bnodejs\b",                   "node.js"),
    (r"\bexpress[\s\-]?js\b",         "express"),
    # Databases
    (r"\bpostgres(?:ql)?\b",          "postgresql"),
    (r"\bms[\s\-]?sql\b",             "mssql"),
    (r"\bsql[\s\-]?server\b",         "mssql"),
    # ML / data
    (r"\bscikit[\s\-]learn\b",        "scikit-learn"),
    (r"\bsklearn\b",                  "scikit-learn"),
    (r"\bmachine[\s\-]learning\b",    "machine-learning"),
    (r"\bdeep[\s\-]learning\b",       "deep-learning"),
    # APIs
    (r"\brestful?\s*api[s]?\b",       "rest-api"),
    (r"\brest\s*api[s]?\b",           "rest-api"),
    # Ruby on Rails
    (r"\bruby[\s\-]on[\s\-]rails\b",  "ruby-on-rails"),
    (r"\brails\b",                    "ruby-on-rails"),
    # Other
    (r"\btailwindcss\b",              "tailwind"),
    (r"\btailwind[\s\-]css\b",        "tailwind"),
    (r"\bts\b",                       "typescript"),
    (r"\bjs\b",                       "javascript"),
]

# Pre-compile all patterns once at module load for speed.
_COMPILED_ALIASES: list[tuple[re.Pattern, str]] = [
    (re.compile(pattern, re.IGNORECASE), replacement)
    for pattern, replacement in _ALIAS_PATTERNS
]


# ── Pipeline steps ────────────────────────────────────────────────────────────

def _normalize_casing(text: str) -> str:
    return text.lower()


def _normalize_skill_spellings(text: str) -> str:
    for pattern, replacement in _COMPILED_ALIASES:
        text = pattern.sub(replacement, text)
    return text


def _collapse_whitespace(text: str) -> str:
    # Normalize tabs and carriage returns to spaces.
    text = re.sub(r"[\t\r]+", " ", text)
    # Collapse multiple spaces to one.
    text = re.sub(r" {2,}", " ", text)
    # Collapse 3+ consecutive newlines to two (preserve paragraph breaks).
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _strip_noisy_chars(text: str) -> str:
    # Remove non-printable / control characters.
    text = re.sub(r"[^\x20-\x7E\n]", " ", text)
    # Remove repetitive punctuation clusters (e.g. ====, ----, ****).
    text = re.sub(r"([=\-*#_|~])\1{2,}", " ", text)
    # Keep only safe characters; preserve . so node.js / next.js survive.
    text = re.sub(r"[^\w\s.,;:()\-\/\.]", " ", text)
    # Clean up any double-spaces introduced above.
    text = re.sub(r" {2,}", " ", text)
    return text.strip()


def _remove_duplicate_sentences(text: str) -> str:
    # Split on common sentence / line boundaries.
    parts = re.split(r"(?<=[.!?\n])\s*", text)
    seen: set[str] = set()
    unique: list[str] = []
    for part in parts:
        key = part.strip().lower()
        if key and key not in seen:
            seen.add(key)
            unique.append(part)
    return " ".join(unique)


# ── Public entry point ────────────────────────────────────────────────────────

def clean(text: str) -> str:
    """
    Normalize a resume or job description for NLP processing.

    Pipeline:
        1. Lowercase
        2. Normalize skill alias spellings  (reactjs → react, node js → node.js)
        3. Collapse whitespace
        4. Strip noisy / non-printable characters
        5. Remove duplicate sentences

    Returns the cleaned string.  The original text is never mutated.
    """
    if not text:
        return ""
    text = _normalize_casing(text)
    text = _normalize_skill_spellings(text)
    text = _collapse_whitespace(text)
    text = _strip_noisy_chars(text)
    text = _remove_duplicate_sentences(text)
    return text
