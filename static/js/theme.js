/* ============================================================
   ORIENTIQ — ADMIN THEME SYSTEM
   ============================================================ */

(function () {
    "use strict";

    var STORAGE_KEY = "orientiq-admin-theme";
    var root = document.documentElement;
    var toggleButtons = document.querySelectorAll("[data-theme-toggle]");

    function getStoredTheme() {
        try {
            return localStorage.getItem(STORAGE_KEY);
        } catch (e) {
            return null;
        }
    }

    function getInitialTheme() {
        var stored = getStoredTheme();
        if (stored === "dark" || stored === "light") {
            return stored;
        }
        return "light";
    }

    function applyTheme(theme) {
        root.setAttribute("data-theme", theme);
    }

    function setTheme(theme) {
        if (theme !== "dark" && theme !== "light") {
            theme = "light";
        }

        root.classList.add("theme-transitioning");
        requestAnimationFrame(function () {
            applyTheme(theme);
            setTimeout(function () {
                root.classList.remove("theme-transitioning");
            }, 250);
        });

        try {
            localStorage.setItem(STORAGE_KEY, theme);
        } catch (e) {
            // storage unavailable; theme still applies in-session.
        }
    }

    function toggleTheme() {
        var current = root.getAttribute("data-theme");
        setTheme(current === "light" ? "dark" : "light");
    }

    applyTheme(getInitialTheme());

    toggleButtons.forEach(function (button) {
        button.addEventListener("click", toggleTheme);
    });

    window.OrientiqAdminTheme = {
        get current() {
            return root.getAttribute("data-theme");
        },
        setTheme: setTheme,
        toggle: toggleTheme,
    };
})();