// Sets the admin theme as early as possible to prevent flash of wrong theme.
(function () {
    "use strict";

    var STORAGE_KEY = "orientiq-admin-theme";
    var preferred = null;

    try {
        preferred = localStorage.getItem(STORAGE_KEY);
    } catch (e) {
        /* ignore */
    }

    if (preferred !== "dark" && preferred !== "light") {
        preferred = "light";
    }

    document.documentElement.setAttribute("data-theme", preferred);
})();