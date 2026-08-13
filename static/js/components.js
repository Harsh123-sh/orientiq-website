/* ============================================================
   ORIENTIQ — COMPONENTS
   ============================================================ */

(function () {
    "use strict";

    /* ---------- Reveal on scroll ---------- */
    var revealElements = document.querySelectorAll(".reveal");

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