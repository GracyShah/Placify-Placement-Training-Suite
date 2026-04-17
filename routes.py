import json
import sqlite3
from pathlib import Path

from flask import Blueprint, current_app, jsonify, redirect, render_template, request, send_file, session, url_for

from data.test_catalog import TOPIC_TEST_CATALOG
from db import (
    create_company_test_attempt,
    create_company_test_response,
    create_test_attempt,
    create_topic_attempt,
    create_topic_response,
    create_user,
    create_user_response,
    finalize_company_test_attempt,
    finalize_test_attempt,
    finalize_topic_attempt,
    get_admin_department_stats,
    get_admin_students,
    get_company_test,
    get_company_test_attempt,
    get_company_test_attempt_by_id,
    get_company_test_questions as db_get_company_test_questions,
    get_company_test_responses,
    get_company_tests_for_user,
    get_latest_ai_recommendation,
    get_questions_for_section,
    get_recommendation_performance,
    get_resume_for_user,
    get_section_performance,
    get_test_sections,
    get_topic_attempt,
    get_topic_attempts_for_user,
    get_topic_responses,
    get_user_by_credentials,
    get_user_scores,
    reset_demo_data,
    save_ai_recommendation,
    save_resume_ai_suggestions,
    upsert_resume_for_user,
)
from utils import (
    ALLOWED_JD_EXTENSIONS,
    ALLOWED_RESUME_EXTENSIONS,
    DEFAULT_JOB_DESCRIPTION,
    TOPIC_TEST_MAP,
    build_ai_recommendation_payload,
    build_tailored_resume,
    build_test_performance_feedback,
    calculate_resume_score,
    compute_capability_match_scores,
    count_projects,
    current_time,
    detect_resume_type,
    extract_uploaded_document_text,
    generate_resume_ai_chat_reply,
    generate_resume_ai_suggestions,
    generate_resume_files,
    score_skills_with_evidence,
)
from nlp.matcher import SkillMatcher
from nlp.scorer import ResumeScorer
from nlp.skill_extractor import SkillExtractor
from nlp.text_preprocessing import TextPreprocessor


routes_bp = Blueprint("routes", __name__)


@routes_bp.route("/health")
def health():
    return jsonify({"status": "ok"})


@routes_bp.route("/")
def index():
    return render_template("index.html")


@routes_bp.route("/login")
def login_page():
    return render_template("login.html")


@routes_bp.route("/student")
def student_page():
    if "user_id" not in session or session.get("role") != "student":
        return redirect(url_for("routes.login_page"))
    return render_template("student.html")


@routes_bp.route("/admin")
def admin_page():
    if "user_id" not in session or session.get("role") != "admin":
        return redirect(url_for("routes.login_page"))
    return render_template("admin.html")


@routes_bp.route("/tests")
def tests_page():
    if "user_id" not in session:
        return redirect(url_for("routes.login_page"))
    return render_template("tests.html")


@routes_bp.route("/dashboard")
def dashboard_page():
    if "user_id" not in session:
        return redirect(url_for("routes.login_page"))
    return render_template("dashboard.html")


@routes_bp.route("/resume")
def resume_page():
    if "user_id" not in session:
        return redirect(url_for("routes.login_page"))
    return render_template("resume.html")


@routes_bp.route("/resume-analyzer")
def resume_analyzer_page():
    if "user_id" not in session:
        return redirect(url_for("routes.login_page"))
    return render_template("resume_analyzer.html")


@routes_bp.route("/company-tests")
def company_tests_page():
    if "user_id" not in session:
        return redirect(url_for("routes.login_page"))
    return render_template("company_tests.html")


@routes_bp.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json() or {}
    user = get_user_by_credentials(data.get("username"), data.get("password"))
    if not user:
        return jsonify({"success": False, "message": "Invalid credentials"}), 401

    session["user_id"] = user["id"]
    session["username"] = user["username"]
    session["role"] = user["role"]
    session["full_name"] = user["full_name"]
    return jsonify({"success": True, "role": user["role"], "redirect": "/student" if user["role"] == "student" else "/admin"})


