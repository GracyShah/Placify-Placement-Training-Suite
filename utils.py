import json
import os
import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from docx import Document
from flask import current_app
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
from werkzeug.utils import secure_filename

from data.test_catalog import TOPIC_TEST_CATALOG
from nlp.resume_parser import ResumeParser


ALLOWED_RESUME_EXTENSIONS = {".pdf", ".docx"}
ALLOWED_JD_EXTENSIONS = {".pdf", ".docx", ".doc"}
DEFAULT_JOB_DESCRIPTION = (
    "We are hiring a software developer with python, java, javascript, sql, git, "
    "react, flask, docker, machine learning, and problem solving skills."
)
TOPIC_TEST_MAP = {
    test["test_id"]: test
    for topic in TOPIC_TEST_CATALOG
    for test in topic["tests"]
}


def current_time():
    return datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%Y-%m-%d %H:%M:%S")


def calculate_resume_score(resume_data, jd_match_percentage=0):
    ats_score = 0
    if resume_data.get("full_name"):
        ats_score += 15
    if resume_data.get("email"):
        ats_score += 10
    if resume_data.get("phone"):
        ats_score += 10
    if resume_data.get("education"):
        ats_score += 20
    if resume_data.get("skills"):
        ats_score += 20
    if resume_data.get("experience") or resume_data.get("projects"):
        ats_score += 25

    keyword_score = 0
    skills_text = " ".join([
        resume_data.get("skills", ""),
        resume_data.get("experience", ""),
        resume_data.get("projects", ""),
    ]).lower()
    important_keywords = ["python", "java", "javascript", "react", "sql", "database", "api", "git", "team", "project", "leadership", "communication", "problem solving", "agile", "development"]
    for keyword in important_keywords:
        if keyword in skills_text:
            keyword_score += 100 / len(important_keywords)

    total_length = sum(len(str(resume_data.get(key, ""))) for key in ["education", "skills", "experience", "projects", "certifications"])
    format_score = 0
    if total_length > 100:
        format_score += 40
    if total_length > 300:
        format_score += 30
    if total_length > 500:
        format_score += 30

    overall_score = (ats_score + keyword_score + format_score) / 3
    overall_score = (overall_score * 0.6) + (jd_match_percentage * 0.4)

    feedback = []
    if ats_score < 70:
        feedback.append("Add more details to key sections like education and experience.")
    if keyword_score < 50:
        feedback.append("Include more relevant technical skills and keywords.")
    if format_score < 60:
        feedback.append("Expand your resume with more detailed descriptions.")
    if overall_score >= 80:
        feedback.append("Excellent resume! Well structured and comprehensive.")
    elif overall_score >= 60:
        feedback.append("Good resume, but there's room for improvement.")
    else:
        feedback.append("Your resume needs significant enhancement.")

    return {
        "ats_score": round(ats_score, 2),
        "keyword_score": round(keyword_score, 2),
        "format_score": round(format_score, 2),
        "overall_score": round(overall_score, 2),
        "feedback": " ".join(feedback),
        "jd_match_percentage": round(jd_match_percentage, 2),
    }


