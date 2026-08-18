import pdfplumber
import spacy

# 1. Load spaCy's trained English NLP model
nlp = spacy.load("en_core_web_sm")

# 2. Expanded 22 Job Roles (Junior, Senior & Specialized Roles)
JOB_ROLE_SKILLS = {
    # Data & AI Roles
    "Junior Data Analyst": ["python", "sql", "excel", "statistics", "data visualization"],
    "Senior Data Analyst": ["python", "sql", "excel", "pandas", "numpy", "tableau", "power bi", "statistics", "data visualization", "a/b testing"],
    "Junior Data Scientist": ["python", "sql", "pandas", "numpy", "statistics", "scikit-learn", "machine learning"],
    "Senior Data Scientist": ["python", "sql", "pandas", "numpy", "statistics", "scikit-learn", "machine learning", "deep learning", "tensorflow", "nlp", "big data"],
    "AI / Machine Learning Engineer": ["python", "machine learning", "deep learning", "tensorflow", "pytorch", "nlp", "scikit-learn", "sql", "docker", "rest api"],
    
    # Frontend Roles
    "Junior Frontend Developer": ["html", "css", "javascript", "git", "responsive design"],
    "Senior Frontend Developer": ["html", "css", "javascript", "react", "typescript", "tailwind css", "next.js", "git", "responsive design", "web performance"],
    
    # Backend Roles
    "Junior Backend Developer": ["python", "sql", "git", "rest api", "flask"],
    "Senior Backend Developer": ["python", "flask", "django", "fastapi", "sql", "postgresql", "mongodb", "rest api", "git", "docker", "microservices"],
    
    # Python Roles
    "Junior Python Developer": ["python", "git", "sql", "data structures", "algorithms"],
    "Senior Python Engineer": ["python", "data structures", "algorithms", "flask", "django", "sql", "git", "object oriented programming", "testing", "docker"],
    
    # Full Stack Roles
    "Junior Full Stack Developer": ["html", "css", "javascript", "python", "flask", "sql", "git"],
    "Senior Full Stack Engineer": ["html", "css", "javascript", "react", "typescript", "python", "flask", "sql", "postgresql", "git", "rest api", "tailwind css", "docker"],
    
    # DevOps & Cloud
    "DevOps Engineer": ["git", "docker", "kubernetes", "ci/cd", "aws", "linux", "python", "bash", "terraform"],
    "Cloud Solutions Architect": ["aws", "azure", "docker", "kubernetes", "cloud security", "python", "networking", "terraform"],
    
    # Specialized Tech Roles
    "Cyber Security Analyst": ["networking", "linux", "python", "cyber security", "ethical hacking", "firewalls", "siem"],
    "Mobile App Developer (Flutter/React Native)": ["javascript", "react native", "flutter", "dart", "mobile dev", "git", "rest api"],
    "UI/UX Designer": ["figma", "wireframing", "prototyping", "user research", "responsive design", "ui design"],
    "Software QA / Automation Tester": ["python", "selenium", "testing", "automation testing", "git", "sql", "jira"],
    "Database Administrator (DBA)": ["sql", "postgresql", "mysql", "mongodb", "database optimization", "backup & recovery", "linux"],
    "Product Manager (Tech)": ["agile", "scrum", "jira", "product roadmap", "data analytics", "user research", "wireframing"],
    "System Administrator": ["linux", "windows server", "networking", "bash", "active directory", "cyber security", "troubleshooting"]
}