@routes_bp.route("/api/register", methods=["POST"])
def api_register():
    data = request.get_json() or {}
    try:
        create_user(
            data.get("username"),
            data.get("email"),
            data.get("password"),
            data.get("full_name"),
            data.get("department"),
            data.get("year"),
            data.get("college", "Placify College"),
        )
    except sqlite3.IntegrityError:
        return jsonify({"success": False, "message": "Username or email already exists"}), 400
    return jsonify({"success": True, "message": "Registration successful"})


@routes_bp.route("/api/logout", methods=["POST"])
def api_logout():
    session.clear()
    return jsonify({"success": True})


@routes_bp.route("/api/topic_tests", methods=["GET"])
def api_topic_tests():
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Not logged in"}), 401

    attempts = get_topic_attempts_for_user(session["user_id"])
    attempt_map = {row["test_key"]: dict(row) for row in attempts}
    payload = []
    for topic in TOPIC_TEST_CATALOG:
        topic_payload = {
            "topic_name": topic["topic_name"],
            "topic_key": topic.get("topic_key"),
            "description": topic["description"],
            "test_count": topic["test_count"],
            "tests": [],
        }
        for test in topic["tests"]:
            attempt = attempt_map.get(test["test_id"])
            topic_payload["tests"].append(
                {
                    "test_id": test["test_id"],
                    "test_name": test["test_name"],
                    "description": test["description"],
                    "question_count": len(test["questions"]),
                    "time_limit": test["time_limit"],
                    "difficulty_tags": sorted({question.get("difficulty", "Medium") for question in test["questions"]}),
                    "attempted": bool(attempt),
                    "status": "Attempted" if attempt else "Not Attempted",
                    "score": attempt["score"] if attempt else None,
                    "completed_at": attempt["completed_at"] if attempt else None,
                    "solution_unlocked": bool(attempt),
                }
            )
        payload.append(topic_payload)
    return jsonify(payload)


@routes_bp.route("/api/topic_tests/<test_id>/questions", methods=["GET"])
def api_topic_test_questions(test_id):
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Not logged in"}), 401

    test = TOPIC_TEST_MAP.get(test_id)
    if not test:
        return jsonify({"success": False, "message": "Test not found"}), 404
    if get_topic_attempt(session["user_id"], test_id):
        return jsonify({"success": False, "message": "This test has already been attempted."}), 400

    return jsonify(
        {
            "test_id": test["test_id"],
            "test_name": test["test_name"],
            "topic_name": test["topic_name"],
            "topic_key": test["topic_key"],
            "time_limit": test["time_limit"],
            "questions": [
                {
                    "question_id": question["question_id"],
                    "question_text": question["question_text"],
                    "option_a": question["options"]["A"],
                    "option_b": question["options"]["B"],
                    "option_c": question["options"]["C"],
                    "option_d": question["options"]["D"],
                    "difficulty": question.get("difficulty", "Medium"),
                }
                for question in test["questions"]
            ],
        }
    )


@routes_bp.route("/api/topic_tests/<test_id>/submit", methods=["POST"])
def api_submit_topic_test(test_id):
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Not logged in"}), 401

    test = TOPIC_TEST_MAP.get(test_id)
    if not test:
        return jsonify({"success": False, "message": "Test not found"}), 404
    if get_topic_attempt(session["user_id"], test_id):
        return jsonify({"success": False, "message": "Each topic test can only be attempted once."}), 400

    data = request.get_json() or {}
    answers = data.get("answers", {})
    time_taken = data.get("time_taken", 0)
    correct_count = 0

    attempt_id = create_topic_attempt(session["user_id"], test["test_id"], test["topic_name"], test["test_name"], len(test["questions"]), time_taken, current_time())
    for question in test["questions"]:
        selected_answer = (answers.get(question["question_id"]) or "").upper()
        is_correct = selected_answer == question["correct_answer"]
        if is_correct:
            correct_count += 1
        create_topic_response(attempt_id, question["question_key"], selected_answer, is_correct)

    score = round((correct_count / len(test["questions"])) * 100, 2) if test["questions"] else 0
    finalize_topic_attempt(attempt_id, score, correct_count)
    _generate_ai_recommendations(session["user_id"])
    topic_group = next((topic for topic in TOPIC_TEST_CATALOG if topic["topic_key"] == test["topic_key"]), {})
    recommendation_pool = [
        other_test["test_name"]
        for other_test in topic_group.get("tests", [])
        if other_test["test_id"] != test_id and not get_topic_attempt(session["user_id"], other_test["test_id"])
    ]
    performance_feedback = build_test_performance_feedback(test["test_name"], test["topic_name"], test["questions"], answers, recommendation_pool)
    return jsonify({"success": True, "score": score, "correct": correct_count, "total": len(test["questions"]), "attempt_id": attempt_id, "test_name": test["test_name"], "topic_name": test["topic_name"], "topic_key": test["topic_key"], "performance_feedback": performance_feedback})


