// script.js - small browser-side helpers. All real data work happens in Python.

// 1) Dark mode toggle (remembered in the browser via localStorage)
const themeButton = document.getElementById("theme-toggle");
function updateThemeButton() {
  const dark = document.documentElement.dataset.theme === "dark";
  themeButton.textContent = dark ? "☀️ Light mode" : "🌙 Dark mode";
}
themeButton.addEventListener("click", () => {
  const dark = document.documentElement.dataset.theme === "dark";
  if (dark) {
    delete document.documentElement.dataset.theme;
    localStorage.setItem("theme", "light");
  } else {
    document.documentElement.dataset.theme = "dark";
    localStorage.setItem("theme", "dark");
  }
  updateThemeButton();
});
updateThemeButton();

// 2) Mobile sidebar toggle
document.getElementById("menu-btn").addEventListener("click", () => {
  document.getElementById("sidebar").classList.toggle("open");
});

// 3) Confirmation dialog before deleting.
//    Any <form data-confirm="..."> asks first; "Cancel" stops the submit.
document.querySelectorAll("form[data-confirm]").forEach((form) => {
  form.addEventListener("submit", (event) => {
    if (!window.confirm(form.dataset.confirm)) event.preventDefault();
  });
});

// 4) Close buttons on notifications, and auto-hide success messages
document.querySelectorAll(".alert").forEach((alertBox) => {
  alertBox.querySelector(".alert-close").addEventListener("click", () => alertBox.remove());
  if (alertBox.classList.contains("alert-success")) {
    setTimeout(() => alertBox.remove(), 4000);
  }
});