# 3. Learning resource links for skills
SKILL_LEARNING_LINKS = {
    "python": "https://www.w3schools.com/python/",
    "sql": "https://www.w3schools.com/sql/",
    "excel": "https://support.microsoft.com/en-us/excel",
    "pandas": "https://pandas.pydata.org/docs/",
    "numpy": "https://numpy.org/doc/stable/",
    "tableau": "https://www.tableau.com/learn",
    "power bi": "https://learn.microsoft.com/en-us/power-bi/",
    "statistics": "https://www.khanacademy.org/math/statistics-probability",
    "data visualization": "https://www.kaggle.com/learn/data-visualization",
    "a/b testing": "https://www.optimizely.com/optimization-glossary/ab-testing/",
    "html": "https://www.w3schools.com/html/",
    "css": "https://www.w3schools.com/css/",
    "javascript": "https://developer.mozilla.org/en-US/docs/Web/JavaScript",
    "react": "https://react.dev/learn",
    "tailwind css": "https://tailwindcss.com/docs",
    "next.js": "https://nextjs.org/docs",
    "git": "https://git-scm.com/doc",
    "typescript": "https://www.typescriptlang.org/docs/",
    "responsive design": "https://web.dev/learn/design",
    "web performance": "https://web.dev/performance/",
    "flask": "https://flask.palletsprojects.com/",
    "django": "https://docs.djangoproject.com/",
    "fastapi": "https://fastapi.tiangolo.com/",
    "postgresql": "https://www.postgresql.org/docs/",
    "mysql": "https://dev.mysql.com/doc/",
    "mongodb": "https://www.mongodb.com/docs/",
    "rest api": "https://restfulapi.net/",
    "docker": "https://docs.docker.com/",
    "kubernetes": "https://kubernetes.io/docs/",
    "microservices": "https://microservices.io/",
    "ci/cd": "https://about.gitlab.com/topics/ci-cd/",
    "aws": "https://aws.amazon.com/training/",
    "azure": "https://learn.microsoft.com/en-us/azure/",
    "linux": "https://www.netacad.com/courses/os-it/ndg-linux-unhatched",
    "bash": "https://www.gnu.org/software/bash/manual/",
    "terraform": "https://developer.hashicorp.com/terraform/tutorials",
    "data structures": "https://www.geeksforgeeks.org/data-structures/",
    "algorithms": "https://www.geeksforgeeks.org/fundamentals-of-algorithms/",
    "object oriented programming": "https://realpython.com/python3-object-oriented-programming/",
    "testing": "https://docs.pytest.org/",
    "machine learning": "https://www.coursera.org/learn/machine-learning",
    "deep learning": "https://www.deeplearning.ai/",
    "tensorflow": "https://www.tensorflow.org/learn",
    "pytorch": "https://pytorch.org/tutorials/",
    "scikit-learn": "https://scikit-learn.org/stable/",
    "nlp": "https://spacy.io/usage/spacy-101",
    "big data": "https://www.ibm.com/topics/big-data",
    "cyber security": "https://www.coursera.org/specializations/cyber-security",
    "ethical hacking": "https://www.geeksforgeeks.org/ethical-hacking/",
    "firewalls": "https://www.cisco.com/c/en/us/products/security/firewalls/index.html",
    "siem": "https://www.splunk.com/en_us/data-insider/what-is-siem.html",
    "react native": "https://reactnative.dev/docs/getting-started",
    "flutter": "https://docs.flutter.dev/",
    "dart": "https://dart.dev/guides",
    "mobile dev": "https://developer.android.com/",
    "figma": "https://help.figma.com/hc/en-us",
    "wireframing": "https://www.usability.gov/how-to-and-tools/methods/wireframing.html",
    "prototyping": "https://designlab.com/blog/ux-prototyping-guide/",
    "user research": "https://www.nngroup.com/articles/",
    "ui design": "https://refactoringui.com/",
    "selenium": "https://www.selenium.dev/documentation/",
    "automation testing": "https://www.browserstack.com/guide/automation-testing-framework",
    "jira": "https://www.atlassian.com/software/jira/guides",
    "database optimization": "https://use-the-index-luke.com/",
    "backup & recovery": "https://www.postgresql.org/docs/current/backup.html",
    "agile": "https://www.atlassian.com/agile",
    "scrum": "https://www.scrum.org/resources/what-is-scrum",
    "product roadmap": "https://www.productplan.com/roadmap-basics/",
    "windows server": "https://learn.microsoft.com/en-us/windows-server/",
    "active directory": "https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/get-started/ad-ds-overview",
    "troubleshooting": "https://support.microsoft.com/"
}

def generate_job_links(role_name):
    """
    Generates direct live job search links for selected role across top portals.
    """
    query = role_name.replace(" ", "%20")
    return {
        "linkedin": f"https://www.linkedin.com/jobs/search/?keywords={query}",
        "indeed": f"https://www.indeed.com/jobs?q={query}",
        "naukri": f"https://www.naukri.com/{role_name.lower().replace(' ', '-')}-jobs",
        "glassdoor": f"https://www.glassdoor.com/Job/jobs.htm?sc.keyword={query}"
    }

def generate_resume_suggestions(text, matched_skills, missing_skills, score):
    """
    Generates smart actionable recommendations to upgrade resume content & ATS compatibility.
    """
    suggestions = []
    
    # 1. Action Verbs Check
    action_words = ["developed", "built", "designed", "engineered", "managed", "implemented", "created", "optimized", "led"]
    found_verbs = [w for w in action_words if w in text]
    if len(found_verbs) < 3:
        suggestions.append("<b>Use Strong Action Verbs:</b> Add action-oriented words like <i>'Engineered'</i>, <i>'Optimized'</i>, or <i>'Implemented'</i> to describe your projects/experience.")

    # 2. Metrics / Quantifiable Achievements
    digits = [char for char in text if char.isdigit()]
    if len(digits) < 5:
        suggestions.append("<b>Add Quantifiable Metrics:</b> Include numbers to highlight achievements (e.g., <i>'Improved speed by 30%'</i> or <i>'Built 5+ full-stack applications'</i>).")

    # 3. Project Section Tip
    if "project" not in text and "projects" not in text:
        suggestions.append("<b>Include Dedicated Projects Section:</b> Clearly list 2-3 key technical projects with GitHub links and live demos.")

    # 4. ATS Formatting
    suggestions.append("<b>ATS Optimization Tip:</b> Ensure your resume uses standard section headers ('Skills', 'Projects', 'Education') and plain PDF formatting.")

    return suggestions

def extract_text_from_pdf(pdf_path):
    extracted_text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    extracted_text += text + " "
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""
    return extracted_text.lower()

def analyze_resume(resume_text, target_role="Junior Data Analyst"):
    required_skills = JOB_ROLE_SKILLS.get(target_role, JOB_ROLE_SKILLS["Junior Data Analyst"])
    
    doc = nlp(resume_text)
    extracted_tokens = set([token.text.lower() for token in doc if not token.is_stop])
    
    matched_skills = []
    missing_skills = []
    
    for skill in required_skills:
        if skill in resume_text or skill in extracted_tokens:
            matched_skills.append(skill.title())
        else:
            missing_skills.append({
                "name": skill.title(),
                "learn_link": SKILL_LEARNING_LINKS.get(skill, "https://google.com")
            })
            
    total_skills = len(required_skills)
    matched_count = len(matched_skills)
    match_score = int(round((matched_count / total_skills) * 100)) if total_skills > 0 else 0
    
    # Generate Job Availability Links
    job_links = generate_job_links(target_role)
    
    # Generate AI Resume Suggestions
    resume_tips = generate_resume_suggestions(resume_text, matched_skills, missing_skills, match_score)
    
    return {
        "match_score": match_score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "total_required": total_skills,
        "target_role": target_role,
        "job_links": job_links,
        "resume_tips": resume_tips
    }