/* ORENTIQ services page explorer interactions. */
(function () {
    "use strict";

    var triggers = Array.prototype.slice.call(document.querySelectorAll("[data-service-explorer-open]"));
    var backdrop = document.querySelector("[data-service-explorer]");
    if (!triggers.length || !backdrop) return;

    // Keep the fixed overlay out of page-specific overflow/transform contexts.
    // This is required on service details as well as the overview page.
    if (backdrop.parentElement !== document.body) {
        document.body.appendChild(backdrop);
    }

    var dialog = backdrop.querySelector("[role='dialog']");
    var closeButton = backdrop.querySelector("[data-service-explorer-close]");
    var expandButton = backdrop.querySelector("[data-service-explorer-expand]");
    var contactButton = backdrop.querySelector("[data-service-explorer-contact]");
    var lastFocused = null;
    var focusableSelector = "a[href], button:not([disabled]), [tabindex]:not([tabindex='-1'])";

    function focusWithoutScrolling(element) {
        if (!element) return;
        try {
            element.focus({ preventScroll: true });
        } catch (error) {
            element.focus();
        }
    }

    function setExpanded(expanded) {
        backdrop.classList.toggle("is-expanded", expanded);
        if (expanded) {
            dialog.setAttribute("aria-label", "All ORENTIQ services");
        } else {
            dialog.removeAttribute("aria-label");
        }
    }

    function openExplorer(event) {
        if (event) event.preventDefault();
        lastFocused = document.activeElement;
        setExpanded(false);
        var scrollbarWidth = window.innerWidth - document.documentElement.clientWidth;
        document.body.style.paddingRight = scrollbarWidth ? scrollbarWidth + "px" : "";
        backdrop.classList.add("is-open");
        backdrop.setAttribute("aria-hidden", "false");
        document.body.classList.add("service-explorer-open");
        focusWithoutScrolling(closeButton);
    }

    function closeExplorer() {
        backdrop.classList.remove("is-open");
        backdrop.setAttribute("aria-hidden", "true");
        document.body.classList.remove("service-explorer-open");
        document.body.style.paddingRight = "";
        setExpanded(false);
        focusWithoutScrolling(lastFocused);
    }

    triggers.forEach(function (trigger) {
        trigger.addEventListener("click", openExplorer);
    });
    closeButton.addEventListener("click", closeExplorer);
    if (expandButton) {
        expandButton.addEventListener("click", function () {
            setExpanded(true);
            focusWithoutScrolling(closeButton);
        });
    }
    if (contactButton) contactButton.addEventListener("click", closeExplorer);
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

    var flowNodes = Array.prototype.slice.call(document.querySelectorAll(".services-flow__node"));
    if (flowNodes.length) {
        var flowRoot = document.querySelector(".services-flow");
        var flowActiveIndex = 0;
        var flowTimer = null;
        var prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

        function setActiveFlowNode(nextIndex) {
            flowActiveIndex = (nextIndex + flowNodes.length) % flowNodes.length;
            flowNodes.forEach(function (node, index) {
                node.classList.toggle("is-active", index === flowActiveIndex);
                node.classList.toggle("is-past", index < flowActiveIndex);
                node.classList.toggle("is-upcoming", index > flowActiveIndex);
            });
        }

        function startFlowAnimation() {
            if (prefersReducedMotion.matches || !flowRoot) return;
            clearInterval(flowTimer);
            flowTimer = window.setInterval(function () {
                setActiveFlowNode(flowActiveIndex + 1);
            }, 1700);
        }

        function pauseFlowAnimation() {
            if (!flowRoot) return;
            clearInterval(flowTimer);
            flowRoot.classList.add("is-paused");
        }

        function resumeFlowAnimation() {
            if (!flowRoot) return;
            flowRoot.classList.remove("is-paused");
            startFlowAnimation();
        }

        flowNodes.forEach(function (node) {
            node.addEventListener("mouseenter", pauseFlowAnimation);
            node.addEventListener("mouseleave", resumeFlowAnimation);
            node.addEventListener("focus", pauseFlowAnimation);
            node.addEventListener("blur", resumeFlowAnimation);
        });

        document.addEventListener("visibilitychange", function () {
            if (document.hidden) {
                clearInterval(flowTimer);
            } else {
                startFlowAnimation();
            }
        });

        setActiveFlowNode(0);
        startFlowAnimation();
    }
})();
