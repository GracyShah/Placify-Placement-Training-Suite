// PLACIFY - Frontend JavaScript Logic

// API helper function
console.log("App.js loaded successfully!");

const resumeAnalyzerState = {
  resumeText: "",
  jobDescriptionText: "",
  suggestions: null,
  chatHistory: [],
}

const THEME_STORAGE_KEY = "theme"

function applyTheme(theme) {
  if (!document.body) return

  const isDarkMode = theme === "dark"
  document.body.classList.toggle("dark-mode", isDarkMode)

  const themeToggle = document.getElementById("theme-toggle")
  if (themeToggle) {
    themeToggle.textContent = isDarkMode ? "Light Mode" : "Dark Mode"
    themeToggle.setAttribute("aria-pressed", String(isDarkMode))
    themeToggle.setAttribute("aria-label", isDarkMode ? "Switch to light mode" : "Switch to dark mode")
  }
}

function getStoredTheme() {
  try {
    return localStorage.getItem(THEME_STORAGE_KEY) === "dark" ? "dark" : "light"
  } catch (error) {
    console.warn("Theme preference unavailable:", error)
    return "light"
  }
}

function saveTheme(theme) {
  try {
    localStorage.setItem(THEME_STORAGE_KEY, theme)
  } catch (error) {
    console.warn("Unable to save theme preference:", error)
  }
}

function toggleTheme() {
  const nextTheme = document.body.classList.contains("dark-mode") ? "light" : "dark"
  applyTheme(nextTheme)
  saveTheme(nextTheme)
}

function ensureThemeToggle() {
  const navLinks = document.querySelector(".nav-content .nav-links")
  if (!navLinks || document.getElementById("theme-toggle")) return

  const toggleItem = document.createElement("li")
  toggleItem.className = "theme-toggle-item"

  const toggleButton = document.createElement("button")
  toggleButton.type = "button"
  toggleButton.id = "theme-toggle"
  toggleButton.className = "theme-toggle"
  toggleButton.addEventListener("click", toggleTheme)

  toggleItem.appendChild(toggleButton)
  navLinks.appendChild(toggleItem)

  applyTheme(getStoredTheme())
}

if (document.body) {
  applyTheme(getStoredTheme())
}

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


const currentTest = {
  mode: null,
  sectionId: null,
  sectionName: "",
  testId: null,
  testName: "",
  topicName: "",
  topicKey: "",
  companyTestId: null,
  companyName: "",
  questions: [],
  answers: {},
  startTime: null,
  duration: 0,
  timerInterval: null,
  latestAttemptId: null,
  latestSolutionUrl: null,
}

function resetCurrentTest() {
  if (currentTest.timerInterval) {
    clearInterval(currentTest.timerInterval)
  }
  currentTest.mode = null
  currentTest.sectionId = null
  currentTest.sectionName = ""
  currentTest.testId = null
  currentTest.testName = ""
  currentTest.topicName = ""
  currentTest.topicKey = ""
  currentTest.companyTestId = null
  currentTest.companyName = ""
  currentTest.questions = []
  currentTest.answers = {}
  currentTest.startTime = null
  currentTest.duration = 0
  currentTest.timerInterval = null
  currentTest.latestAttemptId = null
  currentTest.latestSolutionUrl = null
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;")
}

function getTopicBackAction(topicKey) {
  return `viewTopicTests('${topicKey}')`
}

function getTestStatusBadge(status, attempted) {
  return `<span class="status-pill ${attempted ? "status-attempted" : "status-open"}">${escapeHtml(status)}</span>`
}

function ensureConfirmModal() {
  let modal = document.getElementById("confirm-modal")
  if (modal) return modal

  modal = document.createElement("div")
  modal.id = "confirm-modal"
  modal.className = "modal-overlay hidden"
  modal.innerHTML = `
    <div class="modal-card">
      <div class="card-header" id="confirm-modal-title">Confirm</div>
      <div class="card-body">
        <p id="confirm-modal-message"></p>
        <div class="modal-actions">
          <button class="btn btn-primary" id="confirm-modal-accept">Continue</button>
          <button class="btn btn-secondary" id="confirm-modal-cancel">Cancel</button>
        </div>
      </div>
    </div>
  `
  document.body.appendChild(modal)
  return modal
}

function showConfirmModal(message, acceptLabel = "Continue", cancelLabel = "Cancel") {
  const modal = ensureConfirmModal()
  const messageEl = document.getElementById("confirm-modal-message")
  const acceptBtn = document.getElementById("confirm-modal-accept")
  const cancelBtn = document.getElementById("confirm-modal-cancel")

  messageEl.textContent = message
  acceptBtn.textContent = acceptLabel
  cancelBtn.textContent = cancelLabel
  modal.classList.remove("hidden")

  return new Promise((resolve) => {
    const cleanup = (value) => {
      modal.classList.add("hidden")
      acceptBtn.onclick = null
      cancelBtn.onclick = null
      modal.onclick = null
      resolve(value)
    }
    acceptBtn.onclick = () => cleanup(true)
    cancelBtn.onclick = () => cleanup(false)
    modal.onclick = (event) => {
      if (event.target === modal) cleanup(false)
    }
  })
}