def build_ai_recommendation_payload(performance_rows):
    weak_sections = []
    improvement_areas = []
    overall_avg = 0

    if performance_rows:
        scores = [row["avg_score"] for row in performance_rows]
        overall_avg = sum(scores) / len(scores) if scores else 0
        for row in performance_rows:
            if row["avg_score"] >= 60:
                continue
            section_name = row["section_name"]
            weak_sections.append(section_name)
            if section_name == "Aptitude":
                improvement_areas.append("Practice more quantitative problems and speed calculations")
            elif section_name in ("Logical Reasoning", "Logical"):
                improvement_areas.append("Work on pattern recognition and logical puzzles")
            elif section_name in ("Coding", "DSA Basics"):
                improvement_areas.append("Focus on data structures and algorithms")
            elif section_name == "Verbal":
                improvement_areas.append("Improve vocabulary, grammar accuracy, and reading comprehension speed")
            elif section_name == "SQL":
                improvement_areas.append("Revise joins, grouping, filtering, and query writing fundamentals")
            elif section_name == "HR & Soft Skills":
                improvement_areas.append("Improve communication and behavioral interview skills")
            elif section_name == "Domain Knowledge":
                improvement_areas.append("Study core technical concepts and fundamentals")

    if overall_avg < 50:
        practice_focus = "Focus on fundamentals across all sections. Take more practice tests."
    elif overall_avg < 70:
        practice_focus = "Good progress! Concentrate on weak areas and time management."
    else:
        practice_focus = "Excellent performance! Maintain consistency and polish advanced topics."

    return {
        "weak_sections": weak_sections,
        "improvement_areas": improvement_areas,
        "practice_focus": practice_focus,
        "readiness_score": round(min(overall_avg + 10, 100), 2),
    }


def count_projects(text):
    return len(re.findall(r"\bproject[s]?\b", (text or "").lower()))


def detect_resume_type(resume_text):
    text = (resume_text or "").lower()
    project_count = count_projects(text)
    experience_entries = len(re.findall(r"\bexperience\b|\bworked\b|\bemployment\b|\bdeveloper\b", text))
    internship_hits = len(re.findall(r"\binternship\b|\bintern\b|\btrainee\b", text))

    years = []
    years.extend(float(match) for match in re.findall(r"(\d+(?:\.\d+)?)\+?\s+years?", text))
    years.extend(float(match) for match in re.findall(r"experience\s+of\s+(\d+(?:\.\d+)?)", text))
    max_years = max(years) if years else 0.0

    fresher_score = 0.0
    experienced_score = 0.0
    if max_years >= 2:
        experienced_score += 0.55
    elif max_years >= 1:
        experienced_score += 0.35
    else:
        fresher_score += 0.25
    if internship_hits:
        fresher_score += min(0.25, internship_hits * 0.08)
    if project_count >= max(experience_entries, 1):
        fresher_score += 0.25
    else:
        experienced_score += 0.2
    if experience_entries >= 2:
        experienced_score += 0.25
    elif experience_entries == 1:
        experienced_score += 0.1
    else:
        fresher_score += 0.15

    total_score = fresher_score + experienced_score
    if total_score == 0:
        return {"resume_type": "Fresher", "confidence_score": 0.5}

    fresher_confidence = fresher_score / total_score
    experienced_confidence = experienced_score / total_score
    if experienced_confidence > fresher_confidence:
        return {"resume_type": "Experienced professional", "confidence_score": round(experienced_confidence, 2)}
    return {"resume_type": "Fresher", "confidence_score": round(fresher_confidence, 2)}


def split_items(text):
    return [item.strip() for item in re.split(r"[\n,]+", text or "") if item.strip()]


def extract_capabilities(text, skills=None):
    normalized_text = (text or "").lower()
    extracted_skills = list(skills or [])

    technical_keywords = {"api", "backend", "frontend", "database", "algorithms", "data structures", "machine learning", "deep learning", "testing", "automation", "cloud"}
    domain_keywords = {"finance", "banking", "healthcare", "ecommerce", "education", "analytics", "nlp", "computer vision", "cybersecurity", "devops", "web development"}
    tool_keywords = {"git", "github", "docker", "kubernetes", "aws", "azure", "google cloud", "flask", "django", "fastapi", "react", "node.js", "express.js", "tensorflow", "pytorch", "pandas", "numpy", "scikit-learn"}

    technical_skills = sorted({skill for skill in extracted_skills if skill in technical_keywords or skill in tool_keywords} | {keyword for keyword in technical_keywords if keyword in normalized_text})
    domain_knowledge = sorted({skill for skill in extracted_skills if skill in domain_keywords} | {keyword for keyword in domain_keywords if keyword in normalized_text})
    tools_and_technologies = sorted({skill for skill in extracted_skills if skill in tool_keywords} | {keyword for keyword in tool_keywords if keyword in normalized_text})

    applied_work = []
    for label, patterns in {
        "projects": [r"\bproject[s]?\b", r"\bbuilt\b", r"\bdeveloped\b", r"\bcreated\b"],
        "experience": [r"\bexperience\b", r"\bworked\b", r"\bemployment\b", r"\bengineer\b"],
        "internships": [r"\binternship\b", r"\bintern\b", r"\btrainee\b"],
    }.items():
        if any(re.search(pattern, normalized_text) for pattern in patterns):
            applied_work.append(label)

    return {
        "technical_skills": technical_skills,
        "applied_work": applied_work,
        "domain_knowledge": domain_knowledge,
        "tools_and_technologies": tools_and_technologies,
    }


