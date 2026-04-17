import sqlite3
import threading
from pathlib import Path

from flask import current_app, g

from data.test_catalog import COMPANY_TEST_SEED


INITIALIZATION_LOCK = threading.Lock()

CORE_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    full_name VARCHAR(150) NOT NULL,
    role VARCHAR(20) DEFAULT 'student',
    department VARCHAR(100),
    year INTEGER,
    college VARCHAR(150),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS test_sections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    section_name VARCHAR(100) NOT NULL,
    description TEXT,
    total_questions INTEGER DEFAULT 10,
    time_limit INTEGER DEFAULT 30
);

CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    section_id INTEGER NOT NULL,
    question_text TEXT NOT NULL,
    option_a TEXT NOT NULL,
    option_b TEXT NOT NULL,
    option_c TEXT NOT NULL,
    option_d TEXT NOT NULL,
    correct_answer CHAR(1) NOT NULL,
    difficulty VARCHAR(20) DEFAULT 'medium',
    points INTEGER DEFAULT 1,
    FOREIGN KEY (section_id) REFERENCES test_sections(id)
);

CREATE TABLE IF NOT EXISTS test_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    section_id INTEGER NOT NULL,
    score DECIMAL(5,2) DEFAULT 0,
    total_questions INTEGER NOT NULL,
    correct_answers INTEGER DEFAULT 0,
    time_taken INTEGER,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (section_id) REFERENCES test_sections(id)
);

CREATE TABLE IF NOT EXISTS user_responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    attempt_id INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    selected_answer CHAR(1),
    is_correct BOOLEAN DEFAULT 0,
    FOREIGN KEY (attempt_id) REFERENCES test_attempts(id),
    FOREIGN KEY (question_id) REFERENCES questions(id)
);

CREATE TABLE IF NOT EXISTS resumes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    full_name VARCHAR(150),
    email VARCHAR(150),
    phone VARCHAR(20),
    target_company TEXT,
    target_role TEXT,
    education TEXT,
    skills TEXT,
    experience TEXT,
    projects TEXT,
    certifications TEXT,
    job_description TEXT,
    resume_text TEXT,
    ats_score DECIMAL(5,2) DEFAULT 0,
    keyword_score DECIMAL(5,2) DEFAULT 0,
    format_score DECIMAL(5,2) DEFAULT 0,
    overall_score DECIMAL(5,2) DEFAULT 0,
    feedback TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS ai_recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    weak_sections TEXT,
    improvement_areas TEXT,
    practice_focus TEXT,
    recommendation_payload TEXT,
    readiness_score DECIMAL(5,2) DEFAULT 0,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS topic_test_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    test_key TEXT NOT NULL,
    topic_name TEXT NOT NULL,
    test_name TEXT NOT NULL,
    score DECIMAL(5,2) DEFAULT 0,
    total_questions INTEGER NOT NULL,
    correct_answers INTEGER DEFAULT 0,
    time_taken INTEGER DEFAULT 0,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, test_key),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS topic_test_responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    attempt_id INTEGER NOT NULL,
    question_key TEXT NOT NULL,
    selected_answer TEXT,
    is_correct BOOLEAN DEFAULT 0,
    FOREIGN KEY (attempt_id) REFERENCES topic_test_attempts(id)
);

CREATE TABLE IF NOT EXISTS companies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_name TEXT NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS company_tests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    test_name TEXT NOT NULL,
    total_duration INTEGER,
    total_questions INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id)
);

CREATE TABLE IF NOT EXISTS company_test_questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_test_id INTEGER NOT NULL,
    section TEXT NOT NULL,
    question_type TEXT NOT NULL,
    question_text TEXT NOT NULL,
    option_a TEXT,
    option_b TEXT,
    option_c TEXT,
    option_d TEXT,
    correct_answer TEXT,
    coding_input TEXT,
    coding_output TEXT,
    difficulty TEXT DEFAULT "Medium",
    points INTEGER DEFAULT 1,
    FOREIGN KEY (company_test_id) REFERENCES company_tests(id)
);

