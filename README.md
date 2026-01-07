# PLACIFY - AI-Powered Placement Readiness Platform

A complete full-stack web application built with HTML, CSS, JavaScript, Python (Flask), and SQL for helping college students prepare for campus placements.

## Features

- **Section-wise Mock Tests**: Aptitude, Logical Reasoning, Coding, HR Skills, Domain Knowledge
- **Performance Analytics**: Track progress with detailed section-wise scores and visual graphs
- **Resume Builder**: Create resumes with ATS score checker and keyword analysis
- **AI Recommendations**: Get personalized improvement suggestions based on performance
- **Student Dashboard**: Complete placement readiness profile with scores and history
- **Admin Dashboard**: Department-wise statistics and student readiness reports

## Tech Stack

- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Backend**: Python Flask
- **Database**: SQLite (MySQL compatible)
- **Design**: Dark mode UI with neon cyan & purple theme

## Project Structure

\`\`\`
placify/
├── app.py                  # Flask backend server
├── database.db            # SQLite database (auto-generated)
├── requirements.txt       # Python dependencies
├── README.md             # Documentation
├── sql/
│   └── schema.sql        # Database schema
├── static/
│   ├── css/
│   │   └── style.css     # All styles
│   └── js/
│       └── app.js        # Frontend JavaScript logic
└── templates/
    ├── index.html        # Landing page
    ├── login.html        # Login/Register page
    ├── student.html      # Student dashboard
    ├── admin.html        # Admin dashboard
    ├── tests.html        # Test taking page
    ├── dashboard.html    # Performance analytics
    └── resume.html       # Resume builder
\`\`\`

## Installation & Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Steps

1. **Install Dependencies**

\`\`\`bash
pip install -r requirements.txt
\`\`\`

2. **Run the Application**

\`\`\`bash
python app.py
\`\`\`

3. **Open in Browser**

Navigate to: `http://127.0.0.1:5000`

## Default Login Credentials

### Admin Account
- Username: `admin`
- Password: `admin123`

### Student Account
- Username: `student1`
- Password: `student123`

## Database

The application uses SQLite database which is automatically initialized on first run with:
- Pre-populated test sections
- Sample questions for all sections
- Default admin and student users

## API Endpoints

### Authentication
- `POST /api/login` - User login
- `POST /api/register` - Student registration
- `POST /api/logout` - User logout

### Tests
- `GET /api/test_sections` - Get all test sections
- `GET /api/questions/<section_id>` - Get questions for a section
- `POST /api/submit_test` - Submit test and get score

### Performance
- `GET /api/user_scores` - Get user's test history
- `GET /api/section_performance` - Get section-wise performance
- `GET /api/ai_recommendations` - Get AI-based recommendations

### Resume
- `POST /api/save_resume` - Save resume and get score
- `GET /api/get_resume` - Get user's resume

### Admin
- `GET /api/admin/students` - Get all students (admin only)
- `GET /api/admin/department_stats` - Get department statistics (admin only)

## Features Breakdown

### For Students

1. **Take Tests**: Choose from 5 different test sections
2. **View Scores**: Immediate feedback with correct/incorrect answers
3. **Performance Analytics**: Visual graphs showing section-wise performance
4. **AI Recommendations**: Personalized suggestions for improvement
5. **Resume Builder**: Build and analyze resume with ATS scoring
6. **Readiness Score**: Overall placement readiness percentage

### For Admins

1. **Student Management**: View all registered students
2. **Department Analytics**: Performance statistics by department
3. **Training Insights**: Identify weak areas across student population
4. **Reports**: Export-ready data for decision making

## Extending the Application

### Adding More Questions

Edit `sql/schema.sql` and add more INSERT statements in the questions section, then delete `database.db` and restart the app.

### Adding External AI Integration

Replace the rule-based AI in `generate_ai_recommendations()` function in `app.py` with external API calls (OpenAI, etc.).

### Adding Power BI Integration

Export data from SQLite database and connect to Power BI for advanced visualizations.

### Production Deployment

1. Replace SQLite with MySQL/PostgreSQL
2. Use proper password hashing (bcrypt)
3. Add environment variables for secrets
4. Use production WSGI server (Gunicorn)
5. Add HTTPS with SSL certificates

## Security Notes

**IMPORTANT**: This is a development version. For production:

- Hash passwords using bcrypt or similar
- Use environment variables for secrets
- Implement CSRF protection
- Add rate limiting
- Use HTTPS
- Sanitize all user inputs
- Implement proper session management

## License

This project is open-source and available for educational purposes.

## Support

For issues or questions, please refer to the code comments or contact the development team.
