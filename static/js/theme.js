/* ============================================================
   ORIENTIQ — THEME SYSTEM
   ============================================================ */

(function () {
    "use strict";

    var STORAGE_KEY = "orientiq-theme";
    var root = document.documentElement;

    function getStoredTheme() {
        try {
            return localStorage.getItem(STORAGE_KEY);
        } catch (e) {
            return null;
        }
    }

    function getSystemTheme() {
        return window.matchMedia &&
            window.matchMedia("(prefers-color-scheme: light)").matches
            ? "light"
            : "dark";
    }

    function getInitialTheme() {
        var stored = getStoredTheme();
        if (stored === "dark" || stored === "light") {
            return stored;
        }
        return getSystemTheme();
    }

    function applyTheme(theme) {
        root.setAttribute("data-theme", theme);
    }

    function setTheme(theme) {
        // Add a short transition only when the user actively changes theme.
        // Apply the class first, then change the attribute on the next frame
        // so the transition is visible. Remove it shortly after.
        root.classList.add("theme-transitioning");
        requestAnimationFrame(function () {
            applyTheme(theme);
            setTimeout(function () {
                root.classList.remove("theme-transitioning");
            }, 300);
        });
        try {
            localStorage.setItem(STORAGE_KEY, theme);
        } catch (e) {
            /* storage unavailable — theme still applies for this session */
        }
    }

    function toggleTheme() {
        var current = root.getAttribute("data-theme");
        setTheme(current === "light" ? "dark" : "light");
    }

    // Apply the initial theme as early as possible (no flash).
    applyTheme(getInitialTheme());

    // Expose for the toggle button and other components.
    window.OrientiqTheme = {
        get current() {
            return root.getAttribute("data-theme");
        },
        setTheme: setTheme,
        toggle: toggleTheme,
    };
})();