function getTestPageElements() {
  return {
    title: document.getElementById("page-title"),
    instruction: document.getElementById("test-instruction"),
    sections: document.getElementById("test-sections"),
    companyList: document.getElementById("company-tests"),
    questions: document.getElementById("questions-container"),
    timer: document.getElementById("timer-container"),
    submit: document.getElementById("submit-container"),
  }
}

function showTestCatalog() {
  const elements = getTestPageElements()
  if (!elements.sections) return
  elements.sections.classList.remove("hidden")
  if (elements.companyList) {
    elements.companyList.classList.remove("hidden")
  }
  if (elements.questions) {
    elements.questions.classList.add("hidden")
    elements.questions.innerHTML = ""
  }
  if (elements.timer) {
    elements.timer.classList.add("hidden")
    elements.timer.classList.remove("timer-warning")
  }
  if (elements.submit) {
    elements.submit.classList.add("hidden")
  }
}

async function loadTestSections() {
  const topics = await apiCall("/api/topic_tests")
  const elements = getTestPageElements()
  const container = elements.sections
  if (!container) return

  resetCurrentTest()
  showTestCatalog()
  if (elements.companyList) {
    elements.companyList.classList.add("hidden")
  }
  if (elements.sections) {
    elements.sections.classList.remove("hidden")
  }
  if (elements.title) elements.title.textContent = "Take Tests"
  if (elements.instruction) {
    elements.instruction.textContent = "Select a topic below to view its predefined tests. Each topic-test can be attempted only once, and solutions unlock after submission."
  }

  container.innerHTML = ""
  topics.forEach((topic) => {
    const card = document.createElement("div")
    card.className = "card"
    card.innerHTML = `
      <div class="card-header">${topic.topic_name}</div>
      <div class="card-body">
        <p>${topic.description}</p>
        <p><strong>Available Tests:</strong> ${topic.test_count}</p>
        <button class="btn btn-primary mt-20" onclick="viewTopicTests('${topic.topic_key}')">View Tests</button>
      </div>
    `
    container.appendChild(card)
  })
}

async function viewTopicTests(topicKey) {
  const topics = await apiCall("/api/topic_tests")
  const topic = topics.find((item) => item.topic_key === topicKey)
  const elements = getTestPageElements()
  const container = elements.sections
  if (!topic || !container) return

  showTestCatalog()
  if (elements.title) elements.title.textContent = `${topic.topic_name} Tests`
  if (elements.instruction) {
    elements.instruction.textContent = "Attempt any unlocked topic test once. Attempted tests stay visible with status and solution access."
  }

  container.innerHTML = `
    <div class="card" style="grid-column: 1 / -1;">
      <div class="card-body">
        <button class="btn btn-secondary" onclick="loadTestSections()">Back to Topics</button>
      </div>
    </div>
  `

  topic.tests.forEach((test) => {
    const attempted = Boolean(test.attempted)
    const card = document.createElement("div")
    card.className = "card"
    card.innerHTML = `
      <div class="card-header">${test.test_name}</div>
      <div class="card-body">
        <p>${test.description}</p>
        <p><strong>Questions:</strong> ${test.question_count}</p>
        <p><strong>Time Limit:</strong> ${test.time_limit} minutes</p>
        <p><strong>Difficulty:</strong> ${(test.difficulty_tags || []).join(", ")}</p>
        <p><strong>Status:</strong> ${getTestStatusBadge(test.status, attempted)}</p>
        ${attempted && test.score !== null ? `<p><strong>Last Score:</strong> ${Number(test.score).toFixed(2)}%</p>` : ""}
        <button class="btn btn-primary mt-20" ${attempted ? "disabled" : ""} onclick="startTopicTest('${test.test_id}')">
          ${attempted ? "Attempted" : "Attempt Test"}
        </button>
        <button class="btn btn-secondary mt-20" ${test.solution_unlocked ? "" : "disabled"} onclick="showTopicSolutions('${test.test_id}')">
          ${test.solution_unlocked ? "View Solutions" : "Solutions Locked"}
        </button>
      </div>
    `
    container.appendChild(card)
  })
}

