-- PLACIFY Database Schema
-- SQL Schema for placement readiness platform

-- Users table (students and admins)
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    full_name VARCHAR(150) NOT NULL,
    role VARCHAR(20) DEFAULT 'student', -- 'student' or 'admin'
    department VARCHAR(100),
    year INTEGER,
    college VARCHAR(150),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Test sections table
CREATE TABLE IF NOT EXISTS test_sections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    section_name VARCHAR(100) NOT NULL,
    description TEXT,
    total_questions INTEGER DEFAULT 10,
    time_limit INTEGER DEFAULT 30 -- in minutes
);

-- Questions table
CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    section_id INTEGER NOT NULL,
    question_text TEXT NOT NULL,
    option_a TEXT NOT NULL,
    option_b TEXT NOT NULL,
    option_c TEXT NOT NULL,
    option_d TEXT NOT NULL,
    correct_answer CHAR(1) NOT NULL, -- 'A', 'B', 'C', or 'D'
    difficulty VARCHAR(20) DEFAULT 'medium', -- 'easy', 'medium', 'hard'
    points INTEGER DEFAULT 1,
    FOREIGN KEY (section_id) REFERENCES test_sections(id)
);

-- Test attempts table
CREATE TABLE IF NOT EXISTS test_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    section_id INTEGER NOT NULL,
    score DECIMAL(5,2) DEFAULT 0,
    total_questions INTEGER NOT NULL,
    correct_answers INTEGER DEFAULT 0,
    time_taken INTEGER, -- in seconds
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (section_id) REFERENCES test_sections(id)
);

-- User responses table
CREATE TABLE IF NOT EXISTS user_responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    attempt_id INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    selected_answer CHAR(1), -- 'A', 'B', 'C', or 'D'
    is_correct BOOLEAN DEFAULT 0,
    FOREIGN KEY (attempt_id) REFERENCES test_attempts(id),
    FOREIGN KEY (question_id) REFERENCES questions(id)
);

-- Resumes table
CREATE TABLE IF NOT EXISTS resumes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    full_name VARCHAR(150),
    email VARCHAR(150),
    phone VARCHAR(20),
    education TEXT,
    skills TEXT,
    experience TEXT,
    projects TEXT,
    certifications TEXT,
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

-- AI Recommendations table
CREATE TABLE IF NOT EXISTS ai_recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    weak_sections TEXT, -- JSON array of weak sections
    improvement_areas TEXT,
    practice_focus TEXT,
    readiness_score DECIMAL(5,2) DEFAULT 0,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Insert default test sections
INSERT INTO test_sections (section_name, description, total_questions, time_limit) VALUES
('Aptitude', 'Quantitative and analytical reasoning', 15, 20),
('Logical Reasoning', 'Pattern recognition and logical thinking', 15, 20),
('Coding', 'Programming concepts and problem solving', 10, 30),
('HR & Soft Skills', 'Communication and behavioral questions', 10, 15),
('Domain Knowledge', 'Technical domain specific questions', 10, 20);

-- Insert sample questions for Aptitude
INSERT INTO questions (section_id, question_text, option_a, option_b, option_c, option_d, correct_answer, difficulty) VALUES
(1, 'If a train travels 60 km in 1 hour, how far will it travel in 3.5 hours at the same speed?', '180 km', '210 km', '240 km', '200 km', 'B', 'easy'),
(1, 'What is 15% of 200?', '25', '30', '35', '40', 'B', 'easy'),
(1, 'A shopkeeper marks up the price by 20% and gives 10% discount. What is the net profit percentage?', '8%', '10%', '12%', '15%', 'A', 'medium'),
(1, 'If 5 workers can complete a task in 12 days, how many days will 6 workers take?', '10 days', '9 days', '15 days', '8 days', 'A', 'medium'),
(1, 'The average of 5 numbers is 27. If one number is excluded, the average becomes 25. What is the excluded number?', '35', '37', '33', '39', 'A', 'hard');

