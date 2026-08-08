# skill_map.py
# Canonical skill → category mapping.
# Edit this file to add new technologies or categories — no code changes needed.

SKILL_CATEGORIES: dict[str, list[str]] = {
    "react":             ["frontend", "javascript", "ui", "spa"],
    "next.js":           ["frontend", "javascript", "ssr", "spa"],
    "vue.js":            ["frontend", "javascript", "ui", "spa"],
    "angular":           ["frontend", "javascript", "ui", "spa"],
    "svelte":            ["frontend", "javascript", "ui"],
    "tailwind":          ["frontend", "css", "ui"],
    "typescript":        ["javascript", "frontend", "backend"],
    "javascript":        ["frontend", "backend", "scripting"],
    "node.js":           ["backend", "javascript", "api", "server"],
    "express":           ["backend", "javascript", "api", "server"],
    "fastapi":           ["backend", "python", "api"],
    "django":            ["backend", "python", "api"],
    "flask":             ["backend", "python", "api"],
    "spring":            ["backend", "java", "api"],
    "laravel":           ["backend", "php", "api"],
    "ruby-on-rails":     ["backend", "ruby", "api"],
    "python":            ["scripting", "backend", "data-science", "ml"],
    "java":              ["backend", "oop"],
    "go":                ["backend", "systems"],
    "rust":              ["systems", "backend"],
    "php":               ["backend", "scripting"],
    "ruby":              ["backend", "scripting"],
    "rest-api":          ["api", "backend", "http"],
    "graphql":           ["api", "backend"],
    "postgresql":        ["database", "sql", "relational"],
    "mysql":             ["database", "sql", "relational"],
    "sqlite":            ["database", "sql", "relational"],
    "mssql":             ["database", "sql", "relational"],
    "mongodb":           ["database", "nosql"],
    "redis":             ["database", "cache"],
    "elasticsearch":     ["database", "search"],
    "cassandra":         ["database", "nosql"],
    "machine-learning":  ["ml", "ai", "data-science"],
    "deep-learning":     ["ml", "ai", "neural-network"],
    "tensorflow":        ["ml", "python", "ai"],
    "pytorch":           ["ml", "python", "ai"],
    "scikit-learn":      ["ml", "python", "data-science"],
    "pandas":            ["data-science", "python"],
    "numpy":             ["data-science", "python", "ml"],
    "docker":            ["devops", "containerization"],
    "kubernetes":        ["devops", "containerization", "orchestration"],
    "aws":               ["cloud", "devops"],
    "gcp":               ["cloud", "devops"],
    "azure":             ["cloud", "devops"],
    "terraform":         ["devops", "iac"],
    "ansible":           ["devops", "iac"],
    "git":               ["vcs", "devops"],
    "linux":             ["systems", "devops"],
    "supabase":          ["backend", "database", "baas"],
    "firebase":          ["backend", "database", "baas"],

    # ── Non-technical roles (sales, marketing, business, HR, support) ────────
    "sales":                 ["sales"],
    "b2b":                   ["sales", "business-development"],
    "b2c":                   ["sales", "marketing"],
    "lead-generation":       ["sales", "business-development", "marketing"],
    "business-development":  ["sales", "business-development"],
    "account-management":    ["sales", "business-development", "client-relations"],
    "cold-calling":          ["sales", "outreach"],
    "negotiation":           ["sales", "soft-skill"],
    "crm":                   ["sales", "tools"],
    "salesforce":            ["sales", "crm", "tools"],
    "hubspot":               ["sales", "marketing", "crm", "tools"],
    "digital-marketing":     ["marketing"],
    "seo":                   ["marketing"],
    "content-marketing":     ["marketing", "content"],
    "social-media-marketing": ["marketing"],
    "email-marketing":       ["marketing", "outreach"],
    "market-research":       ["marketing", "sales"],
    "copywriting":           ["marketing", "content"],
    "customer-service":      ["support", "communication"],
    "customer-support":      ["support", "communication"],
    "communication":         ["soft-skill", "communication"],
    "project-management":    ["management", "soft-skill"],
    "recruitment":           ["hr"],
    "human-resources":       ["hr"],
    "accounting":            ["finance"],
    "bookkeeping":           ["finance"],
    "financial-analysis":    ["finance"],
}

# Flat set of all canonical skill names — used for fast membership checks in preprocessor.
SKILL_KEYWORDS: set[str] = set(SKILL_CATEGORIES.keys())

# Flat set of all category tags — lets preprocessor recognise category-level
# words mentioned directly in text (e.g. a JD saying "frontend developer"
# with no specific tech keyword), not just skills that expand into them.
ALL_CATEGORIES: set[str] = {tag for tags in SKILL_CATEGORIES.values() for tag in tags}


def expand_skills(skills: set[str]) -> set[str]:
    """
    Return the union of all category tags for the given skill set.

    Example:
        expand_skills({"react", "node.js"})
        → {"frontend", "javascript", "ui", "spa", "backend", "api", "server"}
    """
    categories: set[str] = set()
    for skill in skills:
        categories.update(SKILL_CATEGORIES.get(skill, []))
    return categories