async function startTopicTest(testId) {
  const result = await apiCall(`/api/topic_tests/${testId}/questions`)
  if (!result.questions) {
    showAlert(result.message || "Unable to load topic test", "error")
    return
  }

  resetCurrentTest()
  currentTest.mode = "topic"
  currentTest.testId = result.test_id
  currentTest.testName = result.test_name
  currentTest.topicName = result.topic_name
  currentTest.topicKey = result.topic_key
  currentTest.questions = result.questions
  currentTest.answers = {}
  currentTest.startTime = Date.now()
  currentTest.duration = result.time_limit * 60

  renderActiveTest()
  startTimer()
}

async function showTopicSolutions(testId) {
  const result = await apiCall(`/api/topic_tests/${testId}/solutions`)
  if (!result.questions) {
    showAlert(result.message || "Unable to load solutions", "error")
    return
  }
  displaySolutions(result, getTopicBackAction(result.topic_key), result.topic_name)
}

async function loadCompanyTests() {
  const companyTests = await apiCall("/api/company_tests")
  const container = document.getElementById("company-tests")
  if (!container) return

  showTestCatalog()
  const elements = getTestPageElements()
  if (elements.companyList) {
    elements.companyList.classList.remove("hidden")
  }
  if (elements.sections) {
    elements.sections.classList.add("hidden")
    elements.sections.innerHTML = ""
  }
  if (elements.title) elements.title.textContent = "Company Wise Placement Tests"
  if (elements.instruction) {
    elements.instruction.textContent = "Select a company to view its predefined tests. Reattempts are allowed for company-wise tests, and solutions stay available after every attempt."
  }
  container.innerHTML = ""

  const groupedCompanies = companyTests.reduce((acc, test) => {
    const existing = acc[test.company_name] || {
      company_name: test.company_name,
      description: test.description,
      total_tests: 0,
      attempted_tests: 0,
    }
    existing.total_tests += 1
    if (test.attempted) existing.attempted_tests += 1
    acc[test.company_name] = existing
    return acc
  }, {})

  Object.values(groupedCompanies).forEach((company) => {
    const card = document.createElement("div")
    card.className = "card"
    card.innerHTML = `
      <div class="card-header">${company.company_name}</div>
      <div class="card-body">
        <p>${company.description || "Structured company-wise placement assessment."}</p>
        <p><strong>Available Tests:</strong> ${company.total_tests}</p>
        <p><strong>Completed Tests:</strong> ${company.attempted_tests}</p>
        <button class="btn btn-primary mt-20" onclick="viewCompanyTests('${company.company_name}')">View Tests</button>
      </div>
    `
    container.appendChild(card)
  })
}

async function viewCompanyTests(companyName) {
  const tests = await apiCall("/api/company_tests")
  const companyTests = tests.filter((item) => item.company_name === companyName)
  const elements = getTestPageElements()
  const container = elements.sections
  if (!container) return

  showTestCatalog()
  if (elements.companyList) {
    elements.companyList.classList.add("hidden")
  }
  elements.sections.classList.remove("hidden")
  if (elements.title) elements.title.textContent = `${companyName} Tests`
  if (elements.instruction) {
    elements.instruction.textContent = "Each company test has a fixed question set. Reattempts are allowed, and solutions unlock after every attempt."
  }

  container.innerHTML = `
    <div class="card" style="grid-column: 1 / -1;">
      <div class="card-body">
        <button class="btn btn-secondary" onclick="loadCompanyTests()">Back to Companies</button>
      </div>
    </div>
  `

  companyTests.forEach((test) => {
    const attempted = Boolean(test.attempted)
    const card = document.createElement("div")
    card.className = "card"
    card.innerHTML = `
      <div class="card-header">${test.test_name}</div>
      <div class="card-body">
        <p>${test.description || "Structured company-wise placement assessment."}</p>
        <p><strong>Questions:</strong> ${test.total_questions}</p>
        <p><strong>Time Limit:</strong> ${test.total_duration} minutes</p>
        <p><strong>Status:</strong> ${getTestStatusBadge(attempted ? "Attempted Earlier" : "Ready", attempted)}</p>
        <p><strong>Attempts:</strong> ${test.attempt_count || 0}</p>
        ${attempted && test.score !== null ? `<p><strong>Latest Score:</strong> ${Number(test.score).toFixed(2)}%</p>` : ""}
        <button class="btn btn-primary mt-20" onclick="startCompanyTest(${test.id}, ${attempted ? "true" : "false"})">
          ${attempted ? "Reattempt Test" : "Attempt Test"}
        </button>
        <button class="btn btn-secondary mt-20" ${attempted ? "" : "disabled"} onclick="showCompanySolutions(${test.id}${test.latest_attempt_id ? `, ${test.latest_attempt_id}` : ""})">
          ${attempted ? "View Latest Solutions" : "Solutions Locked"}
        </button>
      </div>
    `
    container.appendChild(card)
  })
}

