// Sets the theme as early as possible to prevent flash of wrong theme.
(function () {
    var STORAGE_KEY = "orientiq-theme";
    var preferred = null;
    try {
        preferred = localStorage.getItem(STORAGE_KEY);
    } catch (e) {
        /* ignore */
    }
    if (preferred !== "dark" && preferred !== "light") {
        preferred =
            window.matchMedia &&
            window.matchMedia("(prefers-color-scheme: light)").matches
                ? "light"
                : "dark";
    }
    document.documentElement.setAttribute("data-theme", preferred);
})();