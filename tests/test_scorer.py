# tests/test_scorer.py
# Run with: pytest tests/ -v
# Requires the smarthire-backend venv to be active.

import sys
import os

# Ensure the project root is on the path so imports resolve.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from text_cleaner import clean
from preprocessor import extract_skills, extract_skill_set
from skill_map import expand_skills


# ── text_cleaner ──────────────────────────────────────────────────────────────

class TestTextCleaner:
    def test_normalizes_reactjs(self):
        assert "react" in clean("ReactJS developer with 3 years experience")

    def test_normalizes_nodejs_with_space(self):
        assert "node.js" in clean("Strong node js background")

    def test_normalizes_nodejs_no_space(self):
        assert "node.js" in clean("nodejs experience required")

    def test_normalizes_nextjs(self):
        assert "next.js" in clean("Built with NextJS and Vercel")

    def test_normalizes_postgresql(self):
        assert "postgresql" in clean("Postgres database schema design")

    def test_normalizes_scikit_learn(self):
        assert "scikit-learn" in clean("Used scikit learn for model training")

    def test_normalizes_machine_learning(self):
        assert "machine-learning" in clean("machine learning engineer")

    def test_collapses_whitespace(self):
        result = clean("a  b\t\tc   d")
        assert "  " not in result
        assert "\t" not in result

    def test_strips_noisy_punctuation(self):
        result = clean("====Experience====\nFastAPI developer")
        assert "====" not in result
        assert "fastapi" in result

    def test_removes_duplicate_sentences(self):
        repeated = "Python developer. Python developer. FastAPI expert."
        result = clean(repeated)
        # "python developer" should appear only once
        assert result.count("python developer") == 1

    def test_empty_string_returns_empty(self):
        assert clean("") == ""

    def test_none_like_empty(self):
        # preprocessor passes "" for None resume_text; test clean("") stays ""
        assert clean("") == ""


# ── skill extraction ──────────────────────────────────────────────────────────

class TestExtractSkills:
    def test_finds_react(self):
        skills = extract_skills(clean("looking for a react developer"))
        assert "react" in skills

    def test_finds_node_js(self):
        skills = extract_skills(clean("node.js backend experience required"))
        assert "node.js" in skills

    def test_finds_postgresql(self):
        skills = extract_skills(clean("postgresql database design"))
        assert "postgresql" in skills

    def test_finds_fastapi(self):
        skills = extract_skills(clean("built rest apis with fastapi"))
        assert "fastapi" in skills

    def test_finds_machine_learning_bigram(self):
        # "machine-learning" is a hyphenated bigram after cleaning
        skills = extract_skills(clean("machine learning pipeline"))
        assert "machine-learning" in skills

    def test_finds_scikit_learn(self):
        skills = extract_skills(clean("scikit-learn and pandas"))
        assert "scikit-learn" in skills

    def test_returns_set(self):
        result = extract_skills(clean("react node.js postgresql"))
        assert isinstance(result, set)

    def test_empty_text_returns_empty_set(self):
        assert extract_skills("") == set()

    def test_unknown_skills_not_returned(self):
        skills = extract_skills(clean("excellent communication skills and leadership"))
        # None of these map to SKILL_KEYWORDS
        assert "communication" not in skills
        assert "leadership" not in skills


# ── skill expansion ───────────────────────────────────────────────────────────

class TestExpandSkills:
    def test_react_expands_to_frontend(self):
        cats = expand_skills({"react"})
        assert "frontend" in cats
        assert "javascript" in cats

    def test_node_expands_to_backend(self):
        cats = expand_skills({"node.js"})
        assert "backend" in cats
        assert "api" in cats

    def test_fastapi_expands_to_python_and_backend(self):
        cats = expand_skills({"fastapi"})
        assert "python" in cats
        assert "backend" in cats

    def test_postgresql_expands_to_database(self):
        cats = expand_skills({"postgresql"})
        assert "database" in cats
        assert "sql" in cats

    def test_multiple_skills_union(self):
        cats = expand_skills({"react", "django"})
        assert "frontend" in cats   # from react
        assert "backend" in cats    # from django

    def test_empty_set_returns_empty(self):
        assert expand_skills(set()) == set()

    def test_unknown_skill_returns_empty(self):
        assert expand_skills({"unknowntechnology123"}) == set()


# ── Jaccard helper ────────────────────────────────────────────────────────────

class TestJaccard:
    """Tests for the _jaccard private function via scorer module."""

    @pytest.fixture(autouse=True)
    def import_jaccard(self):
        # Import the private helper directly for unit testing.
        from scorer import _jaccard
        self._jaccard = _jaccard

    def test_identical_sets(self):
        assert self._jaccard({1, 2, 3}, {1, 2, 3}) == 1.0

    def test_disjoint_sets(self):
        assert self._jaccard({1}, {2}) == 0.0

    def test_partial_overlap(self):
        score = self._jaccard({1, 2}, {2, 3})
        assert 0.0 < score < 1.0

    def test_both_empty(self):
        assert self._jaccard(set(), set()) == 0.0

    def test_one_empty(self):
        assert self._jaccard({1, 2}, set()) == 0.0


