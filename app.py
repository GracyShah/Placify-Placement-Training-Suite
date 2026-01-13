# PLACIFY - AI-Powered Placement Readiness Platform
# Flask Backend Server

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import sqlite3
########
import pyodbc

conn = pyodbc.connect(
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=localhost;"
    "Database=PlacifyDB;"
    "Trusted_Connection=yes;"
)

cursor = conn.cursor()
cursor.execute("SELECT * FROM Users")
print(cursor.fetchall())

#########

import json
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'placify-secret-key-change-in-production'

# Database configuration
DATABASE = 'database.db'

# Initialize database
def init_db():
    """Initialize database with schema"""
    if not os.path.exists(DATABASE):
        conn = sqlite3.connect(DATABASE)
        with open('sql/schema.sql', 'r') as f:
            conn.executescript(f.read())
        conn.commit()
        conn.close()
        print("Database initialized successfully!")

# Database helper functions
def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def query_db(query, args=(), one=False):
    """Execute SELECT query"""
    conn = get_db()
    cur = conn.execute(query, args)
    rv = cur.fetchall()
    conn.close()
    return (rv[0] if rv else None) if one else rv

def execute_db(query, args=()):
    """Execute INSERT/UPDATE/DELETE query"""
    conn = get_db()
    cur = conn.execute(query, args)
    conn.commit()
    last_id = cur.lastrowid
    conn.close()
    return last_id

# ========== ROUTES ==========

@app.route('/')
def index():
    """Landing page"""
    return render_template('index.html')

@app.route('/login')
def login_page():
    """Login page"""
    return render_template('login.html')

@app.route('/student')
def student_page():
    """Student dashboard page"""
    if 'user_id' not in session or session.get('role') != 'student':
        return redirect(url_for('login_page'))
    return render_template('student.html')

@app.route('/admin')
def admin_page():
    """Admin dashboard page"""
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login_page'))
    return render_template('admin.html')

@app.route('/tests')
def tests_page():
    """Tests page"""
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('tests.html')

@app.route('/dashboard')
def dashboard_page():
    """Dashboard page"""
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('dashboard.html')

@app.route('/resume')
def resume_page():
    """Resume builder page"""
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('resume.html')

# ========== API ENDPOINTS ==========

@app.route('/api/login', methods=['POST'])
def api_login():
    """Login API"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user = query_db('SELECT * FROM users WHERE username = ? AND password = ?',
                    [username, password], one=True)
    
    if user:
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['role'] = user['role']
        session['full_name'] = user['full_name']
        
        return jsonify({
            'success': True,
            'role': user['role'],
            'redirect': '/student' if user['role'] == 'student' else '/admin'
        })
    else:
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@app.route('/api/register', methods=['POST'])
def api_register():
    """Register new student"""
    data = request.get_json()
    
    try:
        execute_db('''INSERT INTO users (username, email, password, full_name, department, year, college)
                      VALUES (?, ?, ?, ?, ?, ?, ?)''',
                   [data.get('username'), data.get('email'), data.get('password'),
                    data.get('full_name'), data.get('department'), data.get('year'),
                    data.get('college', 'Placify College')])
        return jsonify({'success': True, 'message': 'Registration successful'})
    except sqlite3.IntegrityError:
        return jsonify({'success': False, 'message': 'Username or email already exists'}), 400

@app.route('/api/logout', methods=['POST'])
def api_logout():
    """Logout API"""
    session.clear()
    return jsonify({'success': True})

@app.route('/api/test_sections', methods=['GET'])
def api_test_sections():
    """Get all test sections"""
    sections = query_db('SELECT * FROM test_sections')
    return jsonify([dict(row) for row in sections])

@app.route('/api/questions/<int:section_id>', methods=['GET'])
def api_questions(section_id):
    """Get questions for a section"""
    questions = query_db('SELECT id, question_text, option_a, option_b, option_c, option_d FROM questions WHERE section_id = ?',
                         [section_id])
    return jsonify([dict(row) for row in questions])

@app.route('/api/submit_test', methods=['POST'])
def api_submit_test():
    """Submit test and calculate score"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    data = request.get_json()
    section_id = data.get('section_id')
    answers = data.get('answers')  # {question_id: selected_answer}
    time_taken = data.get('time_taken', 0)
    
    # Get correct answers
    questions = query_db('SELECT id, correct_answer, points FROM questions WHERE section_id = ?',
                         [section_id])
    
    correct_count = 0
    total_points = 0
    earned_points = 0
    
    # Create test attempt
    attempt_id = execute_db('''INSERT INTO test_attempts (user_id, section_id, total_questions, time_taken)
                               VALUES (?, ?, ?, ?)''',
                            [session['user_id'], section_id, len(questions), time_taken])
    
    # Check answers
    for question in questions:
        q_id = question['id']
        correct_ans = question['correct_answer']
        points = question['points']
        total_points += points
        
        selected_ans = answers.get(str(q_id), '')
        is_correct = selected_ans.upper() == correct_ans.upper()
        
        if is_correct:
            correct_count += 1
            earned_points += points
        
        # Store user response
        execute_db('''INSERT INTO user_responses (attempt_id, question_id, selected_answer, is_correct)
                      VALUES (?, ?, ?, ?)''',
                   [attempt_id, q_id, selected_ans, is_correct])
    
    # Calculate percentage score
    score = (earned_points / total_points * 100) if total_points > 0 else 0
    
    # Update attempt with score
    execute_db('UPDATE test_attempts SET score = ?, correct_answers = ? WHERE id = ?',
               [score, correct_count, attempt_id])
    
    # Generate AI recommendations after test
    generate_ai_recommendations(session['user_id'])
    
    return jsonify({
        'success': True,
        'score': round(score, 2),
        'correct': correct_count,
        'total': len(questions),
        'attempt_id': attempt_id
    })