async function startCompanyTest(companyTestId, alreadyAttempted = false) {
  if (alreadyAttempted) {
    const confirmed = await showConfirmModal("You have already attempted this test. Do you want to reattempt?", "Reattempt", "Cancel")
    if (!confirmed) return
  }

  const result = await apiCall(`/api/company_tests/${companyTestId}/questions`)
  if (!result.questions) {
    showAlert(result.message || "Unable to load company test", "error")
    return
  }

  resetCurrentTest()
  currentTest.mode = "company"
  currentTest.companyTestId = result.company_test_id
  currentTest.companyName = result.company_name
  currentTest.testName = result.test_name
  currentTest.questions = result.questions.map((question) => ({
    ...question,
    question_id: question.id,
  }))
  currentTest.answers = {}
  currentTest.startTime = Date.now()
  currentTest.duration = result.time_limit * 60

  renderActiveTest()
  startTimer()
}

async function showCompanySolutions(companyTestId, attemptId = null) {
  const suffix = attemptId ? `?attempt_id=${attemptId}` : ""
  const result = await apiCall(`/api/company_tests/${companyTestId}/solutions${suffix}`)
  if (!result.questions) {
    showAlert(result.message || "Unable to load solutions", "error")
    return
  }
  displaySolutions(result, "loadCompanyTests()", result.company_name)
}

function renderActiveTest() {
  const elements = getTestPageElements()
  if (!elements.sections || !elements.questions) return

  elements.sections.classList.add("hidden")
  if (elements.companyList) {
    elements.companyList.classList.add("hidden")
  }
  elements.questions.classList.remove("hidden")
  if (elements.timer) elements.timer.classList.remove("hidden")
  if (elements.submit) elements.submit.classList.remove("hidden")
  if (elements.title) elements.title.textContent = currentTest.testName
  if (elements.instruction) {
    elements.instruction.textContent = currentTest.mode === "company"
      ? `Attempting ${currentTest.companyName} placement test. Reattempts are allowed and the latest solution set will remain accessible.`
      : `Attempting ${currentTest.topicName}. This test can be attempted only once.`
  }
  const timerTitle = document.getElementById("test-title")
  if (timerTitle) {
    timerTitle.textContent = currentTest.mode === "company"
      ? `${currentTest.companyName} - ${currentTest.testName}`
      : `${currentTest.topicName} - ${currentTest.testName}`
  }

  elements.questions.innerHTML = currentTest.questions
    .map(
      (question, index) => `
        <div class="question-card">
          <div class="question-text">
            <strong>Q${index + 1}.</strong> ${question.question_text}
          </div>
          <p><strong>Difficulty:</strong> ${question.difficulty || "Medium"}</p>
          <div class="options">
            ${["A", "B", "C", "D"]
              .map(
                (opt) => `
                  <div class="option" onclick="selectAnswer('${question.question_id}', '${opt}', this)">
                    <strong>${opt}.</strong> ${question["option_" + opt.toLowerCase()]}
                  </div>
                `,
              )
              .join("")}
          </div>
        </div>
      `,
    )
    .join("")
}

function selectAnswer(questionId, answer, element) {
  const siblings = element.parentElement.querySelectorAll(".option")
  siblings.forEach((sibling) => sibling.classList.remove("selected"))
  element.classList.add("selected")
  currentTest.answers[String(questionId)] = answer
}

function startTimer() {
  let remaining = currentTest.duration
  const timerEl = document.getElementById("timer")
  if (!timerEl) return

  function updateTimer() {
    const min = Math.floor(remaining / 60)
    const sec = remaining % 60
    timerEl.textContent = `Time Left: ${min.toString().padStart(2, "0")}:${sec.toString().padStart(2, "0")}`

    if (remaining <= 30 && timerEl.parentElement) {
      timerEl.parentElement.classList.add("timer-warning")
    }
    if (remaining <= 0) {
      clearInterval(currentTest.timerInterval)
      currentTest.timerInterval = null
      showAlert("Time is up! Test auto-submitted.", "error")
      submitTest()
      return
    }
    remaining -= 1
  }

  updateTimer()
  currentTest.timerInterval = setInterval(updateTimer, 1000)
}

async function submitTest() {
  if (currentTest.timerInterval) {
    clearInterval(currentTest.timerInterval)
    currentTest.timerInterval = null
  }

  const timeTaken = Math.floor((Date.now() - currentTest.startTime) / 1000)
  let endpoint = "/api/submit_test"
  let payload = {
    section_id: currentTest.sectionId,
    answers: currentTest.answers,
    time_taken: timeTaken,
  }

  if (currentTest.mode === "topic") {
    endpoint = `/api/topic_tests/${currentTest.testId}/submit`
    payload = { answers: currentTest.answers, time_taken: timeTaken }
  } else if (currentTest.mode === "company") {
    endpoint = `/api/company_tests/${currentTest.companyTestId}/submit`
    payload = { answers: currentTest.answers, time_taken: timeTaken }
  }

  const result = await apiCall(endpoint, "POST", payload)
  if (!result.success) {
    showAlert(result.message || "Failed to submit test", "error")
    return
  }

  currentTest.latestAttemptId = result.attempt_id || null
  displayTestResult(result)
}

