/* ORENTIQ services page explorer interactions. */
(function () {
    "use strict";

    var trigger = document.querySelector("[data-service-explorer-open]");
    var backdrop = document.querySelector("[data-service-explorer]");
    if (!trigger || !backdrop) return;

    var dialog = backdrop.querySelector("[role='dialog']");
    var closeButton = backdrop.querySelector("[data-service-explorer-close]");
    var lastFocused = null;
    var focusableSelector = "a[href], button:not([disabled]), [tabindex]:not([tabindex='-1'])";

    function openExplorer() {
        lastFocused = document.activeElement;
        backdrop.classList.add("is-open");
        backdrop.setAttribute("aria-hidden", "false");
        document.body.classList.add("service-explorer-open");
        closeButton.focus();
    }

    function closeExplorer() {
        backdrop.classList.remove("is-open");
        backdrop.setAttribute("aria-hidden", "true");
        document.body.classList.remove("service-explorer-open");
        if (lastFocused) lastFocused.focus();
    }

    trigger.addEventListener("click", openExplorer);
    closeButton.addEventListener("click", closeExplorer);
    backdrop.addEventListener("click", function (event) {
        if (event.target === backdrop) closeExplorer();
    });

    function handleKeydown(event) {
        if (!backdrop.classList.contains("is-open")) return;
        if (event.key === "Escape") {
            event.preventDefault();
            closeExplorer();
            return;
        }
        if (event.key !== "Tab") return;
        var focusable = Array.prototype.slice.call(dialog.querySelectorAll(focusableSelector));
        if (!focusable.length) return;
        var first = focusable[0];
        var last = focusable[focusable.length - 1];
        if (event.shiftKey && document.activeElement === first) {
            event.preventDefault();
            last.focus();
        } else if (!event.shiftKey && document.activeElement === last) {
            event.preventDefault();
            first.focus();
        }
    }

    window.addEventListener("keydown", handleKeydown, true);
})();
