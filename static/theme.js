document.addEventListener("DOMContentLoaded", () => {
    const themeToggle = document.getElementById("theme-toggle");

    function applyTheme(theme) {
        const isDark = theme === "dark";

        document.documentElement.setAttribute("data-theme", theme);
        document.body.classList.toggle("dark-theme", isDark);

        localStorage.setItem("expireiq-theme", theme);

        if (themeToggle) {
            themeToggle.textContent = isDark ? "☀️" : "🌙";
            themeToggle.title = isDark ? "Switch to light mode" : "Switch to dark mode";
        }
    }

    const savedTheme = localStorage.getItem("expireiq-theme");
    const systemPrefersDark =
        window.matchMedia &&
        window.matchMedia("(prefers-color-scheme: dark)").matches;

    const startingTheme = savedTheme || (systemPrefersDark ? "dark" : "light");

    applyTheme(startingTheme);

    if (themeToggle) {
        themeToggle.addEventListener("click", () => {
            const currentTheme = document.body.classList.contains("dark-theme")
                ? "dark"
                : "light";

            const newTheme = currentTheme === "dark" ? "light" : "dark";

            applyTheme(newTheme);
        });
    }
});