@app.route('/api/user_scores', methods=['GET'])
def api_user_scores():
    """Get user's test scores"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    scores = query_db('''SELECT ta.*, ts.section_name 
                         FROM test_attempts ta
                         JOIN test_sections ts ON ta.section_id = ts.id
                         WHERE ta.user_id = ?
                         ORDER BY ta.completed_at DESC''',
                      [session['user_id']])
    
    return jsonify([dict(row) for row in scores])

@app.route('/api/section_performance', methods=['GET'])
def api_section_performance():
    """Get section-wise performance"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    performance = query_db('''SELECT ts.section_name, 
                             AVG(ta.score) as avg_score,
                             COUNT(ta.id) as attempts
                             FROM test_attempts ta
                             JOIN test_sections ts ON ta.section_id = ts.id
                             WHERE ta.user_id = ?
                             GROUP BY ts.section_name''',
                           [session['user_id']])
    
    return jsonify([dict(row) for row in performance])

from flask import request, jsonify

@app.route("/api/save_resume", methods=["POST"])
def save_resume():
    data = request.json

    # Simple ATS scoring logic (demo)
    score = 0
    suggestions = []

    if len(data.get("skills", "")) > 30:
        score += 25
    else:
        suggestions.append("Add more technical and soft skills.")

    if len(data.get("projects", "")) > 30:
        score += 25
    else:
        suggestions.append("Add more detailed project descriptions.")

    if len(data.get("education", "")) > 20:
        score += 20
    else:
        suggestions.append("Education section needs more clarity.")

    if data.get("experience"):
        score += 15
    else:
        suggestions.append("Add internships or work experience.")

    if data.get("certifications"):
        score += 15
    else:
        suggestions.append("Add relevant certifications.")

    result = {
        "success": True,
        "scores": {
            "ats_score": score,
            "suggestions": suggestions
        }
    }

    return jsonify(result)

@app.route('/api/save_resume', methods=['POST'])
def api_save_resume():
    """Save resume and calculate score"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    data = request.get_json()
    user_id = session['user_id']
    
    # Build resume text
    resume_text = f"{data.get('full_name', '')}\n{data.get('email', '')}\n{data.get('phone', '')}\n"
    resume_text += f"Education: {data.get('education', '')}\n"
    resume_text += f"Skills: {data.get('skills', '')}\n"
    resume_text += f"Experience: {data.get('experience', '')}\n"
    resume_text += f"Projects: {data.get('projects', '')}\n"
    resume_text += f"Certifications: {data.get('certifications', '')}"
    
    # Calculate resume scores
    scores = calculate_resume_score(data)
    
    # Check if resume exists
    existing = query_db('SELECT id FROM resumes WHERE user_id = ?', [user_id], one=True)
    
    if existing:
        # Update existing resume
        execute_db('''UPDATE resumes SET full_name=?, email=?, phone=?, education=?, skills=?,
                      experience=?, projects=?, certifications=?, resume_text=?,
                      ats_score=?, keyword_score=?, format_score=?, overall_score=?, feedback=?,
                      updated_at=CURRENT_TIMESTAMP
                      WHERE user_id=?''',
                   [data.get('full_name'), data.get('email'), data.get('phone'),
                    data.get('education'), data.get('skills'), data.get('experience'),
                    data.get('projects'), data.get('certifications'), resume_text,
                    scores['ats_score'], scores['keyword_score'], scores['format_score'],
                    scores['overall_score'], scores['feedback'], user_id])
    else:
        # Insert new resume
        execute_db('''INSERT INTO resumes (user_id, full_name, email, phone, education, skills,
                      experience, projects, certifications, resume_text,
                      ats_score, keyword_score, format_score, overall_score, feedback)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                   [user_id, data.get('full_name'), data.get('email'), data.get('phone'),
                    data.get('education'), data.get('skills'), data.get('experience'),
                    data.get('projects'), data.get('certifications'), resume_text,
                    scores['ats_score'], scores['keyword_score'], scores['format_score'],
                    scores['overall_score'], scores['feedback']])
    
    return jsonify({'success': True, 'scores': scores})