@routes_bp.route("/api/topic_tests/<test_id>/solutions", methods=["GET"])
def api_topic_test_solutions(test_id):
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Not logged in"}), 401

    test = TOPIC_TEST_MAP.get(test_id)
    if not test:
        return jsonify({"success": False, "message": "Test not found"}), 404

    attempt = get_topic_attempt(session["user_id"], test_id)
    if not attempt:
        return jsonify({"success": False, "message": "Solutions are available only after attempting the test."}), 403

    response_map = {row["question_key"]: dict(row) for row in get_topic_responses(attempt["id"])}
    return jsonify({
        "test_id": test["test_id"],
        "test_name": test["test_name"],
        "topic_name": test["topic_name"],
        "topic_key": test["topic_key"],
        "score": attempt["score"],
        "correct_answers": attempt["correct_answers"],
        "completed_at": attempt["completed_at"],
        "questions": [
            {
                "question_text": question["question_text"],
                "options": question["options"],
                "correct_answer": question["correct_answer"],
                "selected_answer": response_map.get(question["question_key"], {}).get("selected_answer", ""),
                "is_correct": bool(response_map.get(question["question_key"], {}).get("is_correct", 0)),
                "explanation": question["explanation"],
                "difficulty": question.get("difficulty", "Medium"),
            }
            for question in test["questions"]
        ],
    })


@routes_bp.route("/api/test_sections", methods=["GET"])
def api_test_sections():
    return jsonify([dict(row) for row in get_test_sections()])


@routes_bp.route("/api/questions/<int:section_id>", methods=["GET"])
def api_questions(section_id):
    return jsonify([dict(row) for row in get_questions_for_section(section_id)])


@routes_bp.route("/api/submit_test", methods=["POST"])
def api_submit_test():
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Not logged in"}), 401

    data = request.get_json() or {}
    section_id = data.get("section_id")
    answers = data.get("answers", {})
    time_taken = data.get("time_taken", 0)
    questions = get_questions_for_section(section_id, include_answers=True)

    correct_count = 0
    total_points = 0
    earned_points = 0
    attempt_id = create_test_attempt(session["user_id"], section_id, len(questions), time_taken, current_time())

    for question in questions:
        selected_answer = answers.get(str(question["id"]), "")
        is_correct = selected_answer.upper() == question["correct_answer"].upper()
        total_points += question["points"]
        if is_correct:
            correct_count += 1
            earned_points += question["points"]
        create_user_response(attempt_id, question["id"], selected_answer, is_correct)

    score = (earned_points / total_points * 100) if total_points > 0 else 0
    finalize_test_attempt(attempt_id, score, correct_count)
    _generate_ai_recommendations(session["user_id"])
    return jsonify({"success": True, "score": round(score, 2), "correct": correct_count, "total": len(questions), "attempt_id": attempt_id})


@routes_bp.route("/api/company_tests", methods=["GET"])
def api_company_tests():
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Not logged in"}), 401
    return jsonify([dict(row) for row in get_company_tests_for_user(session["user_id"])])


@routes_bp.route("/api/company_tests/<int:company_test_id>/questions", methods=["GET"])
def api_company_test_questions(company_test_id):
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Not logged in"}), 401

    test = get_company_test(company_test_id)
    questions = db_get_company_test_questions(company_test_id)
    latest_attempt = get_company_test_attempt(session["user_id"], company_test_id)
    if not test or not questions:
        return jsonify({"success": False, "message": "Questions not available for this company test yet."}), 404

    return jsonify({
        "company_test_id": company_test_id,
        "company_name": test["company_name"],
        "test_name": test["test_name"],
        "time_limit": test["total_duration"],
        "already_attempted": bool(latest_attempt),
        "latest_attempt_id": latest_attempt["id"] if latest_attempt else None,
        "questions": [dict(row) for row in questions],
    })


