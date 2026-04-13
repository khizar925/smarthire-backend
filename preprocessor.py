# preprocessor.py
# Extract structured skill signals from cleaned resume / job description text.

import re

from text_cleaner import clean
from skill_map import SKILL_KEYWORDS, expand_skills


def extract_skills(text: str) -> set[str]:
    """
    Extract canonical skill names from already-cleaned text.

    Tokenises the text into unigrams and bigrams, then intersects with
    SKILL_KEYWORDS (the canonical keys in skill_map.SKILL_CATEGORIES).

    Returns a set[str] of matched canonical skill names.
    """
    # Capture tokens that may contain internal dots (e.g. node.js, next.js).
    tokens: list[str] = re.findall(r"\b[\w][\w.]*\b", text)

    # Build bigrams to catch multi-word skills such as "machine-learning"
    # (already normalised to hyphenated form by text_cleaner).
    bigrams: list[str] = [
        f"{tokens[i]}-{tokens[i + 1]}"
        for i in range(len(tokens) - 1)
    ]

    candidates: set[str] = set(tokens) | set(bigrams)
    return candidates & SKILL_KEYWORDS


def extract_skill_set(raw_text: str) -> tuple[set[str], set[str]]:
    """
    Full pipeline: clean raw text → extract exact skills → expand to categories.

    Returns:
        exact_skills   — canonical skill names found in the text
        category_tags  — union of all category tags for those skills
                         (e.g. {"react"} → {"frontend", "javascript", "ui", "spa"})
    """
    cleaned = clean(raw_text)
    exact_skills = extract_skills(cleaned)
    category_tags = expand_skills(exact_skills)
    return exact_skills, category_tags
