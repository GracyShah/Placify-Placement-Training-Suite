// PLACIFY - Frontend JavaScript Logic

// API helper function
console.log("App.js loaded successfully!");

async function apiCall(endpoint, method = "GET", body = null) {
  const options = {
    method: method,
    headers: {
      "Content-Type": "application/json",
    },
  }

  if (body) {
    options.body = JSON.stringify(body)
  }

  try {
    const response = await fetch(endpoint, options)
    const data = await response.json()
    return data
  } catch (error) {
    console.error("API Error:", error)
    return { success: false, message: "Network error" }
  }
}

// Show alert message
function showAlert(message, type = "info") {
  const alertDiv = document.createElement("div")
  alertDiv.className = `alert alert-${type}`
  alertDiv.textContent = message

  const container = document.querySelector(".container")
  if (container) {
    container.insertBefore(alertDiv, container.firstChild)
    setTimeout(() => alertDiv.remove(), 5000)
  }
}

// Format date
function formatDate(dateString) {
  const date = new Date(dateString)
  return date.toLocaleDateString() + " " + date.toLocaleTimeString()
}

// Calculate time ago
function timeAgo(dateString) {
  const date = new Date(dateString)
  const seconds = Math.floor((new Date() - date) / 1000)

  if (seconds < 60) return seconds + " seconds ago"
  const minutes = Math.floor(seconds / 60)
  if (minutes < 60) return minutes + " minutes ago"
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return hours + " hours ago"
  const days = Math.floor(hours / 24)
  return days + " days ago"
}

// Login functionality
async function handleLogin(event) {
  event.preventDefault()

  const username = document.getElementById("username").value
  const password = document.getElementById("password").value

  const result = await apiCall("/api/login", "POST", { username, password })

  if (result.success) {
    window.location.href = result.redirect
  } else {
    showAlert(result.message || "Login failed", "error")
  }
}

// Register functionality
async function handleRegister(event) {
  event.preventDefault()

  const formData = {
    username: document.getElementById("reg-username").value,
    email: document.getElementById("reg-email").value,
    password: document.getElementById("reg-password").value,
    full_name: document.getElementById("reg-fullname").value,
    department: document.getElementById("reg-department").value,
    year: Number.parseInt(document.getElementById("reg-year").value),
  }

  const result = await apiCall("/api/register", "POST", formData)

  if (result.success) {
    showAlert("Registration successful! Please login.", "success")
    document.getElementById("register-form").reset()
    // Switch to login tab if exists
    const loginTab = document.querySelector('[data-tab="login"]')
    if (loginTab) loginTab.click()
  } else {
    showAlert(result.message || "Registration failed", "error")
  }
}

// Logout functionality
async function handleLogout() {
  await apiCall("/api/logout", "POST")
  window.location.href = "/login"
}

// Load test sections
async function loadTestSections() {
  const sections = await apiCall("/api/test_sections")
  const container = document.getElementById("test-sections")

  if (!container) return

  container.innerHTML = ""

  sections.forEach((section) => {
    const card = document.createElement("div")
    card.className = "card"
    card.innerHTML = `
            <div class="card-header">${section.section_name}</div>
            <div class="card-body">
                <p>${section.description}</p>
                <p><strong>Questions:</strong> ${section.total_questions}</p>
                <p><strong>Time Limit:</strong> ${section.time_limit} minutes</p>
                <button class="btn btn-primary mt-20" onclick="startTest(${section.id}, '${section.section_name}')">
                    Start Test
                </button>
            </div>
        `
    container.appendChild(card)
  })
}

// Start test
const currentTest = {
  sectionId: null,
  sectionName: "",
  questions: [],
  answers: {},
  startTime: null,
}

async function startTest(sectionId, sectionName) {
  currentTest.sectionId = sectionId
  currentTest.sectionName = sectionName
  currentTest.startTime = Date.now()
  currentTest.answers = {}

  const questions = await apiCall(`/api/questions/${sectionId}`)
  currentTest.questions = questions

  displayQuestions()
}

// Display questions
function displayQuestions() {
  const container = document.getElementById("test-sections")
  if (!container) return

  container.innerHTML = `
        <h2>${currentTest.sectionName} Test</h2>
        <div id="questions-container"></div>
        <div class="flex-between mt-20">
            <button class="btn btn-secondary" onclick="loadTestSections()">Cancel</button>
            <button class="btn btn-primary" onclick="submitTest()">Submit Test</button>
        </div>
    `

  const questionsContainer = document.getElementById("questions-container")

  currentTest.questions.forEach((question, index) => {
    const questionCard = document.createElement("div")
    questionCard.className = "question-card"
    questionCard.innerHTML = `
            <div class="question-text">
                <strong>Q${index + 1}.</strong> ${question.question_text}
            </div>
            <div class="options">
                ${["A", "B", "C", "D"]
                  .map(
                    (opt) => `
                    <div class="option" onclick="selectAnswer(${question.id}, '${opt}', this)">
                        <strong>${opt}.</strong> ${question["option_" + opt.toLowerCase()]}
                    </div>
                `,
                  )
                  .join("")}
            </div>
        `
    questionsContainer.appendChild(questionCard)
  })
}

