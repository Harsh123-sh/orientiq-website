/* ============================================================
   ORIENTIQ — COMPONENTS
   ============================================================ */

(function () {
    "use strict";

    /* ---------- Public motion enrollment ---------- */
    var motionGroups = [
        ".section-heading",
        ".card-service",
        ".card-technology",
        ".card-industry",
        ".card-product",
        ".card-portfolio",
        ".process-step",
        ".card-stat",
        ".cta-card",
        ".trust-item"
    ];

    motionGroups.forEach(function (selector) {
        document.querySelectorAll(selector).forEach(function (element, index) {
            if (!element.classList.contains("reveal") && !element.classList.contains("reveal-up") && !element.classList.contains("reveal-scale")) {
                element.classList.add("reveal-up");
            }
            var siblingIndex = Array.prototype.indexOf.call(element.parentElement ? element.parentElement.children : [], element);
            element.style.setProperty("--reveal-delay", Math.min(Math.max(siblingIndex, index) * 100, 300) + "ms");
        });
    });

    document.querySelectorAll(".hero-eyebrow, .hero h1, .hero p.lead, .hero-actions, .hero-visual, .page-hero .eyebrow, .page-hero h1, .page-hero p").forEach(function (element, index) {
        if (!element.classList.contains("reveal") && !element.classList.contains("reveal-up") && !element.classList.contains("reveal-scale")) {
            element.classList.add(element.classList.contains("hero-visual") ? "reveal-scale" : "reveal-up");
        }
        var heroDelays = [150, 250, 400, 550, 300];
        element.style.setProperty("--reveal-delay", (element.closest(".hero") ? heroDelays[index] || 300 : Math.min(index * 80, 320)) + "ms");
    });

    /* ---------- Reveal on scroll ---------- */
    var revealElements = document.querySelectorAll(".reveal, .reveal-up, .reveal-left, .reveal-right, .reveal-image, .reveal-scale");

    if ("IntersectionObserver" in window) {
        var observer = new IntersectionObserver(
            function (entries) {
                entries.forEach(function (entry) {
                    if (entry.isIntersecting) {
                        entry.target.classList.add("is-visible");
                        observer.unobserve(entry.target);
                    }
                });
            },
            { threshold: 0.1 }
        );

        revealElements.forEach(function (el) {
            observer.observe(el);
        });
    } else {
        // Fallback: show everything immediately.
        revealElements.forEach(function (el) {
            el.classList.add("is-visible");
        });
    }

    /* ---------- Theme toggle buttons ---------- */
    document.querySelectorAll("[data-theme-toggle]").forEach(function (btn) {
        btn.addEventListener("click", function () {
            if (window.OrientiqTheme) {
                window.OrientiqTheme.toggle();
            }
        });
    });

    /* ---------- Password visibility toggle ---------- */
    document.querySelectorAll(".password-toggle").forEach(function (btn) {
        btn.addEventListener("click", function () {
            var input = btn.closest(".password-field").querySelector("input");
            if (!input) return;
            var isPassword = input.type === "password";
            input.type = isPassword ? "text" : "password";
            btn.setAttribute("aria-label", isPassword ? "Hide password" : "Show password");
        });
    });

    /* ---------- Modal foundation ---------- */
    document.querySelectorAll("[data-modal-open]").forEach(function (trigger) {
        trigger.addEventListener("click", function () {
            var target = document.querySelector(
                trigger.getAttribute("data-modal-open")
            );
            if (target) {
                target.classList.add("is-open");
                target.setAttribute("aria-hidden", "false");
                document.body.style.overflow = "hidden";
            }
        });
    });

    document.querySelectorAll("[data-modal-close]").forEach(function (trigger) {
        trigger.addEventListener("click", function () {
            var modal = trigger.closest(".modal-backdrop");
            if (modal) {
                modal.classList.remove("is-open");
                modal.setAttribute("aria-hidden", "true");
                document.body.style.overflow = "";
            }
        });
    });

    document.querySelectorAll(".modal-backdrop").forEach(function (modal) {
        modal.addEventListener("click", function (e) {
            if (e.target === modal) {
                modal.classList.remove("is-open");
                modal.setAttribute("aria-hidden", "true");
                document.body.style.overflow = "";
            }
        });
    });
})();