@app.route('/api/get_resume', methods=['GET'])
def api_get_resume():
    """Get user's resume"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    resume = query_db('SELECT * FROM resumes WHERE user_id = ?', [session['user_id']], one=True)
    
    if resume:
        return jsonify(dict(resume))
    else:
        return jsonify({'success': False, 'message': 'No resume found'}), 404

@app.route('/api/ai_recommendations', methods=['GET'])
def api_ai_recommendations():
    """Get AI-based recommendations"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    recommendations = query_db('SELECT * FROM ai_recommendations WHERE user_id = ? ORDER BY generated_at DESC LIMIT 1',
                               [session['user_id']], one=True)
    
    if recommendations:
        return jsonify(dict(recommendations))
    else:
        # Generate if not exists
        generate_ai_recommendations(session['user_id'])
        recommendations = query_db('SELECT * FROM ai_recommendations WHERE user_id = ? ORDER BY generated_at DESC LIMIT 1',
                                   [session['user_id']], one=True)
        return jsonify(dict(recommendations) if recommendations else {})

@app.route('/api/admin/students', methods=['GET'])
def api_admin_students():
    """Get all students (admin only)"""
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    students = query_db('''SELECT u.*, 
                          AVG(ta.score) as avg_score,
                          COUNT(DISTINCT ta.section_id) as sections_attempted
                          FROM users u
                          LEFT JOIN test_attempts ta ON u.id = ta.user_id
                          WHERE u.role = 'student'
                          GROUP BY u.id''')
    
    return jsonify([dict(row) for row in students])

@app.route('/api/admin/department_stats', methods=['GET'])
def api_admin_department_stats():
    """Get department-wise statistics (admin only)"""
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    stats = query_db('''SELECT u.department, 
                       COUNT(DISTINCT u.id) as student_count,
                       AVG(ta.score) as avg_score,
                       COUNT(ta.id) as total_attempts
                       FROM users u
                       LEFT JOIN test_attempts ta ON u.id = ta.user_id
                       WHERE u.role = 'student' AND u.department IS NOT NULL
                       GROUP BY u.department''')
    
    return jsonify([dict(row) for row in stats])