def compute_overlap_score(resume_values, jd_values):
    resume_set = {value.strip().lower() for value in resume_values if value and value.strip()}
    jd_set = {value.strip().lower() for value in jd_values if value and value.strip()}
    if not jd_set:
        return 100.0
    return round((len(resume_set & jd_set) / len(jd_set)) * 100, 2)


def get_capability_weights(resume_type):
    if resume_type == "Experienced professional":
        return {"technical_skills": 0.3, "applied_work": 0.35, "domain_knowledge": 0.2, "tools_and_technologies": 0.15}
    return {"technical_skills": 0.35, "applied_work": 0.2, "domain_knowledge": 0.15, "tools_and_technologies": 0.3}


def compute_capability_match_scores(resume_text, job_description_text, resume_skills, job_skills, resume_type):
    resume_capabilities = extract_capabilities(resume_text, resume_skills)
    jd_capabilities = extract_capabilities(job_description_text, job_skills)
    weights = get_capability_weights(resume_type)
    category_scores = {key: compute_overlap_score(resume_capabilities[key], jd_capabilities[key]) for key in weights}
    role_fit_score = round(sum(category_scores[key] * weights[key] for key in weights), 2)
    skill_readiness_score = round((category_scores["technical_skills"] * 0.6) + (category_scores["tools_and_technologies"] * 0.25) + (category_scores["domain_knowledge"] * 0.15), 2)
    return {
        "resume_capabilities": resume_capabilities,
        "jd_capabilities": jd_capabilities,
        "category_scores": category_scores,
        "role_fit_score": role_fit_score,
        "skill_readiness_score": skill_readiness_score,
        "learning_gap_score": round(max(0.0, 100.0 - role_fit_score), 2),
    }


def infer_skill_evidence(skill, resume_text):
    normalized_text = (resume_text or "").lower()
    normalized_skill = skill.strip().lower()
    evidence = {"projects": [], "experience": [], "tools_usage": []}
    project_patterns = [rf"project[s]?[^\n.]*{re.escape(normalized_skill)}", rf"{re.escape(normalized_skill)}[^\n.]*project[s]?"]
    experience_patterns = [rf"experience[^\n.]*{re.escape(normalized_skill)}", rf"worked[^\n.]*{re.escape(normalized_skill)}", rf"{re.escape(normalized_skill)}[^\n.]*experience"]
    tool_patterns = [rf"using[^\n.]*{re.escape(normalized_skill)}", rf"with[^\n.]*{re.escape(normalized_skill)}", rf"tool[s]?[^\n.]*{re.escape(normalized_skill)}"]
    for pattern in project_patterns:
        evidence["projects"].extend(re.findall(pattern, normalized_text))
    for pattern in experience_patterns:
        evidence["experience"].extend(re.findall(pattern, normalized_text))
    for pattern in tool_patterns:
        evidence["tools_usage"].extend(re.findall(pattern, normalized_text))
    return {key: list(dict.fromkeys(value)) for key, value in evidence.items()}


def get_skill_confidence_label(score):
    if score >= 75:
        return "High"
    if score >= 45:
        return "Medium"
    return "Low"