# ── score_resumes integration ─────────────────────────────────────────────────

class TestScoreResumes:
    """Integration tests for the full scoring pipeline."""

    SAMPLE_JD = (
        "We are looking for a frontend developer with experience in React and "
        "TypeScript. The candidate should know Next.js and have worked with "
        "PostgreSQL databases. Experience with Docker and AWS is a plus."
    )

    GOOD_RESUME = (
        "Software engineer with 4 years of experience. Proficient in React, "
        "TypeScript, and Next.js. Worked with PostgreSQL and Redis. "
        "Deployed applications on AWS using Docker."
    )

    WEAK_RESUME = (
        "Fresh graduate. Completed coursework in Java and C++. "
        "Interested in software development. No professional experience."
    )

    def test_empty_applications_returns_empty_list(self):
        from scorer import score_resumes
        assert score_resumes(self.SAMPLE_JD, []) == []

    def test_returns_list_of_dicts(self):
        from scorer import score_resumes
        results = score_resumes(self.SAMPLE_JD, [
            {"id": "a1", "full_name": "Alice", "resume_text": self.GOOD_RESUME}
        ])
        assert isinstance(results, list)
        assert len(results) == 1
        assert "score" in results[0]
        assert "application_id" in results[0]

    def test_score_in_valid_range(self):
        from scorer import score_resumes
        results = score_resumes(self.SAMPLE_JD, [
            {"id": "a1", "full_name": "Alice", "resume_text": self.GOOD_RESUME}
        ])
        score = results[0]["score"]
        assert 0.0 <= score <= 100.0

    def test_sorted_descending(self):
        from scorer import score_resumes
        results = score_resumes(self.SAMPLE_JD, [
            {"id": "weak", "full_name": "Bob",   "resume_text": self.WEAK_RESUME},
            {"id": "good", "full_name": "Alice", "resume_text": self.GOOD_RESUME},
        ])
        assert results[0]["score"] >= results[1]["score"]

    def test_good_resume_scores_higher_than_weak(self):
        from scorer import score_resumes
        results = score_resumes(self.SAMPLE_JD, [
            {"id": "weak", "full_name": "Bob",   "resume_text": self.WEAK_RESUME},
            {"id": "good", "full_name": "Alice", "resume_text": self.GOOD_RESUME},
        ])
        score_map = {r["application_id"]: r["score"] for r in results}
        assert score_map["good"] > score_map["weak"]

    def test_semantic_mode_no_breakdown(self, monkeypatch):
        monkeypatch.setenv("SCORING_MODE", "semantic")
        from scorer import score_resumes
        results = score_resumes(self.SAMPLE_JD, [
            {"id": "a1", "full_name": "Alice", "resume_text": self.GOOD_RESUME}
        ])
        assert "breakdown" not in results[0]

    def test_hybrid_mode_has_breakdown(self, monkeypatch):
        monkeypatch.setenv("SCORING_MODE", "hybrid")
        from scorer import score_resumes
        results = score_resumes(self.SAMPLE_JD, [
            {"id": "a1", "full_name": "Alice", "resume_text": self.GOOD_RESUME}
        ])
        assert "breakdown" in results[0]
        bd = results[0]["breakdown"]
        assert "semantic"  in bd
        assert "skill"     in bd
        assert "category"  in bd
        assert bd["mode"]  == "hybrid"

    def test_hybrid_mode_score_in_range(self, monkeypatch):
        monkeypatch.setenv("SCORING_MODE", "hybrid")
        from scorer import score_resumes
        results = score_resumes(self.SAMPLE_JD, [
            {"id": "a1", "full_name": "Alice", "resume_text": self.GOOD_RESUME}
        ])
        assert 0.0 <= results[0]["score"] <= 100.0

    def test_hybrid_mode_react_bridges_to_frontend(self, monkeypatch):
        """
        Resume mentions React; JD mentions frontend.
        In hybrid mode the category score should be > 0 because
        React expands to 'frontend' via skill_map.
        """
        monkeypatch.setenv("SCORING_MODE", "hybrid")
        from scorer import score_resumes
        jd     = "We need a frontend developer experienced in UI design."
        resume = "Proficient in React and TypeScript. Built SPAs."
        results = score_resumes(jd, [{"id": "r1", "full_name": "X", "resume_text": resume}])
        assert results[0]["breakdown"]["category"] > 0

    def test_none_resume_text_handled_gracefully(self):
        from scorer import score_resumes
        results = score_resumes(self.SAMPLE_JD, [
            {"id": "a1", "full_name": "Alice", "resume_text": None}
        ])
        assert len(results) == 1
        assert results[0]["score"] >= 0.0