@routes_bp.route("/api/company_tests/<int:company_test_id>/submit", methods=["POST"])
def api_submit_company_test(company_test_id):
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Not logged in"}), 401

    questions = db_get_company_test_questions(company_test_id, include_answers=True)
    test = get_company_test(company_test_id)
    if not questions or not test:
        return jsonify({"success": False, "message": "Questions not available for this company test yet."}), 404

    data = request.get_json() or {}
    answers = data.get("answers", {})
    time_taken = data.get("time_taken", 0)
    correct_count = 0
    attempt_id = create_company_test_attempt(session["user_id"], company_test_id, time_taken, current_time())

    for question in questions:
        selected_answer = (answers.get(str(question["id"])) or "").upper()
        is_correct = selected_answer == (question["correct_answer"] or "").upper()
        if is_correct:
            correct_count += 1
        create_company_test_response(attempt_id, question["id"], selected_answer, is_correct)

    score = round((correct_count / len(questions)) * 100, 2) if questions else 0
    finalize_company_test_attempt(attempt_id, score)
    _generate_ai_recommendations(session["user_id"])
    recommendation_pool = sorted({row["section"] for row in questions if row["section"]})
    performance_feedback = build_test_performance_feedback(test["test_name"], test["company_name"], questions, answers, recommendation_pool)
    return jsonify({"success": True, "score": score, "correct": correct_count, "total": len(questions), "attempt_id": attempt_id, "performance_feedback": performance_feedback})


@routes_bp.route("/api/company_tests/<int:company_test_id>/solutions", methods=["GET"])
def api_company_test_solutions(company_test_id):
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Not logged in"}), 401

    requested_attempt_id = request.args.get("attempt_id", type=int)
    attempt = get_company_test_attempt_by_id(session["user_id"], company_test_id, requested_attempt_id) if requested_attempt_id else get_company_test_attempt(session["user_id"], company_test_id)
    if not attempt:
        return jsonify({"success": False, "message": "Solutions are available only after attempting the company-wise test."}), 403

    test = get_company_test(company_test_id)
    questions = db_get_company_test_questions(company_test_id, include_answers=True)
    response_map = {row["question_id"]: dict(row) for row in get_company_test_responses(attempt["id"])}

    return jsonify({
        "attempt_id": attempt["id"],
        "company_name": test["company_name"],
        "test_name": test["test_name"],
        "score": attempt["score"],
        "completed_at": attempt["completed_at"],
        "questions": [
            {
                "section": row["section"],
                "question_text": row["question_text"],
                "difficulty": row["difficulty"] if row["difficulty"] else "Medium",
                "options": {"A": row["option_a"], "B": row["option_b"], "C": row["option_c"], "D": row["option_d"]},
                "correct_answer": row["correct_answer"],
                "selected_answer": response_map.get(row["id"], {}).get("selected_answer", ""),
                "is_correct": bool(response_map.get(row["id"], {}).get("is_correct", 0)),
                "explanation": row["coding_output"] or "Review the correct option and compare it with your choice.",
            }
            for row in questions
        ],
    })


@routes_bp.route("/api/user_scores", methods=["GET"])
def api_user_scores():
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Not logged in"}), 401
    return jsonify([dict(row) for row in get_user_scores(session["user_id"])])


@routes_bp.route("/api/section_performance", methods=["GET"])
def api_section_performance():
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Not logged in"}), 401
    return jsonify([dict(row) for row in get_section_performance(session["user_id"])])


@routes_bp.route("/api/save_resume", methods=["POST"])
def api_save_resume():
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Not logged in"}), 401

    data = request.form.to_dict() if request.form else (request.get_json() or {})
    job_description_text = (data.get("job_description") or "").strip()
    jd_file = request.files.get("jd_file")
    if jd_file and jd_file.filename:
        jd_text, jd_extension = extract_uploaded_document_text(jd_file, ALLOWED_JD_EXTENSIONS)
        if jd_extension not in ALLOWED_JD_EXTENSIONS:
            return jsonify({"success": False, "message": "Only PDF, DOCX, and DOC files are allowed for the job description"}), 400
        job_description_text = jd_text.strip()

    tailored_resume = build_tailored_resume(data, job_description_text)
    scores = calculate_resume_score(data, tailored_resume["match_percentage"])
    generate_resume_files(session["user_id"], tailored_resume["sections"])
    upsert_resume_for_user(session["user_id"], {**data, "job_description": job_description_text, "resume_text": tailored_resume["resume_text"]}, scores)

    return jsonify({"success": True, "scores": scores, "resume_text": tailored_resume["resume_text"], "download_pdf_url": "/api/download_resume/pdf", "download_doc_url": "/api/download_resume/doc"})


