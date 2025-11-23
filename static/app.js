document.addEventListener("DOMContentLoaded", () => {
  const body = document.body;
  const themeToggle = document.getElementById("themeToggle");
  const searchInput = document.getElementById("tableSearch");
  const table = document.getElementById("datasetTable");

  // === THEME TOGGLE ===
  const storedTheme = localStorage.getItem("dashboard-theme");
  if (storedTheme === "dark") {
    body.classList.add("dark-mode");
    updateThemeButton(true);
  }

  if (themeToggle) {
    themeToggle.addEventListener("click", () => {
      const isDark = body.classList.toggle("dark-mode");
      localStorage.setItem("dashboard-theme", isDark ? "dark" : "light");
      updateThemeButton(isDark);
    });
  }

  function updateThemeButton(isDark) {
    const label = themeToggle.querySelector("span:last-child");
    if (label) {
      label.textContent = isDark ? "Mode Terang" : "Mode Gelap";
    }
  }

  // === COUNTER ANIMATION ===
  const counters = document.querySelectorAll("[data-counter]");
  counters.forEach((el) => {
    const target = parseFloat(el.dataset.value || "0");
    const suffix = el.dataset.suffix || "";
    if (Number.isNaN(target)) return;
    const duration = 1600;
    const start = performance.now();
    const initialText = el.textContent.trim();

    function animate(now) {
      const progress = Math.min((now - start) / duration, 1);
      const value = Math.floor(progress * target);
      el.textContent = suffix
        ? `${value.toLocaleString("id-ID")}${suffix}`
        : value.toLocaleString("id-ID");
      if (progress < 1) requestAnimationFrame(animate);
    }

    requestAnimationFrame(animate);
  });

  // === TABLE SEARCH ===
  if (searchInput && table) {
    const rows = Array.from(table.querySelectorAll("tbody tr"));
    searchInput.addEventListener("input", (event) => {
      const term = event.target.value.toLowerCase();
      rows.forEach((row) => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(term) ? "" : "none";
      });
    });
  }
});

