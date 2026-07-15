function toggleTheme() {
  document.body.classList.toggle("dark");
  localStorage.setItem(
    "careerPilotTheme",
    document.body.classList.contains("dark") ? "dark" : "light"
  );
}

function toggleSidebar() {
  document.getElementById("sidebar")?.classList.toggle("open");
}

if (localStorage.getItem("careerPilotTheme") === "dark") {
  document.body.classList.add("dark");
}

function showWorkingOverlay(message = "CareerPilot AI is working...") {
  const overlay = document.getElementById("workingOverlay");
  const label = document.getElementById("workingMessage");
  if (label) label.textContent = message;
  if (overlay) overlay.classList.add("show");
}

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("form").forEach((form) => {
    form.addEventListener("submit", () => {
      const button = form.querySelector('button[type="submit"], button:not([type])');
      if (button) {
        button.disabled = true;
        button.dataset.originalText = button.innerHTML;
        button.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Working...';
      }
      showWorkingOverlay("Generating your result. This can take a few seconds...");
    });
  });

  document.querySelectorAll('a[href="/report/download"]').forEach((link) => {
    link.addEventListener("click", () => {
      showWorkingOverlay("Preparing your PDF report...");
      setTimeout(() => document.getElementById("workingOverlay")?.classList.remove("show"), 8000);
    });
  });
});
