
"""
SkillGap AI - Resume Skill Analyzer
Compares resume text against a basic, predefined job-role skill list.
"""

import re
import spacy

# Load spaCy's English model.
# The fallback keeps the prototype usable if the model is not installed yet.
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    nlp = spacy.blank("en")


ROLE_SKILLS = {
    "Data Analyst": [
        "python", "sql", "excel", "power bi", "tableau",
        "statistics", "data visualization", "pandas",
        "numpy", "data cleaning"
    ],
    "Frontend Developer": [
        "html", "css", "javascript", "react", "responsive design",
        "git", "accessibility", "typescript", "rest api", "testing"
    ],
    "Backend Developer": [
        "python", "flask", "django", "sql", "rest api",
        "authentication", "git", "docker", "testing", "databases"
    ],
    "Python Engineer": [
        "python", "oop", "data structures", "algorithms",
        "pytest", "flask", "django", "sql", "git", "api development"
    ],
    "Full Stack Developer": [
        "html", "css", "javascript", "react", "python",
        "flask", "sql", "rest api", "git", "authentication"
    ],
    "Data Scientist": [
        "python", "statistics", "machine learning", "pandas",
        "numpy", "scikit-learn", "data visualization",
        "sql", "data cleaning", "deep learning"
    ],
}

COURSES = {
    "python": "https://www.freecodecamp.org/learn/scientific-computing-with-python/",
    "sql": "https://www.freecodecamp.org/learn/relational-database/",
    "html": "https://developer.mozilla.org/en-US/docs/Learn/HTML",
    "css": "https://developer.mozilla.org/en-US/docs/Learn/CSS",
    "javascript": "https://www.freecodecamp.org/learn/javascript-algorithms-and-data-structures-v8/",
    "react": "https://react.dev/learn",
    "flask": "https://flask.palletsprojects.com/en/stable/tutorial/",
    "django": "https://docs.djangoproject.com/en/stable/intro/tutorial01/",
    "excel": "https://support.microsoft.com/excel",
    "power bi": "https://learn.microsoft.com/en-us/training/powerplatform/power-bi/",
    "tableau": "https://www.tableau.com/learn/training",
    "statistics": "https://www.khanacademy.org/math/statistics-probability",
    "data visualization": "https://www.freecodecamp.org/news/tag/data-visualization/",
    "pandas": "https://pandas.pydata.org/docs/getting_started/intro_tutorials/",
    "numpy": "https://numpy.org/learn/",
    "data cleaning": "https://www.kaggle.com/learn/data-cleaning",
    "responsive design": "https://web.dev/learn/design/",
    "git": "https://docs.github.com/en/get-started",
    "accessibility": "https://web.dev/learn/accessibility/",
    "typescript": "https://www.typescriptlang.org/docs/",
    "rest api": "https://developer.mozilla.org/en-US/docs/Web/HTTP",
    "testing": "https://docs.pytest.org/en/stable/getting-started.html",
    "authentication": "https://developer.mozilla.org/en-US/docs/Web/Security",
    "docker": "https://docs.docker.com/get-started/",
    "databases": "https://www.postgresql.org/docs/",
    "oop": "https://docs.python.org/3/tutorial/classes.html",
    "data structures": "https://www.geeksforgeeks.org/data-structures/",
    "algorithms": "https://www.geeksforgeeks.org/fundamentals-of-algorithms/",
    "pytest": "https://docs.pytest.org/en/stable/",
    "api development": "https://flask.palletsprojects.com/en/stable/",
    "machine learning": "https://www.kaggle.com/learn/intro-to-machine-learning",
    "scikit-learn": "https://scikit-learn.org/stable/getting_started.html",
    "deep learning": "https://www.deeplearning.ai/",
}


def normalize_text(text):
    """Lowercase text and standardize whitespace."""
    text = text.lower()
    return re.sub(r"\s+", " ", text).strip()


def analyze_resume(resume_text, job_role):
    """Return matched skills, missing skills, and match percentage."""

    if job_role not in ROLE_SKILLS:
        raise ValueError("Please select a supported job role.")

    if not resume_text or not resume_text.strip():
        raise ValueError("No readable text was found in the resume PDF.")

    normalized_resume = normalize_text(resume_text)

    # Run the text through spaCy for English tokenization.
    # Skill matching below uses exact phrase checks to reduce false matches.
    doc = nlp(normalized_resume)
    tokens = {token.text for token in doc if not token.is_space}
    padded_text = f" {normalized_resume} "

    required_skills = ROLE_SKILLS[job_role]
    matched = []
    missing = []

    for skill in required_skills:
        skill_normalized = normalize_text(skill)

        # Multiword skills need phrase matching; single words use token matching.
        if " " in skill_normalized:
            found = f" {skill_normalized} " in padded_text
        else:
            found = skill_normalized in tokens

        if found:
            matched.append(skill)
        else:
            missing.append({
                "skill": skill,
                "course_url": COURSES.get(
                    skill,
                    "https://www.freecodecamp.org/learn/"
                ),
            })

    total = len(required_skills)
    percentage = round((len(matched) / total) * 100) if total else 0

    return {
        "job_role": job_role,
        "match_percentage": percentage,
        "matched_count": len(matched),
        "required_count": total,
        "matched_skills": matched,
        "missing_skills": missing,
        "notice": (
            "This is a basic keyword-based estimate, not a hiring decision "
            "or a validated measure of professional ability."
        ),
    }