def score_skills_with_evidence(skills, resume_text):
    confidence = []
    for skill in skills:
        evidence = infer_skill_evidence(skill, resume_text)
        score = 20.0
        if evidence["projects"]:
            score += 35.0
        if evidence["experience"]:
            score += 35.0
        if evidence["tools_usage"]:
            score += 20.0
        if not any(evidence.values()):
            score -= 15.0
        score = max(5.0, min(score, 100.0))
        confidence.append({"skill": skill, "confidence_score": round(score, 2), "confidence_level": get_skill_confidence_label(score), "evidence": evidence})
    return confidence


def build_tailored_resume(data, job_description_text):
    from nlp.skill_extractor import SkillExtractor
    from nlp.text_preprocessing import TextPreprocessor

    preprocessor = TextPreprocessor()
    extractor = SkillExtractor()
    skills_input = data.get("skills", "")
    experience = data.get("experience", "")
    projects = data.get("projects", "")
    certifications = data.get("certifications", "")
    education = data.get("education", "")
    target_company = (data.get("target_company") or "the target company").strip()
    target_role = (data.get("target_role") or "the target role").strip()
    job_description_text = (job_description_text or DEFAULT_JOB_DESCRIPTION).strip()

    combined_text = " ".join([skills_input, experience, projects, certifications, education])
    user_skills = extractor.extract_skills(preprocessor.preprocess(combined_text))
    job_skills = extractor.extract_skills(preprocessor.preprocess(job_description_text))
    merged_skills = list(dict.fromkeys(user_skills + job_skills))
    ats_keywords = ", ".join(job_skills) if job_skills else "python, sql, communication"
    summary = (
        f"Targeting the {target_role} opportunity at {target_company}. "
        f"Candidate brings experience across {', '.join(merged_skills[:8]) or 'software development'} "
        f"with a resume aligned to the job description requirements."
    )
    sections = [
        ("Full Name", data.get("full_name", "")),
        ("Contact", f"Email: {data.get('email', '')}\nPhone: {data.get('phone', '')}"),
        ("Professional Summary", summary),
        ("Core Skills", ", ".join(merged_skills)),
        ("Professional Experience", experience or "Add relevant internships, work experience, or leadership roles."),
        ("Projects", projects or "Add project details with measurable outcomes and tools used."),
        ("Education", education),
        ("Certifications", certifications or "Add certifications relevant to the target role."),
        ("Target Company", target_company),
        ("Target Role", target_role),
        ("Job Description Alignment", job_description_text),
        ("ATS Keywords", ats_keywords),
    ]
    resume_text = "\n\n".join(f"{title}\n{content}".strip() for title, content in sections if content)
    return {"sections": sections, "resume_text": resume_text, "match_percentage": 100.0 if job_skills else 90.0}


def generate_resume_files(user_id, sections):
    output_dir = Path(current_app.config["DOWNLOAD_FOLDER"])
    output_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = output_dir / f"resume_{user_id}.pdf"
    docx_path = output_dir / f"resume_{user_id}.docx"
    generate_resume_pdf(pdf_path, sections)
    generate_resume_docx(docx_path, sections)
    return {"pdf": str(pdf_path), "doc": str(docx_path)}


def generate_resume_pdf(file_path, sections):
    pdf = canvas.Canvas(str(file_path), pagesize=LETTER)
    width, height = LETTER
    x_margin = 50
    y = height - 50
    for title, content in sections:
        if not content:
            continue
        if y < 100:
            pdf.showPage()
            y = height - 50
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(x_margin, y, title)
        y -= 18
        pdf.setFont("Helvetica", 10)
        for line in str(content).splitlines():
            for wrapped_line in wrap_text(line, 90):
                if y < 60:
                    pdf.showPage()
                    y = height - 50
                    pdf.setFont("Helvetica", 10)
                pdf.drawString(x_margin, y, wrapped_line)
                y -= 14
        y -= 10
    pdf.save()