-- Insert sample questions for Logical Reasoning
INSERT INTO questions (section_id, question_text, option_a, option_b, option_c, option_d, correct_answer, difficulty) VALUES
(2, 'Complete the series: 2, 6, 12, 20, 30, ?', '40', '42', '44', '46', 'B', 'medium'),
(2, 'If all roses are flowers and some flowers are red, can we conclude all roses are red?', 'Yes', 'No', 'Cannot determine', 'Insufficient data', 'B', 'easy'),
(2, 'Find the odd one out: Dog, Cat, Tiger, Chair', 'Dog', 'Cat', 'Tiger', 'Chair', 'D', 'easy'),
(2, 'If A is to the north of B and B is to the west of C, where is C with respect to A?', 'South-East', 'North-East', 'South-West', 'North-West', 'A', 'medium'),
(2, 'A cube is painted red on all faces. It is cut into 64 smaller cubes. How many cubes have no face painted?', '8', '16', '24', '32', 'A', 'hard');

-- Insert sample questions for Coding
INSERT INTO questions (section_id, question_text, option_a, option_b, option_c, option_d, correct_answer, difficulty) VALUES
(3, 'What is the time complexity of binary search?', 'O(n)', 'O(log n)', 'O(n log n)', 'O(1)', 'B', 'easy'),
(3, 'Which data structure uses LIFO principle?', 'Queue', 'Stack', 'Array', 'Linked List', 'B', 'easy'),
(3, 'What will be the output of: print(2 ** 3)?', '5', '6', '8', '9', 'C', 'easy'),
(3, 'Which sorting algorithm has best case time complexity of O(n)?', 'Bubble Sort', 'Merge Sort', 'Quick Sort', 'Insertion Sort', 'D', 'medium'),
(3, 'What is the space complexity of recursive fibonacci?', 'O(1)', 'O(n)', 'O(log n)', 'O(n^2)', 'B', 'hard');

-- Insert sample questions for HR & Soft Skills
INSERT INTO questions (section_id, question_text, option_a, option_b, option_c, option_d, correct_answer, difficulty) VALUES
(4, 'What does STAR method stand for in interviews?', 'Start, Tell, Act, Result', 'Situation, Task, Action, Result', 'Skills, Teamwork, Attitude, Response', 'Story, Task, Answer, Reason', 'B', 'easy'),
(4, 'Which is the best answer to "What is your weakness?"', 'I have no weakness', 'I work too hard', 'I am improving my public speaking', 'I am perfect', 'C', 'medium'),
(4, 'What is active listening?', 'Hearing words only', 'Fully concentrating and responding', 'Waiting to speak', 'Interrupting to clarify', 'B', 'easy'),
(4, 'Best way to handle workplace conflict?', 'Avoid the person', 'Communicate openly and professionally', 'Complain to others', 'Ignore it', 'B', 'easy'),
(4, 'What is emotional intelligence?', 'IQ level', 'Ability to understand and manage emotions', 'Being emotional', 'Avoiding feelings', 'B', 'medium');

-- Insert sample questions for Domain Knowledge
INSERT INTO questions (section_id, question_text, option_a, option_b, option_c, option_d, correct_answer, difficulty) VALUES
(5, 'What does HTTP stand for?', 'HyperText Transfer Protocol', 'High Transfer Text Protocol', 'HyperText Transport Protocol', 'High Tech Transfer Protocol', 'A', 'easy'),
(5, 'Which is a relational database?', 'MongoDB', 'PostgreSQL', 'Redis', 'Cassandra', 'B', 'easy'),
(5, 'What is an API?', 'A programming language', 'Application Programming Interface', 'A database', 'A server', 'B', 'easy'),
(5, 'What is the purpose of a PRIMARY KEY?', 'To sort data', 'To uniquely identify records', 'To encrypt data', 'To backup data', 'B', 'medium'),
(5, 'What is REST in web services?', 'A database', 'Representational State Transfer', 'A programming language', 'A server type', 'B', 'medium');

-- Insert default admin user (password: admin123)
-- Password should be hashed in production!
INSERT INTO users (username, email, password, full_name, role, department, college) VALUES
('admin', 'admin@placify.com', 'admin123', 'Admin User', 'admin', 'Administration', 'Placify College');

-- Insert sample student user (password: student123)
INSERT INTO users (username, email, password, full_name, role, department, year, college) VALUES
('student1', 'student1@college.com', 'student123', 'John Doe', 'student', 'Computer Science', 3, 'Placify College');