CREATE TABLE IF NOT EXISTS company_test_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    company_test_id INTEGER NOT NULL,
    score REAL,
    time_taken INTEGER,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (company_test_id) REFERENCES company_tests(id)
);

CREATE TABLE IF NOT EXISTS company_test_responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    attempt_id INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    selected_answer TEXT,
    coding_answer TEXT,
    is_correct BOOLEAN,
    FOREIGN KEY (attempt_id) REFERENCES company_test_attempts(id),
    FOREIGN KEY (question_id) REFERENCES company_test_questions(id)
);
"""

DEFAULT_TEST_SECTIONS = [
    ("Aptitude", "Quantitative and analytical reasoning", 15, 20),
    ("Logical Reasoning", "Pattern recognition and logical thinking", 15, 20),
    ("Coding", "Programming concepts and problem solving", 10, 30),
    ("HR & Soft Skills", "Communication and behavioral questions", 10, 15),
    ("Domain Knowledge", "Technical domain specific questions", 10, 20),
]

DEFAULT_QUESTIONS = [
    (1, "If a train travels 60 km in 1 hour, how far will it travel in 3.5 hours at the same speed?", "180 km", "210 km", "240 km", "200 km", "B", "easy", 1),
    (1, "What is 15% of 200?", "25", "30", "35", "40", "B", "easy", 1),
    (1, "A shopkeeper marks up the price by 20% and gives 10% discount. What is the net profit percentage?", "8%", "10%", "12%", "15%", "A", "medium", 1),
    (1, "If 5 workers can complete a task in 12 days, how many days will 6 workers take?", "10 days", "9 days", "15 days", "8 days", "A", "medium", 1),
    (1, "The average of 5 numbers is 27. If one number is excluded, the average becomes 25. What is the excluded number?", "35", "37", "33", "39", "A", "hard", 1),
    (2, "Complete the series: 2, 6, 12, 20, 30, ?", "40", "42", "44", "46", "B", "medium", 1),
    (2, "If all roses are flowers and some flowers are red, can we conclude all roses are red?", "Yes", "No", "Cannot determine", "Insufficient data", "B", "easy", 1),
    (2, "Find the odd one out: Dog, Cat, Tiger, Chair", "Dog", "Cat", "Tiger", "Chair", "D", "easy", 1),
    (2, "If A is to the north of B and B is to the west of C, where is C with respect to A?", "South-East", "North-East", "South-West", "North-West", "A", "medium", 1),
    (2, "A cube is painted red on all faces. It is cut into 64 smaller cubes. How many cubes have no face painted?", "8", "16", "24", "32", "A", "hard", 1),
    (3, "What is the time complexity of binary search?", "O(n)", "O(log n)", "O(n log n)", "O(1)", "B", "easy", 1),
    (3, "Which data structure uses LIFO principle?", "Queue", "Stack", "Array", "Linked List", "B", "easy", 1),
    (3, "What will be the output of: print(2 ** 3)?", "5", "6", "8", "9", "C", "easy", 1),
    (3, "Which sorting algorithm has best case time complexity of O(n)?", "Bubble Sort", "Merge Sort", "Quick Sort", "Insertion Sort", "D", "medium", 1),
    (3, "What is the space complexity of recursive fibonacci?", "O(1)", "O(n)", "O(log n)", "O(n^2)", "B", "hard", 1),
    (4, "What does STAR method stand for in interviews?", "Start, Tell, Act, Result", "Situation, Task, Action, Result", "Skills, Teamwork, Attitude, Response", "Story, Task, Answer, Reason", "B", "easy", 1),
    (4, "Which is the best answer to \"What is your weakness?\"", "I have no weakness", "I work too hard", "I am improving my public speaking", "I am perfect", "C", "medium", 1),
    (4, "What is active listening?", "Hearing words only", "Fully concentrating and responding", "Waiting to speak", "Interrupting to clarify", "B", "easy", 1),
    (4, "Best way to handle workplace conflict?", "Avoid the person", "Communicate openly and professionally", "Complain to others", "Ignore it", "B", "easy", 1),
    (4, "What is emotional intelligence?", "IQ level", "Ability to understand and manage emotions", "Being emotional", "Avoiding feelings", "B", "medium", 1),
    (5, "What does HTTP stand for?", "HyperText Transfer Protocol", "High Transfer Text Protocol", "HyperText Transport Protocol", "High Tech Transfer Protocol", "A", "easy", 1),
    (5, "Which is a relational database?", "MongoDB", "PostgreSQL", "Redis", "Cassandra", "B", "easy", 1),
    (5, "What is an API?", "A programming language", "Application Programming Interface", "A database", "A server", "B", "easy", 1),
    (5, "What is the purpose of a PRIMARY KEY?", "To sort data", "To uniquely identify records", "To encrypt data", "To backup data", "B", "medium", 1),
    (5, "What is REST in web services?", "A database", "Representational State Transfer", "A programming language", "A server type", "B", "medium", 1),
]

DEFAULT_USERS = [
    ("admin", "admin@placify.com", "admin123", "Admin User", "admin", "Administration", None, "Placify College"),
    ("student1", "student1@college.com", "student123", "John Doe", "student", "Computer Science", 3, "Placify College"),
]

DEFAULT_COMPANY_TESTS = [
    {
        "company_name": seed["company_name"],
        "description": seed["description"],
    }
    for seed in COMPANY_TEST_SEED.values()
]


def init_app(app):
    app.before_request(ensure_database_initialized)
    app.teardown_appcontext(close_db)


def ensure_database_initialized():
    if current_app.config.get("_DB_INITIALIZED"):
        return

    with INITIALIZATION_LOCK:
        if current_app.config.get("_DB_INITIALIZED"):
            return

        database_path = Path(current_app.config["DATABASE_PATH"])
        database_path.parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(database_path) as connection:
            connection.row_factory = sqlite3.Row
            connection.execute("PRAGMA foreign_keys = ON")
            connection.executescript(CORE_TABLES_SQL)
            _ensure_resume_columns(connection)
            _seed_test_sections(connection)
            _seed_questions(connection)
            _seed_default_users(connection)
            _seed_company_tests(connection)
            _seed_company_test_questions(connection)
            connection.commit()

        current_app.config["_DB_INITIALIZED"] = True


def get_db():
    ensure_database_initialized()
    if "db_connection" not in g:
        connection = sqlite3.connect(current_app.config["DATABASE_PATH"])
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        g.db_connection = connection
    return g.db_connection


def close_db(_error=None):
    connection = g.pop("db_connection", None)
    if connection is not None:
        connection.close()


def _fetch_all(query, params=()):
    cursor = get_db().execute(query, params)
    return cursor.fetchall()


def _fetch_one(query, params=()):
    cursor = get_db().execute(query, params)
    return cursor.fetchone()


def _execute(query, params=()):
    connection = get_db()
    cursor = connection.execute(query, params)
    connection.commit()
    return cursor.lastrowid


def _ensure_resume_columns(connection):
    existing_columns = {row["name"] for row in connection.execute("PRAGMA table_info(resumes)").fetchall()}
    missing_columns = {
        "target_company": "ALTER TABLE resumes ADD COLUMN target_company TEXT",
        "target_role": "ALTER TABLE resumes ADD COLUMN target_role TEXT",
        "job_description": "ALTER TABLE resumes ADD COLUMN job_description TEXT",
        "ai_suggestions_payload": "ALTER TABLE resumes ADD COLUMN ai_suggestions_payload TEXT",
        "ai_suggestions_source": "ALTER TABLE resumes ADD COLUMN ai_suggestions_source TEXT",
        "ai_suggestions_updated_at": "ALTER TABLE resumes ADD COLUMN ai_suggestions_updated_at TIMESTAMP",
    }
    recommendation_columns = {row["name"] for row in connection.execute("PRAGMA table_info(ai_recommendations)").fetchall()}
    company_question_columns = {row["name"] for row in connection.execute("PRAGMA table_info(company_test_questions)").fetchall()}
    if "difficulty" not in company_question_columns:
        connection.execute("ALTER TABLE company_test_questions ADD COLUMN difficulty TEXT DEFAULT 'Medium'")
    if "recommendation_payload" not in recommendation_columns:
        connection.execute("ALTER TABLE ai_recommendations ADD COLUMN recommendation_payload TEXT")
    for column_name, statement in missing_columns.items():
        if column_name not in existing_columns:
            connection.execute(statement)


def _seed_test_sections(connection):
    if connection.execute("SELECT COUNT(*) FROM test_sections").fetchone()[0]:
        return
    connection.executemany(
        "INSERT INTO test_sections (section_name, description, total_questions, time_limit) VALUES (?, ?, ?, ?)",
        DEFAULT_TEST_SECTIONS,
    )


def _seed_questions(connection):
    if connection.execute("SELECT COUNT(*) FROM questions").fetchone()[0]:
        return
    connection.executemany(
        "INSERT INTO questions (section_id, question_text, option_a, option_b, option_c, option_d, correct_answer, difficulty, points) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        DEFAULT_QUESTIONS,
    )


def _seed_default_users(connection):
    connection.executemany(
        "INSERT OR IGNORE INTO users (username, email, password, full_name, role, department, year, college) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        DEFAULT_USERS,
    )


def _seed_company_tests(connection):
    for seed in DEFAULT_COMPANY_TESTS:
        connection.execute("INSERT OR IGNORE INTO companies (company_name, description) VALUES (?, ?)", (seed["company_name"], seed["description"]))
        connection.execute("UPDATE companies SET description = ? WHERE company_name = ?", (seed["description"], seed["company_name"]))


def _seed_company_test_questions(connection):
    for company_key, seed in COMPANY_TEST_SEED.items():
        company = connection.execute("SELECT id FROM companies WHERE lower(company_name) = ?", (company_key.lower(),)).fetchone()
        if not company:
            continue
        for test_seed in seed["tests"]:
            company_test = connection.execute(
                "SELECT id FROM company_tests WHERE company_id = ? AND test_name = ?",
                (company["id"], test_seed["test_name"]),
            ).fetchone()
            if not company_test:
                connection.execute(
                    "INSERT INTO company_tests (company_id, test_name, total_duration, total_questions) VALUES (?, ?, ?, ?)",
                    (company["id"], test_seed["test_name"], test_seed["total_duration"], len(test_seed["questions"])),
                )
                company_test = connection.execute(
                    "SELECT id FROM company_tests WHERE company_id = ? AND test_name = ?",
                    (company["id"], test_seed["test_name"]),
                ).fetchone()
            else:
                connection.execute(
                    "UPDATE company_tests SET total_duration = ?, total_questions = ? WHERE id = ?",
                    (test_seed["total_duration"], len(test_seed["questions"]), company_test["id"]),
                )
            if connection.execute("SELECT COUNT(*) FROM company_test_questions WHERE company_test_id = ?", (company_test["id"],)).fetchone()[0]:
                continue
            total_questions = len(test_seed["questions"])
            for index, (section, question_text, options, correct_answer, explanation) in enumerate(test_seed["questions"], start=1):
                difficulty = "Easy" if index <= max(2, total_questions // 3) else ("Hard" if index > total_questions - 1 else "Medium")
                connection.execute(
                    "INSERT INTO company_test_questions (company_test_id, section, question_type, question_text, option_a, option_b, option_c, option_d, correct_answer, coding_output, difficulty, points) VALUES (?, ?, 'mcq', ?, ?, ?, ?, ?, ?, ?, ?, 1)",
                    (company_test["id"], section, question_text, options["A"], options["B"], options["C"], options["D"], correct_answer, explanation, difficulty),
                )


def get_user_by_credentials(username, password):
    return _fetch_one("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))


def create_user(username, email, password, full_name, department, year, college):
    return _execute(
        "INSERT INTO users (username, email, password, full_name, department, year, college) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (username, email, password, full_name, department, year, college),
    )


def get_topic_attempts_for_user(user_id):
    return _fetch_all("SELECT test_key, score, correct_answers, total_questions, completed_at FROM topic_test_attempts WHERE user_id = ?", (user_id,))


def get_topic_attempt(user_id, test_key):
    return _fetch_one("SELECT id, score, correct_answers, completed_at, time_taken FROM topic_test_attempts WHERE user_id = ? AND test_key = ?", (user_id, test_key))


def create_topic_attempt(user_id, test_key, topic_name, test_name, total_questions, time_taken, completed_at):
    return _execute(
        "INSERT INTO topic_test_attempts (user_id, test_key, topic_name, test_name, total_questions, time_taken, completed_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (user_id, test_key, topic_name, test_name, total_questions, time_taken, completed_at),
    )


def create_topic_response(attempt_id, question_key, selected_answer, is_correct):
    return _execute(
        "INSERT INTO topic_test_responses (attempt_id, question_key, selected_answer, is_correct) VALUES (?, ?, ?, ?)",
        (attempt_id, question_key, selected_answer, is_correct),
    )


def finalize_topic_attempt(attempt_id, score, correct_answers):
    _execute("UPDATE topic_test_attempts SET score = ?, correct_answers = ? WHERE id = ?", (score, correct_answers, attempt_id))


def get_topic_responses(attempt_id):
    return _fetch_all("SELECT question_key, selected_answer, is_correct FROM topic_test_responses WHERE attempt_id = ?", (attempt_id,))


def get_test_sections():
    return _fetch_all("SELECT * FROM test_sections ORDER BY id")


def get_questions_for_section(section_id, include_answers=False):
    if include_answers:
        return _fetch_all("SELECT id, correct_answer, points FROM questions WHERE section_id = ? ORDER BY id", (section_id,))
    return _fetch_all("SELECT id, question_text, option_a, option_b, option_c, option_d FROM questions WHERE section_id = ? ORDER BY id", (section_id,))


def create_test_attempt(user_id, section_id, total_questions, time_taken, completed_at):
    return _execute(
        "INSERT INTO test_attempts (user_id, section_id, total_questions, time_taken, completed_at) VALUES (?, ?, ?, ?, ?)",
        (user_id, section_id, total_questions, time_taken, completed_at),
    )


def create_user_response(attempt_id, question_id, selected_answer, is_correct):
    return _execute(
        "INSERT INTO user_responses (attempt_id, question_id, selected_answer, is_correct) VALUES (?, ?, ?, ?)",
        (attempt_id, question_id, selected_answer, is_correct),
    )


def finalize_test_attempt(attempt_id, score, correct_answers):
    _execute("UPDATE test_attempts SET score = ?, correct_answers = ? WHERE id = ?", (score, correct_answers, attempt_id))


def get_company_tests_for_user(user_id):
    seeded_test_names = {
        test_seed["test_name"]
        for company_seed in COMPANY_TEST_SEED.values()
        for test_seed in company_seed["tests"]
    }
    rows = _fetch_all(
        """
        SELECT ct.id, c.company_name, c.description, ct.test_name, ct.total_duration,
               COALESCE(question_counts.question_count, ct.total_questions) AS total_questions,
               latest_attempt.id AS latest_attempt_id,
               latest_attempt.score,
               latest_attempt.completed_at,
               COALESCE(attempt_counts.attempt_count, 0) AS attempt_count,
               CASE WHEN latest_attempt.id IS NULL THEN 0 ELSE 1 END AS attempted
        FROM company_tests ct
        JOIN companies c ON ct.company_id = c.id
        LEFT JOIN (
            SELECT company_test_id, COUNT(*) AS question_count
            FROM company_test_questions
            GROUP BY company_test_id
        ) question_counts ON question_counts.company_test_id = ct.id
        LEFT JOIN (
            SELECT company_test_id, COUNT(*) AS attempt_count
            FROM company_test_attempts
            WHERE user_id = ?
            GROUP BY company_test_id
        ) attempt_counts ON attempt_counts.company_test_id = ct.id
        LEFT JOIN company_test_attempts latest_attempt ON latest_attempt.id = (
            SELECT cta2.id
            FROM company_test_attempts cta2
            WHERE cta2.user_id = ? AND cta2.company_test_id = ct.id
            ORDER BY cta2.completed_at DESC, cta2.id DESC
            LIMIT 1
        )
        ORDER BY c.company_name, ct.test_name
        """,
        (user_id, user_id),
    )
    return [row for row in rows if row["test_name"] in seeded_test_names]


def get_company_test_attempt(user_id, company_test_id):
    return _fetch_one(
        "SELECT id, score, completed_at, time_taken FROM company_test_attempts WHERE user_id = ? AND company_test_id = ? ORDER BY completed_at DESC, id DESC LIMIT 1",
        (user_id, company_test_id),
    )


def get_company_test_attempt_by_id(user_id, company_test_id, attempt_id):
    return _fetch_one(
        "SELECT id, score, completed_at, time_taken FROM company_test_attempts WHERE user_id = ? AND company_test_id = ? AND id = ?",
        (user_id, company_test_id, attempt_id),
    )


def get_company_test(company_test_id):
    return _fetch_one(
        "SELECT ct.id, ct.test_name, ct.total_duration, c.company_name FROM company_tests ct JOIN companies c ON ct.company_id = c.id WHERE ct.id = ?",
        (company_test_id,),
    )


def get_company_test_questions(company_test_id, include_answers=False):
    if include_answers:
        return _fetch_all(
            "SELECT id, section, question_text, option_a, option_b, option_c, option_d, correct_answer, coding_output, difficulty, points FROM company_test_questions WHERE company_test_id = ? ORDER BY id",
            (company_test_id,),
        )
    return _fetch_all(
        "SELECT id, section, question_text, option_a, option_b, option_c, option_d, difficulty FROM company_test_questions WHERE company_test_id = ? ORDER BY id",
        (company_test_id,),
    )


def create_company_test_attempt(user_id, company_test_id, time_taken, completed_at):
    return _execute(
        "INSERT INTO company_test_attempts (user_id, company_test_id, time_taken, completed_at) VALUES (?, ?, ?, ?)",
        (user_id, company_test_id, time_taken, completed_at),
    )


def create_company_test_response(attempt_id, question_id, selected_answer, is_correct):
    return _execute(
        "INSERT INTO company_test_responses (attempt_id, question_id, selected_answer, is_correct) VALUES (?, ?, ?, ?)",
        (attempt_id, question_id, selected_answer, is_correct),
    )


def finalize_company_test_attempt(attempt_id, score):
    _execute("UPDATE company_test_attempts SET score = ? WHERE id = ?", (score, attempt_id))


def get_company_test_responses(attempt_id):
    return _fetch_all("SELECT question_id, selected_answer, is_correct FROM company_test_responses WHERE attempt_id = ?", (attempt_id,))


def get_user_scores(user_id):
    return _fetch_all(
        """
        SELECT ta.score, ta.correct_answers, ta.total_questions, ta.completed_at, ts.section_name
        FROM test_attempts ta
        JOIN test_sections ts ON ta.section_id = ts.id
        WHERE ta.user_id = ?
        UNION ALL
        SELECT tta.score, tta.correct_answers, tta.total_questions, tta.completed_at,
               tta.topic_name || ' - ' || tta.test_name AS section_name
        FROM topic_test_attempts tta
        WHERE tta.user_id = ?
        UNION ALL
        SELECT cta.score,
               COALESCE(correct_counts.correct_answers, 0) AS correct_answers,
               COALESCE(question_counts.total_questions, 0) AS total_questions,
               cta.completed_at,
               c.company_name || ' - ' || ct.test_name AS section_name
        FROM company_test_attempts cta
        JOIN company_tests ct ON cta.company_test_id = ct.id
        JOIN companies c ON ct.company_id = c.id
        LEFT JOIN (
            SELECT ctr.attempt_id, COUNT(*) AS correct_answers
            FROM company_test_responses ctr
            WHERE ctr.is_correct = 1
            GROUP BY ctr.attempt_id
        ) correct_counts ON correct_counts.attempt_id = cta.id
        LEFT JOIN (
            SELECT company_test_id, COUNT(*) AS total_questions
            FROM company_test_questions
            GROUP BY company_test_id
        ) question_counts ON question_counts.company_test_id = ct.id
        WHERE cta.user_id = ?
        ORDER BY completed_at DESC
        """,
        (user_id, user_id, user_id),
    )


def get_section_performance(user_id):
    return _fetch_all(
        """
        SELECT section_name, AVG(score) AS avg_score, COUNT(*) AS attempts
        FROM (
            SELECT ts.section_name AS section_name, ta.score AS score
            FROM test_attempts ta
            JOIN test_sections ts ON ta.section_id = ts.id
            WHERE ta.user_id = ?
            UNION ALL
            SELECT tta.topic_name AS section_name, tta.score AS score
            FROM topic_test_attempts tta
            WHERE tta.user_id = ?
            UNION ALL
            SELECT c.company_name || ' Company Tests' AS section_name, cta.score AS score
            FROM company_test_attempts cta
            JOIN company_tests ct ON cta.company_test_id = ct.id
            JOIN companies c ON ct.company_id = c.id
            WHERE cta.user_id = ?
        ) combined_scores
        GROUP BY section_name
        """,
        (user_id, user_id, user_id),
    )


def get_recommendation_performance(user_id):
    return _fetch_all(
        """
        SELECT source_type, topic_name, test_name, section_name, category_name, difficulty, is_correct, score, completed_at
        FROM (
            SELECT
                'topic' AS source_type,
                tta.topic_name AS topic_name,
                tta.test_name AS test_name,
                tta.topic_name AS section_name,
                ttr.question_key AS category_name,
                NULL AS difficulty,
                CAST(ttr.is_correct AS INTEGER) AS is_correct,
                tta.score AS score,
                tta.completed_at AS completed_at
            FROM topic_test_attempts tta
            JOIN topic_test_responses ttr ON ttr.attempt_id = tta.id
            WHERE tta.user_id = ?
            UNION ALL
            SELECT
                'company' AS source_type,
                c.company_name AS topic_name,
                ct.test_name AS test_name,
                c.company_name AS section_name,
                ctq.section AS category_name,
                COALESCE(ctq.difficulty, 'Medium') AS difficulty,
                CAST(ctr.is_correct AS INTEGER) AS is_correct,
                cta.score AS score,
                cta.completed_at AS completed_at
            FROM company_test_attempts cta
            JOIN company_tests ct ON cta.company_test_id = ct.id
            JOIN companies c ON ct.company_id = c.id
            JOIN company_test_responses ctr ON ctr.attempt_id = cta.id
            JOIN company_test_questions ctq ON ctq.id = ctr.question_id
            WHERE cta.user_id = ?
        ) detailed_rows
        ORDER BY completed_at DESC
        """,
        (user_id, user_id),
    )


def save_ai_recommendation(user_id, weak_sections, improvement_areas, practice_focus, readiness_score, recommendation_payload=None):
    return _execute(
        "INSERT INTO ai_recommendations (user_id, weak_sections, improvement_areas, practice_focus, readiness_score, recommendation_payload) VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, weak_sections, improvement_areas, practice_focus, readiness_score, recommendation_payload),
    )


def get_latest_ai_recommendation(user_id):
    return _fetch_one("SELECT * FROM ai_recommendations WHERE user_id = ? ORDER BY generated_at DESC LIMIT 1", (user_id,))


def get_admin_students():
    return _fetch_all(
        """
        SELECT u.*, AVG(ta.score) AS avg_score, COUNT(DISTINCT ta.section_id) AS sections_attempted
        FROM users u
        LEFT JOIN test_attempts ta ON u.id = ta.user_id
        WHERE u.role = 'student'
        GROUP BY u.id
        ORDER BY u.id
        """
    )


def get_admin_department_stats():
    return _fetch_all(
        """
        SELECT u.department, COUNT(DISTINCT u.id) AS student_count, AVG(ta.score) AS avg_score, COUNT(ta.id) AS total_attempts
        FROM users u
        LEFT JOIN test_attempts ta ON u.id = ta.user_id
        WHERE u.role = 'student' AND u.department IS NOT NULL
        GROUP BY u.department
        ORDER BY u.department
        """
    )


def get_resume_for_user(user_id):
    return _fetch_one("SELECT * FROM resumes WHERE user_id = ?", (user_id,))


def upsert_resume_for_user(user_id, resume_data, scores):
    existing = get_resume_for_user(user_id)
    params = (
        resume_data.get("full_name"),
        resume_data.get("email"),
        resume_data.get("phone"),
        resume_data.get("education"),
        resume_data.get("skills"),
        resume_data.get("experience"),
        resume_data.get("projects"),
        resume_data.get("certifications"),
        resume_data.get("target_company"),
        resume_data.get("target_role"),
        resume_data.get("job_description"),
        resume_data.get("resume_text"),
        scores["ats_score"],
        scores["keyword_score"],
        scores["format_score"],
        scores["overall_score"],
        scores["feedback"],
    )
    if existing:
        _execute(
            "UPDATE resumes SET full_name = ?, email = ?, phone = ?, education = ?, skills = ?, experience = ?, projects = ?, certifications = ?, target_company = ?, target_role = ?, job_description = ?, resume_text = ?, ats_score = ?, keyword_score = ?, format_score = ?, overall_score = ?, feedback = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?",
            params + (user_id,),
        )
        return existing["id"]
    return _execute(
        "INSERT INTO resumes (user_id, full_name, email, phone, education, skills, experience, projects, certifications, target_company, target_role, job_description, resume_text, ats_score, keyword_score, format_score, overall_score, feedback) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (user_id,) + params,
    )


def save_resume_ai_suggestions(user_id, resume_text, job_description_text, suggestions_payload, source):
    existing = get_resume_for_user(user_id)
    if existing:
        _execute(
            "UPDATE resumes SET resume_text = COALESCE(?, resume_text), job_description = COALESCE(?, job_description), ai_suggestions_payload = ?, ai_suggestions_source = ?, ai_suggestions_updated_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?",
            (resume_text, job_description_text, suggestions_payload, source, user_id),
        )
        return existing["id"]
    return _execute(
        "INSERT INTO resumes (user_id, job_description, resume_text, ai_suggestions_payload, ai_suggestions_source, ai_suggestions_updated_at) VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)",
        (user_id, job_description_text, resume_text, suggestions_payload, source),
    )


def reset_demo_data():
    connection = get_db()
    deleted_rows = {}
    protected_users = ("admin", "student1")
    protected_query = "SELECT id FROM users WHERE username IN (?, ?)"
    try:
        connection.execute("BEGIN")
        cursor = connection.execute(f"DELETE FROM user_responses WHERE attempt_id IN (SELECT id FROM test_attempts WHERE user_id NOT IN ({protected_query}))", protected_users)
        deleted_rows["user_responses"] = cursor.rowcount
        cursor = connection.execute(f"DELETE FROM company_test_responses WHERE attempt_id IN (SELECT id FROM company_test_attempts WHERE user_id NOT IN ({protected_query}))", protected_users)
        deleted_rows["company_test_responses"] = cursor.rowcount
        cursor = connection.execute(f"DELETE FROM test_attempts WHERE user_id NOT IN ({protected_query})", protected_users)
        deleted_rows["test_attempts"] = cursor.rowcount
        cursor = connection.execute(f"DELETE FROM company_test_attempts WHERE user_id NOT IN ({protected_query})", protected_users)
        deleted_rows["company_test_attempts"] = cursor.rowcount
        cursor = connection.execute(f"DELETE FROM resumes WHERE user_id NOT IN ({protected_query})", protected_users)
        deleted_rows["resumes"] = cursor.rowcount
        cursor = connection.execute(f"DELETE FROM ai_recommendations WHERE user_id NOT IN ({protected_query})", protected_users)
        deleted_rows["ai_recommendations"] = cursor.rowcount
        connection.commit()
        return deleted_rows
    except Exception:
        connection.rollback()
        raise