@app.route('/api/user_info', methods=['GET'])
def api_user_info():
    """Get current user info"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    return jsonify({
        'user_id': session['user_id'],
        'username': session['username'],
        'full_name': session['full_name'],
        'role': session['role']
    })

# ========== HELPER FUNCTIONS ==========

def calculate_resume_score(resume_data):
    """Calculate resume scores using rule-based AI"""
    
    # ATS Score - Check for key sections
    ats_score = 0
    if resume_data.get('full_name'): ats_score += 15
    if resume_data.get('email'): ats_score += 10
    if resume_data.get('phone'): ats_score += 10
    if resume_data.get('education'): ats_score += 20
    if resume_data.get('skills'): ats_score += 20
    if resume_data.get('experience') or resume_data.get('projects'): ats_score += 25
    
    # Keyword Score - Check for important keywords
    keyword_score = 0
    skills_text = (resume_data.get('skills', '') + ' ' + 
                   resume_data.get('experience', '') + ' ' + 
                   resume_data.get('projects', '')).lower()
    
    important_keywords = ['python', 'java', 'javascript', 'react', 'sql', 'database',
                         'api', 'git', 'team', 'project', 'leadership', 'communication',
                         'problem solving', 'agile', 'development']
    
    for keyword in important_keywords:
        if keyword in skills_text:
            keyword_score += 100 / len(important_keywords)
    
    # Format Score - Check text length and structure
    format_score = 0
    total_length = sum([len(str(resume_data.get(key, ''))) for key in 
                       ['education', 'skills', 'experience', 'projects', 'certifications']])
    
    if total_length > 100: format_score += 40
    if total_length > 300: format_score += 30
    if total_length > 500: format_score += 30
    
    # Overall score
    overall_score = (ats_score + keyword_score + format_score) / 3
    
    # Generate feedback
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
        'ats_score': round(ats_score, 2),
        'keyword_score': round(keyword_score, 2),
        'format_score': round(format_score, 2),
        'overall_score': round(overall_score, 2),
        'feedback': ' '.join(feedback)
    }

def generate_ai_recommendations(user_id):
    """Generate AI-based recommendations for user"""
    
    # Get user's performance
    performance = query_db('''SELECT ts.section_name, AVG(ta.score) as avg_score
                             FROM test_attempts ta
                             JOIN test_sections ts ON ta.section_id = ts.id
                             WHERE ta.user_id = ?
                             GROUP BY ts.section_name''',
                           [user_id])
    
    weak_sections = []
    improvement_areas = []
    overall_avg = 0
    
    if performance:
        scores = [row['avg_score'] for row in performance]
        overall_avg = sum(scores) / len(scores) if scores else 0
        
        # Identify weak sections (below 60%)
        for row in performance:
            if row['avg_score'] < 60:
                weak_sections.append(row['section_name'])
                
                # Add specific improvement suggestions
                if row['section_name'] == 'Aptitude':
                    improvement_areas.append("Practice more quantitative problems and speed calculations")
                elif row['section_name'] == 'Logical Reasoning':
                    improvement_areas.append("Work on pattern recognition and logical puzzles")
                elif row['section_name'] == 'Coding':
                    improvement_areas.append("Focus on data structures and algorithms")
                elif row['section_name'] == 'HR & Soft Skills':
                    improvement_areas.append("Improve communication and behavioral interview skills")
                elif row['section_name'] == 'Domain Knowledge':
                    improvement_areas.append("Study core technical concepts and fundamentals")
    
    # Practice focus recommendations
    if overall_avg < 50:
        practice_focus = "Focus on fundamentals across all sections. Take more practice tests."
    elif overall_avg < 70:
        practice_focus = "Good progress! Concentrate on weak areas and time management."
    else:
        practice_focus = "Excellent performance! Maintain consistency and polish advanced topics."
    
    # Readiness score
    readiness_score = min(overall_avg + 10, 100)  # Bonus points for attempt
    
    # Store recommendations
    execute_db('''INSERT INTO ai_recommendations 
                  (user_id, weak_sections, improvement_areas, practice_focus, readiness_score)
                  VALUES (?, ?, ?, ?, ?)''',
               [user_id, json.dumps(weak_sections), json.dumps(improvement_areas),
                practice_focus, readiness_score])
    
    return True

# ========== MAIN ==========

if __name__ == '__main__':
    init_db()
    print("=" * 50)
    print("PLACIFY - Placement Readiness Platform")
    print("=" * 50)
    print("\nServer starting at http://127.0.0.1:5000")
    print("\nDefault Login Credentials:")
    print("Admin - Username: admin, Password: admin123")
    print("Student - Username: student1, Password: student123")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)
