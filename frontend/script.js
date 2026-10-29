
"use strict";

// Local development API. We will configure the live API during deployment.
const API_URL = "https://skillgap-ai-api.onrender.com/api/analyze";
const MAX_FILE_SIZE = 10 * 1024 * 1024;

const form = document.getElementById("analyzeForm");
const roleSelect = document.getElementById("jobRole");
const fileInput = document.getElementById("resumeFile");
const dropZone = document.getElementById("dropZone");
const uploadTitle = document.getElementById("uploadTitle");
const uploadSubtitle = document.getElementById("uploadSubtitle");
const analyzeButton = document.getElementById("analyzeButton");
const buttonText = document.getElementById("buttonText");
const buttonArrow = document.getElementById("buttonArrow");
const statusMessage = document.getElementById("statusMessage");
const resultsSection = document.getElementById("resultsSection");
const mobileMenu = document.getElementById("mobileMenu");
const navLinks = document.getElementById("navLinks");

let skillChart = null;

// Keep the footer year current.
document.getElementById("currentYear").textContent =
  new Date().getFullYear();

// Display feedback without inserting HTML from user input.
function showStatus(message, type = "") {
  statusMessage.textContent = message;
  statusMessage.className = "status-message";

  if (type) {
    statusMessage.classList.add(type);
  }
}

// Validate the file before making an API request.
function validateFile(file) {
  if (!file) return "Please select your PDF resume.";

  if (!file.name.toLowerCase().endsWith(".pdf")) {
    return "Please upload a PDF file.";
  }

  if (file.size === 0) {
    return "The selected file is empty.";
  }

  if (file.size > MAX_FILE_SIZE) {
    return "Your resume must be 10 MB or smaller.";
  }

  return "";
}

function updateFileDisplay(file) {
  if (!file) {
    uploadTitle.textContent = "Drop your resume here";
    uploadSubtitle.innerHTML =
      'or <span class="browse-link">browse files</span>';
    return;
  }

  uploadTitle.textContent = file.name;
  uploadSubtitle.textContent =
    `${(file.size / (1024 * 1024)).toFixed(2)} MB selected`;
}

fileInput.addEventListener("change", () => {
  const file = fileInput.files[0];

  if (!file) {
    updateFileDisplay(null);
    return;
  }

  const error = validateFile(file);

  if (error) {
    fileInput.value = "";
    updateFileDisplay(null);
    showStatus(error, "error");
    return;
  }

  showStatus("");
  updateFileDisplay(file);
});

// Support dragging a PDF onto the upload area.
["dragenter", "dragover"].forEach((eventName) => {
  dropZone.addEventListener(eventName, (event) => {
    event.preventDefault();
    dropZone.classList.add("dragging");
  });
});

["dragleave", "drop"].forEach((eventName) => {
  dropZone.addEventListener(eventName, (event) => {
    event.preventDefault();
    dropZone.classList.remove("dragging");
  });
});

dropZone.addEventListener("drop", (event) => {
  const file = event.dataTransfer.files[0];

  if (!file) return;

  const error = validateFile(file);

  if (error) {
    showStatus(error, "error");
    return;
  }

  const transfer = new DataTransfer();
  transfer.items.add(file);
  fileInput.files = transfer.files;

  updateFileDisplay(file);
  showStatus("");
});

// Create safe text elements for API results.
function createTextElement(tag, className, text) {
  const element = document.createElement(tag);

  if (className) {
    element.className = className;
  }

  element.textContent = String(text);
  return element;
}

// Accept only valid external HTTPS learning links.
function getSafeCourseUrl(value) {
  try {
    const url = new URL(value);

    if (url.protocol === "https:") {
      return url.href;
    }
  } catch {
    // An invalid URL is handled by returning no link.
  }

  return "";
}

// Render the interactive Chart.js donut.
function renderChart(matchedCount, missingCount) {
  const canvas = document.getElementById("skillChart");

  if (skillChart) {
    skillChart.destroy();
    skillChart = null;
  }

  skillChart = new Chart(canvas, {
    type: "doughnut",
    data: {
      labels: ["Matched skills", "Not detected"],
      datasets: [{
        data: [matchedCount, missingCount],
        backgroundColor: ["#74dfc4", "#46506d"],
        borderWidth: 0,
        hoverOffset: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      cutout: "77%",
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label(context) {
              return `${context.label}: ${context.raw}`;
            }
          }
        }
      }
    }
  });
}

// Check the shape of the response before rendering it.
function validateAnalysisResponse(data) {
  if (
    !data ||
    typeof data.job_role !== "string" ||
    !Array.isArray(data.matched_skills) ||
    !Array.isArray(data.missing_skills) ||
    !Number.isFinite(Number(data.match_percentage))
  ) {
    throw new Error(
      "The server returned an unexpected response. Please check analyzer.py."
    );
  }

  if (
    data.matched_skills.some((skill) => typeof skill !== "string") ||
    data.missing_skills.some(
      (item) =>
        !item ||
        typeof item.skill !== "string"
    )
  ) {
    throw new Error("The analysis response contains invalid skill data.");
  }
}