// Select answer
function selectAnswer(questionId, answer, element) {
  // Remove selection from siblings
  const siblings = element.parentElement.querySelectorAll(".option")
  siblings.forEach((sib) => sib.classList.remove("selected"))

  // Add selection to clicked element
  element.classList.add("selected")

  // Store answer
  currentTest.answers[questionId] = answer
}

// Submit test
async function submitTest() {
  const timeTaken = Math.floor((Date.now() - currentTest.startTime) / 1000)

  const result = await apiCall("/api/submit_test", "POST", {
    section_id: currentTest.sectionId,
    answers: currentTest.answers,
    time_taken: timeTaken,
  })

  if (result.success) {
    displayTestResult(result)
  } else {
    showAlert("Failed to submit test", "error")
  }
}

// Display test result
function displayTestResult(result) {
  const container = document.getElementById("test-sections")
  if (!container) return

  container.innerHTML = `
        <div class="score-display">
            <h2>Test Completed!</h2>
            <div class="score-circle">${result.score}%</div>
            <p style="font-size: 20px; margin: 20px 0;">
                You answered <strong>${result.correct}</strong> out of <strong>${result.total}</strong> questions correctly!
            </p>
            <button class="btn btn-primary" onclick="loadTestSections()">Take Another Test</button>
            <a href="/dashboard" class="btn btn-secondary ml-10">View Dashboard</a>
        </div>
    `
}

// Load user scores
async function loadUserScores() {
  const scores = await apiCall("/api/user_scores")
  const container = document.getElementById("scores-table")

  if (!container) return

  if (scores.length === 0) {
    container.innerHTML = '<p class="text-center">No test attempts yet. Start taking tests!</p>'
    return
  }

  const table = document.createElement("table")
  table.className = "table"
  table.innerHTML = `
        <thead>
            <tr>
                <th>Section</th>
                <th>Score</th>
                <th>Correct Answers</th>
                <th>Total Questions</th>
                <th>Date</th>
            </tr>
        </thead>
        <tbody>
            ${scores
              .map(
                (score) => `
                <tr>
                    <td>${score.section_name}</td>
                    <td><strong>${score.score.toFixed(2)}%</strong></td>
                    <td>${score.correct_answers}</td>
                    <td>${score.total_questions}</td>
                    <td>${timeAgo(score.completed_at)}</td>
                </tr>
            `,
              )
              .join("")}
        </tbody>
    `

  container.innerHTML = ""
  container.appendChild(table)
}

// Load section performance
async function loadSectionPerformance() {
  const performance = await apiCall("/api/section_performance")
  const container = document.getElementById("performance-chart")

  if (!container) return

  if (performance.length === 0) {
    container.innerHTML = '<p class="text-center">No performance data yet.</p>'
    return
  }

  container.innerHTML = ""

  performance.forEach((section) => {
    const card = document.createElement("div")
    card.className = "card"
    card.innerHTML = `
            <div class="card-header">${section.section_name}</div>
            <div class="card-body">
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${section.avg_score}%">
                        ${section.avg_score.toFixed(1)}%
                    </div>
                </div>
                <p style="margin-top: 10px;">Attempts: ${section.attempts}</p>
            </div>
        `
    container.appendChild(card)
  })
}

// Load AI recommendations
async function loadAIRecommendations() {
  const recommendations = await apiCall("/api/ai_recommendations")
  const container = document.getElementById("ai-recommendations")

  if (!container) return

  if (!recommendations.readiness_score) {
    container.innerHTML = '<p class="text-center">Take some tests to get AI recommendations!</p>'
    return
  }

  const weakSections = JSON.parse(recommendations.weak_sections || "[]")
  const improvementAreas = JSON.parse(recommendations.improvement_areas || "[]")

  container.innerHTML = `
        <div class="card">
            <div class="card-header">Placement Readiness Score</div>
            <div class="score-circle" style="margin: 20px auto;">
                ${recommendations.readiness_score.toFixed(1)}%
            </div>
        </div>
        
        ${
          weakSections.length > 0
            ? `
            <div class="card">
                <div class="card-header">Weak Sections</div>
                <div class="card-body">
                    <ul>
                        ${weakSections.map((section) => `<li>${section}</li>`).join("")}
                    </ul>
                </div>
            </div>
        `
            : ""
        }
        
        ${
          improvementAreas.length > 0
            ? `
            <div class="card">
                <div class="card-header">Improvement Suggestions</div>
                <div class="card-body">
                    <ul>
                        ${improvementAreas.map((area) => `<li>${area}</li>`).join("")}
                    </ul>
                </div>
            </div>
        `
            : ""
        }
        
        <div class="card">
            <div class="card-header">Practice Focus</div>
            <div class="card-body">
                <p>${recommendations.practice_focus}</p>
            </div>
        </div>
    `
}

