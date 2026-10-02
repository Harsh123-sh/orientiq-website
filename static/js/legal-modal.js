(function () {
    "use strict";

    function initLegalModal() {
        var modal = document.querySelector("[data-legal-modal]");
        if (!modal) return;

        var dialog = modal.querySelector('[role="dialog"]');
        var content = modal.querySelector("[data-legal-content]");
        var title = modal.querySelector("[data-legal-modal-title], .orentiq-legal-modal__title");
        var triggers = document.querySelectorAll("[data-legal-trigger]");
        var closeButtons = modal.querySelectorAll("[data-legal-close]");
        var activeTrigger = null;
        var scrollPosition = 0;
        var titles = { privacy: "Privacy Policy", terms: "Terms of Service", cookies: "Cookie Policy" };

        function closeModal() {
            if (!modal.classList.contains("is-open")) return;
            modal.classList.remove("is-open");
            modal.setAttribute("aria-hidden", "true");
            document.body.classList.remove("orentiq-legal-modal-open");
            document.body.style.paddingRight = "";
            window.scrollTo(0, scrollPosition);
            if (activeTrigger) activeTrigger.focus();
        }

        function openModal(type, trigger) {
            var template = document.querySelector('[data-legal-template="' + type + '"]');
            if (!template) return;
            activeTrigger = trigger;
            title.textContent = titles[type];
            content.replaceChildren(template.content.cloneNode(true));
            scrollPosition = window.scrollY;
            var scrollbarWidth = window.innerWidth - document.documentElement.clientWidth;
            document.body.style.paddingRight = scrollbarWidth ? scrollbarWidth + "px" : "";
            document.body.classList.add("orentiq-legal-modal-open");
            modal.classList.add("is-open");
            modal.setAttribute("aria-hidden", "false");
            content.scrollTop = 0;
            modal.querySelector(".orentiq-legal-modal__close").focus();
        }

        function trapFocus(event) {
            if (event.key !== "Tab" || !modal.classList.contains("is-open")) return;
            var focusable = modal.querySelectorAll('button, [href], [tabindex]:not([tabindex="-1"])');
            if (!focusable.length) return;
            var first = focusable[0];
            var last = focusable[focusable.length - 1];
            if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
            else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
        }

        triggers.forEach(function (trigger) {
            trigger.addEventListener("click", function (event) {
                event.preventDefault();
                openModal(trigger.dataset.legalTrigger, trigger);
            });
        });
        closeButtons.forEach(function (button) { button.addEventListener("click", closeModal); });
        document.addEventListener("keydown", function (event) {
            if (event.key === "Escape") closeModal();
            trapFocus(event);
        });
        dialog.addEventListener("click", function (event) { event.stopPropagation(); });
    }

    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", initLegalModal);
    else initLegalModal();
}());