function renderPerformanceFeedback(feedback) {
  if (!feedback) return ""
  const categoryItems = Object.entries(feedback.category_breakdown || {})
  const difficultyItems = Object.entries(feedback.difficulty_breakdown || {})
  return `
    <div class="card" style="margin-top: 20px; text-align: left;">
      <div class="card-header">Performance Recommendations</div>
      <div class="card-body">
        <p>${feedback.summary || ""}</p>
        ${
          feedback.recommendations && feedback.recommendations.length
            ? `<ul>${feedback.recommendations.map((item) => `<li>${item}</li>`).join("")}</ul>`
            : ""
        }
        ${
          categoryItems.length
            ? `<p><strong>Topic Accuracy:</strong> ${categoryItems.map(([key, value]) => `${key}: ${value}%`).join(" | ")}</p>`
            : ""
        }
        ${
          difficultyItems.length
            ? `<p><strong>Difficulty Accuracy:</strong> ${difficultyItems.map(([key, value]) => `${key}: ${value}%`).join(" | ")}</p>`
            : ""
        }
      </div>
    </div>
  `
}

function displayTestResult(result) {
  const elements = getTestPageElements()
  showTestCatalog()
  if (!elements.sections) return
  if (elements.companyList) {
    elements.companyList.classList.add("hidden")
  }

  const backAction = currentTest.mode === "company" ? "loadCompanyTests()" : "loadTestSections()"
  const topicBackAction = currentTest.topicKey ? getTopicBackAction(currentTest.topicKey) : "loadTestSections()"
  const solutionAction = currentTest.mode === "company"
    ? `showCompanySolutions(${currentTest.companyTestId}${currentTest.latestAttemptId ? `, ${currentTest.latestAttemptId}` : ""})`
    : `showTopicSolutions('${currentTest.testId}')`

  elements.sections.innerHTML = `
    <div class="score-display">
      <h2>Test Completed!</h2>
      <div class="score-circle">${result.score}%</div>
      <p style="font-size: 20px; margin: 20px 0;">
        You answered <strong>${result.correct}</strong> out of
        <strong>${result.total}</strong> questions correctly!
      </p>
      <button class="btn btn-primary" onclick="${currentTest.mode === "company" ? backAction : topicBackAction}">Back to Tests</button>
      <button class="btn btn-secondary ml-10" onclick="${solutionAction}">View Solutions</button>
      ${renderPerformanceFeedback(result.performance_feedback)}
    </div>
  `

  resetCurrentTest()
}