// Resume builder functions
async function loadResumeForm() {
  const resume = await apiCall("/api/get_resume")

  if (resume && resume.full_name) {
    // Populate form with existing data
    document.getElementById("full_name").value = resume.full_name || ""
    document.getElementById("email").value = resume.email || ""
    document.getElementById("phone").value = resume.phone || ""
    document.getElementById("education").value = resume.education || ""
    document.getElementById("skills").value = resume.skills || ""
    document.getElementById("experience").value = resume.experience || ""
    document.getElementById("projects").value = resume.projects || ""
    document.getElementById("certifications").value = resume.certifications || ""

    // Show scores if available
    if (resume.overall_score) {
      displayResumeScore({
        ats_score: resume.ats_score,
        keyword_score: resume.keyword_score,
        format_score: resume.format_score,
        overall_score: resume.overall_score,
        feedback: resume.feedback,
      })
    }
  }
}

async function handleResumeSave(event) {
  event.preventDefault()

  const resumeData = {
    full_name: document.getElementById("full_name").value,
    email: document.getElementById("email").value,
    phone: document.getElementById("phone").value,
    education: document.getElementById("education").value,
    skills: document.getElementById("skills").value,
    experience: document.getElementById("experience").value,
    projects: document.getElementById("projects").value,
    certifications: document.getElementById("certifications").value,
  }

  const result = await apiCall("/api/save_resume", "POST", resumeData)

  if (result.success) {
    showAlert("Resume saved successfully!", "success")
    displayResumeScore(result.scores)
  } else {
    showAlert("Failed to save resume", "error")
  }
}

function displayResumeScore(scores) {
  const container = document.getElementById("resume-score")
  if (!container) return

  container.innerHTML = `
        <h3 style="margin-bottom: 20px;">Resume Score Analysis</h3>
        
        <div class="grid grid-3 mb-20">
            <div class="stat-card">
                <div class="stat-value">${scores.ats_score.toFixed(0)}</div>
                <div class="stat-label">ATS Score</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${scores.keyword_score.toFixed(0)}</div>
                <div class="stat-label">Keyword Score</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${scores.format_score.toFixed(0)}</div>
                <div class="stat-label">Format Score</div>
            </div>
        </div>
        
        <div class="card">
            <div class="card-header">Overall Score: ${scores.overall_score.toFixed(1)}%</div>
            <div class="card-body">
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${scores.overall_score}%">
                        ${scores.overall_score.toFixed(1)}%
                    </div>
                </div>
                <p style="margin-top: 15px;"><strong>Feedback:</strong> ${scores.feedback}</p>
            </div>
        </div>
    `
}

// Admin functions
async function loadAdminStudents() {
  const students = await apiCall("/api/admin/students")
  const container = document.getElementById("students-table")

  if (!container) return

  const table = document.createElement("table")
  table.className = "table"
  table.innerHTML = `
        <thead>
            <tr>
                <th>Name</th>
                <th>Username</th>
                <th>Department</th>
                <th>Year</th>
                <th>Avg Score</th>
                <th>Tests Taken</th>
            </tr>
        </thead>
        <tbody>
            ${students
              .map(
                (student) => `
                <tr>
                    <td>${student.full_name}</td>
                    <td>${student.username}</td>
                    <td>${student.department || "N/A"}</td>
                    <td>${student.year || "N/A"}</td>
                    <td><strong>${student.avg_score ? student.avg_score.toFixed(2) + "%" : "N/A"}</strong></td>
                    <td>${student.sections_attempted || 0}</td>
                </tr>
            `,
              )
              .join("")}
        </tbody>
    `

  container.innerHTML = ""
  container.appendChild(table)
}

async function loadDepartmentStats() {
  const stats = await apiCall("/api/admin/department_stats")
  const container = document.getElementById("department-stats")

  if (!container) return

  container.innerHTML = ""

  stats.forEach((dept) => {
    const card = document.createElement("div")
    card.className = "card"
    card.innerHTML = `
            <div class="card-header">${dept.department}</div>
            <div class="card-body">
                <p><strong>Students:</strong> ${dept.student_count}</p>
                <p><strong>Average Score:</strong> ${dept.avg_score ? dept.avg_score.toFixed(2) + "%" : "N/A"}</p>
                <p><strong>Total Attempts:</strong> ${dept.total_attempts || 0}</p>
                <div class="progress-bar" style="margin-top: 10px;">
                    <div class="progress-fill" style="width: ${dept.avg_score || 0}%">
                        ${dept.avg_score ? dept.avg_score.toFixed(1) + "%" : "0%"}
                    </div>
                </div>
            </div>
        `
    container.appendChild(card)
  })
}

// Initialize page based on current location
document.addEventListener("DOMContentLoaded", () => {
  const path = window.location.pathname

  if (path === "/tests") {
    loadTestSections()
  } else if (path === "/dashboard") {
    loadUserScores()
    loadSectionPerformance()
    loadAIRecommendations()
  } else if (path === "/resume") {
    loadResumeForm()
  } else if (path === "/admin") {
    loadAdminStudents()
    loadDepartmentStats()
  }
})