def generate_resume_docx(file_path, sections):
    document = Document()
    for index, (title, content) in enumerate(sections):
        if not content:
            continue
        if index == 0:
            document.add_heading(str(content), level=0)
            continue
        document.add_heading(title, level=1)
        for line in str(content).splitlines():
            document.add_paragraph(line)
    document.save(str(file_path))


def wrap_text(text, max_length):
    words = text.split()
    lines = []
    current_line = []
    for word in words:
        trial_line = " ".join(current_line + [word])
        if len(trial_line) <= max_length:
            current_line.append(word)
        else:
            lines.append(" ".join(current_line))
            current_line = [word]
    if current_line:
        lines.append(" ".join(current_line))
    return lines or [""]


def save_uploaded_file(uploaded_file):
    upload_dir = Path(current_app.config["UPLOAD_FOLDER"])
    upload_dir.mkdir(parents=True, exist_ok=True)
    filename = secure_filename(uploaded_file.filename)
    file_path = upload_dir / filename
    uploaded_file.save(file_path)
    return file_path


def extract_uploaded_document_text(uploaded_file, allowed_extensions):
    file_extension = os.path.splitext(uploaded_file.filename)[1].lower()
    if file_extension not in allowed_extensions:
        return None, file_extension
    file_path = save_uploaded_file(uploaded_file)
    if file_extension == ".doc":
        with open(file_path, "rb") as file_handle:
            return file_handle.read().decode("latin-1", errors="ignore"), file_extension
    return ResumeParser.extract_text(file_path), file_extension


def get_openai_client():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY is not set")
    try:
        from openai import OpenAI
    except ImportError as error:
        raise ValueError("OpenAI SDK is not installed") from error
    return OpenAI(api_key=api_key)


def extract_json_object(text):
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise ValueError("AI response was not valid JSON")
        return json.loads(text[start : end + 1])


def normalize_suggestions_payload(payload):
    return {
        "top_strengths": split_items(payload.get("top_strengths", ""))[:3],
        "priority_improvements": split_items(payload.get("priority_improvements", ""))[:5],
        "missing_keywords": split_items(payload.get("missing_keywords", ""))[:8],
        "rewritten_summary": (payload.get("rewritten_summary") or "").strip(),
        "bullet_improvements": split_items(payload.get("bullet_improvements", ""))[:5],
    }


def generate_resume_ai_suggestions(resume_text, job_description_text):
    client = get_openai_client()
    response = client.responses.create(
        model=current_app.config["OPENAI_MODEL"],
        instructions="You are an expert resume coach. Return valid JSON with the keys top_strengths, priority_improvements, missing_keywords, rewritten_summary, and bullet_improvements.",
        input=[{"role": "user", "content": [{"type": "input_text", "text": f"Analyze this resume against the job description and suggest improvements.\n\nResume Text:\n{resume_text}\n\nJob Description Text:\n{job_description_text}"}]}],
    )
    return normalize_suggestions_payload(extract_json_object(response.output_text))


def generate_resume_ai_chat_reply(resume_text, job_description_text, suggestions, question, chat_history):
    client = get_openai_client()
    messages = [{"role": "user", "content": [{"type": "input_text", "text": f"Use the following context to answer follow-up resume improvement questions.\n\nResume Text:\n{resume_text}\n\nJob Description Text:\n{job_description_text}\n\nCurrent Suggestions:\n{json.dumps(suggestions)}"}]}]
    for message in chat_history[-6:]:
        role = message.get("role")
        content = (message.get("content") or "").strip()
        if role in {"user", "assistant"} and content:
            messages.append({"role": role, "content": [{"type": "input_text", "text": content}]})
    messages.append({"role": "user", "content": [{"type": "input_text", "text": question}]})
    response = client.responses.create(
        model=current_app.config["OPENAI_MODEL"],
        instructions="You are a resume coach. Answer follow-up questions using the supplied resume, job description, and prior suggestions. Keep responses clear and actionable.",
        input=messages,
    )
    return response.output_text.strip()