function displaySolutions(result, backAction, label) {
  const elements = getTestPageElements()
  if (!elements.sections) return
  showTestCatalog()
  if (elements.companyList) {
    elements.companyList.classList.add("hidden")
  }
  if (elements.title) elements.title.textContent = `${label} Solutions`
  if (elements.instruction) {
    elements.instruction.textContent = "Solutions unlock after an attempt and remain available for review."
  }

  elements.sections.innerHTML = `
    <div class="card" style="grid-column: 1 / -1;">
      <div class="card-body">
        <button class="btn btn-secondary" onclick="${backAction}">Back</button>
        <p style="margin-top: 15px;"><strong>Score:</strong> ${Number(result.score || 0).toFixed(2)}%</p>
      </div>
    </div>
    ${result.questions
      .map(
        (question, index) => `
          <div class="card" style="grid-column: 1 / -1;">
            <div class="card-header">Question ${index + 1}</div>
            <div class="card-body">
              ${question.section ? `<p><strong>Section:</strong> ${question.section}</p>` : ""}
              ${question.difficulty ? `<p><strong>Difficulty:</strong> ${question.difficulty}</p>` : ""}
              <p><strong>Question:</strong> ${question.question_text}</p>
              <p><strong>Your Answer:</strong> ${question.selected_answer || "Not answered"}</p>
              <p><strong>Correct Answer:</strong> ${question.correct_answer}</p>
              <p><strong>Status:</strong> ${question.is_correct ? "Correct" : "Incorrect"}</p>
              <p><strong>Explanation:</strong> ${question.explanation}</p>
            </div>
          </div>
        `,
      )
      .join("")}
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
  const payload = recommendations.recommendation_payload ? JSON.parse(recommendations.recommendation_payload) : {}
  const topicAccuracy = payload.topic_accuracy || []
  const difficultyAnalysis = payload.difficulty_analysis || {}
  const repeatedMistakes = payload.repeated_mistakes || []
  const nextTests = payload.recommended_next_tests || []
  const latestRecommendations = payload.latest_recommendations || []

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

        ${
          topicAccuracy.length
            ? `
            <div class="card">
                <div class="card-header">Topic Accuracy</div>
                <div class="card-body">
                    <ul>
                        ${topicAccuracy.map((item) => `<li>${item.topic}: ${item.accuracy}% accuracy across ${item.questions_seen} questions</li>`).join("")}
                    </ul>
                </div>
            </div>
        `
            : ""
        }

        ${
          Object.keys(difficultyAnalysis).length
            ? `
            <div class="card">
                <div class="card-header">Difficulty Analysis</div>
                <div class="card-body">
                    <p>${Object.entries(difficultyAnalysis).map(([label, value]) => `${label}: ${value}%`).join(" | ")}</p>
                </div>
            </div>
        `
            : ""
        }

        ${
          repeatedMistakes.length
            ? `
            <div class="card">
                <div class="card-header">Repeated Mistakes</div>
                <div class="card-body">
                    <ul>
                        ${repeatedMistakes.map((item) => `<li>${item}</li>`).join("")}
                    </ul>
                </div>
            </div>
        `
            : ""
        }

        ${
          latestRecommendations.length || nextTests.length
            ? `
            <div class="card">
                <div class="card-header">Recommended Next Steps</div>
                <div class="card-body">
                    ${latestRecommendations.length ? `<ul>${latestRecommendations.map((item) => `<li>${item}</li>`).join("")}</ul>` : ""}
                    ${nextTests.length ? `<p><strong>Suggested next tests:</strong> ${nextTests.join(", ")}</p>` : ""}
                </div>
            </div>
        `
            : ""
        }
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
    document.getElementById("target_company").value = resume.target_company || ""
    document.getElementById("target_role").value = resume.target_role || ""
    document.getElementById("education").value = resume.education || ""
    document.getElementById("skills").value = resume.skills || ""
    document.getElementById("experience").value = resume.experience || ""
    document.getElementById("projects").value = resume.projects || ""
    document.getElementById("certifications").value = resume.certifications || ""
    document.getElementById("job_description").value = resume.job_description || ""

    // Show scores if available
    if (resume.overall_score) {
      displayResumeScore({
        ats_score: resume.ats_score,
        keyword_score: resume.keyword_score,
        format_score: resume.format_score,
        overall_score: resume.overall_score,
        feedback: resume.feedback,
        jd_match_percentage: resume.jd_match_percentage || 0,
      })
    }
  }
}

async function handleResumeSave(event) {
  event.preventDefault()

  const formData = new FormData()
  formData.append("full_name", document.getElementById("full_name").value)
  formData.append("email", document.getElementById("email").value)
  formData.append("phone", document.getElementById("phone").value)
  formData.append("target_company", document.getElementById("target_company").value)
  formData.append("target_role", document.getElementById("target_role").value)
  formData.append("education", document.getElementById("education").value)
  formData.append("skills", document.getElementById("skills").value)
  formData.append("experience", document.getElementById("experience").value)
  formData.append("projects", document.getElementById("projects").value)
  formData.append("certifications", document.getElementById("certifications").value)
  formData.append("job_description", document.getElementById("job_description").value)

  const jdFileInput = document.getElementById("jd_file")
  if (jdFileInput && jdFileInput.files.length) {
    formData.append("jd_file", jdFileInput.files[0])
  }

  const response = await fetch("/api/save_resume", {
    method: "POST",
    body: formData,
  })

  const result = await response.json()

  if (result.success) {
    showAlert("Resume saved successfully!", "success")
    displayResumeScore(result.scores)
    showResumeDownloads(result.download_pdf_url, result.download_doc_url)
    const resumeForm = document.getElementById("resume-form")
    if (resumeForm) {
      resumeForm.reset()
    }
  } else {
    showAlert("Failed to save resume", "error")
  }
}

function showResumeDownloads(pdfUrl, docUrl) {
  const container = document.getElementById("resume-downloads")
  const pdfLink = document.getElementById("download-pdf")
  const docLink = document.getElementById("download-doc")

  if (!container || !pdfLink || !docLink) return

  pdfLink.href = pdfUrl
  docLink.href = docUrl
  container.classList.remove("hidden")
}

function displayResumeScore(scores) {
  const container = document.getElementById("resume-score")
  if (!container) return

  container.innerHTML = `
        <h3 style="margin-bottom: 20px;">Resume Score Analysis</h3>
        
        <div class="grid grid-4 mb-20">
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
            <div class="stat-card">
                <div class="stat-value">${(scores.jd_match_percentage || 0).toFixed(0)}%</div>
                <div class="stat-label">JD Match</div>
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

async function handleResumeAnalyzer(event) {
  event.preventDefault()

  const fileInput = document.getElementById("resume_file")
  const jobDescriptionInput = document.getElementById("job_description")
  const jdFileInput = document.getElementById("jd_file")
  const resultsContainer = document.getElementById("resume-analyzer-results")

  if (!fileInput || !fileInput.files.length) {
    showAlert("Please select a resume file", "error")
    return
  }

  const formData = new FormData()
  formData.append("resume_file", fileInput.files[0])
  formData.append("job_description", jobDescriptionInput ? jobDescriptionInput.value : "")
  if (jdFileInput && jdFileInput.files.length) {
    formData.append("jd_file", jdFileInput.files[0])
  }

  const response = await fetch("/api/analyze_resume", {
    method: "POST",
    body: formData,
  })

  const result = await response.json()

  if (!result.success) {
    showAlert(result.message || "Failed to analyze resume", "error")
    return
  }

  resumeAnalyzerState.resumeText = result.resume_text || ""
  resumeAnalyzerState.jobDescriptionText = result.job_description_text || ""
  resumeAnalyzerState.suggestions = null
  resumeAnalyzerState.chatHistory = []

  resultsContainer.innerHTML = `
        <div class="card-header">Analysis Results</div>
        <div class="card-body">
            <div class="grid grid-2 mb-20">
                <div class="stat-card">
                    <div class="stat-value">${result.match_percentage.toFixed(0)}%</div>
                    <div class="stat-label">Skill Match</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${result.resume_score.toFixed(0)}</div>
                    <div class="stat-label">Resume Score</div>
                </div>
            </div>
            <div class="grid grid-2">
                <div class="card">
                    <div class="card-header">Extracted Skills</div>
                    <div class="card-body">
                        <p>${result.extracted_skills.length ? result.extracted_skills.join(", ") : "No skills detected"}</p>
                    </div>
                </div>
                <div class="card">
                    <div class="card-header">Matched Skills</div>
                    <div class="card-body">
                        <p>${result.matched_skills.length ? result.matched_skills.join(", ") : "No matched skills found"}</p>
                    </div>
                </div>
                <div class="card">
                    <div class="card-header">Missing Skills</div>
                    <div class="card-body">
                        <p>${result.missing_skills.length ? result.missing_skills.join(", ") : "No missing skills"}</p>
                    </div>
                </div>
                <div class="card">
                    <div class="card-header">Extra Skills</div>
                    <div class="card-body">
                        <p>${result.extra_skills.length ? result.extra_skills.join(", ") : "No extra skills"}</p>
                    </div>
                </div>
                <div class="card">
                    <div class="card-header">Keyword Overlap</div>
                    <div class="card-body">
                        <p>${result.keyword_overlap.length ? result.keyword_overlap.join(", ") : "No keyword overlap found"}</p>
                    </div>
                </div>
            </div>
        </div>
    `

  showAlert("Resume analyzed successfully!", "success")
}

function renderResumeAISuggestions(suggestions) {
  const container = document.getElementById("resume-ai-suggestions")
  if (!container) return

  const skillGaps = suggestions.skill_gaps || []
  const missingKeywords = suggestions.missing_keywords || []
  const sectionImprovements = suggestions.section_wise_improvements || []
  const atsTips = suggestions.ats_optimization_tips || []
  const topStrengths = suggestions.top_strengths || []
  const notice = suggestions.notice || ""

  container.innerHTML = `
        <div class="card-header">AI Suggestions</div>
        <div class="card-body">
            ${
              notice
                ? `<div class="alert alert-info mb-20">${notice}</div>`
                : ""
            }
            <div class="grid grid-2">
                <div class="card">
                    <div class="card-header">Skill Gaps</div>
                    <div class="card-body">
                        <p>${skillGaps.length ? skillGaps.join(", ") : "No major skill gaps identified"}</p>
                    </div>
                </div>
                <div class="card">
                    <div class="card-header">Missing Keywords</div>
                    <div class="card-body">
                        <p>${missingKeywords.length ? missingKeywords.join(", ") : "No major keyword gaps identified"}</p>
                    </div>
                </div>
                <div class="card">
                    <div class="card-header">Section-wise Improvements</div>
                    <div class="card-body">
                        ${
                          sectionImprovements.length
                            ? sectionImprovements
                                .map(
                                  (item) =>
                                    `<p><strong>${item.section}:</strong> ${item.improvement}</p>`,
                                )
                                .join("")
                            : "<p>No section-wise improvements returned.</p>"
                        }
                    </div>
                </div>
                <div class="card">
                    <div class="card-header">ATS Optimization Tips</div>
                    <div class="card-body">
                        <p>${atsTips.length ? atsTips.join(", ") : "No ATS optimization tips returned."}</p>
                    </div>
                </div>
                <div class="card">
                    <div class="card-header">Shortlisting Probability</div>
                    <div class="card-body">
                        <p>${suggestions.shortlisting_probability_estimate || "Improvement estimate unavailable"}</p>
                        ${suggestions.match_percentage ? `<p><strong>Match Score:</strong> ${Number(suggestions.match_percentage).toFixed(0)}%</p>` : ""}
                    </div>
                </div>
                <div class="card">
                    <div class="card-header">Top Strengths</div>
                    <div class="card-body">
                        <p>${topStrengths.length ? topStrengths.join(" ") : "No standout strengths detected yet."}</p>
                    </div>
                </div>
            </div>
        </div>
    `
}

function renderResumeAIChat() {
  const container = document.getElementById("resume-ai-chat-messages")
  if (!container) return

  if (!resumeAnalyzerState.chatHistory.length) {
    container.innerHTML = "<p>Ask follow-up questions after generating AI suggestions.</p>"
    return
  }

  container.innerHTML = resumeAnalyzerState.chatHistory
    .map(
      (message) => `
        <div class="card mb-20">
            <div class="card-header">${message.role === "user" ? "You" : "AI Coach"}</div>
            <div class="card-body">
                <p>${message.content}</p>
            </div>
        </div>
      `,
    )
    .join("")
}

async function handleGetAISuggestions() {
  if (!resumeAnalyzerState.resumeText || !resumeAnalyzerState.jobDescriptionText) {
    showAlert("Analyze the resume against a job description first", "error")
    return
  }

  const result = await apiCall("/api/resume_ai_suggestions", "POST", {
    resume_text: resumeAnalyzerState.resumeText,
    job_description_text: resumeAnalyzerState.jobDescriptionText,
  })

  if (!result.success) {
    showAlert(result.message || "Failed to fetch AI suggestions", "error")
    return
  }

  resumeAnalyzerState.suggestions = result.suggestions
  renderResumeAISuggestions(result.suggestions)
  renderResumeAIChat()

  if (result.suggestions && result.suggestions.notice) {
    showAlert(result.suggestions.notice, "info")
  } else {
    showAlert("AI suggestions generated successfully!", "success")
  }
}

async function handleResumeAIChat(event) {
  event.preventDefault()

  const questionInput = document.getElementById("resume-ai-question")
  const question = questionInput ? questionInput.value.trim() : ""

  if (!resumeAnalyzerState.suggestions) {
    showAlert("Generate AI suggestions before asking follow-up questions", "error")
    return
  }

  if (!question) {
    showAlert("Enter a follow-up question", "error")
    return
  }

  resumeAnalyzerState.chatHistory.push({ role: "user", content: question })
  renderResumeAIChat()

  const result = await apiCall("/api/resume_ai_chat", "POST", {
    resume_text: resumeAnalyzerState.resumeText,
    job_description_text: resumeAnalyzerState.jobDescriptionText,
    suggestions: resumeAnalyzerState.suggestions,
    question,
    chat_history: resumeAnalyzerState.chatHistory,
  })

  if (!result.success) {
    resumeAnalyzerState.chatHistory.pop()
    renderResumeAIChat()
    showAlert(result.message || "Failed to fetch AI chat response", "error")
    return
  }

  resumeAnalyzerState.chatHistory.push({ role: "assistant", content: result.answer })
  if (questionInput) {
    questionInput.value = ""
  }
  renderResumeAIChat()
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
  applyTheme(getStoredTheme())
  ensureThemeToggle()

  const path = window.location.pathname

  if (path === "/tests") {
    loadTestSections()
  } else if (path === "/dashboard") {
    loadUserScores()
    loadSectionPerformance()
    loadAIRecommendations()
  } else if (path === "/resume") {
    loadResumeForm()
  } else if (path === "/resume-analyzer") {
    const analyzerForm = document.getElementById("resume-analyzer-form")
    const aiButton = document.getElementById("resume-ai-button")
    const aiChatForm = document.getElementById("resume-ai-chat-form")
    if (analyzerForm) {
      analyzerForm.addEventListener("submit", handleResumeAnalyzer)
    }
    if (aiButton) {
      aiButton.addEventListener("click", handleGetAISuggestions)
    }
    if (aiChatForm) {
      aiChatForm.addEventListener("submit", handleResumeAIChat)
    }
  } else if (path === "/admin") {
    loadAdminStudents()
    loadDepartmentStats()
  } else if (path === "/company-tests") {
    loadCompanyTests()
  }
})