@routes_bp.route("/api/get_resume", methods=["GET"])
def api_get_resume():
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Not logged in"}), 401
    resume = get_resume_for_user(session["user_id"])
    if not resume:
        return jsonify({"success": False, "message": "No resume found"}), 404
    return jsonify(dict(resume))


@routes_bp.route("/api/download_resume/<file_type>", methods=["GET"])
def api_download_resume(file_type):
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Not logged in"}), 401

    base_path = Path(current_app.config["DOWNLOAD_FOLDER"])
    if file_type == "pdf":
        file_path = base_path / f"resume_{session['user_id']}.pdf"
        download_name = "placify_resume.pdf"
    elif file_type == "doc":
        file_path = base_path / f"resume_{session['user_id']}.docx"
        download_name = "placify_resume.docx"
    else:
        return jsonify({"success": False, "message": "Invalid file type"}), 400

    if not file_path.exists():
        return jsonify({"success": False, "message": "Resume file not found"}), 404
    return send_file(file_path, as_attachment=True, download_name=download_name)


@routes_bp.route("/api/analyze_resume", methods=["POST"])
def api_analyze_resume():
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Not logged in"}), 401

    resume_file = request.files.get("resume_file")
    if not resume_file or not resume_file.filename:
        return jsonify({"success": False, "message": "Resume file is required"}), 400

    extracted_text, file_extension = extract_uploaded_document_text(resume_file, ALLOWED_RESUME_EXTENSIONS)
    if file_extension not in ALLOWED_RESUME_EXTENSIONS:
        return jsonify({"success": False, "message": "Only PDF and DOCX files are allowed"}), 400

    job_description_text = (request.form.get("job_description") or "").strip()
    jd_file = request.files.get("jd_file")
    if jd_file and jd_file.filename:
        jd_text, jd_extension = extract_uploaded_document_text(jd_file, ALLOWED_JD_EXTENSIONS)
        if jd_extension not in ALLOWED_JD_EXTENSIONS:
            return jsonify({"success": False, "message": "Only PDF, DOCX, and DOC files are allowed for the job description"}), 400
        job_description_text = jd_text.strip()
    if not job_description_text:
        job_description_text = DEFAULT_JOB_DESCRIPTION

    preprocessor = TextPreprocessor()
    extractor = SkillExtractor()
    scorer = ResumeScorer()
    cleaned_resume_text = preprocessor.preprocess(extracted_text)
    cleaned_job_text = preprocessor.preprocess(job_description_text)
    resume_skills = extractor.extract_skills(cleaned_resume_text)
    job_skills = extractor.extract_skills(cleaned_job_text)
    match_result = SkillMatcher.match(resume_skills, job_skills)

    normalized_resume_skills = {skill.strip().lower() for skill in resume_skills}
    normalized_job_skills = {skill.strip().lower() for skill in job_skills}
    missing_skills = sorted(normalized_job_skills - normalized_resume_skills)
    extra_skills = sorted(normalized_resume_skills - normalized_job_skills)
    keyword_overlap = sorted(normalized_resume_skills & normalized_job_skills)

    resume_score = scorer.calculate_score(match_result["match_percentage"], count_projects(extracted_text))
    resume_type_result = detect_resume_type(extracted_text)
    capability_scores = compute_capability_match_scores(extracted_text, job_description_text, resume_skills, job_skills, resume_type_result["resume_type"])
    skill_confidence = score_skills_with_evidence(resume_skills, extracted_text)

    return jsonify({
        "success": True,
        "extracted_skills": resume_skills,
        "skill_confidence": skill_confidence,
        "matched_skills": match_result["matched_skills"],
        "skill_match_percentage": match_result["match_percentage"],
        "match_percentage": match_result["match_percentage"],
        "missing_skills": missing_skills,
        "extra_skills": extra_skills,
        "keyword_overlap": keyword_overlap,
        "resume_text": extracted_text,
        "job_description_text": job_description_text,
        "resume_type": resume_type_result["resume_type"],
        "resume_type_confidence": resume_type_result["confidence_score"],
        "resume_capabilities": capability_scores["resume_capabilities"],
        "jd_capabilities": capability_scores["jd_capabilities"],
        "capability_category_scores": capability_scores["category_scores"],
        "role_fit_score": capability_scores["role_fit_score"],
        "skill_readiness_score": capability_scores["skill_readiness_score"],
        "learning_gap_score": capability_scores["learning_gap_score"],
        "resume_score": resume_score,
    })


