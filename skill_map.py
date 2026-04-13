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
}

# Flat set of all canonical skill names — used for fast membership checks in preprocessor.
SKILL_KEYWORDS: set[str] = set(SKILL_CATEGORIES.keys())


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