// Display the API's real analysis results.
function renderResults(data) {
  validateAnalysisResponse(data);

  const matchedSkills = data.matched_skills;
  const missingSkills = data.missing_skills;
  const percentage = Number(data.match_percentage);

  if (!Number.isFinite(percentage) || percentage < 0 || percentage > 100) {
    throw new Error("The server returned an invalid match percentage.");
  }

  document.getElementById("resultsSubtitle").textContent =
    `Analysis for ${data.job_role}`;

  document.getElementById("matchPercentage").textContent =
    `${percentage}%`;

  document.getElementById("matchedCount").textContent =
    matchedSkills.length;

  document.getElementById("missingCount").textContent =
    missingSkills.length;

  const matchedContainer = document.getElementById("matchedSkills");
  const missingContainer = document.getElementById("missingSkills");

  matchedContainer.replaceChildren();
  missingContainer.replaceChildren();

  if (matchedSkills.length === 0) {
    matchedContainer.appendChild(
      createTextElement(
        "p",
        "empty-skills",
        "No skills from this list were detected."
      )
    );
  } else {
    matchedSkills.forEach((skill) => {
      matchedContainer.appendChild(
        createTextElement("span", "skill-pill", `✓ ${skill}`)
      );
    });
  }

  if (missingSkills.length === 0) {
    missingContainer.appendChild(
      createTextElement(
        "p",
        "empty-skills",
        "All skills in the predefined list were detected."
      )
    );
  } else {
    missingSkills.forEach((item) => {
      const row = document.createElement("div");
      row.className = "missing-item";

      row.appendChild(createTextElement("span", "", item.skill));

      const courseUrl = getSafeCourseUrl(item.course_url);

      if (courseUrl) {
        const link = document.createElement("a");
        link.href = courseUrl;
        link.target = "_blank";
        link.rel = "noopener noreferrer";
        link.textContent = "Learn ↗";
        link.setAttribute(
          "aria-label",
          `Find learning resources for ${item.skill}`
        );

        row.appendChild(link);
      }

      missingContainer.appendChild(row);
    });
  }

  
const noticeElement = document.getElementById("analysisNotice");

noticeElement.textContent =
  typeof data.notice === "string" && data.notice.trim()
    ? data.notice
    : "This is a keyword-based estimate, not a complete measure of professional ability. A missing keyword does not necessarily mean you lack that skill.";


  renderChart(matchedSkills.length, missingSkills.length);

  resultsSection.hidden = false;

  resultsSection.scrollIntoView({
    behavior: "smooth",
    block: "start"
  });
}

// Send the PDF and selected role to Flask.
form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const file = fileInput.files[0];
  const jobRole = roleSelect.value;
  const fileError = validateFile(file);

  if (fileError) {
    showStatus(fileError, "error");
    return;
  }

  if (!jobRole) {
    showStatus("Please choose your target job role.", "error");
    roleSelect.focus();
    return;
  }

  const formData = new FormData();
  formData.append("resume", file);
  formData.append("job_role", jobRole);

  analyzeButton.disabled = true;
  buttonText.textContent = "Analyzing your resume...";
  buttonArrow.textContent = "◌";
  showStatus("Reading your resume and comparing listed skills...");

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      body: formData
    });

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
      throw new Error(
        data.error || `Analysis failed (HTTP ${response.status}).`
      );
    }

    renderResults(data);
    showStatus("Your analysis is ready.", "success");
  } catch (error) {
    console.error("SkillGap AI analysis error:", error);

    if (error instanceof TypeError) {
      showStatus(
        "Cannot reach the backend. Check that Flask is running on port 5000.",
        "error"
      );
    } else {
      showStatus(
        error.message || "Something went wrong. Please try again.",
        "error"
      );
    }
  } finally {
    analyzeButton.disabled = false;
    buttonText.textContent = "✨ Analyze Resume & Find Skill Gaps";
    buttonArrow.textContent = "→";
  }
});

// Reset the form and chart for another analysis.
document.getElementById("analyzeAnother").addEventListener("click", () => {
  form.reset();
  updateFileDisplay(null);
  showStatus("");

  resultsSection.hidden = true;

  if (skillChart) {
    skillChart.destroy();
    skillChart = null;
  }

  document.getElementById("analyzer").scrollIntoView({
    behavior: "smooth",
    block: "start"
  });
});

// Toggle the mobile navigation.
mobileMenu.addEventListener("click", () => {
  const isOpen = navLinks.classList.toggle("open");

  mobileMenu.setAttribute("aria-expanded", String(isOpen));
  mobileMenu.textContent = isOpen ? "✕" : "☰";
});

navLinks.querySelectorAll("a").forEach((link) => {
  link.addEventListener("click", () => {
    navLinks.classList.remove("open");
    mobileMenu.setAttribute("aria-expanded", "false");
    mobileMenu.textContent = "☰";
  });
});