@routes_bp.route("/api/resume_ai_suggestions", methods=["POST"])
def api_resume_ai_suggestions():
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Not logged in"}), 401

    data = request.get_json() or {}
    resume_text = (data.get("resume_text") or "").strip()
    job_description_text = (data.get("job_description_text") or "").strip()
    if not resume_text or not job_description_text:
        return jsonify({"success": False, "message": "Resume text and job description are required"}), 400

    suggestions = generate_resume_ai_suggestions(resume_text, job_description_text)
    save_resume_ai_suggestions(
        session["user_id"],
        resume_text,
        job_description_text,
        json.dumps(suggestions),
        suggestions.get("source", "nlp"),
    )
    return jsonify({"success": True, "suggestions": suggestions, "message": suggestions.get("notice")})


@routes_bp.route("/api/resume_ai_chat", methods=["POST"])
def api_resume_ai_chat():
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Not logged in"}), 401

    data = request.get_json() or {}
    resume_text = (data.get("resume_text") or "").strip()
    job_description_text = (data.get("job_description_text") or "").strip()
    question = (data.get("question") or "").strip()
    suggestions = data.get("suggestions") or {}
    chat_history = data.get("chat_history") or []
    if not resume_text or not job_description_text or not question:
        return jsonify({"success": False, "message": "Resume text, job description, and question are required"}), 400

    try:
        answer = generate_resume_ai_chat_reply(resume_text, job_description_text, suggestions, question, chat_history)
    except ValueError as error:
        return jsonify({"success": False, "message": str(error)}), 400
    except Exception as error:
        return jsonify({"success": False, "message": f"AI chat failed: {error}"}), 500
    return jsonify({"success": True, "answer": answer})


@routes_bp.route("/api/ai_recommendations", methods=["GET"])
def api_ai_recommendations():
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Not logged in"}), 401

    recommendations = get_latest_ai_recommendation(session["user_id"])
    if not recommendations:
        _generate_ai_recommendations(session["user_id"])
        recommendations = get_latest_ai_recommendation(session["user_id"])
    return jsonify(dict(recommendations) if recommendations else {})


@routes_bp.route("/api/admin/students", methods=["GET"])
def api_admin_students():
    if "user_id" not in session or session.get("role") != "admin":
        return jsonify({"success": False, "message": "Unauthorized"}), 403
    return jsonify([dict(row) for row in get_admin_students()])


@routes_bp.route("/api/admin/department_stats", methods=["GET"])
def api_admin_department_stats():
    if "user_id" not in session or session.get("role") != "admin":
        return jsonify({"success": False, "message": "Unauthorized"}), 403
    return jsonify([dict(row) for row in get_admin_department_stats()])


@routes_bp.route("/api/admin/reset_demo_data", methods=["POST"])
def api_admin_reset_demo_data():
    if "user_id" not in session or session.get("role") != "admin":
        return jsonify({"success": False, "message": "Unauthorized"}), 403
    try:
        deleted_rows = reset_demo_data()
    except sqlite3.DatabaseError as error:
        return jsonify({"success": False, "message": f"Database reset failed: {error}"}), 500
    return jsonify({"success": True, "message": "Demo data cleared successfully", "deleted_rows": deleted_rows})


@routes_bp.route("/api/user_info", methods=["GET"])
def api_user_info():
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Not logged in"}), 401
    return jsonify({"user_id": session["user_id"], "username": session["username"], "full_name": session["full_name"], "role": session["role"]})


def _generate_ai_recommendations(user_id):
    performance = get_recommendation_performance(user_id)
    payload = build_ai_recommendation_payload(performance)
    save_ai_recommendation(
        user_id,
        json.dumps(payload["weak_sections"]),
        json.dumps(payload["improvement_areas"]),
        payload["practice_focus"],
        payload["readiness_score"],
        json.dumps(payload),
    )
